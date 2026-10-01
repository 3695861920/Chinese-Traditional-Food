# -*- coding: utf-8 -*-
"""包装方块验收图：**每个方块一排，左边侧面（2×2 平铺）、右边顶面**。

    python tools/preview_pack.py

为什么不沿用 `preview_compressed.py` 的等轴测图：那张图把每张贴图压成
**平均色**，于是"编织袋的经纬""桶口的铁箍""顶面铺的是米还是豆"全都看不见 ——
而对包装方块来说，这三件事正是唯一要检查的东西。所以这里直接看原图：

    侧面 2×2 平铺（顺便检查接缝）  |  顶面 1 张放大

按包装样式分组输出，每组一张图，放在 tools/downloads/pack_<form>.png。
"""

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import gen_compressed as COMP  # noqa: E402

TEX = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food", "textures", "block")
OUT = os.path.join(ROOT, "tools", "downloads")

CEL = 16
SCALE = 4
CELL = CEL * SCALE
GAP = 4
BG = (44, 46, 52, 255)


def _tile(img, n):
    """n×n 平铺（检查接缝）。"""
    out = Image.new("RGBA", (CEL * n, CEL * n))
    for i in range(n):
        for j in range(n):
            out.paste(img, (i * CEL, j * CEL))
    return out


def _load(path):
    if not os.path.exists(path):
        return None
    return Image.open(path).convert("RGBA")


def sheet(form, rows):
    cols = 2
    W = GAP + cols * (CELL + GAP)
    H = GAP + len(rows) * (CELL + GAP)
    img = Image.new("RGBA", (W, H), BG)
    for i, (bid, side, top) in enumerate(rows):
        y = GAP + i * (CELL + GAP)
        if side is not None:
            img.alpha_composite(_tile(side, 2).resize((CELL, CELL), Image.NEAREST),
                                (GAP, y))
        else:
            # 箱的侧面引用原版木桶贴图，这里没有自己的文件 —— 画个占位
            holder = Image.new("RGBA", (CELL, CELL), (150, 105, 62, 255))
            img.alpha_composite(holder, (GAP, y))
        if top is not None:
            img.alpha_composite(top.resize((CELL, CELL), Image.NEAREST),
                                (GAP + CELL + GAP, y))
    path = os.path.join(OUT, "pack_%s.png" % form)
    img.save(path)
    print("-> %s  (%d 个方块)" % (path, len(rows)))


def main():
    groups = {}
    for (bid, _zh, _en, _src, form, _pal, _fam) in COMP.COMPRESSED:
        rows = groups.setdefault(form, [])
        rows.append((bid, _load(os.path.join(TEX, "%s.png" % bid)),
                     _load(os.path.join(TEX, "%s_top.png" % bid))))
    for form in sorted(groups):
        sheet(form, groups[form])


if __name__ == "__main__":
    main()
