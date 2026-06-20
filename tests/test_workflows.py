import subprocess
import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_workflow_script():
    spec = importlib.util.spec_from_file_location("check_workflows", ROOT / "scripts" / "check_workflows.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_workflow_maintenance_script_passes_for_repository():
    result = subprocess.run(
        [sys.executable, "scripts/check_workflows.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Workflow maintenance checks passed." in result.stdout


def test_ci_workflow_check_rejects_old_actions():
    script = load_workflow_script()

    old_checkout = """
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v6
      - run: python scripts/check_markdown_links.py
      - run: python scripts/check_workflows.py
    """
    old_setup_python = old_checkout.replace("actions/checkout@v4", "actions/checkout@v6").replace(
        "actions/setup-python@v6",
        "actions/setup-python@v4",
    )

    for workflow in [old_checkout, old_setup_python]:
        try:
            script.check_ci_workflow(workflow)
        except AssertionError as exc:
            assert "ci.yml" in str(exc)
        else:
            raise AssertionError("outdated CI workflow action was accepted")


def test_package_workflow_check_rejects_old_actions_and_publish_markers():
    script = load_workflow_script()
    base = """
    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
      - uses: actions/upload-artifact@v5
      - run: mfigci release-preflight --require-dist --output release-preflight.json
      - run: python scripts/check_pypi_name.py matlab-figure-ci --json-out pypi-name-check.json
    """

    bad_workflows = [
        base.replace("actions/checkout@v6", "actions/checkout@v4"),
        base.replace("actions/setup-python@v6", "actions/setup-python@v4"),
        base.replace("actions/upload-artifact@v5", "actions/upload-artifact@v4"),
        base + "\n      - run: python -m twine upload dist/*\n",
        base + "\n      - uses: pypa/gh-action-pypi-publish@release/v1\n",
        base + "\npermissions:\n  id-token: write\n",
        base + "\nTWINE_PASSWORD: secret\n",
    ]

    for workflow in bad_workflows:
        try:
            script.check_package_workflow(workflow)
        except AssertionError as exc:
            assert "package.yml" in str(exc)
        else:
            raise AssertionError("unsafe package workflow was accepted")


def test_issue_triage_workflow_check_rejects_project_scope_markers():
    script = load_workflow_script()
    base = """
on:
  issues:
    types: [opened]
permissions:
  contents: read
  issues: write
jobs:
  checklist:
    steps:
      - run: |
          echo matlab-figure-ecosystem-triage
          echo "minimal fixture or synthetic project"
          echo "Kkkakania/matlab-scientific-figures#31"
          echo "Awaiting feedback"
          gh issue comment "$ISSUE_URL" --body-file /tmp/triage-comment.md
"""

    script.check_issue_triage_workflow(base)

    for workflow in [base + "\n  project: read\n", base + "\n  read:project\n"]:
        try:
            script.check_issue_triage_workflow(workflow)
        except AssertionError as exc:
            assert "issue-triage.yml" in str(exc)
        else:
            raise AssertionError("project-scoped triage workflow was accepted")
