---
title: python-typing提高代码可读性
description: ""
date: 2025-03-15T20:34:43+08:00
image: images/index/index.png
categories:
    - Grammar
tags:
    - python
---

||
|---|
|- []()|





## 首先掌握


### typedDict

```python
from typing import TypedDict

# 定义一个 TypedDict
class Person(TypedDict):
    name: str
    age: int
    email: NotRequired[str]  # 可选字段

# 使用这个类型
person: Person = {"name": "Alice", "age": 25}  # 合法
# person = {"name": "Alice"}  # 非法：缺少 'age' 键
# person = {"name": "Alice", "age": "25"}  # 非法：'age' 应该是 int 类型
```
**特点**
1. **固定键**：`TypedDict` 定义的键是固定的，不能随意添加或删除未定义的键。
2. **类型检查**：类型检查工具（如 `mypy`）会验证字典是否符合定义的结构。
3. **继承性**：可以通过继承扩展 `TypedDict`。


### 基本类型注解
```python
from typing import List, Dict, Tuple, Set, Optional, Union

# 基本类型
name: str = "Alice"
age: int = 25
height: float = 1.75
is_student: bool = True

# 容器类型
numbers: List[int] = [1, 2, 3]
scores: Dict[str, int] = {"Alice": 90, "Bob": 85}
point: Tuple[int, int, str] = (10, 20, "origin")
unique_numbers: Set[int] = {1, 2, 3}

# 可选类型和联合类型
middle_name: Optional[str] = None  # 可以是字符串或 None
id: Union[int, str] = 123  # 可以是整数或字符串


# 函数注解
def greet(name: str) -> str:
    return f"Hello, {name}!"

# 类注解
class Point:
    x: int
    y: int
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

# 泛型
from typing import TypeVar
T = TypeVar('T') # 表示任何类型
def identity(item: T) -> T:
    return item
T = TypeVar('T', int, float)
def add(a: T, b: T) -> T:
    return a + b

# 嵌套类型
from typing import List, Dict
def process_data(data: List[Dict[str, int]]) -> List[int]:
    return [item["value"] for item in data]
    
# callable类型
from typing import Callable
def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Any类型
from typing import Any
def print_anything(value: Any) -> None:
    print(value)

# 类型别名
Vector = List[float]
def normalize(vector: Vector) -> Vector:
    return [v / sum(vector) for v in vector]

# 自定义类型
from typing import NewType
UserId = NewType('UserId', int)
```







---


## typing




{{<bilibili BV14Q4y1n7jz>}}



`typing` 模块在 Python 3.5+ 中引入，用于支持类型注解（Type Hints），帮助开发者在代码中声明变量、函数参数和返回值的类型。它主要用于静态类型检查工具（如 mypy）和提高代码可读性，而不是运行时强制类型检查。

以下是逐步讲解：

---

### 1. **基础概念**
类型注解是 Python 中一种可选的语法，用于标注变量或函数的预期类型。它不会影响代码的运行，但可以被工具（如 IDE 或 mypy）用来检测类型错误。

```python
# 没有类型注解
x = 42

# 有类型注解
x: int = 42
```

---

### 2. **导入 `typing` 模块**
`typing` 模块提供了许多工具，用于处理复杂类型（如列表、字典、函数等）。

```python
from typing import List, Dict, Optional, Union
```

---

### 3. **基本类型注解**
Python 的内置类型（如 `int`, `str`, `float`, `bool`）可以直接使用。

```python
name: str = "Alice"
age: int = 25
height: float = 1.75
is_student: bool = True
```

---

### 4. **容器类型**
`typing` 提供了支持泛型（Generic Types）的工具，用于指定容器内的元素类型。

#### (1) `List`
表示列表及其元素类型：
```python
from typing import List

numbers: List[int] = [1, 2, 3]  # 列表中的元素是整数
names: List[str] = ["Alice", "Bob"]
```

#### (2) `Dict`
表示字典及其键值类型：
```python
from typing import Dict

scores: Dict[str, int] = {"Alice": 90, "Bob": 85}  # 键是字符串，值是整数
```

#### (3) `Tuple`
表示元组及其元素类型：
```python
from typing import Tuple

point: Tuple[int, int, str] = (10, 20, "origin")  # 元组有 3 个元素，类型分别是 int, int, str
```

#### (4) `Set`
表示集合及其元素类型：
```python
from typing import Set

unique_numbers: Set[int] = {1, 2, 3}
```

---

### 5. **可选类型和联合类型**
#### (1) `Optional`
表示一个值可以是某种类型或 `None`：
```python
from typing import Optional

middle_name: Optional[str] = None  # 可以是字符串或 None
middle_name = "Marie"  # 合法
```

#### (2) `Union`
表示一个值可以是多种类型之一：
```python
from typing import Union

id: Union[int, str] = 123  # 可以是整数或字符串
id = "ABC123"  # 也合法
```

> **注意**：从 Python 3.10 开始，可以直接使用 `|` 运算符替代 `Union`，例如 `int | str`。

```python
id: int | str = 123  # Python 3.10+
```

---

### 6. **函数类型注解**
函数的参数和返回值也可以添加类型注解。

```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
```

- `a: int` 表示参数 `a` 应为整数。
- `-> int` 表示函数返回值的类型是整数。

#### 可选参数
```python
from typing import Optional

def get_full_name(first: str, last: str, middle: Optional[str] = None) -> str:
    if middle:
        return f"{first} {middle} {last}"
    return f"{first} {last}"
```

---

### 7. **复杂类型**
#### (1) 嵌套类型
```python
from typing import List, Dict

# 列表中的元素是字典
students: List[Dict[str, int]] = [
    {"Alice": 90},
    {"Bob": 85}
]
```

#### (2) `Callable`
表示可调用对象（如函数）的类型：
```python
from typing import Callable

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# 示例用法
def multiply(x: int, y: int) -> int:
    return x * y

result = apply(multiply, 3, 4)  # 返回 12
```

- `Callable[[int, int], int]` 表示一个函数，接受两个 `int` 参数，返回 `int`。

---

### 8. **自定义类型**
可以使用 `TypeAlias` 定义类型别名（Python 3.6+）：
```python
from typing import TypeAlias

Vector: TypeAlias = List[float]

def magnitude(v: Vector) -> float:
    return sum(x * x for x in v) ** 0.5
```

在 Python 3.12+ 中，可以直接用 `type` 关键字：
```python
type Vector = List[float]  # Python 3.12+
```

---

### 9. **Any 类型**
`Any` 表示任意类型，相当于禁用类型检查：
```python
from typing import Any

data: Any = 42  # 可以是任何类型
data = "hello"  # 合法
```

---

### 10. **使用类型检查工具**
类型注解不会在运行时强制执行。要检查类型错误，可以使用 `mypy`：
1. 安装 mypy：
   ```bash
   pip install mypy
   ```
2. 运行检查：
   ```bash
   mypy your_script.py
   ```

示例：
```python
# test.py
def add(a: int, b: int) -> int:
    return a + b

print(add("1", "2"))  # 类型错误
```
运行 `mypy test.py` 会提示参数类型不匹配。

---

### 11. **常见问题**
- **类型注解会影响性能吗？**
  不会，类型注解仅用于静态检查，运行时会被忽略。
- **Python 版本差异？**
  - Python 3.9+ 支持内置类型（如 `list[int]`）代替 `List[int]`。
  - Python 3.10+ 支持 `|` 替代 `Union`。
  - Python 3.12+ 支持 `type` 关键字定义类型别名。

---

### 12. **完整示例**
```python
from typing import List, Dict, Optional, Union

def process_data(
    numbers: List[int],
    info: Dict[str, str],
    flag: Optional[bool] = None
) -> Union[str, int]:
    if flag:
        return sum(numbers)
    return info.get("name", "Unknown")

result = process_data([1, 2, 3], {"name": "Alice"}, True)
print(result)  # 输出 6
```

---

### Annotated

`Annotated` 是 `typing` 模块中的一种高级类型注解工具，引入于 Python 3.9（`typing_extensions` 模块在早期版本支持）。它允许为类型注解附加元数据（metadata），这些元数据可以被工具、库或运行时处理。

 基本语法
```python
from typing import Annotated

 语法：Annotated[类型, 元数据]
x: Annotated[int, "some metadata"] = 42
```

- `Annotated[Type, metadata]`：`Type` 是变量的实际类型，`metadata` 是附加的任意信息（如字符串、对象等）。
- 元数据不会影响运行时行为，仅供静态分析工具或自定义逻辑使用。

 常见用途
1. **提供额外上下文**：
   `Annotated` 可以为类型添加描述信息，供工具解析。例如，指定变量的约束或用途。
   ```python
   from typing import Annotated

    表示年龄必须是正整数
   Age = Annotated[int, "Must be positive"]
   def set_age(age: Age) -> None:
       assert age > 0, "Age must be positive"
       print(f"Age set to {age}")

   set_age(25)   正常
   set_age(-5)   抛出 AssertionError
   ```

2. **与静态类型检查工具结合**：
   工具如 mypy 或 pyright 可以解析 `Annotated` 的元数据，执行特定检查。例如，某些库（如 `pydantic`）利用 `Annotated` 定义字段约束。
   ```python
   from typing import Annotated
   from pydantic import BaseModel, PositiveInt

   class Person(BaseModel):
       age: Annotated[int, PositiveInt]

   person = Person(age=30)   正常
    person = Person(age=-1)   抛出 ValidationError
   ```

3. **运行时元数据处理**：
   开发者可以编写代码解析 `Annotated` 的元数据。例如，检查字段的约束或生成文档。
   ```python
   from typing import Annotated, get_type_hints, get_args, get_origin

   def process_metadata(cls):
       for name, hint in get_type_hints(cls, include_extras=True).items():
           if get_origin(hint) is Annotated:
               type_, *metadata = get_args(hint)
               print(f"Field {name}: Type={type_}, Metadata={metadata}")

   class User:
       name: Annotated[str, "User's full name"]
       id: Annotated[int, "Unique identifier"]

   process_metadata(User)
    输出：
    Field name: Type=<class 'str'>, Metadata=['User's full name']
    Field id: Type=<class 'int'>, Metadata=['Unique identifier']
   ```

4. **与第三方库集成**：
   许多库（如 `pydantic`, `typer`, `fastapi`）使用 `Annotated` 定义额外约束或行为。例如，FastAPI 用它来指定 API 参数的元数据。
   ```python
   from fastapi import FastAPI
   from typing import Annotated
   from pydantic import StringConstraints

   app = FastAPI()

   @app.get("/user/{name}")
   async def get_user(name: Annotated[str, StringConstraints(min_length=3)]):
       return {"name": name}
   ```

 注意事项
- **运行时行为**：`Annotated` 本身不影响运行时逻辑，元数据的处理依赖工具或自定义代码。
- **兼容性**：Python 3.9+ 内置 `Annotated`，早期版本需使用 `typing_extensions`。
- **元数据任意性**：元数据可以是任何对象（字符串、类、函数等），但需要工具或代码明确如何解析。
- **与普通类型注解的区别**：普通类型注解只描述类型，`Annotated` 允许附加额外信息。

 示例：综合使用
```python
from typing import Annotated, get_type_hints, get_args, get_origin

 定义带有元数据的类型
PositiveInt = Annotated[int, "Must be positive"]

def validate_positive(value: PositiveInt) -> None:
    for annotation in get_args(get_type_hints(validate_positive)['value']):
        if annotation == "Must be positive":
            assert value > 0, "Value must be positive"
    print(f"Valid value: {value}")

validate_positive(10)   输出: Valid value: 10
 validate_positive(-1)   抛出 AssertionError
```

 3. 总结
- `typing` 库为 Python 提供类型注解支持，增强代码健壮性和可读性。
- `Annotated` 是 `typing` 的高级工具，用于为类型附加元数据，广泛用于静态检查、运行时验证和第三方库集成。
- 使用 `Annotated` 时，需结合工具（如 mypy、pydantic）或自定义逻辑解析元数据。



### TypedDict

1. `TypedDict` 简介

`TypedDict` 是用于定义具有固定键和特定类型值的字典的类型注解工具。它最初在 `typing` 模块中引入（Python 3.8+），但 `typing_extensions.TypedDict` 提供了向后兼容支持，适用于 Python 3.7 及更早版本。`TypedDict` 允许开发者为字典的键值对指定明确的类型，增强静态类型检查和代码清晰度。

如果你是3.8+的版本，建议直接从typing中导入

与普通 `dict` 类型注解（如 `dict[str, Any]`）不同，`TypedDict` 确保字典有特定键，且每个键对应特定类型的值，适合描述结构化的字典数据（如 JSON 对象）。

 2. `TypedDict` 的基本用法

`TypedDict` 定义一个类，继承自 `dict`，用于指定字典的结构。以下是基本语法和用法：

 基本定义
```python
from typing import TypedDict

 定义一个 TypedDict
class Person(TypedDict):
    name: str
    age: int

 使用
person: Person = {"name": "Alice", "age": 30}   正确
 person = {"name": "Bob", "age": "25"}   mypy 报错：age 类型应为 int
 person = {"name": "Charlie"}   mypy 报错：缺少 age 键
```

- 键名和类型在类定义中指定。
- 静态类型检查工具（如 mypy）会验证字典是否符合 `TypedDict` 定义的结构。

 可选键
使用 `NotRequired`（Python 3.11+ 或 `typing_extensions`）可以标记某些键为可选：
```python
from typing_extensions import TypedDict, NotRequired

class Person(TypedDict):
    name: str
    age: NotRequired[int]   age 是可选的

person: Person = {"name": "Alice"}   正确
person2: Person = {"name": "Bob", "age": 25}   也正确
```

 必需键
默认情况下，所有键都是必需的。可以用 `Required`（Python 3.11+ 或 `typing_extensions`）显式声明：
```python
from typing_extensions import TypedDict, Required

class Person(TypedDict):
    name: Required[str]
    age: NotRequired[int]
```

 3. 与 `Annotated` 结合

`TypedDict` 可以与 `Annotated` 结合，为键值对附加元数据，进一步描述约束或用途。例如：
```python
from typing import Annotated
from typing_extensions import TypedDict

class Person(TypedDict):
    name: Annotated[str, "Full name of the person"]
    age: Annotated[int, "Must be positive"]

 运行时验证元数据
def validate_person(person: Person):
    from typing import get_type_hints, get_args, get_origin
    hints = get_type_hints(Person, include_extras=True)
    for key, hint in hints.items():
        if get_origin(hint) is Annotated:
            _, *metadata = get_args(hint)
            if key == "age" and "Must be positive" in metadata:
                assert person[key] > 0, "Age must be positive"

person: Person = {"name": "Alice", "age": 30}
validate_person(person)   正确
 validate_person({"name": "Bob", "age": -1})   抛出 AssertionError
```

 4. 高级用法

 继承
`TypedDict` 支持继承，允许扩展或重用现有定义：
```python
from typing_extensions import TypedDict

class Person(TypedDict):
    name: str
    age: int

class Employee(Person):
    employee_id: str

employee: Employee = {"name": "Alice", "age": 30, "employee_id": "E123"}   正确
```

 总数控制（Total）
`TypedDict` 支持 `total` 参数（默认为 `True`），控制是否所有键都必须存在：
```python
from typing_extensions import TypedDict

class Person(TypedDict, total=False):
    name: str
    age: int

person: Person = {"name": "Alice"}   正确，age 可选
```

 与第三方库
`TypedDict` 常用于与 `pydantic` 或 `FastAPI` 配合，定义结构化的输入/输出数据：
```python
from typing_extensions import TypedDict
from pydantic import BaseModel

class Person(TypedDict):
    name: str
    age: int

class PersonModel(BaseModel):
    data: Person

person = PersonModel(data={"name": "Alice", "age": 30})   验证通过
```

 5. 注意事项

- **静态检查**：`TypedDict` 主要用于静态类型检查，运行时行为仍为普通字典。
- **兼容性**：Python 3.7 及以下需使用 `typing_extensions.TypedDict`；3.8+ 可用 `typing.TypedDict`。
- **限制**：`TypedDict` 不支持动态键（如任意字符串键），仅限固定键。
- **与 `Annotated` 协同**：`Annotated` 可为 `TypedDict` 的字段添加元数据，增强描述能力。
- **运行时验证**：需手动或借助库（如 `pydantic`）实现元数据或类型的运行时检查。

 6. 总结

- `typing_extensions.TypedDict` 提供了一种类型安全的方式来定义结构化的字典，适合描述固定键值对的数据结构。
- 结合 `Annotated`，可以为字段添加元数据，增强类型注解的表达力。
- 主要用于静态类型检查（如 mypy），也可与运行时验证工具或框架（如 `pydantic`, `FastAPI`）集成。

