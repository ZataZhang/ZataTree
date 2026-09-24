---
title: Celery
description: ""
date: 2025-10-20T17:12:13+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - others
---


## Celery 详细使用教程：从入门到实践

### 什么是 Celery？

Celery 是一个强大、简单、灵活的**分布式异步任务队列 (Asynchronous Task Queue)**。它主要用于处理那些耗时较长或者可以稍后执行的任务，从而避免阻塞主程序（例如一个 Web 请求）。

**主要使用场景：**

  * **异步任务：** 用户注册后发送欢迎邮件、处理用户上传的图片（缩放、加水印）、生成复杂的报表。
  * **定时任务：** 每天凌晨清理一次数据、每小时从第三方 API 同步一次信息。

### 核心概念

要理解 Celery，你必须先了解它的四个核心组件：

1.  **生产者 (Producer)：** 也就是你的主程序（例如 Flask/Django 应用）。它负责创建任务并将其发送到任务队列中。
2.  **Broker (消息中间件)：** 任务的“信箱”或“中转站”。生产者将任务放入 Broker，Worker 从 Broker 中取出任务。最常用的 Broker 是 **RabbitMQ**（功能最全，官方推荐）和 **Redis**（轻量，易于上手）。
3.  **Worker (消费者)：** 真正执行任务的进程。它会持续监控 Broker，一旦发现新任务，就取出并执行它。你可以同时运行多个 Worker 来实现分布式处理。
4.  **Backend (结果存储)：** （可选）用于存储任务执行结果的地方。如果你需要稍后查询任务的状态或返回值（例如，在网页上显示“报表已生成”），你就需要配置 Backend。常用的 Backend 包括 **Redis**、**RabbitMQ** (amqp) 或数据库 (SQLAlchemy)。

**工作流程：**
`生产者 (App)` -\> `发送任务` -\> `Broker (Redis/RabbitMQ)` -\> `Worker (领取任务)` -\> `执行任务` -\> `(可选) 存入结果` -\> `Backend (Redis/DB)`

-----

### 第一部分：快速入门 (Hello, World)

我们将使用 **Redis** 作为 Broker 和 Backend，因为它安装简单，配置方便。

第1步：环境准备

确保你已经安装了 Python 和 Redis。

1.  **安装 Redis：**

      * (macOS) `brew install redis`，然后 `redis-server`
      * (Linux) `sudo apt install redis-server`
      * (Windows) 建议使用 WSL2 或 Docker。
      * 确保 Redis 服务正在 `localhost:6379` 上运行。

2.  **安装 Python 库：**

    ```bash
    pip install celery redis
    ```

第2步：创建 Celery 应用和任务

创建一个名为 `tasks.py` 的文件。

```python
import time
from celery import Celery

# 1. 创建 Celery 实例
# 第一个参数 'tasks' 是当前模块的名称，这在自动生成任务名时很重要。
# broker 和 backend 都指向我们的 Redis 服务。
# /0 和 /1 代表 Redis 的不同数据库 (db)，避免数据混淆。
app = Celery('tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/1')

# 2. 定义一个任务
# @app.task 装饰器将这个函数注册为 Celery 任务
@app.task
def add(x, y):
    print(f"开始执行任务: {x} + {y}")
    time.sleep(5)  # 模拟一个耗时的操作
    result = x + y
    print(f"任务执行完毕: {result}")
    return result

@app.task
def send_email(to, subject, body):
    print(f"向 {to} 发送邮件...")
    time.sleep(3) # 模拟I/O操作
    print(f"邮件发送成功: 主题 {subject}")
    return "Success"
```

第3步：运行 Celery Worker

**打开一个终端**，cd 到 `tasks.py` 所在的目录，然后运行 Worker 进程：

```bash
# -A tasks: 指定 Celery 实例 (app) 在 'tasks' 模块中
# worker: 启动 worker 进程
# --loglevel=info: 设置日志级别为 INFO，方便我们观察
celery -A tasks worker --loglevel=info
```

如果一切正常，你会看到一个 ASCII art 组成的 Celery Logo，并提示 `[tasks]... ready.`。这表示 Worker 已经连接到 Redis 并准备好接收任务了。

第4步：调用任务

**打开第二个终端**（保持 Worker 终端运行），进入 Python 交互环境（如 `ipython` 或 `python`）：

```python
>>> from tasks import add, send_email

# 1. 异步调用任务
# .delay() 是 .apply_async() 的快捷方式
# 注意：这行代码会 *立即* 返回，不会等待 5 秒
print("准备调用 add(4, 4)...")
task_result = add.delay(4, 4)
print("任务已发送，ID:", task_result.id)

# 2. 尝试调用另一个任务
print("准备发送邮件...")
email_task = send_email.delay("user@example.com", "你好", "这是一封测试邮件。")
print("邮件任务已发送，ID:", email_task.id)

# 3. 查看 Worker 终端
# 此时，你应该能在第一个终端（Worker 终端）看到任务开始执行的日志。
```

第5步：获取任务结果

在**第二个终端**（Python 交互环境）中，我们可以使用 `task_result` 对象（它是一个 `AsyncResult` 实例）来检查任务状态和获取结果：

```python
>>> # 检查任务是否完成
>>> task_result.ready()
False  # (可能还是 False，因为任务在 sleep(5))

# (等待几秒钟)

>>> task_result.ready()
True

>>> # 获取任务状态
>>> task_result.status
'SUCCESS'

>>> # 获取任务的返回值
>>> # .get() 会阻塞当前进程，直到拿到结果
>>> result_value = task_result.get()
>>> print(result_value)
8

>>> # 检查邮件任务
>>> email_task.get()
'Success'

>>> # 如果任务执行出错
>>> # 你可以通过 .status 查看
# 假设我们定义了一个出错的任务
# task_error = error_task.delay()
# task_error.status
# 'FAILURE'
# task_error.get() # 这将会抛出异常
```

-----

### 第二部分：与 Web 框架集成 (以 FastAPI 为例)

在真实项目中，你通常会在 Web 应用（如 FastAPI）中调用 Celery 任务。FastAPI 是一个现代、高性能的 Python Web 框架，基于 ASGI，支持异步操作，与 Celery 集成非常自然。

项目结构

```
my_fastapi_project/
├── main.py          # FastAPI 应用
├── celery_app.py    # Celery 实例和配置
├── tasks.py         # 任务定义
└── requirements.txt
```

**requirements.txt 示例（添加 FastAPI 相关依赖）：**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
celery==5.3.6
redis==5.0.1
```

第1步：配置 Celery (`celery_app.py`)

创建一个中心化的 Celery 实例。由于 FastAPI 没有内置的 `app.config`，我们使用一个配置字典来传递参数。

```python
# celery_app.py
from celery import Celery

# 创建 Celery 实例
celery = Celery(__name__)

# 从配置中加载 Celery 配置
def init_celery(app, config):
    celery.conf.update(config)

    # (可选) 让任务可以使用 FastAPI 的 app context（如果任务需要访问 app 状态）
    # FastAPI 没有传统的 app_context，但我们可以用类似方式处理依赖
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # 这里可以注入 FastAPI 的依赖，如果需要
            # 对于简单任务，可省略
            return self.run(*args, **kwargs)

    celery.Task = ContextTask
```

第2步：定义任务 (`tasks.py`)

任务定义与 Flask 示例相同，几乎无需改动。

```python
# tasks.py
import time
from celery_app import celery

# 注意：我们现在从 celery_app 导入 celery 实例
@celery.task
def long_running_simulation(user_id):
    print(f"开始为用户 {user_id} 运行模拟...")
    time.sleep(10)  # 模拟一个非常耗时的操作
    print(f"用户 {user_id} 的模拟运行完毕。")
    return f"Report for {user_id}"
```

第3步：配置 FastAPI (`main.py`)

```python
# main.py
from fastapi import FastAPI, Query
from celery_app import celery, init_celery
from tasks import long_running_simulation

app = FastAPI()

# 配置（这里直接定义，也可以用环境变量或 pydantic-settings）
config = {
    # Celery Broker
    "CELERY_BROKER_URL": "redis://localhost:6379/0",
    # Celery Backend
    "CELERY_RESULT_BACKEND": "redis://localhost:6379/1"
}

# 初始化 Celery
init_celery(app, config)

@app.get("/")
def index():
    return {"message": "你好, Celery 和 FastAPI!"}

@app.get("/start-task")
def start_task(user_id: str = Query("default_user", description="用户 ID")):
    # 这是一个 Web 请求，我们不想让它等待 10 秒
    # 我们立即将任务推送到队列
    task = long_running_simulation.delay(user_id)

    # 立即返回，并告诉前端任务 ID
    return {
        "message": "任务已启动",
        "task_id": task.id
    }, 202  # 202 Accepted 表示请求已被接受，正在处理

@app.get("/task-status/{task_id}")
def task_status(task_id: str):
    # 从 Backend 查询任务状态
    task_result = long_running_simulation.AsyncResult(task_id)

    if task_result.state == "PENDING":
        # 任务还在队列中，或刚开始
        response = {
            "state": task_result.state,
            "status": "Pending..."
        }
    elif task_result.state != "FAILURE":
        response = {
            "state": task_result.state,
            "status": "In progress...",
        }
        if task_result.state == "SUCCESS":
            response["result"] = task_result.get()  # 获取最终结果
        else:
            response["result"] = task_result.info  # 如果任务正在进行，.info 可能包含中间状态
    else:
        # 任务失败
        response = {
            "state": task_result.state,
            "status": str(task_result.info),  # 失败的异常信息
        }
    return response
```

**注意：**
- FastAPI 支持自动生成 OpenAPI 文档，你可以访问 `/docs` 查看交互式 API 文档。
- 如果需要异步路由，可以将 `@app.get` 改为 `async def`，但这里任务是同步的 Celery 调用，无需。

第4步：运行

你需要运行**两个**服务（确保 Redis 已启动）：

1. **终端 1 (Celery Worker)：**

    ```bash
    # -A 参数指向 celery 实例所在的模块
    # 指向 tasks.py 中导入的 celery 实例
    celery -A tasks.celery worker --loglevel=info
    ```

    *（注：更健壮的方式是使用 `celery -A celery_app.celery worker`，取决于你的 `__name__` 设置。指向 `tasks.celery` 通常可行。）*

2. **终端 2 (FastAPI App)：**

    ```bash
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
    ```

**测试：**

1. 访问 `http://127.0.0.1:8000/start-task?user_id=123`
   - 你会 *立即* 收到一个 JSON 响应，包含 `task_id`。
   - 同时，观察 Worker 终端，你会看到它开始执行 `long_running_simulation`。
2. 复制那个 `task_id`。
3. 访问 `http://127.0.0.1:8000/task-status/{your_task_id}`
   - 一开始，你可能会看到 "Pending" 或 "In progress"。
   - 等待 10 秒后刷新，你会看到 "SUCCESS" 和 `result: "Report for 123"`。

   *额外：访问 `http://127.0.0.1:8000/docs` 查看 Swagger UI，方便测试 API。*

-----

这个示例保持了与 Flask 版本的相似性，便于迁移。如果你的项目需要数据库集成或其他依赖，可以在 Celery 任务中使用 FastAPI 的依赖注入系统进一步扩展。


### 第三部分：定时任务 (Celery Beat)

Celery Beat 是一个**调度器 (Scheduler)**。它负责按计划将任务发送到 Broker，而 Worker 负责执行它们。

第1步：配置 Beat

在你的 Celery 配置中（例如 `celery_app.py` 或 `tasks.py`）添加 `beat_schedule`：

```python
# 在 tasks.py 中
from celery.schedules import crontab

# ... (app = Celery(...) 的定义) ...

@app.task
def periodic_task():
    print("这是一个每 30 秒执行一次的定时任务！")

# 配置定时任务
app.conf.beat_schedule = {
    # 任务名称
    'run-every-30-seconds': {
        'task': 'tasks.periodic_task', # 任务的完整路径名
        'schedule': 30.0,             # 每 30 秒
        'args': ()                    # 任务参数（这里没有）
    },
    # 也可以使用 crontab
    'run-every-midnight': {
        'task': 'tasks.add',
        'schedule': crontab(minute=0, hour=0), # 每天午夜
        'args': (100, 200),
    }
}

# (可选) 设置时区，确保 crontab 按你期望的时区执行
app.conf.timezone = 'Asia/Shanghai'
```

第2步：运行 Beat

要运行定时任务，你**至少**需要两个进程：

1.  **Worker 进程**（用于执行任务）：
    ```bash
    celery -A tasks worker --loglevel=info
    ```
2.  **Beat 进程**（用于调度任务）：
    ```bash
    celery -A tasks beat --loglevel=info
    ```

**快捷方式（开发时用）：**

你也可以在一个命令中同时启动 Worker 和 Beat（不推荐在生产环境中使用 `-B`）：

```bash
# -B 选项表示同时启动一个嵌入的 Beat 进程
celery -A tasks worker -B --loglevel=info
```

启动后，你将看到 Worker 终端每 30 秒打印一次 "这是一个每 30 秒执行一次的定时任务！"。

-----

### 第四部分：监控与最佳实践

1\. 监控：Flower

Flower 是一个基于 Web 的 Celery 监控工具。

1.  **安装：**
    ```bash
    pip install flower
    ```
2.  **运行：**
    ```bash
    # 指向你的 Celery app，并启动 flower
    celery -A tasks flower --port=5555
    ```
3.  访问 `http://localhost:5555`，你将看到一个仪表盘，显示所有 Worker 的状态、已完成的任务、队列中的任务等。

2\. 任务重试

网络抖动或临时性错误很常见。Celery 允许你轻松地重试任务。

```python
import requests

# bind=True: 将任务实例 (self) 作为第一个参数注入
# max_retries: 最大重试次数
# default_retry_delay: 默认重试间隔（秒）
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_api_data(self, url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # 如果是 4xx/5xx 错误，抛出异常
        return response.json()
    except requests.exceptions.RequestException as exc:
        print(f"请求失败: {exc}。正在重试...")
        # self.retry() 会抛出一个 Retry 异常，Celery 会捕获它并稍后重试
        # exc=exc 会将原始异常信息传递下去
        raise self.retry(exc=exc)
```

3\. 关键配置项

在生产环境中，你可能需要调整一些配置：

  * `task_serializer`: 推荐使用 `json` 或 `pickle`。`json` 更安全，但支持的数据类型有限。
  * `result_serializer`: 同上。
  * `task_track_started`: (True) 是否在任务开始执行时就将其状态报告为 "STARTED"。
  * `worker_concurrency`: Worker 进程数，默认是 CPU 核心数。可以根据任务是 I/O 密集型还是 CPU 密集型来调整。
  * `task_acks_late`: (False) 默认情况下，Worker 在 *收到* 任务后立即向 Broker 发送确认（ack），然后才执行。如果 Worker 在执行中崩溃，任务会丢失。
      * 如果设置为 `True`，Worker 会在任务 *执行完毕* 后才发送 ack。如果 Worker 崩溃，Broker 会将任务重新分配给其他 Worker。这保证了任务至少被执行一次（但可能重复执行），称为“at-least-once delivery”。



### 其他知识点


#### shared_task与app.task的区别

@shared_task 是 Celery 中一个非常重要且常用的装饰器。它的核心作用是创建可复用的、不依赖于任何特定 Celery 应用实例（app instance）的任务。

这使得它在编写可插拔的 Django、fastapi 应用、库或任何希望与项目主 Celery 应用解耦的模块时，成为首选的工具。

核心理念：为什么需要 shared_task？
在标准的 Celery 设置中，你可能会这样定义一个任务：

```Python

# myproject/celery.py
from celery import Celery
app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')

# myproject/myapp/tasks.py
from myproject.celery import app

@app.task
def add(x, y):
    return x + y
    
```
这种方法的问题在于，myapp/tasks.py 模块硬编码了对 myproject.celery.app 实例的导入。

想象一下，如果你正在编写一个希望被多个项目（比如一个开源的 Django 插件）使用的 myapp，你并不知道其他项目的 Celery 实例会叫什么名字，或者在哪里定义。如果强行导入 myproject.celery.app，这个应用在其他项目中将无法使用。

@shared_task 解决了这个问题。它创建的任务是一个“懒加载”的代理，它会在运行时自动绑定到当前项目配置的 Celery 实例上。

详细用法
使用 @shared_task 非常简单，只需从 celery 模块中导入它即可。

```Python

from celery import shared_task

@shared_task
def add(x, y):
    print(f'Adding {x} + {y}')
    return x + y
```

当然！@shared_task 的核心优势在于解耦，它允许你定义的任务不依赖任何具体的 Celery 应用（app）实例。这在 FastAPI 项目中尤其有用，可以让你将任务逻辑（tasks.py）与应用实例配置（celery_app.py）和 Web 服务（main.py）完全分开，避免循环导入问题。
下面是一个以 FastAPI 为例的详细教程。

核心理念：为什么在 FastAPI 中使用 shared_task？

想象一个场景：
1. 你在 main.py 中创建了 FastAPI app 和 Celery celery_app。
2. 你在 tasks.py 中定义了一个任务，这个任务需要从 main.py 导入某个工具函数或配置。
3. 同时，你的 main.py 中的 Celery celery_app 需要导入 tasks.py 来注册任务。
这就造成了循环导入（Circular Import），你的应用将无法启动。
@shared_task 解决了这个问题。你可以在 tasks.py 中定义任务，而无需从任何地方导入 Celery app 实例。然后，你创建一个单独的 celery_app.py 文件来实例化 Celery，并告诉它去哪里发现这些 shared_task。


Part 1: 项目结构

一个清晰的 FastAPI + Celery 项目结构如下：

```
fastapi_celery_project/
├── main.py             # 你的 FastAPI 应用
├── celery_app.py       # Celery 实例和配置
├── tasks/
│   ├── __init__.py
│   └── email_tasks.py  # 使用 @shared_task 定义任务
└── requirements.txt
```

Part 2: 依赖安装

requirements.txt:
```
fastapi
uvicorn[standard]
celery
redis
* celery[redis] 也可以，它会捆绑 redis 库。
```
Part 3: 配置 Celery 实例 (celery_app.py)

这是连接所有部分的关键文件。它创建 Celery 实例，并告诉 Celery 去哪里查找任务。
celery_app.py:
```Python



from celery import Celery

# 1. 定义 Broker 和 Backend 的 URL
# 你应该使用环境变量来存储这些敏感信息，这里为了演示而硬编码
BROKER_URL = "redis://localhost:6379/0"
RESULT_BACKEND = "redis://localhost:6379/1"

# 2. 创建 Celery 实例
#    'tasks' 是这个 Celery 实例的默认名称
celery = Celery(
    'tasks',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    
    # 3. 关键！指定 Celery 应该自动发现任务的模块
    #    这里我们指向 'tasks.email_tasks' 模块。
    #    这替代了 Django 的 `autodiscover_tasks()`。
    include=['tasks.email_tasks']
)

# 4. (可选) 更多 Celery 配置
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Los_Angeles', # 建议使用 UTC
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
```

Part 4: 使用 @shared_task 定义任务

现在，我们在 tasks/email_tasks.py 中定义任务，注意这里不需要导入 celery_app.py 中的 celery 实例。
tasks/email_tasks.py:
```Python



import time
from celery import shared_task

# @shared_task 装饰器让这个函数成为一个 Celery 任务
# 它不依赖于任何特定的 Celery app 实例
@shared_task
def send_welcome_email(email: str):
    """
    一个模拟发送欢迎邮件的耗时任务
    """
    print(f"Task started: Sending welcome email to {email}...")
    
    # 模拟一个 5 秒钟的 I/O 操作 (例如 API 调用或 SMTP 通信)
    time.sleep(5) 
    
    print(f"Task finished: Email sent to {email}")
    return f"Successfully sent welcome email to {email}"
```
Part 5: 在 FastAPI 中调用任务

最后，我们在 main.py 中创建 API 端点。当端点被调用时，它会将任务推送到 Celery 队列中，然后立即返回响应。
main.py:
```Python



from fastapi import FastAPI
from tasks.email_tasks import send_welcome_email
from celery.result import AsyncResult
from celery_app import celery as celery_app_instance # 导入用于查询结果的 app 实例

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI + Celery"}

@app.post("/register")
def register_user(email: str):
    """
    一个注册端点，它会异步触发一个欢迎邮件任务
    """
    # .delay() 是 .apply_async() 的快捷方式
    # 它将任务发送到 Celery 队列，并立即返回
    task = send_welcome_email.delay(email)
    
    # 立即返回响应，告诉客户端任务已加入队列
    return {
        "message": "User registration successful. Welcome email is being sent in the background.",
        "task_id": task.id  # 返回任务 ID，以便客户端稍后查询状态
    }

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """
    根据任务 ID 查询任务的状态和结果
    """
    # 使用从 celery_app.py 导入的实例来创建 AsyncResult
    task_result = AsyncResult(task_id, app=celery_app_instance)
    
    if task_result.ready():
        # 任务已完成
        if task_result.successful():
            return {
                "task_id": task_id,
                "status": task_result.status,
                "result": task_result.get() # 获取任务的返回值
            }
        else:
            # 任务失败
            return {
                "task_id": task_id,
                "status": task_result.status,
                "result": str(task_result.info) # 获取异常信息
            }
    else:
        # 任务仍在进行中
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": None
        }
```

Part 6: 如何运行

你需要启动三个独立的进程：
1. 消息代理 (Message Broker)：这里我们使用 Redis。
2. Celery Worker：执行任务的进程。
3. FastAPI 应用：接收 HTTP 请求的 Web 服务器。
1. 启动 Redis (使用 Docker)
```Bash



docker run -d -p 6379:6379 --name my-redis redis
```
2. 启动 Celery Worker
在你的项目根目录 (fastapi_celery_project/) 运行：
```Bash



# -A celery_app.celery 指向 '文件名.Celery实例变量名'
# worker 是命令
# --loglevel=info 是日志级别
celery -A celery_app.celery worker --loglevel=info
```
你会看到 Worker 启动，并成功发现了 tasks.email_tasks.send_welcome_email 任务。
3. 启动 FastAPI 服务器
在另一个终端中运行：
```Bash



uvicorn main:app --reload
```
Part 7: 测试

1. 调用任务：curl -X POST "http://127.0.0.1:8000/register?email=example@test.com"你会立即收到响应：{"message":"User registration successful. Welcome email is being sent in the background.","task_id":"..."}
2. 查看 Worker：在 Celery Worker 的终端中，你会看到任务在 5 秒后被执行：[... INFO/MainProcess] Task tasks.email_tasks.send_welcome_email[...] received
3. Task started: Sending welcome email to example@test.com...
4. Task finished: Email sent to example@test.com
5. [... INFO/MainProcess] Task tasks.email_tasks.send_welcome_email[...] succeeded in 5.01s: 'Successfully sent email...'
6. 
7. 查询结果 (使用你收到的 task_id)：curl http://127.0.0.1:8000/tasks/YOUR_TASK_ID_HERE
    * （5秒内）状态：{"task_id":"...","status":"PENDING","result":null}
    * （5秒后）状态：{"task_id":"...","status":"SUCCESS","result":"Successfully sent welcome email to example@test.com"}


shared_task 常用参数详解

@shared_task 接受所有 @app.task 的参数。

1. bind=True (绑定任务实例)

最常用的参数之一。它告诉 Celery 将任务实例（self）作为第一个参数传递给你的函数。这允许你访问任务的上下文（如请求ID）并执行重试。
```Python



from celery import shared_task
import requests

@shared_task(bind=True, max_retries=3)
def fetch_external_api(self, url):
    """
    一个带自动重试的任务
    self 是任务实例，不是类的 self
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # 4xx 或 5xx 会抛出异常
        return response.json()
    except requests.RequestException as exc:
        print(f"API call failed for {url}. Retrying... (Attempt {self.request.retries + 1})")
        # self.retry() 会抛出一个异常，Celery 会捕获它并稍后重试
        # countdown=15 表示 15 秒后重试
        raise self.retry(exc=exc, countdown=15)
```
2. autoretry_for (自动重试)

bind=True 和 self.retry() 的简化版。你只需指定一个异常元组，Celery 会在捕获到这些异常时自动重试。
```Python



@shared_task(
    autoretry_for=(requests.RequestException, KeyError), 
    retry_kwargs={'max_retries': 5}, 
    retry_backoff=True  # 启用指数退避 (如 2s, 4s, 8s...)
)
def fetch_api_simple(url):
    # 不需要 try/except，也不需要 self
    # 如果 requests.get 抛出 RequestException，Celery 会自动重试
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    # 如果 response.json() 中缺少某个键，抛出 KeyError，也会重试
    return response.json()['some_key'] 
```
3. ignore_result=True (忽略结果)

如果你的任务是“即发即忘”型（fire-and-forget），你根本不关心它的返回值（比如一个简单的日志记录任务），将此设为 True。Celery 将不会在结果后端（Redis）中存储任何结果，从而节省内存和提高性能。
```Python



@shared_task(ignore_result=True)
def log_user_action(user_id, action):
    # 这个任务只是写入日志，不需要返回任何值
    print(f"[LOG] User {user_id} performed action: {action}")
```
4. rate_limit (速率限制)

限制任务的执行频率，例如 "10/m" (每分钟 10 次) 或 "1/s" (每秒 1 次)。这对于防止对外部 API 造成过大压力非常有用。
```Python



@shared_task(rate_limit="5/m")
def call_rate_limited_api():
    # 这个任务在所有 worker 上加起来，每分钟最多执行 5 次
    ...
```
总结：@shared_task vs @app.task

| 特性 | `@shared_task` (来自 `from celery import shared_task`) | `@app.task` (来自 `from celery_app import celery`) |
| :--- | :--- | :--- |
| **依赖性** | **不依赖**任何特定的 Celery app 实例。 | **强依赖**于你导入的 `celery` 实例。 |
| **适用场景** | **推荐在所有项目中（包括 FastAPI）使用**。<br> - 在 `tasks/` 模块中定义任务。<br> - 编写可重用库、插件。 | - 仅在定义 Celery app 的**主文件**（`celery_app.py`）中使用。<br> - 非常简单的、所有代码都在一个文件中的项目。 |
| **主要优势** | **避免循环导入**，实现代码解耦和模块化。 | 简单直接，但容易导致项目结构混乱。 |

#### celery调用任务的方式
在 Celery 中，调用任务（Task）的方式主要有 **三种核心方法**，此外还有一些辅助或高级用法。下面为你**完整列出所有调用方式**，并详细说明它们的作用、适用场景和区别。

---

 ✅ 一、核心调用方法（最常用）

 1. `.delay(*args, **kwargs)`
- **作用**：最简单的异步调用方式，直接将任务发送到消息队列（如 Redis）。
- **特点**：
  - 语法简洁
  - 只支持传递任务参数（`args` 和 `kwargs`）
  - **不支持**设置执行时间、队列、重试策略等高级选项
- **底层实现**：其实是 `apply_async` 的快捷封装
- **示例**：
  ```python
  result = add.delay(4, 5)
  result = translate_file.delay(file_path="/tmp/a.pdf", lang="zh")
  ```

> ✅ **适用场景**：快速原型、简单任务、参数少、无需控制执行策略。

---

 2. `.apply_async(args=[], kwargs={}, **options)`
- **作用**：功能最全的异步调用方式，支持所有 Celery 任务调度选项。
- **可选参数（`**options`）**：
  | 参数 | 说明 |
  |------|------|
  | `countdown` | 多少秒后执行（如 `countdown=10` 表示 10 秒后） |
  | `eta` | 指定具体执行时间（`datetime` 对象） |
  | `expires` | 任务过期时间（秒数或 `datetime`），过期后不再执行 |
  | `queue` | 发送到指定队列（需提前配置） |
  | `routing_key` | 自定义路由键（配合 RabbitMQ 使用） |
  | `serializer` | 序列化格式（如 `'json'`, `'pickle'`） |
  | `retry` | 是否自动重试（布尔值） |
  | `retry_policy` | 重试策略字典（如 `{'max_retries': 3, 'interval_start': 0}`） |
  | `time_limit` | 任务硬性超时时间（秒） |
  | `soft_time_limit` | 软超时（抛异常但可捕获） |

- **示例**：
  ```python
  from datetime import datetime, timedelta

   5秒后执行，60秒后过期，发到 high_priority 队列
  result = translate_file.apply_async(
      kwargs={'file_path': '/tmp/doc.pdf', 'lang': 'en'},
      countdown=5,
      expires=60,
      queue='high_priority'
  )

   指定时间执行
  eta = datetime.utcnow() + timedelta(hours=1)
  result = backup_db.apply_async(eta=eta)
  ```

> ✅ **适用场景**：生产环境、需要精确控制任务行为（延迟、队列、过期、重试等）。

---

 3. `.apply(args=[], kwargs={}, **options)`
- **作用**：**同步执行任务**（在当前进程中立即运行，不经过消息队列！）
- **特点**：
  - **不会发送到 Broker（如 Redis）**
  - **不会被 Worker 执行**
  - 直接调用任务函数，返回结果（类似普通函数调用）
  - 主要用于**测试或调试**
- **示例**：
  ```python
  result = add.apply(args=[2, 3])   立即执行，返回 5
  print(result.get())   5
  ```

> ⚠️ **警告**：不要在生产 Web 请求中使用 `.apply()`，因为它会阻塞当前进程，失去异步意义！

> ✅ **适用场景**：单元测试、本地调试、确保任务逻辑正确。

---

 ✅ 二、通过任务名动态调用（解耦用法）

 4. `celery_app.send_task(task_name, args=[], kwargs={}, **options)`
- **作用**：**不导入任务函数**，仅通过任务名字符串调用任务。
- **优点**：
  - 完全解耦：调用方不需要知道任务定义在哪个模块
  - 适合微服务、插件系统、动态调度
- **前提**：任务必须已注册（Worker 能识别该名字）
- **示例**：
  ```python
  from myproject.celery import app   获取 Celery 实例

  result = app.send_task(
      "doc2x.translate_file",
      kwargs={
          "file_path": "/tmp/x.pdf",
          "target_lang": "fr"
      },
      queue="translation"
  )
  ```

> ✅ **适用场景**：
> - 调度系统不知道具体任务实现
> - 多团队协作，任务名作为接口契约
> - 动态决定调用哪个任务（如根据用户输入）

---

 ✅ 三、组调用与工作流（高级用法）

这些不是“单个任务调用”，而是**组合多个任务**的方式：

 5. `group()` — 并行执行多个任务
```python
from celery import group

jobs = group(add.s(1, 1), add.s(2, 2), add.s(3, 3))
result = jobs.apply_async()
print(result.get())   [2, 4, 6]
```

 6. `chain()` — 串行执行（前一个输出作为后一个输入）
```python
from celery import chain

result = chain(add.s(2, 2), mul.s(4), div.s(2)).apply_async()
 等价于: div(mul(add(2,2), 4), 2) → div(mul(4,4),2) → 16/2 = 8
```

 7. `chord()` — 先并行执行一组任务，再回调一个任务
```python
from celery import chord

callback = finalize.s()
header = [add.s(i, i) for i in range(4)]   [0+0, 1+1, 2+2, 3+3]
result = chord(header)(callback)   callback 接收 [0,2,4,6] 作为参数
```

> ✅ 这些用于复杂任务编排，属于 **Celery Canvas** 功能。

---

 ✅ 四、签名（Signatures）— 任务的“可调用对象”

 8. `task.s(*args, **kwargs)` — 创建任务签名
- **作用**：将任务和参数打包成一个“可传递的对象”，用于组合（如 group/chain）
- **不会立即执行**
- **示例**：
  ```python
  sig = add.s(2, 2)         签名
  result = sig.delay()      现在才异步执行
  ```

> 常用于工作流构建。

---

 ✅ 总结：所有调用方式一览表

| 方法 | 是否异步 | 是否走 Broker | 是否支持高级选项 | 典型用途 |
|------|--------|--------------|----------------|--------|
| `.delay()` | ✅ 是 | ✅ 是 | ❌ 否 | 快速调用 |
| `.apply_async()` | ✅ 是 | ✅ 是 | ✅ 是 | 生产环境标准调用 |
| `.apply()` | ❌ 否 | ❌ 否 | ⚠️ 部分 | 测试/调试 |
| `send_task()` | ✅ 是 | ✅ 是 | ✅ 是 | 动态/解耦调用 |
| `group/chain/chord` | ✅ 是 | ✅ 是 | ✅ 是 | 复杂任务编排 |
| `.s()`（签名） | ❌（需配合 delay/apply_async） | 取决于后续调用 | ✅ | 构建工作流 |

---

 🔒 重要提醒

- 所有 **异步调用**（`.delay`, `.apply_async`, `send_task`）都**依赖 Broker（如 Redis）** 和 **Worker 进程**。
- 如果没启动 Worker，任务会堆积在队列中，**永远不会执行**。
- 不要在 Web 请求中使用 `.get()` 阻塞等待结果（除非你明确知道后果）。




#### 如何调整同时执行的任务数

这是一个非常好的问题。在生产环境中，根据负载情况动态调整 Worker 的并发数（即同时执行的任务数）是运维和资源管理的关键部分。

Celery 提供了两种主要的方式来实现这一点：

1.  **手动远程控制 (Manual Remote Control)：** 你可以向正在运行的 Worker 发送命令，要求它增加或减少工作进程数。
2.  **自动伸缩 (Autoscaling)：** 你可以设置一个最小和最大进程数，Celery Worker 会根据队列中的任务压力自动调整。

下面我们详细讲解这两种方法。

-----

方法一：使用 `celery control` 手动调整（即时生效）

这是最直接的“我想动态调整”的答案。你可以使用 Celery 的远程控制命令 `pool_grow` (增加) 和 `pool_shrink` (减少) 来实时调整。

这要求你的 Worker 进程正在运行。

**适用场景：**

  * 你预知到一波大流量即将到来（例如，市场活动开始），需要立即增加处理能力。
  * 你发现服务器负载过高，需要立即减少并发数来“降温”。

**前提条件：**

  * Worker 必须使用支持动态伸缩的执行池 (Pool)。默认的 `prefork`（多进程）池是支持的。`gevent` 和 `eventlet` 也支持。
  * （如果你在 Windows 上运行，默认池可能不支持，你需要显式使用 `-P gevent` 或 `-P eventlet`）。

1\. 增加并发数 (`pool_grow`)

这个命令告诉 Worker 增加 N 个工作进程。

```bash
# 语法: celery -A <app_name> control pool_grow <N>
# 假设你的应用在 tasks.py 中
# 增加 3 个工作进程
celery -A tasks control pool_grow 3
```

Worker 会立即响应（在日志中可以看到），并启动新的子进程来接收任务。

2\. 减少并发数 (`pool_shrink`)

这个命令告诉 Worker 减少 N 个工作进程。Celery 会*优雅地*关闭这些进程，意味着它们会先完成手中正在执行的任务，然后再退出。

```bash
# 语法: celery -A <app_name> control pool_shrink <N>
# 减少 2 个工作进程
celery -A tasks control pool_shrink 2
```

3\. 针对特定的 Worker

在生产环境中，你可能运行了多个 Worker。你可以通过 `-d` (destination) 参数指定要控制的 Worker：

```bash
# 1. 首先，查看所有正在运行的 Worker
celery -A tasks status

# 2. 假设你看到一个名为 worker1@my-server 的 Worker
# 只给它增加并发
celery -A tasks control pool_grow 2 -d worker1@my-server
```

-----

 方法二：使用 `--autoscale` 自动伸缩（推荐）

这是一种更“自动化”的动态调整。你不需要手动干预，Celery Worker 会自己监控任务队列的压力，并在你设定的范围内自动增加或减少工作进程。

**适用场景：**

  * 任务负载波动很大且难以预测（例如，白天任务多，晚上任务少）。
  * 你希望“设置好就不用管了”，让系统自动优化资源。

1\. 启动 Worker 时开启 Autoscaling

你需要在启动 Worker 时使用 `--autoscale` 选项，并提供**最大并发数**和**最小并发数**。

```bash
# 语法: celery -A <app_name> worker --autoscale=<max_concurrency>,<min_concurrency>
#
# 启动一个 Worker，它最少保留 2 个工作进程，
# 但在负载高时，最多可以扩展到 10 个进程
celery -A tasks worker --autoscale=10,2 --loglevel=info
```

  * **工作原理：** Worker 启动时会以 `min_concurrency` (2个) 进程开始。当它发现队列中等待的任务增多时，它会逐渐增加进程数（`pool_grow`），直到达到 `max_concurrency` (10个)。
  * 当队列变空，任务处理完毕后，它会逐渐减少进程数（`pool_shrink`），直到回到 `min_concurrency` (2个)，以节省系统资源。

2\. 动态调整 Autoscaler 的边界

最强大的功能是：**你可以将方法一和方法二结合起来**。

你可以**在运行时**动态调整那个开启了 `--autoscale` 的 Worker 的**最大/最小**边界！

这是通过 `autoscale` 控制命令完成的：

```bash
# 假设 Worker 以 --autoscale=10,2 启动
# 现在是高峰期，我们希望它最多能扩展到 20 个进程，最少保持 5 个
celery -A tasks control autoscale 20,5
```

Worker 收到命令后，会立即更新它的自动伸缩策略。

-----

 方法三：静态调整（需要重启）

这不算是“动态”调整，但作为对比也提一下。这就是你在启动时使用 `-c` (concurrency) 参数来**固定**并发数。

```bash
# 启动一个固定 8 个工作进程的 Worker
celery -A tasks worker -c 8
```

如果你用这种方式启动，你**仍然**可以使用 `pool_grow` 和 `pool_shrink` 来临时调整它。但是，一旦这个 Worker 重启，它又会回到固定的 `-c 8`。

-----

 总结与建议

| 方法 | 命令 | 效果 | 最佳场景 |
| :--- | :--- | :--- | :--- |
| **手动调整** | `celery control pool_grow <N>` | 立即增加 N 个进程 | 应对已知的突发流量 |
| | `celery control pool_shrink <N>` | 立即（优雅地）减少 N 个进程 | 立即降低服务器负载 |
| **自动伸缩** | `celery worker --autoscale=<max>,<min>` | Worker 根据负载自动在 max 和 min 之间调整 | 生产环境中最推荐的常用方式 |
| **动态调参** | `celery control autoscale <new_max>,<new_min>`| 实时修改 `--autoscale` 的边界 | 运维时根据大趋势调整策略 |
| **静态设置** | `celery worker -c <N>` | 启动时固定 N 个进程 | 开发或负载恒定的简单场景 |

**给你的建议：**

在生产环境中，**始终使用 `--autoscale` 启动你的 Worker**。

`celery -A tasks worker --autoscale=16,4`

然后，当你需要根据全局策略（例如，知道接下来一周是旺季）调整时，使用 `celery control autoscale` 来调整边界。

`celery -A tasks control autoscale 32,8`

这样你就能同时获得自动化的便利性和手动调控的灵活性。