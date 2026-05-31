import json
import os
import subprocess
import sys
from pathlib import Path

from matlab_figure_ci import __version__


def run_cli(args, cwd, env=None):
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "matlab_figure_ci.cli", *args],
        cwd=cwd,
        env=process_env,
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


def test_scan_can_fail_on_warnings_from_config(tmp_path):
    (tmp_path / "script.m").write_text("% Author: example maintainer\nplot(1:10)\n", encoding="utf-8")
    (tmp_path / "mfigci.yml").write_text(
        """
strict:
  fail_on_warnings: true
""",
        encoding="utf-8",
    )

    result = run_cli(["scan", "--config", "mfigci.yml"], tmp_path)

    assert result.returncode == 1
    assert "1 warning" in result.stdout


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


def test_check_preserves_failed_matlab_output_excerpts(tmp_path):
    fake_matlab = tmp_path / "fake-matlab"
    fake_matlab.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"Undefined function or variable 'run_all_figures'.\"\n"
        "echo \"Error using run_all_figures\" >&2\n"
        "exit 7\n",
        encoding="utf-8",
    )
    fake_matlab.chmod(0o755)
    (tmp_path / "gallery").mkdir()
    (tmp_path / "mfigci.yml").write_text(
        """
gallery:
  expected: []
matlab:
  enabled: true
  bin_env: "MFIGCI_TEST_MATLAB"
  batch_command: "run_all_figures"
""",
        encoding="utf-8",
    )

    result = run_cli(
        ["check", "--config", "mfigci.yml", "--report", "mfigci-report.md"],
        tmp_path,
        env={"MFIGCI_TEST_MATLAB": str(fake_matlab)},
    )

    report = (tmp_path / "mfigci-report.md").read_text(encoding="utf-8")
    payload = json.loads((tmp_path / ".mfigci-results.json").read_text(encoding="utf-8"))
    render = payload["render"]
    assert result.returncode == 3
    assert render["status"] == "error"
    assert render["process_exit_code"] == 7
    assert "Undefined function" in render["stdout_excerpt"]
    assert "Error using run_all_figures" in render["stderr_excerpt"]
    assert "MATLAB stdout excerpt" in report
    assert "Undefined function" in report
    assert "MATLAB process exit code: 7" in result.stdout


def test_check_can_fail_on_warnings_when_requested(tmp_path):
    (tmp_path / "script.m").write_text("% Author: example maintainer\nplot(1:10)\n", encoding="utf-8")
    (tmp_path / "gallery").mkdir()
    (tmp_path / "mfigci.yml").write_text("gallery:\n  expected: []\n", encoding="utf-8")

    default = run_cli(["check"], tmp_path)
    strict = run_cli(["check", "--fail-on-warnings"], tmp_path)

    assert default.returncode == 0
    assert strict.returncode == 1
    assert (tmp_path / ".mfigci-results.json").exists()


def test_check_can_fail_on_warnings_from_config(tmp_path):
    (tmp_path / "script.m").write_text("% Author: example maintainer\nplot(1:10)\n", encoding="utf-8")
    (tmp_path / "gallery").mkdir()
    (tmp_path / "mfigci.yml").write_text(
        """
strict:
  fail_on_warnings: true
gallery:
  expected: []
""",
        encoding="utf-8",
    )

    result = run_cli(["check", "--config", "mfigci.yml"], tmp_path)

    assert result.returncode == 1
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
    assert "Optional: run `mfigci init --gitignore` to ignore local report artifacts." in result.stdout
    assert "Next: run `mfigci doctor --config mfigci.yml`" in result.stdout
    assert "Then run `mfigci check --config mfigci.yml --report mfigci-report.md`" in result.stdout
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
    assert "permissions:\n  contents: read" in workflow
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in workflow
    assert "actions/checkout@v6" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "actions/upload-artifact@v5" in workflow
    assert "actions/upload-artifact@v4" not in workflow
    assert "Show effective mfigci policy" in workflow
    assert "mfigci rules --config mfigci.yml" in workflow


def test_init_config_excludes_reviewed_root_license(tmp_path):
    result = run_cli(["init"], tmp_path)

    config_text = (tmp_path / "mfigci.yml").read_text(encoding="utf-8")
    assert result.returncode == 0
    assert '    - "LICENSE"' in config_text


def test_init_can_append_report_artifacts_to_gitignore(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("dist/\n", encoding="utf-8")

    result = run_cli(["init", "--gitignore"], tmp_path)

    assert result.returncode == 0
    assert "updated .gitignore with mfigci report artifacts" in result.stdout
    assert gitignore.read_text(encoding="utf-8") == (
        "dist/\n\n"
        "# matlab-figure-ci local reports\n"
        "mfigci-report.md\n"
        ".mfigci-results.json\n"
    )

    second = run_cli(["init", "--gitignore"], tmp_path)

    assert second.returncode == 0
    assert "already contains mfigci report artifacts" in second.stdout
    assert gitignore.read_text(encoding="utf-8").count("mfigci-report.md") == 1


def test_doctor_shows_safe_defaults_without_config(tmp_path):
    result = run_cli(["doctor"], tmp_path)

    assert result.returncode == 0
    assert "Config path: mfigci.yml (not found; using defaults)" in result.stdout
    assert "Project: matlab-figure-ci-project" in result.stdout
    assert "Scan include: ." in result.stdout
    assert "Gallery expected files: 0" in result.stdout
    assert "Privacy rules: 3" in result.stdout
    assert "Provenance rules: 3" in result.stdout
    assert "Extension errors: 7" in result.stdout
    assert "Extension warnings: 3" in result.stdout
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


def test_release_preflight_passes_for_current_repository():
    result = run_cli(["release-preflight"], Path(__file__).resolve().parents[1])

    assert result.returncode == 0
    assert "OK pyproject" in result.stdout
    assert "OK package-workflow" in result.stdout
    assert "0 error(s), 0 warning(s)" in result.stdout


def test_release_preflight_can_require_dist_outputs(tmp_path):
    result = run_cli(["release-preflight", "--require-dist"], Path(__file__).resolve().parents[1])

    assert result.returncode == 1
    assert "ERROR dist dist/*.whl missing" in result.stdout
    assert "ERROR dist dist/*.tar.gz missing" in result.stdout


def test_release_preflight_can_emit_json():
    result = run_cli(["release-preflight", "--format", "json"], Path(__file__).resolve().parents[1])

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["warnings"] == 0
    assert payload["exitCode"] == 0
    assert any(item["check"] == "pyproject" for item in payload["items"])
    assert "OK pyproject" not in result.stdout


def test_release_preflight_can_write_json_output(tmp_path):
    output = tmp_path / "release-preflight.json"
    result = run_cli(
        ["release-preflight", "--output", str(output)],
        Path(__file__).resolve().parents[1],
    )

    assert result.returncode == 0
    assert "0 error(s), 0 warning(s)" in result.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["errors"] == 0
    assert payload["exitCode"] == 0
    assert any(item["check"] == "package-workflow" for item in payload["items"])


def test_invalid_config_returns_usage_error_without_traceback(tmp_path):
    (tmp_path / "mfigci.yml").write_text(
        """
provenance:
  rules:
    - id: provenance.author_marker
      pattern: Author
      severity: blocker
""",
        encoding="utf-8",
    )

    result = run_cli(["scan", "--config", "mfigci.yml"], tmp_path)

    assert result.returncode == 2
    assert "Configuration error:" in result.stdout
    assert "provenance.rules[0].severity" in result.stdout
    assert "Traceback" not in result.stderr


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
