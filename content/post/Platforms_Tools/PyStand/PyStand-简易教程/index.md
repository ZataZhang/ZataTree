---
title: PyStand-简易教程
description: ""
draft: true
date: 2025-04-28T10:07:02+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - PyStand
---


[pystand项目地址](https://github.com/skywind3000/PyStand)






## 问题和注意事项

1.  python嵌入包的版本要和开发时候的版本一致

我因为开发版本是3.11，搞了一个3.10的python嵌入包而报错


2. 精简代码组织

PyStand.int 仅作为入口，复杂逻辑放入 script 目录的 main.py 或其他模块，方便调试和维护。
路径配置：在 PyStand.int 中通过 sys.path.append 添加 script 或 script.egg 路径，确保模块可加载。






## 打包教程

来源： https://www.zhihu.com/question/48776632/answer/2336654649




![韦神的知乎回答](images/index/image.png)
