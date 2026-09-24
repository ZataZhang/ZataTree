---
title: fastapi-docs_swagger_UI-openAPI
description: ""
date: 2025-09-12T14:26:46+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - FastAPI
---

FastAPI 框架在设计之初就深度集成了 OpenAPI 规范。这意味着：

  * **自动生成文档**：您无需手动编写任何 OpenAPI (Swagger) 配置文件。FastAPI 会自动分析您的代码、路径操作、参数和模型，并生成符合规范的 JSON 文件。
  * **内置交互式界面**：FastAPI 默认就包含了两个交互式的 API 文档界面：Swagger UI 和 ReDoc。您无需进行任何额外配置，开箱即用。
  * **代码即文档**：您的代码就是文档的唯一真实来源。当您修改了代码（例如，添加一个新参数），文档会自动更新，保证了同步性。

-----

### 步骤 1：环境准备

首先，我们需要安装 FastAPI 和一个 ASGI 服务器，这里我们使用 `uvicorn`。

```bash
pip install fastapi "uvicorn[standard]"
```

`"uvicorn[standard]"` 会安装 uvicorn 以及一些推荐的依赖，以获得更好的性能。

-----

### 步骤 2：创建一个简单的 FastAPI 应用

让我们从一个最基础的 "Hello World" 应用开始。创建一个名为 `main.py` 的文件，并写入以下代码：

```python
# main.py
from fastapi import FastAPI

# 1. 创建一个 FastAPI 实例
app = FastAPI()

# 2. 定义一个路径操作 (Path Operation)
@app.get("/")
def read_root():
    return {"Hello": "World"}
```

**代码解释**：

1.  我们导入 `FastAPI` 类并创建了一个实例 `app`。
2.  我们使用 `@app.get("/")` 这个**装饰器 (decorator)** 来告诉 FastAPI，下面的 `read_root` 函数负责处理对路径 `/` 的 `GET` 请求。
3.  函数返回一个字典，FastAPI 会自动将其转换为 JSON 格式的响应。

-----

### 步骤 3：运行应用并查看文档

现在，在您的终端中，使用 uvicorn 来运行这个应用：

```bash
uvicorn main:app --reload
```

  * `main`: 指的是 `main.py` 文件。
  * `app`: 指的是在 `main.py` 中创建的 `app = FastAPI()` 对象。
  * `--reload`: 这个参数会让服务器在您修改代码后自动重启，非常适合开发阶段。

服务器启动后，您会看到类似下面的输出：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12347]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

现在，打开您的浏览器，见证奇迹的时刻到了！

1.  **访问 Swagger UI**:

      * 在浏览器中输入：**`http://127.0.0.1:8000/docs`**

    您将看到一个漂亮的、交互式的 API 文档界面，这正是由 Swagger UI 生成的。

2.  **访问 ReDoc**:

      * 在浏览器中输入：**`http://127.0.0.1:8000/redoc`**

    您会看到另一个由 ReDoc 生成的、风格不同的文档界面。

-----

### 步骤 4：通过示例深入理解

光有 "Hello World" 还不够，让我们添加更复杂的路径操作来探索 FastAPI 是如何生成更丰富的文档的。

修改您的 `main.py` 文件：

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# --- 模型定义 ---
# 使用 Pydantic 定义请求体的数据结构
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# --- FastAPI 应用实例 ---
app = FastAPI(
    title="我的超酷 API",
    description="这是一个使用 FastAPI 构建的示例 API，它展示了自动生成的交互式文档。",
    version="1.0.0",
)

# --- 路径操作 ---

@app.get("/")
def read_root():
    """
    应用的根路径，返回一个欢迎信息。
    """
    return {"Hello": "World"}

@app.get("/items/{item_id}", tags=["Items"])
def read_item(item_id: int, q: Optional[str] = None):
    """
    根据 ID 读取一个物品。

    - **item_id**: 必需的路径参数，必须是整数。
    - **q**: 可选的查询参数。
    """
    return {"item_id": item_id, "q": q}

@app.post("/items/", response_model=Item, tags=["Items"])
def create_item(item: Item):
    """
    创建一个新的物品。

    请求体需要包含物品的详细信息：
    - **name**: 物品名称 (必需)
    - **price**: 物品价格 (必需)
    - **description**: 物品描述 (可选)
    - **tax**: 税费 (可选)
    """
    return item
```

**代码详解与文档对应关系**：

1.  **自定义文档信息**：

      * `app = FastAPI(title="...", description="...", version="...")`
      * 这些参数会直接显示在 Swagger UI 的顶部，用来定义您的 API 的元数据。

2.  **路径参数 (`/items/{item_id}`)**：

      * `item_id: int`：FastAPI 知道 `item_id` 是路径的一部分，并且通过类型注解 `int` 知道它必须是一个整数。
      * **在 Swagger UI 中**：这会被识别为一个必需的、类型为 `integer` 的 `path` 参数。

3.  **查询参数 (`?q=...`)**：

      * `q: Optional[str] = None`：FastAPI 看到这个函数参数不属于路径，所以它将其视为查询参数。`Optional[str]` 和默认值 `None` 告诉 FastAPI 这个参数是可选的。
      * **在 Swagger UI 中**：这会被识别为一个可选的、类型为 `string` 的 `query` 参数。

4.  **请求体 (`Request Body`)**：

      * `item: Item`：我们定义了一个 `Item` 类，它继承自 Pydantic 的 `BaseModel`。FastAPI 会将这个参数识别为请求体。
      * **在 Swagger UI 中**：它会自动生成一个请求体的示例 (`Example Value`) 和模型结构 (`Schema`)，清楚地展示了需要发送的 JSON 格式。

5.  **文档字符串 (`Docstrings`)**：

      * 函数下方的多行字符串（`"""..."""`）会被 FastAPI 提取出来，作为对应路径操作的描述，显示在 Swagger UI 中。这是一种非常 Pythonic 的文档编写方式。

6.  **标签 (`tags=["Items"]`)**：

      * 通过 `tags` 参数，我们可以将相关的路径操作分组。
      * **在 Swagger UI 中**：您会看到一个名为 "Items" 的可折叠部分，里面包含了所有标记为此标签的端点，让文档结构更清晰。

-----

### 步骤 5：再次运行并交互

保存您的 `main.py` 文件。如果 uvicorn 正在以 `--reload` 模式运行，它会自动重启。

现在，**刷新您的 Swagger UI 页面 (`http://127.0.0.1:8000/docs`)**。

您会看到一个内容更丰富、结构更清晰的文档：

**让我们来交互一下**：

1.  **展开 `GET /items/{item_id}`**：

      * 点击 "Try it out" 按钮。
      * 在 `item_id` 字段中输入一个数字，例如 `123`。
      * 在可选的 `q` 字段中输入一些文本，例如 `some-query`。
      * 点击 "Execute" 按钮。

    下方会立刻显示出服务器的响应、请求的 `curl` 命令以及请求的 URL。

2.  **展开 `POST /items/`**：

      * 点击 "Try it out"。
      * 请求体 (`Request body`) 区域会变成一个可编辑的 JSON 编辑器，并且已经填好了示例。
      * 您可以修改 JSON 中的值。
      * 点击 "Execute"。

    您将看到 FastAPI 如何验证您的输入，并返回一个符合 `response_model=Item` 结构的数据。

### 总结

通过这个示例，您可以看到 FastAPI 如何将编写代码和生成 API 文档的过程无缝地结合在一起。您只需要专注于使用 Python 的类型注解和 Pydantic 模型来编写健壮的、类型安全的代码，一份美观、实用且始终保持最新的交互式 API 文档便会自动为您生成。这是 FastAPI 框架最强大的特性之一，也是它深受开发者喜爱的重要原因。