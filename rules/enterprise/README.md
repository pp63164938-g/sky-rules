# 企业规范目录

`rules/enterprise/` 只放企业规范。一家企业一个目录，目录名使用稳定的企业标识，不使用项目名或仓库名。

个人规则仍放在 `rules/common/`、`rules/lang/`、`rules/frontend/`、`rules/backend/`、`rules/projects/`。`rules/backend/` 表示个人后端规则，不代表任何企业。

## 当前企业

| 企业 | 目录 | 当前内容 |
| --- | --- | --- |
| sky | `enterprise/sky/` | 后端规范、Java 语言规范 |

sky 的维护入口、优先级和原始文档登记见 `enterprise/sky/README.md`。

## 新增企业

1. 在本目录下新增 `<企业标识>/`，并创建该企业自己的 `README.md`。
2. README 必须写明企业标识、适用项目或任务、原始文档入口、当前已收录范围和冲突优先级。
3. 按主题放入 `backend/`、`frontend/`、`lang/` 等子目录。禁止把多家企业的规则继续堆进个人规则目录。
4. 在 `rules/rules-manifest.json` 登记实际要拼接的文件，并同步 `rules/README.md` 索引。
5. 更新 `scripts/check-rules.py` 的企业目录清单。只新增企业但没有规则文件时，不得让自检要求该企业目录下必须有文件。
6. 原始文档不在本仓库时，只在企业 README 登记入口。禁止把摘录后的规则目录写成原始文档目录。

## 冲突优先级

用户最新确认 > 当前任务命中的企业规范 > 个人规则。

同一任务命中多家企业，且规则口径不同并会影响实现结果时，先向用户确认使用哪一家。不得把后加入的企业规范默默覆盖已命中的企业规范。
