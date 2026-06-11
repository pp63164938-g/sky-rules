# Sky Rules - AI 编码规范与工作流

统一管理多个 AI 编辑器（Windsurf、Antigravity/Gemini、Cursor 等）的全局规则和工作流。

## 目录结构

```
sky-rules/
├── AGENTS.md              # AI 入口说明：修改边界、先读顺序、新增规则流程
├── rules/                  # 全局规则
│   ├── README.md          # 全局规则维护索引
│   └── global-rules.md    # 各编辑器共用的全局规则（详见下方说明）
├── workflows/              # 工作流文件（所有编辑器共享）
│   ├── README.md          # 工作流维护索引
│   ├── base.*.md           # 基础工作流
│   ├── kl.*.md             # Kunlun 项目专用工作流
│   └── more-tool.*.md      # 工具类工作流
├── sync-workflows.py       # 同步脚本（核心逻辑）
├── sync-targets.example.json # 新增编辑器同步目标配置示例
├── sync-to-editors-only.bat            # 双击：仅同步到编辑器，不执行 Git 操作
├── commit-push-and-sync-to-editors.bat # 双击：Git 提交、推送并同步到编辑器
└── README.md
```

## 维护入口

| 入口 | 面向对象 | 作用 |
|------|----------|------|
| `AGENTS.md` | AI | 进入本仓库后的优先读取入口，说明红线、先读顺序、文件职责和新增规则流程 |
| `README.md` | 人 / AI | 仓库维护手册，说明目录结构、同步方式、接入方式和同步目标 |
| `rules/README.md` | 人 / AI | 全局规则维护索引，说明规则归属、章节策略、写法模板和维护自检 |
| `workflows/README.md` | 人 / AI | 工作流维护索引，说明工作流命名、归属、结构和扩展标准 |

新增规则或工作流时，优先读取 `AGENTS.md`，再按场景读取 `rules/README.md` 或 `workflows/README.md`。长规则正文只维护在 `rules/global-rules.md` 或对应 `workflows/*.md` 中，入口文件只做索引和流程说明。

### `rules/global-rules.md` 说明

这是**所有编辑器共用的全局规则源文件**，包含代码规范、Git 操作规范、CSS 规范等跨项目通用规则。

同步脚本会将它**自动映射**为各编辑器要求的文件名：

| 编辑器 | 同步后的文件路径 | 说明 |
|--------|-----------------|------|
| Antigravity | `~/.gemini/GEMINI.md` | Gemini CLI 要求的固定文件名 |
| Windsurf | `~/.codeium/windsurf/memories/global_rules.md` | Windsurf 要求的固定文件名 |

> 修改规则时只需编辑 `rules/global-rules.md`，运行同步脚本后各编辑器自动生效。

### 新增规则的维护流程

新增规则或工作流时遵循以下顺序：

1. 判断归属：通用硬规则放 `rules/global-rules.md`；通用流程放 `workflows/base.*.md`；Kunlun 专属流程放 `workflows/kl.*.md`；项目专属规则留在对应项目。
2. 搜索查重：先搜索 `rules/` 和 `workflows/`，已有相近内容时优先补充旧规则。
3. 定位章节：按主题插入，禁止追加到文件末尾；新增大章节或新工作流时更新对应 README 索引。
4. 预览确认：AI 写入前必须先展示拟新增内容和插入位置，用户确认后再修改源文件。
5. 同步验证：执行 `python3 sync-workflows.py --no-git`，确认规则和 Skills 已同步到目标工具。

## 使用方式

### 同步脚本（推荐）

| 操作 | 双击 | 终端命令 |
|------|------|---------|
| **仅同步到编辑器，不执行 Git 操作（推荐）** | `sync-to-editors-only.bat` | `python sync-workflows.py --no-git` |
| **Git 提交、推送并同步到编辑器** | `commit-push-and-sync-to-editors.bat` | `python sync-workflows.py` |
| **只查看当前电脑会同步到哪里** | - | `python sync-workflows.py --print-targets` |
| **新电脑接入体检（推荐首次执行）** | - | `python sync-workflows.py --doctor` |
| **强制预创建全部默认目标** | - | `python sync-workflows.py --no-git --include-missing-targets` |

**同步内容：**

| 源文件 | 目标路径 | 说明 |
|--------|----------|------|
| `workflows/*.md` | `~/.codeium/windsurf/global_workflows/` | Windsurf 工作流 |
| `workflows/*.md` | `~/.gemini/antigravity/global_workflows/` | Antigravity 工作流 |
| `workflows/*.md` | `~/.codex/skills/` | Codex Skills |
| `rules/global-rules.md` | `~/.gemini/GEMINI.md` | Antigravity 全局规则 |
| `rules/global-rules.md` | `~/.codeium/windsurf/memories/global_rules.md` | Windsurf 全局规则 |
| `rules/global-rules.md` | `~/.codex/AGENTS.md` | Codex 全局规则 |

**同步特性：**
- 使用 Python `shutil` 处理文件复制，兼容中文路径
- 仓库路径自适应：脚本根据自身所在目录定位源文件，可克隆到任意目录
- 用户目录自适应：同步目标基于当前电脑的用户目录（`~` / `Path.home()`）
- 目标目录可配置：其他电脑的 Gemini / Windsurf / Codex 目录不一致时，可通过环境变量覆盖同步目标
- 未使用工具自动跳过：未检测到 Windsurf / Antigravity / Codex / Agents 目录且未配置环境变量时，不会自动创建对应目录
- 编辑器可扩展：新增其他编辑器时优先通过 `sync-targets.json` / `sync-targets.local.json` 配置目标，不改 Python 同步逻辑
- 同步排除：目录同步支持 `exclude` 排除说明文件，内置工作流同步会排除 `workflows/README.md`
- Codex 加载验证：同步后自动检查 `~/.codex/AGENTS.md`、`~/.codex/skills/` 落盘，并通过 `codex-cli debug prompt-input` 验证 Skills 是否进入模型可见上下文
- 增量同步：比较修改时间，跳过未变更文件
- 镜像模式：自动删除目标目录中源不存在的文件
- `sync-to-editors-only.bat` 仅同步文件，不执行任何 Git 操作
- `commit-push-and-sync-to-editors.bat` 会自动执行 git commit + push，再同步文件

### 自定义同步目标

新电脑接入成本很低：先体检，再同步。

```powershell
python sync-workflows.py --doctor
python sync-workflows.py --no-git
```

`--doctor` 不会同步文件，只会检查：

- 仓库源文件是否存在
- 当前电脑解析到的 Codex / Antigravity / Windsurf / Agents 目标路径
- 每个目标路径来自默认约定、工具环境变量，还是 `SKY_RULES_*` 覆盖
- 目标或最近父目录是否可写

如果体检输出 `OK 当前电脑可以执行同步`，直接运行 `python sync-workflows.py --no-git`。

如果电脑没有使用某个工具，例如没有 Windsurf 或 Antigravity，`--doctor` 会显示 `SKIP`，普通同步会自动跳过，不会创建无用目录。只有以下情况才会同步到该工具：

- 已检测到该工具目录存在
- 已配置对应 `SKY_RULES_*` 环境变量
- 显式传入 `--include-missing-targets` 要求预创建默认目录

默认情况下，脚本使用当前用户目录下的常见路径：

| 目标 | 默认路径 |
|------|----------|
| Windsurf 工作流 | `~/.codeium/windsurf/global_workflows/` |
| Windsurf 全局规则 | `~/.codeium/windsurf/memories/global_rules.md` |
| Antigravity 工作流 | `~/.gemini/antigravity/global_workflows/` |
| Antigravity/Gemini 全局规则 | `~/.gemini/GEMINI.md` |
| Codex 全局规则 | `~/.codex/AGENTS.md` |
| Codex Skills | `~/.codex/skills/` |

如果某台电脑的目录不同，不要修改 `sync-workflows.py`，优先配置环境变量：

| 环境变量 | 作用 |
|----------|------|
| `SKY_RULES_WINDSURF_HOME` | 覆盖 Windsurf 根目录，默认派生 `global_workflows/` 与 `memories/global_rules.md` |
| `SKY_RULES_GEMINI_HOME` | 覆盖 Gemini 根目录，默认派生 `antigravity/global_workflows/` 与 `GEMINI.md` |
| `SKY_RULES_CODEX_HOME` | 覆盖 Codex 根目录，默认派生 `AGENTS.md` 与 `skills/` |
| `SKY_RULES_AGENTS_HOME` | 兼容早期 Agents 根目录，默认派生 `skills/` |
| `SKY_RULES_WINDSURF_WORKFLOWS_DIR` | 精确覆盖 Windsurf 工作流目录 |
| `SKY_RULES_WINDSURF_RULES_FILE` | 精确覆盖 Windsurf 全局规则文件 |
| `SKY_RULES_GEMINI_WORKFLOWS_DIR` | 精确覆盖 Antigravity 工作流目录 |
| `SKY_RULES_GEMINI_RULES_FILE` | 精确覆盖 Antigravity/Gemini 全局规则文件 |
| `SKY_RULES_CODEX_AGENTS_FILE` | 精确覆盖 Codex `AGENTS.md` 文件 |
| `SKY_RULES_CODEX_SKILLS_DIR` | 精确覆盖 Codex Skills 目录 |
| `SKY_RULES_AGENTS_SKILLS_DIR` | 兼容早期 Agents/Codex Skills 目录覆盖 |

兼容优先级：

1. 精确目标变量优先，例如 `SKY_RULES_GEMINI_RULES_FILE`
2. Sky Rules 根目录变量其次，例如 `SKY_RULES_GEMINI_HOME`
3. 工具自身环境变量，例如 Codex 的 `CODEX_HOME`
4. 默认用户目录约定，例如 `~/.gemini/GEMINI.md`

新电脑首次配置建议先执行：

```powershell
python sync-workflows.py --doctor
```

确认输出路径和可写状态符合当前电脑的 Codex / Antigravity / Windsurf 配置后，再执行同步。

PowerShell 临时配置示例：

```powershell
$env:SKY_RULES_WINDSURF_HOME = "$env:USERPROFILE\.windsurf"
$env:SKY_RULES_GEMINI_HOME = "D:\Tools\gemini"
python sync-workflows.py --no-git
```

PowerShell 持久配置示例：

```powershell
[Environment]::SetEnvironmentVariable("SKY_RULES_WINDSURF_HOME", "$env:USERPROFILE\.windsurf", "User")
[Environment]::SetEnvironmentVariable("SKY_RULES_GEMINI_HOME", "D:\Tools\gemini", "User")
```

重新打开终端后执行：

```powershell
python sync-workflows.py --doctor
python sync-workflows.py --no-git
```

### 扩展其他编辑器

新增其他编辑器时，优先使用配置文件，不直接改 `sync-workflows.py`：

| 文件 | 用途 | 是否建议提交 |
|------|------|--------------|
| `sync-targets.json` | 团队共享的新编辑器同步目标 | 是 |
| `sync-targets.local.json` | 某台电脑自己的同步目标或临时路径 | 否，已被 `.gitignore` 忽略 |
| `sync-targets.example.json` | 配置示例 | 是 |

配置示例：

```json
{
  "targets": [
    {
      "name": "示例编辑器全局规则",
      "mode": "codex_rules",
      "source": "rules/global-rules.md",
      "target": "${HOME}/.example-ai/AGENTS.md",
      "target_env": "SKY_RULES_EXAMPLE_RULES_FILE",
      "detect": "${HOME}/.example-ai"
    },
    {
      "name": "示例编辑器工作流",
      "mode": "mirror",
      "source": "workflows",
      "target": "${HOME}/.example-ai/workflows",
      "target_env": "SKY_RULES_EXAMPLE_WORKFLOWS_DIR",
      "detect": "${HOME}/.example-ai",
      "pattern": "*.md",
      "exclude": ["README.md"]
    }
  ]
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| `name` | 体检和同步输出中展示的目标名称 |
| `mode` | 同步模式：`mirror` 镜像目录、`file` 直接复制文件、`codex_rules` 生成去除 frontmatter 的规则文件、`agents_skills` 由工作流生成 Skill |
| `source` | 源文件或源目录，默认相对 `sky-rules` 仓库根目录 |
| `target` | 默认目标路径，支持 `${ROOT}`、`${HOME}`、`~` 和系统环境变量 |
| `target_env` | 精确覆盖目标路径的环境变量名 |
| `detect` | 工具检测目录；不存在且未配置环境变量时，默认同步会跳过该目标 |
| `pattern` | `mirror` / `agents_skills` 使用的文件匹配规则，默认 `*.md` |
| `exclude` | 可选，按文件名排除不参与目录同步或 Skill 生成的说明文件，例如 `["README.md"]` |

新增后先运行：

```powershell
python sync-workflows.py --doctor
```

确认新增目标显示正常，再执行同步。

## 维护说明

> ⚠️ **核心原则：所有规则和工作流的修改，必须在 `sky-rules/` 仓库中进行，严禁直接修改编辑器目录下的文件。**
> 编辑器目录中的文件是**同步产物**，直接修改会在下次同步时被覆盖丢失。

- **修改规则** → 编辑 `rules/global-rules.md` → 双击 `sync-to-editors-only.bat`
- **修改工作流** → 编辑 `workflows/*.md` → 双击 `sync-to-editors-only.bat`
- **新增大章节或新工作流** → 同步更新 `rules/README.md` 或 `workflows/README.md`
- **版本控制**：通过 Git 管理变更历史，可追溯、可回滚
- **多设备同步**：其他设备克隆仓库后运行同步脚本即可
- **AI 优化规则**：让 AI 在 sky-rules 仓库中直接修改，修改后运行同步脚本
