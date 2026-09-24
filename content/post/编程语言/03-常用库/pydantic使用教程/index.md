---
title: pydantic使用教程
description: ""
date: 2025-06-11T10:59:38+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - smallLibrary
---



||
|---|
|- [环境变量配置的代码](#管理应用的变量配置环境变量和初始值的加载顺序)|




### 基础使用

Pydantic 是一个基于 Python 类型提示进行数据验证和设置管理的库。它能够解析和验证复杂的数据结构，并将其转换为 Python 对象，同时在数据不符合规范时给出清晰的错误提示。

-----

 核心优势

  * **代码更简洁、更健壮**: 通过类型提示来定义数据结构，Pydantic 会自动进行验证，减少大量的样板代码。
  * **出色的编辑器支持**: 由于完全基于类型提示，IDE（如 VS Code, PyCharm）可以提供精准的代码补全和类型检查。
  * **极佳的性能**: Pydantic 的核心验证逻辑由 Rust 实现，速度非常快。
  * **与框架无缝集成**: 它被 FastAPI、Django Ninja 等现代 Python Web 框架广泛用作核心组件，用于请求和响应模型的定义。

-----

 快速入门：定义你的第一个模型

首先，确保你已经安装了 Pydantic:

```bash
pip install pydantic
```

最基本的使用方式是创建一个继承自 `pydantic.BaseModel` 的类。

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str = 'John Doe'  带有默认值的字段
    signup_ts: datetime | None = None 可以是 datetime 类型或者 None

 创建 User 实例
user_data = {'id': 123, 'name': 'Alice'}
user = User(**user_data)

print(user.id)
 > 123

print(user.name)
 > Alice

print(user.model_dump())  将模型实例转换为字典
 > {'id': 123, 'name': 'Alice', 'signup_ts': None}
```

 数据验证

如果传入的数据类型不正确，Pydantic 会自动进行转换；如果无法转换，则会抛出一个 `ValidationError`。

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

 尝试用一个字符串来代替整数 ID
user_data = {'id': '123', 'name': 'Alice'}  '123' 会被自动转换为整数 123

try:
    user = User(**user_data)
    print(user)
except ValidationError as e:
    print(e)
 > id=123 name='Alice'

 尝试用一个无法转换的类型
invalid_data = {'id': 'not a number', 'name': 'Bob'}

try:
    User(**invalid_data)
except ValidationError as e:
    print(e.json())
```

运行后，你会得到一个清晰的 JSON 格式错误报告：

```json
[
  {
    "type": "int_parsing",
    "loc": [
      "id"
    ],
    "msg": "Input should be a valid integer, unable to parse string as an integer",
    "input": "not a number"
  }
]
```

-----

 常用功能与进阶用法

 1\. 嵌套模型 (Nested Models)

你可以将一个 `BaseModel` 嵌套在另一个模型中，以构建复杂的数据结构。

```python
from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name: str
    price: float

class Order(BaseModel):
    order_id: int
    items: List[Item]  一个包含 Item 模型的列表

order_data = {
    'order_id': 9527,
    'items': [
        {'name': 'Apple', 'price': 5.5},
        {'name': 'Banana', 'price': 2.8}
    ]
}

order = Order(**order_data)
print(order.items[0].name)
 > Apple

print(order.model_dump_json(indent=2))  转换为格式化的 JSON 字符串
```

输出：

```json
{
  "order_id": 9527,
  "items": [
    {
      "name": "Apple",
      "price": 5.5
    },
    {
      "name": "Banana",
      "price": 2.8
    }
  ]
}
```

 2\. 字段验证与约束 (Field Validation)

Pydantic 提供了 `Field` 函数来为字段添加额外的约束。

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    product_id: int
    name: str = Field(min_length=3, max_length=50)
    price: float = Field(gt=0, description="The price must be greater than zero")  gt = greater than
    tags: list[str] = []
```

在这个例子中：

  * `name` 的长度必须在 3 到 50 个字符之间。
  * `price` 的值必须大于 0。

 3\. 自定义验证器 (Custom Validators)

当内置的验证规则不满足需求时，你可以使用 `@validator` 装饰器创建自己的验证逻辑。

**注意**: 在 Pydantic V2 中，更推荐使用带有 `@field_validator` 的函数。

```python
from pydantic import BaseModel, field_validator

class UserRegistration(BaseModel):
    username: str
    password: str
    password_confirmation: str

    @field_validator('password_confirmation')
    @classmethod
    def passwords_match(cls, v: str, values: 'ValidationInfo') -> str:
         v 是 'password_confirmation' 字段的值
         values.data 包含了模型中所有已解析的字段值
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('Passwords do not match')
        return v
```

 4\. 设置管理 (Settings Management)

Pydantic 的 `BaseSettings` 是管理应用配置的利器。它可以自动从环境变量或 `.env` 文件中读取配置。

首先，安装 `pydantic-settings`：

```bash
pip install pydantic-settings
```

创建一个 `.env` 文件:

```
 .env
API_KEY="your_secret_api_key"
DATABASE_URL="postgresql://user:password@host:port/db"
```

然后定义你的设置类：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    database_url: str
     可以在这里为其他配置项提供默认值
    app_name: str = "My Awesome App"

    class Config:
        env_file = ".env"  指定 .env 文件名

 创建 Settings 实例
settings = Settings()

print(settings.api_key)
 > your_secret_api_key

print(settings.app_name)
 > My Awesome App
```

 5\. 别名生成器 (Alias Generator)

有时，输入的 JSON/dict 的键名可能不是合法的 Python 标识符 (比如 `user-id`)，或者你想在内部使用驼峰命名法 `userId`，而在外部暴露蛇形命名法 `user_id`。这时 `alias` 或 `alias_generator` 就派上用场了。

```python
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

class Person(BaseModel):
    first_name: str
    last_name: str

    class Config:
        alias_generator = to_camel  将蛇形命名转换为驼峰命名
        populate_by_name = True  允许通过字段名和别名两种方式来赋值

 使用别名（驼峰）来创建实例
person_data = {
    'firstName': 'John',
    'lastName': 'Doe'
}
person = Person(**person_data)

print(person.first_name)
 > John

 序列化时也会使用别名
print(person.model_dump(by_alias=True))
 > {'firstName': 'John', 'lastName': 'Doe'}
```

-----

 总结

Pydantic 是一个功能强大且易于使用的库。通过本教程，你应该已经掌握了它的核心用法：

1.  **使用 `BaseModel` 定义数据结构。**
2.  **利用类型提示进行自动数据验证和转换。**
3.  **通过嵌套模型构建复杂的数据对象。**
4.  **使用 `Field` 和 `@field_validator` 添加自定义约束和逻辑。**
5.  **借助 `BaseSettings` 优雅地管理应用配置。**

建议在实际项目中多多使用，并查阅 [Pydantic 官方文档](https://www.google.com/search?q=https://docs.pydantic.dev/) 以了解更多高级功能。



### 管理应用的变量配置（环境变量和初始值的加载）

---

 🚀 使用 Pydantic `BaseSettings` 轻松管理应用配置

在任何应用开发中，管理配置（如数据库连接字符串、API密钥、调试开关等）都是一个关键环节。将配置硬编码在代码中会带来安全风险和维护困难。Pydantic 的 `BaseSettings` 提供了一个优雅的解决方案，可以自动从环境变量或 `.env` 文件中读取配置，并提供类型检查和验证。

本教程将通过分析你提供的 `DemoSettings` 脚本，带你深入了解 `BaseSettings` 的核心功能和最佳实践。

  1. 核心概念：什么是 `BaseSettings`？

简单来说，`BaseSettings` 是一个 Pydantic 模型，但它被赋予了“超能力”：

* **自动读取源**：它会按特定顺序自动从**环境变量**和 **`.env` 文件**中查找并加载配置项。
* **类型转换**：它会自动将读取到的字符串（如 "true", "8000"）转换为正确的 Python 类型（如 `bool`, `int`）。
* **默认值**：你可以像在普通类中一样提供默认值。
* **验证**：你可以使用 Pydantic 强大的验证器来确保配置值的格式正确。

---

  2. 定义你的配置模型

我们从代码的核心 `DemoSettings` 类开始。

```python
class DemoSettings(BaseSettings):
    """演示配置类"""
    
     基本配置
    app_name: str = "Demo App"
    debug: bool = False
    port: int = 8000
    
     API Keys (可选)
    dashscope_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
     ...
```

**关键点说明:**

* **继承 `BaseSettings`**: 这是让 Pydantic 知道这个模型用于管理配置的关键。
* **定义字段**: 像定义普通 Pydantic 模型一样，为每个配置项声明一个带类型注解的类属性。
* **提供默认值**: `app_name: str = "Demo App"` 这行代码意味着，如果在任何地方都找不到 `APP_NAME` 这个配置，它的值将默认为 `"Demo App"`。
* **可选配置**: 使用 `Optional[str]` (在 Python 3.10+ 中可写为 `str | None`) 来表示非必需的配置项，如 `redis_url` 和 API 密钥。

Pydantic 会自动将字段名（如 `app_name`）转换为大写（`APP_NAME`）来查找对应的环境变量。

---

  3. 配置 `BaseSettings` 的行为

你可以在模型内部进行精细的配置，告诉 Pydantic 如何加载和处理设置。代码中优雅地处理了 Pydantic v1 和 v2 的差异。

 Pydantic v2 (推荐)

```python
 Pydantic v2 配置
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
)
```

* **`model_config`**: 这是 Pydantic v2 中配置模型的标准方式。
* **`env_file=".env"`**: 指示 Pydantic 加载当前目录下的 `.env` 文件。
* **`env_file_encoding="utf-8"`**: 确保正确读取包含中文字符的 `.env` 文件。
* **`case_sensitive=False`**: 设置为 `False` 意味着环境变量名不区分大小写（例如 `DEBUG` 和 `debug` 会被同等对待）。

 Pydantic v1 (旧版)

```python
 Pydantic v1 配置
class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    case_sensitive = False
```

如果你还在使用旧版本的 Pydantic，则需要通过一个内嵌的 `Config` 类来完成相同的配置。

---

  4. 添加自定义验证 ✅

这是 `BaseSettings` 最强大的功能之一。你可以确保加载的配置值符合预期的格式。

```python
 Pydantic v2
@field_validator("dashscope_api_key")
@classmethod
def validate_dashscope_key(cls, v):
    if v and not v.startswith("sk-"):
        print(f"警告: DASHSCOPE_API_KEY 可能格式不正确: {v[:10]}...")
    return v
```

这段代码为 `dashscope_api_key` 字段添加了一个验证器。在 Pydantic 尝试填充这个字段的值后，它会调用这个函数：

1.  检查值 `v` 是否存在。
2.  如果存在，检查它是否以 `"sk-"` 开头。
3.  如果格式不符，打印一条警告信息。
4.  **必须返回**验证后的值 `v`。

这可以有效防止因配置错误（例如复制粘贴时漏掉了前缀）导致应用在运行时出错。

---

  5. 理解配置加载的优先级

Pydantic `BaseSettings` 按非常明确的优先级顺序加载配置，这让你能够灵活地在不同环境中覆盖设置。

**优先级从高到低：**

1.  **初始化参数**：在创建实例时直接传入的参数。
    ```python
     port 将会是 9000，忽略所有其他来源
    settings = DemoSettings(port=9000) 
    ```

2.  **环境变量**：系统级的环境变量。
    ```bash
     在终端中设置
    export PORT=8080 
    ```

3.  **`.env` 文件中的变量**：在项目根目录的 `.env` 文件中定义的变量。
    ```dotenv
     .env 文件内容
    PORT=8888
    ```

4.  **模型中定义的默认值**：代码中字段的默认值。
    ```python
     DemoSettings 类中的定义
    port: int = 8000
    ```

💡 **这个优先级顺序非常实用**：你可以在代码中设置一个安全的默认值，在 `.env` 文件中为本地开发提供一套配置，而在生产服务器上通过环境变量来覆盖关键配置（如数据库连接信息），而无需修改任何代码。

---

  6. 实战演练：运行演示脚本

现在，让我们按照演示脚本的逻辑来实际操作一下。

 **步骤 1: 准备文件**

1.  将你的代码保存为 `config_demo.py`。
2.  在与 `config_demo.py` 相同的目录下，创建一个名为 `.env` 的文件。

 **步骤 2: 填充 `.env` 文件**

向 `.env` 文件中添加一些内容。这会覆盖代码中的默认值。

```dotenv
 .env
 覆盖默认的 debug 模式
DEBUG=true

 提供一个可选的 openai_api_key
OPENAI_API_KEY="sk-abcdef123456"

 为演示优先级，我们在这里也设置 PORT
PORT=8888
```

 **步骤 3: 设置环境变量 (可选)**

为了演示最高优先级的环境变量，打开你的终端并执行以下命令（Windows 使用 `set` 而不是 `export`）：

```bash
export DASHSCOPE_API_KEY="sk-this-is-from-env-variable"
export PORT=9999
```

 **步骤 4: 运行脚本**

现在，在你的终端中运行 Python 脚本：

```bash
python config_demo.py
```

 **步骤 5: 分析输出**

你将看到类似下面的输出，它清晰地展示了配置的来源和优先级：

```
============================================================
BaseSettings 功能演示
使用 Pydantic v2
============================================================

1. 当前相关环境变量:
  DASHSCOPE_API_KEY = sk-thi...able
  OPENAI_API_KEY = (未设置)
  DEBUG = (未设置)
  PORT = 9999

2. 创建 BaseSettings 实例:
  ✓ 配置实例创建成功

3. 加载的配置值:
  app_name: Demo App
  debug: True
  port: 9999
  database_url: sqlite:///demo.db
  dashscope_api_key: sk-thi...able
  openai_api_key: sk-abc...456
  redis_url: (未设置)

4. .env 文件演示:
  .env 文件存在，内容:
    2: DEBUG=true
    5: OPENAI_API_KEY=sk-abc...456
    8: PORT=8888

5. 配置优先级演示:
  优先级顺序: 初始化参数 > .env 文件 > 环境变量 > 默认值
  使用初始化参数: app_name='Custom App', port=9000

...
```

**输出解读：**

* `debug: True`：值来自 `.env` 文件，覆盖了代码中默认的 `False`。
* `port: 9999`：值来自**环境变量**，它的优先级高于 `.env` 文件中的 `8888`。
* `dashscope_api_key`: 值来自**环境变量**。
* `openai_api_key`: 值来自 `.env` 文件。
* `app_name: Demo App`：由于环境变量和 `.env` 文件都未设置，所以使用了代码中的默认值。
* 在优先级演示部分，`port` 变为 `9000`，`app_name` 变为 `Custom App`，这证明了**初始化参数**拥有最高优先级。

  总结

通过使用 Pydantic 的 `BaseSettings`，你可以实现一个健壮、可维护且安全的配置系统。

* **分离配置与代码**：让你的代码库更干净，更易于部署到不同环境。
* **消除魔法字符串**：通过强类型字段访问配置（`settings.port`），而不是字典键（`os.getenv("PORT")`），减少了拼写错误。
* **自带验证和类型安全**：在应用启动时就捕获配置错误，而不是在运行时。
* **清晰的优先级**：让你能够自信地管理不同环境下的配置。

将 `BaseSettings` 集成到你的下一个 Python 项目中吧！

好的，这是接续上面教程的完整 Python 演示代码。

---

附录：完整演示代码

你可以将以下代码保存为 `config_demo.py` 文件，并按照教程中的步骤进行操作来亲自体验 `BaseSettings` 的功能。

```python
"""
BaseSettings 功能演示
演示如何使用 Pydantic BaseSettings 从环境变量和 .env 文件加载配置
"""
import os
from typing import Optional
try:
    # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import field_validator
    PYDANTIC_V2 = True
except ImportError:
    # Pydantic v1
    from pydantic import BaseSettings, validator
    PYDANTIC_V2 = False
from pathlib import Path


class DemoSettings(BaseSettings):
    """演示配置类"""
    
    # 基本配置
    app_name: str = "Demo App"
    debug: bool = False
    port: int = 8000
    
    # API Keys
    dashscope_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # 数据库配置
    database_url: str = "sqlite:///demo.db"
    
    # 可选配置
    redis_url: Optional[str] = None
    
    if PYDANTIC_V2:
        # Pydantic v2 配置
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
        )
        
        @field_validator("dashscope_api_key")
        @classmethod
        def validate_dashscope_key(cls, v):
            if v and not v.startswith("sk-"):
                print(f"警告: DASHSCOPE_API_KEY 可能格式不正确: {v[:10]}...")
            return v
    else:
        # Pydantic v1 配置
        @validator("dashscope_api_key")
        def validate_dashscope_key(cls, v):
            if v and not v.startswith("sk-"):
                print(f"警告: DASHSCOPE_API_KEY 可能格式不正确: {v[:10]}...")
            return v
        
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False


def demonstrate_basesettings():
    """演示 BaseSettings 的功能"""
    
    print("=" * 60)
    print("BaseSettings 功能演示")
    print(f"使用 Pydantic {'v2' if PYDANTIC_V2 else 'v1'}")
    print("=" * 60)
    
    # 1. 显示当前环境变量
    print("\n1. 当前相关环境变量:")
    env_vars = ["DASHSCOPE_API_KEY", "OPENAI_API_KEY", "DEBUG", "PORT"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 对于 API Key，只显示前几位和后几位
            if "API_KEY" in var and len(value) > 10:
                display_value = f"{value[:6]}...{value[-4:]}"
            else:
                display_value = value
            print(f"  {var} = {display_value}")
        else:
            print(f"  {var} = (未设置)")
    
    # 2. 创建配置实例
    print("\n2. 创建 BaseSettings 实例:")
    try:
        settings = DemoSettings()
        print("  ✓ 配置实例创建成功")
    except Exception as e:
        print(f"  ✗ 配置实例创建失败: {e}")
        return
    
    # 3. 显示加载的配置
    print("\n3. 加载的配置值:")
    print(f"  app_name: {settings.app_name}")
    print(f"  debug: {settings.debug}")
    print(f"  port: {settings.port}")
    print(f"  database_url: {settings.database_url}")
    
    if settings.dashscope_api_key:
        masked_key = f"{settings.dashscope_api_key[:6]}...{settings.dashscope_api_key[-4:]}"
        print(f"  dashscope_api_key: {masked_key}")
    else:
        print(f"  dashscope_api_key: (未设置)")
    
    if settings.openai_api_key:
        masked_key = f"{settings.openai_api_key[:6]}...{settings.openai_api_key[-4:]}"
        print(f"  openai_api_key: {masked_key}")
    else:
        print(f"  openai_api_key: (未设置)")
    
    if settings.redis_url:
        print(f"  redis_url: {settings.redis_url}")
    else:
        print(f"  redis_url: (未设置)")
    
    # 4. 演示 .env 文件功能
    print("\n4. .env 文件演示:")
    env_file_path = Path(".env")
    if env_file_path.exists():
        print("  .env 文件存在，内容:")
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 隐藏敏感信息
                    if "API_KEY" in line:
                        key, value = line.split('=', 1)
                        if len(value) > 10:
                            value = f"'{value[:6]}...{value[-4:]}'"
                        line = f"{key}={value}"
                    print(f"    {line_num}: {line}")
    else:
        print("  .env 文件不存在")
        print("  你可以创建 .env 文件来测试配置优先级:")
        print("  例如: echo DEBUG=true > .env")
    
    # 5. 演示配置优先级
    print("\n5. 配置优先级演示:")
    print("  优先级顺序: 初始化参数 > 环境变量 > .env 文件 > 默认值")
    
    # 使用初始化参数覆盖
    try:
        custom_settings = DemoSettings(app_name="Custom App", port=9000)
        print(f"  使用初始化参数: app_name='{custom_settings.app_name}', port={custom_settings.port}")
    except Exception as e:
        print(f"  初始化参数演示失败: {e}")
    
    # 6. 显示所有配置的字典形式
    print("\n6. 所有配置 (字典形式):")
    try:
        if PYDANTIC_V2:
            config_dict = settings.model_dump()
        else:
            config_dict = settings.dict()
        
        for key, value in config_dict.items():
            if "api_key" in key.lower() and value and len(str(value)) > 10:
                value = f"{str(value)[:6]}...{str(value)[-4:]}"
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  配置字典显示失败: {e}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_basesettings()
```



### 教程：使用 Pydantic 的 BaseSettings 精通应用配置管理 -- 调整变量优先顺序

![pydantic_settings 中的 BaseSettings配置优先级](images/index/image.png)

管理应用的配置（如 API 密钥、数据库 URL 和调试开关）是一项基础而重要的任务。将这些值硬编码在代码中是一种非常糟糕的做法。Pydantic 的 `BaseSettings` 提供了一个强大而优雅的解决方案，它能够从环境变量或 `.env` 文件中加载你的配置，并结合了强大的类型验证功能。

本教程将引导你有效使用 `BaseSettings`，从基础设置到高级的优先级管理。

1. 什么是 `BaseSettings`？

`BaseSettings` 是一个 Pydantic 模型，它可以自动从你的环境中读取配置值。这使你能够将配置与代码分离，极大地提高了安全性和灵活性。

其基本思想非常简单：
1.  定义一个继承自 `BaseSettings` 的类。
2.  将你的配置变量声明为带有类型提示的类属性。
3.  Pydantic 会处理剩下的事情：读取值、将其转换为正确的类型，并进行验证。

让我们深入代码，看看它是如何工作的。

***

2. 基础设置：`DemoSettings` 类

首先，我们定义配置的结构。`DemoSettings` 类包含了常见的配置项，如应用名称、API 密钥和数据库 URL。它同时演示了如何兼容 Pydantic v1 和 v2。

 定义配置类

```python
import os
from typing import Optional
try:
    # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import field_validator
    PYDANTIC_V2 = True
except ImportError:
    # Pydantic v1
    from pydantic import BaseSettings, validator
    PYDANTIC_V2 = False

class DemoSettings(BaseSettings):
    """演示配置类"""
    
    # --- 带有默认值的字段 ---
    app_name: str = "Demo App"
    debug: bool = False
    port: int = 8000
    
    # --- 用于敏感数据的字段 (API Keys) ---
    dashscope_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # --- 带有复杂值的字段 ---
    database_url: str = "sqlite:///demo.db"

    # --- Pydantic 的配置 ---
    if PYDANTIC_V2:
        # Pydantic v2 使用 model_config 字典进行配置
        model_config = SettingsConfigDict(
            env_file=".env",              # 要加载的 dotenv 文件名
            env_file_encoding="utf-8",    # dotenv 文件的编码
            case_sensitive=False,         # 环境变量是否区分大小写
        )
    else:
        # Pydantic v1 使用内部 Config 类进行配置
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
```

**关键点：**
* **类型提示 (Type Hinting):** 每个配置项（`app_name`, `debug` 等）都有一个类型提示（`str`, `bool`）。Pydantic 会自动将来自环境的字符串值转换为这些类型。例如，环境变量 `DEBUG` 的值如果是 `"true"` 或 `"1"`，会被转换成布尔值 `True`。
* **默认值:** 字段可以有默认值（例如 `app_name: str = "Demo App"`）。如果在任何其他地方都找不到值，则会使用这些默认值。
* **`Optional` 字段:** 使用 `Optional[str]` 表示该配置项不是必需的。
* **配置 (`model_config` / `class Config`):** 这是你告诉 `BaseSettings` 如何工作的地方。这里最重要的设置是 `env_file=".env"`，它指示 Pydantic 在当前目录中查找并加载一个名为 `.env` 的文件。

***

3. 配置加载的优先级

Pydantic 从多个来源加载配置。理解其优先级顺序至关重要。默认情况下，优先级顺序如下：

1.  **环境变量 (Environment Variables):** 这是最重要的来源。在你的 shell 中设置的变量（例如 `export DEBUG=true`）将始终优先于 `.env` 文件中的同名变量。
2.  **`.env` 文件:** 从 `env_file` 指定的文件中加载的值。
3.  **默认值:** 在你的 `DemoSettings` 类中直接定义的默认值。

⚠️ **关于初始化参数的说明：**
如果你在创建 `Settings` 对象时传递了参数，比如 `DemoSettings(port=9000)`，会发生什么？在标准的 `BaseSettings` 实现中，**环境变量仍然会覆盖这些初始化参数**。所提供的代码演示了这一点，并向你展示了在需要时如何更改此行为。

 实际演示

假设你有以下 `.env` 文件：

**.env**
```env
# 应用的配置
APP_NAME="来自 .env 的超棒应用"
DEBUG=true
DASHSCOPE_API_KEY="sk-envfile-xxxxxxxxxxxx"
```

并且你在终端中设置了一个环境变量：
```sh
export DEBUG=false
```

当你创建 `DemoSettings` 的实例时：
```python
settings = DemoSettings()
```

最终得到的值将是：
* `settings.app_name`: `"来自 .env 的超棒应用"` (来自 `.env` 文件)
* `settings.debug`: `False` (来自环境变量，它覆盖了 `.env` 文件中的值)
* `settings.port`: `8000` (来自类中的默认值，因为其他地方都未设置)
* `settings.dashscope_api_key`: `"sk-envfile-xxxxxxxxxxxx"` (来自 `.env` 文件)

***

4. 高级主题：覆盖环境变量

有时，你需要以编程方式设置一个配置值，即使它已经被定义为环境变量。正如我们所注意到的，`BaseSettings` 的默认行为会阻止这种情况。演示代码提供了两种解决方案。

方法一：使用 `CustomPrioritySettings` 自定义类

这是推荐的方法。你可以创建一个自定义的配置类，修改其初始化逻辑，以确保传递给构造函数 (`__init__`) 的参数具有最高优先级。

```python
class CustomPrioritySettings(BaseSettings):
    """
    一个自定义配置类，其中初始化参数会覆盖环境变量。
    """
    
    # ... (与 DemoSettings 完全相同的字段) ...
    app_name: str = "Demo App"
    debug: bool = False
    # ... 等等 ...
    
    def __init__(self, **kwargs):
        # 首先，调用父类的 __init__ 方法。这将像往常一样
        # 从环境和 .env 文件中加载值。
        super().__init__()
        
        # 现在，遍历在初始化时提供的关键字参数，
        # 并用它们来覆盖从环境中加载的任何值。
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

**工作原理：**
1.  `super().__init__()` 首先运行标准的 `BaseSettings` 初始化流程，从环境和 `.env` 文件中加载所有配置。
2.  然后，`for` 循环使用 `kwargs` 中的值来手动设置对象的属性。这有效地覆盖了刚刚从环境中加载的任何值。

**使用方法：**
```python
# 假设 DASHSCOPE_API_KEY 已被设置为环境变量。
# 使用自定义类，下面的初始化将拥有最高优先级。

settings = CustomPrioritySettings(dashscope_api_key="sk-override-from-code")

# settings.dashscope_api_key 现在将是 "sk-override-from-code"
print(f"自定义密钥: {settings.dashscope_api_key}") 
```

方法二：临时修改环境（简单直接）

如果你只需要覆盖一次值，并且不想创建自定义类，可以在创建配置实例之前临时删除环境变量。

```python
# 保存原始的环境变量
original_key = os.environ.get('DASHSCOPE_API_KEY')

# 临时删除它
if original_key:
    del os.environ['DASHSCOPE_API_KEY']

# 初始化配置。现在，初始化参数将被使用。
temp_settings = DemoSettings(dashscope_api_key="sk-init-override-success")

# 恢复环境变量，以免影响应用的其他部分
if original_key:
    os.environ['DASHSCOPE_API_KEY'] = original_key
```
这种方法可行，但通常不够简洁，不推荐在生产代码中使用。

4. 完整的演示脚本

所提供的脚本通过打印配置在每个步骤中的状态，清晰地演示了所有这些概念。这是观察优先级规则和覆盖技术如何实际运作的绝佳方式。

你可以运行该脚本并通过以下方式进行实验：
1.  创建或修改 `.env` 文件。
2.  设置和取消设置环境变量（`export DEBUG=true` 或 `unset DEBUG`）。
3.  观察最终配置如何变化。

这种动手实践的方法将巩固你对 `BaseSettings` 如何简化应用配置的理解。编码愉快！✨