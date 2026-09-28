/**
 * 搜索结果条目：在主题的渲染上补一枚「分类（书）」胶囊。
 *
 * 为什么不直接改主题：themes/hugo-theme-stack 是 vendored submodule，
 * 复制一份 400 行的 search.tsx 进项目会变成永久要跟的分支。
 * 主题的 Search.render 是 public static，且它在 window 的 load 事件里才调用
 * （defer 脚本求值之后），所以在这里换掉这个静态方法就够 ——
 * 命中算法、<mark> 转义、排序、结果计数全部沿用主题那份。
 *
 * 数据来自 layouts/page/search.json 里补的 category / categoryColor 两个字段。
 * 入口见 layouts/page/search.html（打包的是本文件，本文件再把主题那份拉进来）。
 */
import Search from "ts/search.tsx";

interface SearchItem {
    title: string;
    preview: string;
    permalink: string;
    image?: string;
    category?: string;
    categoryColor?: string;
}

function el(tag: string, className?: string): HTMLElement {
    const node = document.createElement(tag);
    if (className) node.className = className;
    return node;
}

function render(item: SearchItem): HTMLElement {
    const article = el("article");
    const link = el("a") as HTMLAnchorElement;
    link.href = item.permalink;

    const details = el("div", "article-details");

    if (item.category) {
        /* 复用文章卡片那套 .article-category 结构和 --chip-raw 变量，
           同一本书在卡片、搜索结果里是同一个颜色（配色见 assets/scss/custom.scss 第 2 节）。 */
        const cat = el("header", "article-category");
        const chip = el("a");
        chip.textContent = item.category;
        if (item.categoryColor) chip.style.setProperty("--chip-raw", item.categoryColor);
        cat.appendChild(chip);
        details.appendChild(cat);
    }

    /* title / preview 里带主题的 <mark> 高亮：文本本身在主题那份里已经逐字转义过，
       和它原来用 dangerouslySetInnerHTML 是同一个信任边界（数据源是本站自己生成的索引）。 */
    const title = el("h2", "article-title");
    title.innerHTML = item.title;

    const preview = el("section", "article-preview");
    preview.innerHTML = item.preview;

    details.appendChild(title);
    details.appendChild(preview);
    link.appendChild(details);

    if (item.image) {
        const wrap = el("div", "article-image");
        const img = document.createElement("img");
        img.src = item.image;
        img.loading = "lazy";
        wrap.appendChild(img);
        link.appendChild(wrap);
    }

    article.appendChild(link);
    return article;
}

(Search as unknown as { render: (item: SearchItem) => HTMLElement }).render = render;
