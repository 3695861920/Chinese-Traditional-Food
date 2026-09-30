# -*- coding: utf-8 -*-
"""把三台机器按**等轴测**画出来，用来肉眼检查机器造型。

    python tools/preview_machines.py furnace_generator
    python tools/preview_machines.py electric_mill
    python tools/preview_machines.py electric_sheller
    python tools/preview_machines.py            # 三台一起

正投影看不出立体形状，等轴测只画朝观察者的三个面并按深度排序，
才能看出"腿撑起来没有""磨盘看得到没有""有没有地方能看穿"。

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

# 只是个示意色：按材质键区分大块，方便看出结构
BASE = {
    "#stone": (140, 142, 145),
    "#iron": (124, 130, 140),
    "#millstone": (96, 98, 100),
    "#grate": (196, 104, 40),
    "#vent": (104, 110, 120),
    "#coil": (186, 122, 66),
    "#hopper": (78, 82, 90),
    # 灶火系统
    "#brick": (172, 108, 82),
    "#bamboo": (196, 198, 140),
    "#steam": (236, 242, 246),
    "#food": (186, 124, 72),
    "#shadow": (72, 66, 60),
    # 电磁炉（通电 / 断电两版顶面）
    "#cookerTop": (74, 62, 56),
    "#cookerTopOn": (232, 122, 48),
    "#cookerPanel": (110, 112, 120),
    # 包装方块（脚本 preview_compressed 会用）
    "#body": (196, 168, 128),
    "#contents": (210, 160, 110),
    "#crate": (176, 132, 86),
    "#band": (110, 86, 60),
}
SHADE = {"up": 1.00, "east": 0.76, "south": 0.56,
         "north": 0.62, "west": 0.48}


def load(name):
    with open(os.path.join(MODELS, "%s.json" % name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def iso(x, y, z):
    return (x - z) * COS30, (x + z) * SIN30 - y


def render(name):
    model = load(name)
    quads = []
    for el in model["elements"]:
        f, t = el["from"], el["to"]
        x0, y0, z0, x1, y1, z1 = f[0], f[1], f[2], t[0], t[1], t[2]
        # 画家算法：按**离观察者最远的那个角**排序，远的先画。
        # （之前用的是"最近的角"，结果同一列上矮的那块被画在上面，
        #   磨盘就被下方更大的八边形盖住了。）
        depth = x0 + y0 + z0
        corners = {
            "up": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
            "east": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
            "west": [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)],
            "north": [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)],
            "south": [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)],
        }
        for face, pts in corners.items():
            data = el["faces"].get(face)
            if not data:
                continue
            base = BASE.get(data["texture"], (255, 0, 255))
            s = SHADE.get(face, 0.7)
            colour = tuple(min(255, int(c * s)) for c in base)
            quads.append((depth, [iso(*p) for p in pts], colour))

    quads.sort(key=lambda q: q[0])
    xs = [p[0] for _d, quad, _c in quads for p in quad]
    ys = [p[1] for _d, quad, _c in quads for p in quad]
    ox, oy = (-min(xs)) * S + PAD, (-min(ys)) * S + PAD
    W = int((max(xs) - min(xs)) * S + PAD * 2)
    H = int((max(ys) - min(ys)) * S + PAD * 2)
    img = Image.new("RGBA", (W, H), (26, 26, 32, 255))
    dr = ImageDraw.Draw(img, "RGBA")
    for _d, quad, colour in quads:
        pts = [(x * S + ox, y * S + oy) for (x, y) in quad]
        dr.polygon(pts, fill=colour + (255,), outline=(0, 0, 0, 90))
    return img


def main():
    names = sys.argv[1:] or ["furnace_generator", "electric_mill",
                             "electric_sheller",
                             "large_furnace_generator", "large_electric_mill",
                             "large_electric_sheller"]
    imgs = [(n, render(n)) for n in names]
    W = sum(i.width for _n, i in imgs) + PAD * (len(imgs) + 1)
    H = max(i.height for _n, i in imgs) + PAD * 2
    sheet = Image.new("RGBA", (W, H), (26, 26, 32, 255))
    x = PAD
    for _n, im in imgs:
        sheet.alpha_composite(im, (x, PAD))
        x += im.width + PAD
    out = os.path.join(ROOT, "tools", "downloads", "machines.png")
    sheet.save(out)
    print("wrote %s (%dx%d)" % (out, sheet.width, sheet.height))
    # 每台单独存一份，方便放大看
    for n, im in imgs:
        im.save(os.path.join(ROOT, "tools", "downloads", "machine_%s.png" % n))
    print("单独: " + ", ".join("machine_%s.png" % n for n, _ in imgs))


if __name__ == "__main__":
    main()
