# TODO  This exe file seems to be unable to create a blog using parameters. 这个py文件打包的exe，无法使用参数创建博客。


import os
from datetime import datetime
import argparse
import subprocess  # 用于打开文件
import sys  # 用于检测操作系统平台
import shutil  # 用于文件复制

# 创建category目录
def create_category(category, image_path=None):
    """创建category目录，可选指定图片"""
    # 创建post下的category目录
    post_target_path = os.path.join("content", "post", category)
    # 创建categories下的category目录
    categories_target_path = os.path.join("content", "categories", category)
    
    try:
        # 创建两个目录
        os.makedirs(post_target_path, exist_ok=True)
        os.makedirs(categories_target_path, exist_ok=True)
        
        # 如果提供了图片，复制到categories目录
        if image_path and os.path.exists(image_path):
            image_name = os.path.basename(image_path)
            target_image_path = os.path.join(categories_target_path, image_name)
            shutil.copy2(image_path, target_image_path)
            
            # 创建_index.md文件
            index_md_path = os.path.join(categories_target_path, "_index.md")
            with open(index_md_path, 'w', encoding='utf-8') as f:
                f.write(f"""---
title: "{category}"
description: "This is category {category}"
date: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")}
slug: "{category}"
image: "{image_name}"
style:
    background: "#238377"
    color: "#fff"
---
""")
            return True, f"Category目录创建成功！图片已复制，_index.md已创建。"
        
        return True, f"Category目录 '{post_target_path}' 和 '{categories_target_path}' 创建成功！"
    except Exception as e:
        return False, f"创建category时发生错误: {str(e)}"



# 创建tag目录
def create_tag(category, tag, image_path=None):
    """创建tag目录，必须指定category，可选指定图片"""
    # 创建post下的tag目录
    post_base_path = os.path.join("content", "post")
    post_target_path = os.path.join(post_base_path, category, tag)
    
    # 创建tags下的tag目录
    tags_target_path = os.path.join("content", "tags", tag)
    
    category_path = os.path.join(post_base_path, category)
    if not os.path.exists(category_path):
        return False, f"错误：Category目录 '{category_path}' 不存在！请先创建category"
    
    try:
        # 创建两个目录
        os.makedirs(post_target_path, exist_ok=True)
        os.makedirs(tags_target_path, exist_ok=True)
        
        # 如果提供了图片，复制到tags目录
        if image_path and os.path.exists(image_path):
            image_name = os.path.basename(image_path)
            target_image_path = os.path.join(tags_target_path, image_name)
            shutil.copy2(image_path, target_image_path)
            # 复制图片到post目录下并重命名为index.png
            target_post_image_path = os.path.join(post_target_path, "index.png")
            shutil.copy2(image_path, target_post_image_path)
            
            # 创建_index.md文件
            index_md_path = os.path.join(tags_target_path, "_index.md")
            with open(index_md_path, 'w', encoding='utf-8') as f:
                f.write(f"""---
title: "{tag}"
description: "This is tag {tag}"
date: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")}
slug: "{tag}"
image: "{image_name}"
style:
    background: "#238377"
    color: "#fff"
---
""")
            return True, f"Tag目录创建成功！图片已复制，_index.md已创建。"
        
        return True, f"Tag目录 '{post_target_path}' 和 '{tags_target_path}' 创建成功！"
    except Exception as e:
        return False, f"创建tag时发生错误: {str(e)}"






# 创建文章目录和index.md文件
def create_folder_and_md(categories, tags, title):
    """创建文章目录和index.md文件，并复制tag目录下的index.png（如果存在）"""
    import shutil  # 添加 shutil 用于文件复制

    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    base_path = os.path.join("content", "post")
    
    if categories:
        target_path = os.path.join(base_path, categories, tags, title)
        parent_path = os.path.join(base_path, categories, tags)
        
        if not os.path.exists(parent_path):
            return False, f"错误：父目录 '{parent_path}' 不存在！请先创建相应的categories和tags目录"
    else:
        matched_paths = []
        for category in os.listdir(base_path):
            category_path = os.path.join(base_path, category)
            if os.path.isdir(category_path):
                tag_path = os.path.join(category_path, tags)
                if os.path.exists(tag_path) and os.path.isdir(tag_path):
                    matched_paths.append(tag_path)
        
        if len(matched_paths) == 0:
            return False, f"错误：未在任何category下找到tags '{tags}'！请先创建相应的tags目录"
        elif len(matched_paths) > 1:
            error_msg = f"错误：找到多个匹配的tags '{tags}'：\n"
            for path in matched_paths:
                error_msg += f"  - {path}\n"
            error_msg += "请指定具体的category以避免歧义"
            return False, error_msg
        else:
            parent_path = matched_paths[0]
            target_path = os.path.join(parent_path, title)
            categories = os.path.basename(os.path.dirname(parent_path))

    try:
        # 创建目标目录
        os.makedirs(target_path, exist_ok=True)
        md_file_path = os.path.join(target_path, "index.md")
        
        header_content = f"""---
title: {title}
description: ""
date: {current_time}
image: images/index/index.png
"""
        if categories:
            header_content += f"""categories:
    - {categories}
"""
        header_content += f"""tags:
    - {tags}
---
"""
        
        # 创建 index.md 文件
        if not os.path.exists(md_file_path):
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(header_content)

        # 检查并复制 index.png
        source_image = os.path.join(parent_path, "index.png")
        target_image_dir = os.path.join(target_path, "images", "index")
        target_image_path = os.path.join(target_image_dir, "index.png")
        
        if os.path.exists(source_image):
            os.makedirs(target_image_dir, exist_ok=True)
            shutil.copy2(source_image, target_image_path)
            return True, f"文件夹 '{target_path}' 和 'index.md' 创建成功！已复制图片到 '{target_image_path}'"
        
        return True, f"文件夹 '{target_path}' 和 'index.md' 创建成功！"
    except Exception as e:
        return False, f"发生错误: {str(e)}"

# 获取现有 Category 和 Tag 列表的函数
def get_existing_categories():
    base_path = os.path.join("content", "post")
    if not os.path.exists(base_path):
        return []
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

def get_existing_tags(category=None):
    base_path = os.path.join("content", "post")
    if not os.path.exists(base_path):
        return []
    tags = set()
    if category:
        category_path = os.path.join(base_path, category)
        if os.path.exists(category_path):
            tags.update([d for d in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, d))])
    else:
        for cat in os.listdir(base_path):
            cat_path = os.path.join(base_path, cat)
            if os.path.isdir(cat_path):
                tags.update([d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d))])
    return sorted(list(tags))

def search_tags(keyword=None):
    """搜索所有tag，可选择按关键词过滤"""
    base_path = os.path.join("content", "post")
    if not os.path.exists(base_path):
        return []
    
    tag_info = []
    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if os.path.isdir(category_path):
            for tag in os.listdir(category_path):
                tag_path = os.path.join(category_path, tag)
                if os.path.isdir(tag_path):
                    if keyword is None or keyword.lower() in tag.lower():
                        tag_info.append({
                            'tag': tag,
                            'category': category,
                            'path': tag_path
                        })
    
    return sorted(tag_info, key=lambda x: x['tag'])

def find_tag_category(tag_name):
    """根据tag名称查找所属的category"""
    base_path = os.path.join("content", "post")
    if not os.path.exists(base_path):
        return None
    
    found_categories = []
    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if os.path.isdir(category_path):
            tag_path = os.path.join(category_path, tag_name)
            if os.path.exists(tag_path) and os.path.isdir(tag_path):
                found_categories.append(category)
    
    return found_categories


# ---------- 交互式 CLI ----------
def _prompt_choice(prompt, options):
    """显示编号选项并返回用户选择的索引，支持返回 None 代表无效或退出"""
    print(prompt)
    for idx, opt in enumerate(options, 1):
        print(f"{idx}. {opt}")
    try:
        choice = int(input("选择序号: ").strip() or "0")
    except ValueError:
        return None
    return choice - 1


def search_tags_items(keyword=None):
    """以 (category, tag, path) 列表返回匹配的 tag"""
    base_path = os.path.join("content", "post")
    if not os.path.exists(base_path):
        return []
    items = []
    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if not os.path.isdir(category_path):
            continue
        for tag in os.listdir(category_path):
            tag_path = os.path.join(category_path, tag)
            if os.path.isdir(tag_path):
                if not keyword or keyword.lower() in tag.lower():
                    items.append((category, tag, tag_path))
    return items


def interactive_create_post():
    """命令行交互：按关键字筛选 tag，选择后创建文章"""
    while True:
        keyword = input("通过关键字筛选Tag（留空显示全部，输入 q 返回）: ").strip()
        if keyword.lower() == "q":
            return

        items = search_tags_items(keyword)
        if not items:
            print("未找到匹配的Tag，请重试。\n")
            continue

        display = [f"{tag} ({cat})" for cat, tag, _ in items]
        display.extend(["重新搜索", "返回主菜单"])

        choice_idx = _prompt_choice("选择一个Tag:", display)
        if choice_idx is None:
            print("无效选择，请重试。\n")
            continue

        if choice_idx == len(display) - 2:  # 重新搜索
            continue
        if choice_idx == len(display) - 1:  # 返回
            return

        sel_cat, sel_tag, _ = items[choice_idx]
        print(f"已选择Tag: {sel_tag} (Category: {sel_cat})")
        while True:
            title = input("请输入文章标题: ").strip()
            if title:
                break
            print("标题不能为空。")
        success, msg = create_folder_and_md(sel_cat, sel_tag, title)
        print(msg + "\n")
        return


def interactive_create_tag():
    """命令行交互：选择/新建 category，再创建 tag"""
    while True:
        categories = get_existing_categories()
        if not categories:
            print("当前没有任何Category，请先创建。")
            new_cat = input("输入新Category名称（或 q 返回）: ").strip()
            if not new_cat or new_cat.lower() == "q":
                return
            img = input("可选：Category图片路径（留空跳过）: ").strip() or None
            success, msg = create_category(new_cat, img)
            print(msg + "\n")
            continue

        options = categories + ["新建Category", "返回主菜单"]
        choice_idx = _prompt_choice("选择一个Category:", options)
        if choice_idx is None:
            print("无效选择，请重试。\n")
            continue

        if choice_idx == len(options) - 2:  # 新建
            new_cat = input("输入新Category名称: ").strip()
            if not new_cat:
                print("名称不能为空。\n")
                continue
            img = input("可选：Category图片路径（留空跳过）: ").strip() or None
            success, msg = create_category(new_cat, img)
            print(msg + "\n")
            continue
        if choice_idx == len(options) - 1:  # 返回
            return

        category = categories[choice_idx]
        while True:
            tag = input("输入要创建的Tag名称: ").strip()
            if tag:
                break
            print("Tag名称不能为空。")
        img = input("可选：Tag图片路径（留空跳过）: ").strip() or None
        success, msg = create_tag(category, tag, img)
        print(msg + "\n")
        return


def interactive_menu():
    """交互主菜单"""
    while True:
        options = ["创建博客 Post（按相似Tag选择）", "创建Tag", "退出"]
        choice_idx = _prompt_choice("Zata 交互模式 - 请选择:", options)
        if choice_idx is None:
            print("无效选择，请重试。\n")
            continue
        if choice_idx == 0:
            interactive_create_post()
        elif choice_idx == 1:
            interactive_create_tag()
        elif choice_idx == 2:
            print("已退出交互模式。")
            return
        print()


# GUI 界面
def create_gui():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
    except ImportError:
        print("错误：无法导入tkinter库，GUI功能不可用")
        return
    
    root = tk.Tk()
    root.title("Zata - 博客管理工具")
    root.geometry("500x550")  # 增加高度以容纳新功能

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, fill="both", expand=True)

    # Category选项卡
    category_frame = ttk.Frame(notebook)
    notebook.add(category_frame, text="创建Category")

    ttk.Label(category_frame, text="Category名称:").pack(pady=5)
    category_entry = ttk.Entry(category_frame, width=40)
    category_entry.pack(pady=5)

    # 添加图片选择
    category_image_path = tk.StringVar()
    ttk.Label(category_frame, text="Category图片:").pack(pady=5)
    category_image_frame = ttk.Frame(category_frame)
    category_image_frame.pack(pady=5)
    category_image_entry = ttk.Entry(category_image_frame, textvariable=category_image_path, width=30)
    category_image_entry.pack(side=tk.LEFT, padx=5)

    def select_category_image():
        filename = filedialog.askopenfilename(
            title="选择Category图片",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            category_image_path.set(filename)

    ttk.Button(category_image_frame, text="浏览", command=select_category_image).pack(side=tk.LEFT)

    def create_category_btn():
        category = category_entry.get().strip()
        if not category:
            messagebox.showerror("错误", "请输入Category名称")
            return
        success, msg = create_category(category, category_image_path.get() if category_image_path.get() else None)
        messagebox.showinfo("结果", msg)
        if success:
            update_category_combobox()
            update_tag_category_combobox()

    ttk.Button(category_frame, text="创建Category", command=create_category_btn).pack(pady=10)

    # Tag选项卡
    tag_frame = ttk.Frame(notebook)
    notebook.add(tag_frame, text="创建Tag")

    ttk.Label(tag_frame, text="选择Category:").pack(pady=5)
    tag_category_combobox = ttk.Combobox(tag_frame, width=37, state="readonly")
    tag_category_combobox.pack(pady=5)
    
    ttk.Label(tag_frame, text="Tag名称:").pack(pady=5)
    tag_entry = ttk.Entry(tag_frame, width=40)
    tag_entry.pack(pady=5)

    # 添加图片选择
    tag_image_path = tk.StringVar()
    ttk.Label(tag_frame, text="Tag图片:").pack(pady=5)
    tag_image_frame = ttk.Frame(tag_frame)
    tag_image_frame.pack(pady=5)
    tag_image_entry = ttk.Entry(tag_image_frame, textvariable=tag_image_path, width=30)
    tag_image_entry.pack(side=tk.LEFT, padx=5)

    def select_tag_image():
        filename = filedialog.askopenfilename(
            title="选择Tag图片",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            tag_image_path.set(filename)

    ttk.Button(tag_image_frame, text="浏览", command=select_tag_image).pack(side=tk.LEFT)

    def update_tag_category_combobox():
        categories = get_existing_categories()
        tag_category_combobox["values"] = categories
        if categories:
            tag_category_combobox.set(categories[0])
        else:
            tag_category_combobox.set("")

    def create_tag_btn():
        category = tag_category_combobox.get()
        tag = tag_entry.get().strip()
        if not category:
            messagebox.showerror("错误", "请先创建一个Category")
            return
        if not tag:
            messagebox.showerror("错误", "请输入Tag名称")
            return
        success, msg = create_tag(category, tag, tag_image_path.get() if tag_image_path.get() else None)
        messagebox.showinfo("结果", msg)
        if success:
            update_tag_combobox()

    ttk.Button(tag_frame, text="创建Tag", command=create_tag_btn).pack(pady=10)

    # 文章选项卡
    post_frame = ttk.Frame(notebook)
    notebook.add(post_frame, text="创建/打开文章")

    # 创建文章部分
    ttk.Label(post_frame, text="选择Category（可选）:").pack(pady=5)
    category_combobox = ttk.Combobox(post_frame, width=37, state="readonly")
    category_combobox.pack(pady=5)
    
    # Tag搜索功能
    ttk.Label(post_frame, text="搜索Tag:").pack(pady=(10, 2))
    search_frame = ttk.Frame(post_frame)
    search_frame.pack(pady=2)
    tag_search_entry = ttk.Entry(search_frame, width=32)
    tag_search_entry.pack(side=tk.LEFT, padx=(0, 5))
    
    def clear_search():
        tag_search_entry.delete(0, tk.END)
        tag_search_entry.insert(0, "输入关键词搜索tag...")
        tag_search_entry.config(foreground='grey')
        update_tag_combobox()
    
    ttk.Button(search_frame, text="清除", command=clear_search, width=6).pack(side=tk.LEFT)
    
    ttk.Label(post_frame, text="选择Tag:").pack(pady=(5, 2))
    tag_combobox = ttk.Combobox(post_frame, width=37, state="readonly")
    tag_combobox.pack(pady=2)
    
    ttk.Label(post_frame, text="文章标题:").pack(pady=5)
    post_title_entry = ttk.Entry(post_frame, width=40)
    post_title_entry.pack(pady=5)

    def update_category_combobox():
        categories = get_existing_categories()
        category_combobox["values"] = [""] + categories
        if categories:
            category_combobox.set("")
    
    def update_tag_combobox(event=None):
        selected_category = category_combobox.get()
        search_keyword = tag_search_entry.get().strip()
        
        # 忽略占位符文本
        if search_keyword == "输入关键词搜索tag...":
            search_keyword = ""
        
        if selected_category:
            tags = get_existing_tags(selected_category)
        else:
            tags = get_existing_tags()
        
        # 如果有搜索关键词，过滤tags
        if search_keyword:
            tags = [tag for tag in tags if search_keyword.lower() in tag.lower()]
        
        tag_combobox["values"] = tags
        if tags:
            tag_combobox.set(tags[0])
        else:
            tag_combobox.set("")

    def on_tag_search_change(event=None):
        """当搜索框内容改变时触发"""
        update_tag_combobox()

    def on_tag_search_focus_in(event):
        """搜索框获得焦点时清除占位符"""
        if tag_search_entry.get() == "输入关键词搜索tag...":
            tag_search_entry.delete(0, tk.END)
            tag_search_entry.config(foreground='black')

    def on_tag_search_focus_out(event):
        """搜索框失去焦点时显示占位符"""
        if not tag_search_entry.get():
            tag_search_entry.insert(0, "输入关键词搜索tag...")
            tag_search_entry.config(foreground='grey')

    # 设置初始占位符
    tag_search_entry.insert(0, "输入关键词搜索tag...")
    tag_search_entry.config(foreground='grey')

    category_combobox.bind("<<ComboboxSelected>>", update_tag_combobox)
    tag_search_entry.bind("<KeyRelease>", on_tag_search_change)
    tag_search_entry.bind("<FocusIn>", on_tag_search_focus_in)
    tag_search_entry.bind("<FocusOut>", on_tag_search_focus_out)

    def create_post_btn():
        category = category_combobox.get() or None
        tag = tag_combobox.get()
        title = post_title_entry.get().strip()
        if not tag or not title:
            messagebox.showerror("错误", "请选择Tag并输入文章标题")
            return
        success, msg = create_folder_and_md(category, tag, title)
        messagebox.showinfo("结果", msg)

    ttk.Button(post_frame, text="创建文章", command=create_post_btn).pack(pady=5)

    # 打开文章部分
    ttk.Separator(post_frame, orient="horizontal").pack(fill="x", pady=10)
    
    ttk.Label(post_frame, text="输入要打开的文章标题:").pack(pady=5)
    open_title_entry = ttk.Entry(post_frame, width=40)
    open_title_entry.pack(pady=5)

    def open_post_btn():
        title = open_title_entry.get().strip()
        if not title:
            messagebox.showerror("错误", "请输入文章标题")
            return
        
        base_path = os.path.join("content", "post")
        found_paths = []
        
        for root, dirs, files in os.walk(base_path):
            if title in dirs:
                md_path = os.path.join(root, title, "index.md")
                if os.path.exists(md_path):
                    found_paths.append(md_path)
        
        if not found_paths:
            messagebox.showerror("错误", f"未找到标题为 '{title}' 的文章")
            return
        elif len(found_paths) > 1:
            messagebox.showwarning("警告", f"找到多个标题为 '{title}' 的文章，将打开第一个:\n{found_paths[0]}")
            file_path = found_paths[0]
        else:
            file_path = found_paths[0]
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # MacOS/Linux
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, file_path])
            messagebox.showinfo("成功", f"已打开文件: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"打开文件失败: {str(e)}")

    ttk.Button(post_frame, text="打开文章", command=open_post_btn).pack(pady=5)

    # 初始化下拉框
    update_category_combobox()
    update_tag_category_combobox()
    update_tag_combobox()

    root.mainloop()

def main():
    parser = argparse.ArgumentParser(prog="zata", description="博客目录和文件管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    create_parser = subparsers.add_parser("create", help="创建文章文件夹和index.md")
    create_parser.add_argument("-c", "--categories", help="博客分类（可选，如果不指定会自动根据tag查找）")
    create_parser.add_argument("-t", "--tags", required=True, help="博客标签")
    create_parser.add_argument("-b", "--title", required=True, help="博客标题")

    category_parser = subparsers.add_parser("create-category", help="创建category目录")
    category_parser.add_argument("-c", "--category", required=True, help="要创建的category名称")
    category_parser.add_argument("-i", "--image", help="category的图片路径")

    tag_parser = subparsers.add_parser("create-tag", help="创建tag目录")
    tag_parser.add_argument("-c", "--category", required=True, help="所属category")
    tag_parser.add_argument("-t", "--tag", required=True, help="要创建的tag名称")
    tag_parser.add_argument("-i", "--image", help="tag的图片路径")

    search_parser = subparsers.add_parser("search-tags", help="搜索现有的tag")
    search_parser.add_argument("-k", "--keyword", help="搜索关键词（可选）")

    gui_parser = subparsers.add_parser("gui", help="启动图形界面")
    subparsers.add_parser("select", help="交互式CLI菜单")

    args = parser.parse_args()

    # 如果没有提供命令，显示帮助并退出
    if args.command is None:
        parser.print_help()
        return

    if args.command == "create":
        # 如果没有指定category，尝试自动查找
        if not args.categories:
            found_categories = find_tag_category(args.tags)
            if len(found_categories) == 0:
                print(f"错误：未找到tag '{args.tags}'！请先创建相应的tag目录")
                return
            elif len(found_categories) == 1:
                args.categories = found_categories[0]
                print(f"自动找到tag '{args.tags}' 属于category '{args.categories}'")
            else:
                print(f"错误：找到多个category包含tag '{args.tags}'：{', '.join(found_categories)}")
                print("请使用 -c 参数指定具体的category")
                return
        
        success, msg = create_folder_and_md(args.categories, args.tags, args.title)
        print(msg)
    elif args.command == "create-category":
        success, msg = create_category(args.category, args.image)
        print(msg)
    elif args.command == "create-tag":
        success, msg = create_tag(args.category, args.tag, args.image)
        print(msg)
    elif args.command == "search-tags":
        tags = search_tags(args.keyword)
        if not tags:
            if args.keyword:
                print(f"未找到包含关键词 '{args.keyword}' 的tag")
            else:
                print("未找到任何tag")
        else:
            print(f"找到 {len(tags)} 个tag:")
            print("-" * 50)
            for tag_info in tags:
                print(f"Tag: {tag_info['tag']}")
                print(f"Category: {tag_info['category']}")
                print(f"路径: {tag_info['path']}")
                print("-" * 50)
    elif args.command == "gui":
        create_gui()
    elif args.command == "select":
        interactive_menu()

if __name__ == "__main__":
    main()