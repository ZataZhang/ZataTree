---
title: "Search"
slug: "search"
layout: "search"
outputs:
    - html
    - json
# 这里故意不写 menu 字段：右上角搜索框已经承担了入口，
# 左栏不再重复放一个 Search 导航项。
# 页面本身必须保留 —— 右栏搜索框提交后就跳到这个页面（表单 action 指向它），
# 而且 outputs 里的 json 是搜索页的数据源，删了搜索就废了。
---
