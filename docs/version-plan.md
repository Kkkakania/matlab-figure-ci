# Version Plan

This project uses version numbers to mark verified behavior, not momentum.

## Current State

- Current public release: `v2.4.5`.
- Distribution: GitHub release tag install.
- Maturity: small public CLI, dogfooded by the companion
  `matlab-scientific-figures` repository, not yet claiming broad adoption.
- PyPI is planned after package-name and clean-install checks.

Future tags should follow [Release cadence](release-cadence.md). Small
documentation or workflow-template edits can land on `main` without a tag.

## v0.3.0 Released

Goal met: make configuration easier to inspect before a repository enables CI.

Delivered:

- `mfigci doctor`.
- Effective config, enabled scanner, gallery, and MATLAB render summaries.
- Privacy-safe output that avoids leaking scan matches or private paths.

Primary issue: #7.

## v1.0.0 Released

Goal met: define what downstream users can rely on.

Delivered:

- Command names and exit codes.
- `.mfigci-results.json` structure.
- JSON report schema.
- Redaction guarantees.
- Relative-path guarantees.
- Default config behavior.

Primary issue: #8.

## v2.0.0 Released

Goal met: mark an explicit compatibility boundary for policy and report
behavior.

Delivered:

- Migration notes from v0.x/v1.x.
- Tests for the public contract.
- Stable documented policy behavior.
- Dogfooding by the companion repository.

Primary issue: #9.
Compatibility notes: `docs/v2-compatibility.md`.

## v2.4.1 Released

Goal met: keep generated workflow templates aligned with current GitHub Actions
runtime changes.

Delivered:

- Node 24-ready workflow templates.
- README install and GitHub Actions snippets aligned to the current release tag.
- Continued downstream dogfooding by `matlab-scientific-figures`.

## v2.4.3 Released

Goal met: harden generated GitHub Actions workflows with least-privilege
defaults.

Delivered:

- `mfigci init` workflow template now includes `permissions: contents: read`.
- README workflow snippet mirrors the generated template.
- CLI tests assert the generated workflow keeps least-privilege permissions.

## v2.4.4 Released

Goal met: publish post-v2 adoption and scan-noise hardening after it proved
useful in downstream dogfooding.

Delivered:

- Adoption report issue template for downstream feedback.
- README package workflow badge and adoption feedback documentation.
- Reviewed root `LICENSE` exclusion in sample configs and generated
  `mfigci init` configuration.
- Documentation on excluding a reviewed project `LICENSE` without exempting
  third-party license bundles.

## v2.4.5 Released

Goal met: make generated GitHub Actions workflows show the effective policy
before enforcing it.

Delivered:

- `mfigci init` workflow template now runs `mfigci rules --config mfigci.yml`
  before `mfigci check`.
- README GitHub Actions snippet mirrors the generated workflow.
- CLI tests assert the generated workflow exposes policy diagnostics.

## v2.4.2 Released

Goal met: ship the post-v2 adoption and maintenance polish as a patch release.

Delivered:

- Tested sample configs for common onboarding modes.
- Adoption playbook for staged repository rollout.
- GitHub issue and pull request templates.
- Release cadence documentation.
- Generated workflow template updated to current maintained GitHub Actions and
  `permissions: contents: read`.

## What Version Numbers Do Not Mean

- They do not imply external adoption, downloads, or stars.
- They do not guarantee any benefit-program approval.
- They do not require a Web UI, cloud service, bot, or marketplace action.
- They do not replace maintainer review.
