---
title: tmux简易使用
description: "从零开始掌握 tmux：会话、窗口、窗格、复制模式与常用配置，打造不掉线的终端工作环境。"
date: 2025-05-09T11:32:28+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftUseExp
    - 简易使用
---

## 安装

### macOS

```bash
# 用 Homebrew（推荐）
brew install tmux

# 用 MacPorts
sudo port install tmux
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install tmux
```

> Ubuntu 自带的 tmux 版本通常较老（1.8），功能受限。需要新版（如 3.x 的 true color 支持等）可以加 PPA：
>
> ```bash
> sudo add-apt-repository ppa:tmux-stable/ppa
> sudo apt update
> sudo apt install tmux
> ```

### Windows

Windows 原生没有 tmux，常见方案：

- **WSL（推荐）**：在 WSL（Ubuntu 等发行版）里 `sudo apt install tmux`，然后通过 Windows Terminal 使用。
- **MSYS2**：自带包管理器：
  ```bash
  pacman -S tmux
  ```
- 不愿用 Linux 子系统的话，可考虑 Windows Terminal 自带的 panes/tabs 作为替代。

### 验证安装

```bash
tmux -V
```

输出形如 `tmux 3.4` 即安装成功。

---

## 什么是 tmux

tmux（Terminal Multiplexer）是一个终端复用器。它允许你在一个终端窗口里运行多个会话（session），每个会话里又能打开多个窗口（window）和窗格（pane）。最实用的好处是：**关闭 SSH 连接或终端窗口后，tmux 会话里的程序仍在后台运行，下次可以原样恢复**。

## 为什么用 tmux

- **会话持久化**：远程服务器上跑长任务，断开 SSH 也不会中断。
- **一屏多用**：把屏幕拆成多个窗格，同时看日志、跑测试、编辑代码。
- **环境快速恢复**：一套窗口/窗格布局保存后，下次一键还原。
- **协作/演示**：多人 attach 到同一会话，方便结对调试。

## 常用命令速查

最常用的几条命令，记住它们就能应付日常 80% 的场景：

```bash
# 创建并进入会话
tmux new -s mysession

# 列出所有会话
tmux ls

# 重新进入会话
tmux attach -t mysession

# 临时退出会话（后台运行）
# 快捷键：Ctrl-b 松开后按 d

# 重命名当前会话
tmux rename-session 新名字

# 重命名指定会话
tmux rename-session -t 旧名字 新名字

# 彻底关闭某个会话
tmux kill-session -t mysession
```

快捷键速记：

| 快捷键 | 作用 |
|--------|------|
| `Ctrl-b d` | 退出会话（ detach，程序继续在后台跑） |
| `Ctrl-b $` | 重命名当前会话 |
| `Ctrl-b c` | 新建窗口 |
| `Ctrl-b n` / `Ctrl-b p` | 下一个 / 上一个窗口 |
| `Ctrl-b %` | 垂直分屏 |
| `Ctrl-b "` | 水平分屏 |
| `Ctrl-b o` | 切换到下一个窗格 |
| `Ctrl-b x` | 关闭当前窗格 |

---

## 基础概念

| 概念 | 说明 |
|------|------|
| 会话（session） | 最高级容器，通常对应一个完整的工作场景，例如“前端开发”“服务器运维”。 |
| 窗口（window） | 会话内的标签页，类似浏览器标签。 |
| 窗格（pane） | 窗口内的分屏区域，一个窗口可分成多个窗格。 |

默认**前缀键（prefix）**是 `Ctrl-b`，所有快捷键都要先按 prefix，松开后按功能键。

## 会话管理

```bash
# 创建无名称会话
tmux

# 创建带名称的会话
tmux new -s mysession

# 在创建时直接执行命令（命令结束会话不关闭）
tmux new -s build -d "npm run build"

# 列出所有会话
tmux ls

# 附加到已有会话
tmux attach -t mysession
# 简写
tmux a -t mysession

# 从外部重命名会话
tmux rename-session -t oldname newname

# 分离当前会话（后台运行，不关闭）
# 快捷键：prefix + d
tmux detach

# 杀死指定会话
tmux kill-session -t mysession

# 杀死所有会话
tmux kill-server
```

### 会话快捷键

| 快捷键 | 作用 |
|--------|------|
| `prefix d` | 分离当前会话 |
| `prefix $` | 重命名当前会话 |
| `prefix s` | 列出所有会话，用方向键选择切换 |
| `prefix (` | 切换到上一个会话 |
| `prefix )` | 切换到下一个会话 |

## 窗口管理

| 快捷键 | 作用 |
|--------|------|
| `prefix c` | 新建窗口 |
| `prefix ,` | 重命名当前窗口 |
| `prefix n` | 切换到下一窗口 |
| `prefix p` | 切换到上一窗口 |
| `prefix 0~9` | 切换到对应编号窗口 |
| `prefix w` | 可视化选择窗口 |
| `prefix &` | 关闭当前窗口 |
| `prefix .` | 修改当前窗口编号 |

命令行操作：

```bash
# 创建窗口
tmux new-window -t mysession -n "logs"

# 关闭窗口
tmux kill-window -t mysession:1
```

## 窗格管理

| 快捷键 | 作用 |
|--------|------|
| `prefix %` | 垂直分割窗格 |
| `prefix "` | 水平分割窗格 |
| `prefix o` | 切换到下一个窗格 |
| `prefix 方向键` | 切换到对应方向窗格 |
| `prefix x` | 关闭当前窗格 |
| `prefix z` | 最大化/还原当前窗格 |
| `prefix 空格` | 切换窗格布局 |
| `prefix {` / `prefix }` | 移动当前窗格位置 |
| `prefix !` | 把当前窗格拆成独立窗口 |

调整窗格大小：

| 快捷键 | 作用 |
|--------|------|
| `prefix Ctrl+方向键` | 以 1 格为单位调整 |
| `prefix Alt+方向键` | 以 5 格为单位调整 |

## 复制模式

tmux 自带复制/滚动模式，方便查看历史输出。

| 快捷键 | 作用 |
|--------|------|
| `prefix [` | 进入复制模式 |
| `prefix ]` | 粘贴缓冲区内容 |
| `prefix =` | 列出粘贴历史 |

复制模式下常用操作：

| 按键 | 作用 |
|------|------|
| `Ctrl-c` / `q` | 退出复制模式 |
| `Ctrl-f` / `Ctrl-b` | 向下/向上翻页 |
| `/` | 向下搜索 |
| `?` | 向上搜索 |
| `v` | 开始选区（vi 模式下） |
| `y` | 复制选区（vi 模式下） |

让 tmux 使用 vi 风格键位：

```bash
# ~/.tmux.conf
setw -g mode-keys vi
```

## 常用配置

创建或编辑 `~/.tmux.conf`：

```bash
# 重新加载配置的快捷键
bind r source-file ~/.tmux.conf \; display-message "Config reloaded!"

# 启用鼠标支持（滚轮、拖拽调整窗格、点击选择窗格）
set -g mouse on

# 把前缀键改成 Ctrl-a（更接近 GNU Screen 习惯）
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# 使用 vi 风格复制模式
setw -g mode-keys vi

# 窗口编号从 1 开始
set -g base-index 1
setw -g pane-base-index 1

# 重新编号窗口（删除中间窗口后自动补齐）
set -g renumber-windows on

# 状态栏显示时间
set -g status-right '%Y-%m-%d %H:%M'

# 窗格边框颜色
set -g pane-border-style fg=colour240
set -g pane-active-border-style fg=colour33
```

配置修改后，可以在 tmux 里按 `prefix r` 重新加载，或执行：

```bash
tmux source-file ~/.tmux.conf
```

## 推荐插件

使用 [Tmux Plugin Manager（TPM）](https://github.com/tmux-plugins/tpm) 管理插件更方便。

安装 TPM：

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

在 `~/.tmux.conf` 末尾加入：

```bash
# 插件列表
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'      # 保存/恢复会话
set -g @plugin 'tmux-plugins/tmux-continuum'      # 自动保存

# 初始化 TPM（必须放在文件最后）
run '~/.tmux/plugins/tpm/tpm'
```

常用插件说明：

| 插件 | 作用 |
|------|------|
| `tmux-sensible` | 一组合理的默认配置 |
| `tmux-resurrect` | 保存和恢复会话、窗口、窗格布局及运行程序 |
| `tmux-continuum` | 自动定时保存，开机后自动恢复 |
| `tmux-yank` | 把 tmux 选区复制到系统剪贴板 |
| `tmux-prefix-highlight` | 在状态栏高亮显示前缀键状态 |

安装插件：先按 `prefix I`（大写 i）。

## 实用工作流示例

### 1. 远程跑长任务

```bash
ssh server
tmux new -s training
# 在会话里执行训练脚本
python train.py
# 按 prefix d 分离，关闭 SSH 即可
```

下次恢复：

```bash
ssh server
tmux attach -t training
```

### 2. 本地开发多面板

```bash
tmux new -s dev
```

然后按 `prefix %` 把窗口分成左右两部分：左边跑编辑器/服务器，右边跑测试或日志。

### 3. 快速保存与恢复环境

安装 `tmux-resurrect` 后：

| 快捷键 | 作用 |
|--------|------|
| `prefix Ctrl-s` | 保存当前环境 |
| `prefix Ctrl-r` | 恢复保存的环境 |

## 进阶技巧

### 1. 同步输入到所有窗格

需要在多台机器或同一组窗口里执行相同命令时，可以打开**输入同步**：

```bash
# 在 tmux 命令行执行
setw synchronize-panes on
```

快捷键绑定（加入 `~/.tmux.conf`）：

```bash
bind S setw synchronize-panes \; display-message "Sync panes: #{?synchronize-panes,ON,OFF}"
```

然后按 `prefix S` 即可切换同步状态。再次关闭：`setw synchronize-panes off`。

### 2. 用脚本一键搭建开发环境

把常用布局写成脚本，避免每次手动分屏：

```bash
#!/bin/bash
# start-dev.sh
SESSION="dev"

tmux has-session -t $SESSION 2>/dev/null
if [ $? != 0 ]; then
    tmux new-session -d -s $SESSION -n editor
    tmux send-keys -t $SESSION:editor 'vim .' C-m
    tmux split-window -h -t $SESSION:editor
    tmux send-keys -t $SESSION:editor.right 'npm run dev' C-m
    tmux split-window -v -t $SESSION:editor.right
    tmux send-keys -t $SESSION:editor.bottom 'git status' C-m
fi

tmux attach -t $SESSION
```

### 3. 嵌套 tmux（本地 + 远程）

如果你本地开了 tmux，SSH 到远程服务器后又开了 tmux，两个 `Ctrl-b` 会冲突。常见解决办法：

- 本地用 `Ctrl-b`，远程用 `Ctrl-a`：
  ```bash
  # 远程服务器的 ~/.tmux.conf
  set -g prefix C-a
  unbind C-b
  bind C-a send-prefix
  ```
- 或者在本地 tmux 里按 `Ctrl-b b`，把 prefix 透传给远程 tmux。

### 4. 查看并重新连接 detached 的会话

```bash
# 列出 detached 的会话
tmux ls

# 如果只有一个 detached 会话，直接 attach
tmux attach
```

### 5. 调整颜色与终端兼容

如果 vim/neovim 在 tmux 里颜色显示异常，加这几行：

```bash
# ~/.tmux.conf
set -g default-terminal "screen-256color"
set -ag terminal-overrides ",xterm-256color:RGB"
```

并确保外部终端也支持 256 色 / true color。

## 命令速查表

```bash
# 会话
tmux new -s <name>          # 新建会话
tmux ls                      # 列出会话
tmux attach -t <name>        # 接入会话
tmux detach                  # 退出当前会话（后台运行）
tmux rename-session -t <old> <new>  # 重命名会话
tmux kill-session -t <name>  # 结束会话
tmux kill-server             # 结束所有会话

# 窗口（在 tmux 内）
prefix c   # 新建窗口
prefix ,   # 重命名窗口
prefix n   # 下一个窗口
prefix p   # 上一个窗口
prefix w   # 可视化选择窗口
prefix 0-9 # 切换到对应编号窗口
prefix &   # 关闭窗口

# 窗格（在 tmux 内）
prefix %   # 垂直分割
prefix "   # 水平分割
prefix o   # 切换窗格
prefix 方向键 # 按方向切换窗格
prefix x   # 关闭窗格
prefix z   # 最大化/还原窗格
prefix 空格 # 切换窗格布局
prefix !   # 把当前窗格拆成独立窗口

# 复制模式
prefix [   # 进入复制/滚动模式
prefix ]   # 粘贴
```

## 常见问题

| 问题 | 原因 / 解决 |
|------|-------------|
| 滚轮不能翻历史 | 按 `prefix [` 进入复制模式后再滚；或开启 `set -g mouse on`。 |
| `Ctrl-b` 没反应 | 先松开 `Ctrl-b` 再按功能键；或者 prefix 被改成了 `Ctrl-a`。 |
| 中文显示乱码 | 检查终端编码为 UTF-8，并在 `~/.tmux.conf` 里加 `setw -g utf8 on`（较新版本已默认支持）。 |
| vim 里按 ESC 有延迟 | 加 `set -sg escape-time 10` 到 `~/.tmux.conf`。 |
| 关闭终端后程序被杀死 | 确保程序是跑在 tmux 会话里，并且你是按 `prefix d` 分离，而不是直接关窗口。 |
| 状态栏不显示 | 确认配置文件没有语法错误，执行 `tmux source-file ~/.tmux.conf` 查看报错。 |

## 小贴士

1. **先松 prefix 再按功能键**：例如 `Ctrl-b` 松开后按 `c`。
2. **善用 `prefix ?`**：随时查看所有快捷键列表。
3. **调整终端大小后**，tmux 会自动适配；如果显示异常，可以按 `prefix r` 刷新。
4. **tmux 默认不共享系统剪贴板**，需要 `tmux-yank` 或配合 `xclip`/`pbcopy` 等工具。
5. **鼠标支持开启后**，可以像普通终端一样滚屏、拖拽调整窗格大小，适合新手过渡。
