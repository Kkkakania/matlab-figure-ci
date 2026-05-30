from pathlib import Path

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


def test_privacy_scan_matches_chinese_sensitive_keywords(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "notes.md").write_text("这里有手机号字段。\n", encoding="utf-8")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 1
    assert result.findings[0].rule_id == "privacy.sensitive_keywords"
    assert result.findings[0].message == "<redacted>"
