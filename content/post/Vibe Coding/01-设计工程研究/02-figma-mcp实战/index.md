---
title: "Figma MCP + Claude Code：从设计稿到上线的全过程"
date: 2026-06-24T14:00:00+08:00
description: "Figma 官方 MCP 发布后，设计稿可以直接被 AI 读取。本篇用一个登录页案例，演示从 Figma Variables、Code Connect 到 Claude Code 生成代码、Chrome MCP 截图验证的完整闭环。"
slug: "02-figma-mcp实战"
image: images/index/index.svg
categories:
    - Vibe Coding
tags:
    - 设计工程研究
    - AI-Frontend
    - Figma
    - MCP
    - Claude-Code
toc: true
draft: true
---

> 这是「AI 时代的前端设计与实现」系列第 02 篇。上一篇讲完 DE 是什么，这一篇进入实战：让 AI 读你的 Figma 稿，而不是看着截图猜。

## 一、旧流程的问题

传统设计稿转代码是这样的：

```
Figma 画稿 → 截图 → 前端手动量间距/颜色 → 写 CSS → 反复比对
```

AI 加入后，常见的版本变成：

```
Figma 画稿 → 截图给 AI → AI 生成代码 → 前端反复改
```

截图少了两个关键信息：

1. **Design token 的语义**：AI 只看到 `#3B82F6`，不知道这是 `primary`。
2. **组件的结构关系**：AI 只看到视觉结果，不知道"这是一个 Button 组件的 hover 态"。

所以 AI 生成的代码往往：**像素接近，但系统不对**——颜色用 hex、间距写死、组件重复造轮子。

Figma MCP 想解决的正是这个问题。

---

## 二、Figma MCP 是什么

2025 年 6 月，Figma 发布官方 [MCP Server](https://www.figma.com/blog/introducing-figma-mcp-server/)。它把 Figma 里的三类上下文直接喂给 coding agent：

### 1. Pattern metadata

- Variables（颜色、间距、字体变量）
- Components（组件定义）
- Styles（样式库）
- 配合 Code Connect 可以直接指向代码文件

### 2. Screenshots

- 解决 metadata 表达不了的布局、动态内容
- 用于视觉验证

### 3. Interactivity + Content

- 状态行为（hover、disabled、loading）
- 文本、SVG、图片、layer 名字、annotations

**结果**：AI 不再"看图说话"，而是"读设计系统"生成代码。

### 要求

- Figma Dev 或 Full seat
- Figma 桌面 app
- 支持 VS Code Copilot、Cursor、Windsurf、Claude Code

---

## 三、案例：一个登录页

我们用这个具体案例走完全流程：

```
设计：登录页
- 居中卡片，最大宽度 400px
- 顶部 Logo，下方表单
- 输入框：邮箱 + 密码
- 按钮：主按钮"登录"
- 错误状态：红色边框 + 下方提示
- 响应式：移动端全宽
```

目标：把它从 Figma 稿转成 Next.js + Tailwind + shadcn/ui 代码。

---

## 四、Step 1：设计稿准备（最关键）

设计稿不是画完就行的。想让 AI 生成好代码，必须满足三个条件：

### 4.1 使用 Figma Variables

颜色、间距、圆角、字体全部用 Variables，不要用硬编码。

```
primitive/blue-500    →  #3B82F6
semantic/primary      →  primitive/blue-500
semantic/error        →  primitive/red-500
spacing-md            →  16px
radius-md             →  8px
```

**关键点**：用 semantic 层包装 primitive。

AI 读到的不是 `#3B82F6`，而是 `semantic/primary`。这样生成的代码可能是：

```tsx
className="bg-primary text-primary-foreground"
```

而不是：

```tsx
className="bg-[#3B82F6] text-white"
```

### 4.2 组件与 Variants

按钮必须有 variants：

- default
- hover
- disabled
- loading

输入框也必须有 variants：

- default
- focus
- error

### 4.3 写 Annotations

在 Figma 里加注释，说明：

- "这是一个 shadcn/ui 的 Button 组件"
- "表单验证失败时，显示 error variant"
- "最大宽度 400px，移动端 100%"

这些 annotations 会被 Figma MCP 的 Content 能力读到。

---

## 五、Step 2：配置 Figma MCP

### 5.1 安装

在 Claude Code 里配置 MCP：

```bash
# 编辑 ~/.claude/CLAUDE.md 或项目 CLAUDE.md
# 添加 Figma MCP server 配置
```

更实际的做法是使用官方 Figma MCP：

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "@figma/mcp-server"],
      "env": {
        "FIGMA_API_KEY": "your-figma-api-key"
      }
    }
  }
}
```

> 配置位置取决于你用的工具。Claude Code 用 `.claude/CLAUDE.md` 或项目级别的 MCP 配置；Cursor 用 `.cursor/mcp.json`。

### 5.2 获取 Figma file key

Figma 文件 URL 形如：

```
https://www.figma.com/design/ABC123/My-Login-Page?node-id=1-234
```

`ABC123` 就是 file key。`node-id=1-234` 指向具体 frame。

---

## 六、Step 3：Claude Code 读取设计稿

启动 Claude Code，让它读取 Figma 文件：

```
读取 Figma 文件 ABC123 中 node-id=1-234 的设计稿，
我需要把它实现成一个 Next.js 14 + Tailwind CSS + shadcn/ui 的登录页。

请输出：
1. 页面结构分析
2. 用到的 design tokens（语义名和值）
3. 用到的 components（是否已有 shadcn/ui 对应组件）
4. 响应式断点
5. 交互状态说明
```

Claude Code 会通过 Figma MCP 调用 `figma_get_file` / `figma_get_nodes` 工具，返回结构化信息。

### 预期输出示例

```markdown
## 页面结构
- 外层：flex 居中，min-h-screen，padding 16px
- 卡片：max-w-[400px]，白色背景，radius-md，shadow-md
- 内容垂直 stack，gap 24px

## Design Tokens
- bg-card: #FFFFFF
- text-primary: #111827
- text-muted: #6B7280
- border-input: #E5E7EB
- primary: #3B82F6
- error: #EF4444
- spacing-md: 16px
- spacing-lg: 24px
- radius-md: 8px

## Components
- Button（shadcn/ui 已有）
- Input（shadcn/ui 已有）
- Label（shadcn/ui 已有）
- Card（shadcn/ui 已有）

## 响应式
- 默认：卡片 max-w-[400px]
- 移动端 sm：width 100%

## 交互状态
- Input focus: border-primary ring-2 ring-primary/20
- Input error: border-error + 下方 text-error 提示
- Button hover: bg-primary/90
- Button disabled: opacity-50 cursor-not-allowed
```

---

## 七、Step 4：生成代码

让 Claude Code 继续：

```
基于上面的分析，生成可运行的 Next.js 14 App Router 页面代码。

约束：
- 使用 shadcn/ui 的 Button、Input、Label、Card 组件
- 不要引入新依赖
- 颜色用 Tailwind 的语义 class（bg-primary、text-primary 等），不要用 hex
- 表单错误状态要能切换
- 响应式：卡片移动端全宽
- 代码放在 app/login/page.tsx
```

### 生成结果示例

```tsx
// app/login/page.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // mock validation
    setError("邮箱或密码错误");
  };

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-[400px]">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">欢迎回来</CardTitle>
          <CardDescription>请输入您的账号信息</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">邮箱</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                className={error ? "border-destructive" : ""}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                type="password"
                className={error ? "border-destructive" : ""}
              />
              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
            </div>
            <Button type="submit" className="w-full">
              登录
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
```

---

## 八、Step 5：Chrome MCP 视觉验证

代码生成完，不能直接收工。要验证两件事：

1. **代码能不能跑**
2. **跑出来的效果和设计稿一不一致**

用 Claude Code 的 Chrome MCP：

```bash
claude --chrome
```

然后：

```
1. 启动本地开发服务器 npm run dev
2. 浏览器打开 http://localhost:3000/login
3. 截图当前页面
4. 和 Figma 设计稿截图做对比
5. 列出视觉差异（颜色、间距、字体、布局）
6. 修复差异，直到视觉一致
```

Claude Code 会执行：

```
npm run dev
→ chrome_navigate http://localhost:3000/login
→ chrome_screenshot
→ 对比 Figma screenshot
→ chrome_click / chrome_input 测试交互态
→ 输出差异列表
→ 修改代码
→ 重复截图
```

---

## 九、Step 6：修复差异（实战中最长的一步）

AI 第一次生成的代码通常不会完美。常见差异：

| 差异 | 原因 | 修复方法 |
|------|------|----------|
| 卡片阴影不对 | Figma 的 shadow token 没映射到 Tailwind | 检查 `shadow-sm/md/lg` 对应关系 |
| 按钮高度不对 | Figma 的 padding 和 shadcn 默认不一致 | 改 `h-10` 或自定义按钮尺寸 |
| 输入框 focus ring 颜色不对 | semantic ring 变量缺失 | 在 `components.json` 或 CSS 变量中补 |
| 移动端没全宽 | max-w 没配合 w-full | 改成 `w-full max-w-[400px]` |
| 字体不对 | 没用项目字体变量 | 检查 `font-sans` 配置 |

修复流程是循环：

```
截图 → 找差异 → 改代码 → 再截图 → 直到通过
```

这是 DE 工作的核心：**不是一次性生成完美代码，而是建立"设计意图 → 代码 → 视觉验证"的反馈循环**。

---

## 十、让整个流程更稳定的技巧

### 10.1 Figma 文件分层要清晰

```
Page: Login
└── Frame: Desktop
    └── Group: Card
        ├── Logo
        ├── Title
        ├── Form
        │   ├── Input / Email
        │   ├── Input / Password
        │   └── Button / Submit
        └── Footer
```

每个组件实例都要命名清楚：`Button/Primary`、`Input/Error`、`Text/Title`。

### 10.2 用 Code Connect 绑定代码

Figma 的 Code Connect 可以把组件和代码文件绑定。AI 读到 `Button/Primary` 时，直接知道对应 `components/ui/button.tsx`。

```bash
npx figma connect
```

配置示例：

```json
{
  "codeSyntax": {
    "Button": {
      "React": "<Button>{label}</Button>",
      "imports": ["import { Button } from '@/components/ui/button'"]
    }
  }
}
```

### 10.3 在 CLAUDE.md 里写死设计规范

项目级 CLAUDE.md 写：

```markdown
## 前端实现规范
- 颜色必须映射到 Tailwind 语义 class，禁止用 hex
- 组件优先使用 shadcn/ui 已有组件
- 间距使用 design tokens（spacing-sm/md/lg）
- 响应式：移动端优先
- 所有交互元素必须有 hover/focus/disabled 状态
```

这样每次 Claude Code 生成代码，都会遵守同一套规则。

### 10.4 用 Stop Hook 强制视觉验证

`.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": {
      "run": "./scripts/visual-check.sh"
    }
  }
}
```

`scripts/visual-check.sh`：

```bash
#!/bin/bash
set -e
npm run build
npm run test:visual
```

Claude Code 不会自动结束，直到视觉测试通过。

---

## 十一、常见坑

### 坑 1：AI 读 Figma 时漏掉 auto layout

Figma 的 auto layout 对应 CSS flex/grid。AI 如果没正确识别，会生成绝对定位或硬编码 margin。解决：导出前把 auto layout 结构命名清楚，或者在 prompt 里明确要求"识别 auto layout"。

### 坑 2：Variables 命名不统一

如果设计稿里同时有 `primary`、`brand-primary`、`main-blue`，AI 会混乱。统一命名空间：`semantic/*`、`primitive/*`、`component/*`。

### 坑 3：截图和设计稿分辨率不同

Claude Code 截图可能是 1x 或 2x，Figma export 也可能是不同 scale。对比前统一 scale。

### 坑 4：动态内容和占位图

设计稿里用 placeholder 图片，实际代码用真实数据。AI 会把 placeholder 当成真实尺寸。解决：在 Figma 里标注"占位图，实际比例 16:9"。

---

## 十二、和 screenshot-to-code 的区别

你可能会问：既然有 screenshot-to-code，为什么还要 Figma MCP？

| 维度 | screenshot-to-code | Figma MCP |
|------|-------------------|-----------|
| 输入 | 图片 | Figma 结构化数据 |
| token 语义 | 无（只能看到 hex） | 有（semantic/primary） |
| 组件识别 | 弱 | 强（Code Connect） |
| 可维护性 | 低 | 高 |
| 适合 | 快速复刻灵感 | 生产代码实现 |
| 和设计师协作 | 单向 | 双向 |

简单说：**screenshot-to-code 适合"抄一个效果"，Figma MCP 适合"实现一个设计系统"**。

---

## 十三、总结：Figma MCP 改变了什么

| 旧流程 | 新流程 |
|--------|--------|
| 截图 → 凭感觉写 CSS | 读 Variables + Components → 生成规范代码 |
| 设计师交付 PNG | 设计师交付"结构化设计系统" |
| 前端手动比对 | Claude in Chrome 自动截图验证 |
| 组件重复造轮子 | Code Connect 直接复用现有组件 |

**Figma MCP 不是让 AI 替代前端，而是让 AI 读懂设计师的意图**。设计师的工作成果从"视觉稿"升级成"机器可读的设计系统"——这正是 DE 角色的核心。

---

## 十四、参考资源

- [Introducing Figma MCP Server](https://www.figma.com/blog/introducing-figma-mcp-server/)
- [Figma Code Connect](https://www.figma.com/dev-mode/code-connect/)
- [Claude Code with Chrome](https://code.claude.com/docs/en/chrome)
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming)

---

> **下一篇预告**：[shadcn/ui + design token：LLM 原生设计系统实践]({{< relref "post/Vibe Coding/01-设计工程研究/03-shadcn设计系统/index.md" >}})。会讲 `components.json` 怎么成为设计 token 的单一真相源，以及 `llms.txt` 怎么让 AI 读懂你的组件库。
