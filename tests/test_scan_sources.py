from matlab_figure_ci.config import load_config
from matlab_figure_ci.scanners import run_scan


def test_provenance_scan_flags_source_markers_as_warning(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "script.m").write_text(
        "Author: Somebody\nCopyright 2020\nGPL\nCSDN\n知乎\n",
        encoding="utf-8",
    )

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 0
    assert result.warning_count >= 3
    assert result.exit_code == 0
    assert {f.rule_id for f in result.findings} >= {
        "provenance.author_marker",
        "provenance.third_party_license",
        "provenance.platform_trace.cn",
    }


def test_provenance_scan_flags_international_platform_traces_as_warning(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "script.m").write_text(
        "Adapted from a Stack Overflow answer and a MathWorks File Exchange snippet.\n",
        encoding="utf-8",
    )

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 0
    assert result.warning_count >= 1
    assert result.exit_code == 0
    assert {f.rule_id for f in result.findings} >= {
        "provenance.platform_trace.intl",
    }
