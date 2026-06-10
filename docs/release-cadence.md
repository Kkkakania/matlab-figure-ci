# Release Cadence

`matlab-figure-ci` had a fast initial stabilization day on 2026-05-30 while the
CLI contract, report format, policy checks, and downstream dogfooding path were
being separated into release milestones.

Going forward, releases should slow down.

## Current Policy

- Keep `v2.5.0` as the current public release until a user-visible reason
  justifies another tag.
- Use patch releases, such as `v2.5.1`, for documentation, CI template, or
  packaging maintenance.
- Use minor releases, such as `v2.6.0`, only when users get a new command,
  policy option, report field, or documented workflow.
- Do not use another major release unless the public CLI, config, report, or
  policy compatibility boundary changes.

## What Does Not Need A Release

These changes can land on `main` without a tag:

- README wording.
- ROADMAP cleanup.
- Small documentation navigation improvements.
- Internal tests that do not change user-visible behavior.

## Maintainer Note

The project should look maintained because the CLI behavior, documentation,
tests, and release notes agree, not because many tags are published quickly.
