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
- local absolute paths, including common macOS, Linux, Windows, WSL,
  Codespaces, and external-volume development paths
- sensitive personal-information keywords

## Provenance Rules

Provenance rules are warnings by default. They do not fail CI unless a project
chooses to make them errors in `mfigci.yml`.

Default provenance checks include source markers, third-party license markers,
and platform traces.

Projects that want strict release gates can keep provenance rules as warnings
for local developer feedback and run `mfigci scan --fail-on-warnings` or
`mfigci check --fail-on-warnings` in CI. The same behavior can be versioned in
`mfigci.yml`:

```yaml
strict:
  fail_on_warnings: true
```

This preserves the default v2 behavior while allowing a repository to opt into
stricter policy enforcement.

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

## Config Validation

`mfigci` validates the policy shape before scanning files. Invalid severities
such as `critical`, non-boolean strict settings, or extension entries that do not
start with `.` return exit code 2 with a configuration error. This keeps CI
failures focused on the mistake in `mfigci.yml` instead of producing confusing
scan output.

## Scan Include And Exclude Rules

`scan.include` and `scan.exclude` are repository-relative path lists. Exclude
entries may be exact names, path prefixes, or simple shell-style globs such as
`.venv*`.

Use excludes for generated local environments, build output, cache directories,
and reviewed repository-maintenance exceptions. Examples include `.git`,
`.venv`, `.venv*`, `dist`, `build`, `.pytest_cache`, and
`.ipynb_checkpoints`.

Do not use broad excludes to hide raw source packs, copied third-party files,
or risky MATLAB binaries from CI. If a directory contains material that should
not be published, remove it from the repository or keep it outside the public
tree instead of masking it with `scan.exclude`.

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
