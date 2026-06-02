"""Configuration loading for mfigci."""

from __future__ import annotations

import re
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
        "exclude": [
            ".git",
            ".venv",
            ".venv*",
            "venv",
            "__pycache__",
            "pycache",
            "dist",
            "build",
            ".pytest_cache",
            ".ipynb_checkpoints",
        ],
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
    "strict": {
        "fail_on_warnings": False,
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

ALLOWED_SEVERITIES = {"error", "warning"}


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


def _require_mapping(value: Any, key: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a mapping")
    return value


def _require_bool(value: Any, key: str) -> None:
    if not isinstance(value, bool):
        raise ConfigError(f"{key} must be true or false")


def _validate_extension_list(values: Any, key: str) -> None:
    if not isinstance(values, list):
        raise ConfigError(f"{key} must be a list of extensions")
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.startswith("."):
            raise ConfigError(f"{key}[{index}] must be an extension string such as .png")


def _validate_policy_rules(config: dict[str, Any], section_name: str) -> None:
    section = _require_mapping(config.get(section_name, {}), section_name)
    _require_bool(section.get("enabled", True), f"{section_name}.enabled")
    if section_name == "privacy":
        _require_bool(section.get("redact_matches", True), "privacy.redact_matches")

    rules = section.get("rules", [])
    if not isinstance(rules, list):
        raise ConfigError(f"{section_name}.rules must be a list")
    for index, rule in enumerate(rules):
        rule_key = f"{section_name}.rules[{index}]"
        if not isinstance(rule, dict):
            raise ConfigError(f"{rule_key} must be a mapping")
        if not isinstance(rule.get("id", ""), str):
            raise ConfigError(f"{rule_key}.id must be a string")
        if not isinstance(rule.get("pattern", ""), str):
            raise ConfigError(f"{rule_key}.pattern must be a string")
        try:
            re.compile(rule.get("pattern", ""))
        except re.error as exc:
            raise ConfigError(f"{rule_key}.pattern is not a valid regular expression: {exc}") from exc
        severity = rule.get("severity", "warning")
        if severity not in ALLOWED_SEVERITIES:
            allowed = ", ".join(sorted(ALLOWED_SEVERITIES))
            raise ConfigError(f"{rule_key}.severity must be one of: {allowed}")


def _validate_extensions(config: dict[str, Any]) -> None:
    extensions = _require_mapping(config.get("extensions", {}), "extensions")
    _validate_extension_list(extensions.get("error", []), "extensions.error")
    _validate_extension_list(extensions.get("warning", []), "extensions.warning")

    allow = extensions.get("allow", [])
    if not isinstance(allow, list):
        raise ConfigError("extensions.allow must be a list")
    for index, rule in enumerate(allow):
        rule_key = f"extensions.allow[{index}]"
        if not isinstance(rule, dict):
            raise ConfigError(f"{rule_key} must be a mapping")
        if not isinstance(rule.get("path", ""), str):
            raise ConfigError(f"{rule_key}.path must be a string")
        _validate_extension_list(rule.get("extensions", []), f"{rule_key}.extensions")


def _validate_gallery(config: dict[str, Any]) -> None:
    gallery = _require_mapping(config.get("gallery", {}), "gallery")
    if not isinstance(gallery.get("path", "gallery"), str):
        raise ConfigError("gallery.path must be a string")
    _validate_extension_list(gallery.get("allowed_extensions", []), "gallery.allowed_extensions")
    min_size = gallery.get("min_size_bytes", 1024)
    if not isinstance(min_size, int) or min_size < 0:
        raise ConfigError("gallery.min_size_bytes must be a non-negative integer")
    expected = gallery.get("expected", [])
    if not isinstance(expected, list):
        raise ConfigError("gallery.expected must be a list of paths")
    for index, value in enumerate(expected):
        if not isinstance(value, str) or not value:
            raise ConfigError(f"gallery.expected[{index}] must be a non-empty path string")


def _validate_config(config: dict[str, Any]) -> None:
    _validate_policy_rules(config, "privacy")
    _validate_policy_rules(config, "provenance")
    _validate_extensions(config)
    _validate_gallery(config)

    strict = _require_mapping(config.get("strict", {}), "strict")
    _require_bool(strict.get("fail_on_warnings", False), "strict.fail_on_warnings")


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

    config = deep_merge(_apply_presets(DEFAULT_CONFIG, _preset_names(loaded)), loaded)
    _validate_config(config)
    return config
