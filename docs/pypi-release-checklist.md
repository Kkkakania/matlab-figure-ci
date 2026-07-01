# PyPI Release Checklist

[简体中文](pypi-release-checklist.zh-CN.md)

`matlab-figure-ci` is not published to PyPI yet. This checklist defines the
gate for a future PyPI release so publishing is deliberate and reproducible.

## Current Status

- GitHub tag installation is the supported installation path.
- Each GitHub release should be dogfooded by `matlab-scientific-figures`
  before any future PyPI publishing step.
- On 2026-07-01, `https://pypi.org/pypi/matlab-figure-ci/json` returned `404`,
  which means the package name was not present on PyPI at that time.

Recheck name availability immediately before publishing, because PyPI state can
change.

## Preflight

1. Confirm the repository is public.
2. Confirm the latest GitHub release CI passed.
3. Confirm `pyproject.toml` metadata is current.
4. Confirm `CHANGELOG.md` has a dated entry for the release.
5. Confirm the package name is still available on PyPI.
6. Confirm no PyPI token is committed to the repository.
7. Confirm the Package workflow uploaded `release-preflight.json` and
   `pypi-name-check.json` for the release candidate commit. The preflight
   artifact should include the `pypi-name` check, and the standalone name-check
   artifact remains a time-sensitive snapshot.
8. Confirm the Package workflow still builds, checks, smoke-installs, and
   uploads a preflight artifact only. It must not contain `twine upload`,
   `pypa/gh-action-pypi-publish`, `id-token: write`, or PyPI token variables.

Run the local release preflight before building:

```bash
mfigci release-preflight
mfigci release-preflight --format json
mfigci release-preflight --output release-preflight.json
mfigci release-preflight --check-pypi-name --output release-preflight.json
```

This checks required release files, `pyproject.toml` metadata, the matching
`CHANGELOG.md` entry, the console script entry point, and the package workflow.
It does not publish anything and does not query PyPI by default. Use the JSON
format in release workflows that need machine-readable `summary`, `exitCode`,
and per-check `items`. Use `--output release-preflight.json` when the normal
text log should stay readable but CI also needs a JSON artifact.
The preflight also verifies that the package workflow does not publish to PyPI;
publishing remains a deliberate manual step until the project intentionally
changes that policy.

Use the helper script immediately before publishing:

```bash
python scripts/check_pypi_name.py matlab-figure-ci --json-out pypi-name-check.json
```

The helper exits `0` when PyPI returns `404`, `1` when the project already
exists, and `2` when the availability check could not be completed.
The JSON file records the checked name, status, detail URL/message, and exit
code so the Package workflow can upload it as a release-candidate artifact.
Because PyPI state is external and time-sensitive, treat this artifact as a
snapshot; re-run the helper immediately before an actual upload.

## Local Build

Build from a clean checkout:

```bash
python -m pip install -e ".[build]"
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*
mfigci release-preflight --require-dist
mfigci release-preflight --require-dist --output release-preflight.json
```

Smoke test the wheel in a fresh environment:

```bash
python -m venv /tmp/mfigci-wheel-test
/tmp/mfigci-wheel-test/bin/python -m pip install dist/*.whl
/tmp/mfigci-wheel-test/bin/mfigci --version
/tmp/mfigci-wheel-test/bin/mfigci --help
```

## Publish

Publish only after the preflight and local build pass:

```bash
python -m twine upload dist/*
```

After publishing:

```bash
python -m venv /tmp/mfigci-pypi-test
/tmp/mfigci-pypi-test/bin/python -m pip install matlab-figure-ci
/tmp/mfigci-pypi-test/bin/mfigci --version
```

Keep the GitHub tag installation documented as a fallback.
