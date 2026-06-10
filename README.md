# matlab-figure-ci

[![CI](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml)
[![Package](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/package.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/package.yml)
[![Release](https://img.shields.io/github/v/release/Kkkakania/matlab-figure-ci)](https://github.com/Kkkakania/matlab-figure-ci/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Languages: English | [简体中文](README.zh-CN.md)

`matlab-figure-ci` is a small CI/CLI quality gate for MATLAB figure
repositories. I use it for the dull checks that are easy to forget before a
public release: missing gallery images, private paths, source markers, binary
artifacts, generated assets in source directories, and optional MATLAB
batch-rendering failures.

It is designed to pair with
[`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures):

- `matlab-scientific-figures` generates publication-ready MATLAB figures.
- `matlab-figure-ci` checks that figure repositories stay clean, reproducible,
  and safe to publish.

## Project Ecosystem

`matlab-figure-ci` is the quality-gate component of a small MATLAB plotting
ecosystem:

- [`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures)
  is the main clean-room gallery and template library.
- [`matlab-figure-ci`](https://github.com/Kkkakania/matlab-figure-ci) checks
  figure repositories for gallery, provenance, privacy, and release-gate drift.
- [`matlab-plotting-skill`](https://github.com/Kkkakania/matlab-plotting-skill)
  connects MATLAB plotting workflows to agent/Codex-style data-to-figure tasks.

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

See the current
[`matlab-scientific-figures` dogfooding report](docs/adoption-report-matlab-scientific-figures.md)
and
[`matlab-plotting-skill` dogfooding report](docs/adoption-report-matlab-plotting-skill.md)
for exact downstream configurations, latest check summaries, and known
boundaries. The staged [adoption playbook](docs/adoption-playbook.md) also
documents the handoff contract between gallery artifacts, agent render reports,
and `mfigci` review reports.

## Version And Distribution Status

The current public release is `v2.5.0`. The supported install path is still a
GitHub release tag install, and the package is not published on PyPI yet.

Unreleased on main after v2.5.0: `mfigci report --style evidence` can format a
small review/application evidence packet from `.mfigci-results.json`. Use it
from a source checkout until the next release tag includes it.

The `v2` line marks the v2 compatibility boundary for the CLI commands,
configuration keys, exit codes, and report fields documented in
[v2 compatibility](docs/v2-compatibility.md). Future PyPI publishing is tracked
separately from that compatibility story so users can treat the current GitHub
tag as the public release while packaging work remains deliberate.

## Quick Start

Install from the GitHub release tag:

```bash
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
```

If your Python installation reports an externally managed Python environment
error, install inside a virtual environment instead of forcing a system install:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
```

Create a starter configuration and GitHub Actions workflow:

```bash
mfigci init
mfigci doctor --config mfigci.yml
mfigci doctor --config mfigci.yml --format json
mfigci check --config mfigci.yml --report mfigci-report.md
```

Run the quality gate:

```bash
mfigci scan --config mfigci.yml
mfigci scan --config mfigci.yml --fail-on-warnings
mfigci scan --config mfigci.yml --paths src/plot.m docs/usage.md
mfigci gallery --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
mfigci check --config mfigci.yml --report mfigci-report.md --fail-on-warnings
mfigci report --input .mfigci-results.json --output mfigci-report.md
mfigci report --style pr-comment --output mfigci-pr-comment.md
mfigci report --style evidence --output mfigci-evidence.md
mfigci report --format json --output mfigci-report.json
mfigci doctor --config mfigci.yml
mfigci doctor --config mfigci.yml --format json
mfigci rules --config mfigci.yml
mfigci release-preflight
mfigci release-preflight --format json
mfigci release-preflight --output release-preflight.json
mfigci release-preflight --require-dist
```

`mfigci check` writes both a Markdown report and machine-readable JSON:

```text
mfigci-report.md
.mfigci-results.json
```

## First 5 Minutes

Use this path to try the tool without changing release policy immediately:

1. Install from the current release tag.

   ```bash
   python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
   ```

2. Create starter files in a throwaway branch or scratch repository.

   ```bash
   mfigci init
   ```

   Add report artifacts to `.gitignore` only when you want the CLI to manage
   those entries:

   ```bash
   mfigci init --gitignore
   ```

   The plain `mfigci init` command does not edit `.gitignore`.

3. Inspect the generated policy before enforcing it.

   ```bash
   mfigci doctor --config mfigci.yml
   mfigci rules --config mfigci.yml
   ```

4. Run the full check and read both reports.

   ```bash
   mfigci check --config mfigci.yml --report mfigci-report.md
   ```

Do not commit `mfigci-report.md`, `.mfigci-results.json`,
`mfigci-evidence.md`, `release-preflight.json`, or `pypi-name-check.json` until
you have reviewed whether the report belongs in your repository or should stay
as a CI artifact.

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
    - ".venv*"
    - "venv"
    - "__pycache__"
    - "dist"
    - "build"
    - ".pytest_cache"
    - ".ipynb_checkpoints"
    - "LICENSE"

generated_assets:
  enabled: true
  severity: warning
  source_dirs:
    - "src"
    - "examples"
    - "templates"
    - "skills"
    - "scripts"
  extensions:
    - ".png"
    - ".jpg"
    - ".jpeg"
    - ".bmp"
    - ".tif"
    - ".tiff"
    - ".gif"
    - ".svg"
    - ".pdf"
  allow: []

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
preset, its gallery-scoped PDF allowance, and repo-local YAML presets for
teams that want to keep lab policy outside the main `mfigci.yml`.
The [JSON report guide](docs/json-report.md) defines the stable report fields,
redaction guarantees, and path guarantees. The
[v2 compatibility guide](docs/v2-compatibility.md) defines the long-term CLI,
config, policy, and report boundary.

Repo-local presets can be listed beside stock presets:

```yaml
presets:
  - matlab-figures
  - ./presets/lab-policy.yml
```

User preset files are resolved relative to `mfigci.yml`, use the same config
shape as the main file, and cannot include nested `presets`.

## Commands

| Command | Purpose |
|---|---|
| `mfigci scan` | Scan privacy, provenance, and risky file extensions |
| `mfigci gallery` | Check expected gallery files exist, are non-empty, and use allowed formats |
| `mfigci check` | Run scan, gallery, optional render, and write reports |
| `mfigci report` | Build full Markdown, PR-comment Markdown, evidence-packet Markdown, or JSON from `.mfigci-results.json` |
| `mfigci init` | Generate starter config and GitHub Actions workflow |
| `mfigci render` | Optionally run MATLAB with `-batch` |
| `mfigci doctor` | Show a privacy-safe summary of the effective configuration |
| `mfigci rules` | Inspect effective privacy, provenance, and extension rules |
| `mfigci release-preflight` | Check package metadata, release files, and packaging workflow readiness |

`mfigci doctor` summarizes include/exclude paths, rule counts, extension policy
counts, gallery expectations, strict warning behavior, and MATLAB render status.
Use it when reviewing a new repository configuration before running a full
scan. Add `--format json` when an ecosystem workflow needs a stable,
machine-readable view of the effective configuration. Both formats warn when
configured scan includes, gallery paths, or expected gallery files do not
exist, while keeping local absolute paths out of the output.

Use `mfigci scan --paths <file...>` in pre-commit or staged-file workflows when
you want privacy, provenance, and extension checks for selected files without
running the full repository scan. The selected paths still respect configured
excludes and symlink safety checks.

By default, warnings do not fail CI. Add `--fail-on-warnings` to `scan` or
`check` when a release gate should treat warnings as policy failures.

`mfigci release-preflight` is a local packaging readiness check. It does not
publish anything. By default it checks repository files, `pyproject.toml`,
`CHANGELOG.md`, and the package workflow. Add `--require-dist` after running
`python -m build` to require `dist/*.whl` and `dist/*.tar.gz`. Add
`--check-pypi-name` only when you intentionally want the command to query the
PyPI JSON API. Add `--format json` when a release workflow needs structured
preflight items and summary counts on stdout. Add `--output
release-preflight.json` when CI should upload the structured payload as an
artifact while keeping the normal text summary in logs. The package workflow
uses that output path so release candidates have a downloadable preflight
record. See [Release artifacts](docs/release-artifacts.md) for what to inspect
before treating that payload as release evidence.

## GitHub Actions

`mfigci init` writes a starter workflow:

```yaml
name: figure-quality

on:
  push:
  pull_request:

permissions:
  contents: read

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  mfigci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - run: pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
      - run: mfigci rules --config mfigci.yml
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

- [Documentation index](docs/README.md)
- [MATLAB CI guide](docs/matlab-ci-guide.md)
- [Adoption playbook](docs/adoption-playbook.md)
- [Dogfooding adoption report](docs/adoption-report-matlab-scientific-figures.md)
- [Plotting-skill adoption report](docs/adoption-report-matlab-plotting-skill.md)
- [JSON report](docs/json-report.md)
- [PR comment report](docs/pr-comment-template.md)
- [Evidence packet template](docs/evidence-packet-template.md)
- [Rule design](docs/rule-design.md)
- [v2 compatibility](docs/v2-compatibility.md)
- [OpenAI Codex maintainer workflow](docs/openai-codex-maintainer-workflow.md)
- [PyPI release checklist](docs/pypi-release-checklist.md)
- [Release artifacts](docs/release-artifacts.md)
- [Release cadence](docs/release-cadence.md)
- [Version plan](docs/version-plan.md)
- [Roadmap](ROADMAP.md)
