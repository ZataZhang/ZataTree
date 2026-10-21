set positional-arguments

# Show how to use this justfile
default:
    @echo "Usage: just search <term>"
    @echo "Example: just search AI-Frontend"

# Open the shared local file & diff viewer from the sibling zata_code_template repo.
# This follows ../dwms/justfile, so the viewer has one maintained implementation.
# It binds to loopback, supports explicit staging and opening files in the system app,
# and recycles itself after an idle timeout. It does not commit, unstage, or discard changes.
# Usage:
#   just view                    # open straight into the diff (改动) view at the repo root
#   just view <path>             # open into the diff view, focused on a changed file
#   just view --files            # open into the files view instead
#   just view --diff             # diff view (already the default; kept as an explicit flag)
#   just view --stop             # recycle this repository's resident instance
#
# The diff view preserves all three Git change classes (已暂存 / 未暂存 / 未跟踪); there is
# no CLI switch for picking one, and no baseline selector — the working tree is the only
# comparison, divided by the git index.
#
# 这条 recipe 刻意写成普通单行而不是 shebang：`just` 每跑一次 shebang recipe 都要多
# 起一个临时脚本，而复用命中路径有 150ms 的耗时预算（见 launch.py 顶部的说明）。
# 解释器优先直连模板仓库 venv；venv 不存在时用 `uv run --project`。先切到当前仓库目录，
# 让共享入口按当前工作目录定位要查看的仓库。`-S` 跳过入口进程的 site 初始化；服务进程
# 由共享入口单独拉起，会正常加载模板仓库 venv 中的预览与语法高亮依赖。
_view_template_directory := justfile_directory() / "../zata_code_template"
_view_launch_script := _view_template_directory / "scripts/shared/view/launch.py"
_view_python := if os_family() == "windows" { _view_template_directory / ".venv/Scripts/python.exe" } else { _view_template_directory / ".venv/bin/python" }
_view_python_command := if path_exists(_view_python) == "true" { quote(_view_python) } else { "uv run --project " + quote(_view_template_directory) + " --no-sync python" }

view *args:
    cd "{{justfile_directory()}}" && exec {{_view_python_command}} -S "{{_view_launch_script}}" {{args}}

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
