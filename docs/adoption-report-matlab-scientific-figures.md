# Adoption Report: matlab-scientific-figures

Snapshot date: 2026-07-09

This report records how the companion repository
[`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures)
uses `matlab-figure-ci`. It is a dogfooding record for maintainers, not a
download metric, external adoption claim, or program eligibility claim.

## Repository Context

| Field | Value |
|---|---|
| Repository type | MATLAB scientific figure gallery |
| Visibility | Public |
| Tool version | `mfigci 2.5.0` |
| Install mode | GitHub release tag in GitHub Actions |
| MATLAB render in public CI | Disabled |
| Gallery policy | Committed output check |
| Latest checked downstream commit | `6a1939e` |
| Latest checked workflow | Figure quality run `28958347031` and Quality checks run `28958347024`, both successful and annotation-free |

The downstream workflow installs `matlab-figure-ci`, prints the effective rules,
runs the full check, and uploads Markdown report and `.mfigci-results.json` artifacts:

```bash
mfigci rules --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
```

Run URLs:

- Figure quality:
  <https://github.com/Kkkakania/matlab-scientific-figures/actions/runs/28958347031>
- Quality checks:
  <https://github.com/Kkkakania/matlab-scientific-figures/actions/runs/28958347024>

## Configuration Summary

The downstream configuration uses:

- `presets: ["matlab-figures"]`
- committed gallery checks for 31 PNG files and 31 SVG files
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
0 error(s), 0 warning(s), 291 file(s) scanned, 31 binary/skipped.
0 error(s), 0 warning(s), 62 gallery file(s) ok.
```

The downstream `Figure quality` and `Quality checks` GitHub Actions workflows
also completed successfully for commit `6a1939e` with zero annotations in the
checked snapshot while the repository stayed pinned to the public `v2.5.0` tag.

## What Worked

- The gallery manifest catches missing or empty committed figure outputs without
  requiring MATLAB on GitHub-hosted runners.
- `mfigci rules` makes the effective privacy, provenance, and extension policy
  visible in CI logs before the full check runs.
- The Markdown report is useful as a CI artifact because it uses relative paths
  and redacts privacy-sensitive findings.
- The machine-readable `.mfigci-results.json` artifact is uploaded beside the
  Markdown report, so later PR review or release-note tooling can inspect the
  same redacted result without scraping Markdown.
- Keeping MATLAB render disabled in public CI matches the reality that public
  runners usually do not have MATLAB installed.
- The downstream repository now also checks GitHub Project-board documentation
  and keeps the live board setup pending until GitHub Projects scopes or a
  verified web-created board are available.
- The downstream maintainer-activity page now includes a repeatable visible
  fork intake helper and records that checked fork default branches had no
  ahead commits to review.
- The downstream Project-board plan now includes a no-Projects-scope triage
  helper for reviewing current open issues and pull requests while the live
  board remains pending.
- The downstream repository now also has a Chinese Project-board setup guide,
  linked from its Chinese README and documentation index, so maintainers can
  recover the same pending-board workflow without relying on the English plan.
- The downstream Project-board docs now explicitly warn maintainers to verify
  the active browser account before using the GitHub web UI, because the `gh`
  CLI account and browser session can point to different GitHub users.
- The downstream Project-board docs now list interim labels for the current
  open issues, so triage remains inspectable while the live GitHub Project board
  is still pending.
- The downstream Project-board seed queue now removes closed feedback hub issues
  from the live board plan while preserving the still-open Project-board,
  domain-pack, and PyPI decision items.
- The downstream workflow now pins `matlab-figure-ci` to `v2.5.0`, keeping the
  README, maintainer dashboard, quality-gate documentation, and version guard
  script aligned with the current public checker release.
- The downstream domain examples now carry the accepted issue-feedback unit
  refinements for the synthetic 5 MW PV example and harmonic magnitudes in
  `% of fundamental`, without expanding the domain pack before more feedback.
- The downstream live snapshot helper now treats green CI and annotation-free status
  as an evidence boundary, so an application packet can cite exact run URLs
  without turning workflow success into an adoption claim.

## Current Boundaries

- A green `mfigci` check proves the committed gallery artifacts are present and
  policy-clean; it does not prove GitHub regenerated those artifacts from MATLAB
  source.
- A successful workflow run is evidence for repository maintenance hygiene, not
  proof of external usage, download volume, or program eligibility.
- MATLAB rendering and unit tests remain a downstream local release-gate
  responsibility unless a runner with MATLAB is explicitly available.
- Warning-strict mode is useful for release gates, but normal development keeps
  provenance warnings as review prompts rather than automatic failures.

## Follow-Up Uses

This report should be updated when the downstream gallery manifest, policy
preset, or CI installation path changes. It is also a concrete reference for new
adopters who want a staged setup: start with scanning, add committed gallery
checks, and enable MATLAB render only where MATLAB is actually available.
