---
title: "主流 Agent 框架对比与多框架统一接口设计"
description: "对比 Deep Agents、LangGraph、LangChain create_agent、OpenAI Agents SDK、PydanticAI、Google ADK 与 Microsoft Agent Framework，并给出多框架共存时的统一请求、响应、流式事件和会话设计。"
date: 2026-08-31T16:00:00+08:00
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 框架与运行时
    - Agent Orchestration
    - LangGraph
    - Deep Agents
    - PydanticAI
draft: false
---

Agent 框架没有一个绝对的“最优解”。文件研究 Agent、强类型业务 Agent、确定性审批流和云厂商原生 Agent，面对的是不同问题。真正稳定的架构不是押注一个框架，而是把**业务协议**与**框架运行时**分开。

本文回答三个问题：

1. 主流 Agent 框架分别擅长什么？
2. 它们的输入与返回结构是否兼容？
3. 如何让不同任务使用不同框架，同时保持统一 API？

---

## 1. 先理解 Agent 框架的层次

不同产品都被称为“Agent 框架”，但抽象层次并不相同：

```text
业务 API / Web / App
        ↓
业务 Agent：客服、研究、抽取、编码
        ↓
Agent Harness：Prompt、Tools、Skills、Memory、Subagents
        ↓
Workflow Runtime：状态图、Checkpoint、Interrupt、恢复
        ↓
模型与工具 Provider
```

例如：

- LangGraph 更接近可持久化的 Workflow Runtime。
- LangChain `create_agent` 是轻量 Agent Harness。
- Deep Agents 是建立在 LangChain 与 LangGraph 上的“电池齐全”Harness。
- OpenAI Agents SDK 同时封装 Agent Loop、Handoff、Guardrail、Session 与 Tracing。
- PydanticAI 更强调 Python 类型、依赖注入和结构化结果。

如果不区分层次，很容易拿“工作流引擎”和“开箱即用的研究 Agent”直接比较。

---

## 2. 主流框架速查

| 框架 | 核心优势 | 更适合 | 主要代价 |
| --- | --- | --- | --- |
| Deep Agents | 文件上下文、Skills、Subagents、沙箱、压缩 | 研究、编码、文档处理、长任务 | 默认能力多，升级时要关注 Harness 行为变化 |
| LangGraph | 状态图、Checkpoint、Interrupt、可恢复执行 | 确定性流程、审批、长事务 | 需要自己设计节点、状态和路由 |
| LangChain `create_agent` | 轻量、模型与工具生态广 | 普通工具调用 Agent | 文件工作区和复杂编排需要自行补充 |
| OpenAI Agents SDK | `Agent + Runner`、Handoff、Guardrail、Tracing | OpenAI 技术栈、客服、业务协作 | 与 OpenAI Responses 生态结合更紧 |
| PydanticAI | 强类型、依赖注入、结构化输出 | FastAPI 后端、抽取、业务自动化 | 文件型 Harness 和复杂工作区能力较少 |
| Google ADK | Sequential/Parallel/Loop、多 Agent、Vertex 集成 | Gemini、GCP、A2A 场景 | 跨云项目的迁移价值要单独评估 |
| Microsoft Agent Framework | Workflow、Memory、Middleware、Azure 托管 | Azure、C#、微软企业生态 | 对非微软栈未必是最低成本选择 |

### 2.1 Deep Agents：长上下文任务 Harness

Deep Agents 的价值不只是“能调用子 Agent”，而是一组协同工作的默认能力：

- 通过虚拟文件系统保存和卸载大块上下文；
- 通过 Summarization 控制长对话；
- 用 Subagents 隔离搜索、代码执行等中间过程；
- 用 Skills 按需加载工作流，避免把所有规则塞进 System Prompt；
- 用 Backend 对接本地目录、状态存储、持久 Store 或沙箱；
- 继承 LangGraph 的流式执行、Checkpoint 和 Human-in-the-loop。

适合：代码 Agent、深度研究、长文档分析、需要沙箱和文件产物的任务。

不适合：只调用两三个业务 API 的简单客服。此时完整 Harness 可能比业务本身还复杂。

> 从 `0.7.0` 开始，Deep Agents 默认 Prompt 更精简，`TodoListMiddleware` 改为显式启用，文件 Backend 默认使用更安全的虚拟路径模式。升级旧项目时还要检查 `write_file` 覆盖语义和新增的递归 `delete` 能力。

参考：[Deep Agents 官方概览](https://docs.langchain.com/oss/python/deepagents/overview)、[Deep Agents Changelog](https://github.com/langchain-ai/deepagents/blob/main/libs/deepagents/CHANGELOG.md)。

### 2.2 LangGraph：确定性主流程

当业务流程本身清晰时，不要把全部控制权交给模型：

```text
输入校验 → 分类 → 检索 → 人工审批 → 执行 → 验证 → 结束
```

这种流程适合直接实现为 LangGraph。模型只负责需要语义判断的节点，路由、重试、上限和失败处理仍由代码决定。

推荐组合：

```text
确定性主流程：LangGraph
开放式复杂节点：Deep Agent 或其他 Agent
```

### 2.3 LangChain `create_agent`：轻量通用 Agent

如果需求只是“模型根据问题选择工具，拿到结果后回答”，`create_agent` 通常已经足够。它保留 LangChain 的模型、工具和 Middleware 生态，又不强制引入完整文件工作区与子 Agent。

### 2.4 OpenAI Agents SDK：OpenAI 原生体验

OpenAI Agents SDK 使用 `Agent + Runner` 管理工具、轮次、Handoff、Guardrail 和 Session，并提供内置 Tracing。它适合：

- 项目主要使用 OpenAI 模型和 Responses API；
- 需要不同专业 Agent 之间 Handoff；
- 希望快速加入输入、输出和工具 Guardrail；
- 不想自己维护 Agent Loop。

如果需要完全跨模型、虚拟文件系统或复杂状态图，Deep Agents/LangGraph 通常更自然。

参考：[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/agents/)、[Guardrails](https://openai.github.io/openai-agents-python/guardrails/)。

### 2.5 PydanticAI：强类型业务 Agent

PydanticAI 很适合已有 Pydantic/FastAPI 技术栈的团队：

- 输入依赖和运行上下文容易注入；
- 输出可以直接是 Pydantic 模型；
- 类型检查和测试体验清晰；
- 可结合 Temporal、DBOS、Prefect、Restate 实现 Durable Execution。

典型任务包括票据抽取、合同分类、字段补全和调用内部业务 API。它们更像“带工具的类型化服务”，不一定需要一个文件型 Agent OS。

参考：[PydanticAI Durable Execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/)。

### 2.6 Google ADK：GCP 与多 Agent Workflow

Google ADK 提供 Sequential、Parallel、Loop 以及动态工作流，可以混合确定性执行节点与 LLM Agent。对于 Gemini、Vertex AI、A2A 和 GCP 托管场景，它具有明显的平台整合优势。

参考：[Google ADK Workflows](https://github.com/google/adk-docs/blob/main/docs/workflows/index.md)。

### 2.7 Microsoft Agent Framework：微软企业栈

Microsoft Agent Framework 覆盖 Agent、Workflow、Memory、Middleware、Checkpoint、Human-in-the-loop 和 Azure 托管，并提供 AutoGen、Semantic Kernel 的迁移路线。Azure、C# 和微软企业集成是它最自然的使用环境。

参考：[Microsoft Agent Framework](https://learn.microsoft.com/en-gb/agent-framework/)。

---

## 3. 它们的返回接口一样吗？

不一样。

| 框架 | 常见调用 | 最终结果入口 |
| --- | --- | --- |
| Deep Agents / LangGraph | `agent.ainvoke(...)` | `state["messages"][-1]` / `state["structured_response"]` |
| OpenAI Agents SDK | `Runner.run(...)` | `result.final_output` |
| PydanticAI | `agent.run(...)` | `result.output` |
| Google ADK | Runner/Event API | 从事件或最终响应中提取 |
| Microsoft Agent Framework | Agent/Workflow API | Response、Message 或 Event |

差异不仅是字段名。各框架的内部对象还承载不同语义：

- LangChain 有 `HumanMessage`、`AIMessage`、`ToolMessage`；
- OpenAI Agents SDK 有 Run Item、Handoff 与原始 Response Item；
- PydanticAI 有自己的 Model Message；
- ADK 和 Microsoft Framework 以各自的 Event/Message 表达执行过程。

因此，不应把框架原始对象直接作为 HTTP 响应。否则前端会被某个框架绑定，切换框架时 API、流式协议和会话结构都要一起重写。

---

## 4. 统一业务协议，而不是统一框架内部

建议只统一四样东西：

1. 请求 `AgentRequest`
2. 最终响应 `AgentResponse`
3. 流式事件 `AgentEvent`
4. 业务会话 ID 到框架会话 ID 的映射

不要强行统一：

- 框架内部 Message；
- LangGraph Checkpoint；
- OpenAI Session/Conversation；
- Provider 原始 Response；
- 框架专属的恢复状态。

### 4.1 统一请求与响应

```python
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """统一的 Agent 请求。"""

    task_id: str
    message: str
    thread_id: str | None = None
    user_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class Usage(BaseModel):
    """统一的模型用量。"""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class AgentResponse(BaseModel):
    """与框架无关的最终响应。"""

    task_id: str
    framework: Literal[
        "deepagents",
        "langgraph",
        "openai-agents",
        "pydantic-ai",
        "google-adk",
        "microsoft-agent-framework",
    ]
    output: str
    data: dict[str, Any] | None = None
    usage: Usage | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentAdapter(Protocol):
    """所有 Agent Adapter 必须实现的业务接口。"""

    async def run(self, request: AgentRequest) -> AgentResponse:
        """运行 Agent 并返回标准结果。"""
        ...
```

`output` 用于展示给人，`data` 用于程序消费。结构化数据不要从自然语言中二次解析，应优先使用框架的 Structured Output 能力。

### 4.2 Deep Agents Adapter

```python
from typing import Any


class DeepAgentsAdapter:
    """将 Deep Agents 状态转换成业务响应。"""

    def __init__(self, agent: Any) -> None:
        self.agent = agent

    async def run(self, request: AgentRequest) -> AgentResponse:
        config: dict[str, Any] = {}
        if request.thread_id:
            config["configurable"] = {"thread_id": request.thread_id}

        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config,
        )
        output = result.get("structured_response")
        data = output.model_dump() if hasattr(output, "model_dump") else output

        return AgentResponse(
            task_id=request.task_id,
            framework="deepagents",
            output=str(result["messages"][-1].content),
            data=data if isinstance(data, dict) else None,
        )
```

### 4.3 PydanticAI Adapter

```python
from typing import Any


class PydanticAIAdapter:
    """将 PydanticAI 结果转换成业务响应。"""

    def __init__(self, agent: Any) -> None:
        self.agent = agent

    async def run(self, request: AgentRequest) -> AgentResponse:
        result = await self.agent.run(request.message)
        output = result.output
        data = output.model_dump() if hasattr(output, "model_dump") else None

        return AgentResponse(
            task_id=request.task_id,
            framework="pydantic-ai",
            output=str(output),
            data=data,
        )
```

### 4.4 OpenAI Agents SDK Adapter

```python
from typing import Any

from agents import Runner


class OpenAIAgentsAdapter:
    """将 OpenAI Agents SDK 结果转换成业务响应。"""

    def __init__(self, agent: Any) -> None:
        self.agent = agent

    async def run(self, request: AgentRequest) -> AgentResponse:
        result = await Runner.run(self.agent, request.message)
        output = result.final_output
        data = output.model_dump() if hasattr(output, "model_dump") else None

        return AgentResponse(
            task_id=request.task_id,
            framework="openai-agents",
            output=str(output),
            data=data,
            metadata={"last_agent": result.last_agent.name},
        )
```

---

## 5. 流式接口才是多框架适配的难点

最终结果容易统一，流式事件更难。不同框架可能输出 Token、Message、Node Update、Tool Event、Handoff、Approval 或 Artifact。

建议定义最小公共事件集：

```python
class AgentEvent(BaseModel):
    """面向前端的统一流式事件。"""

    task_id: str
    sequence: int
    type: Literal[
        "run.started",
        "text.delta",
        "tool.started",
        "tool.completed",
        "handoff.started",
        "approval.required",
        "artifact.created",
        "run.completed",
        "run.failed",
    ]
    agent: str | None = None
    content: str | None = None
    tool_call_id: str | None = None
    tool: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
```

Adapter 负责映射：

```text
LangGraph model token      → text.delta
LangGraph tool node        → tool.started / tool.completed
OpenAI response event      → text.delta
OpenAI handoff item        → handoff.started
PydanticAI text delta      → text.delta
ADK function event         → tool.started / tool.completed
```

建议使用 SSE 或 WebSocket 对外发送这些业务事件，同时将框架原始事件保存在可观测系统中，而不是全部暴露给前端。

---

## 6. 会话和恢复如何处理

不同框架的持久化机制不能直接互换：

- Deep Agents/LangGraph 使用 `thread_id + checkpointer`；
- OpenAI Agents SDK 可以使用 Session、Conversation 或 Previous Response；
- PydanticAI 可以传入历史消息，长任务可接 Durable Execution；
- ADK 和 Microsoft Framework 有各自的 Session/Event/Checkpoint。

业务数据库只保存映射：

```python
class AgentSession(BaseModel):
    """业务会话与框架会话的映射。"""

    session_id: str
    framework: str
    external_session_id: str | None = None
    checkpoint_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

不要尝试把 LangGraph Checkpoint 转换成 OpenAI Session。需要迁移框架时，使用业务层保存的用户消息、结构化结果和必要摘要重新构造上下文。

---

## 7. 推荐的多框架架构

```text
HTTP / SSE / WebSocket
          ↓
AgentRequest / AgentEvent / AgentResponse
          ↓
任务路由器
    ├── 文件与深度研究  → DeepAgentsAdapter
    ├── 确定性长流程    → LangGraphAdapter
    ├── 结构化业务任务  → PydanticAIAdapter
    ├── OpenAI 客服     → OpenAIAgentsAdapter
    └── 云厂商原生任务  → ADK / Microsoft Adapter
          ↓
框架自己的 State、Session、Tracing 和 Runtime
```

任务路由器不应该根据用户的一句话临时“猜框架”，而应该基于明确的任务类型、能力需求和部署策略选择：

```python
class AgentRouter:
    """根据任务类型选择 Agent Adapter。"""

    def __init__(self, adapters: dict[str, AgentAdapter]) -> None:
        self.adapters = adapters

    async def run(
        self,
        task: str,
        request: AgentRequest,
    ) -> AgentResponse:
        adapter = self.adapters.get(task)
        if adapter is None:
            msg = f"不支持的任务类型：{task}"
            raise ValueError(msg)
        return await adapter.run(request)
```

---

## 8. 实际选型建议

### 选择 Deep Agents，如果

- 工具会产生大量文本或文件；
- 需要独立子 Agent 隔离上下文；
- 需要沙箱执行代码；
- 任务持续时间长且步骤开放；
- Skills、Memory、Filesystem 是核心能力。

### 选择 PydanticAI，如果

- 输出必须严格符合业务 Schema；
- Agent 是 FastAPI 服务的一部分；
- 依赖注入和 Python 类型体验优先；
- 工作流主要是调用业务 API，而不是操作文件工作区。

### 选择 OpenAI Agents SDK，如果

- 主要使用 OpenAI Responses API；
- Handoff、Guardrail、Session 和 Tracing 是核心需求；
- 接受较强的 OpenAI 生态结合。

### 选择 LangGraph，如果

- 流程有明确状态机；
- 必须可靠暂停、恢复和重试；
- 人工审批是正式流程节点；
- 需要精确控制每一步，而不是让模型自由规划。

### 选择 ADK 或 Microsoft Agent Framework，如果

- 部署平台、身份、监控和企业集成本身就在对应云生态；
- 平台整合收益高于跨框架可移植性。

---

## 9. 最后的工程原则

1. **框架是实现细节，业务协议才是长期资产。**
2. **统一请求、响应与前端事件，不统一内部消息和 Checkpoint。**
3. **确定性流程交给代码，开放式任务交给 Agent。**
4. **结构化输出由 Schema 保证，不要解析自然语言。**
5. **安全边界放在工具、权限和沙箱，不要只依赖 Prompt。**
6. **每种框架独立做回归评测，再决定路由策略。**

一个健康的多框架系统最终应该做到：替换某个 Agent 实现时，前端 API、业务数据库和其他 Agent 都无需跟着重写。
