"""Privacy, provenance, and file-extension scanners."""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from .result import Finding, ScanResults

TEXT_SKIP_SUFFIXES = {
    ".fig",
    ".mat",
    ".p",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".pdf",
    ".zip",
    ".xlsx",
    ".docx",
    ".doc",
    ".vsd",
    ".mlx",
}


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _relative(root: Path, path: Path) -> str:
    try:
        return _as_posix(path.relative_to(root))
    except ValueError:
        return path.name


def _is_excluded(relative_path: Path, excludes: Iterable[str]) -> bool:
    parts = relative_path.parts
    rel = _as_posix(relative_path)
    for pattern in excludes:
        pattern = pattern.strip("/")
        if (
            pattern in parts
            or any(fnmatch(part, pattern) for part in parts)
            or rel == pattern
            or rel.startswith(f"{pattern}/")
            or fnmatch(rel, pattern)
        ):
            return True
    return False


def _stays_within_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError):
        return False
    return True


def iter_files(root: Path, config: dict, selected_paths: Iterable[str | Path] | None = None) -> Iterable[Path]:
    scan = config.get("scan", {})
    includes = [str(path) for path in selected_paths] if selected_paths is not None else scan.get("include", ["."])
    excludes = scan.get("exclude", [])
    seen: set[Path] = set()

    root = root.resolve()
    for include in includes:
        base = root / include
        if not base.exists():
            continue
        candidates = [base] if base.is_file() else base.rglob("*")
        for path in candidates:
            if not path.is_file():
                continue
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
            if path.is_symlink() and not _stays_within_root(path, root):
                continue
            if _is_excluded(relative, excludes):
                continue
            if path in seen:
                continue
            seen.add(path)
            yield path


def _looks_binary(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SKIP_SUFFIXES:
        return True
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\x00" in sample


def _read_text(path: Path) -> str | None:
    if _looks_binary(path):
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _extension_findings(root: Path, path: Path, config: dict) -> list[Finding]:
    suffix = path.suffix.lower()
    relative = _relative(root, path)
    extensions = config.get("extensions", {})
    if _extension_is_allowed(relative, suffix, extensions.get("allow", [])):
        return []
    error_extensions = {str(item).lower() for item in extensions.get("error", [])}
    warning_extensions = {str(item).lower() for item in extensions.get("warning", [])}
    if suffix in error_extensions:
        return [Finding("error", "extension.error", relative, None, f"risky extension {suffix}")]
    if suffix in warning_extensions:
        return [Finding("warning", "extension.warning", relative, None, f"review extension {suffix}")]
    return []


def _generated_asset_findings(root: Path, path: Path, config: dict) -> list[Finding]:
    generated_assets = config.get("generated_assets", {})
    if not generated_assets.get("enabled", True):
        return []

    suffix = path.suffix.lower()
    extensions = {str(item).lower() for item in generated_assets.get("extensions", [])}
    if suffix not in extensions:
        return []

    relative = _relative(root, path)
    if _path_is_under_any(relative, generated_assets.get("allow", [])):
        return []
    if not _path_is_under_any(relative, generated_assets.get("source_dirs", [])):
        return []

    severity = str(generated_assets.get("severity", "warning"))
    message = "generated asset appears inside a source or template directory"
    return [Finding(severity, "generated_asset.source_tree", relative, None, message)]


def _extension_is_allowed(relative_path: str, suffix: str, allow_rules: list[dict]) -> bool:
    for rule in allow_rules:
        base_path = str(rule.get("path", "")).strip("/")
        allowed_extensions = {str(item).lower() for item in rule.get("extensions", [])}
        if not base_path or suffix not in allowed_extensions:
            continue
        if (
            relative_path == base_path
            or relative_path.startswith(f"{base_path}/")
            or fnmatch(relative_path, base_path)
        ):
            return True
    return False


def _path_is_under_any(relative_path: str, base_paths: list[str]) -> bool:
    rel = relative_path.strip("/")
    for base_path in base_paths:
        base = str(base_path).strip("/")
        if not base:
            continue
        if rel == base or rel.startswith(f"{base}/"):
            return True
    return False


def _rule_findings(root: Path, path: Path, text: str, rules: list[dict], redact: bool) -> list[Finding]:
    findings: list[Finding] = []
    relative = _relative(root, path)
    for rule in rules:
        pattern = str(rule.get("pattern", ""))
        if not pattern:
            continue
        regex = re.compile(pattern)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                rule_id = str(rule.get("id", "rule.unknown"))
                severity = str(rule.get("severity", "warning"))
                message = "<redacted>" if redact or rule_id.startswith("privacy.") else "pattern matched"
                findings.append(Finding(severity, rule_id, relative, line_number, message))
    return findings


def run_scan(root: str | Path, config: dict, paths: Iterable[str | Path] | None = None) -> ScanResults:
    root_path = Path(root).resolve()
    result = ScanResults()

    for path in iter_files(root_path, config, paths):
        result.files_scanned += 1
        result.findings.extend(_extension_findings(root_path, path, config))
        result.findings.extend(_generated_asset_findings(root_path, path, config))

        text = _read_text(path)
        if text is None:
            result.skipped_binary_count += 1
            continue

        privacy = config.get("privacy", {})
        if privacy.get("enabled", True):
            result.findings.extend(
                _rule_findings(root_path, path, text, privacy.get("rules", []), bool(privacy.get("redact_matches", True)))
            )

        provenance = config.get("provenance", {})
        if provenance.get("enabled", True):
            result.findings.extend(_rule_findings(root_path, path, text, provenance.get("rules", []), False))

    return result
