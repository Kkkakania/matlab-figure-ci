"""Command line interface for mfigci."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import ConfigError, load_config
from .gallery import run_gallery_check
from .matlab import run_matlab_render
from .report import load_results, save_json_report, save_markdown, save_results
from .release import (
    release_preflight_exit_code,
    release_preflight_payload,
    release_preflight_summary,
    run_release_preflight,
)
from .result import CheckResults, Finding
from .scanners import run_scan


EXAMPLE_CONFIG = """project:
  name: matlab-scientific-figures

scan:
  include:
    - "."
  exclude:
    - ".git"
    - ".venv"
    - ".venv*"
    - "venv"
    - "__pycache__"
    - "pycache"
    - "dist"
    - "build"
    - ".pytest_cache"
    - ".ipynb_checkpoints"
    - "LICENSE"

privacy:
  enabled: true
  redact_matches: true

provenance:
  enabled: true

extensions:
  error:
    - ".p"
    - ".mat"
    - ".fig"
    - ".doc"
    - ".docx"
    - ".xlsx"
    - ".vsd"
  warning:
    - ".pdf"
    - ".mlx"
    - ".zip"

gallery:
  path: "gallery"
  allowed_extensions:
    - ".png"
    - ".svg"
    - ".pdf"
  min_size_bytes: 1024
  expected:
    - "example.png"

matlab:
  enabled: false
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "run_all_figures"
"""


WORKFLOW = f"""name: figure-quality

on:
  push:
  pull_request:

permissions:
  contents: read

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  mfigci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"

      - name: Install matlab-figure-ci
        run: |
          python -m pip install --upgrade pip
          pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v{__version__}

      - name: Show effective mfigci policy
        run: |
          mfigci rules --config mfigci.yml

      - name: Run mfigci checks
        run: |
          mfigci check --config mfigci.yml --report mfigci-report.md

      - name: Upload mfigci report
        uses: actions/upload-artifact@v5
        if: always()
        with:
          name: mfigci-report
          include-hidden-files: true
          path: |
            mfigci-report.md
            .mfigci-results.json
"""


def _print_scan(result) -> None:
    for finding in result.findings:
        line = "" if finding.line is None else f":L{finding.line}"
        print(f"{finding.severity.upper()} {finding.rule_id} {finding.path}{line} {finding.message}")
    print(
        f"{result.error_count} error(s), {result.warning_count} warning(s), "
        f"{result.files_scanned} file(s) scanned, {result.skipped_binary_count} binary/skipped."
    )


def _print_gallery(result) -> None:
    for item in result.items:
        print(f"{item.status.upper()} {item.path} {item.message}")
    print(f"{result.error_count} error(s), {result.warning_count} warning(s), {result.checked_count} gallery file(s) ok.")


def _policy_exit_code(error_count: int, warning_count: int, fail_on_warnings: bool) -> int:
    if error_count:
        return 1
    if fail_on_warnings and warning_count:
        return 1
    return 0


def _load_config_arg(args):
    if not args.config:
        print("--config must not be empty", file=sys.stderr)
        raise SystemExit(2)
    return load_config(args.config)


def _fail_on_warnings(args, config: dict) -> bool:
    return bool(args.fail_on_warnings or config.get("strict", {}).get("fail_on_warnings", False))


def _public_config_path(config_path: Path, root: Path) -> str:
    if not config_path.is_absolute():
        return config_path.as_posix()
    try:
        return config_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return config_path.name


def _build_check_results(config_path: Path, config: dict, root: Path, include_render: bool) -> CheckResults:
    scan = run_scan(root, config)
    gallery = run_gallery_check(root, config)
    render = {"status": "skipped", "message": "disabled", "exit_code": 0}
    if include_render:
        render = run_matlab_render(root, config)

    findings = list(scan.findings)
    for item in gallery.items:
        if item.status in {"error", "warning"}:
            findings.append(Finding("error" if item.status == "error" else "warning", f"gallery.{item.status}", item.path, None, item.message))

    errors = scan.error_count + gallery.error_count + (1 if render.get("status") == "error" else 0)
    warnings = scan.warning_count + gallery.warning_count
    summary = {
        "errors": errors,
        "warnings": warnings,
        "files_scanned": scan.files_scanned,
        "gallery_checks": len(gallery.items),
        "skipped_binary": scan.skipped_binary_count,
    }
    return CheckResults(
        summary=summary,
        findings=findings,
        scan=scan,
        gallery=gallery,
        render=render,
        config_path=_public_config_path(config_path, root),
        tool_version=__version__,
    )


def command_scan(args) -> int:
    config = _load_config_arg(args)
    result = run_scan(Path.cwd(), config, getattr(args, "paths", None))
    _print_scan(result)
    return _policy_exit_code(result.error_count, result.warning_count, _fail_on_warnings(args, config))


def command_gallery(args) -> int:
    config = _load_config_arg(args)
    result = run_gallery_check(Path.cwd(), config)
    _print_gallery(result)
    return result.exit_code


def command_render(args) -> int:
    config = _load_config_arg(args)
    result = run_matlab_render(Path.cwd(), config)
    print(f"{result['status'].upper()} {result['message']}")
    if result.get("status") == "error":
        if "process_exit_code" in result:
            print(f"MATLAB process exit code: {result['process_exit_code']}")
        if result.get("stdout_excerpt"):
            print("MATLAB stdout excerpt:")
            print(result["stdout_excerpt"])
        if result.get("stderr_excerpt"):
            print("MATLAB stderr excerpt:")
            print(result["stderr_excerpt"])
    return int(result.get("exit_code", 0))


def command_check(args) -> int:
    if not args.report:
        print("--report must not be empty", file=sys.stderr)
        return 2
    if not args.results:
        print("--results must not be empty", file=sys.stderr)
        return 2
    config_path = Path(args.config)
    config = _load_config_arg(args)
    include_render = bool(config.get("matlab", {}).get("enabled", False))
    results = _build_check_results(config_path, config, Path.cwd(), include_render)
    save_results(results, args.results)
    save_markdown(results, args.report)
    _print_scan(results.scan)
    _print_gallery(results.gallery)
    print(f"Report written to {args.report}")
    print(f"Results written to {args.results}")
    print(f"Evidence packet: mfigci report --style evidence --input {args.results} --output mfigci-evidence.md")
    if results.render.get("status") == "error":
        print(f"ERROR render {results.render.get('message')}")
        if "process_exit_code" in results.render:
            print(f"MATLAB process exit code: {results.render['process_exit_code']}")
        if results.render.get("stdout_excerpt"):
            print("MATLAB stdout excerpt:")
            print(results.render["stdout_excerpt"])
        if results.render.get("stderr_excerpt"):
            print("MATLAB stderr excerpt:")
            print(results.render["stderr_excerpt"])
        return 3
    return _policy_exit_code(
        int(results.summary.get("errors", 0)),
        int(results.summary.get("warnings", 0)),
        _fail_on_warnings(args, config),
    )


def command_report(args) -> int:
    if not args.input:
        print("--input must not be empty", file=sys.stderr)
        return 2
    if not args.output:
        print("--output must not be empty", file=sys.stderr)
        return 2
    try:
        results = load_results(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    if args.format == "json":
        save_json_report(results, args.output)
    else:
        save_markdown(results, args.output, style=args.style)
    print(f"Report written to {args.output}")
    return 0


def _write_if_allowed(path: Path, content: str, force: bool) -> str:
    if path.is_dir():
        return f"skipped {path.as_posix()} (directory exists)"
    if path.exists() and not force:
        return f"skipped {path.as_posix()} (already exists)"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote {path.as_posix()}"


def _update_gitignore(path: Path) -> str:
    entries = [
        "mfigci-report.md",
        "mfigci-evidence.md",
        ".mfigci-results.json",
        "release-preflight.json",
        "pypi-name-check.json",
    ]
    header = "# matlab-figure-ci local reports"
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = ""

    existing_lines = text.splitlines()
    missing_entries = [entry for entry in entries if entry not in existing_lines]

    if not missing_entries:
        return "already contains mfigci report artifacts in .gitignore"

    prefix = text
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix:
        prefix += "\n"
    path.write_text(prefix + header + "\n" + "\n".join(missing_entries) + "\n", encoding="utf-8")
    return "updated .gitignore with mfigci report artifacts"


def command_init(args) -> int:
    messages = [
        _write_if_allowed(Path("mfigci.yml"), EXAMPLE_CONFIG, args.force),
        _write_if_allowed(Path(".github/workflows/figure-quality.yml"), WORKFLOW, args.force),
    ]
    if args.gitignore:
        messages.append(_update_gitignore(Path(".gitignore")))
    for message in messages:
        print(message)
    if not args.gitignore:
        print("Optional: run `mfigci init --gitignore` to ignore local report artifacts.")
    print("Next: run `mfigci doctor --config mfigci.yml` to review the effective policy.")
    print("Then run `mfigci check --config mfigci.yml --report mfigci-report.md`.")
    return 0


def _format_list(values) -> str:
    if not values:
        return "(none)"
    return ", ".join(str(value) for value in values)


def _safe_relative_label(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return "<outside-repository>"


def _configured_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _safe_configured_label(root: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return _safe_relative_label(root, path)
    return path.as_posix()


def _format_path_list(root: Path, values) -> str:
    if not values:
        return "(none)"
    return ", ".join(_safe_configured_label(root, str(value)) for value in values)


def _doctor_path_warnings(root: Path, config: dict) -> list[str]:
    warnings: list[str] = []
    scan = config.get("scan", {})
    gallery = config.get("gallery", {})

    for include in scan.get("include", []):
        include_path = _configured_path(root, str(include))
        if not include_path.exists():
            warnings.append(f"WARNING doctor.scan_include_missing {_safe_relative_label(root, include_path)}")

    gallery_path = _configured_path(root, str(gallery.get("path", "gallery")))
    if not gallery_path.exists():
        warnings.append(f"WARNING doctor.gallery_path_missing {_safe_relative_label(root, gallery_path)}")
        return warnings

    for expected in gallery.get("expected", []):
        expected_path = gallery_path / str(expected)
        if not expected_path.exists():
            warnings.append(f"WARNING doctor.gallery_expected_missing {_safe_relative_label(root, expected_path)}")

    return warnings


def _doctor_payload(config_path: Path, config: dict, root: Path) -> dict:
    project = config.get("project", {})
    scan = config.get("scan", {})
    privacy = config.get("privacy", {})
    provenance = config.get("provenance", {})
    generated_assets = config.get("generated_assets", {})
    strict = config.get("strict", {})
    gallery = config.get("gallery", {})
    extensions = config.get("extensions", {})
    matlab = config.get("matlab", {})
    presets = config.get("presets", config.get("preset", []))
    if isinstance(presets, str):
        presets = [presets]

    config_found = config_path.exists()
    config_label = _public_config_path(config_path, root)

    scan_include = [_safe_configured_label(root, str(value)) for value in scan.get("include", [])]
    scan_exclude = [str(value) for value in scan.get("exclude", [])]

    return {
        "schema_version": 1,
        "tool_version": __version__,
        "config_path": config_label,
        "config_found": config_found,
        "project": {
            "name": project.get("name", "(unnamed)"),
        },
        "presets": list(presets),
        "scan": {
            "include": scan_include,
            "exclude": scan_exclude,
            "include_count": len(scan_include),
            "exclude_count": len(scan_exclude),
        },
        "gallery": {
            "path": _safe_configured_label(root, str(gallery.get("path", "gallery"))),
            "allowed_extensions": list(gallery.get("allowed_extensions", [])),
            "min_size_bytes": int(gallery.get("min_size_bytes", 0)),
            "expected_count": len(gallery.get("expected", [])),
        },
        "rules": {
            "privacy_count": len(privacy.get("rules", [])),
            "provenance_count": len(provenance.get("rules", [])),
            "extension_error_count": len(extensions.get("error", [])),
            "extension_warning_count": len(extensions.get("warning", [])),
            "generated_asset_enabled": bool(generated_assets.get("enabled", True)),
            "generated_asset_severity": str(generated_assets.get("severity", "warning")),
            "generated_asset_source_dirs": list(generated_assets.get("source_dirs", [])),
            "generated_asset_extensions": list(generated_assets.get("extensions", [])),
        },
        "privacy": {
            "enabled": bool(privacy.get("enabled", True)),
            "redact_matches": bool(privacy.get("redact_matches", True)),
        },
        "provenance": {
            "enabled": bool(provenance.get("enabled", True)),
        },
        "strict": {
            "fail_on_warnings": bool(strict.get("fail_on_warnings", False)),
        },
        "matlab": {
            "enabled": bool(matlab.get("enabled", False)),
            "bin_env": str(matlab.get("bin_env", "MATLAB_BIN")),
            "fallback_bin": str(matlab.get("fallback_bin", "matlab")),
            "batch_command": str(matlab.get("batch_command", "run_all_figures")),
        },
        "warnings": _doctor_path_warnings(root, config),
    }


def command_doctor(args) -> int:
    if not args.config:
        print("--config must not be empty", file=sys.stderr)
        return 2
    config_path = Path(args.config)
    config = load_config(config_path)
    root = Path.cwd()
    payload = _doctor_payload(config_path, config, root)

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    path_label = payload["config_path"]
    if not payload["config_found"]:
        path_label = f"{path_label} (not found; using defaults)"

    matlab_enabled = bool(payload["matlab"]["enabled"])
    matlab_status = "enabled" if matlab_enabled else "disabled"
    if matlab_enabled:
        matlab_status = f"enabled (env: {payload['matlab']['bin_env']})"

    print("matlab-figure-ci doctor")
    print(f"Config path: {path_label}")
    print(f"Project: {payload['project']['name']}")
    print(f"Presets: {_format_list(payload['presets'])}")
    print(f"Scan include: {_format_list(payload['scan']['include'])}")
    print(f"Scan exclude: {_format_list(payload['scan']['exclude'])}")
    print(f"Privacy scan: {'enabled' if payload['privacy']['enabled'] else 'disabled'}")
    print(f"Privacy rules: {payload['rules']['privacy_count']}")
    print(f"Provenance scan: {'enabled' if payload['provenance']['enabled'] else 'disabled'}")
    print(f"Provenance rules: {payload['rules']['provenance_count']}")
    print(f"Fail on warnings: {'enabled' if payload['strict']['fail_on_warnings'] else 'disabled'}")
    print(f"Gallery path: {payload['gallery']['path']}")
    print(f"Gallery allowed extensions: {_format_list(payload['gallery']['allowed_extensions'])}")
    print(f"Gallery expected files: {payload['gallery']['expected_count']}")
    print(f"Extension errors: {payload['rules']['extension_error_count']}")
    print(f"Extension warnings: {payload['rules']['extension_warning_count']}")
    print(f"Generated asset scan: {'enabled' if payload['rules']['generated_asset_enabled'] else 'disabled'}")
    print(f"MATLAB render: {matlab_status}")
    for warning in payload["warnings"]:
        print(warning)
    return 0


def _print_rule_group(title: str, section: dict, privacy: bool = False) -> None:
    enabled = section.get("enabled", True)
    print(f"{title}: {'enabled' if enabled else 'disabled'}")
    if not enabled:
        return

    redaction = "redacted" if privacy and section.get("redact_matches", True) else "pattern matched"
    for rule in section.get("rules", []):
        rule_id = rule.get("id", "(unnamed)")
        severity = rule.get("severity", "warning")
        message = redaction if privacy else "pattern matched"
        print(f"  - {rule_id} {severity} {message}")


def command_rules(args) -> int:
    config = _load_config_arg(args)
    privacy = config.get("privacy", {})
    provenance = config.get("provenance", {})
    extensions = config.get("extensions", {})
    generated_assets = config.get("generated_assets", {})

    print("matlab-figure-ci rules")
    _print_rule_group("Privacy rules", privacy, privacy=True)
    _print_rule_group("Provenance rules", provenance)
    print(f"Extension errors: {_format_list(extensions.get('error', []))}")
    print(f"Extension warnings: {_format_list(extensions.get('warning', []))}")
    print(f"Generated asset scan: {'enabled' if generated_assets.get('enabled', True) else 'disabled'}")
    print(f"Generated asset severity: {generated_assets.get('severity', 'warning')}")
    print(f"Generated asset source dirs: {_format_list(generated_assets.get('source_dirs', []))}")
    print(f"Generated asset extensions: {_format_list(generated_assets.get('extensions', []))}")
    return 0


def command_release_preflight(args) -> int:
    if args.output == "":
        print("--output must not be empty", file=sys.stderr)
        return 2
    items = run_release_preflight(
        Path.cwd(),
        expected_name=args.name,
        expected_version=__version__,
        check_pypi_name=args.check_pypi_name,
        require_dist=args.require_dist,
    )
    exit_code = release_preflight_exit_code(items, fail_on_warnings=args.fail_on_warnings)
    payload = release_preflight_payload(
        items,
        exit_code=exit_code,
        project_name=args.name,
        project_version=__version__,
    )
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return exit_code

    for item in items:
        print(f"{item.status.upper()} {item.check} {item.message}")
    summary = release_preflight_summary(items)
    print(f"{summary['errors']} error(s), {summary['warnings']} warning(s), {summary['checks']} preflight check(s).")
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mfigci", description="CI checks for MATLAB scientific figure repositories.")
    parser.add_argument("--version", action="version", version=f"mfigci {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="scan privacy, provenance, and risky file extensions")
    scan.add_argument("--config", default="mfigci.yml")
    scan.add_argument("--fail-on-warnings", action="store_true", help="return exit code 1 when warnings are present")
    scan.add_argument("--paths", nargs="+", help="scan only these repository-relative paths")
    scan.set_defaults(func=command_scan)

    gallery = subparsers.add_parser("gallery", help="check expected gallery outputs")
    gallery.add_argument("--config", default="mfigci.yml")
    gallery.set_defaults(func=command_gallery)

    render = subparsers.add_parser("render", help="run optional MATLAB batch rendering")
    render.add_argument("--config", default="mfigci.yml")
    render.set_defaults(func=command_render)

    check = subparsers.add_parser("check", help="run scan, gallery, optional render, and write reports")
    check.add_argument("--config", default="mfigci.yml")
    check.add_argument("--report", default="mfigci-report.md")
    check.add_argument("--results", default=".mfigci-results.json")
    check.add_argument("--fail-on-warnings", action="store_true", help="return exit code 1 when warnings are present")
    check.set_defaults(func=command_check)

    report = subparsers.add_parser("report", help="build markdown or JSON from .mfigci-results.json")
    report.add_argument("--input", default=".mfigci-results.json")
    report.add_argument("--output", default="mfigci-report.md")
    report.add_argument("--format", choices=["markdown", "json"], default="markdown")
    report.add_argument("--style", choices=["full", "pr-comment", "evidence", "triage"], default="full")
    report.set_defaults(func=command_report)

    init = subparsers.add_parser("init", help="write example config and GitHub Actions workflow")
    init.add_argument("--force", action="store_true")
    init.add_argument("--gitignore", action="store_true", help="append local report artifacts to .gitignore")
    init.set_defaults(func=command_init)

    doctor = subparsers.add_parser("doctor", help="show effective config summary")
    doctor.add_argument("--config", default="mfigci.yml")
    doctor.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    doctor.set_defaults(func=command_doctor)

    rules = subparsers.add_parser("rules", help="show effective privacy, provenance, and extension rules")
    rules.add_argument("--config", default="mfigci.yml")
    rules.set_defaults(func=command_rules)

    release_preflight = subparsers.add_parser("release-preflight", help="check packaging readiness before a release")
    release_preflight.add_argument("--name", default="matlab-figure-ci", help="expected package/project name")
    release_preflight.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    release_preflight.add_argument("--output", help="write machine-readable JSON preflight results to this file")
    release_preflight.add_argument(
        "--check-pypi-name",
        action="store_true",
        help="query the PyPI JSON API for the project name; disabled by default",
    )
    release_preflight.add_argument("--require-dist", action="store_true", help="require dist/*.whl and dist/*.tar.gz")
    release_preflight.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="return exit code 1 when warning preflight items are present",
    )
    release_preflight.set_defaults(func=command_release_preflight)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
