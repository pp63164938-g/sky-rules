# Kunlun 菜单：字段权限

触发：`useCustomizeField` / `useField`、角色列、或配置 `interfaceList`。

## 默认映射（无需再问）

| 菜单字段 | 页面含义 | fieldType |
| --- | --- | --- |
| 入参 | 搜索条件（`searchForm` / `sky-search-form-item` 的 `prop`） | `"0"` |
| 出参 | 列表列（`useTable` columns 的 `prop`，不含操作列） | `"1"` |

`webFieldName` = 页面 label；`serviceFieldName` = `prop`。禁止用其它接口、其它 Tab、字典或相似页补字段。

## 绑定位置

- `useCustomizeField(url, tableLoad, apiUrl)` 的 `url` = 资源 `international`。
- `apiUrl` = `{path}:{METHOD}`，对应 `useField` 的 `current`；查找键是该 international 下 `item.key === current`。
- 列表接口绑在 **url 对应的那条资源** 上。Tab 页绑 Tab，禁止绑在父级却让 Vue 读 Tab。
- 空 `apiUrl` 表示不用字段权限，不要凭空绑。

## interfaceList 契约

以当前工程菜单表单为准（`sys-dialog-menu.vue` / `sys-dialog-field.vue`）：

- 接口：`requestType` GET=`"0"` POST=`"1"` PUT=`"2"` DELETE=`"3"`；列表 POST 用 `"1"`。
- 接口 `resourceType` 固定 `"2"`。
- `path` 与 `apiUrl` 的 path 一致，不含 `:{METHOD}`。
- 字段：`fieldType`、`webFieldName`、`serviceFieldName`、`defaultShowFlag`、`defaultUpdateFlag`、`defaultEncryptionFlag`、`defaultEncryptionType`、`sort`。
- 新增字段不带历史 `id`；更新已有接口/字段才带 `id`。
- `interfaceList` 必须随更新 payload 提交，禁止 `null`；清空字段权限用 `[]`。

## Tab 上的新绑定

用户确认「按 Tab 新建、不兼容历史」时：

1. 每个 Tab **新建** `interfaceList` + `fieldList`，不复用父级或历史接口/字段 id。
2. Tab 绑完后，父级若不再承担列表字段权限，更新为 `interfaceList: []`。
3. 父级这次若被 update，也要写当前 `devVersion`。
4. 禁止把父级历史字段改挂到 Tab 上冒充迁移完成。

## 范围

- 入参只来自当前 Tab 已确认搜索项；缺契约不编入参。
- 出参只来自当前表格列；`operate` 等操作列默认不进出参。
- 禁止跨 Tab 借用搜索项或列。
- `defaultShowFlag` 等开关以预览表、用户确认为准；禁止为“看起来完整”改开关。

## 预览与写入

写入前必须表格预览：资源 international、接口 path/METHOD、入参列表、出参列表、父级是否清空。用户确认前禁止调用更新接口。

## 事实来源与失效

- 事实来源：`hook-customize-field` / `hook-field` 的 `url` + `{path}:{METHOD}` 查找键；菜单表单与字段弹窗的 `requestType` / `fieldType` 枚举。
- 失效信号：查找键不再是 `{international}+{path}:{METHOD}`、入参/出参不再对应搜索/列表列、`requestType` / `fieldType` 枚举变化。
- 变化后先停、更新本引用，禁止在业务代码中静默兼容。
