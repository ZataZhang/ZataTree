---
title: "内容地图"
description: "这个站所有文章的地形图：每块的面积等于该分类的文章数，一眼看出重心在哪，以及你该从哪进去。"
date: 2026-09-16T21:00:00+08:00
layout: "map"
slug: "map"
url: "/map/"
menu:
    main:
        # 导航里显示英文，页面标题仍保持中文（其它页也是这样：Tags 页的
        # 标题是「标签云」）。菜单项的 name 会覆盖链接文字。
        name: Map
        weight: -100
        params:
            icon: categories

# 分类分组：把重复命名的分类归并成真实语义分组。
# terms 里写的是实际存在的分类 slug（Hugo 会统一转小写）。
groups:
    - title: "Knowledge"
      desc: "基础知识、通用教程与文档梳理。体量最大的一块，也是最适合从头翻的。"
      terms: ["Knowledge"]
    - title: "项目与应用"
      desc: "完整的项目实战记录：怎么搭、怎么拆、哪里会翻车。"
      terms: ["Project_Application", "Project&Application"]
    - title: "Library"
      desc: "各类库与框架的使用笔记，多数配可直接跑的代码。"
      terms: ["Library", "library", "Python-Library", "python"]
    - title: "Agent"
      desc: "AI Agent 工程：框架选型、上下文与记忆、工具调用、流式协议。"
      terms: ["Agent"]
    - title: "平台与工具"
      desc: "开发平台、CLI、编辑器与效率工具的一手实测。"
      terms: ["Platforms_Tools", "Platforms&Tools"]
    - title: "DeepLearning"
      desc: "模型、训练、推理与相关工具链。"
      terms: ["DeepLearning", "DeepLearing"]
    - title: "Grammar"
      desc: "编程语言语法速查：Python、Matlab、PyQt 等。"
      terms: ["Grammar"]
    - title: "Design"
      desc: "架构设计、建模、图表与原型。"
      terms: ["Design"]
    - title: "Vibe-Coding"
      desc: "AI 辅助前端开发与相关工作流。"
      terms: ["Vibe-Coding"]
    - title: "Engineering"
      desc: "软件工程实践：可观测性、开发流程、协作规范。"
      terms: ["Engineering"]
    - title: "Book"
      desc: "读书笔记与摘录。"
      terms: ["Book"]
    - title: "LLM"
      desc: "大模型本身的能力、限制与用法。"
      terms: ["LLM"]
    - title: "PaperReading"
      desc: "论文精读与要点摘录。"
      terms: ["PaperReading"]

# 三条入口路径，回答「我从哪开始读」
paths:
    - kicker: "第一次来"
      title: "先把知识库的地基过一遍"
      desc: "从通用知识类挑几篇，了解这个站讲事情的颗粒度。"
      terms: ["Knowledge"]
    - kicker: "带着具体问题"
      title: "看别人踩过的坑，别自己再踩"
      desc: "项目实战与工具实测：同一个问题，这里是跑过之后写的结论。"
      terms: ["Project_Application", "Platforms_Tools"]
    - kicker: "在做 AI 相关的东西"
      title: "Agent 工程这条线"
      desc: "从框架选型到记忆、协议、协作，是一条能顺着走完的线。"
      terms: ["Agent", "DeepLearning"]
---

带子上窄到放不下名字的分类，鼠标停上去看数字。下面每张卡片列出最近的三篇代表作，想看全部点分类名。
