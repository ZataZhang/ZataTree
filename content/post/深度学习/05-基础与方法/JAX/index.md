---
title: JAX
description: ""
date: 2025-11-14T22:35:11+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - others
---


### JAX 详细介绍

JAX 是一个由 Google 开发的开源 Python 库，主要用于高性能数值计算和大规模机器学习研究。它以 NumPy 为基础，提供了一个熟悉的数组计算 API，同时引入了先进的程序转换机制，如自动微分（autodiff）和即时编译（JIT），使其特别适合加速器环境（如 GPU 和 TPU）。JAX 的设计理念是“可组合的函数转换”，允许开发者轻松地将计算优化为高效的机器码，从而在保持代码简洁性的前提下实现高性能。

#### 历史背景
JAX 的开发源于 Google Brain 团队对高性能计算的需求。最初于 2018 年左右作为内部工具启动，旨在解决 TensorFlow 在研究阶段的灵活性问题。2020 年，JAX 正式开源，并迅速在机器学习社区流行开来。它受到了 NumPy、Autograd 和 XLA（Accelerated Linear Algebra，Google 的编译器后端）的启发。JAX 的目标是桥接研究原型与生产部署的差距，让研究者能用纯 Python 代码快速迭代，而无需切换到低级优化。截至 2025 年，JAX 已演变为一个成熟生态，集成到 Flax（神经网络库）和 Optax（优化器）等工具中，并被广泛用于天体物理、量子计算和强化学习等领域。

#### 核心特性
JAX 的强大之处在于其“函数转换”系统，这些转换可以无缝应用于 NumPy-like 的代码，而无需修改核心逻辑。以下是其主要特性：

| 特性 | 描述 | 示例应用 |
|------|------|----------|
| **NumPy-like API** | 提供 `jax.numpy`（简称 `jnp`）模块，几乎兼容 NumPy 的所有数组操作，便于从 NumPy 迁移。 | 数组创建、线性代数、统计计算。 |
| **自动微分 (autodiff)** | 支持前向/反向模式自动求导，适用于复杂梯度计算。 | 机器学习中的梯度下降优化。 |
| **JIT 编译** | 使用 XLA 后端将 Python 函数编译为高效机器码，支持懒惰求值。 | 加速循环密集型计算，如模拟。 |
| **向量化 (vmap)** | 自动将函数向量化，支持批量处理。 | 处理多维数据，如图像批次。 |
| **并行映射 (pmap)** | 在多设备（如多个 GPU）上并行执行函数。 | 分布式训练。 |
| **多后端支持** | 无缝运行于 CPU、GPU（CUDA/ROCm）和 TPU，无需代码修改。 | 异构计算环境。 |
| **纯函数式设计** | 数组不可变（immutable），避免副作用，确保可预测性。 | 调试和重现性强。 |

这些特性使 JAX 在性能上远超纯 NumPy，尤其在加速器上。

#### 与 NumPy 和 TensorFlow 的比较
JAX 常被视为 NumPy 的“升级版”和 TensorFlow 的“研究友好”替代品。以下是关键区别：

- **与 NumPy 的比较**：
  - **相似点**：JAX 的 API 高度兼容 NumPy（如 `jnp.array()`、`jnp.dot()`），迁移成本低。
  - **区别**：
    | 方面 | NumPy | JAX |
    |------|-------|-----|
    | **数组可变性** | 支持原地修改（in-place）。 | 不可变，必须返回新数组（函数式风格）。 |
    | **性能** | CPU 上高度优化，但无加速器支持。 | CPU 上可能稍慢（因抽象层），但 GPU/TPU 上更快（JIT 优化）。 |
    | **高级功能** | 无自动微分或编译。 | 支持 autodiff、JIT 等转换。 |
  - **适用场景**：NumPy 适合简单脚本；JAX 适合需要梯度或高性能的场景。

- **与 TensorFlow 的比较**：
  - **相似点**：两者都支持自动微分和图优化，TensorFlow 的 Keras 可与 JAX 集成。
  - **区别**：
    | 方面 | TensorFlow | JAX |
    |------|------------|-----|
    | **抽象层** | 高层 API（如 Keras）+ 图模式/急切执行。 | 低层、纯函数式，专注于核心计算。 |
    | **灵活性** | 研究时需切换模式，部署复杂。 | 统一风格，易于原型到生产。 |
    | **性能** | 内置优化，但自定义扩展难。 | 通过转换实现极致优化，支持自定义后端。 |
    | **学习曲线** | 更完整框架，适合生产。 | 更轻量，适合研究（如结合 Flax）。 |
  - **适用场景**：TensorFlow 适合端到端应用；JAX 更适合实验性 ML 研究，常与 PyTorch-like 库（如 Flax）结合。

总体上，JAX 强调“编写一次，到处运行”，而 NumPy/TensorFlow 更侧重通用性或生产部署。

#### 安装指南
JAX 的安装简单，通过 pip 完成。基本命令：
```
pip install --upgrade jax jaxlib
```
- **CPU 版**：上述命令即可。
- **GPU 版**（CUDA）：`pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html`（替换 cuda12 为你的 CUDA 版本，如 11 或 12）。
- **TPU 版**：需 Google Cloud 环境，参考官方文档。
安装后，验证：`import jax; print(jax.devices())`（显示可用设备）。

#### 基本使用示例
以下是简单示例，展示核心功能。假设已安装 JAX。

1. **基本数组操作**（NumPy 风格）：
   ```python
   import jax.numpy as jnp

   x = jnp.array([1.0, 2.0, 3.0])
   y = jnp.sin(x) + jnp.dot(x, x)
   print(y)  # 输出: [1.84147098 3.90929337 9.83602988]
   ```

2. **自动微分**：
   ```python
   from jax import grad

   def f(x):
       return jnp.sin(x) ** 2

   df_dx = grad(f)(1.0)  # 计算 f 在 x=1.0 处的导数
   print(df_dx)  # 输出: 0.6823278（约值）
   ```

3. **JIT 编译**（加速）：
   ```python
   from jax import jit

   @jit
   def fast_f(x):
       return jnp.dot(x, x) + jnp.sin(x)

   x = jnp.arange(1000000.0)
   result = fast_f(x)  # 首次运行编译，后续高速
   ```

4. **向量化**（处理批量）：
   ```python
   from jax import vmap

   def single_loss(params, x, y):
       return jnp.sum((jnp.dot(x, params) - y) ** 2)

   batched_loss = vmap(single_loss, in_axes=(None, 0, 0))  # 向量化第二个和第三个参数
   # 可用于批量数据训练
   ```

这些示例展示了 JAX 的简洁性。

#### 生态系统与应用
JAX 的生态丰富，包括：
- **Flax/Equinox**：构建神经网络。
- **Optax**：优化器集合。
- **Haiku**：TensorFlow-like 模块化。
应用领域：深度学习、天体模拟（jaxoplanet）、量子计算（QuTiP 集成）和生成模型。 截至 2025 年，JAX 在学术会议（如 NeurIPS）中频繁出现，并被 Meta 和 OpenAI 等公司采用。

#### 总结
JAX 是现代 ML 研究者的利器，它结合了 NumPy 的易用性和 TensorFlow 的高性能，同时提供无与伦比的灵活性。如果你从事数值计算或 AI 原型开发，强烈推荐从官方文档（https://jax.readthedocs.io）入手。JAX 的未来在于进一步优化多模态 AI 和分布式系统，值得持续关注。