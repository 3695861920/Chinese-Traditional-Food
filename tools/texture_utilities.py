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


# ----------------------------------------------------------------
# 柔和的木材色阶
# ----------------------------------------------------------------
# 原来直接把木色硬量化到 4 档，相邻像素一跳就是一整档，看起来“脏”且刺眼。
# 现在改成：在一道**连续的暖木色阶**上取值 ——
#   低对比 + 高密色阶 + 降饱和。
# 具体做法是把底色往灰里拉一点（降饱和），再沿一根 64 级的阶梯取样，
# 于是木纹是“洇”开的，而不是一块一块的。
WOOD_SOFT_RAMP = [
    (141, 111, 79),
    (152, 122, 89),
    (163, 133, 99),
    (174, 144, 109),
    (183, 154, 119),
    (192, 164, 129),
    (200, 172, 138),
    (208, 181, 148),
]


def soft_wood(value):
    """在柔和木色阶上按 0..1 取值（线性插值，不量化）。"""
    v = max(0.0, min(1.0, value)) * (len(WOOD_SOFT_RAMP) - 1)
    i = int(v)
    j = min(len(WOOD_SOFT_RAMP) - 1, i + 1)
    t = v - i
    a, b = WOOD_SOFT_RAMP[i], WOOD_SOFT_RAMP[j]
    return tuple(int(a[k] + (b[k] - a[k]) * t + 0.5) for k in range(3))


def _soft(colour, amount):
    """和 _shade 一样调明暗，但幅度自动减半 —— 案板要的是“柔”，不是对比。"""
    return _shade(colour, amount * 0.5)


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

    柔和处理（相比第一版的硬量化）：

    * 不再 `_quantize(..., 4)`，而是走 `soft_wood()` 的**连续色阶**；
    * 亮度区间从 0.40~0.86 收到 0.58~0.82，对比度降了一倍多；
    * 木节只压 8%、刀痕只压 4% —— 原来压 22% 看起来像砸了个坑；
    * 噪声幅度从 ±0.10 降到 ±0.035，表面因此是“打磨过”的。
    """
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            # 竖直顺纹：沿 y 拉长、沿 x 每隔几像素才变一次
            g = _grain(y, x, 211, 11) * 0.65 + _grain(y, x // 3, 233, 7) * 0.35
            lit = 0.58 + 0.24 * g
            c = soft_wood(lit)
            # 木节：一两个略深的小点（比第一版浅很多）
            for (nx, ny) in ((4.5, 6.2), (11.2, 10.4)):
                d = math.hypot(x - nx, y - ny)
                if d < 1.6:
                    c = _soft(c, -0.16 * (1.0 - d / 1.6))
            # 刀痕：几道几乎看不出的一横线
            if _noise(x // 2, y, 907) > 0.965:
                c = _soft(c, -0.07)
            _px(img, x, y, c)
    return img


def cutting_board_side():
    """案板侧面：木色 + 上沿高光 + 下沿落影（同样走柔和色阶）。"""
    img = _opaque()
    for y in range(SIZE):
        v = (y + 0.5) / SIZE
        lit = 0.80 - 0.30 * (v ** 1.1)
        for x in range(SIZE):
            c = soft_wood(lit)
            c = _soft(c, (_noise(x, y, 59) - 0.5) * 0.05)
            if v < 0.12:
                c = _soft(c, 0.16)
            elif v > 0.90:
                c = _soft(c, -0.24)
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
        v = 0.55 + 0.22 * _noise(x // 2, y // 3, 401) + \
            0.18 * _grain(x, y, 409, 11)
        c = soft_wood(v)
        if y < int(8.0 * U):
            c = _soft(c, 0.20)
        elif y > int(12.6 * U):
            c = _soft(c, -0.30)
        _px(img, x, y, c, 255)
    # 板厚（下面一条暗边）
    for (x, y) in pts:
        if y > int(12.6 * U):
            _px(img, x, y, _soft(soft_wood(0.35), -0.30), 255)

    # 摆一把菜刀
    knife = ICONS.draw("tool_knife", ((196, 200, 208), (146, 152, 162),
                                      (226, 230, 236), (112, 118, 128)), 7)
    img.alpha_composite(knife, (-int(1.0 * U), -int(1.2 * U)))
    return img


def main(out_block, out_item, finalize=None):
    """生成案板的三张图。

    ``finalize`` 由 build_textures 传入，用来把**物品图标**统一到 64x64
    （方块贴图不做放大：它们会被方块模型按 UV 采样，放大会白白占图集）。
    """
    for img, path in ((cutting_board_top(), os.path.join(out_block, "cutting_board.png")),
                      (cutting_board_side(), os.path.join(out_block, "cutting_board_side.png")),
                      (cutting_board_item(), os.path.join(out_item, "cutting_board.png"))):
        if finalize is not None and os.path.dirname(path) == out_item:
            img = finalize(img)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print("wrote %s %dx%d" % (os.path.relpath(path), img.width, img.height))
