# PR Comment Report

`mfigci` can generate a compact Markdown report for manual pull request review.
This is not a bot, GitHub App, or external service. It only formats the existing
`.mfigci-results.json` file so a maintainer can paste the result into a PR,
release checklist, or review note.

## Usage

Run the checks first:

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

Then generate a compact comment:

```bash
mfigci report --style pr-comment --output mfigci-pr-comment.md
```

The command reads `.mfigci-results.json` by default. If that file does not
exist, run `mfigci check` first.

## Example Output

```markdown
### matlab-figure-ci check

Status: **failed**

- Errors: 1
- Warnings: 1
- Files scanned: 42
- Gallery checks: 10
- MATLAB render: skipped

Finding summary:

| Severity | Rule | Count |
|---|---|---:|
| error | privacy.email | 1 |
| warning | provenance.author_marker | 1 |

Top findings:

| Severity | Rule | Location | Message |
|---|---|---|---|
| error | privacy.email | src/example.m:3 | <redacted> |
| warning | provenance.author_marker | README.md:12 | pattern matched |

Next step: fix error findings before merging or releasing.
```

Privacy matches remain redacted in the compact report, the full report, terminal
output, and JSON results.
