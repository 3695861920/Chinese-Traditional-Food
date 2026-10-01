# -*- coding: utf-8 -*-
"""把同一株型的作物拼在一起，检查它们是否真的一眼能分辨。

    python tools/preview_plants.py

输出 tools/downloads/plants_by_habit.png —— 每行一种株型，每列一种作物，
格子里横排显示 4 个生长阶段（幼苗 → 成株）。

 改完 {@code crop_art.py} 先看这张图 —— 比开客户端快得多。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

import content_data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food", "textures", "block")
OUT = os.path.join(ROOT, "tools", "downloads", "plants_by_habit.png")

HABITS = ["grass", "legume", "seedpod", "root", "leafy", "bush", "vine", "fungus"]
Z = 5
CELL = 16 * Z
PAD = 3
STAGES = 4


def main():
    by_habit = {}
    for row in D.CROPS:
        by_habit.setdefault(row[5], []).append(row)

    widest = max(len(v) for v in by_habit.values())
    sheet = Image.new("RGBA",
                      (widest * (CELL * STAGES + PAD * 5) + PAD,
                       len(HABITS) * (CELL + PAD * 2) + PAD),
                      (30, 30, 36, 255))

    for r, habit in enumerate(HABITS):
        rows = by_habit.get(habit, [])
        cy = r * (CELL + PAD * 2) + PAD
        for c, (crop, _zh, _en, _seed, _prod, _h) in enumerate(rows):
            cx = c * (CELL * STAGES + PAD * 5) + PAD
            for s in range(STAGES):
                path = os.path.join(TEX, "%s_crop_stage%d.png" % (crop, s))
                if not os.path.exists(path):
                    continue
                with Image.open(path) as src:
                    img = src.convert("RGBA").resize((CELL, CELL), Image.NEAREST)
                sheet.alpha_composite(img, (cx + s * (CELL + PAD), cy))
        print("%-9s %s" % (habit, " ".join(r[0] for r in rows)))

    sheet.save(OUT)
    print("-> %s (%dx%d)" % (os.path.relpath(OUT, ROOT), sheet.width, sheet.height))


if __name__ == "__main__":
    main()
