---
title: onnx使用教程
description: ""
date: 2025-06-19T10:23:58+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - smallLibrary
---


## ONNX：打通AI模型的“任督二脉”

想象一下，你精心训练了一个深度学习模型，它在你的电脑上用 PyTorch 框架跑得非常出色。现在，你想把它部署到手机App、网页浏览器，甚至是边缘计算设备上。问题来了：这些五花八门的平台和环境，可能并不支持 PyTorch，或者为了追求极致性能，它们有自己偏好的推理引擎。难道要为每个平台都重新训练或用不同的语言重写模型吗？

这正是 **ONNX (Open Neural Network Exchange)** 试图解决的核心痛点。ONNX 就像是人工智能模型领域的“普通话”或“世界语”，它提供了一种开放、中立的格式，让不同框架训练出的模型可以轻松地互相“交流”和“迁移”。

### 什么是 ONNX？

ONNX 的本质是一个**开放的机器学习模型文件格式**。它由微软、亚马逊、Facebook (Meta) 和 IBM 等科技巨头联合开发，并由Linux基金会托管，旨在实现AI模型的互操作性。

你可以将 ONNX 理解为一个“翻译器”和“通用护照”。无论你的模型最初是用 TensorFlow、PyTorch、Keras、Scikit-learn 还是其他主流框架训练的，你都可以将它“翻译”或“导出”为 `.onnx` 格式。这个 `.onnx` 文件包含了模型的网络结构定义和训练好的权重参数。

一旦拥有了 `.onnx` 文件，你就可以在任何支持 ONNX 标准的平台或设备上运行它，这个过程通常借助一个叫做 **ONNX Runtime** 的高性能推理引擎来完成。

### 为什么需要 ONNX？

使用 ONNX 能为你带来诸多好处：

* **框架互操作性 (Interoperability):** 这是其最核心的优势。你可以在你最熟悉、最擅长的框架（如PyTorch）中进行模型的训练和实验，然后将最终模型导出为 ONNX 格式，交付给使用不同技术栈（如C#、Java）的部署团队。
* **硬件加速与性能优化:** ONNX Runtime 针对不同硬件平台（CPU、GPU、FPGA、移动设备芯片等）进行了深度优化。将模型转换为 ONNX 格式后，你可以利用 ONNX Runtime 在目标硬件上获得比原生框架更快的推理速度。
* **简化部署流程:** ONNX 将训练和部署解耦。模型开发者可以专注于算法创新，而部署工程师则可以专注于在各种环境中高效地运行模型，无需关心模型的内部实现细节。
* **模型“长寿”与可复用性:** 随着AI框架的快速迭代，某些框架可能会逐渐被淘汰。将模型保存为 ONNX 格式，可以确保你的模型资产在未来依然可用，不会因为某个特定框架的没落而失效。

### ONNX 核心使用教程

掌握 ONNX 的基本流程可以概括为以下三步：**获取模型 -> 转换模型 -> 部署推理**。

---

#### **第一步：获取或训练一个模型**

这里我们以一个非常经典的图像分类任务为例，使用 PyTorch 框架和预训练的 `ResNet-18` 模型。

```python
import torch
import torchvision

# 加载一个预训练的 ResNet-18 模型
model = torchvision.models.resnet18(pretrained=True)

# 将模型设置为评估模式（这很重要，会关闭 Dropout 和 BatchNorm 的训练行为）
model.eval()

# 创建一个符合模型输入的虚拟（dummy）输入张量
# ResNet-18 需要一个 (batch_size, channels, height, width) 的输入
dummy_input = torch.randn(1, 3, 224, 224)
```

---

#### **第二步：将模型转换为 ONNX 格式**

PyTorch 内置了对 ONNX 导出的原生支持，非常方便。

```python
# 定义输入和输出节点的名称（可选，但推荐）
input_names = [ "actual_input_1" ]
output_names = [ "output_1" ]

# 导出模型
torch.onnx.export(model,               # 你要转换的模型
                  dummy_input,         # 一个虚拟的输入，用于追踪模型的计算图
                  "resnet18.onnx",     # 输出的 ONNX 文件名
                  verbose=True,        # 打印转换过程的详细信息
                  input_names=input_names,
                  output_names=output_names,
                  opset_version=12)    # ONNX 的操作集版本，推荐使用较新的稳定版本
```

执行完上述代码后，你的项目目录下就会生成一个 `resnet18.onnx` 文件。这就是你的模型“护照”。

**如何查看你的 ONNX 模型？**
推荐使用一个非常直观的开源工具 **Netron** ([https://netron.app](https://netron.app))。你可以直接在浏览器中打开这个网址，或者下载它的桌面应用，然后将你的 `.onnx` 文件拖进去，就可以清晰地看到模型的网络结构、输入输出以及每一层的参数。

---

#### **第三步：使用 ONNX Runtime 进行推理**

现在，我们有了 `.onnx` 文件，就可以在任何支持 ONNX Runtime 的环境中使用它了。这里我们继续在 Python 环境下演示如何加载并使用这个模型进行推理。

首先，你需要安装 ONNX Runtime:
```bash
pip install onnxruntime
```

然后，使用以下代码进行推理：

```python
import onnxruntime
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

# 1. 创建一个 ONNX Runtime 的推理会话 (InferenceSession)
ort_session = onnxruntime.InferenceSession("resnet18.onnx")

# 2. 准备输入数据
# 假设我们有一张名为 "cat.jpg" 的图片
img = Image.open("cat.jpg").convert("RGB")

# 3. 对图片进行预处理，使其符合模型输入要求
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
input_tensor = preprocess(img)
input_tensor = input_tensor.unsqueeze(0) # 增加 batch 维度

# 4. 将 PyTorch tensor 转换为 NumPy array
# ONNX Runtime 需要 NumPy 数组作为输入
ort_inputs = {ort_session.get_inputs()[0].name: input_tensor.numpy()}

# 5. 执行推理
ort_outs = ort_session.run(None, ort_inputs)

# 6. 处理输出结果
# ort_outs 是一个列表，我们获取第一个输出
img_out_y = ort_outs[0]

# 找到概率最高的类别索引
predicted_class_idx = np.argmax(img_out_y)

print(f"Predicted class index: {predicted_class_idx}")

# 你可以加载 ImageNet 的类别标签来查看具体的类别名称
# (此处省略加载标签的代码)
```

### 实践中的注意事项

* **动态输入尺寸 (Dynamic Axes):** 在导出 ONNX 模型时，如果你的模型需要处理不同尺寸的输入（例如，不同分辨率的图片或不同长度的文本序列），你可以在 `torch.onnx.export` 函数中通过 `dynamic_axes` 参数来指定。
* **ONNX Opset Version:** `opset_version` (操作集版本) 很重要。它定义了 ONNX 支持的运算符集合。较新的版本支持更多的操作，但也可能需要较新版本的 ONNX Runtime。导出时使用的版本需要与部署时使用的 ONNX Runtime 版本兼容。
* **模型转换的挑战:** 并非所有模型都能被完美转换。一些框架中非常特殊的、自定义的操作可能在 ONNX 中没有对应的标准操作。这时，你可能需要修改模型结构，或者为 ONNX Runtime 实现自定义算子。
* **模型优化:** ONNX 生态系统提供了丰富的工具，可以在转换后对模型进行优化，例如图优化、算子融合和量化（Quantization），以进一步提升性能并减小模型体积，这对于边缘设备部署至关重要。

### 总结

ONNX 已经成为现代 AI 工作流中不可或缺的一环。它打破了框架壁垒，赋予了开发者前所未有的灵活性，让模型的训练、优化和部署可以无缝衔接。无论你是数据科学家、机器学习工程师还是应用开发者，掌握 ONNX 都将极大提升你的工作效率和项目的成功率。从今天起，就开始为你的模型办理这张强大的“世界通行证”吧！