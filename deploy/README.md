# deploy/ —— 部署辅助

面向**自建服务器**（阿里云 ECS 等）。GitHub Pages 不需要这些。

## 顺序

```bash
# ① 本地：生成上传就绪的站点目录（只挑运行时必需文件，不含构建用的 AYJGW.ttf）
python3 deploy.py                 # → dist/

# ② 上传（把 <IP> 换成 ECS 公网 IP）
rsync -avz --delete dist/ root@<IP>:/var/www/oracletcm/

# ③ 服务器上：配置 nginx（.wasm MIME、gzip、libs 长缓存、80→443 跳转）
sudo bash setup-server.sh oracletcm.com /var/www/oracletcm
```

`setup-server.sh` 是**幂等**的：重复执行只会重写配置并 reload；证书就绪后重跑会自动从
「仅 HTTP」切换到「HTTPS」配置。

## 为什么脚本先写「仅 HTTP」配置

nginx 配置里一旦引用 `ssl_certificate` 而证书文件不存在，`nginx -t` 就会失败、服务起不来。
所以脚本先探测证书：

- 找到证书 → 直接写 HTTPS 配置（含 80→443 跳转）
- 没找到 → 先写仅 HTTP 配置让站点能开，并在输出里提示后续申请证书的路径

## 两个容易误判的点

| 现象 | 真实原因 |
| --- | --- |
| 备案通过前访问超时/被重置 | 阿里云对**未备案域名**拦截 80/443 入站，与 nginx 配置无关 |
| nginx 配好了但仍访问不通 | 阿里云**安全组**未放行 80/443（控制台 → 安全组 → 入方向）。服务器本机防火墙是另一层 |

## 关于 HTTPS

这不是可选项：非 `localhost` 的 HTTP 页面**不是安全上下文**，浏览器不会提供摄像头，
手势功能整个不可用。证书可用阿里云「数字证书管理服务」的免费 DV 证书，下载 nginx 版后放到
`/etc/nginx/ssl/<域名>.pem` 与 `.key`，再重跑脚本。

## 备案通过后怎么做

见 **[POST-FILING.md](POST-FILING.md)** —— 逐步清单，含每步的验证命令、
`certbot` 的真实路径（不在 PATH 里）、以及本次踩到的全部陷阱。

## 已在真实服务器上验证（2026-10-15）

`install-site.sh` 已在目标服务器上跑通并逐项复测：

| 检查 | 结果 |
| --- | --- |
| `oracletcm.com/` | 200 `text/html` |
| `oracletcm.com/gesture3d.html` | 200 `text/html` 1,587,069B |
| `libs/three.min.js` | 200 `text/javascript` |
| `libs/hands_solution_simd_wasm_bin.wasm` | 200 **`application/wasm`** |
| `libs/hand_landmark_full.tflite` | 200 `application/octet-stream` |
| `kylinhealth.com.cn`（既有站点） | 301，未受影响 |
| `nginx -t` | **零警告** |
| gzip | `gesture3d.html` 1,587,069B → **850,945B**（省 46%）；`.wasm` 按 `gzip off` 不压缩 |

### 关于 .wasm 的 MIME：不要照抄网上的写法

常见做法是在 server 块里写 `types { application/wasm wasm; }` + `include /etc/nginx/mime.types;`。
本机（nginx 1.30.4）实测**两者都是多余的，且各自触发一条 `nginx -t` 警告**：

- `/etc/nginx/mime.types` 第 713 行**已内置** `application/wasm wasm;`，
  而 `nginx.conf` 的 **http 层已 include 过它** → 服务器本来就把 .wasm 标成
  `application/wasm`（curl 实测 Content-Type 正确）。
  故 server 块里再声明 → `duplicate extension "wasm"`；
- 再 include 一次 mime.types → `duplicate MIME type "text/html"`。

另外 `gzip_types` 里**不要列 `text/html`** —— 它是 nginx 默认就压缩的类型，
重复列出同样会告警（且并非必要）。

### 两个 nginx 语法陷阱（本次都踩到了）

1. **`if` 不能写在 `server` 块里** —— 只能在 `location` 内。我最初想用
   `if ! grep -q ... ; then types{} fi` 做兼容判断，`nginx -t` 直接报
   `directive "if" has no opening "{"`。
2. **改动必须先 `nginx -t` 通过再 `reload`**，并且脚本要 `set -e` ——
   本次正是靠这一点：`nginx -t` 失败即退出，**没有 reload**，
   所以线上配置始终是好的，回滚只是恢复文件、无需重载。

### 分发通道：git 可用，但大陆网络会抖

- 服务器实测 `raw.githubusercontent.com` **不可达**（60s 0 字节），
  但 `github.com` 可用 —— 首次 `git clone --depth 1`（46MB）仅 **3.4 秒**。
- 然而同一命令随后**连续 4 次失败**（`Failed to connect to github.com port 443
  after 36007 ms`），说明大陆访问 GitHub 存在时段性波动。
- 结论：clone 必须带**重试**；若仓库拉不到，小改动可直接在服务器上就地修补
  （本次的 MIME 修正就是这么做的），不必依赖 GitHub。
