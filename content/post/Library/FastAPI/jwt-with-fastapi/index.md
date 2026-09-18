---
title: jwt-with-fastapi
description: ""
date: 2025-09-12T16:48:40+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - FastAPI
---



# JWT (JSON Web Token) 深入解析与实战教程

## 目录
1.  [JWT 是什么？](#1-jwt-是什么)
    * [JWT 的结构](#jwt-的结构)
        * Header (头部)
        * Payload (负载)
        * Signature (签名)
    * [JWT 的工作流程](#jwt-的工作流程)
2.  [基础用法：JWT 的生成与验证](#2-基础用法jwt-的生成与验证)
    * [Node.js 示例 (jsonwebtoken)](#nodejs-示例-jsonwebtoken)
    * [Python 示例 (PyJWT)](#python-示例-pyjwt)
3.  [FastAPI 实战：构建 JWT 认证系统](#3-fastapi-实战构建-jwt-认证系统)
    * [第一步：单用户的 FastAPI 认证](#第一步单用户的-fastapi-认证)
    * [第二步：实现多用户注册与数据库认证](#第二步实现多用户注册与数据库认证)
4.  [安全性最佳实践](#4-安全性最佳实践)

---

## 1. JWT 是什么？

JSON Web Token (JWT)，通常读作 /dʒɒt/，是一种开放标准（RFC 7519），它定义了一种紧凑且自包含的方式，用于在各方之间安全地传输信息。这些信息可以被验证和信任，因为它是经过数字签名的。

JWT 通常被用于**身份验证**和**授权**。在一个典型的场景中，当用户使用其凭据成功登录后，认证服务器将返回一个 JWT。客户端（例如，单页应用或移动应用）会将此令牌存储起来，并在向服务器发送的后续请求中附上此令牌。服务器随后会验证此令牌的有效性，并根据其中包含的信息来授权用户的请求。

由于 JWT 的自包含性，它使得认证过程变得**无状态（Stateless）**。这意味着服务器端不需要在会v会话中存储用户信息，极大地简化了应用程序的扩展。

### JWT 的结构

一个 JWT 由三部分组成，以点（`.`）分隔，它们分别是：

1.  **Header（头部）**
2.  **Payload（负载）**
3.  **Signature（签名）**

因此，一个 JWT 通常看起来像这样：`xxxxx.yyyyy.zzzzz`

#### Header (头部)
头部通常由两部分组成：令牌的类型（`typ`），即 JWT，以及所使用的签名算法（`alg`），例如 HMAC SHA256 或 RSA。

一个典型的头部看起来像这样：
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
````

这个 JSON 会被 `Base64Url` 编码，形成 JWT 的第一部分。

#### Payload (负载)

负载部分包含**声明（Claims）**。声明是关于实体（通常是用户）和其他数据的陈述。声明有三种类型：

  * **Registered claims（注册声明）**: 一些预定义的声明，例如 `iss` (签发者), `exp` (过期时间), `sub` (主题)。
  * **Public claims（公共声明）**: 由使用 JWT 的人随意定义，但为了避免冲突，应该在 IANA JSON Web Token Registry 中定义它们。
  * **Private claims（私有声明）**: 为在同意使用它们的各方之间共享信息而创建的自定义声明。

一个示例负载可能如下所示：

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "admin": true,
  "iat": 1516239022
}
```

该负载也会被 `Base64Url` 编码，以形成 JWT 的第二部分。

**重要提示：** 默认情况下，JWT 的负载是经过 Base64Url 编码的，而不是加密的。任何人都可以解码并读取其内容。因此，**切勿在负载中存储敏感信息**。

#### Signature (签名)

要创建签名部分，您必须获取编码后的头部、编码后的负载、一个**密钥（secret）**，以及在头部中指定的算法，并对其进行签名。

```javascript
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

签名用于验证消息在传输过程中没有被篡改，并验证发送者的身份。

### JWT 的工作流程

1.  **用户认证**: 用户使用凭据（如用户名密码）登录。
2.  **生成并返回 JWT**: 服务器验证凭据，如果成功，则创建一个 JWT 并将其返回给客户端。
3.  **客户端存储 JWT**: 客户端将 JWT 存储在本地（如 localStorage 或 HTTP-Only Cookie）。
4.  **在请求中发送 JWT**: 客户端访问受保护的资源时，会在请求的 `Authorization` 头部中以 `Bearer` 模式包含 JWT。
    ```
    Authorization: Bearer <token>
    ```
5.  **服务器验证 JWT**: 服务器验证令牌的签名。如果有效，则授权该请求。

-----

## 2\. 基础用法：JWT 的生成与验证

### Node.js 示例 (jsonwebtoken)

**安装:**

```bash
npm install jsonwebtoken
```

**代码:**

```javascript
const jwt = require('jsonwebtoken');

// 密钥应存储在环境变量中
const JWT_SECRET = 'your_super_secret_key';

// 1. 生成 Token
function generateToken(user) {
  const payload = { id: user.id, username: user.username };
  const options = { expiresIn: '1h' }; // 1小时后过期
  return jwt.sign(payload, JWT_SECRET, options);
}

// 2. 验证 Token (常用于 Express 中间件)
function verifyToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token == null) return res.sendStatus(401);

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403); // Token 无效或已过期
    req.user = user;
    next();
  });
}

// 使用示例
const myUser = { id: '123', username: 'testuser' };
const token = generateToken(myUser);
console.log('生成的 JWT:', token);
```

### Python 示例 (PyJWT)

**安装:**

```bash
pip install PyJWT
```

**代码:**

```python
import jwt
import datetime

JWT_SECRET = 'your_super_secret_key'
JWT_ALGORITHM = 'HS256'

# 1. 生成 Token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), # 过期时间
        'iat': datetime.datetime.utcnow() # 签发时间
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# 2. 验证 Token
def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return "令牌已过期"
    except jwt.InvalidTokenError:
        return "无效的令牌"

# 使用示例
my_user_id = '456'
token = generate_token(my_user_id)
print(f"生成的 JWT: {token}")

decoded_payload = verify_token(token)
print(f"解码后的负载: {decoded_payload}")
```

-----

## 3\. FastAPI 实战：构建 JWT 认证系统

我们将使用 `FastAPI` 和 `python-jose` 库来构建一个功能完整的认证系统。`python-jose` 是一个功能更全的库，推荐在 FastAPI 项目中使用。

**安装依赖:**

```bash
pip install "fastapi[all]" python-jose "passlib[bcrypt]" sqlalchemy
```

### 第一步：单用户的 FastAPI 认证

这是一个快速入门示例，用户数据硬编码在代码中。

**`main_simple.py`:**

```python
import os
from datetime import datetime, timedelta
from typing import Optional, Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# --- 配置 ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Pydantic 模型 ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# --- 密码处理 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 模拟数据库 ---
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": pwd_context.hash("secretpassword"),
        "disabled": False,
    }
}

# --- 辅助函数 ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- FastAPI 应用 ---
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None or user.disabled:
        raise credentials_exception
    return user

# --- 路由 ---
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
```

### 第二步：实现多用户注册与数据库认证

这是一个真实世界的方案，我们将引入数据库（SQLite + SQLAlchemy），并分离代码结构以提高可维护性。

**项目结构:**

```
.
├── main.py
├── crud.py
├── database.py
├── models.py
└── schemas.py
```

**`database.py`:**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**`models.py`:**

```python
from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
```

**`schemas.py`:**

```python
from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    disabled: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
```

**`crud.py`:**

```python
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
```

**`main.py` (最终版):**

```python
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from . import crud, models, schemas
from .database import SessionLocal, engine

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- 配置和依赖 ---
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 安全和认证 ---
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_active_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=username)
    if user is None or user.disabled:
        raise credentials_exception
    return user

# --- API 端点 ---
@app.post("/users/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    return current_user
```

**如何运行和测试最终版:**

1.  将上述文件保存在同一目录下。
2.  运行 `uvicorn main:app --reload`。
3.  访问 `http://127.0.0.1:8000/docs`。
4.  使用 `POST /users/` 端点注册一个新用户。
5.  使用 `POST /token` 端点，用新用户的凭据登录以获取 token。
6.  点击 "Authorize"，输入 `Bearer <your_token>`。
7.  访问 `GET /users/me/` 端点，你将看到当前登录用户的信息。

-----

## 4\. 安全性最佳实践

  * **使用强大的密钥**: 密钥（Secret Key）应该足够长且难以猜测，并始终存储在环境变量或安全的密钥管理服务中。
  * **使用 HTTPS**: 始终通过 HTTPS 传输 JWT，以防止中间人攻击。
  * **设置令牌过期时间**: 为 JWT 设置一个合理的过期时间（`exp` 声明），以减少令牌泄露带来的风险。
  * **不要在负载中存放敏感信息**: 负载是可解码的，避免存储密码等敏感数据。
  * **考虑令牌撤销**: JWT 本质上是无状态的。如果需要立即撤销某个用户的访问权限，你需要实现一个令牌撤销机制（例如，维护一个无效令牌的黑名单）。
  * **选择合适的签名算法**: `HS256` 是对称算法。`RS256` (非对称算法) 在某些场景下更安全，因为它允许公钥验证，而私钥可以保持安全。

<!-- end list -->

```