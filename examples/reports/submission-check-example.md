# Submission Check Example Report

This is a readable example of how `mfigci` can support a publication-figure
review workflow. It uses synthetic paths, synthetic figure names, and generic
project metadata so the report can be shared publicly.

Use this as a reporting pattern, not as a claim that a paper, experiment, or
submission is scientifically correct.

## Review Scope

| Item | Example value |
|---|---|
| Project | `synthetic-power-figures` |
| Commit | `abc1234` |
| Config | `mfigci.yml` |
| Command | `mfigci check --config mfigci.yml --report mfigci-report.md` |
| Figures reviewed | `figures/voltage-response.svg`, `figures/harmonic-spectrum.png`, `figures/load-forecast.pdf` |
| Data boundary | Synthetic CSV and generated demo signals only |
| MATLAB render | Disabled on the public runner |

## Summary

| Area | Status | What it means |
|---|---|---|
| File hygiene | Pass | No risky public source files were detected under the configured scan paths. |
| Privacy scan | Pass | No email-like strings, local absolute paths, or phone-like identifiers were found. |
| Provenance scan | Review | One copied-source marker would need maintainer review before release. |
| Gallery outputs | Pass | Expected PNG/SVG/PDF outputs exist and are non-empty. |
| Export readiness | Review | One raster figure should be regenerated at higher resolution before submission. |
| MATLAB render | Skipped | Public CI did not run MATLAB; local render evidence should be attached separately when needed. |

## Detailed Findings

### Presentation Checks

| Check | Figure | Result | Suggested action |
|---|---|---|---|
| Font size | `figures/voltage-response.svg` | Pass | Keep labels between 8 and 10 pt for single-column layout. |
| Line width | `figures/voltage-response.svg` | Pass | Current line width is suitable for print preview. |
| Figure dimensions | `figures/load-forecast.pdf` | Review | Confirm single-column or double-column target before final export. |
| Export format | `figures/harmonic-spectrum.png` | Review | Regenerate at 600 dpi or export SVG/PDF if the plot does not rely on dense raster data. |
| Legend and units | `figures/load-forecast.pdf` | Pass | Axes include units and legend labels are short enough for print. |

### Repository Hygiene Checks

| Check | Result | Evidence |
|---|---|---|
| Local/private paths | Pass | Scanner reported no privacy findings. |
| Source boundary | Review | A provenance warning was raised for a copied-source marker in `docs/method-note.md`. |
| Risky extensions | Pass | No `.fig`, `.mat`, `.p`, Office files, or archives were detected under public source paths. |
| Generated assets in source tree | Pass | Gallery assets stayed under configured gallery paths. |
| Release readiness | Review | Keep `mfigci-report.md` and `.mfigci-results.json` as CI artifacts unless the repository intentionally versions review reports. |

## Maintainer Notes

- The provenance warning should be reviewed by a maintainer before public
  release. If the note refers to external code or a third-party chart, either
  replace it with a clean-room explanation or add compatible attribution.
- The raster export warning is a presentation issue, not a scientific issue.
  Re-exporting the figure does not change the underlying data.
- If MATLAB rendering matters, attach a local or self-hosted runner log with the
  MATLAB version, operating system, command, and generated artifact names.

## Boundary Statement

This report checks presentation, packaging, privacy, provenance, gallery, and
release-readiness signals that `mfigci` can observe. It does not verify scientific validity,
experimental design, statistical correctness, manuscript quality, journal acceptance,
competition results, or whether every external asset is legally reusable.

For paid figure-QA or consulting workflows, share the report as a practical
checklist and keep the same boundary: improve figure hygiene and reproducibility
without changing data, writing papers, or promising review outcomes.
