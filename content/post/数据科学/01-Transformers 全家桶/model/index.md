---
title: model
description: ""
date: 2025-03-13T10:36:03+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - transformers
---






# 使用 Hugging Face Transformers 加载与调用预训练模型教程

本教程将介绍如何使用 Hugging Face 的 `transformers` 库加载预训练模型（如 `hfl/rbt3`）、保存模型到本地、以及如何调用模型进行推理。假设你已经安装了 `transformers` 库（可以通过 `pip install transformers` 安装）。


---

## 1. 环境准备

首先，导入必要的模块：

```python
from transformers import AutoConfig, AutoModel, AutoTokenizer
```

- `AutoConfig`: 用于加载模型的配置文件。
- `AutoModel`: 用于加载预训练模型。
- `AutoTokenizer`: 用于加载与模型配套的分词器。

---

## 2. 在线加载模型

Hugging Face 提供了在线加载模型的便捷方式，前提是你有网络连接。

### 示例代码
```python
model = AutoModel.from_pretrained("hfl/rbt3", force_download=True)
```

### 解释
- `"hfl/rbt3"`: 指定要加载的模型名称，这里是 `hfl/rbt3`，一个基于 BERT 的中文预训练模型。
- `force_download=True`: 强制重新下载模型文件，即使本地已有缓存。
- 模型会自动下载到本地缓存目录（通常是 `~/.cache/huggingface/transformers`）。

---

## 3. 下载模型到本地（离线使用）

如果你需要离线使用模型，可以手动下载模型文件。以下是使用 Git 和 Git LFS 的方法：

### 完整克隆模型仓库
```bash
!git clone "https://huggingface.co/hfl/rbt3"
```

### 只下载模型权重文件
```bash
!git lfs clone "https://huggingface.co/hfl/rbt3" --include="*.bin"
```

### 注意事项
- 需要安装 Git 和 Git LFS（大型文件存储扩展）。
- 科学上网可能需要配置代理以访问 Hugging Face。
- 下载后，模型文件会存储在当前目录下的 `rbt3` 文件夹中。

---

## 4. 离线加载模型

假设模型已下载到本地目录 `./rbt3/`，可以用以下方式加载：

```python
model = AutoModel.from_pretrained("rbt3")
```

### 解释
- `"rbt3"`: 如果本地有同名文件夹，Transformers 会优先从本地加载。
- 如果路径不同，可以指定完整路径，例如 `./path/to/rbt3`。

---

## 5. 查看与配置模型参数

模型加载后，可以通过 `config` 查看其配置信息。

### 示例代码
```python
# 加载模型
model = AutoModel.from_pretrained("rbt3")

# 查看模型配置
print(model.config)

# 单独加载配置
config = AutoConfig.from_pretrained("./rbt3/")
print(config)

# 检查特定配置项
print(config.output_attentions)
```

### 解释
- `model.config`: 返回模型的配置对象，包含模型架构、分词器信息等。
- `AutoConfig.from_pretrained`: 可以单独加载配置文件。
- `output_attentions`: 一个布尔值，表示是否输出注意力权重，默认通常为 `False`。

---

## 6. 模型调用

### 6.1 数据准备
使用分词器将文本转换为模型可接受的输入格式。

```python
sen = "弱小的我也有大梦想！"
tokenizer = AutoTokenizer.from_pretrained("rbt3")
inputs = tokenizer(sen, return_tensors="pt")
print(inputs)
```

#### 输出
```
{'input_ids': tensor([[ 101, 2453, 2207, 4638, 2769,  738, 3300, 1920, 3457, 2682, 8013,  102]]), 
 'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]), 
 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])}
```

#### 解释
- `return_tensors="pt"`: 返回 PyTorch 张量格式（也可以用 `"tf"` 返回 TensorFlow 格式）。
- `input_ids`: 分词后的 token ID 序列。
- `attention_mask`: 指示哪些 token 需要被关注（1 表示有效，0 表示填充）。

### 6.2 不带 Model Head 的调用
加载基础模型，获取隐藏状态或注意力输出。

```python
model = AutoModel.from_pretrained("rbt3", output_attentions=True)
output = model(**inputs)
print(output)
print(output.last_hidden_state.size())
print(len(inputs["input_ids"][0]))
```

#### 输出
- `output.last_hidden_state.size()`: `torch.Size([1, 12, 768])`
  - 1: 批次大小（batch size）。
  - 12: 输入序列长度（包括 [CLS] 和 [SEP]）。
  - 768: 隐藏层维度。
- `len(inputs["input_ids"][0])`: 12，与序列长度一致。

#### 解释
- `output_attentions=True`: 输出注意力权重（在 `output.attentions` 中）。
- `last_hidden_state`: 最后一层的隐藏状态，可用于下游任务。

### 6.3 带 Model Head 的调用
加载带分类头的模型，用于特定任务（如序列分类）。

```python
from transformers import AutoModelForSequenceClassification

clz_model = AutoModelForSequenceClassification.from_pretrained("rbt3", num_labels=10)
output = clz_model(**inputs)
print(output)
print(clz_model.config.num_labels)
```

#### 输出
- `output.logits`: 分类的原始分数（logits）。
- `clz_model.config.num_labels`: 10，表示分类类别数。

#### 解释
- `num_labels=10`: 指定分类任务的类别数（默认是 2）。
- 带 Model Head 的模型会在基础模型上添加任务特定层（这里是分类层）。

---

## 7. 总结

通过本教程，你学会了：
1. **在线加载模型**: 使用 `from_pretrained` 从 Hugging Face Hub 下载模型。
2. **离线保存与加载**: 通过 Git 下载模型并在本地使用。
3. **模型配置**: 查看和调整模型参数。
4. **模型调用**: 处理输入文本并获取模型输出（带或不带 Model Head）。


--- 

