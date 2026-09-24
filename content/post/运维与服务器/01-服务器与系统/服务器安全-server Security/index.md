---
title: 服务器安全-server Security
description: ""
date: 2026-03-09T13:54:43+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - Server Operations and Maintenance-服务器运维
---




这份教程的基础架构非常扎实，逻辑清晰。作为一个有追求的 AI 协作伙伴，我为你进行了**深度改写**。

这次改写的核心提升在于：

1. **交互感**：将枯燥的步骤转化为“闯关”体验。
2. **技术严谨性**：修正了 Ubuntu 系统中 `sshd_config.d` 覆盖配置的常见坑点。
3. **可读性**：使用更清晰的 Markdown 布局和视觉引导。

---

# 🛡️ Linux 服务器金钟罩：15 分钟全手工安全加固指南

> **写在前面：** 互联网上每秒有数万个脚本在扫描公网 IP。如果你的服务器还在用默认端口、弱密码、开着 Root 登录，那不是“会不会被黑”的问题，而是“什么时候被黑”的问题。

### 🚨 终极保命准则

**操作期间，千万不要断开当前的 SSH 窗口！**
每完成一步加固，务必**新开一个终端窗口**测试能否登录。确认无误后，再继续下一步。

---

## 第一阶段：深度体检（寻找破绽）

我们先通过一个自检脚本，看看你的服务器在黑客眼中长什么样。

1. **创建检测脚本**：`nano security_check.sh`
2. **填入代码**：



```bash
#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}       服务器基础安全配置自检脚本 (只读模式)      ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] 请使用 sudo 运行此脚本 (例如: sudo bash security_check.sh)${NC}"
  exit 1
fi

echo -e "\n${YELLOW}[1] 正在检查 SSH 安全配置...${NC}"
SSH_PORT=$(sshd -T | grep -w "^port" | awk '{print $2}')
SSH_ROOT_LOGIN=$(sshd -T | grep -w "^permitrootlogin" | awk '{print $2}')
SSH_PASS_AUTH=$(sshd -T | grep -w "^passwordauthentication" | awk '{print $2}')

if [ "$SSH_PORT" == "22" ]; then
    echo -e " 🔴 SSH 端口: $SSH_PORT (默认端口, 易被扫描)"
else
    echo -e " 🟢 SSH 端口: $SSH_PORT (已修改为非标准端口)"
fi

if [ "$SSH_ROOT_LOGIN" == "yes" ]; then
    echo -e " 🔴 Root 直接登录: 允许 (极高风险, 容易被爆破 root 密码)"
else
    echo -e " 🟢 Root 直接登录: 禁止"
fi

if [ "$SSH_PASS_AUTH" == "yes" ]; then
    echo -e " 🔴 密码登录: 允许 (高风险, 建议改用密钥登录)"
else
    echo -e " 🟢 密码登录: 禁止 (安全, 已启用纯密钥登录)"
fi

echo -e "\n${YELLOW}[2] 正在检查防火墙状态...${NC}"
if command -v ufw > /dev/null 2>&1; then
    UFW_STATUS=$(ufw status | grep -i "Status: active\|状态： 激活")
    if [ -n "$UFW_STATUS" ]; then
        echo -e " 🟢 防火墙 (UFW): 已启用"
    else
        echo -e " 🔴 防火墙 (UFW): 未启用!"
    fi
elif command -v firewall-cmd > /dev/null 2>&1; then
    FW_STATUS=$(firewall-cmd --state 2>/dev/null)
    if [ "$FW_STATUS" == "running" ]; then
        echo -e " 🟢 防火墙 (Firewalld): 已启用"
    else
        echo -e " 🔴 防火墙 (Firewalld): 未启用!"
    fi
else
    echo -e " 🔴 未检测到 UFW 或 Firewalld 防火墙工具!"
fi

echo -e "\n${YELLOW}[3] 正在检查防爆破工具 (Fail2ban)...${NC}"
if systemctl is-active --quiet fail2ban; then
    echo -e " 🟢 Fail2ban: 正在运行 (防爆破保护中)"
else
    echo -e " 🔴 Fail2ban: 未安装或未运行!"
fi

echo -e "\n${YELLOW}[4] 正在检查对外暴露的端口 (仅列出监听状态的 TCP 端口)...${NC}"
echo -e "请检查以下端口是否都是你主动开放的？（数据库如3306不应暴露在0.0.0.0）"
netstat_out=$(ss -tulnp | grep tcp | grep LISTEN)
if [ -z "$netstat_out" ]; then
    echo -e " 🟡 未检测到监听中的 TCP 端口"
else
    ss -tulnp | grep tcp | grep LISTEN | awk '{print " - 协议:"$1" | 监听地址:"$5" | 进程:"$7}' | sed 's/users:(("//g' | sed 's/".*//g'
fi

echo -e "\n${YELLOW}[5] 正在检查特权用户...${NC}"
SUPER_USERS=$(awk -F: '($3 == "0" && $1 != "root") {print $1}' /etc/passwd)
if [ -z "$SUPER_USERS" ]; then
    echo -e " 🟢 UID为0的用户: 只有 root (正常)"
else
    echo -e " 🔴 警告! 发现其他具有最高权限的用户: $SUPER_USERS"
fi

echo -e "\n${YELLOW}==================================================${NC}"
echo -e "${YELLOW} 检查完成！请根据 🔴红色的警告项 进行下一步修改。 ${NC}"
echo -e "${YELLOW}==================================================${NC}"
```

3. **赋予权限并执行**：
```bash
chmod +x security_check.sh
sudo ./security_check.sh

```



**你的目标：** 消除所有的 🔴，迎接满屏的 🟢。

---

## 第二阶段：五步锁死安全之门

### 第 1 步：建立“安全通道”（创建 sudo 用户与密钥）

**严禁**直接在 Root 账户下裸奔。

1. **创建新管理账号**：
```bash
adduser armoradmin  # 名字随你起
usermod -aG sudo armoradmin

```


2. **注入 SSH 密钥**（在你的**本地电脑**执行）：
```bash
ssh-keygen -t ed25519 -C "server_key"  # 推荐 ed25519 算法，更短更安全
ssh-copy-id -i ~/.ssh/id_ed25519.pub armoradmin@服务器IP

```


*测试：`ssh armoradmin@服务器IP`，无需密码直接进入即为成功。*

---

### 第 2 步：斩断“后门”（收紧 SSH 配置）

这是最关键的一步。我们要让密码爆破彻底失效。

1. **注意 Ubuntu 特有的坑**：
检查 `/etc/ssh/sshd_config.d/` 下是否有 `.conf` 文件。如果有，里面的配置会优先于主配置。建议直接清理或同步修改。
2. **修改主配置**：`sudo nano /etc/ssh/sshd_config`
```text
# 核心三要素
PermitRootLogin no             # 禁止 Root 登录
PasswordAuthentication no      # 禁止密码登录（关键！）
KbdInteractiveAuthentication no # 彻底切断交互式认证

# 进阶项
Port 22222                     # 修改默认端口（记得在防火墙放行新端口！）

```

*注意* 如果 /etc/ssh/sshd_config.d/ 目录下有任何以 .conf 结尾的文件（比如云厂商预设的配置），它们的内容会覆盖掉你在主配置文件里的修改。


 - 检查方法：ls /etc/ssh/sshd_config.d/

 - 检查密码登录是否已禁用：sshd -T | grep passwordauthentication


3. **检查并重启**：
```bash
sudo sshd -t && sudo systemctl restart ssh

```



---

### 第 3 步：架起“护城河”（UFW 防火墙）

别让你的 Docker 容器或数据库在公网“裸奔”。

1. **初始化策略**：
```bash
sudo ufw default deny incoming  # 默认拒绝所有入站
sudo ufw default allow outgoing # 默认允许所有出站

```


2. **精准开门**：


关于docker swarm
```bash
# 允许 B 服务器访问我的 Swarm 端口
sudo ufw allow from 2.2.2.2 to any proto tcp port 2377,7946
sudo ufw allow from 2.2.2.2 to any proto udp port 7946,4789

# 允许 C 服务器访问我的 Swarm 端口
sudo ufw allow from 3.3.3.3 to any proto tcp port 2377,7946
sudo ufw allow from 3.3.3.3 to any proto udp port 7946,4789
```


```bash
sudo ufw allow 22222/tcp  # 换成你修改后的 SSH 端口！
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS

```


3. **合闸开启**：
```bash
sudo ufw enable

```



---

### 第 4 步：部署“自动保安”（Fail2ban）

Fail2ban 会自动关押那些尝试试探你端口的 IP。

1. **安装并启动**：
```bash
sudo apt install fail2ban -y
sudo systemctl enable --now fail2ban

```


2. **默认保护**：它会自动保护 SSH。你可以通过 `sudo fail2ban-client status sshd` 查看又有多少倒霉蛋被你关进了“小黑屋”。

---

### 第 5 步：内鬼肃清（清理特权用户与危险监听）

1. **监听自查**：运行 `ss -tulnp`。如果看到 `0.0.0.0:3306`，请立即去数据库配置里把 `bind-address` 改为 `127.0.0.1`。
2. **权限自查**：如果脚本提示有除 root 以外的 UID 0 用户，**别犹豫，你的系统大概率已经“不干净”了**。

---

## 第三阶段：最后验收

现在，再次运行你的自检脚本：

```bash
sudo ./security_check.sh

```

---

### 💡 维护锦囊

* **定期更新**：养成每周 `sudo apt update && sudo apt upgrade` 的好习惯。
* **监控日志**：偶尔看看 `/var/log/auth.log`，你会惊讶于外面的世界有多疯狂。

**加固完成了！需要我帮你写一个自动导出安全日志的定时任务脚本吗？**