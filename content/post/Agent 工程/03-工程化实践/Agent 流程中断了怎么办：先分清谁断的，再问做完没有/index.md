---
title: "Agent 流程中断了怎么办：先分清谁断的，再问做完没有"
description: "Agent 节点、外部 API、传输连接和编排状态，四个位置的中断该用四种处理方式。本文整理业界通用的重试、检查点、幂等与对账做法，并用一次真实的 GitHub 接口抖动，说明把所有故障压成「失败就重跑」会白烧多少时间。"
date: 2026-10-23T18:00:00+08:00
weight: 140
slug: "Agent 流程中断了怎么办：先分清谁断的，再问做完没有"
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - Agent 工程实战
draft: true
---

2026 年 10 月 23 日，我让一个自动交付 Agent 的 runner 重跑 GitHub 上的 #73 号任务。前一次它在最后的独立验证阶段超时，我按失败评论里的恢复步骤换了标签，重新启动。

第一次重跑不到一分钟就失败了，日志只有一行：`POST .../issues/73/comments: EOF`。我什么也没改，再跑一次，这次跑了三个多小时，一路走到 pre-PR review，reviewer 补了一个修复提交，然后推送时又来了一个 `EOF`，这次是查询提交状态的 GET 请求。第三次启动时，日志写着「存在尚未交付就绪的本地提交（VerificationFailedError），重新运行 agent 以继续」：runner 把一次网络抖动记成了验证失败，打算把实现阶段重做一遍。

两次失败的原因都是 GitHub 的连接被断开，跟代码无关，却差点让三个小时的工作被当成没做完。这件事让我去查了业界对「中断」的通用处理。我的结论是：**重跑策略要由两个问题决定，一是断在哪个位置，二是这一步到底做完没有**；把所有故障压成「失败就重跑」，既会浪费，也会出事故。

## 一、中断发生在四个位置

一个 Agent 流程里，能断的地方至少有四类，它们的状态存在不同的人手里，重跑的含义也不一样。

| 位置 | 典型故障 | 重跑意味着什么 |
|---|---|---|
| Agent 节点 | 模型超时、输出格式错、陷入循环、进程被杀 | 非确定性，重跑的结果和上次不同 |
| 外部操作 | API 5xx、连接被断开、限流、鉴权过期 | 副作用可能已经发生，重跑可能重复生效 |
| 传输连接 | SSE 断流、长任务轮询中断 | 对端的任务可能还在继续跑 |
| 编排与状态存储 | 编排进程崩溃、机器重启、数据库不可用 | 决定前面三类能不能从中间续 |

一句话区分：Agent 节点重跑是重新掷骰子，外部操作重跑是重复按按钮，传输断线说明不了对端停没停，编排状态决定其余三者能不能恢复。

## 二、比「谁断的」更重要的问题：做完没有

对外部操作，结果有三种。对端明确拒绝是确定失败，收到确认是确定成功，这两种都好处理。麻烦的是第三种：请求发出去了，没拿到响应。超时、`EOF`、断流都属于这一类，调用方不知道对端到底有没有执行。

这时把它当失败直接重发，POST 可能已经生效，于是重复评论、重复下单；把它当成功往下走，又可能漏做。正确动作是先查对端状态，确认没做再补。能不能安全重试，取决于操作是否幂等：

- 天然幂等：GET、按 ID 覆盖写，直接重试。
- 可做成幂等：带幂等键的 POST，或者先查后写。
- 不可幂等：发邮件、扣款、推送出去就收不回的消息，需要补偿或人工确认。

AWS 的 Builders' Library 对此的说法是：有副作用的调用除非 API 幂等，否则不能放心重试；创建类 API 可能需要显式的幂等令牌（[Timeouts, retries and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter)）。

## 三、通用做法：几家系统各自守住了哪一条

下面每条做法都对应一个我查过文档的系统，只写文档里能找到出处的部分。

### 重试放在靠近故障的那一层，并且加退避和抖动

AWS 的文章给了两个理由。一是重试会给已经吃紧的系统加负载，过载时重试「可能让高负载在原始问题解决后还持续很久」；二是分层重试会相乘，文中的例子是五层每层重试三次，对出问题的数据库形成成倍的压力。配套做法是指数退避加抖动（让失败的客户端不要同一时刻一起重试），以及用令牌桶限制本地的重试总量。

### 错误要分类，不可重试的别重试

Temporal 的重试策略支持声明「不可重试的错误类型」，官方建议让重试策略通过超时和最大次数管理重试，只在重试没有意义时才标记不可重试（[Temporal 错误处理最佳实践](https://docs.temporal.io/best-practices/error-handling)）。LangGraph 的节点重试默认也做了分类：`ValueError`、`TypeError`、`RuntimeError`、`OSError` 等不重试，`requests` 和 `httpx` 抛出的错误只在 5xx 时重试（[LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api)）。

这里有个值得留意的细节：默认策略偏保守，网络层断开不一定被覆盖。**用了框架的重试，也要核对一遍它认哪些错误**。

### 用检查点让恢复从中间开始

LangGraph 在每个 super-step 边界写检查点，同一步里并行节点部分失败时，成功节点的写入单独保存，续跑不会重做（[LangGraph 持久化](https://docs.langchain.com/oss/python/langgraph/persistence)）。官方同时要求工作流确定且幂等，副作用要包进 task 里。Temporal 走的是另一条路：编排逻辑靠事件历史重放恢复，有副作用的 Activity 单独重试；Activity 可能「完成后、上报前崩溃」而被重试，所以也要求幂等（[Temporal Activity 故障检测](https://docs.temporal.io/encyclopedia/detecting-activity-failures)）。

两家的共同点：恢复的粒度是阶段或节点，不是整条流水线。

### 对「结果未知」，用幂等键或对账

Stripe 的做法很典型：连接出错、不知道对端是否收到时，用同一个幂等键和同样的参数重发，不会产生重复对象；服务端保存首次请求的状态码和响应体并原样返回，同键不同参数会报错；v1 的键约 24 小时后可被清理（[Stripe：Idempotent requests](https://docs.stripe.com/api/idempotent_requests)）。IETF 也有 Idempotency-Key 头的[草案](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header)，说明这是通用模式。

没有幂等键的接口怎么办？我没有找到 GitHub 对评论创建支持幂等键的文档，下面按「没有」处理。常见替代是在正文里放一个唯一标记，重试前先搜索这个标记是否已存在，存在就当成已发送。

### 远程 Agent 断流，先查状态，再决定订阅还是重发

A2A 1.0 规范里，`GetTask` 取回任务当前状态，`SubscribeToTask` 重新接上事件流。后者的第一个事件必须是当前 `Task`，任务到终态时流必须结束，对已处于终态的任务调用会返回 `UnsupportedOperationError`（[A2A 规范 1.0.0](https://a2a-protocol.org/latest/specification/)）。所以断流后的顺序是：先 `GetTask`，已终态就直接取结果，没到终态再订阅，任何情况下都不应该重新发起一次任务。任务状态里还有 `INPUT_REQUIRED` 和 `AUTH_REQUIRED` 两个中断态，它们要等人或凭据，不是故障。

### 错误什么时候交给模型

Anthropic 的工具调用文档里，工具执行出错时返回 `tool_result` 并设 `is_error: true`，示例就是一个 `ConnectionError ... (HTTP 500)`；参数缺失时 Claude 会带着修正重试 2～3 次。文档还建议错误信息要有指导性，例如 `Rate limit exceeded. Retry after 60 seconds.`（[Anthropic：Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)）。

文档没有规定「网络错误该不该回灌」。我的做法是先在工具层退避重试，用尽预算再回灌；回灌时带上错误类别、已重试次数和「结果是否未知」。否则模型看到一句 `failed`，很可能直接把写操作再发一遍。这一条是我的设计取舍，不是业界共识。

## 四、较优做法：按位置和结果分流

把上面的做法合起来，可以得到一张处理表。

| 故障 | 结果是否已知 | 处理 | 不要做 |
|---|---|---|---|
| 模型输出格式错 | 已知，无副作用 | 带校验错误重试 1～2 次 | 无限重试 |
| 模型停滞或循环 | 已知 | 监督器介入，限制步数，升级给人 | 一直等总超时 |
| 读请求连接被断开 | 无副作用 | 退避加抖动，重试数分钟 | 当业务失败上报 |
| 写请求连接被断开 | **未知** | 先对账（幂等键或唯一标记），再决定补发 | 直接重发或直接判失败 |
| 429 限流 | 已知，未执行 | 按 `Retry-After` 挂起，不算失败 | 立即重试 |
| 401 / 403 | 已知 | 停止并上报 | 重试 |
| 400 校验失败 | 已知 | 回灌给 Agent 或上报 | 当网络错误重试 |
| SSE 或连接断开 | 对端状态未知 | 先查任务状态，未终态再订阅 | 重新发起任务 |
| 编排进程崩溃 | — | 从持久化检查点恢复 | 依赖内存状态 |

这张表背后是四条原则：错误先分类，每类对应一种动作；重试留在最小范围内，耗尽预算才向上抛，而且上层不能把它当成 Agent 工作失败；对外的写操作要留痕，状态至少区分待发、已发、已确认、未知；恢复的粒度跟着阶段走，发布阶段出问题只重做发布。

升级也要有梯度：自动恢复、挂起等待（限流、网络）、通知人。挂起不等于失败，这一点很容易被忽略。

## 五、回头看 #73：三处缺口

用这个框架对一遍 #73 的失败，问题落在 runner 的 GitHub 调用封装里，一共三处。

1. **重试名单里没有 `EOF`。** 可重试的错误靠一组正则识别，列了 TLS 握手超时、`no such host`、500 到 504、499 等，没有连接被断开这一类，所以 `EOF` 一次就判死刑。
2. **读请求根本不重试。** 查询提交状态的函数用 `check=False` 调用，而重试逻辑只在命令抛出异常时才进入，`check=False` 下失败只返回非零退出码，直接绕过了重试。
3. **重试只有约两秒。** 总共 3 次，间隔固定 1 秒。一次几十秒的网络抖动，两秒内全部用完。

再加上推送阶段把所有异常都包成「发布失败」，pre-PR review 随后记成「验证失败」，下一轮就把它当成没做完的实现重跑。这是位置判断出错：外部操作的故障被计入了 Agent 节点。对照第二节，`POST` 评论那次属于结果未知的写操作，更合适的处理是退避重试后，用评论里已有的 `iar:claim` 标记对账。

这三处都不复杂，难的是意识到它们是同一个问题：分类粒度不够，所有故障走同一条路径。

## 六、什么时候不必做这么多

不是每个系统都要上完整的 Durable Execution 或副作用账本。我会按成本分三档：

- **现在就值得做**：补全可重试错误名单、让读请求也走重试、退避拉长并加抖动。改动小，直接消除一类误判。
- **按需做**：只给有副作用的几类写操作（评论、标签、创建 PR）加对账，不必铺到所有调用。
- **暂缓**：引入工作流引擎。只有出现多步、不可逆、且跨系统的外部操作时才值得。

还有一个限制：本文的 GitHub 幂等结论我没有在官方文档里核实，A2A 规范我只读了前面约十万字符，LangGraph 的退避参数没有查到。落地前这几处要再对照一次官方文档。

## 七、结论

中断本身不是问题，问题是处理它的人不知道自己面对的是哪一种。先问断在哪个位置，再问这一步做完没有：Agent 节点按阶段续，外部读操作退避重试，结果未知的写操作先对账，断流的远程任务先查状态。做到这三步，网络抖一下，就只是日志里多一行警告。

## 出处

- [Timeouts, retries and backoff with jitter（AWS Builders' Library）](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter)
- [Temporal：错误处理最佳实践](https://docs.temporal.io/best-practices/error-handling)；[Activity 故障检测](https://docs.temporal.io/encyclopedia/detecting-activity-failures)
- [LangGraph：持久化](https://docs.langchain.com/oss/python/langgraph/persistence)；[Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)；[Graph API（重试策略）](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [A2A 协议规范 1.0.0](https://a2a-protocol.org/latest/specification/)
- [Anthropic：Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
- [Stripe：Idempotent requests](https://docs.stripe.com/api/idempotent_requests)；[IETF Idempotency-Key 草案](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header)
- #73 的现象与 runner 的重试逻辑来自本人本机运行日志与 runner 源码（keda `github_client.py`、`github_helpers.py`、`github_pr_ops.py`），均为一手材料。
