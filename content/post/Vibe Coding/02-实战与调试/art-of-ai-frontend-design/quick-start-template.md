# 🚀 AI 前端开发快速启动模板

本文档提供可直接使用的 Prompt 模板和代码片段，帮助你快速上手 AI 前端开发。

## 📝 Claude Code/Cursor Prompt 模板

### 模板 1：着陆页生成

```
创建一个现代化的 [产品名称] 着陆页，包含以下部分：

## 设计要求
- 主题：[深色/浅色/渐变]
- 主色调：#[颜色代码]
- 风格参考：[网站 URL，如 vercel.com]

## 页面结构

### 1. Hero 区域
- 标题："[主标题]"
- 副标题："[副标题]"
- CTA 按钮：[按钮文字]
- 背景：[渐变/图片/视频]

### 2. 特性展示区
- [特性1名称]：[描述]
- [特性2名称]：[描述]
- [特性3名称]：[描述]

### 3. 社会证明
- 用户评价或数据展示

### 4. 定价方案（可选）
- [定价档位]

### 5. Footer
- 版权信息、社交链接

## 技术栈
- 框架：Next.js 14 (App Router)
- 样式：Tailwind CSS
- 动画：Framer Motion
- 图标：Lucide React

## 功能要求
- ✅ 响应式设计（移动端优先）
- ✅ 滚动动画效果
- ✅ SEO 优化
- ✅ 性能优化
```

---

### 模板 2：组件生成

```
创建一个 [组件名称] 组件：

## Props 定义
- prop1: [类型] - [说明]
- prop2: [类型] - [说明]

## 功能需求
- [功能点1]
- [功能点2]

## 样式要求
- 风格：[glassmorphism / neumorphism / flat / gradient]
- 颜色：[颜色方案]
- 动画：[动画效果]

## 交互行为
- [交互场景1]
- [交互场景2]

## 技术栈
- React + TypeScript
- Tailwind CSS
- [其他库]

## 示例用法
提供使用示例代码
```

---

### 模板 3：设计系统文档

创建 `DESIGN.md` 文件：

```markdown
# [项目名称] 设计系统

## 🎨 颜色系统

### 主色
- Primary: #667eea
- Secondary: #764ba2
- Accent: #f093fb

### 中性色
- Background: #0f0f23
- Surface: #1a1a2e
- Text Primary: #ffffff
- Text Secondary: #e0e0e0

### 功能色
- Success: #10b981
- Warning: #f59e0b
- Error: #ef4444

## 📐 排版系统

### 字体
- 标题：Plus Jakarta Sans (700)
- 正文：Inter (400, 500)
- 代码：JetBrains Mono (400)

### 字号
- h1: text-5xl md:text-7xl
- h2: text-4xl md:text-5xl
- h3: text-2xl md:text-3xl
- body: text-base md:text-lg
- small: text-sm

## 📏 间距系统

使用 Tailwind 默认间距：
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)

## 🎭 组件风格

### 卡片
- 背景：backdrop-blur-xl bg-white/10
- 边框：border border-white/20
- 圆角：rounded-2xl
- 阴影：shadow-xl

### 按钮
- 主按钮：渐变背景 + rounded-full
- 次按钮：透明背景 + 边框
- 尺寸：sm / md / lg

### 输入框
- 背景：bg-white/5
- 边框：border-white/20
- Focus: ring-2 ring-purple-500

## ✨ 动画规范

### 持续时间
- 快速：150ms
- 正常：300ms
- 慢速：500ms

### 缓动函数
- 默认：ease-out
- 弹性：spring(1, 100, 10)
- 线性：linear

### 常用动画
- fadeIn: opacity 0 → 1
- slideUp: translateY(20px) → 0
- scale: scale(0.95) → 1
```

---

## 🛠️ 快速命令

### 项目初始化

```bash
# Next.js + TypeScript + Tailwind
npx create-next-app@latest my-project --typescript --tailwind --app

# 安装常用依赖
npm install framer-motion lucide-react clsx tailwind-merge

# 安装 shadcn/ui
npx shadcn-ui@latest init

# 添加常用组件
npx shadcn-ui@latest add button card dialog toast
```

### 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start

# 代码格式化
npm run lint

# 类型检查
npm run type-check
```

### 部署命令

```bash
# Vercel 部署
npx vercel

# Vercel 生产部署
npx vercel --prod

# 或者推送到 GitHub 自动部署
git add .
git commit -m "feat: add new feature"
git push origin main
```

---

## 📦 常用代码片段

### Framer Motion 动画组件

```typescript
import { motion } from "framer-motion";

// Fade In 动画
export function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
    >
      {children}
    </motion.div>
  );
}

// Scale 动画
export function ScaleOnHover({ children }: { children: React.ReactNode }) {
  return (
    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
      {children}
    </motion.div>
  );
}
```

### Glassmorphism 卡片

```typescript
export function GlassCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative group">
      {/* 光晕效果 */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-400 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity" />
      
      {/* 卡片主体 */}
      <div className="relative backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 hover:border-white/30 transition-all">
        {children}
      </div>
    </div>
  );
}
```

### 渐变文字

```typescript
export function GradientText({ children }: { children: React.ReactNode }) {
  return (
    <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400">
      {children}
    </span>
  );
}
```

### 响应式容器

```typescript
export function Container({ children }: { children: React.ReactNode }) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {children}
    </div>
  );
}
```

---

## 🎯 最佳实践清单

### 性能优化

- [ ] 使用 Next.js Image 组件优化图片
- [ ] 代码分割（dynamic import）
- [ ] 懒加载非关键组件
- [ ] 启用 Tailwind CSS JIT 模式
- [ ] 压缩静态资源

### SEO 优化

- [ ] 添加 meta 标签
- [ ] 使用语义化 HTML
- [ ] 添加 Open Graph 标签
- [ ] 创建 sitemap.xml
- [ ] 添加 robots.txt

### 无障碍访问

- [ ] 所有图片添加 alt 属性
- [ ] 表单元素关联 label
- [ ] 键盘导航支持
- [ ] 适当的颜色对比度
- [ ] ARIA 标签

### 移动端优化

- [ ] 响应式设计
- [ ] 触摸友好的交互区域
- [ ] 避免水平滚动
- [ ] 优化字体大小
- [ ] 减少动画复杂度

---

## 📚 学习资源

### 官方文档
- [Next.js 文档](https://nextjs.org/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Framer Motion 文档](https://www.framer.com/motion)
- [Lucide React 图标](https://lucide.dev)

### 灵感网站
- [Dribbble](https://dribbble.com)
- [Behance](https://behance.net)
- [Land-book](https://land-book.com)
- [Mobbin](https://mobbin.design)

### 开源项目
- [shadcn/ui](https://github.com/shadcn-ui/ui) (116k ⭐)
- [screenshot-to-code](https://github.com/abi/screenshot-to-code) (72k ⭐)
- [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) (57k ⭐)

---

**Happy Coding! 🎨✨**
