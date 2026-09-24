---
title: server_ops
description: ""
date: 2026-03-24T15:25:22+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - Server Operations and Maintenance-服务器运维
---




# 注意事项

## 🩸 血泪教训：别再把数据库和业务代码塞进同一个 Docker 容器了！

**前言：**

刚接触 Docker 的时候，我曾陷入一个深深的误区——认为“容器化部署”就等于把前端、后端、MySQL、Redis 等所有东西全都写进一个 docker-compose.yml 里，然后在服务器上敲一行 docker-compose up -d，看着整个世界“一键启动”，简直爽翻了。

直到最近，我经历了一次惨痛的教训：业务代码引发的资源耗尽导致 MySQL 崩溃，随之而来的是极其痛苦的备份恢复，整个服务直接瘫痪。

这次事故让我彻底顿悟：在生产环境中，绝不能把基础设施（Infra）和实际业务代码混在一起部署。

---

**1. 为什么“一键打包”只适合玩具项目？**

把所有服务部署在同一台机器上，在本地开发或测试环境确实是银弹，但在生产环境却是一场定时炸弹。从“单机思维”走向“架构思维”，我们需要明白以下几个核心差异：

🆚 **无状态（业务应用） vs 有状态（数据库）**

你的后端 API 是“无状态”的，随时可以重启、销毁、水平扩展，崩了拉起一个新的立刻就能用。而数据库（MySQL/PostgreSQL）是“有状态”的，里面存着身家性命。把它们绑在一起，无异于让脆弱的消耗品和贵重的传家宝放在同一个易碎的盒子里。

💣 **恐怖的“爆炸半径”（Blast Radius）**

如果业务代码出现 Bug（比如内存泄漏），或者遭遇突发流量，服务器的 CPU 和内存会被瞬间吃光。这时 Linux 的 OOM Killer 就会无情启动，强制杀掉占用内存大的进程——通常数据库就是那个“冤大头”。业务代码的锅，导致数据库崩溃，进而导致全站瘫痪。

此外，业务日志和数据库争抢磁盘 IOPS，也会让数据库性能大打折扣。

💡 **架构顿悟：让计算归计算，存储归存储。** 将业务应用和数据库分别部署在不同的服务器上，进行物理隔离，是迈向高可用架构的第一步。

---

**2. 妥协与选择：自建 Docker 版 PostgreSQL**

明确了分离部署的原则后，我面临了一个新问题：我手头的云厂商 RDS 只有 MySQL，但我目前的业务非常想用 PostgreSQL。

云厂商的高级托管服务（如 AWS RDS 或 Serverless 方案如 Neon/Supabase）当然是首选，但如果受限于预算或现有资源，单独买一台服务器，用 Docker 跑 PostgreSQL 依然是一个极具性价比且成熟的方案。

很多人担心 Docker 部署数据库会有性能损耗。但在中小规模业务面前，那 2%~5% 的网络/IO损耗完全可以忽略不计。相反，只要坚持了**“物理分离”**的原则，Docker 带来的环境一致性和迁移便利性绝对物超所值。

---

**3. 生产级 Docker PostgreSQL 部署指南**

既然成为了自己的 DBA，就不能像本地开发那样随意。以下是我整理的部署在独立数据库服务器上的生产级 docker-compose.yml 模板：

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine  # 推荐指定明确的版本号，Alpine体积更小
    container_name: postgres_prod
    restart: always            # 宿主机重启时自动拉起
    environment:
      POSTGRES_USER: myuser         # ⚠️ 不要用默认的 postgres 作为日常用户名
      POSTGRES_PASSWORD: MyStrongPassword_123! 
      POSTGRES_DB: mydb           
      TZ: Asia/Shanghai           
    ports:
      # ⚠️ 警告：千万不要写 "5432:5432" 直接暴露公网！
      - "5432:5432"
    volumes:
      # 核心！必须把数据挂载到宿主机，绝对不能留在容器内
      - /data/postgres_data/data:/var/lib/postgresql/data
      # 挂载一个备份目录，方便宿主机的定时任务导出数据
      - /data/postgres_data/backups:/backups
    command: 
      # 【性能调优】Docker PG默认 shared_buffers 极小 (128MB)
      # 推荐把 shared_buffers 设置为这台独立服务器总物理内存的 25% (假设分配1GB)
      - "postgres"
      - "-c"
      - "shared_buffers=1GB"
      - "-c"
      - "max_connections=200"
```

---

**4. 守住底线：数据库保命的“三道防线”**

脱离了云数据库 RDS 的温室，自建 Docker 数据库必须自己做好以下三道保险，否则之前的悲剧迟早重演：

🛡️ **第一道防线：防勒索（网络隔离）**

自建数据库最容易踩的坑就是被勒索软件删库要比特币。

绝对不要把 5432 端口暴露在公网上！

去云服务器控制台的安全组（防火墙）设置中，配置 5432 端口的入站规则：仅允许你业务服务器的内网 IP 访问。

🚀 **第二道防线：突破默认限制（性能调优）**

不要抱怨 Docker 跑 PG 慢，往往是因为没改配置。PG 默认的 shared_buffers 非常保守（128MB），会导致疯狂读写硬盘。如果你这台专用的 DB 服务器有 4G 内存，直接在 docker command 里设为 1GB（25% 原则），性能会有质的飞跃。

💾 **第三道防线：自动化异地备份（保命符）**

由于没了 RDS 的自动备份，我们必须手动写 Crontab 脚本每天导出，并且一定要传到异地（如对象存储 OSS/S3）。

一个简单的 Bash 备份脚本参考 (backup.sh)：

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/data/postgres_data/backups"

# 1. 容器内执行 pg_dump 导出
docker exec postgres_prod pg_dump -U myuser -d mydb -F c -f /backups/mydb_$DATE.dump

# 2. 删除7天前的旧备份（防止撑爆硬盘）
find $BACKUP_DIR -name "*.dump" -type f -mtime +7 -exec rm -f {} \;

# 3. 【关键】上传到对象存储或另一台机器
# ossutil cp $BACKUP_DIR/mydb_$DATE.dump oss://my-backup-bucket/
```

通过 `crontab -e` 设定每天凌晨 3 点执行：`0 3 * * * /bin/bash /data/postgres_data/backup.sh`

---

**写在最后**

从“把所有东西塞进一个容器里一键启动”，到“将业务逻辑与基础设施拆分并做好隔离与备份”，这是每一个开发者向后端架构师蜕变的必经之路。

“性能损失”从来不是自建数据库的痛点，“运维疏忽”才是。只要严格遵守分离部署 + 挂载卷 + 限制公网访问 + 定时异地备份，你用 Docker 搭建的 PostgreSQL，足以平稳支撑你的业务走过漫长的初创和成长期。

---

**5. 用户权限管理：创建只读用户**

在实际生产环境中，我们经常需要给第三方工具或只读分析需求提供数据库访问，但绝不能直接暴露拥有写权限的超级用户。

以下是在 PostgreSQL 中创建一个只读用户的完整命令：

```sql
-- 1. 创建只读用户（替换密码为强密码）
CREATE USER readonly_vanta WITH PASSWORD 'Vanta123456!';

-- 2. 授予数据库连接权限
GRANT CONNECT ON DATABASE "Vanta" TO readonly_vanta;

-- 3. 授予 schema 的使用权限
GRANT USAGE ON SCHEMA public TO readonly_vanta;

-- 4. 授予现有所有表的查询权限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_vanta;

-- 5. 【关键】设置默认权限，使该用户自动拥有未来新建表的查询权
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_vanta;
```

> 💡 **注意事项**
> - 创建用户后，务必在安全组中限制该用户的连接来源 IP，避免公网直接暴露。
> - 如果数据库已有多个 schema，需要针对每个 schema 重复执行 `GRANT USAGE` 和 `GRANT SELECT`。
> - 如需回收权限，可使用 `REVOKE` 命令或直接用 `DROP USER readonly_vanta;` 删除用户。
