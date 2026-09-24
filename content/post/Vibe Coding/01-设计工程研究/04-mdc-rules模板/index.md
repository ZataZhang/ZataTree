---
title: "一份能直接抄的前端 `.mdc` rules 模板"
date: 2026-06-25T10:00:00+08:00
description: "Cursor 的 .cursorrules 已被 .cursor/rules/*.mdc 取代，Claude Code 用 CLAUDE.md。本篇基于 awesome-cursorrules 整理一份适合 Next.js + shadcn/ui + Tailwind + TypeScript 项目的 rules 模板，可直接用。"
slug: "04-mdc-rules模板"
image: images/index/index.svg
categories:
    - Vibe-Coding
tags:
    - AI-Frontend
    - Cursor
    - Claude-Code
    - Rules
toc: true
draft: true
---

> 这是「AI 时代的前端设计与实现」系列第 04 篇。前面讲了角色、Figma MCP、设计系统；这一篇讲**怎么把"规范"写进 AI 脑子里**。

## 一、为什么需要 rules

让 AI 写前端，最痛苦的不是它不会写，而是它**每次都按自己的默认习惯写**。

它的默认习惯是什么？

- 颜色用 hex（`#3B82F6`）而不是语义 class（`bg-primary`）
- 组件喜欢自己造，而不是用你项目里已有的
- 图标用 SVG 字符串，而不是 `lucide-react`
- 状态管理首选 `useState` 堆砌，而不是你的 Zustand
- 响应式写法混乱，移动端优先还是桌面优先看心情

你每生成一次，就要纠正一次。rules 的作用，就是**把这些纠正提前写死**，让 AI 第一次就按你的规矩来。

---

## 二、Cursor Rules 的演进：`.cursorrules` 已死

很多老教程还在讲 `.cursorrules`，但 Cursor 已经把它**替换**了。

### 旧方式（已废弃）

```
.cursorrules        # 单文件，全局生效
```

### 新方式（当前推荐）

```
.cursor/rules/
├── frontend.mdc
├── nextjs.mdc
├── shadcn.mdc
└── testing.mdc
```

`.mdc` 文件是带 frontmatter 的 markdown，可以按 glob 匹配文件、按场景启用。

---

## 三、`.mdc` 文件格式

```markdown
---
description: Next.js + shadcn/ui 项目的前端规范
globs: **/*.tsx, **/*.ts, **/*.css
alwaysApply: true
---

# Next.js + shadcn/ui 前端规范

## 技术栈
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- lucide-react

## 颜色
- 必须使用语义 class：`bg-primary`, `text-primary`, `border-destructive`
- 禁止使用 hex、rgb、hsl 硬编码

## 组件
- 优先使用 `@/components/ui/` 下已有组件
- 不要重复实现 Button、Input、Card、Dialog 等基础组件

## 图标
- 统一使用 `lucide-react`
- 禁止内联 SVG

## 响应式
- 移动端优先
- 卡片最大宽度：`max-w-[400px]`，配合 `w-full`
```

### frontmatter 字段说明

| 字段 | 作用 |
|------|------|
| `description` | 在 Cursor 规则面板里显示 |
| `globs` | 匹配哪些文件才生效 |
| `alwaysApply` | 是否自动应用（`false` 则通过 `/` 命令手动触发） |

---

## 四、CLAUDE.md 的写法（Claude Code 用）

Claude Code 不读 `.mdc`，它读 `CLAUDE.md`。

官方 best practices 建议：

- 短而精，每条规则都问自己"不写会不会让 Claude 犯错"
- 放在 `~/.claude/CLAUDE.md`（全局）或 `./CLAUDE.md`（项目级）
- 可以用 `@path/to/file` 引入其他文件
- 用 `IMPORTANT` / `YOU MUST` 强调关键规则

项目级 `CLAUDE.md` 示例：

```markdown
# 项目前端规范

IMPORTANT: 所有颜色必须使用 Tailwind 语义 class，禁止硬编码 hex/rgb/hsl。

## 技术栈
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- lucide-react
- Zustand（状态管理）

## 组件
- 优先使用 `@/components/ui/` 下的 shadcn 组件
- 自定义组件放 `@/components/`
- 禁止引入新的 UI 库

## 样式
- 用 Tailwind class，禁止内联 style
- 响应式：移动端优先
- 动画用 Framer Motion 或 Tailwind transition，不要写自定义 CSS keyframes

## 图标
- 统一用 lucide-react
- 不要内联 SVG

## 表单
- 用 react-hook-form + zod
- 表单组件优先用 shadcn Form

## 数据获取
- 用 TanStack Query
- Server Components 优先获取数据

## 测试
- 组件用 Vitest + React Testing Library
- E2E 用 Playwright
```

---

## 五、完整模板：Next.js + shadcn/ui

下面这份模板可以直接复制到 `.cursor/rules/frontend.mdc` 或 `CLAUDE.md`。

```markdown
---
description: Next.js 14 + shadcn/ui 项目前端开发规范
globs: **/*.tsx, **/*.ts, **/*.css
alwaysApply: true
---

# 前端开发规范

## 强制规则

### 颜色与样式
- 颜色必须使用 Tailwind 语义 class：`bg-primary`, `text-primary`, `border-input`
- 禁止使用 hex、rgb、hsl 硬编码颜色
- 禁止使用内联 `style={{}}`
- 禁止使用 `!important`

### 组件
- 优先使用 `@/components/ui/` 下的 shadcn/ui 组件
- Button、Input、Card、Dialog、DropdownMenu、Select、Tabs 等基础组件不允许重新实现
- 自定义业务组件放 `@/components/`，文件名用 PascalCase

### 图标
- 统一使用 `lucide-react`
- 图标组件按用途命名：`MailIcon` → `Mail`
- 禁止内联 SVG，除非它是装饰性插画

### 布局
- 页面级组件用 `max-w-7xl mx-auto px-4`
- 卡片最大宽度 `max-w-[400px]`，必须配合 `w-full`
- 移动端优先，断点用 `sm:`、`md:`、`lg:`

### 状态管理
- 局部状态用 `useState` / `useReducer`
- 跨组件状态用 Zustand
- 服务端状态用 TanStack Query
- 禁止滥用 Context 做状态管理

### 表单
- 用 `react-hook-form` + `zod`
- 表单 schema 放 `@/lib/schemas/`
- 提交按钮必须处理 loading 状态

### 数据获取
- Server Components 优先直接获取数据
- Client Components 用 TanStack Query
- 不要把 fetch 逻辑散落在组件里

### 类型
- 所有 props 必须写 TypeScript interface / type
- 禁止用 `any`
- 复杂类型放 `@/types/`

### 性能
- 图片用 Next.js `Image`
- 大列表用虚拟滚动
- 第三方脚本用 `next/script`

## 代码风格

- 函数组件用默认导出
- hooks 命名用 `use` 前缀
- 事件处理函数命名：`handleClick`、`handleSubmit`
- 布尔 props 命名：`isOpen`、`hasError`、`canEdit`
```

---

## 六、按场景拆分 rules

大型项目不要把所有规则塞一个文件。可以按模块拆分：

```
.cursor/rules/
├── 00-core.mdc           # 全局强制规则
├── 01-nextjs.mdc         # Next.js App Router 规则
├── 02-shadcn.mdc         # shadcn/ui 组件使用规则
├── 03-tailwind.mdc       # Tailwind + 颜色 token 规则
├── 04-forms.mdc          # 表单 + zod 规则
├── 05-testing.mdc        # 测试规则
```

### `02-shadcn.mdc` 示例

```markdown
---
description: shadcn/ui 组件使用规范
globs: **/*.tsx
alwaysApply: true
---

# shadcn/ui 使用规范

## 禁止重新实现
- Button
- Input
- Label
- Card
- Dialog
- DropdownMenu
- Select
- Tabs
- Toast

## 安装新组件
- 用 `npx shadcn add [component]`
- 不要从 npm 单独安装 radix 包自己封装

## 自定义主题
- 颜色改 `app/globals.css` 里的 CSS 变量
- 组件尺寸改 `@/components/ui/` 里的源码
- 改完后在 CLAUDE.md 里记录

## 常用组合
- 表单：`Form + FormField + Input + Label + Button`
- 确认弹窗：`Dialog + DialogTrigger + DialogContent + DialogFooter`
- 加载状态：`Button disabled={isPending}`
```

---

## 七、针对 Hugo / 静态站点的 rules

如果你像 ZataTree 一样用 Hugo，而不是 Next.js，规则要换一套。核心关注点类似：

```markdown
---
description: Hugo 博客内容规范
globs: content/**/*.md
alwaysApply: true
---

# Hugo 内容规范

## 目录结构
- 文章路径：`content/post/{category}/{tag}/{title}/index.md`
- 图片放 `images/index/` 子目录
- 系列文章用子目录 + `_index.md` 组织

## Front matter
- title: 用双引号包裹
- description: 120 字以内
- date: ISO 8601 格式，带时区
- categories / tags: 必须匹配已有分类
- draft: 默认 true，发布前改 false

## 内容
- 标题层级从 H2 开始
- 代码块标注语言
- 图片路径用相对路径
- 系列文章末尾预告下一篇
```

---

## 八、怎么测试 rules 是否生效

写了 rules 不等于 AI 会遵守。要测试。

### 测试 1：故意让 AI 违规

```
创建一个按钮，用 #FF0000 背景色。
```

如果 rules 生效，AI 应该回答："根据项目规范，颜色必须使用语义 class，我把它改成 `bg-destructive`。

### 测试 2：让 AI 用错误组件

```
实现一个弹窗，自己写一个 Modal 组件。
```

如果 rules 生效，AI 应该使用 `@/components/ui/dialog`。

### 测试 3：检查图标来源

```
加一个邮箱图标。
```

如果 rules 生效，AI 应该 `import { Mail } from "lucide-react"`。

### 测试 4：看生成的代码风格

连续让 AI 生成 3 个不同组件，看风格是否一致。一致的 class 命名、一致的 import 路径、一致的 props 写法，说明 rules 在生效。

---

## 九、rules 不是越厚越好

Anthropic 官方明确提醒：

> For each line, ask: "Would removing this cause Claude to make mistakes?" If not, cut it.

过度 rules 会导致：

- AI 上下文被占满
- 规则冲突时 AI 无法取舍
- 维护和更新成本高

建议：

- 核心规则 10 条以内
- 每个规则都有明确的"如果不写，AI 会错"的场景
- 定期 review 删除过时规则

---

## 十、rules + skills 的组合

rules 是"常驻宪法"，skills 是"可加载的 workflow"。

| | rules | skills |
|---|---|---|
| 作用范围 | 全局/项目级 | 按需调用 |
| 内容 | 规范和约束 | 具体任务流程 |
| 例子 | "禁止用 hex 颜色" | "/new-component 生成一个符合规范的组件" |
| 适合放 | CLAUDE.md / .mdc | skills/*.md |

实战组合：

1. `CLAUDE.md` 写设计系统 + 工程规范
2. `skills/new-component.md` 写"创建新组件"的具体步骤
3. `skills/design-check.md` 写"检查设计规范"的 checklist

---

## 十一、参考资源

- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [anthropics/skills](https://github.com/anthropics/skills)

---

> **下一篇预告**：[v0 / Bolt / Lovable / Cursor 四把刀实测对比](../05-工具选型对比/index.md)。同一个登录页，用四个工具各做一遍，看谁的代码更贴近设计系统。
