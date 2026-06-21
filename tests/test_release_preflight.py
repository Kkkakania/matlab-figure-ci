from pathlib import Path

from matlab_figure_ci import __version__
from matlab_figure_ci.release import (
    PreflightItem,
    check_package_workflow_does_not_publish,
    classify_pypi_status,
    release_preflight_exit_code,
    release_preflight_payload,
    release_preflight_summary,
    run_release_preflight,
)


ROOT = Path(__file__).resolve().parents[1]


def test_release_preflight_passes_for_repository_metadata():
    items = run_release_preflight(
        ROOT,
        expected_name="matlab-figure-ci",
        expected_version=__version__,
    )

    assert release_preflight_exit_code(items) == 0
    assert any(item.check == "pyproject" and item.message == f'version = "{__version__}"' for item in items)
    assert any(item.check == "package-workflow" and "smoke installs" in item.message for item in items)
    assert any(item.check == "package-workflow" and "checks PyPI package name" in item.message for item in items)
    assert any(item.check == "package-workflow" and "uploads PyPI name-check artifact" in item.message for item in items)
    assert any(item.check == "package-workflow" and "does not publish to PyPI" in item.message for item in items)


def test_release_preflight_can_require_dist_outputs(tmp_path):
    for relative_path in [
        "pyproject.toml",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "src/matlab_figure_ci/cli.py",
        ".github/workflows/package.yml",
    ]:
        source = ROOT / relative_path
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    items = run_release_preflight(
        tmp_path,
        expected_name="matlab-figure-ci",
        expected_version=__version__,
        require_dist=True,
    )

    assert release_preflight_exit_code(items) == 1
    assert any(item.check == "dist" and "dist/*.whl missing" in item.message for item in items)
    assert any(item.check == "dist" and "dist/*.tar.gz missing" in item.message for item in items)


def test_release_preflight_detects_metadata_drift(tmp_path):
    for relative_path in [
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "src/matlab_figure_ci/cli.py",
        ".github/workflows/package.yml",
    ]:
        source = ROOT / relative_path
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8").replace(f'version = "{__version__}"', 'version = "0.0.0"'),
        encoding="utf-8",
    )

    items = run_release_preflight(
        tmp_path,
        expected_name="matlab-figure-ci",
        expected_version=__version__,
    )

    assert release_preflight_exit_code(items) == 1
    assert any(item.status == "error" and "pyproject missing version" in item.message for item in items)


def test_release_preflight_exit_code_can_fail_on_warnings():
    items = [PreflightItem("warning", "pypi-name", "network unavailable")]

    assert release_preflight_exit_code(items) == 0
    assert release_preflight_exit_code(items, fail_on_warnings=True) == 1


def test_release_preflight_payload_is_machine_readable():
    items = [
        PreflightItem("ok", "required-file", "README.md present"),
        PreflightItem("warning", "pypi-name", "network unavailable"),
    ]

    assert release_preflight_summary(items) == {"errors": 0, "warnings": 1, "checks": 2}
    payload = release_preflight_payload(
        items,
        exit_code=0,
        project_name="matlab-figure-ci",
        project_version=__version__,
    )

    assert payload["projectName"] == "matlab-figure-ci"
    assert payload["projectVersion"] == __version__
    assert payload["summary"]["warnings"] == 1
    assert payload["exitCode"] == 0
    assert payload["items"][0] == {
        "status": "ok",
        "check": "required-file",
        "message": "README.md present",
    }


def test_classify_pypi_status_codes():
    assert classify_pypi_status(404) == "available"
    assert classify_pypi_status(200) == "taken"
    assert classify_pypi_status(500) == "unknown"


def test_package_workflow_publish_guard_rejects_upload_markers():
    clean = check_package_workflow_does_not_publish("python -m build\npython -m twine check dist/*\n")
    direct_upload = check_package_workflow_does_not_publish("python -m twine upload dist/*\n")
    trusted_publish = check_package_workflow_does_not_publish("uses: pypa/gh-action-pypi-publish@release/v1\n")

    assert clean.status == "ok"
    assert direct_upload.status == "error"
    assert "twine upload" in direct_upload.message
    assert trusted_publish.status == "error"
    assert "pypa/gh-action-pypi-publish" in trusted_publish.message
