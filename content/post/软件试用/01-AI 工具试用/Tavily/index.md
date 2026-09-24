---
title: Tavily-搜索引擎api
description: ""
date: 2025-05-20T15:34:00+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftUseExp
---


# Tavily API Python SDK 详细使用教程

Tavily API 旨在为 AI 应用和开发者提供一个强大、快速且相关的搜索引擎。它可以直接返回针对查询的总结性答案，并附带相关的源信息。本教程将引导你完成 Tavily Python SDK 的安装和使用。

## 目录

1.  [简介](#1-简介)
2.  [安装](#2-安装)
3.  [API 密钥设置](#3-api-密钥设置)
    * [环境变量（推荐）](#环境变量推荐)
    * [直接在代码中设置](#直接在代码中设置)
4.  [基本搜索](#4-基本搜索)
5.  [`search` 方法详解](#5-search-方法详解)
    * [常用参数](#常用参数)
    * [示例：使用不同参数](#示例使用不同参数)
6.  [理解返回结果](#6-理解返回结果)
    * [整体响应结构](#整体响应结构)
    * [结果条目 (`results`) 结构](#结果条目-results-结构)
7.  [高级搜索功能 (基于 `search` 方法的参数组合)](#7-高级搜索功能-基于-search-方法的参数组合)
    * [获取特定主题信息](#获取特定主题信息)
    * [结合 `include_domains` 和 `exclude_domains`](#结合-include_domains-和-exclude_domains)
8.  [错误处理](#8-错误处理)
9.  [完整示例代码](#9-完整示例代码)
10. [使用技巧](#10-使用技巧)

## 1. 简介

Tavily API 通过其 Python SDK `tavily-python`，可以轻松集成到你的 Python 项目中。它不仅返回传统的搜索结果列表，还能提供一个由 AI 生成的、针对用户查询的直接答案，这对于构建 RAG (Retrieval Augmented Generation) 系统或需要快速获取信息的 AI 应用非常有用。

## 2. 安装

你可以使用 pip 来安装 Tavily Python SDK：

```bash
pip install tavily-python
````

## 3\. API 密钥设置

要使用 Tavily API，你需要一个 API 密钥。你可以从 [Tavily AI 官网](https://tavily.com/) 注册并获取。

获取密钥后，有两种主要方式进行设置：

### 环境变量（推荐）

将 API 密钥设置为环境变量 `TAVILY_API_KEY`。SDK 会自动检测并使用它。

  * **Linux/macOS**:

    ```bash
    export TAVILY_API_KEY="你的API密钥"
    ```

    为了永久生效，可以将这行代码添加到你的 `.bashrc`, `.zshrc` 或其他 shell 配置文件中。

  * **Windows**:
    在系统环境变量中添加一个新变量，名称为 `TAVILY_API_KEY`，值为你的 API 密钥。或者在 PowerShell 中：

    ```powershell
    $env:TAVILY_API_KEY="你的API密钥"
    ```

### 直接在代码中设置

你也可以在初始化 `TavilyClient` 时直接传入 API 密钥：

```python
from tavily import TavilyClient

tavily_client = TavilyClient(api_key="你的API密钥")
```

如果同时设置了环境变量并显式传入密钥，则代码中显式传入的密钥会优先使用。

## 4\. 基本搜索

进行一次基本搜索非常简单：

```python
from tavily import TavilyClient

# 假设 TAVILY_API_KEY 环境变量已设置
# 如果没有设置环境变量，则使用: client = TavilyClient(api_key="YOUR_API_KEY")
client = TavilyClient()

try:
    response = client.search(query="2024年人工智能的最新进展是什么？")
    
    # 打印总结性答案 (如果请求并获得)
    if "answer" in response and response["answer"]:
        print("总结性回答:")
        print(response["answer"])
        print("-" * 30)

    # 打印搜索结果
    if "results" in response and response["results"]:
        print("\n搜索结果:")
        for result in response["results"]:
            print(f"标题: {result['title']}")
            print(f"链接: {result['url']}")
            print(f"内容摘要: {result['content'][:200]}...") # 打印内容的前200个字符
            print("-" * 20)

except Exception as e:
    print(f"搜索过程中发生错误: {e}")
```

## 5\. `search` 方法详解

`TavilyClient.search()` 是核心方法，它接受多个参数来定制你的搜索请求。

### 常用参数

  * `query` (str, 必需): 你的搜索查询语句。
  * `search_depth` (str, 可选): 搜索深度。
      * `"basic"`: 速度更快，结果可能不那么全面。适用于需要快速获取初步信息的场景。（默认值）
      * `"advanced"`: 进行更深入的搜索，可能会检索更多信息并进行更复杂的分析，结果更全面，但耗时和消耗的信用点数可能更多。
  * `include_answer` (bool, 可选): 是否在结果中包含一个由 AI 生成的总结性答案。默认为 `False`（但通常建议设为 `True` 以充分利用 Tavily 的特性）。
  * `include_raw_content` (bool, 可选): 是否在每个搜索结果中包含原始的、未经处理的网页文本内容。默认为 `False`。如果为 `True`，结果中的 `raw_content` 字段将被填充。
  * `max_results` (int, 可选): 返回的最大搜索结果数量。默认通常是 5 个左右。你可以根据需要调整。
  * `time_range` （[none,'day','week','month','year'],可选），默认是none
  * `include_domains` (list[str], 可选): 一个域名列表。Tavily 会尝试优先从这些域名中查找结果。例如：`["wikipedia.org", "github.com"]`。
  * `exclude_domains` (list[str], 可选): 一个域名列表。Tavily 会尝试排除这些域名中的结果。例如：`["pinterest.com"]`。
  * `topic` (str, 可选): 指定搜索的主题领域，帮助Tavily更好地聚焦结果。可选值包括 (但不限于，具体请参考Tavily官方文档是否有更新)：
      * `"general"` (默认)
      * `"news"`
      * `"finance"`
      * `"tech"`
      * `"academic"` (或 `"research_paper"`) - 尤其适合查找学术论文
      * `"code"` - 专注于代码相关的结果
      * *注意*：`topic` 的具体可用值和效果可能会随 API 更新而变化，请查阅最新的 Tavily 文档。

### 示例：使用不同参数

```python
from tavily import TavilyClient

client = TavilyClient() # 假设API密钥已通过环境变量设置

try:
    # 示例 1: 高级搜索，包含答案和原始内容，限定结果数量
    response_advanced = client.search(
        query="什么是量子计算及其潜在应用？",
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        max_results=3
    )
    print("\n--- 高级搜索示例 ---")
    if response_advanced.get("answer"):
        print(f"AI 回答: {response_advanced['answer']}")
    for res in response_advanced.get("results", []):
        print(f"  标题: {res['title']}")
        print(f"  链接: {res['url']}")
        if res.get("raw_content"):
            print(f"  原始内容片段: {res['raw_content'][:100]}...") # 截取前100字符
    
    # 示例 2: 搜索特定主题（例如，新闻）并指定域名
    response_news = client.search(
        query="最新的AI芯片发布",
        topic="news", # 或 "tech"
        include_domains=["theverge.com", "techcrunch.com"],
        max_results=2,
        include_answer=True
    )
    print("\n--- 新闻主题与域名限定搜索示例 ---")
    if response_news.get("answer"):
        print(f"AI 回答: {response_news['answer']}")
    for res in response_news.get("results", []):
        print(f"  标题: {res['title']}")
        print(f"  链接: {res['url']}")

except Exception as e:
    print(f"发生错误: {e}")
```

## 6\. 理解返回结果

Tavily API 的 `search` 方法返回一个 JSON 对象 (在 Python SDK 中是字典)。

### 整体响应结构

一个典型的响应字典可能包含以下键：

  * `query` (str): 你原始的搜索查询。
  * `answer` (str, 可选): 如果 `include_answer=True` 并且 API 能够生成一个总结性答案，这里会包含该答案。
  * `results` (list[dict]): 一个包含搜索结果条目的列表。每个条目都是一个字典。
  * `images` (list[str], 可选): 如果搜索与图片相关且Tavily找到图片，可能会包含图片URL列表 (较少见于主要文本搜索场景，更多特定于图片搜索功能，如果Tavily支持)。
  * `response_time` (float, 可选): API 处理请求所用的时间（秒）。
  * `error` (str, 可选): 如果发生错误，这里可能包含错误信息。

### 结果条目 (`results`) 结构

`results` 列表中的每个字典代表一个搜索结果，通常包含：

  * `title` (str): 搜索结果的标题。
  * `url` (str): 结果的来源 URL。
  * `content` (str): Tavily 提取或生成的与查询相关的该页面的内容摘要或片段。这是非常有用的字段，通常比传统的搜索引擎片段更丰富。
  * `score` (float, 可选): 一个表示结果与查询相关性的分数。分数越高，相关性越强。
  * `raw_content` (str, 可选): 如果请求了 `include_raw_content=True` 并且 Tavily 成功提取，这里会包含来自源 URL 的原始（或接近原始）文本内容。

## 7\. 高级搜索功能 (基于 `search` 方法的参数组合)

通过组合 `search` 方法的不同参数，可以实现更高级的搜索策略。

### 获取特定主题信息

使用 `topic` 参数可以帮助Tavily更好地理解你的意图并返回更相关的结果。

```python
response = client.search(
    query="最新的Python异步编程库有哪些？",
    topic="code", # 或者 "tech"
    include_answer=True,
    max_results=5
)
# 处理 response...
```

### 结合 `include_domains` 和 `exclude_domains`

这对于从特定权威来源获取信息或排除已知低质量来源非常有用。

```python
response = client.search(
    query="气候变化对农业的影响 site:gov OR site:edu", # 也可以在query中使用高级搜索操作符
    search_depth="advanced",
    include_domains=["nasa.gov", "epa.gov", "nature.com"], # 进一步强调优先域名
    exclude_domains=["personalblog.com"], # 排除不想要的域名
    include_answer=True,
    max_results=5
)
# 处理 response...
```

*注意*: `site:` 操作符在 `query` 字符串中是许多搜索引擎支持的标准语法，Tavily 也可能支持。与 `include_domains` 结合使用可以增强效果。

## 8\. 错误处理

在使用 API 时，进行适当的错误处理非常重要。Tavily SDK 可能会因为网络问题、无效的 API 密钥、请求超限等原因抛出异常。

```python
from tavily import TavilyClient
from tavily.errors import TavilyApiError # 可以捕获特定的Tavily错误

client = TavilyClient()

try:
    response = client.search(query="一个可能会失败的查询")
    # ...处理响应...
except TavilyApiError as e:
    print(f"Tavily API 错误: {e}")
    # 例如，处理API密钥无效、超出配额等特定错误
except requests.exceptions.RequestException as e: # requests库是底层依赖
    print(f"网络请求错误: {e}")
except Exception as e:
    print(f"发生了未知错误: {e}")
```

## 9\. 完整示例代码

下面是一个结合了多个特性的完整示例：

```python
import os
from tavily import TavilyClient
from tavily.errors import TavilyApiError
import json # 用于美化打印JSON

def perform_tavily_search(query_text, num_results=3, depth="basic", include_ans=True, include_raw=False):
    """
    执行 Tavily 搜索并打印结果。
    """
    try:
        # 推荐从环境变量获取 API 密钥
        # api_key = os.getenv("TAVILY_API_KEY")
        # if not api_key:
        #     print("错误: TAVILY_API_KEY 环境变量未设置。")
        #     return
        # client = TavilyClient(api_key=api_key)
        
        # 或者，如果你在脚本开头设置了全局的 client 实例：
        client = TavilyClient() # 确保API密钥已通过某种方式提供

        print(f"\n正在搜索 (深度: {depth}, 结果数: {num_results}): '{query_text}'")
        
        response_data = client.search(
            query=query_text,
            search_depth=depth,
            include_answer=include_ans,
            include_raw_content=include_raw,
            max_results=num_results
        )

        print("\n--- API 响应 (JSON 格式) ---")
        print(json.dumps(response_data, indent=2, ensure_ascii=False)) # 美化打印

        if response_data.get("answer"):
            print(f"\n--- 总结性回答 ---")
            print(response_data["answer"])

        print(f"\n--- 搜索结果 ({len(response_data.get('results', []))} 条) ---")
        for i, result in enumerate(response_data.get("results", [])):
            print(f"\n结果 {i+1}:")
            print(f"  标题: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Tavily 内容摘要:\n    {result.get('content', 'N/A')[:300]}...") # 摘要的前300字符
            if result.get("raw_content"):
                print(f"  原始页面内容 (片段):\n    {result['raw_content'][:200]}...") # 原始内容的前200字符
            print(f"  相关性分数: {result.get('score', 'N/A')}")
        
        print("\n" + "="*50)

    except TavilyApiError as e:
        print(f"Tavily API 错误: {e}")
    except Exception as e:
        print(f"执行搜索时发生意外错误: {e}")

if __name__ == "__main__":
    # 确保你已经设置了 TAVILY_API_KEY 环境变量，或者在 TavilyClient() 中直接提供
    # 例如: TavilyClient(api_key="YOUR_TAVILY_API_KEY")
    
    if not os.getenv("TAVILY_API_KEY") and "YOUR_TAVILY_API_KEY" == "YOUR_TAVILY_API_KEY": # 检查是否已设置
         print("请设置 TAVILY_API_KEY 环境变量或在代码中直接提供 API 密钥。")
    else:
        perform_tavily_search(
            query_text="Python在数据科学中的应用",
            num_results=3,
            depth="basic",
            include_ans=True
        )

        perform_tavily_search(
            query_text="解释一下Transformer模型的工作原理",
            num_results=2,
            depth="advanced",
            include_ans=True,
            include_raw=True # 请求原始文本内容
        )
        
        perform_tavily_search(
            query_text="最新发布的宇宙学研究论文",
            num_results=4,
            topic="academic", # 尝试使用主题参数
            depth="advanced",
            include_ans=True
        )

```

## 10\. 使用技巧

  * **明确的查询**: 查询语句越明确，Tavily 返回的结果就越相关。
  * **利用 `search_depth`**: 对于快速概览，`"basic"` 可能足够；对于需要深入信息的研究，`"advanced"` 更佳。
  * **`include_answer`**: 这个参数是 Tavily 的核心优势之一，尽量使用它来获取直接的答案。
  * **`include_raw_content` 与自定义抓取**: 如果 `include_raw_content=True` 能满足需求，可以减少你自己编写网页抓取逻辑的需要。但如果需要非常特定的元素或有复杂的网站结构，你可能仍需要结合你自己的抓取工具（如教程开头提到的 `get_page_content` 函数）。
  * **迭代和优化**: 根据返回结果调整你的查询和参数，以获得最佳效果。
  * **查阅官方文档**: API 和 SDK 可能会更新，定期查阅 [Tavily 官方文档](https://www.google.com/search?q=https://docs.tavily.com/docs/python-sdk/introduction) 以获取最新信息、参数和最佳实践。
  * **管理信用点数**: 注意不同类型的查询（特别是 `search_depth="advanced"` 或请求大量结果）可能会消耗不同的信用点数。

希望这篇教程能帮助你有效地使用 Tavily API Python SDK！

```
