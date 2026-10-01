# -*- coding: utf-8 -*-
"""树叶 / 木制品验收图。

固定三件事，因为这三件事肉眼最容易骗人：

1. **树叶要和原版摆一起比镂空率**（原版 32.8%）。天蓝底色很亮，
   同样的镂空率，蓝看着比绿多得多，没有参照判断不了。
2. **木制品要按"每种木一排"摆**（原木侧 / 原木顶 / 去皮侧 / 去皮顶 / 木板），
   一眼看出 13 种木头的色相是不是真的分得开。
3. **镂空率要打印成数字** —— 数字不会被颜色的明度骗。
"""

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import content_data as DATA          # noqa: E402
import gen_trees                     # noqa: E402
import gen_woods                     # noqa: E402
import vanilla_extract as V          # noqa: E402

TEX = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food", "textures")
BLOCK_DIR = os.path.join(TEX, "block")
ITEM_DIR = os.path.join(TEX, "item")

CEL = 16
TILE = 3
SCALE = 4
CELL = CEL * SCALE
GAP = 4
SKY = (140, 190, 240, 255)
VANILLA_HOLE = 0.328


def hole_rate(img):
    px = list(img.convert("RGBA").getdata())
    return sum(1 for p in px if p[3] == 0) / float(len(px))


def tile3(img):
    """3x3 平铺压在天蓝底上 —— 顺便看接缝有没有网格线。"""
    src = img.convert("RGBA").resize((CEL * TILE, CEL * TILE), Image.NEAREST)
    out = Image.new("RGBA", src.size, SKY)
    out.alpha_composite(src)
    return out.resize((CELL, CELL), Image.NEAREST)


def load(path):
    return Image.open(path).convert("RGBA")


def strip(x0, y0, sheet, fruit):
    """一行五格：原木侧 / 原木顶 / 去皮侧 / 去皮顶 / 木板。"""
    names = ["%s.png" % gen_woods.log(fruit),
             "%s_top.png" % gen_woods.log(fruit),
             "%s.png" % gen_woods.stripped_log(fruit),
             "%s_top.png" % gen_woods.stripped_log(fruit),
             "%s.png" % gen_woods.planks(fruit)]
    for i, name in enumerate(names):
        img = load(os.path.join(BLOCK_DIR, name))
        # 木板/原木按 2x2 平铺看接缝；树皮一张就够
        if name.endswith("planks.png") or name == "%s.png" % gen_woods.log(fruit):
            src = img.resize((CEL * 2, CEL * 2), Image.NEAREST)
            out = Image.new("RGBA", src.size, SKY)
            out.alpha_composite(src)
            img = out
        sheet.alpha_composite(img.resize((CELL, CELL), Image.NEAREST),
                              (x0 + i * (CELL + GAP), y0))


def main():
    fruits = [row[0] for row in DATA.TREE_FRUITS]
    vanilla = V.image("block/oak_leaves").convert("RGBA")

    cols = max(len(fruits) + 1, 5)
    W = GAP + cols * (CELL + GAP)
    H = GAP + (len(fruits) + 2) * (CELL + GAP)
    sheet = Image.new("RGBA", (W, H), (40, 42, 48, 255))

    # ---- 第 1 行：树叶，原版 + 13 种 ----
    y0 = GAP
    sheet.alpha_composite(tile3(vanilla), (GAP, y0))
    lo, hi = 1.0, 0.0
    for i, fruit in enumerate(fruits):
        blk = load(os.path.join(BLOCK_DIR, "%s.png" % gen_trees.leaves(fruit)))
        rate = hole_rate(blk)
        lo, hi = min(lo, rate), max(hi, rate)
        sheet.alpha_composite(tile3(blk), (GAP + (i + 1) * (CELL + GAP), y0))
    print("原版 oak_leaves 镂空率 %.1f%%" % (hole_rate(vanilla) * 100))
    print("本模组镂空率 %.1f%% ~ %.1f%%（原版 %.1f%%）"
          % (lo * 100, hi * 100, VANILLA_HOLE * 100))

    # ---- 第 2 行：树叶物品图标（垫灰底看轮廓） ----
    y0 += CELL + GAP
    for i, fruit in enumerate(fruits):
        it = load(os.path.join(ITEM_DIR, "%s_item.png" % gen_trees.leaves(fruit)))
        patch = Image.new("RGBA", (CELL, CELL), (70, 74, 84, 255))
        patch.alpha_composite(it.resize((CELL, CELL), Image.NEAREST))
        sheet.alpha_composite(patch, (GAP + (i + 1) * (CELL + GAP), y0))

    # ---- 第 3 行起：13 种木制品，一种一行 ----
    for i, fruit in enumerate(fruits):
        strip(GAP, GAP + (i + 2) * (CELL + GAP), sheet, fruit)

    out = os.path.join(ROOT, "tools", "downloads", "trees_preview.png")
    sheet.save(out)
    print("-> %s" % out)


if __name__ == "__main__":
    main()
