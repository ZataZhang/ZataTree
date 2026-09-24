---
title: copier-using
description: ""
date: 2025-09-12T15:26:16+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - others
---



### Copier 是什么？

**Copier** 是一个用于创建和管理项目文件的现代化命令行工具。你可以把它理解为一个强大的“复制粘贴”工具，但它远不止于此。它能根据一个预设的“模板”（template），智能地生成一个新项目，并且在模板更新后，还能将这些更新应用到你已生成的项目中。

它在软件开发领域非常受欢迎，尤其适合用于搭建标准化的项目初始结构，也就是我们常说的“脚手架”（scaffolding）。

**核心特性：**

1.  **项目生成 (Project Generation)**: 从一个模板快速生成一个新项目。在生成过程中，它会向你提问（例如，项目名称、作者、选择特定功能等），然后根据你的回答填充模板中的变量。
2.  **项目更新 (Project Updates)**: 这是 Copier 相较于其前辈（如 Cookiecutter）最大的优势。当模板本身有了改进或修复（比如，升级了依赖库、修复了安全漏洞），你可以使用 Copier 将这些变更安全地同步到已经生成的项目中，而不会覆盖你自己的代码。
3.  **动态与交互式**: 通过一系列问题引导用户完成项目配置，并将答案记录在 `.copier-answers.yml` 文件中，方便未来更新。
4.  **版本控制友好**: 它与 Git 紧密集成，能很好地处理版本变更和代码合并。
5.  **跨平台与语言无关**: Copier 本身由 Python 编写，但它可以为任何编程语言（Go, Rust, JavaScript, Python 等）创建项目模板。

简单来说，**Copier = 项目脚手架 + 持续更新能力**。它解决了传统脚手架工具“一次性生成，后续维护困难”的痛点。

-----

### Copier 使用教程

下面，我们将从安装、创建项目、更新项目等环节，一步步教你如何使用 Copier。

#### 1\. 安装 Copier

首先，你需要一个 Python 环境。然后使用 `pip` 或 `pipx`（推荐）来安装 Copier。`pipx` 可以将 Copier 安装在独立的环境中，避免污染全局 Python 环境。

**使用 pipx (推荐):**

```bash
# 安装 pipx
python -m pip install --user pipx
python -m pipx ensurepath

# 使用 pipx 安装 copier
pipx install copier
```

**使用 pip:**

```bash
pip install copier
```

安装完成后，你可以通过以下命令验证是否成功：

```bash
copier --version
```

#### 2\. 从模板创建新项目 (`copier copy`)

Copier 的核心是模板。模板通常是一个 Git 仓库。我们以一个官方推荐的 Python 项目模板为例。

**命令格式:**

```bash
copier copy <模板地址> <你的项目文件夹名称>
```

**实战演练:**

假设我们要创建一个名为 `my-awesome-project` 的新项目。

```bash
copier copy gh:copier-org/copier-python-template my-awesome-project
```

  * `gh:copier-org/copier-python-template` 是模板的简写地址，它指向 GitHub 上的 `copier-org/copier-python-template` 仓库。你也可以使用完整的 `https://github.com/copier-org/copier-python-template.git` 地址。

执行命令后，Copier 会开始与你交互，提出一系列问题来配置项目：

```
🎤 What is your project name?
   (Default: My Awesome Project)
└──> My Super FastAPI App  # 输入你的项目名

🎤 What is your project description?
   (Default: Awesome project, created with copier-python-template)
└──> A demo project for learning Copier. # 输入描述

... (后续还会有作者、邮箱、选择许可证等问题)
```

你只需要根据提示回答问题即可。回答完毕后，Copier 会做两件事：

1.  在当前目录下创建一个 `my-awesome-project` 文件夹。
2.  文件夹内包含了根据你的回答生成的所有项目文件。
3.  同时，文件夹里还会有一个特殊的 `.copier-answers.yml` 文件，它记录了你刚才的所有回答。**这个文件非常重要，是未来项目更新的关键！**

**`.copier-answers.yml` 文件示例:**

```yaml
# Changes here will be overwritten by Copier
_commit: v0.2.2
_src_path: gh:copier-org/copier-python-template
author_email: your_email@example.com
author_name: Your Name
project_description: A demo project for learning Copier.
project_name: My Super FastAPI App
...
```

#### 3\. 更新现有项目 (`copier update`)

这是 Copier 的“杀手级”功能。假设一段时间后，`copier-python-template` 模板的作者发布了一个新版本，修复了一些 Bug 并增加了一些新功能。你想把这些更新应用到你的 `my-awesome-project` 中。

操作非常简单：

**首先，进入你的项目目录：**

```bash
cd my-awesome-project
```

**然后，执行更新命令：**

```bash
copier update
```

Copier 会自动执行以下步骤：

1.  读取 `.copier-answers.yml` 文件，找到原始模板地址和上次生成时的版本。
2.  检查模板仓库是否有新版本。
3.  使用你之前回答过的答案，重新生成一份最新的项目文件。
4.  将新生成的文件与你当前的项目文件进行对比，并尝试智能合并。

在合并过程中，如果遇到冲突（例如，模板的某个文件和你自己修改过的文件内容不一致），Copier 会生成标准的 `.rej` 冲突文件，或者如果你在 Git 仓库中，它会产生 Git 冲突标记，让你手动解决。

**更新时的注意事项:**

  * 强烈建议在执行 `copier update` 前，确保你的项目已经提交到 Git。这样即使更新出现问题，你也可以轻松回滚。
  * Copier 会尽力保留你自己的代码，但最佳实践是，尽量不要修改由模板直接生成且预计会频繁更新的配置文件（除非你清楚自己在做什么）。

#### 4\. 创建自己的模板

如果你想创建自己的项目模板，也非常简单。

1.  **创建一个标准的项目结构**。例如，一个包含 `README.md`, `.gitignore`, `src/` 等文件的项目。

2.  **将需要动态替换的内容改为 Jinja2 语法**。

      * 文件名可以包含变量，例如 `{{ project_name }}/main.py`。
      * 文件内容也可以包含变量，例如 `README.md` 中可以这样写：

    <!-- end list -->

    ```markdown
    # {{ project_name }}

    {{ project_description }}
    ```

3.  **创建一个 `copier.yml` (或 `copier.yaml`) 文件**。这个文件用来定义 Copier 需要向用户提出的问题。

    **`copier.yml` 示例:**

    ```yaml
    # 定义问题
    project_name:
      type: str
      help: What is your project name?

    project_description:
      type: str
      help: What is your project description?
      default: "A cool project."

    # 定义模板渲染后要执行的命令
    _tasks:
      - git init
      - git add .
      - git commit -m "Initial commit from copier template"
    ```

    这里定义了两个问题：`project_name` 和 `project_description`。用户在生成项目时回答的答案会分别赋值给这两个变量。

4.  **将模板推送到 Git 仓库**（如 GitHub），然后你就可以像之前一样使用 `copier copy` 来从你的模板创建新项目了。

-----

### 总结

  * **对于使用者**: Copier 是一个能让你轻松使用标准化项目模板并保持模板同步更新的强大工具。只需 `copier copy` 创建和 `copier update` 更新。
  * **对于模板维护者/团队**: Copier 是统一团队技术栈、规范项目结构、分发最佳实践的利器。通过维护一个中央模板，所有团队成员都可以快速启动项目并享受持续的模板升级。

你最开始提到的那个脚本，正是在 Copier 这个大生态系统下的一个自动化辅助工具。它解决了 `.env` 文件通常不适合使用 Jinja2 模板直接渲染的问题，通过在 Copier 更新后运行脚本，间接地将 `.copier-answers.yml` 中的配置同步到 `.env` 文件中，实现配置的无缝更新。这正是 Copier 强大扩展性的体现。