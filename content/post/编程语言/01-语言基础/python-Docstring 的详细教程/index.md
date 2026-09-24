---
title: Python-Docstring 的详细教程
description: ""
date: 2025-03-18T11:52:29+08:00
image: images/index/index.png
categories:
    - Grammar
tags:
    - python
---
<!-- ![alt text](images/index/index.png) -->

下面是一个关于 Python 中 **Docstring** 的详细教程，涵盖其定义、作用、格式、常见风格、最佳实践以及如何与工具（如 Sphinx）结合生成文档。我会尽量全面且清晰地讲解。

---

## 什么是 Docstring？

Docstring 是 Python 中的文档字符串（Documentation String），用于为模块、类、函数或方法提供说明。它是一个特殊的字符串，通常写在定义的开头，用三引号 (`"""` 或 `'''`) 包裹。Docstring 的主要作用是：

1. **文档化代码**：为开发者提供函数或类的使用说明。
2. **自动化工具支持**：如 Sphinx、pydoc 等工具可以提取 Docstring 生成 API 文档。
3. **运行时访问**：通过 `__doc__` 属性访问，例如 `print(function.__doc__)`。

**示例：**
```python
def add(a, b):
    """Add two numbers together."""
    return a + b

print(add.__doc__)  # 输出: Add two numbers together.
```

---

## Docstring 的基本规则

根据 Python 的官方规范 **PEP 257**，Docstring 有以下基本要求：

1. **位置**：必须是模块、类、函数定义的第一行语句。
2. **格式**：使用三引号（`"""`），支持多行。
3. **内容**：
   - 单行 Docstring：简短描述，直接写在一行。
   - 多行 Docstring：第一行是摘要，空一行，后续行是详细说明。
4. **缩进**：与代码块对齐。

**单行示例：**
```python
def square(n):
    """Return the square of a number."""
    return n * n
```

**多行示例：**
```python
def divide(a, b):
    """Divide two numbers and return the result.

    This function performs division and handles division by zero.
    """
    return a / b
```

---

## Docstring 的常见风格

不同的项目可能采用不同的 Docstring 风格，以下是三种主流风格的详细说明：

### 1. reStructuredText (reST) 风格
- **特点**：Sphinx 默认支持，常用于生成专业文档。
- **字段**：使用 `:param`、`:return:` 等标记。
- **语法**：基于 reST 标记语言，支持复杂格式。

**示例：**
```python
def multiply(a, b):
    """Multiply two numbers.

    :param float a: The first number to multiply.
    :param float b: The second number to multiply.
    :return: The product of a and b.
    :rtype: float
    :raises TypeError: If inputs are not numbers.
    """
    return a * b
```

**字段说明：**
- `:param <type> <name>:`：描述参数类型和作用。
- `:return:`：描述返回值。
- `:rtype:`：返回值类型。
- `:raises <exception>:`：可能抛出的异常。

---

### 2. Google 风格  （推荐）
- **特点**：简洁直观，易读，需 Sphinx 的 `napoleon` 插件支持。
- **字段**：使用 `Args:`、`Returns:` 等标题。

**示例：**
```python
def subtract(a, b):
    """Subtract b from a.

    Args:
        a (float): The number to subtract from.
        b (float): The number to subtract.

    Returns:
        float: The difference between a and b.

    Raises:
        TypeError: If inputs are not numbers.
    """
    return a - b
```

**字段说明：**
- `Args:`：列出参数，格式为 `name (type): description`。
- `Returns:`：返回值描述，可附带类型。
- `Raises:`：异常描述。

---

### 3. Numpy 风格
- **特点**：结构化强，字段用横线分隔，适合科学计算项目。
- **字段**：使用 `Parameters`、`Returns` 等。

**示例：**
```python
def power(base, exponent):
    """Raise base to the power of exponent.

    Parameters
    ----------
    base : float
        The base number.
    exponent : int
        The exponent to raise the base to.

    Returns
    -------
    float
        The result of base raised to exponent.

    Raises
    ------
    ValueError
        If exponent is negative.
    """
    return base ** exponent
```

**字段说明：**
- `Parameters`：参数列表，每个参数占一行，类型和描述分行。
- `Returns`：返回值描述。
- `Raises`：异常描述。

---

## Docstring 的最佳实践

1. **简洁但完整**：
   - 第一行是简短的摘要（通常不超过一句话）。
   - 详细说明放在后续段落，避免冗长。

2. **描述所有公共接口**：
   - 为所有对外暴露的模块、类、函数写 Docstring。
   - 私有函数（以 `_` 开头）可选择性添加。

3. **参数和返回值**：
   - 列出所有参数的类型、作用，默认值（如有）。
   - 说明返回值的类型和含义。

4. **异常处理**：
   - 如果函数可能抛出异常，必须在 Docstring 中说明。

5. **一致性**：
   - 项目中统一使用一种风格（如 Google 风格），避免混用。

6. **与类型提示结合**：
   - Python 3.5+ 支持类型提示（Type Hints），可以减少 Docstring 中类型描述的重复。

**类型提示示例：**
```python
def greet(name: str) -> str:
    """Greet a person.

    Args:
        name: The name of the person.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"
```

---

## 如何使用 Docstring 生成文档？

### 1. 使用内置工具 pydoc
Python 自带的 `pydoc` 可以直接生成简单的文档：
```bash
python -m pydoc your_module
```
或生成 HTML：
```bash
python -m pydoc -w your_module
```

### 2. 使用 Sphinx（推荐）

|链接|
|---|
|[sphinx使用](../sphinx-快速生成python项目的api文档/)|



Sphinx 是生成专业文档的首选工具，尤其是结合 `autodoc` 扩展。

#### 步骤：
1. **安装 Sphinx**：
   ```bash
   pip install sphinx
   ```

2. **初始化文档**：
   ```bash
   mkdir docs
   cd docs
   sphinx-quickstart
   ```
   按提示配置，生成 `conf.py` 和 `index.rst`。

3. **启用扩展**：
   在 `conf.py` 中添加：
   ```python
   extensions = ['sphinx.ext.autodoc']
   sys.path.insert(0, os.path.abspath('../src'))  # 代码路径
   ```

   如果使用 Google/Numpy 风格，添加：
   ```python
   extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
   ```

4. **编写 `.rst` 文件**：
   在 `index.rst` 中添加：
   ```rst
   .. automodule:: your_module
      :members:
      :undoc-members:
   ```

5. **生成文档**：
   ```bash
   make html  # 或 make.bat html（Windows）
   ```
   打开 `docs/_build/html/index.html` 查看结果。

---

## 常见问题与解答

### Q1：Docstring 和注释有什么区别？
- **Docstring**：用于文档化，写在定义开头，可被工具提取。
- **注释**：用 `#` 写在代码中，仅供开发者阅读，不生成文档。

### Q2：没有 Docstring 会怎样？
- 工具（如 Sphinx）只会提取函数签名，文档内容为空，影响可读性。

### Q3：如何选择风格？
- 小型项目：Google 风格（简单易读）。
- 大型项目或开源：reST（Sphinx 默认）或 Numpy（科学项目）。
- 团队协作：与团队约定一致。

---

## 完整示例

以下是一个综合示例，展示不同风格的 Docstring：

```python
# 文件: math_utils.py
def calculate(a: float, b: float, operation: str = "add") -> float:
    """Perform a mathematical operation on two numbers.

    Google Style:
    Args:
        a (float): The first number.
        b (float): The second number.
        operation (str, optional): The operation to perform. Defaults to "add".

    Returns:
        float: The result of the operation.

    Raises:
        ValueError: If operation is not supported.

    Numpy Style:
    Parameters
    ----------
    a : float
        The first number.
    b : float
        The second number.
    operation : str, optional
        The operation to perform. Defaults to "add".

    Returns
    -------
    float
        The result of the operation.

    Raises
    ------
    ValueError
        If operation is not supported.
    """
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    else:
        raise ValueError("Unsupported operation")
```

运行 Sphinx 后，生成的文档会根据配置解析 Google 或 Numpy 风格。

---