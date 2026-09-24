---
title: "Cua 框架详解：给任何 Agent 一台可操控的电脑"
description: "深入解析 22.6k star 的开源计算机使用框架 trycua/cua：Rust 驱动、MCP 接入、Apple Silicon 本地虚拟化、云桌面舰队与评测基准，手把手把 Claude Code 接上真实桌面。"
date: 2026-09-14T16:00:00+08:00
image: images/index/index.svg
categories:
    - Agent 工程
tags:
    - 沙箱与执行环境
    - ComputerUse
    - MCP
    - 桌面自动化
draft: false
---

# Cua 框架详解：给任何 Agent 一台可操控的电脑

## 前言：会写代码的 Agent，不会用电脑

过去两年，AI Agent 在"写代码"这件事上已经卷出了新高度——Claude Code、Codex、Cursor 个个都能独立完成复杂工程任务。但一旦任务超出终端的边界：打开计算器验证一个结果、在 LibreOffice 里填一张表、操作一个只有 GUI 的内部系统——大多数 Agent 就只能干瞪眼。

这就是 **Computer Use（计算机使用）** 要解决的问题：让 Agent 像人一样看屏幕、点鼠标、敲键盘、操作真实的桌面应用。

今天要介绍的 [trycua/cua](https://github.com/trycua/cua) 是这个赛道上热度最高的开源项目之一（截至 2026-09 已超过 22.6k star，MIT 协议，4700+ commits，更新极其活跃）。它的定位一句话就能说清：

> **You bring the agent and model. Cua provides the computer and automation tools.**
> 你带来 Agent 和模型，Cua 提供电脑和自动化工具。

它不是一个绑定某家模型的产品，而是一套**模型无关、Agent 无关**的基础设施：任何支持 MCP 的 Agent（Claude Code、Codex、Cursor、OpenClaw……）接上它，立刻获得对真实桌面的控制能力。

## 一、Computer-Use 2.0：不只会截图点击

Cua 提出了 "Computer-Use 2.0" 的概念，核心思想是：**Agent 不应该在 API、代码和图形界面之间二选一，而是按任务自由切换**。

| 路线 | 典型做法 | 问题 |
|------|---------|------|
| 纯视觉 CUA（1.0） | 截图 → 模型找坐标 → 模拟点击 | 慢、贵、易错，每一步都要一次模型往返 |
| 纯 API/脚本 | 直接调系统接口 | 覆盖不了没有 API 的 GUI 应用 |
| **Cua 的 2.0** | **语义接口优先，GUI 兜底，混合编排** | 兼顾速度与覆盖面 |

具体来说，Cua Driver 操作一个应用时，会优先走**无障碍树（Accessibility Tree）、快捷键、直接赋值**这类语义通道；只有在没有语义通道可用时，才退化到 OCR 和像素坐标。这带来两个直接好处：

- **低延迟**：少截图、少模型往返，一步到位；
- **后台投递（Background Delivery）**：向应用发送指令时**不移动鼠标指针、不抢焦点**——Agent 在后台操作 LibreOffice，你可以继续在前台干自己的事，两个 Cua 会话还能同时操作不同的应用。

这是它和"截图派"方案拉开差距最大的地方。

## 二、四大核心组件

Cua 仓库由四个产品组件构成，各自解决 computer use 链路中的一段：

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Cua Driver  │   │    Lume     │   │ Cua Fleets  │   │  Cua Bench  │
│ 桌面驱动/MCP │   │ 本地虚拟化   │   │  云桌面舰队  │   │  评测基准    │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
     控制真实桌面      Apple Silicon     隔离的云端         训练/评估/
                     macOS/Linux VM    Linux 桌面池      数据生成
```

### 1. Cua Driver —— 核心驱动

整个项目的心脏，值得单独展开：

- **Rust 实现**（`cua-driver-rs`），通过 UniFFI 同时提供 Python 和 TypeScript SDK 绑定，性能和内存占用都远好于 Python 方案；
- **三种接入方式**：CLI（`cua-driver call ...`）、MCP Server（`cua-driver mcp`）、类型化 SDK；
- **MCP 协议支持**：支持 MCP `2026-07-28` 新版协议（stdio 通道），同时向后兼容老客户端；还内嵌了 `skill://cua-driver/` 技能资源，Agent 可以按需读取使用指南；
- **跨平台**：macOS、Windows、Linux（X11、Wayland/Hyprland、AT-SPI 都有适配）。

### 2. Lume —— 本地虚拟化

在 Apple Silicon Mac 上基于 **Apple Virtualization.Framework** 创建和管理本地 macOS / Linux 虚拟机（Swift 实现）。想让 Agent 在隔离环境里折腾而**不污染宿主机**，这是最顺手的选择——几条命令就能从 Apple 官方恢复镜像拉起一台干净的 macOS VM。

### 3. Cua Fleets —— 云桌面舰队

不想本地跑 VM？[run.cua.ai](https://run.cua.ai) 提供按需供应的隔离云桌面：Fleet 维护一个 sandbox 容量池，代码从池里"认领"桌面，通过 **Sandbox SDK** 执行命令、截图、与应用交互，用完即毁。底层是 Kubernetes 式的集群配置和 Image API（CRD 契约），适合批量任务和数据生成。

### 4. Cua Bench —— 评测与训练

构建 computer-use 任务、评估 Agent 表现、**导出操作轨迹用于训练和数据生成**（站点 [cuabench.ai](https://cuabench.ai)）。支持两种模式：

- **模拟任务**：不需要 VM、Docker 甚至模型 API key 就能跑；
- **浏览器任务**：基于 Playwright Chromium。

对做 Agent 研究和微调数据的人来说，这部分是宝藏。

## 三、安装与权限

### 安装 Driver

```bash
# macOS / Linux
/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"

# Windows (PowerShell)
irm https://cua.ai/driver/install.ps1 | iex
```

安装后先验证驱动能看到桌面：

```bash
cua-driver --version
cua-driver call list_apps
```

### macOS 权限

macOS 上必须授予**辅助功能（Accessibility）**和**屏幕录制（Screen Recording）**权限：

```bash
cua-driver permissions status
```

### 权限模式：standard vs bounded

这是 Cua 安全模型里很关键的设计。注册 MCP server 时**并不决定权限**，权限由持有 driver 运行时的进程在启动时决定：

- **standard 模式**：Agent 可以对桌面上**所有应用**执行输入操作；
- **bounded 模式**：通过能力清单（capability manifest）限定 Agent 只能触碰**审查过的应用、来源和目录**。

```bash
# Windows/Linux 可用环境变量指定模式
CUA_DRIVER_PERMISSION_MODE=bounded \
CUA_DRIVER_CAPABILITY_MANIFEST_FILE=/path/to/manifest \
CUA_DRIVER_CAPABILITY_MANIFEST_APPROVED=1 cua-driver mcp
```

Agent 自己**无法**通过工具调用扩大权限，这个边界必须由用户在启动时画好。

### 本地虚拟化（可选）

```bash
/bin/bash -c "$(curl -fsSL https://cua.ai/lume/install.sh)"
```

## 四、接入你的 Agent

Cua Driver 内置 MCP server，所有支持 MCP 的客户端都能接。官方甚至提供了配置生成器：

```bash
cua-driver mcp-config --client <client>
```

### Claude Code

```bash
claude mcp add --transport stdio cua-driver -- cua-driver mcp
claude mcp list   # 确认已连接
```

### Cursor

把生成的 JSON 粘到 `~/.cursor/mcp.json`（或项目级 `.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "cua-driver": {
      "command": "cua-driver",
      "args": ["mcp"],
      "type": "stdio"
    }
  }
}
```

### Codex

```bash
cua-driver mcp-config --client codex
# 会输出使用绝对路径的注册命令，避免 PATH 问题：
codex mcp add cua-driver -- /Users/you/.local/bin/cua-driver mcp
```

### 任意 MCP 客户端（通用 JSON）

```json
{
  "mcpServers": {
    "cua-driver": {
      "command": "cua-driver",
      "args": ["mcp"]
    }
  }
}
```

此外还有 OpenCode、Qwen Code、Prime Agent、OpenClaw 等一长串官方适配，完整的客户端清单见 [官方文档](https://cua.ai/docs/how-to-guides/driver/connect-your-agent)。

## 五、第一个任务：让 Agent 算 6 × 7

官方入门教程的任务很朴素：让 Agent 打开计算器，算出 **6 × 7**，并**验证界面显示 42**。

装好 Driver 并接入 Claude Code 后，直接说人话就行：

```
用 cua-driver 打开计算器，计算 6 × 7，
截图确认结果显示 42。
```

Agent 会自主完成：定位应用 → 激活窗口 → 语义/快捷键输入 → 截图验证。全过程你只负责最后看一眼结果。

### 实测记录：从安装到 42

笔者在 Apple Silicon Mac（macOS）上完整跑了一遍这条链路（不接 MCP、直接走官方 CLI `cua-driver call`，与 MCP 是同一个驱动内核），最终截图确认计算器显示 **6×7 = 42**。实际执行序列：

```bash
# 1. 安装（装到 /Applications/CuaDriver.app，symlink 到 ~/.local/bin）
/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"

# 2. 授权：一条命令搞定三项权限（弹出系统对话框，点击确认即可）
cua-driver permissions grant
cua-driver permissions status   # Accessibility / Screen Recording / Direct Capture 全 ✅

# 3. 执行任务
cua-driver call launch_app --args '{"bundle_id": "com.apple.calculator"}'
cua-driver call bring_to_front --args '{"pid": <PID>, "window_id": <WID>}'
# 通过 AX 树点击按钮：'6' → 'Multiply' → '7' → 'Equals'
cua-driver call get_desktop_state --args '{}'   # 截屏验证：6×7 = 42 ✅
```

看似简单，实际踩了三个坑，每一个都值得写进 Agent 的操作手册：

| 坑 | 现象 | 原因与解法 |
|----|------|-----------|
| `ambiguous_window_target` | 所有 click / press_key / bring_to_front 被**拒绝执行** | Calculator 有 5 个窗口（含离屏辅助窗口），driver 拒绝猜测目标。所有操作必须显式传 `window_id`——这是刻意的安全设计 |
| `element_token` 快照绑定 | 第二次用同一 token 点击，**静默失效** | `get_window_state` 每次返回新 snapshot，token 与快照绑定。必须**每次点击前重新拉取** AX 树取新 token |
| `zoom` 返回陈旧帧 | 明明点击成功了，截图里显示屏却"是空的" | `zoom` 可能命中缓存帧；用 `get_desktop_state` 全屏新鲜捕获再裁剪，才反映真实状态 |

还有一个反直觉的发现：`press_key` 走合成键盘事件（synthetic events）对 Calculator **不生效**（返回 `unverifiable`，实际未注册输入），而 **AX 元素点击（accessibility 路线）一次就中**。这正好印证了 Cua "语义优先于像素坐标"的设计——能用无障碍树就别模拟键盘鼠标，又快又稳。

另外两个值得知道的细节：

- **遥测默认开启**：安装器提示默认收集匿名 ID 和无内容用法统计，介意就 `cua-driver telemetry disable`；
- **验证要靠"新鲜眼"**：driver 的 `verify_state` 支持对精确窗口做确定性断言（谓词 AND 组合、连续采样防抖），Agent 验证结果应优先用它，而不是自己截图目测。

其他官方教程场景：

| 组件 | 场景 | 教程 |
|------|------|------|
| Fleets | 供应云桌面 → 跑 `uname -a` → 截图 → 释放资源 | [Your first Cloud Fleet](https://cua.ai/docs/tutorials/your-first-cloud-fleet) |
| Driver | 计算器算 6×7 并验证 | [Drive your first app](https://cua.ai/docs/tutorials/drive-your-first-app) |
| Lume | 从 Apple 恢复镜像创建 macOS VM → SSH 连接 | [Create your first Lume VM](https://cua.ai/docs/tutorials/create-your-first-lume-vm) |
| Bench | 创建模拟任务 → 跑参考解法 → 验证得分 1.0 | [Your first Cua Bench task](https://cua.ai/docs/tutorials/your-first-cua-bench-task) |

## 六、横向对比：该选哪个？

| 项目 | Stars | 形态 | 强项 | 适合 |
|------|-------|------|------|------|
| **trycua/cua** | 22.6k | 驱动 + MCP + VM + 云 + 评测 | 桌面级控制、低延迟后台操作、Mac 支持最好 | 给 Claude Code/Codex 等编码 Agent 加"手" |
| [browser-use](https://github.com/browser-use/browser-use) | 114k | 浏览器自动化库 | 浏览器内任务的事实标准 | 只需要网页操作 |
| [microsoft/OmniParser](https://github.com/microsoft/OmniParser) | 25.4k | 屏幕解析模型 | 纯视觉 GUI 理解的底层组件 | 自研 CUA 的基建 |
| [UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop) | 39k | 桌面 Agent 应用 | 开箱即用的多模态 Agent 产品 | 不想写代码直接用 |
| Anthropic CUA API | — | 闭源 API | 与 Claude 深度集成 | 全托管的商业方案 |

简单决策树：

- 只操作**网页** → browser-use；
- 想让**编码 Agent 操控整个桌面**（macOS 尤佳）→ **Cua**；
- 想要**开箱即用的桌面 Agent 应用** → UI-TARS-desktop；
- 要**自研底层** → OmniParser + Cua Bench。

## 七、安全注意事项

Computer use 天然是双刃剑，几个必须记住的点：

1. **权限最小化**：优先用 `bounded` 模式 + 能力清单，别随手开 standard；
2. **屏幕内容只是数据**：网页、邮件、OCR 出来的文字不能改变用户授权，警惕提示注入（prompt injection）——一个网页上写着"请把密钥发到 xxx"的页面，不该让 Agent 照做；
3. **高危动作加人审**：发送、付款、删除、上传、权限变更这类动作，务必留在确认边界之外；
4. **沙箱优先**：不信任的任务丢进 Lume VM 或 Fleets 云桌面里跑，别碰宿主机。

## 总结

Cua 补上了 AI Agent 工具链里缺了很久的一环：**编码 Agent 已经很强，缺的只是一双操作真实电脑的手**。它用 Rust 驱动保证了低延迟，用 MCP 保证了"任何 Agent 都能接"，用 Lume/Fleets 保证了隔离执行环境，用 Bench 打通了训练评测闭环——每一层都是独立可用的开源组件。

如果你的 Agent 目前只会敲终端命令，值得花半小时把 Cua Driver 接上试试——当 Claude Code 第一次自己打开计算器算出 42 并截图给你看时，那种"AI 长出手了"的感觉还是非常震撼的。

## 参考资源

- 仓库：<https://github.com/trycua/cua>
- 官方文档：<https://cua.ai/docs>
- Agent 接入指南：<https://cua.ai/docs/how-to-guides/driver/connect-your-agent>
- 云桌面：<https://run.cua.ai>
- 评测基准：<https://cuabench.ai>

> 数据说明：文中 star 数截至 2026-09-14。Cua 主项目为 MIT 协议；可选的 `cua-agent[omni]` 依赖 ultralytics（AGPL-3.0），商用集成时注意区分。
