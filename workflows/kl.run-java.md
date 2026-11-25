---
description: 在本机启动 Kunlun / sky 系 Java / Spring Boot 后端，并按现象闭环处理编译失败、启动失败、端口、Nacos 环境切换、日志乱码和断点。仅当用户显式点名 kl-run-java 或明确要求按本工作流执行本机 Java 后端启动时使用。
allow_implicit_invocation: false
---

# 本地跑 Java 后端（kl-run-java）

这是 Kunlun / sky 系 Java 后端的本地启动做法。先看当前项目自己的启动类、配置和日志，不要把上一个项目的端口、classpath、数据源或登录补丁照搬过来。

## 入口与环境前置确认

仅在用户点名 `kl-run-java`，或明确要求「按 kl-run-java 跑」「用这个工作流启动本机后端」时使用。

只说「本地跑后端」「把项目跑起来」「换端口启动」「日志乱码」而不点名本工作流的普通相似任务，不构成触发条件；按当前任务适用的其他规则处理，不进入本工作流的固定产物生成和回执流程。

项目目录用用户指定的；没指定时，用当前目录里有 `pom.xml` 和启动类的那个。HTTP 端口用用户指定的；没指定时读项目默认端口。JDWP 调试端口默认 `5005`。HTTP 端口或调试端口被**其他程序**占用时不要杀进程，顺延换一个空闲端口（调试端口顺延后同步写入 `.vscode/launch.json`），并在结果里说明原端口被谁占用。

有两种方式，都要在最后给出同一条可复制的单行命令：

- 用户要自己跑：只输出命令，不启动进程。
- 用户要直接跑起来：用这条命令在后台启动，再用健康检查和配置实证确认。

环境与配置中心指向确认：

1. 先列出项目 `document/k8s` 里 `*-values*.yaml` 的 `SPRING_PROFILES_ACTIVE`，这些才是当前项目可切换的环境，不要写死成 `dev`、`test`、`prod`。用户指定其中一个就用它；没指定时用 `dev`；项目没有 `dev` 时问用户选哪个。
2. 切换环境只改启动参数，不改项目代码。密码只出现在当次命令或本机 `$env:TEMP` 临时 `.props` 文件里，不写进技能，不提交。没有对应 values 时，只传 `-Dspring.profiles.active=<环境>`，缺账号就问用户。
3. **禁止假定同名 K8s 内网域名指向同一套 Nacos**：不同环境的 values 可能都写 `*.svc.cluster.local`，但在各自集群内指向不同 Nacos 实例，而本机办公网 DNS 常固定解析到单一集群（如 `dev`）；同时跨集群环境的 Nacos 外部域名可能只开放 HTTP 80 而未开放 Nacos 2.x 客户端必需的 gRPC 端口（`端口 + 1000`）。切非默认环境前，先在本机核对 `NACOS_HOST` 解析落点与 gRPC 可达性：
   - 若同一配置中心按后缀区分环境且 gRPC 可达，传入对应 `NACOS_*` 与 `-Dspring.profiles.active=<环境>`。
   - 若目标环境 Nacos 仅 HTTP 配置接口可达而 gRPC 不可达，或本机 DNS 固定落到另一集群 Nacos：禁止拿跨集群密码硬撞，也禁止在主数据源仍连旧集群库时宣称已切到目标环境；应通过可达 HTTP 接口拉取目标环境配置到 `$env:TEMP`，在 `.props` 中以 `-Dspring.config.additional-location=file:<正斜杠路径>` 加载（多文件按公共配置在前、应用配置在后逗号分隔；或结合用户已确认的目标库凭证显式覆盖 `spring.datasource.dynamic.datasource.<名称>.url/username/password` / `spring.datasource.*`，并将集群内地址如 Doris 内网端口替换为注释或公共配置标明的集群外端口）。

## 步骤

1. **确认 JDK 与模块开放参数前置**：确认 JDK 与 `pom.xml` 的 `maven.compiler.source` 一致。启动类看 `*Application.java` 的 `package` 加类名，不看 `artifactId`。当 `maven.compiler.source >= 9`（如 JDK 17）时，启动前直接从 `document/k8s` 里 `*-values*.yaml` 的 `DYNAMIC_JAVA_OPTS` 提取全部 `--add-opens`，统一规范为 `--add-opens=<module>/<package>=ALL-UNNAMED` 等号单参数形式，作为启动命令固定项，后续排障重试不得删减。
2. **编译与按项目隔离的幂等参数文件**：先 `compile` 再启动（`compile` 只生成 `target/classes`；不用 IDE 临时生成的 `cp_*.argfile`）。用 Maven 为本项目生成 runtime classpath，写入按 `<artifactId>` 隔离的 `$env:TEMP\kl-run-java-<artifactId>.argfile`；所有 `-D` 参数整份覆写到 `$env:TEMP\kl-run-java-<artifactId>.props`（UTF-8 无 BOM，每个 key 只保留一行，禁止用 `+=` 反复追加制造重复行）：
   - 必带基础项：`-Dserver.port=<端口>`、`-Dlocal.run=true`、项目需要的 `-Dspring.profiles.active=<环境>` 及已确认的配置中心 / 数据源参数。
   - **非主链路子数据源降级规则**：多数据源项目（`dynamic-datasource`）若某个子数据源缺凭证或网络不通，先在项目源码搜索 `@DS("<名称>")` 核查引用范围——命中当前验证主链路时**禁止忽略**，停下向用户确认该库连接串与账号；确认仅旁路模块使用时，写入 `-Dspring.datasource.dynamic.datasource.<名称>.lazy=true` 跳过启动期建池，并在回执中列明受影响功能。非阻塞外部组件（如本地不可达的调度中心注册）保持不阻断启动并在回执说明。
3. **自包含单行运行指令（关旧启新合一）**：进程放后台，不要另建日志文件。无论是首次启动、排障重试还是最终交付，输出给用户在 PowerShell 执行的运行指令必须满足：
   - **强制完整单行**，语句间以 `;` 分隔，引号成对闭合；严禁使用行尾反引号 `` ` `` 折行或 `@'...'@` 多行文本块（防止终端卡进 `>>` 续行提示符）。
   - **开头固定只按 `<启动类全名>` 停止本服务旧进程**，再启动新进程（严禁按端口杀进程）。用户重复执行同一条命令即可自动关闭本服务上一次进程、释放原端口并重新开启：

```powershell
Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -like '*<启动类全名>*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }; chcp 65001 > $null; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Set-Location '<项目目录>'; & '<JDK目录>\bin\java.exe' '-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=<调试端口>' <全部--add-opens参数> '-Dfile.encoding=UTF-8' '-Dsun.stdout.encoding=UTF-8' '-Dsun.stderr.encoding=UTF-8' -cp "@$env:TEMP\kl-run-java-<artifactId>.argfile" "@$env:TEMP\kl-run-java-<artifactId>.props" '<启动类全名>'
```

   生成 classpath 的准备步骤（代码或依赖变化时执行）：

```powershell
mvn -q compile "-Dmdep.includeScope=runtime" "-Dmdep.outputFile=$env:TEMP\kl-run-java-<artifactId>-cp.txt" dependency:build-classpath; $cp = "target\classes;" + ([System.IO.File]::ReadAllText("$env:TEMP\kl-run-java-<artifactId>-cp.txt").Trim()); [System.IO.File]::WriteAllText("$env:TEMP\kl-run-java-<artifactId>.argfile", $cp, (New-Object System.Text.UTF8Encoding($false)))
```

4. **健康检查与最终生效环境实证**：
   - 用项目自己的健康检查确认起来了。Spring Boot 通常是 `http://127.0.0.1:<端口>/actuator/health` 返回 `UP`。日志里出现数据源 `Start completed` 不算成功，进程退出或端口没监听就是失败。
   - **核验实际连通的环境与数据库**：若暴露了 `/actuator/env`，必须读取最终生效的 `spring.profiles.active` 及主数据源 `url` 的主机与库名（脱敏）；未暴露时核对启动日志实际加载的 `PropertySource` 与连接目标。**严禁只凭命令行传入的 `-D` 占位符回显就宣称已连上目标环境**。如果进程没注册到目标环境配置中心，如实告知原因，不要假装已经连上。
5. **异常按需排障（一轮闭环）**：编译失败、启动后进程退出、健康检查未通过，或实测数据源与目标环境不一致时，读取 [启动异常排障引用](references/kl-run-java--troubleshooting.md)，从项目已有日志文件（由 `logback*.xml` 的 `LOG_HOME` 确定，UTF-8 读取，不另建日志文件）取首个失败层级的 `Caused by` 最小修一次，再查健康检查与环境实证。不要同时改多个配置；同一失败签名修一次仍失败，把准确原因和日志路径交给用户，不要继续猜。

断点说明：上面的命令只打开调试端口（默认 `5005`），不会自动连上 IDE。VS Code 按 `Ctrl+Shift+D`，选 `Java: Attach`，服务起来后按 `F5`。不附加时服务照常跑，断点不会停。一条命令不能同时完成「启动 Java」和「打开 IDE 调试器」。

## 怎样算办成

第一次启动、修复后重启、换端口、换环境，只要服务重新启动了（或应用户要求给出启动方案），最后回答都必须**单独逐项**列出下面 9 项，不能只报进程号和健康检查，不要散落在说明段落里：

1. 环境：本次请求的 profile 与实测生效的 profile（不一致时显式说明原因）。另起一行列出本项目可切换的环境，并写明换环境时说「用 `<profile>` 跑」。
2. 实际连通数据源：主数据源最终生效的连接主机名与库名（脱敏实证，禁止回显密码，禁止拿未被引用的 `-D` 占位符充数）。
3. 忽略 / 懒加载项：列出本次启用 `lazy=true` 的子数据源或未连通的非阻塞外部组件，以及关联的 `@DS` 模块与暂不可测的功能；全部正常连通时写「无」。
4. 端口：实际使用的 HTTP 端口与 JDWP 调试端口（若因占用顺延，注明原端口被谁占用）。
5. 访问地址：`http://127.0.0.1:<端口>/actuator/health`（或项目自己的健康检查地址）及实测状态。
6. 运行指令：一整行闭合 PowerShell，用户可以粘贴到自己的终端直接执行。命令开头只停命令行里包含本次启动类的旧进程，再带齐实际 JDK 路径、`--add-opens`、调试端口、`@argfile`、`@props` 和启动类；重复执行同一条指令即可完成重启，不要按端口停进程。
7. 关闭指令：单独一行 PowerShell。只停命令行里包含本次启动类的 Java 进程，不需要端口，也不要按端口停，避免关掉别的服务。
8. 日志：项目已有日志文件的完整路径。不另建日志文件。终端中文乱码时，用 UTF-8 打开这个文件。
9. 断点：写明下拉框要选哪个配置、对应的调试端口，以及点绿色按钮（或按 `F5`）之前服务必须已经在跑。不要只写调试端口。

由技能启动时，健康检查通过（或项目没有健康检查时端口已监听且进程未退出）且主数据源目标核验一致，才算跑起来。用户只要命令时，不启动进程。

## 固定生成这两个文件

每次执行都生成下面两个文件，让本地登录、跨域和断点随时可用。日志用项目已有文件，不新建日志文件，也不生成启动脚本。

两个文件都禁止提交、禁止推送。文件里写明这句，并在交给用户前再提醒一次。不要改 `.gitignore`、`.git/info/exclude` 或 Git 钩子。不要执行 `git add`、`commit` 或 `push`。生成后看 `git status`，出现了就告诉用户提交时必须排除。

### 1. 本地运行补丁

每次都生成。文件已存在且用户没提供新值时，不要覆盖已有的 `staffId`、`jobNumber`、`name`。文件不存在时，先向用户要这三项，不能从旧项目抄，也不能猜：

- `staffId`
- `jobNumber`
- `name`

包名用当前项目启动类第一行的 `package` 加 `.config`。文件放在启动类旁边新建的 `config` 目录，文件名固定 `LocalDevRun.java`。文件第一行必须写：

```text
【禁止提交】【禁止推送】这个文件只留在本机。不要执行 git add，提交前如果它出现在暂存区，先拿掉。
```

这个文件负责本地登录用户和跨域。`staffId`、`jobNumber`、`name` 用用户提供的值。不要用 `@Profile` 绑定 `dev` 或 `test`，否则切换环境后补丁不生效。用 `@ConditionalOnProperty(name = "local.run", havingValue = "true")`。凡是本地直连启动，命令里都加 `-Dlocal.run=true`，和 `-Dspring.profiles.active` 分开。没有这个参数时，补丁不加载。

### 2. VS Code 调试配置

每次都生成 `.vscode/launch.json`。内容只包含一个 `Java: Attach`，端口与本次启动命令实际使用的 `<调试端口>`（默认 `5005`）一致。文件已存在时只确认或更新这个配置，不删除用户已有的其他配置。文件开头用注释写明禁止提交、禁止推送。

断点：服务起来后按 `Ctrl+Shift+D`，选这个配置，再按 `F5`。不按 `F5` 则断点不停。

## 什么时候停下交给用户

- 缺配置中心或当前验证链路核心数据源的账号密码 / 本机可达连接地址，不能从项目里推断。
- 请求切换跨集群环境，但目标配置中心与目标数据库均无本机可达路径或缺少凭证。
- 缺的依赖在本机和公司仓库都不存在，或按分支版本查找后仍缺类。
- 同一失败签名按排障引用修一次后仍失败，或健康检查连续两次失败且不属于排障引用中的已知现象。
- 用户没有提供 `staffId`、`jobNumber`、`name` 且本地不存在已填好的 `LocalDevRun.java`，不能生成登录补丁。
- 用户要求提交或推送 `LocalDevRun.java` 或 `.vscode/launch.json`。拒绝，并说明这两个文件禁止提交、禁止推送。
