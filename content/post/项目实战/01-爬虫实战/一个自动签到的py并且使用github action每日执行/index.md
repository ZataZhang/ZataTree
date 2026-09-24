---
title: 一个自动签到的py并且使用github action每日执行
date: 2025-03-03T14:40:00+08:00
# slug: 文件夹名/index.md ## 必填，文件夹名/index.md
image: image/index/index.png
categories:
    - 项目实战
tags:
    - 爬虫实战
    - git&github
    - 爬虫
---


![alt text](image/index/index.png)
效果就是每天8点去自动签到
![alt text](image/index/index.jpg)



## 使用Cookie进行自动登录（简单，但是很容易因为Cookie过期而需要重新获取Cookie更新）

### Cookie的获取
参考：
https://www.diuber.com/cookie/


首先需要获取Cookie，这个Cookie是登录之后的Cookie，登录之后的Cookie是在浏览器的开发者工具中获取的，具体方法如下：
1. 打开浏览器，登录mx的账号
2. 打开浏览器的开发者工具，在Network中找到请求的接口，点击请求的接口，在Headers中找到Cookie，复制Cookie




### 签到的代码


```py
# mx_checkin.py
import requests
import schedule
import time
from datetime import datetime
Cookie = os.environ.get("MX_COOKIE")  # 把Cookie放置在action的环境变量中,例如这里是MX_COOKIE
# 签到函数
def checkin():
    # 替换为实际的签到接口 URL
    url = XXXXX

    # 准备请求头（可能需要 Cookie 或 Token 来验证身份）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        # 如果需要登录凭证，可以在这里添加 Cookie 或 Authorization
        "Cookie": Cookie,
        # "Authorization": "Bearer your_token_here"
    }

    # 准备请求数据（根据实际接口要求调整）
    data = {
        "userId": "your-user-id",  # 替换为你的用户 ID
        "timestamp": int(time.time())  # 可选：发送当前时间戳
    }

    try:
        # 发送签到请求
        response = requests.post(url, headers=headers)
        response_json = response.json()

        # 检查签到是否成功
        if response.status_code == 200 :
            print(f"{datetime.now()} 签到成功：{response_json.get('msg')}")
        else:
            print(f"{datetime.now()} 签到失败：{response_json.get('msg')}")
    except Exception as e:
        print(f"{datetime.now()} 签到请求失败：{str(e)}")


# 脚本主循环
if __name__ == "__main__":
    print("自动签到脚本已启动...")
    # 首次运行时立即签到（可选）
    checkin()
```

代码写好之后可以先在本地测试，保证测试ok


### github action的工作流配置

关于github action的内容，可以查看我的文章  [`github action使用`](../2-github-action-使用/)


```
# mx_checkin.yml
name: mx_checkin

on:
  schedule:
    # 此处是UTC时间，对应北京时间早八点
    - cron : '00 00 * * *'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.12
      uses: actions/setup-python@v3
      with:
        python-version: "3.12"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Run checkin script
      run: |
        python mx_checkin.py
      env:
        MX_COOKIE: ${{ secrets.MX_COOKIE }}
```

### requirements.txt

把需要的库写在这个文件中
```text
requests
schedule
datetime
```
### 设置仓库密钥
![alt text](image/index/index-1.jpg)

把前面Cookie 填进去 **粘贴过来的时候可以把引号去掉，我记得是不用加引号的，如果发现自己电脑上面测试可以，Action不行的话可以再试试加引号**


---

上面的方法很受限于网站对于cookie的验证，如果网站对cookie验证过于严格，可以尝试下面的方法。

## 使用账号密码进行自动登录（复杂，但是可以避免Cookie过期的问题）

这里我只是给了一个简单的配置，很多网站登录的时候可能会多重验证，那就麻烦了....

### 找到登录的接口

当然每个网站不一样，不能一概而论

![alt text](images/index/index.png)


### 代码

```py
# checkin
import requests
import schedule
import time
from datetime import datetime
import os
import json

from dotenv import load_dotenv
load_dotenv()


def refresh_cookie():
    """刷新 Cookie 的逻辑（需要根据实际网站实现）"""
    global Cookie
    try:
        # 替换为实际的登录 URL 和登录数据
        login_url = "https://mxwljsq.top/auth/login"
        login_data = {
            "email": os.environ.get("MX_EMAIL"),  # 从环境变量获取邮箱
            "passwd": os.environ.get("MX_PASSWORD"),  # 从环境变量获取密码
        }

        print(login_data)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # exit()
        # 发送登录请求
        response = requests.post(login_url, data=login_data, headers=headers)
        print(response.text)
        if response.status_code == 200:
            # 假设登录成功后 Cookie 在响应头中返回
            new_cookie = response.cookies.get_dict()
            Cookie = "; ".join([f"{k}={v}" for k, v in new_cookie.items()])
            print(f"{datetime.now()} Cookie 刷新成功")
            return True
        else:
            print(f"{datetime.now()} Cookie 刷新失败：{response.text}")
            return False
    except Exception as e:
        print(f"{datetime.now()} Cookie 刷新异常：{str(e)}")
        return False

def checkin():
    refresh_cookie()
    global Cookie
    if Cookie is None:
        print("Cookie 为空，请先刷新 Cookie")
        return False
    url = "https://mxwljsq.top/user/checkin"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Cookie": Cookie,
    }

    try:
        response = requests.post(url, headers=headers)
        response_json = response.json()

        if response.status_code == 200:
            print(f"{datetime.now()} 签到成功：{response_json.get('msg')}")
            return True
        else:
            print(f"{datetime.now()} 签到失败：{response_json.get('msg')}")
            # 如果是登录失效，尝试刷新 Cookie
            return False
    except Exception as e:
        print(f"{datetime.now()} 签到请求失败：{str(e)}")
        return False

if __name__ == "__main__":
    print("自动签到脚本已启动...")
    # 加载本地 Cookie，如果没有则使用环境变量中的
    # 首次运行立即签到
    print(f"{datetime.now()} 开始执行签到任务...")
    checkin()
```

```yaml
# mx_checkin.yml
name: mx_checkin

on:
  schedule:
    # 此处是UTC时间，对应北京时间早八点
    - cron : '00 00 * * *'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.12
      uses: actions/setup-python@v3
      with:
        python-version: "3.12"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Run checkin script
      run: |
        python mx_checkin.py
      env:
        MX_EMAIL: ${{ secrets.MX_EMAIL }}
        MX_PASSWORD: ${{ secrets.MX_PASSWORD }}

```

### 设置仓库密钥

![设置仓库密钥](images/index/index-1.png)

这里是肯定不需要加引号的，因为邮箱和密码都是字符串，加引号的话会被认为是字符串。（我试过了）












