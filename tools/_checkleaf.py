# -*- coding: utf-8 -*-
"""临时：检查 13 个树叶图标的实际颜色是否真的不同。用完删。"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import content_data as DATA  # noqa: E402
import gen_trees             # noqa: E402

ITEM = os.path.join(ROOT, "src", "main", "resources", "assets",
                    "chinese_traditional_food", "textures", "item")
BLOCK = os.path.join(ROOT, "src", "main", "resources", "assets",
                     "chinese_traditional_food", "textures", "block")


def mean_rgb(path):
    im = Image.open(path).convert("RGBA")
    tot = [0, 0, 0]
    n = 0
    for (r, g, b, a) in im.getdata():
        if a > 200:
            tot[0] += r
            tot[1] += g
            tot[2] += b
            n += 1
    if not n:
        return None
    return tuple(t // n for t in tot)


print("%-14s %-16s %-16s" % ("fruit", "item mean", "leaf look"))
for (fruit, _s) in DATA.TREE_FRUITS:
    it = mean_rgb(os.path.join(ITEM, "%s_item.png" % gen_trees.leaves(fruit)))
    look = DATA.TREE_LEAF_LOOK[fruit][0]
    print("%-14s %-16s %-16s" % (fruit, it, look))
