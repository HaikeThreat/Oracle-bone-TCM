#!/usr/bin/env python3
# ============================================================
#  add_glyphs.py —— 往精选字库里加字（人工编排层）
#  用法： python3 add_glyphs.py 字1 字2 字3 ...
#  例：   python3 add_glyphs.py 牛 虎 鹿
#  前提： 字必须在 data/oracle_glyphs_full.json 中（已释甲骨文字表）
#
#  职责：只负责把条目并入 data/curated_glyphs.json（唯一的权威数据源），
#        字体子集化与页面注入全部交给 build_glyphs.py。
#        之所以这样分工：早期版本自己解析页面、自己拼条目、自己子集化，
#        与 build_glyphs.py 形成两条并行实现 —— 加的字不带 curated 标记
#        （不进待机巡字池），也不写回 curated_glyphs.json（下次全量重建即丢失）。
#        收敛到单一数据源后，这两个问题从根上消失。
# ============================================================
import json
import os
import subprocess
import sys

chars = list(dict.fromkeys(sys.argv[1:]))          # 去重且保序
if not chars:
    sys.exit("用法: python3 add_glyphs.py 字1 字2 ...")

base = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base, "data", "oracle_glyphs_full.json")
cur_path = os.path.join(base, "data", "curated_glyphs.json")

db = {}
for g in json.load(open(db_path, encoding="utf8")):
    db.setdefault(g["ch"], g)                      # 同字头多行时取首行
missing = [c for c in chars if c not in db]
if missing:
    sys.exit(f"数据库中不存在: {' '.join(missing)}（该字甲骨文未收录）")

cur = json.load(open(cur_path, encoding="utf8"))
skipped = [c for c in chars if c in cur]
todo = [c for c in chars if c not in cur]
if not todo:
    sys.exit("全部已在精选字库中，无需添加")

for c in todo:
    g = db[c]
    cur[c] = {
        "ch": c,
        "code": g["code"],
        "curated": True,                           # 手工加入者即精选：进入待机巡字池
        "py": (g.get("pinyin") or "").replace("'", ""),
        "tag": g.get("tag") or "甲骨文·已录入",
        "intro": g.get("intro") or "",
    }
json.dump(cur, open(cur_path, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"精选字库 {len(cur)} 字: 新增 {' '.join(todo)}"
      + (f"，跳过已有 {' '.join(skipped)}" if skipped else ""))

no_intro = [c for c in todo if not cur[c]["intro"]]
if no_intro:
    print("⚠ 以下字暂无介绍文字（用的是字表默认文案），稍后可在 data/curated_glyphs.json 里补充：",
          " ".join(no_intro))

# 交给唯一的构建实现：重子集化字体 + 注入页面 + 刷新别名表与计数
r = subprocess.run([sys.executable, os.path.join(base, "build_glyphs.py")], cwd=base)
if r.returncode != 0:
    sys.exit(f"build_glyphs.py 失败（退出码 {r.returncode}）")
print("✔ 刷新页面即可使用新字")
