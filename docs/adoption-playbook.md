# Adoption Playbook

This playbook shows a conservative rollout path for adding `matlab-figure-ci`
to a MATLAB figure repository. The goal is to make quality checks useful early
without turning CI into a fragile release blocker.

## Stage 1: Static Scan

Start with privacy, provenance, and risky-extension scanning only.

```bash
cp examples/configs/minimal-static-scan.yml mfigci.yml
mfigci scan --config mfigci.yml
```

For pre-commit or staged-file checks, scan only the files being reviewed:

```bash
mfigci scan --config mfigci.yml --paths src/plot.m docs/usage.md
```

The selected paths still respect configured excludes, missing files are ignored,
and symlinks that resolve outside the project root are skipped.

Use this stage when a repository has source code and documentation but no stable
gallery output yet.

Expected outcome:

- privacy findings are errors
- provenance findings are warnings
- risky binary/source files such as `.fig`, `.mat`, `.p`, `.docx`, and `.xlsx`
  are blocked
- MATLAB is not required

## Stage 2: Gallery Manifest

Once example figures are committed, add exact gallery expectations.

```bash
cp examples/configs/png-svg-gallery.yml mfigci.yml
mfigci gallery --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
```

Keep the manifest small at first. List only figures that are intentionally part
of the public gallery. Avoid temporary renders, private drafts, and screenshots
that contain local paths or unpublished project details.

For figure repositories that export vector PDFs, use
`examples/configs/png-svg-pdf-gallery.yml` and keep PDF files under the gallery
path. The default extension policy warns on PDFs outside the gallery because
they can also be papers, scans, or unclear source material.

## Stage 3: Release Gate

After the repository has stable examples and clean reports, enable warning
failures only in release-oriented jobs.

```bash
mfigci check --config mfigci.yml --report mfigci-report.md --fail-on-warnings
```

Or use the configuration form:

```yaml
strict:
  fail_on_warnings: true
```

This is useful for release tags and pre-release branches. It is often too strict
for early development because provenance warnings are designed to prompt human
review, not to claim a file is illegal or unsafe.

## Stage 4: Optional MATLAB Render

Keep render disabled on public GitHub-hosted runners unless MATLAB is explicitly
available.

```yaml
matlab:
  enabled: false
```

For local machines or self-hosted runners:

```bash
export MATLAB_BIN=/Applications/MATLAB_R2025a.app/bin/matlab
mfigci render --config mfigci.yml
```

When render is enabled in `mfigci check`, failures use a distinct render exit
code so maintainers can separate policy failures from MATLAB runtime failures.

## Dogfooding Pattern

The companion repository `matlab-scientific-figures` uses the staged approach:

- gallery files are checked against a real manifest
- scan rules run without requiring MATLAB
- render remains optional
- reports are uploaded as CI artifacts

This is a maintenance signal: the tool is exercised by a real public repository.
It should not be described as download volume, external adoption, or guaranteed program eligibility.

The current dogfooding snapshot is maintained in
[`adoption-report-matlab-scientific-figures.md`](adoption-report-matlab-scientific-figures.md).

## Ecosystem Handoff Contract

Use `matlab-figure-ci` as the review checkpoint between figure-producing work
and public maintenance decisions. The tool should make the handoff boring and
auditable: a small configuration, a Markdown report, a JSON report, and clear
exit codes.

| Producer | Producer artifact | Next consumer | `matlab-figure-ci` responsibility |
|---|---|---|---|
| `matlab-scientific-figures` | `gallery/*.png and gallery/*.svg`, `mfigci.yml`, template docs | Gallery/API maintainer | Check expected outputs, risky extensions, privacy, provenance, generated-asset placement, and release-gate drift |
| `matlab-plotting-skill` | `render_report.md and render_report.json`, generated PNG/SVG outputs, selected scheme explanation | First-use feedback or future template request | Check exported figures and reports before a maintainer copies conclusions into public issue triage |
| `matlab-figure-ci` | `mfigci-report.md and .mfigci-results.json` | Maintainer review, release notes, PR review packets | Preserve relative paths, redact privacy findings, and separate warnings from policy errors |

Do not use `matlab-figure-ci` as a laundering step. A clean scan does not prove
that copied material is licensed, original, or appropriate for release. It only
shows that the configured checks did not find the risks they know how to detect.
Private datasets, source packs, local absolute paths, screenshots from papers,
and unclear third-party helper code should be removed from the handoff before
the report is shared.

## Maintainer Checklist

- Use relative paths in reports and issue examples.
- Redact emails, local usernames, tokens, unpublished project names, and private
  paths before sharing failures publicly.
- Exclude the repository's own reviewed `LICENSE` file if it creates expected
  provenance noise; do not use that as a blanket exception for third-party
  license bundles or copied source packs.
- Keep `gallery.expected` limited to intentional public artifacts.
- Keep MATLAB rendering optional until runners are known to have MATLAB.
- Use warning-strict mode for releases, not as the first onboarding step.

## Share Adoption Feedback

If you try `matlab-figure-ci` in another repository, open an adoption report
issue. Include the smallest relevant `mfigci.yml` snippet, the commands you ran,
the summary counts from the report, and one setup step that was awkward.

Do not include private repository names, local absolute paths, unpublished data
names, tokens, emails, or copied third-party materials. The report is meant to
improve defaults and documentation, not to collect private project details.
