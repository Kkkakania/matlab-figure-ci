"""Release preflight checks for packaging matlab-figure-ci."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreflightItem:
    """One release preflight check result."""

    status: str
    check: str
    message: str


def release_preflight_summary(items: list[PreflightItem]) -> dict[str, int]:
    """Return counts for a release preflight result set."""

    return {
        "errors": sum(1 for item in items if item.status == "error"),
        "warnings": sum(1 for item in items if item.status == "warning"),
        "checks": len(items),
    }


def release_preflight_payload(items: list[PreflightItem], *, exit_code: int) -> dict:
    """Return a machine-readable release preflight payload."""

    return {
        "summary": release_preflight_summary(items),
        "exitCode": exit_code,
        "items": [
            {
                "status": item.status,
                "check": item.check,
                "message": item.message,
            }
            for item in items
        ],
    }


def _read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def _has_toml_scalar(text: str, key: str, expected: str) -> bool:
    pattern = rf'^{re.escape(key)}\s*=\s*"{re.escape(expected)}"$'
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def classify_pypi_status(status_code: int) -> str:
    """Classify the PyPI JSON API HTTP status for a project name."""

    if status_code == 404:
        return "available"
    if status_code == 200:
        return "taken"
    return "unknown"


def check_pypi_project_name(name: str, timeout: float = 10.0) -> PreflightItem:
    """Check whether a PyPI project name appears available."""

    url = f"https://pypi.org/pypi/{name}/json"
    request = urllib.request.Request(url, headers={"User-Agent": "matlab-figure-ci-release-preflight"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = classify_pypi_status(response.status)
    except urllib.error.HTTPError as exc:
        status = classify_pypi_status(exc.code)
    except urllib.error.URLError as exc:
        return PreflightItem("warning", "pypi-name", f"{url} could not be checked: {exc.reason}")

    if status == "available":
        return PreflightItem("ok", "pypi-name", f"{name} is not present on PyPI")
    if status == "taken":
        return PreflightItem("error", "pypi-name", f"{name} already exists on PyPI")
    return PreflightItem("warning", "pypi-name", f"{url} returned an unexpected status")


def run_release_preflight(
    root: str | Path,
    *,
    expected_name: str,
    expected_version: str,
    check_pypi_name: bool = False,
    require_dist: bool = False,
) -> list[PreflightItem]:
    """Run local release-readiness checks without publishing anything."""

    root_path = Path(root).resolve()
    items: list[PreflightItem] = []

    required_files = [
        "pyproject.toml",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "src/matlab_figure_ci/cli.py",
        ".github/workflows/package.yml",
    ]
    for relative_path in required_files:
        path = root_path / relative_path
        status = "ok" if path.exists() else "error"
        message = f"{relative_path} present" if path.exists() else f"{relative_path} missing"
        items.append(PreflightItem(status, "required-file", message))

    pyproject_path = root_path / "pyproject.toml"
    if pyproject_path.exists():
        pyproject = _read_text(root_path, "pyproject.toml")
        metadata_expectations = {
            "name": expected_name,
            "version": expected_version,
            "readme": "README.md",
            "requires-python": ">=3.9",
            "license": "MIT",
        }
        for key, expected in metadata_expectations.items():
            ok = _has_toml_scalar(pyproject, key, expected)
            items.append(
                PreflightItem(
                    "ok" if ok else "error",
                    "pyproject",
                    f'{key} = "{expected}"' if ok else f'pyproject missing {key} = "{expected}"',
                )
            )
        script_ok = 'mfigci = "matlab_figure_ci.cli:main"' in pyproject
        items.append(
            PreflightItem(
                "ok" if script_ok else "error",
                "console-script",
                "mfigci console script configured" if script_ok else "mfigci console script missing",
            )
        )

    changelog_path = root_path / "CHANGELOG.md"
    if changelog_path.exists():
        changelog = _read_text(root_path, "CHANGELOG.md")
        tag = f"v{expected_version}"
        has_entry = f"## {tag} -" in changelog
        items.append(
            PreflightItem(
                "ok" if has_entry else "error",
                "changelog",
                f"{tag} changelog entry present" if has_entry else f"{tag} changelog entry missing",
            )
        )

    package_workflow_path = root_path / ".github/workflows/package.yml"
    if package_workflow_path.exists():
        workflow = _read_text(root_path, ".github/workflows/package.yml")
        workflow_checks = {
            "python -m build": "builds source and wheel distributions",
            "python -m twine check dist/*": "checks distribution metadata",
            "python -m pip install dist/*.whl": "smoke installs built wheel",
            "mfigci --version": "checks installed console script version",
            "mfigci --help": "checks installed console script help",
        }
        for needle, description in workflow_checks.items():
            ok = needle in workflow
            items.append(
                PreflightItem(
                    "ok" if ok else "error",
                    "package-workflow",
                    description if ok else f"package workflow missing: {needle}",
                )
            )

    if require_dist:
        dist_path = root_path / "dist"
        wheels = list(dist_path.glob("*.whl")) if dist_path.exists() else []
        source_archives = list(dist_path.glob("*.tar.gz")) if dist_path.exists() else []
        items.append(
            PreflightItem(
                "ok" if wheels else "error",
                "dist",
                "wheel distribution present" if wheels else "dist/*.whl missing; run python -m build",
            )
        )
        items.append(
            PreflightItem(
                "ok" if source_archives else "error",
                "dist",
                "source distribution present" if source_archives else "dist/*.tar.gz missing; run python -m build",
            )
        )

    if check_pypi_name:
        items.append(check_pypi_project_name(expected_name))

    return items


def release_preflight_exit_code(items: list[PreflightItem], fail_on_warnings: bool = False) -> int:
    """Return a policy exit code for preflight results."""

    if any(item.status == "error" for item in items):
        return 1
    if fail_on_warnings and any(item.status == "warning" for item in items):
        return 1
    return 0
