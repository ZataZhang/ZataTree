---
title: scipy
description: SCiPY的常用操作
date: 2025-02-27
image: images/index/index.png
slug: scipy
# image: helena-hertz-wWZzXlDpMog-unsplash.jpg
categories:
    - Library
---

# SCiPY
## scipy.interpolate
### interp1d
- 代码
```python
from scipy.interpolate import interp1d
import numpy as np

# 示例数据
x_original = np.array([400, 500, 600, 700])  # 原始波长
y_original = np.array([0.1, 0.3, 0.6, 0.9])  # 对应的测量值
x_new = np.linspace(400, 700, 100)           # 新的波长点（目标插值点）

# 创建插值函数
interp_func = interp1d(x_original, y_original, kind='linear', fill_value="extrapolate")

# 使用插值函数计算新点的值
y_new = interp_func(x_new)

# 打印结果
print("原始波长:", x_original)
print("原始测量值:", y_original)
print("插值后的波长:", x_new)
print("插值后的测量值:", y_new)
```

- 参数解释
1. **`x_original` 和 `y_original`**:
   - 这是已知的原始数据点，分别表示波长和对应的测量值。
   - 它们必须是一维数组，并且长度相同。

2. **`kind`**:
   - 指定插值方法，常用选项包括：
     - `'linear'`：线性插值（默认）。
     - `'nearest'`：最近邻插值。
     - `'quadratic'` 或 `'cubic'`：二次或三次样条插值。
   - 根据数据的平滑性和需求选择合适的插值方法。

3. **`fill_value`**:
   - 当插值点超出原始数据范围时的处理方式。
   - 默认情况下会抛出错误，但可以通过设置 `fill_value="extrapolate"` 允许外推。

4. **`x_new`**:
   - 需要插值到的新点，可以是一个标量或数组。