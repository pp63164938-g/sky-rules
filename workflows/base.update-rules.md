---
description: 优化/新增全局规则或工作流 - 明确规则归属位置，避免重复沟通和添加错位置
---

# 规则与工作流维护规范

当用户要求“同步到全局规则”、“加到规则里”、“调整工作流”等操作时，严格按以下流程执行。

## 0. 单一数据源原则（最高优先级）

> **所有规则和工作流的修改，必须在 `sky-rules` Git 仓库中进行。**
> **严禁直接修改编辑器目录下的文件（如 `~/.codeium/`、`~/.gemini/`）。**

- 编辑器目录中的文件是**同步产物**，直接修改会在下次同步时被覆盖丢失
- 如果当前工作区不是 `sky-rules` 仓库，应先确认 `sky-rules` 仓库的位置，再去该仓库中修改
- 修改完成后，提醒用户运行 `sync-to-editors-only.bat`（或 `python sync-workflows.py --no-git`）同步到各编辑器

## 1. 确认规则归属

**默认规则**：如果用户未指定更新哪个规则文件，**默认更新全局规则**（`sky-rules/rules/global-rules.md`）。

如果用户指定了具体的规则文件或工作流，则更新用户指定的文件。

| 类型 | sky-rules 仓库中的源文件 | 同步目标 | 判断标准 |
|------|---------------------------|---------|--------|
| 全局规则（默认） | `rules/global-rules.md` | Antigravity: `~/.gemini/GEMINI.md`；Windsurf: `~/.codeium/windsurf/memories/global_rules.md`；Codex: `~/.codex/AGENTS.md` | 跨项目通用（TODO 规范、命名规范、Git 规范等） |
| 全局工作流 | `workflows/base.*.md` | Windsurf: `~/.codeium/windsurf/global_workflows/*.md`；Antigravity: `~/.gemini/antigravity/global_workflows/*.md`；Agents/Codex Skills: `~/.agents/skills/*` | 跨项目通用的工作流程 |
| 项目规则 | 项目根目录 `GEMINI.md` | 不经过 `sync-workflows.py` | 与特定项目相关 |
| 项目工作流 | 项目根目录 `.agents/workflows/*.md` | 不经过 `sync-workflows.py` | 项目特有 |

**不确定时先问用户**，不要自行判断。

## 2. 查看目标文件现有内容

**必须先 `view_file` 查看目标文件**，确认：

1. 是否已有相同或类似的规则（避免重复）
2. 应该插入到哪个章节（按主题归类）
3. 现有的编号/格式是什么（保持一致）

## 3. 找到正确的插入位置

- **按主题归类**：新规则放到相关主题的章节下，不要追加到文件末尾
- **检查上下文**：查看目标位置前后 5-10 行，确认上下文正确
- **保持编号连续**：如果是编号列表，更新后续编号

## 4. 避免重复

- 新增前搜索目标文件是否已有类似表述
- 如果已有相似规则，考虑**修改/补充**而非新增
- 全局规则和项目规则不要写相同的内容（项目规则可引用全局规则）

## 5. 编写规则的格式要求

- 一句话说清核心原则
- 必要时附带 ❌ 错误示例 和 ✅ 正确示例
- 保持与现有规则风格一致

## 6. 用户预览确认

**核心原则**：规则内容编写完成后，**必须先让用户预览确认，再写入文件**。禁止跳过预览直接修改规则文件。

**操作步骤**：

1. 将拟定的规则内容以 markdown 形式展示给用户
2. 说明：将插入到哪个文件的哪个章节
3. 等待用户确认后，再执行实际的文件修改
4. 如果用户要求调整，修改后再次预览，直到用户满意

## 7. 操作完成后

- 告知用户：加在了哪个文件的哪个章节
- 如果涉及多个文件（如全局 + 项目都需要改），一次性说明
- **用户确认后的自动同步**：当用户在预览后回复“可以”、“确认”、“更新”、“执行”等明确同意语义时，必须完成实际写入，并立即执行：
  `python D:/self/Ai/sky-rules/sync-workflows.py --no-git`
- 同步命令必须使用 Git Bash 可直接执行的正斜杠路径格式，不要输出 Windows 反斜杠路径
- **同步结果说明必须具体**：执行 `sync-workflows.py --no-git` 后，回复用户时不能只说“已同步到各编辑器”，必须按实际同步内容说明目标：
  - 全局规则：同步到 Antigravity `~/.gemini/GEMINI.md`、Windsurf `~/.codeium/windsurf/memories/global_rules.md`、Codex `~/.codex/AGENTS.md`
  - 工作流：同步到 Windsurf `~/.codeium/windsurf/global_workflows/`、Antigravity `~/.gemini/antigravity/global_workflows/`
  - Skills：由 workflows 生成到 Agents/Codex `~/.agents/skills/`
- **同步后的提交确认**：规则写入、同步完成并输出同步结果后，必须询问用户是否需要提交并推送 `sky-rules` 仓库本次变更。
- 如果用户确认提交/推送，则按 `base-git-commit-message` 的提交信息规范，对 `D:/self/Ai/sky-rules` 仓库生成 commit message，并执行：
  1. `git status --short --branch`
  2. `git diff --cached` / `git diff` 核对变更
  3. 仅暂存本次规则相关源文件
  4. `git commit`
  5. `git push`
- 如果用户未确认提交/推送，只完成规则写入和同步，不执行任何 git 写操作。
- 除非用户明确要求，否则不执行 `git add`、`git commit`、`git push`
