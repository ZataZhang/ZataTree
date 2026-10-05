---
title: "Agent 做视频开源盘点：五条路线、一份真实清单，和它漏水的三处"
description: "把 GitHub 上「让 Agent 自己做完一条视频」的开源系统按技术路线清点，并直接下钻到仓库内部：OpenMontage 的 2143 个文件与 269 行 pipeline manifest 原文、video-use 的 12 条 Hard Rules、HyperFrames 的确定性渲染承诺、1502 行供应商成本表换算出的每条片子多少钱，以及三个项目 issue 里暴露的架构级裂缝。star / push / 许可证 / 文件树均为 2026-10-05 一手核对。"
date: 2026-10-05T16:08:40+08:00
weight: 40
slug: "agentic-video-production-landscape"
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - Agent 工程实战
    - Agent Skills
    - AI-Video
    - Video-Production
    - Remotion
    - MCP
    - Claude-Code
toc: true
draft: false
---

`calesthio/OpenMontage` 的 README 第 416 行写着这么一句：

> OpenMontage uses an **agent-first architecture**. There is no code orchestrator. Your AI coding assistant IS the orchestrator.

翻译过来是：这套系统里**没有编排代码**，跑在你终端里的 Claude Code / Cursor / Codex 本身就是编排器。仓库 63.4k star、AGPL-3.0、最后一次 push 是 2026-10-03（一手，GitHub API 现查）。

这句话让我有点手痒。如果编排逻辑真的不在代码里，那它一定在别的地方——那就得看看那个「别的地方」到底长什么样，是几句 markdown 提示词，还是另有结构。所以我没有停在 README，而是把仓库的文件树、一份流水线清单原文、一份阶段手册原文、以及那份 1502 行的供应商成本表都拉下来看了一遍，最后翻了一圈 issue 找它哪里漏水。

这篇就是这条线上的清点结果：**五条路线、一份真实清单、三处裂缝**。

## 先划清那道工程鸿沟

「能生成一段视频」和「能做完一条视频」之间隔着一长串步骤。拿一条 60 秒的科普片举例，真实清单是：

选题 → 查资料 → 收敛观点 → 写脚本 → 设计分镜 → 生成或检索素材 → 配音 → 选 BGM → 剪辑 → 字幕 → 转场与动画 → 混音 → 渲染 → 质检 → 导出。

**文生视频模型只解决「生成素材」这一格。** 剩下十四格要么没人管，要么散在五个工具里。所以「Agentic Video Production」这个方向的实质不是换个更强的模型，而是有人去补那十四格——补法不同，就分出了下面的路线。

信源分级沿用我[《Agent 自进化开源盘点》]({{< relref "post/Agent 工程/02-框架与运行时/Agent 自进化开源盘点：什么能跑什么在腐烂/index.md" >}})里定的规矩：**一手**是我直查了 GitHub API、仓库文件树或 README 原文；**转述**只在二手渠道看到、没连上原始出处；**未核**的不作为论据。star / push / 许可证 / `created_at` 统一是 **2026-10-05** 从 GitHub API 拉的，文件树来自 `git/trees?recursive=1`，引文来自 `raw.githubusercontent.com`。

还有一件事：这条路线我不是只读文档。我把 `heygen-com/hyperframes` clone 下来读了它的契约与 lint 规则，另外按它 README 描述的写法**手写了一个 924 行的等价实现**（HTML 时间轴 + 逐帧 seek 渲染器 + FFmpeg 编码），用它渲了一条 50 秒竖版解说片，并且真的去验证了「同输入同输出」这句话——**结果第一遍没通过，第二遍查出了原因**，完整过程在「确定性实测」那一节。凡是没跑过的我仍然会标明。

## 这条赛道的时间形状

先把 `created_at` 排一下序，再看每天的 star 增速（增速 = 现 star ÷ 建仓天数，截至 2026-10-05，一手）：

| 仓库 | 建仓 | star | 增速/天 | 路线 |
| --- | --- | --- | --- | --- |
| `harry0703/MoneyPrinterTurbo` | 2024-03-11 | 128,528 | 137 | 关键词→成片 |
| `showlab/MovieAgent` | 2025-03-07 | 366 | 0.7 | 论文 |
| `HKUDS/ViMax` | 2025-03-30 | 12,547 | 23 | 多 Agent 管线 |
| `ATH-MaaS/Pixelle-Video` | 2025-11-07 | 28,640 | 86 | 关键词→成片 |
| `luoluoluo22/jianying-editor-skill` | 2026-01-24 | 3,741 | 15 | 剪辑 |
| `FireRedTeam/FireRed-OpenStoryline` | 2026-02-07 | 3,457 | 14 | 剪辑 |
| `heygen-com/hyperframes` | **2026-03-10** | 56,932 | 272 | 视频即代码 |
| `GVCLab/CutClaw` | **2026-03-18** | 978 | 5 | 剪辑（论文） |
| `calesthio/OpenMontage` | **2026-03-29** | 63,423 | **334** | Agent 即控制平面 |
| `browser-use/video-use` | 2026-04-12 | 28,056 | 159 | 剪辑 |
| `Vincentwei1021/video-shotcraft` | 2026-07-19 | 10,310 | 132 | 视频即代码 |

两个信息量很大的数：

**拐点在 2026 年 3 月。** HyperFrames（03-10）、CutClaw（03-18）、OpenMontage（03-29）在 19 天内先后建仓，三条不同路线同时起跑。这不像是互相抄，更像是某个约束同时松掉了——生成模型 API 的价格和稳定性刚好跨过「能被编排」的门槛。

**增速差两个数量级。** OpenMontage 334/天、HyperFrames 272/天，是 MoneyPrinterTurbo 两年半平均增速的 2 到 2.4 倍；而同一周建仓的论文向项目 CutClaw 只有 5/天。同一股风里，工程可跑的和只有论文的，被市场区别对待得很干脆。

## 路线一：Agent 就是控制平面

### 仓库解剖：1098 个 Markdown 对 539 个 Python

先看体量（一手，`git/trees?recursive=1`，共 2,143 个文件）：

| 类型 | 数量 | 说明 |
| --- | --- | --- |
| `.md` | **1,098** | `.agents/skills` 578 + `.claude/skills` 326 + `skills/` 157 + 其余 37 |
| `.py` | 539 | 工具实现、registry、schemas、tests |
| `.html` | 95 | Remotion 之外的模板与 Backlot 看板 |
| `.tsx` | 56 | `remotion-composer/` 里的场景组件 |
| `.yaml` | 22 | 13 个流水线清单 + 6 个风格 playbook + 若干 |
| `.mp3` | 38 | 示例音频 |

**文档比代码多一倍。** 这不是「README 写得长」，而是整个编排层就是用文档写的。README 里那句 "700+ agent skill and production-knowledge files" 其实还**说少了**——光 `.md` 就 1,098 个，最大的单个文件是 `.agents/skills/vercel-react-best-practices/AGENTS.md`，**98,263 字节**。

另一个细节：这些知识文件是**按宿主复制的**。仓库里同时有 `.claude/`（428 个 skill 文件）、`.agents/`（995 个）、`.codex/`（4 个）、`.cursor/`（3 个）四套目录，上面那个 98KB 的 `vercel-react-best-practices/AGENTS.md` 在 `.claude/skills/` 和 `.agents/skills/` 里各存一份，字节数完全相同。**所以「skill 可移植」这件事，目前还是靠复制目录实现的**——这跟容器镜像早期的分发问题有点像。

`tools/` 那 199 个文件的分布也值得一看，它就是那双手的解剖图：

```text
tools/video 67 · graphics 37 · audio 25 · analysis 15
      _kling 9 · _comfyui 7 · enhancement 7 · avatar 6
      capture 4 · provider_contracts 4 · character 2 · publishers 2
```

注意 `provider_contracts/` 只有 4 个文件，而 `video/` 有 67 个：**供应商抽象层薄，具体适配器厚**。这是所有接了一堆模型 API 的项目共同的形状。

### 一份真实的 pipeline manifest 长什么样

这才是「流程合同」的正文。`pipeline_defs/animated-explainer.yaml`，269 行，我挑关键段：

```yaml
name: animated-explainer
version: "2.0"
category: generated
stability: production
default_checkpoint_policy: guided

orchestration:
  mode: executive-producer
  skill: pipelines/explainer/executive-producer
  budget_default_usd: 2.00
  max_revisions_per_stage: 3
  max_send_backs: 3
  max_wall_time_minutes: 20

required_skills:
  - pipelines/explainer/research-director
  - pipelines/explainer/proposal-director
  - pipelines/explainer/script-director
  - pipelines/explainer/scene-director
  - pipelines/explainer/asset-director
  - pipelines/explainer/edit-director
  - pipelines/explainer/compose-director
  - pipelines/explainer/publish-director
  - meta/reviewer
  - meta/checkpoint-protocol
  - meta/animation-runtime-selector
  - meta/voice-performance-director
```

九个阶段 director + 一堆 meta 技能，编排模式叫 executive-producer（执行制片人），预算默认 **2 美元**，每阶段最多返修 3 次、最多打回 3 次、整片最多 20 分钟墙钟时间。

再看单个阶段的定义，这是我觉得真正值得抄的地方：

```yaml
  - name: research
    skill: pipelines/explainer/research-director
    produces: [research_brief]
    checkpoint_required: false
    human_approval_default: false
    review_focus:
      - Content landscape mapped with at least 3 existing pieces
      - Data points are specific and sourced, not vague
      - Audience questions sourced from real forums, not invented
    success_criteria:
      - Schema-valid research_brief with at least 3 data_points
      - At least 5 sources cited with URLs

  - name: proposal
    produces: [proposal_packet, decision_log]
    checkpoint_required: true
    human_approval_default: true
    review_focus:
      - Production plan reflects actual tool availability from preflight
      - Cost estimate is itemized and honest
      - Alternative production paths shown at different price points
    success_criteria:
      - cost_estimate has itemized line_items with per-tool costs
      - approval.status is "approved" or "approved_with_changes" before proceeding
```

`review_focus` 是**可检查的断言**，不是「注意质量」这种形容词：至少 3 个同类作品、观点必须来自真实论坛而不是编的、至少 5 条带 URL 的来源。`success_criteria` 是 schema 级门禁：审批状态不是 `approved` 就不许往下走。`proposal` 阶段还挂了一个 `sub_stages`，条件是存在视频分析简报时，先渲一段 **10–15 秒的样片**给人确认——**先看一眼小的，再烧大的**。

而 `budget_default_usd: 2.00` 这个默认值，配上后面的成本表就说得通了。

### 2 美元的默认预算不是随便写的

`docs/PROVIDERS.md` 有 1,502 行，是一份带单价的供应商账本（一手）。免费档从低到高排：

| 档位 | 花费 | 解锁什么 |
| --- | --- | --- |
| Pexels + Pixabay | **$0** | 库存图片与视频，够出基础片 |
| Piper（本地装） | **$0** | 完全离线 TTS，无 key、无网络 |
| Google API key | **$0** | 700+ 音色 TTS，1M 字符/月免费 |
| ElevenLabs | **$0** | 高级 TTS + 音乐 + SFX，10K 字符/月 |
| 本地视频生成 | **$0 + GPU** | WAN 2.1、Hunyuan、CogVideo、LTX |
| fal.ai | ~$0.03/图 | FLUX 图片 + Kling/Veo/MiniMax 视频 |
| Runway | $12/月 | Gen-4，最高画质 AI 视频 |

按秒计价的画面素材，差距非常陡：

| 模型 | 单价 | 1 美元能买 |
| --- | --- | --- |
| Kling 2.5 Turbo Pro | $0.07/秒 | 14 秒 |
| grok-imagine-video 720p | $0.07/秒 | 14 秒 |
| 即梦 3.0 Pro | ~$0.05/秒 | 20 秒 |
| **Veo 3** | **$0.40/秒** | **2.5 秒** |
| FLUX Pro v1.1（静帧） | $0.05/图 | 20 张 |

算一下就明白了：一条 60 秒的片子，如果每个镜头都由模型生成，**全用 Veo 3 光画面就是 $24，全用 Kling 是 $4.2**。而默认预算 $2.00 恰好等于 28 秒 Kling、或 5 秒 Veo、或 40 张 FLUX 静帧。也就是说，**这个默认值隐含的判断是：一条短片不该让模型逐秒生成画面**，应该是静帧 + 动效 + 库存素材为主，生成模型只补关键镜头。

这也解释了为什么 `documentary-montage.yaml` 那条流水线会存在——它从 Pexels / Archive.org / NASA / Wikimedia / Unsplash 建一个 CLIP 可检索语料库再剪，整条片子画面成本 $0，不碰任何付费生成 API。

成本表里还有两处态度我很喜欢：

> Unpriced calls return `cost_usd: null` with `cost_status`, not zero.

以及针对 Seedance 2.5 和自建端点：必须先手填 `custom_price_cny_per_million_tokens`，原文是 "unknown pricing is never treated as free"。**未知价格不许当成免费**——一个只做估价的工具最容易在这里骗自己。

### 一份真实的 stage director skill 长什么样

`skills/pipelines/explainer/asset-director.md`，290 行。开头是角色定义：

> You are the Asset Producer for a generated explainer video... **This is where plans become real files.** A missing or low-quality asset will torpedo the final video.

然后是「这个场景该用哪种动效」的路由表，节选：

| 场景类型 | 推荐做法 |
| --- | --- |
| 标题卡、淡入、滑入、缩放 | Remotion 原语 `interpolate()` + `spring()` |
| 词级字幕高亮跟旁白 | 已有的 `CaptionOverlay` 组件 |
| 逐字符 kinetic typography | GSAP SplitText → 读 `.agents/skills/gsap-plugins/SKILL.md` |
| 4 个以上 tween 的多步编排 | GSAP timeline → 读 `.agents/skills/gsap-timeline/SKILL.md` |
| 柱状/折线/饼图/KPI | Remotion 内置图表组件 |
| 终端或 CLI 演示 | Remotion TerminalScene |

配一句明确的偏向：

> **The keep-it-simple bias:** if Remotion primitives solve a scene in ≤ 20 lines, use them. Only pull in GSAP when the plugin genuinely earns its bundle weight.

**能用 20 行以内解决就别引插件**——这句是真正的「老师傅经验」，而它被写成了一个 Agent 每阶段必读的文件。 Prerequisites 表里还专门列了一行 `Cost tracker | tools/cost_tracker.py | Budget governance`：花钱的账本是一个前置依赖，不是事后统计。

### 三层的分工

README 自己画了这张图，看完全面再回头看就很准：

```text
Layer 1: tools/ + pipeline_defs/   "What exists" — 可执行能力 + 编排
Layer 2: skills/                   "How to use it" — 本仓库的规矩与质量线
Layer 3: .agents/skills/           "How it works"  — 外部技术的深度知识包
```

Agent 读 Layer 1 知道能干什么，读 Layer 2 知道该怎么干，读 Layer 3 补底层原理。而 Layer 1 的入口是两个函数，不是靠记忆猜：

```bash
python -c "from tools.tool_registry import registry; registry.discover(); \
  print(registry.support_envelope())"   # 我这台机器到底支持什么
python -c "... print(registry.provider_menu())"  # 供应商菜单
```

`support_envelope` / `provider_menu` 这两个函数名本身就说明态度：**先把可用能力摊开，再谈方案。**

### Backlot：把「Agent 说了什么」换成「剧组在干什么」

另一手是 `python -m backlot open` 打开的本地制片看板：阶段逐个点亮、脚本按剧本页排版、每个 provider 决策和每块钱都贴墙上，跑完能 **▶ REPLAY RUN** 按时间戳回放整次制作。更关键的是分镜表是一个**真的审批门**——素材生成会在逐场景的 contact sheet 上暂停，列出 take、prompt、单素材成本和质量分，让你在**渲染之前**而不是之后点头。

11 条流水线（Animated Explainer / Animation / Avatar Spokesperson / Cinematic / Clip Factory / Documentary Montage / Hybrid / Localization & Dub / Podcast Repurpose / Screen Demo / Talking Head）里，我另外注意到一个不一致：**tagline 说 12 条、README 表格列 11 条、`pipeline_defs/` 目录里有 13 个 YAML**（其中 `framework-smoke.yaml` 是冒烟测试，`character-animation.yaml` 没进表格）。数字不大，但**这类项目的宣传口径和目录状态不同步是常态**，选型的适合靠自己 `ls` 一遍。

### 同路线的其他玩家

| 仓库 | star | 许可证 | push | 特点 |
| --- | --- | --- | --- | --- |
| `HKUDS/ViMax` | 12,547 | MIT | 2026-09-30 | 港大，导演/编剧/制片/生成四合一；长剧本 RAG 拆分、参考图保一致性、VLM 校验首帧 |
| `HITsz-TMG/VideoClaw` | 1,839 | MIT | 2026-08-26 | 哈工大张民团队 + 阿里，"Chat an Idea. Get a Film." |
| `HKUDS/VideoAgent` | 1,919 | MIT | 2026-07-22 | EMNLP 2026，理解 + 剪辑 + 重制一体，按意图路由 |
| `video-db/Director` | 1,545 | MIT | 2026-01-23 | 挂在 VideoDB 后端上做 search/edit/compile/generate 推理 |
| `waooAI/waoowaoo` · `HBAI-Ltd/Toonflow-app` · `chatfire-AI/huobao-drama` | 14.4k · 16.5k · 15.7k | — | — | 国内短剧簇：先建角色/场景/道具资产库，再分镜生成 |

一个反常识观察：**短剧簇几乎都在同一个地方收口——导出剪映草稿**。不是做不到全自动，是大家都发现最后一刀还是要人挪，于是把「不锁死工作流」当成设计目标。video-shotcraft 也一样做了剪映工程导出（README 注明在 JianYing Pro 11.2 for macOS 验证过）。

## 路线二：视频即代码——确定性是入场券

HeyGen 的 `heygen-com/hyperframes`（56,932 star、Apache-2.0、push 2026-10-05，一手）口号是 "Write HTML. Render video. Built for agents."。做法是**把视频定义成 HTML**：

```html
<div id="stage" data-composition-id="launch" data-start="0" data-width="1920" data-height="1080">
  <h1 id="title" class="clip" data-start="1" data-duration="4" data-track-index="1">Launch day</h1>
</div>
```

`data-start` / `data-duration` / `data-track-index` 声明时间与轨道，动画接 GSAP、CSS、Lottie、Three.js、Anime.js、WAAPI 或自定义帧适配器。渲染器在无头 Chrome 里**逐帧 seek**再用 FFmpeg 编码，README 原话："the same input produces the same video"。

这句话才是重点。Agent 生成的东西本来就有随机性，如果渲染这一步也随机，就没有任何可复现性可言。**确定性渲染是把视频放进 CI 和回归测试的前提**，也是它能被 Agent 反复调用而不炸的原因。同类的 [Remotion](https://github.com/remotion-dev/remotion)（61,911 star）更早，但基于 React/TSX；HyperFrames 的卖点正是「不需要 React，没有私有时间线格式」，甚至给了 `/remotion-to-hyperframes` 这个单向迁移 skill。**对大模型来说，写合法 HTML 比写合法 TSX 稳**——这是这条路线存在的理由。

对 Agent 友好体现在 skill 层：仓库发布 **21 个按需加载的 skill**。`/hyperframes` 是路由兼能力地图，README 说它是 "the intent layer that confirms every creation brief up front"——先把需求确认一遍再动手；`/hyperframes-core` 写的是 composition contract 与 determinism 规则；`/hyperframes-cli` 是 `init / lint / check / snapshot / preview / render / publish / doctor` 这条开发闭环，外加 HeyGen 云渲染和 AWS Lambda 分布式渲染。**注意 `lint` 和 `check` 排在 `render` 前面：先静态过一遍，再花渲染时间。**

`Vincentwei1021/video-shotcraft`（10,310 star、Apache-2.0，一手）是这条路线上最好看的**经验资产化**样本，README 头一行就是数字：

> An agent skill for crafting cinematic product videos: **157 shot recipe cards · 214 styles · 214 motion previews** · a production-ready template

它把「电影感」拆成一张张可复用的镜头配方卡（2026-08 从 104 张扩到 152 张，从 209 个候选动效里筛出来），配线上 Gallery 逐个预览。Agent 的路径是 real page captures → 2.5D camera moves → beat-synced cuts → SFX → Remotion render，交付后打开一个 CapCut 式工作台让人接手，并且能导出剪映草稿。**卡片不是 prompt，是能版本管理的资产。**

## 路线三：剪辑 Agent——最成熟，也最「规矩化」

`browser-use/video-use`（28,056 star、MIT、push 2026-10-02，一手）一句话：原素材丢进文件夹，跟 Claude Code 聊几句，拿回 `final.mp4`。

先说体量：**整个仓库 36 个文件**（一手，git tree）。6 个 helper 脚本、一份 342 行的 `SKILL.md`、一份 `install.md`、一个 manim 子技能包（14 篇参考文档）、3 个测试文件。对比 OpenMontage 的 2,143 个文件——**两者都自称 agentic，体量差两个数量级**。所以「要不要一个庞大的知识仓库」取决于任务边界，而不是诚意。

它的核心洞察是 README 里这句：

> The LLM never watches the video. It **reads** it.

第一层是音频转写：每个素材一次 ElevenLabs Scribe，拿到词级时间戳、说话人分离，还有 `(laughter)`、`(applause)`、`(sigh)` 这类音频事件；所有 take 打包成约 12KB 的 `takes_packed.md` 作为主阅读视图。第二层是按需的视觉切片 `timeline_view.py <video> <start> <end>`，输出胶片条 + 波形 + 词标签 + 静音切口候选的 PNG——但 SKILL.md 特别警告它是 **"Not a scan tool — use it at decision points, not constantly"**。

真正说明「怎么做」的是 `SKILL.md` 里那 12 条 Hard Rules，而且**每条都带「否则会发生什么」**：

| 规则 | 原文要点 | 否则 |
| --- | --- | --- |
| 音频优先 | 切口候选来自语音边界与静音间隙 | 变成看图猜刀 |
| 每个段边界 30ms 淡入淡出 | `afade=t=in:st=0:d=0.03` | 每个切口都有爆音 |
| 绝不在词中间下刀 | 所有边缘吸附到词边界 | 吞字 |
| 每个切口加垫片，30–200ms | **Scribe 时间戳本身漂移 50–100ms** | 刀口偏移，掐头去尾 |
| 只用 word-level verbatim ASR | 不用 phrase/SRT 模式，不用去填充词的规范化结果 | 丢掉亚秒间隙数据和编辑信号 |
| 主 SRT 用输出时间线偏移 | `output_time = word.start - segment_start + segment_offset` | 拼接后字幕整体错位 |
| 转写按素材缓存 | 除非源文件变了不重转 | 白烧 API 额度 |
| 多动画并行子 Agent | `Agent` 工具一次开 N 个 | 串行，墙钟时间 N 倍 |
| 先出方案再动手 | 未确认前不碰切口 | 返工 |
| 全部产物写进 `<videos_dir>/edit/` | 绝不写进仓库目录 | 污染 skill 目录 |

这套规则的性质很说明问题：**它们不是理想流程，是踩过的坑的化石**。比如「字幕最后烧」写在 `render.py` 的职责顺序里（逐段抽取 → 拼接 → 叠层 PTS 移位 → **字幕放最后**），切口决策沉淀成 `edl.json`——用剪辑行业现成的 EDL 概念当中间产物，这样人和 Agent 改的是同一份东西。

而 SKILL.md 的元规则我很喜欢：

> **Artistic freedom is the default.** Every specific value, preset, font, color... in this document is a *worked example* from one proven video — not a mandate... **The only things you MUST do are in the Hard Rules section below. Everything else is yours.**

**把「必须」和「举例」明确分开**，是文档式编排最容易漏掉的一件事——不分开，Agent 会把每个示例值当规范照抄。

同路线还有一层「让 Agent 开真软件」的集成：

| 仓库 | star | 说明 |
| --- | --- | --- |
| `luoluoluo22/jianying-editor-skill` | 3,741 | Agent 操作剪映（写草稿工程） |
| `FireRedTeam/FireRed-OpenStoryline` | 3,457 | 把「手动剪辑」换成「表达意图」 |
| `diffusionstudio/editor` | 3,217 | "视频剪辑界的 VS Code"，配 WebCodecs 合成引擎 |
| `veedstudio/open-edit` | 1,511 | Veed 出的开源 Agent 剪辑管线 |
| `GVCLab/CutClaw` | 978 | 小时级长素材 + 音乐卡点的多 Agent 混剪（**无 LICENSE 文件**） |
| Premiere / Resolve MCP | — | `ayushozha/AdobePremiereProMCP`(1000+ 工具)、`samuelgursky/davinci-resolve-mcp`、`lordhoell/davinci-resolve-mcp`、纯 Bash 的 `wizenheimer/vibestudio` |

一个生态位判断：**HyperFrames 已经成了这条路线的动画后端**。video-use 的 SKILL.md 直接写「用 `npx --yes hyperframes ...` 调用」，Remotion 则 `npx create-video@latest` 就地脚手架；OpenMontage 在提案阶段就要在 Remotion 和 HyperFrames 之间二选一，选完锁进 `render_runtime` 字段。上层调度都在把「渲染合成」外包给路线二——**这层是目前最有复用价值的公共底座**（Pixo 那篇 50+ 流水线评测把 HyperFrames 单列为「基础设施层」，与此互证，转述）。

## 路线四：关键词→成片，但别叫它文生视频

`harry0703/MoneyPrinterTurbo` 是这条线上量最大的仓库：**128,528 star、MIT、push 2026-10-04**（一手）。它的真实管线是：LLM 写文案 → 按关键词去 Pexels / Pixabay / Coverr 匹配**库存素材** → TTS 配音（Edge TTS 免费无需 key）→ 字幕与 BGM → **FFmpeg 合成**。全程不生成一个新镜头。

所以适用面很清楚：口播解说、资讯、faceless 账号。Token 便宜、能铺量；指望它出原创镜头就选错了。

工程上它提供四种入口：**AI Agent / WebUI / API / CLI**。CLI 那条 `uv run python cli.py --batch-file ./tasks.json --stop-at video` 吃 UTF-8 的 JSON 数组或 JSONL，一单最多 100 条，所有条目在第一个任务起跑前完成参数与本地文件预检，单条失败不断流，跑完吐一份 `total / succeeded / failed / tasks` 汇总。**这是给无人值守设计的**——你不会跑到第九条才发现第三条的音频路径是错的。

Agent 入口的做法和 video-use 一模一样，值得单独注意：它在仓库里放了一份 `docs/skill/SKILL.md`，你把 raw URL 发给 Agent，Agent 就自己完成安装、配置和出片，只在缺 key 时才问一句。**「让 Agent 自己装自己」已经是这一代工具的标准交付方式了。**

同类：`ATH-MaaS/Pixelle-Video`（28,640 star）、`OpenCut-app/OpenCut`（92,401 star，开源剪映替代，本身不是 Agent 但常被当底座）、`krillinai/OpenCreator`（12,594 star，前身 KrillinAI）。

## 路线五：闭源 Agent 产品

不想自己搭就走这条。2026 年 5 月那几周节奏很密（**日期来自二手评测，转述**）：05-13 Runway Agent（对话式端到端制片）、05-19 Adobe 宣布 for-creativity connector 接入 Gemini、05-21 Aleph 2.0 + Edit Studio、**05-27 Runway MCP**——最后这条是关键：视频能力进了 Agent、编码工具和对话工作区。App Store 描述现在是 "just describe the video you want and let Runway Agent build the whole thing"（一手）。

另外几家：Adobe **Firefly AI Assistant**（官方 helpx 标为 beta，把构思/生成/编辑收进一个环境，一手）；Google **Flow + Veo 3.1**（原生同步音频）；HeyGen 除了 HyperFrames 还有一层 `heygen-com/skills`（466 star）走它的 Video Agent 管线。国产即梦、可灵的 agent 化程度低一档，主要还是模型 + 画布。

## 论文那一支：很多工程手法早有出处

- **MovieAgent**（NUS，arxiv 2503.07314）分层 CoT，模拟导演 / 编剧 / 故事板 / 场地经理。`showlab/MovieAgent` 仓库 366 star、**无 LICENSE 字段**、push 停在 2025-03-26——论文火，但代码不是给你用的。
- **FilmAgent**（SIGGRAPH Asia 2024）、**Anim-Director**、**AniMaker**（SIGGRAPH Asia 2025，MCTS 驱动候选片段生成）——哈工大那条线，VideoClaw 是它们的工程化收口。
- **EditDuet**（SIGGRAPH 2025，Adobe Research）Editor + Critic 双 Agent；**CutClaw** 的 Playwriter/Editor/Reviewer 三段是同一思路的开源版。
- **VideoGen-Eval** 是 agent-as-judge 的前置工作——上面每个项目的「自检」都在做这件事。

索引工具：`PhiloLabs/awesome-video-agents`（14 star，但分类最干净）按 All-in-One / 多 Agent 管线 / 剪辑 / 生成 / 理解 / NLE-MCP 六类整理；`zhuyansen/awesome-claude-video-skills` 收了 **180 个 Agent 视频 skill 并逐个做了安全评级（SAFE / CAUTION / pending）**（转述）。后者给了一个提神的数：**180 个仓库里 107 个不到 50 星，过 1000 星的只有 20 个左右**。按 star 排序选工具，大概率选错。

## 共同的骨架：四条，可以直接抄

把路线一到路线三并排看，收敛出的架构一模一样：

![Agent 做视频的共同骨架：流程合同、能力发现、质量门禁与检查点](images/index/skeleton.svg)

1. **流程合同化**。阶段、输入输出、成功判据写成 Agent 每轮都要读的 YAML/Markdown。`review_focus` 是可检查断言，`success_criteria` 是 schema 门禁——同一句话写在代码注释里没人看，写进 manifest 里就变成操作规程。这是「约束 Agent」和「祈祷 Agent」的分界线。
2. **能力发现前置**。给 Agent 一个 registry（`support_envelope` / `provider_menu`），让它先查「能用什么、多少钱、fallback 是什么」再提方案。幻觉调用大部分不是模型的错，是没人把可用面摊开。
3. **质量门禁 + 自检返工**。渲染完自己抽帧、测音频电平、查字幕、比对一致性，**不合格不许端上来**。预算也是门禁：先估价、有上限、超阈值单独审批。
4. **确定性优先**。能用代码化渲染就别靠模型抽卡。这条同时买到三样东西：可复现、可进 CI、可 Git diff。

## 三处漏水：issue 里看到的真实故障

上面那四条听起来很干净。但把三个项目的 issue 翻一遍，会发现这套架构**新长出了两类以前没有的 bug**。

**裂缝一：文档本身成了 bug 源。** HyperFrames 的 **#5025** 标题是 "Skills: 10 cross-skill contradictions and 11 wrong facts or broken paths"——有人核对那 21 个 skill，报出 **10 处互相矛盾、11 处事实错误或路径失效**（一手，未修复状态）。这和 OpenMontage 那 1,098 个 Markdown 是同一道题的两面：**当编排逻辑住在文档里，文档的一致性就是系统的正确性。**

这里我要更正自己一个判断。我原本写「代码有编译器，Markdown 没有」，读完官方仓库才发现这句话说过头了——它有 `packages/lint`，规则是具名的：`gsap_animates_clip_element`、`gsap_infinite_repeat`、`gsap_css_transform_conflict`、`standalone_composition_wrapped_in_template`、`gsap_timeline_registered_before_async_build`。**文档式契约的 linter 是写得出来的。** 但 #5025 报的 10 处矛盾它一条都不会响：那些是**跨文件的语义分歧**，不是单条可判定的规则。所以真正的分界线不是「有没有编译器」，而是**这条约束能不能被写成局部可判定的谓词**——能，就进 lint；不能，就只能靠人读，而人读的面积随文档数量线性增长。

**裂缝二：能力发现会说谎。** OpenMontage 的 **#637**："diagram_gen reports AVAILABLE without mermaid-cli and silently renders mermaid source"——registry 报告该工具可用，但依赖的 mermaid-cli 根本没装，于是它**静默降级**，把 mermaid 源码当画面渲染出来（一手）。这条正好打在「能力发现前置」这套设计的要害上：`support_envelope` 只检查了「我注册了什么」，没检查「这个能力真的跑得通吗」。**门禁的前提是探针诚实**，而探针最容易在缺依赖时选择继续。

**裂缝三：物理规律还是要还的。** video-use 定了「每个段边界 30ms 淡入淡出防爆音」这条 Hard Rule，#162 报的是 **AAC priming 在 `-c copy` 拼接时仍产生边界咔哒声**——淡入淡出解决不了编码器预热（一手）。同仓库 #118 是「按文档装的 macOS 上字幕烧录两种方式坏掉，其中一种是直接崩」，#125 是「Windows 非 UTF-8 stdout 下 helper 打印崩溃」，#206 是「同名素材批量转写互相覆盖」。video-shotcraft 的 #49（讨论最多的一条）要的是**局部帧重渲染与成片补丁**——改一个镜头不必重渲全片。

这三处合起来是一个判断：**这套架构的失败模式，从「代码崩溃」变成了「文档矛盾、门禁说谎、以及最后一公里编解码问题」。** 前两类是新问题，所以工具链还没跟上——没有 linter 能查 21 个 skill 之间的矛盾，也没有 CI 能验证 `AVAILABLE` 是不是真的可用。

还有一条值得单独拎出来，因为它不是技术问题：OpenMontage 的 **#626** 是一个安全公告——"fake 'OpenMontage-app' installer repo circulating"，**有假冒本项目的安装仓库在流传**（一手）。热门 Agent 工具已经出现供应链仿冒，而这恰恰是因为「把一段 URL 发给 Agent 让它自己装」成了标准交付方式：**你交付的是安装指令，而攻击者也可以。** 装之前先核对仓库归属，别把来路不明的 raw URL 直接贴给 Agent。

## 怎么选

| 你手上有什么 | 走哪条 | 具体 |
| --- | --- | --- |
| 有文章 / 有产品，要演示或宣传短片 | 路线二 | HyperFrames（Apache-2.0，无协议包袱）起步；要发布会质感上 video-shotcraft |
| 有实拍 / 口播原素材 | 路线三 | video-use，MIT，36 个文件，跟 Claude Code 用法天然契合 |
| 要「一句话→成片」的完整调度，或想研究架构 | 路线一 | OpenMontage（**AGPL-3.0，服务化必须开源**）；轻量些看 ViMax（MIT） |
| 要铺量、跑矩阵 | 路线四 | MoneyPrinterTurbo，但接受它是库存素材拼接 |
| 不想碰部署和 key | 路线五 | Runway Agent / Firefly AI Assistant / Flow |
| 预算接近零 | 路线一 + 路线四 | 库存素材 + Piper 本地 TTS + FFmpeg；或 Documentary Montage 那条 CLIP 检索线 |
| 只想把自己的文章变成口播视频 | — | 看[《用 AI 把文章做成口播视频》]({{< relref "post/开发工具链/05-AI 与创作工具/ai-article-to-video/index.md" >}})，那篇是创作 SOP，这篇是系统架构 |

**只有周末两小时的话**：别从 OpenMontage 开始（13 个 manifest、要配一堆 key）。从 video-use（有素材）或 HyperFrames（没素材）开始，两者都是 MIT/Apache、文件少、跑通一条片再决定要不要上编排系统。**这套东西的正确入门顺序是自下而上，不是先买剧组。**

## 几点收获

**「Agent 化」的真正内容是把行规写成文档。** 1,098 个 Markdown、157 张镜头卡、21 个渲染 skill，本质同一件事：把一个剧组靠经验判断的部分，翻译成 Agent 每轮必读的文本。而 video-use 那 12 条 Hard Rules 说明了另一半——**文档里必须区分「必须」和「举例」**，否则 Agent 会把示例值当规范照抄。

**没有调度器，比换个调度器更值得注意。** 传统做法是拿状态机画编排；OpenMontage 直接删掉中央编排器，把编排职责交给读得懂 manifest 的 LLM。代价是可预测性变差，所以它必须用 schemas、contract tests、checkpoint、`max_send_backs: 3`、`max_wall_time_minutes: 20` 把这些不确定性一圈圈钉回来。**这套「用文档编排」的取舍比视频本身更通用**——任何长流程 Agent 应用都会撞上同一道题。

**文档规模到一定量级，它自己就成了最大的 bug 面。** 这是我看完 #5025 之后改的主意。我原本以为「700 个 skill 文件」是纯粹的加分项，但 21 个 skill 就能被查出 10 处矛盾，1,098 个 Markdown 的漂移面积可想而知。更正一处：我原以为这条路线缺的是 linter，读完官方仓库发现 `packages/lint` 已经存在且规则具名——**所以缺口不在工具，而在约束的性质**：单文件内可判定的违规能被拦住，跨文件的语义分歧拦不住。这条路线接下来真正的竞争，是看谁先找到「跨文档一致性」的可判定子集，把它也做成 lint。

**确定性是入场券，不是加分项。** HyperFrames 全部设计（逐帧 seek、无构建步骤、lint 在 render 前）都在买这一件事。视频模型给的是概率，渲染层如果也给概率，这个流水线永远进不了 CI，也永远说不清「昨天那版是怎么出来的」。

**成本表是架构的一部分。** `budget_default_usd: 2.00` 之所以是 2 美元，因为 Veo 3 要 $0.40/秒。不懂这层价格结构，就会设计出「60 秒全镜头生成」的必然破产方案。**「未知价格不当作免费」这条工程纪律，比任何提示词技巧都值钱。**

**体量不等于能力，但等于任务边界。** 2,143 个文件的 OpenMontage 和 36 个文件的 video-use 都自称 agentic，前者要接住从选题到导出的十五格，后者只管把素材剪干净。选错体量比选错工具更常见。

**最成熟的不是 AI 生成电影。** 剪辑（素材→成片）和讲解（文案→动画）跑在最前面，因为它们不跟模型能力较劲。而「一句话生成电影」那一格，仓库普遍年轻、依赖还不稳的生成 API——增速表里 CutClaw 5/天 vs OpenMontage 334/天，就是这个分野的定价。

**留一个出口给人类。** 剪映草稿导出、`edl.json`、`project.md` 会话记忆、分镜审批门、可回放的 Backlot——反复出现在不同仓库里。共识是最后一步要交回人手，区别只是交在哪个阶段。**一个不打算接手的自动化方案，在这条赛道上是不被信任的。**

## 参考

一手（GitHub API / 文件树 / README 与 SKILL 原文，2026-10-05 核对）：

- [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) · [animated-explainer.yaml](https://github.com/calesthio/OpenMontage/blob/main/pipeline_defs/animated-explainer.yaml) · [asset-director.md](https://github.com/calesthio/OpenMontage/blob/main/skills/pipelines/explainer/asset-director.md) · [docs/PROVIDERS.md](https://github.com/calesthio/OpenMontage/blob/main/docs/PROVIDERS.md)
- 安全公告与能力发现缺陷：[OpenMontage #626](https://github.com/calesthio/OpenMontage/issues/626) · [#637](https://github.com/calesthio/OpenMontage/issues/637)
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) · [skill 一致性问题 #5025](https://github.com/heygen-com/hyperframes/issues/5025)
- [browser-use/video-use](https://github.com/browser-use/video-use) · [SKILL.md](https://github.com/browser-use/video-use/blob/main/SKILL.md) · [边界咔哒声 #162](https://github.com/browser-use/video-use/issues/162)
- [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) · [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)
- [HKUDS/ViMax](https://github.com/HKUDS/ViMax) · [HITsz-TMG/VideoClaw](https://github.com/HITsz-TMG/VideoClaw) · [HKUDS/VideoAgent](https://github.com/HKUDS/VideoAgent)
- [PhiloLabs/awesome-video-agents](https://github.com/PhiloLabs/awesome-video-agents) · [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills)
- [remotion-dev/remotion](https://github.com/remotion-dev/remotion) · [FireRedTeam/FireRed-OpenStoryline](https://github.com/FireRedTeam/FireRed-OpenStoryline) · [GVCLab/CutClaw](https://github.com/GVCLab/CutClaw)

论文：

- [MovieAgent: Automated Movie Generation via Multi-Agent CoT Planning (arxiv 2503.07314)](https://huggingface.co/papers/2503.07314)
- [FilmAgent: A Multi-Agent Framework for End-to-End Film Automation](https://github.com/HITsz-TMG/FilmAgent)

转述（二手渠道，未直连原始发布页）：

- [GitHub 上的开源 AI 视频：50+ 条流水线全评测——Agent 就是导演](https://pixo.video/zh/blog/open-source-ai-video-pipelines)
- [AI 视频生成进入工作流阶段：Runway Agent、Aleph 2.0、Adobe Gemini 连接器盘点](https://m.blog.csdn.net/2401_88848122/article/details/161633985)
- [2.96 万 Star 的 OpenMontage，把 AI 视频生成做成了一套 Agent 剧组](https://wangruofeng007.com/blog/2026-06/openmontage-agentic-video-production/)
- [180 个 Claude 视频神器，我把真正值得用的开源 Skill 挖出来了](https://m.toutiao.com/article/7690396465835622912/)
- [Runway 官方 App Store 页面](https://itunes.apple.com/cn/app/id1665024375/) · [Adobe Firefly AI Assistant overview](https://helpx.adobe.com/in/firefly/web/firefly-ai-assistant/firefly-ai-assistant-overview.html)
