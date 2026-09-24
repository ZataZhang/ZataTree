---
title: Playwright Chromium 在 Docker 内 SIGTRAP 启动崩溃排查实录
description: Dokploy 部署后点击登录触发 Playwright TargetClosedError，最终定位为 useradd -r 没创 /home/appuser，chrome 拿不到可写 HOME 导致 crashpad handler 拿不到 --database 而 exit 1，主进程 IMMEDIATE_CRASH（SIGTRAP）。记录六轮被自己打脸的错误假设链
date: 2026-06-08T15:30:00+08:00
image: images/index/index.png
categories:
    - Platforms_Tools
tags:
    - Docker
    - Browser-Automation
---

## 背景

一个 FastAPI 后端 + Playwright（驱动 Chromium 做爬虫/自动化）的项目，通过 Dokploy 部署到一台 Azure VM（内核 `6.14.0-1017-azure`，Ubuntu 24.04）。前端点登录按钮，后端通过 `launch_persistent_context` 起 Chromium 让用户走 VNC 完成一次性登录。

部署后第一次点登录就报：

```text
TargetClosedError: BrowserType.launch_persistent_context:
Target page, context or browser has been closed
<launched> pid=191
[pid=191][err] chrome_crashpad_handler: --database is required
[pid=191][err] [191:191:...:ERROR:.../socket.cc:120] recvmsg: Connection reset by peer (104)
[pid=191] <process did exit: exitCode=null, signal=SIGTRAP>
```

`chrome_crashpad_handler: --database is required` 看起来像主角，其实只是**遗书**：父 chrome 进程已经 SIGTRAP，crashpad handler 被附带拉起来时没拿到参数，才吐了 usage。先理清这一点才不会被带偏。

下面把六轮被自己打脸的错误假设逐一列出，再讲真正根因。**值得保留的不是答案，是思路**。

## 假设 1：旧 profile 跨版本残留

`docker-compose` 把 `kimi-ppt-browser-profile` 命名卷挂到 `/app/.courier/browser-profiles`。第一反应：上次构建的 Chromium 写下的 profile 文件和这次不兼容，启动 assert。

**结果**：用户说"全新部署，没操作过任何东西"。卷是 fresh 的，假设不成立。

## 假设 2：Docker 默认 seccomp 拦 `clone3`

Chromium 1223 (Playwright ≥ 1.49 bundled) 大量用 `clone3`。老 Docker daemon（≤ 20.10.10）的默认 seccomp profile 直接 EPERM。

修了一行 compose：

```yaml
  kimi-ppt-backend:
    security_opt:
      - seccomp=unconfined
```

**结果**：重新部署 → 同样的 SIGTRAP。排除。

## 假设 3：换系统 Google Chrome stable

既然 bundled chromium 1322 跑不起来，换 Google 官方 deb 装的 `google-chrome-stable` 总行了吧？把 `Dockerfile` 改成从 Google APT 装，`KIMI_SLIDES_BROWSER_CHANNEL=chrome` 让 Playwright 通过 `channel='chrome'` 调它。

**结果**：chrome 一样 SIGTRAP。说明不是 chromium binary 自身的 bug。

## 假设 4：AppArmor 拦 userns

写了一个分层探针脚本进入容器实际查原因。关键输出：

```text
[1] docker inspect
  AppArmorProfile: docker-default
  SecurityOpt:     [seccomp=unconfined]
[2] kernel sysctls
  apparmor_restrict_unprivileged_userns = 1
[4] strace of chrome stable
  chrome 主 (pid 353) sendmsg(fd4, 40 bytes)  → 给 crashpad handler 发 IPC 配置
  crashpad handler (pid 355) execve(...)
  crashpad handler +++ exited with 1 +++
  chrome 主 --- SIGTRAP si_code=SI_KERNEL  ← IMMEDIATE_CRASH(int3)
```

`apparmor_restrict_unprivileged_userns=1` 配合 `docker-default` profile 会让 chrome 创建 user namespace 失败。给 compose 加：

```yaml
  kimi-ppt-backend:
    security_opt:
      - seccomp=unconfined
      - apparmor=unconfined
```

**结果**：AppArmor 是 unconfined 了，chrome 仍然 SIGTRAP。`strace` 显示 crashpad handler 启动后没拿到 `--database=` 参数就退（更详尽的 strace 揭示真正原因——见下），所以 userns 不是真正卡点。**这是被自己打脸的一轮**：加 `apparmor=unconfined` 之后我又跑了一次 strace，发现 crashpad handler 根本没走到 userns 那一步，它在解析 argv 阶段就 fail 了。

> 留这一段不是为了丢脸——是因为这次"加了一行还是没好"教会我：**每加一行配置就重新跑一次 strace 看新输出**，不能凭印象假设前一次 trace 仍然成立。

## 真正根因：HOME 目录不存在

回头看 [4] 那段 strace：

```text
355 (handler) execve args = [...--initial-client-fd=5 --shared-client-connection]
                           ↑ 注意：没有 --database=
355 write(stderr, "chrome_crashpad_handler: --datab...")
355 +++ exited with 1 +++
```

**chrome 主进程传给 crashpad handler 的 argv 里没有 `--database=`**。为什么？因为 chrome 决定 `--database=` 路径的算法是 `~/.config/google-chrome/Crash Reports`，根据 `$HOME` 推。

继续探针：

```text
[2] HOME 探测
  HOME=/home/appuser
  ls -ld /home/appuser → No such file or directory

[3] 同样的 chrome 命令用 root 跑
  <html><head></head><body></body></html>   ← 正常！
```

`Dockerfile` 里有一行：

```dockerfile
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
```

`useradd -r` 创建系统用户，**默认不创 home 目录**。`appuser` 进了 `/etc/passwd` 但 `/home/appuser` 不存在。chrome 拿不到可写 `$HOME` → 不传 `--database=` 给 crashpad handler → handler exit 1 → chrome 主进程检测到 handler init 失败 → `IMMEDIATE_CRASH()` 调 `__builtin_debugtrap()` → SIGTRAP。

root 能跑是因为 `HOME=/root`，目录存在。

**修复（一行 Dockerfile）**：

```dockerfile
RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /home/appuser appuser \
    && mkdir -p /app/logs /app/downloads /app/.courier/browser-profiles \
    && chown -R appuser:appgroup /app /home/appuser
```

`useradd -m -d /home/appuser` 才会真创建 home 目录。

**Dokploy Redeploy（重新 build 镜像，3-5 分钟，不是 9 秒的 hot restart）后，chrome 启动正常。**

## 顺手修了一个 selector bug

chrome 起来后，前端点登录立刻弹"已检测到登录成功"——其实没登录。查代码发现 `sites/kimi-slides.yaml:11` 配的是 `logged_in_selector: ".chat-input-editor"`，而 kimi.com 的未登录落地页**就**有 `.chat-input-editor`，selector 立即命中，`on_login_detected` 被错误 fire。

从 VNC 里看登录后页面才出现的元素：

```html
<div class="user-avatar-container" style="width: 28px; height: 28px;">
  <img class="user-avatar" src="...music_head.png" alt="登月者9246" />
  <span class="user-name">登月者9246</span>
  <div class="membership-upgrade">升级</div>
</div>
```

`membership-upgrade`（"升级"按钮）和 `.user-avatar-container` 都是只在登录后才出现的——是更可靠的 post-auth marker。把 selector 换成 `.user-avatar-container` 即可。

## 5 条复盘

### 1. `chrome_crashpad_handler: --database is required` 是结果不是原因

每次看到这一行都要立刻去找父 chrome 进程的退出信号。`SIGTRAP` / `trap int3` 几乎一定是 Chromium 内部 `IMMEDIATE_CRASH()`。crashpad 那段 usage 是它被附带拉起来时打出来的"遗言"，跟死因无关。

### 2. 剥变量比改 compose 重要

报错涉及：卷 / 权限 / seccomp / X server / GPU / 内核 / CPU 指令 / 缺库 / 容器 runtime / app config / 用户身份。每一条都可能引发同一种症状。写脚本一次性把可控变量全部剥掉（手动跑 chromium、用 `/tmp` 隔离卷、headless 隔离 X、`--no-zygote --single-process` 隔离 sandbox），比改一行 compose 重新部署等结果效率高得多。

特别有价值的一步是 **strace 死前最后那个 syscall**——能直接定位到 `clone3` / `seccomp` / `userfaultfd` / `prctl` 哪一类失败。这一步把"猜容器层问题"变成"看 kernel 在哪一步拒绝"。

### 3. `--no-sandbox` 不等于 sandbox 完全关掉

Chromium 至少有三层 sandbox：setuid sandbox、user-namespace sandbox、seccomp-bpf filter。`--no-sandbox` 主要关掉前两层，仍可能在 seccomp 初始化阶段崩。要全关需要：

```text
--no-sandbox --disable-setuid-sandbox --disable-namespace-sandbox --disable-seccomp-filter-sandbox
```

但这只用于诊断——生产即便有问题也不要靠这个绕。

### 4. bundled chromium 不是万能

Playwright 自带的 Chromium 是 Playwright 团队 patched 过的版本，覆盖矩阵窄于 Google 官方 Chrome stable。Azure / 较新 Hyper-V 内核 / 某些 ARM 宿主**三者叠加**就可能让 bundled chromium 启动崩、而系统 Chrome stable 正常——**反过来**也成立。生产容器优先用 `channel='chrome'` 跑系统 Chrome 更保守。

但！这次我们后来发现"换 Chrome stable"本身**也不是修复**——根因（HOME 缺失）对两个 binary 一视同仁。换 binary 治不了真正的病，只是让症状换了个皮。

### 5. Dockerfile 一行 `-m` 缺失，藏得最深

`useradd -r` 不创 home——这是发行版默认行为，dev 阶段本地跑的时候从来不会触发（Mac 跑 docker 不走 rootfs，mount 行为不一样），CI 测试也跑过（其实没跑过——`just test` 不覆盖 docker build）。这种 bug 只能靠"上 prod 看现象"暴露。

防御：

- Dockerfile 优先用 `adduser`（Debian 系）而不是 `useradd`，`adduser` 默认创 home 且交互友好
- 或者显式 `-m -d /home/xxx` 让意图不依赖隐式默认
- 在 CI 里至少跑一次 `docker build && docker run` 验证 chrome 类应用能起，单纯跑 pytest 不够

## 完整最终改动

- `src/backend/Dockerfile`：`useradd` 加 `-m -d /home/appuser`；`chown` 补 `/home/appuser`
- `docker-compose.dokploy.yml`：`security_opt: [seccomp=unconfined, apparmor=unconfined]`（虽然对 chromium 启动不是必须的，但保险）
- `sites/kimi-slides.yaml`：`login_detection_selector` 从 `.chat-input-editor` 换成 `.user-avatar-container`

## 附录：诊断脚本模式

发现 `strace` 末尾 "死前最后几个 syscall" 价值最高，标准化成模板：

```bash
docker exec "$CONTAINER" sh -c '
  CHROME=/opt/google/chrome/chrome
  rm -rf /tmp/cp /tmp/strace.log
  timeout 5 strace -f -y \
    -e trace=execve,clone,clone3,prctl,seccomp,unshare,ptrace,personality,\
membarrier,userfaultfd,pidfd_open \
    -o /tmp/strace.log \
    "$CHROME" --headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu \
      --user-data-dir=/tmp/cp about:blank >/dev/null 2>&1
  HANDLER_PID=$(grep "execve.*chrome_crashpad_handler" /tmp/strace.log | head -1 | awk "{print \$1}")
  grep "^$HANDLER_PID " /tmp/strace.log | tail -40
'
```

`-y` 会显示 fd 对应的资源；`-f` 跟踪子进程；trace 列表只列我们关心的 syscall 防止输出爆炸。

任何 chromium 启动崩的现场，这套脚本是首选入口。
