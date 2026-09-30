# -*- coding: utf-8 -*-
"""把农作物（蔬菜 / 谷物 / 豆 / 种子）的图标拼成一张对照表。

    python tools/preview_crops.py [每行个数] [放大倍数]

输出 tools/downloads/preview_crops.png，并在控制台按同样顺序打印物品 id，
方便一眼看出"哪些作物长得太像"。

农作物图标是 64x64、其余物品是 16x16，所以这里**不读成品图**，
而是直接调用画法重新画一遍 —— 这样每格尺寸一致，对照起来才准。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib
import zlib

from PIL import Image

import content_data as DATA
import crop_icons as CROPS
import texture_icons as ICONS
from build_textures import hash_noise, bayer, quantize, shade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "downloads", "preview_crops.png")


def rows():
    """(分组名, [(id, kind, palette), ...])"""
    def pick(data, kind_index, pal_index, name_index):
        return [(r[0], r[kind_index], r[pal_index]) for r in data
                if r[kind_index] in CROPS.PAINTERS]

    return (
        ("谷物", pick(DATA.INGREDIENTS, 3, 4, 1) + pick(DATA.VEGETABLES, 3, 4, 1)[:0]),
        ("蔬菜", pick(DATA.VEGETABLES, 3, 4, 1)),
        ("种子", pick(DATA.SEEDS, 3, 4, 1)),
    )


def main():
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    cols = max(1, min(30, cols))
    scale = max(1, min(4, scale))

    ICONS.bind(hash_noise, bayer, quantize, shade)
    ICONS.set_size(16)
    ICONS.bind_crops(CROPS)

    groups = []
    for title, items in rows():
        if items:
            groups.append((title, items))

    tile = 64 * scale
    total = sum(len(it) for _t, it in groups)
    print("共 %d 个农作物图标" % total)

    all_items = []
    for title, items in groups:
        print("[%s]" % title)
        for i, (item_id, kind, pal_name) in enumerate(items):
            print("   %2d %-22s %-18s %s" % (i + 1, item_id, kind, pal_name))
            all_items.append((item_id, kind, pal_name))

    rows_n = (len(all_items) + cols - 1) // cols
    base = Image.new("RGBA", (tile, tile), (58, 58, 66, 255))
    for y in range(0, tile, 8):
        for x in range(0, tile, 8):
            if ((x // 8) + (y // 8)) % 2 == 0:
                base.paste((70, 70, 80, 255), (x, y, x + 8, y + 8))

    sheet = Image.new("RGBA", (cols * tile, rows_n * tile), (30, 30, 36, 255))
    for i, (item_id, kind, pal_name) in enumerate(all_items):
        seed = zlib.crc32(item_id.encode("utf-8")) & 0x7FFFFFFF or 1
        img = ICONS.draw(kind, DATA.PALETTES[pal_name], seed).convert("RGBA")
        cell = base.copy()
        cell.alpha_composite(img)
        if scale != 1:
            cell = cell.resize((tile, tile), Image.NEAREST)
        sheet.paste(cell, ((i % cols) * tile, (i // cols) * tile))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print("preview -> %s (%dx%d)" % (os.path.relpath(OUT, ROOT),
                                     sheet.width, sheet.height))


if __name__ == "__main__":
    main()
