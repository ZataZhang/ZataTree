---
title: 微信小程序使用教程——WechatMiniProgram
description: ""
date: 2025-06-08T23:37:17+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - wechatapplet
---


### 第一部分：微信小程序简介

微信小程序是一种无需下载安装即可使用的轻量级应用，通过微信平台运行。它具有开发简单、用户体验流畅、易于推广等特点，广泛应用于电商、工具、服务等领域。

#### 特点：

1.  **无需安装**：用户扫码或搜索即可使用。
2.  **跨平台**：基于微信生态，无需适配多系统。
3.  **开发简单**：使用类似 HTML、CSS、JavaScript 的技术栈。

***

### 第二部分：准备工作

在开始开发之前，你需要准备以下工具和环境：

#### 1. 注册微信小程序账号

*   前往 [微信公众平台](https://mp.weixin.qq.com/)。
*   点击“立即注册”，选择“小程序”类型。
*   填写邮箱、密码等信息，完成注册。
*   注册后会获得一个 **AppID**（小程序唯一标识），后续开发需要用到。

#### 2. 下载微信开发者工具

*   访问 [微信开发者工具下载页面](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)。
*   根据你的操作系统（Windows、Mac 或 Linux）下载稳定版工具。
*   安装完成后，用注册时绑定的微信号扫码登录。

#### 3. 技术基础

微信小程序使用以下技术：

*   **WXML**（类似 HTML）：用于结构。
*   **WXSS**（类似 CSS）：用于样式。
*   **JavaScript**：用于逻辑。
*   **JSON**：用于配置。

如果你熟悉前端开发，这些技术上手会很快。

***

### 第三部分：创建一个简单的小程序

我们将通过一个简单的 “Hello World” 示例，带你了解小程序的开发流程。

#### 1. 创建项目

*   打开微信开发者工具。
*   点击“小程序” -> “新建项目”。
*   填写以下信息：
    *   **项目目录**：选择一个空文件夹存放项目文件。
    *   **AppID**：输入你在公众平台注册时获得的 AppID（测试可用“测试号”）。
    *   **项目名称**：例如 “HelloWorld”。
    ![模版可以使用js基础模版](images/index/image.png)
*   选择“小程序·原生开发”，点击“确定”。

#### 2. 理解项目结构

创建后，项目目录如下：

    ├── pages           // 页面文件夹
    │   ├── index       // 默认首页
    │   │   ├── index.js    // 页面逻辑
    │   │   ├── index.json  // 页面配置
    │   │   ├── index.wxml  // 页面结构
    │   │   └── index.wxss  // 页面样式
    ├── app.js          // 小程序全局逻辑
    ├── app.json        // 小程序全局配置
    ├── app.wxss        // 小程序全局样式
    └── project.config.json  // 项目配置文件

#### 3. 编辑首页

我们将修改 pages/index 下的文件，显示一个简单的 “Hello World” 文本。

*   **index.wxml**（页面结构）：

```html
<view class="container">
  <text>Hello World</text>
</view>
```

*   **index.wxss**（页面样式）：

```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 36rpx;
  color: #333;
}
```

*   **index.js**（页面逻辑，暂时无需修改）：

```javascript
Page({
  data: {
    // 数据可以在此定义
  }
})
```

*   **index.json**（页面配置，可选）：

```json
{
  "navigationBarTitleText": "首页"
}
```

#### 4. 配置全局文件

*   **app.json**（全局配置）：

```json
{
  "pages": [
    "pages/index/index"  // 默认首页路径
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#fff",
    "navigationBarTitleText": "我的小程序",
    "navigationBarTextStyle": "black"
  }
}
```

#### 5. 预览效果

*   在微信开发者工具顶部，点击“预览”。
*   用手机微信扫码，即可在手机上看到 “Hello World” 显示在屏幕中央。

***

### 第四部分：添加交互功能

我们为小程序添加一个按钮，点击后显示一条消息。

#### 1. 修改 WXML

编辑 pages/index/index.wxml：

```html
<view class="container">
  <text>{{msg}}</text>
  <button bindtap="showMessage">点击我</button>
</view>
```

#### 2. 修改 JS

编辑 pages/index/index.js：

```javascript
Page({
  data: {
    msg: "Hello World"  // 初始文本
  },
  showMessage: function() {
    this.setData({
      msg: "你点击了按钮！"
    });
  }
});
```

#### 3. 修改 WXSS

编辑 pages/index/index.wxss，美化按钮：

```css
.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 36rpx;
  color: #333;
}

button {
  margin-top: 20rpx;
  background-color: #07c160;
  color: #fff;
}
```

#### 4. 测试

点击“预览”，扫码后在手机上点击按钮，文本会从 “Hello World” 变为 “你点击了按钮！”。

***

### 第五部分：发布小程序

开发完成后，你可以将其发布到微信平台供用户使用。

1.  **上传代码**：
    *   在开发者工具中，点击右上角“上传”。
    *   填写版本号（如 “1.0.0”）和备注，上传成功后可在公众平台看到。

2.  **提交审核**：
    *   登录 [微信公众平台](https://mp.weixin.qq.com/)。
    *   在“小程序管理” -> “版本管理”中，找到上传的版本，点击“提交审核”。
    *   填写相关信息（如小程序类目、功能介绍），等待微信团队审核（通常 1-7 天）。

3.  **发布上线**：
    *   审核通过后，点击“发布”，小程序即可上线，用户可通过搜索或扫码使用。

***

### 第六部分：学习资源与进阶

#### 官方资源：

*   [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
*   [组件和 API 参考](https://developers.weixin.qq.com/miniprogram/dev/reference/)

#### 进阶建议：

*   学习 **云开发**：微信提供云函数、数据库、存储等功能。
*   掌握 **自定义组件**：提高代码复用性。
*   探索 **小程序插件**：扩展功能。

***
