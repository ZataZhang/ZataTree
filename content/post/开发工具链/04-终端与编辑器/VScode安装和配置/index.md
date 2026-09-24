---
title: VScode使用教程|cursor使用教程
description: 
date: 2025-03-03T00:00:00+08:00
image: images/index/index.png
# slug: 文件夹名/index.md ## 必填，文件夹名/index.md
# image: helena-hertz-wWZzXlDpMog-unsplash.jpg
categories:
    # - DeepLearning
    # - Chart
    # - Python
    # - LLM
    # - Library
    # - PaperReading
    # - Study
    # - Other
    # - Knowledge points
    - Project_Application
tags:
    - VScode
    - 教程
---
参考：
https://blog.csdn.net/weixin_46474921/article/details/132841711

## 安装及设置

### 1. 下载安装

[VScode官网](https://code.visualstudio.com/)
注意，这一步最好全部打勾

![alt text](image/index/index.png)

### 2. 设置默认terminal为cmd

![设置terminal](image/index/index-1.png)

### 自动fetch远程分支

Git 默认不会自动从远程拉取状态更新。只有当你显式运行 `git fetch` 或 `git pull` 时，本地仓库才会更新远程分支引用。如果你希望在 VS Code / Cursor 中自动感知远程分支变化，需要开启自动 fetch：

**设置路径**：`Settings` → 搜索 `git.autofetch` → 勾选启用

![alt text](images/index/image-5.png)

建议同时设置自动 fetch 间隔（默认 3 分钟）：

```json
{
  "git.autofetch": true,
  "git.autofetchPeriod": 180
}
```

**注意**：如果仓库的 remote 名不是默认的 `origin`，VS Code 的 Git 插件和 GitHub Pull Requests 插件可能无法正确识别上下文。需要在 `settings.json` 中显式配置：

```json
{
  "githubPullRequests.remotes": ["zata", "origin", "upstream"]
}
```

配置完成后执行 `Cmd+Shift+P` → `Developer: Reload Window` 生效。

### 设置文件自动保存

![设置文件自动保存](image/index/index-4.png)

### vscode右侧的预览窗口设置

![预览窗口](image/index/index-5.png)

设置方法，在设置里面搜索minimap

![设置显示预览窗口](image/index/index-6.png)

### vscode写markdown插入图片时放在指定目录

参考 https://juejin.cn/post/7244809769794289721

打开粘贴选项

![Edit-Paste As：Enable 勾选](index/PixPin_2025-04-28_10-21-02.png)

![vscode写markdown插入图片时放在指定目录](image/index/index-7.png)

```bash
**/*.md      images/${documentDirName}/${fileName}   # 以原始文件名放到 ./assets/<md文件名>/<图片文件名>
**/*.md      images/${documentBaseName}/${documentBaseName}.${fileExtName}   # 重新以md文件名命名图片名
**/*.md      images/${documentBaseName}/image.${fileExtName}   # 以image.png重命名放到images/文件名    文件夹下
```

### vscode折叠代码 ctrl+k ctrl+0

![alt text](image/index/index-8.png)

### Diff Editor settings

1. 取消相同的代码被折叠

![相同代码被折叠](images/index/image.png)![不打勾不折叠](images/index/image-1.png)![alt text](images/index/image-2.png)

2. diff 双栏变一栏

![单次设置](images/index/image-3.png)![默认设置](images/index/image-4.png)

---

---

---

## vscode 插件

```json
GitLG
Office Viewer
Markdown Preview Mermaid Support
```


1. GitLG
![GitLG](images/index/PixPin_2025-10-22_11-54-38.png)

2. office viewer
![alt text](images/index/index-1.png)

`但是有一个非常严重的问题，就是说如果安装了office viewer 会导致vscode自己的image paste失效`

不过我发现一个解决方案，就是改下配置，然后不要用ctrl+v粘贴，而是用鼠标右键然后paste
![setting json](images/index/index-2.png)  
![paste](images/index/index.gif)

当然，如果想支持更多办公文档的查看，那么可以一步到位，直接安装office viewer(Markdown Editor)。但这个插件有一个坑点，就是会更改markdown文件的格式，所以安装之后，可以取消对markdown文件的默认开启方式。方法很简单，只需右键单击一个markdown文件，选择打开方式，在命令栏中选择最下面的为*.md配置默认编辑器，最后点击文本编辑器就可以了。

此外，这个插件内嵌了一个主题，所以安装之后界面的颜色可能会发生变化，不必惊慌，重新选择一个主题就可以了。

3. Markdown Preview Mermaid Support（作者：Matt Bierner）
特点：这是下载量最高、最基础的 Mermaid 插件。安装后，它会无缝集成到 VS Code 原生的 Markdown 预览功能中。
用法：在 .md 文件中输入 ```mermaid 代码块，然后点击 VS Code 右上角的“预览”按钮（或快捷键 Ctrl+Shift+V / Cmd+Shift+V），就能直接在右侧看到渲染出的图表。

## 遇到的问题和解决方案

### vscode 一直 reactivatiing terminals

这个是由于python扩展找不到虚拟环境的问题，具体可以看
https://stackoverflow.com/questions/78886125/vscode-python-extension-loading-forever-saying-reactivating-terminals/78886126#78886126

![图片显示reactivatiing terminals](image/index/index-9.png)

我的解决方法是把python Locator换成js

![把python Locator换成js](image/index/index-10.png)

### 安装工具包之后，桌面cmd窗口可用，但是vscode/cursor不可用

cmd加载成功，但是 cursor ternimal没有生效。
解决办法：完全退出cursor，然后重启cursor

### GitHub Pull Requests 插件一直 Loading

现象：安装 `GitHub Pull Requests and Issues` 插件后，VS Code 侧边栏一直处于 loading 状态，无法正常显示当前仓库的 PR。

优先检查三个点：

```bash
git remote -v
gh auth status
gh pr list --repo OWNER/REPO --state all --limit 10
```

这次遇到的原因是仓库 remote 名不是默认的 `origin`，而是自定义的 `zata`。VS Code 的 GitHub PR 插件默认主要识别 `origin` 和 `upstream`，如果仓库使用了其他 remote 名，插件可能找不到 GitHub 仓库上下文，于是一直 loading。

解决方法：在 VS Code 的 `settings.json` 中显式配置插件要识别的 remote 名：

```json
"githubPullRequests.remotes": [
  "zata",
  "origin",
  "upstream"
]
```

然后执行：

```text
Cmd+Shift+P
Developer: Reload Window
```

如果还是 loading，打开下面这个输出面板看具体报错：

```text
View -> Output -> GitHub Pull Requests
```

另外要注意：如果 PR 已经 merge，插件的 open PR 列表里可能不会显示。可以用命令确认：

```bash
gh pr list --repo OWNER/REPO --state all --limit 10
gh pr view PR_NUMBER --repo OWNER/REPO
```

### macOS 下按 Cmd+Q 直接退出 VSCode

在 macOS 上使用 VSCode / Cursor 时, 按下 `Cmd+Q` 会触发 macOS 的"退出应用"快捷键, 直接把整个 VSCode 进程关掉 (而不是仅关闭当前窗口), 容易丢失未保存的内容。

解决方法是在 VSCode 的快捷键设置里把 `Cmd+Q` 绑定的命令移除或改成无害操作:

1. 打开 `Cmd+K Cmd+S` (Keyboard Shortcuts) 或者 `File → Preferences → Keyboard Shortcuts`。
2. 搜索 `cmd+q` 或 `Quit`, 找到 `Quit` / `workbench.action.quit` 这一项。
3. 双击该项, 选择 `Remove Keybinding` (删除快捷键), 或者改成 `Cmd+Q` 之外的其他组合 (比如改成 `Cmd+Shift+Q` 之类的)。

也可以直接编辑 `keybindings.json` (命令面板 `Preferences: Open Keyboard Shortcuts (JSON)`), 写入:

```json
[
  {
    "key": "cmd+q",
    "command": "-workbench.action.quit"
  }
]
```

加负号 `-` 表示解除该命令的快捷键绑定。保存后重启 VSCode 生效, 此后按 `Cmd+Q` 不会再退出 VSCode, 只会由 macOS 提示要不要退出 (或者完全没反应), 避免误触丢工作内容。
