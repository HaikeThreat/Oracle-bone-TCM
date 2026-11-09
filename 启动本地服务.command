#!/bin/bash
# 双击即可启动本地预览服务。
#
# 为什么需要它：摄像头 API 只在「安全上下文」里存在。按 W3C《Secure Contexts》
# 规范 3.1 节，host 为 localhost 或 127.0.0.1/8 的源被视为「潜在可信」，
# 所以 http://localhost:8138 是安全上下文，手势功能可用；
# 而 file:// 双击打开虽然也被规范视为可信，但 Safari 会禁止 fetch 本地 wasm
# （报错只有一句 "Load failed"），故必须经 HTTP 打开。
#
# 用法：双击本文件。会自动切到本目录、检测端口、起服务并打开浏览器。
# 保持本终端窗口开着 —— 关掉窗口服务就停了。

set -u

PORT=8138
cd "$(dirname "$0")" || exit 1

# Python 解释器：优先 python3，回落到 /usr/bin/python3（macOS 自带）
PY=$(command -v python3 || echo /usr/bin/python3)
if [ ! -x "$PY" ]; then
  echo "❌ 找不到 python3。请先安装 Python 3（或 Xcode 命令行工具）。"
  echo "按回车键关闭本窗口…"; read -r _; exit 1
fi

show_and_pause() { echo; echo "按回车键关闭本窗口…"; read -r _; }

# ── 端口已被占用：不要重复启动 ────────────────────────────────
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  # 能正常响应说明服务已在跑；不响应则多是上次被杀后的 TIME_WAIT 残留
  if curl -s -m 3 -o /dev/null "http://localhost:$PORT/gesture3d.html"; then
    echo "ℹ️  端口 $PORT 上已经有服务在跑了，直接打开页面。"
    open "http://localhost:$PORT/gesture3d.html"
    echo "（无需重复启动。若要重启：先关掉原来那个终端窗口。）"
    show_and_pause; exit 0
  fi
  echo "⚠️  端口 $PORT 被占用但无响应（通常是上次中断留下的 TIME_WAIT）。"
  echo "    占用进程："
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN | tail -n +2 | sed 's/^/      /'
  echo "    处理办法：关掉原终端窗口，或等待约 1 分钟后重新双击本文件。"
  show_and_pause; exit 1
fi

# ── 启动服务 ──────────────────────────────────────────────────
LOG="/tmp/oracle-serve-$PORT.$$.log"
DELETE_LOG=0
echo "正在启动：python3 serve.py $PORT"
"$PY" serve.py "$PORT" >"$LOG" 2>&1 &
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
# 注意：bash 只在「正常退出」和收到已 trap 的信号时才执行 EXIT trap。
# 关终端窗口发的是 SIGHUP、菜单里的"停止"常发 SIGTERM —— 两者都必须显式接管，
# 否则会留下「python 还在跑、但你已经看不到那个窗口」的孤儿进程。
trap cleanup EXIT HUP INT TERM

# ── 等待就绪（最多约 10 秒）──────────────────────────────────
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
echo "✅ 已就绪：$URL"
echo "   （左下角出现手部骨架 = 手势已生效；没有摄像头会自动回退鼠标模式）"
open "$URL"

echo
echo "👉 请保持本窗口开着。关掉窗口，服务就停了。"
echo "   要停止服务：在本窗口按 Control-C，或直接关闭窗口。"

# 服务自己退出（正常停止 / 崩溃）时清掉日志；异常退出则把日志打出来
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
