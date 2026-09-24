---
title: FastAPI 后端架构设计
description: "面向中大型项目的 FastAPI 后端架构设计示例，涵盖分层组织、模块拆分与可维护性设计。"
date: 2025-09-16T14:48:04+08:00
image: images/index/index.png
categories:
    - Design
tags:
    - 软件架构设计
---
# FastAPI 项目结构化教程

这是一个经过精心设计的、适用于中大型项目的 FastAPI 后端目录结构。它具有良好的模块化、可扩展性和可维护性。

## 目录结构总览

```

.
├── app/                      \# 主要的应用代码目录
│   ├── **init**.py           \# 将 app 目录标记为 Python 包
│   ├── main.py               \# FastAPI 应用的入口文件
│   │
│   ├── api/                  \# API 路由（endpoints）层
│   │   ├── **init**.py
│   │   └── v1/               \# API 版本 v1
│   │       ├── **init**.py
│   │       ├── api.py        \# 聚合 v1 版本的所有路由
│   │       └── endpoints/    \# 存放各个模块的路由文件
│   │           ├── **init**.py
│   │           ├── users.py
│   │           └── items.py
│   │
│   ├── core/                 \# 核心逻辑与配置
│   │   ├── **init**.py
│   │   ├── config.py         \# 应用配置（环境变量等）
│   │   ├── security.py       \# 安全相关（密码哈希、JWT令牌等）
│   │   └── logger.py         \# 日志配置与工具
│   │
│   │── services/              # 新增: 业务逻辑层 (工作流)
│   │   ├── __init__.py
│   │   └── chat_agent/        # 例如 （LangGraph Agent）
│   │       ├── __init__.py
│   │       ├── graph.py       # 编译后的 Agent (Workflow)
│   │       ├── state.py       # AgentState
│   │       ├── nodes.py       # 节点函数
│   │       └── tools.py       # 工具 (e.g., RAG, DB lookup)
│   │
│   ├── crud/                 \# CRUD 数据库操作层
│   │   ├── **init**.py
│   │   ├── base.py           \# 可复用的 CRUD 基类
│   │   ├── crud\_user.py      \# 针对 User 模型的 CRUD 操作
│   │   └── crud\_item.py      \# 针对 Item 模型的 CRUD 操作
│   │
│   ├── db/                   \# 数据库相关
│   │   ├── **init**.py
│   │   ├── base.py           \# SQLAlchemy 的声明式基类 (DeclarativeBase)
│   │   ├── session.py        \# 数据库会话管理
│   │   └── init\_db.py        \# (可选) 初始化数据库脚本
│   │
│   ├── models/               \# SQLAlchemy ORM 模型
│   │   ├── **init**.py
│   │   ├── user.py
│   │   └── item.py
│   │
│   ├── schemas/              \# Pydantic 数据模型（用于数据校验与序列化）
│   │   ├── **init**.py
│   │   ├── user.py
│   │   ├── item.py
│   │   └── token.py
│   │
│   └── dependencies/         \# FastAPI 依赖项注入
│       ├── **init**.py
│       └── common.py         \# 通用依赖项（如获取DB会话、获取当前用户）
│
├── tests/                    \# 测试代码目录
│   ├── **init**.py
│   ├── conftest.py           \# Pytest 的 fixtures 和配置
│   └── api/
│       └── v1/
│           ├── test\_users.py
│
├── logs/                     \# 日志文件目录 (运行时自动创建)
│   ├── app.log               \# 应用主日志文件
│   ├── app.log.1             \# 轮转的历史日志文件
│   └── app.log.2             \# 轮转的历史日志文件
│
├── .env                      \# 环境变量文件 (不应提交到 git)
├── .gitignore                \# Git 忽略文件配置
├── Dockerfile                \# Docker 配置文件
├── requirements.txt          \# Python 依赖包列表
└── README.md                 \# 项目说明文档

````

---

## 详细说明

### 根目录文件

* **`.env`**: 存储敏感信息和环境变量，例如数据库连接字符串、JWT 密钥等。
* **`.gitignore`**: 定义了哪些文件或目录不应被 Git 跟踪。
* **`Dockerfile`**: 用于构建应用的 Docker 镜像，方便容器化部署。
* **`requirements.txt`**: 列出项目的所有 Python 依赖库，使用 `pip install -r requirements.txt` 进行安装。
* **`README.md`**: 项目的说明文件，介绍如何设置、运行和使用该项目。

### `app/` 目录：核心应用

这是你所有业务逻辑代码的家。

* **`main.py`**:
    * **作用**: FastAPI 应用的入口点。
    * **内容**: 创建 FastAPI 实例，挂载中间件 (Middleware)，包含来自 `app/api/` 的主路由，并可以定义全局的异常处理程序。

* **`api/` 目录**: API 层
    * **作用**: 负责处理 HTTP 请求，定义 API 的路径、参数和响应。这一层应该保持精简，只做请求的接收和响应的返回，具体的业务逻辑和数据库操作应该调用其他模块来完成。
    * **`v1/`**: 按版本组织 API 是一个非常好的实践，方便未来升级。
    * **`v1/endpoints/`**: 每个 `*.py` 文件代表一组相关的 API 路由（例如 `users.py` 处理所有 `/users` 相关的请求）。
    * **`v1/api.py`**: 这个文件导入 `endpoints` 中的所有路由，并将它们组合成一个单一的 `APIRouter`，然后这个 `APIRouter` 会被 `main.py` 包含进去。这让 API 版本的管理变得非常清晰。

* **`core/` 目录**: 核心配置
    * **作用**: 存放应用的全局配置和核心功能。
    * **`config.py`**: 使用 Pydantic 的 `BaseSettings` 读取 `.env` 文件和环境变量，为整个应用提供一个统一的配置对象。
    * **`security.py`**: 处理所有与安全相关的功能，如密码的哈希和验证、JWT 令牌的创建和解码。
    * **`logger.py`**: 日志系统的配置和工具函数，提供统一的日志记录接口，支持不同级别的日志输出、文件轮转和格式化配置。

* **`db/` 目录**: 数据库连接与会话
    * **作用**: 管理数据库的连接和会话。
    * **`session.py`**: 定义 SQLAlchemy 的 `engine` 和 `SessionLocal`（会话工厂）。
    * **`base.py`**: 包含 `declarative_base()` 的实例，我们所有的 ORM 模型都将继承自这个基类。这使得 Alembic（数据库迁移工具）能够发现我们的模型。

* **`models/` 目录**: 数据库模型层
    * **作用**: 定义了与数据库表对应的 SQLAlchemy ORM 模型。每个文件对应一个模型（或一组紧密相关的模型）。这些模型描述了数据的结构。

* **`schemas/` 目录**: 数据校验层
    * **作用**: 定义 Pydantic 模型，FastAPI 用它来做数据验证、序列化和文档生成。
    * **职责**:
        1.  **请求体验证**: 验证传入的请求体（例如，创建一个新用户时，确保 `email` 字段是合法的）。
        2.  **响应体塑形**: 决定从 API 返回哪些字段（例如，从数据库查询出的用户对象可能包含哈希后的密码，但我们绝不应该在 API 响应中返回它）。
    * 通常会为每个模型定义多个 Schema，例如 `UserCreate`, `UserUpdate`, `UserInDB`, `User`。

* **`crud/` 目录**: 数据操作层
    * **作用**: "Create, Read, Update, Delete" 的缩写。这一层封装了所有与数据库的直接交互。
    * **职责**: 将数据库操作（如 `db.add(obj)`) 从 API 路由中分离出来。API 路由不应该直接编写 SQLAlchemy 查询语句，而应该调用这里的函数，例如 `crud.user.create_user(...)`。这使得代码更易于测试和重用。
    * **`base.py`**: 可以定义一个通用的 `CRUDBase` 类，包含 `get`, `get_multi`, `create`, `update`, `delete` 等通用方法，然后具体的 `crud_user.py` 只需继承它并添加特定逻辑即可。

* **`dependencies/` 目录**: 依赖注入
    * **作用**: 存放 FastAPI 的依赖项。依赖注入是 FastAPI 的一个核心特性。
    * **职责**: 创建可重用的依赖项，例如 `get_db` 用于为每个请求提供一个数据库会话，并在请求结束后关闭它；`get_current_user` 用于验证 JWT 令牌并返回当前登录的用户。这些依赖项可以在 API 路径操作函数中直接使用。

### `tests/` 目录：测试

* **作用**: 存放所有的测试代码。保持测试代码与应用代码分离。
* **`conftest.py`**: Pytest 的配置文件，用于定义测试范围内的 fixtures（例如，创建一个临时的测试数据库、一个用于发送请求的 `TestClient`）。
* **目录结构**: 测试目录的结构最好能镜像 `app/` 目录的结构，这样可以很容易地找到对应模块的测试。

### `logs/` 目录：日志文件

* **作用**: 存储应用运行时产生的日志文件。
* **自动创建**: 该目录由 `app/core/logger.py` 在首次运行时自动创建，无需手动创建。
* **文件轮转**: 采用日志轮转机制，当主日志文件达到设定大小（如10MB）时，会自动轮转为历史文件，保持最近的5个日志文件。
* **建议**: 在 `.gitignore` 中添加 `logs/` 目录，避免将日志文件提交到版本控制系统。

---

## 示例代码

下面是一些关键文件的示例代码，以帮助你更好地理解它们的具体实现。

#### `app/main.py`
```python
from fastapi import FastAPI
from app.api.v1 import api
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 包含 v1 版本的 API 路由
app.include_router(api.api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to this fantastic app!"}

````

#### `app/api/v1/api.py`

```python
from fastapi import APIRouter
from app.api.v1.endpoints import users, items

api_router = APIRouter()

# 包含 users 和 items 的路由
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
```

#### `app/api/v1/endpoints/users.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.dependencies import common

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(common.get_db)
):
    db_user = crud.user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(common.get_db)
):
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users
```

#### `app/core/config.py`

```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    #SQLALCHEMY_DATABASE_URI: str = "sqlite:///./test.db"
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db")

    # JWT 配置
    SECRET_KEY: str = "a_very_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

#### `app/schemas/user.py`

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

# 基础模型
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

# 创建时需要的字段 (继承自 Base，并添加 password)
class UserCreate(UserBase):
    password: str

# 更新时需要的字段 (所有字段都可选)
class UserUpdate(UserBase):
    password: Optional[str] = None

# 存储在数据库中的模型 (包含 hashed_password)
class UserInDBBase(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True # Pydantic v2 orm_mode for Pydantic v1

# 从 API 返回给用户的模型 (不包含密码)
class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
```

#### `app/crud/crud_user.py`

```python
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

#### `app/dependencies/common.py`

```python
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

# 依赖项：为每个请求创建一个独立的数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### `app/core/logger.py`

```python
import logging
import logging.handlers
import os
from pathlib import Path
from app.core.config import settings

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    设置应用日志记录器
    
    Args:
        name: 日志记录器名称，默认为调用模块的名称
    
    Returns:
        配置好的日志记录器实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 创建日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（带轮转）
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# 创建默认的应用日志记录器
app_logger = setup_logger("fastapi_app")

def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器实例
    
    Args:
        name: 日志记录器名称，如果为None则使用默认应用日志记录器
    
    Returns:
        日志记录器实例
    """
    if name is None:
        return app_logger
    return setup_logger(name)
```

这个结构为你提供了一个坚实的起点。你可以根据项目的具体需求，在这个基础上进行调整和扩展。
