import json
import subprocess
import sys
from pathlib import Path

from matlab_figure_ci import __version__


def run_cli(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "matlab_figure_ci.cli", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_scan_clean_project_returns_zero(tmp_path):
    (tmp_path / "gallery").mkdir()
    (tmp_path / "gallery" / "example.png").write_bytes(b"123456789")
    (tmp_path / "script.m").write_text("plot(1:10)\n", encoding="utf-8")

    result = run_cli(["scan"], tmp_path)

    assert result.returncode == 0
    assert "0 error" in result.stdout


def test_scan_risky_project_returns_nonzero_and_redacts(tmp_path):
    secret = "person@example.com"
    (tmp_path / "script.m").write_text(secret, encoding="utf-8")

    result = run_cli(["scan"], tmp_path)

    assert result.returncode == 1
    assert "<redacted>" in result.stdout
    assert secret not in result.stdout
    assert secret not in result.stderr


def test_scan_can_fail_on_warnings_when_requested(tmp_path):
    (tmp_path / "script.m").write_text("% Author: example maintainer\nplot(1:10)\n", encoding="utf-8")

    default = run_cli(["scan"], tmp_path)
    strict = run_cli(["scan", "--fail-on-warnings"], tmp_path)

    assert default.returncode == 0
    assert "1 warning" in default.stdout
    assert strict.returncode == 1
    assert "1 warning" in strict.stdout


def test_check_generates_markdown_and_json_results(tmp_path):
    gallery = tmp_path / "gallery"
    gallery.mkdir()
    (gallery / "example.png").write_bytes(b"123456789")
    (tmp_path / "mfigci.yml").write_text(
        """
gallery:
  expected:
    - example.png
  min_size_bytes: 8
""",
        encoding="utf-8",
    )

    result = run_cli(["check", "--report", "mfigci-report.md"], tmp_path)

    assert result.returncode == 0
    assert (tmp_path / "mfigci-report.md").exists()
    assert (tmp_path / ".mfigci-results.json").exists()
    payload = json.loads((tmp_path / ".mfigci-results.json").read_text(encoding="utf-8"))
    assert payload["summary"]["errors"] == 0


def test_check_can_fail_on_warnings_when_requested(tmp_path):
    (tmp_path / "script.m").write_text("% Author: example maintainer\nplot(1:10)\n", encoding="utf-8")
    (tmp_path / "gallery").mkdir()
    (tmp_path / "mfigci.yml").write_text("gallery:\n  expected: []\n", encoding="utf-8")

    default = run_cli(["check"], tmp_path)
    strict = run_cli(["check", "--fail-on-warnings"], tmp_path)

    assert default.returncode == 0
    assert strict.returncode == 1
    assert (tmp_path / ".mfigci-results.json").exists()


def test_report_reads_existing_json_and_does_not_make_empty_report(tmp_path):
    missing = run_cli(["report", "--output", "report.md"], tmp_path)
    assert missing.returncode == 2
    assert not (tmp_path / "report.md").exists()

    (tmp_path / ".mfigci-results.json").write_text(
        json.dumps(
            {
                "summary": {"errors": 0, "warnings": 0, "files_scanned": 0},
                "findings": [],
                "scan": {"files_scanned": 0},
                "gallery": {"items": []},
                "render": {"status": "skipped", "message": "disabled"},
                "config_path": "mfigci.yml",
                "tool_version": "0.1.0",
            }
        ),
        encoding="utf-8",
    )

    ok = run_cli(["report", "--output", "report.md"], tmp_path)

    assert ok.returncode == 0
    assert "# matlab-figure-ci report" in (tmp_path / "report.md").read_text(encoding="utf-8")


def test_report_can_write_pr_comment_style(tmp_path):
    (tmp_path / ".mfigci-results.json").write_text(
        json.dumps(
            {
                "summary": {"errors": 1, "warnings": 0, "files_scanned": 1, "gallery_checks": 0},
                "findings": [
                    {
                        "severity": "error",
                        "rule_id": "privacy.email",
                        "path": "src/example.m",
                        "line": 1,
                        "message": "<redacted>",
                    }
                ],
                "scan": {"files_scanned": 1},
                "gallery": {"items": []},
                "render": {"status": "skipped", "message": "disabled"},
                "config_path": "mfigci.yml",
                "tool_version": "0.1.0",
            }
        ),
        encoding="utf-8",
    )

    result = run_cli(["report", "--style", "pr-comment", "--output", "pr-comment.md"], tmp_path)

    output = (tmp_path / "pr-comment.md").read_text(encoding="utf-8")
    assert result.returncode == 0
    assert output.startswith("### matlab-figure-ci check")
    assert "| error | privacy.email | src/example.m:1 | <redacted> |" in output


def test_report_can_write_public_json_format(tmp_path):
    secret = "person@example.com"
    (tmp_path / ".mfigci-results.json").write_text(
        json.dumps(
            {
                "summary": {"errors": 1, "warnings": 0, "files_scanned": 1, "gallery_checks": 0},
                "findings": [
                    {
                        "severity": "error",
                        "rule_id": "privacy.email",
                        "path": "src/example.m",
                        "line": 1,
                        "message": "<redacted>",
                    }
                ],
                "scan": {"files_scanned": 1},
                "gallery": {"items": []},
                "render": {"status": "skipped", "message": "disabled"},
                "config_path": "mfigci.yml",
                "tool_version": "0.1.0",
            }
        ),
        encoding="utf-8",
    )

    result = run_cli(["report", "--format", "json", "--output", "mfigci-report.json"], tmp_path)

    output = (tmp_path / "mfigci-report.json").read_text(encoding="utf-8")
    payload = json.loads(output)
    assert result.returncode == 0
    assert payload["schema_version"] == "mfigci.report.v1"
    assert payload["findings"][0]["message"] == "<redacted>"
    assert secret not in output


def test_init_does_not_overwrite_without_force(tmp_path):
    existing = tmp_path / "mfigci.yml"
    existing.write_text("project:\n  name: keep-me\n", encoding="utf-8")

    result = run_cli(["init"], tmp_path)

    assert result.returncode == 0
    assert "skipped" in result.stdout
    assert "keep-me" in existing.read_text(encoding="utf-8")

    forced = run_cli(["init", "--force"], tmp_path)

    assert forced.returncode == 0
    assert "keep-me" not in existing.read_text(encoding="utf-8")


def test_init_workflow_uses_current_release_tag(tmp_path):
    result = run_cli(["init"], tmp_path)

    workflow = (tmp_path / ".github" / "workflows" / "figure-quality.yml").read_text(encoding="utf-8")
    assert result.returncode == 0
    assert f"matlab-figure-ci.git@v{__version__}" in workflow
    assert "matlab-figure-ci.git@v0.1.0" not in workflow


def test_doctor_shows_safe_defaults_without_config(tmp_path):
    result = run_cli(["doctor"], tmp_path)

    assert result.returncode == 0
    assert "Config path: mfigci.yml (not found; using defaults)" in result.stdout
    assert "Project: matlab-figure-ci-project" in result.stdout
    assert "Scan include: ." in result.stdout
    assert "Gallery expected files: 0" in result.stdout
    assert "MATLAB render: disabled" in result.stdout
    assert str(tmp_path) not in result.stdout


def test_doctor_shows_effective_config_summary(tmp_path):
    (tmp_path / "mfigci.yml").write_text(
        """
project:
  name: demo-gallery
presets:
  - matlab-figures
scan:
  include:
    - src
  exclude:
    - raw
gallery:
  path: gallery
  expected:
    - a.png
    - b.svg
matlab:
  enabled: true
  bin_env: MATLAB_BIN
""",
        encoding="utf-8",
    )

    result = run_cli(["doctor"], tmp_path)

    assert result.returncode == 0
    assert "Config path: mfigci.yml" in result.stdout
    assert "Project: demo-gallery" in result.stdout
    assert "Presets: matlab-figures" in result.stdout
    assert "Scan include: src" in result.stdout
    assert "Scan exclude: raw" in result.stdout
    assert "Gallery path: gallery" in result.stdout
    assert "Gallery expected files: 2" in result.stdout
    assert "Privacy scan: enabled" in result.stdout
    assert "Provenance scan: enabled" in result.stdout
    assert "MATLAB render: enabled (env: MATLAB_BIN)" in result.stdout
    assert str(tmp_path) not in result.stdout


def test_rules_lists_effective_policy_rules(tmp_path):
    result = run_cli(["rules"], tmp_path)

    assert result.returncode == 0
    assert "matlab-figure-ci rules" in result.stdout
    assert "Privacy rules: enabled" in result.stdout
    assert "privacy.email error redacted" in result.stdout
    assert "Provenance rules: enabled" in result.stdout
    assert "provenance.author_marker warning pattern matched" in result.stdout
    assert "Extension errors: .p, .mat, .fig, .doc, .docx, .xlsx, .vsd" in result.stdout
    assert "Extension warnings: .pdf, .mlx, .zip" in result.stdout
    assert str(tmp_path) not in result.stdout


def test_rules_respects_disabled_sections_and_custom_extensions(tmp_path):
    (tmp_path / "mfigci.yml").write_text(
        """
privacy:
  enabled: false
provenance:
  enabled: false
extensions:
  error:
    - ".raw"
  warning: []
""",
        encoding="utf-8",
    )

    result = run_cli(["rules", "--config", "mfigci.yml"], tmp_path)

    assert result.returncode == 0
    assert "Privacy rules: disabled" in result.stdout
    assert "Provenance rules: disabled" in result.stdout
    assert "Extension errors: .raw" in result.stdout
    assert "Extension warnings: (none)" in result.stdout


def test_render_without_matlab_reports_clear_error(tmp_path):
    (tmp_path / "mfigci.yml").write_text(
        """
matlab:
  enabled: true
  bin_env: "MISSING_MATLAB_BIN_FOR_TEST"
  fallback_bin: "definitely-not-a-matlab-binary"
  batch_command: "run_all_figures"
""",
        encoding="utf-8",
    )

    result = run_cli(["render"], tmp_path)

    assert result.returncode == 3
    assert "MATLAB executable not found" in result.stdout
