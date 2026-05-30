import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_markdown_links.py"


spec = importlib.util.spec_from_file_location("check_markdown_links", SCRIPT)
assert spec is not None
check_markdown_links = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(check_markdown_links)


def test_markdown_link_checker_reports_missing_local_link(tmp_path):
    doc = tmp_path / "docs" / "guide.md"
    doc.parent.mkdir()
    doc.write_text("[Missing](missing.md)\n", encoding="utf-8")

    errors = check_markdown_links.check_file(doc, root=tmp_path)

    assert len(errors) == 1
    assert "missing link target" in errors[0]
    assert "missing.md" in errors[0]


def test_markdown_link_checker_accepts_existing_local_link(tmp_path):
    doc = tmp_path / "docs" / "guide.md"
    target = tmp_path / "docs" / "target.md"
    doc.parent.mkdir()
    target.write_text("# Target\n", encoding="utf-8")
    doc.write_text("[Target](target.md)\n", encoding="utf-8")

    assert check_markdown_links.check_file(doc, root=tmp_path) == []
