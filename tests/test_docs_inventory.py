from pathlib import Path

from matlab_figure_ci import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_adoption_playbook_is_discoverable_from_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/adoption-playbook.md" in readme


def test_readme_links_to_chinese_version():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "[简体中文](README.zh-CN.md)" in readme
    assert "[English](README.md)" in chinese


def test_chinese_readme_covers_core_user_flow():
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "Dogfooding 状态" in chinese
    assert "版本和发布状态" in chinese
    assert "快速开始" in chinese
    assert "前 5 分钟" in chinese
    assert "配置" in chinese
    assert "GitHub Actions" in chinese
    assert "当前限制" in chinese
    assert "不是版权清洗工具" in chinese
    assert "核心 scan、gallery、report 和 check 不依赖 MATLAB" in chinese
    assert "mfigci scan --config mfigci.yml --paths" in chinese
    assert "mfigci report --style triage --output mfigci-triage.md" in chinese
    assert "mfigci release-preflight --require-dist" in chinese
    assert "docs/adoption-report-matlab-scientific-figures.md" in chinese
    assert "docs/v2-compatibility.md" in chinese
    assert "docs/pypi-release-checklist.zh-CN.md" in chinese


def test_chinese_pypi_checklist_preserves_publish_boundary():
    text = (ROOT / "docs" / "pypi-release-checklist.zh-CN.md").read_text(encoding="utf-8")
    index = (ROOT / "docs" / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "当前尚未发布到 PyPI" in text
    assert "GitHub release tag" in text
    assert "mfigci release-preflight --require-dist" in text
    assert "python scripts/check_pypi_name.py matlab-figure-ci --json-out pypi-name-check.json" in text
    assert "pypi-name-check.json" in text
    assert "不要为了关闭 issue 而发布 PyPI" in text
    assert "不要在 package workflow 里加入自动上传步骤" in text
    assert "pypi-release-checklist.zh-CN.md" in index


def test_adoption_playbook_keeps_staged_rollout_guidance():
    text = (ROOT / "docs" / "adoption-playbook.md").read_text(encoding="utf-8")

    assert "Stage 1: Static Scan" in text
    assert "Stage 2: Gallery Manifest" in text
    assert "Stage 3: Release Gate" in text
    assert "Stage 4: Optional MATLAB Render" in text
    assert "MATLAB is not required" in text
    assert "guaranteed program eligibility" in text


def test_adoption_playbook_documents_ecosystem_handoff_contract():
    text = (ROOT / "docs" / "adoption-playbook.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Ecosystem Handoff Contract" in text
    assert "Producer artifact" in text
    assert "Next consumer" in text
    assert "gallery/*.png and gallery/*.svg" in text
    assert "render_report.md and render_report.json" in text
    assert "mfigci-report.md and .mfigci-results.json" in text
    assert "matlab-plotting-skill now dogfoods `mfigci check`" in text
    assert "exported gallery artifacts before first-use reports" in text
    assert "Do not use `matlab-figure-ci` as a laundering step" in text
    assert "handoff contract" in readme


def test_dogfooding_adoption_report_is_current_and_bounded():
    text = (ROOT / "docs" / "adoption-report-matlab-scientific-figures.md").read_text(encoding="utf-8")

    assert "Snapshot date: 2026-07-01" in text
    assert "Latest checked downstream commit | `51472f9`" in text
    assert "Figure quality run `28495760136`" in text
    assert "Quality checks run `28495760059`" in text
    assert "successful and annotation-free" in text
    assert "zero annotations" in text
    assert "291 file(s) scanned" in text
    assert "31 binary/skipped" in text
    assert "62 gallery file(s) ok" in text
    assert "not a" in text
    assert "download metric" in text
    assert "external adoption claim" in text
    assert "program eligibility claim" in text
    assert "GitHub Project-board documentation" in text
    assert "visible" in text
    assert "fork intake helper" in text
    assert "ahead commits to review" in text
    assert "no-Projects-scope triage" in text
    assert "Chinese Project-board setup guide" in text
    assert "active browser account" in text
    assert "browser session can point to different GitHub users" in text
    assert "interim labels" in text
    assert "triage remains inspectable" in text
    assert "closed feedback hub issues" in text
    assert "public `v2.5.0` tag" in text
    assert "version guard" in text
    assert "Markdown report and `.mfigci-results.json` artifacts" in text
    assert "synthetic 5 MW PV example" in text
    assert "% of fundamental" in text
    assert "without expanding the domain pack" in text
    assert "green CI and annotation-free status" in text
    assert "exact run URLs" in text
    assert "repository maintenance hygiene" in text
    assert "198 file(s) scanned" not in text
    assert "27c3755" not in text
    assert "27295930398" not in text
    assert "271 file(s) scanned" not in text
    assert "545f6ed" not in text
    assert "27294668185" not in text
    assert "260 file(s) scanned" not in text
    assert "261 file(s) scanned" not in text
    assert "262 file(s) scanned" not in text
    assert "263 file(s) scanned" not in text
    assert "280 file(s) scanned" not in text
    assert "3894c6f" not in text
    assert "27894597253" not in text


def test_plotting_skill_adoption_report_is_current_and_bounded():
    report = ROOT / "docs" / "adoption-report-matlab-plotting-skill.md"
    text = report.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    chinese_index = (ROOT / "docs" / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "docs/adoption-report-matlab-plotting-skill.md" in readme
    assert "adoption-report-matlab-plotting-skill.md" in docs_index
    assert "adoption-report-matlab-plotting-skill.md" in chinese_index
    assert "Snapshot date: 2026-06-21" in text
    assert "Latest checked downstream commit | `a28131f`" in text
    assert "Quality workflow" in text
    assert "27894703366" in text
    assert "successful and annotation-free" in text
    assert "public `v2.5.0` tag" in text
    assert "104 file(s) scanned" in text
    assert "1 warning(s)" in text
    assert "13 binary/skipped" in text
    assert "13 gallery file(s) ok" in text
    assert "docs/application-evidence.md" in text
    assert "companion skill evidence for `matlab-scientific-figures`" in text
    assert "main Codex for Open Source application repository" in text
    assert "MATLAB render in public CI | Disabled" in text
    assert "Markdown report and `.mfigci-results.json` artifacts" in text
    assert "render reports are producer evidence, not source material" in text
    assert "download metric" in text
    assert "external adoption claim" in text
    assert "program eligibility claim" in text
    assert "not proof that MATLAB rendered on GitHub-hosted runners" in text
    assert "annotation status" in text
    assert "a23411a" not in text
    assert "27294667935" not in text
    assert "27295673294" not in text
    assert "f32bb61" not in text
    assert "1db56f7" not in text
    assert "27874276844" not in text
    assert "raw private data" not in text


def test_codex_workflow_documents_review_packet_boundaries():
    text = (ROOT / "docs" / "openai-codex-maintainer-workflow.md").read_text(encoding="utf-8")

    assert "## Review Packet For Maintainers" in text
    assert "## Application Evidence Packet" in text
    assert "workflow run URL" in text
    assert "mfigci-report.md and .mfigci-results.json" in text
    assert "release-preflight.json" in text
    assert "redacted issue or PR link" in text
    assert "not an approval argument" in text
    assert "mfigci release-preflight --require-dist --output release-preflight.json" in text
    assert "downstream `matlab-scientific-figures` dogfooding workflow" in text
    assert "never raw private paths or unredacted findings" in text
    assert "not proof of broad adoption" in text


def test_evidence_packet_template_is_documented():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    chinese_index = (ROOT / "docs" / "README.zh-CN.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    text = (ROOT / "docs" / "evidence-packet-template.md").read_text(encoding="utf-8")

    assert "evidence-packet-template.md" in docs_index
    assert "evidence-packet-template.md" in chinese_index
    assert "mfigci report --style evidence --output mfigci-evidence.md" in readme
    assert "Unreleased on main after v2.5.0" in readme
    assert "Evidence packet report style" in changelog.split("## v2.5.0", maxsplit=1)[0]
    assert "# Evidence Packet Template" in text
    assert "mfigci report --style evidence --output mfigci-evidence.md" in text
    assert "Do not commit `mfigci-evidence.md` by default" in text
    assert "Unreleased on main after v2.5.0" in text
    assert "workflow run URL" in text
    assert "redacted issue or PR link" in text
    assert "not an approval argument" in text


def test_submission_check_example_is_documented_and_bounded():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    chinese_index = (ROOT / "docs" / "README.zh-CN.md").read_text(encoding="utf-8")
    text = (ROOT / "examples" / "reports" / "submission-check-example.md").read_text(encoding="utf-8")
    template = (
        ROOT / "examples" / "reports" / "submission-check-template.zh-CN.md"
    ).read_text(encoding="utf-8")

    assert "examples/reports/submission-check-example.md" in readme
    assert "examples/reports/submission-check-example.md" in chinese
    assert "../examples/reports/submission-check-example.md" in docs_index
    assert "../examples/reports/submission-check-example.md" in chinese_index
    assert "examples/reports/submission-check-template.zh-CN.md" in readme
    assert "examples/reports/submission-check-template.zh-CN.md" in chinese
    assert "../examples/reports/submission-check-template.zh-CN.md" in docs_index
    assert "../examples/reports/submission-check-template.zh-CN.md" in chinese_index
    assert "# Submission Check Example Report" in text
    assert "synthetic paths" in text
    assert "Font size" in text
    assert "Line width" in text
    assert "Figure dimensions" in text
    assert "Export format" in text
    assert "Local/private paths" in text
    assert "Source boundary" in text
    assert "Release readiness" in text
    assert "does not verify scientific validity" in text
    assert "journal acceptance" in text
    assert "promising review outcomes" in text
    assert "# MATLAB 图件投稿前检查模板" in template
    assert "本模板只检查图件质量和发布卫生" in template
    assert "不替代导师、学校、期刊或会议要求" in template


def test_triage_report_template_is_documented():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    chinese_index = (ROOT / "docs" / "README.zh-CN.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    text = (ROOT / "docs" / "issue-triage-report.md").read_text(encoding="utf-8")

    assert "issue-triage-report.md" in docs_index
    assert "issue-triage-report.md" in chinese_index
    assert "mfigci report --style triage --output mfigci-triage.md" in readme
    assert "Issue triage report style" in changelog.split("## v2.5.0", maxsplit=1)[0]
    assert "# Issue Triage Report" in text
    assert "mfigci report --style triage --output mfigci-triage.md" in text
    assert "not a bot" in text
    assert "Suggested triage labels" in text
    assert "Do not commit `mfigci-triage.md` by default" in text
    assert "privacy findings stay redacted" in text


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


def test_rule_design_documents_scan_exclude_globs():
    text = (ROOT / "docs" / "rule-design.md").read_text(encoding="utf-8")

    assert "Scan Include And Exclude Rules" in text
    assert "simple shell-style globs" in text
    assert ".venv*" in text
    assert "Do not use broad excludes to hide raw source packs" in text


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
    assert "Do not commit `mfigci-report.md`, `.mfigci-results.json`," in readme
    assert "`mfigci-evidence.md`, `release-preflight.json`, or `pypi-name-check.json`" in readme
    assert "include-hidden-files: true" in readme
    assert "mfigci-report.md\n            .mfigci-results.json" in readme


def test_readme_lists_release_preflight_command():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "mfigci release-preflight" in readme
    assert "mfigci release-preflight --format json" in readme
    assert "mfigci release-preflight --output release-preflight.json" in readme
    checklist = (ROOT / "docs" / "pypi-release-checklist.md").read_text(encoding="utf-8")
    assert "mfigci release-preflight --check-pypi-name --output release-preflight.json" in checklist
    assert "mfigci release-preflight --require-dist" in readme
    assert "docs/release-artifacts.md" in readme
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in readme


def test_readmes_show_generated_asset_policy():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    example = (ROOT / "mfigci.example.yml").read_text(encoding="utf-8")

    for text in (readme, chinese, example):
        assert "generated_assets:" in text
        assert "source_dirs:" in text
        assert '- ".bmp"' in text
        assert '- ".tif"' in text
        assert '- ".gif"' in text
        assert "allow: []" in text


def test_release_artifacts_doc_explains_preflight_payload():
    text = (ROOT / "docs" / "release-artifacts.md").read_text(encoding="utf-8")

    assert "mfigci release-preflight --require-dist --output release-preflight.json" in text
    assert "projectName" in text
    assert "projectVersion" in text
    assert "summary.errors" in text
    assert "summary.checks" in text
    assert "summary.total" not in text
    assert "release-preflight" in text
    assert "does not publish to PyPI" in text
