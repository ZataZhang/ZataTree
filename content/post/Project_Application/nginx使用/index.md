---
title: Nginx
description: Nginx 是一个高性能的开源 Web 服务器和反向代理服务器，以其高效、轻量和强大的并发处理能力而著称。
date: 2025-02-24
slug: Nginx使用 ## 必填，文件夹名
image: image/index/index.png
categories:
    # - DeepLearning
    # - Chart
    # - Python
    # - LLM
    # - Library
    # - PaperReading
    - Platforms_Tools
---


# Nginx 详细使用教程

## 引言：Nginx 核心概念与架构概览

Nginx 作为一款高性能的开源 Web 服务器和反向代理服务器，自 2002 年由 Igor Sysoev 创建以来，其设计初衷便是为了解决著名的“C10K 问题”——即如何在单台服务器上同时处理上万个并发连接 [1]。与传统的 Web 服务器相比，Nginx 的核心优势在于其轻量级、高稳定性、低资源占用和强大的高并发处理能力 [1]。它所扮演的角色远不止于 Web 服务器，还广泛应用于反向代理、负载均衡、HTTP 缓存等关键领域 [1]。Nginx 能够实现如此卓越性能的根本原因，在于其底层架构的独特设计，即异步非阻塞事件驱动模型和主/工作进程模型。

### 1.1 异步非阻塞事件驱动模型深度解析

传统的 Web 服务器通常采用“多进程/多线程阻塞 I/O”模型，即每一个客户端连接都由一个独立的进程或线程来处理 [3]。这种模型在并发连接数较低时工作良好，但当面对海量并发连接时，服务器会因创建和销毁大量进程/线程、以及频繁的上下文切换而导致 CPU 资源被大量消耗在调度而非实际工作上 [3]。

Nginx 彻底颠覆了这种模式。它采用了一种事件驱动模型，其核心思想是“将等待责任交由应用层”，即服务器不会阻塞等待 I/O 操作（例如从网络套接字读取数据或向磁盘写入文件），而是在 I/O 就绪时，通过操作系统提供的事件通知机制（如 Linux 上的 epoll、BSD 上的 kqueue）来被唤醒并处理 [3]。这意味着 Nginx 的少数几个工作进程（Worker Process）就能够高效地处理成千上万个并发连接。其高性能的本质并非源于单个进程的超高计算能力，而是其架构从根本上避免了传统模型在高并发下必然出现的瓶颈，从而在有限的系统资源下实现了高度的并行处理 [3]。

### 1.2 主/工作进程（Master/Worker）架构模型

Nginx 的运行模型由一个主进程（Master Process）和多个工作进程（Worker Process）组成 [4]。主进程的主要职责是管理工作进程、读取和解析配置文件、处理外部信号（如 reload、stop）以及进行无停机升级 [4]。它本身不直接处理任何网络请求，而是作为整个 Nginx 服务的“指挥中心”存在 [4]。

工作进程则是 Nginx 的“执行者”，每个工作进程都是独立运行的，负责处理来自客户端的所有连接和请求 [4]。由于工作进程之间相互独立，它们在处理请求时无需依赖复杂的加锁机制，这不仅减少了锁带来的开销，也极大地简化了编程和问题排查 [5]。当一个工作进程因某个请求而崩溃时，并不会影响到其他工作进程的正常运行，主进程能够迅速感知到异常并拉起一个新的工作进程来顶替 [5]。这种优雅的进程管理模式不仅提升了服务的稳定性和容错能力，也使得 **无中断配置重载**（`nginx -s reload`）和 **平滑升级** 成为可能，极大地保障了线上服务的可用性 [5]。

## 第一部分：Nginx 的安装与基础管理

本节将提供在不同主流操作系统上部署 Nginx 的详细指南，并介绍其基础管理命令。

### 2.1 基于包管理器的快速部署

对于大多数 Linux 发行版，使用其自带的包管理器是安装 Nginx 最便捷的方式。

**在 Ubuntu/Debian 上：**
首先，更新本地的软件包索引以确保获取最新的软件列表，然后通过 `apt` 命令安装 Nginx [8]。
```bash
sudo apt update
sudo apt install nginx
```
安装完成后，如果服务器启用了防火墙（如 `ufw`），需要允许 HTTP 和 HTTPS 流量通过。Nginx 在安装时会注册相应的防火墙配置文件，可以使用 `sudo ufw allow 'Nginx Full'` 来同时开启 80 和 443 端口 [8]。

**在 CentOS/RHEL 上：**
Nginx 在 CentOS 的默认仓库中可能不是最新版本，因此通常建议先添加 EPEL（Extra Packages for Enterprise Linux）软件仓库 [9]。
```bash
sudo yum install epel-release
sudo yum install nginx
```
对于使用了 `firewalld` 的系统，需要手动添加 HTTP/HTTPS 服务的永久规则并重新加载防火墙 [10]。

### 2.2 从源码编译安装：定制化与模块化

源码编译是另一种常见的安装方式，它提供了高度的灵活性和可定制性，能够根据具体需求选择和编译特定的功能模块 [9]。

在编译前，需要安装一系列依赖库。Nginx 是用 C 语言开发的，因此需要 `gcc` 编译环境 [9]。此外，一些核心功能也依赖于外部库：
*   **PCRE (Perl Compatible Regular Expressions)**：Nginx 的 http 模块使用 PCRE 库来解析正则表达式，例如在 `location` 匹配和 `rewrite` 规则中 [9]。
*   **zlib**：用于支持 HTTP 数据包的 Gzip 压缩功能 [9]。
*   **OpenSSL**：Nginx 支持 https 协议，因此需要 OpenSSL 库来提供加密算法和 SSL 协议支持 [9]。

在 CentOS 下，可以使用 `yum` 命令一次性安装所有依赖 [9]：
```bash
sudo yum install -y gcc pcre pcre-devel zlib zlib-devel openssl openssl-devel
```
在 Ubuntu 下，则使用 `apt` [11]。

安装依赖后，可以从 Nginx 官网下载源码包，然后进行配置、编译和安装 [9]。在 `./configure` 阶段，可以根据需要添加或删除模块。例如，要启用 HTTPS 支持，必须在配置参数中包含 `--with-http_ssl_module` [11]。如果编译时缺少该模块，即使在配置文件中正确设置了 HTTPS，Nginx 在启动时也会报错 `https protocol requires SSL support` [12]。这揭示了一个重要的事实：仅仅修改配置文件是不够的，理解 Nginx 的模块化设计及其编译依赖关系是解决许多深层次问题的关键 [11]。

### 2.3 Nginx 服务基础操作与管理

Nginx 服务可以通过多种方式进行管理。

**使用 systemctl：** 这是现代 Linux 系统管理服务的主流方式。
*   **启动：** `sudo systemctl start nginx` [8]
*   **停止：** `sudo systemctl stop nginx` [8]
*   **重启：** `sudo systemctl restart nginx` [8]
*   **重载：** `sudo systemctl reload nginx`，此命令会在不中断现有连接的情况下，重新加载配置文件并使之生效 [8]。

**使用 Nginx 自身命令：**
*   `nginx -s stop`：快速停止服务 [14]。
*   `nginx -s reload`：重载配置文件 [7]。

在进行任何服务重载或重启之前，务必使用 `nginx -t` 命令来测试配置文件的语法正确性。该命令不仅会检查语法，还会尝试打开配置文件中引用到的文件 [7]。这是避免因配置错误导致服务中断的关键步骤。

## 第二部分：精通 Nginx 配置文件（nginx.conf）

Nginx 的核心在于其配置文件 `nginx.conf`，它决定了 Nginx 的所有行为。该文件采用 Nginx 自定的语法，以 `#` 声明单行注释，每条指令以 `;` 结尾 [17]。

### 3.1 配置文件层级结构深度解析

`nginx.conf` 的结构是分层嵌套的，主要分为以下几个区块 [17]：

*   **main（全局块）：** 位于配置文件的最外层，用于设置影响 Nginx 服务器整体运行的指令，例如定义运行 Nginx 的用户和用户组（`user`），以及工作进程数（`worker_processes`）[18]。
*   **events：** 此区块的指令主要影响 Nginx 服务器与用户的网络连接，例如设置每个工作进程可以支持的最大连接数（`worker_connections`）和选择事件驱动模型（`use epoll`）[18]。
*   **http：** 用于配置 HTTP 协议相关的指令，例如设定 MIME 类型、日志格式、文件编码以及启用 Gzip 压缩等 [19]。`http` 块内部可以包含多个 `server` 块。
*   **server：** 用于定义一个虚拟主机，它可以监听特定的端口和域名，处理相应的 HTTP 请求 [17]。`http` 块中至少需要定义一个 `server` 块才能处理请求 [17]。
*   **location：** `server` 块中的核心指令，用于根据请求的 URI 对请求进行路由处理 [17]。一个 `server` 块中可以包含多个 `location` 块 [17]。

### 3.2 location 匹配规则与优先级

`location` 指令是 Nginx 配置的精髓，它负责根据请求 URI 来决定如何处理请求。Nginx 的 `location` 匹配遵循一套严格的优先级规则，这对于避免配置冲突至关重要。理解这套规则，能够将配置从简单的指令堆砌提升为一种精巧的“路由艺术” [19]。

Nginx 优先选择精确匹配，其次是前缀匹配，最后是正则表达式匹配。不同前缀的匹配规则和优先级如下：

| 匹配前缀 | 匹配规则 | 优先级 | 典型应用场景 |
| :--- | :--- | :--- | :--- |
| `=` | 精确匹配。如果 URI 严格匹配，则停止搜索。 | 1 | 快速处理根路径（`/`）的请求，例如 `location = /`。 |
| `^~` | 普通字符串前缀匹配。如果匹配成功，则停止搜索。 | 2 | 强制匹配特定目录，例如 `location ^~ /images/`，以避免被优先级更低的正则匹配覆盖。 |
| `~` | 区分大小写的正则表达式匹配。 | 3 | 处理特定的文件类型或包含特定模式的 URI。 |
| `~*` | 不区分大小写的正则表达式匹配。 | 4 | 匹配文件扩展名，例如 `location ~* \.(jpg |
| 无前缀 | 普通字符串前缀匹配。 | 5 | 默认匹配规则，例如 `location /documents/`，但会继续查找更精确的匹配。 |
| `/` | 通用匹配。任何请求都会匹配到该规则，作为最后的“捕获”规则。 | 6 | 通常用于将所有未被其他规则匹配到的请求转发给后端应用服务器。 |

需要注意的是，`location` 优先级是初学者最容易犯错的地方。例如，一个看似合理的正则匹配规则（`location ~ \.html$`）可能会被一个优先级更高的普通匹配规则（`location ^~ /documents/`）覆盖，导致期望的配置无法生效 [22]。而 `^~` 的引入正是为了提供这种强制停止匹配的能力，确保某些路径（如静态资源路径）能够被确定性地处理 [19]。

### 3.3 Nginx 内置变量与自定义变量

Nginx 提供了丰富的内置变量，可以用来获取和操作请求、响应、服务器环境等信息 [14]。这些变量以 `$` 符号开头。

| 变量名 | 描述 | 应用示例 |
| :--- | :--- | :--- |
| `$request_uri` | 包含请求参数的原始 URI，如 "/foo/bar.php?arg=baz" | `return 200 '$request_uri';` |
| `$uri` | 不带请求参数的当前 URI，如 "/foo/bar.html" | `return 200 '$uri';` |
| `$remote_addr` | 客户端的 IP 地址 | `proxy_set_header X-Real-IP $remote_addr;` |
| `$remote_port` | 客户端的端口号 | `return 200 '$remote_port';` |
| `$server_name` | 服务器的名称，取决于 `server{}` 模块中配置的 `server_name` | `proxy_set_header Host $server_name;` |
| `$server_addr` | 服务器的 IP 地址 | `return 200 '$server_addr';` |
| `$server_port` | 请求到达服务器的端口号 | `return 200 '$server_port';` |
| `$request_method` | 客户端请求的动作，通常为 GET 或 POST | `if ($request_method = POST) {... }` |
| `$host` | 请求头中的 Host 字段 | `proxy_set_header Host $host;` |

除了内置变量，Nginx 也支持使用 `set` 指令来自定义变量，例如 `set $port_type 8x;` [17]。需要注意的是，`set` 指令不能用于给 Nginx 的内置变量赋值 [17]。

## 第三部分：Nginx 核心功能详解与实战

本节将详细阐述 Nginx 最核心的三大功能，并提供可直接使用的配置示例。

### 4.1 作为 Web 服务器：静态文件托管与虚拟主机

Nginx 凭借其高效的静态文件服务能力，被广泛用作 Web 服务器。

*   **静态文件托管：** 使用 `root` 或 `alias` 指令可以轻松配置静态文件服务。例如，`location /images/ { root /data; }` 将 `/images/` 路径下的请求映射到服务器文件系统中的 `/data/images/` 目录 [14]。这种 **动静分离** 的策略是 Nginx 的重要应用，它将动态请求（如 `*.php`）交给后端应用服务器处理，而由 Nginx 直接处理静态资源（如图片、CSS、JS），从而显著减轻后端服务器的负载 [1]。
*   **虚拟主机配置：** Nginx 允许在同一台物理服务器上托管多个网站。通过在 `http` 块中定义多个 `server` 块，每个 `server` 块通过 `server_name` 和 `listen` 指令监听不同的域名或端口，从而实现虚拟主机功能 [21]。

### 4.2 作为反向代理服务器

反向代理是 Nginx 最强大、最常用的功能之一 [2]。与正向代理（隐藏客户端信息）不同，**反向代理（Reverse Proxy）** 将客户端的请求转发给其背后的一个或多个后端服务器，从而隐藏了后端服务器的真实信息，并作为客户端与后端服务器之间的“中间人” [2]。

*   **核心指令 `proxy_pass`：** 该指令用于将请求转发到指定的后端服务器 URL [21]。例如，将 `www.123.com` 的请求代理到本地运行在 8080 端口的 Tomcat 服务器 [21]：
    ```nginx
    server {
        listen 80;
        server_name www.123.com;
        location / {
            proxy_pass http://127.0.0.1:8080;
        }
    }
    ```
*   **代理请求头配置：** 在进行反向代理时，为了确保后端服务器能正确获取客户端的真实信息，通常需要配置代理请求头 [14]。例如，`proxy_set_header Host $host;` 和 `proxy_set_header X-Real-IP $remote_addr;` 分别用于将原始的 Host 头和客户端真实 IP 传递给后端服务器 [14]。

### 4.3 作为负载均衡器

在服务器集群环境中，Nginx 的负载均衡功能可以将请求分发到集群中的不同服务器，以实现流量的均衡和高可用性 [2]。

*   **核心模块 `upstream`：** `upstream` 指令用于定义后端服务器集群，并可以配置服务器的 IP 地址、端口和权重等参数 [14]。
    ```nginx
    upstream dramatic-offical-website {
        server 10.192.106.133;
        server 10.192.106.134;
    }
    server {
        server_name test-openai.com;
        listen 80;
        location / {
            proxy_pass http://dramatic-offical-website;
        }
    }
    ```
    上述配置将 `test-openai.com` 的请求代理到 `dramatic-offical-website` 集群，由 Nginx 根据负载均衡算法分发到 `10.192.106.133` 或 `10.192.106.134` [14]。

*   **负载均衡算法：** Nginx 内置了多种负载均衡算法 [6]：

    | 算法名称 | 工作原理 | 优缺点 | 典型应用场景 |
    | :--- | :--- | :--- | :--- |
    | **轮询 (round-robin)** | 默认算法。按时间顺序依次将请求分配给后端服务器，如果某个服务器宕机，会自动剔除。 | **优点：** 简单、无需配置。<br>**缺点：** 无法处理每台服务器的性能差异，容易导致性能较弱的服务器过载。 | 适用于后端服务器性能相同、并发量较小的场景。 |
    | **加权轮询 (weight)** | 在轮询的基础上，为每个服务器设置一个权重（`weight`）。权重越高的服务器，被分配到请求的几率越大。 | **优点：** 能够根据服务器的性能差异进行流量分配。<br>**缺点：** 如果权重设置不合理，仍可能导致流量分配不均。 | 适用于后端服务器性能存在差异，需要手动调整流量分配的场景。 |
    | **IP 哈希 (ip_hash)** | 根据客户端的 IP 地址进行哈希计算，将同一 IP 的所有请求固定地分发到同一台后端服务器。 | **优点：** 完美解决了 session 会话持久化问题。<br>**缺点：** 如果某些 IP 的请求量特别大，可能导致特定服务器的负载过高，造成负载不均衡。 | 适用于需要保持用户会话状态，且流量分布相对均匀的业务场景，如电商网站的购物车功能。 |

## 第四部分：高级功能与性能调优

### 5.1 HTTPS 安全配置

为网站启用 HTTPS 是保护数据传输安全和提升用户信任度的关键步骤 [25]。

*   **手动部署 SSL/TLS 证书：** 首先，需要获取 SSL/TLS 证书文件（`.crt` 或 `.pem`）和私钥文件（`.key`）[11]。然后，在 Nginx 的配置文件中进行如下配置 [11]：
    ```nginx
    server {
        listen 443 ssl;
        server_name your_domain.com;
        ssl_certificate /path/to/your/certificate.crt;
        ssl_certificate_key /path/to/your/private.key;
       ...
    }
    ```
    此配置指示 Nginx 在 443 端口上监听 HTTPS 流量，并使用指定的证书和私钥。

*   **使用 Certbot 自动化配置：** 对于个人网站或小型项目，Let's Encrypt 提供了免费的 SSL/TLS 证书，并且可以通过 Certbot 工具实现自动化申请和续期 [25]。在 Ubuntu 上，可以安装 Certbot 及其 Nginx 插件 [25]：
    ```bash
    sudo apt install certbot python3-certbot-nginx
    ```
    然后运行以下命令，Certbot 将自动获取证书并配置 Nginx：
    ```bash
    sudo certbot --nginx -d example.com -d www.example.com
    ```
    Certbot 还会自动设置一个定时任务来在证书过期前自动续期，极大地简化了维护工作 [25]。

### 5.2 Nginx 缓存机制（proxy_cache）

Nginx 的缓存机制是作为反向代理提升性能最有效的手段之一，其核心思想是“用空间换时间” [24]。通过将后端服务器的响应缓存到 Nginx 的磁盘上，可以显著减少对后端服务器的请求次数，从而减轻其负载并缩短响应时间 [24]。

*   **核心指令：** `proxy_cache_path` 用于定义缓存目录的路径和配置参数，例如缓存级别（`levels`）、共享内存区大小（`keys_zone`）、最大缓存空间（`max_size`）和缓存项的非活动时间（`inactive`）[24]。`proxy_cache` 则用于在 `http`、`server` 或 `location` 块中启用缓存 [24]。
*   **缓存策略：** 通过 `proxy_cache_valid`、`proxy_no_cache`、`proxy_cache_bypass` 等指令，可以精细地控制缓存行为，例如设置特定响应码的缓存时间，或者不缓存包含特定 Cookie 的请求 [24]。

### 5.3 性能优化：Gzip 压缩

Gzip 压缩可以显著减少网络传输的数据量，从而加快页面加载速度 [19]。Nginx 提供了 `gzip on` 指令来开启此功能 [19]。然而，大多数教程只简单地教导开启 Gzip，而忽略了其在高并发场景下的潜在性能开销。

对于静态文件，Nginx 默认采用 **动态 Gzip 压缩**，即在每次请求时实时压缩文件 [28]。当面对海量并发请求时，这种实时压缩会消耗大量的 CPU 资源，从而成为性能瓶颈 [28]。

一个真实的案例表明，通过将动态 Gzip 压缩改为 **静态 Gzip 压缩**，可以获得巨大的性能提升 [28]。其核心思想是：在部署时，预先将静态文件压缩成 `.gz` 格式，然后配置 Nginx 使用 `gzip_static on` 指令 [28]。这样，Nginx 在处理请求时会直接提供预先压缩好的文件，完全避免了实时的压缩计算开销 [28]。这种优化手段可以将 CPU 利用率从 90% 降至 7%，同时将吞吐量（QPS）提升 5 倍以上，是一种极为重要的性能调优手段 [28]。

## 第五部分：常见问题排查与故障诊断

### 6.1 日志分析：故障排查的起点

Nginx 的日志文件是排查故障的首要工具。默认情况下，Nginx 的日志文件位于 `/var/log/nginx/` 目录下，其中 `access.log` 记录所有访问请求，`error.log` 记录所有错误和警告信息 [16]。如果日志路径被修改，可以通过 `cat /etc/nginx/nginx.conf | grep 'access_log'` 命令来查找 [29]。

在查看日志时，可以使用不同的命令来满足不同的需求 [16]：
*   `cat`：用于查看整个文件的内容。
*   `less`：用于分页查看大型日志文件。
*   `tail -f`：用于实时监控日志文件的更新，这在故障复现和问题诊断时非常有用。

### 6.2 常见错误代码与解决方案

当 Nginx 出现问题时，错误代码是重要的诊断线索。一个结构化的诊断流程能够帮助用户从根本上解决问题，而不是治标不治本。

| 错误代码 | 常见原因 | 诊断与解决方案 |
| :--- | :--- | :--- |
| **403 Forbidden** | Nginx 进程没有权限访问请求的资源文件或目录。 | 检查 Nginx 配置文件中的 `user` 指令是否正确配置，并确保 Nginx 启动用户拥有目标目录的读写权限。如果权限不足，可以使用 `sudo chown -R nginx:nginx /path/to/directory` 修改文件或目录的所有者 [12]。 |
| **413 Request Entity Too Large** | 客户端上传文件的大小超过了 Nginx 的默认限制。 | 这个错误直接指向 Nginx 的配置问题。需要在 `http`、`server` 或 `location` 块中，增加 `client_max_body_size` 指令的值，例如 `client_max_body_size 100m;` [13]。 |
| **502 Bad Gateway** | Nginx 作为反向代理，无法从后端服务器获取有效响应。这通常是后端服务器故障的信号，而不是 Nginx 本身的问题。 | 这类问题可能由多种原因引起：<br>1.  **后端服务器宕机：** 检查后端应用服务是否正常运行。<br>2.  **磁盘空间不足：** 后端服务器磁盘空间不足可能导致写缓存失败，使用 `df -h` 命令检查磁盘空间 [31]。<br>3.  **php-cgi 进程数不够：** 对于 PHP 网站，后端进程池数量可能不足以处理请求。需要增加 `php-fpm.conf` 文件中的 `pm.max_children` 参数值 [31]。<br>4.  **后端执行超时：** 如果后端应用处理时间过长，可能导致 Nginx 超时。可以在 Nginx 配置文件中适当增加 `proxy_read_timeout` 和 `proxy_send_timeout` 等超时时间 [31]。 |
| **504 Gateway Timeout** | Nginx 在指定时间内未从后端服务器获得响应，通常由后端应用执行缓慢或超时引起。 | 检查后端应用的性能和日志。如果后端确实执行缓慢，可以考虑优化应用代码或增加服务器资源。同时，可以在 Nginx 配置文件中增加 `proxy_connect_timeout`、`proxy_send_timeout` 和 `proxy_read_timeout` 等超时时间 [8]。 |
