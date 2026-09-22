---
title: "Agent 工程实战"
description: "面向生产环境的 AI Agent 系统设计、评估、可观测性与工程化最佳实践"
date: 2026-07-23
slug: "Agent 工程实战"
---

这是 **Agent 工程实战** 系列文章的索引页。聚焦"把 Demo 变成产品"过程中必须解决的那些工程问题：稳定性、可观测性、可评估性、安全合规与成本控制。

## 系列目录

1. [Agent 工程实战开篇:从 Demo 到生产还有多远]({{< relref "post/Agent/Agent 工程实战/Agent 工程实战开篇：从 Demo 到生产还有多远/index.md" >}})
2. [数据库初始化与迁移：从创建那一刻就要钉死的三件事]({{< relref "post/Agent/Agent 工程实战/数据库初始化与迁移：从创建那一刻就要钉死的三件事/index.md" >}})
   - 配套速查：[数据库初始化原则](./数据库初始化与迁移：从创建那一刻就要钉死的三件事/数据库初始化原则.md)
3. [Agent 内容输出规范：本地给路径，远程给协议]({{< relref "post/Agent/Agent 工程实战/Agent 内容输出规范：本地给路径，远程给协议/index.md" >}})
4. [Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点]({{< relref "post/Agent/Agent 工程实战/Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点/index.md" >}})

## 这个系列覆盖什么？

| 主题 | 典型问题 |
| --- | --- |
| 架构与设计 | 单 Agent vs 多 Agent、Plan-Act-Reflect、Human-in-the-loop |
| 工具与协议 | Tool calling、MCP、Function schema 工程化 |
| 记忆系统 | 短期上下文、长期记忆、向量召回与淘汰策略 |
| 评估与回归 | 离线评测集、LLM-as-judge、线上 A/B |
| 可观测性 | Trace、Span、Token 成本、失败重试 |
| 安全与合规 | Prompt 注入防护、敏感工具白名单、审计日志 |
| 成本与性能 | 模型路由、缓存、流式响应、超时治理 |

## 与相邻 tag 的边界

- 想了解某个**具体框架**的入门用法：见 [LangChain]({{< relref "tags/LangChain" >}})、[Agent Orchestration]({{< relref "post/Agent/Agent Orchestration/_index.md" >}})
- 想研究 **RAG / 检索增强**：见 [RAG]({{< relref "tags/RAG" >}})
- 想看**学术 / 综述类**内容：见 [PaperReading](../../PaperReading/)

## 写作约定

- **图表优先**：每节至少 1 个图表 / 代码块；文字段不超过 4 行
- **"症状 → 原因 → 修复"卡片**：每个坑用结构化三栏呈现
- **可运行 / 可复现**：所有 SQL / 代码都标版本号
- **速查表 + 详细正文**：长文必配一张速查表，便于回头查