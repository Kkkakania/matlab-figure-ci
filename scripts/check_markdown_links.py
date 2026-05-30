#!/usr/bin/env python3
"""Check repository-local Markdown links without external dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
EXCLUDED_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__", "build", "dist"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def iter_markdown_files(root: Path = ROOT) -> list[Path]:
    root = root.resolve()
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return sorted(files)


def normalize_target(raw_target: str) -> str:
    target = raw_target.strip().strip("<>")
    if " " in target:
        target = target.split()[0]
    return unquote(target)


def should_skip(target: str) -> bool:
    return (
        not target
        or target.startswith("#")
        or target.startswith(EXTERNAL_PREFIXES)
        or target.startswith("git+")
    )


def check_file(path: Path, root: Path = ROOT) -> list[str]:
    root = root.resolve()
    path = path.resolve()
    text = path.read_text(encoding="utf-8")
    text = FENCE_RE.sub("", text)
    errors: list[str] = []

    for match in LINK_RE.finditer(text):
        target = normalize_target(match.group(1))
        if should_skip(target):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (path.parent / target_path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"{path.relative_to(root)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: missing link target: {target}")

    return errors


def main() -> int:
    root = ROOT
    markdown_files = iter_markdown_files(root)
    errors: list[str] = []
    for path in markdown_files:
        errors.extend(check_file(path, root=root))

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    print(f"OK checked {len(markdown_files)} Markdown file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
