---
title: "阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍"
description: "同一个百炼模型，联网搜索至少有三条入口：Chat Completions 的 enable_search、Responses API 的 web_search 工具、以及 MCP 广场的联网搜索 MCP。它们的能力、计费和踩坑完全不同。本文按我实测的顺序，把每条路的真实行为写清楚。"
date: 2026-09-07T19:40:00+08:00
slug: "阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍"
image: images/index/index.svg
categories:
    - Agent
tags:
    - Agent 工程实战
draft: false
---

给 Agent 接搜索的时候，我以为阿里云百炼的联网搜索就是「一个开关」。实测下来发现完全不是：同一个模型，至少有三条完全不同的搜索入口——Chat Completions 的 `enable_search` 参数、Responses API 的 `web_search` 工具、以及 MCP 广场里的联网搜索 MCP。三者的触发方式、来源返回、计费方式都不同，混着看文档很容易得出「阿里云搜索不行」的错误结论，而实际上只是走错了入口。

这篇文章按我踩坑的顺序写：先说我怎么在错误的入口上浪费了一轮调试，再写正确入口的实测行为，最后把三条路的差异列成表，给一个选型判断。

## 一、Chat Completions + enable_search：会「假装成功」的入口

我的第一版代码走的是 OpenAI-compatible Chat Completions，请求里加了 `extra_body={"enable_search": True}`。请求返回 200，模型照样生成了一段关于 vLLM 的详细回答——看起来一切正常。

直到我想找引用来源才发现：响应里没有任何搜索相关字段。没有 `search_results`，没有 `web_search_info`，没有任何元数据。我又加了一堆参数组合（`search_options.forced_search`、`enable_source` 等文档里能搜到的字段）反复试，结论都一样：**这个私有部署的百炼端点在 Chat Completions 协议下，搜索扩展参数被静默忽略了**。

这类问题最麻烦的地方在于它不报错。请求成功、回答流畅，模型甚至会用「根据最新资料」开头——但那全是参数化记忆在演戏。如果你不检查来源字段，很容易把这种回答当成「搜索生效了但质量一般」，然后得出完全错误的结论。

后来在文档里翻到关键一句：Responses API 暂不支持 `enable_source` 等参数，来源要用专门的方式取——这句话反过来提醒我，这些参数本来就属于不同的协议层。Chat Completions 的搜索行为在不同部署形态下表现不一致，而 Responses API 是明确支持联网搜索的入口。

## 二、Responses API + web_search：能跑通的正路

换成 Responses API 之后，接法反而更简单了。不需要任何 `enable_search` 之类的开关，直接在 `tools` 数组里声明工具：

```python
from openai import OpenAI

client = OpenAI(
    api_key=api_key,
    base_url="https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
)
response = client.responses.create(
    model="qwen3.7-flash",
    input="今天的 GitHub trending",
    tools=[
        {"type": "web_search"},      # 搜索
        {"type": "web_extractor"},   # 抓取网页正文
    ],
    stream=True,
)
```

两个工具的分工和我在 Agent 里自己包搜索工具时的经验一致：`web_search` 负责查，`web_extractor` 负责读正文。文档建议再配上 `code_interpreter`，但多数搜索场景用不上。

实测下来有几个值得记录的行为细节。

**来源不在正文里，在 output 数组里。**提取方式：

```python
for item in response.output:
    if item.type == "web_search_call":
        for source in item.action.sources:
            print(source.url)
```

Responses API 目前不支持 `enable_source`、`enable_citation`、`citation_format`，不会在正文里自动插 `[1]` 角标。要角标标注得走 DashScope 原生调用——这是三条入口差异最直观的一处：同样的搜索，Responses 给你原始链接列表，DashScope 原生给你排版好的引用。

**流式事件是真实可用的。**`response.web_search_call.searching` / `completed` 标记搜索阶段，`response.output_text.delta` 是正文增量。但有一个体验坑：SSE 事件存在批量下发——我实测中 `in_progress`、`searching`、`completed` 三个事件几乎同一时刻到达（23.9s），之前模型明显已经在搜了。如果你做前端 UI，别指望靠这些事件展示即时的「搜索中」状态，最好在请求发出时本地先打一行提示。

**耗时差距很大。**同一问题「今天的 GitHub trending」（qwen3.7-flash）：

| 工具组合 | 实测耗时 |
| --- | --- |
| 只开 `web_search` | 约 14 秒 |
| `web_search + web_extractor` | 约 46–67 秒 |

`web_extractor` 会触发多轮网页抓取，模型要读正文再综合，时间翻三四倍。概览类问题用 `web_search` 就够；需要精确总结文档内容时再开 extractor。

**模型的搜索结果也有时效性陷阱。**即便搜索成功，拿它答「今天 GitHub trending」时，返回的项目列表在不同请求间差异很大，星标数明显不可靠。厂商侧搜索解决的是「能拿到网页」，不解决「网页本身可信」——这部分判断仍然要靠你的 prompt 约束。

## 三、计费：别把它当成模型调用的一部分

这是容易被忽略但必须算清的部分。Responses API 的联网搜索费用分两块：

1. **模型调用费**：搜索到的网页内容拼进提示词，输入 token 按模型标准价格计费。
2. **搜索策略费**：按调用次数收费。turbo 策略 3 元/千次、max 策略 4 元/千次（2026 年 2 月起正式计费，华北 2 地域）；agent 策略 4 元/千次。

也就是说一次带搜索的调用，实际成本 = 模型 token 费 + 搜索次数费，而搜索会把大量网页内容塞进上下文，token 那头的增量往往比搜索费本身更贵。

MCP 广场的「联网搜索 MCP」是另一套独立服务，计费也独立：所有用户前 2000 次调用免费，之后 29 元/千次。它和 Responses API 的内置搜索互不相通——这是很多人（包括我一开始）搞混的地方。

## 四、能力矩阵：三条协议到底差在哪

把官方的能力表和我的实测合在一起看，差异就清楚了。核心结论只有一句：**DashScope 原生协议支持全部进阶功能，OpenAI 兼容协议（无论 Chat Completions 还是 Responses）都只是阉割版**。

| 功能特性 | DashScope | OpenAI 兼容 Chat Completions | OpenAI 兼容 Responses |
| --- | --- | --- | --- |
| 基础联网搜索 | ✅ | ✅ | ✅ |
| 强制联网搜索 | ✅ | ✅ | ❌ |
| 搜索量级策略（turbo / max / agent） | ✅ | ✅ | ❌ |
| 垂域搜索 | ✅ | ✅ | ❌ |
| 搜索时效性设置 | ✅ | ✅ | ❌ |
| 限定搜索来源站点 | ✅ | ✅ | ❌ |
| 自然语言干预检索范围 | ✅ | ✅ | ❌ |
| **返回搜索来源** | ✅ | ❌ | ❌ |
| **角标引用标注** | ✅ | ❌ | ❌ |
| 提前返回搜索来源 | ✅ | ❌ | ❌ |
| 图文混合输出 | ✅ | ✅ | ❌ |

这张表解释了我前面踩的所有坑：Chat Completions 能搜但拿不到来源；Responses API 虽然也不支持「来源返回参数」，但通过 output 数组里的 `web_search_call.action.sources` 可以把链接提取出来；强制搜索、策略设置、时效性、站点限定这些进阶控制，Responses 一律不支持。**如果你的场景需要来源验收、时间范围约束或站点限定，DashScope 原生协议是唯一完整解。**

## 五、search_strategy：四个档位，一次讲清

搜索策略是比协议选择更影响结果质量的参数。四个档位：

| 策略 | 行为 | 适用场景 |
| --- | --- | --- |
| `turbo`（默认） | 兼顾速度与效果 | 日常查询 |
| `max` | 调用多源搜索引擎，结果更全 | 高精度、多源交叉验证 |
| `agent` | 多轮调用搜索工具与大模型，多轮检索与内容整合 | 研究报告；英文场景推荐 |
| `agent_max` | agent 基础上加网页抓取 | 仅限 qwen3-max 思考模式 |

几个关键限制值得记下：

- **`agent` 和 `agent_max` 启用时，只支持 `enable_source: true`，其他联网搜索功能全部不可用**——开了多轮检索就牺牲参数控制，这是硬约束。
- `agent` 策略对模型有要求：Qwen3-Max 系列、Qwen3.5/3.6/3.7 系列可用；Qwen3.8、MiniMax-M2.1、Moonshot-Kimi-K2 与角色扮演模型不支持。走 text 端点时**必须用流式调用**。
- 不同模型处理时效数据的能力不同：qwen3-max 具备日期推理能力（能识别非交易日并提示无数据），qwen-max 会直接返回搜索到的过期数据。股价等强时效查询选 qwen3-max 或更新版本。

我的实测数据可以直接对应到档位：只开 `web_search`（近似 turbo）约 14 秒；加 `web_extractor`（行为上接近 agent_max 的抓取）约 46–67 秒。文档说 agent 策略「响应时间可能更长」不是客气话。

## 六、联网搜索 MCP：第四条路

MCP 广场的「联网搜索 MCP」和上面三条协议层能力完全独立——独立实现、独立计费，也独立于你选哪条 API 协议。所有用户前 2000 次调用免费，之后 29 元/千次。它适合的场景是：多个 Agent / 多个模型要共享同一个搜索出口，不想每条协议各接一遍。

## 七、我的判断

如果你在百炼上做 Agent 搜索，我的建议很短：

1. **先想清楚要什么再选协议**。需要来源验收、时效控制、站点限定 → DashScope 原生；只要基础搜索且想用 OpenAI SDK → Responses API；Chat Completions 只适合「搜到了就行」、不关心来源的场景。
2. **每次搜索调用都验收来源列表**。响应里没有来源字段或 `web_search_call`，就当搜索没发生——不管正文看起来多可信。
3. **搜索策略按场景选**。日常 turbo；研究报告或英文场景上 agent（记得流式）；开了 agent 就别指望还能设时效和站点——它只留了 `enable_source`。
4. **强时效场景先挑模型**。qwen3-max 有日期推理，qwen-max 没有；模型选错，策略再对也会拿旧数据当新数据。
5. **成本核算要把 token 增量算进去**。搜索策略费是明码标价的小头，搜索内容撑大的上下文才是大头。

至于「同一朵云为什么功能入口这么分裂」——Responses 是新一代 Agent 协议，搜索工具按它的 Item 模型设计；Chat Completions 是兼容层，进阶参数在协议上就带不回来。功能不是不存在，是协议层放不下。但文档把三条协议的差异藏在能力表里、又把 MCP 和内置搜索放在同一个页面，踩坑几乎不可避免。希望这篇实测记录帮你少绕一段路。

## 总结

- 百炼的联网搜索不是一个功能，而是四条入口：DashScope 原生、Chat Completions、Responses API、搜索 MCP。能力逐级递减，计费各自独立。
- 能力表的关键行是「返回搜索来源」和「角标引用标注」：只有 DashScope 支持。OpenAI 兼容协议能搜但拿不到结构化引用（Responses 靠 output 数组曲线救国）。
- `search_strategy` 四档：turbo 快、max 全、agent 多轮整合但锁掉其他参数、agent_max 加抓取且只限 qwen3-max 思考模式。
- 强时效场景，模型选择和策略同样重要：qwen3-max 有日期推理，qwen-max 没有。
- 搜索类回答的最低验收标准是来源列表；没有来源，再流畅的回答也不能采信。
