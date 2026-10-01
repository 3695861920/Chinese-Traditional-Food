# -*- coding: utf-8 -*-
"""从游戏本体里取原版贴图，缓存到 tools/downloads/vanilla/。

    （被 texture_compressed.py 调用：量原版木桶顶面的像素，
好让木箱的木框与桶身同色）

为什么需要它
------------
我们有两处要**照着原版的画法来**：

* 包装方块的木箱要"顶端颜色和侧边一样" —— 侧边本来就是原版木桶的贴图，
  所以顶面的木框也得用同一张图里的颜色；
* 作物改成"拿原版作物贴图当骨架重新上色"。

这两件事都要在**构建时**读到原版贴图的像素。所以这里做一层薄薄的
"取一次、之后读缓存"。

素材来自玩家自己的游戏本体，不随本模组分发 —— 只在构建时读进来当参考。
"""

import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", "downloads", "vanilla")
ARTIFACTS = os.path.join(ROOT, "build", "moddev", "artifacts")

# jar 里的路径前缀
PREFIX = "assets/minecraft/textures/"


def _client_jar():
    """找到反编译产物里的客户端 jar（首次 `gradlew build` 后才有）。"""
    if not os.path.isdir(ARTIFACTS):
        return None
    best = None
    for name in sorted(os.listdir(ARTIFACTS)):
        if name.startswith("minecraft-patched-") and name.endswith(".jar") \
                and "sources" not in name:
            best = os.path.join(ARTIFACTS, name)
    return best


def cached_path(name):
    """``"block/barrel_side"`` -> 本地缓存文件路径。"""
    return os.path.join(CACHE, name.replace("/", "_") + ".png")


def grab(name, dst=None):
    """取一张原版贴图到缓存。

    ``name`` 是 ``textures/`` 下的相对路径，例如
    ``"block/barrel_side"``、``"entity/decorated_pot/decorated_pot_side"``。
    已经缓存过就直接返回，不重复解包。

    @return 缓存文件路径；取不到返回 ``None``
    """
    dst = dst or cached_path(name)
    if os.path.exists(dst):
        return dst
    jar = _client_jar()
    if jar is None:
        return None
    entry = PREFIX + name + ".png"
    try:
        with zipfile.ZipFile(jar) as zf:
            if entry not in zf.namelist():
                return None
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with zf.open(entry) as src, open(dst, "wb") as fh:
                fh.write(src.read())
    except (OSError, zipfile.BadZipFile):
        return None
    return dst


def image(name):
    """直接拿一张 PIL 图（取不到返回 ``None``）。"""
    path = grab(name)
    if not path:
        return None
    from PIL import Image
    return Image.open(path).convert("RGBA")


def average(name):
    """一张原版贴图的平均色（取不到返回 ``None``）。"""
    img = image(name)
    if img is None:
        return None
    small = img.resize((1, 1))
    return small.getpixel((0, 0))[:3]
