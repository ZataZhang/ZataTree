---
title: git&github_tutorial
description: git&github使用指南
date: 2025-02-28
slug: git&github ### 必填，文件夹名
image: image/index/index.png
categories:
    - 开发工具链
tags:
    - Git 与 GitHub
    - git&github
    - 教程
---


## 目录
- **Git 基础操作**
  - [git基本使用](#git基本使用)
  - [如果想要临时查看某次commit时项目的全部代码](#如果想要临时查看某次commit时项目的全部代码)
  - [在本地开发环境检查远程是否更新](#在本地开发环境检查远程是否更新)

- **远程仓库操作**
  - [git clone 远程项目,同步远程项目更新](#git-clone-远程项目同步远程项目更新)
  - [git 版本标签](#git-版本标签)

- **分支与合并**
  - [git merge详解](#git-merge详解)
  - [git pull merge git 多人协作的时候怎么解决冲突？](#git-pullmerge-git-多人协作的时候怎么解决冲突)
  - [使用rebase调换最后两个Commit的顺序](#使用rebase调换最后两个Commit的顺序)
  - [软件版本管理与热修复流程](#软件版本管理与热修复流程)

- **版本回退与撤销**
  - [git reset --hard HEAD^ 详解](#git-reset---hard-head-详解andgit-reset---soft-head-详解)
  - [恢复被 Git 合并覆盖的提交并防止未来覆盖](#恢复被-git-合并覆盖的提交并防止未来覆盖)
  - [当前正在进行代码的开发，但是想要看历史commit的项目完整代码，而当前的工作区保证原样](#当前正在进行代码的开发但是想要看历史commit的项目完整代码而当前的工作区保证原样)
  - [回退到上一个版本继续开发的方案](#在-git-中如果你想回退到上一个版本继续开发同时保留已经提交到-main-分支的最新提交可以通过创建新分支并回退的方式实现)
  - [多轮代码提交后才发现重大Bug？如何优雅地修改“上上个” Commit](#多轮代码提交后才发现重大Bug如何优雅地修改上上个-Commit)

- **GitHub 相关**
  - [公式 github github不显示md文件中的公式](#公式-github-github不显示md文件中的公式)
  - [GitHub 分支保护规则（Rulesets）配置](#github-分支保护规则rulesets配置)
  - [Git 进阶教程(git lfs)：从“版本控制”到“内容追踪”](https://mp.weixin.qq.com/s/TEjkisB-s2p-KD_OHS-fnQ)

- **身份验证**
  - [git 使用ssh密钥登录github](#git-使用ssh密钥登录github)
  - [git 使用token登录github 并拉取项目](#git-使用token登录github-并拉取项目如果电脑上已经登录过了需要把账户信息清除掉如果是用ssh密钥登录的也不行清除token账户信息请看下面清除电脑上已经登录的github账户信息)
  - [github 要求2FA认证](#github-要求2fa认证)
  - [github 清除电脑上已经登录的github账户信息](#github-清除电脑上已经登录的github账户信息)
  - [git config --global --add safe.directory 设置安全目录](#git-config---global---add-safe-directory-设置安全目录)

- **问题解决**
  - [解决Mac、linux下使用git命令时中文乱码的办法](#解决mac、linux下使用git命令时中文乱码的办法)
  - [要将远程仓库的 other 分支设置为 main 分支](#要将远程仓库的-other-分支设置为-main-分支并删除原来的-main-分支可以按照以下步骤操作)
  - [使用windows系统服务器做远程开发碰到的问题](#使用windows系统服务器做远程开发碰到的问题)
  - [git clone 出现TLS连接错误](#git-clone-出现以下问题fatal-unable-to-access-xxx-gnutls_handshake-failed-the-tls-connection-was-non-properly-terminated)
  - [git push ssh连接超时问题](#git-push-ssh-connect-to-host-githubcom-port-22-connection-timed-out-fatal-could-not)
  - [远程分支版本冲突问题](#远程分支是v3版本本地的v2版本但是本地修改了文件还没有add也没有commit应该怎么更新本地)
  - [用git hooks解决github大文件报错](#用git-hooks解决github大文件报错100m限制或50m限制大文件50mgit-hooksgit)
  - [云服务器无法访问Github导致git失败方案](#云服务器无法访问github导致git失败方案)
  - [git pull 时出现 "cannot lock ref" 错误的解决方案](#git-pull-时出现-cannot-lock-ref-错误的解决方案)
  - [解决 Git 未检测文件名大小写变化的问题](#Git-无法识别文件名大小写更改一文彻底解决重命名难题)
  - [githook脚本版本控制管理](#githook脚本版本控制管理)
  - [用git hooks解决github大文件报错，100M限制或50M限制|大文件|50M|git hooks|git](#用githooks解决github大文件报错100M限制或50M限制-大文件-50M-githooks-git)
  - [error: cannot lock ref 'refs/remotes/XXX/main': is at XXX...XXX but expected YYY...YYY 解决](#cannot_lock_ref_error)  
  - [一个电脑想要同时使用两个github账号ssh登录](#一个电脑想要同时使用两个github账号ssh登录)

- **实战**
  - [Git 项目依赖管理：Submodule 与 Subtree 实战教程](#Git项目依赖管理-Submodule与Subtree实战教程)
  - [如何将 clone 下来的项目推送到自己的新仓库并同步原始仓库更新](#如何将clone下来的项目推送到自己的新仓库并同步原始仓库更新)

##  git基本使用


 安装

1. windows 安装

![推荐使用便携版](images/index/image-30.png)
![bin目录添加到环境变量](images/index/image-31.png)


2. 简单常用命令

```bash

%%设置用户签名%%
git config --global user.name [username]      
git config --global user.email [useremail]

%%设置对于非ASCII字符的显示方式%%
git config--global core.quotepath false

%%设置init分支名%%
git config --global init.defaultBranch main

git branch --set-upstream-to=origin/<远程分支> <本地分支> # 绑定本地分支和远程分支

# 设置 HTTP/HTTPS 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 或者设置 SOCKS5 代理（更稳定）
git config --global http.proxy socks5://127.0.0.1:7890

git pull --rebase # 变基拉取


git stash push --keep-index  #只 stash 未暂存但已跟踪的修改  加-u 参数同时 stash 未跟踪文件

git stash pop   # 恢复被 stash 的未暂存部分
# 或
git stash apply

git remote prune <remote-name> # 清理本地仓库中对远程仓库 zata 已删除分支的过时跟踪引用。 并不是删除分支


git gc --prune=now  #清理不必要的文件并优化本地仓库


%% 设置远端库别名
git remote add <别名> <网址>

%% 查看远端库
git remote -v

%%获取远程仓库的所有更新，并删除本地已经不存在的远程分支的跟踪引用，以保持本地仓库与远程仓库的同步
git fetch --prune

%%查看本地库状态%%
git status

%%追踪文件，放入暂存区%%
git add [filename]
git add .  #所有文件放入暂存区
%%撤销追踪%%
git restore 【file】

%%删除暂存区的文件%%
git rm --cache 【filename】

%%提交本地库%%
git commit -m "[提交信息]" 【文件名（可以不加）】

%%撤销commit提交%%
git reset --soft HEAD     


%%推送远程库
git push [<远程主机名>] [<本地分支>:<远程分支>] #如果不加分支对应信息就默认上次记录的全部分支
git push origin $(git branch --show-current)  # 将当前分支推送到远程仓库（通常是 `origin`），并保持相同的分支名

%%拉取远程库%%
git pull [<远程主机名>] [<远程分支>:<本地分支>]   # 从远程仓库（名为 origin）的 main 分支拉取代码并自动与本地的 main 分支合并 ,如果方括号里面的不加就默认拉去上一次的
git pull  [<远程主机名>] --depth <分支深度>  [<远程分支>:<本地分支>] # 例如git pull zata --depth 1 hugo:hugo ，用于历史内容过多，只拉取少量历史记录


%%查看引用日志版本信息%%
git reflog 
%%查看详细日志%%
git log
%%以图形化方式查看本地和远程分支的结构%%
git fetch origin
git log --graph --oneline --all --remotes

%%版本穿梭%%  一般用soft多一点
git reset --hard  【版本号】


git log --oneline --graph --all # 显示所有分支的提交记录建议直接使用gitG

--.gitignore--------------------
test* 忽略以test开头的文件
```


## 一些问题解决


### Git Rebase 冲突解决（VS Code） --- 20260308

当你执行 `git rebase <目标分支>` 开始变基后，Git 会尝试将你的提交依次应用到目标分支上。如果在这个过程中发生代码冲突，Git 会自动暂停变基操作，等待你解决冲突。

此时，VS Code 会清晰地提示你当前状态：
*   文件列表中被检测到冲突的文件旁边会出现警告标记（⚠️）。
*   编辑器底部状态栏会显示“合并冲突”的提示。

**解决冲突的核心步骤分为以下环节：**

**第一步：打开并处理冲突文件**
在编辑器中打开有冲突标记的文件，你会看到类似以下结构的代码块：
```
<<<<<<< HEAD
这是你当前分支（正在变基的提交）的代码
=======
这是来自目标分支（或历史提交中）的代码
>>>>>>> commit-hash
```
你需要决定如何整合这些代码。你有两种主要方式来完成这一步：
*   **使用 VS Code 内置工具**：直接点击冲突标记区域上方出现的选项按钮。你可以选择“接受当前更改”、“接受传入更改”或“保留双方更改”。如果内置选项不能满足需求，你也可以手动删除所有的 `<<<<<<<`、`=======` 和 `>>>>>>>` 标记，并编辑成你最终想要的代码。
*   **使用 GitLens 扩展**：如果你安装了 GitLens 扩展，它会提供更加强大和直观的并排对比视图，方便你逐块检查和解决冲突。

**第二步：标记冲突文件为已解决**
在完成一个文件的所有冲突编辑后，你需要告诉 Git 这个文件的冲突已经处理完毕。
*   你可以在 VS Code 的源代码管理侧边栏（√图标）中，找到该文件，点击旁边的“+”号或右键选择“暂存更改”。
*   或者在终端中执行命令 `git add <文件名>`。

**第三步：继续变基过程**
标记完所有已解决的冲突文件后，你需要让 Git 继续执行变基操作。
*   在 VS Code 中，你可以点击底部状态栏的“继续变基”按钮。
*   或者在终端中执行命令 `git rebase --continue`。

随后，Git 会尝试应用下一个提交，你可能需要重复上述步骤来解决后续可能出现的冲突，直到所有提交都应用完成。

**其他有用的命令**
在变基过程中，你还可以使用以下命令：
*   `git rebase --skip`：跳过当前正在应用的提交（请谨慎使用，这意味着完全丢弃这个提交的更改）。
*   `git rebase --abort`：完全终止本次变基操作，分支将回退到执行 `git rebase` 之前的状态。

**快速流程总结**
一个典型的 rebase 解决冲突流程可以简化为：
```
git rebase main
# 发生冲突
# 使用 VS Code 编辑文件解决冲突
git add .
git rebase --continue
# 可能重复“编辑->add->continue”直到完成
```

**最后的重要提示**
*   变基过程可能需要解决多个提交引发的冲突，请耐心处理完一个后继续下一个。
*   随时可以使用 `git status` 命令来查看当前的变基进度和状态。
*   在进行变基等重写历史的操作前，创建一个备份分支是一个好习惯：`git checkout -b backup-branch`。


### 解决Mac、linux下使用git命令时中文乱码的办法

![中文乱码](images/index/image-22.png)

```bash
git config --global core.quotepath false
```

### 要将远程仓库的 `other` 分支设置为 `main` 分支，并删除原来的 `main` 分支，可以按照以下步骤操作：

1. **确保本地仓库是最新的**
   首先，确保你的本地仓库与远程仓库同步，并切换到 `other` 分支：
   ```bash
   git fetch origin
   git checkout other
   git pull origin other
   ```

2. **将 `other` 分支推送到远程的 `main` 分支**
   使用 `git push` 的 `--force` 选项，将 `other` 分支的内容强制覆盖远程的 `main` 分支：
   ```bash
   git push origin other:main --force
   ```
   这会将 `other` 分支的内容直接推送到远程的 `main` 分支，覆盖原有的 `main` 分支。

3. **更新本地仓库**
   在本地仓库中，确保你的 `main` 分支与远程的 `main` 分支同步：
   ```bash
   git checkout main
   git pull origin main
   ```

4. **删除本地的 `other` 分支（可选）**
   如果你不再需要本地的 `other` 分支，可以删除它：
   ```bash
   git branch -d other
   ```

5. **验证操作**
   确认远程仓库的分支状态：
   ```bash
   git fetch origin
   git branch -r
   ```
   你应该看到 `origin/main` 包含了 `other` 分支的内容，且 `origin/other` 仍然存在（除非你也想删除它）。

6. **（可选）删除远程的 `other` 分支**
   如果 `other` 分支不再需要，可以删除远程的 `other` 分支：
   ```bash
   git push origin --delete other
   ```


### 使用windows系统服务器做远程开发碰到的问题 


- 使用哪个版本的git

    感觉这个没有太大关系，不过后面发现便携版本的git也是可用的，感觉以后可以就使用便携版的，毕竟不需要界面

- 使用windows远程服务器进行git pull总是卡死

    2025年0617，买了一个腾讯云到2h2G服务器，想用来写hugo博客， 但是在pull代码的时候总是卡死，试了很多次，我以为是服务器性能太烂了，最后发现，如果使用http地址pull的话就没有问题。但是后面又发现使用github的http地址的话会存在无法push的情况，所以我最终给出的解决方案就是：使用github的http地址拉取项目，然后使用ssh地址同步
    ![alt text](images/index/image-18.png)


### 如果想要临时查看某次commit时项目的全部代码
```bash
git log --oneline
git checkout <commit哈希值>   # 查看代码
git checkout main  # 返回主分支
```



### 在本地开发环境检查远程是否更新


第一种方法

```sh
git log --oneline --graph --all
```

第二种方法

```sh
# 设置跟踪远程分支
git branch --set-upstream-to=origin/<branch> <branch>  # git branch --set-upstream-to=origin/main main


# 查看是否跟踪
git branch -vv


# 下载数据
git fetch origin

# 查看是否有更新
git status 
```

是否跟踪对比

![未跟踪](images/index/image-14.png)
![已经跟踪](images/index/image-13.png)


![可以看见本地和远程分支状态](images/index/image-15.png)

### git clone 远程项目,同步远程项目更新

```sh
git fetch origin #查看远程项目更新
git pull origin 远程分支：本地分支
```




### git 版本标签

1. 什么是版本标签？
标签（Tag） 是 Git 中的一个引用（reference），指向某个特定的提交。
它通常用于标记一个稳定的发布版本，比如 v1 表示第一个正式版本。
在 GitHub 上，标签还会显示在 Releases 页面，便于用户下载或查看。
两种标签类型
轻量标签（Lightweight Tag）：只是一个简单的指针，指向某个提交，不包含额外信息。
附注标签（Annotated Tag）：包含额外元数据（如创建者、日期、描述），更常用于正式发布。

```bash
# 假设你已经完成代码更改并提交
git add .
git commit -m "Finalize version 1.0"

# 创建一个轻量标签（简单标记当前提交）
git tag v1

# 或者创建一个附注标签（带描述信息，推荐用于正式发布）
git tag -a v1 -m "Release version 1.0"

# 查看所有本地标签
git tag

# 推送单个标签到远程仓库（如 GitHub）
git push origin v1

# 或者推送所有标签到远程仓库
git push origin --tags

# （可选）如果需要删除本地标签
git tag -d v1

# （可选）如果需要删除远程标签
git push origin --delete v1
```


### git merge详解


如果没有冲突，Git 会自动完成合并，并创建一个合并提交（merge commit，如果需要的话）。如果有冲突，Git 会暂停合并，提示你解决冲突（后面会讲怎么处理）。

1. 无冲突的合并（Fast-forward）

如果 main 分支没有额外改动，而 feature 分支只是基于 main 增加了提交，Git 会执行"快进合并"（fast-forward）。这时候历史记录会变成一条直线，看起来像是直接在 main 上开发了一样。

2. 有额外提交的合并（Merge Commit）

如果 main 和 feature 都有各自的提交，Git 会创建一个新的合并提交，保留两个分支的历史。
命令一样：
```bash
git merge <分支名>
```
但是，合并后，Git 会自动生成一个 Merge commit，这样，从历史上看，分支信息就非常清楚。

3. 冲突的合并
当两个分支修改了同一文件的同一部分，Git 无法自动决定用哪个版本，就会报冲突。这时你需要手动解决：

运行 git merge feature 后，Git 会提示冲突文件。
打开这些文件，冲突部分会被标记为：
```
<<<<<<< HEAD
（main 分支的内容）
=======
（feature 分支的内容）
>>>>>>> feature
```
编辑文件，保留你想要的部分，删除标记。
解决完后，标记文件为已解决："git add <filename>"，然后提交："git commit -m '解决冲突'

- 实用技巧
查看合并状态：用 git status 检查当前是否在合并过程中。
中止合并：如果合并出了问题，想放弃，可以用：

git merge --abort

- 指定合并策略：默认情况下 Git 会自动选择合并方式，但你可以用选项调整，比如强制非快进合并：

git merge --no-ff feature


### 如何解决 "fatal: Need to specify how to reconcile divergent branches" 错误

 问题根源：什么是“分支分叉”？

这个错误的核心原因是：**您的本地分支和它所跟踪的远程分支，各自都有了新的、对方不知道的提交。**

让我们用一个形象的例子来说明：

1.  您和您的同事都在 `main` 分支上工作。你们最后一次同步时的代码状态是 `Commit O`。

2.  之后，您在本地写了新功能，并创建了两个提交 `A` 和 `B`。

3.  在您提交的这段时间里，您的同事完成了另一个任务，并将他的提交 `C` 和 `D` 推送（push）到了远程仓库。

这时，Git 的历史记录就变成了两条独立的路径，即“分叉”了：

  A---B   <-- 您的本地 `main` 分支

 /

---O---C---D   <-- 远程 origin/main 分支

当您执行 `git pull` 时，Git 发现它无法简单地“快进”（Fast-forward）来更新您的代码，因为它不知道应该如何处理这两条分叉的路径。为了避免自动操作可能带来的混乱，新版 Git 强制要求您必须明确告诉它您的合并策略。

 二、 核心概念：两种合并策略 Merge vs. Rebase

要解决分叉问题，您有两种主要的方法：`Merge` (合并) 和 `Rebase` (变基)。

 方案 A：临时解决本次问题



您可以只在本次 `pull` 命令中指定策略。



* **使用 Rebase (推荐)：**

    ```bash

    git pull --rebase

    ```

    这会用变基的方式拉取并应用远程更新。



* **使用 Merge：**

    ```bash

    git pull --no-rebase  # 或者 git pull --merge

    ```

    这会用传统合并的方式，并生成一个合并提交。



 方案 B：永久配置默认行为 (一劳永逸)



为了避免每次都输入额外参数，您可以为 Git 设置一个全局的默认 `pull` 行为。



* **将 Rebase 设置为默认 (推荐)：**

    如果您喜欢干净的线性历史，这是大多数现代开发者的首选。

    ```bash

    git config --global pull.rebase true

    ```



* **将 Merge 设置为默认：**

    如果您偏爱保留所有合并痕迹的传统方式。

    ```bash

    git config --global pull.rebase false

    ```



* **更严格的 `ff-only` 策略：**

    还有一个选项是 `fast-forward only`。

    ```bash

    git config --global pull.ff only

    ```

    这个设置意味着，只有当您的本地分支没有任何新提交时（即可以“快进”时），`git pull` 才能成功。如果分支出现分叉，`pull` 会直接失败，强制您手动执行 `git rebase` 或 `git merge`，让您对每一次合并操作都更加谨慎。




### |git pull|merge| git 多人协作的时候怎么解决冲突？


使用git-pull 然后git-commit 最后git-push 

如果有冲突可以看[get merge使用](#git-merge详解)

![alt text](image/git@github/git@github.jpg)





### 使用rebase调换最后两个Commit的顺序

```Markdown

# Git 教程：使用 rebase 调换最后两个 Commit 的顺序



本教程将指导你如何使用 `git rebase -i`（交互式 rebase）来调换你本地最后两个 commit 的顺序。## 场景



你通过 `rebase` 将你的本地修改放在了远程分支的最新 commit 之上，但你现在希望反过来，让你自己的修改在前面，让远程的 commit 成为最后一个。**你当前的状态 (HEAD 指向你的修改):**

... -> 远程的最后一个commit -> 你的本地修改 (HEAD)



**你希望达到的状态 (HEAD 指向远程的 commit):**

... -> 你的本地修改 -> 远程的最后一个commit (HEAD)



---



## ⚠️ 重要警告



此操作会**重写 Git 历史**。



**请只在尚未将这些 commit 推送（push）到远程仓库时执行此操作。**

如果你已经推送了 `你的本地修改`，强行修改历史（`git push --force`）会给你的协作者带来严重问题。



---



## 操作步骤



### 步骤 1: 启动交互式 Rebase



你需要编辑最后两个 commit。运行以下命令来启动交互式 rebase，`HEAD~2` 表示“从 HEAD 开始往前数 2 个 commit”。



```bash

git rebase -i HEAD~2

步骤 2: 在编辑器中编辑 Rebase 列表

运行上述命令后，Git 会打开你的默认文本编辑器，显示一个列表。这个列表的顺序是从旧到新（从上到下）。

它看起来会是这样：

pick <hash_A> 远程的最后一个commit 的消息

pick <hash_B> 你的本地修改 的消息



# Rebase ...

# Commands:

# p, pick <commit> = use commit

# ...

pick <hash_A> 是那个较旧的 commit（远程的 commit）。

pick <hash_B> 是那个较新的 commit（你的本地修改）。

步骤 3: 调换 Commit 顺序

你只需要在编辑器中交换这两行的文本顺序，把你的本地修改放到上面（即让它更早发生）：

修改为：

pick <hash_B> 你的本地修改 的消息

pick <hash_A> 远程的最后一个commit 的消息

步骤 4: 保存并退出编辑器

保存文件并关闭编辑器。Git 会立即按照你指定的新顺序重新应用这两个 commit。

步骤 5: 验证结果

操作完成后，你可以使用 git log 来检查历史记录，确认顺序已经被正确调换。

Bash



# 查看最后两个 commit

git log --oneline -2

你现在应该会看到 远程的最后一个commit 的消息 在最上面（最新）的位置。

附录：如何在编辑器中快速调换行顺序

在步骤 3 中，你不需要手动剪切和粘贴。几乎所有编辑器都支持“移动当前行”的快捷键（将光标放在该行任意位置即可）。

常用 GUI 编辑器

Visual Studio Code (VS Code):

Windows / Linux: Alt + ↑ (上移) / Alt + ↓ (下移)

macOS: Option + ↑ (上移) / Option + ↓ (下移)

Sublime Text:

Windows / Linux: Ctrl + Shift + ↑ (上移) / Ctrl + Shift + ↓ (下移)

macOS: Cmd + Ctrl + ↑ (上移) / Cmd + Ctrl + ↓ (下移)

Notepad++:

Ctrl + Shift + ↑ (上移) / Ctrl + Shift + ↓ (下移)

常用终端编辑器 (Git 默认)

Vim / Vi (最常见的默认编辑器):

按 Esc 键确保你处于普通模式 (Normal Mode)。

将光标移动到你想移动的行。

输入 ddp：dd (剪切当前行) + p (粘贴到下一行)，效果是与下一行交换。

输入 ddkP：dd (剪切) + k (上移) + P (粘贴到上一行)，效果是与上一行交换。

(在你的场景中，光标在第二行 pick <hash_B> ... 上时，按 ddkP 即可)

Nano (较简单的编辑器):

Nano 没有直接的“移动行”快捷键，你必须使用剪切和粘贴：

将光标放在要移动的行上。

按 Ctrl + K (剪切该行)。

将光标移动到目标位置（例如，移动到第一行）。

按 Ctrl + U (粘贴该行)。
```



### |公式 | github | github不显示md文件中的公式
`第一种方法：使用github推荐的公式写法（推荐）`
在写md的时候，使用
```
$`  和  `$  
```
来包围行内公式
```
```math  
和
	```
```
来包围单行公式，如下

![alt text](images/index/image.png)

`第二种方法： 插件`

但是还是会有一部分显示不正确
![alt text](images/index/image-1.png)

解决方法：安装插件：https://chrome.google.com/webstore/detail/mathjax-plugin-for-github/ioemnmodlmafdkllaclgeombjnmnbima/related
![插件名](images/index/image-2.png)



### git 使用ssh密钥登录github
` 注意一个密钥只能登录一个github，如果你想要在新的github账户上面添加旧的ssh密钥，就会报错`
准备工作：本地先下载安装好git，注册并登陆github账号
在注册好后的github账号中先创建一个仓库
在本地git创建SSH key
第一步：设置全局的用户名和邮箱（这样主要是不用总是重填）
```cpp
git config --global user.name '用户名' // 切换到你的github用户名上
git config --global user.email 'github账号注册用的邮箱'
```
第二步：生成密钥，有可能提示没有这个库，需要安装一下，去搜索一下
```cpp
ssh-keygen -t rsa -C "你的邮箱地址"
```

第三步：查看自己本地的密钥，执行以下命令

```cpp
ls -al ~/.ssh // 查看本机是否有秘钥文件 没有秘钥文件生成秘钥文件
cd ~/.ssh
ls  // 查看 .ssh 中有什么文件
cat id_rsa.pub // 查看本地的公钥
cat id_rsa // 查看本地的私钥
（如果是windows系统可以直接到C盘的对应用户名文件夹下的.ssh文件夹中查看）
```
	
	
第四步：将公钥复制粘贴到github上

> github上点击头像，点击Settings，进入后点击 SSH and GPS keys，接着点击 New SSH key
> 将公钥粘贴在key输入框那里，Title则随便输入可以就行

![github ssh](images/index/image-3.png)

### `git 使用token登录github 并拉取项目` （如果电脑上已经登录过了，需要把账户信息清除掉。**如果是用ssh密钥登录的也不行**，清除token账户信息请看下面"清除电脑上已经登录的github账户信息"）


<table>
    <tr>
        <td >
        	<img src="images/index/image-4.png" >图1  打开设置
        </td>
        <td >
       		<img src="images/index/image-5.png"  >图2 开发者设置
       	</td>
       	        <td >
       		<img src="images/index/image-6.png"  >图3 点击Token
       	</td>
    </tr>
        <tr>
        <td >
        	<img src="images/index/image-7.png" >图4  生成classic Token
        </td>
        <td >
       		<img src="images/index/image-8.png"  >图5 设置命名和权限
       	</td>
    </tr>
</table>

**最后一步：**
在新设备上pull或者push的时候，会让你登录，有两种方式，一种是账号密码，另一种就算token，选择token，然后粘贴上一步生成的token就可以了


### github 要求2FA认证
今天上线的时候突然发现，github要求我设置2FA认证，不然就不能登录，手机号我必然是没有的，只能用安全密钥控制
具体的github说明在这里：https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication

一句话说，就是需要用TOPT密钥管理工具生成动态密码，然后输入动态密码登录，然后第一次登录会给你一个github-recovery-codes.txt,如果更换设备需要使用这个恢复码登录新设备，然后登录新设备之后也是会给你一个新的恢复码


如果是第一次登录，看到github要求进行2FA，可以安装如下  chrome插件：Github 2FA（去chrome商店搜索）

![Github 2FA应用图标](images/index/image-12.png)

然后你回到github页面刷新，在上面图片红框的那个位置就会出现一个30s的密码，输入就可以确认，确认好之后会让你下周恢复密钥，记得下载保存


### github 清除电脑上已经登录的github账户信息
step1： 进入控制面板点击用户账户

![控制面板-用户账户](images/index/image-9.png)

step2：管理windows凭证

![windows凭证](images/index/image-10.png)

step3：删除github相关的凭证


![删除github凭证](images/index/image-11.png)

### git config --global --add safe.directory 设置安全目录

 命令用途
`git config --global --add safe.directory` 命令用于将指定的目录添加到 Git 的安全目录列表中，解决 Git 安全机制导致的仓库访问问题。

 问题背景
从 Git 2.35.2 开始，Git 引入了更严格的安全机制，默认情况下会拒绝访问由其他用户拥有的目录中的 Git 仓库。这通常发生在以下情况：
- 在 WSL (Windows Subsystem for Linux) 环境中
- 在共享目录或挂载的目录中
- 在 Docker 容器中访问宿主机目录
- 在多用户系统中

 命令语法
```bash
git config --global --add safe.directory <directory-path>
```

 使用示例
```bash
# 添加单个目录到安全目录列表
git config --global --add safe.directory /code/GRT

# 添加当前目录到安全目录列表
git config --global --add safe.directory "$(pwd)"

# 添加多个目录
git config --global --add safe.directory /path/to/repo1
git config --global --add safe.directory /path/to/repo2
```

 查看当前安全目录列表
```bash
# 查看所有安全目录
git config --global --get-all safe.directory

# 查看所有全局配置
git config --global --list | grep safe.directory
```

 删除安全目录
```bash
# 删除特定的安全目录
git config --global --unset-all safe.directory /code/GRT

# 删除所有安全目录配置
git config --global --unset-all safe.directory
```

 常见错误信息
当遇到安全目录问题时，Git 会显示类似以下的错误：
```
fatal: detected dubious ownership in repository at '/code/GRT'
To add an exception for this directory, call:
    git config --global --add safe.directory /code/GRT
```

 安全注意事项
1. **谨慎添加目录**：只添加你信任的目录，避免添加系统关键目录
2. **使用绝对路径**：建议使用绝对路径而不是相对路径
3. **定期检查**：定期检查安全目录列表，删除不再需要的目录
4. **环境隔离**：在不同环境中使用不同的安全目录配置

 替代方案
如果不想使用全局配置，也可以：
1. **使用本地配置**：在特定仓库中使用 `--local` 而不是 `--global`
2. **修改目录权限**：确保目录的所有权正确
3. **使用 Git 环境变量**：设置 `GIT_SAFE_DIRECTORIES` 环境变量

 验证配置
配置完成后，可以验证是否生效：
```bash
# 进入目标目录
cd /code/GRT

# 尝试执行 Git 命令
git status

# 如果没有错误信息，说明配置成功
```

### GitHub 分支保护规则（Rulesets）配置

在团队协作中，保护主分支（如 `main`）是非常重要的一项最佳实践。GitHub 提供了 **Rulesets**（规则集）功能，可以灵活地配置分支保护策略，而无需启用组织级别的付费功能。

下面介绍两种常见的配置方案：

**方案一：极简保护（防删 + 防强制推送）**

适用于个人仓库或小型项目，仅开启最核心的两项保护：

- **Restrict deletions** — 限制删除匹配的分支，防止误删主分支。
- **Block force pushes** — 阻止强制推送，避免历史被覆盖。

配置截图如下：

![极简分支保护](images/index/image-32.png)

**方案二：严格保护（推荐用于团队项目）**

适用于多人协作的项目，要求更规范的代码合入流程：

- **Restrict deletions** — 限制删除分支。
- **Require a pull request before merging** — 必须通过 Pull Request 才能合并代码。
- **Require status checks to pass** — 要求指定的 CI 检查通过后才能合并。例如：
  - `Python Quality Gate`
  - `Frontend Build`
- **Block force pushes** — 阻止强制推送。

配置截图如下：

![严格分支保护](images/index/image-33.png)

> **提示**：Rulesets 对私有仓库完全免费即可使用。对于团队项目，建议至少开启「Require a pull request before merging」和「Require status checks to pass」，以保证代码质量和审计追踪。

### `git clone 出现以下问题：fatal: unable to access XXX: gnutls_handshake() failed: The TLS connection was non-properly terminated.`

`git clone 出现以下问题：fatal: unable to access 'https://github.com/QwenLM/Qwen.git/': gnutls_handshake() failed: The TLS connection was non-properly terminated.`

可以参考stack overflow里面的[Stack](https://stackoverflow.com/questions/68801315/gnutls-handshake-failed-the-tls-connection-was-non-properly-terminated-while)
我是执行下面两行代码解决（ubuntu系统）

```cpp
apt-get update
apt-get install curl
```




### `[git push] ssh: connect to host github.com port 22: Connection timed out fatal: Could not....`
最有可能是防火墙问题，可以参考github官方的解决方法 用443端口解决
https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port

第一步,用以下代码测试443端口是否可用

```cpp
ssh -T -p 443 git@ssh.github.com
```

如果出现这样就是可用的，那么恭喜，十拿九稳了！
![alt text](images/index/image-16.png)
用如下ssh地址替代原来的

```cpp
git clone ssh://git@ssh.github.com:443/YOUR-USERNAME/YOUR-REPOSITORY.git
```
注意是替代，直接用原来的地址加端口是不行的。
![alt text](images/index/image-17.png)


拿下！




### `远程分支是v3版本，本地的v2版本，但是本地修改了文件还没有add也没有commit，应该怎么更新本地？`
**1. 第一步：首先保存你的本地修改：**

> `git stash `
> 
> 这会将你当前的修改暂时保存起来

**2. 第二步：拉取远程更新**

> `git fetch origin`

**3. 第三步：更新本地分支到远程版本**

> `git merge FETCH_HEAD`

**4. 第四步，恢复你之前的本地修改**

> ```cpp git stash pop ```

**5. 如果在恢复 stash 时遇到冲突，你需要手动解决这些冲突。解决完冲突后，你可以:**

> 添加解决冲突后的文件 git add .
> 
>  提交你的修改 git commit -m "your commit message"

**提示：**

如果你想在应用 stash 前查看保存了什么内容，可以用 git stash list 查看 stash 列表
如果你想查看具体改动，可以用 git stash show -p
如果合并时遇到问题，随时可以用 git status 查看当前状态
如果想放弃当前操作回到起点，可以用 git reset --hard HEAD（注意这会丢失未提交的修改）



### 用githooks解决github大文件报错100M限制或50M限制-大文件-50M-githooks-git



如果你已经commit了大文件，并且报错了，可以使用下面方法，基本上都起作用

```bash 
apt-get install git-filter-repo

# 删除指定的大文件（路径必须完全匹配）
git filter-repo --path "路径地址" --invert-paths
```

如果还没有提交

```bash
# 1. 把大文件取消追踪
git rm --cached "path/to/large/file"   # 引号括起来的是大文件地址
# 2. 把大文件加入.gitignore
echo "path/to/large/file" >> .gitignore
# 3. 更改提交  （当然不commit直接git push  XXX 也是可以的）
git add .gitignore
git commit -m "Update .gitignore to exclude large files"
git push XXX main:main --force
```
如果已经在过去的几次commit提交了，并且知道在哪个commit开始出现，可以使用以下方法
```bash
# 1. 撤销最近的提交，但保留更改
git reset --soft HEAD~1
# 如果大文件在更早的提交（比如倒数第二次），用 HEAD~2 或具体哈希：
# git reset --soft abc123^  # abc123 是包含大文件的提交

# 2. 移除大文件
git rm --cached "大文件名"

# 3.重新提交
git commit -m "Remove large file XXX"

# 4. 强制推送
git push XXX main:main --force

```


我写了一个git hooks 文件，在commit大于设定size的文件的时候，拦截commit，并且把大文件名写入.gitignore ，同时从缓存区中移除大文件
**进行版本控制的时候，经常会由于大文件导致上传github出问题，并且版本回退也比较麻烦。
实际上我们很少代码文件会超过50M，而往往是由于数据文件过大导致错误，这些数据文件往往我们可能都不需要进行版本控制**
<font color = "red" size = 5>于是，不如直接通过脚本，默认不对这些大文件进行版本控制
</font>


代码   （文件名设置为pre-commit，防在.git/hooks目录下，注意文件名要一致，这涉及到git hooks的逻辑，不做过多解释）


```py

#!/usr/bin/env python3
# 我在2025年之前用的是 #!/bin/python,但是报错了，改成了上面的内容
import subprocess
import os


if __name__ == "__main__":
    files = subprocess.check_output(['git', 'diff', '--cached', '--name-status'], text=True, encoding='utf-8').split('\n')
    for file in files:
        if len(file.split("\t")[0]) > 0 and file.split("\t")[0] != 'D':
            file_path = file.split("\t")[-1]
            file_size = os.path.getsize(file_path)
            size_in_mb = file_size / (1024 * 1024)
            if size_in_mb >= 50:
                with open('.gitignore', 'a', encoding='utf-8') as f:
                    f.write(file_path + '\n')
                try:
                    # Remove the file from the Git index (staged area)
                    subprocess.check_output(['git', 'rm', '--cached', file_path])
                    print("Removed {} from stage".format(file_path))
                except subprocess.CalledProcessError as e:
                    print("Error removing file from stage: {}".format(e))
                
                try:
                    # Reset the file to unstage changes
                    subprocess.check_output(['git', 'reset', file_path])
                except subprocess.CalledProcessError as e:
                    print("Error while resetting file: {}".format(e))

                print("The file is larger than 50MB and has been added to .gitignore. Please confirm and recommit!")
                print(file_path + "\n")
                exit(1)

```

![](images/index/index.png)


![演示](images/index/index-1.png)


**下面可以配置全局Git 钩子**



LINUX平台
```bash
# 创建全局 Git 钩子目录
mkdir -p ~/.git-template/hooks

# 创建并编辑 pre-commit 钩子脚本
cat > ~/.git-template/hooks/pre-commit << 'EOF'
#!/bin/bash
MAX_SIZE=$((50 * 1024 * 1024)) # 50MB in bytes

# 获取暂存区所有文件的列表
files=$(git diff --cached --name-only --diff-filter=ACM)

for file in $files; do
    # 检查文件是否存在
    if [ -f "$file" ]; then
        # 获取文件大小（字节）
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -gt "$MAX_SIZE" ]; then
            echo "错误：文件 '$file' 超过 50MB（大小：$((size / 1024 / 1024))MB）"
            exit 1
        fi
    fi
done
exit 0
EOF

# 赋予执行权限
chmod +x ~/.git-template/hooks/pre-commit

# 配置 Git 使用全局钩子模板
git config --global init.templatedir ~/.git-template

# （可选）为现有仓库手动复制钩子（替换 /path/to/your/repo 为实际路径）
# cp ~/.git-template/hooks/pre-commit /path/to/your/repo/.git/hooks/pre-commit
# chmod +x /path/to/your/repo/.git/hooks/pre-commit
```


WINDOWS平台

需要 POWERSHELL  因为环境变量
```powershell
# 创建全局 Git 钩子目录
$templateDir = "$env:USERPROFILE\.git-template\hooks"
New-Item -ItemType Directory -Force -Path $templateDir

# 创建 pre-commit 钩子脚本
$hookPath = "$templateDir\pre-commit"
Set-Content -Path $hookPath -Value @'
#!/bin/sh
MAX_SIZE=$((50 * 1024 * 1024)) # 50MB in bytes

# 获取暂存区所有文件的列表
files=$(git diff --cached --name-only --diff-filter=ACM)

for file in $files; do
    # 检查文件是否存在
    if [ -f "$file" ]; then
        # 获取文件大小（字节）
        size=$(wc -c < "$file")
        if [ "$size" -gt "$MAX_SIZE" ]; then
            echo "错误：文件 '$file' 超过 50MB（大小：$((size / 1024 / 1024))MB）"
            exit 1
        fi
    fi
done
exit 0
'@

# 赋予执行权限（Windows 下无需 chmod，但确保 Git Bash 支持）
# 配置 Git 使用全局钩子模板
git config --global init.templatedir "$env:USERPROFILE\.git-template"  # 如果你不用变量，那么就赋绝对路径

# （可选）为现有仓库手动复制钩子（将以下路径替换为实际仓库路径）
# $repoPath = "C:\path\to\your\repo"
# Copy-Item -Path $hookPath -Destination "$repoPath\.git\hooks\pre-commit"
```


**也可以按照下面进行手动配置**

1. 首先创建一个文件夹，然后git init，可以手动将上面代码粘贴修改pre-commit文件

![配置文件夹](images/index/index-3.png)

2. 配置全局钩子，需要绝对路径

![配置全局](images/index/index-2.png)


3. 可以测试一下，原理就是git init的时候，把设置的这些配置复制一份

![创建的新本地git仓库](images/index/index-4.png)

![测试大文件](images/index/index-5.png)


### cannot_lock_ref_error

![cannot_lock_ref_error](images/index/index-6.png)

```bash 
root@ce4322c051c6:/codes/dataAnalysisModels# git pull 
remote: Enumerating objects: 193, done.
remote: Counting objects: 100% (193/193), done.
remote: Compressing objects: 100% (178/178), done.
remote: Total 191 (delta 10), reused 188 (delta 10), pack-reused 0 (from 0)
Receiving objects: 100% (191/191), 115.48 MiB | 149.00 KiB/s, done.
Resolving deltas: 100% (10/10), completed with 2 local objects.
error: cannot lock ref 'refs/remotes/zata/main': is at 801efa1db3242f2be077de0d34e4eb29af0a5751 but expected aab6c46b69629454c3ad76e5a030157169eabb6e
From github.com:zata-zhangtao/dataAnalysisAndModeling_In-GY
 ! aab6c46..801efa1  main       -> zata/main  (unable to update local ref)
```

我的解决方法是
```bash
git fetch --prune
git pull
```


### 云服务器无法访问Github导致git失败方案


可以先去这个网站，哪些ip可用

https://ping.chinaz.com/github.com


然后要修改服务器端的HOSTS

例如：
```
20.205.243.166 github.com
20.205.243.166 raw.githubusercontent.com
```

hosts位置在    /etc/hosts



## 知识点


### GitHub Actions 密钥管理全指南：Repository、Environment 与 Organization Secrets 的区别与最佳实践

在配置 GitHub Actions CI/CD 流水线时，管理敏感信息（API Key、数据库密码、部署 Token）是重中之重。GitHub 提供了多种存储 Secrets（密钥）的方式，最常见的是 **Repository Secrets**，但你可能也注意到了 **Environment Secrets** 和 **Organization Secrets**。

它们到底有什么区别？如果我想让一个变量在几十个仓库里通用，又该怎么办？这篇文章将为你彻底理清这三者的关系、优先级和最佳应用场景。

**一、Repository Secrets vs. Environment Secrets**

这是最基础的两个概念，决定了你的密钥是在“仓库级别”可见，还是在“特定部署环境”下可见。

**1. Repository Secrets (仓库级密钥)**

这是最常用的类型。
*   **位置**：`Settings` -> `Secrets and variables` -> `Actions` -> `Repository secrets`
*   **作用域**：整个代码仓库。仓库内的任何 Workflow、任何分支、任何 Job 都可以直接读取。
*   **适用场景**：
    *   通用的 CI 工具 Token（如 Codecov, SonarQube）。
    *   构建阶段需要的非敏感于环境的凭证（如拉取私有 Docker 镜像的 Token）。

**2. Environment Secrets (环境级密钥)**

这是为 CD（持续部署）设计的更高级功能。
*   **位置**：`Settings` -> `Environments` -> 选择环境（如 `production`） -> `Environment secrets`
*   **作用域**：仅限在 Workflow YAML 中明确指定了该环境的 Job。
*   **核心优势**：
    1.  **部署保护（Deployment Protection Rules）**：你可以设置 **Required reviewers (人工审批)**。例如，Workflow 运行到部署生产环境的步骤时会暂停，直到管理员点击"Approve"，代码才能拿到 Environment Secret 并继续执行。
    2.  **同名变量覆盖**：允许开发环境和生产环境使用同一个变量名（如 `DB_HOST`），但值不同。

**代码示例：如何使用 Environment Secret**

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    # 关键点：必须声明 environment，才能读取到该环境下的 Secret
    environment: production 
    steps:
      - name: Deploy
        env:
          # 如果 production 环境里定义了 API_KEY，这里读到的就是生产环境的 Key
          API_KEY: ${{ secrets.API_KEY }}
        run: ./deploy.sh
```

**3. 对比总结**

| 特性 | Repository Secrets | Environment Secrets |
| :--- | :--- | :--- |
| **可见性** | 所有 Job 可见 | 仅声明 `environment: xxx` 的 Job 可见 |
| **审批机制** | 不支持 | **支持人工审批、等待计时器等** |
| **优先级** | 较低 | **最高** (覆盖同名 Repository Secret) |
| **典型用途** | 单元测试、Lint 检查、构建镜像 | 生产环境数据库密码、AWS 生产证书 |

---

**二、进阶痛点：我想定义所有仓库都能用的变量怎么办？**

当你拥有 20 个微服务仓库，且都需要使用同一个 NPM Token 或者 Slack 通知 Webhook URL 时，在每个仓库里重复配置 Repository Secrets 会让人崩溃。

这时你需要 **Organization Secrets (组织级密钥)**。

**1. 什么是 Organization Secrets？**

*   **位置**：组织主页 -> `Settings` -> `Secrets and variables` -> `Actions`。
*   **前提**：你的仓库必须属于一个 Organization（组织账号），个人账号不支持此功能。

**2. 强大的访问策略 (Access Policy)**

在创建组织密钥时，你可以控制它的传播范围：
*   **All repositories**：组织下所有（现有和未来新建的）仓库都能自动读取。
*   **Private repositories only**：仅私有仓库可用（防止开源项目泄露公司 Token）。
*   **Selected repositories**：手动勾选特定仓库可用（**推荐**，遵循最小权限原则）。

**3. Organization Variables (组织级变量)**

除了加密的 Secrets，GitHub 还允许在组织级定义 **Variables**（明文变量）。
*   适用于非敏感配置，如 `API_BASE_URL`、`COMPANY_NAME`。
*   在代码中通过 `${{ vars.MY_VAR }}` 访问。

---

**三、终极问题：同名变量的优先级（覆盖逻辑）**

如果我在 Organization、Repository 和 Environment 里都定义了同一个名字的变量（比如 `DATABASE_URL`），GitHub 会读取哪一个？

遵循 **“越具体，优先级越高”** 的原则：

1.  **Environment Secrets** (最高优先级) 👑
2.  **Repository Secrets** (中等优先级)
3.  **Organization Secrets** (最低优先级)

**实战场景：**
*   你在 **组织级** 设置了 `SLACK_WEBHOOK` 用于日常通知。
*   突然有个特定仓库 `Project-X` 需要发送通知到另一个独立的 Slack 频道。
*   你只需在 `Project-X` 的 **Repository secrets** 里新建一个同名的 `SLACK_WEBHOOK`。
*   GitHub 会自动优先使用仓库级的配置，而不会影响组织内其他 99 个仓库。

---

**四、最佳实践决策清单**

在创建变量前，请对照此清单选择存储位置：

1.  **这个变量是所有（或多个）项目通用的吗？**
    *   是 -> **Organization Secrets** (如：公司通用的 NPM Token, Slack Webhook)。
    *   否 -> 往下看。

2.  **这个变量涉及“生产环境”或“高风险”操作吗？**
    *   是（如 AWS Prod Key, 生产库密码）-> **Environment Secrets** (并开启人工审批保护)。
    *   否 -> 往下看。

3.  **这个变量需要在不同的环境（Dev/Test/Prod）有不同的值吗？**
    *   是 -> **Environment Secrets** (在不同环境里设同名变量)。
    *   否 -> 往下看。

4.  **默认选项：**
    *   上述情况都不是 -> **Repository Secrets**。

---

**结语**

掌握这三个层级的 Secrets 管理，不仅能让你的 GitHub Actions Workflow 代码更简洁（由 `if/else` 地狱转变为统一变量名），还能大幅提升 CI/CD 流程的安全性。

**Tip**: 如果你是个人开发者账号，无法使用 Organization Secrets，建议创建一个免费的 Organization 并将仓库 Transfer 进去，以便享受全局变量管理的便利。



### 将Python包发布到GitHub并通过pip安装的教程

1. **创建Python包结构**  
   构建以下目录结构：  
   ```
   your_package/
   ├── your_package/
   │   ├── __init__.py
   │   └── your_module.py
   ├── setup.py
   ├── README.md
   ├── LICENSE
   └── requirements.txt
   ```

2. **编写关键文件**  
   - **setup.py** 示例：  
     ```python
     from setuptools import setup, find_packages

     setup(
         name='your_package_name',
         version='0.1.0',
         packages=find_packages(),
         install_requires=[
             'requests>=2.25.1',
         ],
         author='Your Name',
         author_email='your.email@example.com',
         description='A short description of your package',
         long_description=open('README.md').read(),
         long_description_content_type='text/markdown',
         url='https://github.com/yourusername/your_package',
         classifiers=[
             'Programming Language :: Python :: 3',
             'License :: OSI Approved :: MIT License',
         ],
     )
     ```  
   - **your_package/__init__.py**：  
     ```python
     __version__ = '0.1.0'
     ```

3. **初始化Git并上传到GitHub**  
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your_package.git
   git branch -M main
   git push -u origin main
   ```

4. **创建GitHub Release（可选，但推荐）**  
   - 访问GitHub仓库页面，点击"Releases" -> "Create a new release"  
   - 输入版本号（如v0.1.0），发布

5. **通过pip安装**  
   - 直接从GitHub安装：  
     ```bash
     pip install git+https://github.com/yourusername/your_package.git
     ```  
   - 指定分支：  
     ```bash
     pip install git+https://github.com/yourusername/your_package.git@branch_name
     ```  
   - 指定版本（需要有release）：  
     ```bash
     pip install git+https://github.com/yourusername/your_package.git@v0.1.0
     ```

6. **发布到PyPI（可选，允许标准pip安装）**  
   - 安装工具：  
     ```bash
     pip install twine build
     ```  
   - 构建包：  
     ```bash
     python -m build
     ```  
   - 上传到PyPI：  
     ```bash
     twine upload dist/*
     ```  
   - 之后可使用：  
     ```bash
     pip install your_package_name
     ```

**注意事项**：  
- 确保`setup.py`信息准确  
- 设置清晰的GitHub仓库描述和topics  
- 使用MIT或其他合适的许可证  
- 编写详细的README.md，包含安装和使用说明  
- 发布到PyPI需注册账号并配置API token





### git-reset---hard-head-详解andgit-reset---soft-head-详解

```bash
git reset --hard HEAD
```
效果：

撤销所有未提交的更改（包括工作目录和暂存区）。
HEAD 指向的提交成为当前状态，之前的修改全部丢失（不可恢复，除非有其他备份）。

```bash
git reset --soft HEAD
```

功能：将当前分支的指针重置到 HEAD 指向的提交，但保留工作目录和暂存区的所有更改。
效果：

撤销最近的提交（将 HEAD 指针移到当前提交），但修改的内容仍保留在工作目录或暂存区。
可以重新调整或重新提交这些更改。



下面我将逐个参数解释这条命令的含义：

 命令分解
1. **`git reset`**:
   - `git reset` 是 Git 用来重置当前分支的 HEAD（当前分支指针）到指定状态的命令。
   - 它可以影响 Git 的三个主要区域：
     - **工作目录（Working Directory）**：你当前编辑的文件。
     - **暂存区（Staging Area/Index）**：通过 `git add` 添加的文件。
     - **提交历史（Commit History）**：Git 仓库中的提交记录。

2. **`--hard`**:
   - `--hard` 是 `git reset` 的一个选项，指定重置的模式。
   - 它表示**完全重置**，不仅会移动 HEAD 指针，还会：
     - 重置工作目录中的文件内容，使其与指定的提交状态一致。
     - 清空暂存区的内容。
     - 丢弃所有未提交的更改（包括工作目录和暂存区的修改）。
   - 简单来说，`--hard` 会让你的工作目录、暂存区和提交历史完全恢复到指定的提交状态，**不可恢复已丢弃的更改**。

3. **`HEAD^`**:
   - `HEAD` 是 Git 中的一个指针，指向当前分支的最新提交。
   - `^` 是一个相对引用，表示"当前 HEAD 的上一个提交"（即父提交）。
   - 因此，`HEAD^` 表示当前分支最新提交的上一个提交。
   - 如果当前分支的提交历史是 `A <- B <- C`（C 是 HEAD），那么 `HEAD^` 指向 `B`。

 整体含义
`git reset --hard HEAD^` 的作用是：
- 将当前分支的 HEAD 指针移动到上一个提交（`HEAD^`）。
- 重置工作目录和暂存区，使其与 `HEAD^` 指向的提交状态完全一致。
- **丢弃**当前 HEAD 提交（最新提交）以及工作目录和暂存区的所有未提交更改。

 示例场景
假设你的提交历史如下：
```
A <- B <- C (HEAD)
```

### githook脚本版本控制管理

在 Git 项目中，`.githooks` 目录中的钩子（hook）脚本默认是不会被 Git 版本控制系统自动纳入版本管理的，因为 `.githooks` 目录通常被视为本地配置的一部分。为了将 Git 钩子脚本保留到项目中并与团队共享，你需要采取一些额外的步骤。以下是具体的方法：

 方法一：将钩子脚本纳入版本控制
1. **将 `.githooks` 目录重命名或移动到项目中**：
   - 默认情况下，Git 钩子存储在 `.git/hooks` 目录中，这些文件不会被 Git 跟踪。你可以将钩子脚本移动到项目的一个自定义目录（例如 `githooks` 或 `hooks`），并纳入版本控制。
   - 示例：
     ```bash
     mkdir githooks
     mv .git/hooks/pre-commit githooks/pre-commit
     ```

2. **配置 Git 使用自定义钩子目录**：
   - 使用以下命令告诉 Git 使用项目中的自定义钩子目录：
     ```bash
     git config core.hooksPath githooks

      cd githooks
     # 查找所有文件 (f) 并赋予执行权限 
     find . -type f -exec chmod +x {} \;
     ```
   - 这会让 Git 使用 `githooks` 目录中的钩子脚本，而不是默认的 `.git/hooks`。

3. **将钩子脚本提交到版本控制**：
   - 将 `githooks` 目录添加到 Git 版本控制：
     ```bash
     git add githooks
     git commit -m "Add git hooks to project"
     git push
     ```

4. **团队成员同步配置**：
   - 其他团队成员在克隆或拉取项目后，需要手动运行 `git config core.hooksPath githooks` 来启用自定义钩子路径。或者，你可以通过脚本自动设置。

 方法二：使用脚本自动安装钩子
为了让团队成员无需手动配置 `core.hooksPath`，你可以在项目中添加一个安装脚本，自动将钩子脚本复制到 `.git/hooks` 目录。

1. **创建安装脚本**：
   - 在项目根目录创建一个脚本（例如 `install-hooks.sh`）：
     ```bash
     #!/bin/bash
     cp githooks/* .git/hooks/
     chmod +x .git/hooks/*
     echo "Git hooks installed successfully."
     ```
   - 这个脚本会将 `githooks` 目录中的钩子复制到 `.git/hooks` 目录，并确保它们具有可执行权限。

2. **添加到版本控制**：
   - 将 `install-hooks.sh` 和 `githooks` 目录提交到 Git：
     ```bash
     git add githooks install-hooks.sh
     git commit -m "Add git hooks and install script"
     git push
     ```

3. **运行安装脚本**：
   - 团队成员在克隆项目后，运行以下命令来安装钩子：
     ```bash
     ./install-hooks.sh
     ```

 方法三：使用 Git 模板目录
如果你希望钩子脚本在所有新项目中自动生效，可以配置 Git 的全局模板目录：

1. **创建全局钩子模板**：
   - 复制默认的 Git 钩子模板到自定义目录：(如果你还没有自定义模板目录，可以通过下面的代码创建一个)
     ```bash
     git init --template=/path/to/custom-template
     ```
   - 在 `/path/to/custom-template/hooks` 中添加你的钩子脚本。

2. **也可以配置全局模板路径**就不用第一步了：
   - 设置 Git 的全局模板路径：
     ```bash
     git config --global init.templateDir /path/to/custom-template
     ```
   - 之后，任何新初始化的 Git 仓库都会使用这个模板。
   - 具体的使用和介绍可见shou 配置钩子脚本，请查看[用git hooks解决github大文件报错，100M限制或50M限制|大文件|50M|git hooks|git](#用githooks解决github大文件报错100M限制或50M限制-大文件-50M-githooks-git)。

3. **注意事项**：
   - 这种方法适合个人开发环境，但不适合团队项目，因为模板目录是本地的，无法直接共享。

 方法四：使用工具管理钩子
可以使用一些工具来简化 Git 钩子的管理和共享，例如：

- **Husky**（适用于 Node.js 项目）：
  - 如果你的项目是 Node.js 项目，可以使用 Husky 来管理 Git 钩子。安装 Husky 后，它会自动管理 `.git/hooks` 目录，并在 `package.json` 中定义钩子脚本。
  - 安装：
    ```bash
    npm install husky --save-dev
    ```
  - 配置（在 `package.json` 中）：
    ```json
    "husky": {
      "hooks": {
        "pre-commit": "echo 'Running pre-commit hook'"
      }
    }
    ```

- **pre-commit**（适用于 Python 项目）：
  - 如果是 Python 项目，可以使用 `pre-commit` 框架来管理钩子。创建一个 `.pre-commit-config.yaml` 文件，定义钩子脚本，并提交到版本控制。
  - 安装：
    ```bash
    pip install pre-commit
    pre-commit install
    ```

 注意事项
1. **权限问题**：
   - 确保钩子脚本具有可执行权限（`chmod +x githooks/*`）。
   - 在 Windows 系统上，可能需要额外处理文件权限问题。

2. **跨平台兼容性**：
   - 如果团队成员使用不同操作系统（例如 Windows 和 Linux），确保钩子脚本是跨平台的（例如，使用 Bash 脚本或 Python 脚本）。

3. **文档说明**：
   - 在项目的 `README.md` 中添加说明，告诉团队成员如何启用钩子（例如运行 `install-hooks.sh` 或设置 `core.hooksPath`）。

4. **避免覆盖本地钩子**：
   - 如果直接覆盖 `.git/hooks`，可能会覆盖团队成员的本地钩子配置。使用 `core.hooksPath` 或脚本复制的方式更安全。

 总结
最推荐的方式是将钩子脚本放入项目中的 `githooks` 目录，提交到版本控制，并通过脚本或 `git config core.hooksPath` 自动配置。结合工具如 Husky 或 pre-commit 可以进一步简化管理。根据项目类型和团队习惯选择合适的方法。
- 当前 HEAD 指向提交 `C`。
- 执行 `git reset --hard HEAD^` 后：
  - HEAD 移动到 `B`（`HEAD^`）。
  - 提交 `C` 从当前分支的提交历史中移除（但可能仍存在于 Git 的对象数据库中，直到被垃圾回收）。
  - 工作目录和暂存区的内容恢复到提交 `B` 的状态。
  - 任何未提交的更改（工作目录或暂存区）都会被永久删除。

新的提交历史变为：
```
A <- B (HEAD)
```

 注意事项
- **数据丢失风险**：`--hard` 会永久删除未提交的更改和指定的提交（`HEAD` 到 `HEAD^` 之间的提交）。在执行前，建议使用 `git status` 检查是否有未提交的更改，或者用 `git log` 确认提交历史。
- **备份建议**：如果不确定是否需要丢弃更改，可以先用 `git branch backup` 创建一个备份分支，以保留当前 HEAD 的状态。
- **远程仓库影响**：如果当前分支已经推送到远程仓库（如 GitHub），执行 `git reset --hard HEAD^` 后需要用 `git push --force` 强制推送，这可能会影响其他协作者，需谨慎操作。

 总结
- **`git reset`**: 重置 HEAD 到指定状态。
- **`--hard`**: 完全重置，丢弃工作目录和暂存区的更改。
- **`HEAD^`**: 指向当前 HEAD 的上一个提交。

这条命令的总体效果是"撤销最近一次提交并恢复到上一个提交的状态，同时丢弃所有未提交的更改"。如果你只是想撤销提交但保留更改，可以考虑使用 `git reset --soft HEAD^` 或其他命令（如 `git revert`）。

## 实战 -- 使用



### 软件版本管理与热修复流程

这是一个非常经典的软件版本管理问题。在真实的开发场景中非常常见，通常被称为**“热修复”（Hotfix）或“补丁发布”（Patch Release）**。

为了在不影响 0.6.0 开发进度的情况下修复 0.5.0 的 bug，你需要基于 0.5.0 的代码拉取一个新分支，修复 bug 后发布 0.5.1，然后再把修复代码同步回 main 分支。

以下是标准的处理流程（假设你使用的是 Git）：

**第一步：找到 0.5.0 的代码并拉取新分支**

通常你在发布 0.5.0 时会打一个标签（Tag），或者你能找到发布 0.5.0 时的那个 Commit 记录。我们需要基于这个点创建一个专门用于修复和发布的分支（比如叫 hotfix-0.5.1 或 release-0.5.x）：

```bash
 # 假设你的 0.5.0 标签名为 v0.5.0
git checkout -b hotfix-0.5.1 v0.5.0

 # 如果你没有打标签，可以找到当时的 commit hash（比如 a1b2c3d）
git checkout -b hotfix-0.5.1 a1b2c3d
```

**第二步：在新分支上修复 Bug 并修改版本号**

现在你的代码状态已经完全回退到了 0.5.0 发布时的样子。在这里修复那个 bug，并将项目配置文件中的版本号从 0.5.0 修改为 0.5.1（如果你有 package.json、pom.xml 等文件的话）。提交你的代码：

```bash
git add .
git commit -m "fix: 修复了 0.5.0 版本的严重 bug"
git commit -m "chore: 升级版本号至 0.5.1"
```

**第三步：发布 0.5.1**

现在你可以基于这个 hotfix-0.5.1 分支去打包、测试并发布产品了。发布完成后，别忘了打上新标签：

```bash
git tag v0.5.1
git push origin v0.5.1
git push origin hotfix-0.5.1
```

到这一步，你的用户已经可以拿到没有 bug 的 0.5.1 版本了，而你的 main 分支毫无影响。

**第四步：将修复代码同步回 main 分支（极其重要！）**

这一步绝对不能忘！否则你以后发布 0.6.0 时，这个 bug 还会再次出现（也就是所谓的回归 bug）。你有两种常见的方式将修复同步回 main：

**方式 A：合并分支（Merge）—— 适合 Git Flow 等标准工作流**

```bash
git checkout main
git merge hotfix-0.5.1
 # 如果有冲突，解决冲突后提交
git push origin main
```

注意：这可能会把 0.5.1 的版本号更改也合并进来，你可能需要在 main 分支再次修改版本号回 0.6.0-dev。

**方式 B：摘取提交（Cherry-pick）—— 很多团队更喜欢这种，因为它更干净**

如果你在 hotfix-0.5.1 分支上只有一两个修复 bug 的 Commit，你可以只把修复 bug 的代码拿过来，而不拿修改版本号的代码：

```bash
 # 1. 先用 git log 看一下你修复 bug 的那个 commit 的 hash 值（比如 f8e9d0c）
 # 2. 切换回 main 分支
git checkout main
 # 3. 将修复代码“摘”过来
git cherry-pick f8e9d0c
git push origin main
```

**总结流程图**

```text
 (0.5.0) -----------------------------------> (0.6.0)  [main 分支]
           |                                          ^
           |                                          | (同步修复代码 Merge 或 Cherry-pick)
           +--->[修 bug] ---> (发布 0.5.1) --------------+      [hotfix 分支]
```

通过这种方式，既保证了 0.5.0 用户的可用性，又让 main 分支可以继续安心开发 0.6.0 的新功能。

**关于 Main 分支的历史记录问题**

这个问题非常关键！答案是：这取决于你用哪种方式（Merge 还是 Cherry-pick）把代码同步回 main。准确地说，你关心的“记录”分为两种：修复 Bug 的代码记录（比如提交信息："fix: 修复了 xxx"）和 0.5.1 的发布记录（比如提交信息："chore: 升级版本号至 0.5.1" 以及 v0.5.1 的标签 Tag）。

**情况一：如果你使用的是 Cherry-pick（摘取）—— 推荐方式**

如果你采用的是 cherry-pick，你只把“修复 Bug"的那个 commit 拿到了 main 分支。在 main 的历史中：

*   **能看见：** 修复 Bug 的记录（但 Git 会为它生成一个新的 Commit Hash）。
*   **看不见：** 任何关于"0.5.1"字眼的记录（包括改版本号的 commit 和 0.5.1 的 tag 都不会在 main 上出现）。

结果：main 分支的历史非常干净，看起来就像是在开发 0.6.0 的过程中顺手修了一个 bug，历史记录是一条直线向前。

Cherry-pick 后的 main 记录看起来像这样：

```text
 * 9b8c7d6 (HEAD -> main) fix: 修复了导致崩溃的严重 bug  <-- 这是 cherry-pick 过来的新 commit
 * 5a4b3c2 feat: 0.6.0 的新功能 B
 * 4z3y2x1 feat: 0.6.0 的新功能 A
 * a1b2c3d (tag: v0.5.0) release: 发布 0.5.0
```

**情况二：如果你使用的是 Merge（合并）**

如果你直接在 main 分支执行 `git merge hotfix-0.5.1`。在 main 的历史中：

*   **能看见：** 0.5.1 分支上的所有记录，原封不动地出现在了这里。
*   **能看见：** "chore: 升级版本号至 0.5.1" 的提交。
*   **能看见：** 一个额外的合并记录（比如 "Merge branch 'hotfix-0.5.1' into main"）。

结果：你的 main 分支历史里会混入 0.5.1 的发布痕迹。如果在合并时遇到了代码冲突（比如 main 的版本号已经改成了 0.6.0-dev，而 hotfix 改成了 0.5.1），你还需要手动解决冲突，保留 0.6.0-dev。

Merge 后的 main 记录看起来像这样：

```text
 * d4e5f6g (HEAD -> main) Merge branch 'hotfix-0.5.1' into main  <-- 合并节点
 |\
 | * f8e9d0c (tag: v0.5.1, hotfix-0.5.1) chore: 升级版本号至 0.5.1  <-- 0.5.1 的痕迹进来了
 | * e7d8c9b fix: 修复了导致崩溃的严重 bug
 * | 5a4b3c2 feat: 0.6.0 的新功能 B
 * | 4z3y2x1 feat: 0.6.0 的新功能 A
 |/
 * a1b2c3d (tag: v0.5.0) release: 发布 0.5.0
```

**总结与建议**

如果你不想在 main 分支里看到 0.5.1 这种历史版本号的“噪音”，只想要修复 bug 的代码，那么极其建议使用 **cherry-pick**。

这是大型开源项目（比如 Vue, React）和大多数商业公司的标准做法：

1.  main 分支永远只看前方（0.6.0、0.7.0）。
2.  旧版本（0.5.0）出了问题，在旧版本对应的分支（hotfix-0.5.x）上修补并发布 0.5.1。
3.  把修补代码像“摘樱桃”一样（cherry-pick）摘回 main 分支。

这样 main 里就看不见 0.5.1 的版本发布记录，但 Bug 确实被修好了。



### 变基合并多个提交

```bash
# 例:变基合并最近2个提交
git rebase -i HEAD~2

```
这个命令会打开你的默认文本编辑器（通常是 Vim、VSCode 或 Nano），显示类似以下内容：


```text
pick c2b3a4d 实现用户登录API
pick d3c4b5a 添加输入验证
pick e4d5c6b 移除调试日志
pick f5e6d7a 修复拼写错误

# 变基 b1a2b3c..f5e6d7a 到 b1a2b3c（4个提交）
#
# 命令:
# p, pick <提交> = 使用提交
# r, reword <提交> = 使用提交，但编辑提交信息
# e, edit <提交> = 使用提交，但停下来修改提交
# s, squash <提交> = 使用提交，但合并到前一个提交
# f, fixup <提交> = 类似于"squash"，但丢弃提交信息
# x, exec <命令> = 使用shell运行命令（其余行）
# b, break = 在此处停止（稍后用'git rebase --continue'继续）
# d, drop <提交> = 删除提交
# l, label <标签> = 用名称标记当前HEAD
# t, reset <标签> = 重置HEAD到标签
# m, merge [-C <提交> | -c <提交>] <标签> [# <单行信息>]
# . 创建合并提交，使用原合并提交的信息（如果没有原合并提交，则使用单行信息）
```


我们需要将后面的3个提交"压缩"（squash）到第一个提交中。编辑文件如下：

```text
pick c2b3a4d 实现用户登录API
squash d3c4b5a 添加输入验证
squash e4d5c6b 移除调试日志
squash f5e6d7a 修复拼写错误
```

保存并关闭编辑器。Git 会开始处理这些提交，然后再次打开编辑器让你编辑合并后的提交信息。


### 第四步：编写合并后的提交信息

你会看到一个新的编辑器窗口，显示所有被合并提交的信息：

```text
# 这是一个合并了4个提交的组合提交。
# 第一个提交信息：
实现用户登录API

# 这是第二个提交信息：
添加输入验证

# 这是第三个提交信息：
移除调试日志

# 这是第四个提交信息：
修复拼写错误

# 请输入新的提交信息，以说明此组合提交的更改。
# 以'#'开头的行将被忽略，空信息会中止提交。
```

删除所有内容，编写一个新的、更有意义的提交信息

保存并关闭编辑器，Git 就会完成变基操作。


### 多轮代码提交后才发现重大Bug？如何优雅地修改“上上个” Commit

这是一个为你整理好的博客笔记模板，标题和结构都优化过了，适合发布在 CSDN、掘金、Notion 或个人博客上。

**📌 问题场景**

我在开发中遇到了一个棘手的情况：

1. **位置**：倒数第三个 Commit (`HEAD~2`) 提交的代码有问题。
2. **需求**：我需要对这个 Commit 进行**大规模的修改/重构**。
3. **工具**：VS Code。

直接提交一个新的 Fix Commit 虽然简单，但会让 Git 历史变得脏乱。作为有追求的工程师，我希望历史记录干净整洁。本文记录了两种处理方案：**"手术刀模式 (Rebase)"** 和 **"推土机模式 (Reset)"**。

**🛡️ 核心前提：建立安全沙盒**

**在修改 Git 历史前，永远不要直接在主分支（如 main/dev）上操作！**
一旦操作失误（如变基失败），很难恢复。

**正确做法**：新建一个临时分支进行"实验"。

```bash
git checkout -b fix-old-commit
# 所有的修改都在这个分支上进行，确认无误后再合并回主分支或强推。
```

**方案一：手术刀模式 (Interactive Rebase)**

**适用场景**：只想精准修复那个错误的 Commit，且**必须保留**它后面提交的 Commit 记录（例如后面的提交是别人写的，或者与当前修改无关）。

**操作步骤**

1. **启动变基**：
在 VS Code 终端输入命令，回溯到前 3 个版本：
```bash
git rebase -i HEAD~3
```

2. **标记要修改的 Commit**：
Git 会弹出一个编辑器（或 `git-rebase-todo` 文件），找到那个有问题的 Commit，将行首的 `pick` 修改为 **`edit`**。
> `pick` -> `edit`

3. **修改代码**：
保存并关闭文件后，Git 会暂停在那个 Commit 的时间点。
此时在 VS Code 中进行大规模的代码修改。

4. **提交修正**：
改完后，暂存文件并修补当前 Commit：
```bash
git add .
git commit --amend --no-edit
```

5. **完成变基**：
应用后续的提交，回到现代：
```bash
git rebase --continue
```

*(如果有冲突，在 VS Code 中解冲突 -> add -> continue 即可)*

**方案二：推土机模式 (Reset --soft)**

**适用场景**：觉得最近这几次提交都很乱，或者逻辑强相关。不如**把最近的 3 个 Commit 撤销掉，捏成一个完美的 Commit**。

**操作步骤**

1. **软重置**：
将指针回退 3 步，但**保留文件修改**在暂存区：
```bash
git reset --soft HEAD~3
```

2. **状态变化**：
此时，过去 3 次提交的历史记录消失了，但所有的代码变动都还在，并且处于 **Staged (暂存区/绿色)** 状态。

3. **修改与重构**：
直接在现在的代码基础上进行大规模修改、修复 Bug。

4. **提交新版本**：
```bash
git commit -m "refactor: 重构核心逻辑（合并了之前的多次尝试）"
```

**⚖️ 方案对比总结**

| 特性 | 方案一：Rebase -i (变基) | 方案二：Reset --soft (重置) |
| --- | --- | --- |
| **形象比喻** | **精准手术** 🔪 | **推土机** 🚜 |
| **历史记录** | 保持原有提交数量，只修改其中一个 | 将多个历史提交合并为一个新提交 |
| **后续提交** | 保留后续 Commit 的独立性 | 后续 Commit 也会被合并掉 |
| **冲突风险** | 可能会遇到多次冲突（每个后续 Commit 都可能冲突） | **无冲突**（因为是一次性提交） |
| **推荐指数** | ⭐⭐⭐⭐ (团队协作且需保留历史时) | ⭐⭐⭐⭐⭐ (个人开发或整理烂代码时) |

**💡 VS Code 插件推荐**

如果你不习惯命令行，推荐安装 **Git Graph**。

* **Rebase**: 右键父节点 -> `Rebase current branch on this commit` -> 勾选 `Interactive`。
* **Reset**: 右键目标节点 -> `Reset current branch to this commit` -> 选择 `Soft`。

> **最后提示**：如果你修改的分支已经 Push 到了远程且有同事在协作，请务必与同事沟通，因为修改历史记录需要 `git push -f` (强制推送)，这可能会覆盖同事的代码！

### 如何彻底删除 Git 历史记录中的大文件

本教程旨在解决一个常见问题：当你在 `git push` 时，即使已经删除了某个大文件，GitHub 依然提示 `GH001: Large files detected` 错误，导致推送失败。

 问题场景

你执行了 `git rm a_large_file.pkl` 并创建了一个新的 commit，但在推送时仍然看到类似下面的报错：

```bash
remote: error: File your_project/a_large_file.pkl is 107.01 MB; this exceeds GitHub's file size limit of 100.00 MB
remote: error: GH001: Large files detected.
! [remote rejected] main -> main (pre-receive hook declined)
```
![问题](images/index/image-20.png)

**原因是：** Git 会保存每一次的提交记录。虽然你在最新的提交中删除了该文件，但它依然存在于仓库的过往历史中。推送时，GitHub 会检查所有历史记录，发现这个超大文件后便会拒绝接收。

要解决此问题，必须从 Git 的历史记录中将该文件彻底清除。

-----

 推荐方案：使用 `git-filter-repo` (更简单、更快速)

`git-filter-repo` 是 Git 官方现在推荐用来清理历史记录的工具，它比 Git 的原生命令更高效且易于使用。

 1\. 安装 `git-filter-repo`

如果尚未安装，请先执行安装。

  * **macOS (使用 Homebrew):**
    ```bash
    brew install git-filter-repo
    ```
  * 对于其他系统，请参考其[官方安装文档](https://www.google.com/search?q=https://github.com/newren/git-filter-repo/blob/main/INSTALL.md)。

 2\. 从历史记录中删除文件

在你的本地仓库根目录运行以下命令。**此操作会重写历史记录**。

```bash
# 将 "path/to/your/large_file.pkl" 替换为你的大文件实际路径
git filter-repo --path "path/to/your/large_file.pkl" --invert-paths
```

这条命令会自动处理所有分支和标签，从中移除对指定文件的所有引用。

 3\. 强制推送到远程仓库

由于本地历史已被重写，你需要强制推送来覆盖远程仓库的历史。

```bash
git push --force
```

-----

 备选方案：使用纯 Git 命令 `git filter-branch`

![git filter-branch](images/index/image-21.png)

如果你不想安装任何新工具，可以使用 Git 内置的 `filter-branch` 命令。

**警告：** 此命令非常复杂且速度慢，操作前强烈建议**备份你的整个项目文件夹**。

 1\. 执行历史重写命令

```bash
# 将 "path/to/your/large_file.pkl" 替换为你的大文件实际路径
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch "path/to/your/large_file.pkl"' \
--prune-empty --tag-name-filter cat -- --all
```

  * `--ignore-unmatch`: 确保在不包含该文件的历史 commit 上命令不会报错。
  * 此命令执行速度可能很慢，请耐心等待。

 2\. 清理仓库并回收空间

`filter-branch` 会留下备份。运行以下命令以彻底清除旧数据并压缩仓库。

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

 3\. 强制推送

同样，你需要强制推送来更新远程仓库。

```bash
git push --force
```

-----

 未来建议：使用 Git LFS 管理大文件

为了从根源上避免此类问题，当项目中必须包含大文件时，应使用 **Git Large File Storage (LFS)**。

Git LFS 会将大文件存储在专门的服务器上，而在你的仓库中只保留一个轻量级的指针文件，从而使仓库保持小巧和快速。

 LFS 快速上手

1.  **安装 LFS 客户端**
    ```bash
    # macOS
    brew install git-lfs
    ```
2.  **在仓库中启用 LFS** (每个项目只需执行一次)
    ```bash
    git lfs install
    ```
3.  **追踪指定类型的文件** (例如，所有 `.pkl` 和 `.onnx` 文件)
    ```bash
    git lfs track "*.pkl"
    git lfs track "*.onnx"
    ```
4.  **提交 `.gitattributes` 文件**
    `git lfs track` 命令会创建一个 `.gitattributes` 文件，确保将它添加到版本控制中。
    ```bash
    git add .gitattributes
    git commit -m "Configure Git LFS to track large files"
    ```
5.  之后，你就可以像平常一样 `git add` 和 `git commit` 大文件了，LFS 会自动处理它们。

### 如何优雅地处理不再使用的 GitHub 仓库

当一个项目长期不用，但又不想彻底删除时，你有以下三种方法可以将其"隐藏"起来，同时保留代码。

 方案一：归档仓库 (Archive) - ⭐最推荐

这是 GitHub 官方设计的最佳方案，用于封存项目。

**效果:**

- 仓库从你的主页列表消失。
- 项目变为只读，无法再推送新代码。
- **完整保留**所有代码、提交历史、Issues、PRs、Wiki 和 Star。
- 可以随时一键"取消归档"来恢复项目。

**操作步骤:**

1. 进入仓库页面，点击 `Settings` (设置)。
2. 在 `General` (常规) 标签页，拉到最下方的 `Danger Zone` (危险区域)。
3. 点击 `Archive this repository` (归档这个仓库) 并确认。

 方案二：设为私有仓库 (Make Private)

如果只是不想让公众看到，但自己还可能修改。

**效果:**

- 仓库从公开主页消失，只有你和协作者可见。
- 所有功能（推送、提交）完全正常。
- **注意：** 仓库在你自己的仓库列表中依然可见。

**操作步骤:**

1. 进入仓库 `Settings` -> `General` -> `Danger Zone`。
2. 点击 `Change repository visibility` (更改仓库可见性)。
3. 选择 `Make private` (设为私有) 并确认。

 方案三：作为另一项目的分支 (不推荐)

将旧仓库的历史合并到另一个项目中，然后删除旧仓库。这是一种复杂且有损的操作。

**效果:**

- 代码和提交历史被合并到新项目的一个分支上。
- **警告：** 将**永久丢失**旧仓库所有的 Issues、PRs、Wiki 等宝贵记录。
- 会使主项目的历史变得复杂。

**操作步骤 (命令行):**

```bash
# 1. 进入你的主项目目录
cd /path/to/main-project

# 2. 添加旧仓库为临时远程源
git remote add old_repo https://github.com/user/old-repo.git

# 3. 拉取旧仓库数据
git fetch old_repo

# 4. 基于旧仓库历史创建新分支 (假设其主分支为 main)
git switch -c archive/old-project old_repo/main

# 5. 推送新分支到主项目
git push -u origin archive/old-project

# 6. 删除临时远程源
git remote remove old_repo

# 7. 去 GitHub 网站上手动删除 old-repo 仓库
```

总结对比

| 方法 | 优点 | 缺点 | 推荐度 |
| :--- | :--- | :--- | :--- |
| **归档 (Archive)** | 保留所有记录、操作简单、可逆 | 项目只读 | ⭐⭐⭐⭐⭐ |
| **设为私有 (Private)** | 不公开、可继续编辑 | 仍在自己列表显示 | ⭐⭐⭐⭐ |
| **作为分支合并** | 物理上整合代码 | **丢失Issues/PRs等记录**、操作复杂 | ⭐ |

**结论：** 对于"长期不用但想完整保留"的场景，请始终选择**归档 (Archive)**。

### 一个电脑想要同时使用两个github账号ssh登录

1. 第一步，生成另一个账号专用的ssh密钥和公钥，然后把公钥复制到那个账号的github里面

2. 配置客户端以使用正确账号

vim  ~/.ssh/config

```bash
# zata-zhangtao 账号专用
Host github.com-zata
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_zata
  IdentitiesOnly yes
```

3. 然后更新 remote URL ，使用自定义的Host 

```bash
# 例如原本是： git@github.com:zata-zhangtao/ZataTree.git ，改成
git remote set-url zata git@github.com-zata:zata-zhangtao/ZataTree.git  
```



### 恢复被 Git 合并覆盖的提交并防止未来覆盖

 问题背景
主分支（`main`）的修改在合并（如 `zata_ssh/hugo`）时被覆盖，可能是快速合并或 `ort` 策略自动选择远程分支内容导致。

 恢复被覆盖的提交
1. **查看历史**：
   ```bash
   git reflog main
   ```
   找到合并前的提交（如 `b510d7b`）。

2. **恢复提交**：
   ```bash
   git checkout main
   git reset --hard b510d7b
   ```

3. **备份分支**：
   ```bash
   git branch main-backup main
   ```

4. **推送更改（谨慎）**：
   如果已推送到远程，需强制推送：
   ```bash
   git push --force
   ```
   **警告**：提前通知团队，强制推送会影响远程历史。

 重新合并（避免覆盖）
1. **拉取远程分支**：
   ```bash
   git fetch zata_ssh
   ```

2. **非快速合并**：
   ```bash
   git merge --no-ff zata_ssh/hugo
   ```
   若有冲突，手动解决：
   ```bash
   git add <file>
   git commit
   ```

3. **或使用变基**：
   ```bash
   git checkout zata_ssh/hugo
   git rebase main
   git checkout main
   git merge zata_ssh/hugo
   ```

 预防未来覆盖
- **禁用快速合并**：
  ```bash
  git config --global merge.ff false
  git config --global pull.ff only
  ```
- **预览差异**：
  ```bash
  git diff main zata_ssh/hugo
  ```
- **测试合并**：
  ```bash
  git checkout -b temp-merge
  git merge zata_ssh/hugo
  ```

 注意事项
- 检查合并提交（`61d17c8`, `14e36c9`）的文件变化：
  ```bash
  git show 61d17c8
  ```
- 确认 `main` 跟踪分支：
  ```bash
  git branch -vv
  ```


### 当前正在进行代码的开发，但是想要看历史commit的项目完整代码，而当前的工作区保证原样
```bash
# 临时保存当前工作目录中的未提交更改
git stash

# 切换到指定的 commit（替换 <commit id> 为实际的 commit 哈希值，例如 b2dfde96604dcce732aefccc4c7b4dc1fc8b161a）
git checkout <commit id>

# 返回到原始分支（替换 <branch name> 为实际的分支名，例如 main）
git checkout <branch name>

# 恢复之前保存的更改
git stash pop
```

### 在 Git 中，如果你想回退到上一个版本继续开发，同时保留已经提交到 `main` 分支的最新提交，可以通过创建新分支并回退的方式实现。

以下是一个推荐的方案和详细教程，基于 Git 的最佳实践，确保操作安全且保留所有历史记录。

---

- 方案一(推荐)：
1. 基于当前代码创建一个新分支，在新分支上介绍功能修改情况
2. main分支回退到上一个版本
3. 接着在main分支上进行开发
```bash
git branch <branchName>  # 创建一个新分支
git log --oneline # 查看历史commit，方便下面的切换
git reset --hard <HEAD^ 或者 commitId>
```


- 方案二：
1. 直接在main分支上使用revert方法进行回退

```bash
git revert HEAD
```
这会创建一个新的提交，撤销本次更改，恢复上一步状态，但保留所有提交历史。然后可以继续在 `main` 分支上开发。
![revert](images/index/image-19.png)



### 假设你当前在`main`分支，暂存区有文件`file1.txt`和`file2.txt`，想保存到新分支`feature-branch`
```bash
git checkout -b feature-branch
git commit -m "Add file1 and file2 to feature branch"
git push origin feature-branch
```

### 排查 Git push失败问题 


当 `git push` 失败并提示 `Updates were rejected because the remote contains work that you do not have locally`，可以按照以下步骤查看远程仓库中的更改并解决问题：

1. **获取远程更改**  
   运行 `git fetch origin` 下载远程仓库的最新状态，不影响本地工作目录。

2. **比较本地与远程分支**  
   - 查看提交历史：`git log --oneline --graph --all`  
     显示本地 `main` 和远程 `origin/main` 的提交差异。  
   - 查看文件差异：`git diff --name-only origin/main main`  
     列出远程和本地分支间更改的文件。

3. **检查远程独有提交**  
   使用 `git log main..origin/main --oneline` 查看远程 `origin/main` 中独有的提交。  
   查看具体提交内容：`git show <commit-hash>`。

4. **合并远程更改**  
   运行 `git pull origin main` 合并远程更改到本地。如有冲突，手动解决后提交。  
   然后推送：`git push origin main`。

5. **谨慎使用强制推送**  
   若确定覆盖远程更改，运行 `git push origin main --force`（注意：可能丢失他人工作，仅在确认安全时使用）。

**建议**：优先检查远程更改（`git fetch` 和 `git log`），根据需要合并（`git pull`）或强制推送。



### 推送当前分支到远程仓库并保持分支名

要将当前分支推送到远程仓库并保持当前分支的名字，可以按照以下步骤操作：

 步骤
1. **确认当前分支**：
   确保你位于正确的分支。运行以下命令查看当前分支：
   ```bash
   git branch
   ```
   当前分支会有一个 `*` 标记，例如 `* 0710display-prototype3`。

2. **推送当前分支到远程仓库**：
   使用以下命令将当前分支推送到远程仓库（通常是 `origin`），并保持相同的分支名：
   ```bash
   git push origin $(git branch --show-current)
   ```
   - `git branch --show-current` 会返回当前分支的名称（例如 `0710display-prototype3`）。
   - `git push origin <branch-name>` 将当前分支推送到远程仓库的同名分支。

3. **设置上游分支（如果需要）**：
   如果这是第一次推送当前分支到远程仓库，Git 可能会提示当前分支没有上游分支（`no upstream branch`）。你可以通过以下命令推送并同时设置上游分支：
   ```bash
   git push --set-upstream origin $(git branch --show-current)
   ```
   或者简写为：
   ```bash
   git push -u origin $(git branch --show-current)
   ```
   这会将当前分支推送到远程仓库，并将远程分支设置为当前分支的上游分支，方便后续直接使用 `git push` 或 `git pull`。

 示例
假设你的当前分支是 `0710display-prototype3`，你可以运行：
```bash
git push origin 0710display-prototype3
```
或者更通用地：
```bash
git push origin $(git branch --show-current)
```
如果需要设置上游分支：
```bash
git push --set-upstream origin 0710display-prototype3
```

 注意事项
- **检查远程仓库**：
  确保远程仓库（如 `origin`）已配置正确。运行 `git remote -v` 查看远程仓库的 URL。
- **工作区状态**：
  确保你已提交所有更改（`git commit`），否则运行 `git status` 检查是否有未提交的更改。
- **分支名冲突**：
  如果远程仓库已存在同名分支，推送可能会失败（例如，提示需要拉取或强制推送）。可以先运行 `git fetch origin` 检查远程分支状态，或者使用 `git push --force`（谨慎使用，仅当你确定要覆盖远程分支）。

 验证推送
推送完成后，运行以下命令确认远程分支已创建：
```bash
git fetch origin
git branch -r
```
你应该能看到 `origin/0710display-prototype3` 在远程分支列表中。

如果遇到任何错误（例如权限问题或冲突），请分享错误信息，我可以帮你进一步排查！



### git pull 时出现 "cannot lock ref" 错误的解决方案

当执行 `git pull` 时出现类似以下错误：
```
error: cannot lock ref 'refs/remotes/zata/hugo': unable to resolve reference 'refs/remotes/zata/hugo': reference broken
```

这个错误通常是因为本地的 Git 引用缓存与远程仓库状态不一致导致的。

 问题原因
1. **远程分支被强制更新**：远程仓库的分支可能被强制推送（`git push --force`），导致本地缓存的提交哈希值与远程最新的提交哈希值不匹配。
2. **本地引用损坏或不一致**：本地的 `.git/refs/remotes/` 文件可能被锁定、损坏，或者由于网络中断等原因未正确更新。
3. **Git 缓存问题**：Git 的引用日志或跟踪分支信息可能出现了问题，导致无法正常同步。

 解决方法
以下是几种解决方法，建议按顺序尝试：

**方法 1：清理并重新拉取**
```bash
git fetch --prune
git pull
```
- `git fetch --prune` 会更新本地对远程分支的跟踪信息，并删除远程已不存在的分支引用。

**方法 2：强制更新本地引用**
如果确认远程分支的最新状态是你需要的，可以强制更新本地的远程分支引用：
```bash
git fetch origin
git update-ref refs/remotes/zata/hugo origin/hugo
git pull
```
- `git update-ref` 手动将本地的远程分支引用更新为远程分支的最新状态。

**方法 3：删除并重置本地跟踪分支**
```bash
rm .git/refs/remotes/zata/hugo
git fetch origin
git pull
```
- 手动删除本地引用文件，然后重新获取远程分支信息并拉取。

**方法 4：检查锁文件**
错误信息提到"cannot lock ref"，可能是因为存在锁文件导致引用无法更新：
```bash
rm .git/refs/remotes/zata/hugo.lock
git fetch
git pull
```
- 如果存在锁文件，删除它以解除锁定。

**方法 5：彻底清理并重新克隆（最后手段）**
如果以上方法都无效，且你不介意丢失本地未提交的更改：
```bash
cd ..
rm -rf ZataTree
git clone https://github.com/zata-zhangtao/ZataTree.git
cd ZataTree
```
- **注意**：在执行此操作前，请备份所有本地未提交的更改（例如通过 `git stash` 或复制工作目录）。

 预防措施
1. **避免强制推送**：如果多人协作，尽量避免对公共分支使用 `git push --force`，改用 `git push --force-with-lease` 以减少冲突。
2. **定期清理**：定期运行 `git fetch --prune` 清理无效的远程分支引用。
3. **检查网络**：确保网络连接稳定，避免 `git pull` 中断导致引用不一致。



### Git 无法识别文件名大小写更改？一文彻底解决重命名难题

> 适用场景：你在 Windows 或 macOS 上将 `readme.md` 改为 `Readme.md`，但 `git status` 却毫无反应——别慌，这不是 Git 的 bug，而是文件系统的“锅”。本文教你如何正确处理 Git 中的大小写重命名。

你执行了如下操作：

```bash
mv readme.md Readme.md
```

然后运行：

```bash
git status
```

结果 Git **完全没反应**，仿佛什么都没发生。即使你强制 `git add Readme.md`，Git 可能还会报错：“文件已存在”或“路径冲突”。

为什么？

Git 本身是支持文件名大小写的，但它会**尊重底层操作系统的文件系统行为**：

| 操作系统 | 文件系统 | 是否区分大小写 |
|----------|--------|----------------|
| Linux | ext4, XFS 等 | ✅ 是 |
| macOS | APFS / HFS+（默认） | ❌ 否 |
| Windows | NTFS | ❌ 否 |

在 macOS 和 Windows 上，`readme.md` 和 `Readme.md` 被视为**同一个文件**。因此，当你重命名时，文件系统认为“文件没变”，Git 也就检测不到任何修改。

> 💡 这不是 Git 的缺陷，而是为了兼容性做出的设计选择。

✅ 正确解决方案：使用 `git mv` 分两步走

由于直接重命名会被文件系统“吞掉”，我们需要**绕过文件系统的限制**。最可靠的方法是：**先改成一个临时名字，再改成目标名字**。

步骤示例

假设你想把 `login.js` 改为 `Login.js`：

```bash
# 第一步：重命名为临时文件（名字不能和原名仅大小写不同）
git mv login.js temp_login.js

# 第二步：从临时文件重命名为目标文件
git mv temp_login.js Login.js

# 提交更改
git commit -m "Rename login.js to Login.js"
```

✅ 这样 Git 就会正确记录为一次 **重命名操作**，而不是“删除 + 新增”，保持历史连续性。

⚠️ 常见误区

 ❌ 直接在文件管理器中改名
- 在 Finder（macOS）或资源管理器（Windows）里右键重命名 → Git 无法感知。
- 结果：Git 认为原文件被删除，新文件未跟踪。

 ❌ 强行设置 `core.ignorecase false`
```bash
git config core.ignorecase false
```
- 虽然能让 Git “假装”区分大小写，但在不支持的系统上会导致状态混乱（比如误报文件丢失）。
- **不推荐**，尤其在团队协作中可能引发更多问题。

🛠️ 高级技巧：批量重命名脚本（可选）

如果你有多个文件需要改名，可以写个小脚本：

```bash
#!/bin/bash
# rename_case.sh
old="myfile.txt"
new="MyFile.txt"

git mv "$old" "temp_$$.$old"
git mv "temp_$$.$old" "$new"
echo "Renamed $old → $new"
```

运行：
```bash
chmod +x rename_case.sh
./rename_case.sh
```

> `$`$ 是进程 ID，确保临时文件名唯一。

🌐 跨平台协作建议

如果你的团队同时使用 Windows、macOS 和 Linux，请遵守以下规范：

1. **避免仅靠大小写区分文件名**
   ❌ 不要同时存在 `User.js` 和 `user.js`
2. **统一命名风格**
   ✅ 推荐全小写 + 下划线/短横线：`user_profile.js` 或 `user-profile.js`
3. **重命名一律用 `git mv`**
   即使在 Linux 上，也养成好习惯

🔚 总结

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| Git 不识别大小写重命名 | 文件系统不区分大小写（Win/macOS） | ✅ 用 `git mv` 分两步重命名<br>✅ 避免仅靠大小写区分文件 |

记住：**Git 是忠实的记录者，但它的“眼睛”受限于操作系统**。理解这一点，就能从容应对各种“诡异”行为。

📌 小贴士：下次遇到类似问题，先问自己——“我的文件系统真的支持这个操作吗？”

**作者**：你的名字
**标签**：#Git #开发技巧 #跨平台开发 #版本控制
**发布时间**：2026年1月16日


### 如何将clone下来的项目推送到自己的新仓库并同步原始仓库更新

当你 `clone` 一个项目，你的本地仓库默认会有一个名为 `origin` 的远程连接，指向你克隆的那个仓库地址。现在你既想保留自己的修改，又想同步原始仓库的更新，并最终将所有代码推送到你自己的一个全新仓库。

下面是详细的步骤，分为两种情况：

- **方案一：简单直接，将推送目标"切换"到你的新仓库。**
- **方案二：最佳实践，同时管理"原始仓库"和"你的仓库"两个远程地址。** (推荐)


前提：创建你自己的远程仓库

---

无论使用哪种方案，你都需要先在代码托管平台（如 GitHub、Gitee、GitLab）上创建一个**空的**新仓库。

**非常重要：** 创建仓库时，**不要**勾选"使用README文件初始化仓库"、"添加 .gitignore" 或 "选择许可证"，以避免产生不兼容的提交历史。

创建好之后，复制新仓库的 URL 地址（HTTPS 或 SSH 格式），比如 `https://github.com/your-username/your-new-repo.git`。

---

 方案一：切换远程仓库地址 (简单直接)

这个方案直接把本地仓库的 `origin` 指向从原始仓库地址修改为你的新仓库地址。

 第一步：提交你的本地更改

```bash
git status
git add .
git commit -m "这里写下你的提交信息，比如：添加了xx功能"
```

 第二步：同步原始仓库的更新

```bash
git pull --rebase origin main  # 如果你的分支不是 main，请替换为实际分支名
```

- `git pull --rebase` 会先拉取原始仓库的新提交，再把你本地的提交"重新播放"在最前面，保持提交历史线性。
- 如果遇到冲突，解决后用 `git add <文件名>` 标记解决，然后 `git rebase --continue`。

 第三步：更改远程仓库 `origin` 的 URL

```bash
git remote -v  # 查看当前远程仓库地址
git remote set-url origin <你自己的新仓库URL>
git remote -v  # 再次确认
```

 第四步：推送到你自己的仓库

```bash
git push -u origin main  # -u 建立本地分支与远程分支的追踪关系
```

---

 方案二：添加新的远程仓库 (最佳实践)

这个方案保留了原始仓库的连接（通常命名为 `upstream`），同时添加你自己的仓库作为新的远程连接（通常还叫 `origin`）。这样做的好处是，未来你还可以随时方便地从原始仓库拉取更新。

 第一步和第二步：同方案一

```bash
git add .
git commit -m "你的提交信息"
git pull --rebase origin main
```

 第三步：重命名原始仓库并添加你自己的仓库

```bash
git remote rename origin upstream  # 原始仓库重命名为 upstream
git remote add origin <你自己的新仓库URL>  # 添加你自己的仓库为 origin
git remote -v  # 检查远程仓库配置
```

此时你应该能看到：
- `origin` 指向你的新仓库地址（可读写）。
- `upstream` 指向你最初克隆的那个原始仓库地址（通常是只读的）。

 第四步：推送到你自己的仓库

```bash
git push -u origin main
```

 未来的工作流
- 推送自己的修改：`git push origin main`
- 同步原始项目的更新：
  ```bash
  git fetch upstream
  git rebase upstream/main
  ```

---

 常见问题与注意事项

- **分支名不是 main？**
  - 如果你的分支名是 `master` 或其他，请将命令中的 `main` 替换为实际分支名。
- **遇到冲突怎么办？**
  - Git 会提示你解决冲突。解决后 `git add <文件>`，然后 `git rebase --continue`。
- **推送时遇到权限问题？**
  - 检查你是否有新仓库的写权限，或 SSH/Token 配置是否正确。
- **未来如何同步原始仓库的更新？**
  - 只需 `git fetch upstream`，然后 `git rebase upstream/main`。
