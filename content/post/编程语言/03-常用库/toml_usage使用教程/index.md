---
title: toml_usage_tutorial
description: ""
date: 2025-08-05T15:26:51+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - Python_Lib
---

### 什么是 TOML？

TOML (Tom's Obvious, Minimal Language) 是一种专为配置文件设计的、语义清晰且易于阅读的格式。它的目标是成为一个优秀的“最小化”语言，能够无歧义地映射到哈希表（在 Python 中即字典）。

由于其出色的可读性，TOML 已被 Python 社区广泛采用，最著名的应用就是 `pyproject.toml` 文件，用于管理项目的构建和依赖。

一个简单的 TOML 文件 `config.toml` 看起来是这样的：

```toml
# 这是一个 TOML 文件的注释
title = "TOML 示例"

[database]
server = "192.168.1.1"
ports = [ 8001, 8002, 8003 ]
connection_max = 5000
enabled = true

[owner]
name = "Tom Preston-Werner"
dob = 1979-05-27T07:32:00-08:00 # 日期时间格式
```

### 为什么使用 TOML？

  * **可读性强**：语法直观，对人类友好。
  * **结构清晰**：通过 `[table]` 和 `[[array of tables]]` 能够清晰地表达数据结构。
  * **强类型**：支持字符串、整数、浮点数、布尔值、日期时间、数组和表（字典）等明确的数据类型。
  * **官方推荐**：`pyproject.toml` (PEP 518) 的采用使其成为 Python 项目配置的事实标准。

-----

### 在 Python 中使用 TOML

在 Python 中处理 TOML 文件主要有两种方式：

1.  **`tomllib` (标准库, Python 3.11+)**：用于 **读取** TOML 文件。这是 Python 官方内置的库，但功能仅限于解析（读取），不能写入。
2.  **`toml` (第三方库)**：用于 **读取和写入** TOML 文件。在 Python 3.11 之前，这是最流行的选择。即使在 3.11+，当你需要写入 TOML 文件时，它仍然是必需的。

#### 安装第三方库

如果你使用的 Python 版本低于 3.11，或者你需要写入 TOML 文件，首先需要安装 `toml` 库：

```bash
pip install toml
```

### 1\. 读取 TOML 文件

假设我们有以下 `config.toml` 文件：

```toml
# 配置文件示例
title = "我的应用"
version = "1.2.0"

[database]
host = "localhost"
port = 5432
user = "admin"
enabled = true

[users]
roles = ["admin", "editor", "viewer"]

# 数组表，用于表示一组复杂的对象
[[servers]]
name = "alpha"
ip = "10.0.0.1"
role = "database"

[[servers]]
name = "beta"
ip = "10.0.0.2"
role = "web"
```

#### 使用 `tomllib` (Python 3.11+)

`tomllib` 的用法非常简单，和 `json` 模块类似。

  * `tomllib.load()`: 从一个二进制文件流中读取 TOML。
  * `tomllib.loads()`: 从一个字符串中读取 TOML。

<!-- end list -->

```python
# --- 使用 tomllib (Python 3.11+) ---

import tomllib
import pprint # 用于美化输出

try:
    # 注意：必须以二进制模式 ('rb') 打开文件
    with open('config.toml', 'rb') as f:
        config = tomllib.load(f)
        
        # 打印解析后的数据
        pprint.pprint(config)

        # 访问数据
        print("\n--- 访问数据 ---")
        print(f"应用标题: {config['title']}")
        print(f"数据库主机: {config['database']['host']}")
        print(f"第一个服务器的名字: {config['servers'][0]['name']}")

except FileNotFoundError:
    print("错误：config.toml 文件未找到。")
except tomllib.TOMLDecodeError as e:
    print(f"错误：解析 TOML 文件失败: {e}")

```

**输出结果：**

```
{'database': {'enabled': True, 'host': 'localhost', 'port': 5432, 'user': 'admin'},
 'servers': [{'ip': '10.0.0.1', 'name': 'alpha', 'role': 'database'},
             {'ip': '10.0.0.2', 'name': 'beta', 'role': 'web'}],
 'title': '我的应用',
 'users': {'roles': ['admin', 'editor', 'viewer']},
 'version': '1.2.0'}

--- 访问数据 ---
应用标题: 我的应用
数据库主机: localhost
第一个服务器的名字: alpha
```

#### 使用 `toml` (所有 Python 版本)

`toml` 库的用法几乎与 `tomllib` 完全相同。

  * `toml.load()`: 从一个文本文件流中读取 TOML。
  * `toml.loads()`: 从一个字符串中读取 TOML。

<!-- end list -->

```python
# --- 使用 toml (第三方库) ---

import toml
import pprint

try:
    # 注意：使用文本模式 ('r') 打开文件
    with open('config.toml', 'r', encoding='utf-8') as f:
        config = toml.load(f)
        
        pprint.pprint(config)

except FileNotFoundError:
    print("错误：config.toml 文件未找到。")
except toml.TomlDecodeError as e:
    print(f"错误：解析 TOML 文件失败: {e}")
```

**关键区别**：`tomllib.load()` 需要以二进制模式 (`'rb'`) 打开文件，而 `toml.load()` 通常以文本模式 (`'r'`) 打开。

-----

### 2\. 写入 TOML 文件

如前所述，标准库 `tomllib` **不支持写入**。因此，我们必须使用 `toml` 第三方库来将 Python 对象（通常是字典）序列化为 TOML 格式。

  * `toml.dump()`: 将 Python 对象写入到文件流。
  * `toml.dumps()`: 将 Python 对象转换为 TOML 格式的字符串。

#### 示例：创建并写入 TOML 文件

假设我们有一个 Python 字典，并想将其保存为 `new_config.toml`。

```python
import toml
from datetime import datetime

# 1. 定义一个 Python 字典
new_config_data = {
    'app_name': 'SuperApp',
    'version': '2.0.0',
    'debug_mode': False,
    'last_updated': datetime.now(), # toml库支持datetime对象
    
    'database': {
        'host': 'db.example.com',
        'port': 8080,
        'credentials': {
            'user': 'new_user',
            'pass': 's3cr3t'
        }
    },
    
    'features_enabled': ['feature1', 'feature2', 'feature3'],
    
    'nodes': [
        {'name': 'primary', 'ip': '192.168.1.100'},
        {'name': 'replica', 'ip': '192.168.1.101'}
    ]
}

# 2. 将字典写入文件
try:
    with open('new_config.toml', 'w', encoding='utf-8') as f:
        toml.dump(new_config_data, f)
    print("成功将配置写入 new_config.toml 文件。")

except Exception as e:
    print(f"写入文件时出错: {e}")

# 3. (可选) 将字典转换为字符串
config_string = toml.dumps(new_config_data)
print("\n--- TOML 格式字符串 ---")
print(config_string)
```

执行后，会生成一个 `new_config.toml` 文件，内容如下：

```toml
app_name = "SuperApp"
version = "2.0.0"
debug_mode = false
last_updated = 2025-08-05T07:21:54.123456 # 具体时间取决于运行时间
features_enabled = [ "feature1", "feature2", "feature3" ]

[database]
host = "db.example.com"
port = 8080

[database.credentials]
user = "new_user"
pass = "s3cr3t"

[[nodes]]
name = "primary"
ip = "192.168.1.100"

[[nodes]]
name = "replica"
ip = "192.168.1.101"
```

-----

### 综合示例：读取、修改、再写入

这是一个更实际的流程，模拟了从配置文件加载设置，进行修改，然后保存回去的场景。

```python
import toml
import pprint

CONFIG_FILE = 'config.toml'

# --- 1. 读取现有配置 ---
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = toml.load(f)
    print("--- 原始配置 ---")
    pprint.pprint(config)
except FileNotFoundError:
    print(f"配置文件 {CONFIG_FILE} 未找到，将使用空配置。")
    config = {}

# --- 2. 修改配置 ---
# 更新版本号
config['version'] = '1.3.0'

# 禁用数据库
config['database']['enabled'] = False

# 添加一个新的服务器
new_server = {'name': 'gamma', 'ip': '10.0.0.3', 'role': 'monitoring'}
if 'servers' in config:
    config['servers'].append(new_server)
else:
    config['servers'] = [new_server]

print("\n--- 修改后的配置 ---")
pprint.pprint(config)

# --- 3. 写入到新文件 ---
try:
    with open('config_updated.toml', 'w', encoding='utf-8') as f:
        toml.dump(config, f)
    print(f"\n成功将更新后的配置写入 config_updated.toml")
except Exception as e:
    print(f"写入文件时出错: {e}")

```

### 高级话题与注意事项

  * **`pyproject.toml`**：这是现代 Python 项目中最重要的 TOML 应用。它用于定义项目元数据、构建系统（如 setuptools, poetry, flit）和工具配置（如 black, ruff, pytest）。TOML 的清晰结构使这个复杂的配置文件易于管理。
  * **注释和格式保留**：`toml` 和 `tomllib` 在解析时会丢弃文件中的注释和原有格式。如果你需要读取一个 TOML 文件，修改其中的值，然后写回并**保留原始的注释和排版**，你需要使用一个更强大的库，比如 **`tomlkit`**。`tomlkit` 专为这种“往返”场景设计，对于自动化修改 `pyproject.toml` 文件的工具来说至关重要。
      * 安装：`pip install tomlkit`
      * 用法与 `toml` 类似，但它会将 TOML 文档解析为一个特殊的、保留格式信息的对象。
  * **错误处理**：在实际应用中，务必使用 `try...except` 块来捕获 `FileNotFoundError`（文件不存在）和 `TOMLDecodeError`（文件格式错误），以增强程序的健壮性。

### 总结

| 功能 | 库 | 方法 | 描述 |
| :--- | :--- | :--- | :--- |
| **读取** | `tomllib` (Python 3.11+) | `load(file_stream)` | 从二进制文件流解析 |
| | | `loads(string)` | 从字符串解析 |
| **读取/写入** | `toml` (第三方) | `load(file_stream)` | 从文本文件流解析 |
| | | `loads(string)` | 从字符串解析 |
| | | `dump(data, file_stream)` | 将 Python 字典写入文件 |
| | | `dumps(data)` | 将 Python 字典转换为字符串 |
| **保留格式读写** | `tomlkit` (第三方) | (类似 `toml`) | 用于需要保留注释和格式的场景 |

希望这个详细的教程能帮助你熟练地在 Python 项目中使用 TOML！