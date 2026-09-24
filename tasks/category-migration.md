# 分类细化 · 全量映射表（待确认）

> 生成于 2026-09-24 · `scripts/category_migration_map.py`（映射规则的唯一事实源，确认后迁移命令按它落地）
> 迁移 = git mv 目录 + 重写 front matter `categories`。permalink 是 `/p/:slug/`，由 slug 决定 —— 全程零链接变更。
> 约束：60 篇/本上限（最大一本 35 篇，无超限）。书名均为占位名，可整体改。
> ⚠️ = 待你拍板的条目，明细见「待拍板清单」。
> 章节：一篇 = 一书 = 恰好一章（tag 由自由关键词改为章节，不跨书不跨章）。章节顺序即建议阅读顺序，章内顺序迁移后用 weight 定稿。

## 总览

| # | 书 | 篇数 | 章节 | 主要来源 |
|---|---|---|---|---|
| 1 | Agent 工程 | 35 | 6 章 | Agent 的工程实战+Orchestration+散篇；Knowledge 的 Agent 介绍/解码/提示词；DeepLearning/agent 的 n8n、nl2sql、openclaw |
| 2 | RAG 与 LangChain | 17 | 4 章 | Agent 的 LangChain 9 篇 + RAG 4 篇 + RAG 全景/RAGFlow/GraphRAG；向量数据库 |
| 3 | 深度学习 | 21 | 5 章 | DeepLearning 的 models/NLP/frame；Knowledge 的 JAX、字典学习、算子、vllm、模型对比、openbayes |
| 4 | 编程语言 | 29 | 5 章 | Grammar 的 python/PyQt/Matlab；Library 的 Python 库教程（pickle、pytest、PyYAML 等）；SQLAlchemy/Alembic |
| 5 | Web 开发 | 17 | 4 章 | Library 的 FastAPI/Flask/React/flutter；Knowledge 的 Jinja、Celery、streamlit、gradio、异步 API；Refine |
| 6 | 数据科学 | 13 | 3 章 | Library 的 transformers/torch/pandas/matplotlib；Python_Lib 的 numpy/scipy/sklearn；onnx |
| 7 | 构建与打包 | 10 | 2 章 | Platforms_Tools 的 PyInstaller/PyStand/pipx/uv/packageTools；setuptools、poetry、conda、打包 exe |
| 8 | 开发工具链 | 27 | 5 章 | Platforms_Tools 的 Docker/dev_tools/CLI；git&github、VScode、Blender、copier |
| 9 | 设计 | 14 | 3 章 | Design 全部（架构/类图/用例图/数据流图/原型图/作图）；Library/优秀图表学习；项目目录规范 |
| 10 | 工程实践 | 11 | 3 章 | Engineering 全部（可观测性/软件工程/DevOps/平台架构）；.env 安全、代码写作心得、模板规范 |
| 11 | 运维与服务器 | 27 | 5 章 | 服务器运维 11 篇、S3、Linux 4 篇、1panel/Coolify/rustdesk/Server Probe/clash、腾讯云/SSH/Nginx、PostgreSQL/redis/备份 |
| 12 | 项目实战 | 18 | 3 章 | crawler、hugo 建站 7 篇、单片机、Dify、软件自动更新、微信小程序 |
| 13 | 软件试用 | 30 | 5 章 | SoftTrial 17 + SoftUseExp 13（默认决策：独立成书） |
| 14 | 效率与文档 | 10 | 2 章 | markdown、word 技巧、windows/macos、overleaf、文档颜值、文档结构化、categories 概念 |
| 15 | 通识与生活 | 16 | 3 章 | 百科 6 篇、英语、上海地理、徒步、自学方法、尬聊、创业、菜谱、生活量化 |
| 16 | Vibe Coding | 7 | 2 章 | AI-Frontend 7 篇（含 ai-design-research 4 篇） |
| 17 | 面试八股 | 6 | 平铺 | 深度学习八股 5 篇 + LangChain 八股（默认决策：独立成书） |
| 18 | 阅读笔记 | 3 | 平铺 | 《大语言模型》读书笔记、瑞金拉曼血糖论文、近红外光谱知识点 |
| 19 | 科技月报 | 4 | 平铺 | 科技月报 2025/2026、每日资讯、技术热点追踪（专栏形态，按时间排，不排书序） |
| | **合计** | **315** | **60 章** | |

## 映射明细

### 1. Agent 工程 · 35 篇 · 6 章

**第 1 章 · 入门与全景**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Agent 工程实战开篇：从 Demo 到生产还有多远 | `Agent/Agent 工程实战/Agent 工程实战开篇：从 Demo 到生产还有多远` |  |
| Agent 生产工程全景手册：从 Runtime 到业务闭环 | `Agent/Agent 工程实战/Agent生产工程全景手册` |  |
| AI agent介绍：基于大模型的人工智能代理 | `Knowledge/others/AI agent介绍：基于大模型的人工智能代理` |  |

**第 2 章 · 框架与运行时**（8 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 智能体编排设计工程师学习指南 | `Agent/Agent Orchestration/01-智能体编排设计工程师学习指南` |  |
| Agent Runtime 详解：从模型循环到可恢复的企业执行系统 | `Agent/Agent Orchestration/20260922101724_Agent Runtime详解` |  |
| AI Agent Loop 工程：原理、模式与实现 | `Agent/Agent Orchestration/AI Agent Loop 工程：原理、模式与实现` |  |
| Agent 用户记忆与 Skill 沉淀：开源项目参考与架构设计 | `Agent/Agent Orchestration/Agent 用户记忆与 Skill 沉淀：开源项目参考与架构设计` |  |
| Gliding Horse Agent OS 介绍：Rust 构建的工业级 AI Agent 操作系统 | `Agent/Agent Orchestration/Gliding Horse Agent OS 介绍` |  |
| 主流 Agent 框架对比与多框架统一接口设计 | `Agent/Agent Orchestration/主流 Agent 框架对比与多框架统一接口设计` |  |
| 内置 Agent 放哪：一个 is_runnable 陷阱与三类事实源 | `Agent/Agent Orchestration/内置 Agent 放哪：一个 is_runnable 陷阱与三类事实源` |  |
| Agent 记忆模块深度技术文档 | `Agent/Agent Orchestration/记忆模块技术文档` |  |

**第 3 章 · 工程化实践**（10 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Agent 内容输出规范：本地给路径，远程给协议 | `Agent/Agent 工程实战/Agent 内容输出规范：本地给路径，远程给协议` |  |
| Agent 工具没调用，先查模型到底能看见什么 | `Agent/Agent 工程实战/Agent 工具没调用：一次真实链路验收的三层误判` |  |
| ${VAR} 是谁的环境变量：一条只写不读的凭据带走平台密钥 | `Agent/Agent 工程实战/MCP 环境变量展开：一条只写不读的凭据带走平台密钥` |  |
| OpenAI Responses API与Chat Completions API区别详解 | `Agent/Agent 工程实战/OpenAI Responses API与Chat Completions API区别详解` |  |
| 数据库初始化与迁移：从创建那一刻就要钉死的三件事 | `Agent/Agent 工程实战/数据库初始化与迁移：从创建那一刻就要钉死的三件事` |  |
| 给 Agent 接入 Web Search：四种做法，和一条我试过之后放弃的路 | `Agent/Agent 工程实战/给 Agent 接入 Web Search：四种做法，和一条我试过之后放弃的路` |  |
| 让用户选择指定 Skill：从社区实践到生产级 API 设计 | `Agent/Agent 工程实战/让用户选择指定 Skill：从社区实践到生产级 API 设计` |  |
| 阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍 | `Agent/Agent 工程实战/阿里云百炼联网搜索：三种入口，三种结果，我全都踩了一遍` |  |
| ai返回数据的格式不稳定，存在解析错误的问题 | `Agent/Agent开发中遇到的问题/ai返回数据的格式不稳定，存在解析错误的问题` |  |
| 相同LLM不同提示词的对比 | `Knowledge/others/相同LLM不同提示词的对比` | ⚠️#10 |

**第 4 章 · 可观测与协议**（8 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Agent Run 流式协议：事件溯源、SSE 投影与断线恢复 | `Agent/Agent 工程实战/Agent Run 流式协议：事件溯源、SSE 投影与断线恢复` |  |
| Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点 | `Agent/Agent 工程实战/Agent Tracing 基础：Trace、Span 与 OpenTelemetry 埋点` |  |
| Agent 决策审计落地：写入点、复核器与门禁降级判据 | `Agent/Agent 工程实战/Agent 决策审计落地：写入点、复核器与门禁降级判据` |  |
| Agent 决策审计：它与 Tracing 的关系 | `Agent/Agent 工程实战/Agent 决策审计：它与 Tracing 的关系` |  |
| Agent 埋点接 ARMS：上报返回 success，控制台却是空的 | `Agent/Agent 工程实战/Agent 埋点接 ARMS：上报返回 success，控制台却是空的` |  |
| Session、Thread、Run：一条消息为什么是一个 Run | `Agent/Agent 工程实战/Session、Thread、Run：一条消息为什么是一个 Run` |  |
| AG-UI：当 Agent 学会了和前端说话 | `Agent/Agent流式协议/AG-UI：当Agent学会了和前端说话` |  |
| 全量解码与增量解码：原理、区别以及应用 | `Knowledge/others/全量解码与增量解码：原理、区别以及应用` |  |

**第 5 章 · 沙箱与执行环境**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Agent 沙箱选型指南：隔离边界、产品对比与判断标准 | `Agent/Agent Orchestration/Agent 沙箱选型指南：隔离边界、产品对比与判断标准` |  |
| E2B 迁到阿里云云沙箱：能跑通，但别急着上生产 | `Agent/Agent Orchestration/E2B 迁到阿里云云沙箱：能跑通，但别急着上生产` |  |
| Cua 框架详解：给任何 Agent 一台可操控的电脑 | `Agent/ComputerUse/Cua 框架详解：给任何 Agent 一台可操控的电脑` |  |

**第 6 章 · 应用与集成**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| n8n | `DeepLearning/agent/n8n` | ⚠️#1 |
| nl2sql | `DeepLearning/agent/nl2sql` | ⚠️#2 |
| openclaw | `DeepLearning/agent/openclaw` | ⚠️#3 |

### 2. RAG 与 LangChain · 17 篇 · 4 章

**第 1 章 · LangChain 基础**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| LangChain 与 MCP 极简教程：让 Agent 接入外部工具的另一种方式 | `Agent/LangChain/LangChain与MCP极简教程` |  |
| LangChain 常见报错与排查指南 | `Agent/LangChain/LangChain常见报错与排查` |  |
| LangChain 模型接入指南：OpenAI 兼容协议与多平台调用 | `Agent/LangChain/LangChain模型接入指南` |  |
| LangSmith使用教程 | `Agent/LangChain/LangSmith使用教程` |  |
| langchain_core 组件详解：Prompt 模板与 Output Parsers | `Agent/LangChain/langchain_core组件详解` |  |

**第 2 章 · LangChain 进阶**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| DeepAgents完全指南 | `Agent/LangChain/DeepAgents完全指南` |  |
| Langchain-RAG实战教程 | `Agent/LangChain/LangChain-RAG实战教程` |  |
| LangGraph 实战：StateGraph、手写 ReAct 循环与 Map-Reduce 摘要 | `Agent/LangChain/LangGraph实战教程` |  |
| 一个订阅更新摘要 Agent 的完整实践：从提示词踩坑到长文本分块 | `Agent/LangChain/订阅摘要Agent实战` |  |

**第 3 章 · RAG 原理与实践**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| RAG入门：从问题定义到系统设计 | `Agent/RAG/01-RAG入门：从问题定义到系统设计` |  |
| RAG进阶：Chunking、召回、Hybrid Search 与 Rerank | `Agent/RAG/02-RAG进阶：Chunking、召回、Hybrid Search 与 Rerank` |  |
| RAG评测与 Inspect：如何知道问题出在检索、重排还是生成 | `Agent/RAG/03-RAG评测与 Inspect：如何知道问题出在检索、重排还是生成` |  |
| RAG生产实践：常见坑、性能优化与迭代路线图 | `Agent/RAG/04-RAG生产实践：常见坑、性能优化与迭代路线图` |  |

**第 4 章 · RAG 生态与选型**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Graph RAG 开源项目全景：从微软 GraphRAG 到 LightRAG | `Agent/GraphRAG开源项目全景：从微软GraphRAG到LightRAG` |  |
| RAGFlow 深度解析：为什么它是最值得关注的 RAG 开源项目 | `Agent/RAGFlow深度解析：为什么它是最值得关注的RAG开源项目` |  |
| RAG 技术全景：从入门到进阶 | `Agent/RAG技术全景：从入门到进阶` |  |
| vector-database | `DeepLearning/agent/vector-database` | ⚠️#4 |

### 3. 深度学习 · 21 篇 · 5 章

**第 1 章 · 模型与机制**（6 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| DeepSeek_NSA | `DeepLearning/models_and_strategies/Deepseek_NSA` |  |
| ICL-上下文学习 | `DeepLearning/models_and_strategies/ICL-上下文学习` |  |
| Jev：不写字的决策模型，和它真正适合解决的问题 | `DeepLearning/models_and_strategies/Jev：不写字的决策模型，和它真正适合解决的问题` |  |
| MoE | `DeepLearning/models_and_strategies/MoE` |  |
| Attention | `DeepLearning/models_and_strategies/attention注意力机制` |  |
| 大模型结构原理与代码实现 | `DeepLearning/models_and_strategies/模型-transformer原理和代码实现` |  |

**第 2 章 · 训练与对齐**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| LLM微调：qwen2_chat模型部署和微调 | `DeepLearning/NLP/LLM微调：qwen2_chat模型部署和微调` |  |
| Alignment-DPOvsPPOvsGRPO | `DeepLearning/models_and_strategies/Alignment-DPOvsPPOvsGRPO` |  |
| RLHF | `DeepLearning/models_and_strategies/RLHF` |  |
| 增量学习研究综述：理论、方法、应用与未来展望 | `DeepLearning/models_and_strategies/增量学习研究综述：理论、方法、应用与未来展望` |  |

**第 3 章 · NLP 任务**（2 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 命名实体识别 | `DeepLearning/NLP/命名实体识别` |  |
| 文本分类 | `DeepLearning/NLP/文本分类` |  |

**第 4 章 · 推理与部署**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 深度学习开源框架 | `DeepLearning/frame/DeepSpeed` |  |
| vllm | `DeepLearning/frame/vllm` |  |
| openbayes算力平台使用教程 | `Knowledge/others/openbayes算力平台使用教程` | ⚠️#6 |
| vllm使用教程 | `Knowledge/others/vllm实战教程` |  |

**第 5 章 · 基础与方法**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| mechine_learning_models | `DeepLearning/models_and_strategies/mechine_learning_models` |  |
| JAX | `Knowledge/others/JAX` |  |
| 什么是算子？ | `Knowledge/others/什么是算子？` | ⚠️#5 |
| 字典学习（Dictionary Learning） | `Knowledge/others/字典学习（Dictionary Learning）` |  |
| 对比了几种大模型在相同任务下的表现 | `Knowledge/others/对比了几种大模型在相同任务下的表现` | ⚠️#9 |

### 4. 编程语言 · 29 篇 · 5 章

**第 1 章 · 语言基础**（9 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Matlab-基本语法 | `Grammar/Matlab/Matlab-基本语法` | ⚠️#19 |
| Python-Docstring 的详细教程 | `Grammar/python/python-Docstring 的详细教程` |  |
| 【python】__init__.py为什么要写 | `Grammar/python/python-__init__.py为什么要写` |  |
| python-staticmethod 修饰符 | `Grammar/python/python-staticmethod 修饰符` |  |
| python-typing提高代码可读性 | `Grammar/python/python-typing提高代码可读性` |  |
| python-应如何定义包通用的变量-推荐config.py | `Grammar/python/python-应如何定义包通用的变量-推荐config.py` |  |
| python-数据类 | `Grammar/python/python-数据类` |  |
| python-类-类变量和实例变量 | `Grammar/python/python-类` |  |
| python的命名规范 | `Knowledge/others/python的命名规范` |  |

**第 2 章 · 包与工程化**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| python-logging模块添加日志 | `Grammar/python/python-logging模块添加日志` |  |
| python-lru_cache 缓存装饰器 | `Grammar/python/python-lru_cache 缓存装饰器` |  |
| python-在项目中应该如何定义文件路径 | `Grammar/python/python-在项目中应该如何定义文件路径` |  |
| python-将py文件编译为pyc文件并运行 | `Grammar/python/python-将py文件编译为pyc文件并运行` |  |
| python-相对导入错误attempted relative import with no known parent package | `Grammar/python/python-相对导入错误attempted relative import with no known parent package` |  |
| python使用教程-难点和遇到的问题 | `Grammar/python/python-难点和遇到的问题` |  |
| python中将函数设置为定时任务 | `Knowledge/others/python中将函数设置为定时任务` |  |

**第 3 章 · 常用库**（8 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| PyYAML | `Library/Python_Lib/PyYAML` |  |
| Typer + Rich 入门教程 | `Library/Python_Lib/Typer和Rich入门教程` |  |
| pickle | `Library/Python_Lib/pickle` |  |
| pytest测试用例使用教程 | `Library/Python_Lib/pytest` |  |
| python开发环境配置指南 | `Library/Python_Lib/python开发环境配置指南` |  |
| tableprint使用教程 | `Library/Python_Lib/tableprint使用教程` |  |
| toml_usage_tutorial | `Library/Python_Lib/toml_usage使用教程` |  |
| pydantic使用教程 | `Library/smallLibrary/pydantic使用教程` |  |

**第 4 章 · 界面与串口**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| PyQt-入门教程（AI生成） | `Grammar/PyQt/PyQt-入门教程` |  |
| PyQt-设备像素设置 | `Grammar/PyQt/PyQt-设备像素设置` |  |
| pyserial-使用教程 | `Library/pyserial/pyserial-Python 中最常用的串口通信库快速入门` |  |

**第 5 章 · 数据与 ORM**（2 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Alembic | `Project_Application/SQL/Alembic` | ⚠️#18 |
| SQLAlchemy简单入门 | `Project_Application/SQL/SQLAlchemy简单入门` | ⚠️#17 |

### 5. Web 开发 · 17 篇 · 4 章

**第 1 章 · FastAPI**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| ALL-fastapi | `Library/FastAPI/fastapi-ALL` |  |
| fastapi-docs_swagger_UI-openAPI | `Library/FastAPI/fastapi-docs_swagger_UI` |  |
| fastapi-前提知识 | `Library/FastAPI/fastapi-前提知识` |  |
| fastapi使用教程 | `Library/FastAPI/fastapi-第一个简单示例` |  |
| jwt-with-fastapi | `Library/FastAPI/jwt-with-fastapi` |  |
| 注入依赖进一步解释 | `Library/FastAPI/注入依赖进一步解释` |  |
| FASTAPI使用相关问题 | `Library/Python_Lib/fastapi使用` |  |

**第 2 章 · Flask 与后端模式**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Building asynchronous APIs for handling long-term tasks and dynamic resources | `Knowledge/others/Building asynchronous APIs for handling long-term tasks and dynamic resources` |  |
| Celery | `Knowledge/others/Celery` |  |
| Jinja是什么？可以用在做什么？ | `Knowledge/others/Jinja是什么？可以用在做什么？` |  |
| Flask使用教程 | `Library/Flask/Flask使用` |  |
| flask-构建一个简单的文件同步系统 | `Library/Flask/flask-构建一个简单的文件同步系统` |  |

**第 3 章 · 快速原型框架**（2 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| streamlit使用教程 | `Knowledge/others/streamlit使用教程` |  |
| gradio教程 | `Library/Python_Lib/gradio` |  |

**第 4 章 · 前端与跨端**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| React框架使用教程 | `Library/React/React框架使用教程` |  |
| flutter_tutorial | `Library/flutter/flutter_tutorial` |  |
| Refine: 当 API 即界面，CRUD 不再是体力活 | `Platforms_Tools/refine-meta-framework` |  |

### 6. 数据科学 · 13 篇 · 3 章

**第 1 章 · Transformers 全家桶**（6 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| datasets | `Library/transformers/datasets` |  |
| evaluate | `Library/transformers/evaluate` |  |
| model | `Library/transformers/model` |  |
| pipeline | `Library/transformers/pipeline` |  |
| tokenizer | `Library/transformers/tokenizer` |  |
| trainer | `Library/transformers/trainer` |  |

**第 2 章 · 数值与科学计算**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| numpy使用教程 | `Library/Python_Lib/numpy使用教程` |  |
| scipy | `Library/Python_Lib/scipy` |  |
| matplotlib教程-zata——v0.0.0 | `Library/matplotlib/matplotlib使用教程_Zata_v0.0.0` |  |
| pandas使用教程 | `Library/pandas/pandas使用教程` |  |

**第 3 章 · 建模与部署**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| sklearn使用教程 | `Library/Python_Lib/sklearn使用教程` |  |
| onnx使用教程 | `Library/smallLibrary/onnx使用教程` |  |
| torch使用教程-zata——v0.0.0 | `Library/torch/torch使用教程_Zata_v0.0.0` |  |

### 7. 构建与打包 · 10 篇 · 2 章

**第 1 章 · 依赖与环境管理**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| conda使用教程\|pip使用教程\|依赖安装_使用教程 | `Knowledge/others/conda使用相关` |  |
| 包管理工具poetry使用教程 | `Knowledge/others/包管理工具poetry使用教程` |  |
| npm使用教程 | `Platforms_Tools/packageTools/npm使用教程` |  |
| pipx使用教程 | `Platforms_Tools/pipx/pipx使用教程` |  |
| 包管理工具uv使用教程 | `Platforms_Tools/uv/包管理工具uv使用教程` |  |

**第 2 章 · 打包发布**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| setuptools-打包python项目为egg / 安装库函数 | `Library/setuptools/setuptools-打包python项目为egg` |  |
| PyInstaller使用教程 | `Platforms_Tools/PyInstaller/PyInstaller-简易教程` |  |
| Pyinstaller-打包gradio项目 | `Platforms_Tools/PyInstaller/Pyinstaller-打包gradio项目` |  |
| PyStand-简易教程 | `Platforms_Tools/PyStand/PyStand-简易教程` |  |
| python程序打包exe使用教程 | `Project_Application/PythonGUI/PythonGUI-打包成exe` |  |

### 8. 开发工具链 · 27 篇 · 5 章

**第 1 章 · Git 与 GitHub**（6 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Self-hosted Runner | `Project_Application/git&github/Self-hosted Runner` |  |
| gh使用教程 | `Project_Application/git&github/gh使用教程` |  |
| git&github_tutorial | `Project_Application/git&github/git&github使用` |  |
| git-submodule-子模块 | `Project_Application/git&github/git-submodule-子模块` |  |
| 2-github action 使用 | `Project_Application/git&github/github action` |  |
| github release | `Project_Application/git&github/github release` |  |

**第 2 章 · Docker 与容器**（8 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Docker Compose(dev\test\prod) | `Platforms_Tools/Docker/Docker Compose(devtestprod)` |  |
| Docker Swarm 实战（一）：核心概念与集群管理 | `Platforms_Tools/Docker/Docker Swarm 实战` |  |
| Docker Swarm 实战（二）：Traefik 反向代理部署 | `Platforms_Tools/Docker/Docker Swarm 实战 - Traefik 反向代理部署` |  |
| Docker 私有镜像仓库registry | `Platforms_Tools/Docker/Docker 私有仓库` |  |
| Docker使用实战-compose教程 | `Platforms_Tools/Docker/Docker使用实战-compose教程` |  |
| build x86 image in ARM MAC platform and devolopmet to remote server | `Platforms_Tools/Docker/build x86 image in ARM MAC platform and devolopmet to remote server` |  |
| _(无标题)_ | `Platforms_Tools/Docker/docker-ubuntu容器中安装miniconda问题合集` |  |
| docker使用教程 | `Platforms_Tools/Docker/docker容器相关命令` |  |

**第 3 章 · 浏览器自动化**（6 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| AI 生成前端的 E2E 实践：用 Playwright 做视觉回归和功能兜底 | `Platforms_Tools/dev_tools/ai-frontend-e2e` | ⚠️#15 |
| 浏览器会话录制与接口回放：方案调研 | `Platforms_Tools/dev_tools/browser-session-replay` |  |
| 扩展式 RPA：从 Chrome 扩展原理到 Playwright 实战方案 | `Platforms_Tools/dev_tools/extension-rpa` |  |
| 从 noVNC 到 Playwright 截图流：容器内 VNC 踩坑记 | `Platforms_Tools/dev_tools/novnc-playwright` |  |
| Playwright 使用实践与本地浏览器 Profile 避坑 | `Platforms_Tools/dev_tools/playwright-profile` |  |
| Playwright Chromium 在 Docker 内 SIGTRAP 启动崩溃排查实录 | `Platforms_Tools/dev_tools/playwright-sigtrap` |  |

**第 4 章 · 终端与编辑器**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| copier-using | `Knowledge/others/copier-using` |  |
| Herdr 详解：给 AI Agent 用的终端运行时 | `Platforms_Tools/CLI/herdr-ai-agent-terminal-runtime` |  |
| 为 AI 而写的 CLI 设计指南：原则、避坑与难点 | `Platforms_Tools/CLI/为AI而写的CLI设计指南` |  |
| CC Switch 详解：一个应用管住八个 AI 编程 CLI | `Platforms_Tools/dev_tools/cc-switch-guide` |  |
| VScode使用教程\|cursor使用教程 | `Project_Application/VScode/VScode安装和配置` |  |

**第 5 章 · AI 与创作工具**（2 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Blender 详解：奥斯卡和 AI Agent 为什么都选了它 | `Platforms_Tools/Blender/blender-complete-guide` | ⚠️#14 |
| 用 AI 把文章做成口播视频：三条路线、工具盘点与落地管线 | `Platforms_Tools/dev_tools/ai-article-to-video` |  |

### 9. 设计 · 14 篇 · 3 章

**第 1 章 · 软件架构**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 从脚本到企业级平台：AI Agent 系统"整洁架构"演进与 Python 落地指南 | `Design/软件架构设计/AI-Agent四层模块化单体架构` |  |
| FastAPI 后端架构设计 | `Design/软件架构设计/FastAPI后端架构设计` |  |
| 一个标准的软件项目结构 | `Design/软件架构设计/一个标准的软件项目结构` |  |
| 简洁架构（Clean Architecture）：让业务逻辑永远不依赖框架 | `Design/软件架构设计/简洁架构-Clean-Architecture` |  |
| 软件架构设计-培养软件架构师的思维 | `Design/软件架构设计/软件架构设计-培养软件架构师的思维` |  |
| 领域驱动设计（DDD）分层架构：用领域语言构建复杂系统 | `Design/软件架构设计/领域驱动设计分层架构-DDD` |  |
| 一个软件项目的文件目录应该怎么定义 | `Knowledge/others/一个软件项目的文件目录应该怎么定义` | ⚠️#11 |

**第 2 章 · UML 建模图**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 数据流图 | `Design/功能图/数据流图` |  |
| 类图 | `Design/结构图/类图` |  |
| _(无标题)_ | `Design/行为图/用例图` |  |

**第 3 章 · 原型与灵感**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 作图参考 | `Design/值得学习的图/作图参考` |  |
| 漂亮的reademe文件使用教程 | `Design/值得学习的图/漂亮的reademe文件使用教程` |  |
| 使用ai工具绘制原型图html并导入figma | `Design/原型图/使用ai工具绘制原型图html并导入figma` |  |
| 分类图 | `Library/优秀图表学习/分类图` |  |

### 10. 工程实践 · 11 篇 · 3 章

**第 1 章 · 可观测性**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| LogQL 查询语言详解：先选流，再过滤，最后才解析 | `Engineering/可观测性/LogQL查询语言详解` |  |
| 云原生可观测性：从"监控"到"洞察"的进化之路 | `Engineering/可观测性/云原生可观测性-从监控到洞察的进化之路` |  |
| 项目中日志的使用教程 | `Engineering/可观测性/项目中日志的使用教程` |  |

**第 2 章 · 流程与规范**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 软件项目开发流程使用教程 | `Engineering/软件工程/软件项目开发流程` |  |
| 通用模板规范GeneralTemplateSpecifications | `Grammar/general/通用模板规范GeneralTemplateSpecifications` |  |
| 代码写作心得-使用教程 | `Knowledge/others/代码写作心得-使用教程` |  |
| 怎么保存.env文件到github公开的仓库 | `Knowledge/others/怎么保存.env文件到github公开的仓库` |  |

**第 3 章 · DevOps 与平台**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Docker 和 Traefik 一键安装脚本 | `Engineering/DevOps/Docker-Traefik一键安装脚本` |  |
| Woodpecker CI 使用教程 | `Engineering/DevOps/Woodpecker-CI使用教程` |  |
| 企业AI工具平台架构设计：拥抱快速变化的AI生态 | `Engineering/platform-architecture/ai-platform-architecture` |  |
| 开发问题与解法笔记 | `Knowledge/others/开发问题与解法笔记` | ⚠️#13 |

### 11. 运维与服务器 · 27 篇 · 5 章

**第 1 章 · 服务器与系统**（10 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务 | `Knowledge/Linux/1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务` |  |
| bash命令使用教程 | `Knowledge/Linux/bash命令使用教程` |  |
| linux使用教程 | `Knowledge/Linux/linux服务器初始化配置教程` |  |
| Server Probe | `Knowledge/others/Server Probe` |  |
| server_ops | `Platforms_Tools/Server Operations and Maintenance-服务器运维/server_ops` |  |
| 服务器安全-server Security | `Platforms_Tools/Server Operations and Maintenance-服务器运维/服务器安全-server Security` |  |
| 服务器磁盘管理基础 | `Platforms_Tools/Server Operations and Maintenance-服务器运维/服务器磁盘管理基础` |  |
| 阿里云服务器 | `Platforms_Tools/Server Operations and Maintenance-服务器运维/阿里云服务器` |  |
| SSH使用教程 | `Project_Application/SSH/SSH常用命令` |  |
| 腾讯云修改为root登录 | `Project_Application/腾讯云修改root登录` |  |

**第 2 章 · 网络与代理**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 国外服务器扶墙 | `Knowledge/Linux/国外服务器扶墙` |  |
| rustdesk安装使用 | `Knowledge/others/rustdesk安装使用` |  |
| clash 教程 | `Knowledge/others/修改clash中的配置信息` |  |
| 代理配置与环境变量实战 | `Platforms_Tools/Server Operations and Maintenance-服务器运维/代理配置实战` |  |
| 服务器爬墙 | `Platforms_Tools/Server Operations and Maintenance-服务器运维/服务器爬墙` |  |

**第 3 章 · 网关与站点**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| traefik | `Platforms_Tools/Server Operations and Maintenance-服务器运维/traefik` |  |
| 域名迁移 | `Platforms_Tools/Server Operations and Maintenance-服务器运维/域名迁移` |  |
| Nginx | `Project_Application/nginx使用` |  |

**第 4 章 · 容器化部署**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 1panel使用教程｜云服务器使用教程 | `Knowledge/others/1panel使用` |  |
| Coolify | `Knowledge/others/Coolify` |  |
| CICD | `Platforms_Tools/Server Operations and Maintenance-服务器运维/CICD` |  |
| Dokploy | `Platforms_Tools/Server Operations and Maintenance-服务器运维/Dokploy` |  |

**第 5 章 · 存储与数据库**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| S3 兼容存储踩坑记：boto3 新默认校验和撞上 NotImplemented | `Platforms_Tools/S3/S3 兼容存储踩坑记：boto3 新默认校验和撞上 NotImplemented` |  |
| Object Storage (对象存储服务) | `Platforms_Tools/Server Operations and Maintenance-服务器运维/Object Storage (对象存储服务)` |  |
| PostgreSQL | `Project_Application/SQL/PostgreSQL` |  |
| redis | `Project_Application/SQL/redis` |  |
| 数据库备份实战 | `Project_Application/SQL/数据库备份实战` |  |

### 12. 项目实战 · 18 篇 · 3 章

**第 1 章 · 爬虫实战**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| ai-crawler-深度调研报告：人工智能驱动的网络爬虫技术——能力、应用与生态演进 | `Project_Application/crawler/ai-crawler` |  |
| crawler-tutorial | `Project_Application/crawler/crawler-tutorial` |  |
| crawler-爬虫ip代理商 | `Project_Application/crawler/crawler-爬虫ip代理商` |  |
| 一个自动签到的py并且使用github action每日执行 | `Project_Application/crawler/一个自动签到的py并且使用github action每日执行` |  |
| 爬虫-实战-多页面递归爬取 | `Project_Application/crawler/爬虫-实战-多页面递归爬取` |  |
| 爬虫-实战-爬取arXiv AI论文对应的url和title等 | `Project_Application/crawler/爬虫-实战-爬取arXiv AI论文对应的url和title等` |  |
| 爬虫-基础介绍 | `Project_Application/crawler/爬虫知识点` |  |

**第 2 章 · 博客建站**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 1-hugo安装使用 | `Project_Application/hugo/1-hugo安装使用` |  |
| 2-Hugo主题和配置 | `Project_Application/hugo/2-hugo主题和配置` |  |
| 3-hugo博客集成Netlify CMS | `Project_Application/hugo/3-hugo博客集成Netlify CMS` |  |
| 4-自定义Python函数创建博客：告别繁琐的文件头输入 | `Project_Application/hugo/4-自定义Python函数创建博客：告别繁琐的文件头输入` |  |
| 5-引入 Giscus 评论系统 | `Project_Application/hugo/5-引入 Giscus 评论系统` |  |
| hugo使用过程中遇到的问题 | `Project_Application/hugo/hugo使用过程中遇到的问题` |  |
| 给hugo博客的页面增加一个自定义密码（防君子不防小人） | `Project_Application/hugo/给页面增加一个自定义密码（防君子不防小人）` |  |

**第 3 章 · 应用开发**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Dify | `Project_Application/Dify` |  |
| 软件自动更新 | `Project_Application/PythonGUI/PythonGUI-软件自动更新` |  |
| 微信小程序使用教程——WechatMiniProgram | `Project_Application/wechatapplet/微信小程序使用教程` |  |
| 野火F103-MiNI使用教程 | `Project_Application/单片机/野火F103-MiNI使用教程` |  |

### 13. 软件试用 · 30 篇 · 5 章

**第 1 章 · AI 工具试用**（12 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| cc-switch | `Project_Application/SoftTrial/cc-switch` |  |
| ccNexus | `Project_Application/SoftTrial/ccNexus` |  |
| claude-code&codex&Gemini-cli | `Project_Application/SoftTrial/claude-code` |  |
| coze | `Project_Application/SoftTrial/coze` |  |
| everything-claude-code | `Project_Application/SoftTrial/everything-claude-code` |  |
| flora无限画布 | `Project_Application/SoftTrial/flora无限画布` |  |
| wrap.dev | `Project_Application/SoftTrial/wrap.dev` |  |
| 百度自由画布 | `Project_Application/SoftTrial/百度自由画布` |  |
| 软件工程的范式转移：基于 Claude Code 与智能体协作的高效编程实践 | `Project_Application/SoftUseExp/Efficient Programming Based on Claude Code Collaboration with Intelligent Agents` |  |
| Tavily-搜索引擎api | `Project_Application/SoftUseExp/Tavily` | ⚠️#16 |
| cherry-studio | `Project_Application/SoftUseExp/cherry-studio` |  |
| cursor使用教程 | `Project_Application/SoftUseExp/cursor使用教程` |  |

**第 2 章 · 终端与包管理**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| homebrew | `Project_Application/SoftTrial/homebrew` |  |
| nvm | `Project_Application/SoftTrial/nvm` |  |
| wsl使用教程 | `Project_Application/SoftTrial/wsl使用教程` |  |
| postman | `Project_Application/SoftUseExp/postman` |  |
| tmux简易使用 | `Project_Application/SoftUseExp/tmux` |  |
| 多台电脑环境变量(.env)同步方案 | `Project_Application/SoftUseExp/多台电脑环境变量(.env)同步方案` |  |
| 新电脑快速配置-scoop | `Project_Application/SoftUseExp/新电脑快速配置-scoop-homebrew` |  |

**第 3 章 · 部署与自托管**（5 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Coolify vs Dokploy | `Project_Application/SoftTrial/Coolify vs Dokploy` |  |
| alist | `Project_Application/SoftTrial/alist` |  |
| polar-DB | `Project_Application/SoftTrial/polar-DB` |  |
| 网页内容变化监控项目 | `Project_Application/SoftTrial/网页内容变化监控项目` |  |
| github项目newsnow部署 | `Project_Application/SoftUseExp/github项目newsnow部署` |  |

**第 4 章 · 文档与标注**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 数据集标注工具 | `Project_Application/SoftUseExp/LabelStudio-tutorial` |  |
| Sphinx-快速生成python项目的api文档 | `Project_Application/SoftUseExp/Sphinx-快速生成python项目的api文档` |  |
| 生成api文档工具的简易使用 | `Project_Application/SoftUseExp/api文档的写作` |  |

**第 5 章 · 桌面效率工具**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| IObit Unlocker解除文件占用 | `Project_Application/SoftTrial/IObit Unlocker解除文件占用` |  |
| 内网文件传输工具LocalSend | `Project_Application/SoftTrial/内网文件传输工具LocalSend` |  |
| 实用软件工具｜好用软件推荐 | `Project_Application/SoftUseExp/实用软件工具` |  |

### 14. 效率与文档 · 10 篇 · 2 章

**第 1 章 · 写作与排版**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Markdown中常用的图标或徽章 | `Knowledge/markdown/Markdown中常用的图标或徽章` |  |
| markdown使用技巧 | `Knowledge/markdown/markdown使用技巧` |  |
| “categories”（类别）和“tags”（标签）的区别 | `Knowledge/others/categories和tags的区别` | ⚠️#12 |
| 如何提成所写文档和ppt的颜值 | `Knowledge/others/如何提成所写文档和ppt的颜值` |  |
| 文档结构化实战：从 Markdown/PDF 到 Word | `Knowledge/others/技术追踪/文档结构化实战` |  |
| word-封面-你文档的门面 | `Knowledge/word技巧/word-封面-你文档的门面` |  |
| word技巧-排版和布局 | `Knowledge/word技巧/word技巧-排版和布局` |  |

**第 2 章 · 系统小技巧**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| mac os使用经验 | `Knowledge/others/macos使用经验` |  |
| 在overleaf中为什么两个完全一样的代码一个不能显示图片 | `Knowledge/others/在overleaf中为什么两个完全一样的代码一个不能显示图片` |  |
| 关闭win11更新 | `Knowledge/windows/关闭win11更新` |  |

### 15. 通识与生活 · 16 篇 · 3 章

**第 1 章 · 百科知识**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 中国历史知识 | `Knowledge/encyclopedic/中国历史知识` |  |
| 中国各省市介绍 | `Knowledge/encyclopedic/中国各省市介绍` |  |
| 总-百科知识 | `Knowledge/encyclopedic/总-百科知识` |  |
| 文学与幽默知识积累 | `Knowledge/encyclopedic/文学与幽默知识积累` |  |
| 汽车-百科知识 | `Knowledge/encyclopedic/汽车-百科知识` |  |
| 茶叶-百科知识 | `Knowledge/encyclopedic/茶叶` |  |
| shanghai-geographic | `Knowledge/geographic/shanghai-geographic` |  |

**第 2 章 · 英语学习**（2 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| english如何学习 | `Knowledge/English/english如何学习` |  |
| 英语语法知识点 | `Knowledge/English/英语语法知识点` |  |

**第 3 章 · 生活与个人**（7 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 生活中的方法 | `Grammar/general/生活中的收获量化方法` |  |
| cookbook | `Knowledge/others/cookbook` | ⚠️#8 |
| start_a_business | `Knowledge/others/start-a-business` |  |
| 如何和别人尬聊，打破僵局？ | `Knowledge/others/如何和别人尬聊，打破僵局？` |  |
| 如何自学一个新领域？ | `Knowledge/others/如何自学一个领域？` |  |
| 徒步知识点 | `Knowledge/others/徒步知识点` |  |
| 给Zata的公司取一个名字 | `Knowledge/others/给Zata的公司取一个名字` |  |

### 16. Vibe Coding · 7 篇 · 2 章

**第 1 章 · 设计工程研究**（4 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Design Engineer 到底是什么：从 Vercel 拆解到一个新角色 | `Vibe-Coding/AI-Frontend/ai-design-research/01-design-engineer是什么` |  |
| Figma MCP + Claude Code：从设计稿到上线的全过程 | `Vibe-Coding/AI-Frontend/ai-design-research/02-figma-mcp实战` |  |
| shadcn/ui + design token：LLM 原生设计系统实践 | `Vibe-Coding/AI-Frontend/ai-design-research/03-shadcn设计系统` |  |
| 一份能直接抄的前端 `.mdc` rules 模板 | `Vibe-Coding/AI-Frontend/ai-design-research/04-mdc-rules模板` |  |

**第 2 章 · 实战与调试**（3 篇）

| 标题 | 旧位置 | 备注 |
|---|---|---|
| AI 前端调试技巧：把被遮挡翻译成尺寸约束 | `Vibe-Coding/AI-Frontend/AI 前端调试技巧：把被遮挡翻译成尺寸约束` |  |
| 下拉框里显示 _all：Base UI 与 Radix Select 的一个行为差异 | `Vibe-Coding/AI-Frontend/Base UI Select 显示 _all 的坑` |  |
| 用 AI 打造惊艳前端：从 Vibe Coding 到实战的艺术指南 | `Vibe-Coding/AI-Frontend/art-of-ai-frontend-design` |  |

### 17. 面试八股 · 6 篇 · 平铺

| 标题 | 旧位置 | 备注 |
|---|---|---|
| Langchain开发八股-常见问题 | `Knowledge/面试八股/Langchain开发八股-常见问题` |  |
| 深度学习八股-基础理论知识 | `Knowledge/面试八股/深度学习八股-基础理论知识` |  |
| 深度学习八股-实战经验 | `Knowledge/面试八股/深度学习八股-实战经验` |  |
| 深度学习八股-技术栈与工具 | `Knowledge/面试八股/深度学习八股-技术栈与工具` |  |
| 深度学习八股-量化 | `Knowledge/面试八股/深度学习八股-量化` |  |
| 深度学习八股-面试常见问题 | `Knowledge/面试八股/深度学习八股-面试常见问题` |  |

### 18. 阅读笔记 · 3 篇 · 平铺

| 标题 | 旧位置 | 备注 |
|---|---|---|
| 《大语言模型》读书笔记（赵鑫） | `Book/读书笔记/大语言模型-赵鑫` |  |
| 近红外光谱的知识点 | `Knowledge/others/近红外光谱的知识点` | ⚠️#7 |
| 瑞金医院拉曼无创血糖论文 | `PaperReading/RuijinHospitalandNearviewTechnologyLaunchRamanSpectroscopyforNon-InvasiveBloodGlucoseMonitoring_NatureMetabolism` |  |

### 19. 科技月报 · 4 篇 · 平铺

| 标题 | 旧位置 | 备注 |
|---|---|---|
| ❤️每日思考和AI资讯 | `Knowledge/news/资讯和思考` |  |
| 技术热点追踪 | `Knowledge/others/技术追踪/技术热点追踪` |  |
| 科技月报-2025 | `Knowledge/科技月报：机器人又抢饭碗啦/科技月报-2025` |  |
| 科技月报-2026 | `Knowledge/科技月报：机器人又抢饭碗啦/科技月报-2026` |  |

## 待拍板清单

1. `DeepLearning/agent/n8n` — 仅一行 docker 安装命令，建议并入相关长文或删除
2. `DeepLearning/agent/nl2sql` — 24 词占位文，建议补写、并入或删除
3. `DeepLearning/agent/openclaw` — 从 DeepLearning/agent 迁入 Agent 工程线
4. `DeepLearning/agent/vector-database` — 归 RAG 与 LangChain（向量库是 RAG 基建）；也可留深度学习
5. `Knowledge/others/什么是算子？` — 17 词短文，建议合并或补写
6. `Knowledge/others/openbayes算力平台使用教程` — 19 词短文，建议合并或补写
7. `Knowledge/others/近红外光谱的知识点` — 放阅读笔记（与瑞金拉曼血糖论文同主题）；也可去通识与生活
8. `Knowledge/others/cookbook` — 实际是烧牛肉菜谱，归通识与生活
9. `Knowledge/others/对比了几种大模型在相同任务下的表现` — 模型评测归深度学习；也可去 Agent 工程
10. `Knowledge/others/相同LLM不同提示词的对比` — 提示词对比归 Agent 工程；也可去深度学习
11. `Knowledge/others/一个软件项目的文件目录应该怎么定义` — 与《一个标准的软件项目结构》成对，归设计；也可去工程实践
12. `Knowledge/others/categories和tags的区别` — 概念科普归效率与文档；也可去通识与生活
13. `Knowledge/others/开发问题与解法笔记` — 已按要求改名（原 Useful but not attempted）。正文待修缮：开头目录漏列 SSHFS 一问、WSL2 一节只有截图未写答案，建议后续补写或拆分
14. `Platforms_Tools/Blender/blender-complete-guide` — 创作工具归开发工具链；也可去软件试用
15. `Platforms_Tools/dev_tools/ai-frontend-e2e` — 与 Playwright 系列聚堆；其 front matter 现标 Vibe-Coding，也可去那边
16. `Project_Application/SoftUseExp/Tavily` — Agent 搜索 API，随软件试用；也可去 Agent 工程
17. `Project_Application/SQL/SQLAlchemy简单入门` — 数据库 5 篇拆了两处（这对去编程语言，PostgreSQL/redis/备份去运维）；想聚一起可整体挪
18. `Project_Application/SQL/Alembic` — 同上，与 SQLAlchemy 结伴
19. `Grammar/Matlab/Matlab-基本语法` — 语言基础章里唯一的非 Python 内容，可挪深度学习或留作小节

另外两处组级取舍：SoftTrial/SoftUseExp 30 篇里 homebrew、nvm、scoop、tmux、cursor 这类纯开发工具试用文，
如果想严格区分「教程」和「试用」，可挑几篇挪去开发工具链；构建与打包（10 篇）并回开发工具链（27 篇）也随时可以，60 上限内空间足够。

## 短文合并候选（正文 < 400 字）

没有一本超 60 篇，不需要为上限而合并；但下列短文/占位文影响成书后的目录质感，建议合并进同书长文、补写或删除。

| 标题 | 旧位置 | 字数 | 建议 |
|---|---|---|---|
| _(无标题)_ | `Platforms_Tools/Docker/docker-ubuntu容器中安装miniconda问题合集` | 0 | 空文件：补写或删除 |
| _(无标题)_ | `Design/行为图/用例图` | 0 | 空文件：补写或删除 |
| 使用ai工具绘制原型图html并导入figma | `Design/原型图/使用ai工具绘制原型图html并导入figma` | 26 | 极短：并入同书长文或补写 |
| 什么是算子？ | `Knowledge/others/什么是算子？` | 28 | 极短：并入同书长文或补写 |
| openbayes算力平台使用教程 | `Knowledge/others/openbayes算力平台使用教程` | 37 | 极短：并入同书长文或补写 |
| 数据流图 | `Design/功能图/数据流图` | 38 | 极短：并入同书长文或补写 |
| 百度自由画布 | `Project_Application/SoftTrial/百度自由画布` | 54 | 极短：并入同书长文或补写 |
| 给Zata的公司取一个名字 | `Knowledge/others/给Zata的公司取一个名字` | 57 | 极短：并入同书长文或补写 |
| 阿里云服务器 | `Platforms_Tools/Server Operations and Maintenance-服务器运维/阿里云服务器` | 61 | 极短：并入同书长文或补写 |
| 徒步知识点 | `Knowledge/others/徒步知识点` | 67 | 极短：并入同书长文或补写 |
| IObit Unlocker解除文件占用 | `Project_Application/SoftTrial/IObit Unlocker解除文件占用` | 82 | 极短：并入同书长文或补写 |
| 网页内容变化监控项目 | `Project_Application/SoftTrial/网页内容变化监控项目` | 82 | 极短：并入同书长文或补写 |
| word技巧-排版和布局 | `Knowledge/word技巧/word技巧-排版和布局` | 93 | 极短：并入同书长文或补写 |
| n8n | `DeepLearning/agent/n8n` | 94 | 极短：并入同书长文或补写 |
| 3-hugo博客集成Netlify CMS | `Project_Application/hugo/3-hugo博客集成Netlify CMS` | 112 | 极短：并入同书长文或补写 |
| 分类图 | `Library/优秀图表学习/分类图` | 131 | 极短：并入同书长文或补写 |
| 作图参考 | `Design/值得学习的图/作图参考` | 155 | 偏短：可考虑合并 |
| 腾讯云修改为root登录 | `Project_Application/腾讯云修改root登录` | 182 | 偏短：可考虑合并 |
| hugo使用过程中遇到的问题 | `Project_Application/hugo/hugo使用过程中遇到的问题` | 188 | 偏短：可考虑合并 |
| ALL-fastapi | `Library/FastAPI/fastapi-ALL` | 245 | 偏短：可考虑合并 |
| 英语语法知识点 | `Knowledge/English/英语语法知识点` | 252 | 偏短：可考虑合并 |
| coze | `Project_Application/SoftTrial/coze` | 324 | 偏短：可考虑合并 |
| PyStand-简易教程 | `Platforms_Tools/PyStand/PyStand-简易教程` | 347 | 偏短：可考虑合并 |
| english如何学习 | `Knowledge/English/english如何学习` | 393 | 偏短：可考虑合并 |

## 迁移时顺手修的数据问题

front matter 分类 ≠ 目录（Hugo 只认 front matter，迁移时统一以映射表为准）:
  - Platforms_Tools/dev_tools/playwright-profile → front matter 写的是 Library
  - Platforms_Tools/dev_tools/ai-frontend-e2e → front matter 写的是 Vibe-Coding
  - Platforms_Tools/refine-meta-framework → front matter 写的是 Library
  - Project_Application/SQL/SQLAlchemy简单入门 → front matter 写的是 Library
  - Project_Application/nginx使用 → front matter 写的是 Platforms_Tools
0 字节空文件（无标题无分类）: Design/行为图/用例图、Platforms_Tools/Docker/docker-ubuntu容器中安装miniconda问题合集

空目录清理：

- content/post/Design/产品设计/（0 篇）
- content/post/Knowledge/文档结构化/（0 篇）
- content/post/Platforms_Tools/just-worktree-clauded-alias-fix/（0 篇）
- content/post/images/（只有一个 README，不是分类）

## 后续步骤

1. 过一遍本表：改书名/章节名，处理 ⚠️ 条目和合并候选（直接改 md 或口头说，我同步进脚本规则）
2. `zata.py create-category` 建 19 个新分类（含封面图）；今后新文章一篇只挂一个分类、一个 tag=章节
3. 迁移命令（参照 `tools/merge_categories.py` 的 dry-run/--apply 惯例）：git mv 到 `content/post/{书}/{章节}/{文章}` + 重写 categories 和 tags，顺手修 5 处 front matter、处理 2 个空文件、删空目录
4. `hugo server` 全站点验；然后章内排序（weight）定稿书目录，再做书视图前端（书页目录 + 篇尾续读）
