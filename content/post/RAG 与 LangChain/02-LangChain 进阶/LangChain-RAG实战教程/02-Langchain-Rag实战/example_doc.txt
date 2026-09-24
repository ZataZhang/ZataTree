---
title: Langchain的简易教程
description: ""
date: 2025-03-11T11:05:13+08:00
# image: images/index/index.png
categories:
    - Library
tags:
    - LangChain
---


LangChain 是一个强大的开源框架，用于构建基于大型语言模型（LLM）的应用程序。它简化了开发流程，支持上下文感知、外部数据源集成以及复杂的工作流编排。以下是一个最新的入门教程概览，适用于2025年3月的背景：

---

## LangChain 简易教程

### 1. 安装 LangChain
确保您已经安装了 Python（建议使用 3.9 或更高版本）。通过以下命令安装 LangChain 的核心库：
```bash
pip install langchain
```
如果您需要特定的集成（例如 OpenAI、Anthropic 等），可以安装对应的合作伙伴包：
```bash
pip install langchain-openai
pip install langchain-anthropic
```

### 2. 基础概念
LangChain 的核心包括以下几个模块：
- **模型 I/O（Model I/O）**：与 LLM 交互，发送提示并获取输出。
- **内存（Memory）**：保留对话上下文，例如使用 `ConversationBufferMemory`。
- **链（Chains）**：组合提示、模型和外部工具，例如 `LLMChain` 或 `SequentialChain`。
- **检索（Retrieval）**：通过向量数据库（如 Qdrant 或 FAISS）实现检索增强生成（RAG）。
- **代理（Agents）**：让 LLM 根据工具动态决策。

### 3. 快速上手示例：构建一个简单的问答系统



首先再项目路径下面创建一个.env文件，并添加以下内容：
```bash
# 阿里云
## qwq-32b
api_key = "sk-..." # your-api-key
model = "qwq-32b"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# openai
....
```



以下是一个使用 LangChain 与 OpenAI 模型构建简单问答系统的代码示例：
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
load_dotenv()
# 初始化模型
# 可以使用OpenAI的API
# llm = ChatOpenAI(model="gpt-4", api_key="your-openai-api-key")
# 或者可以用其他的API，比如阿里云的
api_key = os.getenv("api_key")
base_url = os.getenv("base_url")
model = os.getenv("model")
llm = ChatOpenAI(api_key=api_key, base_url=base_url,model=model,  streaming=True)

# 定义提示模板
prompt = PromptTemplate(
    input_variables=["question"],
    template="请简洁回答以下问题：{question}"
)

# 创建链
chain = LLMChain(llm=llm, prompt=prompt)

# 运行链
question = "2025年的技术趋势是什么？"
response = chain.run(question)
print(response)
```

**输出示例**（假设模型预测）：  
2025年的技术趋势将聚焦以下方向：  
1. **人工智能与生成式AI**：生成式AI（如大模型）在内容创作、医疗诊断、客户服务等领域广泛应用，推动自动化与个性化服务。  
2. **量子计算**：实用化进展加速，可能在密码学、材料科学和药物研发中解决复杂问题。  
3. **可持续技术**：绿色能源（如高效太阳能、储能技术）、碳捕捉及电动汽车技术进一步成熟，助力碳中和目标。  
4. **扩展现实（XR）与元宇宙**：AR/VR在教育、远程协作和虚拟经济中的渗透率提升，推动沉浸式体验场景。  
5. **生物科技**：基因编辑（如CRISPR）、合成生物学和个性化医疗将革新疾病治疗与生物制造。  
6. **物联网与边缘计算**：5G/6G网络与边缘计算结合，优化工业自动化、智慧城市和实时数据分析。  
7. **网络安全**：零信任架构与AI驱动的安全系统成为应对网络威胁的核心，保护关键基础设施。  

这些趋势将重塑产业、生活方式及全球竞争力。

### 4. 进阶功能：RAG 系统
检索增强生成（RAG）是 LangChain 的强大功能，可结合外部数据回答问题。以下是一个简单示例：
```python
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader

# 加载文档
loader = TextLoader("your_document.txt")
documents = loader.load()

# 创建嵌入并存储到向量数据库
embeddings = OpenAIEmbeddings(api_key="your-openai-api-key")
vector_store = FAISS.from_documents(documents, embeddings)

# 初始化检索链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4", api_key="your-openai-api-key"),
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

# 查询
response = qa_chain.run("文档中提到的重要内容是什么？")
print(response)
```

### 5. 使用 LangGraph 构建复杂代理
LangGraph 是 LangChain 的扩展，适用于构建多代理或复杂工作流。以下是一个简化的 LangGraph 示例：
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 定义状态
class AgentState(TypedDict):
    question: str
    answer: str

# 定义节点
def question_node(state: AgentState) -> AgentState:
    state["answer"] = f"回答：{state['question']}"
    return state

# 创建图
workflow = StateGraph(AgentState)
workflow.add_node("question", question_node)
workflow.set_entry_point("question")
workflow.add_edge("question", END)

# 编译并运行
graph = workflow.compile()
result = graph.invoke({"question": "今天天气如何？"})
print(result["answer"])
```

### 6. 最新资源推荐
截至2025年3月11日，以下资源可能是最新的学习途径：
- **LangChain 官方文档**：访问 [python.langchain.com](https://python.langchain.com) 获取最新 API 参考和指南。
- **LangChain 中文社区**：如 [www.langchain.com.cn](https://www.langchain.com.cn) 或 [www.langchain.asia](https://www.langchain.asia)，提供中文教程和文档。
- **GitHub 仓库**：查看 [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) 获取最新代码和示例。
- **X 上的更新**：关注 @LangChainAI，获取最新集成和教程。例如，2025年3月9日的帖子提到 Deno 与 LangChain.js 的本地 LLM 集成教程。

### 7. 下一步
- **尝试 LangSmith**：用于调试和监控您的 LangChain 应用。
- **部署**：使用 LangServe 将链部署为 REST API。
- **探索多模态**：结合图像或音频输入，扩展应用场景。

---

## LangChain 模块化教程

LangChain 的核心功能可以分为以下几个模块：
1. **模型 I/O（Model I/O）** - 与语言模型交互
2. **内存（Memory）** - 管理对话上下文
3. **链（Chains）** - 组合提示和逻辑
4. **检索（Retrieval）** - 外部数据增强生成
5. **代理（Agents）** - 动态工具调用
6. **LangGraph** - 复杂工作流和多代理系统

以下是每个模块的教程：

---

### 1. 模型 I/O（Model I/O）
**功能**：与 LLM 交互，包括输入提示、调用模型和处理输出。

**教程**：
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# 初始化模型
llm = ChatOpenAI(model="gpt-4", api_key="your-openai-api-key")
# 或者可以用其他的API，比如阿里云的
api_key = "your-api-key"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
llm = OpenAI(api_key=api_key, base_url=base_url,model="qwq-32b",  streaming=True,)

# 定义提示模板
prompt = PromptTemplate.from_template("请用简洁的语言回答：{question}")

# 调用模型
question = "2025年的 AI 趋势是什么？"
response = llm.invoke(prompt.format(question=question))
print(response.content)
```
**输出示例**：  
"2025年的 AI 趋势包括多模态模型和自动化代理的广泛应用。"

**要点**：
- 支持多种模型（OpenAI、Anthropic、Hugging Face 等）。
- 可调整温度（temperature）和最大 token 数等参数。

---

### 2. 内存（Memory）
**功能**：保存和管理对话历史，提供上下文支持。

**教程**：
```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI

# 初始化模型
llm = ChatOpenAI(model="gpt-4", api_key="your-openai-api-key")

# 创建内存
memory = ConversationBufferMemory()

# 创建对话链
conversation = ConversationChain(llm=llm, memory=memory)

# 第一轮对话
print(conversation.run("我叫张三，今年30岁。"))
# 输出：好的，张三，很高兴认识你！你今天过得怎么样？

# 第二轮对话
print(conversation.run("你还记得我多大吗？"))
# 输出：当然记得，你今年30岁！
```
**要点**：
- `ConversationBufferMemory` 存储完整历史。
- 其他选项如 `ConversationSummaryMemory` 可总结对话以节省 token。

---

### 3. 链（Chains）
**功能**：将提示、模型和逻辑组合成可重复使用的流程。

**教程**：
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 初始化模型
llm = ChatOpenAI(model="gpt-4", api_key="your-openai-api-key")

# 定义提示
prompt = PromptTemplate(
    input_variables=["topic"],
    template="请写一段关于{topic}的简短介绍。"
)

# 创建链
chain = LLMChain(llm=llm, prompt=prompt)

# 运行链
response = chain.run(topic="量子计算")
print(response)
```
**输出示例**：  
"量子计算利用量子力学原理进行计算，能够在特定任务上大幅超越传统计算机。"

**要点**：
- `SequentialChain` 可连接多个链。
- 支持条件分支和自定义逻辑。

---

### 4. 检索（Retrieval）
**功能**：通过向量数据库从外部文档中检索相关信息。

**教程**：
```python
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader

# 加载文档
loader = TextLoader("sample.txt")  # 假设文件内容为技术趋势
documents = loader.load()

# 创建嵌入和向量存储
embeddings = OpenAIEmbeddings(api_key="your-openai-api-key")
vector_store = FAISS.from_documents(documents, embeddings)

# 创建检索链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4", api_key="your-openai-api-key"),
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

# 查询
response = qa_chain.run("2025年的技术趋势是什么？")
print(response)
```
**输出示例**：  
"根据文档，2025年的技术趋势包括量子计算和 AI 驱动的自动化。"

**要点**：
- 支持多种向量存储（如 FAISS、Qdrant、Pinecone）。
- 可用于问答、文档搜索等场景。

---

### 5. 代理（Agents）
**功能**：让 LLM 使用工具动态解决问题。

**教程**：
```python
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.utilities import WikipediaAPIWrapper

# 初始化模型
llm = ChatOpenAI(model="gpt-4", api_key="your-openai-api-key")

# 定义工具
wikipedia = WikipediaAPIWrapper()
tools = [
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="用于查询维基百科的信息"
    )
]

# 创建代理
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description")

# 运行代理
response = agent.run("告诉我关于 LangChain 的信息")
print(response)
```
**输出示例**：  
"LangChain 是一个用于构建 LLM 应用的框架，支持内存、检索和代理功能。"

**要点**：
- 支持多种工具（如搜索、计算器、API 调用）。
- 代理类型包括 `react`、`self-ask-with-search` 等。

---

### 6. LangGraph
**功能**：构建复杂的工作流或多代理系统。

**教程**：
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 定义状态
class GraphState(TypedDict):
    question: str
    answer: str

# 定义节点
def answer_node(state: GraphState) -> GraphState:
    state["answer"] = f"答案是：{state['question']} 的解决方案。"
    return state

# 创建图
workflow = StateGraph(GraphState)
workflow.add_node("answer", answer_node)
workflow.set_entry_point("answer")
workflow.add_edge("answer", END)

# 编译并运行
graph = workflow.compile()
result = graph.invoke({"question": "如何学习 LangChain"})
print(result["answer"])
```
**输出示例**：  
"答案是：如何学习 LangChain 的解决方案。"

**要点**：
- LangGraph 适合循环逻辑或多步骤任务。
- 可扩展为多代理协作。

---

### 综合示例：结合所有模块
假设我们要构建一个回答技术问题的系统：
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.agents import initialize_agent, Tool

# 初始化模型和内存
llm = ChatOpenAI(model="gpt-4", api_key="your-openai-api-key")
memory = ConversationBufferMemory()

# 加载外部文档
loader = TextLoader("tech_trends_2025.txt")
documents = loader.load()
vector_store = FAISS.from_documents(documents, OpenAIEmbeddings(api_key="your-openai-api-key"))

# 定义工具
def search_docs(query):
    return vector_store.similarity_search(query)[0].page_content

tools = [Tool(name="DocumentSearch", func=search_docs, description="搜索文档")]

# 创建代理
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", memory=memory)

# 运行
response = agent.run("2025年的技术趋势是什么？")
print(response)
```

---

### 学习资源
- **官方文档**：https://python.langchain.com
- **GitHub**：https://github.com/langchain-ai/langchain
- **X 更新**：关注 @LangChainAI 获取最新动态。

如果您想深入某个模块或需要更具体示例，请告诉我！