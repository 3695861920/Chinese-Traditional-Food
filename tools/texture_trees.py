# -*- coding: utf-8 -*-
"""果树贴图：树苗 / 树叶 / 木制品。**完全程序化生成。**

    （被 tools/build_textures.py 调用，`--only trees`）

配色**不在这里**，全部读 {@code content_data.TREE_LEAF_LOOK} 与
{@code TREE_WOOD_LOOK} —— 想调某棵树的颜色，改那张表，不要来改这个文件。

几套画法
--------

**树苗** 一根短茎 + 两片对生叶 + 顶芽。茎要短而粗（树苗是一截嫩枝，
不是小树），两片叶朝上斜举 —— 这是"苗"最直观的标志。

**树叶（方块）** 照原版分寸：镂空约三成、**不用半透明**、
只有 4 档明度。但**每棵树的叶色/跨度/镂空率/叶簇大小都不同**，
柑橘柿柚这类革质叶再加几点高光。

**树叶（物品图标）** 另画一张**实心**的：一簇三片叶 + 短柄。
方块贴图有洞，直接当图标会在物品栏里变成一块打满孔的绿。

**木制品** 侧面竖纹树皮 / 断面年轮 / 去皮细木纹 / 错缝横板。13 种树
各一套五色，摆一排就是 13 种颜色的木头。

> 注意：这里**不用任何现成素材** —— 早先版本借过 Kenney 的幼苗图，
> 现在全部由代码算出来（见 CREDITS.md）。
"""

import math
import os

from PIL import Image

SIZE = 16

_shade = None
_noise = None


def bind(noise, _bayer, _quantize, shade):
    global _noise, _shade
    _noise, _shade = noise, shade


def _canvas():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), tuple(colour[:3]) + (alpha,))


def _blend(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t + 0.5) for i in range(3))


def _ramp(base, steps=4):
    out = []
    for i in range(steps):
        t = (i / (steps - 1.0)) * 1.7 - 0.85
        out.append(tuple(max(0, min(255, int(c * (1.0 + t * 0.30) + 0.5)))
                         for c in base))
    return out


def _seed(name):
    import zlib
    return zlib.crc32(name.encode("utf-8")) & 0x7FFF or 1


# ======================================================================
# 每棵树长什么样（叶色 / 木色）—— 从 content_data 里读，这里不留副本
# ======================================================================

def _tree_data():
    """惰性导入 content_data（避免 build_textures 的导入顺序问题）。"""
    import content_data as DATA
    return DATA


def leaf_look(fruit):
    """取这棵树的树叶参数；表里没有就退回一个中庸值。"""
    return _tree_data().TREE_LEAF_LOOK.get(
        fruit, ((96, 150, 68), 2.4, 0.32, 4, False))


def wood_look(fruit):
    """取这棵树的木头五色（树皮暗/主/亮、去皮、木板）。"""
    look = _tree_data().TREE_WOOD_LOOK.get(fruit)
    if look is None:
        look = ((74, 56, 40), (108, 82, 56), (140, 110, 78),
                (188, 158, 116), (178, 148, 108))
    return look


def _leaf_ramp(base, spread):
    """4 档叶色。档距比 `_ramp` 宽，而且**由每棵树自己的跨度决定** ——
    枣树亮而花（spread 2.6），柑橘深而平（spread 2.2）。"""
    out = []
    for i in range(4):
        t = (i / 3.0 - 0.5) * 0.62 * (spread / 2.4)
        out.append(tuple(max(0, min(255, int(c * (1.0 + t) + 0.5)))
                         for c in base))
    return out


def leaf_shape(fruit):
    """取这棵树的叶形参数（叶形 / 排列 / 片数 / 宽长比 / 特征）。"""
    return _tree_data().TREE_LEAF_SHAPE.get(
        fruit, ("elliptic", "alternate", 3, 0.36, ()))


def tree_size(fruit):
    """这棵树的树形档次（0 小 / 1 中 / 2 大）—— 决定树苗画多高。"""
    for (fid, size) in _tree_data().TREE_FRUITS:
        if fid == fruit:
            return size
    return 1


def _blade_width(s, form):
    """叶片的宽度剖面：``s`` 是 0（叶基）到 1（叶尖），返回 0~1 的宽度。

    两头都得收到 0（不然叶子没有尖），中间最宽；**最宽处的位置**
    由 {@code TREE_LEAF_FORM} 的两个指数决定：

        w(s) = s^a · (1−s)^b      再归一化到峰值 = 1

    ``a`` 小 → 叶基就宽（卵形）；``b`` 小 → 前端宽（倒卵形）；
    两个相等 → 对称（披针形偏尖、椭圆形偏圆，靠指数的绝对值区分）。
    """
    a, b = _tree_data().TREE_LEAF_FORM[form]
    raw = (s ** a) * ((1.0 - s) ** b)
    peak = ((a / (a + b)) ** a) * ((b / (a + b)) ** b)
    return (raw / peak) if peak > 1e-9 else 0.0


def _twig_colour(fruit):
    """幼枝的颜色：取**这棵树自己的树皮主色**再提亮一档。

    树苗的茎和树叶图标的叶轴都用它 —— 于是枣苗的茎是深红褐、
    柚子苗的茎是黄绿，和那棵树的木头（`TREE_WOOD_LOOK`）是同一套色。
    幼枝本来就比老皮浅，所以整体提亮。
    """
    _dark, bark_main, _light, _stripped, _planks = wood_look(fruit)
    return _shade(bark_main, 0.22)


def _draw_blade(img, bx, by, angle, length, ratio, form, cols,
                traits=(), vein=True):
    """画一片**有学名的叶子**。

    参数
    ----
    ``bx, by``   叶基（叶柄连着茎的那一头）
    ``angle``    叶轴方向（图像坐标，y 向下；-90° 是正上方）
    ``length``   叶长（像素）
    ``ratio``    宽长比（半宽 = length × ratio / 2 时的 1.0 归一化）
    ``form``     叶形（见 `content_data.TREE_LEAF_FORM`）
    ``cols``     (暗轮廓, 主色, 亮色) 三档
    ``traits``   基部三出脉 / 叶柄翼 / 尾尖

    画法：先算出哪些像素在叶片内（含一个"内圈"集合用于找轮廓），
    再按"轮廓→叶脉→受光面"的顺序上色。轮廓是**每片叶子自己的**，
    所以三片叠在一起时后画的那片会把前一片切开，层次自然出来。
    """
    dark, main_c, light_c = cols
    ax, ay = math.cos(angle), math.sin(angle)
    nx, ny = -ay, ax
    half = max(1.0, length * ratio * 0.5)

    cells = []
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x + 0.5 - bx, y + 0.5 - by
            s = (dx * ax + dy * ay) / length
            if not (0.0 <= s < 1.0):
                continue
            v = (dx * nx + dy * ny) / half
            if abs(v) <= _blade_width(s, form):
                cells.append((x, y, s, v))
    if not cells:
        return []

    inner = {(c[0], c[1]) for c in cells}
    for (x, y, s, v) in cells:
        border = any((x + ddx, y + ddy) not in inner
                     for (ddx, ddy) in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if border:
            _px(img, x, y, dark)
        elif vein and abs(v) < 0.16 and 0.14 < s < 0.86:
            _px(img, x, y, dark)                     # 中脉
        elif "three_vein" in traits and 0.04 < s < 0.30 and abs(v) > 0.24:
            _px(img, x, y, dark)                     # 基部三出脉
        else:
            _px(img, x, y, main_c)

    # 受光面：中脉一侧偏下的那条带
    for (x, y, s, v) in cells:
        if 0.10 < s < 0.66 and 0.20 < v < 0.74 * max(0.2, _blade_width(s, form)):
            _px(img, x, y, light_c)

    # 尾尖：在叶尖再拖一个像素出去（热带植物的"滴水尖"）
    if "drip_tip" in traits:
        tx = bx + ax * (length + 0.9)
        ty = by + ay * (length + 0.9)
        _px(img, int(tx), int(ty), dark)
    return cells


def _petiole(img, bx, by, angle, colour, wing=False):
    """叶柄：从叶基往回连到茎上的一小截；柑橘类再加一个翼叶。"""
    ax, ay = math.cos(angle), math.sin(angle)
    for k in (1, 2):
        _px(img, int(bx - ax * k), int(by - ay * k), colour)
    if wing:
        # 翼叶：叶柄两侧各鼓一小块，柑橘/柚的标志
        wx = int(bx - ax * 2.2)
        wy = int(by - ay * 2.2)
        _px(img, wx + 1, wy, colour)
        _px(img, wx, wy + 1, colour)
        _px(img, wx - 1, wy, colour)


# ======================================================================
# 树苗
# ======================================================================

def sapling(name, palette):
    """树苗 —— **一棵小树，不是"一根茎加两片叶"的模板**。

    <h2>上一版为什么不行</h2>
    13 种树苗的**形状完全一样**：茎固定 4 格、两片对生叶固定各占 3 格，
    只有叶色不同。用户一眼就看出是复制粘贴。

    <h2>这一版：按真实的苗画</h2>
    每棵苗由三件事决定，全部来自这棵树自己的数据：

    ============  ==================================================
    茎高           树形大的（柿 / 柚 / 芒果）苗就高，小果木（李 / 杏）苗矮
    叶的排布       互生 → 左右交替；对生 → 同高度成对；
                   羽状复叶（龙眼 / 荔枝）→ 小叶成排地排在叶轴上
    叶形           披针形 / 卵形 / 倒卵形 / 椭圆（`TREE_LEAF_SHAPE`）
    ============  ==================================================

    于是芒果苗是"高茎 + 4 片细长叶"、石榴苗是"矮茎 + 两对对生圆叶"、
    荔枝苗是"一根轴上排着 6 片小叶"—— 摆一排没有两棵是一样的。

    另外**去掉了地上那条土色**：树苗是 `cross` 模型，土色块会浮在
    半空中（原版树苗也没有土）。
    """
    form, arrange, count, ratio, traits = leaf_shape(name)
    size = tree_size(name)
    base, _spread, _hole, _scale, _glossy = leaf_look(name)
    # 嫩芽比成叶浅一点、黄一点（新叶本来就是）
    leaf = _shade(base, 0.18)
    ramp = _leaf_ramp(leaf, 2.4)
    cols = (ramp[0], ramp[2], ramp[3])
    # 茎取这棵树**树皮的暗色** —— 之前用的是提亮过的树皮主色，
    # 一像素宽都嫌亮，整根茎比叶子还抢眼，看着像棕色的杆子。
    _bark_dark = _tree_data().TREE_WOOD_LOOK.get(
        name, ((74, 56, 40),) * 5)[0]
    stem_c = _shade(_bark_dark, 0.16)

    img = _canvas()

    # ---- 茎：树形越大越高（4~7 格）。**一像素宽**，只在根部加粗一格 ----
    stem_h = 4 + size
    base_y = SIZE - 1
    for i in range(stem_h):
        y = base_y - i
        _px(img, 8, y, stem_c)
    _px(img, 7, base_y, _shade(stem_c, -0.18))     # 根颈
    _px(img, 7, base_y - 1, _shade(stem_c, -0.08))

    top = base_y - stem_h + 1

    # 叶的纵向位置：**从茎底铺到茎顶**。
    #
    # 上一版写的是 `top + 1 + i * 2` —— y 往下增大，所以叶数一多
    # （树形大的苗 count=4）最后一片就跑到画布外，茎顶反而是光的。
    # 现在按 stem_h 等分，几片叶都铺得下。
    span = max(1, stem_h - 1)
    if count > 1:
        ys = [base_y - 1 - int(round(i * span / float(count)))
              for i in range(count)]
    else:
        ys = [base_y - 2]

    # ---- 叶：按排列方式长。叶片要**够大**，让茎大部分被叶子盖住 ----
    if arrange == "pinnate":
        # 羽状复叶：小叶成对排在叶轴上（叶片本身就小）
        for y in ys:
            for side in (-1, 1):
                _draw_blade(img, 8 + side * 0.6, y,
                            math.radians(-90 + side * 56),
                            3.8 + size * 0.4, ratio, form, cols, ())
    elif arrange == "opposite":
        for y in ys:
            for side in (-1, 1):
                _draw_blade(img, 8 + side * 0.6, y,
                            math.radians(-90 + side * 62),
                            5.6 + size * 0.6, ratio, form, cols, ())
    else:
        # 互生：左右交替，而且**越往上叶片越小**（苗的顶叶本来就没长开）
        for i, y in enumerate(ys):
            side = -1 if i % 2 == 0 else 1
            ln = (6.2 + size * 0.6) * (1.0 - i * 0.10)
            _draw_blade(img, 8 + side * 0.6, y,
                        math.radians(-90 + side * 52),
                        ln, ratio, form, cols, traits)
    # ---- 顶芽：茎顶一小撮亮色 ----
    _px(img, 8, top, ramp[3])
    _px(img, 8, top + 1, ramp[2])
    return img


# ======================================================================
# 树叶
# ======================================================================

def leaves(name, palette):
    """树叶的**方块贴图** —— 照原版的分寸做，但每棵树各长各的。

    <h2>先量了原版，再动手</h2>
    把原版 `block/oak_leaves` 拆开数了一遍像素：

    * 透明（alpha=0）**32.8%**，其余 **67.2% 全不透明** ——
      原版树叶**根本不用半透明**，通透感全部来自"洞"。
    * 洞**以单像素为主**：56 段连续孔里 36 段长度 1、13 段长度 2、
      6 段长度 3、只有 1 段长度 4（平均 1.50，最长 4）。
      换句话说就是"胡椒盐 + 偶尔两三个连着的"。
    * 整张图**只有 4 种明度**（灰度 102~187，约 1 : 1.83）。

    第一版我按"45% 半透明 + 10% 小洞"去做，3×3 平铺时蓝天透得满屏都是，
    像一块纱窗而不是树冠。第二版又把孔做成 2×2 打底的大团，像被虫啃过。
    —— 量过之后才知道：**通透来自洞的"数量"（三成），不来自 alpha，
    也不来自洞的"大小"。**

    <h2>每棵树各长各的（这一版的重点）</h2>
    上一版 13 种树叶是"同一套参数换个噪声种子"，等于复制粘贴。现在
    叶色、明暗跨度、镂空率、叶簇大小**四项都由 {@code TREE_LEAF_LOOK} 给**：

    ============  ==========================================
    叶基色         直接写进像素（不走运行时 tint）
    明暗跨度       4 档拉多开 —— 枣树亮而花、柑橘深而平
    镂空率         0.28~0.34 之间逐个不同（原版 0.328）
    叶簇尺度       3=小叶密、5=大叶疏
    蜡质反光       柑橘 / 柿 / 柚这类革质叶点几点高光
    ============  ==========================================

    于是枣树叶是亮黄绿的小碎叶、柿树叶是墨绿的大片革质叶、
    梨树叶是灰绿的大叶 —— 13 种摆在一起一眼能分开。

    <h2>三段码</h2>

    1. **洞**：**按个数挑**，不是按阈值切。逐像素噪声 + 半格低频噪声
       合成一个"该不该是洞"的分数，再把分数最低的若干像素挑出来 ——
       个数精确等于 {@code 镂空率 × 256}。低频那一项让洞倾向成小串，
       行程分布于是贴着原版。
       （一开始用两个阈值凑比例，噪声分布一偏就差出十几个百分点，
       量出来只有 21%；改成按个数挑之后是精确值。）
    2. **明度**：4 档 `_leaf_ramp(base, spread)`，用低频噪声决定这一片
       亮还是暗，再逐像素微抖一档。
    3. **不做边缘压暗**。原版没有；加了以后 3×3 平铺会冒出一圈
       规整的矩形暗边（因为"边缘"是贴图的边，不是叶丛的边）。
    """
    base, spread, hole, clump_scale, glossy = leaf_look(name)
    ramp = _leaf_ramp(base, spread)
    seed = _seed(name)

    # --- 1) 挑洞：分数最低的那些 ---
    scored = []
    for y in range(SIZE):
        for x in range(SIZE):
            grain = _noise(x, y, seed + 5)
            # 低频那一项权重小一点：只让洞"倾向"成串，不要连成片
            pair = _noise(x // 2, y // 2, seed + 71)
            scored.append((grain + pair * 0.35, x, y, grain))
    scored.sort()
    target = int(round(hole * SIZE * SIZE))
    grain_of = {}
    holes = set()
    for i, (score, x, y, grain) in enumerate(scored):
        grain_of[(x, y)] = grain
        if i < target:
            holes.add((x, y))

    img = _canvas()
    for y in range(SIZE):
        for x in range(SIZE):
            if (x, y) in holes:
                continue
            clump = _noise(x // clump_scale, y // clump_scale, seed + 19)
            lvl = 1.5 + (clump - 0.5) * spread
            lvl += (grain_of[(x, y)] - 0.5) * (spread * 0.42)
            _px(img, x, y, ramp[max(0, min(3, int(round(lvl))))])

    # 革质叶的高光：几片"翻过来的叶子"反射天光，是很小的一撮亮斑
    if glossy:
        for i in range(4):
            hx = 2 + int(_noise(i, 1, seed + 91) * 12)
            hy = 2 + int(_noise(i, 9, seed + 91) * 12)
            img.putpixel((hx, hy), ramp[3])
            img.putpixel(((hx + 1) % SIZE, hy), ramp[3])
    return img


def leaves_item(name, palette):
    """树叶的**物品图标** —— **一枝该树的叶子**，每棵树的都不一样。

    <h2>为什么不能直接拿方块贴图当图标</h2>
    方块贴图三成是洞、剩下一律不透明，直接复用的话物品栏里就是一块
    打满孔的绿 —— 看不清是片叶子。原版的做法也是这样：方块贴图照旧，
    **物品另用 `item/generated` + 一张实心图标**。

    <h2>走过的两条弯路</h2>

    1. **"旋转椭圆"叠三片** —— 三片糊成一坨；中脉条件
       `abs(v) < 0.14` 在椭圆中心横扫过去，画成了一条又宽又亮的横杠；
       椭圆没有叶尖，轮廓是一团圆的。
    2. **固定披针形 × 3 片** —— 形状终于对了，但**13 棵树的形状一模一样**，
       只是颜色不同，用户直接指出"不要复制粘贴"。

    <h2>这一版：把"一枝叶子"照着真实的树画</h2>

    一枝 = **一根叶轴 + 若干片叶**，两件事都由这棵树自己的数据决定：

    ==============  ======================================================
    叶形            披针形（桃李杏梅芒）/ 卵形（枣、石榴）/
                    倒卵形（柑橘、柚）/ 椭圆（梨、柿、樱、龙眼、荔枝）
    排列            互生（左右交替）/ 对生（同高度成对）/
                    羽状复叶（龙眼、荔枝 —— 一根轴上几对小叶）
    片数            2 ~ 4
    宽长比          0.24（芒果细长）~ 0.46（柿宽圆）
    特征            基部三出脉（枣）/ 叶柄翼叶（柑橘、柚）/ 尾尖（芒果、荔枝）
    ==============  ======================================================

    于是：**荔枝是一根轴上排着 4 对小叶**、**柑橘的叶柄上带一小片翼叶**、
    **枣叶基部有三出脉**、**芒果叶细长带尾尖** —— 形状、叶数、特征三样
    都不同，13 张图标摆一排没有两张是一样的。

    叶色跟方块贴图用**同一份** `TREE_LEAF_LOOK`，所以图标和方块永远同色。
    """
    form, arrange, count, ratio, traits = leaf_shape(name)
    base, _spread, _hole, _scale, _glossy = leaf_look(name)
    # 三档色：轮廓 / 叶面 / 受光。档距比 `_ramp` 宽，图标里才能分出层次。
    dark = _shade(base, -0.46)
    main_c = _shade(base, 0.04)
    light_c = _shade(base, 0.34)
    cols = (dark, main_c, light_c)

    img = _canvas()

    # ---- 叶轴 / 短枝 ----
    #
    # 上一版这里画成了一条**两像素宽的浅棕线**，整枝看着像竹子，
    # 叶子还都飘在旁边。两条教训：
    #   * 枝**只占一像素**而且颜色要压暗（浅棕在绿色里太抢眼）；
    #   * 叶片要**贴着枝长**并且**够大**，让枝大部分被叶子盖住 ——
    #     露出来的那一小截才读作"枝条"，露太多就读作"竹竿"。
    #
    # 两种排布：
    #   * 羽状复叶（龙眼 / 荔枝）—— 真的需要一根**明显的叶轴**，
    #     因为"一根轴上排着小叶"正是它们最好认的特征；
    #   * 其余 —— 叶子从**短枝顶端**发散开（基部张得开、往上收拢），
    #     枝只在下端露一小截，读作"掐下来的一枝"。
    props = _tree_data().TREE_WOOD_LOOK.get(
        name, ((74, 56, 40), (108, 82, 56), (140, 110, 78),
               (188, 158, 116), (178, 148, 108)))
    # 枝条取树皮**最暗**那一档 —— 浅棕在绿色里太抢眼，会把整枝读成竹竿
    stem_c = props[0]

    if arrange == "pinnate":
        ox, oy = 5.4, 14.4
        tx, ty = 9.6, 3.2
        steps = int(max(abs(tx - ox), abs(ty - oy))) + 1
        for i in range(steps + 1):
            t = i / float(steps)
            _px(img, int(round(ox + (tx - ox) * t)),
                int(round(oy + (ty - oy) * t)), stem_c)

        def along(t):
            return (ox + (tx - ox) * t, oy + (ty - oy) * t)

        # 小叶**成对**排在叶轴上，叶片小而狭长
        pairs = max(2, count)
        for i in range(pairs):
            t = 0.18 + i * (0.60 / max(1, pairs - 1))
            px_x, px_y = along(t)
            for side in (-1, 1):
                _draw_blade(img, px_x + side * 0.6, px_y,
                            math.radians(-90 + side * 58),
                            4.6, ratio, form, cols, traits)
        # 顶生小叶：奇数羽状复叶的顶端只有一片
        px_x, px_y = along(1.0)
        _draw_blade(img, px_x, px_y, math.radians(-90),
                    5.2, ratio, form, cols, traits)
    else:
        # 短枝：只在下端露一小截
        bx, by = 8.0, 15.0
        tip = 8.4
        for y in range(7, 16):
            _px(img, int(round(bx)), y, stem_c)
        _px(img, int(round(bx)) - 1, 15, _shade(stem_c, -0.20))

        # 叶子沿枝往上排：**基部张得开、顶端收拢**，越往上越小
        nodes = []
        if arrange == "opposite":
            # 对生：同一个高度左右成对
            for i in range(count):
                t = i / float(max(1, count - 1)) if count > 1 else 0.5
                nodes.append((t, -1))
                nodes.append((t, 1))
        else:
            # 互生：一左一右交替。
            # 节数给 count + 1：多出来的那一节在**最下面**，
            # 补上左下角常空一块的毛病，整枝也更满。
            total = count + 1
            for i in range(total):
                t = i / float(total - 1)
                side = -1 if i % 2 == 1 else 1
                nodes.append((t, side))

        for (t, side) in nodes:
            y = 14.2 - t * 7.0                    # 基部 y=14.2、顶端 y=7.2
            span = 74 - t * 32                    # 张角：基部 74°、顶端 42°
            ln = 8.0 - t * 1.4
            _draw_blade(img, bx + side * 0.7, y,
                        math.radians(-90 + side * span),
                        ln, ratio, form, cols, traits)
        # 枝顶端一片小叶（收口）
        _draw_blade(img, tip, 7.0, math.radians(-90),
                    5.0, ratio, form, cols, traits)

    # ---- 叶柄：最下面露一小截（掐下来的一枝）----
    _px(img, 7, 15, _shade(stem_c, -0.16))
    return img


# ======================================================================
# 木制品：原木 / 木头 / 去皮 / 木板
# ======================================================================
# 13 种果木各一套。五色由 {@code TREE_WOOD_LOOK} 给：
#
#     (树皮暗, 树皮主, 树皮亮, 去皮色, 木板基色)
#
# 所以枣木是红褐、柑橘木是姜黄、柿木近乎黑、柚木偏黄绿 —— 摆一排
# 是 13 种颜色的木头，而不是同一块木头换了个名字。
#
# 原版木头的画法就三条，这里照做：
#
#   * **侧面**：深浅竖线按固定周期循环（原版是 4 像素一轮），
#     再叠一点树皮疙瘩，免得是死板的直线；
#   * **断面**：外圈树皮 + 几圈年轮，越里越浅；
#   * **去皮**：把树皮的疙瘩全去掉，换成沿轴向的细木纹，
#     明度整体抬高一档 —— 一眼就能看出"剥了皮"。
#
# 因为相邻方块会拼接，**纹理必须能左右接缝**：所有的竖线周期都
# 整除 16，横向的疙瘩也用 4 格一组的低频噪声。

def _opaque(colour):
    return Image.new("RGBA", (SIZE, SIZE), tuple(colour[:3]) + (255,))


def log_side(fruit="fruit"):
    """树干侧面：深浅竖线循环 + 树皮疙瘩。"""
    dark, main_c, light, _stripped, _planks = wood_look(fruit)
    img = _opaque(main_c)
    seed = _seed(fruit + "/bark")
    for x in range(SIZE):
        # 周期 4 整除 16 → 左右拼接不会断层
        slot = x % 4
        c = dark if slot == 0 else (light if slot == 2 else main_c)
        for y in range(SIZE):
            v = c
            # 树皮疙瘩：纵向按 4 像素分组，才不是胡椒盐
            bump = _noise(x, y // 4, seed)
            if bump > 0.84:
                v = _shade(c, -0.20)
            elif bump < 0.12:
                v = _shade(c, 0.16)
            _px(img, x, y, v)
    return img


def log_top(fruit="fruit"):
    """树干断面：一圈树皮 + 几圈**很淡**的年轮。

    第一版把年轮画成了树皮那种深色，结果 16×16 下就是一个"靶心" ——
    眼睛先看见一个黑圈，而不是一块木头。原版断面的年轮对比度很低，
    真正的视觉重点只有**外面那一圈树皮**。所以这里：

    * 外圈两像素：树皮暗 + 树皮亮（这是唯一强对比的地方）；
    * 里面全部用去皮色打底（断面的木质本来就是浅的）；
    * 年轮只压 8~14% 的暗，而不是直接上树皮色。
    """
    dark, main_c, light, stripped, _planks = wood_look(fruit)
    img = _opaque(stripped)
    seed = _seed(fruit + "/ring")
    cx = cy = (SIZE - 1) / 2.0

    # 外圈树皮：一像素暗 + 一像素主色，模仿原版"深一圈、浅一圈"
    for y in range(SIZE):
        for x in range(SIZE):
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge == 0:
                _px(img, x, y, dark)
            elif edge == 1:
                _px(img, x, y, main_c)

    # 年轮：低对比度，半径带一点抖动（真年轮不是同心圆）
    for (radius, amount) in ((5.9, -0.11), (3.6, -0.07), (1.8, -0.14)):
        r = radius + (_noise(0, int(radius * 7), seed) - 0.5) * 0.8
        for y in range(SIZE):
            for x in range(SIZE):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if abs(d - r) < 0.5:
                    _px(img, x, y, _shade(stripped, amount))

    # 髓心：正中心一个深点
    _px(img, int(cx), int(cy), _shade(stripped, -0.26))
    _px(img, int(cx) + 1, int(cy), _shade(stripped, -0.18))

    # 木质颗粒，不然断面像塑料
    for y in range(SIZE):
        for x in range(SIZE):
            if _noise(x, y, seed + 40) > 0.88:
                px = img.getpixel((x, y))
                img.putpixel((x, y), _shade(px, -0.07) + (255,))
    return img


def stripped_side(fruit="fruit"):
    """去皮侧面：细密的竖木纹，比树皮亮一档、无疙瘩。"""
    _dark, _main, _light, stripped, _planks = wood_look(fruit)
    img = _opaque(stripped)
    seed = _seed(fruit + "/strip")
    for x in range(SIZE):
        # 细木纹：每 2 像素一条，周期 8 整除 16
        slot = x % 8
        for y in range(SIZE):
            v = stripped
            if slot in (0, 5):
                v = _shade(stripped, -0.14)
            elif slot in (3, 6):
                v = _shade(stripped, 0.08)
            # 长条状的木纹纹理（纵向连续）
            if _noise(x, y // 8, seed) > 0.82:
                v = _shade(v, -0.09)
            _px(img, x, y, v)
    return img


def stripped_top(fruit="fruit"):
    """去皮断面：低对比度的年轮，没有树皮圈。"""
    _dark, _main, _light, stripped, _planks = wood_look(fruit)
    img = _opaque(stripped)
    seed = _seed(fruit + "/stripr")
    cx = cy = (SIZE - 1) / 2.0
    for (radius, amount) in ((6.0, -0.09), (4.0, -0.06), (2.1, -0.13)):
        r = radius + (_noise(1, int(radius * 5), seed) - 0.5) * 0.6
        for y in range(SIZE):
            for x in range(SIZE):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if abs(d - r) < 0.5:
                    _px(img, x, y, _shade(stripped, amount))
    # 髓心
    _px(img, int(cx), int(cy), _shade(stripped, -0.22))
    # 边缘微微收暗，这样一块块断面摆开时边界分得开（但不出网格线）
    for y in range(SIZE):
        for x in range(SIZE):
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge == 0:
                px = img.getpixel((x, y))
                img.putpixel((x, y), _shade(px, -0.10) + (255,))
    return img


def planks(fruit="fruit"):
    """木板：横条的板，每 4 像素一条，条与条错缝（像砌砖那样）。

    原版木板的画法就是**四条横向木板 + 竖着的短接缝错开**。
    错缝是重点：对齐了就变成"竹席"，错开才像一块块板拼的。
    """
    _dark, _main, _light, _stripped, base = wood_look(fruit)
    img = _opaque(base)
    seed = _seed(fruit + "/plank")
    light_b = _shade(base, 0.13)
    dark_b = _shade(base, -0.17)
    seam = _shade(base, -0.34)

    for y in range(SIZE):
        band = y // 4                      # 第几条板
        for x in range(SIZE):
            v = base
            # 板面：每条板整体比上一条差半档，出层次
            if band % 2 == 1:
                v = _shade(base, -0.06)
            # 板上的木纹（横向连续）
            if _noise(x // 4, y, seed) > 0.84:
                v = _shade(v, 0.09)
            elif _noise(x // 4, y, seed + 7) < 0.13:
                v = _shade(v, -0.10)
            _px(img, x, y, v)

    # 板缝：横向，每 4 像素一条暗线
    for band in range(1, 4):
        y = band * 4 - 1
        for x in range(SIZE):
            img.putpixel((x, y), seam + (255,))
            if band < 3:
                img.putpixel((x, y + 1), light_b + (255,))

    # 竖向短接缝：每条板错开 5 像素（和 4 互质 → 16 格不会撞出规律）
    for band in range(4):
        x = (band * 5 + 3) % SIZE
        for y in range(band * 4, band * 4 + 4):
            img.putpixel((x, y), seam + (255,))
            img.putpixel(((x + 1) % SIZE, y), dark_b + (255,))
    return img
