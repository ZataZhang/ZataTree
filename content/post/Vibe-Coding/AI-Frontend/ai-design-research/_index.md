---
title: "AI 时代的前端设计与实现"
description: "研究 AI 时代设计师与前端工程师的协作新范式：设计系统、Design Token、Skills、CLAUDE.md、视觉验证闭环"
slug: "ai-design-research"
---

这是关于「AI 时代，前端设计师怎么把设计稿更好地实现出来」的系列研究。

过去的流程是：设计师在 Figma 画稿 → 交付给前端 → 前端"看着图写代码"。这个流程在 AI 时代正在被重写：设计系统成为单一真相源、AI 工具直接读 token 生成代码、视觉验证由 Agent 闭环完成。设计师和前端的边界开始模糊，一个新角色正在浮现——**Design Engineer**。

本系列试图回答这些问题：

- Design Engineer 到底是个什么样的角色？谁在招、怎么定义？
- 设计稿如何"精确"地转成代码，而不是让 AI 凭感觉猜？
- 什么样的设计系统、什么样的工程规范，能让 AI 写出一致的前端？
- 设计师如何借助 Skills / CLAUDE.md / Hooks，把自己的意图固化为可复用资产？
- 视觉回归、a11y、响应式这些"设计师关心的事"，能不能用 Agent 自动化？

## 系列目录

1. [Design Engineer 到底是什么：从 Vercel 拆解到一个新角色](./01-design-engineer是什么/index.md)
2. [Figma MCP + Claude Code：从设计稿到上线的全过程](./02-figma-mcp实战/index.md)
3. [shadcn/ui + design token：LLM 原生设计系统实践](./03-shadcn设计系统/index.md)
4. [一份能直接抄的前端 `.mdc` rules 模板](./04-mdc-rules模板/index.md)

## 研究框架

```
1. 立角色   →  Design Engineer 是什么、谁在做
2. 转设计稿 →  Figma MCP、Code Connect、设计 token 化
3. 建系统   →  shadcn/ui + components.json + LLM-native 设计系统
4. 配规范   →  CLAUDE.md / .mdc rules / Skills 模板
5. 选工具   →  v0 / Bolt / Lovable / Cursor / Devin Desktop 对比
6. 验视觉   →  Chromatic / Claude in Chrome / Playwright 截图回归
```

## 学习路径

```
理解角色 → 设计系统化 → 工程规范化 → 工具选型 → 视觉验证闭环
```

## 相关资源

- [art-of-ai-frontend-design（姊妹篇：工具教程风格）](../art-of-ai-frontend-design/index.md)
- [智能体编排系列](../../../../Agent/Agent%20Orchestration/_index.md)（同样讨论"新角色 + 工具链"的研究思路）
