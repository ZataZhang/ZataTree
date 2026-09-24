---
title: Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点
description: "用一次『慢』的 Agent Run 讲清 Trace、Span、父子关系、属性与事件的分工，Traces/Metrics/Logs 三根柱子各自回答什么问题，以及 OpenTelemetry 的埋点 API、上下文传递在 Agent 场景下会断在哪里（含 2026-03 Span Event API 弃用的影响）。"
date: 2026-09-22T09:51:00+08:00
slug: "Agent-Tracing-基础：Trace-Span-与-OpenTelemetry-埋点"
image: images/index/index.svg
categories:
    - Agent
tags:
    - Agent 工程实战
    - Agent Tracing
    - 可观测性
    - OpenTelemetry
draft: false
---

用户说：这个 Agent 回答一个问题要 40 秒。

我去 grep 日志，符合条件的只有一行：

```text
2026-09-20 14:02:11 INFO  run finished  run_id=run-7f3a  elapsed=41.3s
```

41.3 秒，和用户说的对得上。然后呢？没有然后了——**日志告诉你"慢"，但告诉不了"慢在哪一步"**。

于是我加 print：在每轮 LLM 调用前后打一行，在每次工具调用前后打一行。半小时后日志变成这样：

```text
14:01:30 LLM #1 start
14:01:37 LLM #1 done
14:01:37 tool web_search start
14:02:01 tool web_search done
14:02:01 LLM #2 start
14:02:16 LLM #2 done
```

能看了，但问题也很明显：这些行**彼此之间没有关系**。换个用户并发进来，两组行就交织成一片；想知道"哪一步占了这 41 秒"，还得靠人肉减时间戳。更别说线上没有 print，只有一条 `run finished`。

这篇文章要解决的，就是把这个"人肉减时间戳"的过程，换成一套有结构、能自动关联的数据。这正是 **Tracing** 干的事。

## 一、Trace 与 Span：一次 Agent Run 就是一棵树

先建立两个最基础的概念，用上面那个 run 当例子。

**Trace（链路）**：一次完整请求的全过程，有一个全局唯一的 `trace_id`。上面这次调用对应一条 trace。

**Span（跨度）**：trace 里的一段工作，有名字、有开始时间、有结束时间，可以有属性和事件。上面每一行 print，本质上都是一个 span。

Span 之间靠 **父子关系** 组织成树。上面那次 run 画成 span 树是这样的：

```text
agent.run                    run.id=run-7f3a  session.id=s-12        [t=0.0 → 41.3s]
├─ gen_ai.chat 第 1 轮        gen_ai.request.model=某模型             [t=0.2 → 6.8s]
├─ tool.web_search           tool.name=web_search                   [t=7.0 → 24.1s]  ← 元凶
├─ gen_ai.chat 第 2 轮        gen_ai.usage.input_tokens=4821          [t=24.3 → 39.6s]
└─ agent.finalize                                                  [t=39.7 → 41.2s]
```

树的形状一出来，答案就自己浮上来了：**24.1 秒花在 `web_search` 上，占掉一半以上**。不需要减时间戳，不需要猜。

这里有三点值得单独说清楚，因为后面所有的坑都出在这三件事上。

**第一，父子关系是"包含"关系，不是"先后"关系。** 子 span 的时间区间落在父 span 区间内。父 span 的耗时不是子 span 的加总——`agent.run` 是 41.3 秒，四个子项加起来也差不多，但如果两个子 span 时间重叠，说明它们在并行，加总就会超过父 span。**时间重叠 = 并发**，这是 span 树比日志强的最直观的一点。

**第二，根 span 只有一个。** 一次 run 对应一个 `agent.run` span（root span），其余都是它的后代。`trace_id` 相同、`parent_span_id` 串起来，就构成了这次 run 的完整路径。排查时从 root 往下看，就是一条推理链。

**第三，span 可以跨进程。** 一次 Agent Run 里，`tool.web_search` 很可能不是本地函数，而是打到一个远程服务甚至别人的 MCP Server 上。只要上下文传得过去（第五节讲），那边产生的 span 会挂到你这棵树上，变成你 trace 的一部分。

## 二、属性与事件：span 上该记什么

有了 tree 骨架，还得有内容。span 上能挂两类东西：**属性（Attributes）** 和 **事件（Events）**。这两个词经常被混用，但分工很清楚。

| | 属性 Attributes | 事件 Events |
| --- | --- | --- |
| 形态 | 键值对，附着在 span 上 | 带时间戳的独立记录 |
| 回答的问题 | 这个 span **是什么** | 这个 span **过程中发生了什么** |
| 典型时机 | span 存续期间的任何时刻 | 某个确定的时间点 |
| 主要用途 | 筛选、分组、聚合 | 还原时间线、记录离散动作 |
| Agent 里的例子 | `gen_ai.request.model`、`gen_ai.usage.output_tokens`、`tool.name` | 重试一次、首个 token 到达、工具返回、抛异常 |

一个够用的判断口诀：**能被拿来当筛选条件的，放属性；只在某一刻发生、要看"什么时候"的，放事件。**

- "所有用了 A 模型的 run 平均耗时多少" → 模型名必须是属性（要聚合)。
- "这次 run 重试了 3 次，每次间隔多久" → 重试是事件（要看时刻）。

在 Agent 语境里，属性这块已经有一份现成的答案：**OpenTelemetry 的 GenAI 语义约定**（`gen_ai.*`）。模型名、token 用量、工具名、会话 id 该叫什么，规范里都钉死了，照着填就能被各种观测后端正确解析。这份约定的字段清单和几个已知的坑，我在 [Agent 埋点接 ARMS]({{< relref "post/Agent/Agent 工程实战/Agent 埋点接 ARMS：上报返回 success，控制台却是空的/index.md" >}}) 里已经逐条整理过，这里只补一条最容易踩的边界：

> **属性会被当成聚合维度，所以基数要有意识。** `run.id`、`session.id` 这种每次都不一样的值，挂在 span 上当属性没问题（trace 是按 `trace_id` 检索的，不存在"按属性建索引"的压力）；但如果这些属性被顺手套进了 Metrics 的维度里，一张指标卡片就会被炸成几万条时间线。分界线不是"能不能当属性"，而是"这个字段会不会流进指标聚合"。同样地，`gen_ai.input.messages` 这类可能含用户隐私的字段，规范明确标成了 Opt-In，不该默认记录。

**事件这块有一件新变化，值得单独提醒。** OTel 在 **2026 年 3 月**宣布弃用 **Span Event API**（也就是 `Span.AddEvent` / `Span.RecordException`），原因是"span 事件"和"日志事件"两套并行的机制造成了重复和困惑。新的事件应该走 **Logs API**，通过上下文与当前 span 关联。需要注意边界：

- 这是**弃用 API，不是删除能力**。`add_event()` 现在还能用，存量数据和在 trace 视图里看事件也照常工作。
- 建议是：新写的埋点别再加对 `add_event()` 的新依赖；自己封装的异常上报，优先走日志库 + OTel 日志桥接，它会自动带上 `trace_id` / `span_id`。

如果你现在就在写埋点，实操上可以这么记：**属性照旧填在 span 上；"某一刻发生了什么"优先记一条结构化日志**——既符合新方向，也天然可搜索。

## 三、Traces、Metrics、Logs：三根柱子各自回答一个问题

到这可能会有一个误解：既然 tracing 这么好，是不是日志和指标就不需要了？

不是。它们是三种不同粒度的问题，互相不能替代：

| 信号 | 回答 | Agent 里的典型用法 |
| --- | --- | --- |
| **Metrics** | "**多少 / 趋势**" | 成功率、P95 延迟、token 消耗与成本、工具错误率 |
| **Traces** | "**哪里 / 路径**" | 单次 run 的完整执行路径、哪一步慢、哪一步失败 |
| **Logs** | "**具体是什么**" | prompt/response 全文、工具入参出参、异常堆栈 |

换个说法：**指标告诉你"出问题了"，trace 告诉你"出在哪个环节"，日志告诉你"那个环节具体发生了什么"。**

三者真正的威力在**关联**。Agent 场景里最常见的一条排查路径长这样：

```text
① 指标：今天 token 消耗比昨天涨了 40%     ← Metrics 发现异常
② 点开这张图的某个时间点                  ← 靠 exemplar 带出 trace_id
③ 落到那一次 run 的 span 树               ← 看到工具被循环调用了 12 次
④ 跳到对应 span 的日志                    ← 看到检索关键词空字符串，导致反复搜
```

这条链要成立，靠的是一个共同的锚点：

> **`trace_id` 是把三根柱子缝在一起的线。** 指标里带 exemplar 引用 trace，日志记录里带 `trace_id`/`span_id`，trace 上挂结构化的 usage 属性——三条路径都指向同一根线，你才能从"指标异常"一路点到"具体那次请求的日志"。

反过来说，如果日志里没有 `trace_id`，这套关联就断了，你又要回到"人肉 grep + 减时间戳"。

## 四、OpenTelemetry 埋点：从 API 到 span 树

OTel 的埋点 API 其实只有三层，理解了这个层次就不会写乱：

```text
TracerProvider   一个进程一个，负责"把 span 送去哪里"（exporter / processor）
   └─ Tracer    按模块命名，比如 "agent.runtime"、"agent.tools"
        └─ Span  一次具体操作，就是树上的一个节点
```

最小可运行的接线（`opentelemetry-sdk 1.44.0`，2026-09 的版本）：

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("agent.runtime")
```

埋点本身，推荐用上下文管理器——它保证**异常也会结束 span**：

```python
with tracer.start_as_current_span("agent.run") as span:
    span.set_attribute("run.id", run_id)
    span.set_attribute("gen_ai.conversation.id", session_id)

    with tracer.start_as_current_span("gen_ai.chat") as chat:
        chat.set_attribute("gen_ai.request.model", model)
        chat.set_attribute("gen_ai.usage.input_tokens", usage.input_tokens)
```

注意 `start_as_current_span` 里的 **current** 两个字——它做的事情是"把新 span 设为当前 span 并放进上下文"，下一个 span 创建时就会自动认它当爹。**父子关系不是手写的，是从上下文里自动读出来的**。这也解释了为什么上下文一丢，span 树就会散成一片（下一节）。

如果用现成的框架，通常不需要手写这些。LangChain / LangGraph 走 callback，OTel 有 instrumentation 包能自动建 span；纯手写的 Agent Runtime 才需要自己决定"哪些动作值得单独一个 span"。我的经验是：

- **值得建 span**：一次 LLM 调用、一次工具调用、一次检索、一次子 Agent 委派、一次 run 的起止。
- **不值得建 span**：纯粹的参数拼装、字符串裁剪。这类动作建 span 只会让树变胖，真要记录就记事件/日志。

## 五、上下文传递：让父子关系不断链

这是入门到能用之间最容易被绊倒的一节。OTel 的上下文（Context）在 Python 里建立在 `contextvars` 之上，含义是"当前执行流里，此刻的当前 span 是谁"。它有两个天然的断裂点。

### 5.1 进程内：异步任务与线程池

`asyncio` 里 `await` 前后的上下文是连续的，一般不会丢。但下面这些会丢：

```python
# 断链：新线程不会继承父线程的上下文
executor.submit(do_work)          # do_work 里 get_current_span() 拿到的是 INVALID_SPAN（不记录的占位）

# 补救：显式把上下文复制过去
import contextvars
ctx = contextvars.copy_context()
executor.submit(ctx.run, do_work)
```

同理，`process` 池、Celery 之类的任务队列，都必须**显式把上下文当参数传过去**，再在另一端 `attach`。这类 bug 的表现很有辨识度：**span 数量是对的，但全是平铺的——每个都是 root，没有父子关系**。

### 5.2 跨进程：W3C Trace Context

跨服务传递靠的是 W3C 标准的 `traceparent` 头：

```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             │  └── trace_id (32 hex) ─────────┘ └─ parent ──┘ └flags
             └ version
```

注入和提取都是现成的：

```python
from opentelemetry import propagate

# 发送方：把当前上下文写进 HTTP header
headers = {}
propagate.inject(headers)          # -> {'traceparent': '00-...'}

# 接收方：从 header 还原上下文，再建 span 就会挂上去
ctx = propagate.extract(received_headers)
with tracer.start_as_current_span("remote.tool", context=ctx):
    ...
```

只要用了带自动埋点的 HTTP/gRPC 客户端，这一步通常是零成本的。**但 Agent 场景有几个地方容易漏**：

- **自己实现的流式接口**（SSE 推 run 事件给前端）：手写的 `fetch` 或自定义协议不会自动带头，得手动 `inject`。
- **调用远程 MCP Server**：这是最常漏的一处。MCP 的请求里如果没带 `traceparent`，那边的 span 就是一棵独立的树，你的 trace 到工具调用这一步就断了。
- **后台任务**：异步评估、异步摘要、定时任务，这些不在请求链路里，需要**显式**把发起时的上下文带过去，否则它们永远是孤儿 span。

> 一个自查方法：跑一次完整 run，数一下 trace 里 root span 有几个。**健康的 trace 只有一个 root**；出现多个 root，说明某处上下文断了，去上面三个地方找。

## 六、三个最常见的坑

按"症状 → 原因 → 修复"记，方便回头查。

**症状一：树是平的，所有 span 都是 root。**
原因是上下文在异步/线程边界断了。
修复：线程池用 `contextvars.copy_context()` 包一层；跨进程检查 `traceparent` 是否真的发出去了（抓一次包最快）。

**症状二：某个 span 永远不结束，trace 一直在长。**
原因是走了 `start_span()` 手动模式却忘了 `end()`，或者异常路径上没走到 `end()`。
修复：默认用 `start_as_current_span()` 上下文管理器；确需手动模式就套 `try/finally`。

**症状三：属性没上去，或者上报报类型错误。**
原因是 OTel 的属性只接受**基本类型**（字符串、数字、布尔和它们的数组），结构化对象塞不进去。
修复：结构化内容先 `json.dumps()` 成字符串；同时想清楚这个字段是不是该进指标维度。

## 七、速查表

| 概念 | 一句话 | Agent 里对应什么 |
| --- | --- | --- |
| Trace | 一次完整请求的全过程，有唯一 `trace_id` | 一次 Agent Run |
| Span | 一段有起止时间的工作，树上的一个节点 | 一次 LLM 调用 / 工具调用 |
| 父子关系 | 子 span 时间落在父 span 内，靠上下文自动建立 | `agent.run` → `tool.web_search` |
| 属性 | 键值对，描述 span"是什么" | `gen_ai.request.model`、`tool.name` |
| 事件 | 带时间戳，记录"某一刻发生了什么" | 重试、首个 token 到达、异常 |
| Metrics | 回答"多少 / 趋势" | 成本、成功率、P95 延迟 |
| Logs | 回答"具体是什么" | prompt/response、工具入参出参 |
| 上下文传递 | `contextvars`（进程内）+ `traceparent`（跨进程） | MCP 调用、SSE 流式、后台任务 |

## 几点收获

- **先问"我要回答什么问题"，再决定用什么信号。** "慢在哪一步"是 trace 的问题，"涨了多少"是指标的问题，硬用日志去回答前两个，就会退化成打印追踪。
- **属性填得对不对，看它能不能被拿来筛。** 能筛的放属性，只能看时刻的放事件，这个口诀能解掉八成的纠结。
- **上下文是隐式的全局状态，隐式的东西最容易断。** 凡是跨了线程、跨了进程、跨了任务队列的边界，都要问一句"当前 span 传过去了吗"。
- **`trace_id` 是整个可观测性的粘合剂。** 日志里印上它、指标 exemplar 里带上它，三根柱子才真正连成一张网。
- **规范在变，别把 `add_event()` 写进新代码。** Span Event API 已经在 2026 年 3 月弃用，新的事件走 Logs API，能力不减，方向更统一。

---

> 基础篇到此，概念就这些。下一步是把它接到具体的观测后端上——`gen_ai.*` 字段怎么填、上报成功但看不到数据怎么办，这些实战里的坑见下一篇 [Agent 埋点接 ARMS]({{< relref "post/Agent/Agent 工程实战/Agent 埋点接 ARMS：上报返回 success，控制台却是空的/index.md" >}})。
