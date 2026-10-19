---
title: 一个 Markdown 文件吃遍各家 Agent：SKILL.md 格式详解与协议演变
description: 从"能不能让某个 skill 用便宜模型跑"这个小问题出发，把 Agent Skills 的 SKILL.md 格式、渐进式披露用法一次讲透，并查证协议自 2025 年 12 月开放标准化以来的真实演变：规范本体几乎冻结，变化都发生在治理、生态与实现层。
date: 2026-10-08T15:16:28+08:00
weight: 130
slug: skill-md-format-and-protocol-evolution
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - Agent 工程实战
draft: false
---

## 从一个省钱的念头开始

前两天整理自己的 skill 库时冒出一个很实际的念头。我给自己常用的几个 Agent 都装了一个叫 `git-diff-report` 的小 skill：它读一遍当前仓库的 git 改动，拼出一份带文件树和高亮 diff、可以直接发给别人看的 HTML 报告。这种活纯属机械劳动——解析 diff、套模板、生成文件——为什么每次都要用最贵的模型跑？能不能给它单独配个便宜模型？

打开文档一查，答案简单得让人愉快：SKILL.md 的 frontmatter 加两行就行。

```yaml
---
name: git-diff-report
description: ...
context: fork
model: lite
---
```

但紧接着第二个问题就冒出来了：这些 skill 目录我是直接分发到 `~/.claude`、`~/.codex` 好几个工具的。**同一个 SKILL.md 拷过去，Codex 那边还认 `context: fork` 和 `model: lite` 吗？** 这背后其实是两个更大的问题：SKILL.md 这套格式到底定义了什么、各家支持到什么程度；以及这套协议从发布到现在，变了多少。

把这两个问题彻底查了一遍之后发现，答案比想象中有意思：**协议本体几乎没变过，变的全是协议之外的东西。**

## Skills 是什么：三行文本取代一套插件体系

在 Skills 出现之前，给 Agent 添加自定义能力是一件很"工程"的事：写插件、实现 SDK 接口、编译打包、走分发渠道。2025 年 10 月 16 日 Anthropic 推出 Skills 时，把这套流程压缩成了一个反常识的形态——**一个带 YAML frontmatter 的 Markdown 文件**：

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
---

## 工作流程

1. 检查 PDF 文件是否存在并可访问
2. 使用 pdftotext 获取基本信息
3. ...
```

`name` 和 `description` 是仅有的两个必填字段，下面随便写什么。没有 SDK，没有编译，没有接口协议。LLM 天然会读 Markdown，所以"安装一个能力"退化成了"放一个文件"。

这个设计能成立的根基是**渐进式披露（progressive disclosure）**，分三级加载：

| 层级 | 加载内容 | 时机 | 成本 |
|---|---|---|---|
| 1. 元数据 | `name` + `description` | Agent 启动时，所有 skill | 每个约 100 token |
| 2. 指令 | SKILL.md 正文 | skill 被激活时 | 建议 < 5000 token |
| 3. 资源 | `scripts/`、`references/`、`assets/` 下的文件 | 按需 | 用到才读 |

第三级是目录约定而非硬性规定：可执行代码放 `scripts/`，补充文档放 `references/`，模板图片放 `assets/`。SKILL.md 正文里用相对路径引用它们。Agent 启动时只背着所有 skill 的一行描述干活，判断某个任务命中了某个 description，才把正文拉进上下文，正文不够了再按需读引用文件。装一百个 skill，日常开销也只有一百个"书签"。

## 格式详解：六个标准字段

SKILL.md 的规范正文在 [agentskills.io](https://agentskills.io/specification)，目录结构很简单：

```
skill-name/
├── SKILL.md          # 必需：元数据 + 指令
├── scripts/          # 可选：可执行代码
├── references/       # 可选：补充文档
├── assets/           # 可选：模板、静态资源
└── ...               # 其他任意文件
```

frontmatter 里标准定义的字段一共六个，逐个说：

### `name`（必填）

约束比想象中严格：1–64 字符，只能小写字母、数字和连字符，不能以连字符开头或结尾，不能有连续连字符——而且**必须和父目录名一致**。

```yaml
name: pdf-processing      # ✓
name: PDF-Processing      # ✗ 不允许大写
name: pdf--processing     # ✗ 不允许连续连字符
```

### `description`（必填）

规范上限 1024 字符，但它值得花心思写，因为这是 Agent 决定"要不要用这个 skill"的唯一依据。规范的 good example 和 poor example 对比很说明问题：

```yaml
# ✓ 动作 + 场景 + 触发词
description: Extracts text and tables from PDF files, fills PDF forms, and merges
  multiple PDFs. Use when working with PDF documents or when the user mentions
  PDFs, forms, or document extraction.

# ✗ Agent 根本不知道什么时候该想起它
description: Helps with PDFs.
```

写法上的经验：把「做什么」和「什么时候用」都写进去，触发词（用户可能说的词）越具体越好。中文场景就写中文触发词，Agent 是按语义匹配的。

### `license`、`compatibility`、`metadata`（可选）

`license` 写许可证名或指向打包在内的 LICENSE 文件；`compatibility`（≤500 字符）声明环境要求，比如 `Requires Python 3.14+ and uv`——大多数用不到它；`metadata` 是字符串到字符串的自由键值对，规范建议键名取得独特一点避免冲突，作者、版本这类信息可以放这。

### `allowed-tools`（可选，实验性）

预批准的工具列表，声明这个 skill 运行时可以不经确认使用哪些工具：

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

注意它**仍是实验性字段**，规范原话是 "Support for this field may vary between agent implementations"。而且各家语法还没对齐：标准规范用空格分隔，Claude Code 和 CodeBuddy 用逗号分隔。跨工具分发的 skill 在这里要留心。

### 正文

frontmatter 之后就是普通 Markdown，没有任何格式限制。规范推荐的骨架：分步指令、输入输出示例、常见边界情况。唯一要记的数字是 **500 行**——超过就该拆文件了，正文只留主干，细节挪去 `references/`，引用链保持一层深，别让 Agent 顺着嵌套引用一路读下去。

写完可以用官方的 `skills-ref` 校验：

```bash
skills-ref validate ./my-skill
```

## 用法：写法上的三个落点

渐进式披露不只是加载机制，它直接决定了 skill 该怎么写：

**一、description 是书签，不是摘要。** Agent 只凭它决定是否激活 skill。把用户会说的原话写进去（"展示当前改动""生成改动预览页"），比写一句漂亮的概括有用得多。

**二、正文是操作手册，不是文档站。** 激活即全文进上下文，所以每一行都在花 token。写步骤、写判断分支、写"不要做什么"，别写背景介绍和原理科普——那些该去 `references/`，让 Agent 需要时自己读。

**三、脚本是能力的实体。** 需要 PDF 解析、数据转换这类确定性操作时，别指望提示词描述算法，在 `scripts/` 放一个正经脚本，正文里只写"运行 `scripts/extract.py`"。提示词负责决策，脚本负责执行，各干各的。

放置位置上各家趋同：用户级放 `~/.claude/skills/`、`~/.codex/skills/`（Claude 与 Codex 桌面端和 CLI 共用同目录），项目级放项目内的对应目录，项目级优先。写好一个 SKILL.md，cp 到几个目录里就完成了"跨平台发布"——这正是这套协议最有杀伤力的地方。

## 各家的扩展字段：格式可移植，配置不可移植

标准只有六个字段，但各家都在往上加自己的扩展。扩展不是背叛——规范把 `metadata` 留成自由键值对，本来就是允许实现层向外生长。

**Claude Code** 是扩展最多的，SKILL.md frontmatter 支持的字段已经有 20 个。挑几个有意思的：

```yaml
---
disable-model-invocation: true   # 只许用户 /name 手动触发，Claude 不得自动加载
user-invocable: false            # 反向对偶：只许 Claude 自动调用，从 / 菜单隐藏
context: fork                    # 在隔离子代理中执行，看不到对话历史
model: haiku                     # 执行模型；inline 模式下也生效
agent: Explore                   # fork 时用哪种子代理
background: false                # fork 默认后台跑，false 表示等结果
effort: low                      # 推理力度覆盖
paths: "src/**/*.ts"             # glob 限定自动激活范围
---
```

`disable-model-invocation` 和 `user-invocable` 是一对漂亮的对偶：前者管住"AI 别自作主张"，典型场景是 `deploy-prod` 这种绝不希望被语义匹配误触发的危险操作；后者管住"别占用户的菜单"，给纯内部引用的辅助 skill 用。

**CodeBuddy Code** 也支持 `context: fork` / `agent` / `model` 这套，但语义有个关键差异：`model` **仅在 `context: fork` 时生效**——inline 模式的 skill 在主对话里跑，模型跟主会话走。Claude Code 的 `model` 则在两种模式下都生效。同一个字段，行为不同。

**Codex CLI** 目前基本只认标准六字段，frontmatter 里的扩展字段会被静默忽略。

于是就有了文章开头那个问题的答案，也是本文最想留下的一句话：

> **未识别的 frontmatter 字段会被各家静默忽略。** 所以把写了 `context: fork` + `model: lite` 的 SKILL.md 拷到 Codex，skill 照常能用、照常被触发，只是那两行不生效，跑在默认模型上。格式是可移植的，模型路由这类配置是不可移植的——想让同一个 skill 在多家都跑便宜模型，得按各家的机制分别配。

还有个容易踩的细节：`model: lite` 这种路由别名也是各家私有词汇。CodeBuddy 的 `lite` 映射到自己的轻量模型档位；Claude Code 的 `model` 接受的是它 `/model` 命令同款值（如 `haiku`、`sonnet`），写 `lite` 大概率解析不到。

## 协议发布至今：本体冻结，四周生长

回到时间线，把发布以来的演变捋一遍：

- **2025-10-16**：Anthropic 推出 Skills，作为 Claude 的能力扩展机制。
- **2025-12 中旬**：Simon Willison 发现 OpenAI 已在 ChatGPT 和 Codex CLI 中悄悄采纳 Skills（Codex 0.65 里已试水）。一个平台的功能设计被竞争对手如此迅速地抄走，这本身就是对格式最硬的背书。
- **2025-12-18**：Anthropic 将 Agent Skills 发布为开放标准，上线 agentskills.io，并捐赠给 Linux Foundation 旗下的 Agentic AI Foundation（AAIF），转入中立治理。
- **2026 年**：Cline、Qwen Code 等工具跟进实现，官方客户端展示列表里从 Claude、ChatGPT、Codex 一路扩到 Pulumi Neo 等各类 Agent 产品。

那协议本体变了吗？我去翻了 agentskills 仓库的提交历史。**一年下来，对规范文本的实质改动只有两处，都是澄清而非变更**：一处修正 `name` 字段的字符范围表述（明确包含数字），一处澄清 `metadata` 的说明措辞。其余提交全是网站内容、客户端 logo 和 README。六个字段、目录约定、渐进式披露，从发布那天起就没动过。

这个"不动"是刻意的。协议把一切可变的余地都留在了三个泄压阀上：`metadata` 自由键值对接住元信息需求，`allowed-tools` 挂着实验性标签观察各家的语法分歧，正文无格式限制容纳一切指令风格。核心保持极小集合，生长全部外包给实现层——Claude Code 从标准六字段扩到二十个，CodeBuddy 加了自己的 `skillOverrides` 可见性控制，Codex 安于标准子集。协议本体冻结，反而成了它被广泛采纳的前提：**实现方不用担心今天写的 skill 明天就作废。**

所以"协议有没有改变"的完整答案是：规范没变，但生态彻底变了。治理从中立化起步（这点和 MCP 的路径一致），采纳从一家功能变成行业默认格式，扩展在实现层各开各的花。一个 Markdown 文件，正在成为 Agent 世界的"通用文件格式"。

## 几点收获

- **协议设计上，小即是大。** 六个字段就完成标准化，靠的是把确定性操作外包给脚本、把可变性外包给 metadata 和实现层扩展。规范冻结不是懒，是为采纳扫清心理障碍。
- **写 skill 的投入应该压在 description 上。** 它是 Agent 唯一凭据，写触发词、写场景，别写文采。正文 < 500 行，多的拆 `references/`。
- **跨工具分发时，只依赖标准六字段的部分是"通用区"，扩展字段是"私辖区"。** 未识别字段静默忽略意味着扩展不会弄坏别家的加载，但也别指望它生效。`allowed-tools` 连分隔符语法都还没统一，是当前最明显的兼容性坑。
- **"发布至今没变"的验证方式是翻仓库提交历史，不是翻记忆。** 一年只有两处文档澄清——这个事实让"协议稳定"从印象变成了可引用的结论。
