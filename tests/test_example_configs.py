from pathlib import Path

from matlab_figure_ci.config import load_config


def test_example_configs_parse_with_public_loader():
    root = Path(__file__).resolve().parents[1]
    config_paths = sorted((root / "examples" / "configs").glob("*.yml"))

    assert config_paths
    for config_path in config_paths:
        config = load_config(config_path)
        assert config["matlab"]["enabled"] is False
        assert isinstance(config["gallery"]["expected"], list)
        assert "LICENSE" in config["scan"]["exclude"]


def test_strict_release_gate_sample_enables_warning_failures():
    root = Path(__file__).resolve().parents[1]
    config = load_config(root / "examples" / "configs" / "strict-release-gate.yml")

    assert config["strict"]["fail_on_warnings"] is True
