---
title: mac os使用经验
description: ""
date: 2025-04-30T00:20:54+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - others
---


## 常用快捷键

* 全屏截图 control+shift+alt+3
* 区域截图 control+shift+alt+4
* 截图/录屏启动器 shift+command+5
* 左右切换空间 control + 左右
* 显示所有应用窗口 control + 上箭头
* 显示当前应用窗口 control + 下箭头
* 同一个应用之间切换窗口 Command + ～
* 显示/隐藏拓展坞  command +  option + D
* 打开强制退出窗口 Command ⌘ + Option ⌥ + Esc
* 直接强制退出 Command ⌘ + Option ⌥ + Shift ⇧ + Esc
* 最小化当前窗口 Command ⌘ + M
* 启动台，可以通过触发角或者设置默认F5打开


![快捷键](images/index/image.png)





## GUI实战

### 一个软件打开了多个窗口，但你只看到一个窗口？

1. 在菜单栏中，点击应用的 “窗口”（Window） 菜单，最下面就可以看到有哪些窗口

2. 使用 Mission Control（三指/四指上滑）查看所有打开的窗口。或者使用键盘上面的control+上箭头

3. 鼠标右键点击 Dock 上该应用的图标，有多个窗口的选项。



### mac OS中哪个剪辑软件最好用

Final Cut Pro


直接去官网下载90天试用

在控制台中执行以下代码刷新试用期限

mv -v ~/Library/Application\ Support/.ffuserdata ~/.Trash,



### mac OS设置环境变量

` 编辑 ~/.zshrc 或 ~/.bash_profile 前，建议备份。`



 **确认当前 Shell**
在终端运行以下命令，确认你使用的是哪种 shell：
```bash
echo $SHELL
```
- 如果输出是 `/bin/zsh`，你用的是 zsh。
- 如果输出是 `/bin/bash`，你用的是 bash。

---


- 方法 1：临时添加（仅当前终端会话有效）
    在终端输入：
    ```bash
    export 变量名=变量值
    ```
    例如：
    ```bash
    export PATH=$PATH:/usr/local/bin
    ```
    这种方式在关闭终端后会失效。

-  方法 2：永久添加（写入配置文件）


    - **对于 zsh**：

    1. 执行以下命令追加环境变量到～/.zshrc文件中
    
    ```zsh
    echo "export 变量名='变量值'" >> ~/.zshrc
    ```

    也可以手动修改

        1. 打开终端，编辑 `~/.zshrc` 文件：
            ```bash
            nano ~/.zshrc
            ```
        2. 在文件末尾添加：
            ```bash
            export 变量名=变量值
            ```
        3. 保存并退出 在nano编辑器中，按Ctrl + X，接着按Y，再按Enter以保存并关闭文件。



    2. 应用更改：

        ```bash
        source ~/.zshrc
        ```
    3. 验证
        重新打开一个终端窗口，然后执行
        ```zsh
        echo $变量名
        ```

    - **对于 bash**：
    1. 执行以下命令追加到 `~/.bash_profile`：
        ```bash
        echo "export 变量名='变量值'" >> ~/.bash_profile
        ```
    当然你也可以手动修改，不在赘述


    2. 应用更改：
        ```bash
        source ~/.bash_profile
        ```
    3. 验证
        ```zsh
        echo $变量名
        ```

- 注意：
    - 如果需要添加到 `PATH`，建议用 `$PATH` 保留现有路径，例如：
    ```bash
    export PATH=$PATH:/新路径
    ```
    - 确保路径正确，避免语法错误。

---


3. **删除环境变量**

方法 1：临时删除（仅当前终端会话）
使用 `unset` 命令：
```bash
unset 变量名
```


方法 2：永久删除
1. 打开对应的 shell 配置文件（`~/.zshrc` 或 `~/.bash_profile`）。
2. 找到包含 `export 变量名=变量值` 的行，删除或注释掉（在行首加 `#`）。
3. 保存并退出。
4. 应用更改：
   ```bash
   source ~/.zshrc
   ```
   或
   ```bash
   source ~/.bash_profile
   ```

---

- 查看所有环境变量：
  ```bash
  printenv 或者 env
  ```

---


## 命令行实战

### macOS 下更改文件夹及文件所有者为 zata 用户的教程

`目标`

将指定文件夹及其下所有文件的权限更改为 `zata` 用户。

`步骤`

1. **打开终端**：
   - 使用 `Command + T` 或在应用程序中打开「终端」。

2. **更改所有者**：
   - 运行以下命令，将文件夹及其内容的所有者设为 `zata`：
     ```bash
     sudo chown -R zata /path/to/your/folder
     ```
     - 替换 `/path/to/your/folder` 为实际文件夹路径（如 `/Users/yourname/Documents`）。
     - `sudo` 需要管理员密码。

3. **（可选）设置权限**：
   - 若需设置具体权限（例如只给 `zata` 读写权限），运行：
     ```bash
     sudo chmod -R u=rwX,go= /path/to/your/folder
     ```

4. **验证更改**：
   - 检查文件所有者和权限：
     ```bash
     ls -l /path/to/your/folder
     ```
   - 包含隐藏文件：
     ```bash
     ls -ld /path/to/your/folder/* /path/to/your/folder/.*
     ```

` 注意事项`

- 确保 `zata` 用户存在（用 `id zata` 检查）。
- 确认路径正确，避免误操作。
- 更改权限前备份重要数据。


---

## 新 Mac 快速配置（Git、Node 与 UV）

新 Mac 到手，先把开发环境搭起来。本文的核心思路是**各司其职**：

| 工具 | 职责 |
|:---|:---|
| **Homebrew** | 装系统级工具（Git、fnm、ripgrep 等）|
| **fnm** | Node 版本管理 |
| **UV** | Python 版本管理 + 包管理 |

不混用职责，不 `brew install node`，避免升级时互相干扰。

> **国内用户注意**：以下步骤大量依赖 GitHub，建议先配好代理再进行安装。

### 一、代理配置（国内用户必看）

如果你有可用的代理工具（Clash/V2Ray/Surge 等），推荐直接写入 `~/.zshrc`，所有终端会话自动生效：

```bash
echo 'export https_proxy=http://127.0.0.1:7890' >> ~/.zshrc
echo 'export http_proxy=http://127.0.0.1:7890' >> ~/.zshrc
echo 'export all_proxy=socks5://127.0.0.1:7890' >> ~/.zshrc
source ~/.zshrc
```

> 不同代理软件的端口可能不同，常见的是 `7890`、`1080`、`6152` 等，请根据实际情况修改。

验证代理生效：

```bash
curl -I https://www.google.com
```

**临时配置（当前终端生效）**：

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890
```

**Homebrew 镜像源（不翻墙的备选）**：

```bash
export HOMEBREW_INSTALL_FROM_API=1
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
git -C "$(brew --repo)" remote set-url origin https://mirrors.ustc.edu.cn/brew.git
brew update
```

### 二、基础环境

#### 2.1 Xcode Command Line Tools

系统级编译依赖，自带一个基础版 Git：

```bash
xcode-select --install
```

#### 2.2 Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 三、Git 安装与配置

#### 3.1 安装

Mac 预装的 Git 版本较旧，通过 Homebrew 装最新版：

```bash
brew install git
git --version
```

#### 3.2 基础配置

```bash
# 改成你自己的
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 默认分支名设为 main
git config --global init.defaultBranch main

# 默认编辑器（可选）
git config --global core.editor "code --wait"
```

#### 3.3 SSH 密钥

生成密钥对并配置到 GitHub，之后 `git clone`/`git push` 就无需反复输密码。

```bash
# 生成密钥对（ed25519 是目前最推荐的算法，比 RSA 更安全、密钥更短）
# -C 只是加个注释，写邮箱方便你识别这是哪台电脑的 key
# 执行后一路回车，会在 ~/.ssh/ 下生成 id_ed25519（私钥，绝不可泄露）和 id_ed25519.pub（公钥，可以公开）
ssh-keygen -t ed25519 -C "your.email@example.com"

# 启动 ssh-agent（密钥管家），eval 是把环境变量注入当前终端，让终端知道管家的位置
# 执行后会输出类似 "Agent pid 12345"
eval "$(ssh-agent -s)"

# 把私钥交给 ssh-agent 保管，之后整个终端会话内的 git 操作都自动认证，无需再输密码
ssh-add ~/.ssh/id_ed25519

# 把公钥复制到剪贴板（macOS 专属命令），然后贴到 GitHub → Settings → SSH and GPG keys → New SSH key
# 注意：是 .pub 文件（公钥），不是没后缀的私钥！
pbcopy < ~/.ssh/id_ed25519.pub
```

粘贴到 GitHub/GitLab 的 SSH Keys 设置页面，然后测试连接：

```bash
ssh -T git@github.com
```

#### 3.4 Git 代理（可选）

加速克隆 GitHub 仓库：

```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

取消代理：

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 四、Node 环境（fnm）

[fnm](https://github.com/Schniz/fnm) 是 Rust 写的 Node 版本管理器，比 nvm 快，兼容 `.nvmrc`。

#### 4.1 安装 fnm

```bash
brew install fnm
```

把 fnm 初始化写入 `~/.zshrc`：

```bash
echo 'eval "$(fnm env --use-on-cd)"' >> ~/.zshrc
source ~/.zshrc
```

#### 4.2 安装 Node

```bash
# 安装并设为默认版本
fnm install 22
fnm default 22

# 验证
node -v
npm -v
```

#### 4.3 常用操作

```bash
# 查看已安装版本
fnm list

# 切换版本
fnm use 20

# 安装 .nvmrc 中指定的版本
fnm install
fnm use
```

### 五、Python 环境（UV）

[UV](https://github.com/astral-sh/uv) 是 Astral 团队开发的极速 Python 包管理器，一个工具替代 pyenv + pip + venv。

#### 5.1 安装 UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装脚本一般会自动配置 shell，如果没有，手动添加：

```bash
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
source ~/.zshrc
```

#### 5.2 安装 Python

```bash
uv python install 3.12
```

#### 5.3 常用操作

```bash
# 创建项目（自带 venv）
uv init myproject
cd myproject

# 添加依赖
uv add requests

# 运行脚本
uv run python script.py

# 同步依赖
uv sync
```

#### 5.4 与 IDE 配合

- **VSCode**: `Python: Select Interpreter` → 选择 `myproject/.venv/bin/python`
- **PyCharm**: `Previously configured interpreter` → 指向 `.venv/bin/python`

### 六、其他推荐工具

#### 6.1 系统增强

```bash
# 全能启动器，取代 Spotlight，支持剪贴板历史、窗口管理、翻译等
# 安装后建议配置：
#   1. 设置快捷键为 Cmd+Space（替代 Spotlight），把 Spotlight 改绑 Option+Space
#   2. 开启「剪贴板历史」（Cmd+Space → Search Clipboard History），默认保存最近 3 个月
#   3. 在 Store 里安装常用扩展：Window Management、Calculator、Dictionary、System Monitor
brew install --cask raycast

# 窗口分屏（左右半屏、上下、四分之一等）
brew install --cask rectangle

# 菜单栏显示 CPU / 内存 / 网速 / 温度
brew install --cask stats

# 折叠菜单栏右侧图标，避免挤爆
brew install --cask hiddenbar

# 彻底卸载应用，连带删除偏好设置、缓存等残留文件
brew install --cask appcleaner
```

#### 6.2 开发工具

```bash
# 终端，比分屏、搜索、配色都比自带 Terminal 强
brew install --cask iterm2

# API 调试工具
brew install --cask postman

# 数据库 GUI（MySQL / PostgreSQL / MongoDB 等）
brew install --cask tableplus

# 容器化开发
brew install --cask docker
```

#### 6.3 命令行神器

```bash
# 一条命令装完
brew install tree eza bat fd fzf zoxide ripgrep tldr jq htop wget curl httpie
```

| 工具 | 取代 | 亮点 |
|:---|:---|:---|
| **eza** | `ls` | 彩色、git 状态、树形、图标 |
| **bat** | `cat` | 语法高亮、行号、Git diff |
| **ripgrep (rg)** | `grep` | 极速、自动忽略 .gitignore |
| **fd** | `find` | 简洁语法、彩色输出 |
| **fzf** | — | 模糊搜索文件 / 历史 / 任何列表 |
| **zoxide** | `cd` | `z xxx` 自动跳转去过的目录 |
| **tldr** | `man` | 看常用命令的简例，不看长篇手册 |
| **jq** | — | 命令行处理 JSON，提取字段、格式化 |
| **htop** | `top` | 交互式系统监控 |
| **httpie** | `curl` | 更友好的 HTTP 请求工具 |

### 七、验证清单

| 检查项 | 命令 | 期望结果 |
|:---|:---|:---|
| Git 版本 | `git --version` | 2.x |
| SSH 连接 | `ssh -T git@github.com` | Hi username! |
| fnm 版本 | `fnm --version` | 1.x |
| Node 版本 | `node -v` | v22.x |
| UV 版本 | `uv --version` | 0.x |
| Python 可用 | `uv run python --version` | 3.12.x |

### 八、一键脚本（可选）

把以上流程写成 `setup.sh`，丢进 GitHub 私有仓库，换机时一条命令跑完：

```bash
#!/bin/bash
set -e

echo "==> 检查代理"
if [ -z "$https_proxy" ]; then
    echo "⚠️  先配好代理再运行"
    exit 1
fi

echo "==> Xcode CLT"
xcode-select --install 2>/dev/null || true

echo "==> Homebrew"
command -v brew >/dev/null || \
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo "==> 工具链"
brew install git fnm tree ripgrep fd jq

echo "==> Node"
eval "$(fnm env --use-on-cd)"
fnm install 22
fnm default 22

echo "==> UV + Python"
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12

echo "==> Git 配置"
read -p "Git 用户名: " name
read -p "Git 邮箱: " email
git config --global user.name "$name"
git config --global user.email "$email"
git config --global init.defaultBranch main

echo "✅ 完成！重启终端生效。"
```

### 总结

| 工具 | 用途 |
|:---|:---|
| **Homebrew** | 系统工具（Git、fnm、ripgrep…）|
| **fnm** | Node 版本管理 |
| **UV** | Python 版本管理 + 包管理 |

各司其职，互不干涉。换机时一条脚本 5 分钟跑完，后续按需扩展即可。


