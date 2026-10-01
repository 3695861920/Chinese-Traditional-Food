# -*- coding: utf-8 -*-
"""诊断：量每种作物贴图的**实际包围盒**，看植株长到多高、多宽。

    python tools/_measure.py

眼睛看缩略图容易误判，直接数像素最准。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROPS = os.path.join(ROOT, "src", "main", "resources", "assets",
                     "chinese_traditional_food", "textures", "block")

NAMES = ["rice", "sorghum", "corn", "radish", "garlic", "napa_cabbage",
         "chive", "soybean", "tomato", "chili", "cucumber", "peanut",
         "wood_ear"]


def bbox(path):
    with Image.open(path) as im:
        px = im.convert("RGBA").load()
    x0 = y0 = 99
    x1 = y1 = -1
    for y in range(16):
        for x in range(16):
            if px[x, y][3] > 0:
                x0, y0 = min(x0, x), min(y0, y)
                x1, y1 = max(x1, x), max(y1, y)
    if x1 < 0:
        return None
    # 图像里 y=0 是顶边，换算成"离地面多高"
    return (x1 - x0 + 1, y1 - y0 + 1, y0, y1)


def main():
    print("%-14s %-28s %s" % ("crop", "stage7 (w,h,top,bottom)", "stages 0..7 高度"))
    for n in NAMES:
        row = []
        for s in range(8):
            p = os.path.join(CROPS, "%s_crop_stage%d.png" % (n, s))
            if not os.path.exists(p):
                row.append("-")
                continue
            b = bbox(p)
            if b is None:
                row.append("0")
                continue
            if s == 7:
                last = "w=%d h=%d top=%d bottom=%d" % b
            row.append(str(b[1]))
        print("%-14s %-28s %s" % (n, last, " ".join(row)))


if __name__ == "__main__":
    main()
