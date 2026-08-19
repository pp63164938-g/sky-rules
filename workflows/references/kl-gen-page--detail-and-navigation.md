# Kunlun 详情与导航实现细则

## 详情页面结构

- `src/components/dev-template/detail.vue` 只提供表单展示、表格展示和固定底部操作三类通用结构，不代表固定的业务模块名称。
- 详情字段优先使用 `sky-form + sky-form-item`；宽屏多列、窄屏自动降列时使用 `common-auto-grid-form`，禁止重复手写响应式网格。
- 详情表格默认使用 `sky-table-pagination`；固定底部操作使用 `com-page-operate-footer`。需求不需要的模板模块直接删除，禁止保留模板 TODO 标题或虚构业务区块。
- 详情内容和模块标题由详情页依据目标详情接口生成；列表页只传查询所需的稳定标识，不承担详情内容组装。
- 复杂详情业务块确实影响主文件阅读时，才拆到当前详情页 `components/`；普通表单和普通表格不为减少行数拆分。

## Tab 页面

- Tab 主页面读取 `src/components/dev-template/tab-template/index.vue`，Tab 内嵌列表同时读取对应子模板。
- Tab 子页面根容器使用当前模板的 `com-page-tab-item-wrapper`，通过插槽取得高度类并绑定给内部表格；禁止复制独立页面的滚动容器导致高度和滚动条异常。
- Tab 内嵌组件不单独生成工作台页签标题；只有独立路由详情、编辑等子页面处理动态页签。

## 路由与参数

- 新建页面后搜索并更新当前业务模块的真实路由配置，使用已确认的 `name`、`path` 和 `component`；禁止根据目录猜测路由名或模块文件。
- 详情跳转只传查询必需标识，并使用当前项目 `@/utils/utils-common` 中的 `encodeRouteQuery`；详情页通过对应的 `decodeRouteQuery` 读取。
- 默认只解密一次。只有同一组件实例确实会切换 query 时，才使用 `useRoute + watch` 重新加载；禁止为了响应式默认包装 `computed(() => decodeRouteQuery())`。
- 标识字段保持接口原值，不对 `int64` / `Long` 或主键语义字段执行 `Number()`、`parseInt()` 或一元 `+` 转换。

## 跨页带入与动态页签

- 复杂临时数据需要跨页传递时，先读取 `emitBringData` / `receiveBringData` 的当前源码和项目用法，确认其存储、读取和清理语义后再使用。
- 接收页可能被 keep-alive 缓存或重复激活时，同时处理首次进入与 `onActivated`；使用已确认的来源标识限制消费范围，避免其他页面模式误用缓存。
- 禁止为了详情展示或动态标题，把完整列表行、列表快照或额外名称塞入 route query / bringData。
- 独立路由子页面需要动态页签标题时，由子页面在目标详情接口成功返回后，使用当前接口字段调用项目已有的 `fetchUpdateBookmarkTitle`；字段为空时保留路由默认标题。
- 标题格式、字段或来源未确认时先反馈，不使用相似字段、其他接口或静态占位拼出看似完整的标题。
