---
title: Typer + Rich 入门教程
description: 用 Typer 写 CLI、用 Rich 美化输出,Python 命令行工具的最佳拍档
date: 2026-06-09T15:30:00+08:00
slug: Typer和Rich入门教程
image: images/index/index.png
draft: false
categories:
    - Library
tags:
    - Python_Lib
    - Typer
    - Rich
    - CLI
---

最近在写一个运维工具,翻了一圈 Python 写 CLI 的库,最后选了 **Typer + Rich**。这套组合的好处是:用类型注解写 CLI,自动拿到漂亮的 help 页面、参数解析、子命令,基本不用自己处理模板代码。这篇把学习过程整理一下,适合第一次用 Typer 的同学。

-----

## 目录

- [为什么是 Typer + Rich](#为什么是-typer--rich)
- [五分钟上手](#五分钟上手)
- [核心概念](#核心概念)
  - [Arguments:必填位置参数](#arguments必填位置参数)
  - [Options:可选命名参数](#options可选命名参数)
  - [错误处理](#错误处理)
- [子命令:嵌套 Typer 应用](#子命令嵌套-typer-应用)
- [Rich 怎么用](#rich-怎么用)
  - [自动部分(零配置)](#自动部分零配置)
  - [手动部分:画表格](#手动部分画表格)
  - [进度条 / JSON / Markdown](#进度条--json--markdown)
- [实战里常用的几个模式](#实战里常用的几个模式)
  - [eager `--version`](#eager---version)
  - [配置默认值 + flag 覆盖](#配置默认值--flag-覆盖)
  - [`--dry-run` 模式](#-dry-run-模式)
- [排错小抄](#排错小抄)
- [一页速查代码](#一页速查代码)
- [练习题](#练习题)
- [参考资料](#参考资料)

-----

## 为什么是 Typer + Rich

- **Typer**:基于 Click,用 Python **类型注解**构建 CLI。help 文本、参数解析、子命令、shell completion 都是开箱即用。
- **Rich**:终端美化库。Typer 内置 Rich 集成,所以你看到的 `╭─╮` 框线、分组的 Options/Commands 面板、错误高亮全是 Rich 自动渲染的,不用自己写一行 Rich 代码。Rich 自己还能画表格、进度条、Markdown、JSON 语法高亮等。

两个库配合,Python 写 CLI 的体验接近 `cargo` / `npm` 这种专业工具。

-----

## 五分钟上手

最小可运行的 CLI,五行就够:

```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    """Say hello to NAME."""
    typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```

保存为 `demo.py`,运行 `python demo.py Alice` → `Hello, Alice!`。
加 `--help` 就能看到 Rich 渲染的 help 页面,**零额外配置**。

-----

## 核心概念

### Arguments:必填位置参数

```python
@app.command()
def deploy(env: str, version: str):
    """Deploy VERSION to ENV."""
    ...
```

调用:`deploy prod v1.2.0`。少传任何一个,Typer 都会报错并提示。

### Options:可选命名参数

```python
@app.command()
def deploy(
    env: str,
    version: str,
    region: str = typer.Option("us-east-1", help="AWS region."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only."),
    verbose: int = typer.Option(0, "-v", count=True, help="Verbosity level."),
):
    ...
```

调用:

```bash
deploy prod v1.2.0 --region eu-west-1 --dry-run -vvv
```

几个关键点:

| 写法 | 含义 |
|---|---|
| `param: str` | 必填位置参数 |
| `param: str = typer.Option("default")` | 有默认值的 option |
| `param: bool = typer.Option(False, "--dry-run")` | flag,出现即 True |
| `param: int = typer.Option(0, "-v", count=True)` | 短选项,支持 `-v -v -v` 累加 |
| `typer.Option(..., help="...")` | 参数的 help 文本 |
| 函数 docstring 第一段 | 命令的简介 |

**类型注解决定一切** — `str` 收字符串,`int` 收整数,`bool` 自动变 flag,`Path` 自动转 `pathlib.Path`,`Literal["a","b"]` 限制枚举。

### 错误处理

```python
@app.command()
def deploy(env: str):
    if env not in {"dev", "staging", "prod"}:
        raise typer.BadParameter(f"unknown env: {env}")
    ...
```

`typer.BadParameter` 和 `typer.Exit(code=1)` 是 Typer 的标准错误出口,会自动用红色打印并以非零码退出。

-----

## 子命令:嵌套 Typer 应用

复杂 CLI 一般会拆成多个子命令,像 `git` 那样:

```
mycli db backup
mycli db list
mycli env provision
mycli logs tail
```

实现方式是 **每个子域一个 Typer 应用,再挂到主应用上**。

```python
# mycli/cli.py
import typer
from mycli.db import cli as db_cli
from mycli.env import cli as env_cli
from mycli.logs import cli as logs_cli

app = typer.Typer(
    name="mycli",
    no_args_is_help=True,   # 不带子命令时显示 help
    add_completion=False,   # 关闭自动安装 shell completion 的提示
)

app.add_typer(db_cli.app,  name="db",   help="Database operations.")
app.add_typer(env_cli.app, name="env",  help="Environment provisioning.")
app.add_typer(logs_cli.app, name="logs", help="Log utilities.")
```

```python
# mycli/db/cli.py
import typer
app = typer.Typer(no_args_is_help=True, add_completion=False)

@app.command("backup")
def backup_command(...):
    """Back up the database."""
    ...

@app.command("list")
def list_command(...):
    """List recent backup runs."""
    ...
```

模式要点:

- 子命令文件独立,各自定义一个 `app = typer.Typer(...)`。
- `add_typer(..., name="db")` 决定子命令的拼写。
- `add_completion=False` 在子应用里也建议加上,避免每个子命令都重复提示装 completion。

-----

## Rich 怎么用

### 自动部分(零配置)

`--help`、参数错误、未识别命令 — Typer 自动用 Rich 渲染,免费拿到好看的 help 和红字报错。

### 手动部分:画表格

```python
from rich.console import Console
from rich.table import Table

console = Console()

@app.command()
def status():
    """Show service status."""
    table = Table(title="Service Status")
    table.add_column("Name", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Uptime", justify="right")
    table.add_row("api", "running", "12d 4h")
    table.add_row("worker", "stopped", "—")
    console.print(table)
```

效果:

```
              Service Status
┏━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Name   ┃ State     ┃ Uptime  ┃
┡━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ api    │ running   │  12d 4h │
│ worker │ stopped   │       — │
└────────┴───────────┴─────────┘
```

`column` 的 `style=` 可以指定颜色,`justify="right"` 控制对齐,`add_row` 一行行加数据。

### 进度条 / JSON / Markdown

```python
from rich.progress import track
from rich.json import JSON
from rich.markdown import Markdown

for item in track(items, description="Processing..."):
    do_work(item)

console.print(JSON('{"a": 1}'))
console.print(Markdown("# title\n*body*"))
```

-----

## 实战里常用的几个模式

### eager `--version`

`--version` 需要在子命令参数解析前就生效,否则 `mycli --version db backup` 会被当成"先解析 db backup,再回头看 --version"。

写法是 `is_eager=True` + callback 抛 `typer.Exit()`:

```python
def _print_version_and_exit(value: bool) -> None:
    if value:
        typer.echo(f"mycli {__version__}")
        raise typer.Exit()

@app.callback()
def _main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V",
        is_eager=True,
        callback=_print_version_and_exit,
        help="Show version and exit.",
    ),
) -> None:
    return None
```

### 配置默认值 + flag 覆盖

CLI 工具经常要从 `.env` 读配置,又要允许 flag 显式覆盖。最简单的写法是用一个 `_resolve` 辅助函数:

```python
def _resolve(value: Optional[str], default: str) -> str:
    return value if value is not None and value != "" else default
```

然后每个 Option 都写成 `Optional[str] = typer.Option(None, ...)`,命令体里统一用 `_resolve(cli_flag, settings.field)` 决定最终值:

- 没传 flag → 用 `.env` 里的配置
- 传了 flag → 覆盖配置
- `.env` 也没设 → 用代码里的 default

> **坑提醒**:别把 `default=settings.field` 写到 Option 上 — Python 的默认参数是在 import 时求值的,不在运行命令的工作目录,容易踩到。

### `--dry-run` 模式

```python
dry_run: bool = typer.Option(False, "--dry-run", help="...")

def run(plan, dry_run: bool):
    if dry_run:
        console.print("[yellow]DRY RUN[/yellow] — no network calls")
        console.print(plan)
        return
    do_real_work(plan)
```

CI / smoke test 里非常有用 — `--dry-run` 不打网络也能验证命令链路。

-----

## 排错小抄

| 现象 | 原因 / 修法 |
|---|---|
| `--help` 显示一坨不分组 | 老版本 Typer;升级到 0.12+ 并装 Rich |
| 中文 help 乱码 | 终端编码不是 UTF-8;`export LANG=en_US.UTF-8` |
| `typer.Option(None, ...)` 拿不到 None | 漏 `from __future__ import annotations` 或没标注 `Optional` |
| 子命令 help 不显示 | 子 `Typer()` 没设 `no_args_is_help=True` |
| `--version` 在子命令里被吞 | 缺 `is_eager=True` + `callback` 抛 `typer.Exit()` |
| default 用配置项不生效 | Python 默认参数在 import 时求值,改用 `_resolve` 模式 |

-----

## 一页速查代码

```python
import typer
from typing import Optional
from rich.console import Console

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()

@app.command()
def greet(
    name: str,                                              # 必填位置参数
    greeting: str = typer.Option("Hi", "-g", help="..."),   # 可选 option
    repeat: int = typer.Option(1, "-r", help="..."),        # 数字
    loud: bool = typer.Option(False, "--loud", help="..."), # flag
):
    """Say GREETING to NAME."""
    msg = f"{greeting}, {name}!"
    if loud:
        msg = msg.upper()
    console.print(msg * repeat)

if __name__ == "__main__":
    app()
```

-----

## 练习题

学完上面这些,推荐按顺序做四道题,做完基本就掌握了:

1. 写一个 `notes add <text>` / `notes list` 的小型 CLI(用 JSON 文件存)。
2. 给 `notes list` 加一个 `--tag` 过滤 option,类型用 `Optional[str]`。
3. 用 `rich.table.Table` 把 `notes list` 渲染成表格。
4. 加一个 `--export json|csv` option,用 `rich.json.JSON` 或自己拼 CSV。

-----

## 参考资料

- Typer 官方文档: <https://typer.tiangolo.com/>
- Rich 官方文档: <https://rich.readthedocs.io/>
- 实战参考:可以找一个真实的 Python CLI 项目翻一翻,比如 `pipx`、`httpie`、`poetry` 这些开源工具的源码,看它们怎么组织子命令、怎么用 Rich 画表格,比自己闭门造车快得多。
