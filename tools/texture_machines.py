# -*- coding: utf-8 -*-
"""水磨 / 脱壳机的方块纹理，以及装置界面的底图。

    python tools/build_textures.py --only machines
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

STONE = [(112, 110, 106), (134, 132, 128), (156, 154, 150), (178, 176, 172)]
WOOD = [(120, 80, 44), (146, 100, 56), (170, 122, 70), (196, 148, 92)]
IRON = [(96, 100, 108), (120, 124, 132), (146, 150, 158), (176, 180, 188)]
WATER = [(38, 82, 148), (52, 104, 176), (70, 130, 200), (98, 160, 220)]


def bind(noise, bayer, quantize, shade):
    global _noise, _bayer, _quantize, _shade
    _noise, _bayer, _quantize, _shade = noise, bayer, quantize, shade


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


def _stone_base(img, seed, tint=1.0):
    for y in range(SIZE):
        for x in range(SIZE):
            v = 0.5 + 0.5 * _noise(x // 3, y // 3, seed)
            v += (_noise(x, y, seed + 5) - 0.5) * 0.35
            idx = _quantize(v * tint, 4, x, y)
            _px(img, x, y, STONE[idx])


def water_mill_top():
    """水磨顶面：中央磨盘 + 一圈石纹 + 四个推动的辐条。"""
    img = _opaque()
    _stone_base(img, 211)
    cx = cy = SIZE / 2.0
    R = 6.4 * U
    for y in range(SIZE):
        for x in range(SIZE):
            dx = x + 0.5 - cx
            dy = y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R:
                continue
            t = r / R
            if t > 0.86:
                continue                       # 外圈留给底座
            # 磨盘：中心略亮，靠近外缘有齿槽
            lit = 0.78 - 0.34 * (t ** 1.5)
            if 0.44 < t < 0.58:
                lit -= 0.22                     # 一圈凹槽
            lit += (_noise(x, y, 307) - 0.5) * 0.10
            idx = _quantize(lit, 4, x, y)
            _px(img, x, y, STONE[idx])
    # 辐条
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        for t in range(0, 40):
            f = t / 39.0
            sx = cx + math.cos(a) * f * R * 0.86
            sy = cy + math.sin(a) * f * R * 0.86
            for (dx2, dy2) in ((-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)):
                _px(img, sx + dx2, sy + dy2, IRON[2])
    # 中心轴
    for (x, y) in _disc(cx, cy, 1.1 * U):
        _px(img, x, y, IRON[3])
    return img


def _disc(cx, cy, r):
    out = []
    for y in range(max(0, int(cy - r - 1)), min(SIZE, int(cy + r + 2))):
        for x in range(max(0, int(cx - r - 1)), min(SIZE, int(cx + r + 2))):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            if dx * dx + dy * dy <= r * r:
                out.append((x, y))
    return out


def water_mill_side():
    """水磨侧面：石块底座 + 一条流动的水痕（暗示水轮）。"""
    img = _opaque()
    for y in range(SIZE):
        v = 0.68 - 0.42 * ((y + 0.5) / SIZE) ** 1.1
        for x in range(SIZE):
            idx = _quantize(v, 4, x, y)
            c = STONE[idx]
            c = _shade(c, (_noise(x, y, 401) - 0.5) * 0.08)
            # 中间一条水带
            if 4.0 * U <= y < 9.0 * U:
                wv = 0.45 + 0.5 * _noise(x // 2, y, 409)
                wi = _quantize(wv, 4, x, y)
                c = WATER[wi]
            elif y < 1.0 * U:
                c = _shade(c, 0.14)
            elif y > 15.0 * U:
                c = _shade(c, -0.24)
            _px(img, x, y, c)
    return img


def grain_sheller_top():
    """脱壳机顶面：木箱 + 中央铁漏斗口。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            plank = int((y / SIZE) * 4)
            ly = y - plank * (SIZE / 4.0)
            lit = 0.44 + 0.32 * (1.0 - ly / (SIZE / 4.0)) \
                + 0.28 * (_noise(x % 11, y, 163 + plank * 13) * 0.6
                          + _noise(x // 2, y, 179) * 0.4)
            idx = _quantize(lit, 4, x, y)
            c = WOOD[idx]
            if ly >= SIZE / 4.0 - 2:
                c = _shade(c, -0.34)
            _px(img, x, y, c)
    # 中央漏斗
    cx = cy = SIZE / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            dx = (x + 0.5 - cx) / (3.2 * U)
            dy = (y + 0.5 - cy) / (3.2 * U)
            d = math.hypot(dx, dy)
            if d <= 1.0:
                lit = 0.30 + 0.30 * d
                idx = _quantize(lit, 4, x, y)
                _px(img, x, y, IRON[idx])
    for (x, y) in _disc(cx, cy, 3.4 * U):
        dx, dy = (x + 0.5 - cx) / (3.4 * U), (y + 0.5 - cy) / (3.4 * U)
        if 0.92 < math.hypot(dx, dy):
            _px(img, x, y, IRON[3])
    return img


def grain_sheller_side():
    """脱壳机侧面：木板 + 一条铁箍 + 四角铆钉。"""
    img = _opaque()
    for y in range(SIZE):
        for x in range(SIZE):
            v = 0.52 + 0.30 * (1.0 - (y + 0.5) / SIZE) \
                + 0.28 * (_noise(x % 13, y, 523) * 0.6 + _noise(x // 2, y, 541) * 0.4)
            idx = _quantize(v, 4, x, y)
            c = WOOD[idx]
            if 6.0 * U <= y < 9.0 * U:
                iv = 0.5 + 0.5 * _noise(x, y, 557)
                c = IRON[_quantize(iv, 4, x, y)]
            elif y > 15.2 * U:
                c = _shade(c, -0.28)
            elif y < 0.8 * U:
                c = _shade(c, 0.12)
            _px(img, x, y, c)
    # 角铆钉
    for (rx, ry) in ((1.4, 1.4), (14.6, 1.4), (1.4, 14.6), (14.6, 14.6)):
        for (x, y) in _disc(rx * U, ry * U, 0.7 * U):
            _px(img, x, y, IRON[3])
    return img


def _item_from_block(top, side=None):
    """把方块顶面当图标，加上右下投影，做出"物品"的感觉。"""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    # 一个斜面（俯视 + 一点厚度）
    inset = 1.2 * U
    body = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    body.paste(top.crop((int(inset), int(inset), SIZE - int(inset), SIZE - int(inset))),
               (int(inset), int(inset * 0.7)))
    # 侧面
    if side is not None:
        strip = side.crop((0, 0, SIZE, int(2.6 * U)))
        body.paste(strip.resize((SIZE - int(inset * 2), int(2.2 * U)), Image.NEAREST),
                   (int(inset), SIZE - int(inset * 1.2)))
    img.alpha_composite(body)
    # 右下投影
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    a = body.getchannel("A")
    sh = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 90))
    sh.putalpha(a.point(lambda v: int(v * 0.35)))
    shadow.alpha_composite(sh, (2, 3))
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.alpha_composite(shadow)
    out.alpha_composite(img)
    return out


def processor_gui():
    """装置界面底图：176x166，MC 风格的木/石面板 + 两个槽位 + 箭头。"""
    W, H = 176, 166
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    # 底板：上半是石板灰、下半是木色（分别对应机器区与背包区）
    for y in range(H):
        for x in range(W):
            if y < 76:
                base = (198, 198, 198)
                v = 0.9 + 0.1 * _noise(x // 2, y // 2, 701)
            else:
                base = (198, 198, 198)
                v = 0.86 + 0.14 * _noise(x // 2, y // 2, 709)
            if x < 3 or y < 3 or x >= W - 3 or y >= H - 3:
                base = (85, 85, 85)          # 外描边
            elif x < 5 or y < 5 or x >= W - 5 or y >= H - 5:
                base = (238, 238, 238)       # 内高光
            c = tuple(min(255, int(ch * v)) for ch in base)
            px[x, y] = c + (255,)

    # 槽位底：凹槽
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

    # 与 ProcessorMenu 里的槽位坐标一致（相对于 leftPos/topPos，
    # 需要减去 1，因为物品渲染在槽位左上角偏 1 像素）
    slot(56 - 1, 35 - 1)
    slot(116 - 1, 35 - 1)
    # 玩家背包 3x9 + 快捷栏 1x9
    for row in range(3):
        for col in range(9):
            slot(8 - 1 + col * 18, 84 - 1 + row * 18)
    for col in range(9):
        slot(8 - 1 + col * 18, 142 - 1)

    # 进度条槽（在底图下半部分：ARROW_Y + ARROW_HEIGHT 的位置）
    arrow_x, arrow_y, arrow_w, arrow_h = 79, 34, 24, 17
    for y in range(arrow_y, arrow_y + arrow_h):
        for x in range(arrow_x, arrow_x + arrow_w):
            px[x, y] = (120, 120, 120, 255)
    for x in range(arrow_x, arrow_x + arrow_w):
        px[x, arrow_y] = (60, 60, 60, 255)
    # 填充段（底图里预画成实心浅色，运行时只按比例裁切）
    for y in range(arrow_y + 1, arrow_y + arrow_h):
        for x in range(arrow_x + 1, arrow_x + arrow_w):
            px[x, y] = (232, 150, 60, 255)
    for y in range(arrow_y + 1, arrow_y + arrow_h - 1):
        for x in range(arrow_x + 1, arrow_x + arrow_w - 1):
            if (x + y) % 3 == 0:
                px[x, y] = (250, 186, 96, 255)

    return img


def grain_sheller_hopper_item():
    """料斗的物品图标：正对着看的一个铁皮漏斗（上宽下窄 + 顶圈）。"""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    def put(x, y, c, a=255):
        if 0 <= x < SIZE and 0 <= y < SIZE:
            img.putpixel((int(x), int(y)), (c[0], c[1], c[2], a))

    iron = ((92, 96, 104), (150, 154, 162))
    wood = ((128, 86, 46), (196, 148, 92))
    # 漏斗：逐行从宽到窄（每行画一条水平的铁皮边）
    top_y, bot_y = 3.0, 11.5
    top_hw, bot_hw = 6.6, 2.0
    for i in range(int((bot_y - top_y) * U)):
        t = i / max(1.0, (bot_y - top_y) * U - 1)
        y = top_y * U + i
        hw = (top_hw + (bot_hw - top_hw) * (t ** 1.25)) * U
        cx = 8.0 * U
        for x in range(int(cx - hw), int(cx + hw)):
            edge = min(x - (cx - hw), (cx + hw) - x)
            if edge < max(1.0, U * 0.55):
                c = iron[1] if (x + y) % 2 == 0 else iron[0]
            else:
                # 内壁：左侧暗、右侧亮，做出"能看进去"的深度
                inside = (x - (cx - hw)) / max(1.0, 2 * hw)
                c = _shade(iron[0], -0.30 + 0.35 * inside)
            put(x, y, c)
    # 顶圈（木框）
    for y in range(int(2.2 * U), int(3.2 * U)):
        for x in range(int(0.9 * U), int(15.1 * U)):
            put(x, y, wood[1] if y < 2.6 * U else wood[0])
    # 下口 + 出料小嘴
    for y in range(int(bot_y * U), int((bot_y + 2.4) * U)):
        for x in range(int(6.2 * U), int(9.8 * U)):
            put(x, y, iron[0] if (x + y) % 2 else iron[1])
    # 下口内圈（深色，表示是通的）
    for y in range(int((bot_y + 0.5) * U), int((bot_y + 2.0) * U)):
        for x in range(int(7.0 * U), int(9.0 * U)):
            put(x, y, _shade(iron[0], -0.45))
    return img


def dish_material_textures():
    """摆在地上的菜与器皿用到的 6 张共享材质。

    只有这几张材质 + 方块着色（BlockColor）就够表现所有菜 ——
    食物与汤汁两张是浅灰的"中性色"，进游戏后会被染成该道菜的配色。
    这和原版给树叶 / 草 / 药水上色是同一套机制。

    **为什么用低频噪声而不是白噪点**：模型是"一层层叠起来"的，
    如果每层都是高频噪点，叠起来会像一堆粗糙的颗粒；用低频（每 4~8 像素
    才变一次）的平滑渐变，叠层之间就能自然过渡，看起来是
    "光滑的釉面 / 打磨过的木头"，而不是噪点块。这也是原版瓷器、木板
    贴图的做法 —— 原版的"颗粒感"来自色阶本身，不是逐像素乱跳。
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dish_models as DM

    # 每种材质给一点"质感方向"：瓷器和食物是光滑的，木头要顺纹，陶土要哑光
    grain = {
        "dish_wood": "x",        # 木纹沿 X 方向
        "dish_clay": "d",        # 陶土：斜向的细颗粒
        "dish_porcelain": None,  # 瓷器：几乎纯净的平滑渐变
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
                    # 木纹 / 铁纹：横向拉长的丝，纵向缓慢变亮
                    a = _noise((x * 2) % (period * 2), y // 3, seed)
                    b = _noise(x // period, y // period, seed + 11)
                    v = 0.45 * a + 0.55 * b
                elif style == "d":
                    a = _noise(x // period, y // period, seed)
                    b = _noise((x + y) // (period * 2), (y - x) // (period * 2),
                               seed + 7)
                    v = 0.6 * a + 0.4 * b
                else:
                    # 光滑面：只有很缓的明暗起伏 + 极少的高光点
                    v = 0.5 + 0.5 * _noise(x // (period * 2), y // (period * 2),
                                           seed)
                    if _noise(x, y, seed + 31) > 0.965:
                        v = 1.0
                # 量化成 4 档 + 柏叶抖动，保住"像素画"的味道
                idx = _quantize(v, 4, x, y)
                img.putpixel((x, y), ramp[idx] + (255,))
        out.append((img, "block", name + ".png"))
    return out


def main(block_dir, item_dir, gui_dir):
    """写三处的贴图。目录直接给**绝对路径**，不要再拿字符串去比。

    这里曾经踩过坑：写成
    ``target = block_dir if directory == "block" else ...``，
    而调用方传进来的 ``block_dir`` 是路径、不是 ``"block"`` 字符串，
    于是一路掉到最后的分支，**所有机器贴图都被写进了 textures/gui/**。
    看着"命令跑成功了"，实际上 textures/block 里一直是旧文件，
    这种错误只有进游戏才发现。现在按 ``(图片, 目标目录, 文件名)`` 直接给定。
    """
    targets = [
        (water_mill_top(), block_dir, "water_mill.png"),
        (water_mill_side(), block_dir, "water_mill_side.png"),
        (grain_sheller_top(), block_dir, "grain_sheller.png"),
        (grain_sheller_side(), block_dir, "grain_sheller_side.png"),
        (_item_from_block(water_mill_top(), water_mill_side()), item_dir, "water_mill.png"),
        (_item_from_block(grain_sheller_top(), grain_sheller_side()), item_dir, "grain_sheller.png"),
        (grain_sheller_hopper_item(), item_dir, "grain_sheller_hopper.png"),
        (processor_gui(), gui_dir, "processor.png"),
    ]
    # dish_material_textures() 返回的第三个字段是 "block"，这里统一换成真实目录
    targets += [(img, block_dir, name) for (img, _kind, name) in dish_material_textures()]

    for img, target, name in targets:
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, name)
        img.save(path)
        print("wrote %-64s %dx%d" % (os.path.relpath(path), img.width, img.height))
