---
title: pickle
description: pickle的常用操作
date: 2025-02-23
image: images/index/index.png
slug: pickle
# image: helena-hertz-wWZzXlDpMog-unsplash.jpg
categories:
    - 编程语言
tags:
    - 常用库
---


# pickle
## 常用操作
###   pickle.dump  将对象保存到文件（序列化）

```python
# 定义一个Python对象
data = {"name": "Alice", "age": 25, "scores": [90, 85, 88]}

# 以二进制写模式打开文件
with open("data.pkl", "wb") as file:
    pickle.dump(data, file)  # 将对象写入文件
```


dump参数：
- **`obj`**（必选）：要序列化的Python对象。可以是几乎任何Python对象（如列表、字典、类实例等）。
- **`file`**（必选）：文件对象，必须是以二进制写模式（`wb`）打开的文件，用于写入序列化后的字节流。
- **`protocol`**（可选）：指定使用的序列化协议版本，默认值是 `None`（使用当前的默认协议，通常是 `4` 或更高版本，取决于Python版本）。
  - 可选值：
    - `0`：人类可读的ASCII格式（较老的协议）。
    - `1`：二进制格式，兼容旧版本。
    - `2`：更高效的二进制格式（Python 2.3+）。
    - `3`：支持更多对象类型（Python 3.0+）。
    - `4`：支持大对象和更多特性（Python 3.4+）。
    - `5`：进一步优化，支持缓冲区（Python 3.8+）。
  - 建议：使用默认值或明确指定 `4` 或 `5`，因为它们效率高且功能强大。
- **`fix_imports`**（可选，关键字参数）：布尔值，默认 `True`。如果为 `True`，会在协议 `0` 或 `1` 下修复导入问题（主要用于跨Python 2/3兼容性）。
- **`buffer_callback`**（可选，关键字参数）：Python 3.8+ 新增，一个回调函数，用于处理缓冲区数据（高级用法，通常不常用）。



### 从文件读取对象（反序列化）
```python
# 以二进制读模式打开文件
with open("data.pkl", "rb") as file:
    loaded_data = pickle.load(file)  # 从文件加载对象

print(loaded_data)  # 输出: {'name': 'Alice', 'age': 25, 'scores': [90, 85, 88]}
```


load参数：
- **`file`**（必选）：文件对象，必须是以二进制读模式（`rb`）打开的文件，包含序列化数据。
- **`fix_imports`**（可选，关键字参数）：布尔值，默认 `True`。处理旧协议（`0` 或 `1`）中导入问题（跨Python 2/3兼容性）。
- **`encoding`**（可选，关键字参数）：字符串，默认 `'ASCII'`。指定如何解码旧协议中的字符串（主要用于从Python 2生成的pickle文件中读取）。
  - 常用值：`'ASCII'`、`'latin1'`、`'utf-8'`。
- **`errors`**（可选，关键字参数）：字符串，默认 `'strict'`。指定解码时的错误处理方式。
  - 常用值：`'strict'`（抛出异常）、`'ignore'`（忽略错误）、`'replace'`（替换无效字符）。
- **`buffers`**（可选，关键字参数）：Python 3.8+ 新增，一个可迭代对象，提供外部缓冲区数据（高级用法，通常不常用）。



### 直接序列化为字节（不保存文件）
```python
# 序列化为字节
byte_data = pickle.dumps(data)
print(byte_data)  # 输出字节流

# 从字节反序列化
new_data = pickle.loads(byte_data)
print(new_data)  # 输出: {'name': 'Alice', 'age': 25, 'scores': [90, 85, 88]}
```


序列化为字节对象（不写入文件）。

dumps参数：
- **`obj`**（必选）：要序列化的Python对象。
- **`protocol`**（可选）：与 `dump()` 的 `protocol` 参数相同，默认是 `None`。
- **`fix_imports`**（可选，关键字参数）：布尔值，默认 `True`，功能同上。
- **`buffer_callback`**（可选，关键字参数）：与 `dump()` 中的相同，Python 3.8+ 支持。


loads参数：
- **`bytes_object`**（必选）：要反序列化的字节对象（通常由 `dumps()` 生成）。
- **`fix_imports`**（可选，关键字参数）：布尔值，默认 `True`，功能同上。
- **`encoding`**（可选，关键字参数）：字符串，默认 `'ASCII'`，功能同 `load()`。
- **`errors`**（可选，关键字参数）：字符串，默认 `'strict'`，功能同 `load()`。
- **`buffers`**（可选，关键字参数）：与 `load()` 中的相同，Python 3.8+ 支持。


