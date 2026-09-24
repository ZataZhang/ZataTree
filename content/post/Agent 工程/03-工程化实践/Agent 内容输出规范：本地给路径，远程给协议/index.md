---
title: "Agent 内容输出规范：本地给路径，远程给协议"
description: "一个 Agent 跑完一次，会输出自然语言、工具调用、产物文件三类内容。本地运行时给文件路径就够了，但一旦把 Agent 挂到远程接口上，就必须有一套类型化的输出协议。本文梳理消息协议、SSE 事件设计、产物通道与 AG-UI 标准。"
date: 2026-09-03T10:00:00+08:00
slug: "Agent 内容输出规范：本地给路径，远程给协议"
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 工程化实践
    - Agent 工程实战
draft: false
---

把 Agent 从"本地脚本"变成"线上服务"时,第一个卡住你的往往不是模型,而是输出。

本地运行时,Agent 写完报告把路径 `print` 出来就行,人类看得懂;一旦换到远程,调用方是另一个程序,它拿到的必须是可以解析的结构化信息——Agent 调用工具了没有?调用了哪个?产物文件怎么下载?这些信息在本地靠肉眼,在远程必须靠协议。

这篇文章回答三个问题:**Agent 到底输出什么、工具调用在消息协议里长什么样、远程接口该用什么方式把这些输出送出去**。

## 一、一次运行的三类输出

一个 Agent 跑完一轮,输出永远是三类东西的组合:

```text
① 自然语言流: 给用户看的解释、报告正文、流式增量文本
② 工具调用事件: 调用了哪个工具、参数是什么、结果是什么
③ 产物 (Artifact): 生成的文件——报告、音频、图片、数据库记录
```

本地和远程的差异,本质上是对这三类输出的**投递方式**不同:

| 输出 | 本地 | 远程 |
| --- | --- | --- |
| 自然语言 | `print` / 终端流式 / Streamlit | SSE 事件里的文本增量块 |
| 工具调用 | 肉眼观察日志 | 结构化事件(工具名、参数、结果) |
| 产物 | 文件路径,直接可访问 | 独立下载端点 + 访问 URL |

其中第②类最难标准化,它夹在"模型输出"和"程序输出"之间,是 Agent 独有的形态。先从它说起。

## 二、消息协议：工具调用在"线"上长什么样

主流 Agent 框架(OpenAI Agents SDK、LangChain、各种自研循环)底层都遵循 OpenAI 兼容的聊天消息格式。工具调用不是一段文字,而是一条结构化消息:

```json
{
  "role": "assistant",
  "content": "我来搜索一下这个问题的答案。",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"AG-UI protocol\", \"limit\": 5}"
      }
    }
  ]
}
```

模型说"我要调用 `web_search`",程序执行后,把结果以 `tool` 角色的消息回灌给模型:

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "搜到 3 条结果：...（或被截断的文本）"
}
```

协议里两个必须知道的细节:

- **`arguments` 是 JSON 字符串,不是对象**——这是协议约定,传输时不会被二次转义/改键序,接收方拿到后自行 `json.loads`。
- **`tool` 消息必须带 `tool_call_id` 回指**——否则模型不知道自己拿到的是哪次调用的结果。

Anthropic 的 content-blocks 格式是另一套等价表达:`tool_use` / `tool_result` 作为内容块混合在 `content` 数组里,概念一致。

> 这一层是**协议事实**,不依赖某个框架。无论你手写循环、用 SDK、还是用 MCP 桥接工具,最终在"线"上走的都是这个形状。

## 三、两类 Agent 框架事件流（仓库实证）

上面是"一次调用"的静态格式;实际编程里,你可能直接在事件流里消费这些消息。有两种主流的流式事件体系,拿真实代码对比:

**1. OpenAI Agents SDK 的事件类型** —— 在 awesome-llm-apps 的流式教程 `openai_sdk_crash_course/4_running_agents/4_4_streaming_events/agent.py` 中,事件按类型分发:

```python
# OpenAI Agents SDK (agents 0.1.x) 流式事件
async for event in Runner.run_streamed(agent, "解释机器学习原理"):
    if hasattr(event, "type"):
        if event.type == "response_start":
            print("[EVENT] Response started")
        elif event.type == "tool_call_start":      # ← 工具调用开始
            print("[EVENT] Tool call started")
        elif event.type == "tool_call_complete":   # ← 工具调用完成
            print("[EVENT] Tool call completed")
        elif event.type == "response_complete":
            print("[EVENT] Response completed")
```

事件名是 `response_start` / `tool_call_start` / `tool_call_complete` / `response_complete`,SDK 在内部维护运行状态,把模型输出和工具执行切成事件抛给你。

**2. Anthropic Messages API 的 content-block 流** —— 事件按内容块细分:

```text
message_start → content_block_start → text_delta × N
→ content_block_stop → content_block_start(tool_use) → tool_use(...)
→ message_stop
```

模型吐一个字推一个字(`text_delta`),工具参数一段一段到达;结果是前一个事件驱动下一个:你先把参数收完整,再执行工具,再把结果作为 `tool_result` 发回。

两者的差别是**粒度**:OpenAI SDK 把你当"运行期观察者",Anthropic 把你当"消息流水线上的协作者"。用到自己的远程接口上,设计可以取其中任意一套——但命名要统一。

## 四、远程接口：三种投递方案

### 方案 A：非流式 REST——返回完整 transcript

`POST /chat` 传入 messages,Agent 全程跑完后把**完整消息数组**(含 tool_calls)一次性返回。简单、可缓存,但调用方是黑盒:埋头等十几秒,看不到过程,长任务容易超时。

```json
// POST /chat  → 200 OK
{
  "messages": [
    {"role": "assistant", "content": "我来搜索一下。", "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "call_abc123", "content": "..."},
    {"role": "assistant", "content": "结论是……"}
  ]
}
```

适用:离线批处理、对延迟不敏感、调用方只需要最终答案的场景。

### 方案 B：SSE 流式——事件驱动的推荐方案

`POST /chat` 返回 `text/event-stream`,Agent 每做一个动作 yield 一个类型化事件。**这是把 Agent 挂到线上最主流的姿势**:死等变成边跑边看,工具调用可渲染、可中断、可审计。

事件类型直接复用上面第三节的命名体系。最小实现:

```python
# 依赖: fastapi>=0.115, uvicorn
from fastapi import FastAPI, StreamingResponse
import json

app = FastAPI()

def agent_pump(user_input: str):
    """Agent 主循环：把模型输出和工具调用压成事件"""
    yield {"type": "message_start", "message": {"role": "assistant", "content": []}}
    yield {"type": "text_delta", "delta": "我先搜索一下。"}
    yield {"type": "tool_use", "name": "web_search", "input": {"query": user_input}}
    result = call_tool("web_search", {"query": user_input})   # 你的工具执行
    yield {"type": "tool_result", "tool_use_id": "call_1", "content": result}
    yield {"type": "text_delta", "delta": "找到 3 条结果，第一条是……"}
    yield {"type": "message_stop"}

@app.post("/chat")
async def chat(payload: dict):
    async def gen():
        for ev in agent_pump(payload["user_input"]):
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```

调用方按 `type` 分发渲染:`text_delta` 追加文本,`tool_use` 显示"🔧 正在搜索……",`tool_result` 渲染结果。事件命名建议直接抄 Anthropic 体系(`text_delta` / `tool_use` / `tool_result`),生态里随处可以找到对照实现;用 OpenAI SDK 的话就抄 `tool_call_start` / `tool_call_complete`,跟你的运行框架一致比追求通用更重要。

### 方案 C：AG-UI / A2UI 标准协议——对接现成前端的正解

AG-UI 是 CopilotKit 发起的开源标准,Anthropic 也在推(A2UI),把事件命名**固定下来**并配上一套前端 SDK。事件类型是一份固定清单:`agent_message_chunk`、`tool_call_start`、`tool_call_detail`、`tool_call_end`、`artifact`、`error`、`end`……

awesome-llm-apps 的 `ai-deep-research-agent` 就是一个 FastAPI + AG-UI 的完整部署:把 LangGraph agent 注册成标准端点(代码截图):

```python
# awesome-llm-apps/generative_ui_agents/ai-deep-research-agent/agent/main.py
agui_config = copilotkit_customize_config(
    emit_tool_calls=["research", "write_todos", "write_file", "read_file", "edit_file"],
)
add_langgraph_fastapi_endpoint(
    app=app, agent=LangGraphAGUIAgent(name="research_assistant", ...), path="/",
)
```

它展示了一个 AG-UI 特有的实用点——`emit_tool_calls`:**只暴露你想让前端看到的工具,子 agent 内部的一堆工具噪声可以过滤掉**。自己设计事件协议时会漏掉这一点,然后前端被内部工具刷屏。

## 五、产物文件：Agent 生成的文件怎么投递

文本和工具事件可以进流,二进制文件不适合塞进 SSH 流。产物通道要为两类对象解耦:

```text
Agent 侧:写完文件 → 产出 artifact 记录(artifact_id + 元数据 + 访问 URL)
接口侧: GET /artifacts/{id} → 返回文件内容(支持 Range 分段下载)
```

事件流里只携带轻量的 artifact 信息,调用方拿到后知识它去 GET。支持 Range 的必要性在于:前端播放音频/视频需要分段请求,断点续传依赖它。

awesome-llm-apps 的 beifong 就是这个模式——`/stream-audio/{filename}` 端点用 `StreamingResponse` + Range 头做音频分段播放,Agent 跑完后把音频路径落库,前端拿 URL 再来拉。

```python
# beifong 的 Range 处理（摘要）
header = request.headers.get("Range", "")      # "bytes=0-1023"
start, end = parse(header, file_size)
return StreamingResponse(file_streamer(), status_code=206, headers={
    "Content-Range": f"bytes {start}-{end}/{file_size}", ...})
```

## 六、决策速查表

| 场景 | 方案 | 关键选型 |
| --- | --- | --- |
| 离线批处理,只要最终答案 | A 非流式 REST | 返回完整 transcript 数组 |
| 线上对话,要过程可见/可中断 | B SSE 流式 | 事件命名抄 Anthropic 或 OpenAI SDK |
| 对接 CopilotKit 等现成前端 | C AG-UI 标准 | 用 `emit_tool_calls` 过滤子 agent 噪声 |
| 产物文件(音频/报告/图片) | 独立下载端点 | artifact_id + URL,配 Range 分段 |
| 工具调用"线"格式 | 消息协议 | `tool_calls`(JSON 字符串入参)+ `role: tool` 回灌 |

## 七、结论

Agent 输出规范的问题,本质是一个**投递分层**问题:

- **协议层**(工具调用在消息里的形状)——由 OpenAI/Anthropic 兼容格式定义,不讨论,直接用。
- **投递层**(怎么把三类输出送出去)——本地给路径,远程走事件流;事件命名跟着你的运行框架走,别自创。
- **标准层**(要不要对齐 AG-UI)——自用方案 B 够用;要对接开源前端,直接上 AG-UI,别重新发明轮子。

先把没一行输出删除——把 Agent 的输出当协议设计,而不是当日志设计,是"能上生产"和"能跑 Demo"的分界线。

<sub>文中仓库实证来自 awesome-llm-apps:流式事件教程 `openai_sdk_crash_course/.../4_4_streaming_events/agent.py`、AG-UI 部署 `generative_ui_agents/ai-deep-research-agent/agent/main.py`、产物分段下载 `beifong/main.py`。</sub>