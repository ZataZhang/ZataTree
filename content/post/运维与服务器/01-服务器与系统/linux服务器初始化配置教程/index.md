---
title: linux使用教程
description: ""
date: 2025-03-16T17:16:02+08:00
image: images/index/index.png
# image: images/index/index.png
categories:
    - Knowledge
tags:
    - Linux
    - 教程
---






## 服务器配置

### Ubuntu 初始化配置



```bash

## 1.设置密码并更新软件包
sudo passwd 
sudo apt update && sudo apt upgrade -y

## 2. 安装ssh-server
sudo apt install  openssh-server

## 3.配置ssh
vim /etc/ssh/sshd_config

# 常见配置项示例
Port 22                    # SSH 端口
PermitRootLogin no        # 禁止 root 登录
PasswordAuthentication yes # 允许密码认证
AllowUsers myuser # 允许特顶用户登录
Port 2222  #修改端口，减少扫描攻击

## 4.重启ssh服务
sudo systemctl restart ssh

## 5.创建用户(避免直接使用root账号)
adduser myuser
usermod -aG sudo myuser


## 6. 连接服务器
ssh root@服务器IP地址 -p [你自己设置的端口]

```



## 一些问题和解决方案

### Linux 下更改当前文件夹及所有内容所有者为 zata 用户

**目标**  
将当前文件夹及其下所有文件和子文件夹的所有者更改为 `zata` 用户。

**步骤**  
1. **打开终端**：按 `Ctrl + Alt + T`，使用 `cd /path/to/your/folder` 进入目标文件夹，确认路径：`pwd`。  
2. **更改所有者**：  
   ```bash
   sudo chown -R zata .
   ```  
   - `.` 表示当前文件夹，`-R` 递归更改所有内容。  
3. **（可选）设置权限**：只给 `zata` 读写权限：  
   ```bash
   sudo chmod -R 700 .
   ```  
4. **验证更改**：检查所有者和权限：  
   ```bash
   ls -la
   ```  

**注意事项**  
- 确认 `zata` 用户存在：`id zata`。若不存在，创建：`sudo adduser zata`。  
- 备份数据，避免误操作。  
- （可选）分配组：`sudo chown -R zata:groupname .`。



### bash: ping: command not found  问题

```bash
apt-get update
apt install iputils-ping
apt install net-tools
```