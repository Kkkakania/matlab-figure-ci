# OpenAI Codex Maintainer Workflow

`matlab-figure-ci` is designed to support real open-source maintenance.

Useful workflows include:

- review pull requests for missing gallery outputs
- catch risky binary files before releases
- summarize scan and gallery failures in release preparation
- triage issues into scanner rules, MATLAB render problems, and documentation
  gaps
- help maintain a clean dogfooding workflow for `matlab-scientific-figures`

AI assistance should not replace maintainer review. It should make review more
consistent and make release checks easier to repeat.

## Dogfooding Review Loop

Use the companion repository as the first adoption test:

1. Update `matlab-figure-ci` on a release tag.
2. Upgrade `matlab-scientific-figures` to that tag.
3. Run `mfigci check --config mfigci.yml --report mfigci-report.md`.
4. Confirm the downstream GitHub Actions workflow passes.
5. Convert any recurring warning or confusing output into a focused issue.

Dogfooding evidence should be factual: link the downstream workflow, release
tag, and issue numbers. Do not translate a passing internal workflow into
claims about broad adoption, downloads, or guaranteed external review outcomes.

This project does not claim that any application or benefit program will be
approved. Its purpose is to create useful, auditable maintenance automation.
