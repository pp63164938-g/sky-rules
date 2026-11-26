# kl-run-java：启动异常排障引用

仅在 `kl-run-java` 编译失败、启动后进程退出、健康检查未通过，或实测生效环境 / 数据源与请求目标不一致时按需读取。每次只根据首个失败层级的准确报错做最小修改，禁止盲目轮换账号、端口或多个配置项。

## 1. 编译与依赖层

| 现象信号 | 根因辨析与处理动作 |
| --- | --- |
| 内部 `SNAPSHOT` 包找不到类、方法签名不匹配或编译报错 | 当前分支依赖了新内部 API，但 `pom.xml` 版本滞后或本机缓存旧快照。先看同系列依赖在公司仓库和本机 `.m2` 有没有匹配当前分支的新版本；先用 `mvn compile` 验证，不要先改业务代码去迁就旧包。缺包在公司仓库与本机都不存在时停下交给用户。 |
| `CreateProcess error=206, 文件名或扩展名太长` | Windows 命令行长度超限。不要拼超长命令行；按主工作流生成 `$env:TEMP\kl-run-java-<artifactId>.argfile`，用 `-cp "@$env:TEMP\kl-run-java-<artifactId>.argfile"` 加载。 |

## 2. 配置中心与跨集群环境层

| 现象信号 | 根因辨析与处理动作 |
| --- | --- |
| Nacos 报 `403 unknown user!` 或 `auth failed` | 先用 `Resolve-DnsName` 核对 `NACOS_HOST`（尤其是 `*.svc.cluster.local`）在本机实际落向哪个集群。不同集群的容器部署清单常复用同名 K8s 内网域名，本机 DNS 往往固定指向默认开发集群，拿另一集群的 Nacos 密码去登默认集群必报 `403`。确认落错集群时禁止继续试密码，改走目标环境可达地址或 HTTP 配置拉取落地加载。 |
| Nacos 2.x 客户端连外部域名报 `Server check fail` / `9848` 超时 | Nacos 2.x SDK 除 HTTP 端口外还需直连 `端口 + 1000` 的 gRPC 端口（如 `8848 -> 9848`），而外部七层网关通常只暴露 HTTP `80`。先测目标集群 Pod / Service 网段是否直连可达（可达则直接用目标 Nacos 内网 IP + `8848`）；若仅 HTTP `80` 可达，则通过 HTTP 接口拉取公共配置与应用配置到 `$env:TEMP`，搭配 `-Dspring.cloud.nacos.config.enabled=false`、`-Dspring.cloud.nacos.discovery.enabled=false` 与 `-Dspring.config.additional-location=file:<公共配置正斜杠路径>,file:<应用配置正斜杠路径>` 启动。 |
| 进程健康检查 `UP`，但 `/actuator/env` 显示 `spring.profiles.active` 被覆盖回其他环境，或主数据源仍连旧集群库 | 所连 Nacos 中缺少目标 `<app>-<profile>.yml`，回退加载了默认 `<app>.yml`，或数据源 URL 在远端配置中写死了内网主机而未引用命令行传入的 `-D<DB>_ADDRESS` 占位符。必须拉取目标环境真实配置或显式覆盖 `spring.datasource.dynamic.datasource.<名称>.url/username/password`（单数据源为 `spring.datasource.*`），直至 `/actuator/env` 实测连接主机与目标一致。 |

## 3. 数据源与外部组件层

| 现象信号 | 根因辨析与处理动作 |
| --- | --- |
| MySQL 报 `Access denied for user '...'@'...' (using password: NO)` | 注意末尾是 `NO`：说明密码占位符未解析为空，或未传对应密码属性（而非密码错）。核对配置中心实际引用的属性名并补齐键值，或检查该子数据源是否为非主链路库。 |
| MySQL 报 `Access denied for user '...'@'...' (using password: YES)` | 末尾是 `YES`：说明已传非空密码，但用户名、密码与当前实际连接的目标 MySQL 实例不匹配（常见于拿 A 环境账密连到了 B 环境实例，或 `.props` 中存在同名重复键被后置旧值覆盖）。先核对实际连接的实例主机名与 `.props` 唯一键值；账密缺失时停下向用户索取。 |
| 启动卡在某个数据源初始化数分钟无响应，随后才抛连接超时 | JDBC URL 含 `autoReconnect=true&maxReconnects=100`，遇到本机不通的内网节点（如集群内 Doris FE 端口）会循环重连百次导致假卡死。先检查配置注释是否有集群外端口替换说明；若该数据源属于旁路模块，先搜 `@DS("<名称>")` 确认未命中当前验证主链路后，加 `-Dspring.datasource.dynamic.datasource.<名称>.lazy=true` 跳过启动期建池，并在回执中披露受影响功能。 |
| 离线加载配置启动带 Dubbo 3.x 的服务时报 `IllegalStateException: No such any registry to reference ...` | 关闭 Spring Cloud Nacos 后，不要把 `dubbo.registry.address` 改为空、`N/A` 或 `multicast://...`，也不要设 `dubbo.registry.subscribe=false`，否则 Dubbo 3.x 判定无可用订阅注册中心会直接阻断启动。保留项目原有可达注册中心配置，仅加 `-Ddubbo.registry.register=false`（防止本机注册成 Provider 劫持公共环境流量）和 `-Ddubbo.consumer.check=false`（防止缺提供者阻断启动），并在回执「忽略 / 懒加载项」说明。 |
| 调度中心（如 `xxl-job`）或旁路监控在本地报注册失败 / 连接拒绝，或连共享环境（如 `test`）需防抢占任务 | 不要改业务代码；切到 `test` 等共享环境时即使不报错也应主动关闭本地执行器注册，防止本机抢占集群定时任务。先查项目 `XxlJobConfig` 的 `@ConditionalOnProperty` 确认真实开关（如昆仑系常用 `-Ddeploy.type=replica`，直接传 `-Dxxl.job.enabled=false` 可能无效）；确认非阻塞或已关闭后在回执「忽略 / 懒加载项」说明。 |

## 4. JVM、端口、编码与终端交互层

| 现象信号 | 根因辨析与处理动作 |
| --- | --- |
| `Web server failed to start. Port <端口> was already in use` 或 JDWP `transport error 202: bind failed` | 先查占用进程的命令行：若是本服务旧进程，用启动指令开头的「按启动类全名停止旧进程」清理重跑；若是其他服务或 IDE 进程，严禁强杀，顺延空闲 HTTP 端口或调试端口（同步更新 `.vscode/launch.json`）并在回执说明原端口被谁占用。 |
| `InaccessibleObjectException: Unable to make protected final java.lang.Class java.lang.ClassLoader.defineClass(...)`（常见于 Dubbo / Javassist / CGLIB） | JDK 9+ 模块封装拦截反射。不要升级依赖绕过；从项目 `document/k8s/*-values*.yaml` 的 `DYNAMIC_JAVA_OPTS` 提取全部 `--add-opens=...` 补入启动命令并固化保留。 |
| 本地直连报登录用户为空，或浏览器 CORS 预检失败 | 绕过了网关注入的用户头和跨域头。确认已生成 `LocalDevRun.java` 且启动参数包含 `-Dlocal.run=true`。 |
| 本地直连接口报集合字段 `NullPointerException`（如部门 / 角色 / 权限列表调用 `.stream()` 提示 `is null`） | `LocalDevRun.java` 构造的登录上下文对象遗漏了部分集合字段初始化（默认为 `null`）。核对当前项目用户与权限类的全部集合字段，统一初始化为空集合（如 `Collections.emptyList()`）；需按指定部门或角色验证时再按需填入测试对象，不要为迁就本地空指针去改业务代码。 |
| 经本机代理转发报 `400 MissingServletRequestParameterException`，或离线模式调跨服务 Feign 报 `UnknownHostException` | ① 先直连 `127.0.0.1:<端口>` 核对接口本身是否正常；直连正常而经代理报缺参，说明代理规则丢弃了 Query 参数（如 Whistle `^` 通配写法中 `**` 只匹配路径不含 `?query`，应改为 `***` 或改用路径前缀转发）。② 离线关闭服务发现（`-Dspring.cloud.nacos.discovery.enabled=false`）时，依赖 Feign 调其他微服务的接口无法解析服务名属预期限制；代理只转发当前联调模块的接口前缀到本机，其余公共接口保留走环境网关。 |
| 控制台中文乱码，英文正常 | Windows 终端代码页与 UTF-8 输出不一致。启动前带 `chcp 65001` 与三个 `encoding=UTF-8` 参数；核对日志直接用 UTF-8 读取 `logback*.xml` 指向的日志文件。 |
| IDE 控制台里多行日志叠在同一行、后输出的内容覆盖前面的，或中文显示成另一个字（如「准」显示成「準」）；同一时间的日志文件内容正常 | 日志格式用了 Spring Boot 默认的 `%clr(...)` 彩色输出，每行带 ANSI 转义序列。IDE 控制台不认这些序列，把其中的控制字符当成移动光标或回车执行，导致覆盖打印；编码参数只管字符解码，管不了换行符。不要改 `logback*.xml` 的 pattern 或 encoder（会影响容器内日志）。在 IDE 运行配置的 VM options 加 `-Dspring.output.ansi.enabled=never`，让 `%clr` 原样输出文字；中文错字同时补三个 `encoding=UTF-8` 参数。日志文件 appender 若也用了同一个 PATTERN 不受影响，文件里没有光标概念。 |
| PowerShell 粘贴命令后出现 `>>` 续行符不执行 | 粘贴内容含未闭合引号、行尾反引号 `` ` `` 换行或多行块。先按 `Ctrl+C` 退回普通 `PS ...>` 提示符，再改用无反引号换行的完整闭合单行命令执行。 |
