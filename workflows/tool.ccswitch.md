---
description: 使用 CC Switch 参考已有 Claude Code 供应商生成、切换和验证 Codex 供应商，并按配置、认证、协议、路由和流式连接分层排障。
---

# CC Switch：从 Claude Code 生成 Codex 供应商

用户要求参考已有 Claude Code 供应商生成 Codex 对应配置、接入 Sub2API 等中转服务、切换 Codex 供应商，或排查切换后 Codex 无法启动、无法进入、误走 ChatGPT 认证和流式断连时使用。

本工作流的首要职责是生成可持久切换的 Codex 供应商配置；故障预防和排障是次级流程。普通 Codex 官方产品问题仍按 `openai-docs` 处理，本工作流只负责 CC Switch 与 Codex 自定义供应商的交界。

## 0. 核心不变量

- CC Switch 中持久化的供应商记录是切换行为的源配置，活动 `config.toml` 是切换生成结果。手工修活动文件后再次切换会复发时，必须回到 CC Switch 供应商或通用配置修复。
- Claude Code 与 Codex 的客户端协议不同，禁止把 Claude provider JSON、环境变量或 URL 原样复制成 Codex TOML。必须先识别真实上游协议，再决定直连还是本地路由。
- Codex 对外层始终使用 Responses 形态；即使真实上游是 OpenAI Chat Completions 或 Anthropic Messages，Codex 配置仍保持 `wire_api = "responses"`，由 CC Switch 根据 `meta.apiFormat` 决定是否转换。
- API Key、Token、Cookie 和登录凭据不得出现在预览、命令回显、补丁、日志摘录或最终交付中。只能确认字段是否存在、长度或脱敏摘要。
- 正常新增或编辑供应商必须通过 CC Switch 表单完成。允许只读查询 SQLite、活动配置和日志定位事实，禁止直接改 SQLite 绕过应用校验。
- 模型 ID、上下文窗口、推理档、最大输出、图片能力和工具能力必须来自供应商文档、真实模型接口、已验证配置或用户确认，禁止按名称猜测。
- 切换可能让当前 Codex 任务立即失去回复能力。切换前必须先给出“切回官方供应商 → 完全退出并重启 Codex → 回到原任务”的恢复路径。

## 1. 引用读取路由

- 生成、转换、复制或校验 Codex 供应商时，必须完整读取 [Codex 供应商生成](references/tool-ccswitch--codex-provider-generation.md)。
- 只有出现启动失败、登录页、Windows 设置页、HTTP 4xx、ChatGPT 账号限制、再次切换复发、流式中断或当前任务无法继续时，才完整读取 [故障预防与分层排障](references/tool-ccswitch--troubleshooting.md)。
- 两类场景同时出现时先完成生成引用中的配置事实表，再读取排障引用；禁止一看到错误就跳过配置来源核对。

## 2. 前置只读确认

1. 确认当前 CC Switch 版本、实际数据目录、数据库文件、Codex 配置目录和活动 `config.toml`。路径必须来自应用设置、当前进程、环境变量或已验证文件，不得套用其他电脑的固定路径。
2. 确认作为来源的 Claude Code 供应商，以及准备创建或修复的 Codex 供应商。相同名称不代表同一条记录，必须以应用类型和 provider ID 区分。
3. 脱敏提取 Claude 供应商中的 Base URL、凭据字段类型、上游协议、默认模型和角色模型候选；只记录是否存在，不输出真实凭据。
4. 核对上游服务真实支持的接口格式和模型 ID。Claude Code 能调用成功只能证明 Claude 链路可用，不能证明同一 URL 原生支持 Codex Responses。
5. 读取当前 CC Switch 源码、发布说明或应用表单行为，确认本版本的 `apiFormat`、路由接管、凭据注入和“保留官方登录”语义。版本事实不一致时，以当前版本为准并说明旧基线已失效。

## 3. 生成 Codex 供应商

1. 建立“来源字段 → Codex 字段 → 依据 → 是否已确认”的脱敏映射表，先确认协议和认证头，再生成配置。
2. 根据上游协议选择：
   - 原生 OpenAI Responses：允许直连上游。
   - OpenAI Chat Completions：使用 CC Switch 本地路由做 Responses ↔ Chat 转换。
   - Anthropic Messages：使用 CC Switch 本地路由做 Responses ↔ Anthropic 转换，并确认当前版本支持该能力。
3. 生成 CC Switch 表单草案：供应商名称、API Key 输入位置、上游 Base URL、默认模型、上游格式、认证字段和已确认的可选模型目录。未确认字段保持空白或标为待确认，不得补默认值伪装完整。
4. 生成最小 Codex TOML 草案，只包含已确认的模型、provider、名称、Base URL 和 `wire_api = "responses"`。API Key 不写入预览；`requires_openai_auth` 交给当前 CC Switch 按凭据和“保留官方登录”策略生成，不机械写死或翻转。
5. 通过 CC Switch 的 Codex 页签创建或编辑供应商并保存。Chat / Anthropic 上游同时开启本地路由和 Codex 接管；Responses 上游根据当前表单和网络需求选择直连或路由，不因“使用了 CC Switch”就强制接管。
6. 保存后只读复查供应商记录：应用类型、provider ID、`meta.apiFormat`、Base URL、默认模型、凭据存在性和可选模型目录必须与草案一致。

## 4. 切换与持久化验证

1. 切换前记录当前官方供应商名称、恢复路径和活动配置的脱敏摘要；禁止备份或展示真实 Key。
2. 在 CC Switch 中启用目标 Codex 供应商。需要路由的供应商必须同时确认路由服务已启动、Codex 已接管且当前 Provider 能命中目标记录。
3. 完全退出并重新启动 Codex，禁止只关闭当前任务页后假定配置已热加载。
4. 先创建新任务发送短请求，再检查模型列表；新任务通过后才回到原任务验证，避免把旧任务绑定、远程压缩或历史上下文问题误判成供应商基础配置失败。
5. 继续验证长流式响应、工具调用、图片输入和二次切换。涉及 Desktop 远程压缩、云任务或 ChatGPT 账号能力时单独登记结果，不得用普通自定义请求成功替代验证。
6. 切回官方供应商并重启一次，再切回目标供应商复测。手工修复只有在二次切换后仍然有效，才算持久化完成。

## 5. 验收门禁

只有同时满足以下条件才可宣布完成：

- 来源 Claude 供应商与目标 Codex 供应商的字段映射有可追溯依据，未泄露真实凭据。
- 上游协议已确认；Chat / Anthropic 上游确实走本地路由，Responses 上游的直连或接管选择有依据。
- Codex provider 的外层 `wire_api` 为 `responses`，真实上游格式保存在 CC Switch `meta.apiFormat`。
- CC Switch 供应商记录、切换后活动配置和当前路由 Provider 三者一致。
- 完全重启后的新任务短请求、模型列表和长流式请求均已验证，或明确列出尚未验证项。
- 切回官方再切回目标后配置仍然有效；不存在依赖后台脚本持续重写活动配置的临时修复。
- 配置中不存在无依据的模型能力、无效 Schema 字段或把 `max_concurrent_threads_per_session` 写成 `0` 的条目。

## 6. 交付格式

最终交付必须包含：

- 来源供应商、目标供应商、上游协议和认证字段的脱敏映射结果。
- CC Switch 表单填写项和最小 Codex TOML；所有凭据使用 `<redacted>` 或“已配置”表示。
- 是否需要本地路由、Codex 接管和完全重启，以及选择依据。
- 新任务、原任务、模型列表、长流式请求、官方往返切换和 Desktop 远程能力的验证结果。
- 未确认的模型、上下文、推理档、最大输出或上游限制。
- 失败时的准确错误文本、所属层级、已排除项和下一步；禁止只回复“配置不对”或“网络问题”。
