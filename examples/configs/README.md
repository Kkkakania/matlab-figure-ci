# mfigci Config Examples

These examples are starting points for MATLAB scientific figure repositories.
Copy one to `mfigci.yml`, then replace gallery filenames with real outputs from
your project.

## Files

- `minimal-static-scan.yml`: privacy, provenance, extension, and report checks
  without a gallery manifest.
- `png-svg-gallery.yml`: committed PNG/SVG gallery outputs.
- `png-svg-pdf-gallery.yml`: committed PNG/SVG/PDF gallery outputs using the
  `matlab-figures` preset.
- `strict-release-gate.yml`: warning-strict release gate for repositories that
  want provenance warnings to fail CI.

All examples keep MATLAB rendering disabled. Enable `matlab.enabled` only on
runners where MATLAB is installed.
