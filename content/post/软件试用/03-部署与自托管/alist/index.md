---
title: alist
description: ""
date: 2026-03-07T17:50:08+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftTrial
---




# AList V3 详细使用教程：安装、配置与 WebDAV 挂载

**AList** 是一款支持多种存储（阿里云盘、百度网盘、OneDrive、Google Drive 等）的文件列表程序。它可以把你的各种网盘聚合在一起，不仅可以直接在网页端预览、下载文件，还能通过 **WebDAV** 协议挂载到本地电脑或第三方播放器（如 Infuse、PotPlayer）上直接看原画视频。

以下是一份保姆级的 AList V3 版本详细使用教程，分为**安装、初始化、添加网盘**和 **WebDAV 挂载**四个主要部分。

---

**一、安装 AList**

AList 支持全平台安装。这里提供最常用的两种安装方式：**Docker（推荐给 NAS/Linux 用户）** 和 **Windows（适合小白和普通电脑）**。

**1. 使用 Docker 安装（最推荐，稳定且干净）**

如果你有云服务器、NAS 或安装了 Docker 的电脑，直接在终端运行以下命令：

```bash
docker run -d --restart=always -v /etc/alist:/opt/alist/data -p 5244:5244 --name="alist" xhofe/alist:latest
```

* **5244** 是默认端口，如果你想换成别的，可以把前一个 `5244` 改掉（例如 `-p 8080:5244`）。

**2. 在 Windows 上安装**

1. 前往 AList 的 [GitHub Releases 页面](https://github.com/alist-org/alist/releases)。
2. 下载名为 `alist-windows-amd64.zip` 的文件。
3. 解压到一个文件夹（例如 `D:\AList\`）。
4. 在文件夹路径栏输入 `cmd` 并回车，打开命令提示符。
5. 输入运行命令：`alist.exe server`，看到 `start server @ 0.0.0.0:5244` 就代表运行成功了。（注意：这个 CMD 窗口不能关，关了 AList 就停了）。

---

**二、初始化与登录**

AList 第一次运行会生成默认密码（或需要你自己设置）。

**1. 获取/设置管理员密码**

* **Docker 用户**：在终端输入以下命令随机生成一个密码，或者手动设置。
* 手动设置密码（推荐，把 `YOUR_PASSWORD` 换成你的密码）：
`docker exec -it alist ./alist admin set YOUR_PASSWORD`

* **Windows 用户**：在刚刚那个没关的 CMD 窗口按 `Ctrl+C` 停止运行，然后输入：
* `alist.exe admin set YOUR_PASSWORD`（设置好后，再重新输入 `alist.exe server` 启动服务）。

**2. 登录后台**

1. 在浏览器输入：`http://你的 IP 地址:5244`（如果你是在本机安装的，就是 `http://127.0.0.1:5244`）。
2. 点击底部的 **“登录”**（或者管理）。
3. 账号输入 `admin`，密码输入你刚刚设置的密码。

---

**三、添加网盘（以阿里云盘为例）**

进入后台管理后，你就可以把各大网盘“装”进 AList 了。

1. 在左侧菜单点击 **存储 (Storage)** -> **添加 (Add)**。
2. **驱动 (Driver)** 选择你要添加的网盘（例如：`阿里云盘 Open`）。
3. **挂载路径 (Mount Path)**：输入你想要在首页显示的文件夹名字，比如 `/阿里云盘`。
4. **填写网盘授权信息 (Token)**：
* 由于大部分网盘需要授权，你需要获取 Token 或 Refresh Token。
* AList 官方提供了一个非常方便的获取工具：访问 `https://alist.nn.ci/zh/guide/drivers/aliyundrive_open.html`（官方文档），里面有获取 Token 的二维码或按钮。
* 用阿里云盘 App 扫码后，网页会显示一串 **Refresh Token**。
* 把这串 Token 复制，回到 AList 后台，粘贴到 **刷新令牌 (Refresh Token)** 这一栏。

5. 其他选项保持默认即可，点击底部 **保存 (Save)**。
6. 回到“存储”列表，如果状态显示为 `work`，说明挂载成功！点击左侧的“主页”，你就能看到你的网盘文件了。

---

**四、进阶玩法：使用 WebDAV 挂载到播放器/电脑**

这是 AList 最强大的功能。你可以把云盘当成本地硬盘用，直接看高清电影，不占用本地空间。

**WebDAV 连接信息：**

* **服务器地址**：`http://你的 IP:5244/dav` （注意后面一定要加 `/dav`）
* **账号**：你的 AList 登录账号（例如 `admin`）
* **密码**：你的 AList 登录密码

**应用场景：**

* **手机/平板看剧 (Infuse / nPlayer / Fileball)**：在播放器里添加网络服务器，选择 WebDAV 协议，填入上面的连接信息，你网盘里的电影立刻变成精美的海报墙，并且可以直接原画播放。
* **电脑看剧 (PotPlayer / VLC)**：在播放器里打开“打开链接”或“添加 FTP/WebDAV"，填入信息即可无缝播放。
* **挂载为电脑本地磁盘**：Windows 用户可以使用 `RaiDrive` 软件，Mac 用户可以使用系统自带的“连接服务器”或 `CloudMounter`，将 AList 映射为一个电脑的本地盘符（比如 Z: 盘），像操作本地文件一样操作网盘。

---

**你想先从哪个网盘开始挂载呢？如果需要获取特定网盘（如百度网盘、OneDrive、夸克网盘）的具体配置方法，我可以为你提供详细步骤。**

