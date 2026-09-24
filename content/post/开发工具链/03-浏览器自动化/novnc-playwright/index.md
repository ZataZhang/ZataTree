---
title: 从 noVNC 到 Playwright 截图流：容器内 VNC 踩坑记
description: 在 Docker 容器内为有头 Chrome 提供远程桌面，先后踩遍 MIT-SHM 0-byte、VizDisplayCompositor 黑屏、x11vnc Azure VM 兼容性等坑，最终放弃 VNC 协议，改用 Playwright Page.screenshot 自定义帧流。记录选型思路、六轮修复与最终架构。
date: 2026-06-09T14:00:00+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - Docker
    - Playwright
    - VNC
    - Browser-Automation
---

## 背景

项目是一个 FastAPI 后端 + Playwright 驱动的浏览器自动化服务，目标是让用户在网页里远程操作一个跑在 Docker 容器内的 Chrome，完成 `kimi.com` 的一次性扫码/账号登录。登录态写入持久化 profile，后续 PPT 生成任务复用。

远程桌面的需求看起来很简单：
- 容器内：`Xvfb`（虚拟显示）+ `openbox`（窗口管理）+ `x11vnc`（VNC 服务端）
- 后端：FastAPI WebSocket 做字节中继，把前端的 RFB 流量转发到 `127.0.0.1:5910`
- 前端：`@novnc/novnc` 的 `RFB` 类连接 WebSocket，渲染桌面

架构上也很规矩：5910 不对外暴露，WebSocket 走 443/HTTPS，用管理员 token + 一次性 ticket 鉴权，没有旁路端口。

PRD 写得整整齐齐，验收清单全部打勾，看起来万无一失。然后我们就掉进了坑里。

---

## 坑一：MIT-SHM 0-byte 画面

**症状**：noVNC 连接成功，但画面全黑，或者显示 0-byte 的帧。

**根因**：x11vnc 默认使用 X11 的 MIT-SHM（共享内存扩展）加速画面抓取。在 Docker 容器里，共享内存行为跟宿主机不一致，x11vnc 读不到像素数据。

**修复**（`2fa2602`）：给 x11vnc 加参数绕过 MIT-SHM：

```bash
x11vnc -noxshm -noxkb -noxrecord -noxfixes -noxdamage ...
```

或者通过环境变量透传：

```bash
X11VNC_EXTRA_ARGS="-noxshm -ncache 0"
```

这个坑还算好填，加参数就能绕过。

---

## 坑二：Chrome VizDisplayCompositor 导致黑屏

**症状**：x11vnc 终于有画面了，但 Chrome 窗口区域永远是黑的。其他窗口（xterm、openbox）显示正常。

**根因**：Chrome 默认启用 Viz Display Compositor，把实际渲染放到独立的合成器进程里，用 GPU 或特殊缓冲区，导致普通的 X11 像素读取（`XGetImage`、`XShmGetImage`）抓不到 Chrome 内容。

**修复**（`58cb8ed`）：启动 Chrome 时禁用 VizDisplayCompositor：

```bash
google-chrome --disable-features=VizDisplayCompositor ...
```

这个坑比较隐蔽，因为其他应用都能正常显示，唯独 Chrome 黑屏。排查了好一阵才定位到是 Chrome 的合成器机制。

---

## 坑三：x11vnc 在 Azure VM 上的兼容性

**症状**：本地 Mac Docker Desktop 测试正常，推到 Azure VM（Ubuntu 24.04，内核 `6.14.0-1017-azure`）后，x11vnc 要么崩溃，要么帧率极低，要么随机断开。

**根因**：x11vnc 对内核版本、X11 扩展、共享内存的依赖比较深，不同宿主机环境表现差异很大。

这时候我们开始尝试替换 VNC 服务端。

### 尝试 1：x0vncserver

TigerVNC 的 `x0vncserver` 更轻量，但 Ubuntu 24.04 的软件源里根本没有这个包（`6765172`）。

### 尝试 2：Xtigervnc

切换到 `Xtigervnc`（`1d3222c`），但发现它的 X0 扩展支持不完整，抓取现有 X 会话的能力不如 x11vnc。

### 尝试 3：x11vnc + ncache

最后又滚回 x11vnc，加上 `-ncache 10` 做客户端缓存（`8ba411d`），试图缓解帧率问题。

这一系列反复说明一个问题：**在容器化 + 云服务器环境下跑传统 VNC 服务端，是一件非常脆弱的事**。每个环境变量、每个内核版本、每个 X11 扩展都可能成为压垮骆驼的最后一根稻草。

---

## 最终方案：彻底放弃 VNC，改用 Playwright 截图

与其继续跟 x11vnc 搏斗，我们换了一个思路：

**既然 Playwright 已经开着 Chrome，为什么不直接让 Playwright 截屏？**

新方案（`40b9014`）：

1. **后端**：Playwright 的 `Page.screenshot()` 每 250ms 截一张图
2. **传输**：自定义 `WebSocketFrameBridge`，把 PNG 字节包上 length-prefixed JSON envelope，通过现有 WebSocket 推给前端
3. **前端**：不用 noVNC RFB 了，直接用原生 `WebSocket` 收帧，把 PNG blob 塞进 `<img>` 标签
4. **输入**：前端把鼠标/键盘事件序列化成 JSON，通过同一个 WebSocket 发回后端，后端用 `page.mouse.click()`、`page.keyboard.press()` 回放

Wire 格式：

```
4-byte LE length (uint32)
N bytes JSON: {"type": "frame", "seq": N, "size": M, "format": "jpeg"}
4-byte LE length (uint32)
M bytes PNG payload
```

---

## 新旧方案对比

| 维度 | noVNC + x11vnc | Playwright 截图流 |
|---|---|---|
| 依赖 | Xvfb + openbox + x11vnc + MIT-SHM workaround | 只有 Xvfb |
| Chrome 兼容性 | 需要 `--disable-features=VizDisplayCompositor` | 不需要特殊 flags |
| 容器稳定性 | 极易受宿主机内核/环境差异影响 | 纯用户态，跟宿主机无关 |
| 带宽 | RFB 协议有增量压缩，带宽低 | 每帧完整 PNG/JPEG，带宽高 |
| 延迟 | RFB 增量更新，延迟低 | 250ms 轮询，延迟稍高 |
| 实现复杂度 | 需要 RFB 中继、VNC 参数调优 | 自定义帧协议，前后端约 200 行 |
| 可维护性 | x11vnc 是黑盒，出问题难排查 | Playwright 截图是白盒，可控 |

牺牲了一点带宽和延迟，换来的是**极高的稳定性和可维护性**。

---

## 教训

1. **VNC 协议是为局域网桌面共享设计的**，强行塞进 Docker + 浏览器自动化的场景，属于削足适履。MIT-SHM、GPU 合成器、X11 扩展这些历史包袱在容器里会集中爆发。

2. **当你在同一个组件上打了 3 个以上补丁还搞不定时，应该考虑替换它**。我们在 x11vnc 上修了 MIT-SHM、VizDisplayCompositor、ncache、环境参数透传……最后发现换掉它比修好它更容易。

3. **用你已经有的工具链解决问题**。既然 Playwright 已经开着浏览器，截屏是它的一等公民 API，为什么不直接用？不要为了追求"标准方案"而引入一整套 VNC 技术栈。

4. **"网页远程桌面"不等于"必须实现 VNC/RDP 协议"**。只要用户能看到画面、能发鼠标键盘，用什么协议不重要。自定义的 JSON+PNG 帧流完全够用。

---

## 代码速查

如果你也在用 Playwright + Docker + 远程桌面，可以直接参考这个模式。

**后端截屏**（Python）：

```python
async def next_frame(self) -> bytes:
    return await page.screenshot(
        type="jpeg",
        quality=70,
        full_page=False,
    )
```

**前端渲染**（TypeScript/React）：

```typescript
const ws = new WebSocket(url);
ws.binaryType = "arraybuffer";
ws.onmessage = (event) => {
    const blob = new Blob([event.data], { type: "image/jpeg" });
    setFrameUrl(URL.createObjectURL(blob));
};
```

**后端输入回放**（Python）：

```python
async def dispatch(self, event: dict) -> None:
    if event["type"] == "click":
        await page.mouse.click(event["x"], event["y"])
    elif event["type"] == "keydown":
        await page.keyboard.press(event["key"])
```
