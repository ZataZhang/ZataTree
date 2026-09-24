---
title: tokenizer
description: ""
date: 2025-03-13T10:32:29+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - transformers
---


这个教程将逐步解释 Tokenizer 的基本用法，包括加载、分词、索引转换、填充截断、处理批量数据以及 Fast/Slow Tokenizer 的对比。教程将使用中文句子 "弱小的我也有大梦想!" 作为示例。

---





# 示例
```py
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained(
    'bert-base-uncased',    # 预训练模型名称
    do_lower_case=True,     # 是否将文本转换为小写
    max_length=512,         # 最大序列长度
    truncation=True,        # 是否截断超过最大长度的输入
    padding='max_length'    # 填充方式
)
```


常用参数说明：
- `from_pretrained`: 指定预训练模型的名称或路径。
- `do_lower_case`: 是否对输入进行小写处理。
- `max_length`: 指定 tokenized 后的最大长度。
- `truncation`: 是否截断超长序列。
- `padding`: 填充策略（如`True`、`max_length`或`longest`）。


---

```py
# 示例文本
text = "Hello, how are you today?"

# 使用tokenizer处理文本
encoded_input = tokenizer(
    text,                  # 输入文本
    add_special_tokens=True,  # 添加特殊标记，如[CLS]和[SEP]
    max_length=128,        # 最大长度（与初始化一致）
    truncation=True,       # 截断超长部分
    padding='max_length',  # 填充到指定长度
    return_tensors='pt'    # 返回PyTorch张量（可选：'tf'为TensorFlow，None为Python列表）
)

# 输出结果
print(encoded_input)
```

**对文本进行Tokenization**

假设你有一段文本，你可以用`tokenizer`将它转化为模型可以理解的输入格式：

```python
# 示例文本
text = "Hello, how are you today?"

# 使用tokenizer处理文本
encoded_input = tokenizer(
    text,                  # 输入文本
    add_special_tokens=True,  # 添加特殊标记，如[CLS]和[SEP]
    max_length=128,        # 最大长度（与初始化一致）
    truncation=True,       # 截断超长部分
    padding='max_length',  # 填充到指定长度
    return_tensors='pt'    # 返回PyTorch张量（可选：'tf'为TensorFlow，None为Python列表）
)

# 输出结果
print(encoded_input)
```

**输出说明**

运行后，`encoded_input`会是一个字典，包含以下键值：
- `input_ids`: 文本转换为的数字ID序列。
- `token_type_ids`: 用于区分句子对（如果是单句输入，通常全是0）。
- `attention_mask`: 标记哪些位置是真实token（1）哪些是填充（0）。

示例输出可能像这样：
```python
{
    'input_ids': tensor([[ 101, 7592, 1010, 2129, 2024, 2017, 2651, 1029,  102,    0,    0, ...]]),
    'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...]]),
    'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, ...]])
}
```

**解码回文本（可选）**

如果你想检查tokenization的结果，可以用`decode`方法将ID转换回文本：
```python
decoded_text = tokenizer.decode(encoded_input['input_ids'][0], skip_special_tokens=True)
print(decoded_text)  # 输出: "hello how are you today"
```

**处理多段文本**

如果有多段文本（比如一个列表），可以这样处理：
```python
texts = ["Hello, how are you?", "I am fine, thanks!"]

encoded_inputs = tokenizer(
    texts,
    add_special_tokens=True,
    max_length=128,
    truncation=True,
    padding='max_length',
    return_tensors='pt'
)

print(encoded_inputs['input_ids'])  # 两个句子的input_ids
```

**常见使用场景**

- **单句输入**: 如上面的`text`示例。
- **句子对**: 如果是问答或文本分类任务，可以传入两个句子：
  ```python
  encoded_input = tokenizer("Hello, how are you?", "I am fine!", return_tensors='pt')
  ```
- **批量处理**: 处理一个文本列表，用于模型训练或推理。

**灵活调整参数**

在使用时，你可以根据需求调整参数。例如：
- 不需要填充：`padding=False`。
- 不返回张量：`return_tensors=None`。
- 只获取ID：`tokenizer.encode(text)`（简单方法）。







# Tokenizer 使用教程

在这个教程中，我们将学习如何使用 Hugging Face `transformers` 库中的 `AutoTokenizer` 来处理自然语言文本。Tokenizer 是自然语言处理 (NLP) 的核心组件，用于将原始文本转换为模型可以理解的数字表示。我们将以中文句子 **"弱小的我也有大梦想!"** 为例，逐步展示 Tokenizer 的功能。

## 环境准备

首先，确保你已经安装了 `transformers` 库。如果没有安装，可以通过以下命令安装：

```bash
pip install transformers
```

然后，导入必要的库：

```python
from transformers import AutoTokenizer
```

## 示例句子

我们将使用以下句子作为示例：

```python
sen = "弱小的我也有大梦想!"
```

---

## Step 1: 加载与保存 Tokenizer

### 从 Hugging Face 加载 Tokenizer

`AutoTokenizer.from_pretrained` 方法允许我们从 Hugging Face 的模型仓库加载预训练的 Tokenizer。这里我们使用 `"uer/roberta-base-finetuned-dianping-chinese"` 模型的 Tokenizer：

```python
tokenizer = AutoTokenizer.from_pretrained("uer/roberta-base-finetuned-dianping-chinese")
print(tokenizer)
```

输出会显示 Tokenizer 的类型和配置信息。

### 保存 Tokenizer 到本地

可以将加载的 Tokenizer 保存到本地目录：

```python
tokenizer.save_pretrained("./roberta_tokenizer")
```

### 从本地加载 Tokenizer

从本地目录加载保存的 Tokenizer：

```python
tokenizer = AutoTokenizer.from_pretrained("./roberta_tokenizer/")
print(tokenizer)
```

---

## Step 2: 句子分词

Tokenizer 的核心功能是将句子拆分为词或子词单元（tokens）。使用 `tokenize` 方法：

```python
tokens = tokenizer.tokenize(sen)
print(tokens)
```

输出示例：
```
['弱', '小', '的', '我', '也', '有', '大', '梦', '想', '!']
```

这些 tokens 是模型词汇表中的基本单元。

---

## Step 3: 查看词典

Tokenizer 内部维护了一个词汇表（vocab），可以通过以下方式查看：

### 获取词汇表

```python
vocab = tokenizer.vocab
print(vocab)  # 输出词典（键是 token，值是对应的 ID）
```

### 获取词汇表大小

```python
vocab_size = tokenizer.vocab_size
print(vocab_size)  # 输出词汇表中的 token 数量，例如 21128
```

---

## Step 4: 索引转换

在 NLP 中，模型需要将 tokens 转换为数字 ID。我们可以使用以下方法实现转换：

### Tokens 转 ID

```python
ids = tokenizer.convert_tokens_to_ids(tokens)
print(ids)
```

输出示例：
```
[2201, 2207, 4638, 2769, 738, 3300, 1920, 3457, 2682, 106]
```

### ID 转 Tokens

```python
tokens = tokenizer.convert_ids_to_tokens(ids)
print(tokens)
```

输出示例：
```
['弱', '小', '的', '我', '也', '有', '大', '梦', '想', '!']
```

### Tokens 转字符串

```python
str_sen = tokenizer.convert_tokens_to_string(tokens)
print(str_sen)
```

输出示例：
```
弱小的我也有大梦想!
```

---

### 更便捷的方式：编码与解码

#### 编码（字符串 → ID）

```python
ids = tokenizer.encode(sen, add_special_tokens=True)
print(ids)
```

输出示例（包含特殊 token，如 `[CLS]` 和 `[SEP]`）：
```
[101, 2201, 2207, 4638, 2769, 738, 3300, 1920, 3457, 2682, 106, 102]
```

#### 解码（ID → 字符串）

```python
str_sen = tokenizer.decode(ids, skip_special_tokens=False)
print(str_sen)
```

输出示例：
```
[CLS] 弱小的我也有大梦想! [SEP]
```

如果不需要特殊 token，可以设置 `skip_special_tokens=True`。

---

## Step 5: 填充与截断

在处理批量数据时，句子长度可能不同，需要进行填充（padding）或截断（truncation）。

### 填充

将句子填充到指定长度（例如 15）：

```python
ids = tokenizer.encode(sen, padding="max_length", max_length=15)
print(ids)
```

输出示例（0 表示填充）：
```
[101, 2201, 2207, 4638, 2769, 738, 3300, 1920, 3457, 2682, 106, 102, 0, 0, 0]
```

### 截断

将句子截断到指定长度（例如 5）：

```python
ids = tokenizer.encode(sen, max_length=5, truncation=True)
print(ids)
```

输出示例：
```
[101, 2201, 2207, 4638, 102]
```

---

## Step 6: 其他输入部分

模型通常需要额外的输入，例如 `attention_mask` 和 `token_type_ids`。

```python
ids = tokenizer.encode(sen, padding="max_length", max_length=15)
attention_mask = [1 if idx != 0 else 0 for idx in ids]  # 1 表示有效 token，0 表示填充
token_type_ids = [0] * len(ids)  # 用于区分句子对，这里全为 0
print(ids)
print(attention_mask)
print(token_type_ids)
```

输出示例：
```
[101, 2201, 2207, 4638, 2769, 738, 3300, 1920, 3457, 2682, 106, 102, 0, 0, 0]
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

---

## Step 7: 快速调用方式

`encode_plus` 或直接调用 `tokenizer` 可以一次性返回所有输入：

```python
inputs = tokenizer.encode_plus(sen, padding="max_length", max_length=15)
print(inputs)
```

或者更简洁：

```python
inputs = tokenizer(sen, padding="max_length", max_length=15)
print(inputs)
```

输出示例（字典形式）：
```
{'input_ids': [101, 2201, 2207, 4638, 2769, 738, 3300, 1920, 3457, 2682, 106, 102, 0, 0, 0], 'token_type_ids': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'attention_mask': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]}
```

---

## Step 8: 处理批量数据

可以一次性处理多个句子：

```python
sens = ["弱小的我也有大梦想",
        "有梦想谁都了不起",
        "追逐梦想的心，比梦想本身，更可贵"]
res = tokenizer(sens)
print(res)
```

输出示例（字典形式，包含多个句子的编码）。

### 性能对比

#### 单条循环处理

```python
%%time
for i in range(1000):
    tokenizer(sen)
```

#### 批量处理

```python
%%time
res = tokenizer([sen] * 1000)
```

批量处理通常比单条循环更快。

---

## Step 9: Fast vs Slow Tokenizer

Hugging Face 提供了 Fast Tokenizer（基于 Rust）和 Slow Tokenizer（基于 Python），Fast Tokenizer 速度更快且功能更丰富。

### 加载 Fast Tokenizer

```python
fast_tokenizer = AutoTokenizer.from_pretrained("uer/roberta-base-finetuned-dianping-chinese")
print(fast_tokenizer)
```

### 加载 Slow Tokenizer

```python
slow_tokenizer = AutoTokenizer.from_pretrained("uer/roberta-base-finetuned-dianping-chinese", use_fast=False)
print(slow_tokenizer)
```

### 性能对比

#### 单条循环处理

```python
%%time
for i in range(10000):
    fast_tokenizer(sen)
```

```python
%%time
for i in range(10000):
    slow_tokenizer(sen)
```

#### 批量处理

```python
%%time
res = fast_tokenizer([sen] * 10000)
```

```python
%%time
res = slow_tokenizer([sen] * 10000)
```

Fast Tokenizer 通常比 Slow Tokenizer 快得多。

### Fast Tokenizer 的额外功能

Fast Tokenizer 支持返回 token 的字符偏移量：

```python
inputs = fast_tokenizer(sen, return_offsets_mapping=True)
print(inputs)
print(inputs.word_ids())  # 每个 token 对应的单词索引
```

Slow Tokenizer 不支持此功能。

---

## Step 10: 加载特殊 Tokenizer

某些模型（如 ChatGLM 或 Skywork）的 Tokenizer 需要特殊加载方式：

```python
tokenizer = AutoTokenizer.from_pretrained("Skywork/Skywork-13B-base", trust_remote_code=True)
print(tokenizer)
```

保存和加载：

```python
tokenizer.save_pretrained("skywork_tokenizer")
tokenizer = AutoTokenizer.from_pretrained("skywork_tokenizer", trust_remote_code=True)
```

编码与解码：

```python
print(tokenizer.decode(tokenizer.encode(sen)))
```

---

## 总结

通过这个教程，我们学习了如何使用 `AutoTokenizer` 加载、分词、编码、解码、处理批量数据，以及 Fast/Slow Tokenizer 的区别。Tokenizer 是 NLP 任务中不可或缺的工具，掌握其用法将为后续的模型训练和推理奠定基础。


--- 

