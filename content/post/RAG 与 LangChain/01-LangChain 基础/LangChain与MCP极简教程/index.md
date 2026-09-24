---
title: LangChain 与 MCP 极简教程：让 Agent 接入外部工具的另一种方式
description: "用 FastMCP 起一个工具服务，用 LangChain 1.4 内建的 langchain.mcp 接进 Agent：双文件跑通 MCP 最小闭环"
date: 2026-09-08T13:00:00+08:00
image: images/index/index.png
categories:
    - Agent
tags:
    - LangChain
---

# LangChain 与 MCP 极简教程

给 Agent 接工具，最常见的做法是把所有工具函数都写在应用代码里，再逐个注册给模型。工具少的时候没问题；一旦工具多起来、或者想跨项目复用，这条路就会越来越累——同样的工具，每个应用都要重新写一遍。

MCP（Model Context Protocol，模型上下文协议）是 Anthropic 在 2024 年底推出的开放协议，解决的就是这个问题：把「工具的定义和执行」从应用代码里拆出来，放到独立的服务器上，客户端按需发现和调用。本文用一个最小的双文件例子——FastMCP 起一个数学工具服务，`langchain.mcp` 把它接进 Agent——把这条链路跑通。

客户端这一侧，2026 年 9 月有个值得注意的变化：**MCP 支持已经进到 LangChain 主干里**。LangChain `v1.4.0` 新增了 `langchain.mcp` 命名空间，基于 FastMCP 实现，把原先独立的 `langchain-mcp-adapters` 包整个取代了——`MultiServerMCPClient` 收敛成一个 `MCPAdapter`。所以现在装依赖是 `pip install "langchain[mcp]"`，不再是单独装一个适配器包。本文代码全部按新写法给。

## MCP 和 Function Call 是什么关系

先说结论：两者不是竞争关系，而是工作在两层的东西。

- **Function calling 是模型的能力**：模型根据工具的名称、描述和参数 schema，决定「该调哪个工具、传什么参数」，并以结构化 JSON 输出。
- **MCP 是工具的供给协议**：约定客户端如何发现服务器上有哪些工具（tool list）、如何调用（tool call）、如何取回结果。

也就是说，MCP 解决的不是「模型会不会调工具」，而是「工具从哪来、谁来维护、能不能复用」。写一次 MCP server，任何支持 MCP 的客户端（Claude Desktop、Cursor、你自己的 Agent）都能连。

## 最小实战：两个文件跑通

项目就两个文件：

- `math_server.py`：MCP 服务端，提供数学工具
- `client.py`：LangChain 客户端，把 MCP 工具接进 Agent

### 服务端：FastMCP 起服务

```python
# math_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

两个细节值得注意：

- 工具用 `@mcp.tool()` 装饰器定义，函数签名和 docstring 就是模型看到的工具说明——和 LangChain `@tool` 的玩法一致，类型注解必须写清楚。
- `transport="stdio"` 表示通过标准输入/输出通信，客户端会以子进程方式拉起这个脚本，本地工具用它最省事；要跨机器就走 HTTP（streamable HTTP / SSE）。

### 客户端：把 MCP 工具接进 Agent

```python
# client.py
import asyncio
import os
from pathlib import Path

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI

# 模型走阿里云百炼的 OpenAI 兼容模式
model = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
)

# 目标类型决定传输方式：Path = stdio 子进程，字符串 = 必须是 http(s) URL
adapter = MCPAdapter(Path("math_server.py"))


async def run_agent():
    async with adapter:
        # 把 MCP 工具加载为 LangChain 工具
        tools = await adapter.list_tools()

        # 创建并运行 agent
        agent = create_agent(model, tools)
        return await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})


if __name__ == "__main__":
    print(asyncio.run(run_agent()))
```

`MCPAdapter` 最省事的地方是**它从你交给它的目标自己推断传输方式**，不需要再写 `transport` 字段：

| 传给 `MCPAdapter` 的目标 | 推断出的传输 |
|---|---|
| `"https://example.com/mcp"` | Streamable HTTP |
| `Path("math_server.py")` | stdio 子进程（每个 adapter 一个） |
| 一个 `FastMCP` 实例 | 进程内直连，不走子进程也不走 socket，跑测试最合适 |
| `{"mcpServers": {...}}` 配置字典 | 多服务器，工具名自动加 `{server}_` 前缀 |
| 现成的 `fastmcp.Client` | 完全自定义（transport、缓存、认证） |

有个坑值得单独说：**脚本路径必须传 `Path` 而不是 `str`**。FastMCP 解析字符串时会先当文件路径试，再当 URL 试，所以一个字符串形式的 `"math_server.py"` 有被当成本地脚本拉起的风险；`MCPAdapter` 的做法更保守——直接拒绝所有不符合 URL 形状的字符串。想跑本地脚本，明确写 `Path(...)`。

### 运行

```bash
pip install "langchain[mcp]" langchain-openai mcp

export DASHSCOPE_API_KEY=your_api_key

python client.py
```

客户端会自己拉起 `math_server.py`，提出问题 "what's (3 + 5) x 12?"，并输出计算结果。

## 运行时发生了什么

1. `MCPAdapter(Path("math_server.py"))` 从目标类型推断出 stdio 传输
2. 进入 `async with adapter` 时以子进程方式启动 `math_server.py`，完成 MCP 握手
3. `adapter.list_tools()` 把服务器上的工具转换成 LangChain 工具列表
4. `create_agent(model, tools)` 用这些工具构建 Agent
5. Agent 收到问题，决定调用哪个工具；实际执行发生在 MCP server 侧，结果经客户端回传给模型

关键点在第 3 步：对 Agent 来说，MCP 工具和本地 `@tool` 定义的工具没有任何区别，适配器把协议细节全部藏掉了。另外返回的每个工具自己持有连接、每次调用各开一个会话，所以**`async with` 退出后 agent 依然可用**——不必把整轮推理都关在上下文里。

## Function Call vs MCP

![Function Calling 与 MCP 的链路对比](images/index/image.png)

| 维度 | Function Calling | MCP |
|---|---|---|
| 解决的问题 | 模型如何表达「调这个工具、参数是这些」 | 工具如何被外部程序发现、提供和复用 |
| 所在层 | 模型 API 的能力 | 客户端与服务端之间的协议 |
| 工具定义位置 | 应用代码里（`@tool` / JSON Schema） | 独立的 MCP server |
| 复用性 | 换个应用基本要重写 | 一个 server 服务所有支持 MCP 的客户端 |
| 传输方式 | 随模型 API 请求一起发送 | stdio / HTTP，工具在进程外执行 |

一句话总结：function calling 决定模型「怎么说」，MCP 决定工具「从哪来」；MCP 工具最终还是要靠 function calling 让模型真正用起来。

## 版本注记：从 langchain-mcp-adapters 迁移过来

这篇教程最早写在 MCP 适配器还是独立包的时期，当时的客户端长这样：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

client = MultiServerMCPClient({
    "math": {"transport": "stdio", "command": "python", "args": ["math_server.py"]},
})
tools = await client.get_tools()
agent = create_react_agent(model, tools)
```

LangChain `v1.4.0`（2026-09-01）之后，这套写法整体退休。对应关系如下：

| 旧（`langchain-mcp-adapters`） | 新（`langchain.mcp`） |
|---|---|
| `MultiServerMCPClient(...)` | `MCPAdapter(target)` |
| `await client.get_tools()` | `await adapter.list_tools()` |
| `load_mcp_tools(session)` | 直接用 `adapter.list_tools()` |
| `convert_mcp_tool_to_langchain_tool` | `as_langchain_tool`（改名，且变成协程） |
| `tool_name_prefix` | 多服务器时自动加 `{server}_` 前缀 |
| `handle_tool_errors` 开关 | 移除。行为固定：`isError=True` 变成 `ToolMessage(status="error")`，传输故障直接抛异常 |
| `Callbacks(on_elicitation=...)` | 取消回调，改为默认开启的 LangGraph `interrupt()` |
| `tool_interceptors` | 用 LangChain `@wrap_tool_call` 中间件（能拦所有工具，不止 MCP 的） |
| 连接上的 `auth` / `headers` | 挪到 `fastmcp.Client` 上 |

三个必须知道的边界：

- **`langchain.mcp` 目前是 beta**（需要 `langchain[mcp]>=1.4.0`），import 时会抛一次 `LangChainBetaWarning`，API 可能变。
- **elicitation 变成 interrupt**：服务端中途要输入时，不再是回调，而是暂停整个 run，用 `Command(resume={"responses": {key: 答案}})` 恢复。这是设计变化，不是 bug。
- **prompts / resources 还没有包装**：`load_mcp_prompt`、`load_mcp_resources` 这些没有对应实现，需要的话直接用 FastMCP 客户端的 `client.get_prompt(...)` / `client.read_resource(...)`。sampling 和 roots 则是因为 MCP 协议本身在无会话时代移除了，会抛 `NotImplementedError`。

依赖包名也顺便更新一下：现在装的是 `langchain[mcp]`，不再需要 `pip install langchain-mcp-adapters`。

收藏的参考资料：

| 资源 |
|---|
| [MCP 终极指南（很值得读）](https://guangzhengli.com/blog/zh/model-context-protocol) |
| [LangChain 官方 MCP 文档](https://docs.langchain.com/oss/python/langchain/mcp) |
| [从 langchain-mcp-adapters 迁移](https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters) |
| [Using LangChain With Model Context Protocol (MCP)](https://cobusgreyling.medium.com/using-langchain-with-model-context-protocol-mcp-e89b87ee3c4c) |
| [知乎：一文看懂 MCP（大模型上下文协议）](https://zhuanlan.zhihu.com/p/27327515233) |
| [Function Call vs MCP](https://www.dailydoseofds.com/p/function-calling-mcp-for-llms/)（本文配图出处） |

## 下一步

- 把数学工具换成你真正需要的东西：查数据库、调内部 API、文件处理，思路完全一样
- 工具链路稳定之后，如果要做长周期、多步骤的 Agent 工程（文件系统、子智能体、上下文管理），看本站的《DeepAgents完全指南》
