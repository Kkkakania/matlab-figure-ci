# Roadmap

`matlab-figure-ci` is intentionally small. Future releases should make the tool
easier to adopt without turning it into a large platform. Version numbers move
only when the public behavior is tested, documented, released, and dogfooded.

## Current State

- Latest release: `v0.2.1`.
- Supported install path: GitHub release tag.
- Dogfooded by `matlab-scientific-figures`.
- PyPI is planned but not published yet.

## v0.3.0: Adoption Diagnostics

Goal: help maintainers understand what `mfigci` will do before CI fails.

- Add a config doctor command.
- Make effective config, gallery expectations, enabled scanners, and MATLAB
  render settings easier to inspect.
- Keep output privacy-safe and path-safe.

Tracking issue: #7.

## v1.0.0: Stable CLI Contract

Goal: define the stable behavior that downstream repositories can rely on.

- Document result schema stability.
- Document exit codes, redaction guarantees, and relative-path guarantees.
- Keep the core commands stable: `scan`, `gallery`, `check`, `report`, `init`,
  and optional `render`.
- Publish only after local package checks and downstream dogfooding pass.

Tracking issue: #8.

## v2.0.0: Compatibility Boundary

Goal: make policy and report compatibility explicit enough for long-term use.

- Define stable config keys, policy rule behavior, result fields, and exit
  codes.
- Add migration notes from v0.x/v1.x.
- Add tests for the public compatibility surface.
- Keep the tool small and local-first.

Tracking issue: #9.

## PyPI Track

PyPI publishing is tracked separately in #1. It should happen only after the
package name is rechecked, build verification passes, and a fresh install smoke
test succeeds. PyPI is not required for the v2.0.0 compatibility boundary, but
it can become the preferred install path once published.

## Non-Goals For Early Releases

- Web UI.
- Cloud service.
- PR comment bot.
- GitHub Marketplace action.
- Complex plugin system.
- Artificial usage, stars, or download claims.
