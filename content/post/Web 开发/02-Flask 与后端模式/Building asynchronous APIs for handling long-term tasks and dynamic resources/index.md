---
title: Building asynchronous APIs for handling long-term tasks and dynamic resources
description: ""
date: 2025-10-20T15:59:14+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - others
---

# 教程：构建处理长时间任务和动态资源的异步 API

这是一个关于如何构建一个健壮的后端系统的教程，该系统用于处理你所描述的场景：一个API接口，用于调用一个可能执行很久、并且需要动态管理并发资源（例如，受限于CPU/内存/GPU）的函数。

我们将使用**异步任务队列**架构，这是解决此类问题的行业标准。

## 核心问题

为什么不能直接在API接口中调用这个耗时函数？

1.  **HTTP 超时**：客户端（浏览器、APP）等待HTTP响应的时间是有限的（通常是30-60秒）。如果你的函数执行5分钟，客户端将收到一个“超时”错误，即使用户的任务最终成功了。
2.  **服务器资源耗尽**：Web服务器（如 Uvicorn, Gunicorn）的工作进程是有限的。如果5个用户同时请求这个耗时5分钟的接口，你的5个Web进程将被全部占用，导致服务器在接下来的5分钟内无法响应**任何其他**请求（例如登录、获取数据等），服务器会“假死”。

## 解决方案：异步任务队列

我们将系统拆分为三个组件：

1.  **API 服务器 (Web Server)**：一个轻量级的接口。它只负责接收请求，验证参数，然后把“任务”丢进一个队列，最后**立即**返回一个`任务ID`给客户端。
2.  **任务队列 (Message Broker)**：一个中间件（我们使用 **Redis**）。它像一个“待办事项”列表，负责存储API服务器发来的任务。
3.  **工作单元 (Worker)**：一个（或多个）**独立于API服务器运行的进程**。它唯一的工作就是盯着任务队列，一旦有新任务，就取出来执行。

这种架构如何解决你的问题：
* **长时间执行**：API在1毫秒内就返回了响应（`{"task_id": "xxx"}`），客户端不需等待。客户端可以稍后使用`task_id`来轮询另一个接口查询结果。
* **动态资源**：你可以根据服务器的资源（CPU、内存）来决定启动多少个Worker进程，或者配置每个Worker**同时执行多少个任务**。这就是你的“动态并发控制”。

---

## 技术栈

* **API 服务器**: **FastAPI** (高性能Python Web框架)
* **任务队列系统**: **Celery** (Python中最流行的任务队列)
* **消息中间件 / 结果存储**: **Redis** (速度极快，Celery的完美搭档)

---

## 第 1 步：环境准备

1.  **安装 Python 库**:
    ```bash
    pip install "fastapi[all]" celery redis
    ```
    * `fastapi[all]`：安装FastAPI及Uvicorn服务器。
    * `celery`：Celery 框架。
    * `redis`：Celery连接Redis所需的Python客户端。

2.  **启动 Redis**:
    最简单的方式是使用 Docker。如果你没有Docker，请从[官网](https://redis.io/topics/quickstart)下载并运行。

    ```bash
    # 这将在后台启动一个Redis服务器，端口为 6379
    docker run -d -p 6379:6379 redis
    ```

---

## 第 2 步：项目结构

创建两个文件：

````

/your\_project
├── tasks.py     \# 定义 Celery 应用和“耗时函数”
└── main.py      \# 定义 FastAPI 接口

````

---

## 第 3 步：编写 Worker 和任务 (`tasks.py`)

这是你“耗时函数”的真正定义之处。

```python
# tasks.py

import time
from celery import Celery

# 1. 初始化 Celery
# 'tasks' 是当前模块的名称
# broker 是任务队列，使用 Redis 的 0 号数据库
# backend 是结果存储，使用 Redis 的 1 号数据库
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 2. 定义你那个“耗时很长、需要动态资源”的函数
# @celery_app.task 装饰器将其注册为 Celery 任务

@celery_app.task
def run_long_analysis(dataset_id: str, complexity: int) -> dict:
    """
    这是一个模拟的耗时任务。
    在真实世界中，这里可能是：
    - 运行一个复杂的AI模型
    - 生成一份巨大的报表
    - 转码一个视频文件
    - 调用第三方的慢速 API
    """
    
    print(f"[任务开始] 正在分析数据集 {dataset_id}，复杂度 {complexity}...")
    
    try:
        # 模拟长时间工作
        # 复杂度越高，工作时间越长
        duration = complexity * 5 
        time.sleep(duration)
        
        # 模拟资源消耗... (这部分由 Celery 的并发设置来控制)
        
        # 任务执行完毕，返回结果
        result = {
            "status": "success",
            "dataset_id": dataset_id,
            "analysis_time_sec": duration,
            "result_url": f"[http://example.com/results/](http://example.com/results/){dataset_id}.zip"
        }
        print(f"[任务成功] {dataset_id} 分析完毕。")
        return result
        
    except Exception as e:
        # 异常处理
        print(f"[任务失败] {dataset_id} 分析失败: {e}")
        return {"status": "failed", "error": str(e)}

````

-----

## 第 4 步：编写 API 接口 (`main.py`)

这是客户端唯一能“看到”的部分。

```python
# main.py

from fastapi import FastAPI, status
from pydantic import BaseModel
from celery.result import AsyncResult

# 1. 导入在 tasks.py 中定义的任务和app
from tasks import run_long_analysis, celery_app

# 初始化 FastAPI
app = FastAPI(title="异步任务API", description="使用 FastAPI 和 Celery")

# 2. 定义 API 的请求体（Pydantic模型）
class TaskRequest(BaseModel):
    dataset_id: str
    complexity: int  # 复杂度，1-10

# 3. 定义 API 的响应体
class TaskResponse(BaseModel):
    message: str
    task_id: str


# === 接口 1: 启动任务 ===
# 状态码 202 (Accepted) 表示“已接受，正在处理”
@app.post("/api/v1/start-analysis", status_code=status.HTTP_202_ACCEPTED, response_model=TaskResponse)
def start_analysis(request: TaskRequest):
    """
    接收分析请求，将其放入任务队列，并立即返回任务ID。
    """
    
    # 关键: .delay()
    # 这不会在当前进程中执行函数，而是将任务消息发送到 Redis 队列
    task = run_long_analysis.delay(request.dataset_id, request.complexity)
    
    # 立即返回响应
    return {
        "message": "任务已接收，正在后台处理",
        "task_id": task.id
    }


# === 接口 2: 查询任务状态/结果 ===
@app.get("/api/v1/task-status/{task_id}")
def get_task_status(task_id: str):
    """
    根据任务ID查询任务的状态和结果。
    """
    
    # 使用 Celery 的 AsyncResult 从 Backend (Redis) 中获取结果
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.ready():
        # 任务已完成
        if task_result.successful():
            # 任务成功
            return {
                "task_id": task_id,
                "status": task_result.status, # "SUCCESS"
                "result": task_result.result  # run_long_analysis 返回的字典
            }
        else:
            # 任务失败
            return {
                "task_id": task_id,
                "status": task_result.status, # "FAILURE"
                "error": str(task_result.info) # 异常信息
            }
    else:
        # 任务仍在进行中
        return {
            "task_id": task_id,
            "status": task_result.status # "PENDING" 或 "STARTED"
        }

```

-----

## 第 5 步：运行系统（关键）

你需要**启动 3 个独立的进程**（打开 3 个终端窗口）。

**终端 1: 运行 Redis** (如果你还没启动)

```bash
docker run -d -p 6379:6379 redis
```

**终端 2: 运行 Celery Worker (耗时函数的执行者)**
这是管理你“动态资源”的地方。

```bash
# -A tasks: 指定 Celery 应用在 tasks.py 文件中的 celery_app
# worker: 启动工作单元
# --loglevel=info: 打印日志
# --concurrency=4: !!! 核心控制 !!! 
#                  这表示这个 Worker 进程“同时”最多执行 4 个任务。
#                  如果你的机器有 16 核 CPU，并且资源充足，可以设为 16。
#                  如果你的函数非常吃内存，可能只能设为 2。
#                  这就是你的“动态资源管理”。
celery -A tasks worker --loglevel=info --concurrency=4
```

  * **如何扩展?** 如果一台机器的 `concurrency=4` 不够用，你可以在**另一台**机器上也运行这个命令，它们会连接同一个Redis，自动分担任务！

**终端 3: 运行 API 服务器**

```bash
# uvicorn 会运行 main.py 中的 app
uvicorn main:app --reload
```

  * `--reload` 模式会在你修改代码后自动重启，方便开发。

-----

## 第 6 步：测试

现在你的整套系统都跑起来了。

**1. 启动一个任务 (POST)**
我们请求一个 复杂度为 3 的任务（即 `3 * 5 = 15` 秒）。

```bash
curl -X POST "[http://127.0.0.1:8000/api/v1/start-analysis](http://127.0.0.1:8000/api/v1/start-analysis)" \
     -H "Content-Type: application/json" \
     -d '{"dataset_id": "data_xyz", "complexity": 3}'
```

你将**立即**收到响应：

```json
{
  "message": "任务已接收，正在后台处理",
  "task_id": "a9b1c8d2-....."
}
```

  * 同时，在**终端 2 (Worker)** 的日志中，你会看到它打印了 `[任务开始] ...`。

**2. 查询任务状态 (GET) - 5秒后**
使用上一步中获取的 `task_id`。

```bash
curl "[http://127.0.0.1:8000/api/v1/task-status/a9b1c8d2-](http://127.0.0.1:8000/api/v1/task-status/a9b1c8d2-)....."
```

因为任务还在运行（总共要15秒），你会收到：

```json
{
  "task_id": "a9b1c8d2-.....",
  "status": "PENDING" 
}
```

**3. 查询任务状态 (GET) - 20秒后**
再次运行上一个命令：

```bash
curl "[http://127.0.0.1:8000/api/v1/task-status/a9b1c8d2-](http://127.0.0.1:8000/api/v1/task-status/a9b1c8d2-)....."
```

现在任务完成了，你会收到：

```json
{
  "task_id": "a9b1c8d2-.....",
  "status": "SUCCESS",
  "result": {
    "status": "success",
    "dataset_id": "data_xyz",
    "analysis_time_sec": 15,
    "result_url": "[http://example.com/results/data_xyz.zip](http://example.com/results/data_xyz.zip)"
  }
}
```

## 总结

你已经成功构建了一个可扩展、健壮的异步任务系统。

  * **API 接口** (`main.py`)：轻量且响应迅速。
  * **耗时函数** (`tasks.py`)：在后台的 Worker 中独立运行。
  * **资源管理**：通过 `celery worker --concurrency=N` 来精确控制并发数，N就是你根据“动态资源”决定的数量。

<!-- end list -->

```