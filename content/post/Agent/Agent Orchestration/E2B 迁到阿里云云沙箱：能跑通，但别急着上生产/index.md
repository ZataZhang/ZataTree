---
title: "E2B 迁到阿里云云沙箱：能跑通，但别急着上生产"
description: "把已有 E2B 应用搬到阿里云函数计算云沙箱的完整记录：三个环境变量就能跑通，但 Team / API Key / RAM 权限三层鉴权的边界、四档兼容清单、五个静默失效的接口、base 与 code-interpreter-v1 的默认值差异、browser / All-In-One 模板的 CDP 与鉴权细节、Snapshot 的命名与超时规则、六类配额约束，才是决定能不能上生产的东西。"
date: 2026-09-21T19:00:00+08:00
slug: "E2B 迁到阿里云云沙箱：能跑通，但别急着上生产"
image: images/index/index.svg
categories:
    - Agent
tags:
    - Agent Orchestration
    - Sandbox
    - E2B
    - 阿里云
draft: false
---

写《Agent 沙箱选型指南》那篇时，我把 E2B 放在「要做 Code Interpreter 就优先试」那一档。文章发出去以后有人在评论里追问：国内有没有对应的方案，网络和合规能不能绕过去。

当时我的回答挺敷衍的，大意是自托管虽然开源，但底下压着 Firecracker、快照、调度、对象存储和一整套控制面，不是周五下午 `docker compose up` 一下就能收工的。

后来才发现，阿里云函数计算（FC）已经把这件事做完了，而且做法相当取巧。

**它没有另起一套 SDK，而是直接兼容了 E2B 的数据面协议。**

于是问题就变成了一个特别诱人的形式：已有 E2B 应用，能不能只改几个环境变量就接上去？

我把一个跑在 E2B 上的小 Runtime 搬了一遍。结论是：**能跑通，而且真的就三个环境变量。但「跑通」和「能上生产」之间，隔着一页清单。**

这一页清单才是这篇想讲的东西。

> 本文对应的官方文档共 38 页，逐页的对照表放在最后一节「文档地图」，你可以按需跳转。

## 一、先把它跑起来

对象是阿里云函数计算的**云沙箱（FC Agent Sandbox）**——面向 AI Agent 和代码执行场景的云端隔离运行环境，按需创建，任务完成后释放。

它的[产品简介](https://help.aliyun.com/zh/functioncompute/product-overview-of-fc-agent-sandbox)写得挺克制：适合承载「不应该直接运行在业务服务进程内」的任务。举的例子是 AI 生成代码执行、数据分析、自动化脚本、依赖复杂的工具调用、临时 Web 服务。这句话其实已经划出了它的边界——**它不是一个通用计算平台，是一个给不可信代码用的执行槽。**

官方把可做的事分成五类：

| 场景 | 说明 |
| --- | --- |
| 运行 Agent 工具 | 给 Agent 一个独立执行环境，运行命令、处理文件、调用工具链 |
| 构建代码解释器 | 执行 Python / Shell 等代码，返回 stdout、stderr、文本结果或文件产物 |
| 处理临时数据任务 | 上传数据文件，在 Sandbox 内清洗、转换、分析、生成报告 |
| 启动临时服务 | 在 Sandbox 内起 HTTP 服务或开发服务器，通过端口访问地址调用 |
| 固化运行环境 | 用模板预装依赖、运行时和工具链，减少每次任务的初始化成本 |

### 核心对象先认一遍

迁移之前值得先花十分钟把这几个对象对上号，因为后面所有的兼容性讨论都是围绕它们展开的：

| 对象 | 作用 |
| --- | --- |
| **Sandbox** | 一次远端隔离执行环境。创建、用、销毁 |
| **Template** | 定义 Sandbox 启动时的运行环境（基础镜像、语言运行时、依赖、工具链） |
| **Commands** | 在 Sandbox 中执行命令或进程 |
| **Filesystem** | 管理 Sandbox 内的文件 |
| **Code Interpreter** | 执行代码片段并在多次执行间保持上下文，常用模板 `code-interpreter-v1` |
| **Network** | 访问 Sandbox 暴露的端口（`getHost(port)`） |
| **Storage** | 本地文件系统只服务当前任务；长期数据走 NAS / OSS |
| **FC Extensions** | 云上扩展：VPC、OSS 挂载、自定义域名、日志监控、Team 配额 |

### 先分清：Team、API Key 和 RAM 权限是三件事

这张表建议在看任何配置步骤之前先过一遍，因为它能省掉一段弯路：

| | Team | API Key | RAM 权限策略 |
| --- | --- | --- | --- |
| 是什么 | 资源隔离单元 | 数据面凭据 | 控制台 / OpenAPI 的操作授权 |
| 绑在谁身上 | 账号下的资源组 | 一个 Team | RAM 用户 / 用户组 / Role |
| 用在哪 | 划分项目和环境 | E2B SDK、CLI、兼容 HTTP API | 控制台、OpenAPI |
| 在哪里建 | 控制台 | 控制台 | RAM 控制台 |

**Team 是「项目 × 环境」的边界**，不是随便起的名字。Template、Sandbox、API Key、Volume 全都挂在 Team 下面，共用一个 Team 就等于这些资源互相全都可见，所以官方建议不同项目、测试和生产各用一个 Team，资源组则留给部门当边界。

然后是这次真正卡住我的地方。

**我一开始以为要跑通沙箱，得先把 RAM 权限配齐。** 这个判断是错的——但我错得挺有迷惑性，因为它「看起来」更安全。官方在[配置 RAM 用户权限](https://help.aliyun.com/zh/agent-sandbox/getting-started/configure-ram-user-permissions)里把两套鉴权分得很干脆：

> 通过 E2B SDK、E2B CLI 或兼容 HTTP API 创建和访问 Sandbox 时，使用 API Key，不需要配置 RAM 权限。

再换个说法：**RAM 权限管控制台和 OpenAPI，API Key 管数据面。** RAM 权限能让你在控制台管 Team、管 API Key、管 Volume；但你想创建一个 Sandbox 并往里跑代码，只认 API Key。文档的「常见误区」里专门点了这一条——**混淆 RAM 权限和 API Key**。

顺带一句，这份文档现在挂在 `help.aliyun.com/zh/agent-sandbox/` 下（产品名从「云沙箱」往「智能体沙箱 Agent Sandbox」上靠了），旧链接仍然能打开，但搜的时候别只按老名字搜。

**但如果你确实要用 OpenAPI 建模板，就会撞上我撞的那面墙。**

我在 RAM 控制台里翻权限策略，按 `fcsandbox` 搜，什么都搜不到；换「服务」下拉列表一个个翻，也没有。第一反应是「是不是我的账号权限太小，看不见这一项」——不是。

**原因很朴素：`fcsandbox` 不在可视化编辑器的服务下拉列表里。** 那个列表只收录注册过 RAM 元数据的服务，这个新产品没进去。而 RAM 创建策略时**并不校验 action 白名单**——你写什么它就存什么。所以正路是根本不要走可视化编辑：

1. RAM 控制台 → 权限策略 → 创建权限策略
2. 编辑方式选 **脚本编辑**，不要选可视化编辑
3. 手写 JSON

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "fcsandbox:*",
      "Resource": "*"
    }
  ]
}
```

这一份是「管理账号下全部 Agent Sandbox 资源」，不含函数计算或其他云服务权限。想收紧到指定地域，`Resource` 改成 `acs:fcsandbox:<region>:<account-id>:*`。

`Action` 的命名规则是 `fcsandbox:<接口名>`——你要找的「建模板、查模板、列模板、删模板」就是这四个字符串，**在控制台里是搜不到的，得直接写进策略**：

```json
"Action": [
  "fcsandbox:CreateTemplate",
  "fcsandbox:GetTemplate",
  "fcsandbox:ListTemplates",
  "fcsandbox:DeleteTemplate"
]
```

接口名去哪儿查？去 [Agent Sandbox 的 OpenAPI 文档](https://api.aliyun.com/document/FCSandbox/2026-05-09/overview)找到业务要调的那个接口，页面上「授权信息」一节会直接告诉你对应的 action 名。**别猜名字**——写错不会报错，只会在调用时静默变成 403。

想收紧到单个 Team 的话：

```json
"Resource": [
  "acs:fcsandbox:cn-beijing:<account-id>:teams/<team-id>",
  "acs:fcsandbox:cn-beijing:<account-id>:teams/<team-id>/*"
]
```

**两条 Resource 都要写，少一条会出那种「看得见但动不了」的怪状态**（文档专门提醒了这一条）：`teams/<team-id>` 是 Team 本身，`teams/<team-id>/*` 才是它下面的 Template / Sandbox / API Key。只给前者，用户能看见 Team，但建模板、建 Key 全都失败。

ARN 的完整形态是 `acs:fcsandbox:<region>:<account-id>:<resource-path>`，层级比想象的深一层：**Sandbox 没有带自己 ID 的 ARN**，它挂在 Template 下面，某个模板创建的沙箱是 `teams/<team-id>/templates/<template-id>/*`。所以「只允许用某个模板」这种粒度是能做出来的。

还有一条：**`fcsandbox` 没有配套的系统策略，只能自定义。** 如果你在「系统策略」里也搜不到，那是对的，不是漏配了什么。文档在「常见误区」里也点名了别图省事挂 `AdministratorAccess`——那会把函数计算和其他云服务的权限一起给出去。

所以回到开头：**先确认你走哪条路。** 只是拿 SDK / CLI 跑沙箱，这一节可以整段跳过，去控制台建 Team 和 API Key 就行；要在 OpenAPI 侧管 Team、Template、API Key 或 Volume，才需要上面这段策略。两种都做的话，记住它俩是**平行的两套凭据**，权限模型、轮换节奏和泄露影响面都不一样。

### 前置：先把 API Key 建出来

这一步没有捷径，必须去控制台。按[创建 API Key](https://help.aliyun.com/zh/functioncompute/create-api-key)的步骤，创建时有两个字段要填：

- **描述**：用来标识用途（开发环境 / 生产环境 / 某个应用 / 某个团队）。文档特别点了一句「不要只写 `test` 或 `default`」——因为后面要按描述筛 Key。
- **过期时间**：可以选永不过期，也可以自定义。**生产环境建议设明确的过期时间并建立轮换机制。**

创建完把完整 Key 复制出来存好。那句「不要写入代码仓库、镜像、模板、日志、截图、工单或前端页面」我不重复了，只说一个容易忽略的：**不要写进模板**——模板是会被复用和分发的。

Key 的管理操作有四个：编辑（改描述、改过期时间、启停）、**重置**（生成新值，旧值立刻失效，用旧值的应用会认证失败）、删除（必须先禁用，建议禁用后观察一段时间再删）。

### 三个环境变量

```bash
export E2B_API_KEY="<your-api-key>"
export E2B_API_URL="https://api.<region>.e2b.fc.aliyuncs.com"
export E2B_DOMAIN="<region>.e2b.fc.aliyuncs.com"
```

关于这三个变量，有几件事值得单独说清楚（[接入参数说明](https://help.aliyun.com/zh/functioncompute/e2b-sdk-integration-parameter-description)里有完整对应关系）：

**第一，SDK 会自动读它们。** 所以你会看到官方示例里有的显式传参、有的什么都不传——两种都对。显式传参的好处是排查时一眼能看到连的是哪个 endpoint，我在迁移阶段是坚持显式传的。

**第二，`E2B_API_URL` 和 `E2B_DOMAIN` 必须显式配置。** 官方 E2B 的示例代码通常不写这两个，因为默认就走 E2B 自己的服务。云沙箱是 FC 侧提供的**兼容端点**，不配就是连到 E2B 官方去了——你的阿里云 Key 在那边自然认不出来。

`E2B_API_URL` 是 SDK 访问云沙箱 API 的地址，`E2B_DOMAIN` 是 SDK 拼接沙箱服务访问地址时用的基础域名。两个都要给，因为控制链路和数据链路是分开的。

**第三，地域必须四处一致。** `E2B_API_URL`、`E2B_DOMAIN`、模板、Sandbox，任意一个不在同一账号或同一地域，现象都是「认证失败 / 模板不可见 / 创建失败 / 连接失败」。按[使用约束](https://help.aliyun.com/zh/functioncompute/usage-constraints-of-fc-agent-sandbox)，当前支持这八个：

| 地域 | region 值 |
| --- | --- |
| 华北 2（北京） | `cn-beijing` |
| 华东 2（上海） | `cn-shanghai` |
| 华东 1（杭州） | `cn-hangzhou` |
| 华南 1（深圳） | `cn-shenzhen` |
| 中国（香港） | `cn-hongkong` |
| 新加坡 | `ap-southeast-1` |
| 美国（弗吉尼亚） | `us-east-1` |
| 美国（硅谷） | `us-west-1` |

**第四，鉴权细节。** 如果你不走 SDK、直接调数据面 HTTP 接口，API Key 是放在 `X-API-KEY` 请求头里的。走 SDK 或 CLI 时，同一个 Key 传给 `api_key` 参数或设成 `E2B_API_KEY` 就行。

### 最小验证：Python

```python
import os
from e2b_code_interpreter import Sandbox


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"缺少环境变量: {name}")
    return value


sandbox = None

try:
    sandbox = Sandbox.create(
        template="code-interpreter-v1",
        api_key=require_env("E2B_API_KEY"),
        api_url=require_env("E2B_API_URL"),
        domain=require_env("E2B_DOMAIN"),
    )

    result = sandbox.commands.run("python3 -c \"print('hello from sandbox')\"")
    print(result.stdout.strip())
finally:
    if sandbox is not None:
        sandbox.kill()
```

### 最小验证：TypeScript

```typescript
import { Sandbox } from "@e2b/code-interpreter";

async function main() {
  const sandbox = await Sandbox.create("code-interpreter-v1", {
    apiKey: process.env.E2B_API_KEY,
    apiUrl: process.env.E2B_API_URL,
    domain: process.env.E2B_DOMAIN,
    timeoutMs: 300_000,
  });

  try {
    const result = await sandbox.commands.run("python3 -c \"print('hello from sandbox')\"");
    console.log(result.stdout.trim());
  } finally {
    await sandbox.kill();
  }
}

main();
```

看到 `hello from sandbox`，说明 SDK、API Key、Endpoint、域名和内置模板这五样东西全都通了。

### 版本会被钉住

[通过 SDK 使用云沙箱](https://help.aliyun.com/zh/functioncompute/using-the-cloud-sandbox-via-the-sdk)里明说了：**方法名和参数形态以你正在使用的 E2B SDK 版本为准。** Python 和 TypeScript 的命名风格还不一样。所以「兼容」这两个字是有版本前提的。

快速入门验证过的固定组合是：

| 语言 | 安装命令 | 运行时要求 |
| --- | --- | --- |
| Python | `pip install e2b==2.31.0 e2b-code-interpreter==2.8.1` | Python 3.10+ |
| TypeScript | `npm install e2b@^2.31.0 @e2b/code-interpreter@^2.6.1` | Node.js 20.18.1+ |

**别用 `latest`。** 生产项目应该把 lockfile 提交上去，升级依赖后重新跑一遍验证脚本。

还有一个具体的差异必须记住：**Python 的参数是 snake_case，TypeScript 是 camelCase。** Python 是 `api_key` / `api_url`，TypeScript 是 `apiKey` / `apiUrl`；Python 的 `timeout` 单位通常是**秒**，TypeScript 的 `timeoutMs` 是**毫秒**。排查时以当前语言 SDK 的类型定义为准，别把另一个语言的字段名复制过来——这种错不报错，只是悄悄用了默认值。

顺带一句：`E2B_ACCESS_TOKEN` 是 E2B 已经废弃的旧认证变量。新版本 CLI 和 SDK 统一用 `E2B_API_KEY`。如果旧版 CLI 还在要求那个变量，先升级 CLI 再重试。

## 二、这套兼容比我想的更深

一开始我以为所谓「兼容」就是照着 E2B 的接口抄了一遍，包一层自家 API。

不是的。**它兼容的是 E2B 的数据面协议。** 这句话的分量在于：只要协议对得上，第三方完全可以自己写 SDK。[接入参数说明](https://help.aliyun.com/zh/functioncompute/e2b-sdk-integration-parameter-description)里写得很清楚：云沙箱数据面以兼容 E2B SDK / CLI 为主，**未提供独立的数据面 SDK**；而 Team、API Key、Quota 这些**控制面资源**可以走原生 OpenAPI、阿里云 SDK 或阿里云 CLI。

阿里云函数计算团队就顺手把 Java 和 Go 的 SDK 写了——因为 E2B 官方只出 Python 和 TypeScript。见 [E2B SDK（Java 与 Go）](https://help.aliyun.com/zh/functioncompute/e2b-sdk-java-and-go)：

- Java：[aliyun-fc/e2b-java-sdk](https://github.com/aliyun-fc/e2b-java-sdk)
- Go：[aliyun-fc/e2b-go-sdk](https://github.com/aliyun-fc/e2b-go-sdk)

两个都还处于「以源码形式提供」的阶段，接入方式有点原生态：

```xml
<!-- Java：2.1.0 还没发到 Maven Central，得先克隆并 mvn clean install 到本地仓库 -->
<dependency>
    <groupId>com.alibaba.serverless</groupId>
    <artifactId>e2b-java-sdk</artifactId>
    <version>2.1.0</version>
</dependency>
```

```bash
git clone https://github.com/aliyun-fc/e2b-java-sdk.git
cd e2b-java-sdk
mvn clean install -DskipTests
```

```bash
# Go：go.mod 里声明的还是旧模块路径 github.com/e2b-dev/e2b-go-sdk，
# 该路径已经取不到了，得用 replace 指到本地目录
git clone https://github.com/aliyun-fc/e2b-go-sdk.git
cd myapp
go mod edit -replace=github.com/e2b-dev/e2b-go-sdk=../e2b-go-sdk
```

Go 这边有个细节挺反直觉：**虽然有本地替换，import 路径仍然要写旧模块路径**，才能和 SDK 当前 `go.mod` 的声明对齐。

```go
import e2b "github.com/e2b-dev/e2b-go-sdk"
```

Java 版有个挺讨喜的设计：`Sandbox` 实现了 `AutoCloseable`，退出 `try` 块就自动 `kill()`。

```java
ConnectionConfig config = ConnectionConfig.builder()
        .apiKey(System.getenv("E2B_API_KEY"))
        .apiUrl(System.getenv("E2B_API_URL"))
        .domain(System.getenv("E2B_DOMAIN"))
        .build();

try (Sandbox sandbox = Sandbox.create("code-interpreter-v1", config)) {
    CommandResult result = sandbox.getCommands().run(
            "python3 -c \"print('hello from sandbox')\""
    );
    System.out.println(result.getStdout().trim());
}
```

Go 版则是 `defer sandbox.Kill(...)`。两边都在用语言本身的机制替你兜住「忘记释放」这件事——这其实是一个挺重要的信号：**写这两个 SDK 的人知道，真正的生产事故里，「忘了 kill」比「调不通接口」更常见。**

但官方也提示了一句：**两个 SDK 实现的是 E2B 数据面协议，接口和默认值与 Python / TypeScript 并不完全一致。** 协议兼容不等于 API 表面对齐，接入前还是得看各自仓库的版本说明。

## 三、一页清单：什么能用，什么别用

这是我建议在动手之前先读完的东西——[E2B 兼容说明](https://help.aliyun.com/zh/functioncompute/e2b-compatibility-explanation)。它把能力分成四档，其中最有价值的不是「兼容」，而是后面三档。

| 能力模块 | 状态 | 关键说明 |
| --- | --- | --- |
| Sandbox | 兼容 | 创建、连接、查询、超时、终止、上传下载地址、端口访问；**暂停/恢复与 Snapshot 需白名单** |
| Commands | 兼容 | 命令执行、进程管理、标准输入、PTY |
| Filesystem | 部分兼容 | 读写、目录管理、重命名、删除、存在性检查、目录监听；**不支持文件自定义元数据** |
| Code Interpreter | 兼容 | 代码执行、上下文管理、流式输出、跨次执行状态保持；**不支持 Java 和 R**；上下文管理**仅 Python SDK** |
| Template | 兼容 | 模板 CRUD、构建、标签、别名 |
| CLI | 部分兼容 | 常用 Sandbox / Template 命令 |
| Metrics | 兼容 | CPU、内存可用；**磁盘/页缓存字段是占位值**，按 1 分钟粒度 |
| Logs / Network Config Update | **受限** | 接口可调用，但返回结果或实际效果存在限制 |
| Snapshots | 兼容（需白名单） | 仅第二代运行时可用，默认保留 7 天 |
| Volume / Access Token | **暂不兼容** | 不建议作为接入路径；Team 请在控制台管理 |

方法级的完整清单在 [E2B SDK 兼容 API 清单](https://help.aliyun.com/zh/functioncompute/e2b-sdk-compatible-api-list)里。下面按模块展开，方便你对着自己的代码库勾一遍。

### Sandbox：覆盖了完整生命周期

```text
Sandbox.create()                     创建
Sandbox.connect(sandboxId)           连接已有 Sandbox（已暂停时自动恢复）
Sandbox.list()                       列出 Sandbox
Sandbox.getInfo(sandboxId)           查询指定 Sandbox 信息
sandbox.getInfo()                    查询当前 Sandbox 信息
sandbox.isRunning()                  判断是否运行中
Sandbox.setTimeout(sandboxId, ms)    调整指定 Sandbox 超时
sandbox.setTimeout(ms)               调整当前 Sandbox 超时
sandbox.pause()                      暂停（需白名单）
sandbox.kill() / Sandbox.kill(id)    终止
sandbox.uploadUrl(path)              获取上传地址
sandbox.downloadUrl(path)            获取下载地址
sandbox.getHost(port)                获取端口访问地址
```

`Sandbox.create()` 支持的常用参数（[创建沙箱](https://help.aliyun.com/zh/functioncompute/create-a-sandbox)）：

| 参数 | 说明 |
| --- | --- |
| `template` | 模板名 / 模板 ID / Snapshot ID / 命名 Snapshot 全名 |
| `timeout` / `timeoutMs` | 沙箱超时，Python 秒 / TS 毫秒 |
| `envs` | 写入沙箱运行环境的环境变量 |
| `metadata` | 写入沙箱**控制面**的自定义元数据 |
| `secure` | 控制端点访问保护强度，见第四节 |

沙箱实例在生命周期内只有三个状态（[code-interpreter-v1 模板](https://help.aliyun.com/zh/functioncompute/code-interpreter-v1-template)）：`running`（就绪）、`paused`（已暂停，可恢复）、`terminated`（已终止）。

**关于超时**（[超时](https://help.aliyun.com/zh/functioncompute/timeout)）：可以在创建时设，也可以创建后用 `setTimeout()` 调。文档的提醒很短但很实在——设置过短任务会被提前回收，设置过长则增加资源占用和费用风险。以及老规矩：**超时不是释放。** 任务做完就 `kill()`，别指望超时回收，那个窗口期里资源一直在计费。

### Commands：批处理走 run，交互走 pty，长任务走后台

```text
sandbox.commands.run()        启动进程并等待结果
sandbox.commands.list()       列出运行中的进程
sandbox.commands.connect()    连接到已有进程
sandbox.commands.sendStdin()  发送标准输入
sandbox.commands.kill()       终止进程
```

三类任务三种走法（[运行命令](https://help.aliyun.com/zh/functioncompute/run-the-command) / [后台命令](https://help.aliyun.com/zh/functioncompute/backend-command) / [PTY](https://help.aliyun.com/zh/functioncompute/pty)）：

**批处理**用 `commands.run()`，同步拿结果。这是我见过的 95% 场景。

**后台进程**加 `background=True`，SDK 立刻返回进程对象，之后可以继续访问端口、连接进程或终止进程：

```python
try:
    process = sandbox.commands.run(
        "python3 -m http.server 8000",
        background=True,
        timeout=10 * 60,
    )

    host = sandbox.get_host(8000)
    print(f"https://{host}")

    running = sandbox.commands.list()
    print(running)

    process.kill()
finally:
    sandbox.kill()
```

这里有个**必须知道的默认值**：**命令执行超时默认通常只有 60 秒。** 后台进程不会因为 SDK 调用返回就自动结束，但**仍受命令超时约束**。所以起个长跑服务而不显式设 `timeout` / `timeoutMs`，它会在 60 秒后被掐。

另外文档的建议也值得照做：**需要持续读取输出的任务，用后台进程 + 连接进程，别用长超时的同步命令阻塞主流程。**

**交互式终端**用独立的 `sandbox.pty`：

```python
from e2b import PtySize, Sandbox

terminal = sandbox.pty.create(PtySize(rows=24, cols=80), timeout=0)
sandbox.pty.send_stdin(terminal.pid, b"python3 - <<'PY'\nimport sys\nprint(sys.stdout.isatty())\nPY\n")
sandbox.pty.send_stdin(terminal.pid, b"exit\n")
result = terminal.wait(on_pty=lambda data: print(data.decode(), end=""))
print(result.exit_code)
```

`pty.create()` 开一个伪终端会话，TypeScript 用 `sendInput()`、Python 用 `send_stdin()`，`terminal.wait()` 等退出。要断开后重连就保存 `terminal.pid`，再用 `sandbox.pty.connect(pid)`；窗口大小变了用 `resize()`。

PTY 的取舍文档列得很干脆：

| 适合 PTY | 不适合 PTY |
| --- | --- |
| 需要模拟真实终端行为的命令 | 只需要稳定解析 stdout/stderr 的批处理 |
| 工具在非 TTY 环境下会关掉颜色/进度/交互 | 需要严格区分 stdout 和 stderr 的任务 |
| 需要给交互式进程发标准输入 | 大量结构化日志输出（PTY 会改格式，解析成本变高） |

**一句话：默认用 `commands.run()`，只有命令明确依赖终端行为时才升到 PTY。** 我见过有人为了「保险」全部走 PTY，结果输出里混进一堆 ANSI 控制字符，正则全废。

### Filesystem：够用，但不要当存储

```text
sandbox.files.list()                    列出目录内容
sandbox.files.exists()                  判断路径是否存在
sandbox.files.getInfo() / get_info()    元信息
sandbox.files.read()                    读文件（默认文本，可读为 bytes / 流）
sandbox.files.write()                   写文件（文本 / bytes / 流；TS 支持批量）
sandbox.files.makeDir() / make_dir()    创建目录
sandbox.files.remove()                  删除
sandbox.files.rename()                  移动或重命名
sandbox.files.watchDir() / watch_dir()  目录监听
```

细节见[读写文件](https://help.aliyun.com/zh/functioncompute/read-and-write-files)。几个实用行为值得记：

- **`write()` 会自动创建缺失的父目录**，写入已存在文件时直接覆盖。所以 Python 那边写两个文件其实不用先 `make_dir`——官方示例里先建目录只是习惯。
- **TypeScript 支持一次写入多个文件**，适合把 Agent 生成的代码、测试文件、配置一起丢进去：

```typescript
await sandbox.files.write([
  { path: "/tmp/project/main.py", data: "print('hello')\n" },
  { path: "/tmp/project/README.md", data: "# Demo\n" },
]);
```

- **二进制也支持**：Python 写 `bytes` 和文件对象，读的时候 `format="bytes"`；TypeScript 写 `ArrayBuffer`、`Blob`、`ReadableStream`。

**目录监听**是个被低估的能力——等 Agent 输出文件、同步任务产物，比轮询 `exists()` 优雅得多。只等单个文件时，可以退回 `exists()` 做有限次数轮询。

### Code Interpreter：核心能力齐全，但减法不止一个

```text
sandbox.runCode() / run_code()
sandbox.createCodeContext() / create_code_context()
sandbox.listCodeContexts() / list_code_contexts()
sandbox.restartCodeContext() / restart_code_context()
sandbox.removeCodeContext() / remove_code_context()
```

输出侧有 stdout、stderr、execution count、裸表达式结果，以及 `execution.results` 富结果；流式场景下还有 stdout / stderr / 结果回调。**同一 Context 内变量和执行状态会保持**——这也是 Code Interpreter 和「每次新起一个进程跑脚本」的本质区别。

但[code-interpreter-v1 模板](https://help.aliyun.com/zh/functioncompute/code-interpreter-v1-template)那页列出的减法比兼容说明里写的更多：

**一是不支持 Java 和 R。** `language` 参数只认 Python、JavaScript、TypeScript、Bash；`run_code` 的 `language` 默认是 `python`。

**二是图表只有降级方案。** 官方原话是「在 Sandbox 内生成图片文件后，通过 Filesystem 或下载 URL 取回」。没有「直接返回一个图片对象」那条路。如果你原来的实现依赖 SDK 直接吐出 png，这里要改。

**三是上下文管理当前只有 Python SDK 能用。** 这条我觉得是整页里最容易被忽略的：TypeScript 的 `runCode` 能正常执行代码，但 `createCodeContext` / `listCodeContexts` / `restartCodeContext` / `removeCodeContext` **当前在本平台不可用**，需要管理独立上下文只能换 Python SDK。做跨语言迁移的话，这一条会直接把方案卡住。

**四是 `logs.stdout` / `logs.stderr` 是字符串列表**，不是字符串。要 `"".join(...)`（Python）或 `.join("")`（TypeScript）拼起来才是完整文本。

`run_code` 的主要参数和默认值：

| 参数 | 说明 |
| --- | --- |
| `code` | 要执行的代码 |
| `language` | `python` / `javascript`，未指定默认 `python`；**与 `context` 互斥** |
| `context` | 指定在哪个代码上下文执行；**与 `language` 互斥** |
| `timeout` / `timeoutMs` | 执行超时，**Python 默认 300 秒，TypeScript 默认 60000 毫秒** |
| `envs` | 自定义环境变量 |
| `on_stdout` / `onStdout` 等 | 流式回调，逐行接收 stdout / stderr / 结果 / 错误 |

执行结果 `Execution` 包含：`logs`（stdout / stderr 列表）、`results`（末表达式结果，含 `text` 文本表示）、`error`（执行异常）、执行计数（Python `execution_count` / TS `executionCount`）。

上下文隔离的行为也很直观：默认上下文里 `x = 42` 之后另一个 `run_code("print(x)")` 能读到；但你 `create_code_context()` 出来的独立上下文里定义的变量，默认上下文**读不到**（会拿到 `NameError`）；`restart_code_context()` 之后变量被清空。

```python
ctx = sbx.create_code_context(language="python", cwd="/home/user")
sbx.run_code("y = 100", context=ctx)
sbx.run_code("print(y)", context=ctx)   # 100

sbx.run_code("print(y)")                # NameError：默认上下文看不到 ctx 的变量
```

`create_code_context` 需要指定 `language`，`cwd` 默认 `/home/user`。`run_code` 的 `context` 参数要传 `Context` 对象；`restart_code_context` / `remove_code_context` 传对象或 ID 字符串都行。

另外从构建模板的官方脚本里还能看到更细的返回值形态，注意这里**有两个超时参数**：

```python
execution = sandbox.run_code("print('hello')", timeout=60, request_timeout=120)

stdout = "".join(execution.logs.stdout or [])
stderr = "".join(execution.logs.stderr or [])
print(execution.error)
```

`timeout` 管代码执行，`request_timeout` 管这次请求本身。**这两个别混。** 后面讲 Snapshot 的时候会看到，混了会很贵。

### Template 与 CLI

模板侧支持 CRUD、构建、标签、别名。CLI 侧的兼容表（[通过 CLI 使用云沙箱](https://help.aliyun.com/zh/functioncompute/using-the-cloud-sandbox-via-the-cli)）：

| 命令 | 状态 | 说明 |
| --- | --- | --- |
| `sandbox create <template>` | 支持 | 创建沙箱并连接交互式终端，**退出终端后自动终止该沙箱** |
| `sandbox list` | 支持 | 默认返回运行中的；可用 `--state`、`--metadata`、`--limit`、`--format` |
| `sandbox kill` | 支持 | 按 ID 终止，也支持 `--all` 批量终止 |
| `sandbox connect` | 支持 | 连接已有沙箱；**退出终端不会自动终止** |
| `sandbox exec` | 支持 | 在运行中的沙箱内执行命令，输出回到本地终端 |
| `sandbox metrics` | 支持 | CPU、内存，分钟级粒度 |
| `template list` | 云沙箱扩展 | E2B 官方 CLI 文档未单独说明该命令 |

**`create` 和 `connect` 在退出终端时的行为是相反的**，这一点特别容易咬人：`e2b sandbox create` 退出就把沙箱杀了，`e2b sandbox connect` 退出则留着。调试时用错一个，要么白等一遍启动，要么留下一堆僵尸沙箱在账单上。

CLI 的安装与配置：

```bash
brew install e2b                      # macOS
npm i -g @e2b/cli@2.20.0              # 或者用 npm
e2b --version                         # 装完先确认版本

export E2B_API_KEY="<your-api-key>"
export E2B_API_URL="https://api.<region>.e2b.fc.aliyuncs.com"
export E2B_DOMAIN="<region>.e2b.fc.aliyuncs.com"

e2b sandbox list                      # 用一条只读命令验证配置
e2b template list                     # 看当前账号有哪些模板
```

CLI 不固定单一版本，官方建议用最新兼容版本。**如果命令行为和文档不一致，先跑 `e2b --version` 和对应命令的 `--help`**，确认本机 CLI 的版本和参数形态，而不是先怀疑文档。

## 四、五个会静默骗你的坑

这部分是我觉得最有信息量的。它们有的抛异常、有的不抛，但共同点是：**都不会告诉你「你要的功能其实没生效」。**

### 坑一：`files.write()` 的 `metadata` 参数

云沙箱当前不支持文件自定义元数据。但 SDK 的方法签名**是接受 `metadata` 的**——Python SDK 会在请求发出去之前自己拦下来，报的错长这样（[自定义元数据](https://help.aliyun.com/zh/functioncompute/custom-metadata)）：

```text
e2b.exceptions.TemplateException:
File metadata requires envd 0.6.2 or later.
```

原因写得很清楚：Sandbox 当前上报 `envd 0.5.2`，而文件自定义元数据需要 `envd 0.6.2` 或以上。普通文件读写完全不受影响。

那页文档还补了一句很关键的：**「升级 SDK 或仅修改 `envd` 版本号声明无法绕过限制」**——该能力需要运行环境完整支持元数据校验、键名小写化和扩展属性持久化。所以这不是一个「等版本」的问题，是后端还没实现。

顺手澄清一个容易混的概念，这个混淆我自己也犯过：

| | 文件自定义元数据 | Sandbox `metadata` |
| --- | --- | --- |
| 挂在哪 | 单个文件上 | 沙箱控制面 |
| 写入方式 | `files.write(..., metadata=...)` | `Sandbox.create(..., metadata=...)` |
| 当前可用 | **否** | 是 |
| 典型用途 | 给文件打业务标签 | 标记任务、用户、场景、版本，便于列表过滤和审计 |

控制面 `metadata` 的用法是这样的（[元数据](https://help.aliyun.com/zh/functioncompute/metadata)），创建时写、`getInfo()` 读，也能用来过滤 `Sandbox.list()`：

```python
sandbox = Sandbox.create(
    template="code-interpreter-v1",
    metadata={"task_id": "task-001", "agent": "code-reviewer"},
)

info = sandbox.get_info()
print(info.metadata)
```

有个细节文档专门强调了：**元数据不会自动变成沙箱内的环境变量。** 如果同一个字段既要管理面可见、又要沙箱内进程能读到，得同时写进 `metadata` 和 `envs`。

元数据的取值建议用短字符串，只放可索引的关联 ID。大段上下文、用户隐私、凭证都不要塞进去。

**那文件标签怎么做？** 文档给了三条替代路径，我按推荐度排了一下：

1. **标签存业务库或对象存储**，用「Sandbox ID + 文件路径」做关联键。这是最干净的。
2. **同目录写一个 JSON 清单文件**，记录文件路径和业务标签。需要跨 Sandbox 保留时，把文件和清单一起写进 NAS / OSS。
3. **如果只是想标记 Sandbox 本身**，直接用控制面 `metadata`——但别把它当文件元数据用。

### 坑二：`run_code` 用错了 SDK

这个坑卡了我一会儿。现象是：Sandbox 创建成功，`commands.run()` 正常，但 `run_code` 就是不行。

原因是 SDK 装错了。**通用 `e2b` SDK 只能使用文件、命令和进程这些基础能力**——即使你指定了 `code-interpreter-v1` 模板，也一样调不了 `runCode` / `run_code`。

而这个坑有一半责任在**默认值**上。官方模板文档列得很清楚：

| SDK | `template` 要不要传 | 不传时的默认模板 |
| --- | --- | --- |
| `e2b_code_interpreter`（Python）/ `@e2b/code-interpreter`（TS） | **不用传** | `code-interpreter-v1` |
| `e2b`（通用） | **必须传** | **`base`** |

**通用 SDK 不传模板拿到的是 `base`，而 `base` 不提供 Code Interpreter 服务。** 所以「我用通用 SDK + 不指定模板 + 调 run_code」和「我用通用 SDK + 指定 code-interpreter-v1 + 调 run_code」，失败原因其实不同：前者连模板都不对，后者模板对了但 SDK 不对。

判断顺序也简单：先用内置 `code-interpreter-v1` 模板跑通代码执行、命令执行、文件读写。内置模板正常而自定义模板不行，再去查自定义模板的 Code Interpreter 依赖、启动命令、监听端口和就绪条件。

### 坑三：上传下载 URL 需要 `secure=false`

这个坑不报错，但它会让一个「看起来已经写好的」浏览器直传链路在最后一跳 403。见[上传和下载文件](https://help.aliyun.com/zh/functioncompute/upload-and-download-files)。

`sandbox.downloadUrl(path)` 和 `sandbox.uploadUrl(path)` 生成的是带签名的访问地址，适合浏览器直传、把结果文件交给未持有 SDK 鉴权信息的环境，或者交给后续系统处理。但文档里有一句加粗的注意：

> 如果要使用 `downloadUrl()` 和 `uploadUrl()` 返回的 URL 上传下载文件，**确保在创建 Sandbox 时显式设置了 `secure=false`**。否则，通过 URL 上传下载文件仍需要请求方携带 `X-Access-Token`。

```python
sandbox = Sandbox.create(..., secure=False)
```

而 `secure=false` 的代价文档也写得很直白：**会降低 Sandbox 暴露端点的访问保护强度。** 所以要配合「控制 Sandbox 生命周期、文件路径、数据敏感性」一起用。

我自己的取舍是：如果只是后端之间传文件，宁可不省这一下，直接用 `files.write()` / `files.read()`。只有「浏览器直传」这种真的拿不到 SDK 凭证的场景，才开 `secure=false`，并且把路径写死在业务侧、不让它由模型决定。

选型标准文档给得也挺清楚，直接抄：

| 场景 | 用什么 |
| --- | --- |
| 小文件、文本、二进制、流式内容、Agent 生成代码 | `files.write()` / `files.read()` |
| 浏览器直传、下载结果文件、交给无 SDK 鉴权环境 | `uploadUrl()` / `downloadUrl()` + `secure=false` |
| 目录遍历、重命名、删除 | Filesystem API |

浏览器直传的接收端用 `multipart/form-data`，字段名是 `file`：

```python
import requests
with open("input.csv", "rb") as f:
    requests.post(upload_url, files={"file": f}).raise_for_status()
```

**大文件上传后建议用 `sandbox.files.exists()` 或命令确认文件可读**——文档专门提了这句，说明「上传成功但文件不可读」是有过的。

### 坑四：Logs 和 Network Config Update

这两个是官方明确标记为「受限」的：

- **Sandbox Logs**：当前返回空数组。
- **Network Config Update**：当前返回成功，但**不进行实际的网络变更**。

官方对它们的定位说得很坦诚——「用于保持 SDK 调用兼容」。所以它们可以留着，让老代码不至于跑挂；但**不能作为生产日志采集或网络治理的控制面依赖**。接入参数说明那页也把它们列进了「不作为接入参数的能力」。

第二个尤其阴。返回 `success` 的操作什么都不做，这种设计在本地联调时完全看不出来，只有到线上要改网络策略、发现改了没生效的时候才会撞上。

正路是：**日志走函数计算日志采集 + 日志服务，网络变更走云沙箱控制面**（[监控与日志](https://help.aliyun.com/zh/functioncompute/monitoring-and-logging)）。而且更进一步——「生产排查应依赖业务侧结构化日志、函数计算日志采集、云监控和日志服务中的数据」。

配合这个结论，文档给了一段挺实用的日志约定：在业务侧记录 `sandbox_created` / `command_finished` 这类事件，字段带上 `taskId`、`sandboxId`、`exitCode`、stdout / stderr 摘要，并且**业务系统要保存任务 ID 与 `sandboxId` 的映射**。

```python
print(json.dumps({
    "event": "command_finished",
    "taskId": task_id,
    "sandboxId": sandbox.sandbox_id,
    "exitCode": result.exit_code,
    "stdout": result.stdout.strip(),
    "stderr": result.stderr.strip(),
}))
```

如果希望沙箱内的程序日志也能被日志服务检索，就让程序直接输出结构化 JSON、并带上 `sandboxId` 和任务 ID。两条日志流最后在日志服务里能按 `taskId` 关联起来。

**关于日志采集配置，文档提醒了三件事要先确认**：配置入口（以云沙箱控制台 / 函数计算控制台 / 日志服务为准，控制台没展示入口就联系产品支持）、生效范围（对账号 / 地域 / 模板 / Sandbox / 会话生效，以及是否只影响新建的 Sandbox）、日志目标（Project、Logstore、索引字段、保存时间和费用策略）。第三项最容易被忽略——**日志费用是那种平时不痛、月底很痛的东西**。

### 坑五：Metrics 的磁盘字段

`e2b sandbox metrics <sandbox-id>` 能看 CPU 和内存，但**磁盘 / 页缓存字段返回的是占位值**，不能用来判断容量。数据按 1 分钟粒度返回。

官方给的建议是：计费、告警、容量治理都要以函数计算控制台、云监控或日志服务里的正式数据为准。指标接口适合调试和看趋势，别拿去搭容量大盘——**1 分钟粒度配占位字段，做成大盘只会得到一条看起来很有道理、实际上是假的曲线。**

## 五、Snapshot 和 pause：白名单能力，别写进架构

### Snapshot 比「兼容」两个字复杂得多

我一开始是照「不兼容」处理的，后来翻[快照（邀测）](https://help.aliyun.com/zh/functioncompute/snapshots)发现已经变了。**Snapshots 现在兼容，但要加白名单，而且仅限第二代运行时（`micro-sandbox`）。**

它的心智模型很好理解：**保存运行中沙箱在某一时刻的文件系统与内存状态，之后用这份快照秒级启动一个同样状态的新沙箱，不必重新构建模板。** 典型场景就是 Agent 任务断点续跑、环境预热、并行克隆探索。

几个关键属性：

- **Snapshot 独立于源沙箱和源模板。** 删除源沙箱或源模板不会删掉 Snapshot；删 Snapshot 也不会影响它们。创建成功后即使源模板被删，仍能用该 Snapshot 恢复沙箱。
- **默认保留 7 天**，到期自动过期，过期后不出现在列表里、也不能用于创建沙箱。
- **留存独立于源沙箱生命周期**——源沙箱终止或超时回收后，未过期的 Snapshot 仍可用。

API 表（注意 Python 和 TypeScript 的名字差异）：

| 操作 | TypeScript | Python |
| --- | --- | --- |
| 创建 | `sandbox.createSnapshot({ name? })` / `Sandbox.createSnapshot(sandboxId, { name? })` | `sandbox.create_snapshot(name=...)` / `Sandbox.create_snapshot(sandbox_id, name=...)` |
| 列表 | `Sandbox.listSnapshots({ sandboxId?, name?, limit?, nextToken? })` | `Sandbox.list_snapshots(sandbox_id=..., name=..., limit=..., next_token=...)` |
| 从快照建沙箱 | `Sandbox.create(snapshotId \| "<TeamName>/<短名>")` | `Sandbox.create(template=snapshot_id \| "<TeamName>/<短名>")` |
| 删除 | `Sandbox.deleteSnapshot(snapshotId \| qualifiedName)` | `Sandbox.delete_snapshot(snapshot_id \| qualified_name)` |

实例方法和静态方法语义相同——实例方法隐含当前沙箱，不用再传 ID；**列表和删除只提供静态方法**。

返回字段里有两个：`snapshotId` / `snapshot_id` 是 UUID，创建、删除、恢复时**优先用它**；`names` 是有名快照的全名列表，无名快照是空数组。**两者相互独立**——全名只出现在 `names` 字段和按名解析里，不替代 ID。

**命名规则是这里最容易踩的地方。** 全名格式是 `<当前 Team 名>/<短名>:<tag>`：

- 短名和 tag 的规则是 `^[_a-zA-Z][-_a-zA-Z0-9]*$`，最长 64，必须以字母或下划线开头。
- Team 名前缀与 Team 展示名相同，最长 32，允许数字开头和空格、点、下划线、连字符（例如默认 Team 的数字名、`My Team`）。
- 段内不能含 `/` 或 `:`，所以「含且仅含一个 `/` 的字符串」只可能是 Snapshot 全名，不会和模板名冲突。

| 传入的 `name` | 结果 |
| --- | --- |
| 省略 / 空 | 无名，`names = []`，只能通过 Snapshot ID 访问 |
| `deps-ready` | `<当前 Team 名>/deps-ready:default` |
| `deps-ready:v1` | `<当前 Team 名>/deps-ready:v1` |
| `demo-team/deps-ready` | `demo-team/deps-ready:default`（前缀必须等于当前 Team 名，大小写不敏感） |

省略 tag 等价于 `default`。同一 Team 内同一个 `(短名, tag)` 同时只能存在一份可用 Snapshot，**名称冲突时创建失败，不覆盖已有快照**，删除后名称立即释放。**Team 没有名字时只能创建无名 Snapshot**。

**然后是那个我觉得最实用的坑：请求超时。**

创建可能持续数分钟。文档明确建议 **SDK 请求超时不少于 300 秒**（TypeScript `requestTimeoutMs: 300_000`；Python `request_timeout=300`）。并且特意点破了那个容易混的点：

> `timeoutMs` / `timeout` 控制的是沙箱生命周期，**不是 Snapshot 请求超时**；默认请求超时通常为 60 秒，不加大时可能在创建完成前失败。

60 秒默认值 + 数分钟的实际耗时 = 一个会间歇性失败的接口。而更麻烦的是它失败之后的处理：

> 创建超时：创建失败，但**服务端可能已建成 Snapshot**。先增大超时。有名 Snapshot 按 `name` 或全名列表确认后再决定是否重试；无名 Snapshot 的 `name` 过滤无效，应先按源沙箱 `sandboxId` 列表核对；**若已存在目标 Snapshot，直接使用其 ID，不要无条件重试。**

「不要无条件重试」这六个字是整篇文档里我最想圈出来的一句。它意味着一个朴素的重试装饰器在这里会持续制造垃圾快照，而每一份都在算存储费。

还有个更隐蔽的：**创建成功后立即调用列表接口，由于索引延迟，可能暂时看不到刚写入的记录。** 但按 ID 或全名恢复、删除都不受影响，可以直接用创建接口返回的值——所以别用「列表里没有」来判断创建失败。

失败条件我整理成表：

| 条件 | 结果 |
| --- | --- |
| 源沙箱不存在或不属于当前调用方 | 创建失败 |
| 沙箱运行时不是 `MicroVM` | 创建失败 |
| 名称非法，或全名前缀不是当前 Team 名 | 创建失败 |
| Team 无名却传了 `name` | 创建失败 |
| 同名同 tag 已存在 | 创建失败，不覆盖 |
| 源沙箱已暂停 / 正在创建 Snapshot / 被其他操作占用 | 创建失败 |
| 从 Snapshot 创建时覆盖环境变量、挂载或镜像 | 创建失败 |
| Snapshot 仍被已恢复沙箱占用 | 删除失败 |
| 按全名恢复或删除但 Snapshot 不存在 | 失败，**不回退为模板** |

创建过程中源沙箱的 `state` 是 `snapshotting`，此时**不能删除该沙箱**；失败则是 `snapshot_failed`，这个状态**默认不出现在沙箱列表里**，得显式按状态过滤才看得到。这一点挺关键——排查「为什么快照没建出来」时，默认列表里是找不到线索的。失败后源沙箱仍可使用或删除。

从 Snapshot 创建沙箱时，哪些参数能覆盖也有明确清单：

- **允许覆盖**：超时、空闲超时、`secure`、`allowInternetAccess`、用户 metadata、`autoPause`、`autoResume`、网络、自定义沙箱 ID。
- **不允许覆盖（传入即失败）**：环境变量、卷 / 文件系统挂载、函数配置、构建 / 镜像、`fc.` 前缀的系统 metadata。

以及一个 TS 特有的坑：**`listSnapshots` / `createSnapshot` / `deleteSnapshot` 的静态调用要走环境变量配 `E2B_API_URL`，不要传不被支持的 `apiUrl` 字段。**

最后一条使用建议我觉得挺值得照做：**没用的 Snapshot 及时删，避免持续产生存储费用；能短时暂停就优先用暂停与恢复，不要动不动就快照。** 7 天保留期是一个「会悄悄花钱」的默认值。

### pause：只为短期保留上下文

`sandbox.pause()` 同样需要白名单（[暂停与恢复](https://help.aliyun.com/zh/functioncompute/pause-and-resume)）。它的语义是「在一段时间内保留状态，之后连同一个 Sandbox 继续用」。`Sandbox.connect(sandboxId)` 连一个已暂停的沙箱时会自动恢复。

```python
sandbox.pause()
# 之后
sandbox = Sandbox.connect(
    sandbox_id,
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
)
```

文档里有三句提醒，我原样保留，因为它们都很容易忽略：

- 恢复后要**重新确认长连接、进程状态和业务层状态**是否符合预期。暂停期间那些东西的存活不能想当然。
- **暂停不等于终止。** 任务完成后仍然要 `kill()`。
- 对需要短期保留上下文的任务才用暂停，不要拿它替代资源释放。

**我的整体判断是：白名单能力不要写进架构。** 白名单是账号级的开关，今天开了明天能关，把它当成设计前提，等于把系统的可用性挂在一个后台配置上。Snapshot 可以当作「运维手段」和「性能优化」，但不要把「断点续跑」做成唯一路径——至少留一条「重建环境」的兜底。

## 六、模板：三个档位，和一个必须自己构建的

模板是这次迁移里我改动最大的一块。内置模板不是「一堆可选镜像」，而是三个能力档位，而且**默认值会咬人**。

### 内置模板清单

[内置模板](https://help.aliyun.com/zh/functioncompute/built-in-templates)一共三个，另有若干需要自行构建：

| 模板 | 需要构建 | 适用场景 | 说明 |
| --- | --- | --- | --- |
| [`base`](https://help.aliyun.com/zh/functioncompute/base-template) | 否，开通即用 | 基础命令、文件访问、SDK 连通性验证 | **不提供 Code Interpreter 服务** |
| [`code-interpreter-v1`](https://help.aliyun.com/zh/functioncompute/code-interpreter-v1-template) | 否，开通即用 | AI Agent 代码执行、数据分析、文件处理 | 快速入门和代码解释器示例默认用它 |
| [`browser`](https://help.aliyun.com/zh/functioncompute/browser-template) | **是** | 浏览器自动化、截图、动态页面抓取 | 要从官方 browser 镜像构建 |
| [All-In-One](https://help.aliyun.com/zh/functioncompute/all-in-one-template) | **是** | 浏览器 + 代码执行协同 | 要从官方 all-in-one 镜像构建 |
| 其他（Desktop、Claude Code、OpenClaw 等） | **是** | 桌面环境、编码 Agent | 从对应官方镜像自行构建 |

`base` 和 `code-interpreter-v1` 在账号开通云沙箱后自动就绪，直接用模板名创建沙箱即可。

### 三者的默认配置对比

这部分我建议直接抄进自己的容量规划里：

| 配置项 | `base` | `code-interpreter-v1` | `browser` | All-In-One |
| --- | --- | --- | --- | --- |
| CPU | 2 vCPU（最低要求） | 2 vCPU（最低要求） | 4 vCPU（推荐起始） | 4 vCPU（推荐规格） |
| 内存 | 2048 MB（最低要求） | 2048 MB（最低要求） | 8192 MB（推荐起始） | 8192 MB（推荐规格） |
| 磁盘 | 10240 MB | 10240 MB | 10240 MB | 10240 MB |
| 端口 | 无业务端口（只有 envd 基础服务） | 5000（沙箱服务监听） | 3000（browser 服务） | 3000（浏览器）+ 5000（代码/文件） |
| Code Interpreter | 不支持 | 支持 Python / JavaScript | 不支持 | 支持 |

`base` 的定位写得很清楚：提供最小化运行环境，内置 E2B envd 兼容基础服务，是 `code-interpreter-v1`、`browser`、All-In-One 三个模板的**共同能力基础**。它不预装数据科学库，也不预置浏览器自动化服务。

**回到坑二那句话**——通用 `e2b` SDK 不传 `template` 时默认创建的就是 `base` 沙箱。而 `base` 的 TypeScript 写法还不太一样，没有模板时 options 是第一个参数：

```typescript
const sbx = await Sandbox.create({ timeoutMs: 600_000 });
```

### Code Interpreter 的硬限制

`code-interpreter-v1` 那页除了能力介绍，还给了一组迁移时一定会用到的数字：

| 限制项 | 约束 |
| --- | --- |
| 沙箱生命周期 | 单个实例**最长 24 小时**（`timeout` 上限 **86400 秒**） |
| 空闲超时 | `sandboxIdleTimeoutSeconds`，**有效下限 60 秒**（低于 60 秒按 60 秒生效） |
| 代码执行超时 | 单次同步执行默认 **Python 300 秒 / TypeScript 60000 毫秒**，可通过 `timeout` / `timeoutMs` 调整 |
| 语言支持 | Python、JavaScript（`language` 默认 `python`） |

**24 小时这个上限值得单独记住。** 如果你的 Runtime 设计里有一个「常驻沙箱」的角色，它在这里是有天花板的。

### Code Interpreter Sandbox 的生产形态

[使用 Code Interpreter Sandbox](https://help.aliyun.com/zh/functioncompute/using-the-code-interpreter-sandbox)那页其实在讲一件更重要的方法论：**交互式 `run_code` 适合开发，固定脚本入口适合生产。**

它建议把分析任务拆成四步：

1. 写入输入数据和分析脚本。
2. 使用**固定入口**执行脚本，例如 `python3 analyze.py`。
3. 要求脚本输出 JSON 摘要，必要时生成文件产物。
4. 读取结果并销毁沙箱。

理由说得很直白：**固定脚本入口更容易做审计、超时和输出校验**，因为脚本版本、输入目录、超时时间和输出格式都更容易固化。`run_code` 更适合模型逐步生成和修正代码的交互式任务。

它还顺手给了一份上线建议，我挑几条最实用的：

- 输入文件要限制大小、类型和路径，避免一次任务占用过多内存或磁盘。
- **输出优先用 JSON 摘要**，图表、表格、报告文件写 `/tmp` 后再下载。
- 对 `stdout`、`stderr`、退出码和结果文件做**统一封装**，避免上层 Agent 直接解析非结构化日志。
- **对分析代码做版本化**——「生产系统不要只保存模型生成的自然语言解释」，这句挺重的。
- 常用依赖（pandas、openpyxl、绘图库、业务 SDK）放进模板。
- 用户可见结果和排障日志分开处理，别把完整堆栈或敏感数据直接返回。

### browser 模板：不是开通即用，CDP 之外还要过鉴权

`browser` 模板提供云原生浏览器环境，通过**标准 Chrome DevTools Protocol（CDP）over WebSocket** 远程控制，原生兼容 Puppeteer、Playwright。它内置 VNC 服务，可以实时看浏览器桌面。**但它的使用分两个阶段：先构建模板，再运行模板。**

**默认配置**：

| 配置项 | 值 |
| --- | --- |
| 容器镜像 | `fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.44` |
| 默认端口 | 3000 |
| CPU | 4 vCPU（推荐起始） |
| 内存 | 8192 MB（推荐起始） |
| 磁盘 | 10240 MB（建议 10 GB） |

**第一步：构建。** 从官方镜像固化出一个带名称的模板：

```python
from dotenv import load_dotenv
from e2b import Template, default_build_logger

load_dotenv()

FROM_IMAGE = "fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.44"

build = Template.build(
    Template().from_image(FROM_IMAGE),
    name="my-browser-template",
    cpu_count=4,
    memory_mb=8192,
    on_build_logs=default_build_logger(),
)
print(f"template_id: {build.template_id}")
```

**第二步：运行。** 创建沙箱后**先轮询 `/health` 等 browser 服务就绪**，再连 CDP：

```python
sbx = Sandbox.create(template="my-browser-template", timeout=900)
host = sbx.get_host(BROWSER_PORT)          # BROWSER_PORT = 3000
token = sbx._envd_access_token             # 公网网关要求 X-Access-Token，否则 403
headers = {"X-Access-Token": token} if token else {}

wait_until_healthy(sbx, host, token)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(f"wss://{host}/ws/automation", headers=headers)
    ...
```

三个 WebSocket 端点，**全部需要在请求头带 `X-Access-Token` 鉴权**：

| 端点 | 路径 | 用途 |
| --- | --- | --- |
| 健康检查 | `https://<sandbox-host>/health` | 判断 browser 服务是否启动完成 |
| CDP 自动化 | `wss://<sandbox-host>/ws/automation` | 浏览器自动化，兼容 Puppeteer 和 Playwright |
| VNC 实时流 | `wss://<sandbox-host>/ws/livestream` | 实时查看浏览器桌面，可用 noVNC 客户端 |

**这里的坑密度比前面几个模块高，我总结成四条：**

**① `X-Access-Token` 的取法是非公开 API。** Python 用 `sbx._envd_access_token`（下划线前缀，说明是内部属性），TypeScript 用 `sbx.envdAccessToken`。文档自己标注了「后续版本可能重命名或移除」。**这意味着这条链路在 SDK 升级时是有断裂风险的**，值得在代码里加一层封装并写测试。

**② noVNC 这种纯浏览器客户端连不上。** 原因很实在：**浏览器 WebSocket API 不支持在握手时设置自定义请求头**，所以带不了 `X-Access-Token`，直连就是 403。要看画面得换支持自定义 header 的客户端（`wscat`、Python `websockets`）。**如果只是想看结果，用 CDP 连接后 `page.screenshot()` 截图更省事**——我觉得这是官方给的最务实的一句建议。

**③ 改窗口尺寸要重新烤镜像，`envs` 不管用。** 浏览器窗口和虚拟屏幕由镜像里三个环境变量控制：

| 环境变量 | 作用 | 默认值 |
| --- | --- | --- |
| `RESOLUTION` | Xvfb 虚拟屏幕分辨率（宽x高x色深） | `1680x1050x24` |
| `BROWSER_WINDOW_SIZE` | Chrome 启动窗口大小（`--window-size`） | 取 `RESOLUTION` 的宽高 |
| `VNC_CLIP` | VNC 实时流的画面裁剪区域 | 与窗口大小一致 |

而 `Sandbox.create` 的 `envs` **只注入沙箱内的命令执行进程，不会影响浏览器栈**。所以想改尺寸，得先用 Dockerfile 把环境变量烤进自定义镜像：

```dockerfile
FROM fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.44

ENV RESOLUTION=1920x1080x24
ENV BROWSER_WINDOW_SIZE=1920x1080
ENV VNC_CLIP=1920x1080
```

推送到镜像仓库后，再用 `from_image` 构建模板。注意**窗口尺寸同时决定 VNC 实时流的画面范围**，但页面内视口仍由 Playwright / Puppeteer 通过 CDP 自己设。

**④ 探测 WebSocket 时会「假失败」。** 在沙箱内用 curl 测 CDP 握手：

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

收到 `101 Switching Protocols` 之后，服务端会继续发 WebSocket 数据帧，**curl 会一直等到 `-m 4` 超时并以退出码 28 结束**。文档专门解释了这不代表握手失败——**判断依据是响应里有没有 `101`，不是 curl 的退出码。**

### All-In-One：浏览器 + 代码执行，同一沙箱

[All-In-One](https://help.aliyun.com/zh/functioncompute/all-in-one-template) 就是在 browser 的基础上叠加 Code Interpreter 服务。差异很简洁：

| 对比项 | browser | All-In-One |
| --- | --- | --- |
| 核心定位 | 轻量浏览器自动化环境 | 浏览器自动化 + 代码执行一体化 |
| Code Interpreter | 不支持 | 支持 Python / JavaScript，含上下文保持 |
| 端口 | 3000 | 3000（浏览器）+ 5000（代码与文件） |
| 默认镜像 | `runtime/browser` | `runtime/all-in-one` |

默认镜像示例是新加坡地域：`fc-e2b-registry.ap-southeast-1.cr.aliyuncs.com/runtime/all-in-one:v0.0.44`。**注意跨地域镜像构建会失败**——镜像地址里的地域必须换成云沙箱接入地域。

浏览器部分（建沙箱、等 `/health`、CDP、截图）和 browser 模板完全一致，只是多了一段：**浏览器阶段产生的截图、HTML、下载文件，可以直接在同一沙箱里交给 Code Interpreter 处理。**

```python
# 承接 browser 流程中的同一个 sbx
execution = sbx.run_code(
    "import json\n"
    "print(json.dumps({'status': 'ok', 'source': 'all-in-one'}, ensure_ascii=False))"
)
print("".join(execution.logs.stdout))
```

用 Code Interpreter 时，SDK 要换回 `e2b_code_interpreter` / `@e2b/code-interpreter`，沙箱由你自己的 All-In-One 模板创建。

**选型标准文档给得很清楚，我直接抄**（[使用 Browser Use Sandbox](https://help.aliyun.com/zh/functioncompute/use-browser-use-sandbox) / [使用 AIO Sandbox](https://help.aliyun.com/zh/functioncompute/using-aio-sandbox)）：

| 任务形态 | 选择 |
| --- | --- |
| 只访问网页、点击、截图、下载、轻量提取 | **Browser Use Sandbox**（browser 模板） |
| 浏览器产物还要在同一会话里清洗、分析、生成报告 | **AIO Sandbox**（All-In-One 模板） |
| 只有代码执行 | **Code Interpreter Sandbox**（code-interpreter-v1） |
| 只要基础命令和文件 | **base** |

AIO 那两页的「推荐流程」都是 8 步，结构很像，我合并一下：**构建业务模板 → 建沙箱并设足够超时 → `get_host(3000)` 拿 host → 轮询 `/health` → 连 CDP 执行操作 → 产物写入沙箱文件系统 → 交给 Code Interpreter 或命令继续处理 → 下载结果、销毁沙箱**。

中间有个细节值得抄：**用固定的任务目录**，例如 `/tmp/aio-task/<task-id>`，把截图、HTML、下载文件、脚本和结果文件放同一目录。另外官方明确提了**「浏览器阶段和代码阶段分别记录输入、输出、日志和错误」**——排查时先确认是页面操作失败，还是后续脚本处理失败，否则这两种错在同一个沙箱里长得一模一样。

### BrowserUse 这类框架怎么接

这块是很多 Agent 框架落地的关键：**让 BrowserUse 连接沙箱暴露的 CDP 地址。**

```python
browser_session = BrowserSession(
    cdp_url=f"wss://{host}/ws/automation",
    browser_profile=BrowserProfile(headless=False, keep_alive=True),
    headers={"X-Access-Token": sandbox._envd_access_token},
)

agent = Agent(
    task="访问 https://example.com，提取页面标题并总结首屏正文",
    llm=ChatOpenAI(model=..., api_key=..., base_url=...),
    browser_session=browser_session,
    use_vision=True,
)
```

职责划分很清楚：**业务服务负责创建和销毁沙箱，BrowserUse 只连接这个沙箱中的浏览器会话。** 用 Puppeteer Core 也一样，`browserWSEndpoint` 填 `wss://<host>/ws/automation`，headers 带 token。

上线建议里有两条我特别认同，顺便呼应了前面沙箱选型那篇的老话题：

- **页面内容可能包含 prompt injection。不要让 Agent 未经校验地执行网页中的指令。**
- **登录态、Cookie、账号凭证和业务 Token 应按任务隔离，通过运行时注入，不写进模板。**
- 每个浏览器任务限制在明确的 URL 范围内，必要时加域名白名单；限制下载文件类型、单文件大小、总输出大小和任务生命周期。

### 自定义模板：从自己的镜像构建

内置模板满足不了时（业务依赖、系统库、运行时版本、企业标准化），才做自定义镜像模板。**生产模板还有几条纪律**（[构建和管理模板](https://help.aliyun.com/zh/functioncompute/build-a-custom-image-template)）：

- 模板名称应唯一、可读，**便于灰度和回滚**。
- 基础镜像来自云沙箱可访问的镜像仓库。
- **镜像仓库、网络配置和云沙箱要在同一地域。**
- 构建依赖不宜过大，否则可能构建超时或失败。
- **生产环境不应覆盖正在使用的模板**，建议新建模板、验证后再切换。

构建流程本身很短——定义模板、提交构建、拿 `template_id` 建沙箱（[快速开始](https://help.aliyun.com/zh/functioncompute/templates)）：

```python
build = Template.build(
    Template().from_image(os.environ["FROM_IMAGE"]),
    name=f"template-{int(time.time())}",
    cpu_count=2,
    memory_mb=2048,
    on_build_logs=default_build_logger(),
)

sandbox = Sandbox.create(template=build.template_id, timeout=900)
```

如果你要用自己的 **ACR EE** 镜像，前置条件比较硬：

- ACR EE 实例要和云沙箱在**同一 UID、同一地域**（经济版不支持）。
- ACR EE 实例要**至少绑定一个 VPC**，且该 VPC 下至少有一个 vSwitch 在函数计算支持的可用区。
- 镜像仓库、VPC、vSwitch 与云沙箱同地域，且访问控制已放通。
- 推送时用 VPC 内网地址，例如 `test-registry-vpc.cn-beijing.cr.aliyuncs.com/runtime/python:3.12-v1`。
- **不要给不同内容的镜像推同一个 tag。** 每个不同镜像都要有新且唯一的 tag（版本号、日期或 commit ID），模板引用那个具体 tag。

镜像本身也有一张要求表，违反任何一条都会让构建或运行失败：

| 级别 | 要求 | 不满足的后果 |
| --- | --- | --- |
| 必须 | 架构为 `linux/amd64`（多架构镜像的 manifest list 要包含 amd64） | 模板转换立即失败 |
| 必须 | 不要开启镜像加速 | 模板转换立即失败 |
| 必须 | `/etc/passwd`、`/etc/group` 是标准文件且可写 | gatewayd 无法初始化默认用户，容器启动失败 |
| 条件 | 固定路径 `/bin/bash` 存在（不能只是能从 PATH 解析到） | `commands.run` 和 PTY 失败 |
| 条件 | PATH 中有 `python3` 或 `python` | Python `run_code` 不可用 |
| 条件 | PATH 中有 `node` | JavaScript `run_code` 不可用 |
| 按需 | `git`、`openssh-client`、CA 证书、构建工具链 | 对应的 Git / SSH / HTTPS / 源码构建操作不可用 |
| 建议 | 系统 PATH 至少包含 `/usr/local/bin`、`/usr/bin`、`/bin` | 登录 shell 里可能缺常用命令 |

`/bin/bash` 那一条我建议特别留意：它说的是**固定路径存在**，不是 PATH 里能找到。很多精简基础镜像（busybox / distroless 派生）会把 bash 放在别处或者干脆没有。还有「不要开镜像加速」这条也挺反直觉——那是个平时看起来纯占便宜的开关。

**模板的定位也说得很清楚**：模板固化的是系统依赖、语言运行时、工具链和基础代码；**用户数据、临时文件和频繁变化的业务状态要在运行时写入**；**密钥、Token 这类敏感凭证不要写进模板，创建沙箱时用环境变量注入**。最后这句我在前面提过一次，这里再强调一遍，因为它是最容易被「顺手固化一下」的操作。

#### 一次真的跑通：从跨地域失败到新加坡模板可用

上面的要求表看起来像文档摘录，直到我真的推了一次镜像，才发现它更适合当成一条**排错顺序**。这次镜像里要固化的是 Node.js、openpyxl、pandas、NumPy 和 SciPy；最终跑通的路径不是「把 Dockerfile 写对」这么简单，而是连续解决了地域、账号、API Key、镜像 manifest 和登录 Shell 五层问题。

先给结论：**自定义模板构建至少有五个必须同时对齐的坐标：Sandbox 地域、E2B Endpoint、E2B API Key 的归属地域、镜像仓库地域、镜像仓库所属账号。** Dockerfile 只是第六个变量。

##### 第一步永远用官方镜像建立基线

不要一上来就拿私有镜像测试。先用同地域官方镜像构建模板并创建 Sandbox：

```env
E2B_API_KEY=
E2B_API_URL=https://api.<region>.e2b.fc.aliyuncs.com
E2B_DOMAIN=<region>.e2b.fc.aliyuncs.com
OFFICIAL_IMAGE=fc-e2b-registry.<region>.cr.aliyuncs.com/runtime/code-interpreter-v1:<published-tag>
```

这一步成功，才能证明 Team、API Key、Endpoint、Domain 和模板服务链路都正常。否则后面看到 `401`、模板不可见或构建失败时，很容易把凭证问题误判成镜像问题。

API Key 是地域级凭据。最安全的只读探测是查询 Sandbox 列表，而不是创建 Sandbox：

```python
import httpx

response = httpx.get(
    "https://api.ap-southeast-1.e2b.fc.aliyuncs.com/sandboxes",
    headers={"X-API-KEY": api_key},
    timeout=15,
)
print(response.status_code)
```

我们这次就碰到过一种很有迷惑性的状态：Endpoint 和 Domain 已经换成新加坡，但 Key 仍然属于北京。结果是新加坡返回 `401`，北京返回 `200`。**Endpoint 改了，不代表 Key 跟着迁移；目标地域必须重新创建 Team/API Key。**

##### 地域不一致不是“慢一点”，而是构建器根本不存在

第一次自定义镜像放在河源 ACR，Sandbox 在北京。构建请求已经被接受，但注入 envd 时失败：

```text
envd inject failed
lookup <account>.cn-heyuan.fc.aliyuncs.com: no such host
```

这不是 DNS 偶发故障。河源不是 FC 云沙箱支持地域，平台根据镜像仓库地域准备 Builder，最终指向了不存在的河源 FC 服务。后来把镜像和 Sandbox 一起迁到新加坡，这一层才消失。

所以地域检查不要只看 Endpoint。完整矩阵应该是：

| 对象 | 必须检查的值 |
| --- | --- |
| E2B API URL | `api.<region>.e2b.fc.aliyuncs.com` |
| E2B Domain | `<region>.e2b.fc.aliyuncs.com` |
| API Key | 在目标地域 Team 下创建 |
| 源镜像仓库 | 与 Sandbox 同地域 |
| Template / Sandbox | 与前三者同地域 |
| VPC / vSwitch / 安全组（ACR EE） | 与仓库和 Sandbox 同地域 |

##### “账号一致”可以从错误信息里反推

镜像迁到新加坡后，第一次仍然失败：

```text
get personal ACR authorization token
AUTHENTICATION_FAILED
user jurisdiction error
```

当时地域、镜像地址、仓库用户名密码都没错。真正的问题是 **E2B API Key 所属账号与 ACR 仓库所属账号不一致**。换成镜像仓库所在账号、同一新加坡 Team 下创建的 Key 后，构建日志依次变成：

```text
template build accepted
starting image conversion
registry resolved
builder prepared
image conversion completed
template function created
```

这条日志序列很有用：`registry resolved` 之前失败，先查仓库类型、账号归属和凭证；`builder prepared` 之前失败，先查地域和 FC Builder；镜像转换完成但 Sandbox 起不来，再查镜像内部结构与运行依赖。

官方文档把受支持的私有 ACR 主路径写成 **ACR 企业版、同 UID、同地域、绑定 VPC**。这次实测中，同账号同地域的 ACR 个人版也通过 E2B `Template.build()` 跑通了镜像转换和 Sandbox 创建，但这只能记作**当前实测行为，不应提升为生产承诺**。生产仍然应按官方支持路径使用 ACR EE；否则平台调整授权或构建策略时，没有稳定性保证。

##### 镜像要同时满足构建器和登录 Shell

最终镜像采用 Node 22 slim 作为基础，再安装 Python 3 虚拟环境和数据依赖。这样比在 Python 镜像里通过 Debian 安装 `npm` 少拉数百个系统包。核心结构如下：

```dockerfile
FROM node:22-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash ca-certificates curl git openssh-client \
        python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY requirements-image.txt /tmp/requirements-image.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements-image.txt
```

这里又踩了一个只有运行时才出现的坑：Docker 构建阶段用 `python` 导入依赖正常，但 Sandbox 的 `bash -lc` 会重置 PATH，`python3` 最后指向系统 Python，报 `ModuleNotFoundError`。

单纯把 `/usr/local/bin/python3` 软链接到虚拟环境也不够。Python 会根据启动路径判断虚拟环境，跨目录软链接可能让它重新落回系统环境。最后用一个明确的包装器解决：

```dockerfile
RUN printf '%s\n' '#!/bin/sh' 'exec /opt/venv/bin/python3 "$@"' \
        > /usr/local/bin/python3 \
    && chmod +x /usr/local/bin/python3
```

**Docker build 中能 import，不代表 Sandbox 登录 Shell 中也能 import。** 验收必须用和 Sandbox 接近的命令：

```bash
docker run --rm --platform linux/amd64 <image> bash -lc '
python3 -c "import openpyxl, pandas, numpy, scipy"
node --version
test -w /etc/passwd
test -w /etc/group
'
```

##### 推送时关闭附加 manifest

FC 模板排错文档明确建议使用单一 `linux/amd64` 并关闭 provenance / SBOM。否则 Buildx 可能同时推送一个 `unknown/unknown` 的 attestation manifest，模板构建器可能把它当成镜像平台异常。

```bash
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --sbom=false \
  --tag "<registry>/<namespace>/<image>:<unique-tag>" \
  --push \
  .
```

这里的 `<unique-tag>` 是纪律，不是装饰。不要把不同内容覆盖到已经被模板引用的 tag；使用日期、版本号或 commit ID，让镜像、模板和一次验证结果能够互相追溯。

##### 最后的验收必须发生在云端 Sandbox

本地镜像测试只证明容器能跑，不能证明 envd 注入、模板函数和 Sandbox 生命周期正常。最终验收应当创建一次临时 Sandbox，实际导入依赖，然后在 `finally` 中释放：

```python
sandbox = Sandbox.create(template=template_id, timeout=300)
try:
    result = sandbox.commands.run(
        "python3 -c \""
        "import openpyxl, pandas, numpy, scipy; "
        "print(openpyxl.__version__, pandas.__version__, "
        "numpy.__version__, scipy.__version__)\" "
        "&& node --version"
    )
    if result.exit_code != 0:
        raise RuntimeError(result.stderr)
    print(result.stdout)
finally:
    sandbox.kill()
```

这次云端最终验证通过的组合是 Python 3.11、Node.js 22、openpyxl 3.1.5、pandas 2.3.2、NumPy 2.3.3、SciPy 1.16.2。版本号不是推荐清单，只是一次可复现构建的证据；真正值得复用的是验收顺序：

1. 官方镜像验证控制链路；
2. 只读探测 API Key 地域；
3. 单平台、唯一 tag 推送自定义镜像；
4. 观察构建日志停在哪一阶段；
5. 在云端 Sandbox 里导入全部关键依赖；
6. 无论成功失败都释放临时 Sandbox。

这轮实测最后留下的判断是：**自定义模板最难排查的不是 Dockerfile，而是“地域 × 账号 × 凭据 × 仓库类型”共同决定的构建控制面。** 先把这四个坐标钉死，再谈镜像内部依赖，排错会快很多。

### 模板的版本管理：名称 + 标签

发布纪律这块，官方给的做法是**名称标识运行环境，标签标记某次构建的阶段或版本**（`prod`、`staging`、`v1`），用来做灰度和回滚（[模板名称与版本](https://help.aliyun.com/zh/functioncompute/template-name)）。

名称建议带上业务场景、语言或基础镜像、关键依赖版本和日期：

```text
agent-python313-20260704
code-review-node22-20260704
data-analysis-py313-v1
```

标签操作有三个：`assignTags` 分配、`getTags` 查询、`removeTags` 移除。有两个坑值得记：

- **不能删除 `default` 标签**（返回 400）。
- **Python 查询标签要用模板 ID**，不是模板名；TypeScript 用模板名就行。分配和移除倒是都按模板名。

```python
Template.assign_tags("agent-python313-20260704", ["staging", "v1"])
tags = Template.get_tags("<template-id>")   # 注意这里是 ID
```

分配和移除标签都是幂等的，重复分配、删不存在的标签都不会报错。`assignTags` 第一个参数用 `name:tag` 格式指定从哪个构建打标签，不带 `:tag` 时默认指向 `default` 构建。

### 沙箱内的环境变量

环境变量分两层，用途不同（[环境变量](https://help.aliyun.com/zh/functioncompute/environment-variable)）：

- **沙箱级 `envs`**：创建时传入，适合多次命令都会用到的配置。
- **命令级 `envs`**：`commands.run()` 时传入，适合单次执行参数，会覆盖沙箱级。

```python
sandbox = Sandbox.create(..., envs={"NODE_ENV": "production", "TASK_ID": "task-001"})

result = sandbox.commands.run("echo $TASK_ID", envs={"TASK_ID": "task-002"})
```

官方建议是**环境变量只放非敏感开关、任务参数和工具配置**，密钥和 Token 由业务侧控制访问范围。以及一条和 metadata 呼应的边界：**不要依赖环境变量保存业务状态**，跨沙箱的持久状态写外部存储。

## 七、FC Extensions：云沙箱不是 E2B 的镜像

如果只是纯「E2B 兼容，换个 endpoint」，那云沙箱的价值就只是「国内有个能连上的 E2B」。但它其实还多了一层 E2B 原生接口里没有的东西：**FC Extensions（云上扩展）**（[概览](https://help.aliyun.com/zh/functioncompute/fc-extensions-overview)）。

| 扩展 | 作用 |
| --- | --- |
| [VPC 网络配置](https://help.aliyun.com/zh/functioncompute/vpc-network-configuration-1) | 让 Sandbox 访问 VPC 内的数据库、内网 API、镜像仓库或其他云资源 |
| [自定义域名](https://help.aliyun.com/zh/functioncompute/custom-domain-name) | 用固定域名和自有证书访问云沙箱 API 及沙箱内服务 |
| [动态挂载 OSS](https://help.aliyun.com/zh/functioncompute/mount-oss-dynamically-1) | 通过 metadata 把 OSS 路径挂进 Sandbox，按本地路径读写对象 |
| [监控与日志](https://help.aliyun.com/zh/functioncompute/monitoring-and-logging) | 查看运行状态与资源指标，把 stdout / stderr 采集到日志服务 |
| [Team 配额管理](https://help.aliyun.com/zh/functioncompute/quota-management) | 给指定 Team 设置 CPU 和内存配额 |
| [OSS Volume](https://help.aliyun.com/zh/functioncompute/create-oss-volume) / [AgenticFS Volume](https://help.aliyun.com/zh/functioncompute/create-an-agenticfs-volume) | 保存可复用的挂载配置，创建沙箱时按名称挂载 |

它的接入方式有一个很重要的性质：**FC Extensions 不是 E2B SDK 的新方法，不需要改导入方式。** 应用侧还是照常 `Sandbox.create()`，VPC、OSS、日志、监控这些是在函数计算控制台或云沙箱控制面配好、然后生效的。

而且它的实际机制比「控制台点一下」更有意思：**VPC 和 OSS 挂载都是通过 Sandbox 的保留 metadata 字段传进去的。**

### VPC 配置：一个保留 metadata 字段

云沙箱通过 `fc.sandbox.network.vpc` 传 VPC 配置——把 `vpcId`、`securityGroupId`、`vSwitchIds` 序列化成 **JSON 字符串**：

```json
{
  "vpcId": "vpc-xxxxxxxx",
  "securityGroupId": "sg-xxxxxxxx",
  "vSwitchIds": ["vsw-xxxxxxxx"]
}
```

```python
sandbox = Sandbox.create(
    **conn_opts,
    metadata={
        "fc.sandbox.network.vpc": json.dumps(vpc_config),
    },
)
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `vpcId` | 是 | 要接入的专有网络 ID |
| `securityGroupId` | 是 | 安全组 ID，用于控制**出方向**访问范围 |
| `vSwitchIds` | 是 | vSwitch ID 列表，**建议配两个或更多**，提高可用性并降低单网段 IP 不足的风险 |

前置条件比想象中多，漏一个就是「创建成功但连不上」：

- vSwitch 要在函数计算支持的可用区（同 VPC 内不同 vSwitch 默认可私网互通）。
- 安全组要是**非云服务托管**的，且**出方向规则**允许访问目标资源的协议和端口。
- 目标资源自己有白名单的（RDS 白名单、自建服务 ACL），要把 **vSwitch 网段**加进去。

**「网络可达不等于业务鉴权通过」**——数据库账号、API Token、RAM Role 这些都还得单独配。这句话文档写得很明白，我觉得是这一节最有价值的一句。

**验证方式**也很实在，而且给了一个我觉得很聪明的判别实验：

1. 用 `socket.create_connection((host, port), timeout=5)` 在沙箱内测 TCP 连通性，可以拿去测 NAS 2049、RDS 3306、Redis 6379 或内网 HTTP 端口。
2. **先建一个不带 `fc.sandbox.network.vpc` 的 Sandbox，确认同一个内网地址不可达；再建一个带 VPC metadata 的，确认可达。** 这样才能证明是 VPC 配置生效，而不是网络本来就通。

常见问题那张表也能当排错清单用：

| 现象 | 可能原因 |
| --- | --- |
| 创建 Sandbox 失败 | 资源 ID 不存在，或与沙箱不在同一地域 / 账号 |
| 创建成功但内网地址不可达 | 安全组出方向未放行、目标资源白名单未含 vSwitch 网段、目标服务未监听 |
| 提示 vSwitch 可用区不支持 | vSwitch 不在函数计算当前地域支持的可用区内 |
| 偶发创建 / 连接失败 | vSwitch 网段可用 IP 不足，或只配了单个可用区 |
| 需要访问公网和 VPC | **只配 VPC 不代表固定公网出口**，公网能力以云沙箱和函数计算网络策略为准 |

还有个表述细节：**`fc.sandbox.network.vpc` 的值必须是 JSON 字符串，不能直接传 Python dict 或 JavaScript object。**

### OSS 挂载：两个 metadata 字段

OSS 动态挂载要传两个字段（[动态挂载 OSS](https://help.aliyun.com/zh/functioncompute/mount-oss-dynamically-1)）：

- `fc.sandbox.storage.oss`：挂载配置，JSON 字符串。
- `fc.sandbox.auth.role`：**用于访问 OSS 的 RAM Role ARN**。

```python
sandbox = Sandbox.create(
    api_key=api_key,
    timeout=300,
    **conn_opts,
    metadata={
        "fc.sandbox.storage.oss": json.dumps(oss_config),
        "fc.sandbox.auth.role": role_arn,
    },
)
```

挂载点配置：

```json
{
  "mountPoints": [
    {
      "bucketName": "example-bucket",
      "mountDir": "/mnt/oss",
      "bucketPath": "/e2b-test",
      "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
      "readOnly": false
    }
  ]
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `bucketName` | 是 | OSS Bucket 名称 |
| `mountDir` | 是 | Sandbox 内挂载目录，必须是绝对路径 |
| `endpoint` | 是 | OSS Endpoint，**应与 Bucket 所在地域匹配** |
| `bucketPath` | 否 | Bucket 内子目录，建议绝对路径；`/` 或留空表示根目录 |
| `readOnly` | 否 | `true` 时只能读挂载目录 |

几个容易踩的点：

- **挂载必须同时配 `fc.sandbox.auth.role`，否则沙箱拿不到 OSS 权限。** 两者缺一不可。
- RAM Role 要授予函数计算服务**可扮演权限**，并具备访问目标 Bucket 或子目录的 OSS 权限。
- `mountDir` 推荐 `/mnt/oss` 或 `/home/user/oss`，**避免与模板内已有系统目录冲突**。
- 跨地域 `endpoint` 会导致延迟升高或访问失败。

**权限建议是这一页最值得抄的部分**，因为它正好把之前沙箱选型那篇讲的「最小权限」落到了具体 policy 上：

- 用 `readOnly: true` 挂输入数据目录，避免任务误写或删除源数据。
- 写入结果用独立前缀，例如 `tenants/<tenant-id>/tasks/<task-id>/outputs/`。
- RAM Policy 只授权任务需要的对象前缀：只读任务给 `oss:ListObjects` + `oss:GetObject`；读写任务再按需加 `oss:PutObject`、`oss:DeleteObject`、`oss:AbortMultipartUpload`、`oss:ListParts`。
- **不要在代码、模板或 metadata 中写长期 AK/SK**，访问 OSS 走 `fc.sandbox.auth.role`。
- 临时产物配 OSS 生命周期清理规则。

### 自定义域名：证书要求比想象中严格

[自定义域名](https://help.aliyun.com/zh/functioncompute/custom-domain-name)解决的是「生产环境要固定域名 + 自有证书」。它把域名分成两条链路：

| 用途 | 示例 | 说明 |
| --- | --- | --- |
| 控制链路域名 | `api.example.com` | 创建、查询、删除云沙箱等 API 请求 |
| 数据链路域名 | `*.example.com` | 访问沙箱内指定端口的服务 |

对应到 SDK 参数就是 `apiUrl` = `https://api.example.com`、`domain` = `example.com`。之后 `sandbox.getHost(8000)` 返回的就变成 `8000-<sandbox-id>.example.com`，`https://{port}-{sandboxId}.example.com` 这种形式。

限制条件我列一下，因为这几条挺容易在配置阶段反复：

- **必须选云沙箱所在地域**，否则域名解析和证书校验可能不生效。
- **控制链路只支持 `api.` 开头的单域名**；数据链路是控制链路去掉 `api.` 前缀后的泛域名。
- **必须 HTTPS。**
- **证书必须覆盖数据链路泛域名**（例如 `*.example.com`）——只覆盖 `api.example.com` 的单域名证书**不满足要求**。
- **私钥必须是未加密的 RSA PEM 格式。** 如果你的私钥是 PKCS#8 的 `-----BEGIN PRIVATE KEY-----`，要先转换：

```bash
openssl rsa -in pkcs8.key -out pkcs1.key
```

- **不支持中文域名。**
- 同一主账号默认最多绑 **5 个**云沙箱自定义域名。
- 自定义域名需要完成备案或接入备案，以控制台校验结果为准。

配置要动两个控制台：云沙箱控制台加域名拿 CNAME，再去云解析 DNS 配解析（控制链路主机记录 `api`，数据链路主机记录 `*`）。配完用 `dig +short CNAME api.example.com` 和 `dig +short CNAME test.example.com` 验证——**第二条是专门用来验证泛域名解析的**，这个细节挺贴心。

还有一个实用提醒：**`sandbox.getHost(port)` 返回的是 host，访问时通常要自己拼 `https://`。**

### Team 配额管理：注意鉴权通道不一样

这块的[文档](https://help.aliyun.com/zh/functioncompute/quota-management)里有一条我认为最容易被忽略、也最容易配错的信息：

> Team 配额管理使用 **POP SDK 和阿里云 AK/SK，不使用云沙箱 API Key 鉴权**。

也就是说，你的系统在这里会同时持有两套凭证：沙箱的 API Key 和阿里云的 AK/SK。**这两套东西的权限模型、轮换策略、泄露影响面都不一样**，值得在密钥管理上分开对待。文档也重申了「云沙箱 API Key 仍通过函数计算控制台创建和管理」「不要把 AK/SK、API Key 写入代码仓库、镜像、模板、日志、截图、工单或前端页面」。

前置条件里有一条挺关键：**「已在阿里云控制台联系客服完成加白」**——所以 Team 配额同样是白名单能力。

配额模型很简单，以 Team ID 作为 `TagValue`，两个配额项：

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| `TagValue` | `*string` | 匹配 `[A-Za-z0-9_-]{1,64}` | 填 Team ID |
| `CpuCores` | `*int32` | ≥ 0 | CPU 核数配额 |
| `MemoryGB` | `*int32` | ≥ 0 | 内存 GB 配额 |

**设为 `0` 表示禁止该 Team 使用对应资源**（不是「无限制」，别理解反）。`UpdateQuota` 是**覆盖式更新**，同一 `TagValue` 多次调用后一次覆盖前一次。

四个接口和对应的 RAM Action：

| 操作 | Go 方法 | RAM Action |
| --- | --- | --- |
| 创建或更新配额 | `UpdateQuota` | `fcsandbox:UpdateQuota` |
| 查询配额 | `DescribeQuota` | `fcsandbox:DescribeQuota` |
| 列出配额 | `ListQuota` | `fcsandbox:ListQuota` |
| 删除配额 | `DeleteQuota` | `fcsandbox:DeleteQuota` |

服务的 RAM 授权码是 `fcsandbox`。如果要按地域和账号收敛范围，把 `Resource` 从 `*` 改成 `acs:fcsandbox:<region>:<account-id>:*`。

这也是我和第一节那段绕了一圈的地方：**配额走的是 RAM 这条路，不是 API Key。** 第一节里说过 `fcsandbox` 不在可视化编辑器里、要用脚本编辑手写——所以真正的现象往往是「沙箱跑得好好的，一到配额接口就 401」，因为两条链路上的凭证压根不是同一套。

用阿里云 POP Go SDK 的骨架：

```go
config := &openapiutil.Config{
    AccessKeyId:     tea.String(os.Getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")),
    AccessKeySecret: tea.String(os.Getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")),
    SecurityToken:   tea.String(os.Getenv("ALIBABA_CLOUD_SECURITY_TOKEN")),
    Endpoint:        tea.String("fcsandbox.cn-beijing.aliyuncs.com"),
}

client, err := fcsandbox.NewClient(config)

resp, err := client.UpdateQuota(&fcsandbox.UpdateQuotaRequest{
    Body: &fcsandbox.Quota{
        TagValue: tea.String(teamID),
        CpuCores: tea.Int32(32),
        MemoryGB: tea.Int32(32),
    },
})
```

错误码表（也可以当排错用）：

| HTTP | Code | 说明 |
| --- | --- | --- |
| 400 | `InvalidParameter` | 参数校验失败，缺少必填字段或格式不合法 |
| 401 | `Unauthorized` | 凭证无效或未提供 |
| 403 | `Forbidden` | 无权操作 |
| 404 | `ResourceQuotaNotFound` | 查询的配额不存在 |
| 429 | `LimitExceeded` | 超出配额限制 |
| 500 | `InternalError` | 服务内部错误 |

删除配额后再查会返回 404，**但可能有短暂的最终一致性延迟**，文档建议用有上限的轮询确认——「有上限」三个字是重点。

使用建议里我最认同两条：**「不要让测试任务和生产任务共用同一个高配额 Team」**，以及 **「配额只解决资源上限问题，不能替代业务侧限流、任务队列、超时控制和资源释放」**。后者是在提醒你：配额是天花板，不是限流器；撞到天花板的失败模式和排队等待完全不一样。

### 日志采集要确认的三件事

前面坑四里说过，E2B 的 Logs 接口返回空数组是已知行为。正路是走[监控与日志](https://help.aliyun.com/zh/functioncompute/monitoring-and-logging)。那一页有一句我觉得该抄进设计文档的话：

> 应用侧可以记录 sandboxId、任务 ID 和命令结果，便于在云上监控或日志页面中定位问题。

它还把常见观测对象列成了清单，可以直接当埋点需求单用：

- **Sandbox 生命周期**：创建、连接、暂停、恢复、终止。
- **命令执行结果**：退出码、stdout、stderr、耗时。
- **资源使用**：CPU、内存、磁盘和网络。
- **关联字段**：`sandboxId`、任务 ID、用户或租户标识、模板名称。
- **结构化日志**：`event`、`taskId`、`sandboxId`、`exitCode`、stdout / stderr 摘要。

注意这里列了「资源使用：CPU、内存、磁盘和网络」——**但指标接口的磁盘字段是占位值**，所以真实数据得从控制台或云监控拿。这两处放在一起看，能看出「观测对象」和「可获取的数据源」是两件事。

## 八、迁不动的那部分怎么办

几个决策，我按「原来怎么做 → 现在怎么做」列一下（[E2B 兼容与迁移](https://help.aliyun.com/zh/functioncompute/e2b-compatibility-and-migration)）：

| 原来（E2B 原生） | 现在（云沙箱） |
| --- | --- |
| Volume 做持久化 | 换 NAS / OSS；跨 Sandbox 的数据本来就不该放本地文件系统 |
| SDK 管理 API Key | 函数计算控制台创建、查看、编辑、重置、禁用、删除 |
| Team 管理 | 函数计算控制台（创建 Team 见[创建 Team](https://help.aliyun.com/zh/functioncompute/create-team)，订阅计划见 [Team 与订阅计划](https://help.aliyun.com/zh/functioncompute/team-and-subscription-plans)） |
| Snapshot 做状态分叉 | 可以，但要白名单 + 第二代运行时，且注意命名与超时规则与官方不同 |
| 文件自定义元数据 | 不支持；改用控制面 `metadata`，或把标签写进业务库 / JSON 清单 |
| 依赖 E2B 的 Logs 接口 | 换成函数计算日志采集 + 业务侧结构化日志 |
| 依赖 E2B 的网络配置更新接口 | 换到云沙箱控制面 |
| 想要固定域名和自有证书 | 用 FC Extensions 的[自定义域名](https://help.aliyun.com/zh/functioncompute/custom-domain-name) |
| 沙箱要访问内网 RDS / Redis / NAS | 用 FC Extensions 的 [VPC 网络配置](https://help.aliyun.com/zh/functioncompute/vpc-network-configuration-1) |
| E2B 托管 MCP Gateway / BYOC | 不在兼容路径里，需要单独设计 |

**API Key 的隔离策略**值得单独说一句：按应用、环境、团队或租户拆分 Key，不要多人多系统共用一个长期 Key；生产用自定义过期时间并定期轮换；**重置或删除前先确认业务侧已经切到新 Key**——这条写在文档里，但我猜真出事的时候是「先重置，再发现有三个服务挂了」。

还有一条和 E2B 一样的老常识，仍然要重复一遍：**Sandbox 的本地文件系统只适合当前任务内的临时文件。** Sandbox 终止之后，这些文件不应该被当成持久数据依赖。临时输入、生成代码和中间结果建议写 `/tmp` 或业务自定义工作目录。

以及从沙箱选型那篇就一直在强调的点：处理用户上传路径时，要限制文件大小、文件类型和可写路径，别把未校验的路径直接传给 Filesystem API 或命令行。**这一点和用哪家沙箱无关**——沙箱防的是代码逃逸，不防你的业务逻辑被 prompt injection 牵着走。浏览器模板那一页把这条说得更直接：**网页内容和下载文件都可能携带 prompt injection。**

## 九、上生产前必须确认的边界

这一节是[使用约束](https://help.aliyun.com/zh/functioncompute/usage-constraints-of-fc-agent-sandbox)的整理。官方把话说得很直接：**快速入门只演示最小接入路径，实际业务接入前应先确认本文约束。**

### 配额：六类不能假设无限

- 单账号或单地域**并发 Sandbox 数**
- 单个 Sandbox 可用的 **CPU、内存和本地磁盘空间**
- 单个 Sandbox 可打开的**进程数、端口数、文件数**
- 单次任务的**输入、输出文件大小**
- **模板构建**的并发数、构建资源和构建时长
- **端口访问**

超出默认配额时，Sandbox 创建、模板构建或任务执行都可能失败。需要更高配额要走控制台或阿里云支持渠道申请。**这条对做 To C 产品的人尤其重要**——你的并发上限不是你代码写的并发数，是账号配额。

### 生命周期

Sandbox 创建后会持续占用资源，直到被主动终止、超时回收，或进入支持的暂停状态。任务完成后 `kill()`。

三个和生命周期相关的数字放在一起记：**上限 24 小时（86400 秒）、空闲超时下限 60 秒、命令超时默认 60 秒。** 超时参数单位差异再说一遍：**Python 通常用秒，TypeScript 用毫秒。**

### 文件与存储

- 本地文件系统只服务当前 Sandbox 生命周期。
- 跨 Sandbox 保留、共享或长期保存的数据写 NAS / OSS。
- 处理用户上传时限制文件大小、类型和可写路径。

## 十、一份可执行的迁移顺序

如果你手上有现成的 E2B 应用，我会建议按这个顺序推，每一步都有明确的验收点：

1. **开通、建 Team、建 Key。** 确认目标地域支持云沙箱、账号已开通云沙箱功能，按「项目 × 环境」建 Team，再在 Team 下创建 API Key，描述写清楚用途。**这一步会同时决定你要不要那段 `fcsandbox` 策略**——只用 SDK 就不需要，要在 OpenAPI 侧管资源才要。
2. **定地域、配环境变量、钉版本。** 选出地域，配好三个环境变量，把 SDK 版本写进 requirements / package.json，别用 `latest`。
3. **跑最小验证，只验证四件事**：创建 Sandbox、执行命令、读写文件、释放资源。文档原话是「不要一开始就迁移复杂模板、网络和存储逻辑」——这个顺序是对的，因为它把变量控制在最少。
4. **想清楚用哪个模板，别让默认值替你做决定。** 要 `run_code` 就必须装 `e2b-code-interpreter` / `@e2b/code-interpreter`；用通用 `e2b` SDK 时**必须显式传 `template`**，不传会落到 `base`。
5. **再迁自定义模板。** 用官方镜像先跑通构建流程，再换自己的 ACR EE 镜像；构建前对着镜像要求表逐条核一遍，并确认镜像仓库、VPC 和沙箱同地域。
6. **需要浏览器能力的话，这里才开始**。browser / All-In-One 都要先构建模板，再注意 `/health` 轮询、`X-Access-Token`、窗口尺寸烤镜像这几件事。
7. **迁移时同步做「能力减法」**：把 Volume、Access Token、Team 管理、文件自定义元数据、E2B Logs 接口这些从代码里挑出来，换成 NAS / OSS、控制台、控制面 `metadata` 和日志采集。
8. **最后才是网络和可观测。** VPC、OSS 挂载、自定义域名、日志采集、Team 配额，都属于 FC Extensions，走 metadata 或控制面配置，不占用迁移改造的窗口。
9. **上线前补三样东西**：显式的 `kill()` 释放路径（`try/finally`、`defer` 或 `AutoCloseable` 都行）、业务侧的 `taskId ↔ sandboxId` 映射、以及结构化日志。

## 十一、排错对照表

踩过一轮之后，我把「现象 → 先查什么」整理成了一张表，比按文档目录翻快：

| 现象 | 优先排查 |
| --- | --- |
| 认证失败 / 模板不可见 | 三个环境变量是否配全、Key 是否被禁用或重置、账号与地域是否一致 |
| 创建失败、连接失败、模板找不到 | API URL、域名、模板、Sandbox **是否同地域** |
| 连接失败 | 目标 Sandbox 是否已终止、超时回收，或不属于当前账号 / 地域 |
| Sandbox 创建成功但 `run_code` 失败 | **SDK 是否装错**；通用 `e2b` SDK 不传模板会落到 `base` |
| 内置模板正常、自定义模板 `run_code` 失败 | 自定义模板的 Code Interpreter 依赖、启动命令、监听端口、就绪条件 |
| TypeScript 里上下文管理方法不可用 | 该能力当前**仅 Python SDK** 提供 |
| 写入报 `File metadata requires envd 0.6.2 or later` | 用了文件自定义元数据，当前不支持；改用控制面 `metadata` |
| 上传 / 下载 URL 403 | 创建 Sandbox 时是否显式设了 `secure=false` |
| 服务起来 60 秒后被杀 | 命令超时默认 60 秒，后台进程要显式设 `timeout` / `timeoutMs` |
| PTY 输出解析不了 | PTY 会改变输出格式；批处理应该用 `commands.run()` |
| 浏览器端点 403 | 请求头缺 `X-Access-Token`（`sbx._envd_access_token` / `sbx.envdAccessToken`） |
| noVNC 连不上 | 浏览器 WebSocket API 不能带自定义 header；改用支持 header 的客户端，或直接截图 |
| CDP 探测返回退出码 28 | 正常现象，看响应里有没有 `101 Switching Protocols` |
| 改了浏览器窗口尺寸没生效 | `envs` 不影响浏览器栈，要烤进镜像（`RESOLUTION` 等） |
| browser / All-In-One 创建模板失败 | 跨地域镜像构建会失败，镜像地址里的地域要换成沙箱地域 |
| 建了带 VPC 的沙箱但内网连不通 | 安全组出方向、目标资源白名单里的 **vSwitch 网段**、服务监听状态 |
| 挂载 OSS 后没有权限 | 是否同时配了 `fc.sandbox.auth.role`（RAM Role ARN） |
| 自定义域名证书校验失败 | 证书要覆盖**数据链路泛域名**（`*.example.com`），且私钥是未加密 RSA PEM |
| 改了网络策略没生效 | Network Config Update 是受限能力，要去控制面改 |
| 抓不到沙箱日志 | E2B Logs 接口返回空数组是已知行为，走函数计算日志采集 |
| 容量 / 费用看着不对 | 别用 Metrics 的磁盘字段（占位值），以控制台 / 云监控 / 日志服务为准 |
| 创建 Snapshot 超时 | `request_timeout` 是否 ≥ 300；**先查是否已建成，不要无条件重试** |
| 沙箱列表里找不到失败的快照 | `snapshot_failed` 状态默认不显示，要按状态过滤 |
| 刚建的 Snapshot 列表里看不到 | 索引延迟；直接用创建返回的 `snapshotId` |
| Team 配额调用报 401 / 403 | 配额用 **AK/SK + `fcsandbox` RAM 授权**，不用沙箱 API Key |
| RAM 控制台搜不到 `fcsandbox` | 该服务不在可视化编辑器的服务列表里，改用**脚本编辑**手写 action |
| 建策略后仍建不了模板 / API Key | Team 级策略要同时给 `teams/<id>` 和 `teams/<id>/*`，只给前者会「看得见动不了」 |
| 沙箱能跑，但 OpenAPI 管不了 Team / API Key | 两套鉴权别混：SDK / CLI 用 API Key，控制台 / OpenAPI 用 RAM 策略 + AK/SK |
| 模板构建失败 | 先查镜像仓库、网络、账号权限，再查 SDK 参数 |
| SDK 可用但 CLI 不可用 | CLI 版本、`E2B_API_KEY`、`E2B_API_URL`、`E2B_DOMAIN` |
| CLI 行为与文档不一致 | 先 `e2b --version` 和 `<cmd> --help` |

## 十二、文档地图

上面所有结论都来自官方文档。我把 38 页按分组列在这里，并标了每页在本文的对应位置——**标「—」的是我提了一句但没展开的，需要细节请直接点链接。**

**入门与接入**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [产品简介](https://help.aliyun.com/zh/functioncompute/product-overview-of-fc-agent-sandbox) | 定位、五类场景、八个核心对象、基本使用路径 | 第一节 |
| [创建 API Key](https://help.aliyun.com/zh/functioncompute/create-api-key) | 控制台创建步骤、过期时间、编辑/重置/删除、安全建议 | 第一节 |
| [通过 SDK 使用云沙箱](https://help.aliyun.com/zh/functioncompute/using-the-cloud-sandbox-via-the-sdk) | Python / TypeScript 快速入门、版本要求 | 第一节 |
| [通过 CLI 使用云沙箱](https://help.aliyun.com/zh/functioncompute/using-the-cloud-sandbox-via-the-cli) | CLI 安装、八步操作流程、各命令示例 | 第三节 |
| [E2B SDK 接入参数说明](https://help.aliyun.com/zh/functioncompute/e2b-sdk-integration-parameter-description) | 三个环境变量与 SDK 参数逐个对应、snake/camel 差异、不作为接入参数的能力 | 第一、二节 |

**兼容与迁移**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [E2B 兼容说明](https://help.aliyun.com/zh/functioncompute/e2b-compatibility-explanation) | 四档兼容状态、各模块完整方法清单、受限与暂不兼容能力 | 第三节 |
| [E2B SDK 兼容 API 清单](https://help.aliyun.com/zh/functioncompute/e2b-sdk-compatible-api-list) | 按对象罗列的兼容方法、使用建议 | 第三节 |
| [E2B 兼容与迁移](https://help.aliyun.com/zh/functioncompute/e2b-compatibility-and-migration) | 迁移四件事、地域一致性、常见问题 | 第一、八节 |
| [E2B SDK（Java 与 Go）](https://help.aliyun.com/zh/functioncompute/e2b-sdk-java-and-go) | 两个 SDK 的安装与快速入门、Maven / replace 注意事项 | 第二节 |
| [使用约束](https://help.aliyun.com/zh/functioncompute/usage-constraints-of-fc-agent-sandbox) | 地域、版本、鉴权、六类配额、生命周期、模板构建、文件存储 | 第九节 |

**Sandbox 功能**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [创建沙箱](https://help.aliyun.com/zh/functioncompute/create-a-sandbox) | `Sandbox.create` 参数（`timeoutMs` / `envs` / `metadata`）、Python 与 TS 传参差异 | 第三节 |
| [生命周期](https://help.aliyun.com/zh/functioncompute/lifecycle) | 创建、连接、查询、终止、设置超时 | 第三节 |
| [超时](https://help.aliyun.com/zh/functioncompute/timeout) | 创建时配置、创建后调整、单位差异 | 第三节 |
| [暂停与恢复](https://help.aliyun.com/zh/functioncompute/pause-and-resume) | 白名单、`pause()`、连接时自动恢复、使用建议 | 第五节 |
| [环境变量](https://help.aliyun.com/zh/functioncompute/environment-variable) | 沙箱级与命令级 `envs`、覆盖规则 | 第六节 |
| [元数据](https://help.aliyun.com/zh/functioncompute/metadata) | 控制面 `metadata` 写法、与环境变量的区别 | 第四节 |
| [快照（邀测）](https://help.aliyun.com/zh/functioncompute/snapshots) | API 表、名称规则、保留 7 天、请求超时 300 秒、十种失败条件、参数覆盖清单 | 第五节 |

**Commands 与 Filesystem**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [运行命令](https://help.aliyun.com/zh/functioncompute/run-the-command) | `commands.*` 方法清单、与 PTY 的分工 | 第三节 |
| [后台命令](https://help.aliyun.com/zh/functioncompute/backend-command) | `background=True`、`getHost`、进程连接与终止、命令超时默认 60 秒 | 第三节 |
| [PTY](https://help.aliyun.com/zh/functioncompute/pty) | `pty.create` / `send_stdin` / `wait` / `resize` / `connect`、何时该用 PTY | 第三节 |
| [读写文件](https://help.aliyun.com/zh/functioncompute/read-and-write-files) | 方法清单、批量写入、二进制与流、目录监听 | 第三节 |
| [上传和下载文件](https://help.aliyun.com/zh/functioncompute/upload-and-download-files) | `uploadUrl` / `downloadUrl`、**`secure=false` 要求**、选型建议 | 第四节 |
| [自定义元数据](https://help.aliyun.com/zh/functioncompute/custom-metadata) | 不支持文件自定义元数据、失败行为、三条替代方案 | 第四节 |

**Code Interpreter**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [Code Interpreter 概览](https://help.aliyun.com/zh/functioncompute/overview-1) | Code Interpreter 能力总览 | 第三节 |
| [使用 Code Interpreter Sandbox](https://help.aliyun.com/zh/functioncompute/using-the-code-interpreter-sandbox) | 四步推荐流程、固定脚本入口优于 `run_code`、六条上线建议 | 第六节 |

**模板**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [内置模板](https://help.aliyun.com/zh/functioncompute/built-in-templates) | 三个内置模板清单、哪些需要自行构建、如何查看 | 第六节 |
| [base 模板](https://help.aliyun.com/zh/functioncompute/base-template) | 功能特性、默认配置（2 vCPU / 2048 MB）、**不传 template 时的默认值** | 第六节 |
| [code-interpreter-v1 模板](https://help.aliyun.com/zh/functioncompute/code-interpreter-v1-template) | 默认端口 5000、24 小时上限、空闲超时下限、`run_code` 参数与默认超时、上下文管理仅 Python | 第三、六节 |
| [browser 模板](https://help.aliyun.com/zh/functioncompute/browser-template) | 镜像与规格、CDP / VNC 端点、`X-Access-Token`、窗口尺寸烤镜像、构建与验证 | 第六节 |
| [All-In-One 模板](https://help.aliyun.com/zh/functioncompute/all-in-one-template) | 与 browser 的差异、3000 + 5000 双端口、跨地域构建会失败 | 第六节 |
| [使用 Browser Use Sandbox](https://help.aliyun.com/zh/functioncompute/use-browser-use-sandbox) | 八步推荐流程、Puppeteer 示例、BrowserUse 接入、六条上线建议 | 第六节 |
| [使用 AIO Sandbox](https://help.aliyun.com/zh/functioncompute/using-aio-sandbox) | 浏览器 + 代码执行协同流程、固定任务目录、接入建议 | 第六节 |
| [快速开始（模板）](https://help.aliyun.com/zh/functioncompute/templates) | `Template.build` 用法、从模板创建沙箱 | 第六节 |
| [模板名称与版本](https://help.aliyun.com/zh/functioncompute/template-name) | 命名建议、标签 `assignTags` / `getTags` / `removeTags`、`default` 不可删 | 第六节 |
| [构建自定义镜像模板](https://help.aliyun.com/zh/functioncompute/build-a-custom-image-template) | ACR EE 前置条件、镜像要求表、官方镜像地址、构建脚本 | 第六节 |
| 其他模板（Desktop / Claude Code / OpenClaw 等） | 需从对应官方镜像自行构建 | 第六节（未展开） |

**FC Extensions**

| 页面 | 内容 | 本文位置 |
| --- | --- | --- |
| [FC Extensions 概览](https://help.aliyun.com/zh/functioncompute/fc-extensions-overview) | 七项扩展、五步使用方式、注意事项 | 第七节 |
| [VPC 网络配置](https://help.aliyun.com/zh/functioncompute/vpc-network-configuration-1) | `fc.sandbox.network.vpc` metadata 格式、前置条件、连通性验证、常见问题 | 第七节 |
| [动态挂载 OSS](https://help.aliyun.com/zh/functioncompute/mount-oss-dynamically-1) | `fc.sandbox.storage.oss` + `fc.sandbox.auth.role`、挂载字段、RAM Policy 建议 | 第七节 |
| [自定义域名](https://help.aliyun.com/zh/functioncompute/custom-domain-name) | 控制链路 / 数据链路域名、证书与私钥要求、DNS 配置、五步验证 | 第七节 |
| [监控与日志](https://help.aliyun.com/zh/functioncompute/monitoring-and-logging) | 配置入口与生效范围、结构化日志、常见观测对象 | 第四、七节 |
| [Team 配额管理](https://help.aliyun.com/zh/functioncompute/quota-management) | POP SDK + AK/SK 鉴权、配额模型、四个接口、RAM 授权、错误码 | 第七节 |
| [配置 RAM 用户权限](https://help.aliyun.com/zh/agent-sandbox/getting-started/configure-ram-user-permissions) | 两套鉴权方式的边界、`fcsandbox` action 与 ARN 格式、三种授权粒度、常见误区 | 第一节 |
| [创建 Team](https://help.aliyun.com/zh/agent-sandbox/getting-started/create-team) | 创建 Team、获取 Team ID、资源组与订阅计划 | 第一节 |
| [Team 与订阅计划](https://help.aliyun.com/zh/functioncompute/team-and-subscription-plans) | Team 与订阅计划的关系 | — |
| [创建 OSS Volume](https://help.aliyun.com/zh/functioncompute/create-oss-volume) | 为 OSS Bucket 或子目录创建可复用挂载配置 | — |
| [创建 AgenticFS Volume](https://help.aliyun.com/zh/functioncompute/create-an-agenticfs-volume) | 为 AgenticFS Access Point 创建可复用挂载配置 | — |

## 总结

几点收获：

**1. 「协议兼容」比「接口兼容」值钱得多。** 三个环境变量就能跑通，是因为它兼容的是数据面协议，而不是照着表抄了一遍方法名——这也是 Java / Go SDK 能被第三方写出来的前提。代价是你得把 SDK 版本钉住，因为协议对齐是跟着版本走的，而且 Python 与 TypeScript 的参数名和单位还不一样。

**2. 兼容清单要当成契约读，重点看「受限」和「暂不兼容」那两档。** 「能调用」不等于「有效果」。Logs 返回空数组、Network Config Update 返回成功但不生效，这两个如果只看方法名不看文档，最后会以「线上偶发空白」和「改了没反应」的形式还给你。

**3. 默认值是这个系统里最需要审计的东西。** 通用 SDK 不传模板落到 `base`（没有 Code Interpreter）、命令超时默认 60 秒、Snapshot 请求超时默认 60 秒但它要跑好几分钟、Snapshot 默认保留 7 天、`secure` 默认要求带 token——**这五个默认值凑在一起，就是一个「Demo 能跑、生产出事」的配置集合。** 文档里专门写了「不要无条件重试」，这种提醒通常意味着它真的发生过。

**4. 静默失败比报错更贵。** 这次真正花时间的坑，基本都不抛异常。`metadata` 那个算厚道的——至少在发请求前把你拦下来了；`secure` 和 Network Config Update 连拦都不拦。判断一个兼容层成熟不成熟，可以看它有多少能力是「返回成功但什么都没做」。

**5. 跨语言抄示例是新的高频错误源。** `timeout` 秒 vs `timeoutMs` 毫秒、`api_key` vs `apiKey`、`make_dir` vs `makeDir`、`get_tags` 要传模板 ID 而 TS 传模板名、TS 里模板是第一个位置参数**但没模板时 options 又跑到第一位**——同一个功能两套写法，而 SDK 不会因为你传错字段名报错，只会用默认值继续跑。**这类错误的共同特征是不报错，所以只能靠纪律防。**

**6. 「兼容」两个字的颗粒度，比你想的细。** 同一个 Code Interpreter，`run_code` 在两种语言里都通，但上下文管理只有 Python 有；同一个 Snapshot，创建和恢复能用，命名和删除路径又和官方不同。**迁移检查表要按「方法 × 语言 × 平台」三维核对，不能按模块粗过。**

**7. 白名单能力不要写进架构。** pause、Snapshot、Team 配额都要加白。能开不代表一直在，当成设计前提就是把可用性挂在别人的后台配置上。

**8. 云沙箱的差异化在 E2B SDK 之外。** 真正的增量是 FC Extensions——VPC、OSS、自定义域名、日志、配额。如果你的场景需要这些，那这套东西的价值远不止「国内能连上的 E2B」；如果不需要，它就成了架构里一块只属于这朵云的代码。

**9. 同一朵云里并存两套鉴权，是新的认知负担。** API Key 管数据面，RAM 权限策略管控制台和 OpenAPI，管配额还要再叠一层 AK/SK。它们报的错长得几乎一样（401 / 403），但该修的地方完全不同。**排查任何「没权限」之前，先确认自己走的是哪条链路**——我这次的弯路，就是从「以为只有一套凭证」开始的。还有一个附带结论：`fcsandbox` 这种新服务不在 RAM 可视化编辑器里，是正常现象，不是你的账号有问题。

**10. 顺手再提醒一次地域。** `E2B_API_URL`、`E2B_DOMAIN`、模板、Sandbox 必须同地域；镜像仓库、VPC、自定义域名也都要同地域。这条排在最前面，也最容易在第一次接入时踩到，因为它和「Key 填错了」的现象几乎一样——都是认证或创建失败，而人的第一反应通常是去查 Key。
