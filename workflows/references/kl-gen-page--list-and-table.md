# Kunlun 列表与表格实现细则

## 模板骨架与数据生态

- 生成 `.vue` 文件时连同模板的文件头注释和 SFC 顺序一起复用；当前模板顺序为文件头注释、`<template>`、`<script>`、`<style>`，交付前按当前模板重新核对。
- 标准列表页的 `columns` 保持在页面 `useTable` 声明中，禁止按旧项目习惯外拆 `data.tsx`、`config.js` 等配置文件。
- `sky-table-pagination` 必须使用 `useTable` 返回的 `fn`，接口通过 `useTable` 的 `fnApi` 接入；禁止自行建立 `tableRef + getTableData + handleParams` 接管分页。
- 弹窗、抽屉或 Tab 子区只要使用 `sky-search-form-a + sky-table-pagination + 接口列表`，同样沿用 `list-a.vue` 的数据生态。
- 搜索 A 直接通过 `tableLoad(searchForm)` 触发表格查询。只有需要同步刷新汇总等旁支数据时，才新增有真实业务职责的方法。
- 搜索项优先使用 `com-form-input`、`com-form-select`、`business-*` 等项目表单组件；没有匹配能力时先说明源码查证结果，再局部使用原生组件。

## 汇总、导出与自定义字段

- 需求包含 `sky-summary` 时，按当前模板的 `#tool` 插槽接入，并通过 `useTable.loadAfter` 使用同一份查询参数刷新汇总；禁止额外使用 `onMounted` 或无依据 `watch` 建立第二条生命周期。
- 导出优先使用 `com-download` 下载中心模式：普通场景传 `api`，导出前需要组装参数时使用 `getInfo`，接口直接返回 URL 时使用 `getUrl`；`getOther` 仅用于已确认的非下载中心场景。
- 标准查询列表按当前 `list-a.vue` / `list-b.vue` 接入 `useCustomizeField`。唯一标识必须来自菜单管理、用户确认或项目真实配置；未确认时使用项目约定的 `TODO:菜单管理页面【唯一标识】` 占位并在交付中说明，禁止按路由或模块名猜测。

## 表头操作与行唯一标识

- 标准列表操作默认放在表格 header 左侧；只有用户明确要求行内操作，或业务无法通过选中行表达时，才使用操作列。
- 同时存在添加、编辑、删除时固定按“添加 → 编辑 → 删除”排列；详情、复制、导出和批量操作排在其后并按业务主次排序。
- 没有实际操作节点时不声明 `#header`，也不为了显示标题从其他模板迁移 `com-page-title`。
- 删除是单条还是批量必须以接口文档或后端确认为准。单删使用模板的单选状态，批量删除使用多选状态；禁止通过字段名或按钮文案推断。
- `primary-key`、`row-key` 和其他行唯一值必须有接口或项目真实代码依据；禁止使用数组下标、列表顺序或未经确认唯一性的展示字段。
- 使用 `com-table-operate` 时必须按组件契约显式传入 `row-id`。默认主键不存在时，先确认稳定唯一值；前端组合 `_rowKey` 只有业务依据明确时才可使用。

## 列渲染与展示边界

- 简单自定义单元格优先在 `columns` 中使用 `formatterRender`；枚举标签、字符串组合、空值展示或返回单个现有组件都属于简单渲染。
- 只有包含多个业务区块、复杂条件、循环或交互的单元格才使用 `#col_${prop}`；该插槽由组件按 `prop` 识别，不额外配置 `slot: true`。
- 普通文本列沿用 `sky-table-pagination` 内置的溢出提示，不重复声明 `showOverflowTooltip: true`，也不额外包裹 Tooltip。
- 完整日期时间列按当前模板和表格表现设置 `minWidth: 160`；如果项目统一时间格式或表格能力发生变化，先以当前源码和实际布局验证结果为准。
- 表格列、搜索项和操作入口完成后沿调用链检查查询、空态、刷新、选择、删除和导出行为，禁止只验证页面静态外观。
