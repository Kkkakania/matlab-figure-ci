"""Optional MATLAB render command support."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

MAX_RENDER_EXCERPT_CHARS = 4000
MAC_HOME_PATTERN = "/" + "Users" + r"/[^\s]+"
LINUX_HOME_PATTERN = "/" + "home" + r"/[^\s]+"
WINDOWS_HOME_PATTERN = "C:" + r"\\Users\\[^\s]+"
SENSITIVE_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(f"({MAC_HOME_PATTERN}|{LINUX_HOME_PATTERN}|{WINDOWS_HOME_PATTERN})"),
]


def _redact(text: str) -> str:
    redacted = text
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub("<redacted>", redacted)
    return redacted


def _excerpt(text: str, limit: int = MAX_RENDER_EXCERPT_CHARS) -> str:
    cleaned = _redact(text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 40].rstrip() + "\n... truncated by matlab-figure-ci ..."


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
            "message": f"MATLAB render failed with exit code {completed.returncode}.",
            "exit_code": 3,
            "process_exit_code": completed.returncode,
            "stdout_excerpt": _excerpt(completed.stdout),
            "stderr_excerpt": _excerpt(completed.stderr),
        }
    return {"status": "ok", "message": "MATLAB render completed.", "exit_code": 0}
