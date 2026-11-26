#!/usr/bin/env python3
import base64
import os
import sys

base = os.path.dirname(os.path.abspath(__file__))
HERBS = {
    "sanqi": ("sanqi_model.glb", "sanqi_model_fallback.js", "SANQI"),
    "baizhi": ("baizhi_model.glb", "baizhi_model_fallback.js", "BAIZHI"),
}
CHUNK = 1_000_000


def build(key):
    src_name, dst_name, prefix = HERBS[key]
    src = os.path.join(base, "libs", src_name)
    dst = os.path.join(base, "libs", dst_name)
    if not os.path.isfile(src):
        sys.exit("缺少 " + src)

    raw = open(src, "rb").read()
    b64 = base64.b64encode(raw).decode("ascii")
    parts = [b64[i:i + CHUNK] for i in range(0, len(b64), CHUNK)]

    with open(dst, "w", encoding="utf-8") as f:
        f.write("/* 自动生成，勿手改。来源: libs/%s\n" % src_name)
        f.write(" * 重新生成: python3 build_model_fallback.py %s\n" % key)
        f.write(" * 用途: file:// 直接打开或 GLB 请求失败时供页面回退加载。 */\n")
        f.write("window.__%s_GLB_BYTES = %d;\n" % (prefix, len(raw)))
        f.write("window.__%s_GLB_B64 =\n" % prefix)
        f.write(" +\n".join('  "' + p + '"' for p in parts))
        f.write(";\n")

    print("已生成 %s（GLB %d 字节 → JS %d 字节）" % (dst, len(raw), os.path.getsize(dst)))


if __name__ == "__main__":
    keys = sys.argv[1:] or ["all"]
    if "all" in keys:
        keys = list(HERBS)
    unknown = [k for k in keys if k not in HERBS]
    if unknown:
        sys.exit("未知药材: %s；可选 %s" % (" ".join(unknown), " ".join(HERBS)))
    for key in keys:
        build(key)
