---
title: nvm
description: ""
date: 2026-02-05T16:53:23+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftTrial
---




# 安装使用


```bash
cd ~  # Switch to Linux Home Directory

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash   #  Install Node.js via NVM (Recommended)

#或者如果网络不行，使用下面的国内镜像去拉取
# curl -o- https://cdn.jsdelivr.net/gh/nvm-sh/nvm@v0.40.3/install.sh | bash

# 如果还是不行，应该是解析的问题
# 查看raw.githubusercontent.com的解析地址，如果是0.0.0.0就是有问题的，使用sudo apt install dnsutils 安装nslookup
#nslookup raw.githubusercontent.com

# 如果是解析问题，使用 Google DNS（8.8.8.8）, 修改好解析之后在进行上一步
#echo "nameserver 8.8.8.8" | tee /etc/resolv.conf  

. "$HOME/.nvm/nvm.sh"  # Activate NVM without restarting:

nvm install 20  # Install Node.js version 20 (LTS):

node --version && npm --version  #  Verify Installation
```