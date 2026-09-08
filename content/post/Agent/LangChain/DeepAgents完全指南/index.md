---
title: DeepAgents完全指南
description: "从协议、架构到生产实践：全面解析 LangChain Deep Agents 的设计理念、API、文件系统、子智能体、上下文管理与部署策略"
date: 2026-09-08T11:26:34+08:00
image: images/index/index.png
categories:
    - Agent
tags:
    - LangChain
---

# DeepAgents 完全指南

> 本文基于 `deepagents==0.7.x`（Python）撰写，涵盖从入门概念到生产部署的全部核心内容。0.x 版本 API 变动较快，如果你的版本低于 0.5，请先升级再对照本文。

---

## 第一章：DeepAgents 是什么

### 1.1 一句话定义

DeepAgents（包名 `deepagents`）是 LangChain 团队推出的一个 **agent harness**（智能体运行框架）—— 一个开箱即用、高度可定制、面向长周期多步任务的智能体运行时。

它不是又一个 LangGraph 图编排工具，也不只是 LangChain 的薄封装，而是一个带有以下"观点"（opinionated）的完整框架：

- **默认就适合长任务**：内置文件系统、上下文压缩、子智能体委派，不用你自己搭。
- **每个组件都可以替换**：模型、文件后端、中间件、子智能体、技能，全部可插拔。
- **模型无关**：只要模型支持 tool calling 就能用——GPT、Claude、Gemini、Qwen、本地 Ollama 都行。
- **生产就绪**：底层是 LangGraph，天然支持流式输出、持久化、checkpoint、断点恢复。

灵感来源是 Claude Code：团队想搞清楚 Claude Code 为什么通用，然后把那些设计提炼成一个可编程的框架。

### 1.2 在 LangChain 生态中的位置

理解 DeepAgents 的关键，是理解 LangChain 生态的三层结构：

```
┌─────────────────────────────────┐
│         LangSmith               │  ← 可观测性、评测、监控
├─────────────────────────────────┤
│         Deep Agents             │  ← 完整 harness（本文主角）
├─────────────────────────────────┤
│    LangChain create_agent       │  ← 轻量 agent（无内置文件系统/子agent）
├─────────────────────────────────┤
│         LangGraph               │  ← 图运行时（状态、节点、边）
└─────────────────────────────────┘
```

- **LangGraph** 是底层的图运行时，管状态、节点、边、checkpoint。
- **LangChain `create_agent`** 是最小的 agent 循环：模型 + 工具 + 消息 → 循环 → 回复。
- **DeepAgents** 在 `create_agent` 之上叠加了一整套 middleware（文件系统、子智能体、上下文压缩、技能、权限），把"裸 agent"变成一个完整的 agent harness。
- 任何 LangGraph 编译后的图都可以作为 DeepAgents 的子智能体传入，实现自定义编排与 DeepAgents 默认行为的混合。

什么时候用什么层：

| 场景 | 用什么 |
|---|---|
| 需要 planning、context 管理、子智能体委派 | **DeepAgents** |
| 只需要一个简单 tool-calling 循环 | LangChain `create_agent` |
| agent 循环不是你想要的形状，需要自定义图 | LangGraph |
| 需要监控、评估、trace | LangSmith（可与上面任何层搭配） |

### 1.3 核心能力一览

| 能力 | 说明 |
|---|---|
| 文件系统 | 内置 `ls / read_file / write_file / edit_file / glob / grep`，支持多种可插拔后端 |
| 子智能体 | 主 agent 通过 `task` 工具委派任务给拥有独立上下文的子 agent |
| 上下文管理 | 自动摘要长对话，超大工具输出自动转存到文件系统 |
| Shell 执行 | 通过 Sandbox 后端提供 `execute` 工具 |
| 持久记忆 | 可插拔的状态和存储后端，支持跨会话记忆 |
| Human-in-the-Loop | 工具调用或文件操作前暂停，等待人工审批/编辑/拒绝 |
| Skills | 可复用的行为模板，按需加载，渐进式披露 |
| 结构化输出 | 主 agent 和子 agent 均支持 Pydantic 模型作为输出 schema |
| MCP 工具 | 可接入任意 MCP server 作为工具 |

### 1.4 安装

```bash
# 推荐
uv add deepagents

# 或者
pip install deepagents
```

要求 Python >= 3.11, < 4.0。

---

## 第二章：架构与中间件协议

DeepAgents 的一切能力都由**中间件栈（middleware stack）**提供。理解这个栈，就理解了 DeepAgents 的全部。

### 2.1 中间件栈的完整顺序

当你调用 `create_deep_agent()` 时，框架会按以下顺序组装中间件：

```
┌─ 基础栈（Base stack）────────────────────────────────┐
│ 1. SkillsMiddleware          （仅当传入 skills）      │
│ 2. FilesystemMiddleware      （始终存在）             │
│ 3. SubAgentMiddleware        （有子智能体时存在）      │
│ 4. SummarizationMiddleware   （始终存在）             │
│ 5. PatchToolCallsMiddleware  （始终存在）             │
│ 6. AsyncSubAgentMiddleware   （有异步子智能体时存在）   │
│ 7. 你的自定义 middleware       （插入到这里）           │
├─ 尾部栈（Tail stack）────────────────────────────────┤
│ 8. Harness profile 额外中间件                          │
│ 9. 工具排除过滤（excluded_tools）                      │
│ 10. AnthropicPromptCachingMiddleware（非 Anthropic noop）│
│ 11. BedrockPromptCachingMiddleware（未装则跳过）        │
│ 12. FireworksPromptCachingMiddleware（未装则跳过）      │
│ 13. MemoryMiddleware         （仅当传入 memory）       │
│ 14. HumanInTheLoopMiddleware （仅当传入 interrupt_on）  │
└──────────────────────────────────────────────────────┘
```

关键点：

- **你的 middleware 插在位置 7**，在核心中间件之后、prompt caching 和 memory 之前。
- 如果你的 middleware 实例的 `.name` 与某个内置中间件相同，它会**原地替换**该内置实例，而不是追加。
- 某些核心中间件（`FilesystemMiddleware`、`SubAgentMiddleware`、`PatchToolCallsMiddleware`）受框架保护，不能通过 `excluded_middleware` 移除。

### 2.2 核心中间件详解

#### FilesystemMiddleware

始终存在。提供以下工具：

| 工具 | 功能 |
|---|---|
| `ls(path)` | 列出目录内容 |
| `read_file(file_path, offset, limit)` | 读取文件，支持分页和多模态（图片/音频/视频） |
| `write_file(file_path, content)` | 创建新文件（仅创建，不覆盖） |
| `edit_file(file_path, old_string, new_string, replace_all)` | 精确字符串替换 |
| `delete(file_path)` | 删除文件（需要后端支持） |
| `glob(pattern, path)` | 模式匹配查找文件 |
| `grep(pattern, path, glob)` | 文本搜索（优先使用 ripgrep） |
| `execute(command, timeout)` | 执行 shell 命令（仅当后端实现 SandboxBackendProtocol） |

它还负责**大工具结果的自动转存**：
- 默认 20000 token 以上的工具输出会被转存到文件系统（路径如 `/large_tool_results/`），上下文中只保留摘要和文件路径。
- 用户消息超过 50000 token 也会被转存。

#### SubAgentMiddleware

有子智能体时存在。提供 `task` 工具，主 agent 用它委派任务给子 agent。子 agent 拥有**完全隔离的上下文窗口**——主 agent 只看到子 agent 的最终输出。

#### SummarizationMiddleware

始终存在。当对话 token 数超过阈值时，自动将旧消息压缩为摘要，完整历史转存到文件系统（路径如 `/conversation_history/`）。阈值的默认值会根据模型的最大输入 token 自动计算，回退方案是固定保留最近 20 条消息。

#### PatchToolCallsMiddleware

始终存在。修复消息历史中悬空的工具调用（例如 agent 在中断后恢复、或收到格式错误的 tool-call 参数时），确保消息流的一致性。

#### SkillsMiddleware

仅当传入 `skills` 参数时存在。将技能目录中的 `SKILL.md` 元数据（name + description）注入系统提示词，让 agent 知道有哪些技能可用。Agent 判断当前任务匹配某个技能时，会主动读取该技能的完整指令。

#### MemoryMiddleware

仅当传入 `memory` 参数时存在。在 agent 启动时加载指定的 `AGENTS.md` 文件内容，追加到系统提示词中。这是 DeepAgents 的"启动记忆"机制。

#### HumanInTheLoopMiddleware

仅当传入 `interrupt_on` 或 permissions 中有 `mode="interrupt"` 的规则时存在。在指定的工具调用前暂停执行，返回中断信息，等待人工决策（approve / edit / reject / respond）。

### 2.3 系统提示词的组装

最终发给模型的 system prompt 由三部分拼接而成（用空行分隔）：

```
system_prompt = USER → BASE → SUFFIX
```

- **USER**：你传入的 `system_prompt` 参数。
- **BASE**：由当前 HarnessProfile 定义（通常为空，或包含模型特定的基础指令）。
- **SUFFIX**：由当前 HarnessProfile 定义的可选后缀指令。

大部分时候你只需要关心 `system_prompt` 参数。`BASE` 和 `SUFFIX` 是框架层面为不同模型提供的默认调优，一般不需要动。

### 2.4 HarnessProfile

HarnessProfile 是"每个模型的默认调优配置包"。当你传入一个模型时，框架会自动解析对应的 profile，决定：

- 额外的中间件（如 Anthropic prompt caching、Bedrock prompt caching）
- 是否禁用某些内置工具（`excluded_tools`）
- 是否排除某些中间件（`excluded_middleware`）
- 额外的系统提示词内容

大部分使用场景不需要手动创建 profile。框架会根据模型类型自动选择。

---

## 第三章：`create_deep_agent` 完整签名

这是 DeepAgents 最核心的函数，理解了每个参数，就理解了整个框架的入口。

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=...,           # 模型
    tools=...,           # 自定义工具
    system_prompt=...,   # 系统提示词
    middleware=...,      # 额外中间件
    subagents=...,       # 子智能体配置
    skills=...,          # 技能目录路径
    memory=...,          # AGENTS.md 记忆文件路径
    permissions=...,     # 文件系统权限规则
    backend=...,         # 文件系统后端
    interrupt_on=...,    # 人工审批的工具名映射
    response_format=..., # 结构化输出 schema
    state_schema=...,    # 自定义图状态 schema
    context_schema=...,  # 运行时上下文 schema
    checkpointer=...,    # LangGraph checkpointer（持久化）
    store=...,           # LangGraph store（跨会话存储）
    debug=...,           # 调试模式
    name=...,            # 图的名称
    cache=...,           # 缓存
)
```

### 3.1 `model` 参数

接受三种形式：

```python
# 1. 字符串（推荐——使用 provider:model 格式）
agent = create_deep_agent(model="openai:gpt-5.5")

# 2. 预初始化的 LangChain ChatModel 实例
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-5.5", temperature=0)
agent = create_deep_agent(model=model)

# 3. 传入 None（已弃用，默认是 claude-sonnet-4-6）
# 从 0.5.3 开始弃用，将在 1.0.0 中移除
```

`provider:model` 字符串由 LangChain 的 `init_chat_model` 函数解析。支持的 provider 包括：`openai`, `anthropic`, `google_genai`, `aws`, `azure_openai`, `ollama`, `fireworks`, `together`, `mistral`, `groq`, `xai` 等。

#### 重要：OpenAI 模型的 Responses API 默认行为

从 DeepAgents 0.6.x 开始，如果你使用 OpenAI 模型，**默认走 Responses API**（不是 Chat Completions）。这是因为 Responses API 支持 OpenAI 的内置工具（web search、code interpreter 等）。

如果你想强制走 Chat Completions：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-5.5", use_responses_api=False)
agent = create_deep_agent(model=model)
```

如果你想用 Responses API 但禁用服务端数据保留：

```python
model = init_chat_model(
    "openai:gpt-5.5",
    use_responses_api=True,
    store=False,
    include=["reasoning.encrypted_content"],
)
agent = create_deep_agent(model=model)
```

#### 接入阿里云百炼（DashScope）

百炼提供 OpenAI 兼容端点，走 Chat Completions 协议：

```python
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

model = ChatOpenAI(
    model="qwen-plus",  # 或 qwen3-max、qwen-max 等
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

agent = create_deep_agent(model=model, tools=[my_tools])
```

如果需要百炼的 `web_search` 等服务端内置工具，有两种策略：

1. **在 tools 中包装**：把百炼 Responses API 的 web_search 调用封装为一个普通 function tool，DeepAgents 通过 tool calling 调用它。
2. **直接用 Responses API**：绕过 DeepAgents，直接调用百炼的 Responses API（失去 DeepAgents 的 harness 能力）。

### 3.2 `tools` 参数

传入模型可以调用的自定义工具。这些工具与内置工具**合并**（additive），不会替换内置工具：

```python
from langchain.tools import tool

@tool
def search_database(query: str) -> str:
    """搜索产品数据库，返回匹配结果"""
    return db.search(query)

@tool
def generate_report(data: dict) -> str:
    """根据数据生成分析报告"""
    return report_gen.run(data)

agent = create_deep_agent(model=model, tools=[search_database, generate_report])
```

要移除内置工具，需要使用 HarnessProfile 的 `excluded_tools` 机制，而不是简单地不传。

### 3.3 `system_prompt` 参数

你自定义的系统提示词。可以是字符串或 `SystemMessage`：

```python
agent = create_deep_agent(
    model=model,
    system_prompt="你是一个数据分析助手。在给出结论之前，先用 Python 工具验证数据。",
)
```

如果传入 `SystemMessage`，会保留其上的 `cache_control` 标记（用于 Anthropic prompt caching 的显式断点）。

### 3.4 `response_format` 参数

让 agent 的最终输出符合指定的结构化 schema：

```python
from pydantic import BaseModel, Field

class ResearchReport(BaseModel):
    """研究报告的结构化输出"""
    title: str = Field(description="报告标题")
    summary: str = Field(description="核心发现摘要")
    key_findings: list[str] = Field(description="关键发现列表")
    confidence: float = Field(description="置信度 0-1")
    sources: list[str] = Field(description="参考来源")

agent = create_deep_agent(
    model=model,
    tools=[web_search],
    response_format=ResearchReport,
)

result = agent.invoke({"messages": [{"role": "user", "content": "调研 LangGraph 的最新特性"}]})

# 访问结构化输出
report = result["structured_response"]
print(report.title)
print(report.confidence)
```

`response_format` 接受：
- Pydantic `BaseModel` 子类
- Python `dataclass`
- `TypedDict`
- JSON Schema 字典
- `ToolStrategy(schema)`：通过 tool calling 提取
- `ProviderStrategy(schema)`：使用 provider 原生结构化输出
- `AutoStrategy(schema)`：自动选择最佳策略

### 3.5 `checkpointer` 与持久化

DeepAgents 底层是 LangGraph，所以天然支持持久化：

```python
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    model=model,
    tools=tools,
    checkpointer=MemorySaver(),  # 内存持久化
)

# 使用 thread_id 区分不同会话
config = {"configurable": {"thread_id": "user-123-session-456"}}
result = agent.invoke({"messages": [...]}, config=config)
```

生产环境使用 PostgreSQL 或 SQLite：

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgresql://...")
agent = create_deep_agent(model=model, checkpointer=checkpointer)
```

文件系统（`StateBackend`）的内容也会随 checkpoint 持久化——同一 thread 内跨多轮对话，文件不会丢失。


---

## 第四章：文件系统与后端

DeepAgents 内置的文件系统是一个**虚拟文件系统**（VFS）。它不是直接操作你的操作系统文件，而是通过**后端协议（backend protocol）**抽象，让文件操作落到不同的存储介质上。

### 4.1 内置工具

| 工具名 | 签名 | 说明 |
|---|---|---|
| `ls` | `ls(path: str) -> list[str]` | 列出目录内容 |
| `read_file` | `read_file(file_path: str, offset: int = 0, limit: int = 500) -> str` | 读取文件内容，支持偏移和限制 |
| `write_file` | `write_file(file_path: str, content: str) -> str` | 创建新文件（仅创建，不能覆盖已有文件） |
| `edit_file` | `edit_file(file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> str` | 精确字符串替换 |
| `delete` | `delete(file_path: str) -> str` | 删除文件（需要后端支持删除操作） |
| `glob` | `glob(pattern: str, path: str = "/") -> list[str]` | 模式匹配查找 |
| `grep` | `grep(pattern: str, path: str = "/", glob: str = None) -> list[str]` | 内容搜索（优先使用 ripgrep） |
| `execute` | `execute(command: str, timeout: int = 300) -> str` | 执行 shell 命令（仅当后端实现 SandboxBackendProtocol） |

### 4.2 后端协议

DeepAgents 的文件后端遵循 `BackendProtocol`。核心方法是：

```python
class BackendProtocol(Protocol):
    def ls(self, path: str) -> list[str]: ...
    def read(self, file_path: str, offset: int = None, limit: int = None) -> str: ...
    def write(self, file_path: str, content: str) -> None: ...
    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> None: ...
    def delete(self, file_path: str) -> None: ...
    def glob(self, pattern: str, path: str = "/") -> list[str]: ...
    def grep(self, pattern: str, path: str = "/", glob: str = None) -> list[str]: ...
```

如果后端实现了 `SandboxBackendProtocol`（继承自 BackendProtocol，额外要求 `execute` 方法），就会额外暴露 `execute` 工具。

### 4.3 StateBackend（默认）

**StateBackend** 是默认后端。文件内容直接存储在 LangGraph 的 state 中：

```python
# 不传 backend 参数，默认使用 StateBackend
agent = create_deep_agent(model=model, tools=tools)

# 文件存在 state["files"] 字典中，key 是路径，value 是内容字符串
result = agent.invoke({"messages": [{"role": "user", "content": "写一个 hello.py"}]})
print(result["files"])  # {"/hello.py": "print('hello world')"}
```

特点：
- 文件随 checkpoint 持久化，同一 thread 内跨会话不丢失。
- **跨 thread 不共享**（每个 thread 有独立的 state）。
- 无需外部依赖。
- 适合快速原型和不需要真正落盘的场景。

### 4.4 CompositeBackend

CompositeBackend 允许你把不同路径前缀路由到不同后端，实现"混合存储"：

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, SandboxBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/workspace": StateBackend(),
        "/artifacts": StoreBackend(store=my_store, namespace=("artifacts",)),
        "/memory": StoreBackend(store=my_store, namespace=("agent_memory",)),
        "/sandbox": SandboxBackend(root_dir="/tmp/agent_sandbox", timeout=60),
        "/data": CompositeBackend.FilesystemBackend(root_dir="/path/to/shared_data"),
    },
)

agent = create_deep_agent(model=model, backend=backend)
```

### 4.5 SandboxBackend

SandboxBackend 允许 agent 在一个受控的目录中执行 shell 命令：

```python
from deepagents import create_deep_agent
from deepagents.backends import SandboxBackend

backend = SandboxBackend(
    root_dir="/tmp/agent_workspace",
    timeout=120,          # 命令超时（秒）
    max_output_size=50000,
)

agent = create_deep_agent(model=model, backend=backend)

# agent 可以调用 execute("pip install requests") 或 execute("python analysis.py")
```

实现 `SandboxBackendProtocol` 后，`execute` 工具会自动暴露给 agent。

### 4.6 FilesystemBackend（本地真实文件系统）

如果你想让 agent 直接操作本地磁盘（例如代码编辑、数据处理），可以使用 FilesystemBackend：

```python
from deepagents.backends.filesystem import FilesystemBackend

backend = FilesystemBackend(root_dir="/Users/zata/code/my-project")

agent = create_deep_agent(model=model, backend=backend)

# agent 可以 read_file / write_file / edit_file / glob / grep 操作真实文件
```

### 4.7 StoreBackend（跨会话存储）

StoreBackend 利用 LangGraph 的 Store 接口，将文件内容存储在一个跨 thread 共享的键值存储中：

```python
from langgraph.store.memory import InMemoryStore
from deepagents.backends import StoreBackend

store = InMemoryStore()
backend = StoreBackend(store=store, namespace=("shared_files",))

agent = create_deep_agent(model=model, backend=backend)

# 文件在不同 thread 之间共享（只要使用同一个 store）
```

生产环境搭配 PostgreSQL Store：

```python
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string("postgresql://...")
backend = StoreBackend(store=store, namespace=("knowledge_base",))
agent = create_deep_agent(model=model, backend=backend)
```

### 4.8 权限控制

通过 `permissions` 参数精细控制文件系统访问：

```python
agent = create_deep_agent(
    model=model,
    backend=backend,
    permissions=[
        {"path": "/workspace/*", "operations": ["read", "write", "edit"], "mode": "allow"},
        {"path": "/memory/*", "operations": ["read", "write"], "mode": "allow"},
        {"path": "/system/*", "mode": "deny"},
        {"path": "/*", "operations": ["read"], "mode": "allow"},
        {"path": "/*", "operations": ["write", "edit", "delete"], "mode": "interrupt"},
    ],
)
```

权限模式：

| 模式 | 行为 |
|---|---|
| `allow` | 直接放行 |
| `deny` | 直接拒绝，返回错误信息给 agent |
| `interrupt` | 暂停执行，等待人工审批 |

权限规则按顺序匹配，第一条匹配的规则生效。

---

## 第五章：子智能体

子智能体是 DeepAgents 最有特色的能力之一。核心思想：主 agent 通过 `task` 工具把一个任务委派给一个拥有**独立上下文窗口**的子 agent。主 agent 只看到子 agent 的最终输出，不会看到子 agent 的中间过程。

这解决了长任务中的关键问题：**上下文污染**。当主 agent 执行搜索、阅读、分析等中间步骤时，会产生大量 token。如果这些 token 都堆在主 agent 的上下文里，很快就会超出限制或降低推理质量。子智能体隔离了这些噪音。

### 5.1 预配置子智能体

```python
from deepagents import create_deep_agent
from deepagents.subagents import SubAgent

researcher = SubAgent(
    name="research-agent",
    description="负责搜索和整理信息，输出结构化研究报告",
    system_prompt="你是一个信息研究员。用 web_search 和 read_file 工具完成调研任务。",
    model="openai:gpt-5.5",  # 子智能体可以用不同模型
    tools=[web_search],
)

analyst = SubAgent(
    name="data-analyst",
    description="负责数据分析和可视化",
    system_prompt="你是一个数据分析师。用 Python 分析数据，生成报告。",
    model="anthropic:claude-sonnet-4-6",
    tools=[execute_python, read_file],
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[researcher, analyst],
    system_prompt="你是一个团队负责人。用 task 工具委派任务给子智能体。",
)
```

当主 agent 判断需要调研时，会调用：

```json
{
  "tool": "task",
  "args": {
    "description": "调研 LangGraph 最新特性并输出报告",
    "subagent_type": "research-agent"
  }
}
```

### 5.2 自定义子智能体（传入编译后的 LangGraph）

任何 LangGraph `CompiledStateGraph` 都可以作为子智能体传入：

```python
from langgraph.graph import StateGraph, MessagesState, END

# 构建一个自定义图
workflow = StateGraph(MessagesState)
workflow.add_node("analyze", analyze_node)
workflow.add_node("report", report_node)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "report")
workflow.add_edge("report", END)
custom_graph = workflow.compile()

agent = create_deep_agent(
    model=model,
    subagents=[
        {
            "name": "custom-analyst",
            "description": "自定义分析管道",
            "graph": custom_graph,
        }
    ],
)
```

### 5.3 主/子上下文隔离原理

```
主 Agent 上下文                          子 Agent 上下文
┌─────────────────────┐                ┌─────────────────────────────┐
│ system prompt       │                │ 子智能体的 system prompt     │
│ user message        │                │ task description (作为输入) │
│ ... 历史消息 ...     │                │ 子智能体的工具和文件系统      │
│ tool: task(...)     │──委派──────────→│                             │
│                     │                │  (子 agent 内部循环)         │
│                     │←───────────────│ 最终输出（文本摘要）         │
│ tool result         │                └─────────────────────────────┘
│ ... 继续 ...        │
└─────────────────────┘
```

- 子 agent 看不到主 agent 的对话历史，只看到任务描述。
- 主 agent 看不到子 agent 的中间 tool calls、搜索结果、文件内容。
- 子 agent 的文件系统与主 agent **共享**（默认使用同一个 backend）。
- 如果子 agent 需要向主 agent 传递大文件，通过文件系统写入，主 agent 用 `read_file` 读取。

### 5.4 什么时候用子智能体

| 场景 | 是否需要子智能体 |
|---|---|
| 简单搜索 + 回答 | 不需要，一个 agent + web_search 就够 |
| 多步调研：搜索多个主题、阅读多个来源、综合报告 | 需要——用 researcher 子智能体隔离搜索噪音 |
| 多文件代码修改 | 需要——用 coder 子智能体隔离文件操作 |
| 多源数据采集和分析 | 需要——不同子智能体处理不同数据源 |
| 单一任务，不需要委派 | 不需要，直接用主 agent |

### 5.5 异步子智能体：并行委派

DeepAgents 同时提供同步和异步两套接口。当需要并行处理多个独立任务时，可以在异步运行环境中用 `asyncio.gather` 同时发起多个调用，每个子智能体在自己的隔离上下文中工作，主流程只汇总最终结果。

```python
import asyncio

# 同一 agent 的多个独立任务并行执行
results = await asyncio.gather(
    agent.ainvoke({"messages": [("user", "研究主题 A")]}, config),
    agent.ainvoke({"messages": [("user", "研究主题 B")]}, config),
)
```

如果子智能体内部执行的是 I/O 密集操作（网络搜索、文件读写），并行能显著缩短总耗时。注意每个并行调用会消耗独立的模型调用和 token 配额；`asyncio.gather` 默认在任一任务异常时取消全部，生产代码建议加 `return_exceptions=True` 后逐个检查。

### 5.6 多级子智能体

子智能体的 `subagents` 字段可以继续传入子智能体配置，形成"主 agent → 一级子 agent → 二级子 agent"的层级结构。每一层都有独立的上下文窗口，适合大型项目中"项目经理 → 领域专家 → 执行者"的分工模式。

```python
deep_researcher = SubAgent(
    name="deep-researcher",
    model="openai:gpt-5.5",
    system_prompt="深入研究并写报告",
    subagents={
        "subagents": [
            SubAgent(
                name="fact-checker",
                model="openai:gpt-5.5",
                system_prompt="验证研究结论中的关键事实",
            ),
        ],
    },
)
```

层级不宜过深（建议不超过 2-3 层）：每加一层，主 agent 看到的信息就更间接，且 token 消耗按乘数增长。

---

## 第六章：上下文管理

DeepAgents 内置了两层上下文管理机制：**摘要压缩**和**大工具输出转存**。

### 6.1 SummarizationMiddleware：对话摘要压缩

当对话的 token 数超过阈值时，SummarizationMiddleware 会：

1. 将旧消息替换为一条摘要消息
2. 将完整的旧消息转存到文件系统（路径如 `/conversation_history/{message_id}.json`）
3. 保留最近的消息在上下文中

```
压缩前：
[sys] [msg1] [msg2] [msg3] [msg4] [msg5] ... [msgN]
       ↑ 全部保留在上下文中

压缩后：
[sys] [摘要消息（包含历史概要+文件路径）] [msgN-2] [msgN-1] [msgN]
                              ↑ 完整历史在 /conversation_history/
```

阈值配置：

```python
from deepagents import create_deep_agent
from deepagents.middleware.summarization import SummarizationMiddleware

agent = create_deep_agent(
    model=model,
    tools=tools,
    middleware=[
        SummarizationMiddleware(
            token_threshold=100000,   # 超过 100k token 触发压缩
            keep_messages=10,          # 保留最近 10 条消息
        )
    ],
)
```

阈值默认值根据模型的最大输入 token 自动计算。例如：
- GPT-5（128k context）→ 阈值约 100k token
- Claude（200k context）→ 阈值约 160k token
- 回退方案：保留最近 20 条消息

### 6.2 大工具输出转存

FilesystemMiddleware 监控所有工具的输出。当输出超过阈值（默认 20000 token）时：

1. 将完整输出写入文件系统（路径如 `/large_tool_results/{tool_call_id}.txt`）
2. 在上下文中只保留摘要消息：`[输出过大，已转存到 /large_tool_results/xxx.txt，请用 read_file 读取]`

```python
# 你可以自定义阈值
from deepagents.middleware.filesystem import FilesystemMiddleware

fs_mw = FilesystemMiddleware(
    large_output_threshold=10000,  # 10000 token 超限
    large_output_dir="/my_tool_results",
)

agent = create_deep_agent(model=model, middleware=[fs_mw])
```

### 6.3 记忆与跨会话

通过 `memory` 参数加载 AGENTS.md：

```python
agent = create_deep_agent(
    model=model,
    tools=tools,
    memory="/path/to/AGENTS.md",  # 启动时注入到系统提示词
)
```

对于需要动态更新的长期记忆，使用 StoreBackend：

```python
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
memory_backend = StoreBackend(store=store, namespace=("agent_memory",))

agent = create_deep_agent(
    model=model,
    backend=memory_backend,
    system_prompt="你是一个有记忆的助手。在 /memory 目录中维护长期记忆。",
)
```

Agent 可以通过文件工具读写 `/memory/` 目录，实现跨会话的记忆更新。

---

## 第七章：Skills（技能系统）

Skills 是 DeepAgents 的渐进式披露机制——将复杂的指令和工具组合打包成可复用的模块，按需加载。

### 7.1 基本用法

每个技能是一个目录，包含一个 `SKILL.md` 文件：

```
my_skills/
├── code-review/
│   └── SKILL.md
├── data-viz/
│   ├── SKILL.md
│   └── templates/
│       └── chart.py
└── web-research/
    └── SKILL.md
```

`SKILL.md` 的格式：

```markdown
---
name: code-review
description: 对代码库进行系统性审查，检查安全性、性能、可维护性
---

## 步骤

1. 读取目标文件列表（用 glob 工具）
2. 逐一读取关键文件
3. 检查以下方面：
   - 安全性：SQL注入、XSS、不安全的反序列化
   - 性能：N+1 查询、内存泄漏、不必要的全表扫描
   - 可维护性：函数长度、重复代码、缺失的类型注解
4. 用 write_file 工具输出审查报告到 /reports/code-review-{date}.md

## 工具

优先使用 grep 搜索特定模式，用 read_file 读取上下文。
```

```python
agent = create_deep_agent(
    model=model,
    tools=tools,
    skills="/path/to/my_skills",
)
```

SkillsMiddleware 会将每个技能的 `name` 和 `description` 注入系统提示词。Agent 判断当前任务匹配某个技能时，会主动 `read_file` 读取该技能的完整指令。

### 7.2 为什么是"渐进式披露"

如果所有技能的完整内容都塞在系统提示词里，token 浪费严重。渐进式披露的设计是：

- **系统提示词只包含元数据**（name + description），几十个 token 每技能。
- **完整指令在文件系统中**，agent 按需读取。
- 10 个技能的元数据 ≈ 300 token，比全量内容（可能几千 token）节省 90% 以上。

### 7.3 带资源的技能

技能目录中可以包含额外文件（模板、脚本、配置等），agent 可以通过文件系统工具访问：

```
my_skills/
└── report-generator/
    ├── SKILL.md
    ├── templates/
    │   ├── report_template.md
    │   └── chart_template.py
    └── config.yaml
```

Agent 读取 `SKILL.md` 后，可以根据指令进一步读取 `templates/` 中的文件。

### 7.4 社区技能示例：研究评估评分标准

官方仓库提供了多个可复用的技能示例。下面是一个"研究评估"技能（rubrics 模式）的典型结构——把评审专家的评分维度固化成可复用的指令文件：

```markdown
---
name: evaluate-research
description: 用评分标准评估研究报告质量
---

## 评分标准

按以下维度评估研究报告（每项 1-5 分）：

1. **事实准确性**：关键事实是否有可靠来源支撑
2. **逻辑连贯性**：结论是否从证据自然推出
3. **完整性**：是否遗漏了重要角度
4. **可操作性**：读者能否据此做出决策

## 流程

1. 阅读研究报告全文
2. 逐项打分并给出具体依据
3. 汇总总分和改进建议
```

将此文件放入技能目录后，agent 在收到"评估报告"类任务时会自动加载该技能。你可以基于自己的领域编写类似的评分模板——技能系统的本质就是把"怎么做"的专家知识封装成可复用的指令文件。

---

## 第八章：Human-in-the-Loop（人机协作）

DeepAgents 允许在工具调用前暂停，等待人工决策。这在生产环境中至关重要——你不希望 agent 在没有人工审核的情况下执行危险操作（删除文件、发送邮件、执行数据库变更等）。

### 8.1 `interrupt_on` 参数

```python
agent = create_deep_agent(
    model=model,
    tools=[send_email, delete_record, web_search, write_file],
    interrupt_on={
        "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
        "delete_record": {"allowed_decisions": ["approve", "reject"]},
    },
)

# 第一次 invoke 会触发中断
result = agent.invoke({"messages": [...]})

# 检查是否中断
if result["__interrupt__"]:
    # 获取中断信息
    interrupt_info = result["__interrupt__"][0]
    print(f"工具: {interrupt_info.value['action_request']['action']}")
    print(f"参数: {interrupt_info.value['action_request']['args']}")

    # 人工决策
    human_decision = interrupt_info.value["resume"]
    # 或者用 resume 重新启动
    resumed = agent.invoke(
        {"__interrupt__": [{"resume": {"type": "accept"}}]},
        config=config,
    )
```

### 8.2 通过 permissions 实现文件操作审批

```python
agent = create_deep_agent(
    model=model,
    backend=backend,
    permissions=[
        {"path": "/workspace/*", "mode": "allow"},
        {"path": "/*", "operations": ["write", "edit", "delete"], "mode": "interrupt"},
    ],
)
```

所有 workspace 外的写操作都会触发人工审批。

### 8.3 中断恢复协议

DeepAgents 的 HITL 基于 LangGraph 的 interrupt 机制。中断后：

1. 图的状态（包括 messages、files）已通过 checkpointer 保存。
2. `agent.invoke()` 返回 `__interrupt__` 信息。
3. 人工决策通过 `agent.invoke()` resume：

```python
config = {"configurable": {"thread_id": "session-1"}}

# 第一次调用，触发中断
result1 = agent.invoke({"messages": [...]}, config=config)

# 检查中断并恢复
if "__interrupt__" in result1:
    decision = input("批准/编辑/拒绝？(approve/edit/reject): ")
    result2 = agent.invoke(
        Command(resume={"type": decision}),
        config=config,
    )
```

支持的决策类型：

| 决策 | 行为 |
|---|---|
| `{"type": "accept"}` | 批准，继续执行工具调用 |
| `{"type": "edit", "args": {...}}` | 编辑参数后继续执行 |
| `{"type": "reject", "message": "..."}` | 拒绝，将拒绝理由传回给 agent |
| `{"type": "respond", "message": "..."}` | 不执行工具，向 agent 提供额外信息 |

---

## 第九章：流式输出与中间过程

DeepAgents 基于 LangGraph，支持多种流式模式：

### 9.1 流式 token

```python
from langchain_core.messages import AIMessageChunk

config = {"configurable": {"thread_id": "session-1"}}

for event in agent.stream(
    {"messages": [{"role": "user", "content": "分析这份数据"}]},
    config=config,
    stream_mode="messages",
):
    # event 是 (message_chunk, metadata) 元组
    msg_chunk, metadata = event
    if hasattr(msg_chunk, "content") and isinstance(msg_chunk.content, str):
        print(msg_chunk.content, end="", flush=True)
```

### 9.2 流式工具调用

```python
for event in agent.stream(
    input_data,
    config=config,
    stream_mode="updates",
):
    # 每个节点的更新
    for node_name, node_update in event.items():
        print(f"节点: {node_name}")
        if "messages" in node_update:
            for msg in node_update["messages"]:
                print(f"  {msg.type}: {msg.content[:100] if isinstance(msg.content, str) else msg.content}")
```

### 9.3 流式文件操作

通过 `stream_mode="updates"`，可以看到文件系统的变化：

```python
for event in agent.stream(
    input_data,
    config=config,
    stream_mode="updates",
):
    for node_name, node_update in event.items():
        if "files" in node_update:
            print(f"文件变化: {node_update['files'].keys()}")
```

---

## 第十章：生产部署

### 10.1 部署选项

| 方案 | 适用场景 |
|---|---|
| LangGraph Platform | 托管部署，LangSmith 集成，自动扩缩 |
| Docker + 自建 | 需要完全控制的私有化部署 |
| Serverless（Vercel/Modal/Cloud Run） | 事件驱动、低流量场景 |
| LangSmith Deployment | 与 LangSmith 评估和监控深度集成 |

### 10.2 Docker 部署示例

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# 安装依赖
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动（LangGraph serve）
CMD ["uv", "run", "langgraph", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.3 环境变量

```bash
# 模型 API Key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# LangSmith（可选，但强烈推荐）
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=my-agent

# 数据库（生产 checkpointer）
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### 10.4 安全模型

DeepAgents 遵循"信任 LLM"模型。Agent 可以做任何工具允许的事情。安全边界必须在你这一侧强制执行：

- **后端层面**：使用 SandboxBackend 或 FilesystemBackend 的 `root_dir` 限制 agent 能访问的目录。
- **权限层面**：使用 `permissions` 参数控制读写和删除操作。
- **工具层面**：不要暴露你不想让 agent 执行的工具。
- **HITL 层面**：对危险操作（删除、发送、支付）设置 `interrupt_on`。
- **网络层面**：如果 agent 有 web 访问能力，确保它不能访问内网端点。

### 10.5 可观测性

LangSmith 集成：

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=your_key
export LANGSMITH_PROJECT=production-agent
```

设置环境变量后，所有 agent 调用自动产生 trace。无需改代码。

### 10.6 评测

```python
from langsmith import Client

client = Client()

# 创建评测数据集
dataset = client.create_dataset("deep-agents-eval")
client.create_examples(
    dataset_id=dataset.id,
    inputs=[
        {"messages": [{"role": "user", "content": "调研 X 并写报告"}]},
        {"messages": [{"role": "user", "content": "修复 bug #123"}]},
    ],
)

# 运行评测
client.evaluate(
    agent,
    data=dataset.id,
    evaluators=[
        # 自定义评估器
        lambda outputs, reference: {"accuracy": compute_match(outputs, reference)},
    ],
)
```

---

## 第十一章：实战模式

### 11.1 研究智能体

```python
from deepagents import create_deep_agent
from deepagents.subagents import SubAgent
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """搜索互联网获取信息"""
    # 接入 Tavily / Bocha / 百炼 WebSearch MCP
    ...

@tool
def web_extract(url: str) -> str:
    """抽取网页正文内容"""
    ...

research_subagent = SubAgent(
    name="researcher",
    description="搜索和整理信息",
    system_prompt="你是一个信息研究员。用 web_search 和 web_extract 完成调研。",
    model="openai:gpt-5.5",
    tools=[web_search, web_extract],
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[research_subagent],
    system_prompt="""你是一个研究助手。
    收到调研任务后，用 task 工具委派给 researcher 子智能体。
    基于子智能体的输出，综合并生成最终回答。""",
)
```

### 11.2 代码智能体

```python
from deepagents.backends.filesystem import FilesystemBackend

backend = FilesystemBackend(root_dir="/path/to/repo")

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    system_prompt="""你是一个代码编辑助手。
    先用 glob 和 grep 了解代码库结构。
    修改代码前先 read_file 阅读上下文。
    修改后用 execute 工具运行测试验证。
    修改必须最小化，不要过度工程化。""",
)
```

### 11.3 数据分析智能体

```python
from deepagents.backends import SandboxBackend

backend = SandboxBackend(
    root_dir="/tmp/data_sandbox",
    timeout=300,
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=backend,
    system_prompt="""你是一个数据分析师。
    先用 execute("ls /") 查看数据文件。
    用 execute("python -c \"...\\"") 或 execute("head -n 100 data.csv") 探索数据。
    用 execute("python analysis.py") 执行分析脚本。
    用 write_file 生成分析报告。""",
)
```

### 11.4 混合模式：DeepAgents + 百炼 Responses API

当你需要 DeepAgents 的 harness 能力 + 百炼的 web_search：

```python
import os
from openai import OpenAI
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

# 百炼 Responses API 客户端（用于 web_search）
bailian = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

@tool
def bailian_web_search(query: str) -> str:
    """搜索互联网获取最新信息（使用百炼 web_search）"""
    response = bailian.responses.create(
        model="qwen3-max",
        input=query,
        tools=[{"type": "web_search"}],
    )
    # 提取搜索结果
    results = []
    for item in response.output:
        if getattr(item, "type", None) == "web_search_call":
            results.append(str(item))
        elif getattr(item, "type", None) == "message":
            for content in getattr(item, "content", []):
                if hasattr(content, "text"):
                    results.append(content.text)
    return "\n".join(results)

# DeepAgents 走 Chat Completions
model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

agent = create_deep_agent(
    model=model,
    tools=[bailian_web_search],
    system_prompt="你是一个研究助手。用 bailian_web_search 查询最新信息。",
)
```

---

## 第十二章：协议对比总结

### 12.0 Deep Agents Code（dcode）

除了可编程的 Python/JS 库，LangChain 还提供了 **Deep Agents Code**（`dcode`）——一个预构建的终端编码智能体，定位类似 Claude Code 或 Cursor CLI，底层就是 DeepAgents harness。它让你不用写代码就能体验文件系统、子智能体、上下文管理等全部能力。

```bash
# 一键安装
curl -LsSf https://langch.in/dcode | bash

# 在项目目录中启动
cd your-project
dcode
```

dcode 使用任何支持 tool calling 的 LLM 作为后端。对于想先"用"再"编"的用户，建议先试 dcode 感受 harness 行为，再用 `create_deep_agent` 定制自己的流程。

官方文档：<https://docs.langchain.com/deepagents-code>

### 12.1 DeepAgents 的模型协议

DeepAgents 对模型的唯一要求是 **tool calling**。它不关心底层是 Chat Completions 还是 Responses API，只要 LangChain ChatModel 能完成以下循环：

```
发送 [system, user, assistant(tool_calls), tool(results)] → 模型返回 tool_calls 或 text → 循环
```

- Chat Completions 兼容端点（OpenAI、DashScope、Ollama、vLLM）：直接用 `ChatOpenAI`。
- Responses API（OpenAI / 百炼）：通过 `init_chat_model("openai:...", use_responses_api=True)`。
- Anthropic：直接用 `ChatAnthropic` 或 `"anthropic:claude-sonnet-4-6"`。
- 本地模型：`ChatOllama` 或 `ChatVLLM`。

### 12.2 与百炼 Responses API 的关系

| 维度 | DeepAgents + Chat Completions | 百炼 Responses API |
|---|---|---|
| 协议 | Chat Completions（`messages`） | Responses（`input`） |
| 工具调用 | 客户端执行（LangChain tool calling） | 服务端内置（web_search 等） |
| Agent 循环 | DeepAgents 框架管 | 你自己管 |
| 搜索 | 需要自己包装工具 | 服务端内置 |
| 文件系统 | 内置 | 无 |
| 子智能体 | 内置 | 无 |
| 上下文管理 | 内置 | 无 |
| HITL | 内置 | 无 |

### 12.3 选型决策树

```
需要 DeepAgents 的 harness 能力？
├─ 是 → 需要 web_search？
│   ├─ 是 → 自己包装搜索为 function tool（推荐）
│   │       或混合模式（DeepAgents + 百炼 Responses API）
│   └─ 否 → 直接用 DeepAgents + Chat Completions
└─ 否 → 需要服务端内置工具（web_search 等）？
    ├─ 是 → 直接用百炼 Responses API
└─ 否 → LangChain create_agent / LangGraph
```

### 12.4 RubricMiddleware：自评迭代循环

DeepAgents 内置了 `RubricMiddleware`，让你用"评分标准"定义**什么叫做完成**。当 agent 准备结束回复时，中间件会调用一个独立的"评分器"子智能体，根据 rubric 逐条检查 agent 的输出。如果评分器返回 `needs_revision`，其反馈会作为 `HumanMessage` 注入上下文，agent 循环继续——直到评分器返回 `satisfied`、`failed` 或达到最大迭代次数。

```python
from deepagents import create_deep_agent
from deepagents.middleware import RubricMiddleware

rubric_mw = RubricMiddleware(
    rubric=[
        {"criterion": "所有关键论断都有来源引用", "weight": 3},
        {"criterion": "结论与证据逻辑一致", "weight": 2},
        {"criterion": "无事实错误", "weight": 3},
    ],
    grader_model="openai:gpt-5.5",
    max_iterations=3,
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[rubric_mw],
    system_prompt="你是一个研究助手，写完报告后自我检查再提交。",
)
```

这个模式非常适合对输出质量有硬性要求的场景（合规文档、技术报告、代码审查），把"人工再审一遍"变成可编程的自动质量门。

### 12.5 官方示例集导读

GitHub 仓库的 [examples/](https://github.com/langchain-ai/deepagents/tree/main/examples) 目录包含十多个端到端案例，按学习优先级推荐如下：

| 示例 | 亮点 |
|---|---|
| `content-builder-agent` | 用 Memory + Skills + Subagents 三原语构建内容写作 agent，最适合入门 |
| `deep_research` | 完整的深度研究 agent（多轮搜索 + 报告生成），展示实际 token 管理 |
| `text-to-sql-agent` | 自然语言 → SQL，展示 planning + filesystem + subagent 组合 |
| `rubric_middleware` | RubricMiddleware + LangSmith trace，展示自评迭代全流程 |
| `async-subagent-server` | 异步子智能体 + 服务端部署，生产级 FastAPI 集成 |
| `ralph_mode` | Ralph 自主循环模式（Geoff Huntley），`while :; do agent; done` 的 DeepAgents 实现 |
| `better-harness` | 用一个 DeepAgent 优化另一个 agent harness 的元循环（harness engineering） |

建议先跑 `content-builder-agent` 理解三原语（Memory / Skills / Subagents），再按需深入其他案例。

---

## 附录

### A. 常用环境变量

| 变量 | 说明 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `DASHSCOPE_API_KEY` | 阿里云百炼 API key |
| `LANGSMITH_TRACING` | 启用 LangSmith trace |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGSMITH_PROJECT` | LangSmith 项目名 |
| `LANGCHAIN_TRACING_V2` | 启用 LangSmith trace（旧变量名） |
| `LANGCHAIN_API_KEY` | LangSmith API key（旧变量名） |
| `LANGCHAIN_PROJECT` | LangSmith 项目名（旧变量名） |

### B. 版本注意事项

- `deepagents` 0.7.x 是当前最新版本系列。
- 0.5.x → 0.6.x 有重大 API 变化（`SubAgent` 类型变化、`response_format` 新增）。
- 0.6.x → 0.7.x 新增了 skills、memory、permissions 等功能。
- 如果从 0.3.x 升级，`SubAgent` 已从 dict 改为类型化对象，`create_deep_agent` 的参数名有变化。
- 0.x 版本 API 变动快，生产环境建议锁定版本（`uv add deepagents==0.7.13`）。

#### 本文覆盖的版本快照（截至 2026-09-08）

| 包 | 本文基准版本 | 发布日期 | 备注 |
|---|---|---|---|
| `deepagents`（Python） | 0.7.13 | 2026-09-02 | 核心库，本文主体内容 |
| `deepagents-code`（dcode） | 0.1.66 | 2026-09-03 | 终端编码智能体，见 12.0 节 |
| `deepagents-talon` | 0.0.7 | 2026-09-07 | 独立发布，本文未覆盖 |
| `langchain-quickjs` | 0.3.7 | 2026-09-06 | JS 运行时，本文未覆盖 |
| `deepagents.js`（JS/TS） | — | — | 独立仓库，见附录 C |

#### 下次更新检查清单

1. 查看 [GitHub Releases](https://github.com/langchain-ai/deepagents/releases) 确认 `deepagents` 最新 minor 版本（当前 0.7.x；如果发布 0.8 或 1.0，优先检查 breaking changes）。
2. 对比 [CHANGELOG](https://github.com/langchain-ai/deepagents/blob/main/CHANGELOG.md)（或 release notes），重点看：
   - 新增/移除的中间件（`libs/deepagents/deepagents/middleware/` 目录）
   - `create_deep_agent` 签名变化
   - 新增的 examples 目录
3. 检查 `deepagents-code` 是否有新 major 功能（dcode 迭代很快，几乎每周发版）。
4. 确认本文引用的文档链接是否仍然有效（LangChain 文档路径经常重组）。
5. 如果有新的 middleware 或新的 examples，优先补充到第 2 章（中间件详解）和 12.5 节（示例导读）。

### C. 生态与跨语言

- **JavaScript/TypeScript**：DeepAgents 提供了 `deepagents.js` 库（[GitHub](https://github.com/langchain-ai/deepagentsjs)），适合在 Node.js 环境中构建 agent。
- **Deep Agents Code**：终端编码智能体，安装命令见 [12.0 节](#120-deep-agents-codedcode)。

### D. 相关资源

- [GitHub 仓库](https://github.com/langchain-ai/deepagents)
- [官方文档](https://docs.langchain.com/oss/python/deepagents/overview)
- [API Reference](https://reference.langchain.com/python/deepagents/)
- [示例代码](https://github.com/langchain-ai/deepagents/tree/main/examples)
- [LangChain 生态概览](https://docs.langchain.com/oss/python/concepts/products)

---

*本文基于 DeepAgents 0.7.13 版本编写，2026 年 9 月。API 在 1.0 之前可能变化，请以官方文档为准。*
