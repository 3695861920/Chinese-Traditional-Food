# -*- coding: utf-8 -*-
"""食材包装方块的贴图：包装本身 + 露出来的内容物。

    python tools/build_textures.py --only compressed

**卡通风**（这一版的重点）
------------------------
之前是"写实像素画"：细噪声、多色阶、弱对比。看起来像真的粗麻布，
但放在一起灰扑扑的、辨识度也不高。这一版改成卡通：

1. **平涂**：每种材质只用 2~3 个色阶，中间不做抖动渐变 —— 色块边界干净；
2. **粗描边**：所有形状都套一圈 1 像素的深色轮廓。这是卡通感最关键的一条，
   它让"一袋米""一箱番茄"在远处就能从背景里跳出来；
3. **高饱和**：颜色往饱和端推（内容物尤其明显），不再往灰里调；
4. **大色块**：颗粒画大、果子画大、少画小碎点。

实现上的做法：所有内容物都由"先铺色块，再统一描边"两步完成 ——
描边是后处理（`_outline_all`），所以每种形态不用各自操心边界。

一张图分两半
------------
每种方块生成两张：

* ``<id>.png``       —— **包装本身**（麻袋是布纹、木箱是木板、陶缸是釉面）；
* ``<id>_top.png``   —— **露出来的内容物**（袋口 / 箱口 / 缸口）。

这样才像农夫乐事的稻米袋 / 卷心菜箱：**不用右键，一眼就看出装的是什么**。
"""

import math

from PIL import Image

SIZE = 16
U = SIZE / 16.0

_noise = None
_bayer = None
_quantize = None
_shade = None


def set_size(size):
    global SIZE, U
    SIZE = size
    U = size / 16.0


def bind(noise, bayer, quantize, shade):
    global _noise, _bayer, _quantize, _shade
    _noise, _bayer, _quantize, _shade = noise, bayer, quantize, shade


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


def _seed(name):
    import zlib
    return zlib.crc32(name.encode("utf-8")) & 0x7FFF or 1


# ======================================================================
# 卡通风的两个基础手法
# ======================================================================

# 描边用的深色。不用纯黑 —— 纯黑在像素画里太硬，深暖褐更贴木头与食物。
INK = (56, 38, 28)


def _saturate(colour, amount=0.45):
    """把颜色往饱和端推（卡通的第一条：颜色要"艳"）。

    做法是把当前亮度当作基准，把每个通道往"离灰最远"的方向拉。
    """
    r, g, b = colour[:3]
    grey = (r + g + b) / 3.0
    out = []
    for c in (r, g, b):
        v = grey + (c - grey) * (1.0 + amount)
        out.append(max(0, min(255, int(v + 0.5))))
    return tuple(out)


def _flat(value, levels):
    """平涂：把连续值切成 levels 档，**不做抖动** —— 卡通的色块边界要干净。"""
    v = max(0.0, min(0.9999, value))
    return int(v * levels)


def _palette(pal, levels=3):
    """从一个 4 档配色里取出一组"平涂用"的颜色：暗 / 主 / 亮（都加饱和）。"""
    dark, main, light, _accent = pal
    if levels >= 3:
        return [_saturate(dark), _saturate(main), _saturate(light)]
    return [_saturate(dark), _saturate(main)]


def _ink(img, colour=INK):
    """给整张图上**粗描边**：所有不透明像素的边缘套一圈深色。

    这是卡通感最关键的一步 —— 形状有了明确的轮廓，
    远处就能认出来，而且同一套画风横跨 34 种方块。
    """
    px = img.load()
    w, h = img.size
    edges = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                continue
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                    edges.append((x, y))
                    break
    for (x, y) in edges:
        px[x, y] = colour + (255,)
    return img


def _band(img, y0, y1, colour):
    """在整宽上画一条色带（捆扎绳 / 箍）。"""
    px = img.load()
    for y in range(max(0, y0), min(SIZE, y1)):
        for x in range(SIZE):
            px[x, y] = colour + (255,)


def _border(img, colour, thickness=1):
    """四周一圈边框（卡通方块的"外轮廓"）。"""
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            if x < thickness or y < thickness or x >= SIZE - thickness or y >= SIZE - thickness:
                px[x, y] = colour + (255,)


# ======================================================================
# 包装本身
# ======================================================================

# 布袋的底色：偏中性的粗麻色。内容物的颜色会往这上面"染"一点，
# 于是不同内容物的袋子各不相同，但一眼还都是布。
BURLAP = (150, 128, 96)


def _tint_toward(pal, base, amount):
    """把配色往基准色里调 —— amount=0 全是基准色，1 全是配色。"""
    dark, main, light, accent = pal
    return tuple(int(base[i] + (main[i] - base[i]) * amount + 0.5) for i in range(3))


def shell(name, palette, form):
    """包装本身的贴图（卡通风：平涂 + 粗描边 + 高饱和）。"""
    img = _opaque()
    seed = _seed(name)

    if form in ("bag", "sack"):
        # 粗麻布：往内容物的颜色染 50%（袋子带一点货的颜色，好认），
        # 织纹只留"每 4 像素一道"的大格 —— 细织纹在卡通里只会变脏。
        base = _saturate(_tint_toward(palette, BURLAP, 0.50), 0.30)
        dark = _shade(base, -0.18)
        light = _shade(base, 0.16)
        for y in range(SIZE):
            for x in range(SIZE):
                # 大格布纹：横竖各一道，平涂两色
                c = dark if (x % 4 == 0 or y % 4 == 0) else base
                if (x % 4 == 2 and y % 4 == 2):
                    c = light
                _px(img, x, y, c)
        _band(img, 0, 1, _shade(base, -0.30))          # 袋底的暗边
        _band(img, SIZE - 1, SIZE, _shade(base, -0.30))

    elif form == "jar":
        # 陶缸：釉面做成"三条横向色带"，平涂 —— 卡通器皿就是这么画的
        base = _saturate(_tint_toward(palette, (128, 96, 80), 0.60), 0.35)
        for y in range(SIZE):
            band = (y * 5) // SIZE                      # 0..4，均分五大块
            c = (base,
                 _shade(base, 0.20),
                 base,
                 _shade(base, -0.14),
                 _shade(base, -0.26))[band]
            for x in range(SIZE):
                _px(img, x, y, c)

    elif form == "brick":
        # 压块：**大颗粒**平涂（不是细噪点），像压实的饲料块
        ramp = _palette(palette, 3)
        for y in range(SIZE):
            for x in range(SIZE):
                # 4×4 的大颗粒，每颗一种颜色 —— 卡通味的"碎料"
                v = _noise(x // 4, y // 4, seed)
                c = ramp[min(2, _flat(v, 4))]
                _px(img, x, y, c)
        _band(img, 0, 1, _shade(ramp[0], -0.25))
        _band(img, SIZE - 1, SIZE, _shade(ramp[0], -0.25))

    else:  # crate —— 这里的 body 其实用不到（箱子用共用木板），留个兜底
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, _saturate(_tint_toward(palette, BURLAP, 0.3), 0.3))
    return _ink(img)


# ======================================================================
# 内容物
# ======================================================================

def _blob(img, cx, cy, rx, ry, pal, seed, light=(-0.45, -0.5), rim=True):
    """一个"果子"：平涂两色 + 一块高光。

    卡通风的做法和写实反着来 —— **不做球面渐变**，只用"主色 + 一道月牙形
    阴影 + 一块方形高光"，然后把轮廓交给 `_ink` 统一描边。
    这样 16×16 里也能一眼数出"这是番茄"。
    """
    ramp = _palette(pal, 3)
    main_c, dark_c, light_c = ramp[0], ramp[1], ramp[2]
    pts = []
    for y in range(max(0, int(cy - ry - 2)), min(SIZE, int(cy + ry + 3))):
        for x in range(max(0, int(cx - rx - 2)), min(SIZE, int(cx + rx + 3))):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                pts.append((x, y, dx, dy))

    for (x, y, dx, dy) in pts:
        # 只用"受光 / 背光"两档：卡通的明暗就该是硬边
        c = light_c if (dx + dy) < -0.35 else main_c
        if (dx + dy) > 0.55:
            c = dark_c
        _px(img, x, y, c)

    # 方形高光（不是圆点 —— 方点才是卡通）
    if rx >= 2.0:
        hx, hy = int(cx - rx * 0.45), int(cy - ry * 0.45)
        for y in (hy, hy + 1):
            for x in (hx, hx + 1):
                if 0 <= x < SIZE and 0 <= y < SIZE and (x, y) in {(p[0], p[1]) for p in pts}:
                    _px(img, x, y, (255, 255, 255))
    return pts


def contents(name, palette, family):
    """露出来的内容物（卡通风：大色块 + 统一描边）。"""
    img = _opaque()
    seed = _seed(name)
    ramp = _palette(palette, 3)
    dark_c, main_c, light_c = ramp

    if family == "round":
        # 一个个圆果排开 —— 像番茄箱 / 蒜箱那样，一眼能数出来。
        # 数量刻意少、个头刻意大：16×16 里塞 8 个就糊成一团了，
        # 6 个、每个 3.4 像素半径刚好“看得清也装得满”。
        rows = ((4.2, 4.6), (11.8, 4.2),
                (3.0, 11.4), (8.0, 10.0), (13.2, 11.6),
                (8.0, 3.0))
        for i, (cx, cy) in enumerate(rows):
            r = 3.4 - (i % 2) * 0.30
            _blob(img, cx * U, cy * U, r * U, r * U, palette, seed + i * 17)

    elif family == "leafy":
        # 几片叠在一起的大叶子（不是细碎的小叶，也不是尖锐的星形）。
        # 每片叶子只两色 + 一条叶脉，剩下的交给统一描边。
        for i, (cx, cy, rx, ry, rot) in enumerate((
                (5.6, 6.4, 5.2, 4.6, -0.30),
                (11.0, 8.0, 4.6, 4.2, 0.35),
                (7.6, 12.2, 5.0, 4.2, -0.10))):
            pts = []
            ca, sa = math.cos(rot), math.sin(rot)
            for y in range(SIZE):
                for x in range(SIZE):
                    dx = (x + 0.5 - cx * U) / U
                    dy = (y + 0.5 - cy * U) / U
                    u = dx * ca - dy * sa
                    v = dx * sa + dy * ca
                    # 叶子不是椭圆：一头尖一头圆
                    if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0 + 0.35 * (u / rx):
                        pts.append((x, y, u / rx, v / ry))
            for (x, y, u, v) in pts:
                if (u + v) < -0.30:
                    c = light_c
                elif (u + v) > 0.55:
                    c = dark_c
                else:
                    c = main_c
                _px(img, x, y, c)
            # 叶脉：一条从基部到头部的粗线
            for (x, y, u, v) in pts:
                if abs(v) < 0.12:
                    _px(img, x, y, dark_c)

    elif family == "lump":
        # 大块干货：几块不规则的大块，平涂 + 一道亮面
        for i, (cx, cy, rx, ry, rot) in enumerate((
                (4.6, 5.0, 3.6, 3.2, -0.3), (10.6, 4.6, 3.4, 3.0, 0.2),
                (7.6, 10.0, 3.8, 3.4, -0.1), (13.0, 11.4, 2.8, 2.6, 0.4))):
            pts = []
            ca, sa = math.cos(rot), math.sin(rot)
            for y in range(SIZE):
                for x in range(SIZE):
                    dx = (x + 0.5 - cx * U) / U
                    dy = (y + 0.5 - cy * U) / U
                    u = dx * ca - dy * sa
                    v = dx * sa + dy * ca
                    # 加一点不规则，免得全是椭圆
                    wob = 1.0 + 0.22 * math.sin(math.atan2(v, u) * 3.0)
                    if (u / (rx * wob)) ** 2 + (v / (ry * wob)) ** 2 <= 1.0:
                        pts.append((x, y, u / rx, v / ry))
            for (x, y, u, v) in pts:
                if (u + v) < -0.35:
                    c = light_c
                elif (u + v) > 0.60:
                    c = dark_c
                else:
                    c = main_c
                _px(img, x, y, c)

    elif family == "paste":
        # 酱：一整片平涂 + 几个"油光"和大颗粒。
        # 卡通的酱不能画成一锅粥，得是"一块酱 + 几点亮"。
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, main_c)
        for i in range(5):
            gx = int(2.4 * U + i * 2.8 * U)
            gy = int((3.0 + (i % 2) * 5.0) * U)
            for y in range(gy, min(SIZE, gy + max(1, int(1.6 * U)))):
                for x in range(gx, min(SIZE, gx + max(1, int(1.6 * U)))):
                    _px(img, x, y, dark_c)
        # 两处油光
        for (gx, gy) in ((int(5.0 * U), int(6.4 * U)), (int(11.0 * U), int(10.4 * U))):
            for y in range(gy, min(SIZE, gy + 2)):
                for x in range(gx, min(SIZE, gx + 2)):
                    _px(img, x, y, light_c)

    else:  # grain
        # 颗粒堆：**大颗**的平涂颗粒（不是细噪点）。
        # 4×4 一颗，每颗一种颜色，堆得整整齐齐 —— 卡通粮堆的样子。
        for y in range(SIZE):
            for x in range(SIZE):
                grain = (_noise(x // 4, y // 4, seed) * 3.0)
                idx = min(2, int(grain))
                c = (dark_c, main_c, light_c)[idx]
                # 每颗颗粒的左上角点一块亮（"一颗一颗"的感觉）
                if x % 4 == 0 and y % 4 == 0:
                    c = light_c
                elif x % 4 == 3 or y % 4 == 3:
                    c = dark_c
                _px(img, x, y, c)

    return _ink(img)


# ======================================================================
# 共用贴图
# ======================================================================

def band():
    """捆扎绳 / 箱箍 / 缸沿（卡通风）：平涂三道带 —— 亮 / 主 / 暗。"""
    img = _opaque()
    dark = _saturate(_shade((96, 74, 52), -0.35))
    main_c = _saturate((150, 116, 78))
    light_c = _saturate(_shade((150, 116, 78), 0.30))
    lines = ((0, 1, dark), (1, 3, light_c), (3, SIZE - 2, main_c),
             (SIZE - 2, SIZE - 1, light_c), (SIZE - 1, SIZE, dark))
    for (y0, y1, c) in lines:
        _band(img, y0, y1, c)
    return _ink(img)


def crate():
    """木箱的板条（卡通风）：平涂的竖板 + 一道亮边 + 粗描边。

    周期整除 16（板条 4），所以相邻的箱子挨着放不会出现断裂的木纹。
    """
    img = _opaque()
    wood_dark = _saturate((150, 108, 66))
    wood_main = _saturate((184, 138, 90))
    wood_light = _saturate((212, 170, 118))
    ink_line = _saturate((104, 70, 40))
    for y in range(SIZE):
        for x in range(SIZE):
            slot = x % 4
            if slot == 0:
                c = ink_line                   # 板缝
            elif slot == 1:
                c = wood_light                 # 缝边高光（卡通板条的"倒角"）
            elif slot == 3:
                c = wood_dark                 # 板的另一侧
            else:
                c = wood_main
            # 上下横档：一整条亮色，把箱子"框"起来
            if y < 1 or y >= SIZE - 1:
                c = ink_line
            elif y < 3 or y >= SIZE - 3:
                c = wood_light
            _px(img, x, y, c)
    return _ink(img)
