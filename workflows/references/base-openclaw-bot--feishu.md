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

公开资讯机器人的工具与 Skill 权限仍须按职责收敛。实例能够执行服务器命令，不代表每个 Agent 都应获得服务器体检、配置写入、网关控制或秘密读取能力；业务 Skill 需要执行脚本时，只开放对应的受限入口和必要网络能力。专用 Agent 使用当前 Schema 明确支持的 `agents.list[].skills` 设置完整允许列表，避免无关运维、配置和其他业务 Skill 进入模型上下文。

## 空 @ 与输入状态

- 群内直接 `@` 机器人但没有文字时，通道层只负责生成通用请求：按当前 Workspace 定义的空 `@` 行为执行；若 Workspace 未定义，则简短询问用途。
- 具体默认动作写在每个机器人的 `AGENTS.md`，例如资讯机器人可以定义为执行当天资讯检查。禁止在共享适配器、补丁或服务文件中写死 Account ID、机器人名或业务问题。
- 空 `@` 兼容实现必须具备幂等检查和版本失效信号。OpenClaw 或飞书插件升级后目标代码结构变化时，应拒绝自动修改并重新核对当前版本，禁止模糊替换构建产物。
- `typingIndicator` 必须显式启用并通过真实消息验证。Schema 默认值、配置文件存在或权限列表看起来完整，都不能代替“收到消息后出现、最终回复后清除”的端到端证据。

## 定时任务与网关维护

- 创建机器人前同时列出 OpenClaw Cron 和同一用户的 systemd Timer。凡会重启、刷新或停止网关的维护任务，都必须避开业务任务从开始时间到 `timeoutSeconds` 的完整运行窗口。
- 维护脚本必须在重启前检查当前是否存在活动 Cron、Agent Run 或业务子进程；存在活动任务时记录 `DEFERRED` 并退出，由 Timer 稍后重试。禁止为了固定刷新时间打断在途任务。
- 使用 `scripts/validate-openclaw-schedule-collisions.py` 对简单日历计划做自动检查；脚本无法解析的复杂日历必须进入人工复核，不能视为无冲突。
- 长耗时业务任务必须提供单一确定性入口。该入口负责互斥、超时、有限重试、临时文件清理、状态推进和人类可读错误；当前 OpenClaw Schema 支持 `command` / `commandArgv` 时，Cron 直接调用入口，不再经过模型。只有当前版本不支持命令任务时，Cron Agent 才执行一次入口并原样返回标准输出。
- 禁止在 Cron 提示中让模型自行使用后台命令、`sleep`、`ps | grep`、PID 终止、并发重跑或临时拼接运行清单。这些操作会把正常进程结束误判为失败，并可能造成重复采集和技术错误外泄。
- 重载网关后必须用有上限的轮询同时检查 systemd 服务状态与 `/readyz` 等当前版本健康接口。禁止固定等待几秒后只请求一次；服务仍在启动时出现的短暂 `connection refused` 应继续轮询，超过明确上限仍未就绪才判定失败并读取日志。

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
3. Workspace 中存在该机器人的 `AGENTS.md`、`SOUL.md` 和所需业务 Skill；`AGENTS.md` 明确空 `@` 默认行为或明确退回询问。
4. 全局共享 Skill 能被 OpenClaw 发现，但专用 Agent 通过显式 `agents.list[].skills` 只加载职责所需 Skill，且不具备自改全局配置和密钥的权限。
5. `typingIndicator` 显式为 `true`，并有真实消息上的出现与清除证据。
6. OpenClaw Schema、仓库配置校验器和 Cron/Timer 冲突校验器均通过；专用机器人已用重复的 `--agent-skill` 验证完整 Skill 白名单，用 `--require-tool` / `--forbid-tool` 验证显式 `tools.allow`，不会继承无关 Skill 或高权限工具。
7. 模型鉴权冒烟测试成功，不存在 401、模型不存在或上游超时。
8. 私聊、群内带文字直接 `@`、群内空 `@` 的端到端测试均有日志证据；`skills list --agent <Agent ID> --eligible --json` 或模型运行报告只出现预期业务 Skill。
9. 每个定时任务都完成受控试跑：单入口、单实例、无更新静默、有更新投递、错误可读且不泄露内部命令。
10. 网关重载使用有界健康轮询完成验收，没有把启动期间的一次连接拒绝误报为部署失败。

## 常见失败与定位顺序

- 日志出现 `group ... not in groupAllowFrom`：群策略仍是 `allowlist`，或旧群白名单尚未清理。
- 私聊完全无反馈：检查 `dmPolicy`、配对状态、应用可用范围和事件是否到达网关。
- 飞书没有入站日志：检查机器人是否加入会话、事件订阅、长连接、权限和应用发布状态。
- 入站日志存在但路由到错误 Agent：检查 Account ID 与 Binding。
- 网关已连接但无回复：检查 Agent 执行日志、模型调用和 Workspace，不要直接归因于飞书。
- 部署脚本报告 `connection refused` 但稍后网关正常：检查是否只做了固定延时后的单次健康请求；改为有上限的服务状态与健康接口联合轮询，再依据超时结果判断。
- 首次消息没有任何回复且日志出现 401：先修复模型凭据并重新做模型冒烟，不要继续调整飞书白名单。
- 只有空 `@` 没反应：检查通道空消息处理是否仍跳过、共享兼容层是否因版本升级失效，以及 Workspace 是否定义默认行为；禁止为每个 Account 复制一份硬编码补丁。
- 回答混入其他机器人能力或无关操作说明：检查专用 Agent 是否遗漏 `agents.list[].skills`，以及运行报告中是否注入了预期外 Skill；不要只限制工具后仍让全部 Skill 进入提示词。
- 没有输入状态：显式检查 `typingIndicator`、消息 Reaction 权限和运行日志；配置默认开启不等于飞书端已生效。
- 定时任务出现 `interrupted by gateway restart`：对照 OpenClaw Cron 与 systemd Timer 的完整运行窗口，修复维护冲突并增加活动任务延后。
- 结果中出现 `run python`、`ps aux`、PID 或内部路径：定时任务仍由模型管理进程，应改成单一确定性入口并原样返回标准输出。
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
