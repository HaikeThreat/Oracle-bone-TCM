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

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Connection", "close")
        super().end_headers()


# 必须用 ThreadingTCPServer：原生 TCPServer 是单线程的，一个卡住的连接
# （keep-alive、被中断的下载、预连接）就会让整个站点停止响应。
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server((args.host, args.port), NoCacheHandler) as httpd:
    print(f"serving no-cache on {args.host}:{args.port}")
    httpd.serve_forever()
