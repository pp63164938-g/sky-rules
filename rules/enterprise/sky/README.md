# sky 企业规范

本目录收录 sky 企业规范的规则摘录。它不是 sky 原始规范文档目录；原始文档未进入本仓库时，只能按本文件登记的入口回溯。

## 适用与优先级

- 企业标识：`sky`。
- 适用任务：sky 后端开发、sky Java 项目、sky 多版本本地联调。
- 冲突优先级：用户最新确认 > 本目录企业规范 > `rules/` 下的个人规则。
- 原始文档入口：未登记。当前规则摘录来自 sky 企业后端文档和 sky 多版本部署演示；拿到稳定的本地目录、仓库或文档地址后，补到这里，不把本目录改称原始文档目录。

## 已收录

| 路径 | 内容 |
| --- | --- |
| `backend/10-service-api-contract.md` | 接口契约与服务分层 |
| `backend/20-data-persistence.md` | 数据持久化与事务 |
| `backend/30-auth-permission-security.md` | 鉴权、权限与安全边界 |
| `backend/40-jobs-cache-observability.md` | 任务、缓存与可观测性 |
| `backend/50-multi-version-local-debug.md` | 多版本开发部署与本地联调 |
| `lang/java.md` | Java 语言规范。原文未到位的部分仍是待核对骨架 |

## 维护方式

1. 新增 sky 规范时，先判断是后端、前端、语言层还是其他主题，放到本目录对应子目录。
2. Java 规范默认归本目录的 `lang/java.md`，不要再放回 `rules/lang/`。
3. 多版本、发布、运行时隔离等 sky 专属内容归本目录，不要写入个人 `rules/backend/`。
4. 新增或移动文件后，同步更新 `rules/rules-manifest.json`、`rules/README.md` 和 `scripts/check-rules.py` 的 sky 文件清单。
5. 原始文档与本目录摘录冲突时，先报告冲突，不以摘录覆盖原始文档。
