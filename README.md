# Sky Rules - AI 编码规范与工作流

统一管理多个 AI 编辑器（Windsurf、Antigravity/Gemini、Cursor 等）的全局规则和工作流。

## 目录结构

```
sky-rules/
├── rules/                  # 全局规则
│   └── global-rules.md    # 各编辑器共用的全局规则（详见下方说明）
├── workflows/              # 工作流文件（所有编辑器共享）
│   ├── base.*.md           # 基础工作流
│   ├── kl.*.md             # Kunlun 项目专用工作流
│   └── more-tool.*.md      # 工具类工作流
├── sync-workflows.py       # 同步脚本（核心逻辑）
├── sync-workflows.bat      # 同步脚本（双击运行）
└── README.md
```

### `rules/global-rules.md` 说明

这是**所有编辑器共用的全局规则源文件**，包含代码规范、Git 操作规范、CSS 规范等跨项目通用规则。

同步脚本会将它**自动映射**为各编辑器要求的文件名：

| 编辑器 | 同步后的文件路径 | 说明 |
|--------|-----------------|------|
| Antigravity | `~/.gemini/GEMINI.md` | Gemini CLI 要求的固定文件名 |
| Windsurf | `~/.codeium/windsurf/memories/global_rules.md` | 暂由 Windsurf 自行管理 |

> 修改规则时只需编辑 `rules/global-rules.md`，运行同步脚本后各编辑器自动生效。

## 使用方式

### 同步脚本（推荐）

双击 `sync-workflows.bat` 或在终端执行：

```bash
# 全量同步（git 提交 + 文件同步）
python sync-workflows.py

# 仅同步文件，跳过 git 提交
python sync-workflows.py --no-git
```

**同步内容：**

| 源文件 | 目标路径 | 说明 |
|--------|----------|------|
| `workflows/*.md` | `~/.codeium/windsurf/global_workflows/` | Windsurf 工作流 |
| `workflows/*.md` | `~/.gemini/antigravity/global_workflows/` | Antigravity 工作流 |
| `rules/global-rules.md` | `~/.gemini/GEMINI.md` | Antigravity 全局规则 |

**同步特性：**
- 使用 Python `shutil` 处理文件复制，兼容中文路径
- 增量同步：比较修改时间，跳过未变更文件
- 镜像模式：自动删除目标目录中源不存在的文件
- 自动 git commit + push

## 维护说明

> ⚠️ **核心原则：所有规则和工作流的修改，必须在 `sky-rules/` 仓库中进行，严禁直接修改编辑器目录下的文件。**
> 编辑器目录中的文件是**同步产物**，直接修改会在下次同步时被覆盖丢失。

- **修改规则** → 编辑 `rules/global-rules.md` → 运行 `sync-workflows.bat`
- **修改工作流** → 编辑 `workflows/*.md` → 运行 `sync-workflows.bat`
- **版本控制**：通过 Git 管理变更历史，可追溯、可回滚
- **多设备同步**：其他设备克隆仓库后运行同步脚本即可
- **AI 优化规则**：让 AI 在 sky-rules 仓库中直接修改，修改后运行同步脚本
