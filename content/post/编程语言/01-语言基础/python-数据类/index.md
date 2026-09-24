---
title: python-数据类
description: ""
date: 2025-03-15T20:43:43+08:00
image: images/index/index.png
categories:
    - Grammar
tags:
    - python
---

<!-- ![alt text](images/index/index.png) -->

在 Python 中，数据类（Data Classes）是通过 `dataclasses` 模块实现的，它在 Python 3.7+ 中引入。数据类是一种简洁的方式，用于创建主要用于存储数据的类，自动生成诸如 `__init__`、`__repr__`、`__eq__` 等特殊方法。结合 `typing` 模块，数据类可以更优雅地定义类型安全的结构体。

以下是关于数据类的使用教程：

---

### 1. **基本概念**
数据类通过装饰器 `@dataclass` 定义，减少样板代码。你只需要声明字段和类型，Python 会自动为你生成构造器和其他方法。

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    height: float

# 创建实例
p = Person("Alice", 25, 1.75)
print(p)  # 输出: Person(name='Alice', age=25, height=1.75)
```

- `name: str` 表示字段 `name` 是字符串类型。
- `@dataclass` 自动生成 `__init__`，所以你可以直接传入参数创建对象。

---

### 2. **导入和基本用法**
需要从 `dataclasses` 模块导入 `dataclass`：

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)       # 输出: Point(x=1, y=2)
print(p1 == p2) # 输出: True（自动生成 __eq__）
```

---

### 3. **默认值**
你可以为字段指定默认值：

```python
@dataclass
class Student:
    name: str
    id: int = 0  # 默认值
    grade: str = "A"

s = Student("Bob")
print(s)  # 输出: Student(name='Bob', id=0, grade='A')
```

> **注意**：带默认值的字段必须放在没有默认值的字段后面（与普通函数参数规则一致）。

---

### 4. **与 `typing` 结合**
数据类可以与 `typing` 模块结合，支持复杂类型。

#### (1) 使用容器类型
```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Team:
    name: str
    members: List[str]
    scores: Dict[str, int]
    leader: Optional[str] = None

t = Team("Alpha", ["Alice", "Bob"], {"Alice": 90, "Bob": 85})
print(t)  # 输出: Team(name='Alpha', members=['Alice', 'Bob'], scores={'Alice': 90, 'Bob': 85}, leader=None)
```

#### (2) 使用 Union 或其他类型
```python
from typing import Union

@dataclass
class Product:
    id: Union[int, str]
    price: float

p = Product("ABC123", 19.99)
print(p)  # 输出: Product(id='ABC123', price=19.99)
```

---

### 5. **不可变数据类**
通过设置 `frozen=True`，可以创建不可变（immutable）的数据类，防止字段被修改。

```python
@dataclass(frozen=True)
class ImmutablePoint:
    x: int
    y: int

p = ImmutablePoint(1, 2)
# p.x = 3  # 会抛出 FrozenInstanceError
```

---

### 6. **自定义行为**
#### (1) 添加方法
数据类仍然是普通的类，你可以添加自定义方法：

```python
@dataclass
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height

r = Rectangle(3.0, 4.0)
print(r.area())  # 输出: 12.0
```

#### (2) 自定义 `__post_init__`
如果需要在初始化后执行额外逻辑，可以定义 `__post_init__`：

```python
@dataclass
class Employee:
    name: str
    salary: float
    bonus: float = 0.0

    def __post_init__(self):
        self.total_salary = self.salary + self.bonus

e = Employee("Alice", 50000, 5000)
print(e.total_salary)  # 输出: 55000.0
```

---

### 7. **高级选项**
`@dataclass` 接受一些参数来控制行为：

- `order=True`：生成比较方法（如 `__lt__`, `__gt__`），支持排序。
- `frozen=True`：使对象不可变。
- `init=False`：禁用自动生成 `__init__`。
- `repr=False`：禁用自动生成 `__repr__`。

示例：
```python
@dataclass(order=True)
class Student:
    name: str
    score: int

s1 = Student("Alice", 90)
s2 = Student("Bob", 85)
print(s1 > s2)  # 输出: True（基于字段顺序比较）
```

---

### 8. **与类型检查工具结合**
数据类与 `mypy` 配合使用时，可以检测类型错误：

```python
@dataclass
class Book:
    title: str
    pages: int

b = Book("Python Guide", "300")  # 类型错误：pages 应为 int
```
运行 `mypy script.py` 会报错。

---

### 9. **与普通类的对比**
普通类：
```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Person(name={self.name}, age={self.age})"

    def __eq__(self, other):
        if isinstance(other, Person):
            return self.name == other.name and self.age == other.age
        return False
```

数据类：
```python
@dataclass
class Person:
    name: str
    age: int
```

数据类自动生成上述方法，代码更简洁。

---

### 10. **完整示例**
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Course:
    title: str
    students: List[str]
    credits: int = 3
    instructor: Optional[str] = None

    def add_student(self, student: str) -> None:
        self.students.append(student)

c = Course("Python 101", ["Alice", "Bob"])
c.add_student("Charlie")
print(c)  # 输出: Course(title='Python 101', students=['Alice', 'Bob', 'Charlie'], credits=3, instructor=None)
```

---

### 11. **注意事项**
- 数据类适用于简单的、主要用于存储数据的类。如果逻辑复杂，建议使用普通类。
- 类型注解是可选的，但推荐使用以提高可读性和工具支持。
- 默认值必须是不可变对象（如 `int`, `str`），避免使用 `list` 或 `dict` 作为默认值（可以用 `field` 解决，见下文）。

#### 使用 `field` 指定默认工厂
```python
from dataclasses import dataclass, field

@dataclass
class Inventory:
    items: List[str] = field(default_factory=list)  # 使用工厂函数创建默认值

i = Inventory()
i.items.append("apple")
print(i)  # 输出: Inventory(items=['apple'])
```

---

希望这个教程能帮你掌握数据类的用法！如果有更多问题或需要具体示例，请随时告诉我。