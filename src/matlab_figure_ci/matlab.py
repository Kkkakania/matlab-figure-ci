"""Optional MATLAB render command support."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def run_matlab_render(root: str | Path, config: dict) -> dict:
    matlab_config = config.get("matlab", {})
    env_name = str(matlab_config.get("bin_env", "MATLAB_BIN"))
    fallback = str(matlab_config.get("fallback_bin", "matlab"))
    command = str(matlab_config.get("batch_command", "run_all_figures"))
    matlab_bin = os.environ.get(env_name) or shutil.which(fallback)

    if not matlab_bin:
        return {
            "status": "error",
            "message": "MATLAB executable not found. Set MATLAB_BIN or ensure matlab is on PATH.",
            "exit_code": 3,
        }

    completed = subprocess.run(
        [matlab_bin, "-batch", command],
        cwd=Path(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return {
            "status": "error",
            "message": "MATLAB render failed.",
            "exit_code": 3,
        }
    return {"status": "ok", "message": "MATLAB render completed.", "exit_code": 0}
