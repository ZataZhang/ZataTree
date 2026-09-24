---
title: 数据集标注工具
description: ""
date: 2025-12-29T15:05:31+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftUseExp
---


## ubiai

![ubiai](images/index/image-2.png)


## LabelStudio

![LabelStudio](images/index/image-1.png)

### install

```sh
docker run -it -p 8080:8080 -v %cd%/mydata:/label-studio/data heartexlabs/label-studio:latest label-studio --log-level DEBUG
```

-v %cd%/mydata:/label-studio/data
    挂载本地目录到容器中，实现数据持久化。
    %cd%：这是 Windows 命令行中的变量，表示当前目录（在 Linux/macOS 中应写作 $(pwd)）。
    所以 %cd%/mydata 指的是你当前文件夹下的 mydata 子目录。
    它被挂载到容器内的 /label-studio/data 路径。

![在我的指定目录下安装](images/index/image.png)