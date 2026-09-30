# -*- coding: utf-8 -*-
"""机器的方块材质、物品图标，以及装置界面的底图。

    python tools/build_textures.py --only machines

画材质的三条规矩
----------------
1. **只用 2~3 种颜色**：像素画里颜色一多就糊。石、木、铁各给一套 4 档色阶，
   但一张图里最多用 3 档。
2. **图案周期必须整除 16**：石缝 8、木板 4、铆钉错缝 8/4。
   这样任意两块相邻的同材质面都能对上，机器拼起来不会有断裂的纹路。
3. **不画逐像素噪点**：噪点既费像素，又会在方块边界处"断掉"，
   因为每个面都是独立采样的。改用**结构性花纹**（砌缝、板缝、铆钉），
   这些东西的周期是死的，跨面一定对齐。

关于 UV
-------
模型那边已经改成"按面的大小自动算 UV"（见 `machine_models.box()`），
所以这里只需要保证材质本身是**可平铺**的：任何一块区域看起来都合理。
"""

import math
import os
import zlib

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
# 石：偏冷的青灰（现实里的磨盘石就是这种青石）
STONE = [(96, 98, 100), (118, 120, 122), (140, 142, 144), (162, 164, 166)]
# 木：老榆木/松木，偏黄褐
WOOD = [(104, 68, 36), (132, 90, 50), (158, 112, 66), (184, 138, 88)]
# 湿木：泡在水里的木料，整体压暗压绿（水车专用，和普通木料区分开）
WET_WOOD = [(62, 54, 38), (84, 74, 52), (108, 96, 68), (132, 118, 86)]
# 铁：偏冷的灰
IRON = [(84, 88, 94), (106, 110, 118), (130, 134, 142), (158, 162, 170)]
# 深铁：料斗内壁 / 磨盘轴孔，比普通铁更暗
DARK_IRON = [(52, 54, 58), (68, 70, 76), (86, 88, 94), (106, 108, 114)]


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


# ======================================================================
# 方块材质
# ======================================================================

def machine_stone():
    """砌石：8×8 一块，缝 1 像素。

    每块石头的左上角压一档亮、右下角压一档暗 —— 不用噪点也能有体积感，
    而且因为周期是 8，跨方块、跨面永远对齐。
    """
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


def machine_wood():
    """木：4 像素一块横板，板缝在下沿。周期 4。"""
    img = _opaque()
    for y in range(SIZE):
        r = y % 4
        if r == 3:
            c = WOOD[0]                      # 板缝
        elif r == 0:
            c = WOOD[3]                      # 板上沿受光
        else:
            c = WOOD[1]
        for x in range(SIZE):
            # 每 8 像素一个竖向木节，位置固定，保证可平铺
            if x % 8 == 5 and r == 1:
                c = WOOD[2]
            _px(img, x, y, c)
    return img


def machine_iron():
    """铁：错缝铆接板。周期 8/4。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if y % 8 == 0:
                c = IRON[0]                  # 横向接缝
            elif (x % 8 == 0) and (y % 8 < 5):
                c = IRON[0]                  # 竖向接缝（错缝）
            else:
                c = IRON[1]
            # 铆钉：每 8 像素一颗，位置固定
            if (x % 8, y % 8) in ((2, 4), (6, 1)):
                c = IRON[3]
            _px(img, x, y, c)
    return img


def machine_wheel():
    """水车叶板：泡过水的深色木料 + 每 4 像素一道横向水痕。周期 4。"""
    img = _opaque()
    for y in range(SIZE):
        r = y % 4
        if r == 3:
            c = WET_WOOD[0]
        elif r == 0:
            c = WET_WOOD[2]
        else:
            c = WET_WOOD[1]
        for x in range(SIZE):
            # 每 8 像素一小段深色，模拟年轮 / 水渍
            if (x % 8) in (2, 3) and r == 2:
                c = WET_WOOD[0]
            _px(img, x, y, c)
    return img


def machine_millstone():
    """磨盘顶面：同心磨纹 + 四道放射状槽 + 中央轴孔。

    刻意用一套**比砌石深得多**的青黑色 —— 磨盘是整台水磨的主角，
    颜色要是和石台一个调子，摆在一起就完全看不出哪块是磨盘了。
    """
    img = _opaque()
    dark = [(58, 60, 62), (78, 80, 82), (98, 100, 102), (118, 120, 122)]
    cx = cy = SIZE / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy) / (SIZE / 2.0)
            if d < 0.16:
                c = DARK_IRON[0]
            elif d > 0.93:
                c = dark[0]
            elif abs(d - 0.62) < 0.07 or abs(d - 0.80) < 0.06:
                c = dark[0]
            else:
                c = dark[1]
            ang = math.atan2(dy, dx)
            if 0.16 < d < 0.93 and abs(math.sin(ang * 2.0)) < 0.16:
                c = dark[0]
            _px(img, x, y, c)
    return img


def machine_hopper():
    """料斗内壁：深色铁皮 + 每 8 像素一道折缝（像钣金压出来的槽）。周期 8。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if x % 8 == 0:
                c = DARK_IRON[0]             # 折缝
            elif x % 8 == 1:
                c = DARK_IRON[3]             # 折缝旁的受光面
            else:
                c = DARK_IRON[1]
            _px(img, x, y, c)
    return img


# ----------------------------------------------------------------------
# 标记性贴图：机器是实心的、没法挖洞，所以"水车装这儿 / 谷子倒这儿"
# 这类信息只能靠贴在特定面上的图案来表达。
# ----------------------------------------------------------------------

def machine_axle():
    """水车轴座：一块铁底板，正中一个带黄油嘴的轴承孔。

    贴在水磨塔架朝外的那一面 —— 玩家一眼就知道水车挂这里。
    """
    img = _opaque()
    cx = cy = SIZE / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d > 7.2:
                c = WOOD[1]                  # 板外的木身
            elif d > 6.4:
                c = IRON[0]
            elif d > 3.2:
                # 轴承盘面：左上亮、右下暗
                lit = 0.5 + 0.5 * (1.0 - min(1.0, d / 6.4))
                c = IRON[3] if (x + y) < SIZE - 2 else IRON[1]
                if d > 5.6:
                    c = IRON[1]
            elif d > 1.8:
                c = DARK_IRON[1]             # 轴孔内圈
            else:
                c = DARK_IRON[0]             # 轴孔
            _px(img, x, y, c)
    # 四角螺栓
    for (bx, by) in ((3, 3), (12, 3), (3, 12), (12, 12)):
        _px(img, bx, by, IRON[3])
    return img


def machine_crank():
    """摇柄那面：木板 + 一个铁曲柄盘，盘上伸出一条摇臂。"""
    img = machine_wood()
    cx = cy = SIZE / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= 3.0:
                c = IRON[1] if d > 1.6 else IRON[3]
                if d <= 0.9:
                    c = DARK_IRON[0]
                _px(img, x, y, c)
    # 摇臂：从盘心往右下伸出去
    for i in range(4, 7):
        for j in range(-1, 2):
            _px(img, int(cx) + i, int(cy) + i + j, IRON[2])
    return img


def machine_hopper_top():
    """料斗顶面：一圈圈往里收的方口 —— 从上往下看就是"可以往里倒谷子"。

    用同心方框而不是挖洞：挖洞会让侧面看穿，方框既表达了漏斗，
    又完全实心。
    """
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            # 到最近边的距离（0 = 贴图边缘）
            e = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if e >= 7:
                c = "#" and DARK_IRON[0]     # 最里：斗底（最暗）
            elif e >= 5:
                c = DARK_IRON[1]
            elif e >= 3:
                c = DARK_IRON[2]
            elif e >= 2:
                c = IRON[1]                  # 铁皮斜坡
            elif e >= 1:
                c = WOOD[2]                  # 木口沿
            else:
                c = WOOD[0]
            _px(img, x, y, c)
    # 四角各一颗铆钉，强调这是"一圈框"
    for (bx, by) in ((2, 2), (13, 2), (2, 13), (13, 13)):
        _px(img, bx, by, IRON[3])
    return img


def machine_outlet():
    """出料口那一面：木身上开一条横向的深色出料槽。"""
    img = machine_wood()
    for y in range(int(6.0 * U), int(11.0 * U)):
        for x in range(int(1.0 * U), int(15.0 * U)):
            if y < int(6.8 * U) or y >= int(10.2 * U):
                c = WOOD[0]                  # 槽口上下沿
            else:
                c = DARK_IRON[0]             # 槽内（深色，看得出是通的）
            _px(img, x, y, c)
    return img


BLOCK_TEXTURES = {
    "machine_stone": machine_stone,
    "machine_wood": machine_wood,
    "machine_iron": machine_iron,
    "machine_wheel": machine_wheel,
    "machine_millstone": machine_millstone,
    "machine_hopper": machine_hopper,
    "machine_axle": machine_axle,
    "machine_crank": machine_crank,
    "machine_hopper_top": machine_hopper_top,
    "machine_outlet": machine_outlet,
}


# ======================================================================
# 物品图标
# ======================================================================

def _blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def _shadow(img, alpha=110, dx=1, dy=2):
    """把图像自身当遮罩，往右下投一层阴影 —— 原版物品图标的常规做法。"""
    a = img.getchannel("A")
    sh = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.alpha_composite(sh, (dx, dy))
    out.alpha_composite(img)
    return out


def water_mill_item():
    """水磨图标：一块立起来的磨盘 + 中间轴孔 + 底座。

    直接用磨盘的正面剪影，比"截一段方块顶面"好认得多。
    """
    img = _blank()
    cx = cy = 8.0
    r_out = 6.5
    # 盘身
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.7 - cy) / r_out
            if d <= 1.0:
                if d > 0.84:
                    c = STONE[0]
                elif d < 0.18:
                    c = DARK_IRON[0]
                elif d < 0.26:
                    c = STONE[3]
                elif abs(d - 0.52) < 0.075 or abs(d - 0.70) < 0.065:
                    c = STONE[0]
                else:
                    c = STONE[2]
                _px(img, x, y, c)
    # 底座：一条木台
    for y in range(int(13.2 * U), int(15.4 * U)):
        for x in range(int(1.0 * U), int(15.0 * U)):
            _px(img, x, y, WOOD[1] if y < 14.6 * U else WOOD[0])
    return _shadow(img)


def grain_sheller_item():
    """碾米机图标：木机箱 + 顶上料斗 + 侧面摇柄。"""
    img = _blank()
    # 机箱
    for y in range(int(6.0 * U), int(13.4 * U)):
        for x in range(int(2.0 * U), int(12.4 * U)):
            r = (y // max(1, int(3 * U))) % 2
            _px(img, x, y, WOOD[2] if r else WOOD[1])
    # 上下铁箍
    for y in list(range(int(6.4 * U), int(7.4 * U))) + \
             list(range(int(12.0 * U), int(13.0 * U))):
        for x in range(int(2.0 * U), int(12.4 * U)):
            _px(img, x, y, IRON[1] if y % 2 else IRON[2])
    # 料斗：上宽下窄的梯形
    for i, y in enumerate(range(int(2.0 * U), int(6.0 * U))):
        t = i / max(1.0, 4.0 * U - 1)
        half = (1.6 + 2.4 * t) * U
        for x in range(int(7.2 * U - half), int(7.2 * U + half)):
            _px(img, x, y, DARK_IRON[2] if x % 2 else DARK_IRON[1])
    # 摇柄：从右侧伸出的弯柄
    for x in range(int(12.4 * U), int(15.0 * U)):
        for y in range(int(8.4 * U), int(9.8 * U)):
            _px(img, x, y, IRON[2])
    for y in range(int(6.4 * U), int(8.6 * U)):
        for x in range(int(14.0 * U), int(15.4 * U)):
            _px(img, x, y, WOOD[2])
    return _shadow(img)


def water_mill_part_item():
    """水磨部件图标：一块砌石台。"""
    img = _blank()
    for y in range(int(4.5 * U), int(12.5 * U)):
        for x in range(int(1.5 * U), int(14.5 * U)):
            lx, ly = x - int(1.5 * U), y - int(4.5 * U)
            if lx % max(1, int(3 * U)) == 0 or ly % max(1, int(4 * U)) == 0:
                c = STONE[0]
            elif lx % max(1, int(3 * U)) == 1:
                c = STONE[3]
            else:
                c = STONE[1]
            _px(img, x, y, c)
    # 顶面亮一档，做出"看得到台面"的厚度
    for x in range(int(1.5 * U), int(14.5 * U)):
        for y in range(int(3.6 * U), int(4.5 * U)):
            _px(img, x, y, STONE[2])
    return _shadow(img)


def grain_sheller_part_item():
    """碾米机部件图标：一根带铁箍的木立柱 + 一小段横梁。"""
    img = _blank()
    # 立板
    for y in range(int(2.5 * U), int(14.4 * U)):
        for x in range(int(4.0 * U), int(11.0 * U)):
            r = (y // max(1, int(3 * U))) % 2
            _px(img, x, y, WOOD[2] if r else WOOD[1])
    for y in list(range(int(3.4 * U), int(4.6 * U))) + \
             list(range(int(12.2 * U), int(13.4 * U))):
        for x in range(int(4.0 * U), int(11.0 * U)):
            _px(img, x, y, IRON[1] if (x + y) % 2 else IRON[2])
    # 横梁
    for y in range(int(7.0 * U), int(9.0 * U)):
        for x in range(int(10.6 * U), int(14.6 * U)):
            _px(img, x, y, WOOD[2])
    return _shadow(img)


def water_wheel_item():
    """水车图标：正面看的一个木轮（轮缘 + 四根辐条 + 铁轮毂）。"""
    img = _blank()
    cx = cy = 8.0
    r_out, r_in = 7.2, 5.6
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d > r_out:
                continue
            if d > r_in:
                # 轮缘
                _px(img, x, y, WET_WOOD[2] if (x + y) % 4 < 2 else WET_WOOD[1])
            elif d < 1.6:
                _px(img, x, y, IRON[1])
            else:
                # 辐条：十字
                dx, dy = abs(x + 0.5 - cx), abs(y + 0.5 - cy)
                if dx < 0.9 or dy < 0.9:
                    _px(img, x, y, WET_WOOD[1])
    # 轮毂
    for (x, y) in ((cx, cy),):
        for yy in range(SIZE):
            for xx in range(SIZE):
                if math.hypot(xx + 0.5 - x, yy + 0.5 - y) < 1.7:
                    _px(img, xx, yy, IRON[1])
    return _shadow(img)


# ======================================================================
# 装置界面底图
# ======================================================================

def processor_gui():
    """装置界面底图：176x166，MC 风格的木/石面板 + 两个槽位 + 箭头。"""
    W, H = 176, 166
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    for y in range(H):
        for x in range(W):
            v = 0.9 + 0.1 * _noise(x // 2, y // 2, 701)
            base = (198, 198, 198)
            if x < 3 or y < 3 or x >= W - 3 or y >= H - 3:
                base = (85, 85, 85)          # 外描边
            elif x < 5 or y < 5 or x >= W - 5 or y >= H - 5:
                base = (238, 238, 238)       # 内高光
            px[x, y] = tuple(min(255, int(ch * v)) for ch in base) + (255,)

    def slot(sx, sy):
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

    # 与 ProcessorMenu 的槽位坐标一致（减 1：物品渲染在槽位左上角偏 1 像素）
    slot(56 - 1, 35 - 1)
    slot(116 - 1, 35 - 1)
    for row in range(3):
        for col in range(9):
            slot(8 + col * 18 - 1, 84 + row * 18 - 1)
    for col in range(9):
        slot(8 + col * 18 - 1, 142 - 1)

    ax, ay, aw, ah = 79, 34, 24, 17
    for y in range(ay, ay + ah):
        for x in range(ax, ax + aw):
            px[x, y] = (120, 120, 120, 255)
    for x in range(ax, ax + aw):
        px[x, ay] = (60, 60, 60, 255)
    for y in range(ay + 1, ay + ah):
        for x in range(ax + 1, ax + aw):
            px[x, y] = (232, 150, 60, 255)
    for y in range(ay + 1, ay + ah - 1):
        for x in range(ax + 1, ax + aw - 1):
            if (x + y) % 3 == 0:
                px[x, y] = (250, 186, 96, 255)
    return img


# ======================================================================
# 摆在地上的菜与器皿的共享材质
# ======================================================================

def dish_material_textures():
    """菜与器皿用到的 6 张共享材质（颜色由方块着色染）。"""
    import sys
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
    targets = []
    for name, fn in BLOCK_TEXTURES.items():
        targets.append((fn(), block_dir, "%s.png" % name))

    # 物品图标：
    #   机器核心 -> 结构复杂，单独画；部件 -> 就是它的样子，直接当图标
    targets.append((water_mill_item(), item_dir, "water_mill.png"))
    targets.append((grain_sheller_item(), item_dir, "grain_sheller.png"))
    targets.append((water_mill_part_item(), item_dir, "water_mill_part.png"))
    targets.append((grain_sheller_part_item(), item_dir, "grain_sheller_part.png"))
    targets.append((water_wheel_item(), item_dir, "water_wheel.png"))
    targets.append((processor_gui(), gui_dir, "processor.png"))

    for img, name in dish_material_textures():
        targets.append((img, block_dir, name))

    for img, target, name in targets:
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, name)
        img.save(path)
        print("wrote %-64s %dx%d" % (os.path.relpath(path), img.width, img.height))
