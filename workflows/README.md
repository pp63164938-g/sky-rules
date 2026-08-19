# 工作流维护索引

`workflows/` 用于维护可被多种 AI 工具复用的场景化流程。同步脚本会把这些 Markdown 文件同步为 Windsurf / Antigravity 工作流，并转换为 Codex Skills。

## 命名规则

| 前缀 | 用途 | 示例 |
| --- | --- | --- |
| `base.*.md` | 跨项目通用工作流 | `base.docs.md`、`base.update-rules.md` |
| `kl.*.md` | Kunlun 项目专属工作流 | `kl.gen-page.md`、`kl.menu-manage.md` |
| `more-tool.*.md` | 特定工具或私有工具链工作流 | `more-tool.commit-and-sync-skill.md` |

同步到 Codex Skills 时，文件名中的 `.` 会转换为 `-`，例如 `base.update-rules.md` 对应 `base-update-rules`。

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

## 工作流伴随资源

工作流依赖的结构化数据必须作为伴随资源与工作流一起同步，禁止只同步工作流说明文件。`base.project-context.md` 与仓库根目录的 `project-catalog.json` 组成不可拆分的资源包：

- 仓库根目录文件是唯一数据源，禁止在各平台目录手工维护副本。
- 普通工作流目标将伴随资源放在工作流文件同目录；Skill 目标将伴随资源放在对应 `SKILL.md` 同目录。
- 新平台使用 `mirror` 或 `agents_skills` 工作流同步模式时自动获得伴随资源，不按平台名称增加专用复制逻辑。
- 新增工作流同步模式时必须先定义伴随资源布局；未支持时体检、同步和一致性验证必须失败。

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
| 生成 Kunlun 页面 | `kl.gen-page.md` |
| 管理 Kunlun 菜单权限 | `kl.menu-manage.md` |
| 生成提交信息并提交 | `base.git-commit-message.md` |
| i18n 翻译处理 | `base.i18n.md` |

## 维护自检

- 是否已有工作流可以补充。
- 文件命名是否符合前缀语义。
- `description` 是否能说明触发场景。
- 是否包含前置确认、执行步骤、验证交付。
- 是否更新了本索引。
- 是否已同步并验证 Codex Skill 可见性。
