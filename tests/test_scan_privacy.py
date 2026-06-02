from pathlib import Path

import pytest

from matlab_figure_ci.config import load_config
from matlab_figure_ci.scanners import run_scan


def test_privacy_scan_matches_email_and_redacts_everywhere(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    secret = "person@example.com"
    (project / "example.m").write_text(f"value = '{secret}';\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 1
    finding = result.findings[0]
    assert finding.rule_id == "privacy.email"
    assert finding.message == "<redacted>"
    assert secret not in finding.to_dict()["message"]


def test_privacy_scan_matches_local_absolute_path_without_leaking(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    secret = "/Users/example/Desktop/private-data"
    (project / "example.m").write_text(f"source = '{secret}';\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    messages = " ".join(f.message for f in result.findings)
    assert result.error_count == 1
    assert "<redacted>" in messages
    assert secret not in messages


@pytest.mark.parametrize(
    "secret",
    [
        "/users/example/Desktop/private-data",
        "/home/example/private-data",
        "/mnt/c/Users/example/private-data",
        "c:\\users\\example\\private-data",
        "C:\\Users\\example\\private-data",
        "%USERPROFILE%\\private-data",
        "/workspaces/private-repo/private-data",
        "/Volumes/External/private-data",
    ],
)
def test_privacy_scan_matches_common_local_path_variants_without_leaking(tmp_path, secret):
    project = tmp_path / "project"
    project.mkdir()
    (project / "example.m").write_text(f"source = '{secret}';\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    messages = " ".join(f.message for f in result.findings)
    payload = " ".join(str(finding.to_dict()) for finding in result.findings)
    assert result.error_count == 1
    assert result.findings[0].rule_id == "privacy.local_absolute_path"
    assert "<redacted>" in messages
    assert secret not in messages
    assert secret not in payload


def test_privacy_scan_matches_chinese_sensitive_keywords(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "notes.md").write_text("这里有手机号字段。\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 1
    assert result.findings[0].rule_id == "privacy.sensitive_keywords"
    assert result.findings[0].message == "<redacted>"


def test_default_scan_excludes_globbed_local_venv_directories(tmp_path):
    project = tmp_path / "project"
    hidden = project / ".venv-mfigci"
    hidden.mkdir(parents=True)
    (hidden / "script.m").write_text("person@example.com\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 0
    assert result.files_scanned == 0


def test_default_scan_excludes_notebook_checkpoint_directories(tmp_path):
    project = tmp_path / "project"
    hidden = project / ".ipynb_checkpoints"
    hidden.mkdir(parents=True)
    (hidden / "notes.md").write_text("person@example.com\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 0
    assert result.files_scanned == 0
