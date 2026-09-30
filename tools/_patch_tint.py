# -*- coding: utf-8 -*-
"""把 dish_models.py 里液体面的 tintindex 从 0 改成 1（与食物主体区分）。"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "tools", "dish_models.py")

s = io.open(p, encoding="utf-8").read()
before = s
s = s.replace('"#liquid", uv=[0, 0, 8, 8], tint=0)', '"#liquid", uv=[0, 0, 8, 8], tint=1)')
s = s.replace('"#liquid", uv=[0, 0, 9, 9], tint=0)', '"#liquid", uv=[0, 0, 9, 9], tint=1)')
s = s.replace('"#liquid", uv=[0, 0, 2.8, 2.8], tint=0)', '"#liquid", uv=[0, 0, 2.8, 2.8], tint=1)')
s = s.replace('"#liquid", uv=[0, 0, 2.6, 2.2], tint=0)', '"#liquid", uv=[0, 0, 2.6, 2.2], tint=1)')
s = s.replace('"#liquid", uv=[0, 0, 2, 1.8], tint=0)', '"#liquid", uv=[0, 0, 2, 1.8], tint=1)')

if s == before:
    print("no change (already patched?)")
else:
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("patched; liquid faces with tint=1:", s.count("tint=1"))
