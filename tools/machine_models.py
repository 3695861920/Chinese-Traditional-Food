# -*- coding: utf-8 -*-
"""三台电力设备的方块模型与方块状态。

    python tools/machine_models.py

设计目标：像"机器"，不像"方块"
--------------------------------
一个 16×16×16 的实心立方体贴上花纹，读出来永远只是"一个方块"。
所以这三台机器都做成**有机器的剪影**：

* **支腿**——机身坐在四条腿上，底下是空的（真实机器的样子）；
* **机身内缩**——主体从 1..15，四周留出缝，轮廓不再是方块；
* **显著的工作部件露在外头**——
  发电机的炉膛/烟囱/铜线圈，磨粉机的磨盘，脱壳机的料斗与滚筒；
* 顶面的部件（烟囱、磨盘、料斗）会**伸出方块上边界**，视觉上明显更高。

关于"透视"
----------
之前用户说过不要透视 —— 那次的问题是**薄壳 + 中空内腔**，
斜着看就能看到方块背面。这里的做法不同：

* 机身是**实心体块**（闭合盒子），不存在内腔；
* 支腿之间的空隙是"机器下面"，本来就该看得见地面；
* 料斗是**敞口朝上**的，从上往下看进去是对的，侧面看仍是厚实的斗壁。

所以既像机器，又不会看到"方块的内侧"。所有部件都用实心盒子，不重叠。
"""

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food")
NS = "chinese_traditional_food"

FACES = ("up", "down", "north", "south", "west", "east")
SIDES = ("north", "south", "west", "east")
ALL_BUT_DOWN = ("up", "north", "south", "west", "east")


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _uv_for(face, x0, y0, z0, x1, y1, z1):
    """按面的大小算 UV，从贴图左上角开始取（配合可平铺材质不出现错位）。"""
    if face in ("up", "down"):
        w, h = x1 - x0, z1 - z0
    elif face in ("north", "south"):
        w, h = x1 - x0, y1 - y0
    else:
        w, h = z1 - z0, y1 - y0
    w = max(1.0, min(16.0, w))
    h = max(1.0, min(16.0, h))
    return [0, 0, w, h]


def box(faces, x0, y0, z0, x1, y1, z1, default=None):
    """实心盒子。

    `faces` 是逐面材质（只写需要特别的）；没写的用 `default`。
    """
    out = {}
    for f in FACES:
        tex = faces.get(f, default)
        if tex is None:
            continue
        out[f] = {"texture": tex, "uv": _uv_for(f, x0, y0, z0, x1, y1, z1)}
    if not out:
        raise ValueError("一个面都没有的盒子")
    return {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": out}


def oct_prism(cx, cz, r, y0, y1, tex, cut=0.30, faces=None, top=None):
    """八棱柱（沿 Y）：3 块实心盒子拼出一个八边形截面。

    像素画里画不出真圆，八边形是性价比最高的近似 ——
    磨盘、料斗口这类"圆的零件"都用它。
    """
    ch = r * cut
    parts = (
        (cx - r + ch, cz - r, cx + r - ch, cz + r),
        (cx - r, cz - r + ch, cx - r + ch, cz + r - ch),
        (cx + r - ch, cz - r + ch, cx + r, cz + r - ch),
    )
    out = []
    for (a0, b0, a1, b1) in parts:
        f = dict(faces or {})
        if top:
            f["up"] = top
        out.append(box(f or {"up": tex, "down": tex}, a0, y0, b0, a1, y1, b1,
                       default=tex))
    return out


def sq_ring(x0, z0, x1, z1, t, y0, y1, tex, top=None):
    """方形环（一圈厚壁，中间是通的）：料斗用。

    上下两条通长、左右两条避开它们 —— 段与段不重叠、不共面。
    """
    f_top = top or tex
    out = [
        box({"up": f_top}, x0, y0, z0, x1, y1, z0 + t, default=tex),
        box({"up": f_top}, x0, y0, z1 - t, x1, y1, z1, default=tex),
        box({"up": f_top}, x0, y0, z0 + t, x0 + t, y1, z1 - t, default=tex),
        box({"up": f_top}, x1 - t, y0, z0 + t, x1, y1, z1 - t, default=tex),
    ]
    return out


def legs(spread, h, size, tex, inner=None):
    """四条支腿。spread = 腿心到边界的距离；size = 腿宽的一半。"""
    out = []
    for (cx, cz) in ((spread, spread), (16.0 - spread, spread),
                     (spread, 16.0 - spread), (16.0 - spread, 16.0 - spread)):
        out.append(box({}, cx - size, 0.0, cz - size, cx + size, h, cz + size,
                       default=tex))
        # 脚垫
        out.append(box({}, cx - size - 0.6, 0.0, cz - size - 0.6,
                       cx + size + 0.6, 1.2, cz + size + 0.6,
                       default=inner or tex))
    return out


# ======================================================================
# 熔炉发电机
# ======================================================================

def furnace_generator():
    """熔炉发电机：四条腿撑起的火炉 —— 炉身 + 炉门 + 铜线圈 + 三个烟囱。"""
    E = []
    # 支腿
    E += legs(spread=2.4, h=3.2, size=1.3, tex="#iron", inner="#stone")

    # 炉身：实心块，四周从 1 到 15（不是整格）
    E.append(box({"down": "#stone"}, 1.0, 3.2, 1.0, 15.0, 12.4, 15.0,
                 default="#stone"))

    # 两侧的铜线圈：凸出炉身一点，像真的绕组
    for y0 in (5.0, 7.4, 9.8):
        E.append(box({}, 0.2, y0, 1.6, 1.0, y0 + 1.6, 14.4, default="#coil"))
        E.append(box({}, 15.0, y0, 1.6, 15.8, y0 + 1.6, 14.4, default="#coil"))

    # 顶板
    E.append(box({"up": "#iron"}, 0.6, 12.4, 0.6, 15.4, 13.6, 15.4,
                 default="#iron"))

    # 炉门：正面一块凸出的框 + 里面的炉栅
    E.append(box({}, 2.2, 4.4, 0.2, 13.8, 11.6, 1.2, default="#iron"))
    E.append(box({"north": "#grate"}, 3.4, 5.6, 0.0, 12.6, 10.4, 0.3,
                 default="#iron"))
    # 门闩
    E.append(box({}, 7.2, 10.4, 0.0, 8.8, 12.0, 0.6, default="#iron"))

    # 三个烟囱（伸出方块上边界，视觉上明显更高）
    for i in range(3):
        x = 3.0 + i * 4.0
        E.append(box({}, x, 13.6, 3.2, x + 2.4, 19.0, 6.4, default="#iron"))
        E.append(box({}, x - 0.6, 19.0, 2.6, x + 3.0, 20.0, 7.0,
                     default="#stone"))

    # 侧面的压力表
    E.append(box({"south": "#coil"}, 6.6, 8.0, 15.0, 9.4, 10.6, 15.8,
                 default="#coil"))
    return E


# ======================================================================
# 电动磨粉机
# ======================================================================

def electric_mill():
    """电动磨粉机：四条腿 + 电机机身 + 顶上一大一小两扇磨盘 + 出料口。"""
    E = []
    E += legs(spread=2.4, h=3.0, size=1.3, tex="#iron", inner="#stone")

    # 机身
    E.append(box({"down": "#iron"}, 1.2, 3.0, 1.2, 14.8, 10.6, 14.8,
                 default="#iron"))
    # 机身正面的散热百叶
    E.append(box({"north": "#vent"}, 2.6, 4.4, 0.4, 13.4, 9.6, 1.2,
                 default="#iron"))
    # 机身上的铁箍
    for y0 in (3.0, 9.4):
        E.append(box({}, 0.8, y0, 0.8, 15.2, y0 + 1.4, 15.2, default="#iron"))

    # 下磨盘（八棱柱）
    E += oct_prism(8.0, 8.0, 6.6, 10.6, 13.0, "#millstone", top="#millstone")
    # 上磨盘：小一圈、再高一层
    E += oct_prism(8.0, 8.0, 4.6, 13.0, 15.4, "#millstone", top="#millstone")
    # 中心立轴
    E.append(box({}, 7.0, 15.4, 7.0, 9.0, 17.6, 9.0, default="#iron"))
    # 轴顶的传动轮
    E.append(box({}, 6.0, 17.6, 6.0, 10.0, 18.6, 10.0, default="#coil"))

    # 进料斗：机身背面上的一个小方斗
    E.append(box({}, 5.4, 10.6, 12.6, 10.6, 14.0, 15.6, default="#hopper"))
    E.append(box({"up": "#hopper"}, 5.0, 14.0, 12.2, 11.0, 14.6, 16.0,
                 default="#hopper"))

    # 出料口：正面下方伸出来的一个斜槽
    E.append(box({}, 5.0, 3.4, 1.0, 11.0, 5.4, 3.4 + 0.1, default="#hopper"))
    E.append(box({}, 5.0, 2.6, 0.2, 11.0, 4.6, 1.6, default="#hopper"))
    return E


# ======================================================================
# 电动脱壳机
# ======================================================================

def electric_sheller():
    """电动脱壳机：四条腿 + 机身 + 敞口料斗 + 侧面电机 + 出料口。"""
    E = []
    E += legs(spread=2.4, h=3.0, size=1.3, tex="#iron", inner="#stone")

    # 机身
    E.append(box({"down": "#iron"}, 1.2, 3.0, 1.2, 14.8, 11.0, 14.8,
                 default="#iron"))
    E.append(box({"north": "#vent"}, 2.6, 4.4, 0.4, 13.4, 10.0, 1.2,
                 default="#iron"))
    for y0 in (3.0, 9.8):
        E.append(box({}, 0.8, y0, 0.8, 15.2, y0 + 1.4, 15.2, default="#iron"))

    # 顶上的敞口料斗：三级方形环，从上往下看真的能看到斗里
    E += sq_ring(3.0, 3.0, 13.0, 13.0, 1.6, 11.0, 14.0, "#hopper")
    E += sq_ring(2.0, 2.0, 14.0, 14.0, 1.8, 14.0, 16.6, "#hopper",
                 top="#hopper")
    E += sq_ring(0.8, 0.8, 15.2, 15.2, 2.0, 16.6, 18.4, "#hopper",
                 top="#hopper")
    # 斗底的出料喉（伸进机身里）
    E.append(box({}, 6.2, 8.6, 6.2, 9.8, 11.2, 9.8, default="#hopper"))

    # 侧面的电机：圆柱 + 铜线圈
    E += oct_prism(15.6, 8.0, 2.6, 5.4, 11.0, "#iron", top="#coil")
    E.append(box({}, 15.4, 7.4, 6.6, 16.4, 9.0, 9.4, default="#coil"))

    # 出料口
    E.append(box({}, 4.6, 2.6, 0.2, 11.4, 4.8, 1.8, default="#hopper"))

    # 正面的检修盖（带铜把手）
    E.append(box({}, 4.0, 5.6, 0.2, 12.0, 8.4, 1.0, default="#iron"))
    E.append(box({}, 7.2, 7.0, 0.0, 8.8, 7.8, 0.4, default="#coil"))
    return E


# ======================================================================
# 大型机（"3×3 放大版"）
# ======================================================================
#
# 与小型机的区别（造型上）：
#
# * **没有支腿**：小型机坐在四条腿上、底下是空的；大型机是落地的一整台
#   机组，所以主体从 0 到 16 铺满整格 —— 也因此碰撞箱是完整的一格；
# * **多出来的部件**：双烟囱 / 双磨盘 / 双料斗、外置的配电箱与飞轮、
#   一圈加强筋与铆钉排 —— 体量感完全不一样，一眼能看出是升级版；
# * 仍然全部是**实心盒子**，不做薄壳中空，所以不会出现"透视"。

def large_furnace_generator():
    """大型熔炉发电机：落地机组 + 双炉膛 + 双烟囱 + 侧面配电箱与飞轮。"""
    E = []
    # 底座（含一圈加强筋）
    E.append(box({"down": "#stone"}, 0.0, 0.0, 0.0, 16.0, 2.0, 16.0,
                 default="#stone"))
    E.append(box({}, -0.4, 0.0, -0.4, 16.4, 1.0, 16.4, default="#iron"))

    # 主炉体
    E.append(box({"down": "#stone"}, 0.4, 2.0, 0.4, 15.6, 11.6, 15.6,
                 default="#stone"))
    # 上段收一点，形成台阶轮廓
    E.append(box({"up": "#iron"}, 1.0, 11.6, 1.0, 15.0, 13.4, 15.0,
                 default="#iron"))

    # 两侧的加强筋（三道）
    for y0 in (3.0, 5.6, 8.2):
        E.append(box({}, -0.5, y0, 0.8, 0.4, y0 + 2.0, 15.2, default="#iron"))
        E.append(box({}, 15.6, y0, 0.8, 16.5, y0 + 2.0, 15.2, default="#iron"))

    # 正面：两扇炉门并排（各自带炉栅与门闩）—— 双炉膛
    for i in range(2):
        x0 = 1.6 + i * 7.0
        E.append(box({}, x0, 3.4, -0.2, x0 + 6.4, 10.6, 0.8, default="#iron"))
        E.append(box({"north": "#grate"}, x0 + 0.9, 4.4, -0.4, x0 + 5.5, 9.6,
                     0.2, default="#iron"))
        E.append(box({}, x0 + 2.6, 9.6, -0.4, x0 + 3.8, 11.0, 0.2,
                     default="#iron"))

    # 双烟囱
    for cx in (4.4, 11.6):
        E.append(box({}, cx - 1.4, 13.4, 4.6, cx + 1.4, 20.6, 8.2,
                     default="#iron"))
        E.append(box({}, cx - 2.0, 20.6, 4.0, cx + 2.0, 21.8, 8.8,
                     default="#stone"))
        E.append(box({}, cx - 1.0, 21.8, 4.9, cx + 1.0, 22.4, 7.9,
                     default="#grate"))

    # 右侧配电箱 + 压力表
    E.append(box({}, 11.2, 4.0, 15.4, 15.2, 10.0, 16.6, default="#iron"))
    for y0 in (5.0, 6.8, 8.6):
        E.append(box({"south": "#coil"}, 12.0, y0, 16.4, 14.4, y0 + 1.2, 16.9,
                     default="#coil"))

    # 左侧飞轮（八棱柱）+ 皮带
    E += oct_prism(0.8, 8.0, 3.4, 5.0, 11.0, "#iron", top="#coil")
    E.append(box({}, 0.0, 7.4, 7.4, 0.4, 8.6, 8.6, default="#coil"))

    # 顶部散热片
    for i in range(4):
        z = 3.0 + i * 2.6
        E.append(box({}, 1.4, 13.4, z, 14.6, 14.4, z + 1.2, default="#vent"))
    return E


def large_electric_mill():
    """大型电动磨粉机：落地机组 + 上下双磨盘 + 环绕的传动轮 + 双出料槽。"""
    E = []
    E.append(box({"down": "#iron"}, 0.0, 0.0, 0.0, 16.0, 2.0, 16.0,
                 default="#iron"))
    E.append(box({}, -0.4, 0.0, -0.4, 16.4, 1.0, 16.4, default="#stone"))

    # 机身
    E.append(box({"down": "#iron"}, 0.4, 2.0, 0.4, 15.6, 9.6, 15.6,
                 default="#iron"))
    # 正面的散热百叶（整片，比小型机宽一倍）
    E.append(box({"north": "#vent"}, 1.4, 3.2, -0.2, 14.6, 8.6, 0.6,
                 default="#iron"))
    # 铁箍
    for y0 in (2.4, 9.0):
        E.append(box({}, 0.0, y0, 0.0, 16.0, y0 + 1.6, 16.0, default="#iron"))

    # 下磨盘
    E += oct_prism(8.0, 8.0, 7.4, 9.6, 12.4, "#millstone", top="#millstone")
    # 上磨盘
    E += oct_prism(8.0, 8.0, 5.4, 12.4, 15.2, "#millstone", top="#millstone")
    # 第三层小盘（大型机比小型机多一级）
    E += oct_prism(8.0, 8.0, 3.4, 15.2, 17.4, "#millstone", top="#millstone")
    # 中心立轴 + 传动轮
    E.append(box({}, 6.8, 17.4, 6.8, 9.2, 20.2, 9.2, default="#iron"))
    E.append(box({}, 5.4, 20.2, 5.4, 10.6, 21.4, 10.6, default="#coil"))

    # 环绕的两条传动轮（左右各一，八棱柱）
    E += oct_prism(0.8, 4.4, 2.6, 4.0, 9.0, "#iron", top="#coil")
    E += oct_prism(0.8, 11.6, 2.6, 4.0, 9.0, "#iron", top="#coil")

    # 进料斗：顶部大斗
    E += sq_ring(4.4, 10.0, 11.6, 16.0, 1.4, 9.6, 12.4, "#hopper")
    E += sq_ring(3.4, 9.0, 12.6, 16.0, 1.6, 12.4, 15.0, "#hopper",
                 top="#hopper")

    # 双出料槽
    for i in range(2):
        x0 = 1.2 + i * 7.6
        E.append(box({}, x0, 2.2, 0.0, x0 + 5.8, 4.4, 1.6, default="#hopper"))
        E.append(box({"north": "#hopper"}, x0 + 0.6, 3.0, -0.4, x0 + 5.2, 4.2,
                     0.2, default="#hopper"))
    return E


def large_electric_sheller():
    """大型电动脱壳机：落地机组 + 三层大料斗 + 双滚筒 + 外置电机与检修门。"""
    E = []
    E.append(box({"down": "#iron"}, 0.0, 0.0, 0.0, 16.0, 2.0, 16.0,
                 default="#iron"))
    E.append(box({}, -0.4, 0.0, -0.4, 16.4, 1.0, 16.4, default="#stone"))

    # 机身
    E.append(box({"down": "#iron"}, 0.4, 2.0, 0.4, 15.6, 10.0, 15.6,
                 default="#iron"))
    E.append(box({"north": "#vent"}, 1.4, 3.2, -0.2, 14.6, 9.0, 0.6,
                 default="#iron"))
    for y0 in (2.4, 9.4):
        E.append(box({}, 0.0, y0, 0.0, 16.0, y0 + 1.6, 16.0, default="#iron"))

    # 双滚筒：两个并排的八棱柱横在机身正面（脱壳的核心部件）
    for cx in (4.8, 11.2):
        E += oct_prism(cx, 1.6, 3.2, 4.4, 8.0, "#millstone", top="#coil")

    # 三层递增的大料斗
    E += sq_ring(4.0, 5.0, 12.0, 13.0, 1.5, 10.0, 13.0, "#hopper")
    E += sq_ring(2.6, 4.0, 13.4, 14.0, 1.8, 13.0, 16.0, "#hopper",
                 top="#hopper")
    E += sq_ring(1.0, 3.0, 15.0, 15.0, 2.0, 16.0, 19.0, "#hopper",
                 top="#hopper")
    # 斗底的出料喉（两根，对应双滚筒）
    for cx in (5.2, 10.8):
        E.append(box({}, cx - 1.4, 7.6, 6.4, cx + 1.4, 10.4, 9.6,
                     default="#hopper"))

    # 右侧外置电机
    E += oct_prism(15.8, 8.0, 3.0, 4.4, 10.4, "#iron", top="#coil")
    E.append(box({}, 15.4, 6.4, 5.6, 16.8, 8.0, 10.4, default="#coil"))

    # 双出料口
    for i in range(2):
        x0 = 1.6 + i * 7.0
        E.append(box({}, x0, 2.2, 0.0, x0 + 6.0, 4.6, 1.8, default="#hopper"))

    # 正面的检修门（带观察窗）
    E.append(box({}, 2.4, 4.6, -0.2, 13.6, 8.6, 0.4, default="#iron"))
    E.append(box({"north": "#grate"}, 5.0, 5.4, -0.4, 11.0, 7.8, 0.0,
                 default="#grate"))

    # 顶部排气口
    for cx in (3.6, 12.4):
        E.append(box({}, cx - 1.0, 19.0, 7.0, cx + 1.0, 20.6, 10.0,
                     default="#grate"))
    return E


# ======================================================================
# 材质与生成
# ======================================================================
TEX = {
    "particle": "%s:block/machine_iron" % NS,
    "stone": "%s:block/machine_stone" % NS,
    "iron": "%s:block/machine_iron" % NS,
    "millstone": "%s:block/machine_millstone" % NS,
    "grate": "%s:block/machine_grate" % NS,
    "vent": "%s:block/machine_vent" % NS,
    "coil": "%s:block/machine_coil" % NS,
    "hopper": "%s:block/machine_hopper" % NS,
    # 灶火系统
    "bamboo": "%s:block/machine_bamboo" % NS,
    "steam": "%s:block/machine_steam" % NS,
    # 锅里的熟食（不走方块着色 —— 锅具没有颜色属性，直接画成熟食色）
    "food": "%s:block/machine_cooked" % NS,
    # 器皿内壁 / 层缝的暗色
    "shadow": "%s:block/dish_shadow" % NS,
    # 电磁炉的顶面 / 面板（有通电与断电两版）
    "cookerTop": "%s:block/machine_cooker_top" % NS,
    "cookerTopOn": "%s:block/machine_cooker_top_on" % NS,
    "cookerPanel": "%s:block/machine_cooker_panel" % NS,
}

BUILDERS = {
    "furnace_generator": furnace_generator,
    "electric_mill": electric_mill,
    "electric_sheller": electric_sheller,
    "large_furnace_generator": large_furnace_generator,
    "large_electric_mill": large_electric_mill,
    "large_electric_sheller": large_electric_sheller,
}

# 灶火系统（炉灶 + 三件锅具）单独放在 stove_models.py 里 ——
# 它们的造型语言（砖台、竹笼、敞口锅）和机器差别很大，混在一处反而难读。
import stove_models  # noqa: E402

stove_models.bind(sys.modules[__name__])

BUILDERS.update({
    "stove": stove_models.stove,
    "wok": stove_models.wok,
    "steamer": stove_models.steamer,
    "soup_pot": stove_models.soup_pot,
})

# 哪些方块带一个额外的 "powered" 方块状态（并因此多一份模型）。
# 电磁炉就是这么做的：通电时顶面的线圈换成发光的那张。
# 值为 "通电模型里被替换掉的材质键 -> 替换成的新键"。
POWERED_BLOCKS = {
    "stove": {"cookerTop": "cookerTopOn"},
}

# 小型机（带腿）与大型机（落地）在方块状态上完全一样，都是 4 个朝向；
# 下面的 build_blockstates 会把 BUILDERS 里的每一项都写一份。

# 上一版（整块方块 / 多方块）留下来的孤儿模型
STALE = (
    "water_mill_core", "water_mill_core_bare", "grain_sheller_core",
    "grain_sheller_core_bare", "water_mill_fallback", "grain_sheller_fallback",
    "water_mill", "grain_sheller", "water_mill_part", "grain_sheller_part",
    "water_wheel", "machine_hopper",
)
for _m in ("water_mill", "grain_sheller"):
    for _x in range(4):
        for _y in range(4):
            for _z in range(4):
                STALE = STALE + ("%s_p%d%d%d" % (_m, _x, _y, _z),)
for _ax in ("x", "z"):
    for _f in range(4):
        STALE = STALE + ("water_wheel_%s_%d" % (_ax, _f),)


def build_models():
    out = os.path.join(RES, "models", "block")
    for stale in STALE:
        path = os.path.join(out, "%s.json" % stale)
        if os.path.exists(path):
            os.remove(path)

    total = 0
    for name, fn in BUILDERS.items():
        elements = fn()
        _write(os.path.join(out, "%s.json" % name), {
            "parent": "minecraft:block/block",
            # 不需要 cutout：所有材质都是不透明的，实心渲染更省
            "textures": TEX,
            "elements": elements,
        })
        total += 1
        # 带 powered 状态的方块：再写一份"通电版"模型，只换掉指定材质
        swaps = POWERED_BLOCKS.get(name)
        if swaps:
            on_tex = dict(TEX)
            for old, new in swaps.items():
                on_tex[old] = TEX[new]
            _write(os.path.join(out, "%s_on.json" % name), {
                "parent": "minecraft:block/block",
                "textures": on_tex,
                "elements": elements,
            })
            total += 1
    print("machine models: %d" % total)


def build_blockstates():
    out = os.path.join(RES, "blockstates")
    yrot = {"north": 0, "east": 90, "south": 180, "west": 270}
    for name in BUILDERS:
        variants = {}
        if name in POWERED_BLOCKS:
            # facing × powered 的**所有**组合都要列出来，漏一个就会
            # 在那种状态下模型直接 Missing。
            for facing, deg in yrot.items():
                for powered in ("false", "true"):
                    entry = {
                        "model": "%s:block/%s%s"
                                 % (NS, name, "_on" if powered == "true" else "")
                    }
                    if deg:
                        entry["y"] = deg
                    variants["facing=%s,powered=%s" % (facing, powered)] = entry
        else:
            for facing, deg in yrot.items():
                entry = {"model": "%s:block/%s" % (NS, name)}
                if deg:
                    entry["y"] = deg
                variants["facing=%s" % facing] = entry
        _write(os.path.join(out, "%s.json" % name), {"variants": variants})
        print("blockstate %-20s %d 朝向" % ("%s.json" % name, len(variants)))


if __name__ == "__main__":
    build_models()
    build_blockstates()
