---
title: python-lru_cache 缓存装饰器
description: ""
date: 2026-05-29T11:09:25+08:00
image: images/index/index.png
categories:
    - Grammar
tags:
    - python
---


# Python `lru_cache` 缓存装饰器详解

`lru_cache` 是 Python 标准库 `functools` 里的一个**装饰器**，作用很纯粹：

> 记住函数的**入参 → 返回值**，下次同样入参直接返回缓存结果，不再执行函数体。

LRU = **L**east **R**ecently **U**sed（最近最少使用），是它在缓存满时的淘汰策略。

---

## 1. 它解决了什么问题

一个常见的痛点：某个函数纯计算，但比较慢（读盘、解析、网络、递归、DP 子问题等等）。同样入参被反复调用时，每一次都重算一遍，是纯浪费。

```python
import time

def slow_square(x: int) -> int:
    time.sleep(1)
    return x * x

slow_square(3)   # 1 秒
slow_square(3)   # 又 1 秒
slow_square(3)   # 再 1 秒……
```

加上 `lru_cache`：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def slow_square(x: int) -> int:
    time.sleep(1)
    return x * x

slow_square(3)   # 1 秒（miss，真的算）
slow_square(3)   # 0 秒（hit，从缓存取）
slow_square(3)   # 0 秒（hit）
```

---

## 2. 基本用法

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

fib(50)   # 一瞬间出结果；没有 cache 时这是经典指数爆炸
```

- `maxsize=128`：最多记住 128 组不同的 `(入参 → 结果)` 映射。
- 超出后**最久没被命中的那个条目会被踢掉**（这就是 LRU 的"L"和"R"）。
- 缓存挂在**函数对象**上，进程生命周期内一直存在；不同进程之间不共享。

---

## 3. 入参必须是可哈希的

`lru_cache` 内部把入参组成 tuple 当作 dict 的 key，所以入参必须是 **hashable**：

| 可以做 key | 不能做 key |
|---|---|
| `int` / `float` / `str` / `bool` | `list` |
| `tuple`（且其中元素也都可哈希） | `dict` |
| `frozenset` | `set` |
| `bytes` / `None` | 普通可变对象 |
| `pathlib.Path` | `numpy.ndarray` |

传入不可哈希参数时会抛 `TypeError: unhashable type`。

```python
@lru_cache
def bad(x):
    return sum(x)

bad([1, 2, 3])   # TypeError: unhashable type: 'list'
bad((1, 2, 3))   # OK
```

> 关键字参数也会参与 key 计算，并且 `f(1, 2)` 和 `f(1, b=2)` 被当作**不同**的缓存条目——尽量统一调用风格。

---

## 4. 自带的辅助能力

被装饰的函数会多出三个方法：

```python
fib.cache_info()
# CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)

fib.cache_clear()   # 清空整张缓存表
fib.cache_parameters()   # {'maxsize': 128, 'typed': False}（3.9+）
```

- `cache_info()` 调优时很有用：`hits` 远大于 `misses` 才说明缓存值钱。
- `cache_clear()` 是**测试或长跑服务里热更新配置时必备**——下一节会展开。

---

## 5. `maxsize` 和 `typed` 怎么选

```python
@lru_cache(maxsize=None, typed=False)
def f(...): ...
```

- `maxsize=None` 或直接 `@functools.cache`（3.9+）：**无大小上限、无淘汰**。适合"键空间天然有限"的场景，比如解析一份固定文件、有限枚举类型。
- `maxsize=数字`：留个上限防内存爆炸；常用 `128`、`256`、`1024`，按调用模式估。
- `typed=True`：把 `f(1)` 和 `f(1.0)` 当成两个不同 key。默认 `False`，多数情况下不用动。

---

## 6. 实战例子：缓存配置文件解析

我在自己的项目里用 `lru_cache` 包装一个读取 TOML 配置的函数：

```python
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=4)
def load_models_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """加载 config.toml 中的 [models] section，并缓存解析结果。"""
    resolved_path = Path(config_path) if config_path else DEFAULT_TOML
    with open(resolved_path, "rb") as toml_file_handle:
        raw_toml_data = tomllib.load(toml_file_handle)
    return raw_toml_data.get("models", {})
```

收益：

- 长跑进程（API server、Agent runtime）里同样的配置可能被读上百次，加 cache 后只读盘一次。
- `maxsize=4` 是保守值——默认 key 只有 `None`（默认路径），留三个余量给测试或自定义路径。

---

## 7. 三个常见陷阱

### 7.1 返回的是同一个对象，不是拷贝

```python
@lru_cache
def get_settings() -> dict[str, Any]:
    return {"db_url": "postgres://..."}

cfg = get_settings()
cfg["db_url"] = "evil"   # ⚠️ 改的是缓存里的那个 dict

get_settings()["db_url"]   # 'evil'，已经被污染
```

**对策**：要么让函数返回不可变结构（`frozendict`、`tuple`、`@dataclass(frozen=True)`），要么在调用方拿到后立刻 `copy.deepcopy`，要么明确约定"只读"。

### 7.2 外部状态变了，缓存不会感知

```python
@lru_cache
def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

read_file("config.toml")   # 读到 v1
# ... 文件被改了 ...
read_file("config.toml")   # 还是 v1！
```

`lru_cache` 只看入参，不看文件 mtime、不看时间戳。**热重载场景不能用 `lru_cache`**；要么换成手动管理的缓存层 + watchdog，要么手动 `cache_clear()`。

### 7.3 测试之间缓存会泄漏

pytest 跑在同一个 Python 进程里，模块级别的 `@lru_cache` 函数缓存会跨测试残留。前一个测试用 `tmp_path` 写入的配置，可能被后一个测试当作"默认配置"读到。

**对策**：写一个 autouse fixture 在每个测试前清缓存。

```python
@pytest.fixture(autouse=True)
def _clear_models_config_cache() -> None:
    load_models_config.cache_clear()
```

---

## 8. `lru_cache` vs `functools.cache`（3.9+）

```python
from functools import cache, lru_cache

@cache                     # 等价于 lru_cache(maxsize=None)
def f(x): ...

@lru_cache(maxsize=128)    # 有上限，会淘汰
def g(x): ...
```

- `@cache`：写法最简洁；无上限、无 LRU 淘汰、有内存风险。键空间小、可控时用它。
- `@lru_cache(maxsize=...)`：键空间不确定、可能膨胀时用它，留一道保险。

---

## 9. 在类的方法上慎用

```python
class Service:
    @lru_cache(maxsize=128)
    def expensive(self, x: int) -> int:
        ...
```

这种写法**会把 `self` 也作为 cache key 的一部分**，看上去能跑，但有两个副作用：

1. 每个 `Service` 实例都有自己一份缓存（其实是 method 共享一张表、按 `self` 隔离）。
2. **缓存会持有 `self` 的强引用**，让本来该被回收的实例无法被 GC——是个隐蔽的内存泄漏。

更稳妥的做法：把要缓存的部分**抽成模块级函数**（不依赖 `self`），或者用第三方库 `cachetools` 的 `@cachedmethod`。

---

## 10. 一图小结

| 场景 | 推荐做法 |
|---|---|
| 纯计算函数、入参 hashable | `@lru_cache(maxsize=128)` |
| 入参取值空间小、不会膨胀 | `@functools.cache` |
| 入参里有 `list` / `dict` | 先把它转 `tuple` / `frozenset` 再缓存，或不用 cache |
| 文件 / 配置可能被外部改 | 不要用 `lru_cache`，自己管理失效 |
| 测试之间不能共享缓存 | autouse fixture 调 `.cache_clear()` |
| 实例方法 | 抽成模块级函数，或换 `cachetools.cachedmethod` |

`lru_cache` 是 Python 里"用最少的代码换到最多的性能"的几个工具之一，但用之前最好先想清楚两件事：

1. **同样入参真的会被反复调用吗？** 如果不会，加 cache 只是徒增复杂度。
2. **被缓存的返回值是否安全共享？** 是否需要担心调用方误改、外部状态过期、`self` 泄漏？

想清楚这两点，再决定要不要加 `@lru_cache`。
