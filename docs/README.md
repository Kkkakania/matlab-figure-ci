# Documentation

[简体中文文档索引](README.zh-CN.md)

This directory collects the public maintainer and user documentation for
`matlab-figure-ci`. Start with the guide that matches the job you are doing.

## Getting Started

- [MATLAB CI guide](matlab-ci-guide.md): configure `mfigci` for figure
  repositories, optional MATLAB batch rendering, and CI runners.
- [Adoption playbook](adoption-playbook.md): roll out static scans, gallery
  checks, release gates, and optional render checks in stages.
- [Dogfooding adoption report](adoption-report-matlab-scientific-figures.md):
  current `matlab-scientific-figures` integration snapshot and check results.
- [Plotting-skill adoption report](adoption-report-matlab-plotting-skill.md):
  current `matlab-plotting-skill` integration snapshot and check results.

## Reports And Rules

- [JSON report](json-report.md): machine-readable report fields, redaction, and
  relative path guarantees.
- [PR comment report](pr-comment-template.md): compact Markdown output for
  manual pull request review.
- [Submission check example](../examples/reports/submission-check-example.md):
  a concrete publication-figure QA report using synthetic paths and bounded
  claims.
- [Evidence packet template](evidence-packet-template.md): copyable review and
  application evidence packet generated from `.mfigci-results.json`.
- [Issue triage report](issue-triage-report.md): compact issue/PR triage note
  generated from `.mfigci-results.json`.
- [Rule design](rule-design.md): privacy, provenance, extension, and preset
  policy choices.
- [Chinese rule design](rule-design.zh-CN.md): Chinese-language explanation of
  privacy, provenance, extension, and gallery PDF boundaries.
- [v2 compatibility](v2-compatibility.md): stable CLI, config, report, and
  policy boundaries for the v2 line.

## Maintainer Workflow

- [OpenAI Codex maintainer workflow](openai-codex-maintainer-workflow.md):
  practical AI-assisted maintenance uses without adoption claims or eligibility
  promises.
- [PyPI release checklist](pypi-release-checklist.md): future package publishing
  readiness steps.
- [Chinese PyPI release checklist](pypi-release-checklist.zh-CN.md):
  Chinese-language publishing gate and non-publishing boundary.
- [Release artifacts](release-artifacts.md): how to inspect the
  `release-preflight` JSON artifact before a release decision.
- [Release cadence](release-cadence.md): versioning and release hygiene for the
  current line.
- [Version plan](version-plan.md): milestone boundaries and public release
  tracking.
