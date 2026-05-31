# Changelog

## Unreleased

- Escape Markdown table cells in full and PR-comment reports so pipe
  characters in paths, rule IDs, or messages do not break report tables.
- Add finding summaries grouped by severity and rule to Markdown and PR-comment
  reports for faster maintainer triage.
- Skip symlinks that resolve outside the scanned project root so local privacy
  and provenance scans do not inspect external workspace files.
- Planned: post-v2 packaging and adoption hardening.
- Added a documentation inventory test that keeps ROADMAP status language
  aligned with the current release, PyPI posture, and slower release cadence.
- Added JSON stdout and `--output` file support for `mfigci release-preflight`
  so release workflows can consume structured preflight summaries and check
  items.
- The Package workflow now runs `release-preflight --require-dist --output`
  and uploads the JSON preflight report as a workflow artifact.
- Added a grouped documentation index and a regression test that keeps every
  documentation Markdown file discoverable from it.
- Added a lightweight CI Markdown link check for repository-local documentation
  links.
- Fixed roadmap and version-plan release metadata ordering after the `v2.4.5`
  release, and added roadmap coverage to the public-version regression test.
- Added a dogfooding adoption report for the current
  `matlab-scientific-figures` integration snapshot.
- Added package metadata regression tests for the distribution name, runtime
  version, CLI entry point, dependency split, and package workflow smoke checks.

## v2.4.5 - 2026-05-30

- Added a regression test that keeps public release references aligned with
  the package version.
- Expanded the Codex maintainer workflow with concrete API credit uses and a
  factual evidence checklist.
- Added CI smoke coverage for `mfigci doctor` and `mfigci rules`.
- Updated the generated `mfigci init` workflow and README workflow snippet to
  print effective policy rules before running the full check.

## v2.4.4 - 2026-05-30

- Added an adoption report issue template for downstream repository feedback.
- Documented how downstream users should share adoption feedback safely.
- Added a README badge for the package build workflow.
- Documented excluding a reviewed project `LICENSE` from scan noise without
  exempting third-party license bundles.
- Added the reviewed `LICENSE` exclusion to sample configs.
- Added the reviewed `LICENSE` exclusion to the generated `mfigci init`
  configuration.

## v2.4.3 - 2026-05-30

- Updated the generated GitHub Actions workflow template and README example to
  include `permissions: contents: read`.

## v2.4.2 - 2026-05-30

- Add release cadence guidance and update the version plan so it matches the
  current release state.
- Added tested example configs for minimal scanning, PNG/SVG galleries,
  PNG/SVG/PDF galleries, and strict release gates.
- Added GitHub issue and pull request templates for reproducible bug reports,
  scoped feature requests, and privacy-aware PR review.
- Added an adoption playbook for staged repository rollout from scan-only
  onboarding to gallery manifests, release gates, and optional MATLAB render.
- Updated the generated GitHub Actions workflow template to use
  `actions/upload-artifact@v5`.

## v2.4.1 - 2026-05-30

- Updated repository workflows to use Node 24-ready `actions/checkout@v6` and
  `actions/setup-python@v6`.
- Updated the generated GitHub Actions workflow template and README snippet to
  use Node 24-ready `actions/checkout@v6` and `actions/setup-python@v6`.

## v2.4.0 - 2026-05-30

- Added early validation for policy rule severities, strict warning settings,
  and extension policy lists.

## v2.3.0 - 2026-05-30

- Added optional `strict.fail_on_warnings` config support for warning-strict
  repositories.

## v2.2.0 - 2026-05-30

- Added optional `--fail-on-warnings` strict mode to `scan` and `check`.

## v2.1.0 - 2026-05-30

- Added `mfigci rules` for privacy-safe inspection of effective policy rules.

## v2.0.0 - 2026-05-30

- Documented the v2 CLI, config, policy, report, and migration compatibility
  boundary.

## v1.0.0 - 2026-05-30

- Documented stable JSON report fields, internal results boundaries, and
  redaction/path guarantees.

## v0.3.0 - 2026-05-30

- Documented the path from v0.3.0 to v2.0.0 with milestone boundaries.
- Added `mfigci doctor` for privacy-safe effective configuration summaries.

## v0.2.1 - 2026-05-30

- Added PyPI release checklist and package build CI for future publishing.
- Added project URLs and optional build dependencies to package metadata.
- Documented downstream dogfooding with `matlab-scientific-figures`.

## v0.2.0 - 2026-05-30

- Added the `matlab-figures` rule preset for gallery-oriented MATLAB figure
  repositories.
- Added `mfigci report --format json` for a documented machine-readable report.
- Added a compact `mfigci report --style pr-comment` output for manual PR
  review notes.
- Added documentation for PR-comment-ready reports without adding a bot or
  external service.

## v0.1.0 - 2026-05-30

- First public release.
- Added `scan`, `gallery`, `check`, `report`, `init`, and optional `render`.
- Added Markdown and JSON reports.
- Added conservative privacy, provenance, and extension checks.
- Added GitHub Actions template and MATLAB CLI documentation.
