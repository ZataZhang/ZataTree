---
title: trainer
description: ""
date: 2025-03-13T10:45:32+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - transformers
---




# 使用 `Trainer` 进行文本分类的教程

`Trainer` 是 Hugging Face `transformers` 库中一个高级工具，用于简化和加速模型的训练、评估和预测流程。它封装了训练过程中的许多细节，适合快速实现深度学习任务。本教程将以你提供的代码为基础，讲解如何使用 `Trainer` 完成一个中文情感分类任务（基于 `ChnSentiCorp_htl_all.csv` 数据集）。

---

## 1. 准备工作：导入相关包

首先，我们需要导入必要的库和模块：

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import torch
import evaluate
```

- `AutoTokenizer`：用于加载预训练的分词器。
- `AutoModelForSequenceClassification`：加载适用于序列分类任务的预训练模型。
- `Trainer` 和 `TrainingArguments`：核心工具，用于定义训练流程和参数。
- `datasets`：用于加载和处理数据集。
- `evaluate`：用于加载评估指标（如准确率和 F1 分数）。

---

## 2. 加载数据集

我们需要加载用于训练的数据集，这里假设你有一个名为 `ChnSentiCorp_htl_all.csv` 的 CSV 文件，包含 `review`（文本）和 `label`（标签）两列：

```python
dataset = load_dataset("csv", data_files="./ChnSentiCorp_htl_all.csv", split="train")
dataset = dataset.filter(lambda x: x["review"] is not None)
print(dataset)
```

- `load_dataset`：从 CSV 文件加载数据集。
- `filter`：过滤掉 `review` 列为空的样本，确保数据质量。

输出示例：  
```
Dataset({
    features: ['label', 'review'],
    num_rows: 7766
})
```

---

## 3. 划分数据集

将数据集划分为训练集和测试集：

```python
datasets = dataset.train_test_split(test_size=0.1)
print(datasets)
```

- `train_test_split`：按照 9:1 的比例将数据集分为训练集（90%）和测试集（10%）。

输出示例：  
```
DatasetDict({
    train: Dataset({
        features: ['label', 'review'],
        num_rows: 6989
    })
    test: Dataset({
        features: ['label', 'review'],
        num_rows: 777
    })
})
```

---

## 4. 数据集预处理

为了让数据适配模型输入，我们需要对文本进行分词（tokenization）并添加标签：

```python
tokenizer = AutoTokenizer.from_pretrained("hfl/rbt3")

def process_function(examples):
    tokenized_examples = tokenizer(examples["review"], max_length=128, truncation=True)
    tokenized_examples["labels"] = examples["label"]
    return tokenized_examples

tokenized_datasets = datasets.map(process_function, batched=True, remove_columns=datasets["train"].column_names)
print(tokenized_datasets)
```

- `AutoTokenizer.from_pretrained`：加载与预训练模型匹配的分词器（这里是 `hfl/rbt3`）。
- `process_function`：
  - 使用 `tokenizer` 对 `review` 文本进行分词，限制最大长度为 128，并截断超长部分。
  - 将标签列 `label` 重命名为 `labels`（`Trainer` 要求的字段名）。
- `map`：对整个数据集应用预处理函数，`batched=True` 表示批量处理，`remove_columns` 删除原始列，只保留分词后的字段（如 `input_ids`, `attention_mask`, `labels`）。

输出示例：  
```
DatasetDict({
    train: Dataset({
        features: ['input_ids', 'token_type_ids', 'attention_mask', 'labels'],
        num_rows: 6989
    })
    test: Dataset({
        features: ['input_ids', 'token_type_ids', 'attention_mask', 'labels'],
        num_rows: 777
    })
})
```

---

## 5. 创建模型

加载预训练模型并用于序列分类任务：

```python
model = AutoModelForSequenceClassification.from_pretrained("hfl/rbt3")
print(model.config)
```

- `AutoModelForSequenceClassification`：加载适用于分类任务的模型（默认情况下，`hfl/rbt3` 会自动配置为 2 分类任务）。
- `model.config`：查看模型配置，例如类别数量、隐藏层大小等。

输出示例：  
```
RobertaConfig {
  "num_labels": 2,
  "hidden_size": 768,
  ...
}
```

---

## 6. 创建评估函数

定义一个评估函数，用于计算模型在验证集上的表现：

```python
acc_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def eval_metric(eval_predict):
    predictions, labels = eval_predict
    predictions = predictions.argmax(axis=-1)  # 将 logits 转换为预测类别
    acc = acc_metric.compute(predictions=predictions, references=labels)
    f1 = f1_metric.compute(predictions=predictions, references=labels)
    acc.update(f1)  # 合并 accuracy 和 f1 分数
    return acc
```

- `evaluate.load`：加载预定义的评估指标（准确率和 F1 分数）。
- `eval_metric`：接收 `Trainer` 传递的预测结果（`eval_predict`），计算并返回指标。
  - `predictions.argmax`：从 logits 中提取预测类别。
  - `acc.update(f1)`：将 F1 分数添加到结果字典中。

---

## 7. 配置 `TrainingArguments`

`TrainingArguments` 定义了训练过程中的超参数和策略：

```python
train_args = TrainingArguments(
    output_dir="./checkpoints",          # 模型和检查点的保存路径
    per_device_train_batch_size=64,      # 训练时的批量大小
    per_device_eval_batch_size=128,      # 验证时的批量大小
    logging_steps=10,                    # 每 10 步打印一次日志
    evaluation_strategy="epoch",         # 每个 epoch 评估一次
    save_strategy="epoch",               # 每个 epoch 保存一次模型
    save_total_limit=3,                  # 最多保存 3 个检查点
    learning_rate=2e-5,                  # 学习率
    weight_decay=0.01,                   # 权重衰减
    metric_for_best_model="f1",          # 使用 F1 分数选择最佳模型
    load_best_model_at_end=True          # 训练结束后加载最佳模型
)
print(train_args)
```

- 重要参数：
  - `evaluation_strategy` 和 `save_strategy`：控制评估和保存的频率。
  - `metric_for_best_model`：指定用于选择最佳模型的指标。
  - `load_best_model_at_end`：确保训练结束后使用性能最好的模型。

---

## 8. 创建 `Trainer`

将模型、参数和数据集组合成 `Trainer` 对象：

```python
from transformers import DataCollatorWithPadding

trainer = Trainer(
    model=model,
    args=train_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    compute_metrics=eval_metric
)
```

- `DataCollatorWithPadding`：动态填充输入序列到相同长度，优化批量处理效率。
- `Trainer` 参数：
  - `model`：待训练的模型。
  - `args`：训练参数。
  - `train_dataset` 和 `eval_dataset`：训练和验证数据集。
  - `data_collator`：数据整理器。
  - `compute_metrics`：自定义的评估函数。

---

## 9. 模型训练

开始训练模型：

```python
trainer.train()
```

- `trainer.train()`：执行完整的训练循环。
- 训练过程中会：
  - 每 `logging_steps`（10 步）打印损失。
  - 每个 epoch 评估模型并保存检查点。
  - 根据 `metric_for_best_model`（F1 分数）选择最佳模型。

输出示例：  
```
[164/164 01:23, Epoch 3/3]
Epoch  Training Loss  Validation Loss  Accuracy  F1
1      0.3521         0.2914           0.875     0.882
2      0.2456         0.2678           0.890     0.895
3      0.1987         0.2593           0.892     0.899
```

---

## 10. 模型评估

在测试集上评估模型性能：

```python
eval_results = trainer.evaluate(tokenized_datasets["test"])
print(eval_results)
```

- `trainer.evaluate()`：计算并返回测试集上的指标（accuracy 和 F1）。
- 输出示例：  
```
{'eval_loss': 0.2593, 'eval_accuracy': 0.892, 'eval_f1': 0.899, 'eval_runtime': 2.34}
```

---

## 11. 模型预测

对测试集或新输入进行预测：

### 预测整个测试集
```python
predictions = trainer.predict(tokenized_datasets["test"])
print(predictions.metrics)
```

- `trainer.predict()`：返回预测结果，包括 logits、标签和评估指标。

输出示例：  
```
{'test_loss': 0.2593, 'test_accuracy': 0.892, 'test_f1': 0.899}
```

### 预测单个句子
```python
from transformers import pipeline

model.config.id2label = {0: "负向", 1: "正向"}  # 定义标签映射
pipe = pipeline("text-classification", model=model, tokenizer=tokenizer, device=0)
sen = "我觉得不错！"
result = pipe(sen)
print(result)
```

- `pipeline`：快速构建推理管道。
- `id2label`：将数字标签映射为人类可读的标签。
- 输出示例：  
```
[{'label': '正向', 'score': 0.95}]
```

---

## 总结

通过以上步骤，你可以使用 `Trainer` 完成以下任务：
1. 数据加载与预处理。
2. 模型配置与训练。
3. 评估模型性能。
4. 对新数据进行预测。

### `Trainer` 的优点
- **简洁**：无需手动编写训练循环。
- **灵活**：支持自定义评估指标和超参数。
- **高效**：内置优化（如动态填充、多 GPU 支持）。

