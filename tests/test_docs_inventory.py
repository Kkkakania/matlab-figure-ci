from pathlib import Path

from matlab_figure_ci import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_adoption_playbook_is_discoverable_from_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/adoption-playbook.md" in readme


def test_adoption_playbook_keeps_staged_rollout_guidance():
    text = (ROOT / "docs" / "adoption-playbook.md").read_text(encoding="utf-8")

    assert "Stage 1: Static Scan" in text
    assert "Stage 2: Gallery Manifest" in text
    assert "Stage 3: Release Gate" in text
    assert "Stage 4: Optional MATLAB Render" in text
    assert "MATLAB is not required" in text
    assert "guaranteed program eligibility" in text


def test_public_version_references_match_package_version():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    version_plan = (ROOT / "docs" / "version-plan.md").read_text(encoding="utf-8")
    release_cadence = (ROOT / "docs" / "release-cadence.md").read_text(encoding="utf-8")
    tag = f"v{__version__}"

    assert f"matlab-figure-ci.git@{tag}" in readme
    assert f"## {tag} -" in changelog
    assert f"Current public release: `{tag}`" in version_plan
    assert f"Keep `{tag}` as the current public release" in release_cadence


def test_docs_index_lists_all_documentation_files():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    doc_files = sorted(path.name for path in (ROOT / "docs").glob("*.md") if path.name != "README.md")

    assert doc_files
    for doc_file in doc_files:
        assert f"({doc_file})" in docs_index


def test_ci_runs_markdown_link_check():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert (ROOT / "scripts" / "check_markdown_links.py").exists()
    assert "python scripts/check_markdown_links.py" in workflow
