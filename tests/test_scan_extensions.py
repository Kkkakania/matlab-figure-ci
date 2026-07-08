from matlab_figure_ci.config import load_config
from matlab_figure_ci.scanners import run_scan


def test_extension_scan_errors_for_risky_matlab_office_origin_and_binary_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    for name in [
        "plot.fig",
        "data.mat",
        "locked.p",
        "paper.docx",
        "table.xlsx",
        "origin.opju",
        "project.opj",
        "sheet.ogwu",
        "helper.exe",
        "plugin.dll",
        "plugin.so",
        "plugin.dylib",
        "static.a",
        "object.o",
        "object.obj",
        "import.lib",
        "fast.mexmaci64",
    ]:
        (project / name).write_bytes(b"binary")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 17
    assert all(f.rule_id == "extension.error" for f in result.findings if f.severity == "error")


def test_pdf_is_warning_not_error_by_default(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "figure.pdf").write_bytes(b"%PDF-1.7")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 0
    assert result.warning_count == 1
    assert result.findings[0].rule_id == "extension.warning"


def test_extension_policy_matches_configured_extensions_case_insensitively(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "plot.fig").write_bytes(b"binary")
    (project / "figure.pdf").write_bytes(b"%PDF-1.7")
    config_path = project / "mfigci.yml"
    config_path.write_text(
        """
extensions:
  error:
    - .FIG
  warning:
    - .PDF
""".lstrip(),
        encoding="utf-8",
    )

    result = run_scan(project, load_config(config_path))

    assert {(finding.severity, finding.rule_id, finding.path) for finding in result.findings} == {
        ("error", "extension.error", "plot.fig"),
        ("warning", "extension.warning", "figure.pdf"),
    }


def test_origin_addons_and_matlab_toolboxes_warn_by_default(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    for name in [
        "origin-addon.opx",
        "toolbox.mltbx",
        "plan.mpp",
        "image.psd",
        "scene.c4d",
        "movie.mp4",
        "notebook.ipynb",
        "origin-script.ogs",
        "raw.bmp",
        "photo.jpg",
        "scan.tif",
        "loop.gif",
    ]:
        (project / name).write_bytes(b"binary")

    result = run_scan(project, load_config(project / "missing.yml"))

    warning_paths = {finding.path for finding in result.findings if finding.rule_id == "extension.warning"}
    assert result.error_count == 0
    assert result.warning_count == 12
    assert warning_paths == {
        "origin-addon.opx",
        "toolbox.mltbx",
        "plan.mpp",
        "image.psd",
        "scene.c4d",
        "movie.mp4",
        "notebook.ipynb",
        "origin-script.ogs",
        "raw.bmp",
        "photo.jpg",
        "scan.tif",
        "loop.gif",
    }


def test_matlab_figures_preset_allows_gallery_pdf_but_warns_elsewhere(tmp_path):
    project = tmp_path / "project"
    (project / "gallery").mkdir(parents=True)
    (project / "docs").mkdir()
    (project / "gallery" / "figure.pdf").write_bytes(b"%PDF-1.7")
    (project / "docs" / "notes.pdf").write_bytes(b"%PDF-1.7")
    config_path = project / "mfigci.yml"
    config_path.write_text("presets:\n  - matlab-figures\n", encoding="utf-8")

    result = run_scan(project, load_config(config_path))

    warning_paths = {finding.path for finding in result.findings if finding.rule_id == "extension.warning"}
    assert "gallery/figure.pdf" not in warning_paths
    assert "docs/notes.pdf" in warning_paths
    assert result.error_count == 0


def test_extension_allow_path_accepts_globs_for_nested_gallery_layouts(tmp_path):
    project = tmp_path / "project"
    (project / "gallery" / "paper-a").mkdir(parents=True)
    (project / "gallery" / "paper-b" / "nested").mkdir(parents=True)
    (project / "gallery" / "paper-a" / "figure.pdf").write_bytes(b"%PDF-1.7")
    (project / "gallery" / "paper-b" / "nested" / "figure.pdf").write_bytes(b"%PDF-1.7")
    (project / "drafts").mkdir()
    (project / "drafts" / "figure.pdf").write_bytes(b"%PDF-1.7")
    config_path = project / "mfigci.yml"
    config_path.write_text(
        """
extensions:
  allow:
    - path: gallery/**/*.pdf
      extensions:
        - .pdf
""".lstrip(),
        encoding="utf-8",
    )

    result = run_scan(project, load_config(config_path))

    warning_paths = {finding.path for finding in result.findings if finding.rule_id == "extension.warning"}
    assert "gallery/paper-a/figure.pdf" not in warning_paths
    assert "gallery/paper-b/nested/figure.pdf" not in warning_paths
    assert "drafts/figure.pdf" in warning_paths
    assert result.error_count == 0


def test_binary_files_are_skipped_for_text_scans_without_traceback(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "raw.mat").write_bytes(b"\x00\x01\x02\x03\xff\x00binary")

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.error_count == 1
    assert result.skipped_binary_count == 1


def test_symlink_to_external_file_does_not_escape_project_root(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    external = tmp_path / "external.txt"
    external.write_text("person@example.com\n", encoding="utf-8")
    (project / "linked.txt").symlink_to(external)

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.files_scanned == 0
    assert result.error_count == 0


def test_symlink_to_internal_file_is_scanned(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    target = project / "internal.txt"
    target.write_text("plain text\n", encoding="utf-8")
    (project / "linked.txt").symlink_to(target)

    result = run_scan(project, load_config(project / "missing.yml"))

    assert result.files_scanned == 2
    assert result.error_count == 0


def test_generated_assets_in_source_tree_are_warned(tmp_path):
    project = tmp_path / "project"
    (project / "templates" / "python").mkdir(parents=True)
    (project / "examples").mkdir()
    (project / "gallery").mkdir()
    (project / "templates" / "python" / "line_plot.png").write_bytes(b"fake png")
    (project / "examples" / "raw_preview.bmp").write_bytes(b"fake bmp")
    (project / "gallery" / "line_plot.png").write_bytes(b"fake png")
    (project / "gallery" / "raw_preview.bmp").write_bytes(b"fake bmp")

    result = run_scan(project, load_config(project / "missing.yml"))

    generated_paths = {finding.path for finding in result.findings if finding.rule_id == "generated_asset.source_tree"}
    assert generated_paths == {"examples/raw_preview.bmp", "templates/python/line_plot.png"}
    assert result.error_count == 0


def test_generated_assets_can_be_allowed(tmp_path):
    project = tmp_path / "project"
    (project / "templates" / "python").mkdir(parents=True)
    (project / "templates" / "python" / "line_plot.png").write_bytes(b"fake png")
    config_path = project / "mfigci.yml"
    config_path.write_text(
        "generated_assets:\n"
        "  allow:\n"
        "    - templates/python\n",
        encoding="utf-8",
    )

    result = run_scan(project, load_config(config_path))

    assert all(finding.rule_id != "generated_asset.source_tree" for finding in result.findings)
