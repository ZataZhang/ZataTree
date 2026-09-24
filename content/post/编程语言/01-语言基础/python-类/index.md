---
title: python-类-类变量和实例变量
description: python语法-类-类变量和实例变量
date: 2025-02-24
slug: 类 ## 必填，文件夹名
image: images/index/index.png
categories:
    - 编程语言
tags:
    - 语言基础
    - python
---


<!-- ![alt text](images/index/index.png) -->

在 Python 中，类的变量可以分为**类变量**和**实例变量**。它们的定义方式和使用场景有所不同。以下是详细的说明：

---

### 1. **类变量**
类变量是属于类本身的变量，所有该类的实例共享同一个类变量。它通常直接定义在类的内部，但在 `__init__` 方法之外。

#### 定义方式：
```python
class MyClass:
    class_variable = "I am a class variable"

    def __init__(self, instance_variable):
        self.instance_variable = instance_variable
```

#### 特点：
- 类变量可以通过类名直接访问，也可以通过实例访问。
- 如果通过实例修改类变量，实际上是为该实例创建了一个同名的实例变量，而不会影响类变量本身。

#### 示例：
```python
# 访问类变量
print(MyClass.class_variable)  # 输出: I am a class variable

# 实例化对象
obj1 = MyClass("Instance 1")
obj2 = MyClass("Instance 2")

# 通过实例访问类变量
print(obj1.class_variable)  # 输出: I am a class variable
print(obj2.class_variable)  # 输出: I am a class variable

# 修改类变量
MyClass.class_variable = "Modified class variable"
print(obj1.class_variable)  # 输出: Modified class variable
print(obj2.class_variable)  # 输出: Modified class variable

# 注意：通过实例修改类变量
obj1.class_variable = "Modified by obj1"
print(obj1.class_variable)  # 输出: Modified by obj1（这是实例变量）
print(obj2.class_variable)  # 输出: Modified class variable（类变量未变）
```

---

### 2. **实例变量**
实例变量是属于每个实例的变量，不同实例之间的实例变量互不影响。它们通常通过 `__init__` 方法定义，并在实例化时初始化。

#### 定义方式：
```python
class MyClass:
    def __init__(self, instance_variable):
        self.instance_variable = instance_variable
```

#### 特点：
- 实例变量只能通过实例访问，不能通过类名直接访问。
- 每个实例都有自己独立的实例变量。

#### 示例：
```python
# 实例化对象
obj1 = MyClass("Instance 1")
obj2 = MyClass("Instance 2")

# 访问实例变量
print(obj1.instance_variable)  # 输出: Instance 1
print(obj2.instance_variable)  # 输出: Instance 2

# 修改实例变量
obj1.instance_variable = "Modified Instance 1"
print(obj1.instance_variable)  # 输出: Modified Instance 1
print(obj2.instance_variable)  # 输出: Instance 2（不受影响）
```

---

### 3. **总结与建议**
- **类变量**：如果某个变量是所有实例共享的，或者需要在类级别上进行管理（如计数器、配置信息等），可以直接定义在类中。
- **实例变量**：如果某个变量是每个实例独有的，应该通过 `__init__` 方法定义。

#### 示例结合类变量和实例变量：
```python
class Car:
    # 类变量
    total_cars = 0

    def __init__(self, brand, model):
        # 实例变量
        self.brand = brand
        self.model = model
        # 更新类变量
        Car.total_cars += 1

    @classmethod
    def get_total_cars(cls):
        return cls.total_cars

# 创建实例
car1 = Car("Toyota", "Corolla")
car2 = Car("Honda", "Civic")

# 访问实例变量
print(car1.brand, car1.model)  # 输出: Toyota Corolla
print(car2.brand, car2.model)  # 输出: Honda Civic

# 访问类变量
print(Car.get_total_cars())  # 输出: 2
```

---

### 4. **注意事项**
- 不要在 `__init__` 方法中定义类变量，因为这样会导致逻辑混乱，容易误以为它是实例变量。
- 如果需要动态地为类添加变量，可以使用 `setattr` 或直接操作类的 `__dict__` 属性，但这通常不推荐，除非有特殊需求。
