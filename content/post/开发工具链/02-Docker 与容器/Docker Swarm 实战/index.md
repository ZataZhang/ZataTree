---
title: "Docker Swarm 实战（一）：核心概念与集群管理"
description: Docker Swarm 原生集群编排完整指南，涵盖架构、核心概念、节点管理、服务部署与常用运维操作。
date: 2026-04-12T10:00:00+08:00
image: images/index/index.png
slug: docker-swarm-guide
categories:
    - 开发工具链
tags:
    - Docker 与容器
    - Docker
draft: false
---

## 系列文章

| 篇 | 主题 |
|---|---|
| 一（本篇） | 核心概念与集群管理 |
| [二](../docker-swarm-traefik-deployment/) | Traefik 反向代理部署 |

---

## 为什么选择 Docker Swarm

在容器编排领域，Kubernetes 是行业标准，但对于中小规模项目，Docker Swarm 往往是更务实的选择：

- **零额外依赖**：Docker 自带，无需单独安装
- **学习曲线平缓**：`docker-compose.yml` 稍加改造就能用于 Swarm
- **运维成本低**：单机也能跑，按需扩展到多节点
- **足够稳定**：生产可用，社区成熟

如果你的业务规模不需要 K8s 的复杂调度能力，Swarm 是一个省心的选择。

---

## 核心概念

### Node（节点）

Swarm 集群由多个 Docker 主机（Node）组成，分两类角色：

| 角色 | 职责 |
|---|---|
| **Manager** | 维护集群状态、调度任务、处理 API 请求 |
| **Worker** | 执行容器任务，不参与调度决策 |

- Manager 节点同时也承担 Worker 职责（可配置为纯 Manager）
- 生产环境建议部署奇数个 Manager（3 或 5），保证 Raft 共识算法的容错能力
- 单机部署时，本机同时充当 Manager 和 Worker

### Service（服务）

Service 是 Swarm 的基本部署单元，描述"运行什么、运行几份、如何更新"：

```
Service
├── replicated mode：固定副本数，调度器负责在节点间分配
└── global mode：每个节点各运行一个副本（适合日志收集、监控 agent 等）
```

### Task（任务）

Task 是 Service 的最小执行单元，对应一个运行中的容器实例。调度器将 Task 分配到合适的节点上执行。

### Stack（栈）

Stack 是一组相关 Service 的集合，通过 `docker-compose.yml`（需加 `deploy` 字段）定义，用 `docker stack deploy` 一键部署。

### Overlay Network（覆盖网络）

Swarm 使用 overlay 网络让不同节点上的容器互相通信，底层通过 VXLAN 封装实现跨主机网络。

---

## 安装与初始化

### 安装 Docker

```bash
curl -fsSL https://get.docker.com | sh
```

国内网络可通过 DaoCloud 镜像安装：

```bash
curl -sSL https://get.daocloud.io/docker | sh
```

### 初始化 Swarm

```bash
# 初始化，指定对外通告的 IP（通常为服务器公网 IP 或内网 IP）
docker swarm init --advertise-addr <IP>
```

初始化成功后会输出加入集群的命令，记录备用：

```
To add a worker to this swarm, run the following command:
    docker swarm join --token SWMTKN-1-xxx <IP>:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

### 查看集群状态

```bash
docker node ls
```

输出示例：

```
ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123 *                      node-1     Ready     Active         Leader
def456                        node-2     Ready     Active         
ghi789                        node-3     Ready     Active         Reachable
```

---

## 节点管理

### 添加节点

```bash
# 在 Manager 节点上获取加入 token
docker swarm join-token worker    # 获取 worker 加入命令
docker swarm join-token manager   # 获取 manager 加入命令

# 在目标机器上执行输出的 join 命令
docker swarm join --token <TOKEN> <MANAGER_IP>:2377
```

### 更改节点角色

```bash
# Worker 升级为 Manager
docker node promote <NODE_ID>

# Manager 降级为 Worker
docker node demote <NODE_ID>
```

### 节点维护与下线

```bash
# 将节点置为维护模式（停止接受新任务，现有任务迁移到其他节点）
docker node update --availability drain <NODE_ID>

# 恢复为可调度状态
docker node update --availability active <NODE_ID>

# 从集群中删除节点（需先 drain）
docker node rm <NODE_ID>
```

---

## 服务管理

### 创建服务

```bash
# 基本格式
docker service create \
  --name my-web \
  --replicas 3 \
  --publish published=8080,target=80 \
  nginx:alpine
```

常用参数：

| 参数 | 说明 |
|---|---|
| `--replicas N` | 副本数量 |
| `--publish` | 端口映射 |
| `--network` | 加入指定网络 |
| `--env KEY=VAL` | 环境变量 |
| `--constraint` | 调度约束（如 `node.role==manager`） |
| `--limit-cpu / --limit-memory` | 资源限制 |
| `--restart-condition` | 重启策略 |
| `--update-parallelism` | 滚动更新并发数 |

### 查看服务

```bash
docker service ls                        # 列出所有服务
docker service ps <SERVICE>             # 查看服务的任务列表（各副本状态）
docker service inspect <SERVICE>        # 查看服务详细配置
docker service inspect --pretty <SERVICE>  # 易读格式
```

### 扩缩容

```bash
docker service scale my-web=5          # 将副本数调整为 5
docker service scale svc1=3 svc2=2    # 同时调整多个服务
```

### 滚动更新

```bash
# 更新镜像版本
docker service update --image nginx:1.25 my-web

# 控制更新节奏
docker service update \
  --update-parallelism 2 \     # 每批更新 2 个副本
  --update-delay 10s \         # 每批之间等待 10 秒
  --image nginx:1.25 my-web
```

更新失败时回滚：

```bash
docker service rollback my-web
```

### 删除服务

```bash
docker service rm my-web
```

---

## Stack 部署

Stack 是推荐的生产部署方式，用 Compose 文件统一描述整个应用栈。

### Compose 文件关键差异

与普通 `docker-compose.yml` 相比，Stack 文件需要增加 `deploy` 字段，并且**不支持** `build`（镜像必须提前构建好）：

```yaml
services:
  api:
    image: myregistry/api:latest
    networks:
      - app-net
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.api.rule=Host(`api.example.com`)"

networks:
  app-net:
    driver: overlay
```

### 部署与更新

```bash
# 部署（stack 不存在则创建，已存在则更新）
docker stack deploy -c docker-compose.stack.yml myapp

# 带环境变量
ENV_VAR=value docker stack deploy -c stack.yml myapp

# 查看 stack 中的服务
docker stack services myapp

# 查看 stack 中所有任务
docker stack ps myapp

# 删除整个 stack
docker stack rm myapp
```

---

## 网络管理

### 创建 overlay 网络

```bash
# 基本创建
docker network create --driver overlay my-network

# 可附加（允许独立容器加入，非 Swarm service 也能连接）
docker network create --driver overlay --attachable my-network
```

### 网络模式对比

| 模式 | 适用场景 |
|---|---|
| `overlay` | Swarm service 之间的跨节点通信（默认） |
| `host` | 直接使用宿主机网络栈，性能最高，但端口冲突风险 |
| `ingress` | Swarm 内置的负载均衡网络（自动创建，无需手动管理） |

### 端口发布模式

```yaml
ports:
  - target: 80
    published: 80
    protocol: tcp
    mode: host      # host 模式：直接绑定到宿主机，绕过 Swarm 的 ingress 负载均衡
```

```yaml
ports:
  - "80:80"         # ingress 模式（默认）：通过 Swarm routing mesh 转发，任意节点均可接收流量
```

---

## 配置与密钥管理

### Secret（敏感数据）

```bash
# 创建 secret
echo "my_db_password" | docker secret create db_password -
docker secret create ssl_cert ./cert.pem

# 在 service 中使用
docker service create \
  --name db \
  --secret db_password \
  postgres:15
```

在 Compose 文件中：

```yaml
services:
  db:
    image: postgres:15
    secrets:
      - db_password

secrets:
  db_password:
    external: true   # 使用已存在的 secret
```

Secret 会以文件形式挂载到容器的 `/run/secrets/<secret_name>`。

### Config（非敏感配置）

```bash
# 创建 config
docker config create nginx_conf ./nginx.conf

# 在 service 中使用
docker service create \
  --name web \
  --config source=nginx_conf,target=/etc/nginx/nginx.conf \
  nginx
```

---

## 常用运维操作

### 查看服务日志

```bash
docker service logs <SERVICE>              # 输出所有副本的日志
docker service logs -f <SERVICE>           # 实时跟踪
docker service logs --tail 50 <SERVICE>    # 最近 50 行
```

### 强制重新部署（不改配置）

```bash
docker service update --force <SERVICE>
```

### 查看任务失败原因

```bash
docker service ps --no-trunc <SERVICE>
```

`--no-trunc` 会显示完整的错误信息，方便排查启动失败的原因。

### 清理已停止的任务

Swarm 默认保留已完成的任务记录，可通过以下方式清理：

```bash
docker system prune           # 清理未使用的容器、网络、镜像
docker system prune --volumes # 同时清理 volume
```

---

## 常见问题

**Q：`docker stack deploy` 报错 `network not found`？**

A：`external: true` 的网络必须在 deploy 之前手动创建，否则 Swarm 不会自动创建它：

```bash
docker network create --driver overlay --attachable traefik-public
```

**Q：服务副本一直是 `0/1`，`docker service ps` 显示 `pending`？**

A：常见原因：
- 节点资源不足（CPU/内存超出限制）
- 调度约束无法满足（如 `node.role==manager` 但 manager 不可用）
- host-mode 端口冲突（等旧容器退出自动恢复）
- 镜像拉取失败（检查仓库权限和网络）

**Q：滚动更新后服务异常，如何回滚？**

```bash
docker service rollback <SERVICE>
```

**Q：单机 Swarm 和 docker compose up 有什么区别？**

| 特性 | docker compose | docker stack (Swarm) |
|---|---|---|
| 高可用 | 无 | 副本自动重启、跨节点调度 |
| 滚动更新 | 无 | 内置，支持回滚 |
| Secret 管理 | 无 | 原生支持 |
| 扩缩容 | 手动 | `docker service scale` |
| 适用场景 | 本地开发 | 生产部署 |

---

## 下一步

- [Docker Swarm 实战（二）：Traefik 反向代理部署](../docker-swarm-traefik-deployment/) — 在 Swarm 上部署 Traefik v2，实现 HTTPS 自动证书和路由转发
