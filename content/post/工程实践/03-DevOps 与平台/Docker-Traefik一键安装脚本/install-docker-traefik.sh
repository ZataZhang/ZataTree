#!/usr/bin/env bash
set -Eeuo pipefail

# Ubuntu/Debian server installer for Docker Engine + Traefik.
#
# Usage:
#   bash install-docker-traefik.sh
#   ACME_EMAIL=you@your-domain.com bash install-docker-traefik.sh
#
# If you do NOT pass ACME_EMAIL, the script installs Traefik with HTTP only
# and skips the Let's Encrypt resolver. You can re-run with a real email
# later to enable HTTPS certificate issuance.
#
# Optional environment variables:
#   TRAEFIK_DIR=/opt/traefik
#   TRAEFIK_NETWORK=traefik
#   TRAEFIK_IMAGE=traefik:v3.7
#   ACME_EMAIL=you@your-domain.com
#   ENABLE_HTTPS_REDIRECT=true|false
#   INSTALL_SAMPLE=true|false
#   WHOAMI_HOST=whoami.example.com

TRAEFIK_DIR="${TRAEFIK_DIR:-/opt/traefik}"
TRAEFIK_NETWORK="${TRAEFIK_NETWORK:-traefik}"
TRAEFIK_IMAGE="${TRAEFIK_IMAGE:-traefik:v3.7}"
# Default is empty on purpose. When empty, the script does NOT write a
# certificatesResolvers block to traefik.yml — Traefik will only serve the
# built-in fallback self-signed cert, which is fine for local dev.
#
# To enable Let's Encrypt you MUST pass a real mailbox:
#   ACME_EMAIL=you@your-domain.com bash install-docker-traefik.sh
#
# Do NOT pass the legacy placeholder "admin@example.com" / "you@example.com":
# Let's Encrypt silently rejects the registration, acme.json is never created,
# and Traefik serves the TRAEFIK DEFAULT CERT to every visitor. If you've
# already done this, fix the running install with the
# "fix-acme-email.sh" companion script in this repo.
ACME_EMAIL="${ACME_EMAIL:-}"
ENABLE_HTTPS_REDIRECT="${ENABLE_HTTPS_REDIRECT:-}"
INSTALL_SAMPLE="${INSTALL_SAMPLE:-false}"
WHOAMI_HOST="${WHOAMI_HOST:-whoami.localhost}"

SUDO=()

log() {
  printf '\n[%s] %s\n' "$(date +'%H:%M:%S')" "$*"
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
}

require_sudo() {
  if [[ "$(id -u)" -eq 0 ]]; then
    SUDO=()
    return
  fi

  command -v sudo >/dev/null 2>&1 || die "请用 root 运行，或先安装 sudo。"
  sudo -v
  SUDO=(sudo)
}

detect_distro() {
  command -v apt-get >/dev/null 2>&1 || die "此脚本只支持 Ubuntu/Debian 的 apt 系统。"
  [[ -r /etc/os-release ]] || die "找不到 /etc/os-release，无法识别系统。"

  # shellcheck disable=SC1091
  . /etc/os-release

  DOCKER_DISTRO="${ID:-}"
  DOCKER_CODENAME="${VERSION_CODENAME:-}"

  if [[ "$DOCKER_DISTRO" == "ubuntu" ]]; then
    DOCKER_CODENAME="${UBUNTU_CODENAME:-$DOCKER_CODENAME}"
  elif [[ "$DOCKER_DISTRO" == "debian" ]]; then
    :
  elif [[ "${ID_LIKE:-}" == *ubuntu* && -n "${UBUNTU_CODENAME:-}" ]]; then
    DOCKER_DISTRO="ubuntu"
    DOCKER_CODENAME="$UBUNTU_CODENAME"
  elif [[ "${ID_LIKE:-}" == *debian* ]]; then
    DOCKER_DISTRO="debian"
  else
    die "当前系统不是官方支持的 Ubuntu/Debian：ID=${ID:-unknown} ID_LIKE=${ID_LIKE:-unknown}"
  fi

  [[ -n "$DOCKER_CODENAME" ]] || die "无法识别发行版 codename，请手动设置 Docker apt 源。"
}

remove_conflicting_docker_packages() {
  local packages=(
    docker.io
    docker-doc
    docker-compose
    docker-compose-v2
    podman-docker
    containerd
    runc
  )
  local installed=()

  for package in "${packages[@]}"; do
    if dpkg -s "$package" >/dev/null 2>&1; then
      installed+=("$package")
    fi
  done

  if ((${#installed[@]} > 0)); then
    log "移除可能冲突的旧 Docker 发行版包：${installed[*]}"
    "${SUDO[@]}" apt-get remove -y "${installed[@]}"
  fi
}

install_docker() {
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    log "Docker 和 Compose 插件已存在，跳过 Docker 安装。"
    return
  fi

  detect_distro
  remove_conflicting_docker_packages

  log "安装 Docker apt 源依赖。"
  "${SUDO[@]}" apt-get update
  "${SUDO[@]}" apt-get install -y ca-certificates curl

  log "添加 Docker 官方 apt 仓库：${DOCKER_DISTRO} ${DOCKER_CODENAME}"
  "${SUDO[@]}" install -m 0755 -d /etc/apt/keyrings
  "${SUDO[@]}" curl -fsSL "https://download.docker.com/linux/${DOCKER_DISTRO}/gpg" -o /etc/apt/keyrings/docker.asc
  "${SUDO[@]}" chmod a+r /etc/apt/keyrings/docker.asc

  local arch
  arch="$(dpkg --print-architecture)"

  "${SUDO[@]}" tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/${DOCKER_DISTRO}
Suites: ${DOCKER_CODENAME}
Components: stable
Architectures: ${arch}
Signed-By: /etc/apt/keyrings/docker.asc
EOF

  log "安装 Docker Engine、Buildx 和 Compose 插件。"
  "${SUDO[@]}" apt-get update
  "${SUDO[@]}" apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  "${SUDO[@]}" systemctl enable --now docker

  if [[ -n "${SUDO_USER:-}" && "${SUDO_USER}" != "root" ]]; then
    "${SUDO[@]}" usermod -aG docker "$SUDO_USER"
    log "已把用户 ${SUDO_USER} 加入 docker 组；重新登录后可不加 sudo 使用 docker。"
  fi
}

resolve_https_redirect_default() {
  if [[ -z "$ENABLE_HTTPS_REDIRECT" ]]; then
    if [[ -n "$ACME_EMAIL" ]]; then
      ENABLE_HTTPS_REDIRECT="true"
    else
      ENABLE_HTTPS_REDIRECT="false"
    fi
  fi

  case "$ENABLE_HTTPS_REDIRECT" in
    true|false) ;;
    *) die "ENABLE_HTTPS_REDIRECT 只能是 true 或 false。" ;;
  esac
}

create_traefik_network() {
  if "${SUDO[@]}" docker network inspect "$TRAEFIK_NETWORK" >/dev/null 2>&1; then
    log "Docker 网络 ${TRAEFIK_NETWORK} 已存在。"
    return
  fi

  log "创建 Docker 网络：${TRAEFIK_NETWORK}"
  "${SUDO[@]}" docker network create "$TRAEFIK_NETWORK"
}

write_traefik_files() {
  resolve_https_redirect_default

  log "写入 Traefik 配置到 ${TRAEFIK_DIR}"
  "${SUDO[@]}" mkdir -p "${TRAEFIK_DIR}/dynamic" "${TRAEFIK_DIR}/letsencrypt" "${TRAEFIK_DIR}/examples"
  "${SUDO[@]}" touch "${TRAEFIK_DIR}/letsencrypt/acme.json"
  "${SUDO[@]}" chmod 600 "${TRAEFIK_DIR}/letsencrypt/acme.json"

  "${SUDO[@]}" tee "${TRAEFIK_DIR}/.env" >/dev/null <<EOF
TRAEFIK_IMAGE=${TRAEFIK_IMAGE}
EOF

  "${SUDO[@]}" tee "${TRAEFIK_DIR}/docker-compose.yml" >/dev/null <<EOF
services:
  traefik:
    image: \${TRAEFIK_IMAGE}
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    networks:
      - ${TRAEFIK_NETWORK}
    ports:
      - "80:80"
      - "443:443"
      - "127.0.0.1:8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./dynamic:/etc/traefik/dynamic:ro
      - ./letsencrypt:/letsencrypt
    healthcheck:
      test: ["CMD", "traefik", "healthcheck", "--ping"]
      interval: 30s
      timeout: 5s
      retries: 3

networks:
  ${TRAEFIK_NETWORK}:
    name: ${TRAEFIK_NETWORK}
    external: true
EOF

  "${SUDO[@]}" tee "${TRAEFIK_DIR}/traefik.yml" >/dev/null <<EOF
api:
  dashboard: true
  insecure: true

log:
  level: INFO

accessLog: {}

ping: {}

entryPoints:
  web:
    address: ":80"
EOF

  if [[ "$ENABLE_HTTPS_REDIRECT" == "true" ]]; then
    "${SUDO[@]}" tee -a "${TRAEFIK_DIR}/traefik.yml" >/dev/null <<'EOF'
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true
EOF
  fi

  "${SUDO[@]}" tee -a "${TRAEFIK_DIR}/traefik.yml" >/dev/null <<EOF
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: "${TRAEFIK_NETWORK}"
  file:
    directory: "/etc/traefik/dynamic"
    watch: true
EOF

  if [[ -n "$ACME_EMAIL" ]]; then
    "${SUDO[@]}" tee -a "${TRAEFIK_DIR}/traefik.yml" >/dev/null <<EOF

certificatesResolvers:
  letsencrypt:
    acme:
      email: "${ACME_EMAIL}"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: web
EOF
  fi

  write_whoami_example
}

write_whoami_example() {
  if [[ -n "$ACME_EMAIL" ]]; then
    "${SUDO[@]}" tee "${TRAEFIK_DIR}/examples/whoami.compose.yml" >/dev/null <<EOF
services:
  whoami:
    image: traefik/whoami:v1.11
    restart: unless-stopped
    networks:
      - ${TRAEFIK_NETWORK}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(\`${WHOAMI_HOST}\`)"
      - "traefik.http.routers.whoami.entrypoints=websecure"
      - "traefik.http.routers.whoami.tls=true"
      - "traefik.http.routers.whoami.tls.certresolver=letsencrypt"

networks:
  ${TRAEFIK_NETWORK}:
    external: true
EOF
  else
    "${SUDO[@]}" tee "${TRAEFIK_DIR}/examples/whoami.compose.yml" >/dev/null <<EOF
services:
  whoami:
    image: traefik/whoami:v1.11
    restart: unless-stopped
    networks:
      - ${TRAEFIK_NETWORK}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(\`${WHOAMI_HOST}\`)"
      - "traefik.http.routers.whoami.entrypoints=web"

networks:
  ${TRAEFIK_NETWORK}:
    external: true
EOF
  fi
}

start_traefik() {
  log "启动 Traefik。"
  "${SUDO[@]}" docker compose \
    --env-file "${TRAEFIK_DIR}/.env" \
    -f "${TRAEFIK_DIR}/docker-compose.yml" \
    up -d
}

install_sample_if_requested() {
  [[ "$INSTALL_SAMPLE" == "true" ]] || return

  log "启动 whoami 示例服务：${WHOAMI_HOST}"
  "${SUDO[@]}" docker compose \
    -f "${TRAEFIK_DIR}/examples/whoami.compose.yml" \
    -p whoami \
    up -d
}

print_summary() {
  cat <<EOF

完成。

Traefik 配置目录：
  ${TRAEFIK_DIR}

常用命令：
  sudo docker compose --env-file ${TRAEFIK_DIR}/.env -f ${TRAEFIK_DIR}/docker-compose.yml ps
  sudo docker compose --env-file ${TRAEFIK_DIR}/.env -f ${TRAEFIK_DIR}/docker-compose.yml logs -f
  sudo docker compose --env-file ${TRAEFIK_DIR}/.env -f ${TRAEFIK_DIR}/docker-compose.yml restart

Dashboard 默认只监听服务器本机：
  http://127.0.0.1:8080/dashboard/

远程查看 dashboard 可用 SSH 端口转发：
  ssh -L 8080:127.0.0.1:8080 user@server

示例服务配置已生成：
  ${TRAEFIK_DIR}/examples/whoami.compose.yml

EOF

  if [[ -z "$ACME_EMAIL" ]]; then
    cat <<EOF
提示：本次没有传 ACME_EMAIL，所以还没有启用 Let's Encrypt 证书解析器。
  - 当前 Traefik 只能提供 HTTP（80 端口），HTTPS 会返回自签证书。
  - 想启用真证书，先把 DNS 解析指到本机，再重跑：
      ACME_EMAIL=you@your-domain.com bash $(basename "$0")
    脚本是幂等的，会自动追加 certificatesResolvers 段并重启 Traefik。

EOF
  else
    cat <<EOF
Let's Encrypt 证书解析器已启用（ACME_EMAIL=${ACME_EMAIL}）。
  - DNS 必须先把要签发的域名解析到本机，否则 LE HTTP challenge 拿不到 80。
  - 第一个外部 HTTPS 请求触发后，Traefik 会自动向 LE 申请证书（通常 30 秒内）。
  - 想看 LE 流程：sudo docker logs -f \$(sudo docker ps -q --filter ancestor=${TRAEFIK_IMAGE})
  - 证书存放在 ${TRAEFIK_DIR}/letsencrypt/acme.json，Traefik 自动续期。
  - 如果浏览器一直显示"此网站的证书无效"，确认 traefik.yml 里 email 字段没被误改成占位。

EOF
  fi
}

main() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi

  require_sudo

  # Fail fast if the user passed a known placeholder email. Let's Encrypt
  # silently rejects registrations with these, the cert never gets issued,
  # and Traefik falls back to its default self-signed cert (which browsers
  # mark as "invalid"). Reject up front with a clear pointer to the fix.
  if [[ -n "$ACME_EMAIL" ]]; then
    if [[ "$ACME_EMAIL" =~ @(example\.com|example\.org|example\.net|localhost)$ ]]; then
      die "ACME_EMAIL='$ACME_EMAIL' 看起来是占位邮箱。Let's Encrypt 不会接受 example.com / localhost 等保留域名，会导致证书申请失败、浏览器报'此网站的证书无效'。请传一个真实邮箱，例如 ACME_EMAIL=you@your-domain.com"
    fi
    if ! [[ "$ACME_EMAIL" =~ ^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$ ]]; then
      die "ACME_EMAIL='$ACME_EMAIL' 格式不像合法邮箱。"
    fi
  fi

  install_docker
  create_traefik_network
  write_traefik_files
  start_traefik
  install_sample_if_requested
  print_summary
}

main "$@"
