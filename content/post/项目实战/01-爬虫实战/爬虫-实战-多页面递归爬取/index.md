---
title: 爬虫-实战-多页面递归爬取
description: ""
date: 2025-03-20T10:20:00+08:00
image: images/index/index.png
categories:
    - 项目实战
tags:
    - 爬虫实战
    - 爬虫
---



```python
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time

# 配置爬虫参数
START_URL = "https://arxiv.org/list/cs.AI/new"  # 替换为你想爬取的起始URL
MAX_DEPTH = 1  # 最大爬取深度
OUTPUT_FILE = "crawled_data.json"  # 输出文件名

# 用于存储已访问的URL，避免重复
visited_urls = set()

# 用于存储爬取结果
crawled_data = []

def crawl(url, depth=0):
    # 检查深度限制和是否已访问
    if depth > MAX_DEPTH or url in visited_urls:
        return
    
    print(f"正在爬取: {url} (深度: {depth})")
    
    try:
        # 发送HTTP请求
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # 检查请求是否成功
        
        # 标记为已访问
        visited_urls.add(url)
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 提取当前页面的标题作为主要内容（可以根据需要修改）
        page_title = soup.title.string if soup.title else "无标题"

        # 提取页面中的内容
        content = soup.get_text()
        
        # 存储当前页面的URL和内容
        crawled_data.append({
            "url": url,
            "title": page_title,
            "depth": depth,
            "content": content
        })
        
        # 提取页面中的所有链接
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            link_text = link.text.strip() or "无文本"
            
            # 将相对URL转换为绝对URL
            absolute_url = urljoin(url, href)
            
            # 简单过滤，只爬取http或https链接
            if absolute_url.startswith(("http://", "https://")):
                # 递归爬取新链接
                crawl(absolute_url, depth + 1)
                
        # 避免过于频繁请求，礼貌爬取
        time.sleep(1)
        
    except requests.RequestException as e:
        print(f"爬取 {url} 失败: {e}")
        
def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

def main():
    print("开始爬取...")
    crawl(START_URL)
    save_to_file(crawled_data, OUTPUT_FILE)
    print(f"爬取完成，共爬取 {len(crawled_data)} 个页面")

if __name__ == "__main__":
    main()


```



---

### 1. 代码概述
这个爬虫使用 `requests` 获取网页内容，`BeautifulSoup` 解析 HTML，然后递归爬取页面中的链接，最终将结果保存为 JSON 文件。主要功能包括：
- 从指定起始 URL 开始爬取。
- 限制爬取深度，避免无限递归。
- 提取页面标题和文本内容。
- 保存爬取结果到本地文件。

---

### 2. 导入库
```python
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time
```
- `requests`：用于发送 HTTP 请求获取网页内容。
- `BeautifulSoup`（来自 `bs4`）：解析 HTML 内容，提取所需数据。
- `json`：将爬取结果保存为 JSON 格式。
- `urljoin`（来自 `urllib.parse`）：将相对 URL 转换为绝对 URL。
- `time`：用于添加延迟，避免过于频繁请求服务器。

---

### 3. 配置爬虫参数
```python
START_URL = "https://arxiv.org/list/cs.AI/new"  # 替换为你想爬取的起始URL
MAX_DEPTH = 1  # 最大爬取深度
OUTPUT_FILE = "crawled_data.json"  # 输出文件名
```
- `START_URL`：爬虫的起始页面，这里是 arXiv 的 AI 分类新论文页面。
- `MAX_DEPTH`：限制递归爬取的深度，防止爬虫无限扩展（这里设为 1，只爬取起始页面和其直接链接）。
- `OUTPUT_FILE`：结果保存的文件名。

---

### 4. 全局变量
```python
visited_urls = set()
crawled_data = []
```
- `visited_urls`：一个集合（`set`），记录已访问的 URL，避免重复爬取。
- `crawled_data`：一个列表，存储所有爬取到的页面数据。

---

### 5. 主爬取函数 `crawl`
```python
def crawl(url, depth=0):
```
- `url`：要爬取的网页地址。
- `depth`：当前爬取的深度，默认从 0 开始。

#### 5.1 检查条件
```python
if depth > MAX_DEPTH or url in visited_urls:
    return
```
- 如果当前深度超过 `MAX_DEPTH` 或 URL 已访问过，则停止爬取并返回。

#### 5.2 发送请求
```python
print(f"正在爬取: {url} (深度: {depth})")
try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()  # 检查请求是否成功
```
- 打印当前爬取的 URL 和深度。
- 使用 `requests.get` 发送 HTTP GET 请求：
  - `headers`：伪装成浏览器，避免被服务器拒绝。
  - `timeout=20`：设置 20 秒超时，防止请求挂起。
- `raise_for_status()`：如果请求失败（比如 404 或 500），抛出异常。

#### 5.3 标记已访问
```python
visited_urls.add(url)
```
- 将当前 URL 添加到 `visited_urls` 集合，避免重复爬取。

#### 5.4 解析 HTML
```python
soup = BeautifulSoup(response.text, "html.parser")
```
- 使用 `BeautifulSoup` 将网页的 HTML 内容解析为可操作的对象。

#### 5.5 提取标题和内容
```python
page_title = soup.title.string if soup.title else "无标题"
content = soup.get_text()
```
- `page_title`：提取页面的 `<title>` 标签内容，如果没有则设为“无标题”。
- `content`：提取页面所有文本内容（去掉 HTML 标签）。

#### 5.6 保存数据
```python
crawled_data.append({
    "url": url,
    "title": page_title,
    "depth": depth,
    "content": content
})
```
- 将当前页面的信息（URL、标题、深度、内容）存入 `crawled_data` 列表。

#### 5.7 提取并递归爬取链接
```python
for link in soup.find_all("a", href=True):
    href = link.get("href")
    link_text = link.text.strip() or "无文本"
    absolute_url = urljoin(url, href)
    if absolute_url.startswith(("http://", "https://")):
        crawl(absolute_url, depth + 1)
```
- `soup.find_all("a", href=True)`：查找页面中所有带 `href` 属性的 `<a>` 标签（超链接）。
- `href`：获取链接地址。
- `link_text`：获取链接的文本内容，若为空则设为“无文本”。
- `urljoin(url, href)`：将相对链接（如 `/about`）转换为绝对链接（如 `https://arxiv.org/about`）。
- 如果链接以 `http://` 或 `https://` 开头，则递归调用 `crawl`，深度加 1。

#### 5.8 延迟
```python
time.sleep(1)
```
- 每次请求后暂停 1 秒，避免对服务器造成过大压力（礼貌爬取）。

#### 5.9 错误处理
```python
except requests.RequestException as e:
    print(f"爬取 {url} 失败: {e}")
```
- 如果请求失败（如超时或 404），打印错误信息。

---

### 6. 保存数据函数 `save_to_file`
```python
def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")
```
- `json.dump`：将数据以 JSON 格式写入文件。
- `ensure_ascii=False`：支持非 ASCII 字符（如中文）。
- `indent=4`：格式化 JSON，使其更易读。

---

### 7. 主函数 `main`
```python
def main():
    print("开始爬取...")
    crawl(START_URL)
    save_to_file(crawled_data, OUTPUT_FILE)
    print(f"爬取完成，共爬取 {len(crawled_data)} 个页面")
```
- 调用 `crawl` 开始爬取。
- 保存结果到文件。
- 打印爬取的总页面数。

---

### 8. 运行代码
```python
if __name__ == "__main__":
    main()
```
- 确保代码只在直接运行脚本时执行（而不是被导入时）。

---

### 9. 运行示例
1. 安装依赖：
   ```bash
   pip install requests beautifulsoup4
   ```
2. 运行代码：
   - 爬虫从 `https://arxiv.org/list/cs.AI/new` 开始。
   - 爬取该页面及其直接链接（深度 ≤ 1）。
   - 结果保存到 `crawled_data.json`。
3. 输出文件示例：
   ```json
   [
       {
           "url": "https://arxiv.org/list/cs.AI/new",
           "title": "New submissions for cs.AI",
           "depth": 0,
           "content": "...页面文本内容..."
       },
       {
           "url": "https://arxiv.org/abs/1234.56789",
           "title": "Paper Title",
           "depth": 1,
           "content": "...论文摘要等内容..."
       }
   ]
   ```

---

### 10. 注意事项
- **礼貌爬取**：`time.sleep(1)` 避免过于频繁请求，但可以根据网站政策调整。
- **robots.txt**：检查目标网站的 `robots.txt`（如 `https://arxiv.org/robots.txt`），确保遵守规则。
- **异常处理**：当前只处理了请求相关的异常，可根据需要扩展。
- **内容提取**：当前提取所有文本（`get_text()`），可改为提取特定元素（如论文标题、摘要）。

---

### 11. 改进建议
- **过滤链接**：添加域名限制（如只爬 `arxiv.org` 的链接）。
- **多线程**：使用 `threading` 或 `asyncio` 加速爬取。
- **数据清洗**：去掉无关内容（如页脚、导航栏）。
- **代理支持**：添加代理池以应对封禁。

