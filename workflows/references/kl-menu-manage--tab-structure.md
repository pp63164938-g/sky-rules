# Kunlun 菜单：Tab 结构

触发：页面是 `sky-tab` 多 Tab，或用户要求按 Tab 拆菜单 / 权限 / 字段。

本文件只约束菜单资源与权限结构。Tab 页面的 UI 骨架、滚动容器、页签标题见 `kl.gen-page` 的详情与导航引用，禁止在此重复。

## 不变量

- Tab 是父级页面下的 **子菜单**（`resourceType "0"`），不是按钮（`"1"`）。
- 父级保留唯一 Vue 路由；Tab **不单独注册 Vue 路由**。
- Tab 在系统菜单里 **隐藏**：`webShowFlag=false`。
- 前端用菜单权限过滤 Tab：`hasAuthorize([tab.sign], 'menu')`。

## 标识与路径

- 父级 `international`：页面级，与父级 `router`、Vue 路由一致。
- Tab：`{父级international}:tab-{语义slug}`，例如 `module:biz:page:tab-xxx`。
- Tab `router` 可填 Tab 路径（供资源记录），**禁止**按该路径加 Vue route。
- Tab 内按钮：`{Tab international}:{后缀}`，父级是 Tab 资源，不是页面父级。
- 无导出入口不编 `:export`。

## 菜单名称与页签文案

两套名字不要混：

| 位置 | 规则 | 例子 |
| --- | --- | --- |
| 资源 `name`（菜单管理列表） | `tab-` + 页签中文标题 | `tab-业务页签` |
| 页面 Tab `label` | 只有中文标题，**不加** `tab-` | `业务页签` |
| `international` | `{父级}:tab-{英文slug}` | `module:biz:page:tab-xxx` |

- 管理列表用 `tab-` 前缀区分隐藏子菜单；权限 key 仍看 `international`，不看中文名。
- 禁止把 Vue `label` 写成 `tab-xxx`。
- 禁止把中文 `tab-` 前缀写进 `international`。

## 前端

- 全量 `allTabsList`，每项含 `sign` = Tab `international`。
- `tabsList = computed(() => allTabsList.filter(tab => hasAuthorize([tab.sign], 'menu')))`。
- 各 Tab 页 `useCustomizeField` 的 url = **该 Tab** 的 `international`。

## 菜单写入

| 资源 | resourceType | webShowFlag | router | 说明 |
| --- | --- | --- | --- | --- |
| 页面父级 | 菜单 `"0"` | 显示 | 页面路由 | 唯一 Vue 路由 |
| Tab | 菜单 `"0"` | 隐藏 | Tab 路径，无 Vue 路由 | 子级，parentId=页面 |
| Tab 内按钮 | 按钮 `"1"` | 按表单 | `""` | parentId=Tab |

预览必须逐行给出上述字段。用户确认前禁止写入。

已有本规范时，禁止再把「Tab 做成按钮还是菜单」「要不要 Vue 路由」「webShowFlag」当疑问。

## 事实来源与失效

- 事实来源：当前工程菜单表单 `sys-dialog-menu.vue` 的 `resourceType` / `webShowFlag`，以及已落地的 Tab 页 `allTabsList` + `hasAuthorize(..., 'menu')`。
- 失效信号：`resourceType` 枚举变化、Tab 改为独立 Vue 路由、前端不再用菜单权限过滤 Tab。
- 变化后先停、更新本引用，禁止在业务代码中静默兼容。
