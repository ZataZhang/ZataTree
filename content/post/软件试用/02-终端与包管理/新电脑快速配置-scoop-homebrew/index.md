---
title: 新电脑快速配置-scoop
description: ""
date: 2026-02-10T11:59:09+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftUseExp
---





# windows (注意要最好打开clash的TUN模式)

1. 必备开发工具安装：

    ```powershell
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
    ```powershell
    irm get.scoop.sh | iex
    ```
    ```powershell
    scoop install git uv just nvm
    ```
    安装wsl,执行命令,然后重启电脑,使用管理员打开powershell,输入wsl ---- [官方教程](https://learn.microsoft.com/en-us/windows/wsl/install)
    ```powershell
    wsl --install
    ```
    进入wsl后必须安装
    ```bash
    sudo apt update
    sudo apt install git just -y
    curl -LsSf https://astral.sh/uv/install.sh | sh
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    ```
    
    

2. 必安装软件

    - [vscode下载地址](https://code.visualstudio.com/insiders)
    - [docker下载地址](https://www.docker.com/get-started/)
    - [clash下载地址](https://github.com/clash-verge-rev/clash-verge-rev)
    - [cherry studio下载地址](https://docs.cherry-ai.com/cherry-studio/download)
    - [cc-swith下载地址](https://github.com/farion1231/cc-switch/releases)
    - [claude code下载地址 --- 最好开tun模式或者设置代理端口环境变量](https://code.claude.com/docs/en/overview)
    - [codex下载地址](https://developers.openai.com/codex/cli/)




3. 额外插件安装

- 智能桌面助手--主要功能是查看当前输入法是中/英文

    [ImTip 智能桌面助手](https://github.com/aardio/ImTip) 