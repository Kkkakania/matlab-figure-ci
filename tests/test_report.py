import json

from matlab_figure_ci.report import build_json_report, build_markdown_report, build_pr_comment_report, load_results
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


def test_pr_comment_report_is_compact_and_redacted():
    secret = "person@example.com"
    results = CheckResults(
        summary={"errors": 1, "warnings": 1, "files_scanned": 8, "gallery_checks": 2},
        findings=[
            Finding(
                severity="error",
                rule_id="privacy.email",
                path="src/example.m",
                line=3,
                message="<redacted>",
            ),
            Finding(
                severity="warning",
                rule_id="provenance.author_marker",
                path="README.md",
                line=9,
                message="pattern matched",
            ),
        ],
        scan=ScanResults(files_scanned=8),
        gallery=GalleryResults(items=[GalleryItem(status="ok", path="gallery/example.png", message="present")]),
        render={"status": "skipped", "message": "disabled"},
        config_path="mfigci.yml",
        tool_version="0.1.0",
    )

    comment = build_pr_comment_report(results)

    assert comment.startswith("### matlab-figure-ci check")
    assert "# matlab-figure-ci report" not in comment
    assert "| error | privacy.email | src/example.m:3 | <redacted> |" in comment
    assert secret not in comment
    assert len(comment) < 1500


def test_json_report_has_stable_fields_and_redacted_findings():
    secret = "person@example.com"
    results = CheckResults(
        summary={"errors": 1, "warnings": 0, "files_scanned": 1, "gallery_checks": 0},
        findings=[
            Finding(
                severity="error",
                rule_id="privacy.email",
                path="src/example.m",
                line=1,
                message="<redacted>",
            )
        ],
        scan=ScanResults(files_scanned=1),
        gallery=GalleryResults(items=[]),
        render={"status": "skipped", "message": "disabled"},
        config_path="mfigci.yml",
        tool_version="0.1.0",
    )

    payload = json.loads(build_json_report(results))

    assert payload["schema_version"] == "mfigci.report.v1"
    assert payload["summary"]["errors"] == 1
    assert payload["findings"][0]["message"] == "<redacted>"
    assert secret not in json.dumps(payload)
