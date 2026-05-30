# Roadmap

`matlab-figure-ci` is intentionally small in v0.1.0. The next releases should
make the tool easier to adopt without turning it into a large platform.

## v0.1.x

- Keep the current CLI stable: `scan`, `gallery`, `check`, `report`, `init`, and
  optional `render`.
- Improve docs based on dogfooding feedback from
  `matlab-scientific-figures`.
- Fix scanner or report bugs before adding broad new behavior.

## v0.2.x Candidates

- Publish to PyPI after the GitHub-tag install path has been tested.
- Add a stable JSON report output interface.
- Add rule presets for common MATLAB figure repository layouts.
- Add a PR-comment-ready Markdown report template without building a bot.
- Expand MATLAB render and gallery manifest examples.

## Later Ideas

- Add optional JSON schema documentation.
- Add self-hosted MATLAB runner examples.
- Explore a composite GitHub Action only after the CLI interface is stable.

## Non-Goals For Early Releases

- Web UI.
- Cloud service.
- PR comment bot.
- GitHub Marketplace action.
- Complex plugin system.
- Artificial usage, stars, or download claims.
