# CC Switch：Codex 供应商生成

本引用用于把一个已经可用的 Claude Code 供应商转换为 CC Switch 中可持久切换的 Codex 供应商。目标是复用同一上游服务和凭据，不是复制 Claude 客户端配置文本。

## 目录

- [1. 当前实现事实与失效信号](#1-当前实现事实与失效信号)
- [2. 先建立脱敏配置事实表](#2-先建立脱敏配置事实表)
- [3. 协议选择](#3-协议选择)
- [4. 字段生成规则](#4-字段生成规则)
- [5. 最小配置草案](#5-最小配置草案)
- [6. CC Switch 供应商新增与编辑](#6-cc-switch-供应商新增与编辑)
- [7. 生成结果验证表](#7-生成结果验证表)

## 1. 当前实现事实与失效信号

本基线于 2026 年 9 月 4 日根据 CC Switch 当前源码和发布说明核实，关键事实来源包括：

- `src/components/providers/forms/ProviderForm.tsx`：Codex 保存 `meta.apiFormat`，并在表单切换协议时保持 `wire_api = "responses"`。
- `src/utils/providerCapabilities.ts`：Codex 的 OpenAI Chat 和 Anthropic 上游需要路由，原生 Responses 可直连。
- `src-tauri/src/codex_config.rs`：第三方凭据注入、`requires_openai_auth` 对齐、活动配置预检和保留官方登录行为。
- `docs/guides/codex-claude-routing-guide-zh.md`：Anthropic Messages 路由链路；该能力要求 CC Switch 3.17.0 及以上。
- `docs/release-notes/v3.20.1-zh.md`：Codex CLI 0.149 之后的第三方 config-only 凭据策略。

出现以下任一信号时，本引用中的版本事实视为可能失效，必须重新读取当前 CC Switch 源码、发布说明或表单实际行为：

- `apiFormat` 可选值、路由标记或 Codex 高级选项发生变化。
- 第三方 Key 不再写入 provider 级 `experimental_bearer_token`，或“保留官方登录”开关语义变化。
- Codex 原生支持新的上游协议，不再要求 Responses 外层。
- CC Switch 切换后的活动配置与本引用描述不同，但应用校验和请求实际成功。

## 2. 先建立脱敏配置事实表

从 CC Switch 数据库、导出配置或编辑表单中只读提取来源 Claude 供应商。不得输出整条 JSON、数据库记录或真实凭据。

| 来源事实 | 常见来源字段 | 目标用途 | 处理要求 |
| --- | --- | --- | --- |
| 上游地址 | `ANTHROPIC_BASE_URL`、表单 Base URL | Codex 供应商的上游 Base URL | 核对是否为服务根地址、带 `/v1` 的根地址或完整接口 URL |
| 上游凭据 | `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_API_KEY` | CC Switch Codex 表单的 API Key | 只确认存在性；禁止回显值 |
| 真实协议 | `meta.apiFormat`、供应商文档、已验证请求路径 | `meta.apiFormat` 与路由选择 | Claude 可用不等于 Responses 可用，必须单独确认 |
| 默认模型 | `ANTHROPIC_MODEL`、Claude 表单默认模型 | Codex `model` | 必须是上游实际接受的模型 ID |
| 角色模型候选 | `ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL` | Codex 模型目录候选 | 只作为候选，去重并逐项确认可调用性 |
| 认证头 | Claude provider 的 Key 字段或网关文档 | Anthropic 路由的认证字段 | Bearer 与 `x-api-key` 不得同时猜测 |
| 完整 URL 模式 | `meta.isFullUrl` 或表单开关 | 路由如何拼接路径 | 仅当上游文档给出完整接口 URL 时启用 |

事实表必须明确区分：

- **已确认值**：来自当前 CC Switch 记录、上游文档、真实请求或用户明确确认。
- **候选值**：来自 Claude 的角色模型配置，但尚未在 Codex 链路验证。
- **不可迁移项**：Claude 专属的权限、客户端行为、系统提示、环境变量或 Beta 头，不能因为来源 provider 有值就复制到 Codex。

## 3. 协议选择

先确定真实上游协议，再写入 Codex 供应商记录。

| 上游格式 | CC Switch `meta.apiFormat` | Codex 外层 `wire_api` | 是否需要本地路由 | 活动配置的 Base URL |
| --- | --- | --- | --- | --- |
| OpenAI Responses | `openai_responses` | `responses` | 通常不需要 | 上游地址；若用户主动接管则按当前路由生成 |
| OpenAI Chat Completions | `openai_chat` | `responses` | 需要 | CC Switch 当前本地路由地址 |
| Anthropic Messages | `anthropic` | `responses` | 需要 | CC Switch 当前本地路由地址 |

关键判断：

- 上游文档或实测存在 `/responses`，且请求/流式事件符合 OpenAI Responses，才可选择 `openai_responses`。
- 只有 `/chat/completions` 或明确写 OpenAI Chat 兼容时，选择 `openai_chat`，由本地路由转换。
- 只有 `/v1/messages` 或明确写 Anthropic Messages 时，选择 `anthropic`。直接把该上游地址交给 Codex 会请求 `/responses` 并产生 404。
- 来源 Claude provider 的 `meta.apiFormat` 是强线索，但旧数据可能缺失或被用户改动；最终以当前上游契约和真实请求为准。
- 不得仅因来源 Claude 的 `meta.apiFormat` 选择 Codex 上游格式。同一 Base URL 已实测存在可用的 `/responses` 时，应优先按实测选择 `openai_responses`。
- 路由模式下，CC Switch 供应商记录保存真实上游地址；切换生成的活动 `config.toml` 指向本机路由。两者不同是正常设计，不得把本机路由地址反写成上游地址。

## 4. 字段生成规则

### 4.1 供应商名称和 ID

- 名称由用户确认，建议能区分来源服务和应用类型，但不要自行添加会误导协议或计费归属的名称。
- provider ID 使用 CC Switch 生成或经当前版本校验的 ID。直接新增时按当前版本自定义 Codex 记录的 ID 形态生成新 ID；当前 3.20.1 使用 UUID。禁止占用空名残留卡、内置 ID 或其他 provider 的现成 ID，除非用户明确要求复用。
- 同名 Claude 和 Codex 记录必须继续按应用类型分开，不得把 Claude 记录直接改成 Codex 记录。

### 4.2 Base URL

- 默认从来源 Claude provider 的已验证上游地址迁移，但必须先确认路径语义。
- 服务根地址或 `/v1` 根地址按 CC Switch 当前供应商字段规则填写。
- 来源是完整 `/v1/messages`、`/chat/completions` 等接口 URL 时，只有当前版本支持且已启用“完整 URL”模式才原样迁移。
- 禁止为了让错误消失而在末尾轮流拼接 `/v1`、`/responses`、`/chat/completions` 或 `/messages`。每次路径变化必须有文档、表单语义或路由日志依据。

### 4.3 API Key 与认证字段

- 来源存在 `ANTHROPIC_AUTH_TOKEN` 时，Anthropic 路由通常对应 `Authorization: Bearer`；来源存在 `ANTHROPIC_API_KEY` 时，通常对应 `x-api-key`。仍须以当前 provider 或网关文档为准。
- 两个来源字段同时存在时，先确认 Claude 当前实际使用哪个字段，禁止按变量名优先级自行选一个。
- API Key 只写入持久化供应商凭据字段，不写入工作流输出、TOML 预览或 Git 文件。
- 当前 CC Switch v3.20.1 的直接第三方切换会把 Key 注入活动 provider 表的 `experimental_bearer_token`，不再依赖 `auth.json` 传递第三方 Key；路由接管则由本地路由向上游注入。只读检查时必须把该字段值脱敏。

### 4.4 默认模型与模型目录

- `model` 只使用已确认能被上游调用的精确 ID；展示名称不能替代模型 ID。
- Claude 的 Opus / Sonnet / Haiku 角色模型只能作为目录候选，不自动等同于 Codex 的默认模型。
- 用户明确指定默认模型时，按用户指定写入；用户只给出口语名或简写时，先对照目标上游模型列表解析成真实 ID，并在结果中说明解析。
- 用户未指定默认模型时，使用本次推荐值：优先用来源供应商已验证且目标上游存在的主模型；否则留空并在结果中标明待确认。推荐值必须写入结果，不得静默改口。
- 不同上游的同名口语模型可能对应不同精确 ID。必须以目标上游模型列表为准，禁止把另一张供应商卡或另一上游的 model 字符串原样搬过来。
- 模型目录可包含多个已确认模型，供 Codex 模型选择器使用；未配置目录不影响默认模型直接调用，但模型可能不会出现在列表中。
- 上下文窗口、最大窗口、推理档、最大输出、输入模态和工具能力必须逐模型有依据。没有依据时留空，禁止复制另一个模型或按家族名称推断。
- 不要把同一个模型分别伪装成多个能力不同的条目来迁就 UI；模型能力应来自真实上游。

### 4.5 `requires_openai_auth` 与保留官方登录

- 不把 `requires_openai_auth = true/false` 当成固定模板字段，也不通过机械翻转它解决全部认证问题。
- 当前 CC Switch v3.20.1 会根据第三方 provider 是否有自有凭据，以及“非接管切换时保留官方登录”开关，重写活动 provider 表上的该值；手工值可能在下一次切换时被覆盖。
- 开启保留官方登录表示第三方切换时不删除官方 ChatGPT 登录；关闭时当前版本删除 `auth.json`，而不是把第三方 Key 写进去。
- 即使普通自定义请求使用第三方 provider，Codex Desktop 的远程压缩、云任务或其他账号能力仍可能走 ChatGPT 账号路径。是否受 ChatGPT 额度或模型支持限制必须按具体操作单独验证。

### 4.6 禁止复制的配置

除非当前 Codex Schema、CC Switch 表单和用户需求均有明确依据，不从 Claude provider 或其他历史配置复制以下内容：

- `[agents]` 和线程并发设置，尤其禁止生成 `max_concurrent_threads_per_session = 0`。
- Claude 专属环境变量、系统提示、权限模式、Hooks、MCP 或客户端模拟头。
- 其他 provider 的模型目录、上下文窗口、推理档和工具声明。
- 无依据的 `requires_openai_auth`、`env_key`、`auth`、`aws` 或顶层 `openai_base_url` 兼容配置。

## 5. 最小配置草案

向用户预览时只给出无密钥的最小结构：

```toml
model = "<confirmed-model>"
model_provider = "<provider-id>"

[model_providers.<provider-id>]
name = "<provider-name>"
base_url = "<confirmed-upstream-base-url>"
wire_api = "responses"
```

同时在配置说明中单独标注：

```text
CC Switch 上游格式：openai_responses | openai_chat | anthropic
API Key：已配置，不展示
认证字段：Authorization Bearer | x-api-key | 不涉及
本地路由：需要 | 不需要
保留官方登录：按用户当前选择
```

注意：Chat / Anthropic 路由启用后，活动 `config.toml` 的 `base_url` 应由 CC Switch 改成当前本地路由地址；上面的上游地址仍保存在 CC Switch provider 中供路由转发。

## 6. CC Switch 供应商新增与编辑

目标是把已确认草案落到 CC Switch 的 Codex 供应商记录。表单 GUI、桌面控制和活动 `config.toml` 都不是源配置。

### 6.1 路径选择

1. 用户要求参考某个已有供应商、同步到 Codex、新增或修改对应供应商时，默认直接新增或定点编辑持久化记录。
2. 不要求用户先建空卡；桌面控制表单只在 GUI 可用且用户明确要求时作为备选。
3. 禁止把活动 `config.toml` 写成新供应商；下次切换会覆盖。
4. 禁止占用空名残留卡或其他 provider 的现成行，除非用户明确要求复用该 ID。
5. 官方导入链接若需要把 API Key 放进命令行参数，则不得使用。
6. 来源协议、上游地址和模型 ID 已有当前证据时，禁止再做一轮全量探测；只在协议未知或请求的模型 ID 与上游列表冲突时补最小核对。

### 6.2 新增

1. 先备份当前 CC Switch 数据库到应用 backups 目录。
2. 只读确认来源供应商，以及目标 Codex 名称尚未占用。
3. 按当前版本 schema 插入新的 Codex 行：新 ID、`app_type=codex`、已确认名称 / Base URL / 最小 TOML / 凭据字段 / `meta.apiFormat`。当前 3.20.1 自定义 Codex 记录使用 UUID。
4. `is_current` 保持 0，除非用户明确要求切换。
5. 只写入最小 Codex TOML 和必要 meta；禁止复制当前启用供应商的 projects、MCP、plugins、personality、sandbox 快照。
6. 凭据从已确认来源字段复制到 Codex `OPENAI_API_KEY`，只记录存在性、长度或脱敏摘要。

### 6.3 编辑

1. 先备份，再按 `app_type` 与 provider ID 定位目标行；名称只作核对，不能单独当作唯一键。
2. 只更新用户要求的字段，例如默认模型、Base URL、协议或凭据。
3. 未要求切换时不得改 `is_current`，也不得重写活动 `config.toml`。
4. 目标行若正在启用，必须说明活动配置要等重新启用或完全重启后才会变化。

### 6.4 字段与复查

1. Anthropic 上游按来源 provider 或网关文档选择 `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_API_KEY` 对应认证字段。
2. “模拟 Claude Code 客户端”默认关闭；只有上游明确限制客户端且用户同意时才开启。开启后仍被拒说明限制可能在服务端，不继续堆伪装头。
3. “最大输出 tokens”只在 Anthropic 路由且模型真实上限已确认时填写；不确认时保留默认并将截断验证列为待测。
4. 模型映射只加入已确认模型；逐项填写真实能力，不复制来源 Claude provider 中未验证的角色模型能力。
5. Chat / Anthropic 上游开启本地路由总开关和 Codex 接管。记录当前实际监听地址，不把默认端口当成永久事实。
6. 保存后只读复查：应用类型、provider ID、名称、`meta.apiFormat`、Base URL、默认模型、凭据存在性没有串到其他 provider。
7. CC Switch 正在运行时，界面可能仍是内存缓存；需要用户重新打开应用查看新卡，但不能因此去 Enable。
8. 默认模型：用户指定则按用户指定；未指定则使用本次推荐值。口语名先解析成上游真实 ID。
9. 同步完成后必须输出结果，不得只写“已保存”。

## 7. 生成结果验证表

| 验证项 | 预期结果 | 失败时归属 |
| --- | --- | --- |
| Provider 持久化记录 | Codex 应用、ID、协议、上游地址和模型均正确 | CC Switch 供应商记录持久化 |
| 活动 TOML 可解析 | Codex 启动时无 `config_load` Schema 错误 | Codex 配置生成 |
| Responses 直连 | 活动 Base URL 指向真实上游，请求命中 `/responses` | 上游协议 / 认证 |
| Chat / Anthropic 路由 | 活动 Base URL 指向本地路由，路由当前 Provider 命中目标供应商 | 路由接管 / provider 选择 |
| 新任务短请求 | 返回成功且计入目标 provider | 基础配置 |
| 模型列表 | 只出现已配置目录；默认模型可直接调用 | 模型目录 |
| 官方往返切换 | 切回再切回后仍成功 | 持久化源配置 |

生成阶段发现任何失败时，不继续试填更多无依据字段。保留当前事实表并转入 `tool-ccswitch--troubleshooting.md` 对应层级。
