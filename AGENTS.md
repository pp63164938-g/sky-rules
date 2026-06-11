# Sky Rules AI 入口

本仓库是 AI 全局规则与工作流的源仓库。AI 进入本仓库后，应优先读取本文件，再按任务场景读取 `README.md`、`rules/README.md` 或 `workflows/README.md`。

## 核心红线

- 所有规则和工作流修改必须发生在本仓库源文件中，禁止直接修改 `~/.codex/`、`~/.gemini/`、`~/.codeium/` 等同步产物。
- 修改规则或工作流前必须先确认归属、查重、定位插入章节，禁止把新内容直接追加到文件末尾。
- 新增或调整规则前必须先给用户预览拟写内容和插入位置，用户确认后再写入。
- 未经用户明确要求，禁止执行 `git add`、`git commit`、`git push`。
- 示例必须抽象化，禁止复制真实业务代码、接口路径、权限标识、客户 / 供应商 / 金额等生产信息。

## 先读顺序

| 场景 | 优先读取 |
| --- | --- |
| 了解仓库用途、同步方式 | `README.md` |
| 新增 / 修改全局规则 | `rules/README.md`、`rules/rules-manifest.json`、目标规则文件 |
| 新增 / 修改工作流 | `workflows/README.md`、目标 `workflows/*.md` |
| 扩展同步目标 | `README.md`、`sync-targets.example.json`、`sync-workflows.py` |
| 规则结构自检 | `scripts/check-rules.py` |
| 提交规则仓库变更 | `workflows/base.git-commit-message.md` |

## 文件职责

| 文件 / 目录 | 职责 |
| --- | --- |
| `README.md` | 人类维护手册，说明仓库结构、同步命令、接入方式 |
| `rules/README.md` | 全局规则维护索引，说明规则归属、章节策略、写法模板 |
| `rules/rules-manifest.json` | 全局规则拼接清单，决定各规则源文件的同步顺序 |
| `rules/global-rules.md` | 全局规则常驻入口，只承载核心理念、P0 红线、场景索引等高优先级内容 |
| `rules/core/` | 跨场景基础硬规则，例如工作流、禁止发散、格式化、注释 |
| `rules/scenes/` | 场景化细则，例如接口联调、组件类型、样式、i18n、终端验证 |
| `rules/projects/` | 项目专属规则，只放特定项目需要遵守的补充规则 |
| `workflows/README.md` | 工作流维护索引，说明命名、归属、扩展标准 |
| `workflows/*.md` | 各场景工作流源文件，会同步为 Windsurf / Antigravity 工作流和 Codex Skills |
| `scripts/check-rules.py` | 规则仓库自检脚本，检查 manifest、索引、拼接结果和同步产物 |
| `sync-workflows.py` | 同步脚本，负责把源规则和工作流同步到各 AI 工具 |

## 新增规则流程

1. 判断归属：通用规则进 `rules/core/` 或 `rules/scenes/`；P0 红线和场景索引才进 `rules/global-rules.md`；通用流程进 `workflows/base.*.md`；Kunlun 专属流程进 `workflows/kl.*.md`；项目专属规则留在对应项目。
2. 搜索查重：先搜索 `rules/` 和 `workflows/`，已有相近内容时优先补充旧规则。
3. 定位章节：按 `rules/README.md` 和 `rules/rules-manifest.json` 找目标文件，按主题插入，禁止追加到无关文件末尾。
4. 预览确认：向用户展示拟新增内容、目标文件和目标章节，等待确认。
5. 写入源文件：只改本仓库源文件，不改同步产物；新增规则文件时必须同步更新 `rules/rules-manifest.json` 和 `rules/README.md`。
6. 同步验证：在仓库根目录执行 `python3 sync-workflows.py --no-git`；同步脚本默认会先执行 `python3 scripts/check-rules.py --source-only`，同步后再执行 `python3 scripts/check-rules.py`。
7. 输出回执：说明实际同步目标、拼接规则源、Codex 可见性、二次自检和提交状态。

## 新增规则写法

一条可长期维护的规则应尽量包含：

- 核心原则：一句话说明规则要解决的问题。
- 适用场景：说明什么时候必须执行。
- 硬性红线：列出禁止行为。
- 正反例：只保留最小抽象示例。
- 判断标准：让后续 AI 和维护者能快速自检。

## 同步说明

常用命令：

```bash
python3 sync-workflows.py --no-git
python3 scripts/check-rules.py
```

同步后需要说明：

- 全局规则是否同步到 Codex `~/.codex/AGENTS.md`、Antigravity `~/.gemini/GEMINI.md`、Windsurf `~/.codeium/windsurf/memories/global_rules.md`。
- 工作流是否同步到 Windsurf / Antigravity 工作流目录。
- Codex Skills 是否生成到 `~/.codex/skills/`。
- Codex `prompt-input` 是否能看到代表性 Skills。
- 同步脚本内置自检是否执行；`--skip-rules-check` 只能在排障时使用，正常规则变更禁止跳过。

最终回复必须输出闭环验收回执：

- 自检：`python3 scripts/check-rules.py` -> OK / WARN / FAIL
- 同步：`python3 sync-workflows.py --no-git` -> OK / WARN / FAIL
- Codex 验证：`AGENTS.md` 落盘、Skills 数量、`prompt-input` 代表性 Skills 可见性
- 二次自检：同步后再次执行 `python3 scripts/check-rules.py` -> OK / WARN / FAIL
- 提交状态：未提交 / 已提交 commit hash；如果未推送也要说明
