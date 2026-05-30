# Contributing

Thank you for helping improve `matlab-figure-ci`.

## Development

```bash
python -m pip install -e ".[test]"
pytest
mfigci --help
```

## Pull Requests

- Keep v0.1.x changes small and testable.
- Add or update tests for scanner, gallery, report, or CLI behavior.
- Do not add private datasets, unclear third-party assets, or generated binary
  artifacts to the repository.
- Keep MATLAB rendering optional.

## Rule Changes

Rules should be conservative and explainable. Provenance markers should remain
warnings unless there is a clear policy reason to make them errors.
