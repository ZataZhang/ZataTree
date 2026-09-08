---
title: README
description: BLOG介绍
date: 2025-02-24T00:00:00+08:00
# slug: 文件夹名/index.md ## 必填，文件夹名/index.md
# image: helena-hertz-wWZzXlDpMog-unsplash.jpg
categories:
    # - DeepLearning
    # - Design
    # - Engineering
    # - Python
    # - LLM
    # - Project&Application
    # - Library
    # - PaperReading
    # - Study
    # - Other
    # - Knowledge points
tags:
    - github

---



# 内容模板

```md
---
title: XXX
description: XXX
date: 2025-02-24
slug: XXX/index.md ## 必填，文件夹名/index.md
draft: true  # 设置文章为草稿状态，Hugo 默认不会渲染，但是本地使用hugo server -D可以查看到
image: XXX
categories:
    # - DeepLearning
    # - Design
    # - Engineering
    # - Python
    # - LLM
    # - Library
    # - PaperReading
    # - Other

---
```

# 简介
本仓库旨在为计算机科学及相关领域的学习者和从业者提供一个系统化的知识概览。内容覆盖计算机基础、编程语言、算法与数据结构、操作系统、网络、数据库、人工智能等多个领域，所有内容均以简明扼要的方式呈现，适合快速查阅和入门学习。无论是初学者还是希望巩固基础知识的开发者，都可以在这里找到有价值的信息。

# 构建工具
zata.py文件的打包方式
```bash
pyinstaller --onefile --console --name=zata --clean zata.py
```

# 内容目录

## 知识点 (Knowledge)

### 百科知识
- [文学与幽默知识积累](../文学与幽默知识积累)
- [中国历史知识](../中国历史知识/)
- [茶叶](../茶叶/)
- [汽车-百科知识](../汽车-百科知识/)
- [总-百科知识](../总-百科知识/)
- [中国各省市介绍](../中国各省市介绍/)

### English
- [英语语法知识点](../英语语法知识点/)
- [english如何学习](../english如何学习/)

### 面试八股
- [深度学习八股-面试常见问题](../深度学习八股-面试常见问题/)
- [深度学习八股-量化](../深度学习八股-量化/)
- [深度学习八股-技术栈与工具](../深度学习八股-技术栈与工具/)
- [深度学习八股-实战经验](../深度学习八股-实战经验/)
- [深度学习八股-基础理论知识](../深度学习八股-基础理论知识/)
- [Langchain开发八股-常见问题](../Langchain开发八股-常见问题/)

### 系统相关
- [Linux](../Linux/)
  - [国外服务器扶墙](../国外服务器扶墙/)
  - [linux服务器初始化配置教程](../linux服务器初始化配置教程/)
- [Windows](../windows/)
  - [关闭win11更新](../关闭win11更新/)

### 其他知识
- [科技周报：机器人又抢饭碗啦](../科技周报：机器人又抢饭碗啦/)
- [word技巧](../word技巧/)
- [markdown](../markdown/)
- [news](../news/)
- [others](../others/)

## 项目和应用 (Project_Application)

### 爬虫
- [爬虫-基础介绍](../爬虫知识点/)
- [爬虫-实战-爬取arXiv AI论文对应的url和title等](../爬虫-实战-爬取arXiv AI论文对应的url和title等/)
- [爬虫-实战-多页面递归爬取](../爬虫-实战-多页面递归爬取/)
- [一个自动签到的py并且使用github action每日执行](../一个自动签到的py并且使用github action每日执行/)

### Hugo博客
- [1-hugo安装使用](../1-hugo安装使用/)
- [2-hugo主题和配置](../2-hugo主题和配置/)
- [3-hugo博客集成Netlify CMS](../3-hugo博客集成Netlify CMS/)
- [4-自定义Python函数创建博客：告别繁琐的文件头输入](../4-自定义Python函数创建博客：告别繁琐的文件头输入/)
- [5-引入 Giscus 评论系统](../5-引入 Giscus 评论系统/)
- [hugo使用过程中遇到的问题](../hugo使用过程中遇到的问题/)
- [给页面增加一个自定义密码（防君子不防小人）](../给页面增加一个自定义密码（防君子不防小人）/)

### Git & GitHub
- [git&github使用](../git&github使用/)
- [github release](../github release/)
- [github action](../github action/)
- [git-submodule-子模块](../git-submodule-子模块/)

### 其他项目
- [Dify](../Dify/)
- [软件使用经验 (SoftUseExp)](../SoftUseExp/)
- [软件试用 (SoftTrial)](../SoftTrial/)
- [腾讯云修改root登录](../腾讯云修改root登录/)
- [单片机](../单片机/)
- [微信小程序 (wechatapplet)](../wechatapplet/)
- [nginx使用](../nginx使用/)
- [VScode](../VScode/)
- [SSH](../SSH/)
- [PythonGUI](../PythonGUI/)

## 深度学习 (DeepLearning)

### 模型&策略
- [Attention](../attention注意力机制/) - 注意力机制（Attention Mechanism）详解
- [MoE](../MoE/) - 混合专家模型
- [模型-transformer原理和代码实现](../模型-transformer原理和代码实现/)
- [增量学习研究综述：理论、方法、应用与未来展望](../增量学习研究综述：理论、方法、应用与未来展望/)
- [RLHF](../RLHF/)
- [ICL-上下文学习](../ICL-上下文学习/)
- [Deepseek_NSA](../Deepseek_NSA/)

### 工具和框架
- [Tools](../Tools/)
- [NLP](../NLP/)

## 代码库教程 (Library)

### Python库
- [PyYAML](../PyYAML/) - PyYAML的常用操作
- [scipy](../scipy/)
- [sklearn使用教程](../sklearn使用教程/)
- [numpy使用教程](../numpy使用教程/)
- [tableprint使用教程](../tableprint使用教程/)
- [pickle](../pickle/)
- [gradio](../gradio/)
- [fastapi使用](../fastapi使用/)

### 其他库
- [小工具库 (smallLibrary)](../smallLibrary/)
- [优秀图表学习](../优秀图表学习/)
  - [分类图](../分类图/)
- [transformers](../transformers/)
- [torch](../torch/)
- [setuptools](../setuptools/)
- [pyserial](../pyserial/)
- [pandas](../pandas/)
- [matplotlib](../matplotlib/)
- [SQLAlchemy](../SQLAlchemy/)
- [React](../React/)
- [Flask](../Flask/)
- [FastAPI](../FastAPI/)

## 编程语法 (Grammar)

### Python
- [python-类](../python-类/)
- [python-难点和遇到的问题](../python-难点和遇到的问题/)
- [python-相对导入错误attempted relative import with no known parent package](../python-相对导入错误attempted relative import with no known parent package/)
- [python-数据类](../python-数据类/)
- [python-应如何定义包通用的变量-推荐config.py](../python-应如何定义包通用的变量-推荐config.py/)
- [python-将py文件编译为pyc文件并运行](../python-将py文件编译为pyc文件并运行/)
- [python-在项目中应该如何定义文件路径](../python-在项目中应该如何定义文件路径/)
- [python-typing提高代码可读性](../python-typing提高代码可读性/)
- [python-staticmethod 修饰符](../python-staticmethod 修饰符/)
- [python-logging模块添加日志](../python-logging模块添加日志/)
- [python-__init__.py为什么要写](../python-__init__.py为什么要写/)
- [python-Docstring 的详细教程](../python-Docstring 的详细教程/)

### 其他语言
- [PyQt](../PyQt/)
- [Matlab](../Matlab/)

## 设计 (Design)

### 软件架构设计
- [软件架构设计-培养软件架构师的思维](./Design/软件架构设计/软件架构设计-培养软件架构师的思维/)
- [FastAPI 后端架构设计](./Design/软件架构设计/FastAPI后端架构设计/)
- [一个标准的软件项目结构](./Design/软件架构设计/一个标准的软件项目结构/)

### 设计图与原型
- [行为图](./Design/行为图/)
- [结构图](./Design/结构图/)
- [原型图](./Design/原型图/)
- [功能图](./Design/功能图/)
- [值得学习的图](./Design/值得学习的图/)

## 工程实践 (Engineering)

### 软件工程
- [软件项目开发流程](./Engineering/软件工程/软件项目开发流程/)

### 可观测性
- [项目中日志的使用教程](./Engineering/可观测性/项目中日志的使用教程/)

## 论文阅读 (PaperReading)
- [RuijinHospitalandNearviewTechnologyLaunchRamanSpectroscopyforNon-InvasiveBloodGlucoseMonitoring_NatureMetabolism](../RuijinHospitalandNearviewTechnologyLaunchRamanSpectroscopyforNon-InvasiveBloodGlucoseMonitoring_NatureMetabolism/) - 瑞金医院拉曼光谱血糖监测

## 智能体 (Agent)

### metaGPT
- [metaGPT](../metaGPT/)

### LangChain
- [LangChain模型接入指南](../LangChain模型接入指南/)
- [langchain_core组件详解](../langchain_core组件详解/)
- [LangGraph实战教程](../LangGraph实战教程/)
- [LangChain-RAG实战教程](../LangChain-RAG实战教程/)
- [LangChain与MCP极简教程](../LangChain与MCP极简教程/)
- [LangSmith使用教程](../LangSmith使用教程/)
- [LangChain常见报错与排查](../LangChain常见报错与排查/)
- [订阅摘要Agent实战](../订阅摘要Agent实战/)
- [DeepAgents完全指南](../DeepAgents完全指南/)

### 其他Agent相关
- [Agent开发中遇到的问题](../Agent开发中遇到的问题/)

## 其他分类

### 书籍 (Book)

#### 大语言模型-赵鑫
- [1-背景与基础知识](../Book/大语言模型-赵鑫/1-背景与基础知识/)
- [2-预训练部分](../Book/大语言模型-赵鑫/2-预训练部分/)
- [03-微调与对齐](../Book/大语言模型-赵鑫/03-微调与对齐/)
- [04-大模型使用](../Book/大语言模型-赵鑫/04-大模型使用/)

### 平台工具 (Platforms_Tools)
- [Platforms_Tools](../Platforms_Tools/)

### 标签和分类页面
- [Tags](../tags)
- [Categories](../categories)

# 写作注意事项

## 文件结构
- 每个文章都需要单独的文件夹
- 文件夹内必须包含 `index.md` 文件
- 图片等资源文件与 `index.md` 文件放在同一文件夹内

## Front Matter 必填字段
- `title`: 文章标题
- `description`: 文章描述
- `date`: 发布日期
- `slug`: 文件夹名/index.md （必填）
- `categories`: 分类（可选，但建议填写）
- `tags`: 标签（可选）

## 可选字段
- `draft: true`: 设置文章为草稿状态，Hugo 默认不会渲染，但是本地使用 `hugo server -D` 可以查看到
- `image`: 文章封面图片

## 分类说明
主要分类包括：
- `DeepLearning`: 深度学习相关
- `Design`: 设计与建模
- `Engineering`: 工程实践
- `Python`: Python 相关
- `LLM`: 大语言模型相关
- `Library`: 库和工具相关
- `PaperReading`: 论文阅读
- `Knowledge`: 知识点
- `Project&Application`: 项目和应用
- `Other`: 其他

## 本地预览
使用以下命令进行本地预览：
```bash
hugo server -D  # 包括草稿
hugo server     # 不包括草稿
```
