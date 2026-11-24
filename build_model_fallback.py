#!/usr/bin/env python3
# ============================================================
#  build_model_fallback.py —— 生成三七写实模型的「脚本内嵌」后备副本
#
#  为什么需要它：
#   · 浏览器在 file:// 下禁止 fetch() 读取本地文件（CORS: origin 'null'），
#     直接双击 index.html 时 libs/sanqi_model.glb 会加载失败；
#   · <script src> 不受这条限制，所以把 GLB 转成 Base64 放进 JS，
#     页面在 fetch 失败时动态加载它，写实模型照样能出现。
#
#  用法： python3 build_model_fallback.py
#  产物： libs/sanqi_model_fallback.js（约 13MB，仅 file:// / 加载失败时才请求）
#  注意： 更换 libs/sanqi_model.glb 后必须重跑本脚本，并把页面顶部 ASSET_V 加一
#         （libs/ 是 immutable 长缓存，不加版本号浏览器会继续用旧副本）。
# ============================================================
import base64
import os
import sys

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "libs", "sanqi_model.glb")
dst = os.path.join(base, "libs", "sanqi_model_fallback.js")

if not os.path.isfile(src):
    sys.exit("缺少 " + src)

raw = open(src, "rb").read()
b64 = base64.b64encode(raw).decode("ascii")

# 分块拼接：避免编辑器/工具面对一条 13MB 的超长行，浏览器解析和单个字面量等价
CHUNK = 1_000_000
parts = [b64[i:i + CHUNK] for i in range(0, len(b64), CHUNK)]

with open(dst, "w", encoding="utf-8") as f:
    f.write("/* 自动生成，勿手改。来源: libs/sanqi_model.glb\n")
    f.write(" * 重新生成: python3 build_model_fallback.py（换模型后同时把 ASSET_V 加一）\n")
    f.write(" * 用途: file:// 直接打开或 GLB 请求失败时，供页面回退加载三七写实模型。 */\n")
    f.write("window.__SANQI_GLB_BYTES = %d;\n" % len(raw))
    f.write("window.__SANQI_GLB_B64 =\n")
    f.write(" +\n".join('  "' + p + '"' for p in parts))
    f.write(";\n")

print("✔ 已生成 %s" % dst)
print("  GLB %d 字节 → Base64 %d 字符 → JS %d 字节" % (
    len(raw), len(b64), os.path.getsize(dst)))
