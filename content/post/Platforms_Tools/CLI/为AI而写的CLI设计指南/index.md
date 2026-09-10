---
title: 为 AI 而写的 CLI 设计指南：原则、避坑与难点
description: "给 AI Agent 调用的命令行工具，和给人用的 CLI 是两种东西。本文以 FreshAI CLI（设备码登录 + 博客草稿/发布）的真实实现为骨架，讲清非交互、stdout/stderr 分工、结构化输出、语义化退出码、幂等与「结果未知」这些设计要点，并给出避坑清单和交付自检表。"
date: 2026-09-10T15:30:00+08:00
slug: agent-friendly-cli
image: images/index/index.svg
categories:
    - Platforms_Tools
tags:
    - CLI
    - Agent 工程实战
    - 教程
toc: true
draft: false
---

最近在给 FreshAI 写一个供 AI 操作外部能力的命令行工具，落地之后回头总结，发现它和「给人用的 CLI」几乎是两套设计哲学。传统 CLI 是给一个坐在 tty 前、能看进度、会按 `y/n` 的人设计的；而 Agent 看不到屏幕，它只能拿到两样东西：**stdout 的字节流**和**进程退出码**。一旦这两样东西被污染或语义不清，Agent 就会「飞盲」——重试已经成功的操作、放弃其实失败了的操作，或者把一段散文当数据去解析。

这篇文章把我踩过的坑整理成一套可复用的设计准则，骨架来自 FreshAI CLI（`packages/fresh-cli`，唯一依赖 `httpx` 的独立 Python 包），并对照 [Agent CLI Guidelines](https://aclig.dev/)、[12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)、[clig.dev](https://clig.dev/) 这些公开规范。核心心法只有一句：

> **把 CLI 当成一个「传输层是 argv / stdout / 退出码」的 RPC 接口，人只是其中一个调用方。**

---

## 一、为什么 Agent 时代 CLI 又重要了

- **Agent 天生会用 CLI。** LLM 的训练语料里有大量 shell 命令，它对 `git submodule add`、`pip install` 这类「动词-名词」结构有很强的先验。相比之下，让 Agent 现学一个私有 SDK 的调用姿势，要额外喂文档、额外占上下文。
- **CLI 是最省 token、最可组合的能力接口。** 不需要常驻进程、不需要握手协议，一个 `exec` 就能调用；输出可以裁剪到 Agent 真正需要的字段。
- **但传统 CLI 的三条默认行为，恰好都是 Agent 的天敌：** ①默认交互、②进度和结果混在一起打印、③错误只给人看。

所以「为 AI 写 CLI」不是发明一套新东西，而是把 CLI 里那些**给机器看的契约**显式化、稳定化。

---

## 二、设计原则：到底该怎么写

### 2.1 默认非交互（non-interactive by default）

Agent 没有 tty，任何 `input()` / `confirm()` / 分页器都会把它卡死直到超时。FreshAI CLI 的做法是：

- **只有显式命令进入交互流程。** 全部命令里，只有 `fresh login` 会打开浏览器，其余命令一律非交互。
- **危险操作不靠「逐次确认」保护，而靠「独立命令 + 最小权限」。** 「直接公开发布」不是给草稿命令加一个 `--yes`，而是一条独立命令 `fresh blog publish`，并且在登录授权时就必须单独拿到 `blogs:publish` scope。这样 Agent 的「公开」意图是可审计、可拒绝的，而不是被一个交互弹窗挡住的。

这是 [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46) 第 7 条（stdin 不是 tty 时也必须能跑完）在 Agent 场景下的强化版：**交互是例外，不是默认。**

### 2.2 stdout 只放结果，stderr 只放诊断

这条老规矩在 Agent 场景里是生死线。Agent 往往直接 `json.loads(stdout)`，你混进一行「正在上传…」，解析立刻崩。

FreshAI CLI 的分工：

| 通道 | 内容 |
|---|---|
| stdout | 最终结果：`--json` 时是唯一的 envelope；文本模式是正文或结果行 |
| stderr | 进度、提示、诊断、`request-id`、健康检查详情、中断消息 |

实现上就两个函数，所有输出都必须走它们，不允许 `print()` 裸奔：

```python
def _emit_progress(message: str) -> None:
    """输出脱敏进度信息到 stderr。"""
    print(message, file=sys.stderr)

def print_json_envelope(payload: dict) -> None:
    """把 envelope 以 UTF-8 JSON 写到 stdout（单行结束，无多余日志）。"""
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    sys.stdout.flush()
```

注意 `flush()`：Agent 常常边读边解析，缓冲没冲出去就是「命令卡住」的经典假象。

### 2.3 结构化输出 + 版本化 schema

成功的输出和失败的输出必须是**同一个形状**，这样 Agent 只需要一个解析器：

```json
{
  "schema_version": 1,
  "ok": true,
  "result": { },
  "error": null,
  "request_id": "…"
}
```

失败时 `ok=false, result=null`，把细节放进 `error`：

```json
{
  "schema_version": 1,
  "ok": false,
  "result": null,
  "error": {
    "code": "scope_denied",
    "message": "当前凭证缺少 blogs:publish 授权",
    "http_status": 403,
    "execution_status": "not_started"
  },
  "request_id": null
}
```

三个细节值得强调：

1. **`schema_version` 是给未来留的活路。** 字段只增不改不删（append-only contract），Agent 脚本就不会因为一次升级集体失灵。
2. **`error.code` 是 string，不是 HTTP 状态码的复读。** `invalid_input / login_required / authorization_expired / scope_denied / not_found / request_conflict / resource_state_changed / network_error / protocol_error` 这些码才是 Agent 分支判断的依据。
3. **Token-bounded。** 列表命令默认分页（`--limit 1-100`、`--offset`），不要把几千行喷进 Agent 的上下文窗口——上下文是它最贵的资源。

### 2.4 语义化退出码，并写进文档

Agent 可以**只读退出码**就决定下一步，不必解析正文。FreshAI CLI 的约定：

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 2 | 本地输入 / 配置错误（未联网） |
| 3 | 登录 / 授权错误 |
| 4 | 资源 / 冲突 / 其他 HTTP 错误 |
| 5 | 网络 / 超时 |
| 6 | 协议或凭证落盘错误 |
| 130 | 用户中断（128 + SIGINT） |

两个坑：

- **argparse 出错时默认就 exit 2**，正好可以复用来表达「本地输入错误」，但你要**知道**它是 2，别让它和你自定义的码打架。
- **130 是 128+SIGINT 的惯例**，`Ctrl+C` 中断应显式返回 130，而不是 1，否则脚本无法区分「被打断」和「执行失败」。

### 2.5 错误要「可迁移、可恢复」，并且脱敏

好的错误信息同时服务两种读者：

- **给人看：** `message` 说清楚发生了什么；
- **给程序看：** `code` + `http_status` + `execution_status` 让 Agent 能自动纠错。

同时，**错误输出是泄密高发区**。服务端可能返回一整页 HTML、异常堆栈里可能带 token、正文可能出现在报错里。这类内容一律不能回显：

```python
def _extract_error_message(response: httpx.Response) -> str:
    """从错误响应中提取脱敏说明；不回显服务端 HTML 或原始异常。"""
    try:
        payload = response.json()
    except ValueError:
        body_text = (response.text or "").strip()
        if body_text.startswith("<"):
            return f"HTTP {response.status_code}：服务端返回了非 JSON 响应"
        ...
```

跨层映射也要固定下来，Agent 才能预测：`401→登录类`、`403→scope/授权类`、`404→not_found`、`409→冲突类`、`5xx/429→网络类`。

### 2.6 幂等：所有写操作的第一公民

**为什么 Agent 特别需要幂等？** 因为它会重试。超时了重试、进程被 kill 了重试、并发调度重试——人手动敲命令很少连敲两次，Agent 会。没有幂等键，就是重复发文章、重复下单、重复扣款。

FreshAI CLI 的做法：客户端生成一个 UUID 请求编号，作为 `Idempotency-Key` 发给服务端，并且**在请求发出前就把它打到 stderr、留在错误里**：

```python
print(f"request-id: {resolved_request_id}", file=sys.stderr)
# …
extra_headers={"Idempotency-Key": idempotency_key}
```

服务端按 `(author, request_id)` + 内容摘要去重，语义必须明确写清楚：

| 情况 | 服务端行为 |
|---|---|
| 同编号 + 同内容 + 目标状态未变 | 返回原结果，`replayed=true`，不新建 |
| 同编号 + 不同内容 / 不同模式 | `409 request_conflict`，不覆盖 |
| 同编号但原稿已发布 / 已删除 | `409 resource_state_changed`，不复活、不自动公开 |

这样「重试」就变成了安全操作。反过来，**如果 CLI 每次重试都生成新编号，幂等就形同虚设**——这一点下面「难点」还会展开。

### 2.7 区分「失败」和「结果未知」

这是全篇**最重要、也最容易做错**的一点，值得单列一节，我放在第三部分重点讲。

### 2.8 配置解析要有确定的优先级

环境一多，站点/后端地址就会飘。FreshAI CLI 把解析顺序定死，并且让 `doctor` 命令把**来源**也报出来：

```
--server  >  进程环境变量 DOMAIN  >  .env.local  >  .env  >  已保存的唯一站点凭证
```

两条纪律：

- **全部缺失时，在联网前就报 `invalid_input`（退出码 2）**，绝不连接到未知站点。
- **绝不静默回退。** 显式给了无效值就报错；本地存了多个站点就要求显式指定，不「猜」一个。

### 2.9 认证：让 Agent 能无人值守登录，但密钥不进 argv / history

- **永远不要提供 `--token` 参数。** 命令行会进入 shell history、进程列表（`ps`）、CI 日志。FreshAI CLI 明确「无明文 `--token` 参数」。
- **用设备码授权（[RFC 8628](https://www.rfc-editor.org/rfc/rfc8628) 风格）**：CLI 创建挑战 → 用户在浏览器确认 → CLI 按 `interval` 轮询、领取**只出现一次**的 token → 原子写入本地凭证文件。
- **最小权限 + 有效期 + 可撤销 + 不自动续期。** scope 分开（`drafts:create` / `drafts:read` / `publish`），30 天到期，网页可逐台撤销。
- **必须给一条无头路径。** `fresh login --no-browser` 只打印 URL 和核对码，方便在别的设备/无 GUI 环境完成授权。

### 2.10 本地先校验，未联网前拒绝非法输入

能本地判定的错误，就别浪费一次网络往返，更别让它产生半成品远程状态。FreshAI CLI 在打包阶段就把这些挡掉（退出码 2）：

- 标题为空；`--file` 与 `--package` 同时给；
- 文件不是合法 UTF-8；内容全空白；
- 超过大小上限（Markdown ≤ 1 MiB、HTML ≤ 2 MiB、ZIP ≤ 20 MiB）；
- `--request-id` 不是合法 UUID；`--file` 误传 `.zip`（提示改用 `--package`）。

### 2.11 命令树与命名：一致性 > 聪明

- **动词-名词分层**，和 `git` 一致：`fresh blog draft create` / `fresh blog draft get <id>` / `fresh blog draft list` / `fresh blog publish`。
- **参数命名要全链统一。** 这一条是用真实返工换来的：初版写成了 `--site`，与规格里的 `--server` 不一致，最后从参数、`args`、帮助文案、报错文案到测试和文档全部更名了一遍。
- **帮助即文档。** `prog`、`description`、每个参数的 `help` 都写清楚，让 Agent（通过 `--help`）能自学命令树。

---

## 三、重点与难点拆解

### 难点一：「结果未知」——网络失败不等于操作失败

**现象：** 一个创建文章的请求发出去，读响应时超时了。这次创建到底成功了没有？——**不知道。**

如果 CLI 简单地把超时当「失败」，Agent 会：
- 认为文章没发出去 → 重发 → 如果第一次其实成功了，就产生了重复；
- 或者反过来，Agent 以为成功了，实际服务端根本没收到。

**正确做法：把「请求执行状态」提升为一等公民。**

```python
EXECUTION_COMPLETED = "completed"    # 已知结果
EXECUTION_UNKNOWN = "unknown"        # 已发出，结果未知
EXECUTION_NOT_STARTED = "not_started"  # 本地拒绝，没发出
```

关键在**区分「连接阶段失败」和「发送后失败」**：

```python
except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
    # 连都没连上，请求肯定没送达
    raise TransportError("无法连接 …", sent=False, timed_out=True)
except httpx.TimeoutException as exc:
    # 发出去了但没等到响应，可能已经成功
    raise TransportError("请求超时 …", sent=True, timed_out=True)
```

然后对「结果未知」给出**可执行的重试指令**，而不是一句「失败了」：

```python
if transport_failure.sent:
    retry_hint = (
        f"请求已发送但结果未知，请用相同命令与相同编号重试：--request-id {request_id}"
        "（不要切换 draft/publish 模式）。"
    )
    execution_status = EXECUTION_UNKNOWN
```

5xx 也一样处理：**服务端 500 可能是写了一半，属于结果未知**，不能当作确定失败。

> 这条原则的价值：错误分类错一档，Agent 的决策就错一个方向。区分 `not_started`（可安全重发）和 `unknown`（必须原编号重试）是「Agent 敢用这个 CLI」的前提。

### 难点二：幂等的边界是一个状态机

幂等键不是「查一下有没有就返回」那么简单，资源会**变状态**：草稿会被网页发布成公开文章、会被删除。此时同编号的旧请求该怎么答？答案是**冲突，而不是复活或覆盖**：

```
draft --(网页 publish)--> published --(不可逆)--> 公开文章
draft --(网页 delete)--> deleted    --(不可恢复)
```

- 原稿还在草稿态 → 同编号同内容重放，返回原 `id`；
- 原稿已发布/已删除 → `409 resource_state_changed`，**不复活、不自动公开、不改动已公开文章**。

同时，网页端的操作和 CLI 的创建请求可能并发，必须保证「同一状态转换只有一方成功」。这套状态机（而不是「有就返回」）才是真正可用的幂等。

### 难点三：凭证存储的原子性与权限

本地凭证文件里是明文 token，一旦损坏或权限过宽就是事故。要做到：

- **目录 0700、文件 0600**，读取时**校验权限**，过宽直接拒绝（`CredentialStoreError`）；
- **原子写入**：同目录临时文件 → `fchmod` → `write` → `flush` → `fsync` → `os.replace`，任何一步失败都清理临时文件、**不破坏既有文件**；
- **拒绝损坏内容**，而不是静默返回空凭证（否则用户会莫名「被登出」）；
- **支持 `FRESH_HOME` 重定向**，这是让测试隔离真实 `~/.fresh` 的关键（下面测试部分会用到）。

```python
descriptor, temporary_name = tempfile.mkstemp(dir=str(credentials_path.parent), …)
try:
    os.fchmod(descriptor, CREDENTIALS_FILE_MODE)
    with os.fdopen(descriptor, "w", encoding="utf-8") as fh:
        json.dump(all_credentials, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(temporary_name, credentials_path)
except BaseException:
    os.unlink(temporary_name)  # 失败不留垃圾，也不动旧文件
    raise
```

### 难点四：超时要分层

一个 `timeout` 值打天下是不行的：

- **连接超时**和**读超时**语义不同（前者可安全重试）；
- **创建/发布类**请求要传文件、服务端要解包落库，**只读**请求则应该快速失败。FreshAI CLI 给创建类 120s 总墙钟、只读 10s；
- Agent 侧还得有**自己的调用超时**，且要大于 CLI 超时，否则 Agent 先把 CLI 杀了，就永远拿不到 `unknown` 这个语义。

### 难点五：轮询类交互的细节

设备码登录是一条**长时间、可能抖动**的轮询链路，几个坑：

- 必须尊重服务端给的 `interval`，过快会被回 `slow_down`，要**顺延并退避**；
- 要有**总截止时间**（`expires_in`，默认 10 分钟），到点报 `authorization_expired`；
- **网络抖动不等于授权失败**，应打印进度并继续轮询，而不是直接退出；
- token **只发放一次**，已领取再轮询要报「请重新登录」而不是重复发；
- 领取成功后**落盘失败，要尽力撤销刚拿到的授权**，否则会留下一份「用户以为没登录、服务端却存在」的僵尸凭证。

### 难点六：分发与版本一致性（一个真金白银的坑）

CLI 源码改了，但**分发的 wheel 版本号没变**（一直是 `0.1.0`），会发生什么？`uv` 看到 URL 和版本都没变，直接用缓存里的旧构建——**你改了代码，用户装到的还是旧的，而且毫无报错**。

规避方式：

- 改源码后**必须重新构建并提交 wheel**，让分发产物与源码一致；
- 从站点安装时显式强制刷新：`uv tool install --reinstall --refresh "<wheel URL>"`；
- wheel URL 必须以真实文件名（`.whl`）结尾，`uv` 才认，所以先查元信息端点再拼 URL；
- 更好的做法是让版本号真正随发布递增，而不是恒定。

再往上一层是**更新机制本身的设计**，对 Agent 场景有两条特殊纪律：

- **不要做静默自动更新。** 人用 CLI，更新后行为变了会自己发现；Agent 的脚本是按当次 `--help`/契约写的，后台悄悄换版本等于脚本脚下抽地板。正确姿势：提供 `--version`，可以启动时提示「有新版本」，但升级必须由调用方显式触发。
- **升级必须遵守 append-only contract。** 旧脚本依赖的命令、参数、退出码、JSON 字段一个都不能变、不能删、不能改语义——否则每次更新都是一次全量脚本回归。`schema_version` 与版本提示配合，让 Agent 能感知并自行决定是否迁移。

### 难点七：测试策略——契约测试 + 真实入口 E2E

Agent 驱动的 CLI 出错代价高，测试要分两层：

**① 契约测试（快，不发真实网络）。** 用 `httpx.MockTransport` 注入假响应，验证 envelope 形状、错误码映射、退出码、站点解析、打包逻辑。关键是把副作用隔离掉：

```python
@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("FRESH_HOME", str(tmp_path / "fresh-home"))  # 别碰真实 ~/.fresh
    monkeypatch.delenv("DOMAIN", raising=False)
    monkeypatch.chdir(tmp_path)

@pytest.fixture(autouse=True)
def no_real_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda seconds: None)          # 跳过轮询等待

@pytest.fixture(autouse=True)
def no_real_browser(monkeypatch):
    monkeypatch.setattr(cli_auth.webbrowser, "open", lambda *a, **k: True)
```

**② 真实入口 E2E（慢，但不可省）。** 用真实浏览器走授权页、真实 CLI 子进程（从 wheel 安装、`cwd` 在仓库外、`HOME` 隔离、不传 `--server` 走主路径解析），验证「安装 → 登录 → 草稿 → 发布 → 撤销」的完整闭环。只测 mock 的 CLI 会在真实授权页、真实 CSP、真实跳转上翻车。

---

## 四、避坑清单（速查表）

| # | 坑 | 症状 | 正确做法 |
|---|---|---|---|
| 1 | 默认交互 | Agent 卡在确认/分页，直到超时 | 默认非交互，交互只留给显式命令 |
| 2 | 进度写 stdout | `json.loads(stdout)` 失败 | 进度/日志一律 stderr |
| 3 | JSON 模式混入人类文案/彩色 | 解析器被 emoji、ANSI 码带偏 | JSON 模式只输出一个 envelope |
| 4 | 直接抛 traceback | Agent 读到一堆栈，无法纠错 | 结构化 `error.code` + 可执行建议 |
| 5 | 明文 `--token` | 进 shell history / ps / CI 日志 | 设备码授权，token 只经本地凭证 |
| 6 | 把超时当失败 | 重复副作用（重复发文） | 区分 `not_started` / `unknown` |
| 7 | 忽略幂等 | 重试即重复写 | `Idempotency-Key` + 状态机 |
| 8 | 静默切换站点/环境 | 写错环境，且无人察觉 | 优先级固定，缺失即报错 |
| 9 | 退出码随手写 | 脚本无法分支 | 语义化并写进文档，`Ctrl+C` 用 130 |
| 10 | 错误里带 secret/正文 | 泄密 | 错误脱敏，不回显 HTML/异常原文 |
| 11 | 只读命令也强制登录 | `doctor` 之类无法排障 | 只读诊断不要求身份校验 |
| 12 | 凭证权限 0644 | 明文 token 被同机他人读取 | 目录 0700、文件 0600，原子写 |
| 13 | 跟随重定向跨 origin | 串站/SSRF，写错站点 | 关闭自动重定向，校验同 origin |
| 14 | wheel 版本恒定 | 改了源码，用户装到旧构建 | 重建并提交 wheel，`--reinstall --refresh` |
| 15 | CLI import 后端内部代码 | 耦合重、装不上、版本打架 | 独立包，只依赖 HTTP 客户端 |
| 16 | 人类表格和机器输出共用一条路径 | 机器解析人类排版 | `--json` 与文本模式分路 |
| 17 | 分页缺失/无上限 | 列表撑爆上下文 | `--limit`/`--offset`，默认有界 |
| 18 | 只按扩展名判定内容格式 | `.htm` / 无扩展名的 HTML 被静默当 Markdown 发成字面文本 | 内容嗅探（`<!doctype html`）兜底，或对可疑组合给出警告 |

---

## 五、一个最小骨架

把上面的原则压成一个可以直接抄的骨架（Python + argparse + httpx）：

```python
# output.py —— 输出契约与退出码
SCHEMA_VERSION = 1
EXIT_OK, EXIT_LOCAL_INPUT, EXIT_AUTH = 0, 2, 3
EXIT_HTTP, EXIT_NETWORK, EXIT_PROTOCOL, EXIT_INTERRUPTED = 4, 5, 6, 130


class CliError(Exception):
    def __init__(self, code, message, *, http_status=None,
                 execution_status="completed", exit_code=EXIT_HTTP, request_id=None):
        super().__init__(message)
        self.code, self.message = code, message
        self.http_status, self.execution_status = http_status, execution_status
        self.exit_code, self.request_id = exit_code, request_id


def success_envelope(result, *, request_id=None):
    return {"schema_version": SCHEMA_VERSION, "ok": True, "result": result,
            "error": None, "request_id": request_id}


def error_envelope(error: CliError):
    return {"schema_version": SCHEMA_VERSION, "ok": False, "result": None,
            "error": {"code": error.code, "message": error.message,
                      "http_status": error.http_status,
                      "execution_status": error.execution_status},
            "request_id": error.request_id}


# main.py —— 统一错误出口
def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _dispatch(args)
    except CliError as error:
        _emit_cli_error(error, as_json=bool(getattr(args, "json", False)))
        return error.exit_code
    except KeyboardInterrupt:
        print("已中断", file=sys.stderr)
        return EXIT_INTERRUPTED
```

配套的 `_emit_cli_error` / `print_json_envelope` 记住两条：**JSON 模式走 stdout，文本模式走 stderr；进度永远 stderr。**

---

## 六、交付前自检清单

- [ ] 默认非交互；危险操作靠「独立命令 + 最小 scope」，而不是交互确认
- [ ] stdout 只有结果，stderr 只有诊断；JSON 模式不混入人类文案
- [ ] 统一 envelope + `schema_version`，成功/失败同形状
- [ ] 退出码语义化、已文档化，`Ctrl+C` 返回 130
- [ ] 所有写操作幂等：`request-id` / `Idempotency-Key`，并定义重放/冲突/状态变更语义
- [ ] 严格区分 `completed` / `unknown` / `not_started`，对 `unknown` 给出原编号重试指令
- [ ] 错误脱敏，不回显 token、正文、服务端 HTML、原始异常
- [ ] 配置优先级明确且可诊断；缺失时联网前报错；不静默回退
- [ ] 无明文 `--token`；支持无头/设备码登录；凭证 0600 原子写
- [ ] 本地输入校验（编码、空值、大小、互斥、格式）先于联网
- [ ] 列表有界（分页/limit），不撑爆上下文
- [ ] 契约测试用 mock transport + 隔离 HOME；E2E 走真实入口
- [ ] 分发产物（wheel）版本与源码一致

---

## 参考

- [Agent CLI Guidelines（aclig.dev）](https://aclig.dev/) —— 面向 Agent 的十条不变量：只读默认、自描述、有界输出、注入防护、可无头认证、只增契约等
- [12 Factor CLI Apps（Heroku / JDX）](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46) —— 帮助、flags、stdout/stderr、错误处理、XDG
- [clig.dev](https://clig.dev/) —— 命令行界面设计通用准则
- [RFC 8628：OAuth 2.0 Device Authorization Grant](https://www.rfc-editor.org/rfc/rfc8628) —— 设备码授权
- FreshAI CLI 源码：`packages/fresh-cli/src/fresh_cli/`（`main.py` / `output.py` / `client.py` / `credentials.py` / `config.py` / `blogs.py` / `auth.py`）
