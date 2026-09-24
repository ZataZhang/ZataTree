---
title: python开发环境配置指南
description: ""
date: 2026-01-25T19:39:45+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - Python_Lib
---




最快安装命令合集如下

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop install git  ## 注意要按指示执行几个命令
scoop install uv
scoop install just
scoop install nvm


```


# 🚀 2026 现代化 Python 开发环境配置指南：拥抱 uv 与 Just

换了新电脑，最让人头疼也最令人兴奋的事情莫过于**重新配置开发环境**。

作为一个 Python 开发者，过去我们可能需要安装 `pyenv` 管理版本，用 `virtualenv` 或 `conda` 管理环境，用 `poetry` 管理依赖，再写一个臃肿的 `Makefile` 来跑任务。

但时代变了。在 Rust 重写万物的浪潮下，我们的工具链已经可以极致精简且飞快。

今天这篇由零开始的指南，将带你用最现代的工具栈——**uv**, **Git**, 和 **Just**——打造一台高效的 Python 开发机器。

---

## 🛠️ 第一步：准备包管理器 (Windows 特别篇)

对于 macOS 和 Linux 用户，系统通常自带或很容易安装包管理器。但对于 **Windows** 用户，系统自带的 `winget` 往往因为缺少组件或版本问题（比如 LTSC 版本）导致无法使用。

因此，**强烈推荐 Windows 开发者安装 Scoop**。它类似于 Mac 的 Homebrew，将软件安装在用户目录下，无需管理员权限，干净又卫生。

* **🪟 Windows (安装 Scoop)**
打开 PowerShell，运行以下两行命令：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

```


*安装完 Scoop 后，接下来的工具安装将变得丝般顺滑。*
* **🍎 macOS**
确保安装了 Homebrew：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```


* **🐧 Linux**
使用系统自带的 `apt`, `dnf` 或 `pacman` 即可。

---

## 1. Git：基石配置

在新电脑上，Git 是第一个需要就位的工具。

### 安装 Git

* **🪟 Windows**: `scoop install git` (推荐) 或下载安装包， 注意的是安装完成之后会提示执行三条命，然后还要把"C:\Users\zata\scoop\apps\git\current\usr\bin"粘贴到path环境变量,因为涉及到cygpath,不配置环境变量用不了
* **🍎 macOS**: `brew install git`
* **🐧 Linux**: `sudo apt install git` (Ubuntu/Debian)

### 基础配置

安装完成后，记得执行以下配置，让 `git pull` 和 `diff` 更符合现代习惯：

```bash
# 1. 身份认证
git config --global user.name "Zata"
git config --global user.email "your_email@example.com"

# 2. 现代化默认设置
git config --global init.defaultBranch main
git config --global pull.rebase true  # 保持提交线整洁，避免无意义的 merge commit

# 3. (可选) 安装 Delta 让 diff 界面更漂亮
# Windows: scoop install delta
# Mac: brew install git-delta

```

---

## 2. uv：极速的 Python 全能管家

如果你还在纠结是用 `conda` 还是 `poetry`，请直接尝试 **uv**。它由 Astral 团队构建，**集成了 Python 版本管理、虚拟环境管理和包依赖管理**。

这意味着：你甚至不需要去 Python 官网下载安装包，uv 会帮你搞定一切。

### 安装 uv

* **🪟 Windows**:
```powershell
scoop install uv
# 或者: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

```


* **🍎 macOS & 🐧 Linux**:
```bash
curl -lsSf https://astral.sh/uv/install.sh | sh

```



### 核心工作流

在空文件夹中启动一个新项目，以前需要好几步，现在只需要：

```bash
# 1. 初始化项目 (自动创建 pyproject.toml)
uv init my-project
cd my-project

# 2. 指定 Python 版本 (uv 会自动下载并安装该版本，无需系统预装)
uv python install 3.12

# 3. 添加依赖 (极速解析并同步)
uv add fastapi uvicorn

# 4. 运行命令 (自动使用虚拟环境，不用手动 activate)
uv run uvicorn main:app --reload

```

---

## 3. Just：比 Make 更现代的任务运行器

以前我们常在项目里放一个 `Makefile` 来记录常用命令。但 Make 对 Windows 支持极差，且语法古老。

**Just** 是一个跨平台的任务运行器。它使用 `Justfile`，语法清晰，且在 Windows/Mac/Linux 上表现完全一致。

### 安装 Just

* **🪟 Windows**: `scoop install just` (最稳健)
* **🍎 macOS**: `brew install just`
* **🐧 Linux**:
```bash
sudo apt install just
```



### 配置你的第一个 Justfile

在项目根目录创建一个名为 `Justfile` 的文件（注意大小写）：

```makefile
# 列出所有可用命令
default:
    @just --list

# 安装依赖
install:
    uv sync

# 运行格式化工具 (集成 ruff)
fmt:
    uv run ruff format .

# 运行本地开发服务器
dev:
    uv run uvicorn src.main:app --reload --port 8000

# 清理缓存
clean:
    rm -rf .ruff_cache .venv

```

现在，无论你在哪个系统上，只需要在终端输入 `just dev` 就能启动服务，再也不用去记那些冗长的 CLI 参数了。

---

## 4. 终端美化 (Optional)

无论你用什么系统，一个好的 Prompt 能让你心情愉悦。强烈推荐 **Starship**。它能用极简的图标显示当前的 Python 版本、Git 分支状态、执行时长等。

* **安装**:
* Windows: `scoop install starship`
* Mac/Linux: `curl -sS https://starship.rs/install.sh | sh`


* **配置**:
在你的 Shell 配置文件（如 `.zshrc` 或 PowerShell profile）中加入初始化脚本即可。

---

## 总结

对于 2026 年的 Python 开发环境，我的建议非常简单：

1. **Git** 管理代码。
2. **uv** 管理 Python 生命周期（版本+依赖）。
3. **Just** 管理项目指令。
4. **(Windows用户)** 使用 **Scoop** 来安装上述工具。

这套 "黄金三角" 组合拳不仅安装简单，迁移方便，而且**完全跨平台**。把时间花在写代码上，而不是等待环境配置的进度条上。
