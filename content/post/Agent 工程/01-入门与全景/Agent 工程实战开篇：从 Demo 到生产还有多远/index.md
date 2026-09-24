---
title: "Agent 工程实战开篇：从 Demo 到生产还有多远"
description: "为什么同样的 Agent 代码在笔记本上跑得通，到线上就崩——梳理把 AI Agent 从 Demo 变成产品过程中最常见的工程陷阱与解决思路"
date: 2026-07-23T10:31:54+08:00
slug: "Agent 工程实战开篇：从 Demo 到生产还有多远"
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 入门与全景
    - Agent 工程实战
draft: false
---

> 这是 Agent 工程实战系列的第一篇。我会把在生产环境里踩过的坑、验证过的方案，按主题整理成可复用的工程手册。

## 一句话定义 Agent 工程

**Agent 工程 = 把一个在本地能跑 80% 的 LLM 循环，变成一个在真实流量下 99% 可用、可观测、可评估、可控成本的服务。**

把这句话拆开，至少有五件事要做：

1. **可控** — 输出可控、行为可控、失败可控
2. **可观测** — 每一步都留下 trace，事后能复盘
3. **可评估** — 不是"看着还不错"，是有数据证明它确实不错
4. **可扩展** — 用户从 10 个到 10 万个，延迟和成本不会爆
5. **可治理** — 安全、合规、可解释、可下线

下面聊聊从 Demo 走到生产最容易翻车的几个点。

## 1. 别再把 Prompt 当成"代码"

Demo 阶段你可以在 `system prompt` 里写一段 200 字的话，模型听话；但到了生产：

- 不同模型的 instruction-following 能力差异巨大
- 用户输入会污染 prompt 结构（prompt injection）
- Prompt 一改，行为就会漂移，且没人能精确描述改了什么

**工程化做法：**

- Prompt 模板独立仓库管理，版本化（每条上线记录到变更日志）
- 把"工具说明"、"角色设定"、"业务规则"、"用户输入"在拼接时显式分段，而不是塞进同一个 f-string
- 关键 prompt 用 **LLM 评审 / 回归集** 守门，而不是靠人肉感觉

## 2. Tool Calling 不是 `if name == "...":`

很多 Demo 是这样的：

```python
if "天气" in user_input:
    return get_weather(...)
```

这种"伪 function calling"看起来工作，但生产里会立刻暴露问题：

- 用户可以构造输入绕过规则
- 没有 schema 校验，模型幻觉出来的参数会直接打到下游
- 没有权限隔离，所有工具对所有 prompt 开放

**工程化做法：**

- 用真正的 tool/function schema（OpenAI / Anthropic 风格），让模型输出结构化参数
- 用 **Pydantic / Zod** 在边界做参数校验
- 工具分级别：**只读工具** / **写工具** / **外部副作用工具**，按风险分桶调用
- 高风险工具强制 **Human-in-the-loop** 确认

## 3. Agent Loop 必须有上限

最经典的 bug：

```
用户问了一个含糊的问题 →
Agent 没拿到足够信息 →
Agent 又去调用工具 →
工具又返回模糊结果 →
Agent 再调工具 →
... → token 烧光 / 循环 100 次 / 超时
```

**工程化做法：**

- 显式设置 **max_steps**（建议 ≤ 10）
- 区分"成功终止"、"最大步数终止"、"循环检测终止"
- 检测到重复 state（同一组工具调用两次以上）→ 主动 break 并 fallback 到"我不知道"
- 关键决策点强制 **reflection / self-critique**，但要限制其调用次数

## 4. 可观测性：先有 Trace，再谈优化

没有 trace 的 Agent 优化就是"蒙眼调参"。生产里至少要有：

- **Span**：每一次 LLM 调用、工具调用、记忆读写的输入 / 输出 / 耗时 / token
- **Trace ID**：贯穿一次完整任务的所有 span
- **成本字段**：每次调用的 input/output token 与单价
- **失败分类**：timeout / 工具异常 / 解析失败 / 内容安全拦截

推荐起步就用 [LangSmith](https://docs.smith.langchain.com/)、[Langfuse](https://langfuse.com/)、[Arize Phoenix](https://phoenix.arize.com/) 这类平台之一，自建成本不低。

## 5. 评估不是上线后再想的事

生产里最容易回答不出的问题："这个版本比上个版本到底好了多少？"

**最小可用的评估体系：**

- **离线评测集**：50~200 个有标准答案或参考回答的 case，回归门禁
- **LLM-as-judge**：用一个更强的模型给输出打分，但要注意：评分模型本身也会偏
- **线上指标**：任务成功率、人工接管率、单任务成本、p95 延迟
- **红队 / 注入集**：专门挑 prompt injection 与越权场景，定期跑

## 6. 成本治理：模型路由 + 缓存 + 流式

Agent 系统烧钱的速度比传统服务快得多，因为：

- 多轮 LLM 调用 × 长上下文 × 复杂工具链
- "小问题用大模型"是常态浪费

**工程化做法：**

- **模型路由**：简单任务走小模型（如分类、提取），复杂任务才走大模型
- **语义缓存**：相似 query 直接返回上次结果，注意要带 cache key 的失效策略
- **流式输出**：长生成场景下，TTFT 比总时长更重要
- **预算熔断**：单任务 / 单用户 / 单租户的 token 上限，超限自动降级

## 7. 安全：默认假设你的 Prompt 会被攻破

- **不要** 把系统提示视为秘密，它一定会被泄露
- **不要** 让 LLM 决定要不要执行高风险工具（删库、转账、发邮件），必须硬规则守门
- **必须** 对工具返回值做清洗——它也是用户可控输入
- **必须** 审计日志：谁、什么时候、通过哪个 agent、调了哪个工具、传了什么参数

## 这个系列接下来会写什么？

按上面七个主题，每个都会展开成一篇实战文章，配可运行示例：

1. Prompt 工程化：从 f-string 到模板系统
2. Tool Calling 工程化：schema、权限、Human-in-the-loop
3. Agent Loop 设计：状态机视角的 ReAct
4. 可观测性实战：Langfuse / LangSmith 接入
5. 评估体系搭建：离线集 + LLM-judge + 线上指标
6. 成本与性能：模型路由、缓存、流式
7. 安全与合规：Prompt injection 防护与审计

如果你也在做 Agent，欢迎把你踩过的坑写在评论区——下一篇我会挑留言里出现最多的那个话题。

## 参考

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OpenAI: A practical guide to building agents](https://platform.openai.com/docs/guides/agents)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Langfuse: Open Source LLM Engineering](https://langfuse.com/)