# -*- coding: utf-8 -*-
"""模拟界面的绘制结果：把底图 + 按比例裁切的"满帧"叠起来看一眼。

    python tools/preview_gui.py

坐标必须和 `tools/texture_machines.py` 与两个 Screen 类一致。
改布局后跑一下，比开客户端快得多。
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food", "textures", "gui")
OUT = os.path.join(ROOT, "tools", "downloads", "gui_preview.png")

TEX_W, TEX_H = 256, 256          # 画布
PANEL_W, PANEL_H = 176, 166      # 面板
ARROW_X, ARROW_Y, ARROW_W, ARROW_H = 79, 34, 24, 17
ARROW_FULL = (176, 0)
FLAME_X, FLAME_Y, FLAME_W, FLAME_H = 81, 54, 14, 14
FLAME_FULL = (176, 20)
ENERGY_X, ENERGY_Y, ENERGY_W, ENERGY_H = 152, 20, 16, 26
ENERGY_FULL = (176, 40)
SCALE = 3


def paste(src, dst, x, y, u, v, w, h):
    """模拟 blit：从 src 的 (u,v) 取 w*h 贴到 dst 的 (x,y)。"""
    if w <= 0 or h <= 0:
        return
    dst.alpha_composite(src.crop((int(u), int(v), int(u + w), int(v + h))),
                        (int(x), int(y)))


def mock(name, progress, energy_ratio, flame):
    img = Image.open(os.path.join(GUI, "%s.png" % name)).convert("RGBA")
    # 只取面板那部分当底图（Screen 里就是这么 blit 的）
    out = img.crop((0, 0, PANEL_W, PANEL_H))

    if name == "processor":
        filled = int(ARROW_W * progress)
        paste(img, out, ARROW_X, ARROW_Y,
              ARROW_FULL[0], ARROW_FULL[1], filled, ARROW_H)
    else:
        h = max(1, int(FLAME_H * flame)) if flame > 0 else 0
        if h:
            paste(img, out, FLAME_X, FLAME_Y + (FLAME_H - h),
                  FLAME_FULL[0], FLAME_FULL[1] + FLAME_H - h, FLAME_W, h)

    lit = int(ENERGY_H * energy_ratio)
    if lit:
        paste(img, out, ENERGY_X, ENERGY_Y + (ENERGY_H - lit),
              ENERGY_FULL[0], ENERGY_FULL[1] + ENERGY_H - lit, ENERGY_W, lit)

    return out.resize((PANEL_W * SCALE, PANEL_H * SCALE), Image.NEAREST)


def main():
    # 两列：左边"刚开始"，右边"快好了"
    shots = [
        mock("processor", 0.0, 0.0, 0),
        mock("processor", 0.55, 0.75, 0),
        mock("generator", 0.0, 0.0, 0.0),
        mock("generator", 0.0, 0.5, 0.6),
    ]
    W = sum(s.width for s in shots) + 12 * (len(shots) + 1)
    H = max(s.height for s in shots) + 24
    sheet = Image.new("RGBA", (W, H), (24, 24, 30, 255))
    x = 12
    for s in shots:
        sheet.alpha_composite(s, (x, 12))
        x += s.width + 12
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print("wrote %s (%dx%d)" % (OUT, sheet.width, sheet.height))
    print("顺序: 磨粉机(空) | 磨粉机(进度55% 电75%) | 发电机(空) | 发电机(烧60% 电50%)")


if __name__ == "__main__":
    main()
