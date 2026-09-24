---
title: pandas使用教程
description: ""
date: 2025-05-13T11:12:26+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - pandas
    - 教程
---




# Pandas 使用教程


Pandas 是 Python 中一个强大的数据分析和处理库。它提供了高性能、易于使用的数据结构和数据分析工具。本教程将介绍 Pandas 的基本概念和常用操作。

## 1. 安装 Pandas

如果你还没有安装 Pandas，可以使用 pip 进行安装：

```bash
pip install pandas
```

## 2. Pandas 的核心数据结构

Pandas 主要有两种核心数据结构：**Series** 和 **DataFrame**。

### 2.1 Series

Series 是一种一维的、类似数组的对象，能够保存任何数据类型（整数、字符串、浮点数、Python 对象等）。它由一组数据以及一组与之相关的数据标签（即索引）组成。

#### 创建 Series

```python
import pandas as pd
import numpy as np # 通常与 pandas 一起使用

# 从列表创建 Series
data_list = [10, 20, 30, 40, 50]
s1 = pd.Series(data_list)
print("从列表创建的 Series:")
print(s1)
print("-" * 30)

# 指定索引
index_list = ['a', 'b', 'c', 'd', 'e']
s2 = pd.Series(data_list, index=index_list)
print("指定索引的 Series:")
print(s2)
print("-" * 30)

# 从字典创建 Series
data_dict = {'x': 100, 'y': 200, 'z': 300}
s3 = pd.Series(data_dict)
print("从字典创建的 Series:")
print(s3)
print("-" * 30)
```

#### Series 的属性和方法

```python
# 访问元素
print("访问 s2 中的元素 'c':", s2['c'])
print("访问 s2 中前两个元素:\n", s2[:2])
print("-" * 30)

# 属性
print("s2 的索引:", s2.index)
print("s2 的值:", s2.values)
print("s2 的数据类型:", s2.dtype)
print("s2 的形状:", s2.shape)
print("s2 的大小:", s2.size)
print("-" * 30)

# 常用方法
print("s1 的和:", s1.sum())
print("s1 的平均值:", s1.mean())
print("s1 大于 30 的元素:\n", s1[s1 > 30])
print("-" * 30)
```

### 2.2 DataFrame

DataFrame 是一个二维的、表格型的数据结构，它含有一组有序的列，每列可以是不同的值类型（数值、字符串、布尔值等）。DataFrame 既有行索引也有列索引，可以被看作是由 Series 组成的字典。

#### 创建 DataFrame

```python
# 从字典创建 DataFrame (字典的键是列名，值是列表或 Series)
data_df = {
    '姓名': ['张三', '李四', '王五', '赵六'],
    '年龄': [25, 30, 22, 28],
    '城市': ['北京', '上海', '广州', '深圳']
}
df1 = pd.DataFrame(data_df)
print("从字典创建的 DataFrame:")
print(df1)
print("-" * 30)

# 指定行索引
df2 = pd.DataFrame(data_df, index=['a', 'b', 'c', 'd'])
print("指定行索引的 DataFrame:")
print(df2)
print("-" * 30)

# 从列表的列表创建 DataFrame
data_list_of_lists = [
    ['Alice', 25, 'New York'],
    ['Bob', 30, 'London'],
    ['Charlie', 35, 'Paris']
]
df3 = pd.DataFrame(data_list_of_lists, columns=['Name', 'Age', 'City'])
print("从列表的列表创建的 DataFrame:")
print(df3)
print("-" * 30)

# 从 NumPy ndarray 创建 DataFrame
data_np = np.random.randn(4, 3) # 生成 4x3 的随机数数组
df4 = pd.DataFrame(data_np, columns=['A', 'B', 'C'])
print("从 NumPy ndarray 创建的 DataFrame:")
print(df4)
print("-" * 30)
```

## 3. 数据加载与保存

Pandas 可以轻松地从多种文件格式中读取数据，并将数据保存到这些格式中。

### 3.1 读取数据

```python
# 创建一个示例 CSV 文件 (在实际使用中，你通常会有一个已存在的文件)
csv_data = """id,name,score
1,Alice,85
2,Bob,90
3,Charlie,78
"""
with open("example.csv", "w") as f:
    f.write(csv_data)

# 从 CSV 文件读取数据
df_csv = pd.read_csv('example.csv')
print("从 CSV 文件读取的 DataFrame:")
print(df_csv)
print("-" * 30)

# 读取 Excel 文件 (需要安装 openpyxl 或 xlrd 库: pip install openpyxl xlrd)
# 假设你有一个 example.xlsx 文件
# df_excel = pd.read_excel('example.xlsx', sheet_name='Sheet1')
# print("从 Excel 文件读取的 DataFrame:")
# print(df_excel)
# print("-" * 30)

# 读取 JSON 文件
# json_data = """
# [
#   {"id": 1, "name": "David", "score": 92},
#   {"id": 2, "name": "Eve", "score": 88}
# ]
# """
# with open("example.json", "w") as f:
#     f.write(json_data)
# df_json = pd.read_json('example.json')
# print("从 JSON 文件读取的 DataFrame:")
# print(df_json)
# print("-" * 30)
```

### 3.2 保存数据

```python
# 将 DataFrame 保存到 CSV 文件
df1.to_csv('output.csv', index=False) # index=False 表示不将行索引写入文件
print("df1 已保存到 output.csv")
print("-" * 30)

# 将 DataFrame 保存到 Excel 文件
# df1.to_excel('output.xlsx', sheet_name='Data', index=False)
# print("df1 已保存到 output.xlsx")
# print("-" * 30)

# 将 DataFrame 保存到 JSON 文件
# df1.to_json('output.json', orient='records', lines=True) # orient='records' 每行一个 JSON 对象
# print("df1 已保存到 output.json")
# print("-" * 30)
```

## 4. 数据查看与选择

### 4.1 查看数据

```python
print("查看 df1 的前几行 (默认 5 行):")
print(df1.head())
print("-" * 30)

print("查看 df1 的后几行 (默认 5 行):")
print(df1.tail(3)) # 查看后 3 行
print("-" * 30)

print("查看 df1 的索引:")
print(df1.index)
print("-" * 30)

print("查看 df1 的列名:")
print(df1.columns)
print("-" * 30)

print("查看 df1 的数据类型:")
print(df1.dtypes)
print("-" * 30)

print("查看 df1 的形状 (行数, 列数):")
print(df1.shape)
print("-" * 30)

print("获取 df1 的描述性统计信息:")
print(df1.describe(include='all')) # include='all' 包括非数值列
print("-" * 30)

print("获取 df1 的简要信息:")
df1.info()
print("-" * 30)
```

### 4.2 选择数据

Pandas 提供了多种选择数据的方式。

#### 选择列

```python
# 选择单列 (返回 Series)
ages = df1['年龄']
print("选择 '年龄' 列:")
print(ages)
print(type(ages))
print("-" * 30)

# 选择多列 (返回 DataFrame)
name_city = df1[['姓名', '城市']]
print("选择 '姓名' 和 '城市' 列:")
print(name_city)
print(type(name_city))
print("-" * 30)
```

#### 选择行

##### `loc`: 基于标签的索引

```python
print("使用 df2 (有自定义行索引):")
print(df2)
print("-" * 30)

# 选择单行
row_b = df2.loc['b']
print("选择行 'b':")
print(row_b)
print("-" * 30)

# 选择多行
rows_ac = df2.loc[['a', 'c']]
print("选择行 'a' 和 'c':")
print(rows_ac)
print("-" * 30)

# 选择行和列
name_age_b = df2.loc['b', ['姓名', '年龄']]
print("选择行 'b' 的 '姓名' 和 '年龄':")
print(name_age_b)
print("-" * 30)

# 选择所有行的特定列
all_rows_name_age = df2.loc[:, ['姓名', '年龄']]
print("选择所有行的 '姓名' 和 '年龄':")
print(all_rows_name_age)
print("-" * 30)
```

##### `iloc`: 基于整数位置的索引

```python
print("使用 df1 (默认整数行索引):")
print(df1)
print("-" * 30)

# 选择第一行 (位置 0)
row_0 = df1.iloc[0]
print("选择第一行:")
print(row_0)
print("-" * 30)

# 选择前两行 (位置 0 和 1)
rows_01 = df1.iloc[[0, 1]] # 或 df1.iloc[0:2]
print("选择前两行:")
print(rows_01)
print("-" * 30)

# 选择第一行、第一列的元素
element_00 = df1.iloc[0, 0]
print("选择第一行、第一列的元素:", element_00)
print("-" * 30)

# 选择特定行和列
subset_iloc = df1.iloc[[0, 2], [0, 1]] # 第 0, 2 行 和 第 0, 1 列
print("选择特定行和列:")
print(subset_iloc)
print("-" * 30)
```

#### 条件选择 (布尔索引)

```python
# 选择年龄大于 25 的行
older_than_25 = df1[df1['年龄'] > 25]
print("年龄大于 25 的行:")
print(older_than_25)
print("-" * 30)

# 组合条件 (使用 & 表示 AND, | 表示 OR)
condition = (df1['年龄'] > 25) & (df1['城市'] == '深圳')
filtered_df = df1[condition]
print("年龄大于 25 且城市为深圳的行:")
print(filtered_df)
print("-" * 30)

# 使用 isin() 方法
cities_of_interest = ['北京', '深圳']
df_in_cities = df1[df1['城市'].isin(cities_of_interest)]
print("城市为北京或深圳的行:")
print(df_in_cities)
print("-" * 30)
```

## 5. 数据清洗

数据清洗是数据分析中非常重要的一步。

### 5.1 处理缺失值 (NaN)

```python
# 创建一个包含缺失值的 DataFrame
data_missing = {
    'A': [1, 2, np.nan, 4],
    'B': [5, np.nan, np.nan, 8],
    'C': [9, 10, 11, 12],
    'D': [np.nan, np.nan, np.nan, np.nan]
}
df_missing = pd.DataFrame(data_missing)
print("包含缺失值的 DataFrame:")
print(df_missing)
print("-" * 30)

# 检查缺失值
print("检查每列是否有缺失值:")
print(df_missing.isnull()) # 返回布尔型 DataFrame
print("-" * 30)
print("统计每列缺失值的数量:")
print(df_missing.isnull().sum())
print("-" * 30)

# 删除包含缺失值的行或列
# 删除任何包含 NaN 的行
df_dropped_rows = df_missing.dropna()
print("删除包含 NaN 的行后的 DataFrame:")
print(df_dropped_rows)
print("-" * 30)

# 删除任何包含 NaN 的列
df_dropped_cols = df_missing.dropna(axis=1) # axis=1 表示按列操作
print("删除包含 NaN 的列后的 DataFrame:")
print(df_dropped_cols)
print("-" * 30)

# 删除所有值都为 NaN 的列
df_dropped_all_nan_cols = df_missing.dropna(axis=1, how='all')
print("删除所有值都为 NaN 的列后的 DataFrame:")
print(df_dropped_all_nan_cols)
print("-" * 30)

# 填充缺失值
# 用特定值填充所有 NaN
df_filled_zero = df_missing.fillna(0)
print("用 0 填充所有 NaN 后的 DataFrame:")
print(df_filled_zero)
print("-" * 30)

# 用列的平均值填充 NaN (仅对数值列有效)
df_filled_mean_A = df_missing.copy() # 创建副本以避免修改原始 DataFrame
df_filled_mean_A['A'] = df_filled_mean_A['A'].fillna(df_filled_mean_A['A'].mean())
print("用列 'A' 的平均值填充 NaN 后的 DataFrame:")
print(df_filled_mean_A)
print("-" * 30)

# 使用前一个有效值填充 (向前填充)
df_ffill = df_missing.fillna(method='ffill')
print("向前填充后的 DataFrame:")
print(df_ffill)
print("-" * 30)

# 使用后一个有效值填充 (向后填充)
df_bfill = df_missing.fillna(method='bfill')
print("向后填充后的 DataFrame:")
print(df_bfill)
print("-" * 30)
```

### 5.2 处理重复数据

```python
data_duplicates = {
    'col1': ['A', 'B', 'A', 'C', 'B', 'B'],
    'col2': [1, 2, 1, 3, 2, 2]
}
df_duplicates = pd.DataFrame(data_duplicates)
print("包含重复数据的 DataFrame:")
print(df_duplicates)
print("-" * 30)

# 检查重复行
print("检查重复行 (除第一次出现外，其余标记为 True):")
print(df_duplicates.duplicated())
print("-" * 30)

# 删除重复行 (默认保留第一个出现的)
df_no_duplicates = df_duplicates.drop_duplicates()
print("删除重复行后的 DataFrame:")
print(df_no_duplicates)
print("-" * 30)

# 删除重复行 (保留最后一个出现的)
df_no_duplicates_last = df_duplicates.drop_duplicates(keep='last')
print("删除重复行 (保留最后一个) 后的 DataFrame:")
print(df_no_duplicates_last)
print("-" * 30)

# 基于特定列删除重复项
df_no_duplicates_subset = df_duplicates.drop_duplicates(subset=['col1'])
print("基于 'col1' 删除重复项后的 DataFrame:")
print(df_no_duplicates_subset)
print("-" * 30)
```

### 5.3 数据类型转换

```python
print("df1 的数据类型:")
print(df1.dtypes)
print("-" * 30)

# 将 '年龄' 列转换为浮点数
df_copy = df1.copy()
df_copy['年龄'] = df_copy['年龄'].astype(float)
print("将 '年龄' 列转换为浮点数后的数据类型:")
print(df_copy.dtypes)
print(df_copy)
print("-" * 30)

# 处理可能出现的错误 (例如，将包含非数字的字符串列转换为数字)
df_error = pd.DataFrame({'vals': ['1', '2', 'apple', '4']})
# df_error['vals'] = df_error['vals'].astype(int) # 这会报错
df_error['vals_numeric'] = pd.to_numeric(df_error['vals'], errors='coerce') # 'coerce' 会将无法转换的值设为 NaT 或 NaN
print("使用 to_numeric 处理转换错误:")
print(df_error)
print("-" * 30)
```

## 6. 数据操作

### 6.1 添加和删除列

```python
# 添加新列
df_copy = df1.copy()
df_copy['职业'] = ['工程师', '医生', '学生', '教师'] # 列表长度需与行数一致
print("添加 '职业' 列后的 DataFrame:")
print(df_copy)
print("-" * 30)

df_copy['工龄'] = 0 # 添加值为常量的列
print("添加 '工龄' 列后的 DataFrame:")
print(df_copy)
print("-" * 30)

# 基于现有列创建新列
df_copy['年龄_加五'] = df_copy['年龄'] + 5
print("添加 '年龄_加五' 列后的 DataFrame:")
print(df_copy)
print("-" * 30)

# 删除列
df_dropped_city = df_copy.drop('城市', axis=1) # axis=1 表示删除列, inplace=True 可以直接修改原 DataFrame
print("删除 '城市' 列后的 DataFrame:")
print(df_dropped_city)
print("-" * 30)

# 删除多列
df_dropped_multi = df_copy.drop(['职业', '工龄'], axis=1)
print("删除 '职业' 和 '工龄' 列后的 DataFrame:")
print(df_dropped_multi)
print("-" * 30)
```

### 6.2 应用函数 (apply, map, applymap)

#### `apply()`
可以作用于行或列。

```python
df_apply = df1[['年龄']].copy() # 只取年龄列，方便演示
print("原始 '年龄' 列:")
print(df_apply)
print("-" * 30)

# 对列应用函数
def square(x):
    return x * x

df_apply['年龄平方_apply_col'] = df_apply['年龄'].apply(square)
print("对 '年龄' 列应用 square 函数:")
print(df_apply)
print("-" * 30)

# 对行应用函数 (通常与 lambda 函数结合)
df_numeric_data = pd.DataFrame(np.random.randn(3, 3), columns=['A', 'B', 'C'])
print("数值型 DataFrame:")
print(df_numeric_data)
df_numeric_data['Row_Sum'] = df_numeric_data.apply(lambda row: row.sum(), axis=1)
print("对行应用求和函数:")
print(df_numeric_data)
print("-" * 30)
```

#### `map()`
作用于 Series 的每个元素。

```python
s_map = df1['城市'].copy()
city_mapping = {'北京': 'BJ', '上海': 'SH', '广州': 'GZ', '深圳': 'SZ'}
s_map_transformed = s_map.map(city_mapping)
print("原始 '城市' Series:")
print(s_map)
print("使用 map 转换后的 '城市' Series:")
print(s_map_transformed)
print("-" * 30)

# 如果映射字典中没有某个键，则对应元素会变为 NaN
s_map_partial = pd.Series(['北京', '上海', '成都'])
s_map_partial_transformed = s_map_partial.map(city_mapping)
print("部分映射:")
print(s_map_partial_transformed)
print("-" * 30)
```

#### `applymap()`
作用于 DataFrame 的每个元素。

```python
df_applymap_data = df1[['年龄']].copy() # 使用数值列
print("原始 DataFrame (年龄):")
print(df_applymap_data)
df_applymap_transformed = df_applymap_data.applymap(lambda x: x + 10) # DataFrame 中所有元素加 10
print("使用 applymap 将所有元素加 10:")
print(df_applymap_transformed)
print("-" * 30)
```

### 6.3 排序

```python
# 按索引排序
df_sorted_index = df2.sort_index(ascending=False) # 按行索引降序
print("按行索引降序排序:")
print(df_sorted_index)
print("-" * 30)

df_sorted_columns = df1.sort_index(axis=1, ascending=True) # 按列名升序
print("按列名升序排序:")
print(df_sorted_columns)
print("-" * 30)

# 按值排序
df_sorted_age = df1.sort_values(by='年龄', ascending=False)
print("按 '年龄' 降序排序:")
print(df_sorted_age)
print("-" * 30)

# 按多列排序
df_sorted_city_age = df1.sort_values(by=['城市', '年龄'], ascending=[True, False])
print("按 '城市'(升序) 和 '年龄'(降序) 排序:")
print(df_sorted_city_age)
print("-" * 30)
```

## 7. 分组 (Group By)

分组操作通常涉及以下一个或多个步骤：
- **分割 (Splitting)**: 根据某些条件将数据分成组。
- **应用 (Applying)**: 对每个组独立应用一个函数。
- **合并 (Combining)**: 将结果组合成一个数据结构。

```python
data_sales = {
    'Store': ['A', 'B', 'A', 'B', 'A', 'C', 'B', 'C'],
    'Product': ['Apple', 'Banana', 'Orange', 'Apple', 'Banana', 'Orange', 'Orange', 'Apple'],
    'Sales': [100, 150, 80, 90, 120, 70, 130, 60],
    'Quantity': [10, 15, 8, 9, 12, 7, 13, 6]
}
df_sales = pd.DataFrame(data_sales)
print("销售数据 DataFrame:")
print(df_sales)
print("-" * 30)

# 按 'Store' 分组并计算每家店的总销售额
grouped_by_store_sales = df_sales.groupby('Store')['Sales'].sum()
print("按 'Store' 分组计算总销售额:")
print(grouped_by_store_sales)
print(type(grouped_by_store_sales)) # 返回 Series
print("-" * 30)

# 按 'Store' 分组并计算每家店的平均销售额和总数量
grouped_by_store_agg = df_sales.groupby('Store').agg({'Sales': 'mean', 'Quantity': 'sum'})
print("按 'Store' 分组计算平均销售额和总数量:")
print(grouped_by_store_agg)
print(type(grouped_by_store_agg)) # 返回 DataFrame
print("-" * 30)

# 按多个列分组
grouped_by_store_product = df_sales.groupby(['Store', 'Product'])['Sales'].sum()
print("按 'Store' 和 'Product' 分组计算总销售额:")
print(grouped_by_store_product) # 返回多级索引的 Series
print("-" * 30)

# 分组后迭代
for name, group in df_sales.groupby('Store'):
    print(f"Store: {name}")
    print(group)
    print("-" * 10)
print("-" * 30)

# 分组后应用自定义函数
def top_sales_product(df_group):
    return df_group.sort_values(by='Sales', ascending=False).iloc[0]

top_product_by_store = df_sales.groupby('Store').apply(top_sales_product)
print("每家店销售额最高的产品记录:")
print(top_product_by_store)
print("-" * 30)
```

## 8. 合并与连接 (Merge, Join, Concat)

### 8.1 `concat()`: 拼接

用于沿某个轴将多个 Pandas 对象（Series 或 DataFrame）拼接在一起。

```python
df_c1 = pd.DataFrame({'A': ['A0', 'A1'], 'B': ['B0', 'B1']})
df_c2 = pd.DataFrame({'A': ['A2', 'A3'], 'B': ['B2', 'B3']})
df_c3 = pd.DataFrame({'C': ['C0', 'C1'], 'D': ['D0', 'D1']})

# 沿行拼接 (默认 axis=0)
concatenated_rows = pd.concat([df_c1, df_c2])
print("沿行拼接 df_c1 和 df_c2:")
print(concatenated_rows)
print("-" * 30)

# 沿行拼接，忽略原始索引并重置索引
concatenated_rows_reset_index = pd.concat([df_c1, df_c2], ignore_index=True)
print("沿行拼接并重置索引:")
print(concatenated_rows_reset_index)
print("-" * 30)

# 沿列拼接 (axis=1)
concatenated_cols = pd.concat([df_c1, df_c3], axis=1)
print("沿列拼接 df_c1 和 df_c3:")
print(concatenated_cols)
print("-" * 30)
```

### 8.2 `merge()`: 数据库风格的连接

根据一个或多个键将 DataFrame 的行连接起来。

```python
left = pd.DataFrame({
    'key': ['K0', 'K1', 'K2', 'K3'],
    'A': ['A0', 'A1', 'A2', 'A3'],
    'B': ['B0', 'B1', 'B2', 'B3']
})
right = pd.DataFrame({
    'key': ['K0', 'K1', 'K4', 'K5'],
    'C': ['C0', 'C1', 'C2', 'C3'],
    'D': ['D0', 'D1', 'D2', 'D3']
})
print("Left DataFrame:")
print(left)
print("Right DataFrame:")
print(right)
print("-" * 30)

# 内连接 (Inner Join - 默认): 基于 'key' 列的交集
merged_inner = pd.merge(left, right, on='key')
print("内连接结果:")
print(merged_inner)
print("-" * 30)

# 左连接 (Left Join): 使用左边 DataFrame 的所有键
merged_left = pd.merge(left, right, on='key', how='left')
print("左连接结果:")
print(merged_left)
print("-" * 30)

# 右连接 (Right Join): 使用右边 DataFrame 的所有键
merged_right = pd.merge(left, right, on='key', how='right')
print("右连接结果:")
print(merged_right)
print("-" * 30)

# 外连接 (Outer Join): 使用两个 DataFrame 键的并集
merged_outer = pd.merge(left, right, on='key', how='outer')
print("外连接结果:")
print(merged_outer)
print("-" * 30)

# 基于不同列名的键合并
left_diff_key = pd.DataFrame({'lkey': ['K0', 'K1'], 'A': ['A0', 'A1']})
right_diff_key = pd.DataFrame({'rkey': ['K0', 'K1'], 'C': ['C0', 'C1']})
merged_diff_keys = pd.merge(left_diff_key, right_diff_key, left_on='lkey', right_on='rkey')
print("基于不同列名合并:")
print(merged_diff_keys)
print("-" * 30)
```

### 8.3 `join()`: 基于索引的连接

`join()` 方法用于基于索引或指定列将两个 DataFrame 连接起来。默认情况下，它尝试按索引进行左连接。

```python
left_join_df = pd.DataFrame(
    {'A': ['A0', 'A1', 'A2']},
    index=['K0', 'K1', 'K2']
)
right_join_df = pd.DataFrame(
    {'B': ['B0', 'B1', 'B2']},
    index=['K0', 'K1', 'K3'] # K2 不同
)
print("Left Join DataFrame:")
print(left_join_df)
print("Right Join DataFrame:")
print(right_join_df)
print("-" * 30)

# 默认左连接 (基于索引)
joined_df = left_join_df.join(right_join_df)
print("默认左连接结果:")
print(joined_df)
print("-" * 30)

# 外连接 (how='outer')
joined_outer_df = left_join_df.join(right_join_df, how='outer')
print("外连接结果:")
print(joined_outer_df)
print("-" * 30)

# 在列上连接 (需要先将列设置为索引)
left_on_col = pd.DataFrame({
    'key': ['K0', 'K1', 'K2'],
    'A': ['A0', 'A1', 'A2']
})
right_on_col = pd.DataFrame({
    'other_key': ['K0', 'K1', 'K3'],
    'B': ['B0', 'B1', 'B2']
})
joined_on_key = left_on_col.join(right_on_col.set_index('other_key'), on='key')
print("在 'key' 和 'other_key' 列上连接:")
print(joined_on_key)
print("-" * 30)
```

## 9. 时间序列数据

Pandas 在处理时间序列数据方面非常强大。

```python
# 创建日期范围
date_rng = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D') # 每天
print("日期范围:")
print(date_rng)
print("-" * 30)

# 创建一个带时间索引的 Series
time_series = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
print("时间序列数据:")
print(time_series)
print("-" * 30)

# 创建一个带时间索引的 DataFrame
df_time = pd.DataFrame({'value': np.random.randint(0, 100, len(date_rng))}, index=date_rng)
df_time['day_of_week'] = df_time.index.day_name()
print("带时间索引的 DataFrame:")
print(df_time)
print("-" * 30)

# 选择特定日期的数据
print("选择 2024-01-05 的数据:")
print(df_time.loc['2024-01-05'])
print("-" * 30)

# 选择日期范围的数据
print("选择 2024-01-03 到 2024-01-07 的数据:")
print(df_time['2024-01-03':'2024-01-07'])
print("-" * 30)

# 重采样 (Resampling) - 例如，按周汇总数据
weekly_sum = df_time['value'].resample('W').sum() # 'W' 表示每周
print("按周汇总的总值:")
print(weekly_sum)
print("-" * 30)

# 移动窗口计算 (Moving Window Calculations)
df_time['rolling_mean_3D'] = df_time['value'].rolling(window=3).mean() # 3 天的移动平均值
print("带 3 天移动平均值的 DataFrame:")
print(df_time)
print("-" * 30)
```

## 10. 绘图 (Plotting)

Pandas 可以与 Matplotlib 集成，方便地绘制图表。 (需要安装 `matplotlib`: `pip install matplotlib`)

```python
import matplotlib.pyplot as plt

# Series 绘图
ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2020', periods=1000))
ts = ts.cumsum() # 累积和
ts.plot()
plt.title("Random Walk Time Series")
plt.show() # 在脚本中运行时需要此行来显示图形

# DataFrame 绘图
df_plot = pd.DataFrame(np.random.randn(10, 4), columns=['A', 'B', 'C', 'D'])
df_plot.plot(kind='bar') # 柱状图
plt.title("DataFrame Bar Plot")
plt.show()

df_sales.groupby('Store')['Sales'].sum().plot(kind='pie', autopct='%1.1f%%')
plt.title("Sales by Store")
plt.ylabel('') # 隐藏 y 轴标签
plt.show()
```

这只是 Pandas 功能的冰山一角。Pandas 非常强大，有许多高级功能和用法。建议查阅官方文档以获取更全面的信息：[https://pandas.pydata.org/pandas-docs/stable/](https://pandas.pydata.org/pandas-docs/stable/)









## 使用技巧

###  不同的写csv文件方法
```python
#################################################
#############         csv模块  ##################
#################################################
import csv
# 要写入的数据
data = [
    ['Name', 'Age', 'City'],
    ['John', 30, 'New York'],
    ['Alice', 25, 'Los Angeles'],
    ['Bob', 35, 'Chicago']
]

# 打开CSV文件并写入数据
with open('output.csv', 'w', newline='') as csvfile:
    # 创建一个CSV写入对象
    csv_writer = csv.writer(csvfile)
    
    # 循环写入每一行数据
    for row in data:
        csv_writer.writerow(row)

print("数据已成功写入到 output.csv 文件中。")


#################################################
#############       Pandas     ##################
#################################################

import pandas as pd

# 创建一个DataFrame对象，包含要写入的数据
data = {
    'Name': ['John', 'Alice', 'Bob'],
    'Age': [30, 25, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)

# 将DataFrame写入CSV文件
df.to_csv('output.csv', index=False)

print("数据已成功写入到 output.csv 文件中。")

# 追加写入
new_data = {
    'Name': 'Sarah',
    'Age': 20,
    'City':'toky'
}
df_new = pd.DataFrame(new_data,index=[0])
existing_csv_file  = 'output.csv'
# 将新数据追加到现有的CSV文件中
df_new.to_csv(existing_csv_file, mode='a', header=False, index=False)
```

