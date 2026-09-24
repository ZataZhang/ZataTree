---
title: pipx使用教程
description: ""
date: 2025-05-12T14:32:42+08:00
image: images/index/index.png
categories:
    - 构建与打包
tags:
    - 依赖与环境管理
    - pipx
    - 教程
---


参考：

https://pipx.pypa.io/stable

https://zhuanlan.zhihu.com/p/637791135

https://www.kancloud.cn/madxzb/python-guide/2248088

---




`pipx` 是一个帮助你安装和运行 Python 终端应用的工具，它的主要优点是能将这些应用安装在独立隔离的环境中，避免与系统或其他项目的 Python 包产生冲突。

## **`pipx` 的核心优势：**

* **隔离性：** 每个通过 `pipx` 安装的应用都有自己独立虚拟环境，这意味着它们的依赖项不会影响到你的全局 Python 环境或其他项目。
* **便利性：** 可以轻松地运行 Python 应用，而无需手动创建和管理虚拟环境。
* **安全性：** 减少了全局安装 Python 包可能带来的风险。
* **简洁性：** 专注于应用本身，而不是其复杂的依赖关系。

## **教程大纲：**

1.  **安装 `pipx`**
2.  **`pipx` 的基本使用**
    * 安装 Python 应用
    * 运行应用
    * 列出已安装的应用
    * 升级应用
    * 卸载应用
    * 运行一次性的应用 (使用 `pipx run`)
3.  **`pipx` 的进阶使用**
    * 管理 `pipx` 环境
    * 自定义 `pipx` 安装位置
    * 注入额外的包到应用环境中
4.  **常用命令总结**

---

## **1. 安装 `pipx`**

`pipx` 本身也是一个 Python 包，你可以使用 `pip` 来安装它。

* **如果你使用的是 Python 3.6 或更高版本 (推荐)：**

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

    `--user` 参数会将 `pipx` 安装在你的用户目录下，而不是系统全局目录。`pipx ensurepath` 命令会确保 `pipx` 安装的可执行文件路径被添加到你的系统 `PATH` 环境变量中。执行完此命令后，你可能需要**重启你的终端或者重新加载你的 shell 配置文件** (例如 `.bashrc`, `.zshrc`) 才能让 `PATH` 的改动生效。

* **使用包管理器 (例如 Homebrew on macOS, apt on Debian/Ubuntu)：**

    * **macOS (使用 Homebrew):**
        ```bash
        brew install pipx
        pipx ensurepath
        ```

    * **Debian/Ubuntu (可能需要较新版本)：**
        ```bash
        sudo apt update
        sudo apt install pipx
        pipx ensurepath
        ```
        (注意：通过系统包管理器安装的版本可能不是最新的。)

* **验证安装：**

    打开一个新的终端窗口，然后输入：

    ```bash
    pipx --version
    ```

    如果安装成功，你会看到 `pipx` 的版本号。

---

## **2. `pipx` 的基本使用**

**2.1 安装 Python 应用**

使用 `pipx install <package_name>` 命令来安装一个 Python 应用。`pipx` 会自动为这个应用创建一个新的隔离环境，并将应用的可执行文件链接到 `~/.local/bin` (默认情况下)。

**示例：** 安装 `cowsay` (一个经典的终端程序)

```bash
pipx install cowsay
```

**示例：** 安装 `youtube-dl` 或其现代替代品 `yt-dlp` (一个视频下载工具)

```bash
pipx install yt-dlp
```

**示例：** 安装 `black` (一个 Python 代码格式化工具)

```bash
pipx install black
```

安装完成后，如果 `~/.local/bin` 在你的 `PATH` 中，你就可以直接在终端运行这些应用了。

**2.2 运行应用**

一旦通过 `pipx` 安装了应用，你就可以像运行其他任何终端命令一样运行它。

**示例：**

```bash
cowsay "Hello from pipx!"
yt-dlp --version
black --version
```

**2.3 列出已安装的应用**

要查看所有通过 `pipx` 安装的应用及其环境信息，使用：

```bash
pipx list
```

输出会显示每个应用的版本、Python 版本、可执行文件路径等。

**2.4 升级应用**

* **升级单个应用：**

    ```bash
    pipx upgrade <package_name>
    ```
    例如，升级 `yt-dlp`:
    ```bash
    pipx upgrade yt-dlp
    ```

* **升级所有已安装的应用：**

    ```bash
    pipx upgrade-all
    ```

**2.5 卸载应用**

要移除一个通过 `pipx` 安装的应用及其隔离环境，使用：

```bash
pipx uninstall <package_name>
```
例如，卸载 `cowsay`:
```bash
pipx uninstall cowsay
```

**2.6 运行一次性的应用 (使用 `pipx run`)**

如果你只是想临时运行一个 Python 应用，而不想永久安装它，可以使用 `pipx run` 命令。`pipx` 会在一个临时的虚拟环境中下载并运行该应用，运行结束后会自动清理环境。

这对于那些你不经常使用，或者只是想尝试一下的工具非常有用。

**示例：**

* 运行 `cowsay` 并传递参数，而无需先 `pipx install cowsay`:
    ```bash
    pipx run cowsay "Temporary moo"
    ```

* 运行一个简单的 HTTP 服务器 (Python 内置的 `http.server` 模块)：
    ```bash
    pipx run http.server -- --directory /path/to/your/files 8000
    ```
    注意：当应用本身也需要接收参数时，你可能需要在应用参数前加上 `--`，以告诉 `pipx` 后面的参数是给应用而不是给 `pipx run` 命令的。

* 运行特定版本的应用：
    ```bash
    pipx run black==22.3.0 --check .
    ```

---

## **3. `pipx` 的进阶使用**

**3.1 管理 `pipx` 环境**

* **重新安装所有包：**
    如果 `pipx` 的内部结构或 Python 版本发生变化，你可能需要重新安装所有应用。
    ```bash
    pipx reinstall-all
    ```

* **查看某个应用的详细信息：**
    ```bash
    pipx list --include-injected <package_name>
    ```
    这会显示应用的安装路径、Python 版本以及任何通过 `pipx inject` 注入的额外包。

**3.2 自定义 `pipx` 安装位置**

默认情况下，`pipx` 将环境安装在 `~/.local/pipx/venvs`，可执行文件链接到 `~/.local/bin`。你可以通过环境变量来修改这些路径：

* `PIPX_HOME`: 定义 `pipx` 安装环境和元数据的根目录 (默认为 `~/.local/pipx`)。
* `PIPX_BIN_DIR`: 定义 `pipx` 链接应用可执行文件的目录 (默认为 `~/.local/bin`)。

如果你修改了这些变量，记得也要更新你的 `PATH` 环境变量，并可能需要运行 `pipx ensurepath` 来帮助你设置。

**示例 (在你的 `.bashrc` 或 `.zshrc` 中设置)：**

```bash
export PIPX_HOME=/opt/pipx_venvs
export PIPX_BIN_DIR=/opt/pipx_bin
export PATH="$PIPX_BIN_DIR:$PATH" # 确保新的 bin 目录在 PATH 中
```
修改后请重新加载 shell 配置或重启终端。

**3.3 注入额外的包到应用环境中 (`pipx inject`)**

有时，一个通过 `pipx` 安装的应用可能需要一些可选的依赖或插件才能启用特定功能。你可以使用 `pipx inject` 命令将额外的包安装到该应用已存在的隔离环境中。

**示例：**

假设你安装了 `black`，并且想为它安装 `jupyter` 插件（注意：这只是一个假设的例子，`black` 本身可能不需要这样操作，具体看应用文档）。

```bash
pipx install black
pipx inject black some-black-plugin another-plugin
```

* 查看注入的包：
    ```bash
    pipx list --include-injected black
    ```

* **谨慎使用 `inject`：** `inject` 的主要目的是为了应用的插件或可选依赖。过度使用 `inject` 来构建复杂的环境可能会违背 `pipx` 保持应用隔离和简洁的初衷。如果一个应用需要很多额外的包才能运行，可能它更适合通过 `pip` 在一个专门的虚拟环境中进行管理 (例如使用 `venv` 或 `conda`)。

---

## **4. 常用命令总结**

| 命令                       | 描述                                                           |
| :------------------------- | :------------------------------------------------------------- |
| `pipx install <pkg>`       | 安装一个 Python 应用到隔离环境。                               |
| `pipx run <pkg> [args...]` | 在临时环境中运行一个 Python 应用。                             |
| `pipx uninstall <pkg>`     | 卸载一个应用及其环境。                                         |
| `pipx uninstall-all`       | 卸载所有通过 `pipx` 安装的应用。                               |
| `pipx list`                | 列出所有已安装的应用。                                           |
| `pipx upgrade <pkg>`       | 升级一个已安装的应用。                                         |
| `pipx upgrade-all`         | 升级所有已安装的应用。                                         |
| `pipx reinstall <pkg>`     | 重新安装一个应用 (使用与之前相同的 Python 版本)。               |
| `pipx reinstall-all`       | 重新安装所有应用。                                             |
| `pipx inject <pkg> [deps...]`| 将额外的包注入到已安装应用的环境中。                           |
| `pipx ensurepath`          | 确保 `pipx` 的可执行文件路径 (通常是 `~/.local/bin`) 在你的 PATH 中。 |
| `pipx completions`         | 为你的 shell 生成自动补全脚本。                                |
| `pipx --version`           | 显示 `pipx` 的版本。                                           |
| `pipx <command> --help`    | 显示特定命令的帮助信息。                                       |

---

## **何时使用 `pipx` vs `pip`?**

* **使用 `pipx`：**
    * 当你想要安装和运行一个主要作为**命令行工具/应用**的 Python 包时 (例如 `httpie`, `black`, `poetry`, `ansible`, `awscli` 等)。
    * 你希望这些工具全局可用，但又不想它们污染你的系统 Python 或其他项目的环境。

* **使用 `pip` (通常在虚拟环境中，如 `venv`)：**
    * 当你为一个特定的 Python **项目**安装**库依赖**时 (例如 `requests`, `numpy`, `django` 等)。这些是你会在 Python 代码中 `import` 的库。
    * 这些库是项目的一部分，而不是独立的命令行应用。

希望这个教程能帮助你开始使用 `pipx`！它是一个非常实用的工具，可以让你的 Python 应用管理更加清爽和高效。