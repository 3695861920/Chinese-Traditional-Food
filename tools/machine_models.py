# -*- coding: utf-8 -*-
"""大型多方块机器的模型、方块状态与结构表。

    python tools/machine_models.py

设计要点
--------
**一体成型**
    机器看起来必须是"一整块做出来的"，不能是几个方块拼起来。
    做法不是靠渲染黑科技，而是**干脆不生成内部面**：
    结构表摆完之后，每一格朝向"同一台机器的另一格"的那个面直接不写进模型。
    于是机器外壳上没有任何接缝，相邻方块之间的过渡也彻底消失
    —— 比依赖背面剔除更可靠（不挑贴图的透明通道，也不受区块边界影响）。

**水磨要能接水车**
    水磨本体只到磨盘和横轴为止，两侧各留一个**水车接口**（iron 轴座 + 轴承箍），
    玩家把「水车」放在接口外侧，水车泡在水里，水磨才会转。
    这样"动力"是看得见的实体，而不是凭空判定"旁边有水"。

**纹理要连得自然、像素要少**
    贴图统一由 `tools/texture_machines.py` 用**不超过 3 种颜色**画，
    并且图案周期必须整除 16（石缝 8、木板 4），所以任意两块相邻的同材质面
    都能无缝对接。没有逐像素噪点 —— 噪点既费像素又会在方块边界断掉。

布局（核心一律在结构最底层，`dy >= 0`，否则往地下延伸会导致无法放置）::

    水磨                                  手摇碾米机
    y=2   [柱][轴][柱]  <- 横轴与轴承座      y=2        [斗]
    y=1   [台][台][台]                     y=1   [柱][板][柱]
    y=0   [台][核][台]                     y=0   [架][架][架]
          [台][台][台]                            [架][核][架]
                                                  [架][架][架]

    水车放在 [轴] 的外侧一格（+X / -X / +Z / -Z 都行）。
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food")
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                    "chinese_traditional_food")
NS = "chinese_traditional_food"

# 六个面：为了生成时能按方向处理
FACE_DIRS = {
    "down":  (0, -1, 0),
    "up":    (0, 1, 0),
    "north": (0, 0, -1),
    "south": (0, 0, 1),
    "west":  (-1, 0, 0),
    "east":  (1, 0, 0),
}
UV_FULL = [0, 0, 16, 16]


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
# 结构定义：相对核心的偏移 -> 部件种类
# ======================================================================
# 偏移范围 -1..1（水平）/ 0..2（竖直），方块状态里编码成 0..3（值 = 偏移 + 1）。

def water_mill_parts():
    """水磨：3×3 石台（核心在正中）+ 横轴 + 两侧水车接口 + 两根立柱。"""
    parts = {}
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx == 0 and dz == 0:
                continue                         # 这一格是核心（磨盘）
            parts[(dx, 0, dz)] = "base"
    parts[(0, 1, 0)] = "axle"                    # 横轴过顶
    parts[(-1, 1, 0)] = "mount"                  # 左水车接口
    parts[(1, 1, 0)] = "mount"                   # 右水车接口
    parts[(0, 1, -1)] = "post"
    parts[(0, 1, 1)] = "post"
    return parts


def grain_sheller_parts():
    """脱壳机：3×3 木架（核心在正中）+ 四角立柱 + 四边机箱板 + 顶部料斗。"""
    parts = {}
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx == 0 and dz == 0:
                continue
            parts[(dx, 0, dz)] = "frame"
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx == 0 and dz == 0:
                continue                         # 正中留空，能直接看到核心
            parts[(dx, 1, dz)] = "pillar" if (dx and dz) else "panel"
    parts[(0, 2, 0)] = "hopper_top"
    return parts


STRUCTURES = {
    "water_mill": water_mill_parts(),
    "grain_sheller": grain_sheller_parts(),
}

# 水车接口允许挂水车的四个方向（相对接口格）
MOUNT_DIRECTIONS = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]


# ======================================================================
# 贴图键
# ======================================================================
# 只用少量材质：石 / 木 / 铁 / 水车 / 磨盘 / 料斗口。
# 全部由 texture_machines.py 用 <=3 种颜色画，且图案周期整除 16（可无缝平铺）。
TEX = {
    "particle": "%s:block/machine_stone" % NS,
    "stone": "%s:block/machine_stone" % NS,
    "wood": "%s:block/machine_wood" % NS,
    "iron": "%s:block/machine_iron" % NS,
    "wheel": "%s:block/machine_wheel" % NS,
    "millstone": "%s:block/machine_millstone" % NS,
    "hopper": "%s:block/machine_hopper" % NS,
}


def _faces_for(cell, occupied, override=None):
    """返回这一格"该画出来"的面。

    只要某个方向上是同一台机器的另一格，那个面就是内部面，直接不生成 ——
    机器因此是一整块，没有任何接缝。
    """
    if override is not None:
        return list(override)
    out = []
    for name, (dx, dy, dz) in FACE_DIRS.items():
        if (cell[0] + dx, cell[1] + dy, cell[2] + dz) not in occupied:
            out.append(name)
    return out


def cube(texture, faces, x0=0.0, y0=0.0, z0=0.0, x1=16.0, y1=16.0, z1=16.0,
         uv=UV_FULL, tint=None):
    """一个立方体，只生成指定的面。"""
    out = {}
    for f in faces:
        d = {"texture": texture, "uv": list(uv)}
        if tint is not None:
            d["tintindex"] = tint
        out[f] = d
    return {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": out}


# ----------------------------------------------------------------------
# 水磨的部件
# ----------------------------------------------------------------------

def water_mill_base(occupied, cell):
    """石台：整格石块，只画朝外的面。"""
    return [cube("#stone", _faces_for(cell, occupied))]


def water_mill_post(occupied, cell):
    """立柱：整格木柱，托住上面的横轴。"""
    return [cube("#wood", _faces_for(cell, occupied))]


def water_mill_axle(occupied, cell):
    """横轴格：木身 + 顶上一条横向铁轴（沿 X 贯穿）。"""
    E = [cube("#wood", _faces_for(cell, occupied))]
    # 铁轴：贴着顶面，沿 X 方向通长；沿 Y 用两块木轴承夹住
    E.append(cube("#iron", ["up", "north", "south"], 0, 14.2, 5.6, 16, 16, 10.4))
    E.append(cube("#wood", ["west", "east", "up"], 0, 12.2, 4.0, 3.0, 16, 12.0))
    E.append(cube("#wood", ["west", "east", "up"], 13.0, 12.2, 4.0, 16, 16, 12.0))
    return E


def water_mill_mount(occupied, cell):
    """水车接口：木身 + 朝外的铁轴座（轴头伸出去 2 像素，一眼看得出该挂水车）。

    轴座开在"和核心相反的一侧"，所以左右两个接口都是朝外的。
    """
    E = [cube("#wood", _faces_for(cell, occupied))]
    # 判断哪一侧朝外（远离核心 = X 偏移的符号）
    out_west = cell[0] > 0        # 位于核心右侧 -> 朝外是 +X(east)
    side = "east" if out_west else "west"
    x0, x1 = (16.0, 18.0) if out_west else (-2.0, 0.0)
    xa, xb = (14.0, 16.0) if out_west else (0.0, 2.0)
    # 轴头
    E.append(cube("#iron", ["up", "down", "north", "south", side],
                  x0, 6.6, 6.6, x1, 9.4, 9.4))
    # 轴承箍：一块贴着外立面的铁板
    E.append(cube("#iron", [side], min(xa, xb), 3.6, 3.6, max(xa, xb), 12.4, 12.4))
    return E


# ----------------------------------------------------------------------
# 脱壳机的部件
# ----------------------------------------------------------------------

def grain_sheller_frame(occupied, cell):
    return [cube("#wood", _faces_for(cell, occupied))]


def grain_sheller_pillar(occupied, cell):
    """角柱：铁箍加固的木柱。"""
    E = [cube("#wood", _faces_for(cell, occupied))]
    for y0 in (1.6, 12.4):
        E.append(cube("#iron", ["north", "south", "west", "east"],
                      0.0, y0, 0.0, 16.0, y0 + 1.6, 16.0))
    return E


def grain_sheller_panel(occupied, cell):
    """机箱板：木板 + 上下铁箍，中间一条竖缝。"""
    E = [cube("#wood", _faces_for(cell, occupied))]
    for y0 in (1.6, 12.4):
        E.append(cube("#iron", ["north", "south", "west", "east"],
                      0.0, y0, 0.0, 16.0, y0 + 1.6, 16.0))
    return E


def grain_sheller_hopper_top(occupied, cell):
    """顶部料斗：木身 + 顶面掏出的漏斗口。"""
    E = [cube("#wood", _faces_for(cell, occupied))]
    # 漏斗口：顶面四个方向的斜板，围出一个上宽下窄的方口
    E.append(cube("#hopper", ["north"], 4.0, 10.0, 3.0, 12.0, 16.0, 5.0))
    E.append(cube("#hopper", ["south"], 4.0, 10.0, 11.0, 12.0, 16.0, 13.0))
    E.append(cube("#hopper", ["west"], 3.0, 10.0, 5.0, 5.0, 16.0, 11.0))
    E.append(cube("#hopper", ["east"], 11.0, 10.0, 5.0, 13.0, 16.0, 11.0))
    # 口的底部（能看进去）
    E.append(cube("#hopper", ["up"], 5.0, 10.0, 5.0, 11.0, 10.4, 11.0))
    # 口沿一圈铁箍
    E.append(cube("#iron", ["up"], 2.4, 15.2, 2.4, 13.6, 16.0, 13.6))
    return E


PART_BUILDERS = {
    "water_mill": {
        "base": water_mill_base,
        "post": water_mill_post,
        "axle": water_mill_axle,
        "mount": water_mill_mount,
    },
    "grain_sheller": {
        "frame": grain_sheller_frame,
        "pillar": grain_sheller_pillar,
        "panel": grain_sheller_panel,
        "hopper_top": grain_sheller_hopper_top,
    },
}


# ----------------------------------------------------------------------
# 核心（formed=true 是完整机器，formed=false 是"缺零件"）
# ----------------------------------------------------------------------

def water_mill_core(occupied, cell):
    """水磨核心：上下两扇磨盘 + 中心轴 + 前侧出料槽。"""
    E = [cube("#stone", _faces_for(cell, occupied))]
    # 上磨盘：比整格略小的圆盘（用八边形近似），顶面是磨纹
    E.append(cube("#millstone", ["up"], 1.6, 15.0, 1.6, 14.4, 16.0, 14.4))
    E.append(cube("#stone", ["north", "south", "west", "east"],
                  1.6, 13.4, 1.6, 14.4, 15.0, 14.4))
    # 中心轴
    E.append(cube("#iron", ["up", "north", "south", "west", "east"],
                  6.8, 16.0, 6.8, 9.2, 18.0, 9.2))
    # 出料槽：前侧一块斜出的小木槽
    E.append(cube("#wood", ["up", "north"], 4.6, 13.6, -3.0, 11.4, 15.2, 1.6))
    return E


def water_mill_core_bare(occupied, cell):
    """水磨核心（缺零件）：只剩底座与中心轴，一眼能看出该补什么。"""
    E = [cube("#stone", _faces_for(cell, occupied), 0.0, 0.0, 0.0, 16.0, 12.0, 16.0)]
    E.append(cube("#iron", ["up", "north", "south", "west", "east"],
                  6.8, 12.0, 6.8, 9.2, 15.0, 9.2))
    return E


def grain_sheller_core(occupied, cell):
    """脱壳机核心：木机身 + 侧面摇柄 + 前侧出料口。"""
    E = [cube("#wood", _faces_for(cell, occupied))]
    # 铁箍两圈
    for y0 in (2.0, 9.0):
        E.append(cube("#iron", ["north", "south", "west", "east"],
                      0.0, y0, 0.0, 16.0, y0 + 1.6, 16.0))
    # 摇柄：轴 + 弯柄 + 握把，全部收在格子内（伸出去会和机箱板穿插）
    E.append(cube("#iron", ["east", "up", "down", "north", "south"],
                  13.0, 5.6, 7.0, 16.0, 8.8, 9.0))
    E.append(cube("#iron", ["up", "east", "north", "south"],
                  11.4, 8.0, 7.0, 16.0, 9.2, 9.0))
    E.append(cube("#wood", ["east", "north", "south"],
                  11.6, 4.8, 6.6, 13.0, 11.6, 9.4))
    return E


def grain_sheller_core_bare(occupied, cell):
    """脱壳机核心（缺零件）：光板木箱，摇柄还没装上。"""
    E = [cube("#wood", _faces_for(cell, occupied), 0.0, 0.0, 0.0, 16.0, 10.0, 16.0)]
    E.append(cube("#iron", ["up"], 1.0, 10.0, 1.0, 15.0, 10.4, 15.0))
    return E


CORE_BUILDERS = {
    "water_mill": {"core": water_mill_core, "core_bare": water_mill_core_bare},
    "grain_sheller": {"core": grain_sheller_core,
                      "core_bare": grain_sheller_core_bare},
}


# ----------------------------------------------------------------------
# 水车（独立方块，挂在接口外侧）
# ----------------------------------------------------------------------

def water_wheel(axis, frame):
    """水车：轮缘不动，只有辐条与叶片转 —— 4 帧就是转动动画。

    水车是一块薄轮子（厚度 3 像素），轴沿 `axis`：
    * axis == "x" -> 轮面在 YZ 平面（挂在东西两侧的接口上）；
    * axis == "z" -> 轮面在 XY 平面（挂在南北两侧的接口上）。

    元素旋转用模型自带的 `rotation`（绕轴，origin 在轮心），
    所以不需要任何渲染器就有转动效果。
    """
    a = frame * 22.5
    E = []

    def spin(x0, y0, z0, x1, y1, z1, tx):
        rot = {"origin": [8.0, 8.0, 8.0], "axis": axis, "angle": a,
               "rescale": False}
        el = cube(tx, ["up", "down", "north", "south", "west", "east"],
                  x0, y0, z0, x1, y1, z1)
        el["rotation"] = rot
        E.append(el)

    if axis == "x":
        # 轮缘：一个外径 15、内径 11 的方环（沿 X 只有 3 像素厚）
        for (y0, y1, z0, z1) in ((0.6, 15.4, 5.4, 6.6), (0.6, 15.4, 9.4, 10.6),
                                 (5.4, 6.6, 6.6, 9.4), (9.4, 10.6, 6.6, 9.4)):
            E.append(cube("#wheel", ["north", "south", "up", "down",
                                     "west", "east"], 6.5, y0, z0, 9.5, y1, z1))
        # 四根辐条 + 叶片（跟着转）
        spin(6.5, 7.0, 7.0, 9.5, 9.0, 9.0, "#wheel")
        for (y0, y1, z0, z1) in ((0.6, 15.4, 6.4, 9.6),):
            spin(6.0, y0, z0, 10.0, y1, z1, "#wheel")
        spin(6.0, 6.4, 0.6, 10.0, 9.6, 15.4, "#wheel")
        # 轮毂
        E.append(cube("#iron", ["north", "south"], 6.5, 6.6, 6.6, 9.5, 9.4, 9.4))
    else:
        for (x0, x1, z0, z1) in ((0.6, 15.4, 5.4, 6.6), (0.6, 15.4, 9.4, 10.6),
                                 (5.4, 6.6, 6.6, 9.4), (9.4, 10.6, 6.6, 9.4)):
            E.append(cube("#wheel", ["north", "south", "up", "down",
                                     "west", "east"], x0, 6.5, z0, x1, 9.5, z1))
        spin(7.0, 6.5, 7.0, 9.0, 9.5, 9.0, "#wheel")
        spin(0.6, 6.0, 6.4, 15.4, 10.0, 9.6, "#wheel")
        spin(6.4, 6.0, 0.6, 9.6, 10.0, 15.4, "#wheel")
        E.append(cube("#iron", ["west", "east"], 6.6, 6.5, 6.6, 9.4, 9.5, 9.4))
    return E


# ======================================================================
# 生成
# ======================================================================

def _occupied(machine):
    """这台机器占用的全部格子（含核心）。"""
    cells = {(0, 0, 0)}
    cells.update(STRUCTURES[machine].keys())
    return cells


def build_models():
    out = os.path.join(RES, "models", "block")

    # 清掉上一版留下的孤儿模型，免得越积越多
    for stale in ("water_mill_wheel", "water_mill_wheel_top", "water_mill_gearbox",
                  "grain_sheller_hopper", "water_mill", "grain_sheller",
                  "grain_sheller_crank0", "grain_sheller_crank1",
                  "grain_sheller_crank2", "grain_sheller_crank3"):
        path = os.path.join(out, "%s.json" % stale)
        if os.path.exists(path):
            os.remove(path)
            print("removed stale model %s" % stale)

    total = 0
    for machine, builders in PART_BUILDERS.items():
        cells = _occupied(machine)
        for cell, kind in sorted(STRUCTURES[machine].items()):
            elements = builders[kind](cells, cell)
            model = {
                "parent": "minecraft:block/block",
                "render_type": "cutout",
                                "textures": TEX,
                "elements": elements,
            }
            name = "%s_%s" % (machine, kind)
            _write(os.path.join(out, "%s.json" % name), model)
            print("model  %-28s %2d elements" % (name, len(elements)))
            total += 1

    for machine, builders in CORE_BUILDERS.items():
        cells = _occupied(machine)
        for kind, fn in builders.items():
            elements = fn(cells, (0, 0, 0))
            name = "%s_%s" % (machine, kind)
            _write(os.path.join(out, "%s.json" % name), {
                "parent": "minecraft:block/block",
                "render_type": "cutout",
                                "textures": TEX,
                "elements": elements,
            })
            print("model  %-28s %2d elements" % (name, len(elements)))
            total += 1

    # 水车：2 个轴向 × 4 帧
    for axis in ("x", "z"):
        for frame in range(4):
            elements = water_wheel(axis, frame)
            name = "water_wheel_%s_%d" % (axis, frame)
            _write(os.path.join(out, "%s.json" % name), {
                "parent": "minecraft:block/block",
                "render_type": "cutout",
                                "textures": TEX,
                "elements": elements,
            })
            total += 1
    print("model  water_wheel_x/z_0..3        8 frames")
    print("machine models: %d" % total)


def build_blockstates():
    out = os.path.join(RES, "blockstates")

    # 部件：dx/dy/dz 各 0..3 —— 把全部组合都列出来，没用到的一律指向同层通用外观。
    # （引擎会尝试解析方块的全部状态组合，缺一个就在日志里刷 "Missing model"。）
    for machine, parts in STRUCTURES.items():
        fallback_kind = "base" if machine == "water_mill" else "frame"
        variants = {}
        for dx in range(4):
            for dy in range(4):
                for dz in range(4):
                    kind = parts.get((dx - 1, dy - 1, dz - 1))
                    model = ("%s:block/%s_%s" % (NS, machine, kind)
                             if kind else "%s:block/%s_%s" % (NS, machine, fallback_kind))
                    variants["dx=%d,dy=%d,dz=%d" % (dx, dy, dz)] = {"model": model}
        _write(os.path.join(out, "%s_part.json" % machine), {"variants": variants})
        print("blockstate %-24s %d variants（结构用 %d 个）"
              % ("%s_part.json" % machine, len(variants), len(parts)))

    # 核心：formed 两种外观
    for machine in STRUCTURES:
        _write(os.path.join(out, "%s.json" % machine), {
            "variants": {
                "formed=false": {"model": "%s:block/%s_core_bare" % (NS, machine)},
                "formed=true": {"model": "%s:block/%s_core" % (NS, machine)},
            }
        })
        print("blockstate %-24s 2 variants (formed)" % ("%s.json" % machine))

    # 水车：axis × angle
    variants = {}
    for axis in ("x", "z"):
        for frame in range(4):
            variants["axis=%s,angle=%d" % (axis, frame)] = {
                "model": "%s:block/water_wheel_%s_%d" % (NS, axis, frame)
            }
    _write(os.path.join(out, "water_wheel.json"), {"variants": variants})
    print("blockstate %-24s %d variants" % ("water_wheel.json", len(variants)))


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
 * {@code grain_sheller_parts()}，模型、方块状态、结构表会一起同步。</p>
 *
 * <h2>为什么用"相对核心的偏移"描述结构</h2>
 * 每个部件方块都带 {@code dx/dy/dz} 三个属性记录它相对核心的偏移，
 * 所以部件能自己算出核心在哪（{@code 核心 = 部件位置 - 偏移}），
 * 不需要方块实体、不需要 ID 同步，两台机器挨着也不会串。
 *
 * <p>偏移范围是 -1~2，方块状态里编码成 0~3（值 = 偏移 + 1）。</p>
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
        const = machine.upper()
        lines = []
        for (dx, dy, dz) in sorted(table, key=lambda k: (k[1], k[2], k[0])):
            lines.append("            new Part(%d, %d, %d)" % (dx, dy, dz))
        parts.append("    /** %s 的全部部件位置（不含核心自身）。 */\n" % machine)
        parts.append("    public static final List<Part> %s = List.of(\n" % const)
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
