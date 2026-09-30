# -*- coding: utf-8 -*-
"""大型多方块机器的模型、方块状态与结构表。

    python tools/machine_models.py

四条设计原则
------------
**一、机器必须是一整块（不透视）**
    每一格都是**实心的整格**，水平方向铺满 16×16，格子之间没有任何缝隙；
    朝向邻格的面会被剔除，所以从外面永远只能看到最外层的表面。
    机器的样子靠**材质分区**表达（青石基座 / 木构件 / 铁箍 / 磨盘 /
    轴座 / 出料口 / 漏斗口），而不是靠挖空做浮雕 ——
    挖空的地方斜着看就能看进机器内部，那正是"透视"。

**二、UV 从贴图左上角开始取**
    以前所有面都写 `uv=[0,0,16,16]`，一条 2 像素宽的薄板会把整张贴图
    挤进 2 像素，看起来就是一道道条纹。现在按面的实际尺寸算 UV
    （1 贴图像素 = 1 模型像素），而且**从同一个角开始取** ——
    这样相邻方块的纹路是接起来的，看不出中间有一条方块边界。
    （曾经改成"居中取样"，结果每格都取贴图正中最漂亮的那块，
    纹路完全对不上，一格一格的特别明显。）

**三、模型按"格"生成，不按"种类"生成**
    以前同一种部件（比如 8 个底座格）只留一个模型，而每个格子的邻居
    不一样 —— 结果有些格子该有的面没生成，机器侧面是漏的。
    现在每格一个模型，面剔除按该格的真实邻接算，绝不漏面。

**四、机器用 AO**
    机器的构件大多是彼此分开的盒子（轴头、铁箍、漏斗），
    开着环境光遮蔽能让凹角自动压暗，层次一眼就出来。

结构
----
水磨（核心 = 正中那格，顶面是磨盘）::

    y=+1   [机体][机体][机体]
           [塔架][轴座][塔架]     <- 两侧外表面是水车接口
           [机体][机体][机体]
    y= 0   [基座][基座][基座]
           [基座][核心][基座]     <- 青石基座
           [基座][基座][基座]

    水车挂在塔架外侧那一格。

碾米机::

    y=+2           [料斗]          <- 顶面是漏斗口
    y=+1   [机箱][机箱][机箱]
           [机箱][机箱][摇柄]      <- 摇柄朝外
           [机箱][机箱][机箱]
    y= 0   [基座][基座][基座]
           [基座][核心][基座]
           [基座][基座][基座]
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food")
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                    "chinese_traditional_food")
NS = "chinese_traditional_food"

# 六个面与方向偏移（生成时按方向判断"这个面朝哪、是不是内部面"）
FACE_DIRS = {
    "down":  (0, -1, 0),
    "up":    (0, 1, 0),
    "north": (0, 0, -1),
    "south": (0, 0, 1),
    "west":  (-1, 0, 0),
    "east":  (1, 0, 0),
}
ALL_FACES = ("up", "down", "north", "south", "west", "east")
# 判断"这块盒子的面是否正好贴着格边界"时的容差
EPS = 0.001


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ======================================================================
# 结构定义
# ======================================================================

def water_mill_parts():
    """水磨：3×3×2 实心机体 + 正中抬起的磨盘塔。

    轮廓靠**高度差**做造型（两侧塔架 16 高、四角 12 高、正中再抬一格），
    而不是靠挖空 —— 挖空从斜着看就能看进机器内部，那就是"透视"。
    所有格子都是实心的，所以永远只能看到最外层表面。
    """
    parts = {}
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx or dz:
                parts[(dx, 0, dz)] = "footing"          # 基座层（实心 3×3）
                parts[(dx, 1, dz)] = "body_low"         # 起手先按四角（矮）
    # 四条边的中格抬高，做出"两侧塔架 + 前后墙"的高低差
    for dz in (-1, 1):
        parts[(0, 1, dz)] = "body"
    for dx in (-1, 1):
        parts[(dx, 1, 0)] = "tower"                     # 塔架（兼水车接口）
    parts[(0, 2, 0)] = "cap"                            # 正中抬起的磨盘塔
    return parts


def sheller_parts():
    """碾米机：3×3×2 实心机体 + 顶上的料斗。"""
    parts = {}
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx or dz:
                parts[(dx, 0, dz)] = "footing"
                parts[(dx, 1, dz)] = "body_low"
    # 四条边的中格抬高（四角仍是矮的），顶上再坐一个料斗
    for dz in (-1, 1):
        parts[(0, 1, dz)] = "body"
    parts[(-1, 1, 0)] = "body"
    parts[(1, 1, 0)] = "crank"                          # 朝外那一面装摇柄
    parts[(0, 2, 0)] = "hopper"
    return parts


STRUCTURES = {
    "water_mill": water_mill_parts(),
    "grain_sheller": sheller_parts(),
}


def _occupied(machine):
    cells = {(0, 0, 0)}
    cells.update(STRUCTURES[machine].keys())
    return cells


def _outward(cell, occupied):
    """这一格朝向机器外部的方向集合。"""
    return {name for name, (dx, dy, dz) in FACE_DIRS.items()
            if (cell[0] + dx, cell[1] + dy, cell[2] + dz) not in occupied}


# ======================================================================
# 构件构造
# ======================================================================

def _box_faces(x0, y0, z0, x1, y1, z1, cell, occupied):
    """这一块盒子的哪些面该画。

    只有当"邻居是本机的另一格"**并且**这块盒子贴着那条格边界时，
    那一面才算内部面被剔掉。所以细梁露在外面的部分照样有面，
    而贴着邻居的整格大板则会被完整剔除 —— 两者都对。
    """
    out = []
    for name, (dx, dy, dz) in FACE_DIRS.items():
        if (cell[0] + dx, cell[1] + dy, cell[2] + dz) in occupied:
            if name == "down" and y0 <= EPS:
                continue
            if name == "up" and y1 >= 16 - EPS:
                continue
            if name == "north" and z0 <= EPS:
                continue
            if name == "south" and z1 >= 16 - EPS:
                continue
            if name == "west" and x0 <= EPS:
                continue
            if name == "east" and x1 >= 16 - EPS:
                continue
        out.append(name)
    return out


def _uv_for(face, x0, y0, z0, x1, y1, z1):
    """按面的大小算 UV：1 贴图像素 = 1 模型像素，**从贴图左上角开始取**。

    这一点是"一体成型"的关键：每个方块的面都从 UV 的同一个角开始取，
    只要贴图本身可平铺，相邻方块接起来就是**连续的纹路**，
    看不出中间有一条方块边界。

    （之前改成"居中取样"是错的 —— 那样每格都取贴图正中最漂亮的那块，
    结果相邻方块的纹路完全对不上，一眼就是一格一格的。）
    """
    if face in ("up", "down"):
        w, h = x1 - x0, z1 - z0
    elif face in ("north", "south"):
        w, h = x1 - x0, y1 - y0
    else:
        w, h = z1 - z0, y1 - y0
    w = max(1.0, min(16.0, w))
    h = max(1.0, min(16.0, h))
    return [0, 0, w, h]


def box(tex, x0, y0, z0, x1, y1, z1, cell, occupied,
        skip=(), faces=None, uv=None):
    """一块构件。面为空时返回 None（调用方用 _add 跳过）。"""
    fs = list(faces) if faces is not None else \
        _box_faces(x0, y0, z0, x1, y1, z1, cell, occupied)
    fs = [f for f in fs if f not in skip]
    if not fs:
        return None
    out = {}
    for f in fs:
        out[f] = {"texture": tex,
                  "uv": uv if uv is not None else _uv_for(f, x0, y0, z0, x1, y1, z1)}
    return {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": out}


def _add(E, el):
    if el is not None:
        E.append(el)
    return E


# =================================================================# ======================================================================
# 构件
# ======================================================================
#
# 所有构件都是**实心的整格**（水平方向铺满 16×16）。这是"不透视"的
# 根本保证：格子之间没有任何缝隙，内部的面又被剔除，所以从外面永远
# 只能看到最外层的表面。
#
# 机器"长什么样"靠**材质分区**表达，而不是靠挖空做浮雕 ——
# 挖空的地方从斜着看就能看进机器内部，那正是用户说的"透视"。


def column(cell, occupied, bands, faces=None):
    """把一个整格竖着切成几段不同材质。

    `bands` 是 ``[(y0, y1, tex), ...]``，首尾相接铺满 0..16；
    段与段之间那两个面互相剔除，所以不会共面闪烁。

    `faces` 可以再按面覆盖材质（比如把朝外那一面换成轴座贴图）。
    """
    faces = faces or {}
    E = []
    n = len(bands)
    for i, (y0, y1, tex) in enumerate(bands):
        skip = []
        if i > 0:
            skip.append("down")       # 和下一段共面
        if i < n - 1:
            skip.append("up")
        fs = _box_faces(0, y0, 0, 16, y1, 16, cell, occupied)
        fs = [f for f in fs if f not in skip]
        if not fs:
            continue
        out = {}
        for f in fs:
            out[f] = {"texture": faces.get(f, tex),
                      "uv": _uv_for(f, 0, y0, 0, 16, y1, 16)}
        E.append({"from": [0, y0, 0], "to": [16, y1, 16], "faces": out})
    return E


# ----------------------------------------------------------------------
# 水磨
# ----------------------------------------------------------------------

def wm_footing(cell, occupied):
    """水磨基座：实心的一整格 —— 下半青石、上半木台。"""
    return column(cell, occupied, [(0, 5.0, "#stone"), (5.0, 16.0, "#wood")])


def wm_body_low(cell, occupied):
    """机体（矮）：木构 + 一圈铁箍，高度只有 12 —— 让轮廓有高低差。"""
    return column(cell, occupied, [(0, 3.0, "#wood"), (3.0, 5.0, "#iron"),
                                   (5.0, 12.0, "#wood")])


def wm_body(cell, occupied):
    """机体（高）：木构 + 铁箍。"""
    return column(cell, occupied, [(0, 3.0, "#wood"), (3.0, 5.0, "#iron"),
                                   (5.0, 16.0, "#wood")])


def wm_tower(cell, occupied):
    """塔架：木身 + 铁箍，**外侧面换成轴座贴图** —— 一眼看出水车装这儿。

    轴座不靠"挖进去"表现（挖了就漏），而是用一张带轴承孔的贴图贴在
    朝外那一面上；水车方块自己的轮毂也会往这边伸一截，两边就接上了。
    """
    out_x = "east" if cell[0] > 0 else "west"
    E = column(cell, occupied, [(0, 3.0, "#wood"), (3.0, 5.0, "#iron"),
                                (5.0, 16.0, "#wood")],
               faces={out_x: "#axle"})
    # 轴头：从内往外伸到格边界，和邻格水轮的轮毂接上
    if cell[0] > 0:
        _add(E, box("#iron", 12, 6.5, 6.0, 16, 9.5, 10.0, cell, occupied))
    else:
        _add(E, box("#iron", 0, 6.5, 6.0, 4, 9.5, 10.0, cell, occupied))
    return E


def wm_cap(cell, occupied):
    """正中抬起的磨盘塔：**顶面是磨盘石**。

    磨盘放在整台机器最高处 —— 埋在里面谁也看不见，
    而磨盘恰恰是水磨最有辨识度的那一块。
    """
    return column(cell, occupied,
                  [(0, 3.0, "#wood"), (3.0, 5.0, "#iron"),
                   (5.0, 12.0, "#wood"), (12.0, 16.0, "#millstone")],
                  faces={"up": "#millstone", "north": "#outlet"})


def wm_core(cell, occupied):
    """水磨核心（成形）：和其它基座格一样的实心块。

    核心埋在机器正中，从外面看不到 —— 它的作用是“放下这一块就长出整台机器”。
    """
    return wm_footing(cell, occupied)


def wm_core_bare(cell, occupied):
    """水磨核心（缺零件）：只有青石基座。"""
    return column(cell, occupied, [(0, 5.0, "#stone"), (5.0, 8.0, "#wood")])


# ----------------------------------------------------------------------
# 碾米机
# ----------------------------------------------------------------------

def gs_footing(cell, occupied):
    """碾米机基座：实心整格，下半石、上半木。"""
    return column(cell, occupied, [(0, 4.0, "#stone"), (4.0, 16.0, "#wood")])


def gs_body_low(cell, occupied):
    """机箱（矮）：让四角比四边低，做出高低差。"""
    return column(cell, occupied, [(0, 2.0, "#iron"), (2.0, 12.0, "#wood"),
                                   (12.0, 14.0, "#iron")])


def gs_body(cell, occupied):
    """机箱（高）：实心整格木料 + 上下两道铁箍。"""
    return column(cell, occupied, [(0, 2.0, "#iron"), (2.0, 14.0, "#wood"),
                                   (14.0, 16.0, "#iron")])


def gs_crank(cell, occupied):
    """带摇柄的那一面：机箱 + 朝外的曲柄（收在格内）。"""
    out_x = "east" if cell[0] > 0 else "west"
    E = column(cell, occupied, [(0, 2.0, "#iron"), (2.0, 14.0, "#wood"),
                                (14.0, 16.0, "#iron")],
               faces={out_x: "#crank"})
    if cell[0] > 0:
        _add(E, box("#iron", 12, 6.0, 7.0, 16, 10.0, 9.0, cell, occupied))
        _add(E, box("#wood", 13, 4.0, 4.5, 16, 13.0, 11.5, cell, occupied))
    else:
        _add(E, box("#iron", 0, 6.0, 7.0, 4, 10.0, 9.0, cell, occupied))
        _add(E, box("#wood", 0, 4.0, 4.5, 3, 13.0, 11.5, cell, occupied))
    return E


def gs_hopper(cell, occupied):
    """顶部料斗：实心整格，**顶面是漏斗口贴图**。

    不做中空的"斗壁" —— 中空就会从侧面看穿。用一张同心方框的漏斗口
    贴图表达"这里可以往里倒谷子"，效果一样，而且结实不漏。
    """
    return column(cell, occupied,
                  [(0, 4.0, "#wood"), (4.0, 14.0, "#hopper"), (14.0, 16.0, "#wood")],
                  faces={"up": "#hopper_top"})


def gs_core(cell, occupied):
    """碾米机核心（成形）：和其它基座格一样，但北面是出料口。"""
    return column(cell, occupied, [(0, 4.0, "#stone"), (4.0, 16.0, "#wood")],
                  faces={"north": "#outlet"})


def gs_core_bare(cell, occupied):
    """碾米机核心（缺零件）：只剩底座。"""
    return column(cell, occupied, [(0, 4.0, "#stone"), (4.0, 8.0, "#wood")])


PART_BUILDERS = {
    "water_mill": {
        "footing": wm_footing,
        "body_low": wm_body_low,
        "body": wm_body,
        "tower": wm_tower,
        "cap": wm_cap,
    },
    "grain_sheller": {
        "footing": gs_footing,
        "body_low": gs_body_low,
        "body": gs_body,
        "crank": gs_crank,
        "hopper": gs_hopper,
    },
}

CORE_BUILDERS = {
    "water_mill": {"core": wm_core, "core_bare": wm_core_bare},
    "grain_sheller": {"core": gs_core, "core_bare": gs_core_bare},
}


# ======================================================================
# 水车
# ======================================================================

def water_wheel(axis, frame):
    """水车：轮缘不转，辐条与叶片绕轮心转 —— 4 帧就是转动动画。

    转动用模型自带的 `rotation`（origin 在轮心），所以不需要任何渲染器。
    """
    a = frame * 22.5
    E = []

    def spin(x0, y0, z0, x1, y1, z1, tx):
        el = {
            "from": [x0, y0, z0], "to": [x1, y1, z1],
            "rotation": {"origin": [8.0, 8.0, 8.0], "axis": axis,
                         "angle": a, "rescale": False},
            "faces": {},
        }
        for f in ALL_FACES:
            if axis == "x":
                w, h = ((y1 - y0, z1 - z0) if f in ("up", "down")
                        else ((x1 - x0, y1 - y0) if f in ("north", "south")
                              else (z1 - z0, y1 - y0)))
            else:
                w, h = ((x1 - x0, z1 - z0) if f in ("up", "down")
                        else ((x1 - x0, y1 - y0) if f in ("north", "south")
                              else (z1 - z0, y1 - y0)))
            w = max(1.0, min(16.0, w))
            h = max(1.0, min(16.0, h))
            u0 = round((16.0 - w) / 2.0)
            v0 = round((16.0 - h) / 2.0)
            el["faces"][f] = {"texture": tx, "uv": [u0, v0, u0 + w, v0 + h]}
        E.append(el)

    def still(x0, y0, z0, x1, y1, z1, tx, faces):
        el = {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": {}}
        for f in faces:
            if f in ("up", "down"):
                w, h = (x1 - x0, z1 - z0)
            elif f in ("north", "south"):
                w, h = (x1 - x0, y1 - y0)
            else:
                w, h = (z1 - z0, y1 - y0)
            u0 = round((16.0 - w) / 2.0)
            v0 = round((16.0 - h) / 2.0)
            el["faces"][f] = {"texture": tx, "uv": [u0, v0, u0 + w, v0 + h]}
        E.append(el)

    if axis == "x":
        # 轮缘：八边形方环，沿 X 只有 3 像素厚
        for (y0, y1, z0, z1) in ((0.6, 15.4, 4.6, 6.2), (0.6, 15.4, 9.8, 11.4),
                                 (4.6, 6.2, 6.2, 9.8), (9.8, 11.4, 6.2, 9.8)):
            still(6.5, y0, z0, 9.5, y1, z1, "#wheel", ALL_FACES)
        # 贯通的轴：从格的一头穿到另一头，这样无论水车装在哪一侧，
        # 轴都能和水磨塔架伸出来的轴头在格边界上接上。
        still(0.0, 6.5, 6.5, 16.0, 9.5, 9.5, "#iron", ALL_FACES)
        # 辐条 + 叶片（跟着转）
        spin(6.5, 6.4, 2.0, 9.5, 9.6, 14.0, "#wheel")
        spin(6.5, 2.0, 6.4, 9.5, 14.0, 9.6, "#wheel")
        spin(6.5, 6.8, 6.8, 9.5, 9.2, 9.2, "#wheel")
        # 轮毂
        still(6.0, 6.0, 6.0, 10.0, 10.0, 10.0, "#iron", ["north", "south"])
    else:
        for (x0, x1, z0, z1) in ((0.6, 15.4, 4.6, 6.2), (0.6, 15.4, 9.8, 11.4),
                                 (4.6, 6.2, 6.2, 9.8), (9.8, 11.4, 6.2, 9.8)):
            still(x0, 6.5, z0, x1, 9.5, z1, "#wheel", ALL_FACES)
        still(6.5, 6.5, 0.0, 9.5, 9.5, 16.0, "#iron", ALL_FACES)
        spin(6.4, 6.5, 2.0, 14.0, 9.5, 14.0, "#wheel")
        spin(2.0, 6.5, 6.4, 14.0, 9.5, 9.6, "#wheel")
        spin(6.8, 6.5, 6.8, 9.2, 9.5, 9.2, "#wheel")
        still(6.0, 6.0, 6.0, 10.0, 10.0, 10.0, "#iron", ["west", "east"])
    return E


# ======================================================================
# 材质
# ======================================================================
TEX = {
    "particle": "%s:block/machine_stone" % NS,
    "stone": "%s:block/machine_stone" % NS,
    "wood": "%s:block/machine_wood" % NS,
    "iron": "%s:block/machine_iron" % NS,
    "wheel": "%s:block/machine_wheel" % NS,
    "millstone": "%s:block/machine_millstone" % NS,
    "hopper": "%s:block/machine_hopper" % NS,
    # 标记性贴图：贴在特定面上，用来"点出"交互位置。
    # 因为机器是实心的、不能挖洞，所以这些位置只能靠贴图表达。
    "axle": "%s:block/machine_axle" % NS,          # 水车轴座（朝外那一面）
    "crank": "%s:block/machine_crank" % NS,        # 摇柄那一面
    "hopper_top": "%s:block/machine_hopper_top" % NS,  # 料斗顶面（漏斗口）
    "outlet": "%s:block/machine_outlet" % NS,      # 出料口那一面
}


# ======================================================================
# 生成
# ======================================================================

STALE = (
    # 旧版按"部件种类"生成的模型（会漏面，已废弃）
    "water_mill_base", "water_mill_post", "water_mill_axle", "water_mill_mount",
    "grain_sheller_frame", "grain_sheller_pillar", "grain_sheller_panel",
    "grain_sheller_hopper_top",
    # 更早期的
    "water_mill_wheel", "water_mill_wheel_top", "water_mill_gearbox",
    "grain_sheller_hopper", "water_mill", "grain_sheller",
    "grain_sheller_crank0", "grain_sheller_crank1",
    "grain_sheller_crank2", "grain_sheller_crank3",
    "machine_hopper",
)


def _emit(name, elements):
    # ambientocclusion 用默认值 true：机器的构件大多是彼此分开的盒子，
    # 开了 AO 之后凹角会自动压暗，立柱、横梁、轴承座之间的层次一眼就出来了。
    # （摆在地上的菜是层层叠起来的，那种情况才要关掉 AO 免得出现脏缝。）
    _write(os.path.join(RES, "models", "block", "%s.json" % name), {
        "parent": "minecraft:block/block",
        "render_type": "cutout",
        "textures": TEX,
        "elements": elements,
    })
    return len(elements)


def build_models():
    out = os.path.join(RES, "models", "block")
    for stale in STALE:
        path = os.path.join(out, "%s.json" % stale)
        if os.path.exists(path):
            os.remove(path)
            print("removed stale model %s" % stale)

    total = 0
    for machine, table in STRUCTURES.items():
        cells = _occupied(machine)
        builders = PART_BUILDERS[machine]
        for cell, kind in sorted(table.items()):
            elements = builders[kind](cell, cells)
            if not elements:
                raise SystemExit("%s %s 没有生成任何构件" % (machine, kind))
            name = "%s_p%d%d%d" % (machine, cell[0] + 1, cell[1] + 1, cell[2] + 1)
            n = _emit(name, elements)
            print("model  %-26s %2d 构件  偏移(%d,%d,%d)  %s"
                  % (name, n, cell[0], cell[1], cell[2], kind))
            total += 1

        for kind, fn in CORE_BUILDERS[machine].items():
            name = "%s_%s" % (machine, kind)
            n = _emit(name, fn((0, 0, 0), cells))
            print("model  %-26s %2d 构件  %s" % (name, n, kind))
            total += 1

        # 兜底外观：结构表里没列出的偏移组合用它（正常玩不到）
        fallback = "machine_stone" if machine == "water_mill" else "machine_wood"
        fb = box("#stone" if machine == "water_mill" else "#wood",
                 0, 0, 0, 16, 16, 16, (0, 0, 0), set(), skip=("up", "down"))
        _emit("%s_fallback" % machine, [fb])
        total += 1

    for axis in ("x", "z"):
        for frame in range(4):
            _emit("water_wheel_%s_%d" % (axis, frame), water_wheel(axis, frame))
            total += 1
    print("model  water_wheel_x/z_0..3      8 帧")
    print("machine models: %d" % total)


def build_blockstates():
    out = os.path.join(RES, "blockstates")

    for machine, table in STRUCTURES.items():
        variants = {}
        for dx in range(4):
            for dy in range(4):
                for dz in range(4):
                    cell = (dx - 1, dy - 1, dz - 1)
                    if cell in table:
                        model = "%s:block/%s_p%d%d%d" % (NS, machine, dx, dy, dz)
                    else:
                        model = "%s:block/%s_fallback" % (NS, machine)
                    variants["dx=%d,dy=%d,dz=%d" % (dx, dy, dz)] = {"model": model}
        _write(os.path.join(out, "%s_part.json" % machine), {"variants": variants})
        print("blockstate %-22s %d variants（结构用 %d 个）"
              % ("%s_part.json" % machine, len(variants), len(table)))

    for machine in STRUCTURES:
        _write(os.path.join(out, "%s.json" % machine), {
            "variants": {
                "formed=false": {"model": "%s:block/%s_core_bare" % (NS, machine)},
                "formed=true": {"model": "%s:block/%s_core" % (NS, machine)},
            }
        })
        print("blockstate %-22s 2 variants (formed)" % ("%s.json" % machine))

    variants = {}
    for axis in ("x", "z"):
        for frame in range(4):
            variants["axis=%s,angle=%d" % (axis, frame)] = {
                "model": "%s:block/water_wheel_%s_%d" % (NS, axis, frame)
            }
    _write(os.path.join(out, "water_wheel.json"), {"variants": variants})
    print("blockstate %-22s %d variants" % ("water_wheel.json", len(variants)))


# ======================================================================
# 结构表（Java）
# ======================================================================

JAVA_HEADER = '''package com.ctf.chinese_traditional_food.common.block;

import java.util.List;

/**
 * 大型多方块机器的结构表。
 *
 * <p><b>本文件由 {@code tools/machine_models.py} 生成，请不要手改。</b>
 * 要调整机器形状请改那个脚本里的 {@code water_mill_parts()} /
 * {@code sheller_parts()}，模型、方块状态、结构表会一起同步。</p>
 *
 * <h2>为什么用"相对核心的偏移"描述结构</h2>
 * 每个部件方块都带 {@code dx/dy/dz} 三个属性记录它相对核心的偏移，
 * 所以部件能自己算出核心在哪（{@code 核心 = 部件位置 - 偏移}），
 * 不需要方块实体、不需要 ID 同步，两台机器挨着也不会串。
 *
 * <p>偏移范围是 -1~2，方块状态里编码成 0~3（值 = 偏移 + 1）。
 * 核心一律在结构最底层（{@code dy >= 0}），因为放置时下方是实地，
 * 结构往地下延伸就放不下来了。</p>
 */
public final class MachineStructure {

    /**
     * 结构中的一格。
     *
     * @param dx 相对核心的 X 偏移（-1 ~ 2）
     * @param dy 相对核心的 Y 偏移（0 ~ 2）
     * @param dz 相对核心的 Z 偏移（-1 ~ 2）
     */
    public record Part(int dx, int dy, int dz) {
        public int encodedX() {
            return this.dx + 1;
        }

        public int encodedY() {
            return this.dy + 1;
        }

        public int encodedZ() {
            return this.dz + 1;
        }
    }

'''


def build_java():
    parts = [JAVA_HEADER]
    for machine, table in STRUCTURES.items():
        lines = []
        for (dx, dy, dz) in sorted(table, key=lambda k: (k[1], k[2], k[0])):
            lines.append("            new Part(%d, %d, %d)" % (dx, dy, dz))
        parts.append("    /** %s 的全部部件位置（不含核心自身）。 */\n" % machine)
        parts.append("    public static final List<Part> %s = List.of(\n"
                     % machine.upper())
        parts.append(",\n".join(lines) + "\n    );\n\n")
    parts.append("    private MachineStructure() {}\n}\n")
    _write_text(os.path.join(JAVA, "common", "block", "MachineStructure.java"),
                "".join(parts))
    print("java   MachineStructure.java (%s)"
          % ", ".join("%s=%d" % (m, len(t)) for m, t in STRUCTURES.items()))


if __name__ == "__main__":
    build_models()
    build_blockstates()
    build_java()
