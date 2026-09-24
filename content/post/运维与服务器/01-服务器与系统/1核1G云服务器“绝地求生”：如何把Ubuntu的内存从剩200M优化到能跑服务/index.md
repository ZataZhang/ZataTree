---
title: 1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务
description: ""
date: 2026-02-22T20:11:29+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - Linux
---



# [实战] 1核1G云服务器“绝地求生”：如何把Ubuntu的内存从剩200M优化到能跑服务？

**【前言：年轻人的第一台云服务器】**

趁着云厂商搞活动，你是不是也入手了一台 **1核 1G** 的“入门级”云服务器？

你满怀期待地装上了最新的 Ubuntu LTS，准备大干一场（建博客、跑脚本、练Linux）。结果刚连上 SSH，随手敲了一个 `free -h`，当场心凉了一半：

> **Total: 980Mi | Used: 700Mi | Free: 200Mi**

还没跑任何业务，系统纯待机就吃掉了近 800M 内存，只剩下 200M 还能干嘛？跑个 `apt update` 都怕卡死，更别提装 MySQL 了。

别急着重装系统，在 1G 内存的极限环境下，我们需要掌握一些 **Linux 精细化运维** 的技巧。本文将手把手教你如何榨干这台服务器的每一滴性能。

---

**【第一阶段：ICU 急救（配置 Swap）】**

剩下 200M 内存最大的风险是什么？是 **OOM (Out Of Memory)**。一旦内存耗尽，Linux 内核会启动 OOM Killer，随机杀掉占用内存最高的进程（通常就是你的数据库或 Web 服务）。

**Swap（虚拟内存）** 是小内存服务器的救命稻草。虽然硬盘读写比内存慢几个数量级，但它能保证系统“卡顿”而不是“宕机”。

**操作步骤：**

1. **创建 2G 的 Swap 文件**（一般设置为物理内存的 1-2 倍）：
```bash
sudo fallocate -l 2G /swapfile
```

2. **设置权限并格式化**：
```bash
sudo chmod 600 /swapfile
sudo mkswap /swapfile
```

3. **启用 Swap**：
```bash
sudo swapon /swapfile
```

4. **设置开机自启**（重要，否则重启失效）：
```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

5. **调整 Swappiness（使用倾向）**：
默认值是 60，意味着内存用到 40% 就开始用 Swap。对于 1G 内存，我们希望尽量用物理内存，满了再用 Swap，防止频繁 IO 卡死系统。建议设为 10。
```bash
sudo sysctl vm.swappiness=10
```

**永久生效（写入配置文件）：**
```bash
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

> **效果：** 现在你拥有了 1G 内存 + 2G 虚拟内存，至少不用担心程序一启动就暴毙了。

---

**【第二阶段：卸载“内存刺客” Snapd】**

如果你用的是 Ubuntu，那么内存占用高的罪魁祸首通常是 **Snap**。

Ubuntu 官方为了推行 Snap 包管理，默认在后台运行 `snapd` 服务，并挂载了一堆 loop device。这在 16G 内存的电脑上没感觉，但在 1G 的服务器上简直是“吸血鬼”。

**优化方案：斩草除根**

如果你不强依赖 snap 安装软件（建议服务器端全用 apt 或 docker），请直接卸载它。

**第一步：停止服务**
```bash
sudo systemctl stop snapd
sudo systemctl disable snapd
```

**第二步：彻底卸载（耗时稍长，耐心等待）**
```bash
sudo apt autoremove --purge snapd -y
```

**第三步：阻止它自动回来（可选）**
```bash
sudo apt-mark hold snapd
```

> **效果：** 这一步通常能释放 **50M - 100M** 的纯物理内存，且 `df -h` 列表瞬间清爽了。

---

**【第三阶段：关闭非必要系统服务】**

Ubuntu Server 为了通用性，开了很多你可能根本用不上的服务。

**1. 关闭自动更新 (Unattended Upgrades)**
自动更新会在后台静默运行 apt，极度消耗 IO 和内存。小内存机器建议改为手动定期维护。
```bash
sudo systemctl stop unattended-upgrades
sudo systemctl disable unattended-upgrades
```

**2. 移除 Cloud-init**
如果是云服务器，`cloud-init` 仅在第一次创建实例时有用（用于注入 SSH Key、设置 hostname 等）。之后它就是个累赘。
```bash
sudo touch /etc/cloud/cloud-init.disabled
sudo apt purge cloud-init -y
```

**3. 限制系统日志**
`systemd-journald` 可能会占用大量内存做日志缓存。
编辑 `/etc/systemd/journald.conf`，修改或添加：
```ini
SystemMaxUse=50M
```
然后重启服务：
```bash
sudo systemctl restart systemd-journald
```

---

**【第四阶段：软件选型的智慧】**

在 1G 内存上，软件的选择比优化更重要。**不要试图挑战物理定律。**

**1. 数据库：告别 MySQL 8.0**
MySQL 8.0 默认配置启动空载就要 400M+ 内存，加上系统本身，直接爆内存。
* **青铜方案**：使用 **MariaDB**，并修改 `my.cnf`，将 `innodb_buffer_pool_size` 调低至 64M 或 128M。
* **王者方案**：使用 **SQLite**。如果你的业务是个人博客（Typecho, Hexo）、简单的 CMS 或测试项目，SQLite 是文件型数据库，**0 内存常驻**，性能在低并发下甚至优于 MySQL。

**2. Web 服务器：Nginx 是唯一真神**
不要用 Apache，它的进程模型比较吃资源。Nginx 或 Caddy 是小内存服务器的最佳拍档。

**3. 编程语言环境**
* **Java**: 尽量避开。JVM 是内存黑洞。
* **Python/Node**: 勉强可以，控制依赖数量。
* **Go/Rust**: 完美适配，编译后的二进制文件占用极小。
* **PHP**: 可以用，但需要调整 `php-fpm` 配置，限制 `pm.max_children` 为 5 左右，防止并发来了把内存撑爆。

---

**【终极方案：换个“瘦”点的系统】**

如果经过上述优化，Ubuntu 依然让你感到捉襟见肘，那么问题可能不在你，而在 Ubuntu。

Ubuntu 是一个“胖”系统，为了易用性塞了太多东西。如果你的目标是 **极致省资源**，建议重装系统：

* **推荐：Debian 11/12**
Debian 是 Ubuntu 的上游，极其稳定且纯净。同样的 1G 配置，Debian 11 启动后内存占用通常只有 **70M - 120M**。这直接给你省出了 600M+ 的空间！

* **极限：Alpine Linux**
空载仅需 **10M** 内存。但它是基于 musl libc 的，命令习惯和软件兼容性（特别是 glibc 依赖）需要一定门槛，适合 Docker 容器化部署。

---

**【总结】**

**1核 1G 并不是电子垃圾**，它依然可以跑得很欢快。

1. **先加 Swap**，保命要紧。
2. **卸载 Snap**，释放资源。
3. **精简服务**，关掉自动更新。
4. 如果可能，**重装成 Debian**。

只要配置得当，这台小机器跑一个日均 IP 1000 的博客、挂个探针、跑个签到脚本依然是绰绰有余的。


# [选型指南] 1 核 1G 云服务器，装 Ubuntu、Debian 还是 CentOS？

这是一个为你定制的博客文章，专门针对那些在 **“云服务器装什么系统”** 这个问题上纠结的用户。

这篇文章延续了之前的硬核实战风格，重点对比了主流发行版在**小内存（1 核 1G/2G）**场景下的表现，帮你做出最理性的选择。

---

**前言：你的起跑线决定了终点**

当你花 99 块钱买了一台 1 核 1G 的入门级云服务器时，你其实正站在一个岔路口。

很多人觉得：“反正都是 Linux，随便装一个不就行了？”
**大错特错。**

在 16G 内存的电脑上，系统本身占 500M 还是 100M 你感觉不到区别；但在 1G 内存的服务器上，这 **400M 的差距**，就是“能不能跑得动 Docker"或者“数据库会不会半夜崩溃”的生死线。

今天我们就来一场 **Linux 发行版大乱斗**，看看谁才是小内存 VPS 的“真命天子”。

---

**选手一：Ubuntu Server (特别是 20.04/22.04)**

**标签：** `网红` `资源大户` `生态最好`

Ubuntu 无疑是目前最流行的发行版。它的社区极其强大，你遇到任何问题，百度/谷歌搜出来的教程 80% 都是基于 Ubuntu 的。

*   **优点：** 
    *   教程多，遇到报错容易解决。
    *   PPA 软件源丰富，想装最新版 Node.js 或 Golang 非常容易。
    *   开箱即用，预装了 UFW、Sudo 等工具。
*   **缺点（致命）：** 
    *   **胖。** 真的很胖。
    *   为了推广自家的 Snap 包管理，强制后台运行 Snapd 守护进程，加上 Cloud-init 等云服务组件，**空载启动内存占用常年在 400MB - 600MB**。
    *   对于 1G 内存的机器，系统吃掉一半，剩下一半你还想跑 MySQL？做梦。

**适合人群：** 内存 ≥ 4GB 的土豪，或者极其依赖某些 Ubuntu 独占教程的新手。

---

**选手二：Debian (推荐 11/12)**

**标签：** `极简` `稳定` `省内存的神`

Debian 是 Ubuntu 的“爸爸”（Ubuntu 基于 Debian 开发）。它去掉了 Ubuntu 那些花里胡哨的商业推广服务，保留了最纯粹的 Linux 核心。

*   **优点：**
    *   **极度省内存。** Debian 11 Server 空载启动仅需 **70MB - 120MB**。相比 Ubuntu，它直接为你省出了 300M+ 的“纯利润”。
    *   **极其稳定。** Debian 的稳定分支是以“稳如老狗”著称的，服务器跑几年不重启是常态。
    *   **无缝迁移。** 命令和 Ubuntu 99% 通用（都是 `apt`，都是 `systemd`），你会用 Ubuntu 就会用 Debian。
*   **缺点：**
    *   默认软件库的版本策略偏保守（比较旧），但可以通过添加源解决。
    *   极其纯净，可能需要你手动 `apt install sudo` 或 `apt install ufw`（但这其实是优点）。

**适合人群：** **1 核 1G / 2G 用户的首选。** 懂点基础 Linux 的人。

---

**选手三：CentOS (及 AlmaLinux / Rocky Linux)**

**标签：** `企业级` `老派` `正在消亡`

曾经的服务器霸主，互联网公司的标配。但自从 RedHat 宣布 **CentOS 7 停止维护** 且 CentOS 8 转为“上游测试版（Stream）”后，它的地位就在急剧下降。

*   **现状：**
    *   **CentOS 7：** 太老了，内核老，软件老，且已停止维护，**不推荐**。
    *   **CentOS Stream：** 激进的测试版，不适合生产环境。
    *   **AlmaLinux / Rocky Linux：** CentOS 的完美替代品，原汁原味的企业级 RHEL 体验。
*   **资源占用：** 介于 Debian 和 Ubuntu 之间，空载约 **200MB - 300MB**。
*   **缺点：**
    *   包管理器 `yum/dnf` 的速度体感上比 `apt` 慢。
    *   很多个人开发者的软件（如某些一键脚本、面板）现在优先适配 Debian/Ubuntu 系，CentOS 支持度在下降。

**适合人群：** 公司生产环境要求（必须兼容 RHEL）、正在学习红帽认证（RHCE）的同学。**个人小鸡不推荐。**

---

**选手四：Alpine Linux**

**标签：** `极端` `微型` `容器专家`

这是一个走极端路线的系统。它不是基于常见的 GNU 库（glibc），而是基于 musl libc。

*   **优点：**
    *   **小到离谱。** 空载内存占用仅 **5MB - 15MB**。
    *   镜像体积极小，下载秒完。
*   **缺点（劝退）：**
    *   **兼容性地狱。** 因为缺少 glibc，很多常见的二进制程序（如标准的 JDK、某些编译好的 Python 库）无法直接运行，会报错“文件不存在”。
    *   命令不同。它用 `apk` 安装软件，没有 `systemd`，很多习惯要改。

**适合人群：** Docker 深度玩家（作为容器底包）、极端资源匮乏环境、Linux 老鸟。**新手慎入。**

---

**总结：一张图告诉你怎么选**

| 特性 | **Ubuntu 20/22** | **Debian 11/12** | **CentOS 7/Alma** | **Alpine** |
| :--- | :--- | :--- | :--- | :--- |
| **空载内存** | 400MB+ (胖) | **80MB - 120MB (优)** | 200MB+ (中) | 10MB (神) |
| **命令习惯** | `apt` (主流) | `apt` (同上) | `yum/dnf` | `apk` |
| **软件新旧** | 新 | 稳 (偏旧) | 旧/稳 | 新 |
| **上手难度** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **1G 机器推荐**| ❌ 不推荐 | ✅ **强烈推荐** | ⭕ 勉强可用 | ⚠️ 仅限专家 |

**最终建议**

*   如果你手里拿着 **1 核 1G** 的服务器，**请无脑安装 Debian 11 或 12**。
    *   理由：它能让你用 Ubuntu 的操作习惯，享受到极致的资源利用率。
*   如果你是去公司上班，公司要求用啥你就用啥（通常是 CentOS 或 Rocky）。
*   如果你是玩 Docker 微服务架构，可以尝试 Alpine。

**别再让操作系统吃掉你 40% 的性能了，换个 Debian，给你的业务留点活路吧。**

---
*觉得有用？点赞收藏，下次重装系统不迷路。*


# 服务器带宽测试完全指南：场景、方法与单位换算

测试服务器带宽，通常分两种场景：

1.  **想看综合表现：** 比如连接国内（电信/联通/移动）快不快，连接海外快不快。
2.  **想看瞬时峰值：** 就像家里测速一样，看最大能跑多少。

以下是几种最常用、最硬核的测试方法（按推荐程度排序）：

---

**方法一：使用“一键测速脚本” (最推荐，VPS 玩家必备)**

这是 Linux 服务器圈子最常用的方法。这些脚本会自动测试服务器连接全球（包括中国大陆三网）的上传和下载速度，并生成漂亮的报告。

**推荐脚本 1：Hyperspeed (测速速度快，节点多，但是注意，没有配置的情况下可能会有中文乱码)**

这是一个专注于网络测速的脚本，它会测试国内三网和国际主要节点的带宽。

```bash
bash <(curl -Lso- https://bench.im/hyperspeed)
```

**推荐脚本 2：Superbench (经典老牌)**

不仅测网速，还能顺便把你的 CPU 型号、磁盘 I/O 读写速度一起测了。

```bash
wget -qO- --no-check-certificate https://raw.githubusercontent.com/oooldking/script/master/superbench.sh | bash
```

**如何看结果？**

*   **Upload Speed (上行带宽):** 这是最重要的。决定了你的服务器给用户发数据的速度（比如你建站，用户打开网页的速度）。
*   **Download Speed (下行带宽):** 决定了你服务器下载文件的速度。

---

**方法二：使用 Speedtest 命令行版 (最准确的单点测试)**

如果你只关心“这一刻我的最大带宽是多少”，用 Ookla 官方的 Speedtest 工具最准。

**1. 安装 Speedtest：**

Debian/Ubuntu 默认源里的版本比较老，建议用下面的方式安装 Python 版，轻量方便。

先安装 pip（如果还没有的话）：

```bash
apt update
apt install python3-pip -y
```

安装 speedtest-cli：

```bash
pip3 install speedtest-cli
```

**2. 开始测速：**

*   **简单测速（自动找最近节点）：**
    ```bash
    speedtest-cli
    ```

*   **生成图片链接（方便发给朋友看）：**
    ```bash
    speedtest-cli --share
    ```

---

**方法三：实时监控 (看着流量跑)**

如果你正在下载东西，或者想看着服务器当前的实时带宽占用，可以用 `nload`。它像个仪表盘一样。

**1. 安装：**

```bash
apt install nload -y
```

**2. 运行：**

```bash
nload
```

*   **Incoming:** 进来的流量（下载）
*   **Outgoing:** 出去的流量（上传）
*   按键盘上的左右箭头键可以在不同网卡之间切换。

---

**⚠️ 新手必看的“带宽单位”坑**

**千万别搞混了 `Mbps` 和 `MB/s`！**

*   商家卖给你的带宽通常是 **Mbps** (Megabits per second, 小写的 b)。
*   你在浏览器/迅雷里看到的速度通常是 **MB/s** (Megabytes per second, 大写的 B)。

**换算公式：除以 8**

| 商家标称带宽 | 理论最高下载速度 (MB/s) |
| :--- | :--- |
| **1 Mbps** | 128 KB/s (慢到令人发指) |
| **5 Mbps** | 640 KB/s (勉强看标清视频) |
| **10 Mbps** | 1.25 MB/s |
| **30 Mbps** | 3.75 MB/s (轻量级应用够用) |
| **100 Mbps** | 12.5 MB/s |
| **1 Gbps** | 125 MB/s |

**实战判断：**

如果你买的是 30Mbps 的服务器，你用 `nload` 看到 Outgoing 跑到 **3.5MB/s** 左右，说明带宽已经跑满了。