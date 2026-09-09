---
name: zatatree-blog
description: "[Updated 2026-09-09] Write or update posts for the ZataTree Hugo blog (www.zata.cc) — merge-vs-new judgment, content/post/{category}/{tag}/{title} structure, frontmatter, SVG-first cover generation (1200×400 strip-safe layout), screenshot/asset handling, narrative blog writing style, and local validation. Triggers on: 写博客, 更新博客, 记录到博客, ZataTree, blog post, write blog, hugo blog."
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

把一次工作会话中的问题/方案沉淀为 ZataTree 博客（Hugo + hugo-theme-stack，部署在 www.zata.cc）的文章。本 skill 位于仓库内（`.qoder/skills/zatatree-blog/`），所有路径相对仓库根目录。

## 前置：必读仓库规范

仓库根目录的 `AGENTS.md` 是权威规范（内容结构、frontmatter、封面决策树）。每次动笔前先读它，本 skill 只沉淀它没写的**经验**。

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
- frontmatter 模板见仓库 AGENTS.md；`date` 用 `date "+%Y-%m-%dT%H:%M:%S+08:00"` 取当前时间，别照抄模板里的示例日期。

## 封面 SVG：按长条展示位设计（2026-09 实测）

**先知道封面在站点上的真实展示方式**（对 www.zata.cc 用浏览器实测过）：

| 展示位 | 尺寸（桌面端实测） | 裁切方式 |
|---|---|---|
| 首页/列表大卡片 | 全宽 × **固定高** 250px，≈845×250，**约 3.4:1 长条** | `object-fit: cover` **中心裁切** |
| 移动端同一卡片 | ≈350×150，约 2.3:1 | cover 中心裁切（改裁左右） |
| 文章页头图 | 全宽、按原图比例完整显示（≤50vh） | 不裁切 |
| compact 小缩略图 | 120×120 正方形 | cover 中心裁切 |

旧规范按 1200×630（OG 比例 1.9:1）画，首页长条只会显示中间约 56% 高度，上下各裁掉 ~22%，标题和示意图经常被切掉——这就是「页面上的封面是一条细长条且构图不对」的根因。

**首选：用仓库自带的生成脚本**（2026-09 起，全部现役封面由它产出，风格统一）：

```bash
python3 tools/cover.py                                # 重刷所有引用 index.svg 的文章封面
python3 tools/cover.py content/post/<路径>/index.md   # 只重生成某一篇
```

脚本从 frontmatter 读标题/tags/分类，自动完成：1200×400 画布、标题字号与两行折行、
tag 胶囊、按分类映射的配色与图形母题（Agent→graph、Engineering→terminal、
Platforms_Tools→layers、Library→doc、Vibe-Coding→flow……）。新文章写完 frontmatter
后跑一次即可，不要手写 SVG。

**手写 SVG 时的底线规范**（脚本覆盖不了的特殊构图才手写）：

- 画布 **1200×400（3:1）**，`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400">`。**width/height 属性必须写**（只写 viewBox 时浏览器 naturalWidth=0，渲染塌陷）。
- **安全区构图**：标题、tag 词、示意图全部放在中央安全带——垂直方向 y∈[80, 320]（中间 60%），水平方向两侧各留 ≥100px 边距。背景渐变、装饰纹理可以满幅出血，但放边缘的内容默认会被裁掉。
- **视觉基调**（与 tools/cover.py 一致，保持全站封面统一）：深海军蓝底 `#0B1220` + 低透明度点阵纹理；左侧 6px 强调色竖条；标题白色 `#F8FAFC`、font-weight 700、左对齐 x=96，按长度自动降档（72→44px，过长折两行）；标题下 112×6 圆角强调条；tag 用**圆角胶囊**（底 `#152238`、描边 `#2c3a58`、等宽字体 `#9FB3D1`），不要裸文本；右上角 `zata.cc` 等宽小字水印；右侧图形母题限位 x∈[760,1120]、y∈[120,280]，线框风格 stroke 2.5、`fill:none` 为主，重用标题区不重叠。
- 无外部资源、无远程字体，只用 `sans-serif` / `monospace` 泛型字体；文件 < 20KB。
- 配色用主题色 `#5b87bf` 及蓝/紫/青系（每个分类一对固定强调色，见 `tools/cover.py` 的 `CATEGORY_STYLE`，不要临场发挥新配色）。
- frontmatter 指向它：`image: images/index/index.svg`。
- 没有现成封面时**不要搜网络图**，一律生成 SVG。
- 改完用浏览器或 `qlmanage -t -s 1200 -o /tmp images/index/index.svg` 过一眼，重点检查：标题是否被折行截断、母题与文字是否重叠、裁切后四边是否有内容贴边。

## 第三步：写法——叙事博客，不是工程报告

这是本 skill 的核心。ZataTree 的文章是**叙事风格**（参考 `content/post/Vibe-Coding/AI-Frontend/AI 前端调试技巧：把被遮挡翻译成尺寸约束/index.md`），不要把实现报告直接贴上去。

结构范式：

1. **钩子开场**：从现象切入，写出第一直觉（通常是错的猜测），给读者代入感。例：「第一反应：文案写错了……打开代码一看，不对劲。」
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

本机已装 hugo（extended，v0.165+），直接用：

```bash
hugo server -D   # 预览，起浏览器过一眼首页卡片的封面裁切效果
hugo --gc --minify
```

注意：`hugo.yaml` 里的 `baseurl: www.zata.cc` **没有协议头**，直接 `hugo` 出的静态页里图片 URL 是坏的（无协议被当相对路径，封面显示为细条）——预览一律走 `hugo server`，部署走 GitHub Actions（CI 会用 `--baseURL` 覆盖，不受影响）。

如果某台机器没有 hugo，做替代校验即可，不要为验证而 `brew install hugo`：

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

## 收尾

- 不主动 `git add/commit/push`，ZataTree 的部署走 `hugo` 分支 + GitHub Actions，是否提交由用户决定。
- 提醒用户在本地 `hugo server -D` 过一眼渲染效果（重点看首页卡片的封面裁切）。
