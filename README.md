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

## Dogfooding Status

This tool is dogfooded by
[`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures),
the companion MATLAB gallery repository. Its workflow installs
`matlab-figure-ci` from a release tag and runs:

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

The downstream configuration checks gallery PNG/SVG outputs, privacy and
provenance traces, risky file extensions, and the `matlab-figures` preset. This
is a maintenance signal, not a usage metric: it shows the CLI is exercised by a
real public repository without claiming external adoption or downloads.

## Quick Start

Install from the GitHub release tag:

```bash
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.4.3
```

Create a starter configuration and GitHub Actions workflow:

```bash
mfigci init
```

Run the quality gate:

```bash
mfigci scan --config mfigci.yml
mfigci scan --config mfigci.yml --fail-on-warnings
mfigci gallery --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
mfigci check --config mfigci.yml --report mfigci-report.md --fail-on-warnings
mfigci report --input .mfigci-results.json --output mfigci-report.md
mfigci report --style pr-comment --output mfigci-pr-comment.md
mfigci report --format json --output mfigci-report.json
mfigci doctor --config mfigci.yml
mfigci rules --config mfigci.yml
```

`mfigci check` writes both a Markdown report and machine-readable JSON:

```text
mfigci-report.md
.mfigci-results.json
```

## Configuration

`mfigci` reads `mfigci.yml` by default. If it is missing, safe defaults are used:
scan can run, gallery has no expected files, and MATLAB rendering is disabled.
Configuration mistakes such as unknown rule severities or malformed extension
lists fail early with a clear configuration error before files are scanned.

```yaml
project:
  name: matlab-scientific-figures

presets:
  - matlab-figures

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

strict:
  fail_on_warnings: false

matlab:
  enabled: false
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "run_all_figures"
```

For real repositories, replace `example.png` with the actual gallery outputs.
The [MATLAB CI guide](docs/matlab-ci-guide.md) includes PNG/SVG/PDF manifest
examples and optional MATLAB render examples for local and self-hosted runners.
Reusable starter configs live in [examples/configs](examples/configs/).
The [adoption playbook](docs/adoption-playbook.md) shows a staged rollout from
static scans to gallery manifests, release gates, and optional MATLAB render.
If you try that rollout in another repository, use the adoption report issue
template to share what worked and what made setup harder.
The [rule design guide](docs/rule-design.md) explains the `matlab-figures`
preset, including its gallery-scoped PDF allowance.
The [JSON report guide](docs/json-report.md) defines the stable report fields,
redaction guarantees, and path guarantees. The
[v2 compatibility guide](docs/v2-compatibility.md) defines the long-term CLI,
config, policy, and report boundary.

## Commands

| Command | Purpose |
|---|---|
| `mfigci scan` | Scan privacy, provenance, and risky file extensions |
| `mfigci gallery` | Check expected gallery files exist, are non-empty, and use allowed formats |
| `mfigci check` | Run scan, gallery, optional render, and write reports |
| `mfigci report` | Build full Markdown, PR-comment Markdown, or JSON from `.mfigci-results.json` |
| `mfigci init` | Generate starter config and GitHub Actions workflow |
| `mfigci render` | Optionally run MATLAB with `-batch` |
| `mfigci doctor` | Show a privacy-safe summary of the effective configuration |
| `mfigci rules` | Inspect effective privacy, provenance, and extension rules |

By default, warnings do not fail CI. Add `--fail-on-warnings` to `scan` or
`check` when a release gate should treat warnings as policy failures.

## GitHub Actions

`mfigci init` writes a starter workflow:

```yaml
name: figure-quality

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  mfigci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - run: pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.4.3
      - run: mfigci check --config mfigci.yml --report mfigci-report.md
      - uses: actions/upload-artifact@v5
        if: always()
        with:
          name: mfigci-report
          path: mfigci-report.md
```

## Current Limits

- No PyPI release yet.
- No web UI, cloud service, PR comment bot, or Marketplace action.
- MATLAB rendering is optional because public GitHub runners normally do not
  include MATLAB.
- Provenance rules are warnings by default. They are prompts for maintainer
  review, not a copyright-cleaning mechanism.

## Documentation

- [MATLAB CI guide](docs/matlab-ci-guide.md)
- [Adoption playbook](docs/adoption-playbook.md)
- [JSON report](docs/json-report.md)
- [PR comment report](docs/pr-comment-template.md)
- [Rule design](docs/rule-design.md)
- [v2 compatibility](docs/v2-compatibility.md)
- [OpenAI Codex maintainer workflow](docs/openai-codex-maintainer-workflow.md)
- [PyPI release checklist](docs/pypi-release-checklist.md)
- [Release cadence](docs/release-cadence.md)
- [Version plan](docs/version-plan.md)
- [Roadmap](ROADMAP.md)
