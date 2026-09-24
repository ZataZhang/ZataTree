---
title: PostgreSQL
description: ""
date: 2025-12-30T12:27:59+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SQL
---



## 安装

1. PG数据库安装

* **Docker (最快方式):**
```bash
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres

```

* **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

```

* **Windows/Mac:** 推荐直接去官网下载 [PostgreSQL Installer](https://www.postgresql.org/download/)。


2. 相关工具的安装

[navicat for PG lite](https://www.navicat.com.cn/download/navicat-premium-lite)

---

2. 连接 (使用命令行 psql)

PostgreSQL 安装后会创建一个默认的超级用户，叫 `postgres`。

* **在 Linux/Mac 终端中登录：**
```bash
# 切换到 postgres 用户并启动 psql 工具
sudo -u postgres psql

```


* **登录成功后：** 你会看到提示符变成 `postgres=#`，这表示你已经是超级管理员了。




## 基础操作实战 (CRUD)

以下命令请在 `psql` 命令行或图形化客户端的 SQL 编辑器中执行。**注意：SQL 语句末尾必须加分号 `;**`。

1. 数据库操作

```sql
-- 创建一个新数据库
CREATE DATABASE my_app;

-- 切换/连接到这个数据库 (psql 专用指令，非 SQL)
\c my_app
-- 提示符会变为 my_app=#

```

2. 创建表 (Create Table)

PostgreSQL 的数据类型非常丰富。

* `SERIAL`: 相当于 MySQL 的 `AUTO_INCREMENT`（自增主键）。
* `TEXT`: PG 中推荐使用 `TEXT` 代替 `VARCHAR`，性能几乎一样但没有长度限制。

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

3. 插入数据 (Insert)

```sql
-- 插入单条数据
INSERT INTO users (username, email, age) 
VALUES ('zhang_san', 'zhang@example.com', 25);

-- 插入多条数据
INSERT INTO users (username, email, age) 
VALUES 
('li_si', 'li@example.com', 30),
('wang_wu', 'wang@example.com', 22);

```

4. 查询数据 (Select)

```sql
-- 查询所有
SELECT * FROM users;

-- 条件查询
SELECT username, email FROM users WHERE age > 24;

-- 排序与限制
SELECT * FROM users ORDER BY age DESC LIMIT 1;

```

5. 更新与删除 (Update & Delete)

```sql
-- 更新
UPDATE users SET age = 26 WHERE username = 'zhang_san';

-- 删除
DELETE FROM users WHERE age < 20;

```

---

`进阶功能 (PG 的杀手锏)`

这是大家选择 PG 而不是 MySQL 的主要原因：**对 JSON 的原生支持**。你可以把它当成 MongoDB 来用。

1. 创建包含 JSON 的表

假设我们要存用户的“配置信息”，每个人的配置都不一样，且经常变动。

```sql
CREATE TABLE user_configs (
    user_id INT,
    config JSONB  -- JSONB 是二进制存储的 JSON，查询速度极快
);

```

2. 插入 JSON 数据

```sql
INSERT INTO user_configs (user_id, config)
VALUES (1, '{"theme": "dark", "notifications": true, "tags": ["admin", "editor"]}');

```

3. 查询 JSON 内部的字段

PG 提供了特殊的运算符 `->` 和 `->>`。

```sql
-- 查询 theme 是 dark 的用户
SELECT * FROM user_configs WHERE config->>'theme' = 'dark';

-- 甚至可以查询 JSON 数组中是否包含某个值
SELECT * FROM user_configs WHERE config->'tags' ? 'admin';

```

---

`第五步：常用的 `psql` 快捷指令 (作弊条)`

如果你使用命令行工具 `psql`，这些指令必须背下来（注意这些指令前面是反斜杠 `\`，且不需要分号）：

| 指令 | 作用 | 对应 MySQL |
| --- | --- | --- |
| `\l` | 列出所有数据库 | `SHOW DATABASES;` |
| `\c dbname` | 切换到指定数据库 | `USE dbname;` |
| `\dt` | 列出当前库下的所有表 | `SHOW TABLES;` |
| `\d tablename` | 查看表结构详细信息 | `DESC tablename;` |
| `\q` | **退出 psql** | `EXIT;` |
| `\timing` | 开启/关闭查询计时 | (无) |

---

## 概念

#### 知识点
PostgreSQL（常被简称为 Postgres 或 PG）是一个功能非常强大的开源数据库。对于刚接触它的人来说，最主要的门槛在于它的**架构概念**和**命令行工具**与 MySQL 略有不同。

这是一个从 0 到 1 的详细上手教程。

在使用之前，需要理解 PG 的层级结构，这比 MySQL 多了一层：

* **MySQL:** 实例 (Instance) -> 数据库 (Database/Schema) -> 表 (Table)
* **PostgreSQL:** 实例 (Instance) -> 数据库 (Database) -> **模式 (Schema)** -> 表 (Table)
* *注：默认情况下，一切都会放在名为 `public` 的模式下，所以初学者可以暂时忽略“模式”这一层，当作它不存在。*

#### 推荐的图形化客户端 (GUI)

如果你不想天天敲命令行，推荐下载以下软件来管理 Postgres：

1. **pgAdmin 4:** 官方提供的工具，功能最全，web 风格，但有时候稍微有点慢。
2. **DBeaver (强烈推荐):** 免费开源，支持 PG、MySQL 等所有数据库，界面类似 Eclipse，功能非常强大。
3. **Navicat for PostgreSQL:** 收费软件，好用但贵。

