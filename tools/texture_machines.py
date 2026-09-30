# -*- coding: utf-8 -*-
"""机器方块的材质、物品图标，以及两个界面的底图。

    python tools/build_textures.py --only machines

画材质的三条规矩
----------------
1. **只用 2~3 种颜色**：像素画里颜色一多就糊。石、木、铁各给一套 4 档色阶，
   但一张图里最多用 3 档。
2. **图案周期必须整除 16**：砌缝 8、板缝 4、铆钉错缝 8/4。
   这样任意两块相邻的同材质面都能对上，机器拼起来不会有断裂的纹路。
3. **不画逐像素噪点**：噪点既费像素，又会在方块边界处"断掉"。
   改用**结构性花纹**（砌缝、板缝、铆钉、百叶），周期是死的，跨面一定对齐。

关于 UV
-------
模型那边按面的大小自动算 UV（见 `machine_models.py` 的 `box()`），
所以这里只需要保证材质本身是**可平铺**的：任何一块区域看起来都合理。
"""

import math

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


def bind(noise, bayer, quantize, shade):
    global _noise, _bayer, _quantize, _shade
    _noise, _bayer, _quantize, _shade = noise, bayer, quantize, shade


# ======================================================================
# 色阶
# ======================================================================
# 石：偏冷的青灰
STONE = [(96, 98, 100), (118, 120, 122), (140, 142, 144), (162, 164, 166)]
# 木：老榆木，偏黄褐
WOOD = [(104, 68, 36), (132, 90, 50), (158, 112, 66), (184, 138, 88)]
# 铁：偏冷的灰
IRON = [(84, 88, 94), (106, 110, 118), (130, 134, 142), (158, 162, 170)]
# 深铁：机器内腔、炉膛
DARK_IRON = [(40, 42, 46), (56, 58, 62), (74, 76, 82), (96, 98, 104)]
# 磨盘：比砌石深得多的青黑，让"这是磨盘"一眼可辨
MILLSTONE = [(58, 60, 62), (78, 80, 82), (98, 100, 102), (118, 120, 122)]
# 火：炉膛里的火光
FIRE = [(120, 40, 12), (188, 74, 18), (238, 138, 32), (252, 200, 96)]
# 铜：发电机的线圈绕组
COPPER = [(126, 74, 40), (162, 100, 54), (196, 130, 74), (224, 166, 108)]


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


# ======================================================================
# 方块材质
# ======================================================================

def machine_stone():
    """砌石：8×8 一块，缝 1 像素。周期 8，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            lx, ly = x % 8, y % 8
            if lx == 0 or ly == 0:
                c = STONE[0]                 # 砌缝
            elif lx == 1 or ly == 1:
                c = STONE[3]                 # 左上受光的倒角
            elif lx == 7 or ly == 7:
                c = STONE[0]                 # 右下阴影
            else:
                c = STONE[1]
            _px(img, x, y, c)
    return img


def machine_iron():
    """铁：错缝铆接板。周期 8/4，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if y % 8 == 0:
                c = IRON[0]                  # 横向接缝
            elif (x % 8 == 0) and (y % 8 < 5):
                c = IRON[0]                  # 竖向接缝（错缝）
            else:
                c = IRON[1]
            if (x % 8, y % 8) in ((2, 4), (6, 1)):
                c = IRON[3]                  # 铆钉
            _px(img, x, y, c)
    return img


def machine_millstone():
    """磨盘顶面：同心磨纹 + 四道放射槽 + 中央轴孔。

    用一套明显更深的青黑 —— 磨盘是磨粉机的主角，
    颜色和壳体一个调子就完全看不出哪块是磨盘了。
    """
    img = _opaque()
    cx = cy = SIZE / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy) / (SIZE / 2.0)
            if d > 0.97:
                c = IRON[1]                  # 盘边的铁箍
            elif d < 0.16:
                c = DARK_IRON[0]             # 轴孔
            elif d > 0.90:
                c = MILLSTONE[0]
            elif abs(d - 0.60) < 0.07 or abs(d - 0.78) < 0.06:
                c = MILLSTONE[0]             # 同心磨纹
            else:
                c = MILLSTONE[1]
            ang = math.atan2(dy, dx)
            if 0.16 < d < 0.90 and abs(math.sin(ang * 2.0)) < 0.16:
                c = MILLSTONE[0]             # 四道放射槽
            _px(img, x, y, c)
    return img


def machine_grate():
    """炉膛正面：竖向的炉栅 + 里面透出的火光。

    发电机的"正面"，一眼就能看出这台是烧东西的。
    """
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            e = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if e < 2:
                c = IRON[1]                  # 外框
                if e == 0:
                    c = IRON[0]
            else:
                # 炉膛内部：越靠下越亮（火在下面烧）
                lvl = (y - 2) / 11.0
                if lvl < 0.25:
                    c = DARK_IRON[1]
                elif lvl < 0.55:
                    c = FIRE[0]
                elif lvl < 0.85:
                    c = FIRE[1]
                else:
                    c = FIRE[2]
                # 炉栅：每 4 像素一根竖铁条，盖在火上
                if (x % 4) == 0:
                    c = IRON[0]
                elif (x % 4) == 1:
                    c = IRON[1]
            _px(img, x, y, c)
    return img


def machine_vent():
    """百叶散热面：脱壳机 / 磨粉机的"正面"，斜向的散热片。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            e = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if e < 2:
                c = IRON[0] if e == 0 else IRON[2]
            else:
                # 竖向百叶：每 3 像素一片，片上亮下暗
                r = y % 3
                if r == 0:
                    c = DARK_IRON[1]         # 叶间阴影
                elif r == 1:
                    c = IRON[3]              # 叶片受光
                else:
                    c = IRON[1]
            _px(img, x, y, c)
    return img


def machine_coil():
    """绕组面：发电机侧面露出一圈圈铜线圈。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if (y % 4) in (0, 1):
                c = COPPER[1] if (y % 4) == 0 else COPPER[2]
                if (x % 8) in (0, 1):
                    c = COPPER[0]            # 每圈一个小接头
            else:
                c = IRON[1]
                if (y % 4) == 2:
                    c = IRON[0]
            _px(img, x, y, c)
    return img


def machine_hopper():
    """深色铁皮内壁：每 8 像素一道折缝。周期 8，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if x % 8 == 0:
                c = DARK_IRON[0]
            elif x % 8 == 1:
                c = DARK_IRON[2]
            else:
                c = DARK_IRON[1]
            if y % 8 == 7:
                c = DARK_IRON[0]
            _px(img, x, y, c)
    return img


BLOCK_TEXTURES = {
    "machine_stone": machine_stone,
    "machine_iron": machine_iron,
    "machine_millstone": machine_millstone,
    "machine_grate": machine_grate,
    "machine_vent": machine_vent,
    "machine_coil": machine_coil,
    "machine_hopper": machine_hopper,
}


# ======================================================================
# 物品图标
# ======================================================================

def _blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def _rect(img, x0, y0, x1, y1, colour):
    for y in range(int(y0 * U), int(y1 * U)):
        for x in range(int(x0 * U), int(x1 * U)):
            _px(img, x, y, colour)


def _shadow(img, alpha=110, dx=1, dy=2):
    """把图像自身当遮罩往右下投一层阴影 —— 原版物品图标的常规做法。"""
    a = img.getchannel("A")
    sh = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.alpha_composite(sh, (dx, dy))
    out.alpha_composite(img)
    return out


def furnace_generator_item():
    """图标：烧着火的铁炉子，左边三个烟囱。"""
    img = _blank()
    # 机身
    _rect(img, 3.0, 5.0, 14.0, 14.0, STONE[1])
    _rect(img, 3.0, 5.0, 14.0, 6.0, STONE[2])      # 顶面受光
    _rect(img, 3.0, 13.0, 14.0, 14.0, STONE[0])    # 底边
    # 炉膛：中间一块火
    for y in range(int(7.0 * U), int(12.0 * U)):
        for x in range(int(5.0 * U), int(12.0 * U)):
            lvl = (y - 7.0 * U) / (5.0 * U)
            c = FIRE[0] if lvl < 0.35 else (FIRE[1] if lvl < 0.7 else FIRE[2])
            if (x % max(1, int(2 * U))) == 0:
                c = DARK_IRON[0]               # 炉栅
            _px(img, x, y, c)
    # 烟囱
    for i in range(3):
        _rect(img, 4.0 + i * 2.0, 2.0, 5.4 + i * 2.0, 5.0, IRON[1])
        _rect(img, 4.0 + i * 2.0, 2.0, 5.4 + i * 2.0, 2.6, IRON[2])
    # 右侧铜线圈
    _rect(img, 12.0, 7.0, 14.0, 12.0, COPPER[1])
    return _shadow(img)


def electric_mill_item():
    """图标：铁壳磨粉机，顶面是磨盘。"""
    img = _blank()
    _rect(img, 2.0, 4.0, 14.0, 14.0, IRON[1])
    _rect(img, 2.0, 4.0, 14.0, 5.0, IRON[2])
    _rect(img, 2.0, 13.0, 14.0, 14.0, IRON[0])
    # 顶面的磨盘：同心圆
    cx, cy = 8.0, 9.0
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx * U, y + 0.5 - cy * U)
            if d < 4.6 * U:
                if d < 0.9 * U:
                    c = DARK_IRON[0]
                elif abs(d - 2.0 * U) < 0.5 * U or abs(d - 3.4 * U) < 0.4 * U:
                    c = MILLSTONE[0]
                else:
                    c = MILLSTONE[1]
                _px(img, x, y, c)
    # 正面的一排散热片
    for i in range(4):
        _rect(img, 3.5 + i * 2.4, 4.4, 4.6 + i * 2.4, 5.4, IRON[3])
    return _shadow(img)


def electric_sheller_item():
    """图标：铁壳脱壳机，正面是百叶，顶上一个小料斗。"""
    img = _blank()
    _rect(img, 2.0, 5.0, 14.0, 14.0, IRON[1])
    _rect(img, 2.0, 5.0, 14.0, 6.0, IRON[2])
    _rect(img, 2.0, 13.0, 14.0, 14.0, IRON[0])
    # 正面百叶
    for y in range(int(7.0 * U), int(12.6 * U), max(1, int(1.2 * U))):
        _rect(img, 3.4, y / U, 12.6, (y + max(1, int(0.5 * U))) / U, IRON[3])
    # 顶上的料斗
    for i, y in enumerate(range(int(1.4 * U), int(5.2 * U))):
        t = i / max(1.0, 3.8 * U - 1)
        half = (1.2 + 2.6 * t) * U
        for x in range(int(8.0 * U - half), int(8.0 * U + half)):
            _px(img, x, y, DARK_IRON[2] if x % max(1, int(U)) else DARK_IRON[1])
    # 侧面摇柄
    _rect(img, 13.6, 8.0, 15.2, 11.4, COPPER[1])
    return _shadow(img)


# ======================================================================
# 界面底图
# ======================================================================
#
# 画布是 **256×256**（原版惯例），不是 176×166 —— 这不是浪费，而是必须的：
#
#   面板本身只占左上角 176×166；**动态部件的"满帧"必须画在面板之外**
#   （这里放在 x=176 开始的条带里）。
#
# 为什么不放在面板下方：底图是整张 blit 上去的，画在面板里的任何东西
# 一开始就会显示出来 —— 满帧要是画在里面，0% 进度时箭头看起来就是满的。
# 放在面板外侧，它就永远只在需要时被单独裁切贴进来。
#
# 同理，Screen 里 blit 的 textureWidth/Height 必须是 256/256
# （引擎按 u/textureWidth 归一化 UV，传 176 反而会错位）。

GUI_W, GUI_H = 176, 166        # 面板尺寸
TEX_W, TEX_H = 256, 256        # 画布尺寸

# ---- 加工机（电动磨粉机 / 电动脱壳机）----
PROC_INPUT = (56, 35)
PROC_OUTPUT = (116, 35)
ARROW = (79, 34, 24, 17)                    # 面板里的空箭头
ARROW_FULL = (176, 0)                       # 画布上的满箭头

# ---- 熔炉发电机 ----
GEN_FUEL = (80, 35)
FLAME = (81, 54, 14, 14)                    # 面板里的空火苗
FLAME_FULL = (176, 20)                      # 画布上的满火苗

# ---- 共用的竖排电量条 ----
ENERGY = (152, 20, 16, 26)                  # 面板里的空槽
ENERGY_FULL = (176, 40)                     # 画布上的满槽


def _panel(W, H, seed):
    """MC 风格的灰色面板底 + 三像素外框。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    for y in range(H):
        for x in range(W):
            v = 0.9 + 0.1 * _noise(x // 2, y // 2, seed)
            base = (198, 198, 198)
            if x < 3 or y < 3 or x >= W - 3 or y >= H - 3:
                base = (85, 85, 85)          # 外描边
            elif x < 5 or y < 5 or x >= W - 5 or y >= H - 5:
                base = (238, 238, 238)       # 内高光
            px[x, y] = tuple(min(255, int(c * v)) for c in base) + (255,)
    return img


def _canvas():
    return Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))


def _slot(img, box):
    """槽位底：18×18，左上压暗、右下提亮。"""
    sx, sy = box[0] - 1, box[1] - 1
    px = img.load()
    for y in range(sy, sy + 18):
        for x in range(sx, sx + 18):
            px[x, y] = (139, 139, 139, 255)
    for x in range(sx, sx + 18):
        px[x, sy] = (55, 55, 55, 255)
    for y in range(sy, sy + 18):
        px[sx, y] = (55, 55, 55, 255)
    for x in range(sx + 1, sx + 18):
        px[x, sy + 17] = (255, 255, 255, 255)
    for y in range(sy + 1, sy + 18):
        px[sx + 17, y] = (255, 255, 255, 255)


def _player_inventory(img):
    for row in range(3):
        for col in range(9):
            _slot(img, (8 + col * 18, 84 + row * 18))
    for col in range(9):
        _slot(img, (8 + col * 18, 142))


def _arrow_mask(x0, y0, w, h):
    """右向箭头的形状掩码：左边是箭杆，右边是三角箭头。"""
    out = set()
    cy = h / 2.0
    for yy in range(h):
        for xx in range(w):
            t = xx / float(w)
            if t < 0.60:
                half = h * 0.21
            else:
                half = (h * 0.44) * (1.0 - (t - 0.60) / 0.40)
            if abs((yy + 0.5) - cy) <= half:
                out.add((x0 + xx, y0 + yy))
    return out


def _flame_mask(x0, y0, w, h):
    """火苗形状掩码：上尖下宽的水滴。"""
    out = set()
    cx = w / 2.0
    for yy in range(h):
        for xx in range(w):
            t = (yy + 0.5) / h                # 0 顶 1 底
            half = w * (0.10 + 0.30 * (t ** 0.7))
            if abs((xx + 0.5) - cx) <= half:
                out.add((x0 + xx, y0 + yy))
    return out


def _draw_arrow(img, box, full):
    """箭头的一帧。full=True 是橙色（画在面板外的满帧）。"""
    x, y, w, h = box
    px = img.load()
    # 凹槽底
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px[xx, yy] = (110, 110, 110, 255)
    for yy in range(y, y + h):
        px[x, yy] = (80, 80, 80, 255)
        px[x + w - 1, yy] = (150, 150, 150, 255)
    for xx in range(x, x + w):
        px[xx, y] = (70, 70, 70, 255)
        px[xx, y + h - 1] = (160, 160, 160, 255)
    # 箭头本体
    body = (232, 150, 60) if full else (150, 150, 150)
    hi = (250, 186, 96) if full else (170, 170, 170)
    for (xx, yy) in _arrow_mask(x, y, w, h):
        px[xx, yy] = (hi if (xx + yy) % 3 else body) + (255,)


def _draw_flame(img, box, full):
    """火苗的一帧。full=True 是橙红火焰（画在面板外的满帧）。"""
    x, y, w, h = box
    px = img.load()
    # 炉膛底
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px[xx, yy] = (60, 60, 60, 255)
    for yy in range(y, y + h):
        px[x, yy] = (80, 80, 80, 255)
        px[x + w - 1, yy] = (150, 150, 150, 255)
    for xx in range(x, x + w):
        px[xx, y] = (70, 70, 70, 255)
        px[xx, y + h - 1] = (160, 160, 160, 255)
    for (xx, yy) in _flame_mask(x, y, w, h):
        t = (yy - y) / float(h)               # 0 顶 1 底
        if full:
            if t < 0.35:
                c = (250, 176, 60)
            elif t < 0.70:
                c = (222, 96, 22)
            else:
                c = (150, 46, 12)
        else:
            c = (96, 74, 46)                  # 未点燃时只留一个暗轮廓
        px[xx, yy] = c + (255,)


def _draw_energy(img, box, full):
    """竖排电量条的一帧。"""
    x, y, w, h = box
    px = img.load()
    fill = (232, 150, 60) if full else (60, 60, 60)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px[xx, yy] = fill + (255,)
    if full:
        # 每 4 像素一道亮纹，"电"的感觉比纯色块好
        for yy in range(y + 1, y + h - 1):
            if (yy - y) % 4 == 0:
                for xx in range(x + 1, x + w - 1):
                    px[xx, yy] = (250, 186, 96, 255)
    for xx in range(x, x + w):
        px[xx, y] = (40, 40, 40, 255)
        px[xx, y + h - 1] = (150, 150, 150, 255)
    for yy in range(y, y + h):
        px[x, yy] = (40, 40, 40, 255)
        px[x + w - 1, yy] = (150, 150, 150, 255)


def processor_gui():
    """加工机界面：面板 + 两个槽 + 空箭头（满箭头画在面板外）。"""
    img = _canvas()
    img.alpha_composite(_panel(GUI_W, GUI_H, 701), (0, 0))
    _slot(img, PROC_INPUT)
    _slot(img, PROC_OUTPUT)
    _player_inventory(img)
    _draw_arrow(img, ARROW, full=False)                  # 面板内：空箭头
    _draw_arrow(img, (ARROW_FULL[0], ARROW_FULL[1],
                      ARROW[2], ARROW[3]), full=True)    # 面板外：满箭头
    _draw_energy(img, ENERGY, full=False)
    _draw_energy(img, (ENERGY_FULL[0], ENERGY_FULL[1],
                       ENERGY[2], ENERGY[3]), full=True)
    return img


def generator_gui():
    """发电机界面：面板 + 燃料槽 + 空火苗（满火苗画在面板外）。"""
    img = _canvas()
    img.alpha_composite(_panel(GUI_W, GUI_H, 709), (0, 0))
    _slot(img, GEN_FUEL)
    _player_inventory(img)
    _draw_flame(img, FLAME, full=False)                  # 面板内：空火苗
    _draw_flame(img, (FLAME_FULL[0], FLAME_FULL[1],
                      FLAME[2], FLAME[3]), full=True)    # 面板外：满火苗
    _draw_energy(img, ENERGY, full=False)
    _draw_energy(img, (ENERGY_FULL[0], ENERGY_FULL[1],
                       ENERGY[2], ENERGY[3]), full=True)
    return img


# ======================================================================
# 摆在地上的菜与器皿的共享材质
# ======================================================================

def dish_material_textures():
    """菜与器皿用到的共享材质（颜色由方块着色染）。"""
    import os
    import sys
    import zlib
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dish_models as DM

    grain = {"dish_wood": "x", "dish_clay": "d", "dish_porcelain": None,
             "dish_iron": "x"}

    out = []
    for name, ramp in DM.MATERIALS.items():
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
        style = grain.get(name)
        period = 8 if SIZE >= 32 else 4
        seed = zlib.crc32(name.encode("utf-8")) & 0xFFFF
        for y in range(SIZE):
            for x in range(SIZE):
                if style == "x":
                    a = _noise((x * 2) % (period * 2), y // 3, seed)
                    b = _noise(x // period, y // period, seed + 11)
                    v = 0.45 * a + 0.55 * b
                elif style == "d":
                    a = _noise(x // period, y // period, seed)
                    b = _noise((x + y) // (period * 2), (y - x) // (period * 2),
                               seed + 7)
                    v = 0.6 * a + 0.4 * b
                else:
                    v = 0.5 + 0.5 * _noise(x // (period * 2), y // (period * 2),
                                           seed)
                    if _noise(x, y, seed + 31) > 0.965:
                        v = 1.0
                idx = _quantize(v, 4, x, y)
                img.putpixel((x, y), ramp[idx] + (255,))
        out.append((img, name + ".png"))
    return out


# ======================================================================
def main(block_dir, item_dir, gui_dir):
    import os

    targets = []
    for name, fn in BLOCK_TEXTURES.items():
        targets.append((fn(), block_dir, "%s.png" % name))

    targets.append((furnace_generator_item(), item_dir, "furnace_generator.png"))
    targets.append((electric_mill_item(), item_dir, "electric_mill.png"))
    targets.append((electric_sheller_item(), item_dir, "electric_sheller.png"))
    targets.append((processor_gui(), gui_dir, "processor.png"))
    targets.append((generator_gui(), gui_dir, "generator.png"))

    for img, name in dish_material_textures():
        targets.append((img, block_dir, name))

    for img, target, name in targets:
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, name)
        img.save(path)
        print("wrote %-64s %dx%d" % (os.path.relpath(path), img.width, img.height))
