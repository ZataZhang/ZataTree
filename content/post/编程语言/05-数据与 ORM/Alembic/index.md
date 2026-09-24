---
title: Alembic
description: ""
date: 2025-09-12T17:43:01+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SQL
---



常用命令
```bash
# === Alembic 核心命令速查 ===

# 1. 初始化
# 作用：在项目中创建 Alembic 环境 (alembic.ini, env.py 等)
alembic init <alembic目录名>

# 2. 生成迁移脚本
# 作用：对比模型与数据库差异，自动生成迁移文件
alembic revision -m "简短的描述" --autogenerate

# 3. 执行升级 (应用迁移)
# 作用：将数据库更新到最新版本
alembic upgrade head
# 作用：升级到指定版本
alembic upgrade <版本号>
# 作用：向前升级 1 个版本
alembic upgrade +1

# 4. 执行降级 (回滚迁移)
# 作用：将数据库回滚 1 个版本
alembic downgrade -1
# 作用：回滚到指定版本
alembic downgrade <版本号>
# 作用：回滚到最初始 (空) 状态
alembic downgrade base

# 5. 查看状态
# 作用：查看当前数据库所在的版本
alembic current
# 作用：查看所有迁移历史
alembic history

# 6. 标记版本 (不执行SQL)
# 作用：将数据库“欺骗”为已处于某个版本 (常用于修复错误状态)
alembic stamp head
alembic stamp <版本号>

# 7. 查看迁移内容
# 作用：显示某个迁移版本将执行的 SQL (预览)
alembic show <版本号或head>

```




### 什么是 Alembic？

Alembic 是一个为 [SQLAlchemy](https://www.sqlalchemy.org/) 设计的轻量级数据库迁移工具。在软件开发中，特别是项目迭代过程中，数据库的结构（Schema）几乎不可避免地会发生变化，例如添加新表、增加字段、修改数据类型等。直接在生产数据库上手动修改 SQL 是一件风险很高且难以追踪和协作的事情。

Alembic 的出现就是为了解决这个问题。它允许你：

  * **版本化管理数据库结构**：就像使用 Git 管理代码一样，Alembic 可以为你的数据库结构的每一次变更创建一个版本。
  * **生成迁移脚本**：它可以自动或半自动地检测你的 SQLAlchemy 模型（Models）与当前数据库结构之间的差异，并生成相应的 Python 迁移脚本。
  * **轻松升级和降级**：你可以通过简单的命令，将数据库结构“升级”到最新版本，或者“降级”到任意一个旧版本。
  * **团队协作**：团队成员可以共享迁移脚本，确保每个人的开发环境和最终的生产环境数据库结构保持一致。
  * **保证数据安全**：它提供了在迁移过程中处理现有数据的能力。

简单来说，**Alembic 就是连接你的应用程序代码（通过 SQLAlchemy 模型定义）和数据库实际状态之间的桥梁，并用版本化的脚本来管理这种变化。**

### Alembic 核心概念

在开始使用之前，理解几个核心概念至关重要：

  * **Migration (迁移)**：指从一个数据库结构版本变为另一个版本的操作。
  * **Revision (版本号)**：Alembic 会为每一次迁移生成一个唯一的、有序的版本号（一个哈希字符串），用于标识数据库的特定状态。
  * **Migration Script (迁移脚本)**：一个包含 `upgrade()` 和 `downgrade()` 两个函数的 Python 文件。`upgrade()` 函数定义了如何将数据库“升级”到这个版本，而 `downgrade()` 则定义了如何“降级”回上一个版本。
  * **Environment (环境)**：Alembic 的运行环境。它由 `alembic.ini` 配置文件和 `env.py` 脚本文件定义，用于配置数据库连接、SQLAlchemy 模型的元数据等。

-----

### Alembic 使用教程

下面我们将通过一个实际的例子，一步步带你入门 Alembic。

#### 第一步：安装

首先，确保你已经安装了 SQLAlchemy 和 Alembic。如果还没有，可以通过 uv或者 pip 安装：

```bash
uv add sqlalchemy almbic
---
pip install sqlalchemy alembic
```

同时，你需要为你想要连接的数据库安装相应的驱动。例如，对于 PostgreSQL，你可能需要安装 `psycopg2-binary`：

```bash
pip install psycopg2-binary
```
如果是Sqlite的话，就不需要安装驱动

#### 第二步：初始化 Alembic 环境

在一个新的项目目录中，运行以下命令来创建一个 Alembic "迁移仓库"：

```bash
alembic init alembic
```

这个命令会创建一个名为 `alembic` 的文件夹和一个 `alembic.ini` 配置文件。目录结构如下：

```
your_project/
├── alembic/
│   ├── versions/            # 存放所有迁移脚本的地方
│   ├── script.py.mako       # 生成迁移脚本的模板
│   └── env.py               # 配置和运行Alembic环境的脚本
└── alembic.ini              # Alembic 的主配置文件
```

#### 第三步：配置数据库连接

打开 `alembic.ini` 文件，找到 `sqlalchemy.url` 这一行，并修改它以指向你的数据库。例如，使用 Sqlite：

```ini
# atexample.ini
...
sqlalchemy.url = sqlite:///./resources/app.db
...
```
页可以在env.py文件中进行配置'config.set_main_option("sqlalchemy.url", settings.database_url) '
```python
from alembic import context

# Add the project root to the path to import our app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import our database configuration and models
from app.core.database import Base
from app.core.config import settings
from app.models import User  # Import models for autogenerate

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from our configuration
config.set_main_option("sqlalchemy.url", settings.database_url) 
```



#### 第四步：关联 SQLAlchemy 模型

现在，需要让 Alembic知道你的 SQLAlchemy 模型定义在哪里，以便进行比较。

1.  **创建你的模型**：
    假设你在项目根目录下有一个 `models.py` 文件，内容如下：

    ```python
    # models.py
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)
        email = Column(String(100)) # 假设我们稍后会把这个字段设为非空
    ```

2.  **配置 `env.py`**：
    打开 `alembic/env.py` 文件，进行以下修改：

      * 导入你的模型 `Base`：

        ```python
        # 在文件顶部
        from my_project.models import Base # 假设你的项目名叫 my_project
        ```

      * 找到 `target_metadata = None` 这一行，并将其修改为：

        ```python
        # 指向你的模型的 Base.metadata
        target_metadata = Base.metadata
        ```

    这步操作告诉 Alembic：“请以 `Base.metadata` 中定义的模型作为最终的数据库结构标准。”

#### 第五步：创建第一个迁移脚本

现在，你的数据库还是空的，而你的代码中已经定义了一个 `User` 模型。让我们来生成第一个迁移脚本，以在数据库中创建 `users` 表。

运行以下命令：

```bash
alembic revision --autogenerate -m "Create users table"
```

  * `revision`: 创建一个新的版本脚本。
  * `--autogenerate`: 这个是 Alembic 的核心功能之一。它会自动检测 `target_metadata` (你的模型) 和当前数据库之间的差异，并自动生成迁移代码。
  * `-m "..."`: 为这次迁移添加一段简短的描述信息。

执行成功后，你会在 `alembic/versions/` 目录下看到一个新的 Python 文件，文件名类似 `xxxxxxxxxxxx_create_users_table.py`。打开它，内容大致如下：

**需要非常注意的一点是，upgrade和downgrade函数需要再次检查一下，因为会生成错误，例如，想要设置默认的数值，需要在生成之后添加server_default='0'参数**

```python
"""Create users table

Revision ID: xxxxxxxxxxxx
Revises:
Create Date: 2023-10-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'xxxxxxxxxxxx'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
```

`upgrade()` 函数包含了创建 `users` 表的代码，而 `downgrade()` 则包含了删除该表的代码。

#### 第六步：应用迁移 (升级数据库)

现在，我们来执行这个迁移脚本，真正地在数据库中创建这张表。

运行以下命令：

```bash
alembic upgrade head
```

  * `upgrade`: 执行升级操作。
  * `head`: `head` 是一个特殊的标识符，代表最新的版本。这条命令的意思是“将数据库升级到最新版本”。

执行后，连接到你的数据库，你会发现 `users` 表已经被成功创建了。同时，数据库中还会多出一张名为 `alembic_version` 的表，它用来记录当前数据库的版本号。

#### 第七步：进行模型变更并再次迁移

项目继续开发，需求变更，我们需要给 `User` 模型增加一个 `fullname` 字段，并且把 `email` 字段设置为非空。

1.  **修改模型**：

    ```python
    # models.py
    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)
        fullname = Column(String(100)) # 新增字段
        email = Column(String(100), nullable=False) # 修改为非空
    ```

2.  **生成新的迁移脚本**：
    再次运行 `autogenerate` 命令：

    ```bash
    alembic revision --autogenerate -m "Add fullname column and set email to non-nullable"
    ```

    Alembic 会检测到模型的变动，并生成一个新的迁移脚本。内容可能如下：

    ```python
    """Add fullname column and set email to non-nullable

    Revision ID: yyyyyyyyyyyy
    Revises: xxxxxxxxxxxx
    Create Date: 2023-10-27 10:10:00.000000

    """
    ...
    def upgrade() -> None:
        # ### commands auto generated by Alembic - please adjust! ###
        op.add_column('users', sa.Column('fullname', sa.String(length=100), nullable=True))
        op.alter_column('users', 'email',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=False)
        # ### end Alembic commands ###

    def downgrade() -> None:
        # ### commands auto generated by Alembic - please adjust! ###
        op.alter_column('users', 'email',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=True)
        op.drop_column('users', 'fullname')
        # ### end Alembic commands ###
    ```

    **注意**：将一个可空列改为不可空列时，如果表中已有数据且该列为 `NULL`，直接升级会失败。`autogenerate` 无法解决所有逻辑问题，有时需要你手动编辑迁移脚本，例如为已有行的 `email` 列提供一个默认值。

3.  **应用新的迁移**：

    ```bash
    alembic upgrade head
    ```

    执行后，`users` 表的结构就会被更新。

#### 第八步：降级数据库

如果你想撤销最近的一次迁移，可以执行降级操作。

```bash
# 降级一个版本
alembic downgrade -1

# 降级到指定的版本号
alembic downgrade yyyyyyyyyyyy

# 降级到最初始的状态（空数据库）
alembic downgrade base
```

### 常用 Alembic 命令总结

  * `alembic init <directory>`: 初始化 Alembic 仓库。
  * `alembic revision --autogenerate -m "message"`: 自动生成新的迁移脚本。
  * `alembic upgrade head`: 升级到最新版本。
  * `alembic upgrade +1`: 升级一个版本。
  * `alembic upgrade <revision>`: 升级到指定版本。
  * `alembic downgrade base`: 降级到最初始状态。
  * `alembic downgrade -1`: 降级一个版本。
  * `alembic downgrade <revision>`: 降级到指定版本之前。
  * `alembic history`: 显示迁移历史记录。
  * `alembic current`: 显示当前数据库的版本号。
  * `alembic stamp head`: 不执行迁移脚本，但将数据库的版本号标记为最新。这在手动修改数据库后，想让 Alembic 状态与数据库同步时很有用。

希望这份详细的介绍和教程能帮助你快速上手 Alembic！它是一个非常强大且实用的工具，在任何使用 SQLAlchemy 的项目中都值得引入。