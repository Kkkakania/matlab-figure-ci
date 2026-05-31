import re
import importlib.util
from pathlib import Path

from matlab_figure_ci import __version__


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def load_script(relative_path):
    spec = importlib.util.spec_from_file_location("script_under_test", ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def assert_toml_scalar(text, key, expected):
    pattern = rf'^{re.escape(key)}\s*=\s*"{re.escape(expected)}"$'
    assert re.search(pattern, text, flags=re.MULTILINE), f"missing {key} = {expected!r}"


def test_pyproject_core_metadata_matches_runtime_version():
    text = read_text("pyproject.toml")

    assert_toml_scalar(text, "name", "matlab-figure-ci")
    assert_toml_scalar(text, "version", __version__)
    assert_toml_scalar(text, "description", "A CI/CLI quality gate for MATLAB scientific figure repositories.")
    assert_toml_scalar(text, "readme", "README.md")
    assert_toml_scalar(text, "requires-python", ">=3.9")
    assert_toml_scalar(text, "license", "MIT")


def test_pyproject_keeps_runtime_dependencies_minimal():
    text = read_text("pyproject.toml")
    dependencies = text.split("dependencies = [", 1)[1].split("]", 1)[0]
    test_extra = text.split("test = [", 1)[1].split("]", 1)[0]
    build_extra = text.split("build = [", 1)[1].split("]", 1)[0]

    assert '"PyYAML>=6.0"' in dependencies
    assert "pytest" not in dependencies
    assert "build>=" not in dependencies
    assert "twine>=" not in dependencies
    assert '"pytest>=8.0"' in test_extra
    assert '"build>=1.2"' in build_extra
    assert '"twine>=5.0"' in build_extra


def test_console_script_points_to_cli_main():
    text = read_text("pyproject.toml")

    assert 'mfigci = "matlab_figure_ci.cli:main"' in text


def test_package_workflow_builds_checks_and_smoke_installs_wheel():
    text = read_text(".github/workflows/package.yml")

    assert 'pip install -e ".[build]"' in text
    assert "python -m build" in text
    assert "python -m twine check dist/*" in text
    assert "mfigci release-preflight --require-dist --output release-preflight.json" in text
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in text
    assert "actions/upload-artifact@v5" in text
    assert "name: release-preflight" in text
    assert "path: release-preflight.json" in text
    assert "/tmp/mfigci-wheel-smoke/bin/python -m pip install dist/*.whl" in text
    assert "/tmp/mfigci-wheel-smoke/bin/mfigci --version" in text
    assert "/tmp/mfigci-wheel-smoke/bin/mfigci --help" in text


def test_pypi_name_helper_classifies_api_status_codes():
    script = load_script("scripts/check_pypi_name.py")

    assert script.classify_status(404) == "available"
    assert script.classify_status(200) == "taken"
    assert script.classify_status(500) == "unknown"


def test_pypi_release_checklist_uses_name_helper():
    text = read_text("docs/pypi-release-checklist.md")

    assert "mfigci release-preflight" in text
    assert "mfigci release-preflight --format json" in text
    assert "mfigci release-preflight --output release-preflight.json" in text
    assert "mfigci release-preflight --require-dist --output release-preflight.json" in text
    assert "python scripts/check_pypi_name.py matlab-figure-ci" in text
    assert "exits `0` when PyPI returns `404`" in text
