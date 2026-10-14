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
