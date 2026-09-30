# -*- coding: utf-8 -*-
"""给器皿类方块（案板）生成纹理。并入 tools/build_textures.py 调用。

    python tools/build_textures.py --only utilities
"""
import math
import os

from PIL import Image

SIZE = 16
U = SIZE / 16.0


def set_size(size):
    global SIZE, U
    SIZE = size
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
    """案板顶面：一整块打磨过的木板。

    注意这里**不再**画横向的拼板条 —— 拼板已经由三维模型
    （`tools/display_models.py` 里把板面拆成两块、中间留一道缝）表达了。
    贴图再叠一层横条纹会和模型的竖缝打架，看起来又乱又脏。
    所以这里只负责"木头本身的质感"：沿板长的顺纹 + 轻微的使用痕迹。
    纹理坐标里 U→X、V→Z，而板子沿 Z 方向铺满，所以木纹要**竖直**。
    """
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            # 竖直顺纹：沿 y 拉长、沿 x 每隔几像素才变一次
            g = _grain(y, x, 211, 11) * 0.65 + _grain(y, x // 3, 233, 7) * 0.35
            lit = 0.40 + 0.46 * g
            idx = _quantize(lit, 4, x, y)
            c = WOOD[idx]
            # 木节：一两个略深的小点
            for (nx, ny) in ((4.5, 6.2), (11.2, 10.4)):
                if math.hypot(x - nx, y - ny) < 1.5:
                    c = _shade(c, -0.22)
            # 刀痕：几道几乎看不出的一横线
            if _noise(x // 2, y, 907) > 0.955:
                c = _shade(c, -0.10)
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
