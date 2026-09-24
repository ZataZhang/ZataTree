---
title: everything-claude-code
description: ""
date: 2026-03-17T10:53:29+08:00
image: images/index/index.png
categories:
    - Project_Application
tags:
    - SoftTrial
---



# 安装和配置




# 注意事项
## 概念
更准确地说，它是把一整套 AI 开发工作流打包成仓库和插件，主要包括：

  - agents：子代理角色，比如规划、架构、代码审查、安全审查
  - skills：可复用工作流，比如 TDD、持续学习、搜索优先、安全检查、前后端模式
  - commands：斜杠命令，比如 /plan、/verify、/code-review、/multi-execute
  - hooks / rules / mcp-configs：自动化钩子、规范规则、MCP 外部工具接入

  它的核心目标是把 AI 编码助手从“会聊天的工具”变成“更像工程团队的系统”：更会规划、记忆上下文、做验证循环、自动审查、安全扫
  描和多代理协作。

  如果你问“适合拿来干嘛”，答案是：

  - 搭一套更强的 Claude Code/Codex 开发环境
  - 复用现成的 agent/skill/rule
  - 给团队统一 AI 编码规范和自动化流程
  如果你问“它是不是一个能直接运行的产品”，答案是否。它更像一个 AI coding workflow toolkit，不是 SaaS/后端/前端业务项目。

  补充一点：截至 2026-03-17，GitHub 页面显示它已经定位成 “AI agent harness performance optimization system”，英文 README
  写的是 21 agents / 102 skills / 52 commands；我看到中文 README 里还是较早的 13 / 43 / 31，推测中文文档有些滞后。

  来源：
  GitHub 仓库 (https://github.com/affaan-m/everything-claude-code)
  README.md (https://github.com/affaan-m/everything-claude-code/blob/main/README.md)
  package.json (https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/package.json)




