---
title: flask-构建一个简单的文件同步系统
description: ""
date: 2025-05-12T09:59:01+08:00
image: images/index/index.png
categories:
    - Library
tags:
    - Flask
---



# 使用Python构建文件同步系统：步骤指南

在当今互联网时代，能够在本地机器和远程服务器之间同步文件的能力变得至关重要。无论是备份重要文档、与团队成员共享大文件，还是在多个设备间保持数据一致性，一个强大的文件同步系统都能发挥重要作用。在这篇博客文章中，我们将逐步介绍如何使用Python构建一个简单而强大的文件同步系统，并为大文件传输添加进度条功能。

## 挑战

我们的目标是创建一个系统，能够：

1. 将本地文件上传到远程服务器
2. 从服务器下载文件到本地机器
3. 检查服务器上是否存在某个文件
4. 处理大文件传输并提供可视化反馈

## 解决方案

我们将分两部分构建我们的解决方案：一个使用Flask的服务器端应用程序，和一个与服务器交互的客户端脚本。

### 第一部分：服务器

首先，让我们使用Flask创建一个简单的服务器，它可以处理文件上传、下载和存在性检查。

```python
from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "没有文件部分"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        return jsonify({"message": "文件上传成功"}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"error": "文件未找到"}), 404

@app.route('/check/<filename>', methods=['GET'])
def check_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

这个服务器提供了三个主要端点：
- `/upload` 用于文件上传
- `/download/<filename>` 用于文件下载
- `/check/<filename>` 用于检查服务器上是否存在某个文件

### 第二部分：客户端

现在，让我们创建一个客户端脚本，它可以与我们的服务器交互并处理文件同步。我们将使用 `requests` 库进行HTTP通信，使用 `tqdm` 库来显示进度条。

```python
import requests
import os
from tqdm import tqdm

SERVER_URL = "http://your_server_ip:5000"

def upload_file(filename):
    file_size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"正在上传 {filename}") as pbar:
            response = requests.post(
                f"{SERVER_URL}/upload",
                files={"file": f},
                data={"filename": os.path.basename(filename)},
                headers={"Content-Length": str(file_size)},
                stream=True
            )
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    pbar.update(len(chunk))
    print(response.json())

def download_file(filename):
    with requests.get(f"{SERVER_URL}/download/{filename}", stream=True) as response:
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            with open(filename, 'wb') as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=f"正在下载 {filename}"
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = f.write(chunk)
                        pbar.update(size)
            print(f"文件 {filename} 下载成功")
        else:
            print(response.json())

def check_file(filename):
    response = requests.get(f"{SERVER_URL}/check/{filename}")
    return response.json()['exists']

def sync_file(filename):
    if os.path.exists(filename) and not check_file(filename):
        print(f"正在将 {filename} 上传到服务器...")
        upload_file(filename)
    elif check_file(filename) and not os.path.exists(filename):
        print(f"正在从服务器下载 {filename}...")
        download_file(filename)
    elif not check_file(filename) and not os.path.exists(filename):
        print(f"文件 {filename} 在本地和服务器上都不存在")
    else:
        print(f"文件 {filename} 在本地和服务器上都已存在")

# 使用示例
sync_file("large_file.zip")
```

这个客户端脚本提供了几个关键功能：

1. **文件上传**：将文件发送到服务器，并显示进度条。
2. **文件下载**：从服务器检索文件，并显示进度条。
3. **文件检查**：验证服务器上是否存在某个文件。
4. **同步逻辑**：根据文件在本地和服务器上的存在情况，决定是上传、下载还是跳过该文件。

`sync_file` 函数封装了我们的同步逻辑：
- 如果文件在本地存在但服务器上不存在，则上传。
- 如果文件在服务器上存在但本地不存在，则下载。
- 如果文件在两个位置都不存在，我们会得到通知。
- 如果文件在两个位置都存在，我们会得到通知，无需采取任何操作。

## 整合使用

要使用这个文件同步系统：

1. 在您的远程机器上启动Flask服务器。
2. 在客户端脚本中更新 `SERVER_URL`，使其指向您的服务器。
3. 运行客户端脚本，指定您想要同步的文件。

此外，如果你是本地服务器，进行了内网穿透，可以使用以下代码，优先使用本地ip地址，下面代码做了优化，将函数封装成为一个类

```python
import requests
import os
from tqdm import tqdm
import time

class FileSync:
    def __init__(self, server_url1, server_url2):
        self.SERVER_URL1 = server_url1
        self.SERVER_URL2 = server_url2
        self.server_url = None

    def check_server(self, url):
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_server_url(self):
        if self.check_server(self.SERVER_URL1 + "check/test.txt"):
            self.server_url = self.SERVER_URL1
            return self.SERVER_URL1
        elif self.check_server(self.SERVER_URL2 + "check/test.txt"):
            self.server_url = self.SERVER_URL2
            return self.SERVER_URL2
        else:
            raise Exception("无法连接到任何服务器")

    def upload_file(self, filename):
        self.get_server_url()
        file_size = os.path.getsize(filename)
        with open(filename, 'rb') as f:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"正在上传 {filename}") as pbar:
                response = requests.post(
                    f"{self.server_url}upload",
                    files={"file": (os.path.basename(filename), f)},
                    data={"filename": os.path.basename(filename)},
                    stream=True
                )
                for chunk in iter(lambda: f.read(8192), b''):
                    if chunk:
                        pbar.update(len(chunk))
        print(response.json())

    def download_file(self, filename):
        self.get_server_url()
        with requests.get(f"{self.server_url}download/{os.path.basename(filename)}", stream=True) as response:
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                with open(filename, 'wb') as f, tqdm(
                    total=total_size, unit='B', unit_scale=True, desc=f"正在下载 {filename}"
                ) as pbar:
                    for chunk in response.iter_content(block_size):
                        size = f.write(chunk)
                        pbar.update(size)
                print(f"文件 {filename} 下载成功")
            else:
                print(response.json())

    def check_file(self, filename):
        self.get_server_url()
        basename = os.path.basename(filename)
        response = requests.get(f"{self.server_url}check/{basename}")
        return response.json()['exists']

    def sync_file(self, filename):
        try:
            self.get_server_url()  # 确保使用可用的服务器
            basename = os.path.basename(filename)
            if os.path.exists(filename) and not self.check_file(basename):
                print(f"正在将 {filename} 上传到服务器...")
                self.upload_file(filename)
            elif self.check_file(basename) and not os.path.exists(filename):
                print(f"正在从服务器下载 {filename}...")
                self.download_file(filename)
            elif not self.check_file(basename) and not os.path.exists(filename):
                print(f"文件 {filename} 在本地和服务器上都不存在")
            else:
                print(f"文件 {filename} 在本地和服务器上都已存在")
        except Exception as e:
            print(f"同步过程中发生错误: {str(e)}")

# 使用示例
if __name__ == "__main__":
    sync = FileSync("http://你弟内网ip/:5000", "http://你的公网ip:5000")
    # print(sync.check_file("test.txt"))
    sync.sync_file(r"C:\BaiduSyncdisk\code&note\0A-ZATA\data\光谱数据\MZI酒精数据_21&27&79&30_.xlsx")
```

## 结论

这个简单而有效的文件同步系统展示了我们如何利用Python创建强大的工具来管理不同位置的数据。添加进度条使其特别适用于处理大文件，在可能较长的传输操作期间提供视觉反馈。

虽然这个系统是一个很好的起点，但还有许多方式可以扩展它：
- 添加身份验证以实现安全的文件传输
- 实现文件版本控制
- 创建监视系统，自动同步更改
- 开发图形用户界面，便于交互

祝您编码愉快，愿您的文件永远保持同步！