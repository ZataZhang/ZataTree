---
title: Flask使用教程
description: ""
date: 2025-03-10T16:00:15+08:00
image: images/index/index.png
# image: images/index/index.png
categories:
    - Library
tags:
    - Flask
    - 教程
---




## Flak的基础语法和使用

### 1. 安装 Flask

首先，你需要安装 Flask。确保你已经安装了 Python（推荐使用 Python 3.7 或以上版本）。可以通过 `pip` 安装 Flask：

```bash
pip install flask
```

安装完成后，你可以在 Python 解释器中验证是否成功安装：

```python
import flask
print(flask.__version__)
```

如果没有报错并输出版本号，说明 Flask 已成功安装。

---

### 2. 创建一个简单的 Flask 应用

让我们创建一个最基本的 Flask 应用。以下是一个简单的示例代码，保存为 `app.py`：

```python
from flask import Flask

# 创建 Flask 应用实例
app = Flask(__name__)

# 定义路由和视图函数
@app.route('/')
def home():
    return '欢迎使用 Flask!'

# 运行应用
if __name__ == '__main__':
    app.run(debug=True)
```

#### 代码解释：
- `Flask(__name__)`：创建一个 Flask 应用实例，`__name__` 是 Python 的内置变量，表示当前模块的名称。
- `@app.route('/')`：定义一个路由，当用户访问根路径（`/`）时，触发下面的函数。
- `app.run(debug=True)`：启动 Flask 内置的开发服务器，`debug=True` 启用调试模式，方便开发时查看错误。

#### 运行应用：
在终端中进入文件所在目录，运行以下命令：

```bash
python app.py
```

然后在浏览器中访问 `http://127.0.0.1:5000/`，你会看到页面显示“欢迎使用 Flask!”。

---

### 3. 添加更多路由

Flask 允许你定义多个路由。例如，我们可以添加一个新的路由 `/hello`：

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '欢迎使用 Flask!'

@app.route('/hello')
def hello():
    return '你好，世界!'

if __name__ == '__main__':
    app.run(debug=True)
```

访问 `http://127.0.0.1:5000/hello`，你会看到“你好，世界!”。

#### 动态路由：
你还可以通过路由参数传递动态值，例如：

```python
@app.route('/user/<name>')
def user(name):
    return f'你好，{name}!'
```

访问 `http://127.0.0.1:5000/user/Alice`，页面会显示“你好，Alice!”。

---

```py
from flask import Flask, request

app = Flask(__name__)

@app.route('/greet')
def greet():
    # Access query string parameters using request.args
    name = request.args.get('name', 'Guest')  # Default to 'Guest' if 'name' is not provided
    return f'你好，{name}!'

if __name__ == '__main__':
    app.run(debug=True)
```


在浏览器中访问 `URL_ADDRESS在浏览器中访问 `http://127.0.0.1:5000/greet?name=Alice`，页面会显示“你好，Alice!”。



### 4. 使用模板渲染 HTML

直接返回字符串不适合复杂的页面。Flask 支持使用 Jinja2 模板引擎来渲染 HTML 文件。首先，创建一个 `templates` 文件夹，并在其中创建一个文件 `index.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask 教程</title>
</head>
<body>
    <h1>欢迎，{{ name }}!</h1>
</body>
</html>
```

然后修改 `app.py` 使用模板：

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/user/<name>')
def user(name):
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
```

- `render_template`：渲染模板并传入变量（这里是 `name`）。
- 文件结构：
  ```
  项目文件夹/
  ├── app.py
  └── templates/
      └── index.html
  ```

访问 `http://127.0.0.1:5000/user/Bob`，页面会显示“欢迎，Bob!”。

---


### 5. 使用过滤器

Jinja2 提供了许多内置过滤器，用于在模板中处理变量。你也可以自定义过滤器。以下是一些常见的用法。

#### 修改 `app.py`
我们将传递更多数据到模板中，以便展示过滤器的效果：

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/user/<name>')
def user(name):
    user_data = {
        'name': name,
        'age': 25,
        'bio': '这是一个简单的介绍。',
        'join_date': '2023-10-15'
    }
    return render_template('index.html', **user_data)

if __name__ == '__main__':
    app.run(debug=True)
```

#### 修改 `templates/index.html`
添加一些过滤器示例：

```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask 教程</title>
</head>
<body>
    <h1>欢迎，{{ name | upper }}!</h1>
    <p>年龄: {{ age | default('未知') }}</p>
    <p>简介: {{ bio | truncate(10) }}</p>
    <p>加入日期: {{ join_date | replace('-', '/') }}</p>
    <p>名字长度: {{ name | length }}</p>
</body>
</html>
```

#### 过滤器说明
- `| upper`：将字符串转换为大写，例如“alice”变成“ALICE”。
- `| default('未知')`：如果变量未定义或为空，则显示默认值“未知”。
- `| truncate(10)`：截断字符串到指定长度（这里是 10 个字符），超出部分用省略号表示。
- `| replace('-', '/')`：将字符串中的“-”替换为“/”，例如“2023-10-15”变成“2023/10/15”。
- `| length`：返回变量的长度，例如“Alice”的长度是 5。

#### 运行结果
访问 `http://127.0.0.1:5000/user/Alice`，页面显示：
```
欢迎，ALICE!
年龄: 25
简介: 这是一个简...
加入日期: 2023/10/15
名字长度: 5
```

#### 自定义过滤器
如果内置过滤器不够用，可以定义自己的过滤器。例如，我们添加一个反转字符串的过滤器：

修改 `app.py`：

```python
from flask import Flask, render_template

app = Flask(__name__)

# 自定义过滤器：反转字符串
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.route('/user/<name>')
def user(name):
    user_data = {
        'name': name,
        'age': 25,
        'bio': '这是一个简单的介绍。',
        'join_date': '2023-10-15'
    }
    return render_template('index.html', **user_data)

if __name__ == '__main__':
    app.run(debug=True)
```

修改 `index.html`，添加自定义过滤器：

```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask 教程</title>
</head>
<body>
    <h1>欢迎，{{ name | upper }}!</h1>
    <p>年龄: {{ age | default('未知') }}</p>
    <p>简介: {{ bio | truncate(10) }}</p>
    <p>加入日期: {{ join_date | replace('-', '/') }}</p>
    <p>名字长度: {{ name | length }}</p>
    <p>反转名字: {{ name | reverse }}</p>
</body>
</html>
```

访问 `http://127.0.0.1:5000/user/Alice`，页面会多一行：
```
反转名字: ecilA
```

- `@app.template_filter('reverse')`：注册一个名为 `reverse` 的自定义过滤器。
- `s[::-1]`：Python 切片语法，反转字符串。

---



### 6. 处理表单数据

Flask 可以轻松处理用户提交的表单数据。以下是一个简单的例子，包含 GET 和 POST 请求：

#### 修改 `templates/index.html`：
```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask 表单</title>
</head>
<body>
    <h1>提交你的名字</h1>
    <form method="POST">
        <input type="text" name="username">
        <input type="submit" value="提交">
    </form>
    {% if name %}
        <h2>你好，{{ name }}!</h2>
    {% endif %}
</body>
</html>
```

#### 修改 `app.py`：
```python
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    name = None
    if request.method == 'POST':
        name = request.form['username']
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
```

- `request`：从 Flask 中导入，用于获取表单数据。
- `methods=['GET', 'POST']`：允许该路由处理 GET 和 POST 请求。
- `request.form['username']`：获取表单中 `name="username"` 的输入值。

运行后，访问 `http://127.0.0.1:5000/`，输入名字并提交，会显示欢迎信息。

---



### 7. 使用控制语句

Jinja2 模板支持控制语句，主要包括条件语句（`if`、`elif`、`else`）和循环语句（`for`）。这些语句可以根据传入的数据动态渲染内容。

#### 修改 `app.py`
我们将传递一个包含用户列表的数据，并添加一些条件判断的变量：

```python
from flask import Flask, render_template

app = Flask(__name__)

# 自定义过滤器：反转字符串
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.route('/users')
def users():
    user_list = [
        {'name': 'Alice', 'age': 25, 'active': True},
        {'name': 'Bob', 'age': 30, 'active': False},
        {'name': 'Charlie', 'age': 15, 'active': True}
    ]
    show_details = True  # 用于条件语句
    return render_template('users.html', users=user_list, show_details=show_details)

if __name__ == '__main__':
    app.run(debug=True)
```

#### 创建 `templates/users.html`
在 `templates` 文件夹中新建 `users.html`，添加条件语句和循环语句：

```html
<!DOCTYPE html>
<html>
<head>
    <title>用户列表</title>
</head>
<body>
    <h1>用户列表</h1>

    <!-- 循环语句：遍历用户列表 -->
    <ul>
    {% for user in users %}
        <li>
            {{ user.name }} (年龄: {{ user.age }})
            <!-- 条件语句：根据 active 显示状态 -->
            {% if user.active %}
                <span style="color: green;">活跃</span>
            {% else %}
                <span style="color: red;">不活跃</span>
            {% endif %}
        </li>
    {% endfor %}
    </ul>

    <!-- 条件语句：是否显示详细信息 -->
    {% if show_details %}
        <h2>额外信息</h2>
        <p>总用户数: {{ users | length }}</p>
        <p>第一个用户: {{ users[0].name | upper }}</p>
    {% else %}
        <p>详细信息已隐藏</p>
    {% endif %}

    <!-- 多条件示例 -->
    {% for user in users %}
        {% if user.age >= 18 and user.active %}
            <p>{{ user.name }} 是成年活跃用户</p>
        {% elif user.age < 18 %}
            <p>{{ user.name }} 是未成年</p>
        {% endif %}
    {% endfor %}
</body>
</html>
```

#### 控制语句说明
1. **循环语句 `for`**：
   - `{% for user in users %}`：遍历 `users` 列表，`user` 是每次循环的单个元素。
   - 在 `<ul>` 中动态生成每个用户的 `<li>` 标签。

2. **条件语句 `if`**：
   - `{% if user.active %}`：检查用户是否活跃，显示不同颜色状态。
   - `{% if show_details %}`：根据 `show_details` 的值决定是否显示额外信息。
   - `{% elif %}` 和 `{% else %}`：支持多条件分支。

3. **结合过滤器**：
   - `{{ users | length }}`：计算用户列表长度。
   - `{{ users[0].name | upper }}`：将第一个用户的名字转换为大写。

#### 运行结果
访问 `http://127.0.0.1:5000/users`，页面显示：
```
用户列表
- Alice (年龄: 25) 活跃
- Bob (年龄: 30) 不活跃
- Charlie (年龄: 15) 活跃

额外信息
总用户数: 3
第一个用户: ALICE

Alice 是成年活跃用户
Charlie 是未成年
```

#### 修改条件
如果你将 `app.py` 中的 `show_details = True` 改为 `False`，则“额外信息”部分会变为：
```
详细信息已隐藏
```

#### 嵌套控制语句
你还可以在循环中嵌套条件语句，或者在条件中嵌套循环。例如，添加一个嵌套示例到 `users.html`：

```html
<!-- 嵌套示例：列出活跃用户 -->
<h2>活跃用户</h2>
<ul>
{% for user in users if user.active %}
    <li>{{ user.name }}</li>
{% endfor %}
</ul>
```

这会输出：
```
活跃用户
- Alice
- Charlie
```

- `{% for user in users if user.active %}`：直接在 `for` 循环中过滤，只遍历活跃用户。

---


### 8. 添加静态文件

Flask 支持静态文件（如 CSS、图片等）。创建一个 `static` 文件夹，并在其中添加 `style.css`：

```css
h1 {
    color: blue;
}
```

修改 `index.html` 引入样式：

```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask 表单</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>提交你的名字</h1>
    <form method="POST">
        <input type="text" name="username">
        <input type="submit" value="提交">
    </form>
    {% if name %}
        <h2>你好，{{ name }}!</h2>
    {% endif %}
</body>
</html>
```

- `url_for('static', filename='style.css')`：生成静态文件的 URL。

文件结构：
```
项目文件夹/
├── app.py
├── static/
│   └── style.css
└── templates/
    └── index.html
```

重新运行应用，标题会变成蓝色。

---


### 9. 模板继承

模板继承通过定义一个基础模板（包含通用结构），然后在子模板中扩展特定部分，非常适合构建具有一致布局的网站。

#### 创建基础模板 `templates/base.html`
在 `templates` 文件夹中创建 `base.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}默认标题{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <h1>欢迎使用 Flask</h1>
        <nav>
            <a href="{{ url_for('home') }}">首页</a> |
            <a href="{{ url_for('users') }}">用户列表</a>
        </nav>
    </header>

    <!-- 内容块，子模板可以覆盖 -->
    {% block content %}
        <p>这是默认内容</p>
    {% endblock %}

    <footer>
        <p>&copy; 2025 Flask 教程</p>
    </footer>
</body>
</html>
```

- `{% block title %}` 和 `{% block content %}`：定义可被子模板覆盖的块。
- `{{ url_for('xxx') }}`：动态生成路由链接。
- 静态文件 `style.css` 已在上文提到，确保 `static` 文件夹中有该文件。

#### 修改 `app.py`
添加首页路由，并更新用户路由以使用模板继承：

```python
from flask import Flask, render_template

app = Flask(__name__)

# 自定义过滤器：反转字符串
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/users')
def users():
    user_list = [
        {'name': 'Alice', 'age': 25, 'active': True},
        {'name': 'Bob', 'age': 30, 'active': False},
        {'name': 'Charlie', 'age': 15, 'active': True}
    ]
    show_details = True
    return render_template('users.html', users=user_list, show_details=show_details)

if __name__ == '__main__':
    app.run(debug=True)
```

#### 创建子模板 `templates/home.html`
继承 `base.html`，覆盖特定块：

```html
{% extends "base.html" %}

{% block title %}首页{% endblock %}

{% block content %}
    <h2>欢迎来到首页</h2>
    <p>这是一个简单的 Flask 应用示例。</p>
{% endblock %}
```

- `{% extends "base.html" %}`：指定继承的基础模板。
- `{% block title %}`：覆盖标题块。
- `{% block content %}`：覆盖内容块。

#### 修改 `templates/users.html` 使用继承
将之前的 `users.html` 修改为继承 `base.html`：

```html
{% extends "base.html" %}

{% block title %}用户列表{% endblock %}

{% block content %}
    <h2>用户列表</h2>
    <ul>
    {% for user in users %}
        <li>
            {{ user.name }} (年龄: {{ user.age }})
            {% if user.active %}
                <span style="color: green;">活跃</span>
            {% else %}
                <span style="color: red;">不活跃</span>
            {% endif %}
        </li>
    {% endfor %}
    </ul>

    {% if show_details %}
        <h3>额外信息</h3>
        <p>总用户数: {{ users | length }}</p>
        <p>第一个用户: {{ users[0].name | upper }}</p>
    {% else %}
        <p>详细信息已隐藏</p>
    {% endif %}

    <h3>活跃用户</h3>
    <ul>
    {% for user in users if user.active %}
        <li>{{ user.name }}</li>
    {% endfor %}
    </ul>
{% endblock %}
```

#### 文件结构
```
项目文件夹/
├── app.py
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── home.html
    └── users.html
```

#### 运行结果
- 访问 `http://127.0.0.1:5000/`（首页）：
  ```
  欢迎使用 Flask
  首页 | 用户列表
  欢迎来到首页
  这是一个简单的 Flask 应用示例。
  © 2025 Flask 教程
  ```

- 访问 `http://127.0.0.1:5000/users`（用户列表）：
  ```
  欢迎使用 Flask
  首页 | 用户列表
  用户列表
  - Alice (年龄: 25) 活跃
  - Bob (年龄: 30) 不活跃
  - Charlie (年龄: 15) 活跃
  额外信息
  总用户数: 3
  第一个用户: ALICE
  活跃用户
  - Alice
  - Charlie
  © 2025 Flask 教程
  ```

#### 扩展说明
- **保留父模板内容**：如果想在子模板中保留父模板的块内容，可以使用 `{{ super() }}`。例如：
  ```html
  {% block content %}
      {{ super() }}
      <p>追加的内容</p>
  {% endblock %}
  ```
  这会在子模板中保留 `base.html` 的默认内容 `<p>这是默认内容</p>` 并追加新内容。

- **多级继承**：你可以让一个子模板再被其他模板继承，形成多级结构。

---

### 10. 部署（简单说明）

开发完成后，你可能想将应用部署到服务器上。常用方法：
- 使用 `gunicorn`（生产环境 Web 服务器）：
  ```bash
  pip install gunicorn
  gunicorn --bind 0.0.0.0:8000 app:app
  ```
- 配合 Nginx 或其他反向代理服务器。

在本地调试时，`app.run()` 就足够了。

---

### 总结

这是一个 Flask 的基础教程，涵盖了安装、路由、模板、表单和静态文件的使用。你可以根据需求扩展功能，例如连接数据库（如 Flask-SQLAlchemy）、添加用户认证等。如果需要更深入的讲解或特定功能，请告诉我！


## Flask操作数据库

下面是一个使用 Flask 操作数据库的教程，基于 Python 的 Flask 框架和常见的 SQLite 数据库（也可以扩展到其他数据库如 MySQL 或 PostgreSQL）。我会逐步介绍如何设置 Flask 应用、连接数据库、执行 CRUD 操作（创建、读取、更新、删除），并提供示例代码。

---

### Flask 操作数据库教程

Flask 是一个轻量级的 Python Web 框架，结合数据库操作可以快速构建动态网站或 API。本教程将使用 SQLite 作为数据库，因为它是 Python 内置的，无需额外安装。你也可以根据需要替换为其他数据库。

---

### 环境准备

在开始之前，确保你已安装 Python，并准备好以下工具：

1. **安装 Flask**  
   在终端运行以下命令：
   ```bash
   pip install flask
   ```

2. **数据库工具**  
   本教程使用 SQLite，无需额外安装。如果想使用 MySQL 或 PostgreSQL，可以安装对应驱动，例如 `pip install pymysql` 或 `pip install psycopg2`。

3. **项目结构**  
   创建一个项目文件夹，结构如下：
   ```
   flask_db_demo/
   ├── app.py
   ├── templates/
   │   └── index.html
   └── database.db  (稍后生成)
   ```

---

### 步骤 1：初始化 Flask 和数据库

创建一个简单的 Flask 应用并连接 SQLite 数据库。

#### 代码示例：app.py

```python
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # 返回字典形式的行数据
    return conn

# 初始化数据库和表
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

# 在应用启动时初始化数据库
init_db()

@app.route('/')
def index():
    return "Hello, Flask with Database!"

if __name__ == '__main__':
    app.run(debug=True)
```

#### 说明
1. **数据库连接**：`get_db_connection()` 函数建立与 SQLite 文件 `database.db` 的连接。
2. **表创建**：`init_db()` 函数创建一个名为 `users` 的表，包含 `id`、`name` 和 `email` 字段。
3. **启动应用**：运行 `python app.py`，访问 `http://127.0.0.1:5000/` 查看结果。

---

### 步骤 2：实现 CRUD 操作

接下来，我们将实现数据库的增删改查功能，并通过网页展示。

#### 1. 创建（Create）数据

添加一个路由，允许用户通过表单提交数据。

##### 修改 app.py
```python
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_user.html')
```

##### 创建 templates/add_user.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>Add User</title>
</head>
<body>
    <h2>Add New User</h2>
    <form method="POST">
        <label>Name:</label><input type="text" name="name" required><br>
        <label>Email:</label><input type="email" name="email" required><br>
        <button type="submit">Add</button>
    </form>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
```

#### 2. 读取（Read）数据

修改首页路由，显示所有用户信息。

##### 修改 app.py
```python
@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('index.html', users=users)
```

##### 创建 templates/index.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>User List</title>
</head>
<body>
    <h2>User List</h2>
    <table border="1">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user['id'] }}</td>
            <td>{{ user['name'] }}</td>
            <td>{{ user['email'] }}</td>
            <td>
                <a href="{{ url_for('edit_user', id=user['id']) }}">Edit</a> |
                <a href="{{ url_for('delete_user', id=user['id']) }}" onclick="return confirm('Are you sure?')">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <a href="{{ url_for('add_user') }}">Add New User</a>
</body>
</html>
```

#### 3. 更新（Update）数据

添加编辑用户的路由和页面。

##### 修改 app.py
```python
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)
```

##### 创建 templates/edit_user.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>Edit User</title>
</head>
<body>
    <h2>Edit User</h2>
    <form method="POST">
        <label>Name:</label><input type="text" name="name" value="{{ user['name'] }}" required><br>
        <label>Email:</label><input type="email" name="email" value="{{ user['email'] }}" required><br>
        <button type="submit">Update</button>
    </form>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
```

#### 4. 删除（Delete）数据

添加删除用户的路由。

##### 修改 app.py
```python
@app.route('/delete/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
```

---

### 步骤 3：运行和测试

1. 保存所有文件。
2. 在终端运行 `python app.py`。
3. 打开浏览器访问 `http://127.0.0.1:5000/`。
4. 测试添加、编辑、删除用户功能。

---

### 注意事项

1. **安全性**  
   - 当前示例未处理表单验证和 SQL 注入防护（已使用参数化查询避免基本注入）。
   - 生产环境中建议使用 Flask-WTF 和 CSRF 保护。

2. **扩展性**  
   - 可替换 SQLite 为 MySQL 或 PostgreSQL，只需修改连接字符串和驱动。
   - 推荐使用 ORM（如 SQLAlchemy）简化数据库操作。

3. **调试**  
   - `app.run(debug=True)` 仅用于开发，生产环境需使用 WSGI 服务器（如 Gunicorn）。

---

### 总结

通过本教程，你学会了如何在 Flask 中连接 SQLite 数据库并实现基本的 CRUD 操作。你可以根据需求扩展功能，例如添加用户认证、分页或 API 接口。如果有疑问，欢迎提问！