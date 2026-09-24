---
title: matplotlib教程-zata——v0.0.0
description: ""
date: 2025-05-11T05:59:00+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - matplotlib
---




[参考菜鸟教程](https://www.runoob.com/matplotlib/matplotlib-zh.html)





### matplotlib中文显示乱码问题



```python

对于 Windows：

plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
在 Windows 系统上，选择 SimHei（黑体）或其他中文字体，并将其设置为 Matplotlib 的默认字体。

对于 Linux：

plt.rcParams['font.family'] = 'WenQuanYi Micro Hei'  # 替换为你选择的字体
```

如果不知道有哪些字体可以，可以先执行以下代码

```python
from matplotlib import pyplot as plt
import matplotlib
a=sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])

for i in a:
    print(i)
```