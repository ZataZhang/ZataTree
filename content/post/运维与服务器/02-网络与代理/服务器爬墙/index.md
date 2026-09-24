---
title: 服务器爬墙
description: ""
date: 2026-03-20T00:31:26+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - Server Operations and Maintenance-服务器运维
---



# 安装和配置

[mihomo安装包](mihomo-linux-amd64-v1.19.21.deb)

[mmdb文件](country.mmdb)

--- 

[mihomo - github地址](https://github.com/MetaCubeX/mihomo/releases)

[maxmind-geoip - github地址](https://github.com/Dreamacro/maxmind-geoip/releases)

1. 首先下载deb包和mmdb（或者压缩包）
![deb安装包](images/index/image.png)
![mmdb文件](images/index/image-2.png)


2. 传输到远程服务器
```bash 
scp <deb包名>.deb root@remote_server:/root/
scp <mmdb文件名>.mmdb root@remote_server:/root/
```

3. 安装deb包
```bash 
dpkg -i /root/<deb包名>.deb
```

4.下载 Country.mmdb
```bash
# 进入配置目录
cd /etc/mihomo
# 下载 Country.mmdb
curl -L -o Country.mmdb https://ghp.ci/https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/country.mmdb

#或者

# 复制 mmdb 文件
cp /root/<mmdb文件名>.mmdb Country.mmdb
# 复制 mmdb 文件
cp Country.mmdb /etc/mihomo/
```

5. 修改配置文件
```bash
# 编辑配置文件
vim /etc/mihomo/config.conf


# 粘贴你的clash配置文件
【-------】


# 把这几行添加到配置文件的开头
geodata-loader: memconservative
geodata-mode: false # 某些版本可用
external-controller: 0.0.0.0:9090  # 外部控制端口，建议 0.0.0.0 方便远程访问
secret: "your_secret_password"            # 控制面板密码 (强烈建议修改)
external-ui: ui                    # 控制面板文件目录 (可选)
```

![alt text](images/index/image-1.png)


6. 重启服务
```bash
# 重启服务
systemctl restart mihomo

# 立即查看日志
journalctl -u mihomo -f
```

7. 访问控制面板
```bash
# 访问控制面板
http://remote_server:9090/ui?secret=your_secret_password
```

8. 配置环境变量
```bash
# 写入环境变量
echo "export http_proxy=http://127.0.0.1:7890" >> ~/.bashrc
echo "export https_proxy=http://127.0.0.1:7890" >> ~/.bashrc
# 使其立即生效
source ~/.bashrc
```
9. 设置开机自启
```bash
# 设置开机自启
systemctl enable mihomo
```