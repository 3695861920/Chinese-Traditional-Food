# -*- coding: utf-8 -*-
"""作物贴图：**完全程序化生成**，不使用任何现成素材。

    （被 tools/build_textures.py 调用，`--only crops`）

<h2>为什么之前程序画得难看，而这次能画好</h2>

前两版程序画法的失败不是"没用心"，是**方法错了**：

* 直接在 16×16 的网格上算坐标 —— 一条斜线只能画成楼梯，
  一片叶子只能是菱形；
* 每片叶、每根茎各画各的，没有遮挡关系 —— 叠在一起就糊成一团。

这一版换了两个根本做法：

**一、超采样（supersampling）。**
先在一张 **8 倍**分辨率的画布（128×128）上用**浮点坐标**画曲线、
画带锥度的笔画，画完再把 8×8 个小像素**平均**成一个最终像素。
这样斜线、弧线、叶尖的圆角都是平滑的 —— 因为"抗锯齿"这件事
在降采样那一步自然发生了。

**二、按部位记深度（depth）。**
每画一个部件就记一个自增的深度号。降采样之后：
轮廓（旁边是空的）压暗一档，**部位与部位的交界**（左右深度不同）
也压暗一档。于是叶子叠叶子时，底下的那片会自然"退到后面去"，
而不是糊成一坨。这两步加起来就是像素画里说的"描边 + 内轮廓"。

<h2>形状怎么来的</h2>

一片叶子 = **沿一条弧线、笔宽按叶片剖面变化的笔画**。
剖面用 `sin(π t^0.75)`：根部窄、四成处最宽、尖端收拢 —— 这就是叶子。

一根茎 = 同样的一条笔画，只是笔宽从根到梢线性收细。

所以整个生成器只需要三个图元：**带锥度的曲线笔画**、**圆**、**椭圆**。
八种株型的差别只在于"弧线怎么摆、宽窄多少、果实长什么样"。

<h2>八种株型</h2>

===========  ==========================================================
`grass`      一丛**拱形**的长窄叶，成熟时顶端抽穗（稻 / 谷 / 高粱 / 玉米）
`legume`     直立茎 + 三出复叶，成熟时挂豆荚
`seedpod`    细直茎 + 稀疏小叶，成熟时顶部分叉结蒴果
`root`       贴地**羽状**叶，成熟时基部露出根肩
`leafy`      从中心放射的宽叶，白菜成熟时抱出一颗球
`bush`       单茎 + 互生叶，成熟时叶腋垂果
`vine`       贴地横走的藤 + 大叶，成熟时躺着瓜
`fungus`     枯木 + 簸开的耳片
===========  ==========================================================

配色取自**收获物**：叶色是在一个基准绿上转一点色相、并按收获物的
深浅微调（深色作物如木耳、茄子，叶子也跟着深）；
穗 / 果 / 露出的根肩直接用收获物本身的颜色 ——
所以红番茄、紫茄子、白萝卜都体现在果实上，而叶子始终是叶子。
"""

import math
import os
import zlib

from PIL import Image

SIZE = 16          # 成品边长
SS = 8             # 超采样倍数（画在 SIZE*SS 的画布上）
BIG = SIZE * SS


# ======================================================================
# 颜色
# ======================================================================

def _clamp(v):
    return max(0, min(255, int(v + 0.5)))


def _shade(colour, t):
    """把颜色往暗（t<0）或亮（t>0）推一档。"""
    if t >= 0:
        f = 1.0 + t
        return tuple(_clamp(c * f) for c in colour[:3])
    f = 1.0 + t
    return tuple(_clamp(c * f) for c in colour[:3])


def _mix(a, b, t):
    return tuple(_clamp(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _hue_shift(colour, amount):
    """转一点色相（用于同株型之间的区分）。"""
    if not amount:
        return colour[:3]
    import colorsys
    r, g, b = [c / 255.0 for c in colour[:3]]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + amount) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (_clamp(r * 255), _clamp(g * 255), _clamp(b * 255))


def _ramp(colour, steps=4, spread=0.34):
    """从一排颜色拉出明暗阶（暗 → 亮）。"""
    out = []
    for i in range(steps):
        t = (i / (steps - 1.0)) * 2.0 - 1.0
        out.append(_shade(colour, t * spread))
    return out


def _lum(colour):
    return (colour[0] * 0.30 + colour[1] * 0.59 + colour[2] * 0.11) / 255.0


def _soften(colour, amount=0.18):
    """把颜色往它自己的灰里调一点 —— 降饱和。

    程序生成的颜色容易太"艳"。往灰里混一点点，
    一丛绿就会从"荧光绿"变成"草地的绿"，这就是"柔和"的来源。
    """
    grey = sum(colour[:3]) / 3.0
    return tuple(_clamp(c + (grey - c) * amount) for c in colour[:3])


def _pixel_ramp(colour, steps=4):
    """**像素画用的色阶**：从阴影到受光。

    和普通渐变不同，这里有两个刻意的选择：

    * **底面压得够暗**（0.52 倍）—— 最暗那一阶要能直接当**轮廓线**用，
      所以不必额外画黑边；
    * **顶面只提一点点**（1.20 倍）—— 提太多会变成刺眼的高光，
      而像素画的高光靠"位置"（左上边缘）而不是靠"更亮"。

    中间两阶落在 0.75 与 0.98，间距均匀 —— 抖动出来的图案才好看。
    """
    lo, hi = 0.54, 1.28
    out = []
    for i in range(steps):
        t = i / (steps - 1.0)
        k = lo + (hi - lo) * t
        out.append(tuple(_clamp(c * k) for c in colour[:3]))
    return out


# Bayer 4×4 有序抖动阈值。像素画的"渐变"全靠它：
# 在两档色之间按这个图案交替，眼睛就会把一个 16×16 的小方块读成"渐变"。
BAYER4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def _bayer(x, y):
    return (BAYER4[y & 3][x & 3] + 0.5) / 16.0


def _dither(t, levels, x, y):
    """把 0~1 的连续值**带抖动地**量化成 ``levels`` 档。

    这是整套画法里最关键的一步：有了它，8 倍超采样出来的
    平滑明暗才会落成"两三种颜色交替"的像素图案 ——
    远看是渐变、近看是像素，而不是一片噪点或者一片死平。
    """
    t = max(0.0, min(0.9999, t))
    scaled = t * (levels - 1)
    base = int(scaled)
    if scaled - base > _bayer(x, y):
        base += 1
    return max(0, min(levels - 1, base))


def _seed(name):
    return zlib.crc32(name.encode("utf-8")) & 0x7FFF or 1


# ======================================================================
# 几何
# ======================================================================

def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp2(p, q, t):
    return (_lerp(p[0], q[0], t), _lerp(p[1], q[1], t))


def _bezier(p0, p1, p2, n=26):
    """二次贝塞尔 —— 叶片的弧线、拱起的叶丛都用它。

    为什么不用"直线 + 折角"：折角在降采样后会变成难看的硬拐弯，
    而贝塞尔出来的弧线平滑，正是叶子该有的样子。
    """
    pts = []
    for i in range(n + 1):
        t = i / float(n)
        u = 1.0 - t
        pts.append((
            u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        ))
    return pts


def _leaf_profile(t):
    """叶片剖面：根部窄 → 四成处最宽 → 尖端收拢。

    指数 0.75 让最宽处落在偏根部的位置 —— 真实叶子就是这样
    （叶基圆钝、叶尖渐尖），用对称的 sin(πt) 会显得上下一样胖。
    """
    return math.sin(math.pi * (t ** 0.75))


# ======================================================================
# 画布：超采样 + 深度
# ======================================================================

class Sheet:
    """一张超采样画布。

    三个缓冲：
      * ``cov``   覆盖标记（哪些超采样像素被画到了）
      * ``col``   颜色
      * ``dep``   深度号（后画的大）—— 用来在降采样后区分部件边界
    """

    def __init__(self):
        self.cov = bytearray(BIG * BIG)
        self.col = [(0, 0, 0)] * (BIG * BIG)
        self.dep = bytearray(BIG * BIG)
        self.depth = 0

    # ---- 内部：把 16 空间的浮点坐标换成超采样整数坐标 ----
    # 注意 y 轴：16 空间里 y=0 是**地面**、向上为正；
    # 图像里 y=0 是顶边。这里统一在 stamp 里翻转。
    def _stamp(self, cx, cy, r, colour):
        rr = r * SS
        x0 = max(0, int((cx - r) * SS))
        x1 = min(BIG, int((cx + r) * SS) + 1)
        y0 = max(0, int((cy - r) * SS))
        y1 = min(BIG, int((cy + r) * SS) + 1)
        d = self.depth
        for iy in range(y0, y1):
            row = BIG - 1 - iy              # 翻转 y
            base = row * BIG
            dy = iy + 0.5 - cy * SS
            for ix in range(x0, x1):
                dx = ix + 0.5 - cx * SS
                if dx * dx + dy * dy <= rr * rr:
                    k = base + ix
                    self.cov[k] = 1
                    self.col[k] = colour
                    self.dep[k] = d

    def stroke(self, pts, w_from, w_to, colour, cap=True):
        """沿折线画一条**带锥度**的笔画。

        ``w_from`` / ``w_to`` 是两端的半宽（16 空间）。
        做法是沿弧线密集地"盖章"：每一步盖一个半径插值出来的圆，
        相邻圆重叠之后就是一条平滑收细的笔画。
        """
        self.depth = (self.depth + 1) & 0xFF
        n = len(pts)
        if n < 2:
            return
        steps = max(2, int(sum(math.dist(pts[i], pts[i + 1])
                               for i in range(n - 1)) * SS * 1.6))
        for s in range(steps + 1):
            t = s / float(steps)
            fi = t * (n - 1)
            i = min(n - 2, int(fi))
            f = fi - i
            cx, cy = _lerp2(pts[i], pts[i + 1], f)
            w = _lerp(w_from, w_to, t)
            if w <= 0.02:
                continue
            self._stamp(cx, cy, w, colour)

    def blade(self, spine, max_w, colour, taper=0.0):
        """一片叶子：沿 ``spine`` 画，宽度按叶片剖面变化。

        ``taper`` 给叶片一点"向一侧偏斜"的感觉（真实叶子两侧不对称）。
        """
        self.depth = (self.depth + 1) & 0xFF
        n = len(spine)
        if n < 2:
            return
        steps = max(3, n * 3)
        for s in range(steps + 1):
            t = s / float(steps)
            fi = t * (n - 1)
            i = min(n - 2, int(fi))
            f = fi - i
            cx, cy = _lerp2(spine[i], spine[i + 1], f)
            w = max_w * _leaf_profile(t)
            if w <= 0.05:
                continue
            if taper:
                # 往侧向偏一点：叶子的中脉不在正中
                nx, ny = spine[min(n - 1, i + 1)]
                px, py = spine[i]
                dx, dy = nx - px, ny - py
                ln = math.hypot(dx, dy) or 1.0
                off = taper * w * (t - 0.5)
                cx += (-dy / ln) * off
                cy += (dx / ln) * off
            self._stamp(cx, cy, w, colour)

    def disc(self, c, r, colour):
        self.depth = (self.depth + 1) & 0xFF
        self._stamp(c[0], c[1], r, colour)

    def ellipse(self, c, rx, ry, colour, rot=0.0):
        """椭圆（果实、穗子）。用"在一个旋转过的坐标系里盖章"实现。"""
        self.depth = (self.depth + 1) & 0xFF
        ca, sa = math.cos(-rot), math.sin(-rot)
        # 用圆的盖法会变成正圆，这里改成逐超采样像素判断
        d = self.depth
        cx, cy = c
        rx = max(rx, 0.05)
        ry = max(ry, 0.05)
        x0 = max(0, int((cx - max(rx, ry)) * SS))
        x1 = min(BIG, int((cx + max(rx, ry)) * SS) + 1)
        y0 = max(0, int((cy - max(rx, ry)) * SS))
        y1 = min(BIG, int((cy + max(rx, ry)) * SS) + 1)
        for iy in range(y0, y1):
            row = BIG - 1 - iy
            base = row * BIG
            dy = (iy + 0.5) / SS - cy
            for ix in range(x0, x1):
                dx = (ix + 0.5) / SS - cx
                u = dx * ca - dy * sa
                v = dx * sa + dy * ca
                if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0:
                    k = base + ix
                    self.cov[k] = 1
                    self.col[k] = colour
                    self.dep[k] = d

    # ---- 降采样 ----
    def resolve(self):
        """把 BIG×BIG 平均成 16×16，返回 (PIL 图, 边界标记)。"""
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        px = img.load()
        # 记录哪些输出像素是"部件交界"，后处理时要压暗
        edge = [[False] * SIZE for _ in range(SIZE)]

        for oy in range(SIZE):
            for ox in range(SIZE):
                r = g = b = 0
                n = 0
                depths = {}
                for sy in range(SS):
                    # **不要再翻转 y**。`_stamp` 存的时候已经把"世界 y
                    # （0=地面）"翻成"图像行（0=顶边）"了；这里若再翻一次
                    # 就是**双重翻转** —— 结果是整株植物上下颠倒：
                    # 根长在头顶、穗垂在土里。（踩过一次，dump 像素才发现。）
                    row = oy * SS + sy
                    base = row * BIG
                    for sx in range(SS):
                        k = base + ox * SS + sx
                        if not self.cov[k]:
                            continue
                        c = self.col[k]
                        r += c[0]
                        g += c[1]
                        b += c[2]
                        n += 1
                        d = self.dep[k]
                        depths[d] = depths.get(d, 0) + 1
                total = SS * SS
                # 覆盖阈值必须**低**。一像素宽的叶子斜穿过一个输出像素时，
                # 在 8×8 的超采样里只盖住十来个子像素（≈ 15~25%）。
                # 阈值定高（比如 0.42）会把细叶整条吃掉 —— 植株就"秃"了。
                # 定在 0.20，细叶能活，而抗锯齿仍然有效（颜色是平均出来的）。
                if n < total * 0.20:
                    continue
                px[ox, oy] = (_clamp(r / float(n)), _clamp(g / float(n)),
                              _clamp(b / float(n)), 255)
                # 部件交界：这个小方块里出现了两种以上深度
                big = [d for d, c in depths.items() if c >= total * 0.15]
                if len(big) > 1:
                    edge[oy][ox] = True
        return img, edge


# ======================================================================
# 后处理：描边 + 内轮廓 + 左上高光
# ======================================================================
#
# 这是像素画里最关键的一步。降采样出来的图虽然平滑，但
# **颜色是连续的**（抗锯齿产生了几百种中间色），那不是像素画。
#
# 所以最后一步要把它**压回一张小色板**，并且用**有序抖动**过渡：
#
#   1. 按色相判断这个像素属于"叶"还是"果实"，选对应的色阶；
#   2. 用它的亮度在色阶里定位成一个 0~1 的连续值；
#   3. **带 Bayer 抖动地**量化成 4 档 —— 于是渐变变成"两三种颜色交替"；
#   4. 再看它是不是轮廓 / 部件交界 / 受光面，在色阶里上下挪一档。
#
# 做完这一步，整张图只剩 8 种颜色（叶 4 + 果 4），
# 而且边缘是**硬的**（不再有半透明的过渡色）—— 这才是像素世界的味道。

def _finish(img, edge, ramps):
    """把超采样的平滑图像**压回小色板**，并用有序抖动做过过渡。

    这是像素画里最关键的一步。降采样出来的图颜色是连续的
    （抗锯齿产生了几百种中间色），那不是像素画。所以：

    1. 为每个像素在**多个色板**里挑最近的那个（叶 / 果 / 木…）；
    2. 用它的亮度在色板里定位成一个 0~1 的连续值；
    3. **带 Bayer 抖动地**量化成 4 档 —— 渐变变成"两三种颜色交替"；
    4. 再看它是不是轮廓 / 部件交界 / 受光面，在色板里上下挪一档。

    <h3>为什么要"多个色板 + 就近归类"</h3>
    一开始我用"绿系归叶、暖系归果"这种色相判断，结果**木耳的木头**
    （棕褐色）被归进了果色板 —— 而木耳的果色是近乎全黑的，
    于是那截木头直接变成一块黑。改成"就近归类"就不会有这种事：
    每种材质都能找到和自己最接近的那一档。

    做完这一步整张图只剩十几种颜色，而且边缘是**硬的**
    （不再有半透明的过渡色）—— 这才是像素世界的味道。
    """
    ramps = [r for r in ramps if r]
    if not ramps:
        return img

    src = img.copy()
    sp = src.load()
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    op = out.load()

    solid = [[sp[x, y][3] > 0 for x in range(SIZE)] for y in range(SIZE)]

    def at(x, y):
        return solid[y][x] if 0 <= x < SIZE and 0 <= y < SIZE else False

    def pick(rgb):
        """挑最接近的那个色板，并返回 (色板, 该像素在里面的 0~1 位置)。"""
        best, best_d, best_t = ramps[0], 1 << 30, 0.5
        for ramp in ramps:
            lo, hi = _lum(ramp[0]), _lum(ramp[-1])
            span = (hi - lo) or 1.0
            t = (_lum(rgb) - lo) / span
            # 与"这个亮度上色板会给的颜色"比距离，而不是与端点比
            idx = max(0, min(len(ramp) - 1, int(round(t * (len(ramp) - 1)))))
            c = ramp[idx]
            d = ((rgb[0] - c[0]) ** 2 + (rgb[1] - c[1]) ** 2
                 + (rgb[2] - c[2]) ** 2)
            if d < best_d:
                best, best_d, best_t = ramp, d, t
        return best, best_t

    for y in range(SIZE):
        for x in range(SIZE):
            if not solid[y][x]:
                continue
            ramp, t = pick(sp[x, y][:3])
            last = len(ramp) - 1
            idx = _dither(t, len(ramp), x, y)

            silhouette = not (at(x - 1, y) and at(x + 1, y)
                              and at(x, y - 1) and at(x, y + 1))
            if silhouette:
                idx = 0                     # 最暗那一档正好当轮廓线
            else:
                if edge[y][x]:
                    idx = max(0, idx - 1)   # 部件交界：压暗一档
                # 受光：紧贴剪影**左侧或上侧**的那一圈提一档
                if not at(x - 1, y) or not at(x, y - 1):
                    idx = min(last, idx + 1)
            op[x, y] = ramp[idx] + (255,)

    return out


# ======================================================================
# 果实形状
# ======================================================================

FRUIT_SHAPE = {
    "veg_tomato": "round", "veg_potato": "round",
    "veg_chili": "long", "veg_eggplant": "long",
    "veg_cucumber": "melon", "veg_wintermelon": "melon",
    "veg_luffa": "melon", "veg_bitter": "melon",
    "bean_round": "pod", "bean_mung": "pod", "bean_kidney": "pod",
    "bean_pea": "pod", "bean_flat": "pod", "bean_peanut": "pod",
    "ear_paddy": "spike", "ear_foxtail": "spike",
    "ear_sorghum": "spike", "crop_corn": "ear",
    "crop_sesame": "capsule",
    "veg_radish": "shoulder", "veg_sweetpotato": "shoulder",
    "veg_yam": "shoulder", "veg_taro": "bulb",
    "veg_garlic": "bulb", "veg_ginger": "bulb",
    "veg_napa": "leafball",
    "veg_woodear": "ear",
}


def _shape_of(kind):
    return FRUIT_SHAPE.get(kind or "", "round")


# ======================================================================
# 八种株型
# ======================================================================
#
# 约定：y 从 0（地面）向上。所有函数都画在 [0,16]×[0,16] 里。
#
# 每个函数负责：茎（先画，在底层）→ 叶（自下而上，左右交替）→ 果实（最后，压在最上）

def _grass(sh, stage, leaf, fruit, h, shape, rnd):
    """禾本：一丛**拱形**的长窄叶，成熟时顶端抽穗。"""
    n = 3 + stage // 2                       # 叶数随生长增加
    base = 7.6
    for i in range(n):
        side = -1 if i % 2 == 0 else 1
        spread = (i // 2)
        bx = base + side * (0.4 + spread * 0.45)
        # 拱形：从根部往外拱出去，再向上收。
        # 外张幅度要够大 —— 拱得太窄就变成一根竖线（第一版就是）
        arch = 2.6 + spread * 1.3
        top = h * (1.0 - spread * 0.13)
        spine = _bezier(
            (bx, 0.4),
            (bx + side * arch, top * 0.55),
            (bx + side * arch * 0.85, top),
            22)
        # 相邻叶片深浅交替 —— 不然一丛叶子糊成一块同色的绿
        lv = leaf if i % 2 == 0 else _shade(leaf, -0.10)
        w = 0.46 + 0.14 * (1.0 - stage / 7.0)
        sh.blade(spine, w, lv, taper=0.25 * side)

    # 中间补一根**直立**的叶：只有左右外张的弧形会劈成两丛、中间空一个洞。
    # 禾本科本来就有直立的主孽，补上它就成了一丛草。
    sh.blade(_bezier((base, 0.4),
                     (base + 0.25, h * 0.62),
                     (base + 0.1, h * 0.97), 18),
             0.50, leaf)

    # 穗：第 5 阶起抽出来，用收获物的颜色
    if stage >= 4:
        grow = min(1.0, (stage - 3) / 4.0 + 0.25)
        for i in range(0, n, 2):
            side = -1 if i % 2 == 0 else 1
            sp = (i // 2)
            bx = base + side * (0.4 + sp * 0.45)
            top = h * (1.0 - sp * 0.13)
            tipx = bx + side * (2.6 + sp * 1.3) * 0.85
            if shape == "ear":
                # 玉米：棒子长在**腰上**（叶腋），而且只有一根
                if i == 0:
                    sh.ellipse((bx + side * 1.5, h * 0.52),
                               1.05 * grow, 2.3 * grow, fruit, rot=0.18 * side)
                    # 苞叶
                    for k in (-1, 1):
                        sh.blade(_bezier((bx + side * 1.5 + k * 0.8, h * 0.52),
                                         (bx + side * 1.5 + k * 2.0, h * 0.60),
                                         (bx + side * 1.5 + k * 1.4, h * 0.72),
                                         12),
                                 0.55, _shade(leaf, -0.12))
            else:
                # 稻 / 谷 / 高粱：穗子从叶尖上方抽出来
                ln = 1.5 + 1.9 * grow
                sh.ellipse((tipx, top + ln * 0.55),
                           0.85 * grow + 0.35, ln * 0.62, fruit,
                           rot=0.12 * side)
                # 穗上的小颗粒
                for g in range(3 + int(grow * 3)):
                    t = g / float(3 + int(grow * 3))
                    gx = tipx + side * 0.25
                    gy = top + ln * (0.28 + 0.55 * t)
                    sh.disc((gx, gy), 0.30 + 0.08 * grow,
                            _shade(fruit, 0.16 if g % 2 else -0.10))


def _legume(sh, stage, leaf, fruit, h, shape, rnd):
    """豆科：直立茎 + 三出复叶，成熟时挂豆荚。"""
    sh.stroke(_bezier((7.8, 0.4), (7.8 + rnd() * 0.6 - 0.3, h * 0.5), (8.0, h), 14),
              0.62, 0.34, leaf)

    nodes = 2 + stage // 2
    for i in range(nodes):
        t = (i + 1) / float(nodes + 1)
        y = h * t
        side = -1 if i % 2 == 0 else 1
        # 三出复叶：一片朝外、一片朝上、一片朝内。
        # 叶展要够开 —— 花生 / 黄豆的丛是“铺开”的，窄了就成一束
        for (ang, ln, wd) in ((-0.55, 2.6, 0.62),
                              (-0.05, 3.1, 0.70),
                              (0.45, 2.5, 0.58)):
            a = ang * side + (0.25 if side > 0 else -0.25)
            ex = 8.0 + side * 0.55 + math.sin(a) * ln * 1.5
            ey = y + math.cos(a) * ln
            sh.blade(_bezier((8.0 + side * 0.5, y),
                             ((8.0 + ex) / 2, (y + ey) / 2 - 0.5),
                             (ex, ey), 14),
                     wd * (0.55 + 0.10 * (1 - stage / 7.0)), leaf, taper=0.2 * side)

    if stage >= 4 and shape != "bulb":
        grow = min(1.0, (stage - 3) / 4.0 + 0.25)
        for i in range(2):
            y = h * (0.30 + i * 0.22)
            side = -1 if i % 2 == 0 else 1
            sh.ellipse((8.0 + side * 1.15, y), 0.38 * grow + 0.15,
                       1.35 * grow + 0.25, fruit, rot=0.22 * side)
    elif stage >= 4:
        # 花生：荚在**地下**，只在根边露一点
        grow = min(1.0, (stage - 3) / 4.0 + 0.25)
        sh.ellipse((7.2, 0.9), 1.5 * grow, 0.85 * grow, fruit)
        sh.ellipse((9.1, 0.8), 1.0 * grow, 0.65 * grow, _shade(fruit, -0.12))


def _seedpod(sh, stage, leaf, fruit, h, shape, rnd):
    """籽用：细直茎 + 稀疏小叶，成熟时顶部分叉结蒴果（芝麻）。"""
    sh.stroke(((8.0, 0.4), (7.9, h * 0.5), (8.0, h)), 0.52, 0.30, leaf)

    n = 1 + stage // 2
    for i in range(n):
        t = (i + 1) / float(n + 2)
        y = h * t
        side = -1 if i % 2 == 0 else 1
        ex = 8.0 + side * (2.6 + 0.35 * i)
        ey = y + 0.9
        sh.blade(_bezier((8.0 + side * 0.4, y),
                         ((8.0 + ex) / 2, y - 0.2),
                         (ex, ey), 12),
                 0.62, leaf, taper=0.3 * side)

    if stage >= 3:
        grow = min(1.0, (stage - 3) / 4.0 + 0.30)
        branches = [(8.0, h)] if stage < 5 else [(8.0, h), (6.9, h - 0.9),
                                                 (9.1, h - 0.9)]
        for (bx, by) in branches:
            sh.ellipse((bx, by + 0.55), 0.62 * grow + 0.20,
                       0.95 * grow + 0.30, fruit)
            for g in range(2):
                sh.disc((bx - 0.45 + g * 0.9, by + 0.5), 0.30 + 0.10 * grow,
                        _shade(fruit, -0.14))


def _root(sh, stage, leaf, fruit, h, shape, rnd):
    """块根：贴地**羽状**叶，成熟时基部露出根肩。

    分两层（外矮内高）才有层次；而且先画叶、后画露出的根 ——
    这样叶子压在根上，看着是"从根里长出来的"。
    """
    pairs = 2 + stage // 2
    for i in range(pairs):
        side = -1 if i % 2 == 0 else 1
        outer = i // 2
        tip_y = h * (0.95 - outer * 0.15)
        tip_x = 8.0 + side * (1.6 + outer * 1.35)
        bx = 8.0 + side * (0.4 + outer * 0.45)
        sh.blade(_bezier((bx, 0.8),
                         (bx + side * 1.0, tip_y * 0.55),
                         (tip_x, tip_y), 16),
                 0.60 - outer * 0.05, leaf, taper=0.28 * side)
        # 羽状：主脉两侧各挂两片小裂片
        for k in (0.38, 0.70):
            mx = _lerp(bx, tip_x, k)
            my = _lerp(0.8, tip_y, k)
            for s2 in (-1, 1):
                sh.blade(_bezier((mx, my),
                                 (mx + s2 * 0.6, my + 0.25),
                                 (mx + s2 * 1.05, my + 0.70), 10),
                         0.34 - outer * 0.03, _shade(leaf, -0.08))

    if stage >= 4:
        grow = min(1.0, (stage - 3) / 4.0 + 0.25)
        if shape == "shoulder":
            sh.ellipse((8.0, 0.70), 2.0 * grow + 0.45, 0.85 * grow + 0.28, fruit)
            for k in (-1, 1):
                sh.ellipse((8.0 + k * 1.35 * grow, 0.58), 0.80, 0.48,
                           _shade(fruit, -0.12))
        else:
            # 蒜 / 姜 / 芋：一整颗球茎坐在根上
            sh.ellipse((8.0, 1.00), 1.55 * grow + 0.40, 1.10 * grow + 0.32, fruit)
            sh.ellipse((8.0, 1.90 + grow * 0.35), 0.38, 0.50,
                       _shade(fruit, 0.20))


def _leafy(sh, stage, leaf, fruit, h, shape, rnd):
    """叶菜：莲座叶。

    莲座的层次靠**两层**：外层叶矮而外张（快趴下了）、内层叶高而直立。
    之前所有叶子的端高度一样，就堆成一个矮墩（这就是第一版难看的原因之一）。

    韭菜与葱例外 —— 它们是一束**细长的管状叶**，得单独画。
    """
    if shape in ("veg_chive", "veg_scallion"):
        n = 3 + stage // 2
        for i in range(n):
            off = (i - n // 2) * 0.95
            hh = h * (1.0 - abs(i - n // 2) * 0.12)
            lean = 0.10 * off * abs(off)
            sh.blade(_bezier((8.0 + off * 0.30, 0.5),
                             (8.0 + off * 0.85 + lean * 0.4, hh * 0.55),
                             (8.0 + off + lean, hh), 14),
                     0.42, leaf)
        return

    n = 2 + stage // 1.6
    for i in range(int(n)):
        side = -1 if i % 2 == 0 else 1
        outer = i // 2
        tip_y = h * (0.98 - outer * 0.17)
        tip_x = 8.0 + side * (1.5 + outer * 1.5)
        bx = 8.0 + side * (0.35 + outer * 0.35)
        # 相邻叶片深浅交替，叶丛才有层
        lv = leaf if i % 2 == 0 else _shade(leaf, -0.11)
        sh.blade(_bezier((bx, 0.6),
                         (bx + side * 1.1, tip_y * 0.55),
                         (tip_x, tip_y), 18),
                 0.84 - outer * 0.07, lv, taper=0.22 * side)
        # 叶脉：一根细的深色线，让叶片不是一块平色
        sh.stroke(_bezier((bx, 0.8), (bx + side * 0.9, tip_y * 0.5),
                          (tip_x * 0.96, tip_y * 0.94), 12),
                  0.17, 0.10, _shade(leaf, -0.18))

    # 中间再立两片，把中心填住（莲座的中心不会露土）
    for k in (-1, 1):
        sh.blade(_bezier((8.0 + k * 0.5, 0.6),
                         (8.0 + k * 0.3, h * 0.50),
                         (8.0 + k * 0.9, h * 0.92), 14),
                 0.70, _shade(leaf, 0.06))

    if shape == "leafball" and stage >= 5:
        grow = min(1.0, (stage - 5) / 2.0 + 0.45)
        # 抱心：中间一颗球，用收获物的颜色（白菜是白的，得看得出来）
        sh.ellipse((8.0, h * 0.42), 2.2 * grow + 0.5, 2.0 * grow + 0.5, fruit)
        sh.ellipse((7.2, h * 0.42 + 0.7), 0.9 * grow, 0.75 * grow,
                   _shade(fruit, 0.24))


def _bush(sh, stage, leaf, fruit, h, shape, rnd):
    """茄果：单茎 + 互生叶，成熟时叶腋垂果。"""
    sh.stroke(((8.0, 0.4), (7.85 + rnd() * 0.3, h * 0.5), (8.0, h)),
              0.68, 0.40, leaf)

    nodes = []
    n = 2 + stage // 1.7
    for i in range(int(n)):
        t = (i + 1) / float(int(n) + 1)
        y = h * t
        side = -1 if i % 2 == 0 else 1
        ex = 8.0 + side * (2.4 + 0.2 * i)
        ey = y + 0.55
        sh.blade(_bezier((8.0 + side * 0.45, y),
                         ((8.0 + ex) / 2, y - 0.35),
                         (ex, ey), 15),
                 0.95, leaf, taper=0.25 * side)
        nodes.append((8.0 + side * 1.35, y))

    if stage >= 4:
        grow = min(1.0, (stage - 3) / 4.0 + 0.28)
        picks = nodes[-2:] if shape == "round" else nodes[-1:]
        for (nx, ny) in picks:
            if shape == "long":
                # 辣椒 / 茄子：垂着的一根
                sh.ellipse((nx, ny - 1.5 * grow - 0.3),
                           0.62 * grow + 0.18, 1.6 * grow + 0.45, fruit)
                sh.disc((nx, ny + 0.25), 0.34, _shade(fruit, -0.24))
            else:
                # 番茄：两三颗圆果挤在一起
                for k, (dx, dy) in enumerate(((0, 0), (-1.0, -0.75),
                                              (0.9, -1.15))):
                    r = (0.95 - k * 0.13) * grow + 0.30
                    sh.disc((nx + dx, ny + dy - 0.5), r,
                            fruit if k == 0 else _shade(fruit, -0.10 * k))
                sh.disc((nx - 0.3, ny - 1.0), 0.28, _shade(fruit, 0.28))


def _vine(sh, stage, leaf, fruit, h, shape, rnd):
    """藤本：贴地横走的藤 + 大叶，成熟时躺着瓜。"""
    run = min(11.0, 3.0 + stage * 1.15)
    x0 = 8.0 - run / 2.0
    spine = _bezier((x0, 0.9), (8.0, 1.6 + rnd() * 0.5),
                    (x0 + run, 1.0), 20)
    sh.stroke(spine, 0.42, 0.30, leaf)

    n = 1 + stage // 2
    for i in range(n):
        t = (i + 1) / float(n + 1)
        fi = t * (len(spine) - 1)
        j = min(len(spine) - 2, int(fi))
        f = fi - j
        bx, by = _lerp2(spine[j], spine[j + 1], f)
        side = -1 if i % 2 == 0 else 1
        # 叶长必须**跟着高度走**。之前写死了 2.4+0.35i，
        # 结果黄瓜整株只有 5 格高（叶子全趴在地上）。
        ln = h * (0.42 + 0.11 * i)
        ex = bx + side * (1.2 + ln * 0.32)
        ey = by + ln
        sh.blade(_bezier((bx, by), (bx + side * 1.2, by + ln * 0.5),
                         (ex, ey), 15),
                 0.88, leaf, taper=0.2 * side)

    if stage >= 4:
        grow = min(1.0, (stage - 3) / 4.0 + 0.28)
        if shape == "melon":
            # 瓜躺在地上（细长的更像黄瓜，扁圆的像冬瓜）
            sh.ellipse((6.3, 1.15), 2.0 * grow + 0.55, 1.15 * grow + 0.35, fruit,
                       rot=-0.08)
            if stage >= 6:
                sh.ellipse((10.3, 1.05), 1.6 * grow + 0.45,
                           0.95 * grow + 0.30, _shade(fruit, -0.10),
                           rot=0.06)
            sh.ellipse((6.0, 1.9), 0.8, 0.35, _shade(fruit, 0.24), rot=-0.2)
        else:
            sh.ellipse((6.8, 1.2), 1.5 * grow + 0.45, 1.0 * grow + 0.3, fruit)


def _fungus(sh, stage, leaf, fruit, h, shape, rnd):
    """菌：枯木 + 簸开的耳片。

    木耳本身是**近乎全黑**的，但 16×16 里一片黑就只剩一坨，认不出来。
    所以耳片要提亮到"深红褐"—— 既能看出是木耳，又还是暗色调。
    """
    wood = WOOD
    # 提亮耳片：木耳本身近乎全黑，但 16×16 里一片黑就只剩一坨。
    # 拉到"深红褐"—— 既能看出是木耳，又还是暗色调。
    ear = tuple(_clamp(c * 1.55 + 26) for c in fruit[:3])
    w = 2.2 + stage * 0.20
    sh.ellipse((8.0, 0.9), w, 0.80 + stage * 0.07, wood)
    # 木头的纹理
    for k in range(3):
        yy = 0.55 + k * 0.42
        sh.stroke(((8.0 - w + 0.4, yy), (8.0, yy + 0.06),
                   (8.0 + w - 0.4, yy)), 0.14, 0.14, _shade(wood, -0.26))

    if stage >= 2:
        grow = min(1.0, (stage - 1) / 6.0 + 0.25)
        # 耳片要**够大**才认得出来是木耳 —— 之前半径不到 1，
        # 整个方块只有 4 格高，看着像一块脏土。
        spots = [(-1.7, h * 0.30, 1.00), (1.5, h * 0.42, 0.85),
                 (0.0, h * 0.62, 0.62)]
        for (dx, dy, sc) in spots:
            if stage < 4 and sc < 0.9:
                continue
            r = (1.85 * sc) * grow + 0.55
            sh.ellipse((8.0 + dx, dy), r, r * 0.78, ear, rot=0.2 * dx)
            sh.ellipse((8.0 + dx - r * 0.3, dy - r * 0.28),
                       r * 0.38, r * 0.30, _shade(ear, 0.30))


PAINTERS = {
    "grass": _grass, "legume": _legume, "seedpod": _seedpod,
    "root": _root, "leafy": _leafy, "bush": _bush,
    "vine": _vine, "fungus": _fungus,
}

# 每种株型成熟时的最大高度（16 空间里的格）
MAX_HEIGHT = {
    "grass": 13.5, "legume": 11.5, "seedpod": 13.0, "root": 10.5,
    "leafy": 10.0, "bush": 12.5, "vine": 11.0, "fungus": 8.5,
}

# 株型 -> 叶色色相偏移（让同一套画法在不同作物上有区别）
HUE_SHIFT = {
    "grass": 0.020, "seedpod": 0.030, "root": -0.012,
    "leafy": -0.028, "legume": 0.012, "bush": -0.018,
    "vine": 0.004, "fungus": -0.060,
}

# 基准绿（取原版草丛的绿，放在 Minecraft 里不刺眼）
BASE_GREEN = (94, 148, 58)

# 菌类那截枯木的颜色。提成模块常量是因为色板构建也要用它
# （见 render 里对 fungus 的处理）。
WOOD = (132, 100, 66)

# 逐作物微调：(高度倍率, 叶色偏移修正)
TWEAK = {
    "corn":        (1.10, 0.0),
    "sorghum":     (1.08, 0.01),
    "rice":        (0.92, 0.02),
    "millet":      (0.90, 0.03),
    "chive":       (1.12, 0.00),
    "scallion":    (1.18, 0.00),
    "garlic":      (0.95, 0.01),
    "ginger":      (0.80, 0.02),
    "taro":        (1.00, 0.0),
    "sweet_potato": (0.92, 0.0),
    "chinese_yam": (0.95, 0.0),
    # 花生是**矮丛**，比其它豆科矮一大截
    "peanut":      (0.72, 0.0),
    "winter_melon": (1.05, 0.0),
    "cucumber":    (0.98, 0.0),
    "luffa":       (1.02, 0.0),
    "napa_cabbage": (1.05, 0.0),
    "spinach":     (0.95, -0.01),
    "celery":      (1.05, 0.0),
    "wood_ear":    (1.05, 0.0),
}


# ======================================================================
# 入口
# ======================================================================

def render(crop_id, palette, habit, stage, produce_kind=None):
    """画一张作物贴图。

    @param crop_id       作物 id（同时当作随机种子，保证每次生成一致）
    @param palette       收获物的配色（4 档）
    @param habit         株型（grass / legume / ...）
    @param stage         生长阶段 0~7
    @param produce_kind  收获物的图标种类，决定果实形状
    """
    if habit not in PAINTERS:
        habit = "bush"

    seed = _seed(crop_id)
    state = [seed]

    def rnd():
        """确定性伪随机 —— 同一种作物每次生成必须一模一样。"""
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return (state[0] >> 8) / float(0x7FFFFF)

    # ---- 叶色：基准绿 + 株型色相 + 按收获物深浅微调 + 降饱和 ----
    produce_main = tuple(palette[1]) if len(palette) > 1 else tuple(palette[0])
    leaf = _hue_shift(BASE_GREEN, HUE_SHIFT.get(habit, 0.0))
    dark_bias = (sum(BASE_GREEN) - sum(produce_main)) / 255.0 / 3.0
    leaf = _mix(leaf, _shade(BASE_GREEN, -0.30),
                max(0.0, min(0.45, dark_bias * 0.55)))
    # 降饱和：程序的绿容易"荧光"，往灰里混一点立刻变柔
    leaf = _soften(leaf, 0.20)

    # ---- 高度 ----
    h = MAX_HEIGHT.get(habit, 9.0)
    mult, hue_fix = TWEAK.get(crop_id, (1.0, 0.0))
    h *= mult
    if hue_fix:
        leaf = _hue_shift(leaf, hue_fix)
    # 前两阶就是个小芽，长到第 3 阶才开始像样
    t = stage / 7.0
    h *= (0.22 + 0.78 * (t ** 0.85))

    # ---- 果实颜色 ----
    # 太白的话调暖一点（否则在绿叶间像一块死白），
    # 再降一点饱和 —— 和叶子用同一套"柔和"标准，两者才配得上。
    fruit = _soften(_readable(produce_main), 0.12)

    sh = Sheet()
    PAINTERS[habit](sh, stage, leaf, fruit, h, _shape_of(produce_kind), rnd)
    img, edge = sh.resolve()

    # 色板：叶 + 果。菌类再加一条"木头"的色板 ——
    # 只给两条的话，木耳的棕褐色木头会被误判成（近乎全黑的）果色板，
    # 那一截木头就变成一块黑。
    ramps = [_pixel_ramp(leaf), _pixel_ramp(fruit)]
    if habit == "fungus":
        ramps.append(_pixel_ramp(WOOD))
    return _finish(img, edge, ramps)


def _readable(colour):
    """把"太白"的果实色调得能看。

    萝卜、蒜、白菜的主色接近纯白。直接画在绿叶中间就是一块死白 ——
    看着像长霉，而不是"露出来的白萝卜"。所以对近白色加一点暖调
    （往晒过的陶土色偏），白里带黄，立刻就成了根。
    """
    r, g, b = colour[:3]
    hi = max(r, g, b)
    lo = min(r, g, b)
    sat = 0.0 if hi == 0 else (hi - lo) / float(hi)
    if hi > 214 and sat < 0.22:
        return _mix(colour, (186, 160, 108), 0.36)
    return colour
