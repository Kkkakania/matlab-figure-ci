# PyPI 发布检查清单

[English](pypi-release-checklist.md) | 简体中文

`matlab-figure-ci` 当前尚未发布到 PyPI。本页用于记录未来发布 PyPI 前必须完成的检查，让发布动作保持审慎、可复现、可审计。

这不是发布说明，也不是要求马上上传包。当前稳定安装路径仍然是 GitHub release tag。

## 当前状态

- 公开 release tag 安装仍然是当前支持路径。
- 每个 GitHub release 应先被 `matlab-scientific-figures` dogfood，再考虑是否推进 PyPI。
- 2026-07-01，`https://pypi.org/pypi/matlab-figure-ci/json` 返回 `404`，表示该名称在当时未出现在 PyPI。
- PyPI 名称状态是外部状态，随时可能变化。历史检查只能作为当时快照，不能替代发布前最后一次检查。
- `Package` workflow 只负责构建、检查、smoke install 和上传 artifact；它不应该自动上传到 PyPI。

## 发布前必须确认

1. 仓库是公开仓库。
2. 目标 release commit 的 GitHub Actions 已通过。
3. `pyproject.toml` 的包名、版本、描述、license、入口点和依赖仍然正确。
4. `CHANGELOG.md` 有对应版本的日期记录。
5. 发布前重新检查 PyPI 名称状态。
6. 仓库中没有 PyPI token 或其他发布凭据。
7. `Package` workflow 为目标 commit 上传了 `release-preflight.json` 和 `pypi-name-check.json`。
8. `Package` workflow 仍然只做构建、检查、安装验证和 artifact 上传，不包含自动发布步骤、trusted publishing 权限或 token 变量。
9. GitHub tag 安装路径继续保留为 fallback。

## 本地 preflight

先运行不发布的 release preflight：

```bash
mfigci release-preflight
mfigci release-preflight --format json
mfigci release-preflight --output release-preflight.json
```

这些命令检查 release 文件、`pyproject.toml` 元数据、`CHANGELOG.md` 版本记录、console script 入口和 package workflow。默认不会查询 PyPI，也不会发布任何内容。

构建完成后，再要求 dist 输出存在：

```bash
mfigci release-preflight --require-dist
mfigci release-preflight --require-dist --output release-preflight.json
```

`release-preflight.json` 更适合作为 CI artifact 保存，不建议默认提交到仓库。

## PyPI 名称快照

发布前立即运行名称检查：

```bash
python scripts/check_pypi_name.py matlab-figure-ci --json-out pypi-name-check.json
```

结果含义：

- exit code `0`：PyPI 当前返回未占用状态。
- exit code `1`：PyPI 当前已有该项目名，不能继续按这个名称发布。
- exit code `2`：检查失败或网络状态不确定，需要重试或人工确认。

`pypi-name-check.json` 记录名称、状态、说明和 exit code。它只是当时快照；真正上传前仍要重新运行。

## 本地构建和安装验证

从干净 checkout 构建：

```bash
python -m pip install -e ".[build]"
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*
mfigci release-preflight --require-dist
```

在干净虚拟环境里安装 wheel：

```bash
python -m venv /tmp/mfigci-wheel-test
/tmp/mfigci-wheel-test/bin/python -m pip install dist/*.whl
/tmp/mfigci-wheel-test/bin/mfigci --version
/tmp/mfigci-wheel-test/bin/mfigci --help
```

只有当这些检查都通过，并且维护者明确决定发布，才进入手动上传阶段。

## 发布后验证

发布后必须用新的干净环境验证 PyPI 安装：

```bash
python -m venv /tmp/mfigci-pypi-test
/tmp/mfigci-pypi-test/bin/python -m pip install matlab-figure-ci
/tmp/mfigci-pypi-test/bin/mfigci --version
/tmp/mfigci-pypi-test/bin/mfigci --help
```

完成后再更新公开文档，把 PyPI 安装路径和 GitHub tag fallback 的关系写清楚。

## 不要做的事

- 不要为了关闭 issue 而发布 PyPI。
- 不要在 package workflow 里加入自动上传步骤。
- 不要把 PyPI token、trusted publishing 权限或发布凭据写进普通 CI。
- 不要把历史名称检查当作当前事实。
- 不要声称 PyPI 发布代表外部采用、下载量或任何项目申请一定通过。

这个清单的价值是让未来发布决定有证据，而不是催促发布。
