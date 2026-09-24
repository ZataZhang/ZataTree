---
title: SQLAlchemy简单入门
description: ""
date: 2025-03-11T09:43:28+08:00
image: images/index/index.png
# image: images/index/index.png
categories:
    - Library
tags:
    - SQL
---

## 基础使用

SQLAlchemy 是 Python 中最流行的 ORM（对象关系映射）工具，用于操作数据库。它分为两部分：**SQLAlchemy Core**（底层 SQL 操作）和 **SQLAlchemy ORM**（对象映射）。本教程将涵盖两者的基础知识和示例。

---

### 1. 安装 SQLAlchemy
首先，您需要安装 SQLAlchemy 和数据库驱动（例如 SQLite、MySQL 或 PostgreSQL）。这里以 SQLite 为例，因为它无需额外安装数据库服务器。

```bash
pip install sqlalchemy
```

如果使用 MySQL 或 PostgreSQL，需要安装对应的驱动：
- MySQL: `pip install pymysql`
- PostgreSQL: `pip install psycopg2`

---

### 2. SQLAlchemy Core 基础
SQLAlchemy Core 提供了一种接近原生 SQL 的方式来操作数据库。

#### 2.1 连接数据库
首先，我们需要创建一个引擎（Engine）来连接数据库。

```python
from sqlalchemy import create_engine

# SQLite 数据库（文件存储在本地）
engine = create_engine('sqlite:///example.db', echo=True)  # echo=True 打印 SQL 日志
```

#### 2.2 定义表结构
使用 `Table` 对象定义数据库表。

```python
from sqlalchemy import Table, Column, Integer, String, MetaData

# 创建元数据对象
metadata = MetaData()

# 定义 users 表
users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('age', Integer)
)
```

#### 2.3 创建表
将定义的表结构应用到数据库中。

```python
# 创建所有表
metadata.create_all(engine)
```

#### 2.4 插入数据
使用 `insert()` 方法插入数据。

```python
from sqlalchemy import insert

# 插入单条数据
with engine.connect() as connection:
    stmt = insert(users).values(name='Alice', age=25)
    connection.execute(stmt)
    connection.commit()

# 插入多条数据
with engine.connect() as connection:
    stmt = insert(users).values([
        {'name': 'Bob', 'age': 30},
        {'name': 'Charlie', 'age': 35}
    ])
    connection.execute(stmt)
    connection.commit()
```

#### 2.5 查询数据
使用 `select()` 方法查询数据。

```python
from sqlalchemy import select

with engine.connect() as connection:
    stmt = select(users).where(users.c.age > 25)  # 查询年龄大于 25 的用户
    result = connection.execute(stmt)
    for row in result:
        print(row)  # 输出：(id, name, age)
```

#### 2.6 更新和删除
更新和删除数据分别使用 `update()` 和 `delete()`。

```python
from sqlalchemy import update, delete

with engine.connect() as connection:
    # 更新
    stmt = update(users).where(users.c.name == 'Alice').values(age=26)
    connection.execute(stmt)
    connection.commit()

    # 删除
    stmt = delete(users).where(users.c.name == 'Charlie')
    connection.execute(stmt)
    connection.commit()
```

---

### 3. SQLAlchemy ORM 基础
SQLAlchemy ORM 将数据库表映射为 Python 类，提供更面向对象的方式。

#### 3.1 定义模型
使用声明式基类（Declarative Base）定义表结构。

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

# 创建基类
Base = declarative_base()

# 定义 User 类
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

    def __repr__(self):
        return f"<User(name='{self.name}', age={self.age})>"

# 创建引擎和表
engine = create_engine('sqlite:///example_orm.db', echo=True)
Base.metadata.create_all(engine)
```

#### 3.2 添加数据
使用会话（Session）操作数据。

```python
# 创建会话
with Session(engine) as session:
    # 添加单个用户
    alice = User(name='Alice', age=25)
    session.add(alice)

    # 添加多个用户
    session.add_all([
        User(name='Bob', age=30),
        User(name='Charlie', age=35)
    ])

    # 提交事务
    session.commit()
```

#### 3.3 查询数据
使用 `query` 或 `select` 进行查询。

```python
with Session(engine) as session:
    # 查询所有用户
    users = session.query(User).all()
    for user in users:
        print(user)

    # 过滤查询
    older_users = session.query(User).filter(User.age > 25).all()
    for user in older_users:
        print(user)
```

#### 3.4 更新和删除
直接修改对象或使用 `delete()`。

```python
with Session(engine) as session:
    # 更新
    alice = session.query(User).filter_by(name='Alice').first()
    alice.age = 26
    session.commit()

    # 删除
    charlie = session.query(User).filter_by(name='Charlie').first()
    session.delete(charlie)
    session.commit()
```

---

### 4. 关系（Relationships）
SQLAlchemy ORM 支持表之间的关系，例如一对多。

#### 4.1 定义关系模型
以下是一个用户（User）和地址（Address）的一对多关系示例。

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    addresses = relationship('Address', back_populates='user')  # 一对多关系

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='addresses')  # 多对一关系

# 创建表
Base.metadata.create_all(engine)
```

#### 4.2 操作关系数据
添加用户及其地址。

```python
with Session(engine) as session:
    user = User(name='Alice')
    user.addresses = [Address(email='alice@example.com'), Address(email='alice2@example.com')]
    session.add(user)
    session.commit()

    # 查询
    alice = session.query(User).filter_by(name='Alice').first()
    print(alice.addresses)  # 输出 Alice 的所有地址
```

---

### 5. 高级功能
#### 5.1 事务管理
SQLAlchemy 会话默认支持事务。如果需要手动控制：

```python
with Session(engine) as session:
    try:
        session.add(User(name='Test'))
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
```

#### 5.2 原生 SQL
如果需要执行原生 SQL：

```python
with engine.connect() as connection:
    result = connection.execute("SELECT * FROM users WHERE age > 25")
    for row in result:
        print(row)
```

#### 5.3 连接池
SQLAlchemy 默认使用连接池管理数据库连接，可以通过 `pool_size` 和 `max_overflow` 配置：

```python
engine = create_engine('sqlite:///example.db', pool_size=5, max_overflow=10)
```

---

### 6. 总结
- **Core** 适合需要灵活 SQL 的场景。
- **ORM** 适合面向对象编程，简化数据库操作。
- 通过 `engine`、`metadata` 和 `session`，SQLAlchemy 提供了强大的数据库操作能力。

---



## Model类的使用

```py

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    check_frequency = db.Column(db.String(50), nullable=False)
    last_checked = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    selectors = db.relationship('Selector', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')
    changes = db.relationship('Change', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subscription {self.name}>'
```


您提供的代码片段展示了一个使用 **Flask-SQLAlchemy**（基于 SQLAlchemy 的扩展）定义的 `Subscription` 模型类。这个类定义了一个数据库表结构，并包含了字段、外键和关系。以下是对这个类的详细解析：

---

### 前置条件
- `db = SQLAlchemy()`：这是一个 Flask-SQLAlchemy 的实例，通常在 Flask 应用中初始化。它封装了 SQLAlchemy 的功能，并与 Flask 应用上下文绑定。
- 需要导入必要的模块，例如：
  ```python
  from flask_sqlalchemy import SQLAlchemy
  from datetime import datetime
  ```

---

### 类定义
```python
class Subscription(db.Model):
```
- `Subscription` 是一个继承自 `db.Model` 的类，`db.Model` 是 Flask-SQLAlchemy 提供的基类，用于声明数据库模型。
- 这个类会映射到数据库中的一个表，默认表名为类名的小写形式（`subscription`）。如果想自定义表名，可以添加 `__tablename__ = 'custom_name'`。

---

### 字段（Columns）
每个字段使用 `db.Column` 定义，指定数据类型和约束条件。以下是逐一解析：

1. **`id = db.Column(db.Integer, primary_key=True)`**
   - 类型：`Integer`（整数）。
   - 约束：`primary_key=True` 表示这是主键，唯一标识每一行。通常会自动递增（SQLite 和 PostgreSQL 默认支持）。
   - 作用：作为表的主键，用于唯一标识每个订阅记录。

2. **`name = db.Column(db.String(100), nullable=False)`**
   - 类型：`String(100)`（长度最多 100 个字符的字符串）。
   - 约束：`nullable=False` 表示该字段不能为空，必须提供值。
   - 作用：存储订阅的名称，例如“新闻订阅”。

3. **`url = db.Column(db.String(500), nullable=False)`**
   - 类型：`String(500)`（长度最多 500 个字符的字符串）。
   - 约束：`nullable=False` 表示不能为空。
   - 作用：存储订阅的 URL，例如某个网站的地址。

4. **`category = db.Column(db.String(50), nullable=False)`**
   - 类型：`String(50)`（长度最多 50 个字符的字符串）。
   - 约束：`nullable=False` 表示不能为空。
   - 作用：存储订阅的类别，例如“科技”或“娱乐”。

5. **`check_frequency = db.Column(db.String(50), nullable=False)`**
   - 类型：`String(50)`。
   - 约束：`nullable=False` 表示不能为空。
   - 作用：存储检查频率，例如“daily”或“weekly”。（注：如果频率是固定的选项，可以考虑使用 `db.Enum` 类型。）

6. **`last_checked = db.Column(db.DateTime, nullable=True)`**
   - 类型：`DateTime`（日期时间类型）。
   - 约束：`nullable=True` 表示可以为空。
   - 作用：记录上一次检查订阅的时间，可能为空（例如新创建时尚未检查）。

7. **`last_updated = db.Column(db.DateTime, nullable=True)`**
   - 类型：`DateTime`。
   - 约束：`nullable=True` 表示可以为空。
   - 作用：记录订阅内容最后更新的时间，可能为空（例如未发生变化）。

8. **`status = db.Column(db.String(20), default='active')`**
   - 类型：`String(20)`。
   - 约束：`default='active'` 表示默认值为“active”。
   - 作用：存储订阅的状态，例如“active”或“inactive”。

9. **`created_at = db.Column(db.DateTime, default=datetime.utcnow)`**
   - 类型：`DateTime`。
   - 约束：`default=datetime.utcnow` 表示默认值为当前 UTC 时间（注意：这里使用的是函数 `datetime.utcnow` 而不是 `datetime.utcnow()`，因为 SQLAlchemy 需要一个可调用的对象）。
   - 作用：记录订阅创建的时间。

---

### 外键（Foreign Key）
```python
user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```
- 类型：`Integer`。
- 外键：`db.ForeignKey('user.id')` 表示这是一个外键，引用 `user` 表的 `id` 列。
- 约束：`nullable=False` 表示不能为空，必须关联一个用户。
- 作用：将 `Subscription` 与 `User` 表关联，表示每个订阅属于某个用户。

注意：这里假设存在一个 `User` 模型类，定义了 `id` 字段，例如：
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 其他字段...
```

---

### 关系（Relationships）
SQLAlchemy ORM 支持表之间的关系，这里定义了两个一对多关系：

1. **`selectors = db.relationship('Selector', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')`**
   - **目标**：`Selector` 是一个关联的模型类，表示“选择器”（可能用于指定订阅内容的提取规则）。
   - **backref**：`'subscription'` 表示在 `Selector` 类中可以通过 `subscription` 属性反向访问对应的 `Subscription` 对象。
   - **lazy**：`'dynamic'` 表示返回一个动态查询对象（而不是直接加载所有数据），可以用 `.all()` 或 `.filter()` 等方法进一步操作。
   - **cascade**：`'all, delete-orphan'` 表示所有操作（包括删除）都会级联到相关记录，且如果 `Subscription` 被删除，所有关联的 `Selector` 也会被删除（孤儿删除）。
   - 作用：一个订阅可以有多个选择器（一对多关系）。

   假设的 `Selector` 类：
   ```python
   class Selector(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))
       # 其他字段...
   ```

2. **`changes = db.relationship('Change', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')`**
   - **目标**：`Change` 表示“变更”记录（可能用于跟踪订阅内容的更改）。
   - **backref**：`'subscription'` 允许从 `Change` 反向访问 `Subscription`。
   - **lazy**：`'dynamic'` 同上。
   - **cascade**：`'all, delete-orphan'` 同上。
   - 作用：一个订阅可以有多个变更记录（一对多关系）。

   假设的 `Change` 类：
   ```python
   class Change(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))
       # 其他字段...
   ```

---

### 字符串表示方法
```python
def __repr__(self):
    return f'<Subscription {self.name}>'
```
- 定义了对象的字符串表示形式。
- 调用 `print(subscription)` 时会显示类似 `<Subscription News>` 的输出，便于调试。

---

### 整体功能解析
`Subscription` 类描述了一个订阅系统中的核心实体，可能用于一个订阅管理或内容监控应用：
- **字段**：记录订阅的基本信息（名称、URL、类别等）、状态和时间戳。
- **外键**：通过 `user_id` 与用户关联，确保每个订阅属于某个用户。
- **关系**：
  - `selectors`：允许为订阅定义多个选择器（例如 CSS 选择器或 XPath，用于提取网页内容）。
  - `changes`：记录订阅内容的变更历史。
- **级联删除**：当订阅被删除时，关联的 `selectors` 和 `changes` 也会自动删除。

---

### 示例用法
假设在 Flask 应用中初始化并使用这个模型：

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

# 定义模型（如上所述）

# 创建表
with app.app_context():
    db.create_all()

# 添加数据
with app.app_context():
    new_subscription = Subscription(
        name='Tech News',
        url='https://example.com',
        category='Tech',
        check_frequency='daily',
        user_id=1
    )
    db.session.add(new_subscription)
    db.session.commit()

# 查询
with app.app_context():
    subscription = Subscription.query.filter_by(name='Tech News').first()
    print(subscription)  # 输出: <Subscription Tech News>
    print(subscription.selectors.all())  # 查询关联的 selectors
```

---

### 注意事项
1. **Flask 上下文**：Flask-SQLAlchemy 需要在应用上下文中操作（如 `with app.app_context():`）。
2. **外键完整性**：确保 `user_id` 引用的 `User` 记录存在，否则会抛出异常。
3. **动态加载**：`lazy='dynamic'` 适合大数据量场景，但需要显式调用 `.all()` 或其他方法来获取数据。


## SQLAlchemy Relationships 教程：理解数据库表之间的关系

在这篇教程中，我们将探讨如何使用 SQLAlchemy（一个流行的 Python ORM 工具）中的 `db.relationship` 来定义和操作数据库表之间的关系。我们将以一个简单的订阅监控系统为例，逐步讲解代码，并展示如何通过关系字段简化数据库操作。

当前日期是 **2025年3月10日**，我们将使用最新版本的 SQLAlchemy 语法。

---

### 示例背景：订阅监控系统
假设我们正在构建一个系统，用于监控网页的变化。系统中包含以下三个表：
- **Subscription（订阅）**：表示用户订阅的网页监控任务。
- **Selector（选择器）**：定义订阅中要监控的网页元素（如某个 `<div>` 或 `<p>`）。
- **Change（变化）**：记录选择器检测到的变化（如内容更新或元素出现/消失）。

这些表之间存在关联：
- 一个 `Subscription` 可以有多个 `Selector` 和多个 `Change`（一对多）。
- 一个 `Selector` 可以有多个 `Change`（一对多）。
- `Change` 属于某个 `Subscription` 和某个 `Selector`。

我们将使用 SQLAlchemy 的 `db.relationship` 来定义这些关系。

---

### 模型代码
以下是完整的模型定义，我们将在后面逐一讲解其中的 `Relationships`。

```python
from app import db
from datetime import datetime

# 订阅表
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    check_frequency = db.Column(db.String(50), nullable=False)
    last_checked = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关系字段
    selectors = db.relationship('Selector', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')
    changes = db.relationship('Change', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subscription {self.name}>'

# 选择器表
class Selector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    selector_path = db.Column(db.String(500), nullable=False)
    monitor_type = db.Column(db.String(50), nullable=False)  # content_change, element_presence, attribute_change
    keywords = db.Column(db.String(500), nullable=True)
    last_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    
    def __repr__(self):
        return f'<Selector {self.name} for {self.subscription_id}>'

# 变化表
class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    selector_id = db.Column(db.Integer, db.ForeignKey('selector.id'), nullable=False)
    old_content = db.Column(db.Text, nullable=True)
    new_content = db.Column(db.Text, nullable=True)
    change_type = db.Column(db.String(50), nullable=False)  # content_change, element_appeared, element_disappeared, attribute_change
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    
    # 关系字段
    selector = db.relationship('Selector')
    
    def __repr__(self):
        return f'<Change {self.id} for {self.subscription_id}>'
```

---

### 什么是 `db.relationship`？
`db.relationship` 是 SQLAlchemy 提供的一种工具，用于定义数据库表之间的关系。它允许你：
- 通过对象属性访问关联的数据，而无需手动编写 SQL 查询。
- 支持一对多、多对一等关系。
- 通过 `backref` 参数实现双向访问。

在我们的代码中，`db.relationship` 连接了 `Subscription`、`Selector` 和 `Change` 三个表。

---

### 逐步解析代码中的 `Relationships`

#### `Subscription` 中的关系
在 `Subscription` 类中定义了两个关系字段：

##### `selectors = db.relationship('Selector', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')`
- **含义**：
  - `Subscription` 和 `Selector` 是一对多关系。一个订阅可以有多个选择器。
  - `Selector` 表中的 `subscription_id` 是外键，指向 `Subscription` 的 `id`。
- **参数解析**：
  - `'Selector'`：关联的目标模型类。
  - `backref='subscription'`：在 `Selector` 中生成一个反向引用属性 `subscription`，允许从 `Selector` 访问其所属的 `Subscription`。
  - `lazy='dynamic'`：延迟加载，返回一个动态查询对象，需要手动调用 `.all()` 或其他方法获取数据。
  - `cascade='all, delete-orphan'`：当 `Subscription` 被删除时，其所有 `Selector` 也会被删除；如果某个 `Selector` 失去了与 `Subscription` 的关联，也会被删除。
- **用法示例**：
  ```python
  sub = Subscription.query.get(1)  # 获取 ID 为 1 的订阅
  all_selectors = sub.selectors.all()  # 获取所有相关选择器
  for selector in all_selectors:
      print(selector.name)
  ```

##### `changes = db.relationship('Change', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')`
- **含义**：
  - `Subscription` 和 `Change` 是一对多关系。一个订阅可以有多个变化记录。
- **参数解析**：
  - 同上，`backref` 和 `cascade` 的作用类似。
- **用法示例**：
  ```python
  sub = Subscription.query.get(1)
  all_changes = sub.changes.all()  # 获取所有变化记录
  for change in all_changes:
      print(f"Change: {change.old_content} -> {change.new_content}")
  ```

---

#### `Change` 中的关系
##### `selector = db.relationship('Selector')`
- **含义**：
  - `Change` 和 `Selector` 是一对多关系。一个选择器可以有多个变化记录。
  - `Change` 表中的 `selector_id` 是外键，指向 `Selector` 的 `id`。
- **参数解析**：
  - `'Selector'`：关联的目标模型类。
  - 默认 `lazy='select'`：在访问时自动加载关联的 `Selector` 对象。
  - 没有 `backref`，因此无法从 `Selector` 直接访问其所有 `Change`（需要手动查询）。
- **用法示例**：
  ```python
  change = Change.query.get(1)  # 获取 ID 为 1 的变化记录
  related_selector = change.selector  # 获取对应的选择器
  print(related_selector.name)
  ```

---

### `Relationships` 的核心作用
通过 `db.relationship`，我们可以：
1. **简化数据访问**：
   - 无需编写复杂的 SQL JOIN 查询，直接通过对象属性访问关联数据。
2. **支持双向导航**：
   - 例如，从 `Subscription` 到 `Selector`（`sub.selectors`），或从 `Selector` 到 `Subscription`（`selector.subscription`）。
3. **自动管理外键**：
   - 创建对象时，SQLAlchemy 会自动处理外键赋值。
4. **级联操作**：
   - 删除 `Subscription` 时，其所有 `Selector` 和 `Change` 也会被删除。

---

### 实战示例
让我们通过一个完整示例展示 `Relationships` 的用法。

#### 创建数据
```python
# 创建一个订阅
sub = Subscription(
    name="Tech News",
    url="https://example.com/news",
    category="News",
    check_frequency="daily",
    user_id=1
)

# 创建两个选择器
selector1 = Selector(
    name="Headline",
    selector_path="div.headline",
    monitor_type="content_change",
    subscription=sub  # 自动关联
)
selector2 = Selector(
    name="Summary",
    selector_path="p.summary",
    monitor_type="content_change",
    subscription=sub
)

# 创建一个变化记录
change = Change(
    selector_id=selector1.id,
    old_content="Old Headline",
    new_content="New Headline",
    change_type="content_change",
    subscription=sub
)

# 保存到数据库
db.session.add(sub)
db.session.commit()
```

#### 查询数据
```python
# 获取订阅
sub = Subscription.query.filter_by(name="Tech News").first()

# 查看所有选择器
print("Selectors:")
for selector in sub.selectors:
    print(f"- {selector.name}: {selector.selector_path}")

# 查看所有变化
print("Changes:")
for change in sub.changes:
    print(f"- {change.old_content} -> {change.new_content}")

# 从变化反向访问选择器
first_change = sub.changes.first()
print(f"Change belongs to selector: {first_change.selector.name}")
```

**输出示例**：
```
Selectors:
- Headline: div.headline
- Summary: p.summary
Changes:
- Old Headline -> New Headline
Change belongs to selector: Headline
```

---

### 总结
- **`db.relationship`** 是 SQLAlchemy 中定义表关系的核心工具。
- 它通过外键建立联系，支持对象化导航和级联操作。
- 参数如 `backref`、`lazy` 和 `cascade` 提供了灵活的控制方式。
- 在实际开发中，合理使用 `Relationships` 可以大大简化代码，提高开发效率。

