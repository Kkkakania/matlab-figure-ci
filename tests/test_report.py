import json

from matlab_figure_ci.report import (
    build_evidence_packet_report,
    build_json_report,
    build_markdown_report,
    build_pr_comment_report,
    build_triage_report,
    load_results,
)
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
    assert "## Finding Summary" in markdown
    assert "| error | privacy.email | 1 |" in markdown


def test_load_results_requires_existing_json(tmp_path):
    missing = tmp_path / ".mfigci-results.json"

    try:
        load_results(missing)
    except FileNotFoundError as exc:
        assert "mfigci check" in str(exc)
        assert "--results .mfigci-results.json" in str(exc)
        assert "--input .mfigci-results.json" in str(exc)
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
            Finding(
                severity="warning",
                rule_id="provenance.author_marker",
                path="docs/notes.md",
                line=2,
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
    assert "Finding summary:" in comment
    assert "| warning | provenance.author_marker | 2 |" in comment
    assert "| error | privacy.email | src/example.m:3 | <redacted> |" in comment
    assert secret not in comment
    assert len(comment) < 1500


def test_evidence_packet_report_is_copyable_and_bounded():
    secret = "person@example.com"
    results = CheckResults(
        summary={"errors": 0, "warnings": 2, "files_scanned": 12, "gallery_checks": 3},
        findings=[
            Finding(
                severity="warning",
                rule_id="provenance.author_marker",
                path="docs/notes.md",
                line=4,
                message="pattern matched",
            ),
            Finding(
                severity="warning",
                rule_id="generated_asset.source_tree",
                path="src/preview.png",
                line=None,
                message="generated asset in source tree",
            ),
        ],
        scan=ScanResults(files_scanned=12),
        gallery=GalleryResults(items=[GalleryItem(status="ok", path="gallery/example.png", message="present")]),
        render={"status": "skipped", "message": "disabled"},
        config_path="mfigci.yml",
        tool_version="2.5.0",
    )

    packet = build_evidence_packet_report(results)

    assert packet.startswith("### matlab-figure-ci evidence packet")
    assert "Review packet" in packet
    assert "Application packet" in packet
    assert "workflow run URL" in packet
    assert "redacted issue or PR link" in packet
    assert "mfigci-report.md" in packet
    assert ".mfigci-results.json" in packet
    assert "not an approval argument" in packet
    assert "| warning | provenance.author_marker | 1 |" in packet
    assert secret not in packet
    assert "person@example.com" not in packet


def test_triage_report_groups_errors_warnings_and_next_actions():
    secret = "person@example.com"
    results = CheckResults(
        summary={"errors": 2, "warnings": 2, "files_scanned": 16, "gallery_checks": 4},
        findings=[
            Finding(
                severity="error",
                rule_id="privacy.email",
                path="src/example.m",
                line=3,
                message="<redacted>",
            ),
            Finding(
                severity="error",
                rule_id="extensions.error",
                path="private/source.fig",
                line=None,
                message="forbidden extension",
            ),
            Finding(
                severity="warning",
                rule_id="provenance.author_marker",
                path="README.md",
                line=8,
                message="pattern matched",
            ),
            Finding(
                severity="warning",
                rule_id="generated_asset.source_tree",
                path="src/preview.png",
                line=None,
                message="generated asset in source tree",
            ),
        ],
        scan=ScanResults(files_scanned=16),
        gallery=GalleryResults(
            items=[
                GalleryItem(status="error", path="gallery/missing.png", message="missing"),
                GalleryItem(status="ok", path="gallery/example.png", message="present"),
            ]
        ),
        render={"status": "skipped", "message": "disabled"},
        config_path="mfigci.yml",
        tool_version="2.5.0",
    )

    note = build_triage_report(results)

    assert note.startswith("### matlab-figure-ci triage note")
    assert "Status: **blocked**" in note
    assert "`privacy`" in note
    assert "`provenance`" in note
    assert "`gallery`" in note
    assert "Blockers" in note
    assert "| error | privacy.email | src/example.m:3 | <redacted> |" in note
    assert "| error | extensions.error | private/source.fig | forbidden extension |" in note
    assert "Warnings to review" in note
    assert "| warning | generated_asset.source_tree | src/preview.png | generated asset in source tree |" in note
    assert "Next maintainer action" in note
    assert "Fix policy errors before merge or release" in note
    assert secret not in note


def test_triage_report_treats_render_error_as_blocking():
    results = CheckResults(
        summary={"errors": 0, "warnings": 0, "files_scanned": 3, "gallery_checks": 0},
        findings=[],
        scan=ScanResults(files_scanned=3),
        gallery=GalleryResults(items=[]),
        render={"status": "error", "message": "MATLAB executable not found"},
        config_path="mfigci.yml",
        tool_version="2.5.0",
    )

    note = build_triage_report(results)

    assert "Status: **blocked**" in note
    assert "`blocked`" in note
    assert "`render`" in note
    assert "| error | render | MATLAB | MATLAB executable not found |" in note
    assert "Fix policy errors before merge or release" in note


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


def test_reports_redact_absolute_config_paths():
    results = CheckResults(
        summary={"errors": 0, "warnings": 0, "files_scanned": 1, "gallery_checks": 0},
        findings=[],
        scan=ScanResults(files_scanned=1),
        gallery=GalleryResults(items=[]),
        render={"status": "skipped", "message": "disabled"},
        config_path="/Users/example/private-project/mfigci.yml",
        tool_version="0.1.0",
    )

    json_payload = json.loads(build_json_report(results))
    evidence = build_evidence_packet_report(results)
    triage = build_triage_report(results)

    assert json_payload["config_path"] == "mfigci.yml"
    assert "private-project" not in evidence
    assert "private-project" not in triage
    assert "- Config: `mfigci.yml`" in evidence
    assert "- Config: `mfigci.yml`" in triage


def test_markdown_reports_escape_table_cells():
    results = CheckResults(
        summary={"errors": 1, "warnings": 0, "files_scanned": 1, "gallery_checks": 0},
        findings=[
            Finding(
                severity="error",
                rule_id="privacy.custom|pipe",
                path="src/with|pipe.m",
                line=4,
                message="pattern | matched\nnext line",
            )
        ],
        scan=ScanResults(files_scanned=1),
        gallery=GalleryResults(items=[]),
        render={"status": "skipped", "message": "disabled"},
        config_path="mfigci.yml",
        tool_version="0.1.0",
    )

    full = build_markdown_report(results)
    comment = build_pr_comment_report(results)

    assert "privacy.custom\\|pipe" in full
    assert "src/with\\|pipe.m" in full
    assert "pattern \\| matched next line" in full
    assert "privacy.custom\\|pipe" in comment
    assert "src/with\\|pipe.m:4" in comment
