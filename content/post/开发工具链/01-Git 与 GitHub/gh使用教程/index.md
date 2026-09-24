---
title: gh使用教程
description: "详细介绍 GitHub CLI（gh）的常用命令、认证方式、仓库操作、PR/Issue 流程、Actions、Release、API 调用与自动化实践"
date: 2026-04-12T21:50:00+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - git&github
    - gh
    - github
    - 教程
---

## 1. 常用命令速查

**case**
```bash
# 创建私有仓库并推送本地代码
gh repo create my-project --private --source=. --push
```

```bash
# 查看帮助与版本
gh --version
gh help
gh <command> --help

# 登录与认证
gh auth login
gh auth status
gh auth logout

# 仓库
gh repo clone owner/repo
gh repo create
gh repo view --web
gh repo fork
gh repo sync

# Pull Request
gh pr create --fill
gh pr list
gh pr view
gh pr checkout 123
gh pr diff
gh pr review --approve
gh pr merge

# Issue
gh issue create
gh issue list
gh issue view 123
gh issue comment 123 --body "补充说明"
gh issue close 123

# GitHub Actions
gh workflow list
gh run list
gh run view <run-id>
gh run watch
gh run download <run-id>

# Release
gh release create v1.0.0
gh release list
gh release view v1.0.0
gh release upload v1.0.0 dist/app.tar.gz

# 浏览器与搜索
gh browse
gh browse 123
gh search prs --author @me
gh search issues --owner your-org

# API 与脚本
gh api user
gh api repos/OWNER/REPO/pulls
gh pr list --json number,title,url

# 配置与效率
gh alias set pv "pr view"
gh config set editor vim
gh extension search
gh extension install owner/gh-extension-name
```

## 2. `gh` 是什么

`gh` 是 GitHub 官方命令行工具，核心价值不是替代 `git`，而是把原本要在 GitHub 网页上完成的事情搬到终端里。

适合用 `git` 做的事情：

- 本地提交、分支切换、变基、合并、查看工作区变更
- 与任意 Git 远程交互，而不局限于 GitHub

适合用 `gh` 做的事情：

- 登录 GitHub 账号
- 创建和管理 Pull Request、Issue、Release
- 查看和触发 GitHub Actions
- 直接调用 GitHub API
- 安装 GitHub CLI 扩展

最实用的理解方式是：`git` 管仓库历史，`gh` 管 GitHub 平台能力。

## 3. 安装与初始化

### 安装

常见安装方式如下：

```bash
# macOS
brew install gh

# Windows
winget install --id GitHub.cli

# Ubuntu / Debian
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
  sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
  sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
```

安装后先确认版本：

```bash
gh --version
```

### 登录

最常用的是交互式登录：

```bash
gh auth login
```

执行后通常会依次选择：

- 登录 `GitHub.com` 还是企业版 GitHub
- 使用 `HTTPS` 还是 `SSH`
- 通过浏览器登录还是输入令牌

登录完成后可以检查状态：

```bash
gh auth status
```

如果你已经有环境变量令牌，也可以让 `gh` 直接使用：

```bash
export GITHUB_TOKEN=your_token
gh auth status
```

说明：

- 日常个人开发，交互式 `gh auth login` 最省事
- 在 CI、脚本、自动化环境里，更常见的是 `GITHUB_TOKEN`
- 如果你使用 GitHub Enterprise，可以用 `gh auth login --hostname <hostname>`

## 4. 仓库操作

### 克隆仓库

```bash
gh repo clone owner/repo
```

它本质上还是帮你完成 GitHub 仓库级别的克隆，但写法更统一，也方便后续继续使用 `gh`。

### 创建仓库

```bash
gh repo create
```

这个命令会进入交互流程，通常会问你：

- 仓库名称
- 是否公开
- 是否添加 README
- 是否推送当前目录

如果你想快速把当前项目推到 GitHub，经常很好用。

### 查看仓库信息

```bash
gh repo view
gh repo view --web
gh repo view owner/repo
```

常见用途：

- 在终端查看仓库概要
- 直接在浏览器打开仓库页面
- 脱离当前目录查看别的仓库

### Fork 与同步

```bash
gh repo fork
gh repo sync
```

典型场景：

1. `fork` 别人的仓库到自己账号下
2. 在自己的 fork 上开发
3. 上游仓库更新后，用 `gh repo sync` 同步

如果你平时经常参与开源项目，这两个命令非常顺手。

## 5. Pull Request 工作流

`gh` 最有价值的部分之一，就是把 PR 的完整链路搬到命令行里。

### 创建 PR

```bash
gh pr create
gh pr create --fill
```

`--fill` 会自动用当前分支的提交信息帮你生成标题和描述，适合已经写好了比较规范 commit message 的情况。

常见流程：

```bash
git checkout -b feature/login
git add .
git commit -m "feat: add login page"
git push -u origin feature/login
gh pr create --fill
```

### 查看 PR

```bash
gh pr list
gh pr view
gh pr view 123
gh pr view --web
```

适合查看：

- 当前仓库有哪些 PR
- 某个 PR 的详情
- 直接跳转浏览器继续看评论和检查项

### 切换到某个 PR

```bash
gh pr checkout 123
```

这个命令很适合代码评审场景。你不用先找分支名，直接通过 PR 编号就能把代码拉到本地。

### 查看差异、检查、评审、合并

```bash
gh pr diff 123
gh pr checks 123
gh pr review 123 --approve
gh pr review 123 --comment -b "建议补一个测试"
gh pr merge 123
```

这一组命令基本覆盖了 PR 审查最常见的动作：

- 看 diff
- 看 CI 是否通过
- approve / comment / request changes
- 合并 PR

如果团队流程比较规范，`gh` 能明显减少频繁切浏览器的次数。

## 6. Issue 管理

### 创建与查看

```bash
gh issue create
gh issue list
gh issue view 123
gh issue view 123 --web
```

适合用来做：

- 快速提 bug
- 记录待办事项
- 查看当前仓库未关闭的问题

### 评论、编辑、关闭

```bash
gh issue comment 123 --body "我来处理这个问题"
gh issue edit 123 --add-label bug
gh issue close 123
gh issue reopen 123
```

如果你把 GitHub Issues 当轻量项目管理工具，这一组命令会非常高频。

## 7. GitHub Actions 与 CI/CD

`gh` 对 Actions 的支持很实用，尤其适合你在终端里排查 CI。

### 查看工作流和运行记录

```bash
gh workflow list
gh run list
gh run view <run-id>
```

### 观察运行状态

```bash
gh run watch
```

这个命令适合在你刚 push 代码后盯 CI 结果，不用一直刷新网页。

### 下载产物与重新运行

```bash
gh run download <run-id>
gh run rerun <run-id>
```

常见场景：

- 下载构建产物
- CI 因偶发网络问题失败时重跑
- 快速定位是哪一步报错

## 8. Release 管理

如果你的项目通过 GitHub Release 发版本，`gh` 可以把整个流程命令化。

### 创建与查看 Release

```bash
gh release create v1.0.0
gh release list
gh release view v1.0.0
```

### 上传构建产物

```bash
gh release upload v1.0.0 dist/app.tar.gz
```

这在发布二进制、压缩包、安装包时很方便，尤其适合配合脚本或 CI 自动化。

## 9. `gh api`：把 GitHub API 直接带进终端

很多人低估了 `gh api`，但它其实是 `gh` 最强的能力之一。

### 基本调用

```bash
gh api user
gh api repos/OWNER/REPO
gh api repos/OWNER/REPO/issues
```

如果某个能力暂时没有现成的 `gh <group> <subcommand>`，往往可以直接退回到 `gh api`。

### 搭配 JSON 输出

```bash
gh pr list --json number,title,url
gh issue list --json number,title,labels
gh workflow list --json id,name,path,state
```

这类写法很适合：

- 给 shell 脚本喂数据
- 做自动化统计
- 和 `jq` 配合筛选字段

例如：

```bash
gh pr list --json number,title,author --jq '.[] | {number, title, author: .author.login}'
```

如果你经常写脚本，建议尽快把 `--json`、`--jq` 这套用起来。

## 10. 提效能力：别名、配置、扩展

### alias

```bash
gh alias set pv "pr view"
gh alias set pc "pr create --fill"
gh pv
gh pc
```

适合把高频长命令压缩成自己熟悉的缩写。

### config

```bash
gh config set editor vim
gh config get editor
```

最常见的是设置默认编辑器，避免某些命令唤起你不想用的编辑器。

### extension

```bash
gh extension search
gh extension install owner/gh-extension-name
gh extension list
gh extension upgrade --all
```

扩展机制可以理解为给 `gh` 加外挂命令。对于一些官方没内置、但社区已经做好了的能力，扩展通常是最快方案。

## 11. 推荐的实际使用方式

如果你是个人开发者，可以先掌握这条最实用链路：

1. `gh auth login`
2. `gh repo clone owner/repo`
3. `git checkout -b feature/xxx`
4. 本地开发并提交
5. `git push -u origin feature/xxx`
6. `gh pr create --fill`
7. `gh pr checks`
8. `gh pr merge`

如果你负责 CI/CD 或平台维护，再补上这些：

- `gh workflow list`
- `gh run list`
- `gh run watch`
- `gh release create`
- `gh api`

如果你经常参与开源协作，再补上这些：

- `gh repo fork`
- `gh repo sync`
- `gh issue list`
- `gh pr checkout`
- `gh pr review`

## 12. 常见问题

### `gh` 和 `git` 到底怎么分工？

一句话：

- `git` 负责版本控制
- `gh` 负责 GitHub 平台交互

最合理的方式不是二选一，而是组合使用。

### 为什么有些仓库命令要加 `-R`？

因为 `gh` 默认优先使用当前目录对应的仓库上下文。如果你不在仓库目录里，或者你想操作别的仓库，就显式指定：

```bash
gh pr list -R OWNER/REPO
```

### 命令太多记不住怎么办？

先记住三件事：

```bash
gh
gh <command>
gh <command> --help
```

`gh` 的帮助系统本身就做得很好，遇到不熟悉的子命令时直接查帮助通常最快。

## 13. 参考资料

- [GitHub CLI manual](https://cli.github.com/manual/index)
- [GitHub CLI quickstart](https://docs.github.com/en/enterprise-cloud@latest/github-cli/github-cli/quickstart)
- [About GitHub CLI](https://docs.github.com/en/github-cli/github-cli/about-github-cli)
