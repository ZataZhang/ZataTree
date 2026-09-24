---
title: fastapi-前提知识
description: ""
date: 2025-04-01T14:37:44+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - FastAPI
---


### 1. Python 基础
FastAPI 是基于 Python 的框架，因此你需要熟悉 Python 3.6+ 的基本语法和特性。以下是关键点：

#### 1.1 变量和数据类型
- Python 使用动态类型，无需显式声明变量类型。
- 常用数据类型：整数（`int`）、浮点数（`float`）、字符串（`str`）、列表（`list`）、字典（`dict`）。

```python
name = "Alice"  # 字符串
age = 25       # 整数
scores = [90, 85, 88]  # 列表
person = {"name": "Alice", "age": 25}  # 字典
```

#### 1.2 函数和类型注解
- 定义函数使用 `def` 关键字。
- FastAPI 大量使用 Python 的类型注解（Type Hints），需要熟悉。

```python
# 基本函数
def add(a, b):
    return a + b

# 带类型注解的函数
def add_with_types(a: int, b: int) -> int:
    return a + b

print(add(3, 5))         # 输出: 8
print(add_with_types(3, 5))  # 输出: 8
```

类型注解是 FastAPI 的核心特性，用于参数验证和自动生成文档。

#### 1.3 类和对象
- FastAPI 使用 Pydantic 模型（基于类），需要理解面向对象编程基础。

```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, I'm {self.name}!"

alice = Person("Alice", 25)
print(alice.greet())  # 输出: Hello, I'm Alice!
```

#### 1.4 模块和包
- Python 使用 `import` 引入模块，FastAPI 是一个外部包。
- 安装包使用 `pip`，例如：`pip install fastapi`。

```python
import math
print(math.sqrt(16))  # 输出: 4.0
```

#### 1.5 异常处理
- 使用 `try` 和 `except` 处理错误，FastAPI 中常用。

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")
```

---

### 2. 异步编程基础
FastAPI 是异步框架，基于 Python 的 `asyncio` 库。你需要理解异步编程的核心概念：`async` 和 `await`。

#### 2.1 同步 vs 异步
- **同步**：代码按顺序执行，等待每个操作完成。
- **异步**：可以在等待某个操作（如网络请求）时执行其他任务。

```python
# 同步示例
def sync_task():
    print("任务开始")
    print("任务结束")

sync_task()
```

```python
# 异步示例
import asyncio

async def async_task():
    print("任务开始")
    await asyncio.sleep(1)  # 模拟耗时操作
    print("任务结束")

asyncio.run(async_task())
```

#### 2.2 `async` 和 `await`
- `async def` 定义异步函数。
- `await` 用于暂停执行，等待异步操作完成。

```python
import asyncio

async def say_hello():
    print("Hello")
    await asyncio.sleep(2)  # 等待 2 秒
    print("World")

# 运行异步函数
asyncio.run(say_hello())
```

#### 2.3 多个异步任务
- 使用 `asyncio.gather` 并发运行多个异步任务。

```python
import asyncio

async def task1():
    await asyncio.sleep(1)
    print("任务 1 完成")

async def task2():
    await asyncio.sleep(2)
    print("任务 2 完成")

async def main():
    await asyncio.gather(task1(), task2())

asyncio.run(main())
# 输出:
# 任务 1 完成 (1秒后)
# 任务 2 完成 (2秒后)
```

FastAPI 使用异步来处理多个请求，提高性能，因此理解这些概念至关重要。

---

### 3. HTTP 协议基础
FastAPI 是一个 Web 框架，基于 HTTP 协议。你需要了解 HTTP 的基本工作原理。

#### 3.1 HTTP 请求和响应
- **请求**：客户端（如浏览器）向服务器发送的操作。
- **响应**：服务器返回的数据。

请求示例（伪代码）：
```
GET /hello HTTP/1.1
Host: example.com
```

响应示例：
```
HTTP/1.1 200 OK
Content-Type: text/plain

Hello, World!
```

#### 3.2 HTTP 方法
- **GET**：获取数据。
- **POST**：提交数据。
- **PUT**：更新数据。
- **DELETE**：删除数据。

FastAPI 使用这些方法定义路由，例如：
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def read_hello():
    return {"message": "Hello, World!"}
```

#### 3.3 状态码
- **200 OK**：成功。
- **404 Not Found**：资源未找到。
- **500 Internal Server Error**：服务器错误。

FastAPI 会自动返回状态码，你也可以手动指定：
```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id > 0:
        return {"item_id": item_id}
    raise HTTPException(status_code=404, detail="Item not found")
```

#### 3.4 请求头和正文
- **请求头**：元数据，如 `Content-Type`。
- **请求正文**：发送的数据，通常是 JSON。

FastAPI 使用 Pydantic 处理请求正文：
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

#### 3.5 URL 和查询参数
- URL 路径：如 `/items/123`。
- 查询参数：如 `/items/?q=test`。

FastAPI 示例：
```python
@app.get("/items/")
def read_items(q: str = None):
    return {"query": q}
```

---

### 4. 实践练习
结合以上知识，尝试以下练习：
1. 编写一个带类型注解的函数，计算两个数的和。
2. 创建一个异步函数，模拟等待 3 秒后返回结果。
3. 安装 FastAPI 和 Uvicorn，运行一个简单的 GET 路由，返回 JSON 数据。

示例答案：
```python
# 练习 1
def sum_numbers(a: int, b: int) -> int:
    return a + b

# 练习 2
import asyncio
async def wait_and_return():
    await asyncio.sleep(3)
    return "等待结束"

# 练习 3
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
# 运行：uvicorn main:app --reload
```

---
