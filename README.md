---
title: README
description: ZataTree 博客仓库说明与内容索引
date: 2025-02-24T00:00:00+08:00
---

# ZataTree

个人知识库站点，覆盖计算机基础、编程语言、算法与数据结构、操作系统、网络、数据库、AI/ML、工程实践等方向。内容以「可快速查阅」为目标写成，适合入门与查漏补缺。

- 线上地址：<https://www.zata.cc>
- 框架：Hugo（extended），主题 [hugo-theme-stack](themes/hugo-theme-stack)
- 部署：推送到 `hugo` 分支后由 GitHub Actions 自动构建并发布到 GitHub Pages

# 快速开始

```bash
# 更新主题子模块（首次克隆后必做）
git submodule update --init --recursive

# 本地预览（含草稿）
hugo server -D

# 本地预览（不含草稿）
hugo server

# 本地构建
hugo --gc --minify --baseURL "https://www.zata.cc/"
```

> **Hugo 版本注意**：CI 固定使用 **0.141.0 extended**，本机版本可能更新。改动 `layouts/` 或 `hugo.yaml` 后，本地能构建成功不代表 CI 能通过，push 后务必确认 Actions 部署成功。

本地若不做一次 `git config core.quotePath false`，中文路径文章的 `lastmod` 会解析异常，导致首页排序错乱（CI 已设置）。

# 仓库结构

```
content/
├── post/{分类}/{标签}/{文章}/index.md   # 文章正文，目录名即文章名
│                                        # （少数历史文章直接放在 {分类}/{文章}/）
├── categories/                          # 分类元数据与配图
├── tags/                                # 标签元数据与配图
└── page/                                # 独立页面（关于、归档等）
layouts/                                 # 覆盖主题的模板与 shortcode
assets/  static/                         # 样式与静态资源
tools/                                   # 辅助脚本（封面、索引、分类合并）
hugo.yaml                                # 站点与主题配置
zata.py                                  # 内容管理工具（创建分类/标签/文章）
```

# 写作规范

## 文章结构

每篇文章独占一个目录，正文固定为 `index.md`，图片等资源放在同目录的 `images/` 下：

```
content/post/{分类}/{标签}/{文章标题}/
├── index.md
└── images/index/index.svg   # 封面
```

## Front Matter

```yaml
---
title: 文章标题
description: 一句话描述，用于列表页和搜索结果
date: 2025-01-15T10:00:00+08:00
image: images/index/index.svg   # 封面，见下节
categories:
    - Agent
tags:
    - LangChain
draft: false
---
```

- `title` / `description` / `date` / `categories` / `tags` 必填，`draft` 可选。
- `slug` 已不再需要，URL 直接由目录路径决定（历史文章里残留的 `slug` 可忽略）。
- 本地写草稿用 `draft: true`，`hugo server -D` 才能看到。

## 封面图

每篇已发布文章都要有封面，并在 front matter 中用 `image: images/index/index.svg` 引用。缺封面时**不要去找图库图**，用仓库生成器产出统一风格的深色 SVG：

```bash
python3 tools/cover.py content/post/<路径>/index.md   # 单篇（可传多个路径）
python3 tools/cover.py                                # 重刷所有用 SVG 封面的文章
```

生成器会读取 front matter 的标题/标签/分类，输出 1200×400 的 SVG：深藏青底 + 左侧 6px 色条 + 标题与标签胶囊，右侧留白处放对应分类的几何图形。分类配色在 `tools/cover.py` 的 `CATEGORY_STYLE` 中定义，新增分类时在那里补一条（当前 `Book` 与 `Project_Application` 还没配，走的是默认色）。

## 分类与标签

当前分类（`categories`）：

| 分类 | 覆盖范围 |
| --- | --- |
| `Agent` | LLM 应用、LangChain/LangGraph、RAG、Agent 编排与沙箱 |
| `DeepLearning` | 模型原理、训练与微调、NLP |
| `Library` | 三方库与框架使用教程 |
| `Grammar` | 语言语法（Python、Matlab、PyQt） |
| `Design` | 架构设计、原型与图表 |
| `Engineering` | 软件工程、可观测性、DevOps |
| `Platforms_Tools` | 开发工具与平台（Docker、uv、CLI 等） |
| `Project_Application` | 动手项目与应用（爬虫、博客、运维） |
| `Vibe-Coding` | AI 辅助编码/前端实践 |
| `Knowledge` | 百科、英语、面试八股、系统知识 |
| `PaperReading` | 论文阅读笔记 |
| `Book` | 书籍读书笔记 |

标签在同一分类下保持唯一：**同一个标签只能有一种写法**，否则 Hugo 会按 key 合并，显示名会在每次构建时随机互换。标签命名风格：`Agent-*` 系列用 Title Case 加空格（如 `Agent Tracing`），其余以简短英文或中文词为宜。新增标签前先用 `python zata.py search-tags -k "关键词"` 查重。

# 工具

| 工具 | 用途 |
| --- | --- |
| `python3 tools/readme_index.py` | 依据 `content/post/` 重新生成本文件的「内容目录」段落（`--check` 只校验不写入） |
| `python3 tools/cover.py [文章路径 ...]` | 生成/重刷封面 SVG；不带参数时只处理 front matter 中 `image: images/index/index.svg` 的文章 |
| `python3 tools/merge_categories.py` | 分类合并的迁移脚本 |
| `python zata.py create -c <分类> -t <标签> -b <标题>` | 按模板新建文章 |
| `python zata.py create-category / create-tag / search-tags / gui / select` | 分类与标签的创建、查询，以及图形界面 / 交互式菜单 |
| `just search <关键词>` | 按路径或 front matter 标题检索文章 |

打包 `zata.py` 为单文件可执行程序：

```bash
pyinstaller --onefile --console --name=zata --clean zata.py
```

> `tools/` 下的脚本都是纯标准库 Python 3，无需额外依赖。

# 部署

推送 `hugo` 分支即触发 `.github/workflows/hugo.yaml`：安装 Hugo 0.141.0 extended → `hugo --gc --minify` → 发布到 GitHub Pages。无需手动操作；如需手动构建，见「快速开始」。

# 内容目录

按 `content/post/` 的实际目录结构生成，括号内为该分类的文章数。**本段由 `python3 tools/readme_index.py` 自动生成，请勿手工编辑** —— 增删文章后重新运行该脚本即可。

<!-- BEGIN:CONTENT-INDEX -->
## Agent 工程 (35)

### 01-入门与全景

- [AI agent介绍：基于大模型的人工智能代理](content/post/Agent%20工程/01-入门与全景/AI%20agent介绍：基于大模型的人工智能代理/)
- [Agent 工程实战开篇：从 Demo 到生产还有多远](content/post/Agent%20工程/01-入门与全景/Agent%20工程实战开篇：从%20Demo%20到生产还有多远/)
- [Agent 生产工程全景手册：从 Runtime 到业务闭环](content/post/Agent%20工程/01-入门与全景/Agent生产工程全景手册/)

### 02-框架与运行时

- [智能体编排设计工程师学习指南](content/post/Agent%20工程/02-框架与运行时/01-智能体编排设计工程师学习指南/)
- [Agent Runtime 详解：从模型循环到可恢复的企业执行系统](content/post/Agent%20工程/02-框架与运行时/20260922101724_Agent%20Runtime详解/)
- [AI Agent Loop 工程：原理、模式与实现](content/post/Agent%20工程/02-框架与运行时/AI%20Agent%20Loop%20工程：原理、模式与实现/)
- [Agent 用户记忆与 Skill 沉淀：开源项目参考与架构设计](content/post/Agent%20工程/02-框架与运行时/Agent%20用户记忆与%20Skill%20沉淀：开源项目参考与架构设计/)
- [Gliding Horse Agent OS 介绍：Rust 构建的工业级 AI Agent 操作系统](content/post/Agent%20工程/02-框架与运行时/Gliding%20Horse%20Agent%20OS%20介绍/)
- [主流 Agent 框架对比与多框架统一接口设计](content/post/Agent%20工程/02-框架与运行时/主流%20Agent%20框架对比与多框架统一接口设计/)
- [内置 Agent 放哪：一个 is_runnable 陷阱与三类事实源](content/post/Agent%20工程/02-框架与运行时/内置%20Agent%20放哪：一个%20is_runnable%20陷阱与三类事实源/)
- [Agent 记忆模块深度技术文档](content/post/Agent%20工程/02-框架与运行时/记忆模块技术文档/)

### 03-工程化实践

- [Agent 内容输出规范：本地给路径，远程给协议](content/post/Agent%20工程/03-工程化实践/Agent%20内容输出规范：本地给路径，远程给协议/)
- [Agent 工具没调用，先查模型到底能看见什么](content/post/Agent%20工程/03-工程化实践/Agent%20工具没调用：一次真实链路验收的三层误判/)
- [${VAR} 是谁的环境变量：一条只写不读的凭据带走平台密钥](content/post/Agent%20工程/03-工程化实践/MCP%20环境变量展开：一条只写不读的凭据带走平台密钥/)
- [OpenAI Responses API与Chat Completions API区别详解](content/post/Agent%20工程/03-工程化实践/OpenAI%20Responses%20API与Chat%20Completions%20API区别详解/)
- [ai返回数据的格式不稳定，存在解析错误的问题](content/post/Agent%20工程/03-工程化实践/ai返回数据的格式不稳定，存在解析错误的问题/)
- [数据库初始化与迁移：从创建那一刻就要钉死的三件事](content/post/Agent%20工程/03-工程化实践/数据库初始化与迁移：从创建那一刻就要钉死的三件事/)
- [相同LLM不同提示词的对比](content/post/Agent%20工程/03-工程化实践/相同LLM不同提示词的对比/)
- [给 Agent 接入 Web Search：四种做法，和一条我试过之后放弃的路](content/post/Agent%20工程/03-工程化实践/给%20Agent%20接入%20Web%20Search：四种做法，和一条我试过之后放弃的路/)
- [让用户选择指定 Skill：从社区实践到生产级 API 设计](content/post/Agent%20工程/03-工程化实践/让用户选择指定%20Skill：从社区实践到生产级%20API%20设计/)
- [阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍](content/post/Agent%20工程/03-工程化实践/阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍/)

### 04-可观测与协议

- [AG-UI：当 Agent 学会了和前端说话](content/post/Agent%20工程/04-可观测与协议/AG-UI：当Agent学会了和前端说话/)
- [Agent Run 流式协议：事件溯源、SSE 投影与断线恢复](content/post/Agent%20工程/04-可观测与协议/Agent%20Run%20流式协议：事件溯源、SSE%20投影与断线恢复/)
- [Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点](content/post/Agent%20工程/04-可观测与协议/Agent%20Tracing%20基础：Trace、Span%20与%20OpenTelemetry%20埋点/)
- [Agent 决策审计落地：写入点、复核器与门禁降级判据](content/post/Agent%20工程/04-可观测与协议/Agent%20决策审计落地：写入点、复核器与门禁降级判据/)
- [Agent 决策审计：它与 Tracing 的关系](content/post/Agent%20工程/04-可观测与协议/Agent%20决策审计：它与%20Tracing%20的关系/)
- [Agent 埋点接 ARMS：上报返回 success，控制台却是空的](content/post/Agent%20工程/04-可观测与协议/Agent%20埋点接%20ARMS：上报返回%20success，控制台却是空的/)
- [Session、Thread、Run：一条消息为什么是一个 Run](content/post/Agent%20工程/04-可观测与协议/Session、Thread、Run：一条消息为什么是一个%20Run/)
- [全量解码与增量解码：原理、区别以及应用](content/post/Agent%20工程/04-可观测与协议/全量解码与增量解码：原理、区别以及应用/)

### 05-沙箱与执行环境

- [Agent 沙箱选型指南：隔离边界、产品对比与判断标准](content/post/Agent%20工程/05-沙箱与执行环境/Agent%20沙箱选型指南：隔离边界、产品对比与判断标准/)
- [Cua 框架详解：给任何 Agent 一台可操控的电脑](content/post/Agent%20工程/05-沙箱与执行环境/Cua%20框架详解：给任何%20Agent%20一台可操控的电脑/)
- [E2B 迁到阿里云云沙箱：能跑通，但别急着上生产](content/post/Agent%20工程/05-沙箱与执行环境/E2B%20迁到阿里云云沙箱：能跑通，但别急着上生产/)

### 06-应用与集成

- [n8n](content/post/Agent%20工程/06-应用与集成/n8n/)
- [nl2sql](content/post/Agent%20工程/06-应用与集成/nl2sql/)
- [openclaw](content/post/Agent%20工程/06-应用与集成/openclaw/)

## RAG 与 LangChain (17)

### 01-LangChain 基础

- [LangChain 与 MCP 极简教程：让 Agent 接入外部工具的另一种方式](content/post/RAG%20与%20LangChain/01-LangChain%20基础/LangChain与MCP极简教程/)
- [LangChain 常见报错与排查指南](content/post/RAG%20与%20LangChain/01-LangChain%20基础/LangChain常见报错与排查/)
- [LangChain 模型接入指南：OpenAI 兼容协议与多平台调用](content/post/RAG%20与%20LangChain/01-LangChain%20基础/LangChain模型接入指南/)
- [LangSmith使用教程](content/post/RAG%20与%20LangChain/01-LangChain%20基础/LangSmith使用教程/)
- [langchain_core 组件详解：Prompt 模板与 Output Parsers](content/post/RAG%20与%20LangChain/01-LangChain%20基础/langchain_core组件详解/)

### 02-LangChain 进阶

- [DeepAgents完全指南](content/post/RAG%20与%20LangChain/02-LangChain%20进阶/DeepAgents完全指南/)
- [Langchain-RAG实战教程](content/post/RAG%20与%20LangChain/02-LangChain%20进阶/LangChain-RAG实战教程/)
- [LangGraph 实战：StateGraph、手写 ReAct 循环与 Map-Reduce 摘要](content/post/RAG%20与%20LangChain/02-LangChain%20进阶/LangGraph实战教程/)
- [一个订阅更新摘要 Agent 的完整实践：从提示词踩坑到长文本分块](content/post/RAG%20与%20LangChain/02-LangChain%20进阶/订阅摘要Agent实战/)

### 03-RAG 原理与实践

- [RAG入门：从问题定义到系统设计](content/post/RAG%20与%20LangChain/03-RAG%20原理与实践/01-RAG入门：从问题定义到系统设计/)
- [RAG进阶：Chunking、召回、Hybrid Search 与 Rerank](content/post/RAG%20与%20LangChain/03-RAG%20原理与实践/02-RAG进阶：Chunking、召回、Hybrid%20Search%20与%20Rerank/)
- [RAG评测与 Inspect：如何知道问题出在检索、重排还是生成](content/post/RAG%20与%20LangChain/03-RAG%20原理与实践/03-RAG评测与%20Inspect：如何知道问题出在检索、重排还是生成/)
- [RAG生产实践：常见坑、性能优化与迭代路线图](content/post/RAG%20与%20LangChain/03-RAG%20原理与实践/04-RAG生产实践：常见坑、性能优化与迭代路线图/)

### 04-RAG 生态与选型

- [Graph RAG 开源项目全景：从微软 GraphRAG 到 LightRAG](content/post/RAG%20与%20LangChain/04-RAG%20生态与选型/GraphRAG开源项目全景：从微软GraphRAG到LightRAG/)
- [RAGFlow 深度解析：为什么它是最值得关注的 RAG 开源项目](content/post/RAG%20与%20LangChain/04-RAG%20生态与选型/RAGFlow深度解析：为什么它是最值得关注的RAG开源项目/)
- [RAG 技术全景：从入门到进阶](content/post/RAG%20与%20LangChain/04-RAG%20生态与选型/RAG技术全景：从入门到进阶/)
- [vector-database](content/post/RAG%20与%20LangChain/04-RAG%20生态与选型/vector-database/)

## Vibe Coding (7)

### 01-设计工程研究

- [Design Engineer 到底是什么：从 Vercel 拆解到一个新角色](content/post/Vibe%20Coding/01-设计工程研究/01-design-engineer是什么/)
- [Figma MCP + Claude Code：从设计稿到上线的全过程](content/post/Vibe%20Coding/01-设计工程研究/02-figma-mcp实战/)
- [shadcn/ui + design token：LLM 原生设计系统实践](content/post/Vibe%20Coding/01-设计工程研究/03-shadcn设计系统/)
- [一份能直接抄的前端 `.mdc` rules 模板](content/post/Vibe%20Coding/01-设计工程研究/04-mdc-rules模板/)

### 02-实战与调试

- [AI 前端调试技巧：把被遮挡翻译成尺寸约束](content/post/Vibe%20Coding/02-实战与调试/AI%20前端调试技巧：把被遮挡翻译成尺寸约束/)
- [下拉框里显示 _all：Base UI 与 Radix Select 的一个行为差异](content/post/Vibe%20Coding/02-实战与调试/Base%20UI%20Select%20显示%20_all%20的坑/)
- [用 AI 打造惊艳前端：从 Vibe Coding 到实战的艺术指南](content/post/Vibe%20Coding/02-实战与调试/art-of-ai-frontend-design/)

## Web 开发 (17)

### 01-FastAPI

- [ALL-fastapi](content/post/Web%20开发/01-FastAPI/fastapi-ALL/)
- [fastapi-docs_swagger_UI-openAPI](content/post/Web%20开发/01-FastAPI/fastapi-docs_swagger_UI/)
- [fastapi-前提知识](content/post/Web%20开发/01-FastAPI/fastapi-前提知识/)
- [fastapi使用教程](content/post/Web%20开发/01-FastAPI/fastapi-第一个简单示例/)
- [FASTAPI使用相关问题](content/post/Web%20开发/01-FastAPI/fastapi使用/)
- [jwt-with-fastapi](content/post/Web%20开发/01-FastAPI/jwt-with-fastapi/)
- [注入依赖进一步解释](content/post/Web%20开发/01-FastAPI/注入依赖进一步解释/)

### 02-Flask 与后端模式

- [Building asynchronous APIs for handling long-term tasks and dynamic resources](content/post/Web%20开发/02-Flask%20与后端模式/Building%20asynchronous%20APIs%20for%20handling%20long-term%20tasks%20and%20dynamic%20resources/)
- [Celery](content/post/Web%20开发/02-Flask%20与后端模式/Celery/)
- [Flask使用教程](content/post/Web%20开发/02-Flask%20与后端模式/Flask使用/)
- [Jinja是什么？可以用在做什么？](content/post/Web%20开发/02-Flask%20与后端模式/Jinja是什么？可以用在做什么？/)
- [flask-构建一个简单的文件同步系统](content/post/Web%20开发/02-Flask%20与后端模式/flask-构建一个简单的文件同步系统/)

### 03-快速原型框架

- [gradio教程](content/post/Web%20开发/03-快速原型框架/gradio/)
- [streamlit使用教程](content/post/Web%20开发/03-快速原型框架/streamlit使用教程/)

### 04-前端与跨端

- [React框架使用教程](content/post/Web%20开发/04-前端与跨端/React框架使用教程/)
- [flutter_tutorial](content/post/Web%20开发/04-前端与跨端/flutter_tutorial/)
- [Refine: 当 API 即界面，CRUD 不再是体力活](content/post/Web%20开发/04-前端与跨端/refine-meta-framework/)

## 工程实践 (11)

### 01-可观测性

- [LogQL 查询语言详解：先选流，再过滤，最后才解析](content/post/工程实践/01-可观测性/LogQL查询语言详解/)
- [云原生可观测性：从"监控"到"洞察"的进化之路](content/post/工程实践/01-可观测性/云原生可观测性-从监控到洞察的进化之路/)
- [项目中日志的使用教程](content/post/工程实践/01-可观测性/项目中日志的使用教程/)

### 02-流程与规范

- [代码写作心得-使用教程](content/post/工程实践/02-流程与规范/代码写作心得-使用教程/)
- [怎么保存.env文件到github公开的仓库](content/post/工程实践/02-流程与规范/怎么保存.env文件到github公开的仓库/)
- [软件项目开发流程使用教程](content/post/工程实践/02-流程与规范/软件项目开发流程/)
- [通用模板规范GeneralTemplateSpecifications](content/post/工程实践/02-流程与规范/通用模板规范GeneralTemplateSpecifications/)

### 03-DevOps 与平台

- [Docker 和 Traefik 一键安装脚本](content/post/工程实践/03-DevOps%20与平台/Docker-Traefik一键安装脚本/)
- [Woodpecker CI 使用教程](content/post/工程实践/03-DevOps%20与平台/Woodpecker-CI使用教程/)
- [企业AI工具平台架构设计：拥抱快速变化的AI生态](content/post/工程实践/03-DevOps%20与平台/ai-platform-architecture/)
- [开发问题与解法笔记](content/post/工程实践/03-DevOps%20与平台/开发问题与解法笔记/)

## 开发工具链 (27)

### 01-Git 与 GitHub

- [Self-hosted Runner](content/post/开发工具链/01-Git%20与%20GitHub/Self-hosted%20Runner/)
- [gh使用教程](content/post/开发工具链/01-Git%20与%20GitHub/gh使用教程/)
- [git&github_tutorial](content/post/开发工具链/01-Git%20与%20GitHub/git&github使用/)
- [git-submodule-子模块](content/post/开发工具链/01-Git%20与%20GitHub/git-submodule-子模块/)
- [2-github action 使用](content/post/开发工具链/01-Git%20与%20GitHub/github%20action/)
- [github release](content/post/开发工具链/01-Git%20与%20GitHub/github%20release/)

### 02-Docker 与容器

- [Docker Compose(dev\test\prod)](content/post/开发工具链/02-Docker%20与容器/Docker%20Compose(devtestprod)/)
- [Docker Swarm 实战（一）：核心概念与集群管理](content/post/开发工具链/02-Docker%20与容器/Docker%20Swarm%20实战/)
- [Docker Swarm 实战（二）：Traefik 反向代理部署](content/post/开发工具链/02-Docker%20与容器/Docker%20Swarm%20实战%20-%20Traefik%20反向代理部署/)
- [Docker 私有镜像仓库registry](content/post/开发工具链/02-Docker%20与容器/Docker%20私有仓库/)
- [Docker使用实战-compose教程](content/post/开发工具链/02-Docker%20与容器/Docker使用实战-compose教程/)
- [build x86 image in ARM MAC platform and devolopmet to remote server](content/post/开发工具链/02-Docker%20与容器/build%20x86%20image%20in%20ARM%20MAC%20platform%20and%20devolopmet%20to%20remote%20server/)
- [docker-ubuntu容器中安装miniconda问题合集](content/post/开发工具链/02-Docker%20与容器/docker-ubuntu容器中安装miniconda问题合集/)
- [docker使用教程](content/post/开发工具链/02-Docker%20与容器/docker容器相关命令/)

### 03-浏览器自动化

- [AI 生成前端的 E2E 实践：用 Playwright 做视觉回归和功能兜底](content/post/开发工具链/03-浏览器自动化/ai-frontend-e2e/)
- [浏览器会话录制与接口回放：方案调研](content/post/开发工具链/03-浏览器自动化/browser-session-replay/)
- [扩展式 RPA：从 Chrome 扩展原理到 Playwright 实战方案](content/post/开发工具链/03-浏览器自动化/extension-rpa/)
- [从 noVNC 到 Playwright 截图流：容器内 VNC 踩坑记](content/post/开发工具链/03-浏览器自动化/novnc-playwright/)
- [Playwright 使用实践与本地浏览器 Profile 避坑](content/post/开发工具链/03-浏览器自动化/playwright-profile/)
- [Playwright Chromium 在 Docker 内 SIGTRAP 启动崩溃排查实录](content/post/开发工具链/03-浏览器自动化/playwright-sigtrap/)

### 04-终端与编辑器

- [VScode使用教程|cursor使用教程](content/post/开发工具链/04-终端与编辑器/VScode安装和配置/)
- [CC Switch 详解：一个应用管住八个 AI 编程 CLI](content/post/开发工具链/04-终端与编辑器/cc-switch-guide/)
- [copier-using](content/post/开发工具链/04-终端与编辑器/copier-using/)
- [Herdr 详解：给 AI Agent 用的终端运行时](content/post/开发工具链/04-终端与编辑器/herdr-ai-agent-terminal-runtime/)
- [为 AI 而写的 CLI 设计指南：原则、避坑与难点](content/post/开发工具链/04-终端与编辑器/为AI而写的CLI设计指南/)

### 05-AI 与创作工具

- [用 AI 把文章做成口播视频：三条路线、工具盘点与落地管线](content/post/开发工具链/05-AI%20与创作工具/ai-article-to-video/)
- [Blender 详解：奥斯卡和 AI Agent 为什么都选了它](content/post/开发工具链/05-AI%20与创作工具/blender-complete-guide/)

## 效率与文档 (10)

### 01-写作与排版

- [Markdown中常用的图标或徽章](content/post/效率与文档/01-写作与排版/Markdown中常用的图标或徽章/)
- [“categories”（类别）和“tags”（标签）的区别](content/post/效率与文档/01-写作与排版/categories和tags的区别/)
- [markdown使用技巧](content/post/效率与文档/01-写作与排版/markdown使用技巧/)
- [word-封面-你文档的门面](content/post/效率与文档/01-写作与排版/word-封面-你文档的门面/)
- [word技巧-排版和布局](content/post/效率与文档/01-写作与排版/word技巧-排版和布局/)
- [如何提成所写文档和ppt的颜值](content/post/效率与文档/01-写作与排版/如何提成所写文档和ppt的颜值/)
- [文档结构化实战：从 Markdown/PDF 到 Word](content/post/效率与文档/01-写作与排版/文档结构化实战/)

### 02-系统小技巧

- [mac os使用经验](content/post/效率与文档/02-系统小技巧/macos使用经验/)
- [关闭win11更新](content/post/效率与文档/02-系统小技巧/关闭win11更新/)
- [在overleaf中为什么两个完全一样的代码一个不能显示图片](content/post/效率与文档/02-系统小技巧/在overleaf中为什么两个完全一样的代码一个不能显示图片/)

## 数据科学 (13)

### 01-Transformers 全家桶

- [datasets](content/post/数据科学/01-Transformers%20全家桶/datasets/)
- [evaluate](content/post/数据科学/01-Transformers%20全家桶/evaluate/)
- [model](content/post/数据科学/01-Transformers%20全家桶/model/)
- [pipeline](content/post/数据科学/01-Transformers%20全家桶/pipeline/)
- [tokenizer](content/post/数据科学/01-Transformers%20全家桶/tokenizer/)
- [trainer](content/post/数据科学/01-Transformers%20全家桶/trainer/)

### 02-数值与科学计算

- [matplotlib教程-zata——v0.0.0](content/post/数据科学/02-数值与科学计算/matplotlib使用教程_Zata_v0.0.0/)
- [numpy使用教程](content/post/数据科学/02-数值与科学计算/numpy使用教程/)
- [pandas使用教程](content/post/数据科学/02-数值与科学计算/pandas使用教程/)
- [scipy](content/post/数据科学/02-数值与科学计算/scipy/)

### 03-建模与部署

- [onnx使用教程](content/post/数据科学/03-建模与部署/onnx使用教程/)
- [sklearn使用教程](content/post/数据科学/03-建模与部署/sklearn使用教程/)
- [torch使用教程-zata——v0.0.0](content/post/数据科学/03-建模与部署/torch使用教程_Zata_v0.0.0/)

## 构建与打包 (10)

### 01-依赖与环境管理

- [conda使用教程|pip使用教程|依赖安装_使用教程](content/post/构建与打包/01-依赖与环境管理/conda使用相关/)
- [npm使用教程](content/post/构建与打包/01-依赖与环境管理/npm使用教程/)
- [pipx使用教程](content/post/构建与打包/01-依赖与环境管理/pipx使用教程/)
- [包管理工具poetry使用教程](content/post/构建与打包/01-依赖与环境管理/包管理工具poetry使用教程/)
- [包管理工具uv使用教程](content/post/构建与打包/01-依赖与环境管理/包管理工具uv使用教程/)

### 02-打包发布

- [PyInstaller使用教程](content/post/构建与打包/02-打包发布/PyInstaller-简易教程/)
- [PyStand-简易教程](content/post/构建与打包/02-打包发布/PyStand-简易教程/)
- [Pyinstaller-打包gradio项目](content/post/构建与打包/02-打包发布/Pyinstaller-打包gradio项目/)
- [python程序打包exe使用教程](content/post/构建与打包/02-打包发布/PythonGUI-打包成exe/)
- [setuptools-打包python项目为egg / 安装库函数](content/post/构建与打包/02-打包发布/setuptools-打包python项目为egg/)

## 深度学习 (21)

### 01-模型与机制

- [DeepSeek_NSA](content/post/深度学习/01-模型与机制/Deepseek_NSA/)
- [ICL-上下文学习](content/post/深度学习/01-模型与机制/ICL-上下文学习/)
- [Jev：不写字的决策模型，和它真正适合解决的问题](content/post/深度学习/01-模型与机制/Jev：不写字的决策模型，和它真正适合解决的问题/)
- [MoE](content/post/深度学习/01-模型与机制/MoE/)
- [Attention](content/post/深度学习/01-模型与机制/attention注意力机制/)
- [大模型结构原理与代码实现](content/post/深度学习/01-模型与机制/模型-transformer原理和代码实现/)

### 02-训练与对齐

- [Alignment-DPOvsPPOvsGRPO](content/post/深度学习/02-训练与对齐/Alignment-DPOvsPPOvsGRPO/)
- [LLM微调：qwen2_chat模型部署和微调](content/post/深度学习/02-训练与对齐/LLM微调：qwen2_chat模型部署和微调/)
- [RLHF](content/post/深度学习/02-训练与对齐/RLHF/)
- [增量学习研究综述：理论、方法、应用与未来展望](content/post/深度学习/02-训练与对齐/增量学习研究综述：理论、方法、应用与未来展望/)

### 03-NLP 任务

- [命名实体识别](content/post/深度学习/03-NLP%20任务/命名实体识别/)
- [文本分类](content/post/深度学习/03-NLP%20任务/文本分类/)

### 04-推理与部署

- [深度学习开源框架](content/post/深度学习/04-推理与部署/DeepSpeed/)
- [openbayes算力平台使用教程](content/post/深度学习/04-推理与部署/openbayes算力平台使用教程/)
- [vllm](content/post/深度学习/04-推理与部署/vllm/)
- [vllm使用教程](content/post/深度学习/04-推理与部署/vllm实战教程/)

### 05-基础与方法

- [JAX](content/post/深度学习/05-基础与方法/JAX/)
- [mechine_learning_models](content/post/深度学习/05-基础与方法/mechine_learning_models/)
- [什么是算子？](content/post/深度学习/05-基础与方法/什么是算子？/)
- [字典学习（Dictionary Learning）](content/post/深度学习/05-基础与方法/字典学习（Dictionary%20Learning）/)
- [对比了几种大模型在相同任务下的表现](content/post/深度学习/05-基础与方法/对比了几种大模型在相同任务下的表现/)

## 科技月报 (4)

- [技术热点追踪](content/post/科技月报/技术热点追踪/)
- [科技月报-2025](content/post/科技月报/科技月报-2025/)
- [科技月报-2026](content/post/科技月报/科技月报-2026/)
- [❤️每日思考和AI资讯](content/post/科技月报/资讯和思考/)

## 编程语言 (29)

### 01-语言基础

- [Matlab-基本语法](content/post/编程语言/01-语言基础/Matlab-基本语法/)
- [Python-Docstring 的详细教程](content/post/编程语言/01-语言基础/python-Docstring%20的详细教程/)
- [【python】__init__.py为什么要写](content/post/编程语言/01-语言基础/python-__init__.py为什么要写/)
- [python-staticmethod 修饰符](content/post/编程语言/01-语言基础/python-staticmethod%20修饰符/)
- [python-typing提高代码可读性](content/post/编程语言/01-语言基础/python-typing提高代码可读性/)
- [python-应如何定义包通用的变量-推荐config.py](content/post/编程语言/01-语言基础/python-应如何定义包通用的变量-推荐config.py/)
- [python-数据类](content/post/编程语言/01-语言基础/python-数据类/)
- [python-类-类变量和实例变量](content/post/编程语言/01-语言基础/python-类/)
- [python的命名规范](content/post/编程语言/01-语言基础/python的命名规范/)

### 02-包与工程化

- [python-logging模块添加日志](content/post/编程语言/02-包与工程化/python-logging模块添加日志/)
- [python-lru_cache 缓存装饰器](content/post/编程语言/02-包与工程化/python-lru_cache%20缓存装饰器/)
- [python-在项目中应该如何定义文件路径](content/post/编程语言/02-包与工程化/python-在项目中应该如何定义文件路径/)
- [python-将py文件编译为pyc文件并运行](content/post/编程语言/02-包与工程化/python-将py文件编译为pyc文件并运行/)
- [python-相对导入错误attempted relative import with no known parent package](content/post/编程语言/02-包与工程化/python-相对导入错误attempted%20relative%20import%20with%20no%20known%20parent%20package/)
- [python使用教程-难点和遇到的问题](content/post/编程语言/02-包与工程化/python-难点和遇到的问题/)
- [python中将函数设置为定时任务](content/post/编程语言/02-包与工程化/python中将函数设置为定时任务/)

### 03-常用库

- [PyYAML](content/post/编程语言/03-常用库/PyYAML/)
- [Typer + Rich 入门教程](content/post/编程语言/03-常用库/Typer和Rich入门教程/)
- [pickle](content/post/编程语言/03-常用库/pickle/)
- [pydantic使用教程](content/post/编程语言/03-常用库/pydantic使用教程/)
- [pytest测试用例使用教程](content/post/编程语言/03-常用库/pytest/)
- [python开发环境配置指南](content/post/编程语言/03-常用库/python开发环境配置指南/)
- [tableprint使用教程](content/post/编程语言/03-常用库/tableprint使用教程/)
- [toml_usage_tutorial](content/post/编程语言/03-常用库/toml_usage使用教程/)

### 04-界面与串口

- [PyQt-入门教程（AI生成）](content/post/编程语言/04-界面与串口/PyQt-入门教程/)
- [PyQt-设备像素设置](content/post/编程语言/04-界面与串口/PyQt-设备像素设置/)
- [pyserial-使用教程](content/post/编程语言/04-界面与串口/pyserial-Python%20中最常用的串口通信库快速入门/)

### 05-数据与 ORM

- [Alembic](content/post/编程语言/05-数据与%20ORM/Alembic/)
- [SQLAlchemy简单入门](content/post/编程语言/05-数据与%20ORM/SQLAlchemy简单入门/)

## 设计 (14)

### 01-软件架构

- [从脚本到企业级平台：AI Agent 系统"整洁架构"演进与 Python 落地指南](content/post/设计/01-软件架构/AI-Agent四层模块化单体架构/)
- [FastAPI 后端架构设计](content/post/设计/01-软件架构/FastAPI后端架构设计/)
- [一个标准的软件项目结构](content/post/设计/01-软件架构/一个标准的软件项目结构/)
- [一个软件项目的文件目录应该怎么定义](content/post/设计/01-软件架构/一个软件项目的文件目录应该怎么定义/)
- [简洁架构（Clean Architecture）：让业务逻辑永远不依赖框架](content/post/设计/01-软件架构/简洁架构-Clean-Architecture/)
- [软件架构设计-培养软件架构师的思维](content/post/设计/01-软件架构/软件架构设计-培养软件架构师的思维/)
- [领域驱动设计（DDD）分层架构：用领域语言构建复杂系统](content/post/设计/01-软件架构/领域驱动设计分层架构-DDD/)

### 02-UML 建模图

- [数据流图](content/post/设计/02-UML%20建模图/数据流图/)
- [用例图](content/post/设计/02-UML%20建模图/用例图/)
- [类图](content/post/设计/02-UML%20建模图/类图/)

### 03-原型与灵感

- [作图参考](content/post/设计/03-原型与灵感/作图参考/)
- [使用ai工具绘制原型图html并导入figma](content/post/设计/03-原型与灵感/使用ai工具绘制原型图html并导入figma/)
- [分类图](content/post/设计/03-原型与灵感/分类图/)
- [漂亮的reademe文件使用教程](content/post/设计/03-原型与灵感/漂亮的reademe文件使用教程/)

## 软件试用 (30)

### 01-AI 工具试用

- [软件工程的范式转移：基于 Claude Code 与智能体协作的高效编程实践](content/post/软件试用/01-AI%20工具试用/Efficient%20Programming%20Based%20on%20Claude%20Code%20Collaboration%20with%20Intelligent%20Agents/)
- [Tavily-搜索引擎api](content/post/软件试用/01-AI%20工具试用/Tavily/)
- [cc-switch](content/post/软件试用/01-AI%20工具试用/cc-switch/)
- [ccNexus](content/post/软件试用/01-AI%20工具试用/ccNexus/)
- [cherry-studio](content/post/软件试用/01-AI%20工具试用/cherry-studio/)
- [claude-code&codex&Gemini-cli](content/post/软件试用/01-AI%20工具试用/claude-code/)
- [coze](content/post/软件试用/01-AI%20工具试用/coze/)
- [cursor使用教程](content/post/软件试用/01-AI%20工具试用/cursor使用教程/)
- [everything-claude-code](content/post/软件试用/01-AI%20工具试用/everything-claude-code/)
- [flora无限画布](content/post/软件试用/01-AI%20工具试用/flora无限画布/)
- [wrap.dev](content/post/软件试用/01-AI%20工具试用/wrap.dev/)
- [百度自由画布](content/post/软件试用/01-AI%20工具试用/百度自由画布/)

### 02-终端与包管理

- [homebrew](content/post/软件试用/02-终端与包管理/homebrew/)
- [nvm](content/post/软件试用/02-终端与包管理/nvm/)
- [postman](content/post/软件试用/02-终端与包管理/postman/)
- [tmux简易使用](content/post/软件试用/02-终端与包管理/tmux/)
- [wsl使用教程](content/post/软件试用/02-终端与包管理/wsl使用教程/)
- [多台电脑环境变量(.env)同步方案](content/post/软件试用/02-终端与包管理/多台电脑环境变量(.env)同步方案/)
- [新电脑快速配置-scoop](content/post/软件试用/02-终端与包管理/新电脑快速配置-scoop-homebrew/)

### 03-部署与自托管

- [Coolify vs Dokploy](content/post/软件试用/03-部署与自托管/Coolify%20vs%20Dokploy/)
- [alist](content/post/软件试用/03-部署与自托管/alist/)
- [github项目newsnow部署](content/post/软件试用/03-部署与自托管/github项目newsnow部署/)
- [polar-DB](content/post/软件试用/03-部署与自托管/polar-DB/)
- [网页内容变化监控项目](content/post/软件试用/03-部署与自托管/网页内容变化监控项目/)

### 04-文档与标注

- [数据集标注工具](content/post/软件试用/04-文档与标注/LabelStudio-tutorial/)
- [Sphinx-快速生成python项目的api文档](content/post/软件试用/04-文档与标注/Sphinx-快速生成python项目的api文档/)
- [生成api文档工具的简易使用](content/post/软件试用/04-文档与标注/api文档的写作/)

### 05-桌面效率工具

- [IObit Unlocker解除文件占用](content/post/软件试用/05-桌面效率工具/IObit%20Unlocker解除文件占用/)
- [内网文件传输工具LocalSend](content/post/软件试用/05-桌面效率工具/内网文件传输工具LocalSend/)
- [实用软件工具｜好用软件推荐](content/post/软件试用/05-桌面效率工具/实用软件工具/)

## 运维与服务器 (27)

### 01-服务器与系统

- [1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务](content/post/运维与服务器/01-服务器与系统/1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务/)
- [SSH使用教程](content/post/运维与服务器/01-服务器与系统/SSH常用命令/)
- [Server Probe](content/post/运维与服务器/01-服务器与系统/Server%20Probe/)
- [bash命令使用教程](content/post/运维与服务器/01-服务器与系统/bash命令使用教程/)
- [linux使用教程](content/post/运维与服务器/01-服务器与系统/linux服务器初始化配置教程/)
- [server_ops](content/post/运维与服务器/01-服务器与系统/server_ops/)
- [服务器安全-server Security](content/post/运维与服务器/01-服务器与系统/服务器安全-server%20Security/)
- [服务器磁盘管理基础](content/post/运维与服务器/01-服务器与系统/服务器磁盘管理基础/)
- [腾讯云修改为root登录](content/post/运维与服务器/01-服务器与系统/腾讯云修改root登录/)
- [阿里云服务器](content/post/运维与服务器/01-服务器与系统/阿里云服务器/)

### 02-网络与代理

- [rustdesk安装使用](content/post/运维与服务器/02-网络与代理/rustdesk安装使用/)
- [代理配置与环境变量实战](content/post/运维与服务器/02-网络与代理/代理配置实战/)
- [clash 教程](content/post/运维与服务器/02-网络与代理/修改clash中的配置信息/)
- [国外服务器扶墙](content/post/运维与服务器/02-网络与代理/国外服务器扶墙/)
- [服务器爬墙](content/post/运维与服务器/02-网络与代理/服务器爬墙/)

### 03-网关与站点

- [Nginx](content/post/运维与服务器/03-网关与站点/nginx使用/)
- [traefik](content/post/运维与服务器/03-网关与站点/traefik/)
- [域名迁移](content/post/运维与服务器/03-网关与站点/域名迁移/)

### 04-容器化部署

- [1panel使用教程｜云服务器使用教程](content/post/运维与服务器/04-容器化部署/1panel使用/)
- [CICD](content/post/运维与服务器/04-容器化部署/CICD/)
- [Coolify](content/post/运维与服务器/04-容器化部署/Coolify/)
- [Dokploy](content/post/运维与服务器/04-容器化部署/Dokploy/)

### 05-存储与数据库

- [Object Storage (对象存储服务)](content/post/运维与服务器/05-存储与数据库/Object%20Storage%20(对象存储服务)/)
- [PostgreSQL](content/post/运维与服务器/05-存储与数据库/PostgreSQL/)
- [S3 兼容存储踩坑记：boto3 新默认校验和撞上 NotImplemented](content/post/运维与服务器/05-存储与数据库/S3%20兼容存储踩坑记：boto3%20新默认校验和撞上%20NotImplemented/)
- [redis](content/post/运维与服务器/05-存储与数据库/redis/)
- [数据库备份实战](content/post/运维与服务器/05-存储与数据库/数据库备份实战/)

## 通识与生活 (16)

### 01-百科知识

- [shanghai-geographic](content/post/通识与生活/01-百科知识/shanghai-geographic/)
- [中国历史知识](content/post/通识与生活/01-百科知识/中国历史知识/)
- [中国各省市介绍](content/post/通识与生活/01-百科知识/中国各省市介绍/)
- [总-百科知识](content/post/通识与生活/01-百科知识/总-百科知识/)
- [文学与幽默知识积累](content/post/通识与生活/01-百科知识/文学与幽默知识积累/)
- [汽车-百科知识](content/post/通识与生活/01-百科知识/汽车-百科知识/)
- [茶叶-百科知识](content/post/通识与生活/01-百科知识/茶叶/)

### 02-英语学习

- [english如何学习](content/post/通识与生活/02-英语学习/english如何学习/)
- [英语语法知识点](content/post/通识与生活/02-英语学习/英语语法知识点/)

### 03-生活与个人

- [cookbook](content/post/通识与生活/03-生活与个人/cookbook/)
- [start_a_business](content/post/通识与生活/03-生活与个人/start-a-business/)
- [如何和别人尬聊，打破僵局？](content/post/通识与生活/03-生活与个人/如何和别人尬聊，打破僵局？/)
- [如何自学一个新领域？](content/post/通识与生活/03-生活与个人/如何自学一个领域？/)
- [徒步知识点](content/post/通识与生活/03-生活与个人/徒步知识点/)
- [生活中的方法](content/post/通识与生活/03-生活与个人/生活中的收获量化方法/)
- [给Zata的公司取一个名字](content/post/通识与生活/03-生活与个人/给Zata的公司取一个名字/)

## 阅读笔记 (3)

- [瑞金医院拉曼无创血糖论文](content/post/阅读笔记/RuijinHospitalandNearviewTechnologyLaunchRamanSpectroscopyforNon-InvasiveBloodGlucoseMonitoring_NatureMetabolism/)
- [《大语言模型》读书笔记（赵鑫）](content/post/阅读笔记/大语言模型-赵鑫/)
- [近红外光谱的知识点](content/post/阅读笔记/近红外光谱的知识点/)

## 面试八股 (6)

- [Langchain开发八股-常见问题](content/post/面试八股/Langchain开发八股-常见问题/)
- [深度学习八股-基础理论知识](content/post/面试八股/深度学习八股-基础理论知识/)
- [深度学习八股-实战经验](content/post/面试八股/深度学习八股-实战经验/)
- [深度学习八股-技术栈与工具](content/post/面试八股/深度学习八股-技术栈与工具/)
- [深度学习八股-量化](content/post/面试八股/深度学习八股-量化/)
- [深度学习八股-面试常见问题](content/post/面试八股/深度学习八股-面试常见问题/)

## 项目实战 (18)

### 01-爬虫实战

- [ai-crawler-深度调研报告：人工智能驱动的网络爬虫技术——能力、应用与生态演进](content/post/项目实战/01-爬虫实战/ai-crawler/)
- [crawler-tutorial](content/post/项目实战/01-爬虫实战/crawler-tutorial/)
- [crawler-爬虫ip代理商](content/post/项目实战/01-爬虫实战/crawler-爬虫ip代理商/)
- [一个自动签到的py并且使用github action每日执行](content/post/项目实战/01-爬虫实战/一个自动签到的py并且使用github%20action每日执行/)
- [爬虫-实战-多页面递归爬取](content/post/项目实战/01-爬虫实战/爬虫-实战-多页面递归爬取/)
- [爬虫-实战-爬取arXiv AI论文对应的url和title等](content/post/项目实战/01-爬虫实战/爬虫-实战-爬取arXiv%20AI论文对应的url和title等/)
- [爬虫-基础介绍](content/post/项目实战/01-爬虫实战/爬虫知识点/)

### 02-博客建站

- [1-hugo安装使用](content/post/项目实战/02-博客建站/1-hugo安装使用/)
- [2-Hugo主题和配置](content/post/项目实战/02-博客建站/2-hugo主题和配置/)
- [3-hugo博客集成Netlify CMS](content/post/项目实战/02-博客建站/3-hugo博客集成Netlify%20CMS/)
- [4-自定义Python函数创建博客：告别繁琐的文件头输入](content/post/项目实战/02-博客建站/4-自定义Python函数创建博客：告别繁琐的文件头输入/)
- [5-引入 Giscus 评论系统](content/post/项目实战/02-博客建站/5-引入%20Giscus%20评论系统/)
- [hugo使用过程中遇到的问题](content/post/项目实战/02-博客建站/hugo使用过程中遇到的问题/)
- [给hugo博客的页面增加一个自定义密码（防君子不防小人）](content/post/项目实战/02-博客建站/给页面增加一个自定义密码（防君子不防小人）/)

### 03-应用开发

- [Dify](content/post/项目实战/03-应用开发/Dify/)
- [软件自动更新](content/post/项目实战/03-应用开发/PythonGUI-软件自动更新/)
- [微信小程序使用教程——WechatMiniProgram](content/post/项目实战/03-应用开发/微信小程序使用教程/)
- [野火F103-MiNI使用教程](content/post/项目实战/03-应用开发/野火F103-MiNI使用教程/)
<!-- END:CONTENT-INDEX -->
