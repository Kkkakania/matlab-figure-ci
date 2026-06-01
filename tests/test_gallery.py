from matlab_figure_ci.config import load_config
from matlab_figure_ci.gallery import run_gallery_check


def write_config(project, expected, min_size=8, allowed=None):
    allowed = allowed or [".png", ".svg", ".pdf"]
    config_path = project / "mfigci.yml"
    config_path.write_text(
        f"""
gallery:
  path: gallery
  allowed_extensions:
{chr(10).join(f"    - {ext}" for ext in allowed)}
  min_size_bytes: {min_size}
  expected:
{chr(10).join(f"    - {name}" for name in expected)}
""",
        encoding="utf-8",
    )
    return load_config(config_path)


def test_gallery_ok_returns_zero(tmp_path):
    gallery = tmp_path / "gallery"
    gallery.mkdir()
    (gallery / "example.png").write_bytes(b"123456789")

    result = run_gallery_check(tmp_path, write_config(tmp_path, ["example.png"]))

    assert result.error_count == 0
    assert result.checked_count == 1
    assert result.exit_code == 0


def test_gallery_reports_missing_file(tmp_path):
    (tmp_path / "gallery").mkdir()

    result = run_gallery_check(tmp_path, write_config(tmp_path, ["missing.png"]))

    assert result.error_count == 1
    assert result.items[0].status == "error"
    assert "missing" in result.items[0].message


def test_gallery_reports_empty_file(tmp_path):
    gallery = tmp_path / "gallery"
    gallery.mkdir()
    (gallery / "empty.svg").write_bytes(b"")

    result = run_gallery_check(tmp_path, write_config(tmp_path, ["empty.svg"]))

    assert result.error_count == 1
    assert "empty" in result.items[0].message


def test_gallery_reports_unexpected_extension(tmp_path):
    gallery = tmp_path / "gallery"
    gallery.mkdir()
    (gallery / "temp.bmp").write_bytes(b"123456789")

    result = run_gallery_check(tmp_path, write_config(tmp_path, ["temp.bmp"], allowed=[".png"]))

    assert result.error_count == 0
    assert result.warning_count == 1
    assert result.items[0].status == "warning"


def test_gallery_rejects_expected_paths_outside_gallery(tmp_path):
    gallery = tmp_path / "gallery"
    gallery.mkdir()
    (tmp_path / "outside.png").write_bytes(b"123456789")

    result = run_gallery_check(tmp_path, write_config(tmp_path, ["../outside.png"]))

    assert result.error_count == 1
    assert result.items[0].status == "error"
    assert "outside the gallery directory" in result.items[0].message
