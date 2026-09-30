# -*- coding: utf-8 -*-
"""
内容完整性校验。

    python tools/validate_content.py

检查项：
  1. 所有资源 JSON 能被解析；
  2. 所有 PNG 是 64x64 RGBA；
  3. 每个物品在 content_data 里声明，且有对应的：语言键、客户端物品、物品模型、纹理；
  4. 每个配方都能解析，且引用的物品 / 标签都真实存在（本模组物品 + 已知原版物品）；
  5. 本模组标签引用的物品都存在；
  6. 每个菜品都有配方。

任何一项失败都会以非零退出码结束，方便挂到 CI 上。
"""

import json
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_data as DATA  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources")
NS = "chinese_traditional_food"
ASSETS = os.path.join(RES, "assets", NS)
DATA_DIR = os.path.join(RES, "data", NS)

problems = []


def fail(msg):
    problems.append(msg)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:                      # noqa: BLE001
        fail("JSON 解析失败 %s: %s" % (os.path.relpath(path, ROOT), exc))
        return None


def walk(root, suffix):
    for base, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(suffix):
                yield os.path.join(base, name)


# ----------------------------------------------------------------------
def check_json():
    n = 0
    for path in walk(RES, ".json"):
        load_json(path)
        n += 1
    return n


def check_png():
    n = 0
    for path in walk(RES, ".png"):
        img = Image.open(path)
        if img.size != (64, 64):
            fail("PNG 尺寸不是 64x64: %s %s" % (os.path.relpath(path, ROOT), img.size))
        if img.mode != "RGBA":
            fail("PNG 不是 RGBA: %s %s" % (os.path.relpath(path, ROOT), img.mode))
        n += 1
    return n


def collect_declared():
    """content_data 里声明的全部条目 id。"""
    ids = set()
    kinds = {}
    for row in DATA.INGREDIENTS + DATA.SEASONINGS + DATA.FRUITS + DATA.VEGETABLES:
        ids.add(row[0])
        kinds[row[0]] = row[3]
    for row in DATA.TOOLS:
        ids.add(row[0])
        kinds[row[0]] = row[3]
    dishes = set()
    for row in DATA.DISHES:
        ids.add(row[0])
        kinds[row[0]] = row[4]
        dishes.add(row[0])
    # 手写的摆放 / 加工方块
    for extra in ("plate", "serving_platter", "cutting_board"):
        ids.add(extra)
    return ids, dishes, kinds


def check_assets(ids):
    lang_zh = load_json(os.path.join(ASSETS, "lang", "zh_cn.json")) or {}
    lang_en = load_json(os.path.join(ASSETS, "lang", "en_us.json")) or {}

    for item_id in sorted(ids):
        # 摆放 / 加工方块注册的是 BlockItem，语言键走 block. 前缀
        hand_written = ("plate", "serving_platter", "cutting_board")
        prefixes = ("item.", "block.") if item_id in hand_written else ("item.",)
        checks = {
            "语言(zh)": any("%s%s.%s" % (p, NS, item_id) in lang_zh for p in prefixes),
            "语言(en)": any("%s%s.%s" % (p, NS, item_id) in lang_en for p in prefixes),
            "客户端物品": os.path.exists(os.path.join(ASSETS, "items", "%s.json" % item_id)),
            "物品模型": os.path.exists(os.path.join(ASSETS, "models", "item", "%s.json" % item_id)),
            "纹理": os.path.exists(os.path.join(ASSETS, "textures", "item", "%s.png" % item_id)),
        }
        for what, ok in checks.items():
            if not ok:
                fail("%s 缺少%s" % (item_id, what))


def known_items():
    """本模组全部物品 + 允许引用的原版物品。"""
    ids, _dishes, _kinds = collect_declared()
    allowed_vanilla = {
        "minecraft:wheat", "minecraft:stick", "minecraft:iron_ingot", "minecraft:clay_ball",
        "minecraft:glass", "minecraft:planks", "minecraft:bowl", "minecraft:water_bucket",
        "minecraft:milk_bucket", "minecraft:bone_meal", "minecraft:sugar", "minecraft:blaze_powder",
        "minecraft:egg", "minecraft:potato", "minecraft:carrot", "minecraft:beef",
        "minecraft:porkchop", "minecraft:chicken", "minecraft:mutton", "minecraft:rabbit",
        "minecraft:cod", "minecraft:salmon", "minecraft:kelp", "minecraft:dried_kelp",
        "minecraft:brown_mushroom", "minecraft:red_mushroom", "minecraft:honey_bottle",
        "minecraft:sweet_berries", "minecraft:cocoa_beans", "minecraft:ink_sac",
        "minecraft:apple", "minecraft:beetroot",
    }
    return {"%s:%s" % (NS, i) for i in ids} | allowed_vanilla


def check_recipes(dishes):
    known = known_items()
    recipes_dir = os.path.join(DATA_DIR, "recipe")
    have_recipe = set()

    for path in walk(recipes_dir, ".json"):
        obj = load_json(path)
        if obj is None:
            continue
        recipe_id = os.path.basename(path)[:-5]
        have_recipe.add(recipe_id)

        refs = []
        kind = obj.get("type", "")
        if kind == "minecraft:crafting_shapeless":
            for ing in obj.get("ingredients", []):
                refs.append(ing)
        elif kind == "minecraft:crafting_shaped":
            refs.extend(obj.get("key", {}).values())
        elif kind == "minecraft:smelting":
            refs.append(obj.get("ingredient", {}))
        else:
            fail("配方 %s 使用了未知的 type=%s（本批次只支持工作台与熔炉）" % (recipe_id, kind))

        for ref in refs:
            if "item" in ref:
                if ref["item"] not in known:
                    fail("配方 %s 引用了不存在的物品 %s" % (recipe_id, ref["item"]))
            elif "tag" in ref:
                tag_ns, tag_path = ref["tag"].split(":", 1)
                if tag_ns == "c":
                    tag_file = os.path.join(RES, "data", "c", "tags", "item",
                                            "%s.json" % tag_path)
                elif tag_ns == NS:
                    tag_file = os.path.join(DATA_DIR, "tags", "item", "%s.json" % tag_path)
                else:
                    continue      # 原版标签默认存在
                if not os.path.exists(tag_file):
                    fail("配方 %s 引用了不存在的标签 #%s" % (recipe_id, ref["tag"]))

        result = obj.get("result", {})
        rid = result.get("id")
        if rid and rid.startswith(NS + ":") and rid not in known:
            fail("配方 %s 的产物 %s 不存在" % (recipe_id, rid))

    for dish in sorted(dishes):
        if dish not in have_recipe:
            fail("菜品 %s 没有配方" % dish)

    return len(list(walk(recipes_dir, ".json"))), len(have_recipe)


def check_tags():
    known = known_items()
    n = 0
    for path in walk(os.path.join(DATA_DIR, "tags"), ".json"):
        obj = load_json(path)
        if obj is None:
            continue
        n += 1
        for value in obj.get("values", []):
            if isinstance(value, str) and not value.startswith("#"):
                if value.startswith(NS + ":") and value not in known:
                    fail("标签 %s 引用了不存在的物品 %s"
                         % (os.path.relpath(path, ROOT), value))
    # c 命名空间标签
    for path in walk(os.path.join(RES, "data", "c", "tags"), ".json"):
        obj = load_json(path)
        if obj is None:
            continue
        n += 1
        for value in obj.get("values", []):
            if isinstance(value, str) and value.startswith(NS + ":") and value not in known:
                fail("c 标签 %s 引用了不存在的物品 %s"
                     % (os.path.relpath(path, ROOT), value))
    return n


def check_java_effects():
    """菜品引用的效果常量必须在 DishEffects.java 里定义。"""
    effects_file = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                                "chinese_traditional_food", "common", "food", "DishEffects.java")
    with open(effects_file, encoding="utf-8") as fh:
        src = fh.read()
    defined = set(re.findall(r"List<ServeEffect>\s+([A-Z_]+)\s*=", src))
    used = {row[8] for row in DATA.DISHES}
    for name in sorted(used - defined):
        fail("菜品引用了未定义的效果 DishEffects.%s" % name)
    return len(defined), len(used)


def check_icon_kinds():
    import texture_icons as ICONS
    missing = set()
    for row in DATA.INGREDIENTS + DATA.SEASONINGS + DATA.FRUITS + DATA.VEGETABLES:
        if row[3] not in ICONS.PAINTERS:
            missing.add(row[3])
    for row in DATA.TOOLS:
        if row[3] not in ICONS.PAINTERS:
            missing.add(row[3])
    for row in DATA.DISHES:
        if row[4] not in ICONS.PAINTERS:
            missing.add(row[4])
    for kind in sorted(missing):
        fail("图标种类 %s 没有画法" % kind)

    bad_palettes = set()
    for row in DATA.INGREDIENTS + DATA.SEASONINGS + DATA.FRUITS + DATA.VEGETABLES:
        if row[4] not in DATA.PALETTES:
            bad_palettes.add(row[4])
    for row in DATA.TOOLS:
        if row[4] not in DATA.PALETTES:
            bad_palettes.add(row[4])
    for row in DATA.DISHES:
        if row[5] not in DATA.PALETTES:
            bad_palettes.add(row[5])
    for name in sorted(bad_palettes):
        fail("配色 %s 未在 PALETTES 中定义" % name)


def check_cutting(ids):
    """案板切割表：产出必须是本模组真实存在的物品。"""
    import importlib.util
    path = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                        "chinese_traditional_food", "common", "recipe", "ModCutting.java")
    if not os.path.exists(path):
        fail("未找到生成的 ModCutting.java")
        return 0
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    entries = re.findall(r'new Entry\("([^"]+)",\s*"([^"]+)",\s*(true|false),\s*(\d+)\)', src)
    if len(entries) != len(DATA.CUTTING):
        fail("ModCutting.java 的条目数 %d 与 content_data.CUTTING 的 %d 不一致"
             % (len(entries), len(DATA.CUTTING)))
    for (_inp, out, _knife, _time) in entries:
        if out not in ids:
            fail("案板切割产出 %s 不是本模组的物品" % out)
    return len(entries)


def main():
    ids, dishes, _kinds = collect_declared()
    print("声明条目: %d（其中菜品 %d）" % (len(ids), len(dishes)))

    print("JSON 文件: %d" % check_json())
    print("PNG 文件 : %d" % check_png())
    check_assets(ids)
    n_recipes, n_have = check_recipes(dishes)
    print("配方文件: %d" % n_recipes)
    print("标签文件: %d" % check_tags())
    print("效果常量: 定义 %d / 引用 %d" % check_java_effects())
    print("案板规则: %d" % check_cutting(ids))
    check_icon_kinds()

    if problems:
        print("\n发现 %d 个问题：" % len(problems))
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("\n全部检查通过。")


if __name__ == "__main__":
    main()
