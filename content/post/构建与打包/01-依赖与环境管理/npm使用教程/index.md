---
title: npm使用教程
description: ""
date: 2025-07-16T00:40:23+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - npm
---

这是一份详细的 npm (Node Package Manager) 使用教程，从入门基础到高级技巧和最佳实践，希望能帮助你完全掌握这个强大的工具。

-----

### 目录

- [什么是 npm？](#1-什么是-npm)
- [安装 npm](#2-安装-npm)
- [核心概念](#3-核心概念)
- [常用命令详解](#4-常用命令详解)
  - [npm init](#npm-init)
  - [npm install](#npm-install)
  - [npm uninstall](#npm-uninstall)
  - [npm update](#npm-update)
  - [npm run](#npm-run)
  - [npm list](#npm-list)
- [深入理解 package.json](#5-深入理解-packagejson)
- [版本管理：语义化版本 (SemVer)](#6-版本管理语义化版本-semver)
- [进阶命令](#7-进阶命令)
  - [npm outdated](#npm-outdated)
  - [npm ci](#npm-ci)
  - [npm audit](#npm-audit)
  - [npm view](#npm-view)
  - [npx](#npx)
- [最佳实践和技巧](#8-最佳实践和技巧)
- [npm 相关问题解决教程](#npm-相关问题解决教程)
  - [前端启动问题](#1-前端启动问题)
  - [npm 脚本命令详解](#2-npm-脚本命令详解)
  - [常用 npm 脚本配置](#3-常用-npm-脚本配置)
  - [常见问题排查](#4-常见问题排查)
  - [脚本最佳实践](#5-脚本最佳实践)
  - [问题解决总结](#6-问题解决总结)

-----

### 常用命令

以下是最常用的 npm 命令：

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `npm install` | `npm i` | 安装项目依赖 | `npm install` |
| `npm install <package>` | `npm i <package>` | 安装特定包 | `npm install lodash` |
| `npm install <package> --save-dev` | `npm i <package> -D` | 安装开发依赖 | `npm install jest -D` |
| `npm uninstall <package>` | `npm un <package>` | 卸载包 | `npm uninstall lodash` |
| `npm update` | - | 更新包 | `npm update` |
| `npm init` | - | 初始化项目 | `npm init` |
| `npm init -y` | - | 快速初始化 | `npm init -y` |
| `npm start` | - | 启动应用 | `npm start` |
| `npm test` | - | 运行测试 | `npm test` |
| `npm run <script>` | - | 运行脚本 | `npm run dev` |
| `npm list` | `npm ls` | 查看已安装的包 | `npm list --depth=0` |
| `npm outdated` | - | 检查过时的包 | `npm outdated` |
| `npm audit` | - | 安全漏洞检查 | `npm audit` |
| `npm audit fix` | - | 修复安全漏洞 | `npm audit fix` |
| `npx <package>` | - | 执行包而不安装 | `npx create-react-app my-app` |

#### 快速参考

```bash
# 初始化项目
npm init -y

# 安装依赖
npm install [--legacy-peer-deps]   

# 安装/卸载包
npm install <包名>
npm install <包名> --save-dev
npm uninstall <包名>

# 运行脚本
npm start
npm run dev
npm test

# 查看/更新/安全
npm list --depth=0
npm outdated
npm update
npm audit
npm audit fix
```

### 1\. 什么是 npm？

npm (Node Package Manager) 是 Node.js 的默认包管理器。它主要有两个功能：

  * **命令行工具 (CLI)**: 一个安装在你电脑上的命令行工具，用于安装、管理和发布 JavaScript 包。
  * **在线仓库 (Registry)**: 一个巨大的公共在线数据库，存放了成千上万个可重用的 JavaScript 代码包（也称为模块或依赖）。

简单来说，当你需要一个特定功能（比如处理日期、发送网络请求）时，你不需要从零开始写，可以直接从 npm 仓库下载别人已经写好的包，并在你的项目中使用。

### 2\. 安装 npm

npm 是随 Node.js 一起安装的。所以，你只需要安装 Node.js，npm 就会自动安装好。

1.  访问 [Node.js 官方网站](https://nodejs.org/)。
2.  下载推荐的 **LTS (Long Term Support)** 版本并安装。
3.  安装完成后，打开你的终端（在 Windows 上是 Command Prompt 或 PowerShell，在 macOS/Linux 上是 Terminal），运行以下命令来验证安装：

<!-- end list -->

```bash
# 查看 Node.js 版本
node -v

# 查看 npm 版本
npm -v
```

如果能看到版本号，说明安装成功。

### 3\. 核心概念

理解这三个文件/文件夹是掌握 npm 的关键。

  * `package.json`
      * **是什么**：项目的"身份证"或"说明书"。它是一个 JSON 格式的配置文件，位于项目的根目录。
      * **作用**：定义了项目的名称、版本、作者等元数据，并且最重要的是，它记录了项目需要哪些依赖包（`dependencies`）和开发过程中需要哪些依赖包（`devDependencies`）。
  * `node_modules`
      * **是什么**：存放所有项目依赖的文件夹。
      * **作用**：当你使用 `npm install` 命令时，npm 会根据 `package.json` 的记录，从 npm 仓库下载所有需要的包，并存放在这个文件夹里。**这个文件夹通常非常大，不应该提交到版本控制系统（如 Git）中**。
  * `package-lock.json`
      * **是什么**：锁定依赖版本的"快照"文件。
      * **作用**：它精确地记录了 `node_modules` 文件夹中每个包的**确切版本**及其依赖树。这确保了团队中每个成员以及在服务器上部署时，安装的依赖版本都是完全一致的，避免了"在我电脑上能跑"的问题。**这个文件应该提交到版本控制系统**。

### 4\. 常用命令详解

#### `npm init`

用于初始化一个新的 Node.js 项目，它会引导你创建一个 `package.json` 文件。

```bash
# 创建一个新文件夹并进入
mkdir my-project
cd my-project

# 运行初始化命令
npm init
```

系统会问你一系列问题（项目名称、版本、描述等），你可以一路按回车使用默认值。

如果你想快速生成一个默认的 `package.json`，可以使用 `-y` 标志：

```bash
npm init -y
```

#### `npm install`

这是最核心、最常用的命令。

  * **别名**: `npm i`

  * **安装项目所有依赖**:
    如果你的项目里已经有 `package.json` 和 `package-lock.json` 文件，直接运行：

    ```bash
    npm install
    ```

    npm 会读取 `package-lock.json` 并安装所有依赖到 `node_modules` 文件夹。

  * **安装特定包**:

    ```bash
    # 安装一个包，并将其添加到 "dependencies" (生产环境依赖)
    npm install lodash

    # 安装一个包，并将其添加到 "devDependencies" (开发环境依赖)
    # 比如测试工具、打包工具等
    npm install jest --save-dev
    # 或者使用简写
    npm install jest -D
    ```

    > **`dependencies` vs `devDependencies`**

    >   - `dependencies`: 你的应用在生产环境中运行时必须的包（如 React, Express）。
    >   - `devDependencies`: 只在开发和构建过程中需要的包（如 Webpack, ESLint, Jest）。

  * **全局安装**:
    有些包是命令行工具（比如 `nodemon`），需要全局安装才能在任何地方使用。

    ```bash
    npm install -g nodemon
    ```

    > **注意**: 尽量避免过多全局安装，优先使用 `npx` (后面会讲)。

    以下是与依赖管理和冲突解决相关的常用参数：

| 参数                     | 说明                                                                 | 对你的错误的适用场景                                   |
|--------------------------|----------------------------------------------------------------------|-----------------------------------------------------|
| `--legacy-peer-deps`     | 忽略 peer dependency 冲突，使用旧版 npm 的解析逻辑。                   | 绕过 `typescript` 与 `react-scripts` 的版本冲突。      |
| `--force`                | 强制安装，覆盖依赖冲突，可能忽略合法约束。                             | 作为最后手段解决无法解析的冲突。                     |
| `--save`                 | 将包保存到 `package.json` 的 `dependencies` 中（npm < 7 默认行为）。    | 添加新包时使用，非直接相关。                         |
| `--save-dev`             | 将包保存到 `package.json` 的 `devDependencies` 中。                    | 安装 `typescript` 作为开发依赖时使用。               |
| `--no-audit`             | 跳过依赖的安全审计。                                                 | 加速安装，减少审计相关的延迟。                       |
| `--no-fund`              | 抑制 npm 的资助提示信息。                                             | 提高输出日志的可读性。                               |
| `--verbose`              | 提供详细的安装日志输出。                                             | 调试安装问题时查看更多日志信息。                     |
| `--production`           | 仅安装 `dependencies`（跳过 `devDependencies`）。                      | 生产环境部署时使用，与此问题无关。                   |
| `--cache=<path>`         | 指定自定义缓存目录。                                                 | 缓存问题持续存在时使用，较少需要。                   |

#### `npm uninstall`

用于卸载一个包。

  * **别名**: `npm un`

<!-- end list -->

```bash
# 卸载一个包，并将其从 package.json 中移除
npm uninstall lodash

# 卸载一个开发依赖
npm uninstall jest --save-dev
# 或
npm uninstall jest -D
```

#### `npm update`

用于将包更新到 `package.json` 中指定的版本范围内的最新版本。

```bash
# 更新所有包
npm update

# 只更新特定的包
npm update lodash
```

> **注意**: `npm update` 比较保守，它会遵守 `package.json` 中的版本规则（如 `^` 或 `~`）。它不会将包升级到一个新的主版本（Major version）。

#### `npm run`

用于运行在 `package.json` 文件中 `scripts` 部分定义的脚本。

假设你的 `package.json` 如下：

```json
{
  "scripts": {
    "start": "node index.js",
    "test": "jest",
    "build": "webpack"
  }
}
```

你可以这样运行脚本：

```bash
# 运行 start 脚本
npm run start
# 对于 "start", "test", "stop", "restart"，可以省略 run
npm start

# 运行 test 脚本
npm test

# 运行 build 脚本
npm run build
```

#### `npm list`

用于查看当前项目安装了哪些包，以及它们的依赖关系。

```bash
# 查看所有一级包
npm list --depth=0

# 查看全局安装的包
npm list -g --depth=0
```

### 5\. 深入理解 `package.json`

一个典型的 `package.json` 文件结构：

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "A simple project.",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "keywords": ["tutorial", "npm"],
  "author": "Your Name",
  "license": "ISC",
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "nodemon": "^2.0.22"
  }
}
```

  * `"name"`: 包的名称，必须是唯一的、小写的，不能有空格。
  * `"version"`: 当前版本号，遵循[语义化版本](https://www.google.com/search?q=%236-%E7%89%88%E6%9C%AC%E7%AE%A1%E7%90%86%E8%AF%AD%E4%B9%89%E5%8C%96%E7%89%88%E6%9C%AC-semver)。
  * `"description"`: 项目描述。
  * `"main"`: 项目的入口文件。
  * `"scripts"`: 定义可执行的脚本命令。
  * `"dependencies"`: 生产环境依赖。
  * `"devDependencies"`: 开发环境依赖。

### 6\. 版本管理：语义化版本 (SemVer)

npm 使用语义化版本来管理包的版本。版本号格式为 `主版本号.次版本号.修订号` (`MAJOR.MINOR.PATCH`)。

  * `MAJOR`: 当你做了不兼容的 API 修改。
  * `MINOR`: 当你做了向下兼容的功能性新增。
  * `PATCH`: 当你做了向下兼容的问题修正。

在 `package.json` 中，你经常会看到版本号前面有 `^` 或 `~`：

  * `^` (Caret): 锁定主版本号，允许次版本号和修订号更新。例如 `^4.18.2` 匹配 `>=4.18.2` 且 `<5.0.0` 的所有版本。这是 `npm install <package>` 的默认行为。
  * `~` (Tilde): 锁定主版本号和次版本号，只允许修订号更新。例如 `~4.18.2` 匹配 `>=4.18.2` 且 `<4.19.0` 的所有版本。

### 7\. 进阶命令

#### `npm outdated`

检查哪些包已经过时了，可以更新。

```bash
npm outdated
```

它会列出当前版本、期望版本和最新版本，非常方便。

#### `npm ci`

这个命令用于持续集成 (Continuous Integration, CI) 环境，比如在 Jenkins 或 GitHub Actions 中。

```bash
npm ci
```

它和 `npm install` 的区别：

1.  **严格**: 它完全根据 `package-lock.json` 来安装，如果 `package.json` 和 `package-lock.json` 不一致，它会报错退出。
2.  **快速**: 它会先删除现有的 `node_modules`，然后进行一次全新的、干净的安装，通常比 `npm install` 更快。
3.  **确定性**: 保证了在任何机器上安装的依赖都是完全一致的。

**最佳实践**: 在开发时使用 `npm install`，在自动化构建和部署时使用 `npm ci`。

#### `npm audit`

扫描你的项目依赖，查找已知的安全漏洞。

```bash
npm audit
```

如果发现漏洞，它会提供报告，并可能提供修复命令：

```bash
npm audit fix
```

#### `npm view`

在不安装的情况下，查看一个包的详细信息。

  * **别名**: `npm v`

<!-- end list -->

```bash
# 查看 React 的所有版本
npm view react versions

# 查看 Express 的最新版本信息
npm view express
```

#### `npx`

一个非常有用的工具，它允许你**执行**一个 npm 包的命令，而不需要全局安装它。

**场景**: 假设你想用 `create-react-app` 创建一个新的 React 项目。

  * **旧方式 (不推荐)**: `npm install -g create-react-app`，然后 `create-react-app my-app`。这会把 `create-react-app` 全局安装在你的系统里，可能很快就过时了。
  * **新方式 (推荐)**:
    ```bash
    npx create-react-app my-app
    ```
    `npx` 会临时下载最新版的 `create-react-app`，运行它，然后在命令结束后清理掉，不会污染你的全局环境。

### 8\. 最佳实践和技巧

1.  **始终提交 `package-lock.json`**: 确保团队协作和部署的一致性。
2.  **使用 `.npmrc` 文件**: 你可以在项目根目录或用户主目录下创建一个 `.npmrc` 文件来配置 npm 的行为，比如设置私有仓库地址：`registry=https://registry.npm.taobao.org` (如果你在中国，这可以加速下载)。
3.  **优先使用 `npx`**: 对于一次性的脚手架工具或不常用的命令，使用 `npx` 而不是全局安装。
4.  **定期运行 `npm outdated` 和 `npm audit`**: 保持你的依赖更新并关注安全问题。
5.  **理解 `dependencies` 和 `devDependencies` 的区别**: 将包正确地归类，可以减小生产环境安装包的体积。

-----

## npm 相关问题解决教程

### 1. 前端启动问题

#### 问题现象
运行 `npm run dev` 后，虽然显示服务器启动成功：
```
VITE v4.5.14  ready in 123 ms
➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

但访问 `http://localhost:3000` 时出现：
```
ERR_EMPTY_RESPONSE
127.0.0.1 未发送任何数据
```

#### 解决方案

##### 临时解决方案
```bash
npm run dev -- --host 0.0.0.0
```

##### 永久解决方案1：修改 package.json（推荐）
```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "start": "vite --host 0.0.0.0",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  }
}
```

##### 永久解决方案2：修改 vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',  // 添加这行
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

##### 永久解决方案3：使用环境变量
创建 `frontend/.env` 文件：
```bash
VITE_HOST=0.0.0.0
VITE_PORT=3000
```

然后在 `vite.config.ts` 中使用：
```typescript
export default defineConfig({
  // ... 其他配置
  server: {
    host: process.env.VITE_HOST || '0.0.0.0',
    port: Number(process.env.VITE_PORT) || 3000,
    // ... 其他配置
  },
})
```

### 2. npm 脚本命令详解

#### 内置脚本 vs 自定义脚本

##### 内置脚本（不需要 `run`）
```bash
npm start      # 启动应用
npm test       # 运行测试
npm stop       # 停止应用
npm restart    # 重启应用
npm install    # 安装依赖
npm uninstall  # 卸载依赖
npm update     # 更新依赖
npm publish    # 发布包
npm version    # 版本管理
npm pack       # 打包
```

##### 自定义脚本（必须使用 `run`）
```bash
npm run dev    # 开发模式
npm run build  # 构建生产版本
npm run lint   # 代码检查
npm run preview # 预览构建结果
```

#### 为什么 `npm start` 不需要 `run`？

1. **历史原因**：`start` 和 `test` 是最常用的命令，npm 从早期就支持直接调用
2. **简化常用操作**：启动和测试是最频繁的操作，简化输入提高效率
3. **标准化约定**：所有 npm 包都遵循这个约定

#### 实际验证
```bash
# 这些命令完全等效
npm start === npm run start
npm test === npm run test

# 但是 npm 允许省略 run（仅限内置脚本）
npm start  # ✅ 推荐写法
npm test   # ✅ 推荐写法
```

### 3. 常用 npm 脚本配置

#### 基础配置
```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "start": "vite --host 0.0.0.0",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  }
}
```

#### 进阶配置
```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "start": "npm run dev",
    "build": "tsc && vite build",
    "build:prod": "NODE_ENV=production npm run build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "test": "vitest",
    "test:watch": "vitest --watch",
    "clean": "rm -rf dist node_modules/.vite",
    "reinstall": "rm -rf node_modules package-lock.json && npm install"
  }
}
```

### 4. 常见问题排查

#### 端口占用问题
```bash
# 检查端口占用
lsof -i :3000
netstat -tlnp | grep :3000

# 杀死占用端口的进程
kill -9 <PID>
```

#### 清除缓存
```bash
# 清除 npm 缓存
npm cache clean --force

# 清除 Vite 缓存
rm -rf node_modules/.vite

# 完全重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 网络问题
```bash
# 测试本地连接
curl -I http://localhost:3000
curl -I http://127.0.0.1:3000
curl -I http://0.0.0.0:3000
```

### 5. 脚本最佳实践

#### 脚本命名约定
```json
{
  "scripts": {
    "start": "启动应用（通常是生产环境）",
    "dev": "开发模式启动",
    "build": "构建生产版本",
    "build:dev": "构建开发版本",
    "build:prod": "构建生产版本",
    "test": "运行测试",
    "test:watch": "监听模式运行测试",
    "lint": "代码检查",
    "lint:fix": "代码检查并自动修复",
    "preview": "预览构建结果",
    "clean": "清理构建文件"
  }
}
```

#### 参数传递
```bash
# 向脚本传递参数
npm run dev -- --port 3001
npm run build -- --mode production

# 在 package.json 中使用参数
"dev": "vite --host 0.0.0.0 --port 3000"
```

### 6. 问题解决总结

- **问题核心**：Vite 默认只绑定 localhost，需要添加 `--host 0.0.0.0`
- **推荐方案**：直接在 package.json 中配置参数
- **npm 命令**：内置脚本不需要 `run`，自定义脚本需要 `run`
- **最佳实践**：使用标准的脚本命名约定，方便团队协作

-----


