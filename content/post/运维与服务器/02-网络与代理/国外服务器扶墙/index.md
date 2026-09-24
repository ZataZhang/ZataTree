---
title: 国外服务器扶墙
description: ""
date: 2025-04-24T00:19:47+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - Linux
---

`两个实际上都没成功。。。还是很难的，所以以后国外服务器还是别买。。。`
参考 https://ry.huaji.store/2020/08/Linux-magic-network/
# V2ray
安装客户端
参考 ： https://v2raya.org/docs/prologue/installation/debian/

```bash
# Ubuntu、Debian 
wget -qO - https://apt.v2raya.org/key/public-key.asc | sudo tee /etc/apt/keyrings/v2raya.asc
echo "deb [signed-by=/etc/apt/keyrings/v2raya.asc] https://apt.v2raya.org/ v2raya main" | sudo tee /etc/apt/sources.list.d/v2raya.list
sudo apt update
sudo apt install v2raya v2ray ## 也可以使用 xray 包
sudo systemctl start v2raya.service # 启动
```
然后访问 ip:2017
参考 https://v2raya.org/docs/prologue/quick-start/
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/cd10adc28cc742ce9295da14a72a3316.png)
在第一次进入页面时，你需要创建一个管理员账号，请妥善保管你的用户名密码，如果遗忘，使用sudo v2raya --reset-password命令重置。



# Shadowsocks

安装conda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
cd ~
source .bashrc
```

安装shadowsocks组件

```bash
sudo pip3 install https://github.com/shadowsocks/shadowsocks/archive/master.zip -U
或
sudo pip3 install shadowsocks
```
此外，如果你需要使用 Shadowsocks 新的加密方式的话，比如 Chacha20-Ietf-Poly1305，你还需要装下面这个东西

```bash
# ubuntu
sudo apt install libsodium-dev

# centos
sudo yum -y install epel-release
sudo yum -y install libsodium
```
配置
新建配置文件夹和配置文件

```bash
sudo mkdir /etc/shadowsocks
sudo vi /etc/shadowsocks/shadowsocks.json
```

配置如下，具体内容自行修改（没有梯子请自行联系工信部申请）

```bash
{
    "server": "your_server_url",
    "server_port": 23333,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "your_server_password",
    "timeout": 60,
    "method": "chacha20-ietf-poly1305",
    "workers": 1,
    "fast_open": false
}
```

其中

```bash
server：科学上网代理提供商的 Shadowsocks 服务器地址
server_port：科学上网代理提供商的 Shadowsocks 服务器端口
local_address：本地 Sock5 代理地址
local_port：本地 Sock5 代理端口
password：科学上网代理提供商的 Shadowsocks 连接密码
timeout：超时等待时间（秒）
method：加密方式
workers：工作线程数
fast_open：TCP Fast Open，按需开启
```

配置完成，之后就可以通过 local_address 和 local_port 走 Sock5 代理了

启动脚本
创建启动脚本 /etc/systemd/system/shadowsocks.service

这里请确认你的 sslocal 的所在位置，自行修改脚本文件中的 /usr/local/bin/sslocal，位置不对启动服务时会报 203 错误

```bash
[Unit]
Description=Shadowsocks

[Service]
TimeoutStartSec=0
ExecStart=/usr/local/bin/sslocal -c /etc/shadowsocks/shadowsocks.json

[Install]
WantedBy=multi-user.target
```

GO! GO! GO!
启动服务或者配置开机自启动

# 开机自启动

```bash
sudo systemctl enable shadowsocks.service
```

# 启动服务

```bash
sudo systemctl start shadowsocks.service
```

# 查看状态

```bash
sudo systemctl status shadowsocks.service
```

# 停止服务

```bash
sudo systemctl stop shadowsocks.service
```

测试一下，看看你的 ip 地址是否符合预期

```bash
curl --socks5 127.0.0.1:1080 https://httpbin.org/ip
```

到这里 Shadowsocks 部分就结束了，可以直接跳转后面的 Sock5 代理部分接着搞

