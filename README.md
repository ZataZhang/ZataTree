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
## Agent (41)

### Agent Orchestration

- [智能体编排设计工程师学习指南](content/post/Agent/Agent%20Orchestration/01-智能体编排设计工程师学习指南/)
- [Agent Runtime 详解：从模型循环到可恢复的企业执行系统](content/post/Agent/Agent%20Orchestration/20260922101724_Agent%20Runtime详解/)
- [AI Agent Loop 工程：原理、模式与实现](content/post/Agent/Agent%20Orchestration/AI%20Agent%20Loop%20工程：原理、模式与实现/)
- [Agent 沙箱选型指南：隔离边界、产品对比与判断标准](content/post/Agent/Agent%20Orchestration/Agent%20沙箱选型指南：隔离边界、产品对比与判断标准/)
- [Agent 用户记忆与 Skill 沉淀：开源项目参考与架构设计](content/post/Agent/Agent%20Orchestration/Agent%20用户记忆与%20Skill%20沉淀：开源项目参考与架构设计/)
- [E2B 迁到阿里云云沙箱：能跑通，但别急着上生产](content/post/Agent/Agent%20Orchestration/E2B%20迁到阿里云云沙箱：能跑通，但别急着上生产/)
- [Gliding Horse Agent OS 介绍：Rust 构建的工业级 AI Agent 操作系统](content/post/Agent/Agent%20Orchestration/Gliding%20Horse%20Agent%20OS%20介绍/)
- [主流 Agent 框架对比与多框架统一接口设计](content/post/Agent/Agent%20Orchestration/主流%20Agent%20框架对比与多框架统一接口设计/)
- [内置 Agent 放哪：一个 is_runnable 陷阱与三类事实源](content/post/Agent/Agent%20Orchestration/内置%20Agent%20放哪：一个%20is_runnable%20陷阱与三类事实源/)
- [Agent 记忆模块深度技术文档](content/post/Agent/Agent%20Orchestration/记忆模块技术文档/)

### Agent 工程实战

- [Agent Run 流式协议：事件溯源、SSE 投影与断线恢复](content/post/Agent/Agent%20工程实战/Agent%20Run%20流式协议：事件溯源、SSE%20投影与断线恢复/)
- [Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点](content/post/Agent/Agent%20工程实战/Agent%20Tracing%20基础：Trace、Span%20与%20OpenTelemetry%20埋点/)
- [Agent 内容输出规范：本地给路径，远程给协议](content/post/Agent/Agent%20工程实战/Agent%20内容输出规范：本地给路径，远程给协议/)
- [Agent 决策审计：它与 Tracing 的关系](content/post/Agent/Agent%20工程实战/Agent%20决策审计：它与%20Tracing%20的关系/)
- [Agent 埋点接 ARMS：上报返回 success，控制台却是空的](content/post/Agent/Agent%20工程实战/Agent%20埋点接%20ARMS：上报返回%20success，控制台却是空的/)
- [Agent 工具没调用，先查模型到底能看见什么](content/post/Agent/Agent%20工程实战/Agent%20工具没调用：一次真实链路验收的三层误判/)
- [Agent 工程实战开篇：从 Demo 到生产还有多远](content/post/Agent/Agent%20工程实战/Agent%20工程实战开篇：从%20Demo%20到生产还有多远/)
- [OpenAI Responses API与Chat Completions API区别详解](content/post/Agent/Agent%20工程实战/OpenAI%20Responses%20API与Chat%20Completions%20API区别详解/)
- [数据库初始化与迁移：从创建那一刻就要钉死的三件事](content/post/Agent/Agent%20工程实战/数据库初始化与迁移：从创建那一刻就要钉死的三件事/)
- [给 Agent 接入 Web Search：四种做法，和一条我试过之后放弃的路](content/post/Agent/Agent%20工程实战/给%20Agent%20接入%20Web%20Search：四种做法，和一条我试过之后放弃的路/)
- [让用户选择指定 Skill：从社区实践到生产级 API 设计](content/post/Agent/Agent%20工程实战/让用户选择指定%20Skill：从社区实践到生产级%20API%20设计/)
- [阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍](content/post/Agent/Agent%20工程实战/阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍/)

### Agent开发中遇到的问题

- [ai返回数据的格式不稳定，存在解析错误的问题](content/post/Agent/Agent开发中遇到的问题/ai返回数据的格式不稳定，存在解析错误的问题/)

### Agent流式协议

- [AG-UI：当 Agent 学会了和前端说话](content/post/Agent/Agent流式协议/AG-UI：当Agent学会了和前端说话/)

### ComputerUse

- [Cua 框架详解：给任何 Agent 一台可操控的电脑](content/post/Agent/ComputerUse/Cua%20框架详解：给任何%20Agent%20一台可操控的电脑/)

- [Graph RAG 开源项目全景：从微软 GraphRAG 到 LightRAG](content/post/Agent/GraphRAG开源项目全景：从微软GraphRAG到LightRAG/)

### LangChain

- [DeepAgents完全指南](content/post/Agent/LangChain/DeepAgents完全指南/)
- [Langchain-RAG实战教程](content/post/Agent/LangChain/LangChain-RAG实战教程/)
- [LangChain 与 MCP 极简教程：让 Agent 接入外部工具的另一种方式](content/post/Agent/LangChain/LangChain与MCP极简教程/)
- [LangChain 常见报错与排查指南](content/post/Agent/LangChain/LangChain常见报错与排查/)
- [LangChain 模型接入指南：OpenAI 兼容协议与多平台调用](content/post/Agent/LangChain/LangChain模型接入指南/)
- [LangGraph 实战：StateGraph、手写 ReAct 循环与 Map-Reduce 摘要](content/post/Agent/LangChain/LangGraph实战教程/)
- [LangSmith使用教程](content/post/Agent/LangChain/LangSmith使用教程/)
- [langchain_core 组件详解：Prompt 模板与 Output Parsers](content/post/Agent/LangChain/langchain_core组件详解/)
- [一个订阅更新摘要 Agent 的完整实践：从提示词踩坑到长文本分块](content/post/Agent/LangChain/订阅摘要Agent实战/)

### RAG

- [RAG入门：从问题定义到系统设计](content/post/Agent/RAG/01-RAG入门：从问题定义到系统设计/)
- [RAG进阶：Chunking、召回、Hybrid Search 与 Rerank](content/post/Agent/RAG/02-RAG进阶：Chunking、召回、Hybrid%20Search%20与%20Rerank/)
- [RAG评测与 Inspect：如何知道问题出在检索、重排还是生成](content/post/Agent/RAG/03-RAG评测与%20Inspect：如何知道问题出在检索、重排还是生成/)
- [RAG生产实践：常见坑、性能优化与迭代路线图](content/post/Agent/RAG/04-RAG生产实践：常见坑、性能优化与迭代路线图/)

- [RAGFlow 深度解析：为什么它是最值得关注的 RAG 开源项目](content/post/Agent/RAGFlow深度解析：为什么它是最值得关注的RAG开源项目/)
- [RAG 技术全景：从入门到进阶](content/post/Agent/RAG技术全景：从入门到进阶/)

## Book (1)

### 读书笔记

- [《大语言模型》读书笔记（赵鑫）](content/post/Book/读书笔记/大语言模型-赵鑫/)

## DeepLearning (19)

### NLP

- [LLM微调：qwen2_chat模型部署和微调](content/post/DeepLearning/NLP/LLM微调：qwen2_chat模型部署和微调/)
- [命名实体识别](content/post/DeepLearning/NLP/命名实体识别/)
- [文本分类](content/post/DeepLearning/NLP/文本分类/)

### agent

- [n8n](content/post/DeepLearning/agent/n8n/)
- [nl2sql](content/post/DeepLearning/agent/nl2sql/)
- [openclaw](content/post/DeepLearning/agent/openclaw/)
- [vector-database](content/post/DeepLearning/agent/vector-database/)

### frame

- [深度学习开源框架](content/post/DeepLearning/frame/DeepSpeed/)
- [vllm](content/post/DeepLearning/frame/vllm/)

### models_and_strategies

- [Alignment-DPOvsPPOvsGRPO](content/post/DeepLearning/models_and_strategies/Alignment-DPOvsPPOvsGRPO/)
- [DeepSeek_NSA](content/post/DeepLearning/models_and_strategies/Deepseek_NSA/)
- [ICL-上下文学习](content/post/DeepLearning/models_and_strategies/ICL-上下文学习/)
- [Jev：不写字的决策模型，和它真正适合解决的问题](content/post/DeepLearning/models_and_strategies/Jev：不写字的决策模型，和它真正适合解决的问题/)
- [MoE](content/post/DeepLearning/models_and_strategies/MoE/)
- [RLHF](content/post/DeepLearning/models_and_strategies/RLHF/)
- [Attention](content/post/DeepLearning/models_and_strategies/attention注意力机制/)
- [mechine_learning_models](content/post/DeepLearning/models_and_strategies/mechine_learning_models/)
- [增量学习研究综述：理论、方法、应用与未来展望](content/post/DeepLearning/models_and_strategies/增量学习研究综述：理论、方法、应用与未来展望/)
- [大模型结构原理与代码实现](content/post/DeepLearning/models_and_strategies/模型-transformer原理和代码实现/)

## Design (12)

### 值得学习的图

- [作图参考](content/post/Design/值得学习的图/作图参考/)
- [漂亮的reademe文件使用教程](content/post/Design/值得学习的图/漂亮的reademe文件使用教程/)

### 功能图

- [数据流图](content/post/Design/功能图/数据流图/)

### 原型图

- [使用ai工具绘制原型图html并导入figma](content/post/Design/原型图/使用ai工具绘制原型图html并导入figma/)

### 结构图

- [类图](content/post/Design/结构图/类图/)

### 行为图

- [用例图](content/post/Design/行为图/用例图/)

### 软件架构设计

- [从脚本到企业级平台：AI Agent 系统"整洁架构"演进与 Python 落地指南](content/post/Design/软件架构设计/AI-Agent四层模块化单体架构/)
- [FastAPI 后端架构设计](content/post/Design/软件架构设计/FastAPI后端架构设计/)
- [一个标准的软件项目结构](content/post/Design/软件架构设计/一个标准的软件项目结构/)
- [简洁架构（Clean Architecture）：让业务逻辑永远不依赖框架](content/post/Design/软件架构设计/简洁架构-Clean-Architecture/)
- [软件架构设计-培养软件架构师的思维](content/post/Design/软件架构设计/软件架构设计-培养软件架构师的思维/)
- [领域驱动设计（DDD）分层架构：用领域语言构建复杂系统](content/post/Design/软件架构设计/领域驱动设计分层架构-DDD/)

## Engineering (7)

### DevOps

- [Docker 和 Traefik 一键安装脚本](content/post/Engineering/DevOps/Docker-Traefik一键安装脚本/)
- [Woodpecker CI 使用教程](content/post/Engineering/DevOps/Woodpecker-CI使用教程/)

### platform-architecture

- [企业AI工具平台架构设计：拥抱快速变化的AI生态](content/post/Engineering/platform-architecture/ai-platform-architecture/)

### 可观测性

- [LogQL 查询语言详解：先选流，再过滤，最后才解析](content/post/Engineering/可观测性/LogQL查询语言详解/)
- [云原生可观测性：从"监控"到"洞察"的进化之路](content/post/Engineering/可观测性/云原生可观测性-从监控到洞察的进化之路/)
- [项目中日志的使用教程](content/post/Engineering/可观测性/项目中日志的使用教程/)

### 软件工程

- [软件项目开发流程使用教程](content/post/Engineering/软件工程/软件项目开发流程/)

## Grammar (18)

### Matlab

- [Matlab-基本语法](content/post/Grammar/Matlab/Matlab-基本语法/)

### PyQt

- [PyQt-入门教程（AI生成）](content/post/Grammar/PyQt/PyQt-入门教程/)
- [PyQt-设备像素设置](content/post/Grammar/PyQt/PyQt-设备像素设置/)

### general

- [生活中的方法](content/post/Grammar/general/生活中的收获量化方法/)
- [通用模板规范GeneralTemplateSpecifications](content/post/Grammar/general/通用模板规范GeneralTemplateSpecifications/)

### python

- [Python-Docstring 的详细教程](content/post/Grammar/python/python-Docstring%20的详细教程/)
- [【python】__init__.py为什么要写](content/post/Grammar/python/python-__init__.py为什么要写/)
- [python-logging模块添加日志](content/post/Grammar/python/python-logging模块添加日志/)
- [python-lru_cache 缓存装饰器](content/post/Grammar/python/python-lru_cache%20缓存装饰器/)
- [python-staticmethod 修饰符](content/post/Grammar/python/python-staticmethod%20修饰符/)
- [python-typing提高代码可读性](content/post/Grammar/python/python-typing提高代码可读性/)
- [python-在项目中应该如何定义文件路径](content/post/Grammar/python/python-在项目中应该如何定义文件路径/)
- [python-将py文件编译为pyc文件并运行](content/post/Grammar/python/python-将py文件编译为pyc文件并运行/)
- [python-应如何定义包通用的变量-推荐config.py](content/post/Grammar/python/python-应如何定义包通用的变量-推荐config.py/)
- [python-数据类](content/post/Grammar/python/python-数据类/)
- [python-相对导入错误attempted relative import with no known parent package](content/post/Grammar/python/python-相对导入错误attempted%20relative%20import%20with%20no%20known%20parent%20package/)
- [python-类-类变量和实例变量](content/post/Grammar/python/python-类/)
- [python使用教程-难点和遇到的问题](content/post/Grammar/python/python-难点和遇到的问题/)

## Knowledge (67)

### English

- [english如何学习](content/post/Knowledge/English/english如何学习/)
- [英语语法知识点](content/post/Knowledge/English/英语语法知识点/)

### Linux

- [1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务](content/post/Knowledge/Linux/1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务/)
- [bash命令使用教程](content/post/Knowledge/Linux/bash命令使用教程/)
- [linux使用教程](content/post/Knowledge/Linux/linux服务器初始化配置教程/)
- [国外服务器扶墙](content/post/Knowledge/Linux/国外服务器扶墙/)

### encyclopedic

- [中国历史知识](content/post/Knowledge/encyclopedic/中国历史知识/)
- [中国各省市介绍](content/post/Knowledge/encyclopedic/中国各省市介绍/)
- [总-百科知识](content/post/Knowledge/encyclopedic/总-百科知识/)
- [文学与幽默知识积累](content/post/Knowledge/encyclopedic/文学与幽默知识积累/)
- [汽车-百科知识](content/post/Knowledge/encyclopedic/汽车-百科知识/)
- [茶叶-百科知识](content/post/Knowledge/encyclopedic/茶叶/)

### geographic

- [shanghai-geographic](content/post/Knowledge/geographic/shanghai-geographic/)

### markdown

- [Markdown中常用的图标或徽章](content/post/Knowledge/markdown/Markdown中常用的图标或徽章/)
- [markdown使用技巧](content/post/Knowledge/markdown/markdown使用技巧/)

### news

- [❤️每日思考和AI资讯](content/post/Knowledge/news/资讯和思考/)

### others

- [1panel使用教程｜云服务器使用教程](content/post/Knowledge/others/1panel使用/)
- [AI agent介绍：基于大模型的人工智能代理](content/post/Knowledge/others/AI%20agent介绍：基于大模型的人工智能代理/)
- [Building asynchronous APIs for handling long-term tasks and dynamic resources](content/post/Knowledge/others/Building%20asynchronous%20APIs%20for%20handling%20long-term%20tasks%20and%20dynamic%20resources/)
- [Celery](content/post/Knowledge/others/Celery/)
- [Coolify](content/post/Knowledge/others/Coolify/)
- [JAX](content/post/Knowledge/others/JAX/)
- [Jinja是什么？可以用在做什么？](content/post/Knowledge/others/Jinja是什么？可以用在做什么？/)
- [Server Probe](content/post/Knowledge/others/Server%20Probe/)
- [Useful but not attempted](content/post/Knowledge/others/Useful%20but%20not%20attempted/)
- [“categories”（类别）和“tags”（标签）的区别](content/post/Knowledge/others/categories和tags的区别/)
- [conda使用教程|pip使用教程|依赖安装_使用教程](content/post/Knowledge/others/conda使用相关/)
- [cookbook](content/post/Knowledge/others/cookbook/)
- [copier-using](content/post/Knowledge/others/copier-using/)
- [mac os使用经验](content/post/Knowledge/others/macos使用经验/)
- [openbayes算力平台使用教程](content/post/Knowledge/others/openbayes算力平台使用教程/)
- [python中将函数设置为定时任务](content/post/Knowledge/others/python中将函数设置为定时任务/)
- [python的命名规范](content/post/Knowledge/others/python的命名规范/)
- [rustdesk安装使用](content/post/Knowledge/others/rustdesk安装使用/)
- [start_a_business](content/post/Knowledge/others/start-a-business/)
- [streamlit使用教程](content/post/Knowledge/others/streamlit使用教程/)
- [vllm使用教程](content/post/Knowledge/others/vllm实战教程/)
- [一个软件项目的文件目录应该怎么定义](content/post/Knowledge/others/一个软件项目的文件目录应该怎么定义/)
- [什么是算子？](content/post/Knowledge/others/什么是算子？/)
- [代码写作心得-使用教程](content/post/Knowledge/others/代码写作心得-使用教程/)
- [clash 教程](content/post/Knowledge/others/修改clash中的配置信息/)
- [全量解码与增量解码：原理、区别以及应用](content/post/Knowledge/others/全量解码与增量解码：原理、区别以及应用/)
- [包管理工具poetry使用教程](content/post/Knowledge/others/包管理工具poetry使用教程/)
- [在overleaf中为什么两个完全一样的代码一个不能显示图片](content/post/Knowledge/others/在overleaf中为什么两个完全一样的代码一个不能显示图片/)
- [如何和别人尬聊，打破僵局？](content/post/Knowledge/others/如何和别人尬聊，打破僵局？/)
- [如何提成所写文档和ppt的颜值](content/post/Knowledge/others/如何提成所写文档和ppt的颜值/)
- [如何自学一个新领域？](content/post/Knowledge/others/如何自学一个领域？/)
- [字典学习（Dictionary Learning）](content/post/Knowledge/others/字典学习（Dictionary%20Learning）/)
- [对比了几种大模型在相同任务下的表现](content/post/Knowledge/others/对比了几种大模型在相同任务下的表现/)
- [徒步知识点](content/post/Knowledge/others/徒步知识点/)
- [怎么保存.env文件到github公开的仓库](content/post/Knowledge/others/怎么保存.env文件到github公开的仓库/)
- 技术追踪
    - [技术热点追踪](content/post/Knowledge/others/技术追踪/技术热点追踪/)
    - [文档结构化实战：从 Markdown/PDF 到 Word](content/post/Knowledge/others/技术追踪/文档结构化实战/)
- [相同LLM不同提示词的对比](content/post/Knowledge/others/相同LLM不同提示词的对比/)
- [给Zata的公司取一个名字](content/post/Knowledge/others/给Zata的公司取一个名字/)
- [近红外光谱的知识点](content/post/Knowledge/others/近红外光谱的知识点/)

### windows

- [关闭win11更新](content/post/Knowledge/windows/关闭win11更新/)

### word技巧

- [word-封面-你文档的门面](content/post/Knowledge/word技巧/word-封面-你文档的门面/)
- [word技巧-排版和布局](content/post/Knowledge/word技巧/word技巧-排版和布局/)

### 科技月报：机器人又抢饭碗啦

- [科技月报-2025](content/post/Knowledge/科技月报：机器人又抢饭碗啦/科技月报-2025/)
- [科技月报-2026](content/post/Knowledge/科技月报：机器人又抢饭碗啦/科技月报-2026/)

### 面试八股

- [Langchain开发八股-常见问题](content/post/Knowledge/面试八股/Langchain开发八股-常见问题/)
- [深度学习八股-基础理论知识](content/post/Knowledge/面试八股/深度学习八股-基础理论知识/)
- [深度学习八股-实战经验](content/post/Knowledge/面试八股/深度学习八股-实战经验/)
- [深度学习八股-技术栈与工具](content/post/Knowledge/面试八股/深度学习八股-技术栈与工具/)
- [深度学习八股-量化](content/post/Knowledge/面试八股/深度学习八股-量化/)
- [深度学习八股-面试常见问题](content/post/Knowledge/面试八股/深度学习八股-面试常见问题/)

## Library (36)

### FastAPI

- [ALL-fastapi](content/post/Library/FastAPI/fastapi-ALL/)
- [fastapi-docs_swagger_UI-openAPI](content/post/Library/FastAPI/fastapi-docs_swagger_UI/)
- [fastapi-前提知识](content/post/Library/FastAPI/fastapi-前提知识/)
- [fastapi使用教程](content/post/Library/FastAPI/fastapi-第一个简单示例/)
- [jwt-with-fastapi](content/post/Library/FastAPI/jwt-with-fastapi/)
- [注入依赖进一步解释](content/post/Library/FastAPI/注入依赖进一步解释/)

### Flask

- [Flask使用教程](content/post/Library/Flask/Flask使用/)
- [flask-构建一个简单的文件同步系统](content/post/Library/Flask/flask-构建一个简单的文件同步系统/)

### Python_Lib

- [PyYAML](content/post/Library/Python_Lib/PyYAML/)
- [Typer + Rich 入门教程](content/post/Library/Python_Lib/Typer和Rich入门教程/)
- [FASTAPI使用相关问题](content/post/Library/Python_Lib/fastapi使用/)
- [gradio教程](content/post/Library/Python_Lib/gradio/)
- [numpy使用教程](content/post/Library/Python_Lib/numpy使用教程/)
- [pickle](content/post/Library/Python_Lib/pickle/)
- [pytest测试用例使用教程](content/post/Library/Python_Lib/pytest/)
- [python开发环境配置指南](content/post/Library/Python_Lib/python开发环境配置指南/)
- [scipy](content/post/Library/Python_Lib/scipy/)
- [sklearn使用教程](content/post/Library/Python_Lib/sklearn使用教程/)
- [tableprint使用教程](content/post/Library/Python_Lib/tableprint使用教程/)
- [toml_usage_tutorial](content/post/Library/Python_Lib/toml_usage使用教程/)

### React

- [React框架使用教程](content/post/Library/React/React框架使用教程/)

### flutter

- [flutter_tutorial](content/post/Library/flutter/flutter_tutorial/)

### matplotlib

- [matplotlib教程-zata——v0.0.0](content/post/Library/matplotlib/matplotlib使用教程_Zata_v0.0.0/)

### pandas

- [pandas使用教程](content/post/Library/pandas/pandas使用教程/)

### pyserial

- [pyserial-使用教程](content/post/Library/pyserial/pyserial-Python%20中最常用的串口通信库快速入门/)

### setuptools

- [setuptools-打包python项目为egg / 安装库函数](content/post/Library/setuptools/setuptools-打包python项目为egg/)

### smallLibrary

- [onnx使用教程](content/post/Library/smallLibrary/onnx使用教程/)
- [pydantic使用教程](content/post/Library/smallLibrary/pydantic使用教程/)

### torch

- [torch使用教程-zata——v0.0.0](content/post/Library/torch/torch使用教程_Zata_v0.0.0/)

### transformers

- [datasets](content/post/Library/transformers/datasets/)
- [evaluate](content/post/Library/transformers/evaluate/)
- [model](content/post/Library/transformers/model/)
- [pipeline](content/post/Library/transformers/pipeline/)
- [tokenizer](content/post/Library/transformers/tokenizer/)
- [trainer](content/post/Library/transformers/trainer/)

### 优秀图表学习

- [分类图](content/post/Library/优秀图表学习/分类图/)

## PaperReading (1)

- [瑞金医院拉曼无创血糖论文](content/post/PaperReading/RuijinHospitalandNearviewTechnologyLaunchRamanSpectroscopyforNon-InvasiveBloodGlucoseMonitoring_NatureMetabolism/)

## Platforms_Tools (38)

### Blender

- [Blender 详解：奥斯卡和 AI Agent 为什么都选了它](content/post/Platforms_Tools/Blender/blender-complete-guide/)

### CLI

- [Herdr 详解：给 AI Agent 用的终端运行时](content/post/Platforms_Tools/CLI/herdr-ai-agent-terminal-runtime/)
- [为 AI 而写的 CLI 设计指南：原则、避坑与难点](content/post/Platforms_Tools/CLI/为AI而写的CLI设计指南/)

### Docker

- [Docker Compose(dev\test\prod)](content/post/Platforms_Tools/Docker/Docker%20Compose(devtestprod)/)
- [Docker Swarm 实战（一）：核心概念与集群管理](content/post/Platforms_Tools/Docker/Docker%20Swarm%20实战/)
- [Docker Swarm 实战（二）：Traefik 反向代理部署](content/post/Platforms_Tools/Docker/Docker%20Swarm%20实战%20-%20Traefik%20反向代理部署/)
- [Docker 私有镜像仓库registry](content/post/Platforms_Tools/Docker/Docker%20私有仓库/)
- [Docker使用实战-compose教程](content/post/Platforms_Tools/Docker/Docker使用实战-compose教程/)
- [build x86 image in ARM MAC platform and devolopmet to remote server](content/post/Platforms_Tools/Docker/build%20x86%20image%20in%20ARM%20MAC%20platform%20and%20devolopmet%20to%20remote%20server/)
- [docker-ubuntu容器中安装miniconda问题合集](content/post/Platforms_Tools/Docker/docker-ubuntu容器中安装miniconda问题合集/)
- [docker使用教程](content/post/Platforms_Tools/Docker/docker容器相关命令/)

### PyInstaller

- [PyInstaller使用教程](content/post/Platforms_Tools/PyInstaller/PyInstaller-简易教程/)
- [Pyinstaller-打包gradio项目](content/post/Platforms_Tools/PyInstaller/Pyinstaller-打包gradio项目/)

### PyStand

- [PyStand-简易教程](content/post/Platforms_Tools/PyStand/PyStand-简易教程/)

### S3

- [S3 兼容存储踩坑记：boto3 新默认校验和撞上 NotImplemented](content/post/Platforms_Tools/S3/S3%20兼容存储踩坑记：boto3%20新默认校验和撞上%20NotImplemented/)

### Server Operations and Maintenance-服务器运维

- [CICD](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/CICD/)
- [Dokploy](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/Dokploy/)
- [Object Storage (对象存储服务)](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/Object%20Storage%20(对象存储服务)/)
- [server_ops](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/server_ops/)
- [traefik](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/traefik/)
- [代理配置与环境变量实战](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/代理配置实战/)
- [域名迁移](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/域名迁移/)
- [服务器安全-server Security](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/服务器安全-server%20Security/)
- [服务器爬墙](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/服务器爬墙/)
- [服务器磁盘管理基础](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/服务器磁盘管理基础/)
- [阿里云服务器](content/post/Platforms_Tools/Server%20Operations%20and%20Maintenance-服务器运维/阿里云服务器/)

### dev_tools

- [用 AI 把文章做成口播视频：三条路线、工具盘点与落地管线](content/post/Platforms_Tools/dev_tools/ai-article-to-video/)
- [AI 生成前端的 E2E 实践：用 Playwright 做视觉回归和功能兜底](content/post/Platforms_Tools/dev_tools/ai-frontend-e2e/)
- [浏览器会话录制与接口回放：方案调研](content/post/Platforms_Tools/dev_tools/browser-session-replay/)
- [CC Switch 详解：一个应用管住八个 AI 编程 CLI](content/post/Platforms_Tools/dev_tools/cc-switch-guide/)
- [扩展式 RPA：从 Chrome 扩展原理到 Playwright 实战方案](content/post/Platforms_Tools/dev_tools/extension-rpa/)
- [从 noVNC 到 Playwright 截图流：容器内 VNC 踩坑记](content/post/Platforms_Tools/dev_tools/novnc-playwright/)
- [Playwright 使用实践与本地浏览器 Profile 避坑](content/post/Platforms_Tools/dev_tools/playwright-profile/)
- [Playwright Chromium 在 Docker 内 SIGTRAP 启动崩溃排查实录](content/post/Platforms_Tools/dev_tools/playwright-sigtrap/)

### packageTools

- [npm使用教程](content/post/Platforms_Tools/packageTools/npm使用教程/)

### pipx

- [pipx使用教程](content/post/Platforms_Tools/pipx/pipx使用教程/)

- [Refine: 当 API 即界面，CRUD 不再是体力活](content/post/Platforms_Tools/refine-meta-framework/)

### uv

- [包管理工具uv使用教程](content/post/Platforms_Tools/uv/包管理工具uv使用教程/)

## Project_Application (64)

- [Dify](content/post/Project_Application/Dify/)

### PythonGUI

- [python程序打包exe使用教程](content/post/Project_Application/PythonGUI/PythonGUI-打包成exe/)
- [软件自动更新](content/post/Project_Application/PythonGUI/PythonGUI-软件自动更新/)

### SQL

- [Alembic](content/post/Project_Application/SQL/Alembic/)
- [PostgreSQL](content/post/Project_Application/SQL/PostgreSQL/)
- [SQLAlchemy简单入门](content/post/Project_Application/SQL/SQLAlchemy简单入门/)
- [redis](content/post/Project_Application/SQL/redis/)
- [数据库备份实战](content/post/Project_Application/SQL/数据库备份实战/)

### SSH

- [SSH使用教程](content/post/Project_Application/SSH/SSH常用命令/)

### SoftTrial

- [Coolify vs Dokploy](content/post/Project_Application/SoftTrial/Coolify%20vs%20Dokploy/)
- [IObit Unlocker解除文件占用](content/post/Project_Application/SoftTrial/IObit%20Unlocker解除文件占用/)
- [alist](content/post/Project_Application/SoftTrial/alist/)
- [cc-switch](content/post/Project_Application/SoftTrial/cc-switch/)
- [ccNexus](content/post/Project_Application/SoftTrial/ccNexus/)
- [claude-code&codex&Gemini-cli](content/post/Project_Application/SoftTrial/claude-code/)
- [coze](content/post/Project_Application/SoftTrial/coze/)
- [everything-claude-code](content/post/Project_Application/SoftTrial/everything-claude-code/)
- [flora无限画布](content/post/Project_Application/SoftTrial/flora无限画布/)
- [homebrew](content/post/Project_Application/SoftTrial/homebrew/)
- [nvm](content/post/Project_Application/SoftTrial/nvm/)
- [polar-DB](content/post/Project_Application/SoftTrial/polar-DB/)
- [wrap.dev](content/post/Project_Application/SoftTrial/wrap.dev/)
- [wsl使用教程](content/post/Project_Application/SoftTrial/wsl使用教程/)
- [内网文件传输工具LocalSend](content/post/Project_Application/SoftTrial/内网文件传输工具LocalSend/)
- [百度自由画布](content/post/Project_Application/SoftTrial/百度自由画布/)
- [网页内容变化监控项目](content/post/Project_Application/SoftTrial/网页内容变化监控项目/)

### SoftUseExp

- [软件工程的范式转移：基于 Claude Code 与智能体协作的高效编程实践](content/post/Project_Application/SoftUseExp/Efficient%20Programming%20Based%20on%20Claude%20Code%20Collaboration%20with%20Intelligent%20Agents/)
- [数据集标注工具](content/post/Project_Application/SoftUseExp/LabelStudio-tutorial/)
- [Sphinx-快速生成python项目的api文档](content/post/Project_Application/SoftUseExp/Sphinx-快速生成python项目的api文档/)
- [Tavily-搜索引擎api](content/post/Project_Application/SoftUseExp/Tavily/)
- [生成api文档工具的简易使用](content/post/Project_Application/SoftUseExp/api文档的写作/)
- [cherry-studio](content/post/Project_Application/SoftUseExp/cherry-studio/)
- [cursor使用教程](content/post/Project_Application/SoftUseExp/cursor使用教程/)
- [github项目newsnow部署](content/post/Project_Application/SoftUseExp/github项目newsnow部署/)
- [postman](content/post/Project_Application/SoftUseExp/postman/)
- [tmux简易使用](content/post/Project_Application/SoftUseExp/tmux/)
- [多台电脑环境变量(.env)同步方案](content/post/Project_Application/SoftUseExp/多台电脑环境变量(.env)同步方案/)
- [实用软件工具｜好用软件推荐](content/post/Project_Application/SoftUseExp/实用软件工具/)
- [新电脑快速配置-scoop](content/post/Project_Application/SoftUseExp/新电脑快速配置-scoop-homebrew/)

### VScode

- [VScode使用教程|cursor使用教程](content/post/Project_Application/VScode/VScode安装和配置/)

### crawler

- [ai-crawler-深度调研报告：人工智能驱动的网络爬虫技术——能力、应用与生态演进](content/post/Project_Application/crawler/ai-crawler/)
- [crawler-tutorial](content/post/Project_Application/crawler/crawler-tutorial/)
- [crawler-爬虫ip代理商](content/post/Project_Application/crawler/crawler-爬虫ip代理商/)
- [一个自动签到的py并且使用github action每日执行](content/post/Project_Application/crawler/一个自动签到的py并且使用github%20action每日执行/)
- [爬虫-实战-多页面递归爬取](content/post/Project_Application/crawler/爬虫-实战-多页面递归爬取/)
- [爬虫-实战-爬取arXiv AI论文对应的url和title等](content/post/Project_Application/crawler/爬虫-实战-爬取arXiv%20AI论文对应的url和title等/)
- [爬虫-基础介绍](content/post/Project_Application/crawler/爬虫知识点/)

### git&github

- [Self-hosted Runner](content/post/Project_Application/git&github/Self-hosted%20Runner/)
- [gh使用教程](content/post/Project_Application/git&github/gh使用教程/)
- [git&github_tutorial](content/post/Project_Application/git&github/git&github使用/)
- [git-submodule-子模块](content/post/Project_Application/git&github/git-submodule-子模块/)
- [2-github action 使用](content/post/Project_Application/git&github/github%20action/)
- [github release](content/post/Project_Application/git&github/github%20release/)

### hugo

- [1-hugo安装使用](content/post/Project_Application/hugo/1-hugo安装使用/)
- [2-Hugo主题和配置](content/post/Project_Application/hugo/2-hugo主题和配置/)
- [3-hugo博客集成Netlify CMS](content/post/Project_Application/hugo/3-hugo博客集成Netlify%20CMS/)
- [4-自定义Python函数创建博客：告别繁琐的文件头输入](content/post/Project_Application/hugo/4-自定义Python函数创建博客：告别繁琐的文件头输入/)
- [5-引入 Giscus 评论系统](content/post/Project_Application/hugo/5-引入%20Giscus%20评论系统/)
- [hugo使用过程中遇到的问题](content/post/Project_Application/hugo/hugo使用过程中遇到的问题/)
- [给hugo博客的页面增加一个自定义密码（防君子不防小人）](content/post/Project_Application/hugo/给页面增加一个自定义密码（防君子不防小人）/)

- [Nginx](content/post/Project_Application/nginx使用/)

### wechatapplet

- [微信小程序使用教程——WechatMiniProgram](content/post/Project_Application/wechatapplet/微信小程序使用教程/)

### 单片机

- [野火F103-MiNI使用教程](content/post/Project_Application/单片机/野火F103-MiNI使用教程/)

- [腾讯云修改为root登录](content/post/Project_Application/腾讯云修改root登录/)

## Vibe-Coding (7)

### AI-Frontend

- [AI 前端调试技巧：把被遮挡翻译成尺寸约束](content/post/Vibe-Coding/AI-Frontend/AI%20前端调试技巧：把被遮挡翻译成尺寸约束/)
- [下拉框里显示 _all：Base UI 与 Radix Select 的一个行为差异](content/post/Vibe-Coding/AI-Frontend/Base%20UI%20Select%20显示%20_all%20的坑/)
- ai-design-research
    - [Design Engineer 到底是什么：从 Vercel 拆解到一个新角色](content/post/Vibe-Coding/AI-Frontend/ai-design-research/01-design-engineer是什么/)
    - [Figma MCP + Claude Code：从设计稿到上线的全过程](content/post/Vibe-Coding/AI-Frontend/ai-design-research/02-figma-mcp实战/)
    - [shadcn/ui + design token：LLM 原生设计系统实践](content/post/Vibe-Coding/AI-Frontend/ai-design-research/03-shadcn设计系统/)
    - [一份能直接抄的前端 `.mdc` rules 模板](content/post/Vibe-Coding/AI-Frontend/ai-design-research/04-mdc-rules模板/)
- [用 AI 打造惊艳前端：从 Vibe Coding 到实战的艺术指南](content/post/Vibe-Coding/AI-Frontend/art-of-ai-frontend-design/)
<!-- END:CONTENT-INDEX -->
