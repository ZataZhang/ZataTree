---
title: python-logging模块添加日志
description: ""
date: 2025-03-18T14:30:39+08:00
image: images/index/index.png
categories:
    - Grammar
tags:
    - python
---


<!-- ![alt text](images/index/index.png) -->

在 Python 项目中添加日志功能是一个很好的实践，可以帮助你跟踪程序运行状态、调试问题以及记录重要事件。对于一个包含多个文件且存在调用关系的项目，可以通过以下步骤实现日志功能：

## 基本概念

### 1. 使用 Python 的 `logging` 模块
Python 内置的 `logging` 模块非常强大且灵活，适合在多文件项目中使用。相比 `print`，它提供了日志级别（如 DEBUG、INFO、ERROR 等）、格式化输出、文件记录等功能。

### 2. 基本实现步骤
以下是一个在多文件项目中添加日志的通用方法：

#### (1) 创建一个日志配置模块
在一个单独的文件（例如 `logger.py`）中配置日志，这样可以全局复用。

```python
# logger.py
import logging
import os

# 创建日志器
logger = logging.getLogger('MyProject')
logger.setLevel(logging.DEBUG)  # 设置全局日志级别

# 创建日志处理器（输出到控制台）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 控制台显示 INFO 及以上级别

# 创建日志处理器（输出到文件）
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # 文件记录 DEBUG 及以上级别

# 设置日志格式
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到日志器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 提供获取日志器的方法
def get_logger(name):
    return logging.getLogger(f"MyProject.{name}")
```

这个配置：
- 将日志同时输出到控制台和文件。
- 文件日志记录所有级别（DEBUG 及以上），控制台只显示 INFO 及以上。
- 日志格式包括时间、模块名、级别、文件名、行号和消息。

#### (2) 在其他文件中使用日志
在项目中的各个文件里，通过 `logger.py` 获取日志器并使用。

例如，假设你有两个文件 `module1.py` 和 `module2.py`，它们之间有调用关系：

```python
# module1.py
from logger import get_logger

logger = get_logger("module1")

def func1():
    logger.debug("正在执行 func1")
    logger.info("func1 开始调用 func2")
    from module2 import func2
    func2()
    logger.info("func1 执行完成")
```

```python
# module2.py
from logger import get_logger

logger = get_logger("module2")

def func2():
    logger.debug("正在执行 func2")
    logger.warning("func2 中可能有潜在问题")
    logger.info("func2 执行完成")
```

#### (3) 主程序入口
在主程序中调用这些模块：

```python
# main.py
from logger import get_logger
from module1 import func1

logger = get_logger("main")

if __name__ == "__main__":
    logger.info("程序启动")
    func1()
    logger.info("程序结束")
```

运行后，日志会同时输出到控制台和 `logs/app.log` 文件中。文件中的日志可能如下：

```
2025-03-17 10:00:00,123 - MyProject.main - INFO - main.py:7 - 程序启动
2025-03-17 10:00:00,125 - MyProject.module1 - DEBUG - module1.py:5 - 正在执行 func1
2025-03-17 10:00:00,126 - MyProject.module1 - INFO - module1.py:6 - func1 开始调用 func2
2025-03-17 10:00:00,127 - MyProject.module2 - DEBUG - module2.py:5 - 正在执行 func2
2025-03-17 10:00:00,128 - MyProject.module2 - WARNING - module2.py:6 - func2 中可能有潜在问题
2025-03-17 10:00:00,129 - MyProject.module2 - INFO - module2.py:7 - func2 执行完成
2025-03-17 10:00:00,130 - MyProject.module1 - INFO - module1.py:8 - func1 执行完成
2025-03-17 10:00:00,131 - MyProject.main - INFO - main.py:9 - 程序结束
```

控制台只会显示 INFO 及以上级别的日志。

### 3. 高级配置（可选）
如果项目较大或需求更复杂，可以考虑以下优化：

#### (1) 使用配置文件
将日志配置写入一个配置文件（例如 `logging_config.ini`），然后通过 `logging.config` 加载：

```ini
# logging_config.ini
[loggers]
keys=root

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('logs/app.log', 'a', 'utf-8')

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
```

在 `logger.py` 中加载：

```python
# logger.py
import logging.config

logging.config.fileConfig("logging_config.ini")
logger = logging.getLogger("MyProject")

def get_logger(name):
    return logging.getLogger(f"MyProject.{name}")
```

#### (2) 日志按时间分割
使用 `logging.handlers.TimedRotatingFileHandler` 实现日志按时间（例如每天）分割：

```python
# logger.py
from logging.handlers import TimedRotatingFileHandler

file_handler = TimedRotatingFileHandler(
    "logs/app.log", when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
```

这会每天生成一个新日志文件，并保留最近 7 天的日志。

#### (3) 避免重复日志
如果模块被多次导入，确保日志处理器不会重复添加。可以在 `logger.py` 中添加检查：

```python
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
```

### 4. 注意事项
- **日志级别**：合理选择日志级别（DEBUG 用于调试，INFO 用于常规信息，WARNING 用于警告，ERROR 用于错误）。
- **性能**：日志过多可能影响性能，建议在生产环境中调整日志级别（例如只记录 INFO 以上）。
- **模块化**：通过 `get_logger("模块名")` 为每个模块创建独立的日志器，便于追踪调用关系。

### 5. 总结
通过以上方法，你可以在多文件 Python 项目中实现统一的日志管理。推荐从简单的 `logger.py` 开始，随着项目需求增加再逐步优化配置。



在 Python 的 `logging` 模块中，日志级别是用来区分日志消息重要性的一种机制。不同的级别对应不同的使用场景，帮助开发者或运维人员快速筛选和定位信息。`logging` 模块内置了以下几种标准日志级别，从低到高排列：

## 日志级别划分

以下是 Python `logging` 模块的标准日志级别及其数值（数值越大，级别越高）：

| 级别       | 数值 | 描述                                                                 |
|------------|------|----------------------------------------------------------------------|
| `NOTSET`   | 0    | 未设置，默认级别，通常不直接使用。                                   |
| `DEBUG`    | 10   | 调试信息，通常用于开发和调试阶段，记录详细的程序运行细节。           |
| `INFO`     | 20   | 常规信息，用于确认程序按预期运行，记录关键步骤或状态。               |
| `WARNING`  | 30   | 警告信息，表示可能存在问题，但程序仍能继续运行（默认级别）。         |
| `ERROR`    | 40   | 错误信息，表示发生了较严重的问题，某些功能可能无法正常执行。         |
| `CRITICAL` | 50   | 严重错误信息，表示程序遇到致命问题，可能无法继续运行。               |

### 各日志级别的使用场景
1. **`DEBUG`（调试）**
   - **用途**：记录详细的调试信息，例如变量值、函数调用栈、循环迭代等。
   - **场景**：开发和测试阶段，用于排查问题。
   - **示例**：
     ```python
     logger.debug("变量 x 的值: %s", x)
     ```

2. **`INFO`（信息）**
   - **用途**：记录程序正常运行时的关键信息，例如启动、结束、重要步骤完成。
   - **场景**：生产环境中确认程序正常运行。
   - **示例**：
     ```python
     logger.info("服务器启动成功，监听端口: 8080")
     ```

3. **`WARNING`（警告）**
   - **用途**：记录潜在问题或非预期情况，但不影响程序继续运行。
   - **场景**：提醒开发者或用户注意某些异常情况。
   - **示例**：
     ```python
     logger.warning("配置文件未找到，使用默认设置")
     ```

4. **`ERROR`（错误）**
   - **用途**：记录发生的错误，通常会导致某些功能失效。
   - **场景**：生产环境中记录需要修复的问题。
   - **示例**：
     ```python
     logger.error("数据库连接失败: %s", exception_message)
     ```

5. **`CRITICAL`（严重）**
   - **用途**：记录致命错误，通常会导致程序崩溃或无法继续运行。
   - **场景**：需要立即关注和处理的问题。
   - **示例**：
     ```python
     logger.critical("系统内存不足，程序即将退出")
     ```

### 日志级别的工作机制
- **日志器的级别**：通过 `logger.setLevel()` 设置，只有大于等于该级别的日志才会记录。
  - 例如，如果设置为 `INFO`，则 `DEBUG` 日志不会输出，但 `INFO`、`WARNING`、`ERROR` 和 `CRITICAL` 会输出。
- **处理器的级别**：每个处理器（如 `StreamHandler`、`FileHandler`）也可以单独设置级别，决定输出哪些日志。
  - 例如，控制台只显示 `INFO` 及以上，文件记录 `DEBUG` 及以上。

### 示例代码
```python
import logging

# 创建日志器
logger = logging.getLogger("example")
logger.setLevel(logging.DEBUG)  # 日志器记录所有级别

# 创建控制台处理器，只显示 INFO 及以上
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# 创建文件处理器，记录 DEBUG 及以上
file_handler = logging.FileHandler("example.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# 测试不同级别日志
logger.debug("这是一个调试信息")
logger.info("这是一个常规信息")
logger.warning("这是一个警告信息")
logger.error("这是一个错误信息")
logger.critical("这是一个严重错误信息")
```

**输出结果**：
- **控制台**（只显示 `INFO` 及以上）：
  ```
  INFO - 这是一个常规信息
  WARNING - 这是一个警告信息
  ERROR - 这是一个错误信息
  CRITICAL - 这是一个严重错误信息
  ```
- **文件 `example.log`**（记录 `DEBUG` 及以上）：
  ```
  2025-03-17 10:00:00,123 - DEBUG - 这是一个调试信息
  2025-03-17 10:00:00,124 - INFO - 这是一个常规信息
  2025-03-17 10:00:00,125 - WARNING - 这是一个警告信息
  2025-03-17 10:00:00,126 - ERROR - 这是一个错误信息
  2025-03-17 10:00:00,127 - CRITICAL - 这是一个严重错误信息
  ```

### 如何选择日志级别
- **开发阶段**：多用 `DEBUG` 和 `INFO`，方便调试。
- **生产环境**：通常设置为 `INFO` 或 `WARNING`，避免过多调试信息影响性能。
- **异常处理**：用 `ERROR` 或 `CRITICAL` 记录错误，并结合异常堆栈（如 `logger.exception()`）。

### 自定义日志级别（可选）
如果内置级别不够用，可以通过 `logging.addLevelName()` 定义新级别：
```python
logging.addLevelName(15, "VERBOSE")
logger.setLevel(15)
logger.log(15, "这是一个自定义VERBOSE信息")
```
