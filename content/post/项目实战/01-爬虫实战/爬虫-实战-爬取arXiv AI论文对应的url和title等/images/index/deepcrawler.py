import requests
from bs4 import BeautifulSoup
import json
import time

# 配置参数
START_URL = "https://arxiv.org/list/cs.AI/new"  # arXiv AI 新论文页面
OUTPUT_FILE = "arxiv_papers.json"  # 输出文件名

def crawl_arxiv_papers():
    print(f"开始爬取: {START_URL}")
    
    try:
        # 发送HTTP请求 send an HTTP request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(START_URL, headers=headers, timeout=20)
        response.raise_for_status() # 如果请求失败，抛出异常 if response.status_code != 200:
        
        # 解析HTML内容 parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser") # 使用html.parser解析HTML内容 use html.parser to parse the HTML content
        
        # 存储爬取结果  store the crawling results
        papers = []
        
        # 查找所有论文条目 (每个条目通常是一对dt和dd标签) find all the paper items (each item is usually a pair of dt and dd tags)
        dt_tags = soup.find_all("dt")
        
        for dt_tag in dt_tags:
            # 找到对应的dd标签 find the corresponding dd tag
            dd_tag = dt_tag.find_next_sibling("dd") # 找到下一个兄弟标签 ，也就是平行标签 find the next sibling tag 
            if not dd_tag:
                continue
                
            paper = {}
            
            # 从dt标签提取论文链接 extract the paper link from the dt tag
            paper_link = dt_tag.find("a", href=True, title="Abstract")
            if paper_link:
                paper["arxiv_url"] = paper_link["href"]
                paper["arxiv_id"] = paper_link.text.strip()
            
            # 从dd标签提取meta信息 extract the meta information from the dd tag
            meta_div = dd_tag.find("div", class_="meta")
            if not meta_div:
                continue
                
            # 提取标题
            title_div = meta_div.find("div", class_="list-title mathjax")
            if title_div:
                # 移除"Title:"前缀
                title_text = title_div.get_text(strip=True)
                if "Title:" in title_text:
                    title_text = title_text.split("Title:", 1)[1].strip()
                paper["title"] = title_text
            
            # 提取摘要
            abstract = meta_div.find("p", class_="mathjax")
            if abstract:
                paper["abstract"] = abstract.get_text(strip=True)
            
            # 提取评论(如果存在)
            comments_div = meta_div.find("div", class_="list-comments mathjax")
            if comments_div:
                comments_text = comments_div.get_text(strip=True)
                if "Comments:" in comments_text:
                    comments_text = comments_text.split("Comments:", 1)[1].strip()
                paper["comments"] = comments_text
            
            # 提取作者
            authors_div = meta_div.find("div", class_="list-authors")
            if authors_div:
                authors = [a.get_text(strip=True) for a in authors_div.find_all("a")]
                paper["authors"] = authors
            
            # 提取学科分类
            subjects_div = meta_div.find("div", class_="list-subjects")
            if subjects_div:
                subjects_text = subjects_div.get_text(strip=True)
                if "Subjects:" in subjects_text:
                    subjects_text = subjects_text.split("Subjects:", 1)[1].strip()
                paper["subjects"] = subjects_text
            
            # 添加到结果列表
            if paper:
                papers.append(paper)
        
        return papers
        
    except requests.RequestException as e:
        print(f"爬取失败: {e}")
        return []

def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

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