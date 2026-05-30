"""Markdown and JSON report helpers."""

from __future__ import annotations

import json
from pathlib import Path

from .result import CheckResults


def build_markdown_report(results: CheckResults) -> str:
    summary = results.summary
    lines = [
        "# matlab-figure-ci report",
        "",
        "## Summary",
        "",
        f"- Errors: {summary.get('errors', 0)}",
        f"- Warnings: {summary.get('warnings', 0)}",
        f"- Files scanned: {summary.get('files_scanned', 0)}",
        f"- Gallery checks: {summary.get('gallery_checks', 0)}",
        f"- MATLAB render: {results.render.get('status', 'skipped')}",
        "",
        "## Findings",
        "",
        "| Severity | Rule | File | Line | Message |",
        "|---|---|---|---|---|",
    ]
    if results.findings:
        for finding in results.findings:
            line = "" if finding.line is None else str(finding.line)
            lines.append(f"| {finding.severity} | {finding.rule_id} | {finding.path} | {line} | {finding.message} |")
    else:
        lines.append("| ok | none |  |  | No findings |")

    lines.extend(["", "## Gallery", ""])
    if results.gallery.items:
        for item in results.gallery.items:
            lines.append(f"- {item.status.upper()} {item.path}: {item.message}")
    else:
        lines.append("- No gallery entries checked.")

    lines.extend(["", "## Render", "", f"- {results.render.get('status', 'skipped')}: {results.render.get('message', 'disabled')}"])
    lines.extend(["", "## Next steps", ""])
    if summary.get("errors", 0):
        lines.append("- Fix error findings before releasing or merging.")
    elif summary.get("warnings", 0):
        lines.append("- Review warning findings and confirm they are intentional.")
    else:
        lines.append("- No blocking issues found.")
    lines.append("")
    return "\n".join(lines)


def save_results(results: CheckResults, path: str | Path) -> None:
    Path(path).write_text(json.dumps(results.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def load_results(path: str | Path) -> CheckResults:
    results_path = Path(path)
    if not results_path.exists():
        raise FileNotFoundError(
            f"{results_path} not found. Run `mfigci check --report mfigci-report.md` before `mfigci report`."
        )
    data = json.loads(results_path.read_text(encoding="utf-8"))
    return CheckResults.from_dict(data)


def save_markdown(results: CheckResults, path: str | Path) -> None:
    Path(path).write_text(build_markdown_report(results), encoding="utf-8")
