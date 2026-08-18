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
   - 如果是详情页：`detail.vue`

2. **防“四不像”高危雷区对照单**
   - 🔴 **雷区 0：SFC 块顺序不按 dev-template**
     - ❌ 按个人习惯把 `<script>` 写在 `<template>` 前面，或者只复制模板逻辑、不复制 SFC 文件结构。
     - ✅ **正解：** 生成 `.vue` 文件时，必须连同 SFC 块顺序一起克隆 `src/components/dev-template/` 对应模板；模板是 `文件头注释 → <template> → <script> → <style>`，新页面也必须保持同样顺序。
     - ✅ `list-a.vue`、`list-b.vue`、`dialog-update.vue` 当前均为 `<template>` 在上、`<script>` 在下；页面和弹窗生成时必须保持这个顺序。
     - ✅ 完成后必须用搜索或读取文件确认目标文件与模板的块顺序一致，例如检查 `^<template>`、`^<script>`、`^<style>` 出现顺序；如果不一致，必须先修正再交付。
   - 🔴 **雷区 1：外拆配置**
     - ❌ 像老 Vue2 项目一样建一堆如 `data.tsx`、`config.js` 的文件导出 `columns`。
     - ✅ **正解：** 全部内联，就在本 `index.vue` 里面的 `useTable` 方法声明内部去写 `[ { label: '...', prop: '...' } ]` 即可。 
   - 🔴 **雷区 2：剥离 `fn` 原生生态**
     - ❌ 把 `useTable` 原本自带并吐出的 `fn` 给丢弃，自己在 `<sky-table-pagination :fn="getTableData">` 里单独接管分页获取逻辑。
     - ✅ **正解：** `<sky-table-pagination :fn="fn">`，并直接在 `useTable` 第二个参数 `{ fnApi: 你的API方法 }` 进行赋值。若只是占位接口且页面暂不需要可视化数据，可临时用 `{ fnApi: () => Promise.resolve({ data: { records: [], total: 0 }}) as any }` 占位；若进入静态开发并需要页面可预览，则必须按“雷区 8”在 API 层提供精简 Mock 数据。
   - 🔴 **雷区 2 补充：弹窗内列表也必须沿用 list-a 数据生态**
     - ❌ 在弹窗、抽屉、Tab 子区里只要出现 `sky-search-form-a + sky-table-pagination + 接口列表`，禁止自行写 `tableRef + getTableData + handleParams + settingSearchForm` 接管分页和搜索。
     - ✅ **正解：** 容器可以按弹窗模板使用 `sky-dialog`，但搜索、表格和接口列表逻辑必须沿用 `list-a.vue` 的内部生态：`useTable(...)` 返回 `columns / fn / tableLoad / tableRef`，表格绑定 `:fn="fn"`，搜索触发 `tableLoad(searchForm)`。
     - ✅ 静态开发需要可视化数据时，Mock 仍放在 API 层；组件不改造 `useTable` / `fn` 链路。
   - 🔴 **雷区 3：复杂化搜索表单事件**
     - ❌ 自己实现 `@search="onSearch"` 并且还在方法里搞一堆 `removeEmpty(handleActiveFormParams(...))` 然后才更新刷新列表，并创建 `settingSearchFrom` 保存参数。
     - ✅ **正解：** 表单的触发就直接 `<sky-search-form-a @search="tableLoad(searchForm)" ...>` 结束战斗！如果有旁支获取聚合数据的操作，才自定义一个方法，并在内部纯粹地调用 `tableLoad(searchForm.value)` 和其余获取方法即可。
   - 🔴 **雷区 3 补充：搜索 A 禁止退回裸表单项**
     - ❌ 使用 `sky-search-form-a` 时，禁止手写 `sky-search-form-item-a + el-input / el-select`，再自己维护搜索参数转换。
     - ✅ **正解：** 按 `list-a.vue` 使用 `com-form-input`、`com-form-select`、`business-*` 等表单组件；搜索项的 `prop` 与 `v-model` 字段保持一致。
     - ✅ 除非当前组件确实没有对应 `com-form-*` 能力，才允许局部使用原生组件，并必须说明原因。
   - 🔴 **雷区 4：表单与表格字段及下拉选缺少阶段区分**
     - ❌ 静态开发 / 未联调阶段缺字段依据时，把临时字段伪装成正式接口字段，导致后续联调无法搜索定位。
     - ❌ 联调确认后，已经确认的字段、枚举、Options 仍继续使用 `form_`、`table_`、`mock`、`temp`、`待联调` 等临时开发命名，导致正式代码看起来像联调占位。
     - ❌ 为了套模板，在已确认接口字段上机械增加 `form_` / `table_` 前缀，导致 `searchForm` / `formData` 字段名和接口参数字段名不一致。
     - ❌ 需求需要下拉 / 远程搜索时，没有对应下拉接口，却拿分页接口、列表接口或相似页面接口硬包装成 Options，例如没有“考核模板下拉接口”时用“评估模板分页查询”包装 `templateIdOptions`。
     - ❌ 缺少接口或数据源时，直接删除搜索项、按钮、页签、表格列、弹窗区域，只在代码注释里说明缺口，导致用户以为需求不存在。
     - ✅ **正解：** 
       - 静态开发 / 未联调阶段允许使用 `form_`、`table_`、`TODO待联调_` 等临时命名预留，但必须可搜索、可定位，不能伪装成正式字段；
       - 已经通过接口文档、抓包或后端确认的表单字段，`prop` 与 `v-model` 必须直接使用接口参数字段名，不再额外套 `form_` 前缀；
       - 已经确认的表格列 `prop` 必须直接使用接口响应字段名，不再额外套 `table_` 前缀；
       - 未确认字段才使用 `TODO待联调_用途描述` 或 `TODO无此联调字段_用途描述`，并在联调后替换为真实字段或保留可搜索缺失标记；
       - **下拉 Options 变量必须按接口字段链路命名**：`status` 的下拉就是 `statusOptions`，`templateId` 的远程下拉就是 `templateIdOptions` / `templateIdOptionsDispatch`。禁止为了套模板机械命名成 `form_考核状态Options`，也不要把已确认字段改成难以和接口字段对应的中文变量名。
       - 缺少接口但需求入口明确存在时，必须保持真实功能应有的控件形态、绑定和交互，只在最终字段、参数、Options 或动作标识处使用 `TODO待联调_用途描述` 预留。禁止仅因接口待开发新增禁用态、待联调提示、过滤函数、影子状态或临时流程；静态成功统一放在 API 层 Mock。
   - 🔴 **雷区 4 补充：下拉接口返回 `id/name` 时重复手写转换**
     - ❌ 对接口返回的标准 `id/name` 下拉数据手写 `data.map(item => ({ label: item.name, value: item.id }))`。
     - ✅ **正解：** 必须优先复用项目公共转换工具：
       `import { getIdName2ValueLabelList } from '@/components/common/form/utils'`
       并在 `useSimpleSelecter` 中使用：
       `transform: data => getIdName2ValueLabelList(data ?? [])`
     - ✅ 只有接口返回结构不是标准 `id/name`，或需要保留额外字段、特殊 value 规则时，才允许按业务显式转换，并在代码附近说明原因。
   - 🔴 **雷区 4 补充：标准下拉 Options 取项手写查找**
     - ❌ 对已经符合 `CommonEnum` / 标准 `{ label, value }` 结构的下拉 Options，手写 `xxxOptions.find(optionItem => optionItem.value === value)` 获取选中项。
     - ❌ 只为了读取选中项的额外字段，重新封装本地查找函数或重复写查找逻辑。
     - ✅ **正解：** 必须优先复用项目公共方法：
       `import { getListOption } from '@/components/common/form/utils'`
       `const xxxOption = getListOption(value, xxxOptions)`
     - ✅ 只需要展示 label 时，使用同位置公共方法 `getListOptionLabel(value, xxxOptions)`；需要读取单位、颜色、状态配置等额外字段时，先用 `getListOption` 获取完整 option，再读取对应字段。
     - ✅ 只有 Options 不是标准 `{ label, value }` 结构，或匹配字段不是 `value` 时，才允许先显式转换成标准 Options；不要在业务文件里重复手写查找逻辑。
   - 🔴 **雷区 4 补充：枚举标签展示优先使用 com-map-tag**
     - ❌ 对枚举 / 状态标签展示，明明项目已有 `com-map-tag`，却手写 `el-tag + getListOptionLabel + 兜底值`。
     - ❌ 只为了区分标签颜色，额外编写 `getXxxTagType(value)`、多段 `if` 分支或本地映射函数，导致和项目推荐的标签映射组件重复。
     - ✅ **正解：** 只要需求是“枚举值映射为标签文案 / 标签颜色”，必须优先使用 `com-map-tag`，并把 label、value、type/color 等配置集中放在对应 Options / TagMap 中。
     - ✅ `com-map-tag` 不局限于列表页；表格列、下拉 option、详情页、弹窗只读状态标签等纯展示位置都应优先使用。
     - ✅ `getListOptionLabel(value, xxxOptions)` 只用于普通文本枚举展示；一旦展示形态是 tag、状态标签、颜色标签，优先级低于 `com-map-tag`。
     - ✅ `com-map-tag` 已内置空值展示、命中映射展示、未命中展示原始值等逻辑，禁止在业务页面重复手写同类兜底。
     - ✅ `com-map-tag` 只负责展示，不作为表单控件；需要 `v-model`、校验、提交的字段，应使用 `com-form-select`、`com-form-radio` 等表单组件。禁用态只读表单字段，优先使用禁用态表单组件复用同一份 Options。
     - ✅ 表格列中的简单标签展示必须由 `formatterRender` 直接返回 `com-map-tag`；只有标签还包含额外业务交互，导致列配置明显变长、难以维护时，才改用列插槽，并说明原因。
     - ✅ `com-map-tag` 的统一展示属性必须优先写在组件 props 上，例如同一列所有标签都不需要圆角时，写 `<com-map-tag :value="value" :map="xxxStatusOptions" :round="false" />`。
     - ✅ 只有某个枚举项需要不同于其他枚举项的展示属性时，才把 `round`、`size`、`effect`、`class`、`style` 等写进 Options / TagMap 的对应项。
     - ❌ 禁止所有枚举项都重复写相同展示配置，例如每个 option 都写 `round: false`、相同 `size` 或相同 `effect`；这类统一样式应外提到组件 props。

     ```vue
     <!-- ❌ 禁止：普通枚举标签展示手写 el-tag 和兜底链 -->
     <template #col_xxxStatus="{ value }">
         <el-tag :type="getXxxTagType(value)">
             {{ getListOptionLabel(value, xxxStatusOptions) ?? value ?? '-' }}
         </el-tag>
     </template>

     <!-- ✅ 正确：简单标签映射通过 formatterRender 返回项目约定的 com-map-tag -->
     <script setup lang="tsx">
     const columns = [
         {
             label: '业务状态',
             prop: 'xxxStatus',
             formatterRender: ({ value }) => <com-map-tag value={value} map={xxxStatusOptions} />
         }
     ]
     </script>

     <!-- ❌ 禁止：所有项都重复写相同展示属性 -->
     <script setup lang="ts">
     const xxxStatusOptions: CommonEnum<{ type: 'success' | 'warning'; round: boolean }> = [
         { label: '状态A', value: 1, type: 'success', round: false },
         { label: '状态B', value: 2, type: 'warning', round: false }
     ]
     </script>

     <!-- ✅ 正确：统一展示属性写在组件 props 上 -->
     <script setup lang="tsx">
     const xxxStatusOptions: CommonEnum<{ type: 'success' | 'warning' }> = [
         { label: '状态A', value: 1, type: 'success' },
         { label: '状态B', value: 2, type: 'warning' }
     ]

     const columns = [
         {
             label: '业务状态',
             prop: 'xxxStatus',
             formatterRender: ({ value }) => <com-map-tag value={value} map={xxxStatusOptions} round={false} />
         }
     ]
     </script>

     <!-- ✅ 正确：下拉 option 中的状态标签也复用 com-map-tag -->
     <template #option="optionItem">
         <span>{{ optionItem.label }}</span>
         <com-map-tag :value="optionItem.status" :map="xxxStatusOptions" />
     </template>
     ```
   - 🔴 **雷区 4 补充：下拉 Options 未显式声明类型**
     - ❌ `com-form-select` 使用的 `options` 变量不声明类型，或 `useSimpleSelecter` 不传泛型，导致类型无法和 `com-form-select` 的 `options?: CommonEnum` 对齐。
      - ✅ **远程下拉正解：** 使用 `useSimpleSelecter<CommonEnumItem>` 或明确的业务下拉项类型，并按接口字段链路命名：
        `const [templateIdOptions, templateIdOptionsDispatch] = useSimpleSelecter<CommonEnumItem>(...)`
      - ✅ **静态下拉正解：** 使用 `CommonEnum` 显式标注，并按接口字段链路命名：
        `const statusOptions: CommonEnum = [{ label: '启用', value: 1 }]`
     - ✅ 若下拉项需要保留额外字段，必须定义清晰的扩展类型，并让 `useSimpleSelecter<xxx>` 与 `com-form-select` 的实际选项结构保持一致。
   - 🔴 **雷区 4 补充：枚举与常量未按指定规范处理**
     - ❌ 需求写了“枚举值：人工编辑、系统计算”，却把字段当普通输入框处理，或在列表 / 弹窗里直接写死中文展示。
     - ❌ 仅用于下拉展示和提交的静态枚举，禁止为每个枚举值机械声明 `xxx人工编辑 = '人工编辑'`、`xxx系统计算 = '系统计算'` 这类常量。
     - ❌ 单次使用的 Tab 标识、场景值、请求值、普通文案或 Mock 值，禁止仅因为名称较长、带 TODO、方便联调替换或以后可能复用就提前抽成常量。
     - ✅ **指定规范：** Kunlun 页面中的枚举建模、常量抽离和待联调值处理，必须严格执行全局“函数抽象边界规范”“枚举映射规范”和“禁止静默发散规范”，本工作流不另设常量口径。
     - ✅ 静态枚举统一声明 `CommonEnum` Options；普通文本展示复用 `getListOptionLabel(value, xxxOptions)`，标签展示优先使用 `com-map-tag`，表单使用 `com-form-select` / 单选等枚举组件。
     - ✅ 仅用于 Options 展示、默认值和提交的枚举值，直接在 Options 中维护 `label/value`，默认值优先从 `xxxOptions[0].value` 等已确认项取得，不拆枚举项常量。
     - ✅ 需求只给中文枚举展示值、未给接口 id/code 时，应先区分用途：纯展示或文档明确提交中文时，`options.value` 才可暂用中文；只要该值会参与业务判断、状态分支、禁用规则、按钮显隐、接口参数分支、组件 `active-value/inactive-value` 等逻辑，就必须使用 `TODO待联调_值_用途描述` 占位，例如 `TODO待联调_值_业务状态启用` / `TODO待联调_值_业务状态禁用`，联调时再替换为后端 id/code/value。
     - ✅ 模板中可以显式写 `if / else-if` 表达复杂业务分支，但分支条件必须基于接口值、枚举 value 或 TODO 待联调值，不能直接用“启用 / 禁用 / 系统计算”等展示文案判断。
     - ✅ 只有已确认值被多个独立业务分支使用、跨文件复用，或形成稳定前端协议 / 明确业务集合时，才抽常量，并用 JSDoc 说明来源、具体值含义和使用范围。
   - 🔴 **雷区 5：主观猜测导入路径**
     - ❌ 凭主观经验直接手写未确认的工具包或组件路径，例如 `import request from '@/utils/request'`，导致严重的类型与位置错误。
     - ✅ **正解：** 除非完全确定，否则必须使用工具去 `view_file` 或搜索本项目真实正在生效的其他代码中的正确文件引用形式，确保完全契合此项目的基建位置。
   - 🔴 **雷区 6：临时权限标识随意发散**
     - ❌ 在没有菜单管理、接口文档、后端确认、用户确认或项目已有同功能真实权限标识作为依据时，禁止自行推测权限标识，例如 `v-sky-authorize="'sys:XXX'"`、`v-sky-authorize="'xxx:yyy:zzz'"`。
     - ❌ 禁止根据路由路径、页面目录、按钮文案、操作名自行拼接看似合理的权限标识；写了未配置的真实权限，后续既不知道要配，也不知道该配哪个。
     - ❌ 禁止自行根据操作名编造不同的权限占位符，例如 `v-sky-authorize="'TODO：业务批量确认操作权限'"`。
     - ✅ 如果菜单管理、接口文档、后端或用户已经明确提供真实权限标识，才允许按真实值填写。
     - ✅ 如果功能节点需要权限控制，但真实权限标识暂未确认，必须统一使用 `v-sky-authorize="'TODO：功能权限待配置'"` 预留；后续确认菜单权限配置后再替换为真实标识。
     - ✅ 项目钩子中存在专门针对本地环境（DEV）的检测策略，会统一放行 `TODO：功能权限待配置` 这一临时权限占位。
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
     - ❌ 认为原型图中没有画出“自定义列”的设置图标，就在开发标准列表页时直接省略 `useCustomizeField` 的接入；或者根据页面路径、组件名、路由名、业务模块名自行推断唯一标识后直接写入。
     - ✅ **正解：** 只要是标准的查询列表页（使用了 `sky-search-form-a` 和 `sky-table-pagination`），**无论产品原型是否明确标出，都必须固定强制接入 `useCustomizeField`**。
     - ✅ `useCustomizeField` 的第一个参数必须以菜单管理页面配置的“唯一标识”为准；综合设置等系统页面同样先到菜单管理确认真实唯一标识。
     - ✅ 如果当前无法从菜单管理或用户提供的信息中确认唯一标识，必须使用 `TODO:菜单管理页面【唯一标识】` 占位，不能根据路径或命名习惯推断。
     - ✅ 页面生成或改造完成后，必须主动向用户说明当前使用的唯一标识来源；如果是 TODO 占位，必须提醒用户提供/确认菜单管理中的真实唯一标识后再替换写入。
       ```vue
       // 脚本部分（不确定标识时必须用 TODO 占位）
       const { searchAProps, fieldTableProps, dateMode } = useCustomizeField('TODO:菜单管理页面【唯一标识】', () => tableLoad())
       
       // 模板部分
       // <sky-search-form-a v-bind="searchAProps" ...>
       // <sky-table-pagination v-bind="fieldTableProps" ...>
       ```
   - 🔴 **雷区 10 补充：组件 Props 无依据增删**
     - ❌ 看到组件支持某个 prop，就为了“保险”自行追加或覆盖组件默认行为，例如需求和 `list-a.vue` 模板都没有要求时，擅自给表格加 `:dblclick-detail="false"`。
     - ❌ 反过来也不能机械照抄所有模板 props：如果需求明确不需要复选框、批量选择等能力，就不要无脑保留 `show-select`、`primary-key` 等选择相关配置。
     - ✅ **正解：** 组件 Props 必须按“模板基础结构 + 当前需求必要性”取舍：模板里已有且符合当前页面的保留；需求明确需要的补充；需求不需要或没有依据的不要加。
     - ✅ **正解：** 如果某个组件默认行为看起来可能影响业务，但需求没有明确要求修改，必须先询问确认，不能自行通过传 `false`、空值或额外参数去覆盖默认行为。
     - ✅ 示例：需要批量操作或多选时，可以按需求使用 `show-select` 和 `primary-key`；没有多选需求时不要主动添加。需要禁用双击详情时，必须由需求明确提出后再配置 `:dblclick-detail="false"`。
   - 🔴 **雷区 10 补充：表格唯一 Key 禁止自行推断**
     - ❌ 给 `sky-table-pagination`、表格多选、行展开、树表、缓存行状态等能力配置 `primary-key` / `row-key` / 行唯一 key 时，禁止根据字段名看起来像唯一就自行推断，例如把 `code`、`name`、`no` 等展示字段直接当唯一 key。
     - ❌ 禁止为了让选择、删除、编辑或回显逻辑先跑通，临时使用数组下标、列表顺序、前端拼接值作为表格唯一 key。
     - ✅ **正解：** 表格唯一 key 必须来自接口文档、抓包响应、后端确认、用户明确说明，或项目已有同接口真实代码可证明的唯一字段。
     - ✅ 如果当前无法确认唯一字段，但需求又需要多选、批量操作、行展开、跨页选中、编辑删除等依赖行唯一性的能力，必须先和用户沟通确认，不能自行猜测。
     - ✅ 如果需求不需要依赖行唯一性的能力，不要为了“看起来完整”主动添加 `primary-key` / `row-key`。
   - 🔴 **雷区 10 补充：弹窗结构不按模板**
     - ❌ 只要是弹窗，不允许直接把 `<sky-dialog>` / `<el-dialog>` 及其表单逻辑写在列表页 `index.vue` 中。
     - ✅ **正解：** 标准列表页的业务弹窗必须放在当前页面同级 `dialog/` 目录下，例如 `./dialog/dialog-update.vue`。
     - ✅ 列表页只保留打开弹窗的入口函数，通过 `createDefaultComponent` 动态加载弹窗组件。
     - ✅ 新增弹窗必须使用以下调用结构：
       ```ts
       function handleAdd() {
           import('./dialog/dialog-update.vue').then(async component => {
               createDefaultComponent(component.default, {
                   type: 'add',
                   onSubmit: () => tableLoad()
               })
           })
       }
       ```
     - ✅ 编辑弹窗必须使用同类调用结构：
       ```ts
       function handleEdit(row: Omix) {
           import('./dialog/dialog-update.vue').then(async component => {
               createDefaultComponent(component.default, {
                   type: 'edit',
                   id: row.id,
                   onSubmit: () => tableLoad()
               })
           })
       }
       ```
     - ✅ 弹窗内部结构、状态命名、loading 拆分、`dialogValue`、`formData`、`formRules`、`handleConfirm`、`emit('submit')`、`sky-dialog` / `el-scrollbar` / `sky-form` / `common-grid-form` 等细节，必须以 `src/components/dev-template/dialog/dialog-update.vue` 为唯一模板来源。
     - ✅ 生成弹窗前必须先读取 `src/components/dev-template/dialog/dialog-update.vue`，按其现有结构解析复用；除非需求明确要求，不要自行改成 `el-form`、自定义 footer、内联 loading、或其他弹窗骨架。
     - ✅ 弹窗组件内部负责表单回显、校验、提交接口、成功提示和关闭逻辑；列表页只负责打开弹窗和提交成功后的 `tableLoad()` 或按需求无刷更新当前行。
   - 🔴 **雷区 10 补充：编辑弹窗直接依赖列表 row**
     - ❌ 标准编辑弹窗禁止直接接收列表行 `row` 并用 `props.row` 初始化表单，这会让弹窗依赖列表字段结构，也容易遗漏详情接口字段。
     - ❌ `dev-template/dialog-update.vue` 中关于 `row` 的注释不是默认许可，不能因为模板注释提到 `row` 就绕过详情接口。
     - ✅ **正解：** 编辑入口按 `dev-template/dialog-update.vue` 传入 `id`，弹窗 props 使用 `id?: number | string`，并在弹窗内部通过 `updateDetail()` 调详情接口或 API 层静态 detail mock 回显。
     - ✅ 列表行只负责提供唯一标识，不作为编辑表单的数据源。
     - ✅ 后端暂未提供详情接口但编辑弹窗需要回显时，应在 API 层预留详情函数和 mock，保持弹窗主流程与正式联调一致。
     - ✅ 只有用户明确说明无需详情接口、列表数据就是完整编辑数据，或业务组件本身就是行内编辑器时，才允许传 `row`；使用前必须在最终回复里说明原因。
   - 🔴 **雷区 10 补充：弹窗表单布局整行滥用**
     - ❌ 为贴截图或图省事，给新增/编辑弹窗里的所有表单项都加 `class="col-span-full"`，导致标准弹窗从双列网格退化成单列表单。
     - ✅ **正解：** 标准新增/编辑弹窗必须以 `src/components/dev-template/dialog-update.vue` 的 `common-grid-form` 双列网格为默认布局；普通输入框、选择框、开关、只读字段默认占一列。
     - ✅ 只有 `textarea`、备注、说明、附件上传、长文本、复杂自定义块等确实需要横向展示空间的字段，才允许使用 `class="col-span-full"` 跨整行。
     - ✅ 除非设计或需求明确指定特殊宽度，否则不要自行给 `sky-dialog` 加 `width` 覆盖模板默认宽度。
   - 🔴 **雷区 10 补充：表单必填校验重复声明**
     - ❌ 对 `com-form-input`、`com-form-select` 等 `com-form-*` 表单组件已经传了 `required` 时，又在 `useForm` 的 `formRules` 中重复写同字段必填规则。
     - ✅ **正解：** `com-form-*` 组件自身已支持 `required` 并会生成对应必填校验；普通必填场景只写组件上的 `required` 即可。
     - ✅ 只有复杂校验、自定义 validator、跨字段联动校验、或组件 `required` 无法覆盖的业务规则，才允许额外在 `useForm` 第二个参数中声明 `formRules`。
     - ✅ 弹窗模板中若仅存在基础必填项，应保持 `useForm(formData)` 的简单写法，避免为了“保险”重复维护两套校验来源。
   - 🔴 **雷区 10 补充：前置禁用状态重复提示**
     - ❌ 按钮已经通过 `:disabled="!hasSingleSelected"` 禁用时，禁止再在 `handleEdit(row)`、`handleDelete(row)`、计算属性或 tooltip 中重复提示“请选择一条数据”。
     - ❌ `com-form-*` 已经通过 `required` 自动校验时，禁止在提交函数里重复写同字段空值提示。
     - ✅ **正解：** 页面生成时，未选中、未填写这类入口层状态交给按钮禁用、显隐控制或组件校验处理。
     - ✅ 业务函数只处理真正的业务禁用原因或异常状态，例如“系统预置项无法删除”“已被模板引用”“接口返回异常”。
     - ✅ Tooltip 只展示业务原因，不展示已经由禁用态表达的普通前置条件。
   - 🔴 **雷区 10 补充：操作按钮带提示仍使用绝对定位**
     - ❌ 在 `<el-button>` 内直接使用默认模式的 `<com-tips-wrapper>`，导致提示图标绝对定位后覆盖按钮文字。
     - ✅ **正解：** 操作按钮内需要提示时，必须使用 `<com-tips-wrapper mode="inline">按钮文案</com-tips-wrapper>`。
     - ✅ `list-a.vue` / `list-b.vue` 模板已提供“带提示操作”示例，页面生成时按模板复用，不要自行拼裸 `el-tooltip` 或绝对定位图标。
     - ✅ 提示只展示业务说明、风险或影响，不展示已由按钮禁用态表达的普通前置条件。
   - 🔴 **雷区 10 补充：表单组件默认值重复声明**
     - ❌ 未查看 `com-form-input` 源码，就根据需求文档里的“限制 120 / 限制 500”直接给组件补 `maxlength="120"` 或 `maxlength="500"`。
     - ✅ **正解：** 使用 `com-form-input` 前必须先确认组件默认值；当前组件普通输入框默认 `maxlength: 120`，`type="textarea"` 默认 `maxlength: 500`，且 textarea 默认带 `autosize`。
     - ✅ 需求限制与组件默认值一致时，不要重复声明；只有需求限制不同于组件默认值，或业务需要显示字数统计等额外行为时，才显式传入对应 props。
     - ✅ 页面生成时遇到 `com-form-*` 的 `required`、`maxlength`、`clearable`、`autosize` 等常见能力，必须先读组件源码或类型定义，确认默认值后再决定是否传参。
   - 🔴 **雷区 10 补充：标准表单上传优先使用 com-form-upload**
     - ❌ 表单 / 弹窗内出现标准上传字段时，未检查公共组件就直接手写 `el-upload`、文件类型校验、文件大小校验和数量限制。
     - ❌ 上传接口 URL 未确认时，为了套公共组件伪造 `url` 或把占位地址写成确定逻辑。
     - ✅ **正解：** 标准表单上传场景必须先检查并优先使用 `com-form-upload`，复用其 `sky-form-item`、token header、`typeList`、`limitSize`、数量限制和成功提示等公共能力。
     - ✅ 使用前必须先读取 `src/components/common/form/com-form-upload.vue` 源码或类型定义，确认当前需求需要传哪些 props；公共组件已覆盖的校验，不要在业务文件重复手写。
     - ✅ 后端已确认上传接口时，`url` 必须使用真实上传接口；文件类型优先用 `typeList` 表达，文件大小优先用 `limitSize` 表达，数量限制优先走组件透传能力。
     - ✅ 后端未提供上传接口时，禁止伪造正式 `url`，也禁止改成本地选择态或禁用上传；继续使用真实上传组件和交互，只在最终 `url` 绑定位置使用 `TODO待联调_附件上传接口` 预留，最终回复中说明缺口。
     - ✅ 只有复杂自定义上传 UI、纯本地临时选择、拖拽排序等公共组件无法覆盖的场景，才允许局部使用 `el-upload`，并在代码附近说明原因。
   - 🔴 **雷区 10 补充：useForm 泛型兜底**
     - ❌ 弹窗表单中禁止为了省事写 `useForm<Omix>({...})`，这会抹掉表单字段结构，降低类型约束。
     - ✅ **正解：** 标准弹窗按 `dev-template/dialog-update.vue` 使用 `useForm({...})`，让 TypeScript 根据初始化对象自动推断字段类型。
     - ✅ 只有确实存在复杂表单模型、接口模型复用、联合字段或需要显式约束返回结构时，才允许定义明确业务类型并传给 `useForm<业务表单类型>`。
     - ✅ 不允许用 `Omix`、`any` 这类宽泛类型作为“让类型先过”的兜底泛型。
   - 🔴 **雷区 10 补充：业务组件拆分边界**
     - ❌ 禁止为了减少 `index.vue` 或弹窗文件行数，把标准列表页的搜索区、表格区、header 操作区、tool 汇总区，或标准添加/编辑弹窗的普通表单区强行拆成子组件。
     - ❌ 禁止把 `list-a.vue` / `list-b.vue` / `dialog-update.vue` 这类 dev-template 标准骨架拆散使用；模板文件本身表达的就是页面或弹窗主职责。
     - ✅ **正解：** 标准列表页默认保持 `搜索区 + 表格 + columns 列渲染配置 + header/tool 插槽 + 必要的复杂列插槽` 在同一个页面文件中，便于按模板查找和维护。
     - ✅ **正解：** 标准添加/编辑弹窗默认保持 `sky-dialog + sky-form + 表单字段 + 提交/回显` 在同一个弹窗文件中，普通表单字段不单独拆组件。
     - ✅ 只有弹窗或页面内部存在动态表格、复杂配置区、独立校验区、上传/选择器、可复用业务块等明确业务子模块时，才拆分该子模块。
     - ✅ 拆分后的子组件必须有清晰业务边界：子组件负责自身状态、局部交互、局部校验和样式；父组件只负责打开关闭、主提交、接口调用和成功后的列表刷新。
     - ✅ 子组件对外只暴露必要能力，例如 `validate()`、`addRow()`；如果需要大量透传 props、emit、ref 方法，说明边界没有拆清楚，应优先保留在当前文件。
   - 🔴 **雷区 10 补充：详情模板使用边界**
     - ❌ 禁止把 `src/components/dev-template/detail.vue` 当成固定业务模板使用，默认生成“基础信息 / 明细信息 / 操作日志”等业务模块。
     - ❌ 禁止为了还原单个详情页，把折叠头部、概要指标、评分项、审批区、分层规则等具体业务结构写进详情基础模板。
     - ✅ **正解：** `detail.vue` 只表达三类通用结构：表单形式展示、表格形式展示、固定底部操作。
     - ✅ 表单形式展示必须优先使用 `sky-form + sky-form-item`；纯展示内容默认使用 `sky-ellipsis-tooltip` 单行展示，除非需求明确要求多行展示。
     - ✅ 表单布局需要宽屏多列、窄屏自动降列时，使用 `common-auto-grid-form`，不要在详情页重复手写响应式 grid。
     - ✅ 详情字段展示统一使用 `sky-form + sky-form-item` 承载只读字段，不要自行拼 `div + label + value` 结构；这样后续字段从只读展示切换为可编辑表单时，可以沿用同一套表单骨架。
     - ✅ 详情字段布局优先使用项目公共样式 `form-item-content-start common-auto-grid-form` 做弹性列展示，通过 CSS 变量控制最小列宽和列间距；禁止为每个详情页手写 grid、flex 列数，或自行计算 label 最大宽度。
     - ✅ 表格形式展示默认使用 `sky-table-pagination`；只有需求明确是静态规则表、复杂合并表或表格组件无法满足时，才允许使用更贴合业务的表格实现，并说明原因。
     - ✅ 固定底部操作统一使用 `com-page-operate-footer`；无固定底部操作的详情页直接删除该模块。
     - ✅ 详情页中的表单模块、表格模块、底部操作模块都必须按需求复制、删除或改名，标题使用真实业务语义；禁止保留模板里的 `TODO表单模块标题`、`TODO表格模块标题`。
     - ✅ 详情模块标题由详情页内部根据业务模块或详情数据生成，禁止依赖列表页通过 route query 传入展示标题；列表页只传详情查询必需的加密标识。
     - ✅ 详情页内容由详情页内部通过详情接口或本页数据结构生成，禁止让列表页承担详情内容组装职责。
     - ✅ 详情页复杂业务块只有在当前文件明显影响阅读时才拆分，拆到当前详情页同级 `components/` 目录；普通表单展示、普通表格展示不要为了行数强行拆组件。
   - 🔴 **雷区 10 补充：复杂弹窗目录化边界**
     - ❌ 简单新增 / 编辑弹窗禁止为了“看起来规范”强行改成文件夹结构。
     - ❌ 禁止只因为弹窗里出现上传区、选择器、动态表格、提示列表等“复杂 UI”，就直接升级为文件夹结构；目录化的前提是已经需要抽离额外文件，否则文件夹没有实际作用。
     - ❌ 禁止在 `src/components/dev-template/dialogs/` 里开发真实业务弹窗；该目录只用于说明复杂弹窗目录化规范。
     - ❌ 禁止维护第二套完整弹窗模板，例如把 `dialog-update.vue` 的完整内容再复制一份到 `dev-template/dialogs/dialog-xxx/index.vue`，导致两边同步改模板。
     - ❌ 复杂弹窗拆分时，禁止直接新增 `dialog-xxx.vue`、`dialog-update.xxx.vue`，也禁止把 `dialog-xxx-table.vue`、`dialog-xxx-config.vue` 等文件平铺在页面目录下。
     - ✅ **简单弹窗正解：** 弹窗逻辑仍可由单个文件清晰承载时，统一放在页面 `dialog/` 目录下，例如 `dialog/dialog-import-score.vue`，列表页使用 `import('./dialog/dialog-import-score.vue')` 动态加载。
     - ✅ **复杂弹窗正解：** 只有复杂到必须抽离至少一个额外文件时，才在目标业务页面目录下使用文件夹结构，例如弹窗专属 `components/`、`types.ts`、`hooks/`、`dialog-业务名.ts`。
     - ✅ 是否目录化的判断标准不是“弹窗看起来复杂”，而是“单文件是否已经无法清晰表达边界，且确实存在可独立维护的额外文件”。
     - ✅ 复杂弹窗目录化结构：
       ```text
       dialogs/
         dialog-业务名/
           index.vue       # 从 src/components/dev-template/dialog-update.vue 复制后改造
           components/     # 当前弹窗专属组件，按需创建
           dialog-业务名.ts # 当前弹窗专属函数 / 常量，按需创建
           types.ts        # 当前弹窗专属类型，按需创建
           hooks/          # 当前弹窗专属 hooks，按需创建
       ```
     - ✅ 如果目录下只有一个 `index.vue`，没有任何专属子组件、类型、hooks 或工具文件，应退回单文件 `dialog/dialog-业务名.vue`。
     - ✅ 复杂弹窗的 `index.vue` 仍然必须以 `dialog-update.vue` 为唯一骨架来源，保留 `sky-dialog`、`dialogValue`、`loadingState`、`useForm`、`handleConfirm`、`updateDetail` 等主结构，再按业务拆出局部模块。
     - ✅ `components/` 只放当前弹窗专属组件；子组件按业务职责命名，例如 `rule-condition-table.vue`、`import-error-list.vue`，禁止命名成 `table.vue`、`config.vue`。
     - ✅ 列表页动态加载路径：简单弹窗用 `import('./dialog/dialog-业务名.vue')`；复杂弹窗用 `import('./dialogs/dialog-业务名/index.vue')`。
     - ✅ 生成复杂弹窗前，必须先读取 `src/components/dev-template/dialogs/README.md`，确认这是模板规范目录，不是业务开发目录。
   - 🔴 **雷区 11：遗漏路由配置**
     - ❌ 新建页面后，认为视图代码写完即完成任务，没有去检查和配置路由，导致页面无法在系统中实际访问。
     - ✅ **正解：** 新建全新页面后，**必须**主动搜索并更新 `src/router/` 目录下对应业务模块的路由配置文件（例如 `oc-routes.ts`、`crm-routes.ts` 等），添加正确的 `path`、`name` 和 `component` 映射，确保页面可被正确路由加载。
   - 🔴 **雷区 11 补充：详情跳转参数未加密**
     - ❌ 跳转详情页时禁止直接把业务 id、code、单号等明文参数裸放到 `query` 中，例如 `query: { id: row.id }`。
     - ✅ **正解：** 详情跳转必须使用项目公共方法加密参数：
       ```ts
       import { encodeRouteQuery } from '@/utils/utils-common'

       router.push({
           name: 'TODO详情路由Name',
           query: {
               ...encodeRouteQuery({ id: row.id })
           }
       })
       ```
     - ✅ 详情页读取参数必须使用对应公共方法解密，默认直接读取一次即可：
       ```ts
       import { decodeRouteQuery } from '@/utils/utils-common'

       /** 详情页路由参数 */
       const routeQuery = decodeRouteQuery()
       ```
     - ✅ 只有同一个详情组件实例内确实会切换 query 时，才使用 `useRoute + watch` 明确监听并重新拉详情；不要为了“响应式”默认包一层 `computed(() => decodeRouteQuery())`。
     - ✅ 列表页跳详情只传详情查询必需参数；详情页标题、展示内容、模块标题应在详情页内部根据详情数据生成，不通过 query 透传。
     - ✅ 如需跨页携带复杂临时数据，优先参考项目已有 `emitBringData` / `receiveBringData` 用法，不要把大对象直接塞入 route query。
     - ✅ 使用 `emitBringData` / `receiveBringData` 时，必须先查看 `src/utils/utils-common.tsx` 的实现和项目既有用法，确认它是 localStorage 一次性带入机制：发送方先写入再跳转，接收方读取后会清理缓存。
     - ✅ 接收页若可能被 keep-alive 缓存，或同一路由页面可能已经打开后再次从列表页跳入，不能只在 `setup` / 首次挂载时调用 `receiveBringData`；必须同时在首次进入和 `onActivated` 中处理带入数据。
     - ✅ 接收带入数据时必须用 `bringType` 判断来源，并按当前页面模式限制处理范围，例如只在新增 / 创建模式消费，避免编辑、详情、重提等页面误吃跨页缓存。
   - 🔴 **雷区 11 补充：父页面代为生成子页面动态页签标题**
     - ❌ 从列表页进入详情、编辑等独立路由子页面时，为生成工作台页签标题，把业务名称、标题文案或完整列表行通过 route query / bringData 一并传入。
     - ❌ 子页面详情接口已经返回可用于区分页面的名称或编码，却始终使用静态 `meta.title`，导致同时打开多个同类子页面时无法区分页签。
     - ✅ **正解：** 本条“子页面”指从父页面进入的详情、编辑等独立路由页面；Tab 内嵌业务组件不单独生成工作台页签。
     - ✅ 路由 `meta.title` 只作为数据加载前的通用标题。需求需要“页面名-业务名称”等动态页签标题时，由子页面在目标详情接口成功返回后，基于当前接口字段生成标题，并调用项目已有的 `fetchUpdateBookmarkTitle` 更新。
     - ✅ 父页面只传子页面查询必需的加密标识，不为页签标题额外传名称、展示文案或列表行；禁止使用列表快照、bringData 或其他接口字段补动态标题。
     - ✅ 动态标题字段为空时保留路由默认标题，禁止自行拼接空值、占位符或相似字段。标题格式或字段未确认时，先按需求文档、接口文档或用户说明确认。
     - ✅ 新增等不依赖详情接口的子页面，也由子页面根据自身模式和已确认数据决定标题；纯静态标题直接使用路由 `meta.title`，无需重复调用更新能力。

     ```ts
     const route = useRoute()
     const { fetchUpdateBookmarkTitle } = useStore(usePermissions)

     // 详情接口返回业务名称后，由当前子页面更新自身页签标题。
     if (data.TODO业务名称) {
         await fetchUpdateBookmarkTitle(route.fullPath, `TODO页面名-${data.TODO业务名称}`)
     }
     ```
   - 🔴 **雷区 12：遗漏 API 的全局异常提示配置**
     - ❌ 在定义 API 时，不加 `message` 参数，导致接口报错时没有全局的错误拦截提示；或者在每个接口里硬编码写死 `message: true`，导致后期无法统一调整。
     - ✅ **正解：** 在定义所有可能需要报错强提醒的 API（包括查询、操作等）时，**必须**参考 CRM 模块的规范，在 API 文件的头部统一声明 `const message = true // 默认开启异常提醒`，然后在 `request` 配置中传入简写的 `message`。由统一拦截器自动接管并抛出业务异常提示。至于成功提示（`ElMessage.success`），仍然由业务方在 `try` 块内按需手动抛出。
   - 🔴 **雷区 12 补充：API 文件归属过细**
     - ❌ 新增一个页面就默认新建一个 API 文件，例如为了单个“展会邀约对象”页面单独创建 `exhibition-invite-object.ts`，导致 `src/api/xxx/` 下文件越来越碎。
     - ✅ **正解：** 新增接口前必须先查看当前业务模块已有 API 文件，按业务域归属复用已有文件。例如页面属于“活动&推广管理”，且已存在 `src/api/csc/marketing-activities.ts`，则接口应优先追加到该文件中。
     - ✅ 只有当接口属于全新的独立业务域、预计会承载多个页面/一组完整能力，或用户明确要求拆分时，才允许新建 API 文件。
     - ✅ 如果没有充分依据新建 API 文件，也不要在 `src/api/xxx/index.ts` 中新增独立导出命名空间；应沿用既有模块导出，例如 `API.marketingActivities.xxx`。
   - 🔴 **雷区 12 补充：Kunlun API / 类型定义未按指定规范与 URL 路径过度抽离**
     - ✅ **指定规范：** Kunlun API 定义、请求入参、响应类型、类型位置、`Omix` 使用边界和跨接口字段归属，必须严格执行全局“API 函数入参类型定义规范”“API 类型位置默认规范”“API 响应类型定义规范”“跨接口字段归属规范”和“type 与 interface 选择规范”；`kl-gen-page` 不维护第二套口径。
     - ❌ 禁止新写或修改接口时用 `request<Omix>` / `request<Array<Omix>>` 承接已确认响应，再在页面、Hook、下拉回调或跳转逻辑里读取字段。
     - ❌ Kunlun API 实现文件禁止新增顶层 `type` / `interface`；禁止以“不导出、只在当前 API 文件使用”为由，把独立类型留在 API 文件中。
     - ✅ 短小、无嵌套且只使用一次的请求 / 响应结构，直接内联在 API 函数参数或 `request<T>` 泛型中。
     - ✅ 字段较多、结构复杂、被多个 API 使用，或需要被页面、组件、Hook、下拉、跳转、提交参数显式引用的 API DTO，统一放入 `src/api/{module}/interface/{domain}.resolver.ts`。目标模块尚无 `interface/` 目录时，按同一项目结构补齐，不能退回 API 文件声明类型。
     - ✅ 新增 resolver 后必须补齐完整导出链：`src/api/{module}/interface/index.ts` 导出 resolver，再由 `src/api/interface.ts` 导出模块 interface；API、页面和组件通过项目统一出口引用，例如 `import * as env from '@/api/interface'`。
     - ✅ 新增类型前必须搜索 Kunlun 全项目的 API 类型目录、模块出口、统一出口和实际导入方式，禁止只参考当前业务模块或 SRM。CRM、SYS、Public、MC、SRM 等模块现有 resolver 链路都属于项目依据。
     - ✅ resolver 文件沿用项目既有 `interface` 风格；页面表单类型、ViewModel、前端 `_xxx` 扩展字段放页面 / 组件 `types.ts`，不要放进 API resolver，也不要放到 Options / enum 文件。
     - ✅ API 实现文件只保留请求函数、必要导入、请求配置和函数内部 Mock；存量 API 文件中的独立类型属于历史写法，不得作为新代码模板，也不要求本次顺手重构无关存量代码。
     - ❌ 禁止为同一组 API 抽 URL 前缀常量再拼接路径，例如 `XXX_URL_PREFIX + '/page'`。
     - ✅ **正解：** API 函数里的 `url` 必须直接写完整接口路径，便于打开函数时立即确认真实请求地址。
     - ✅ 只有跨环境配置、网关基地址、或项目已有统一请求基建要求时，才允许使用公共路径能力；普通业务接口路径不抽局部常量。

     ```ts
     // ❌ 禁止：业务 API 局部抽前缀常量再拼路径
     const XXX_URL_PREFIX = '/v2/xxx/yyy'

     export function getXxxPage(data?: Omix) {
         return request({
             url: `${XXX_URL_PREFIX}/page`,
             method: 'POST',
             data
         })
     }

     // ✅ 正确：函数定义处直接看到完整接口地址
     export function getXxxPage(data?: Omix) {
         return request({
             url: '/v2/xxx/yyy/page',
             method: 'POST',
             data
         })
     }
     ```
   - 🔴 **雷区 13：禁止直接把操作按钮放入表格操作列**
     - ❌ 禁止在标准列表页中直接新增 `operateCol`、`#col_operate`、`prop: 'operate'`，把“编辑 / 删除 / 详情”等操作默认放在表格最右侧操作列。
     - ❌ 原型图或截图里出现操作列，也不能直接照搬为行内操作；Kunlun 页面生成必须先服从 `src/components/dev-template/list-a.vue` 的 header 操作模式。
     - ✅ **正解：** “编辑 / 删除 / 详情”等单行操作默认放在表格 header 左侧，通过 `show-select` 选中一条数据后操作。
     - ✅ 新增、导出、批量操作、生成、同步等页面级操作也默认放在 header 左侧。
     - ✅ 只有用户明确说“必须每行内联操作 / 保留表格操作列 / 每行展示编辑删除”，或业务确实无法通过选中行操作表达时，才允许使用操作列；使用前必须说明原因。
     - ✅ 如果需求明确允许使用操作列，`columns` 末尾只写 `{ operateCol: true }`；`label`、`prop`、`fixed`、`disabledAuth` 等默认属性由 `sky-table-pagination` 统一补齐，除非需求明确要求覆盖。
     - ✅ 行内操作插槽使用 `#col_operate`；未启用操作列时不要保留 `operateCol` 或 `#col_operate`。
     - ✅ `src/components/dev-template/list-a.vue` / `list-b.vue` 中的操作列仅作为可选示例，页面生成默认仍按 header 左侧操作按钮模式克隆。
     - ✅ 如果使用操作列，优先按项目已有封装方式处理，例如 `com-table-operate`，不要随手堆多个裸 `el-button`。
     - 🔴 **`com-table-operate` 的 `row-id` 是必传值**：每次使用都必须显式传入，即使当前操作暂时不需要 loading，也不允许省略。
     - ✅ 默认取业务主键：`:row-id="row.id"`；“默认取 id”不代表可以不写该属性。
     - ✅ 当前接口没有 `id`，或 `id` 不能唯一标识行时，必须根据接口文档、抓包、后端或用户确认，传入其他稳定唯一字段、前端组合 `_rowKey`，或取值函数。
     - ✅ `row-id` 最终必须得到有效的字符串或数字；禁止使用数组下标、分页内序号或未经确认唯一性的展示文案。
     - ❌ Vue 的 `:key`、表格的 `primary-key` 不能代替 `com-table-operate` 的 `row-id`，组件仍须显式传入。

     ```vue
     <!-- 常规场景：默认取业务主键 id，但仍必须显式传入 -->
     <com-table-operate :row-id="row.id" :row :data="operateList" />

     <!-- 非 id 场景：传入已经确认的稳定唯一值 -->
     <com-table-operate :row-id="row._rowKey" :row :data="operateList" />
     ```
   - 🔴 **雷区 13 补充：表头操作按钮顺序混乱**
     - ❌ 禁止把 `添加` 放在 `编辑 / 删除` 后面，导致列表页常规维护入口顺序不一致。
     - ❌ 禁止按编码时想到什么就写什么的顺序排列按钮。
     - ✅ **正解：** 标准列表页表头操作区中，若同时存在 `添加 / 编辑 / 删除`，必须固定按 `添加 → 编辑 → 删除` 排列。
     - ✅ `添加` 是新增入口，默认放在最前；`编辑 / 删除` 是选中行维护操作，紧跟其后。
     - ✅ `详情 / 复制 / 导出 / 批量操作 / 生成任务 / 同步` 等其他按钮放在 `添加 / 编辑 / 删除` 后面，再按业务主次排序。
     - ✅ `src/components/dev-template/list-a.vue` / `list-b.vue` 的示例也必须保持这个顺序，页面生成时直接照模板克隆。
   - 🔴 **雷区 13 补充：删除操作模式擅自定单删或批删**
     - ❌ 接口文档未明确时，禁止默认把“删除”写成单删，也禁止默认写成批量删除。
     - ✅ **正解：** 删除模式必须以接口文档或后端说明为准；单删使用 `hasSingleSelected` + `firstSelected`，批量删除使用 `hasSelected` + `selectedTable`。
     - ✅ 接口未提供时，应先询问用户或使用 `TODO待联调_删除是否支持批量` / `TODO待联调_评估项ID列表` 等待联调标记，不能把猜测字段当成正式字段。
     - ✅ 静态开发阶段若用户确认先按批量删除占位，按钮禁用态使用 `!hasSelected`；若确认按单删占位，按钮禁用态使用 `!hasSingleSelected`。
     - ✅ 删除禁用原因需要按选中范围判断：批量删除时任一选中项命中“系统预置 / 被引用 / 有历史数据”等业务限制，都应禁用或拦截删除。
   - 🔴 **雷区 13 补充：无操作按钮时擅自添加页面标题**
     - ❌ 在 `list-a.vue` 类型页面中，如果表格头部没有操作按钮、导出、批量操作等实际功能，禁止为了显示标题而额外添加：
       `<template #header><com-header-between table><com-page-title /></com-header-between></template>`
     - ✅ **正解：** `list-a.vue` 的 `#header` 只用于承载表格左上角操作按钮、导出等功能节点；没有操作节点时不要声明 `#header` 插槽。
     - ✅ `com-page-title` 仅在模板本身存在对应结构或需求明确要求时使用，禁止从 `list-b.vue` 等其他模板迁移到 `list-a.vue`。
   - 🔴 **雷区 14：Tab 子页面使用了错误的容器组件**
     - ❌ 在开发 Tab 内嵌的子页面时（如 `tabs/tab-xxx.vue`），习惯性地复制了独立页面的 `<com-page-scroll-wrapper>` 和 `<com-page-wrapper-item>`，导致 Tab 切换时高度计算错误或滚动条异常。
     - ✅ **正解：** **但凡是挂载在 Tab 下的子页面**，必须且只能使用 `<com-page-tab-item-wrapper>` 作为根容器！同时必须通过 `<template #="{ hFullClass }">` 解构出高度类名，并绑定给内部的 `<sky-table-pagination :class="hFullClass">`，让表格自动撑满剩余高度。严格参照 `src/components/dev-template/tab-template/tabs/tab-list-a.vue`。
   - 🔴 **雷区 15：画蛇添足的 showOverflowTooltip**
     - ❌ 在 `useTable` 的 `columns` 配置中，手动为普通文本列写上 `showOverflowTooltip: true`。
     - ✅ **正解：** `sky-table-pagination` 底层默认已为所有列开启了超出截断与 Tooltip 提示功能，**无需且不应显式声明**该属性，除非确需设为 `false` 来关闭提示或允许换行。
   - 🔴 **雷区 15 补充：纯文本展示未考虑长文本**
     - ❌ 在卡片、详情、弹窗只读区、表格自定义列插槽、下拉 option、业务列表项等位置，直接写 `{{ xxx }}`、`<span>{{ xxx }}</span>` 或普通 `div + 文本`，没有考虑接口返回文本过长导致挤压、换行撑高、遮挡按钮或破坏布局。
     - ❌ 为了省事只写 CSS `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;`，导致用户看不到完整内容，也没有统一 Tooltip 体验。
     - ✅ **正解：** 纯文本展示只要存在长度不确定的接口字段、用户输入内容、名称、编码、备注、说明、国家地区、客户 / 供应商名称等，都必须优先使用 `sky-ellipsis-tooltip` 承载。
     - ✅ 单行展示默认使用 `sky-ellipsis-tooltip`；需求明确允许多行摘要时，使用 `:line-clamp="行数"`，不要让文本无限换行撑开布局。
     - ✅ `content-class` 用于承接当前业务文本样式；如果需要限制浮层宽度，再通过 `tooltip-class` 设置，例如 `max-w-240`。禁止为了省事给每个文本手写一套局部 tooltip。
     - ✅ 普通 `sky-table-pagination` 文本列已内置超出截断与 Tooltip，不需要额外包一层；但如果使用 `#col_xxx` 自定义列插槽后自行拼纯文本，仍要按本规则使用 `sky-ellipsis-tooltip`。
     - ✅ 静态短文案、固定按钮文案、固定 label、已由 `el-text truncated` / 表格内置 tooltip / 业务组件内部明确处理过省略的场景，不需要重复包裹。

     ```vue
     <!-- ❌ 禁止：接口文本长度不确定，却直接裸展示 -->
     <span class="xxx-card__name">{{ row.TODO业务字段 }}</span>

     <!-- ✅ 正确：纯文本展示优先使用 sky-ellipsis-tooltip -->
     <sky-ellipsis-tooltip content-class="xxx-card__name" tooltip-class="max-w-240">
         {{ formatEmptyValue(row.TODO业务字段) }}
     </sky-ellipsis-tooltip>

     <!-- ✅ 正确：多行摘要使用 line-clamp 控制高度 -->
     <sky-ellipsis-tooltip :line-clamp="2" content-class="xxx-card__desc" tooltip-class="max-w-360">
         {{ formatEmptyValue(row.TODO业务说明) }}
     </sky-ellipsis-tooltip>
     ```
   - 🔴 **雷区 15 补充：空值判断与统一文本占位重复实现**
     - ❌ 禁止在 Kunlun 业务页面重复声明 `formatText`、`formatEmptyText` 等局部空值占位函数。
     - ❌ 禁止使用 `value || '-'` 处理展示空值；数字 `0`、布尔值 `false` 都可能是有效业务值。
     - ❌ 新增或修改空值判断时，禁止优先使用 `isEmpty / isNotEmpty`，或手写 `null / undefined / 空字符串` 判断。
     - ✅ **项目约定：** 从 `@/utils/utils-common` 导入 `formatEmptyValue`、`isBlank`、`isNotBlank`。
     - ✅ 文本、表格自定义单元格、详情只读字段等纯展示内容需要空值占位时，统一使用 `formatEmptyValue(value)`。
     - ✅ `formatEmptyValue` 将 `''`、`null`、`undefined` 显示为 `-`，数字 `0` 和布尔值 `false` 保持原值。
     - ✅ 业务逻辑需要判断空值时，`isBlank / isNotBlank` 的使用优先级高于 `isEmpty / isNotEmpty`；前者遵循 Kunlun 项目统一空值语义，并提供 TypeScript 类型收窄。
     - ✅ 判断“为空”使用 `isBlank(value)`；判断“有值”使用 `isNotBlank(value)`，禁止通过 `!isBlank(value)` 表达有值。
     - ✅ `formatEmptyValue` 只负责纯文本展示，不用于表单初始化、查询参数、提交数据或业务分支判断。
     - ✅ `sky-table-pagination` 普通文本列已有统一空值展示时，不重复增加格式化；只有 `formatterRender`、自定义列插槽、原生静态表格或其他纯文本展示由业务自行渲染时，才调用 `formatEmptyValue`。

     ```ts
     import { formatEmptyValue, isBlank, isNotBlank } from '@/utils/utils-common'

     const displayValue = formatEmptyValue(value)

     if (isBlank(value)) return

     if (isNotBlank(value)) {
         useValue(value)
     }
     ```
   - 🔴 **雷区 15 补充：表格列渲染优先级与插槽入口**
     - ❌ 需要简单自定义单元格展示时，默认编写 `<template #col_xxx>`，导致模板堆积大量零散列插槽。
     - ❌ 使用 `<template #col_xxx>` 自定义列时，又在对应 `columns` 配置里追加 `slot: true`。
     - ❌ 未查看 `sky-table-pagination` 源码，只凭 Element Plus 或其他项目经验猜测列渲染与插槽写法。
     - ✅ **正解：** `sky-table-pagination` 需要自定义单元格渲染时，优先在 `columns` 中使用 `formatterRender`。
     - ✅ 字符串拼接、枚举标签、简单空值展示，以及返回单个已有业务组件并传入少量 Props 的场景，均直接使用 `formatterRender`。
     - ✅ 已有单元格组件可以直接由 `formatterRender` 返回；禁止仅为了调用该组件再声明一层列插槽。
     - ✅ 只有渲染结构包含多个业务区块、较多条件分支或循环、复杂交互、嵌套插槽等内容，导致 `formatterRender` 明显拉长列配置、降低可读性和维护性时，才使用 `#col_${prop}` 列插槽。
     - ✅ 判断依据是维护复杂度，不机械规定代码行数；简单 JSX 即使需要换行书写，仍优先保留在 `formatterRender`。
     - ✅ `sky-table-pagination` 会优先识别 `#col_${prop}` 插槽；使用这种插槽时，`columns` 中只需要配置同名 `prop`，不得追加 `slot: true`。
     - ✅ 只有确实要使用 `item.slot` 分支对应的原始 `prop` 命名插槽时，才允许配置 `slot: true`，并且必须先确认组件源码和模板示例。
     - ✅ 页面生成时必须参考 `src/components/dev-template/list-a.vue` / `list-b.vue`，并按本节优先级选择 `formatterRender` 或复杂列插槽，禁止混用两套入口。
   - 🔴 **雷区 16：时间字段列宽分配不合理**
     - ❌ 针对时间类字段没有设定宽度，导致在不同屏幕尺寸下可能出现折行或挤压，影响阅读体验。
     - ✅ **正解：** 只要是包含完整日期时间的字段（例如展示格式为 `YYYY-MM-DD HH:mm:ss`），在 `columns` 配置中**必须为其显式设置 `minWidth: 160`**，确保时间信息始终保持单行完整展示。
   - 🔴 **雷区 17：页面逻辑忽略全局枚举分支与过程注释规范**
     - ❌ 在页面生成时，只判断一个枚举值，然后把剩余情况默认当作另一个业务类型处理；或只写函数名注释，关键 `if`、接口选择、兜底返回没有过程注释。
     - ✅ **正解：** 页面生成同样必须遵循全局规则中的“枚举条件分支判断规范”和“注释位置与内容分层规范”。已知枚举值必须逐个显式判断；关键分支、接口选择、兜底返回必须在代码附近说明业务原因。
