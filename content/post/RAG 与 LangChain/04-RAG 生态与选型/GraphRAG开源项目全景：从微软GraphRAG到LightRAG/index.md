---
title: Graph RAG 开源项目全景：从微软 GraphRAG 到 LightRAG
description: Graph RAG 是 RAG 技术的重要演进方向，本文系统梳理主流开源项目，帮你快速选型。
date: 2026-03-27T16:00:00+08:00
image: images/index/index.png
categories:
    - RAG 与 LangChain
tags:
    - RAG 生态与选型
    - RAG
    - GraphRAG
    - KnowledgeGraph
    - OpenSource
---

传统 RAG 的核心思路是"向量检索 + 生成"，但在处理需要多跳推理、全局理解的问题时，效果往往不理想。

Graph RAG（知识图谱 + RAG）通过构建文档间的实体关系网络，让检索不再局限于局部相似度匹配，而是能够进行图遍历、社区发现、路径推理。这让 RAG 系统能回答更复杂的问题。

这篇文章系统梳理 Graph RAG 的主流开源项目，帮你快速了解和选型。

## 一、为什么需要 Graph RAG

### 传统 RAG 的局限

```
问题 1：多跳推理

用户问："A 公司的合作方的竞争对手有哪些？"

传统 RAG：
1. 检索"A 公司的合作方" → 找到 B 公司
2. 检索"B 公司的竞争对手" → 找到 C、D 公司

问题：
- 需要两轮检索，中间结果可能丢失
- 无法自动发现推理路径

Graph RAG：
A 公司 --合作--> B 公司 --竞争--> C、D 公司
一次图遍历即可完成
```

```
问题 2：全局理解

用户问："这篇文章的核心观点是什么？"

传统 RAG：
- 检索 Top-K 相关段落
- 但核心观点可能分散在各处
- 无法形成全局视角

Graph RAG：
- 通过社区发现，将文档划分为多个主题
- 每个社区生成摘要
- 整合社区摘要，形成全局理解
```

### Graph RAG 的核心思路

```
传统 RAG：
文档 → Chunk → 向量化 → 向量检索

Graph RAG：
文档 → 实体抽取 → 关系抽取 → 知识图谱
                                    ↓
                            图检索 + 向量检索
                                    ↓
                                LLM 生成
```

## 二、主流框架概览

| 框架 | Stars | 作者 | 核心特点 | 适用场景 |
|------|-------|------|----------|----------|
| **LightRAG** | 36K+ | 港大 HKUDS | 轻量快速，双层检索 | 中小规模，实时更新 |
| **GraphRAG** | 33K+ | Microsoft | 社区摘要，全局理解 | 大规模文档 |
| **HippoRAG** | 3.5K+ | 俄亥俄州立 | 模拟海马体记忆 | 长期记忆系统 |
| **Fast-GraphRAG** | 3.8K+ | Circlemind | 自适应，快速 | 快速部署 |
| **Neo4j Graph Builder** | 4.7K+ | Neo4j | 企业级图数据库 | 可视化，企业应用 |
| **R2R** | 7.8K+ | SciPhi AI | 生产级，完整方案 | 企业部署 |

下面逐一详细介绍。

## 三、Microsoft GraphRAG

### 基本信息

```
GitHub: https://github.com/microsoft/graphrag
Stars: 33,800+
论文: GraphRAG: Unlocking LLM Discovery on Narrative Private Data
语言: Python
```

### 核心原理

GraphRAG 的核心创新是**社区发现 + 社区摘要**：

```
Step 1: 知识图谱构建
文档 → 实体抽取 → 关系抽取 → 图存储

Step 2: 社区发现
用 Leiden 算法将图划分为多个社区
每个社区是一个紧密相关的实体群组

Step 3: 社区摘要
对每个社区，用 LLM 生成摘要
摘要包含社区的核心实体和关系

Step 4: 检索
局部查询：从相关实体出发，图遍历
全局查询：检索社区摘要，整合回答
```

### 架构图

```
┌──────────────────────────────────────────────────────┐
│              Microsoft GraphRAG Pipeline             │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   文档输入        │
              └────────┬─────────┘
                        │
         ┌──────────────┼───────────────┐
         ▼              ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │ 文本分块 │   │ 实体抽取  │   │ 关系抽取  │
    └────┬────┘   └────┬─────┘   └────┬─────┘
         │              │               │
         └──────────────┼───────────────┘
                        ▼
              ┌──────────────────┐
              │   知识图谱        │
              │   (NetworkX)      │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   社区发现        │
              │   (Leiden)        │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   社区摘要        │
              │   (LLM 生成)      │
              └────────┬─────────┘
                        │
         ┌──────────────┼───────────────┐
         ▼              ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │ 局部查询 │   │ 全局查询  │   │ 混合查询  │
    └────┬────┘   └────┬─────┘   └────┬─────┘
         │              │               │
         └──────────────┼───────────────┘
                        ▼
              ┌──────────────────┐
              │   LLM 生成答案    │
              └──────────────────┘
```

### 快速开始

```python
# 安装
pip install graphrag

# 初始化项目
python -m graphrag.index --init --root ./ragtest

# 配置（settings.yaml）
graphrag:
  llm:
    type: openai_chat
    model: gpt-4o
  embeddings:
    type: openai_embedding
    model: text-embedding-3-small

# 构建索引
python -m graphrag.index --root ./ragtest

# 查询
python -m graphrag.query --root ./ragtest --method local "What is the main topic?"
python -m graphrag.query --root ./ragtest --method global "What are the key themes?"
```

### 查询模式

```
Local Search（局部查询）：
- 从问题中识别实体
- 扩展实体的邻居节点
- 用局部子图生成答案
- 适合：具体事实查询

Global Search（全局查询）：
- 检索相关社区摘要
- 整合多个社区的信息
- 形成全局视角
- 适合："核心观点"、"主要主题"类问题

DRIFT Search（混合查询）：
- 结合局部和全局
- 动态调整检索范围
- 适合：复杂推理问题
```

### 优缺点

```
优点：
✅ 全局理解能力强（社区摘要）
✅ 微软官方维护，质量有保障
✅ 论文驱动，原理清晰
✅ 支持多种查询模式

缺点：
❌ 索引构建慢（需要多次 LLM 调用）
❌ 成本高（实体抽取、关系抽取、社区摘要）
❌ 不适合实时更新（重建索引代价大）
❌ 需要一定学习成本
```

### 适用场景

```
✅ 推荐：
- 大规模文档库（10K+ 文档）
- 需要全局理解（"核心观点"、"主要趋势"）
- 需要多跳推理
- 离线构建，在线查询

❌ 不推荐：
- 小规模知识库
- 需要实时更新
- 成本敏感
```

## 四、LightRAG

### 基本信息

```
GitHub: https://github.com/HKUDS/LightRAG
Stars: 36,600+
论文: LightRAG: Simple and Fast Retrieval-Augmented Generation (EMNLP 2025)
作者: 香港大学数据科学实验室
语言: Python
```

### 核心创新

LightRAG 针对 GraphRAG 的痛点做了优化：

```
GraphRAG 的问题：
1. 索引构建慢：需要多次 LLM 调用
2. 成本高：实体抽取、关系抽取、社区摘要
3. 不支持实时更新

LightRAG 的解决方案：
1. 双层检索：低层（实体）+ 高层（关键概念）
2. 无需社区发现：用双层图代替
3. 流式插入：支持实时更新
4. 轻量存储：无需图数据库，文件即可
```

### 双层检索原理

```
传统 GraphRAG：
文档 → 实体 → 图 → 社区发现 → 社区摘要 → 检索

LightRAG：
文档 → 实体 + 关键概念 → 双层图 → 直接检索

双层图结构：
┌─────────────────────────────────────┐
│         高层（关键概念层）           │
│    [AI] ── [机器学习] ── [深度学习]  │
│         │           │           │   │
├─────────┼───────────┼───────────┼───┤
│         │           │           │   │
│         ▼           ▼           ▼   │
│         低层（实体层）               │
│   [GPT-4]  [神经网络]  [CNN/RNN]     │
└─────────────────────────────────────┘

查询时：
1. 先在高层找到相关概念
2. 再在低层找到具体实体
3. 双层结果融合
```

### 快速开始

```python
# 安装
pip install lightrag-hku

# 基础使用
from lightrag import LightRAG
from lightrag.llm import openai_complete_if_cache, openai_embedding

# 初始化
rag = LightRAG(
    working_dir="./rag_storage",
    llm_model_func=openai_complete_if_cache,
    embedding_func=openai_embedding
)

# 插入文档
with open("document.txt", "r") as f:
    rag.insert(f.read())

# 查询
result = rag.query("What is machine learning?", mode="hybrid")

# 查询模式
result = rag.query("...", mode="naive")    # 纯向量检索
result = rag.query("...", mode="local")    # 局部图检索
result = rag.query("...", mode="global")   # 全局图检索
result = rag.query("...", mode="hybrid")   # 混合检索
```

### 性能对比（官方数据）

```
索引构建时间：
- GraphRAG: 100 分钟
- LightRAG: 10 分钟
- 提升: 10x

查询时间：
- GraphRAG: 2 秒
- LightRAG: 0.3 秒
- 提升: 6x

成本（Token 消耗）：
- GraphRAG: $10
- LightRAG: $1
- 降低: 90%

准确率：
- GraphRAG: 45%
- LightRAG: 52%
- 提升: 7%
```

### 优缺点

```
优点：
✅ 快：索引和查询都很快
✅ 省：成本降低 50-90%
✅ 灵活：支持实时插入更新
✅ 简单：无需图数据库
✅ 准确：双层检索更精准

缺点：
❌ 全局理解不如 GraphRAG（无社区摘要）
❌ 大规模场景下，图文件可能很大
❌ 功能相对简单
```

### 适用场景

```
✅ 推荐：
- 中小规模知识库（< 10K 文档）
- 需要实时更新
- 成本敏感
- 快速原型

❌ 不推荐：
- 超大规模文档
- 需要深度全局理解
```

## 五、HippoRAG

### 基本信息

```
GitHub: https://github.com/OSU-NLP-Group/HippoRAG
Stars: 3,500+
论文: HippoRAG: A Neurobiological Framework for Long-Term Memory (NeurIPS 2024)
作者: 俄亥俄州立大学
语言: Python
```

### 核心原理：模拟海马体

```
人类记忆机制：
海马体（Hippocampus）：
- 索引新记忆
- 将记忆整合到大脑皮层

大脑皮层：
- 存储长期记忆
- 知识以网络形式组织

检索时：
- 从海马体获取线索
- 在大脑皮层中激活相关记忆
- 通过联想找到答案

HippoRAG 的实现：
海马体 → 向量索引（快速找到入口）
大脑皮层 → 知识图谱（关联检索）
检索 → Personalized PageRank（模拟联想）
```

### 架构图

```
┌──────────────────────────────────────────────────────┐
│                  HippoRAG 架构                       │
└──────────────────────────────────────────────────────┘

索引阶段：
文档 → Passage 节点 → 向量化（海马体索引）
     → 实体抽取 → 实体节点
     → 关系抽取 → 边
     → 知识图谱（大脑皮层）

检索阶段：
Query → 向量化 → 找到相关 Passage 节点
                          ↓
              Personalized PageRank
              （从入口节点扩散）
                          ↓
                   激活相关实体和 Passage
                          ↓
                      LLM 生成答案
```

### Personalized PageRank

```
传统 PageRank：
- 所有节点平等
- 计算全局重要性

Personalized PageRank：
- 从特定节点出发（Query 相关的 Passage）
- 计算相对这些节点的重要性
- 模拟"联想"过程

示例：
Query: "GPT-4 的训练数据"

Step 1: 向量检索找到入口 Passage
入口节点: [Passage_A, Passage_B]

Step 2: Personalized PageRank
从 Passage_A、Passage_B 出发
计算其他节点的激活程度

Step 3: 激活扩散
Passage_A → 实体"GPT-4" → 实体"训练数据" → Passage_C
Passage_B → 实体"OpenAI" → 实体"GPT-4" → ...

Step 4: 收集高激活度的 Passage
Top-K: [Passage_A, Passage_B, Passage_C, ...]

Step 5: LLM 生成答案
```

### 快速开始

```python
# 安装
pip install hipporag

# 使用
from hipporag import HippoRAG

rag = HippoRAG(
    graph_db="neo4j",  # 支持 Neo4j 或 NetworkX
    llm_model="gpt-4",
    embedding_model="text-embedding-3-small"
)

# 索引
rag.index("./documents")

# 查询
result = rag.query("What are the key features of GPT-4?")
```

### 适用场景

```
✅ 推荐：
- 长期记忆系统
- 持续学习的知识库
- 需要精准检索
- 个性化 RAG

❌ 不推荐：
- 简单问答场景
- 成本敏感
```

## 六、Neo4j + RAG 方案

### Neo4j LLM Graph Builder

```
GitHub: https://github.com/neo4j-labs/llm-graph-builder
Stars: 4,700+
作者: Neo4j 官方
语言: Python
```

### 核心特点

```
Neo4j 的优势：
1. 成熟的图数据库
2. 强大的 Cypher 查询语言
3. 可视化工具（Neo4j Browser）
4. 企业级支持

LLM Graph Builder 的功能：
1. 从非结构化文本构建知识图谱
2. 支持多种 LLM（OpenAI、Azure、Gemini、Ollama）
3. 实体和关系抽取
4. 图谱可视化
```

### 工作流程

```
┌──────────────────────────────────────────────────────┐
│           Neo4j Graph Builder Pipeline               │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   文档输入        │
              │  (PDF/TXT/URL)   │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   文本分块        │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   LLM 实体抽取    │
              │  "苹果公司" → Organization │
              │  "库克" → Person  │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   LLM 关系抽取    │
              │  (苹果公司, CEO, 库克) │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   存入 Neo4j      │
              │  CREATE (a:Org {name:"苹果"})│
              │  CREATE (b:Person {name:"库克"})│
              │  CREATE (a)-[:CEO]->(b) │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   图检索 + LLM    │
              └──────────────────┘
```

### 快速开始

```python
# 安装
pip install neo4j-graphrag

from neo4j import GraphDatabase
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.generation import GraphRAG

# 连接 Neo4j
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# 初始化
llm = OpenAILLM(model_name="gpt-4")
embedder = OpenAIEmbeddings()
rag = GraphRAG(driver, llm, embedder)

# 构建图谱
rag.build_graph("./documents")

# 查询
result = rag.search("Who is the CEO of Apple?")
```

### 适用场景

```
✅ 推荐：
- 企业级应用
- 需要可视化
- 已有 Neo4j 基础设施
- 复杂图查询

❌ 不推荐：
- 小规模、轻量场景
- 不想维护图数据库
```

## 七、其他值得关注的项目

### 1. Fast-GraphRAG

```
GitHub: https://github.com/circlemind-ai/fast-graphrag
Stars: 3,800+

特点：
- 自适应：根据数据和查询自动调整
- 快速：优化的检索算法
- 简单：开箱即用

适用：快速部署，数据多样
```

### 2. R2R (Reason to Retrieve)

```
GitHub: https://github.com/SciPhi-AI/R2R
Stars: 7,800+

特点：
- 生产级 RAG 系统
- Agentic RAG（Agent + RAG）
- 支持知识图谱
- 完整 RESTful API
- 评估工具

适用：企业级部署
```

### 3. graph-rag-agent（拼好RAG）

```
GitHub: https://github.com/1517005260/graph-rag-agent
Stars: 2,200+

特点：
- 融合 GraphRAG + LightRAG + Neo4j
- DeepSearch 推理能力
- 自制 GraphRAG 评估框架
- 国产项目，中文友好

适用：学习对比，评估测试
```

### 4. Medical-Graph-RAG

```
GitHub: https://github.com/ImprintLab/Medical-Graph-RAG
Stars: 800+
论文: ACL 2025

特点：
- 医疗领域专用
- 循证医学信息检索
- 医学实体识别优化

适用：医疗知识库
```

### 5. GraphRAG-Local-UI

```
GitHub: https://github.com/severian42/GraphRAG-Local-UI
Stars: 2,300+

特点：
- 支持本地 LLM（Ollama）
- 完整 UI 界面
- 索引/调参/查询/可视化
- 无需云端 API

适用：本地部署，隐私敏感
```

## 八、框架对比

### 性能对比

| 指标 | GraphRAG | LightRAG | HippoRAG |
|------|----------|----------|----------|
| 索引速度 | 慢 | 快 10x | 中等 |
| 查询速度 | 中等 | 快 5x | 快 |
| 成本 | 高 | 低 50-90% | 中等 |
| 全局理解 | 强 | 中等 | 中等 |
| 局部检索 | 强 | 强 | 很强 |
| 实时更新 | ❌ | ✅ | ✅ |

### 功能对比

| 功能 | GraphRAG | LightRAG | HippoRAG | Neo4j |
|------|----------|----------|----------|-------|
| 社区发现 | ✅ | ❌ | ❌ | ✅ |
| 双层检索 | ❌ | ✅ | ❌ | ❌ |
| PageRank | ❌ | ❌ | ✅ | ✅ |
| 可视化 | ❌ | ❌ | ❌ | ✅ |
| 本地部署 | ✅ | ✅ | ✅ | ✅ |
| 流式插入 | ❌ | ✅ | ✅ | ✅ |

### 适用场景对比

```
大规模文档（10K+）：
1. GraphRAG（全局理解）
2. Neo4j + RAG（企业级）

中小规模（< 10K）：
1. LightRAG（快速、低成本）
2. Fast-GraphRAG（简单部署）

长期记忆：
1. HippoRAG（模拟海马体）

医疗/专业领域：
1. Medical-Graph-RAG
2. KG_RAG

本地部署：
1. GraphRAG-Local-UI
2. LightRAG + Ollama
```

## 九、选型决策树

```
开始选型
    │
    ├─ 需要全局理解（"核心观点"、"主要趋势"）？
    │   ├─ 是 → Microsoft GraphRAG
    │   └─ 否 → 继续
    │
    ├─ 需要实时更新？
    │   ├─ 是 → LightRAG
    │   └─ 否 → 继续
    │
    ├─ 需要可视化？
    │   ├─ 是 → Neo4j + RAG
    │   └─ 否 → 继续
    │
    ├─ 长期记忆系统？
    │   ├─ 是 → HippoRAG
    │   └─ 否 → 继续
    │
    ├─ 成本敏感？
    │   ├─ 是 → LightRAG
    │   └─ 否 → 继续
    │
    ├─ 快速原型？
    │   ├─ 是 → LightRAG / Fast-GraphRAG
    │   └─ 否 → 继续
    │
    └─ 企业级部署？
        ├─ 是 → R2R / Neo4j + RAG
        └─ 否 → LightRAG
```

## 十、学习资源

### 必读论文

```
1. GraphRAG: Unlocking LLM Discovery on Narrative Private Data
   - Microsoft GraphRAG 原始论文
   - 社区发现 + 社区摘要的核心思想

2. LightRAG: Simple and Fast Retrieval-Augmented Generation
   - EMNLP 2025
   - 双层检索的设计

3. HippoRAG: A Neurobiological Framework for Long-Term Memory
   - NeurIPS 2024
   - 模拟海马体的记忆机制

4. From Local to Global: A Graph RAG Approach to Query-Focused Summarization
   - 图检索到全局理解的演进
```

### 开源资源

```
Awesome-GraphRAG:
https://github.com/DEEP-PolyU/Awesome-GraphRAG
- 论文、项目、基准测试汇总

GraphRAG 深度学习:
https://github.com/JayLZhou/GraphRAG
- GraphRAG 源码解读

LightRAG 实验对比:
https://github.com/NanGePlus/LightRAGTest
- LightRAG vs GraphRAG 性能对比
```

### 官方文档

```
Microsoft GraphRAG:
https://microsoft.github.io/graphrag/

LightRAG:
https://github.com/HKUDS/LightRAG/blob/main/README.md

Neo4j GraphRAG:
https://neo4j.com/docs/graphrag-manual/
```

## 十一、总结

Graph RAG 是 RAG 技术的重要演进方向，让检索从"局部相似度匹配"升级为"全局图推理"。

```
核心框架对比：

Microsoft GraphRAG：
- 定位：大规模文档，全局理解
- 优势：社区摘要，全局视角
- 代价：构建慢，成本高

LightRAG：
- 定位：中小规模，快速部署
- 优势：快速、低成本、实时更新
- 代价：全局理解较弱

HippoRAG：
- 定位：长期记忆，精准检索
- 优势：模拟海马体，联想检索
- 代价：相对复杂

Neo4j + RAG：
- 定位：企业级，可视化
- 优势：成熟图数据库，生态完善
- 代价：需要维护数据库
```

**选型建议**：

- 快速上手：LightRAG
- 全局理解：Microsoft GraphRAG
- 企业部署：Neo4j + RAG 或 R2R
- 长期记忆：HippoRAG
- 本地部署：GraphRAG-Local-UI

没有银弹，关键是根据场景选择合适的工具。

---

**相关文章**：
- [RAG 技术全景：从入门到进阶]({{< relref "post/RAG 与 LangChain/04-RAG 生态与选型/RAG技术全景：从入门到进阶/index.md" >}})
- [RAGFlow 深度解析：为什么它是最值得关注的 RAG 开源项目]({{< relref "post/RAG 与 LangChain/04-RAG 生态与选型/RAGFlow深度解析：为什么它是最值得关注的RAG开源项目/index.md" >}})
