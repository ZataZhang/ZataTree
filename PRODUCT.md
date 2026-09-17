# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

一线开发者与工程实践者。他们在真实项目里用 AI Agent / LLM / 各类新工具做事，遇到具体问题时打开这个站——通常是搜到某篇文章，或者想找"这个工具到底靠不靠谱"的一手结论。不是在系统学习，是在解决问题。

## Product Purpose

个人技术博客（ZataTree，www.zata.cc），把作者在 AI / CS / 软件工程上的实践沉淀成可检索的知识库。存在的理由是：网上关于新工具的二手转述太多，缺一手实测。

成功 = 读者带着问题进来，看完能直接动手，或者能判断一条路该不该走。

## Positioning

**一手实测**。每篇文章建立在对工具真实运行、真实踩坑的记录上（如 herdr 文章标注"基于本机 herdr 0.9.0 的实测输出"）。这是转述型内容无法复制的。

## Operating Context

- 文章为中文，技术术语与代码保留英文
- 有英文镜像站（hugo 多语言，默认 zh-cn）
- 读者常在通勤/工位碎片时间阅读，也常在移动端
- 内容有明确的时间属性：新工具类文章会过时，读者会注意日期

## Capabilities and Constraints

- Hugo 静态站，hugo-theme-stack 主题（vendored），Giscus 评论
- 当前 304 篇文章，2025–2026，21 个分类，165 个标签
- **已知内容问题：分类体系有重复**——`Library`/`library`、`Project_Application`/`Project&Application`、`Platforms_Tools`/`Platforms&Tools`、`DeepLearning`/`DeepLearing`（拼写错误），以及 `others`、`python`、`前端架构`、`LLM`、`Chart` 等临时分类。真实语义分类约 10 个。
- 封面由 `tools/cover.py` 统一生成（1200×400 SVG，标题烘焙在图内）
- 术语沿用站内既有用法（分类名、标签名）

## Brand Commitments

- 站名 ZataTree，作者署名「扎塔-Zata」
- 已确立视觉系统：hugo-theme-stack 的浅色卡片式，深蓝 `#0B1220` 封面 + 按分类配色（见 `tools/cover.py` 的 `CATEGORY_STYLE`）
- 自托管 IBM Plex Sans（拉丁）+ 系统中文（PingFang SC / 微软雅黑）
- 浅色/暗色双模式

## Evidence on Hand

- `content/post/` 304 篇真实文章，含大量代码块、实测输出与表格
- `tools/cover.py` 生成的成套 SVG 封面
- 真实的分类/标签计数（见上文 Capabilities）
- 无：用户量数据、订阅数、商业主张。不得虚构。

## Product Principles

1. 一手实测优先于转述，结论要能被读者复现。
2. 尊重读者时间：先给结论，再给推导。
3. 内容有保质期——新工具类文章要标清版本与日期。
4. 不做营销腔，用工程语言描述工程问题。
5. 结构服务于检索：读者是来找答案的，不是来从头读的。

## Accessibility & Inclusion

正文对比度需满足 WCAG AA（4.5:1）——已作为本次修复的既定标准。
