---
title: "Agent 沙箱选型指南：隔离边界、产品对比与判断标准"
description: "从 Docker、gVisor、Wasm 到 E2B、Daytona、Modal、Runloop、Deno Sandbox 与 AgentCore，讲清 Agent 沙箱的隔离边界、产品特点和选型方法。"
date: 2026-09-02T18:00:00+08:00
image: images/index/index.svg
categories:
    - Agent
tags:
    - Agent Orchestration
    - Agent
    - Sandbox
    - Agent Security
    - Code Execution
draft: false
---

事情是这样的。

这两天我在给自己的通用 Agent Runtime 加代码执行能力。

前面都挺顺，模型接上了，文件能传了，多轮对话也存进 SQLite 了。然后我顺手看了一眼 Deep Agents 里面的 `LocalShellBackend`，发现只要换掉一行代码，Agent 就能直接运行 Shell。

那一瞬间确实有点爽。

前一秒它还只是个会聊天、会读文件的脑子，后一秒它就能写 Python、跑测试、装依赖、改项目。像是给一个飘在空气里的灵魂，突然塞进去一双手。

然后我又顺手看了一眼它的底层实现。

```python
subprocess.run(
    command,
    shell=True,
    cwd=str(self.cwd),
)
```

我当时就冷静了。

这哪是什么沙箱。

这分明是把我 Mac 的终端密码写在纸条上，然后递给了一个会自己做决定的 AI 牛马。。。

它当然能干活。但它也能读我的 `.env`，能翻 SSH Key，能删文件，能装软件，能访问网络。只要一次 Prompt Injection，一份被投毒的 README，或者模型单纯抽了一下风，事情就可能从「帮我跑个测试」变成「哥们你项目怎么没了」。

所以我开始认真研究 Agent 沙箱。

研究完以后，我发现这个领域最容易让人误解的地方，不是产品太少，而是大家把四五种完全不同的东西，全叫成了 Sandbox。

有的只是限制 Python 能调用哪些函数。

有的是共享宿主机内核的容器。

有的是一秒钟启动一台微型虚拟机。

还有的干脆给 Agent 准备了一台可以暂停、快照、分叉的云电脑。

名字都一样，安全边界差得十万八千里。

这篇文章，我就想把这件事彻底聊清楚。

不一定全对，我自己也还在给 Runtime 做选型。但至少下次再看到「安全执行任意代码」这几个字，我们可以先别急着信，先问一句。

你这个安全，到底安全在哪？

1

先把一个最大的误会拆掉。

工作目录，不等于沙箱。

很多 Agent 框架会让你配置一个 `workspace`，然后告诉模型，所有文件都在这个目录里操作。听起来像是给它圈了一块地，但如果底层只是普通的 `subprocess`，这个目录通常只决定命令从哪里开始运行。

Agent 依然可以执行 `cd ..`，可以读取绝对路径，也可以访问整个网络。

`chroot` 不是完整沙箱，Python 虚拟环境不是沙箱，Conda 不是沙箱，给 Agent 单独建个文件夹更不是沙箱。

甚至 `virtual_mode=True` 这种路径限制，也只能约束框架提供的 `read_file` 和 `write_file`。一旦 Agent 拿到了 Shell，它直接执行 `cat ~/.ssh/id_ed25519`，前面的路径规则就跟门口贴的「闲人免进」差不多。

LocalShellBackend 也一样。

它很适合你在完全可信的个人开发环境里快速试验，因为简单，快，而且没有云端延迟。但 Deep Agents 自己在源码里写得很直白，它没有进程隔离，没有资源限制，命令直接以当前用户权限在宿主机运行。

所以它是执行器，不是沙箱。

这句话可以记一下。

能执行代码，和能安全执行代码，中间隔着一整套基础设施。

那一套基础设施至少要回答5个问题。

Agent 能看到哪些文件，能不能碰宿主机，能不能访问网络，能拿到哪些密钥，CPU、内存、进程数和执行时间有没有上限。

少回答一个，那个洞以后都可能变成事故入口。

2

最轻的一层，是语言级沙箱。

典型代表是 WebAssembly、Wasmtime、Deno 权限系统，还有一些基于 QuickJS、Pyodide 的代码解释器。

这类方案不是给 Agent 一台完整电脑，而是给它一个能力受限的语言运行时。

以 Wasmtime 为例，WebAssembly 代码默认拿不到宿主机文件、网络和系统调用。它想读某个目录，宿主程序必须通过 WASI 明确把这个能力交给它。官方把这套模型称为 capability-based security，也就是你不给钥匙，它连门在哪里都不知道。[Wasmtime Security](https://docs.wasmtime.dev/security.html)

Deno 也有类似的味道。默认情况下，程序不能随便读文件、访问网络、读取环境变量或者启动子进程，必须显式添加 `--allow-read`、`--allow-net`、`--allow-env` 这类权限。[Deno Permissions](https://docs.deno.com/runtime/reference/permissions/)

这类沙箱最大的优点就是轻。

启动快，资源开销小，很适合让 Agent 做公式计算、数据转换、运行一小段 JavaScript 或 Python 子集。你有10万个用户，每个人偶尔让 AI 算个表格，没必要给每个人启动一台 Linux 虚拟机。

但限制也非常明显。

真实的软件工程世界，根本不是一个纯函数。

Agent 可能要运行 `git`，装 `npm` 包，调用 `ffmpeg`，编译 Rust，起一个 PostgreSQL，再用 Playwright 打开浏览器。到了这一步，语言级沙箱很快就会开始劝退你。

不是它不安全，而是它太安全了。

安全到很多活干不了。

所以我的判断很简单。如果你的 Agent 只运行短小、单语言、输入输出明确的代码，Wasm 或受限解释器非常香。如果你想做 Claude Code、Codex 这类真正的软件工程 Agent，就别硬拗了，直接往完整 Linux 环境走。

3

再往上一层，是容器。

也就是大家最熟悉的 Docker。

Docker 通过 Linux Namespace 隔离进程、网络和挂载点，再用 cgroups 限制 CPU、内存和 I/O。相比在宿主机直接跑 `subprocess`，已经安全了太多。Docker 官方的安全文档也把 Namespace、cgroups、Capabilities、seccomp 和 AppArmor 这些能力列为主要防线。[Docker Engine Security](https://docs.docker.com/engine/security/)

而且它真的太方便了。

一个 `Dockerfile` 就能把 Python、Node.js、浏览器和项目依赖钉死。镜像可以缓存，容器可以秒级创建，出了问题直接删掉重来。对本地开发、CI 和内部可信 Agent 来说，性价比高得离谱。

但普通 Linux 容器有一个绕不开的问题。

它和宿主机共享内核。

这就像酒店里每个房间都有自己的门锁，但大家共用同一套地基和管道。大多数时候完全够用，可一旦攻击者找到内核漏洞或容器配置错误，边界就可能被打穿。

如果你想保留容器的使用方式，又不想让应用直接面对宿主机内核，中间还有 gVisor 这条路。它用一个由 Go 编写的用户态应用内核拦截系统调用，Docker 和 Kubernetes 仍然可以通过 OCI Runtime `runsc` 来运行容器。代价也很直接，系统调用多的程序会慢一点，部分 Linux 能力不完全兼容。[What is gVisor](https://gvisor.dev/docs/)

所以 gVisor 很像夹在普通容器和虚拟机之间的一层。比共享内核的原生容器多一道墙，又没有完整虚拟机那么重。

更危险的往往还不是内核漏洞，而是我们自己手欠。

为了让 Agent 能构建镜像，顺手把 `/var/run/docker.sock` 挂进容器。

为了方便改代码，直接把整个项目甚至用户目录读写挂载进去。

为了少处理几个权限问题，加一个 `--privileged`。

好家伙。

三板斧下去，沙箱基本只剩图标了。

Docker 官方也明确提醒，能控制 Docker daemon 的用户，本身就拥有接近宿主机 root 的能力。因为它完全可以创建一个容器，再把宿主机根目录挂进去。[Docker daemon attack surface](https://docs.docker.com/engine/security/)

如果你只是做个人开发，Docker 容器依然是一个很现实的起点。但至少要做到非 root 用户、只挂载必要目录、禁止 privileged、不挂 Docker Socket、默认断网、限制 CPU 和内存、设置超时、执行后销毁。

一开始可能会有点烦。

尤其依赖缓存、文件同步、Git 权限这些东西，搞起来很容易让人想直接 `chmod 777` 然后躺平。但你相信我，沙箱配置里每一次为了省事而开的口子，最后都会变成 Agent 最自由发挥的地方。

4

比较骚的事来了。

就在很多人还把 Docker 容器当成 Agent 沙箱的时候，Docker 自己已经推出了一个就叫 Docker Sandboxes 的产品。

它不是普通容器套壳，而是给每个编码 Agent 启动独立的 microVM。每个沙箱有自己的内核、文件系统、网络和 Docker Engine，Agent 可以在里面 `sudo`、装包、跑 Compose，但碰不到宿主机的 Docker daemon。[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/)

而且它已经直接支持 Claude Code、Codex、Copilot、Cursor、Gemini、OpenCode 等一堆 Agent。[Supported agents](https://docs.docker.com/ai/sandboxes/agents/)

对本地开发者来说，这个方向我是真的觉得很对。

以前你要安全运行 Codex，大概有两个选择。要么自己折腾 Docker 和一堆安全参数，要么把代码扔给远程沙箱。现在变成一句命令。

```bash
sbx run codex
```

微虚拟机里甚至还有一套独立 Docker Engine。Agent 要构建镜像、起数据库、跑 Docker Compose，都在那台 VM 里面折腾。炸了也是炸自己的小房间，不会把宿主机 Docker 一锅端。

但这里有一颗非常值得提醒的雷。

Docker Sandboxes 默认会把当前工作区直接读写挂进 VM。Agent 在里面删除代码，你宿主机上的代码也会同步消失。官方提供 `--clone` 模式，让 Agent 在 VM 内的私有副本工作，原仓库只读挂载，但这不是默认值。[Docker Sandboxes Security](https://docs.docker.com/ai/sandboxes/security/)

所以真要用，我会优先开 clone 模式。

另外它默认禁止未授权的出站 TCP，凭证通过宿主机代理注入，请求发到被允许的域名时才补上真实密钥。这个设计非常关键，因为密钥压根不以明文进入沙箱。[Docker Sandbox Credentials](https://docs.docker.com/ai/sandboxes/configuration/credentials/)

这也是我研究这圈产品以后越来越在意的一条标准。

一个沙箱如果把 API Key 塞进环境变量，然后告诉我「放心，环境是隔离的」，我会打一个问号。

因为 Prompt Injection 不需要逃逸沙箱。Agent 自己就能执行 `env`，然后把 Key 发出去。

真正更稳的做法，是让密钥永远留在沙箱外面，由受控代理在指定域名的请求出口临时注入。

墙是一层。

不把金库钥匙放进墙里，是另一层。

5

如果要把这种微虚拟机能力做成云 API，最知名的玩家之一就是 E2B。

E2B 用 Firecracker microVM 运行沙箱。它的架构文档里讲得很细，每个 Sandbox 是一个有独立内核的 Linux 微虚拟机，模板会提前启动并做内存、磁盘和 VM 状态快照。创建沙箱时不是从零开机，而是恢复快照，文件系统再用 Copy-on-Write，只拉取真正访问到的数据。[E2B Architecture](https://github.com/e2b-dev/infra/blob/main/docs/ARCHITECTURE.md)

所以它能同时拿到两个以前看起来有点冲突的东西。

虚拟机级隔离，和接近容器的启动速度。

E2B 的产品心智也特别清晰，就是给 Agent 一台临时 Linux 电脑。你可以运行 Shell，可以读写文件，可以自定义模板。如果只是做数据分析，还有单独的 Code Interpreter SDK，直接运行 Python 或 JavaScript，并返回图表和执行结果。项目本身开源，也支持自托管。[E2B GitHub](https://github.com/e2b-dev/e2b)

如果你正在做一个模型无关的代码解释器、数据分析 Agent，或者需要大量短生命周期环境，E2B 很顺手。

它的问题也很现实。

这是远程环境，文件要上传，结果要下载，每次工具调用都有网络延迟。自托管虽然开源，但底下是 Firecracker、网络、快照、调度、对象存储和一整套控制面，绝不是周五下午 `docker compose up` 一下就能收工的东西。

我自己看完它的架构，只剩一个感受。

可以自己部署，和适合自己部署，完全是两回事。。。

6

Daytona 和 E2B 看起来很像，但气质不太一样。

E2B 更像给 AI 应用提供一个通用的安全执行层。Daytona 更像是给 Agent 准备完整、可组合、可长期工作的开发机。

Daytona 官方把 Sandbox 描述为拥有独立内核、文件系统、网络栈和 vCPU、内存、磁盘配额的计算环境，支持 Python、JavaScript、TypeScript、Shell、持久化会话和快照。[Daytona Documentation](https://www.daytona.io/docs/en/)

它比较打动我的一个设计，是 Secret 不一定要真的进入 Sandbox。

Daytona 可以在沙箱里只放一个占位 Token，出站 HTTPS 请求经过代理时，只有目标域名命中允许列表，代理才把占位符替换成真实密钥。沙箱里的代码看不到明文，日志里也不该出现明文。[Daytona Secrets](https://www.daytona.io/docs/en/secrets/)

这个能力对企业内部 Agent 特别重要。

因为很多 Agent 不是只跑一段 Python，它要拉私有仓库、访问内部 API、查数据库。你不可能永远断网，但你也绝对不想把一个万能 Token 塞给它。域名绑定的代理注入，至少把「能使用凭证」和「能偷走凭证」分开了一点。

Daytona 还支持有状态解释器、后台 Session、PTY 和长进程，比较适合 Coding Agent、数据流水线，以及需要多轮保留环境的任务。[Daytona Process Execution](https://www.daytona.io/docs/en/process-code-execution/)

如果你的 Agent 工作方式像一个工程师，要在同一台机器上连续干几十分钟甚至几小时，我会重点看 Daytona。

7

再往工程师工作站这个方向走，就是 Runloop。

它把沙箱叫 Devbox。

这个名字其实很诚实，因为它提供的已经不只是安全执行一段代码，而是一台面向 Agent 的云开发机。可以拉仓库、编译代码、跑浏览器、保留状态、暂停恢复，还能使用自定义 Blueprint 和 Snapshot。[Runloop Devbox](https://docs.runloop.ai/docs/devboxes/overview)

Runloop 最有意思的场景，是分叉。

假设 Agent 面前有3种修 Bug 的方案。你可以先给当前磁盘做一个快照，再从同一个快照启动3台 Devbox，让3个 Agent 各走一条路，最后跑测试选最好的那一个。[Runloop Snapshots](https://docs.runloop.ai/docs/devboxes/snapshots)

这一下就不只是安全问题了。

沙箱开始变成 Agent 的时间机器。

可以回滚，可以复制，可以并行探索。以前工程师在 Git 分支上做的事，现在整个操作系统状态都能分支。

当然，能力越完整，成本和生命周期治理就越重要。快照如果不清理，会一直占存储。长生命周期 Devbox 如果忘了暂停，账单也会用自己的方式提醒你什么叫长期记忆。

所以 Runloop 更适合复杂 Coding Agent、自动修复、代码评测和并行实验，不是拿来算 `1+1` 的。

8

Modal 又是另一种气质。

它本来就是 Serverless AI 基础设施，Sandbox 只是其中一个能力。所以它特别适合需要弹性并发、定制镜像，甚至 GPU 的 Agent 任务。

Modal Sandbox 可以动态创建容器，执行任意命令，保留同一沙箱里的状态，设置超时，也可以挂载 Volume。官方甚至专门给了 Claude Code 和 LangGraph Coding Agent 的完整例子。[Modal Sandboxes](https://modal.com/docs/guide/sandboxes)

比较夸张的是，你可以直接给 Agent 的沙箱挂一张 T4，让它在里面跑模型或处理视频。[Modal LangGraph Agent](https://modal.com/docs/examples/agent)

如果你的 Agent 要做的是普通代码解释，Modal 可能有点像开跑车送外卖。

但如果任务是视频生成、模型推理、GPU 数据处理，或者突然并发出几千个沙箱，Modal 的基础设施属性就出来了。它不是最纯粹的 Agent Sandbox 产品，但它是一个很强的通用计算平台。

这块选型其实看任务，不看名气。

要一台会长期工作的开发机，看 Daytona、Runloop。

要大量短时解释器，看 E2B、Deno Sandbox。

要 GPU 和 Serverless 弹性，看 Modal。

9

Deno Sandbox 是最近让我有点惊喜的一个新选手。

它不是前面讲的 Deno 语言权限系统，而是真正的 Linux microVM。官方文档显示，每个沙箱都在 Hypervisor 层隔离，毫秒级启动，可以执行命令、使用持久卷，并且默认是临时环境。[Deno Sandbox](https://docs.deno.com/sandbox/)

它在安全设计上也比较激进。

出站网络可以做严格策略，Secret 不进入环境变量，只在访问批准域名时由平台替换，而且会做结果脱敏。[Deno Sandbox Security](https://docs.deno.com/sandbox/security/)

目前它更像一个快速发展的新产品，默认资源和会话时长有明确限制，区域也不像成熟云厂商那么广。但对于 TypeScript、Deno 生态和边缘应用来说，它非常值得关注。

顺便说一句，这里特别容易混淆。

`deno run` 的权限沙箱，是语言级能力控制。

Deno Sandbox，是云端 Linux microVM。

一个名字，两层边界。

买东西之前真的得看说明书，不然很容易拿到一把儿童安全剪刀，然后以为自己租了一间银行金库。

10

如果公司已经深度在 AWS 里，Amazon Bedrock AgentCore Code Interpreter 会更顺。

它提供托管的 Python 执行环境，能做计算、数据分析、可视化和结果校验。网络可以选择 Sandbox、Public 或 VPC 模式，访问 AWS 资源则由 IAM Role 控制。[AgentCore Code Interpreter](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html)

它的优势不是「最适合所有 Agent」，而是 AWS 那套治理能力。

IAM、VPC、Security Group、CloudTrail、企业账户、合规控制，这些东西一旦进了大公司，比单纯启动快几十毫秒重要得多。Agent 要访问 S3、EFS、内部数据库，也有一条相对原生的路。

但 AWS 的代价大家也懂。

概念多，配置多，权限策略写着写着，人会逐渐进入一种我是谁我在哪的哲学状态。

LangSmith Sandbox 也属于生态型选择。它和 LangGraph、Deep Agents 的衔接自然，支持命令、文件、端口隧道和工作区权限。但截至我写这篇文章时，官方文档仍标记为 Private Preview，所以更适合已经重度使用 LangSmith、愿意跟着产品一起迭代的团队。[LangSmith Sandbox Permissions](https://docs.langchain.com/langsmith/sandbox-permissions)

11

聊了这么多，我做了一张尽量不骗人的表。

| 方案 | 隔离边界 | 最适合什么 | 最明显的短板 |
| --- | --- | --- | --- |
| LocalShellBackend | 没有隔离 | 可信个人实验 | 直接执行宿主机命令 |
| Wasm、受限解释器 | 语言运行时 | 短代码、计算、转换 | 系统工具和依赖受限 |
| 普通 Docker | 共享内核容器 | 本地开发、CI、可信内部任务 | 配置不当容易穿透边界 |
| Docker Sandboxes | 本地 microVM | Codex、Claude Code 等编码 Agent | 默认直挂工作区仍有风险 |
| E2B | 云端 Firecracker microVM | Code Interpreter、短时 Agent 任务 | 远程延迟，自托管复杂 |
| Daytona | 云端隔离开发环境 | 有状态 Coding Agent、企业内部 Agent | 引入外部平台与费用 |
| Runloop | 云端虚拟 Devbox | 长任务、快照分叉、并行修复 | 生命周期和存储治理更重 |
| Modal | Serverless 隔离容器 | 高并发、GPU、定制计算 | 对简单解释器可能偏重 |
| Deno Sandbox | 云端 Linux microVM | 快速临时环境、Deno 与 TS 生态 | 产品较新，资源与区域有限 |
| AgentCore | AWS 托管解释器 | AWS 企业环境、VPC 与 IAM 集成 | 云绑定和配置复杂度高 |
| LangSmith Sandbox | LangChain 托管沙箱 | LangGraph、Deep Agents 团队 | 当前仍处预览阶段 |

如果屏幕前的你，现在就在做自己的 Agent，我自己的不成熟建议是这样。

个人在 Mac 上玩 Coding Agent，先看 Docker Sandboxes，尽量用 `--clone`，别让 Agent 直接改宿主机工作区。只是偶尔跑一点可信代码，硬化后的 Docker 也够用。

做一个面向用户的 Code Interpreter，优先试 E2B、Deno Sandbox，或者 Daytona。先把文件上传、命令执行、超时、结果下载这条链跑通，再考虑自建。

做企业内部 Coding Agent，看 Daytona、Runloop，或者你所在云厂商的托管方案。重点不是 Demo 跑得多快，而是身份、审计、网络、密钥和数据驻留能不能交代清楚。

需要 GPU、高并发和复杂镜像，看 Modal。

已经全家桶 AWS，就认真评估 AgentCore，别为了技术洁癖硬造一套 IAM 和 VPC。

至于自己用 Docker 或 Firecracker 搭一套，我不是说不行。

但你得诚实评估一下，你到底是在做 Agent 产品，还是准备顺便创业做一家云计算公司。

12

最后再说几个我觉得比产品名字更重要的判断标准。

沙箱是不是每个用户、每个 Thread 独立。不同用户共用一个长生命周期环境，文件和进程串了，那就不是记忆，是串门。

网络是不是默认拒绝。只要默认全网可达，Prompt Injection 就有了天然的数据出口。

密钥是不是明文进环境变量。最好由外部代理按域名注入，而且日志、错误信息和响应都要脱敏。

宿主机目录是不是直接读写挂载。尤其 `.git/hooks`、CI 配置、IDE Task、`.claude`、`.codex` 这些文件，有些改动甚至不会出现在普通 `git diff` 里。

有没有 CPU、内存、磁盘、PID、输出大小和墙钟时间限制。超时只杀父进程不杀进程组，也可能留下一窝后台孤儿。

有没有快照和销毁策略。沙箱太短，装一次依赖等半天。沙箱太长，污染、成本和跨任务泄漏一起上来。

有没有完整审计。谁在什么时间，以哪个 Agent 身份，执行了哪条命令，读写了哪些文件，访问了哪个域名，最后退出码是什么。

还有一个经常被忘掉的点。

沙箱防得住代码逃到宿主机，但防不住 Agent 在沙箱里做坏事。

如果网络是开放的，Agent 仍然可以把用户上传的文件发走。如果你把数据库密钥放进去，它仍然可以把库删掉。如果它能调用宿主机上的高权限 MCP，那个 MCP 就是墙上新开的一扇门。

所以沙箱从来不是一句「安全了」。

它只是把事故半径，从整台电脑，缩小到一个可控房间。

我写到这里，突然想起计算机安全里一个特别老的原则，最小权限。

这个词听起来一点都不性感，甚至有点像公司安全培训里最容易被跳过的那页 PPT。

但 Agent 时代，它突然变得非常具体。

以前的软件权限是开发者写死的。一个图片处理程序，正常情况下不会突然决定去翻你的 SSH Key。

Agent 不一样。

它的能力边界是动态的，它会读新的内容，会形成新的计划，会把几个看起来无害的工具串起来。模型越聪明，越能自己找到完成目标的路，也越需要我们提前决定，哪些路从物理上就不应该存在。

这有点像养一只特别聪明的哈士奇。

你不能把家门钥匙、银行卡和电锯全扔给它，然后靠 System Prompt 写一句「你是一只可靠、简洁、不会拆家的狗」。

它今天不拆，不代表这套系统是安全的。

真正的安全，是它就算想拆，也只能拆自己的玩具屋。

回到我最开始那行 `subprocess.run`。

代码还是那几行，Agent 也还是那个 Agent。但当它从宿主机 Shell 被放进一个有独立文件系统、受控网络、外置密钥和资源上限的沙箱以后，它才真正从一个危险的 Demo，开始有了一点产品的样子。

手，是给了。

笼子，也得跟上。

大时代啊，朋友们。

以上，既然看到这里了，如果觉得不错，随手点个赞、在看、转发三连吧，如果想第一时间收到推送，也可以给我个星标⭐～

谢谢你看我的文章，我们，下次再见。

