# -*- coding: utf-8 -*-
"""把生成好的物品图标拼成一张放大预览图，方便一次性检查画风。

    python tools/preview_icons.py [每行个数]

输出 tools/downloads/preview_icons.png
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM_DIR = os.path.join(ROOT, "src", "main", "resources", "assets",
                        "chinese_traditional_food", "textures", "item")
OUT = os.path.join(ROOT, "tools", "downloads", "preview_icons.png")


def main():
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    # 输出图的大小是 cols*tile x rows*tile，会**平方级**吃掉内存：
    # tile=64*scale，图标有 200 多个，scale=8 时整张图能到上亿像素，
    # 直接把机器拖死。所以这里夹紧到 1~4，并限制列数。
    if scale < 1 or scale > 4:
        print("!! scale 只支持 1~4（当前 %d），已夹到范围内" % scale)
        scale = max(1, min(4, scale))
    if cols < 1 or cols > 40:
        print("!! cols 只支持 1~40（当前 %d），已夹到范围内" % cols)
        cols = max(1, min(40, cols))

    names = sorted(f for f in os.listdir(ITEM_DIR) if f.endswith(".png"))
    if not names:
        print("no icons found")
        return

    tile = 16 * scale          # 源图是 16x16，放多少倍就多大
    rows = (len(names) + cols - 1) // cols

    # 棋盘底只做一块，所有格子共用 —— 之前是每个图标都重新 paste 一遍，
    # 大尺寸时那几千次 paste 本身就是不小的开销。
    base = Image.new("RGBA", (tile, tile), (58, 58, 66, 255))
    for y in range(0, tile, 8):
        for x in range(0, tile, 8):
            if ((x // 8) + (y // 8)) % 2 == 0:
                base.paste((70, 70, 80, 255), (x, y, x + 8, y + 8))

    sheet = Image.new("RGBA", (cols * tile, rows * tile), (30, 30, 36, 255))

    for i, name in enumerate(names):
        with Image.open(os.path.join(ITEM_DIR, name)) as src:
            img = src.convert("RGBA")
        if img.size != (tile, tile):
            img = img.resize((tile, tile), Image.NEAREST)
        cell = base.copy()
        cell.alpha_composite(img)
        sheet.paste(cell, ((i % cols) * tile, (i // cols) * tile))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print("preview -> %s  (%d icons, %dx%d)"
          % (os.path.relpath(OUT, ROOT), len(names), sheet.width, sheet.height))


if __name__ == "__main__":
    main()
