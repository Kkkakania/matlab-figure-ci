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
                "pattern": (
                    r"((?i:/users/)[^\s'\"<>]+"
                    r"|(?i:/home/)[^\s'\"<>]+"
                    r"|(?i:/mnt/[a-z]/)[^\s'\"<>]+"
                    r"|(?i:[a-z]:\\users\\)[^\s'\"<>]+"
                    r"|(?i:%USERPROFILE%[\\/])[^\s'\"<>]+"
                    r"|/workspaces/[^\s'\"<>]+"
                    r"|/Volumes/[^\s'\"<>]+)"
                ),
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
                "id": "provenance.platform_trace.cn",
                "pattern": r"(CSDN|bilibili|知乎|小红书|公众号)",
                "severity": "warning",
            },
            {
                "id": "provenance.platform_trace.intl",
                "pattern": (
                    r"(medium\.com|Substack|Reddit|Stack Overflow|StackExchange|"
                    r"GitHub Gist|gist\.github\.com|Kaggle|MathWorks File Exchange)"
                ),
                "severity": "warning",
            },
        ],
    },
    "extensions": {
        "error": [
            ".p",
            ".mat",
            ".fig",
            ".doc",
            ".docx",
            ".xlsx",
            ".vsd",
            ".opju",
            ".opj",
            ".ogwu",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".a",
            ".o",
            ".obj",
            ".lib",
            ".mexmaci",
            ".mexmaci64",
            ".mexglx",
            ".mexa64",
            ".mexsol",
            ".mexlx",
            ".mexhp7",
            ".mex4",
        ],
        "warning": [
            ".pdf",
            ".mlx",
            ".zip",
            ".opx",
            ".mltbx",
            ".mpp",
            ".psd",
            ".c4d",
            ".mp4",
            ".ipynb",
            ".pyc",
            ".rds",
            ".cas",
            ".msh",
            ".db",
            ".ogs",
            ".bmp",
            ".jpg",
            ".jpeg",
            ".tif",
            ".tiff",
            ".gif",
        ],
        "allow": [],
    },
    "generated_assets": {
        "enabled": True,
        "severity": "warning",
        "source_dirs": ["src", "examples", "templates", "skills", "scripts"],
        "extensions": [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif", ".svg", ".pdf"],
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


def _is_preset_path(name: str) -> bool:
    return (
        name.startswith("./")
        or name.startswith("../")
        or name.startswith("/")
        or name.endswith(".yml")
        or name.endswith(".yaml")
    )


def _read_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise ConfigError(f"Preset file not found: {label}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse preset {label}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ConfigError(f"Preset must be a mapping: {label}")
    return loaded


def _load_user_preset(name: str, base_dir: Path) -> dict[str, Any]:
    preset_path = Path(name)
    if not preset_path.is_absolute():
        preset_path = base_dir / preset_path
    loaded = _read_yaml_mapping(preset_path, name)
    if "presets" in loaded or "preset" in loaded:
        raise ConfigError(f"User preset {name} must not include presets")

    try:
        _validate_config(deep_merge(DEFAULT_CONFIG, loaded))
    except ConfigError as exc:
        raise ConfigError(f"Invalid user preset {name}: {exc}") from exc
    return loaded


def _apply_presets(config: dict[str, Any], names: list[str], base_dir: Path | None = None) -> dict[str, Any]:
    result = deepcopy(config)
    preset_base_dir = base_dir or Path.cwd()
    for name in names:
        if name in PRESETS:
            result = deep_merge(result, PRESETS[name])
        elif _is_preset_path(name):
            result = deep_merge(result, _load_user_preset(name, preset_base_dir))
        else:
            available = ", ".join(sorted(PRESETS))
            raise ConfigError(f"Unknown preset '{name}'. Available presets: {available}")
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


def _validate_string_list(values: Any, key: str, label: str) -> None:
    if not isinstance(values, list):
        raise ConfigError(f"{key} must be a list of {label}")
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise ConfigError(f"{key}[{index}] must be a non-empty {label}")


def _validate_scan(config: dict[str, Any]) -> None:
    scan = _require_mapping(config.get("scan", {}), "scan")
    _validate_string_list(scan.get("include", []), "scan.include", "path string")
    _validate_string_list(scan.get("exclude", []), "scan.exclude", "path or glob string")


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
    _validate_string_list(expected, "gallery.expected", "path string")


def _validate_matlab(config: dict[str, Any]) -> None:
    matlab = _require_mapping(config.get("matlab", {}), "matlab")
    _require_bool(matlab.get("enabled", False), "matlab.enabled")
    for key in ("bin_env", "fallback_bin", "batch_command"):
        value = matlab.get(key, "")
        if not isinstance(value, str) or not value:
            raise ConfigError(f"matlab.{key} must be a non-empty string")
        if any(character.isspace() and character not in {" "} for character in value):
            raise ConfigError(f"matlab.{key} must not contain control characters")


def _validate_generated_assets(config: dict[str, Any]) -> None:
    generated_assets = _require_mapping(config.get("generated_assets", {}), "generated_assets")
    _require_bool(generated_assets.get("enabled", True), "generated_assets.enabled")
    severity = generated_assets.get("severity", "warning")
    if severity not in ALLOWED_SEVERITIES:
        allowed = ", ".join(sorted(ALLOWED_SEVERITIES))
        raise ConfigError(f"generated_assets.severity must be one of: {allowed}")
    source_dirs = generated_assets.get("source_dirs", [])
    if not isinstance(source_dirs, list) or not all(isinstance(item, str) for item in source_dirs):
        raise ConfigError("generated_assets.source_dirs must be a list of paths")
    _validate_extension_list(generated_assets.get("extensions", []), "generated_assets.extensions")
    allow = generated_assets.get("allow", [])
    if not isinstance(allow, list) or not all(isinstance(item, str) for item in allow):
        raise ConfigError("generated_assets.allow must be a list of paths")


def _validate_config(config: dict[str, Any]) -> None:
    _validate_scan(config)
    _validate_policy_rules(config, "privacy")
    _validate_policy_rules(config, "provenance")
    _validate_extensions(config)
    _validate_gallery(config)
    _validate_matlab(config)
    _validate_generated_assets(config)

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

    config = deep_merge(_apply_presets(DEFAULT_CONFIG, _preset_names(loaded), config_path.parent), loaded)
    _validate_config(config)
    return config
