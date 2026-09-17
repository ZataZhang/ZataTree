---
title: 腾讯云修改为root登录
description: 腾讯云修改为root登录
date: 2025-02-24
slug: 腾讯云修改root登录/index.md ## 必填，文件夹名/index.md
image: image/腾讯云修改root登录/腾讯云修改root登录.jpg
categories:
    # - DeepLearning
    # - Chart
    # - Python
    # - LLM
    # - Library
    # - PaperReading
    # - Other
    - Project_Application

---

```bash
sudo passwd root
sudo vim /etc/ssh/sshd_config
# 修改 PermitRootLogin yes
sudo systemctl restart ssh

如果需要通过密钥登录root,最好使用ssh-copy-id, 我试过自己粘贴,很麻烦
```



![alt text](image/腾讯云修改root登录/腾讯云修改root登录.jpg)