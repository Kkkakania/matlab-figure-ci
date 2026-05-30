# MATLAB CI Guide

MATLAB rendering is optional in `matlab-figure-ci`.

Public GitHub-hosted runners usually do not include MATLAB, so v0.1.0 keeps
`matlab.enabled: false` by default. The static checks still work without MATLAB:
privacy scanning, provenance warnings, risky extension checks, gallery checks,
and report generation.

## Local Rendering

Set `MATLAB_BIN` when MATLAB is not on `PATH`:

```bash
MATLAB_BIN=/Applications/MATLAB_R2025a.app/bin/matlab mfigci render --config mfigci.yml
```

The command uses MATLAB batch mode:

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

## Failure Checklist

- Confirm MATLAB is installed.
- Confirm `MATLAB_BIN` points to the executable, not the app bundle.
- Confirm the batch command exists on the MATLAB path.
- Keep render disabled in public CI unless the runner has MATLAB available.
