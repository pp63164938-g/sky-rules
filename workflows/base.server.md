---
description: 连接服务器 - 通过 SSH 连接远程服务器并执行操作
---

# 连接服务器工作流

## 服务器列表

### 服务器 A — 腾讯云（个人）

| 项目     | 值                                        |
| -------- | ----------------------------------------- |
| IP       | `43.138.132.82`                           |
| 用户名   | `root`                                    |
| 系统     | OpenCloudOS (主机名: VM-8-13-opencloudos) |
| 认证方式 | SSH 密钥                                  |
| 私钥路径 | `~/.ssh/skey-25y3q7tf.pem`                |

### 服务器 B — 内网测试机（JumpServer）

| 项目           | 值                                                       |
| -------------- | -------------------------------------------------------- |
| IP             | `172.30.1.213`                                           |
| 用户名         | `root`                                                   |
| 密码           | `PgsSB4pZ3igWeJmW`（⚠️ 动态值，过期需向用户索取）       |
| 认证方式       | JumpServer SSH Token                                     |
| JumpServer 地址| `https://jump-dev.skyline.com`                           |
| SSH 端口       | `2222`                                                   |
| JMS Token      | `JMS-46878f07-da20-4ccc-b0cc-02caa1f3b6df`（⚠️ 动态值）|
| API Key ID     | `5fcf2a98-e9dd-40e7-8147-b6e111702b6a`                  |
| API Key Secret | `ZiU87fcenkMG6LG6zJ1MzkAcQT75AXO1O2fu`                 |

**连接方式说明**：此服务器为内网机器，通过 JumpServer 跳板机（`jump-dev.skyline.com:2222`）SSH Token 方式访问。

> ⚠️ **JMS Token 和密码是动态的，会定期过期**。当 SSH 连接出现 `Permission denied` 时，**必须向用户索取新的 Token 和密码**，不要重试旧凭据。

### 服务器 C — RackNerd（pht.plus）

| 项目     | 值                        |
| -------- | ------------------------- |
| IP       | `192.129.240.235`         |
| 用户名   | `root`                    |
| 系统     | Ubuntu 24                 |
| 认证方式 | SSH 密钥                  |
| 私钥路径 | `~/.ssh/pht_plus_ed25519` |
| 面板域名 | `bt.pht.plus`             |

## 连接命令

### 服务器 A（腾讯云）

通过 Git Bash 的 SSH 连接（CMD 中无原生 ssh）：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i %USERPROFILE%\.ssh\skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82
```

### 服务器 B（JumpServer）

通过 JumpServer SSH Token 连接（端口 2222）：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -o StrictHostKeyChecking=no -p 2222 JMS-46878f07-da20-4ccc-b0cc-02caa1f3b6df@jump-dev.skyline.com
```

连接后会要求输入密码：`PgsSB4pZ3igWeJmW`

### 服务器 C（RackNerd / pht.plus）

通过 Git Bash 的 SSH 连接：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i %USERPROFILE%\.ssh\pht_plus_ed25519 -o StrictHostKeyChecking=no root@192.129.240.235
```

// turbo-all

## 执行步骤

1. 使用上述命令连接服务器
2. 连接成功后，根据用户需求执行操作
3. 操作完成后退出服务器（`exit`）

## 构建部署

### 部署决策规则

> [!IMPORTANT]
> **内网服务器已配置 git，部署时优先直接在内网 `git pull` + `docker compose build`**。
> 跨服务器镜像迁移（腾讯云 → 内网）仅作为**备用方案**，仅在内网 git 不可用时使用。

| 部署目标 | 首选方案 | 备用方案 |
|---------|---------|--------|
| **腾讯云** | SSH 单次命令 `git pull` + `docker compose build` | — |
| **内网** | JumpServer 交互式连接 → `git pull` + `docker compose build` | 腾讯云构建 → 镜像迁移 |

### 服务器项目路径识别

**禁止硬编码项目路径**，必须根据当前工作区动态确定：

1. 从当前工作区 URI 提取项目名（如 `d:\self\Ai\more-tool` → `more-tool`）
2. **腾讯云**项目路径为 `/.self/<项目名>`（如 `/.self/more-tool`）
3. **内网**项目路径为 `/opt/<项目名>`（如 `/opt/more-tool`）
4. 如果不确定，先用 `find / -maxdepth 3 -name "<项目名>" -type d 2>/dev/null` 确认路径

### 服务器通用信息

| 项目            | 腾讯云                                                     | 内网                              |
| --------------- | --------------------------------------------------------- | --------------------------------- |
| 项目根目录      | `/.self/`                                                 | `/opt/`                           |
| Node.js 路径    | `/www/server/nodejs/v22.16.0/bin/`                        | 同左                              |
| GitHub 远程仓库 | HTTPS + PAT Token 认证                                    | 同左（已配置 git）                |
| Git HTTP 版本   | 已配置降级为 HTTP/1.1（解决腾讯云访问 GitHub 不稳定问题） | 无需降级                          |

### 部署方式自动检测

**构建前必须先检测项目的部署方式**，禁止盲目假设：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "cd /.self/<PROJECT> && ls docker-compose.yml 2>&1; docker ps --filter name=<PROJECT> --format '{{.Names}} {{.Status}}' 2>&1"
```

判断规则：

| 条件 | 部署方式 | 构建命令 |
|------|---------|---------|
| 有 `docker-compose.yml` 且有运行中容器 | **Docker** | `docker compose up -d --build ...` |
| 无 `docker-compose.yml` 或无容器 | **裸构建 + PM2** | `pnpm build` + `pm2 restart` |

### 构建步骤

使用**单次 SSH 远程执行命令**方式（避免交互终端输出混乱）。

以下命令中的 `<PROJECT>` 替换为实际项目名（从当前工作区推导）：

**通用步骤 — 拉取最新代码：**

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "cd /.self/<PROJECT> && git pull 2>&1"
```

#### Docker 方式

重新构建并启动（仅重建 web 和 server，不动 mysql 等依赖服务）：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "cd /.self/<PROJECT> && docker compose up -d --build --no-deps web server 2>&1"
```

- **`--no-deps`**：不重建依赖服务（mysql），避免端口冲突
- **`--build`**：强制重新构建镜像（使用最新代码）

#### 裸构建 + PM2 方式

根据项目的 `package.json` scripts 决定具体构建命令，通常为：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "export PATH=/www/server/nodejs/v22.16.0/bin:\$PATH && cd /.self/<PROJECT> && pnpm install && pnpm build 2>&1"
```

构建完成后重启 PM2 进程：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "export PATH=/www/server/nodejs/v22.16.0/bin:\$PATH && pm2 restart <进程名> 2>&1"
```

### 关键注意事项

- `git pull` 如果卡住，通常是 GitHub PAT Token 过期，需要用户提供新 Token 后更新远程 URL
- 更新 Token 命令：`git remote set-url origin https://用户名:TOKEN@github.com/用户名/仓库.git`

### 内网服务器直接部署

内网服务器已配置 git，可以直接 `git pull` + `docker compose build`，无需跨服务器迁移。

连接内网后执行（路径为 `/opt/<PROJECT>`）：

```bash
cd /opt/<PROJECT> && git pull && docker compose up -d --build --no-deps web server
```

### 跨服务器 Docker 镜像迁移（腾讯云 → 内网）【备用方案】

**适用场景**：内网服务器 git 不可用时的备用方案，通过腾讯云构建镜像后传输到内网。

**前提条件**：
- 内网服务器可访问腾讯云公网 IP（已验证可通）
- 腾讯云安全组已放行 3000 端口（Docker 项目默认端口）

> [!IMPORTANT]
> **慢操作由用户执行**：`docker save`（镜像导出）和 `curl`（镜像下载）耗时较长且无进度输出，
> AI 执行时会显示卡住。**这两个步骤必须提供命令让用户自行执行**，不要用 `run_command` 直接执行。
> 用户执行完毕后由 AI 继续后续步骤。

**完整流程**：

#### 步骤 1：腾讯云拉取代码 + 构建镜像

// turbo

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "cd /.self/<PROJECT> && git pull 2>&1"
```

// turbo

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "cd /.self/<PROJECT> && docker compose up -d --build 2>&1"
```

#### 步骤 2：导出镜像 + 启动临时 HTTP（⚠️ 用户执行）

> [!WARNING]
> `docker save` 耗时 30-60 秒且无输出，**必须提供命令让用户在自己的终端执行**。

将以下命令提供给用户，在 Git Bash 终端执行：

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "docker save <PROJECT>-web <PROJECT>-server | gzip > /tmp/<PROJECT>-images.tar.gz && ls -lh /tmp/<PROJECT>-images.tar.gz && echo DONE"
```

使用 `gzip` 压缩可从 ~200MB 减小到 ~73MB，加快传输速度。

#### 步骤 3：腾讯云停 web 容器 + 启临时 HTTP

// turbo

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "docker stop <PROJECT>-web-1 2>/dev/null; cd /tmp && nohup python3 -m http.server 3000 > /dev/null 2>&1 & echo 'HTTP_READY'"
```

> **端口选择**：必须使用腾讯云安全组已放行的端口（如 3000）。9999 等未放行端口会超时。

#### 步骤 4：内网下载 + 加载 + 启动

在内网服务器的 **JumpServer SSH 交互式会话**中执行：

```bash
curl -o /tmp/<PROJECT>-images.tar.gz http://43.138.132.82:3000/<PROJECT>-images.tar.gz && gunzip -c /tmp/<PROJECT>-images.tar.gz | docker load && cd /opt/<PROJECT> && docker compose up -d
```

> 下载 73MB 约需 3-4 分钟，`curl` 会显示进度条。

如果是**首次部署**，需要先创建 `docker-compose.yml`（使用 `image` 而非 `build`）：

```bash
mkdir -p /opt/<PROJECT> && cat > /opt/<PROJECT>/docker-compose.yml << 'EOF'
services:
  web:
    image: <PROJECT>-web:latest
    ports:
      - "3000:3000"
    depends_on:
      - server
    extra_hosts:
      - "gitlab.praise.com:172.30.1.225"
    restart: unless-stopped

  server:
    image: <PROJECT>-server:latest
    ports:
      - "3001:3001"
    environment:
      - PORT=3001
    restart: unless-stopped
EOF
```

#### 步骤 5：清理腾讯云临时资源

关闭临时 HTTP 服务，恢复腾讯云 Docker 容器：

// turbo

```bash
"C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/skey-25y3q7tf.pem -o StrictHostKeyChecking=no root@43.138.132.82 "fuser -k 3000/tcp 2>/dev/null; cd /.self/<PROJECT> && docker compose up -d --no-recreate 2>&1"
```

#### 步骤 6：验证内网服务

```bash
curl -s -o /dev/null -w "web: HTTP %{http_code}\n" http://localhost:3000
curl -s -o /dev/null -w "server: HTTP %{http_code}\n" http://localhost:3001
```

内网访问地址：`http://172.30.1.213:3000`

#### 关键注意事项

- **慢操作（导出/下载）**：必须提供命令让用户执行，不要用 `run_command`
- **端口限制**：腾讯云安全组只放行了特定端口（80、443、3000、3001 等）
- **docker-compose.yml 差异**：内网用 `image` 引用预构建镜像，腾讯云用 `build` 从源码构建
- **镜像名称**：`docker save` 和 `docker load` 的镜像名必须与 `docker-compose.yml` 中 `image` 字段一致
- **传输后清理**：传输完成后务必关闭腾讯云临时 HTTP 服务并恢复原有容器

## 注意事项

- 私钥文件必须使用 **Unix 换行符**（`\n`），Windows 换行符（`\r\n`）会导致认证失败
- 如需修复换行符：`"C:\Program Files\Git\usr\bin\sed.exe" -i "s/\r$//" %USERPROFILE%\.ssh\skey-25y3q7tf.pem`
- CMD 环境中 SSH 以非交互模式运行（无 TTY），优先使用**单次 SSH 远程执行命令**而非交互式会话
- 用户名是 `root`，不是 `lighthouse`
