# -*- coding: utf-8 -*-
"""农作物（蔬菜 / 谷物 / 豆类）与它们的种子的精细画法。

为什么单独开一个文件
--------------------
`texture_icons.py` 里同类作物共用一个画法，于是 5 种瓜长得一模一样、
4 种叶菜只有颜色不同 —— 玩家根本认不出哪个是黄瓜、哪个是冬瓜。
这里改成 **一种作物一套画法**：

* 黄瓜带刺瘤、冬瓜有白霜、丝瓜有棱、苦瓜满身瘤皱、茄子紫皮带萼；
* 白菜是紧实的叶球，小白菜是摊开的散叶，菠菜是深绿尖叶束，香菜是羽状裂叶；
* 萝卜是长圆锥带绿缨，红薯是纺锤块根，山药是细长棒，芋头是圆球带芽。

分辨率
------
这些图标用 **64x64**（其余物品仍是 16x16 的原版分辨率）。
农作物的辨识度全在形体细节上（叶脉、瓜棱、瘤点、种脐），16x16 画不下。
Minecraft 的方块图集与物品图集都允许一张图里混着不同尺寸的贴图。

坐标约定
--------
和其它图标一致：坐标是"原版像素"（0~16），由 `texture_icons.U` 换算到实际像素。
所以同一套画法在 16 / 32 / 64 下都能出图，只是细节多少不同。
"""

import math
import random

# texture_icons 在第一次用到时把自己注入进来（避免循环 import）
TI = None


def bind(module):
    global TI
    TI = module


# ======================================================================
# 小工具
# ======================================================================

def _rng(seed, salt=0):
    return random.Random((seed + 1) * 7919 + salt * 104729)


def _pick(pal, value, levels=4):
    """按 0..1 的亮度取调色板里的一档（暗 -> 主 -> 亮 -> 点缀）。"""
    dark, main, light, accent = pal
    i = int(max(0.0, min(0.9999, value)) * (len(pal) - 1) + 0.5)
    return (dark, main, light, accent)[min(3, i)]


def _shadev(colour, v):
    """把亮度值当明暗修正用。"""
    return TI._shade(colour, v)


# 画叶菜时反复用到的几个"局部配色"：不进 content_data 的调色板，
# 因为它们只在这几个画法里出现（菜帮、绿缨、萼片…）。
LEAF_GREEN = ((104, 152, 62), (62, 104, 38), (142, 190, 94), (44, 78, 30))
LEAF_DEEP = ((74, 122, 54), (42, 84, 34), (108, 156, 78), (30, 62, 26))
CALYX_GREEN = ((96, 140, 58), (60, 96, 36), (132, 176, 86), (42, 70, 28))
PALE_FLESH = ((242, 242, 234), (194, 194, 184), (252, 252, 248), (224, 222, 210))
GLASS_BODY = ((232, 226, 200), (186, 178, 152), (250, 246, 228), (206, 196, 168))


# ======================================================================
# 形状基元
# ======================================================================

# 光从左上来；用来给“横截坐标”定正负号，保证总是受光侧为正
LIGHT_X, LIGHT_Y = -0.7071, -0.7071


def _rim(img, mask, shade, s_min=0.55):
    """轮廓：除了最强的受光边，其余边界都压暗一档，把外形交代清楚。

    ``s`` 是横截坐标，但**已按受光方向归一**（正 = 朝光）。所以“只保留受光边”
    这句话对竖着的黄瓜和横着的萝卜同样成立。
    """
    for (x, y), (t, s) in mask.items():
        edge = ((x + 1, y) not in mask or (x, y + 1) not in mask
                or (x - 1, y) not in mask or (x, y - 1) not in mask)
        if edge and s < s_min:
            c = shade(t, s, x, y)
            if c is not None:
                TI.px(img, x, y, TI._shade(c, -0.40), 255)


def _body(img, path, half, shade, seed=0, samples=56, outline=True):
    """把一条弯曲的"管状躯体"（瓜 / 茄子 / 豆荚 / 叶）画出来。

    * ``path(t) -> (cx, cy)``   轴线，原版像素
    * ``half(t) -> 半宽``
    * ``shade(t, s, x, y) -> (r,g,b) | None``
      ``s`` 是横截坐标，**已按受光方向归一**：+1 = 最朝光的那一侧，-1 = 背光侧；
      返回 None 表示跳过该像素
    """
    U = TI.U
    mask = {}
    for i in range(samples + 1):
        t = i / float(samples)
        cx, cy = path(t)
        h = half(t)
        if h <= 0.12:
            continue
        e = 1e-3
        ax, ay = path(max(0.0, t - e))
        bx, by = path(min(1.0, t + e))
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / ln, tx / ln
        # 法线有可能指向背光侧，视路径方向而定 —— 这里统一翻正，
        # 否则“竖着的黄瓜”和“横着的萝卜”会一个亮左边、一个亮下边。
        flip = 1.0 if (nx * LIGHT_X + ny * LIGHT_Y) >= 0.0 else -1.0
        for (x, y) in TI.oval_pts(cx, cy, h, h):
            dx = (x + 0.5 - cx * U) / U
            dy = (y + 0.5 - cy * U) / U
            s = flip * (dx * nx + dy * ny) / h
            if -1.0 <= s <= 1.0:
                mask.setdefault((x, y), (t, s))
    if not mask:
        return {}
    for (x, y), (t, s) in mask.items():
        c = shade(t, s, x, y)
        if c is not None:
            TI.px(img, x, y, c, 255)
    if outline:
        _rim(img, mask, shade)
    return mask


def _tube_shade(pal, seed, levels=4, bias=0.56, spread=0.62, extra=None, grain=0.14):
    """圆柱面着色回调。``extra(t, s, x, y, v)`` 可以再调亮度（条纹 / 瘤点）。"""
    table = (pal[1], pal[0], pal[2], pal[3])
    if extra is None:
        def extra(t, s, x, y, v):
            return v

    def shade(t, s, x, y):
        v = bias + spread * s
        v += (TI._noise(x, y, seed) - 0.5) * grain
        v = extra(t, s, x, y, v)
        return table[TI._quantize(max(0.0, min(1.0, v)), levels, x, y)]
    return shade


def _leaf_profile(t, width):
    """叶片的半宽曲线：基部窄、中前段最宽、尖端收成一点。"""
    return width * (math.sin(math.pi * (0.12 + 0.88 * t)) ** 0.70) * (1.0 - 0.45 * t)


def _leaf(img, bx, by, tx, ty, width, pal, seed, curve=0.0, midrib=True,
          levels=3, bias=0.60, leaf_edge=True):
    """一片尖叶。``curve`` > 0 时叶子朝法线正方向弯（做出自然的外翻）。"""
    dx, dy = tx - bx, ty - by
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln

    def path(t):
        bend = curve * (t ** 1.5)
        return (bx + dx * t + nx * bend, by + dy * t + ny * bend)

    def half(t):
        return _leaf_profile(t, width)

    def extra(t, s, x, y, v):
        if midrib and abs(s) < 0.09:
            return v - 0.62
        if leaf_edge and abs(abs(s) - 0.74) < 0.10:
            return v + 0.24
        return v

    shade = _tube_shade(pal, seed, levels=levels, bias=bias, spread=0.30, extra=extra,
                        grain=0.16)
    return _body(img, path, half, shade, seed, samples=44)


def _stalk(img, x0, y0, x1, y1, w0, w1, pal, seed, ribs=0, levels=3):
    """一根茎（葱管 / 菜帮 / 叶柄）。``ribs`` > 0 时画出纵向凹槽。"""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln

    def path(t):
        return (x0 + dx * t, y0 + dy * t)

    def half(t):
        return w0 + (w1 - w0) * t

    def extra(t, s, x, y, v):
        if ribs:
            g = math.sin((s + 1.0) * math.pi * ribs)
            v += 0.16 if g > 0.55 else (-0.16 if g < -0.55 else 0.0)
        return v

    shade = _tube_shade(pal, seed, levels=levels, bias=0.62, spread=0.50,
                        extra=extra, grain=0.10)
    return _body(img, path, half, shade, seed + 17, samples=40)


def _heap(img, cx, cy, r, count, one, seed, squash=0.78, salt=3, shadow=True):
    """一堆颗粒。``one(x, y, ang, i, rnd)`` 画一颗；按 y 排序，近的盖远的。"""
    if shadow:
        TI.ground_shadow(img, cx, cy + r * squash + 1.4, r * 0.96, 1.5, 55)
    rnd = _rng(seed, salt)
    items = []
    for i in range(count):
        a = rnd.uniform(0.0, math.tau)
        d = r * (rnd.random() ** 0.60)
        items.append((cy + math.sin(a) * d * squash, cx + math.cos(a) * d,
                      rnd.uniform(-60.0, 60.0), i))
    items.sort()
    for (py_, px_, ang, i) in items:
        one(px_, py_, ang, i, rnd)


def _grain_one(rx, ry, pinch=0.0, hilum=0.24, shade_scale=1.0):
    """把一个椭球谷粒包成 `_heap` 需要的 one 回调。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img=_current_img[0], cx=x, cy=y, rx=rx, ry=ry, deg=ang,
                      pal=_current_pal[0], seed=int(rnd.random() * 1e6),
                      pinch=pinch, hilum=hilum, shade=shade_scale)
    return one


def _grain_one(rx, ry, pinch=0.0, hilum=0.24, shade_scale=1.0):
    """把一个椭球谷粒包成 `_heap` 需要的 one 回调。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img=_current_img[0], cx=x, cy=y, rx=rx, ry=ry, deg=ang,
                      pal=_current_pal[0], seed=int(rnd.random() * 1e6),
                      pinch=pinch, hilum=hilum, shade=shade_scale)
    return one


# `_heap` 的 one 回调拿不到 img/pal 时用得上（单线程，够用）
_current_img = [None]
_current_pal = [None]


def _beans(img, pal, cx, cy, r, specs, count, seed, squash=0.78):
    """一把豆子 / 谷粒：specs 是 (rx, ry, pinch, hilum) 的列表，循环取用。"""
    def one(x, y, ang, i, rnd):
        rx, ry, pinch, hilum = specs[i % len(specs)]
        TI._draw_bean(img, x, y, rx, ry, ang, pal,
                      seed=int(rnd.random() * 1e6), pinch=pinch, hilum=hilum)
    _heap(img, cx, cy, r, count, one, seed, squash=squash)


def _calyx(img, cx, cy, r, pal, seed, points=5, tilt=0.0):
    """果蒂：一小撮萼片 + 一小段柄（番茄 / 茄子 / 辣椒共用）。"""
    main, dark, light, accent = pal
    for i in range(points):
        a = tilt + (i / float(points)) * math.tau
        tipx = cx + math.cos(a) * r * 1.45
        tipy = cy + math.sin(a) * r * 0.78
        _leaf(img, cx, cy, tipx, tipy, r * 0.34, pal, seed + i * 13, midrib=False,
              levels=3, bias=0.66)
    TI.paint(img, TI.oval_pts(cx, cy, r * 0.42, r * 0.34), dark)
    _stalk(img, cx, cy, cx, cy - r * 1.5, r * 0.20, r * 0.15, pal, seed + 71, levels=3)


# ======================================================================
# 谷物：穗与粒
# ======================================================================

def ear_paddy(img, pal, seed):
    """稻穗：主秆扬起来之后整条穗子下垂，两侧交错挂着带芒的谷粒。"""
    main, dark, light, accent = pal
    # 主秆
    _stalk(img, 3.2, 14.6, 7.6, 4.8, 0.30, 0.22, LEAF_GREEN, seed, levels=3)
    # 穗轴：从秆顶向下垂
    spine = []
    for i in range(13):
        t = i / 12.0
        spine.append((7.6 + 6.2 * t, 4.8 + 3.2 * (t ** 1.7)))
    for i, (sx, sy) in enumerate(spine):
        side = 1 if i % 2 == 0 else -1
        gx = sx + side * 0.72
        gy = sy + 0.34 + side * 0.24
        TI._draw_bean(img, gx, gy, 1.04, 0.54, side * 34.0, pal,
                      seed + i * 9, hilum=0.0, shade=1.0)
        gx2 = sx - side * 0.58
        TI._draw_bean(img, gx2, gy + 0.30, 0.94, 0.48, -side * 30.0, pal,
                      seed + i * 9 + 3, hilum=0.0, shade=0.96)
        # 芒：每粒谷子上两根短芒
        for lean in (-0.60, 0.40):
            for d in range(4):
                TI.px(img, (gx + lean * d * 0.44) * TI.U,
                      (gy - 0.34 - d * 0.56) * TI.U, accent, 200)
    # 穗轴本身
    for (sx, sy) in spine:
        TI.paint(img, TI.oval_pts(sx, sy, 0.22, 0.22), TI._shade(accent, -0.25))


def ear_foxtail(img, pal, seed):
    """谷穗（粟）：立着的毛刷状穗子，密密麻麻的细芒。"""
    main, dark, light, accent = pal
    _stalk(img, 8.0, 14.6, 8.0, 5.6, 0.32, 0.24, LEAF_GREEN, seed, levels=3)
    rnd = _rng(seed, 11)
    # 穗身：一根胖乎乎的毛刷（上尖下宽）
    for i in range(110):
        t = rnd.random() ** 0.75
        gy = 2.0 + t * 4.4
        gx = 8.0 + rnd.uniform(-1.0, 1.0) * (0.45 + t * 1.55)
        TI._draw_bean(img, gx, gy, 0.58, 0.38, rnd.uniform(-70, 70), pal,
                      seed + i, hilum=0.0)
    # 芒
    for i in range(46):
        t = rnd.random()
        gy = 2.2 + t * 4.6
        gx = 8.0 + rnd.uniform(-1.0, 1.0) * (0.55 + t * 1.65)
        ang = rnd.uniform(-1.1, 1.1)
        for d in range(4):
            TI.px(img, (gx + math.sin(ang) * d * 0.52) * TI.U,
                  (gy - d * 0.66) * TI.U, accent, 190)
    # 顶部收尖
    TI.paint(img, TI.poly_pts([(7.2, 2.4), (8.8, 2.4), (8.0, 0.7)]), light)


def ear_sorghum(img, pal, seed):
    """高粱穗：密实的竖向椭圆穗，暗红褐色，顶端几根长芒。"""
    main, dark, light, accent = pal
    _stalk(img, 8.0, 14.8, 8.0, 6.4, 0.36, 0.28, LEAF_GREEN, seed, levels=3)
    rnd = _rng(seed, 5)
    for i in range(150):
        a = rnd.uniform(0.0, math.tau)
        d = rnd.random() ** 0.45
        gx = 8.0 + math.cos(a) * d * 2.45
        gy = 4.4 + math.sin(a) * d * 3.0 - d * 0.9
        TI._draw_bean(img, gx, gy, 0.54, 0.46, rnd.uniform(-60, 60), pal,
                      seed + i, hilum=0.0)
    for i in range(9):
        a = -1.1 + i * 0.28
        for d in range(5):
            TI.px(img, (8.0 + math.sin(a) * d * 0.44) * TI.U,
                  (1.8 + d * 0.52) * TI.U, accent, 170)


def _grain_heap(specs, count, r):
    def painter(img, pal, seed):
        _beans(img, pal, 8.0, 8.6, r, specs, count, seed)
    return painter


grain_rice = _grain_heap([(0.96, 0.44, 0.0, 0.10), (0.88, 0.42, 0.0, 0.14)], 32, 4.5)
grain_glutinous = _grain_heap([(0.72, 0.62, 0.0, 0.12)], 26, 4.4)
grain_millet = _grain_heap([(0.52, 0.44, 0.0, 0.06)], 42, 4.3)


def crop_corn(img, pal, seed):
    """玉米棒：金黄玉米粒 + 外剥的绿色苞叶 + 顶上的玉米须。"""
    main, dark, light, accent = pal
    # 苞叶（左右各一片）
    _leaf(img, 6.6, 12.4, 3.4, 3.6, 1.7, LEAF_GREEN, seed + 3, curve=0.9)
    _leaf(img, 9.4, 12.4, 12.6, 3.6, 1.7, LEAF_GREEN, seed + 7, curve=-0.9)
    _leaf(img, 8.0, 13.2, 6.0, 9.0, 1.2, LEAF_GREEN, seed + 11, curve=0.6)

    def path(t):
        return (8.0 + 0.5 * math.sin(t * 2.6), 3.4 + t * 8.6)

    def half(t):
        return 1.55 * (math.sin(math.pi * (0.14 + 0.86 * t)) ** 0.42)

    def extra(t, s, x, y, v):
        row = (y // max(2, int(TI.U * 0.9)))
        col = int((s + 1.0) * 3.2)
        if (row + col) % 2:
            v -= 0.16
        if row % 2 == 0:
            v += 0.05
        return v

    shade = _tube_shade(pal, seed, levels=4, bias=0.60, spread=0.42, extra=extra)
    _body(img, path, half, shade, seed, samples=48)
    # 玉米须
    rnd = _rng(seed, 21)
    for i in range(7):
        a = -1.0 + i * 0.34
        for d in range(4):
            TI.px(img, (8.0 + math.sin(a) * d * 0.34) * TI.U,
                  (2.8 - d * 0.55) * TI.U, TI._shade(accent, 0.10), 200)


def crop_sesame(img, pal, seed):
    """芝麻：一堆极小、扁平的白 / 黑籽。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img, x, y, 0.42, 0.28, ang, pal, seed=int(rnd.random() * 1e6),
                      hilum=0.0, shade=1.05)
    _heap(img, 8.0, 8.8, 4.4, 46, one, seed)


def crop_lotus_seed(img, pal, seed):
    """莲子：大颗椭圆，带明显的种脐与一层浅色外壳。"""
    _beans(img, pal, 8.0, 8.6, 4.3,
           [(1.45, 1.05, 0.0, 0.46), (1.30, 0.98, 0.0, 0.44)], 7, seed)


def bean_pea(img, pal, seed):
    """豌豆：圆鼓鼓的青豆，白色种脐很明显。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img, x, y, 1.86, 1.78, ang, pal, seed=int(rnd.random() * 1e6),
                      hilum=0.40)
    _heap(img, 8.0, 9.0, 3.5, 6, one, seed, salt=9)


def bean_peanut(img, pal, seed):
    """花生：带壳的葫芦形，壳上有网格纹。"""
    for i, (cx, cy, ang) in enumerate(((6.2, 7.0, -18.0), (10.0, 8.8, 16.0),
                                       (7.4, 11.4, -8.0))):
        _body(img,
              lambda t, cx=cx, cy=cy, ang=ang: (
                  cx + math.cos(math.radians(ang)) * (t - 0.5) * 4.6
                  - math.sin(math.radians(ang)) * 0.0,
                  cy + math.sin(math.radians(ang)) * (t - 0.5) * 4.6),
              lambda t: 1.30 * (0.55 + 0.45 * abs(math.sin(t * math.pi * 2.0))),
              _tube_shade(pal, seed + i, levels=4, bias=0.60, spread=0.60,
                          extra=lambda t, s, x, y, v: v + (0.16 if (int(t * 9) + int((s + 1) * 3)) % 2 else -0.14)),
              seed + i, samples=40)


# ======================================================================
# 工具：一束叶 / 一束茎（叶菜类共用）
# ======================================================================

def _bundle(img, pal, seed, blades, root=None, root_pal=None):
    """按 blades 里给出的叶片依次画出来。"""
    if root is not None:
        _stalk(img, root[0], root[1], root[2], root[3], root[4], root[5],
               root_pal or LEAF_GREEN, seed + 61, levels=3)
    for i, spec in enumerate(blades):
        _leaf(img, spec[0], spec[1], spec[2], spec[3], spec[4], pal,
              seed + i * 23, curve=spec[5] if len(spec) > 5 else 0.0,
              levels=3, bias=spec[6] if len(spec) > 6 else 0.60)


# ======================================================================
# 蔬菜
# ======================================================================

def veg_napa(img, pal, seed):
    """白菜：紧实的叶球，外叶包住浅色菜心，底部一段白色菜帮。"""
    main, dark, light, accent = pal
    # 菜帮
    _stalk(img, 8.0, 14.8, 8.0, 11.0, 3.0, 2.6, PALE_FLESH, seed, levels=3)
    # 外层叶（左右外翻）
    _leaf(img, 5.0, 13.8, 2.4, 4.6, 2.1, pal, seed + 5, curve=1.5)
    _leaf(img, 11.0, 13.8, 13.6, 4.6, 2.1, pal, seed + 9, curve=-1.5)
    _leaf(img, 6.4, 13.4, 4.6, 3.4, 1.7, pal, seed + 13, curve=0.9)
    _leaf(img, 9.6, 13.4, 11.4, 3.4, 1.7, pal, seed + 17, curve=-0.9)
    # 菜心（更浅、更靠中间）
    _leaf(img, 8.0, 13.2, 7.4, 3.0, 2.2, pal, seed + 21, curve=0.25, bias=0.78)
    _leaf(img, 8.0, 13.2, 8.8, 3.2, 2.0, pal, seed + 25, curve=-0.25, bias=0.74)


def veg_bokchoy(img, pal, seed):
    """小白菜：长白柄 + 柄顶一小把亮绿叶子，整体像“小汤匙”。"""
    main, dark, light, accent = pal
    for i, (x0, x1, top, lean) in enumerate(((5.0, 4.2, 5.4, -1.4),
                                             (7.0, 6.8, 4.4, -0.6),
                                             (9.0, 9.2, 4.4, 0.6),
                                             (11.0, 11.8, 5.4, 1.4))):
        # 长长的白柄
        _stalk(img, x0, 13.8, x1, top + 1.6, 0.62, 0.50, PALE_FLESH,
               seed + i * 7, ribs=1)
        # 柄顶的绿叶（向外翻）
        _leaf(img, x1, top + 1.8, x1 + lean * 2.4, top - 1.4, 1.35, pal,
              seed + i * 7 + 3, curve=lean * 0.6)
    # 根部
    _stalk(img, 8.0, 14.8, 8.0, 13.6, 1.1, 1.3, PALE_FLESH, seed + 41, levels=3)


def veg_spinach(img, pal, seed):
    """菠菜：一大把深绿的尖叶摊成扇形，根部一小截暗红。"""
    _bundle(img, pal, seed, [
        (7.8, 12.8, 2.4, 5.6, 1.95, 1.5),
        (8.2, 12.8, 13.6, 5.6, 1.95, -1.5),
        (7.9, 12.8, 4.4, 2.8, 1.75, 0.8),
        (8.1, 12.8, 11.6, 2.8, 1.75, -0.8),
        (8.0, 12.6, 6.6, 1.2, 1.50, 0.35),
        (8.0, 12.6, 9.4, 1.2, 1.50, -0.35),
    ], root=(8.0, 14.8, 8.0, 12.2, 1.05, 1.35),
        root_pal=((150, 68, 56), (108, 42, 34), (186, 100, 84), (84, 30, 24)))


def veg_cilantro(img, pal, seed):
    """香菜：羽状裂叶 —— 一根细梗上挂几片锯齿状的小叶。"""
    main, dark, light, accent = pal
    _stalk(img, 8.0, 14.6, 8.0, 5.0, 0.36, 0.24, LEAF_GREEN, seed, levels=3)
    rnd = _rng(seed, 31)
    for i in range(5):
        t = i / 4.0
        basey = 5.0 + t * 5.2
        for side in (-1, 1):
            bx = 8.0 + side * 0.25
            lx = bx + side * (2.5 - t * 0.6)
            ly = basey - 1.2 - rnd.uniform(0.0, 0.8)
            _leaf(img, bx, basey, lx, ly, 1.0, pal, seed + i * 7 + (0 if side < 0 else 3),
                  midrib=False, levels=3, bias=0.66)
    # 顶上一小簇
    _leaf(img, 8.0, 4.6, 7.0, 2.6, 0.9, pal, seed + 41, midrib=False, bias=0.70)
    _leaf(img, 8.0, 4.6, 9.0, 2.6, 0.9, pal, seed + 43, midrib=False, bias=0.70)


def veg_celery(img, pal, seed):
    """芹菜：几根带纵槽的浅绿扁柄，顶端挂着小叶。"""
    for i, (x0, x1, lean) in enumerate(((5.6, 4.6, -0.5), (7.4, 7.2, -0.1),
                                        (9.2, 9.6, 0.2), (10.8, 11.5, 0.6))):
        top = 4.2 + abs(lean) * 1.4
        _stalk(img, x0, 14.4, x1, top, 0.78, 0.62, pal, seed + i * 11, ribs=2)
        _leaf(img, x1, top + 0.2, x1 + lean * 3.0, top - 2.4, 1.1, pal,
              seed + i * 11 + 5, midrib=False, levels=3, bias=0.68)


def veg_chive(img, pal, seed):
    """韭菜：长长的一束细扁叶，根部只有很窄的一截白。"""
    _bundle(img, pal, seed, [
        (4.2, 13.4, 1.6, 2.0, 0.52, 0.7),
        (5.6, 13.6, 4.0, 1.2, 0.56, 0.35),
        (7.2, 13.6, 6.4, 0.6, 0.58, 0.2),
        (8.8, 13.6, 9.6, 0.6, 0.58, -0.2),
        (10.4, 13.6, 12.0, 1.2, 0.56, -0.35),
        (11.8, 13.4, 14.4, 2.0, 0.52, -0.7),
    ], root=(8.0, 14.8, 8.0, 13.6, 1.9, 2.1), root_pal=PALE_FLESH)


def veg_scallion(img, pal, seed):
    """葱：白葱头 + 三根带尖的绿管。"""
    _stalk(img, 8.0, 14.6, 8.0, 10.4, 2.2, 1.8, PALE_FLESH, seed, levels=3)
    for i, (top, lean) in enumerate(((1.4, -1.1), (0.8, 0.0), (1.8, 1.2))):
        x0 = 6.4 + i * 1.6
        _stalk(img, x0, 11.0, x0 + lean * 2.2, top, 0.66, 0.34, LEAF_GREEN,
               seed + i * 17, ribs=1)
    # 葱头的横纹
    for k in range(3):
        y = (11.4 + k * 1.1) * TI.U
        for x in range(int(6.0 * TI.U), int(10.0 * TI.U)):
            if TI._noise(x, int(y), seed) < 0.35:
                TI.px(img, x, y, TI._shade(PALE_FLESH[1], -0.10), 255)


def veg_garlic_sprout(img, pal, seed):
    """蒜苗：宽而扁的叶（比韭菜宽一倍），根上连着一瓣蒜。"""
    _bundle(img, pal, seed, [
        (5.4, 12.8, 2.8, 3.0, 1.25, 0.7),
        (7.0, 13.0, 5.6, 2.0, 1.32, 0.35),
        (8.8, 13.0, 10.2, 2.0, 1.32, -0.35),
        (10.6, 12.8, 13.2, 3.0, 1.25, -0.7),
    ], root=None)
    # 根部连着的一瓣蒜
    _body(img, lambda t: (8.0, 12.4 + t * 2.2),
          lambda t: 1.55 * (math.sin(math.pi * (0.12 + 0.86 * t)) ** 0.26),
          _tube_shade(PALE_FLESH, seed + 31, levels=3, bias=0.68, spread=0.44),
          seed + 31, samples=24)


def veg_eggplant(img, pal, seed):
    """茄子：紫色长茄，带绿萼，表皮有一条明显的高光。"""
    def path(t):
        return (6.6 + 3.6 * t + 0.5 * math.sin(t * 3.0), 5.4 + 8.2 * t)

    def half(t):
        return 2.05 * (math.sin(math.pi * (0.16 + 0.84 * t)) ** 0.40)

    def extra(t, s, x, y, v):
        if abs(s - 0.42) < 0.16:          # 高光带
            v += 0.30
        if abs(s + 0.72) < 0.14:          # 背光处再压一档
            v -= 0.12
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.52,
                                       spread=0.50, extra=extra), seed, samples=52)
    _calyx(img, 6.6, 5.2, 1.55, CALYX_GREEN, seed + 3, points=5)


def veg_cucumber(img, pal, seed):
    """黄瓜：深绿的带瘤小刺瓜，略弯，表面有浅色纵纹。"""
    def path(t):
        return (5.2 + 5.6 * t + 0.9 * math.sin(t * 2.2), 4.0 + 9.6 * t)

    def half(t):
        return 1.42 * (math.sin(math.pi * (0.12 + 0.86 * t)) ** 0.34)

    def extra(t, s, x, y, v):
        if abs(abs(s) - 0.55) < 0.10 or abs(s) < 0.07:
            v += 0.22                        # 纵向浅色条纹
        cell = (int(t * 15.0), int((s + 1.0) * 4.5))
        if TI._noise(cell[0], cell[1], seed) > 0.76:
            v += 0.34                        # 刺瘤
        elif TI._noise(cell[1], cell[0], seed + 5) > 0.80:
            v -= 0.26
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.52,
                                       spread=0.55, extra=extra), seed, samples=54)
    _stalk(img, 4.6, 3.6, 3.9, 1.9, 0.34, 0.24, LEAF_DEEP, seed + 9, levels=3)


def veg_wintermelon(img, pal, seed):
    """冬瓜：胖乎乎的深青皮大瓜，表面一层白霜。"""
    def path(t):
        return (8.0 + 0.6 * math.sin(t * 3.1), 5.4 + 9.0 * t)

    def half(t):
        return 3.75 * (math.sin(math.pi * (0.16 + 0.84 * t)) ** 0.32)

    def extra(t, s, x, y, v):
        n = TI._noise(x // 3, y // 3, seed)
        if n > 0.62:
            v += 0.34                        # 白霜
        elif n < 0.22:
            v -= 0.18
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.56,
                                       spread=0.46, extra=extra), seed, samples=52)
    _stalk(img, 7.6, 5.2, 6.4, 2.6, 0.50, 0.32, LEAF_DEEP, seed + 4, levels=3)


def veg_luffa(img, pal, seed):
    """丝瓜：细长的浅绿瓜，三条明显的纵棱，一端留着干花。"""
    def path(t):
        return (5.4 + 5.4 * t + 1.5 * math.sin(t * 1.9), 3.4 + 10.4 * t)

    def half(t):
        return 1.18 * (math.sin(math.pi * (0.10 + 0.88 * t)) ** 0.30)

    def extra(t, s, x, y, v):
        for ridge in (-0.85, 0.0, 0.85):
            if abs(s - ridge) < 0.07:
                v += 0.30
            elif abs(s - ridge) < 0.17:
                v -= 0.14
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.56,
                                       spread=0.44, extra=extra), seed, samples=56)
    # 干花
    TI.paint(img, TI.poly_pts([(4.8, 3.2), (6.0, 3.2), (5.4, 1.4)]),
             TI._shade(pal[3], 0.10))


def veg_bitter(img, pal, seed):
    """苦瓜：青黄绿、短胖、满身瘤皱的瓜。"""
    def path(t):
        return (5.4 + 5.4 * t + 1.1 * math.sin(t * 2.4), 3.4 + 9.4 * t)

    def half(t):
        return 1.92 * (math.sin(math.pi * (0.13 + 0.85 * t)) ** 0.30)

    def extra(t, s, x, y, v):
        cell = (int(t * 13.0), int((s + 1.0) * 4.0))
        h = TI._noise(cell[0], cell[1], seed)
        if h > 0.56:
            v += 0.46                        # 瘤子受光面
        elif h < 0.32:
            v -= 0.30                        # 瘤子之间的沟
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.58,
                                       spread=0.40, extra=extra), seed, samples=58)
    _stalk(img, 5.0, 3.2, 4.2, 1.6, 0.32, 0.22, LEAF_DEEP, seed + 6, levels=3)


def veg_greenbean(img, pal, seed):
    """豆角：细长豆荚，能看出里面一颗颗豆粒的鼓包，一端带梗。"""
    def path(t):
        return (3.8 + 9.4 * t, 11.8 - math.sin(t * math.pi) * 4.6)

    def half(t):
        return 1.06 * (math.sin(math.pi * (0.09 + 0.90 * t)) ** 0.26)

    def extra(t, s, x, y, v):
        # 豆粒的鼓包：沿轴周期性地隆起
        bump = math.sin(t * math.pi * 9.0)
        v += 0.20 * bump
        if abs(s) < 0.16:
            v += 0.10
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.60,
                                       spread=0.38, extra=extra), seed, samples=64)
    # 梗
    _stalk(img, 3.9, 11.9, 2.6, 13.2, 0.24, 0.18, LEAF_DEEP, seed + 2, levels=3)


def veg_tomato(img, pal, seed):
    """西红柿：圆球 + 绿萼 + 高光。"""
    TI.sphere(img, 8.0, 9.2, 4.5, pal, seed, squash=0.92, light=(-0.55, -0.60))
    _calyx(img, 8.0, 5.0, 1.35, CALYX_GREEN, seed + 3, points=6)


def veg_chili(img, pal, seed):
    """辣椒：细长的尖椒，微微弯，深红发亮，带绿蒂。"""
    def path(t):
        return (4.8 + 7.0 * t, 5.2 + 7.6 * t + 1.3 * math.sin(t * 2.6))

    def half(t):
        return 1.10 * (math.sin(math.pi * (0.10 + 0.90 * t)) ** 0.45) * (1.0 - 0.18 * t)

    def extra(t, s, x, y, v):
        if abs(s - 0.40) < 0.20:
            v += 0.28
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.54,
                                       spread=0.46, extra=extra), seed, samples=50)
    _calyx(img, 4.8, 5.2, 1.10, CALYX_GREEN, seed + 5, points=5, tilt=0.6)


def veg_radish(img, pal, seed):
    """萝卜：白色的长圆锥，头顶一丛绿缨。"""
    def path(t):
        return (8.0 + 0.4 * math.sin(t * 3.3), 5.8 + 8.4 * t)

    def half(t):
        return 2.05 * (1.0 - 0.80 * (t ** 0.85))

    _body(img, path, half, _tube_shade(pal, seed, levels=3, bias=0.66,
                                       spread=0.44), seed, samples=48)
    _bundle(img, LEAF_GREEN, seed + 17, [
        (7.8, 5.8, 5.4, 1.4, 0.85, -0.7),
        (8.0, 5.8, 8.0, 1.0, 0.95, 0.0),
        (8.2, 5.8, 10.6, 1.4, 0.85, 0.7),
    ])
    # 根须
    for i in range(3):
        TI.px(img, (8.0 + i - 1) * TI.U, (14.2 + i * 0.4) * TI.U, pal[3], 200)


def veg_sweetpotato(img, pal, seed):
    """红薯：纺锤形块根，表面几道横纹，一端带小芽。"""
    def path(t):
        return (4.4 + 7.4 * t + 0.5 * math.sin(t * 2.5), 9.0 + 1.1 * math.sin(t * 3.0))

    def half(t):
        return 2.25 * (math.sin(math.pi * (0.12 + 0.86 * t)) ** 0.34)

    def extra(t, s, x, y, v):
        if int(x / (TI.U * 1.6) + t * 4) % 3 == 0:
            v -= 0.14
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.58,
                                       spread=0.50, extra=extra), seed, samples=48)
    _leaf(img, 4.4, 8.8, 2.6, 6.2, 0.7, LEAF_GREEN, seed + 7, midrib=False, bias=0.70)


def veg_yam(img, pal, seed):
    """山药：细长的直棒，表皮有细长的须根痕。"""
    def path(t):
        return (5.0 + 2.0 * t, 2.4 + 11.6 * t)

    def half(t):
        return 1.32 * (math.sin(math.pi * (0.10 + 0.88 * t)) ** 0.30)

    def extra(t, s, x, y, v):
        if TI._noise(x, y // 2, seed) > 0.72:
            v -= 0.20
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.60,
                                       spread=0.50, extra=extra), seed, samples=56)


def veg_taro(img, pal, seed):
    """芋头：圆中带扁的块茎，顶上一个褐色的芽眼。"""
    TI.sphere(img, 8.0, 9.4, 4.2, pal, seed, squash=0.86, light=(-0.55, -0.58))
    # 芽眼
    TI.paint(img, TI.oval_pts(8.0, 5.4, 0.85, 0.55), TI._shade(pal[1], -0.20))
    for i in range(3):
        TI.px(img, (7.6 + i * 0.4) * TI.U, (4.6 - i * 0.2) * TI.U, pal[3], 220)
    # 侧面的须根痕
    for i in range(4):
        TI.px(img, (5.2 + i * 1.4) * TI.U, (12.6 + (i % 2) * 0.5) * TI.U, pal[1], 170)


def veg_ginger(img, pal, seed):
    """姜：几节连在一起的块状根茎，节上有芽。"""
    main, dark, light, accent = pal
    lumps = (((6.0, 9.8), 2.5, -0.3), ((10.4, 7.6), 2.1, 0.4), ((9.2, 11.8), 1.8, 0.1))
    for i, ((cx, cy), r, ang) in enumerate(lumps):
        _body(img,
              lambda t, cx=cx, cy=cy, r=r, ang=ang: (
                  cx + math.cos(ang) * (t - 0.5) * r * 2.0,
                  cy + math.sin(ang) * (t - 0.5) * r * 2.0),
              lambda t, r=r: r * (math.sin(math.pi * (0.16 + 0.84 * t)) ** 0.34),
              _tube_shade(pal, seed + i * 9, levels=3, bias=0.62, spread=0.52,
                          extra=lambda t, s, x, y, v: v + (0.16 if TI._noise(x // 2, y // 2, seed + i * 3) > 0.58 else -0.10)),
              seed + i * 9, samples=36)
    for i in range(3):
        TI.paint(img, TI.oval_pts(5.2 + i * 1.1, 7.6 + i * 0.5, 0.26, 0.22), accent)


def veg_garlic(img, pal, seed):
    """蒜：一整头蒜，瓣缝清楚，顶部收成纸状的尖。"""
    main, dark, light, accent = pal

    def path(t):
        return (8.0, 6.4 + t * 7.6)

    def half(t):
        return 3.35 * (math.sin(math.pi * (0.14 + 0.86 * t)) ** 0.30)

    def extra(t, s, x, y, v):
        # 瓣缝：纵向的几道凹线
        for k in (-0.62, -0.21, 0.21, 0.62):
            if abs(s - k) < 0.06:
                v -= 0.34
        return v

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.66,
                                       spread=0.42, extra=extra), seed, samples=48)
    # 顶部纸尖
    TI.paint(img, TI.poly_pts([(6.2, 6.6), (9.8, 6.6), (8.9, 3.0), (8.0, 2.2), (7.1, 3.0)]),
             TI._shade(accent, -0.06))
    _stalk(img, 8.0, 3.4, 8.0, 1.8, 0.30, 0.20, PALE_FLESH, seed + 3, levels=3)


def veg_woodear(img, pal, seed):
    """木耳：卷曲的耳片，边缘薄而亮。"""
    main, dark, light, accent = pal
    rnd = _rng(seed, 8)
    for i, (cx, cy, rx, ry, rot) in enumerate(((6.0, 9.6, 3.0, 2.2, -0.45),
                                               (10.2, 7.4, 2.5, 1.9, 0.35),
                                               (9.0, 11.8, 2.2, 1.7, -0.15))):
        pts = []
        for (x, y) in TI.oval_pts(cx, cy, rx, ry):
            dx, dy = x + 0.5 - cx * TI.U, y + 0.5 - cy * TI.U
            ca, sa = math.cos(rot), math.sin(rot)
            u, v = dx * ca - dy * sa, dx * sa + dy * ca
            wob = 1.0 + 0.22 * math.sin(math.atan2(v, u) * 5.0)
            if u * u / ((rx * TI.U) ** 2) * wob + v * v / ((ry * TI.U) ** 2) <= 1.0:
                pts.append((x, y))
        for (x, y) in pts:
            v = 0.42 + 0.55 * TI._noise(x // 2, y // 2, seed + i * 7)
            TI.px(img, x, y, (dark, main, light, accent)[TI._quantize(v, 3, x, y)], 255)
        TI.outline(img, pts, accent)
        for (x, y) in pts:
            if TI._noise(x, y, seed + i) > 0.72:
                TI.px(img, x, y, light, 190)


def veg_shoot(img, pal, seed):
    """鲜笋：层叠的笋壳，顶上收成尖。"""
    main, dark, light, accent = pal
    layers = ((2.4, 6.2, 5.6, 4.0), (3.4, 9.4, 10.2, 3.8), (4.0, 13.0, 9.2, 3.0))
    for i, (x0, y0, x1, y1) in enumerate(layers):
        pts = TI.poly_pts([(x0, y1), (x1, y1), (x1 - 0.7, y0), (x0 + 0.7, y0)])
        for (x, y) in pts:
            v = 0.50 + 0.50 * TI._noise(x // 2, y // 2, seed + i * 5) \
                + (0.14 if x < 8 * TI.U else -0.10)
            TI.px(img, x, y, _pick(pal, v, 3), 255)
        TI.outline(img, pts, accent)
        # 壳缘的亮线
        for x in range(int((x0 + 0.6) * TI.U), int((x1 - 0.6) * TI.U)):
            TI.px(img, x, y1 * TI.U - 1, TI._shade(light, 0.10), 200)
    TI.paint(img, TI.poly_pts([(6.4, 4.2), (9.6, 4.2), (8.0, 1.4)]), light)


def veg_shoot_dried(img, pal, seed):
    """笋干：压扁晒干的笋条，颜色偏褐、有皱。"""
    main, dark, light, accent = pal
    for i, (cx, cy, ang, w, ln) in enumerate(((6.4, 8.2, -0.35, 0.95, 6.2),
                                              (9.6, 7.4, 0.30, 0.85, 5.6),
                                              (8.0, 11.6, -0.10, 0.90, 5.0))):
        _body(img,
              lambda t, cx=cx, cy=cy, ang=ang, ln=ln: (
                  cx + math.cos(ang) * (t - 0.5) * ln,
                  cy + math.sin(ang) * (t - 0.5) * ln),
              lambda t, w=w: w * (math.sin(math.pi * (0.10 + 0.88 * t)) ** 0.30),
              _tube_shade(pal, seed + i * 11, levels=3, bias=0.60, spread=0.46,
                          extra=lambda t, s, x, y, v: v - (0.18 if TI._noise(x, y // 2, seed + i) > 0.60 else 0.0)),
              seed + i * 11, samples=36)


def veg_pickle(img, pal, seed):
    """腌菜：一口小坛，坛口露出压着的菜叶。"""
    main, dark, light, accent = pal
    clay = ((170, 108, 76), (124, 74, 50), (200, 142, 108), (98, 56, 38))

    def path(t):
        return (8.0, 6.0 + t * 8.0)

    def half(t):
        return 3.5 * (math.sin(math.pi * (0.16 + 0.84 * t)) ** 0.30) * (0.86 + 0.20 * t)

    _body(img, path, half, _tube_shade(clay, seed, levels=4, bias=0.62, spread=0.50),
          seed, samples=44)
    # 坛口
    TI.paint(img, TI.oval_pts(8.0, 6.4, 3.0, 0.85), TI._shade(clay[0], 0.12))
    # 露出的菜
    _leaf(img, 7.4, 6.2, 5.0, 3.0, 1.0, pal, seed + 5, midrib=False, bias=0.70)
    _leaf(img, 8.6, 6.2, 11.0, 3.0, 1.0, pal, seed + 9, midrib=False, bias=0.70)
    _leaf(img, 8.0, 6.0, 8.0, 2.6, 1.1, pal, seed + 13, midrib=False, bias=0.74)


def veg_bean_sprout(img, pal, seed):
    """豆芽：细白的茎 + 顶上一对嫩叶 + 一小截豆瓣。"""
    main, dark, light, accent = pal
    rnd = _rng(seed, 4)
    for i, (cx, tall) in enumerate(((6.0, 8.6), (8.0, 10.8), (10.0, 7.8))):
        _stalk(img, cx, 14.2, cx + rnd.uniform(-0.4, 0.4), tall, 0.44, 0.34,
               PALE_FLESH, seed + i * 9, levels=3)
        _leaf(img, cx, tall, cx - 1.3, tall - 1.4, 0.80, pal, seed + i * 5,
              midrib=False, bias=0.70)
        _leaf(img, cx, tall, cx + 1.3, tall - 1.4, 0.80, pal, seed + i * 5 + 2,
              midrib=False, bias=0.66)


# ======================================================================
# 种子
# ======================================================================

def seed_paddy(img, pal, seed):
    """稻种：带壳的稻粒，细长略尖。"""
    _beans(img, pal, 8.0, 8.8, 4.4,
           [(0.90, 0.42, 0.16, 0.0), (0.82, 0.40, 0.14, 0.0)], 26, seed)


def seed_millet(img, pal, seed):
    """谷种：极小的一堆金黄小粒。"""
    _beans(img, pal, 8.0, 8.8, 4.3, [(0.48, 0.40, 0.0, 0.0)], 40, seed)


def seed_sorghum(img, pal, seed):
    """高粱种：比谷粒大一点、暗红的圆粒。"""
    _beans(img, pal, 8.0, 8.8, 4.4, [(0.62, 0.52, 0.0, 0.20)], 24, seed)


def seed_corn(img, pal, seed):
    """玉米种：金黄扁楔形的玉米粒。"""
    def one(x, y, ang, i, rnd):
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for (u, v) in ((0.0, -0.62), (0.46, -0.20), (0.34, 0.46),
                       (-0.34, 0.46), (-0.46, -0.20)):
            pts.append((x + u * ca - v * sa, y + u * sa + v * ca))
        pxs = TI.poly_pts(pts)
        for (px_, py_) in pxs:
            dx = (px_ + 0.5 - x * TI.U) / TI.U
            dy = (py_ + 0.5 - y * TI.U) / TI.U
            v = 0.62 - 0.30 * (dx + dy) + (TI._noise(px_, py_, seed) - 0.5) * 0.18
            TI.px(img, px_, py_, (pal[1], pal[0], pal[2], pal[3])[
                TI._quantize(v, 4, px_, py_)], 255)
        TI.outline(img, pxs, pal[1] if len(pal) > 1 else pal[0])
    _heap(img, 8.0, 8.8, 4.2, 16, one, seed)


def seed_peanut(img, pal, seed):
    """花生种：带红衣的花生米。"""
    _beans(img, pal, 8.0, 8.8, 4.3,
           [(1.30, 0.92, 0.0, 0.0), (1.16, 0.86, 0.0, 0.0)], 9, seed)


def seed_sesame(img, pal, seed):
    """芝麻种：极小、扁平的籽。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img, x, y, 0.38, 0.24, ang, pal, seed=int(rnd.random() * 1e6),
                      hilum=0.0, shade=1.05)
    _heap(img, 8.0, 8.8, 4.3, 44, one, seed)


def seed_brassica(img, pal, seed):
    """白菜 / 小白菜种：红褐色的圆籽。"""
    _beans(img, pal, 8.0, 8.8, 4.4, [(0.58, 0.54, 0.0, 0.18)], 30, seed)


def seed_radish(img, pal, seed):
    """萝卜种：比白菜籽大一圈、颜色更浅。"""
    _beans(img, pal, 8.0, 8.8, 4.4, [(0.86, 0.76, 0.0, 0.22)], 16, seed)


def seed_capsicum(img, pal, seed):
    """辣椒种：淡黄色的扁圆盘。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img, x, y, 0.92, 0.62, ang, pal, seed=int(rnd.random() * 1e6),
                      hilum=0.0, shade=1.05)
    _heap(img, 8.0, 8.8, 4.3, 12, one, seed)


def seed_cucurbit(img, pal, seed):
    """瓜类种：扁椭圆，边缘一圈略厚。"""
    def one(x, y, ang, i, rnd):
        _body(img,
              lambda t, x=x, y=y, ang=ang: (
                  x + math.cos(math.radians(ang)) * (t - 0.5) * 2.2,
                  y + math.sin(math.radians(ang)) * (t - 0.5) * 2.2),
              lambda t: 0.74 * (math.sin(math.pi * (0.12 + 0.86 * t)) ** 0.28),
              _tube_shade(pal, int(rnd.random() * 1e6), levels=3, bias=0.66,
                          spread=0.40),
              seed, samples=26, outline=True)
    _heap(img, 8.0, 8.8, 4.2, 11, one, seed)


def seed_solanum(img, pal, seed):
    """茄科种（茄子 / 番茄）：淡黄扁圆形。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img, x, y, 0.72, 0.62, ang, pal, seed=int(rnd.random() * 1e6),
                      hilum=0.0, shade=1.00)
    _heap(img, 8.0, 8.8, 4.3, 20, one, seed)


def seed_prickly(img, pal, seed):
    """菠菜种：带小刺的褐色球。"""
    def one(x, y, ang, i, rnd):
        TI.sphere(img, x, y, 0.62, pal, seed=int(rnd.random() * 1e6),
                  light=(-0.5, -0.55))
        for k in range(4):
            a = rnd.uniform(0, math.tau)
            TI.px(img, (x + math.cos(a) * 0.75) * TI.U,
                  (y + math.sin(a) * 0.75) * TI.U, pal[1], 220)
    _heap(img, 8.0, 8.8, 4.3, 14, one, seed)


def seed_umbel(img, pal, seed):
    """芹菜 / 香菜种：细长的小籽。"""
    def one(x, y, ang, i, rnd):
        TI._draw_bean(img, x, y, 0.72, 0.36, ang, pal, seed=int(rnd.random() * 1e6),
                      hilum=0.0, shade=1.05)
    _heap(img, 8.0, 8.8, 4.3, 22, one, seed)


def seed_allium(img, pal, seed):
    """韭菜 / 葱种：黑色、扁平带棱的三角籽。"""
    def one(x, y, ang, i, rnd):
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for (u, v) in ((0.0, -0.70), (0.55, 0.20), (0.0, 0.62), (-0.55, 0.20)):
            pts.append((x + u * ca - v * sa, y + u * sa + v * ca))
        pxs = TI.poly_pts(pts)
        for (px_, py_) in pxs:
            dx = (px_ + 0.5 - x * TI.U) / TI.U
            dy = (py_ + 0.5 - y * TI.U) / TI.U
            v = 0.55 - 0.32 * (dx + dy)
            TI.px(img, px_, py_, (pal[1], pal[0], pal[2], pal[3])[
                TI._quantize(v, 3, px_, py_)], 255)
        TI.outline(img, pxs, pal[3])
    _heap(img, 8.0, 8.8, 4.2, 20, one, seed)


def seed_allium_round(img, pal, seed):
    """葱种：比韭菜籽圆一点、偏褐。"""
    _beans(img, pal, 8.0, 8.8, 4.3, [(0.50, 0.46, 0.0, 0.0)], 34, seed)


def seed_taro(img, pal, seed):
    """芋种：带芽眼的小芋头。"""
    def one(x, y, ang, i, rnd):
        TI.sphere(img, x, y, 1.05, pal, seed=int(rnd.random() * 1e6),
                  squash=0.9, light=(-0.55, -0.58))
        TI.px(img, (x + 0.2) * TI.U, (y - 0.9) * TI.U, pal[3], 230)
    _heap(img, 8.0, 9.0, 3.2, 5, one, seed)


def seed_slip(img, pal, seed):
    """红薯秧：一段带芽的薯块。"""
    def path(t):
        return (6.0 + 4.4 * t, 10.4 - 1.0 * math.sin(t * 3.0))

    def half(t):
        return 1.95 * (math.sin(math.pi * (0.14 + 0.84 * t)) ** 0.34)

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.58, spread=0.50),
          seed, samples=40)
    _leaf(img, 7.0, 9.4, 5.0, 6.2, 0.80, LEAF_GREEN, seed + 7, midrib=False, bias=0.70)
    _leaf(img, 9.0, 9.2, 11.4, 6.0, 0.75, LEAF_GREEN, seed + 11, midrib=False, bias=0.66)


def seed_yam(img, pal, seed):
    """山药嘴子：一小截带芽的山药。"""
    _stalk(img, 7.6, 13.6, 8.4, 5.6, 1.25, 1.05, pal, seed, ribs=1)
    _leaf(img, 8.0, 5.8, 6.4, 3.4, 0.70, LEAF_GREEN, seed + 5, midrib=False, bias=0.70)
    _leaf(img, 8.0, 5.8, 9.6, 3.4, 0.70, LEAF_GREEN, seed + 9, midrib=False, bias=0.66)


def seed_ginger(img, pal, seed):
    """姜种：一块带芽的姜。"""
    main, dark, light, accent = pal
    _body(img,
          lambda t: (6.8 + 2.6 * math.sin(t * 2.2), 7.0 + 6.0 * t),
          lambda t: 2.3 * (math.sin(math.pi * (0.16 + 0.84 * t)) ** 0.34),
          _tube_shade(pal, seed, levels=3, bias=0.62, spread=0.52,
                      extra=lambda t, s, x, y, v: v + (0.16 if TI._noise(x // 2, y // 2, seed) > 0.58 else -0.10)),
          seed, samples=40)
    TI.paint(img, TI.oval_pts(8.2, 3.6, 0.55, 0.42), LEAF_GREEN[0])
    TI.px(img, 8.2 * TI.U, 3.0 * TI.U, LEAF_GREEN[2], 235)


def seed_garlic(img, pal, seed):
    """蒜种：单独一瓣蒜。"""
    main, dark, light, accent = pal

    def path(t):
        return (8.0, 5.4 + t * 7.4)

    def half(t):
        return 2.1 * (math.sin(math.pi * (0.12 + 0.86 * t)) ** 0.28) * (0.82 + 0.22 * t)

    _body(img, path, half, _tube_shade(pal, seed, levels=4, bias=0.66, spread=0.46,
                                       extra=lambda t, s, x, y, v: v - (0.22 if abs(s) < 0.07 else 0.0)),
          seed, samples=44)
    TI.paint(img, TI.poly_pts([(7.2, 5.6), (8.8, 5.6), (8.0, 2.8)]),
             TI._shade(accent, -0.04))


def seed_spawn(img, pal, seed):
    """木耳菌种：一袋木屑菌包，袋口露出白色菌丝。"""
    main, dark, light, accent = pal
    pts = TI.poly_pts([(4.4, 5.2), (11.6, 5.2), (11.0, 14.2), (5.0, 14.2)])
    for (x, y) in pts:
        v = 0.45 + 0.55 * TI._noise(x // 2, y // 2, seed)
        TI.px(img, x, y, (dark, main, light, light)[TI._quantize(v, 3, x, y)], 255)
    # 袋口的褶皱
    for i in range(4):
        xx = 5.0 + i * 1.8
        for (x, y) in TI.poly_pts([(xx, 4.4), (xx + 0.7, 4.4), (xx + 0.3, 6.2)]):
            TI.px(img, x, y, TI._shade(light, 0.18), 235)
    # 菌丝
    for i in range(5):
        xx = 5.6 + i * 1.2
        for (x, y) in TI.poly_pts([(xx, 6.6), (xx + 0.5, 6.6), (xx + 0.2, 9.4)]):
            if TI._noise(x, y, seed + i) > 0.35:
                TI.px(img, x, y, (232, 230, 220), 220)
    TI.outline(img, pts, dark)


# ======================================================================
# 调度表
# ======================================================================

PAINTERS = {
    # --- 谷物 ---
    "ear_paddy": ear_paddy, "ear_foxtail": ear_foxtail, "ear_sorghum": ear_sorghum,
    "grain_rice": grain_rice, "grain_glutinous": grain_glutinous,
    "grain_millet": grain_millet, "crop_corn": crop_corn,
    "crop_sesame": crop_sesame, "crop_lotus_seed": crop_lotus_seed,
    "bean_pea": bean_pea, "bean_peanut": bean_peanut,
    # --- 叶菜 / 茎菜 ---
    "veg_napa": veg_napa, "veg_bokchoy": veg_bokchoy, "veg_spinach": veg_spinach,
    "veg_cilantro": veg_cilantro, "veg_celery": veg_celery, "veg_chive": veg_chive,
    "veg_scallion": veg_scallion, "veg_garlic_sprout": veg_garlic_sprout,
    "veg_bean_sprout": veg_bean_sprout, "veg_pickle": veg_pickle,
    # --- 瓜果 ---
    "veg_eggplant": veg_eggplant, "veg_cucumber": veg_cucumber,
    "veg_wintermelon": veg_wintermelon, "veg_luffa": veg_luffa,
    "veg_bitter": veg_bitter, "veg_greenbean": veg_greenbean,
    "veg_tomato": veg_tomato, "veg_chili": veg_chili,
    # --- 根茎 ---
    "veg_radish": veg_radish, "veg_sweetpotato": veg_sweetpotato,
    "veg_yam": veg_yam, "veg_taro": veg_taro,
    "veg_ginger": veg_ginger, "veg_garlic": veg_garlic,
    # --- 菌 / 笋 ---
    "veg_woodear": veg_woodear, "veg_shoot": veg_shoot,
    "veg_shoot_dried": veg_shoot_dried,
    # --- 种子 ---
    "seed_paddy": seed_paddy, "seed_millet": seed_millet, "seed_sorghum": seed_sorghum,
    "seed_corn": seed_corn, "seed_peanut": seed_peanut, "seed_sesame": seed_sesame,
    "seed_brassica": seed_brassica, "seed_radish": seed_radish,
    "seed_capsicum": seed_capsicum, "seed_cucurbit": seed_cucurbit,
    "seed_solanum": seed_solanum, "seed_prickly": seed_prickly,
    "seed_umbel": seed_umbel, "seed_allium": seed_allium,
    "seed_allium_round": seed_allium_round, "seed_taro": seed_taro,
    "seed_slip": seed_slip, "seed_yam": seed_yam, "seed_ginger": seed_ginger,
    "seed_garlic": seed_garlic, "seed_spawn": seed_spawn,
}

# 这些图标用 64x64 画（其余物品保持原版分辨率）
FINE_KINDS = frozenset(PAINTERS)
