# matlab-figure-ci

[![CI](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml)
[![Package](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/package.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/package.yml)
[![Release](https://img.shields.io/github/v/release/Kkkakania/matlab-figure-ci)](https://github.com/Kkkakania/matlab-figure-ci/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

语言： [English](README.md) | 简体中文

`matlab-figure-ci` 是给 MATLAB 科研绘图仓库用的质量检查工具。它不负责画图，而是帮维护者在提交、合并或发布前检查这些常见问题：示例图有没有丢，图片文件是不是空的，仓库里有没有 `.fig`、`.mat`、`.p` 这类不适合直接公开的文件，文档和代码里有没有本地路径、邮箱、来源不明的作者或平台痕迹。

这个工具适合已经有 MATLAB 绘图代码、示例 gallery 或科研图表模板的仓库。对于刚开始整理图表模板的人，它也可以作为一个保守的公开发布检查清单。

## 它解决什么问题

科研绘图仓库容易出现几类发布风险。代码本身能运行，但 gallery 图没有重新生成；示例图存在，但尺寸为 0 或格式不在预期范围；历史素材里混进 `.fig`、`.mat`、Office 文档、压缩包或 PDF；文档里残留本机路径、邮箱或个人环境信息；复制来的片段保留了作者、版权、许可证或平台来源线索。

`matlab-figure-ci` 把这些检查做成 CLI 和 GitHub Actions 可以调用的质量门。它的默认策略偏保守，隐私问题默认是 error，来源问题默认是 warning，MATLAB 渲染默认关闭。

## 和其他仓库的关系

这个仓库是 MATLAB 绘图开源生态里的检查层：

- [`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures) 提供 clean-room 科研图表模板和 gallery。
- `matlab-figure-ci` 检查图表仓库的 gallery、隐私、来源、危险文件和 release 准备状态。
- [`matlab-plotting-skill`](https://github.com/Kkkakania/matlab-plotting-skill) 把 MATLAB 绘图流程接到 agent/Codex 风格的数据到图表任务。

目前 `matlab-scientific-figures` 已经在 CI 中 dogfood 这个工具。它会从 release tag 安装 `matlab-figure-ci`，然后运行：

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

这说明工具在一个真实公开仓库里持续使用，但这不是下载量、外部采用量或申请项目通过率的证明。

## 当前版本

当前公开 release 是 `v2.4.5`。推荐安装方式仍然是 GitHub release tag：

```bash
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.4.5
```

项目还没有发布到 PyPI。`v2` 系列的 CLI 命令、配置键、退出码和报告字段边界记录在 [v2 compatibility](docs/v2-compatibility.md)。

如果系统 Python 提示 externally managed Python，不建议强行安装到系统环境。使用虚拟环境更稳妥：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.4.5
```

## 最小接入流程

先在临时分支或测试仓库中生成配置：

```bash
mfigci init
```

查看实际生效的配置和规则：

```bash
mfigci doctor --config mfigci.yml
mfigci rules --config mfigci.yml
```

运行完整检查：

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

`check` 会生成两个文件：

```text
mfigci-report.md
.mfigci-results.json
```

这两个文件通常适合作为 CI artifact。除非你确认报告本身应该被版本管理，否则不要直接提交到仓库。

## 常用命令

| 命令 | 用途 |
|---|---|
| `mfigci scan` | 扫描隐私痕迹、来源风险和危险文件扩展名 |
| `mfigci gallery` | 检查 gallery 文件是否存在、非空，并符合允许格式 |
| `mfigci check` | 一次运行 scan、gallery、可选 render，并生成报告 |
| `mfigci report` | 从 `.mfigci-results.json` 生成 Markdown、PR comment Markdown 或 JSON |
| `mfigci init` | 生成 starter 配置和 GitHub Actions workflow |
| `mfigci render` | 可选调用 MATLAB `-batch` |
| `mfigci doctor` | 查看不会泄露隐私的配置摘要 |
| `mfigci rules` | 查看生效的隐私、来源和扩展名规则 |
| `mfigci release-preflight` | 检查打包、release 文件和 workflow 准备状态 |

默认情况下，warning 不会让 CI 失败。如果你想在 release gate 中把 warning 也当作失败，可以使用：

```bash
mfigci scan --config mfigci.yml --fail-on-warnings
mfigci check --config mfigci.yml --report mfigci-report.md --fail-on-warnings
```

`release-preflight` 只检查发布准备情况，不会发布 PyPI，也不会创建 GitHub Release：

```bash
mfigci release-preflight
mfigci release-preflight --format json
mfigci release-preflight --output release-preflight.json
mfigci release-preflight --require-dist
```

## 配置示例

`mfigci.yml` 是主要配置文件。如果没有这个文件，工具会使用安全默认值：可以运行 scan，gallery 没有默认 expected 文件，MATLAB render 关闭。

```yaml
project:
  name: matlab-scientific-figures

presets:
  - matlab-figures

scan:
  include:
    - "."
  exclude:
    - ".git"
    - ".venv"
    - ".venv*"
    - "venv"
    - "__pycache__"
    - "dist"
    - "build"
    - ".pytest_cache"
    - ".ipynb_checkpoints"
    - "LICENSE"

gallery:
  path: "gallery"
  allowed_extensions:
    - ".png"
    - ".svg"
    - ".pdf"
  min_size_bytes: 1024
  expected:
    - "example.png"

strict:
  fail_on_warnings: false

matlab:
  enabled: false
  bin_env: "MATLAB_BIN"
  fallback_bin: "matlab"
  batch_command: "run_all_figures"
```

真实项目里要把 `example.png` 换成自己的 gallery 文件名。`matlab.enabled` 默认是 `false`，因为公开 GitHub runner 通常没有 MATLAB。只有在本机或自托管 runner 已经配置好 MATLAB 时，再启用 render。

## GitHub Actions 示例

`mfigci init` 会生成一个 starter workflow。核心步骤是安装当前 release tag，展示规则，然后运行完整检查：

```yaml
name: figure-quality

on:
  push:
  pull_request:

permissions:
  contents: read

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  mfigci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - run: pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.4.5
      - run: mfigci rules --config mfigci.yml
      - run: mfigci check --config mfigci.yml --report mfigci-report.md
      - uses: actions/upload-artifact@v5
        if: always()
        with:
          name: mfigci-report
          path: mfigci-report.md
```

## 使用边界

`matlab-figure-ci` 不是版权清洗工具。它只能提醒你仓库里可能存在来源不明、授权不明、隐私残留或不适合公开发布的材料。维护者仍然需要自己判断文件是否可以公开。

项目目前没有 Web UI、云服务、PR comment bot 或 Marketplace action。MATLAB render 是可选能力，核心 scan、gallery、report 和 check 不依赖 MATLAB。

## 延伸文档

- [Documentation index](docs/README.md)
- [MATLAB CI guide](docs/matlab-ci-guide.md)
- [Adoption playbook](docs/adoption-playbook.md)
- [Dogfooding adoption report](docs/adoption-report-matlab-scientific-figures.md)
- [JSON report](docs/json-report.md)
- [PR comment report](docs/pr-comment-template.md)
- [Rule design](docs/rule-design.md)
- [v2 compatibility](docs/v2-compatibility.md)
- [OpenAI Codex maintainer workflow](docs/openai-codex-maintainer-workflow.md)
- [PyPI release checklist](docs/pypi-release-checklist.md)
- [Release artifacts](docs/release-artifacts.md)
- [Release cadence](docs/release-cadence.md)
- [Version plan](docs/version-plan.md)
- [Roadmap](ROADMAP.md)
