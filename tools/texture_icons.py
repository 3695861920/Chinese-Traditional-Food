# -*- coding: utf-8 -*-
"""
Minecraft 风格图标绘制器（64x64）。

`content_data.py` 里每个物品都声明了一个"图标种类"（kind），
这里为每种 kind 提供一个画法。所有画法共用同一套基元与规范：

* 硬边：逐像素写入，不做抗锯齿；
* 窄色板 + Bayer 抖动：用调用方传入的 4 档配色，量化过渡；
* 逐像素噪声：叠加细微颗粒，避免大色块；
* 物品图标一律透明背景，并给右下加一档暗边做体积感。

坐标一律用"原版像素"单位（0~16），由 U 换算到实际像素。
"""

import math

from PIL import Image

SIZE = 64
U = SIZE / 16.0

# 由 build_textures.py 注入（避免循环 import）
_noise = None
_bayer = None
_quantize = None
_shade = None


def bind(noise, bayer, quantize, shade):
    global _noise, _bayer, _quantize, _shade
    _noise, _bayer, _quantize, _shade = noise, bayer, quantize, shade


# ======================================================================
# 基元
# ======================================================================

def blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def P(cx, cy):
    """原版像素坐标 -> 本图像素坐标（取像素中心）。"""
    return cx * U, cy * U


def disc_pts(cx, cy, r):
    cx, cy, r = cx * U, cy * U, r * U
    r2 = r * r
    out = []
    for y in range(max(0, int(cy - r - 1)), min(SIZE, int(cy + r + 2))):
        for x in range(max(0, int(cx - r - 1)), min(SIZE, int(cx + r + 2))):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            if dx * dx + dy * dy <= r2:
                out.append((x, y))
    return out


def oval_pts(cx, cy, rx, ry):
    cx, cy, rx, ry = cx * U, cy * U, rx * U, ry * U
    out = []
    for y in range(max(0, int(cy - ry - 1)), min(SIZE, int(cy + ry + 2))):
        for x in range(max(0, int(cx - rx - 1)), min(SIZE, int(cx + rx + 2))):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                out.append((x, y))
    return out


def box_pts(x0, y0, x1, y1):
    out = []
    for y in range(max(0, int(y0 * U)), min(SIZE, int(round(y1 * U)))):
        for x in range(max(0, int(x0 * U)), min(SIZE, int(round(x1 * U)))):
            out.append((x, y))
    return out


def poly_pts(points):
    """扫描线填充多边形，points 是原版像素坐标列表。"""
    pts = [(x * U, y * U) for (x, y) in points]
    ys = [p[1] for p in pts]
    y0, y1 = int(min(ys)), int(max(ys)) + 1
    out = []
    n = len(pts)
    for y in range(max(0, y0), min(SIZE, y1)):
        yc = y + 0.5
        xs = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            if (ay <= yc < by) or (by <= yc < ay):
                t = (yc - ay) / (by - ay)
                xs.append(ax + (bx - ax) * t)
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(max(0, int(xs[i])), min(SIZE, int(xs[i + 1]) + 1)):
                out.append((x, y))
    return out


def paint(img, pts, colour):
    for (x, y) in pts:
        px(img, x, y, colour)


def sphere(img, cx, cy, r, pal, seed=0, squash=1.0, light=(-0.55, -0.55)):
    """球体（水果 / 珠子）：左上受光，右下沉到暗档，最后压一圈描边。"""
    main, dark, light_c, accent = pal
    rx, ry = r, r * squash
    pts = set(oval_pts(cx, cy, rx, ry))
    for (x, y) in pts:
        dx = (x + 0.5 - cx * U) / (rx * U)
        dy = (y + 0.5 - cy * U) / (ry * U)
        # 距离光源的远近 -> 亮度
        d = math.hypot(dx - light[0], dy - light[1]) / 1.7
        v = 0.92 - 0.85 * min(1.0, d)
        v += (_noise(x, y, seed) - 0.5) * 0.10
        idx = _quantize(v, 4, x, y)
        c = (dark, main, light_c, accent)[idx] if idx < 4 else light_c
        px(img, x, y, c, 255)
    # 高光
    hx, hy = cx - rx * 0.34, cy - ry * 0.34
    paint(img, oval_pts(hx, hy, rx * 0.20, ry * 0.16), light_c)
    # 右下描边
    for (x, y) in pts:
        if (x + 1, y) not in pts or (x, y + 1) not in pts:
            if (x + 0.5 - cx * U) + (y + 0.5 - cy * U) > 0:
                px(img, x, y, dark, 255)


def outline(img, pts, colour):
    s = set(pts)
    for (x, y) in s:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in s:
                px(img, x + dx, y + dy, colour, 255)


def scatter(img, cx, cy, r, count, pal, seed=0, size=0.75, squash=0.82):
    """在一团里撒若干小颗粒（豆子 / 芝麻 / 花椒）。"""
    main, dark, light, accent = pal
    import random
    rnd = random.Random(seed)
    for _ in range(count):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(0, r * 0.82)
        sx, sy = cx + math.cos(a) * d, cy + math.sin(a) * d * squash
        jitter = rnd.uniform(-1.0, 1.0)
        for (x, y) in oval_pts(sx, sy, size, size * 0.85):
            c = light if jitter > 0 else main
            if _noise(x, y, seed) < 0.25:
                c = dark
            px(img, x, y, c, 255)


def noise_fill(img, pts, pal_base, seed, levels=3, lo=0.0, hi=1.0, ordered=True):
    """用窄色板 + 抖动填充一块区域（粉堆 / 米饭 / 面）。"""
    for (x, y) in pts:
        v = lo + (hi - lo) * _noise(x // 2, y // 2, seed)
        idx = _quantize(v, levels, x, y, ordered=ordered)
        px(img, x, y, pal_base[min(idx, len(pal_base) - 1)], 255)


def ground_shadow(img, cx, cy, rx, ry, alpha=70):
    for (x, y) in oval_pts(cx, cy, rx, ry):
        px(img, x, y, (0, 0, 0), alpha)


# ======================================================================
# 谷物 / 粉类
# ======================================================================

def icon_grain(img, pal, seed):
    """一堆米粒。"""
    ground_shadow(img, 8, 13.4, 5.6, 1.5, 60)
    import random
    rnd = random.Random(seed)
    main, dark, light, accent = pal
    for _ in range(46):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(0, 4.4)
        sx, sy = 8 + math.cos(a) * d, 8.4 + math.sin(a) * d * 0.72
        ang = rnd.uniform(-0.5, 0.5)
        for i in range(3):
            x = sx + math.cos(ang) * i * 0.55 - 0.55
            y = sy + math.sin(ang) * i * 0.55
            c = light if i == 2 else (main if i == 1 else dark)
            px(img, x * U, y * U, c, 255)


def icon_ear(img, pal, seed):
    """稻穗：一根穗 + 两侧谷粒。"""
    main, dark, light, accent = pal
    # 茎
    for y in range(int(4.5 * U), int(14.5 * U)):
        px(img, 8 * U, y, accent, 255)
        px(img, 8 * U + 1, y, dark, 255)
    # 谷粒
    for i in range(7):
        gy = 4.6 + i * 1.25
        w = 3.4 - i * 0.30
        paint(img, oval_pts(8 - w * 0.42, gy, 0.72, 1.05), main if i % 2 else light)
        paint(img, oval_pts(8 + w * 0.42, gy, 0.72, 1.05), light if i % 2 else main)
        paint(img, oval_pts(8, gy + 0.5, 0.30, 0.42), accent)
    # 顶部芒
    for (x0, y0, x1, y1) in ((8, 4.2, 6.8, 2.0), (8, 4.2, 9.2, 2.0), (8, 4.2, 8.0, 1.6)):
        for (x, y) in poly_pts([(x0 - 0.2, y0), (x0 + 0.2, y0), (x1, y1)]):
            px(img, x, y, accent, 255)


def icon_corn(img, pal, seed):
    """玉米：棒身 + 外剥的苞叶。"""
    main, dark, light, accent = pal
    paint(img, oval_pts(8, 8.6, 3.0, 5.4), main)
    for y in range(int(3.6 * U), int(13.8 * U)):
        for x in range(int(5.2 * U), int(10.8 * U)):
            if (x + y) % max(2, int(U)) == 0:
                px(img, x, y, dark, 210)
            if (x - y) % max(2, int(U)) == 0:
                px(img, x, y, light, 150)
    paint(img, poly_pts([(5.4, 6.0), (7.4, 3.0), (7.8, 4.2), (6.2, 7.0)]), accent)
    paint(img, poly_pts([(10.6, 6.0), (8.6, 3.0), (8.2, 4.2), (9.8, 7.0)]), accent)
    paint(img, poly_pts([(6.0, 12.5), (8.0, 14.6), (10.0, 12.5), (8.0, 13.2)]), accent)


def icon_powder(img, pal, seed):
    """一堆粉 + 后面一个敞口布袋。"""
    main, dark, light, accent = pal
    # 袋子
    paint(img, poly_pts([(3.6, 5.0), (6.0, 2.4), (10.0, 2.4), (12.4, 5.0), (12.0, 11.6), (4.0, 11.6)]), accent)
    for (x, y) in poly_pts([(4.2, 5.4), (6.2, 3.2), (9.8, 3.2), (11.8, 5.4), (11.4, 8.4), (4.6, 8.4)]):
        v = _noise(x, y, seed)
        px(img, x, y, main if v > 0.4 else light, 255)
    # 袋口的褶皱
    for i in range(5):
        xx = 4.4 + i * 1.55
        for (x, y) in poly_pts([(xx, 2.8), (xx + 0.6, 2.8), (xx + 0.3, 4.6)]):
            px(img, x, y, dark, 220)
    # 倒出来的粉堆
    pile = oval_pts(8, 13.2, 4.6, 2.0)
    for (x, y) in pile:
        v = 0.35 + 0.65 * _noise(x // 2, y, seed + 5)
        px(img, x, y, light if v > 0.6 else main, 255)
    for (x, y) in pile:
        if _noise(x, y, seed + 11) < 0.20:
            px(img, x, y, dark, 190)


def icon_crystal(img, pal, seed):
    """冰糖：几块不规则晶体。"""
    main, dark, light, accent = pal
    chunks = [((5.0, 8.6), 2.4), ((9.6, 6.4), 2.0), ((8.4, 11.0), 1.8), ((11.8, 10.0), 1.4)]
    for i, ((cx, cy), r) in enumerate(chunks):
        pts = poly_pts([(cx, cy - r), (cx + r, cy - r * 0.25),
                        (cx + r * 0.6, cy + r * 0.9), (cx - r * 0.8, cy + r * 0.8),
                        (cx - r, cy - r * 0.2)])
        for (x, y) in pts:
            px(img, x, y, light if (x - x) == 0 and _noise(x, y, seed + i) > 0.45 else main, 235)
        for (x, y) in pts:
            if _noise(x, y, seed + i * 7) < 0.18:
                px(img, x, y, dark, 235)
        outline(img, pts, accent)


# ======================================================================
# 豆类 / 颗粒
# ======================================================================

def icon_beans(img, pal, seed):
    ground_shadow(img, 8, 13.2, 5.0, 1.4, 55)
    scatter(img, 8, 8.6, 4.6, 22, pal, seed, size=0.95, squash=0.75)


def icon_seeds(img, pal, seed):
    ground_shadow(img, 8, 13.0, 4.4, 1.3, 50)
    scatter(img, 8, 8.6, 4.2, 34, pal, seed, size=0.52, squash=0.78)


def icon_nuts(img, pal, seed):
    main, dark, light, accent = pal
    ground_shadow(img, 8, 13.2, 5.0, 1.4, 55)
    for (cx, cy) in ((5.6, 10.0), (10.4, 9.4), (8.0, 6.2)):
        sphere(img, cx, cy, 2.5, pal, seed, squash=0.72, light=(-0.6, -0.5))
        # 花生壳的网格纹
        for i in range(3):
            for (x, y) in poly_pts([(cx - 2, cy - 1 + i * 1.0), (cx - 1.8, cy - 0.4 + i * 1.0),
                                    (cx + 1.8, cy - 0.4 + i * 1.0)]):
                px(img, x, y, dark, 150)


def icon_berries(img, pal, seed):
    main, dark, light, accent = pal
    ground_shadow(img, 8, 13.2, 4.8, 1.4, 55)
    for (cx, cy, r) in ((6.0, 9.8, 2.2), (10.0, 9.2, 2.0), (8.0, 6.4, 1.8), (11.2, 11.6, 1.5)):
        sphere(img, cx, cy, r, pal, seed, light=(-0.55, -0.6))
    # 小蒂
    for (cx, cy) in ((6.0, 9.8), (10.0, 9.2), (8.0, 6.4)):
        for (x, y) in poly_pts([(cx - 0.3, cy - 2.4), (cx + 0.3, cy - 2.4), (cx, cy - 1.6)]):
            px(img, x, y, accent, 255)


def icon_cherries(img, pal, seed):
    main, dark, light, accent = pal
    for (cx, cy) in ((6.2, 10.6), (10.0, 11.0)):
        sphere(img, cx, cy, 2.3, pal, seed, light=(-0.55, -0.55))
    for (cx, cy, tx, ty) in ((6.2, 8.4, 7.2, 3.4), (10.0, 8.8, 8.8, 3.4)):
        for (x, y) in poly_pts([(cx - 0.18, cy), (cx + 0.18, cy), (tx, ty)]):
            px(img, x, y, accent, 255)
    paint(img, poly_pts([(6.6, 4.4), (7.6, 3.0), (9.4, 3.4), (8.4, 4.8)]), light)


def icon_flowers(img, pal, seed):
    """桂花：一枝细梗上几点小花。"""
    main, dark, light, accent = pal
    for (x, y) in poly_pts([(3.6, 12.6), (4.1, 12.6), (11.6, 4.2), (11.1, 4.2)]):
        px(img, x, y, accent, 255)
    for i in range(6):
        cx, cy = 4.6 + i * 1.35, 11.6 - i * 1.42
        paint(img, oval_pts(cx - 0.55, cy, 0.85, 0.62), main)
        paint(img, oval_pts(cx + 0.55, cy - 0.35, 0.85, 0.62), light)
        paint(img, oval_pts(cx, cy + 0.5, 0.72, 0.55), main)
        paint(img, oval_pts(cx, cy + 0.2, 0.26, 0.26), dark)


# ======================================================================
# 薯类 / 根茎
# ======================================================================

def icon_tuber(img, pal, seed):
    """块茎（红薯 / 山药 / 芋头 / 萝卜）：椭圆 + 横向细纹。"""
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.2, 3.4, 4.8))
    for (x, y) in pts:
        dx = (x + 0.5 - 8 * U) / (3.4 * U)
        dy = (y + 0.5 - 9.2 * U) / (4.8 * U)
        d = math.hypot(dx + 0.5, dy + 0.5) / 1.8
        v = 0.90 - 0.82 * min(1.0, d) + (_noise(x, y, seed) - 0.5) * 0.10
        px(img, x, y, (dark, main, light, accent)[_quantize(v, 4, x, y)], 255)
    # 横纹
    for i in range(5):
        yy = 5.8 + i * 1.6
        hw = 2.8 * math.sqrt(max(0.05, 1 - ((yy - 9.2) / 4.8) ** 2))
        for x in range(int((8 - hw) * U), int((8 + hw) * U), 2):
            px(img, x, yy * U, dark, 130)
    # 顶芽
    paint(img, poly_pts([(7.6, 4.6), (8.4, 4.6), (8.0, 3.2)]), accent)
    outline(img, pts, accent)


def icon_ginger(img, pal, seed):
    """姜：几节不规则块。"""
    main, dark, light, accent = pal
    lumps = [((6.0, 9.6), 2.4), ((10.2, 7.6), 2.0), ((9.0, 12.0), 1.7)]
    for i, ((cx, cy), r) in enumerate(lumps):
        pts = oval_pts(cx, cy, r, r * 0.86)
        for (x, y) in pts:
            v = 0.55 + 0.45 * _noise(x // 2, y // 2, seed + i * 3)
            px(img, x, y, light if v > 0.62 else main, 255)
        for (x, y) in pts:
            if _noise(x, y, seed + i) < 0.16:
                px(img, x, y, dark, 200)
        outline(img, pts, accent)


def icon_garlic(img, pal, seed):
    """蒜：一头蒜 + 顶部尖。"""
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.4, 3.6, 4.4))
    paint(img, poly_pts([(6.4, 6.2), (9.6, 6.2), (8.0, 2.6)]), main)
    for (x, y) in pts:
        v = 0.85 - 0.7 * min(1.0, math.hypot((x + 0.5 - 8 * U) / (3.6 * U) + 0.5,
                                             (y + 0.5 - 9.4 * U) / (4.4 * U) + 0.5) / 1.7)
        px(img, x, y, (dark, main, light, light)[_quantize(v, 4, x, y)], 255)
    # 瓣缝
    for x in (6.4, 8.0, 9.6):
        for y in range(int(6.6 * U), int(13.4 * U)):
            px(img, x * U, y, dark, 170)
    outline(img, pts, accent)


def icon_shoot(img, pal, seed):
    """笋：层叠的笋壳。"""
    main, dark, light, accent = pal
    layers = [(2.6, 5.0, 5.2, 3.6), (3.5, 8.0, 9.0, 3.4), (3.9, 11.4, 8.1, 2.8)]
    for (x0, y0, x1, y1) in layers:
        paint(img, poly_pts([(x0, y1), (x1, y1), (x1 - 0.8, y0), (x0 + 0.8, y0)]), main)
        for (x, y) in poly_pts([(x0 + 0.4, y1 - 0.6), (x1 - 0.4, y1 - 0.6), (x1 - 0.9, y0 + 0.4), (x0 + 0.9, y0 + 0.4)]):
            v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
            px(img, x, y, light if v > 0.55 else main, 255)
    # 笋尖
    paint(img, poly_pts([(6.4, 3.4), (9.6, 3.4), (8.0, 1.6)]), light)


# ======================================================================
# 叶菜 / 茎 / 瓜果
# ======================================================================

def icon_leafy(img, pal, seed):
    """叶菜：几片外翻的叶子包住菜心。"""
    main, dark, light, accent = pal
    leaves = [((8.0, 7.4), 4.6, 6.2, 0.0), ((5.0, 8.6), 3.0, 4.6, -0.55),
              ((11.0, 8.6), 3.0, 4.6, 0.55), ((6.4, 11.6), 2.6, 3.8, -0.3),
              ((9.6, 11.6), 2.6, 3.8, 0.3)]
    for i, ((cx, cy), rx, ry, rot) in enumerate(leaves):
        pts = []
        for (x, y) in oval_pts(cx, cy, rx, ry):
            dx, dy = x + 0.5 - cx * U, y + 0.5 - cy * U
            ca, sa = math.cos(rot), math.sin(rot)
            px_, py_ = dx * ca - dy * sa, dx * sa + dy * ca
            if px_ * px_ / ((rx * U) ** 2) + py_ * py_ / ((ry * U) ** 2) <= 1.0:
                pts.append((x, y))
        for (x, y) in pts:
            v = 0.55 + 0.45 * _noise(x // 2, y // 2, seed + i * 5)
            px(img, x, y, (dark, main, light, light)[_quantize(v, 3, x, y)], 255)
        # 叶脉
        for t in range(int(ry * U)):
            xx = cx * U + math.cos(rot) * 0
            px(img, xx, cy * U - t, dark, 120)
        outline(img, pts, accent)
    # 菜帮
    paint(img, poly_pts([(7.2, 12.6), (8.8, 12.6), (8.8, 14.6), (7.2, 14.6)]), light)


def icon_stalk(img, pal, seed):
    """芹菜 / 韭菜：一束细长茎。"""
    main, dark, light, accent = pal
    for i in range(5):
        cx = 4.2 + i * 1.9
        tip = 3.2 + abs(i - 2) * 0.7
        for (x, y) in poly_pts([(cx - 0.55, 13.6), (cx + 0.55, 13.6), (cx + 0.4, tip), (cx - 0.4, tip)]):
            v = _noise(x // 2, y // 3, seed + i)
            px(img, x, y, light if v > 0.55 else main, 255)
        for y in range(int(tip * U), int(13.6 * U), int(U)):
            px(img, cx * U, y, dark, 160)
    paint(img, oval_pts(8, 12.8, 4.0, 1.4), accent)


def icon_sprout(img, pal, seed):
    """豆芽：细白茎 + 顶上一对小叶。"""
    main, dark, light, accent = pal
    for (cx, tall) in ((5.8, 9.0), (8.0, 11.4), (10.2, 8.2)):
        for (x, y) in poly_pts([(cx - 0.35, 14.0), (cx + 0.35, 14.0), (cx + 0.25, tall), (cx - 0.25, tall)]):
            px(img, x, y, light, 255)
        for y in range(int(tall * U), int(14.0 * U), 2):
            px(img, cx * U - 1, y, dark, 120)
        paint(img, oval_pts(cx - 0.9, tall - 0.6, 1.0, 0.7), main)
        paint(img, oval_pts(cx + 0.9, tall - 0.6, 1.0, 0.7), main)


def icon_long_veg(img, pal, seed):
    """长条瓜菜（黄瓜 / 茄子 / 丝瓜 / 冬瓜）。"""
    main, dark, light, accent = pal
    pts = set(poly_pts([(6.0, 3.0), (10.0, 3.0), (10.8, 12.4), (7.4, 14.0), (5.4, 11.6)]))
    for (x, y) in pts:
        v = 0.5 + 0.5 * _noise(x // 2, y // 3, seed)
        # 左亮右暗
        v += 0.18 if x < 8 * U else -0.12
        px(img, x, y, (dark, main, light, light)[_quantize(v, 3, x, y)], 255)
    for i in range(6):
        xx = 6.4 + i * 0.75
        for y in range(int(4.0 * U), int(13.4 * U), 3):
            px(img, xx * U, y, light, 90)
    outline(img, pts, accent)
    paint(img, poly_pts([(7.4, 2.2), (8.8, 2.2), (8.1, 0.9)]), accent)


def icon_pod(img, pal, seed):
    """豆角：弯曲的豆荚，露出一点豆粒。"""
    main, dark, light, accent = pal
    pts = set()
    for t in range(0, 100):
        f = t / 99.0
        cx = 3.6 + f * 9.0
        cy = 11.6 - math.sin(f * math.pi) * 5.4
        for (x, y) in oval_pts(cx, cy, 1.35, 1.05):
            pts.add((x, y))
    for (x, y) in pts:
        v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.6 else main, 255)
    outline(img, pts, accent)
    for i in range(4):
        fx = 4.6 + i * 2.2
        fy = 11.0 - math.sin((fx - 3.6) / 9.0 * math.pi) * 5.4
        paint(img, oval_pts(fx, fy, 0.55, 0.45), dark)


def icon_round_veg(img, pal, seed):
    """圆形茄果（西红柿 / 辣椒）。"""
    main, dark, light, accent = pal
    sphere(img, 8, 9.0, 4.6, pal, seed, squash=0.94)
    # 蒂
    paint(img, poly_pts([(6.4, 4.8), (9.6, 4.8), (8.0, 2.8)]), accent)
    for (x, y) in oval_pts(8, 4.6, 2.6, 0.9):
        px(img, x, y, accent, 255)


def icon_bulb(img, pal, seed):
    """葱：白葱头 + 绿葱管。"""
    main, dark, light, accent = pal
    for i in range(3):
        cx = 6.0 + i * 2.0
        top = 2.6 + i * 0.9
        for (x, y) in poly_pts([(cx - 0.55, 9.6), (cx + 0.55, 9.6), (cx + 0.4, top), (cx - 0.4, top)]):
            v = _noise(x // 2, y // 3, seed + i)
            px(img, x, y, light if v > 0.5 else main, 255)
    paint(img, oval_pts(8, 11.6, 2.8, 2.4), (245, 246, 238))
    for i in range(3):
        for (x, y) in poly_pts([(6.0, 12.0), (10.0, 12.0), (9.6, 14.2), (6.4, 14.2)]):
            if (x // 2 + y // 3) % 2 == 0:
                px(img, x, y, (222, 222, 210), 255)
    for (x, y) in oval_pts(8, 10.0, 1.0, 1.4):
        px(img, x, y, dark, 120)


def icon_fungus(img, pal, seed):
    """木耳：卷曲的黑褐色耳片。"""
    main, dark, light, accent = pal
    for (cx, cy, rx, ry, rot) in ((6.4, 9.4, 2.8, 2.0, -0.5), (10.0, 7.6, 2.4, 1.8, 0.4),
                                  (9.0, 11.6, 2.0, 1.6, -0.2)):
        pts = set()
        for (x, y) in oval_pts(cx, cy, rx, ry):
            dx, dy = x + 0.5 - cx * U, y + 0.5 - cy * U
            ca, sa = math.cos(rot), math.sin(rot)
            u_, v_ = dx * ca - dy * sa, dx * sa + dy * ca
            if u_ * u_ / ((rx * U) ** 2) + v_ * v_ / ((ry * U) ** 2) <= 1.0:
                pts.add((x, y))
        for (x, y) in pts:
            v = _noise(x // 2, y // 2, seed)
            px(img, x, y, lighter(dark, main, light, v), 255)
        outline(img, pts, accent)


def lighter(dark, main, light, v):
    if v < 0.34:
        return dark
    if v < 0.72:
        return main
    return light


# ======================================================================
# 水果
# ======================================================================

def icon_fruit_round(img, pal, seed):
    sphere(img, 8, 9.4, 4.8, pal, seed, squash=0.96)
    main, dark, light, accent = pal
    paint(img, poly_pts([(7.6, 4.8), (8.6, 4.8), (8.1, 2.8)]), accent)
    paint(img, oval_pts(9.6, 3.4, 1.5, 0.7), accent)


def icon_banana(img, pal, seed):
    main, dark, light, accent = pal
    pts = set()
    for t in range(0, 120):
        f = t / 119.0
        cx = 3.0 + f * 10.0
        cy = 5.0 + math.sin(f * math.pi * 0.9) * 6.4
        for (x, y) in oval_pts(cx, cy, 1.5, 1.2):
            pts.add((x, y))
    for (x, y) in pts:
        v = 0.55 + 0.45 * _noise(x // 2, y // 3, seed)
        px(img, x, y, light if v > 0.6 else main, 255)
    for (x, y) in pts:
        if (y - (5.0 + math.sin(((x / U - 3.0) / 10.0) * math.pi * 0.9) * 6.4) * U) > 0.4 * U:
            px(img, x, y, dark, 190)
    outline(img, pts, accent)
    paint(img, poly_pts([(12.6, 10.6), (13.8, 12.4), (12.4, 12.0)]), accent)


def icon_grape(img, pal, seed):
    main, dark, light, accent = pal
    ground_shadow(img, 8, 14.0, 4.2, 1.2, 55)
    rows = [(3, 5.6), (4, 7.4), (3, 9.2), (2, 11.0)]
    for r, (count, yy) in enumerate(rows):
        start = 8 - (count - 1) * 1.05
        for i in range(count):
            sphere(img, start + i * 2.1, yy, 1.15, pal, seed + r * 5 + i, light=(-0.6, -0.6))
    for (x, y) in poly_pts([(7.8, 4.3), (8.2, 4.3), (8.0, 2.6)]):
        px(img, x, y, accent, 255)


def icon_kiwi(img, pal, seed):
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.4, 4.4, 4.2))
    for (x, y) in pts:
        v = 0.5 + 0.5 * _noise(x // 2, y // 3, seed)
        px(img, x, y, light if v > 0.6 else main, 255)
    outline(img, pts, accent)
    paint(img, oval_pts(8, 9.4, 2.8, 2.6), (150, 190, 96))
    for i in range(12):
        a = i * math.tau / 12
        paint(img, oval_pts(8 + math.cos(a) * 1.7, 9.4 + math.sin(a) * 1.6, 0.24, 0.24), (46, 40, 32))
    paint(img, oval_pts(8, 9.4, 0.6, 0.6), (232, 236, 206))


def icon_mango(img, pal, seed):
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.2, 4.2, 5.0))
    for (x, y) in pts:
        dx = (x + 0.5 - 8 * U) / (4.2 * U)
        dy = (y + 0.5 - 9.2 * U) / (5.0 * U)
        # 芒果一边红一边黄
        v = 0.72 - 0.6 * min(1.0, math.hypot(dx + 0.5, dy + 0.6) / 1.8)
        if dx > 0.25:
            px(img, x, y, (208, 92, 46) if _noise(x, y, seed) > 0.4 else (176, 62, 30), 255)
        else:
            px(img, x, y, (dark, main, light, light)[_quantize(v, 3, x, y)], 255)
    outline(img, pts, accent)
    paint(img, poly_pts([(7.6, 4.4), (8.6, 4.4), (8.1, 2.6)]), accent)


def icon_pineapple(img, pal, seed):
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.8, 3.8, 4.4))
    for (x, y) in pts:
        v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.58 else main, 255)
    # 菱形网纹
    for y in range(int(5.6 * U), int(14.0 * U), max(2, int(U * 0.8))):
        for x in range(int(4.4 * U), int(11.6 * U), max(2, int(U * 0.8))):
            if ((x // 2) + (y // 2)) % 2 == 0:
                px(img, x, y, dark, 150)
    outline(img, pts, accent)
    # 冠芽
    for i in range(5):
        cx = 5.6 + i * 1.2
        paint(img, poly_pts([(cx - 0.4, 5.4), (cx + 0.4, 5.4), (cx + (i - 2) * 0.9, 1.4)]), accent)


# ======================================================================
# 调味料容器
# ======================================================================

def icon_bottle(img, pal, seed, cap=(120, 116, 108)):
    """细口瓶：酱 / 醋 / 酒 / 油。"""
    main, dark, light, accent = pal
    # 瓶身
    body = set(poly_pts([(4.6, 6.4), (11.4, 6.4), (11.4, 14.2), (4.6, 14.2)]))
    body |= set(oval_pts(8, 14.0, 3.4, 0.9))
    for (x, y) in body:
        if y > 6.4 * U:
            px(img, x, y, lighter(dark, main, light, _noise(x // 2, y // 3, seed)), 255)
    # 液面高光
    paint(img, poly_pts([(6.0, 7.4), (7.2, 7.4), (7.2, 13.0), (6.0, 13.0)]), light)
    # 瓶颈 + 瓶盖
    neck = set(poly_pts([(6.8, 4.0), (9.2, 4.0), (9.2, 6.6), (6.8, 6.6)]))
    paint(img, neck, dark)
    paint(img, box_pts(6.4, 2.8, 9.6, 4.2), cap)
    for (x, y) in box_pts(6.4, 2.8, 9.6, 4.2):
        if (x + y) % 3 == 0:
            px(img, x, y, _shade(cap, -0.18), 255)
    outline(img, body | neck, accent)
    # 标签
    paint(img, box_pts(5.6, 9.0, 10.4, 11.6), (238, 232, 208))
    paint(img, box_pts(6.2, 9.8, 9.8, 10.2), accent)


def icon_jar(img, pal, seed, lid=(150, 142, 126)):
    """广口罐：酱料 / 腐乳 / 腌菜 / 高汤。"""
    main, dark, light, accent = pal
    body = set(poly_pts([(3.8, 5.6), (12.2, 5.6), (11.6, 14.4), (4.4, 14.4)]))
    for (x, y) in body:
        v = _noise(x // 2, y // 3, seed)
        px(img, x, y, lighter(dark, main, light, v), 255)
    # 玻璃反光
    paint(img, poly_pts([(5.2, 7.0), (6.4, 7.0), (6.0, 13.2), (4.8, 13.2)]), light)
    outline(img, body, accent)
    # 罐口与盖布
    paint(img, box_pts(3.2, 4.0, 12.8, 5.8), lid)
    for (x, y) in box_pts(3.2, 4.0, 12.8, 5.8):
        if (x + y) % 4 == 0:
            px(img, x, y, _shade(lid, -0.16), 255)
    paint(img, box_pts(5.4, 4.6, 10.6, 5.2), _shade(lid, 0.18))


def icon_sachet(img, pal, seed):
    """香料小包：几只不同形状的香料堆在布上。"""
    main, dark, light, accent = pal
    paint(img, oval_pts(8, 12.8, 5.0, 1.6), (206, 196, 172))
    for (cx, cy, r) in ((5.8, 9.6, 1.7), (10.0, 8.6, 1.5), (8.0, 11.4, 1.4)):
        sphere(img, cx, cy, r, pal, seed, squash=0.9, light=(-0.6, -0.6))


def icon_star(img, pal, seed):
    """八角：八角的星形。"""
    main, dark, light, accent = pal
    pts = set()
    for i in range(8):
        a = i * math.tau / 8 - math.pi / 2
        tip = (8 + math.cos(a) * 4.6, 9.0 + math.sin(a) * 4.6)
        left = (8 + math.cos(a - 0.32) * 1.5, 9.0 + math.sin(a - 0.32) * 1.5)
        right = (8 + math.cos(a + 0.32) * 1.5, 9.0 + math.sin(a + 0.32) * 1.5)
        pts |= set(poly_pts([left, tip, right]))
    for (x, y) in pts:
        v = _noise(x // 2, y // 2, seed)
        px(img, x, y, lighter(dark, main, light, v), 255)
    outline(img, pts, accent)
    paint(img, oval_pts(8, 9.0, 1.2, 1.2), dark)


def icon_bark(img, pal, seed):
    """桂皮：卷起来的树皮。"""
    main, dark, light, accent = pal
    for i in range(3):
        x0 = 4.0 + i * 2.6
        pts = set(poly_pts([(x0, 4.0), (x0 + 2.0, 4.6), (x0 + 1.6, 13.6), (x0 - 0.4, 13.0)]))
        for (x, y) in pts:
            v = 0.45 + 0.55 * _noise(x // 2, y // 3, seed + i * 3)
            px(img, x, y, light if v > 0.6 else main, 255)
        for (x, y) in pts:
            if _noise(x, y, seed + i) < 0.2:
                px(img, x, y, dark, 190)
        outline(img, pts, accent)


def icon_leaf_flat(img, pal, seed):
    """香叶：几片平铺的干叶。"""
    main, dark, light, accent = pal
    for (cx, cy, rot) in ((6.6, 8.6, -0.4), (10.0, 7.4, 0.5), (8.2, 11.8, 0.15)):
        pts = set()
        for (x, y) in oval_pts(cx, cy, 1.9, 3.2):
            dx, dy = x + 0.5 - cx * U, y + 0.5 - cy * U
            ca, sa = math.cos(rot), math.sin(rot)
            u_, v_ = dx * ca - dy * sa, dx * sa + dy * ca
            if u_ * u_ / ((1.9 * U) ** 2) + v_ * v_ / ((3.2 * U) ** 2) <= 1.0:
                pts.add((x, y))
        for (x, y) in pts:
            v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
            px(img, x, y, light if v > 0.6 else main, 255)
        outline(img, pts, accent)
        # 主脉
        for t in range(-3, 4):
            for (x, y) in poly_pts([(cx + math.cos(rot + 1.57) * t * 0.15 - 0.2,
                                     cy + math.sin(rot + 1.57) * t * 0.15 - 0.2),
                                    (cx + math.cos(rot + 1.57) * t * 0.15 + 0.2,
                                     cy + math.sin(rot + 1.57) * t * 0.15 + 0.2)]):
                px(img, x, y, dark, 120)


def icon_dried_chili(img, pal, seed):
    """干辣椒：几根皱巴巴的红辣椒。"""
    main, dark, light, accent = pal
    for i, (cx, cy, rot) in enumerate(((5.4, 8.4, -0.35), (9.4, 7.6, 0.4), (7.8, 11.6, 0.1))):
        pts = set()
        for t in range(0, 40):
            f = t / 39.0
            sx = cx + (f - 0.5) * 5.4
            sy = cy + (f - 0.5) * 4.4 * math.sin(rot)
            for (x, y) in oval_pts(sx, sy, 0.85, 0.68):
                pts.add((x, y))
        for (x, y) in pts:
            v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed + i)
            px(img, x, y, light if v > 0.6 else main, 255)
        for (x, y) in pts:
            if _noise(x, y, seed + i * 9) < 0.18:
                px(img, x, y, dark, 200)
        outline(img, pts, accent)


def icon_paste_ball(img, pal, seed):
    """豆沙：几团搓好的馅。"""
    main, dark, light, accent = pal
    ground_shadow(img, 8, 13.6, 4.6, 1.3, 55)
    for (cx, cy, r) in ((6.0, 10.4, 2.4), (10.2, 10.0, 2.2), (8.0, 6.6, 2.0)):
        sphere(img, cx, cy, r, pal, seed, squash=0.9, light=(-0.55, -0.6))


def icon_tofu_block(img, pal, seed):
    """豆腐：三块 3/4 视角的方豆腐。"""
    main, dark, light, accent = pal
    top = (252, 251, 246)
    mid = (238, 235, 224)
    low = (206, 202, 186)
    for (bx, by, bw, bh) in ((1.4, 3.6, 5.6, 5.2), (8.6, 2.8, 5.6, 5.2), (4.4, 8.6, 7.2, 5.6)):
        x0, y0 = int(bx * U), int(by * U)
        w, h = int(bw * U), int(bh * U)
        th = max(2, int(h * 0.30))
        for yy in range(y0, min(SIZE, y0 + h)):
            for xx in range(x0, min(SIZE, x0 + w)):
                c = top if yy - y0 < th else (mid if xx - x0 < w * 0.42 else low)
                if _noise(xx, yy, seed) < 0.15:
                    c = _shade(c, -0.06)
                px(img, xx, yy, c, 255)
        for xx in range(x0, min(SIZE, x0 + w)):
            px(img, xx, min(SIZE - 1, y0 + th - 1), _shade(accent, 0.3), 255)
            px(img, xx, min(SIZE - 1, y0 + h - 1), accent, 255)
        for yy in range(y0, min(SIZE, y0 + h)):
            px(img, x0, yy, accent, 255)
            px(img, min(SIZE - 1, x0 + w - 1), yy, accent, 255)


# ======================================================================
# 厨具与餐具
# ======================================================================

def icon_tool_knife(img, pal, seed):
    main, dark, light, accent = pal
    # 刀身
    blade = set(poly_pts([(3.4, 9.0), (11.4, 4.0), (12.4, 5.6), (5.0, 11.0)]))
    for (x, y) in blade:
        v = 0.5 + 0.6 * _noise(x // 3, y, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    for (x, y) in blade:
        if y > 9.0 * U:
            px(img, x, y, dark, 190)
    outline(img, blade, accent)
    # 刀柄
    handle = set(poly_pts([(4.4, 10.6), (6.0, 12.2), (3.0, 14.6), (1.8, 13.4)]))
    for (x, y) in handle:
        px(img, x, y, (120, 74, 38) if _noise(x, y, seed + 3) > 0.4 else (86, 52, 26), 255)
    outline(img, handle, (52, 30, 14))


def icon_tool_cleaver(img, pal, seed):
    main, dark, light, accent = pal
    blade = set(poly_pts([(5.0, 3.2), (13.4, 3.2), (13.4, 9.6), (5.0, 9.6)]))
    for (x, y) in blade:
        v = 0.5 + 0.6 * _noise(x // 3, y, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    paint(img, box_pts(5.0, 3.2, 13.4, 4.0), light)
    outline(img, blade, accent)
    handle = set(poly_pts([(1.6, 5.6), (5.2, 5.6), (5.2, 7.6), (1.6, 7.6)]))
    for (x, y) in handle:
        px(img, x, y, (120, 74, 38), 255)
    outline(img, handle, (52, 30, 14))


def icon_tool_spatula(img, pal, seed):
    main, dark, light, accent = pal
    head = set(poly_pts([(4.4, 2.6), (11.6, 2.6), (10.4, 8.4), (5.6, 8.4)]))
    for (x, y) in head:
        v = 0.5 + 0.6 * _noise(x // 2, y, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    for (x, y) in head:
        if (x // 2) % 2 == 0:
            px(img, x, y, dark, 90)
    outline(img, head, accent)
    # 柄
    paint(img, box_pts(7.2, 8.2, 8.8, 13.4), (120, 74, 38))
    paint(img, box_pts(8.8, 8.2, 9.2, 13.4), (72, 44, 22))
    paint(img, box_pts(7.2, 13.0, 8.8, 14.4), (86, 52, 26))


def icon_tool_slotted(img, pal, seed):
    main, dark, light, accent = pal
    bowl = set(oval_pts(8, 5.6, 4.4, 3.0))
    for (x, y) in bowl:
        v = 0.5 + 0.6 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    # 漏孔
    for (cx, cy) in ((6.4, 5.0), (8.0, 4.4), (9.6, 5.0), (6.8, 6.4), (9.2, 6.4), (8.0, 6.8)):
        paint(img, oval_pts(cx, cy, 0.42, 0.36), (0, 0, 0))
        for (x, y) in oval_pts(cx, cy, 0.42, 0.36):
            img.putpixel((x, y), (0, 0, 0, 0))
    outline(img, bowl, accent)
    paint(img, box_pts(7.4, 8.4, 8.6, 13.6), (120, 74, 38))
    paint(img, box_pts(8.6, 8.4, 9.0, 13.6), (72, 44, 22))


def icon_tool_spoon(img, pal, seed):
    main, dark, light, accent = pal
    bowl = set(oval_pts(6.6, 5.0, 3.0, 3.6))
    for (x, y) in bowl:
        v = 0.5 + 0.6 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.5 else main, 255)
    paint(img, oval_pts(6.6, 5.0, 2.0, 2.5), dark)
    outline(img, bowl, accent)
    paint(img, box_pts(6.0, 8.2, 7.2, 13.8), (120, 74, 38))
    paint(img, box_pts(7.2, 8.2, 7.6, 13.8), (72, 44, 22))


def icon_tool_rolling(img, pal, seed):
    main, dark, light, accent = pal
    paint(img, box_pts(3.6, 6.0, 12.4, 9.4), main)
    for (x, y) in box_pts(3.6, 6.0, 12.4, 9.4):
        if _noise(x // 2, y, seed) < 0.22:
            px(img, x, y, dark, 160)
    paint(img, box_pts(3.6, 6.0, 12.4, 6.8), light)
    paint(img, box_pts(3.6, 8.6, 12.4, 9.4), dark)
    paint(img, box_pts(5.6, 9.4, 7.2, 10.2), accent)
    paint(img, box_pts(8.8, 9.4, 10.4, 10.2), accent)


def icon_tool_chopsticks(img, pal, seed):
    main, dark, light, accent = pal
    for i in range(2):
        x0 = 5.0 + i * 2.2
        for (x, y) in poly_pts([(x0, 2.4), (x0 + 1.0, 2.4), (x0 + 2.2, 13.6), (x0 + 1.2, 13.6)]):
            v = _noise(x // 2, y // 4, seed + i)
            px(img, x, y, light if v > 0.5 else main, 255)
        for y in range(int(3.0 * U), int(13.4 * U), 3):
            px(img, (x0 + 1.2) * U, y, dark, 130)
    # 筷头（细端）
    paint(img, poly_pts([(4.6, 2.0), (6.0, 2.0), (5.4, 4.2)]), accent)


def icon_table_saucer(img, pal, seed):
    """小碟子：椭圆浅盘 + 青花圈。"""
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.6, 5.6, 3.8))
    for (x, y) in pts:
        v = 0.55 + 0.5 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    paint(img, oval_pts(8, 9.6, 4.4, 2.9), dark)
    paint(img, oval_pts(8, 10.0, 3.8, 2.4), light)
    outline(img, pts, accent)
    # 青花圈
    for (x, y) in oval_pts(8, 9.6, 3.0, 1.9):
        px(img, x, y, accent, 170)


def icon_table_cup(img, pal, seed):
    """杯子：直筒杯 + 茶色内壁。"""
    main, dark, light, accent = pal
    body = set(poly_pts([(5.0, 4.6), (11.0, 4.6), (10.4, 13.6), (5.6, 13.6)]))
    for (x, y) in body:
        v = 0.5 + 0.55 * _noise(x // 2, y // 3, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    # 杯口
    paint(img, oval_pts(8, 4.8, 3.0, 1.2), dark)
    paint(img, oval_pts(8, 4.9, 2.3, 0.85), (198, 158, 96))
    # 把手
    for (dx, dy, r) in ((3.4, 9.0, 0.0),):
        for (x, y) in oval_pts(11.6, 9.0, 1.6, 2.0):
            px(img, x, y, main, 255)
        for (x, y) in oval_pts(11.6, 9.0, 0.9, 1.2):
            img.putpixel((x, y), (0, 0, 0, 0))
    outline(img, body, accent)


# ======================================================================
# 菜品
# ======================================================================

def _food_chunks(img, pts_set, pal, seed, count, spread, size=1.3, edge=True):
    """在器皿里撒配料块（肉丁 / 菜粒），带一点立体感。

    edge=True 时给每块配一档暗描边 —— 浅色的菜（白切鸡、清蒸鱼）
    放在白瓷盘上如果没有描边就完全看不出轮廓。
    """
    import random
    main, dark, light, accent = pal
    edge_colour = _shade(dark, -0.28)
    rnd = random.Random(seed)
    put = []
    for _ in range(count):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(0, spread)
        put.append((8 + math.cos(a) * d, 8.6 + math.sin(a) * d * 0.62,
                    rnd.uniform(size * 0.7, size * 1.25)))
    # 后面的先画
    put.sort(key=lambda t: t[1])
    for (cx, cy, r) in put:
        pts = [p for p in oval_pts(cx, cy, r, r * 0.78) if p in pts_set]
        if not pts:
            continue
        for (x, y) in pts:
            v = _noise(x // 2, y // 2, seed + int(cx * 10))
            px(img, x, y, light if v > 0.6 else main, 255)
        # 左上高光 + 右下阴影，让块有体积
        for (x, y) in pts:
            if x < cx * U and y < cy * U and _noise(x, y, seed + 1) > 0.55:
                px(img, x, y, light, 255)
            elif _noise(x, y, seed) < 0.16:
                px(img, x, y, dark, 200)
        if edge:
            outline(img, pts, edge_colour)


def _vessel_bowl(img, pal, seed, inside):
    """碗（汤 / 粥 / 面 / 丸子）。inside(cx,cy,r) 由调用方决定内里画什么。"""
    main, dark, light, accent = pal
    # 碗身
    pts = set(poly_pts([(3.0, 7.6), (13.0, 7.6), (11.4, 13.6), (4.6, 13.6)]))
    pts |= set(oval_pts(8, 13.4, 3.4, 0.9))
    for (x, y) in pts:
        v = 0.5 + 0.55 * _noise(x // 2, y // 3, seed)
        px(img, x, y, light if v > 0.6 else main, 255)
    for (x, y) in pts:
        if y > 11.6 * U:
            px(img, x, y, dark, 170)
    # 碗口
    rim = set(oval_pts(8, 7.6, 5.0, 2.0))
    for (x, y) in rim:
        if (x, y) not in pts or y <= 7.6 * U:
            px(img, x, y, light, 255)
    outline(img, pts | rim, accent)
    # 碗内阴影环，让汤面与碗口分开
    for (x, y) in oval_pts(8, 7.7, 4.5, 1.9):
        px(img, x, y, INNER_RING, 255)
    # 内里
    inner = oval_pts(8, 7.8, 4.2, 1.7)
    inside(set(inner), 8, 7.8, 4.2)


# 器皿内圈 / 底部的固定色调：不跟随菜品配色，
# 否则浅色菜（白切鸡、清蒸鱼）放在白瓷盘上会完全看不见。
INNER_RING = (150, 146, 134)
INNER_BASE = (176, 168, 146)


def _vessel_plate(img, pal, seed, inside):
    """盘子（炒菜 / 蒸菜）。"""
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.0, 6.2, 4.6))
    for (x, y) in pts:
        v = 0.55 + 0.5 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    outline(img, pts, accent)
    # 盘内：一圈深色描边 + 一层暖色底，再画菜
    for (x, y) in oval_pts(8, 9.0, 4.9, 3.5):
        px(img, x, y, INNER_RING, 255)
    base = set(oval_pts(8, 9.0, 4.2, 2.9))
    for (x, y) in base:
        v = _noise(x // 2, y // 2, seed + 17)
        px(img, x, y, _shade(INNER_BASE, 0.10) if v > 0.5 else INNER_BASE, 255)
    inside(base, 8, 9.0, 4.6)


def _vessel_platter(img, pal, seed, inside):
    """大拼盘上的整只菜（鸡 / 鸭 / 鹅 / 肘子）。"""
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 10.6, 6.6, 3.6))
    for (x, y) in pts:
        v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
        px(img, x, y, (146, 102, 56) if v > 0.55 else (116, 78, 40), 255)
    outline(img, pts, (72, 48, 24))
    for (x, y) in oval_pts(8, 10.0, 6.3, 3.2):
        px(img, x, y, (110, 74, 40), 255)
    inside(set(oval_pts(8, 10.0, 6.0, 3.0)), 8, 10.0, 6.2)


def _vessel_pot(img, pal, seed, inside):
    """砂锅（炖菜）。"""
    main, dark, light, accent = pal
    pts = set(oval_pts(8, 9.4, 5.6, 4.6))
    for (x, y) in pts:
        v = 0.5 + 0.5 * _noise(x // 2, y // 3, seed)
        px(img, x, y, (86, 90, 98) if v > 0.55 else (54, 58, 66), 255)
    outline(img, pts, (30, 32, 38))
    inside(set(oval_pts(8, 9.6, 4.6, 3.6)), 8, 9.6, 4.8)


def _vessel_cup(img, pal, seed, inside):
    """酒杯 / 茶盏。"""
    main, dark, light, accent = pal
    body = set(poly_pts([(5.6, 6.4), (10.4, 6.4), (9.8, 12.4), (6.2, 12.4)]))
    for (x, y) in body:
        v = 0.5 + 0.55 * _noise(x // 2, y // 3, seed)
        px(img, x, y, light if v > 0.55 else main, 255)
    outline(img, body, accent)
    paint(img, oval_pts(8, 6.6, 2.5, 1.0), dark)
    inside(set(oval_pts(8, 6.8, 2.1, 0.8)), 8, 6.8, 2.1)
    paint(img, box_pts(6.4, 12.6, 9.6, 13.6), accent)


def _fill_liquid(img, pts, pal, seed, level=1.0, gloss=True):
    main, dark, light, accent = pal
    for (x, y) in pts:
        v = 0.45 + 0.5 * _noise(x // 2, y // 2, seed)
        px(img, x, y, light if v > 0.62 else main, 255)
    if gloss:
        for (x, y) in pts:
            if _noise(x, y, seed + 33) < 0.07:
                px(img, x, y, light, 210)


def icon_dish_soup(img, pal, seed):
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed)
        _food_chunks(img, pts, pal, seed + 1, 6, r * 0.72, 0.85)
    _vessel_bowl(img, ((226, 230, 236), (176, 182, 192), (250, 252, 255), (60, 92, 156)),
                 seed, inside)


def icon_congee(img, pal, seed):
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed, gloss=False)
        _food_chunks(img, pts, ((188, 96, 52), (140, 62, 30), (216, 138, 88), (110, 48, 22)),
                     seed + 5, 8, r * 0.78, 0.62)
    _vessel_bowl(img, ((226, 230, 236), (176, 182, 192), (250, 252, 255), (60, 92, 156)),
                 seed, inside)


def icon_noodles(img, pal, seed):
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed, gloss=False)
        # 面条：几条弧线
        for i in range(6):
            for t in range(0, 30):
                f = t / 29.0
                xx = 5.6 + f * 5.0
                yy = 6.8 + math.sin(f * 3.4 + i) * 0.6 + i * 0.10
                if (int(xx * U), int(yy * U)) in pts:
                    px(img, xx * U, yy * U, (238, 226, 190), 255)
        _food_chunks(img, pts, ((110, 156, 74), (72, 112, 46), (150, 190, 108), (52, 84, 30)),
                     seed + 3, 5, r * 0.7, 0.7)
    _vessel_bowl(img, ((226, 230, 236), (176, 182, 192), (250, 252, 255), (60, 92, 156)),
                 seed, inside)


def icon_balls_bowl(img, pal, seed):
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, ((214, 208, 190), (168, 162, 146), (240, 236, 222), (150, 144, 128)),
                     seed, gloss=False)
        for (dx, dy) in ((-1.6, 0.0), (1.6, 0.0), (0.0, -0.5), (0.8, 0.6), (-0.8, 0.6)):
            for (x, y) in oval_pts(8 + dx, 7.8 + dy, 1.25, 1.05):
                if (x, y) in pts:
                    v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed + int(dx * 3))
                    px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
            for (x, y) in oval_pts(8 + dx, 7.8 + dy, 1.25, 1.05):
                if (x, y) in pts and _noise(x, y, seed) < 0.16:
                    px(img, x, y, pal[1], 190)
    _vessel_bowl(img, ((226, 230, 236), (176, 182, 192), (250, 252, 255), (60, 92, 156)),
                 seed, inside)


def _make_plate_dish(pal_chunks, count=7, spread=4.0, size=1.25):
    def painter(img, pal, seed):
        def inside(pts, cx, cy, r):
            _food_chunks(img, pts, pal, seed, count, spread * (r / 4.6), size)
        _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                      seed, inside)
    return painter


def icon_dish_plate(img, pal, seed):
    _make_plate_dish(None)(img, pal, seed)


def icon_dish_fish(img, pal, seed):
    """整条鱼装在盘里。"""
    def inside(pts, cx, cy, r):
        # 鱼身
        body = set(oval_pts(8.2, 9.0, 4.4, 2.0))
        for (x, y) in body:
            if (x, y) in pts:
                v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
                px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        # 尾巴
        for (x, y) in poly_pts([(3.8, 9.0), (1.8, 7.2), (2.6, 9.0), (1.8, 10.8)]):
            if (x, y) in pts:
                px(img, x, y, pal[1], 255)
        # 眼睛
        for (x, y) in oval_pts(11.0, 8.6, 0.4, 0.4):
            if (x, y) in pts:
                px(img, x, y, (30, 26, 22), 255)
        # 姜丝葱丝
        for i in range(6):
            xx = 4.6 + i * 1.3
            for (x, y) in oval_pts(xx, 10.6, 0.5, 0.35):
                if (x, y) in pts:
                    px(img, x, y, (128, 172, 84), 255)
        for (x, y) in body:
            if (x, y) in pts and _noise(x, y, seed) < 0.14:
                px(img, x, y, pal[3], 200)
    _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                  seed, inside)


def icon_dish_whole(img, pal, seed):
    """整只禽（鸡 / 鸭 / 鹅）：俯视的整鸡造型。"""
    def inside(pts, cx, cy, r):
        # 身体
        for (x, y) in oval_pts(8.4, 10.0, 4.4, 2.6):
            if (x, y) in pts:
                v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
                px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        # 腿
        for dx in (-2.2, 2.2):
            for (x, y) in oval_pts(8.4 + dx, 11.4, 1.0, 1.4):
                if (x, y) in pts:
                    px(img, x, y, pal[1], 255)
            for (x, y) in oval_pts(8.4 + dx, 12.4, 1.2, 0.7):
                if (x, y) in pts:
                    px(img, x, y, (222, 190, 140), 255)
        # 头颈
        for (x, y) in oval_pts(8.4, 7.4, 1.6, 1.4):
            if (x, y) in pts:
                px(img, x, y, pal[2], 255)
        for (x, y) in poly_pts([(7.4, 6.6), (8.6, 6.6), (8.0, 5.0)]):
            if (x, y) in pts:
                px(img, x, y, (196, 148, 60), 255)
        for (x, y) in oval_pts(7.8, 7.2, 0.28, 0.28):
            if (x, y) in pts:
                px(img, x, y, (30, 26, 22), 255)
        # 油亮
        for i in range(5):
            for (x, y) in oval_pts(5.6 + i * 1.4, 9.0 + (i % 2) * 1.2, 0.5, 0.28):
                if (x, y) in pts:
                    px(img, x, y, _shade(pal[2], 0.25), 200)
    _vessel_platter(img, ((146, 102, 56), (110, 74, 38), (188, 140, 88), (78, 50, 24)),
                    seed, inside)


def icon_meatball(img, pal, seed):
    """丸子 / 狮子头。"""
    def inside(pts, cx, cy, r):
        for (dx, dy, rr) in ((0.0, 0.0, 2.6), (-2.6, 0.8, 1.8), (2.6, 0.8, 1.8)):
            for (x, y) in oval_pts(8 + dx, 9.2 + dy, rr, rr * 0.82):
                if (x, y) in pts:
                    v = 0.45 + 0.55 * _noise(x // 2, y // 2, seed + int(dx * 4))
                    px(img, x, y, pal[2] if v > 0.6 else pal[0], 255)
            for (x, y) in oval_pts(8 + dx - rr * 0.3, 9.2 + dy - rr * 0.35, rr * 0.3, rr * 0.22):
                if (x, y) in pts:
                    px(img, x, y, _shade(pal[2], 0.22), 255)
    _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                  seed, inside)


def icon_dish_pot(img, pal, seed):
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed)
        _food_chunks(img, pts, ((198, 150, 92), (150, 106, 56), (222, 182, 130), (118, 80, 40)),
                     seed + 2, 9, r * 0.78, 1.0)
    _vessel_pot(img, pal, seed, inside)


def icon_braised_block(img, pal, seed):
    """东坡肉 / 红烧肉：几块方形肉，皮朝上。"""
    def inside(pts, cx, cy, r):
        for (dx, dy, w, h) in ((0.0, 0.0, 3.6, 2.8), (-2.6, 1.6, 2.6, 2.2), (2.6, 1.4, 2.6, 2.2)):
            box = set(poly_pts([(8 + dx - w / 2, 8.6 + dy - h / 2), (8 + dx + w / 2, 8.6 + dy - h / 2),
                                (8 + dx + w / 2, 8.6 + dy + h / 2), (8 + dx - w / 2, 8.6 + dy + h / 2)]))
            for (x, y) in box & pts:
                v = _noise(x // 2, y // 2, seed + int(dx * 3))
                # 上沿是皮（深红亮），下面是肉
                if y < (8.6 + dy - h / 2 + 0.7) * U:
                    px(img, x, y, (176, 58, 40) if v > 0.4 else (138, 40, 26), 255)
                else:
                    px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
            outline(img, box & pts, pal[1])
    _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                  seed, inside)


def icon_steamed_plate(img, pal, seed):
    """蒸菜：盘上盖着蒸汽感的食材。"""
    def inside(pts, cx, cy, r):
        _food_chunks(img, pts, pal, seed, 8, 4.0, 1.15)
        # 热气
        for i in range(3):
            for t in range(0, 26):
                f = t / 25.0
                xx = 6.2 + i * 1.8 + math.sin(f * 5.0 + i) * 0.5
                yy = 6.6 - f * 4.4
                if (int(xx * U), int(yy * U)) in pts:
                    px(img, xx * U, yy * U, (240, 244, 248), 90)
    _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                  seed, inside)


def icon_crab(img, pal, seed):
    """蟹：俯视的蟹壳 + 蟹钳 + 蟹脚。"""
    def inside(pts, cx, cy, r):
        # 脚
        for side in (-1, 1):
            for i in range(3):
                for (x, y) in poly_pts([(8 + side * 3.2, 8.4 + i * 1.1),
                                        (8 + side * 5.6, 7.8 + i * 1.4),
                                        (8 + side * 5.6, 8.4 + i * 1.4)]):
                    if (x, y) in pts:
                        px(img, x, y, pal[1], 255)
        # 蟹钳
        for side in (-1, 1):
            for (x, y) in oval_pts(8 + side * 4.6, 6.6, 1.3, 1.6):
                if (x, y) in pts:
                    px(img, x, y, pal[0], 255)
        # 壳
        for (x, y) in oval_pts(8, 9.0, 3.4, 2.6):
            if (x, y) in pts:
                v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed)
                px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        # 壳上的纹
        for i in range(3):
            for (x, y) in oval_pts(6.6 + i * 1.4, 9.0, 0.3, 1.6):
                if (x, y) in pts:
                    px(img, x, y, pal[1], 180)
        # 眼
        for dx in (-0.9, 0.9):
            for (x, y) in oval_pts(8 + dx, 6.6, 0.28, 0.28):
                if (x, y) in pts:
                    px(img, x, y, (28, 24, 20), 255)
    _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                  seed, inside)


def icon_rice_dish(img, pal, seed):
    """盖饭 / 糯米饭：碗里堆尖的饭 + 配料。"""
    def inside(pts, cx, cy, r):
        _food_chunks(img, pts, ((246, 244, 232), (206, 202, 186), (255, 254, 248), (180, 174, 156)),
                     seed, 16, r * 0.8, 0.62)
        _food_chunks(img, pts, pal, seed + 7, 5, r * 0.6, 1.0)
    _vessel_bowl(img, ((226, 230, 236), (176, 182, 192), (250, 252, 255), (60, 92, 156)),
                 seed, inside)


def icon_dumpling(img, pal, seed):
    """饺子 / 艾饺：三只月牙饺。"""
    ground_shadow(img, 8, 13.6, 5.0, 1.3, 55)
    for (cx, cy, w, rot) in ((5.4, 10.4, 2.6, -0.15), (10.4, 10.0, 2.5, 0.15), (8.0, 6.6, 2.7, 0.0)):
        pts = set()
        for (x, y) in oval_pts(cx, cy, w, w * 0.62):
            pts.add((x, y))
        for (x, y) in pts:
            v = 0.55 + 0.45 * _noise(x // 2, y // 2, seed + int(cx))
            px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        # 褶子
        for i in range(5):
            xx = cx - w * 0.7 + i * (w * 0.35)
            for (x, y) in poly_pts([(xx, cy - w * 0.5), (xx + 0.35, cy - w * 0.5), (xx + 0.2, cy + w * 0.15)]):
                if (x, y) in pts:
                    px(img, x, y, pal[1], 220)
        outline(img, pts, pal[3])


def icon_zongzi(img, pal, seed):
    """粽子：箬叶包的三角粽 + 扎绳。"""
    ground_shadow(img, 8, 13.8, 5.0, 1.3, 55)
    for (ox, oy, sc) in ((5.2, 10.2, 0.92), (10.6, 10.0, 0.9), (8.0, 6.4, 1.0)):
        body = set(poly_pts([(8 + (ox - 8) * 0.9, 13.0), (ox - 2.6 * sc, 9.6 * sc + oy * 0.1 + 3.2),
                             (ox + 2.6 * sc, 9.6 * sc + oy * 0.1 + 3.2)]))
        # 用更稳的三角：底边 + 顶点，围绕 (ox, oy)
        body = set(poly_pts([(ox - 2.5 * sc, oy + 3.0 * sc),
                             (ox + 2.5 * sc, oy + 3.0 * sc),
                             (ox, oy - 3.2 * sc)]))
        for (x, y) in body:
            v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed + int(ox))
            px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        # 叶脉
        for i in range(4):
            for (x, y) in poly_pts([(ox - 2.0 * sc + i * 1.2 * sc, oy + 2.8 * sc),
                                   (ox - 1.8 * sc + i * 1.2 * sc, oy + 2.8 * sc),
                                   (ox, oy - 3.0 * sc)]):
                if (x, y) in body:
                    px(img, x, y, pal[1], 150)
        # 扎绳
        for yy in (oy - 0.4 * sc, oy + 1.4 * sc):
            for (x, y) in poly_pts([(ox - 2.4 * sc, yy), (ox + 2.4 * sc, yy),
                                    (ox + 2.4 * sc, yy + 0.45 * sc), (ox - 2.4 * sc, yy + 0.45 * sc)]):
                if (x, y) in body:
                    px(img, x, y, (186, 156, 96), 235)
        outline(img, body, pal[3])


def icon_mooncake(img, pal, seed):
    """月饼：圆饼 + 花纹 + 侧面的花边。"""
    ground_shadow(img, 8, 13.6, 5.0, 1.3, 55)
    for (ox, oy) in ((6.4, 9.6), (10.4, 9.2)):
        side = set(poly_pts([(ox - 3.0, oy - 2.6), (ox + 3.0, oy - 2.6),
                             (ox + 2.8, oy + 2.8), (ox - 2.8, oy + 2.8)]))
        for (x, y) in side:
            v = _noise(x // 2, y // 3, seed)
            px(img, x, y, pal[1] if v > 0.5 else pal[0], 255)
        top = set(oval_pts(ox, oy - 2.4, 3.0, 1.6))
        for (x, y) in top:
            px(img, x, y, pal[2], 255)
        outline(img, side | top, pal[3])
        # 花纹
        for i in range(6):
            a = i * math.tau / 6
            for (x, y) in oval_pts(ox + math.cos(a) * 1.5, oy - 0.4 + math.sin(a) * 0.8, 0.38, 0.3):
                px(img, x, y, pal[3], 220)
        paint(img, oval_pts(ox, oy - 0.4, 0.5, 0.4), pal[3])


def icon_cake_slice(img, pal, seed):
    """年糕 / 重阳糕：切片的糕 + 上面的枣。"""
    ground_shadow(img, 8, 13.6, 5.0, 1.3, 55)
    for i, (cx, cy) in enumerate(((6.0, 10.6), (10.0, 10.2), (8.0, 7.0))):
        slab = set(poly_pts([(cx - 2.8, cy + 1.8), (cx + 2.8, cy + 1.8),
                             (cx + 2.6, cy - 1.6), (cx - 2.6, cy - 1.6)]))
        for (x, y) in slab:
            v = 0.5 + 0.5 * _noise(x // 2, y // 3, seed + i)
            px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        paint(img, poly_pts([(cx - 2.6, cy - 1.6), (cx + 2.6, cy - 1.6),
                             (cx + 2.4, cy - 0.7), (cx - 2.4, cy - 0.7)]), pal[2])
        outline(img, slab, pal[3])
        for (dx, dy) in ((-1.4, 0.2), (1.4, 0.4)):
            paint(img, oval_pts(cx + dx, cy + dy, 0.55, 0.45), (168, 46, 34))


def icon_cookie(img, pal, seed):
    """巧果：几只油炸的小花形点心。"""
    ground_shadow(img, 8, 13.6, 5.0, 1.3, 55)
    for (cx, cy, r) in ((5.8, 10.4, 2.3), (10.2, 9.8, 2.1), (8.0, 6.6, 2.0)):
        pts = set()
        for i in range(6):
            a = i * math.tau / 6
            pts |= set(oval_pts(cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45,
                                r * 0.55, r * 0.55))
        for (x, y) in pts:
            v = 0.5 + 0.5 * _noise(x // 2, y // 2, seed + int(cx))
            px(img, x, y, pal[2] if v > 0.55 else pal[0], 255)
        for (x, y) in pts:
            if _noise(x, y, seed + 5) < 0.14:
                px(img, x, y, pal[1], 200)
        outline(img, pts, pal[3])


def icon_spring_roll(img, pal, seed):
    """春卷：三只金黄的卷。"""
    ground_shadow(img, 8, 13.6, 5.2, 1.3, 55)
    for (cx, cy, rot) in ((5.8, 10.4, -0.25), (10.2, 9.8, 0.3), (8.0, 7.4, 0.05)):
        pts = set()
        for t in range(0, 40):
            f = t / 39.0
            sx = cx + (f - 0.5) * 5.6 * math.cos(rot)
            sy = cy + (f - 0.5) * 5.6 * math.sin(rot)
            for (x, y) in oval_pts(sx, sy, 1.1, 0.95):
                pts.add((x, y))
        for (x, y) in pts:
            v = 0.5 + 0.55 * _noise(x // 2, y // 2, seed + int(cx))
            px(img, x, y, pal[2] if v > 0.5 else pal[0], 255)
        # 卷皮纹
        for i in range(4):
            for (x, y) in poly_pts([(cx - 2.0 + i * 1.3, cy - 0.9), (cx - 1.8 + i * 1.3, cy - 0.9),
                                    (cx - 1.6 + i * 1.3, cy + 0.9), (cx - 1.8 + i * 1.3, cy + 0.9)]):
                if (x, y) in pts:
                    px(img, x, y, pal[1], 170)
        outline(img, pts, pal[3])


def icon_cured_meat(img, pal, seed):
    """腊肉：挂在绳上的几块腌肉。"""
    for (x, y) in poly_pts([(3.2, 3.0), (12.8, 3.0), (12.8, 3.4), (3.2, 3.4)]):
        px(img, x, y, (186, 156, 96), 255)
    for (cx, h) in ((5.4, 4.4), (8.0, 4.0), (10.6, 4.6)):
        pts = set(poly_pts([(cx - 1.3, 3.4), (cx + 1.3, 3.4), (cx + 1.1, h + 4.6), (cx - 1.1, h + 4.6)]))
        for (x, y) in pts:
            v = 0.5 + 0.5 * _noise(x // 2, y // 3, seed + int(cx))
            # 上端肥肉偏白，下端瘦肉偏红
            if y > (h + 2.0) * U:
                px(img, x, y, (176, 84, 48) if v > 0.4 else (132, 58, 32), 255)
            else:
                px(img, x, y, (240, 222, 200) if v > 0.5 else (214, 188, 160), 255)
        outline(img, pts, (86, 46, 24))


def icon_wine_cup(img, pal, seed):
    """菊花酒：小酒盏 + 酒液 + 一朵菊花。"""
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed)
    _vessel_cup(img, ((226, 230, 236), (176, 182, 192), (250, 252, 255), (60, 92, 156)),
                seed, inside)
    # 飘着的菊花
    for i in range(8):
        a = i * math.tau / 8
        paint(img, oval_pts(10.6 + math.cos(a) * 1.0, 4.2 + math.sin(a) * 1.0, 0.42, 0.42),
              (232, 196, 84))
    paint(img, oval_pts(10.6, 4.2, 0.4, 0.4), (196, 138, 40))


def icon_shredded(img, pal, seed):
    """切好的丝：一小把细长条。"""
    main, dark, light, accent = pal
    import random
    rnd = random.Random(seed)
    ground_shadow(img, 8, 13.4, 5.0, 1.3, 55)
    strands = []
    for i in range(14):
        base_x = 3.4 + i * 0.68
        lean = rnd.uniform(-1.4, 1.4)
        strands.append((base_x, lean))
    strands.sort(key=lambda t: t[1])
    for (base_x, lean) in strands:
        for t in range(0, 34):
            f = t / 33.0
            sx = base_x + lean * f + rnd.uniform(-0.06, 0.06)
            sy = 3.6 + f * 9.4
            for (x, y) in oval_pts(sx, sy, 0.34, 0.30):
                c = light if f < 0.45 else (main if f < 0.8 else dark)
                px(img, x, y, c, 255)
    # 扎起来的一段
    for (x, y) in poly_pts([(6.0, 6.4), (10.0, 6.4), (10.0, 7.2), (6.0, 7.2)]):
        px(img, x, y, accent, 220)


def icon_fillet(img, pal, seed):
    """鱼片：三片斜切的鱼柳。"""
    main, dark, light, accent = pal
    ground_shadow(img, 8, 13.4, 5.0, 1.3, 55)
    for i, (cx, cy) in enumerate(((6.0, 10.6), (10.0, 9.6), (8.0, 6.4))):
        pts = set(poly_pts([(cx - 2.6, cy + 1.4), (cx + 2.4, cy - 1.0),
                            (cx + 2.8, cy + 0.4), (cx - 2.2, cy + 2.4)]))
        for (x, y) in pts:
            v = _noise(x // 2, y // 2, seed + i * 3)
            px(img, x, y, light if v > 0.6 else main, 255)
        # 切片纹
        for k in range(3):
            xx = cx - 1.6 + k * 1.6
            for (x, y) in poly_pts([(xx, cy + 2.0), (xx + 0.28, cy + 2.0),
                                    (xx - 1.6, cy - 0.8)]):
                if (x, y) in pts:
                    px(img, x, y, dark, 170)
        outline(img, pts, accent)


def icon_braised(img, pal, seed):
    """红烧 / 葱烧类：盘里一汪油亮的深色汁 + 食材块。"""
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed)
        _food_chunks(img, pts, ((196, 148, 88), (146, 102, 54), (222, 180, 126), (114, 76, 38)),
                     seed + 4, 8, r * 0.76, 1.15)
        # 收汁的亮边
        for (x, y) in pts:
            if _noise(x, y, seed + 9) < 0.10:
                px(img, x, y, (232, 168, 92), 190)
    _vessel_plate(img, ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
                  seed, inside)


def icon_mapo(img, pal, seed):
    """麻婆豆腐：深色砂锅 + 红油 + 白豆腐丁 + 葱花 + 花椒。"""
    def inside(pts, cx, cy, r):
        _fill_liquid(img, pts, pal, seed)
        # 豆腐丁
        for (dx, dy, w) in ((-1.8, -1.0, 1.0), (1.4, -1.4, 0.9), (-1.2, 1.2, 1.0),
                            (1.8, 1.0, 0.8), (0.2, 0.0, 0.85)):
            box = set(poly_pts([(8 + dx - w, 7.8 + dy - w * 0.8), (8 + dx + w, 7.8 + dy - w * 0.8),
                                (8 + dx + w, 7.8 + dy + w * 0.8), (8 + dx - w, 7.8 + dy + w * 0.8)])) & pts
            for (x, y) in box:
                px(img, x, y, (250, 249, 243) if y < (7.8 + dy) * U else (234, 231, 218), 255)
            outline(img, box, (176, 172, 156))
        # 葱花
        import random
        rnd = random.Random(seed + 3)
        for _ in range(12):
            a = rnd.uniform(0, math.tau)
            d = rnd.uniform(0, 2.6)
            sx, sy = 8 + math.cos(a) * d, 7.8 + math.sin(a) * d * 0.6
            for (x, y) in oval_pts(sx, sy, 0.34, 0.26):
                if (x, y) in pts:
                    px(img, x, y, (110, 164, 68), 255)
        # 花椒
        for (dx, dy) in ((-2.4, 1.4), (2.2, -0.8), (0.6, 1.8)):
            for (x, y) in oval_pts(8 + dx, 7.8 + dy, 0.32, 0.32):
                if (x, y) in pts:
                    px(img, x, y, (56, 34, 22), 255)
    _vessel_pot(img, pal, seed, inside)


# ======================================================================
# 调度表
# ======================================================================

PAINTERS = {
    # 谷物 / 粉类
    "grain": icon_grain, "ear": icon_ear, "corn": icon_corn,
    "powder": icon_powder, "crystal": icon_crystal,
    # 豆 / 颗粒
    "beans": icon_beans, "seeds": icon_seeds, "nuts": icon_nuts,
    "berries": icon_berries, "cherries": icon_cherries, "flowers": icon_flowers,
    "paste_ball": icon_paste_ball,
    # 根茎
    "tuber": icon_tuber, "ginger": icon_ginger, "garlic": icon_garlic, "shoot": icon_shoot,
    # 叶菜 / 茎 / 瓜
    "leafy": icon_leafy, "stalk": icon_stalk, "sprout": icon_sprout,
    "long_veg": icon_long_veg, "pod": icon_pod, "round_veg": icon_round_veg,
    "bulb": icon_bulb, "fungus": icon_fungus,
    # 水果
    "fruit_round": icon_fruit_round, "banana": icon_banana, "grape": icon_grape,
    "kiwi": icon_kiwi, "mango": icon_mango, "pineapple": icon_pineapple,
    # 调味料容器
    "bottle": icon_bottle, "jar": icon_jar, "sachet": icon_sachet, "star": icon_star,
    "bark": icon_bark, "leaf_flat": icon_leaf_flat, "dried_chili": icon_dried_chili,
    # 厨具餐具
    "tool_knife": icon_tool_knife, "tool_cleaver": icon_tool_cleaver,
    "tool_spatula": icon_tool_spatula, "tool_slotted": icon_tool_slotted,
    "tool_spoon": icon_tool_spoon, "tool_rolling": icon_tool_rolling,
    "tool_chopsticks": icon_tool_chopsticks,
    "table_saucer": icon_table_saucer, "table_cup": icon_table_cup,
    # 食材方块 / 半成品
    "tofu_block": icon_tofu_block, "shredded": icon_shredded, "fillet": icon_fillet,
    # 菜品
    "dish_soup": icon_dish_soup, "congee": icon_congee, "noodles": icon_noodles,
    "balls_bowl": icon_balls_bowl, "rice_dish": icon_rice_dish,
    "dish_plate": icon_dish_plate, "braised": icon_braised, "dish_fish": icon_dish_fish,
    "dish_whole": icon_dish_whole, "meatball": icon_meatball,
    "dish_pot": icon_dish_pot, "braised_block": icon_braised_block,
    "steamed_plate": icon_steamed_plate, "crab": icon_crab, "mapo": icon_mapo,
    "dumpling": icon_dumpling, "zongzi": icon_zongzi, "mooncake": icon_mooncake,
    "cake_slice": icon_cake_slice, "cookie": icon_cookie, "spring_roll": icon_spring_roll,
    "cured_meat": icon_cured_meat, "wine_cup": icon_wine_cup,
}


def draw(kind, palette, seed):
    """按 kind 画一张 64x64 图标。palette 是 4 档颜色元组。"""
    painter = PAINTERS.get(kind)
    if painter is None:
        raise KeyError("没有 %s 的画法，请在 texture_icons.PAINTERS 里登记" % kind)
    img = blank()
    painter(img, palette, seed)
    return img
