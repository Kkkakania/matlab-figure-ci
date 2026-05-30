# MATLAB CI Guide

MATLAB rendering is optional in `matlab-figure-ci`.

Public GitHub-hosted runners usually do not include MATLAB, so `mfigci` keeps
`matlab.enabled: false` by default. The static checks still work without MATLAB:
privacy scanning, provenance warnings, risky extension checks, gallery checks,
and report generation.

## Local Rendering

Use `MATLAB_BIN` when MATLAB is installed but not on `PATH`. On macOS, point to
the executable inside the app bundle:

```bash
MATLAB_BIN=/Applications/MATLAB_R2025a.app/bin/matlab \
  mfigci render --config mfigci.yml
```

When `matlab` is already on `PATH`, no environment variable is needed:

```bash
mfigci render --config mfigci.yml
```

`mfigci render` uses MATLAB batch mode and does not invoke a shell:

```bash
matlab -batch "run_all_figures"
```

The batch command is configured in `mfigci.yml`:

```yaml
matlab:
  enabled: true
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "run_all_figures"
```

For a repository with `src/` and `examples/`, use a batch command that prepares
the MATLAB path before rendering:

```yaml
matlab:
  enabled: true
  batch_command: "addpath(genpath('src')); addpath(genpath('examples')); runAllExamples('gallery')"
```

## CI Rendering

Keep render disabled on ordinary public GitHub runners:

```yaml
matlab:
  enabled: false
```

Enable render only on a runner that has MATLAB installed, such as a self-hosted
runner or a CI environment prepared by your organization:

```yaml
matlab:
  enabled: true
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "addpath(genpath('src')); addpath(genpath('examples')); runAllExamples('gallery')"
```

Example self-hosted workflow step:

```yaml
- name: Render and check figures
  env:
    MATLAB_BIN: /Applications/MATLAB_R2025a.app/bin/matlab
  run: mfigci check --config mfigci.yml --report mfigci-report.md
```

## Gallery Manifests

The `gallery.expected` list is a manifest of files that must exist after
rendering or after checking in committed gallery outputs. Use real output names,
not placeholder names.

Copyable `mfigci.yml` examples are available in `examples/configs/`:

- `minimal-static-scan.yml`
- `png-svg-gallery.yml`
- `png-svg-pdf-gallery.yml`
- `strict-release-gate.yml`

PNG and SVG example:

```yaml
gallery:
  path: "gallery"
  allowed_extensions:
    - ".png"
    - ".svg"
  min_size_bytes: 1024
  expected:
    - "line_plot.png"
    - "line_plot.svg"
    - "heatmap.png"
    - "heatmap.svg"
```

PNG, SVG, and PDF example:

```yaml
gallery:
  path: "gallery"
  allowed_extensions:
    - ".png"
    - ".svg"
    - ".pdf"
  min_size_bytes: 1024
  expected:
    - "line_plot.png"
    - "line_plot.svg"
    - "line_plot.pdf"
    - "surface_3d.png"
    - "surface_3d.svg"
    - "surface_3d.pdf"
```

PDF files are allowed in gallery manifests when explicitly listed and permitted
by `allowed_extensions`. Outside gallery usage, PDFs remain a warning by default
because they can be valid figure exports or unreviewed document artifacts.

## Failure Checklist

- Confirm MATLAB is installed.
- Confirm `MATLAB_BIN` points to the executable, not the app bundle.
- Confirm the batch command exists on the MATLAB path.
- Confirm the gallery manifest lists files your render command actually writes.
- Keep render disabled in public CI unless the runner has MATLAB available.
