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

    names = sorted(f for f in os.listdir(ITEM_DIR) if f.endswith(".png"))
    if not names:
        print("no icons found")
        return

    tile = 64 * scale
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * tile, rows * tile), (30, 30, 36, 255))

    for i, name in enumerate(names):
        img = Image.open(os.path.join(ITEM_DIR, name)).convert("RGBA")
        if img.size != (64, 64):
            img = img.resize((64, 64), Image.NEAREST)
        img = img.resize((tile, tile), Image.NEAREST)
        # 棋盘底，方便看清透明区域
        base = Image.new("RGBA", (tile, tile), (58, 58, 66, 255))
        for y in range(0, tile, 8):
            for x in range(0, tile, 8):
                if ((x // 8) + (y // 8)) % 2 == 0:
                    base.paste((70, 70, 80, 255), (x, y, x + 8, y + 8))
        base.alpha_composite(img)
        sheet.paste(base, ((i % cols) * tile, (i // cols) * tile))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print("preview -> %s  (%d icons, %dx%d)"
          % (os.path.relpath(OUT, ROOT), len(names), sheet.width, sheet.height))


if __name__ == "__main__":
    main()
