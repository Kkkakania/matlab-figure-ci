import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
