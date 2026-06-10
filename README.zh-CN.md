# matlab-figure-ci

[![CI](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/ci.yml)
[![Package](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/package.yml/badge.svg)](https://github.com/Kkkakania/matlab-figure-ci/actions/workflows/package.yml)
[![Release](https://img.shields.io/github/v/release/Kkkakania/matlab-figure-ci)](https://github.com/Kkkakania/matlab-figure-ci/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

语言： [English](README.md) | 简体中文

`matlab-figure-ci` 是一个面向 MATLAB 科研绘图仓库的 CI/CLI 质量门工具。我主要用它处理那些发布前容易忘、但出问题会很麻烦的检查：gallery 输出缺失、本地路径、来源标记、二进制产物，以及可选 MATLAB 批量渲染失败。

它设计上和 [`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures) 配套：

- `matlab-scientific-figures` 负责生成出版级 MATLAB 科研图表。
- `matlab-figure-ci` 检查图表仓库是否保持干净、可复现，并适合公开发布。

## 项目生态

`matlab-figure-ci` 是一个小型 MATLAB 绘图生态里的质量门组件：

- [`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures) 是主要的 clean-room gallery 和模板库。
- [`matlab-figure-ci`](https://github.com/Kkkakania/matlab-figure-ci) 检查图表仓库的 gallery、来源、隐私和 release gate 漂移。
- [`matlab-plotting-skill`](https://github.com/Kkkakania/matlab-plotting-skill) 把 MATLAB 绘图工作流接到 agent/Codex 风格的数据到图表任务。

## Dogfooding 状态

这个工具已经被配套 MATLAB gallery 仓库 [`matlab-scientific-figures`](https://github.com/Kkkakania/matlab-scientific-figures) dogfood。该仓库的 workflow 会从 release tag 安装 `matlab-figure-ci`，然后运行：

```bash
mfigci check --config mfigci.yml --report mfigci-report.md
```

下游配置会检查 PNG/SVG gallery 输出、隐私和来源痕迹、风险扩展名，以及 `matlab-figures` preset。这是维护信号，含义是 CLI 正在一个真实公开仓库中被持续运行；它不是使用量指标，也不声称外部采用量或下载量。

当前的 [dogfooding adoption report](docs/adoption-report-matlab-scientific-figures.md) 记录了下游配置、最近检查摘要和已知边界。

实际维护时，我把它当作交接检查点使用：`matlab-scientific-figures` 交出 gallery 图和配置，`matlab-plotting-skill` 交出渲染报告和导出图，`matlab-figure-ci` 交出 `mfigci-report.md` 与 `.mfigci-results.json`。扫描通过不等于授权通过，也不等于材料来源可靠；它只说明当前配置能识别的风险没有触发。更完整的交接说明见 [Adoption playbook](docs/adoption-playbook.md)。

对外介绍这个工具时，最好只列可复查证据：release tag、workflow run URL、`mfigci` 报告 artifact、`release-preflight.json`、下游 dogfooding workflow，以及一个已经脱敏的 issue 或 PR 链接。不要把这些材料写成使用量或审批通过承诺。

## 版本和发布状态

当前公开 release 是 `v2.5.0`。目前支持的安装路径仍然是 GitHub release tag，项目尚未发布到 PyPI。

`v2` 系列定义了 CLI 命令、配置键、退出码和报告字段的兼容边界。相关说明见 [v2 compatibility](docs/v2-compatibility.md)。未来 PyPI 发布会单独推进，这样用户可以把当前 GitHub tag 当作公开 release 使用，同时让打包发布保持审慎节奏。

## 快速开始

从 GitHub release tag 安装：

```bash
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
```

如果你的 Python 安装提示 externally managed Python environment，不要强行写入系统环境。建议使用虚拟环境：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
```

生成 starter 配置和 GitHub Actions workflow：

```bash
mfigci init
mfigci doctor --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
```

运行质量门：

```bash
mfigci scan --config mfigci.yml
mfigci scan --config mfigci.yml --fail-on-warnings
mfigci scan --config mfigci.yml --paths src/plot.m docs/usage.md
mfigci gallery --config mfigci.yml
mfigci check --config mfigci.yml --report mfigci-report.md
mfigci check --config mfigci.yml --report mfigci-report.md --fail-on-warnings
mfigci report --input .mfigci-results.json --output mfigci-report.md
mfigci report --style pr-comment --output mfigci-pr-comment.md
mfigci report --format json --output mfigci-report.json
mfigci doctor --config mfigci.yml
mfigci rules --config mfigci.yml
mfigci release-preflight
mfigci release-preflight --format json
mfigci release-preflight --output release-preflight.json
mfigci release-preflight --require-dist
```

`mfigci check` 会同时写出 Markdown 报告和机器可读 JSON：

```text
mfigci-report.md
.mfigci-results.json
```

## 前 5 分钟

如果只是试用工具，先不要改变 release 策略。推荐用这个路径：

1. 从当前 release tag 安装。

   ```bash
   python -m pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
   ```

2. 在临时分支或 scratch 仓库中生成 starter 文件。

   ```bash
   mfigci init
   ```

   只有当你希望 CLI 管理报告产物的 ignore 条目时，才添加：

   ```bash
   mfigci init --gitignore
   ```

   普通的 `mfigci init` 不会编辑 `.gitignore`。

3. 在真正执行策略前查看生成结果。

   ```bash
   mfigci doctor --config mfigci.yml
   mfigci rules --config mfigci.yml
   ```

4. 运行完整检查，并阅读 Markdown 和 JSON 两份报告。

   ```bash
   mfigci check --config mfigci.yml --report mfigci-report.md
   ```

在确认报告是否应该进入仓库之前，不要提交 `mfigci-report.md`、`.mfigci-results.json` 或 `release-preflight.json`。这些文件通常更适合作为 CI artifact。

## 配置

`mfigci` 默认读取 `mfigci.yml`。如果配置文件不存在，会使用安全默认值：scan 可以运行，gallery 没有 expected 文件，MATLAB rendering 关闭。配置中的规则级别、扩展名列表或字段形状如果写错，会在扫描文件前给出配置错误。

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

generated_assets:
  enabled: true
  severity: warning
  source_dirs:
    - "src"
    - "examples"
    - "templates"
    - "skills"
    - "scripts"
  extensions:
    - ".png"
    - ".jpg"
    - ".jpeg"
    - ".bmp"
    - ".tif"
    - ".tiff"
    - ".gif"
    - ".svg"
    - ".pdf"
  allow: []

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

真实仓库需要把 `example.png` 换成实际 gallery 输出。 [MATLAB CI guide](docs/matlab-ci-guide.md) 包含 PNG/SVG/PDF manifest 示例，以及本机和自托管 runner 的可选 MATLAB render 示例。可复用 starter 配置位于 [examples/configs](examples/configs/)。

[Adoption playbook](docs/adoption-playbook.md) 给出从静态扫描、gallery manifest、release gate 到可选 MATLAB render 的分阶段接入方式。如果你在其他仓库中尝试这套流程，可以通过 adoption report issue template 反馈哪些步骤顺利，哪些地方增加了配置成本。

[Rule design](docs/rule-design.md) 解释 `matlab-figures` preset、gallery 范围内 PDF 的处理方式，以及如何用仓库内 YAML preset 承载实验室或小团队自己的规则。[JSON report](docs/json-report.md) 定义稳定报告字段、redaction 保证和路径保证。[v2 compatibility](docs/v2-compatibility.md) 说明长期 CLI、配置、策略和报告边界。

如果一个课题组或小团队想复用同一套规则，可以把本地 preset 和内置 preset 一起列出来：

```yaml
presets:
  - matlab-figures
  - ./presets/lab-policy.yml
```

本地 preset 路径相对于 `mfigci.yml` 解析，内容使用和主配置相同的字段形状，但不能再包含 `presets`，避免递归和合并顺序变得不透明。

## 命令

| 命令 | 用途 |
|---|---|
| `mfigci scan` | 扫描隐私、来源和风险文件扩展名 |
| `mfigci gallery` | 检查 expected gallery 文件是否存在、非空，并使用允许格式 |
| `mfigci check` | 执行 scan、gallery、可选 render，并写出报告 |
| `mfigci report` | 从 `.mfigci-results.json` 生成完整 Markdown、PR comment Markdown 或 JSON |
| `mfigci init` | 生成 starter 配置和 GitHub Actions workflow |
| `mfigci render` | 可选使用 MATLAB `-batch` 执行渲染命令 |
| `mfigci doctor` | 输出隐私安全的有效配置摘要 |
| `mfigci rules` | 查看生效的隐私、来源和扩展名规则 |
| `mfigci release-preflight` | 检查套件元数据、release 文件和打包 workflow 准备状态 |

`mfigci doctor` 会汇总 include/exclude 路径、规则数量、扩展名策略数量、gallery expected 数量、warning 严格模式和 MATLAB render 状态。审查新仓库配置时，先运行它再做完整扫描。它也会提示缺失的 scan include、gallery 路径和 expected gallery 文件，同时避免在终端输出本机绝对路径。

`mfigci scan --paths <file...>` 适合 pre-commit 或 staged-file 工作流。它只扫描指定文件，但仍然遵守配置中的 exclude 规则和 symlink 安全检查。

默认情况下，warning 不会让 CI 失败。需要在 release gate 中把 warning 当作策略失败时，对 `scan` 或 `check` 添加 `--fail-on-warnings`。

`mfigci release-preflight` 是本地打包准备检查，不会发布任何内容。默认检查仓库文件、`pyproject.toml`、`CHANGELOG.md` 和 package workflow。运行 `python -m build` 后可以添加 `--require-dist`，要求存在 wheel 和 source distribution。只有在你明确需要查询 PyPI JSON API 时，才添加 `--check-pypi-name`。需要结构化 stdout 时使用 `--format json`；需要把结构化 payload 作为 CI artifact 上传时使用 `--output release-preflight.json`。更多说明见 [Release artifacts](docs/release-artifacts.md)。

## GitHub Actions

`mfigci init` 会写入 starter workflow：

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
      - run: pip install git+https://github.com/Kkkakania/matlab-figure-ci.git@v2.5.0
      - run: mfigci rules --config mfigci.yml
      - run: mfigci check --config mfigci.yml --report mfigci-report.md
      - uses: actions/upload-artifact@v5
        if: always()
        with:
          name: mfigci-report
          path: mfigci-report.md
```

## 当前限制

- 尚未发布到 PyPI。
- 没有 Web UI、云服务、PR comment bot 或 Marketplace action。
- MATLAB rendering 是可选能力，因为公开 GitHub runner 通常不包含 MATLAB。
- 来源规则默认是 warning。它们用于提示维护者复核。`matlab-figure-ci` 不是版权清洗工具，也不能替维护者判断材料是否可以公开。
- 核心 scan、gallery、report 和 check 不依赖 MATLAB。

## 文档

- [中文文档索引](docs/README.zh-CN.md)
- [中文规则设计说明](docs/rule-design.zh-CN.md)
- [Documentation index](docs/README.md)
- [MATLAB CI guide](docs/matlab-ci-guide.md)
- [Adoption playbook](docs/adoption-playbook.md)
- [Dogfooding adoption report](docs/adoption-report-matlab-scientific-figures.md)
- [JSON report](docs/json-report.md)
- [PR comment report](docs/pr-comment-template.md)
- [Rule design](docs/rule-design.md)
- [v2 compatibility](docs/v2-compatibility.md)
- [OpenAI Codex maintainer workflow](docs/openai-codex-maintainer-workflow.md)
- [中文 PyPI 发布检查清单](docs/pypi-release-checklist.zh-CN.md)
- [PyPI release checklist](docs/pypi-release-checklist.md)
- [Release artifacts](docs/release-artifacts.md)
- [Release cadence](docs/release-cadence.md)
- [Version plan](docs/version-plan.md)
- [Roadmap](ROADMAP.md)
