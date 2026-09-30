# -*- coding: utf-8 -*-
"""
生成《国风·传统食物》的 Minecraft 风格纹理（64x64）。

用法
----
    powershell -NoProfile -ExecutionPolicy Bypass -File tools/fetch_cc0_assets.ps1
    python tools/build_textures.py            # 默认 64x64
    python tools/build_textures.py --size 16  # 想要原版分辨率也能出图

设计规范：64x64 的 Minecraft 像素画
-----------------------------------
分辨率提到 64x64 之后，**风格仍然是 Minecraft**，靠的是守住这几条：

1. **硬边**：逐像素直接写，不做超采样、不做 LANCZOS、不做高斯模糊 ——
   任何抗锯齿都会让材质看起来"糊"，和原版方块放一起会很突兀。
2. **窄色板 + 抖动**：每种材质只用 6~8 档亮度，档与档之间用 **Bayer 4x4 有序抖动**
   过渡（这是像素画的经典手法），而不是连续渐变。
3. **逐像素颗粒**：木质、瓷釉、汤面都叠加确定性伪随机噪声，模拟 MC 贴图的"脏感"。
4. **不烘焙方向光**：方块贴图进游戏后会由引擎按面统一打光
   （顶面 1.0 / 南北 0.8 / 东西 0.6 / 底面 0.5）。所以顶面贴图只做"器皿自身的弧度明暗"，
   不叠全局的左上高光，否则进游戏会双重变暗。
5. **方块贴图可平铺**：木质拼盘的木纹左右上下自洽，连续摆一排不会出现硬接缝。
6. **物品图标**：透明背景，右下一圈压暗一档当体积感，和原版工具/食物图标一致。

配色来源
--------
木质托盘的木色不是拍脑袋定的，而是从下载到的 CC0 素材
（Kenney "Pixel Platformer Food Expansion"、OpenGameArt maruki / Luca Pixel 的
16x16 食物包）里用 HSV 筛出棕橙区间再按亮度分档得到的。
提取结果写在 tools/downloads/cc0_palette_report.txt，可复查。详见 ATTRIBUTION.md。
"""

import argparse
import colorsys
import math
import os
import sys
import zlib

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets",
                      "chinese_traditional_food", "textures")
BLOCK_DIR = os.path.join(ASSETS, "block")
ITEM_DIR = os.path.join(ASSETS, "item")
GUI_DIR = os.path.join(ASSETS, "gui")
DOWNLOADS = os.path.join(ROOT, "tools", "downloads")
EXTRACTED = os.path.join(DOWNLOADS, "extracted")

CC0_SHEETS = [
    os.path.join(EXTRACTED, "kenney_pixel-platformer-food-expansion", "Tilemap", "tilemap.png"),
    os.path.join(EXTRACTED, "oga_16x16px_food_items", "Foodies", "foodies_sheet.png"),
]

# 由 main() 依据 --size 设置
SIZE = 64
U = SIZE / 16.0      # 1 个"原版像素" = U 个本图像素；所有几何都用这个单位描述


# ======================================================================
# 基础工具：确定性噪声 + Bayer 抖动 + 量化
# ======================================================================

def hash_noise(x, y, seed):
    """确定性的 [0,1) 伪随机。同一坐标永远同一结果，保证可重复构建。"""
    n = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / float(0x1000000)


BAYER4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def bayer(x, y):
    """Bayer 4x4 有序抖动阈值，落在 [0,1)。像素画的"渐变"就靠它。"""
    return (BAYER4[y & 3][x & 3] + 0.5) / 16.0


def quantize(value, levels, x, y, ordered=True, seed=0):
    """把 0..1 的连续值量化成 levels 档。ordered=True 用 Bayer 抖动，否则用随机抖动。"""
    value = max(0.0, min(1.0, value))
    scaled = value * (levels - 1)
    base = int(scaled)
    frac = scaled - base
    threshold = bayer(x, y) if ordered else hash_noise(x, y, seed)
    if frac > threshold:
        base += 1
    return max(0, min(levels - 1, base))


def shade(colour, amount):
    """调亮(>0)或调暗(<0)，用于在窄色板之外做极小的明暗修正。"""
    if amount >= 0:
        return tuple(min(255, int(c + (255 - c) * amount + 0.5)) for c in colour[:3])
    return tuple(max(0, int(c * (1.0 + amount) + 0.5)) for c in colour[:3])


# ======================================================================
# 画布与基元（坐标一律用"原版像素"单位，内部乘 U）
# ======================================================================

def blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


def put(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def disc(cx, cy, radius):
    """返回半径内的像素坐标列表。cx/cy/radius 用原版像素单位。"""
    cx *= U
    cy *= U
    radius *= U
    r2 = radius * radius
    out = []
    limit = SIZE
    y0 = max(0, int(cy - radius - 1))
    y1 = min(limit, int(cy + radius + 2))
    x0 = max(0, int(cx - radius - 1))
    x1 = min(limit, int(cx + radius + 2))
    for y in range(y0, y1):
        dy = y + 0.5 - cy
        for x in range(x0, x1):
            dx = x + 0.5 - cx
            if dx * dx + dy * dy <= r2:
                out.append((x, y))
    return out


def annulus(cx, cy, r_inner, r_outer):
    outer = set(disc(cx, cy, r_outer))
    inner = set(disc(cx, cy, r_inner))
    return sorted(outer - inner)


def rect(x0, y0, x1, y1):
    """闭区间矩形，单位是原版像素。"""
    out = []
    for y in range(max(0, int(y0 * U)), min(SIZE, int(round(y1 * U)))):
        for x in range(max(0, int(x0 * U)), min(SIZE, int(round(x1 * U)))):
            out.append((x, y))
    return out


# ======================================================================
# 从 CC0 素材提取配色
# ======================================================================

WOOD_FALLBACK = [(120, 80, 44), (146, 100, 56), (170, 122, 70), (196, 148, 92)]


def extract_cc0_palette():
    """量化 CC0 素材，返回 (全部主色, 暖木色四档)，并写一份可复查的报告。

    木色不是直接拿素材里的某个颜色用（16x16 食物包里最多的是胡萝卜橙、
    面点淡褐，直接拿来会偏亮偏橙），而是：
      1) 用 HSV 从素材里筛出"棕橙"区间的候选色；
      2) 取这些候选色的**色相中位数**作为木材色相；
      3) 用受控的饱和度 / 明度生成四档亮度阶梯。
    这样既有据可依，又能保证四档颜色能直接当木材用。
    """
    all_colours = []
    for path in CC0_SHEETS:
        if not os.path.exists(path):
            continue
        img = Image.open(path).convert("RGBA")
        rgb = Image.new("RGB", img.size, (255, 0, 255))
        rgb.paste(img, mask=img.getchannel("A"))
        q = rgb.quantize(colors=32, method=Image.MEDIANCUT)
        pal = q.getpalette()
        for count, index in q.getcolors():
            r, g, b = pal[index * 3:index * 3 + 3]
            if (r, g, b) == (255, 0, 255):
                continue
            all_colours.append(((r, g, b), count))
    all_colours.sort(key=lambda t: -t[1])

    # 筛"棕橙"候选：色相 18~46 度，饱和度与明度都在中间偏暗的地带。
    # 红油(≈10 度) 与 奶油白(饱和度极低) 会被排除。
    warm = []
    for (r, g, b), _ in all_colours:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if not (18.0 <= h * 360.0 <= 46.0):
            continue
        if not (0.28 <= s <= 0.72):
            continue
        if not (0.30 <= v <= 0.82):
            continue
        warm.append((r, g, b))

    hues = sorted(colorsys.rgb_to_hsv(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)[0]
                  for c in warm)
    if hues:
        mid_hue = hues[len(hues) // 2]
    else:
        # 素材缺失时的兜底色相：约 30 度
        mid_hue = 30.0 / 360.0
    sat = 0.46 if warm else 0.44

    wood = []
    for value in (0.34, 0.46, 0.58, 0.70):
        r, g, b = colorsys.hsv_to_rgb(mid_hue, sat, value)
        wood.append((int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)))

    os.makedirs(DOWNLOADS, exist_ok=True)
    report = os.path.join(DOWNLOADS, "cc0_palette_report.txt")
    with open(report, "w", encoding="utf-8") as fh:
        fh.write("CC0 素材配色提取报告\n")
        fh.write("=====================\n\n")
        fh.write("来源素材:\n")
        for p in CC0_SHEETS:
            fh.write("  - %s  (%s)\n" % (os.path.relpath(p, ROOT),
                                          "存在" if os.path.exists(p) else "缺失"))
        fh.write("\n全部主色（按出现像素数排序，最多 40 个）:\n")
        for (r, g, b), count in all_colours[:40]:
            fh.write("  #%02X%02X%02X  %8d px\n" % (r, g, b, count))
        fh.write("\n通过 HSV 筛选得到的棕橙候选（暗 -> 亮）:\n")
        for (r, g, b) in warm:
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            fh.write("  #%02X%02X%02X  H=%5.1f S=%.2f V=%.2f\n"
                     % (r, g, b, h * 360.0, s, v))
        fh.write("\n色相中位数 = %.1f 度，饱和度取 %.2f\n" % (mid_hue * 360.0, sat))
        fh.write("\n最终四档木色（暗 -> 亮）:\n")
        for (r, g, b) in wood:
            fh.write("  #%02X%02X%02X\n" % (r, g, b))
    print("palette report ->", os.path.relpath(report, ROOT))
    return all_colours, wood


# ======================================================================
# 色板
# ======================================================================

# 青花瓷釉：8 档，从盘沿暗部到高光
PORCELAIN = [
    (146, 152, 166),
    (164, 170, 182),
    (182, 188, 200),
    (200, 206, 216),
    (216, 222, 230),
    (230, 235, 242),
    (242, 246, 250),
    (250, 252, 255),
]
# 青花钴蓝：4 档
COBALT = [
    (20, 34, 74),
    (32, 58, 116),
    (46, 82, 152),
    (66, 106, 186),
]
# 砂锅 / 铁器
IRONWARE = [
    (30, 32, 38),
    (44, 47, 54),
    (60, 64, 72),
    (80, 84, 94),
    (104, 108, 118),
    (132, 136, 146),
]
# 红油（麻婆豆腐）：深红棕 -> 亮橙红，整体压得比"番茄酱"更暗更沉
SAUCE = [
    (78, 24, 14),
    (98, 30, 16),
    (118, 38, 20),
    (138, 48, 24),
    (158, 60, 28),
    (176, 74, 32),
    (192, 92, 38),
]
# 豆腐
TOFU = [
    (168, 164, 148),
    (196, 192, 176),
    (216, 212, 196),
    (232, 229, 216),
    (243, 241, 230),
    (250, 249, 241),
    (253, 252, 247),
]
SCALLION = [(74, 118, 48), (96, 148, 60), (118, 172, 74), (142, 194, 92)]
PEPPERCORN = [(46, 28, 18), (66, 42, 26)]


# ======================================================================
# 1. 青花瓷盘 —— 方块顶面
# ======================================================================

PLATE_RADIUS = 7.62      # 原版像素单位（16 格坐标系中的半径）


def plate_porcelain_colour(x, y, cx, cy, radius, with_outline):
    """器皿自身的弧度明暗（不含全局方向光）。"""
    dx = (x + 0.5 - cx) / radius
    dy = (y + 0.5 - cy) / radius
    dist = min(1.0, (dx * dx + dy * dy) ** 0.5)

    # 盘心略亮，靠外因弧度而暗
    lit = 0.86 - 0.34 * (dist ** 2.6)
    # 盘沿内侧的凹槽
    if 0.795 < dist < 0.905:
        lit -= 0.155
    # 最外一圈再压一点，形成收边
    if dist > 0.955:
        lit -= 0.11
    # 釉面的细微颗粒
    lit += (hash_noise(x, y, 17) - 0.5) * 0.075

    idx = quantize(lit, len(PORCELAIN), x, y, ordered=True)
    c = PORCELAIN[idx]

    if with_outline:
        # 物品图标：右下弧压一档，做出体积感
        if (dx + dy) > 0.45 and dist > 0.60:
            c = shade(c, -0.13)
    return c


def draw_plate_top(with_outline=False):
    img = blank()
    cx = cy = SIZE / 2.0
    radius = PLATE_RADIUS * U

    for (x, y) in disc(8.0, 8.0, PLATE_RADIUS):
        put(img, x, y, plate_porcelain_colour(x, y, cx, cy, radius, with_outline))

    # --- 青花：外沿双线 ---
    for (x, y) in annulus(8.0, 8.0, 6.72, 7.10):
        put(img, x, y, COBALT[2])
    for (x, y) in annulus(8.0, 8.0, 6.34, 6.52):
        put(img, x, y, COBALT[1])

    # --- 青花：一圈连续的"回纹/蔓草"点饰 ---
    for i in range(24):
        a = i * (math.tau / 24.0)
        px_ = 8.0 + math.cos(a) * 5.55
        py_ = 8.0 + math.sin(a) * 5.55
        for (x, y) in disc(px_, py_, 0.30):
            put(img, x, y, COBALT[1] if i % 2 == 0 else COBALT[0])

    # --- 青花：内圈细线 ---
    for (x, y) in annulus(8.0, 8.0, 3.42, 3.62):
        put(img, x, y, COBALT[1])

    # --- 青花：八瓣缠枝花 ---
    for (x, y) in disc(8.0, 8.0, 1.05):
        put(img, x, y, COBALT[1])
    for i in range(8):
        a = i * (math.tau / 8.0)
        px_ = 8.0 + math.cos(a) * 2.30
        py_ = 8.0 + math.sin(a) * 2.30
        for (x, y) in disc(px_, py_, 0.62):
            put(img, x, y, COBALT[2])
        # 花瓣外的小叶
        px2 = 8.0 + math.cos(a) * 3.02
        py2 = 8.0 + math.sin(a) * 3.02
        for (x, y) in disc(px2, py2, 0.26):
            put(img, x, y, COBALT[0])

    return img


# ======================================================================
# 2. 青花瓷盘 —— 方块侧面
# ======================================================================

def draw_plate_side():
    img = opaque()
    for y in range(SIZE):
        v = (y + 0.5) / SIZE
        # 瓷釉从上到下变暗（器皿自身的过渡，不是全局光照）
        lit = 0.92 - 0.70 * (v ** 1.12)
        for x in range(SIZE):
            idx = quantize(lit, len(PORCELAIN), x, y, ordered=True)
            c = PORCELAIN[idx]

            # 釉面的竖向细纹
            c = shade(c, ((hash_noise(x, y, 59) - 0.5) * 0.06))

            # 圈足：底部一条青花粗线 + 一条细线（各约 1~2 像素，别做成整条蓝色带）
            yy = v * 16.0
            if 11.55 <= yy < 11.95:
                c = COBALT[2]
            elif 12.30 <= yy < 12.55:
                c = COBALT[1]
            elif yy >= 14.7:
                c = shade(c, -0.20)      # 底沿落影
            elif yy < 0.5:
                c = shade(c, 0.10)       # 顶沿高光

            put(img, x, y, c)
    return img


# ======================================================================
# 3. 木质拼盘 —— 方块（可平铺）
# ======================================================================

def wood_grain(x, y, seed, period):
    """沿 X 方向伸展的木纹，用整数除法保证左右可平铺、上下不接缝。"""
    return hash_noise(x % period, y, seed) * 0.6 + hash_noise(x // 2, y, seed + 7) * 0.4


def draw_platter_block(wood):
    """wood: 四档，[0] 最暗 ~ [3] 最亮。木板横向四条，纹理可平铺。"""
    img = opaque()
    plank_h = SIZE / 4.0
    for y in range(SIZE):
        for x in range(SIZE):
            plank = int(y / plank_h)
            ly = y - plank * plank_h
            # 板内上下：上略亮下略暗
            local = 1.0 - (ly / plank_h)
            grain = wood_grain(x, y, 101 + plank * 31, 9)
            lit = 0.42 + 0.36 * local + 0.30 * grain
            idx = quantize(lit, 4, x, y, ordered=True)
            c = wood[idx]

            # 板缝（每块板的底边）：暗线 + 下一行高光
            if ly >= plank_h - 2:
                c = shade(c, -0.34)
            elif ly >= plank_h - 3:
                c = shade(c, 0.12)

            # 个别年轮结点，让木纹不那么均匀
            if hash_noise(x // 6, plank, 909) < 0.30 and abs(ly - plank_h * 0.42) < 1.5:
                c = shade(c, -0.13)

            # 四边矮沿：外一圈压暗，内一圈轻描
            if x == 0 or y == 0 or x == SIZE - 1 or y == SIZE - 1:
                c = shade(wood[0], -0.20)
            elif x < int(1 * U) or y < int(1 * U) \
                    or x >= SIZE - int(1 * U) or y >= SIZE - int(1 * U):
                c = shade(c, -0.17)
            elif x < int(1.6 * U) or y < int(1.6 * U) \
                    or x >= SIZE - int(1.6 * U) or y >= SIZE - int(1.6 * U):
                c = shade(c, 0.12)

            put(img, x, y, c)
    return img


# ======================================================================
# 4. 木质拼盘 —— 物品图标（俯视 + 四份菜）
# ======================================================================

DISH_TINTS = [
    (176, 62, 38),     # 红油菜
    (240, 236, 220),   # 白豆腐
    (96, 148, 66),     # 青菜
    (150, 92, 46),     # 红烧肉
]


def draw_platter_item(wood):
    img = blank()

    # --- 托盘主体：1..15 格，圆角 1 格 ---
    tiles = rect(1.0, 1.6, 15.0, 14.4)
    corner = int(1.2 * U)
    for (x, y) in tiles:
        # 圆角：切掉靠近四角的三角区
        for (ox, oy, sx, sy) in ((1.0, 1.6, 1, 1), (15.0, 1.6, -1, 1),
                                 (1.0, 14.4, 1, -1), (15.0, 14.4, -1, -1)):
            cx_ = ox * U
            cy_ = oy * U
            if (x - cx_) * sx + (y - cy_) * sy < -corner * 1.42:
                break
        else:
            lit = 0.50 + 0.32 * (1.0 - (y / SIZE)) + 0.22 * wood_grain(x, y, 613, 11)
            idx = quantize(lit, 4, x, y, ordered=True)
            c = wood[idx]

            # 十字分隔：暗示四个格子
            mid = SIZE / 2.0
            if abs(x - mid) < U * 0.5 or abs(y - mid) < U * 0.5:
                c = shade(c, -0.20)
            # 外沿
            if x < int(1.9 * U) or x >= SIZE - int(1.9 * U) \
                    or y < int(2.4 * U) or y >= SIZE - int(2.4 * U):
                c = shade(wood[0], -0.12)
            put(img, x, y, c, 255)

    # --- 四份菜 ---
    centres = [(4.5, 4.9), (11.5, 4.9), (4.5, 11.1), (11.5, 11.1)]
    for (ox, oy), tint in zip(centres, DISH_TINTS):
        for (x, y) in disc(ox, oy, 2.55):
            dx = (x + 0.5 - ox * U) / (2.55 * U)
            dy = (y + 0.5 - oy * U) / (2.55 * U)
            dist = min(1.0, (dx * dx + dy * dy) ** 0.5)
            lit = 0.92 - 0.55 * (dist ** 2.2) + (hash_noise(x, y, 1301) - 0.5) * 0.10
            idx = quantize(lit, 5, x, y, ordered=True)
            base = tuple(max(0, min(255, int(ch * (0.55 + 0.55 * idx / 4.0)))) for ch in tint)
            put(img, x, y, base, 255)
        # 一点点葱花 / 高光，避免四份菜太同质
        for (x, y) in disc(ox - 0.9, oy - 0.9, 0.42):
            put(img, x, y, shade(tint, 0.42), 255)
    return img


# ======================================================================
# 5. 豆腐 —— 物品图标
# ======================================================================

TOFU_TOP_TONE = (253, 252, 247)
TOFU_MID_TONE = (238, 235, 224)
TOFU_DARK_TONE = (206, 202, 186)
TOFU_EDGE_TONE = (162, 158, 142)


def draw_tofu():
    """三块豆腐，3/4 视角：顶面最亮、左面次之、右面最暗，最后勾一圈边。"""
    img = blank()
    cubes = [
        (1.2, 3.6, 5.8, 5.2),
        (8.6, 2.8, 5.8, 5.2),
        (4.2, 8.4, 7.6, 6.0),
    ]
    for (bx, by, bw, bh) in cubes:
        x0 = int(round(bx * U))
        y0 = int(round(by * U))
        w = int(round(bw * U))
        h = int(round(bh * U))
        top_h = max(2, int(round(h * 0.30)))

        for yy in range(y0, min(SIZE, y0 + h)):
            for xx in range(x0, min(SIZE, x0 + w)):
                if yy - y0 < top_h:
                    # 顶面：整体最亮，靠后有极轻微的渐变
                    t = (yy - y0) / float(top_h)
                    base = TOFU_TOP_TONE if t < 0.6 else TOFU_MID_TONE
                elif (xx - x0) < w * 0.42:
                    base = TOFU_MID_TONE
                else:
                    base = TOFU_DARK_TONE
                # 豆腐表面的细微孔洞感
                if hash_noise(xx, yy, 71) < 0.16:
                    base = shade(base, -0.06)
                put(img, xx, yy, base, 255)

        # 顶面与侧面的分界线
        for xx in range(x0, min(SIZE, x0 + w)):
            put(img, xx, min(SIZE - 1, y0 + top_h - 1), shade(TOFU_EDGE_TONE, 0.24), 255)
        # 左 / 右面的立体分界
        split = x0 + int(round(w * 0.42))
        for yy in range(y0 + top_h, min(SIZE, y0 + h)):
            put(img, split, yy, shade(TOFU_MID_TONE, -0.10), 255)
        # 外描边
        for xx in range(x0, min(SIZE, x0 + w)):
            put(img, xx, y0, shade(TOFU_TOP_TONE, 0.0), 255)
            put(img, xx, min(SIZE - 1, y0 + h - 1), TOFU_EDGE_TONE, 255)
        for yy in range(y0, min(SIZE, y0 + h)):
            put(img, x0, yy, TOFU_EDGE_TONE, 255)
            put(img, min(SIZE - 1, x0 + w - 1), yy, TOFU_EDGE_TONE, 255)
    return img


# ======================================================================
# 6. 麻婆豆腐 —— 物品图标（砂锅 + 红油 + 豆腐丁 + 葱花 + 花椒）
# ======================================================================

def draw_mapo_tofu():
    img = blank()
    cx = cy = 8.0
    bowl_r = 7.80
    soup_r = 5.60      # 汤面比锅口小一圈，留出可见的深色锅壁

    # --- 砂锅 ---
    for (x, y) in disc(cx, cy, bowl_r):
        dx = (x + 0.5 - cx * U) / (bowl_r * U)
        dy = (y + 0.5 - cy * U) / (bowl_r * U)
        dist = min(1.0, (dx * dx + dy * dy) ** 0.5)
        # 锅壁：外圈暗、内圈稍亮；再叠一点器皿弧度
        lit = 0.50 - 0.40 * (dist ** 1.4) - 0.08 * (dx + dy)
        lit += (hash_noise(x, y, 907) - 0.5) * 0.08
        idx = quantize(lit, len(IRONWARE), x, y, ordered=True)
        c = IRONWARE[idx]
        # 锅沿的一线高光（不能太亮，否则砂锅会变成不锈钢）
        if 0.88 < dist < 0.96:
            c = shade(c, 0.16)
        # 最外一圈压暗，勾出锅的轮廓
        if dist > 0.965:
            c = shade(c, -0.30)
        put(img, x, y, c, 255)

    # --- 红油汤面 ---
    for (x, y) in disc(cx, cy, soup_r):
        dx = (x + 0.5 - cx * U) / (soup_r * U)
        dy = (y + 0.5 - cy * U) / (soup_r * U)
        dist = min(1.0, (dx * dx + dy * dy) ** 0.5)
        # 两团油光
        d1 = (((x + 0.5 - 6.0 * U) ** 2 + (y + 0.5 - 5.5 * U) ** 2) ** 0.5) / U
        d2 = (((x + 0.5 - 10.1 * U) ** 2 + (y + 0.5 - 10.0 * U) ** 2) ** 0.5) / U
        lit = 0.46 + 0.24 * hash_noise(x // 2, y, 1103)
        if d1 < 2.6:
            lit += 0.44 * (1.0 - d1 / 2.6) ** 1.5
        if d2 < 1.8:
            lit += 0.28 * (1.0 - d2 / 1.8) ** 1.5
        lit -= 0.26 * (dist ** 3)          # 靠锅壁变暗
        idx = quantize(lit, len(SAUCE), x, y, ordered=True)
        put(img, x, y, SAUCE[idx], 255)

    # --- 豆腐丁（切成小方，带顶面高光） ---
    cubes = [
        (3.5, 3.4, 2.7, 2.5), (8.9, 4.3, 2.7, 2.5), (4.4, 8.8, 2.7, 2.5),
        (10.4, 8.9, 2.2, 2.1), (7.7, 7.3, 2.2, 2.1), (5.9, 5.6, 2.0, 1.9),
    ]
    for (bx, by, bw, bh) in cubes:
        x0 = int(round(bx * U))
        y0 = int(round(by * U))
        w = int(round(bw * U))
        h = int(round(bh * U))
        for yy in range(y0, min(SIZE, y0 + h)):
            for xx in range(x0, min(SIZE, x0 + w)):
                ty = (yy - y0) / float(max(1, h))
                lit = 0.94 - 0.42 * ty + (hash_noise(xx, yy, 1319) - 0.5) * 0.06
                idx = quantize(lit, len(TOFU), xx, yy, ordered=True)
                put(img, xx, yy, TOFU[idx], 255)
        for xx in range(x0, min(SIZE, x0 + w)):
            put(img, xx, min(SIZE - 1, y0 + h - 1), TOFU[0], 255)
        for yy in range(y0, min(SIZE, y0 + h)):
            put(img, min(SIZE - 1, x0 + w - 1), yy, TOFU[1], 255)

    # --- 葱花（小段） ---
    scallions = [(2.4, 6.2, 0), (6.6, 2.6, 1), (12.0, 6.4, 0), (6.2, 12.2, 1),
                 (11.4, 11.5, 0), (8.6, 6.6, 1), (3.2, 10.4, 0), (9.6, 12.0, 1)]
    for (sx, sy, rot) in scallions:
        for i in range(3):
            x_ = int(round((sx + (i * 0.55 if rot == 0 else 0)) * U))
            y_ = int(round((sy + (0 if rot == 0 else i * 0.55)) * U))
            put(img, x_, y_, SCALLION[2], 255)
            put(img, x_ + 1, y_, SCALLION[1], 255)
            if i == 0:
                put(img, x_, y_ + 1, SCALLION[0], 255)

    # --- 花椒 ---
    for (px_, py_) in [(4.9, 6.1), (9.8, 3.6), (9.2, 12.3), (12.3, 8.6), (7.4, 10.3)]:
        x_ = int(round(px_ * U))
        y_ = int(round(py_ * U))
        put(img, x_, y_, PEPPERCORN[0], 255)
        put(img, x_ + 1, y_, PEPPERCORN[1], 255)
        put(img, x_, y_ + 1, PEPPERCORN[1], 255)
    return img


# ======================================================================
def save(img, directory, name):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    img.save(path)
    return path


def main():
    global SIZE, U
    parser = argparse.ArgumentParser(description="生成 Minecraft 风格纹理")
    parser.add_argument("--size", type=int, default=16,
                        help="纹理边长，默认 16（原版分辨率）；最大 64")
    parser.add_argument("--only",
                        choices=["displays", "content", "utilities", "machines", "all"],
                        default="all",
                        help="只生成器皿 / 只生成内容图标 / 只生成工具方块 / 只生成机器与界面 / 全部")
    args = parser.parse_args()

    # 必须拦住离谱的 --size：所有画法都是**逐像素**的 Python 循环，
    # 单张图的耗时大致与边长平方成正比，而且每种图标要画好几遍。
    # 传个 512 的话就是 16 倍的像素量 x 222 个图标 —— 机器会直接假死，
    # 而 Minecraft 本身也只接受 2 的幂的方形贴图，所以 16~64 完全够用。
    if args.size < 16 or args.size > 64 or (args.size & (args.size - 1)) != 0:
        parser.error("--size 必须是 16~64 之间的 2 的幂（原版是 16；64 已是像素画的极限）")

    SIZE = args.size
    U = SIZE / 16.0

    # 内容图标由 texture_icons 绘制（与 content_data 一一对应）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import content_data as DATA
    import texture_icons as ICONS
    ICONS.bind(hash_noise, bayer, quantize, shade)
    ICONS.set_size(SIZE)
    # 农作物（蔬菜 / 谷物 / 豆 / 种子）另有一套精细画法，固定 64x64
    import crop_icons
    ICONS.bind_crops(crop_icons)
    print("icon size = %d（农作物 %d 种用 64x64）" % (SIZE, len(ICONS.FINE_KINDS)))

    _, wood = extract_cc0_palette()
    if not wood or len(wood) < 4:
        wood = WOOD_FALLBACK
    print("size =", SIZE, " wood palette:",
          " ".join("#%02X%02X%02X" % c for c in wood))

    if args.only in ("displays", "all"):
        for img, directory, name in (
            (draw_plate_top(with_outline=False), BLOCK_DIR, "plate.png"),
            (draw_plate_side(), BLOCK_DIR, "plate_side.png"),
            (draw_platter_block(wood), BLOCK_DIR, "serving_platter.png"),
            (draw_plate_top(with_outline=True), ITEM_DIR, "plate.png"),
            (draw_platter_item(wood), ITEM_DIR, "serving_platter.png"),
        ):
            print("wrote %-52s %dx%d" % (os.path.relpath(save(img, directory, name), ROOT),
                                         img.width, img.height))

    if args.only in ("utilities", "all"):
        import texture_utilities as UTIL
        UTIL.bind(hash_noise, bayer, quantize, shade)
        UTIL.set_size(SIZE)
        UTIL.main(BLOCK_DIR, ITEM_DIR)

    if args.only in ("machines", "all"):
        import texture_machines as MACH
        MACH.bind(hash_noise, bayer, quantize, shade)
        MACH.set_size(SIZE)
        MACH.main(BLOCK_DIR, ITEM_DIR, GUI_DIR)

    if args.only in ("content", "all"):
        # 收集 content_data 里所有需要图标的条目
        entries = []
        for row in DATA.INGREDIENTS:
            entries.append((row[0], row[3], row[4]))
        for row in DATA.SEEDS:
            entries.append((row[0], row[3], row[4]))
        for row in DATA.SEASONINGS:
            entries.append((row[0], row[3], row[4]))
        for row in DATA.FRUITS:
            entries.append((row[0], row[3], row[4]))
        for row in DATA.VEGETABLES:
            entries.append((row[0], row[3], row[4]))
        for row in DATA.TOOLS:
            entries.append((row[0], row[3], row[4]))
        for row in DATA.DISHES:
            entries.append((row[0], row[4], row[5]))

        missing_kinds = set()
        missing_palettes = set()
        count = 0
        for (item_id, kind, palette_name) in entries:
            if kind not in ICONS.PAINTERS:
                missing_kinds.add(kind)
                continue
            if palette_name not in DATA.PALETTES:
                missing_palettes.add(palette_name)
                continue
            palette = DATA.PALETTES[palette_name]
            # 用 CRC32 而不是 Python 的 hash()：后者对字符串带进程级随机盐，
            # 每次运行结果都不同，会导致纹理“不可复现”、diff 噪声很大。
            seed = zlib.crc32(item_id.encode("utf-8")) & 0x7FFFFFFF
            if seed == 0:
                seed = 1
            img = ICONS.draw(kind, palette, seed)
            save(img, ITEM_DIR, "%s.png" % item_id)
            count += 1
            # 打印进度：逐像素画法本来就慢（64x64 的农作物更慢），
            # 没有进度输出时很容易被误当成"卡死了"，进而把进程一起杀掉。
            if count % 20 == 0:
                print("  ... %d/%d" % (count, len(entries)), flush=True)

        print("content icons: %d" % count)
        if missing_kinds:
            print("!! 缺少画法的图标种类: %s" % ", ".join(sorted(missing_kinds)))
        if missing_palettes:
            print("!! 未定义的配色: %s" % ", ".join(sorted(missing_palettes)))


if __name__ == "__main__":
    main()
