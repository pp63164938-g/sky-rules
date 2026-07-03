# Vue 路由跳转规范

**核心原则**：路由跳转优先使用 `name` 方式，避免使用硬编码路径。

**目的**：路径变更时只需修改路由配置，无需全局搜索替换。

**代码示例**：

```javascript
// ❌ 不推荐 - 硬编码路径
this.$router.push("/agent/contractSign");

// ✅ 推荐 - 使用路由 name
this.$router.push({ name: "contractSign" });

// ✅ 带参数的跳转
this.$router.push({ name: "userDetail", params: { id: 123 } });
this.$router.push({ name: "search", query: { keyword: "test" } });
```

# 枚举映射规范

**核心原则**：枚举展示和枚举判断必须避免三元表达式、散落硬编码和重复数据源。优先判断当前模块是否已经存在下拉 Options；有下拉时复用下拉数据源，没有下拉时再使用映射对象（Map/Object）作为唯一数据源。

**适用场景**：接口状态、类型、模式、错误码、业务枚举、按钮状态、样式状态、下拉展示、提交值和条件分支判断。

**硬性红线**：禁止用三元表达式承载业务枚举；禁止重复维护 options 与 map；接口真实值不确定时必须用 `TODO待联调_值_用途描述` 或先确认。

**有下拉 Options 的展示场景**：当枚举值已经以 `CommonEnum` / `xxxOptions` 形式存在时，展示 label 必须优先复用该 options 数据源，禁止为了展示再维护一份内容完全相同的映射对象。

```javascript
// ❌ 禁止 - options 和 map 内容重复维护
const businessTypeOptions = [
  { label: "供应商", value: 1 },
  { label: "客户", value: 2 },
];

const BUSINESS_TYPE_LABEL_MAP = {
  1: "供应商",
  2: "客户",
};

// ✅ 推荐 - 直接复用已有下拉 options
const businessTypeLabel = getListOptionLabel(businessType, businessTypeOptions);

// ✅ 可选 - 特殊场景直接查找 options
const businessTypeLabel = businessTypeOptions.find(businessTypeOption => businessTypeOption.value === businessType)?.label ?? "未知";
```

**枚举 Options 与值常量边界**：

- 当需求文档明确写出“枚举值：A、B、C”时，该字段默认按枚举字段处理：表单优先使用下拉 / 单选等枚举组件，列表展示必须通过统一 Options + `getListOptionLabel(value, xxxOptions)`，禁止把中文枚举值散落写死在模板、表格 formatter 或输入框展示里。
- 若需求只提供中文枚举展示值、没有提供接口 id/code，应先区分用途：
  - 仅用于纯展示，或需求 / 接口文档明确说明提交值就是中文枚举值时，才允许 `options.value` 暂用中文枚举值本身。
  - 只要该值会参与业务判断、状态分支、禁用规则、按钮显隐、接口参数分支、组件 `active-value/inactive-value` 等逻辑，禁止直接使用“启用 / 禁用 / 系统计算”等中文展示文案作为判断值或提交值。
  - 接口真实值不确定时，必须使用 `TODO待联调_值_用途描述` 占位，把“值”紧跟在 `TODO待联调_` 后面，明确这是给接口 id/code/value 预留的值，而不是字段名或展示文案。禁止写成 `TODO待联调_用途描述值` 这种把“值”放在末尾的形式。例如：`TODO待联调_值_业务状态启用` / `TODO待联调_值_业务类型目标项`。
- 只读场景如果必须使用输入框展示，也不能直接展示原始硬编码文本，应由枚举 Options 派生展示值。
- 禁止为每个枚举项机械拆分值常量。只有枚举值会被多处业务判断、接口分支、禁用规则或跨文件复用时，才单独抽值常量；仅用于 options 展示/提交时，直接在 options 中维护 `label/value`。
- 新增默认值优先从 options 中取值，例如 `xxxOptions[0].value`；如果默认项不是第一项或有明确业务名称，再单独声明“默认值”常量，不要把所有枚举项都拆成常量。

**禁止使用展示文字做业务判断**：

- 禁止用页面展示文案、标签文案、按钮文案等 UI 文字直接做业务判断，例如 `row.status === '启用'`、`type === '系统计算'`。除非用户或接口文档明确说明该字段的真实提交值/接口值就是该文字，否则必须使用接口 id/code/value、枚举 Options 的 `value`、映射对象或常量集合判断。
- 禁止使用中文、英文或任何多语言展示文案做业务判断；`label`、`name`、按钮文案、标签文案、提示文案都只能用于展示，不能控制图标、按钮状态、提交分支、权限分支、样式状态或接口参数。
- 禁止用 `includes`、正则、大小写转换等方式从展示文案中推断业务场景，例如 `label.includes('目标文案')`、`name.toUpperCase().includes('IM')`。
- 静态开发阶段如果接口只给了中文枚举值，必须集中维护在当前页面必要范围内的 Options / 映射中，再由 `value` 驱动展示和判断；不要在模板和函数里散落重复中文判断。
- 如果接口暂时只返回展示文案而没有稳定 `id/code/value`，不得把展示文案包装成确定业务判断；必须使用 `TODO待联调_值_用途描述` 预留稳定标识，并反馈需要后端补充真实枚举值。
- 枚举仅在当前局部展示使用时，不要为了“看起来规范”强行抽到可复用文件；可以在当前函数或当前模块内维护最小映射，但判断入口仍应基于统一数据源。
- 模板中可以显式写 `if / else-if` 表达复杂业务分支，但分支条件必须基于接口值、枚举 value 或 TODO 待联调值，不能基于展示文案。

```javascript
// ❌ 禁止 - 展示文案不是稳定业务标识
const visible = optionItem.label.includes('目标文案')

// ✅ 正确 - 使用接口稳定标识
const visible = optionItem.value === TARGET_SCENE_CODE

// ✅ 正确 - 后端未提供稳定标识时显性预留
const visible = optionItem.value === 'TODO待联调_值_目标场景'
```

**无下拉 Options 的展示场景**：当当前模块没有现成下拉 options，或该映射本身就是稳定业务常量时，使用映射对象统一维护 value → label。

```javascript
// ❌ 禁止：业务枚举用多层三元
const statusText = status === 1 ? '状态A' : status === 2 ? '状态B' : '未知'

// ✅ 正确：使用唯一映射数据源
const STATUS_MAP = {
    1: '状态A',
    2: '状态B'
}
const statusText = STATUS_MAP[status] || '未知'
```

**多类型条件判断**：当多个类型共享相同逻辑时，使用常量集合 + `includes` 判断：

```javascript
// ❌ 禁止 - 硬编码单值判断，新增类型时容易遗漏
v-if="rule.productType === 1"

// ✅ 推荐 - 提取常量集合，新增类型只需修改一处
const SMS_VOICE_PRODUCT_TYPES = [1, 3, 4]
v-if="SMS_VOICE_PRODUCT_TYPES.includes(rule.productType)"
```

**三元表达式使用限制**：

- 只有永远不会扩展的纯布尔正反场景，才允许使用三元表达式，例如是否显示“是/否”、是否加一个简单占位文案
- 只要判断对象是状态、类型、模式、错误码、业务枚举、接口返回标识，禁止使用三元表达式，必须使用映射对象、明确分支或常量集合
- 只要后续可能新增第三种状态，禁止使用三元表达式，即使当前只有两个值
- 不确定是否会扩展时，默认按会扩展处理，禁止使用三元表达式
- 三元表达式不能承载业务状态命名转换，例如把 `configured/conflict` 转成 `primary/danger`，业务状态和样式状态必须分层处理
**判断标准**：

- **有下拉 Options 的枚举展示**：禁止重复维护 Map/Object，必须优先复用 `getListOptionLabel(value, xxxOptions)` 或 `xxxOptions.find(...)`
- **无下拉 Options 的枚举展示**：禁止使用三元运算符，必须使用映射对象（Map/Object）统一维护
- **多状态判断**：禁止使用三元运算符，必须使用映射对象或明确分支
- **多类型共享逻辑**：禁止硬编码单值判断，必须提取常量集合 + `includes`
- **真假二元判断 (Boolean)**：仅简单、确定永远不扩展的 Yes/No 场景允许使用三元运算符；不确定时禁止使用

## 枚举条件分支判断规范

**核心原则**：当条件字段是枚举类型时，必须显式判断每个已知枚举值，禁止只判断其中一个值，再把剩余情况默认当作另一个枚举值处理，除非该默认分支确实是业务兜底并写明原因。

**跨语法一致要求**：

- 业务枚举、状态、类型、来源、模式、权限、按钮状态、图标类型、样式状态等条件分支，不区分写在 Vue template、JS / TS、TSX / JSX、computed、formatter、render 函数或映射函数中，都必须遵守同一套分支规则。
- 禁止只判断一个已知业务值，再用 `else`、`v-else`、`switch default`、三元表达式的 `:` 分支、映射对象的默认值、`??` / `||` 兜底，把其他未枚举值默认渲染成另一个已知业务表现。
- 已确认枚举值必须逐个显式判断；未知值只能走“未知 / 空渲染 / 禁用 / TODO 待确认 / 异常提示”等真正兜底分支，不能静默复用某个业务分支。
- `else`、`v-else`、`default` 只允许用于真实二元 UI 状态，例如有数据 / 无数据、加载中 / 非加载中、展开 / 收起、选中 / 未选中；如果条件来源是业务枚举或状态值，则默认不按真实二元处理。
- `switch default` 只能表达未知或异常兜底，禁止把 default 当作某个确定业务类型处理。
- TSX / JSX 中的三元渲染同样受限：禁止写成 `type === TYPE_A ? <IconA /> : <IconB />` 来承载业务枚举；应显式判断 `TYPE_A`、`TYPE_B`，未知值返回 `null` 或明确兜底 UI。

```javascript
// ❌ 禁止：只判断 A，剩余情况默认当 B
if (targetType === TARGET_TYPE_A) {
    return getAOptions()
}

return getBOptions()

// ✅ 正确：已知枚举逐个判断，未知类型单独处理
if (targetType === TARGET_TYPE_A) {
    // 类型 A 使用 A 数据源
    return getAOptions()
}

if (targetType === TARGET_TYPE_B) {
    // 类型 B 使用 B 数据源
    return getBOptions()
}

// 未识别类型，避免未来新增枚举时误走旧逻辑
return []
```

```tsx
// ❌ 禁止 - TSX 三元把非 A 都渲染成 B
return type === TYPE_A ? <IconA /> : <IconB />

// ✅ 正确 - TSX 中同样显式判断已知枚举
if (type === TYPE_A) {
    return <IconA />
}

if (type === TYPE_B) {
    return <IconB />
}

return null
```

```vue
<!-- ❌ 禁止 - Vue template 中用 v-else 吞掉未知业务类型 -->
<XxxIconA v-if="type === TYPE_A" />
<XxxIconB v-else />

<!-- ✅ 正确 - 已知枚举显式判断 -->
<XxxIconA v-if="type === TYPE_A" />
<XxxIconB v-if="type === TYPE_B" />
```

**判断标准**：

- 先判断这个条件是不是业务枚举 / 状态 / 类型 / 来源；如果是，就按枚举分支规则处理。
- 不看语法形式，看业务含义；`v-else`、`else`、`default`、三元 `:`、映射默认值，本质上都是“剩余分支”。
- 枚举值有明确含义时，每个已知值都要显式判断。
- 禁止用“非 A 即 B”的写法处理业务枚举。
- 默认分支只能用于真正的未知/兜底场景，并且必须有过程注释说明原因。
- 未来新增枚举值时，应新增独立分支，而不是复用旧默认逻辑。
- 新增一个枚举值时，页面是否会自动误入旧业务 UI；如果会，说明写法不合格。
- 未知值是否被显性处理；如果未知值悄悄展示成 A/B/C 中某一种，说明写法不合格。

# 条件分支编写规范

**核心原则**：优先使用扁平的 `if → return` 提前退出风格，避免 `if-else` / `if-elseif-else` 链式嵌套。

**适用场景**：业务状态判断、接口选择、权限 / 按钮显隐、异常兜底、提交前校验、枚举分支。

**硬性红线**：能明确判断的业务枚举必须逐个显式判断；禁止把“剩余情况”默认等同于某个具体业务类型。

**目的**：减少嵌套层级，提高可读性，新增分支时只需在末尾 `return` 前插入新的 `if` 块。

**代码示例**：

```javascript
// ❌ 不推荐 - if-else 链式嵌套
function getFilteredItems(type, items) {
  if (type === "a") {
    return items.filter((item) => item.parentId === 1);
  } else if (type === "b") {
    return items.filter((item) => item.value === 2);
  } else {
    return items;
  }
}

// ✅ 推荐 - 扁平 if + 最后 return
function getFilteredItems(type, items) {
  if (type === "a") {
    return items.filter((item) => item.parentId === 1);
  }
  if (type === "b") {
    return items.filter((item) => item.value === 2);
  }
  // 其他场景：返回全部
  return items;
}
```

**判断标准**：

- 每个分支独立判断，用 `if` + 提前 `return` 处理
- 默认行为放在函数/回调末尾作为最终 `return`
- 新增场景时只需在末尾 `return` 前插入新的 `if` 块，无需修改已有分支

## 明确分支优先规范

**核心原则**：当业务条件可以明确判断时，必须显式写出对应分支，禁止为了省代码量用默认分支吞掉其他可明确判断的场景。兜底分支只用于未知、异常、兼容历史脏数据等确实无法提前枚举的情况。

**正向精准判断优先**：

- 当业务规则命中的是某几个明确枚举值 / 状态值时，必须正向列出这些值，例如 `A || B` 或常量集合 `includes(A, B)`；禁止用 `value !== X`、`!isXxx`、“非 A” 等取反方式，把剩余值偷懒归为同一业务场景。
- 正向判断不是只针对字段名像 `status` / `type` 的变量。只要条件表达的是“命中某个明确业务场景 / 业务分支 / 业务能力 / 业务来源”，无论字段名是 `source`、`mode`、`flag`、`code`、`key`、`bringType` 还是其他业务字段，都必须优先正向判断命中的明确值；禁止用 `!==`、`!isXxx` 或“非目标值”把未枚举的其他业务场景静默吞掉。
- 只有业务本身明确是“排除某类后的全部剩余情况”，或需求 / 接口文档明确写明“除 X 外均按 Y 处理”时，才允许使用取反判断；代码附近必须写明依据和影响范围。
- 枚举值未确认时，禁止通过反向判断绕过缺失枚举；必须先确认真实 value，或用 `TODO待联调_值_用途描述` 标记后再做正向判断。
- 多个明确类型共享同一逻辑时，优先使用有业务语义的常量集合表达命中范围；后续新增枚举时只扩展集合，禁止让新增枚举自动落入旧的取反逻辑。

```javascript
// ❌ 禁止 - 用“非 C”偷懒覆盖 A/B，未来新增 D 会误入旧逻辑
function isTargetScene(type) {
    return type !== TYPE_C
}

// ✅ 正确 - 正向列出当前确认命中的业务类型
const TARGET_SCENE_TYPES = [TYPE_A, TYPE_B]

function isTargetScene(type) {
    return TARGET_SCENE_TYPES.includes(type)
}
```

```javascript
// ❌ 禁止 - 当前只确认“目标来源”需要刷新，却用反向判断吞掉其他来源
if (source !== TARGET_SOURCE) return
refreshList()

// ✅ 正确 - 明确命中目标业务来源时才刷新
if (source === TARGET_SOURCE) {
    refreshList()
}
```

```javascript
// ❌ 禁止 - 只写一个明确分支，其余全部默认处理
if (targetType === TARGET_TYPE_SUPPLIER) {
    return getSupplierOptions()
}

return getCustomerOptions()

// ✅ 正确 - 能明确的分支逐个写清楚
if (targetType === TARGET_TYPE_SUPPLIER) {
    return getSupplierOptions()
}

if (targetType === TARGET_TYPE_CUSTOMER) {
    return getCustomerOptions()
}

// 未知类型才走兜底，避免后续新增类型时误走客户逻辑
return []
```

**判断标准**：

- 能通过枚举、状态码、类型字段明确判断的分支，必须显式判断。
- 禁止把“剩余情况”默认等同于某个具体业务类型。
- 兜底分支必须表达未知/异常/兼容场景，并在代码附近写明原因。
- 后续拓展新类型时，应新增独立分支，而不是复用旧兜底逻辑。

## 兜底值使用规范

**核心原则**：兜底值必须有明确业务目的，禁止为了消除报错、让页面看起来正常、让校验通过而随手使用 `??`、`||` 或默认枚举值。兜底不能掩盖接口缺字段、历史脏数据或业务状态异常。

**兜底必须告知用户**：任何兜底逻辑完成后都必须在最终回复中明确告知用户，不能只写在代码里，也不能等用户审查 diff 才发现。告知内容至少包括兜底位置、兜底值或兜底策略、依据、影响范围和后续是否需要后端 / 用户确认。

**使用兜底前必须先判断目的**：

1. **新增初始化**：允许使用明确业务默认值，例如新增表单默认选中第一个类型
2. **纯展示占位**：允许使用 `value ?? '-'`、`list ?? []` 等不影响提交和业务判断的占位
3. **可选字段默认**：允许对非必填、非关键字段做空值兜底，例如 `remark ?? ''`
4. **历史脏数据兼容**：必须写明兼容原因，并通过提示、禁用提交、异常状态或上报让问题可感知
5. **必填字段 / 枚举 / ID / 金额 / 状态 / 提交参数**：禁止静默兜底，必须校验缺失并显式处理异常
6. **接口字段链式兜底**：只有接口文档、后端说明、历史兼容说明或明确业务规则证明多个字段语义等价时，才允许 `a ?? b ?? c` 这类链式兜底；否则禁止为了“看起来有值”跨字段兜底

**禁止行为**：

- 禁止在编辑详情回显时，把接口缺失的必填枚举默认成第一个选项
- 禁止接口字段缺失时用本地默认值继续提交，导致错误数据被保存
- 禁止用兜底让表单校验“看起来通过”
- 禁止用 `||` 兜底可能为 `0`、`false`、空字符串的有效业务值
- 禁止把接口中语义相近但来源不同的字段串成兜底链，例如“轮次方案名称”缺失时兜到“流程当前方案名称”再兜到“流程方案名称”，除非文档明确说明三者可替代
- 禁止用兜底掩盖接口缺字段、缺轮次、缺状态等联调问题；缺失时应暴露为空、标记 `TODO无此联调字段_用途描述`，或反馈后端确认
- 禁止在注释中只写“兜底展示”，必须说明兜底依据，例如“兼容旧接口无 xxx 字段”或“后端确认 A/B 字段语义一致”
- 禁止只在代码注释里说明兜底，不在最终回复里告知用户
- 禁止用静态示例值、默认日期、默认数量、默认名称等让页面看起来完整；没有真实数据时必须暴露缺口或使用 TODO 标记

**代码示例**：

```typescript
// ✅ 允许 - 新增表单初始化，业务明确默认供应商
const formData = {
    businessType: businessTypeOptions[0].value
}

// ❌ 禁止 - 编辑回显缺少类型时静默兜底为供应商，会掩盖接口异常
formData.value = {
    businessType: data.businessType ?? businessTypeOptions[0].value
}

// ✅ 正确 - 编辑回显必填枚举缺失时显式暴露问题，避免错误提交
if (data.businessType == null) {
    ElMessage.error('详情缺少类型，无法编辑')
    return
}

formData.value = {
    businessType: data.businessType
}

// ❌ 禁止 - 没有文档证明这些字段语义等价
const status =
    latestRoundRecord?.actionTypeName ??
    disposalRecord?.currentActionTypeName ??
    disposalRecord?.actionTypeName

// ✅ 正确 - 只取当前业务明确的数据源；缺失时让问题暴露
const latestStatus = latestRoundRecord?.actionTypeName
```

**最终回复格式**：

```md
兜底逻辑：
- 位置：xxx
  策略：缺少 xxx 时显示 / 提交 / 判断为 xxx
  依据：xxx
  影响：影响 xxx
  后续：无需处理 / 待后端补字段 / 待用户确认
```

**判断标准**：

- 兜底后是否会影响保存、查询参数、接口参数或业务分支；会影响则不能静默兜底
- 兜底值是否只是展示占位；只是展示占位才允许简单兜底
- 兜底是否会让接口缺字段、脏数据、异常状态看起来正常；会掩盖问题则禁止
- 必填字段缺失时必须显式报错或阻断流程，不能用默认值绕过
- 链式兜底中的每个字段是否有明确等价依据；没有依据时必须删除兜底或反馈确认
- 最终回复是否已明确列出本次新增或调整的所有兜底逻辑；未说明则视为交付不完整

# 交互前置状态与重复提示规范

**核心原则**：当交互入口已经通过禁用态、显隐、表单校验、路由守卫等方式阻止用户触发时，业务函数内部不要再重复写同一前置条件的提示和兜底逻辑。

**禁止行为**：

- 按钮已通过 `:disabled="!hasSingleSelected"` 禁用时，在 `handleEdit(row)` 中再次提示“请选择一条数据”
- 计算属性已经用于控制按钮禁用态时，又返回“请选择一条数据”作为 tooltip 业务原因
- 表单组件已经通过 `required` 自动校验时，又在提交函数中重复写同字段空值提示
- 为了“保险”在每个函数入口都写无业务意义的 `if (!xxx) { message; return }`

**正确做法**：

- 前置交互状态由入口控制，例如按钮禁用、表单校验、显隐控制
- 业务函数内部只处理真正可能发生的业务异常、接口异常、并发状态或权限变化
- Tooltip 只展示业务禁用原因，例如“系统预置项无法删除”“已被模板引用”，不要展示入口层已处理的“请选择一条数据”
- 如果函数可能被多个入口复用，且某些入口无法保证前置条件，应把无提示的安全返回与入口层提示分开处理

## 操作按钮带业务提示规范

**核心原则**：当按钮文案旁需要展示业务说明、风险提示或多行提示时，禁止在 `el-button` 内直接使用默认绝对定位模式的 `com-tips-wrapper`，否则图标可能压住按钮文字。

**正确做法**：

- 按钮内部必须使用 `mode="inline"`，让提示图标参与按钮内容布局
- 提示内容只说明业务原因或操作影响，不展示“请选择一条数据”这类已由禁用态表达的前置条件
- 多行提示可在 `content` 中使用 `<br />`

**代码示例**：

```vue
<el-button>
    <com-tips-wrapper content="第一行提示<br />第二行提示" mode="inline">
        删除
    </com-tips-wrapper>
</el-button>
```
