---
name: Adoption report
about: Share results from trying matlab-figure-ci in another figure repository
title: "[Adoption]: "
labels: question, help wanted
assignees: ""
---

## Repository Context

- Repository type: MATLAB figures / mixed MATLAB project / other
- Public or private:
- MATLAB render enabled in CI: yes/no
- `matlab-figure-ci` version or tag:

## Configuration Used

Paste the smallest relevant `mfigci.yml` snippet. Redact private paths, emails,
tokens, unpublished project names, and private data names.

```yaml

```

## Commands Run

```bash
mfigci rules --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
```

## Result

```text
Errors:
Warnings:
Gallery files checked:
Binary/skipped files:
```

## Privacy Check

- [ ] I did not include private paths, private datasets, credentials, or
      unpublished project names.
- [ ] I redacted emails, tokens, local usernames, and organization-specific
      identifiers from config snippets and output.

## What Worked

Which scanner, gallery, report, init, or docs behavior was immediately useful?

## What Was Awkward

What part of setup, output, defaults, documentation, or CI integration slowed
you down?

## Follow-Up Suggestion

Describe one small change that would make adoption easier for another
maintainer.
