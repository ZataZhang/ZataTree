---
title: Alignment-DPOvsPPOvsGRPO
description: ""
date: 2025-11-25T20:51:18+08:00
image: images/index/index.png
categories:
    - DeepLearning
tags:
    - models_and_strategies
---


### GRPO


**GRPO (Group Relative Policy Optimization)** 是一种高效的强化学习（RL）算法，专门用于大型语言模型（LLM）的后训练阶段（Post-training）。

它由 **DeepSeek** 团队在发布 DeepSeekMath 和 DeepSeek-R1（推理模型）时作为核心技术推出。GRPO 的最大创新在于**摒弃了传统 PPO（近端策略优化）中昂贵的“评论家”（Critic / Value Function）模型**，从而极大地降低了训练时的显存占用和计算成本。

以下是关于 GRPO 的详细技术介绍：

-----

### 1\. 核心概念：什么是 GRPO？

  * **全称**：Group Relative Policy Optimization
  * **中文直译**：组相对策略优化
  * **核心思想**：
    在传统的强化学习（如 PPO）中，我们需要一个“评论家”模型来预测当前状态的价值，以计算“优势函数”（Advantage）。
    GRPO 发现，我们可以通过对同一个问题（Prompt）采样**一组（Group）不同的回答，利用这一组回答的平均奖励**作为基准（Baseline），来计算每个回答的相对好坏。这样就不再需要一个额外的神经网络来做“评论家”了。

### 2\. GRPO 的工作原理（算法流程）

GRPO 的训练过程可以简单概括为“**小组赛马，优胜劣汰**”：

1.  **生成（Group Sampling）**：
    对于每一个输入的问题 $q$，模型（Actor）会生成一组 $G$ 个不同的输出 $\{o_1, o_2, ..., o_G\}$。

      * *例如：给模型一道数学题，让它生成 64 种不同的解题过程。*

2.  **打分（Reward Calculation）**：
    使用奖励模型（Reward Model）或规则（如数学题答案是否正确）给这 $G$ 个输出分别打分，得到奖励值 $\{r_1, r_2, ..., r_G\}$。

3.  **计算优势（Advantage Estimation）**：
    这是 GRPO 的精髓。它不依赖外部模型来判断“好坏”，而是计算每个输出在**当前这组输出中**的相对表现。
    公式逻辑简化为：
    $$A_i = \frac{r_i - \text{mean}(R)}{\text{std}(R)}$$

      * $A_i$：第 $i$ 个回答的优势值。
      * $\text{mean}(R)$：这组回答的平均分。
      * 如果一个回答的分数高于平均分，它的优势就是正的（被鼓励）；反之则是负的（被抑制）。

4.  **策略更新（Policy Optimization）**：
    利用计算出的优势值 $A_i$，通过梯度下降更新模型的参数，使其下一次更有可能生成高分回答。同时，GRPO 会在损失函数中加入 **KL 散度（KL Divergence）** 项，防止模型更新步子太大，偏离原始模型（Reference Model）太远，导致训练崩塌。

-----

### 3\. GRPO vs. PPO：关键区别

这是理解 GRPO 价值的最重要部分。PPO 是 ChatGPT 等模型使用的传统方法，而 GRPO 做出了重大简化。

| 特性 | PPO (Proximal Policy Optimization) | GRPO (Group Relative Policy Optimization) |
| :--- | :--- | :--- |
| **模型组件** | 需要 4 个模型：<br>1. Actor (当前策略)<br>2. **Critic (价值网络)**<br>3. Ref (参考模型)<br>4. Reward (奖励模型) | 只需要 3 个模型：<br>1. Actor (当前策略)<br>2. Ref (参考模型)<br>3. Reward (奖励模型)<br>**❌ 移除了 Critic** |
| **显存占用** | **极高**。Critic 模型通常和 Actor 一样大，训练时需要加载两个巨型模型。 | **较低**。节省了 Critic 模型的显存，通常能节省 30%-50% 的资源。 |
| **计算优势的方式** | 依赖 Critic 模型预测的“价值”来计算 GAE (Generalized Advantage Estimation)。 | 依赖**组内平均分**（Group Mean）作为基准。 |
| **计算复杂度** | 高，需要前向和反向传播 Critic 网络。 | 低，仅涉及简单的统计计算。 |

### 4\. GRPO 的核心优势

1.  **大幅降低训练成本**：
    由于不需要训练和推理那个和 LLM 一样大的 Critic 模型，显存需求大幅下降。这意味着在同样的硬件上，你可以训练参数量更大的模型，或者使用更大的 Batch Size。

2.  **更适合“推理”任务**：
    DeepSeek-R1 的成功证明了 GRPO 非常适合数学、代码等逻辑推理任务。在这些任务中，通过多次采样（生成多种解法）来寻找正确路径是一种非常自然的学习方式。

3.  **训练稳定性**：
    虽然移除了 Critic，但 GRPO 通过组内归一化（Group Normalization）和 KL 惩罚项，依然保持了非常稳定的训练过程，不仅没有损失效果，在数学推理榜单（如 GSM8K, MATH）上甚至超越了传统 PPO。

### 5\. 总结

**GRPO 是强化学习在 LLM 时代的一次“减法”革命。**

它证明了在拥有强大基础模型（Base Model）的前提下，我们不需要复杂的价值网络来指导模型，只需要让模型“自己和自己比”（在一组生成结果中比较），就能高效地进化出强大的推理能力。这也是 DeepSeek 系列模型能够以较低成本取得高性能的关键技术之一。


---

分割线
2025-11-26

---



DPO (Direct Preference Optimization) 和 PPO (Proximal Policy Optimization) 是目前大语言模型（LLM）**对齐（Alignment）** 阶段最主流的两种算法。它们的核心目标都是让模型的输出符合人类的偏好（即 RLHF - Reinforcement Learning from Human Feedback）。

简单来说：**PPO 是经典的“学院派”方法（OpenAI 早期使用），而 DPO 是高效的“实战派”新贵（目前开源界更流行）。**

以下是两者的详细介绍和对比：

---

### 一、 PPO (Proximal Policy Optimization)
**全称：近端策略优化**

PPO 是在 ChatGPT 早期训练中成名的方法。它是一种标准的强化学习（RL）算法。

#### 1. 核心原理
PPO 的核心思想是：**在优化策略（Policy）以获得更高奖励的同时，限制新策略与旧策略之间的差异，防止模型“学歪”或训练崩溃。**

在 LLM 的 RLHF 流程中，PPO 通常包含以下三个阶段：
1.  **SFT (Supervised Fine-Tuning)：** 先用高质量指令数据微调模型，得到基座模型。
2.  **RM (Reward Model Training)：** 训练一个奖励模型（Critic），它能给 LLM 的回复打分（模仿人类的偏好）。
3.  **RL (PPO)：** 利用 RM 的打分作为奖励信号，通过 PPO 算法更新 LLM 的参数。

#### 2. 训练时的“四个模型”
PPO 的工程实现非常复杂，因为它在训练显存中通常需要维护 **4 个模型**：
* **Actor (策略模型)：** 正在训练的 LLM，负责生成文本。
* **Critic (价值模型)：** 估计当前状态的价值（通常由 RM 初始化）。
* **Ref Model (参考模型)：** 冻结权重的 SFT 模型，用于计算 KL 散度（防止 Actor 跑偏）。
* **Reward Model (奖励模型)：** 冻结权重，用于给 Actor 的输出打分。

#### 3. 优缺点
* **优点：**
    * **理论上限高：** 在数据极其丰富、算力充足的情况下，PPO 往往能探索出更好的解。
    * **在线生成：** 它在训练中会不断生成新的样本（Sampling），能够探索未见过的空间。
* **缺点：**
    * **极其耗费资源：** 需要同时加载多个模型，显存占用巨大。
    * **训练极不稳定：** 超参数极其敏感（学习率、KL 系数等），容易出现 reward hacking（模型为了高分输出乱码）或训练发散。
    * **速度慢：** 因为涉及到在线采样（Generation）过程，训练吞吐量低。

---

### 二、 DPO (Direct Preference Optimization)
**全称：直接偏好优化**

DPO 是斯坦福大学在 2023 年提出的算法。它颠覆了 RLHF 必须包含“奖励模型”和“强化学习”的传统范式。

#### 1. 核心原理
DPO 的核心洞见是：**我们不需要显式地训练一个奖励模型（Reward Model）。**

数学推导证明，最优的策略（Policy）和最优的奖励函数之间存在直接的映射关系。DPO 将 RLHF 问题转化为了一个简单的 **二分类损失函数（Classification Loss）** 问题。

DPO 不需要让模型在训练时生成文本，而是直接使用偏好数据对 $(x, y_w, y_l)$ 进行训练（$x$ 是提示，$y_w$ 是胜出的回复，$y_l$ 是失败的回复）。

#### 2. 训练流程
DPO 省略了 RM 的训练步骤，直接优化 Policy：
* **公式直觉：** 增加模型生成“好回复”($y_w$) 的概率，同时降低生成“坏回复”($y_l$) 的概率。
* **参考模型：** 训练时只需要加载 **2 个模型**（正在训练的 Policy Model 和冻结的 Reference Model）。

#### 3. 优缺点
* **优点：**
    * **实现简单：** 代码实现类似传统的监督学习（Cross Entropy），无需复杂的 RL 循环。
    * **显存占用低：** 不需要 Critic 和独立的 Reward Model。
    * **训练稳定：** 不容易发散，超参数较少。
    * **速度快：** 没有推理采样阶段，训练速度大幅提升。
* **缺点：**
    * **容易过拟合：** 对偏好数据的质量非常敏感。如果数据中有噪声，DPO 会迅速拟合这些噪声。
    * **分布外泛化能力：** 有研究指出，在处理完全没见过的 Prompt 时，PPO 可能比 DPO 稍好（存在争议）。

---

### 三、 PPO vs. DPO 核心对比表

| 特性 | PPO (Proximal Policy Optimization) | DPO (Direct Preference Optimization) |
| :--- | :--- | :--- |
| **本质** | 强化学习 (RL) | 监督学习 / 优化方法 |
| **显存需求** | **极高** (需加载 Actor, Critic, Ref, RM) | **较低** (只需 Policy, Ref) |
| **训练流程** | 复杂 (采样 -> 打分 -> 更新 -> 循环) | 简单 (直接在偏好数据上计算 Loss) |
| **稳定性** | **差** (对超参极度敏感，调试困难) | **好** (类似 SFT 的稳定性) |
| **数据要求** | 需要 Reward Model 训练数据 + Unlabeled Prompts | 需要成对的偏好数据 $(y_w, y_l)$ |
| **主要风险** | Reward Hacking (钻空子刷分) | Overfitting (过拟合差数据) |
| **工业界现状** | OpenAI (GPT-4), Anthropic 早期使用 | Llama 3, Zephyr, Qwen 等开源模型主流选择 |

---

### 四、 为什么现在开源界主要用 DPO？

虽然 PPO 在理论上可能探索能力更强，但在实际的开源大模型开发（如 Llama 3 的微调、Qwen 的对齐）中，**DPO 及其变体（如 IPO, KTO）已经占据了统治地位**。原因如下：

1.  **算力就是金钱：** PPO 需要的显存和时间是 DPO 的数倍。对于大多数团队，用 PPO 训练一个 70B 的模型成本过高。
2.  **效果足够好：** 实验表明，在大多数公开基准测试中，DPO 的效果与 PPO 持平甚至更好，且实现难度低得多。
3.  **变体涌现：** 基于 DPO 衍生出了很多改进版，例如：
    * **ORPO：** 甚至不需要 SFT 阶段，直接由预训练模型一步到位进行偏好对齐。
    * **SimPO：** 进一步简化 DPO，去掉了 Reference Model，显存更省。

### 五、 总结建议

* **如果你是学术研究者**，研究 RL 算法本身，或者你有无限算力想要探索 LLM 的极限，可以深入研究 **PPO**。
* **如果你是算法工程师**（在企业落地 LLM），或者你在做微调项目，**请首选 DPO**。它能让你用更少的 GPU，在更短的时间内获得一个听话、对齐良好的模型。

---
**接下来您希望我为您做什么？**
1. 提供一段使用 `TRL` 库进行 **DPO 训练的 Python 代码示例**。
2. 深入讲解 DPO 的**损失函数（Loss Function）数学细节**。
3. 介绍 DPO 的最新变体（如 **ORPO** 或 **SimPO**）是如何进一步优化的。