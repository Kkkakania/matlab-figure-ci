from pathlib import Path

import pytest

from matlab_figure_ci.config import ConfigError, load_config


def test_missing_config_uses_safe_defaults(tmp_path):
    config = load_config(tmp_path / "missing.yml")

    assert config["gallery"]["expected"] == []
    assert config["matlab"]["enabled"] is False
    assert config["strict"]["fail_on_warnings"] is False
    assert ".pdf" in config["extensions"]["warning"]
    assert ".pdf" not in config["extensions"]["error"]


def test_reads_mfigci_yml(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text(
        """
project:
  name: demo
gallery:
  path: figures
  expected:
    - first.png
matlab:
  enabled: true
  batch_command: run_all_figures
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config["project"]["name"] == "demo"
    assert config["gallery"]["path"] == "figures"
    assert config["gallery"]["expected"] == ["first.png"]
    assert config["matlab"]["enabled"] is True


def test_invalid_config_shape_raises_clear_error(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="mapping"):
        load_config(config_path)


def test_matlab_figures_preset_adds_gallery_pdf_allowance_without_breaking_defaults(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text(
        """
presets:
  - matlab-figures
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert ".pdf" in config["extensions"]["warning"]
    assert {"path": "gallery", "extensions": [".pdf"]} in config["extensions"]["allow"]
    assert ".pdf" in config["gallery"]["allowed_extensions"]
    assert config["matlab"]["enabled"] is False


def test_unknown_preset_raises_clear_error(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text("presets:\n  - not-a-preset\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Unknown preset"):
        load_config(config_path)


def test_invalid_policy_severity_raises_clear_error(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text(
        """
privacy:
  rules:
    - id: privacy.email
      pattern: email
      severity: critical
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match=r"privacy.rules\[0\].severity"):
        load_config(config_path)


def test_invalid_strict_flag_raises_clear_error(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text(
        """
strict:
  fail_on_warnings: sometimes
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="strict.fail_on_warnings"):
        load_config(config_path)


def test_invalid_extension_policy_raises_clear_error(tmp_path):
    config_path = tmp_path / "mfigci.yml"
    config_path.write_text(
        """
extensions:
  error:
    - fig
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match=r"extensions.error\[0\]"):
        load_config(config_path)
