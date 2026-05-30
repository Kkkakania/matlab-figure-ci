"""Configuration loading for mfigci."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


class ConfigError(Exception):
    """Raised when mfigci configuration cannot be loaded."""


DEFAULT_CONFIG: dict[str, Any] = {
    "project": {"name": "matlab-figure-ci-project"},
    "scan": {
        "include": ["."],
        "exclude": [".git", ".venv", "venv", "__pycache__", "pycache", "dist", "build", ".pytest_cache"],
    },
    "privacy": {
        "enabled": True,
        "redact_matches": True,
        "rules": [
            {
                "id": "privacy.email",
                "pattern": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                "severity": "error",
            },
            {
                "id": "privacy.local_absolute_path",
                "pattern": r"(/Users/[^\s'\"]+|C:\\Users\\[^\s'\"]+|/home/[^\s'\"]+)",
                "severity": "error",
            },
            {
                "id": "privacy.sensitive_keywords",
                "pattern": r"(身份证|银行卡|手机号|家庭住址|微信号)",
                "severity": "error",
            },
        ],
    },
    "provenance": {
        "enabled": True,
        "rules": [
            {
                "id": "provenance.author_marker",
                "pattern": r"(Author:|Created by|Copyright)",
                "severity": "warning",
            },
            {
                "id": "provenance.third_party_license",
                "pattern": r"(GPL|GNU General Public License|CC-BY|转载|原作者)",
                "severity": "warning",
            },
            {
                "id": "provenance.platform_trace",
                "pattern": r"(CSDN|bilibili|知乎|小红书|公众号)",
                "severity": "warning",
            },
        ],
    },
    "extensions": {
        "error": [".p", ".mat", ".fig", ".doc", ".docx", ".xlsx", ".vsd"],
        "warning": [".pdf", ".mlx", ".zip"],
        "allow": [],
    },
    "gallery": {
        "path": "gallery",
        "allowed_extensions": [".png", ".svg", ".pdf"],
        "min_size_bytes": 1024,
        "expected": [],
    },
    "matlab": {
        "enabled": False,
        "bin_env": "MATLAB_BIN",
        "fallback_bin": "matlab",
        "batch_command": "run_all_figures",
    },
}


PRESETS: dict[str, dict[str, Any]] = {
    "matlab-figures": {
        "gallery": {
            "allowed_extensions": [".png", ".svg", ".pdf"],
            "min_size_bytes": 1024,
        },
        "extensions": {
            "allow": [
                {
                    "path": "gallery",
                    "extensions": [".pdf"],
                }
            ],
        },
    }
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _preset_names(loaded: dict[str, Any]) -> list[str]:
    configured = loaded.get("presets", loaded.get("preset", []))
    if isinstance(configured, str):
        return [configured]
    if isinstance(configured, list) and all(isinstance(item, str) for item in configured):
        return list(configured)
    if configured:
        raise ConfigError("presets must be a string or list of strings")
    return []


def _apply_presets(config: dict[str, Any], names: list[str]) -> dict[str, Any]:
    result = deepcopy(config)
    for name in names:
        if name not in PRESETS:
            available = ", ".join(sorted(PRESETS))
            raise ConfigError(f"Unknown preset '{name}'. Available presets: {available}")
        result = deep_merge(result, PRESETS[name])
    return result


def load_config(path: str | Path = "mfigci.yml") -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return deepcopy(DEFAULT_CONFIG)

    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse {config_path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ConfigError(f"Configuration must be a mapping: {config_path}")

    config = _apply_presets(DEFAULT_CONFIG, _preset_names(loaded))
    return deep_merge(config, loaded)
