#!/bin/bash

# Zata - 博客管理工具 (Shell版本)
# 对应 zata.py 的功能

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    if ! command -v cp &> /dev/null; then
        missing_deps+=("cp")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}错误：缺少必要的依赖: ${missing_deps[*]}${NC}"
        echo "请安装缺少的依赖后重试"
        exit 1
    fi
}

# 获取当前时间
get_current_time() {
    date +"%Y-%m-%dT%H:%M:%S+08:00"
}

# 创建category目录
create_category() {
    local category="$1"
    local image_path="$2"
    
    # 创建post下的category目录
    local post_target_path="content/post/$category"
    # 创建categories下的category目录
    local categories_target_path="content/categories/$category"
    
    # 创建目录
    mkdir -p "$post_target_path"
    mkdir -p "$categories_target_path"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}创建category时发生错误${NC}"
        return 1
    fi
    
    # 如果提供了图片，复制到categories目录
    if [ -n "$image_path" ] && [ -f "$image_path" ]; then
        local image_name=$(basename "$image_path")
        local target_image_path="$categories_target_path/$image_name"
        cp "$image_path" "$target_image_path"
        
        # 创建_index.md文件
        local index_md_path="$categories_target_path/_index.md"
        cat > "$index_md_path" << EOF
---
title: "$category"
description: "This is category $category"
date: $(get_current_time)
slug: "$category"
image: "$image_name"
style:
    background: "#238377"
    color: "#fff"
---
EOF
        echo -e "${GREEN}Category目录创建成功！图片已复制，_index.md已创建。${NC}"
    else
        echo -e "${GREEN}Category目录 '$post_target_path' 和 '$categories_target_path' 创建成功！${NC}"
    fi
    
    return 0
}

# 创建tag目录
create_tag() {
    local category="$1"
    local tag="$2"
    local image_path="$3"
    
    # 创建post下的tag目录
    local post_base_path="content/post"
    local post_target_path="$post_base_path/$category/$tag"
    
    # 创建tags下的tag目录
    local tags_target_path="content/tags/$tag"
    
    local category_path="$post_base_path/$category"
    if [ ! -d "$category_path" ]; then
        echo -e "${RED}错误：Category目录 '$category_path' 不存在！请先创建category${NC}"
        return 1
    fi
    
    # 创建目录
    mkdir -p "$post_target_path"
    mkdir -p "$tags_target_path"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}创建tag时发生错误${NC}"
        return 1
    fi
    
    # 如果提供了图片，复制到tags目录
    if [ -n "$image_path" ] && [ -f "$image_path" ]; then
        local image_name=$(basename "$image_path")
        local target_image_path="$tags_target_path/$image_name"
        cp "$image_path" "$target_image_path"
        # 复制图片到post目录下并重命名为index.png
        local target_post_image_path="$post_target_path/index.png"
        cp "$image_path" "$target_post_image_path"
        
        # 创建_index.md文件
        local index_md_path="$tags_target_path/_index.md"
        cat > "$index_md_path" << EOF
---
title: "$tag"
description: "This is tag $tag"
date: $(get_current_time)
slug: "$tag"
image: "$image_name"
style:
    background: "#238377"
    color: "#fff"
---
EOF
        echo -e "${GREEN}Tag目录创建成功！图片已复制，_index.md已创建。${NC}"
    else
        echo -e "${GREEN}Tag目录 '$post_target_path' 和 '$tags_target_path' 创建成功！${NC}"
    fi
    
    return 0
}

# 创建文章目录和index.md文件
create_folder_and_md() {
    local categories="$1"
    local tags="$2"
    local title="$3"
    
    local current_time=$(get_current_time)
    local base_path="content/post"
    
    local target_path=""
    local parent_path=""
    
    if [ -n "$categories" ]; then
        target_path="$base_path/$categories/$tags/$title"
        parent_path="$base_path/$categories/$tags"
        
        if [ ! -d "$parent_path" ]; then
            echo -e "${RED}错误：父目录 '$parent_path' 不存在！请先创建相应的categories和tags目录${NC}"
            return 1
        fi
    else
        # 自动查找tag所在的category
        local matched_paths=()
        for category in "$base_path"/*/; do
            if [ -d "$category" ]; then
                category_name=$(basename "$category")
                tag_path="$category$tags"
                if [ -d "$tag_path" ]; then
                    matched_paths+=("$tag_path")
                fi
            fi
        done
        
        if [ ${#matched_paths[@]} -eq 0 ]; then
            echo -e "${RED}错误：未在任何category下找到tags '$tags'！请先创建相应的tags目录${NC}"
            return 1
        elif [ ${#matched_paths[@]} -gt 1 ]; then
            echo -e "${RED}错误：找到多个匹配的tags '$tags'：${NC}"
            for path in "${matched_paths[@]}"; do
                echo "  - $path"
            done
            echo "请指定具体的category以避免歧义"
            return 1
        else
            parent_path="${matched_paths[0]}"
            target_path="$parent_path/$title"
            categories=$(basename "$(dirname "$parent_path")")
        fi
    fi
    
    # 创建目标目录
    mkdir -p "$target_path"
    local md_file_path="$target_path/index.md"
    
    # 创建index.md文件
    if [ ! -f "$md_file_path" ]; then
        cat > "$md_file_path" << EOF
---
title: $title
description: ""
date: $current_time
image: images/index/index.png
EOF
        
        if [ -n "$categories" ]; then
            cat >> "$md_file_path" << EOF
categories:
    - $categories
EOF
        fi
        
        cat >> "$md_file_path" << EOF
tags:
    - $tags
---
EOF
    fi
    
    # 检查并复制 index.png
    local source_image="$parent_path/index.png"
    local target_image_dir="$target_path/images/index"
    local target_image_path="$target_image_dir/index.png"
    
    if [ -f "$source_image" ]; then
        mkdir -p "$target_image_dir"
        cp "$source_image" "$target_image_path"
        echo -e "${GREEN}文件夹 '$target_path' 和 'index.md' 创建成功！已复制图片到 '$target_image_path'${NC}"
    else
        echo -e "${GREEN}文件夹 '$target_path' 和 'index.md' 创建成功！${NC}"
    fi
    
    return 0
}

# 获取现有Category列表
get_existing_categories() {
    local base_path="content/post"
    if [ ! -d "$base_path" ]; then
        return
    fi
    
    for category in "$base_path"/*/; do
        if [ -d "$category" ]; then
            basename "$category"
        fi
    done
}

# 获取现有Tag列表
get_existing_tags() {
    local category="$1"
    local base_path="content/post"
    
    if [ ! -d "$base_path" ]; then
        return
    fi
    
    if [ -n "$category" ]; then
        local category_path="$base_path/$category"
        if [ -d "$category_path" ]; then
            for tag in "$category_path"/*/; do
                if [ -d "$tag" ]; then
                    basename "$tag"
                fi
            done
        fi
    else
        for cat in "$base_path"/*/; do
            if [ -d "$cat" ]; then
                for tag in "$cat"/*/; do
                    if [ -d "$tag" ]; then
                        basename "$tag"
                    fi
                done
            fi
        done | sort -u
    fi
}

# 搜索tags
search_tags() {
    local keyword="$1"
    local base_path="content/post"
    
    if [ ! -d "$base_path" ]; then
        return
    fi
    
    for category in "$base_path"/*/; do
        if [ -d "$category" ]; then
            category_name=$(basename "$category")
            for tag in "$category"/*/; do
                if [ -d "$tag" ]; then
                    tag_name=$(basename "$tag")
                    if [ -z "$keyword" ] || echo "$tag_name" | grep -qi "$keyword"; then
                        echo "Tag: $tag_name"
                        echo "Category: $category_name"
                        echo "路径: $tag"
                        echo "---"
                    fi
                fi
            done
        fi
    done
}

# 根据tag名称查找所属的category
find_tag_category() {
    local tag_name="$1"
    local base_path="content/post"
    
    if [ ! -d "$base_path" ]; then
        return
    fi
    
    local found_categories=()
    for category in "$base_path"/*/; do
        if [ -d "$category" ]; then
            category_name=$(basename "$category")
            tag_path="$category$tag_name"
            if [ -d "$tag_path" ]; then
                found_categories+=("$category_name")
            fi
        fi
    done
    
    printf '%s\n' "${found_categories[@]}"
}



# 内部：以简单可解析格式返回匹配的 tag 列表：category::tag::path
search_tags_items() {
    local keyword="$1"
    local base_path="content/post"
    if [ ! -d "$base_path" ]; then
        return
    fi

    shopt -s nullglob
    for category in "$base_path"/*/; do
        [ -d "$category" ] || continue
        local category_name
        category_name=$(basename "$category")
        for tag in "$category"/*/; do
            [ -d "$tag" ] || continue
            local tag_name
            tag_name=$(basename "$tag")
            if [ -z "$keyword" ] || echo "$tag_name" | grep -qi "$keyword"; then
                # 使用制表符分隔，避免双冒号分割问题
                printf '%s\t%s\t%s\n' "$category_name" "$tag_name" "$tag"
            fi
        done
    done
}

# 交互：创建文章（可通过关键字筛选Tag）
interactive_create_post() {
    while true; do
        echo -e "${BLUE}通过关键字筛选Tag（留空显示全部，输入 q 返回）：${NC}"
        read -r -p "> " keyword
        if [[ "$keyword" == "q" || "$keyword" == "Q" ]]; then
            return 0
        fi

        # 收集匹配项
        local lines=()
        while IFS= read -r line; do
            lines+=("$line")
        done < <(search_tags_items "$keyword")

        if [ ${#lines[@]} -eq 0 ]; then
            echo -e "${YELLOW}未找到匹配的Tag，请重试。${NC}"
            continue
        fi

        # 构造显示项
        local display=()
        local cats=()
        local tags=()
        local paths=()
        local i
        for ((i=0; i<${#lines[@]}; i++)); do
            IFS=$'\t' read -r c t p <<< "${lines[$i]}"
            cats+=("$c")
            tags+=("$t")
            paths+=("$p")
            display+=("$t ($c)")
        done

        local options=("${display[@]}" "重新搜索" "返回主菜单")
        echo -e "${BLUE}选择一个Tag:${NC}"
        PS3="选择序号: "
        select choice in "${options[@]}"; do
            if [ -z "$choice" ]; then
                echo -e "${YELLOW}无效选择，请重试。${NC}"
                continue
            fi

            local total=${#options[@]}
            local re_search_index=$((total-1))
            local back_index=$((total))

            if [ "$REPLY" -eq "$re_search_index" ]; then
                # 重新搜索
                break
            elif [ "$REPLY" -eq "$back_index" ]; then
                return 0
            else
                local idx=$((REPLY-1))
                if [ $idx -ge 0 ] && [ $idx -lt ${#display[@]} ]; then
                    local sel_cat="${cats[$idx]}"
                    local sel_tag="${tags[$idx]}"
                    echo -e "${BLUE}已选择Tag: ${sel_tag} (Category: ${sel_cat})${NC}"
                    local title=""
                    while true; do
                        read -r -p "请输入文章标题: " title
                        if [ -n "$title" ]; then
                            break
                        fi
                        echo -e "${YELLOW}标题不能为空。${NC}"
                    done
                    create_folder_and_md "$sel_cat" "$sel_tag" "$title"
                    return 0
                else
                    echo -e "${YELLOW}无效选择，请重试。${NC}"
                fi
            fi
        done
    done
}

# 交互：创建Tag（选择已有Category）
interactive_create_tag() {
    while true; do
        # 读取现有类别
        local categories=()
        while IFS= read -r line; do
            [ -n "$line" ] && categories+=("$line")
        done < <(get_existing_categories)

        if [ ${#categories[@]} -eq 0 ]; then
            echo -e "${YELLOW}当前没有任何Category，请先创建。${NC}"
            local new_cat
            read -r -p "输入新Category名称（或 q 返回）: " new_cat
            if [[ "$new_cat" == "q" || "$new_cat" == "Q" || -z "$new_cat" ]]; then
                return 0
            fi
            read -r -p "可选：Category图片路径（留空跳过）: " img
            create_category "$new_cat" "$img"
            continue
        fi

        local options=("${categories[@]}" "新建Category" "返回主菜单")
        echo -e "${BLUE}选择一个Category:${NC}"
        PS3="选择序号: "
        select choice in "${options[@]}"; do
            if [ -z "$choice" ]; then
                echo -e "${YELLOW}无效选择，请重试。${NC}"
                continue
            fi
            local total=${#options[@]}
            local new_index=$((total-1))
            local back_index=$((total))
            if [ "$REPLY" -eq "$new_index" ]; then
                # 新建Category
                local new_cat
                read -r -p "输入新Category名称: " new_cat
                [ -z "$new_cat" ] && { echo -e "${YELLOW}名称不能为空${NC}"; break; }
                read -r -p "可选：Category图片路径（留空跳过）: " img
                create_category "$new_cat" "$img"
                break
            elif [ "$REPLY" -eq "$back_index" ]; then
                return 0
            else
                local idx=$((REPLY-1))
                if [ $idx -ge 0 ] && [ $idx -lt ${#categories[@]} ]; then
                    local category="${categories[$idx]}"
                    local tag
                    while true; do
                        read -r -p "输入要创建的Tag名称: " tag
                        [ -n "$tag" ] && break
                        echo -e "${YELLOW}Tag名称不能为空。${NC}"
                    done
                    read -r -p "可选：Tag图片路径（留空跳过）: " img
                    create_tag "$category" "$tag" "$img"
                    return 0
                else
                    echo -e "${YELLOW}无效选择，请重试。${NC}"
                fi
            fi
        done
    done
}

# 交互主菜单
interactive_menu() {
    echo -e "${BLUE}Zata 交互模式${NC}"
    while true; do
        local options=("创建博客 Post（按相似Tag选择）" "创建Tag" "退出")
        PS3="选择序号: "
        select choice in "${options[@]}"; do
            case "$REPLY" in
                1)
                    interactive_create_post
                    break
                    ;;
                2)
                    interactive_create_tag
                    break
                    ;;
                3)
                    echo -e "${GREEN}已退出交互模式。${NC}"
                    return 0
                    ;;
                *)
                    echo -e "${YELLOW}无效选择，请重试。${NC}"
                    ;;
            esac
        done
    done
}


# 显示帮助信息
show_help() {
    cat << EOF
Zata - 博客管理工具 (Shell版本)

 用法: $0 [命令] [选项]
 无参数时默认进入交互模式（等同于 `$0 select`）

命令:
  create             创建文章文件夹和index.md
    -c, --categories  博客分类（可选，如果不指定会自动根据tag查找）
    -t, --tags        博客标签（必需）
    -b, --title       博客标题（必需）

  create-category    创建category目录
    -c, --category    要创建的category名称（必需）
    -i, --image       category的图片路径（可选）

  create-tag         创建tag目录
    -c, --category    所属category（必需）
    -t, --tag         要创建的tag名称（必需）
    -i, --image       tag的图片路径（可选）

  search-tags        搜索现有的tag
    -k, --keyword     搜索关键词（可选）

  select | menu      交互式选择创建 博客/Tag（支持按相似名称筛选Tag）

示例:
  $0 create -t "技术" -b "我的第一篇博客"
  $0 create-category -c "技术"
  $0 create-tag -c "技术" -t "Python"
  $0 search-tags -k "技术"
  $0 select

EOF
}

# 主函数
main() {
    # 检查依赖
    check_dependencies
    
    # 如果没有参数，显示帮助
    if [ $# -eq 0 ]; then
        interactive_menu
        exit 0
    fi
    
    # 解析命令行参数
    case "$1" in
        "create")
            shift
            local categories=""
            local tags=""
            local title=""
            
            while [[ $# -gt 0 ]]; do
                case $1 in
                    -c|--categories)
                        categories="$2"
                        shift 2
                        ;;
                    -t|--tags)
                        tags="$2"
                        shift 2
                        ;;
                    -b|--title)
                        title="$2"
                        shift 2
                        ;;
                    *)
                        echo -e "${RED}未知参数: $1${NC}"
                        show_help
                        exit 1
                        ;;
                esac
            done
            
            if [ -z "$tags" ] || [ -z "$title" ]; then
                echo -e "${RED}错误：tags和title是必需参数${NC}"
                show_help
                exit 1
            fi
            
            # 如果没有指定category，尝试自动查找
            if [ -z "$categories" ]; then
                local found_categories=($(find_tag_category "$tags"))
                if [ ${#found_categories[@]} -eq 0 ]; then
                    echo -e "${RED}错误：未找到tag '$tags'！请先创建相应的tag目录${NC}"
                    exit 1
                elif [ ${#found_categories[@]} -eq 1 ]; then
                    categories="${found_categories[0]}"
                    echo -e "${BLUE}自动找到tag '$tags' 属于category '$categories'${NC}"
                else
                    echo -e "${RED}错误：找到多个category包含tag '$tags'：${found_categories[*]}${NC}"
                    echo "请使用 -c 参数指定具体的category"
                    exit 1
                fi
            fi
            
            create_folder_and_md "$categories" "$tags" "$title"
            ;;
            
        "create-category")
            shift
            local category=""
            local image=""
            
            while [[ $# -gt 0 ]]; do
                case $1 in
                    -c|--category)
                        category="$2"
                        shift 2
                        ;;
                    -i|--image)
                        image="$2"
                        shift 2
                        ;;
                    *)
                        echo -e "${RED}未知参数: $1${NC}"
                        show_help
                        exit 1
                        ;;
                esac
            done
            
            if [ -z "$category" ]; then
                echo -e "${RED}错误：category是必需参数${NC}"
                show_help
                exit 1
            fi
            
            create_category "$category" "$image"
            ;;
            
        "create-tag")
            shift
            local category=""
            local tag=""
            local image=""
            
            while [[ $# -gt 0 ]]; do
                case $1 in
                    -c|--category)
                        category="$2"
                        shift 2
                        ;;
                    -t|--tag)
                        tag="$2"
                        shift 2
                        ;;
                    -i|--image)
                        image="$2"
                        shift 2
                        ;;
                    *)
                        echo -e "${RED}未知参数: $1${NC}"
                        show_help
                        exit 1
                        ;;
                esac
            done
            
            if [ -z "$category" ] || [ -z "$tag" ]; then
                echo -e "${RED}错误：category和tag是必需参数${NC}"
                show_help
                exit 1
            fi
            
            create_tag "$category" "$tag" "$image"
            ;;
            
        "search-tags")
            shift
            local keyword=""
            
            while [[ $# -gt 0 ]]; do
                case $1 in
                    -k|--keyword)
                        keyword="$2"
                        shift 2
                        ;;
                    *)
                        echo -e "${RED}未知参数: $1${NC}"
                        show_help
                        exit 1
                        ;;
                esac
            done
            
            local results=$(search_tags "$keyword")
            if [ -z "$results" ]; then
                if [ -n "$keyword" ]; then
                    echo "未找到包含关键词 '$keyword' 的tag"
                else
                    echo "未找到任何tag"
                fi
            else
                echo "$results"
            fi
            ;;
            

            
        -h|--help|help)
            show_help
            ;;
            
        "select"|"menu"|"interactive")
            # 进入交互式菜单
            interactive_menu
            ;;

        *)
            echo -e "${RED}未知命令: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 
