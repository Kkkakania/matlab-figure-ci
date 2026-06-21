# Adoption Report: matlab-plotting-skill

Snapshot date: 2026-06-21

This report records how the companion repository
[`matlab-plotting-skill`](https://github.com/Kkkakania/matlab-plotting-skill)
uses `matlab-figure-ci`. It is a dogfooding record for maintainers, not a
download metric, external adoption claim, or program eligibility claim.

## Repository Context

| Field | Value |
|---|---|
| Repository type | Agent-facing MATLAB plotting skill |
| Visibility | Public |
| Tool version | `mfigci 2.5.0` |
| Install mode | GitHub release tag in GitHub Actions |
| MATLAB render in public CI | Disabled |
| Gallery policy | Committed preview check |
| Latest checked downstream commit | `a28131f` |
| Latest checked workflow | Quality workflow, run `27894703366`, successful and annotation-free |

The downstream workflow installs `matlab-figure-ci` from the public `v2.5.0` tag,
prints the effective rules, runs the full check, and uploads Markdown report and
`.mfigci-results.json` artifacts:

```bash
mfigci rules --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
```

Run URL:
<https://github.com/Kkkakania/matlab-plotting-skill/actions/runs/27894703366>

## Configuration Summary

The downstream configuration uses:

- `presets: ["matlab-figures"]`
- committed preview checks for 13 PNG files under `docs/gallery`
- `.png`, `.svg`, and `.pdf` as allowed gallery extensions
- `strict.fail_on_warnings: false`
- `matlab.enabled: false`
- reviewed exclusions for the repository's own `LICENSE`, shell privacy scanner,
  first-use feedback collector, and tests that intentionally contain policy
  patterns

The gallery manifest currently expects PNG previews because that is what the
skill repository commits. SVG and PDF remain allowed extensions for future
render outputs, but they are not claimed as current expected artifacts.

## Current Result

Latest local dogfooding command with the released checker:

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

Result:

```text
0 error(s), 1 warning(s), 104 file(s) scanned, 13 binary/skipped.
0 error(s), 0 warning(s), 13 gallery file(s) ok.
```

The downstream `Quality` GitHub Actions workflow also completed successfully
for commit `a28131f`, with no GitHub annotations at the checked snapshot.

## What Worked

- The committed preview gallery is checked before first-use reports or render
  summaries are reused in public issue triage.
- `mfigci rules` exposes the active privacy, provenance, extension, and gallery
  policy before the full check runs.
- The Markdown report and `.mfigci-results.json` artifacts work together: the
  Markdown is readable in a review, and the JSON can feed later triage or
  release-note tooling without scraping prose.
- `mfigci-report.md`, `.mfigci-results.json`, and `mfigci-evidence.md` stay
  ignored locally unless a maintainer deliberately reviews and commits a
  redacted report.
- The skill repository now carries its own reviewer-facing
  `docs/application-evidence.md`, and it now describes the repository as
  companion skill evidence for `matlab-scientific-figures` rather than as the
  main Codex for Open Source application repository.
- The no-render public CI boundary matches the repository's first-use story:
  metadata, docs, manifests, and committed previews can be checked without
  requiring MATLAB on GitHub-hosted runners.

## Current Boundaries

- A green `mfigci` check is not proof that MATLAB rendered on GitHub-hosted runners.
- `render_report.md/json` and exported figures are handoff artifacts; render reports are producer evidence, not source material.
- The check does not prove that a user's private data, local template folder, or
  third-party plotting helper is safe to publish.
- The report should be cited as maintainer evidence only when linked to the
  exact commit, workflow run, and command summary above.
- The one current warning is the reviewed generated-asset warning for the
  checked diagram SVG under the skill examples directory.
- A green downstream workflow should be cited only together with the exact run
  URL and annotation status, not as broad adoption evidence.

## Follow-Up Uses

Update this report when `matlab-plotting-skill` changes its gallery manifest,
pins a different `matlab-figure-ci` tag, or starts running MATLAB render on a
runner where MATLAB is explicitly available.
