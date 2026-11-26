#!/usr/bin/env bash
# ============================================================
#  install-site.sh —— 在服务器上部署甲骨文站点
#
#  用法（在服务器上执行）：
#     sudo bash install-site.sh                    # 从已克隆的仓库目录部署
#     REPO=/tmp/oracle-src sudo -E bash install-site.sh
#
#  设计前提（本机实测得出，不是通用假设）：
#   · 服务器在大陆，raw.githubusercontent.com 不可达（60s 0 字节），
#     但 github.com 可用（浅克隆 46MB 仅 3.4 秒）→ 故用 git 作为分发通道。
#   · 本机已有 nginx 与 certbot 在服务 既有站点，
#     故本脚本只【新增】一个 server 块，绝不改写或删除既有配置。
#   · 备案通过前不可加域名解析（阿里云限制），也不可签发证书，
#     故证书签发与解析绑定留到备案后由运维步骤完成（见 deploy/README.md）。
#
#  幂等：重复执行只会覆盖站点文件与该站点的 nginx 配置，然后 reload。
# ============================================================
set -euo pipefail

DOMAIN="${DOMAIN:-oracletcm.com}"
WWW="${WWW:-www.${DOMAIN}}"
SITE_ROOT="${SITE_ROOT:-/var/www/oracletcm}"
REPO="${REPO:-}"
CONF="/etc/nginx/conf.d/${DOMAIN}.conf"

# 需要发布的文件：运行时被请求的 11 个 + 两个 fallback + 三味中药模型及后备
# （详见 deploy/README.md 与根 README 的「部署」一节）
LIB_FILES=(
  three.min.js
  hands.js
  hands.binarypb
  hands_solution_simd_wasm_bin.js
  hands_solution_simd_wasm_bin.wasm
  hands_solution_packed_assets.data
  hands_solution_packed_assets_loader.js
  hand_landmark_full.tflite
  # fallback：无 SIMD 的浏览器与 modelComplexity:0 —— 不做兜底会有一批浏览器跑不起来
  hands_solution_wasm_bin.js
  hands_solution_wasm_bin.wasm
  hand_landmark_lite.tflite
  # 中药展厅：三七 / 白芷写实模型 + file:// / GLB 失败时的脚本内嵌后备
  sanqi_model.glb
  sanqi_model_fallback.js
  baizhi_model.glb
  baizhi_model_fallback.js
  # 部位特写右侧的化学结构式线稿
  struct_aconitine.png
  struct_rg1.png
  struct_quercetin.png
  struct_imperatorin.png
  struct_orig_aconitine.png
  struct_orig_rg1.png
  struct_orig_quercetin.png
  struct_orig_imperatorin.png
  structure_data.js
  structure_points_v2.js
)

[ "$(id -u)" -eq 0 ] || { echo "请用 root 或 sudo 执行" >&2; exit 1; }
command -v nginx >/dev/null || { echo "未安装 nginx" >&2; exit 1; }

# ── 定位源目录（仓库根）────────────────────────────────────────────────
if [ -z "$REPO" ]; then
  for c in "$(cd "$(dirname "$0")/.." && pwd)" /tmp/oracle-src /opt/oracle-src "$HOME/oracle-src"; do
    [ -f "$c/gesture3d.html" ] && REPO="$c" && break
  done
fi
[ -n "$REPO" ] && [ -f "$REPO/gesture3d.html" ] || {
  echo "找不到源目录（需含 gesture3d.html）。用 REPO=/path sudo -E bash $0 指定。" >&2; exit 1; }

echo "==> 源目录: $REPO"
echo "==> 域名:   $DOMAIN / $WWW"
echo "==> 站点根: $SITE_ROOT"

# ── 发布文件 ──────────────────────────────────────────────────────────
mkdir -p "$SITE_ROOT/libs"
install -m 644 "$REPO/gesture3d.html" "$SITE_ROOT/gesture3d.html"

# index.html 直接从仓库拷贝：新版是独立扉页（展厅选择 + 备案页脚），
# 不再由脚本生成跳转页，避免线上首页与仓库版本不一致。
install -m 644 "$REPO/index.html" "$SITE_ROOT/index.html"

for f in "${LIB_FILES[@]}"; do
  src="$REPO/libs/$f"
  [ -f "$src" ] || { echo "缺少 $src" >&2; exit 1; }
  install -m 644 "$src" "$SITE_ROOT/libs/$f"
done

# 许可与来源声明随站点发布（公开部署应可查）
for f in LICENSE THIRD-PARTY-NOTICE.md; do
  [ -f "$REPO/$f" ] && install -m 644 "$REPO/$f" "$SITE_ROOT/$f"
done

chown -R root:root "$SITE_ROOT"
echo "==> 已发布 $(du -sh "$SITE_ROOT" | cut -f1) 到 $SITE_ROOT"

# ── nginx：只新增本站点配置，不动既有站点 ────────────────────────────────
# 先探测证书：certbot 签过证书后重跑本脚本会自动切到 HTTPS 配置。
if [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  echo "==> 检测到证书，写入 HTTPS 配置"
  cat > "$CONF" <<NGINX
server {
    listen 80;
    server_name ${DOMAIN} ${WWW};
    return 301 https://\$host\$request_uri;
}
server {
    listen 443 ssl;
    http2 on;
    server_name ${DOMAIN} ${WWW};

    ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    root ${SITE_ROOT};
    index index.html;
    # 此处无需声明 .wasm MIME，也无需 include mime.types：
    # nginx.conf 的 http 层已 include 了 /etc/nginx/mime.types，
    # 其中已含 application/wasm（本机实测见其第 713 行），实测 Content-Type 正确。
    # 若在此重复声明，nginx -t 会报 duplicate extension / duplicate MIME type。

    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/css application/javascript text/javascript application/json;

    # libs/ 首屏约 16MB，长缓存后只在首次付；页面顶部 ASSET_V 可破缓存
    # .glb 模型启用 gzip（约 44MB → 19MB）；其余 libs 仍保持 gzip off
    location ~ ^/libs/.+\.glb\$ {
        gzip on;
        gzip_types model/gltf-binary;
        gzip_comp_level 6;
        gzip_min_length 1024;
        gzip_vary on;
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files \$uri =404;
    }

    location /libs/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        gzip off;                # wasm/tflite 已是压缩格式，再压无益
        try_files \$uri =404;
    }
    location ~ \.html\$ { add_header Cache-Control "no-cache"; }

    client_max_body_size 32m;
}
NGINX
else
  echo "==> 尚无证书，先写入 HTTP 配置（备案通过并签发证书后重跑本脚本会自动切换）"
  cat > "$CONF" <<NGINX
server {
    listen 80;
    server_name ${DOMAIN} ${WWW};

    root ${SITE_ROOT};
    index index.html;
    # 此处无需声明 .wasm MIME，也无需 include mime.types：
    # nginx.conf 的 http 层已 include 了 /etc/nginx/mime.types，
    # 其中已含 application/wasm（本机实测见其第 713 行），实测 Content-Type 正确。
    # 若在此重复声明，nginx -t 会报 duplicate extension / duplicate MIME type。

    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/css application/javascript text/javascript application/json;

    # .glb 模型启用 gzip（约 44MB → 19MB）；其余 libs 仍保持 gzip off
    location ~ ^/libs/.+\.glb\$ {
        gzip on;
        gzip_types model/gltf-binary;
        gzip_comp_level 6;
        gzip_min_length 1024;
        gzip_vary on;
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files \$uri =404;
    }

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

# ── 校验并 reload（既有站点 的站点不受影响）──────────────────────────
nginx -t
systemctl reload nginx

echo
echo "✔ 部署完成: $CONF"
echo "  本地自测（绕过域名与备案，直接指定 Host）："
echo "    curl -s -o /dev/null -w '%{http_code} %{content_type}\\n' -H 'Host: ${DOMAIN}' http://127.0.0.1/gesture3d.html"
echo "    curl -s -o /dev/null -w '%{http_code} %{content_type}\\n' -H 'Host: ${DOMAIN}' http://127.0.0.1/libs/three.min.js"
echo "  站点文件总览:"
find "$SITE_ROOT" -type f | sed 's|^|    |'
