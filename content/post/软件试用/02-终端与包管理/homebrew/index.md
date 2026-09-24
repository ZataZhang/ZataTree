---
title: homebrew
description: ""
date: 2026-02-01T19:57:49+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftTrial
---


# Homebrew 完全指南：从安装到高效使用（2026 最新版）

> 本文全面介绍 macOS 和 Linux 下最流行的包管理器 Homebrew，涵盖安装、配置、常用命令、实战技巧及常见问题排查，助你成为命令行效率大师。

---

Homebrew（昵称 *brew*）是 macOS 和 Linux 上开源的包管理器，被誉为 "The Missing Package Manager for macOS"。它允许你用一行命令安装数千款开发工具、应用和库，无需手动编译或处理依赖。

```bash
# 传统方式（繁琐）
./configure && make && sudo make install

# Homebrew（优雅）
brew install node
```

Homebrew 的优势在于其简单直观的操作方式，无需管理员权限即可安装软件，能够自动解决软件依赖关系，支持大量可用软件包（formulae），同时还能支持 macOS 和 Linux 平台。此外，它还提供了 Cask 来安装图形界面应用，以及 Bottles 来使用预编译二进制文件。

---

从 Homebrew 4.0 起，官方在 [brew.sh](https://brew.sh) 首页主推 `.pkg` 安装方式，更适合新手。

**安装步骤：**

1. 访问 GitHub Releases：
   👉 https://github.com/Homebrew/brew/releases/latest

2. 下载最新 `.pkg` 文件（如 `homebrew-4.6.1.pkg`）

3. 双击安装包，按向导完成安装（需输入密码）

4. **自动配置 PATH**（4.6.0+ 版本已内置，无需手动操作）

5. 验证安装：
   ```bash
   brew --version
   # 输出示例：Homebrew 4.6.1
   ```

> 💡 安装路径自动选择：
> - **Apple Silicon (M1/M2/M3/M4)** → `/opt/homebrew`
> - **Intel Mac** → `/usr/local`

如果需要，也可以使用传统脚本方法进行安装：

```bash
# 安装前确保已安装 Xcode 命令行工具
xcode-select --install

# 执行官方安装脚本
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

> ⚠️ 安装后若 `brew` 命令不可用，请按终端提示配置 PATH：
> ```bash
> # Apple Silicon
> echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
> eval "$(/opt/homebrew/bin/brew shellenv)"
> ```

---

为了进一步提升 Homebrew 的使用体验，可进行一些基础配置和优化。例如，配置国内镜像源以大幅提升下载速度：

```bash
# 替换 brew.git 仓库
git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git

# 替换 formulae 源（Apple Silicon）
git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git

# Intel Mac 额外替换：
# git -C "$(brew --repo homebrew/cask)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git

# 重置并更新
brew update-reset
brew update
```

> 🌐 常用镜像源：
> - 清华大学：`https://mirrors.tuna.tsinghua.edu.cn`
> - 中科大：`https://mirrors.ustc.edu.cn`
> - 阿里云：`https://mirrors.aliyun.com`

此外，启用自动补全功能可以让你更高效地使用 Homebrew：

```bash
# Zsh（macOS Catalina 及以上默认）
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
brew shellenv >> ~/.zshrc
source ~/.zshrc

# Bash
brew shellenv >> ~/.bash_profile
source ~/.bash_profile
```

---

Homebrew 提供了一些核心命令来管理软件包。以下是常用的命令速查表：

| 命令 | 说明 | 示例 |
|------|------|------|
| `brew install <pkg>` | 安装软件 | `brew install git` |
| `brew uninstall <pkg>` | 卸载软件 | `brew uninstall node` |
| `brew reinstall <pkg>` | 重装软件 | `brew reinstall python@3.12` |
| `brew upgrade <pkg>` | 升级指定软件 | `brew upgrade curl` |
| `brew upgrade` | 升级所有软件 | — |
| `brew cleanup` | 清理旧版本 | — |
| `brew list` | 列出已安装软件 | — |
| `brew info <pkg>` | 查看软件信息 | `brew info nginx` |
| `brew search <keyword>` | 搜索软件包 | `brew search postgres` |

对于 GUI 应用管理，使用 `brew install --cask` 命令可以安装图形界面应用：

```bash
# 安装图形界面应用
brew install --cask google-chrome
brew install --cask visual-studio-code

# 卸载
brew uninstall --cask iterm2

# 查看所有已安装 Cask
brew list --cask
```

> 💡 Cask 支持的应用包括：Chrome、VS Code、Docker、Obsidian、Raycast 等。

使用 `brew search` 和 `brew deps` 可以进行软件包的搜索及查看依赖关系：

```bash
# 搜索软件
brew search python

# 查看可安装的版本
brew search /python@/

# 查看软件依赖树
brew deps --tree node
```

---

在实际使用中，Homebrew 可以帮助你快速搭建开发环境。例如，以下命令可以用于配置一个前端开发环境：

```bash
# 1. 安装核心工具链
brew install node yarn pnpm git coreutils

# 2. 安装 GUI 工具
brew install --cask visual-studio-code iterm2 docker

# 3. 安装数据库
brew install postgresql redis

# 4. 启动服务（后台运行）
brew services start postgresql
brew services start redis

# 5. 验证安装
node -v && npm -v && psql --version
```

对于需要管理多个版本 Python 的场景，可以安装特定版本并切换路径：

```bash
# 安装特定版本
brew install python@3.11 python@3.12

# 切换版本（通过 PATH 优先级）
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

python3 --version  # 输出 3.11.x
```

---

Homebrew 还提供了一些高级技巧，例如使用 `brew bundle` 管理项目依赖：

在项目根目录创建 `Brewfile`：

```ruby
# Brewfile
brew "git"
brew "node"
brew "redis"
cask "visual-studio-code"
```

一键安装/同步环境：
```bash
brew bundle          # 安装所有依赖
brew bundle cleanup  # 卸载未在 Brewfile 中声明的软件
```

> ✅ 适合团队协作、新机器快速配置、云开发环境复现

同时还可查看软件安装位置与配置：

```bash
# 查看安装路径
brew --prefix node

# 查看配置文件位置
brew --prefix redis
# 输出：/opt/homebrew/opt/redis
# 配置文件通常在：/opt/homebrew/etc/redis.conf
```

遇到问题时，可使用以下命令进行诊断与修复：

```bash
# 检查环境健康状态
brew doctor

# 修复常见问题（如权限、PATH 错误）
brew cleanup
sudo chown -R $(whoami) $(brew --prefix)/*
```

---

在实际使用过程中，可能会遇到一些常见问题。以下是一些问题及其解决方案的汇总：

| 问题 | 解决方案 |
|------|----------|
| `command not found: brew` | 重启终端，或执行 `eval "$(/opt/homebrew/bin/brew shellenv)"` |
| 权限错误 `/opt/homebrew` | `sudo chown -R $(whoami):admin /opt/homebrew` |
| 安装卡在 `Updating Homebrew...` | 按 `Ctrl+C` 取消，配置国内镜像源后重试 |
| `Error: Cannot install under Rosetta 2` | 确保终端以原生 ARM 模式运行（非 Rosetta） |
| 卸载 Homebrew | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"` |

---

为了更好地使用 Homebrew，建议遵循以下最佳实践：

✅ **推荐做法：**
- 优先使用 `.pkg` 安装器，减少配置烦恼
- 定期执行 `brew update && brew upgrade && brew cleanup`
- 用 `Brewfile` 管理个人/团队开发环境
- 遇到问题先运行 `brew doctor` 诊断

❌ **避免做法：**
- 不要混用 `sudo brew`（Homebrew 设计为无 sudo 运行）
- 不要手动修改 `/opt/homebrew` 下的文件结构
- 不要同时使用多个镜像源（易导致冲突）

---

如需了解更多 Homebrew 的信息，可以参考以下资源：

- 官方文档：https://docs.brew.sh
- 公式仓库：https://github.com/Homebrew/homebrew-core
- Cask 仓库：https://github.com/Homebrew/homebrew-cask
- 社区论坛：https://github.com/Homebrew/discussions

---

Homebrew 不仅是软件安装工具，更是现代开发者的工作流基石。掌握它，意味着你能在几分钟内搭建起完整的开发环境，告别繁琐的手动配置。

> 🚀 **行动建议**：现在就打开终端，执行 `brew install just`，用 justfile 管理你的常用命令，体验效率飞跃！

```bash
# 创建你的第一个 justfile
echo 'hello:
    echo "Hello from Homebrew!"' > justfile
just hello
```

Happy Brewing! 🍻

# Homebrew 为什么它是 macOS 上的必备工具

Homebrew 是一款 macOS（现在也支持 Linux）的**包管理器**（Package Manager），它的口号是“macOS 缺失的软件包的管理器”。对于任何想要深度掌握 macOS 的用户（尤其是开发者、设计师或极客）来说，Homebrew 几乎是“必装”的神器。

你可以把 **Homebrew** 理解为 macOS 上的“软件管家”或“应用商店”，但它是通过**命令行（Terminal）**来运作的，而且比普通的 App Store 强大得多。以下是关于 Homebrew 的全方位解读，包括你提到的一系列问题，以及我认为你需要知道的额外信息。

Homebrew 的特点包括：

- **极简操作：** 不需要去浏览器搜索官网、下载 `.dmg` 文件、拖拽到 Applications 文件夹。一行命令搞定一切。
- **依赖管理（杀手级特性）：** 很多软件需要依赖其他的小程序库才能运行。如果你手动安装，经常会遇到“缺少 xxx 库”的报错。Homebrew 会自动把这些“依赖包”全部帮你下载并配置好。
- **沙盒安装：** Homebrew 会将软件包安装到独立目录（Apple Silicon 芯片在 `/opt/homebrew`，Intel 芯片在 `/usr/local/Cellar`），然后通过“软链接”整合到系统里。这意味着它不会弄乱你的系统核心文件，删除时也能删得很干净。
- **开源免费：** 它完全由社区驱动，配方（Formulae）更新速度极快。

如果你只是偶尔装个微信或 Word，可能不需要它。但如果你有以下需求，它是必须的：

1. **安装开发者工具：** 比如 Python, Node.js, Git, MySQL 等。这些工具在 App Store 里找不到，去官网下载配置环境变量又非常麻烦，Homebrew 能一键搞定。
2. **统一管理与更新：** 你的电脑里装了50个软件，怎么更新？一个一个打开检查更新吗？用 Homebrew，只需要输入 `brew upgrade`，所有通过它安装的软件都会自动升级到最新版。
3. **脚本化部署：** 如果你换了新 Mac，不需要花一天时间重新下载软件。你可以导出一个 Homebrew 列表文件，在新电脑上运行一行命令，所有软件自动装好。

虽然 Homebrew 是目前 macOS 上最主流的选择，但也有其他替代品：

| 替代品 | 特点 | 评价 |
| --- | --- | --- |
| **MacPorts** | 历史悠久，模仿 FreeBSD 的 Ports 系统。 | **更严谨**。它在完全独立的目录中编译和安装软件，不依赖 macOS 自带的库。这使得它更稳定，但占用空间更大，编译时间更长。 |
| **Nix** | 跨平台，基于纯函数式语言的包管理器。 | **更极客**。它非常强大，支持回滚版本、多版本共存，能保证环境绝对一致。但学习曲线极陡峭，适合高级开发者。 |
| **App Store** | 苹果官方商店。 | **更安全但受限**。适合普通用户下载日常 App，但不仅没有开发工具，且很多开源软件因为审核原因无法上架。 |
| **手动安装** | 下载 DMG/PKG 文件。 | **最原始**。难以管理更新，卸载往往残留垃圾文件。 |

**结论：** 对于 95% 的 macOS 用户，**Homebrew 是最佳选择**，因为它的社区最活跃，软件库最全。

除了基础功能，Homebrew 还有几个关键概念，理解它们能让你成为真正的“高阶用户”。

什么是 Cask？（Homebrew 的 GUI 扩展）

很多人以为 Homebrew 只能装黑底白字的命令行工具（如 Git）。其实不是！Homebrew 有一个扩展叫 **Homebrew Cask**。

- `brew install python` -> 安装的是**命令行工具**（配方 Formula）。
- `brew install --cask google-chrome` -> 安装的是**图形界面软件**（比如 Chrome, VS Code, IINA, Discord, 微信等）。
**这意味着你可以用 Homebrew 管理你电脑上几乎所有的软件。**

如何维护和清理？

Homebrew 下载安装包后，默认会保留旧版本的缓存。时间久了会占用几十 GB 空间。

- **常用命令：** `brew cleanup`
- 这个命令会删除所有过期的下载缓存和旧版本软件，瞬间释放大量磁盘空间。

- **常用命令：** `brew doctor`
- 如果你发现 Homebrew 报错，运行这个命令，它会像医生一样自动诊断问题并告诉你怎么修复。

Apple Silicon (M1/M2/M3) 的路径变化

如果你使用的是新款 Mac（M系列芯片），Homebrew 的安装路径发生了变化：

- **旧款 Intel Mac:** `/usr/local`
- **新款 M 芯片 Mac:** `/opt/homebrew`
这主要是为了避免与 macOS 自带的 Rosetta 转译机制冲突。虽然使用上没区别，但在配置环境变量时需要注意。

Brewfile (备份你的 Mac)

这是最酷的功能。你可以创建一个名为 `Brewfile` 的文本文件，里面写上：

```ruby
brew "git"
brew "node"
cask "google-chrome"
cask "visual-studio-code"
```

然后运行 `brew bundle`。Homebrew 就会按照这个清单自动把所有软件装好。这被称为 **"Infrastructure as Code" (基础设施即代码)**，是很多工程师配置新电脑的秘诀。

Homebrew 是 macOS 的**外挂级**装备。它让软件安装变得像手机应用商店一样简单，同时又保留了极高的可控性和专业性。

**想现在尝试一下吗？**
你只需要打开你的终端（Terminal），粘贴官方的一行安装代码即可开始。