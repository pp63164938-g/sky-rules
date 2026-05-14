---
description: Kunlun 页面生成 (严格按照 dev-template 模板，绝对克隆，禁止凭空发散四不像代码)
---

# Kunlun 页面生成工作流 (kl.gen-page)

适用场景：新建标准页面。

> [!CAUTION]
> **绝对不可越线原则：**
> 任何生成的页面必须 **100% 同构参考** `src/components/dev-template/` 目录里的骨架代码（如 `list-a.vue`、`list-b.vue`、`tab-template`）。
> **禁止**擅自使用老项目或其他框架带来的旧语法与习惯！
> **禁止**自行发明或拼接未曾出现在的模板里的复杂逻辑（例如脱裤子放屁抽离出 `data.tsx`、强行改造 `useTable` 把分页截留到自建的 `getTableData` 中、手工编写复杂的 `handleActiveFormParams` 和 `settingSearchFrom` 等）。
> **一切必须与模板结构如出一辙，不能做四不像！如果需求里明确加了某组件（例如 sky-summary 汇总），才可以在对应插槽上添置。**

## 执行指引

1. **动笔前强制 `view_file` 看源码骨架**
   务必先打开 `d:\project\kunlun\2\skyline-kunlun-ui-main\src\components\dev-template\` 下的标准件进行通读：
   - 如果是搜素A（常规表单独立）：`list-a.vue`
   - 如果是搜索B（表单进折叠）：`list-b.vue`
   - 如果有Tab页面：`tab-template/index.vue`

2. **防“四不像”高危雷区对照单**
   - 🔴 **雷区 1：外拆配置**
     - ❌ 像老 Vue2 项目一样建一堆如 `data.tsx`、`config.js` 的文件导出 `columns`。
     - ✅ **正解：** 全部内联，就在本 `index.vue` 里面的 `useTable` 方法声明内部去写 `[ { label: '...', prop: '...' } ]` 即可。 
   - 🔴 **雷区 2：剥离 `fn` 原生生态**
     - ❌ 把 `useTable` 原本自带并吐出的 `fn` 给丢弃，自己在 `<sky-table-pagination :fn="getTableData">` 里单独接管分页获取逻辑。
     - ✅ **正解：** `<sky-table-pagination :fn="fn">`，并直接在 `useTable` 第二个参数 `{ fnApi: 你的API方法 }` 进行赋值。若只是占位接口且页面暂不需要可视化数据，可临时用 `{ fnApi: () => Promise.resolve({ data: { records: [], total: 0 }}) as any }` 占位；若进入静态开发并需要页面可预览，则必须按“雷区 8”在 API 层提供精简 Mock 数据。
   - 🔴 **雷区 3：复杂化搜索表单事件**
     - ❌ 自己实现 `@search="onSearch"` 并且还在方法里搞一堆 `removeEmpty(handleActiveFormParams(...))` 然后才更新刷新列表，并创建 `settingSearchFrom` 保存参数。
     - ✅ **正解：** 表单的触发就直接 `<sky-search-form-a @search="tableLoad(searchForm)" ...>` 结束战斗！如果有旁支获取聚合数据的操作，才自定义一个方法，并在内部纯粹地调用 `tableLoad(searchForm.value)` 和其余获取方法即可。
   - 🔴 **雷区 4：表单与表格字段及下拉选不带语义前缀或未保持一致**
     - ❌ `searchForm` 或 `columns` 的配置里的属性直接写原始键名，或者下拉选项随意命名为 `TODO待联调_状态Options` 但其实真正绑定的表单字段叫 `form_TODO待联调_状态`。
     - ✅ **正解：** 
       - 表单字段绑定的 `prop` 及 `v-model` 必须带 `form_` 开头（如 `form_TODO待联调_用户名`）；
       - 表格列的 `prop` 必须带 `table_` 开头（如 `table_TODO待联调_用户名`）；
       - **下拉列表接收变量名必须与所绑定的表单字段名完全一致并仅在末尾附加 `Options`**（例如：如果所绑定的字段为 `form_TODO待联调_状态`，则选项配置名必须严格声明为 `const [form_TODO待联调_状态Options]`，并以 `:options="form_TODO待联调_状态Options"` 的方式传入）。
   - 🔴 **雷区 5：主观猜测导入路径**
     - ❌ 凭主观经验直接手写未确认的工具包或组件路径，例如 `import request from '@/utils/request'`，导致严重的类型与位置错误。
     - ✅ **正解：** 除非完全确定，否则必须使用工具去 `view_file` 或搜索本项目真实正在生效的其他代码中的正确文件引用形式，确保完全契合此项目的基建位置。
   - 🔴 **雷区 6：临时权限标识随意发散**
     - ❌ 自行根据操作名编造不同的权限标识占位符（如 `v-sky-authorize="'TODO：业务批量确认操作权限'"`）。这会导致在未配置真实权限前，与本项目设定的临时权限本地降级方案脱节。
     - ✅ **正解：** 开发期针对权限待确定的按钮或功能节点，**必须统一、恒定地使用 `v-sky-authorize="'TODO：功能权限待配置'"` 这一字符串**，项目钩子中存在专门针对本地环境（DEV）的检测策略来统一放行它。
   - 🔴 **雷区 7：汇总组件（sky-summary）随意挂载与生命周期混乱**
     - ❌ 自行将汇总接口调用的动作放入 `onMounted`，或者随意用 `watch` 监听表格数据变化再去拉汇总，没有和表格的查询条件参数相互绑定。
     - ✅ **正解：** 如果需求指出需要数据汇总控制台，`src/components/dev-template/` 下的基础骨架中已被预留好了相关的 `<template #tool>` 插槽与对应的 `getSummaryData` 获取方法结构。**必须直接使用该解法**；并保证获取动作**必须且只能**被挂载接管于 `useTable` 的 `loadAfter: (params) => getSummaryData(params)` 钩子中触发，以确保每次列表发生查询变化时，自动联动刷新底部的汇总数据！
   - 🔴 **雷区 8：静态开发期 Mock 过度工程化**
     - ❌ 在 API 文件里为临时 Mock 抽离一堆 `MOCK_*` 常量、字段映射、过滤函数、分页函数，甚至完整模拟后端查询逻辑。
     - ❌ 在组件里内联 Mock 数据，或者为了临时展示改造 `useTable` / `fn` / 搜索事件链路。
     - ✅ **正解：** 静态开发期无真实接口时，Mock 数据只放在 API 函数内部，用 `// @mock-start 联调时删除` 和 `// @mock-end` 包住；函数内直接返回 3-5 条贴合表格列语义的 `records`，`total` 直接写对应条数即可。
     - ✅ **正解：** Mock 只负责撑起页面展示和列宽校验，不模拟复杂后端能力；不要额外实现筛选、分页、排序、字段映射等临时逻辑，除非用户明确要求。
     - ✅ **正解：** `// @mock-end` 后保留被注释的正式 `request` 代码，保留真实入参变量，联调时只需删除 Mock 块并放开正式请求。
   - 🔴 **雷区 9：导出按钮（com-download）未走下载中心模式**
     - ❌ 自行手写原生下载逻辑，或在无特殊理由的情况下直接使用 `getOther` 模式。
     - ✅ **正解：** 导出功能**必须优先使用 `com-download` 组件的下载中心模式**，按以下优先级选用：
       1. **极简模式（最推荐）**：直接传 `api` 属性，组件内部全权处理：
          `<com-download api="/v2/导出请求地址" :data="() => searchParams" />`
       2. **复杂逻辑模式**：导出前需二次组装参数时使用 `getInfo`：
          `<com-download :get-info="onExport" />`
       3. 仅当接口已直接返回最终 URL 时，才允许使用 `getUrl`。
       4. `getOther` 仅限下载中心以外的自定义下载场景（文件流、第三方链接等），组件此时仅提供统一按钮样式和 loading 管理。
       - 具体用法参见 `src/components/common/com-download.vue` 文件顶部注释。
   - 🔴 **雷区 10：遗漏 `useCustomizeField` 或自行发散唯一标识**
     - ❌ 认为原型图中没有画出“自定义列”的设置图标，就在开发标准列表页时直接省略 `useCustomizeField` 的接入；或者在不知道精确标识符时，自行胡乱编造。
     - ✅ **正解：** 只要是标准的查询列表页（使用了 `sky-search-form-a` 和 `sky-table-pagination`），**无论产品原型是否明确标出，都必须固定强制接入 `useCustomizeField`**。必须为其分配全局唯一的标识符，**在静态开发且无法精确确定标识符时，严禁自行发散，必须使用 TODO 占位**。最后将返回的属性准确绑定到对应组件上。
       ```vue
       // 脚本部分（不确定标识时必须用 TODO 占位）
       const { searchAProps, fieldTableProps, dateMode } = useCustomizeField('TODO待联调_自定义列唯一标识', () => tableLoad())
       
       // 模板部分
       // <sky-search-form-a v-bind="searchAProps" ...>
       // <sky-table-pagination v-bind="fieldTableProps" ...>
       ```
   - 🔴 **雷区 11：遗漏路由配置**
     - ❌ 新建页面后，认为视图代码写完即完成任务，没有去检查和配置路由，导致页面无法在系统中实际访问。
     - ✅ **正解：** 新建全新页面后，**必须**主动搜索并更新 `src/router/` 目录下对应业务模块的路由配置文件（例如 `oc-routes.ts`、`crm-routes.ts` 等），添加正确的 `path`、`name` 和 `component` 映射，确保页面可被正确路由加载。
   - 🔴 **雷区 12：遗漏 API 的全局异常提示配置**
     - ❌ 在定义 API 时，不加 `message` 参数，导致接口报错时没有全局的错误拦截提示；或者在每个接口里硬编码写死 `message: true`，导致后期无法统一调整。
     - ✅ **正解：** 在定义所有可能需要报错强提醒的 API（包括查询、操作等）时，**必须**参考 CRM 模块的规范，在 API 文件的头部统一声明 `const message = true // 默认开启异常提醒`，然后在 `request` 配置中传入简写的 `message`。由统一拦截器自动接管并抛出业务异常提示。至于成功提示（`ElMessage.success`），仍然由业务方在 `try` 块内按需手动抛出。
   - 🔴 **雷区 13：操作按钮位置不规范（含导出等特殊按钮）**
     - ❌ 在未明确要求的情况下，将“编辑”、“删除”等操作按钮放在表格最右侧的“操作列”中；或在毫无依据的情况下，擅自使用 `<template #right>` 将导出按钮强行挤到表格右上角。
     - ✅ **正解：** 所有操作的按钮（包括新增、批量操作、针对单条数据的“编辑”，以及 **导出等特殊按钮**），**默认必须全都在表格的左上角**！即直接放置在 `<com-header-between table>` 的默认插槽中（无需区分 `#left` 和 `#right`）。**除非用户或需求明确指明需要放在右侧，否则严禁自作主张使用 `<template #right>` 破坏左侧对齐阵型。**
   - 🔴 **雷区 14：Tab 子页面使用了错误的容器组件**
     - ❌ 在开发 Tab 内嵌的子页面时（如 `tabs/tab-xxx.vue`），习惯性地复制了独立页面的 `<com-page-scroll-wrapper>` 和 `<com-page-wrapper-item>`，导致 Tab 切换时高度计算错误或滚动条异常。
     - ✅ **正解：** **但凡是挂载在 Tab 下的子页面**，必须且只能使用 `<com-page-tab-item-wrapper>` 作为根容器！同时必须通过 `<template #="{ hFullClass }">` 解构出高度类名，并绑定给内部的 `<sky-table-pagination :class="hFullClass">`，让表格自动撑满剩余高度。严格参照 `src/components/dev-template/tab-template/tabs/tab-list-a.vue`。
   - 🔴 **雷区 15：画蛇添足的 showOverflowTooltip**
     - ❌ 在 `useTable` 的 `columns` 配置中，手动为普通文本列写上 `showOverflowTooltip: true`。
     - ✅ **正解：** `sky-table-pagination` 底层默认已为所有列开启了超出截断与 Tooltip 提示功能，**无需且不应显式声明**该属性，除非确需设为 `false` 来关闭提示或允许换行。
   - 🔴 **雷区 16：时间字段列宽分配不合理**
     - ❌ 针对时间类字段没有设定宽度，导致在不同屏幕尺寸下可能出现折行或挤压，影响阅读体验。
     - ✅ **正解：** 只要是包含完整日期时间的字段（例如展示格式为 `YYYY-MM-DD HH:mm:ss`），在 `columns` 配置中**必须为其显式设置 `minWidth: 160`**，确保时间信息始终保持单行完整展示。
