---
description: 连接服务器创建、扩展、修复或验收接入飞书的 OpenClaw 机器人，并按统一基线处理 Account、Agent、Binding、Workspace、私聊配对、群聊 @、白名单和共享 Skill。
---

# 飞书 OpenClaw 机器人

用户提出新增、复制、重命名、部署或排查飞书 OpenClaw 机器人，或要求把流程模板化时使用。本工作流负责基础设施和接入闭环，不代替机器人的业务人格与知识规则。

## 0. 最高优先级原则

- 使用 `base-server` 连接目标 VPS；先读取当前版本的 OpenClaw 文档、配置 Schema 和真实日志，禁止凭历史经验猜字段。
- App Secret、模型密钥、Token 等秘密只能写入目标配置或受限临时文件，不得出现在终端回显、日志摘录、补丁、对话或最终交付中。
- OpenClaw 内部 Agent 只允许执行只读检查、生成脱敏诊断和交接清单；不得修改自身全局配置、密钥、Binding 或网关状态。全局变更必须由外部基础设施执行者完成。
- 修改前创建带时间戳的配置备份；校验失败时禁止重载网关或宣布完成。
- 配置写入、网关重载和飞书外部消息均属于有影响操作，只在用户明确要求创建、修复或应用已确认方案时执行。

## 1. 必读基线

执行前完整读取 [references/base-openclaw-bot--feishu.md](references/base-openclaw-bot--feishu.md)。如果当前 OpenClaw 版本与基线冲突，以当前版本的官方文档、Schema 和实际行为为准，先说明差异，再决定是否更新本仓库基线。

## 2. 前置确认

1. 确认机器人名称、职责、Agent ID、飞书 App ID，以及需要写入新 Workspace 的 `AGENTS.md`、`SOUL.md` 和业务 Skill。
2. 只读检查 OpenClaw 版本、活动配置文件、Accounts、Agents、Bindings、Workspace、共享 Skills、网关状态和飞书通道日志。
3. 判断任务是新增、幂等补全还是故障修复；相同 App ID、Account ID、Agent ID 或 Binding 已存在时不得重复创建。
4. 检查飞书后台前提：机器人能力、消息权限、`im.message.receive_v1`、长连接订阅、可用范围和已发布版本。无法访问后台时，明确列出用户需要完成的页面操作，不得写成已验证。

## 3. 执行步骤

1. 备份活动配置，并记录备份路径和恢复命令；备份内容不得带回对话。
2. 优先使用当前版本提供的配置命令写入；只有文档和 Schema 明确时才编辑配置文件。
3. 应用用户已确认的飞书访问基线，清理与基线冲突的旧白名单。全局策略会影响同一实例中的全部飞书 Accounts，必须在实施前显性告知。
4. 创建或补全 Account、Agent、Binding 和 Workspace。沿用当前实例的真实目录、模型、身份和路由结构，不复制其他机器人的人格或长期记忆。
5. 把机器人业务规则放入其 Workspace；把跨机器人创建流程放入全局共享 Skill，禁止混淆两者归属。
6. 使用权限为 `600` 的临时文件或实例现有的秘密引用机制写入秘密；完成后立即删除秘密临时文件。
7. 先运行 OpenClaw 自带配置校验，再运行仓库 `scripts/validate-openclaw-feishu-config.py`。通过 `~/.sky-rules/local.json` 或当前仓库根目录定位脚本，禁止复制后长期维护第二份本地源文件。
8. 校验通过后重载网关，检查通道连接和目标 Account 日志。
9. 要求用户完成一次私聊和一次新群直接 @ 测试；日志必须证明消息到达、路由到目标 Agent 并产生回复。
10. 清理诊断和秘密临时文件，输出已验证、待用户后台操作、待端到端测试三类结论。

## 4. 跨电脑与 VPS 复用

- `sky-rules` Git 仓库是唯一源文件。新电脑先克隆仓库，再运行 `python sync-workflows.py --no-git` 生成 `~/.codex/skills/base-openclaw-bot/`。
- VPS 的 OpenClaw 共享入口使用当前实例实际加载的全局 Skills 目录，通常是 `~/.openclaw/skills/base-openclaw-bot/`。部署时由本仓库主工作流生成 `SKILL.md`，并复制对应引用与校验器；不得在 VPS 上单独演进规则。
- 更新本工作流后重新同步 Codex，并重新部署 VPS 共享 Skill；VPS 版本应记录源仓库提交或文件摘要，便于检查漂移。

## 5. 验收门禁

只有同时满足以下条件才可宣布机器人创建完成：

- OpenClaw 配置通过当前版本 Schema 校验和仓库校验器。
- Account、Agent、Binding 一一对应，无重复或冲突路由。
- Workspace、`AGENTS.md`、`SOUL.md` 和业务 Skill 归属正确。
- 网关和目标飞书 Account 已连接。
- 未知私聊用户能进入配对流程，不会静默丢弃。
- 机器人在未登记的新群中只在被直接 @ 时响应。
- 日志不存在 `not in groupAllowFrom`、错误 Agent 路由或秘密泄露。

如果飞书后台权限、发布或人工测试尚未完成，只能写“基础设施配置已完成，端到端验收待完成”。

## 6. 交付格式

最终交付必须包含：

- 新增或修复的 Account、Agent、Binding、Workspace 和共享 Skill；秘密字段全部脱敏。
- 配置备份位置、校验结果、网关状态和端到端测试结果。
- 飞书后台仍需用户完成的操作。
- 当前访问基线及其全局影响范围。
- 失败时的恢复路径和仍未验证的风险。
