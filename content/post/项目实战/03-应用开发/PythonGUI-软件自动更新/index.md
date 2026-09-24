---
title: 软件自动更新
description: 软件自动更新是指通过内置机制检测新版本并下载安装，以保持软件最新和安全，这里以python语言为例
date: 2025-02-28
slug: 软件自动更新 ## 必填，文件夹名
image: image/index/index.png
categories:
    # - DeepLearning
    # - Chart
    # - LLM
    # - Library
    # - PaperReading
    # - Other
    - Project_Application
tags:
    - PythonGUI

---


# 软件自动更新

## TODO 
- [ ] 把服务器部署功能写成docker file的形式 【2025-02-26】 
- [x] 把客户端的封装成一个exe 【2025-02-26】 
- [ ] 把上传更新文件写成用一个页面上传 【2025-02-26】 
- [ ] 当前的更新和上传方式都是把全部的文件都上传和下载，文件一大太慢了，需要优化一下，只上传更新的文件 【2025-02-26】 


## 软件自动更新的重要性
1. 当软件开发过程中出现一些小bug，可以通过热补丁的方式快速修复（热补丁比较难，暂时没学）
2. 如果软件版本升级，不用总是去重新下载安装包。
3. 从用户体验角度来说，软件能自动更新也是更方便使用的。

## 软件自动更新方面我找到的一些参考

https://blog.csdn.net/danxuezx/article/details/83784318
https://www.cnblogs.com/lindexi/p/18426258 【五颗星，很值得看】
https://www.chromium.org/developers/design-documents/software-updates-courgette/ 【谷歌的压缩编译压缩方法】
https://github.com/wayne-1024/auto-upgrade 【一个自动更新的代码仓库，就是比较旧了】
https://github.com/vslavik/winsparkle?tab=readme-ov-file 【winsparkle 一个用于自动更新的框架】
https://zhuanlan.zhihu.com/p/425845057 【动态更新的知识，大佬】
https://fugary.com/?p=523 【比较详细的教程】
https://www.cnblogs.com/CSSZBB/p/12882068.html 【这个人自己写了一个发布更新程序，部署在他自己服务器，可供别人使用】

## 我自己写了一个自动更新的代码，基于python 的

主要分为（ 用于提供更新服务的后端 ， 有更新就下载文件进行更新的前端  ）

1. 首先需要在服务器端部署一个服务，这个服务主要用于两个功能，第一个功能就是你把新的版本上传给他，第二个功能就是，你的客户端每次启动的时候来访问一下这个服务，看看有没有更新可以用，如果有更新那么就下载更新，提供下载的功能
2. 前端也就是客户端，每次启动的时候都去检查一下，如果有更新了就下载更新，然后根据配置文件去本地找文件进行更新

### 服务器端

首先需要在服务器上面安装python环境，然后运行下面的代码（建议新建一个文件夹）


flask 需要建议在后台运行，可以使用tmux

**安装tmux**

```bash
apt-get update
apt-get install tmux

tmux new -s [会话名]  # 新建会话

tmux a -t [会话名]  # 进入会话

ctrl + b + d  # 退出会话

tmux kill-session -t 【会话名或编号】  # 杀死会话

```

**安装conda**

```bash

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
cd ~
source .bashrc

```

**创建虚拟环境**

```bash
conda create -n myenv python=3.10
conda activate myenv
```

**安装flask**

```bash
pip install flask
```







flask程序
```python
# app.py
from flask import Flask, jsonify, send_file, request
import os
import json
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1600 * 1024 * 1024  # 配置最大可上传的文件大小为1600MB


# 配置文件存储路径
UPLOAD_FOLDER = 'updates'
CONFIG_FILE = 'update_config.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def ensure_upload_folder():
    """确保上传文件夹存在"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def calculate_file_hash(file_path):
    """计算文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def update_config(version, notes, filename):
    """更新配置文件"""
    config = {
        "version": version,
        "publish_notes": notes,
        "download_url": f"/download/{filename}",
        "file_hash": calculate_file_hash(os.path.join(app.config['UPLOAD_FOLDER'], filename)),
        "keep_old_files": ["data.txt"]  # 可以根据需要修改
    }
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

@app.route('/')
def hello():
    return "Hello, Flask with Nginx!"

@app.route('/update_config')
def get_update_config():
    """获取更新配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": "Configuration file not found"}), 404

@app.route('/download/<filename>')
def download_file(filename):
    """下载更新文件"""
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)),
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传新版本"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    version = request.form.get('version')
    notes = request.form.get('notes')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        ensure_upload_folder()
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        update_config(version, notes, filename)
        return jsonify({"message": "Upload successful"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# requirements.txt
"""
Flask==3.0.0
gunicorn==21.2.0
Werkzeug==3.0.0
"""

```


在tmux 里面，使用 python app.py 运行起来，然后分离会话

如果这一步没有问题的话，使用浏览器访问【域名:5000】，如果能访问到，说明后端程序已经配置成功了

![alt text](image/软件自动更新/软件自动更新-1.jpg)





**nginx 配置**

上面光配置了flask的后端程序是不行，这样直接访问域名/ip是找不到的，还需要配置nginx做一个代理，让nginx去访问flask的后端程序

首先你需要安装nginx,可以按照下面的步骤进行安装,`注意，安装就可以了，不要启动nginx！！！`
```python
# Ubuntu官方列表的Nginx版本不一定是最新的。所以请添加Nginx安装列表：
# 这一步不是必须的，但建议执行，不然安装的Nginx版本会挺旧的。
$ sudo apt install software-properties-common
$ sudo add-apt-repository ppa:nginx/stable

# 更新列表
$ sudo apt-get update

# 安装 Nginx
$ sudo apt-get install nginx

$ nginx -v       # 查看Nginx版本号
$ dpkg -L nginx  # 查看Nginx安装位置，输出/usr/share/doc/nginx。其他文件在/etc/nginx
$ dpkg --list    # 查看已安装的包

$ sudo apt-get remove nginx nginx-common  # 删除Nginx（保留配置文件)
$ sudo apt-get purge nginx nginx-common   # 删除Nginx（且不保留配置文件)
$ sudo apt-get autoremove                 # 删除依赖（dependencies）

$ service nginx status   # 查看Nginx状态，默认在运行ing
# 此时访问服务器的IP地址即可看到"Welcome to nginx!"的页面

# 每次更新 Nginx 配置后，都建议重启一下 Nginx
$ service nginx start    # Nginx启动命令
$ service nginx stop     # Nginx停止命令
$ service nginx restart  # Nginx重启命令
```
**nginx配置**

进入到配置文件中

```bash
vim /etc/nginx/sites-available/update-server
```
修改以下代码
```python
server {
    listen 80; # 也就是其他地方访问需要的端口，nginx默认是80，也就是不需要额外加端口可以访问,记得把防火墙打开，还要就是没有被其他程序占用，
    server_name zata.cc;  # 自己的域名或者ip地址

    location / {
        proxy_pass http://127.0.0.1:5000; # 需要代理的地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```





然后创建符号链接让配置生效
```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/update-server /etc/nginx/sites-enabled/
```

查看符号链接是否创建成功
```bash
ls -l /etc/nginx/sites-enabled/
```

查看配置是否有问题
```bash
sudo nginx -t
```

启动nginx  
```bash
cd /etc/nginx
servce nginx start
```

再检查一下是否有问题
```bash
sudo nginx -t
```

然后直接访问域名或者ip

![alt text](image/软件自动更新/软件自动更新-2.jpg)

可以看到不加端口也可以访问了
到这一步说明flask和nginx都配成功了，不过如果遇到：
```bash
<html>
<head><title>413 Request Entity Too Large</title></head>
<body>
<center><h1>413 Request Entity Too Large</h1></center>
<hr><center>nginx/1.18.0 (Ubuntu)</center>
</body>
</html>
```
这个是由于nginx也有上传文件大小的要求，可以修改nginx的配置文件

---
---

上传前需要准备代码文件和用于更新的配置文件
首先是代码文件，这个需要打包成.zip文件，然后解压之后就相当于安装目录下面的所有文件

就比如这个文件夹，remote.zip里面的文件就是所有其他文件打包的

![alt text](image/软件自动更新/软件自动更新.jpg)



然后是配置文件，这个文件是用来记录当前版本的信息，以及更新的信息,这个本地和远程都需要放，本地版本的配置文件里面的版本只有小于远程版本才会更新的


测试时候上传服务器可以把版本调大一点

// conf.json

```json

{
    "keep_files": [
        "data.txt",
        "updater.py"
    ],
    "version": "1.0.0",
    "publish_notes": "初始版本"

}
```

keep_files 是需要保留的文件，这些文件或者是文件夹不会倍更新
version 是当前版本的信息

publish_notes 是更新的信息

然后把这两个文件都上传到服务器上，然后就可以使用了

**上传文件**

这里就使用windows的命令行进行上传，当然也可以使用其他方式

```bash
curl -X POST -F "zip_file=@remote.zip" -F "config=@conf.json" [your IP or domain]/upload

``` 
这里上传之后就看客户端了


---


### 客户端

首先把这个程序放在客户端的安装目录下面 （注意修改你的ip或者域名）

python文件打包成exe （单文件，无控制台）
```bash
pyinstaller -F -w updater.py  
```

**客户端的程序**
#### 客户端更新程序
```python
# # updater.py
# # updater.py
import json
import hashlib
import os
import shutil
import requests
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', default="XXX.XXX.XXX.XXX", help="服务器IP地址或域名")
args = parser.parse_args()
YOUR_HOST = args.host

class AutoUpdater:
    def __init__(self, config_path=f"http://{YOUR_HOST}/update_config"):
        self.config_path = config_path
        self.config = None
        with open('update.json', 'r', encoding='utf-8') as f:
            self.current_version = json.load(f)['version']
        
    def load_config(self):
        """加载更新配置文件"""
        try:
            # 远程配置文件
            response = requests.get(self.config_path)
            self.config = response.json()
            return True
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return False
            
    def check_update(self):
        """检查是否需要更新"""
        if not self.config:
            return False
            
        return self.config['version'] != self.current_version
        
    def calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def download_update(self, temp_dir="temp_update"):
        """下载更新文件"""
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        try:
            # 下载更新文件
            update_file = f"{temp_dir}/update.zip"
            download_route = self.config["download_url"]

            
            response = requests.get(f'http://{YOUR_HOST}{download_route}', stream=True)
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            # 验证文件哈希
            if self.calculate_file_hash(update_file) != self.config['file_hash']:
                print("文件验证失败！")
                return False
                
            return update_file
        except Exception as e:
            print(f"下载更新失败: {str(e)}")
            return False
            
    def backup_files(self, backup_dir="backup"):
        """备份当前文件"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 备份当前目录下的所有文件
            for item in os.listdir('.'):
                if item not in [backup_dir, 'temp_update', 'updater.exe','launcher.exe']:
                    src = os.path.join('.', item)
                    dst = os.path.join(backup_dir, item)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst)
            return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False
            
    def apply_update(self, update_file, temp_dir="temp_update"):
        """应用更新"""
        try:
            # 解压更新文件
            shutil.unpack_archive(update_file, temp_dir)
            
            # 保留指定的旧文件和文件夹
            keep_files = self.config.get('keep_files', [])
            for file in keep_files:
                if os.path.exists(file):
                    # 如果文件在子文件夹中,需要创建对应的临时文件夹
                    temp_path = os.path.join(temp_dir, f"{file}")
                    temp_dir_path = os.path.dirname(temp_path)
                    if temp_dir_path and not os.path.exists(temp_dir_path):
                        os.makedirs(temp_dir_path)
                    print(f"备份: {file} -> {temp_path}")
                    if os.path.isfile(file):
                        shutil.copy2(file, temp_path)
                    elif os.path.isdir(file):
                        # 如果是文件夹则整个复制
                        shutil.copytree(file, temp_path)
            
            need_restart = False
            # 修改删除文件的部分，添加重试和错误处理
            for item in os.listdir('.'):
                if item not in ['backup', 'temp_update', 'updater.exe','launcher.exe']:
                    path = os.path.join('.', item)
                    
                    try:
                        if os.path.isfile(path):
                            try:
                                os.remove(path)
                            except PermissionError:
                                print(f"警告: 文件 {path} 正在使用中，将在重启后更新")
                                need_restart = True
                                continue
                        elif os.path.isdir(path):
                            try:
                                shutil.rmtree(path)
                            except PermissionError:
                                print(f"警告: 目录 {path} 中的某些文件正在使用中，将在重启后更新")
                                need_restart = True
                                continue
                    except Exception as e:
                        print(f"删除 {path} 时出错: {str(e)}")
                        continue
            # 如果需要重启，创建标记文件
            if need_restart:
                with open("need_restart", "w") as f:
                    f.write("1")
                print("部分文件需要在重启后完成更新")
                return True  # 仍然返回True，因为这是预期的行为

            # 复制新文件时添加错误处理
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join('.', item)
                try:
                    if os.path.isfile(src):
                        try:
                            shutil.copy2(src, dst)
                        except PermissionError:
                            print(f"警告: 无法复制文件 {dst}，可能需要重启后完成更新")
                    elif os.path.isdir(src):
                        try:
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        except PermissionError:
                            print(f"警告: 无法复制目录 {dst}，可能需要重启后完成更新")
                except Exception as e:
                    print(f"复制 {src} 到 {dst} 时出错: {str(e)}")
                    continue
            
            # 恢复需要保留的旧文件和文件夹
            for file in keep_files:
                temp_path = os.path.join(temp_dir, file)
                if os.path.exists(temp_path):
                    # 如果是带路径的文件,先创建目录
                    file_dir = os.path.dirname(file)
                    if file_dir and not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                    if os.path.isfile(temp_path):
                        shutil.copy2(temp_path, file)
                    elif os.path.isdir(temp_path):
                        # 如果是文件夹则整个恢复
                        if os.path.exists(file):
                            shutil.rmtree(file)
                        shutil.copytree(temp_path, file)
            
            return True
        except Exception as e:
            print(f"应用更新失败: {str(e)}, 错误位置: {e.__traceback__.tb_lineno}行")
            return False
    def cleanup(self, temp_dir="temp_update", backup_dir="backup"):
        """清理临时文件和备份"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            if os.path.exists("update.zip"):
                os.remove("update.zip")
        except Exception as e:
            print(f"清理文件失败: {str(e)}")

    def update(self):
        """执行更新流程"""
        if not self.load_config():
            return False
            
        if not self.check_update():
            print("当前已是最新版本")
            return True
            
        print(f"发现新版本: {self.config['version']}")
        print("更新说明:")
        print(self.config['publish_notes'])
        
        # 下载更新
        update_file = self.download_update()
        if not update_file:
            return False
        print(f"下载更新文件: {update_file}")
            
        # 备份当前文件
        if not self.backup_files():
            return False
        print("备份完成")
            
        # 应用更新
        if not self.apply_update(update_file):
            print("更新失败，正在恢复备份...")
            if self.apply_update("backup"):
                print("恢复备份成功")
                self.cleanup()
            else:
                print("恢复备份失败，请手动恢复")
            return False
            
        # 清理临时文件和备份
        self.cleanup()
        print(f"更新完成！当前版本: {self.config['version']}")
        return True
    

if __name__ == "__main__":
    try:
        updater = AutoUpdater()
        update_result = updater.update()
        print("更新" + ("成功" if update_result else "失败"))
    except Exception as e:
        print(f"更新过程中发生错误: {str(e)}")
    finally:
        input("按任意键退出...")


```

此外，本地需要一个update.json文件，这个文件是用来记录当前版本的信息,这个和远程的内容是一样的，本地版本的配置文件里面的版本只有小于远程版本才会更新的

例如： 
![alt text](image/软件自动更新/软件自动更新-3.jpg)


测试：

![alt text](image/软件自动更新/软件自动更新-4.jpg)




可以把上面的代码打包exe，然后运行，实际上就可以进行更新了，不过我们平常的使用方法应该是检查更新，如果没有更新就打开正常的界面，于是可以使用下面的代码



**启动器代码**
```py
import os
import sys
import subprocess
import time
import shutil

def main():
    # 检查是否有更新程序在运行
    updater_path = "updater.exe"
    if os.path.exists(updater_path):
        # 运行更新程序
        subprocess.run([updater_path], check=True)
        
        # 如果更新成功且需要重启
        if os.path.exists("need_restart"):
            # 删除重启标记
            os.remove("need_restart")
            
            # 等待原程序完全退出
            time.sleep(2)
            
            # 完成未完成的更新操作
            if os.path.exists("temp_update"):
                for root, dirs, files in os.walk("temp_update"):
                    for file in files:
                        src = os.path.join(root, file)
                        dst = os.path.join(root.replace("temp_update", ""), file)
                        try:
                            if os.path.exists(dst):
                                os.remove(dst)
                            shutil.copy2(src, dst)
                        except Exception as e:
                            print(f"更新文件失败: {e}")
                
                # 清理临时文件
                shutil.rmtree("temp_update")

    # 启动主程序
    main_program = "main.exe"  # 替换为你的主程序名
    if os.path.exists(main_program):
        subprocess.run([main_program])

if __name__ == "__main__":
    main()

```

#### 更完善的更新程序（更新和启动在一个文件里面）

```py
# updater.py
import json
import hashlib
import os
import shutil
import requests
from pathlib import Path
import argparse
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import threading

parser = argparse.ArgumentParser()
parser.add_argument('--host', default="XXX.XXX.XXX.XXX", help="服务器IP地址或域名")
args = parser.parse_args()
YOUR_HOST = args.host

TARGET_APP = "launcher.exe"

class AutoUpdater:
    def __init__(self, config_path=f"http://{YOUR_HOST}/update_config"):
        self.config_path = config_path
        self.config = None
        with open('update.json', 'r', encoding='utf-8') as f:
            self.current_version = json.load(f)['version']
        
    def load_config(self):
        try:
            response = requests.get(self.config_path)
            self.config = response.json()
            return True
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return False
            
    def check_update(self):
        if not self.config:
            return False
        return self.config['version'] != self.current_version
        
    def calculate_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def download_update(self, temp_dir="temp_update"):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        try:
            update_file = f"{temp_dir}/update.zip"
            download_route = self.config["download_url"]
            response = requests.get(f'http://{YOUR_HOST}{download_route}', stream=True)
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            if self.calculate_file_hash(update_file) != self.config['file_hash']:
                print("文件验证失败！")
                return False
            return update_file
        except Exception as e:
            print(f"下载更新失败: {str(e)}")
            return False
            
    def backup_files(self, backup_dir="backup"):
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            for item in os.listdir('.'):
                if item not in [backup_dir, 'temp_update', 'updater.exe','launcher.exe']:
                    src = os.path.join('.', item)
                    dst = os.path.join(backup_dir, item)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst)
            return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False
            
    def apply_update(self, update_file, temp_dir="temp_update"):
        try:
            shutil.unpack_archive(update_file, temp_dir)
            keep_files = self.config.get('keep_files', [])
            for file in keep_files:
                if os.path.exists(file):
                    temp_path = os.path.join(temp_dir, f"{file}")
                    temp_dir_path = os.path.dirname(temp_path)
                    if temp_dir_path and not os.path.exists(temp_dir_path):
                        os.makedirs(temp_dir_path)
                    print(f"备份: {file} -> {temp_path}")
                    if os.path.isfile(file):
                        shutil.copy2(file, temp_path)
                    elif os.path.isdir(file):
                        shutil.copytree(file, temp_path)
            
            need_restart = False
            for item in os.listdir('.'):
                if item not in ['backup', 'temp_update', 'updater.exe','launcher.exe']:
                    path = os.path.join('.', item)
                    try:
                        if os.path.isfile(path):
                            try:
                                os.remove(path)
                            except PermissionError:
                                print(f"警告: 文件 {path} 正在使用中，将在重启后更新")
                                need_restart = True
                                continue
                        elif os.path.isdir(path):
                            try:
                                shutil.rmtree(path)
                            except PermissionError:
                                print(f"警告: 目录 {path} 中的某些文件正在使用中，将在重启后更新")
                                need_restart = True
                                continue
                    except Exception as e:
                        print(f"删除 {path} 时出错: {str(e)}")
                        continue
            if need_restart:
                with open("need_restart", "w") as f:
                    f.write("1")
                print("部分文件需要在重启后完成更新")
                return True

            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join('.', item)
                try:
                    if os.path.isfile(src):
                        try:
                            shutil.copy2(src, dst)
                        except PermissionError:
                            print(f"警告: 无法复制文件 {dst}")
                    elif os.path.isdir(src):
                        try:
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        except PermissionError:
                            print(f"警告: 无法复制目录 {dst}")
                except Exception as e:
                    print(f"复制 {src} 到 {dst} 时出错: {str(e)}")
                    continue
            
            for file in keep_files:
                temp_path = os.path.join(temp_dir, file)
                if os.path.exists(temp_path):
                    file_dir = os.path.dirname(file)
                    if file_dir and not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                    if os.path.isfile(temp_path):
                        shutil.copy2(temp_path, file)
                    elif os.path.isdir(temp_path):
                        if os.path.exists(file):
                            shutil.rmtree(file)
                        shutil.copytree(temp_path, file)
            
            return True
        except Exception as e:
            print(f"应用更新失败: {str(e)}, 错误位置: {e.__traceback__.tb_lineno}行")
            return False
            
    def cleanup(self, temp_dir="temp_update", backup_dir="backup"):
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            if os.path.exists("update.zip"):
                os.remove("update.zip")
        except Exception as e:
            print(f"清理文件失败: {str(e)}")

    def update(self):
        if not self.load_config():
            return False
        if not self.check_update():
            print("当前已是最新版本")
            return True
            
        print(f"发现新版本: {self.config['version']}")
        print("更新说明:")
        print(self.config['publish_notes'])
        
        update_file = self.download_update()
        if not update_file:
            return False
        print(f"下载更新文件: {update_file}")
            
        if not self.backup_files():
            return False
        print("备份完成")
            
        if not self.apply_update(update_file):
            print("更新失败，正在恢复备份...")
            if self.apply_update("backup"):
                print("恢复备份成功")
                self.cleanup()
            else:
                print("恢复备份失败，请手动恢复")
            return False
            
        self.cleanup()
        print(f"更新完成！当前版本: {self.config['version']}")
        return True

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False
    
def start_target_app():
    try:
        if os.path.exists(TARGET_APP):
            subprocess.Popen(TARGET_APP)
        else:
            messagebox.showerror("错误", f"找不到 {TARGET_APP}，请确保文件存在！")
    except Exception as e:
        messagebox.showerror("错误", f"启动 {TARGET_APP} 失败: {str(e)}")

def show_updating_window(root, updater, callback):
    update_window = tk.Toplevel(root)
    update_window.title("更新")
    update_window.geometry("300x100")
    update_window.resizable(False, False)
    
    # Center the window
    update_window.update_idletasks()
    width = update_window.winfo_width()
    height = update_window.winfo_height()
    x = (update_window.winfo_screenwidth() // 2) - (width // 2)
    y = (update_window.winfo_screenheight() // 2) - (height // 2)
    update_window.geometry(f'+{x}+{y}')
    
    label = ttk.Label(update_window, text="正在更新，请稍候...")
    label.pack(pady=20)
    
    progress = ttk.Progressbar(update_window, mode='indeterminate')
    progress.pack(pady=10, padx=20, fill='x')
    progress.start()
    
    # Run update in a separate thread
    def run_update():
        result = updater.update()
        root.after(0, lambda: finish_update(result, update_window, callback))
    
    thread = threading.Thread(target=run_update)
    thread.start()
    
    return update_window

def finish_update(result, update_window, callback):
    update_window.destroy()
    callback(result)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    try:
        updater = AutoUpdater()
        if not updater.load_config():
            messagebox.showerror("错误", "无法加载更新配置，请检查网络或服务器状态")
        elif not updater.check_update():
            # messagebox.showinfo("更新结果", "当前已是最新版本")
            start_target_app()
        else:
            while is_process_running(TARGET_APP):
                response = messagebox.askyesno("提示", f"{TARGET_APP} 正在运行，请关闭它以继续更新。\n是否重试？")
                if not response:
                    root.destroy()
                    exit()
            
            def update_callback(result):
                if result:
                    messagebox.showinfo("更新结果", f"更新成功！当前版本: {updater.config['version']}")
                    start_target_app()
                else:
                    messagebox.showerror("更新结果", "更新失败，请查看日志或联系管理员")
            
            # Show updating window and run update in thread
            show_updating_window(root, updater, update_callback)
            root.mainloop()  # Keep the GUI running
            exit()  # Exit after mainloop ends
    except Exception as e:
        messagebox.showerror("错误", f"更新过程中发生错误: {str(e)}")
    
    root.destroy()
```

