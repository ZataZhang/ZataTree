---
title: Agent 埋点接 ARMS：上报返回 success，控制台却是空的
description: "把 Agent Run 的 span 树接进阿里云 ARMS 的完整过程：gen_ai 语义约定怎么填、为什么 200 success 也可能是假象、地域和入口这两个坑怎么踩出来的、以及对话里带附件时 span 该怎么记。"
date: 2026-09-18T18:05:00+08:00
slug: "Agent-埋点接-ARMS：上报返回-success，控制台却是空的"
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

上报接口返回 `200`，响应体是两个引号包着的 `"success"`。控制台刷新了五遍，调用链分析里 `Span 数量: 0`。

第一反应当然是上报没成功。于是回头去查 payload、查鉴权、查代理——查了小半个小时，最后发现**数据一直都在，是我看的地方不对**。

这篇文章把这个过程完整记下来。前面是排查（含三个可以复用的判别实验），后面是这次顺带做的一个具体问题：**对话里带附件时，span 应该怎么记**。

> 前置概念（Trace 与 Span、父子关系、属性与事件的边界、上下文传递）见同系列 [Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点]({{< relref "post/Agent/Agent 工程实战/Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点/index.md" >}})。本篇不重复讲基础，直接从"接进 ARMS 之后为什么看不到"讲起。

## 一、`gen_ai.*` 到底是什么

动手之前先明确一件事：埋点里那一堆 `gen_ai.xxx` 不是我起的名字，是 **OpenTelemetry 的 GenAI 语义约定**（Generative AI semantic conventions）——社区为"生成式 AI / LLM 应用"单独定义的一套属性规范。

它解决的问题很朴素。没有规范时，同一个"模型名"会被写成 `model`、`model_name`、`llm.model`；"输入 token"叫 `prompt_tokens`、`input_tokens`、`usage.prompt`。结果就是**换个观测后端，埋点得重写一遍**。

约定把名字、类型、取值都钉死了，所以一份埋点能同时被 Langfuse、Phoenix、ARMS 正确解析。它大致覆盖五类：

| 类别 | 属性 | 说明 |
| --- | --- | --- |
| 操作身份 | `gen_ai.operation.name` | `chat` / `embeddings` / `invoke_agent` |
| 厂商与模型 | `gen_ai.provider.name`、`gen_ai.request.model`、`gen_ai.response.model` | provider 是判别字段 |
| 对话内容 | `gen_ai.input.messages`、`gen_ai.output.messages`、`gen_ai.system_instructions` | 结构化消息，见下文 |
| 用量与结果 | `gen_ai.usage.input_tokens`、`output_tokens`、`gen_ai.response.finish_reasons` | 成本核算靠这组 |
| 工具与会话 | `gen_ai.tool.name`、`gen_ai.tool.call.id`、`gen_ai.conversation.id` | 关联工具调用与多轮会话 |

其中 `input.messages` / `output.messages` 是**结构化**的，不是一段纯文本。每条消息是 `{role, parts[]}`，part 有这些类型：

| part 类型 | 必填字段 | 用在哪 |
| --- | --- | --- |
| `text` | `content` | 普通文本 |
| `uri` | `uri`、`modality` | 文件已在对象存储里，span 只记引用 |
| `file` | `file_id`、`modality` | 用厂商预上传能力（如 OpenAI Files API） |
| `blob` | `content`、`modality` | 只有必须内联时才用，base64 进 span 有成本也有合规风险 |
| `tool_call` / `tool_call_response` | `name` / `response` | 工具调用与结果 |

> 三个必须知道的坑：**这些属性绝大部分还是 `Development` 状态，会改名**——`gen_ai.system` 就被重命名成了 `gen_ai.provider.name`，`gen_ai.prompt.*` 也被 `input.messages` 取代；**结构化属性落不到 span 上**，OTel 的 Python SDK 只接受基本类型，所以得 `json.dumps` 成字符串再塞；**`input/output.messages` 是 Opt-In 属性**，规范明确说不该默认记录，因为可能含用户隐私。

## 二、span 树怎么设计

目标形态是一次 Agent Run 对应一棵 span 树，业务库的 Run 记录里存 `trace_id` 作为关联键：

```text
agent.run [run.id=run-xxx, user.id=demo-user-1, session.id=demo-session-1]
├─ agent.attach_document       file.uri / file.mime_type / file.size_bytes
├─ gen_ai chat                 gen_ai.input.messages / usage.* / latency_ms
├─ tool get_freight_quote      gen_ai.tool.name / gen_ai.tool.call.id / tool.result
└─ gen_ai chat                 基于工具结果的第二轮作答
```

写属性的部分收敛成几个 helper，别散在业务代码里——改名时只改一处：

```python
def set_llm_request(span, *, provider, model, messages, conversation_id=None):
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.provider.name", provider)
    span.set_attribute("gen_ai.request.model", model)
    if conversation_id:
        span.set_attribute("gen_ai.conversation.id", conversation_id)
    # system 消息按约定不进 input messages，单独走 system_instructions
    span.set_attribute(
        "gen_ai.input.messages",
        json.dumps(to_input_messages(messages), ensure_ascii=False),
    )
```

`to_input_messages` 里做两件事：把 system 消息摘出去、把文本统一截断。**截断不是可选项**——`input.messages` 里塞进一个 8000 字的 prompt，span 会大得没法用。

## 三、一个 200 success 的假象

配置填完，跑起来，日志里看到这一行：

```text
POST http://tracing-analysis-dc-sg.aliyuncs.com/adapt_<xx>_<xx>/api/otlp/traces HTTP/1.1" 200 9
```

`200`、响应体 9 字节（就是 `"success"` 加引号）。这种时候人很容易直接跳到"好，通了"，然后去控制台发现什么都没有，再回头怀疑人生。

我做了三个实验来定位问题到底在链路哪一段。这三个实验本身挺通用，值得记：

| 实验 | 操作 | 结果 | 排除了什么 |
| --- | --- | --- | --- |
| 绕过本地代理 | `--noproxy '*'` 直连重发 | 同样 `200 "success"` | 不是代理伪造的响应 |
| 发垃圾 payload | `head -c 300 /dev/urandom` 当 body 发过去 | `400 Bad Request` | 网关**真的在解析** protobuf，不是无脑返回成功 |
| 伪造 license key | 把 `/adapt_.../` 换成随机串 | `403 Forbidden` | key 是**有效**的，且服务端会校验 workspace |

三个实验做完，结论就很硬了：**数据确实被服务端收下了**，而且收进了一个合法的 workspace。既然服务端没问题，那"看不到"就只剩一种可能——**去看的那个地方，不是数据所在的地方**。

![诊断切段图：把上报链路切成 Agent 进程、本地代理、ARMS 网关、控制台四段，实验①绕过代理排除代理伪造，实验②发垃圾字节得到 400 排除网关不解析，实验③伪造 license key 得到 403 证明 key 有效，四段全部通过后剩下唯一的失败段是控制台的地域、页签与页面作用域](images/index/diagnosis.svg)

事实也确实如此。

## 四、三个坑

### 坑一：地域

接入点是 `tracing-analysis-dc-sg.aliyuncs.com`，`dc-sg` 就是**新加坡**。而控制台默认停在别的地域，调用链分析自然是空的。

| | |
| --- | --- |
| **症状** | 上报 `200 success`，控制台调用链分析 `Span 数量: 0`，左侧所有维度显示"没有匹配的值" |
| **原因** | 控制台地域与接入点地域不一致。数据在 `ap-southeast-1`，眼睛在别处 |
| **修复** | 控制台切到与接入点同地域；`应用列表` 也要在同地域看 |

这类问题最坑的地方在于：**它不报错**。上报端一切正常，服务端一切正常，只有"人对不上"。

### 坑二：入口

地域切对之后，还有第二层错位。控制台里同一个应用有不止一个入口：

- **应用列表** 分 `OpenTelemetry` 和 `ARMS` 两个页签。通过 OTel SDK 上报的应用只出现在前者；后者是 ARMS 探针接入的应用列表。看错页签 = 看到空列表。
- **应用维度的调用链分析** 是带过滤的。我一度搜索框里直接粘 trace_id，仍然是 0 —— 因为页面作用域被钉死在某个应用上，搜索条件没换掉"应用"这个更大的前提。页面里搜出来的搜索框内容长这样：

```text
serviceName:"agentrun-agent-quick-oUpbu" and resources.acs.arms.service_id : "azmulz8rp8..."
```

第三段 `resources.acs.arms.service_id` 是 ARMS 探针注入的资源属性。**OTel 自己上报的 span 根本没有这个属性**，所以这个条件永远匹配不上。

| | |
| --- | --- |
| **症状** | 搜 trace_id 也搜不到；应用列表某个页签永远是空的 |
| **原因** | 页面作用域（应用 / 页签）与数据的归属不匹配 |
| **修复** | 换到不绑定单个应用的入口，或把搜索条件改成 `serviceName:"<你的服务名>"` |

### 坑三：配置写法

第三个坑不致命，但错误信息很难自查，因为**不报错**：

```bash
# 错的：ARMS 的 header 不是 Authorization: Bearer
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer <token>

# 对的：HTTP 接入点鉴权编码在 /adapt_<xx>_<xx>/ 路径里，headers 留空
OTEL_EXPORTER_OTLP_ENDPOINT=http://tracing-analysis-dc-sg.aliyuncs.com/adapt_<xx>_<xx>/api/otlp/traces
OTEL_EXPORTER_OTLP_HEADERS=

# 只有 gRPC 才需要 header，格式是 Authentication=<token>
OTEL_EXPORTER_OTLP_ENDPOINT=http://tracing-analysis-dc-sg.aliyuncs.com:8090
OTEL_EXPORTER_OTLP_HEADERS=Authentication=<token>
```

还有一条同类的：HTTP 接入点**自带** `/api/otlp/traces`，不要再拼 `/v1/traces`——那是本地 Jaeger 的写法，拼上去就是 404。

## 五、对话里带附件怎么记

这是这次真正想解决的问题：Agent 的对话里带了文件，trace 上该怎么表达。

关键决定是**文件不进 span 的字节流**。做法是三处落点：

| 位置 | 记什么 |
| --- | --- |
| `agent.attach_document` span | `file.uri` / `file.mime_type` / `file.size_bytes` / `file.doc_id` |
| `gen_ai chat` 的 `gen_ai.input.messages` | 该条 user 消息的 `parts` 里一个 `uri` part + 一个 `text` part |
| 业务库 | 文件归属业务层（doc_id ↔ Run），trace 里只留引用 |

![三层落点图：左边对象存储是唯一保存文件字节的地方；中间 trace 用 agent.attach_document 记 file.uri 与规模，用 gen_ai.input.messages 的 text、uri、text 三个 part 记模型看到的内容；右边业务库用 trace_id 关联两层](images/index/attachment.svg)

实测落进 ARMS 的属性长这样：

```json
[{"role": "user", "parts": [
  {"type": "text", "content": "按附件里的信息报价"},
  {"type": "uri", "uri": "oss://bucket/uploads/doc-adcc4d1f/booking-note.txt",
   "modality": "document", "mime_type": "text/plain"},
  {"type": "text", "content": "订舱委托书 / BOOKING NOTE\n委托编号：BN-2026-0918-075…"}
]}]
```

三个设计取舍值得说一下：

**第一，`uri` part 和 `text` part 成对出现。** `uri` 是溯源（文件从哪来），`text` 是模型真正读到的内容（服务端预抽取的结果）。只记 `uri`，排查时无法回答"模型到底看没看到附件"；只记 `text`，又丢了文件来源。两个都记才查得动。

**第二，`modality` 是必填。** `uri` 和 `file` part 都要求这个字段，取值 `image` / `video` / `audio` / `document`。容易漏，漏了后端可能直接忽略这个 part。

**第三，模型调用侧和 trace 侧要分开构造。** 应用侧消息保留结构化内容（`{type: "text"}` / `{type: "document"}`），发给 OpenAI 兼容端点时拍平成纯文本；转成 `gen_ai.input.messages` 时才展开成 uri + text。这样两边各取所需，不会为了迁就某一方而变形：

```python
# 模型侧：附件以抽取文本注入
def to_openai_content(content):
    if isinstance(content, str):
        return content
    chunks = []
    for item in content:
        if item["type"] == "text":
            chunks.append(item["text"])
        elif item["type"] == "document":
            chunks.append(f"[[附件 {item['uri']}]]\n{item['extracted_text']}")
    return "\n\n".join(chunks)
```

验证方式是让模型复述附件里的独有信息——它在回答里用上了委托书的 `ETD 2026-09-25`、截关时间和"14 天免箱期"。这说明附件确实进了模型上下文，不只是进了 span。

顺手补的一个洞：`BatchSpanProcessor` 默认靠 `atexit` 冲刷，进程被强杀（Ctrl-C、沙箱超时）时最后一批 span 会丢。Run 结束处显式 `force_flush()` 更稳。

## 六、数据怎么拿出来给 AI 看

控制台是给人看的，AI 想自己查得走另外三条路：

**1. OpenAPI**（免费，最直接）。`xtrace` 产品两个接口就能拼出一个导出脚本：

| 接口 | 作用 | 关键参数 |
| --- | --- | --- |
| `SearchTraces` | 按条件列出调用链，返回 TraceID 列表 | `RegionId`、`StartTime`/`EndTime`（毫秒）、`ServiceName`、`OperationName`、`MinDuration`、`Tag`、`PageNumber`/`PageSize` |
| `GetTrace` | 按 TraceID 取完整 span 明细 | `TraceID`、`RegionId` |

翻页拿 ID，再逐条取详情，落地成 JSON 就完了。

**2. 可观测 MCP Server**（`aliyun/alibabacloud-observability-mcp-server`）。Go 单二进制，里面正好有对应的工具：

```json
{
  "mcpServers": {
    "alibaba_cloud_observability": {
      "command": "./bin/alibabacloud-observability-mcp-server",
      "args": ["start", "--stdio"],
      "env": {
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "<AK>",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "<SK>",
        "ALIBABA_CLOUD_REGION": "cn-singapore"
      }
    }
  }
}
```

接上之后可以直接问"昨天耗时最长的几条 Run 是什么，`gen_ai.input.messages` 里带没带附件"，由 `umodel_search_traces` / `umodel_get_traces` 去取。两个注意点：用只读 RAM 用户（`AliyunARMSReadOnlyAccess`），别用主账号 AK；`sls_text_to_sql`、`sls_sop` 这类 AI 工具走 STAROps 单独计费，不需要就在 `config.yaml` 的 `enabled_tools` 里关掉。

**3. Collector 双写**。反正上报端在自己手里，OTel Collector 同一份数据同时投 ARMS 和本地存储（ClickHouse / 文件 / 对象存储）。本地那份没有 AK、没有分页、随便 SQL——**AI 分析用它比用控制台 API 舒服得多**。ARMS 负责看瀑布图和告警，本地那份负责喂给 Agent。

## 总结

几个收获，都是这次真金白银换来的：

**1. 200 不等于数据可用。** `"success"` 只说明网关收了，说明不了数据落到了你正在看的那个地方。判断"到底通没通"要有独立证据——我这次用的是"发垃圾字节看它报不报错"和"伪造 key 看它拦不拦"，两个实验各一次请求，就能把链路切段定位。

**2. 可观测性接入的坑，多半在"人对不上"而不是"数据不通"。** 地域、页签、页面作用域、filter 条件，这四样任何一个不对，现象都是同一个：空列表。而且全都不报错。排查时优先怀疑这个，比怀疑 SDK 划算。

**3. 约定比实现重要。** 用 `gen_ai.*` 的收益在这次很直观：同一份埋点，改个 endpoint 就从本地控制台切到了 ARMS，一行代码没动。代价是要接受它还在 `Development`、会改名——所以属性写入必须收敛到 helper 里。

**4. 文件类数据，"引用 + 摘要"比"内容"有用。** 把 pdf 塞进 span 不会让排查更容易，只会让它更贵更难搜。`uri` part 记来源、`text` part 记模型看到的内容、业务库存文件本身，三层各司其职。

**5. 顺手能修的洞就别留着。** `force_flush()` 这种一行的事，不补就是"偶发丢 trace"，而偶发丢 trace 是最难查的那类问题——它会让上面所有的排查经验都建立在错误的观察上。
