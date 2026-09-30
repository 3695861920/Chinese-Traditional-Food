# -*- coding: utf-8 -*-
"""生成「餐具类方块」的三维模型：餐盘、大拼盘、案板。

    python tools/display_models.py

为什么要重做
------------
之前这三样各是**一块平板**（餐盘是 0.5 格厚的白板、案板是 1 格厚的板），
摆在地上像一块瓷砖，完全没有"盘子"的样子。这里改成和
`tools/dish_models.py` 同一套叠层手法：

* **餐盘**：圈足 + 盘腹 + 一圈翘起的盘沿，盘心因此比盘沿**低 0.8 像素** ——
  菜摆上去是"盛"在盘子里，而不是浮在板子上；
* **大拼盘**：木质托盘，四边起沿、两侧带提手、四角有小垫脚；
* **案板**：厚木砧板，两块拼板中间留一道拼缝，底面收一圈倒角。

几何约定与 `dish_models.py` 完全一致（八边形切片 + 精确相接不重叠），
所以不需要任何渲染器就能有"圆润的器皿"。
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food")
NS = "chinese_traditional_food"


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def box(x0, y0, z0, x1, y1, z1, texture, uv=None, cull=None, faces=None):
    faces = faces or ["up", "down", "north", "south", "west", "east"]
    out = {}
    for f in faces:
        d = {"texture": texture, "uv": uv or [0, 0, 16, 16]}
        if cull is not None and f == cull:
            d["cullface"] = f
        out[f] = d
    return {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": out}


def _oct(cx, cz, rx, rz, y0, y1, texture, cut=0.40, cull=None):
    """八边形切片：3 个互不重叠的矩形精确铺满（和 dish_models 同一套）。"""
    ch = rx * cut
    cv = rz * cut
    return [
        box(cx - rx + ch, y0, cz - rz, cx + rx - ch, y1, cz + rz,
            texture, cull=cull),
        box(cx - rx, y0, cz - rz + cv, cx - rx + ch, y1, cz + rz - cv, texture),
        box(cx + rx - ch, y0, cz - rz + cv, cx + rx, y1, cz + rz - cv, texture),
    ]


def _disc(cx, cz, r, y0, h, texture, layers=2, shrink=0.18, cut=0.40, cull=None):
    """圆盘：沿 Y 逐层收小的八边形，做出厚度与圆角。"""
    out = []
    dh = h / layers
    for i in range(layers):
        t = i / (layers - 1) if layers > 1 else 0.0
        s = 1.0 - shrink * (t ** 1.5)
        out += _oct(cx, cz, r * s, r * s, y0 + i * dh, y0 + (i + 1) * dh,
                    texture, cut=cut, cull=cull if i == 0 else None)
    return out


def _ring(x0, z0, x1, z1, w, y0, y1, texture):
    """方形环（上下两条通长、左右两条避开）—— 精确铺满、不重叠。

    环的**内壁**朝内、外壁朝外，所以盘沿会比盘心高出一截，
    中间那块盘心顶面正好露出来当"盘底"。
    """
    return [
        box(x0, y0, z0, x1, y1, z0 + w, texture),
        box(x0, y0, z1 - w, x1, y1, z1, texture),
        box(x0, y0, z0 + w, x0 + w, y1, z1 - w, texture),
        box(x1 - w, y0, z0 + w, x1, y1, z1 - w, texture),
    ]


# ----------------------------------------------------------------------
def plate():
    """青花瓷餐盘。

    <pre>
    y=3.35 ┌───────────────────────┐   <- 盘沿顶面（青花边）
    y=3.20 └──┐                 ┌──┘
             │                 │
    y=2.55   └─────────────────┘      <- 盘底顶面，比盘沿低 0.8 像素
             （菜就"盛"在这一层上）
    y=2.40  ────── 盘腹 ──────
    y=0.70  ────── 盘腹下段 ──
    y=0.00  ────── 圈足 ──────
    </pre>
    """
    E = []
    # 圈足：比盘腹小一圈，于是盘子是"垫起来"的
    E += _oct(8, 8, 4.2, 4.2, 0.0, 0.7, "#side", cut=0.30, cull="down")
    # 盘腹：两层，下层小、上层大，形成外扩的弧线
    E += _oct(8, 8, 6.2, 6.2, 0.7, 1.7, "#side", cut=0.30)
    E += _oct(8, 8, 7.0, 7.0, 1.7, 2.4, "#side", cut=0.30)
    # 盘底顶面（青花图案），比盘沿低
    E += _oct(8, 8, 7.0, 7.0, 2.4, 2.55, "#top", cut=0.30)
    # 盘沿：一圈厚边，比盘底高 0.8 像素，且向外多伸 0.4 像素
    E += _ring(0.8, 0.8, 15.2, 15.2, 1.5, 2.4, 3.2, "#side")
    E += _ring(0.8, 0.8, 15.2, 15.2, 1.5, 3.2, 3.35, "#top")
    return E


def serving_platter():
    """大拼盘：木托盘 —— 四角垫脚 + 底板 + 四边起沿 + 两侧提手。"""
    E = []
    # 垫脚
    for (cx, cz) in ((2.4, 2.4), (13.6, 2.4), (2.4, 13.6), (13.6, 13.6)):
        E += _oct(cx, cz, 1.3, 1.3, 0.0, 0.5, "#wood", cut=0.30, cull="down")
    # 底板：两层，下层略小形成倒角
    E += _oct(8, 8, 7.4, 7.4, 0.5, 0.9, "#wood", cut=0.18)
    E += _oct(8, 8, 7.6, 7.6, 0.9, 1.0, "#wood", cut=0.18)
    # 盘面：菜摆在 y=1.0 这一层上
    E += _oct(8, 8, 7.0, 7.0, 1.0, 1.15, "#wood", cut=0.18)
    # 四边起沿：一整圈，形成托盘边
    E += _ring(0.2, 0.2, 15.8, 15.8, 1.4, 1.0, 2.2, "#wood")
    E += _ring(0.2, 0.2, 15.8, 15.8, 1.4, 2.2, 2.35, "#wood")
    # 两侧提手
    E.append(box(-0.9, 1.2, 5.4, 0.3, 2.4, 10.6, "#wood"))
    E.append(box(15.7, 1.2, 5.4, 16.9, 2.4, 10.6, "#wood"))
    return E


def cutting_board():
    """案板：厚木砧板，两块拼板 + 一道拼缝 + 底部倒角。

    <pre>
    y=1.9 ┌──────┬──────┐   <- 板面（两块拼板，中间一道缝）
    y=1.6 │      │      │
          └──────────────┘
    y=0.5   ┌──────────┐     <- 板身
    y=0       └────────┘     <- 底面收一圈倒角
    </pre>
    """
    E = []
    # 底部倒角：比板身小一圈，于是底边有斜口
    E.append(box(0.9, 0.0, 0.9, 15.1, 0.5, 15.1, "#side", cull="down"))
    # 板身
    E.append(box(0.4, 0.5, 0.4, 15.6, 1.6, 15.6, "#side"))
    # 板面：两块拼板，中间留一道缝（缝里透出下面板身的深色）
    E.append(box(0.4, 1.6, 0.4, 7.6, 1.9, 15.6, "#top"))
    E.append(box(8.4, 1.6, 0.4, 15.6, 1.9, 15.6, "#top"))
    return E


# ----------------------------------------------------------------------
TARGETS = {
    "plate": ("plate", "plate_side", plate),
    "serving_platter": ("serving_platter", "serving_platter", serving_platter),
    "cutting_board": ("cutting_board", "cutting_board_side", cutting_board),
}


def build():
    out = os.path.join(RES, "models", "block")
    for name, (top, side, fn) in TARGETS.items():
        elements = fn()
        model = {
            "parent": "minecraft:block/block",
            "render_type": "cutout",
            "textures": {
                "particle": "%s:block/%s" % (NS, top),
                "top": "%s:block/%s" % (NS, top),
                "side": "%s:block/%s" % (NS, side),
                "wood": "%s:block/%s" % (NS, side),
            },
            "elements": elements,
        }
        _write(os.path.join(out, "%s.json" % name), model)
        lo = [min(e["from"][i] for e in elements) for i in range(3)]
        hi = [max(e["to"][i] for e in elements) for i in range(3)]
        print("model  %-16s %2d elements  x=%.1f..%.1f z=%.1f..%.1f  top=%.3f"
              % (name, len(elements), lo[0], hi[0], lo[2], hi[2],
                 hi[1] / 16.0))


if __name__ == "__main__":
    build()
