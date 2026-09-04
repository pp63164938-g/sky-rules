# 工作流维护索引

`workflows/` 用于维护可被多种 AI 工具复用的场景化流程。同步脚本会把这些 Markdown 文件同步为 Windsurf / Antigravity 工作流，并转换为 Codex Skills。

## 命名规则

| 前缀 | 用途 | 示例 |
| --- | --- | --- |
| `base.*.md` | 跨项目通用工作流 | `base.docs.md`、`base.update-rules.md` |
| `kl.*.md` | Kunlun 项目专属工作流 | `kl.gen-page.md`、`kl.menu-manage.md` |
| `tool.*.md` | 可跨项目复用的工具配置、接入和排障工作流 | `tool.ccswitch.md` |
| `more-tool.*.md` | More-Tool 项目专属工作流或指针 | `more-tool.commit-and-sync-skill.md` |

同步到 Codex Skills 时，文件名中的 `.` 会转换为 `-`，例如 `base.update-rules.md` 对应 `base-update-rules`。

一般工具工作流统一使用 `tool.*.md`；`more-tool.*.md` 只表示现有 More-Tool 项目归属，不作为“更多工具”的通用前缀，也不要求批量重命名已有文件。

## 新增还是补充

优先补充已有工作流，只有满足以下条件时才新增文件：

- 场景边界清晰，能被独立触发。
- 流程包含稳定步骤，而不只是单条规则。
- 与已有工作流职责不同，合并后会让原工作流变得难读。
- 后续可能反复使用，值得独立命名。

不应新增工作流的情况：

- 只是某条编码规则，应放入 `rules/global-rules.md`。
- 只是某个项目的一次性操作，应放项目规则或当前任务说明。
- 只是现有工作流的补充检查项，应更新现有工作流。

## 工作流结构

推荐结构：

```md
---
description: 工作流用途说明
allow_implicit_invocation: false
---

# 工作流名称

触发场景说明。

## 0. 最高优先级原则

不可违反的核心约束。

## 1. 前置确认

执行前必须确认的上下文。

## 2. 执行步骤

按顺序列出操作流程。

## 3. 验证与交付

说明如何验证、如何向用户反馈。
```

`allow_implicit_invocation` 为可选的 Codex Skill 调用策略；省略时默认允许按 `description` 自动匹配。设为 `false` 时，同步脚本会生成 `agents/openai.yaml`，该 Skill 仅允许用户通过 `$skill-name` 显式调用。显式调用工作流的 `description` 和正文仍须同步写清触发边界，避免其他平台误判。

## 工作流渐进式引用

工作流主文件只保留核心不变量、执行顺序、场景选择和验收门禁。接近 500 行、首次读取被截断，或包含三个及以上独立场景时，应把场景细则拆入 `workflows/references/`，避免每次触发都加载无关内容。

- 引用文件统一命名为 `<skill-name>--<topic>.md`，例如 `kl-gen-page--list-and-table.md`。
- `<skill-name>` 使用工作流同步到 Codex 后的目录名；`kl.gen-page.md` 对应 `kl-gen-page`。
- 主工作流通过 `references/<skill-name>--<topic>.md` 相对路径链接，并明确每个引用的触发条件。
- 命中多个场景时完整读取全部命中引用；未命中的引用不得无差别加载。
- 主文件、引用文件和全局规则之间保持单一口径；通用规则留在 `rules/`，引用只维护场景专属事实和执行细则。
- 引用超过 100 行时在顶部提供目录；优先压缩重复示例，禁止通过继续拆出多层引用制造深层跳转。
- 组件版本、目录结构或项目配置变化导致引用失效时，以当前源码为事实依据并回到本仓库更新引用，禁止在同步产物或业务代码中静默兼容。

## 工作流伴随资源

工作流依赖的结构化数据和渐进式引用必须作为伴随资源一起同步，禁止只同步工作流主文件：

- `base.project-context.md` 与仓库根目录的 `project-catalog.json` 组成不可拆分的项目目录资源包；普通工作流目标放在工作流文件同目录，Skill 目标放在对应 `SKILL.md` 同目录。
- `workflows/references/*.md` 是渐进式引用的唯一源文件；普通工作流目标同步到工作流目录的 `references/`，Codex 同步到对应 Skill 的 `references/`。
- 工作流引用的仓库级校验器统一放在根目录 `scripts/`；主工作流写明通过仓库根目录定位，不在 Codex 同步产物中维护第二份源文件。部署到独立运行环境时可以复制脚本，但部署副本不得独立演进。
- 新平台使用 `mirror` 或 `agents_skills` 工作流同步模式时自动获得对应资源，不按平台名称增加专用复制逻辑。
- 同步时自动清理过期引用；`--verify` 必须检查缺失、额外和内容不一致。
- 新增工作流同步模式时必须先定义两类伴随资源布局；未支持时体检、同步和一致性验证必须失败。

## 维护要求

- 工作流应描述“怎么做”，全局规则应描述“必须 / 禁止什么”。
- 仅允许用户显式调用的工作流必须设置 `allow_implicit_invocation: false`，并在触发说明中明确普通相似任务不构成触发条件。
- 工作流中的规则如果具有跨场景通用性，应同步沉淀到 `rules/global-rules.md`。
- 新增工作流后必须更新本文件的命名或索引说明。
- 工作流中的示例必须抽象化，禁止复制真实业务接口、路径、权限标识和生产数据。
- 修改工作流后必须执行 `python3 sync-workflows.py --no-git`，确认 Codex Skills 已重新生成。

## 常见归属

| 场景 | 推荐工作流 |
| --- | --- |
| 新增 / 优化全局规则 | `base.update-rules.md` |
| 根据页面路径或项目说明识别项目目录和专属要求 | `base.project-context.md` |
| 根据接口文档联调 | `base.debugging.md`、`base.docs.md` |
| 用户显式指定后，根据需求文档推进前端、后端或全栈开发闭环 | `base.requirement-dev-closed-loop.md` |
| 创建、扩展、修复或验收飞书 OpenClaw 机器人 | `base.openclaw-bot.md` |
| 生成 Kunlun 页面 | `kl.gen-page.md` |
| 管理 Kunlun 菜单权限 | `kl.menu-manage.md` |
| 生成提交信息并提交 | `base.git-commit-message.md` |
| i18n 翻译处理 | `base.i18n.md` |
| 参考 Claude Code 供应商生成、切换或排查 CC Switch Codex 供应商 | `tool.ccswitch.md` |

## 维护自检

- 是否已有工作流可以补充。
- 文件命名是否符合前缀语义。
- `description` 是否能说明触发场景。
- 是否包含前置确认、执行步骤、验证交付。
- 是否更新了本索引。
- 是否已同步并验证 Codex Skill 可见性。
