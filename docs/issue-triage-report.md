# Issue Triage Report

`mfigci` can format a compact triage note from `.mfigci-results.json`. The note
is meant for a maintainer who is looking at an issue, pull request, or release
candidate and wants the policy state in one small block.

This is not a bot, GitHub App, or automatic reviewer. It does not post comments
by itself, decide whether a contribution is acceptable, or prove that a file is
licensed. It only reformats the same checked results that already exist in the
full Markdown and JSON reports.

Unreleased on main after v2.5.0: this report style is available from a source
checkout on `main` until the next release tag includes it. The current `v2.5.0`
GitHub tag does not include this style.

Run the checks first:

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

Then generate the triage note:

```bash
mfigci report --style triage --output mfigci-triage.md
```

Do not commit `mfigci-triage.md` by default. Keep it as a local review note or
copy the relevant part into a public issue or pull request after checking that
privacy findings stay redacted.

The output includes:

- status: `blocked`, `needs maintainer review`, or `ready`;
- summary counts for errors, warnings, files scanned, gallery checks, and
  MATLAB render status;
- Suggested triage labels such as `privacy`, `provenance`, `gallery`, or
  `risky-files`;
- top blocking findings;
- warnings that need maintainer review;
- next maintainer action.

Use this report when an issue or pull request needs a short decision trail:

- policy errors block merge or release until fixed;
- provenance warnings ask for source and permission review;
- gallery warnings ask for output or manifest review;
- render errors ask for MATLAB-specific reproduction;
- clean reports can still need human review when the change affects public API,
  templates, examples, or release notes.

The triage note is deliberately smaller than the full report. Keep
`mfigci-report.md` and `.mfigci-results.json` as the durable artifacts when a
release decision, public application note, or later debugging step needs more
evidence.
