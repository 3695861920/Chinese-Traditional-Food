# -*- coding: utf-8 -*-
"""大型机器的方块纹理、物品图标与装置界面底图。

    python tools/build_textures.py --only machines

画风约定（**像素尽可能少 + 纹理要连得自然**）
------------------------------------------
这两条要求其实是同一件事的两面：

1. **颜色少**：每张方块贴图最多 **3 种颜色**（石 / 木 / 铁各一套 4 档色阶里取 3 档）。
   没有渐变、没有抗锯齿 —— 就是像素画本来的样子。原版的石头、木板、
   石砖也都是这个量级。
2. **图案周期整除 16**：所有花纹（石缝 8 像素、木板 4 像素、铁板 4 像素）
   的周期都能整除 16，所以贴图**上下左右都能无缝平铺**。
   相邻两个方块的同材质面接在一起时，花纹是连续的，看不出方块边界
   —— 这正是"一体成型"的观感来源之一。
3. **不撒噪点**：逐像素的随机颗粒既费颜色又必然在方块边界断开，
   所以这里一个像素的随机噪点都不用。需要"脏感"时用规则的缝和高光代替。

配合 `machine_models.py` 里"内部面根本不生成"的做法，机器外壳就是
一整块连续表面 + 连续纹理。
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
# 色阶：每套只用得到其中 3 档
# ======================================================================
STONE = [(112, 110, 106), (134, 132, 128), (156, 154, 150), (178, 176, 172)]
WOOD = [(120, 80, 44), (146, 100, 56), (170, 122, 70), (196, 148, 92)]
IRON = [(96, 100, 108), (120, 124, 132), (146, 150, 158), (176, 180, 188)]


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


# ======================================================================
# 6 张方块贴图
# ======================================================================

def machine_stone():
    """石：8×8 一块，缝 1 像素，每块石头上固定位置一颗高光。3 色，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            if (x % 8 == 0) or (y % 8 == 0):
                c = STONE[1]                      # 石缝
            else:
                c = STONE[2]                      # 石面
                if (x % 8, y % 8) == (2, 2):
                    c = STONE[3]                  # 高光
            _px(img, x, y, c)
    return img


def machine_wood():
    """木：4 像素一块横板，中间一行亮、最下一行是缝。3 色，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        r = y % 4
        c = WOOD[0] if r == 3 else (WOOD[2] if r == 0 else WOOD[1])
        for x in range(SIZE):
            _px(img, x, y, c)
    return img


def machine_iron():
    """铁：4×8 的错缝铆接板。2 色，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            c = IRON[1] if ((x // 4) + (y // 8)) % 2 == 0 else IRON[2]
            if y % 8 == 0:
                c = IRON[0]                       # 横向接缝
            _px(img, x, y, c)
    return img


def machine_wheel():
    """水车叶轮：沿 X 每 8 像素一换色的木板，配 8 像素一行的缝。3 色，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            c = WOOD[2] if (x % 8) < 4 else WOOD[1]
            if y % 8 == 0:
                c = WOOD[0]
            _px(img, x, y, c)
    return img


def machine_millstone():
    """磨盘顶面：同心磨纹 + 中央轴孔。只用在核心顶面，不需要平铺。"""
    img = _opaque()
    cx = cy = SIZE / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (SIZE / 2.0)
            if d < 0.20:
                c = IRON[0]                       # 轴孔
            elif d < 0.30:
                c = STONE[3]
            elif d < 0.62:
                c = STONE[2]
            elif d < 0.76:
                c = STONE[1]                      # 一圈磨纹
            else:
                c = STONE[2]
            _px(img, x, y, c)
    return img


def machine_hopper():
    """料斗内壁：更暗的木色 + 4 像素一道的竖直木纹。2 色，可平铺。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            c = WOOD[1] if (x % 4) < 2 else WOOD[0]
            _px(img, x, y, c)
    return img


BLOCK_TEXTURES = {
    "machine_stone": machine_stone,
    "machine_wood": machine_wood,
    "machine_iron": machine_iron,
    "machine_wheel": machine_wheel,
    "machine_millstone": machine_millstone,
    "machine_hopper": machine_hopper,
}


# ======================================================================
# 物品图标
# ======================================================================

def _item_from_block(top, side=None):
    """把方块顶面当图标，加上右下投影，做出"物品"的感觉。"""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    inset = 1.2 * U
    body = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    body.paste(top.crop((int(inset), int(inset), SIZE - int(inset), SIZE - int(inset))),
               (int(inset), int(inset * 0.7)))
    if side is not None:
        strip = side.crop((0, 0, SIZE, int(2.6 * U)))
        body.paste(strip.resize((SIZE - int(inset * 2), int(2.2 * U)), Image.NEAREST),
                   (int(inset), SIZE - int(inset * 1.2)))
    img.alpha_composite(body)
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    a = body.getchannel("A")
    sh = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 90))
    sh.putalpha(a.point(lambda v: int(v * 0.35)))
    shadow.alpha_composite(sh, (2, 3))
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.alpha_composite(shadow)
    out.alpha_composite(img)
    return out


def water_wheel_item():
    """水车图标：正面看的一个木轮（轮缘 + 四根辐条 + 铁轮毂）。

    整个图标只用 3 种颜色，靠"圆环 + 十字辐条"这个剪影认出来，
    不做任何渐变 —— 和原版工具图标的画法一致。
    """
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cx = cy = 8.0
    r_out, r_in = 7.0, 5.2
    for y in range(SIZE):
        for x in range(SIZE):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r_in <= d <= r_out:
                # 轮缘：外侧一档暗色当描边
                c = WOOD[0] if d > r_out - 0.9 else WOOD[2]
                _px(img, x, y, c)
    # 四根辐条
    for (ax, ay, bx, by) in ((8, 2.6, 8, 13.4), (2.6, 8, 13.4, 8),
                             (4.2, 4.2, 11.8, 11.8), (11.8, 4.2, 4.2, 11.8)):
        steps = int(max(abs(bx - ax), abs(by - ay)) * 2) + 1
        for i in range(steps):
            t = i / max(1, steps - 1)
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            _px(img, x * U, y * U, WOOD[1])
            _px(img, x * U + 1, y * U, WOOD[1])
            _px(img, x * U, y * U + 1, WOOD[1])
    # 轮毂
    for y in range(SIZE):
        for x in range(SIZE):
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= 1.6:
                _px(img, x, y, IRON[1])
    return img


def processor_gui():
    """装置界面底图：176x166，MC 风格的灰面板 + 两个槽位 + 箭头。"""
    W, H = 176, 166
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    for y in range(H):
        for x in range(W):
            base = (198, 198, 198)
            if x < 3 or y < 3 or x >= W - 3 or y >= H - 3:
                base = (85, 85, 85)
            elif x < 5 or y < 5 or x >= W - 5 or y >= H - 5:
                base = (238, 238, 238)
            px[x, y] = base + (255,)

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

    # 与 ProcessorMenu 的槽位坐标一致（要减 1，物品渲染在槽位左上角偏 1 像素）
    slot(56 - 1, 35 - 1)
    slot(116 - 1, 35 - 1)
    for row in range(3):
        for col in range(9):
            slot(8 + col * 18 - 1, 84 + row * 18 - 1)
    for col in range(9):
        slot(8 + col * 18 - 1, 142 - 1)

    # 中间的进度箭头（运行时按比例裁切）
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
# 摆在地上的菜的共享材质（属于"餐具"那一套，颜色由方块着色染）
# ======================================================================

def dish_material_textures():
    """菜与器皿用到的 6 张共享材质。

    同样只用 4 档色阶 + 柏叶抖动，并且用**低频**（每 4~8 像素才变一次）
    的花纹而不是白噪点 —— 叠层之间就能自然过渡，看起来是光滑的釉面。
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dish_models as DM

    grain = {
        "dish_wood": "x",
        "dish_clay": "d",
        "dish_porcelain": None,
        "dish_iron": "x",
    }

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
    # 物品图标
    targets.append((_item_from_block(machine_millstone(), machine_stone()),
                    item_dir, "water_mill.png"))
    targets.append((_item_from_block(machine_wood(), machine_iron()),
                    item_dir, "grain_sheller.png"))
    targets.append((water_wheel_item(), item_dir, "water_wheel.png"))
    targets.append((processor_gui(), gui_dir, "processor.png"))
    for img, name in dish_material_textures():
        targets.append((img, block_dir, name))

    for img, target, name in targets:
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, name)
        img.save(path)
        print("wrote %-64s %dx%d" % (os.path.relpath(path), img.width, img.height))
