# -*- coding: utf-8 -*-
"""树苗与树叶图标的对照图 —— 上排树苗、下排树叶图标。

    python tools/preview_sapling.py

为什么要单独做这张：13 个树苗/树叶图标的**形状差异**（叶形、排列、
片数、特征）在小图里最容易看漏。垫灰底 + 8 倍放大，
一眼就能看出"是不是复制粘贴"。
"""

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import content_data as DATA   # noqa: E402
import gen_trees              # noqa: E402

TEX = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food", "textures")
OUT = os.path.join(ROOT, "tools", "downloads")

S = 8
CEL = 16 * S
GAP = 6
BG = (44, 46, 52, 255)
PAD = (64, 68, 78, 255)


def _put(img, x, y, path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, PAD)
    bg.alpha_composite(im)
    img.alpha_composite(bg.resize((CEL, CEL), Image.NEAREST), (x, y))


def main():
    fruits = [row[0] for row in DATA.TREE_FRUITS]
    W = GAP + (CEL + GAP) * len(fruits)
    H = GAP + (CEL + GAP) * 2
    sheet = Image.new("RGBA", (W, H), BG)
    for i, fruit in enumerate(fruits):
        x = GAP + i * (CEL + GAP)
        _put(sheet, x, GAP,
             os.path.join(TEX, "block", "%s.png" % gen_trees.sapling(fruit)))
        _put(sheet, x, GAP + CEL + GAP,
             os.path.join(TEX, "item",
                          "%s.png" % gen_trees.leaves_item(fruit)))
    out = os.path.join(OUT, "sapling_leaf_strip.png")
    sheet.save(out)
    print("-> %s  (%d 种果树)" % (out, len(fruits)))


if __name__ == "__main__":
    main()
