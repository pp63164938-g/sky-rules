# 函数抽象边界规范

**核心原则**：禁止为了“看起来结构化”而把简单表达式、单行字符串拼接、单次使用且无业务语义的逻辑强行抽成函数。函数抽象必须带来明确收益：复用、隔离复杂逻辑、表达稳定业务概念、封装外部差异或降低主流程认知成本。

**适用场景**：页面方法、事件处理、参数组装、接口调用包装、工具函数、常量抽离、公共函数复用。

**硬性红线**：禁止套壳函数、无业务语义二次包装、单次简单表达式抽函数；抽象必须让调用处更清晰或减少真实重复。

**禁止行为**：

- 单行表达式只使用一次，却额外抽函数
- 函数名只是重复代码行为，没有提供新的业务语义
- 为简单字符串拼接、简单取值、简单布尔判断单独建函数
- 抽函数后调用处仍然需要回看函数实现才能理解真实逻辑
- 为了添加函数注释而制造没有必要的函数
- 禁止新增“套壳函数”：函数内部只是调用另一个函数，没有新增业务判断、参数转换、副作用隔离、错误处理、复用语义或阅读收益时，应直接调用原函数。后续确实出现差异化逻辑时，再按真实变化新增函数，禁止为了“以后可能扩展”提前制造两层函数调用。
- 禁止在抽离公共函数后，再在调用方新增只负责转参、无额外业务语义的二次包装函数。公共函数已经表达稳定业务概念时，调用处应直接调用公共函数；只有调用方需要补充本页面独有的业务分支、兼容逻辑、副作用或能显著降低阅读成本时，才允许保留页面内包装函数。

**常量抽离判断顺序**：

1. **先判断确定性**：未确认的接口字段、请求参数、响应字段、枚举真实值或数据源，即使后续需要统一替换，也不能仅因为“待联调”而抽成普通常量；必须继续使用 `TODO待联调_` / `TODO无此联调字段_`、API Mock 或空 Options 显性暴露。
2. **再判断维护收益**：只有满足以下任一条件时才抽常量：同一已确认值被多个独立业务判断或配置点复用；需要跨文件复用；值本身形成稳定前端协议、项目约定或明确业务集合；集中维护后能真实降低遗漏风险。
3. **单次使用默认不抽**：只使用一次的场景标识、Tab 标识、状态值、请求值、普通文案或 Mock 值，直接写在业务位置；不能因为名称较长、需要注释、带 TODO、以后可能复用，就提前抽常量。
4. **Options 是枚举唯一数据源**：枚举只用于下拉展示、标签展示、默认值或接口提交时，直接在 `xxxOptions` 中维护 `label/value`，禁止把每个 value 再机械拆成独立常量。默认值优先从 Options 中取得。
5. **Mock 不做常量体系**：API Mock 中的临时值直接保留在 `@mock-start` 块内，禁止为联调替换方便建立 `MOCK_*`、`TODO_*` 常量或临时映射体系。
6. **常量必须说明业务身份**：确实需要抽离的常量必须用 JSDoc 说明来源、具体值含义和使用范围；禁止只写名称相似但没有稳定业务概念的常量。

**简单枚举命中判断不额外封装**：

- 当判断只是“当前值是否等于类型 A / 类型 B”或“列表是否包含类型 A / 类型 B”这类简单枚举命中逻辑时，优先在当前响应式派生、分支或提交逻辑中直接写出判断条件，禁止再封装一层 `isXxxType` / `hasXxxType` / `getXxxVisible` 等函数导致阅读链路变长。
- 只有判断逻辑被多处复用、条件组合较复杂、需要隔离外部差异、或函数名能表达稳定业务概念时，才允许抽函数。
- 直接写判断时必须在附近写清楚业务注释，说明命中的具体类型、枚举值来源和对应业务表现，禁止留下无注释的裸枚举判断。

**重复业务判断统一入口**：

- 同一业务判断在同一组件或模块中重复出现 3 次及以上时，应抽成语义明确的谓词函数，统一供显隐、禁用、样式或脚本分支复用。
- “简单判断不额外封装”只适用于单次或少量使用；达到真实重复门槛时，统一判断入口优先，避免业务条件调整或联调字段替换时漏改。
- 判断依赖当前行、选项或其他入参时，使用接收入参的普通纯函数；禁止为了复用带参数判断建立外部响应式状态或参数化 `computed`。
- 待联调字段参与重复判断时，TODO 字段和值应保留在谓词函数的实际比较位置，便于后续统一替换；禁止为了抽离判断将其包装成无依据的正式字段或普通常量。
- 多处条件只有字段、枚举和命中语义完全一致时才共用同一谓词函数；语义不同的判断禁止为了减少代码强行合并。

```vue
<!-- ❌ 禁止 - 同一业务判断散落在多个模板属性中 -->
<XxxTag v-if="row.TODO待联调_业务状态 === TODO待联调_值_目标状态" />
<XxxButton :disabled="row.TODO待联调_业务状态 === TODO待联调_值_目标状态" />
<XxxPanel :class="{ 'is-target': row.TODO待联调_业务状态 === TODO待联调_值_目标状态 }" />

<!-- ✅ 正确 - 同一业务判断统一复用谓词函数 -->
<XxxTag v-if="isTargetBusinessRow(row)" />
<XxxButton :disabled="isTargetBusinessRow(row)" />
<XxxPanel :class="{ 'is-target': isTargetBusinessRow(row) }" />
```

```ts
/** 判断当前行是否命中目标业务状态 */
function isTargetBusinessRow(row: XxxRow) {
    return row.TODO待联调_业务状态 === TODO待联调_值_目标状态
}
```

```javascript
// ❌ 禁止 - 简单类型命中又封装一层，阅读时需要跳转确认函数内部
function hasTargetType(typeList) {
    return typeList.includes(TYPE_A) || typeList.includes(TYPE_B)
}

const visible = computed(() => hasTargetType(form.typeList))

// ✅ 正确 - 直接写出命中的业务类型，并用注释说明业务表现
const visible = computed(() => {
    // 类型 A / 类型 B：展示目标字段
    return form.typeList.includes(TYPE_A) || form.typeList.includes(TYPE_B)
})
```

**代码示例**：

```javascript
// ❌ 禁止 - 单次使用的简单拼接，不需要函数
function getInviteObjectKey(objectCode, objectCodeIndex) {
    return `${objectCode}_${objectCodeIndex}`
}

const row = {
    inviteObjectKey: getInviteObjectKey(objectCodeItem, objectCodeIndex)
}

// ✅ 正确 - 直接内联，调用处更清晰
const row = {
    inviteObjectKey: `${objectCodeItem}_${objectCodeIndex}`
}
```

```javascript
// ❌ 禁止 - 页面内函数只是给公共函数转参，没有新增业务语义
function getBusinessDisabled() {
    return getXxxDisabled({ businessType, loading, hasValue })
}

const isBusinessDisabled = computed(getBusinessDisabled)

// ✅ 正确 - 直接在响应式派生点调用公共函数
const isBusinessDisabled = computed(() => getXxxDisabled({ businessType, loading, hasValue }))
```

```javascript
// ❌ 禁止 - 只是套壳，没有新增任何处理
function handleXxx(dataList) {
    return fetchXxx(dataList)
}

// ✅ 正确 - 直接调用已有函数
fetchXxx(dataList)

// ✅ 可以新增函数 - 后续确实出现本页面独有处理时再抽
function handleXxx(dataList) {
    if (!isBusinessScene.value) return

    return fetchXxx(dataList)
}
```

```javascript
// ✅ 可以抽函数 - 存在稳定业务语义或复杂兼容逻辑
function getStaffGroupOptions(staffGroupItem) {
    const staffOptions =
        staffGroupItem.staffOptions ??
        staffGroupItem.staffList ??
        staffGroupItem.staffOptionList

    if (Array.isArray(staffOptions)) return staffOptions

    return []
}
```

**判断标准**：

- 只用一次、只有一行、没有业务命名价值 → 不抽函数
- 能直接看懂的简单表达式 → 优先内联
- 函数只是“换个名字调用另一个函数” → 不抽；等出现真实业务分支、参数整理、错误处理或复用需求时再新增函数
- 有复用、有复杂分支、有接口差异、有稳定业务概念 → 可以抽函数
- 抽函数后必须让主流程更清晰，而不是增加跳转成本
- 单次使用、语义清楚、没有稳定业务概念 → 不抽常量
- 仅因待联调、方便替换、可能复用 → 不抽常量
- 多个独立业务分支复用、跨文件复用或形成稳定协议 → 可以抽常量
- 仅用于 Options 展示和提交 → Options 自身作为唯一数据源，不拆枚举项常量
- 文案需要多处保持一致、跨文件复用，或是产品统一口径 → 可以抽常量，并用 JSDoc 说明业务含义和使用场景

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
# 变量命名规范

**核心原则**：在循环迭代（如 `map`、`forEach`、`find`）或复杂的业务逻辑方法中，**禁止使用含义不明的单字符变量名**（如 `s`、`t`、`i`、`item` 等）。必须使用完整、具有语义化的单词进行命名。

**目的**：解决复杂业务场景下变量指代不明、容易混淆的问题，同时便于后期全局搜索和维护。

**代码示例**：

```javascript
// ❌ 禁止 - 含义不明的单字符变量名
allSettlements.map((s, index) => {
  const tiers = parseAmountRange(s.amountRange || '')
  return tiers.map(t => ({ ... }))
})

// ✅ 推荐 - 语义明确的完整单词
allSettlements.map((settlementItem, index) => {
  const monthlyTiers = parseAmountRange(settlementItem.amountRange || '')
  return monthlyTiers.map(tierItem => ({ ... }))
})
```

**判断标准**：

- **禁止简写**：禁止使用 `s`、`t`、`v` 等缩写代替业务对象名
- **语义化**：变量名应准确描述其代表的数据内容（如 `settlementItem` 而非 `item`）
- **例外情况**：仅在极简的二行以内、逻辑单一的箭头函数中，且不涉及复杂对象属性访问时，才可视情况允许使用 `item` 或 `val`，但仍优先推荐完整命名。
