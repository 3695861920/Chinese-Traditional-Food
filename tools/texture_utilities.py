# -*- coding: utf-8 -*-
"""给器皿类方块（案板）生成纹理。并入 tools/build_textures.py 调用。

    python tools/build_textures.py --only utilities
"""
import math
import os

from PIL import Image

SIZE = 64
U = SIZE / 16.0

# 由 build_textures.py 注入
_noise = None
_bayer = None
_quantize = None
_shade = None

WOOD = [(120, 80, 44), (146, 100, 56), (170, 122, 70), (196, 148, 92)]


def bind(noise, bayer, quantize, shade):
    global _noise, _bayer, _quantize, _shade
    _noise, _bayer, _quantize, _shade = noise, bayer, quantize, shade


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


def _grain(x, y, seed, period):
    """沿 X 方向伸展的木纹，整数取模保证可平铺。"""
    return (_noise(x % period, y, seed) * 0.6
            + _noise(x // 2, y, seed + 7) * 0.4)


# ----------------------------------------------------------------------
def cutting_board_top():
    """案板顶面：一整块厚木板 + 中间一圈使用痕迹。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            plank = int((y / SIZE) * 3)         # 三块板
            ly = y - plank * (SIZE / 3.0)
            local = 1.0 - ly / (SIZE / 3.0)
            lit = 0.42 + 0.34 * local + 0.30 * _grain(x, y, 211 + plank * 17, 11)
            idx = _quantize(lit, 4, x, y)
            c = WOOD[idx]
            if ly >= SIZE / 3.0 - 2:
                c = _shade(c, -0.34)
            elif ly >= SIZE / 3.0 - 3:
                c = _shade(c, 0.12)
            # 中间的使用痕迹：一圈略深的刀痕
            dx = (x + 0.5 - SIZE / 2.0) / SIZE
            dy = (y + 0.5 - SIZE / 2.0) / SIZE
            d = math.hypot(dx, dy)
            if 0.22 < d < 0.36 and _noise(x, y, 907) < 0.35:
                c = _shade(c, -0.13)
            _px(img, x, y, c)
    return img


def cutting_board_side():
    """案板侧面：木色 + 上沿高光 + 下沿落影。"""
    img = _opaque()
    for y in range(SIZE):
        v = (y + 0.5) / SIZE
        lit = 0.72 - 0.52 * (v ** 1.1)
        for x in range(SIZE):
            idx = _quantize(lit, 4, x, y)
            c = WOOD[idx]
            c = _shade(c, (_noise(x, y, 59) - 0.5) * 0.07)
            if v < 0.12:
                c = _shade(c, 0.14)
            elif v > 0.90:
                c = _shade(c, -0.22)
            _px(img, x, y, c)
    return img


def cutting_board_item():
    """案板物品图标：3/4 视角的木板 + 一把菜刀。"""
    img = _blank()
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import texture_icons as ICONS

    # 板面（一个平行四边形，模拟斜视角）
    pts = set()
    for y in range(int(7.0 * U), int(13.4 * U)):
        for x in range(int(1.4 * U), int(14.6 * U)):
            # 上边缘斜切，做出立体感
            skew = (y - 7.0 * U) / (6.4 * U * 2.0)
            if x - int(1.4 * U) < skew * U * 0.9:
                continue
            pts.add((x, y))
    for (x, y) in pts:
        v = 0.45 + 0.35 * _noise(x // 2, y // 3, 401) + \
            0.20 * _grain(x, y, 409, 11)
        idx = _quantize(v, 4, x, y)
        c = WOOD[idx]
        if y < int(8.0 * U):
            c = _shade(c, 0.18)
        elif y > int(12.6 * U):
            c = _shade(c, -0.28)
        _px(img, x, y, c, 255)
    # 板厚（下面一条暗边）
    for (x, y) in pts:
        if y > int(12.6 * U):
            _px(img, x, y, _shade(WOOD[0], -0.30), 255)

    # 摆一把菜刀
    knife = ICONS.draw("tool_knife", ((196, 200, 208), (146, 152, 162),
                                      (226, 230, 236), (112, 118, 128)), 7)
    img.alpha_composite(knife, (-int(1.0 * U), -int(1.2 * U)))
    return img


def main(out_block, out_item):
    for img, path in ((cutting_board_top(), os.path.join(out_block, "cutting_board.png")),
                      (cutting_board_side(), os.path.join(out_block, "cutting_board_side.png")),
                      (cutting_board_item(), os.path.join(out_item, "cutting_board.png"))):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print("wrote %s" % os.path.relpath(path))
