# Version Plan

This project uses version numbers to mark verified behavior, not momentum.

## v0.3.0

The next adoption release should make configuration easier to inspect before a
repository enables CI. The main target is a config doctor command that can show
the effective config, enabled scanners, gallery expectations, and MATLAB render
setting without leaking private paths or scan matches.

Primary issue: #7.

## v1.0.0

The first stable release should define what downstream users can rely on:

- command names and exit codes
- `.mfigci-results.json` structure
- JSON report schema
- redaction guarantees
- relative-path guarantees
- default config behavior

Primary issue: #8.

## v2.0.0

The major release should mark an explicit compatibility boundary for policy and
report behavior. It should include migration notes from v0.x/v1.x and tests for
the public contract. A v2 release is justified only if the contract is clear and
dogfooded by at least the companion repository.

Primary issue: #9.
Compatibility notes: `docs/v2-compatibility.md`.

## What Version Numbers Do Not Mean

- They do not imply external adoption, downloads, or stars.
- They do not guarantee any benefit-program approval.
- They do not require a Web UI, cloud service, bot, or marketplace action.
- They do not replace maintainer review.
