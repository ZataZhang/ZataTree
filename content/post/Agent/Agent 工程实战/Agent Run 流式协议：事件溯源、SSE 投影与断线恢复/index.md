---
title: "Agent Run 流式协议：事件溯源、SSE 投影与断线恢复"
description: "把 Agent Runtime 的执行过程变成前端可稳定消费的流，关键不是把模型输出直接 pipe 给客户端，而是先把执行事实落库，再把事件投影到 SSE。本文记录我当前系统里的三层协议设计：Runner 端口事件、Canonical 事件库和 SSE wire format。"
date: 2026-09-07T10:30:00+08:00
slug: "Agent Run 流式协议：事件溯源、SSE 投影与断线恢复/index.md"
image: images/index/index.svg
categories:
    - Agent
tags:
    - Agent 工程实战
    - SSE
    - Protocol
draft: false
---

很多 Agent 系统的流式输出，本质上是把模型服务的 chunk 直接转发给浏览器。这样做上线很快，但一旦遇到刷新页面、断线重连、审计和取消，就会立刻发现：**前端消费的不是一个可恢复的事件流，而是一条一次性管道。**

我现在的做法是把协议拆成三层：Runtime 先产出领域事件，Adapter 统一映射成 canonical 事件并落库，最后由 SSE 端点从事件库里做投影。这篇文章记录这套协议的实际形态，以及它为什么这样设计。

## 一、三层结构

整条链路可以这样理解：

```text
Runtime / Runner
  └─ AgentEvent              执行器内部事件
      └─ Adapter 映射
          └─ AgentRunEvent   canonical 事实，落库并分配 seq
              └─ SSE 端点    committed event 的投影
                  └─ 前端
```

### Runner 端口层

`AgentEvent` 是 Runtime 对外的最小事件模型，目前有 7 种类型：

| 类型 | 专用字段 | 含义 |
| --- | --- | --- |
| `state_change` | `state` | Runtime 内部状态迁移 |
| `delta` | `content` | 模型文本增量 |
| `tool_call` | `tool_name` / `tool_call_id` / `tool_args` | 工具调用开始 |
| `tool_result` | `tool_name` / `tool_call_id` / `tool_result` | 工具结果摘要 |
| `artifact` | `artifact` | 结构化产物元数据 |
| `done` | `answer` | 最终答案全文 |
| `error` | `error_code` / `error_message` | 失败 |

这一层有意做薄。不管 Runtime 是 LangGraph、DeepAgents，还是新接的沙箱执行器，只要转换成这 7 类事件，后端后面的所有逻辑都不用重复实现。

### Canonical 层

Adapter 把 Runtime 事件映射成 canonical 事件。canonical 层不是照抄 Runtime 词汇，而是补齐运行生命周期：

| Canonical 事件 | 来源 | payload 要点 |
| --- | --- | --- |
| `run.started` | Adapter 生成 | `started_at` |
| `message.started` | Adapter 生成 | `message_id`、`role` |
| `message.delta` | `delta` | `message_id`、`content_index`、`delta` |
| `tool.call.started` | `tool_call` | `tool_call_id`、`tool_name`、`arguments` |
| `tool.call.completed` | `tool_result` | `result`、`result_checksum` |
| `artifact.created` | `artifact` | 产物 metadata |
| `message.completed` | `done` | `content`、`content_checksum` |
| `run.completed` | `done` 后置 | `message_id` |
| `run.failed` | `error` | `error.code`、`error.message`、`error.retryable` |
| `run.cancelled` | 取消路径 | `external_stop_confirmed` |

落库后的 envelope 长这样：

```json
{
  "run_id": "run_xxx",
  "seq": 4,
  "event_type": "message.delta",
  "occurred_at": "2026-09-07T10:30:00.123456",
  "recorded_at": "2026-09-07T10:30:00.126000",
  "agent_id": "freight_agent",
  "agent_snapshot_checksum": "...",
  "payload": { "message_id": "message_xxx", "delta": "..." },
  "payload_checksum": "...",
  "schema_version": 1,
  "trace_id": "...",
  "span_id": "..."
}
```

这里最重要的是 `seq`。Runtime 事件本身不携带权威序号；Adapter 只提交 candidate，repository 落库时按 `last_event_seq + 1` 分配。**事件一旦提交，顺序就是系统事实。**

## 二、SSE wire format

对外入口是：

```http
GET /api/agent-runs/{run_id}/events
```

SSE 使用命名帧：

```text
id: 4
event: message.delta
data: {"run_id":"run_xxx","seq":4,"event_type":"message.delta",...}

```

几个关键语义：

1. **重放优先。** 客户端可以用 `?after_seq=` 查询参数，也可以用标准 SSE 的 `Last-Event-ID` 请求头；服务端取较大值，然后从事件库里回放。
2. **游标安全。** 游标为负，或大于当前 `last_event_seq`，返回 422，避免客户端拿着错误游标等一个永远不会来的事件。
3. **实时推送。** 端点每 250ms 从 committed repository 拉取新事件；发现序号 gap 就断流，不静默跳过。
4. **keep-alive。** 空闲 15 秒发送 SSE 注释帧 `: keep-alive`。
5. **自然终止。** Run 进入终态且事件全部送完，连接主动关闭。

一次成功 Run 的典型序列：

```text
id: 1   event: run.started
id: 2   event: message.started
id: 3   event: message.delta
id: 4   event: tool.call.started
id: 5   event: tool.call.completed
id: 6   event: message.delta
id: 7   event: artifact.created
id: 8   event: message.completed
id: 9   event: run.completed
```

失败或取消时，终态分别是 `run.failed` 或 `run.cancelled`。Adapter 用一个终态闸保证三者最多出现一个。

## 三、为什么先落库，再投影

这是整套协议的核心取舍。

### 断线恢复变成查询问题

客户端刷新页面后，不需要 Runtime 重跑一遍，也不需要服务端缓存整个连接状态。只要带上 `Last-Event-ID: 5`，服务端就查询 `seq > 5` 的事件继续发。断线恢复从连接层问题退化成数据库查询问题。

### Runtime 崩溃不丢执行事实

事件写入 committed store 之后，Runtime 进程是否还活着，不影响前端重放历史。审计、排障和 UI 恢复消费的是同一份数据。

### 多 Runtime 共享同一套前端协议

不同执行器的事件风格可能差异很大。Adapter 负责把差异吸收在入口处，前端只认识 canonical 词汇。新增 Runtime 时，可以避免出现“沙箱一套流、业务 Agent 一套流”的分裂。

### 工具调用能稳定配对

`tool_call_id` 优先使用底层模型下发的 id。如果 Runtime 丢了开始事件，Adapter 会补发一个 `tool.call.started`，让 UI 仍然成对渲染。这个“配对自愈”很小心地只影响展示完整性，不把 Run 打成失败。

## 四、当前边界和改进方向

这套协议也有几个明显的边界。

**SSE 出口是客户端胖投影。** 目前 `data` 帧直接序列化完整 envelope，`agent_snapshot_checksum`、`provenance`、`payload_checksum` 等审计字段也被发给前端。短期省事，长期更适合收敛成只包含 `seq`、`event_type`、`occurred_at`、`payload` 的客户端投影。

**实时性靠 250ms 轮询。** 对文本流足够，但并发观看的连接多了，数据库查询会线性放大。合理演进是加一个进程内或跨实例 pub/sub，只负责“唤醒”轮询，不负责权威事件投递；事件仍然以数据库为准。

**内容模型只有文本增量。** `message.delta` 目前只有 `content_index` 和文本，没有结构化 content block。未来要支持图片、图表卡片或分块富文本，应增量引入 block 类型，而不是扩出新的顶层事件。

**`state_change` 是死词汇。** Runtime 端口定义了它，但 canonical Adapter 不会映射。后续应该删除或明确语义，避免接入方误以为它会被消费。

**协议演进规则需要写死。** 客户端对未知事件类型必须忽略，而不是报错。`schema_version` 目前存在，但配套演进策略还要补文档。

## 总结

这套协议不是行业标准，传输层用的也不是什么新东西，但它把几件事做对了：**事件先成为带序号的事实，SSE 只是投影；Runtime 词汇保持最小，canonical 词汇保持稳定；断线恢复用标准 SSE 游标；工具调用、产物、失败、取消全部事件化。**

如果要从这套设计里抽象一条通用经验，那就是：Agent 的远程流式接口不应该让客户端订阅“模型的输出过程”，而应该让客户端订阅“系统已经发生并且可恢复的执行事实”。管道可以丢，事实不应该丢。
