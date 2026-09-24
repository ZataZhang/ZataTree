---
title: Woodpecker CI 使用教程
description: "从概念、架构、部署到流水线 YAML，系统了解轻量级开源 CI/CD 工具 Woodpecker CI。"
date: 2026-06-07T10:00:00+08:00
image: images/index/index.png
categories:
    - Engineering
tags:
    - DevOps
    - CI/CD
---

Woodpecker CI 是一个开源、轻量、容器优先的 CI/CD 工具。它的定位很清晰：代码仓库发生 push、pull request、tag、手动触发等事件后，Woodpecker 读取仓库里的 YAML 配置，然后把每个步骤放进容器里执行。

如果你已经熟悉 GitHub Actions，可以把 Woodpecker 理解成一个更偏自托管、更轻量、更贴近 Drone CI 风格的流水线系统。它不绑定某一家代码托管平台，可以接 GitHub、GitLab、Gitea、Forgejo、Bitbucket 等 forge，适合团队希望把 CI/CD 控制权放在自己服务器上的场景。

---

## 一、如何安装 Woodpecker CI

第一次了解 Woodpecker CI，建议先用 Docker Compose 跑一个最小可用版本。先跑起来，再理解 pipeline、workflow、step 这些概念会更直观。

下面以接入 GitHub 为例。如果你使用 Gitea、Forgejo 或 GitLab，整体步骤类似，只是 forge 相关环境变量不同。

这篇教程优先写 Docker Compose，是因为它最适合单台服务器和第一次试用。如果你已经有 Kubernetes 集群，应该优先看本节后面的 Helm 安装方式，Helm Chart 也是官方提供的部署方式。

### 1. 安装前准备

你需要准备：

- 一台已经安装 Docker 和 Docker Compose 的服务器。
- 一个能访问 Woodpecker Web UI 的地址，例如 `https://ci.example.com`。
- 一个代码平台账号，例如 GitHub、GitLab、Gitea、Forgejo。
- 目标仓库的管理员权限，因为 Woodpecker 需要创建 webhook。
- 一个 Server 和 Agent 共享的随机密钥。

生成共享密钥：

```bash
openssl rand -hex 32
```

### 2. 创建 GitHub OAuth App

如果接 GitHub，需要在 GitHub 创建 OAuth App，不是 GitHub App。

路径：

```text
GitHub -> Settings -> Developer settings -> OAuth Apps -> New OAuth App
```

关键配置：

```text
Homepage URL: https://ci.example.com
Authorization callback URL: https://ci.example.com/authorize
```

创建完成后，记录：

- `Client ID`
- `Client Secret`

它们会分别填到 `WOODPECKER_GITHUB_CLIENT` 和 `WOODPECKER_GITHUB_SECRET`。

### 3. 编写 docker-compose.yaml

创建一个目录，例如：

```bash
mkdir -p /opt/woodpecker
cd /opt/woodpecker
```

写入 `docker-compose.yaml`：

```yaml
services:
  woodpecker-server:
    image: woodpeckerci/woodpecker-server:v3
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - woodpecker-server-data:/var/lib/woodpecker/
    environment:
      - WOODPECKER_OPEN=true
      - WOODPECKER_HOST=${WOODPECKER_HOST}
      - WOODPECKER_GITHUB=true
      - WOODPECKER_GITHUB_CLIENT=${WOODPECKER_GITHUB_CLIENT}
      - WOODPECKER_GITHUB_SECRET=${WOODPECKER_GITHUB_SECRET}
      - WOODPECKER_AGENT_SECRET=${WOODPECKER_AGENT_SECRET}

  woodpecker-agent:
    image: woodpeckerci/woodpecker-agent:v3
    command: agent
    restart: always
    depends_on:
      - woodpecker-server
    volumes:
      - woodpecker-agent-config:/etc/woodpecker
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WOODPECKER_SERVER=woodpecker-server:9000
      - WOODPECKER_AGENT_SECRET=${WOODPECKER_AGENT_SECRET}

volumes:
  woodpecker-server-data:
  woodpecker-agent-config:
```

### 4. 编写 .env

同目录创建 `.env`：

```bash
WOODPECKER_HOST=https://ci.example.com
WOODPECKER_GITHUB_CLIENT=你的 GitHub OAuth App Client ID
WOODPECKER_GITHUB_SECRET=你的 GitHub OAuth App Client Secret
WOODPECKER_AGENT_SECRET=用 openssl rand -hex 32 生成的随机字符串
```

这里最容易写错的是 `WOODPECKER_HOST`。它必须是浏览器和代码平台 webhook 都能访问到的 Woodpecker 外部地址，不要写成容器内地址，也不要在末尾加 `/`。

### 5. 启动服务

```bash
docker compose up -d
docker compose ps
```

查看日志：

```bash
docker compose logs -f woodpecker-server
docker compose logs -f woodpecker-agent
```

如果一切正常，打开：

```text
https://ci.example.com
```

使用 GitHub 登录，然后在 Woodpecker UI 里启用你的仓库。

### 6. 让仓库真正跑起来

Woodpecker 安装完成后，还需要在仓库里添加流水线配置。最小示例是：

```text
.woodpecker/build.yaml
```

```yaml
when:
  - event: push
    branch: main

steps:
  - name: hello
    image: alpine
    commands:
      - echo "hello woodpecker"
```

提交并 push 到 `main` 后，Woodpecker 应该会收到 webhook 并开始执行 pipeline。

### 7. 已有 Dokploy / Traefik：不需要 Nginx

如果你已经习惯用 Dokploy 配合 Traefik 快速部署应用，Woodpecker 并不会变难。Woodpecker 不自带 Traefik，但它可以像普通 Web 应用一样接入现有 Traefik 网关。

如果服务器还没有安装 Docker 和 Traefik，可以先按这篇文章准备公共入口层：[Docker 和 Traefik 一键安装脚本]({{< relref "/post/Engineering/DevOps/Docker-Traefik一键安装脚本/index.md" >}})。

核心思路是：

```text
https://ci.example.com
        |
        v
Traefik / Dokploy 网关
        |
        v
woodpecker-server:8000
```

Agent 不需要从公网访问 `https://ci.example.com`。如果 `woodpecker-server` 和 `woodpecker-agent` 在同一个 Docker Compose 项目里，Agent 直接用内部地址连接即可：

```text
WOODPECKER_SERVER=woodpecker-server:9000
```

也就是说，Traefik 只负责 Web UI、OAuth 回调、webhook 入口；Agent 和 Server 的 gRPC 通信可以留在 Docker 内部网络里。

如果由 Dokploy UI 管理域名，通常只需要：

1. 用 Dokploy 创建一个 Docker Compose 应用。
2. 填入 Woodpecker 的 compose 配置。
3. 给 `woodpecker-server` 配域名，例如 `ci.example.com`。
4. 让 Dokploy 把外部 HTTPS 转发到容器内部端口 `8000`。
5. `.env` 中保持 `WOODPECKER_HOST=https://ci.example.com`。

如果你直接写 Traefik labels，可以把 `woodpecker-server` 改成类似下面这样。网络名、证书 resolver、entrypoint 要替换成你现有 Traefik 的配置：

```yaml
services:
  woodpecker-server:
    image: woodpeckerci/woodpecker-server:v3
    restart: always
    expose:
      - "8000"
    volumes:
      - woodpecker-server-data:/var/lib/woodpecker/
    environment:
      - WOODPECKER_OPEN=true
      - WOODPECKER_HOST=${WOODPECKER_HOST}
      - WOODPECKER_GITHUB=true
      - WOODPECKER_GITHUB_CLIENT=${WOODPECKER_GITHUB_CLIENT}
      - WOODPECKER_GITHUB_SECRET=${WOODPECKER_GITHUB_SECRET}
      - WOODPECKER_AGENT_SECRET=${WOODPECKER_AGENT_SECRET}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.woodpecker.rule=Host(`ci.example.com`)"
      - "traefik.http.routers.woodpecker.entrypoints=websecure"
      - "traefik.http.routers.woodpecker.tls.certresolver=letsencrypt"
      - "traefik.http.services.woodpecker.loadbalancer.server.port=8000"
    networks:
      - traefik-public
      - default

  woodpecker-agent:
    image: woodpeckerci/woodpecker-agent:v3
    command: agent
    restart: always
    depends_on:
      - woodpecker-server
    volumes:
      - woodpecker-agent-config:/etc/woodpecker
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WOODPECKER_SERVER=woodpecker-server:9000
      - WOODPECKER_AGENT_SECRET=${WOODPECKER_AGENT_SECRET}

volumes:
  woodpecker-server-data:
  woodpecker-agent-config:

networks:
  traefik-public:
    external: true
```

注意这里没有暴露：

```yaml
ports:
  - "8000:8000"
```

因为公网入口已经由 Traefik 接管。只有在没有 Traefik、Nginx、Caddy、Dokploy 这类网关时，才需要把端口直接映射出来。

### 8. Kubernetes 环境：用 Helm 安装

如果你的基础设施已经是 Kubernetes，不需要用上面的 Docker Compose。Woodpecker 官方提供了 Helm Chart，可以直接安装：

```bash
helm install woodpecker oci://ghcr.io/woodpecker-ci/helm/woodpecker --version <VERSION>
```

实际使用时建议带上 namespace：

```bash
helm install woodpecker oci://ghcr.io/woodpecker-ci/helm/woodpecker \
  --version <VERSION> \
  --namespace woodpecker \
  --create-namespace
```

这里的 `<VERSION>` 是 Helm Chart 版本，不一定等于 Woodpecker Server 的应用版本。安装前可以到官方 Helm 仓库或 release 页面确认当前 chart 版本。

生产环境通常会准备一个 `values.yaml`，把域名、OAuth、持久化、Ingress 等配置写进去。例如：

```yaml
server:
  env:
    WOODPECKER_OPEN: "true"
    WOODPECKER_HOST: "https://ci.example.com"
    WOODPECKER_GITHUB: "true"
    WOODPECKER_GITHUB_CLIENT: "你的 GitHub OAuth App Client ID"
    WOODPECKER_GITHUB_SECRET: "你的 GitHub OAuth App Client Secret"
    WOODPECKER_AGENT_SECRET: "用 openssl rand -hex 32 生成的随机字符串"

  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - host: ci.example.com
        paths:
          - path: /
            pathType: Prefix

agent:
  enabled: true
```

然后执行：

```bash
helm upgrade --install woodpecker oci://ghcr.io/woodpecker-ci/helm/woodpecker \
  --version <VERSION> \
  --namespace woodpecker \
  --create-namespace \
  -f values.yaml
```

选择 Docker Compose 还是 Helm，可以这样判断：

| 场景 | 推荐方式 |
|---|---|
| 单台云服务器、先学习、先跑通 | Docker Compose |
| 已经用 Dokploy / Traefik 管理应用域名 | Docker Compose + 现有 Traefik |
| 已经有 Kubernetes 集群 | Helm |
| 需要 Ingress、StorageClass、PodMonitor、RBAC 等 K8s 能力 | Helm |
| 不熟悉 Kubernetes，只想给个人项目跑 CI | Docker Compose |

Helm 不是更高级就一定更适合。它适合已经有 K8s 运维体系的团队；如果只是个人服务器或小团队单机部署，Docker Compose 反而更容易维护。

### 9. 中国服务器注意事项

如果服务器在中国大陆，安装本身没有特殊问题，但镜像和依赖源要提前规划：

- 把 `woodpeckerci/woodpecker-server:v3`、`woodpeckerci/woodpecker-agent:v3` 同步到国内镜像仓库。
- 如果使用 Helm，`oci://ghcr.io/woodpecker-ci/helm/woodpecker` 也可能受 GHCR 网络影响，必要时提前准备代理或内部镜像/制品仓库。
- CI 里用到的 `node`、`python`、`golang` 等基础镜像也尽量走私有仓库。
- npm、pip、Go modules 配置国内源。
- 如果 GitHub webhook 到国内服务器不稳定，更推荐自建 Gitea、Forgejo 或 GitLab。

---

## 二、为什么关注 Woodpecker CI

Woodpecker CI 值得了解的原因主要有几个：

1. **轻量**：核心组件少，部署成本比很多完整 DevOps 平台低。
2. **容器化**：每个 step 都运行在指定镜像里，构建环境可复现。
3. **自托管友好**：CI 服务、构建 agent、数据都可以放在自己的机器上。
4. **YAML 简洁**：常见的 build、test、deploy 流水线写法很直观。
5. **多代码平台支持**：不是只能依赖 GitHub Actions 这一类平台内置 CI。

它比较适合下面这些场景：

- 使用 Gitea、Forgejo、GitLab 自建代码平台，希望配一套轻量 CI。
- 项目需要访问内网环境，不方便把构建任务放到公有云 CI。
- 小团队想要一个足够简单、可维护、可迁移的 CI/CD 系统。
- 已经用 Docker 管理构建、测试和部署环境。

不太适合的场景：

- 团队已经深度依赖 GitHub Actions Marketplace 或 GitLab CI 生态。
- 需要复杂的企业级权限、审计、合规工作流。
- 不希望维护任何 CI 基础设施。

---

## 三、核心架构

Woodpecker CI 主要由两个组件组成：

### 1. Server

Server 负责 Web UI、用户登录、仓库管理、webhook 接收、流水线调度、状态回写等事情。

代码平台有新事件时，例如 push 到 `main`，平台会通过 webhook 通知 Woodpecker Server。Server 找到对应仓库的流水线配置，然后创建 pipeline。

### 2. Agent

Agent 负责真正执行流水线任务。它从 Server 接收任务，然后启动容器运行 step。

如果使用 Docker 后端，Agent 通常需要访问宿主机 Docker daemon，所以部署时经常会看到：

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

这意味着 Agent 可以控制宿主机 Docker，权限很高。生产环境里要认真限制谁能修改 CI 配置、谁能拿到 secret、哪些仓库可以运行构建。

### 3. 执行流程

一个典型流程是：

1. 开发者 push 代码到仓库。
2. Git 平台通过 webhook 通知 Woodpecker。
3. Woodpecker Server 拉取仓库配置。
4. Server 创建 pipeline，并分配给 Agent。
5. Agent clone 代码，按 YAML 定义依次运行 step。
6. 每个 step 在独立容器里执行命令。
7. Server 把成功或失败状态回写到代码平台。

---

## 四、基本概念

### 1. Pipeline

Pipeline 是一次完整的 CI/CD 执行，例如某次 push 触发的一轮构建。

### 2. Workflow

一个 pipeline 至少包含一个 workflow。workflow 是一组共享同一个 workspace 的 step。最简单的配置可以写在 `.woodpecker.yaml`，也可以把多个 workflow 拆成 `.woodpecker/` 目录下的多个 YAML 文件。

例如：

```text
.woodpecker/
  lint.yaml
  test.yaml
  deploy.yaml
```

Woodpecker 会把这些文件识别成多个 workflow。多个 workflow 可以并行执行，也可以通过 `depends_on` 建立依赖。

### 3. Step

Step 是 workflow 里的一个执行单元。每个 step 指定一个镜像，然后在容器里运行命令。

```yaml
steps:
  - name: test
    image: node:22
    commands:
      - npm ci
      - npm test
```

### 4. Plugin

Plugin 本质上也是容器镜像，只是它把常见任务封装好了，例如上传文件、构建镜像、发送通知等。使用 plugin 时一般通过 `settings` 传参。

```yaml
steps:
  - name: upload
    image: woodpeckerci/plugin-s3
    settings:
      bucket: my-bucket
      source: public/**/*
      target: /site/
      secret_key:
        from_secret: aws_secret_key
```

## 五、创建第一条流水线

在项目根目录创建：

```text
.woodpecker/build.yaml
```

写入：

```yaml
when:
  - event: push
    branch: main

steps:
  - name: install
    image: node:22
    commands:
      - npm ci

  - name: test
    image: node:22
    commands:
      - npm test

  - name: build
    image: node:22
    commands:
      - npm run build
```

这条流水线的含义：

- 只有 push 到 `main` 分支才运行。
- 使用 `node:22` 镜像作为执行环境。
- 依次执行安装依赖、测试、构建。
- 任意命令返回非 0 状态码，后续 step 默认不会继续执行，workflow 标记失败。

如果项目是 Python：

```yaml
when:
  - event: [push, pull_request]

steps:
  - name: test
    image: python:3.12
    commands:
      - pip install -r requirements.txt
      - pytest
```

如果项目是 Go：

```yaml
when:
  - event: [push, pull_request]

steps:
  - name: test
    image: golang:1.23
    commands:
      - go test ./...
```

---

## 六、条件执行

Woodpecker 使用 `when` 控制 workflow 或 step 在什么情况下执行。

### 1. 只在 main 分支执行

```yaml
when:
  - event: push
    branch: main
```

### 2. tag 时发布

```yaml
steps:
  - name: release
    image: alpine
    commands:
      - echo "release version $CI_COMMIT_TAG"
    when:
      - event: tag
```

### 3. pull request 只跑测试，不发布

```yaml
steps:
  - name: test
    image: node:22
    commands:
      - npm ci
      - npm test

  - name: deploy
    image: alpine
    commands:
      - ./deploy.sh
    when:
      - event: push
        branch: main
```

这个模式很重要：不要在 pull request 事件里暴露部署密钥，尤其是公开仓库。

---

## 七、多个 workflow 的拆分

大型项目不建议把所有事情塞进一个 YAML。可以拆成：

```text
.woodpecker/
  lint.yaml
  test.yaml
  docker.yaml
  deploy.yaml
```

例如 `.woodpecker/lint.yaml`：

```yaml
steps:
  - name: lint
    image: node:22
    commands:
      - npm ci
      - npm run lint
```

`.woodpecker/test.yaml`：

```yaml
steps:
  - name: test
    image: node:22
    commands:
      - npm ci
      - npm test
```

`.woodpecker/deploy.yaml`：

```yaml
depends_on:
  - lint
  - test

when:
  - event: push
    branch: main

steps:
  - name: deploy
    image: alpine
    commands:
      - ./deploy.sh
```

这样做的好处：

- lint 和 test 可以更早反馈。
- 不同 workflow 的状态可以分别回写到代码平台。
- workflow 可以并行跑，提升整体速度。
- deploy 明确依赖 lint 和 test 成功。

---

## 八、Secret 管理

CI/CD 经常要用密钥，例如 Docker registry 密码、SSH 私钥、云服务 token。不要把这些值写进仓库 YAML。

Woodpecker 的 secret 可以通过 UI 或 CLI 设置，然后在 YAML 中用 `from_secret` 引用：

```yaml
steps:
  - name: deploy
    image: alpine
    environment:
      SSH_KEY:
        from_secret: production_ssh_key
    commands:
      - mkdir -p ~/.ssh
      - echo "$SSH_KEY" > ~/.ssh/id_rsa
      - chmod 600 ~/.ssh/id_rsa
      - ./deploy.sh
```

也可以传给 plugin：

```yaml
steps:
  - name: publish-image
    image: woodpeckerci/plugin-docker-buildx
    settings:
      repo: registry.example.com/my-app
      tags: latest
      username:
        from_secret: registry_username
      password:
        from_secret: registry_password
```

Secret 使用建议：

- 不要在日志里 `echo` secret。
- 不要默认把 secret 暴露给 pull request。
- 公开仓库尤其要警惕来自 fork 的 PR。
- 为生产环境和测试环境使用不同 secret。
- 定期轮换部署密钥。

---

## 九、常见流水线模板

### 1. 前端项目：测试并构建

```yaml
when:
  - event: [push, pull_request]

steps:
  - name: build
    image: node:22
    commands:
      - npm ci
      - npm run lint
      - npm test
      - npm run build
```

### 2. Docker 镜像构建

```yaml
when:
  - event: push
    branch: main

steps:
  - name: docker
    image: woodpeckerci/plugin-docker-buildx
    settings:
      repo: registry.example.com/my-app
      tags:
        - latest
        - ${CI_COMMIT_SHA}
      username:
        from_secret: registry_username
      password:
        from_secret: registry_password
```

### 3. 部署到服务器

```yaml
depends_on:
  - build

when:
  - event: push
    branch: main

steps:
  - name: deploy
    image: alpine:3.20
    environment:
      SSH_KEY:
        from_secret: production_ssh_key
      DEPLOY_HOST:
        from_secret: production_host
    commands:
      - apk add --no-cache openssh-client
      - mkdir -p ~/.ssh
      - echo "$SSH_KEY" > ~/.ssh/id_rsa
      - chmod 600 ~/.ssh/id_rsa
      - ssh -o StrictHostKeyChecking=no "$DEPLOY_HOST" "cd /opt/app && docker compose pull && docker compose up -d"
```

这个例子能跑通，但生产中建议更严谨：

- 不要长期关闭 `StrictHostKeyChecking`。
- 使用最小权限部署用户。
- 服务器端只允许执行必要命令。
- 部署前保留当前版本，方便回滚。

---

## 十、和 GitHub Actions 的区别

| 对比项 | Woodpecker CI | GitHub Actions |
|---|---|---|
| 部署方式 | 主要面向自托管 | GitHub 托管为主，也支持 self-hosted runner |
| 代码平台 | 可接多种 forge | 深度绑定 GitHub |
| 执行模型 | step 基于容器镜像 | action + shell + runner 环境 |
| 配置风格 | 简洁，接近 Drone CI | 功能丰富，语法更庞大 |
| 生态 | 插件生态较小 | Marketplace 很大 |
| 适合场景 | 自建 Git、内网部署、轻量 CI | GitHub 项目、丰富第三方 action、托管 CI |

简单判断：

- 你的代码主要放 GitHub，并且不想维护 CI 服务器：优先 GitHub Actions。
- 你在用 Gitea/Forgejo，或者需要内网自托管：Woodpecker CI 很值得试。
- 你希望 CI 配置尽量贴近容器和 shell：Woodpecker CI 的心智负担较低。

---

## 十一、生产使用建议

### 1. 给 CI 单独准备机器

不要把 Woodpecker Agent 随便放在核心业务机器上。Agent 需要运行不可信代码，尤其在多人协作或开源仓库里，风险很高。

### 2. 限制仓库和用户权限

谁能启用仓库、谁能改 `.woodpecker/` 配置、谁能读取 secret，都要明确。

### 3. 注意 Docker socket 风险

挂载 `/var/run/docker.sock` 等于让 Agent 拥有很高的宿主机控制能力。能不用特权就不用特权，能隔离 agent 就隔离 agent。

### 4. 持久化和备份数据

Server 数据目录里包含用户、仓库、流水线等信息。Docker Compose 部署时要持久化 `/var/lib/woodpecker/`，并做定期备份。

### 5. 使用 HTTPS

`WOODPECKER_HOST` 建议配置成 HTTPS 地址。已有 Dokploy、Traefik、Caddy、Nginx 或云平台网关时，直接复用现有网关即可，不需要为了 Woodpecker 额外改用 Nginx。

### 6. 把流水线当代码审查

`.woodpecker/` 下的 YAML 能决定 CI 机器执行什么命令。它应该像业务代码一样经过 review。

---

## 十二、排查问题的思路

### 1. 仓库没有触发流水线

检查：

- 仓库是否已在 Woodpecker UI 中启用。
- 当前用户是否有仓库 admin 权限。
- 代码平台 webhook 是否创建成功。
- `.woodpecker.yaml` 或 `.woodpecker/*.yaml` 路径是否正确。
- `when` 条件是否把事件过滤掉了。

### 2. Agent 不执行任务

检查：

- `woodpecker-agent` 容器是否在运行。
- `WOODPECKER_SERVER` 是否能访问。
- `WOODPECKER_AGENT_SECRET` 是否和 Server 一致。
- gRPC 端口是否被网络或反向代理挡住。
- Docker socket 是否挂载成功。

### 3. step 找不到文件

检查：

- 文件是否在仓库里。
- 前一个 step 生成的文件是否写在 workspace 内。
- 多 workflow 之间不共享 workspace，只有同一个 workflow 内的 step 共享。

### 4. secret 为空

检查：

- secret 名称是否和 `from_secret` 一致。
- 当前事件是否允许使用该 secret。
- pull request 是否被默认限制访问 secret。
- secret 是否被限制到某些 plugin 或 image。

---

## 十三、总结

Woodpecker CI 的核心价值是：用较少的组件，搭建一套可自托管、容器化、配置直观的 CI/CD 系统。

学习它时可以按这个顺序：

1. 先用 Docker Compose 或 Helm 跑一个最小实例。
2. 在仓库里创建 `.woodpecker/build.yaml`，确认 webhook 能触发 pipeline。
3. 再理解 Server、Agent、Pipeline、Workflow、Step 的关系。
4. 掌握 `steps`、`commands`、`when`、`depends_on`、`from_secret`。
5. 逐步拆分 lint、test、build、deploy 多个 workflow。
6. 最后考虑生产环境的权限、安全、备份和 agent 隔离。

如果你维护的是自建 Git 平台，或者项目部署强依赖内网环境，Woodpecker CI 是一个很务实的选择。

---

## 参考资料

- [Woodpecker CI 官方文档](https://woodpecker-ci.org/docs/intro)
- [Woodpecker CI Docker Compose 安装](https://woodpecker-ci.org/docs/administration/installation/docker-compose)
- [Woodpecker CI Helm Chart 安装](https://woodpecker-ci.org/docs/administration/installation/helm-chart)
- [Woodpecker CI Workflow syntax](https://woodpecker-ci.org/docs/usage/workflow-syntax)
- [Woodpecker CI Workflows](https://woodpecker-ci.org/docs/usage/workflows)
- [Woodpecker CI Secrets](https://woodpecker-ci.org/docs/usage/secrets)
