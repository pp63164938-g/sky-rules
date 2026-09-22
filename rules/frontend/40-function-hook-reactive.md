# Vue Hook / Composable 抽离规范

**核心原则**：Hook / Composable 只用于封装具有独立响应式状态、副作用或可复用业务流程的组合式逻辑；禁止为了“文件拆分”把简单表达式、纯工具函数、单次按钮逻辑强行抽成 Hook。

**适用场景**：独立响应式状态、接口请求流程、并发控制、缓存、订阅、表单校验、跨组件复用逻辑。

**硬性红线**：没有响应式状态、副作用、生命周期或复用边界的纯函数，不应抽成 Hook；不能只为减少主文件行数拆 Hook。

**适合抽离为 Hook 的场景**：

- 包含独立的 `ref` / `reactive` / `computed` / `watch` / 生命周期，并围绕一个稳定业务概念组织，例如预览得分、远程下拉、表格状态、轮询任务。
- 同一块逻辑同时包含状态、接口请求、并发控制、缓存、订阅、表单校验、错误处理等流程，留在页面主组件会打散主流程。
- 会被 2 个及以上组件或页面复用，且调用方只需要关心输入参数和返回状态 / 方法。
- 页面专属但业务边界清晰，抽出后主组件能更聚焦模板、入口参数和提交主流程。

**不应抽离为 Hook 的场景**：

- 只是简单 `computed`、格式化函数、单次点击处理、单行字符串拼接或普通取值。
- 函数内部没有 Vue 响应式状态、副作用或生命周期，只是纯数据转换；这类逻辑应保留为普通函数，或放到 `utils`。
- 抽离后调用方仍必须频繁回看 Hook 内部实现才能理解业务，说明边界没有变清晰。
- 只为减少主文件行数而拆分，但没有稳定业务命名和独立职责。

**命名与目录规范**：

- Hook 函数必须使用 `useXxx` 命名，文件名与导出函数保持一致，例如 `useXxxPreview.ts`。
- 页面专属 Hook 放在当前页面或功能目录的 `hooks/` 下；跨页面复用 Hook 才上升到 `src/hooks/`。
- Hook 文件默认使用 `.ts`；只有确实返回 JSX / TSX 渲染内容时才使用 `.tsx`。
- 一个 Hook 文件优先只导出一个主 Hook；内部辅助函数保持私有，除非确有复用需求再单独导出。

**代码示例**：

```ts
// ❌ 禁止 - 只是纯格式化，不应抽 Hook
export function useXxxFormat() {
    return { formatXxx }
}

// ✅ 正确 - 独立业务状态 + 接口请求 + 并发控制，可抽 Hook
export function useXxxPreview(options) {
    const previewInfo = ref({})
    const requestNo = ref(0)

    async function handleChange(dataList) {
        // 校验、去重、并发控制、调用接口
    }

    return { previewInfo, handleChange }
}
```

# Vue 响应式派生数据使用规范

**核心原则**：`computed` 只用于真正需要响应式缓存、模板自动更新或多处响应式消费的派生数据；不要把一次性计算、事件处理内的临时转换、带参数转换逻辑都写成 `computed`。

**适用场景**：模板展示、禁用状态、列表渲染、多处响应式消费、事件处理中的临时转换。

**硬性红线**：点击、提交、生成、预览等一次性流程不要为了取一次值维护 `computed`；`computed` 内禁止副作用。

**禁止行为**：

- 点击按钮、提交表单、预览生成等一次性流程中，只为了取一次值而定义 `computed`
- 参数化转换逻辑写成 `computed`，再通过外部响应式变量间接驱动
- 仅为了“统一取值”把简单解析、拆分、过滤逻辑放进 `computed`
- 在 `computed` 内做接口请求、状态写入、消息提示等副作用

**代码示例**：

```javascript
// ❌ 不推荐 - 点击生成时才需要编码，却长期维护 computed 依赖
const inviteObjectCodes = computed(() => formData.value.objectCodes.split(/[，,\n]+/).filter(Boolean))

async function handleGenerate() {
    const objectCodes = inviteObjectCodes.value
}

// ✅ 推荐 - 一次性流程中按需执行函数，输入输出更明确
function getInviteObjectCodes() {
    return formData.value.objectCodes.split(/[，,\n]+/).filter(Boolean)
}

async function handleGenerate() {
    const objectCodes = getInviteObjectCodes()
}
```

**判断标准**：

- 模板直接展示、禁用状态、列表渲染依赖，并且需要随响应式数据自动变化 → 可以用 `computed`
- 只在某个函数执行时使用一次，例如点击“生成邀约信息”时解析编码 → 用普通函数或函数内局部变量
- 需要传参、需要明确输入输出的数据转换 → 用普通函数
- 逻辑本身不是响应式消费点，就不要为了“方便拿值”引入 `computed`
