# Java 语言规范

> **归属维度**：语言层规则。约束 Java 语言本身的写法，与端无关。
> **生效条件**：当前项目事实语言为 Java 时生效。判定依据：项目存在 `pom.xml` / `build.gradle` / project-catalog.json 登记。
> **来源**：默认以 sky 企业后端文档为准（企业规范）。
> **边界**：语言层规则只收录在本目录；接口契约、持久化、鉴权等端规则在 `rules/backend/`，禁止混淆。

## 防混淆条款

- 禁止默认「后端 = Java」：后端项目语言以项目事实为准（`pom.xml`/`build.gradle` → Java；`package.json` → JS/TS 走 `lang/js-ts.md`）。
- 禁止把 `lang/js-ts.md` 的 JS/TS 细则（JSDoc 格式、`===`、枚举 Options 等）套用到 Java 代码。
- 禁止把本文件的 Java 口径套用到前端或 Node 后端代码。

## 注释规范

> 待补充：以 sky 企业后端文档的注释规定为准。企业文档原文到位前，本章节不沉淀任何个人推断口径；Java 代码注释按项目已有代码风格处理，并在交付中说明依据。
