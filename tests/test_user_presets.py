import pytest

from matlab_figure_ci.config import ConfigError, load_config


def test_loads_user_preset_relative_to_config_file(tmp_path):
    (tmp_path / "presets").mkdir()
    (tmp_path / "presets" / "lab.yml").write_text(
        """
gallery:
  allowed_extensions:
    - ".png"
    - ".svg"
  min_size_bytes: 4096
strict:
  fail_on_warnings: true
extensions:
  error:
    - ".docx"
    - ".xlsx"
  warning:
    - ".pdf"
""",
        encoding="utf-8",
    )
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text(
        """
presets:
  - matlab-figures
  - ./presets/lab.yml
project:
  name: lab-figures
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config["project"]["name"] == "lab-figures"
    assert config["gallery"]["allowed_extensions"] == [".png", ".svg"]
    assert config["gallery"]["min_size_bytes"] == 4096
    assert config["strict"]["fail_on_warnings"] is True
    assert config["extensions"]["error"] == [".docx", ".xlsx"]
    assert config["extensions"]["warning"] == [".pdf"]


def test_user_preset_cannot_include_nested_presets(tmp_path):
    (tmp_path / "lab.yml").write_text(
        """
presets:
  - matlab-figures
gallery:
  min_size_bytes: 4096
""",
        encoding="utf-8",
    )
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text("presets:\n  - ./lab.yml\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="must not include presets"):
        load_config(config_path)


def test_user_preset_validation_mentions_preset_path(tmp_path):
    (tmp_path / "bad.yml").write_text(
        """
privacy:
  rules:
    - id: privacy.custom
      pattern: "[unterminated"
      severity: error
""",
        encoding="utf-8",
    )
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text("presets:\n  - ./bad.yml\n", encoding="utf-8")

    with pytest.raises(ConfigError, match=r"./bad.yml"):
        load_config(config_path)
