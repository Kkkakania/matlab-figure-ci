# Release Artifacts

`mfigci release-preflight` can write a structured JSON payload that is useful
as a release-candidate artifact. The artifact is a review aid, not a publishing
step and not proof that a package was uploaded to PyPI.

## When To Use It

Use the artifact when a maintainer wants a durable record that a commit passed
the packaging preflight checks:

```bash
python -m build
python -m twine check dist/*
mfigci release-preflight --require-dist --output release-preflight.json
```

The package workflow runs the same preflight command and uploads the file as a
GitHub Actions artifact named `release-preflight`. The workflow also adds
`--check-pypi-name`, so the artifact includes a `pypi-name` item from the PyPI
JSON API while still avoiding any publish step.

## What To Inspect

The JSON payload contains:

- `projectName`
- `projectVersion`
- `summary.checks`
- `summary.errors`
- `summary.warnings`
- `exitCode`
- per-check `items`

For a release candidate, inspect the artifact before tagging or publishing:

1. Confirm `summary.errors` is `0`.
2. Confirm `projectName` and `projectVersion` match the intended package.
3. Review any warnings instead of treating them as decoration.
4. Confirm the workflow commit matches the intended release candidate.
5. Confirm `dist/*.whl` and `dist/*.tar.gz` were required by the preflight run.
6. Recheck the PyPI project name immediately before any future publish step.

## What It Does Not Do

- It does not publish to PyPI.
- It does not create a GitHub release.
- It does not prove installability from PyPI before the package exists there.
- It does not replace the checklist in
  [`pypi-release-checklist.md`](pypi-release-checklist.md).

## Maintainer Comment Template

When documenting progress in an issue, keep the update short:

```text
Release preflight artifact is available for <commit>.

- Command: mfigci release-preflight --require-dist --output release-preflight.json
- Result: 0 errors, <n> warnings, <n> checks
- Artifact: release-preflight
- Status: no PyPI publish yet
```
