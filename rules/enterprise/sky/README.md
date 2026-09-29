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
| `lang/java.md` | Java 语言规范。只收录企业文档原文；原文未到位的部分仍是待核对骨架 |
| `practice/java.md` | 开发 sky Java 项目时总结的写法。不是企业原文，不覆盖 `lang/java.md` |

## 维护方式

1. 新增 sky 规范时，先判断来源，再判断主题。
2. 企业文档原文进对应主题文件。Java 原文只进 `lang/java.md`。
3. 开发 sky 项目时总结、企业文档没写的写法，进 `practice/` 同主题文件。Java 实践进 `practice/java.md`。
4. 不限定 sky、其他企业也能用的个人写法，进 `rules/lang/`、`rules/backend/` 或 `rules/frontend/`。禁止借企业原文文件暂存。
5. 多版本、发布、运行时隔离等 sky 专属内容归本目录，不要写入个人 `rules/backend/`。
6. 新增或移动文件后，同步更新 `rules/rules-manifest.json` 和 `rules/README.md`。`scripts/check-rules.py` 没有写死 sky 文件清单时，不必只为新增 practice 文件改脚本。
7. 原始文档与本目录摘录冲突时，先报告冲突，不以摘录覆盖原始文档。实践总结与企业原文冲突时同样不覆盖原文。
