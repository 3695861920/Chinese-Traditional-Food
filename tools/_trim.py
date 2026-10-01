# -*- coding: utf-8 -*-
"""临时：删掉 texture_compressed 里已经没人用的 _speckle / _cloth。用完删。"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "tools", "texture_compressed.py")

s = io.open(P, encoding="utf-8").read()

a = s.index("def _speckle(")
b = s.index("def _woven(")
s = s[:a] + s[b:]

old = (
    "<h3>\u548c `_cloth` \u7684\u533a\u522b</h3>\n"
    "    `_cloth` \u662f\u201c\u6492\u6591\u70b9\u7684\u7c97\u9ebb\u5e03\u201d\uff0c"
)
new = (
    "<h3>\u4e3a\u4ec0\u4e48\u4e0d\u518d\u201c\u6492\u6591\u70b9\u201d</h3>\n"
    "    \u4e0a\u4e00\u7248\u7684\u505a\u6cd5\u662f\u5728\u4e00\u5757\u5e03\u8272\u4e0a"
    "\u6492\u758f\u843d\u7684\u6591\u70b9\u3002\u6591\u70b9\u8981\u201c\u758f\u843d + "
    "\u6210\u7c07\u201d\u624d\u50cf\u5e03\uff08\u6bcf\u4e2a\u50cf\u7d20\u72ec\u7acb"
    "\u968f\u673a = \u7535\u89c6\u96ea\u82b1\uff0c\u8fdc\u770b\u53ea\u5269\u810f\uff09\uff0c"
    "\u4f46\u8fd8\u662f\u4e00\u5757\u6709\u9897\u7c92\u7684\u8272\u5757\u3002\n"
)
if old in s:
    s = s.replace(old, new)
    print("docstring 已更新")
else:
    print("!! 没找到要替换的 docstring，手工检查")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("删除 _speckle / _cloth 完成")
