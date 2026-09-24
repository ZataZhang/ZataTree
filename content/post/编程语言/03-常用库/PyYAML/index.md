---
title: PyYAML
description: PyYAML的常用操作
date: 2025-02-24
image: images/index/index.png
slug: PyYAML
# image: helena-hertz-wWZzXlDpMog-unsplash.jpg
categories:
    - Library
---


`PyYAML` 是一个用于处理 YAML 文件的 Python 库。YAML 是一种人类可读的数据序列化格式，常用于配置文件、数据交换等场景。`PyYAML` 提供了将 YAML 数据与 Python 对象之间进行转换的功能。

以下是 `PyYAML` 的一些常用代码示例：

### 1. 安装 PyYAML
首先，你需要安装 `PyYAML` 库。可以通过以下命令安装：

```bash
pip install pyyaml
```

### 2. 加载 YAML 文件并解析为 Python 对象

假设你有一个名为 `config.yaml` 的 YAML 文件，内容如下：

```yaml
name: John Doe
age: 30
address:
  street: 123 Main St
  city: Anytown
  country: USA
hobbies:
  - Reading
  - Hiking
  - Coding
```

你可以使用 `yaml.load()` 或 `yaml.safe_load()` 来加载这个文件并将其解析为 Python 对象。

```python
import yaml

# 打开并读取 YAML 文件
with open('config.yaml', 'r') as file:
    data = yaml.safe_load(file)

# 访问解析后的 Python 对象
print(data['name'])  # 输出: John Doe
print(data['address']['city'])  # 输出: Anytown
print(data['hobbies'][0])  # 输出: Reading
```

### 3. 将 Python 对象保存为 YAML 文件

你可以使用 `yaml.dump()` 将 Python 对象保存为 YAML 格式的文件。

```python
import yaml

# Python 对象
data = {
    'name': 'Jane Doe',
    'age': 25,
    'address': {
        'street': '456 Elm St',
        'city': 'Othertown',
        'country': 'Canada'
    },
    'hobbies': ['Swimming', 'Cycling']
}

# 将 Python 对象写入 YAML 文件
with open('output.yaml', 'w') as file:
    yaml.dump(data, file, allow_unicode=True)
```

生成的 `output.yaml` 文件内容如下：

```yaml
address:
  city: Othertown
  country: Canada
  street: 456 Elm St
age: 25
hobbies:
- Swimming
- Cycling
name: Jane Doe
```

### 4. 使用 `yaml.load()` 和 `yaml.safe_load()` 的区别

- `yaml.load()`：可以加载任何 YAML 文档，但它可能会执行任意代码（如果 YAML 文件中包含恶意代码），因此不推荐在不信任的输入上使用。
- `yaml.safe_load()`：只加载简单的 YAML 文档，不会执行任意代码，推荐在处理不受信任的输入时使用。

```python
import yaml

# 使用 safe_load 加载 YAML 文件
with open('config.yaml', 'r') as file:
    data = yaml.safe_load(file)

# 使用 load 加载 YAML 文件（不推荐）
with open('config.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)  # FullLoader 更安全
```

### 5. 自定义对象的序列化和反序列化

如果你有自定义的 Python 类，并希望将其序列化为 YAML 或从 YAML 反序列化，你可以通过 `yaml.add_representer()` 和 `yaml.add_constructor()` 来实现。

```python
import yaml

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Person(name={self.name}, age={self.age})"

# 定义如何将 Person 对象转换为 YAML
def person_representer(dumper, data):
    return dumper.represent_mapping('!person', {'name': data.name, 'age': data.age})

# 定义如何从 YAML 转换回 Person 对象
def person_constructor(loader, node):
    value = loader.construct_mapping(node)
    return Person(value['name'], value['age'])

# 注册自定义的 representer 和 constructor
yaml.add_representer(Person, person_representer)
yaml.add_constructor('!person', person_constructor)

# 创建一个 Person 对象
person = Person('Alice', 28)

# 将 Person 对象转换为 YAML 字符串
yaml_str = yaml.dump(person)
print(yaml_str)

# 从 YAML 字符串转换回 Person 对象
loaded_person = yaml.load(yaml_str, Loader=yaml.FullLoader)
print(loaded_person)
```

输出结果：

```yaml
!person
age: 28
name: Alice
```

```python
Person(name=Alice, age=28)
```

### 6. 处理多文档 YAML 文件

YAML 文件可以包含多个文档，每个文档由 `---` 分隔。你可以使用 `yaml.load_all()` 或 `yaml.safe_load_all()` 来加载所有文档。

```yaml
---
name: John Doe
age: 30
---
name: Jane Doe
age: 25
```

```python
import yaml

# 读取包含多个文档的 YAML 文件
with open('multi_doc.yaml', 'r') as file:
    for data in yaml.safe_load_all(file):
        print(data)
```

输出结果：

```python
{'name': 'John Doe', 'age': 30}
{'name': 'Jane Doe', 'age': 25}
```

### 总结

- `yaml.safe_load()`：用于安全地加载 YAML 文件。
- `yaml.dump()`：用于将 Python 对象保存为 YAML 文件。
- `yaml.load_all()` 和 `yaml.safe_load_all()`：用于处理包含多个文档的 YAML 文件。
- 自定义对象的序列化和反序列化可以通过 `yaml.add_representer()` 和 `yaml.add_constructor()` 实现。

这些是 `PyYAML` 的一些常见用法，适合处理配置文件、数据存储等任务。
