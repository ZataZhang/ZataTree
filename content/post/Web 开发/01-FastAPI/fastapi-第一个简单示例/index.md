---
title: fastapi使用教程
description: ""
date: 2025-04-01T14:43:52+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - FastAPI
---

代码地址

https://github.com/zata-zhangtao/Zata-code/tree/main/07-html%2Bfastapi/fastapi/tutorial/phase1-fastapi%E7%AE%80%E5%8D%95%E7%9A%84%E5%BC%80%E5%A7%8B

---


### **教程大纲**
1. **环境准备**
2. **基础示例：Hello World**
3. **路径参数和查询参数**
4. **请求体和数据验证**
5. **异步编程**
6. **依赖注入**
7. **中间件和错误处理**
8. **部署 FastAPI 应用**

---

### **1. 环境准备**
#### 安装必要的工具  (我在教程中安装的python=3.11)
确保您已安装 Python 3.7 或更高版本，然后使用以下命令安装 FastAPI 和 Uvicorn（一个 ASGI 服务器，用于运行 FastAPI）：
```bash
uv add fastapi  "uvicorn[standard]"
```

#### 可选：安装其他依赖
- `pydantic`：用于数据验证（FastAPI 已包含）。
- `httpx`：用于测试 API（可选）。

---

### **2. 基础示例：Hello World**
让我们从一个简单的 FastAPI 应用开始。

#### 代码示例
创建一个文件 `main.py`：
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# 然后你就可以使用 uvicorn 01-simple_start:app  --reload  去开启服务了

# 当然你也可以直接运行，使用下面的方式去开启服务

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


```

#### 运行应用
在终端中运行以下命令：
```bash
uvicorn main:app --reload
```
- `main` 是文件名（不带 `.py`）。
- `app` 是 FastAPI 实例的名称。
- `--reload` 会在代码更改时自动重启服务器，适合开发环境。

#### 测试
打开浏览器访问 `http://127.0.0.1:8000`，您将看到：
```json
{"message": "Hello World"}
```

![hello](images/index/index-1.png)

FastAPI 还提供交互式文档，访问 `http://127.0.0.1:8000/docs` 查看 Swagger UI。

    ![Swagger UI](images/index/index-2.png)
---

### **3. 路径参数和查询参数**
#### 路径参数
路径参数通过 URL 传递，例如 `/items/1`。
```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```
访问 `http://127.0.0.1:8000/items/42`，返回：
```json
{"item_id": 42}
```

![a](images/index/index-3.png)


#### 查询参数
查询参数通过 `?key=value` 形式传递。
```python
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```
访问 `http://127.0.0.1:8000/items/?skip=5&limit=20`，返回：
```json
{"skip": 5, "limit": 20}
```
![查询](images/index/index-4.png)

---

### **4. 请求体和数据验证**
FastAPI 使用 Pydantic 模型来处理请求体和数据验证。

#### 定义 Pydantic 模型
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None  # 可选字段，默认 None
```

#### 处理 POST 请求
```python
@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "price": item.price, "is_offer": item.is_offer}
```

#### 测试
使用 Swagger UI (`/docs`) 或以下 `curl` 命令：
```bash
curl -X POST "http://localhost:8000/items/" -H "Content-Type: application/json" -d "{\"name\": \"Book\", \"price\": 9.99, \"is_offer\": true}"
```
返回：
```json
{"name": "Book", "price": 9.99, "is_offer": true}
```

![测试curl命令](images/index/index-5.png)

如果数据格式错误（例如 `price` 传入字符串），FastAPI 会自动返回验证错误。

![如果传入字符串会自动校验](images/index/index-6.png)


---

### **5. 异步编程**
FastAPI 支持异步函数，使用 `async def`，适合 I/O 密集型操作（如数据库查询）。

#### 异步示例
```python
import asyncio

@app.get("/async/")
async def read_async():
    await asyncio.sleep(1)  # 模拟异步操作
    return {"message": "This is async"}
```

访问 `http://127.0.0.1:8000/async/`，1 秒后返回结果。

    ![异步编程](images/index/index-7.png)

---

### **6. 依赖注入**
依赖注入允许您在多个路由中复用代码，例如身份验证或数据库连接。

#### 定义依赖
```python
from fastapi import Depends

async def common_parameters(q: str | None = None, skip: int = 0):
    return {"q": q, "skip": skip}

@app.get("/depends/")
async def read_depends(commons: dict = Depends(common_parameters)):
    return commons
```

访问 `http://127.0.0.1:8000/depends/?q=test&skip=10`，返回：
```json
{"q": "test", "skip": 10}
```

我感觉注入依赖是一个比较难理解的内容，可以再看下面的内容增强理解


---

### **7. 中间件和错误处理**
#### 添加中间件
中间件用于处理请求和响应的全局逻辑，例如日志记录。
```python
@app.middleware("http")
async def add_custom_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Custom"] = "Example"
    return response
```

#### 自定义异常处理
```python
from fastapi import HTTPException

@app.get("/error/")
async def read_error():
    raise HTTPException(status_code=404, detail="Item not found")
```
访问 `http://127.0.0.1:8000/error/`，返回：
```json
{"detail": "Item not found"}
```

---

### **8. 部署 FastAPI 应用**
#### 使用 Uvicorn 生产环境
去掉 `--reload`，指定主机和端口：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 使用 Gunicorn + Uvicorn
安装 Gunicorn：
```bash
pip install gunicorn
```
运行：
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
- `-w 4` 表示 4 个工作进程。

#### Docker 部署
创建一个 `Dockerfile`：
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install fastapi uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
构建并运行：
```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

---

### **9. HTTPS/SSL 配置**
在生产环境中，使用 HTTPS 是保护数据传输安全的重要措施。FastAPI 可以通过 Uvicorn 轻松配置 SSL 证书。

#### SSL 证书准备
首先，您需要准备 SSL 证书文件：
- **证书文件** (`.pem` 或 `.crt`)：包含公钥和证书信息
- **私钥文件** (`.key`)：用于加密通信

#### 配置 HTTPS 的 FastAPI 应用
```python
import os
from pathlib import Path
from fastapi import FastAPI

app = FastAPI(title="Simple FastAPI App with SSL", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World", "ssl_enabled": True}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "secure": True}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/ssl-info")
async def ssl_info():
    cert_path = Path("resources/SSLcertificate/test.aizata.com.pem")
    key_path = Path("resources/SSLcertificate/test.aizata.com.key")
    
    return {
        "certificate_exists": cert_path.exists(),
        "private_key_exists": key_path.exists(),
        "certificate_path": str(cert_path),
        "key_path": str(key_path)
    }

if __name__ == "__main__":
    import uvicorn
    port = 8443
    
    # SSL certificate paths
    ssl_cert_path = "resources/SSLcertificate/test.aizata.com.pem"
    ssl_key_path = "resources/SSLcertificate/test.aizata.com.key"
    
    # Check if SSL files exist
    if os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path):
        print(f"Starting server with SSL/HTTPS on port {port}...")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            ssl_certfile=ssl_cert_path,
            ssl_keyfile=ssl_key_path
        )
    else:
        print(f"SSL certificates not found, starting HTTP server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
```

#### 命令行启动 HTTPS 服务
您也可以直接通过命令行启动 HTTPS 服务：
```bash
uvicorn main:app --host 0.0.0.0 --port 8443 --ssl-certfile resources/SSLcertificate/test.aizata.com.pem --ssl-keyfile resources/SSLcertificate/test.aizata.com.key
```

#### 测试 HTTPS 连接
启动服务后，访问 `https://localhost:8443` 或 `https://your-domain.com:8443`：
- 浏览器会显示安全连接标识
- API 文档地址：`https://localhost:8443/docs`
- 健康检查：`https://localhost:8443/health`
- SSL 信息：`https://localhost:8443/ssl-info`

#### 自签名证书（开发环境）
对于开发环境，您可以生成自签名证书：
```bash
# 生成私钥
openssl genrsa -out private.key 2048

# 生成自签名证书
openssl req -new -x509 -key private.key -out certificate.pem -days 365 -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
```

#### 生产环境建议
1. **使用受信任的 CA 证书**：从 Let's Encrypt 或其他 CA 获取免费证书
2. **证书自动续期**：设置自动续期脚本
3. **反向代理**：使用 Nginx 或 Apache 作为反向代理处理 SSL
4. **安全头部**：添加安全相关的 HTTP 头部

#### 使用 Nginx 反向代理（推荐）
在生产环境中，通常使用 Nginx 处理 SSL 终止：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.pem;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

这样，FastAPI 应用运行在 HTTP 端口 8000，Nginx 处理 HTTPS 并代理请求到 FastAPI。