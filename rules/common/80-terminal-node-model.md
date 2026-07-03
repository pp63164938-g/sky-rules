# 终端文件操作编码规范

**核心原则**：在终端（PowerShell/CMD）中操作文件时，**必须保证 UTF-8 编码不被破坏**。

**背景**：PowerShell 的 `Get-Content`、`Set-Content`、`-replace` 等命令默认使用系统编码（GBK/CP936），会导致 UTF-8 文件中的中文字符变成乱码。

**规则**：

| 操作     | ❌ 禁止                                         | ✅ 正确                                                                                                          |
| -------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 复制文件 | `Copy-Item` + `Set-Content`                     | `[System.IO.File]::ReadAllBytes/WriteAllBytes`（二进制复制）                                                     |
| 文本替换 | `Get-Content -Raw` + `-replace` + `Set-Content` | 优先使用代码编辑工具（`replace_file_content`），或用 `[System.IO.File]::ReadAllText/WriteAllText` 显式指定 UTF-8 |
| 读取文件 | `Get-Content`                                   | `[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)`                                             |

**优先级**：修改文件内容时，**优先使用代码编辑工具**（`replace_file_content` / `multi_replace_file_content`），避免经过终端处理文本。仅在批量操作或搜索替换等场景才使用终端命令，且必须显式指定 UTF-8。

# Node.js 版本管理规范

**核心原则**：**禁止使用 `nvm`**，必须使用 **Volta** 管理 Node.js 版本。

- ❌ **禁止** `nvm install`、`nvm use`、`nvm alias` 等所有 nvm 命令
- ❌ **禁止**建议用户安装或使用 nvm
- ✅ **强制** 使用 `volta install node@版本号` 安装 Node.js
- ✅ **强制** 使用 `volta pin node@版本号` 固定项目 Node.js 版本
- ✅ 使用 `volta list` 查看当前已安装的版本
- ✅ 使用 `volta run --node 版本号 命令` 临时指定版本运行

**代码示例**：

```bash
# ❌ 禁止 - 使用 nvm
nvm install 20
nvm use 20

# ✅ 正确 - 使用 volta
volta install node@20
volta pin node@20
```

# 模型专用规范

**核心原则**：不同的 AI 模型有特定的工作流规范，需根据当前模型类型遵循对应规则。

## Gemini 模型

当使用 Gemini 模型时，**必须严格遵循** `.gemini/antigravity/global_workflows/gemini.md` 中的所有规范，包括：

1. **语言规范**：全程使用中文交互（对话、文档、注释）
2. **计划与执行决策**：自主评估任务复杂度，选择 Fast 或 Plan 模式
3. **死循环熔断机制**：自我监控，发现死循环立即中断并反馈
4. **全局开发规范**：严格遵循本文件（`.gemini/.gemini.md`）中的所有规范

## 其他模型

其他模型同样需遵循本文件中的全局开发规范，但无需强制遵循 Gemini 专用工作流。
