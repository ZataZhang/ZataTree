---
title: LangChain 模型接入指南：OpenAI 兼容协议与多平台调用
description: "用 langchain_openai 接入一切 OpenAI 兼容端点：换头三要素、百炼实战踩坑、多平台速查与环境变量配置"
date: 2026-09-08T11:00:00+08:00
image: images/index/index.png
categories:
    - Agent
tags:
    - LangChain
---

# LangChain 模型接入指南：OpenAI 兼容协议与多平台调用

`langchain_openai` 名字里带 openai，能做的事却比名字大得多：任何兼容 OpenAI 接口协议的模型服务，它都能接。而到今天，**OpenAI API 格式已经成了事实上的工业标准**——阿里百炼、DeepSeek、vLLM、Ollama，无一例外都把"兼容 OpenAI 协议"当成默认姿势。

所以在 LangChain 里接模型这件事，可以收敛成一套打法：用 `ChatOpenAI` 和 `OpenAIEmbeddings`，配合目标平台的三要素。我把这套打法叫**"换头"**——换平台时业务代码一行不动，只改三处：`base_url`、`api_key`、`model`。一个原本基于 GPT-4 写的应用，改完这三处就直接跑在通义千问上。

这篇文章做两件事：以阿里百炼为例，把对话、流式、嵌入、工具调用四类调用完整走一遍（嵌入那里有个很容易漏的坑）；然后给一份多平台速查表，覆盖 6 家 ChatModel 和 5 家 Embeddings 的包名与初始化要点，换平台时直接查表。

## 一、百炼实战：用 ChatOpenAI 跑通四类调用

### 1.1 准备：包、Key 和 Base URL

```bash
pip install langchain-openai langchain-core
```

去[阿里云百炼控制台](https://bailian.console.aliyun.com/)拿两样东西：

1. **API Key**（`sk-` 开头）
2. **Base URL**：百炼的 OpenAI 兼容端点是 `https://dashscope.aliyuncs.com/compatible-mode/v1`

组件上只需要认识两个类，正好对应 LLM 应用的两块基石：

| 类 | 用途 | 百炼上的对应模型 |
|---|---|---|
| `ChatOpenAI` | 对话、指令跟随、逻辑推理、工具调用（Function Calling） | 通义千问系列（`qwen-plus`、`qwen-max`、`qwen-turbo`、`qwen-long`） |
| `OpenAIEmbeddings` | 文本转向量，构建 RAG 的基础 | 向量模型（`text-embedding-v2`、`text-embedding-v3` 等） |

`ChatOpenAI` 走 Chat Completion 接口：输入是消息列表（`SystemMessage`、`HumanMessage`、`AIMessage`），输出是 `AIMessage`。千问的具体型号清单见百炼官方的[模型列表](https://help.aliyun.com/zh/model-studio/getting-started/models)。

### 1.2 基础对话

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 为清晰起见先写成明文变量；生产环境放环境变量，做法见第三节
ALIBABA_API_KEY = "sk-你的阿里百炼API_KEY"
ALIBABA_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

chat_model = ChatOpenAI(
    model="qwen-plus",       # 指向百炼的模型 ID
    api_key=ALIBABA_API_KEY,
    base_url=ALIBABA_BASE_URL,
    temperature=0.7,
    streaming=True,
)

messages = [
    SystemMessage(content="你是一个专业的Python代码助手。"),
    HumanMessage(content="请用Python写一个冒泡排序，并解释其时间复杂度。"),
]

print(chat_model.invoke(messages).content)
```

除了 `model` / `api_key` / `base_url` 三处"换头"参数，其余写法与调 GPT-4 完全一致——这正是兼容协议的价值。

### 1.3 流式输出

把 `invoke` 换成 `stream` 就是流式：

```python
for chunk in chat_model.stream(messages):
    print(chunk.content, end="", flush=True)
```

`chunk.content` 是每次生成的一小段文本。流式对大模型应用的用户体验提升非常直接，做对话类产品基本是必选项。

### 1.4 向量嵌入：最不能漏的一行

做 RAG（知识库助手）时用 `OpenAIEmbeddings` 调百炼的向量模型。这里有个坑，也是全文最值得记住的一行参数：

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-v2",
    api_key=ALIBABA_API_KEY,
    base_url=ALIBABA_BASE_URL,
    check_embedding_ctx_length=False,  # 关键：关掉 OpenAI 特有的长度检查，防止报错
)

vector = embeddings.embed_query("阿里百炼是一个大模型服务平台。")
print(f"生成的向量维度: {len(vector)}")
print(f"向量前 5 位: {vector[:5]}")
```

`OpenAIEmbeddings` 默认开着一段 OpenAI 特有的逻辑：发送前先按 OpenAI 的分词器做上下文长度检查，超长文本会在本地被切块再分批发送。接到百炼这种非 OpenAI 端点上，这套本地检查既无必要，又可能在调用时直接报错。显式传 `check_embedding_ctx_length=False` 把它关掉就正常了。第一次接百炼嵌入如果莫名报错，先看是不是漏了这个参数。

### 1.5 工具调用：bind_tools

百炼的 Qwen 模型对 Function Calling 的支持很好，且完全走 OpenAI 的格式。用 `bind_tools` 把工具绑定到模型上，模型决定调用时，请求会出现在返回消息的 `tool_calls` 属性里，而不是正文里：

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str):
    """查询某个城市的天气信息。"""
    return f"{city} 的天气是晴天，气温 25 度。"

llm_with_tools = chat_model.bind_tools([get_weather])

response = llm_with_tools.invoke("杭州今天天气怎么样？")
print(f"工具调用请求: {response.tool_calls}")
```

拿到 `tool_calls` 之后，取出参数、真正执行工具、把结果作为 ToolMessage 回传给模型，就是一个完整的工具调用循环——LangChain 的 Agent 封装和 LangGraph 处理的就是这个循环。

## 二、为什么推荐用 langchain_openai 接百炼

一个自然的疑问：阿里有官方 SDK，LangChain 里也有 `ChatTongyi` 这种原生类，为什么绕道 `langchain_openai`？理由有三。

1. **代码零迁移成本。** 项目原本基于 GPT-4 开发的话，不需要改动任何业务逻辑，把环境变量里的 `BASE_URL` 和 `API_KEY` 换掉，应用就从 OpenAI 切到了百炼 Qwen。把 `langchain_openai` 当默认接入层，各平台互为"平替"，切换成本约等于零。

2. **生态支持最完善。** LangChain 社区对 OpenAI 类的支持是优先级最高的；走标准接口，后续接 LangGraph、LangSmith 这些工具也最顺。

3. **工具调用格式统一。** OpenAI 的 Tool Calling 格式是当前的黄金标准。百炼通过兼容接口让 Qwen 像 GPT 一样精准地调用工具，不需要自己处理格式转换。

反过来说，只有当你要用 DashScope 原生协议里、兼容层没覆盖的能力时，才需要回到原生 SDK——这条备选路线放在第五节。

## 三、环境变量与 Key 管理

### 3.1 永久环境变量：CMD / GUI / zsh / bash

以百炼的 `DASHSCOPE_API_KEY` 为例。这个名字不是随便起的：第五节的 `ChatTongyi`、`DashScopeEmbeddings` 都默认读它。

```bash
# Windows CMD
setx DASHSCOPE_API_KEY "YOUR_DASHSCOPE_API_KEY"
echo %DASHSCOPE_API_KEY%   # 验证

# Windows 图形界面
# 系统属性 → 环境变量，手动添加，不再赘述

# zsh
echo "export DASHSCOPE_API_KEY='YOUR_DASHSCOPE_API_KEY'" >> ~/.zshrc
source ~/.zshrc
echo $DASHSCOPE_API_KEY   # 验证

# bash
echo "export DASHSCOPE_API_KEY='YOUR_DASHSCOPE_API_KEY'" >> ~/.bashrc
source ~/.bashrc
echo $DASHSCOPE_API_KEY   # 验证
```

### 3.2 .env 模板：多平台共存

写进 shell 配置不适合多项目切换，更常见的做法是每个项目放一个 `.env`，用 `python-dotenv` 加载：

```bash
# 阿里云百炼
DASHSCOPE_API_KEY=sk-你的key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# OpenAI 官方（或另一个兼容端点）
OPENAI_API_KEY=sk-你的key
# OPENAI_BASE_URL=
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    streaming=True,
)
```

再进一步还有个偷懒技巧：openai 官方 SDK 本身就认 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL` 两个环境变量。把这两个变量指向百炼，代码里连 `api_key`、`base_url` 都不用写，`ChatOpenAI(model="qwen-plus")` 就能直接跑——切换平台时只动环境变量，一行代码不改。

### 3.3 百炼计费预警

百炼有个和 OpenAI 不一样的计费方式，要提前知道：它没办法单独充值消费，费用会直接从控制台里扣钱。所以动手跑代码之前，先把控制台的高消费预警设上。

## 四、多平台速查表

"换头"的前提是各家有自己的接入包。LangChain 0.2 之后，集成被拆成一个个独立的合作包，下面两张表按"提供商 → 安装包 → 初始化要点"整理。表里的型号名只是写作时存在过的示例，各家更新很快，使用前以官方现役型号为准。

### 4.1 ChatModel（6 家）

| 提供商 | 安装包 | 初始化要点 |
|---|---|---|
| OpenAI / 任意 OpenAI 兼容端点 | `langchain-openai` | `ChatOpenAI(model="gpt-4o-mini")`，默认读 `OPENAI_API_KEY`；接百炼则加 `base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"`，`model` 换成 `qwen-plus` 等 |
| Anthropic | `langchain-anthropic` | `ChatAnthropic(model="claude-sonnet-4-5-20250929")`，默认读 `ANTHROPIC_API_KEY` |
| Google | `langchain-google-genai` / `langchain-google-vertexai` | Gemini API 走 `ChatGoogleGenerativeAI(model="gemini-2.5-flash")`，读 `GOOGLE_API_KEY`；GCP 走 `ChatVertexAI`，需要 gcloud 登录或 `GOOGLE_APPLICATION_CREDENTIALS` |
| Hugging Face | `langchain-huggingface` | `HuggingFaceEndpoint(repo_id="google/flan-t5-large", task="text-generation")`，读 `HUGGINGFACEHUB_API_TOKEN`；本地 pipeline 用 `HuggingFacePipeline` |
| Cohere | `langchain-cohere` | `ChatCohere(model="command-r")`，默认读 `COHERE_API_KEY` |
| Ollama（本地） | `langchain-ollama` | `ChatOllama(model="llama3.2")`；服务默认在 `http://localhost:11434`，不在默认地址时传 `base_url` |

### 4.2 Embeddings（5 家）

| 提供商 | 安装包 | 初始化要点 |
|---|---|---|
| OpenAI / 任意 OpenAI 兼容端点 | `langchain-openai` | `OpenAIEmbeddings(model="text-embedding-3-small")`；接百炼：`model="text-embedding-v2"` + `base_url` + `check_embedding_ctx_length=False` |
| Google | `langchain-google-genai` / `langchain-google-vertexai` | `GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")`；Vertex 用 `VertexAIEmbeddings(model_name="text-embedding-005")` |
| Hugging Face（本地） | `langchain-huggingface` + `sentence-transformers` | `HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")`，可用 `model_kwargs={'device': 'cuda'}` 指定设备 |
| Cohere | `langchain-cohere` | `CohereEmbeddings(model="embed-v4.0")` |
| Ollama（本地） | `langchain-ollama` | `OllamaEmbeddings(model="nomic-embed-text")` |

### 4.3 相对旧版速查的更新

这张表由 2025 年初那版速查表更新而来，几处变化需要说明：

- `langchain_community.llms.HuggingFaceHub` → `langchain-huggingface` 包的 `HuggingFaceEndpoint`。Hugging Face 的推理接入这几年变动很大（Inference API 已让位给 Inference Providers），这条路线以官方文档为准。
- `langchain_community.chat_models.ChatOllama` → `langchain-ollama` 包的 `ChatOllama`，`OllamaEmbeddings` 同步从 `langchain_community.embeddings` 迁到 `langchain-ollama`。
- `langchain_community.embeddings.HuggingFaceEmbeddings` → `langchain-huggingface` 的同名类。
- 旧表里的 `gpt-3.5-turbo`、`claude-3-sonnet-20240229`、`gemini-pro`、`llama2` 等型号已过时，表中换成了更新的型号；它们同样会过期，以各家官方型号页为准。

### 4.4 两个容易忽略的差异

- **`embed_query` 与 `embed_documents` 分工不同**：前者嵌入单条查询文本（用户搜索的那句话），返回一个向量；后者批量嵌入多个文档，返回向量列表。检索系统的两侧——入库文档和用户查询——必须用同一个嵌入模型，否则维度和语义空间都对不上。
- **向量维度因模型而异**：`text-embedding-3-small` 是 1536 维，`text-embedding-3-large` 是 3072 维，常见的 sentence-transformers 模型多为 384 或 768 维。维度决定了向量库的结构和相似度计算，入库后换嵌入模型基本等于重建整个库。

## 五、备选路线：原生 DashScope 与 init_chat_model

### 5.1 ChatTongyi / DashScopeEmbeddings（legacy）

LangChain 社区包里保留了走 DashScope 原生 SDK 的两个类。⚠️ 以下是 0.x 时代的社区包写法，能用，但新项目建议优先走 OpenAI 兼容层：

```bash
pip install langchain-community dashscope
```

```python
# ⚠️ 此为 langchain_community 0.x 时代写法
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage

chatLLM = ChatTongyi(
    model="qwen-max",
    streaming=True,
)
res = chatLLM.stream([HumanMessage(content="hi")], streaming=True)
for r in res:
    print("chat resp:", r.content)
```

嵌入对应 `DashScopeEmbeddings`：

```python
# ⚠️ 此为 langchain_community 0.x 时代写法
from langchain_community.embeddings import DashScopeEmbeddings

embeddings = DashScopeEmbeddings(model="text-embedding-v2")

query_result = embeddings.embed_query("This is a test document.")
print("文本向量长度：", len(query_result))

doc_results = embeddings.embed_documents(
    ["Hi there!", "Oh, hello!", "What's your name?",
     "My friends call me World", "Hello World!"])
print("文本向量数量：", len(doc_results), "，文本向量长度：", len(doc_results[0]))
```

两个类都默认读 `DASHSCOPE_API_KEY` 环境变量。什么时候才需要这条路线：要用 DashScope 原生协议里、兼容层没覆盖的能力时。纯粹跑对话和嵌入，没有理由不用兼容层。

### 5.2 init_chat_model

LangChain 官方还提供了统一初始化入口 `init_chat_model`，按模型名和 provider 一步创建实例，不用记各家类名：

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "qwen-plus",
    model_provider="openai",   # 指定走 langchain_openai 的 ChatOpenAI
    api_key="sk-你的key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

其余参数原样透传给对应类，细节以官方文档为准。

## 总结

把这篇文章压成几条可执行的结论：

1. **把 `langchain_openai` 当默认接入层**。OpenAI API 格式已是事实工业标准，`ChatOpenAI` + `OpenAIEmbeddings` 能接一切兼容端点。
2. **换平台只改三处**：`base_url`、`api_key`、`model`，业务代码不动；配合环境变量或 `.env`，可以做到一行代码不换平台。
3. **接百炼做嵌入，`check_embedding_ctx_length=False` 必加**，这是最容易漏的一行。
4. **跑代码前先设百炼高消费预警**，它的费用直接从控制台账户扣，没有独立余额。
5. **新项目直接装独立集成包**（`langchain-ollama`、`langchain-huggingface` 等），`langchain_community` 里的模型类当 legacy 看。

下一步：拿 1.2 的基础对话代码，把三个"换头"参数换成你手上的平台——百炼、DeepSeek 或本地 Ollama——跑通第一条消息。然后做两件事：用 `bind_tools` 试一次工具调用，用 `OpenAIEmbeddings` 把一段文本打成向量。这三步走完，LangChain 接模型这件事就算真正上手了。
