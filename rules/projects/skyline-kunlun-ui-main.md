# skyline-kunlun-ui-main 项目专用规范

## Element Plus Namespace 规范

**核心原则**：本项目 Element Plus namespace 固定为 `el-sky`。所有运行时 DOM 类名使用 `.el-sky-*`，CSS 变量使用 `--el-sky-*`。

**项目依据**：

- `src/packages/hooks/hook-configer.tsx` 中的 namespace 配置为 `el-sky`。
- `src/styles/element/index.scss` 中的样式 namespace 配置为 `el-sky`。

**硬性红线**：

- 禁止在样式、脚本选择器、测试定位器或其他 DOM 定位代码中使用默认 `.el-*` 运行时类名。
- 禁止使用默认 `--el-*` CSS 变量。
- 禁止同时编写 `.el-sky-*` 与 `.el-*`，不得以“兼容默认 Element Plus”为理由保留本项目不会生成的前缀。
- 本规则适用于所有直接或间接引用 Element Plus 运行时类名、CSS 变量或 DOM 结构的代码与配置，包括但不限于普通样式、`:deep()`、`:global()`、脚本选择器、测试和自动化定位器。
- 后续新增任何样式机制、测试工具或 DOM 定位方式时，只要涉及 Element Plus 运行时标识，均自动受本规则约束，无需逐项补充场景名称。
- Vue 组件标签 `<el-button>`、`<el-select>` 等不属于运行时类名，继续按项目组件注册方式使用。

**正确做法**：

- Element Plus DOM 类名统一使用 `.el-sky-*`。
- Element Plus CSS 变量统一使用 `--el-sky-*`。
- 修改到存量错误前缀时，应在本次涉及范围内直接纠正，禁止继续复制或增加双前缀兼容。
- 交付前对本次修改文件执行默认前缀检查：
  `rg -n --pcre2 '\.el-(?!sky-)|--el-(?!sky-)' <本次修改文件>`
- 检查命中项时只处理运行时类名和 CSS 变量，不把 `<el-button>` 等组件标签误判为问题。

**判断标准**：

- 本次新增或修改的 Element Plus 运行时类名是否全部以 `.el-sky-` 开头。
- 本次新增或修改的 Element Plus CSS 变量是否全部以 `--el-sky-` 开头。
- 是否不存在没有运行时依据的默认前缀或双前缀兼容。
