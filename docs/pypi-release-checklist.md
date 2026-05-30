# PyPI Release Checklist

`matlab-figure-ci` is not published to PyPI yet. This checklist defines the
gate for a future PyPI release so publishing is deliberate and reproducible.

## Current Status

- GitHub tag installation is the supported installation path.
- `v0.2.0` has been released and dogfooded by `matlab-scientific-figures`.
- On 2026-05-30, `https://pypi.org/pypi/matlab-figure-ci/json` returned `404`,
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

## Local Build

Build from a clean checkout:

```bash
python -m pip install -e ".[build]"
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*
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
