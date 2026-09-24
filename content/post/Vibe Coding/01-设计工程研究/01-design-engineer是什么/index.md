---
title: "Design Engineer 到底是什么：从 Vercel 拆解到一个新角色"
date: 2026-06-24T10:00:00+08:00
description: "Vercel 在 2024 年正式定义 Design Engineer 这个角色。本篇拆解 Vercel 的三种工作流，对比 Linear、Stripe、Figma 等公司的招聘现状，给出一份'DE 自检清单'——为什么这个角色在 AI 时代正在崛起。"
slug: "01-design-engineer是什么"
image: images/index/index.svg
categories:
    - Vibe Coding
tags:
    - 设计工程研究
    - AI-Frontend
    - Design-Engineer
    - Vercel
toc: true
draft: true
---

> 这是「AI 时代的前端设计与实现」系列第 01 篇。先把"研究什么"说清楚，再聊"怎么做"。

## 一、缘起：一种新岗位的浮现

2024 年 3 月，Vercel 官方博客发表了一篇署名 5 人的长文——**《Design Engineering at Vercel》**。这篇文章没有讲怎么写代码，也没有讲怎么用 AI；它只讲了一件事：**Vercel 内部的 Design Engineer 团队是怎么工作的**。

这是「Design Engineer」这个角色第一次被一家头部公司**系统性、官方化**地定义。在此之前，它散落在 Twitter 个人简介、零星博客、独立设计师的口头禅里；在此之后，它开始被招聘市场认真对待。

> 2026 年再回头看：Vercel 是发源地，DE 作为独立 title 主要集中在 AI / 前端工具公司；Linear、Stripe、Figma、Notion、Framer、Shopify 这些大厂**至今没有 DE 头衔**——他们走的是"Product Designer + 软件工程师"并行、个体跨栈的路线。

本篇要回答三个问题：

1. Vercel 自己怎么定义 DE？三种工作流分别是什么？
2. 为什么这个角色在 AI 时代**正在崛起**？
3. 设计师 / 前端 / 产品经理，谁应该往这个方向走？

---

## 二、Vercel 怎么定义 Design Engineer

Vercel 博客里的定义没有华丽的措辞，但非常具体。DE 不是一个新工种，而是一个**新的工作模式**——它的核心是"设计"和"工程"**不再是接力，而是**[**并集**](https://vercel.com/blog/design-engineering-at-vercel)。

Vercel 把 DE 的工作流分成三种：

### 工作流 A：与设计师协作

- 在 Figma 或 code 里**并肩工作**
- 跳过传统的 "design handoff"（设计交付）环节
- 设计师定义意图，DE 实现并迭代细节

**典型场景**：营销页、活动页、品牌视觉表达——这些"一次性"但需要设计与实现高度对齐的产物。

### 工作流 B：嵌入产品团队

- DE 作为独立个体，**嵌入某个产品团队**
- 可以独立交付 feature，也可以和该团队的设计师/工程师**共创**
- 长期归属产品组的 OKR

**典型场景**：复杂产品功能，需要 DE 的设计判断力 + 工程师的实施力。

### 工作流 C：独立 ownership

- 持续数天到数周的、**设计驱动的项目**
- DE 一个人对结果负责
- 通常用于新想法的快速验证、或品牌级体验打磨

**典型场景**：landing page redesign、design system 重构、动效系统。

> 这三种工作流的共同点：**DE 既是设计意图的源头，也是工程实现的责任人**——中间没有"翻译"环节。

### 技能要求：全栈到夸张

Vercel JD 里对 DE 的要求非常杂：

- Figma 设计（视觉、交互）
- code 设计（架构、组件）
- 生产代码（React、Next.js）
- GLSL shader（GPU 着色器）
- Three.js / WebGL / 3D
- Blender（建模）
- 视频剪辑

一句话总结：**从像素到代码、从静态到动态，DE 都得能上手**。

这不是"招一个人干两个人的活"——而是 Vercel 内部的产品（landing、官网、博客、文档、设计工具）**对"极致视觉 + 可上线代码"的需求是连续的**，中间塞一个交付环节会丢东西。

---

## 三、招聘市场：DE 到底在哪？

光看 Vercel 自己不够，要看整个市场。2026 年的实际状况是：

| 公司 | DE 头衔存在 | 替代形式 |
|------|------------|----------|
| **Vercel** | ✅ 长期招聘 | — |
| **Linear** | ❌ | Senior/Staff Product Designer + Product Engineer |
| **Stripe** | ❌ | Brand Designer + 普通工程师 |
| **Figma** | ❌ | "Software Engineer, Interaction Design" |
| **Notion** | ❌ | Product Designer + 普通工程师 |
| **Framer** | ❌ | Senior Product Engineer + Product Designer |
| **Shopify** | ❌ | Staff Brand Designer + 普通工程师 |

**结论**：

> "Design Engineer" 作为独立 title，主要集中在 **AI / 前端工具公司**（Vercel 是发源地，Anthropic、Replicate、V0 类公司里都有类似角色）。其他大厂普遍走"设计 + 工程并行 + 个体跨栈"路线——**DE 不是一个 JD 头衔，而是一种工作模式**。

这意味着两件事：

1. **不要因为某家大厂没有 DE title，就以为这个角色不存在**——它的边界更模糊，可能叫"全栈设计师"、可能叫"Creative Engineer"、可能根本藏在 Product Designer JD 的"bonus"里。
2. **DE 不是一个职位，是一个能力维度**——你可以在任何 title 下培养 DE 能力，关键是能不能在"设计意图"和"生产代码"之间**快速切换**而不掉链子。

---

## 四、为什么是现在？AI 时代的三个推力

DE 不是新概念（前端圈 10 年前就在争论"设计师要不要写代码"），但**它为什么在 2024–2026 年突然变得重要**？因为 AI 改变了三件事：

### 推力 1：实现成本断崖式下降

过去的实现成本：

> 设计师画稿 → 写 spec → 找前端 → 等排期 → 改 bug → 上线

现在的实现成本：

> 设计师描述需求 → AI 生成初版 → 设计师/DE 调细节 → 上线

**前端实现从"专业活"变成了"编辑活"**——这让"懂设计的人直接出活"成为可能。DE 角色从"理论可行"变成"经济划算"。

### 推力 2：设计系统的"资产化"

过去的设计系统是 PPT + Figma Library + Style Dictionary，**人和人交接会丢**。

现在的设计系统是：

- `components.json`（shadcn/ui 的单一真相源）
- `llms.txt`（给 LLM 读的精简文档）
- Figma Variables / Tokens（机器可读）
- Storybook + MCP（让 Agent 直接读组件元数据）

**设计 token 化、组件元数据化**之后，AI 写代码不再"凭感觉"——它能读懂你的设计系统，输出符合规范的前端。DE 不再需要手写每一行 CSS。

### 推力 3：视觉验证闭环

过去的设计验收靠人眼：

> 设计师看截图 → 找 bug → 提工单 → 前端改 → 再看截图

现在的视觉验证靠 Agent：

> Claude Code 启动 Chrome → 截图 → 调样式 → 再截图对比

**视觉回归从"人工抽查"变成"自动 diff"**。DE 不再需要依赖 QA 团队的反馈——他自己能跑完整个验证闭环。

---

## 五、谁应该成为 DE？

DE 不是"设计师转前端"或"前端转设计"——**它是两个维度的交集**：

```
         设计敏感
            ↑
            |
    DE ●    |    ● 传统设计师
            |      （实现靠前端）
            |
   传统前端 ●-------
            |
         工程能力
```

适合走 DE 路的人：

- **设计师**：已经会 Figma，想把"想法"直接变成"上线的东西"
- **前端工程师**：对视觉细节有强迫症，不愿把"好不好看"完全交给设计师
- **产品经理 / 独立开发者**：想独立完成 MVP，不被设计/前端排期卡住
- **AI 工具的重度用户**：用 Cursor / Claude Code 已经上手，缺的是"设计判断力"

不适合走 DE 路的人：

- **纯视觉艺术家**：对工程无感，活在自己的 Figma 里更自在
- **纯后端 / 算法工程师**：对像素级细节不感兴趣
- **追求"专人专事"的人**：DE 强在跨域，单域深度可能不如专家

---

## 六、DE 自检清单

如果你正在考虑往 DE 方向走，10 个问题自检：

### 设计侧

- [ ] 能用 Figma 独立完成一个完整的 landing page 设计（含交互态）
- [ ] 理解 design token（颜色、间距、字体、圆角、阴影）能 token 化
- [ ] 能区分"视觉问题"和"实现问题"——这页丑是设计没做好，还是 CSS 写歪了？
- [ ] 会写简单的 design spec（不是设计稿，而是给 AI 读的文本描述）

### 工程侧

- [ ] 能用 React/Vue 写出一个生产可用的组件（含 props、state、a11y）
- [ ] 理解 Tailwind CSS / CSS-in-JS / CSS Variables
- [ ] 会用 Git，能跑 `hugo dev` / `next dev` 看效果
- [ ] 能用 Playwright / Claude in Chrome 截图验证

### AI 侧

- [ ] 会写 CLAUDE.md / .mdc rules（让 AI 按你的规范工作）
- [ ] 会用 v0 / Bolt / Lovable / Cursor / Claude Code 中至少 2 个
- [ ] 会搭 Agent 验证闭环（hooks + Playwright + 视觉对比）

**6/10 通过**：可以开始 DE 实践
**8/10 通过**：已经是 DE
**10/10 通过**：可以开课了

---

## 七、本系列要研究的问题

回到系列开头的研究框架。本篇回答了第一个问题——**"DE 是什么"**。后续 5 篇会展开：

| 篇 | 主题 | 核心问题 |
|----|------|----------|
| 02 | Figma MCP + Claude Code | 设计稿怎么"精确"转代码？ |
| 03 | shadcn/ui + design token | 怎么搭一个 LLM-native 的设计系统？ |
| 04 | `.mdc` rules 模板 | 怎么用 CLAUDE.md 让 AI 写一致的前端？ |
| 05 | v0 / Bolt / Lovable / Cursor | AI 工具怎么选？ |
| 06 | 视觉验证 hooks | 怎么让 AI 自己做视觉回归？ |

---

## 八、参考资源

- [Design Engineering at Vercel](https://vercel.com/blog/design-engineering-at-vercel) —— DE 的"官方定义"
- [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) —— 前端 rules 模板库
- [anthropics/skills](https://github.com/anthropics/skills) —— Anthropic 官方的 frontend-design skill
- [Storybook MCP for React](https://storybook.js.org/blog/storybook-mcp-for-react) —— Agent 读设计系统的桥梁

---

> **下一篇预告**：[Figma MCP + Claude Code：从设计稿到上线的全过程]({{< relref "post/Vibe Coding/01-设计工程研究/02-figma-mcp实战/index.md" >}})。会演示用 Figma MCP 读 Variables、用 Claude Code 调样式、用 Chrome MCP 截图对比的完整流程。
