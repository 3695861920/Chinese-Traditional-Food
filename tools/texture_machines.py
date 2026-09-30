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
# 砖：炉灶的砖石台体，比砌石暖
BRICK = [(122, 76, 60), (150, 96, 74), (178, 120, 94), (204, 148, 118)]
# 竹：蒸笼的竹篾，偏黄绿
BAMBOO = [(150, 152, 96), (176, 178, 120), (200, 202, 148), (222, 224, 176)]
# 蒸汽：几乎是白的，带一点灰蓝
STEAM = [(198, 206, 212), (218, 226, 232), (236, 242, 246), (250, 252, 254)]
# 灶上的菜（炒锅 / 蒸笼里的内容物）。**不走方块着色** ——
# 锅具是功能方块而不是摆盘方块，没有颜色属性，所以这里直接画成"熟食色"。
COOKED = [(126, 74, 40), (156, 96, 52), (186, 124, 72), (212, 156, 104)]


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


def machine_brick():
    """砖石台面：错缝砌法，砖缝每 8 像素一道（周期整除 16，可平铺）。

    炉灶的台体。和 `machine_stone` 的区别是**暖色调 + 有砖缝** ——
    灶台和机器放在一起时要一眼看出"这是个砌出来的灶"。
    """
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            row = y // 4
            # 错缝：奇数行整体错开半块砖
            offset = (row % 2) * 4
            if y % 4 == 3:
                c = BRICK[0]                  # 横缝
            elif (x + offset) % 8 == 7:
                c = BRICK[0]                  # 竖缝
            else:
                # 每块砖给一点明暗差，砖墙才不像贴纸
                tone = 1 + ((x // 8 + row) % 3)
                c = BRICK[min(3, tone)]
                if _noise(x, y, 733) > 0.86:
                    c = BRICK[0]              # 麻点
            _px(img, x, y, c)
    return img


def machine_bamboo():
    """竹篾编面：横竖交织的竹条，周期 4 与 2。蒸笼用。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if y % 4 == 0:
                c = BAMBOO[0]                 # 横向竹条的缝
            elif x % 2 == 0:
                c = BAMBOO[2]                 # 竖向竹条
            else:
                c = BAMBOO[1]
            if (x % 8) in (0, 1) and y % 4 != 0:
                c = BAMBOO[3]                 # 每 8 像素一根亮篾
            _px(img, x, y, c)
    return img


def machine_steam():
    """蒸汽：几乎纯白、带一点灰蓝，用低频噪声做出"云"的感觉。

    **不画结构花纹** —— 蒸汽本来就是无定形的，加线反而假。
    """
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            v = 0.45 + 0.55 * _noise(x // 4, y // 4, 811)
            idx = _quantize(v, 4, x, y)
            c = STEAM[idx]
            _px(img, x, y, c, 235)            # 略透明，蒸汽才轻
    return img


def machine_cooked():
    """锅里的熟食：暖褐色的块状料，带几粒点缀。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            v = 0.35 + 0.65 * _noise(x // 2, y // 2, 907)
            c = COOKED[_quantize(v, 4, x, y)]
            # 几粒深色的花椒 / 葱花
            if _noise(x // 3, y // 3, 919) > 0.88:
                c = COOKED[0]
            _px(img, x, y, c)
    return img


# ======================================================================
# 电磁炉（卡通风）
# ======================================================================

def _cartoon_top(img, seed, on):
    """电磁炉顶面：同心圆线圈 + 粗描边。

    卡通味道全靠三件事：**粗黑边、平涂、高饱和**。
    """
    cx = cy = SIZE / 2.0
    ring_dark = (26, 28, 32)
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (SIZE / 2.0)
            if d > 0.98:
                c = ring_dark                       # 外框
            elif d > 0.86:
                c = (208, 212, 218)                 # 亮圈（不锈钢边）
            elif d > 0.20 and abs((d * 4.0) % 1.0 - 0.5) < 0.16:
                # 线圈：4 条同心环，通电时亮橙红、断电时暗灰
                if on:
                    c = (255, 122, 40) if ((d * 4.0) % 2.0) < 1.0 else (255, 196, 72)
                else:
                    c = (96, 92, 88)
            else:
                c = (54, 56, 62) if not on else (72, 60, 56)
            _px(img, x, y, c)

    # 正中的小圆（磁芯）
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (SIZE / 2.0)
            if d < 0.18:
                _px(img, x, y, (208, 212, 218))
            elif d < 0.22:
                _px(img, x, y, ring_dark)
    # 卡通高光：左上角一块亮斑
    for y in range(int(2 * U), int(5 * U)):
        for x in range(int(2 * U), int(6 * U)):
            if abs(y - 3.5 * U) + abs(x - 3.5 * U) < 2.6 * U:
                _px(img, x, y, (246, 248, 252))
    return img


def machine_cooker_top():
    """电磁炉顶面 —— 断电（暗灰色的线圈）。"""
    return _cartoon_top(_opaque(), 1301, on=False)


def machine_cooker_top_on():
    """电磁炉顶面 —— 通电（发光的橙红线圈）。"""
    return _cartoon_top(_opaque(), 1301, on=True)


def machine_cooker_panel():
    """电磁炉正面那道控制条：一排小圆扭 + 粗描边。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            e = min(y, SIZE - 1 - y)
            if e == 0:
                c = (26, 28, 32)                    # 粗描边
            elif e == 1:
                c = (208, 212, 218)
            else:
                c = (68, 70, 78)
            _px(img, x, y, c)
    # 四个圆钮：两个亮（启用）两个暗
    for i in range(4):
        bx = 2.0 + i * 4.0
        lit = i % 2 == 0
        for y in range(SIZE):
            for x in range(SIZE):
                d = math.hypot((x + 0.5 - bx * U) / U, (y + 0.5 - 8 * U) / U)
                if d < 1.2:
                    _px(img, x, y, (120, 214, 120) if lit else (150, 150, 158))
                elif d < 1.7:
                    _px(img, x, y, (26, 28, 32))
    return img


BLOCK_TEXTURES = {
    "machine_stone": machine_stone,
    "machine_iron": machine_iron,
    "machine_millstone": machine_millstone,
    "machine_grate": machine_grate,
    "machine_vent": machine_vent,
    "machine_coil": machine_coil,
    "machine_hopper": machine_hopper,
    # 灶火系统（电磁炉 / 炒锅 / 蒸笼 / 汤锅）
    "machine_bamboo": machine_bamboo,
    "machine_steam": machine_steam,
    "machine_cooked": machine_cooked,
    # 电磁炉
    "machine_cooker_top": machine_cooker_top,
    "machine_cooker_top_on": machine_cooker_top_on,
    "machine_cooker_panel": machine_cooker_panel,
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


# 机器类的物品图标（名字 -> 画法）。新增大机器时在这里登记即可。
#
# 大型机的图标刻意画得**更满、更复杂**：主体几乎占满整格、没有腿部留空，
# 并且多画双烟囱 / 双磨盘 / 双滚筒这些"多一套部件"的特征 ——
# 放在一起时一眼就能分出哪个是升级版。
def large_furnace_generator_item():
    """图标：双烟囱的大型炉组，正面两扇炉门。"""
    img = _blank()
    # 底座
    _rect(img, 0.8, 12.4, 15.2, 14.6, DARK_IRON[0])
    # 主体（几乎占满）
    _rect(img, 1.2, 3.4, 14.8, 12.4, STONE[1])
    _rect(img, 1.2, 3.4, 14.8, 4.6, STONE[2])
    # 两扇炉门 + 火光
    for i in range(2):
        x0 = 2.0 + i * 6.6
        _rect(img, x0, 5.4, x0 + 5.6, 11.2, DARK_IRON[1])
        for y in range(int(6.2 * U), int(10.6 * U)):
            for x in range(int((x0 + 0.7) * U), int((x0 + 4.9) * U)):
                lvl = (y - 6.2 * U) / (4.4 * U)
                c = FIRE[0] if lvl < 0.35 else (FIRE[1] if lvl < 0.7 else FIRE[2])
                if (x % max(1, int(2 * U))) == 0:
                    c = DARK_IRON[0]
                _px(img, x, y, c)
    # 双烟囱
    for cx in (4.6, 11.4):
        _rect(img, cx - 1.4, 0.8, cx + 1.4, 3.4, IRON[1])
        _rect(img, cx - 1.4, 0.8, cx + 1.4, 1.4, IRON[2])
    # 两侧加强筋
    for i in range(3):
        _rect(img, 0.6, 6.0 + i * 2.2, 1.4, 7.6 + i * 2.2, IRON[3])
        _rect(img, 14.6, 6.0 + i * 2.2, 15.4, 7.6 + i * 2.2, IRON[3])
    return _shadow(img)


def large_electric_mill_item():
    """图标：三层磨盘的大型磨粉机，左右各一个传动轮。"""
    img = _blank()
    _rect(img, 0.8, 10.6, 15.2, 14.6, IRON[0])
    _rect(img, 1.2, 6.4, 14.8, 10.6, IRON[1])
    _rect(img, 1.2, 6.4, 14.8, 7.4, IRON[2])
    # 正面的散热百叶
    for i in range(3):
        _rect(img, 2.6, 7.8 + i * 0.9, 13.4, 8.4 + i * 0.9, IRON[3])
    # 三层磨盘：一圈圈收小
    cx, cy = 8.0, 8.4
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx * U, y + 0.5 - cy * U)
            if d < 5.6 * U:
                if d < 0.9 * U:
                    c = DARK_IRON[0]
                elif d < 3.0 * U:
                    c = MILLSTONE[1]
                elif d < 4.4 * U:
                    c = MILLSTONE[0]
                else:
                    c = MILLSTONE[1]
                _px(img, x, y, c)
    # 左右传动轮
    for x0 in (0.2, 14.2):
        _rect(img, x0, 8.4, x0 + 1.6, 12.4, COPPER[1])
        _rect(img, x0, 8.4, x0 + 1.6, 9.0, COPPER[2])
    # 中心立轴
    _rect(img, 7.2, 1.6, 8.8, 4.2, IRON[1])
    _rect(img, 6.0, 0.8, 10.0, 1.8, COPPER[1])
    return _shadow(img)


def large_electric_sheller_item():
    """图标：双滚筒 + 三层大料斗的大型脱壳机。"""
    img = _blank()
    _rect(img, 0.8, 11.4, 15.2, 14.8, IRON[0])
    _rect(img, 1.2, 7.2, 14.8, 11.4, IRON[1])
    _rect(img, 1.2, 7.2, 14.8, 8.2, IRON[2])
    # 双滚筒（两个并排的圆）
    for cx in (4.8, 11.2):
        for y in range(SIZE):
            for x in range(SIZE):
                d = math.hypot(x + 0.5 - cx * U, y + 0.5 - 9.6 * U)
                if d < 2.4 * U:
                    _px(img, x, y, MILLSTONE[0] if d < 1.6 * U else MILLSTONE[1])
        _rect(img, cx - 0.4, 9.2, cx + 0.4, 10.0, COPPER[2])
    # 三层大料斗（从下往上张开）
    for i, y in enumerate(range(int(3.6 * U), int(7.4 * U))):
        t = i / max(1.0, 3.8 * U - 1)
        half = (1.6 + 3.4 * t) * U
        for x in range(int(8.0 * U - half), int(8.0 * U + half)):
            _px(img, x, y, DARK_IRON[2] if x % max(1, int(U)) else DARK_IRON[1])
    # 顶部排气口
    for cx in (4.0, 12.0):
        _rect(img, cx - 0.8, 2.6, cx + 0.8, 3.6, DARK_IRON[1])
    return _shadow(img)


ITEM_ICONS = {
    "furnace_generator": furnace_generator_item,
    "electric_mill": electric_mill_item,
    "electric_sheller": electric_sheller_item,
    "large_furnace_generator": large_furnace_generator_item,
    "large_electric_mill": large_electric_mill_item,
    "large_electric_sheller": large_electric_sheller_item,
}


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

# ---- 锅具（炒锅 / 蒸笼 / 汤锅）：2×2 四格原料区 ----
# 这四个坐标必须和 ProcessorMenu.GRID_* 一一对应。
COOKER_GRID_X, COOKER_GRID_Y = 44, 24
COOKER_GRID_STEP = 22
COOKER_OUTPUT = (122, 33)
COOKER_ARROW = (92, 33, 24, 17)

# ---- 「正在加工」的高亮框：放在面板外的条带里（见 cooker_gui 的注释）----
SLOT_MARK = (176, 140)

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
    """电动设备的界面：面板 + 一个进料槽 + 出料槽 + 空箭头。"""
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


def cooker_gui():
    """锅具的界面：面板 + **2×2 四格原料区** + 出料槽。

    四格按 ``ProcessorMenu`` 的 ``GRID_INPUT_X/Y/STEP`` 摆，
    箭头也跟着右移 —— 这两处坐标必须和 Java 那边一致，
    改了一边记得改另一边（``tools/preview_gui.py`` 可以对着看）。
    """
    img = _canvas()
    img.alpha_composite(_panel(GUI_W, GUI_H, 733), (0, 0))
    for i in range(4):
        x = COOKER_GRID_X + (i % 2) * COOKER_GRID_STEP
        y = COOKER_GRID_Y + (i // 2) * COOKER_GRID_STEP
        _slot(img, (x, y))
    _slot(img, COOKER_OUTPUT)
    _player_inventory(img)
    _draw_arrow(img, (COOKER_ARROW[0], COOKER_ARROW[1], ARROW[2], ARROW[3]),
                full=False)
    _draw_arrow(img, (ARROW_FULL[0], ARROW_FULL[1],
                      ARROW[2], ARROW[3]), full=True)    # 满箭头（面板外）
    _draw_energy(img, ENERGY, full=False)
    _draw_energy(img, (ENERGY_FULL[0], ENERGY_FULL[1],
                       ENERGY[2], ENERGY[3]), full=True)

    # 选中框：**画在面板外的条带里**。面板是整张 blit 上去的，
    # 画在面板内的话一开始就会显示出来（和"满帧不能放面板里"是同一个坑）。
    _draw_slot_mark(img, (SLOT_MARK[0], SLOT_MARK[1]))
    return img


def _draw_slot_mark(img, box):
    """高亮框：一圈亮黄边 + 内圈暗线，用来标出"正在加工那一格"。"""
    x, y = box
    px = img.load()
    for yy in range(y, y + 20):
        for xx in range(x, x + 20):
            on_border = (xx == x or xx == x + 19 or yy == y or yy == y + 19)
            if not on_border:
                continue
            corner = (xx in (x, x + 19)) and (yy in (y, y + 19))
            px[xx, yy] = (255, 224, 96, 255) if not corner else (255, 250, 200, 255)


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
def main(block_dir, item_dir, gui_dir, finalize=None):
    """生成机器相关的全部贴图。

    ``finalize`` 由 build_textures 传入，只作用于 **item_dir** 里的物品图标
    （统一到 64x64）；方块贴图与界面图保持原分辨率 ——
    方块贴图会被模型按 UV 采样、界面图有固定像素坐标，放大只会白白占图集。
    """
    import os

    targets = []
    for name, fn in BLOCK_TEXTURES.items():
        targets.append((fn(), block_dir, "%s.png" % name))

    for name, fn in ITEM_ICONS.items():
        targets.append((fn(), item_dir, "%s.png" % name))
    targets.append((processor_gui(), gui_dir, "processor.png"))
    targets.append((cooker_gui(), gui_dir, "cooker.png"))
    targets.append((generator_gui(), gui_dir, "generator.png"))

    for img, name in dish_material_textures():
        targets.append((img, block_dir, name))

    for img, target, name in targets:
        if finalize is not None and target == item_dir:
            img = finalize(img)
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, name)
        img.save(path)
        print("wrote %-64s %dx%d" % (os.path.relpath(path), img.width, img.height))
