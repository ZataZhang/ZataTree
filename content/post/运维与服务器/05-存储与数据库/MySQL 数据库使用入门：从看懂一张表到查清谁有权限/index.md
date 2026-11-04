---
title: MySQL 数据库使用入门：从看懂一张表到查清谁有权限
description: "写给平时不怎么碰数据库的开发者：先分清表结构和数据，再学会安全地查询、多表关联、幂等脚本和事务，最后用一个真实形态的权限系统，把「数据库为什么能控制接口调用」讲清楚。文中 SQL 全部在 MySQL 8.0 上实测。"
date: 2026-11-03T14:30:00+08:00
slug: mysql-database-basics
image: images/index/index.svg
categories:
    - 运维与服务器
tags:
    - 存储与数据库
    - SQL
toc: true
draft: false
---

## 写这篇的起因

最近在后端项目里加了一个「AI Agent 配置」管理功能，上线前要在测试库执行一段 SQL。执行完 AI 回报说：「表已创建，4 个权限目录节点已写入。」我打开数据库客户端，看到了一张表的字段列表，却找不到所谓的数据，也不明白往表里插 4 行字为什么就能控制后端接口谁能调。

这篇把那次摸索整理成一份入门：

1. 数据库里到底有什么，表结构和数据怎么区分；
2. 怎么连、怎么查，哪些操作危险；
3. 多张表怎么关联起来回答一个业务问题；
4. 发布脚本为什么要写成能重复执行；
5. 用一个权限系统的完整例子，把「数据库控制接口调用」讲透。

文中所有示例 SQL 都在一个临时的 MySQL 8.0 容器里跑过，贴出来的结果就是实际输出。表名和数据做了脱敏，但结构和真实项目一致。

---

## 一、先建立正确的心智模型

### 1.1 库、表、行、列

可以先拿 Excel 类比：

| 数据库概念 | Excel 类比 | 说明 |
|---|---|---|
| 数据库服务器（实例） | 一台装了 Excel 的电脑 | 一个 MySQL 进程，有地址和端口 |
| 库（database / schema） | 一个 .xlsx 文件 | 比如测试库 `app_test`、生产库 `app_prod` |
| 表（table） | 文件里的一个 sheet | 比如 `agent_config` |
| 列（column / field） | 表头的一列 | 比如 `agent_id`、`enabled` |
| 行（row / record） | 一行数据 | 一条具体的配置 |

和 Excel 最大的不同是：**数据库的列是事先定死的**。每一列有类型、长度、能不能为空，写错类型的数据会被直接拒绝。这份「事先定死的规则」就是表结构。

### 1.2 表结构 vs 数据：我第一次就看错了

数据库客户端（Navicat、DBeaver、DataGrip 都一样）打开一张表时通常有两种视图：

- **设计 / 结构视图**（Navicat 里叫 Design Table，标签页是 Fields、Indexes、Comment……）：显示这张表有哪些列、什么类型、有哪些索引。这里**永远看不到数据**。
- **数据视图**（双击表名打开的那个网格）：显示表里实际存了哪些行。

我当时看到的是 Fields 标签页，一行一行列着 `id / agent_id / company_id …`，误以为那就是数据。其实那是「列的定义」，相当于 Excel 的表头说明。

用 SQL 也能分别看这两样：

```sql
-- 看结构：有哪些列
DESCRIBE agent_config;

-- 看数据：有哪些行
SELECT * FROM agent_config;
```

`DESCRIBE` 的输出：

```text
+--------------------+---------------+------+-----+---------+----------------+
| Field              | Type          | Null | Key | Default | Extra          |
+--------------------+---------------+------+-----+---------+----------------+
| id                 | bigint        | NO   | PRI | NULL    | auto_increment |
| agent_id           | varchar(100)  | NO   | MUL | NULL    |                |
| company_id         | varchar(100)  | NO   |     | NULL    |                |
| card_url           | varchar(2048) | NO   |     | NULL    |                |
| api_key_ciphertext | varchar(2048) | NO   |     | NULL    |                |
| enabled            | tinyint(1)    | NO   |     | 1       |                |
| create_time        | datetime      | NO   |     | NULL    |                |
| update_time        | datetime      | NO   |     | NULL    |                |
+--------------------+---------------+------+-----+---------+----------------+
```

另外，一张刚建好的表**本来就是空的**。它要等业务代码或者管理接口往里写，才会有数据。看到 0 行不一定是出错了。

### 1.3 读懂一份建表语句

下面这段是示例里的 Agent 配置表，几乎每个关键字都值得认识一下：

```sql
CREATE TABLE agent_config (
    id                 BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
    agent_id           VARCHAR(100)  NOT NULL COMMENT 'Agent 别名',
    company_id         VARCHAR(100)  NOT NULL COMMENT '公司',
    card_url           VARCHAR(2048) NOT NULL COMMENT 'Agent 地址',
    api_key_ciphertext VARCHAR(2048) NOT NULL COMMENT '加密后的 API Key',
    enabled            TINYINT(1)    NOT NULL DEFAULT 1 COMMENT '是否启用',
    create_time        DATETIME      NOT NULL COMMENT '创建时间（UTC）',
    update_time        DATETIME      NOT NULL COMMENT '更新时间（UTC）',
    PRIMARY KEY (id),
    UNIQUE KEY uk_agent_company (agent_id, company_id),
    KEY idx_agent_enabled (agent_id, enabled)
) ENGINE=InnoDB COMMENT='Agent 配置';
```

**常见列类型**

| 类型 | 存什么 | 注意 |
|---|---|---|
| `BIGINT` | 64 位整数 | 主键常用。很多项目用「雪花 ID」，是一串 19 位左右的数字 |
| `INT` | 32 位整数 | 层级、排序号这类小数字 |
| `TINYINT(1)` | 0~255 的小整数 | MySQL 没有真正的布尔类型，惯例用它存 0/1 |
| `VARCHAR(n)` | 最长 n 个字符的字符串 | n 是上限，不是固定长度；超长会报错或被截断 |
| `DATETIME` | 日期时间 | **不带时区**。存的是 UTC 还是北京时间，要看项目约定和列注释 |
| `DECIMAL(p,s)` | 精确小数 | 金额必须用它，不要用 `FLOAT/DOUBLE` |
| `TEXT` | 长文本 | 不能有默认值，也不适合建普通索引 |

**列上的约束**

- `NOT NULL`：这一列必须有值。
- `DEFAULT 1`：插入时没给值就用 1。
- `AUTO_INCREMENT`：插入时自动生成递增 id。
- `COMMENT`：列说明。看不懂一列时，第一件事就是看它的注释。

**键和索引**

- `PRIMARY KEY (id)`：主键，每行唯一的身份证，不能重复、不能为空。
- `UNIQUE KEY uk_agent_company (agent_id, company_id)`：唯一约束。这里的意思是「同一个 Agent 在同一家公司只能有一条配置」，重复插入会直接报错。**业务规则写进了表结构**，这是数据库帮你兜底的地方。
- `KEY idx_agent_enabled (agent_id, enabled)`：普通索引，只为了查得快，不限制数据。第七节专门讲。

`DESCRIBE` 输出里 `Key` 列的 `PRI` 表示主键，`MUL` 表示这列是某个非唯一索引（或联合索引）的第一列。

**表级选项**

- `ENGINE=InnoDB`：存储引擎。InnoDB 支持事务和行锁，现在基本都用它。
- `CHARSET=utf8mb4`：字符集。一定用 `utf8mb4`，MySQL 里名叫 `utf8` 的那个其实存不了 emoji 和部分生僻字。

---

## 二、连接数据库：先想清楚连的是哪个库

### 2.1 连接需要哪些信息

无论用什么客户端，连接都要这几项：

| 参数 | 例子 | 说明 |
|---|---|---|
| Host | `10.0.0.12` | 数据库服务器地址 |
| Port | `3306` | MySQL 默认端口 |
| User / Password | `readonly_user` | 账号密码 |
| Database | `app_test` | 默认进入的库，可以不填 |

在微服务项目里，这些信息通常**不写在代码仓库里**，而是放在配置中心（Nacos、Apollo、K8s Secret 等）。想知道服务连的是哪个库，去配置中心看对应服务的数据源配置。

### 2.2 测试库和生产库要从视觉上区分开

最常见的事故不是 SQL 写错，而是**在生产库上执行了本该在测试库执行的 SQL**。几个简单的习惯：

- 在客户端里给生产连接设成醒目的颜色（Navicat、DBeaver 都支持连接着色），名字前加 `【PROD】`。
- 日常排查用**只读账号**。只读账号从根上杜绝误删误改。
- 执行脚本前先 `SELECT DATABASE();` 确认当前所在的库。脚本开头写 `USE app_test;` 也是同样的目的。

### 2.3 命令行连接

```bash
mysql -h 10.0.0.12 -P 3306 -u readonly_user -p app_test
# 回车后输入密码；不要把密码直接写在 -p 后面，否则会留在 shell 历史里
```

---

## 三、查询：只读，放心大胆地练

`SELECT` 不改数据，是最安全的操作，也是最常用的。

### 3.1 基本形状

```sql
SELECT 列1, 列2        -- 要哪些列；* 表示全部
  FROM 表名
 WHERE 条件            -- 过滤行
 ORDER BY 列 [DESC]    -- 排序
 LIMIT 20;             -- 最多返回多少行
```

例子：查出 Agent 配置相关的所有权限码，按路径排序：

```sql
SELECT code, name, path
  FROM permission_catalog
 WHERE code LIKE 'ai_agent_config%'
 ORDER BY path;
```

```text
+-------------------------------+------------------------+--------------------------------------------------------------+
| code                          | name                   | path                                                         |
+-------------------------------+------------------------+--------------------------------------------------------------+
| ai_agent_config               | AI Agent Configuration | /configuration/ai_agent_config                               |
| ai_agent_config_edit          | Edit                   | /configuration/ai_agent_config/ai_agent_config_edit          |
| ai_agent_config_module_access | Module Access          | /configuration/ai_agent_config/ai_agent_config_module_access |
| ai_agent_config_new           | New                    | /configuration/ai_agent_config/ai_agent_config_new           |
+-------------------------------+------------------------+--------------------------------------------------------------+
```

### 3.2 WHERE 的常用写法

```sql
WHERE enabled = 1                        -- 等于
WHERE enabled <> 1                       -- 不等于
WHERE company_id IN ('C001', 'C002')     -- 在列表里
WHERE code LIKE 'ai_agent%'              -- 以 ai_agent 开头；% 是任意字符
WHERE create_time >= '2026-11-01'        -- 时间比较
WHERE parent_id IS NULL                  -- 为空，注意不能写 = NULL
WHERE enabled = 1 AND agent_id = 'x'     -- 组合条件；AND、OR 混用时记得加括号
```

### 3.3 第一个陷阱：NULL 不能用等号

`NULL` 表示「未知」，任何东西和它比较的结果都是「未知」，所以 `= NULL` 永远匹配不到：

```sql
SELECT COUNT(*) FROM permission_catalog WHERE parent_id = NULL;   -- 0
SELECT COUNT(*) FROM permission_catalog WHERE parent_id IS NULL;  -- 1
```

同理，`WHERE status <> 'DONE'` 也**不会**返回 `status` 为 NULL 的行。查「不是某个值」时，要想一想 NULL 的行该不该算进去。

### 3.4 统计：COUNT 与 GROUP BY

```sql
-- 每个父节点下面有几个子节点
SELECT parent_id, COUNT(*) AS children
  FROM permission_catalog
 WHERE parent_id IS NOT NULL
 GROUP BY parent_id;
```

```text
+-----------+----------+
| parent_id | children |
+-----------+----------+
|         1 |        2 |
|         2 |        3 |
+-----------+----------+
```

`GROUP BY` 把行按某一列分组，再对每组做 `COUNT / SUM / MAX` 这类聚合。

### 3.5 查询时的好习惯

- **大表先加 `LIMIT`**。生产上几千万行的表，一个不带条件的 `SELECT *` 能把客户端卡死，还会给数据库加压。
- **只取需要的列**，尤其不要随手把密钥、手机号这类敏感列查出来、截图、贴到聊天群里。示例表里的 `api_key_ciphertext` 虽然是密文，也没必要出现在日常查询结果里。
- 时间列先看注释是 UTC 还是本地时间。北京时间比 UTC 快 8 小时，按日期筛选时最容易差一天。

---

## 四、多表关联：业务问题通常要跨好几张表

一张表只存一类东西。像「谁能新增 Agent 配置」这种问题，答案散落在好几张表里，要用 `JOIN` 拼起来。

### 4.1 示例的数据模型

这是一个很典型的「权限目录 + 用户组授权」模型：

```text
staff（员工）
   │ 多对多
group_member（组成员）
   │
user_group（用户组）
   │ 一对多
group_permission（组授权：组 + 权限码 + 允许/拒绝）
   │ 通过 permission_code 对应
permission_catalog（权限目录：一棵树，只定义有哪些权限码）
```

为什么要中间表 `group_member`？因为一个人可以在多个组，一个组也有多个人，这种**多对多关系**必须拆一张单独的表来存，每行记一对「谁在哪个组」。

### 4.2 INNER JOIN：两边都匹配上才保留

```sql
SELECT s.username, g.name AS group_name, p.permission_code, p.is_allowed
  FROM staff s
  JOIN group_member m     ON m.staff_id = s.id
  JOIN user_group g       ON g.id = m.group_id AND g.is_active = 1
  JOIN group_permission p ON p.group_id = g.id
 ORDER BY s.username;
```

```text
+----------+---------------+-------------------------------+------------+
| username | group_name    | permission_code               | is_allowed |
+----------+---------------+-------------------------------+------------+
| alice    | IT Admin      | configuration                 |          1 |
| bob      | AI Maintainer | ai_agent_config_module_access |          1 |
| carol    | Finance       | currency                      |          1 |
+----------+---------------+-------------------------------+------------+
```

读法：从员工出发，经过组成员找到组，再从组找到它的授权。`s`、`m`、`g`、`p` 是表的别名，写起来短一些。`ON` 后面写两张表靠哪一列对上。

注意 `root` 不在结果里，因为他没有加入任何组，第一步 JOIN 就被筛掉了。

### 4.3 LEFT JOIN：左边全保留，右边没有就填 NULL

```sql
SELECT s.username, m.group_id
  FROM staff s
  LEFT JOIN group_member m ON m.staff_id = s.id
 ORDER BY s.username;
```

```text
+----------+----------+
| username | group_id |
+----------+----------+
| alice    | G1       |
| bob      | G2       |
| carol    | G3       |
| root     | NULL     |
+----------+----------+
```

**怎么选**：想找「两边都有的」用 `JOIN`；想找「左边所有的，顺带看看右边有没有」，或者想专门找「右边没有的」（加 `WHERE m.group_id IS NULL`），用 `LEFT JOIN`。

### 4.4 树形数据：怎么找出一个节点的所有祖先

权限目录是一棵树：

```text
configuration                          （level 1）
├─ currency                            （level 2）
└─ ai_agent_config                     （level 2）
   ├─ ai_agent_config_module_access    （level 3）
   ├─ ai_agent_config_new              （level 3）
   └─ ai_agent_config_edit             （level 3）
```

树在数据库里常见两种存法，示例表两种都存了：

- `parent_id`：每个节点记住自己的父节点 id；
- `path`：把从根到自己的整条路径拼成字符串，比如 `/configuration/ai_agent_config/ai_agent_config_new`。

**方法一：利用 path 前缀**。祖先的 path 一定是自己 path 的前缀：

```sql
SELECT a.code
  FROM permission_catalog t
  JOIN permission_catalog a
    ON t.path = a.path OR t.path LIKE CONCAT(a.path, '/%')
 WHERE t.code = 'ai_agent_config_new'
 ORDER BY a.level;
```

这里同一张表 JOIN 了自己（自关联），`t` 是目标节点，`a` 是候选祖先。拼接 `'/%'` 而不是 `'%'`，是为了避免 `/configuration/ai` 错误匹配到 `/configuration/ai_agent_config`。

**方法二：递归 CTE（MySQL 8.0+）**，顺着 `parent_id` 一级一级往上走：

```sql
WITH RECURSIVE chain AS (
    SELECT id, parent_id, code, level
      FROM permission_catalog
     WHERE code = 'ai_agent_config_new'      -- 起点
    UNION ALL
    SELECT p.id, p.parent_id, p.code, p.level
      FROM permission_catalog p
      JOIN chain c ON p.id = c.parent_id      -- 每次找上一级
)
SELECT code, level FROM chain ORDER BY level;
```

两种方法结果相同：

```text
+---------------------+-------+
| code                | level |
+---------------------+-------+
| configuration       |     1 |
| ai_agent_config     |     2 |
| ai_agent_config_new |     3 |
+---------------------+-------+
```

这条祖先链在下一节的权限判断里是关键。

---

## 五、案例：数据库为什么能「控制」接口调用

这是我最初最困惑的地方。答案是：**拦截请求的是后端代码，数据库里存的是「谁被允许」这份名单**。

### 5.1 代码里声明「需要什么」

后端接口上加一个注解，写明调用它需要的权限码。以 Java / Spring 项目为例：

```java
@PostMapping("/agents/configurations")
@RequireRight("ai_agent_config_new")       // 需要「新增」权限
public R<AgentConfigurationVO> create(@RequestBody AgentConfigurationCreateRequest request) {
    ...
}
```

框架用 AOP 切面在进入方法前先拦一下：

```text
请求进来
  │
  ▼
切面读取注解上的权限码 "ai_agent_config_new"
  │
  ▼
问权限服务：当前登录用户有没有这个码？
  │                 └── 权限服务去查数据库里的授权表
  ├── 有 → 执行业务方法
  └── 没有 → 返回 403 "You do not have permission to perform this operation."
```

这种模式很通用：Spring Security 写作 `@PreAuthorize("hasAuthority('...')")`，Shiro 写作 `@RequiresPermissions("...")`，思想都是 **RBAC（基于角色的访问控制）**：代码只声明需要什么，谁拥有什么放在数据里。好处是开通或收回权限只需要改数据，不用改代码、不用发版。

### 5.2 数据库里存「谁被允许」，分两层

1. **权限目录 `permission_catalog`**：定义系统里有哪些权限码，是一份清单。管理界面的权限树就按它展示。上线时那 4 行 INSERT 就写在这一层，所以执行完以后，管理员才能在界面上找到这几个权限并勾选。
2. **授权数据 `group_permission` 等**：记录哪个组拥有哪个权限码。真正判断时查的是这一层。

所以只插了目录、没做授权时，这几个权限对绝大多数人来说就是「存在但没人有」。

### 5.3 两条容易忽略的规则：继承和超管

实际系统里，判断「有没有 `ai_agent_config_new`」时，一般不只看这一个码，还会看它的**整条祖先链**：

- 被授予 `configuration`（整个配置目录）的组，自动拥有下面所有子权限，包括这次新加的；
- 很多系统还有**超级管理员**标记，直接跳过判断。

这两条会让「新权限还没授给任何人」这个直觉出错。把它们写成一条 SQL，问「谁现在能新增 Agent 配置」：

```sql
SELECT DISTINCT s.username,
       CONCAT('via ', g.name, ' -> ', p.permission_code) AS reason
  FROM staff s
  JOIN group_member m     ON m.staff_id = s.id
  JOIN user_group g       ON g.id = m.group_id AND g.is_active = 1
  JOIN group_permission p ON p.group_id = g.id AND p.is_allowed = 1
 WHERE s.is_active = 1
   AND p.permission_code IN ('configuration', 'ai_agent_config', 'ai_agent_config_new')  -- 祖先链
UNION
SELECT username, 'super admin'
  FROM staff
 WHERE is_super_admin = 1 AND is_active = 1
 ORDER BY username;
```

```text
+----------+-------------------------------+
| username | reason                        |
+----------+-------------------------------+
| alice    | via IT Admin -> configuration |
| root     | super admin                   |
+----------+-------------------------------+
```

解读：

- `alice` 所在的 IT Admin 组被授予了整个 `configuration`，于是**自动继承**了这次新加的新增权限，虽然没人专门给过她。
- `root` 是超管，直接放行。
- `bob` 只有 `ai_agent_config_module_access`（查看），不在祖先链里，所以不能新增。
- `carol` 只有 `currency`，和这条链无关。

`UNION` 把两段查询的结果上下拼在一起并去重；`UNION ALL` 不去重，更快。

> 这个例子是简化版。真实系统里通常还有「拒绝优先」「按公司/分公司/部门维度生效」等规则。判断时一定要以权限服务的代码为准，SQL 只是帮你排查、核对。

如果权限里包含能看到或修改密钥这类敏感操作，上线前应该专门用类似的查询核对一遍：**继承过来的人里，有没有不该有的？**

---

## 六、修改数据：先 SELECT，再动手

`INSERT / UPDATE / DELETE` 会改数据，是事故高发区。

### 6.1 三条铁律

1. **先用同样的 WHERE 跑一遍 SELECT**，确认影响的行数和内容符合预期，再把 `SELECT ... FROM` 换成 `UPDATE ... SET` 或 `DELETE FROM`。
2. **永远不要漏写 WHERE**。`UPDATE agent_config SET enabled = 0;` 会把整张表都改掉。MySQL 客户端可以开启 `SET SQL_SAFE_UPDATES = 1;`，没有带键条件的 UPDATE/DELETE 会被直接拒绝。
3. **生产上的写操作要有审批、有回滚方案**。数据库没有回收站。

### 6.2 事务：给自己留一个反悔的机会

事务把多条语句打包成一个整体，要么全部生效（`COMMIT`），要么全部撤销（`ROLLBACK`）：

```sql
START TRANSACTION;

UPDATE agent_config SET enabled = 0;     -- 故意漏了 WHERE
SELECT ROW_COUNT();                       -- 看看影响了几行：1（C001 由 1 改成 0；C002 本来就是 0，不计入）

ROLLBACK;                                 -- 发现不对，撤销

SELECT company_id, enabled FROM agent_config;
```

```text
+------------+---------+
| company_id | enabled |
+------------+---------+
| C001       |       1 |
| C002       |       0 |
+------------+---------+
```

数据回到了原样。几点要注意：

- 很多客户端默认是**自动提交（autocommit）**，每条语句执行完立刻生效。手动改数据时，先 `START TRANSACTION`，检查无误再 `COMMIT`。
- 事务没提交前会持有锁，**不要开着事务去吃饭**，别的请求会被堵住。
- `CREATE TABLE`、`ALTER TABLE`、`DROP TABLE` 这类 DDL 在 MySQL 里会**隐式提交**，不能回滚。

### 6.3 DDL：改表结构比改数据更要小心

```sql
ALTER TABLE agent_config ADD COLUMN remark VARCHAR(500) NULL COMMENT '备注';  -- 加列
ALTER TABLE agent_config ADD KEY idx_company (company_id);                    -- 加索引
DROP TABLE agent_config;                                                       -- 删表，连数据一起没了
```

大表上的 `ALTER TABLE` 可能执行很久，期间还可能锁表。生产环境改表结构通常要挑低峰期，或者用 pt-online-schema-change、gh-ost 这类在线变更工具。

---

## 七、发布脚本：写成能重复执行的

上线 SQL 往往要在测试库、预发库、生产库各跑一遍，中途失败还可能要重跑。如果脚本第二次执行就报错，或者插出重复数据，就很麻烦。所以发布脚本要写成**幂等**的：执行一次和执行多次，结果一样。

### 7.1 常用的幂等写法

```sql
-- 建表：已存在就跳过
CREATE TABLE IF NOT EXISTS agent_config ( ... );

-- 插入：不存在才插
INSERT INTO permission_catalog (parent_id, code, name, level, path, sort)
SELECT p.id, 'ai_agent_config_delete', 'Delete', p.level + 1,
       CONCAT(p.path, '/ai_agent_config_delete'), 40
  FROM permission_catalog p
 WHERE p.code = 'ai_agent_config'
   AND NOT EXISTS (SELECT 1 FROM permission_catalog c WHERE c.code = 'ai_agent_config_delete');
```

实测连续执行两次这条 INSERT，`ROW_COUNT()` 分别是 `1` 和 `0`：第一次插入了，第二次因为已经存在，什么都没做。

这条语句还有一个巧妙之处：**父节点 id 不写死**，而是用 `SELECT p.id FROM ... WHERE p.code = 'ai_agent_config'` 现查。不同环境里同一个节点的 id 往往不一样，写死 id 很容易在某个环境挂错父节点。

### 7.2 一份合格发布脚本的样子

```sql
-- ## 2026-11-02 Agent 配置持久化
-- 说明：做什么、为什么、先跑 SQL 还是先发服务
USE app_test;

CREATE TABLE IF NOT EXISTS ...;          -- 1. 结构变更
INSERT ... WHERE NOT EXISTS (...);       -- 2. 基础数据，幂等

SELECT code, name, path                  -- 3. 执行后自检
  FROM permission_catalog
 WHERE code LIKE 'ai_agent_config%';

-- 回滚（注释状态，需要时手动执行）：
--   DELETE FROM permission_catalog WHERE code IN (...);
--   DROP TABLE agent_config;
```

要素：说明、指定库、幂等、带自检查询、写好回滚。

---

## 八、索引：为什么有的查询快、有的慢

### 8.1 索引是什么

索引就像书后面的关键词索引：不用一页页翻，直接按关键词跳到对应的页码。没有索引时，数据库只能**全表扫描**，一行一行地比。

### 8.2 用 EXPLAIN 看查询走没走索引

在查询前面加 `EXPLAIN`，数据库会告诉你它打算怎么执行，而不是真的执行：

```sql
EXPLAIN SELECT * FROM agent_config WHERE agent_id = 'doc-agent' AND enabled = 1;
```

```text
| type | possible_keys                      | key               | rows |
| ref  | uk_agent_company,idx_agent_enabled | idx_agent_enabled |    1 |
```

```sql
EXPLAIN SELECT * FROM agent_config WHERE enabled = 1;
EXPLAIN SELECT * FROM agent_config WHERE card_url LIKE '%example%';
```

```text
| type | possible_keys | key  | rows |
| ALL  | NULL          | NULL |    2 |
```

关注三列：

- `type`：`const` / `eq_ref` / `ref` / `range` 都算走了索引；**`ALL` 是全表扫描**，大表上要警惕。
- `key`：实际用了哪个索引，`NULL` 表示没用。
- `rows`：预计要扫描多少行。

### 8.3 最左前缀原则

联合索引 `idx_agent_enabled (agent_id, enabled)` 像电话簿：先按姓排，姓相同再按名排。

- 按 `agent_id` 查：能用（相当于按姓找）。
- 按 `agent_id` + `enabled` 查：能用。
- **只按 `enabled` 查：用不上**（只知道名不知道姓，电话簿帮不了你），所以上面第二个 EXPLAIN 是 `ALL`。

另外两种常见的「索引失效」：

- `LIKE '%xxx'`，以 `%` 开头的模糊查询用不上索引；`LIKE 'xxx%'` 可以。
- 在列上套函数，比如 `WHERE DATE(create_time) = '2026-11-03'`。改成 `WHERE create_time >= '2026-11-03' AND create_time < '2026-11-04'` 就能走索引。

小表（几百几千行）全表扫描也很快，不用为此焦虑；索引的价值在数据量大起来以后。

---

## 九、数据库和后端代码怎么配合

### 9.1 ORM 和 Mapper

后端很少手写 JDBC，一般用 MyBatis / MyBatis-Plus、JPA、SQLAlchemy 这类工具。表和代码的对应关系通常是：

```java
@TableName("agent_config")              // 实体类对应哪张表
public class AgentConfigEntity {
    private Long id;
    private String agentId;             // 驼峰字段 ↔ 下划线列名 agent_id
    private String apiKeyCiphertext;
    ...
}
```

想知道某张表被哪里用到，在代码里搜表名，找到 `@TableName` 或 Mapper XML 里的 SQL 就行。反过来，看到一个实体类，看它的 `@TableName` 就知道去哪张表查数据。

### 9.2 SQL 注入：`#{}` 和 `${}`

MyBatis 里有两种拼参数的方式：

```xml
WHERE code = #{code}     <!-- 预编译参数，安全 -->
WHERE code = '${code}'   <!-- 直接拼字符串，危险 -->
```

如果 `code` 来自用户输入，比如 `x' OR '1'='1`，第二种写法会变成 `WHERE code = 'x' OR '1'='1'`，条件恒真。这就是 SQL 注入。规则很简单：**参数一律用 `#{}`**，`${}` 只用于确实无法参数化、且值来自白名单的场景（比如排序列名）。

### 9.3 敏感数据：库里只存密文

示例表的 API Key 列叫 `api_key_ciphertext`，存的是 AES-GCM 加密后的密文，加密密钥放在单独受保护的配置里，不在库里。这样即使有人能读这张表（比如有只读账号的开发），也拿不到真正的 Key。

设计这类表时的原则：

- 密钥、密码、Token **不明文入库**。密码用单向哈希（bcrypt、argon2），需要还原的密钥用对称加密。
- 列名直接表明是密文，提醒后来的人不要把它当明文用。
- 查询接口返回给前端时**不回传**这一列，最多显示「已配置」。

---

## 十、常见坑速查

| 现象 | 原因 | 解决 |
|---|---|---|
| 打开表只看到列名，看不到数据 | 打开的是结构视图 | 切到数据视图，或 `SELECT * ... LIMIT 20` |
| `WHERE x = NULL` 查不到 | NULL 不能用等号比较 | 用 `IS NULL` / `IS NOT NULL` |
| 按日期查少了一天 | 列存的是 UTC，条件按北京时间写 | 先看列注释，换算时区 |
| emoji 存进去变成 `????` 或报错 | 字符集是 `utf8` 不是 `utf8mb4` | 表和连接都用 `utf8mb4` |
| `Duplicate entry ... for key 'uk_xxx'` | 违反唯一约束 | 先查是否已存在，或改用幂等写法 |
| `Data too long for column` | 超过 `VARCHAR(n)` 长度 | 检查数据，或评估加长列 |
| UPDATE 改了整张表 | 漏写 WHERE | 先 SELECT、用事务、开 `SQL_SAFE_UPDATES` |
| 别的请求一直卡住 | 有人开着事务没提交，锁住了行 | `SHOW PROCESSLIST` 找到会话，提交或回滚 |
| 查询很慢 | 全表扫描 | `EXPLAIN` 看 `type`，按最左前缀补索引 |
| 新权限「没授给任何人」却有人能用 | 继承了父节点授权，或者是超管 | 按祖先链和超管标记一起查 |

---

## 十一、命令速查

```sql
-- 环境
SELECT DATABASE();                       -- 当前在哪个库
SHOW DATABASES;                          -- 有哪些库
USE app_test;                            -- 切换库
SHOW TABLES;                             -- 当前库有哪些表
SHOW TABLES LIKE '%agent%';              -- 按名字找表

-- 结构
DESCRIBE agent_config;                   -- 列定义
SHOW CREATE TABLE agent_config;          -- 完整建表语句（含索引、注释）
SHOW INDEX FROM agent_config;            -- 索引

-- 按列名找表（不知道某个字段在哪张表时很好用）
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT
  FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = 'app_test' AND COLUMN_NAME LIKE '%agent%';

-- 查询
SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT 20;
SELECT col, COUNT(*) FROM t GROUP BY col;
EXPLAIN SELECT ...;

-- 修改（先 SELECT 确认）
START TRANSACTION;
UPDATE t SET col = v WHERE id = 1;
SELECT ROW_COUNT();
COMMIT;   -- 或 ROLLBACK;

-- 排查
SHOW PROCESSLIST;                        -- 当前有哪些连接在跑什么
```

---

## 写在最后

回头看最初那个问题：「4 个权限目录节点」其实就是权限目录表里的 4 行数据。它们本身不拦截任何请求，只是给后端代码里的 `@RequireRight("...")` 提供了一份可以被授予的权限清单。真正决定谁能调接口的，是授权表里的数据，加上继承和超管这两条规则。

对不常碰数据库的人来说，记住这几件事就够应付大部分场景：

1. 分清**结构**和**数据**，看不懂一列先看注释；
2. 先确认**连的是哪个库**，日常用只读账号；
3. 写操作**先 SELECT、再事务、最后提交**；
4. 发布脚本写成**幂等**，带自检和回滚；
5. 业务问题拆成「从哪张表出发、经过哪些表、靠哪一列对上」，再用 JOIN 拼起来。
