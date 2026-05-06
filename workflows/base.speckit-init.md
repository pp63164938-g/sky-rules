---
description: 初始化规约 - 当用户请求初始化规约、拉取规约模板、设置项目规范时，从 git 仓库拉取 .agent .specify .windsurf 目录到当前项目根目录
---

# 规约初始化 (speckit-init)

从 Git 仓库自动拉取规约模板（`.agent`、`.specify`、`.windsurf` 目录）到当前项目根目录，实现项目规约的快速初始化。

## 规约仓库配置

| 项目         | 值                                                                              |
| ------------ | ------------------------------------------------------------------------------- |
| **仓库地址** | `http://gitlab.praise.com/skyline-internal-open/skyline-ai-spec-coding.git`     |
| **默认分支** | `main`                                                                          |
| **目标目录** | `.agent`、`.specify`、`.windsurf`                                               |

## 执行步骤

### 1. 检测项目根目录

```bash
# 获取项目根目录（优先 git 根目录，否则使用当前目录）
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
```

### 2. 检查目标目录是否已存在

检查 `$PROJECT_ROOT` 下是否已存在 `.agent`、`.specify`、`.windsurf` 目录。

- 如果**不存在**：直接进入步骤 3
- 如果**存在**：询问用户选择操作方式：
  - **覆盖**：删除现有目录，使用新版本
  - **合并**：保留现有文件，只添加缺失的文件
  - **跳过**：不处理该目录

### 3. 克隆规约仓库

```bash
# 创建临时目录
TEMP_DIR=$(mktemp -d)

# 浅克隆规约仓库
git clone --depth=1 --branch main \
  http://gitlab.praise.com/skyline-internal-open/skyline-ai-spec-coding.git \
  "$TEMP_DIR/spec-repo"
```

### 4. 复制规约目录

根据用户选择的操作方式执行复制：

```bash
# 新建/覆盖模式
cp -r "$TEMP_DIR/spec-repo/.agent" "$PROJECT_ROOT/"
cp -r "$TEMP_DIR/spec-repo/.specify" "$PROJECT_ROOT/"
cp -r "$TEMP_DIR/spec-repo/.windsurf" "$PROJECT_ROOT/"
```

合并模式下，只复制目标目录中不存在的文件。

### 5. 清理临时文件

```bash
rm -rf "$TEMP_DIR"
```

### 6. 验证并输出结果

列出已初始化的目录，确认内容完整。

## 初始化后可用的 Workflow 命令

| 命令                   | 说明         |
| ---------------------- | ------------ |
| `/speckit.demand`      | ① 需求分析   |
| `/speckit.product`     | ② 产品设计   |
| `/speckit.architecture`| ③ 架构设计   |
| `/speckit.plan`        | ④ 开发计划   |
| `/speckit.tasks`       | ⑤ 任务分配   |
| `/speckit.implement`   | ⑥ 执行开发   |
| `/speckit.unittest`    | ⑦ 单元测试   |
| `/speckit.testcase`    | ⑧ 测试用例   |
| `/speckit.functest`    | ⑧ 功能测试   |
| `/speckit.testreport`  | ⑨ 测试报告   |
| `/speckit.report`      | ⑩ 开发报告   |
| `/speckit.archive`     | 📦 迭代归档  |
| `/speckit.update`      | 🔄 增量更新  |

## 错误处理

| 错误场景       | 处理方式                              |
| -------------- | ------------------------------------- |
| 网络错误       | 检查网络连接，重试                    |
| 仓库不存在     | 检查仓库地址是否正确                  |
| 权限不足       | 配置 git 认证（SSH key 或 Token）     |
| 不在 git 仓库中| 使用当前目录作为项目根目录            |

## 注意事项

1. 确保有权限访问规约仓库（配置 SSH key 或 Personal Access Token）
2. 默认不覆盖已存在的目录，会询问用户选择
3. 使用 `--depth=1` 浅克隆减少下载量
4. 执行完毕后自动清理临时目录

// turbo-all
