from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_template(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_bug_report_template_asks_for_reproducible_context():
    text = read_template(".github/ISSUE_TEMPLATE/bug_report.md")

    assert "Reproduction" in text
    assert "Environment" in text
    assert "Configuration" in text
    assert "Output" in text
    assert "Redact private paths" in text


def test_feature_request_template_keeps_scope_small():
    text = read_template(".github/ISSUE_TEMPLATE/feature_request.md")

    assert "Problem" in text
    assert "Proposed behavior" in text
    assert "Scope" in text
    assert "Backward compatibility risk" in text


def test_pull_request_template_preserves_quality_gate_checklist():
    text = read_template(".github/pull_request_template.md")

    assert "pytest" in text
    assert "mfigci --help" in text
    assert "private datasets" in text
    assert "MATLAB rendering optional" in text
