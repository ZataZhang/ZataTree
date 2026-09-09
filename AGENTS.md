# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

> **Framework: Hugo** — This is a **Hugo** static site generator project (Hugo 0.141.0 extended). All content lives under `content/`, uses Hugo's TOML/YAML frontmatter conventions, and is rendered through the `hugo-theme-stack` theme. Use `hugo` / `hugo server` for build and dev work — do not introduce other static-site tooling.

## Repository Overview

This is a Hugo-based static blog repository named "ZataTree" that serves as a comprehensive knowledge base covering computer science, programming, AI/ML, and software development topics. The site is deployed at www.zata.cc and uses the hugo-theme-stack theme.

## Architecture

### Content Structure
The blog follows a hierarchical content organization:
- **Categories**: Top-level content classifications (Agent, Design, Engineering, DeepLearning, Grammar, Knowledge, Library, PaperReading, Platforms_Tools, Project_Application)
- **Tags**: Specific topics within categories
- **Posts**: Individual articles organized as `content/post/{category}/{tag}/{title}/index.md`

### Key Directories
- `content/post/`: Main content organized by category/tag/title structure
- `content/categories/`: Category metadata and images
- `content/tags/`: Tag metadata and images  
- `themes/hugo-theme-stack/`: Hugo theme (git submodule)
- `public/`: Generated static site output
- `static/`: Static assets (favicon, etc.)
- `assets/`: Theme assets and custom configurations

## Development Commands

### Hugo Site Management
```bash
# Local development with drafts
hugo server -D

# Local development without drafts  
hugo server

# Build static site
hugo --gc --minify

# Build with specific baseURL
hugo --gc --minify --baseURL "https://www.zata.cc/"
```

### Content Management Tool
The repository includes a custom Python tool (`zata.py`) for content management:

```bash
# Build the zata tool
pyinstaller --onefile --console --name=zata --clean zata.py

# Create new category
python zata.py create-category -c "CategoryName" -i "path/to/image.png"

# Create new tag  
python zata.py create-tag -c "CategoryName" -t "TagName" -i "path/to/image.png"

# Create new article
python zata.py create -c "CategoryName" -t "TagName" -b "Article Title"

# Search existing tags
python zata.py search-tags -k "keyword"

# Launch GUI interface
python zata.py gui
```

## Content Creation Workflow

### Article Structure
Each article must follow this structure:
```
content/post/{category}/{tag}/{title}/
├── index.md          # Main content file
├── images/           # Article images (optional)
└── {other-assets}    # Additional files (optional)
```

### Front Matter Template
```yaml
---
title: Article Title
description: Brief description
date: 2025-01-15T10:00:00+08:00
slug: title/index.md
image: images/index/index.png  # Optional
categories:
    - CategoryName
tags:
    - TagName
draft: false  # Set to true for drafts
---
```

### Important Conventions
- **Multilingual Support**: Default content language is zh-cn (Chinese), with English support
- **Image Handling**: Article images should be placed in `images/index/` subdirectory
- **Naming**: Use descriptive folder names that match the article title
- **Categories**: Must be pre-created using the zata tool
- **Tags**: Must be associated with categories and pre-created

### Cover Image Generation

Every published article must have a cover image referenced from its frontmatter as `image: images/index/index.<ext>`.

**When creating or reviewing an article**, follow this decision tree:

1. Check whether `images/index/index.png` (or `.svg`, `.jpg`, `.webp`) already exists in the article directory.
2. If it exists → leave it alone, just confirm the frontmatter `image:` field points to it.
3. If it is **missing**, do **not** search the web for a stock image. Instead, **generate an SVG cover**:
   - File path: `{article-dir}/images/index/index.svg`
   - Canvas: **1200×400 (3:1), with `width`/`height` attributes on the `<svg>` root** (not just `viewBox` — without them browsers report `naturalWidth = 0` and the image collapses).
   - Why 3:1: the homepage/list cards crop covers to a fixed-height full-width strip (≈845×250, ~3.4:1 on desktop, `object-fit: cover` center-crop); 1200×630 covers lose ~44% of their height there. The article page hero shows the image at its natural ratio.
   - Safe-zone layout: keep the title (font-size ≥72px), tag words, and any diagram inside the central band y∈[80, 320] with ≥100px side margins. Background gradients/decoration may bleed to the edges; anything placed at the edges will be cropped on the homepage.
   - Style: minimal, geometric, with the article title and (optionally) 1–2 tag words. Use the `hugo-theme-stack` accent palette (primary `#5b87bf`, accent tones of blue / purple / teal). Avoid stock-photo clichés.
   - Format: inline SVG, no external assets, no remote fonts (use generic `sans-serif` / `serif`). Keep file size small (< 20 KB ideal).
4. After generating, add or update the frontmatter:
   ```yaml
   image: images/index/index.svg
   ```

This rule applies to any new article, any article extracted from another article's directory (e.g. the `记忆模块技术文档` extraction), and any article missing a cover during cleanup. SVG-first keeps the repo self-contained and avoids copyright issues.

## Deployment

### GitHub Actions
The repository uses GitHub Actions for automatic deployment:
- **Trigger**: Pushes to `hugo` branch
- **Hugo Version**: 0.141.0 (extended)
- **Target**: GitHub Pages
- **Workflow**: `.github/workflows/hugo.yaml`

### Manual Deployment
```bash
# Ensure git submodules are updated
git submodule update --init --recursive

# Build and deploy
hugo --gc --minify --baseURL "https://www.zata.cc/"
```

## Theme Configuration

### Key Settings in hugo.yaml
- **Theme**: hugo-theme-stack
- **Base URL**: www.zata.cc  
- **Default Language**: zh-cn
- **Comments**: Giscus integration enabled
- **Features**: Search, archives, categories, tag cloud widgets

### Customizations
- Custom footer template: `layouts/partials/footer/custom.html`
- Bilibili shortcode: `layouts/shortcodes/bilibili.html`
- Avatar and sidebar configuration in hugo.yaml

## Troubleshooting

### Common Issues
1. **Theme not loading**: Ensure git submodule is properly initialized
2. **Build failures**: Check Hugo version compatibility (requires extended version)
3. **Missing images**: Verify image paths in front matter match actual file locations
4. **Category/tag errors**: Use zata tool to create proper directory structure

### File Permissions
The zata.py tool requires write permissions to create directories and files in the content folder.

## Content Guidelines

### Supported Categories
- **Agent**: AI agents, LangChain, MetaGPT
- **Design**: Architecture, modeling, diagrams, prototyping
- **Engineering**: Software engineering, observability, development practices
- **DeepLearning**: ML models, training, tools
- **Grammar**: Programming language syntax (Python, Matlab, PyQt)
- **Knowledge**: General knowledge, tutorials, documentation
- **Library**: Code libraries and frameworks
- **PaperReading**: Academic paper summaries
- **Platforms_Tools**: Development tools and platforms  
- **Project_Application**: Practical projects and applications

### Writing Standards
- Use clear, descriptive titles
- Include proper front matter metadata
- Organize images in dedicated folders
- Follow established category/tag taxonomy
- Write in Markdown with Hugo shortcodes when needed
