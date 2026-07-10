#!/usr/bin/env python3
"""Check repository workflow maintenance policy."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
PACKAGE_WORKFLOW = ROOT / ".github" / "workflows" / "package.yml"
TRIAGE_WORKFLOW = ROOT / ".github" / "workflows" / "issue-triage.yml"
DEPENDABOT_CONFIG = ROOT / ".github" / "dependabot.yml"


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


def require_read_only_contents_permission(text: str, workflow_name: str) -> None:
    reject(text, "contents: write", workflow_name)
    require(text, "permissions:", workflow_name)
    require(text, "contents: read", workflow_name)


def check_ci_workflow(text: str) -> None:
    require_read_only_contents_permission(text, "ci.yml")
    require(text, "actions/checkout@", "ci.yml")
    require(text, "actions/setup-python@", "ci.yml")
    require(text, "python scripts/check_markdown_links.py", "ci.yml")
    require(text, "python scripts/check_workflows.py", "ci.yml")
    reject(text, "actions/checkout@v4", "ci.yml")
    reject(text, "actions/checkout@v5", "ci.yml")
    reject(text, "actions/setup-python@v4", "ci.yml")
    reject(text, "actions/setup-python@v5", "ci.yml")


def check_package_workflow(text: str) -> None:
    require_read_only_contents_permission(text, "package.yml")
    require(text, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", "package.yml")
    require(text, "actions/checkout@", "package.yml")
    require(text, "actions/setup-python@", "package.yml")
    require(text, "actions/upload-artifact@", "package.yml")
    require(text, "mfigci release-preflight --require-dist --check-pypi-name --output release-preflight.json", "package.yml")
    require(text, "python scripts/check_pypi_name.py matlab-figure-ci --json-out pypi-name-check.json", "package.yml")
    require(text, "name: pypi-name-check", "package.yml")
    require(text, "path: pypi-name-check.json", "package.yml")
    reject(text, "actions/checkout@v4", "package.yml")
    reject(text, "actions/checkout@v5", "package.yml")
    reject(text, "actions/setup-python@v4", "package.yml")
    reject(text, "actions/setup-python@v5", "package.yml")
    reject(text, "actions/upload-artifact@v4", "package.yml")
    reject(text, "twine upload", "package.yml")
    reject(text, "pypa/gh-action-pypi-publish", "package.yml")
    reject(text, "id-token: write", "package.yml")
    reject(text, "TWINE_PASSWORD", "package.yml")


def check_issue_triage_workflow(text: str) -> None:
    require(text, "issues:", "issue-triage.yml")
    require(text, "types: [opened]", "issue-triage.yml")
    require(text, "issues: write", "issue-triage.yml")
    require(text, "matlab-figure-ecosystem-triage", "issue-triage.yml")
    require(text, "gh issue comment", "issue-triage.yml")
    require(text, "minimal fixture or synthetic project", "issue-triage.yml")
    require(text, "Kkkakania/matlab-scientific-figures#31", "issue-triage.yml")
    require(text, "Awaiting feedback", "issue-triage.yml")
    reject(text, "project:", "issue-triage.yml")
    reject(text, "read:project", "issue-triage.yml")


def check_dependabot_config(text: str) -> None:
    require(text, "version: 2", "dependabot.yml")
    require(text, "package-ecosystem: github-actions", "dependabot.yml")
    require(text, 'directory: "/"', "dependabot.yml")
    require(text, "interval: weekly", "dependabot.yml")
    require(text, "open-pull-requests-limit: 5", "dependabot.yml")
    require(text, "prefix: ci", "dependabot.yml")
    reject(text, "package-ecosystem: pip", "dependabot.yml")
    reject(text, "package-ecosystem: npm", "dependabot.yml")
    reject(text, "interval: daily", "dependabot.yml")
    reject(text, "open-pull-requests-limit: 20", "dependabot.yml")


def main() -> int:
    try:
        check_ci_workflow(read_workflow(CI_WORKFLOW))
        check_package_workflow(read_workflow(PACKAGE_WORKFLOW))
        check_issue_triage_workflow(read_workflow(TRIAGE_WORKFLOW))
        check_dependabot_config(read_workflow(DEPENDABOT_CONFIG))
    except AssertionError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    print("Workflow maintenance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
