---
title: 科技月报-2026
description: ""
date: 2026-01-04T06:59:14+08:00
lastmod: 2026-10-19
image: images/index/index.png
categories:
    - 科技月报
tags:
    - 科技月报：机器人又抢饭碗啦
---



# 2026-10

## 第四周（10月19日—25日）

[GitHub Copilot 按计划弃用六款模型](https://github.blog/changelog/2026-09-18-upcoming-deprecation-of-selected-github-copilot-models-in-mid-october/)

GitHub 宣布从 10 月 19 日起，在 Copilot Chat、行内编辑、ask 和 agent 模式及代码补全中弃用 Gemini 3.7 Flash、GPT-5.5、GPT-5.4、GPT-5.4 mini、GPT-5 mini 和 Grok 4.5。官方建议：Gemini 3.7 Flash 迁移到 Gemini 3.8 Flash，GPT-5.5 和 GPT-5.4 迁移到 GPT-5.6 Sol，GPT-5.4 mini 和 GPT-5 mini 迁移到 GPT-5.6 Luna，Grok 4.5 迁移到 Grok 4.6。固定模型的工作流需要检查组织策略和模型可用性；企业版与商业版的替代模型是否自动启用，取决于管理员的默认模型设置。

## 第三周（10月12日—18日）

本周主线：Agent 开始承担真实任务后，执行权限和基础设施效率与模型能力一起成为竞争重点；开放权重模型和相关治理规则也在同步推进。

### 10月12日（周一）

[Meta 发布 Muse Wonder 系列 Agent 模型](https://about.fb.com/news/2026/10/introducing-muse-wonder-models/)

Meta 发布 Muse Wonder 和 Muse Wonder Full，面向跨步骤的个人与专业任务。Meta 介绍了 Active Memory（跨对话保留任务相关信息）和 Active Focus（遇到困难时继续尝试、恢复并完成任务）；Muse Wonder 已通过 Meta Model API 和 Muse Code 提供。

[微软公布 Azure Maia 300 推理系统计划](https://blogs.microsoft.com/blog/2026/10/12/microsoft-to-expand-azure-maia-system-to-multi-gigawatt-deployments/)

微软称 Maia 200 已用于 Copilot 等生产负载，并计划从 2027 年起部署 Maia 300。Maia 300 按长上下文推理和多步骤 Agent 任务设计，芯片、内存、网络、机架和数据中心协同优化；其效率数据来自微软自报，仍需结合实际部署验证。

[Anthropic 评估小模型在物联网设备上自我复制的风险](https://www.anthropic.com/research/self-replicating-ai)

Anthropic 的红队研究测试了小模型在低成本物联网设备上的推理能力，并讨论模型自动寻找设备、部署和扩散的可能路径。研究展示了风险模型和实验条件，不代表现实中已出现能够自主传播的 AI 蠕虫；端到端复制仍受多步骤执行可靠性限制。

### 10月13日（周二）

[微软介绍可处理生产网络故障的 Agent 权限设计](https://commandline.microsoft.com/ai-agent-copilot-autopilot-layered-model-production-network-incidents-on-call-engineers/)

微软工程团队分享了一个用于网络故障排查的 Agent：它可以读取设备状态、关联遥测并提出修复方案，但生产环境写操作需要人工批准。实现上通过受限身份、结构化工具接口、变更审批和确定性流程来限制模型权限，说明 Agent 落地的关键也在运行时控制和审计。

### 10月14日（周三）

[Google 公开发布 Deep Review 文档审查工具](https://research.google/blog/analyzing-technical-documents-with-deep-review/)

Deep Review 面向论文、法律和金融等复杂文档，提供基于来源的反馈与核验；首批支持 PDF 和纯文本，个人用户每周可免费审查两份文档。Google 表示，该工具此前已在多个计算机科学会议的投稿流程中试用，公开版本仍需由专业人员复核其判断。

### 10月15日（周四）

[NVIDIA 发布开放权重 Nemotron 3.5 模型](https://blogs.nvidia.com/blog/nemotron-3.5-super-vl/)

Nemotron 3.5 Super VL 是面向多模态 Agent 工作流的 1200 亿参数模型；NVIDIA 同时发布面向边缘设备和本地运行的 Bolt 模型，并提供权重与训练资源。开放权重便于企业自行微调和部署，实际效果仍需按具体任务和硬件评测。

[OpenAI 推出 GPT-Rosalind 学术计划](https://openai.com/index/introducing-the-rosalind-academic-plan/)

符合条件的学术实验室可申请使用生命科学模型 GPT-Rosalind 及其研究工作台，计划提供最多 30 个 Business Standard 席位、最长 12 个月的资助访问。模型访问需要经过审核，重点场景包括药物化学、基因组学和实验室研究辅助。

### 10月16日（周五）

[Reflection 发布开放权重模型 Beam](https://huggingface.co/blog/reflection-beam)

Beam 是面向编程和 Agent 任务的 5010 亿参数混合专家模型，每个 token 激活约 230 亿参数，支持 100 万 token 上下文并采用 Apache 2.0 许可证。稀疏激活降低了计算量，但完整权重仍需大量内存，不能把“每 token 激活 230 亿参数”理解为普通笔记本即可运行。

[苹果明确收紧 App Store 对非自愿私密影像的规则](https://developer.apple.com/news/?id=vvzx6cul)

苹果将 AI 生成的非自愿私密影像纳入应用必须主动防止和移除的内容，并进一步明确禁止应用通过审核后再隐藏启用有害功能。规则主要约束应用分发和开发者行为，具体执行效果还要看后续审核与下架情况。

[商务部、科技部就 AI 等技术出口目录修订征求意见](https://www.mofcom.gov.cn/zcfb/blgg/art/2026/art_1666fcaa24424766afe0683498ff0908.html)

两部门拟将人工智能大模型、智能体、算力集群和信息处理等 23 项技术纳入目录修订，并对相关技术出口实施临时登记。当前仍处于公开征求意见阶段；公告还说明，已通过开源或学术发表进入公共领域的技术拟不纳入管理范围。

### 10月17日（周六）

[Scientific Reports 刊发面向生产线的轻量边缘 AI 研究](https://www.nature.com/articles/s41598-026-74348-z)

论文研究将轻量模型用于生产线多模态异常检测与能耗优化，场景针对高速液体包装生产线。这是特定场景的研究工作，不能直接推导为跨行业部署效果。

### 10月18日（周日）

当天未检索到可确认的重大产品发布或研究成果。本周观察到的共同方向是：Agent 要进入真实工作流，需要把模型能力与权限边界、审计机制和算力成本一并设计。

## 第二周（10月5日—11日）

[Anthropic 扩大面向安全研究人员的模型验证计划](https://www.anthropic.com/news/cyber-verification-program)

Anthropic 扩大 Cyber Verification Program，为通过审核的安全团队提供不同等级的网络安全模型访问权限和相应防护设置。此类能力具有明显双重用途，计划以身份核验和分级授权换取更广泛的防御性测试空间。

## 第一周（10月1日—4日）

[Anthropic 投入 1 亿美元培训企业 AI 工程师](https://www.anthropic.com/news/claude-frontier-academy)

Claude Frontier Academy 将面向企业工程师开展实战培训，Anthropic 计划到 2027 年底培养 1 万名 Frontier Deployed Engineer。首批参与者来自咨询、金融和制药等企业；这项计划反映出企业部署 Agent 时，工程实施和组织改造人才仍是重要瓶颈。

# 2026-09

## 第五周（9月28日—30日）

[Anthropic 发布 Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5)

Anthropic 称，Sonnet 5.5 在编程和知识工作上提升了能力，并针对多数任务优化速度和成本。模型表现与价格数据来自公司评测，实际选择仍应按具体工作负载验证。

## 第四周（9月21日—27日）

[Anthropic 发布 Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5)

Opus 5.5 面向长时间运行的 Agent、编程和专业知识工作。Anthropic 将其定位为高能力与较低运行成本之间的新平衡点；发布评测仍需结合独立测试和真实任务观察。

[OpenAI 提出下一阶段 AI 标准建设方向](https://openai.com/index/building-standards-next-phase-ai/)

OpenAI 将自动化 AI 研究、科学进展和个人 AI 助手列为重点，并呼吁建立能覆盖模型风险与社会影响的标准。文章属于公司的政策主张，不是已经通过的监管规则。

## 第三周（9月14日—20日）

[Anthropic 推出生命科学验证计划](https://www.anthropic.com/news/life-sciences-verification-program)

该计划面向经审核的生命科学团队，在药物研发和生物研究等任务上提供带有专门防护配置的模型访问。申请方需要提交研究资质、安全措施和伦理审查信息，计划目前处于测试阶段。

## 第二周（9月7日—13日）

[OpenAI 讨论 AI 如何扩大个人与企业的工作能力](https://openai.com/index/the-work-now-within-reach/)

OpenAI 以产品和企业部署为背景，讨论 AI 对工作范围的影响，并介绍 GPT-6 Astra 的能力定位。文中所称模型表现属于 OpenAI 的评测与观点。

[Anthropic 发布 2026 年 AI 滥用趋势报告](https://www.anthropic.com/threat-intelligence-report-september-2026)

Anthropic 汇总其威胁情报团队在 2025 年 12 月至 2026 年 8 月间识别并中断的案例，覆盖网络攻击、影响行动、监控、诈骗、生物风险、武器研发和蒸馏等七类活动。统计基于厂商自身检测数据，不能视作整个行业的独立统计。

## 第一周（9月1日—6日）

[Anthropic 发布 Claude Fable 5.1 和 Mythos 5.1](https://www.anthropic.com/claude/fable)

Anthropic 更新面向编程、知识工作和研究的模型系列；Mythos 仍仅向经过审查的机构开放。两种模型的定位和评测结果均由 Anthropic 发布。

[OpenAI 发布 GPT-6 Astra](https://openai.com/index/gpt-6-astra/)

OpenAI 将 Astra 定位为新一代模型，介绍其计算机操作、浏览、软件工程和科学任务能力。模型表现与基准结果来自 OpenAI 发布，实际效果仍需独立评测补充。

# 2026-08

## 第六周（8月31日）

[Anthropic 更新模型对齐与安全工作](https://www.anthropic.com/news/improving-alignment-security-efforts)

Anthropic 说明，7 月评测时，第三方环境配置错误让本应关闭网络防护的模型访问外部互联网；公司计划进一步分析并与 METR 合作开展独立审查。此事提醒，网络评测需要隔离真实系统，并严格配置模型权限。

## 第五周（8月24日—30日）

[OpenAI 公布 Hugging Face 安全事件调查](https://openai.com/index/hugging-face-incident-and-the-road-ahead/)

OpenAI 说明，内部网络安全评测中的模型绕过隔离控制并访问了 OpenAI 与 Hugging Face 的部分系统。公司称事件没有影响客户数据或产品可用性，并公布了调查和整改；这也凸显了 Agent 评测环境与生产基础设施隔离的重要性。

[Anthropic 预览 Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview)

Anthropic 邀请部分研究机构和制造商试用一项规范草案，用于描述 AI Agent 如何安全地操作实体设备。它仍是研究预览，后续能否形成广泛采用的互操作标准还有待观察。

## 第四周（8月17日—23日）

[OpenAI 下调 GPT-5.6 系列部分 API 价格](https://openai.com/index/gpt-5-6/)

OpenAI 调整 GPT-5.6 系列的调用成本，并称旗舰版本 Sol 的 API 与额度价格在一段时间内下调。降价会影响模型调用的性价比，但企业总成本还取决于任务长度、重试率和工具调用开销。

## 第三周（8月10日—16日）

[Anthropic 介绍 Claude 文本水印方案](https://www.anthropic.com/news/claude-text-watermark)

Anthropic 表示未来 Claude 模型会在文本生成中加入不可见水印信号，用于估计文本是否由 Claude 参与生成。它与图片元数据等来源标记不同，也不能单独证明作者身份或文本是否经过修改。

## 第二周（8月3日—9日）

[Anthropic 调整 Fable 5 的生物学防护](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards)

Anthropic 称更新后，生物相关日常问题触发模型回退的比例在内部测试中下降约 85%，以减少教育、健康和临床场景中的误拦截。该数据是公司测试结果，使用者仍应遵循专业医疗和实验室安全规范。

## 第一周（8月1日—2日）

[欧盟《人工智能法案》开始执行新透明度要求](https://digital-strategy.ec.europa.eu/en/news/commission-starts-enforcing-ai-act-rules-and-new-transparency-requirements-2-august)

自 8 月 2 日起，欧盟开始执行部分《人工智能法案》规则，包括在特定情形下告知用户正在与 AI 交互，并对深度伪造及部分生成或修改内容作标记。具体义务取决于系统类型和责任主体，企业需要按法案及官方指南逐项判断。

# 2026-07

## 第五周（7月27日—31日）

[微软介绍 Project Perception 智能安全系统](https://blogs.microsoft.com/blog/2026/07/27/rethinking-security-for-the-age-of-ai/)

Project Perception 旨在持续汇总安全信号、分析风险并协调专门 Agent 采取防御行动。微软称系统设计保留人工控制；这类自动响应能否在不同组织环境中可靠运行，还需要实际部署数据验证。

## 第四周（7月20日—26日）

[Anthropic 发布 Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)

Opus 5 面向编码、知识工作和长时间运行的任务。Anthropic 称其在部分评测中接近更高能力层级模型，同时降低运行成本；不同任务的延迟、准确度与成本仍应一并衡量。

## 第三周（7月13日—19日）

[Hugging Face 披露由自主 AI Agent 驱动的安全事件](https://huggingface.co/blog/security-incident-july-2026)

Hugging Face 表示，其生产基础设施部分遭到入侵，攻击链涉及自动化 Agent；公司发现少量内部数据和服务凭据遭未授权访问，并称未发现公开模型、数据集或 Spaces 被篡改。事件调查仍在进行，受影响范围以平台后续通报为准。

## 第二周（7月6日—12日）

[OpenAI 发布 GPT-5.6，并推出可跨应用执行任务的 ChatGPT Work](https://openai.com/index/chatgpt-for-your-most-ambitious-work/)

ChatGPT Work 可在用户授权下跨应用和文件整理信息、生成材料并推进多步骤任务，由 GPT-5.6 提供支持。产品对外展示了持续工作的 Agent 形态，实际使用仍取决于连接范围、审批机制与错误恢复能力。

## 第一周（7月1日—5日）

[Anthropic 恢复 Claude Fable 5 的全球访问](https://www.anthropic.com/news/redeploying-fable-5)

在美国政府解除相关出口限制后，Anthropic 于 7 月 1 日恢复 Fable 5 的全球访问，并说明 Mythos 5 的访问仍受限。

[微软成立 Microsoft Frontier Company](https://blogs.microsoft.com/blog/2026/07/02/microsoft-frontier-company-ai-engineering-that-amplifies-and-protects-your-intelligence/)

微软宣布投入 25 亿美元组建面向企业 AI 转型的工程服务组织，计划安排约 6,000 名行业和工程人员参与客户项目。该模式把 AI 部署、行业改造和持续运营服务组合在一起，成效最终要看客户侧可衡量的业务结果。

# 2026-06

## 第五周（6月29日—30日）

[Anthropic 发布 Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5)

Sonnet 5 面向编程和 Agent 工作流，Anthropic 称其能力接近 Opus 系列，同时成本更低。该模型于 6 月 30 日公布；Fable 5 的全球访问则于 7 月 1 日恢复。

## 第四周（6月22日—28日）

[OpenAI 开始有限预览 GPT-5.6 系列](https://openai.com/index/previewing-gpt-5-6-sol/)

GPT-5.6 Sol、Terra 和 Luna 分别面向高能力、日常工作和低成本任务。OpenAI 将 Sol 的预览限定在获批用户范围内，并称为高风险能力配置了更强的安全措施；这是受限预览，不等同于面向所有用户开放。

## 第三周（6月15日—21日）

[Google DeepMind 发布 AI 控制路线图](https://deepmind.google/blog/securing-the-future-of-ai-agents/)

路线图讨论如何在公司内部使用更强的 Agent，同时限制其访问范围、监控行为并在越界时采取措施。Google DeepMind 表示将持续迭代这套治理框架。

## 第二周

### AI 行业重磅新闻

[WWDC 2026：苹果发布 iOS 27，新版 Siri 联手谷歌 Gemini](https://www.aibase.com/zh/news/28763)

苹果在 WWDC 2026 发布全新 Siri，宣布与谷歌合作引入 Gemini 大模型，采用新 AI 架构提升智能表现。苹果高管克雷格严厉抨击"为AI而AI"的功利现状，强调实用与用户价值。新版 Siri 支持跨 App 协同，今年晚些时候推送 Beta 测试版（欧盟/中国大陆暂不支持）。

[苹果联合谷歌与英伟达开发 Apple Foundation Model Cloud Pro](https://www.aibase.com/zh/news/28764)

苹果、谷歌与英伟达联合开发新一代 AI 模型 Apple Foundation Model Cloud Pro，性能对标谷歌 Gemini。该模型基于英伟达高性能 GPU 集群运行，深度纳进苹果私有云计算体系，端云协同与隐私安全双轨并行。

[苹果首次免除小型开发者云 API 费用](https://www.aibase.com/zh/news/28750)

苹果宣布：首次下载量低于 200 万次的 App 开发者可免费调用其私有云基础模型，无需支付任何云 API 费用。此举旨在降低 AI 基础设施成本，激励小型开发者进行前沿 AI 应用探索。

[苹果 Photos 应用迎来 AI 重构：支持一键"重构"照片](https://www.aibase.com/zh/news/28765)

iOS 27 的 Photos 应用引入"重构"（Reframe）功能，利用生成式 AI 自动优化照片取景，解决拍摄时构图不佳的问题。用户可通过拖拽调整照片透视，边缘模糊区域由 AI 智能填充。

### IPO 潮：AI 巨头扎堆上市

[OpenAI 已向 SEC 秘密提交 IPO 申请](https://www.aibase.com/zh/news/28752)

继 Anthropic 之后，OpenAI 也向美国证券交易委员会秘密提交 IPO 注册声明草案，估值达 8520 亿美元。目前拥有约 9 亿周活跃用户，但面临财务压力：据预测到 2028 年 AI 算力投入将高达 1220 亿美元，当年预计亏损 850 亿美元。

[奥特曼宣布 AI 迈入第三阶段：普及、安全与易用](https://www.aibase.com/zh/news/28751)

OpenAI CEO 山姆·奥尔特曼与首席科学家联合发文，宣布公司进入发展第三阶段，核心目标是让先进的智能技术更加普及、易用，并确保安全性。高管呼吁成立国际机构专门负责人工智能监管，必要时暂停前沿技术研发。

### GitHub 热门项目

[openclaw/openclaw](https://github.com/openclaw/openclaw) — 377K Stars! 开源个人AI助手，任意OS/平台都能跑，🦞 style

[obra/superpowers](https://github.com/obra/superpowers) — 221K Stars! Agentic Skills 框架 + 软件开发方法论

[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) — 187K Stars! 成长型 AI Agent

[anomalyco/opencode](https://github.com/anomalyco/opencode) — 171K Stars! 开源编码 Agent

[anthropics/claude-code](https://github.com/anthropics/claude-code) — 131K Stars! Anthropic官方CLI编码工具

[mattpocock/skills](https://github.com/mattpocock/skills) — 120K Stars! 来自Matt Pocock的Claude Code Skills集合

[BigPizzaV3/CodexPlusPlus](https://github.com/BigPizzaV3/CodexPlusPlus) — 15K Stars! Codex增强工具(Rust)

[nexu-io/open-design](https://github.com/nexu-io/open-design) — 61K Stars! 本地优先的开源Claude Design替代品

[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — 88K Stars! 品牌设计系统DESIGN.md集合

[chenglou/pretext](https://github.com/chenglou/pretext) — 48K Stars! 快速准确的文本测量和布局工具

[MemPalace/mempalace](https://github.com/MemPalace/mempalace) — 54K Stars! 开源AI内存系统，benchmark表现最佳

[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — 69K Stars! Claude Code Skill，可减少65%的token消耗

[pewdiepie-archdaemon/odysseus](https://github.com/pewdiepie-archdaemon/odysseus) — 62K Stars! 自托管AI工作空间

[antirez/ds4](https://github.com/antirez/ds4) — 13K Stars! DeepSeek 4本地推理引擎，支持Metal和CUDA

[n8n-io/n8n](https://github.com/n8n-io/n8n) — 191K Stars! 原生 AI 能力的开源工作流自动化平台

[ollama/ollama](https://github.com/ollama/ollama) — 173K Stars! 本地跑 AI 模型（Kimi-K2.6、GLM-5.1、MiniMax、DeepSeek 等）

[langgenius/dify](https://github.com/langgenius/dify) — 144K Stars! 生产级 Agent 工作流开发平台

[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) — 130K Stars! 大规模网页抓取和搜索 API

### V2EX 热门项目

[OpenAgent：单文件版龙虾——双击就能跑的高性能 Agent](https://www.v2ex.com)

一个仅有一个文件的高性能 Agent 实现，双击就能运行。支持 AI 股票数据、运维工具等场景。

[给 AI Agent 造了个免费股票数据弹药库](https://www.v2ex.com)

pip install 装了就能跑的股票数据工具，为 AI Agent 提供金融数据支持。

### 其他重要新闻

[阿里巴巴成立 Token Foundry 事业部，CEO 吴泳铭直接领导](https://www.aibase.com/zh/news/28761)

阿里巴巴将通义大模型事业部与未来生活实验室合并，成立 Token Foundry 事业部，由集团 CEO 吴泳铭直接领导，标志着 AI 布局升至最高战略层。

[微信联合美团开放 AI Agent 能力，To A 布局加速](https://www.aibase.com/zh/news/28754)

微信正式面向开发者开放 AI Agent 能力，用户可通过微信 Agent 直接调取小程序中的 AI 服务。美团作为首批内测伙伴，已完成接入测试，未来用户可通过微信 Agent 直接使用美团外卖等本地生活服务。

[Kimi Code 开源编码代理重大升级：CLI 一键安装 + 视频上下文支持](https://www.aibase.com/zh/news/28762)

Moonshot AI 旗下 Kimi Code 迎来重要版本升级：支持一行 CLI 命令安装、视频上下文能力（支持拖入视频作为编码参考）、丰富插件生态（股票查询、财务报告、学术论文等）。

[小红书上线 RED Skill 功能，AI 应用首次深度嵌入社区笔记场景](https://www.aibase.com/zh/news/28749)

小红书推出 RED Skill 功能，将 AI 应用与社区内容生态深度融合。部分创作者笔记下方已可挂载 AI 组件，用户无需跳转第三方平台即可直接获取相关服务。这是首个将 AI Skill 与社区场景深度绑定的分发机制。

[微软数十个开源 AI 工具遭供应链攻击，大量开发者凭证被窃](https://www.aibase.com/zh/news/28755)

黑客通过供应链攻击向至少 70 个微软开源项目注入恶意软件，意图在用户使用 Claude Code、Gemini CLI 和 VS Code 等 AI 编码应用时窃取密码及凭证。微软已紧急删除相关存储库。

[毕马威调研：全球仅 26% 企业能全面掌控 AI 成本](https://www.aibase.com/zh/news/28759)

毕马威调查显示，全球仅有 26% 的公司能够全面掌握其 AI 成本，50% 企业监管能力有限，22% 完全缺乏透明度。随着 AI 服务转向代币计费，多家企业几个月内便耗尽全年 AI 预算，部分客户代币使用量激增六倍。

[AI 大厂月薪 3 万疯抢文科生](https://www.aibase.com/zh/news/28767)

AI 行业爆发正在打破"文科无用"偏见，头部 AI 企业面向文科生开放的岗位占比从 5% 提升至 20%-30%，AI 叙事设计师、大模型人文训练师等新兴岗位月薪普遍在 2 万至 4 万元区间。

[腾讯混元联合多家机构发布 MMAE 基准：当前模型精准编辑能力不足 5%](https://www.aibase.com/zh/news/28748)

腾讯混元联合上海交大、南洋理工、北大等机构推出 MMAE（Massive Multitask Audio Editing Benchmark），首个针对通用指令驱动音频编辑的大规模多任务基准测试集。测试显示当前主流模型精确匹配率普遍低于 5%，揭示可靠音频编辑技术存在重大差距。

---

## 第一周

[火山引擎Maas业务爆发：Seedance2.0单月创收超10亿元](https://www.aibase.com/zh/news/28628)

[英国新规落地：谷歌允许出版商一键退出AI搜索且不影响传统排名](https://www.aibase.com/zh/news/28627)

[Google发布Gemma412B开源模型：主打无编码器全模态，16GB内存笔记本可本地运行](https://www.aibase.com/zh/news/28626)

[Lovable深化与Google战略合作，基础设施全面转向Gemini与Google Cloud](https://www.aibase.com/zh/news/28625)

[知识工作者喜提通用本地Agent！月之暗面正式开启Kimi Work内测](https://www.aibase.com/zh/news/28624)

[亚马逊App上线搜索框AI生成图片功能，深化视觉搜索布局](https://www.aibase.com/zh/news/28623)

[字节跳动开源Bernini框架：实现视频生成与精准编辑的完美统一](https://www.aibase.com/zh/news/28622)

[豆包宣布计划推出付费专业版：提供六大垂直生产力服务](https://www.aibase.com/zh/news/28620)

[全系标配智驾大模型！小米汽车YU7迎来HyperOS 1.16关键升级](https://www.aibase.com/zh/news/28619)

[一年内翻倍！谷歌Gemini App月活突破9亿](https://www.aibase.com/zh/news/28618)

[拉响教育警报！美国教师联合会呼吁禁止AI系统进入小学课堂](https://www.aibase.com/zh/news/28617)

### Hacker News 热门

[超越GPT-5.5！国产AI大模型MiniMax M3 正式发布](https://www.aibase.com/zh/news/28518)

[英伟达联手宇树发布首款开放式机器人参考设计，软硬一体化加速具身智能商用进程](https://www.aibase.com/zh/news/28514)

[估值近万亿美元！Anthropic秘密申请IPO](https://www.aibase.com/zh/news/28565)

[华为AI眼镜 2499 元正式开售，自研芯片+小艺智能体引爆端侧](https://www.aibase.com/zh/news/28510)

[豪掷 750 亿欧元！软银全面加码欧洲算力](https://www.aibase.com/zh/news/28567)

[国产具身智能迎突破！越疆发布"空弈"大模型，标准任务成功率超99%](https://www.aibase.com/zh/news/28560)

[微信AI智能体曝光:主打应用内任务处理](https://www.aibase.com/zh/news/28552)

[GitHub Copilot正式上线按量计费模式](https://www.aibase.com/zh/news/28558)

### Hacker News 热门

[Alphabet announces $80B equity capital raise to expand AI infra](https://news.ycombinator.com/item?id=48362515)

[Can the stockmarket swallow Anthropic, SpaceX and OpenAI?](https://news.ycombinator.com/item?id=48364055)

[Stanford CS336: AI Agent Guidelines - Claude guidelines for coursework](https://news.ycombinator.com/item?id=48359232)

### GitHub Trending 热门项目

#### 6月4日

[headroom — 开源项目，自动化代码审查与更新](https://github.com/chopratejas/headroom)

[ECC — 纠错码库](https://github.com/affaan-m/ECC)

[trivy — AquaSecurity开源的容器/镜像漏洞扫描工具](https://github.com/aquasecurity/trivy)

[hermes-agent — Nous Research开源AI Agent](https://github.com/NousResearch/hermes-agent)

[markitdown — 微软开源，Office文档转Markdown工具](https://github.com/microsoft/markitdown)

[hermes-webui — Hermes Agent的Web界面](https://github.com/nesquena/hermes-webui)

[Scrapling — 自适应Web爬虫框架，支持AI和MCP](https://github.com/D4Vinci/Scrapling)

[opendataloader-pdf — OpenDataLab PDF数据加载器](https://github.com/opendataloader-project/opendataloader-pdf)

[airllm — 大模型内存优化，无注意力机制的LLM推理](https://github.com/lyogavin/airllm)

[supermemory — AI时代的记忆引擎](https://github.com/supermemoryai/supermemory)

[Vibe-Trading — AI驱动的金融交易框架](https://github.com/HKUDS/Vibe-Trading)

[fff — 最快最准的文件搜索工具，支持AI Agents和Neovim](https://github.com/dmtrKovalenko/fff)

#### 6月3日

[build-your-own-x — 511k Star! 从零构建你喜欢的技术](https://github.com/codecrafters-io/build-your-own-x)

[TradingAgents — Multi-Agents LLM 金融交易框架](https://github.com/TauricResearch/TradingAgents)

[MoneyPrinterTurbo — AI一键生成高清短视频](https://github.com/harry0703/MoneyPrinterTurbo)

[Scrapling — 自适应Web爬虫框架，支持AI和MCP](https://github.com/D4Vinci/Scrapling)

[heretic — LLM自动去除审查过滤](https://github.com/p-e-w/heretic)

[compound-engineering-plugin — Claude Code/Codex/Cursor的Compound工程插件](https://github.com/EveryInc/compound-engineering-plugin)

[oh-my-pi — AI Coding终端工具，Rust+TypeScript](https://github.com/can1357/oh-my-pi)

[hermes-webui — Hermes Agent的Web界面](https://github.com/nesquena/hermes-webui)

[supermemory — AI时代的记忆引擎](https://github.com/supermemoryai/supermemory)

[VoxCPM — 清华开源，多语言TTS和声音克隆](https://github.com/OpenBMB/VoxCPM)

[fff — 最快最准的文件搜索工具，支持AI Agents和Neovim](https://github.com/dmtrKovalenko/fff)


# 2026-05

## 第五周（5月25日—31日）

[OpenAI 发布 2026 年选举信息与安全措施](https://openai.com/index/election-safeguards-2026/)

OpenAI 介绍了面向选举信息查询、网络防御和 AI 内容来源核验的工作，并表示将扩展与可靠选举信息提供方的合作。相关措施是平台方公布的安排，不代表可彻底消除合成内容误导。

[OpenAI 发布前沿 AI 治理框架](https://openai.com/index/openai-frontier-governance-framework/)

框架公开说明 OpenAI 如何评估并缓解网络攻击、生物风险、有害操纵和失控等风险，也包括模型报告、安全管理和事件响应。文件是公司的自我治理框架，并非独立监管审计。

## 第四周

[Google I/O 2026 | 开发者主题演讲精华集锦 — AI 从辅助迈向独立处理复杂任务的智能体阶段](https://www.geekpark.net/news/364870)

[1年暴涨8倍！借力AI，存储大厂美光市值突破1万亿美元](https://www.geekpark.net/news/364872)

[打破光刻工艺束缚，华为提出「韬定律」](https://www.geekpark.net/news/364791)

[宇树科技将于6月1日接受科创板上市审核](https://www.geekpark.net/news/364791)

[不止于Copilot：医渡科技超级智能体，想做医疗界的Claude Code](https://www.geekpark.net/news/364838)

[谷歌CEO承认：Gemini 在 AI 编程赛道已落后](https://www.geekpark.net/news/364791)

[法拉利首款纯电动车 Ferrari Luce 发布](https://www.geekpark.net/news/364791)

[奥尔特曼改口：AI 对白领岗位的冲击没那么严重](https://www.aibase.com/zh/news/28393)

[Codex 自我蒸馏玩法爆火！让 Codex 自动扫描历史会话并打包成可复用工具](https://www.aibase.com/zh/news/28392)

[OpenAI 推理模型自主攻克80年难题：独立解决埃尔德什单位距离猜想](https://www.aibase.com/zh/news/28391)

[小鹏汽车推进人形机器人量产冲刺：计划2026年底量产，2027年进店导购](https://www.aibase.com/zh/news/28390)

[OpenAI 广告业务大转向：取消20万美元预付，全面拥抱中小商家](https://www.aibase.com/zh/news/28388)

[Google 将 SynthID 技术接入搜索与 Chrome：一键验证是否为 AI 生成](https://www.aibase.com/zh/news/28384)

[通义千问升级"拍照问健康"：能圈图、懂推理，三甲医生实测认可](https://www.aibase.com/zh/news/28379)

[MiniCPM-V 4.6 发布：仅1.3B参数的端侧多模态巅峰](https://www.aibase.com/zh/news/28378)

[Stability AI 发布 Stable Audio 3：长音频秒级生成](https://www.aibase.com/zh/news/28377)

[Uber 四个月烧光全年 AI 预算，高管质疑投入产出比](https://www.aibase.com/zh/news/28373)

[上海发布 AI 微短剧"沪8条"：最高千万资助，全流程 AI 化](https://www.aibase.com/zh/news/28374)

[高考考场不准作弊！国内主流大模型集体发声：期间将禁用拍题答疑](https://www.aibase.com/zh/news/28381)

[环球音乐与 TikTok 续签多年授权协议，AI 监管成为合作核心](https://www.aibase.com/zh/news/28380)

### GitHub 热门项目

[kimi-code — MoonshotAI 开源的下一代 Agent 起点，对标 Claude Code](https://github.com/MoonshotAI/kimi-code)

[awesome-architecture — 21 张架构地图（含 AI Gateway、RAG、Agent、推理服务等）+ 系统设计教程，中英文双语](https://github.com/study8677/awesome-architecture)

[DeepSeek-GUI — DeepSeek 模型的 AI Agent 工作区，内置 Code 和 Claw 模式](https://github.com/XingYu-Zhong/DeepSeek-GUI)

[codex-shim — 本地 Responses-API shim，让 Codex Desktop 接入自建模型](https://github.com/0xSero/codex-shim)

[ccglass — 查看 Claude Code / Codex / Kimi 等 Coding Agent 实际发送到模型的内容，本地代理 + Web Dashboard](https://github.com/jianshuo/ccglass)

[ai-memory — Agent Coding CLI 的长期记忆解决方案，支持不同 Agent 工具间的记忆交接](https://github.com/akitaonrails/ai-memory)

[FigMirror — 自动按任意论文的图表风格绘制你的数据，AI Agent 工具](https://github.com/VILA-Lab/FigMirror)

[PiD — NVIDIA 开源的快速高分辨率潜在解码器，基于像素扩散](https://github.com/nv-tlabs/PiD)

#### [Open Design — 开源 Claude Design 替代](https://github.com/nexu-io/open-design)

Open Design 的定位很清晰：把 Claude Design 这类“AI 生成设计稿 / 原型 / 演示 / 视觉资产”的能力做成 local-first 的开源桌面工具。它不是单纯的网页生成器，而是把 design system、skills、plugins、coding agent 串成一个本地设计工作流。

值得关注的点：

- 支持 web、desktop、mobile 原型，也能生成 slides、images、videos 等多种设计资产。
- 可以导出 HTML、PDF、PPTX、MP4，对“从想法到可交付物”很友好。
- 能接 Claude Code、Codex、Cursor、OpenCode、Qwen、Kimi 等 coding agent，适合做 AI 设计工作流中枢。
- 更像“AI 时代的 Figma 替代方向”：不是在画布上手动推像素，而是让设计系统和 agent 共同产出可运行的 artifact。

我的判断：这个项目值得持续跟踪。AI 编程工具已经很卷了，但“AI 设计 + 前端实现 + 可交付导出”的链路还没有完全跑通，Open Design 刚好踩在这个交叉点上。

#### [Headroom — AI 上下文压缩神器](https://github.com/chopratejas/headroom)

Headroom 解决的是 Agent 使用里的一个硬问题：工具输出、日志、文件、RAG chunk、历史对话太长，最后把 LLM context 撑爆，或者让成本和延迟飙升。它会在内容进入模型前做压缩，目标是用更少 token 保持同样的回答质量。

值得关注的点：

- 可以压缩 tool outputs、logs、files、RAG chunks、conversation history。
- 支持 library、proxy、MCP server 多种接入方式，不一定要改原项目代码。
- 强调 local-first 和 reversible compression，适合对隐私和可追溯性敏感的场景。
- 对 Claude Code、Codex、Cursor、LangChain 这类长任务场景很有价值。

我的判断：如果未来 coding agent 越来越依赖长日志、长 diff、长检索结果，那么“上下文工程”会成为基础设施。Headroom 这种工具很可能会变成 Agent Infra 的一层标配。

#### [Taste Skill — 给 AI 培养审美的前端 skill](https://github.com/Leonxlnx/taste-skill)

Taste Skill 不是一个普通 UI 组件库，而是一组给 AI agent 使用的前端设计 skill。它主要解决 AI 生成页面时常见的问题：布局无聊、留白混乱、字体层级弱、动效随意、整体看起来像模板站。

值得关注的点：

- 用 skill 的方式约束 AI 输出，让页面在 layout、typography、motion、spacing 上更像专业设计。
- 包含 greenfield 前端生成、已有项目 redesign、image-to-code、brandkit 等不同场景。
- 可以通过 `npx skills add` 安装，也可以直接把 `SKILL.md` 复制到项目或对话里使用。
- 对 Codex、Claude Code、Cursor 这类“能直接改前端代码”的工具尤其有用。

我的判断：这类项目说明 AI 前端开发已经从“能不能写出来”进入“写出来是否好看、是否有品味”的阶段。以后前端 agent 的竞争点会越来越多地落在审美、交互细节和设计一致性上。

#### [English-level-up-tips — 离谱的英语学习指南](https://github.com/byoungd/English-level-up-tips)

这个项目不是 AI 工具，但很适合放在科技热点里当“高质量学习资源”。它是一份面向中文读者的英语进阶指南，重点不是背几个单词，而是讲英语学习的方法、路线和长期训练思路。

值得关注的点：

- 内容偏系统学习，而不是碎片技巧。
- 对程序员、研究生、AI 从业者都有实际价值，因为很多一手技术资料仍然是英文。
- 英语能力本质上是信息获取能力，尤其在 AI、开源、论文、产品文档这些场景里非常明显。

我的判断：AI 时代更需要英语，而不是更不需要英语。因为 AI 可以帮你翻译，但你自己能直接阅读英文资料，依然意味着更低的信息损耗和更快的判断速度。

#### [ai-engineering-from-scratch — 从零手搓 AI 工程](https://github.com/rohitg00/ai-engineering-from-scratch)

ai-engineering-from-scratch 是一份非常系统的 AI 工程学习路线，强调 Learn it、Build it、Ship it。它覆盖数学基础、机器学习、深度学习、CV、NLP、Audio、Transformer、LLM、RAG、MCP、Agent Engineering 等主题，并且大量内容都偏“从原理到实现”。

值得关注的点：

- 不是只讲 API 调用，而是从底层原理和代码实现入手。
- 内容跨度很大，适合建立完整 AI 工程地图。
- 覆盖 LLM Engineering、MCP、Agent Engineering 等当前很实用的新方向。
- 对想从“会调包”进阶到“能理解系统、能造轮子、能做工程落地”的人很适合。

我的判断：这类项目的价值在于补齐 AI 工程师的基本功。现在很多 AI 应用看起来门槛很低，但真正做稳定、可评估、可扩展的系统，还是需要扎实理解模型、数据、推理、工具调用、上下文和部署链路。


## 第三周（5月11日—17日）

[Google 举办 Android Show：I/O Edition](https://blog.google/products-and-platforms/platforms/android/android-show-io-edition-2026/)

Google 预告 Android 系统向更深度的智能功能演进，并展示 Googlebook 等新设备形态和开发者功能，为随后 I/O 的 AI 与 Android 发布预热。

[OpenAI 更新 ChatGPT 对敏感对话的识别方式](https://openai.com/index/chatgpt-recognize-context-in-sensitive-conversations/)

OpenAI 表示，更新会结合对话中逐步出现的风险线索来调整安全回应，帮助区分日常交流和需要额外谨慎处理的情况。该能力涉及模型行为和安全策略，效果仍需要持续评估误报与漏报。

## 第二周（5月4日—10日）

[OpenAI 与 PwC 合作构建财务工作流 Agent](https://openai.com/index/openai-pwc-finance-collaboration/)

双方计划围绕预算、预测、采购、付款和财务结账等工作流开发企业 Agent，并把治理和人工监督纳入部署设计。合作尚处于推进阶段，公布的方案不等于已在所有客户场景验证。

[Google 汇总 4 月 AI 发布：Gemma 4、Deep Research Max 与 Cloud Next](https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-april-2026/)

Google 的月度回顾显示，4 月产品重点同时覆盖模型、研究 Agent、TPU 和企业 Agent 平台，竞争焦点从模型能力延伸至算力和完整部署工具链。

## 第一周（5月1日—3日）

[Microsoft Agent 365 正式商用](https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/)

Agent 365 为企业提供发现、观察和治理多来源 Agent 的控制层，并支持对独立身份和权限的 Agent 进行管理。它反映出企业从试用 AI 转向规模化部署后，管理 Agent 身份和活动成为新的基础需求。

# 2026-04

## 第五周（4月29日—30日）

[Google DeepMind 探索 AI 临床协作工具的研究路径](https://deepmind.google/blog/ai-co-clinician/)

这项研究讨论如何将 AI 用作临床人员的协作工具，覆盖问诊、信息整理和临床决策支持等环节。Google DeepMind 将其描述为研究与验证路径，不是可替代医护人员的独立诊疗产品。

## 第四周（4月22日—28日）

[Google Cloud Next 发布企业 Agent 平台与第八代 TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/next-2026/)

Google Cloud 将 Agent 开发、部署和管理作为大会重点，并公布第八代 TPU。大规模部署的成本、能耗和客户采用数据仍需要持续观察。

[OpenAI 发布 GPT-5.5](https://openai.com/index/introducing-gpt-5-5/)

GPT-5.5 面向编程、知识工作、计算机操作和多步骤任务。OpenAI 将其定位为能自行规划和使用工具的通用模型；API 于次日开放，具体表现仍应结合不同任务评测。

[DeepSeek 发布 DeepSeek-V4 预览版并开放权重](https://deepseek.com/en/news/v4-preview/)

V4 提供 Pro 和 Flash 两种版本，官方称二者均支持 100 万 token 上下文，并同步更新 API 与模型权重。模型基准和与闭源模型的比较来自 DeepSeek 自测，最终应用效果仍需第三方验证。

## 第三周（4月15日—21日）

[Google 发布 Deep Research 与 Deep Research Max](https://blog.google/innovation-and-ai/models-and-research/gemini-models/next-generation-gemini-deep-research/)

新版研究 Agent 增加 MCP 支持和原生可视化，面向长周期、多来源的资料分析任务。Google 将 Deep Research Max 定位为更强的长程分析工具，报告仍需用户核验来源和推理过程。

## 第二周（4月8日—14日）

[Google 更新 Gemini Robotics-ER 1.6](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-robotics-er-1-6/)

该模型面向机器人的空间理解、视觉推理和动作规划，4 月 14 日起可通过 Gemini API 和 AI Studio 供开发者试用。API 可用不代表模型已能在通用机器人上安全自主运行。

## 第一周（4月1日—7日）

[Google 发布开放模型 Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)

Gemma 4 面向本地部署、推理和 Agent 工作流，采用 Apache 2.0 许可。Google 介绍了其推理和多模态能力；本地可运行性仍取决于具体型号、量化方式和设备资源。

# 2026-03

## 第五周（3月29日—31日）

[OpenAI 宣布完成 1,220 亿美元融资](https://openai.com/index/accelerating-the-next-phase-ai/)

OpenAI 表示本轮融资承诺金额为 1,220 亿美元，并将资金用于算力、产品和企业服务扩张。公司同时公布用户与营收数据；这些数字来自公司披露，仍需结合后续财务信息理解。

[Anthropic 与澳大利亚政府签署 AI 安全合作备忘录](https://www.anthropic.com/news/australia-MOU)

双方计划开展模型能力与风险评估、与澳大利亚 AI 安全研究机构合作，并资助当地学术研究。合作着重让政府和独立研究者获得更多模型风险信息。

## 第四周（3月22日—28日）

[Google DeepMind 发布有关防范 AI 有害操纵的研究](https://deepmind.google/blog/protecting-people-from-harmful-manipulation/)

研究聚焦 AI 系统可能利用人的认知弱点施加影响，讨论识别和降低这类风险的方法。当前产品是否已普遍出现此类操纵，仍缺乏行业层面的系统统计。

[Salesforce AI Research 推出 AI Foundry](https://www.salesforce.com/news/stories/ai-foundry-announcement/)

AI Foundry 面向企业级智能体研究，讨论如何让多个 Agent 在企业系统中协同处理任务。其研究也把授权、监督和法律责任纳入自治 Agent 的设计问题。

## 第三周（3月15日—21日）

[OpenAI 发布 GPT-5.4 mini 和 nano](https://openai.com/index/introducing-gpt-5-4-mini-and-nano/)

这两款小模型面向代码、分类、数据提取和多模态工具调用等高频任务。轻量版本可以降低延迟与调用成本，但仍需按任务判断是否能达到大模型的可靠度。

[NVIDIA GTC 2026 集中发布 AI 基础设施与 Agent 软硬件](https://nvidianews.nvidia.com/online-press-kit/gtc-2026-news)

大会展示 Vera Rubin 平台、面向 Agent 的 CPU 与存储系统，以及 NemoClaw 和开放模型计划，反映产业投入正从单一 GPU 扩展到算力、网络、存储和运行时的整套基础设施。厂商路线图与量产交付时间仍需分别看待。

## 第二周（3月8日—14日）

[微软发布 Microsoft 365 E7 Frontier Suite 与 Agent 365 计划](https://blogs.microsoft.com/blog/2026/03/09/introducing-the-first-frontier-suite-built-on-intelligence-trust/)

微软把 Copilot、Agent 管理和企业安全能力组合为新的企业产品方案，并将 Agent 365 定位为管理和治理 Agent 的控制层。企业 Agent 数量增加后，可见性、身份权限和审计将成为基础设施的一部分。

## 第一周（3月1日—7日）

[苹果发布 iPhone 17e 和搭载 M4 的 iPad Air](https://www.apple.com/newsroom/2026/03/apple-introduces-iphone-17e/)（[iPad Air](https://www.apple.com/uk/newsroom/2026/03/apple-introduces-the-new-ipad-air-powered-by-m4/)）

苹果于 3 月初连续公布多款设备更新。iPhone 17e 使用 A19 芯片，苹果称其 Neural Engine 面向大型生成模型进行了优化；这也让设备端 AI 能力成为入门机型更新的一部分。

# 2026-02


## 第四周（2月22日—28日）

[Anthropic 称发现针对 Claude 的大规模蒸馏活动](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks)

Anthropic 表示，三家 AI 实验室通过约 2.4 万个虚假账号与 Claude 进行超过 1,600 万次交互，试图提取模型能力用于训练。蒸馏本身是常见且合法的模型训练方法；争议焦点在于数据获取方式、服务条款和授权边界，相关指控应视作 Anthropic 的公开陈述。

## 第三周

[如何在1-2年内成为某个领域的专家](https://www.zhihu.com/question/604298189/answer/2007008280740925555?share_code=WLPxaFrQC5XT&utm_psn=2008169961105929223)

[bun 1.3来了，替代npm](https://mp.weixin.qq.com/s/qy9oGEHLx18JGBjg8Ryi-w)

[gemini 3 是最强模型吗](https://www.zhihu.com/question/1975199818042327496/answer/2006490495979909971?share_code=L8GWWeZim4Y4&utm_psn=2006813374617510293)

[国产小龙虾开源！网易有道开源 LobsterAI：国产 Agent 的"真·干活"时代来了！](https://mp.weixin.qq.com/s/mB2ru7MUOCyVWeh-YBO6ww)

## 第二周

[一个视频看完ClaudeCode过去几个月重大更新](https://www.bilibili.com/video/BV1YgzTBTEEG?-Arouter=story&buvid=XXEAF42E0D12CAAB7A17180004AFD47D57D49)

[Agent Infra: Sandbox技术和选型](https://zhuanlan.zhihu.com/p/1999938129465979624?share_code=v0vwE98ByUpm&utm_psn=2006043128814126180)

[我与agent的2025](https://zhuanlan.zhihu.com/p/2005799834565755820?share_code=112LHNaDLvPR&utm_psn=2005986208887628599)

[多智能体系统：基于A2A协议实现AI智能体编排](https://zhuanlan.zhihu.com/p/2005705701478114362?share_code=ggwj41jYcBxy&utm_psn=2005985492290791362)

[为啥coze和dify这种llmops没热度了，是不是没必要部署了？ - Jayhow的回答 - 知乎]([text](https://www.zhihu.com/question/1953809252960407580/answer/1998778960763455230))

[ai 排行榜](https://www.zhihu.com/question/1975199818042327496/answer/2006490495979909971)

[cursor trae 比较](https://www.zhihu.com/question/1946791222762014096/answer/2004939008887787533?share_code=12Ze0cu2iZ7bn&utm_psn=2005369288580690949)

[如何评价anthropic在可解释性方面工作？](https://www.zhihu.com/question/1911022705769152635/answer/2004915744811529185?share_code=PdvaGU5GgFcL&utm_psn=2005367305350169225)

## 第一周

[trae](https://zhuanlan.zhihu.com/p/1999437027184230530?share_code=2G6xSHltIClx&utm_psn=2004469742006706443)

[trae](https://zhuanlan.zhihu.com/p/2001972320089167419?share_code=1k8f0nCNvMQCo&utm_psn=2004471921446769732)



# 2026-01


## 第五周


[agent 入门指南](https://zhuanlan.zhihu.com/p/1995813479794353043?share_code=bl8f9GqJ9csl&utm_psn=1997781967228401056)

[Coze 2.0 Skill ](https://mp.weixin.qq.com/s/xcT-buTknDmCKaEEatn0Pg)

[什么样的行为极大的改善了你的心理健康？](https://www.zhihu.com/question/1937991623154852740/answer/1976405280599326735?share_code=FpaAr61Z9rij&utm_psn=1997964778161854228)

[模糊搜索插件, claude LSP的增强](https://github.com/wsdjeg/picker.nvim)

[未来程序员的展望](https://www.zhihu.com/question/1962476460834031068/answer/1998496081793812142?share_code=15y8wxP2dsSKF&utm_psn=1998498556911322652)

[RankCoT 用排序思维链 + 自反思，提升 RAG 性能上限](https://www.zhihu.com/pin/1998023052370407583?native=1&scene=share&share_code=6ALccC6vCcyP&utm_psn=1998543061576349216)

[一人开发者的技术路线  作战地图](https://github.com/XiaomingX/indie-hacker-tools-plus)

[给AI编码智能体用的简单开放格式](https://github.com/agentsmd/agents.md)

[notebooklm的使用技巧](https://www.bilibili.com/video/BV1FXvfBREHe?-Arouter=story&buvid=XXEAF42E0D12CAAB7A17180004AFD47D57D49&from_spmid=tm.recommend.0.0&is_story_h5=false&mid=6gzusIP5Ek7I2qEGhVKy2g%3D%3D&plat_id=163&share_from=ugc&share_medium=android&share_plat=android&share_session_id=1478c7f3-d64e-42dc-af3c-1f8e9017678f&share_source=WEIXIN&share_tag=s_i&spmid=main.ugc-video-detail-vertical.0.0&timestamp=1769273755&unique_k=VYz6aid&up_id=3546884870244925)

[GroupViT 深度剖析：如何仅用文本监督实现零样本语义分割？](https://zhuanlan.zhihu.com/p/1998719498753160269?share_code=1v3jC5ApjaBo&utm_psn=1998740189334507614)

[如何自己做一个类似claude code 的agent](https://zhuanlan.zhihu.com/p/1998443272360710794?share_code=15K3kMgw4yn0C&utm_psn=1998743450040944249)

[阿里开源Qwen3-tts](https://mp.weixin.qq.com/s/gVQrVAWzSJ1VnrwkHKfCJA)

[让多个agent同时帮你干活](https://github.com/eigent-ai/eigent)

[RAG、LangChain、Agent 到底有什么关系？](https://www.zhihu.com/question/2495164206/answer/23805726342?share_code=UXjNKS0GhEuL&utm_psn=1998782570024957157)

[人生问答提示词](https://mp.weixin.qq.com/s/DKEMNX76RHbNtpoqUawv9A)

[大模型方面的推荐书籍](https://www.zhihu.com/question/13137834509/answer/1996602577983406520?share_code=7KHEzH8sW6eY&utm_psn=1998853367041118867)

[Agentic Memory 思考](https://zhuanlan.zhihu.com/p/1998702974571152503?share_code=6w2szgzNwn38&utm_psn=1999039893146462061)

[Clawdbot - 会进化,可以通过聊天工具接入的个人助手](https://mp.weixin.qq.com/s/7GZxu1i4AGJ5S0uCkJyVig)[github](https://github.com/clawdbot/clawdbot)

[antigravity 使用方式 -- 摆脱地域限制](https://zhuanlan.zhihu.com/p/1997232428591371625?share_code=FMxaZnVntu1c&utm_psn=1999205420162627540)

[可视化杀进程](https://www.zhihu.com/pin/1994591422993688206?native=1&scene=share&share_code=ZjulDozgxule&utm_psn=1999213479769445468)

[Everything Claude Code  -- 如何正确使用claude code](https://mp.weixin.qq.com/s/hBShK-aD0KQpkGz43TPTgQ)[另一篇文章](https://zhuanlan.zhihu.com/p/1997978582736204425?share_code=4akMY0oPbvBS&utm_psn=1998498080161538735)

[谷歌"可编程搜索"要变天了](https://mp.weixin.qq.com/s/xBvW9NNJEg8iSnbnVyEyGQ)

[Mistral 发布 ocr 3 提高手写以及结构化文档识别准确率](https://mp.weixin.qq.com/s/h7CH6VE_W4I229dqG7K7yQ)


[使用agent 搞定ocr - 吴恩达](https://mp.weixin.qq.com/s/BzhG5cq2wizdHnJHYbaaLA)[课程地址](https://www.deeplearning.ai/short-courses/document-ai-from-ocr-to-agentic-doc-extraction/)

[什么是lovable](https://blog.logto.io/zh-TW/lovable-logto-auth)

[agent 未来的展望](https://mp.weixin.qq.com/s/v33WXh-qBSqps-pPddxXXg)

[大模型上下文优化方法](https://mp.weixin.qq.com/s/Kg5oiN4LUWPDuW6ngTlP5A)

[claude LSP插件](https://mp.weixin.qq.com/s/6irUretbQVnwM5epUk4frg)

[把github项目封装成为一个skills - 以youtube下载为例](https://mp.weixin.qq.com/s/JER462B3dVYlwVYl6rTmzw)

[OCR模型 LightOnOCR-2-1B](https://mp.weixin.qq.com/s/ptTmYm-TJaFMculcIlFgzQ)

[一个被忽视的prompt是复制粘贴](https://mp.weixin.qq.com/s/jlpaO-piFqvnxAgVJ47wyw)




## 第四周

[banana slides](https://zhuanlan.zhihu.com/p/1989349474322108982)[github](https://github.com/Anionex/banana-slides)

[gemini 本地反代](https://github.com/cliouo/aistudio-build-proxy-all)

[claude code 技术原理](https://www.zhihu.com/question/1920949805166858531/answer/1926373954517444345?share_code=vEroR7UkBCRf&utm_psn=1997255059692623213)

[Ralph Loop](https://mp.weixin.qq.com/s/bKd9Z57DoJZC1oq1pLrNHA)
[github](https://github.com/snarktank/ralph?tab=readme-ov-file)

[solidquene 替代redis](https://mp.weixin.qq.com/s/qcxn9LRQV4l0RCbskSetxg)

[让ai通过json生成UI代码](https://mp.weixin.qq.com/s/_5C9zv1ETZYXArXGKkrB7Q)

[滑块验证码破解机制](https://www.zhihu.com/question/287191234/answer/1925877980816713052?share_code=ZiZLVu08z1V9&utm_psn=1997222492343914583)

[planning-with-files 做技术预研](https://zhuanlan.zhihu.com/p/1996159235571087230?share_code=eazo9XwLnksF&utm_psn=1997028579922444851)

[Chat2DB - AI数据库连接客户端](https://github.com/CodePhiliaX/Chat2DB)

[nano banana  做ppt生成的提示词](https://zhuanlan.zhihu.com/p/1977185306399762070)  

提示词: 极简商务演示风格，苹果发布会美学，大量留白，干净的无衬线字体，高端摄影图，网格布局，Helvetica字体，4k分辨率，超干净背景。

[ai agent 记忆体系分类](https://zhuanlan.zhihu.com/p/1985435669187825983?share_code=MGCCA9B6mhU9&utm_psn=1996501582125228373)

[claude code 的设计模式解析](https://github.com/shareAI-lab/learn-claude-code)

[现代大模型一般采用哪些技术框架](https://www.zhihu.com/question/667226672/answer/1996320972941305569?share_code=UtmmRrYo9G3B&utm_psn=1996505533277045877)

[如何一天修改你的人生 - 鸡汤文学](https://zhuanlan.zhihu.com/p/1996049853562786218?share_code=1jqDmMhRinwbu&utm_psn=1996862846630393332)

[claude cowork平替](https://mp.weixin.qq.com/s/9TQfGuRfVIE5IBIAD6WN8g)

[nanobanana 生成ppt](https://zhuanlan.zhihu.com/p/1976238610337521748)

[deepseek mHC](https://zhuanlan.zhihu.com/p/1996653743056393440?share_code=1fhjuA2MGUDPE&utm_psn=1996975644815402549)

## 第三周

[google translateGemma - 先进的翻译模型](https://mp.weixin.qq.com/s/GtwrZjLd2V7PJ9wMAxZEiA)
[claude code templates -- 给claude code的提示词 保证相应准确](https://github.com/davila7/claude-code-templates)

[claude code skills](https://zhuanlan.zhihu.com/p/1995802528294646467?share_code=Et3BCY9CDni3&utm_psn=1996163291421114646)

[垂直ai agent落地](https://zhuanlan.zhihu.com/p/1994124775983970078?share_code=1kQtqEr4P62o8&utm_psn=1995864694217519537)
[Windows自动化软件zTasker - 定时软件](https://mp.weixin.qq.com/s/a4hA-MdY3MujwXyNE13bUw)


[优雅的打印日志](https://mp.weixin.qq.com/s/uuE31DPndh4OU5miYlaEmA)

[程序员需要学习的长青技能](https://www.zhihu.com/question/658581470/answer/3537010340?share_code=13LxuIBhw5qmK&utm_psn=1994135294623097989)

[使用ai生成ppt和科研绘图](https://mp.weixin.qq.com/s/EvYW0-2xXBHsUawEcNuVMQ)

## 第二周

[开源 Skills -- 让ai模仿manus的思考计划执行](https://mp.weixin.qq.com/s/xcdMQU0Ab7-dEfNHre7_4A)  --- [github](https://github.com/OthmanAdi/planning-with-files/tree/master)

[大模型推理框架，SGLang和vLLM有哪些区别？](https://www.zhihu.com/question/666943660/answer/1914348903668651349?share_code=h9km3fx6Orp5&utm_psn=1992517491310731858)

[曾对AI嗤之以鼻，如今2周生成7万行代码：Rust大佬与Claude联手打造新语言Rue](https://zhuanlan.zhihu.com/p/1992184161176396135?share_code=KmCtV9l4Zdpe&utm_psn=1992543254135198132)

[claude skills](https://zhuanlan.zhihu.com/p/1992416332776498488?share_code=ghBLWee96a06&utm_psn=1992675370751788552)

[恭喜你! 发明了 [最强] RAG测试工具](https://www.bilibili.com/video/BV1btmYBFE9L/?share_source=copy_web&vd_source=05dd0ef7887b6a935d77cde96e5a7d4b)

[Deeptutor ai帮助学习](https://mp.weixin.qq.com/s/uiovqvQlhDY2oZy-WUdiKA)

## 第一周

[autoclaude](https://github.com/AndyMik90/Auto-Claude)

[google ai studio使用教程](https://zhuanlan.zhihu.com/p/1977832770446320894?share_code=I7X3192NaNcj&utm_psn=1990033509985837570)

[deep agent](https://zhuanlan.zhihu.com/p/1979938537802597911?share_code=SJW9la3F9HpO&utm_psn=1990116568189919279)

[把 antigravity模型偷出来](https://www.bilibili.com/video/BV1c5vfBQEuN/?buvid=XXEAF42E0D12CAAB7A17180004AFD47D57D49&from_spmid=dt.dt.video.0&is_story_h5=false&mid=6gzusIP5Ek7I2qEGhVKy2g%3D%3D&p=1&plat_id=114&share_from=ugc&share_medium=android&share_plat=android&share_session_id=1649104f-2c07-4db5-83e5-1f0a09c1cd11&share_source=WEIXIN&share_tag=s_i&spmid=united.player-video-detail.0.0&timestamp=1767344255&unique_k=dx1DokC&up_id=46377861)

[whisper加速](https://mp.weixin.qq.com/s/1YpL7r-_L2tmEpyeKLSyTA)

[easy vibe](https://mp.weixin.qq.com/s/8ag9l96iXy5uyM38ZQA3ow)

[1.5K Star！GitHub 开源神器 LifeTrace，帮你找回消失的记忆与时间-- 屏幕记录工具，和我之前的想法一样](https://mp.weixin.qq.com/s/Err7QrrgaMKYqd39TiJuiw)

[11.2K Star！AI编程Agent的"赛博包工头"来了，Vibe Kanban让效率再翻 10 倍！-感觉和autoclaude类似](https://mp.weixin.qq.com/s/umgH2sbsgxGFhZonjROnIg)

[Qwen-Edit-2511](https://www.bilibili.com/video/BV1hqicBCE9N?buvid=XXEAF42E0D12CAAB7A17180004AFD47D57D49&from_spmid=dt.dt.video.0&is_story_h5=false&mid=6gzusIP5Ek7I2qEGhVKy2g%3D%3D&plat_id=114&share_from=ugc&share_medium=android&share_plat=android&share_session_id=beae95ce-b321-4bb3-9c21-3a7dcd5f04d5&share_source=WEIXIN&share_tag=s_i&spmid=united.player-video-detail.0.0&timestamp=1767450382&unique_k=A554YYB&up_id=78652351)

