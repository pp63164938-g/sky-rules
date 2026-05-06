---
description: Icon/图片替换 - 将 TODOicon_ 标记的临时图标替换为设计提供的正式图标
---

# Icon/图片替换工作流

> 用于将静态开发阶段预留的临时 icon（标记为 `TODOicon_`）替换为设计提供的正式图标。

## 1. 查找待替换的 Icon

搜索项目中所有 `TODOicon_` 标记：

```bash
# 在项目根目录执行
grep -rn "TODOicon_" src/
```

或使用 IDE 全局搜索 `TODOicon_`。

## 2. Icon 命名规范

新增 icon 文件时，**必须先查看项目现有的 icon 命名风格**，保持一致性。

### 核心原则

1. **先调研后命名**：新增 icon 前，先查看 `src/icons/svg/` 或项目 icon 目录中已有文件的命名风格
2. **保持风格一致**：每个项目可能有不同的命名习惯，应遵循当前项目的已有风格
3. **描述清晰**：命名应能清晰表达 icon 的用途或所属位置

### 常见命名风格参考

不同项目可能采用不同风格，以下仅供参考：

| 风格 | 说明 | 示例 |
|------|------|------|
| `使用位置_描述` | 以页面/组件名开头 | `contractSign_download.svg` |
| `功能-描述` | 以功能用途命名 | `withdraw-coins.svg` |
| `类型-状态` | 以类型+状态命名 | `check-success.svg` |
| `通用描述` | 简洁直接描述 | `email-tip.svg` |

### 命名建议

1. **优先带上使用位置**：便于快速定位 icon 的使用场景
   - 示例：`withdraw-address.svg`、`contractSign_computer.svg`

2. **状态变体保持统一**：同一 icon 的不同状态，命名规则应一致
   - 示例：`arrow.svg` → `disabled-arrow.svg`
   - 示例：`check-success.svg` → `check-warning.svg`

3. **避免以下命名**：
   - ❌ 描述不清：`icon.svg`、`icon1.svg`、`new-icon.svg`
   - ❌ 中文命名：`新图标.svg`（可能导致编码问题）

### 操作步骤

```bash
# 1. 先查看项目已有 icon 的命名风格
ls src/icons/svg/

# 2. 根据已有风格命名新 icon
# 3. 将 icon 文件放入对应目录
```

## 3. 确认设计提供的 Icon 资源

检查设计提供的 icon 文件位置（通常在以下目录）：

- `icon/` - 项目根目录的 icon 文件夹
- `src/assets/icons/` - 资源目录
- `src/assets/images/` - 图片目录
- `public/icons/` - 公共资源目录

列出可用的 icon 文件：

```bash
# 查看 icon 目录结构
ls -la icon/
ls -la src/assets/icons/
```

## 4. 替换流程

### 4.1 映射确认与准备工作（关键）

**第 1 步：生成映射关系表并让用户确认**
在执行任何代码修改或提供终端指令之前，AI **必须**先使用表格形式向用户展示映射关系，让用户确认：

| 原始提供文件 | 目标命名 | 代码使用的位置/TODO标记 |
|------------|---------|-----------------------|
| 1.svg      | PromotionSteps_register.svg | TODOicon_注册步骤图标 |
| 2.svg      | PromotionSteps_certification.svg | TODOicon_认证步骤图标 |

> **AI 必须等待用户明确回复确认后，才能进行后续的文件复制和代码替换。**

**第 2 步：提供终端指令执行原则**
- 涉及文件移动、复制、删除等操作，**禁止 AI 自动执行**。
- **必须同时提供两套指令**：一套适用于 **Bash (如 Git Bash)** (`cp`, `rm` 等)，一套适用于 **PowerShell** (`Copy-Item`, `Remove-Item` 等)。由于不同开发者的终端环境不同，提供两种以避免 `command not found` 报错。
- **中文路径特例**：如果文件路径包含中文，必须特别提醒用户**使用 PowerShell** 进行操作，因为 CMD 或部分配置不当的 Bash 在极大概率上会导致文件损坏或乱码。
- 用户需**一次性复制并手动执行**指令。
- 执行前需确认当前目录位置。

### 4.2 理解标记格式

静态开发时，临时 icon 采用**附加标记**方式，不影响原 icon 显示：

```html
<!-- 原始临时标记（icon 可正常显示） -->
<i class="el-icon-question TODOicon_待替换"></i>
```

### 4.3 替换策略

**尺寸调整原则**：
- **自行调整**：根据 icon 文件的实际尺寸和设计稿要求，灵活调整代码中的 `size` 或 `width/height`。
- **不依赖文件尺寸**：SVG 文件本身的大小不代表显示大小，需通过 CSS 或组件属性控制。

**代码替换示例**：

**方式一：替换为 System Icon (SVG Sprite)**

适用于项目已配置 `svg-sprite-loader` 的情况（如 `src/icons/svg`）。

```html
<!-- 替换前 -->
<i class="el-icon-question TODOicon_待替换"></i>

<!-- 替换后 -->
<svg-icon icon-class="withdrawal-rules" style="font-size: 14px;" />
```

**方式二：替换为 Img 标签**

适用于普通图片资源。

```html
<!-- 替换前 -->
<i class="el-icon-question TODOicon_待替换"></i>

<!-- 替换后 -->
<img src="@/assets/icons/custom-icon.svg" width="20" />
```

### 4.4 批量替换

如果有多个相同的临时 icon，可以使用全局替换：

1. 确认替换规则
2. 使用 IDE 的全局替换功能
3. **注意**：替换时需同时删除 `TODOicon_xxx` 标记 class
4. 替换完成后检查效果

## 5. 验证替换结果

1. **终端指令执行确认**：确认用户已执行所有文件操作指令。
2. **视觉检查**：启动项目，检查 icon 是否正常显示，尺寸是否协调。
3. **清理检查**：再次搜索 `TODOicon_`，确保没有遗漏

```bash
# 确认没有遗留标记
grep -rn "TODOicon_" src/
```

## 6. 注意事项

- **删除标记 class**：替换时务必删除 `TODOicon_xxx` 标记，不要遗留
- **保留原有样式**：替换时注意保留原有的样式 class（如尺寸、颜色等）
- **检查响应式**：确认 icon 在不同尺寸下显示正常
- **参考现有用法**：替换前先查看项目中其他 icon 的使用方式，保持一致

## 7. 清理与收尾

替换并验证无误后，**必须**执行清理工作：

1.  **移除临时源文件**：向用户提供指令（如 PowerShell 的 `Remove-Item`），删除用户提供在根目录用来中转的临时原始 SVG 文件（如 `1.svg`、`2.svg`）。
2.  **移除临时注释**：删除如 `<!-- icon 预留位置 -->` 等占位注释。
3.  **移除废弃代码**：删除被注释掉的旧 `<i>` 或 `<img>` 标签，保持代码整洁。
4.  **删除冗余目录**：如果切换了图标存储位置（如从 `src/assets` 迁移至 `src/icons`），务必删除不再使用的旧目录，避免混淆。
