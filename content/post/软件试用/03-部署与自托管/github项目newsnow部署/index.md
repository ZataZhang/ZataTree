---
title: github项目newsnow部署
description: ""
date: 2025-03-13T22:25:19+08:00
image: images/index/index.png
categories:
    - 软件试用
tags:
    - 部署与自托管
    - SoftUseExp
---


<!-- ![newsnow](images/index/index.png) -->

{{< bilibili BV1X8QhY5EB5 >}}


### 项目介绍

项目地址：

https://github.com/ourongxing/newsnow

newsnow是一个新闻聚合平台，用户可以关注自己感兴趣的新闻，并查看新闻内容。


### 使用docker部署 -- windows

1. 安装好docker desktop

![安装docker](images/index/index-1.png)

具体的部署方式就不介绍了


2. 下载项目文件

![nowsnow项目文件](images/index/index-2.png)


3. 在当前项目下执行docker compose up 命令


![docker compose](images/index/index-4.png)
![docker 容器](images/index/index-3.png)



### 使用docker部署 -- linux服务器

1. 安装好docker，可以使用1panel或者是宝塔面板

```bash
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh && sudo bash quick_start.sh
```

![alt text](images/index/index-5.png)


2. 使用docker编排进行部署

```bash
version: '3'

services:
  newsnow:
    image: ghcr.io/ourongxing/newsnow:latest
    container_name: newsnow
    restart: always
    ports:
      - '4444:4444'
    environment:
      - G_CLIENT_ID=
      - G_CLIENT_SECRET=
      - JWT_SECRET=
      - INIT_TABLE=true
      - ENABLE_CACHE=true
```

![alt text](images/index/index-6.png)

3. 打开你的ip地址:4444