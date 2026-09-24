---
title: "内置 Agent 放哪：一个 is_runnable 陷阱与三类事实源"
description: "从「内置 Agent 在目录里永远显示不可用」这个陷阱出发，一路讨论内置 Agent / Runtime / Skill / MCP 的定义放哪、权限怎么给，最后沉淀成 Agent 平台的三类事实源判断规则。"
date: 2026-09-22T18:39:16+08:00
slug: builtin-agent-source-of-truth
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 框架与运行时
    - Agent Orchestration
    - Agent 工程实战
draft: false
---

```python
def is_runnable(self, *, supported_source_types: frozenset[str]) -> bool:
    return bool(
        self.enabled
        and self.organization_unit_id
        and self.runtime_connection_id
        and self.runtime_source_agent_id
        and self.runtime_descriptor_checksum
        and self.runtime_source_type in supported_source_types
    )
```

这是我们 Agent 平台领域模型里的一个函数。六项条件硬 AND，是用户目录 `available` 字段的唯一来源——某个 Agent 在用户面前是「可用」还是灰掉的，就看这一行。

原型评审通过那天（13 个页面状态全可达、console 零报错），我以为万事俱备。这个函数不这么认为，而我当时的第一反应居然是：是不是原型里哪个开关忘了画。打开领域模型逐个条件对了一遍，才发现不对的是更深一层——我们正准备上线的「内置 Agent」，第四、第五个条件**永远没有值可填**。

## 先交代这是个什么平台

一个企业内的 Agent 托管平台，两类角色两个面：管理员在 Admin 侧管 Runtime、管 Agent、做分配；普通用户在 public 目录里挑一个 Agent 对话，每次对话背后是一次可恢复、有事件流的 Run。

「Agent 在这个平台上」其实是两半东西：

- **业务定义行**，存在数据库里：名字、系统提示词、业务目的、任务契约、负责人、可见范围、分配给了哪些部门/人；
- **Runtime 绑定**，就是上面 `runtime_` 开头的那几个字段：这个 Agent 实际「由谁执行」——绑到哪条连接、远端的哪个候选、候选定义的哪个版本、来源类型是什么。

平台自己的执行引擎叫 internal Runtime（另有一个隔离沙箱 sandbox），而所谓**外部 Runtime**，是通过 endpoint 接进来的第三方 Agent 服务：管理员登记一条连接，向它「发现」远端暴露的候选 Agent，再挑一个绑到业务定义行上——平台只负责转发对话，真正的执行发生在远端。

上线至今的 Agent 全是这种「外部绑定型」。这次要新增的是另一种：**内置 Agent**——跟着平台发布、定义由平台方（ops）拥有、跑在平台自己的 internal Runtime 上，不再有任何远端。

而 `is_runnable` 是在只有外部绑定型的世界里写出来的。这就是冲突的全部来源。

## 一个硬 AND 的陷阱

回到开头那六项条件。为什么外部 Agent 个个能过？因为三个 `runtime_*` 字段是一套「绑定三件套」，从发现流程里带回来：绑的是哪条连接（`runtime_connection_id`）、远端的哪个候选（`runtime_source_agent_id`）、候选定义的哪个版本（descriptor 的 SHA-256）。三个字段的语义**全部指向远端有个东西**。

内置 Agent 没有任何远端，也没有「发现候选再绑定」这一步。第四、第五个字段没东西可填，只能空着。于是内置 Agent 一建出来：管理页面上一切正常，用户目录里永远「不可用」。原型画得再顺，接上实现就是坏的。

这个坑怎么爬，其实只有三条路，走一遍就明白为什么最后只剩「按来源分叉」一条：

**路一：全局放宽，把两个字段从校验里删掉。** 不行。这两项对外部 Agent 是实打实的防线——远端候选被改名、被下线，descriptor 的 checksum 会变化，创建 Run 时能当场拦下；删掉之后，坏绑定要到运行时被远端拒绝才知道，而且「这条分配基于哪个版本的远端定义」这个审计问题永远失去答案。

**路二：内置行也填上值。** 给 `runtime_source_agent_id` 造一个假想候选的常量 ID、checksum 填占位符。能跑，但等于伪造语义——内置 Agent 并不对应任何「被发现的候选」，审计里那句「基于远端哪个版本」在内置行上变成一个指向不存在事物的假答案。这种假答案能骗过所有人，直到有人认真看一眼。

**路三：按来源分叉。** 条件不再是「六个字段都有值」，而是「这个来源的 Agent，凭什么算完整」。内置行的完整性定义本来就不同：它需要的不是远端三件套，而是**定义内容的哈希**——声明文件的 SHA-256（下一节讲定义放哪，那里会看到这个哈希从哪来）。外部那套一个字不改，内置按自己的完整性定义显式分叉：

```python
if self.origin == "builtin":
    return bool(
        self.enabled
        and self.organization_unit_id
        and self.runtime_connection_id
        and self.runtime_descriptor_checksum    # 声明文件内容的 SHA-256
        and self.runtime_source_type in supported_source_types
    )
```

但这句话立刻引出了下一个问题：**内置 Agent 的定义，到底放在哪里？** 不回答「定义放哪」，checksum 根本无从谈起。

## 定义放哪：三个候选，和仓库里的三个先例

摆出来的选项有三个。翻代码时发现，每个选项在仓库里都已有先例——这反而让选择变得清楚了。

**选项一：Python 常量 + 启动 seed。** 内置工具就是这么办的：

```python
def seed_tools() -> None:
    """写入模板内置工具种子数据。"""
    ...
    if database_session.query(ToolModel).first() is not None:
        return                      # 表里有数据就跳过：seed 只插一次
    seed_tool_models = [
        ToolModel(id="web_search", name="网页搜索", ...),
        ToolModel(id="code_runner", name="代码执行", ...),
    ]
```

最省事，但改一个 prompt 要发版。更麻烦的是它让数据库处于一种「半拥有」状态：seed 只插一次不更新，管理员在 DB 里改了，DB 成了事实源；管理员删了，下次重启又复活。「内置项的删除与启停归属」必须额外写死规则，不然一定有人踩。

**选项二：config.toml 声明段。** 平台里非密钥配置的家：

```toml
[mcp_connection.types.standard-remote-mcp]
label = "标准远程 MCP"
capability_id = "mcp_generic"
```

可评审、可 diff，但 TOML 是放标量和短表的地方。内置 Agent 的核心资产是**一篇长 prompt**，塞进配置文件会把 config.toml 变成没人愿意 review 的怪物。

**选项三：ops 拥有的声明目录。** 仓库里刚沉淀出的新模式——每个条目一个声明文件，和它的实现代码放在一起：

```toml
# 启动声明目录：每个 *.toml 声明一个本地 stdio server 的启动方式...
# ⚠️ 本目录必须由 ops 拥有、运行时只读，且不能落在 workspace_root 内
[mcp_connection.declarations]
root = "src/skill_mcp_react_agent/servers"
```

改文件 = 提 PR + 评审 + 重新部署；装配期校验，越界直接启动失败；管理面只能选用、不能编辑内容。「ops」在这里是所有权：声明目录归运维/平台方，管理员只能启停和分配，运行时进程只读。

最后拍板选了目录，起决定性作用的却是第四个观察——**内置 Skill 早就在过同一条路**：每个 Skill 一个目录、`SKILL.md` 带 frontmatter、加载器解析、`content_checksum = SHA-256(SKILL.md)`。内置 Agent 和内置 Skill 在资产性质上完全同构：ops 拥有、内容是长文本、随代码发布。Skill 用目录用得很好，没有理由给 Agent 发明第二套。

于是 checksum 的问题顺手解了：内置行的 `runtime_descriptor_checksum` 填**声明文件的内容哈希**。和 Skill 的 `content_checksum` 完全同构，审计表零分叉——「这条分配基于哪个版本的定义」对外部行是远端 descriptor 的哈希，对内置行是声明文件的哈希，语义同一个：**定义内容的哈希**。

顺带两条派生结论：

- **内置 Agent 禁止派生。** Derive（把一个 Agent 复制成独立新行，留 `derived_from_agent_id` 但后续不同步）隐含假设「定义在 DB 里、可以随意复制」。内置 Agent 的定义根本不在 DB，派生出来的行既不是内置（不在目录里）也不是外部（没有远端），目录会被迫长出第三类。想以内置 Agent 为底做变体，正确动作是去声明目录加一个文件。
- **内置 Runtime 反过来，不需要目录。** 内建的 Runtime 就一两个，存在与否跟着代码装配走（adapter 类注册了才存在），为它们建声明目录等于给两个硬编码条目套登记簿。它唯一值得声明的是基础提示词——而这一项现状已经是文件式的：config.toml 只放指针，prompt 是代码旁边的 markdown：

```toml
system_prompt_path = "src/skill_mcp_react_agent/SYSTEM_PROMPT.md"
```

长文本进文件、ops 评审、config 只做指针——声明目录的精神已经在这了，只差给它一个名分。

## 权限：把 Agent 给了他，Skill 跟不跟过去？

模型问题定了，下一个问题更贴近日常：管理员把一个 Agent 分配给某人，这个人就能直接用 Agent 需要的 Skill 吗？还是全部解耦——给了 Agent 还要再给 Skill / MCP 的权限？

先盘现状，发现已经是混合模型：

| 资源 | 授权挂在哪 |
|---|---|
| MCP 连接 | Agent 上（一个 Agent 绑一条连接） |
| 工具 | Agent 上（descriptor 声明） |
| Skill | **人身上**（平台范围默认全员；restricted 需要按人或按部门显式授权） |

而且 Skill 的门禁是刻意双层：目录展示和 Run 创建共用同一个策略实例，装配处的注释写得很直白——否则「目录里看不到，但直接提交 skill_id 仍能运行」，两层门禁形同虚设。也就是说现状的回答是**解耦**：分配 Agent 给的是「可以指挥这个 Agent」，不是「获得这个 Agent 用到的一切」。

要不要改成随 Agent 传递授权？想明白的结论还是不要，三个理由：

1. **越权面**。Skill 的运行资产是会真实进入沙箱执行环境的字节。随 Agent 传递，等于分配动作一次性授出该 Agent 引用的全部执行能力，做分配的人根本不知道授出去了什么。
2. **审计粒度**。授权挂人身上，「谁能用这个 Skill」是一次查询；挂 Agent 上，要从分配图反向遍历才能算出来。
3. **哲学一致**。「Agent 声明它用什么、人决定他能用什么」的分离，和前面「定义不进 DB、DB 只存启停与分配」是同一件事：**声明与授权分离**。

代价当然有：管理员要多做一步 Skill 分配，用户会碰到「Agent 能打开、跑到某步被拒」。这个用 UX 补，不用权限模型补——分配页展示该 Agent 引用了哪些 Skill、标出当前用户缺哪些授权、给一个「补齐授权」的快捷入口。

## 一条没查过的链路：执行根本不读 DB 里的提示词

到这里，「让内置 Agent 能用」的清单看起来就是：模型加 `origin`、`is_runnable` 分叉、装配期 seed、Run 创建门禁分叉——两天量级的活。但把「创建 → 快照 → 执行」整条链路走一遍之后，发现真正的大鱼藏在水里：

`RunStartRequest` 只有 `run_id / question / session_id / skill_id / resources`——**没有提示词字段**。内部 runner 执行时用的是自己初始化时加载的配置 prompt，DB Agent 行上的 `system_prompt` 在 canonical Run 链路里根本没人读，只被一版旧编排器消费过。

也就是说：光修 `is_runnable`，内置 Agent 只是「建得出来、显示可用」；管理员精心填写的业务提示词是摆设，跑出来的行为和平台默认 Agent 一模一样。

要让它「按配置真的跑出区别」，得是第二档工作：把业务提示词送进执行链路，按「Runtime 基础 → Agent 业务 → 本次 Skill」固定顺序拼接，并且**在 Run 创建时就拼好冻进执行快照**——而不是执行时现查。否则声明文件后续一改，历史 Run 的含义跟着变，审计链就断了。快照冻结合并结果，「这条 Run 基于哪个版本的什么定义」才永远有据可查。

内部 runner 恰好有一个顺手的性质：它自己配置的那份 prompt（`SYSTEM_PROMPT.md`）天然就是拼接的第一层「Runtime 基础」。两层结构不用推翻任何现有设计，缺的只是把第二层递进去的那段管道。

## 沉淀：三类事实源

问题讨论完，发现贯穿始终的其实只有一个问题：**每类「内置事实」的事实源在哪**。仓库里绕了一圈，答案收敛成三类，各归各位：

| 事实长什么样 | 放哪 | 例子 |
|---|---|---|
| 少量标量、开关、阈值，环境相关 | config.toml 段 | 风险门的 `enabled=false`、超时、URL |
| 长文本、ops 拥有、要评审、条目会增多 | 声明目录 | 内置 Agent 定义、MCP server 启动声明、SKILL.md |
| 行为实现、绑定关系、每行可变状态 | 代码 + DB 行 | Runtime adapter、连接登记、启停 override |

判断触发信号从来不是「它是内置的」，而是三个条件是否同时成立：**内容是文本、改它不该发版、条目会长多**。风险门控全是数字和开关，一条都不中，所以它老老实实待在 config.toml；Runtime 实例的 endpoint 每个部署环境一个值，进 Git 只会造成配置漂移，所以它待在管理面维护的 DB 里；内置 Agent 的 prompt 三条全中，所以它进声明目录。

还有两条纪律，防止这个模式长歪：

1. **第二个真实案例出现之前，不再开新目录。** 边界靠需求撑开，不靠类比——否则三个月后会有七八个名义上「声明式」实际没人维护的目录。
2. **目录加载器要收敛成一套约定。** 现在 MCP declarations 和 Skill loader 已经是两套平行的「扫目录、解析、fail-fast、算内容哈希」实现，内置 Agent 是第三个。这次应该把共享部分抽出来——尤其是路径安全校验（目录必须 ops 拥有、运行时只读、不能落在 Agent 可写区），这种安全边界最容易在「照着上一个抄一份」时漏抄其中一行。

## 几点收获

- 「新增一类实体来源」的任务里，最值钱的检查不是画新页面，而是把现存的硬校验函数（如 `is_runnable`）逐条过一遍「新来源下这一项怎么办」。原型验证的是界面，领域模型里的 AND 才是会坏的地方。
- 承担审计语义的字段（checksum 类）永远给内容哈希，不留空、不造占位符。只要每类来源都能给出「定义内容的哈希」，表就不用分叉，审计问题就有统一句式的答案。
- 权限要不要随组合传递，答案基本永远是不要。授权粒度应该对齐审计粒度——挂在人身上的权限，才回答得了「谁能用这个」。
- 管理面填的字段，执行链路不读是最隐蔽的一类断裂。任何「配置了但没生效」的排查，都应该从配置一路走到 `start_run` 那一刻，看参数到底有没有出现在请求里。
- 「放哪」类决策（config / 目录 / DB）不是风格偏好，把「谁改它、内容是不是文本、有没有每行可变状态」三个问题一问，答案通常自己浮出来。问完记得再问一句：仓库里有没有人已经这么干过？先例比原则更有约束力。

相关阅读：这个链路里 Runtime、Adapter、Harness 的分工，之前整理过一篇[《Agent Runtime 详解》](https://www.zata.cc/p/agent-runtime-explained/)，可以和本文对照着看。
