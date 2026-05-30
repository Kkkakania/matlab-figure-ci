# Roadmap

`matlab-figure-ci` is intentionally small. The roadmap should match README,
CHANGELOG, and the latest GitHub release.

## Current State

- Latest release: `v2.4.5`.
- Supported install path: GitHub release tag.
- Dogfooded by `matlab-scientific-figures`.
- PyPI is planned but not published yet.
- Maturity: small public CLI; adoption claims should stay conservative until
  external users appear.
- Stable public surface: CLI commands, config keys, JSON report fields, exit
  behavior, and policy warning semantics documented for v2.

## Completed Release Tracks

### v0.3.0: Adoption Diagnostics

Delivered:

- `mfigci doctor`.
- Effective configuration inspection.
- Privacy-safe configuration summaries.

### v1.0.0: Stable CLI Contract

Delivered:

- Stable command set for `scan`, `gallery`, `check`, `report`, `init`, and
  optional `render`.
- Documented exit behavior and local-first usage.
- Downstream dogfooding in `matlab-scientific-figures`.

### v2.0.0: Compatibility Boundary

Delivered:

- Stable config and report compatibility contract.
- v2 compatibility documentation.
- Public policy behavior for privacy, provenance, risky extensions, gallery
  checks, and optional MATLAB rendering.

### v2.1.0: Policy Visibility

Delivered:

- `mfigci rules`.
- Downstream workflow step that prints the effective policy before checking.

### v2.2.0: Warning Policy Clarity

Delivered:

- README guidance that strict warning failure is available.
- Downstream dogfooding keeps warnings non-blocking while policy evidence is
  visible in CI artifacts.

### v2.3.0: Adoption Hardening

Delivered:

- Current GitHub release tag used by README install examples.
- CHANGELOG and documentation aligned around the v2 adoption path.
- Continued downstream dogfooding by `matlab-scientific-figures`.

### v2.4.0: Policy Validation

Delivered:

- Early validation for policy rule severities.
- Early validation for strict warning settings.
- Early validation for extension policy lists.
- README install examples aligned to the current release tag.

### v2.4.1: Workflow Template Maintenance

Delivered:

- Repository CI workflows updated to Node 24-ready GitHub Actions.
- `mfigci init` now generates Node 24-ready workflow examples.
- README GitHub Actions snippets match the generated template.
- Release tag, package smoke checks, and downstream dogfooding stay aligned.

### v2.4.2: Adoption Materials

Delivered:

- Tested starter configurations for common onboarding modes.
- Adoption playbook for staged rollout from scan-only checks to gallery
  manifests and optional MATLAB rendering.
- GitHub issue and pull request templates for reproducible maintainer feedback.
- Release cadence documentation that separates patch, minor, and major release
  reasons.

### v2.4.3: Least-Privilege Workflows

Delivered:

- Generated GitHub Actions workflow now includes `permissions: contents: read`.
- README workflow snippet mirrors the least-privilege template.
- CLI tests assert the generated workflow keeps the permission boundary.

### v2.4.4: Adoption Feedback and Scan Noise

Delivered:

- Adoption report issue template for downstream repository feedback.
- Documentation for excluding a reviewed root `LICENSE` without exempting
  third-party license bundles.
- Sample configs and generated init config include the reviewed root `LICENSE`
  exclusion.

### v2.4.5: Policy Diagnostics in CI

Delivered:

- Generated GitHub Actions workflow runs `mfigci rules --config mfigci.yml`
  before the full quality gate.
- README workflow snippet mirrors the policy diagnostics step.
- CLI tests assert the generated workflow exposes effective policy rules before
  enforcement.

## Next Candidates

- PyPI release after package-name recheck and clean install smoke tests.
- More sample configs for figure repositories with PNG/SVG/PDF galleries.
- A short migration note for users moving from GitHub tag installs to PyPI.
- Stronger docs around warning policy choices and CI lifecycle maintenance.

## Versioning Pace

The fast `v2.x` stabilization happened during the first public hardening pass.
It should not become the normal release rhythm. Future releases should follow
[Release cadence](docs/release-cadence.md): patch tags for small fixes, minor
tags for user-visible workflows, and no major tag unless the public
compatibility boundary changes.

## Non-Goals

- Web UI.
- Cloud service.
- PR comment bot.
- GitHub Marketplace action.
- Complex plugin system.
- Artificial usage, stars, downloads, or adoption claims.
