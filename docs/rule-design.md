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

Use `mfigci rules --config mfigci.yml` to inspect the effective rules before
running a scan. The command prints rule ids, severities, and extension policies,
but it does not print regex patterns or scan file contents.

## Presets

Presets are named bundles of conservative defaults. They reduce configuration
boilerplate without adding personal, project-specific, or historical keywords to
the global defaults.

Enable presets in `mfigci.yml`:

```yaml
presets:
  - matlab-figures
```

### `matlab-figures`

The `matlab-figures` preset is designed for repositories that commit a rendered
figure gallery.

It does:

- keep MATLAB render disabled by default
- keep `.pdf` in the global warning list
- allow `.pdf` files under `gallery/` without an extension warning
- keep `.png`, `.svg`, and `.pdf` as allowed gallery formats

It does not:

- allow `.fig`, `.mat`, or `.p` files
- allow PDFs outside `gallery/`
- add personal names, social platforms beyond the default provenance rules, or
  project-specific historical keywords

Example:

```yaml
presets:
  - matlab-figures

gallery:
  path: "gallery"
  expected:
    - "line_plot.png"
    - "line_plot.svg"
    - "line_plot.pdf"
```

With this preset, `gallery/line_plot.pdf` is accepted as a gallery output, but
`docs/paper.pdf` still receives a warning.
