---
title: bash命令使用教程
description: ""
date: 2025-07-18T17:41:56+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - Linux
---

```bash
# ==================================
#       常用 BASH 命令精简版
# ==================================

export all_proxy=socks5h://127.0.0.1:7898 # 设置全局代理，包括 wget, curl 等

# --- 文件和目录管理 (File & Directory Management) ---
ls -l              # 以长格式列出文件和目录
cd /path/to/dir    # 切换目录
pwd                # 显示当前工作目录路径
mkdir new_dir      # 创建新目录
rm file.txt        # 删除文件
rm -r old_dir      # 递归删除目录及其内容
cp source dest     # 复制文件或目录
mv old_name new_name # 移动或重命名文件/目录
touch file.txt     # 创建空文件或更新时间戳
find . -name "*.log" # 在当前目录及子目录中查找.log文件
cat file.txt       # 查看整个文件内容
less file.log      # 分页查看文件内容 (按 'q' 退出)
head -n 20 file.txt # 查看文件前20行
tail -n 20 file.txt # 查看文件后20行
tail -f file.log   # 实时跟踪文件更新

# --- 文本处理 (Text Processing) ---
grep "pattern" file.log        # 在文件中搜索模式
ps aux | grep "nginx"          # 管道示例：查找nginx进程
sed 's/old/new/g' file.txt     # 替换文件中的文本
awk '{print $1, $3}' data.txt  # 提取并打印指定列
sort file.txt | uniq -c        # 排序并统计不重复的行
wc -l file.txt                 # 计算文件的行数

# --- 系统监控与进程管理 (System & Process Management) ---
ps aux             # 显示所有用户的详细进程信
top                # 动态显示进程活动 (按 'q' 退出)
htop               # 交互式进程查看器 (top的增强版)
kill 12345         # 终止指定PID的进程
pkill "process_name" # 根据名称终止进程
df -h              # 显示磁盘空间使用情况 (人类可读格式)
du -sh /path/to/dir # 显示指定目录的总大小
free -m            # 显示内存使用情况 (以MB为单位)
uptime             # 显示系统运行时间

# --- 网络 (Networking) ---
ping google.com    # 测试网络连通性
ip addr show       # 显示网络接口信息 (ifconfig的替代品)
ss -tuln           # 显示监听中的TCP/UDP端口 (netstat的替代品)
curl -I http://example.com # 获取URL的HTTP头部信息
wget http://example.com/file.zip # 下载文件

# --- 权限管理 (Permissions) ---
chmod +x script.sh         # 为脚本添加执行权限
chown user:group file.txt  # 更改文件所有者和组
sudo command               # 以超级用户身份执行命令

# --- 重定向 (Redirection) ---
command > file.txt      # 将输出重定向到文件 (覆盖)
command >> file.txt     # 将输出追加到文件末尾
command < file.txt      # 将文件内容作为命令的输入
command 2> error.log    # 将标准错误重定向到文件

```



## 如何把文件夹里的所有文件移动到同级目录

有时候我们想把一个文件夹（比如文件夹A）里的所有文件，移动到它的同级目录（也就是它的上一级目录）。可以按照下面的步骤操作：

1. 打开终端。
2. 进入文件夹A的上一级目录：
   ```bash
   cd /路径/到/文件夹A的上一级目录
   ```
3. 执行下面的命令，把文件夹A里的所有文件移动到当前目录：
   ```bash
   mv 文件夹A/* .
   ```
   这里，`文件夹A/*` 表示文件夹A里的所有文件，`.` 表示当前目录。

**注意：**
- 这个命令只会移动文件夹A里的文件，不会移动隐藏文件（以.开头的文件）和子文件夹。
- 如果有同名文件，可能会被覆盖，请提前检查。
- 移动完成后，文件夹A会变空，可以用 `rmdir 文件夹A` 删除它。
