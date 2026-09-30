# -*- coding: utf-8 -*-
"""把整台机器按**等轴测**画出来，用来肉眼检查机器的立体形状。

    python tools/preview_machines.py water_mill
    python tools/preview_machines.py grain_sheller
    python tools/preview_machines.py water_wheel

正投影会把后面的构件也画出来、镂空的地方会被填满，看不出真实形状；
等轴测只画朝观察者的三个面并按深度排序，才能看出机器的轮廓、
高低差、以及**有没有地方能看穿**。

改模型之后跑一下这个，比反复开客户端快得多。
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(ROOT, "src", "main", "resources", "assets",
                      "chinese_traditional_food", "models", "block")

S = 9.0                     # 每个"模型像素"画多少屏幕像素
COS30, SIN30 = math.cos(math.pi / 6), math.sin(math.pi / 6)
PAD = 16

BASE = {
    "#stone": (140, 142, 145),
    "#wood": (166, 116, 64),
    "#iron": (124, 130, 140),
    "#wheel": (104, 92, 62),
    "#millstone": (96, 98, 100),
    "#hopper": (78, 82, 90),
    "#axle": (168, 150, 96),
    "#crank": (150, 120, 96),
    "#hopper_top": (70, 74, 82),
    "#outlet": (112, 88, 56),
}
# 三个可见面的明暗：顶面最亮，+X 面其次，+Z 面最暗
SHADE = {"up": 1.00, "east": 0.76, "south": 0.56}


def load(name):
    with open(os.path.join(MODELS, "%s.json" % name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def cells_of(machine):
    """返回 [(dx, dy, dz, 模型名)]。"""
    if machine == "water_wheel":
        return [(0, 0, 0, "water_wheel_x_0")]
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import machine_models as MM
    out = [(0, 0, 0, "%s_core" % machine)]
    for (dx, dy, dz), _kind in sorted(MM.STRUCTURES[machine].items()):
        out.append((dx, dy, dz, "%s_p%d%d%d" % (machine, dx + 1, dy + 1, dz + 1)))
    return out


def iso(x, y, z):
    """世界坐标（方块单位）-> 屏幕坐标。y 向上。"""
    sx = (x - z) * COS30
    sy = (x + z) * SIN30 - y
    return sx, sy


def main():
    machine = sys.argv[1] if len(sys.argv) > 1 else "water_mill"
    boxes = []      # (depth, [(sx,sy)...], 颜色)
    for (cx, cy, cz, name) in cells_of(machine):
        model = load(name)
        for el in model["elements"]:
            f, t = el["from"], el["to"]
            x0, y0, z0 = (cx * 16 + f[0], cy * 16 + f[1], cz * 16 + f[2])
            x1, y1, z1 = (cx * 16 + t[0], cy * 16 + t[1], cz * 16 + t[2])
            face_tex = {}
            for fname, data in el["faces"].items():
                face_tex[fname] = data.get("texture", "#stone")
            depth = (x1 + y1 + z1)
            # 三组可见面的四个角
            quads = {
                "up": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
                "east": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
                "south": [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)],
            }
            for fname, pts in quads.items():
                if fname not in face_tex:
                    continue
                colour = BASE.get(face_tex[fname], (255, 0, 255))
                s = SHADE[fname]
                colour = tuple(min(255, int(c * s)) for c in colour)
                boxes.append((depth, [iso(*p) for p in pts], colour, fname))

    boxes.sort(key=lambda b: b[0])
    xs = [p[0] for _d, quad, _c, _f in boxes for p in quad]
    ys = [p[1] for _d, quad, _c, _f in boxes for p in quad]
    # 注意：iso() 出来的还是"模型像素"单位，画布尺寸和原点都要乘 S
    ox = (-min(xs)) * S + PAD
    oy = (-min(ys)) * S + PAD
    W = int((max(xs) - min(xs)) * S + PAD * 2)
    H = int((max(ys) - min(ys)) * S + PAD * 2)
    img = Image.new("RGBA", (W, H), (26, 26, 32, 255))
    dr = ImageDraw.Draw(img, "RGBA")
    for _d, quad, colour, _f in boxes:
        pts = [(x * S + ox, y * S + oy) for (x, y) in quad]
        dr.polygon(pts, fill=colour + (255,), outline=(0, 0, 0, 90))

    out = os.path.join(ROOT, "tools", "downloads", "machine_%s.png" % machine)
    img.save(out)
    print("wrote %s (%dx%d)  构件 %d 个面" % (out, W, H, len(boxes)))


if __name__ == "__main__":
    main()
