---
title: OpenAI Responses API与Chat Completions API区别详解
description: 对比 OpenAI Responses API 与 Chat Completions API 的核心差异、能力边界、迁移成本与选型建议
date: 2026-09-07T18:05:39+08:00
image: images/index/index.svg
categories:
  - Agent
tags:
  - OpenAI API
draft: false
---

## 一句话结论

Chat Completions 是传统的“聊天消息补全”接口：调用方自己维护完整的消息历史，模型按输入生成一条 assistant 回复。Responses 是 OpenAI 推出的新一代统一接口：不仅支持生成回复，还内置工具调用、Agent 循环、会话状态管理和结构化输出 Item，为构建 Agent 应用而生。

## 核心区别总览

| 维度 | Chat Completions | Responses |
|---|---|---|
| 端点 | `POST /v1/chat/completions` | `POST /v1/responses` |
| 输入格式 | `messages[]` 数组（客户端维护完整对话历史） | `input`（可以是字符串或消息数组），支持通过 `previous_response_id` 让服务端管理历史 |
| 系统提示 | 放在 `messages` 中的 `role: "system"` | 独立的顶层 `instructions` 字段 |
| 输出格式 | `choices[]`，每项包含 `message` | `output[]`，一组类型化 Item（`message`、`function_call`、`reasoning` 等） |
| 内置工具 | 仅自定义函数调用 | 原生支持 `web_search`、`file_search`、`code_interpreter`、`computer_use`、MCP、图像生成等 |
| Agent 循环 | 单次请求通常只完成一轮工具调用 | 一次请求内模型可多次调用工具，形成 Agent 循环 |
| 状态管理 | 无状态，客户端手动维护历史 | `store: true` 默认开启，服务端保存上下文；也支持加密推理 Item 实现无状态 |
| 推理模型 | 推理 Token 暴露有限 | 提供更完整的推理摘要与工具联动 |
| 流式输出 | `delta` 增量块 | 类型化的 SSE 事件（按 `type` 分支处理） |
| 多候选生成 | 支持 `n > 1` 返回多个 `choices` | 已移除，只返回一个结果 |
| Structured Output | `response_format` | `text.format` |

## 协议结构差异

### Chat Completions：消息数组驱动

客户端负责拼装完整对话上下文：

```json
{
  "model": "gpt-4o",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "什么是 Responses API？" }
  ]
}
```

响应结构围绕 `choices` 展开：

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Responses API 是..."
      }
    }
  ]
}
```

### Responses：类型化 Item 驱动

输入更灵活，最简单可以直接传字符串：

```json
{
  "model": "gpt-4o",
  "input": "什么是 Chat Completions API？"
}
```

也可以传入结构化消息并指定 `instructions`：

```json
{
  "model": "gpt-4o",
  "instructions": "You are a helpful assistant.",
  "input": [
    { "role": "user", "content": "帮我比较两个 API 的区别。" }
  ]
}
```

响应由一组类型化 Item 组成：

```json
{
  "id": "resp_xxx",
  "output": [
    { "type": "reasoning", "summary": "..." },
    { "type": "message", "role": "assistant", "content": [{ "type": "output_text", "text": "..." }] }
  ]
}
```

## 工具调用与 Agent 能力

### Chat Completions 中的工具调用

Chat Completions 支持 `tools` 与 `tool_calls`，但逻辑是“一问一答”模式：模型返回 `tool_calls` 后，客户端需要执行工具、手动把结果追加回 `messages`，再发起下一次请求才能让模型继续。

适合场景：

- 单次函数调用（查数据库、调用一个 API）
- 简单的多轮对话机器人
- 兼容现有生态的主流方案（大量第三方框架和推理服务以此为准）

### Responses 中的 Agent 循环

Responses API 一次请求内可以完成多轮工具调用。模型可以搜索、读文件、执行代码、再推理，最终在一个响应中返回结果，客户端无需手动维护中间的工具调用状态。

示例：

```json
{
  "model": "gpt-4o",
  "tools": [{ "type": "web_search" }, { "type": "code_interpreter" }],
  "input": "搜索今天的AI新闻，然后写一段 100 字的摘要"
}
```

适合场景：

- 需要“搜索 + 总结”或“读文件 + 分析”的多步骤任务
- Agent 工作流、自动化研究助手
- 希望服务端托管上下文与工具执行的应用

## 会话状态管理

这是两者最实际的工程差异之一。

**Chat Completions：** 完全无状态。每一轮对话客户端都要把之前所有消息重新发送一遍。对话越长，每次请求的 Token 成本越高，客户端需要自己实现历史裁剪、摘要、缓存等逻辑。

**Responses：** 默认开启 `store: true`，服务端会保存对话上下文。后续请求只需传 `previous_response_id` 指向上一次的响应，服务端自动拼接历史：

```json
{
  "model": "gpt-4o",
  "previous_response_id": "resp_xxx",
  "input": "继续刚才的话题"
}
```

如果担心数据隐私，可以使用 `store: false` 并利用加密推理 Item（Encrypted Reasoning Items）实现“无状态但保留推理上下文”的模式，适合 ZDR（Zero Data Retention）场景。

## 流式事件差异

### Chat Completions 流式

返回一系列 `delta` 块，客户端拼接 `delta.content` 即可：

```
data: {"choices":[{"delta":{"content":"你"}}]}
data: {"choices":[{"delta":{"content":"好"}}]}
data: [DONE]
```

### Responses 流式

返回一组按 `type` 区分的 SSE 事件，每个事件都有明确的生命周期：

```
event: response.output_text.delta
data: {"type":"response.output_text.delta","delta":"你"}

event: response.function_call_arguments.delta
data: {"type":"response.function_call_arguments.delta","delta":"..."}

event: response.completed
data: {"type":"response.completed"}
```

Responses 的事件粒度更细，能区分“文本开始”“工具参数流”“推理摘要”“响应完成”等阶段，适合构建更精确的 UI 反馈。

## 兼容性与迁移成本

| 方面 | 说明 |
|---|---|
| 向后兼容 | Chat Completions 没有废弃计划，现有代码可继续使用 |
| 第三方兼容 | 大量开源推理服务（vLLM、Ollama、各种国内模型）只实现了 Chat Completions 兼容协议；Responses 兼容目前仅限 OpenAI 官方和少数服务 |
| 迁移路径 | OpenAI 提供 migration guide，主要改动是把 `messages` 换成 `input`，系统提示提取到 `instructions`，`choices` 改为 `output` |
| SDK 支持 | OpenAI 官方 SDK 两条路径都支持；社区 SDK 大多以 Chat Completions 为主 |

**判断标准：** 如果你的应用需要部署到非 OpenAI 的模型服务（本地模型、第三方推理引擎），Chat Completions 是事实标准。如果只在 OpenAI 生态内构建，Responses 功能更完整。

## 选型建议

| 场景 | 推荐 |
|---|---|
| 新项目、Agent 应用、需要内置工具 | Responses |
| 兼容已有代码 / 只做简单文本补全 | Chat Completions |
| 需要服务端托管对话状态、减少 Token 重复发送 | Responses |
| 需要部署到第三方或本地推理服务 | Chat Completions |
| 需要多候选生成（`n > 1`） | Chat Completions |
| 需要完整推理摘要与工具联动 | Responses |

## 总结

Chat Completions 和 Responses API 目前都在维护，没有废弃关系。核心区别不是“新旧替代”，而是定位不同：

- **Chat Completions** 是通用的事实标准协议，兼容性最好，适合任何模型服务和简单对话场景。
- **Responses** 是 OpenAI 为 Agent 时代设计的新一代接口，提供内置工具、Agent 循环、会话状态管理和更丰富的输出结构，适合在 OpenAI 生态内构建复杂智能体应用。

如果你在构建多步骤、需要工具协作的 Agent 应用，Responses API 能显著降低工程复杂度；如果你的核心需求是“调一个模型拿结果”，Chat Completions 依然是最简单、最兼容的选择。
