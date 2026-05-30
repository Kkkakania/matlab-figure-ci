import json

from matlab_figure_ci.report import build_markdown_report, load_results
from matlab_figure_ci.result import CheckResults, Finding, GalleryItem, GalleryResults, ScanResults


def test_report_outputs_markdown_with_summary_and_findings(tmp_path):
    results = CheckResults(
        summary={"errors": 1, "warnings": 0, "files_scanned": 1},
        findings=[
            Finding(
                severity="error",
                rule_id="privacy.email",
                path="src/example.m",
                line=3,
                message="<redacted>",
            )
        ],
        scan=ScanResults(files_scanned=1),
        gallery=GalleryResults(items=[GalleryItem(status="ok", path="gallery/example.png", message="present")]),
        render={"status": "skipped", "message": "disabled"},
        config_path="mfigci.yml",
        tool_version="0.1.0",
    )

    markdown = build_markdown_report(results)

    assert "# matlab-figure-ci report" in markdown
    assert "| error | privacy.email | src/example.m | 3 | <redacted> |" in markdown


def test_load_results_requires_existing_json(tmp_path):
    missing = tmp_path / ".mfigci-results.json"

    try:
        load_results(missing)
    except FileNotFoundError as exc:
        assert "mfigci check" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")


def test_json_results_do_not_contain_privacy_match(tmp_path):
    secret = "person@example.com"
    payload = {
        "summary": {"errors": 1, "warnings": 0, "files_scanned": 1},
        "findings": [
            {
                "severity": "error",
                "rule_id": "privacy.email",
                "path": "src/example.m",
                "line": 1,
                "message": "<redacted>",
            }
        ],
        "gallery": {"items": []},
        "render": {"status": "skipped", "message": "disabled"},
        "config_path": "mfigci.yml",
        "tool_version": "0.1.0",
    }
    path = tmp_path / ".mfigci-results.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_results(path)

    assert secret not in json.dumps(loaded.to_dict())
