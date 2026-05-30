# matlab-figure-ci

[![CI](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Kkkakania/matlab-figure-ci)](https://github.com/Kkkakania/matlab-figure-ci/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

`matlab-figure-ci` is a small CI/CLI quality gate for MATLAB scientific figure
repositories. It helps maintainers catch missing gallery outputs, risky binary
files, privacy traces, unclear provenance markers, and optional MATLAB batch
rendering failures before a public release.

It is designed to pair with
[`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures):

- `matlab-scientific-figures` generates publication-ready MATLAB figures.
- `matlab-figure-ci` checks that figure repositories stay clean, reproducible,
  and safe to publish.

## Quick Start

Install from the GitHub release tag:

```bash
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v0.1.0
```

Create a starter configuration and GitHub Actions workflow:

```bash
mfigci init
```

Run the quality gate:

```bash
mfigci scan --config mfigci.yml
mfigci gallery --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
mfigci report --input .mfigci-results.json --output mfigci-report.md
```

`mfigci check` writes both a Markdown report and machine-readable JSON:

```text
mfigci-report.md
.mfigci-results.json
```

## Configuration

`mfigci` reads `mfigci.yml` by default. If it is missing, safe defaults are used:
scan can run, gallery has no expected files, and MATLAB rendering is disabled.

```yaml
project:
  name: matlab-scientific-figures

scan:
  include:
    - "."
  exclude:
    - ".git"
    - ".venv"
    - "venv"
    - "__pycache__"
    - "dist"
    - "build"
    - ".pytest_cache"

gallery:
  path: "gallery"
  allowed_extensions:
    - ".png"
    - ".svg"
    - ".pdf"
  min_size_bytes: 1024
  expected:
    - "example.png"

matlab:
  enabled: false
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "run_all_figures"
```

## Commands

| Command | Purpose |
|---|---|
| `mfigci scan` | Scan privacy, provenance, and risky file extensions |
| `mfigci gallery` | Check expected gallery files exist, are non-empty, and use allowed formats |
| `mfigci check` | Run scan, gallery, optional render, and write reports |
| `mfigci report` | Build Markdown from `.mfigci-results.json` |
| `mfigci init` | Generate starter config and GitHub Actions workflow |
| `mfigci render` | Optionally run MATLAB with `-batch` |

## GitHub Actions

`mfigci init` writes a starter workflow:

```yaml
name: figure-quality

on:
  push:
  pull_request:

jobs:
  mfigci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v0.1.0
      - run: mfigci check --config mfigci.yml --report mfigci-report.md
```

## Current Limits

- No PyPI release in v0.1.0.
- No web UI, cloud service, PR comment bot, or Marketplace action.
- MATLAB rendering is optional because public GitHub runners normally do not
  include MATLAB.
- Provenance rules are warnings by default. They are prompts for maintainer
  review, not a copyright-cleaning mechanism.

## Documentation

- [MATLAB CI guide](docs/matlab-ci-guide.md)
- [Rule design](docs/rule-design.md)
- [OpenAI Codex maintainer workflow](docs/openai-codex-maintainer-workflow.md)
- [Roadmap](ROADMAP.md)
