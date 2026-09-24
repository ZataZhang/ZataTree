---
title: Markdown中常用的图标或徽章
description: ""
date: 2025-03-18T11:33:14+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - markdown
---


|下载网站|
|---|
|https://igoutu.cn/icons/set/markdown|
|https://blog.csdn.net/luo15242208310/article/details/114530777|
|https://shields.io/badges/static-badge|

### 常用 Shields.io 徽章示例
Shields.io 是一个生成徽章的流行服务，以下是一些常见的 Markdown 格式徽章代码：

1. **下载按钮**

[![Download](https://img.shields.io/badge/Download-Install%20Package-blue)](https://example.com)


   ```
   [![Download](https://img.shields.io/badge/Download-Install%20Package-blue)](https://example.com)
   ```
   显示效果：一个蓝色“Download - Install Package”徽章，点击可跳转到链接。

2. **版本号**

   [![Version](https://img.shields.io/badge/Version-1.0.0-green)](https://example.com)

   ```
   [![Version](https://img.shields.io/badge/Version-1.0.0-green)](https://example.com)
   ```
   显示效果：绿色“Version - 1.0.0”徽章。

3. **许可证**

   [![License](https://img.shields.io/badge/License-MIT-yellow)](https://example.com)

   ```
   [![License](https://img.shields.io/badge/License-MIT-yellow)](https://example.com)
   ```
   显示效果：黄色“License - MIT”徽章。

4. **构建状态**

   [![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)](https://example.com)

   ```
   [![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)](https://example.com)
   ```
   显示效果：亮绿色“Build - Passing”徽章。

5. **自定义文本**

   [![Custom](https://img.shields.io/badge/Custom-Message-red)](https://example.com)

   ```
   [![Custom](https://img.shields.io/badge/Custom-Message-red)](https://example.com)
   ```
   显示效果：红色“Custom - Message”徽章。

### 如何自定义
- **颜色**：可以替换 `blue`、`green`、`yellow` 等为其他颜色（如 `red`、`orange`、`purple`），或使用 HEX 代码（如 `#FF5733`）。
- **文本**：修改 `Download-Install%20Package` 为你想要的文字，用 `%20` 表示空格。
- **链接**：将 `(https://example.com)` 替换为实际的 URL。

### 获取更多徽章
如果你需要更多样式，可以访问 [Shields.io](https://shields.io/) 自定义生成，然后将生成的 URL 放入 Markdown 格式：
```
[![标签](徽章URL)](跳转链接)
```

### 其他图标资源
如果是指非徽章类图标（比如 emoji 或图片），可以这样嵌入：
1. **Emoji**：
   ```
   下载：📥
   ```
   显示效果：下载：📥

2. **外部图片**：
   ```
   ![图标](https://example.com/icon.png)
   ```

如果你想要更具体的图标或某种风格的“图标中心”（hub），可以告诉我更多需求，我再帮你完善！