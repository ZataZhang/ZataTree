---
title: "让用户选择指定 Skill：从社区实践到生产级 API 设计"
description: "Agent Skills 规范并没有定义用户如何点名执行 Skill。本文对比 Deep Agents、VS Code、Codex 与 Jan 的调用模式，并给出一套包含权限、快照、幂等和运行时强制激活的生产级设计。"
date: 2026-09-02T15:00:00+08:00
slug: "让用户选择指定-Skill：从社区实践到生产级-API-设计"
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 工程化实践
    - Agent 工程实战
draft: false
---

最近在做 Agent 运行接口时，我碰到了一个看起来很小、真正实现起来却牵动整条运行链的问题。

系统已经加载了多个 Skill，模型也会根据用户问题自动挑选。现在产品希望再往前走一步，让用户在发送消息前直接选择「这次就用 freight-quote」。接口该怎么设计？是不是在请求里加一个 `skill_id` 就结束了？

我的判断是，`skill_id` 确实应该加，但它只是入口。一个能上线的显式 Skill 选择方案，还必须同时解决可见范围、授权、强制激活、版本快照、幂等和审计。否则界面看起来是用户选中了 Skill，Runtime 实际上仍可能没用它。

## 一、先分清三个经常混在一起的概念

讨论接口之前，先把 Skill 的三个状态拆开。

```text
Agent 被允许使用哪些 Skill
            ↓
用户这次请求选择了哪个 Skill
            ↓
Runtime 最终激活了哪些 Skill
```

它们分别对应能力范围、用户意图和执行事实。

一个 Agent 可以被管理员配置为允许使用 `freight-quote` 和 `document-recognition`。用户本次只选择 `freight-quote`，Runtime 就应当加载它，并把最终激活结果记录下来。用户不能因为知道另一个 Skill 的名字，就越过 Agent 配置直接调用。

如果不做这层区分，后面很容易出现两类问题。

一类是权限问题。前端隐藏了 Skill，但用户手工构造请求仍能调用；另一类是事实问题。用户选择了 Skill，后端只是往 Prompt 里加了一句「请使用 freight-quote」，模型最后没有读取对应的 `SKILL.md`，系统却把这次执行展示成已使用。

所以，显式选择不只是一个 UI 功能，它是新的运行契约。

## 二、Agent Skills 规范解决了什么，又没解决什么

[Agent Skills 开放规范](https://agentskills.io/specification)定义的是 Skill 包格式。一个 Skill 至少包含一个 `SKILL.md`，front matter 中必须有稳定的 `name` 和用于发现的 `description`，还可以包含 `scripts/`、`references/` 和 `assets/`。

它推荐渐进式披露。Agent 启动时只读取所有 Skill 的名称和描述；决定激活某个 Skill 后，再加载完整指令；执行过程中按需读取脚本和参考资料。这样既能保留大量能力，又不会一开始就把所有内容塞进上下文。

但规范没有定义 HTTP 请求应该长什么样，也没有规定 `/skill-name`、Picker 或 `skill_id`。这不是规范遗漏，而是边界划分。Skill 包应该能够跨宿主复用，至于谁能调用、怎么选择、如何审计，需要由 Codex、VS Code、Deep Agents 或业务平台自己决定。

因此，在自己的 API 中增加结构化 `skill_id`，不会破坏 Agent Skills 兼容性。真正需要避免的是把平台权限、运行状态等私有字段硬塞进通用 `SKILL.md`，让内容包和业务控制面耦合在一起。

## 三、开源社区的几种典型做法

### 1. Deep Agents，让模型根据描述自动选择

[LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/skills)在创建 Agent 时接收 Skill 来源目录。

```python
agent = create_deep_agent(
    model=model,
    skills=["/skills/"],
)
```

`SkillsMiddleware` 扫描目录，将每个 Skill 的 `name` 和 `description` 注入系统上下文。模型判断任务匹配后，再通过文件能力读取完整 `SKILL.md`。

这种模式很适合自动路由，也支持给不同 Agent 或 Subagent 配置不同 Skill 集合。但它没有提供一个通用的 `invoke(skill_id=...)` 契约。也就是说，Deep Agents 原生解决的是「哪些 Skill 可被发现」，不是「用户指定后如何强制激活」。

### 2. VS Code，把 Skill 变成可选择的 Slash Command

[VS Code 的 Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)同时支持模型自动加载和用户显式调用。用户可以在聊天框输入：

```text
/webapp-testing for the login page
```

Skill 还可以通过 front matter 控制两个方向的调用权限。

| 配置 | 用户可调用 | 模型可自动调用 | 适用场景 |
|---|---:|---:|---|
| 默认 | 是 | 是 | 通用 Skill |
| `user-invocable: false` | 否 | 是 | 只作为后台知识或流程 |
| `disable-model-invocation: true` | 是 | 否 | 必须由用户主动启动 |
| 两者同时设置 | 否 | 否 | 暂停或隐藏 |

这里最值得借鉴的不是 Slash Command 的外观，而是显式调用后的语义。宿主会直接加载对应 Skill 的完整指令，不会把 `/webapp-testing` 当成一段普通用户文字，再赌模型能不能正确理解。

### 3. Jan，把调用方式和能力白名单拆开

[Jan 的 Skill Invocation](https://www.jan.ai/docs/agent/skill-invocation)支持 `/release` 和 `/skill:release staging` 这类显式命令，同时还提供独立的 Skill 白名单。

```toml
[skills]
enabled = ["release", "security-review"]
```

这体现了一个很重要的工程原则。Skill 是否启用，与这一次由用户还是模型触发，是两个正交维度。一个 Skill 必须先在 Agent 的可用集合里，之后才谈得上显式或自动调用。

### 4. Codex，允许自动选择，也允许用户点名

OpenAI 在 [Codex app 的公开介绍](https://openai.com/index/introducing-the-codex-app/)中明确说明，用户可以要求 Codex 使用指定 Skill，也可以让 Codex根据任务自动选择。

社区方案看起来各不相同，但方向其实已经很清楚。产品一般不会在自动和手动之间二选一，而是同时保留两种入口，再由宿主系统负责权限和激活。

## 四、为什么只往 Prompt 里拼一句话不够

最省事的实现大概是这样。

```python
question = f"请使用 {skill_id} skill。\n{user_question}"
```

它能在 Demo 里工作，却很难成为可信的运行边界。

模型可能看到了 Skill 名称，但没有读取 `SKILL.md`；用户输入也可能尝试覆盖前面的要求；Skill 内容更新后，历史 Run 无法证明当时使用的是哪个版本。更麻烦的是，审计日志只能证明系统发送过一句提示，不能证明 Runtime 真正激活过对应流程。

这里要承认一个边界。即使后端完整注入了 Skill 指令，也无法数学意义上保证概率模型百分之百遵守。不过平台至少应该保证三件可验证的事实。

1. 用户选择的 Skill 经过了授权校验。
2. 运行上下文确实加载了这个版本的完整 Skill。
3. 执行记录保存了请求选择和实际激活结果。

把这三件事做好，才算把不确定性限制在模型执行层，而不是让接口和运行时本身也含糊不清。

## 五、一套适合生产系统的 API 设计

### 1. 先让前端查询这个 Agent 能用什么

建议提供 Agent 作用域下的 Skill 列表，而不是一个不带权限语境的全局列表。

```http
GET /api/agents/{agent_id}/skills
```

```json
{
  "items": [
    {
      "id": "freight-quote",
      "name": "运费报价",
      "description": "根据尺寸、重量和运输方式估算运费",
      "user_invocable": true,
      "model_invocable": true
    }
  ]
}
```

这个接口只返回当前用户可见、当前 Agent 已授权并且运行环境可用的 Skill。文件路径、服务器目录和内部凭据不应该出现在响应里。

### 2. Run 请求使用结构化选择

创建 Run 时可以引入 `skill_selection`。

```json
{
  "agent_id": "agent_123",
  "skill_selection": {
    "mode": "required",
    "skill_id": "freight-quote"
  },
  "input": {
    "content": [
      {
        "type": "text",
        "text": "2 个箱子，每个 1×1×1 米，毛重 300kg"
      }
    ]
  }
}
```

我倾向于保留三种模式。

| mode | Runtime 行为 | 适用场景 |
|---|---|---|
| `auto` | 从 Agent 允许集合中自动匹配 | 普通对话和兼容现有行为 |
| `required` | 强制加载指定 Skill | 用户在 Picker 或 Slash Command 中点名 |
| `none` | 本次不向模型暴露 Skill | 基础问答、隔离测试或安全场景 |

第一期如果想控制改动范围，也可以只增加可空的 `skill_id`，未传时等价于 `auto`。但显式 `mode` 更容易表达「不使用 Skill」，也为以后支持多个 Skill 留出了边界。

### 3. Slash Command 只是一种输入方式

前端完全可以提供熟悉的交互。

```text
/freight-quote 帮我计算这票货
```

但发送前应该把它解析成结构化请求。数据库和 Runtime 不应依赖解析原始文本中的 `/` 命令，因为移动端 Picker、工作流节点和 API 客户端未必使用同一种文本语法。

## 六、Runtime 应该如何真正激活指定 Skill

对 `auto` 模式，可以继续使用 Deep Agents 默认的渐进式发现，让模型在允许集合中选择。

对 `required` 模式，我更推荐由宿主在 invocation 开始前读取并验证 `SKILL.md`，把完整指令放入受信任的运行上下文，同时只暴露该 Skill 所需且被授权的资源。这样做会失去一点渐进加载带来的 token 优势，但一次只加载一个指定 Skill，成本通常可控，语义也更明确。

如果系统在启动时编译一个包含全部 Skill 的 Agent 单例，还要再做一步改造。运行时实例应该按有效配置缓存，而不是让所有 Agent 和所有 Run 永远共用同一个 Skill 集合。

```text
runtime_connection_id
+ runtime_source_agent_id
+ skill_bundle_checksum
+ model_configuration_checksum
= compiled agent cache key
```

这样既不必每次 Run 都重新构建 Agent，也不会让一个只允许使用 `freight-quote` 的 Agent 意外看到另一个部门的 Skill。

对于存在依赖的 Skill，可以把请求选择和有效集合分开。用户选择一个主 Skill，后端解析出它允许依赖的辅助 Skill，最终形成不可变的 effective bundle。不要允许客户端直接提交任意路径或任意依赖列表。

## 七、为什么 Skill 快照必须进入 Run

生产系统中的 Run 不只是一次临时函数调用，它往往还承担重放、审计、故障分析和结果归因。

建议在 Run 创建时冻结以下信息。

```json
{
  "skill_selection": {
    "mode": "required",
    "requested_skill_id": "freight-quote",
    "effective_skill_ids": ["freight-quote"]
  },
  "skill_snapshots": [
    {
      "skill_id": "freight-quote",
      "version": "1.2.0",
      "content_checksum": "sha256:...",
      "source": "platform"
    }
  ]
}
```

这里的 checksum 很关键。Skill 作者明天修改了 `SKILL.md`，历史记录仍然能够说明昨天的 Run 看到了什么。它还应该进入幂等请求摘要，否则同一个 `Idempotency-Key` 在不同 Skill 下可能错误地重放同一条 Run。

如果 Skill 自带脚本和参考文件，仅计算 `SKILL.md` 并不总是够。更稳妥的做法是为整个可执行 Skill 包计算内容清单和 bundle checksum，至少覆盖本次可能读取的受管资源。

## 八、安全边界不能交给前端

用户选择 Skill 后，后端至少要执行下面这条校验链。

```text
解析 skill_id
    ↓
确认 Skill 存在且版本可用
    ↓
确认当前用户有权运行该 Agent
    ↓
确认 Skill 属于该 Agent 的 allowed_skill_ids
    ↓
确认允许用户显式调用
    ↓
冻结快照并创建 Run
    ↓
Runtime 加载有效 Skill bundle
```

客户端只能传稳定 ID，不能传 `skills_paths`、`SKILL.md` 内容或本机目录。对普通用户，未找到和无权限最好采用防枚举语义，不泄露其他 Agent 安装了什么能力。

另外，Skill 的 `allowed-tools` 目前在开放规范中仍属于实验字段，不同宿主支持程度不同。生产系统不能只靠 front matter 当权限控制。真正的工具白名单、文件边界、网络访问和高风险操作确认，仍要由 Runtime 和基础设施层强制执行。

## 九、怎么分阶段落地

这项改造不需要一步做到完整市场和版本仓库，可以分成三个阶段。

### 阶段一，跑通单 Skill 显式选择

- 解析现有 `SKILL.md` 的 `name` 和 `description`
- 提供 Agent 作用域的 Skill 查询接口
- Run 请求增加 `skill_selection`
- 校验 `skill_id`，并在 `required` 模式预加载完整 Skill
- 把 Skill ID 和内容 checksum 写入 Run 快照及幂等摘要

### 阶段二，建立 Agent 与 Skill 的授权关系

- 为 Agent 增加 `allowed_skill_ids`
- 管理端支持绑定和解绑
- 区分 `user_invocable` 与 `model_invocable`
- Runtime 按有效 Skill bundle 缓存编译结果
- 事件或 Trace 中记录 Skill 激活事实

### 阶段三，再考虑版本和依赖治理

- Skill 版本发布、启用与回滚
- 依赖解析和 bundle checksum
- 组织、部门和用户级可见性
- 风险分级、签名校验和供应链扫描
- 对 Skill 选择正确率、失败率和成本做评估

这里容易踩的坑，是一开始就做一个很重的 Skill Marketplace，却还没有证明用户为什么要选、选完后能否稳定执行。先把「选择、授权、激活、记录」这条最短闭环跑通，通常更划算。

## 十、我的判断

如果系统只是个人助手，用户在 Prompt 中写一句「使用某某 Skill」可能已经够用。它实现快，失败后影响也有限。

但只要系统出现多租户、多个 Business Agent、高风险工具或运行历史，Skill 就不再只是 Prompt 模板。它开始接近一个带权限、版本和执行策略的能力包。此时，显式选择必须成为结构化 API 和不可变运行事实。

我最终会采用这样的组合。

- 用 Agent Skills 规范维护可移植的内容包
- 用 Agent 的 `allowed_skill_ids` 管理能力边界
- 用 `skill_selection` 表达本次用户意图
- 用宿主预加载实现 `required` 语义
- 用 Skill snapshot 和 checksum 保证历史可追踪
- 用 Picker 或 Slash Command 改善交互，但不让文本语法成为后端契约

这套设计比简单增加一个字段多做了一些工作，但这些工作不是过度设计。它们正好对应一个生产 Agent 最难回答的几个问题：谁允许它做、用户要求它做什么、它运行时到底加载了什么，以及事后能不能证明。

## 总结

用户显式选择 Skill，真正要落地的是一条完整的执行链，而不是一句 Prompt。

1. Agent Skills 规范负责内容包和渐进加载，不负责业务 API。
2. 社区主流是自动选择与显式选择并存，由宿主负责调用语义。
3. Agent 允许集合、用户请求选择和 Runtime 实际激活必须分开记录。
4. `required` 模式应该由后端加载完整 Skill，不能再交给模型二次决定。
5. Skill 版本和内容 checksum 应进入 Run 快照与幂等摘要。

界面上的 Skill Picker 很轻，背后真正有价值的，是把一次看似随意的模型选择，变成可以授权、复现和审计的运行事实。
