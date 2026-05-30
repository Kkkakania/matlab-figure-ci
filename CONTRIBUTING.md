# Contributing

Thank you for helping improve `matlab-figure-ci`.

## Development

```bash
python -m pip install -e ".[test]"
pytest
mfigci --help
```

## Issues

Use the bug report template for reproducible CLI problems and include the
smallest relevant `mfigci.yml` snippet. Redact private paths, emails, local
usernames, tokens, unpublished project names, and sensitive scan output before
posting.

Use the feature request template for focused maintainer workflow improvements.
Keep requests tied to a command, configuration field, report output, or
documented workflow.

## Pull Requests

- Keep v0.1.x changes small and testable.
- Add or update tests for scanner, gallery, report, or CLI behavior.
- Do not add private datasets, unclear third-party assets, or generated binary
  artifacts to the repository.
- Keep MATLAB rendering optional.

## Rule Changes

Rules should be conservative and explainable. Provenance markers should remain
warnings unless there is a clear policy reason to make them errors.
