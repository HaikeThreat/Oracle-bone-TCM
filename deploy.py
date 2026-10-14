#!/usr/bin/env python3
# ============================================================
#  deploy.py —— 生成「上传就绪」的站点目录
#  用法： python3 deploy.py [输出目录]        默认 dist/
#
#  为什么不直接上传整个仓库：
#   · libs/ 共 28MB，但运行时只请求其中 8 个文件；另外有个 AYJGW.ttf（4.2MB）
#     纯粹是构建时才用的完整字体（页面内嵌的是 base64 子集），传上去毫无用处。
#   · data/、*.py、docs/、.git/ 都不该出现在站点根目录（会被直接下载）。
#
#  ⚠ 有两类文件「没被请求」但**必须保留**，脚本会显式校验它们存在：
#   · hands_solution_wasm_bin.{js,wasm}（非 SIMD）—— 旧浏览器 fallback，
#     libs/hands.js 会探测 SIMD 支持后在两个变体间二选一，删了就有一批浏览器跑不起来。
#   · hand_landmark_lite.tflite —— modelComplexity:0 时用的备用模型。
# ============================================================
import os
import shutil
import sys

base = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "dist")

# 站点根文件
ROOT_FILES = ["index.html", "gesture3d.html"]

# 运行时需要 + 必须保留的 fallback（见上方说明）
LIB_FILES = [
    "three.min.js",
    "hands.js",
    "hands.binarypb",
    "hands_solution_simd_wasm_bin.js",
    "hands_solution_simd_wasm_bin.wasm",
    "hands_solution_packed_assets.data",
    "hands_solution_packed_assets_loader.js",
    "hand_landmark_full.tflite",
    # —— 以下为 fallback，体积不小但删不得 ——
    "hands_solution_wasm_bin.js",
    "hands_solution_wasm_bin.wasm",
    "hand_landmark_lite.tflite",
]

missing = [f for f in ROOT_FILES if not os.path.isfile(os.path.join(base, f))]
missing += [f for f in LIB_FILES if not os.path.isfile(os.path.join(base, "libs", f))]
if missing:
    sys.exit("缺少必需文件: " + " ".join(missing))

if os.path.exists(out):
    shutil.rmtree(out)
os.makedirs(os.path.join(out, "libs"))

total = 0
for f in ROOT_FILES:
    src = os.path.join(base, f)
    shutil.copy2(src, os.path.join(out, f))
    total += os.path.getsize(src)
for f in LIB_FILES:
    src = os.path.join(base, "libs", f)
    shutil.copy2(src, os.path.join(out, "libs", f))
    total += os.path.getsize(src)

# 许可与来源声明一并随站点发布（公开部署时应可查）
extra = 0
for f in ("LICENSE", "THIRD-PARTY-NOTICE.md", "README.md"):
    p = os.path.join(base, f)
    if os.path.isfile(p):
        shutil.copy2(p, os.path.join(out, f))
        extra += 1

print(f"✔ 已生成站点目录: {out}")
print(f"  文件 {len(ROOT_FILES) + len(LIB_FILES) + extra} 个，合计 {total / 1024 / 1024:.1f} MB")
print(f"  （仓库 libs/ 为 {sum(os.path.getsize(os.path.join(base,'libs',f)) for f in os.listdir(os.path.join(base,'libs')) if os.path.isfile(os.path.join(base,'libs',f))) / 1024 / 1024:.1f} MB，"
      f"未纳入 AYJGW.ttf —— 它仅供 build_glyphs.py 构建时子集化）")
print()
print("  下一步：把该目录内容上传到服务器站点根，并按 README「部署」一节配置 nginx")
print("  （务必配 HTTPS —— 非 localhost 的 HTTP 下浏览器不提供摄像头）")
