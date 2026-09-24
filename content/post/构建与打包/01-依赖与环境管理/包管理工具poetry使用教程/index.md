---
title: 包管理工具poetry使用教程
description: ""
date: 2025-05-13T17:59:15+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - others
    - 教程
---

Poetry 是一个 Python 的依赖管理和项目打包工具，旨在简化 Python 项目的工作流程。本教程将涵盖安装、基本使用、常见命令和一些实用技巧，适合初学者和有一定经验的用户。

---

## 1. 什么是 Poetry？

Poetry 是一个用于管理 Python 项目依赖、虚拟环境和打包的工具。它通过一个 `pyproject.toml` 文件统一管理项目的元数据、依赖和构建配置。相比传统的 `pip` 和 `requirements.txt`，Poetry 提供了更现代化的工作流。

主要特点：
- 自动管理虚拟环境
- 精确的依赖解析，避免版本冲突
- 简化的项目打包和发布流程
- 支持 `pyproject.toml`，符合 PEP 517/518 标准

---

## 2. 安装 Poetry

### 2.1 安装 Poetry
在 Linux、macOS 或 Windows（推荐使用 WSL 或 PowerShell）上，可以通过以下命令安装 Poetry：

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

或者使用 pip（不推荐，但可用）：
```bash
pip install poetry
```

### 2.2 验证安装
安装完成后，检查 Poetry 版本：
```bash
poetry --version
```
输出类似：`Poetry (version 1.8.3)` 表示安装成功。

### 2.3 配置 Poetry
默认情况下，Poetry 会在每个项目中创建虚拟环境。你可以配置全局设置，例如让虚拟环境存储在项目目录内：
```bash
poetry config virtualenvs.in-project true
```

查看所有配置：
```bash
poetry config --list
```

---

## 3. 创建一个新项目

### 3.1 初始化项目
在终端中，创建一个新项目：
```bash
poetry new my-project
```

这会生成以下目录结构：
```
my-project/
├── pyproject.toml    # 项目配置文件
├── README.md        # 项目说明文件
├── my_project/      # 代码目录
│   └── __init__.py
└── tests/           # 测试目录
    └── __init__.py
```

### 3.2 使用现有项目
如果你有一个现有的 Python 项目，可以进入项目目录并初始化 Poetry：
```bash
cd my-existing-project
poetry init
```
这会引导你交互式地创建 `pyproject.toml` 文件，输入项目名称、版本、依赖等信息。

---

## 4. 管理依赖

### 4.1 添加依赖
使用 `poetry add` 安装依赖并自动更新 `pyproject.toml` 和 `poetry.lock` 文件。例如，安装 `requests`：
```bash
poetry add requests
```

指定版本：
```bash
poetry add requests@^2.28.0
```

开发依赖（仅用于开发环境，例如测试工具）：
```bash
poetry add pytest --group dev
```

### 4.2 移除依赖
移除某个依赖：
```bash
poetry remove requests
```

### 4.3 查看依赖
列出所有已安装的依赖：
```bash
poetry show
```

显示依赖树：
```bash
poetry show --tree
```

### 4.4 锁定依赖
Poetry 使用 `poetry.lock` 文件锁定依赖的确切版本，确保一致性。更新锁文件：
```bash
poetry lock
```

如果只想更新依赖到最新兼容版本：
```bash
poetry update
```

---

## 5. 管理虚拟环境

### 5.1 激活虚拟环境
Poetry 自动为项目创建虚拟环境。激活虚拟环境：
```bash
poetry shell
```

退出虚拟环境：
```bash
exit
```

### 5.2 在虚拟环境中运行命令
不进入 `shell` 也可以直接运行命令：
```bash
poetry run python my_script.py
```

运行测试（例如使用 pytest）：
```bash
poetry run pytest
```

### 5.3 检查虚拟环境
查看当前虚拟环境路径：
```bash
poetry env info
```

列出所有虚拟环境：
```bash
poetry env list
```

删除虚拟环境：
```bash
poetry env remove python3.10
```

---

## 6. 打包和发布项目

### 6.1 配置项目
编辑 `pyproject.toml`，确保 `[tool.poetry]` 部分包含正确的元数据，例如：
```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "A sample Python project"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.28.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.2.0"
```

### 6.2 构建项目
生成项目的 `wheel` 或 `sdist` 文件：
```bash
poetry build
```

输出文件会出现在 `dist/` 目录中，例如：
```
dist/
├── my_project-0.1.0-py3-none-any.whl
├── my_project-0.1.0.tar.gz
```

### 6.3 发布到 PyPI
配置 PyPI 的 token（在 PyPI 官网生成）：
```bash
poetry config pypi-token.pypi your-api-token
```

发布项目：
```bash
poetry publish
```

如果发布到测试 PyPI：
```bash
poetry publish --repository testpypi
```

---

## 7. 常用命令速查

| 命令                        | 功能                                  |
|-----------------------------|---------------------------------------|
| `poetry new <name>`         | 创建新项目                            |
| `poetry init`               | 初始化现有项目                        |
| `poetry add <package>`      | 添加依赖                              |
| `poetry remove <package>`   | 移除依赖                              |
| `poetry install`            | 安装所有依赖                          |
| `poetry update`             | 更新依赖到最新兼容版本                |
| `poetry lock`               | 锁定依赖版本                          |
| `poetry shell`              | 进入虚拟环境                          |
| `poetry run <command>`      | 在虚拟环境中运行命令                  |
| `poetry build`              | 构建项目                              |
| `poetry publish`            | 发布项目到 PyPI                       |
| `poetry env info`           | 查看虚拟环境信息                      |

---

## 8. 实用技巧

### 8.1 使用特定 Python 版本
如果系统中安装了多个 Python 版本，可以指定 Poetry 使用的版本：
```bash
poetry env use python3.10
```

### 8.2 导出 requirements.txt
如果需要与不支持 Poetry 的工具兼容，可以导出依赖：
```bash
poetry export -f requirements.txt --output requirements.txt
```

### 8.3 管理多个依赖组
Poetry 支持依赖分组。例如，添加文档生成工具到 `docs` 组：
```bash
poetry add sphinx --group docs
```

安装特定组的依赖：
```bash
poetry install --only docs
```

### 8.4 解决依赖冲突
如果依赖解析失败，检查 `poetry.lock` 或运行：
```bash
poetry lock --no-update
```

### 8.5 集成 IDE
大多数现代 IDE（如 PyCharm、VS Code）支持 Poetry。确保 IDE 指向 Poetry 创建的虚拟环境路径（通过 `poetry env info` 查看）。

---

## 9. 常见问题

### 9.1 Poetry 安装依赖很慢？
尝试设置国内镜像（例如清华源）：
```bash
poetry config pypi-mirror https://pypi.tuna.tsinghua.edu.cn/simple
```

### 9.2 虚拟环境未激活？
确保运行 `poetry shell` 或 `poetry run`。如果仍无效，检查是否正确安装了 Python 和 Poetry。

### 9.3 如何升级 Poetry？
升级到最新版本：
```bash
poetry self update
```

---

## 10. 资源推荐

- **官方文档**：https://python-poetry.org/docs/
- **PyPI**：https://pypi.org/
- **Poetry GitHub**：https://github.com/python-poetry/poetry
- **社区讨论**：在 X 平台搜索 `#Poetry` 或 `#Python` 获取最新动态

---



# Poetry 和 uv 

以下是对 Poetry 和 uv 的对比分析，帮你理解它们的相似点和不同点。

---

## 1. 相似点

Poetry 和 uv 都是现代化的 Python 工具，旨在改进传统的 `pip` 和 `requirements.txt` 工作流。它们的共同点包括：

- **依赖管理**：两者都提供依赖解析和锁定功能，生成精确的依赖文件（Poetry 用 `poetry.lock`，uv 用 `uv.lock`）。
- **虚拟环境**：自动创建和管理虚拟环境，隔离项目依赖。
- **项目配置**：基于 `pyproject.toml` 文件管理项目元数据和依赖，符合 PEP 517/518。
- **命令行接口**：提供简洁的 CLI 命令（如 `add`、`install`、`run`）来管理依赖和运行脚本。
- **打包支持**：都支持构建和发布 Python 包到 PyPI。
- **现代化体验**：目标是简化工作流，解决 `pip` 的依赖冲突和环境管理问题。

这些相似点让你感觉它们“很像”，因为它们都在解决 Python 生态中类似的问题。

---

## 2. 不同点

尽管功能上有重叠，Poetry 和 uv 在设计理念、性能和使用场景上有显著差异：

### 2.1 设计理念
- **Poetry**：
  - 专注于 Python 项目的**全生命周期管理**，包括依赖管理、虚拟环境、打包和发布。
  - 强调**用户友好**和**跨平台一致性**，适合开发者和小型团队。
  - 提供一体化的工作流，适合需要从项目创建到发布的完整工具链的场景。
- **uv**：
  - 由 Astral 团队（Ruff 开发者）开发，定位为**高性能**的 Python 工具链。
  - 更专注于**速度**和**效率**，用 Rust 编写，解析和安装依赖的速度远超 Poetry。
  - 设计上更模块化，适合需要快速迭代或大型项目的高级用户。

### 2.2 性能
- **Poetry**：
  - 使用 Python 编写，依赖解析和安装速度相对较慢，尤其在复杂项目中。
  - 依赖解析有时会因兼容性检查而耗时。
- **uv**：
  - 用 Rust 编写，依赖解析和安装速度极快（官方宣称比 Poetry 快 10-100 倍）。
  - 优化了缓存和并行下载，适合 CI/CD 和大规模项目。

### 2.3 功能侧重
- **Poetry**：
  - 提供内置的**项目初始化**（`poetry new`）和**发布工具**（`poetry publish`）。
  - 支持**依赖分组**（如 `dev`、`docs`），方便管理不同用途的依赖。
  - 更适合**小型到中型项目**或需要简单配置的开发者。
- **uv**：
  - 提供更灵活的**工具链**，包括依赖管理、脚本运行、Python 版本管理和项目工作流。
  - 支持**工作空间**（workspaces），适合管理 monorepo 或多项目结构。
  - 更适合**高级用户**或需要高性能的场景，如 CI/CD 流水线或大型项目。

### 2.4 虚拟环境管理
- **Poetry**：
  - 自动为每个项目创建虚拟环境，默认存储在全局缓存目录（可配置为项目内）。
  - 使用 `poetry shell` 进入虚拟环境，体验类似传统虚拟环境。
- **uv**：
  - 虚拟环境管理更轻量，创建速度更快，默认存储在项目目录下的 `.venv`。
  - 支持直接运行命令（`uv run`）而无需显式激活环境，简化工作流。

### 2.5 依赖解析
- **Poetry**：
  - 使用 `poetry.lock` 锁定依赖版本，解析过程较为严格，确保跨环境一致性。
  - 依赖解析有时过于谨慎，可能拒绝安装不完全兼容的版本。
- **uv**：
  - 使用 `uv.lock`（基于 lockfiles 的新标准），解析更灵活且速度更快。
  - 支持**增量解析**，在 CI/CD 中减少重复工作。

### 2.6 生态集成
- **Poetry**：
  - 与现有 Python 生态（如 PyPI、pytest）集成良好，社区成熟。
  - 对 IDE（如 PyCharm、VS Code）的支持更友好，配置简单。
- **uv**：
  - 生态还在快速发展，部分功能（如发布工具）不如 Poetry 成熟。
  - 与 Ruff（Astral 的代码检查工具）深度集成，适合追求全栈 Rust 工具链的用户。

### 2.7 学习曲线和社区
- **Poetry**：
  - 文档全面，社区活跃，学习曲线较平缓。
  - 适合初学者和需要稳定工具的开发者。
- **uv**：
  - 文档正在完善，功能迭代很快，可能需要更多摸索。
  - 更适合有经验的开发者或愿意尝试新工具的用户。

---

## 3. 代码示例对比

为了直观感受它们的相似与不同，下面是对常见任务的命令对比：

### 3.1 创建项目
- **Poetry**：
  ```bash
  poetry new my-project
  cd my-project
  ```
  生成带 `pyproject.toml` 的项目结构。
- **uv**：
  ```bash
  uv init my-project
  cd my-project
  ```
  生成简化的项目结构，包含 `pyproject.toml`。

### 3.2 添加依赖
- **Poetry**：
  ```bash
  poetry add requests
  ```
  更新 `pyproject.toml` 和 `poetry.lock`。
- **uv**：
  ```bash
  uv add requests
  ```
  更新 `pyproject.toml` 和 `uv.lock`，速度更快。

### 3.3 运行脚本
- **Poetry**：
  ```bash
  poetry run python my_script.py
  ```
  或进入虚拟环境：
  ```bash
  poetry shell
  python my_script.py
  ```
- **uv**：
  ```bash
  uv run python my_script.py
  ```
  无需显式激活虚拟环境。

### 3.4 锁定依赖
- **Poetry**：
  ```bash
  poetry lock
  ```
- **uv**：
  ```bash
  uv lock
  ```

### 3.5 安装依赖
- **Poetry**：
  ```bash
  poetry install
  ```
- **uv**：
  ```bash
  uv sync
  ```

---

## 4. 为什么感觉很像？

你感觉 Poetry 和 uv 很像，可能因为：
- 两者都使用 `pyproject.toml` 作为核心配置文件，命令结构类似（`add`、`run` 等）。
- 都旨在取代 `pip` 和 `virtualenv`，提供更现代的工作流。
- 在基本操作（如添加依赖、运行脚本）上，命令和输出体验接近。

但 uv 的高性能（得益于 Rust）和模块化设计使其更像一个“下一代”工具，而 Poetry 更像一个成熟的“全家桶”解决方案。

---

## 5. 选择哪个？

### 选择 Poetry 如果：
- 你想要一个**稳定、成熟**的工具，文档和社区支持完善。
- 你是初学者或需要简单的项目管理流程。
- 你重视**跨平台一致性**和**发布到 PyPI** 的便捷性。
- 你不需要极致的性能，中小型项目足够。

### 选择 uv 如果：
- 你追求**高性能**，特别是在 CI/CD 或大型项目中。
- 你需要管理**复杂项目结构**（如 monorepo）。
- 你愿意尝试新工具并接受快速迭代的生态。
- 你已经使用 Ruff 或其他 Astral 工具，想保持工具链一致。

---

## 6. 总结

Poetry 和 uv 在功能上有重叠，都简化了 Python 依赖管理和项目工作流，但它们的侧重点不同：
- **Poetry**：成熟、用户友好，适合中小型项目和完整工作流。
- **uv**：高性能、模块化，适合高级用户和大规模项目。

如果你刚开始，Poetry 可能更易上手；如果你追求速度或复杂项目管理，uv 可能是更好的选择。可以根据项目需求尝试两者，甚至在不同项目中混用（不过要注意虚拟环境隔离）。

如果你有具体场景（比如某个任务想对比 Poetry 和 uv 的用法），可以告诉我，我可以进一步细化说明！