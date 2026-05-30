import json
import subprocess
import sys
from pathlib import Path


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
