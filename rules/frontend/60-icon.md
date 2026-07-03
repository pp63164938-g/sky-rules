# Icon 使用规范

**核心原则**：使用 Icon 时，必须参考当前项目已有的 Icon 用法，保持风格统一。

## Icon 来源

项目中使用的 Icon 可能来自以下来源：

1. **项目自定义 Icon**：通过 `@/assets/icons/` 或类似目录引入的自定义图标
2. **组件库 Icon**：如 Element UI 的 `el-icon-xxx`、Ant Design 的 `a-icon` 等
3. **第三方图标库**：如 iconfont、Font Awesome 等

## 使用前检查

使用 Icon 前，应先检查：

1. **查看项目现有 Icon 用法**：搜索项目中类似功能的 Icon 是如何引入和使用的
2. **确认图标库版本**：确保使用的图标在当前版本中可用
3. **保持一致性**：同类功能使用相同风格的 Icon

## Icon 使用方式查证门禁

**核心原则**：使用或替换 Icon 前，必须先确认当前项目、当前模块的 Icon 使用风格，禁止拿到 SVG 后直接套用某一种写法。

**执行顺序**：

1. 先查同页面 / 同模块 / 同类功能的 Icon 写法，例如 `<local-xxx />`、`svg-icon`、`<img src="...">`、组件库 Icon。
2. 再查构建或自动导入配置，确认是否存在统一加载机制，例如 `unplugin-icons`、`IconsResolver`、`FileSystemIconLoader`、`svg-sprite-loader`。
3. 根据当前项目事实选择写法：
   - 如果项目当前风格是 `<img src="@/assets/icons/xxx.svg">`，允许继续使用 `<img>`。
   - 如果项目当前风格是 `el-icon + local-*`，应按该方式新增 / 替换。
   - 如果项目当前风格是 `svg-icon` / Sprite，应按项目约定使用 `svg-icon`。
4. 最终回复中说明本次 Icon 写法依据，例如“同模块已有 `el-icon + local-*`，且配置了 `FileSystemIconLoader`”。

**禁止行为**：

- 禁止未查项目已有用法，就直接使用 `<img>`、`svg-icon`、`local-*` 或组件库 Icon。
- 禁止只因为用户提供的是 SVG，就默认用 `<img>`。
- 禁止套用其他项目的 Icon 习惯。

## 静态开发临时 Icon 标记

适用场景：静态开发阶段，设计稿中的 Icon 尚未提供或尚未确定时。

**标记规范**：

- 在原有 Icon class 基础上，**附加** `TODOicon_` 标记 class
- 标记不影响 Icon 正常显示，仅用于后续全局搜索定位
- 便于后续全局搜索 `TODOicon_` 进行逐一替换

**代码示例**：

```html
<!-- ❌ 不推荐 - 直接使用临时 icon，后续难以查找 -->
<i class="el-icon-question"></i>

<!-- ✅ 推荐 - 保留原 icon class，附加 TODOicon_ 标记 -->
<i class="el-icon-question TODOicon_待替换"></i>

<!-- ✅ 也可以标注具体替换目标 -->
<i class="el-icon-question TODOicon_替换为设计图标"></i>
```

**使用规则**：

1. 静态开发时，不确定的 Icon 必须附加 `TODOicon_` 标记
2. 标记不影响 Icon 正常显示，开发期间可正常预览
3. 联调或设计确认后，全局搜索 `TODOicon_` 进行替换（同时删除标记 class）
4. 上线前确保所有 `TODOicon_` 标记已清理
