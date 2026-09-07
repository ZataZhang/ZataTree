---
title: "给 Agent 接入 Web Search：四种做法，和一条我试过之后放弃的路"
description: "Agent 需要实时信息时，接入 web search 有五条路径：模型厂商内置工具、搜索 API 包 function tool、MCP server、CLI+Skill，以及自托管 SearXNG。本文给出前四种的具体做法与选型建议；第五种我实测过，聚合并没有解决上游不稳定的问题，最终很难用，不推荐。"
date: 2026-09-07T10:00:00+08:00
slug: "给-Agent-接入-Web-Search：四种做法，和一条我试过之后放弃的路/index.md"
image: images/index/index.svg
categories:
    - Agent
tags:
    - Agent 工程实战
draft: false
---

Agent 的知识止于训练数据。一旦问题涉及「最近」——新发布的版本、上周的新闻、当前的价格——就需要 web search。这件事看起来简单，做起来第一道坎是选型：给 Agent 接入搜索的方式五花八门，方案之间的差别比看起来大。

把主流做法按「搜索能力由谁提供」归类，其实只有五种：模型厂商内置的搜索工具、搜索 API 包成 function tool、MCP server、CLI+Skill，以及自托管元搜索引擎（SearXNG）。

我的判断：前四种都走得通，选哪种主要取决于你的模型入口（官方 API 还是自建端点）和工程形态（代码内工具、协议层还是命令行）；第五种 SearXNG 听起来是「免费、自主、无配额」的最优解，我搭过一套给 Agent 用，结论是不推荐——聚合并没有解决上游不稳定的问题，反而把不稳定的方差叠加进了每次搜索。下面逐条展开。

## 一、先想清楚：搜索在谁的进程里执行

五种方式的名义差别是「用什么产品」，本质差别是搜索这个动作发生在哪里：

| 方式 | 搜索在哪执行 | 你要维护什么 | 对模型入口的要求 |
| --- | --- | --- | --- |
| 厂商内置搜索工具 | 模型厂商侧 | 几乎为零 | 绑定官方 API |
| 搜索 API + function tool | 你的进程 | 一个 tool 和一个 API key | 任何支持 function calling 的模型 |
| MCP server | 你的进程（协议层） | server 配置与进程 | 任何支持 MCP 的框架 |
| CLI + Skill | Agent 的 shell 里 | 脚本与 SKILL.md | 有 execute/shell 工具的 Agent |
| 自托管 SearXNG | 你自己的服务器 | 一整套搜索引擎运维 | 包成 tool 后同方式二 |

这个视角直接决定第一道筛选：如果你的模型跑在自建 vLLM 或其他 OpenAI 兼容端点上，第一种方式直接出局——厂商内置工具只在官方端点生效，vLLM 不提供搜索后端。这也是很多人（包括我）从官方 API 切到自建端点后，被迫重新做选型的原因。

另一个前置认知：**搜索工具几乎必须配一个抓取（fetch）工具**。搜索返回的是链接和摘要，Agent 要真正引用就得读全文。下面每种方式的讨论里，搜索和抓取都是成对出现的。

## 二、方式一：模型厂商内置的搜索工具

OpenAI Responses API 的 `web_search`、Claude API 的 `web_search` 工具、Gemini 的 `google_search` grounding 都属于这一类：搜索在厂商侧执行，返回结果自带引用，客户端零实现。

以 Claude 为例，全部接入代码就是声明一个工具：

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    # Opus 4.8/4.7/4.6 与 Sonnet 4.6 用 web_search_20260209，
    # 更早的模型用基础版 web_search_20250305
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
    messages=[
        {"role": "user", "content": "vLLM 最新版本支持哪些 OpenAI 兼容接口？"}
    ],
)
```

阿里云百炼也是这个形态，但接口协议有个容易踩的坑：联网搜索要走 **OpenAI-compatible Responses API**，而不是 Chat Completions。在 Chat Completions 里传 `enable_search` 这类参数，请求不会报错，但厂商侧搜索可能根本没触发——我就先在这里卡了一次：模型照样回答，正文看起来很专业，响应里却没有任何搜索来源。正确的接法是 `tools` 声明：

```python
client = OpenAI(api_key=key, base_url="https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
response = client.responses.create(
    model="qwen3.7-flash",
    input="今天的 GitHub trending",
    tools=[
        {"type": "web_search"},      # 搜索
        {"type": "web_extractor"},   # 抓取正文，效果更完整但更慢
    ],
    stream=True,
)
```

来源也不混在正文里，而在 `response.output` 里 `type == "web_search_call"` 的元素中，`action.sources` 就是链接列表。流式事件同样能拿到：`response.web_search_call.searching` / `completed` 表示搜索阶段，`response.output_text.delta` 才是正文增量。

两个实测数字（同一问题「今天的 GitHub trending」，qwen3.7-flash）：只开 `web_search` 约 14 秒；`web_search + web_extractor` 约 46–67 秒。`web_extractor` 的定位就是搜索工具里的 fetch——它让模型读正文，代价是会触发多轮抓取。还有一个体验细节：阿里云的 SSE 事件有批量下发的情况，`in_progress` / `searching` 可能到搜索快结束时才一起到达，客户端如果要展示「正在搜索」，最好在请求发出时先本地打印一行。

OpenAI 和 Gemini 形态类似：`tools` 里声明一个类型，其余交给平台。没有客户端实现、没有 key 管理、引用自动带回，模型对这类原生工具的使用意愿也最强——不需要你教它什么时候搜。要注意的是这类参数是厂商扩展：换厂商就得换参数名和协议，自建 vLLM 不认识它们。

代价有三个：

- **绑定官方 API**。换模型入口这条路就断了，前面说过。
- **按次计费**。两大厂商目前都是 $10/千次搜索的量级（以官网为准），量大的场景要算清这笔钱和 token 账的关系。
- **可控性有限**。`allowed_domains`/`blocked_domains` 这类过滤参数有，但缓存、代理、结果后处理这些深度定制没有。

适合的场景很明确：用官方 API、想零维护快速上线、搜索量不大。这是「能用」的天花板最低、起步最快的一条路。

## 三、方式二：搜索 API 包成 function tool（通用性最好）

找一个搜索 API，用 Agent 框架的工具机制包一层。这是模型无关的默认解，也是自建端点场景的主路。先选后端：

| 后端 | 定位 | 免费额度 | 备注 |
| --- | --- | --- | --- |
| [Tavily](https://www.tavily.com/) | 专为 Agent 设计，直接返回清洗后的正文摘录 | 有月度免费额度 | LangChain 有现成集成 `langchain-tavily` |
| Exa | 语义/神经搜索 | 有 | 适合「找相似资料」而非关键词匹配 |
| Jina（s.jina.ai） | 搜索 + grounding | 有 | 与 r.jina.ai 抓取配套 |
| Serper / SerpAPI | Google 结果页的结构化代理 | 注册赠送 | 返回 SERP 结构，正文要自己抓 |
| Brave Search API | 传统搜索 API | 有月度免费额度 | |
| 博查（Bocha）、智谱 web-search-pro | 国内可直连 | 少量 | 不想给 Agent 配代理出口时用 |
| DuckDuckGo（`ddgs` 包） | 免费无 key | 无限（被限流） | 质量与稳定性一般，适合原型验证 |

两个选型提醒：Bing Search API 已于 2025 年 8 月退役，按旧教程选型会踩空；各家额度与价格随时调整，动手前以官网为准。

接入的最短路径是现成集成：

```python
# uv pip install langchain-tavily
from langchain_tavily import TavilySearch

search = TavilySearch(max_results=5)
agent = create_deep_agent(model=model, tools=[search], system_prompt=...)
```

要控制输出格式或随时换后端，就自己包一层。以 LangChain 为例：

```python
from langchain_core.tools import tool
from tavily import TavilyClient

client = TavilyClient()  # 读 TAVILY_API_KEY 环境变量
from datetime import datetime
TODAY = datetime.now().astimezone()

@tool
def web_search(query: str) -> str:
    """搜索互联网，返回最相关的网页标题、链接与内容摘录。
当问题涉及训练数据之后的信息（新版本、新闻、当前价格）时调用。"""
    result = client.search(
        query=f"{query} (current date: {TODAY:%Y-%m-%d})",
        max_results=5,
        time_range="week",
    )
    return "\n\n".join(
        f"[{r['title']}]({r['url']})\n{r['content']}"
        f"\npublished: {r.get('published_date') or 'unknown'}"
        for r in result["results"]
    )
```

注意工具的 docstring 不是注释，是模型判断「何时调用」的依据——触发条件必须写进描述里，这一点后面还会反复出现。

配套的 fetch 工具，最省事的版本是走 r.jina.ai 把网页转成 Markdown：

```python
import httpx
from langchain_core.tools import tool

@tool
def fetch_url(url: str) -> str:
    """抓取网页并返回正文。拿到 web_search 的结果链接后，引用前先读全文。"""
    resp = httpx.get(f"https://r.jina.ai/{url}", timeout=30)
    return resp.text[:20000]  # 截断保护，防止单页吃满 context
```

（需要更强的抓取能力再上 Firecrawl。）

三条工程经验：

- **搜索和抓取分成两个工具。**合并成一个「搜了顺便读」的工具，模型的调用意愿和结果质量都会下降，排查问题也更难。
- **时效性是检索约束，不是模型自觉。**我踩过一个很典型的坑：用 Tavily 搜「今天的 GitHub trending」，Tavily 返回的混合了旧博客、旧榜单和缓存页，模型把结果里的「2025」当成了当前年份，最后一本正经地回答「今天是 2025 年」。修法是把时间边界从模型手里拿走：system prompt 注入本机当前日期，搜索查询附带 `current date`，检索强制 `time_range="week"`，结果逐条带 `published` 字段。不要把 `time_range` 作为可选参数交给模型决定——它连今天几号都不确定。
- **弱模型要强指令。**qwen 级别的开源模型对「何时该搜」并不敏感，光给工具不够，还要在 system prompt 里写明「问题涉及训练截止后的信息时，必须先调用 web_search，再回答」这类硬规则。
- **网络环境要提前想好。**国内网络下 Tavily 等域名走代理即可；要求直连就选博查或智谱。

## 四、方式三：MCP server

搜索能力不写在 Agent 代码里，而是挂在 MCP server 上，Agent 通过标准协议发现并调用。现成的 server 很多：[tavily-mcp](https://github.com/tavily-ai/tavily-mcp)、Brave 的官方 MCP、官方参考实现里的 [fetch server](https://github.com/modelcontextprotocol/servers)，以及若干 SearXNG 的 MCP 封装。

LangChain 生态用 `langchain-mcp-adapters` 接入：

```python
# uv pip install langchain-mcp-adapters
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "tavily-mcp"],
            "env": {"TAVILY_API_KEY": "..."},
        },
        "fetch": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-fetch"],
        },
    }
)
tools = await client.get_tools()
# tools 是标准 LangChain 工具，直接进 create_deep_agent / LangGraph
```

什么时候它比方式二好：

- **换后端不改代码**。从 Tavily 换到 Brave，改一段 server 配置就行，Agent 侧零改动。
- **多 Agent 共享工具栈**。CLI Agent、IDE 插件、Web 服务共用同一份 MCP 配置，工具升级一处生效。
- **生态即插即用**。搜索之外，抓取、爬虫、浏览器自动化都有现成 server，不写胶水代码。

代价是多一层进程管理和协议开销，调试链路变长——工具不工作时，得先分清是 server 挂了、配置错了还是适配层的问题。另外 MCP 不是唯一答案：2026 年的 Agent 工具生态里，MCP 和 CLI+Skill 是并列的两条路线，而不是替代关系，这正好引出下一种方式。

## 五、方式四：CLI + Skill

不给 Agent 专门的搜索工具，而是给它 shell 执行能力加一个搜索 CLI，再用 SKILL.md 教它什么时候用、怎么解析输出。飞书给 Agent 生态提供的 lark-cli 就是这条路线的实例——CLI 工具 + Skill 文档，不经过 MCP。

形态上，search.py 就是方式二里那个 API 调用，只是入口从 function tool 变成命令行：

```text
skills/web-search/SKILL.md
---
name: web-search
description: 需要训练数据之后的最新信息时，用 CLI 搜索并阅读网页
---
# 网络搜索

需要最新信息时：
1. 执行 `python search.py "查询词"`，获取结果列表（JSON）
2. 挑选最相关的 2~3 个链接，执行 `python fetch.py <url>` 阅读正文
3. 回答时附上来源链接
```

现成的搜索 CLI（比如 ddgr）也可以用，但输出解析比结构化的 tool result 脆，自己包一层脚本输出 JSON 更稳。

这条路线的取舍：

- 优点是**透明和复用**。每一步都能手工复现，调试时直接跑同一条命令；已有 CLI 工具栈零成本接入；不挑 Agent 框架，版本管理走 git。
- 缺点是**解析脆、权限面大**。给了 shell 就是给了世界，生产环境必须配沙箱；整个流程依赖模型认真读 SKILL.md，弱模型更容易跳过文档直接编。

适合已经有 execute/shell 工具且沙箱化的 Agent 运行时（deepagents 类框架都是这个形态），以及团队偏好可审计的命令行工作流的情况。

## 六、方式五：自托管 SearXNG——我试过，放弃

SearXNG 是开源的元搜索引擎：自己不索引网页，把查询转发给 Google、Bing、DuckDuckGo 等上游引擎再聚合结果，自带 [JSON API](https://docs.searxng.org/)，无 key 无配额。

它的卖点写在项目首页上：免费、隐私可控、不依赖单一搜索巨头。「聚合多个上游，一个挂了还有别的」——这句话对 Agent 场景特别有说服力，我当时也是这么被说服的。搭完给 Agent 用了一段时间之后，我的结论是：**这套卖点里的容错是「结果集层面」的，而 Agent 需要的是「结果质量层面」的稳定，聚合解决不了后者。**

展开说三点。

**第一，聚合没有解决上游不稳定，反而放大了它。**元搜索的容错逻辑是：某个上游挂了，其他上游还能出结果，所以「总有东西返回」。但 Agent 对搜索的要求不是「多少有点结果」，而是每次都拿到质量稳定的相关结果——搜索结果的抖动会直接传导成 Agent 行为的抖动，而且极难归因：答案变差了，你分不清是模型的问题还是搜索的问题。实际表现就是这种抖动：上游今天 CAPTCHA、明天限流，结果时好时坏，且坏的时机无法预期。

**第二，自托管处在上游风控最不利的位置。**SearXNG 的出口是你的服务器：数据中心 IP、没有浏览器指纹、没有登录态。Google 和 Bing 对这类无头流量的限流和 CAPTCHA 是最狠的，而 Tavily、Brave 这类搜索 API 收的钱，本质上就是「由服务商维护合规的抓取出口」的成本。你省下的是 API 费，付出的是和一个风控体系长期对抗。

**第三，运维对象从「一个 API key」变成「一套搜索引擎」。**引擎启停配置、上游可用性监控、CAPTCHA 处理、结果字段映射，国内部署还要给上游引擎配代理出口。这些全是隐性成本，而且没有 SLA——坏了就是你自己修。

一句话总结：它解决的问题（隐私、成本）在 Agent 搜索场景里不是主要矛盾，它引入的问题（不稳定性）恰恰是 Agent 最不能接受的。

边界也说清楚：如果是强隐私合规、内网部署的硬约束，并且有专人维护，SearXNG 值得重新评估——它在那个场景里解决的问题才是真问题。但「给 Agent 加个搜索」这个需求，别从这里开始。

## 七、怎么选

决策表：

| 你的情况 | 推荐起点 |
| --- | --- |
| 用官方 API，要最快上线 | 方式一 |
| 自建/兼容端点（vLLM 等），要模型无关 | 方式二（Tavily 起步） |
| 多 Agent 共享工具栈，要解耦 | 方式三 |
| 已有沙箱化的 execute 工具和 CLI 栈 | 方式四 |
| 想省钱/隐私，考虑自托管 SearXNG | 先算隐性运维成本，默认不推荐 |

三个与具体方式无关的工程结论：

1. **搜索和抓取永远是两个工具**，一个查链接，一个读全文。
2. **触发条件写进工具描述和 system prompt**，弱模型尤其需要硬规则，否则工具躺在那里没人调。
3. **搜索结果对 context 的消耗很可观**：一次搜索五条结果就是一到两千 token，深度调研任务给独立的 researcher 子 Agent，让它搜完、读完、综合完再带回结论，别让原始搜索结果塞满主循环。
4. **永远区分「厂商侧搜索生效了没有」。**请求不报错不代表搜索被触发：响应里没有 `web_search_call` / 来源字段，模型就是在拿参数化记忆演戏。把来源列表当作搜索类回答的最低验收标准，没有来源就不要采信。

## 总结

- 五种方式按「搜索在谁的进程里执行」分层，前四种都能落地，选型看模型入口和工程形态。
- 自建 OpenAI 兼容端点是分水岭：厂商内置工具直接排除，搜索 API 包 function tool 成为默认解。
- SearXNG 的聚合容错是结果集层面的，不解决 Agent 需要的结果质量稳定性，且自托管在上游风控里处于最不利的位置——实测后放弃，不推荐。
- 无论选哪种：search 和 fetch 成对出现，触发条件写进描述，重调研用子 Agent 隔离。
