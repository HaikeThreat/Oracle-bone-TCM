#!/usr/bin/env bash
# ============================================================
#  setup-server.sh —— 在阿里云 ECS 上一键配置站点
#  用法（在服务器上，用 root 或 sudo 执行）：
#     sudo bash setup-server.sh oracletcm.com /var/www/oracletcm
#
#  它做的事：装 nginx → 写入站点配置（.wasm MIME、gzip、libs 长缓存、
#  HTTP→HTTPS 跳转）→ 开防火墙 80/443 → 给出后续申请证书的下一步。
#
#  ⚠ 两个前提，脚本会检查并提示：
#   1) 域名 ICP 备案必须已通过 —— 备案前阿里云会拦截 80/443 的入站访问，
#      此时无论怎么配都访问不通，不要误判为配置错误。
#   2) HTTPS 证书需另行申请（阿里云免费 DV 证书或 certbot）。
#      没有证书时 nginx 不会启动（配置里引用了证书路径），
#      故本脚本会先用「仅 HTTP」配置让站点能起来，证书就绪后再切换到完整配置。
# ============================================================
set -euo pipefail

DOMAIN="${1:-oracletcm.com}"
ROOT="${2:-/var/www/oracletcm}"
CONF="/etc/nginx/conf.d/${DOMAIN}.conf"

if [ "$(id -u)" -ne 0 ]; then
  echo "请用 root 或 sudo 执行" >&2
  exit 1
fi

echo "==> 域名: $DOMAIN   站点根: $ROOT"

# 1) 装 nginx
if ! command -v nginx >/dev/null 2>&1; then
  echo "==> 安装 nginx"
  if command -v dnf >/dev/null 2>&1; then dnf install -y nginx
  elif command -v yum >/dev/null 2>&1; then yum install -y nginx
  elif command -v apt-get >/dev/null 2>&1; then apt-get update && apt-get install -y nginx
  else echo "未识别的包管理器，请手动安装 nginx" >&2; exit 1; fi
fi

# 2) 站点目录
mkdir -p "$ROOT"
if [ ! -f "$ROOT/index.html" ]; then
  echo "⚠ $ROOT 下还没有站点文件。请在本地执行 python3 deploy.py，"
  echo "  再把 dist/ 里的内容上传到 $ROOT（例如："
  echo "  rsync -avz --delete dist/ root@<ECS公网IP>:$ROOT/ ）"
fi

# 3) 证书探测：决定用完整 HTTPS 配置还是先起 HTTP
CERT=""
for c in "/etc/nginx/ssl/${DOMAIN}.pem" "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"; do
  [ -f "$c" ] && CERT="$c" && KEY="${c%.pem}.key" && break
done
# certbot 的 key 文件名固定为 privkey.pem，单独处理
if [ -n "$CERT" ] && [ ! -f "${KEY:-}" ]; then
  [ -f "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" ] && KEY="/etc/letsencrypt/live/${DOMAIN}/privkey.pem"
fi

if [ -n "$CERT" ] && [ -f "$KEY" ]; then
  echo "==> 检测到证书: $CERT，写入 HTTPS 配置"
  cat > "$CONF" <<NGINX
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};
    ssl_certificate     ${CERT};
    ssl_certificate_key ${KEY};
    ssl_protocols TLSv1.2 TLSv1.3;

    root ${ROOT};
    index index.html;

    # .wasm 的 MIME 必须显式声明：默认 octet-stream 会让 MediaPipe 走慢速回退
    types { application/wasm wasm; }
    include /etc/nginx/mime.types;

    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/html text/css application/javascript text/javascript application/json;

    # libs/ 首屏约 16MB，开长缓存后只在首次付；页面顶部 ASSET_V 可破缓存
    location /libs/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        gzip off;                # wasm/tflite 已是压缩格式，再压无益
        try_files \$uri =404;
    }
    location ~ \.html\$ { add_header Cache-Control "no-cache"; }

    client_max_body_size 32m;
}
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$host\$request_uri;
}
NGINX
else
  echo "==> 未检测到证书，先写入「仅 HTTP」配置（站点可访问，但手势/摄像头不可用）"
  echo "    证书就绪后重跑本脚本即会自动切换为 HTTPS 配置"
  cat > "$CONF" <<NGINX
server {
    listen 80;
    server_name ${DOMAIN};
    root ${ROOT};
    index index.html;

    types { application/wasm wasm; }
    include /etc/nginx/mime.types;

    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/html text/css application/javascript text/javascript application/json;

    location /libs/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        gzip off;
        try_files \$uri =404;
    }
    location ~ \.html\$ { add_header Cache-Control "no-cache"; }

    client_max_body_size 32m;
}
NGINX
fi

# 4) 防火墙
echo "==> 放行 80/443"
if command -v firewall-cmd >/dev/null 2>&1; then
  firewall-cmd --permanent --add-service=http  >/dev/null 2>&1 || true
  firewall-cmd --permanent --add-service=https >/dev/null 2>&1 || true
  firewall-cmd --reload >/dev/null 2>&1 || true
elif command -v ufw >/dev/null 2>&1; then
  ufw allow 80/tcp  >/dev/null 2>&1 || true
  ufw allow 443/tcp >/dev/null 2>&1 || true
fi
echo "    注意：阿里云安全组也要放行 80/443（控制台 → 安全组 → 入方向）"

# 5) 自检并 reload
nginx -t
systemctl enable nginx >/dev/null 2>&1 || true
systemctl reload nginx 2>/dev/null || systemctl restart nginx

echo
echo "✔ 配置完成：$CONF"
[ -n "$CERT" ] && echo "  访问：https://${DOMAIN}/" || echo "  访问：http://${DOMAIN}/  （尚未启用 HTTPS，摄像头不可用）"
echo
echo "后续："
echo "  · 备案通过后若仍无法访问，先查阿里云安全组是否放行 80/443"
echo "  · 申请免费证书：阿里云「数字证书管理服务」签发后下载 nginx 版，"
echo "    放到 /etc/nginx/ssl/${DOMAIN}.pem 与 .key，然后重跑本脚本"
