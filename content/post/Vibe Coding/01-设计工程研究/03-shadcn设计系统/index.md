---
title: "shadcn/ui + design token：LLM 原生设计系统实践"
date: 2026-06-24T18:00:00+08:00
description: "shadcn/ui 在 2025 年后把自己定位为 AI-Ready 组件库。本篇讲如何把 components.json 变成 design token 的单一真相源，让 Claude Code 直接读懂你的主题、组件和约束。"
slug: "03-shadcn设计系统"
image: images/index/index.svg
categories:
    - Vibe-Coding
tags:
    - AI-Frontend
    - shadcn-ui
    - Design-Token
    - Design-System
toc: true
draft: true
---

> 这是「AI 时代的前端设计与实现」系列第 03 篇。前两篇讲了 DE 是什么、Figma MCP 怎么读设计稿；这一篇讲**设计系统本身怎么为 AI 而写**。

## 一、为什么传统设计系统对 AI 不友好

一个典型的传统企业设计系统可能长这样：

```
design-system/
├── tokens/           # JSON 设计 token
├── components/       # React 组件源码
├── figma/            # Figma Library
├── docs/             # 文档
└── dist/             # 发布产物
```

这套东西对人很友好，但对 AI 有几个问题：

1. **token 和代码是分离的**：设计 token 在 JSON 里，组件代码在 TSX 里，AI 读不到对应关系。
2. **组件用法分散在文档里**：AI 读完组件源码，不知道推荐怎么用。
3. **主题配置不透明**：AI 不知道你的 primary 色到底是哪个 class。
4. **定制化程度高**：每个项目都魔改过，AI 用通用模板会翻车。

结果：AI 生成的代码**风格对不上、组件用不对、颜色写死**。

shadcn/ui 的解法很直接：**把设计系统变成一份机器可读、和人可改的单一配置文件**。

---

## 二、shadcn/ui 的 AI-Ready 改造

2025 年后，shadcn/ui 官方在几个方向上明确做了 AI 适配：

### 2.1 `components.json` 成为单一真相源

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "zinc",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

这份文件回答了几个关键问题：

- 项目用哪个 base color？
- CSS variables 是否开启？
- 组件别名是什么？
- 工具函数在哪？

Claude Code 读到这个文件，就不会再问你"你们的 Button 放在哪"。

### 2.2 `llms.txt`：给 LLM 看的精简文档

shadcn/ui 官网提供了 `llms.txt`：

```
https://ui.shadcn.com/llms.txt
```

这份文件是 LLM-optimized 的文档，比普通 HTML 文档更利于 AI 理解：

- 组件 API 简洁
- 用法示例直接
- 没有广告和导航噪音

你可以把 `llms.txt` 加到 Claude Code 的上下文里：

```
@https://ui.shadcn.com/llms.txt
```

### 2.3 shadcn/ui 官方 MCP Server

shadcn/ui 官方提供了 MCP server，让 Claude Code / Cursor 直接读 registry：

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["-y", "@shadcn/mcp-server"]
    }
  }
}
```

AI 可以直接查询：

- 有哪些组件可用
- 每个组件的 props
- 最新版本是什么
- 怎么安装

### 2.4 注册表机制（Registry）

shadcn/ui 不只是组件库，更是一个 registry 协议。你可以：

- 发布自己的组件到私有 registry
- 让 AI 读你的 registry
- 在团队内共享"定制版 shadcn"

```bash
npx shadcn add @myteam/button
```

---

## 三、Design Token 化：从 Figma 到代码

### 3.1 三层 token 结构

推荐把 design token 分成三层：

```
primitive/      # 原子值
  blue-500: #3B82F6
  gray-100: #F3F4F6
  spacing-4: 16px

semantic/       # 语义化
  primary: blue-500
  background: white
  muted: gray-500

component/      # 组件级
  button-primary-bg: primary
  button-primary-text: white
  input-border: border
```

### 3.2 在 CSS 变量中落地

`app/globals.css`：

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;
    --primary: 217 91% 60%;
    --primary-foreground: 0 0% 100%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 217 91% 60%;
    --radius: 0.5rem;
  }
}
```

### 3.3 在 Tailwind 里注册

`tailwind.config.ts`：

```ts
const config = {
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
};

export default config;
```

---

## 四、让 AI 读懂你的设计系统

### 4.1 项目级 CLAUDE.md

```markdown
# 前端设计系统规范

## 技术栈
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide React

## 颜色
所有颜色必须使用语义 class：
- 主色：bg-primary / text-primary
- 背景：bg-background
- 卡片：bg-card
- 错误：bg-destructive / text-destructive
- 禁用：opacity-50 cursor-not-allowed

禁止使用 hex、rgb、hsl 硬编码颜色。

## 组件
- 优先使用 @/components/ui/ 下已有组件
- 不要重复实现 Button、Input、Card、Dialog 等基础组件
- 自定义组件放 @/components/

## 间距
- 使用 Tailwind 默认间距 scale
- 区块间距优先：py-12 / py-16 / py-20
- 卡片内间距优先：p-6 / p-8

## 响应式
- 移动端优先
- 卡片最大宽度：max-w-[400px]
- 容器最大宽度：max-w-7xl mx-auto px-4

## 字体
- 标题：font-semibold / font-bold
- 正文：text-base text-foreground
- 辅助文字：text-sm text-muted-foreground
```

### 4.2 把 token 暴露给 AI

AI 读代码比读文档强。所以把 token 直接写在代码里，是最稳的。

`lib/design-tokens.ts`：

```ts
export const tokens = {
  color: {
    primary: "hsl(var(--primary))",
    background: "hsl(var(--background))",
    card: "hsl(var(--card))",
    muted: "hsl(var(--muted))",
    destructive: "hsl(var(--destructive))",
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
  },
  radius: {
    sm: "calc(var(--radius) - 4px)",
    md: "calc(var(--radius) - 2px)",
    lg: "var(--radius)",
  },
} as const;
```

### 4.3 用 components.json 约束 AI

`components.json` 里的配置，本身就是给 AI 看的：

```json
{
  "aliases": {
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

Claude Code 看到 `ui: @/components/ui`，就知道 Button 应该去这里找。

---

## 五、实战：让 AI 按你的设计系统生成卡片组件

### 5.1 给 AI 的 prompt

```
在 @/components/feature-card.tsx 创建一个特性卡片组件。

要求：
- 使用 shadcn/ui 的 Card 组件
- 包含 icon、title、description 三个 props
- icon 使用 Lucide React
- 卡片使用 bg-card、圆角 radius-lg、内边距 p-6
- hover 时边框颜色变为 border-primary/50
- 标题：text-xl font-semibold text-card-foreground
- 描述：text-sm text-muted-foreground
- 不要引入新依赖
- 写 TypeScript，导出类型
```

### 5.2 预期输出

```tsx
// components/feature-card.tsx
import { LucideIcon } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export function FeatureCard({
  icon: Icon,
  title,
  description,
}: FeatureCardProps) {
  return (
    <Card className="group bg-card p-6 transition-colors hover:border-primary/50">
      <CardHeader className="space-y-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <CardTitle className="text-xl font-semibold text-card-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
```

### 5.3 验证

让 Claude Code 检查：

```
检查 @/components/feature-card.tsx 是否符合以下规则：
1. 没有硬编码颜色
2. 使用了 shadcn/ui 的 Card
3. icon 来自 lucide-react
4. 类型定义正确
5. 响应式无误
```

---

## 六、Storybook MCP：让 AI 读你的组件故事

如果你的设计系统更复杂，光是 `components.json` 不够。可以接入 **Storybook MCP**。

Storybook MCP 把 stories / docs / API 作为组件元数据喂给 agent。根据官方 benchmark：

- 生成质量提升 12.8%
- 速度提升 2.76 倍
- token 消耗减少 27%

接入方式：

```bash
npx storybook@latest upgrade
npx storybook add @storybook/addon-mcp
```

然后 Claude Code 可以通过 MCP 查询：

- "Button 组件有哪些 variants？"
- "Dialog 的用法示例是什么？"
- "这个组件支持哪些 props？"

---

## 七、Design Token 和 AI 的关系

可以概括成一句话：

> **Design token 是设计师和 AI 之间的协议**。

| 没有 token | 有 token |
|------------|----------|
| "这里用 #3B82F6" | "这里用 primary" |
| AI 写死颜色 | AI 用语义 class |
| 换主题要全局替换 | 改 CSS 变量即可 |
| 设计稿和代码不同步 | Figma Variables = CSS Variables |
| AI 每次重新发明样式 | AI 复用已有 token |

---

## 八、常见坑

### 坑 1：token 层级混乱

不要 primitive 和 semantic 混用。AI 会分不清 "blue-500" 和 "primary" 哪个该用。

### 坑 2：CSS 变量命名不统一

避免同时存在 `--primary`、`--brand-primary`、`--main-color`。统一用 `--primary`。

### 坑 3：shadcn 组件被魔改后没文档

如果你改了 Button 的默认样式，要在 `CLAUDE.md` 里写清楚：

```markdown
Button 组件已定制：默认尺寸为 lg，圆角为 full。
```

### 坑 4：AI 读不到私有 registry

如果用了私有 shadcn registry，要让 MCP server 有权限访问。

---

## 九、总结

设计系统为 AI 而写，核心就三件事：

1. **单一真相源**：`components.json` + `globals.css` + `tailwind.config.ts`
2. **语义化 token**：primitive → semantic → component
3. **暴露给 AI**：CLAUDE.md + llms.txt + Storybook MCP

当 AI 能读你的 design system，它写的代码就不再是"风格接近"，而是"规范一致"。

这是 DE 工作的基础设施：不是每次都从零描述"用哪个颜色"，而是让 AI 继承你的设计语言。

---

## 十、参考资源

- [shadcn/ui docs](https://ui.shadcn.com/docs)
- [shadcn/ui theming](https://ui.shadcn.com/docs/theming)
- [shadcn/ui MCP](https://ui.shadcn.com/docs/mcp)
- [Storybook MCP for React](https://storybook.js.org/blog/storybook-mcp-for-react)
- [W3C Design Tokens Format](https://design-tokens.github.io/community-group/format/)

---

> **下一篇预告**：[一份能直接抄的前端 `.mdc` rules 模板]({{< relref "post/Vibe-Coding/AI-Frontend/ai-design-research/04-mdc-rules模板/index.md" >}})。会从 PatrickJS/awesome-cursorrules 整理出适合 Next.js + shadcn/ui 项目的规则模板。
