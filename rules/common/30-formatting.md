# Codex 代码格式化规范

**核心原则**：Codex 修改代码后，必须按当前项目已有的格式化 / lint 工具处理本次修改文件；项目存在 `.vscode` 保存格式化配置时，必须把它作为格式化意图来源并尝试映射到可执行 CLI，禁止直接跳过。

**背景说明**：Codex 直接修改文件不会触发 VS Code 的保存动作，所以不能把 `editor.formatOnSave` 当成“已经格式化”。但 `.vscode/settings.json` 代表项目或团队的格式化约定，必须用于反推应执行的格式化工具；只有无法在当前项目中找到可调用脚本、依赖或 CLI 时，才说明无法由 Codex 稳定触发。

**执行规则**：

1. **先检查项目格式化入口**：先查看 `package.json` 中是否存在 `lint:fix`、`format`、`prettier`、`eslint`、`biome`、`stylelint` 等脚本或配置。
2. **同步检查 VS Code 配置**：如果存在 `.vscode/settings.json`，必须查看 `editor.formatOnSave`、`editor.defaultFormatter`、`editor.codeActionsOnSave`、语言级 formatter 配置，确认是否开启保存格式化或保存修复。
3. **按 VS Code 配置映射 CLI**：当 `.vscode` 开启保存格式化时，应根据 `defaultFormatter` 或 `codeActionsOnSave` 判断对应工具，并优先使用项目脚本、项目依赖或 `node_modules/.bin` 中已存在的 CLI 对本次修改文件执行等价格式化。
4. **只处理本次修改文件**：除非用户明确要求，禁止全项目无差别格式化，避免产生大量无关 diff。
5. **禁止自行引入工具**：项目没有明确使用 ESLint / Prettier / Biome / Stylelint 时，禁止为了格式化自行新增依赖或配置，必须先询问用户。
6. **禁止把 VS Code 配置当成已执行结果**：`.vscode/settings.json` 只能作为格式化工具和保存动作的线索；不能因为项目配置了 `editor.formatOnSave` 就跳过格式化命令。
7. **只有编辑器插件能力时必须说明**：如果项目只有 `.vscode` 自动格式化配置，但没有项目脚本、项目依赖或可调用 CLI，必须说明当前无法由 Codex 稳定触发格式化，并建议补充项目级 `format` / `lint:fix` 脚本。
8. **无法执行时必须说明**：如果项目缺少格式化命令、依赖未安装、命令执行失败，必须在回复中明确说明原因和未格式化的范围。
9. **格式化结论必须四项完整**：最终回复中只要提到“已格式化 / 未格式化 / 无格式化命令”，必须同时说明：
   - 项目脚本检查结果：`package.json` 是否存在 `format` / `lint:fix` 等入口；
   - 本地 CLI 检查结果：`node_modules/.bin` 中是否存在 Prettier / ESLint / Biome / Stylelint 等可执行文件；
   - VS Code 配置检查结果：是否存在 `.vscode/settings.json`，是否开启 `editor.formatOnSave`，以及 `editor.defaultFormatter` / `codeActionsOnSave` 指向什么工具；
   - 执行或未执行结论：实际执行了哪个命令；若未执行，说明是因为缺少项目脚本、缺少本地 CLI，还是只有编辑器插件能力无法由 Codex 稳定触发。
10. **Vite 项目不默认 build**：格式化验证优先使用轻量命令，不得把 `npm run build`、`pnpm build`、`vite build` 当作默认格式化或验证步骤。

**判断标准**：

- 修改代码后，必须主动检查项目已有格式化方式和 `.vscode` 保存格式化配置。
- `.vscode` 开启保存格式化时，必须尝试映射到项目内可执行格式化命令；能执行就执行，不能执行才说明限制。
- 有明确格式化工具时，必须对本次修改文件执行对应格式化。
- 只有 `.vscode` 自动格式化配置时，不能视为已格式化完成。
- 没有明确工具或无法从 `.vscode` 映射到 CLI 时，必须暂停确认或说明限制，不能按个人习惯生成新格式化配置。
- 最终回复中的格式化说明必须包含项目脚本、本地 CLI、VS Code 配置、执行结论四项；缺少任一项时，不能下“无需格式化 / 无格式化命令”的结论。
- 如果未检查 `.vscode/settings.json`，只能说“项目级 CLI 暂未发现”，不能说“项目没有格式化配置”。
- 最终回复必须说明是否已执行格式化，以及使用了哪个命令；未执行时说明原因。
