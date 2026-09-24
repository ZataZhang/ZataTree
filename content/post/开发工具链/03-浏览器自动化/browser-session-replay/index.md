---
title: 浏览器会话录制与接口回放：方案调研
date: 2026-07-27
image: images/index/index.svg
categories:
    - Platforms_Tools
tags:
    - dev_tools
    - Browser-Automation

---

## 背景与目标

想做这样一个工具：

1. 用户打开一个目标网站
2. 在浏览器里手动操作（点击、输入、滚动、跳转）
3. 后台实时记录每一步 DOM 事件 + 每个 HTTP 接口的请求/响应
4. 操作结束后，能看到一份按时间线排列的"操作 + 接口"清单，必要时还能重放

这类能力在业内通常叫 **Session Replay / 用户会话录制**。

## 核心原理

```
┌─────────────┐   事件 / 网络上报     ┌──────────┐
│  浏览器注入  │ ────────────────────> │  后端    │
│  SDK / 扩展  │                      │  落库    │
└─────────────┘                      └──────────┘
       │                                   │
       │ DOM 快照 + 事件流                  ▼
       └─────────────────────>        回放页面
                                   (rrweb-player 等)
```

关键三件事：

- **DOM 事件捕获**：`click` / `input` / `scroll` / `navigation`，通常用 `addEventListener` 全局委托 + 事件冒泡
- **网络拦截**：浏览器侧 `XMLHttpRequest` / `fetch` 包装一层钩子，或者用 Service Worker / 浏览器扩展的 `webRequest` API
- **DOM 变化记录**：`MutationObserver` 监听 DOM 增量变化，配合初始快照实现像素级回放

## 现有方案

### 商业产品（开箱即用）

| 工具 | 特点 |
|---|---|
| **SessionStack** | 像素级回放 + 错误捕获 + 性能分析，企业级 |
| **FullStory** | 数字体验分析，强在漏斗和搜索 |
| **LogRocket** | 类 SessionStack，回放 + Redux/Zustand 状态回放 |
| **Hotjar** | 更偏热力图和漏斗 |
| **Microsoft Clarity** | 免费，基础回放 + 热力图 |

### 开源方案

- **[rrweb](https://github.com/rrweb-io/rrweb)** — 最主流的开源前端录制库，用 `MutationObserver` + 事件监听完整还原 DOM 变化，配套有 `rrweb-player` 回放器。LogRocket 早期也借鉴过类似思路
- **rrweb-snapshot / rrweb-player** — 序列化和回放子包
- **Playwright Trace Viewer** / **Patchright** — 如果场景是"复现自动化流程"，Playwright 自带的 trace 就能记录每一步点击、请求、截图

## 自己从零做的思路

### 最简 MVP

```
浏览器扩展
  └─ content script 注入目标页面
       ├─ 监听 click / input / scroll
       ├─ 包装 XHR / fetch
       └─ 周期性上报到 /collect
后端
  └─ POST /collect  → 追加写入 events.jsonl
本地 CLI
  └─ 解析 events.jsonl  → 打印时间线 / 启动 rrweb-player
```

代码量很小，半天能跑通。

### 进阶版（像素级回放）

```js
// 浏览器侧：rrweb 录制
import { record } from 'rrweb';
const events = [];
record({
  emit(event) { events.push(event); },
});
// 周期性批量上报到后端
setInterval(() => postEvents(events.splice(0)), 1000);
```

```js
// 回放侧
import rrwebPlayer from 'rrweb-player';
new rrwebPlayer({
  target: document.body,
  props: { events: fetchedEvents },
});
```

## 选型建议

按"想做什么"分场景推荐：

| 需求 | 推荐方案 |
|---|---|
| 自己排查自动化 bug | **Playwright Trace**（`context.tracing.start()`），零成本 |
| 给自家产品做用户行为分析 | **rrweb + 自建后端**，可控、私有化部署友好 |
| 想要现成的商业级方案 | **LogRocket / SessionStack** |
| 只想看热力图 | **Hotjar / Microsoft Clarity**（免费） |

## 与现有 patchright 项目的结合点

本仓库（kimi-patchright）本身在做浏览器自动化相关的 slide 调试。如果只是想在调试 slide 自动化流程时复盘浏览器里的真实操作 + 接口调用，**Playwright Trace + patchright 的 `page.on('request')` / `page.on('response')` 就够用了**，不需要单独再搭一套录制系统。

如果目标是 toC 的通用录制工具，那需要再想清楚定位：是要 rrweb 那种像素回放，还是只做事件流（轻量、可被搜索聚合）。

## 参考资料

- rrweb: https://github.com/rrweb-io/rrweb
- SessionStack 原理: https://www.sessionstack.com/
- Playwright Trace: https://playwright.dev/docs/trace-viewer