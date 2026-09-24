---
title: "Docker Swarm 实战（二）：Traefik 反向代理部署"
description: 在 Docker Swarm 集群上部署 Traefik v2 作为反向代理，含 HTTPS 自动证书和踩坑记录。
date: 2026-04-12T11:00:00+08:00
image: images/index/index.png
slug: docker-swarm-traefik-deployment
categories:
    - Platforms_Tools
tags:
    - Docker
draft: false
---

> 记录一次真实的生产环境部署过程，包含踩过的坑和解决方案。

**环境说明**

- 服务器：阿里云 ECS（Ubuntu）
- 应用栈：FastAPI 后端 + Next.js 前端 + Celery + Redis
- 反向代理：Traefik v2.11
- 容器编排：Docker Swarm
- 镜像仓库：阿里云 ACR

---

**第一步：安装 Docker**

```bash
curl -fsSL https://get.docker.com | sh
```

国内服务器如果无法访问，通过 DaoCloud 镜像拉取：

```bash
# 拉取镜像示例
docker pull docker.m.daocloud.io/traefik:v2.11
```

验证安装：

```bash
docker version
```

---

**第二步：初始化 Docker Swarm**

单机部署时，本机既是 manager 也是 worker：

```bash
docker swarm init --advertise-addr <服务器公网IP>
```

执行后会输出一个 `docker swarm join` 命令，如果以后需要加入 worker 节点可以用它。

---

**第三步：创建 Traefik 公共网络**

Traefik 通过 overlay 网络发现各服务，这个网络必须在部署任何 stack 之前创建好：

```bash
docker network create --driver overlay --attachable traefik-public
```

> **重要**：应用的 `docker-compose.stack.yml` 中 `traefik-public` 网络标记为 `external: true`，如果这个网络不存在，`docker stack deploy` 会直接报错失败。

---

**第四步：准备 Traefik 配置文件**

将以下 `stack.yml` 上传到服务器 `/opt/myapp/traefik/stack.yml`：

```yaml
services:
  traefik:
    image: docker.m.daocloud.io/traefik:v2.11
    command:
      - --providers.docker=true
      - --providers.docker.swarmMode=true
      - --providers.docker.endpoint=unix:///var/run/docker.sock
      - --providers.docker.exposedByDefault=false
      - --providers.docker.network=traefik-public
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
      - --entrypoints.web.http.redirections.entrypoint.scheme=https
      - --certificatesresolvers.letsencrypt.acme.email=${TRAEFIK_ACME_EMAIL}
      - --certificatesresolvers.letsencrypt.acme.storage=/var/lib/traefik/acme/acme.json
      - --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
      - --ping=true
    ports:
      - target: 80
        published: 80
        protocol: tcp
        mode: host
      - target: 443
        published: 443
        protocol: tcp
        mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /opt/myapp/traefik/acme.json:/var/lib/traefik/acme/acme.json
    networks:
      - traefik-public
    healthcheck:
      test: ["CMD", "traefik", "healthcheck", "--ping"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role==manager

networks:
  traefik-public:
    external: true
    name: traefik-public
```

---

**第五步：准备 ACME 证书存储文件**

Traefik 会自动申请 Let's Encrypt 证书并写入这个文件，**文件必须提前创建且权限为 600**：

```bash
mkdir -p /opt/myapp/traefik
touch /opt/myapp/traefik/acme.json
chmod 600 /opt/myapp/traefik/acme.json
```

> 文件内容是空的完全没问题，Traefik 首次启动后会自动填充。

---

**第六步：部署 Traefik**

```bash
cd /opt/myapp/traefik

TRAEFIK_ACME_EMAIL=你的邮箱@example.com \
docker stack deploy -c stack.yml traefik
```

验证是否正常运行：

```bash
docker stack services traefik
# 应看到 REPLICAS 为 1/1

docker service logs traefik_traefik --tail 20
# 应看到 "Configuration loaded from flags."
```

---

**踩坑记录**

**坑 1：Traefik v3 的 swarm provider 与 Docker 29 不兼容**

**现象**：日志持续报错 `client version 1.24 is too old. Minimum supported API version is 1.40`，服务始终 `0/1`。

**原因**：Traefik v3.3.5 的 swarm provider 内部 Docker 客户端使用了旧版 API（1.24），而 Docker 29.x daemon 最低只支持 API 1.40。设置 `DOCKER_API_VERSION` 环境变量无效，因为 Traefik 的 swarm provider 没有使用该变量。

**解决方案**：降级到 Traefik v2.11，v2 的 Docker provider 对 Swarm 支持成熟稳定。

同时注意 v2 和 v3 的命令参数不同：

| 功能 | v3 | v2 |
|---|---|---|
| 启用 Swarm | `--providers.swarm=true` | `--providers.docker.swarmMode=true` |
| 端点 | `--providers.swarm.endpoint` | `--providers.docker.endpoint` |
| 默认不暴露 | `--providers.swarm.exposedByDefault` | `--providers.docker.exposedByDefault` |

**坑 2：静态配置文件与 CLI 参数冲突**

**现象**：同时使用 `--configFile=/etc/traefik/traefik.yml` 和 CLI 参数时，ACME 存储路径用了配置文件里的旧路径，导致 `open /letsencrypt/acme.json: no such file or directory`。

**解决方案**：二选一，不要混用。推荐只用 CLI 参数，去掉 `--configFile` 和 `configs` 挂载。

**坑 3：SCP 上传目录时目标路径不存在**

**现象**：
```
scp: realpath /opt/myapp/traefik/: No such file or directory
scp: upload "...": path canonicalization failed
```

**解决方案**：上传前先在服务器上创建目录：

```bash
ssh root@your-server "mkdir -p /opt/myapp/traefik"
```

**坑 4：host-mode 端口被占用导致 Pending**

**现象**：`docker service ps` 看到 `host-mode port already in use on 1 node`，新任务处于 Pending 状态。

**原因**：滚动更新时旧容器仍在运行占用端口，新容器无法启动。等旧容器退出后会自动恢复正常，不需要手动干预。

---

**部署顺序总结**

```
1. 安装 Docker
2. docker swarm init
3. docker network create --driver overlay --attachable traefik-public
4. 准备 acme.json（touch + chmod 600）
5. docker stack deploy -c stack.yml traefik     ← Traefik 先于应用部署
6. docker stack deploy -c docker-compose.stack.yml <app-stack-name>
```

Traefik 会监听 Docker Swarm 的服务变化，自动根据 `deploy.labels` 中的配置生成路由规则和申请 HTTPS 证书，无需重启。
