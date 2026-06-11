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
- **找不到源文件时必须停止并询问路径**：如果暂时无法定位 `sky-rules` 源仓库、源规则文件或源工作流文件，必须先向用户确认真实源路径；禁止因为“先找不到原文件”就直接修改 `~/.codex/AGENTS.md`、`~/.codex/skills/`、`~/.gemini/`、`~/.codeium/` 等同步产物，也禁止把同步产物当作临时修改方案。
- **必须先改源文件，再看同步结果**：所有规则 / 工作流变更都应先写入 `sky-rules` 源文件，再通过同步脚本生成编辑器产物；同步产物只允许用于验证落盘结果和模型可见性，不允许作为编辑入口。
- 修改完成后，先运行 `python3 scripts/check-rules.py` 自检规则结构，再运行 `sync-to-editors-only.bat`（或优先使用 `python3 sync-workflows.py --no-git`，当前环境仅 `python` 可用时再使用 `python sync-workflows.py --no-git`）同步到各编辑器

## 0.1 sky-rules 源仓库定位规范

**核心原则**：当当前工作区不是 `sky-rules` 源仓库时，必须先通过可验证来源定位源仓库，禁止把某台机器的固定路径写入规则或工作流。

定位顺序：

1. 优先使用用户明确提供的路径，并校验该目录包含 `sync-workflows.py`、`rules/rules-manifest.json`、`rules/global-rules.md`、`workflows/`。
2. 若当前会话已确认过源仓库路径，可以复用该路径，但每次使用前仍需重新校验仓库标识文件。
3. 可使用工具配置、环境变量、shell history 等作为线索，但只能作为线索，必须进入目录后校验。
4. 搜索目录必须收敛在常见项目目录或已知父目录内，禁止默认全盘 `find /`、扫描整个 `/mnt`、`/home` 等大范围挂载点。
5. 若短时间内无法确认源仓库，必须停止并询问用户路径，禁止继续扩大扫描范围。

示例路径必须使用占位表达，例如 `<已确认的 sky-rules 仓库路径>` 或 `$SKY_RULES_REPO`，禁止写入个人机器上的绝对路径。

## 1. 确认规则归属

**默认规则**：如果用户未指定更新哪个规则文件，默认更新 `sky-rules` 的全局规则体系，但必须先通过 `rules/README.md` 和 `rules/rules-manifest.json` 定位具体源文件。只有 P0 红线、场景索引、读取策略这类常驻入口内容，才直接更新 `rules/global-rules.md`。

如果用户指定了具体的规则文件或工作流，则更新用户指定的文件。

| 类型 | sky-rules 仓库中的源文件 | 同步目标 | 判断标准 |
|------|---------------------------|---------|--------|
| 全局规则（默认） | `rules/rules-manifest.json` 拼接的 `rules/global-rules.md`、`rules/core/*.md`、`rules/scenes/*.md`、`rules/projects/*.md` | Antigravity: `~/.gemini/GEMINI.md`；Windsurf: `~/.codeium/windsurf/memories/global_rules.md`；Codex: `~/.codex/AGENTS.md` | 跨项目通用（TODO 规范、命名规范、Git 规范等） |
| 全局工作流 | `workflows/base.*.md` | Windsurf: `~/.codeium/windsurf/global_workflows/*.md`；Antigravity: `~/.gemini/antigravity/global_workflows/*.md`；Codex Skills: `~/.codex/skills/*` | 跨项目通用的工作流程 |
| 项目规则 | 项目根目录 `GEMINI.md` | 不经过 `sync-workflows.py` | 与特定项目相关 |
| 项目工作流 | 项目根目录 `.agents/workflows/*.md` | 不经过 `sync-workflows.py` | 项目特有 |

**不确定时先问用户**，不要自行判断。

## 1.1 维护索引同步规范

**核心原则**：新增规则、章节、工作流或同步目标时，必须同步维护对应索引文件，避免后续 AI 只能靠全局搜索理解结构。

| 变更类型 | 需要同步检查的索引 |
|---------|-------------------|
| 新增全局规则大章节 | `rules/README.md` |
| 新增全局规则源文件 | `rules/rules-manifest.json`、`rules/README.md` |
| 调整全局规则归属策略 | `rules/rules-manifest.json`、`rules/README.md`、根目录 `AGENTS.md` |
| 新增工作流文件 | `workflows/README.md` |
| 调整工作流命名或分类 | `workflows/README.md`、根目录 `AGENTS.md` |
| 新增 AI 工具同步目标 | `README.md`、`sync-targets.example.json` |
| 调整规则维护流程 | 根目录 `AGENTS.md`、`README.md` |
| 调整规则自检闭环 | `scripts/check-rules.py`、根目录 `AGENTS.md`、`README.md`、`rules/README.md` |

- 索引文件只写职责、入口、流程和归属说明，不复制长规则正文。
- 如果只是补充某条已有规则，不需要机械更新索引；只有新增大章节、改变归属或新增工作流时才更新。
- 写入前预览时必须一并说明是否需要更新索引；不需要更新时说明原因。
- `rules/rules-manifest.json` 是全局规则同步顺序的唯一清单；新增、删除或重命名 `rules/` 下的规则源文件时，必须同步维护 manifest。
- 涉及规则、manifest、索引或同步流程调整时，必须同步维护 `scripts/check-rules.py` 的校验项；如果不需要更新脚本，必须说明原因。

## 1.2 全局规则拆分文件定位规范

**核心原则**：修改全局规则时，禁止直接把内容塞进 `rules/global-rules.md`。必须先按 `rules/README.md` 的规则文件索引定位目标细则文件。

定位顺序：

1. 先读 `rules/README.md`，根据“规则文件索引”和“新增规则归属”确定候选文件。
2. 再读 `rules/rules-manifest.json`，确认候选文件在拼接清单中，且同步顺序合理。
3. 搜索候选文件和相邻主题文件，确认是否已有类似规则。
4. 只有当规则属于 P0 红线、规则读取策略、场景索引或示例总体要求时，才修改 `rules/global-rules.md`。
5. 如果现有文件无法承载新增主题，先向用户预览新增文件名、放置目录、manifest 插入位置和 README 索引更新内容，确认后再写入。

## 2. 查看目标文件现有内容

**必须先 `view_file` 查看目标文件**，确认：

1. 是否已有相同或类似的规则（避免重复）
2. 应该插入到哪个章节（按主题归类）
3. 现有的编号/格式是什么（保持一致）

如果目标是全局规则体系，还必须先查看 `rules/README.md` 和 `rules/rules-manifest.json`，确认目标规则源文件和 manifest 状态。

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
- 规则示例必须抽象化：禁止直接复制真实业务代码、真实接口路径、真实变量名、真实权限标识、真实客户 / 供应商 / 金额等生产信息作为示例。
- 示例只保留能说明规则的最小结构，用 `xxx`、`TODO业务字段`、`getXxxList`、`业务状态` 等抽象命名表达场景，避免把业务细节伪装成可照搬模板。
- 示例代码应控制长度，只展示关键错误点和正确写法；能用 5 行说明的问题，不贴完整组件、完整接口、完整弹窗。
- 如果必须引用真实项目约定，例如固定占位符、固定公共方法、固定目录名，才保留真实名称，并说明这是“项目约定”而不是普通示例。

## 6. 用户预览确认

**核心原则**：规则内容编写完成后，**必须先让用户预览确认，再写入文件**。禁止跳过预览直接修改规则文件。

**操作步骤**：

1. 将拟定的规则内容以 markdown 形式展示给用户
2. 说明：将插入到哪个文件的哪个章节
3. 说明：是否需要同步更新 `rules/rules-manifest.json`、`AGENTS.md`、`README.md`、`rules/README.md` 或 `workflows/README.md`
4. 等待用户确认后，再执行实际的文件修改
5. 如果用户要求调整，修改后再次预览，直到用户满意

## 7. 操作完成后

- 告知用户：加在了哪个文件的哪个章节
- 如果涉及多个文件（如全局 + 项目都需要改），一次性说明
- 如果涉及索引维护，说明同步更新了哪个索引文件；如果未更新索引，说明原因
- 如果涉及全局规则源文件新增 / 删除 / 重命名，说明 `rules/rules-manifest.json` 的拼接顺序变化
- **用户确认后的自动同步**：当用户在预览后回复“可以”、“确认”、“更新”、“执行”等明确同意语义时，必须完成实际写入，并立即执行：
  1. 在已确认的 `sky-rules` 仓库根目录优先执行 `python3 scripts/check-rules.py`；如果当前环境仅 `python` 可用且确认其指向 Python 3，再执行 `python scripts/check-rules.py`
  2. 自检通过后，优先执行 `python3 sync-workflows.py --no-git`；如果当前环境仅 `python` 可用且确认其指向 Python 3，再执行 `python sync-workflows.py --no-git`
  3. 同步完成后再次执行 `python3 scripts/check-rules.py`，确认生成后的 Codex Skill 等同步产物也已包含维护闭环
- 如果需要输出完整命令，必须基于当前电脑上已确认的仓库实际路径生成；Git Bash 使用正斜杠路径格式，禁止写死某台电脑的本地路径
- 如果当前电脑的 Gemini / Windsurf / Codex / Agents 目录与默认约定不同，必须通过 `SKY_RULES_*` 环境变量覆盖同步目标，禁止直接修改同步脚本里的目标路径
- 在新电脑或目录不确定时，必须优先执行 `python3 sync-workflows.py --doctor` 体检 Codex / Antigravity / Windsurf / Agents 的实际写入路径和可写状态；如果当前环境仅 `python` 可用且确认其指向 Python 3，再执行 `python sync-workflows.py --doctor`
- 如果 `--doctor` 显示某个未使用工具目标为 `SKIP`，属于正常结果；默认同步会跳过该目标，禁止为了没用的工具强行创建目录
- 后续扩展其他编辑器同步目标时，优先通过 `sync-targets.json` 增加团队共享目标；仅当前电脑私有的目标写入 `sync-targets.local.json`，禁止为了新增编辑器直接改 Python 同步逻辑
- **同步结果说明必须具体**：执行 `sync-workflows.py --no-git` 后，回复用户时不能只说“已同步到各编辑器”，必须按实际同步内容说明目标：
  - 自检结果：说明 `scripts/check-rules.py` 是否通过，若有 WARN 必须列出警告含义
  - 全局规则：按 `rules/rules-manifest.json` 拼接后，同步到 Antigravity `~/.gemini/GEMINI.md`、Windsurf `~/.codeium/windsurf/memories/global_rules.md`、Codex `~/.codex/AGENTS.md`
  - 工作流：同步到 Windsurf `~/.codeium/windsurf/global_workflows/`、Antigravity `~/.gemini/antigravity/global_workflows/`
  - Skills：由 workflows 生成到 Codex `~/.codex/skills/`
  - Codex 验证：必须说明 `AGENTS.md` 落盘、Skills 落盘数量，以及 `prompt-input` 是否可见代表性 Skills
- **闭环验收结果必须输出**：最终回复必须用精简回执交代执行结果，禁止只说“已完成 / 已同步”。格式至少包含：
  - `自检：python3 scripts/check-rules.py -> OK / WARN / FAIL`
  - `同步：python3 sync-workflows.py --no-git -> OK / WARN / FAIL`
  - `Codex 验证：AGENTS.md 已落盘，Skills 数量，prompt-input 代表性 Skills 可见性`
  - `二次自检：python3 scripts/check-rules.py -> OK / WARN / FAIL`
  - `提交状态：未提交 / 已提交 commit hash；未推送时也要说明`
- 如果任一环节出现 `WARN` 或 `FAIL`，必须摘出关键原因和影响范围；只有用户明确要求“贴完整输出”时，才贴完整终端输出。
- **同步后的提交确认**：规则写入、同步完成并输出同步结果后，必须询问用户是否需要提交并推送 `sky-rules` 仓库本次变更。
- 如果用户确认提交/推送，则按 `base-git-commit-message` 的提交信息规范，对已确认的 `sky-rules` 仓库生成 commit message，并执行：
  1. `git status --short --branch`
  2. `git diff --cached` / `git diff` 核对变更
  3. 仅暂存本次规则相关源文件
  4. `git commit`
  5. `git push`
- 如果用户未确认提交/推送，只完成规则写入和同步，不执行任何 git 写操作。
- 除非用户明确要求，否则不执行 `git add`、`git commit`、`git push`
