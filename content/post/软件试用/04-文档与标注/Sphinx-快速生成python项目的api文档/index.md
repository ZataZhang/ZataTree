---
title: Sphinx-快速生成python项目的api文档
description: ""
date: 2025-03-18T00:16:22+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftUseExp
---

<!-- ![alt text](images/index/index.png) -->
---

```bash 
# 初始化一个新的 Sphinx 项目
sphinx-quickstart

# 生成 HTML 文档
make html

# 清空构建目录
make clean

# 生成 PDF 文档（需要安装 LaTeX）
make latexpdf

# 生成单页 HTML 文档
make singlehtml

# 检查 reStructuredText 格式
make rst

# 启动本地服务器预览文档（需安装 sphinx-autobuild）
sphinx-autobuild source build/html

# 生成 API 文档（需配置 sphinx-apidoc）
sphinx-apidoc -o source/ <module_path>

# 构建并检查链接有效性
make linkcheck
```

下面是conf.py文件的参考配置，此外你还需要在index.rst文件的最后一行增加文字即modules

```py
# conf.py 

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('../../src/'))  # 添加src目录到路径


project = 'fainitgleam'
copyright = '2025, zata'
author = 'zata'
release = '1.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    'sphinx.ext.autodoc',      # 自动从docstrings生成文档
    'sphinx.ext.viewcode',     # 添加查看源码的链接
    'sphinx.ext.napoleon',     # 支持Google风格的文档字符串
]

# 配置autodoc扩展
autodoc_member_order = 'bysource'  # 按源码顺序记录成员
add_module_names = False  # 不在API文档中添加模块名

templates_path = ['_templates']
exclude_patterns = []

language = 'zh'


html_theme = 'sphinx_rtd_theme'  # 使用ReadTheDocs主题
html_static_path = ['_static']

```





# Sphinx 使用教程

Sphinx 是一个功能强大的 Python 文档生成工具，广泛用于生成 Python 项目的技术文档、API 文档以及其他类型的文档。它支持 reStructuredText（reST）格式，并可以输出 HTML、PDF、ePub 等多种格式。本教程将详细介绍如何安装、配置和使用 Sphinx 生成专业文档。

---

## 1. 安装 Sphinx

### 1.1 前提条件
- 确保已安装 Python（建议使用 Python 3.6 或更高版本）。
- 安装 `pip`，Python 的包管理工具。

### 1.2 安装 Sphinx
在终端运行以下命令安装 Sphinx：

```bash
pip install sphinx
```

### 1.3 验证安装
安装完成后，检查 Sphinx 是否正确安装：

```bash
sphinx-build --version
```

输出类似 `sphinx-build 4.x.x`，表示安装成功。

### 1.4 可选：安装主题
Sphinx 默认主题较为简单，可以安装更现代化的主题，如 Read the Docs 风格的主题：

```bash
pip install sphinx-rtd-theme
```

---

## 2. 创建 Sphinx 项目

### 2.1 初始化项目
1. 创建一个项目目录（例如 `my-docs`）：
   ```bash
   mkdir my-docs
   cd my-docs
   ```

2. 运行 `sphinx-quickstart` 初始化 Sphinx 项目：
   ```bash
   sphinx-quickstart
   ```

3. 回答交互式问题：
   - **Separate source and build directories**: 推荐选择 `y`，将源文件和构建输出分开。
   - **Project name**: 输入项目名称，例如 `My Project`。
   - **Author name(s)**: 输入作者姓名。
   - **Project release**: 输入版本号，例如 `1.0`。
   - **Language**: 输入文档语言（默认 `en`，中文可输入 `zh_CN`）。

完成后，Sphinx 会生成以下文件结构：
```
my-docs/
├── build/              # 构建输出目录
├── source/             # 源文件目录
│   ├── conf.py        # Sphinx 配置文件
│   ├── index.rst      # 主文档文件
│   └── _static/       # 静态文件（如 CSS、图片）
│   └── _templates/    # 模板文件
└── Makefile           # 用于 Linux/Mac 的构建脚本
└── make.bat           # 用于 Windows 的构建脚本
```

---

## 3. 配置 Sphinx

### 3.1 编辑 `conf.py`
`conf.py` 是 Sphinx 的核心配置文件，位于 `source/` 目录下。以下是一些常用配置项：

- **项目信息**：
  ```python
  project = 'My Project'
  author = 'Your Name'
  release = '1.0'
  ```

- **语言设置**（中文文档）：
  ```python
  language = 'zh_CN'
  ```

- **主题设置**（使用 Read the Docs 主题）：
  ```python
  html_theme = 'sphinx_rtd_theme'
  ```

- **扩展启用**：
  Sphinx 支持多种扩展，常用扩展包括：
  - `sphinx.ext.autodoc`: 自动生成 Python 代码的 API 文档。
  - `sphinx.ext.napoleon`: 支持 Google/Numpy 风格的文档字符串。
  - `sphinx.ext.viewcode`: 显示源代码链接。

  在 `conf.py` 中启用扩展：
  ```python
  extensions = [
      'sphinx.ext.autodoc',
      'sphinx.ext.napoleon',
      'sphinx.ext.viewcode',
  ]
  ```

- **静态文件路径**：
  默认情况下，`_static` 和 `_templates` 路径已配置好，确保不要修改：
  ```python
  html_static_path = ['_static']
  ```

### 3.2 设置中文支持
如果文档使用中文，确保 `language = 'zh_CN'`，并安装支持中文的主题（如 `sphinx-rtd-theme`）。此外，推荐使用 UTF-8 编码保存所有 `.rst` 文件。

---

## 4. 编写文档

Sphinx 使用 reStructuredText（reST）作为默认标记语言，类似于 Markdown 但更适合技术文档。

### 4.1 编辑 `index.rst`
`index.rst` 是文档的入口文件。默认内容如下：

```rst
.. My Project documentation master file

Welcome to My Project's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

- **标题**：使用 `=`、`-`、`~` 等符号创建标题层级。
- **目录树（toctree）**：使用 `.. toctree::` 指令添加子页面，例如：
  ```rst
  .. toctree::
     :maxdepth: 2
     :caption: Contents:

     intro
     api
  ```
  这里 `intro` 和 `api` 对应 `intro.rst` 和 `api.rst` 文件。

### 4.2 创建新页面
在 `source/` 目录下创建新的 `.rst` 文件，例如 `intro.rst`：

```rst
Introduction
============

This is the introduction to My Project.

.. note::
   This is a note directive to highlight important information.
```

将新文件添加到 `index.rst` 的 `toctree` 中。

### 4.3 常用 reST 语法
- **粗体/斜体**：
  ```rst
  **bold text** *italic text*
  ```

- **代码块**：
  ```rst
  .. code-block:: python

     def hello():
         print("Hello, Sphinx!")
  ```

- **链接**：
  ```rst
  `Sphinx 官网 <https://www.sphinx-doc.org>`_
  ```

- **列表**：
  ```rst
  - Item 1
  - Item 2
    - Subitem
  ```

---

## 5. 生成文档

### 5.1 构建 HTML 文档
在项目根目录运行：
```bash
make html
```

- 输出文件将生成在 `build/html/` 目录下。
- 打开 `build/html/index.html` 查看生成的文档。

### 5.2 清理构建
如果需要重新构建，清理旧输出：
```bash
make clean
```

### 5.3 其他格式
Sphinx 支持多种输出格式，例如 PDF（需要安装 `latexmk` 和 TeX 环境）：
```bash
make latexpdf
```

---

## 6. 自动生成 API 文档

如果你的项目包含 Python 代码，可以使用 `sphinx.ext.autodoc` 自动生成 API 文档。

### 6.1 配置 autodoc
确保 `conf.py` 已启用 `sphinx.ext.autodoc` 和 `sphinx.ext.napoleon`。

### 6.2 创建 Python 模块
假设你的项目有一个 Python 模块 `my_module.py`：
```python
def greet(name):
    """Greet someone.

    Args:
        name (str): The name of the person to greet.

    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"
```

### 6.3 生成 API 文档
1. 创建 `api.rst` 文件：
   ```rst
   API Documentation
   =================

   .. automodule:: my_module
      :members:
      :undoc-members:
      :show-inheritance:
   ```

2. 将 `api.rst` 添加到 `index.rst` 的 `toctree`。

3. 确保 `my_module.py` 在 Python 路径中，可以通过修改 `conf.py` 添加模块路径：
   ```python
   import os
   import sys
   sys.path.insert(0, os.path.abspath('../'))
   ```

4. 重新构建文档：
   ```bash
   make html
   ```

---

## 7. 发布文档

### 7.1 本地查看
直接打开 `build/html/index.html` 查看生成的文档。

### 7.2 托管到 Read the Docs
1. 将项目推送到 GitHub/GitLab。
2. 登录 [Read the Docs](https://readthedocs.org/)，导入你的项目。
3. 配置 Read the Docs 自动构建，需在项目根目录添加 `.readthedocs.yml`：
   ```yaml
   version: 2
   build:
     os: ubuntu-22.04
     tools:
       python: "3.10"
   python:
     install:
       - requirements: requirements.txt
   ```

4. 在 `requirements.txt` 中列出依赖：
   ```
   sphinx
   sphinx-rtd-theme
   ```

### 7.3 其他托管方式
- **GitHub Pages**：将 `build/html/` 内容部署到 GitHub Pages。
- **Netlify**：配置 Netlify 自动构建 `make html`。

---

## 8. 实用技巧

### 8.1 自定义主题
在 `_static/` 目录下添加自定义 CSS 文件，并在 `conf.py` 中启用：
```python
html_static_path = ['_static']
html_css_files = ['custom.css']
```

### 8.2 使用 Markdown
如果更习惯 Markdown，可以安装 `myst-parser`：
```bash
pip install myst-parser
```

在 `conf.py` 中启用：
```python
extensions.append('myst_parser')
```

然后可以使用 `.md` 文件代替 `.rst`。

### 8.3 自动构建
使用 `sphinx-autobuild` 实现文档实时预览：
```bash
pip install sphinx-autobuild
sphinx-autobuild source/ build/html/
```

---

## 9. 常见问题

- **Q: 文档没有更新？**
  A: 运行 `make clean` 清理旧构建，然后重新运行 `make html`。

- **Q: 中文显示乱码？**
  A: 确保 `language = 'zh_CN'`，并使用支持中文的主题。

- **Q: 模块未找到？**
  A: 检查 `sys.path` 是否包含模块路径。

---

## 10. 进一步学习
- 官方文档：https://www.sphinx-doc.org
- reStructuredText 入门：http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
- Read the Docs 教程：https://docs.readthedocs.io



## 补充：使用 `sphinx-apidoc` 自动生成 API 文档

Sphinx 提供了 `sphinx-apidoc` 工具，可以自动扫描 Python 项目中的模块、类和函数，生成对应的 reStructuredText（reST）文档框架。以下是详细步骤：

---

### 1. 确保启用必要扩展
在 `source/conf.py` 中确保已启用以下扩展：
```python
extensions = [
    'sphinx.ext.autodoc',    # 自动提取文档字符串
    'sphinx.ext.napoleon',   # 支持 Google/Numpy 风格文档字符串
    'sphinx.ext.viewcode',   # 添加源代码链接
]
```

### 2. 项目结构示例
假设你的 Python 项目结构如下：
```
my-docs/
├── my_project/
│   ├── __init__.py
│   ├── module1.py
│   └── module2/
│       ├── __init__.py
│       └── submodule.py
├── source/
│   ├── conf.py
│   ├── index.rst
│   └── _static/
└── Makefile
```

其中 `module1.py` 包含以下代码：
```python
def greet(name):
    """Greet someone.

    Args:
        name (str): The name of the person to greet.

    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"
```

### 3. 运行 `sphinx-apidoc`
在项目根目录（`my-docs/`）运行以下命令：
```bash
sphinx-apidoc -o source/ my_project/
```

#### 参数说明：
- `-o source/`: 指定生成的 `.rst` 文件输出到 `source/` 目录。
- `my_project/`: 要扫描的 Python 模块或包的路径。
- 可选参数：
  - `-f`: 强制覆盖已存在的 `.rst` 文件。
  - `-M`: 将模块文档放在子模块之前（默认子模块优先）。
  - `-e`: 为每个模块生成单独的页面。
  - `--private`: 包含私有成员（以 `_` 开头的成员）。
  - `--no-toc`: 不生成目录树文件（`modules.rst`）。

示例命令（强制覆盖并包含私有成员）：
```bash
sphinx-apidoc -f -e --private -o source/ my_project/
```

### 4. 检查生成的文件
运行后，`source/` 目录下会生成类似以下文件：
```
source/
├── conf.py
├── index.rst
├── my_project.rst
├── my_project.module1.rst
├── my_project.module2.rst
├── my_project.module2.submodule.rst
└── modules.rst
```

- `my_project.rst` 和 `modules.rst` 是模块的索引文件。
- 每个 `.rst` 文件对应一个模块，包含 `.. automodule::` 指令，自动引用模块中的文档字符串。

### 5. 更新 `index.rst`
将生成的模块索引添加到 `index.rst` 的 `toctree` 中，例如：
```rst
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   intro
```

这里 `modules` 指向 `modules.rst`，它会自动包含所有生成的 API 文档。

### 6. 配置 Python 路径
为了让 Sphinx 找到你的 Python 模块，需在 `conf.py` 中添加模块路径：
```python
import os
import sys
sys.path.insert(0, os.path.abspath('../my_project'))
```

### 7. 构建文档
运行以下命令生成 HTML 文档：
```bash
make html
```

打开 `build/html/index.html`，你将看到自动生成的 API 文档，包含 `module1.py` 中 `greet` 函数的文档字符串。

---

### 8. 实用技巧
- **过滤成员**：在 `.rst` 文件中，可以通过 `:members:`、`:undoc-members:`、`:private-members:` 等控制显示的成员。例如：
  ```rst
  .. automodule:: my_project.module1
     :members:
     :private-members:
     :undoc-members:
     :show-inheritance:
  ```

- **忽略文件**：如果不想为某些模块生成文档，可以在 `sphinx-apidoc` 命令后添加忽略路径：
  ```bash
  sphinx-apidoc -o source/ my_project/ my_project/module2/*
  ```

- **自动化脚本**：将 `sphinx-apidoc` 集成到构建流程中，例如在 `Makefile` 中添加：
  ```makefile
  apidoc:
      sphinx-apidoc -f -o source/ my_project/
  ```

  然后运行 `make apidoc && make html`。

---

### 9. 注意事项
- **文档字符串**：确保你的 Python 代码中有清晰的文档字符串（docstring），否则生成的文档会缺少内容。
- **模块路径**：如果模块未正确导入，检查 `sys.path` 配置。
- **更新文档**：每次修改 Python 代码后，需重新运行 `sphinx-apidoc`（加 `-f` 覆盖）或手动更新 `.rst` 文件。

---

### 10. 进一步优化
- **自定义模板**：在 `source/_templates/` 中创建自定义模板，修改 `sphinx-apidoc` 生成的 `.rst` 文件格式。
- **持续集成**：在 CI/CD 流程中自动运行 `sphinx-apidoc` 和 `make html`，确保文档始终与代码同步。

通过 `sphinx-apidoc`，你可以快速为大型 Python 项目生成 API 文档，大大提高效率！





## 示例项目：一个简单的计算器
假设我们有一个小项目 `calculator`，结构如下：
```
calculator/
├── calc.py        # 主代码文件
└── docs/          # 文档文件夹（稍后创建）
```

### 1. 创建项目代码
先在 `calculator` 文件夹下创建 `calc.py`，内容如下：
```python
"""这是一个简单的计算器模块。"""

def add(a, b):
    """将两个数相加。

    参数:
        a (int): 第一个数
        b (int): 第二个数

    返回:
        int: 两数之和
    """
    return a + b

def subtract(a, b):
    """将两个数相减。

    参数:
        a (int): 被减数
        b (int): 减数

    返回:
        int: 两数之差
    """
    return a - b
```

这个文件有模块级 docstring 和函数级 docstring，Sphinx 可以利用这些生成文档。

---

### 2. 设置 Sphinx
#### 安装 Sphinx
确保你有 Python 环境，然后在终端运行：
```bash
pip install sphinx
```

#### 初始化文档
进入 `calculator` 文件夹，运行：
```bash
mkdir docs
cd docs
sphinx-quickstart
```
系统会问你一些问题，按以下方式回答（其他可以默认回车）：
- `Separate source and build directories (y/n)`：输入 `n`（简单起见，放在一起）。
- `Project name`：输入 `Calculator`。
- `Author name(s)`：输入你的名字，比如 `张三`。
- `Project release`：输入 `1.0`。

完成后，`docs` 文件夹会变成这样：
```
calculator/
├── calc.py
└── docs/
    ├── conf.py       # 配置文件
    ├── index.rst     # 主文档文件
    ├── Makefile      # Linux/Mac 生成工具
    └── make.bat      # Windows 生成工具
```

---

### 3. 配置 Sphinx
#### 修改 `conf.py`
打开 `docs/conf.py`，做两处调整：
1. **添加项目路径**，让 Sphinx 能找到 `calc.py`：
   在文件顶部添加：
   ```python
   import os
   import sys
   sys.path.insert(0, os.path.abspath('..'))  # 指向 calculator 目录
   ```

2. **启用 `autodoc` 扩展**，支持自动生成代码文档：
   找到 `extensions` 列表，改成：
   ```python
   extensions = ['sphinx.ext.autodoc']
   ```

#### 检查 `index.rst`
默认的 `index.rst` 可能是：
```
Welcome to Calculator's documentation!
======================================

.. toctree::
   :maxdepth: 2
```
暂时不用改，后面会加内容。

---

### 4. 自动生成代码文档
#### 用 `sphinx-apidoc`
在 `docs` 目录下运行：
```bash
sphinx-apidoc -o . ..
```
- `-o .`：输出到当前目录（`docs`）。
- `..`：扫描上级目录（`calculator`）。

这会生成：
- `modules.rst`：模块总览。
- `calc.rst`：针对 `calc.py` 的文档。

看看 `calc.rst`，内容大概是：
```
calc
====

.. automodule:: calc
   :members:
   :undoc-members:
   :show-inheritance:
```

#### 整合到 `index.rst`
编辑 `index.rst`，加入模块链接：
```
Welcome to Calculator's documentation!
======================================

这是一个简单的计算器项目，提供加法和减法功能。

.. toctree::
   :maxdepth: 2

   modules
```
这里手动加了句介绍文字，`modules` 指向自动生成的模块文档。

---

### 5. 手动添加使用说明
新建一个文件 `docs/usage.rst`，写点教程：
```
使用说明
========

这是一个计算器的使用方法。

步骤
----
1. 导入模块：
   .. code-block:: python

      from calc import add, subtract

2. 调用函数：
   .. code-block:: python

      print(add(3, 5))      # 输出 8
      print(subtract(10, 2)) # 输出 8
```

然后在 `index.rst` 的 `toctree` 里加一行：
```
.. toctree::
   :maxdepth: 2

   modules
   usage
```

---

### 6. 生成文档
在 `docs` 目录下运行：
```bash
make html  # Linux/Mac
```
或
```bash
make.bat html  # Windows
```

完成后，打开 `docs/_build/html/index.html`，你会看到：
- 首页有欢迎文字和目录。
- 点击 “modules” -> “calc”，显示 `add` 和 `subtract` 的自动文档（从 docstring 生成）。
- 点击 “使用说明”，显示手动写的教程。

---

### 结果预览
网页大概长这样：
- **首页**：
  ```
  Welcome to Calculator's documentation!
  这是一个简单的计算器项目，提供加法和减法功能。
  - modules
  - usage
  ```
- **calc 页面**：
  ```
  calc
  这是一个简单的计算器模块。
  add(a, b)
    将两个数相加。
    参数: a (int) - 第一个数, b (int) - 第二个数
    返回: int - 两数之和
  subtract(a, b)
    将两个数相减。
    ...
  ```
- **usage 页面**：
  ```
  使用说明
  这是一个计算器的使用方法。
  步骤
  1. 导入模块：
     from calc import add, subtract
  2. 调用函数：
     print(add(3, 5))      # 输出 8
     ...
  ```

---

### 总结流程
1. **写代码+注释**：`calc.py` 里加 docstring。
2. **初始化**：`sphinx-quickstart` 创建文档框架。
3. **配置**：改 `conf.py` 加路径和扩展。
4. **自动生成**：用 `sphinx-apidoc` 提取代码文档。
5. **手动补充**：写 `usage.rst` 加说明。
6. **生成网页**：`make html`。

---
