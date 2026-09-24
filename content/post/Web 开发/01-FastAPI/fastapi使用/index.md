---
title: FASTAPI使用相关问题
description: FASTAPI
date: 2025-02-28
image: images/index/index.png
slug: fastapi使用 ## 必填，文件夹名
# image: helena-hertz-wWZzXlDpMog-unsplash.jpg
categories:
    - Web 开发
tags:
    - FastAPI
    - Python_Library
---
#  ☆ FASTAPI
## 运行环境和安装
1. 安装python环境
2. 安装fastapi
3. 安装uvicron
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/dd651babd8de40d9b1dda5958b8e1605.png)

# 开始使用fastapi
## 01.第一个简单程序

```bash
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}
```
运行：运行有两种方式
方法1. 在文件路径下运行命令（这种方式在windows中容易出问题，如果显示无法找到命令，可以使用第二种方法）

```bash
uvicron main:app --reload
# 其中，main指的是文件名main.py, app指的是文件中定义的对象app，--reload指的是代码更改后重新加载的开发模式
```

方法2. 代码中导入uvicron包，

```python
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}
if __name__ == "__main__":
    uvicorn.run(app = "main:app", host="0.0.0.0", port=8000，reload = True)

```

---
---
# fastapi部署


## 使用uvicorn部署（一般在开发场景下）

`step1: 安装uvicorn`

```bash
pip install uvicorn
```

`step2：运行uvicorn	`

有两种方式，一直是直接用代码：

```python
if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
```
另一种是在控制台

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`step3 : 设置后台运行`

但是本身uvicorn是不带后台运行功能的，因此你需要结合其他工具实现后台运行功能，我常用的是Tmux，这里不做说明
参考：[阮一峰 Tmux使用教程](https://www.ruanyifeng.com/blog/2019/10/tmux.html)

【推荐使用下面的gunicorn部署】


--- 
---


## 使用gunicorn部署
step1：


使用gunicorn最好在你服务的main.py同级目录下面新建一个gunicorn.py文件
| 参考： https://blog.csdn.net/asd54090/article/details/137783835
```py
# gunicorn.py
import os

# 设置守护进程
daemon=True
# 监听内网端口8000
bind='0.0.0.0:8000'
# 设置进程文件目录
pidfile='./gunicorn.pid'
chdir='./' # 工作目录
# 工作模式
worker_class='uvicorn.workers.UvicornWorker'
# 并行工作进程数 核心数*2+1个
workers=3  #multiprocessing.cpu_count()+1
# 指定每个工作者的线程数
threads=2
# 设置最大并发量
worker_connections = 2000
loglevel='debug' # 错误日志的日志级别
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
# 设置访问日志和错误信息日志路径
log_dir = "./log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
accesslog = "./log/gunicorn_access.log"
errorlog = "./log/gunicorn_error.log"

```

step2： 

然后要在服务器下面安装相应的库`(非常注意的一点是，step3用gunicorn启动的时候，如果有错误它控制台是不报错的，所以强烈建议先用uvicorn能启动之后再用gunicorn)`

```cpp
pip install fastapi
pip install gunicorn
```

step3: 

```bash
gunicorn main:app -c gunicorn.py
```
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/a75b4e1ac57d426d818b9ce4e3643bc9.jpeg)
可以看见，这里运行之后啥也不报

当然也可以不用配置文件，直接执行下面命令启动应用

```cpp
gunicorn main:app -b 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker --daemon
```


step4：
如果想要关闭项目
需要通过Kill的方式，`可以看上面的参考链接`
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/44483c4bf5b443f18a2b16f6c7dd552e.jpeg)




## 配置Nginx代理访问(可选）

详情可见 [nginx使用]({{< relref "post/运维与服务器/03-网关与站点/nginx使用/index.md" >}})
修改nginx的设置：

```cpp
server {
            listen 80; # ngixn的主页端口
           # listen 443 ssl;
            server_name XXX.com;  # 填你自己的域名或者IP
            access_log  /var/log/nginx/access.log;
            location / {
                proxy_pass http://127.0.0.1:8000;  # 你的服务端口
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For
                $proxy_add_x_forwarded_for;
        }
    }
```

然后运行nginx -s reload  或者 service nginx restart





