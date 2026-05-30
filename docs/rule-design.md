# Rule Design

`matlab-figure-ci` is not a copyright-cleaning tool.

Its goal is to stop unclear provenance, accidental private data, risky binaries,
and unreviewed third-party material from entering public figure repositories.
When a provenance warning appears, maintainers should verify permission or
replace the material with clean-room code or generated data.

## Privacy Rules

Privacy rules are enabled by default and report errors. Matches are redacted in
terminal output, Markdown reports, and JSON results.

Default privacy checks include:

- email-like strings
- local absolute paths
- sensitive personal-information keywords

## Provenance Rules

Provenance rules are warnings by default. They do not fail CI unless a project
chooses to make them errors in `mfigci.yml`.

Default provenance checks include source markers, third-party license markers,
and platform traces.

## Extension Rules

Default errors:

- `.p`
- `.mat`
- `.fig`
- `.doc`
- `.docx`
- `.xlsx`
- `.vsd`

Default warnings:

- `.pdf`
- `.mlx`
- `.zip`

PDF is a warning, not an error, because scientific figure repositories often
export legitimate vector PDFs.
