# -*- coding: utf-8 -*-
"""为「直接摆在地上的菜」生成三维方块模型与配套材质表。

    python tools/dish_models.py            # 写到 src/main/resources

思路（为什么这样做才"像原版"）
------------------------------
原版表达三维食物用的是**方块 + 方块状态 + 立方体模型**（蛋糕、南瓜派、
讲台、蜂巢都是这么干的），而不是给每道菜单独写渲染器。所以这里照同样路子：

1. 只注册**一个**方块 `placed_dish`，它有一个 `shape` 方块状态属性；
2. `shape` 决定用哪个三维模型（12 种器型：碗 / 盘 / 大盘 / 砂锅 / 鱼盘 /
   饺子 / 月饼 / 粽 / 糕片 / 酒盏 / 罐 / 方块）；
3. 模型是**手写的立方体元素**（不是平面贴图），所以有真正的体积、厚度、
   弧度与叠层；
4. 纹理由少量共享的 16x16 材质（陶、瓷、木、铁、食物）组成，
   每道菜靠**方块着色（BlockColor）**按自己的菜系配色上色 ——
   这也是原版给树叶 / 草 / 药水上色的同一套机制。

怎么"画圆"
----------
像素画里没法真的画圆。这里的做法是把一个圆**精确拆成 3 个互不重叠的矩形**
（中间一条通长，左右两条避开切角），拼出一个八边形：

        ┌───────┐
      ┌─┘       └─┐
      │           │     <- 中间矩形 + 左右两块 = 八边形
      └─┐       ┌─┘
        └───────┘

然后沿 Y **一层层收缩堆叠**（每层比下层小一点、高一截），
就得到了"圆润、有厚度"的盘沿与弧度。原版南瓜派、蛋糕边也是这种叠层手法。
这样既不超界、也不共面闪烁（共享的边界平面法线相反，背面剔除会处理掉一半），
更不需要任何旋转元素。

"模型多大就占多大"
------------------
`bounds(shape)` 会**从生成的元素里实测**包围盒极值，写进 `DishPlacement.BOUNDS`，
Java 端直接拿它建 `VoxelShape`。所以盘子只有薄薄一层、酒盏不会挡住整格 ——
占地范围永远和看得见的模型一致。
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food")
NS = "chinese_traditional_food"

# 方块状态属性的名字（要和 Java 里的 EnumProperty 一致）
PROPERTY = "shape"

# ======================================================================
# 12 种器型 -> 食物图标种类
# ======================================================================
# 键是方块状态的取值（小写），值是说明 + 对应 content_data 里的图标种类列表
SHAPES = {
    "bowl":       ["dish_soup", "congee", "noodles", "balls_bowl", "rice_dish", "mapo"],
    "plate":      ["dish_plate", "braised", "steamed_plate", "meatball", "braised_block"],
    "platter":    ["dish_whole", "cured_meat"],
    "pot":        ["dish_pot"],
    "fish_plate": ["dish_fish", "crab"],
    "dumpling":   ["dumpling"],
    "mooncake":   ["mooncake", "cookie"],
    "zongzi":     ["zongzi"],
    "cake_slice": ["cake_slice", "spring_roll"],
    "cup":        ["wine_cup"],
    "jar":        ["jar", "bottle"],
    "cube":       ["tofu_block"],
}

SHAPE_ORDER = ["bowl", "plate", "platter", "pot", "fish_plate", "dumpling",
               "mooncake", "zongzi", "cake_slice", "cup", "jar", "cube"]


def shape_for(kind):
    for shape, kinds in SHAPES.items():
        if kind in kinds:
            return shape
    return None


# ======================================================================
# 共享材质（16x16）
# ======================================================================
# 每种材质给一组亮度档。这几个色阶会被 tools/texture_machines.py
# 做成**平滑渐变**的 16x16 贴图（低频噪声，不是白噪点），
# 所以叠层看起来是"光滑的釉面 / 木纹"，而不是粗糙的噪点块。
MATERIALS = {
    # 陶（砂锅、粗碗）
    "dish_clay":  ((96, 60, 44), (122, 80, 58), (150, 104, 76), (176, 132, 100)),
    # 瓷（碗、盘、盏）
    "dish_porcelain": ((196, 200, 208), (222, 226, 232), (240, 244, 248), (170, 176, 186)),
    # 木（盘托、案面）
    "dish_wood":  ((120, 80, 44), (146, 100, 56), (170, 122, 70), (196, 148, 92)),
    # 铁（锅沿、箍）
    "dish_iron":  ((96, 100, 108), (124, 128, 136), (152, 156, 164), (78, 82, 90)),
    # 食物本体（会被方块着色染成该道菜的配色）
    "dish_food":  ((210, 210, 210), (232, 232, 232), (250, 250, 250), (188, 188, 188)),
    # 汁水 / 汤（也会被染色，但更暗一档）
    "dish_liquid": ((150, 150, 150), (176, 176, 176), (200, 200, 200), (126, 126, 126)),
}

# 食物色与汤汁色在 BlockTintSource 里的下标
TINT_FOOD = 0
TINT_LIQUID = 1


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


# ----------------------------------------------------------------------
# 立方体元素的便捷构造
# ----------------------------------------------------------------------

def box(x0, y0, z0, x1, y1, z1, texture, uv=None, tint=None, cull=None):
    """一个立方体。

    ``uv`` 缺省是整张贴图（[0,0,16,16]）；材质本身是平滑的，
    所以这样铺满不会露出接缝。``tint`` 是 tintindex（方块着色用）。
    """
    face = {"texture": texture, "uv": uv or [0, 0, 16, 16]}
    if tint is not None:
        face["tintindex"] = tint
    out = {}
    for f in ("up", "down", "north", "south", "west", "east"):
        d = dict(face)
        if cull is not None and f == cull:
            d["cullface"] = f
        out[f] = d
    return {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": out}


def _oct(cx, cz, rx, rz, y0, y1, texture, tint=None, cut=0.40, cull=None):
    """八边形切片：3 个**互不重叠**的矩形精确铺满一个八边形。

    中间一条通长（覆盖 |x|<=rx-cut，|z|<=rz），左右两条避开切角。
    三者只在边界平面上相接，法线相反，背面剔除后不会闪烁。
    这就是本文件的"画圆"基元。
    """
    ch = rx * cut      # X 方向的切角长度
    cv = rz * cut      # Z 方向的切角长度
    return [
        box(cx - rx + ch, y0, cz - rz, cx + rx - ch, y1, cz + rz,
            texture, tint=tint, cull=cull),
        box(cx - rx, y0, cz - rz + cv, cx - rx + ch, y1, cz + rz - cv,
            texture, tint=tint),
        box(cx + rx - ch, y0, cz - rz + cv, cx + rx, y1, cz + rz - cv,
            texture, tint=tint),
    ]


def _disc(cx, cz, r, y0, h, texture, tint=None, layers=4, shrink=0.42,
          cut=0.40, cull=None):
    """圆盘：沿 Y 收缩堆叠的八边形。

    最底下一层最大，往上逐层收小 —— 于是有了厚度、有了圆润的边，
    就像像素画里画球体的手法。每层精确相接（不重叠），
    相接处法线相反，不会闪烁。
    """
    out = []
    dh = h / layers
    for i in range(layers):
        t = i / (layers - 1) if layers > 1 else 0.0
        s = 1.0 - shrink * (t ** 1.55)          # 越往上收得越快，边更圆
        r_i = r * s
        out += _oct(cx, cz, r_i, r_i, y0 + i * dh, y0 + (i + 1) * dh,
                    texture, tint=tint, cut=cut, cull=cull if i == 0 else None)
    return out


def _disc_ellipse(cx, cz, rx, rz, y0, h, texture, tint=None, layers=4,
                  shrink=0.34, cut=0.40):
    """椭圆盘（鱼盘）：和圆盘一样，只是两个半径不同。"""
    out = []
    dh = h / layers
    for i in range(layers):
        t = i / (layers - 1) if layers > 1 else 0.0
        s = 1.0 - shrink * (t ** 1.55)
        out += _oct(cx, cz, rx * s, rz * s, y0 + i * dh, y0 + (i + 1) * dh,
                    texture, tint=tint, cut=cut)
    return out


def _ring(x0, z0, x1, z1, w, y0, y1, texture, tint=None):
    """方形环：上下两条通长，左右两条避开它们 —— 精确铺满，无重叠。"""
    return [
        box(x0, y0, z0, x1, y1, z0 + w, texture, tint=tint),
        box(x0, y0, z1 - w, x1, y1, z1, texture, tint=tint),
        box(x0, y0, z0 + w, x0 + w, y1, z1 - w, texture, tint=tint),
        box(x1 - w, y0, z0 + w, x1, y1, z1 - w, texture, tint=tint),
    ]


def _vessel(x0, z0, x1, z1, y0, h, texture, tint=None, layers=3, flare=0.9):
    """中空器皿的壁：一层层向外张开的方形环，做出"碗腹"的弧线。

    flare 是底层相对顶层的收缩量（0.8 = 底层比口沿窄 20%）。
    中空器皿用方形环而不是八边形 —— 原版的碗、炼药锅、花盆本来也是方的。
    """
    out = []
    cx = (x0 + x1) / 2.0
    cz = (z0 + z1) / 2.0
    hw = (x1 - x0) / 2.0          # 顶层半宽
    dh = h / layers
    for i in range(layers):
        t = i / (layers - 1) if layers > 1 else 0.0
        s = flare + (1.0 - flare) * t      # 从底(flare)张到顶(1.0)
        w = hw * s
        # 壁厚也随高度略变：底部厚实，口沿薄
        thick = 1.6 - 0.6 * t
        out += _ring(cx - w, cz - w, cx + w, cz + w, thick,
                     y0 + i * dh, y0 + (i + 1) * dh, texture, tint=tint)
    return out


# ----------------------------------------------------------------------
# 12 种器型的三维几何
# ----------------------------------------------------------------------

def geometry(shape):
    """返回 (elements, 是否需要食物色 tint)。

    约定：tint index 0 = 食物主体，1 = 汤汁 / 汁水，
    都会被方块着色染成该道菜的配色；无 tintindex 的面保持材质本色。
    """
    E = []

    # ------------------------------------------------------------------
    if shape == "bowl":
        # 粗瓷碗：圆底 + 三层张开的碗腹 + 口沿 + 汤面 + 料堆
        E += _disc(8, 8, 5.4, 0.0, 0.9, "#clay", layers=3, shrink=0.30)
        E += _vessel(2.3, 2.3, 13.7, 13.7, 0.9, 3.0, "#clay", layers=3, flare=0.80)
        # 口沿：一圈略宽的厚边，把碗口"收"住
        E += _ring(1.9, 1.9, 14.1, 14.1, 1.3, 3.9, 4.6, "#clay")
        # 汤面
        E += _oct(8, 8, 5.6, 5.6, 3.4, 4.0, "#liquid", tint=TINT_LIQUID, cut=0.30)
        # 料堆：三坨高低错开
        E += _oct(6.4, 6.6, 2.5, 2.4, 4.0, 5.3, "#food", tint=TINT_FOOD, cut=0.30)
        E += _oct(10.0, 9.6, 2.1, 2.2, 4.0, 6.1, "#food", tint=TINT_FOOD, cut=0.30)
        E += _oct(7.6, 10.6, 1.7, 1.5, 4.0, 4.9, "#food", tint=TINT_FOOD, cut=0.30)
        # 点缀（葱花 / 枸杞）
        E += [box(5.6, 5.3, 6.2, 7.0, 5.7, 7.2, "#liquid", tint=TINT_LIQUID)]
        E += [box(9.4, 6.1, 8.8, 10.6, 6.5, 9.8, "#liquid", tint=TINT_LIQUID)]
        return E, True

    # ------------------------------------------------------------------
    if shape == "plate":
        # 浅盘：四层收缩的圆盘 + 中间堆起来的菜 + 浇汁
        E += _disc(8, 8, 6.8, 0.0, 1.5, "#porcelain", layers=4, shrink=0.30)
        E += _disc(8, 8, 4.6, 1.5, 1.5, "#food", tint=TINT_FOOD, layers=3, shrink=0.36)
        E += _disc(8, 8, 3.0, 3.0, 1.2, "#food", tint=TINT_FOOD, layers=3, shrink=0.40)
        # 浇汁：盘心一圈更暗的汁水
        E += _oct(8, 8, 2.0, 2.0, 2.9, 3.2, "#liquid", tint=TINT_LIQUID, cut=0.34)
        # 配菜：三个小点
        for (dx, dz) in ((-3.6, -3.0), (3.4, -3.4), (-2.8, 3.6)):
            E += _oct(8 + dx, 8 + dz, 0.9, 0.9, 1.6, 2.3, "#food",
                      tint=TINT_FOOD, cut=0.34)
        return E, True

    # ------------------------------------------------------------------
    if shape == "platter":
        # 大盘 / 整只菜：木托两层 + 菜身两层 + 背脊 + 两侧腿
        E += _disc(8, 8, 7.4, 0.0, 1.2, "#wood", layers=3, shrink=0.24)
        E += _oct(8, 8, 6.2, 6.2, 1.2, 1.6, "#wood", cut=0.36)
        E += _disc(8, 8, 5.6, 1.6, 2.2, "#food", tint=TINT_FOOD, layers=4, shrink=0.32)
        E += _disc(8, 8, 3.6, 3.8, 1.0, "#food", tint=TINT_FOOD, layers=3, shrink=0.42)
        # 两片腿 / 翅
        E += _oct(5.2, 5.4, 2.0, 1.6, 1.6, 2.8, "#food", tint=TINT_FOOD, cut=0.30)
        E += _oct(10.8, 10.6, 2.0, 1.6, 1.6, 2.8, "#food", tint=TINT_FOOD, cut=0.30)
        # 油光
        E += _oct(8, 8, 4.4, 4.4, 3.7, 4.0, "#liquid", tint=TINT_LIQUID, cut=0.36)
        return E, True

    # ------------------------------------------------------------------
    if shape == "pot":
        # 砂锅：锅底 + 三层锅腹 + 铁锅沿 + 双耳 + 炖菜
        E += [box(1.4, 0.0, 1.4, 14.6, 1.0, 14.6, "#clay")]
        E += _vessel(1.0, 1.0, 15.0, 15.0, 1.0, 4.2, "#clay", layers=3, flare=0.84)
        E += _ring(0.6, 0.6, 15.4, 15.4, 1.1, 5.2, 6.0, "#iron")
        # 双耳
        E += [box(0.0, 3.2, 6.4, 1.0, 4.6, 9.6, "#clay")]
        E += [box(15.0, 3.2, 6.4, 16.0, 4.6, 9.6, "#clay")]
        # 炖菜：汤面 + 两坨料 + 点缀
        E += _oct(8, 8, 6.2, 6.2, 5.0, 5.6, "#liquid", tint=TINT_LIQUID, cut=0.32)
        E += _oct(6.6, 6.8, 2.4, 2.3, 5.6, 6.8, "#food", tint=TINT_FOOD, cut=0.30)
        E += _oct(9.8, 9.4, 2.2, 2.4, 5.6, 7.3, "#food", tint=TINT_FOOD, cut=0.30)
        E += [box(5.8, 6.8, 6.0, 7.2, 7.2, 7.4, "#liquid", tint=TINT_LIQUID)]
        return E, True

    # ------------------------------------------------------------------
    if shape == "fish_plate":
        # 鱼盘：长椭圆盘 + 身 / 尾 / 头 / 背鳍 / 眼
        E += _disc_ellipse(8, 8, 7.2, 4.6, 0.0, 1.1, "#porcelain", layers=3,
                           shrink=0.24)
        E += _disc_ellipse(8, 8, 4.8, 2.6, 1.1, 1.9, "#food", tint=TINT_FOOD,
                           layers=3, shrink=0.34)
        # 尾巴
        E += _oct(13.4, 8, 1.5, 1.8, 1.2, 2.6, "#food", tint=TINT_FOOD, cut=0.26)
        # 头
        E += _oct(3.4, 8, 1.7, 1.6, 1.4, 2.9, "#food", tint=TINT_FOOD, cut=0.28)
        # 背鳍
        E += _oct(8, 8, 3.4, 0.7, 2.9, 3.6, "#food", tint=TINT_FOOD, cut=0.30)
        # 眼与身上淋的汁
        E += [box(2.9, 2.5, 7.4, 3.7, 3.1, 8.6, "#liquid", tint=TINT_LIQUID)]
        E += [box(10.2, 3.0, 7.2, 11.4, 3.4, 8.8, "#liquid", tint=TINT_LIQUID)]
        E += [box(6.4, 3.0, 6.6, 8.0, 3.4, 9.4, "#liquid", tint=TINT_LIQUID)]
        return E, True

    # ------------------------------------------------------------------
    if shape == "dumpling":
        # 饺子：三只（底 + 鼓起的肚 + 顶上的褶），摆成三角居中
        for (ox, oz) in ((5.0, 5.0), (11.0, 5.0), (8.0, 11.0)):
            E += _oct(ox, oz, 2.3, 2.0, 0.2, 0.9, "#food",
                      tint=TINT_FOOD, cut=0.36)
            E += _oct(ox, oz, 1.9, 1.7, 0.9, 1.9, "#food",
                      tint=TINT_FOOD, cut=0.36)
            E += _oct(ox, oz, 1.2, 1.1, 1.9, 2.6, "#food",
                      tint=TINT_FOOD, cut=0.36)
            # 褶（两道细边）
            E += [box(ox - 1.3, 2.6, oz - 1.3, ox + 1.3, 2.9, oz - 0.9, "#food",
                      tint=TINT_FOOD)]
            E += [box(ox - 1.3, 2.6, oz + 0.9, ox + 1.3, 2.9, oz + 1.3, "#food",
                      tint=TINT_FOOD)]
        return E, True

    # ------------------------------------------------------------------
    if shape == "mooncake":
        # 月饼：方中带圆的厚饼（三层台阶）+ 顶面纹样 + 中心印记
        for (ox, oz) in ((4.9, 4.9), (11.3, 4.7), (8.1, 11.1)):
            E += _oct(ox, oz, 2.5, 2.3, 0.0, 0.7, "#food",
                      tint=TINT_FOOD, cut=0.34)
            E += _oct(ox, oz, 2.2, 2.0, 0.7, 2.0, "#food",
                      tint=TINT_FOOD, cut=0.34)
            # 顶面纹样：外圈 + 中心
            E += _oct(ox, oz, 1.5, 1.4, 2.0, 2.3, "#food",
                      tint=TINT_FOOD, cut=0.34)
            E += _oct(ox, oz, 0.7, 0.7, 2.3, 2.6, "#liquid",
                      tint=TINT_LIQUID, cut=0.34)
        return E, True

    # ------------------------------------------------------------------
    if shape == "zongzi":
        # 粽子：四棱锥（逐层收小的八边形）+ 腰绳 + 顶上露出的米
        for (ox, oz) in ((5.4, 8.0), (10.6, 7.8)):
            for i in range(6):
                s = 2.6 - i * 0.36
                y = 0.8 + i * 0.52
                E += _oct(ox, oz, s, s, y, y + 0.56, "#food",
                          tint=TINT_FOOD, cut=0.34)
            # 腰绳（十字两道）
            E += [box(ox - 2.7, 2.1, oz - 0.35, ox + 2.7, 2.5, oz + 0.35, "#wood")]
            E += [box(ox - 0.35, 2.1, oz - 2.7, ox + 0.35, 2.5, oz + 2.7, "#wood")]
            # 顶上露出的米
            E += _oct(ox, oz, 0.6, 0.6, 3.9, 4.3, "#food", tint=TINT_FOOD, cut=0.30)
        return E, True

    # ------------------------------------------------------------------
    if shape == "cake_slice":
        # 糕片 / 年糕：三片错开的厚片 + 每片顶上的点缀
        for i in range(3):
            y = 0.2 + i * 1.5
            ox = 6.9 + (i % 2) * 0.9
            oz = 6.7 + (i % 3) * 0.7
            E += _oct(ox, oz, 3.4, 3.2, y, y + 1.45, "#food",
                      tint=TINT_FOOD, cut=0.30)
            # 顶面高光边（薄薄一圈，显得切片光滑）
            E += _oct(ox, oz, 3.0, 2.8, y + 1.45, y + 1.6, "#food",
                      tint=TINT_FOOD, cut=0.30)
            # 点缀（枣 / 桂花）
            E += [box(ox - 1.8, y + 1.6, oz - 1.6, ox - 0.6, y + 2.1, oz - 0.4,
                      "#liquid", tint=TINT_LIQUID)]
            E += [box(ox + 0.6, y + 1.6, oz + 0.6, ox + 1.6, y + 2.0, oz + 1.6,
                      "#liquid", tint=TINT_LIQUID)]
        return E, True

    # ------------------------------------------------------------------
    if shape == "cup":
        # 酒盏：圈足 + 三层张开的盏壁 + 口沿 + 酒液 + 一朵花
        E += _disc(8, 8, 3.2, 0.0, 0.6, "#porcelain", layers=2, shrink=0.24)
        E += _vessel(5.6, 5.6, 10.4, 10.4, 0.6, 2.6, "#porcelain",
                     layers=3, flare=0.72)
        E += _ring(5.0, 5.0, 11.0, 11.0, 0.9, 3.2, 4.0, "#porcelain")
        E += _oct(8, 8, 3.4, 3.4, 2.9, 3.4, "#liquid", tint=TINT_LIQUID, cut=0.32)
        E += _oct(8, 8, 1.1, 1.1, 3.4, 3.7, "#food", tint=TINT_FOOD, cut=0.32)
        return E, True

    # ------------------------------------------------------------------
    if shape == "jar":
        # 罐 / 瓶：两层鼓腹 + 收口 + 盖布与系绳 + 腹上的标签
        E += _disc(8, 8, 3.8, 0.0, 0.8, "#clay", layers=2, shrink=0.24)
        E += _vessel(3.8, 3.8, 12.2, 12.2, 0.8, 3.4, "#clay", layers=3, flare=0.80)
        E += _vessel(5.0, 5.0, 11.0, 11.0, 4.2, 2.6, "#clay", layers=3, flare=0.62)
        E += _ring(5.4, 5.4, 10.6, 10.6, 0.9, 6.8, 7.6, "#clay")
        # 盖布
        E += _disc(8, 8, 3.3, 7.6, 0.7, "#wood", layers=3, shrink=0.30)
        # 系绳
        E += [box(4.4, 7.2, 7.4, 11.6, 7.7, 8.6, "#wood")]
        # 标签（一张贴在腹部的瓷牌）
        E += [box(6.2, 3.6, 3.9, 9.8, 5.6, 4.4, "#porcelain")]
        return E, False

    # ------------------------------------------------------------------
    if shape == "cube":
        # 方块食材（豆腐 / 卤味块）：一正两副，都带一点亮边
        E += _oct(5.2, 5.4, 2.7, 2.6, 0.0, 5.4, "#food", tint=TINT_FOOD, cut=0.26)
        E += _oct(5.2, 5.4, 2.3, 2.2, 5.4, 5.6, "#food", tint=TINT_FOOD, cut=0.26)
        E += _oct(11.0, 4.8, 2.3, 2.2, 0.0, 4.4, "#food", tint=TINT_FOOD, cut=0.26)
        E += _oct(11.0, 4.8, 1.9, 1.8, 4.4, 4.6, "#food", tint=TINT_FOOD, cut=0.26)
        E += _oct(8.0, 11.0, 2.4, 2.3, 0.0, 3.8, "#food", tint=TINT_FOOD, cut=0.26)
        E += _oct(8.0, 11.0, 2.0, 1.9, 3.8, 4.0, "#food", tint=TINT_FOOD, cut=0.26)
        # 卤汁挂边
        E += [box(4.2, 0.0, 4.4, 8.2, 0.5, 8.4, "#liquid", tint=TINT_LIQUID)]
        return E, True

    raise ValueError("未知器型: %s" % shape)


# ======================================================================
def bounds(shape):
    """从模型元素**实测**包围盒：[minX, minY, minZ, maxX, maxY, maxZ]。

    Java 端拿它建 VoxelShape —— 于是"模型多大就占多大"是**自动成立**的，
    改了模型不用再手动同步碰撞箱。单位是方块坐标 0~16。
    """
    elements, _ = geometry(shape)
    lo = [min(e["from"][i] for e in elements) for i in range(3)]
    hi = [max(e["to"][i] for e in elements) for i in range(3)]
    lo[1] = min(lo[1], 0.0)
    return [lo[0], lo[1], lo[2], hi[0], hi[1], hi[2]]


def build_models():
    """生成 12 个三维方块模型。"""
    out = os.path.join(RES, "models", "block")
    for shape in SHAPE_ORDER:
        elements, _tinted = geometry(shape)
        model = {
            "ambientocclusion": False,
            "textures": {
                "particle": "%s:block/dish_porcelain" % NS,
                "porcelain": "%s:block/dish_porcelain" % NS,
                "clay": "%s:block/dish_clay" % NS,
                "wood": "%s:block/dish_wood" % NS,
                "iron": "%s:block/dish_iron" % NS,
                "food": "%s:block/dish_food" % NS,
                "liquid": "%s:block/dish_liquid" % NS,
            },
            "elements": elements,
        }
        _write(os.path.join(out, "placed_dish_%s.json" % shape), model)
        print("model  placed_dish_%-11s %2d elements  bounds=[%s]"
              % (shape, len(elements),
                 ", ".join("%.1f" % v for v in bounds(shape))))


def build_blockstate():
    """生成 placed_dish 的 blockstate：shape=<值> -> 模型。

    注意变体键必须写成「属性名=取值」（这里是 shape=bowl），
    只写取值会被判定为未知属性，模型会 Missing。
    """
    variants = {}
    for shape in SHAPE_ORDER:
        variants["%s=%s" % (PROPERTY, shape)] = {
            "model": "%s:block/placed_dish_%s" % (NS, shape)
        }
    path = os.path.join(RES, "blockstates", "placed_dish.json")
    _write(path, {"variants": variants})
    print("blockstate placed_dish.json (%d variants)" % len(variants))


def build_shape_table():
    """输出 图标种类 -> 器型 的映射，供 Java 端与内容生成器使用。"""
    table = {}
    for shape, kinds in SHAPES.items():
        for kind in kinds:
            table[kind] = shape
    path = os.path.join(ROOT, "tools", "downloads", "dish_shapes.json")
    _write(path, table)
    print("shape table -> tools/downloads/dish_shapes.json (%d kinds)" % len(table))
    return table


if __name__ == "__main__":
    build_models()
    build_blockstate()
    build_shape_table()
