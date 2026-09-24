---
title: 通用模板规范GeneralTemplateSpecifications
description: ""
date: 2025-12-31T07:03:54+08:00
image: images/index/index.png
categories:
    - Grammar
tags:
    - general
---



# Template
## git commit 

Git commit 消息的格式有多种最佳实践，其中最流行和推荐的是 **Conventional Commits**（约定式提交）规范。这是一种轻量级的规范，能让 commit 历史更清晰、可读性强，便于自动化生成 changelog、语义化版本号（SemVer）等。

Conventional Commits 标准格式
基本结构：
```
<type>([optional scope]): <subject>

[optional body]

[optional footer(s)]
```

- **type**（必填）：提交类型，常见的有：
  - `feat`：新功能（feature）
  - `fix`：修复 bug
  - `docs`：文档修改
  - `style`：代码格式调整（不影响功能，如空格、缩进）
  - `refactor`：重构（既不是新功能也不是 bug 修复）
  - `perf`：性能优化
  - `test`：添加或修改测试
  - `build`：影响构建系统或外部依赖的变更（如 npm、gulp）
  - `ci`：CI 配置变更（如 GitHub Actions）
  - `chore`：其他杂项（不修改 src 或 test）

- **scope**（可选）：影响范围，用圆括号括起，例如 `(parser)` 或 `(login)`，表示修改了哪个模块。如果有多个模块涉及更改，以主范围为主，其他在正文中说明，以保持简洁和可读性。

- **subject**（必填）：简短描述，使用**祈使语气、现在时**（如 “添加” 而非 “添加了” 或 “添加过”），首字母小写（规范推荐），长度控制在 50 字符以内。

- **body**（可选）：详细说明，为什么修改、改了什么。换行分段，每行建议不超过 72 字符。用空行与 subject 分隔。

- **footer**（可选）：脚注，用于标注破坏性变更或关联 issue。
  - 破坏性变更：`BREAKING CHANGE: <描述>`（会导致 major 版本升级）
  - 关联 issue：`Closes #123` 或 `Refs #456`

 示例
1. 简单 commit：
   ```
   feat(login): 添加用户登录功能
   ```

2. 带 body 和 footer：
   ```
   fix(cache): 防止缓存数据过期

   使用请求 ID 来跟踪缓存有效性，移除旧的超时逻辑。

   BREAKING CHANGE: 移除旧 API 接口
   Closes #42
   ```

一般最佳实践（即使不严格用 Conventional Commits）
- 第一行（subject）不超过 50 字符。
- 用空行分隔 subject 和 body。
- body 每行不超过 72 字符。
- 使用祈使语气（Imperative mood）：如 “修复 bug” 而非 “修复了 bug”。
- 解释**为什么**修改，而不是只说**改了什么**（代码本身已显示改了什么）。
- 避免无意义消息如 “fix” 或 “update”。




## code comments 代码注释

好的代码注释是提升代码可读性、可维护性和团队协作的关键。注释的核心原则是：**解释“为什么”（Why），而不是重复“做什么”（What）**。如果通过良好的命名、结构和逻辑，代码已经足够自解释，则无需过多注释。

---

`通用注释原则（适用于所有语言）`

1. **注释目的**：解释复杂逻辑、设计决策、业务背景、潜在陷阱或历史原因。避免对明显代码重复解释（如 `i++ // i加1`）。

2. **注释风格**：

   - 简洁、准确、无歧义。

   - 与代码同步更新，杜绝过时注释。

   - 注释占比建议：普通代码 10%-20%，复杂逻辑可达 30%-50%。

3. **常见注释类型**：

   - 文件/模块头部注释：说明整体功能、作者、版本、版权等。

   - 类/结构体/模块注释：说明用途、设计思路。

   - 函数/方法注释：说明功能、参数、返回值、异常、调用示例。

   - 代码块注释：解释一段复杂逻辑的目的或算法。

   - 行内注释：谨慎使用，仅用于关键点或魔法数字。

4. **最佳实践**：

   - 优先使用可生成文档的注释格式（如 Docstring、Javadoc）。

   - 使用统一标记表示待办事项：

     - `TODO(作者): 说明待完成事项`

     - `FIXME(作者): 说明需要修复的问题`

     - `NOTE: 重要说明`

   - 修复 Bug 时，必须在相关位置注释原因及修复思路。

   - 避免大段注释块遮挡代码逻辑，必要时将复杂说明移至函数文档。


---

`文件头部注释模板（适用于大多数语言）`

```text

/**

 * 文件描述：简要描述本文件的主要功能和作用。

 *

 * @author 你的名字 <email@example.com>

 * @version 1.0.0

 * @create 2025-12-30

 * @update 2025-12-30: 初始版本

 *             xxxx-xx-xx: 修改内容简述

 *

 * Copyright (c) 2025 Your Company. All rights reserved.

 */

```

---

`函数/方法注释模板（推荐文档式注释）`

**Python（Google风格 Docstring）示例**：

```python

def calculate_user_score(user_id: int, include_bonus: bool = True) -> float:

    """

    计算用户综合评分。

    该函数根据用户历史行为、活跃度和奖励规则计算最终评分。

    评分公式经过多次 A/B 测试优化，当前权重为：活跃度 40%、成就 35%、奖励 25%。

    参数

    ----------

    user_id : int

        用户唯一 ID，必须存在于数据库中。

    include_bonus : bool, optional

        是否包含临时奖励加分（默认 True）。

    返回值

    -------

    float

        用户综合评分，范围 0.0 ~ 100.0。

    异常

    -----

    ValueError

        当 user_id 不存在或为负数时抛出。

    NotFoundError

        当用户数据未加载时抛出。

    示例

    --------

    >>> calculate_user_score(12345)

    87.5

    >>> calculate_user_score(12345, include_bonus=False)

    82.3

    注意

    ----

    该函数依赖缓存，缓存失效时会自动重新计算。

    """

```

**Java/JavaScript/TypeScript（Javadoc/JSDoc）示例**：

```java

/**

 * 计算用户综合评分。

 *

 * 该函数根据用户历史行为、活跃度和奖励规则计算最终评分。

 * 评分公式经过多次 A/B 测试优化，当前权重为：活跃度 40%、成就 35%、奖励 25%。

 *

 * @param userId 用户唯一 ID，必须存在于数据库中

 * @param includeBonus 是否包含临时奖励加分，默认 true

 * @return 用户综合评分，范围 0.0 ~ 100.0

 * @throws ValueError 当 userId 不存在或为负数时抛出

 * @throws NotFoundError 当用户数据未加载时抛出

 * @example

 *   calculateUserScore(12345) // 返回 87.5

 * @since 1.2.0

 */

public double calculateUserScore(int userId, boolean includeBonus = true) {

    // ...

}

```

---

`代码块与行内注释示例`

```python

# ==============================================================================

# 关键算法块：用户行为衰减权重计算

# 原因：近期行为对评分影响更大，使用指数衰减模型模拟“遗忘曲线”

# 公式：weight = base ^ (days_elapsed / half_life)

# ==============================================================================

for record in user_records:

    # 计算行为发生天数间隔（基于当前日期）

    days_elapsed = (current_date - record.timestamp).days

    

    # 半衰期为 30 天，即 30 天后权重减半

    weight = decay_base ** (days_elapsed / HALF_LIFE_DAYS)  # NOTE: decay_base < 1

    

    total_score += record.value * weight

```

---

`总结最佳实践`

- **第一行（函数/类总结）控制在 50-72 字符以内**，清晰表达核心目的。

- **用空行分隔总结与详细说明**。

- **详细说明解释“为什么”这样设计**，而非仅仅“做了什么”。

- **使用祈使语气或陈述事实**，保持专业、一致。

- **避免无意义注释**，如 “临时变量” 或 “循环”。

- **保持注释与代码同步**，这是最重要的一条。


## 数据库字段定义规范

良好的数据库字段定义规范能确保数据一致性、提升查询性能、便于维护和扩展，同时降低因字段命名或类型不统一导致的 Bug。以下是企业级项目中推荐的数据库字段定义最佳实践（适用于 MySQL、PostgreSQL、Oracle 等关系型数据库）。

---

`通用原则`
1. **命名规范**
   - 使用**小写字母 + 下划线**（snake_case），禁止驼峰命名。
   - 字段名必须**语义明确、见名知意**，避免缩写，除非是公认缩写（如 `id`、`url`、`ip`）。
     - 推荐：`user_name`、`order_status`、`created_at`
     - 避免：`uname`、`stat`、`cts`
   - 业务相关字段需体现业务含义，例如：
     - `is_deleted` 而非 `del_flag`
     - `order_amount` 而非 `money`
   - 布尔类型字段以 `is_xxx` 开头（如 `is_vip`、`is_deleted`）。
   - 外键字段命名：`xxx_id`（如 `user_id`、`order_id`）。
   - 统一前缀避免冲突（如多表联查时）：如日志表用 `log_` 开头。

2. **数据类型选择原则**
   - **优先选择更小的类型**，节省存储空间并提升性能。
   - 整数：`INT`（或 `BIGINT`）优先于 `VARCHAR` 存数字。
   - 金额：统一使用 `DECIMAL(18,2)` 或 `DECIMAL(20,6)`，**禁止使用 FLOAT/DOUBLE**。
   - 时间：优先使用 `DATETIME` 或 `TIMESTAMP`，根据是否需要时区选择。
     - `created_at`、`updated_at` 推荐使用 `DATETIME DEFAULT CURRENT_TIMESTAMP`。
   - 状态/类型枚举：优先使用 `TINYINT` 或 `SMALLINT`，配合注释说明枚举含义。
   - IP 地址：使用 `INT UNSIGNED`（通过 `INET_ATON/INET_NTOA` 转换）或 `VARCHAR(15)`。
   - 长文本：区分 `VARCHAR(255)`、`TEXT`、`MEDIUMTEXT` 根据实际长度。

3. **字段属性规范**
   - **主键**：统一命名为 `id`，类型 `BIGINT UNSIGNED AUTO_INCREMENT`。
   - **NOT NULL**：除明确允许为空的字段外，所有字段默认 `NOT NULL`，并设置合理 `DEFAULT` 值。
     - 示例：`status TINYINT NOT NULL DEFAULT 0`
   - **默认值**：必须显式设置，避免隐式默认导致数据不一致。
   - **注释**：**每个字段必须有注释**，说明业务含义、取值范围、枚举说明等。

4. **通用字段（推荐每张表必备）**
   ```sql
   id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
   created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
   updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
   is_deleted        TINYINT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除：0-正常，1-已删除',
   creator_id        BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '创建人ID',
   updater_id        BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '更新人ID'
   ```

---

`表定义模板示例`
```sql
CREATE TABLE `user` (
  `id`              BIGINT UNSIGNED AUTO_INCREMENT COMMENT '用户ID'
                    PRIMARY KEY,
  `user_name`       VARCHAR(50) NOT NULL DEFAULT '' COMMENT '用户名（登录名）',
  `nick_name`       VARCHAR(50) NOT NULL DEFAULT '' COMMENT '昵称',
  `password`        VARCHAR(100) NOT NULL COMMENT '密码（加密存储）',
  `mobile`          VARCHAR(20) NOT NULL DEFAULT '' COMMENT '手机号',
  `email`           VARCHAR(100) NOT NULL DEFAULT '' COMMENT '邮箱',
  `status`          TINYINT NOT NULL DEFAULT 1 COMMENT '状态：0-禁用，1-正常，2-冻结',
  `is_vip`          TINYINT NOT NULL DEFAULT 0 COMMENT '是否VIP：0-否，1-是',
  `vip_expire_time` DATETIME NULL COMMENT 'VIP到期时间（NULL表示非VIP）',
  `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted`      TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-正常，1-已删除',
  `creator_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '创建人ID',
  `updater_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '更新人ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';
```

---

`索引规范`
- 主键自动建立聚簇索引。
- 常用查询字段建立普通索引或唯一索引。
- 联合索引字段顺序：**等值条件 > 范围条件 > 排序字段**（最左前缀原则）。
- 索引命名：`idx_字段名1_字段名2`、`uniq_字段名1_字段名2`。
- 避免过多索引（建议单表索引数 ≤ 5 个）。

---

`其他最佳实践`
- **字符集**：统一使用 `utf8mb4` 支持表情符号。
- **存储引擎**：生产环境优先 `InnoDB`。
- **表名**：复数形式 + 下划线（如 `orders`、`user_logs`），或业务模块前缀（如 `pay_orders`）。
- **版本控制**：所有建表语句和变更语句放入 Git，配合 Flyway/Liquibase 等工具管理。
- **审核机制**：所有 DDL 变更必须经过代码审查和测试环境验证。

---

`总结`
- **字段名（subject）**：控制在合理长度，清晰表达业务含义（50 字符以内为佳）。
- **字段注释（body）**：详细说明“为什么这样设计”、取值范围、业务规则。
- **默认值与 NOT NULL**：像 commit 的 footer，强制规范，避免隐式行为。
- **保持一致性**：整个项目所有表风格统一，这是最重要的一条。



## logger 日志规范（Python 项目通用版）

良好的日志配置和管理是保障系统可观测性、快速定位问题和长期稳定运行的基础。日志应提供清晰的结构化信息、合理的级别划分、可靠的输出渠道，同时避免性能开销过大或日志泛滥。

本规范适用于所有 Python 项目（Web 服务、爬虫、脚本、数据处理等），旨在统一日志风格、提升排查效率。

---

`通用日志原则`

1. **日志级别使用规范**：

   - **DEBUG**：详细调试信息（如中间变量、API 请求/响应详情）。仅开发/测试环境开启，生产环境关闭。
   - **INFO**：关键业务里程碑、正常流程节点（如“服务启动完成”“任务开始执行”“请求处理成功”）。
   - **WARNING**：潜在问题或降级处理（如“缓存未命中”“重试成功”“使用默认配置”）。
   - **ERROR**：业务异常、可捕获错误，必须附带异常堆栈和关键上下文。
   - **CRITICAL**：严重错误，导致进程/服务不可用（如配置缺失、数据库永久连接失败）。

2. **日志内容要求**：

   - 必须包含足够上下文（如 request_id、user_id、task_id、url 等关键标识）。
   - 敏感信息严格脱敏（手机号、身份证、密码、token 等禁止明文打印）。
   - 优先使用结构化日志（JSON 格式），便于 ELK、Loki 等系统解析。
   - 单条日志避免过长（建议 < 4KB），必要时拆分或仅记录关键字段。
   - 禁止在高频循环中记录 DEBUG/INFO 日志。

3. **最佳实践**：

   - 全项目使用单一全局 logger 实例，避免重复初始化。
   - 支持控制台 + 文件双输出，生产环境必须落盘。
   - 日志文件建议按日期滚动，避免单个文件过大。
   - 支持动态调整日志级别（不重启进程）。
   - 异常捕获后必须记录 ERROR 日志并附带 exc_info=True。
   - 生产环境禁止使用 print() 输出业务日志。

---

`推荐日志配置实现（通用版）`

```python
"""全局日志配置模块

该模块提供项目统一的日志管理器，支持：
- 单例模式全局 logger
- 控制台 + 文件输出
- 日志文件按日期滚动（ RotatingFileHandler 或 TimedRotatingFileHandler ）
- JSON 结构化格式可选
- 配置从 settings 或环境变量加载
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# 项目配置示例（实际项目中可替换为自己的 config 模块或 pydantic Settings）
class LogConfig:
    LOG_LEVEL: str = "INFO"                  # DEBUG/INFO/WARNING/ERROR/CRITICAL
    LOG_DIR: str = "logs"                     # 日志目录
    LOG_FILE_NAME: str = "app.log"            # 日志文件名
    LOG_MAX_BYTES: int = 50 * 1024 * 1024     # 单文件最大 50MB
    LOG_BACKUP_COUNT: int = 10                # 保留 10 个备份文件
    LOG_JSON_FORMAT: bool = False            # 是否启用 JSON 结构化日志
    LOG_CONSOLE: bool = True                 # 是否输出到控制台

# 可替换为你的实际配置加载方式
config = LogConfig()


class LoggerManager:
    """日志管理器（单例模式）"""

    _instance: Optional['LoggerManager'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'LoggerManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        """初始化全局 logger"""
        logger_name = "app"  # 可改为项目名，如 "myproject" 或 __name__
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

        # 避免重复添加 handler（多次导入模块时）
        if self._logger.handlers:
            return

        # 创建日志目录
        log_dir = Path(config.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / config.LOG_FILE_NAME

        # 格式化器
        if config.LOG_JSON_FORMAT:
            # 推荐第三方库：python-json-logger
            try:
                from python_json_logger.jsonlogger import JsonFormatter
                formatter = JsonFormatter(
                    '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s'
                )
            except ImportError:  # fallback
                formatter = logging.Formatter(
                    '{"time":"%(asctime)s", "name":"%(name)s", "level":"%(levelname)s", '
                    '"file":"%(filename)s:%(lineno)d", "message":%(message)s}'
                )
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        # 文件处理器 - 按大小滚动
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        # 可选：按天滚动（替代方案）
        # file_handler = logging.handlers.TimedRotatingFileHandler(
        #     filename=log_file,
        #     when='midnight',
        #     interval=1,
        #     backupCount=30,
        #     encoding='utf-8'
        # )

        # 控制台处理器
        if config.LOG_CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """获取配置好的全局 logger"""
        return self._logger


# 全局 logger 实例（项目中统一导入使用）
logger = LoggerManager().get_logger()
```

---

`使用示例`

```python
from logger import logger  # 假设文件名为 logger.py

def process_task(task_id: str, url: str):
    logger.info("task.start", task_id=task_id, url=url)  # 推荐结构化键值对

    try:
        data = fetch_data(url)
        logger.info("fetch.success", task_id=task_id, data_size=len(data))
        
        result = process(data)
        logger.info("task.success", task_id=task_id)
        
    except Exception as e:
        logger.error(
            "task.failed",
            task_id=task_id,
            url=url,
            exc_info=e,  # 自动打印堆栈
            error=str(e)
        )
        raise
```

---

`总结最佳实践`

- **全项目只导入一个全局 logger**，避免散乱创建 logging.getLogger()。
- **生产环境必须启用文件滚动**，防止磁盘写满。
- **推荐逐步迁移到 JSON 结构化日志**，极大提升日志查询效率。
- **敏感数据脱敏** 是安全合规底线。
- **异常必须记录堆栈**，不允许“吞异常”而不日志。
- **日志配置集中管理**，支持通过环境变量或配置文件灵活调整。
- **写日志时站在“凌晨 3 点被告警叫醒”的角度**：这条日志能否让你快速定位问题？
