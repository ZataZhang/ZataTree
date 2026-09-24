#!/usr/bin/env python3
"""生成「分类=书」细化的全量迁移映射表 tasks/category-migration.md。

本脚本只读 content/post，不改动任何文件。真正迁移由后续命令按这里的
RULES / OVERRIDES 落地（git mv 目录 + 重写 front matter categories）。
文章 permalink 是 /p/:slug/，URL 只由 slug 决定 —— 迁移零链接变更。

映射完整性有硬校验：任何文章既不在 OVERRIDES 也不在 RULES 则报错退出；
写了却没命中任何文章的规则键也会告警，防止路径打错字静默失效。

书名均为占位名，整体改名不影响映射。60 篇/本上限（2026-09-24 定）：
当前最大一本 34 篇，无超限。

用法：
    python3 scripts/category_migration_map.py             # 写 tasks/category-migration.md
    python3 scripts/category_migration_map.py --stdout    # 只打印不写文件
"""
import argparse
import os
import re
import sys
from collections import defaultdict

ROOT = "content/post"
OUT = "tasks/category-migration.md"

# ---------------------------------------------------------------- 书单（展示顺序）
BOOK_ORDER = [
    "Agent 工程", "RAG 与 LangChain", "深度学习", "编程语言", "Web 开发",
    "数据科学", "构建与打包", "开发工具链", "设计", "工程实践",
    "运维与服务器", "项目实战", "软件试用", "效率与文档", "通识与生活",
    "Vibe Coding", "面试八股", "阅读笔记", "科技月报",
]

BOOK_SOURCES = {
    "Agent 工程": "Agent 的工程实战+Orchestration+散篇；Knowledge 的 Agent 介绍/解码/提示词；DeepLearning/agent 的 n8n、nl2sql、openclaw",
    "RAG 与 LangChain": "Agent 的 LangChain 9 篇 + RAG 4 篇 + RAG 全景/RAGFlow/GraphRAG；向量数据库",
    "深度学习": "DeepLearning 的 models/NLP/frame；Knowledge 的 JAX、字典学习、算子、vllm、模型对比、openbayes",
    "编程语言": "Grammar 的 python/PyQt/Matlab；Library 的 Python 库教程（pickle、pytest、PyYAML 等）；SQLAlchemy/Alembic",
    "Web 开发": "Library 的 FastAPI/Flask/React/flutter；Knowledge 的 Jinja、Celery、streamlit、gradio、异步 API；Refine",
    "数据科学": "Library 的 transformers/torch/pandas/matplotlib；Python_Lib 的 numpy/scipy/sklearn；onnx",
    "构建与打包": "Platforms_Tools 的 PyInstaller/PyStand/pipx/uv/packageTools；setuptools、poetry、conda、打包 exe",
    "开发工具链": "Platforms_Tools 的 Docker/dev_tools/CLI；git&github、VScode、Blender、copier",
    "设计": "Design 全部（架构/类图/用例图/数据流图/原型图/作图）；Library/优秀图表学习；项目目录规范",
    "工程实践": "Engineering 全部（可观测性/软件工程/DevOps/平台架构）；.env 安全、代码写作心得、模板规范",
    "运维与服务器": "服务器运维 11 篇、S3、Linux 4 篇、1panel/Coolify/rustdesk/Server Probe/clash、腾讯云/SSH/Nginx、PostgreSQL/redis/备份",
    "项目实战": "crawler、hugo 建站 7 篇、单片机、Dify、软件自动更新、微信小程序",
    "软件试用": "SoftTrial 17 + SoftUseExp 13（默认决策：独立成书）",
    "效率与文档": "markdown、word 技巧、windows/macos、overleaf、文档颜值、文档结构化、categories 概念",
    "通识与生活": "百科 6 篇、英语、上海地理、徒步、自学方法、尬聊、创业、菜谱、生活量化",
    "Vibe Coding": "AI-Frontend 7 篇（含 ai-design-research 4 篇）",
    "面试八股": "深度学习八股 5 篇 + LangChain 八股（默认决策：独立成书）",
    "阅读笔记": "《大语言模型》读书笔记、瑞金拉曼血糖论文、近红外光谱知识点",
    "科技月报": "科技月报 2025/2026、每日资讯、技术热点追踪（专栏形态，按时间排，不排书序）",
}

# ---------------------------------------------------------------- 按原分类/tag 的整组规则
# 仅收「该 tag 下所有文章去向一致」的 tag；去向分裂的 tag 走下面的 OVERRIDES。
RULES = {
    ("Agent", "Agent 工程实战"): "Agent 工程",
    ("Agent", "Agent Orchestration"): "Agent 工程",
    ("Agent", "LangChain"): "RAG 与 LangChain",
    ("Agent", "RAG"): "RAG 与 LangChain",
    ("DeepLearning", "models_and_strategies"): "深度学习",
    ("DeepLearning", "NLP"): "深度学习",
    ("DeepLearning", "frame"): "深度学习",
    ("Design", "软件架构设计"): "设计",
    ("Design", "值得学习的图"): "设计",
    ("Engineering", "可观测性"): "工程实践",
    ("Engineering", "DevOps"): "工程实践",
    ("Grammar", "python"): "编程语言",
    ("Grammar", "PyQt"): "编程语言",
    ("Knowledge", "面试八股"): "面试八股",
    ("Knowledge", "科技月报：机器人又抢饭碗啦"): "科技月报",
    ("Knowledge", "encyclopedic"): "通识与生活",
    ("Knowledge", "English"): "通识与生活",
    ("Knowledge", "Linux"): "运维与服务器",
    ("Knowledge", "markdown"): "效率与文档",
    ("Knowledge", "word技巧"): "效率与文档",
    ("Library", "FastAPI"): "Web 开发",
    ("Library", "Flask"): "Web 开发",
    ("Library", "transformers"): "数据科学",
    ("Platforms_Tools", "Docker"): "开发工具链",
    ("Platforms_Tools", "dev_tools"): "开发工具链",
    ("Platforms_Tools", "CLI"): "开发工具链",
    ("Platforms_Tools", "PyInstaller"): "构建与打包",
    ("Platforms_Tools", "Server Operations and Maintenance-服务器运维"): "运维与服务器",
    ("Project_Application", "crawler"): "项目实战",
    ("Project_Application", "hugo"): "项目实战",
    ("Project_Application", "git&github"): "开发工具链",
    ("Project_Application", "SoftTrial"): "软件试用",
    ("Project_Application", "SoftUseExp"): "软件试用",
    ("Vibe-Coding", "AI-Frontend"): "Vibe Coding",
}

# ---------------------------------------------------------------- 逐篇归属（judgment calls）
OVERRIDES = {
    # --- Knowledge/others 垃圾抽屉，40 篇逐篇归位 ---
    "Knowledge/others/代码写作心得-使用教程": "工程实践",
    "Knowledge/others/怎么保存.env文件到github公开的仓库": "工程实践",
    "Knowledge/others/技术追踪/技术热点追踪": "科技月报",
    "Knowledge/others/技术追踪/文档结构化实战": "效率与文档",
    "Knowledge/others/徒步知识点": "通识与生活",
    "Knowledge/others/什么是算子？": "深度学习",
    "Knowledge/others/近红外光谱的知识点": "阅读笔记",
    "Knowledge/others/如何自学一个领域？": "通识与生活",
    "Knowledge/others/如何和别人尬聊，打破僵局？": "通识与生活",
    "Knowledge/others/对比了几种大模型在相同任务下的表现": "深度学习",
    "Knowledge/others/一个软件项目的文件目录应该怎么定义": "设计",
    "Knowledge/others/全量解码与增量解码：原理、区别以及应用": "Agent 工程",
    "Knowledge/others/1panel使用": "运维与服务器",
    "Knowledge/others/AI agent介绍：基于大模型的人工智能代理": "Agent 工程",
    "Knowledge/others/Building asynchronous APIs for handling long-term tasks and dynamic resources": "Web 开发",
    "Knowledge/others/categories和tags的区别": "效率与文档",
    "Knowledge/others/Celery": "Web 开发",
    "Knowledge/others/修改clash中的配置信息": "运维与服务器",
    "Knowledge/others/conda使用相关": "构建与打包",
    "Knowledge/others/cookbook": "通识与生活",
    "Knowledge/others/Coolify": "运维与服务器",
    "Knowledge/others/copier-using": "开发工具链",
    "Knowledge/others/字典学习（Dictionary Learning）": "深度学习",
    "Knowledge/others/JAX": "深度学习",
    "Knowledge/others/Jinja是什么？可以用在做什么？": "Web 开发",
    "Knowledge/others/相同LLM不同提示词的对比": "Agent 工程",
    "Knowledge/others/macos使用经验": "效率与文档",
    "Knowledge/others/openbayes算力平台使用教程": "深度学习",
    "Knowledge/others/在overleaf中为什么两个完全一样的代码一个不能显示图片": "效率与文档",
    "Knowledge/others/包管理工具poetry使用教程": "构建与打包",
    "Knowledge/others/如何提成所写文档和ppt的颜值": "效率与文档",
    "Knowledge/others/python的命名规范": "编程语言",
    "Knowledge/others/python中将函数设置为定时任务": "编程语言",
    "Knowledge/others/rustdesk安装使用": "运维与服务器",
    "Knowledge/others/Server Probe": "运维与服务器",
    "Knowledge/others/start-a-business": "通识与生活",
    "Knowledge/others/streamlit使用教程": "Web 开发",
    "Knowledge/others/Useful but not attempted": "工程实践",
    "Knowledge/others/vllm实战教程": "深度学习",
    "Knowledge/others/给Zata的公司取一个名字": "通识与生活",
    # --- Library/Python_Lib 12 篇逐篇拆到语言/Web/数据科学 ---
    "Library/Python_Lib/fastapi使用": "Web 开发",
    "Library/Python_Lib/gradio": "Web 开发",
    "Library/Python_Lib/numpy使用教程": "数据科学",
    "Library/Python_Lib/scipy": "数据科学",
    "Library/Python_Lib/sklearn使用教程": "数据科学",
    "Library/Python_Lib/pickle": "编程语言",
    "Library/Python_Lib/pytest": "编程语言",
    "Library/Python_Lib/python开发环境配置指南": "编程语言",
    "Library/Python_Lib/PyYAML": "编程语言",
    "Library/Python_Lib/tableprint使用教程": "编程语言",
    "Library/Python_Lib/toml_usage使用教程": "编程语言",
    "Library/Python_Lib/Typer和Rich入门教程": "编程语言",
    # --- 其他去向分裂的 tag ---
    "DeepLearning/agent/n8n": "Agent 工程",
    "DeepLearning/agent/nl2sql": "Agent 工程",
    "DeepLearning/agent/openclaw": "Agent 工程",
    "DeepLearning/agent/vector-database": "RAG 与 LangChain",
    "Library/smallLibrary/onnx使用教程": "数据科学",
    "Library/smallLibrary/pydantic使用教程": "编程语言",
    "Grammar/general/生活中的收获量化方法": "通识与生活",
    "Grammar/general/通用模板规范GeneralTemplateSpecifications": "工程实践",
    "Project_Application/SQL/SQLAlchemy简单入门": "编程语言",
    "Project_Application/SQL/Alembic": "编程语言",
    "Project_Application/SQL/PostgreSQL": "运维与服务器",
    "Project_Application/SQL/redis": "运维与服务器",
    "Project_Application/SQL/数据库备份实战": "运维与服务器",
    "Project_Application/PythonGUI/PythonGUI-软件自动更新": "项目实战",
    "Project_Application/PythonGUI/PythonGUI-打包成exe": "构建与打包",
    # --- 单篇 tag 目录（index.md 直接躺在分类或 tag 目录下）---
    "Agent/Agent流式协议/AG-UI：当Agent学会了和前端说话": "Agent 工程",
    "Agent/Agent开发中遇到的问题/ai返回数据的格式不稳定，存在解析错误的问题": "Agent 工程",
    "Agent/ComputerUse/Cua 框架详解：给任何 Agent 一台可操控的电脑": "Agent 工程",
    "Agent/GraphRAG开源项目全景：从微软GraphRAG到LightRAG": "RAG 与 LangChain",
    "Agent/RAG技术全景：从入门到进阶": "RAG 与 LangChain",
    "Agent/RAGFlow深度解析：为什么它是最值得关注的RAG开源项目": "RAG 与 LangChain",
    "Book/读书笔记/大语言模型-赵鑫": "阅读笔记",
    "Design/结构图/类图": "设计",
    "Design/行为图/用例图": "设计",
    "Design/功能图/数据流图": "设计",
    "Design/原型图/使用ai工具绘制原型图html并导入figma": "设计",
    "Engineering/软件工程/软件项目开发流程": "工程实践",
    "Engineering/platform-architecture/ai-platform-architecture": "工程实践",
    "Grammar/Matlab/Matlab-基本语法": "编程语言",
    "Knowledge/geographic/shanghai-geographic": "通识与生活",
    "Knowledge/windows/关闭win11更新": "效率与文档",
    "Knowledge/news/资讯和思考": "科技月报",
    "Library/优秀图表学习/分类图": "设计",
    "Library/pyserial/pyserial-Python 中最常用的串口通信库快速入门": "编程语言",
    "Library/setuptools/setuptools-打包python项目为egg": "构建与打包",
    "Library/matplotlib/matplotlib使用教程_Zata_v0.0.0": "数据科学",
    "Library/pandas/pandas使用教程": "数据科学",
    "Library/torch/torch使用教程_Zata_v0.0.0": "数据科学",
    "Library/flutter/flutter_tutorial": "Web 开发",
    "Library/React/React框架使用教程": "Web 开发",
    "PaperReading/RuijinHospitalandNearviewTechnologyLaunchRamanSpectroscopyforNon-InvasiveBloodGlucoseMonitoring_NatureMetabolism": "阅读笔记",
    "Platforms_Tools/Blender/blender-complete-guide": "开发工具链",
    "Platforms_Tools/S3/S3 兼容存储踩坑记：boto3 新默认校验和撞上 NotImplemented": "运维与服务器",
    "Platforms_Tools/pipx/pipx使用教程": "构建与打包",
    "Platforms_Tools/PyStand/PyStand-简易教程": "构建与打包",
    "Platforms_Tools/uv/包管理工具uv使用教程": "构建与打包",
    "Platforms_Tools/packageTools/npm使用教程": "构建与打包",
    "Platforms_Tools/refine-meta-framework": "Web 开发",
    "Project_Application/Dify": "项目实战",
    "Project_Application/nginx使用": "运维与服务器",
    "Project_Application/腾讯云修改root登录": "运维与服务器",
    "Project_Application/单片机/野火F103-MiNI使用教程": "项目实战",
    "Project_Application/wechatapplet/微信小程序使用教程": "项目实战",
    "Project_Application/SSH/SSH常用命令": "运维与服务器",
    "Project_Application/VScode/VScode安装和配置": "开发工具链",
}

# ---------------------------------------------------------------- 待拍板条目（⚠️，编号见生成文档）
FLAGS = {
    "DeepLearning/agent/n8n": "仅一行 docker 安装命令，建议并入相关长文或删除",
    "DeepLearning/agent/nl2sql": "24 词占位文，建议补写、并入或删除",
    "DeepLearning/agent/openclaw": "从 DeepLearning/agent 迁入 Agent 工程线",
    "DeepLearning/agent/vector-database": "归 RAG 与 LangChain（向量库是 RAG 基建）；也可留深度学习",
    "Knowledge/others/什么是算子？": "17 词短文，建议合并或补写",
    "Knowledge/others/openbayes算力平台使用教程": "19 词短文，建议合并或补写",
    "Knowledge/others/近红外光谱的知识点": "放阅读笔记（与瑞金拉曼血糖论文同主题）；也可去通识与生活",
    "Knowledge/others/cookbook": "实际是烧牛肉菜谱，归通识与生活",
    "Knowledge/others/对比了几种大模型在相同任务下的表现": "模型评测归深度学习；也可去 Agent 工程",
    "Knowledge/others/相同LLM不同提示词的对比": "提示词对比归 Agent 工程；也可去深度学习",
    "Knowledge/others/一个软件项目的文件目录应该怎么定义": "与《一个标准的软件项目结构》成对，归设计；也可去工程实践",
    "Knowledge/others/categories和tags的区别": "概念科普归效率与文档；也可去通识与生活",
    "Knowledge/others/Useful but not attempted": "技术问题清单，更像待写选题池，建议改造或合并",
    "Platforms_Tools/Blender/blender-complete-guide": "创作工具归开发工具链；也可去软件试用",
    "Platforms_Tools/dev_tools/ai-frontend-e2e": "与 Playwright 系列聚堆；其 front matter 现标 Vibe-Coding，也可去那边",
    "Project_Application/SoftUseExp/Tavily": "Agent 搜索 API，随软件试用；也可去 Agent 工程",
    "Project_Application/SQL/SQLAlchemy简单入门": "数据库 5 篇拆了两处（这对去编程语言，PostgreSQL/redis/备份去运维）；想聚一起可整体挪",
    "Project_Application/SQL/Alembic": "同上，与 SQLAlchemy 结伴",
}

# ---------------------------------------------------------------- 迁移时要顺手修的数据问题（front matter 校验发现）
INTEGRITY = [
    "front matter 分类 ≠ 目录（Hugo 只认 front matter，迁移时统一以映射表为准）:",
    "  - Platforms_Tools/dev_tools/playwright-profile → front matter 写的是 Library",
    "  - Platforms_Tools/dev_tools/ai-frontend-e2e → front matter 写的是 Vibe-Coding",
    "  - Platforms_Tools/refine-meta-framework → front matter 写的是 Library",
    "  - Project_Application/SQL/SQLAlchemy简单入门 → front matter 写的是 Library",
    "  - Project_Application/nginx使用 → front matter 写的是 Platforms_Tools",
    "0 字节空文件（无标题无分类）: Design/行为图/用例图、Platforms_Tools/Docker/docker-ubuntu容器中安装miniconda问题合集",
]
EMPTY_DIRS = [
    "content/post/Design/产品设计/（0 篇）",
    "content/post/Knowledge/文档结构化/（0 篇）",
    "content/post/Platforms_Tools/just-worktree-clauded-alias-fix/（0 篇）",
    "content/post/images/（只有一个 README，不是分类）",
]

SHORT_THRESHOLD = 400  # 正文字数低于此值进「短文合并候选」


def read_article(rel):
    f = os.path.join(ROOT, rel, "index.md")
    try:
        text = open(f, encoding="utf-8").read()
    except OSError:
        return "", 0
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    title = m.group(1).strip().strip('"').strip("'") if m else ""
    lines = text.splitlines()
    delims, body_start = 0, len(lines)
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            delims += 1
            if delims == 2:
                body_start = i + 1
                break
    body = "\n".join(lines[body_start:])
    return title, len(re.sub(r"\s", "", body))


def collect():
    rels = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "index.md" in filenames:
            rels.append(os.path.relpath(dirpath, ROOT))
    return sorted(rels)


def esc(s):
    return s.replace("|", "\\|").replace("\t", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true", help="只打印不写文件")
    opts = ap.parse_args()

    rels = collect()
    rows = defaultdict(list)   # book -> [(rel, title, chars)]
    unmapped, used_overrides, used_rules = [], set(), set()
    for rel in rels:
        book = OVERRIDES.get(rel)
        if book:
            used_overrides.add(rel)
        else:
            parts = rel.split(os.sep)
            key = (parts[0], parts[1] if len(parts) >= 3 else None)
            book = RULES.get(key)
            if book:
                used_rules.add(key)
        if not book:
            unmapped.append(rel)
            continue
        title, chars = read_article(rel)
        rows[book].append((rel, title, chars))

    dead_overrides = set(OVERRIDES) - used_overrides
    dead_rules = set(RULES) - used_rules
    if unmapped or dead_overrides or dead_rules:
        for r in unmapped:
            print(f"未映射文章: {r}", file=sys.stderr)
        for k in sorted(dead_overrides):
            print(f"OVERRIDES 键未命中任何文章（检查是否打错字）: {k}", file=sys.stderr)
        for k in sorted(dead_rules, key=repr):
            print(f"RULES 键未命中任何文章: {k}", file=sys.stderr)
        sys.exit(1)

    defined = set(OVERRIDES.values()) | set(RULES.values())
    unknown = defined - set(BOOK_ORDER)
    if unknown:
        print(f"书名不在 BOOK_ORDER 里: {unknown}", file=sys.stderr)
        sys.exit(1)

    total = sum(len(v) for v in rows.values())
    over60 = [b for b in BOOK_ORDER if len(rows.get(b, [])) > 60]

    out = []
    w = out.append
    w("# 分类细化 · 全量映射表（待确认）")
    w("")
    w("> 生成于 2026-09-24 · `scripts/category_migration_map.py`（映射规则的唯一事实源，确认后迁移命令按它落地）")
    w("> 迁移 = git mv 目录 + 重写 front matter `categories`。permalink 是 `/p/:slug/`，由 slug 决定 —— 全程零链接变更。")
    w("> 约束：60 篇/本上限（最大一本 "
      + str(max(len(v) for v in rows.values())) + " 篇，无超限）。书名均为占位名，可整体改。")
    w("> ⚠️ = 待你拍板的条目，明细见「待拍板清单」。")
    w("")
    w("## 总览")
    w("")
    w("| # | 书 | 篇数 | 主要来源 |")
    w("|---|---|---|---|")
    for i, b in enumerate(BOOK_ORDER, 1):
        w(f"| {i} | {b} | {len(rows.get(b, []))} | {BOOK_SOURCES[b]} |")
    w(f"| | **合计** | **{total}** | |")
    w("")

    w("## 映射明细")
    w("")
    for i, b in enumerate(BOOK_ORDER, 1):
        items = sorted(rows.get(b, []))
        w(f"### {i}. {b} · {len(items)} 篇")
        w("")
        w("| 标题 | 旧位置 | 备注 |")
        w("|---|---|---|")
        for rel, title, _ in items:
            t = esc(title) if title else "_(无标题)_"
            note = f"⚠️#{list(FLAGS).index(rel) + 1}" if rel in FLAGS else ""
            w(f"| {t} | `{esc(rel)}` | {note} |")
        w("")

    w("## 待拍板清单")
    w("")
    for i, (rel, reason) in enumerate(FLAGS.items(), 1):
        w(f"{i}. `{rel}` — {reason}")
    w("")
    w("另外两处组级取舍：SoftTrial/SoftUseExp 30 篇里 homebrew、nvm、scoop、tmux、cursor 这类纯开发工具试用文，")
    w("如果想严格区分「教程」和「试用」，可挑几篇挪去开发工具链；构建与打包（10 篇）并回开发工具链（27 篇）也随时可以，60 上限内空间足够。")
    w("")

    w("## 短文合并候选（正文 < 400 字）")
    w("")
    w("没有一本超 60 篇，不需要为上限而合并；但下列短文/占位文影响成书后的目录质感，建议合并进同书长文、补写或删除。")
    w("")
    w("| 标题 | 旧位置 | 字数 | 建议 |")
    w("|---|---|---|---|")
    shorts = [(rel, title, c) for b in BOOK_ORDER for (rel, title, c) in rows.get(b, [])
              if c < SHORT_THRESHOLD]
    for rel, title, c in sorted(shorts, key=lambda x: x[2]):
        t = esc(title) if title else "_(无标题)_"
        if c == 0:
            advice = "空文件：补写或删除"
        elif c < 150:
            advice = "极短：并入同书长文或补写"
        else:
            advice = "偏短：可考虑合并"
        w(f"| {t} | `{esc(rel)}` | {c} | {advice} |")
    w("")

    w("## 迁移时顺手修的数据问题")
    w("")
    for line in INTEGRITY:
        w(line)
    w("")
    w("空目录清理：")
    w("")
    for d in EMPTY_DIRS:
        w(f"- {d}")
    w("")
    w("## 后续步骤")
    w("")
    w("1. 过一遍本表：改书名、处理 ⚠️ 条目和合并候选（直接改 md 或口头说，我同步进脚本规则）")
    w("2. `zata.py create-category` 建 19 个新分类（含封面图），旧分类元数据保留到验证后再删")
    w("3. 迁移命令（参照 `tools/merge_categories.py` 的 dry-run/--apply 惯例）：git mv 目录 + 重写 categories，顺手修上面 5 处 front matter、处理 2 个空文件、删空目录")
    w("4. `hugo server` 全站点验，之后再做书视图前端（书页目录 + 篇尾续读）")
    w("")

    doc = "\n".join(out)
    if opts.stdout:
        print(doc)
    else:
        open(OUT, "w", encoding="utf-8").write(doc)
    print(f"共 {total} 篇，{len(BOOK_ORDER)} 本" + ("；超 60 篇的书: " + ", ".join(over60) if over60 else "；全部在 60 篇上限内"), file=sys.stderr)
    for b in BOOK_ORDER:
        print(f"{b}: {len(rows.get(b, []))}", file=sys.stderr)


if __name__ == "__main__":
    main()
