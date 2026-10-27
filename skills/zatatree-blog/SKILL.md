---
name: zatatree-blog
description: "[Updated 2026-09-22] Write or update posts for the ZataTree Hugo blog (~/code/ZataTree, www.zata.cc) — merge-vs-new judgment, content/post/{category}/{tag}/{title} structure, frontmatter, SVG-first cover generation, screenshot/asset handling, narrative blog writing style, and local validation when hugo is unavailable. Triggers on: 写博客, 更新博客, 记录到博客, ZataTree, blog post, write blog, hugo blog."
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# ZataTree 博客写作

把一次工作会话中的问题/方案沉淀为 ZataTree 博客（Hugo + hugo-theme-stack，部署在 www.zata.cc）的文章。

## 前置：必读仓库规范

博客仓库根目录的 `AGENTS.md` 是权威规范（内容结构、frontmatter、封面决策树）。每次动笔前先读它，本 skill 只沉淀它没写的**经验**。

仓库路径：`/Users/zata/code/ZataTree`（如用户环境不同，以实际为准）。

## 第一步：合并还是新开

不要默认新开文章。先找候选：

```bash
ls content/post/<疑似分类>/          # 看同分类下有什么
rg -i -l '关键词' content/post      # 全文搜相关主题
```

判断标准：

- 找到主题高度重合的文章 → **合并进去**（新增小节，保持该文原有结构）。
- 只是同领域但问题类型不同（例如一篇讲提示词技巧、一篇讲组件库行为差异）→ **新开**。合并会互相稀释。
- 拿不准时把候选文章的标题列给用户定。

分类/标签必须已存在（`content/categories/`、`content/tags/` 下有对应目录）。不存在时用仓库的 `zata.py create-category / create-tag` 创建，不要手建目录。

## 第二步：建文章目录与素材

结构（Hugo Page Bundle）：

```text
content/post/{category}/{tag}/{title}/
├── index.md
└── images/
    └── index/
        ├── index.svg      # 封面，必须有
        └── *.png          # 正文引用的截图等
```

素材处理经验：

- **截图复用工作产物，但先过隐私关**。验证截图、报错截图从原项目目录 `cp` 进 `images/index/`，正文用相对路径 `![描述](images/index/xxx.png)` 引用。引用后必须确认文件存在（裂图是最高发问题）。
- **截图发布前必须脱敏**。工作截图常含隐私：真实域名/IP、token 与密钥、内部路径、用户名/邮箱、他人信息、未公开的业务数据。逐张检查后按情况选方案：
  - 敏感区域小 → 裁剪或打码（遮住，不要半透明模糊，马赛克可逆性差时直接实心覆盖）。
  - 敏感的是数据而非界面 → 用假数据在本地复现一遍再重截，信息量不变。
  - 报错/日志类 → 优先贴文本代码块代替截图（更可读、可搜索、零隐私风险）。
  - UI 对比类 → 可画「问题 vs 修复后」的极简 SVG 示意图替代（与封面 SVG 风格一致）。
  - 只需要界面局部 → 裁剪到最小必要区域，天然缩小隐私面。
  - 拿不准某张图是否敏感 → 问用户，不要默认放行。
- **封面 SVG-first**：没有现成封面时不要搜网络图，生成 1200×630 的内联 SVG（无外部资源、无远程字体、用 `sans-serif`/`monospace` 泛型字体、< 20KB）。配色用主题色 `#5b87bf` 及蓝/紫/青系。内容元素：文章标题 + 1~2 个 tag 词 + 一个极简示意图（能画「问题 vs 修复后」的对比最好）。frontmatter 指向它：`image: images/index/index.svg`。
- frontmatter 模板见仓库 AGENTS.md；`date` 用 `date "+%Y-%m-%dT%H:%M:%S+08:00"` 取当前时间，别照抄模板里的示例日期。

## 第三步：写法——叙事博客，不是工程报告

这是本 skill 的核心。ZataTree 的文章是**叙事风格**（参考 `content/post/Vibe-Coding/AI-Frontend/AI 前端调试技巧：把被遮挡翻译成尺寸约束/index.md`），不要把实现报告直接贴上去。

结构范式：

1. **钩子开场**：从现象切入，写出第一直觉（通常是错的猜测），给读者代入感。例：「第一反应：文案写错了……打开代码一看，不对劲。」
   - **device 防套路**：「第一反应是……」「讨论/群里有人说」属于转述式钩子，最容易连续多篇长成模板脸。动笔前回想上一两篇用了哪种；换着来——从物件切入（一段代码、一条报错、一个反常识数字），或从时刻/画面切入。「有人说」只在引语本身有信息量时用，且必须真实发生。
2. **排查过程按真实认知顺序讲**：先猜什么 → 为什么排除 → 什么线索指向真相。关键证据贴出来（类型定义、源码片段）。
3. **技术差异拟人化/对比化**：两个库、两种方案的行为差异，用「贴心 vs 实诚」这类性格对比讲，比平铺直叙好读。
4. **修复给前后对比代码**：`// 修复前` / `// 修复后` 成对出现，能复用现有机制（翻译 key、已有 helper）就明确说出来。
5. **同类清扫单独一节**：这类 bug 的模式是什么、扫了多少处、哪些不用改（说明判断依据，防误伤）。
6. **验证说清楚层级**：静态检查 + 真实入口截图，别只写「已修复」。
7. **结尾写「几点收获」**：每条经验带一句解释，像随笔不像清单。

禁忌（工程报告腔）：

- 「根因/修改/验证」三段式小标题堆列表
- 罗列改了哪些文件多少处作为正文主体（放一节即可）
- 没有开场现象、没有错误猜测的直接陈述

语言：中文，技术术语保留原文。代码注释跟随目标项目语言习惯。

## 第四步：验证

本机可能**没有 hugo**（仓库里的 `hugo.exe` 是 Windows 二进制）。先探测：

```bash
command -v hugo && hugo version
```

- 有 hugo → `hugo server -D` 或 `hugo --gc --minify` 构建验证。
- 没有 hugo → 做替代校验，并向用户说明没跑完整构建：

```bash
# frontmatter 可解析 + 正文图片引用全部存在
python3 - <<'EOF'
import re, pathlib, yaml
text = pathlib.Path("index.md").read_text(encoding="utf-8")
fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))
print("frontmatter OK:", fm["title"])
for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
    print(img, "->", "OK" if pathlib.Path(img).exists() else "MISSING")
EOF

# SVG 封面渲染冒烟（macOS）
qlmanage -t -s 1200 -o /tmp images/index/index.svg
```

不要为验证而 `brew install hugo`（改动用户系统需先征得同意）。

## 收尾

- 不主动 `git add/commit/push`，ZataTree 的部署走 `hugo` 分支 + GitHub Actions，是否提交由用户决定。
- 提醒用户在本地 `hugo server -D` 过一眼渲染效果。
