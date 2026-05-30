"""Command line interface for mfigci."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .config import ConfigError, load_config
from .gallery import run_gallery_check
from .matlab import run_matlab_render
from .report import load_results, save_json_report, save_markdown, save_results
from .result import CheckResults, Finding
from .scanners import run_scan


EXAMPLE_CONFIG = """project:
  name: matlab-scientific-figures

scan:
  include:
    - "."
  exclude:
    - ".git"
    - ".venv"
    - "venv"
    - "__pycache__"
    - "pycache"
    - "dist"
    - "build"
    - ".pytest_cache"

privacy:
  enabled: true
  redact_matches: true

provenance:
  enabled: true

extensions:
  error:
    - ".p"
    - ".mat"
    - ".fig"
    - ".doc"
    - ".docx"
    - ".xlsx"
    - ".vsd"
  warning:
    - ".pdf"
    - ".mlx"
    - ".zip"

gallery:
  path: "gallery"
  allowed_extensions:
    - ".png"
    - ".svg"
    - ".pdf"
  min_size_bytes: 1024
  expected:
    - "example.png"

matlab:
  enabled: false
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "run_all_figures"
"""


WORKFLOW = """name: figure-quality

on:
  push:
  pull_request:

jobs:
  mfigci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install matlab-figure-ci
        run: |
          python -m pip install --upgrade pip
          pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v0.1.0

      - name: Run mfigci checks
        run: |
          mfigci check --config mfigci.yml --report mfigci-report.md

      - name: Upload mfigci report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: mfigci-report
          path: mfigci-report.md
"""


def _print_scan(result) -> None:
    for finding in result.findings:
        line = "" if finding.line is None else f":L{finding.line}"
        print(f"{finding.severity.upper()} {finding.rule_id} {finding.path}{line} {finding.message}")
    print(
        f"{result.error_count} error(s), {result.warning_count} warning(s), "
        f"{result.files_scanned} file(s) scanned, {result.skipped_binary_count} binary/skipped."
    )


def _print_gallery(result) -> None:
    for item in result.items:
        print(f"{item.status.upper()} {item.path} {item.message}")
    print(f"{result.error_count} error(s), {result.warning_count} warning(s), {result.checked_count} gallery file(s) ok.")


def _build_check_results(config_path: Path, config: dict, root: Path, include_render: bool) -> CheckResults:
    scan = run_scan(root, config)
    gallery = run_gallery_check(root, config)
    render = {"status": "skipped", "message": "disabled", "exit_code": 0}
    if include_render:
        render = run_matlab_render(root, config)

    findings = list(scan.findings)
    for item in gallery.items:
        if item.status in {"error", "warning"}:
            findings.append(Finding("error" if item.status == "error" else "warning", f"gallery.{item.status}", item.path, None, item.message))

    errors = scan.error_count + gallery.error_count + (1 if render.get("status") == "error" else 0)
    warnings = scan.warning_count + gallery.warning_count
    summary = {
        "errors": errors,
        "warnings": warnings,
        "files_scanned": scan.files_scanned,
        "gallery_checks": len(gallery.items),
        "skipped_binary": scan.skipped_binary_count,
    }
    return CheckResults(
        summary=summary,
        findings=findings,
        scan=scan,
        gallery=gallery,
        render=render,
        config_path=config_path.as_posix(),
        tool_version=__version__,
    )


def command_scan(args) -> int:
    config = load_config(args.config)
    result = run_scan(Path.cwd(), config)
    _print_scan(result)
    return result.exit_code


def command_gallery(args) -> int:
    config = load_config(args.config)
    result = run_gallery_check(Path.cwd(), config)
    _print_gallery(result)
    return result.exit_code


def command_render(args) -> int:
    config = load_config(args.config)
    result = run_matlab_render(Path.cwd(), config)
    print(f"{result['status'].upper()} {result['message']}")
    return int(result.get("exit_code", 0))


def command_check(args) -> int:
    config_path = Path(args.config)
    config = load_config(config_path)
    include_render = bool(config.get("matlab", {}).get("enabled", False))
    results = _build_check_results(config_path, config, Path.cwd(), include_render)
    save_results(results, args.results)
    save_markdown(results, args.report)
    _print_scan(results.scan)
    _print_gallery(results.gallery)
    print(f"Report written to {args.report}")
    print(f"Results written to {args.results}")
    if results.render.get("status") == "error":
        print(f"ERROR render {results.render.get('message')}")
        return 3
    return 1 if results.summary.get("errors", 0) else 0


def command_report(args) -> int:
    try:
        results = load_results(args.input)
    except FileNotFoundError as exc:
        print(str(exc))
        return 2
    if args.format == "json":
        save_json_report(results, args.output)
    else:
        save_markdown(results, args.output, style=args.style)
    print(f"Report written to {args.output}")
    return 0


def _write_if_allowed(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return f"skipped {path.as_posix()} (already exists)"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote {path.as_posix()}"


def command_init(args) -> int:
    messages = [
        _write_if_allowed(Path("mfigci.yml"), EXAMPLE_CONFIG, args.force),
        _write_if_allowed(Path(".github/workflows/figure-quality.yml"), WORKFLOW, args.force),
    ]
    for message in messages:
        print(message)
    print("Tip: add mfigci-report.md and .mfigci-results.json to .gitignore.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mfigci", description="CI checks for MATLAB scientific figure repositories.")
    parser.add_argument("--version", action="version", version=f"mfigci {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="scan privacy, provenance, and risky file extensions")
    scan.add_argument("--config", default="mfigci.yml")
    scan.set_defaults(func=command_scan)

    gallery = subparsers.add_parser("gallery", help="check expected gallery outputs")
    gallery.add_argument("--config", default="mfigci.yml")
    gallery.set_defaults(func=command_gallery)

    render = subparsers.add_parser("render", help="run optional MATLAB batch rendering")
    render.add_argument("--config", default="mfigci.yml")
    render.set_defaults(func=command_render)

    check = subparsers.add_parser("check", help="run scan, gallery, optional render, and write reports")
    check.add_argument("--config", default="mfigci.yml")
    check.add_argument("--report", default="mfigci-report.md")
    check.add_argument("--results", default=".mfigci-results.json")
    check.set_defaults(func=command_check)

    report = subparsers.add_parser("report", help="build markdown or JSON from .mfigci-results.json")
    report.add_argument("--input", default=".mfigci-results.json")
    report.add_argument("--output", default="mfigci-report.md")
    report.add_argument("--format", choices=["markdown", "json"], default="markdown")
    report.add_argument("--style", choices=["full", "pr-comment"], default="full")
    report.set_defaults(func=command_report)

    init = subparsers.add_parser("init", help="write example config and GitHub Actions workflow")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=command_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
