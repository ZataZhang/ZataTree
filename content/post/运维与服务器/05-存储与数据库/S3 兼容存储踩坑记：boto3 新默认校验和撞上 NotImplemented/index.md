---
title: S3 兼容存储踩坑记：boto3 新默认校验和撞上 NotImplemented
description: "一次寻常的重新部署，让博客发布接口全线 500——最小草稿也发不出去，但登录、列表、健康检查全是绿的。根因藏在 boto3 1.36 的一次默认值变更里：PutObject 悄悄带上了 STREAMING-UNSIGNED-PAYLOAD-TRAILER，而第三方 S3 兼容实现不认这套新编码。"
date: 2026-09-10T23:58:52+08:00
slug: s3-boto3-checksum-notimplemented
image: images/index/index.svg
categories:
    - Platforms_Tools
tags:
    - S3
    - boto3
    - 踩坑
toc: true
draft: false
---

## 一场"全线 500"的发布事故

用自家 CLI 发布一篇博客，服务端返回 500。第一反应：肯定是包格式不对——毕竟几分钟前刚被 422 拒过一次（一个 2.9MB 的自包含 HTML 超了单条目 2MiB 上限），说明接口是通的，可能是我 ZIP 打包的方式不合规范。

于是按标准流程排查：换 Markdown 源文件 + 图片资源重新打包、用最小草稿（三行文字的 md）测基本链路、HTML 单文件再试一遍……结果所有创建请求一律 500，draft 和 publish 两个端点无一幸免。

但诡异的是：登录正常，草稿列表正常，健康检查正常，公开博客列表也能刷出来。**所有读路径全绿，所有写路径全红。**

如果真是包格式问题，最小草稿不可能挂；如果是认证问题，读接口不可能全通。这不像"我的请求有问题"，更像"服务端某个环节坏了"。

## 422 和 500 之间隔着一道分界线

回头看现象，有一条隐藏的分界线：

- 超限的 index.html 报 **422**（校验错误，`Zip entry exceeds the 2 MiB limit`）
- 所有通过校验的请求报 **500**

后端是分层架构：API 层收包 → core 层的 `BlogService.extract_zip_package` 做校验（格式、大小、路径白名单、symlink）→ 校验通过后 `upload_blog` 把正文和附件逐个写入对象存储。

422 在校验层抛出，说明请求已经正常穿过 API 层；500 卡在**校验通过后的第一步**——`put_object`。把服务端日志拉出来，最底下赫然一行：

```text
botocore.exceptions.ClientError: An error occurred (NotImplemented) when
calling the PutObject operation: Aws MultiChunkedEncoding
STREAMING-UNSIGNED-PAYLOAD-TRAILER is not supported.
```

问题根本不在博客业务，也不在包格式——是**对象存储的写入**挂了。博客发布只是撞在枪口上的第一个受害者：任何要往 S3 写东西的功能（博客、语音、知识库）此时全部阵亡。

## 先补一点背景：S3 兼容生态与请求编码

### S3 API 是事实标准，但"兼容"是程度问题

AWS S3 的 REST API 已经是对象存储的事实标准，MinIO、Cloudflare R2、Backblaze B2、各家云厂商的兼容端点都实现了这套协议。自建 MinIO 时，客户端通过几个参数接入：

```python
boto3.client(
    "s3",
    endpoint_url="http://your-minio:9000",  # 指向自建端点，而非 aws
    region_name="us-east-1",                # MinIO 通常随便填一个
    aws_access_key_id=...,
    aws_secret_access_key=...,
    config=boto3.session.Config(
        s3={"addressing_style": "path"},    # 关键：path-style
    ),
)
```

其中 `addressing_style` 决定 bucket 怎么进 URL：`path` 风格是 `http://endpoint/bucket/key`，`virtual_hosted` 风格是 `http://bucket.endpoint/key`。自建 MinIO 没法给每个 bucket 配域名泛解析，所以必须用 path-style——这是自建存储的第一个常识坑。

但"实现了 S3 API"不等于"实现了 AWS 最新加的每一个字段"。S3 协议在演进，兼容实现永远在追赶，追赶不上的时候，就会返回一个很直白的错误码：**NotImplemented**。

### 签名 V4 之下，请求体有三种"泳姿"

AWS 签名协议 V4 在传输 payload 时有这么几种形态：

| 形态 | 特点 |
|---|---|
| signed payload | 请求体整体参与签名计算，头里放完整哈希 |
| `UNSIGNED-PAYLOAD` | 请求体不参与签名，靠 TLS 保证完整性 |
| `STREAMING-*` | 请求体按 `aws-chunked` 分块流式传输，边传边签 |

而这次出事的 `STREAMING-UNSIGNED-PAYLOAD-TRAILER` 是最新的变体：分块流式 + 不签名 + **trailer**——即在所有数据块传完之后，再追加一个尾部块，携带整个请求体的 CRC32 校验和。这套机制是 AWS 2024 年底力推的"默认数据完整性"改造的一部分。

## 根因：boto3 1.36 改了一个默认值

2025 年 1 月，boto3 1.36.0 发布，官方 changelog 里有一条不起眼的变更：

> Default value of `request_checksum_calculation` is changed from `when_required` to `when_supported`.

翻译成人话：

- **以前（`when_required`）**：只有 API 明确要求校验和时才算。`PutObject` 不要求，所以请求体就是普通字节流，任何 S3 兼容实现都吃得下。
- **现在（`when_supported`）**：只要 API *支持* 校验和（`PutObject` 正好支持），就默认给请求体算 CRC32，并用上面那套 `STREAMING-UNSIGNED-PAYLOAD-TRAILER` 编码传输。

于是新版 boto3 对旧 MinIO（以及一批没跟进的兼容端点）发出的每个 PutObject 都长成了它们看不懂的样子，对端的回应整齐划一：`NotImplemented`。

为什么是"部署之后"才炸？仓库里 `pyproject.toml` 写的是 `boto3>=1.43.28`，依赖锁在 1.43.28。上一版镜像构建时拉的依赖、和这次重新构建拉的依赖，中间隔着这次默认值变更——**代码一行没改，重新构建镜像本身就成了变更**。这也是"锁文件 + 常态化重新部署"模式的一个隐性代价：依赖漂移会以最意想不到的方式找上门。

## 修复：一行 Config，三个层次

修复本身轻得可笑，在创建 boto3 客户端的 Config 里显式把行为钉回旧默认：

```python
# 修复前：跟随 SDK 默认，1.36+ 对 PutObject 附带流式校验尾
config=boto3.session.Config(s3={"addressing_style": addressing_style})

# 修复后：仅在 API 要求时才计算校验和
config=boto3.session.Config(
    s3={"addressing_style": addressing_style},
    request_checksum_calculation="when_required",
)
```

除了改代码，还有两条等价路径，按生效成本排序：

1. **环境变量**（不重新构建镜像，改完配置重启即生效）：给后端进程加 `AWS_REQUEST_CHECKSUM_CALCULATION=when_required`，botocore 会读这个变量；
2. **代码 Config**（本文做法）：写死在适配器里，不依赖部署环境是否记得配这个变量；
3. **升级存储端**：新版本 MinIO 已支持流式校验尾，升级后可以吃回新默认。但注意必须升到 2026-04 之后的补丁版本——这条 trailer 路径先后曝出 CVE-2025-31489、CVE-2026-40344 等认证绕过漏洞（签名校验不完整，持有任意 secret 即可上传），修复分别落在 `RELEASE.2025-04-03T14-56-28Z` 和 `RELEASE.2026-04-11T03-20-12Z`。对安全敏感的自建场景，`when_required` 依旧是更稳的答案。但"为了让客户端新默认能跑而去升级存储"这个依赖方向，在自建场景里通常不如反过来稳。

选代码层还有一个架构上的理由：全仓库只有一个创建 boto3 客户端的地方——infrastructure 层的对象存储适配器，博客、语音、知识库全部经由它读写。**修一处，全站愈合**；这也意味着这类坑永远值得修在适配器里，而不是散落在各调用方。

## 同类清扫：适配器里还埋着一个 ASCII 坑

顺着这次排查把对象存储适配器翻了一遍，发现它早已修过另一个"协议约束"类的问题，记录于此，因为它们本质上是同一类坑：**S3 的某些约束不在文档第一页，而在 HTTP 协议的物理规则里。**

S3 的用户元数据（`x-amz-meta-*`）走的是 HTTP header，而 RFC 7230 规定 header 值必须是 ASCII。存中文描述时，botocore 的 `validate_ascii_metadata` 会在**发请求之前**就拒绝你：

```python
put_object(key=..., data=..., metadata={"title": "融入"})  # ParamValidationError
```

适配器里的解法是"写入时编码 + 侧车标记还原"：非 ASCII 值先 percent-encode，同时多写一个 `<key>-encoding: utf-8-pct` 的侧车键；读取时发现有侧车标记就 `unquote` 还原。不依赖任何带外信息，元数据自描述。

```python
def _sanitize_s3_metadata(metadata):
    for key, value in metadata.items():
        if value.isascii():
            sanitized[key] = value
        else:
            sanitized[key] = quote(value, safe="")          # 值编码
            sanitized[f"{key}-encoding"] = "utf-8-pct"      # 侧车标记
```

把它和这次的校验和坑放在一起看，S3 兼容存储的踩坑地图就清晰了：**一类的坑源于"协议在演进，兼容端在追赶"（NotImplemented）；另一类源于"协议在收紧，客户端在把关"（ASCII 校验）**。前者修客户端编码方式，后者修数据编码方式，但都该修在同一个适配器里。

## 验证

修复的验证分三层，也正好对应问题的影响面：

1. **单元测试**：对象存储适配器的元数据编解码测试全过，确认 Config 变更不影响既有行为；
2. **影响面**：全仓库搜索 `boto3.client` 只有适配器一处调用点——博客、语音、知识库三条业务线同时被这一行修复覆盖；
3. **真实入口**：重新部署后，用 CLI 以原来的命令重新发布那篇文章，一次通过，公开页面正常渲染。

顺带一提，之前 422 拒掉的那个 2.9MB 自包含 HTML，最后也没有硬塞进去，而是改用设计内的路径：Markdown 正文 + 图片平铺进 `assets/` 打包上传。事后看这次事故像是两件事，其实共享同一个教训——**别和平台默认值较劲，走它给你留的路**。

## 几点收获

- **"兼容 S3"是一个光谱，不是一个开关**。协议基础操作（对象增删改查）早就稳定，差异都藏在演进中的新特性里。判断一个兼容端点的成色，看它对最新协议扩展的支持比看 README 有用。
- **SDK 的默认值也是 API**。boto3 这次变更完全符合语义化版本（major 没动，默认值动了），但对你来说行为就是变了。升级依赖 = 引入一次隐形变更，重新部署和改代码应该获得同级别的敬畏。
- **读写分离是天然的故障定位器**。"读全绿、写全红"直接把嫌疑范围从整个 API 收窄到存储写入路径。分层架构平时的意义在排障时兑现：日志栈从 API 层一路穿到 botocore，每层只做一件事，所以每一栈帧都在缩小包围圈。
- **报错信息里最值钱的词是 NotImplemented**。它不是"你错了"，而是"我们（实现方）还没做这个"——看到它就该去查协议演进和版本差异，而不是盯着自己的请求参数找茬。
