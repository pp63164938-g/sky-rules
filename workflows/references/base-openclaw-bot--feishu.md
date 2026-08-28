# 飞书 OpenClaw 机器人基线

## 访问策略

用户已确认当前共享 OpenClaw 实例默认采用以下策略：

```json5
{
  channels: {
    feishu: {
      dmPolicy: "pairing",
      groupPolicy: "open",
      requireMention: true
    }
  }
}
```

- 私聊使用 `pairing`：未知用户进入配对流程，不允许静默丢弃。
- 群聊使用 `open`：机器人加入任何群后，无需登记群 Chat ID。
- `requireMention: true`：只有直接 @ 机器人时才响应；`@所有人` 不等于直接 @ 机器人。
- `groupAllowFrom` 在此基线下应删除，避免残留配置误导维护者。
- `allowFrom` 若因兼容保留，只允许用户 Open ID（`ou_...`）或通配符 `*`。
- 群 Chat ID 使用 `oc_...`；不得把用户 Open ID（`ou_...`）写入群 ID 位置。

## 作用范围与安全边界

`channels.feishu.dmPolicy`、`groupPolicy` 和 `requireMention` 是飞书通道全局策略，不是单个 Account 策略。修改会影响同一实例中的全部飞书机器人。

公开资讯和知识问答机器人使用上述基线。若新增能访问财务、隐私、生产写入或服务器管理能力的敏感机器人，不要静默收紧全部机器人；应优先评估独立 OpenClaw 实例、独立配置或明确的群内发送者限制，并由用户确认隔离方案。

## 飞书后台模板清单

飞书开放平台没有保证能完整复制应用配置的通用模板，因此每个新应用按下列清单验收：

1. 启用机器人能力。
2. 开通当前 OpenClaw 版本文档要求的消息收发权限。
3. 订阅 `im.message.receive_v1`。
4. 使用长连接接收事件，或采用当前实例已验证的连接方式。
5. 发布新版本，应用可用范围包含测试用户。
6. 把机器人加入目标群，确认群内能直接 @ 到机器人。

## OpenClaw 新机器人清单

1. Account 的 App ID 与飞书应用一致，秘密字段已安全写入且未回显。
2. Agent ID、Account ID、Binding 和 Workspace 对应同一机器人。
3. Workspace 中存在该机器人的 `AGENTS.md`、`SOUL.md` 和所需业务 Skill。
4. 全局共享 Skill 能被 OpenClaw 发现，但内部 Agent 不具备自改全局配置和密钥的权限。
5. OpenClaw Schema 校验与仓库校验器均通过。
6. 私聊和新群直接 @ 的端到端测试均有日志证据。

## 常见失败与定位顺序

- 日志出现 `group ... not in groupAllowFrom`：群策略仍是 `allowlist`，或旧群白名单尚未清理。
- 私聊完全无反馈：检查 `dmPolicy`、配对状态、应用可用范围和事件是否到达网关。
- 飞书没有入站日志：检查机器人是否加入会话、事件订阅、长连接、权限和应用发布状态。
- 入站日志存在但路由到错误 Agent：检查 Account ID 与 Binding。
- 网关已连接但无回复：检查 Agent 执行日志、模型调用和 Workspace，不要直接归因于飞书。
- 新电脑没有本 Skill：确认已克隆 `sky-rules`，运行同步脚本，并用 Codex 的 Skill 列表或模型输入诊断确认实际加载。

## 共享 Skill 部署布局

以目标 OpenClaw 实际文档和 `openclaw skills` 诊断为准，推荐布局：

```text
~/.openclaw/skills/base-openclaw-bot/
├── SKILL.md
├── references/
│   └── base-openclaw-bot--feishu.md
└── scripts/
    └── validate-openclaw-feishu-config.py
```

VPS 目录是部署产物，不是规则源。更新时从 `sky-rules` 重新生成和覆盖，并在覆盖前后核对文件摘要。
