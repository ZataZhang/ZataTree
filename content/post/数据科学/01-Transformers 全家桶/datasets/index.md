---
title: datasets
description: ""
date: 2025-03-13T10:38:50+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - transformers
---



---


# Hugging Face Datasets 库基本使用教程

Hugging Face 的 `datasets` 库是一个强大的工具，用于加载、处理和管理数据集，尤其在自然语言处理 (NLP) 任务中非常流行。本教程将结合你的代码，逐步讲解其基本用法。


---

## 1. 环境准备

首先，确保你安装了必要的库：

```bash
pip install datasets transformers
```

然后导入相关模块：

```python
import transformers
from datasets import load_dataset, Dataset, load_from_disk
```

---

## 2. 加载在线数据集

### 2.1 加载完整数据集

可以通过 `load_dataset` 函数直接加载 Hugging Face Hub 上的在线数据集。例如：

```python
datasets = load_dataset("madao33/new-title-chinese")
print(datasets)
```

输出会显示数据集的结构，通常包含 `train`、`validation` 和 `test` 等划分。

### 2.2 加载特定任务数据集

有些数据集是集合（如 `super_glue`），可以指定加载某项任务：

```python
boolq_dataset = load_dataset("super_glue", "boolq")
print(boolq_dataset)
```

### 2.3 按划分加载

可以指定加载某个具体划分（如 `train`）：

```python
dataset = load_dataset("madao33/new-title-chinese", split="train")
print(dataset)
```

还可以加载部分数据：
- 指定范围：`train[10:100]`（第10到100条）
- 指定百分比：`train[:50%]`（前50%）
- 自定义划分：`["train[:50%]", "train[50%:]"]`（分成两部分）

```python
dataset = load_dataset("madao33/new-title-chinese", split="train[:50%]")
print(dataset)
```

---



## 8. 加载本地数据集

### 8.1 加载单个文件

支持多种格式（如 CSV）：

```python
dataset = load_dataset("csv", data_files="./ChnSentiCorp_htl_all.csv", split="train")
print(dataset)
```

或使用 `Dataset.from_csv`：
```python
dataset = Dataset.from_csv("./ChnSentiCorp_htl_all.csv")
```

### 8.2 加载多个文件

加载文件夹内所有文件：

```python
dataset = load_dataset("csv", data_files=["./all_data/file1.csv", "./all_data/file2.csv"], split="train")
```

### 8.3 从 Pandas 转换

```python
import pandas as pd
data = pd.read_csv("./ChnSentiCorp_htl_all.csv")
dataset = Dataset.from_pandas(data)
```

### 8.4 从 List 转换

需要明确字段名：

```python
data = [{"text": "abc"}, {"text": "def"}]
dataset = Dataset.from_list(data)
```

### 8.5 使用自定义脚本

可以编写加载脚本（如 `load_script.py`）加载复杂数据：

```python
dataset = load_dataset("./load_script.py", split="train")
```

---

## 3. 查看数据集

加载数据集后，可以通过以下方法查看数据：

### 3.1 访问具体样本

```python
datasets = load_dataset("madao33/new-title-chinese")
print(datasets["train"][0])  # 第一个样本
print(datasets["train"][:2])  # 前两个样本
```

### 3.2 访问特定字段

```python
print(datasets["train"]["title"][:5])  # 前5个标题
```

### 3.3 查看元信息

```python
print(datasets["train"].column_names)  # 列名
print(datasets["train"].features)      # 数据类型和特征
```

---

## 4. 数据集划分

### 4.1 随机划分

将数据集分为训练集和测试集：

```python
dataset = datasets["train"]
split_dataset = dataset.train_test_split(test_size=0.1)  # 10%作为测试集
print(split_dataset)
```

### 4.2 按标签比例划分

对于分类任务，可以按标签比例划分：

```python
dataset = boolq_dataset["train"]
split_dataset = dataset.train_test_split(test_size=0.1, stratify_by_column="label")
print(split_dataset)
```

---

## 5. 数据选取与过滤

### 5.1 选取

选择特定索引的样本：

```python
selected = datasets["train"].select([0, 1])  # 取第0和第1个样本
print(selected)
```

### 5.2 过滤

根据条件过滤数据：

```python
filter_dataset = datasets["train"].filter(lambda example: "中国" in example["title"])
print(filter_dataset["title"][:5])  # 查看过滤后的前5个标题
```

---

## 6. 数据映射（Map）

`map` 函数可以对数据集的每个样本应用自定义处理。

### 6.1 简单映射

给标题添加前缀：

```python
def add_prefix(example):
    example["title"] = 'Prefix: ' + example["title"]
    return example

prefix_dataset = datasets.map(add_prefix)
print(prefix_dataset["train"][:10]["title"])
```

### 6.2 使用 Tokenizer 预处理

结合 `transformers` 的 `AutoTokenizer` 进行编码：

```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

def preprocess_function(example):
    model_inputs = tokenizer(example["content"], max_length=512, truncation=True)
    labels = tokenizer(example["title"], max_length=32, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

processed_datasets = datasets.map(preprocess_function)
print(processed_datasets)
```

### 6.3 优化映射

- **多线程**：加速处理
```python
processed_datasets = datasets.map(preprocess_function, num_proc=4)
```

- **批量处理**：提高效率
```python
processed_datasets = datasets.map(preprocess_function, batched=True)
```

- **移除原始列**：只保留处理后的字段
```python
processed_datasets = datasets.map(preprocess_function, batched=True, remove_columns=datasets["train"].column_names)
```

remove_columns=datasets["train"].column_names 的作用是告诉 datasets.map 在处理完成后，删除原始数据集中的所有列，只保留 process_function 返回的字段。具体原因如下：   

1. 减少内存占用： 原始列（如 review）可能是长文本，占用大量内存。分词后，input_ids 和 attention_mask 是数值化的表示，通常比原始文本更紧凑。移除原始列可以节省内存，特别是在处理大规模数据集时。
2. 适配模型输入： Hugging Face 的模型（如基于 transformers 的模型）通常只接受特定的输入字段（如 input_ids, attention_mask, token_type_ids, 和 labels）
3. 简化数据结构： 在分词后，原始列（如 review）的作用已经完成，保留它们没有实际意义。移除这些列可以让数据集更简洁，便于调试和后续操作。
---

## 7. 保存与加载

### 7.1 保存到本地

```python
processed_datasets.save_to_disk("./processed_data")
```

### 7.2 从本地加载

```python
processed_datasets = load_from_disk("./processed_data")
print(processed_datasets)
```

---


## 9. 与 DataCollator 结合使用

`DataCollatorWithPadding` 可以动态填充数据，适合 PyTorch 的 `DataLoader`。

### 9.1 数据预处理

```python
from transformers import DataCollatorWithPadding

dataset = load_dataset("csv", data_files="./ChnSentiCorp_htl_all.csv", split="train")
dataset = dataset.filter(lambda x: x["review"] is not None)

def process_function(examples):
    tokenized_examples = tokenizer(examples["review"], max_length=128, truncation=True)
    tokenized_examples["labels"] = examples["label"]
    return tokenized_examples

tokenized_dataset = dataset.map(process_function, batched=True, remove_columns=dataset.column_names)
```

### 9.2 创建 DataLoader

```python
from torch.utils.data import DataLoader

collator = DataCollatorWithPadding(tokenizer=tokenizer)
dl = DataLoader(tokenized_dataset, batch_size=4, collate_fn=collator, shuffle=True)

# 查看前几个批次
num = 0
for batch in dl:
    print(batch["input_ids"].size())  # 动态填充后的输入尺寸
    num += 1
    if num > 10:
        break
```

---

## 总结

通过本教程，你学会了：
1. 加载在线和本地数据集。
2. 查看和操作数据集（划分、选取、过滤）。
3. 使用 `map` 进行数据预处理。
4. 保存和加载处理后的数据集。
5. 将数据集与 PyTorch 的 `DataLoader` 结合使用。

