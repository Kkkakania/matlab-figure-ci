# Maintainer Workflow

`matlab-figure-ci` is designed to support real open-source maintenance.

Useful workflows include:

- review pull requests for missing gallery outputs
- catch risky binary files before releases
- summarize scan and gallery failures in release preparation
- triage issues into scanner rules, MATLAB render problems, and documentation
  gaps
- help maintain a clean dogfooding workflow for `matlab-scientific-figures`
- review Dependabot GitHub Actions updates as ordinary maintenance pull
  requests, not as automatic merge authority

Automation can support repetitive maintenance checks while leaving the final
decision with a maintainer:

- draft first responses for incomplete bug reports without exposing private
  findings or absolute paths
- summarize `.mfigci-results.json` into release notes or manual PR review
  comments
- compare a proposed rule change against `docs/rule-design.md` and flag places
  where the docs, examples, and tests need to move together
- triage adoption reports into documentation gaps, scanner behavior bugs,
  gallery manifest issues, and MATLAB render environment issues
- prepare changelog drafts from merged commits while avoiding adoption,
  download, or eligibility claims

Do not use automation to manufacture stars, comments, downloads, or fake users.

## Dogfooding Review Loop

Use the companion repository as the first adoption test:

1. Update `matlab-figure-ci` on a release tag.
2. Upgrade `matlab-scientific-figures` to that tag.
3. Run `mfigci check --config mfigci.yml --report mfigci-report.md`.
4. Confirm the downstream GitHub Actions workflow passes.
5. Convert any recurring warning or confusing output into a focused issue.

Dogfooding evidence should be factual: link the downstream workflow, release
tag, and issue numbers. Do not translate a passing internal workflow into
claims about broad adoption, downloads, or guaranteed external review outcomes.

## Evidence Checklist

When describing the project publicly, keep the evidence limited to facts that
can be linked or reproduced:

- public repository URL
- latest GitHub release tag
- CI and package workflow status for the relevant commit
- Dependabot GitHub Actions update PRs when workflow dependencies change
- downstream dogfooding repository and workflow link
- issue or discussion links that show real maintenance work
- local command summaries such as `pytest`, `mfigci check`, and package build
  results

Avoid metrics that are not present yet. If there are no external users,
downloads, or stars, say the project is early and dogfooded by the companion
repository instead of inventing adoption.

## Review Packet For Maintainers

For a release candidate, issue update, or public maintainer note, collect a compact
review packet:

- the release tag or commit under review;
- the `CI` and `Package` workflow run URL for that commit;
- `mfigci-report.md and .mfigci-results.json` as CI artifacts or redacted
  summaries, never copied raw findings;
- the `mfigci release-preflight --require-dist --output release-preflight.json`
  artifact when packaging readiness matters;
- the downstream `matlab-scientific-figures` dogfooding workflow result when a
  rule or report change affects figure repositories;
- a redacted issue or PR link that shows what motivated the change;
- the command output summary, never raw private paths or unredacted findings.

This packet is evidence for maintainership and repeatability. It is not proof of broad adoption.
It is also not proof of download volume or eligibility for any external program.
