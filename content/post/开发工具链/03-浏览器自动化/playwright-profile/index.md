---
title: Playwright 使用实践与本地浏览器 Profile 避坑
description: "记录 Python Playwright 的常用启动方式、登录态复用，以及误用本地 Chrome 用户目录可能导致历史记录或个人数据受损的避坑经验。"
date: 2025-08-31T08:13:49+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - Python_Lib
    - Playwright
    - Browser-Automation
toc: true
draft: false
---

## 一个代价很大的坑

我之前写 Playwright 程序时，希望它直接使用电脑上安装的浏览器和已有登录状态，于是让它复用了本地 Chrome 的用户目录。结果自动化运行后，日常浏览器里的历史记录全部消失了。

这个经历里最容易混淆的是两件事：

- **使用本机安装的 Chrome 程序**：通常没问题。
- **使用日常 Chrome 的用户数据目录（Profile）**：风险很高，不应该这样做。

Playwright 默认创建隔离的 `BrowserContext`，其行为类似一个全新的无痕环境，不会读取日常 Chrome 的历史记录、Cookie 或扩展。只有在使用 `launch_persistent_context()` 并把 `user_data_dir` 指向真实 Chrome 用户目录时，自动化程序才会直接读写日常浏览数据。

## 为什么真实 Profile 可能出问题

Chrome 的用户目录中不只是 Cookie，还包含：

- `History`：浏览历史数据库
- `Cookies`：Cookie 数据库
- `Login Data`：保存的登录信息
- `Bookmarks`：书签
- `Preferences`：浏览器配置
- 扩展、缓存和站点本地存储

这些文件中有不少是 SQLite 数据库。普通 Chrome 和 Playwright 同时访问同一个 Profile，可能发生文件锁冲突、数据库损坏或配置覆盖。如果脚本还带有清理、复制、初始化目录的逻辑，就可能直接覆盖原数据。

另外，Chrome 现在也限制自动化工具访问默认用户目录。Playwright 官方明确建议：不要把日常 Chrome 的主 `User Data` 目录传给自动化程序，而应创建独立目录作为自动化 Profile。

## 错误示例：直接复用日常 Chrome Profile

macOS 上，Chrome 的用户数据通常位于：

```text
~/Library/Application Support/Google/Chrome
```

不要这样写：

```python
from pathlib import Path

from playwright.sync_api import sync_playwright


chrome_user_data_dir = (
    Path.home() / "Library/Application Support/Google/Chrome"
)

with sync_playwright() as playwright:
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=chrome_user_data_dir,
        channel="chrome",
        headless=False,
    )
    page = context.new_page()
    page.goto("https://example.com")
    context.close()
```

这里的危险点不是 `channel="chrome"`，而是 `user_data_dir` 指向了日常使用的 Chrome 数据目录。

还要注意，`chrome://version` 中显示的“个人资料路径”可能是：

```text
.../Google/Chrome/Default
```

而 Chromium 启动参数所需的 `user_data_dir` 是它的父目录：

```text
.../Google/Chrome
```

不要因为两者层级不同，就尝试把 `Default` 或它的父目录逐个传给脚本测试；它们都属于真实浏览数据。

## 正确方案一：使用系统 Chrome，但创建专用 Profile

如果需要有头浏览器、持久化 Cookie 或长期登录状态，可以为自动化单独创建目录：

```python
from pathlib import Path

from playwright.sync_api import sync_playwright


automation_profile_dir = Path.cwd() / ".playwright-profile"
automation_profile_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=automation_profile_dir,
        channel="chrome",
        headless=False,
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://example.com")
    context.close()
```

这段代码中：

- `channel="chrome"` 使用本机安装的 Google Chrome。
- `.playwright-profile` 只供自动化程序使用。
- 关闭后 Cookie、本地存储等仍会保留，下一次运行可以继续使用。
- 日常 Chrome 和自动化 Chrome 的数据完全分离。

应把专用 Profile 加入 `.gitignore`，避免将 Cookie 或凭据提交到仓库：

```gitignore
.playwright-profile/
```

## 正确方案二：只保存登录状态

如果只是运行测试，通常不需要保存整个浏览器 Profile。更轻量的做法是登录一次后导出 `storage_state`：

```python
from pathlib import Path

from playwright.sync_api import sync_playwright


auth_state_path = Path("playwright/.auth/user.json")
auth_state_path.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://example.com/login")
    # 在这里完成登录。

    context.storage_state(path=auth_state_path)
    browser.close()
```

后续运行时加载它：

```python
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context(
        storage_state="playwright/.auth/user.json",
    )
    page = context.new_page()
    page.goto("https://example.com")
    browser.close()
```

`storage_state` 主要保存 Cookie、localStorage 和 IndexedDB，比复制整个 Profile 更适合自动化测试。但这个文件仍可能包含有效登录凭据，也必须加入 `.gitignore`：

```gitignore
playwright/.auth/
```

## 普通隔离模式

不需要复用登录状态时，直接使用 Playwright 默认的隔离模式最安全：

```python
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        channel="chrome",
        headless=False,
    )
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://example.com")
    browser.close()
```

每个新建的 `BrowserContext` 都是独立的干净环境。关闭 Context 后其中的临时 Cookie 和本地存储会被丢弃，但不会触碰日常 Chrome Profile。

## 安全检查清单

在运行任何复用浏览器状态的 Playwright 程序前，至少检查以下事项：

1. `user_data_dir` 是否指向专用目录，而不是 Chrome、Edge 或 Chromium 的日常用户目录。
2. 普通浏览器和 Playwright 是否会同时打开同一个 Profile。
3. cleanup 逻辑是否可能对未校验的路径执行 `rmtree()`、`rm -rf` 或覆盖复制。
4. 是否可以用 `storage_state` 替代整个持久化 Profile。
5. 自动化 Profile 和认证状态文件是否已加入 `.gitignore`。
6. 重要浏览器数据是否有同步或系统备份。

如果程序必须清理自动化 Profile，应使用固定的专用路径，并在删除前验证目录名称。不要对来自环境变量或外部输入、尚未解析和校验的路径直接执行递归删除。

## 历史记录消失后的排查

发现历史记录不见后，先不要继续频繁启动 Chrome：

1. 完全退出普通 Chrome 和 Playwright。
2. 备份整个 Chrome 用户目录。
3. 打开 `chrome://version`，确认普通 Chrome 当前使用的是 `Default`、`Profile 1` 还是其他 Profile。
4. 检查各 Profile 下是否仍有 `History` 文件。
5. 检查 Chrome Sync、Time Machine 或其他系统备份。

macOS 上常见的历史数据库位置包括：

```text
~/Library/Application Support/Google/Chrome/Default/History
~/Library/Application Support/Google/Chrome/Profile 1/History
```

`History` 是 SQLite 数据库。如果只是切换到了空 Profile，原数据可能仍在其他目录；如果数据库已被覆盖或重新创建，则需要从同步或备份中恢复。

## 总结

使用 Playwright 时要区分“浏览器程序”和“浏览器数据”：

- 想使用本地 Chrome：设置 `channel="chrome"`。
- 想保存自动化登录状态：使用专用 `user_data_dir`。
- 只想复用测试登录态：优先使用 `storage_state`。
- 永远不要让自动化程序直接操作日常 Chrome Profile。

## 参考资料

- [Playwright：BrowserType.launch_persistent_context](https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context)
- [Playwright：Authentication](https://playwright.dev/python/docs/auth)
- [Playwright：Browser contexts](https://playwright.dev/python/docs/browser-contexts)
- [Playwright Python 使用教程](https://cuiqingcai.com/36045.html)
