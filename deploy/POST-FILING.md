# 备案通过后的收尾清单

`oracletcm.com` 的站点**已经部署完成并验证通过**，唯一卡住的是 ICP 备案。
本文件记录备案通过后要做的每一步，以及每步的**验证方法**与**已知陷阱**。

> 当前状态（2026-10-15 实测）
>
> | 项 | 状态 |
> | --- | --- |
> | 站点文件 | `/var/www/oracletcm/`（26MB，17 个文件）已就位 |
> | ⚠ **站点文件里的代码版本** | **落后，必须先传**：服务器那份是 2026-10-15 00:42 上传的；此后本地又改了 8 个提交（`52cd3ba..4ab4304`）。**别把"文件已就位"当成"内容是最新的"** |
> | 本地待上传产物 | `dist/`（2026-10-15 10:56 重建，16 文件 25.4MB，`gesture3d.html` 与源文件逐字节一致）已就绪 |
> | nginx 配置 | `/etc/nginx/conf.d/oracletcm.com.conf`，`nginx -t` **零警告** |
> | 服务器本机自测 | `/`、`gesture3d.html`、`three.min.js`、`hands_solution_simd_wasm_bin.wasm` 全部 **200**，wasm 的 Content-Type 为 `application/wasm` |
> | gzip | `gesture3d.html` 1,587,069B → **850,945B**（省 46%）；`.wasm` 按 `gzip off` 不压缩 |
> | 既有站点 `kylinhealth.com.cn` | **未受影响** |
> | DNS 解析记录 | **0 条** ← 备案后才允许添加 |
> | 证书 | **未签** ← ACME 需要 80 端口可公网响应 |
> | 安全组 | 已放行 **80 / 443**（无需改动） |

## 为什么现在访问不了（不是配置问题）

从公网请求会拿到 **403**，响应头 `Server: Beaver`，页面内容是
`Non-compliance ICP Filing` 并跳转到阿里云备案提示页。

**这是阿里云接入层的拦截，发生在请求到达你的 nginx 之前**：

| 请求来源 | 结果 |
| --- | --- |
| 服务器本机 `curl -H 'Host: oracletcm.com' http://127.0.0.1/` | **200**（不经接入层） |
| 公网 `curl -H 'Host: oracletcm.com' http://47.95.12.207/` | **403**（被接入层拦下） |
| 公网用已备案域名 `Host: kylinhealth.com.cn` | **301**（直达 nginx） |

所以**不要怀疑服务器配置**。

---

## 步骤 0：先把最新代码传上去（其余步骤的前置）

服务器上那份是 2026-10-15 00:42 的版本，**不含当天随后的 8 个修复**：

```
4ab4304  右上角胶囊中轴线与标题对齐
b2f4104  补上唯一缺失的释义 + 卡片字头不再回退宋体
6002261  待机巡字「两个字之间隔 40~50 秒」（换字把自己关掉了 + 空歇改到散开后）
081d778  手势控制窗格下移 10px
987e1d0  右上角对调（胶囊在上、参数在下）
f794a8f  「点条目列表会动一下」：滚动锚定加错元素 + 重建时滚动条消失
2bccdc9  字形卡片统一等高 + 简介垂直居中
58c7536  字形列表密度（简介最多两行、不等高）
```

```bash
python3 deploy.py                                   # 本地重建 dist/（幂等）
rsync -avz --delete dist/ root@47.95.12.207:/var/www/oracletcm/
```

**验证**：服务器上比对大小（本地 `dist/gesture3d.html` 应为 `1604529` 字节）：

```bash
ls -la /var/www/oracletcm/gesture3d.html
grep -c "scrollbar-gutter:stable\|translateY(-3px)\|OracleGlyphFont" /var/www/oracletcm/gesture3d.html
# 三个都应 ≥1；若为 0 说明还是旧版
```

之后再按下面步骤 1（DNS）→ 2（证书）→ 3（可选：重跑 install-site.sh）→ 4（四层验证）→ 5（回归既有站点）走。

## 步骤 1：加 DNS 解析（备案通过后立刻做）

在阿里云 DNS 控制台，或直接用 CLI：

```bash
# 裸域
aliyun alidns AddDomainRecord --DomainName oracletcm.com \
  --RR @ --Type A --Value 47.95.12.207 --TTL 600
# www
aliyun alidns AddDomainRecord --DomainName oracletcm.com \
  --RR www --Type A --Value 47.95.12.207 --TTL 600
```

TTL 用 **600**（10 分钟）：解析刚开始可能要调整，短 TTL 便于回滚。

**验证**：等 1–2 分钟后

```bash
nslookup oracletcm.com 223.5.5.5        # 应返回 47.95.12.207
```

## 步骤 2：签发证书

关键事实（已实测）：`certbot` 装在 **`/opt/certbot/bin/certbot`（5.8.0）**，
**不在 PATH 里**，直接敲 `certbot` 会 command not found。
续期已由 `/etc/cron.d/certbot-renew` 覆盖（每天 3:14 与 15:14，带
`--deploy-hook "systemctl reload nginx"`），所以**新证书也会自动续期，无需另外配**。

```bash
/opt/certbot/bin/certbot --nginx \
  -d oracletcm.com -d www.oracletcm.com \
  --non-interactive --agree-tos --redirect \
  --reuse-account a62c39721e7805162d6d75f6abb22524
```

- `--reuse-account` 复用已有 ACME 账号（避免新建账号触发速率限制）
- `--redirect` 让 certbot 自己加 80→443 跳转
- certbot 会自动改写 `oracletcm.com.conf` 里的 server 块，**不会动 kylinhealth**

**验证**：

```bash
/opt/certbot/bin/certbot certificates          # 应列出 oracletcm.com，有效期约 90 天
openssl x509 -in /etc/letsencrypt/live/oracletcm.com/fullchain.pem \
  -noout -subject -dates -ext subjectAltName
```

## 步骤 3：重跑部署脚本（可选，但推荐）

`deploy/install-site.sh` 会**先探测证书**：检测到证书就写 HTTPS 配置，否则写 HTTP 配置。
若步骤 2 用 `--nginx` 已自动配好，这一步可跳过；若想用脚本里那份更完整的配置
（含 `libs/` 长缓存、gzip 参数），就重跑一次：

```bash
REPO=/tmp/oracle-src bash /tmp/oracle-src/deploy/install-site.sh
```

> 服务器上拉取仓库有坑：`raw.githubusercontent.com` **不可达**，
> `github.com` 可用但**时通时断**（实测首测 clone 46MB 仅 3.4 秒，
> 随后连续 4 次连接超时）。所以脚本里的 clone 必须带重试；
> 小改动建议直接在服务器上改，别依赖 GitHub。

**验证**：

```bash
nginx -t                       # 必须 successful 且无 error
systemctl reload nginx
```

> ⚠️ **顺序不可颠倒**：一定要 `nginx -t` 通过再 `reload`。
> 曾用 `if` 指令做条件判断导致配置语法错误 —— 因为 `if` **不允许写在 `server` 块里**
> （只能在 `location` 内）。当时正是靠「先校验、失败即退出」保住了线上配置。

## 步骤 4：四层验证

```bash
# ① 接入层是否放行
curl -sI https://oracletcm.com/ | head -3

# ② 关键资源与 MIME
for p in / /gesture3d.html /libs/three.min.js /libs/hands_solution_simd_wasm_bin.wasm; do
  curl -s -o /dev/null -w "%{http_code}  %{content_type}  $p\n" "https://oracletcm.com$p"
done
# .wasm 必须是 application/wasm，否则 MediaPipe 会走慢速回退

# ③ 压缩是否生效
curl -s -o /dev/null -w "%{size_download}\n" -H 'Accept-Encoding: gzip' https://oracletcm.com/gesture3d.html
# 应接近 850945，而不是 1587069

# ④ 缓存头
curl -sI https://oracletcm.com/libs/three.min.js | grep -i cache-control
# 应为 public, max-age=31536000, immutable
```

**最后必须用真实浏览器验证摄像头**：打开 `https://oracletcm.com/`，
点「🎥 手势控制」，确认左下角骨架出现、手势能聚形。

> 这一步不能省。HTTP 下 `navigator.mediaDevices` 是 `undefined`
> （实测 `isSecureContext: false` → 浏览器直接移除该 API），
> 页面会提示「摄像头不可用…已回退鼠标模式」。只有 HTTPS 才可用。

## 步骤 5：回归确认既有站点

```bash
curl -sI https://kylinhealth.com.cn/ | head -3      # 应仍正常
ls -la /etc/nginx/conf.d/                            # 两个 .conf 各自独立
```

---

## 已知陷阱汇总

| 陷阱 | 说明 |
| --- | --- |
| `certbot` 不在 PATH | 必须用全路径 `/opt/certbot/bin/certbot` |
| `if` 不能写在 `server` 块 | 只能在 `location` 内，否则 `nginx -t` 报 `directive "if" has no opening "{"` |
| 改配置必须先校验后 reload | `set -e` + `nginx -t && systemctl reload`，失败就不要 reload |
| `.wasm` MIME 不要照抄网上写法 | 本机 `mime.types` 已内置 wasm 且 http 层已 include，重复声明会告警 |
| `gzip_types` 不要列 `text/html` | 它是 nginx 默认压缩类型，重复列出会告警 |
| `http2` 写法 | 用 `http2 on;`；`listen ... http2` 已废弃并会告警（实测） |
| 服务器拉 GitHub 会抖 | clone 需重试；`raw.githubusercontent.com` 完全不可达 |
| 备案前不要试图用 hosts 绕过 | 阿里云拦的是**公网请求的域名**，本机绑 hosts 依然 403 |

## 顺带一提（与本站无关）

安全组里 **16909 端口对 `0.0.0.0/0` 开放**，那是 OpenClaw gateway。
若不需要公网访问，建议在安全组里收紧 —— 它目前是暴露状态。
