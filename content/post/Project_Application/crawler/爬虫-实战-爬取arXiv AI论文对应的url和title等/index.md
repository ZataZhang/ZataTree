---
title: 爬虫-实战-爬取arXiv AI论文对应的url和title等
description: ""
date: 2025-03-20T10:59:07+08:00
image: images/index/index.png
categories:
    - Project&Application
tags:
    - 爬虫
---





# 教程：使用 Python 爬取 arXiv AI 论文 / Tutorial: Crawling arXiv AI Papers with Python



|代码文件和实例arXiv的html文件|
|---|
|[爬虫代码](images/index/deepcrawler.py) |
|[json输出](images/index/arxiv_papers.json) |
|[html示例](/files/arxiv-ai-papers-sample.html)|

在本教程中，您将学习如何使用 Python 从 arXiv（一个流行的研究论文库）爬取最新的人工智能（AI）论文，并将结果保存为 JSON 文件。我们将逐步拆解代码，解释其功能，并告诉您如何根据需要进行修改。

In this tutorial, you’ll learn how to use Python to scrape the latest Artificial Intelligence (AI) papers from arXiv (a popular repository of research papers) and save the results in a JSON file. We’ll break down the code step by step, explaining its functionality and how you can modify it for your needs.

---

## 前提条件 / Prerequisites
开始之前，请确保您已安装以下内容：  
Before you begin, ensure you have the following installed:
- **Python 3.x**: 我们将使用的编程语言 / The programming language we’ll use.
- **库 / Libraries**:
  - `requests`: 用于发送 HTTP 请求获取网页 / For making HTTP requests to fetch web pages.
  - `beautifulsoup4`: 用于解析 HTML 内容 / For parsing HTML content.
  - `json`: Python 内置库，用于处理 JSON 数据 / Built-in Python library for working with JSON data.

安装所需库（使用 pip）：  
Install the required libraries using pip:
```bash
pip install requests beautifulsoup4
```

---

## 代码功能 / What the Code Does
这个脚本会：  
The script:
1. 从 arXiv 的 AI 新论文页面 (`https://arxiv.org/list/cs.AI/new`) 获取最新论文。  
   Fetches the latest AI papers from the arXiv page (`https://arxiv.org/list/cs.AI/new`).
2. 提取每篇论文的详细信息，例如标题、摘要、作者、评论和学科分类。  
   Extracts details like title, abstract, authors, comments, and subjects for each paper.
3. 将数据保存到 JSON 文件 (`arxiv_papers.json`)。  
   Saves the data in a JSON file (`arxiv_papers.json`).

让我们深入代码！  
Let’s dive into the code!

---

## 第一步：导入库 / Step 1: Importing Libraries
```python
import requests
from bs4 import BeautifulSoup
import json
import time
```
- `requests`: 发送 HTTP 请求以获取网页内容 / Sends HTTP requests to fetch the webpage.
- `BeautifulSoup`: 解析网页的 HTML 内容 / Parses the HTML content of the webpage.
- `json`: 处理 JSON 格式的数据保存 / Handles saving the scraped data in JSON format.
- `time`: 本脚本未使用，但可用于将来添加延迟 / Not used in this script but imported for potential future use (e.g., adding delays).

---

## 第二步：设置参数 / Step 2: Setting Configuration Parameters
```python
START_URL = "https://arxiv.org/list/cs.AI/new"  # arXiv AI 新论文页面 / arXiv AI new papers page
OUTPUT_FILE = "arxiv_papers.json"  # 输出文件名 / Output filename
```
- `START_URL`: 我们要爬取的网页（arXiv 的 AI 新论文页面）。  
   The webpage we want to scrape (new AI papers on arXiv).
- `OUTPUT_FILE`: 保存爬取数据的文件名。  
   The name of the file where the scraped data will be saved.

**修改建议 / Tip**: 您可以更改 `START_URL` 来爬取其他 arXiv 类别，例如 `cs.LG`（机器学习）。  
You can modify `START_URL` to scrape a different arXiv category (e.g., `cs.LG` for Machine Learning).

---

## 第三步：定义爬取函数 / Step 3: Defining the Crawling Function
```python
def crawl_arxiv_papers():
    print(f"开始爬取: {START_URL}")
    
    try:
        # 发送 HTTP 请求 / Send HTTP request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(START_URL, headers=headers, timeout=20)
        response.raise_for_status()
```
- `crawl_arxiv_papers()`: 执行爬取的主要函数 / The main function that performs the scraping.
- `headers`: 模拟浏览器请求，避免被服务器阻止 / Mimics a browser request to avoid being blocked by the server.
- `requests.get()`: 获取网页内容，设置 20 秒超时 / Fetches the webpage content with a 20-second timeout.
- `raise_for_status()`: 如果请求失败（例如 404 错误），抛出异常 / Raises an exception if the request fails (e.g., 404 error).

### 解析 HTML / Parsing the HTML
```python
        soup = BeautifulSoup(response.text, "html.parser")
        
        papers = []
        
        dt_tags = soup.find_all("dt")
```
- `BeautifulSoup`: 将 HTML 内容解析为可操作的结构 / Parses the HTML content into a navigable structure.
- `papers`: 存储爬取结果的列表 / A list to store the scraped paper data.
- `dt_tags`: 查找所有 `<dt>` 标签，每篇论文的条目从这里开始 / Finds all `<dt>` tags, which mark the start of each paper entry on the arXiv page.

### 提取论文详情 / Extracting Paper Details
```python
        for dt_tag in dt_tags:
            dd_tag = dt_tag.find_next_sibling("dd")
            if not dd_tag:
                continue
                
            paper = {}
```
- 遍历每个 `<dt>` 标签，找到对应的 `<dd>` 标签（包含元数据）。  
  Loops through each `<dt>` tag and finds its sibling `<dd>` tag (contains metadata).
- `paper`: 存储单篇论文详情的字典 / A dictionary to store details of a single paper.

#### 提取论文链接和 ID / Extracting Paper URL and ID
```python
            paper_link = dt_tag.find("a", href=True, title="Abstract")
            if paper_link:
                paper["arxiv_url"] = paper_link["href"]
                paper["arxiv_id"] = paper_link.text.strip()
```
- 找到 `<dt>` 中的摘要链接，提取 URL 和 arXiv ID（例如 `arXiv:XXXX.XXXX`）。  
  Finds the abstract link in `<dt>` and extracts the URL and arXiv ID (e.g., `arXiv:XXXX.XXXX`).

#### 提取元数据 / Extracting Metadata
```python
            meta_div = dd_tag.find("div", class_="meta")
            if not meta_div:
                continue
```
- 在 `<dd>` 中找到 `<div class="meta">`，它包含论文的详细信息。  
  Finds the `<div class="meta">` inside `<dd>`, which holds the paper’s details.

#### 标题 / Title
```python
            title_div = meta_div.find("div", class_="list-title mathjax")
            if title_div:
                title_text = title_div.get_text(strip=True)
                if "Title:" in title_text:
                    title_text = title_text.split("Title:", 1)[1].strip()
                paper["title"] = title_text
```
- 提取论文标题并移除 "Title:" 前缀。  
  Extracts the paper title and removes the "Title:" prefix.

#### 摘要 / Abstract
```python
            abstract = meta_div.find("p", class_="mathjax")
            if abstract:
                paper["abstract"] = abstract.get_text(strip=True)
```
- 提取论文摘要。  
  Extracts the abstract text.

#### 评论（可选） / Comments (Optional)
```python
            comments_div = meta_div.find("div", class_="list-comments mathjax")
            if comments_div:
                comments_text = comments_div.get_text(strip=True)
                if "Comments:" in comments_text:
                    comments_text = comments_text.split("Comments:", 1)[1].strip()
                paper["comments"] = comments_text
```
- 如果存在评论（例如 "10 pages, 3 figures"），则提取它。  
  Extracts comments if they exist (e.g., "10 pages, 3 figures").

#### 作者 / Authors
```python
            authors_div = meta_div.find("div", class_="list-authors")
            if authors_div:
                authors = [a.get_text(strip=True) for a in authors_div.find_all("a")]
                paper["authors"] = authors
```
- 提取作者列表。  
  Extracts a list of author names.

#### 学科分类 / Subjects
```python
            subjects_div = meta_div.find("div", class_="list-subjects")
            if subjects_div:
                subjects_text = subjects_div.get_text(strip=True)
                if "Subjects:" in subjects_text:
                    subjects_text = subjects_text.split("Subjects:", 1)[1].strip()
                paper["subjects"] = subjects_text
```
- 提取学科分类（例如 "Artificial Intelligence (cs.AI)"）。  
  Extracts the subject categories (e.g., "Artificial Intelligence (cs.AI)").

#### 添加到列表 / Adding to List
```python
            if paper:
                papers.append(paper)
```
- 将论文字典添加到 `papers` 列表中。  
  Adds the paper dictionary to the `papers` list.

### 错误处理 / Error Handling
```python
    except requests.RequestException as e:
        print(f"爬取失败: {e}")
        return []
```
- 捕获网络相关的错误，如果请求失败则返回空列表。  
  Catches network-related errors and returns an empty list if the request fails.

---

## 第四步：保存数据到文件 / Step 4: Saving Data to a File
```python
def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")
```
- `save_to_file()`: 将爬取的数据写入 JSON 文件。  
  Writes the scraped data to a JSON file.
- `ensure_ascii=False`: 保留非 ASCII 字符（例如中文或特殊符号）。  
  Preserves non-ASCII characters (e.g., Chinese or special symbols).
- `indent=4`: 格式化 JSON 文件以便阅读。  
  Formats the JSON file for readability.

---

## 第五步：主函数和执行 / Step 5: Main Function and Execution
```python
def main():
    print("开始爬虫程序...")
    papers = crawl_arxiv_papers()
    
    if papers:
        save_to_file(papers, OUTPUT_FILE)
        print(f"爬取完成，共获取 {len(papers)} 篇论文信息")
    else:
        print("未获取到任何论文信息")

if __name__ == "__main__":
    main()
```
- `main()`: 协调爬取和保存过程。  
  Orchestrates the crawling and saving process.
- `if __name__ == "__main__"`: 确保脚本仅在直接运行时执行（而不是被导入时）。  
  Ensures the script runs only when executed directly (not when imported).

---

## 运行代码 / Running the Code
1. 将代码保存到文件（例如 `arxiv_crawler.py`）。  
   Save the code in a file (e.g., `arxiv_crawler.py`).
2. 在同一目录下打开终端。  
   Open a terminal in the same directory.
3. 运行脚本：  
   Run the script:
   ```bash
   python arxiv_crawler.py
   ```
4. 检查输出文件 `arxiv_papers.json` 查看结果。  
   Check the output file `arxiv_papers.json` for the results.

### 示例输出 / Sample Output
`arxiv_papers.json` 文件可能如下所示：  
The `arxiv_papers.json` file might look like this:
```json
[
    {
        "arxiv_url": "/abs/2503.12345",
        "arxiv_id": "arXiv:2503.12345",
        "title": "A New AI Model",
        "abstract": "This paper introduces...",
        "authors": ["John Doe", "Jane Smith"],
        "subjects": "Artificial Intelligence (cs.AI)"
    },
    ...
]
```

---

## 自定义建议 / Tips for Customization
- **更改类别 / Change Category**: 修改 `START_URL` 来爬取其他 arXiv 类别（例如 `https://arxiv.org/list/cs.LG/new` 用于机器学习）。  
  Modify `START_URL` to scrape a different arXiv category (e.g., `https://arxiv.org/list/cs.LG/new` for Machine Learning).
- **添加延迟 / Add Delays**: 在循环中加入 `time.sleep(2)` 以避免对服务器造成过大压力。  
  Use `time.sleep(2)` in the loop to avoid overwhelming the server.
- **错误日志 / Error Logging**: 使用日志记录代替 `print` 语句，以便更好地调试。  
  Add logging instead of `print` statements for better debugging.

---
