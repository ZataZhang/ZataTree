---
title: numpy使用教程
description: ""
date: 2025-06-18T14:44:27+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - Python_Lib
---


---

### NumPy 教程

```py
import numpy as np

# 1. 创建数组
arr1 = np.array([1, 2, 3, 4])  # 一维数组
arr2 = np.array([[1, 2], [3, 4]])  # 二维数组
zeros = np.zeros((2, 3))  # 2x3 零矩阵
ones = np.ones((3, 2))  # 3x2 全一矩阵
arange = np.arange(0, 10, 2)  # 范围数组 [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)  # 等间距数组 [0.  , 0.25, 0.5 , 0.75, 1.  ]
random_arr = np.random.rand(2, 3)  # 2x3 随机数组（0到1）

# 2. 数组属性
print(arr2.shape)  # 形状 (2, 2)
print(arr2.ndim)  # 维度 2
print(arr2.dtype)  # 数据类型
print(arr2.size)  # 元素总数 4

# 3. 数组操作
print(arr1 + 2)  # 元素级加 [3, 4, 5, 6]
print(arr1 * 3)  # 元素级乘 [3, 6, 9, 12]
print(arr2.reshape(4,))  # 改变形状 [1, 2, 3, 4]
print(arr2.T)  # 转置 [[1, 3], [2, 4]]

# 4. 索引和切片
arr3 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(arr3[0, 1])  # 访问元素 2
print(arr3[0:2, 1:3])  # 切片 [[2, 3], [5, 6]]
print(arr3[arr3 > 5])  # 布尔索引 [6, 7, 8, 9]
print(arr3[[0, 2], [1, 2]])  # 花式索引 [2, 9]

# 5. 数学和统计函数
print(np.sqrt(arr1))  # 平方根
print(np.sum(arr3))  # 总和 45
print(np.mean(arr3))  # 均值 5.0
print(np.std(arr3))  # 标准差
print(np.max(arr3))  # 最大值 9
print(np.min(arr3, axis=1))  # 每行最小值 [1, 4, 7]

# 6. 线性代数
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(A @ B)  # 矩阵乘法 [[19, 22], [43, 50]]
print(np.linalg.det(A))  # 行列式 -2.0
print(np.linalg.inv(A))  # 矩阵逆
eigvals, eigvecs = np.linalg.eig(A)  # 特征值和特征向量
print(eigvals, eigvecs)

# 7. 广播
arr4 = np.array([1, 2, 3])
arr5 = np.array([[1], [2], [3]])
print(arr4 + arr5)  # 广播运算

# 8. 拼接与分割
vstack = np.vstack((A, B))  # 垂直拼接
hstack = np.hstack((A, B))  # 水平拼接
split = np.split(arr3, 3, axis=0)  # 沿轴0分成3部分

# 9. 排序与搜索
arr6 = np.array([3, 1, 4, 1, 5])
print(np.sort(arr6))  # 排序 [1, 1, 3, 4, 5]
print(np.argsort(arr6))  # 排序索引 [1, 3, 0, 2, 4]
print(np.argmax(arr6))  # 最大值索引 4
print(np.argmin(arr6))  # 最小值索引 1

# 10. 随机数
np.random.seed(42)  # 设置种子
print(np.random.rand(2, 3))  # 均匀分布随机数
print(np.random.randn(2, 3))  # 正态分布随机数
print(np.random.randint(1, 10, size=(2, 3)))  # 随机整数
arr7 = np.array([1, 2, 3, 4, 5])
np.random.shuffle(arr7)  # 随机打乱
creplace = np.random.choice(arr7, size=3, replace=False)  # 随机选择

# 11. 结构化数组
dtype = np.dtype([('name', 'U10'), ('age', 'i4')])
data = np.array([('Alice', 25), ('Bob', 30)], dtype=dtype)
print(data['name'])  # ['Alice', 'Bob']

# 12. 高级数学
print(np.cumsum(arr1))  # 累积和 [1, 3, 6, 10]
print(np.cumprod(arr1))  # 累积积 [1, 2, 6, 24]
print(np.fft.fft(arr1))  # 快速傅里叶变换
print(np.gradient(arr1))  # 梯度

# 13. 保存和加载
np.save('array.npy', arr1)  # 保存数组
loaded_arr = np.load('array.npy')  # 加载数组
np.savetxt('array.txt', arr1, delimiter=',')  # 保存为文本

# 14. 内存优化
arr8 = np.array([1, 2, 3], dtype=np.float32)  # 指定类型减少内存
arr8 += 10  # 就地操作
```

#### 2. **创建数组**
NumPy 的核心是 `ndarray` 对象，用于表示多维数组。以下是常见创建方法：

```python
# 一维数组
arr1 = np.array([1, 2, 3, 4])

# 二维数组
arr2 = np.array([[1, 2], [3, 4]])

# 全零数组
zeros = np.zeros((2, 3))  # 2x3 零矩阵

# 全一数组
ones = np.ones((3, 2))  # 3x2 全一矩阵

# 范围数组
arange = np.arange(0, 10, 2)  # 从0到10（不含10），步长2

# 等间距数组
linspace = np.linspace(0, 1, 5)  # 从0到1，生成5个等间距数

# 随机数组
random_arr = np.random.rand(2, 3)  # 2x3 随机数（0到1）
```

---

#### 3. **数组属性**
查看数组的形状、维度和数据类型：

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# 形状
print(arr.shape)  # (2, 3)

# 维度
print(arr.ndim)  # 2

# 数据类型
print(arr.dtype)  # int64（具体取决于系统）

# 元素总数
print(arr.size)  # 6
```

---

#### 4. **数组操作**
NumPy 支持高效的元素级操作和广播机制。

```python
arr = np.array([1, 2, 3, 4])

# 元素级运算
print(arr + 2)  # [3, 4, 5, 6]
print(arr * 3)  # [3, 6, 9, 12]

# 数组间运算
arr2 = np.array([5, 6, 7, 8])
print(arr + arr2)  # [6, 8, 10, 12]

# 改变形状
arr3 = np.array([[1, 2], [3, 4]])
print(arr3.reshape(4,))  # [1, 2, 3, 4]

# 转置
print(arr3.T)  # [[1, 3], [2, 4]]
```

---

#### 5. **索引和切片**
NumPy 数组支持灵活的索引和切片操作。

```python
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# 访问元素
print(arr[0, 1])  # 2

# 切片
print(arr[0:2, 1:3])  # [[2, 3], [5, 6]]

# 布尔索引
print(arr[arr > 5])  # [6, 7, 8, 9]

# 花式索引
print(arr[[0, 2], [1, 2]])  # [2, 9]
```

---

#### 6. **数学和统计函数**
NumPy 提供丰富的数学和统计操作。

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# 基本数学函数
print(np.sqrt(arr))  # 平方根
print(np.exp(arr))  # 指数
print(np.sin(arr))  # 正弦

# 统计函数
print(np.sum(arr))  # 总和：21
print(np.mean(arr))  # 均值：3.5
print(np.std(arr))  # 标准差
print(np.max(arr))  # 最大值：6
print(np.min(arr, axis=1))  # 每行最小值：[1, 4]
```

---

#### 7. **线性代数**
NumPy 支持矩阵运算和线性代数操作。

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 矩阵乘法
print(np.dot(A, B))  # [[19, 22], [43, 50]]

# 矩阵 determinant
print(np.linalg.det(A))  # -2.0

# 矩阵逆
print(np.linalg.inv(A))  # [[-2, 1], [1.5, -0.5]]

# 特征值和特征向量
eigvals, eigvecs = np.linalg.eig(A)
print(eigvals)  # 特征值
print(eigvecs)  # 特征向量
```

---

#### 8. **保存和加载数据**
NumPy 支持将数组保存到文件或从文件加载。

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# 保存到文件
np.save('array.npy', arr)

# 加载文件
loaded_arr = np.load('array.npy')
print(loaded_arr)

# 保存为文本
np.savetxt('array.txt', arr, delimiter=',')
```

---

#### 9. **性能优化提示**
- 使用 NumPy 的向量化操作，避免 Python 循环。
- 预分配数组大小，避免动态扩展。
- 使用 `inplace` 操作（如 `+=`）减少内存分配。
- 选择合适的数据类型（如 `float32` 而非 `float64`）以节省内存。

---

#### 10. **常见问题与调试**
- **形状不匹配**：检查 `shape` 属性，确保广播规则适用。
- **数据类型问题**：使用 `astype` 转换类型，如 `arr.astype(np.float32)`。
- **内存问题**：处理大数组时，考虑分块处理或使用 `memmap`。

---

好的！下面我将扩展 NumPy 教程，深入介绍更多高级功能和实用技巧，涵盖广播、数组拼接、排序、随机数生成、结构化数组、内存优化以及实际应用场景。每个部分都附上清晰的代码示例，放在代码块中，方便您直接使用。教程将保持简洁但全面，适合进一步学习 NumPy。

---
#### 1. **广播机制（Broadcasting）**
NumPy 的广播机制允许不同形状的数组进行运算，自动扩展维度以匹配。

```python
import numpy as np

# 标量与数组运算
arr = np.array([[1, 2, 3], [4, 5, 6]])
print(arr + 10)  # 每个元素加10
# [[11, 12, 13], [14, 15, 16]]

# 不同形状数组运算
arr1 = np.array([1, 2, 3])
arr2 = np.array([[1], [2], [3]])
print(arr1 + arr2)  # 广播后相加
# [[2, 3, 4], [3, 4, 5], [4, 5, 6]]

# 手动广播
arr3 = np.array([1, 2, 3]).reshape(1, 3)
print(arr3 + arr2)  # 同上
```

**提示**：广播要求维度兼容（维度相同或其中一个为 1）。检查 `shape` 避免错误。

---

#### 2. **数组拼接与分割**
NumPy 提供多种方法来合并或拆分数组。

```python
# 拼接数组
arr1 = np.array([[1, 2], [3, 4]])
arr2 = np.array([[5, 6], [7, 8]])

# 垂直拼接
vstack = np.vstack((arr1, arr2))
print(vstack)
# [[1, 2], [3, 4], [5, 6], [7, 8]]

# 水平拼接
hstack = np.hstack((arr1, arr2))
print(hstack)
# [[1, 2, 5, 6], [3, 4, 7, 8]]

# 沿指定轴拼接
concat = np.concatenate((arr1, arr2), axis=0)  # 同 vstack
print(concat)

# 分割数组
arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
split = np.split(arr, 2, axis=1)  # 沿轴1分成2部分
print(split)  # [array([[1, 2], [5, 6]]), array([[3, 4], [7, 8]])]
```

---

#### 3. **排序与搜索**
NumPy 支持高效的数组排序和元素搜索。

```python
arr = np.array([3, 1, 4, 1, 5, 9, 2])

# 排序
sorted_arr = np.sort(arr)
print(sorted_arr)  # [1, 1, 2, 3, 4, 5, 9]

# 获取排序索引
indices = np.argsort(arr)
print(indices)  # [1, 3, 6, 0, 2, 4, 5]

# 二维数组按某列排序
arr2d = np.array([[3, 1], [2, 4], [1, 3]])
sorted_by_col0 = arr2d[arr2d[:, 0].argsort()]
print(sorted_by_col0)  # [[1, 3], [2, 4], [3, 1]]

# 搜索最大/最小值索引
max_idx = np.argmax(arr)
min_idx = np.argmin(arr)
print(max_idx, min_idx)  # 5, 1
```

---

#### 4. **随机数生成**
NumPy 的 `random` 模块提供多种随机数生成方法，适合模拟和机器学习。

```python
# 设置随机种子以确保可重复性
np.random.seed(42)

# 均匀分布（0到1）
rand_uniform = np.random.rand(2, 3)
print(rand_uniform)

# 正态分布（均值0，标准差1）
rand_normal = np.random.randn(2, 3)
print(rand_normal)

# 随机整数
rand_int = np.random.randint(low=1, high=10, size=(2, 3))
print(rand_int)

# 随机打乱数组
arr = np.array([1, 2, 3, 4, 5])
np.random.shuffle(arr)
print(arr)  # 顺序随机变化

# 随机选择
choices = np.random.choice(arr, size=3, replace=False)
print(choices)  # 从arr中随机选3个数
```

---

#### 5. **结构化数组**
NumPy 支持结构化数组，类似数据库表，适合存储异构数据。

```python
# 定义结构化数据类型
dtype = np.dtype([('name', 'U10'), ('age', 'i4'), ('score', 'f4')])

# 创建结构化数组
data = np.array([('Alice', 25, 85.5), ('Bob', 30, 90.0)], dtype=dtype)
print(data)
# [('Alice', 25, 85.5) ('Bob', 30, 90. )]

# 访问字段
print(data['name'])  # ['Alice', 'Bob']
print(data[0]['score'])  # 85.5
```

---

#### 6. **高级数学运算**
NumPy 提供丰富的数学函数，适合科学计算。

```python
arr = np.array([1, 2, 3, 4])

# 累积和
cumsum = np.cumsum(arr)
print(cumsum)  # [1, 3, 6, 10]

# 累积积
cumprod = np.cumprod(arr)
print(cumprod)  # [1, 2, 6, 24]

# 快速傅里叶变换 (FFT)
fft = np.fft.fft(arr)
print(fft)

# 梯度计算
gradient = np.gradient(arr)
print(gradient)  # [1., 1., 1., 1.]（均匀间隔）
```

---

#### 7. **内存优化与大数组处理**
处理大数组时，NumPy 提供内存高效的工具。

```python
# 使用 memmap 处理大文件
arr = np.memmap('large_array.dat', dtype='float32', mode='w+', shape=(10000, 10000))
arr[:] = np.random.rand(10000, 10000)
print(arr.shape)  # (10000, 10000)

# 指定数据类型减少内存
arr_float32 = np.array([1, 2, 3], dtype=np.float32)
print(arr_float32.nbytes)  # 12 字节（比默认 float64 小）

# 就地操作
arr = np.array([1, 2, 3])
arr += 10  # 就地加10，节省内存
print(arr)  # [11, 12, 13]
```

---

#### 8. **实际应用示例：数据分析**
以下是一个简单的数据分析示例，展示 NumPy 的实际应用。

```python
# 模拟数据集：1000 个学生的成绩
np.random.seed(42)
scores = np.random.normal(loc=75, scale=10, size=1000)

# 计算统计指标
mean_score = np.mean(scores)
std_score = np.std(scores)
print(f"平均分: {mean_score:.2f}, 标准差: {std_score:.2f}")

# 筛选优秀学生（成绩 > 85）
excellent = scores[scores > 85]
print(f"优秀学生人数: {len(excellent)}")

# 分组统计（按分数段）
bins = np.array([0, 60, 70, 80, 90, 100])
hist, bin_edges = np.histogram(scores, bins=bins)
print("分数分布:", hist)  # 每个区间的学生人数
```

---

#### 9. **与 Pandas 结合**
NumPy 是 Pandas 的底层引擎，结合使用非常常见。

```python
import pandas as pd

# NumPy 数组转为 DataFrame
arr = np.array([[1, 2], [3, 4], [5, 6]])
df = pd.DataFrame(arr, columns=['A', 'B'])
print(df)

# DataFrame 转为 NumPy 数组
np_arr = df.to_numpy()
print(np_arr)
```

---

#### 10. **调试与性能提升**
- **调试**：使用 `np.seterr(all='raise')` 捕获浮点错误。
- **性能**：使用 `@` 运算符进行矩阵乘法，替代 `np.dot` 以提高可读性。
- **向量化**：避免 for 循环，使用 NumPy 的内置函数。
- **并行化**：对于超大数组，考虑结合 `numba` 或 `multiprocessing`。

```python
# 矩阵乘法简写
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(A @ B)  # [[19, 22], [43, 50]]

# 错误捕获
np.seterr(all='raise')
try:
    np.array([1]) / 0
except FloatingPointError:
    print("捕获到除零错误")
```

---
