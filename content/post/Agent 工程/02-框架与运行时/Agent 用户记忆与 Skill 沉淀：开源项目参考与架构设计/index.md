---
title: "Agent 用户记忆与 Skill 沉淀：开源项目参考与架构设计"
description: "对比 Mem0、Letta、Zep、Graphiti、LangGraph、Agent Skills、OpenHands 与 Voyager，梳理可治理用户记忆和可演进 Skill 的架构设计。"
date: 2026-08-31T18:00:00+08:00
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 框架与运行时
    - Agent Orchestration
    - Memory
    - Agent Skills
    - Context Engineering
draft: false
---

当 Agent 可以替换、模型持续升级时，真正应该长期留在平台中的，不是某个 Agent 的私有会话状态，而是用户拥有的资料、记忆和可复用 Skill。

目前还没有一个开源项目同时做好跨 Agent 用户记忆、来源追溯、权限、删除、Skill 版本、评测和发布治理。比较现实的路线是组合借鉴：用成熟项目解决提取、检索和加载问题，由平台自己负责资产归属与治理。

本文回答三个问题：

1. 用户记忆可以参考哪些项目？
2. Skill 应该如何沉淀、加载和演进？
3. 如何把这些机制组合成一个面向生产环境的 Agent Harness？

---

## 1. 先区分 Memory、Experience 和 Skill

长期数据不应全部塞进一个向量库。更清晰的分类是：

| 类型 | 回答的问题 | 推荐资产 |
| --- | --- | --- |
| Semantic Memory | 用户是谁、偏好什么、有哪些稳定事实？ | `MemoryItem` |
| Episodic Memory | 过去发生了什么、结果如何？ | `Run / Event / Outcome / Experience` |
| Procedural Memory | 怎样做某件事更可靠？ | `SkillCandidate / SkillVersion` |

LangGraph 的长期记忆概念也采用 semantic、episodic、procedural 分类，并区分交互热路径写入与后台写入。参考：[LangGraph Memory Overview](https://docs.langchain.com/oss/python/concepts/memory)。

这个边界很重要：用户偏好不是 Skill，一次成功运行也不是 Skill。只有经过抽象、验证、去除个案数据并且能够复用的过程，才适合晋升为 Skill。

---

## 2. 用户记忆项目对比

| 项目 | 擅长什么 | 值得借鉴 | 不宜直接照搬 |
| --- | --- | --- | --- |
| Mem0 / OpenMemory | 结构化提取、检索和 Memory CRUD | scope、变更历史、过滤删除、混合检索 | Agent 可直接修改正式记忆，治理层较弱 |
| Letta / MemGPT | 分层记忆和后台整理 | Memory Block、共享记忆、sleep-time consolidation | 记忆通常围绕 Agent 组织 |
| Zep / Graphiti | 时间变化的事实和关系 | Episode、Entity、Relation、valid time | 第一阶段直接引入图数据库成本较高 |
| LangGraph / LangMem | 记忆分类和写入时机 | semantic/episodic/procedural、hot/background write | 是组件工具箱，不是完整治理系统 |

### 2.1 Mem0：参考第一版 API 和检索流水线

Mem0 的典型流程是：

```text
Conversation
    → 提取事实或偏好
    → 判断 ADD / UPDATE / DELETE / NOOP
    → 按 user / agent / run 等 scope 保存
    → 向量或图检索
```

它已经提供更新、删除、历史和反馈等实际能力。更新操作可以纠正旧事实；删除支持按用户、Agent、Run 和 metadata 过滤，并对无过滤条件的全量删除增加保护。参考：[Mem0 Update Memory](https://docs.mem0.ai/core-concepts/memory-operations/update)、[Mem0 Delete Memory](https://docs.mem0.ai/core-concepts/memory-operations/delete)。

适合借鉴的部分包括：

- 标准化的 `add/search/update/delete/history` 能力；
- 用户、应用、Agent 和 Run 等检索 namespace；
- 提取、冲突判断与索引更新分离；
- 显式批量删除和防误删设计；
- 用 feedback 修正后续记忆。

生产平台应在 Mem0 之上增加治理层。模型不能直接执行正式的 `ADD/UPDATE/DELETE`，而应先提交候选：

```text
MemoryCandidate
    → policy / user review
    → MemoryRevision
    → active MemoryItem projection
```

### 2.2 Zep / Graphiti：参考会变化的事实

Graphiti 使用时间知识图谱保存动态上下文，主要对象包括：

- Episode：原始会话、文档或业务事件；
- Entity：用户、组织、项目、地点等实体；
- Relation/Fact：实体之间的关系与事实；
- 时间信息：事实何时观察到、何时有效、何时失效。

Graphiti 支持增量更新，不要求每次重新批处理全部历史。参考：[Graphiti 官方介绍](https://help.getzep.com/graphiti/getting-started/welcome)、[Zep Graph 数据模型](https://help.getzep.com/v2/understanding-the-graph)。

例如，下面两条偏好不应该简单覆盖：

```text
2026-01：用户优先海运
2026-06：用户现在优先空运
```

更合理的表达是：

```text
Preference("shipping_mode", "sea")
valid_from = 2026-01
valid_to   = 2026-06

Preference("shipping_mode", "air")
valid_from = 2026-06
valid_to   = null
```

第一版不一定需要图数据库，但数据模型应预留：

- `observed_at`
- `valid_from / valid_to`
- `supersedes_memory_id`
- `contradicts_memory_id`
- `source_refs`
- `status=active/superseded/disputed/retracted`

否则长期记忆很容易退化成不断被覆盖、无法审计的用户画像 JSON。

### 2.3 Letta：参考分层上下文和后台整理

Letta 将一部分长期状态组织成持续出现在上下文中的 Memory Block，并允许多个 Agent 共享 Block。参考：[Letta Memory Blocks](https://docs.letta.com/api/typescript/resources/agents/subresources/blocks)。

它提出的 sleep-time compute 也很有价值：主 Agent 完成交互后，由后台 Agent 整理、压缩和重构记忆，把高延迟的 consolidation 移出用户交互路径。参考：[Letta Sleep-time Compute](https://www.letta.com/blog/sleep-time-compute/)。

可以映射成下面的后台流水线：

```text
Run completed
    → Candidate extraction
    → contradiction detection
    → clustering / deduplication
    → sensitivity classification
    → user or policy review
    → index refresh
```

需要注意的是：Canonical Memory 应属于用户或组织，而不是某个 Agent。Agent 只能通过当前 Run 的授权 ContextPack 获得只读快照。

---

## 3. Skill 沉淀项目对比

### 3.1 Agent Skills：作为可携带交换格式

Agent Skills 使用一个简单目录表达可复用能力：

```text
my-skill/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

它采用 Progressive Disclosure：

1. 启动时只暴露名称和描述；
2. 任务匹配时加载完整 `SKILL.md`；
3. 执行时才按需读取脚本、参考资料和资源。

这样可以让大量 Skill 共存，而不必把所有指令一次性塞入上下文。参考：[Agent Skills 规范](https://github.com/Open-Dot-Agents/SKILL.md)、[Anthropic Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)。

推荐把 Agent Skills 当成导入、导出和适配器交付格式，而不是平台事实源：

```text
SkillVersion（平台事实源）
    ↓ build / export
Agent Skills bundle（可携带交换格式）
    ↓ adapter
Codex / Claude / OpenHands / 自有 Agent
```

平台内部继续维护不可变 `SkillVersion`，每个版本可以构建成标准 Skill Bundle，并带有 checksum、依赖、权限和兼容性信息。

### 3.2 OpenHands：参考多级作用域和加载优先级

OpenHands 支持项目级、用户级、组织级和全局 Skill，并区分 always-on instructions 与按需加载 Skill。参考：[OpenHands Skills](https://docs.openhands.dev/overview/skills)。

平台可以采用类似作用域：

```text
platform baseline
    < organization Skill
    < workspace or project Skill
    < user Skill
    < Run explicitly selected Skill
```

但不能只用“同名文件覆盖”处理冲突。每次 Run 应记录：

- 实际选择的 SkillVersion；
- 选择原因：用户指定、规则匹配或 Agent 请求；
- 匹配分数与被排除原因；
- 依赖解析结果；
- 实际注入的文件和 token 成本；
- 执行过的脚本、工具和权限。

这些信息应成为 ContextPack 和 Run Evidence 的一部分。

### 3.3 Voyager：参考从成功轨迹生成 Skill

Voyager 在任务执行成功并通过验证后，将可复用实现抽象进 Skill Library；新任务再根据描述检索、组合已有 Skill。Skill Library 是它实现跨任务泛化的重要部分。参考：[Voyager 论文](https://openreview.net/pdf?id=P8E4Br72j3)。

值得借鉴的机制包括：

- 只从经过验证的成功轨迹中蒸馏；
- Skill 具有明确描述、前置条件和适用场景；
- 新 Skill 与已有 Skill 做相似性和能力重叠检查；
- Skill 可以组合，但依赖必须显式；
- 失败用于修复候选，不直接污染正式 Skill 库。

---

## 4. 推荐的双流水线设计

Memory 和 Skill 可以共享来源追踪、Review 和 Eval 基础设施，但生命周期不能混在一起。

### 4.1 Memory Pipeline

```text
Run / Event / Artifact
    → MemoryCandidate
    → Review or low-risk policy
    → MemoryRevision
    → MemoryItem projection
    → Retrieval evaluation
```

MemoryItem 不应原地覆盖，推荐使用“不可变 Revision + 当前投影”：

```text
MemoryItem
- id
- owner_scope
- memory_kind
- active_revision_id
- status

MemoryRevision
- id
- memory_id
- content
- structured_claim
- source_refs
- confidence
- sensitivity
- observed_at
- valid_from / valid_to
- created_by
- decision
- supersedes_revision_id
```

纠正时创建新 Revision，旧版本保留审计但不再进入新的 ContextPack。删除还应区分：

- Logical retraction：禁止召回，但保留必要审计记录；
- Physical purge：清除正文、embedding、缓存、图索引和派生副本；
- Tombstone：只保留不能反推出原文的删除证明。

### 4.2 Skill Pipeline

```text
Successful Run + Outcome + Ground Truth
    → SkillCandidate
    → Draft SkillVersion
    → Sandbox Eval
    → Review
    → Published SkillVersion
    → Canary / rollback
```

一个可运行的 SkillVersion 至少需要：

```text
SkillVersion
- instructions
- description / trigger hints
- references
- scripts / assets checksums
- tool and runtime dependencies
- required capabilities
- requested permissions
- compatibility constraints
- source run / outcome refs
- eval suite and version
- publish status
- rollback target
```

其中 `description` 不只是展示信息，它参与 Skill 召回，因此也必须版本化并接受评测。

---

## 5. ContextPack 必须说明“为什么选中”

只记录“本次用了哪条记忆和哪个 Skill”还不够。为了调试召回错误、权限问题和效果退化，建议记录检索证据：

```text
ContextPackEntry
- asset_id / version_id
- asset_type
- selection_reason
- scope_match
- relevance_score
- recency_score
- trust / confidence
- token_cost
- policy_decision_id
- redaction_applied
```

这样才能回答：

- 为什么选中了这条记忆？
- 为什么另一条没有进入上下文？
- 是召回、重排、权限过滤还是 token budget 导致遗漏？
- 更换 Agent 或模型后，ContextPack 是否仍然一致？

ContextPack 应是每个 Run 的不可变授权快照，而不是 Agent 对用户资产仓库的一次开放查询权限。

---

## 6. Skill 的安全晋升路径

不要从一次成功运行直接自动发布正式 Skill。更安全的顺序是：

```text
Observed pattern
    → Suggested procedure
    → SkillCandidate
    → Draft
    → Sandbox verified
    → Human approved
    → Published
    → Canary
    → Stable
```

只有同时满足以下条件，才适合创建 SkillCandidate：

- 至少有一次带明确 Ground Truth 的成功；
- 能从业务输入中移除用户个案和敏感数据；
- 相对已有 Skill 有新增价值；
- 没有扩大工具或数据权限；
- 有可重复执行的测试 fixture；
- 能明确描述适用条件和失败边界。

自动提炼可以提高效率，但发布必须由 Eval、权限检查和明确门禁控制。

---

## 7. 推荐的组合方案

没有必要选择一个框架承包全部能力。更实际的组合是：

| 设计领域 | 推荐参考 |
| --- | --- |
| Memory API 与基础检索流水线 | Mem0 |
| 时间、冲突和事实失效模型 | Graphiti / Zep |
| 后台整理与 consolidation | Letta |
| 记忆类型和写入时机 | LangGraph / LangMem |
| Skill Bundle 与渐进加载 | Agent Skills / SKILL.md |
| 用户、组织、项目作用域 | OpenHands |
| 从成功经验蒸馏 Skill | Voyager |
| 发布、验证与回滚 | 平台自己的 Eval、Ground Truth 与 Verifier |

整体架构可以概括为：

```text
UserResource / Run / Event / Artifact
                │
                ├──→ Memory Candidate ──→ Review ──→ Memory Revision
                │                                  │
                │                                  ↓
                │                         ContextPack Retrieval
                │                                  │
                └──→ Skill Candidate ───→ Eval ────┤
                                                   ↓
                                         Authorized Agent Run
```

Mem0 和 Graphiti 主要解决“怎样记住和找到”，Agent Skills 解决“怎样包装和按需加载”。生产级 Agent Harness 还需要回答：

> 这是谁的资产、来源是什么、为什么可信、谁批准、哪个 Agent 可以使用、运行时用了哪个版本、效果是否真的改善，以及如何纠正、撤回和删除。

这些治理能力，才是用户记忆和 Skill 能够跨 Agent 长期沉淀的关键。
