set positional-arguments

# Show how to use this justfile
default:
    @echo "Usage: just search <term>"
    @echo "Example: just search AI-Frontend"

# Open the local read-only file & diff viewer (scripts/shared/view/).
# The service binds the loopback address only, serves read requests only, and
# never writes to the repository being viewed. It stays resident for a fast
# second launch and recycles itself after an idle timeout.
# Usage:
#   just view                    # open straight into the diff (改动) view at the repo root
#   just view <path>             # open into the diff view, focused on a changed file
#   just view --files            # open into the files view instead
#   just view --diff             # diff view (already the default; kept as an explicit flag)
#   just view --stop             # recycle this repository's resident instance
#
# The diff view always lists all three sections (已暂存 / 未暂存 / 未跟踪); there is no
# CLI switch for picking one, and no baseline selector — the working tree is the only
# comparison, divided by the git index.
#
# 这条 recipe 刻意写成普通单行而不是 shebang：`just` 每跑一次 shebang recipe 都要多
# 起一个临时脚本，而复用命中路径有 150ms 的耗时预算（见 launch.py 顶部的说明）。
# 本仓库没有 venv，直接走 PATH 上的 python3。
# `-S`（跳过 site 初始化）同样是冲着这 150ms 去的：入口进程只用标准库与同目录的
# instance.py，服务进程由 launch.py 以不带 `-S` 的方式单独拉起，语法高亮照常可用。
view *args:
    exec python3 -S "{{justfile_directory()}}/scripts/shared/view/launch.py" {{args}}

# Thin alias: open the viewer in the diff view (already the default).
diff *args:
    exec just view --diff {{args}}

# Search blog posts by path/filename or by title in front matter
search term:
    @echo "=== Files matching '{{ term }}' in path ==="
    @find content/post -type f | rg -i -F {{ quote(term) }} || true
    @echo
    @echo "=== Posts with title matching '{{ term }}' ==="
    @rg -i -g '**/index.md' '^title:' content/post 2>/dev/null | rg -i -F {{ quote(term) }} || true
