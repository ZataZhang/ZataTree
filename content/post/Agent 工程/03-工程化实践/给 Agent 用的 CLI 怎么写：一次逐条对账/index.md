---
title: "给 Agent 用的 CLI 怎么写：一次逐条对账"
description: "「给 Agent 写工具」的讨论大多停在 prompt 和 tool schema，但每天被 Agent 真正敲下去的是 CLI。我把这一代公开的 agent-facing CLI 设计原则翻了一遍，拿自己维护的 iar 逐条对账，发现它只对了「跑得起来」那一半——另外三件事还停在「给人看」。"
date: 2026-09-30T14:15:00+08:00
weight: 110
slug: "cli-for-agents-design-audit"
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - Agent 工程实战
draft: false
---

「给 Agent 写工具」这件事最近被讲得很多，但话题大多停在 prompt 和 tool schema 那一层。真正每天被 Agent 敲下去的，其实是 CLI——它没有 schema 的仪式感，却承担了绝大多数「让模型去操作一个系统」的活。

我维护一个叫 iar 的 Agent 编排器（仓库名 keda）。它自己就是跑 agent 的，顺手还随包发了一个 operator skill，教 Claude、Codex 这些外部 agent 怎么用它。所以很长一段时间里，我默认它已经够「给 Agent 用」了。

直到有人问我一句：你这个 CLI，算 agent-friendly 吗？

我不想凭感觉回答，于是把这一代公开的 CLI 设计原则翻了一遍，再拿 iar 逐条对账。结果有点意外：它不是不合格，而是**只对了一半**——「跑得起来」那半边做得很扎实，「让调用它的 Agent 更容易成功」那半边，还停在「给人看」。

这篇文章不写结论清单，写这次对账的过程：这代共识长什么样、iar 哪几条真的达标、哪三条是硬缺口，以及一个我差点抄错的「正确废话」。

## 一、这代共识，收敛得比想象中快

翻完一圈，真正有分量的其实是这几份：

- **Anthropic《Writing effective tools for agents》**：最常被点名的一条是「不要 1:1 包 API」（*"a common error we've observed is tools that merely wrap existing software functionality or API endpoints"*），以及错误信息要 specific & actionable，而不是一句 opaque error code。
- **Google / Justin Poehnelt《You Need to Rewrite Your CLI for AI Agents》**：Agent DX ≠ Human DX。给出 raw JSON payload 优先、运行时 schema 自省、field mask 控制 context、input hardening（Agent 会 hallucinate 出 `../.ssh` 这种路径）、以及 **ship SKILL.md 而不只是命令**。
- **Agent-First CLI 的 16 条原则**：Structured Output、Semantic Exit Codes、Machine-Readable Help、Non-Interactive Default……
- **Agent CLI Guide 的 10 条**：noun-verb 命令树、long flag 优先、stdout=数据 / stderr=消息、TTY-aware、语义退出码表。
- **AXI benchmark（425 次实测）**：agent-optimized CLI 在成功率、成本、延迟上全面压过 MCP 包装（100% / $0.050 / 15.7s vs 87% / $0.148 / 34.2s）。

来源五花八门，但可以压成三条轴——**发现层、执行层、解析层**：

![给 Agent 用的 CLI 的三层契约](images/index/agent-cli-layers.svg)

- **发现层**：Agent 得知道你能做什么。`--help`、稳定命令树、运行时 `schema`、随包 skill。
- **执行层**：Agent 得能稳定地把命令跑对。非交互默认、幂等、`--dry-run`、语义退出码、stdout/stderr 分离。
- **解析层**：Agent 得拿到能消费的结果。`--json`、稳定字段、默认高信号、分页/限量。

三条轴缺一条，Agent 就在那一层摔跤。

## 二、拿 iar 逐条对账

先说好消息。iar 在执行层其实做得很靠前，有几条甚至比很多自称 agent-friendly 的工具扎实：

- **非交互默认**：`--yes` 到处都是，交互只发生在 `sys.stdin.isatty()` 为真时。
- **TTY-aware**：交互终端里 daemon 会显示仿多列的实时面板；一旦重定向到文件或 CI，同一个命令自动退化成加 `[issue #N]` 前缀的纯文本行。
- **输出有边界**：`iar logs` 默认只给尾部窗口（约 64 KiB）+ `--lines`，明确不从头倾泻整份日志——这一条对应的是「别把 500 行塞进 Agent 的上下文窗口」。
- **随包发 skill**：`iar init` 会把 operator skill 装到每个检测到的 agent 的用户级 skills 目录，还会保护用户已改过的同名文件。这正好是 Poehnelt 说的「ship SKILL.md, not just commands」。

但把「解析层」摊开，画风就变了。整个仓库里能吐 JSON 的地方只有两处：`iar issue list --output json` 和 `iar agent … --json`。两处旗标名不同、序列化方式不同、返回结构也不同。剩下 `registry list`、`daemon status`、`worktree path`、`loop list` 这些，要么没有机器输出，要么只能靠正则去啃人类表格。

退出码更简单：除了极少数用法错误返回 `2`，几乎**所有失败都塌缩成 `1`**。调用方分不清「仓库没注册」和「网络超时」和「参数写错了」——只能回过头去 parse stderr 的自然语言。

第三条缺口是没有自省入口。Agent 想知道某条命令接受哪些参数、哪些是枚举、默认值是多少，只能读 `--help`，或者依赖 skill 里手写的命令表；CLI 一演进，那张表就开始漂移。

对账结果大概是：

| 维度 | 共识要求 | iar 现状 | 判定 |
|---|---|---|---|
| 非交互默认 | 禁交互 prompt | `--yes` + isatty 守卫 | ✅ |
| TTY-aware | 非 TTY 自动退化 | 面板 → 前缀文本 | ✅ |
| `--dry-run` | 写操作必备 | init/run/workflow 等全覆盖 | ✅ |
| 输出有边界 | 默认限量 | 日志尾部窗口 | ✅ |
| 随包 skill | ship SKILL.md | operator skill 自动装 | ✅ |
| 结构化输出 | **每条**产数据的命令 | 只有两处，旗标不统一 | ⚠️ |
| 语义退出码 | 0/1/2/3/4/5/10 | 基本只有 0/1/2 | ❌ |
| 运行时自省 | `schema` / `--describe` | 无 | ❌ |

一句话：**执行层已经是「给 Agent 用」的写法了，解析层还停在「给人看」的写法。**

![对账：执行层达标，解析层留白](images/index/agent-cli-audit.svg)

## 三、最该补的三样

### 1. 让 stdout 变成纯数据

资料里唯一被称为「无例外」的一条：**如果命令返回的是数据，就应该有稳定的机器可读格式；成功结果写 stdout，警告、进度、错误写 stderr。**

为什么值得较真？因为 Agent 的解析是脆的。只要 stdout 里混进一个 spinner、一行 `WARNING`、一个 ANSI 色码，下游的 `jq` 就会崩：

```bash
# 人类友好模式：表格
iar issue list --repo-id keda

# Agent 模式：stdout 只有数据，可以直接 pipe
iar issue list --json --repo-id keda | jq '.[] | select(.state=="open") | .number'
```

iar 的问题不是「没有 JSON」，而是「JSON 是零散的例外」。真正要补的是一个**统一出口**：同样的 `--json`（`--output json` 为等价别名），同样的 stdout/stderr 分工，同一种序列化口径。

### 2. 退出码是 Agent 看到的第一信号

命令跑完，Agent 拿到的第一个信号不是 stderr 里的文字，而是退出码。可现在的 `1` 是一个「万能垃圾桶」——什么错都是它。于是 Agent 要么放弃自己判断，要么去猜自然语言。

资料给出的语义码表其实很朴素：

| 退出码 | 含义 | Agent 该做什么 |
|---|---|---|
| 0 | 成功 | 继续下一步 |
| 1 | 未分类失败 | 读 stderr |
| 2 | 用法错误 | 改参数后重试 |
| 3 | 未找到 | 换个目标 |
| 4 | 无权限 / 未鉴权 | 停下来报告缺凭据 |
| 5 | 冲突 / 已存在 | 跳过或改为更新 |
| 10 | dry-run 通过 | 可以真正执行了 |

这里有个现实约束：扩展退出码属于**对外契约的行为变更**。只判断「是否非零」的脚本无害，但假设「任何非零都等于 1」的脚本会受影响。所以我的做法是——只在「有明确类别」的失败点启用新码，其余继续返回 `1` 兜底，并在 `--help` 和 release note 里把码表摊开。宁可小步，也不一次把面铺大。

### 3. 让 CLI 自己描述自己

Agent 没法 Google 你的文档。把 API 说明塞进 system prompt 又贵、又会过期——文档站上的版本，和此刻真正装的 CLI 早就不是一份东西了。

更好的做法是让命令自己回答自己：

```bash
iar schema --json | jq '.commands[] | select(.name=="issue list") | .options[] | select(.name=="--output")'
# { "name": "--output", "type": "choice", "enum": ["table", "json"], "default": "table", "required": false }
```

关键在于**从真实命令树运行时派生**，而不是维护一份静态 schema 文件。静态文件必然随着 CLI 演进漂移，派生则零维护——schema 是什么样，取决于你此刻真的装了哪个版本。

## 四、一个我差点抄错的地方：不做「非 TTY 自动切 JSON」

几份原则里都写着同一条：**非 TTY 时自动切 JSON**，颜色、分页、交互 prompt 全部关掉。听上去很对，我差点直接照抄。

但它对一个已经有大量用户的 CLI 是个陷阱。iar 有相当多人把 `iar …` 的输出接进管道和脚本。一旦「非 TTY 自动 JSON」上线，这些脚本会在**无人察觉**的情况下换掉输入——今天还能被 `grep` 的表格，明天变成一坨 JSON，脚本静默地错，比大声地报错难查得多。

所以我替 iar 定的规矩是：**机器模式必须显式声明**。不传 `--json` / `--output json`，永远是给人看的输出；要机器格式，自己说清楚。

代价是 Agent 得记住加旗标。但这恰恰是 operator skill 该干的事——把「机器消费一律 `--json`」写成不变量，等于替 Agent 记住了。**默认行为不动，是比「聪明地自动切换」更高的优先级。**

## 五、CLI 还是 MCP？

对账过程中总有人问：既然都给 Agent 用了，为什么不直接上 MCP？

AXI 那组 425 次实测给了一个反直觉的答案：agent-optimized CLI 在成功率（100% vs 87%）、成本（$0.050 vs $0.148）、延迟（15.7s vs 34.2s）三个维度全面领先 MCP 包装。原因也直白——每个 MCP tool 的 schema 定义本身就要吃掉几百 token，调用还多一层 round-trip；而 CLI 天生能 pipe、一次 bash 调用就能串起多个操作。

更准确的理解不是二选一，而是分工：

- **CLI 是执行接口**：先把底层能力做成稳定、可组合、可脚本化的命令。
- **MCP 是分发与治理接口**：当工具多到 Agent 一次记不住、或者运行环境根本不给 shell 时，再补一层。

所以这次我给 iar 排的顺序是：**先把 CLI 的机器契约做对，MCP 留到真正需要「无 shell 环境」时再评估。**

## 六、后续补记：把操作知识跟着 CLI 一起交付

> 2026-10-20 更新：前文保留最初对账时的 `iar` 名称和行为快照。项目现名 KedaCode，当前命令是 `kc`（也支持 `kedacode`），旧 `iar` 命令已不再安装。下面记录当前实现，不应把前面的历史示例直接当成最新版使用指南。

回头看，「随包发一个 SKILL.md」只说了分发动作。真正有用的是：**把 Agent 如何选择流程、理解结果、处理异常的操作知识，作为 CLI 的一部分交付和维护。** 目前项目里的 `kedacode-operator`，比最初那句「自动安装 Skill」走得更完整。

### 主文件负责路由，具体流程按需读取

它已经从单文件手册改成 `SKILL.md + references/`，但这只是结构上的拆分，还需要持续控制主文件的内容量：主文件先列用户意图，例如「建 issue」「看进度」「卡住了」「后台跑」「装环境与查 Agent 配置」，再指向对应说明文件。

```text
kedacode-operator/
├── SKILL.md
└── references/
    ├── create-issue.md
    ├── watch.md
    ├── triage.md
    ├── daemon.md
    └── setup-and-config.md
    …
```

Agent 先选路，再读该路的操作说明。共享规则留在主文件：只读请求不启动执行；已有明确授权继续有效；`--dry-run` 只是预览；机器消费显式使用 `--json`；退出码如何解释。具体的执行、恢复和配置步骤则跟着各自的 reference 维护。

这也不是只给命令换个存放位置。例如用户说「看看进度」，Skill 应引导它去查询和读日志，不能因为看到了 `run` 就启动任务；初始化因配置已存在而拒绝时，应走独立的 Skill 刷新入口，不能拿重建配置来修安装。**参数表说明什么能执行，Skill 说明此刻该选哪条路。**

### 参数交给真实命令树，Skill 解释选择和边界

当前 Skill 遇到未知旗标、默认值或枚举值，会引导 Agent 查 `kc schema --json` 或对应命令的 `--help`，而不是凭静态表格猜。命令细节以真实命令树为准，Skill 和文档据此修正。

但运行时 schema 也有边界：声明层的 `required` 并不一定包含全部业务条件。例如部分持久写入操作在 schema 中的 `--scope` 显示为非必填，实际省略会返回用法错误。Skill 会补充这类调用约束。因此，它既不能替代真实命令，也不只是重复 `--help`。

### 安装之外，还要能更新和保留用户修改

当前实现把随包目录作为发行源，安装时记录受管文件清单和内容摘要。受管范围是随包的主文件与 `references/` Markdown；用户自己增加的笔记或资源不会被当成发行包内容覆盖。

- 已与当前包一致的副本，报告无需更新。
- 能通过安装元数据或已知历史摘要确认未修改的旧副本，可以自动刷新，并清理旧发行版已经移除的受管文件。
- 用户修改过、或无法确认来源的不同副本，默认保留并报告冲突；只有明确授权覆盖，才替换受管文件。

刷新还有独立入口 `kc skill install`，不必重新生成仓库配置。若只需修复一个安装副本，可以先用 `kc skill repair-operator --skill-dir <absolute-path> --dry-run` 看计划，再在用户明确要求覆盖后使用 `--force`。这里保护的是用户实际改过的内容，而不是让所有旧副本永远停在旧版本。

### 把 Skill 纳入 CLI 的变更交付

维护规则要求：CLI 新增或修改命令、旗标、退出码、机器输出时，同时检查随包 Skill 和使用文档。项目已有测试覆盖安装资源、重复安装、冲突保护，并抽取主文件和 references 中的命令示例，与真实命令树及允许旗标清单比对。

这些检查能发现不存在的命令或旗标，却不能证明整条操作流程正确，更不能证明 Agent 每次都会理解指令。流程选择、授权边界和恢复建议，仍需要结合实际行为审阅。

这套做法最值得保留的不是目录结构，而是责任关系：**CLI 发布可执行能力，Skill 随包发布操作知识，两者一起演进。** 如果手里已经有一个给 Agent 用的 CLI，先补齐常用流程、更新机制和变更同步，通常就能获得实际收益；不必一开始另建一套知识分发平台。

## 七、再对照外部经验：有目录分层，还不等于写得够好

> 本节调研于 2026-10-20。以下区分外部经验、当前项目事实与待验证建议；没有把别人的实践当成我们已经取得的效果。

补完当前实现后，我又查了 Agent Skills 开放指南、Anthropic 的工程文章、OpenAI Agents SDK 的维护实践，以及 Vercel 的 Skill 分发工具。最值得吸收的经验，集中在三件事：看真实执行、控制必读内容、识别安装副本的版本关系。

### 看命令是否存在，也看 Agent 为什么这样操作

[Anthropic 的工程文章](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)建议从代表性任务中观察 Agent 的能力缺口，再逐步补充 Skill，并关注实际使用轨迹。[Agent Skills 评估指南](https://agentskills.io/skill-creation/evaluating-skills)进一步建议从两三个真实案例开始，在独立上下文里比较有无 Skill，或比较旧版与新版，同时保留结果、时间和可得用量。

放到我们的场景，可以先固定三个请求：

| 请求 | 要观察的行为边界 |
|---|---|
| 「看看这个 Issue 到哪了」 | 查询进度，不启动任务或后台进程 |
| 「配置已经初始化，只刷新 Skill」 | 走独立刷新入口，不重建配置 |
| 「本地 Skill 改过，帮我看看冲突」 | 检查并解释，不擅自强制覆盖 |

命令示例检查可以证明某个旗标存在，却不能证明 Agent 在这个请求下会选它。对比时需要记录它实际发现了哪份 Skill、读取哪份 reference、请求了哪些命令，以及最终结果。只看答复里写着「我已检查」不够。

为控制成本，建议先各跑一次旧版与新版，共六次独立会话。外部写入可以用命令捕获替身隔离，但真实模型的选择与文件读取不能被模拟；否则测到的只是预先写好的流程。报告也必须说明，这一层不是 live GitHub 验证。六次结果只能提供首轮反馈，不能推出普遍成功率。

### 行数少，不代表主文件负担小

[Agent Skills 编写指南](https://agentskills.io/skill-creation/best-practices)强调：只补 Agent 缺少的项目知识，按明确条件读取细节，过度全面的说明也可能引出无关操作。[OpenAI Agents SDK 的公开维护实践](https://developers.openai.com/blog/skills-agents-sdk)则把清晰触发、较窄职责与具体输出作为内容组织原则。后者是仓库维护 Skill 的经验，借鉴到随包 operator 时仍需结合自己的流程。

这也修正了我对现状的一点评价：**我们已经做了 hub + references，但不能仅凭这个结构就称主文件足够精简。** 2026-10-20 的采样中，主文件只有 88 行，却有约 3,877 个空白分隔词、26 KB；批次聚合、claim 选举和快速发布等细节仍以长段落常驻。这个词数不是 token 数，也不能直接换算节省多少成本。

下一步的建议是：共享底线保留，路线详情继续下沉。退出码表、只读约束、授权范围和用户修改保护仍在主文件；某种运行模式的完整资格与恢复步骤移到对应说明，并留下明确读取条件。那些 Agent 不容易自己识别的危险前提，应保留简短提醒，不能为了变短把它藏起来。

是否真的更好，要连同 reference 的读取成本一起看。主文件缩短了，若每次都要连读几份附录，总成本未必下降。

### 随包源更新，不等于任意安装副本都更新

[Vercel 的 skills 工具](https://github.com/vercel-labs/skills#sync-skills-from-npm-packages-experimental)提供了实验性的 npm 随包 Skill 同步：把依赖里的 Skill 链接进项目，让操作知识随依赖更新。它是版本跟随的一种具体实现，仍标为 experimental，也不是 Python 项目应直接照搬的方案。

对我们更直接的提醒是区分三份东西：**当前发行包内的源、用户目录里未修改的安装副本、用户自己改过的副本。** 当前项目已经能在原生会话启动时刷新可确认未修改的旧副本，也会保留修改过的副本并阻止该会话继续启动。独立刷新和单目录修复都有既有入口。

因此，眼下更划算的改进是把这些边界说明清楚，不能一看到 CLI 升级就断言所有 Skill 副本也已升级。尚无必要仅为这个提醒再造一个版本检测器或分发系统。

这些建议已整理成待执行 PRD：精简常驻内容、做三案例旧新对比、补齐安装副本差异说明。**目前是改进计划，还没有对应的行为评估结论。** 后续是否保留每处改写，应由实际轨迹、边界正确性和可得成本共同决定。

## 几点收获

- **「给 Agent 用」不是一种风格，是三层可检查的契约**。发现层、执行层、解析层——缺一层，Agent 就在那层摔。只凭「我们有 skill、有 MCP」就自称 agent-native，通常只覆盖了发现层的一角。
- **执行层容易达标，解析层最容易欠账**。非交互、dry-run、TTY 退化这些，写起来体感强、见效快；`--json` 统一、退出码分类、schema 自省这些「契约类」的活，不写也不会立刻出事——直到某个 Agent 在半夜因为一个 `1` 猜错了方向。
- **最难的不是抄原则，是判断哪条原则对你不适用**。「非 TTY 自动 JSON」就是典型：它对全新 CLI 是优点，对已有用户的老 CLI 是兼容性地雷。原则是坐标，不是圣旨。
- **能让 Agent 自己省事的，是稳定，不是聪明**。统一旗标、稳定字段、可区分退出码、可自省的命令树——这些东西一点都不性感，但它们决定了调用方第几次尝试能成功。
- **CSV 级的口径能救很多争论**。这次真正让我敢下判断的，是 AXI 那组实测数字；在「CLI vs MCP」这种各有道理的争论里，一组可复现的 benchmark 比十篇立场文章都管用。
- **CLI 契约变更时，也要检查随包 Skill 是否需要同步。** 子命令、参数、权限、退出码或 JSON 输出变化后，检查 Skill 是否仍能正确引导 Agent 发现命令、选择流程、完成授权和解释结果；受影响就更新，不受影响也记录理由。这次 FreshAI 增加 Agent 创建命令时，代码和指南都已更新，最初却漏了随包 Skill，直到专门检查才发现。`SKILL.md` 不是打包时写一次就结束的说明，而是 CLI 的下游契约，需要跟着受影响的行为一起维护。
