# Security Policy

Please report security or privacy concerns through GitHub Issues if the report
does not contain sensitive details. If sensitive data is involved, open a brief
issue asking for a private contact path.

`matlab-figure-ci` is a local CLI tool. It does not upload source files, reports,
or scan results to external services.

GitHub Actions dependencies are monitored with Dependabot in
`.github/dependabot.yml`. Dependabot updates are reviewed as ordinary
maintenance pull requests: CI must pass, release claims stay factual, and
workflow permissions should remain narrow.
