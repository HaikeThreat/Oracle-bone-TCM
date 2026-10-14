#!/usr/bin/env python3
"""全量重建字库：把 data/oracle_glyphs_full.json 里的字全部灌进页面。

与 add_glyphs.py 的分工：
  add_glyphs.py   逐个加字（日常用，只重子集化涉及的码位）
  build_glyphs.py 全量重建（一次性把整个数据表灌进去，或数据表更新后重跑）

做三件事：
  1. 生成 ORACLE_GLYPHS 数组，写入 window.ORACLE_GLYPHS_INLINE
  2. 重新子集化 libs/AYJGW.ttf 并按 base64 内嵌进页面
  3. 更新面板静态计数初值

用法：
  python3 build_glyphs.py            # 全量
  python3 build_glyphs.py --limit 200  # 只取前 N 个（试体积用）
"""
import argparse
import base64
import io
import json
import os
import re
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

base = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只取前 N 个字（0=全部）")
    ap.add_argument("--src", default="libs/AYJGW.ttf")
    ap.add_argument("--db", default="data/oracle_glyphs_full.json")
    ap.add_argument("--curated", default="data/curated_glyphs.json",
                    help="人工润色条目 JSON（默认取仓库内 data/curated_glyphs.json）")
    args = ap.parse_args()

    db_path = os.path.join(base, args.db)
    page_path = os.path.join(base, "gesture3d.html")
    src_font = os.path.join(base, args.src)
    for p in (db_path, page_path, src_font):
        if not os.path.exists(p):
            sys.exit(f"找不到 {p}")

    html = open(page_path, encoding="utf8").read()

    # ── 1. 现有条目：保留其手写 tag/intro（人工润色过，不能用数据表覆盖）
    #     数据表里同一字头可能有多行，取第一行；有 tag/intro 的才认。
    db = json.load(open(db_path, encoding="utf8"))
    by_ch = {}
    for g in db:
        if g["ch"] not in by_ch:
            by_ch[g["ch"]] = g

    cur = {}
    if args.curated:
        cur = json.load(open(os.path.join(base, args.curated), encoding="utf8"))
    else:
        for m in re.finditer(r"\{ ch: '([^']+)', code: 'U([0-9A-F]+)'([^\n]*?)\}", html):
            ch, code, rest = m.group(1), m.group(2), m.group(3)
            tag = re.search(r"tag: '([^']*)'", rest)
            intro = re.search(r"intro: '([^']*)'", rest)
            cur[ch] = {
                "ch": ch, "code": "U" + code,
                "tag": tag.group(1) if tag else "",
                "intro": intro.group(1) if intro else "",
                "hidden": "hidden: true" in rest,
            }
    print(f"人工润色条目 {len(cur)} 个（优先采用其文案）")

    # ── 2. 遍历数据表顺序，已有条目沿用，其余用数据表文案
    src_cmap = set(TTFont(src_font).getBestCmap())
    rows, skipped = [], []
    for g in db:
        ch = g["ch"]
        if ch in cur:
            e = dict(cur[ch])
        else:
            e = {"ch": ch, "code": g["code"], "tag": g.get("tag") or "", "intro": g.get("intro") or ""}
        if int(e["code"].lstrip("U"), 16) not in src_cmap:
            skipped.append(ch)
            continue
        rows.append(e)

    # 补漏：人工条目里若用繁体字头（如 麥/冊），其码位与数据表的简体字头
    # （麦/册）相同，但字头不同 → 按数据表遍历时根本收不到，必须补进来，
    # 否则这些字会从字库中消失（曾因此丢掉 麥、冊 两个字）。
    for ch, e in cur.items():
        if ch not in {r["ch"] for r in rows}:
            rows.append(dict(e))
            print(f"  补入数据表未收录的字头：{ch}（{e['code']}）")

    # 去重（同一字头只留一条）
    seen, uniq = set(), []
    for e in rows:
        if e["ch"] in seen:
            continue
        seen.add(e["ch"])
        uniq.append(e)

    # 按码位去重：不同字头可能指向同一码位（简繁同字，如 麥/麦、冊/册），
    # 显示出来就是两个一模一样的按钮。人工条目优先（有 cur 记录的胜出）。
    by_code, dedup = {}, []
    for e in uniq:
        prev = by_code.get(e["code"])
        if prev is None:
            by_code[e["code"]] = e
            dedup.append(e)
        else:
            keep_new = (e["ch"] in cur) and (prev["ch"] not in cur)
            if keep_new:
                print(f"  同码位去重：{prev['ch']} 与 {e['ch']} 同为 {e['code']}，保留人工条目 {e['ch']}")
                dedup[dedup.index(prev)] = e
                by_code[e["code"]] = e
            else:
                print(f"  同码位去重：{prev['ch']} 与 {e['ch']} 同为 {e['code']}，保留 {prev['ch']}")
    uniq = dedup

    # 排序：人工编排过的字排在前面（保持原有顺序），其余按数据表顺序追加。
    # 原因：待机 14 秒会自动巡下一字，若把 1200 多个通用字混在前面，
    # 开场先看到的会是「一」「丁」「乙」这类与中医无关的字，
    # 而精心挑的 67 个（心/木/水/火/土…）反被淹没。
    if cur:
        curb = {ch: i for i, ch in enumerate(cur)}          # 人工编排顺序
        dbo = {e["ch"]: i for i, e in enumerate(uniq)}        # 数据表顺序（去重后）
        n_cur = len(curb)
        uniq.sort(key=lambda e: curb.get(e["ch"], n_cur + dbo[e["ch"]]))
        head = [e["ch"] for e in uniq[:n_cur]]
        want = [ch for ch in cur]
        if head != want:
            bad = [(i, want[i], head[i]) for i in range(len(want)) if want[i] != head[i]][:5]
            print(f"⚠ 人工编排顺序不一致：{len(bad)} 处，例如 {bad}")
        print(f"排序：前 {n_cur} 个为人工编排，其后 {len(uniq) - n_cur} 个按数据表顺序")

    # 面板里选不中的字（cur 中 hidden:true）保留在数组与字体中，但不显示按钮
    if args.limit:
        uniq = uniq[: args.limit]

    print(f"写入条目 {len(uniq)} 个" + (f"，跳过 {len(skipped)} 个（码位不在源字体）" if skipped else ""))

    # ── 3. 生成 JS 数组（拼音单独存 py 字段，供搜索用，不显示）
    lines = []
    for e in uniq:
        g = by_ch.get(e["ch"], {})
        py = (g.get("pinyin") or "").replace("'", "")
        parts = [f"ch: '{e['ch']}'", f"code: '{e['code']}'"]
        if e.get("hidden"):
            parts.append("hidden: true")
        if py:
            parts.append(f"py: '{py}'")
        parts.append(f"tag: '{e['tag'].replace(chr(39), '')}'")
        parts.append(f"intro: '{e['intro'].replace(chr(39), '')}'")
        lines.append("  { " + ", ".join(parts) + " },")
    arr = "[\n" + "\n".join(lines) + "\n]"

    # ── 4. 字体子集化
    text = "".join(chr(int(e["code"].lstrip("U"), 16)) for e in uniq)
    opts = subset.Options()
    opts.layout_features = []
    opts.hinting = False
    opts.desubroutinize = True
    f = subset.load_font(src_font, opts)
    s = subset.Subsetter(options=opts)
    s.populate(text=text)
    s.subset(f)
    tmp = "/tmp/oracle_subset_build.ttf"
    f.save(tmp)

    chk = TTFont(tmp).getBestCmap()
    miss = [e["ch"] for e in uniq if int(e["code"].lstrip("U"), 16) not in chk]
    assert not miss, f"子集缺字: {miss}"
    b64 = base64.b64encode(open(tmp, "rb").read()).decode()
    print(f"字体子集 {os.path.getsize(tmp) / 1024:.0f} KB（base64 {len(b64) / 1024:.0f} KB），校验通过")

    # ── 5. 回写页面
    # 5a. 数组 → window.ORACLE_GLYPHS_INLINE（放在主脚本之前）
    html, n1 = re.subn(
        r"<script>window\.ORACLE_GLYPHS_INLINE\s*=\s*\[.*?\];</script>",
        lambda m: "<script>window.ORACLE_GLYPHS_INLINE = " + arr + ";</script>",
        html, count=1, flags=re.S,
    )
    if n1 == 0:
        anchor = "\n<script>\n'use strict';"
        assert anchor in html, "找不到注入锚点"
        html = html.replace(
            anchor,
            "\n<!-- 字库数据：由 build_glyphs.py 生成，勿手改 -->\n"
            "<script>window.ORACLE_GLYPHS_INLINE = " + arr + ";</script>" + anchor,
            1,
        )

    # 5b. 字体 base64
    html, n2 = re.subn(r"(base64,)[A-Za-z0-9+/=]+(\))", lambda m: m.group(1) + b64 + m.group(2), html, count=1)
    assert n2 == 1, "字体 base64 替换失败"

    # 5c. 面板静态计数初值
    visible = sum(1 for e in uniq if not e.get("hidden"))
    # 标签可能是 span 或 div（面板改造后为 span），两者都要认，否则替换会静默失败
    html, n3 = re.subn(r'(<[a-z]+ id="glyphCount">)字形库\d+字(</[a-z]+>)',
                       lambda m: m.group(1) + f"字形库{visible}字" + m.group(2), html, count=1)
    if n3 != 1:
        print("⚠ 未能更新面板计数初值（未匹配到 glyphCount 文本）")

    open(page_path, "w", encoding="utf8").write(html)
    print(f"✔ 已写入 gesture3d.html —— 面板可选 {visible} 字（含隐藏共 {len(uniq)} 条）")


if __name__ == "__main__":
    main()
