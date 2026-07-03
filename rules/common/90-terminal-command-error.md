# 终端命令执行规范

**终端环境设定**：

**适用场景**：自动化终端命令、复杂管道 / 重定向、API 测试、构建验证、后台命令、Windows 路径输出。

**硬性红线**：复杂命令必须先确认终端语法；API 测试必须加超时；Vite 项目默认不执行 full build；后台命令转异步后必须立即轮询。

即使底层系统被识别为 Windows 并默认调用 PowerShell，在执行自动化终端命令（如 `run_command`）时，**必须优先将默认环境视为 Git Bash**。除了极简单且跨平台的通用命令（如 `npm run dev`），对于所有复杂操作（包含管道、重定向、环境变量传递、特定语法等），**优先使用 `bash -c "你的命令"` 进行包裹执行**，**严禁在未确认终端类型时混用 PowerShell 与 Bash 的语法和转义规则**。

**PowerShell 回退兼容规范**：

当 `bash -c` 启动失败、系统实际只能使用 PowerShell，或命令已经明确在 PowerShell 中执行时，必须按 PowerShell 语法重写命令，禁止继续套用 Bash 转义规则。

- ❌ 禁止在 PowerShell 参数中使用 Bash 风格的 `\"` 转义双引号，这会导致 `rg`、`node -e` 等命令收到被截断的参数。
- ✅ PowerShell 中优先使用单引号包裹包含双引号的参数，例如：`rg -n ':fn="getTableData"' src/xxx.vue`
- ✅ `rg` 多关键字固定文本搜索优先使用 `-F -e`，避免正则、括号、反斜杠和 shell 转义叠加出错：
  `rg -n -F -e 'getTableData' -e ':fn="getTableData"' -e 'tableLoad(searchForm)' src/xxx.vue`
- ✅ 复杂正则在 PowerShell 中执行前必须先拆成固定文本搜索或分步查询；确实需要正则时，必须用 PowerShell 合法引号重新书写并先小范围验证。
- ✅ 在 PowerShell 中读取 UTF-8 文件时，仍应遵循“终端文件操作编码规范”，使用 `[System.IO.File]::ReadAllText/ReadAllLines(..., [System.Text.Encoding]::UTF8)`，不要用会破坏编码的 `Get-Content` 管道写回。

**对外输出命令的路径格式规范**：

当给用户输出可复制执行的终端命令时，必须根据目标终端选择正确路径格式，避免 Windows 路径在 Git Bash 中被反斜杠转义。

- 如果命令代码块标记为 `bash`，或上下文要求在 Git Bash / MINGW64 中执行：
  - ❌ 禁止输出 Windows 反斜杠路径：`D:\实际仓库路径\sky-rules\sync-workflows.py`
  - ✅ 必须输出基于当前已确认仓库位置的 Git Bash 可执行路径：`D:/实际仓库路径/sky-rules/sync-workflows.py`
  - ✅ 路径包含空格、中文或特殊字符时必须加双引号：`python "D:/实际仓库路径/sky-rules/sync-workflows.py" --no-git`
  - ✅ 如果当前终端已在 `sky-rules` 仓库根目录，优先输出相对命令：`python sync-workflows.py --no-git`

- 如果命令代码块标记为 `powershell`，才允许使用当前已确认仓库位置的 Windows 反斜杠路径：`D:\实际仓库路径\sky-rules\sync-workflows.py`

**判断标准**：给用户的命令必须能在其当前终端中直接复制执行；不要把 PowerShell 路径格式放进 Bash 命令块。

**AI 规则 / Skills 同步验证规范**：

当执行全局规则、项目规则、工作流、Skills、MCP 配置等 AI 工具配置同步时，禁止只以“文件复制成功 / 命令输出 OK”作为最终成功标准，必须同时验证目标工具实际读取的位置和模型可见上下文。

- **先确认真实读取目录**：不得凭默认路径或历史经验判断目标目录；必须优先使用工具自带诊断命令、配置输出、环境变量、实际 prompt/context 调试入口确认。例如 Codex 应以 `codex-cli doctor`、`codex-cli debug prompt-input`、`CODEX_HOME`、`~/.codex/config.toml` 等实际结果为准。
- **同步脚本必须输出具体目标**：同步完成后必须列出规则文件、Skills/工作流目录的绝对路径，以及生成数量；禁止只回复“已同步到各编辑器”。
- **必须验证实际加载**：只要工具提供模型输入、上下文、插件/Skill 列表或诊断入口，就必须用该入口确认代表性规则或 Skill 已进入工具可见上下文。Codex 场景必须确认 `prompt-input` 中能看到代表性 Skills，例如 `base-debugging`、`base-docs`、`kl-gen-page`。
- **路径不一致时修源头**：如果发现同步产物写入路径和工具实际读取路径不一致，必须优先修改 `sky-rules` 源同步脚本或可提交配置，让所有项目复用正确逻辑；禁止只在当前机器手动复制一次。
- **跨项目通用原则**：项目内需要使用规则/Skills 时，只运行 `sky-rules` 同步入口或项目约定入口；禁止在业务项目中手工维护同一份全局规则副本，避免不同项目规则漂移。

**核心原则**：禁止命令在编辑器中"假死"（显示 Running 但实际已完成或无响应）。

**Vite 项目构建验证规范**：

当当前项目可识别为 Vite 前端项目（如存在 `vite.config.*`，或 `package.json` scripts 中使用 `vite build`）时，日常页面开发、接口联调、Mock 替换、样式调整、规则同步等任务默认不执行 full build。

- ❌ 禁止在用户未明确要求时自动执行：`npm run build`、`pnpm build`、`yarn build`、`vite build`
- ✅ 优先使用轻量检查：`git diff --check`、目标文件搜索、局部类型/语法检查、已有轻量 lint 命令
- ✅ 如果确实需要构建验证，必须先说明原因并征得用户确认
- ✅ 仅在用户明确要求 build、排查构建失败、发布前验证、CI/部署相关任务时才执行 full build

**判断标准**：Vite 的生产构建成本较高且容易产生额外产物；除非构建本身就是任务目标，否则不要把 build 当作默认验证步骤。

**前端日常开发验证分级规范**：

当任务属于单页面开发、接口联调、Mock 替换、局部样式调整、表单/表格小范围变更时，默认采用轻量验证，禁止直接上全项目重检查。

- ✅ 默认轻量验证：
  - `git diff --check` 检查本次变更补丁
  - 对本次新增/修改的 `.vue` 文件做 SFC 解析或模板编译检查
  - 使用 `rg` 定向确认路由、API、组件引用、TODO 标记是否符合预期
  - 有项目级 `format` / `lint:fix` 时，仅对本次修改文件执行对应命令

- ⚠️ 中等验证需按场景选择：
  - `vue-tsc --noEmit` 属于全项目类型检查，不作为单页面开发默认验证
  - 仅在修改公共类型、通用组件、Hook、工具函数、路由核心配置、TS 配置，或用户明确要求时执行
  - 如果 `vue-tsc` 因项目存量问题、OOM 或无关文件报错失败，应停止继续加码重试，并明确说明失败原因和是否命中新改文件
  - 禁止在未说明原因时自动提高 Node heap 继续反复跑全项目检查

- ❌ 默认禁止：
  - 日常页面开发默认执行 `npm run build` / `pnpm build` / `yarn build`
  - 为了验证单个页面而触发全项目构建或全项目类型扫描
  - 遇到无关存量错误后顺手修改非本次任务文件

**超时策略**：

| 命令类型                                   | WaitMsBeforeAsync | 说明                                            |
| ------------------------------------------ | ----------------- | ----------------------------------------------- |
| 短命令（`ls`、`cat`、`status`、`git log`） | 5000-10000ms      | 同步等待完成，直接返回结果                      |
| 中等命令（`npm install`、`build`）         | 10000ms           | 同步等待，超时则转后台并立即轮询                |
| 长命令（AI 生成、大规模编译）              | 500ms             | 立即转后台，**必须紧接着轮询** `command_status` |

**API 测试必须加超时**：

```bash
# ❌ 禁止 - 无超时，可能永远卡住
curl -s -X POST "https://api.example.com/..."

# ✅ 正确 - 加超时
curl -s --connect-timeout 10 --max-time 30 -X POST "https://api.example.com/..."
```

**后台命令轮询规则**：

- 命令转后台后，**必须在下一个工具调用中立即轮询** `command_status`
- 禁止发送命令到后台后做其他事情而忘记检查状态
- 轮询超过 5 分钟无新输出，主动终止命令并报告

# 错误处理与用户感知规范

**核心原则**：严禁在核心业务、交互动作或外部系统对接环节“静默吞噬”错误。发生异常（如 Token 失效、HTTP 报错、构建提取失败等）时，必须通过合理的方式建立**明确的用户感知触点**。

**目的**：绝对禁止“出了错但系统没有任何反应/仅仅打印一行日志”的“黑盒现象”。确保发生问题时，不论是前台点击还是后台默默轮询，最终都能通过 UI 交互或推送通道把问题暴露给用户或运维，引导其人为干预。

**具体要求与做法**：

1. **前台交互场景**：用户发生点击操作（Click）后，所有的失败分支（`catch` 异常、非 200/成功返回），必须通过 `Toast`/`Notice`/`Message` 框显式提示用户出错原因及解决建议，而不能吞没在控制台内。
2. **后台异步/轮询场景**：当自动化任务遇到无法自行突破的“死结”（如通过 `catch` 捕获到网络异常、或者自动挽回失败的 Token 401 过期），不要只写 `console.error` 了事。应该将该错误**具象化为一个特定的终态/异常态**（例如将状态扭转为 `TOKEN_EXPIRED` 或 `FETCH_FAILED`），并由系统主动利用钉钉、邮件等通知通道推送给干预人。
3. **关于 `try-catch` 的吞噬**：仅有绝对不影响主流程分支且已经具备正确兜底数据的边缘场景，才允许使用空 `catch (e) {}` 块，并强制在内加上明确注释（如 `// ignore: 可降级，使用默认配置`）。

**代码示例**：

```typescript
// ❌ 禁止：静默吞噬错误
try {
  await triggerTask()
} catch (error) {
  console.error(error)
}

// ✅ 后台任务：转成异常态并通知
if (response.status === 401 && !newToken) {
  await notifyOwner({ status: 'TOKEN_EXPIRED' })
  return
}

// ✅ 前台交互：明确提示用户
try {
  await api.updateConfig()
  this.$message.success('更新成功')
} catch (err) {
  this.$message.error(err.message || '操作失败')
}
```
