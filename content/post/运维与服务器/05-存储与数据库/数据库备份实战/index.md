---
title: 数据库备份实战
description: "PostgreSQL 与 MySQL 数据库备份策略、自动化脚本与恢复演练完整指南"
date: 2026-05-28T14:55:07+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SQL
---

## 前言

数据是企业的核心资产，数据库备份是数据安全的最后一道防线。本文将系统介绍 PostgreSQL 和 MySQL 的备份方法、自动化策略以及恢复演练流程。

## 一、PostgreSQL 备份

### 1.1 pg_dump 基础用法

`pg_dump` 是 PostgreSQL 最常用的逻辑备份工具，支持单数据库导出。

```bash
# 基本备份命令
pg_dump -h localhost -U postgres -d mydb > backup.sql

# 压缩备份（推荐）
pg_dump -h localhost -U postgres -d mydb -Fc > backup.dump

# 仅备份结构（不含数据）
pg_dump -h localhost -U postgres -d mydb --schema-only > schema.sql

# 仅备份数据（不含结构）
pg_dump -h localhost -U postgres -d mydb --data-only > data.sql

# 备份指定表
pg_dump -h localhost -U postgres -d mydb -t users -t orders > tables.sql
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `-h` | 数据库主机地址 |
| `-U` | 连接用户名 |
| `-d` | 数据库名称 |
| `-Fc` | 自定义格式压缩（推荐，支持并行恢复） |
| `-t` | 指定备份的表 |

### 1.2 pg_dumpall 全库备份

备份整个 PostgreSQL 实例（所有数据库 + 全局对象）：

```bash
# 备份所有数据库和全局对象（角色、表空间等）
pg_dumpall -h localhost -U postgres > all_databases.sql

# 仅备份全局对象（角色定义）
pg_dumpall -h localhost -U postgres --globals-only > globals.sql
```

### 1.3 恢复方法

```bash
# 恢复 SQL 格式备份
psql -h localhost -U postgres -d mydb < backup.sql

# 恢复自定义格式备份（支持并行）
pg_restore -h localhost -U postgres -d mydb -j 4 backup.dump

# 恢复前创建新数据库
createdb -h localhost -U postgres mydb_restore
pg_restore -h localhost -U postgres -d mydb_restore backup.dump
```

---

## 二、MySQL 备份

### 2.1 mysqldump 基础用法

```bash
# 基本备份命令
mysqldump -h localhost -u root -p mydb > backup.sql

# 备份所有数据库
mysqldump -h localhost -u root -p --all-databases > all_databases.sql

# 备份指定表
mysqldump -h localhost -u root -p mydb users orders > tables.sql

# 仅备份结构
mysqldump -h localhost -u root -p mydb --no-data > schema.sql

# 仅备份数据
mysqldump -h localhost -u root -p mydb --no-create-info > data.sql
```

**推荐参数组合：**

```bash
# 生产环境推荐参数
mysqldump -h localhost -u root -p \
  --single-transaction \      # InnoDB 一致性快照
  --routines \                # 包含存储过程和函数
  --triggers \                # 包含触发器
  --events \                  # 包含事件
  --master-data=2 \           # 记录 binlog 位置（用于主从同步）
  mydb > backup.sql
```

### 2.2 恢复方法

```bash
# 恢复数据库
mysql -h localhost -u root -p mydb < backup.sql

# 恢复所有数据库
mysql -h localhost -u root -p < all_databases.sql
```

---

## 三、其他 PostgreSQL 图形化工具

除了 Navicat，还有多种优秀的 PostgreSQL 客户端工具支持备份和恢复功能。

### 3.1 pgAdmin

pgAdmin 是 PostgreSQL 官方推荐的免费图形化管理工具：

**安装方法：**

```bash
# 使用 Homebrew 安装（macOS）
brew install --cask pgadmin4

# 或从官网下载：https://www.pgadmin.org/download/
```

**备份步骤：**

1. 连接数据库服务器，选择目标数据库
2. 右键点击数据库 →「备份」
3. 配置备份选项：
   - **格式**：Custom（推荐）、Directory、Plain SQL、Tar
   - **编码**：UTF8（推荐）
   - **中定义**：选择「仅结构」或「结构和数据」
4. 选择备份文件保存位置，点击「备份」

**恢复步骤：**

1. 右键点击目标数据库 →「恢复」
2. 选择备份文件（.backup 或 .dump）
3. 配置恢复选项：
   - **架构**：选择要恢复的 schema
   - **数据**：选择要恢复的表
4. 点击「恢复」执行

**优点：**

- 免费开源，官方推荐
- 功能全面，支持服务器管理
- 跨平台（Windows/macOS/Linux）

**缺点：**

- 界面较复杂，新手上手较难
- 大数据库备份可能较慢

---

### 3.2 DBeaver

DBeaver 是一款功能强大的免费数据库管理工具，支持 PostgreSQL 及多种数据库：

**安装方法：**

```bash
# 使用 Homebrew 安装（macOS）
brew install --cask dbeaver-community

# 或从官网下载：https://dbeaver.io/download/
```

**备份步骤：**

1. 右键点击数据库 →「工具」→「备份数据库」
2. 选择备份对象（整个库或指定表）
3. 配置备份选项：
   - **格式**：SQL、Dump、CSV 等
   - **选项**：包含索引、触发器、外键等
4. 保存备份文件

**恢复步骤：**

1. 右键点击目标数据库 →「工具」→「恢复数据库」
2. 选择备份文件
3. 配置恢复选项
4. 执行恢复

**优点：**

- 完全免费开源
- 支持 80+ 种数据库
- 界面友好，功能丰富
- 支持数据导出/导入

**缺点：**

- 功能较多，界面稍显复杂

---

### 3.3 DataGrip

JetBrains DataGrip 是一款专业的数据库 IDE（付费）：

**安装方法：**

```bash
# 使用 Homebrew 安装（macOS）
brew install --cask datagrip

# 或从官网下载：https://www.jetbrains.com/datagrip/download/
```

**备份方式：**

1. 右键数据库 →「Dump to File」导出
2. 使用 Database Diff 进行数据库同步备份

**特点：**

- 强大的 SQL 编辑和调试功能
- 支持多数据库管理
- 与 JetBrains 全家桶集成良好

---

### 3.4 HeidiSQL

HeidiSQL 主要用于 MySQL/MariaDB，但也支持 PostgreSQL：

**备份：**

- 右键数据库 →「导出数据库为 SQL」
- 支持自定义导出选项

**特点：**

- 免费、轻量级
- Windows 专用

---

### 3.5 phpPgAdmin

基于 Web 的 PostgreSQL 管理工具：

**特点：**

- 浏览器访问，无需安装客户端
- 适合服务器管理
- 功能相对基础

---

### 3.6 Adminer

轻量级单文件数据库管理工具：

**特点：**

- 仅一个 PHP 文件，非常轻量
- 支持 PostgreSQL、MySQL、MongoDB 等
- 可直接通过 Web 访问

---

### 3.7 工具对比

| 工具 | 类型 | 价格 | 跨平台 | 特点 |
|------|------|------|--------|------|
| **Navicat** | 桌面应用 | 付费 | Windows/macOS/Linux | 功能全面，界面美观 |
| **pgAdmin** | 桌面应用 | 免费 | 全平台 | 官方推荐，功能强大 |
| **DBeaver** | 桌面应用 | 免费 | 全平台 | 开源社区活跃 |
| **DataGrip** | IDE | 付费 | 全平台 | 开发者友好 |
| **HeidiSQL** | 桌面应用 | 免费 | Windows | 轻量级 |
| **phpPgAdmin** | Web 应用 | 免费 | 全平台 | 无需安装客户端 |
| **Adminer** | Web 应用 | 免费 | 全平台 | 极轻量级 |

---

### 3.8 命令行工具补充

除了图形化工具，以下命令行工具也非常有用：

**pg_dumpall**（已介绍）：备份所有数据库

```bash
pg_dumpall -h localhost -U postgres > all.sql
```

**psql**（已介绍）：恢复 SQL 文件

```bash
psql -h localhost -U postgres -d mydb < backup.sql
```

**pg_basebackup**：物理备份（完整数据库复制）

```bash
# 创建物理备份
pg_basebackup -h localhost -U postgres -D /backup/base -Ft -z -P

# 恢复物理备份
pg_restore -d postgres /backup/base
```

**Barman**：企业级备份管理工具

```bash
# 配置备份服务器
barman check pg_server
barman backup pg_server
barman recover pg_server latest /var/lib/postgresql/data
```

---

## 四、Navicat 图形化备份

Navicat 是一款流行的数据库管理工具，支持 MySQL、PostgreSQL、SQL Server、Oracle 等多种数据库，提供直观的图形界面进行备份操作。

**安装方法：**

```bash
# 使用 Homebrew 安装 Navicat Premium（macOS）
brew install --cask navicat-premium

# 或安装 Navicat for PostgreSQL 专用版
brew install --cask navicat-for-postgresql

# 或从官网下载：https://www.navicat.com.cn/download/navicat-premium
```

### 4.1 PostgreSQL 备份

1. **连接数据库**：在左侧连接列表中选择 PostgreSQL 连接
2. **开始备份**：
   - 右键点击目标数据库 → 选择「备份数据库」
   - 或菜单栏选择「工具」→「备份数据库」
3. **配置备份选项**：
   - 选择备份格式（建议选择「自定义」格式）
   - 可选择要包含的对象（表、视图、函数等）
4. **保存备份**：点击「开始」后选择保存位置

### 4.2 MySQL 备份

1. **连接数据库**：在左侧连接列表中选择 MySQL 连接
2. **数据同步（迁移备份）**：
   - 菜单栏选择「工具」→「数据同步」
   - 源选择当前数据库
   - 目标选择文件或另一个数据库
3. **导出数据库**：
   - 右键数据库 →「转储 SQL 文件」→「结构和数据」或「仅结构」
   - 自动生成 .sql 文件保存到本地

### 4.3 定时自动备份（Navicat Premium）

Navicat Premium 支持定时任务自动备份：

1. **新建批处理作业**：
   - 菜单栏选择「工具」→「自动运行」或「计划」
   - 点击「新建批处理作业」
2. **添加备份任务**：
   - 从左侧拖拽「备份」任务到右侧流程区
   - 选择连接和数据库
3. **配置定时计划**：
   - 勾选「计划」选项卡
   - 设置执行频率（每天、每周等）
   - 设置执行时间
4. **保存并启用**：
   - 保存批处理作业
   - 勾选「启用」启动定时任务

### 4.4 Navicat Cloud 备份

Navicat Cloud 提供云端备份同步功能：

1. **登录 Navicat Cloud**：
   - 菜单栏「文件」→「登录 Navicat Cloud」
   - 输入账号密码
2. **同步备份**：
   - 右键数据库 →「备份到 Navicat Cloud」
   - 或通过「工具」→「同步」上传备份
3. **恢复云端备份**：
   - 从 Navicat Cloud 下载备份文件
   - 恢复到本地数据库

### 4.5 Navicat 恢复数据库

备份的最终目的是恢复，Navicat 提供了便捷的恢复功能：

**PostgreSQL 恢复步骤：**

1. 右键点击目标数据库 → 选择「还原数据库」
2. 选择备份文件（.backup 或 .dump 格式）
3. 配置恢复选项：
   - **仅还原结构**：只恢复表结构，不恢复数据
   - **仅还原数据**：只恢复数据，表结构需已存在
   - **结构和数据**：完整恢复（推荐）
4. 点击「开始」执行恢复

**MySQL 恢复步骤：**

1. **运行 SQL 文件**：
   - 右键目标数据库 →「运行 SQL 文件」
   - 选择之前导出的 .sql 备份文件
   - 执行导入

2. **数据同步恢复**：
   - 菜单栏「工具」→「数据同步」
   - 源选择备份文件或备份库
   - 目标选择要恢复的数据库
   - 执行同步

**恢复注意事项：**

| 场景 | 注意事项 |
|------|---------|
| **覆盖恢复** | 确保目标库已清空或删除，避免数据冲突 |
| **部分恢复** | 可选择仅恢复特定表，减少恢复时间 |
| **跨版本恢复** | 高版本备份可能无法恢复到低版本数据库 |
| **字符集问题** | 确保备份和恢复使用相同字符集，避免乱码 |

### 4.6 Navicat 备份注意事项

| 注意事项 | 说明 |
|---------|------|
| **备份位置** | 建议保存到非系统盘，避免系统崩溃丢失 |
| **文件命名** | 包含日期时间，便于追溯（如 `mydb_20260528.sql`） |
| **定期检查** | 定期验证备份文件能否正常恢复 |
| **大数据库** | 超大数据库建议使用命令行工具，性能更优 |
| **密码保护** | 敏感数据库建议设置备份文件密码 |

---

## 五、自动化备份脚本

### 5.1 PostgreSQL 自动备份脚本

```bash
#!/bin/bash
# pg_backup.sh - PostgreSQL 自动备份脚本

# 配置变量
PG_HOST="localhost"
PG_USER="postgres"
PG_PORT="5432"
BACKUP_DIR="/backup/postgresql"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 获取所有数据库列表
DATABASES=$(psql -h $PG_HOST -U $PG_USER -p $PG_PORT -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;")

# 遍历备份每个数据库
for DB in $DATABASES; do
    DB=$(echo $DB | tr -d ' ')
    if [ -n "$DB" ]; then
        echo "正在备份数据库: $DB"
        pg_dump -h $PG_HOST -U $PG_USER -p $PG_PORT -d $DB -Fc > "$BACKUP_DIR/${DB}_${DATE}.dump"
    fi
done

# 清理过期备份
find $BACKUP_DIR -name "*.dump" -mtime +$RETENTION_DAYS -delete

echo "备份完成！"
```

### 5.2 MySQL 自动备份脚本

```bash
#!/bin/bash
# mysql_backup.sh - MySQL 自动备份脚本

# 配置变量
MYSQL_HOST="localhost"
MYSQL_USER="root"
MYSQL_PASS="your_password"
BACKUP_DIR="/backup/mysql"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 获取所有数据库列表
DATABASES=$(mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASS -e "SHOW DATABASES;" | grep -v Database | grep -v information_schema | grep -v performance_schema)

# 遍历备份每个数据库
for DB in $DATABASES; do
    echo "正在备份数据库: $DB"
    mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASS \
        --single-transaction --routines --triggers --events \
        $DB | gzip > "$BACKUP_DIR/${DB}_${DATE}.sql.gz"
done

# 清理过期备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "备份完成！"
```

### 5.3 配置定时任务

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点执行备份
0 2 * * * /scripts/pg_backup.sh >> /var/log/pg_backup.log 2>&1
0 2 * * * /scripts/mysql_backup.sh >> /var/log/mysql_backup.log 2>&1
```

---

## 六、云存储备份

### 5.1 上传到 AWS S3

```bash
#!/bin/bash
# upload_to_s3.sh

BACKUP_DIR="/backup/postgresql"
S3_BUCKET="s3://your-bucket/database-backups"
DATE=$(date +%Y%m%d)

# 同步备份文件到 S3
aws s3 sync $BACKUP_DIR $S3_BUCKET/$DATE/ \
    --storage-class STANDARD_IA \
    --delete

# 设置生命周期规则自动清理旧备份（在 S3 控制台配置）
```

### 5.2 上传到 Cloudflare R2

```bash
# 使用 rclone 同步到 R2
rclone sync /backup/postgresql r2:your-bucket/database-backups/$(date +%Y%m%d)/
```

---

## 七、备份策略最佳实践

### 6.1 备份类型对比

| 类型 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| **全量备份** | 备份所有数据 | 恢复简单快速 | 占用空间大，耗时长 |
| **增量备份** | 仅备份变化数据 | 占用空间小 | 恢复需要全量+所有增量 |
| **差异备份** | 备份自上次全量后的变化 | 恢复比增量快 | 比增量占用更多空间 |

### 6.2 推荐策略

```
生产环境推荐备份策略：

┌─────────────────────────────────────────────────────┐
│  周日：全量备份                                      │
│  周一~周六：增量备份                                 │
│  保留周期：至少 4 周                                 │
│  异地备份：同步到云存储（S3/R2/OSS）                 │
│  恢复演练：每月至少 1 次                            │
└─────────────────────────────────────────────────────┘
```

### 6.3 备份验证清单

- [ ] 备份文件是否完整生成
- [ ] 备份文件大小是否合理
- [ ] 备份是否按时执行（检查 cron 日志）
- [ ] 异地备份是否同步成功
- [ ] 定期进行恢复演练

---

## 八、数据恢复（命令行）

命令行恢复是生产环境中最重要的技能，本节详细介绍 PostgreSQL 和 MySQL 的恢复操作。

### 7.1 PostgreSQL 恢复详解

**基础恢复命令：**

```bash
# 恢复 SQL 格式备份（纯文本）
psql -h localhost -U postgres -d mydb < backup.sql

# 恢复自定义格式备份（.dump 文件）
pg_restore -h localhost -U postgres -d mydb backup.dump

# 并行恢复（加快大数据库恢复速度）
pg_restore -h localhost -U postgres -d mydb -j 4 backup.dump
```

**创建新数据库恢复：**

```bash
# 1. 创建新数据库
createdb -h localhost -U postgres mydb_new

# 2. 恢复数据到新数据库
pg_restore -h localhost -U postgres -d mydb_new backup.dump
```

**恢复前清理目标库：**

```bash
# 如果目标库存在且要完全覆盖，先删除
dropdb -h localhost -U postgres mydb

# 重新创建数据库
createdb -h localhost -U postgres mydb

# 恢复数据
pg_restore -h localhost -U postgres -d mydb backup.dump
```

**选择性恢复（仅恢复指定表）：**

```bash
# 列出备份中的所有对象
pg_restore -l backup.dump

# 仅恢复特定表
pg_restore -h localhost -U postgres -d mydb -t users backup.dump
pg_restore -h localhost -U postgres -d mydb -t orders backup.dump

# 仅恢复存储过程
pg_restore -h localhost -U postgres -d mydb -P -t function_name backup.dump
```

**恢复前检查选项：**

```bash
# 先检查备份文件内容（不执行恢复）
pg_restore --help  # 查看所有选项

# 不带数据恢复（仅检查结构）
pg_restore -h localhost -U postgres -d mydb --schema-only backup.dump

# 恢复到另一个表空间
pg_restore -h localhost -U postgres -d mydb --tablespace=new_space backup.dump
```

### 7.2 MySQL 恢复详解

**基础恢复命令：**

```bash
# 恢复单个数据库
mysql -h localhost -u root -p mydb < backup.sql

# 恢复所有数据库（备份时包含 CREATE DATABASE 语句）
mysql -h localhost -u root -p < all_databases.sql

# 恢复压缩备份（gzip 格式）
gunzip < backup.sql.gz | mysql -h localhost -u root -p mydb

# 或使用 zcat
zcat backup.sql.gz | mysql -h localhost -u root -p mydb
```

**指定字符集恢复：**

```bash
# 如果有字符集问题，指定字符集
mysql -h localhost -u root -p --default-character-set=utf8mb4 mydb < backup.sql

# 或在 SQL 文件开头设置
mysql -h localhost -u root -p --init-command="SET NAMES utf8mb4" mydb < backup.sql
```

**覆盖恢复（先清空后导入）：**

```bash
# 1. 删除并重建数据库
mysql -h localhost -u root -p -e "DROP DATABASE IF EXISTS mydb; CREATE DATABASE mydb;"

# 2. 恢复数据
mysql -h localhost -u root -p mydb < backup.sql
```

**选择性恢复（仅恢复指定表）：**

```bash
# 方法1：使用 sed 提取指定表
sed -n '/DROP TABLE.*`表名`;/,/UNLOCK TABLES;/p' backup.sql > table.sql
mysql -h localhost -u root -p mydb < table.sql

# 方法2：使用 mysqlimport（需要先创建空表）
mysqlimport -h localhost -u root -p mydb table_data.txt

# 方法3：使用 mydumper 并行导出/导入指定表
mydumper -h localhost -u root -p -o /backup/tables -t users -t orders
myloader -h localhost -u root -p -d /backup/tables -o mydb
```

**表结构与数据分离恢复：**

```bash
# 仅恢复表结构
mysql -h localhost -u root -p mydb < schema.sql

# 仅恢复数据（表结构需已存在）
mysql -h localhost -u root -p mydb --init-command="SET foreign_key_checks=0; SET unique_checks=0; SET SESSION tx_isolation='READ-UNCOMMITTED';" < data.sql
```

### 7.3 恢复高级技巧

**时间点恢复（PITR）：**

PostgreSQL 支持基于时间点的恢复：

```bash
# 1. 停止 PostgreSQL
sudo systemctl stop postgresql

# 2. 备份当前数据目录
sudo cp -r /var/lib/postgresql/data /var/lib/postgresql/data.bak

# 3. 恢复到指定时间点
PGDATA=/var/lib/postgresql/data pg_restore -P --clean --create --dbname=postgres backup.dump

# 或编辑 postgresql.conf 设置恢复目标时间
# recovery_target_time = '2026-05-28 10:00:00'
```

MySQL binlog 恢复：

```bash
# 1. 确定恢复时间点
mysqlbinlog --start-datetime="2026-05-28 10:00:00" --stop-datetime="2026-05-28 12:00:00" mysql-bin.000001 > recovery.sql

# 2. 应用恢复
mysql -h localhost -u root -p mydb < recovery.sql
```

**增量备份恢复：**

```bash
# PostgreSQL WAL 归档恢复
# 1. 恢复基础全量备份
pg_restore -h localhost -U postgres -d postgres backup.dump

# 2. 应用 WAL 文件
psql -h localhost -U postgres -d mydb < 000000010000000000000001
psql -h localhost -U postgres -d mydb < 000000010000000000000002
```

**跨服务器恢复：**

```bash
# PostgreSQL：恢复远程数据库
pg_dump -h remote_host -U postgres -d mydb | pg_restore -h localhost -U postgres -d mydb

# MySQL：远程到本地
mysqldump -h remote_host -u root -p mydb | mysql -h localhost -u root -p mydb
```

### 7.4 恢复检查清单

执行恢复前务必检查以下项目：

| 检查项 | 操作 |
|--------|------|
| **备份文件完整性** | 检查文件大小和校验和 |
| **磁盘空间** | 确认目标磁盘有足够空间 |
| **数据库版本** | 确保备份和目标版本兼容 |
| **字符集** | 确认字符集设置一致 |
| **连接权限** | 确认恢复账号有足够权限 |
| **依赖关系** | 检查存储过程、触发器依赖 |
| **外键约束** | 恢复时关闭外键检查可加速 |

---

## 九、恢复演练

恢复演练是备份策略中**最容易被忽视但最重要**的环节！

### 9.1 演练脚本

```bash
#!/bin/bash
# restore_drill.sh - 恢复演练脚本

BACKUP_FILE="/backup/postgresql/mydb_20260528_020000.dump"
TEST_DB="mydb_drill_test"
PG_HOST="localhost"
PG_USER="postgres"

echo "=== 数据库恢复演练开始 ==="
echo "时间: $(date)"

# 1. 创建测试数据库
echo "1. 创建测试数据库: $TEST_DB"
dropdb -h $PG_HOST -U $POSTGRES_USER $TEST_DB 2>/dev/null || true
createdb -h $PG_HOST -U $PG_USER $TEST_DB

# 2. 执行恢复
echo "2. 执行恢复..."
pg_restore -h $PG_HOST -U $PG_USER -d $TEST_DB $BACKUP_FILE

# 3. 验证数据
echo "3. 验证数据完整性..."
TABLE_COUNT=$(psql -h $PG_HOST -U $PG_USER -d $TEST_DB -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "   恢复表数量: $TABLE_COUNT"

# 4. 清理测试数据库
echo "4. 清理测试数据库..."
dropdb -h $PG_HOST -U $PG_USER $TEST_DB

echo "=== 恢复演练完成 ==="
```

### 9.2 演练报告模板

```
数据库恢复演练报告
==================
日期：2026-05-28
演练人员：张三

备份文件：mydb_20260528_020000.dump
备份大小：1.2 GB

演练结果：
- 恢复耗时：3分28秒
- 表数量：45
- 数据完整性：✓ 通过
- 应用连接测试：✓ 通过

结论：备份有效，恢复流程正常。
```

---

## 十、常见问题

### Q1: 备份时数据库是否需要停服？

**不需要。** PostgreSQL 的 `pg_dump` 和 MySQL 的 `mysqldump --single-transaction` 都支持在线热备份，不会阻塞业务。

### Q2: 大数据库备份太慢怎么办？

- PostgreSQL：使用 `-j` 参数并行备份/恢复
- MySQL：考虑使用 `mydumper` 工具并行导出
- 超大数据库建议使用物理备份工具（pg_basebackup、XtraBackup）

### Q3: 如何备份 Docker 中的数据库？

```bash
# PostgreSQL
docker exec postgres pg_dump -U postgres mydb > backup.sql

# MySQL
docker exec mysql mysqldump -u root -pPassword mydb > backup.sql
```

---

## 总结

1. **备份是刚需**：没有备份的数据库就是在裸奔
2. **自动化是关键**：手动备份一定会被遗忘
3. **异地备份是保障**：服务器挂了，备份还在
4. **演练是验证**：没测试过的备份等于没有备份
5. **监控是补充**：备份失败要及时告警

记住：**数据无价，备份先行！**
