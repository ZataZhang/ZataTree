---
title: crawler-tutorial
description: ""
date: 2025-11-19T11:28:14+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - crawler
---





## 第一部分：主流爬虫框架/库对照

目前市面上最主流的方案大多基于 Python，同时也包含 Go 语言的高性能方案。

1. Scrapy (Python) - 工业级霸主
Scrapy 是 Python 生态中最流行、功能最强大的异步爬虫框架。

- **核心特点**：基于 Twisted 异步网络框架，自带下载器、中间件、调度器、管道等全套组件。
- **优点**：并发能力极强（速度快），生态完善（有 Scrapy-Redis 分布式插件）。
- **缺点**：学习曲线陡峭，不支持 JS 渲染（需配合 Splash/Selenium）。
- **适用场景**：**海量数据抓取**、全站爬虫、分布式爬虫。

2. Requests + BeautifulSoup (Python) - 入门首选
严格来说是两个库的组合，是最常见的入门方案。

- **核心特点**：同步阻塞模式，代码极其简单。
- **优点**：上手极快，灵活，适合写一次性脚本。
- **缺点**：效率低（同步），无断点续传、去重等机制。
- **适用场景**：**学习演示**、小规模爬取、API 接口抓取。

3. Playwright / Selenium (Python/Node.js) - 浏览器自动化
本质是自动化测试工具，通过控制真实浏览器来爬取数据。

- **核心特点**：所见即所得，能处理所有 JavaScript 动态渲染。
- **优点**：完美模拟用户行为，能搞定几乎所有动态网页。
- **缺点**：**慢**（需加载浏览器内核），资源消耗大。*注：推荐使用 Playwright 替代 Selenium。*
- **适用场景**：**高度动态网站**（SPA）、模拟登录、无需高并发的复杂任务。

4. Colly (Golang) - 性能怪兽
Go 语言生态中最强的爬虫框架。

- **核心特点**：编译型语言，单机并发能力极强。
- **优点**：运行速度通常快于 Python，部署只需一个二进制文件。
- **缺点**：数据清洗生态不如 Python 丰富，有语言门槛。
- **适用场景**：**追求极致性能**和高吞吐量的企业级爬虫。

📊 综合对照表

| 特性 | Scrapy | Requests+BS4 | Playwright | Colly |
| :--- | :--- | :--- | :--- | :--- |
| **语言** | Python | Python | Python/Node | Go |
| **类型** | 异步框架 | 同步库 | 浏览器自动化 | 异步框架 |
| **速度** | 🚀 极快 | 🐢 慢 | 🐌 极慢 | 🚀🚀 超快 |
| **JS支持**| ❌ (需插件) | ❌ | ✅ (完美) | ❌ |
| **上手度**| 困难 | 极易 | 中等 | 中等 |

---

## 第二部分：高难度场景（验证码 + 强反爬）解决方案

当面对 **验证码（CAPTCHA）** 和 **强反爬机制**（如 Cloudflare 5秒盾、TLS 指纹识别、滑块验证）时，传统的 Scrapy 和 Requests 往往会失效。

此时，“拟人化”程度比“速度”更重要。以下是梯队推荐：

👑 第一梯队：抗检测与过盾之王

**DrissionPage (Python)**
目前 Python 爬虫圈的“版本之子”，专为对抗 Selenium 被识别而生。
- **核心原理**：结合了 `Requests` 和 `Chromium CDP` 协议。不使用 WebDriver（避免被检测），直接控制浏览器。
- **杀手锏**：
    - **无视 WebDriver 检测**：天然过很多检测。
    - **模式切换**：登录/过验证码时用浏览器模式，抓数据时切换回发包模式，兼顾速度与通过率。
- **适用**：**Cloudflare 盾**、极难爬取的网站。

**Playwright + `playwright-stealth`**
- **核心原理**：新一代自动化工具配合隐藏特征插件。
- **杀手锏**：支持复杂的鼠标轨迹模拟（抗滑块），`stealth` 插件可掩盖自动化特征。

🛡️ 第二梯队：底层协议反爬（TLS 指纹）

**curl_cffi (Python)**
- **解决痛点**：很多网站通过检测 **TLS/JA3 指纹** 来识别 Python 脚本。即使你伪造了 User-Agent，用 Requests 依然会被封。
- **功能**：模拟 Chrome/Firefox 的底层 SSL 握手特征，骗过服务器。
- **适用**：**非 JS 渲染**但防火墙极高（Akamai, Cloudflare）的站点。

---

第三部分：验证码具体攻克策略

框架是枪，解决验证码需要“外挂”。

1.  **简单数字/字母验证码**
    *   **方案**：**ddddocr** (Python库)
    *   **特点**：免费、离线、开箱即用，识别率优秀。

2.  **滑块 / 缺口 / 点选验证码**
    *   **方案**：**DrissionPage / Playwright + YOLO (目标检测)**
    *   **逻辑**：截图 -> AI 识别缺口坐标 -> 生成**模拟人类抖动**的鼠标轨迹进行拖拽。

3.  **地狱级验证码 (ReCaptcha / hCaptcha)**
    *   **方案**：**打码平台 (YesCaptcha / 2Captcha)**
    *   **逻辑**：不要自己破解。调用平台 API，支付少量费用获取 Token，这是工业界最稳方案。

---

💡 最终选型建议

1.  **初学者/简单任务** 👉 `Requests` + `BeautifulSoup`
2.  **海量数据/通用爬取** 👉 `Scrapy`
3.  **网站有 Cloudflare 盾 / 极其变态** 👉 **`DrissionPage`** (强烈推荐)
4.  **需要处理滑块/复杂交互** 👉 `Playwright` + `YOLO`
5.  **只被 TLS 指纹拦截** 👉 `curl_cffi`





## 告别手动写爬虫代码-从F12到Python

手动编写 `requests` 代码经常因为标点符号、Header 格式错误、TLS 指纹识别或 Cookie 过期而导致报错，这是非常正常的情况。

针对**“把 cURL/F12 快速转成可运行代码”**这个需求，这里整理了四个“神器”帮你一键解决。按推荐程度排序如下：

---

1. CurlConverter (Web版/命令行)
> **定位：** 最推荐，零门槛，全球开发者首选。

专门解决手动抄写 Header 和 Cookie 的痛点。它能把 cURL 命令完美“翻译”成 Python requests 代码（支持数十种语言）。

* **网址：** [curlconverter.com](https://curlconverter.com)
* **优点：** 自动处理 Header 格式、JSON 转义、Cookie 字典化，完全避免由于手误导致的 Bug。

使用步骤：
1.  在浏览器 F12 开发者工具的网络面板中，右键点击请求 -> **Copy as cURL**。
2.  打开网站，直接粘贴到左边的文本框里。
3.  右边会自动生成 Python 代码，直接复制到 IDE 运行即可。

---

 2. Postman (调试神器)
> **定位：** 先验证请求有效性，再生成代码。

如果你生成的代码跑不通，很有可能是请求本身的问题（如 Cookie 已过期）。Postman 允许你在可视化界面先测通接口。

使用步骤：
1.  打开 Postman，点击左上角的 **Import** -> **Raw Text**。
2.  粘贴 cURL 命令并点击 Import，Postman 会自动填充参数。
3.  点击 **Send** 测试：
    * 如果报错，说明 Cookie 或参数失效，需重新抓包。
    * 如果成功，点击右侧栏的 **</>** 图标 (Code snippet)。
4.  选择 **Python - Requests**，复制生成的代码。

---

3. 进阶大杀器：curl_cffi
> **定位：** 解决“代码逻辑没错，但被服务器拦截 (403 Forbidden)”的问题。

**重点注意：** 如果 CurlConverter 生成的代码一模一样却报错（如 403 或连接重置），大概率是因为 **TLS 指纹识别**。百度、Cloudflare 等大厂会识别 Python `requests` 库的指纹并拦截。

**解决方案：** 使用 `curl_cffi` 库模拟真实浏览器指纹。

安装：
```bash
pip install curl_cffi
````

代码示例：

用法几乎与 requests 一致，只需增加 `impersonate` 参数：

```python
from curl_cffi import requests

# 把生成的 requests 代码拿过来，改成用 curl_cffi 调用
response = requests.post(
    "YOUR_URL_HERE", 
    headers=headers, 
    data=data, 
    impersonate="chrome110"  # 关键：伪装成 Chrome 浏览器
)
```

-----

4\. 终极懒人方案：Playwright Codegen

> **定位：** 录制即代码，解决极其复杂的反爬虫。

如果你不想分析接口参数，也不想处理反爬，可以直接使用浏览器自动化录制。虽然运行效率比 requests 低，但因其是真实浏览器操作，极难被屏蔽。

使用步骤：

在终端输入以下命令，浏览器会自动弹出：

```bash
playwright codegen fanyi.baidu.com
```

你在这个浏览器里的每一次点击和输入，终端窗口都会实时生成对应的 Python 代码。

-----

总结与建议

1.  **第一步：** 先用 **CurlConverter** 转换代码，尝试运行。
2.  **第二步：** 如果代码报 `403/404` 或 `Connection Error`，说明遭遇反爬，请放弃标准 requests，直接改用 **curl\_cffi**。
3.  **调试：** 如果还是无法解决，请检查 HTTP 状态码或 Python 抛出的具体 Exception。

<!-- end list -->

```

下一步建议
如果您在使用 `curl_cffi` 后仍然遇到报错，或者需要处理更复杂的动态加载页面（JavaScript 渲染），您希望我为您生成一段 **Playwright 的基础启动代码** 吗？