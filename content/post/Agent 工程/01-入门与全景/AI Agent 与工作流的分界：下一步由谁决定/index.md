---
title: "AI Agent 与工作流的分界：下一步由谁决定"
description: "用运行时控制权解释 AI Agent 与工作流的工程分界，再对照自主智能体研究中的记忆、工具、反馈与评测论文，讲清 Agent 循环、最小实现和适用边界。"
date: 2025-05-07T14:34:02+08:00
lastmod: 2026-10-21T16:54:52+08:00
weight: 10
slug: "what-is-ai-agent"
aliases:
    - /p/AI agent介绍：基于大模型的人工智能代理/
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - Agent 工程实战
draft: false
---

> 2025 年 6 月 25 日，Gartner 在新闻稿里提出了"agent washing"这个说法。他们清点了市面上号称 agentic AI 的厂商，估算几千家里约 130 家符合他们对 Agent 的标准，剩下的则可能只是给客服机器人、RPA 流程和"AI 助手"换了名字。同一份稿子还预测，到 2027 年底超过 40% 的 agentic AI 项目会被取消，原因包括成本失控、价值不清和风险控制不足。（一手：[Gartner 新闻稿](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)）

一年过去，这个词不但没过时，反而更准了。今天任何一个能调 API 的产品都自称 Agent。所以这篇不打算再抄一遍"Agent = 大模型 + 规划 + 记忆 + 工具"的零件清单——那张清单你能背下来，但它判断不了一个系统到底是不是 Agent，也解释不了为什么那么多"零件齐全"的项目最后烂尾。

我认为判断只归结为一句话：

> **下一步做什么，是模型在运行时自己决定的，还是人提前在代码里写死的。前者是 Agent，后者是工作流。**

这篇文章就沿着这条线展开：先讲清这条分界（第一节），再看过了分界的 Agent 内部在跑什么（第二节），写一个几十行的最小实现（第三节），然后回答"那框架还值不值得用"（第四节），最后给出一个残酷但省钱的结论——大多数"Agent 项目"该做的是工作流（第五节）。

## 一、一条线：控制流归谁

Anthropic 在 2024 年 12 月的工程博客里给出了一种实用的工程分类。它把带 LLM 的系统分成两种（[原文](https://www.anthropic.com/engineering/building-effective-agents)）：

- **工作流（Workflow）**：LLM 和工具通过预定义的代码路径被编排（"orchestrated through predefined code paths"）。
- **Agent**：LLM 动态地主导自己的流程和工具使用，自己掌握"怎么完成任务"（"dynamically direct their own processes and tool usage"）。

在 Anthropic 的工程分类里，两者都属于带 LLM 的系统，主要差别是：**决定下一步的人，是写代码的你，还是运行时的大模型。**

这条线是本文的工程判据；学术界对"自主智能体"的定义覆盖范围更广。经典 Agent 研究还会看系统是否处在环境中、能否持续感知和行动、是否沿时间追求目标；LLM Agent 综述则把角色设定、记忆、规划、行动和环境反馈放进同一套架构里。[Franklin 与 Graesser 的自主 Agent 分类](https://doi.org/10.1007/BFb0013570)、[LLM 自主 Agent 综述](https://doi.org/10.1007/s11704-024-40231-1)和[中文综述](https://aclanthology.org/2024.ccl-2.8/)可以对照着读。下文用"下一步由谁决定"区分工程控制流；判断一个自主 Agent 是否有用，还要看它能不能执行动作、接收环境结果并据此修正后续行为。

这句话值得停一秒。它意味着"用了 function calling"不等于 Agent，"接了 RAG"不等于 Agent，"有记忆模块"也不等于 Agent——只要那套流程的顺序是你写死在代码里的，它就是个（可能很复杂的）工作流。

Anthropic 把工作流本身又拆成五种模式，这份清单基本成了行业通用词汇：

| 模式 | 干什么 | 典型场景 |
| --- | --- | --- |
| Prompt chaining | 把一个任务拆成顺序执行的多次调用，步与步之间加校验 | 大纲 → 起草 → 校对 |
| Routing | 先分类输入，再分发给专门的提示或模型 | 工单分流、简单问题走小模型 |
| Parallelization | 并发跑独立子任务（分片），或同一任务跑多次投票 | 多角度审查、提高置信度 |
| Orchestrator-workers | 一个中心模型在运行时拆出子任务，分给 worker 再汇总 | 步数不可预测的复杂任务 |
| Evaluator-optimizer | 一个模型生成，另一个模型评审，循环到达标 | 有明确评分标准的迭代优化 |

这五种模式共享一个前提：控制流由代码预先编排。Agent 则把部分控制权交给运行时模型，具体路径无法在写代码时完整枚举；系统仍然需要设置最大步数、权限范围和人工中断点。

这里有个很容易被误读的地方。"Agent 比工作流高级"是错的。Anthropic 自己的建议是反过来的：

> 构建 LLM 应用时，先选复杂度较低的做法；遇到具体限制时再增加复杂度。

原文还指出，有些场景可以不构建 agentic 系统。因为多出来的每一分自主性都要用可预测性、延迟和钱去换：

| 维度 | 工作流 | Agent |
| --- | --- | --- |
| 适合 | 步骤固定、可事先枚举的任务 | 步数不可预测的开放式任务 |
| 可预测性 | 高，代码路径是显式的 | 低，控制流由模型决定 |
| 成本 / 延迟 | 每个决策点才付推理费 | 每个额外回合都在叠加 |
| 可调试性 | 出错能定位到某一步 | 需要沙箱测试和护栏 |
| 错误传播 | 局部 | 早期错误会被后续回合放大 |

![工作流与 Agent 的分界：控制流写死在代码里还是由模型在运行时决定](images/index/workflow-vs-agent.svg)

所以判断一个需求要不要做成 Agent，有个很朴素的测试：你能不能在写代码之前，把步骤一条条列出来？能，就用工作流。退款审批有个已知的流程形状；"调研一下我们第二季度流失率为什么会飙升"没有。

## 二、过了那条线，内部在跑什么

跨过那条线的 Agent，内部并不是什么神秘结构。今天常见的交互骨架，在 2022 年由 ReAct 清晰呈现出来。

2022 年 10 月，Shunyu Yao 等人发表了 [ReAct](https://arxiv.org/abs/2210.03629)（arXiv:2210.03629，ICLR 2023）。在那之前，CoT 擅长"想"但不接触外部世界，行动类方法擅长"做"但不会推理。ReAct 把两者交错起来，形成一个三步循环：

- **Thought（思考）**：模型先写下"我打算做什么"，这段推理留在上下文里，可被记录和审计。
- **Action（行动）**：据此发起一次工具调用，指定工具名和参数。
- **Observation（观察）**：把工具返回结果写回上下文，作为下一轮思考的输入。

在 ALFWorld 上，ReAct 只用一两个上下文示例，就比论文中的模仿学习和强化学习方法高出 **34 个百分点；在 WebShop 上高出 10 个百分点**（[论文](https://arxiv.org/abs/2210.03629)）。这项工作给后续研究提供了一个清晰的交互模板；后来的论文继续拆解工具使用、记忆、反馈学习和开放环境中的技能积累，并没有收敛成唯一架构。

![ReAct 循环：Thought 与 Action 交错，Observation 把外部世界的真实反馈带回上下文](images/index/react-loop.svg)

用这个视角看，一个 Agent 通常由四样东西拼起来，而这个分法出自 Lilian Weng 那篇被引无数的综述（[LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)）：

1. **模型**：负责推理和决策的那个大脑，也是唯一算得上"智能"的部分。
2. **工具（Tools）**：模型做不到或不知道的事的接口——搜索、数据库、代码执行器、你的业务 API。这是许多 Agent 项目的主要工程工作，因为你要把模型接到一堆"从没被设计成要应付一个会自信地搞错的东西"的旧系统上。
3. **记忆（Memory）**：短期记忆就是上下文窗口，有限且昂贵；长期记忆通常是向量库或知识图谱，按需检索。它解决的是"窗口装不下"和"跨会话要记得"。
4. **规划（Planning）**：把任务拆成子目标、对失败路径自我批判再重试，通常通过提示词、状态记录和失败重试来实现。

这几部分本身都不能证明系统具有自主性。工具提供动作接口，记忆保存状态，规划组织后续步骤；它们要和运行时控制流、环境反馈连起来，才会形成 Agent 的闭环。零件清单无法代替控制流证据。

### ReAct 之后，研究开始追问不同的问题

ReAct 讲清楚了推理和行动怎样交替，但一个循环本身不会自动带来可靠的工具使用、长期记忆或持续学习。几篇代表论文分别把这些问题拆开研究：

| 论文 | 研究切口 | 对 Agent 设计的启示 |
| --- | --- | --- |
| [Toolformer](https://proceedings.neurips.cc/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html)（NeurIPS 2023） | 模型学习何时调用 API、传入什么参数、怎样使用返回值 | 工具调用是需要单独训练和评测的能力，不是接上 API 就会用 |
| [Reflexion](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)（NeurIPS 2023） | 把环境反馈转成文字反思，存进情景记忆供后续尝试使用 | 反馈可以在不更新模型参数的情况下影响之后的决策 |
| [Generative Agents](https://doi.org/10.1145/3586183.3606763)（UIST 2023） | 在社会模拟中存储经历、生成反思，再检索记忆来规划行为 | 记忆需要写入、整理和检索机制；论文任务是社会模拟，不等于通用电脑操作 |
| [Voyager](https://arxiv.org/abs/2305.16291)（TMLR 2024） | 在 Minecraft 中结合自动课程、技能库和环境反馈持续探索 | 开放式任务需要积累可复用技能，也需要验证每次尝试是否完成 |

这些论文研究的环境和任务不同，不能把各自结果拼成一张统一能力榜。它们共同说明了一点：自主性落在模型与环境之间的闭环里，包含工具接口、状态、反馈和验证；单看模型是否能生成一个动作，还不足以判断系统能否独立完成任务。

### 评测开始把 Agent 放进真实交互环境

评测论文把"能不能做事"具体化为环境中的任务完成：

| 论文 | 任务或环境 | 能观察什么 |
| --- | --- | --- |
| [AgentBench](https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html)（ICLR 2024） | 八种交互环境 | 跨任务的推理、决策和多轮执行 |
| [WebArena](https://proceedings.iclr.cc/paper_files/paper/2024/hash/4410c0711e9154a7a2d26f9b3816d1ef-Abstract-Conference.html)（ICLR 2024） | 可复现的网站和长程浏览任务 | 多页面操作后，目标状态是否真的达成 |
| [OSWorld](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d413e48f84dc61244b6be550f1cd8f5-Abstract-Datasets_and_Benchmarks_Track.html)（NeurIPS 2024） | Ubuntu、Windows、macOS 上的真实桌面应用 | 多模态 Agent 能否操作应用并完成开放式电脑任务 |
| [SWE-agent](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)（NeurIPS 2024） | SWE-bench 软件工程任务 | 面向 Agent 设计的计算机接口如何影响代码导航、修改和测试 |

这里有个和工程选型直接相关的变化：论文不只看模型说"我已完成"，而是检查网页、文件、应用或测试环境中的结果。AgentBench、WebArena 和 OSWorld 的基线成绩来自 2024 年论文实验；它们在本文里用来说明评测方法，不代表 2026 年模型的当前排名。2025 年的 [PlanGenLLMs](https://aclanthology.org/2025.acl-long.958/) 和 2026 年的[自主 Agent 评测综述](https://aclanthology.org/2026.findings-acl.1330/)进一步整理了规划质量、成本、安全和鲁棒性等维度。

## 三、从最小循环到自定义 Agent

把上面那套循环落到代码上，它短得有点让人失望。对齐 OpenAI function calling 的循环描述，骨架是这四步：

1. 把任务和可用工具清单发给模型；
2. 如果模型要求调用工具，就执行它，并把结果发回模型；
3. 重复；
4. 直到模型给出最终答案，**或者触发了你自己设的上限**。

```python
def run_agent(task, tools, model, max_steps=10):
    messages = [{"role": "user", "content": task}]
    for step in range(max_steps):                 # 步骤 4：硬上限，必须有
        resp = model.chat(messages, tools=tools)   # 步骤 1
        messages.append(resp)

        if not resp.tool_calls:                    # 模型不再调工具 = 给出答案
            return resp.content

        for call in resp.tool_calls:               # 步骤 2：执行工具
            result = dispatch(call.name, call.args)  # 参数要在这里校验
            messages.append({"role": "tool",
                             "tool_call_id": call.id,
                             "content": result})    # 步骤 3：观察写回

    return "达到最大步数仍未完成"                    # 显式区分"成功终止"和"被截断"
```

一个能跑通 Demo 的 Agent 就这么几十行。它的价值在于帮你把注意力从"框架该选哪个"拉回到实际影响结果的地方：

- **工具定义**：名字、参数 schema、描述，尤其是"什么时候不该用它"。工具描述写不清楚，模型就会幻觉出根本不存在的参数。
- **停止条件**：`max_steps` 只是底线。还要能识别"同一组工具被反复调用"这种循环，并主动降级到"我不知道"。
- **错误与校验**：模型吐出来的参数先在边界上用 Pydantic / Zod 校验，再打到下游系统。
- **可观测**：每一次模型调用和工具调用都得留下输入、输出、耗时、token。没有 trace 的 Agent 优化就是蒙眼调参。

Anthropic 在确认"这个场景确实需要 Agent"之后，把设计收敛成三件事：环境（Agent 看到的世界）、工具（它的手脚）、系统提示（目标、约束、停止规则）。其余的缓存、并行调用、进度 UI，都是行为跑通之后才谈的优化。

### 把它定制成自己的 Agent，先写一张任务卡

自定义 Agent 通常不需要从训练模型开始。先为一个具体任务配置目标、指令、资料、工具和停止规则；用户偏好可以写进指令或经同意后保存为记忆。只有样例评测显示问题稳定地来自模型本身的行为模式，再评估微调或更复杂的架构。

动手前先填这张任务卡：

| 项目 | 要写清楚的问题 |
| --- | --- |
| 目标与触发条件 | 它负责解决哪一种重复任务？什么请求不属于它？ |
| 输入与输出 | 用户会提供什么；结果要用什么格式交付？ |
| 可用资料 | 它能读哪些文件、知识库或网页？资料冲突时怎么标注？ |
| 工具与权限 | 它需要哪些只读或写入工具？哪些操作必须先让人确认？ |
| 完成标准 | 什么证据可以说明任务真的完成，而不只是回答得像完成了？ |
| 停止与记忆 | 什么时候停止、报告不确定性或交还给人？哪些信息需要跨任务保留？ |

以"技术博客资料研究助理"为例：输入一个主题后，它检索论文和官方文档，读取资料并整理带来源的摘要；每个关键结论都要能回到原文，检索结果互相矛盾时要并列说明。第一版只开放搜索和文件读取，文章写入目录或发布前由作者确认。它的验收标准不是"写得流畅"，而是引用能打开、论文信息准确、结论没有超出来源支持的范围。

随后按这个顺序实现：

1. **先写指令。** 说明角色、任务边界、工作步骤、输出格式，以及不知道或证据不足时该怎么答。指令负责引导行为，不能代替工具权限检查。
2. **只接完成任务所需的工具。** 每个工具写清名称、参数、返回值和适用场景；先从只读能力开始。写文件、发消息、改数据这类有副作用的操作，应由程序校验权限，并在需要时等待人工确认。
3. **区分知识与行动。** 稳定资料放进可检索的文档或知识库；搜索、计算、查询状态等实时动作交给工具。只把确实要跨会话沿用的偏好保存为长期记忆。
4. **定好闭环和停机条件。** 设定最大轮数、超时、工具失败处理、成功判据和转人工条件；对工具结果做程序校验，再决定是否继续。
5. **用真实样例反复验收。** 准备常见请求、缺少信息、资料冲突、工具报错等样例，检查任务是否完成、引用是否可靠、权限边界是否生效，并记录耗时、成本和失败原因。

下面这份指令骨架可以直接改成自己的版本：

```text
你负责：{一项具体任务}
适用请求：{触发条件与边界}
输入：{需要的材料}
工作步骤：{先做什么，再做什么}
可用工具：{工具名称、用途及限制}
完成标准：{可以检查的结果}
不确定或失败时：{说明缺口、重试上限、何时交还给人}
输出格式：{字段、结构、语气}
```

如果用 Python 实现，可以先沿用上面的最小循环，自己控制模型调用和工具分发；需要现成的运行时、工具接入、会话状态或追踪能力时，再看框架。比如 [OpenAI Agents SDK Quickstart](https://openai.github.io/openai-agents-python/quickstart/) 展示了 Agent、指令、工具和运行器的基本组合；这些框架原语能帮你搭运行时，任务边界和验收标准仍要由你定义。

## 四、那 LangChain 这类框架到底解决了什么

关于框架，常见的问法是"LangChain 为什么必要"。这个问法容易把问题带偏：框架解决的不是"让模型更聪明"。

框架的价值是把上面那个循环工程化，具体有三件事：

1. **状态持久化与断点恢复**。一个任务跑几十分钟、中间机器重启、用户取消，你需要能暂停、检查、恢复一次运行。这是从 Demo 到生产的一道重要关卡。
2. **可观测与评估**。把 trace/span、成本字段、失败分类统一起来，接上 LangSmith、Langfuse 这类平台。
3. **多模型、多工具的路由与适配**。不同厂商的 tool 调用格式、流式协议、重试语义都不一样，框架帮你抹平。

代价也需要计算。Anthropic 建议能用模型原生 API 就先用原生 API，理由是框架有时会把 prompt 藏起来，也容易鼓励过度设计。这个提醒对 2026 年的语境依然成立：现在模型原生的 tool use 和结构化输出已经足够好用；很多场景下，一套能读懂 trace 的调试习惯，比再加一层编排抽象更直接。

我的经验法则是：

| 你的处境 | 建议 |
| --- | --- |
| 单流程、验证概念、就想看看模型行不行 | 直接调 API，几十行搞定 |
| 需要断点、重放、审计轨迹 | 上带 checkpoint 的图式框架（如 LangGraph 这类） |
| 需要跨语言、跨团队统一工具接入 | 把工具层标准化（MCP），框架保持可替换 |
| 只是想要"看起来像 Agent" | 先回到第一节，重新判断你需不需要 Agent |

工具标准化这一层值得单独提一句。**Model Context Protocol（MCP）** 为模型访问外部工具和数据提供统一协议，和编排框架处在不同层次。框架会过时，但你为了接入自家系统而写的工具定义可以活得更久。这是值得长期投入的资产。协议本身的演变，这个系列有单独一篇梳理。

## 五、大多数"Agent 项目"该做的是工作流

回到开头 Gartner 那 40%。不少被取消的项目从第一步就选错了问题。

判断顺序其实很短：

![选型判断：先问步骤能否事先枚举，再问有没有可验证的反馈信号](images/index/when-to-use-agent.svg)

1. 步骤能不能事先枚举？能，就用工作流。退款审批、周报生成、工单分流，全是工作流。
2. 步骤不能枚举时，有没有可验证的反馈信号？比如测试跑不跑得过、环境状态对不对、截图里按钮在不在。有反馈，Agent 才能依据结果自我纠错；没有反馈，系统会变得更贵，也更难判断对错。
3. **路径开放且结果可验证**，这类任务适合考虑 Agent。软件开发（多文件改动 + 测试作为 ground truth）、需要反复试错的调研、可控环境里的计算机操作，都属于这一类。

这也顺带解释了编程 Agent 为什么相对容易评估：软件测试能给出便宜、客观的反馈信号，`pytest` 会直接报告检查结果。

## 结论：自主性要落在可验证的闭环里

"下一步由谁决定"是区分工程控制流的好判据；学术上的自主 Agent 还要求它持续处在环境里感知、行动和追求目标。ReAct 展示了推理与行动如何循环，Toolformer、Reflexion、Generative Agents 和 Voyager 分别补上工具使用、反馈记忆、长期行为与技能积累；AgentBench、WebArena、OSWorld 等工作则把评估放回交互环境中。

做选型时，先写下任务目标、可观察状态、允许动作、成功判据和停止上限。步骤可完整枚举，就用工作流；路径需要根据环境变化，但每一步有可验证反馈，再考虑把控制权交给 Agent。**模型能决定下一步只是起点，能验证行动结果并安全停止，才构成可用的自主闭环。**

## 参考

下面四份综述 PDF 保存在本页 `papers/` 目录，文件未经修改；文章页同时链接到出版方或 ACL Anthology 的原始页面。许可与来源记录见[资料说明](papers/README.txt)。

- [Gartner: Over 40% of Agentic AI Projects Will Be Canceled by End of 2027](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)（一手，含 "agent washing" 与约 130 家真实厂商的估算）
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（工作流与 Agent 的定义、五种工作流模式）
- [OpenAI Agents SDK Quickstart](https://openai.github.io/openai-agents-python/quickstart/)（Python 中组合 Agent 指令、工具和运行器的官方示例）
- [Is it an Agent, or just a Program? A Taxonomy for Autonomous Agents](https://doi.org/10.1007/BFb0013570)（Franklin 与 Graesser，1996/1997；经典自主 Agent 定义与分类）
- [A Survey on Large Language Model based Autonomous Agents](https://doi.org/10.1007/s11704-024-40231-1)（Wang et al., Frontiers of Computer Science, 2024；[本地 PDF](papers/Wang-2024-autonomous-agents-survey-FCS.pdf)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）
- [《基于大语言模型的自主智能体概述》](https://aclanthology.org/2024.ccl-2.8/)（陈旭，CCL 2024；[本地 PDF](papers/Chen-2024-autonomous-agent-survey-CCL.pdf)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)（Yao et al., 2022，ICLR 2023）
- [Toolformer: Language Models Can Teach Themselves to Use Tools](https://proceedings.neurips.cc/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html)（NeurIPS 2023）
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)（NeurIPS 2023）
- [Generative Agents: Interactive Simulacra of Human Behavior](https://doi.org/10.1145/3586183.3606763)（Park et al., UIST 2023）
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291)（Wang et al., TMLR 2024）
- [AgentBench: Evaluating LLMs as Agents](https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html)（ICLR 2024）
- [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://proceedings.iclr.cc/paper_files/paper/2024/hash/4410c0711e9154a7a2d26f9b3816d1ef-Abstract-Conference.html)（ICLR 2024）
- [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d413e48f84dc61244b6be550f1cd8f5-Abstract-Datasets_and_Benchmarks_Track.html)（NeurIPS 2024）
- [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)（NeurIPS 2024）
- [PlanGenLLMs: A Modern Survey of LLM Planning Capabilities](https://aclanthology.org/2025.acl-long.958/)（Wei et al., ACL 2025；[本地 PDF](papers/Wei-2025-PlanGenLLMs-ACL.pdf)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）
- [A Survey on Evaluation of LLM-based Agents](https://aclanthology.org/2026.findings-acl.1330/)（Yehudai et al., Findings of ACL 2026；[本地 PDF](papers/Yehudai-2026-agent-evaluation-survey-ACL.pdf)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）
- [Lilian Weng: LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)（planning / memory / tools 三分法）

延伸阅读（同栏目）：

- [Agent 工程实战开篇：从 Demo 到生产还有多远](/p/agent-工程实战开篇从-demo-到生产还有多远/)——把上面这套概念推进到生产的常见陷阱
- [Agent 生产工程全景手册：从 Runtime 到业务闭环](/p/agent-production-engineering-handbook/)——Runtime、评测、治理与业务闭环
- [2026 年 AI Agent 现状：一次带出处的全景清点](/p/ai-agent-landscape-2026-audit/)——框架消长与协议标准化的最新盘点
