---
title: Docker使用实战-compose教程
description: ""
date: 2025-03-18T15:48:18+08:00
image: images/index/index.png
categories:
    - 开发工具链
tags:
    - Docker 与容器
    - Docker
---



```bash
#--------------------------------------
# 1. 通用/推荐的关闭方式 (任何系统)
#--------------------------------------

# 向 Redis 服务器发送关闭信号 (会安全保存数据)
# 这是最推荐的关闭方式
redis-cli shutdown

#--------------------------------------
# 直接运行 / Docker 容器内 (你当前的环境)
#--------------------------------------

# 启动 (前台运行，日志会占满终端)
redis-server

# 启动 (使用配置文件，推荐)
redis-server /path/to/redis.conf

# 启动 (后台运行，就像你之前用的)
redis-server &

# 关闭 (在 Docker 或直接运行时，用 cli 关闭)
redis-cli shutdown

# 强行关闭 (如果上面的命令无效)
# 1. 找到进程 PID
ps aux | grep redis-server
# 2. 杀死进程 (用 PID 替换 12345)
kill 12345



#--------------------------------------
# Linux (使用 systemd, 如 Ubuntu, CentOS)
#--------------------------------------

# 启动服务
sudo systemctl start redis-server
# (服务名也可能是 redis)
# sudo systemctl start redis

# 停止服务
sudo systemctl stop redis-server

# 重启服务
sudo systemctl restart redis-server

# 查看服务状态
sudo systemctl status redis-server

# 设置开机自启
sudo systemctl enable redis-server


```


下面是一个详细的 Docker Compose 教程，涵盖了从基础概念到实际操作的全面内容。教程将逐步讲解 Docker Compose 的用途、安装、配置文件编写以及常见使用场景，帮助你快速上手。

---

## Docker Compose 起步教程

### 什么是 Docker Compose？
Docker Compose 是一个用于定义和运行多容器 Docker 应用的工具。它通过一个 YAML 文件（通常是 `docker-compose.yml`）来配置多个服务、网络和卷，然后使用单一命令启动和管理这些容器。相比手动运行 `docker run`，它更适合需要协调多个容器的复杂应用。

#### 适用场景
- 开发环境：快速搭建包含前端、后端、数据库等的本地开发环境。
- 测试：运行集成测试或模拟生产环境。
- 小型部署：单机多容器应用的部署。

---

### 安装 Docker Compose
Docker Compose 有两种形式：
1. **旧版（docker-compose）**：一个独立的 Python 工具。
2. **新版（docker compose）**：集成在 Docker CLI 中的插件，从 Docker 20.10 开始默认包含。

#### 检查是否已安装
运行以下命令：
```bash
docker compose version
```
- 如果输出类似 `Docker Compose version v2.x.x`，说明已安装新版。
- 如果提示未找到命令，尝试 `docker-compose --version` 检查旧版。

#### 安装（如果需要）
- **Linux / macOS / Windows（新版）**：
  如果你的 Docker 是最新版（20.10+），无需额外安装，直接用 `docker compose`。
- **旧版安装（可选）**：
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

#### 前提条件
- 已安装 Docker Engine（运行 `docker --version` 确认）。

---

### 基本概念
- **服务（Services）**：一个服务对应一个容器，可以基于镜像启动，定义端口、卷等。
- **网络（Networks）**：Compose 默认创建网络，所有服务可以互相通信。
- **卷（Volumes）**：用于持久化数据，防止容器删除后数据丢失。
- **`docker-compose.yml`**：核心配置文件，描述整个应用。

---

### 创建第一个 Docker Compose 文件
假设我们要搭建一个简单的 Web 应用，包括：
- 一个 Nginx Web 服务器。
- 一个 Redis 数据库。

#### 1. 创建项目目录
```bash
mkdir my-compose-app
cd my-compose-app
```

#### 2. 编写 `docker-compose.yml`
创建一个名为 `docker-compose.yml` 的文件，内容如下：
```yaml
version: '3.8'  # 使用最新稳定的版本
services:
  web:
    image: nginx:latest  # 使用官方 Nginx 镜像
    ports:
      - "8080:80"        # 主机端口 8080 映射到容器端口 80
    volumes:
      - ./html:/usr/share/nginx/html  # 挂载本地 html 文件夹
  redis:
    image: redis:latest  # 使用官方 Redis 镜像
    ports:
      - "6379:6379"      # 映射 Redis 默认端口
    volumes:
      - redis-data:/data # 使用命名卷存储数据

volumes:
  redis-data:          # 定义一个命名卷
```

#### 文件解析
- `version: '3.8'`：指定 Compose 文件格式版本。
- `services`：定义两个服务：
  - `web`：运行 Nginx，映射端口 8080:80，挂载本地 `./html` 文件夹。
  - `redis`：运行 Redis，映射端口 6379，数据存储在命名卷 `redis-data`。
- `volumes`：定义一个命名卷 `redis-data`，用于持久化 Redis 数据。

#### 3. 创建 HTML 文件（可选）
在项目目录下创建 `html` 文件夹，并添加一个简单的 `index.html`：
```bash
mkdir html
echo "<h1>Hello, Docker Compose!</h1>" > html/index.html
```

#### 4. 启动应用
运行以下命令启动所有服务：
```bash
docker compose up -d
```
- `-d` 表示后台运行。

#### 5. 验证
- 检查运行中的容器：
  ```bash
  docker compose ps
  ```
  输出应显示 `web` 和 `redis` 服务状态为 `Up`。
- 访问 Nginx：打开浏览器，输入 `http://localhost:8080`，应看到 "Hello, Docker Compose!"。
- 检查 Redis：用 Redis 客户端连接 `localhost:6379`。

#### 6. 停止和清理
停止服务并删除容器：
```bash
docker compose down
```
如果要删除卷数据：
```bash
docker compose down -v
```

---

### 常用配置字段
以下是 `docker-compose.yml` 中常用的字段：

#### 服务配置
- `image`：指定镜像（如 `nginx:latest`）。
- `build`：构建镜像（替代 `image`），指定 Dockerfile 路径：
  ```yaml
  build:
    context: .       # 构建上下文路径
    dockerfile: Dockerfile  # Dockerfile 文件名
  ```
- `ports`：端口映射，格式 `"主机端口:容器端口"`。
- `volumes`：卷挂载，支持本地路径或命名卷：
  ```yaml
  volumes:
    - ./data:/app/data  # 本地路径
    - my-volume:/data   # 命名卷
  ```
- `environment`：环境变量：
  ```yaml
  environment:
    - DEBUG=true
    - PORT=8080
  ```
- `depends_on`：定义服务启动依赖：
  ```yaml
  depends_on:
    - redis
  ```

#### 全局配置
- `networks`：自定义网络：
  ```yaml
  networks:
    my-network:
      driver: bridge
  ```
- `volumes`：定义命名卷：
  ```yaml
  volumes:
    my-volume:
  ```

---

### 进阶示例：WordPress + MySQL
以下是一个更复杂的例子，搭建 WordPress 和 MySQL：

#### `docker-compose.yml`
```yaml
version: '3.8'
services:
  db:
    image: mysql:8.0
    volumes:
      - db-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: somewordpress
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
    restart: unless-stopped

  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    volumes:
      - wp-data:/var/www/html
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    depends_on:
      - db
    restart: unless-stopped

volumes:
  db-data:
  wp-data:
```

#### 启动
```bash
docker compose up -d
```
访问 `http://localhost:8080`，即可看到 WordPress 安装页面。

---

### 常用命令
- 启动服务：`docker compose up -d`
- 停止服务：`docker compose stop`
- 删除服务（保留卷）：`docker compose down`
- 查看日志：`docker compose logs [服务名]`
- 重启服务：`docker compose restart`
- 构建镜像：`docker compose build`
- 查看服务状态：`docker compose ps`

---

### 保存和迁移
#### 保存镜像
1. 提交容器为镜像：
   ```bash
   docker commit my-compose-app_web_1 mywebimage:latest
   ```
2. 导出镜像：
   ```bash
   docker save -o myimages.tar mywebimage:latest
   ```

#### 备份卷
```bash
docker run --rm -v my-compose-app_db-data:/data -v $(pwd):/backup busybox tar cvf /backup/db-backup.tar /data
```

#### 恢复
1. 加载镜像：
   ```bash
   docker load -i myimages.tar
   ```
2. 恢复卷：
   ```bash
   docker run --rm -v my-compose-app_db-data:/data -v $(pwd):/backup busybox tar xvf /backup/db-backup.tar -C /data
   ```
3. 启动：`docker compose up -d`

---

### 注意事项
- **版本选择**：根据 Docker Engine 版本选择合适的 `version`（推荐 `3.8` 或更高）。
- **命名冲突**：多个 Compose 项目运行时，卷和网络名称可能冲突，可用 `docker compose -p 项目名` 指定项目名。
- **最佳实践**：尽量通过 `build` 和 Dockerfile 定义镜像，而不是手动修改容器。

---

## Dokploy + Traefik 生产部署

### 背景

在 Dokploy 上使用 `docker-compose.dokploy.yml` 部署应用后，页面访问返回 404。这个 404 通常不是前端 Nginx 的 SPA fallback 返回的，因为前端容器内的 `/` 一般会 fallback 到 `index.html`。

更常见的原因是 Traefik 没有匹配到任何路由：

- `DOMAIN` 没有被 Docker Compose 插值，生成了空的 `Host(``)`。
- 访问的域名不是 compose labels 里声明的 Host rule。
- 容器没有接入 Dokploy 的 Traefik 网络。
- 后端不健康，依赖后端健康状态的前端服务没有启动。

### Dokploy 环境变量

在 Dokploy 的 Compose Environment 中必须配置：

```env
DOMAIN=fsense.example.com
```

注意：

- `DOMAIN` 只写域名，不要写 `http://`、`https://` 或路径。
- 本地 `.env.dokploy` 不一定会被 Dokploy 自动加载。除非 Dokploy 的 compose 命令显式使用 `--env-file .env.dokploy`，否则要把变量复制到 Dokploy UI 的 Environment 中。
- 密钥、数据库地址、对象存储配置等也放在 Dokploy Environment，不要写入公开仓库。

### DNS 记录

如果 compose 使用三套前端域名，需要把这些域名都解析到 Dokploy 服务器：

```text
fsense.example.com
admin.fsense.example.com
addin.fsense.example.com
```

对应关系：

| 域名 | 服务 |
| --- | --- |
| `https://${DOMAIN}` | `outlook-index` |
| `https://admin.${DOMAIN}` | `admin-frontend` |
| `https://addin.${DOMAIN}` | `outlook-addin` |

### Traefik labels 模板

主站前端示例：

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=dokploy-network"
  - "traefik.http.middlewares.outlook-index-https-redirect.redirectscheme.scheme=https"
  - "traefik.http.routers.outlook-index-web.rule=Host(`${DOMAIN:?Set DOMAIN in Dokploy environment}`)"
  - "traefik.http.routers.outlook-index-web.entrypoints=web"
  - "traefik.http.routers.outlook-index-web.middlewares=outlook-index-https-redirect"
  - "traefik.http.routers.outlook-index.rule=Host(`${DOMAIN:?Set DOMAIN in Dokploy environment}`)"
  - "traefik.http.routers.outlook-index.entrypoints=websecure"
  - "traefik.http.routers.outlook-index.tls=true"
  - "traefik.http.routers.outlook-index.tls.certresolver=letsencrypt"
  - "traefik.http.services.outlook-index.loadbalancer.server.port=80"
```

管理后台示例：

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=dokploy-network"
  - "traefik.http.middlewares.admin-frontend-https-redirect.redirectscheme.scheme=https"
  - "traefik.http.routers.admin-frontend-web.rule=Host(`admin.${DOMAIN:?Set DOMAIN in Dokploy environment}`)"
  - "traefik.http.routers.admin-frontend-web.entrypoints=web"
  - "traefik.http.routers.admin-frontend-web.middlewares=admin-frontend-https-redirect"
  - "traefik.http.routers.admin-frontend.rule=Host(`admin.${DOMAIN:?Set DOMAIN in Dokploy environment}`)"
  - "traefik.http.routers.admin-frontend.entrypoints=websecure"
  - "traefik.http.routers.admin-frontend.tls=true"
  - "traefik.http.routers.admin-frontend.tls.certresolver=letsencrypt"
  - "traefik.http.services.admin-frontend.loadbalancer.server.port=80"
```

Outlook add-in 示例：

```yaml
environment:
  - OUTLOOK_ADDIN_HOST_URL=https://addin.${DOMAIN:?Set DOMAIN in Dokploy environment}
labels:
  - "traefik.enable=true"
  - "traefik.docker.network=dokploy-network"
  - "traefik.http.middlewares.outlook-addin-https-redirect.redirectscheme.scheme=https"
  - "traefik.http.routers.outlook-addin-web.rule=Host(`addin.${DOMAIN:?Set DOMAIN in Dokploy environment}`)"
  - "traefik.http.routers.outlook-addin-web.entrypoints=web"
  - "traefik.http.routers.outlook-addin-web.middlewares=outlook-addin-https-redirect"
  - "traefik.http.routers.outlook-addin.rule=Host(`addin.${DOMAIN:?Set DOMAIN in Dokploy environment}`)"
  - "traefik.http.routers.outlook-addin.entrypoints=websecure"
  - "traefik.http.routers.outlook-addin.tls=true"
  - "traefik.http.routers.outlook-addin.tls.certresolver=letsencrypt"
  - "traefik.http.services.outlook-addin.loadbalancer.server.port=80"
```

关键点：

- `${DOMAIN:?Set DOMAIN in Dokploy environment}` 可以让 compose 在变量缺失时直接失败，避免部署出空 Host rule。
- `traefik.docker.network=dokploy-network` 明确告诉 Traefik 走 Dokploy 网络。
- `web` 路由负责 HTTP 入口，并通过 middleware 跳到 HTTPS。
- `websecure` 路由负责 HTTPS 入口和证书。

### 网络配置

服务需要接入 Dokploy 的外部网络：

```yaml
networks:
  dokploy-network:
    external: true
```

每个需要被 Traefik 或反向代理访问的服务都要加入该网络：

```yaml
networks:
  - dokploy-network
```

如果服务不需要公网访问，例如内部 backend，可以只 `expose` 端口，不直接挂 Traefik label。

### 只重建后端导致前端 API 代理失效

Dokploy / Docker Compose 部署时可能只重建发生变更的服务。例如后端代码变化后，只重建 `backend`，而 `frontend` 容器没有重启。

这种情况下可能出现一个隐蔽问题：

- `frontend` 里的 Nginx 启动时解析过 `backend:8000`。
- 后端容器重建后，Docker 内部 IP 发生变化。
- 前端容器没有重启，Nginx 仍然可能持有旧的 upstream 解析结果。
- 页面本身还能打开，但 `/api/*` 代理到后端失败，看起来像"前端路由"或"接口路由"坏了。

推荐做法是让 Nginx 使用 Docker 内置 DNS，并定期重解析后端服务名：

```nginx
resolver 127.0.0.11 ipv6=off valid=5s;

location /api/ {
    set $backend_upstream backend:8000;

    rewrite ^/api/?(.*)$ /$1 break;
    proxy_pass http://$backend_upstream;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

注意：`proxy_pass` 一旦使用变量，就不要再写成 `proxy_pass http://$backend_upstream/;`。带变量的 `proxy_pass` 不再沿用普通 `proxy_pass http://backend:8000/;` 的 URI 替换语义，尾部 `/` 很容易把请求错误地转发到根路径。

这个问题和 Traefik Host rule 404 不是同一个层面：

- Traefik Host rule 错误：请求进不了前端容器，通常直接 404。
- Nginx backend DNS 过期：请求能进前端容器，但 `/api/*` 代理后端失败。

### macOS Docker build 使用 Clash 代理

在 macOS + Docker Desktop + Clash 环境里，`docker compose build` 和宿主机终端不是同一个网络视角。宿主机里的 `127.0.0.1` 是 Mac 自己，但 Docker build 容器里的 `127.0.0.1` 是构建容器本身。

一个典型现象是前端镜像构建时报平台原生依赖缺失，例如：

```text
Error: Cannot find module '../lightningcss.linux-arm64-musl.node'
```

如果日志里 `RUN npm ci` 显示为 `CACHED`，说明这次构建没有重新安装依赖。缓存层里可能缺了 Alpine / Linux / arm64 需要的 optional native package，例如 `lightningcss-linux-arm64-musl`。这类问题看起来像 Node 包损坏，本质上经常是“旧 Docker build 缓存层 + 网络代理不稳定”共同导致的。

先强制绕过缓存验证真实问题：

```bash
docker compose build --no-cache kimi-ppt-frontend
```

如果错误变成 `npm ERR! code ECONNRESET`，就说明重新拉包时 Docker build 到 npm registry 的链路不稳定。

检查当前 shell 代理：

```bash
printenv | grep -i proxy
```

检查 `~/.zshrc` 是否有重复覆盖：

```bash
grep -nE 'proxy|Proxy|Clash|789[0-9]' ~/.zshrc
```

容易出现的错误配置是前面写了一个可用端口，后面又覆盖成另一个端口：

```bash
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export ALL_PROXY="socks5://127.0.0.1:7897"

# 后面又覆盖了 http_proxy / https_proxy
export https_proxy=http://127.0.0.1:7899 http_proxy=http://127.0.0.1:7899
```

应该保留一套一致配置。普通宿主机命令可以继续使用 `127.0.0.1`：

```bash
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export HTTP_PROXY="$http_proxy"
export HTTPS_PROXY="$https_proxy"
export ALL_PROXY="socks5://127.0.0.1:7897"
export all_proxy="$ALL_PROXY"
export NO_PROXY="127.0.0.1,localhost,::1,host.docker.internal,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12"
export no_proxy="$NO_PROXY"
```

但 Docker build 里要把代理地址改成宿主机网关：

```bash
docker compose build --no-cache \
  --build-arg HTTP_PROXY=http://host.docker.internal:7897 \
  --build-arg HTTPS_PROXY=http://host.docker.internal:7897 \
  kimi-ppt-frontend
```

如果前端镜像已经重新构建成功，再构建整套服务：

```bash
docker compose build
docker compose up -d
```

验证入口：

```bash
curl -I http://localhost/
curl http://localhost:8000/health
```

如果 `http://localhost/` 返回 `200 OK`，`/health` 返回类似 `{"status":"ok"}`，说明前端和后端容器都已经正常启动。

注意：不要把完整 `~/.zshrc` 粘贴到公开位置。很多人会把 API key、token 和代理配置都放在同一个 shell 配置文件里。

### 404 排查命令

在服务器或 Dokploy 构建环境中检查最终插值结果：

```bash
docker compose -f docker-compose.dokploy.yml config | grep 'Host'
```

正常情况下应该看到实际域名，例如：

```text
Host(`fsense.example.com`)
Host(`admin.fsense.example.com`)
Host(`addin.fsense.example.com`)
```

检查容器是否运行：

```bash
docker ps | grep app-
```

检查后端健康和启动日志：

```bash
docker logs app-backend --tail=100
```

如果后端不健康，依赖 `condition: service_healthy` 的前端服务可能不会启动，Traefik 也就没有可用服务。

### 修复检查清单

- Dokploy Environment 中已设置 `DOMAIN`，且值不包含协议和路径。
- DNS 已解析 `${DOMAIN}`、`admin.${DOMAIN}`、`addin.${DOMAIN}`。
- compose labels 中有 `traefik.docker.network=dokploy-network`。
- HTTPS router 使用 `entrypoints=websecure`、`tls=true`、`tls.certresolver=letsencrypt`。
- HTTP router 使用 `entrypoints=web` 并绑定 HTTPS redirect middleware。
- `docker compose config` 输出的 Host rule 是实际域名，不是空字符串。
- `backend` 健康检查通过，前端容器正常启动。
- 如果只重建过 `backend` 后 `/api/*` 失效，检查前端 Nginx 是否使用 Docker DNS 运行时重解析。

---


