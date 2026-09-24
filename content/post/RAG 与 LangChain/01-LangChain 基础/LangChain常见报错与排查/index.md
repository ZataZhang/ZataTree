---
title: LangChain 常见报错与排查指南
description: "从 API Key 到 OutputParserException 再到 Agent 死循环：七类高频报错的原因与解法，外加 1.x 时代最常撞见的 import 报错对照表"
date: 2026-09-08T13:30:00+08:00
image: images/index/index.png
categories:
    - Agent
tags:
    - LangChain
---

# LangChain 常见报错与排查指南

LangChain 应用报错时，最浪费时间的不是修，而是不知道问题出在哪一层。密钥、模型、提示、解析、编排——每一层的症状可能长得一样（都是「输出不对」），但修法完全不同。

最有效的第一步：**先看模型的原始输出**。把解析器临时换成 `StrOutputParser`（或直接 print 响应对象），原始输出正常，问题在解析层；原始输出本身就不对，问题在配置、提示或模型。这一步能省掉大半瞎猜时间。

## 先定位：问题出在哪一层

| 层 | 典型症状 | 排查手段 |
|---|---|---|
| 配置层 | AuthenticationError、模型不存在 | 检查环境变量；用 curl 直接调平台 API 验证密钥 |
| 模型层 | 输出质量差、不按指令来 | 换 StrOutputParser 看原始输出；换模型对比 |
| 解析层 | OutputParserException | 确认原始输出没问题后，再调格式指令 |
| 编排层 | Agent 死循环、链路数据对不上 | `verbose=True`、LangSmith 追踪、astream_events |

## 七类高频报错

### 1. API 密钥错误（AuthenticationError）

**症状**：提示 API 密钥无效、缺失或未设置。

**原因**：

- 环境变量没设置或没导出（`OPENAI_API_KEY`、`DASHSCOPE_API_KEY` 等）
- 密钥过期、被删或无效
- 账户余额不足（百炼这类预付费平台尤其常见）

**解决**：

- `print(os.getenv("OPENAI_API_KEY"))` 确认进程内真的读到了
- 检查密钥有效性，必要时重新生成
- 确认账户状态和余额

### 2. 模型未找到（NotFoundError）

**症状**：提示指定的模型不存在或无法访问。

**原因**：

- 模型名拼写错误（比如把 `qwen-plus` 写成 `qwen_plus`）
- 模型对当前 API 密钥或账户不可用（部分模型需要专门开通权限）
- API 服务区域问题

**解决**：

- 核对模型名拼写；模型名是精确匹配，多一个横线少一个点都不行
- 查提供商文档，确认模型可用性和访问权限

### 3. 提示模板错误（TemplateFormatError / MissingInputVariables）

**症状**：渲染提示时报错，或最终提示里出现了没被替换的 `{variable}`。

**原因**：

- 模板占位符与调用时传入的输入键不匹配
- 模板语法错误——f-string 风格里想输出字面量 `{` 却没写成 `{{`

**解决**：

- 确保调用链时提供了模板里所有占位符变量
- 单独测试渲染：`prompt.invoke({...})` 看渲染结果是否符合预期

### 4. Agent 输出解析错误（OutputParserException）

**症状**：LLM 输出不符合 Agent 期望的格式（0.x 时代的 ReAct Agent 未能正确输出 "Thought:" / "Action:" 等）。

**原因**：

- 模型难以理解提示中的输出格式要求
- 提示过于复杂，或工具描述含糊导致模型困惑
- 模型能力不足

**解决**：

- 简化输出格式要求；在提示里加几个符合格式的 few-shot 示例
- 改进工具描述，写清楚功能和预期输入
- `handle_parsing_errors=True`（0.x 的 AgentExecutor 参数）：把解析错误反馈给模型，让它自我纠正
- 换更强的模型

> ⚠️ 版本注记：这套症状主要属于 0.x 时代的文本协议 Agent（ReAct）。1.x 的 `create_agent` 走原生 tool calling，模型输出结构化 JSON，这类格式解析错误已大幅减少。自己写 Pydantic 解析时仍会遇到 OutputParserException，处理思路见本站《langchain_core 组件详解》。

### 5. 工具执行错误（ToolException）

**症状**：Agent 正确选中了工具，但工具执行失败。

**原因**：

- 传给工具的参数无效
- 工具依赖的外部服务不可用（限流、网络问题）
- 工具内部逻辑错误

**解决**：

- 工具内部用 try-except 捕获异常，返回有意义的错误信息给 Agent，而不是让它崩掉
- 在工具入口验证参数；把工具拿出来独立测试
- 在提示里引导 Agent：工具失败时换一种方法，或如实报告

### 6. 上下文长度超出（ContextWindowExceeded / InvalidRequestError）

**症状**：提示 + 对话历史 + 输出预留的总 token 超过模型上限。

**原因**：

- 对话历史无限累积
- RAG 检索了过多的文档块
- 提示本身冗长

**解决**：

- ⚠️ 0.x 的 `ConversationBufferWindowMemory` / `ConversationTokenBufferMemory` / `ConversationSummaryBufferMemory` 已随 legacy memory 体系移除；现代等价做法是 LangGraph checkpointer + 消息裁剪（`trim_messages`），或对长输入做分块摘要（本站《订阅摘要 Agent 实战》有完整案例）
- 控制检索文档的数量和长度
- 精简提示；或换长上下文模型

### 7. Agent 死循环（MaxIterationsExceeded）

**症状**：Agent 反复执行同样的无效操作，直到达到迭代上限。

**原因**：

- 提示不清晰，无法引导 Agent 走向正确方向
- 工具集不完备，缺少解决任务所需的关键能力
- LLM 在复杂推理中迷失

**解决**：

- 改进提示，给出明确的目标和终止条件
- 审查工具集是否齐备
- 谨慎加大迭代上限——0.x 是 AgentExecutor 的 `max_iterations`，LangGraph 时代对应 config 里的 `recursion_limit`；但先排查其他原因，调上限只是兜底
- 引入人工介入：Agent 卡住时让用户兜底

## 1.x 时代最常见的报错：import 一个已被移除的类

LangChain 1.0（2025 年 10 月发布）移除了全部 legacy 抽象。老教程代码今天最常见的死法不是逻辑错误，而是 import 直接报错：

```text
ImportError: cannot import name 'LLMChain' from 'langchain.chains'
```

遇到这类报错，对照表查一下，基本都有明确的现代等价物：

| 被移除的老写法 | 现代等价物 |
|---|---|
| `LLMChain` | LCEL 管道：`prompt \| llm \| parser` |
| `RetrievalQA` | LCEL 检索链，或 `create_retrieval_tool` |
| `ConversationChain` | LangGraph `StateGraph` + checkpointer |
| `initialize_agent` / `AgentExecutor` | `langchain.agents.create_agent`（1.x）/ `langgraph.prebuilt.create_react_agent` |
| `create_openai_functions_agent` 等旧 Agent 构造器 | 同上，统一到 `create_agent`，协议统一走 tool calling |
| `langchain.memory.*`（ConversationBufferMemory 等） | LangGraph checkpointer + 消息裁剪（`trim_messages`） |
| `load_summarize_chain` | LangGraph map-reduce，或 LCEL 手写 |
| `langchain.text_splitter` | `langchain_text_splitters` 独立包 |
| `langchain_community` 里的 ChatOllama / HuggingFaceEmbeddings | `langchain-ollama` / `langchain-huggingface` 独立包 |
| `langchain_core.pydantic_v1` | 直接用 pydantic v2 |

需要读存量老代码时，这份表反过来用就是「翻译词典」。

## 排查顺序清单

1. 报错栈最底层是平台 API 的 4xx？→ 配置层，查密钥、模型名、余额
2. 拿原始输出：StrOutputParser 或 print，判断问题在模型层还是解析层
3. 是解析错？改格式指令 + few-shot + 重试
4. Agent 行为怪？开 `verbose` / 用 LangSmith 追踪，看每一步的消息流
5. 还查不出来？把最小可复现片段剥出来单独跑

## 总结

- 报错先分层：配置 → 模型 → 解析 → 编排，症状会骗人，层不会
- 看原始输出是最快的定位手段
- 1.x 时代大半「奇怪的报错」其实是 import 了已移除的类，对照表一查便知
- 过程观测交给工具：LangSmith（见本站《LangSmith使用教程》）+ astream_events
