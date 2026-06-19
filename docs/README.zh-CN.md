# 文档索引

[English documentation](README.md) | 简体中文

这里整理 `matlab-figure-ci` 的中文使用路径。建议先按你当前要做的事情选择文档，而不是从头顺序阅读。

## 第一次接入

- [MATLAB CI 指南](matlab-ci-guide.md)：了解 `mfigci` 在 GitHub Actions、本地机器和可选 MATLAB render 中分别负责什么。
- [Adoption playbook](adoption-playbook.md)：按阶段接入静态扫描、gallery 检查、release gate 和可选 render，适合不想一开始就把 CI 做得太重的仓库。
- [Dogfooding adoption report](adoption-report-matlab-scientific-figures.md)：查看 `matlab-scientific-figures` 当前如何实际使用本工具。
- [Plotting-skill adoption report](adoption-report-matlab-plotting-skill.md)：查看 `matlab-plotting-skill` 当前如何实际使用本工具。

## 规则和报告

- [中文规则设计说明](rule-design.zh-CN.md)：解释隐私规则、来源风险、禁用扩展名、PDF 处理方式，以及为什么 provenance 默认只是 warning。
- [Rule design](rule-design.md)：英文版规则设计说明。
- [JSON report](json-report.md)：机器可读报告字段、脱敏保证和相对路径保证。
- [PR comment report](pr-comment-template.md)：适合复制到 pull request 评论里的紧凑 Markdown 报告。
- [Submission check example](../examples/reports/submission-check-example.md)：一份使用合成路径和边界声明的投稿前图件检查示例。
- [Evidence packet template](evidence-packet-template.md)：从 `.mfigci-results.json` 生成 review/application 证据包草稿。
- [Issue triage report](issue-triage-report.md)：从 `.mfigci-results.json` 生成 issue/PR 分诊摘要。
- [v2 compatibility](v2-compatibility.md)：v2 版本线的 CLI、配置、报告和策略兼容边界。

## 维护和发布

- [OpenAI Codex maintainer workflow](openai-codex-maintainer-workflow.md)：如何把 Codex 用在真实 OSS 维护中，例如 issue triage、PR review 和 release notes。
- [中文 PyPI 发布检查清单](pypi-release-checklist.zh-CN.md)：未来发布 PyPI 前需要确认的事项，以及为什么当前不应为了关闭 issue 而发布。
- [PyPI release checklist](pypi-release-checklist.md)：英文版 PyPI 发布检查清单。
- [Release artifacts](release-artifacts.md)：如何查看 `release-preflight` JSON artifact。
- [Release cadence](release-cadence.md)：当前版本线的发布节奏和避免过度 release 的原则。
- [Version plan](version-plan.md)：版本边界和公开 release 规划。

## 推荐阅读顺序

如果你只是想在一个 MATLAB 绘图仓库里加质量门：

1. 先运行 `mfigci init` 生成 starter 配置。
2. 阅读 [中文规则设计说明](rule-design.zh-CN.md)，确认哪些 warning 只是提醒、哪些 error 会导致 CI 失败。
3. 用 `mfigci doctor --config mfigci.yml` 检查配置摘要。
4. 用 `mfigci check --config mfigci.yml --report mfigci-report.md` 生成报告。
5. 把报告作为 CI artifact 保存，不要默认提交到仓库。

如果你维护的是公开科研绘图项目，请额外确认：

- gallery 里的图是合成数据或你有权公开的数据生成的。
- `.mat`、`.fig`、`.p`、Office 文件和压缩包没有进入公开仓库。
- provenance warning 不是让你“删掉痕迹”，而是提醒你确认材料来源和授权。
- MATLAB render 在公共 GitHub runner 上通常不可用，第一版 CI 可以只做 scan、gallery 和 report。

如果你在维护 `matlab-figure-ci` 自身：

- 发布 PyPI 前先读 [中文 PyPI 发布检查清单](pypi-release-checklist.zh-CN.md)。
- 不要为了制造活跃度或关闭 issue 而发布。
- 先确认 release-preflight、Package workflow artifact、PyPI 名称快照和干净安装验证。
