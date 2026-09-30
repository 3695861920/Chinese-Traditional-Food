# -*- coding: utf-8 -*-
"""兼容配方：农夫乐事 / 森罗物语 / 同作者的 TFC Food Port。

    python tools/gen_compat.py

思路：**加载阶段动态检测**，不写死依赖
--------------------------------------
三个模组都是可选的。做法是给每一份"需要厨具"的配方套一个
`neoforge:conditions`，由 NeoForge 在数据包加载时求值：

    {"type": "neoforge:mod_loaded", "modid": "farmersdelight"}

于是**没装的模组对应的配方根本不会进入配方管理器**（不是被隐藏，
是压根不加载），JEI 里也不会出现做不了的东西。游戏也不会有
"缺少依赖"的报错 —— 因为条件不满足时那份 JSON 直接被丢弃。

这与"把配方写在代码里再运行时判断"相比，好处是：
* 数据包层面的规则，玩家可以自己覆盖 / 禁用；
* 不增加任何启动开销；
* 用 `/reload` 就能试。

具体适配了什么
--------------
1. **农夫乐事**（`farmersdelight`）
   * 切菜板（`farmersdelight:cutting`）：本模组的食材 → 蔬菜丝 / 肉丝 / 鱼片
   * 烹饪锅（`farmersdelight:cooking`）：高汤 / 汤 / 粥
2. **森罗物语**（`kaleidoscope_cookery`）
   * 切菜板、石磨、锅，按对方 README 里的设备类型写
3. **TFC Food Port**（`tfc_food_port`）
   * 对方的月饼 / 果酱链条与本模组的月饼互相可替代

**没有对方模组时怎么办**：这些配方全部不存在，玩家用本模组自带的
案板 / 炉灶 / 磨粉机做同样的事 —— 那条路完全不依赖外部模组
（见 {@code content_data.CUTTING} 与 {@code STEAMING}/{@code BOILING}/{@code COOKING}）。
"""

import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "src", "main", "resources", "data",
                    "chinese_traditional_food")
NS = "chinese_traditional_food"

FD = "farmersdelight"
KC = "kaleidoscope_cookery"
TFC = "tfc_food_port"

# ======================================================================
# 1) 农夫乐事
# ======================================================================
# 切菜板：对方用 "ingredients" + "result"，且支持 "tool"（是否要刀）。
FD_CUTTING = [
    # (配方名, 输入, 产出, 数量)
    ("cut_shredded_tofu",   "tofu",           "shredded_tofu",     1),
    ("cut_shredded_veg",    "#c:vegetables",  "shredded_vegetable", 1),
    ("cut_shredded_meat",   "#c:raw_meat",    "shredded_meat",     1),
    ("cut_fish_fillet",     "#c:raw_fish",    "fish_fillet",       1),
]

# 烹饪锅：对方的 schema 是 ingredients 列表 + result + container（可选）。
FD_COOKING = [
    ("cook_stock",        ["bone_meal", "water_bucket"],                "stock",           "bowl"),
    ("cook_egg_drop_soup", ["stock", "egg"],                            "egg_drop_soup",   "bowl"),
    ("cook_zhou_congee",  ["rice", "rice"],                             "zhou_congee",     "bowl"),
    ("cook_red_bean_soup", ["red_bean", "red_bean", "sugar"],           "red_bean_soup",   "bowl"),
    ("cook_mung_bean_soup", ["mung_bean", "mung_bean", "sugar"],        "mung_bean_soup",  "bowl"),
    ("cook_wonton_soup",  ["flour", "raw_meat_tag", "stock"],           "wonton_soup",     "bowl"),
    ("cook_yam_ribs_soup", ["chinese_yam", "raw_meat_tag", "stock"],    "yam_ribs_soup",   "bowl"),
]


def _ns(name, default_ns):
    """裸名字补命名空间；已经是 ns:path 或 #tag 的原样返回。"""
    if name.startswith("#"):
        return "#" + (name[1:] if ":" in name[1:] else "c:" + name[1:])
    if ":" in name:
        # 兼容用 "raw_meat_tag" 这种写法表示某个标签
        if name.endswith("_tag"):
            return "#c:" + name[:-4]
        return name
    return "%s:%s" % (default_ns, name)


def gen_farmers_delight(base):
    n = 0
    # 切菜板
    for (rid, src, out, count) in FD_CUTTING:
        _write(os.path.join(base, "%s__fd.json" % rid), {
            "type": "%s:cutting" % FD,
            "ingredients": [{"item": _ns(src, NS)} if src.startswith("#")
                            else {"item": _ns(src, NS)}],
            "result": [{"item": "%s:%s" % (NS, out), "count": count}],
            "tool": {"tag": "c:tools/knife"},
            "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": FD}],
        })
        n += 1
    # 烹饪锅
    for (rid, mats, out, container) in FD_COOKING:
        recipe = {
            "type": "%s:cooking" % FD,
            "ingredients": [_ns(m, "minecraft") for m in mats],
            "result": {"id": "%s:%s" % (NS, out), "count": 1},
            "experience": 0.35,
            "cookingtime": 200,
            "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": FD}],
        }
        recipe["container"] = "%s:%s" % ("minecraft" if container == "bowl" else NS,
                                         container)
        _write(os.path.join(base, "%s__fd.json" % rid), recipe)
        n += 1
    return n


# ======================================================================
# 2) 森罗物语
# ======================================================================
# 按对方 README：切菜板 / 石磨 / 锅 三种设备，字段风格与农夫乐事相近。
KC_CUTTING = [
    ("kc_cut_shredded_tofu", "tofu",          "shredded_tofu",     1),
    ("kc_cut_shredded_veg",  "#c:vegetables", "shredded_vegetable", 1),
    ("kc_cut_shredded_meat", "#c:raw_meat",   "shredded_meat",     1),
    ("kc_cut_fish_fillet",   "#c:raw_fish",   "fish_fillet",       1),
]

KC_STONE_MILL = [
    ("kc_mill_flour",      "wheat",  "flour",      1),
    ("kc_mill_rice_flour", "rice",   "rice_flour", 1),
    ("kc_mill_corn_flour", "corn",   "corn_flour", 1),
    ("kc_mill_pepper",     "sichuan_peppercorn", "pepper_powder", 1),
]

KC_POT = [
    ("kc_boil_stock",       ["bone_meal", "water_bucket"],          "stock",           "bowl"),
    ("kc_boil_egg_drop",    ["stock", "egg"],                        "egg_drop_soup",   "bowl"),
    ("kc_boil_congee",      ["rice", "rice"],                        "zhou_congee",     "bowl"),
    ("kc_boil_red_bean",    ["red_bean", "red_bean", "sugar"],       "red_bean_soup",   "bowl"),
    ("kc_boil_lotus",       ["lotus_seed", "sugar"],                 "lotus_seed_soup", "bowl"),
]


def gen_kaleidoscope(base):
    n = 0
    for (rid, src, out, count) in KC_CUTTING:
        _write(os.path.join(base, "%s.json" % rid), {
            "type": "%s:cutting_board" % KC,
            "ingredients": [{"item": _ns(src, NS)}],
            "result": [{"item": "%s:%s" % (NS, out), "count": count}],
            "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": KC}],
        })
        n += 1
    for (rid, src, out, count) in KC_STONE_MILL:
        _write(os.path.join(base, "%s.json" % rid), {
            "type": "%s:stone_mill" % KC,
            "ingredient": _ns(src, "minecraft"),
            "result": {"id": "%s:%s" % (NS, out), "count": count},
            "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": KC}],
        })
        n += 1
    for (rid, mats, out, container) in KC_POT:
        _write(os.path.join(base, "%s.json" % rid), {
            "type": "%s:pot" % KC,
            "ingredients": [_ns(m, "minecraft") for m in mats],
            "result": {"id": "%s:%s" % (NS, out), "count": 1},
            "container": "minecraft:%s" % container,
            "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": KC}],
        })
        n += 1
    return n


# ======================================================================
# 3) TFC Food Port
# ======================================================================
# 同作者的另一个模组。它也有月饼与果酱链条，两边互通最自然：
# 它的面团能做我们的月饼，我们的豆沙能做它的月饼。
#
# 注意这里用的是 **26.1 的纯字符串 Ingredient**（`"#tag"` / `"ns:item"`），
# 而不是老版本的 `{"tag": ...}` / `{"item": ...}` 对象 —— 后者在 26.1 里
# 会直接报 "Not a JSON object" 之类，配方根本加载不进来。
TFC_BRIDGE = [
    # (配方名, pattern, key, 产出 id, 数量)
    ("tfc_mooncake_from_their_dough",
     ["DDD", "DPD", "DDD"],
     {"D": "#%s:dough" % TFC, "P": "%s:bean_paste" % NS},
     "%s:dousha_yuebing" % NS, 4),
    ("tfc_bean_paste_from_their_jam",
     ["JJ", "JJ"],
     {"J": "#%s:jam" % TFC},
     "%s:bean_paste" % NS, 2),
]


def gen_tfc(base):
    n = 0
    for (rid, pattern, key, out, count) in TFC_BRIDGE:
        _write(os.path.join(base, "%s.json" % rid), {
            "type": "minecraft:crafting_shaped",
            "pattern": pattern,
            "key": key,
            "result": {"id": out, "count": count},
            "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": TFC}],
        })
        n += 1
    return n


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def main():
    base = os.path.join(DATA, "recipe", "compat")
    # 先清掉上一次生成的文件，避免改了清单之后留下孤儿配方
    if os.path.isdir(base):
        for name in os.listdir(base):
            if name.endswith(".json"):
                os.remove(os.path.join(base, name))
    fd = gen_farmers_delight(base)
    kc = gen_kaleidoscope(base)
    tfc = gen_tfc(base)
    print("compat recipes: farmersdelight=%d kaleidoscope=%d tfc=%d" % (fd, kc, tfc))
    print("  -> %s" % os.path.relpath(base, ROOT))


if __name__ == "__main__":
    main()
