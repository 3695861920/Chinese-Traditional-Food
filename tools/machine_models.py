# -*- coding: utf-8 -*-
"""
手摇式脱壳机的三维模型（无 UI，摇柄操作，可加料斗组成多方块）。

    python tools/machine_models.py

现实原型与建模思路
------------------
手摇碾米/脱壳机的结构非常简单，正好适合用方块模型表达：

    ┌──────────┐   <- 料斗（hopper，可选，叠在主体上方）
    │   漏斗   │
    ├──────────┤
    │ 木箱主体 │   <- 主体（base，含摇柄与出料口）
    │      ╭───┤
    └──────╯   │   <- 摇柄（crank，4 个角度做转动动画）
       △ 出料口

* **主体**：木箱 + 铁箍 + 侧面的出料口；
* **摇柄**：一根弯柄，朝向 4 个方向分别出一张模型，
  由方块状态 `crank=0..3` 切换 —— 每摇一次就换下一张，
  于是**不需要任何渲染器**就有转动动画（原版拉杆/中继器也是这个套路）；
* **料斗**：顶部漏斗，叠上之后容量变大（多方块）。

模型全部是手写的立方体元素，和原版方块同一个体系。
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


def box(x0, y0, z0, x1, y1, z1, texture, uv=None, cull=None, faces=None,
        rotation=None):
    faces = faces or ["up", "down", "north", "south", "west", "east"]
    out = {}
    for f in faces:
        face = {"texture": texture}
        if uv is not None:
            face["uv"] = uv
        if cull is not None and f == cull:
            face["cullface"] = f
        out[f] = face
    el = {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": out}
    if rotation is not None:
        el["rotation"] = rotation
    return el


TEX = {
    "particle": "%s:block/grain_sheller_side" % NS,
    "wood": "%s:block/grain_sheller_side" % NS,
    "top": "%s:block/grain_sheller" % NS,
    "iron": "%s:block/dish_iron" % NS,
}


def sheller_body():
    """主体：木箱 + 顶部铁圈 + 出料口。"""
    E = []
    # 木箱（略矮，上面要叠料斗）
    E.append(box(1.0, 0.0, 1.0, 15.0, 10.0, 15.0, "#wood",
                 uv=[0, 0, 14, 10], cull="down"))
    # 顶部一圈（与料斗衔接的接口）
    E.append(box(2.2, 10.0, 2.2, 13.8, 11.2, 13.8, "#iron", uv=[0, 0, 11, 1]))
    # 中央进料口（凹陷）
    E.append(box(5.4, 10.4, 5.4, 10.6, 11.0, 10.6, "#iron", uv=[0, 0, 5, 0.6]))
    # 出料口（前面一块斜板 + 小托盘）
    E.append(box(4.0, 2.6, 0.2, 12.0, 3.4, 1.2, "#iron", uv=[0, 0, 8, 0.8]))
    E.append(box(4.6, 1.4, 0.0, 11.4, 2.6, 1.0, "#wood", uv=[0, 0, 7, 1.2]))
    # 四角铆钉
    for (rx, rz) in ((1.6, 1.6), (14.4, 1.6), (1.6, 14.4), (14.4, 14.4)):
        E.append(box(rx - 0.6, 4.0, rz - 0.6, rx + 0.6, 5.2, rz + 0.6,
                     "#iron", uv=[0, 0, 1.2, 1.2]))
    return E


def sheller_crank(frame):
    """摇柄：4 个角度。frame 0..3 分别指向 东 / 北 / 西 / 南。

    用 rotation 让同一段几何绕轴转 90° * frame。

    注意：rotation 必须绕元素自身中心附近的 pivot，且元素尺寸要是整数，
    否则方块模型校验会报错（原版对 rotation 有这些限制）。
    """
    ang = [0, 90, 180, 270][frame]
    E = []
    # 轴（固定在侧面，不转）
    E.append(box(0.0, 5.4, 7.4, 1.6, 8.6, 8.6, "#iron", uv=[0, 0, 1.6, 3.2]))
    # 柄（绕轴心旋转）
    E.append(box(-0.4, 7.4, 7.6, 1.6, 8.4, 8.4, "#iron", uv=[0, 0, 2, 1],
                 rotation={"origin": [0.6, 7.9, 8.0], "axis": "x", "angle": ang,
                           "rescale": False}))
    # 握把（在柄的末端，跟着转）
    E.append(box(0.2, 6.6, 8.6, 1.4, 9.2, 10.0, "#wood", uv=[0, 0, 1.2, 2.6],
                 rotation={"origin": [0.6, 7.9, 8.0], "axis": "x", "angle": ang,
                           "rescale": False}))
    return E


def hopper():
    """料斗：上宽下窄的四片斜面 + 顶圈。"""
    E = []
    # 四片斜面（用四个斜放的薄板近似漏斗）
    E.append(box(0.4, 12.0, 0.4, 15.6, 13.2, 3.2, "#iron", uv=[0, 0, 15, 1.2]))
    E.append(box(0.4, 12.0, 12.8, 15.6, 13.2, 15.6, "#iron", uv=[0, 0, 15, 1.2]))
    E.append(box(0.4, 12.0, 3.2, 3.2, 13.2, 12.8, "#iron", uv=[0, 0, 3, 1.2]))
    E.append(box(12.8, 12.0, 3.2, 15.6, 13.2, 12.8, "#iron", uv=[0, 0, 3, 1.2]))
    # 底部收口
    E.append(box(4.6, 10.0, 4.6, 11.4, 12.2, 11.4, "#iron", uv=[0, 0, 6.8, 2.2]))
    # 顶圈
    E.append(box(0.0, 13.2, 0.0, 16.0, 14.0, 16.0, "#wood", uv=[0, 0, 16, 0.8]))
    return E


def build():
    out = os.path.join(RES, "models", "block")

    # --- 主体：4 个摇柄角度 ---
    for frame in range(4):
        model = {
            "ambientocclusion": False,
            "textures": TEX,
            "elements": sheller_body() + sheller_crank(frame),
        }
        _write(os.path.join(out, "grain_sheller_crank%d.json" % frame), model)
        print("model grain_sheller_crank%d  %d elements"
              % (frame, len(model["elements"])))

    # --- 料斗 ---
    _write(os.path.join(out, "grain_sheller_hopper.json"), {
        "ambientocclusion": False,
        "textures": TEX,
        "elements": hopper(),
    })
    print("model grain_sheller_hopper  %d elements" % len(hopper()))

    # --- blockstate：crank=0..3 ---
    _write(os.path.join(RES, "blockstates", "grain_sheller.json"), {
        "variants": {
            "crank=%d" % f: {"model": "%s:block/grain_sheller_crank%d" % (NS, f)}
            for f in range(4)
        }
    })
    print("blockstate grain_sheller.json (4 crank frames)")

    _write(os.path.join(RES, "blockstates", "grain_sheller_hopper.json"), {
        "variants": {"": {"model": "%s:block/grain_sheller_hopper" % NS}}
    })
    print("blockstate grain_sheller_hopper.json")


if __name__ == "__main__":
    build()
