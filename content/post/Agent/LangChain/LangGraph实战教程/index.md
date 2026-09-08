---
title: LangGraph 实战：StateGraph、手写 ReAct 循环与 Map-Reduce 摘要
description: "从 State 与条件边，到亲手写一遍 tool-call 循环，再到完整的 ReAct 天气助手与长文本分块摘要图"
date: 2026-09-08T12:30:00+08:00
image: images/index/index.png
categories:
    - Agent
tags:
    - LangChain
---

# LangGraph 实战：StateGraph、手写 ReAct 循环与 Map-Reduce 摘要

LangChain 进入 1.x 之后，LangGraph 不再是"进阶选读"，而是整个框架的编排核心：官方一行式 `create_agent` 的底下就是一张 LangGraph 图，Agent 的决策、工具调用、记忆全在图上跑。看懂 LangGraph，基本等于看懂 Agent 本身。

这篇文章解决三件事。一是把 StateGraph、State、条件边这几个地基概念一次讲透；二是不用任何 Agent 封装，手写一遍 tool-call 循环——写完你会发现 Agent 没有魔法，它就是消息列表上转的一圈代码；三是用 LangGraph 把这个循环工程化成完整的 ReAct 天气助手，再补一个 Map-Reduce 长文本摘要图和记忆持久化。

文章由我 2025 年 5～6 月的三篇笔记（《Langchain-Graph实战教程》《LangChain-实战-Tools使用教程》《Langgraph使用教程》）整合而成。合并时修正了原笔记的几处真实 bug——条件边示例的构建顺序与路由映射错误、手动循环里对 `tool_call["args"]` 多加的一句 `json.loads`——过时 API 统一在文末版本注记里交代。全文示例模型走阿里云 DashScope 的 qwen 系（qwen-plus / qwen-max）OpenAI 兼容端点，只需要一个 `DASHSCOPE_API_KEY` 环境变量。

## 1. 基础三件套：StateGraph、State 与条件边

### 1.1 StateGraph：把应用建成一张状态机

`StateGraph` 把应用定义为状态机：节点（node）是执行单元，通常是普通 Python 函数；边（edge）决定流程如何在节点之间转换。构建一张图固定是四步：

1. 定义 State——图运行时传递的数据结构
2. `add_node` 添加节点
3. 连边：普通边写死流转，条件边动态路由，入口用 `START`
4. `compile()` 编译成可执行应用，之后用 `invoke` 跑

依赖安装一次说清：`pip install langchain langgraph langchain_openai`。

### 1.2 State 与 Annotated：覆盖还是追加

State 是一个 `TypedDict`，定义图的模式和状态更新方式。聊天场景下 State 通常只有一个键：`messages`。关键在 `add_messages` 这个 reducer 函数——它决定新消息是**追加**进列表，而不是覆盖列表：

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages 的类型是 "list"。`add_messages` 函数
    # 在注解中定义了如何更新这个状态键
    # （在这种情况下，它会将消息追加到列表中，而不是覆盖它们）
    messages: Annotated[list, add_messages]
```

`Annotated` 是 Python 类型提示系统的特殊类型，允许为类型附加元数据。在 LangGraph 里它承担两个职责：

- **类型定义**：第一个参数 `list` 表示 `messages` 字段是列表
- **行为定义**：第二个参数 `add_messages` 是 reducer 函数，定义这个键怎么更新——新消息到来时追加进现有列表，而不是整体替换

两种语义的区别直观感受一下：

```python
# 不使用 Annotated（默认行为：覆盖）
state = {"messages": ["消息1"]}
state["messages"] = ["消息2"]
# 结果：["消息2"]

# 使用 Annotated + add_messages
state = {"messages": ["消息1"]}
# 新消息到来时，add_messages 将其追加到列表
# 结果：["消息1", "消息2"]
```

这种设计在对话场景特别有用：保持对话历史、消息按顺序累积、不会意外覆盖。反过来，没有 reducer 注解的字段就是"最后一次写入覆盖"的语义——第 4 节 Map-Reduce 的流水线正好要靠这个默认行为。

### 1.3 MessagesState：内置的消息状态

自己写 `Annotated[list, add_messages]` 是标准做法，LangGraph 也把它做成了内置状态类 `MessagesState`，位于 `langgraph.graph` 模块，专为对话场景设计。它内部维护一个 `messages` 键，等价于：

```python
class MessagesState(TypedDict):
    messages: Annotated[list, add_messages]
```

它的特点：

- 与 LangChain 的消息类型（`HumanMessage`、`AIMessage`、`SystemMessage`、`ToolMessage`）直接兼容
- 节点返回 `{"messages": [...]}` 时自动追加进消息列表
- 可以通过继承扩展自定义字段

一个能跑通的最小示例：

```python
import os
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

def chatbot_node(state: MessagesState):
    # 取出当前消息，调用 LLM；返回值会自动追加进 messages
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot_node)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
app = graph.compile()

result = app.invoke({"messages": [HumanMessage(content="你好！今天能帮我什么？")]})
for message in result["messages"]:
    print(f"{message.__class__.__name__}: {message.content}")
```

运行后会打印两条消息：一条 `HumanMessage`，一条 LLM 追加的 `AIMessage`。

需要扩展状态时，继承加字段即可：

```python
class CustomMessagesState(MessagesState):
    user_id: str
    session_id: int

graph = StateGraph(CustomMessagesState)
```

状态将包含 `messages` 列表以及 `user_id` 和 `session_id`，节点可读写这些字段。两个使用注意：消息必须符合 `BaseMessage` 或兼容格式，塞普通字符串会出问题；长对话历史要么确认模型的上下文窗口装得下，要么自己加截断策略。

### 1.4 条件边：让图自己决定下一步

普通边是写死的流转，条件边（`add_conditional_edges`）根据状态动态路由：条件函数的返回值经过映射字典决定下一个节点。这是 LangGraph 表达分支逻辑的方式，也是后面 ReAct 循环里"有 tool_calls 就去执行工具、没有就结束"的实现基础。

下面这个示例修正过原笔记的两处问题：一是 `add_edge(START, "router")` 写在了 `add_node("router", ...)` 之前——节点还没注册就连边，LangGraph 校验阶段直接报错；二是路由函数返回 `"help_node"` / `"chatbot_node"`，与图中实际节点名 `"help"` / `"chatbot"` 错位，而且同一个函数既被当节点又被当条件函数。修正思路：路由函数只作为条件函数，从 `START` 直接条件路由，返回值与节点名严格对齐。

```python
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

def route_by_intent(state: MessagesState) -> Literal["help", "chatbot"]:
    last_message = state["messages"][-1].content.lower()
    if "帮助" in last_message:
        return "help"
    return "chatbot"

def help_node(state: MessagesState):
    return {"messages": [AIMessage(content="这里是帮助信息！")]}

def chatbot_node(state: MessagesState):
    return {"messages": [AIMessage(content="来聊聊吧！")]}

graph = StateGraph(MessagesState)
graph.add_node("help", help_node)
graph.add_node("chatbot", chatbot_node)

# 条件边：起点是 START，路由函数的返回值映射到目标节点
graph.add_conditional_edges(
    START,
    route_by_intent,
    {"help": "help", "chatbot": "chatbot"},
)
graph.add_edge("help", END)
graph.add_edge("chatbot", END)

app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="我需要帮助")]})
print(result["messages"][-1].content)  # 输出：这里是帮助信息！
```

`add_conditional_edges` 收三个参数：起点节点（这里用特殊节点 `START`）、条件函数、返回值到目标节点的映射字典。条件边也可以从普通节点出发——第 3 节的 `should_continue` 就是从 `agent` 节点出发的。

## 2. 手写 tool-call 循环：Agent 到底在替你做什么

在让 LangGraph 接管之前，值得把这个循环亲手写一遍。`create_agent`、`AgentExecutor`、`ToolNode` 这些封装拆开看没有魔法，核心就是：**在消息列表上跑一圈循环**。整个流程四步：

1. 把用户消息和工具定义一起发给 LLM
2. 检查响应里有没有 `tool_calls`
3. 有：执行对应函数，结果包成 `ToolMessage` 回填进消息列表
4. 带着完整消息再次调用 LLM，它基于工具结果生成最终回复

先定义模型和工具（沿用原笔记的三个 mock 工具）：

```python
import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

model = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

@tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """获取指定位置的当前天气。"""
    return f"{location}当前天气晴朗，温度25{unit}"

@tool
def create_user(name: str, email: str, age: Optional[int] = None) -> Dict[str, Any]:
    """在系统中创建新用户。"""
    user = {"id": hash(email) % 10000, "name": name, "email": email}
    if age:
        user["age"] = age
    return user

@tool
def search_database(query: str) -> List[Dict[str, Any]]:
    """搜索数据库获取信息。"""
    if "产品A" in query:
        return [{"id": 1, "name": "产品A", "price": 99.99}]
    return []

tools = [get_weather, create_user, search_database]

# bind_tools：把工具定义绑定到 LLM，LLM 就"知道"这些工具的存在
llm_with_tools = model.bind_tools(tools)

# 工具名 -> Tool 对象，供手动执行时查找
available_tools = {t.name: t for t in tools}
```

`@tool` 装饰器把普通 Python 函数变成 LangChain 工具：函数签名和 docstring 会被转成 LLM 可读的工具描述——LLM 何时调用、怎么调用全靠 docstring。`bind_tools(tools)` 是关键一步：绑定之后，LLM 在认为合适时就会在响应里返回"工具调用请求"，而不是纯文本。

接下来是循环本身，不用任何 Agent 框架：

```python
# 步骤 1：初始消息列表
messages = [
    HumanMessage(content="创建一个名为李四的用户，邮箱为lisi@example.com，年龄28岁。然后告诉我北京的天气。"),
]

# 步骤 2：第一次调用 LLM（消息 + 工具定义）
first_response = llm_with_tools.invoke(messages)
messages.append(first_response)   # AIMessage，可能带 tool_calls

# 步骤 3：检查并处理 tool_calls
if first_response.tool_calls:
    for tool_call in first_response.tool_calls:
        # tool_call 是 {"name": ..., "args": ..., "id": ...}
        # 注意：args 在 LangChain 里已经是解析好的 dict
        function_name = tool_call["name"]
        function_args = tool_call["args"]

        if function_name in available_tools:
            try:
                result = available_tools[function_name].invoke(function_args)
            except Exception as e:
                result = f"Error executing function {function_name}: {e}"
            content = str(result)
        else:
            content = f"Error: Unknown function {function_name}"

        # 结果包成 ToolMessage，tool_call_id 关联原始请求
        messages.append(ToolMessage(
            tool_call_id=tool_call["id"],   # 必须提供原始调用的 ID
            content=content,
            name=function_name,
        ))

    # 步骤 4：带着工具结果二次调用 LLM
    final_response = llm_with_tools.invoke(messages)
    print(final_response.content)
else:
    # 第一次响应就没有 tool_calls，说明 LLM 直接回答了
    print(first_response.content)
```

四个关键点：

- `first_response.tool_calls` 是一个列表。这条消息同时涉及"创建用户"和"查天气"两件事，模型支持并行工具调用时，一次响应里会返回多个 tool_calls，循环逐个执行、逐个回填——并行工具调用的全部真相就这么多
- `tool_call["args"]` 拿到的**已经是解析好的 dict**。原笔记在这里紧跟过一句 `json.loads(...)`——dict 传进 `loads` 会直接 TypeError，这句必须删掉。较老的单函数 `function_call` 格式里参数才是 JSON 字符串，两种格式混写最容易在这里翻车
- `ToolMessage` 必须带 `tool_call_id`，LLM 靠它把结果和哪一次请求对应起来
- 二次调用时，发给 LLM 的是完整三段消息：`HumanMessage`（原始请求）+ `AIMessage`（带 tool_calls 的调用决定）+ `ToolMessage`（执行结果）。LLM 看到这三段，才能生成综合回复

把这段跑通之后再回头看 Agent 封装：`create_agent` / `AgentExecutor` / LangGraph 的 `ToolNode`，做的就是"第 3 步 + 第 4 步包进一个带停止条件的循环"——没有 tool_calls 就退出循环返回文本。手写一遍的意义就在这里：以后封装出问题，你知道往哪一层查。

## 3. 完整实战：天气助手 ReAct

现在把第 2 节手写的循环交给 LangGraph 工程化：用户用自然语言问某城市天气（示例支持上海和北京），应用自动判断是否调用天气工具，拿到结果后作答，并且记得住对话上下文。

这一节整体迁自我当时的天气助手实战笔记，代码分六段，每段跟着当时的知识点注解。

### 3.1 环境与依赖

安装（原笔记把 `typing`、`os` 也写进了 pip install——它们是标准库，不是 pip 包，这里已删掉）：

```bash
pip install langchain langgraph langchain_openai langchain_core
```

设置环境变量 `DASHSCOPE_API_KEY`，并做启动检查：

```python
import os
if not os.getenv("DASHSCOPE_API_KEY"):
    raise ValueError("DASHSCOPE_API_KEY environment variable not set. Please set it before running.")
```

`os.getenv` 从环境变量读密钥，避免硬编码进代码。

### 3.2 工具定义：@tool

```python
from langchain_core.tools import tool

@tool
def get_weather_updates(query: str) -> str:
    """
    查询城市当前天气 (Query current weather for a city)
    Use this tool to find out the current weather for a given city.
    """
    print(f"--- Tool 'get_weather_updates' called with query: {query} ---")
    query_lower = query.lower()
    if "上海" in query_lower or 'shanghai' in query_lower:
        return "now is 30 celsius, foggy"
    elif "北京" in query_lower or 'beijing' in query_lower:
        return "now is 20 celsius, sunny"
    else:
        return f"Weather information for {query} not available with this tool. Only Shanghai and Beijing are supported."

tools = [get_weather_updates]
```

知识点：

- `@tool` 装饰器把普通函数转成 LangChain 工具，`query: str` 的类型提示和返回值提示都会进入工具描述
- docstring 至关重要：LLM 根据工具名和 docstring 判断**何时调用**（工具能干什么）和**怎么调用**（`query` 参数该传什么）。描述含糊，调用就跟着含糊
- 工具内部目前是 mock 的假数据，实际应用中替换成真实天气 API 调用即可
- `tools = [get_weather_updates]` 收进列表，后续绑定到 LLM

### 3.3 模型初始化与工具绑定

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0
)

model_with_tools = model.bind_tools(tools)
```

知识点：

- `ChatOpenAI` 虽然名字带 OpenAI，但通过 `base_url` + `api_key` 可以接任何 OpenAI 兼容服务，这里接 DashScope
- `temperature=0` 让输出更确定，对需要精确调用工具的场景是稳妥选择
- `bind_tools(tools)` 之后，LLM 在认为合适时返回的将不是纯文本，而是携带工具调用指令的 `AIMessage`

### 3.4 状态与节点

状态用第 1 节的 `MessagesState`——本质就是 `messages: Annotated[list, add_messages]`，每次节点返回 `{"messages": [...]}` 时自动追加。节点有两个，一个调模型，一个执行工具：

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)  # 预构建的工具执行节点

def call_model(state: MessagesState):
    messages = state["messages"]
    print(f"--- Calling model with {len(messages)} messages. Last message type: {type(messages[-1])} ---")
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}
```

知识点：

- `ToolNode(tools)` 是 LangGraph 的预构建节点：接收工具调用请求，执行对应工具，把输出包装成 `ToolMessage` 返回——第 2 节手写的那段 for 循环，它内部替你做了
- `call_model` 是自定义的 Agent 节点：把当前全部消息历史交给绑定了工具的 LLM。LLM 能直接回答时返回普通 `AIMessage`；需要工具时返回带 `tool_calls` 属性的 `AIMessage`，其中包含工具名、参数和唯一的 `tool_call_id`
- 返回值封装成 `{"messages": [response]}`，由 `MessagesState` 自动追加进消息列表

### 3.5 条件边与图构建

```python
from typing import Literal
from langgraph.graph import START, END
from langgraph.checkpoint.memory import MemorySaver

def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    # 最后一条消息是否是带工具调用请求的 AIMessage
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls and len(last_message.tool_calls) > 0:
        print(f"--- LLM decided to use tools: {last_message.tool_calls} ---")
        return "tools"   # 有工具调用，去 "tools" 节点
    print("--- LLM decided NOT to use tools. Ending. ---")
    return END            # 没有，结束流程

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)   # Agent 节点
workflow.add_node("tools", tool_node)   # 工具节点
workflow.add_edge(START, "agent")       # 入口

# 条件边：从 "agent" 出发，由 should_continue 的返回值决定去向
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",  # 返回 "tools" -> 去 "tools" 节点
        END: END           # 返回 END -> 结束
    }
)
workflow.add_edge("tools", "agent")      # 工具执行完，回到 "agent"

checkpointer = MemorySaver()            # 内存检查点，保存对话状态
app = workflow.compile(checkpointer=checkpointer)
```

知识点：

- `tools -> agent` 这条回边是整张图的灵魂：工具执行完回到 LLM，让它基于工具结果继续生成——这就是 ReAct（Reasoning and Acting）循环
- `MemorySaver` 把每个线程（对话）的状态存在内存里，让对话有记忆；生产环境要换持久化存储（第 5 节展开）
- `compile(checkpointer=...)` 把图定义转成可执行应用，同时接入状态持久化

### 3.6 执行：两轮对话

```python
# 用字符串区分不同的对话线程
thread_id = "chat_thread_42"
config = {"configurable": {"thread_id": thread_id}}

print("\nInvoking for Shanghai...")
shanghai_input = {"messages": [HumanMessage(content="what's the weather in Shanghai?")]}
final_state_shanghai = app.invoke(shanghai_input, config=config)

if final_state_shanghai["messages"] and isinstance(final_state_shanghai["messages"][-1], AIMessage):
    print(f"Final response for Shanghai: {final_state_shanghai['messages'][-1].content}")

print("\nInvoking for Beijing (same thread)...")
beijing_input_message = HumanMessage(content="what's the weather in Beijing?")
# 第二次调用：同一个 thread_id，新消息自动追加到已有历史之后
final_state_beijing = app.invoke({"messages": [beijing_input_message]}, config=config)

if final_state_beijing["messages"] and isinstance(final_state_beijing["messages"][-1], AIMessage):
    print(f"Final response for Beijing: {final_state_beijing['messages'][-1].content}")
```

知识点：

- `thread_id` 区分对话会话。配合 checkpointer，相同 `thread_id` 的调用共享同一段对话历史
- 第二次问北京天气时只传新的 `HumanMessage`——`MessagesState` 自动把它追加到上海那轮之后，LLM 处理北京问题时看得到之前的完整对话
- `final_state["messages"][-1].content` 取最后一条 AI 消息，即最终回复

### 3.7 六步执行流程梳理

现在把 "what's the weather in Shanghai?" 这句话输进去之后，图里到底发生了什么逐步拆开——这段是当初记这篇笔记时最值得留下的部分：

1. **入口（`agent` 节点）**
   - `call_model` 被调用，`model_with_tools.invoke` 收到 `[HumanMessage(content="what's the weather in Shanghai?")]`
   - LLM（qwen-max）分析输入和 `get_weather_updates` 的 docstring，判断需要调用这个工具，参数 `query` 应为 "Shanghai"
   - LLM 返回带 `tool_calls` 的 `AIMessage`，例如 `tool_calls=[ToolCall(name='get_weather_updates', args={'query': 'Shanghai'}, id='call_abc123')]`
   - `call_model` 返回 `{"messages": [AIMessage_with_tool_call]}`

2. **条件路由（`should_continue`）**
   - 检查最后一条消息，发现有 `tool_calls`
   - 返回 `"tools"`

3. **工具执行（`tools` 节点）**
   - `ToolNode` 接收 `tool_calls`，找到 `get_weather_updates`，用参数 `{'query': 'Shanghai'}` 调用
   - 工具执行，返回字符串 `"now is 30 celsius, foggy"`
   - `ToolNode` 把结果包装成 `ToolMessage(content="now is 30 celsius, foggy", tool_call_id='call_abc123')`
   - 返回 `{"messages": [ToolMessage_with_result]}`

4. **返回 Agent（`agent` 节点）**
   - `tools -> agent` 的回边把流程带回 `call_model`，此时 `state["messages"]` 包含：
     1. `HumanMessage(content="what's the weather in Shanghai?")`
     2. `AIMessage(..., tool_calls=[...])`
     3. `ToolMessage(content="now is 30 celsius, foggy", tool_call_id='call_abc123')`
   - LLM 看到原始问题、自己调用工具的决定、工具的执行结果，基于这些生成自然回复，例如 `AIMessage(content="The current weather in Shanghai is 30 degrees Celsius and foggy.")`
   - `call_model` 返回 `{"messages": [AIMessage_final_response]}`

5. **条件路由（`should_continue`）**
   - 检查最后一条消息（最终回复），没有 `tool_calls`
   - 返回 `END`

6. **结束**
   - 图执行结束，`app.invoke` 返回最终状态
   - 代码从 `final_state["messages"][-1].content` 提取并打印最终回复
   - `MemorySaver` 把包含这四条消息的完整状态存到 `thread_id="chat_thread_42"` 名下

后续问北京天气时，由于 `thread_id` 相同，`call_model` 的初始状态里就包含上海那四条消息，再加上新的 `HumanMessage(content="what's the weather in Beijing?")`——LLM 因此有上下文感知。

回头看这张图，它就是第 2 节手写循环的图化：`agent` 节点是"调 LLM"，`tools` 节点是"执行 tool_calls 并回填 ToolMessage"，`should_continue` 条件边是循环的停止条件。手写过一遍再看这里，每一层都能对上号。

### 3.8 收尾要点

- 工具定义（`@tool`）：docstring 是 LLM 理解工具的唯一入口
- 模型绑定（`bind_tools`）：让 LLM 知道有哪些工具可用
- `MessagesState`：消息历史的自动追加
- `ToolNode`：预置的工具执行器
- 条件边 + `END`：循环的出口
- `MemorySaver` + `thread_id`：跨轮次的对话记忆

## 4. Map-Reduce：超长文本分段摘要

前两节都在聊 Agent 循环，换一个场景：文本长度超过模型单次上下文窗口，怎么做摘要？

经典解法是 Map-Reduce——大数据领域的老朋友，用在长文本摘要上正合适：

1. **切片（Chunking）**：把长文本切成模型一次吃得下的小块
2. **映射（Map）**：对每个块独立摘要，这一步天然可并行
3. **规约（Reduce）**：把所有小摘要合并，让模型做最后一次整合，产出连贯的最终摘要

LangGraph 适合表达这种多步骤工作流：状态在节点间流转，每一步做什么清清楚楚。完整代码：

```python
import os
from typing import TypedDict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END

llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0,
)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

# 1. 图的状态：整个流程要跟踪的全部数据
class GraphState(TypedDict):
    text: str              # 原始长文本
    chunks: List[str]      # 切分后的文本块列表
    summaries: List[str]   # 每个文本块的摘要列表
    final_summary: str     # 最终的摘要

# 2. 节点：切分
def chunk_text_node(state: GraphState):
    print("--- 正在切分文本 ---")
    chunks = text_splitter.split_text(state['text'])
    return {"chunks": chunks}

# 3. 节点：Map，对每个块独立摘要
def summarize_map_node(state: GraphState):
    print("--- 正在对每个块进行摘要 (Map) ---")
    map_prompt = ChatPromptTemplate.from_template(
        "简要总结以下文本内容：\n\n{chunk}"
    )
    summarize_chain = map_prompt | llm

    # batch 并行处理所有块，max_concurrency 控制并发
    summaries = summarize_chain.batch(
        [{"chunk": chunk} for chunk in state['chunks']],
        config={"max_concurrency": 5}
    )
    # batch 返回 AIMessage 列表，提取 .content
    cleaned_summaries = [s.content for s in summaries]
    return {"summaries": cleaned_summaries}

# 4. 节点：Reduce，合并所有小摘要
def summarize_reduce_node(state: GraphState):
    print("--- 正在合并所有摘要 (Reduce) ---")
    summaries_joined = "\n\n".join(state['summaries'])

    reduce_prompt = ChatPromptTemplate.from_template(
        "你收到了关于一个长文档的多个摘要。请将它们整合成一个连贯、流畅、全面的最终摘要。\n\n"
        "以下是各个部分的摘要：\n{summaries_text}"
    )
    reduce_chain = reduce_prompt | llm
    final_summary = reduce_chain.invoke({"summaries_text": summaries_joined})
    return {"final_summary": final_summary.content}

# 5. 连图
workflow = StateGraph(GraphState)
workflow.add_node("chunker", chunk_text_node)
workflow.add_node("mapper", summarize_map_node)
workflow.add_node("reducer", summarize_reduce_node)

workflow.add_edge(START, "chunker")   # 入口
workflow.add_edge("chunker", "mapper")
workflow.add_edge("mapper", "reducer")
workflow.add_edge("reducer", END)
app = workflow.compile()

# 6. 跑一个示例：把一段文本重复 10 次模拟长文本
long_text = """
人工智能（AI）正在以前所未有的速度改变世界。从自动驾驶汽车到医疗诊断，AI的应用无处不在。
其核心技术包括机器学习、深度学习和自然语言处理。机器学习使计算机能够从数据中学习规律，而无需进行显式编程。
深度学习是机器学习的一个分支，它利用深度神经网络模型，在图像识别、语音识别等领域取得了巨大成功。
自然语言处理则致力于让计算机能够理解和生成人类语言，Siri和ChatGPT就是最好的例子。
然而，AI的发展也带来了挑战，如数据隐私、算法偏见和就业冲击。解决这些问题需要技术、法律和伦理的共同努力。
""" * 10

final_state = app.invoke({"text": long_text})
print(final_state['final_summary'])
```

代码要点：

1. `GraphState` 是 TypedDict，像一份清单，规定流程要跟踪的全部数据（原文、块、各块摘要、最终摘要）。注意这里的字段**没有** `add_messages` 这类 reducer——默认覆盖语义，每个字段只由一个节点整体写入一次，正好匹配这条线性流水线（对照 1.2 节）
2. `chunk_text_node` 是入口节点：接收 `text`，用 `RecursiveCharacterTextSplitter` 切分，`chunks` 写回状态
3. `summarize_map_node` 是 Map 步骤：`batch()` 并行为每个块生成摘要，比手写 for 循环高效；返回的 `AIMessage` 列表要取 `.content`
4. `summarize_reduce_node` 是 Reduce 步骤：小摘要拼接后交给 LLM 做最后一次、也是最关键的整合
5. 边的连接定义流水线顺序：`chunker -> mapper -> reducer -> END`
6. `invoke({"text": long_text})` 启动整张图——初始状态只需要 `text` 一个键，LangGraph 按定义好的流程执行完所有步骤，返回包含全部结果的最终状态

这套结构既绕开了上下文窗口限制，流程又清晰可维护：想加一步"摘要去重"或"质量过滤"，加个节点就行。

## 5. 记忆与持久化：MemorySaver 与 thread_id

第 3 节的天气助手已经用上了 `MemorySaver`，这里把机制单独拆开讲，因为它值得。

LangGraph 的记忆靠 checkpointer（检查点）机制：图每执行完一步，就把当前状态存一份快照。编译时传入 checkpointer，运行时指定 `thread_id`：

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
result = app.invoke({"messages": [HumanMessage(content="你好！")]}, config)

# 后续调用恢复状态：只传新消息，历史自动接上
result = app.invoke({"messages": [HumanMessage(content="继续聊")]}, config)
```

- `thread_id` 是记忆的单位：同一个 `thread_id` 下的调用共享状态，换一个 `thread_id` 就是全新对话
- `MemorySaver` 存在内存里，进程结束记忆就没了——适合开发和测试
- 生产环境要换持久化实现：官方提供了 SQLite、Postgres 等独立安装的 checkpointer 包，也可以自己接 Redis 这类存储

命名注记：这个类现在叫 `InMemorySaver`，`MemorySaver` 是保留的旧别名，两个名字指向同一个东西，新代码建议用前者。

## 6. 版本注记：从 0.x 写法到 LangChain 1.x

这篇整合自 0.x 时代的笔记，几处新旧差异统一交代：

- **`set_entry_point` 已统一为 `add_edge(START, ...)`**。原笔记的天气助手和 Map-Reduce 图用的都是 `set_entry_point("agent")` 这类写法，官方后来统一成 `add_edge(START, "agent")`（连同 `set_finish_point` → `add_edge(node, END)`），本文正文已全部改写。旧写法当前仍可用，但属废弃路径
- **`ChatTongyi` 属 legacy**。原笔记另一处用 `langchain_community.chat_models` 的 `ChatTongyi` 直连通义——这个包里的集成属于 legacy。本文统一走 DashScope 的 OpenAI 兼容端点（`ChatOpenAI` + `base_url`），这也是当时验证过可行的路线
- **模型**。原笔记示例里有 `gpt-3.5-turbo`（已下线）和 `gpt-4o-mini`，整合时统一替换为 DashScope 的 `qwen-plus` / `qwen-max`
- **一行式封装**。现在构建 ReAct Agent 不需要手搓图：`langgraph.prebuilt.create_react_agent` 一行拉起；LangChain 1.x 的 `langchain.agents.create_agent` 是官方标准入口，底层就是 LangGraph。但我的判断是：手写一遍第 2 节那个循环，仍然是理解这些封装的最佳方式——封装出问题时，你得知道问题出在哪一层

更深的 Agent 工程化路线——多智能体、子智能体、规划与上下文管理——同目录的《DeepAgents完全指南》是这篇的自然延伸。

参考：[LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)

## 附：题外话——我试过的 LangChain 知识图谱（不是 LangGraph）

如实交代：写《Langchain-Graph实战教程》那篇笔记时，我把两个 "Graph" 搞混了——LangChain 的 Knowledge Graph 功能和 LangGraph 是完全不同的东西。前者（`GraphQAChain`、`NetworkXEntityGraph`、`LLMGraphTransformer`）用图结构表示知识、做图谱问答；后者是工作流编排框架。一个是数据，一个是执行引擎。

不过那次实验的踩坑记录值得留档。当时用 `LLMGraphTransformer`（`langchain_experimental`）从文本构建内存知识图谱，写法如下（`Tongyi` 同样来自 `langchain_community`，属当时的旧写法）：

```python
from langchain_community.llms import Tongyi
from langchain_community.graphs import NetworkXEntityGraph
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from langchain_core.documents import Document

llm_for_graph = Tongyi(model_name="qwen-plus")

document_content = """
张三是北京大学的教授，他研究人工智能领域。
李四是张三的学生，他就读于清华大学，学习计算机科学。
王五是百度的工程师，百度是一家位于北京的科技公司。
"""
docs = [Document(page_content=document_content)]

llm_transformer = LLMGraphTransformer(llm=llm_for_graph)
graph_documents = llm_transformer.convert_to_graph_documents(docs)

final_graph = NetworkXEntityGraph()
final_graph.add_graph_documents(graph_documents)
for triple in final_graph.get_triples():
    print(triple)
```

两个结论：

1. **`GraphQAChain` 对 `NetworkXEntityGraph` 支持不佳**。当时直接 `graph_qa_chain.run(question)` 基本走不通——它内部按生成 Cypher 查询的思路工作，而内存图根本不支持 Cypher，一跑就抛错
2. **手工三元组检索是可用的备选**。绕开 Chain，直接从图里捞相关三元组当上下文，交给 LLM 回答：

```python
def get_relevant_triples(graph, entity_name):
    """检索与某个实体相关的三元组"""
    lines = []
    for s, p, o in graph.get_triples():
        if entity_name in str(s) or entity_name in str(o):
            lines.append(f"({s}, {p}, {o})")
    return "\n".join(lines)

context = get_relevant_triples(final_graph, "张三")
# 再把 context 和问题拼进 prompt，交给 LLM 生成答案
```

另外说明：`LLMGraphTransformer` 至今还在 `langchain_experimental` 里，仍属实验性，别在生产上依赖它。我的判断：真要做知识图谱问答，直接上 Neo4j 配 `GraphCypherQAChain`；或者更轻的做法——三元组检索本质上就是 RAG 的一种上下文来源，没必要被"图谱"这个词吓住。

## 总结

- LangGraph 的地基是三件套：`StateGraph`（状态机）、State（reducer 决定覆盖还是追加）、条件边（动态路由）。`MessagesState` 只是 `Annotated[list, add_messages]` 的官方打包
- Agent 没有魔法：`tool_calls` → 执行 → `ToolMessage` 回填 → 二次调用，一行式封装做的就是在消息列表上转这一圈
- ReAct 循环的图表达就三个部件：`agent` / `tools` 节点、`should_continue` 条件边、`tools -> agent` 回边
- 超出上下文窗口的活交给 Map-Reduce，图让流水线每一步可插拔
- 记忆的单位是 `thread_id` + checkpointer，内存版叫 `InMemorySaver`

先手写一遍循环、看懂消息怎么流，再谈一行式封装——这是全文的路线，也是我判断的入门 LangGraph 最不绕的路。
