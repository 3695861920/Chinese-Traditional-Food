# -*- coding: utf-8 -*-
"""树叶验收图：**拉原版橡树叶当标尺**，和自己的排在一起比。

为什么要拉原版进来：光看自己的图，"透多少"根本判断不了 ——
天蓝底色很亮，同样的镂空比例，蓝看着比绿多得多。只有把原版摆旁边，
"够不够通透""孔是不是太大"才有个客观参照。

每行三格：

    原版 oak_leaves 3x3 平铺 | 自己的 3x3 平铺 | item 图标

同时把**镂空率**印出来（原版 32.8%）—— 这是最硬的一个数，
肉眼会被颜色的明度骗，这个数不会。
"""

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import content_data as DATA          # noqa: E402
import gen_trees                     # noqa: E402
import vanilla_extract as V          # noqa: E402

ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets",
                      "chinese_traditional_food", "textures")
BLOCK_DIR = os.path.join(ASSETS, "block")
ITEM_DIR = os.path.join(ASSETS, "item")

CEL = 16
TILE = 3
SCALE = 6
CELL = CEL * SCALE
GAP = 6
SKY = (140, 190, 240, 255)
VANILLA_HOLE = 0.328


def hole_rate(img):
    px = list(img.convert("RGBA").getdata())
    return sum(1 for p in px if p[3] == 0) / float(len(px))


def tile(img):
    """3x3 平铺并压在天蓝底上 —— 顺便能看接缝有没有网格线。"""
    src = img.convert("RGBA").resize((CEL * TILE, CEL * TILE), Image.NEAREST)
    out = Image.new("RGBA", src.size, SKY)
    out.alpha_composite(src)
    return out.resize((CELL, CELL), Image.NEAREST)


def main():
    fruits = [row[0] for row in DATA.TREE_FRUITS]
    vanilla = V.image("block/oak_leaves").convert("RGBA")

    W = (CELL + GAP) * 3 + GAP
    H = (CELL + GAP) * (len(fruits) + 1) + GAP
    sheet = Image.new("RGBA", (W, H), (40, 42, 48, 255))

    # 第一行：原版当标尺（方块贴图 / 平铺 / 直接放大）
    y0 = GAP
    sheet.alpha_composite(tile(vanilla), (GAP, y0))
    sheet.alpha_composite(tile(vanilla), (GAP + CELL + GAP, y0))
    sheet.alpha_composite(vanilla.resize((CELL, CELL), Image.NEAREST),
                          (GAP + (CELL + GAP) * 2, y0))
    print("原版 oak_leaves 镂空率 %.1f%%" % (hole_rate(vanilla) * 100))

    lo, hi = 1.0, 0.0
    for i, fruit in enumerate(fruits):
        y0 = GAP + (i + 1) * (CELL + GAP)
        blk = Image.open(os.path.join(BLOCK_DIR,
                                      "%s.png" % gen_trees.leaves(fruit)))
        it = Image.open(os.path.join(ITEM_DIR,
                                     "%s_item.png" % gen_trees.leaves(fruit)))
        sheet.alpha_composite(tile(blk), (GAP, y0))
        sheet.alpha_composite(tile(blk), (GAP + CELL + GAP, y0))
        rate = hole_rate(blk)
        lo, hi = min(lo, rate), max(hi, rate)
        # item 图标垫灰底，方便看轮廓与实心程度
        patch = Image.new("RGBA", (CELL, CELL), (70, 74, 84, 255))
        patch.alpha_composite(
            it.convert("RGBA").resize((CELL, CELL), Image.NEAREST))
        sheet.alpha_composite(patch, (GAP + (CELL + GAP) * 2, y0))

    out = os.path.join(ROOT, "tools", "downloads", "leaves_preview.png")
    sheet.save(out)
    print("本模组镂空率 %.1f%% ~ %.1f%%（原版 %.1f%%）"
          % (lo * 100, hi * 100, VANILLA_HOLE * 100))
    print("-> %s" % out)


if __name__ == "__main__":
    main()
