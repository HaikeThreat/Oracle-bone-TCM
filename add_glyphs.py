#!/usr/bin/env python3
# ============================================================
#  add_glyphs.py —— 向页面添加甲骨文字（从数据库取码位重建字体子集）
#  用法： python3 add_glyphs.py 字1 字2 字3 ...
#  例：   python3 add_glyphs.py 牛 虎 鹿
#  前提： 字必须在 data/oracle_glyphs_full.json 中（1530 已释甲骨文）
#         libs/AYJGW.ttf 为完整原始字体（子集化源）
# ============================================================
import json, re, base64, sys, os
from fontTools import subset
from fontTools.ttLib import TTFont

chars = list(sys.argv[1:])
if not chars: sys.exit("用法: python3 add_glyphs.py 字1 字2 ...")

base = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base, "data", "oracle_glyphs_full.json")
db = {g["ch"]: g["code"] for g in json.load(open(db_path))}
missing = [c for c in chars if c not in db]
if missing: sys.exit(f"数据库中不存在: {' '.join(missing)}（该字甲骨文未收录）")

# 当前页面字库 + 去重追加
html = open(os.path.join(base, "gesture3d.html"), encoding="utf8").read()
pairs = re.findall(r"\{ ch: '([^']+)', code: 'U([0-9A-F]+)'", html)
cur = {ch: "U" + c for ch, c in pairs}
skipped = [c for c in chars if c in cur]
for c in skipped: chars.remove(c)
if not chars: sys.exit("全部已在字库中，无需添加")
for c in chars: cur[c] = db[c]
print(f"字库 → {len(cur)} 字: 新增 {' '.join(chars)}" + (f"，跳过已有 {' '.join(skipped)}" if skipped else ""))

# 字体子集化（源字体在 libs/AYJGW.ttf）
src_font = os.path.join(base, "libs", "AYJGW.ttf")
if not os.path.exists(src_font): sys.exit(f"找不到原始字体 {src_font}")
text = "".join(chr(int(c[1:], 16)) for c in cur.values())
opts = subset.Options(); opts.layout_features = []; opts.hinting = False; opts.desubroutinize = True
f = subset.load_font(src_font, opts)
s = subset.Subsetter(options=opts); s.populate(text=text); s.subset(f)
tmp = "/tmp/oracle_subset_tmp.ttf"
f.save(tmp)
print(f"子集字体: {os.path.getsize(tmp)} bytes")

# 硬校验：解码回读，全部码位必须在 cmap
chk = TTFont(tmp).getBestCmap()
miss = [c for c in cur.values() if int(c[1:], 16) not in chk]
assert not miss, f"子集缺字: {miss}"

b64 = base64.b64encode(open(tmp, 'rb').read()).decode()
# chip 条目（tag/intro 从介绍库读取，缺介绍的列出提醒）
intros_path = os.path.join(base, "data", "intros.json")
intros = json.load(open(intros_path)) if os.path.exists(intros_path) else {}
chip_entries = ""
need_intro = []
for c in chars:
    info = intros.get(c) or {}
    tag = info.get("tag") or "甲骨文·已录入"
    intro = info.get("intro") or ""
    if not intro: need_intro.append(c)
    chip_entries += "  { ch: '%s', code: '%s', tag: '%s', intro: '%s' },\n" % (c, cur[c], tag, intro)
if need_intro:
    print("⚠ 以下字暂无介绍文字，稍后可补充：", " ".join(need_intro))
# 注入 gesture3d.html：字体 + chip 条目 + 计数
fp = os.path.join(base, "gesture3d.html")
h = open(fp, encoding="utf8").read()
i = h.find("base64,"); j = h.find(")", i)
h = h[:i + len("base64,")] + b64 + h[j:]
# chip 条目：插在字形表最后一个字目行之后
lines2 = h.split("\n")
idx = max(k for k, l in enumerate(lines2) if re.match(r"^\s*\{ ch: '", l))
lines2.insert(idx + 1, chip_entries.rstrip("\n"))
h = "\n".join(lines2)
# 计数由页面按 ORACLE_GLYPHS 实时渲染，无需在此改写文本。
# （原先这里写的是 r"字形库\\d+字" —— 双反斜杠使 \\d 成了字面反斜杠+d，
#   正则永远匹配不到，等于空操作。既然页面已能自动显示，直接删掉这一步。）
open(fp, "w", encoding="utf8").write(h)
print(f"✔ 已注入 gesture3d.html —— 刷新页面即可使用新字")
