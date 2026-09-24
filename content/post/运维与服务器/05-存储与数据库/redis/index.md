---
title: redis
description: ""
date: 2025-10-17T11:26:56+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SQL
---


### 目录

- 一些问题处理

[Redis未授权访问漏洞处理](#Redis未授权访问漏洞处理)
[本地mac上_运行一个redis容器_然后想要在另一个容器中使用这个redis怎么做](#本地mac上_运行一个redis容器_然后想要在另一个容器中使用这个redis怎么做)




```bash 
# Redis 常用命令总结（适用于 apt install redis/redis-server 安装的场景，包括容器内）

```bash
# 1. 最简单直接启动（前台运行，用于测试）
redis-server

# 2. 使用配置文件后台启动（推荐方式）
redis-server /etc/redis/redis.conf

# 3. 带常用参数直接启动（不依赖配置文件）
redis-server --port 6379 --daemonize yes --protected-mode no

# 4. 检查 Redis 是否正常运行
redis-cli ping                  # 返回 PONG 表示成功
redis-cli -p 6379 ping

# 5. 优雅停止 Redis（强烈推荐，会自动保存数据）
redis-cli shutdown              # 默认执行 SAVE
redis-cli -p 6379 shutdown

# 6. 不保存数据直接停止
redis-cli shutdown nosave

# 7. 强制杀死进程（不推荐，可能丢数据）
kill -9 $(pidof redis-server)
pkill -9 redis-server

# 8. 重启 Redis
redis-cli shutdown && redis-server /etc/redis/redis.conf

# 9. 使用 service 管理（你在容器里通过 apt 安装后直接可用！）
service redis-server start      # 启动
service redis-server stop       # 停止
service redis-server restart    # 重启
service redis-server status     # 查看状态

# 10. 等价的更短写法（很多系统都支持）
service redis start
service redis stop
service redis restart
service redis status

# 11. 直接调用 init 脚本（永远有效）
/etc/init.d/redis-server start
/etc/init.d/redis-server stop
/etc/init.d/redis-server restart
/etc/init.d/redis-server status

# 12. 查看进程
ps aux | grep redis
pgrep -fl redis
```




### 什么是 Redis？

Redis (Remote Dictionary Server) 是一个开源的、使用 C 语言编写的、支持网络、可基于内存亦可持久化的日志型、Key-Value 数据库，并提供多种语言的 API。

它通常被称为“数据结构服务器”，因为值（value）可以是字符串 (String)、哈希 (Hash)、列表 (List)、集合 (Set) 和有序集合 (Sorted Set) 等类型。

**Redis 的主要特点：**

  * **速度快：** 数据存储在内存中，读写速度非常快。
  * **数据类型丰富：** 支持多种复杂的数据结构。
  * **持久化：** 可以将内存中的数据保存到磁盘中，重启时可以再次加载进行使用。
  * **原子性：** Redis 的所有操作都是原子性的，要么执行成功，要么执行失败，不会出现中间状态。
  * **丰富的特性：** 支持发布/订阅、事务、Lua 脚本等功能。

**常见应用场景：**

  * **缓存：** 这是 Redis 最常见的用途，用于缓存数据库查询结果、网页、或任何可以被缓存的数据，以减轻数据库压力。
  * **计数器：** 利用 Redis 原子性的 `INCR` 命令可以轻松实现高并发的计数功能，例如文章阅读量、点赞数。
  * **会话存储：** 存储用户的会话信息（Session），实现分布式系统的会话共享。
  * **排行榜：** 使用有序集合（Sorted Set）可以轻松实现实时更新的排行榜。
  * **消息队列：** 使用列表（List）的 `LPUSH` 和 `RPOP` 命令可以实现简单的消息队列。

-----

 第一步：安装 Redis

你可以通过以下几种方式安装 Redis：

1\. 在 Linux (Ubuntu/Debian) 上安装

使用包管理器是最简单的方式：

```bash
sudo apt update
sudo apt install redis-server
```

安装完成后，Redis 服务会自动启动。你可以使用以下命令检查服务状态：

```bash
sudo systemctl status redis-server
```

2. 使用 Docker 安装 (推荐，跨平台)

如果你安装了 Docker，这是最简单且最干净的安装方式，适用于任何操作系统。

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

这个命令会从 Docker Hub 下载最新的 Redis 镜像，并在后台运行一个名为 `my-redis` 的容器，将容器的 6379 端口映射到你主机的 6379 端口。

如果你在一个docker内开发，另一个docker容器安装redis

[本地mac上_运行一个redis容器_然后想要在另一个容器中使用这个redis怎么做](#本地mac上_运行一个redis容器_然后想要在另一个容器中使用这个redis怎么做)




-----

 第二步：连接到 Redis

安装并启动 Redis 后，你可以使用 `redis-cli` (Redis Command Line Interface) 连接到它。

如果你是直接在系统上安装的 Redis，直接在终端输入：

```bash
redis-cli
```

如果你是通过 Docker 安装的，你需要进入到容器内部：

```bash
docker exec -it my-redis redis-cli
```

连接成功后，你会看到类似下面的提示符：

```
127.0.0.1:6379>
```

现在，你可以开始输入 Redis 命令了。

**测试连接：**

输入 `PING` 命令，如果服务器正常运行，它会返回 `PONG`。

```
127.0.0.1:6379> PING
PONG
```

如果你的redis是安装在另外一个容器，使用如下
```bash
# 1. 进入你的应用容器
docker exec -it <你的应用容器名> bash  # 或者 sh

# 2. 在容器内部，更新包列表并安装
root@<container-id>:/# apt-get update
root@<container-id>:/# apt-get install redis-tools -y

# 3. 现在你可以使用了
root@<container-id>:/# redis-cli -h my-redis
my-redis:6379> PING
PONG
```



-----

 第三步：学习基本命令和数据结构

Redis 是一个 Key-Value 数据库。每个 Key 都有一个与之关联的 Value。下面是 Redis 最核心的五种数据结构及其常用命令。

1. 字符串 (String)

这是最基本的数据类型，一个 key 对应一个 value。

  * **`SET key value`**: 设置一个键值对。
    ```
    127.0.0.1:6379> SET username "gemini"
    OK
    ```
  * **`GET key`**: 获取一个键的值。
    ```
    127.0.0.1:6379> GET username
    "gemini"
    ```
  * **`DEL key`**: 删除一个键。
    ```
    127.0.0.1:6379> DEL username
    (integer) 1
    ```
  * **`INCR key`**: 将 key 中储存的数字值增一（如果 key 不存在，则初始化为 0 再执行 INCR 操作）。
    ```
    127.0.0.1:6379> SET page_views 100
    OK
    127.0.0.1:6379> INCR page_views
    (integer) 101
    ```

2\. 哈希 (Hash)

Hash 是一个 string 类型的 field 和 value 的映射表，它非常适合用于存储对象。

  * **`HSET key field value`**: 将哈希表 key 中的字段 field 的值设为 value。
    ```
    127.0.0.1:6379> HSET user:1 name "Alice" age 25
    (integer) 2
    ```
  * **`HGET key field`**: 获取哈希表 key 中给定字段 field 的值。
    ```
    127.0.0.1:6379> HGET user:1 name
    "Alice"
    ```
  * **`HGETALL key`**: 获取在哈希表中指定 key 的所有字段和值。
    ```
    127.0.0.1:6379> HGETALL user:1
    1) "name"
    2) "Alice"
    3) "age"
    4) "25"
    ```
  * **`HDEL key field`**: 删除哈希表 key 中的一个或多个指定字段。
    ```
    127.0.0.1:6379> HDEL user:1 age
    (integer) 1
    ```

3\. 列表 (List)

List 是简单的字符串列表，按照插入顺序排序。你可以添加一个元素到列表的头部（左边）或者尾部（右边）。

  * **`LPUSH key element [element ...]`**: 将一个或多个值插入到列表头部。
    ```
    127.0.0.1:6379> LPUSH tasks "task1" "task2"
    (integer) 2
    ```
  * **`RPUSH key element [element ...]`**: 将一个或多个值插入到列表尾部。
    ```
    127.0.0.1:6379> RPUSH tasks "task3"
    (integer) 3
    ```
  * **`LRANGE key start stop`**: 获取列表指定范围内的元素。(`0` 是第一个元素, `-1` 是最后一个元素)。
    ```
    127.0.0.1:6379> LRANGE tasks 0 -1
    1) "task2"
    2) "task1"
    3) "task3"
    ```
  * **`LPOP key`**: 移出并获取列表的第一个元素。
    ```
    127.0.0.1:6379> LPOP tasks
    "task2"
    ```
  * **`RPOP key`**: 移出并获取列表的最后一个元素。
    ```
    127.0.0.1:6379> RPOP tasks
    "task3"
    ```

4\. 集合 (Set)

Set 是 String 类型的无序集合。集合成员是唯一的，这就意味着集合中不能出现重复的数据。

  * **`SADD key member [member ...]`**: 向集合添加一个或多个成员。
    ```
    127.0.0.1:6379> SADD tags "database" "nosql" "redis"
    (integer) 3
    ```
  * **`SMEMBERS key`**: 返回集合中的所有成员。
    ```
    127.0.0.1:6379> SMEMBERS tags
    1) "redis"
    2) "nosql"
    3) "database"
    ```
  * **`SISMEMBER key member`**: 判断 member 元素是否是集合 key 的成员。
    ```
    127.0.0.1:6379> SISMEMBER tags "redis"
    (integer) 1
    127.0.0.1:6379> SISMEMBER tags "mysql"
    (integer) 0
    ```
  * **`SREM key member [member ...]`**: 移除集合中一个或多个成员。
    ```
    127.0.0.1:6379> SREM tags "nosql"
    (integer) 1
    ```

5\. 有序集合 (Sorted Set / ZSET)

和 Set 一样，Sorted Set 也是 string 类型元素的集合，且不允许重复的成员。不同的是每个元素都会关联一个 double 类型的分数（score）。Redis 正是通过分数来为集合中的成员进行从小到大的排序。

  * **`ZADD key score member [score member ...]`**: 向有序集合添加一个或多个成员，或者更新已存在成员的分数。
    ```
    127.0.0.1:6379> ZADD leaderboard 100 "player1" 250 "player2" 50 "player3"
    (integer) 3
    ```
  * **`ZRANGE key start stop [WITHSCORES]`**: 通过索引区间返回有序集合成指定区间内的成员（按分数从小到大）。
    ```
    127.0.0.1:6379> ZRANGE leaderboard 0 -1 WITHSCORES
    1) "player3"
    2) "50"
    3) "player1"
    4) "100"
    5) "player2"
    6) "250"
    ```
  * **`ZREVRANGE key start stop [WITHSCORES]`**: 返回有序集中指定区间内的成员，通过索引，分数从高到低。
    ```
    127.0.0.1:6379> ZREVRANGE leaderboard 0 1 WITHSCORES
    1) "player2"
    2) "250"
    3) "player1"
    4) "100"
    ```
  * **`ZREM key member [member ...]`**: 移除有序集合中的一个或多个成员。
    ```
    127.0.0.1:6379> ZREM leaderboard "player3"
    (integer) 1
    ```

-----

 第四步：一些通用的重要命令

  * **`KEYS pattern`**: 查找所有符合给定模式的 key。**注意：** 在生产环境中要慎用，因为它会遍历所有的键，可能会阻塞服务器。
    ```
    127.0.0.1:6379> KEYS *
    1) "tasks"
    2) "user:1"
    3) "page_views"
    ...
    ```
  * **`EXPIRE key seconds`**: 为给定的 key 设置过期时间，以秒计。当 key 过期后，它会被自动删除。这对于实现缓存非常有用。
    ```
    127.0.0.1:6379> SET cache_data "some important data"
    OK
    127.0.0.1:6379> EXPIRE cache_data 60  // 60秒后过期
    (integer) 1
    ```
  * **`TTL key`**: 以秒为单位，返回给定 key 的剩余生存时间 (Time To Live)。
    ```
    127.0.0.1:6379> TTL cache_data
    (integer) 55  // (还剩55秒)
    ```
  * **`FLUSHDB`**: 删除当前数据库里的所有数据。**极度危险，请谨慎使用！**
  * **`FLUSHALL`**: 删除所有数据库里的所有数据。**极度危险，请谨慎使用！**

-----

 第五步：在你的代码中使用 Redis

`redis-cli` 是一个很好的学习和调试工具，但在实际应用中，你需要在你的编程语言中通过 Redis 客户端库来连接和操作 Redis。

几乎所有主流语言都有成熟的 Redis 客户端库。例如：

  * **Python**: `redis-py`
  * **Java**: `Jedis`, `Lettuce`
  * **Node.js**: `node-redis`, `ioredis`
  * **Go**: `go-redis`
  * **PHP**: `phpredis`

**Python 示例 (`redis-py`)**

1.  安装库:

    ```bash
    pip install redis
    ```

2.  连接和使用:

    ```python
    import redis

    # 连接到本地 Redis 服务
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # 使用 String
    r.set('foo', 'bar')
    print(r.get('foo')) # 输出: bar

    # 使用 Hash
    r.hset('user-session:123', mapping={
        'name': 'John',
        'surname': 'Smith',
        'company': 'Redis',
        'age': 29
    })
    print(r.hgetall('user-session:123'))
    ```

 总结和后续学习

恭喜你！你已经完成了 Redis 的入门。你现在应该知道如何安装、连接 Redis，并使用其核心数据结构进行基本操作。

**下一步可以学习：**

  * **Redis 持久化：** 了解 RDB 和 AOF 两种持久化方式的区别和配置。
  * **Redis 事务：** 学习 `MULTI` 和 `EXEC` 命令来执行一组原子操作。
  * **发布/订阅 (Pub/Sub)：** 探索 Redis 的消息发布和订阅功能。
  * **Redis 安全：** 学习如何为 Redis 设置密码和配置安全的网络访问。
  * **Redis 集群：** 了解主从复制 (Replication)、哨兵 (Sentinel) 和集群 (Cluster) 模式以实现高可用和扩展性。



### 一些操作

#### Redis未授权访问漏洞处理

```md
漏洞描述：Redis 未授权访问漏洞
Redis 未授权访问漏洞是一个非常严重的安全问题，它通常是因为 Redis 服务器直接暴露在公网或内网中，并且**没有配置密码认证**导致的。攻击者可以利用这个漏洞读取、修改甚至删除数据，更严重的情况下，可以利用 Redis 的一些特性（如写入 `authorized_keys` 或计划任务文件）来获取服务器的控制权。

以下是处理和防御 Redis 未授权访问漏洞的主要步骤和措施：

### 1\. 启用密码认证（最重要）

在 Redis 配置文件中设置一个**强密码**，启用认证功能。

  * **修改配置文件：** 找到 `redis.conf` 文件（通常在 `/etc/redis/` 或 `/etc/redis/redis.conf`）。
  * **设置密码：** 找到或添加 `requirepass` 这一行，并设置一个复杂的密码。
    ```conf
    requirepass yourStrongPasswordHere
    ```
    *记得替换 `yourStrongPasswordHere` 为你设置的实际密码。*
  * **重启 Redis：** 更改配置后，需要重启 Redis 服务使其生效。
    ```bash
    # 例如：
    sudo systemctl restart redis
    # 或者
    sudo service redis-server restart
    ```
  * **验证：** 使用 `redis-cli` 连接后，尝试执行命令，会提示需要认证。
    ```bash
    redis-cli
    > PING
    (error) NOAUTH Authentication required.
    > AUTH yourStrongPasswordHere
    OK
    > PING
    PONG
    ```

### 2\. 限制网络访问（网络隔离）

Redis 本身的设计是运行在受信任的环境中，因此不应该直接暴露给公网。

  * **绑定本地或私有 IP：** 仅允许 Redis 监听应用的服务器 IP 或本地回环地址（`127.0.0.1`）。在 `redis.conf` 中修改 `bind` 选项：
      * **仅允许本地访问：**
        ```conf
        bind 127.0.0.1
        ```
      * **允许特定内网 IP 访问：** 绑定内网 IP 地址。
        ```conf
        bind 127.0.0.1 192.168.1.100  # 替换为你的应用服务器IP
        ```
  * **配置防火墙：** 使用防火墙（如 `iptables`, `ufw`, 安全组等）限制对 Redis 端口（默认是 6379）的访问，**只允许**信任的应用服务器 IP 地址连接。
  * **网络分段：** 将 Redis 服务器放在一个独立的、只有应用服务器能访问的私有网络段中。

### 3\. 启用保护模式（Protected Mode）

Redis 3.2.0 及更高版本引入了保护模式（Protected Mode）。

  * **检查配置：** 在 `redis.conf` 中确保 `protected-mode` 设置为 `yes`。
    ```conf
    protected-mode yes
    ```
    *在默认配置下，如果 Redis 没有设置密码且绑定了非本地回环地址，保护模式会自动开启，阻止外部连接，仅响应本地回环地址（`127.0.0.1`）的请求。*

### 4\. 禁用或重命名危险命令

为了防止攻击者利用 Redis 的配置命令进行恶意操作（如写入 `authorized_keys`），可以考虑禁用或重命名一些高风险命令。

  * **禁用或重命名 `CONFIG` 命令：** 在 `redis.conf` 中添加：
    ```conf
    # 禁用 CONFIG 命令
    rename-command CONFIG ""
    # 或者重命名（推荐，防止应用端需要用到）
    rename-command CONFIG aRandomStringForConfig
    ```
  * 其他高危命令如 `FLUSHALL`、`FLUSHDB`、`SAVE`、`BGSAVE` 也可以根据需要进行限制。

### 5\. 使用低权限用户运行 Redis

不要使用 `root` 用户运行 Redis 服务。创建一个专门的低权限用户来运行 Redis 进程，即使被攻击者攻破，也能限制其在系统上的权限。

### 总结加固：

1.  **设置强密码（`requirepass`）。**
2.  **限制网络访问（`bind` 和防火墙）。**
3.  **确保 `protected-mode yes`。**
4.  **禁用或重命名高危命令（`CONFIG`）。**
5.  **使用低权限用户运行。**
```

#### 本地mac上_运行一个redis容器_然后想要在另一个容器中使用这个redis怎么做


在 Mac 本地上，要让一个容器（应用容器）连接到另一个容器（Redis 容器），最推荐和最现代的方法是使用**自定义的 Docker 网络**。

这能确保容器之间可以通过一个稳定且易于记的主机名（即你的 Redis 容器名）进行通信，而不需要关心动态变化的 IP 地址。

这里是详细的步骤，分为两种主要方法：

- 方法一：使用 Docker CLI 命令（推荐）

这是最基础和最清晰的方法，分为三步：

1\. 创建一个自定义的 Docker 网络

首先，创建一个新的“桥接”网络。所有需要相互通信的容器都应该连接到这个网络。

```bash
docker network create my-app-network
```

  * `my-app-network` 是你给这个网络起的名字，可以自定义。

2\. 启动 Redis 容器并连接到该网络

在运行 Redis 容器时，使用 `--network` 参数指定它加入你刚创建的网络。同时，使用 `--name` 给它一个固定的名字（例如 `my-redis`），这个名字将作为它在网络内部的主机名。

```bash
docker run -d \
  --name my-redis \
  --network my-app-network \
  redis
```

  * `-d`：在后台运行。
  * `--name my-redis`：将容器命名为 `my-redis`。
  * `--network my-app-network`：将其连接到 `my-app-network`。
  * **注意**：我在这里**没有**使用 `-p 6379:6379`。因为你的应用容器在同一个网络中，它可以直接通过 `6379` 端口访问 Redis。只有当你需要从 Mac *主机*（例如通过 `redis-cli` 或桌面 GUI）访问这个 Redis 时，才需要添加 `-p 6379:6379` 来将端口暴露给主机。

3\. 启动你的应用容器并连接到同一网络

现在，启动你的第二个容器（例如一个 Node.js、Python 或 Java 应用），并同样将它连接到 `my-app-network`。

```bash
docker run -it \
  --network my-app-network \
  <你的应用镜像名>
```

4\. 在应用中连接 Redis

在你的应用代码中，连接 Redis 的主机地址**不再是 `localhost` 或 `127.0.0.1`**，而是你在第二步中为 Redis 容器设置的名字：`my-redis`。

  * **Redis 连接字符串示例**：`redis://my-redis:6379`

Docker 会自动将 `my-redis` 这个主机名解析为 Redis 容器在 `my-app-network` 网络中的内部 IP 地址。

-----

- 方法二：使用 Docker Compose（更简单的多容器管理）

如果你需要同时管理 Redis 和你的应用两个（或更多）容器，使用 `docker-compose` 是一个更简单、更可维护的方法。它会自动为你创建和管理网络。

1.  在你的项目根目录创建一个 `docker-compose.yml` 文件。

2.  在该文件中定义你的两个服务（`app` 和 `redis`）：

    ```yaml
    version: '3.8' # 使用一个较新的版本

    services:
      # 你的应用程序服务
      app:
        build: .  # 假设你的 Dockerfile 在当前目录
        # 或者使用 image: <你的应用镜像名>
        ports:
          - "8080:80" # 举例：将你应用的80端口映射到主机的8080
        environment:
          # 关键：在这里注入 Redis 的主机名
          - REDIS_HOST=my-redis
          - REDIS_PORT=6379
        # 确保你的应用在 redis 启动后再启动
        depends_on:
          - my-redis

      # 你的 Redis 服务
      my-redis: # 服务的名字
        image: redis
        # 你可以保留这个名字，也可以不写
        container_name: my-redis-container
        # 如果需要从主机访问，取消下面这行的注释
        # ports:
        #   - "6379:6379"

    # Docker Compose 会自动创建一个默认网络
    # 并将 app 和 my-redis 两个服务都加入其中
    ```

3.  在 `docker-compose.yml` 文件所在的目录中，运行以下命令：

    ```bash
    docker-compose up -d
    ```

Docker Compose 会自动完成所有操作：

1.  创建一个名为 `项目目录名_default` 的网络。
2.  启动名为 `my-redis` 的 Redis 服务。
3.  启动你的 `app` 服务。
4.  在 `app` 容器内部，可以直接使用主机名 `my-redis`（即 `services:` 下定义的服务名）来连接到 Redis。

-----

- 补充：连接到 Mac *主机* 上的 Redis

如果你的意思是 Redis **没有**运行在容器里，而是**直接安装在你的 Mac 电脑上**，而你想从一个 Docker 容器里去连接它，那么情况有所不同。

在这种情况下，你不能使用 `localhost`（因为 `localhost` 在容器内部指的是容器自己）。你需要使用一个特殊的 DNS 名称：`host.docker.internal`。

  * **连接地址**：`host.docker.internal:6379`

`host.docker.internal` 是 Docker for Mac 提供的一个特殊地址，它会解析为你 Mac 主机的 IP 地址。
