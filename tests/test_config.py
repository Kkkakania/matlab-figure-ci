from pathlib import Path

import pytest

from matlab_figure_ci.config import ConfigError, load_config


def test_missing_config_uses_safe_defaults(tmp_path):
    config = load_config(tmp_path / "missing.yml")

    assert config["gallery"]["expected"] == []
    assert config["matlab"]["enabled"] is False
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
