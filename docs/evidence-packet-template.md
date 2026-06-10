# Evidence Packet Template

`mfigci` can format a small evidence packet from the same
`.mfigci-results.json` file used by `mfigci report`. The packet is meant for
maintainers who need a short review note, release note attachment, or public
application summary without pasting raw findings.

Unreleased on main after v2.5.0: this report style is available from a source
checkout on `main` until the next release tag includes it. The current `v2.5.0`
GitHub tag does not include this style.

Run the checks first:

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

Then generate the packet:

```bash
mfigci report --style evidence --output mfigci-evidence.md
```

Do not commit `mfigci-evidence.md` by default. Keep it as a local review note
or CI artifact unless the repository has a clear reason to version the filled
packet.

The output includes:

- summary counts for errors, warnings, files scanned, gallery checks, and
  MATLAB render status;
- artifact reminders for `mfigci-report.md` and `.mfigci-results.json`;
- placeholders for workflow run URL, commit, and redacted issue or PR link;
- a compact finding summary by rule;
- separate review packet and application packet notes.

Use the review packet when talking with maintainers or contributors. Use the
application packet when describing the project outside the issue queue. In both
cases, keep privacy findings redacted, use relative paths, and link public
evidence instead of copying local logs.

This is not an approval argument. It is also not a usage metric, download
claim, or adoption claim. It only records what `mfigci` checked and which public
artifact another maintainer can inspect.
