"""Markdown and JSON report helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .result import CheckResults


def _format_location(path: str, line: int | None) -> str:
    if line is None:
        return path
    return f"{path}:{line}"


def _markdown_table_cell(value: object) -> str:
    text = str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _append_render_excerpt(lines: list[str], label: str, content: str | None) -> None:
    if not content:
        return
    lines.extend(["", f"### {label}", "", "```text", content, "```"])


def _finding_counts_by_rule(results: CheckResults) -> list[tuple[str, str, int]]:
    counts = Counter((finding.severity, finding.rule_id) for finding in results.findings)
    return sorted(((severity, rule_id, count) for (severity, rule_id), count in counts.items()), key=lambda item: (-item[2], item[0], item[1]))


def _append_finding_summary(lines: list[str], results: CheckResults) -> None:
    lines.extend(["", "## Finding Summary", ""])
    counts = _finding_counts_by_rule(results)
    if not counts:
        lines.append("- No findings.")
        return

    lines.extend(["| Severity | Rule | Count |", "|---|---|---:|"])
    for severity, rule_id, count in counts:
        lines.append(f"| {_markdown_table_cell(severity)} | {_markdown_table_cell(rule_id)} | {count} |")


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
            lines.append(
                f"| {_markdown_table_cell(finding.severity)} | {_markdown_table_cell(finding.rule_id)} | "
                f"{_markdown_table_cell(finding.path)} | {_markdown_table_cell(line)} | {_markdown_table_cell(finding.message)} |"
            )
    else:
        lines.append("| ok | none |  |  | No findings |")

    _append_finding_summary(lines, results)

    lines.extend(["", "## Gallery", ""])
    if results.gallery.items:
        for item in results.gallery.items:
            lines.append(f"- {item.status.upper()} {item.path}: {item.message}")
    else:
        lines.append("- No gallery entries checked.")

    lines.extend(["", "## Render", "", f"- {results.render.get('status', 'skipped')}: {results.render.get('message', 'disabled')}"])
    if "process_exit_code" in results.render:
        lines.append(f"- Process exit code: {results.render.get('process_exit_code')}")
    _append_render_excerpt(lines, "MATLAB stdout excerpt", results.render.get("stdout_excerpt"))
    _append_render_excerpt(lines, "MATLAB stderr excerpt", results.render.get("stderr_excerpt"))
    lines.extend(["", "## Next steps", ""])
    if summary.get("errors", 0):
        lines.append("- Fix error findings before releasing or merging.")
    elif summary.get("warnings", 0):
        lines.append("- Review warning findings and confirm they are intentional.")
    else:
        lines.append("- No blocking issues found.")
    lines.append("")
    return "\n".join(lines)


def build_pr_comment_report(results: CheckResults) -> str:
    summary = results.summary
    errors = int(summary.get("errors", 0))
    warnings = int(summary.get("warnings", 0))
    status = "failed" if errors else "passed"
    lines = [
        "### matlab-figure-ci check",
        "",
        f"Status: **{status}**",
        "",
        f"- Errors: {errors}",
        f"- Warnings: {warnings}",
        f"- Files scanned: {summary.get('files_scanned', 0)}",
        f"- Gallery checks: {summary.get('gallery_checks', 0)}",
        f"- MATLAB render: {results.render.get('status', 'skipped')}",
        "",
    ]

    if results.findings:
        counts = _finding_counts_by_rule(results)
        if counts:
            lines.extend(["Finding summary:", "", "| Severity | Rule | Count |", "|---|---|---:|"])
            for severity, rule_id, count in counts[:5]:
                lines.append(f"| {_markdown_table_cell(severity)} | {_markdown_table_cell(rule_id)} | {count} |")
            if len(counts) > 5:
                lines.append(f"| info | truncated | {len(counts) - 5} more rule group(s) in the full report |")
            lines.append("")

        lines.extend(
            [
                "Top findings:",
                "",
                "| Severity | Rule | Location | Message |",
                "|---|---|---|---|",
            ]
        )
        for finding in results.findings[:8]:
            lines.append(
                f"| {_markdown_table_cell(finding.severity)} | {_markdown_table_cell(finding.rule_id)} | "
                f"{_markdown_table_cell(_format_location(finding.path, finding.line))} | {_markdown_table_cell(finding.message)} |"
            )
        if len(results.findings) > 8:
            lines.append(f"| info | truncated |  | {len(results.findings) - 8} more finding(s) in the full report |")
        lines.append("")
    else:
        lines.extend(["No findings.", ""])

    if results.render.get("status") == "error":
        lines.append(f"Render error: {results.render.get('message', 'MATLAB render failed.')}")
        if "process_exit_code" in results.render:
            lines.append(f"MATLAB process exit code: {results.render.get('process_exit_code')}")
        lines.append("See the full report artifact for stdout/stderr excerpts.")
        lines.append("")

    if errors:
        lines.append("Next step: fix error findings before merging or releasing.")
    elif warnings:
        lines.append("Next step: review warning findings and confirm they are intentional.")
    else:
        lines.append("Next step: no blocking figure-quality issues found.")
    lines.append("")
    return "\n".join(lines)


def build_evidence_packet_report(results: CheckResults) -> str:
    summary = results.summary
    errors = int(summary.get("errors", 0))
    warnings = int(summary.get("warnings", 0))
    status = "needs attention" if errors else "ready for maintainer review"
    lines = [
        "### matlab-figure-ci evidence packet",
        "",
        f"Status: **{status}**",
        "",
        "Generated from `.mfigci-results.json`. Fill the placeholders before sharing.",
        "",
        "Verification summary:",
        "",
        f"- Errors: {errors}",
        f"- Warnings: {warnings}",
        f"- Files scanned: {summary.get('files_scanned', 0)}",
        f"- Gallery checks: {summary.get('gallery_checks', 0)}",
        f"- MATLAB render: {results.render.get('status', 'skipped')}",
        f"- Config: `{results.config_path or 'mfigci.yml'}`",
        f"- Tool version: `{results.tool_version or 'unknown'}`",
        "",
        "Artifacts to attach or link:",
        "",
        "- `mfigci-report.md`",
        "- `.mfigci-results.json`",
        "- workflow run URL: `<paste GitHub Actions run URL>`",
        "- commit: `<paste commit SHA>`",
        "- redacted issue or PR link: `<paste public issue/PR URL>`",
        "",
    ]

    counts = _finding_counts_by_rule(results)
    if counts:
        lines.extend(["Finding summary:", "", "| Severity | Rule | Count |", "|---|---|---:|"])
        for severity, rule_id, count in counts[:8]:
            lines.append(f"| {_markdown_table_cell(severity)} | {_markdown_table_cell(rule_id)} | {count} |")
        if len(counts) > 8:
            lines.append(f"| info | truncated | {len(counts) - 8} more rule group(s) in the full report |")
        lines.append("")
    else:
        lines.extend(["Finding summary: no findings.", ""])

    lines.extend(
        [
            "Review packet:",
            "",
            "- Check the changed files against the findings above.",
            "- Confirm privacy findings are redacted and paths are relative.",
            "- Fix policy errors before merge or release.",
            "- Review warnings as provenance or maintenance prompts, not as license-cleaning proof.",
            "",
            "Application packet:",
            "",
            "- Use the repository URL, release tag or commit, workflow run URL, and redacted issue or PR link.",
            "- Mention dogfooding only when the downstream workflow is linked.",
            "- Keep `mfigci-report.md` and `.mfigci-results.json` as artifacts or summaries.",
            "- This is not an approval argument, usage metric, download claim, or adoption claim.",
            "",
        ]
    )
    return "\n".join(lines)


def build_json_report(results: CheckResults) -> str:
    payload = results.to_dict()
    public_payload = {
        "schema_version": "mfigci.report.v1",
        "tool_version": payload.get("tool_version", ""),
        "config_path": payload.get("config_path", ""),
        "summary": payload.get("summary", {}),
        "findings": payload.get("findings", []),
        "gallery": payload.get("gallery", {}),
        "render": payload.get("render", {}),
    }
    return json.dumps(public_payload, indent=2, ensure_ascii=False) + "\n"


def save_results(results: CheckResults, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def load_results(path: str | Path) -> CheckResults:
    results_path = Path(path)
    if not results_path.exists():
        raise FileNotFoundError(
            f"{results_path} not found. Run `mfigci check --results .mfigci-results.json` first, "
            "then `mfigci report --input .mfigci-results.json`."
        )
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse {results_path}: {exc.msg}") from exc
    return CheckResults.from_dict(data)


def save_markdown(results: CheckResults, path: str | Path, style: str = "full") -> None:
    if style == "pr-comment":
        content = build_pr_comment_report(results)
    elif style == "evidence":
        content = build_evidence_packet_report(results)
    else:
        content = build_markdown_report(results)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def save_json_report(results: CheckResults, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_json_report(results), encoding="utf-8")
