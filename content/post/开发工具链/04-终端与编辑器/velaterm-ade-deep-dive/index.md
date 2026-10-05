---
title: "VelaTerm 深度调研：把 iTerm2 和 Codex 装进同一个窗口的 ADE"
description: "VelaTerm 是一款开源（MIT）的多智能体开发环境：会话树管理九种编程 Agent、递归分屏终端、vspawn 派生子会话、vsearch/vtell 跨会话通信、Plan/Execute 拆任务、vkb 知识库，外加 SSH/浏览器/手机三路远程访问。本文基于官网、GitHub 仓库与第三方评测做一轮完整调研：产品定位、功能全景、技术架构、版本节奏、成熟度风险与竞品对比。"
date: 2026-09-30T20:00:00+08:00
slug: velaterm-ade-deep-dive
image: images/index/index.svg
categories:
    - 开发工具链
tags:
    - 终端与编辑器
    - Agent 工程实战
    - 调研
toc: true
draft: false
---

如果你同时跑着几个 Claude Code、Codex，标签页早就堆成了一排乱码，分不清哪个 Agent 在干活、哪个在等你批准——VelaTerm 就是冲这个场景来的。

它的官方公式很简单：**VelaTerm = iTerm2 + Codex**。像 Codex 一样管理智能体会话，像 iTerm2 一样分屏使用终端，两者放进同一个原生应用，还能推到浏览器和手机上继续用。它给自己起的名字是 **ADE（Agent Development Environment）**——"不只是终端，也不只是 IDE"。

需要先声明：本文是一轮**基于公开资料的深度调研**（官网、GitHub 仓库、Release notes、第三方评测，检索时间 2026-09-30），不是像之前 [Herdr 那篇]({{< relref "herdr-ai-agent-terminal-runtime" >}})那样的本机实测。所有功能描述以官方文档为准，未经我亲手验证的地方会在行文中说明。

---

## 一、项目档案

| 项目 | 内容 |
|---|---|
| 定位 | 多智能体开发环境（ADE）：终端 + 编程 Agent 会话管理 |
| 官网 | [velaterm.com](https://velaterm.com/zh-CN) |
| 仓库 | [github.com/vlinx-io/VelaTerm](https://github.com/vlinx-io/VelaTerm)（TypeScript 为主） |
| 出品方 | VLINX Software |
| 许可证 | MIT（2026-08-11 公开源码，仓库创建于 2026-08-09） |
| 最新版本 | v0.2.6（2026-09-30 发布，就是今天） |
| GitHub 数据 | ⭐ 240 · fork 27 · open issues 66（2026-09-30 查询） |
| 平台 | macOS（Apple Silicon/Intel）、Windows（x64/arm64）、Linux（x86_64/aarch64） |
| Shell | macOS zsh；Windows PowerShell / Git Bash（完整版内置）/ WSL；Linux bash |
| 价格 | 免费，MIT 开源，无付费层 |

几个第三方渠道的补充信息：[myaiexp](http://www.myaiexp.com/en/items/dev-tools/velaterm) 和 [HuntScreens](https://huntscreens.com/zh/products/velaterm) 都把它归入"多代理开发环境"类目；[Honeystax](https://honeystax.com/p/velaterm) 在 2026 年 8 月中给出的评估是"GitHub 健康 57/100、无安全策略、当时 8 个 open issues、风险 42/100"——两个月后的今天 issues 涨到了 66 个，项目迭代极快（见第六节），但治理配套还没跟上。

---

## 二、它到底是什么：一个窗口里的三层东西

理解 VelaTerm 最快的方式，是把它的窗口拆成三层看：

1. **底层：真实终端。** 每个会话都是一个真实 PTY，切走之后进程继续在后台跑。支持递归分屏（任意面板向右/向下拆，嵌套无深度限制）、命令与路径补全、`vopen` 把文件打开成标签页（带语法高亮、Markdown 渲染、图片查看）。
2. **中间层：Agent 会话。** 九种编程 Agent 作为"一等会话"运行——Claude Code、Codex、OpenCode、Copilot、Cursor、Antigravity、Cline、Pi 等。每个 Agent 有实时状态（working / pending / ready 等）、支持会话恢复和自定义启动参数。
3. **顶层：协作与组织。** 项目 → 分组 → 嵌套子分组 → 会话的树形结构，配搜索、重命名、归档；Agent 之间可以互相搜索对话、发消息、派生子和任务拆分（这是它和普通终端的分水岭，第四节细讲）。

同一个 Agent 会话有**两种视图**：会话视图把 Agent 的计划、改动、命令、测试结果渲染成一条对话流；切到终端视图就直接操作 Agent 自己的 TUI。这个"对话/终端双视图"是它区别于 tmux 系工具的一个显性特征。

另外两个日常顺手的点：

- **信息面板**：Agent 干活时，右栏实时显示订阅额度（plan quota）、上下文占用、Token 用量和系统负载——额度还剩多少不用去服务商后台查。
- **通知系统**：会话状态变化走树中的脉冲点、状态栏计数器和桌面通知三路，Agent 卡住等输入时不用逐个窗口巡检。

---

## 三、功能全景速览

按官方 README 的板块整理：

| 板块 | 能力 |
|---|---|
| 终端 | 真实 PTY、递归分屏、命令/路径建议（Tab 补全）、后台持久化 |
| Agent 会话 | 九种 Agent 一等会话、实时状态、恢复、自定义启动参数 |
| 会话组织 | 项目/分组/嵌套子分组/会话的无限层级树、搜索、归档 |
| 视图 | 会话视图（对话流）⇄ 终端视图（原生 TUI）随时切换 |
| 内置编辑器 | WYSIWYG Markdown 编辑器、代码编辑器、图片查看器；桌面端还有内置浏览器 |
| Git 集成 | 每会话显示分支、领先/落后提交数、改动量 |
| 代码审计 | 内置 Codex Security 工作流，用本机已登录的 Codex 或 Claude Code 跑全仓库/目录/工作树审计，可导出 Markdown/JSON 报告（实验性） |
| 知识库 | 会话知识库 + 本地 Markdown 笔记库，统一搜索；Agent 可用 `vkb` 查询 |
| 远程 | SSH 连接、HTTPS 端到端加密浏览器访问、iOS/Android 原生 App（官方标注 coming soon） |
| 其他 | 亮暗主题跟随系统、界面多语言完整翻译、游戏中心（Pixel Wing，键鼠/触控/手柄皆可） |

游戏中心这种东西出现在"开发工具"里多少有点彩蛋性质，但也说明团队的定位是"开发者长时间待着的工作空间"，而不只是一个终端模拟器。

---

## 四、重头戏：多智能体协作

这是 VelaTerm 与"带分屏的终端"真正拉开差距的部分，也是它敢自称 ADE 的底气。四组能力：

### 4.1 `vspawn`：一条命令派生子会话

Agent 在干活途中可以把旁支任务交给一个子会话：选 Agent、选模型、选推理强度，需要隔离就给它分配独立 worktree。子会话出现在父会话下方，进度在树里直接可见——本质上是把"多 Agent 编排"从脚本层面搬进了会话树。

### 4.2 跨会话通信：`vsearch` / `vrefer` / `vtell`

不同 Agent 的会话之间（Claude、Codex、OpenCode、Pi 等）可以互相查：

| 命令 | 作用 |
|---|---|
| `vsearch` | 搜索所有会话的对话内容 |
| `vrefer` | 读取某段对话，或直接就它提问 |
| `vtell` | 给其他会话发消息；加 `--steer` 可插入对方**正在进行的回合** |

想象一个典型场景：Claude 会话在改认证代码，可以 `vsearch` 找到之前某个 Codex 会话讨论过的数据库约定，`vrefer` 向它追问细节，再 `vtell` 通知另一个会话配合调整——Agent 之间的上下文不再靠人复制粘贴搬运。

### 4.3 Plan / Execute：一个大任务，一组会话

规划/执行模式把大任务拆给多个会话协作，流程分三步：

1. **规划**：规划会话（planner）制定方案、拆分任务；规划与执行可分别配置 Agent、模型和推理强度。
2. **执行**：`vflow` 提出拆分方案，**你逐项调整并确认后**才开始执行；每个执行会话（executor）在独立 worktree 里并行做一件事，作为规划会话的子会话显示在树中。
3. **验收**：`vtell --report` 把执行结果回传给规划会话逐项验收，未达标的任务退回原执行会话返工，上下文完整保留。

值得注意的是设计取舍：**拆分方案需要人工审批**，不是全自动发车；worktree 可以每个会话独立、也可以全员共享同一棵。这比"一键 Agent 军团"类产品保守，但在真实项目里更容易控制爆炸半径。

### 4.4 `vkb`：会话里的结论沉淀成知识

- `vkb memories` — 查会话知识库（把有价值的会话整理进条目，附带来源）
- `vkb notes` — 查本地 Markdown 笔记库（带标签、收藏、回收站）
- `vkb explore` — 查代码图谱，**在本机完成、不调用 AI 模型**

三者统一搜索。等于给 Agent 配了一个"动手前先查档案"的入口，也让散落在历史会话里的结论可以复用。

---

## 五、远程与移动：三种接管方式

远程是 VelaTerm 宣传里占比很大的一块：

| 方式 | 说明 |
|---|---|
| SSH | 应用内直连远程机器，连接前确认主机指纹 |
| 浏览器 | 一键开启 HTTPS 服务，端到端加密，任意设备打开 URL 就是完整桌面 UI，无需安装 |
| 手机 | iOS / Android 原生 App，扫码配对、推送通知、直接回复 Agent；官网标注"coming very soon" |

还有账号化的**配对链接**和**设备列表**管理；v0.2.0 起支持共享项目/会话——通过出站隧道把宿主的真实界面转发到共享 URL，权限限定在被授权的项目或会话范围内。

对"在服务器上跑长任务、地铁上用手机瞄一眼进度、顺手批准一个操作"这种工作流，这条链路是完整的。端到端加密这一点官方反复强调（"传输链路上没有可读的明文"），显然是在回应"把终端搬到浏览器"必然引发的安全疑虑。

---

## 六、技术架构与版本节奏

### 6.1 技术栈

| 层级 | 选型 |
|---|---|
| 桌面外壳 | **Tauri 2**（Rust 后端 + 系统 WebView）；另有一个 Electron 外壳并存（`electron/` 目录） |
| PTY | `portable-pty`（来自 wezterm） |
| 前端 | React 19 + TypeScript + Vite |
| 终端渲染 | xterm.js（fit / web-links / search / image / unicode11 插件） |
| 状态管理 | Zustand |
| 持久化 | SQLite（rusqlite，内置编译） |
| 样式 | Tailwind v4，主题基于 CSS 变量 |

选 Tauri 2 而不是 Electron 做主壳，换来的是"安装包仅数 MB、不捆绑 Chromium、启动快、多终端并发依然流畅"（官方口径；第三方介绍一致）。它解决的痛点很实际——这类会话管理器如果自己就是内存大户，跑十几个 Agent 会话就先把自己压垮了。

### 6.2 版本节奏：快得不正常

- 2026-08-09 仓库创建，08-11 公开源码
- v0.1.x 一路迭代到 108+
- v0.2.0（9 月中）：远程访问成体系（SSH/URL/指纹确认/扫码/账号登录）、实验性代码审计、本地知识库、Plan-and-Execute 会话
- v0.2.2（09-15）：用量限额后自动续跑（Claude/Codex 5 小时/周限额重置后自动恢复，默认关）、Windows 一键安装 OpenCode/Grok/Crush、会话知识库归档与全文搜索
- v0.2.3（09-24）→ v0.2.4（09-26）→ v0.2.5（09-28）→ **v0.2.6（09-30）**：差不多两天一个版本

v0.2.6 重点是远程连接体验（指纹确认、配对链接、账号设备选择）和对话视图分页加载。这个发版密度在个人/小团队开源项目里属于第一梯队——好处是反馈闭环极快，坏处是每两天升一次级，用户跟不上，文档也容易滞后于代码。

---

## 七、成熟度与风险，说清楚

调研不能只报喜。汇总几条需要注意的点：

1. **项目非常年轻。** 开源至今不到两个月，还处在 0.2.x 阶段，API、数据格式、行为都可能有破坏性变化。
2. **社区规模尚小。** 240 star（截至 2026-09-30）说明还在早期采用阶段；66 个 open issues 相对这个体量不算少。
3. **治理配套缺位。** Honeystax 8 月的评估提到仓库**没有 security policy**；远程访问涉及"把终端界面推到网络上"这种高危场景，安全响应机制的重要性远高于普通终端工具。虽然端到端加密的设计方向是对的，但"无安全策略"和"快节奏发版"组合在一起，建议**不要把远程访问端口直接暴露到公网**，至少先放在可信局域网/VPN 内。
4. **本文未经实测。** 所有功能描述来自官方材料，"九种 Agent 一等会话""端到端加密"这些关键声明的实际成色，要以你自己的试用为准。
5. **手机 App 还在路上。** 官网标注 coming soon，现在移动端走浏览器布局（自动重排为触控 UI）。

---

## 八、竞品对比

这个赛道今年明显热起来了，各家切入点不同：

| 工具 | 形态 | 切入点 | 和 VelaTerm 的差异 |
|---|---|---|---|
| **VelaTerm** | 原生 GUI 应用（Tauri 2） | ADE：会话树 + 双视图 + 跨会话协作 + 远程/移动 | 唯一同时做到"GUI 会话树 + 内置协作命令 + 浏览器/手机接管"的 |
| [Herdr](https://herdr.dev)（本站有[实测长文]({{< relref "herdr-ai-agent-terminal-runtime" >}})） | Rust 单二进制 TUI | tmux 的 Agent 化改造：语义状态 + socket 控制平面 + 插件体系 | 无 GUI、无内置浏览器/编辑器；但 API 面更完整、状态语义更严谨，适合活在终端里的人 |
| tmux / Warp | 传统终端 | tmux 是会话持久化原语；Warp 是现代化终端 | 不感知 Agent 状态，协作要自己拼 |
| Emdash | 桌面应用 | 用 Git worktree 隔离并行 Agent | 偏"并行实验场"，无终端分屏和远程接管 |
| cmux | macOS 终端 | Ghostty 基座 + 垂直标签 + Agent 通知 | macOS 独占，功能面窄 |
| Superset / Herdr 类 runtime | CLI | 在隔离 worktree 里批量养 Agent | 面向脚本化/无人值守场景 |

一句话选型：

- 要**图形界面、会话树、手机上看进度** → VelaTerm 是当前完成度最高的选择
- 要**严谨的 Agent 状态语义和可编程控制平面**、且愿意住在终端里 → Herdr
- 只是想要会话不丢 → tmux 依然是答案

---

## 九、适合谁

**适合：**

- 同时跑多个编程 Agent，标签页已经管理不动的人
- 想让 Agent 之间互相查资料、发消息、拆任务，而不是自己当传话筒的人
- 需要在服务器跑长任务、随时用浏览器/手机接管的人
- Windows 用户注意：这是少数把 Windows 当一等公民对待的同类项目（内置 Git Bash、x64/arm64 双架构、安装器处理了 npm wrapper 这类 Windows 特有坑）

**不适合 / 再等等：**

- 追求生产环境稳定性、受不了两天一个版本的人
- 需要完整插件生态的人（Herdr 的插件市场更成熟）
- 对"终端数据上网络"零容忍、又不打算细看安全配置的人
- 纯终端原教旨主义者——你会更想要 Herdr 或干脆 tmux

---

## 参考

- [velaterm.com](https://velaterm.com/zh-CN) —— 官网与用户手册（下载、入门指南、AI 智能体会话、远程开发、更新日志）
- [github.com/vlinx-io/VelaTerm](https://github.com/vlinx-io/VelaTerm) —— 源码（MIT），README 有中文版与技术栈说明
- [Releases](https://github.com/vlinx-io/VelaTerm/releases) —— v0.1.x → v0.2.6 完整变更记录
- [myaiexp：VelaTerm](http://www.myaiexp.com/en/items/dev-tools/velaterm) / [HuntScreens：VelaTerm](https://huntscreens.com/zh/products/velaterm) —— 第三方产品收录与功能摘要
- [Honeystax：VelaTerm](https://honeystax.com/p/velaterm) —— 仓库健康度评估（2026-08-15 快照）
- 本站关联阅读：[Herdr 详解：给 AI Agent 用的终端运行时]({{< relref "herdr-ai-agent-terminal-runtime" >}}) —— 同赛道另一条路线的本机实测

> **信息时效**：本文数据检索于 2026-09-30（GitHub 数据、版本号均为此日快照）。项目迭代极快，阅读时请以官网与仓库的最新状态为准。
