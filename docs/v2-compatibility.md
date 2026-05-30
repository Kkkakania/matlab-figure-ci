# v2 Compatibility Boundary

`matlab-figure-ci` v2 is the compatibility boundary for local-first MATLAB
figure repository checks. It does not add a cloud service, Web UI, bot, or
marketplace action. The value of v2 is a documented and tested policy/report
contract.

## Stable Commands

These commands are part of the v2 public CLI surface:

| Command | Stability |
|---|---|
| `mfigci scan` | Stable |
| `mfigci gallery` | Stable |
| `mfigci check` | Stable |
| `mfigci report` | Stable |
| `mfigci init` | Stable |
| `mfigci render` | Stable optional command |
| `mfigci doctor` | Stable diagnostics command |

New commands can be added later, but these command names should not be removed
or repurposed without a major release.

## Stable Exit Codes

| Code | Meaning |
|---|---|
| `0` | No policy errors |
| `1` | Policy or gallery errors were found |
| `2` | Configuration, missing-results, or runtime usage error |
| `3` | MATLAB render failed |

Warnings alone do not make `scan`, `gallery`, or `check` fail.

## Stable Config Keys

The following top-level keys are public v2 config keys:

- `project`
- `presets`
- `scan`
- `privacy`
- `provenance`
- `extensions`
- `gallery`
- `strict`
- `matlab`

The following nested keys are stable enough for downstream repositories:

- `project.name`
- `scan.include`
- `scan.exclude`
- `privacy.enabled`
- `privacy.redact_matches`
- `privacy.rules`
- `provenance.enabled`
- `provenance.rules`
- `extensions.error`
- `extensions.warning`
- `extensions.allow`
- `gallery.path`
- `gallery.allowed_extensions`
- `gallery.min_size_bytes`
- `gallery.expected`
- `strict.fail_on_warnings`
- `matlab.enabled`
- `matlab.bin_env`
- `matlab.fallback_bin`
- `matlab.batch_command`

Unknown future keys should be ignored unless they conflict with existing keys.

## Stable Policy Behavior

- Privacy rules are errors by default.
- Privacy match messages are redacted as `<redacted>`.
- Provenance rules are warnings by default.
- Warnings do not fail `mfigci scan` or `mfigci check` by default.
- `strict.fail_on_warnings: true` or `--fail-on-warnings` makes warning-only
  `scan` and `check` runs return exit code 1.
- Risky binary extensions such as `.p`, `.mat`, and `.fig` are errors by
  default.
- `.pdf` is a warning globally but may be allowed in gallery paths by the
  `matlab-figures` preset.
- Text scanning skips binary or undecodable files instead of crashing.
- Paths in findings and gallery items are repository-relative.

## Stable Report Behavior

The public JSON report uses `schema_version: mfigci.report.v1`. See
`docs/json-report.md` for stable fields and examples. The `.mfigci-results.json`
working file remains readable by `mfigci report` but is not the recommended
integration surface for external tools.

## Migration From v0.x And v1.x

For most repositories, migration is:

1. Upgrade the install tag in CI.
2. Run `mfigci doctor --config mfigci.yml` and review the effective config.
3. Run `mfigci check --config mfigci.yml --report mfigci-report.md`.
4. If consuming JSON, prefer `mfigci report --format json` over parsing
   `.mfigci-results.json` directly.

Projects that had treated provenance warnings as failures should keep doing so
in their own CI wrapper if desired. The default v2 behavior keeps provenance as
warning-only to avoid false blocking.

## Non-Goals

- No hosted scanning service.
- No PR comment bot requirement.
- No GitHub Marketplace action requirement.
- No broad plugin system.
- No copyright-cleaning claims.
- No usage, download, or adoption inflation.
