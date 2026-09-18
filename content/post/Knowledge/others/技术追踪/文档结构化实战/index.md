---
title: 文档结构化实战：从 Markdown/PDF 到 Word
description: "记录 Markdown 转 Word、PDF 转 Word 的实战经验，包括 LaTeX 公式渲染、表格提取等难点攻克"
date: 2026-06-04T12:00:00+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - 文档结构化
    - python
    - python-docx
    - pyMuPDF
    - LaTeX
    - OMML
---

> 纸上得来终觉浅，绝知此事要躬行。本文记录文档结构化转换的实战经验，重点攻克 LaTeX 公式渲染、表格提取等难点。

## 背景

写学术论文时，常有两类需求：
1. **Markdown → Word**：用 Markdown 写内容，一键套用学术模板生成 Word
2. **PDF → Word**：把 PDF 论文转成可编辑的 Word 文档

本文基于 [kritidocx-demo](https://github.com/your-repo/kritidocx-demo) 项目，总结实战中踩过的坑和解决方案。

---

## 一、Markdown 转 Word

### 1.1 方案选择

| 方案 | 优点 | 缺点 |
|------|------|------|
| KritiDocX | 功能完整，支持模板 | 依赖外部库 |
| python-docx + BeautifulSoup | 纯 Python，可控性强 | 需要自己实现解析逻辑 |

本项目采用 **python-docx + BeautifulSoup** 方案，自己掌控每一行代码。

### 1.2 核心流程

```
Markdown (内容)
       ↓
HTML (markdown 库解析)
       ↓
模板 HTML (插入变量)
       ↓
Word (python-docx 生成)
```

### 1.3 LaTeX 公式 → Word OMML

这是最复杂的部分。Word 使用 OMML (Office Math Markup Language) 存储数学公式，需要把 LaTeX 语法转换为 OMML XML。

#### 实现思路

```python
def parse_latex_to_omml(latex: str) -> OxmlElement:
    """将 LaTeX 转换为 Word OMML 结构"""
    math = create_element("oMath")

    # 处理分数 \frac{分子}{分母}
    frac_match = re.search(r"\\frac\{([^}]+)\}\{([^}]+)\}", latex)
    if frac_match:
        frac = create_element("f")
        # ... 构建 oMath 分数结构

    return math
```

#### 关键点

1. **命名空间**：OMML 使用 `m:` 前缀的命名空间
   ```python
   def create_element(tag: str, text: str = None, **attrs) -> OxmlElement:
       elem = OxmlElement(f"m:{tag}")  # m:oMath, m:f, m:num...
       for key, val in attrs.items():
           elem.set(qn(f"m:{key}"), val)
       return elem
   ```

2. **分数结构**：
   ```
   oMath
   └── f (fraction)
       ├── fPr (fraction properties)
       │   └── ctrlPr → ctrl: "on"
       ├── num (numerator)
       └── den (denominator)
   ```

3. **文本模式**：`\text{...}` 需要转换为纯文本 run
   ```python
   latex = re.sub(r"\\text\{([^}]+)\}", r"\1", latex)
   ```

### 1.4 模板系统

预置三种学术模板：论文(paper)、会议(conference)、报告(report)，通过 HTML 模板定义格式：

```html
<!-- templates/paper.html 片段 -->
<header>
    <h1>$TITLE$</h1>
    <p class="author">$AUTHOR$</p>
</header>
<div class="abstract">
    <h2>摘要</h2>
    <p>$ABSTRACT$</p>
</div>
<main></main>
```

运行时替换 `$TITLE$`、`$AUTHOR$` 等变量，将 Markdown 解析后的 HTML 插入 `<main></main>`。

### 1.5 效果

```bash
md2latex demo/sample.md --template paper -o output.docx
```

生成的 Word 包含：
- 标题居中、作者信息
- 摘要样式
- LaTeX 公式渲染为可编辑的 OMML
- 表格、图片自动插入

---

## 二、PDF 转 Word

### 2.1 方案选择

| 库 | 用途 | 特点 |
|----|------|------|
| pyMuPDF | 提取文本、图像 | 速度快，支持布局分析 |
| pdfplumber | 提取表格 | 专门优化表格检测 |
| python-docx | 生成 Word | 跨平台 API 友好 |

本项目采用 **pyMuPDF + pdfplumber + python-docx** 三件套。

### 2.2 文本提取

pyMuPDF 的 `page.get_text("dict")` 可以获取详细的文本块信息，包括字体大小、位置：

```python
def extract_text_with_layout(page: fitz.Page) -> list[tuple[str, float]]:
    """提取文本，保留布局信息"""
    text_dict = page.get_text("dict")

    items = []
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:  # 只处理文本块
            continue

        block_lines = []
        for line in block.get("lines", []):
            line_texts = []
            for span in line.get("spans", []):
                text = span.get("text", "")
                if text.strip():
                    line_texts.append(text)

            if line_texts:
                line_text = " ".join(line_texts)
                block_lines.append(line_text)

        if block_lines:
            spans = block.get("lines", [[]])[0].get("spans", [])
            size = sum(s.get("size", 10) for s in spans) / len(spans) if spans else 10
            items.append((block_bbox[1], "\n".join(block_lines), size))

    return sorted(items, key=lambda x: x[0])  # 按 y 坐标排序
```

### 2.3 标题识别

根据字体大小判断标题级别：

```python
def detect_heading(text: str, size: float) -> tuple[bool, str]:
    """判断文本是否为标题"""
    text_stripped = text.strip()

    # 特殊关键词
    if text_stripped.lower() in ["abstract", "摘要"]:
        return True, "Heading 2"

    # 编号标题（如 "1. Introduction"）
    section_match = re.match(r"^(\d+\.?\d*)\s+[A-Z][a-z]", text_stripped)
    if section_match and len(text_stripped) < 80:
        return True, "Heading 2"

    # 字体大小判断
    if size >= 14:
        return True, "Heading 1"
    if size >= 12:
        return True, "Heading 2"

    return False, "Normal"
```

### 2.4 表格提取

pdfplumber 的 `extract_words()` 返回单词级别的位置信息，可以基于 y 坐标分组重建表格：

```python
def extract_mmlu_table(page: pdfplumber.pdf.Page) -> list[list[str]]:
    """提取特定表格（MMLU 语言能力对比表）"""
    words = page.extract_words()

    rows_dict = defaultdict(list)
    for w in words:
        y = round(w['top'] / 10) * 10  # 按 10px 分组
        text = w['text'].strip()
        if text and len(text) < 30:
            rows_dict[y].append({'text': text, 'x0': w['x0']})

    table_data = []
    for y in sorted(rows_dict.keys()):
        row_items = sorted(rows_dict[y], key=lambda w: w['x0'])
        texts = [item['text'] for item in row_items]
        x_positions = [item['x0'] for item in row_items]
        x_spread = max(x_positions) - min(x_positions)

        # 判断是否为表格行
        if x_spread > 250 and len(texts) >= 2:
            table_data.append(texts[:3])

    return table_data if len(table_data) >= 10 else []
```

### 2.5 图像提取

pyMuPDF 可以直接提取嵌入图片：

```python
def extract_images(page: fitz.Page, output_path: Path) -> None:
    """提取页面中的图片"""
    for img in page.get_images(full=True):
        xref = img[0]
        base_image = page.parent.extract_image(xref)
        img_bytes = base_image["image"]
        ext = base_image["ext"]

        temp_path = output_path.parent / f"temp_{xref}.{ext}"
        with open(temp_path, "wb") as f:
            f.write(img_bytes)

        # 插入 Word
        run.add_picture(str(temp_path), width=Inches(5))
        temp_path.unlink()  # 用完删除
```

### 2.6 效果

```bash
python -m md2latex.pdf2docx demo/sample_paper.pdf -o output.docx
```

生成的 Word 包含：
- 按阅读顺序排列的段落
- 自动识别的标题层级
- 检测到的表格
- 页面中的嵌入图片

---

## 三、踩坑记录

### 3.1 LaTeX 公式渲染失败

**问题**：复杂的 LaTeX 公式（如矩阵、多行公式）转换后 Word 显示异常。

**原因**：只实现了分数、文本等简单结构，复杂的 `\begin{pmatrix}`、`\begin{align}` 等未处理。

**解决**：
1. 简化 LaTeX 输入，避免使用多行公式
2. 或降级为图片渲染：先用 LaTeX 生成图片，再插入 Word

### 3.2 表格跨页断开

**问题**：PDF 中跨页的表格被拆成两个独立表格。

**原因**：pdfplumber 按页提取，不跨页合并。

**解决**：维护一个跨页表格 buffer，检测到表头后开始收集，直到遇到非表格内容再写入 Word。

### 3.3 字体大小与标题级别不匹配

**问题**：有些 PDF 使用非标准字体，检测到的字体大小与实际视觉大小不符。

**原因**：PDF 内部字体大小与渲染大小可能不同（缩放因子）。

**解决**：结合字体名判断（如 "Times-Bold" 通常是标题）和字号双重判断。

### 3.4 图片尺寸过大

**问题**：提取的图片在 Word 中显示过大或过小。

**原因**：未指定尺寸时，python-docx 使用图片原始尺寸。

**解决**：
```python
run.add_picture(str(img_path), width=Inches(5.0))  # 固定宽度 5 英寸
```

---

## 四、关键代码片段

### 4.1 插入 OMML 数学公式

```python
def insert_omml_paragraph(doc: Document, latex: str, center: bool = False) -> None:
    """将 LaTeX 公式插入为 Word OMML"""
    para = doc.add_paragraph()
    if center:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    math_para = create_omml_math(latex)
    para._element.append(math_para)
```

### 4.2 清理 PDF 提取的文本

```python
def clean_text(text: str, preserve_spaces: bool = False) -> str:
    """清理控制字符"""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    if preserve_spaces:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'\n\s*\n', '\n\n', text)
    else:
        text = re.sub(r'\s+', ' ', text)

    return text.strip()
```

### 4.3 创建 Word 表格

```python
def create_table(doc: Document, table_data: list[list[str]]) -> None:
    """创建带边框的 Word 表格"""
    max_cols = max(len(row) for row in table_data)
    table = doc.add_table(rows=len(table_data), cols=max_cols)
    table.style = "Table Grid"

    for row_idx, row_data in enumerate(table_data):
        for col_idx, cell_text in enumerate(row_data):
            if col_idx < max_cols:
                cell = table.rows[row_idx].cells[col_idx]
                cell.text = clean_text(cell_text, False)
```

---

## 五、实战项目

完整的实现代码见：[kritidocx-demo](https://github.com/your-repo/kritidocx-demo)

```
kritidocx-demo/
├── md2latex/           # Markdown → Word
│   ├── converter.py    # 核心转换逻辑
│   ├── templates/      # HTML 模板
│   └── pdf2docx/       # PDF → Word
└── demo/               # 示例文件
```

---

*持续更新中...*