# 全局规则维护索引

`rules/` 用于维护跨项目、跨 AI 工具通用的规则正文。规则源文件按 `common/`、`frontend/`、`backend/`、`projects/` 拆分，`sync-workflows.py` 会按 `rules/rules-manifest.json` 的顺序拼接为各 AI 工具实际读取的完整全局规则。

## 文件职责

| 文件 / 目录 | 职责 |
| --- | --- |
| `global-rules.md` | 常驻入口，只放核心理念、P0 红线、场景索引、示例要求等高优先级内容 |
| `rules-manifest.json` | 全局规则拼接清单，决定同步到各 AI 工具的规则顺序 |
| `common/` | 前端、后端和其他开发任务都必须遵守的通用规则 |
| `frontend/` | 前端专属规则，约束 Vue、组件、Hook、样式、UI、路由、i18n、Icon 等 |
| `backend/` | 后端专属规则，约束接口实现、服务分层、数据库、鉴权、安全、任务、缓存、日志等 |
| `projects/` | 项目专属规则，只放特定项目需要遵守的补充规则 |
| `../scripts/check-rules.py` | 规则仓库自检脚本，检查 manifest、索引、拼接结果和同步产物 |

## 规则文件索引

| 文件 | 主题 | 适用内容 |
| --- | --- | --- |
| `global-rules.md` | 常驻入口与 P0 红线 | 核心理念、规则读取策略、P0 硬性红线、场景索引、示例要求 |
| `common/10-workflow.md` | 通用开发工作流与需求读取 | 开发前调研、需求文档读取、需求与接口优先级、Git 操作规范 |
| `common/20-no-hallucination.md` | 通用禁止发散与最小侵入 | 禁止脑补、禁止静默发散、禁止顺手优化、精准替换 |
| `common/30-formatting.md` | 通用格式化规范 | Codex 修改代码后的格式化与轻量验证要求 |
| `common/40-comments.md` | 通用代码清理与注释 | 代码清理、变量 / 函数 / 模板 / 样式注释、文件头注释 |
| `common/50-docs-debugging-api.md` | 通用文档接口联调 | 静态接口、TODO 字段、联调开发、跨接口字段归属、临时代码标记 |
| `common/60-testing-release.md` | 全栈测试、迁移与发布 | 前后端分层验证、契约测试、数据库迁移、兼容发布、回滚和交付验收 |
| `frontend/10-components-types.md` | 前端组件函数类型查证 | 组件 / 函数 / Hook 查证、公共能力复用、业务组件边界、TypeScript 类型处理 |
| `frontend/20-style-ui.md` | 前端样式与 UI 还原 | CSS/SCSS、布局弹性、组件默认样式、UnoCSS、UI 设计图还原 |
| `frontend/30-routing-enum-branch.md` | 前端路由枚举分支交互 | Vue 路由、枚举映射、条件分支、兜底值、交互前置状态与按钮提示 |
| `frontend/40-function-hook-reactive.md` | 前端函数 Hook 响应式命名 | 函数抽象边界、Vue Hook 抽离、computed 使用、变量命名 |
| `frontend/50-i18n.md` | 前端 i18n 翻译规范 | 禁止自动翻译、i18n key 扩展、语言文件扩展与 HTML 样式限制 |
| `frontend/60-icon.md` | 前端 Icon 使用规范 | Icon 来源、使用方式查证、临时 Icon 标记 |
| `frontend/70-vue-file-header.md` | 前端 Vue 文件头注释 | 新建 Vue 组件文件的头部说明注释规范 |
| `backend/10-service-api-contract.md` | 后端接口契约与服务分层 | 服务端接口契约、DTO、Controller / Service 分层、响应结构和错误码 |
| `backend/20-data-persistence.md` | 后端数据持久化与事务 | 数据库结构、Migration、SQL / ORM、事务、幂等和数据一致性 |
| `backend/30-auth-permission-security.md` | 后端鉴权权限与安全边界 | 服务端鉴权、权限校验、资源归属、租户隔离和敏感信息保护 |
| `backend/40-jobs-cache-observability.md` | 后端任务缓存与可观测性 | 定时任务、队列、缓存、分布式锁、日志、指标、告警和失败终态 |
| `common/80-terminal-node-model.md` | 通用终端文件 Node 模型 | 终端文件编码、Node 版本管理、模型专用规范 |
| `common/90-terminal-command-error.md` | 通用终端同步验证与错误处理 | 终端命令执行、Vite 验证分级、AI 规则同步验证、错误处理与用户感知 |
| `projects/buka-laaffic-ui-customer.md` | buka-laaffic 项目规则 | buka-laaffic-ui-customer 专用 i18n 与简繁体规则 |
| `projects/itnio-ui-customer.md` | itnio 项目规则 | itnio-ui-customer 专用错误码、错误提示、扩展前确认规则 |

## 新增规则归属

新增规则前先判断归属，避免所有内容都堆进常驻入口。

| 规则类型 | 推荐位置 | 判断标准 |
| --- | --- | --- |
| P0 红线、规则读取策略、场景索引 | `global-rules.md` | 需要所有任务第一时间看到，且不读细则也不能违反 |
| 需求读取、禁止脑补、Git、注释、格式化、终端、接口契约协作、跨端测试与发布 | `common/` | 前端、后端和其他开发任务都适用 |
| Vue、组件、Hook、SCSS、UI、路由、i18n、Icon、浏览器交互 | `frontend/` | 约束前端页面、组件、样式和用户界面 |
| Controller、Service、DTO、数据库、事务、鉴权、缓存、队列、日志、安全 | `backend/` | 约束服务端实现、数据持久化和运行时边界 |
| 项目专属补充 | `projects/*.md` | 只服务某个项目，不应污染通用规则 |
| 具体工作步骤 | `workflows/base.*.md` 或 `workflows/kl.*.md` | 更像流程，不是单条规则 |

## 前端 / 后端 / 通用判定顺序

1. **先看改动产物**：`.vue`、组件、Hook、SCSS、路由、i18n、Icon 属于前端；Controller、Service、DTO、Entity、Repository、SQL、Migration、队列、缓存、鉴权中间件属于后端；Git、需求读取、禁止脑补、注释、自检、终端命令属于通用。
2. **再看规则约束对象**：约束页面展示、组件写法和样式还原的是前端；约束接口实现、数据落库和服务端校验的是后端；约束 AI 开发前后如何确认和交付的是通用。
3. **最后看验证入口**：浏览器、Vite、SFC、样式检查偏前端；接口测试、数据库迁移、服务日志、鉴权链路偏后端；契约测试、跨端端到端验证、发布与回滚、`git diff --check`、规则同步和自检脚本偏通用。
4. **混合规则不强行塞单类**：接口字段不能脑补、跨接口字段归属、联调缺口反馈这类协作契约优先放 `common/`；必要时再在 `frontend/` 或 `backend/` 补专属细则。

## 新增规则流程

1. **查重**：先搜索 `rules/` 和 `workflows/`，确认是否已有相似规则。
2. **判定归属**：按本文件索引选择目标规则文件；能补充现有文件就补充现有文件。
3. **定位插入点**：按主题插入，不追加到无关文件末尾；检查目标位置前后上下文。
4. **预览确认**：写入前先给用户展示规则内容、目标文件和目标章节。
5. **维护清单**：新增规则文件时，必须同步更新 `rules/rules-manifest.json` 和本文件索引；只补充已有文件时通常不需要更新 manifest。
6. **同步验证**：写入后执行 `python3 sync-workflows.py --no-git`；同步脚本会自动执行同步前源结构自检和同步后全量自检，确认拼接后的全局规则已同步到目标工具。

## 新增规则文件流程

只有新增主题足够稳定、现有文件无法承载时，才新增规则文件。

1. 在 `common/`、`frontend/`、`backend/` 或 `projects/` 下创建语义化文件名。
2. 在 `rules/rules-manifest.json` 中加入新文件，并放到正确拼接顺序。
3. 在本文件的“规则文件索引”和“新增规则归属”中补充入口。
4. 更新根目录 `AGENTS.md`，如果新增了新的先读场景或目录职责。
5. 执行 `python3 sync-workflows.py --no-git`，通过内置自检确保新增文件、manifest、索引和同步产物互相一致。
6. 验证目标工具读取完整规则。

## 规则写法模板

```md
## 规则名称

**核心原则**：一句话说清楚这条规则解决什么问题。

**适用场景**：说明什么时候必须遵守。

**硬性红线**：

- 禁止 xxx。
- 禁止 xxx。

**正确做法**：

- 应该 xxx。
- 应该 xxx。

**代码示例**：

\```ts
// ❌ 禁止 - 抽象反例
const value = xxx

// ✅ 正确 - 抽象正例
const result = getXxxValue(xxx)
\```

**判断标准**：

- 是否满足 xxx。
- 是否避免 xxx。
```

## 示例要求

- 示例必须抽象化，不使用真实业务接口、真实权限标识、真实客户 / 供应商 / 金额等生产信息。
- 示例只保留能说明规则的最小结构，避免贴完整组件、完整接口或完整弹窗。
- 固定项目约定可以保留真实名称，但必须说明这是项目约定。

## 维护自检

- 新规则是否已经搜索查重。
- 新规则是否放在对应主题文件。
- 新规则是否比已有规则更清晰，而不是重复表达。
- 新规则是否包含明确的禁止项和判断标准。
- 新增规则文件后是否更新 `rules/rules-manifest.json`。
- 新增大主题后是否更新本索引和根目录 `AGENTS.md`。
- 修改后是否执行 `python3 sync-workflows.py --no-git` 并通过内置前后自检。
- 修改后是否同步并验证目标工具可见性。
- 最终回复是否输出自检、同步、Codex 可见性、二次自检和提交状态的闭环验收回执。
