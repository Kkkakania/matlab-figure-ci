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
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    version_plan = (ROOT / "docs" / "version-plan.md").read_text(encoding="utf-8")
    release_cadence = (ROOT / "docs" / "release-cadence.md").read_text(encoding="utf-8")
    tag = f"v{__version__}"

    assert f"matlab-figure-ci.git@{tag}" in readme
    assert f"Latest release: `{tag}`" in roadmap
    assert f"## {tag} -" in changelog
    assert f"Current public release: `{tag}`" in version_plan
    assert f"Keep `{tag}` as the current public release" in release_cadence


def test_roadmap_status_language_is_current():
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")

    assert "## Current State" in roadmap
    assert "## Completed Release Tracks" in roadmap
    assert "## Next Candidates" in roadmap
    assert "## Versioning Pace" in roadmap
    assert "PyPI is planned but not published yet" in roadmap
    assert "It should not become the normal release rhythm" in roadmap
    assert "Artificial usage, stars, downloads, or adoption claims" in roadmap
    assert "planned additions" not in roadmap.lower()
    assert "latest release: `v0." not in roadmap.lower()


def test_changelog_unreleased_section_is_release_ready():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased = changelog.split("## v", maxsplit=1)[0]

    assert "## Unreleased" in unreleased
    assert "Planned:" not in unreleased
    assert "TODO" not in unreleased


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
    assert (ROOT / "scripts" / "check_workflows.py").exists()
    assert "python scripts/check_workflows.py" in workflow


def test_contributing_documents_supported_test_commands():
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    pr_template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

    assert 'python -m pip install -e ".[test]"' in contributing
    assert "uv run --extra test pytest" in contributing
    assert "uv run --extra test pytest" in pr_template
    assert "v0.1.x" not in contributing


def test_docs_cover_externally_managed_python_installs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "externally managed Python" in readme
    assert "python3 -m venv .venv" in readme
    assert ". .venv/bin/activate" in readme
    assert "python3 -m venv .venv" in contributing
    assert 'python -m pip install -e ".[test]"' in contributing


def test_readme_explains_version_and_distribution_status():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    tag = f"v{__version__}"

    assert "## Version And Distribution Status" in readme
    assert f"The current public release is `{tag}`" in readme
    assert "GitHub release tag install" in readme
    assert "not published on PyPI yet" in readme
    assert "v2 compatibility boundary" in readme


def test_readme_has_first_five_minutes_adoption_path():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "## First 5 Minutes" in readme
    assert "1. Install from the current release tag." in readme
    assert "2. Create starter files in a throwaway branch or scratch repository." in readme
    assert "3. Inspect the generated policy before enforcing it." in readme
    assert "4. Run the full check and read both reports." in readme
    assert "mfigci init --gitignore" in readme
    assert "The plain `mfigci init` command does not edit `.gitignore`" in readme
    assert "Do not commit `mfigci-report.md`, `.mfigci-results.json`, or `release-preflight.json`" in readme


def test_readme_lists_release_preflight_command():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "mfigci release-preflight" in readme
    assert "mfigci release-preflight --format json" in readme
    assert "mfigci release-preflight --output release-preflight.json" in readme
    assert "mfigci release-preflight --require-dist" in readme
    assert "docs/release-artifacts.md" in readme
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in readme


def test_release_artifacts_doc_explains_preflight_payload():
    text = (ROOT / "docs" / "release-artifacts.md").read_text(encoding="utf-8")

    assert "mfigci release-preflight --require-dist --output release-preflight.json" in text
    assert "summary.errors" in text
    assert "release-preflight" in text
    assert "does not publish to PyPI" in text
