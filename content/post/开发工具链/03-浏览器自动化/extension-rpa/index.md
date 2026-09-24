---
title: 扩展式 RPA：从 Chrome 扩展原理到 Playwright 实战方案
description: "拆解 Chrome 扩展型 RPA 直接复用用户登录态的核心原理，并整理三种用 Playwright 复用用户浏览器的实战方案、坑点与适用场景。"
date: 2026-07-27T10:00:00+08:00
slug: 扩展式RPA：从Chrome扩展接管到Playwright实战
image: images/index/index.svg
categories:
    - 开发工具链
tags:
    - 浏览器自动化
    - dev_tools
    - RPA
    - Playwright
    - Browser-Automation
toc: true
draft: false
---

## 一个观察

之前在 [[../L../Library/Python_Lib/playwright/index.md]] 里写过 Playwright 自己起隔离浏览器的常规打法。但在看到一些 RPA 工具的形态后，问题就变成另一个：

> 为什么有些 RPA 工具是装成 Chrome 扩展，一打开就能直接「操控」用户已经登录好的页面？

答案并不复杂：这两种工具在底层就是两套完全不同的思路。

## 核心原理：谁拥有那个浏览器

普通 Playwright(或者类似 Puppeteer、Selenium)启动的是**全新的、独立的浏览器实例**，和你日常用的 Chrome 没有任何关系。Cookies 是空的，需要重新登录或注入 `storage_state`。

而 Chrome 扩展型 RPA 长这样：

```text
┌──────────────────────────────────────────┐
│  你的 Chrome 浏览器（同进程）              │
│                                          │
│  ┌────────────┐  ┌────────────────────┐  │
│  │ Tab: 微博   │  │ Extension: RPA 工具 │  │
│  │ (已登录)    │  │ 注入 content script │  │
│  └────────────┘  └────────────────────┘  │
│        ↑                │                │
│        └────────────────┘                │
│         共享同一个 cookie 存储              │
│         共享同一个 origin 权限             │
└──────────────────────────────────────────┘
```

扩展里跑的内容脚本 (`content script`) 语法上是独立脚本，但它**直接被注入到登录页面的 DOM 里**，运行在该页面的 JS context 中。所以当它调用 `fetch('/api/user/info')` 时，浏览器自动带上微博的 cookies，服务器认为这就是用户本人。

整件事可以浓缩成一句话：

> 扩展是装在你浏览器里的代码，你在浏览器里登录了什么，它就拥有什么。

这也是为什么做需要登录态的 RPA 任务，扩展方案往往比 Playwright 简单十倍 —— 因为它根本不需要解决「登录」这个问题。

### 几块关键拼图

扩展形式看起来神秘，其实就是下面这几块常规 MV3 API 拼起来的：

`manifest.json` 声明权限：

```json
{
  "permissions": [
    "cookies",
    "storage",
    "tabs",
    "scripting",
    "activeTab"
  ],
  "host_permissions": [
    "*://*.weibo.com/*",
    "*://*.example.com/*"
  ]
}
```

`content.js` 注入目标页面，所有 `fetch` 自动带登录态：

```javascript
async function autoPost(content) {
  document.querySelector('#editor').value = content;
  document.querySelector('#submit').click();
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.cmd === 'post') {
    autoPost(msg.text);
    sendResponse({ ok: true });
  }
});
```

后台脚本 `background.js` 里直接读 cookie：

```javascript
chrome.cookies.getAll({ domain: '.weibo.com' }, (cookies) => {
  console.log(cookies); // 直接拿到用户的所有登录态
});
```

把上面三块加一个 `popup.html`，就是最简版「扩展式 RPA」。

### 两种方案对比

| 维度 | Playwright / 独立 RPA | 扩展式 RPA |
|------|----------------------|-----------|
| 启动方式 | 独立进程，自己的浏览器 | 跑在用户已有的 Chrome |
| 登录态 | 无，需要自登录或注入 `storage_state` | **天然继承**用户浏览器的登录态 |
| 反爬检测 | 高（指纹、IP、行为模式） | 低（就是用户本人） |
| 用户授权 | 无感（代码里随便用） | 需要用户主动装扩展 |
| 部署难度 | 简单，纯代码 | 需要打包扩展、上架商店或 crx 安装 |
| 资源占用 | 完整浏览器进程 | 几乎为零 |
| 适用场景 | 批量任务、服务器端 | 辅助个人用户、低频任务 |

### 反爬角度的思考

扩展式 RPA 看起来「开挂」，但也不是万能：

1. **指纹检测**：`window.chrome.runtime` 等扩展特征可以被检测
2. **行为检测**：点击速度、操作序列如果太机械，仍能被识别
3. **数据回流**：云端 SaaS 形态的 RPA 在网络层会被分析
4. **扩展权限**：Chrome 在安装时展示权限，敏感权限可能让用户警觉
5. **Manifest V3 限制**：MV3 收紧了远程代码执行、跨域请求，扩展型 RPA 的能力被削弱

### 商业产品参考

- **UI.Vision (Kantu)**：经典老牌，扩展形式，直接读用户登录态
- **Browserflow**：Chrome 商店里很常见
- **Axiom.ai**：扩展 + 云端
- **影刀 / 八爪鱼**：部分功能走扩展模式，处理需要登录的网站
- **Automa**（开源）：GitHub 上有源码，可以学到完整的实现

---

## 用 Playwright 模拟扩展式 RPA

虽然「真扩展」的形态在 Playwright 这边不好复刻（Playwright 是独立进程，无法直接读取用户 Chrome 的 cookies），但有一种折中方案：让 Playwright **复用用户已登录的浏览器**。技术上叫 **Persistent Context**。

核心 API 是 `launch_persistent_context`：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 关键：指向真实 Chrome 的用户数据目录
    # macOS : ~/Library/Application Support/Google/Chrome
    # Windows: %LOCALAPPDATA%\Google\Chrome\User Data
    context = p.chromium.launch_persistent_context(
        user_data_dir='/Users/zata/Library/Application Support/Google/Chrome',
        channel='chrome',          # 强制用系统 Chrome，不是 chromium
        headless=False,            # 必须可视化（见下面）
        no_viewport=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-first-run',
        ],
    )
    page = context.new_page()
    page.goto('https://weibo.com')
    # 此时你已经是登录状态了，直接用
    page.locator('.follow-btn').first.click()
```

### 但这条路的坑很大

和同仓库那篇 [[../L../Library/Python_Lib/playwright/index.md]] 的警告一致 —— 复用真实 Chrome 的 Profile 风险极高：

1. **必须先完全关闭 Chrome**：用户数据目录是文件锁定的，Chrome 在开的时候 Playwright 启动会直接报 `Failed to create a ProcessSingleton for your profile`。
2. **`headless=False` 是硬需求**：不是「看得到」这么简单的诉求，而是 headless 模式下被检测概率会显著上升，自动化特征也更明显。
3. **User Data 目录要用整个 `User Data`，而不是 `Default`**。
4. **不要做 `rm -rf` 这种清理动作**：容易连带覆盖或损坏历史、书签。

写个辅助函数降低出错的可能：

```python
import subprocess
import time

def kill_chrome():
    """杀进程,确保数据目录不被 Chrome 自己锁住"""
    subprocess.run(['pkill', '-9', 'Google Chrome'], check=False)
    time.sleep(2)
```

### 实际可运行的完整脚本

```python
# rpa.py
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
USER_DATA = Path.home() / 'Library/Application Support/Google/Chrome'


def ensure_chrome_closed() -> None:
    subprocess.run(['pkill', '-9', '-f', 'Google Chrome'], check=False)
    time.sleep(2)


def run() -> None:
    ensure_chrome_closed()

    with sync_playwright() as p:
        # Playwright 启动一个临时 Chrome 进程,加载你的用户数据
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA),
            executable_path=CHROME_PATH,
            headless=False,
            no_viewport=True,
            args=['--disable-blink-features=AutomationControlled'],
            ignore_default_args=['--enable-automation'],
        )

        try:
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://weibo.com')

            # 验证:这里应该能直接看到登录态
            assert '登录' not in page.title(), '用户态异常,可能 Chrome 未正常启动'

            # 开始自动化...
            page.goto('https://weibo.com/u/1234567890')
            page.locator('text=关注').first.click()
            print('✅ 关注成功')

        finally:
            browser.close()
            time.sleep(1)


if __name__ == '__main__':
    run()
```

### 进阶：CDP 远程连接

`launch_persistent_context` 有一个尴尬的体验：用户在自己用 Chrome，你想跑 RPA，必须先杀 Chrome 再启动一次。更优雅的方案是 **Chrome DevTools Protocol（CDP）远程连接**：

```bash
# 第一步：用户在终端手动启动 Chrome（带远程调试）
google-chrome --remote-debugging-port=9222
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 第二步：Playwright 接管这个 Chrome,而不是新启
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    context = browser.contexts[0]   # 复用用户的 context
    page = context.pages[0]         # 接管用户当前的 tab
    page.goto('https://weibo.com')
```

CDP 方案的好处：

- 不需要杀 Chrome
- 用户当前打开的 tab 可以直接被我们接管
- 跑完可以「无缝」还给用户

### Playwright + Chrome Extension

如果目标是**让用户装一个扩展，由扩展来驱动云端 Playwright**，逻辑反过来：

```text
┌─────────────────────────────────────────┐
│  用户 Chrome                              │
│  ├── 你的 Extension (MV3)                 │
│  │    └── WebSocket 客户端                 │
│  └── 普通网页                              │
│       └── 被扩展的 content script 操控     │
└────────────┬────────────────────────────┘
             │ ws://localhost:8765
             ▼
┌─────────────────────────────────────────┐
│  你的 Python 服务                         │
│  ├── WebSocket Server                    │
│  └── Playwright(可选,云端兜底)             │
└─────────────────────────────────────────┘
```

这种架构适合做 **SaaS 化的 RPA**：扩展做「采集 + 可视化」，云端 Playwright 做「批量执行」。

---

## 方案选型表

| 场景 | 推荐方案 |
|------|---------|
| 个人脚本，偶尔跑一下 | `launch_persistent_context` + 杀 Chrome |
| 个人脚本，经常跑 | CDP 远程连接 + 一个一键启动 Chrome 的 `.command` 文件 |
| 工具化，要给同事用 | CDP 方案 + 配启动器 |
| 做产品，要分发 | 写 Chrome 扩展（完全独立，无需 Playwright） |

前三种方案都没跳出 Playwright 的能力范围，基本能覆盖 90% 的需求。最后一种是真正的「扩展式 RPA」，但投入就大很多了 —— 它本身就是一个独立的产品形态，从 manifest、签名、商店审核到 MV3 限制都是另一套工程。

如果是从零开始想把 RPA 能力给到个人用户，**先从 CDP 方案做起**，把脚本跑通、把页面录制做成、把回放做成；等到扩展的能力真的有必要了，再考虑写 MV3 分发。

## 参考资料

- [Playwright: `launch_persistent_context`](https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context)
- [Playwright: Connect over CDP](https://playwright.dev/python/docs/other-ports#connect-over-cdp)
- [Chrome Extensions: Manifest V3 Migration](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [Chrome Extensions: Cookies API](https://developer.chrome.com/docs/extensions/reference/api/cookies)
- [rrweb / rrweb-player](https://github.com/rrweb-io/rrweb)（会话录制的开源参考实现）
- [Automa - Chrome 扩展式 RPA 开源实现](https://www.automa.site/)
