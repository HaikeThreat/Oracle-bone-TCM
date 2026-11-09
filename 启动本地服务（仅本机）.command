#!/bin/bash
# 与「启动本地服务.command」相同，但只监听 127.0.0.1，不对局域网暴露。
#
# 什么时候用这个：在咖啡厅、展厅、会议等不可信 Wi-Fi 下。
# 默认那份用的是 0.0.0.0（监听所有网卡），同一局域网内的其他人
# 可以通过 http://你的IP:8138 访问你的电脑 —— 虽然只提供静态文件、
# 且他们打开的页面拿不到你的摄像头权限（摄像头授权是按访问者自己的
# 浏览器给的），但非必要不暴露总是更好的选择。
#
# 注意：127.0.0.1 同样落在 W3C《Secure Contexts》3.1 节规定的
# 127.0.0.0/8 范围内，仍是安全上下文，手势功能完全可用。

set -u

PORT=8138
cd "$(dirname "$0")" || exit 1

PY=$(command -v python3 || echo /usr/bin/python3)
if [ ! -x "$PY" ]; then
  echo "❌ 找不到 python3。请先安装 Python 3（或 Xcode 命令行工具）。"
  echo "按回车键关闭本窗口…"; read -r _; exit 1
fi

show_and_pause() { echo; echo "按回车键关闭本窗口…"; read -r _; }

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  if curl -s -m 3 -o /dev/null "http://localhost:$PORT/gesture3d.html"; then
    echo "ℹ️  端口 $PORT 上已经有服务在跑了，直接打开页面。"
    open "http://localhost:$PORT/gesture3d.html"
    show_and_pause; exit 0
  fi
  echo "⚠️  端口 $PORT 被占用但无响应（通常是 TIME_WAIT 残留）。"
  echo "    请关掉原终端窗口，或等约 1 分钟后重新双击本文件。"
  show_and_pause; exit 1
fi

LOG="/tmp/oracle-serve-$PORT.$$.log"
DELETE_LOG=0
echo "正在启动（仅本机）：python3 serve.py $PORT --host 127.0.0.1"
"$PY" serve.py "$PORT" --host 127.0.0.1 >"$LOG" 2>&1 &
SERVER_PID=$!

# 收尾：杀掉子进程，避免留下孤儿占着端口（否则下次双击会误报"端口被占用"）
cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null
    wait "$SERVER_PID" 2>/dev/null
  fi
  [ "${DELETE_LOG:-0}" = "1" ] && rm -f "$LOG"
  return 0
}
# SIGHUP（关窗口）与 SIGTERM（菜单"停止"）都必须显式接管，否则会留下孤儿进程
trap cleanup EXIT HUP INT TERM

READY=0
for _ in $(seq 1 20); do
  if curl -s -m 2 -o /dev/null "http://localhost:$PORT/gesture3d.html"; then READY=1; break; fi
  sleep 0.5
done

if [ "$READY" != "1" ]; then
  echo "❌ 启动失败，serve.py 的输出如下："
  echo "────────────────────────────────────────"
  cat "$LOG"
  echo "────────────────────────────────────────"
  show_and_pause; exit 1
fi

URL="http://localhost:$PORT/gesture3d.html"
echo "✅ 已就绪（仅本机可访问）：$URL"
open "$URL"
echo
echo "👉 请保持本窗口开着。关掉窗口，服务就停了。"
echo "   要停止服务：在本窗口按 Control-C，或直接关闭窗口。"

# 服务自己退出时清掉日志；异常退出则把日志打出来
DELETE_LOG=1
wait "$SERVER_PID"
CODE=$?
if [ "$CODE" -ne 0 ] && [ "$CODE" -ne 130 ] && [ "$CODE" -ne 143 ]; then
  echo "⚠️  服务异常退出（退出码 $CODE），日志："
  echo "────────────────────────────────────────"
  cat "$LOG" 2>/dev/null
  echo "────────────────────────────────────────"
  show_and_pause
fi
exit 0
