# Roadmap

`matlab-figure-ci` is intentionally small. The roadmap should match README,
CHANGELOG, and the latest GitHub release.

## Current State

- Latest release: `v2.3.0`.
- Supported install path: GitHub release tag.
- Dogfooded by `matlab-scientific-figures`.
- PyPI is planned but not published yet.
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

## Next Candidates

- PyPI release after package-name recheck and clean install smoke tests.
- More sample configs for figure repositories with PNG/SVG/PDF galleries.
- A short migration note for users moving from GitHub tag installs to PyPI.
- Stronger docs around warning policy choices.

## Non-Goals

- Web UI.
- Cloud service.
- PR comment bot.
- GitHub Marketplace action.
- Complex plugin system.
- Artificial usage, stars, downloads, or adoption claims.
