# -*- coding: utf-8 -*-
"""把包装方块按等轴测拼成一张对照图，用来检查"看不看得出装的是什么"。

    python tools/preview_compressed.py [每行个数]

输出 tools/downloads/compressed.png。复用 preview_machines 的等轴测渲染，
只是把材质键换成包装方块的那几个。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

import preview_machines as PM
import gen_compressed as COMP

# 包装方块的贴图路径（新模型的键是 side/top/bottom，不是 #body/#contents）
NS = "chinese_traditional_food"

# 原版木桶 / 陶罐贴图的近似平均色（箱子与缸直接用它们）
BARREL_SIDE = (138, 96, 56)
BARREL_BOTTOM = (150, 105, 62)
POT_SIDE = (150, 100, 82)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "downloads", "compressed.png")
TEX_DIR = os.path.join(ROOT, "src", "main", "resources", "assets",
                       "chinese_traditional_food", "textures", "block")


def _average(path):
    """一张贴图的平均色（缩到 1×1 就是求均值，PIL 自己会算）。"""
    with Image.open(path) as src:
        return src.convert("RGBA").resize((1, 1), Image.BOX).getpixel((0, 0))[:3]


def real_palette(bid, form):
    """按方块的**真实贴图**采出一组颜色，键是贴图路径。

    占位色只能看出"这地方有块木头"，看不出"箱子里装的是番茄还是大米"——
    而对包装方块来说，后者正是最该看的东西。所以这里把每张贴图压成平均色，
    等轴测图就带上了真实色相（虽然仍看不出细节）。
    """
    pal = {
        "minecraft:block/barrel_side": BARREL_SIDE,
        "minecraft:block/barrel_bottom": BARREL_BOTTOM,
        # 缸身改成自绘了，不再需要原版陶土的近似色
    }
    side = os.path.join(TEX_DIR, "%s.png" % bid)
    top = os.path.join(TEX_DIR, "%s_top.png" % bid)
    if os.path.exists(side):
        pal["%s:block/%s" % (NS, bid)] = _average(side)
    if os.path.exists(top):
        pal["%s:block/%s_top" % (NS, bid)] = _average(top)
    return pal


def main():
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    cols = max(1, min(20, cols))

    rows_all = COMP.COMPRESSED
    names = [row[0] for row in rows_all]
    imgs = []
    for (bid, _zh, _en, _src, form, _pal, _fam) in rows_all:
        try:
            imgs.append(PM.render(bid, real_palette(bid, form)))
        except Exception as exc:                      # noqa: BLE001
            print("!! 渲染失败 %s: %s" % (bid, exc))

    tile_w = max(i.width for i in imgs) + 8
    tile_h = max(i.height for i in imgs) + 8
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * tile_w, rows * tile_h), (26, 26, 32, 255))

    for i, name in enumerate(names):
        img = imgs[i]
        x = (i % cols) * tile_w + (tile_w - img.width) // 2
        y = (i // cols) * tile_h + (tile_h - img.height) // 2
        sheet.alpha_composite(img, (x, y))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print("preview -> %s (%dx%d, %d 个)" % (os.path.relpath(OUT, ROOT),
                                            sheet.width, sheet.height, len(imgs)))
    # 排版顺序也打出来，对着图看
    for i, n in enumerate(names):
        print("   %2d %s" % (i + 1, n))

    texture_sheet(names)


TEX_OUT = os.path.join(ROOT, "tools", "downloads", "compressed_textures.png")


def texture_sheet(names):
    """把**真实贴图**放大拼一张：左格是包装本身、右格是露出的内容物。

    上面那张等轴测图用的是占位色（只看结构），这张才是真正的画风检查 ——
    "袋子里装的是不是苹果""箱子里是不是胡萝卜"在这张图上一目了然。
    """
    scale = 4
    cell = 16 * scale
    pad = 4
    cols = 7
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (cell * 2 + pad * 3), rows * (cell + pad * 2)),
                      (30, 30, 36, 255))

    for i, name in enumerate(names):
        cx = (i % cols) * (cell * 2 + pad * 3) + pad
        cy = (i // cols) * (cell + pad * 2) + pad
        for k, suffix in enumerate(("", "_top")):
            path = os.path.join(TEX_DIR, "%s%s.png" % (name, suffix))
            if not os.path.exists(path):
                continue
            with Image.open(path) as src:
                img = src.convert("RGBA").resize((cell, cell), Image.NEAREST)
            sheet.alpha_composite(img, (cx + k * (cell + pad), cy))

    sheet.save(TEX_OUT)
    print("textures -> %s (%dx%d)" % (os.path.relpath(TEX_OUT, ROOT),
                                      sheet.width, sheet.height))


if __name__ == "__main__":
    main()
