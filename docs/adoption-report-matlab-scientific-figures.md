# Adoption Report: matlab-scientific-figures

Snapshot date: 2026-06-04

This report records how the companion repository
[`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures)
uses `matlab-figure-ci`. It is a dogfooding record for maintainers, not a
download metric, external adoption claim, or program eligibility claim.

## Repository Context

| Field | Value |
|---|---|
| Repository type | MATLAB scientific figure gallery |
| Visibility | Public |
| Tool version | `mfigci 2.4.5` |
| Install mode | GitHub release tag in GitHub Actions |
| MATLAB render in public CI | Disabled |
| Gallery policy | Committed output check |
| Latest checked downstream commit | `262431b` |

The downstream workflow installs `matlab-figure-ci`, prints the effective rules,
runs the full check, and uploads the Markdown report artifact:

```bash
mfigci rules --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
```

## Configuration Summary

The downstream configuration uses:

- `presets: ["matlab-figures"]`
- committed gallery checks for 30 PNG files and 30 SVG files
- `.png`, `.svg`, and `.pdf` as allowed gallery extensions
- `strict.fail_on_warnings: false`
- `matlab.enabled: false`
- reviewed exclusions for the repository's own `LICENSE` and local scanner
  implementation files that intentionally contain policy patterns

PDF is allowed in the gallery configuration because many figure repositories
export publication-ready vector PDFs, but the current manifest only expects PNG
and SVG files.

## Current Result

Latest local dogfooding command:

```bash
mfigci check --config mfigci.yml --report mfigci-report.md --results .mfigci-results.json
```

Result:

```text
0 error(s), 0 warning(s), 260 file(s) scanned, 30 binary/skipped.
0 error(s), 0 warning(s), 60 gallery file(s) ok.
```

## What Worked

- The gallery manifest catches missing or empty committed figure outputs without
  requiring MATLAB on GitHub-hosted runners.
- `mfigci rules` makes the effective privacy, provenance, and extension policy
  visible in CI logs before the full check runs.
- The Markdown report is useful as a CI artifact because it uses relative paths
  and redacts privacy-sensitive findings.
- Keeping MATLAB render disabled in public CI matches the reality that public
  runners usually do not have MATLAB installed.
- The downstream repository now also checks GitHub Project-board documentation
  and keeps the live board setup pending until GitHub Projects scopes or a
  verified web-created board are available.

## Current Boundaries

- A green `mfigci` check proves the committed gallery artifacts are present and
  policy-clean; it does not prove GitHub regenerated those artifacts from MATLAB
  source.
- MATLAB rendering and unit tests remain a downstream local release-gate
  responsibility unless a runner with MATLAB is explicitly available.
- Warning-strict mode is useful for release gates, but normal development keeps
  provenance warnings as review prompts rather than automatic failures.

## Follow-Up Uses

This report should be updated when the downstream gallery manifest, policy
preset, or CI installation path changes. It is also a concrete reference for new
adopters who want a staged setup: start with scanning, add committed gallery
checks, and enable MATLAB render only where MATLAB is actually available.
