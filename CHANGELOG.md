# Changelog

## Unreleased

- Planned: post-v2 packaging and adoption hardening.

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
