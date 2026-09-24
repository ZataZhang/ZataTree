---
title: 命名实体识别
description: ""
date: 2025-03-13T14:29:48+08:00
image: images/index/index.png
# image: images/index/index.png
categories:
    - DeepLearning
tags:
    - NLP
---


# 基于Transformers的命名实体识别（NER）教程

命名实体识别（NER）是自然语言处理（NLP）中的一项重要任务，目标是从文本中识别出命名实体（如人名、地名、组织名等）并对其进行分类。本教程将使用Hugging Face的`transformers`库，结合一个中文NER数据集（例如“人民日报NER数据集”），实现一个完整的NER模型训练和预测流程。

---

## Step 1: 导入相关包

首先，我们需要导入必要的库和模块：

```python
import evaluate
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification
```

- `evaluate`: 用于加载评估指标，例如`seqeval`，专门用于NER任务的评估。
- `datasets`: Hugging Face提供的数据集管理工具，用于加载和处理数据。
- `transformers`: 核心库，提供预训练模型、分词器和训练工具。

---

## Step 2: 加载数据集

我们需要一个NER数据集。这里以“人民日报NER数据集”为例，您可以在线加载或从本地加载：

```python
# 在线加载（需要联网）
# ner_datasets = load_dataset("peoples_daily_ner", cache_dir="./data")

# 本地加载（无需联网）
from datasets import DatasetDict
ner_datasets = DatasetDict.load_from_disk("ner_data")
print(ner_datasets)
```

输出示例：
```
DatasetDict({
    train: Dataset({...})
    validation: Dataset({...})
    test: Dataset({...})
})
```

### 查看数据集内容
- 查看第一条训练数据：
```python
print(ner_datasets["train"][0])
```
输出示例：
```
{'tokens': ['小', '明', '在', '北', '京', '上', '班'], 'ner_tags': [1, 2, 0, 3, 4, 0, 0]}
```

- 查看特征信息：
```python
print(ner_datasets["train"].features)
```
输出示例：
```
{'tokens': Sequence(feature=Value(dtype='string')),
 'ner_tags': Sequence(feature=ClassLabel(names=['O', 'B-PER', 'I-PER', 'B-LOC', 'I-LOC', ...]))}
```

- 获取标签列表：
```python
label_list = ner_datasets["train"].features["ner_tags"].feature.names
print(label_list)
```
输出示例：
```
['O', 'B-PER', 'I-PER', 'B-LOC', 'I-LOC', ...]
```
这里，`O`表示非实体，`B-`和`I-`分别表示实体的开始和内部（BIO标注格式）。

---

## Step 3: 数据集预处理

NER任务需要将文本分词并对齐标签。由于预训练模型的分词器（如BERT）可能会将一个词拆分成多个子词（subword），我们需要确保标签与分词后的结果对齐。

### 加载分词器
```python
tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-macbert-base")
```

### 测试分词器
对于已经分词好的数据（如`tokens`），需要设置`is_split_into_words=True`：
```python
res = tokenizer(ner_datasets["train"][0]["tokens"], is_split_into_words=True)
print(res)
```
输出示例：
```
{'input_ids': [101, 2207, 6607, 1762, 1266, 7425, 677, 4408, 102], 'token_type_ids': [...], 'attention_mask': [...]}
```

查看`word_ids`（每个token对应的原始词索引）：
```python
print(res.word_ids())
```
输出示例：
```
[None, 0, 1, 2, 3, 4, 5, 6, None]
```
- `None`表示特殊token（如`[CLS]`和`[SEP]`），其他数字对应原始`tokens`的索引。

### 定义预处理函数
我们需要将标签与分词结果对齐：
```python
def process_function(examples):
    tokenized_examples = tokenizer(examples["tokens"], max_length=128, truncation=True, is_split_into_words=True)
    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_examples.word_ids(batch_index=i)
        label_ids = []
        for word_id in word_ids:
            if word_id is None:  # 特殊token用-100标记（会被模型忽略）
                label_ids.append(-100)
            else:
                label_ids.append(label[word_id])  # 对齐原始标签
        labels.append(label_ids)
    tokenized_examples["labels"] = labels
    return tokenized_examples

# 应用到数据集
tokenized_datasets = ner_datasets.map(process_function, batched=True)
print(tokenized_datasets["train"][0])
```

---

## Step 4: 创建模型

加载预训练模型，并指定标签数量：
```python
model = AutoModelForTokenClassification.from_pretrained("hfl/chinese-macbert-base", num_labels=len(label_list))
print(model.config.num_labels)  # 验证标签数量
```

注意：`num_labels`必须与`label_list`长度一致，否则会导致设备错误。

---

## Step 5: 创建评估函数

NER任务通常使用`seqeval`来计算F1分数等指标：

```python
# 安装seqeval（如果未安装）
# !pip install seqeval

# 加载评估模块
seqeval = evaluate.load("seqeval_metric.py")  # 本地加载方式

def eval_metric(pred):
    predictions, labels = pred
    predictions = np.argmax(predictions, axis=-1)

    # 将ID转换为标签，忽略-100
    true_predictions = [[label_list[p] for p, l in zip(pred, label) if l != -100] 
                       for pred, label in zip(predictions, labels)]
    true_labels = [[label_list[l] for p, l in zip(pred, label) if l != -100] 
                   for pred, label in zip(predictions, labels)]

    result = seqeval.compute(predictions=true_predictions, references=true_labels, mode="strict", scheme="IOB2")
    return {"f1": result["overall_f1"]}
```

---

## Step 6: 配置训练参数

```python
args = TrainingArguments(
    output_dir="models_for_ner",
    per_device_train_batch_size=64,
    per_device_eval_batch_size=128,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    metric_for_best_model="f1",
    load_best_model_at_end=True,
    logging_steps=50,
    num_train_epochs=1  # 为了演示设为1，实际可设为3-5
)
```

---

## Step 7: 创建训练器

```python
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    compute_metrics=eval_metric,
    data_collator=DataCollatorForTokenClassification(tokenizer=tokenizer)
)
```

`DataCollatorForTokenClassification`会自动对齐输入和标签，填充到相同长度。

---

## Step 8: 模型训练

```python
trainer.train()
```

训练完成后，评估测试集：
```python
trainer.evaluate(eval_dataset=tokenized_datasets["test"])
```

---

## Step 9: 模型预测

使用`pipeline`进行推理：
```python
from transformers import pipeline

# 设置id2label
model.config.id2label = {idx: label for idx, label in enumerate(label_list)}

# 创建NER pipeline
ner_pipe = pipeline("token-classification", model=model, tokenizer=tokenizer, device=0, aggregation_strategy="simple")

# 预测示例
text = "小明在北京上班"
res = ner_pipe(text)
print(res)
```
输出示例：
```
[{'entity_group': 'PER', 'start': 0, 'end': 2, 'word': '小明'},
 {'entity_group': 'LOC', 'start': 3, 'end': 5, 'word': '北京'}]
```

提取结果：
```python
ner_result = {}
for r in res:
    if r["entity_group"] not in ner_result:
        ner_result[r["entity_group"]] = []
    ner_result[r["entity_group"]].append(text[r["start"]:r["end"]])
print(ner_result)
```
输出示例：
```
{'PER': ['小明'], 'LOC': ['北京']}
```

---

## 总结

通过以上步骤，您已经完成了：
1. 数据加载与预处理
2. 模型创建与训练
3. 评估与预测

