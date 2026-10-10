#!/usr/bin/env python3
# 无缓存静态服务器（开发用，避免改了页面浏览器还吃缓存）
# 用法： python3 serve.py [端口] [--host 地址]    默认 0.0.0.0:8138
import argparse, http.server, socketserver

ap = argparse.ArgumentParser(description="无缓存静态文件服务器")
ap.add_argument("port", nargs="?", type=int, default=8138)
ap.add_argument("--host", default="0.0.0.0", help="默认 0.0.0.0，仅本机用 127.0.0.1")
args = ap.parse_args()

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer((args.host, args.port), NoCacheHandler) as httpd:
    print(f"serving no-cache on {args.host}:{args.port}")
    httpd.serve_forever()
