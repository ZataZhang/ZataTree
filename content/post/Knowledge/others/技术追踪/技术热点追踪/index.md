---
title: 技术热点追踪
description: "持续追踪 Agent 与文档结构化领域的技术热点与开源项目"
date: 2026-06-04T10:00:00+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - agent
    - 文档结构化
    - LLM
    - RAG
    - OCR
---

> 技术领域持续追踪记录，持续更新...

## Agent 框架

### LangChain

- **GitHub**: [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
- **Stars**: 138k
- **简介**: Agent 工程平台，提供模块化组件和第三方集成，简化 AI 应用开发。支持 LangGraph 用于构建可控的 Agent 工作流。
- **特点**: 丰富的集成生态、灵活的抽象层、生产级特性

### MetaGPT

- **GitHub**: [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)
- **Stars**: 68.5k
- **简介**: 多 Agent 框架，模拟软件公司角色协作。输入一行需求，输出完整的需求文档、数据结构、API 设计等。
- **特点**: SOP 流程化、角色扮演（产品经理/架构师/工程师）、Data Interpreter 数据分析能力

### CrewAI

- **GitHub**: [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
- **Stars**: 52.8k
- **简介**: 完全独立于 LangChain 的多 Agent 编排框架，提供 Crews（自主协作）和 Flows（事件驱动工作流）两种模式。
- **特点**: 高性能、灵活定制、无外部依赖、YAML 配置化

### AutoGen (Microsoft)

- **GitHub**: [microsoft/autogen](https://github.com/microsoft/autogen)
- **Stars**: 58.7k
- **状态**: 已进入维护模式
- **推荐**: 新项目建议使用 [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)

---

## LLM 推理

### Ollama

- **GitHub**: [ollama/ollama](https://github.com/ollama/ollama)
- **Stars**: 173k
- **简介**: 本地大模型运行工具，支持 Kimi、GLM、DeepSeek、Qwen、Gemma 等模型。一键运行，本地部署。
- **特点**:
  - 丰富的模型库
  - REST API 支持
  - 多平台支持（macOS/Windows/Linux）
  - Docker 部署
  - 与 Claude Code、Copilot 等集成

### llama.cpp

- **GitHub**: [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **Stars**: 114.5k
- **简介**: C/C++ 实现的 LLM 推理引擎，高性能、本地化运行。
- **特点**:
  - 纯 C/C++ 实现，无依赖
  - Apple Silicon 原生优化（Metal）
  - CUDA/ROCm/ Vulkan 多后端
  - 支持 1.5-8bit 量化
  - 多语言 Binding（Python/Go/JS/Rust/C# 等）

### vLLM

- **GitHub**: [vllm-project/vllm](https://github.com/vllm-project/vllm)
- **Stars**: 81.9k
- **简介**: 高吞吐量 LLM 推理服务，支持 PagedAttention、Tensor Parallelism。
- **特点**:
  - 高吞吐量推理
  - OpenAI 兼容 API
  - Continuous Batching
  - 多 GPU 分布式推理

### SGLang

- **GitHub**: [sglang-ai/sglang](https://github.com/sglang-ai/sglang)
- **Stars**: 31k
- **简介**: 高效的大模型服务框架，支持 RadixAttention、前融批处理。
- **特点**:
  - 结构化生成加速
  - 前融批处理（Early Prefill）
  - 支持对话、代码、Agent 多场景
  - 与 vLLM 互补的调度优化

---

## RAG 检索增强生成

### RAGFlow

- **GitHub**: [infiniflow/ragflow](https://github.com/infiniflow/ragflow)
- **Stars**: 81.9k
- **简介**: 基于深度文档理解的 RAG 引擎，提供端到端 RAG 工作流。
- **特点**:
  - 深度文档理解
  - 模板化分块
  - 可溯源的引用
  - 支持 GraphRAG
  - 多种数据源兼容

### 其他 RAG 工具

| 工具 | Stars | 特点 |
|------|-------|------|
| [MaxKB](https://github.com/1Panel-dev/MaxKB) | 21.1k | 开箱即用的 RAG 聊天机器人 |
| [R2R](https://github.com/SciPhi-AI/R2R) | - | 开源 RAG 引擎 |

---

## 文档结构化

### MinerU

- **GitHub**: [opendatalab/MinerU](https://github.com/opendatalab/MinerU)
- **Stars**: 66.3k
- **简介**: 高精度文档解析引擎，将 PDF、DOCX、PPTX、XLSX、图片、网页转换为 Markdown/JSON。
- **特点**:
  - VLM + OCR 双引擎，支持 109 种语言
  - 原生 DOCX/PPTX/XLSX 解析
  - 公式→LaTeX、表格→HTML
  - 表结构重建、跨页表格合并
  - MCP Server 原生集成 LangChain/Dify/FastGPT

### Marker

- **GitHub**: [datalab-to/marker](https://github.com/datalab-to/marker)
- **Stars**: 35.7k
- **简介**: 将 PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB 快速转换为 Markdown/JSON/HTML。
- **特点**:
  - 表格、公式、代码块、链接提取
  - 支持 LLM 提升准确率（Gemini/Ollama/Claude/OpenAI）
  - 支持结构化提取（Schema 定义）
  - GPU/CPU/MPS 多平台支持

### Docling

- **GitHub**: [docling/docling](https://github.com/docling-project/docling)
- **Stars**: 28.4k
- **简介**: IBM 开源的文档解析工具，支持 PDF、DOCX、HTML、图片等格式转换为 JSON/Markdown/HTML。
- **特点**:
  - 表格结构识别与转换
  - 代码块、公式、链接提取
  - 多语言支持
  - 简单易用的 API

### 其他文档工具

| 项目 | 语言 | 特点 |
|------|------|------|
| [markitdown](https://github.com/matamorphosis/markitdown) | Python | 从 Word/PDF/HTML 提取 Markdown，结构保真 |
| [unstructured](https://github.com/Unstructured-IO/unstructured) | Python | 通用文档解析，支持 30+ 格式 |
| [pyMuPDF](https://github.com/pymupdf/pymupdf) | Python | PDF 解析，提取文本、表格、图像 |
| [python-docx](https://github.com/python-openxml/python-docx) | Python | Word 文档解析 |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | Python | 专注 PDF 表格提取 |

## Data Agent 数据智能体

### Data Interpreter (MetaGPT)

- **GitHub**: [DataInterpreter/DataInterpreter](https://github.com/DataInterpreter/DataInterpreter)
- **Stars**: 9.8k
- **简介**: MetaGPT 开源的数据分析智能体，将自然语言查询转换为可执行的数据分析代码。
- **特点**:
  - 动态任务规划与分解
  - 代码生成与执行（Python/SQL）
  - 图表自动生成
  - 多数据源支持（CSV/Excel/Database/API）

### Open Data Lab 工具链

- **GitHub**: [opendatalab/OpenDataLab](https://github.com/opendatalab/OpenDataLab)
- **Stars**: 16.8k
- **简介**: 数据智能体全家桶，包含数据采集、标注、处理、分析全链路工具。
- **子项目**:
  - [LabelLLM](https://github.com/opendatalab/LabelLLM): 智能数据标注
  - [MinerU](https://github.com/opendatalab/MinerU): 文档解析
  - [PDF-Genie](https://github.com/opendatalab/PDF-Genie): PDF 智能理解

---

## 编程智能体

### SWE-Agent

- **GitHub**: [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)
- **Stars**: 19.4k
- **简介**: 软件工程智能体，可自动修复 GitHub Issues，支持代码搜索、编辑、终端操作。
- **特点**:
  - VS Code 风格工具调用
  - 根因分析能力
  - 多轮对话式修复

### OpenHands

- **GitHub**: [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)
- **Stars**: 45k
- **简介**: AI 编码智能体，支持代码编辑、bash 终端、浏览器自动化。
- **特点**:
  - 多智能体协作
  - 沙盒环境执行
  - 支持 GitHub Issues 自动修复
  - 与 VS Code 深度集成

---

## OCR 文字识别

### Surya

- **GitHub**: [datalab-to/surya](https://github.com/datalab-to/surya)
- **Stars**: 20.5k
- **简介**: 650M 参数的 OCR 模型，支持 90+ 语言。
- **特点**:
  - 高精度（olmOCR-bench 得分 83.3%）
  - 高速（RTX 5090 上 5 页/秒）
  - 布局分析
  - 表格识别
  - vLLM 或 llama.cpp 后端

---

## 相关工具汇总

| 类别 | 工具 | Stars | 用途 |
|------|------|-------|------|
| Agent | LangChain | 138k | Agent 开发框架 |
| Agent | MetaGPT | 68.5k | 多 Agent 软件开发 |
| Agent | CrewAI | 52.8k | 多 Agent 编排 |
| Data Agent | Open Data Lab | 16.8k | 数据处理全家桶 |
| 编程智能体 | SWE-Agent | 19.4k | 代码修复智能体 |
| 编程智能体 | OpenHands | 45k | AI 编码智能体 |
| LLM | Ollama | 173k | 本地模型运行 |
| LLM | llama.cpp | 114.5k | 高性能推理引擎 |
| LLM | vLLM | 81.9k | 高吞吐量推理服务 |
| LLM | SGLang | 31k | 结构化生成加速 |
| RAG | RAGFlow | 81.9k | 文档理解 RAG |
| RAG | MaxKB | 21.1k | 开箱即用的 RAG 聊天机器人 |
| 文档 | MinerU | 66.3k | PDF 解析 |
| 文档 | Marker | 35.7k | 文档转换 |
| OCR | Surya | 20.5k | 文字识别 |

---

*持续更新中...*