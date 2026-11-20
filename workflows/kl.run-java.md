---
description: 在本机启动 Kunlun / sky 系 Java / Spring Boot 后端，并按现象闭环处理编译失败、启动失败、端口、Nacos 环境切换、日志乱码和断点。仅当用户显式点名 kl-run-java 或明确要求按本工作流执行本机 Java 后端启动时使用。
allow_implicit_invocation: false
---

# 本地跑 Java 后端（kl-run-java）

这是 Kunlun / sky 系 Java 后端的本地启动做法。先看当前项目自己的启动类、配置和日志，不要把上一个项目的端口、classpath、数据源或登录补丁照搬过来。

## 入口

仅在用户点名 `kl-run-java`，或明确要求「按 kl-run-java 跑」「用这个工作流启动本机后端」时使用。

只说「本地跑后端」「把项目跑起来」「换端口启动」「日志乱码」而不点名本工作流的普通相似任务，不构成触发条件；按当前任务适用的其他规则处理，不进入本工作流的固定产物生成和回执流程。

项目目录用用户指定的。没指定时，用当前目录里有 `pom.xml` 和启动类的那个。端口用用户指定的。没指定时读项目默认端口；默认端口被占用就换一个空闲端口。

有两种方式，都要在最后给出同一条可复制命令：

- 用户要自己跑：只输出命令，不启动进程。
- 用户要直接跑起来：用这条命令在后台启动，再用健康检查确认。

先列出项目 `document/k8s` 里 `*-values*.yaml` 的 `SPRING_PROFILES_ACTIVE`，这些才是当前项目可切换的环境，不要写死成 `dev`、`test`、`prod`。用户指定其中一个就用它。没指定时用 `dev`；项目没有 `dev` 时问用户选哪个。

切换环境只改启动参数，不改项目代码。把选中文件里的 `NACOS_HOST`、`NACOS_PORT`、`NACOS_USER`、`NACOS_PASSWORD` 转成 `-D` 放进这一次的命令。密码只出现在当次命令里，不写进技能，不提交。没有对应 values 时，只传 `-Dspring.profiles.active=<环境>`，缺账号就问用户。

`dev` 和 `test` 的 Nacos 地址可能相同。切换后加载的是配置中心里带环境后缀的配置，不是换了一台机器。回答里要写明这次用的环境。如果进程没注册到该环境的 Nacos，把日志里的注册失败原因告诉用户，不要假装已经连上。

## 步骤

1. 确认 JDK 与 `pom.xml` 的 `maven.compiler.source` 一致。启动类看 `*Application.java` 的 `package` 加类名，不看 `artifactId`。
2. 先编译再启动。`compile` 只生成 `target/classes`，本地调试用这个。`package` 会再打包，`install` 是把当前项目装进本机仓库给别的项目按完全相同坐标引用。不要用 IDE 临时生成的 `cp_*.argfile`，那份可能属于另一个项目。
3. 用 Maven 为本项目生成 classpath，再启动。进程放后台，不要另建日志文件。启动参数至少包含用户指定的端口和 UTF-8。Spring profile 只在项目需要时加。输出给用户的命令开头只停本项目的旧进程，再启动新进程。判断依据是命令行里包含这次的启动类全名。端口被别的程序占用时不要杀进程，换一个空闲端口，并在结果里说明原端口被谁占用。

```powershell
Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -like '*<启动类全名>*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }; chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
mvn -q -DincludeScope=runtime "-DoutputFile=$env:TEMP\kl-run-java-cp.txt" dependency:build-classpath
$cp = "target\classes;" + ((Get-Content -Raw "$env:TEMP\kl-run-java-cp.txt").Trim())
Set-Content -NoNewline "$env:TEMP\kl-run-java.argfile" $cp
& java "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005" "-Dfile.encoding=UTF-8" "-Dsun.stdout.encoding=UTF-8" "-Dsun.stderr.encoding=UTF-8" "-Dserver.port=<端口>" -cp "@$env:TEMP\kl-run-java.argfile" "<启动类全名>"
```

4. 用项目自己的健康检查确认起来了。Spring Boot 通常是 `http://127.0.0.1:<端口>/actuator/health` 返回 `UP`。日志里出现数据源 `Start completed` 不算成功，进程退出或端口没监听就是失败。
5. 失败时读项目自己的日志文件，取最后一条 `Caused by`，对照下表修一次，再查健康检查。同一类错误修一次仍失败，把原因和这个日志路径交给用户，不要继续改。

闭环只走这一轮：编译失败先看依赖；启动后进程退出或端口没监听，就看项目日志文件末尾；健康检查通过才结束。不要同时改多个配置。

日志不另建文件。先看项目 `logback*.xml` 的 `LOG_HOME`，把那个已有文件的完整路径告诉用户。控制台中文乱码时，用 UTF-8 打开这个文件，不要看终端。

断点：上面的命令只打开调试端口 `5005`，不会自动连上 IDE。VS Code 按 `Ctrl+Shift+D`，添加配置选 `Java: Attach`，端口填 `5005`，服务起来后按 `F5`。不附加时服务照常跑，断点不会停。一条命令不能同时完成「启动 Java」和「打开 IDE 调试器」。

## 容易出错的地方

先看现象，再决定查哪一层。不要一上来改业务代码或换一个更大的版本号。

| 现象 | 方向 |
|---|---|
| 找不到主类 | 没编译，或 classpath 来自别的项目。重新编译，并用本项目 Maven 生成的 classpath。 |
| 找不到依赖里的类，或实现类和方法签名对不上 | 优先按当前 Git 分支解决，不改业务代码。分支名 `feature/v` 后面的那段就是版本号，例如 `feature/v1.1.1` 对应 `1.1.1-SNAPSHOT`。`feature/v*` 合并到 `develop` 后生成 test 环境的包；`integration` 分支对应 dev 环境的包。先用这个版本到对应环境仓库找 jar。找不到再停，把分支、版本号和缺的坐标交给用户。不要按仓库里更大的版本号替换，不要给接口补空实现，不要改 Controller 或 Service。 |
| 依赖下载失败 | IDE 里勾的 profile 多半只影响发布地址。下载仓库看本机 `settings.xml` 的 `mirrorOf`。缺的包可能在另一个环境仓库，不要改全局 settings 去影响所有项目。 |
| `using password: NO`，用户名变成操作系统用户名 | 数据源账号密码是空的。地址和账号通常在配置中心，不在代码和 k8s values 里。本地 values 文件不会自动生效。可以懒加载这个数据源，不要猜密码。 |
| 直连本地后登录用户为空或预检失败 | 浏览器只带 token。用户信息和跨域头通常由网关补上，绕过网关就会丢。按下面「本地运行补丁」生成单独文件。 |
| 浏览器拒绝连接 | 进程已经退出或端口没监听。往日志末尾找 `Caused by`，不要看中间的连接池启动日志。 |
| 中文日志乱码，英文正常 | 程序按 UTF-8 输出，Windows 终端按 GBK 显示。这不是业务错误。启动前执行 `chcp 65001`，并加上面的三个 encoding 参数。文件日志用 UTF-8 打开核对。 |

k8s 的 `*-values.yaml` 只在部署时注入环境变量。本地点运行用的是 `bootstrap` / `application` 的默认值，加上你显式传的 `-D`。

## 怎样算办成

第一次启动、修复后重启、换端口、换环境，只要服务重新启动了，最后回答都必须单独列出这几项。不能只报进程号和健康检查。不要散落在说明里：

1. 环境：当前跑的 profile。另起一行列出本项目可切换的环境，并写明换环境时说「用 <profile> 跑」。
2. 端口：实际使用的端口。
3. 访问地址：`http://127.0.0.1:<端口>/actuator/health`，或项目自己的健康检查地址。
4. 运行指令：一整行 PowerShell，用户可以粘贴到自己的终端执行。命令开头只停命令行里包含本次启动类的旧进程，再启动。不要按端口停进程。命令里的端口、启动类和 JDK 路径都换成这次的实际值。
5. 关闭指令：单独一行 PowerShell。只停命令行里包含本次启动类的 Java 进程，不需要端口，也不要按端口停，避免关掉别的服务。
6. 日志：项目已有日志文件的完整路径。不另建日志文件。终端中文乱码时，用 UTF-8 打开这个文件。
7. 断点：写明下拉框要选哪个配置，以及点绿色按钮之前服务必须已经在跑。不要只写调试端口。

由技能启动时，健康检查通过，或项目没有健康检查时端口已监听且进程没有退出，才算跑起来。用户只要命令时，不启动进程。

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

每次都生成 `.vscode/launch.json`。内容只包含一个 `Java: Attach`，端口是启动命令里的 `5005`。文件已存在时只确认这个配置在，不删除用户已有的其他配置。文件开头用注释写明禁止提交、禁止推送。

断点：服务起来后按 `Ctrl+Shift+D`，选这个配置，再按 `F5`。不按 `F5` 则断点不停。

## 什么时候停下交给用户

- 缺的是配置中心或数据库里的账号密码，不能从项目里推断。
- 缺的依赖在本机和公司仓库都不存在，或换版本后仍缺类。
- 健康检查连续两次失败，且不是上面表里的现象。
- 用户没有提供 `staffId`、`jobNumber`、`name`，不能生成登录补丁。
- 用户要求提交或推送 `LocalDevRun.java` 或 `.vscode/launch.json`。拒绝，并说明这两个文件禁止提交、禁止推送。
