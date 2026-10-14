#!/usr/bin/env python3
# 无缓存静态服务器（开发用，避免改了页面浏览器还吃缓存）
# 用法： python3 serve.py [端口] [--host 地址]    默认 0.0.0.0:8138
import argparse, http.server, socketserver

ap = argparse.ArgumentParser(description="无缓存静态文件服务器")
ap.add_argument("port", nargs="?", type=int, default=8138)
ap.add_argument("--host", default="0.0.0.0", help="默认 0.0.0.0，仅本机用 127.0.0.1")
args = ap.parse_args()

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    # 关掉 keep-alive：浏览器常挂着一个长连接，单线程服务器会被它堵住，
    # 表现为「服务器在监听但请求全部超时」（本项目实际踩过）。
    protocol_version = "HTTP/1.0"

    # libs/ 里的模型与运行时体积很大（约 28MB），但内容几乎不变，
    # 一律禁缓存会让每个访客每次打开都重下 16MB —— 公开部署时这是致命的。
    # 故只对 libs/ 开长缓存，其余（HTML、data/）保持不强缓存以便改动即时生效。
    # 改 libs/ 里文件时把页面顶部的 ASSET_V 加一即可破缓存（见 gesture3d.html）。
    IMMUTABLE_PREFIX = "/libs/"

    def end_headers(self):
        path = self.path.split("?")[0]
        if path.startswith(self.IMMUTABLE_PREFIX):
            # 一年 + immutable：命中缓存时浏览器连请求都不发
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        else:
            # no-cache = 允许存副本但每次校验（有 Last-Modified，改动即时生效）
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()


# 必须用 ThreadingTCPServer：原生 TCPServer 是单线程的，一个卡住的连接
# （keep-alive、被中断的下载、预连接）就会让整个站点停止响应。
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server((args.host, args.port), NoCacheHandler) as httpd:
    print(f"serving no-cache on {args.host}:{args.port}")
    httpd.serve_forever()
