#!/usr/bin/env python3
"""Check repository workflow maintenance policy."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
PACKAGE_WORKFLOW = ROOT / ".github" / "workflows" / "package.yml"


def read_workflow(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing workflow: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, workflow_name: str) -> None:
    if needle not in text:
        raise AssertionError(f"{workflow_name} missing required setting: {needle}")


def reject(text: str, needle: str, workflow_name: str) -> None:
    if needle in text:
        raise AssertionError(f"{workflow_name} contains outdated or unsafe setting: {needle}")


def check_ci_workflow(text: str) -> None:
    require(text, "actions/checkout@v6", "ci.yml")
    require(text, "actions/setup-python@v6", "ci.yml")
    require(text, "python scripts/check_markdown_links.py", "ci.yml")
    require(text, "python scripts/check_workflows.py", "ci.yml")
    reject(text, "actions/checkout@v4", "ci.yml")
    reject(text, "actions/setup-python@v4", "ci.yml")


def check_package_workflow(text: str) -> None:
    require(text, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", "package.yml")
    require(text, "actions/checkout@v6", "package.yml")
    require(text, "actions/setup-python@v6", "package.yml")
    require(text, "actions/upload-artifact@v5", "package.yml")
    require(text, "mfigci release-preflight --require-dist --output release-preflight.json", "package.yml")
    require(text, "python scripts/check_pypi_name.py matlab-figure-ci --json-out pypi-name-check.json", "package.yml")
    require(text, "name: pypi-name-check", "package.yml")
    require(text, "path: pypi-name-check.json", "package.yml")
    reject(text, "actions/checkout@v4", "package.yml")
    reject(text, "actions/setup-python@v4", "package.yml")
    reject(text, "actions/upload-artifact@v4", "package.yml")
    reject(text, "twine upload", "package.yml")
    reject(text, "pypa/gh-action-pypi-publish", "package.yml")
    reject(text, "id-token: write", "package.yml")
    reject(text, "TWINE_PASSWORD", "package.yml")


def main() -> int:
    try:
        check_ci_workflow(read_workflow(CI_WORKFLOW))
        check_package_workflow(read_workflow(PACKAGE_WORKFLOW))
    except AssertionError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    print("Workflow maintenance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
