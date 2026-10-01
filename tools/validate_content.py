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
  6. 每道菜都能在某口锅里做出来（菜品不再有工作台配方）。

任何一项失败都会以非零退出码结束，方便挂到 CI 上。
"""

import io
import json
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_data as DATA  # noqa: E402
import gen_content  # noqa: E402  （锅谱计划就写在里面，校验要对得上）

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
    """纹理必须是正方形、边长为 2 的幂（Minecraft 的贴图惯例）。

    默认是原版的 16x16；若用 `build_textures.py --size 64` 生成精细版，
    这里同样能通过。界面底图（textures/gui）尺寸另算，不参与检查。
    """
    n = 0
    for path in walk(RES, ".png"):
        img = Image.open(path)
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        if "/textures/gui/" in rel:
            n += 1
            continue
        w, h = img.size
        if w != h or w < 16 or (w & (w - 1)) != 0:
            fail("PNG 尺寸不是正方形 2 的幂: %s %s" % (rel, img.size))
        if img.mode != "RGBA":
            fail("PNG 不是 RGBA: %s %s" % (rel, img.mode))
        n += 1
    return n


def collect_declared():
    """content_data 里声明的全部条目 id。"""
    ids = set()
    kinds = {}
    for row in (DATA.INGREDIENTS + DATA.SEEDS + DATA.SEASONINGS
                + DATA.FRUITS + DATA.VEGETABLES):
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
    # 手写的功能方块（它们的物品与语言键在 ModItems / lang 里单独提供）
    for extra in HAND_WRITTEN_BLOCKS:
        ids.add(extra)
    # 生成出来的压缩方块也算"已声明"，否则配方检查会误报
    for extra in compressed_blocks():
        ids.add(extra)
    # 13 套木制品（原木/去皮/木板/楼梯/台阶/栅栏/栅栏门）。
    # 漏掉这一步的后果是：标签与配方检查会把 117 个方块全报成"不存在的物品"。
    for extra in wood_blocks():
        ids.add(extra)
    return ids, dishes, kinds


# 手写的功能方块：它们注册的是 BlockItem，语言键走 block. 前缀，
# 且模型 / 方块状态都是手写或由 display_models.py 生成的。
HAND_WRITTEN_BLOCKS = ("plate", "cutting_board",
                       "furnace_generator", "electric_mill", "electric_sheller",
                       "large_furnace_generator", "large_electric_mill", "large_electric_sheller",
                       "stove", "wok", "steamer", "soup_pot")


def compressed_blocks():
    """食材压缩方块的 id 列表。

    它们由 tools/gen_compressed.py 生成，清单在同一个脚本里，
    所以这里直接读那份数据，而不是再手抄一遍 —— 手抄肯定会漏。
    """
    import gen_compressed
    return [row[0] for row in gen_compressed.COMPRESSED]


def wood_blocks():
    """13 套木制品的方块 id（每种木 9 个 = 117 个）。

    同样从生成器的数据里读，不手抄。**加了新的木质形态不用改这里** ——
    `gen_woods.FORMS` 是唯一的清单。
    """
    import gen_woods
    out = []
    for fruit in gen_woods.fruits():
        for _form, fn in gen_woods.FORMS:
            out.append(fn(fruit))
    return out


# ======================================================================
# 树苗 / 树叶（ModTrees 生成，名字由 gen_trees 定）
# ======================================================================

def tree_blocks():
    """树苗与树叶：它们也是 BlockItem（`block.` 语言键 + `items/*.json`）。"""
    import gen_trees
    out = []
    for (fruit, _size) in DATA.TREE_FRUITS:
        out.append(gen_trees.sapling(fruit))
        out.append(gen_trees.leaves(fruit))
    return out

# 生成出来的压缩方块：语言键与资源由 tools/gen_compressed.py 负责，
# 这里做成一堆常量，避免每次调用都重新读一遍数据表。
COMPRESSED_IDS = tuple(compressed_blocks())

# 种子（方块物品）——它们的翻译键在 block. 前缀下，不在 item. 下。
# 详见 tools/check_lang.py 开头那段说明。
SEED_IDS = tuple(row[3] for row in DATA.CROPS)

# 所有"注册的是 BlockItem"的生成物：翻译键走 block. 前缀、
# 只有 items/<id>.json 没有 models/item/<id>.json。
# 漏一个就会在 check_assets 里被当成普通物品，去查不存在的
# `item.` 语言键与 `textures/item/<id>.png`，然后误报一大串。
BLOCK_ITEM_IDS = (tuple(compressed_blocks()) + tuple(wood_blocks())
                  + tuple(tree_blocks()) + tuple(SEED_IDS))


def check_assets(ids):
    lang_zh = load_json(os.path.join(ASSETS, "lang", "zh_cn.json")) or {}
    lang_en = load_json(os.path.join(ASSETS, "lang", "en_us.json")) or {}

    for item_id in sorted(ids):
        # 手写功能方块 + 全部生成出来的方块物品：
        #   语言键走 block. 前缀，客户端物品只需要 items/<id>.json。
        if (item_id in HAND_WRITTEN_BLOCKS or item_id in BLOCK_ITEM_IDS):
            if not any("block.%s.%s" % (NS, item_id) in d for d in (lang_zh, lang_en)):
                fail("%s 缺少语言键（block. 前缀）" % item_id)
            if not os.path.exists(os.path.join(ASSETS, "items", "%s.json" % item_id)):
                fail("%s 缺少客户端物品定义" % item_id)
            continue
        prefixes = ("item.",)
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
        "minecraft:apple", "minecraft:beetroot", "minecraft:stone_bricks",
        "minecraft:stone", "minecraft:wheat_seeds", "minecraft:furnace",
        "minecraft:cauldron",
        # 大型机配方要用的进阶材料
        "minecraft:iron_block", "minecraft:lava_bucket", "minecraft:copper_ingot",
        # 农夫乐事 / 森罗物语 / TFC 兼容配方里会用到的通用原版材料
        "minecraft:bowl", "minecraft:bucket", "minecraft:glass_bottle",
        "minecraft:honeycomb", "minecraft:sugar_cane", "minecraft:bamboo",
        "minecraft:melon_slice", "minecraft:pumpkin", "minecraft:sweet_berries",
        "minecraft:glow_berries", "minecraft:brown_mushroom", "minecraft:red_mushroom",
        "minecraft:crimson_fungus", "minecraft:warped_fungus",
        "minecraft:nether_wart", "minecraft:sea_pickle", "minecraft:cod",
        "minecraft:salmon", "minecraft:tropical_fish", "minecraft:pufferfish",
        "minecraft:rabbit", "minecraft:beetroot", "minecraft:beetroot_seeds",
        "minecraft:melon_seeds", "minecraft:pumpkin_seeds",
        # 灶火系统（炉灶 / 炒锅 / 蒸笼 / 汤锅）的配方材料
        "minecraft:bricks",
        # 锅里的"真做法"要用的：熬高汤的骨头、酿醋/酱的糖
        "minecraft:bone",
    }
    return {"%s:%s" % (NS, i) for i in ids} | allowed_vanilla


def check_recipes(dishes):
    known = known_items()
    recipes_dir = os.path.join(DATA_DIR, "recipe")
    have_recipe = set()
    dish_with_workbench = []

    for path in walk(recipes_dir, ".json"):
        obj = load_json(path)
        if obj is None:
            continue
        recipe_id = os.path.basename(path)[:-5]
        have_recipe.add(recipe_id)

        refs = []
        kind = obj.get("type", "")

        # ---- 外部模组的兼容配方：schema 完全是别人定的，不能按我们的规矩查 ----
        # （比如农夫乐事的切菜板 `result` 是**数组**、材料是 {"item": ...} 对象。）
        # 这里只做一件有意义的事：检查**我们自己**的物品引用没写错，
        # 其余的格式正确性由对方模组在加载时自己报错。
        if kind and not kind.startswith("minecraft:"):
            if not obj.get("neoforge:conditions"):
                fail("兼容配方 %s 缺少 neoforge:conditions（没装对方模组时会报错）"
                     % recipe_id)
            blob = json.dumps(obj, ensure_ascii=False)
            for ref in re.findall(r'"(%s:[a-z_0-9/]+)"' % NS, blob):
                if ref not in known:
                    fail("兼容配方 %s 引用了不存在的物品 %s" % (recipe_id, ref))
            continue

        if kind == "minecraft:crafting_shapeless":
            refs.extend(obj.get("ingredients", []))
        elif kind == "minecraft:crafting_shaped":
            refs.extend(obj.get("key", {}).values())
        elif kind == "minecraft:smelting":
            refs.append(obj.get("ingredient"))
        else:
            fail("配方 %s 使用了未知的 type=%s（本批次只支持工作台与熔炉）" % (recipe_id, kind))

        # 26.1 的 Ingredient 是纯字符串："minecraft:x" 或 "#tag"
        for ref in refs:
            if not isinstance(ref, str):
                fail("配方 %s 的材料不是字符串（26.1 要求纯字符串）: %r" % (recipe_id, ref))
                continue
            if ref.startswith("#"):
                tag_ns, tag_path = ref[1:].split(":", 1)
                if tag_ns == "c":
                    tag_file = os.path.join(RES, "data", "c", "tags", "item",
                                            "%s.json" % tag_path)
                elif tag_ns == NS:
                    tag_file = os.path.join(DATA_DIR, "tags", "item", "%s.json" % tag_path)
                else:
                    continue      # 原版标签默认存在
                if not os.path.exists(tag_file):
                    fail("配方 %s 引用了不存在的标签 %s" % (recipe_id, ref))
            elif ref.startswith(NS + ":") and ref not in known:
                fail("配方 %s 引用了不存在的物品 %s" % (recipe_id, ref))

        result = obj.get("result", {})
        rid = result.get("id")
        if rid and rid.startswith(NS + ":") and rid not in known:
            fail("配方 %s 的产物 %s 不存在" % (recipe_id, rid))
        # 菜品一律下锅做，不该再冒出工作台配方
        # （外部模组搭的桥不算：那种配方带 neoforge:conditions，是故意留的旁路）
        if rid and rid[len(NS) + 1:] in dishes and not obj.get("neoforge:conditions"):
            dish_with_workbench.append(recipe_id)

    # ---- 菜品：只认锅谱（ModRecipes 里的 CookEntry 表），不认工作台配方 ----
    if dish_with_workbench:
        fail("这些菜品还在用工作台配方，应该改成锅谱: %s"
             % ", ".join(sorted(dish_with_workbench)))

    cooked = cooked_items()
    missing = sorted(set(dishes) - cooked)
    if missing:
        fail("这些菜品没有任何锅谱（蒸/煮/炒）: %s" % ", ".join(missing))

    return len(list(walk(recipes_dir, ".json"))), len(have_recipe)


def cooked_items():
    """从生成的 ModRecipes.java 里读出所有锅谱产物（短名，不带命名空间）。

    锅谱是 Java 常量表而不是 JSON，所以这里直接扫源码 ——
    反正它由 gen_content.py 生成，格式是定死的。
    """
    path = os.path.join(
        "src", "main", "java", "com", "ctf", "chinese_traditional_food",
        "common", "recipe", "ModRecipes.java")
    if not os.path.exists(path):
        fail("找不到 %s（锅谱都写在这里，先跑 gen_content.py）" % path)
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    return set(re.findall(r'new CookEntry\("([a-z_0-9]+)"', source))


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
    # 原版 minecraft 命名空间下的标签（mineable/needs_xxx_tool 等）：
    # 这些是手写的，方块被删掉后很容易忘记同步，所以也要检查。
    mc_tags = os.path.join(RES, "data", "minecraft", "tags")
    for path in walk(mc_tags, ".json"):
        obj = load_json(path)
        if obj is None:
            continue
        n += 1
        for value in obj.get("values", []):
            if isinstance(value, str) and not value.startswith("#"):
                if value.startswith(NS + ":") and value not in known:
                    fail("原版标签 %s 引用了不存在的方块 %s"
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
    # 农作物（蔬菜 / 谷物 / 豆 / 种子）的画法在 crop_icons 里，
    # 这里要和 build_textures 一样把它们并进来，否则会误报"没有画法"。
    import crop_icons
    ICONS.bind_crops(crop_icons)
    missing = set()
    for row in (DATA.INGREDIENTS + DATA.SEEDS + DATA.SEASONINGS
                + DATA.FRUITS + DATA.VEGETABLES):
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
    for row in (DATA.INGREDIENTS + DATA.SEEDS + DATA.SEASONINGS
                + DATA.FRUITS + DATA.VEGETABLES):
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


def cook_table(src, name):
    """从 ModRecipes.java 里抠出某一张 CookEntry 表的正文。

    表长这样（中间是若干行 ``new CookEntry(...)``）：

        public static final List<CookEntry> WOK = List.of(
            ...
        );

    只抠到对应的 ``);`` 为止，免得把后面几张表也数进来。
    """
    head = "List<CookEntry> %s = List.of(" % name
    start = src.find(head)
    if start < 0:
        return ""
    start += len(head)
    end = src.find("\n    );", start)
    return src[start:end if end >= 0 else len(src)]


def check_cutting(ids):
    """硬编码处理表：条数要对得上，产出必须是本模组真实存在的物品。"""
    path = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                        "chinese_traditional_food", "common", "recipe", "ModRecipes.java")
    if not os.path.exists(path):
        fail("未找到生成的 ModRecipes.java")
        return 0
    with open(path, encoding="utf-8") as fh:
        src = fh.read()

    # 装置规则：new Entry("输入", "产出", 数量, "副产物", 概率F, tick)
    # 只包含**耗电**的两种：磨粉（MILLING）与脱壳（SHELLING）。
    # 蒸/煮/炒靠炉灶生火，它们用的是不带副产物的 CookEntry（下一段查）。
    entries = re.findall(
        r'new Entry\("([^"]+)",\s*"([^"]+)",\s*(\d+),\s*"([^"]*)",\s*([\d.]+)F,\s*(\d+)\)',
        src)
    expected = len(DATA.MILLING) + len(DATA.SHELLING)
    if len(entries) != expected:
        fail("ModRecipes.java 的装置规则数 %d 与 content_data 的 %d 不一致"
             % (len(entries), expected))
    for (_inp, out, _count, byproduct, _chance, _ticks) in entries:
        if out not in ids:
            fail("装置规则产出 %s 不是本模组的物品" % out)
        if byproduct and byproduct not in ids:
            fail("装置规则副产物 %s 不是本模组的物品" % byproduct)

    # 锅谱：new CookEntry("产出", 数量, tick, List.of("材料", ...))
    # 菜品**只**从这里产出，所以条数必须和 dish_cook_plan 算出来的一模一样。
    known = known_items()
    cook = re.findall(
        r'new CookEntry\("([^"]+)",\s*(\d+),\s*(\d+),\s*List\.of\(([^)]*)\)\)',
        src)
    # dish_cook_plan 只需要 id 与 kind，这里直接从元组表拼出来，
    # 免得把 collect() 整条链拉进校验脚本
    dish_rows = [dict(id=row[0], kind=row[4]) for row in DATA.DISHES]
    dish_ids = {row[0] for row in DATA.DISHES}
    plan = gen_content.dish_cook_plan(dish_rows)
    for pot, rows in plan.items():
        got = len(re.findall(r'new CookEntry\("', cook_table(src, pot)))
        if got != len(rows):
            fail("ModRecipes.java 的 %s 锅谱 %d 条，计划里是 %d 条"
                 % (pot, got, len(rows)))
    for (out, _count, _ticks, mats) in cook:
        if out not in ids and out not in dish_ids:
            fail("锅谱产出 %s 既不是本模组的物品也不是菜品" % out)
        for mat in re.findall(r'"([^"]+)"', mats):
            if mat.startswith("#"):
                continue        # 标签由 check_tags 负责
            # 材料要写成全名，和 known_items() 的"ns:path"形式对齐
            if mat not in known:
                fail("锅谱里的材料 %s 不存在" % mat)

    # 案板规则：new CuttingEntry("输入", "产出", true/false, tick)
    cutting = re.findall(r'new CuttingEntry\("([^"]+)",\s*"([^"]+)",\s*(true|false),\s*(\d+)\)',
                         src)
    if len(cutting) != len(DATA.CUTTING):
        fail("ModRecipes.java 的案板规则数 %d 与 content_data 的 %d 不一致"
             % (len(cutting), len(DATA.CUTTING)))
    for (_inp, out, _knife, _time) in cutting:
        if out not in ids:
            fail("案板切割产出 %s 不是本模组的物品" % out)

    return len(entries) + len(cook) + len(cutting)


def check_model_refs():
    """静态检查资源引用链：items -> model -> texture / blockstates -> model -> texture。

    这一类错误（拼错模型路径、少一张贴图）**编译期完全看不出来**，
    只有进游戏时才会在日志里刷 "Unable to load model"。
    在这里提前挡住，比每次开客户端捞日志便宜得多。
    """
    assets = os.path.join(RES, "assets", NS)
    item_defs = os.path.join(assets, "items")
    model_dir = os.path.join(assets, "models")
    tex_dir = os.path.join(assets, "textures")
    state_dir = os.path.join(assets, "blockstates")

    def resolve_model(ref):
        """把 "ns:path" / "path" 解析成 models/<path>.json；跨命名空间返回 None。"""
        if ":" in ref:
            space, path = ref.split(":", 1)
            if space != NS:
                return None          # 原版 / 其它模组的模型，本脚本不管
        else:
            path = ref
        return os.path.join(model_dir, path + ".json")

    def resolve_texture(ref):
        if ref.startswith("#"):
            return None              # 引用本模型 textures 段里的键，另行检查
        if ":" in ref:
            space, path = ref.split(":", 1)
            if space != NS:
                return None
        else:
            path = ref
        return os.path.join(tex_dir, path + ".png")

    n = 0

    # 1) 客户端物品定义 items/<id>.json -> 模型
    for path in walk(item_defs, ".json"):
        obj = load_json(path)
        ref = (obj or {}).get("model", {}).get("model")
        n += 1
        if not ref:
            fail("%s 没有 model.model" % os.path.relpath(path, ROOT))
            continue
        target = resolve_model(ref)
        if target is not None and not os.path.exists(target):
            fail("%s 指向了不存在的模型 %s" % (os.path.relpath(path, ROOT), ref))

    # 2) blockstates/<id>.json -> 模型
    for path in walk(state_dir, ".json"):
        obj = load_json(path) or {}
        for variant, body in obj.get("variants", {}).items():
            for entry in (body if isinstance(body, list) else [body]):
                ref = entry.get("model")
                n += 1
                if not ref:
                    continue
                target = resolve_model(ref)
                if target is not None and not os.path.exists(target):
                    fail("%s 的变体 %s 指向了不存在的模型 %s"
                         % (os.path.relpath(path, ROOT), variant, ref))
        for part in obj.get("multipart", []):
            ref = part.get("apply", {}).get("model")
            if ref:
                target = resolve_model(ref)
                if target is not None and not os.path.exists(target):
                    fail("%s 的 multipart 指向了不存在的模型 %s"
                         % (os.path.relpath(path, ROOT), ref))

    # 3) 模型里的 textures 段 -> 贴图文件
    for path in walk(model_dir, ".json"):
        obj = load_json(path) or {}
        declared = set(obj.get("textures", {}).keys())
        for key, ref in obj.get("textures", {}).items():
            if not isinstance(ref, str):
                continue
            n += 1
            target = resolve_texture(ref)
            if target is not None and not os.path.exists(target):
                fail("%s 的贴图 %s 不存在" % (os.path.relpath(path, ROOT), ref))

        # 4) 元素面里的 "#键" 必须在本模型的 textures 段里定义过。
        #    漏一个键的后果是那一面没有贴图 —— 进游戏只会打一行
        #    "Missing texture references in model"，编译期完全看不出来。
        for element in obj.get("elements", []):
            for face_name, face in (element.get("faces") or {}).items():
                ref = face.get("texture")
                n += 1
                if isinstance(ref, str) and ref.startswith("#") and ref[1:] not in declared:
                    fail("%s 的面 %s 引用了未定义的纹理键 %s"
                         % (os.path.relpath(path, ROOT), face_name, ref))

    # 5) 反向检查：有没有**没人用**的贴图（孤儿）。
    #    改设计时最容易漏掉这一步 —— 旧贴图会一直躺在资源目录里，
    #    既没人引用、又让人以为"机器用的是那张图"，非常难查。
    #    textures/gui 例外：界面的图是从 Java 里引用的，模型里看不到。
    used = set()
    for path in walk(model_dir, ".json"):
        obj = load_json(path) or {}
        for ref in obj.get("textures", {}).values():
            if isinstance(ref, str) and not ref.startswith("#"):
                target = resolve_texture(ref)
                if target is not None:
                    used.add(os.path.normcase(os.path.abspath(target)))
    for path in walk(tex_dir, ".png"):
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        if "/textures/gui/" in rel:
            continue
        n += 1
        if os.path.normcase(os.path.abspath(path)) not in used:
            fail("贴图 %s 没有任何模型引用（孤儿贴图）" % rel)

    return n


def check_item_models():
    """**反向**检查：每个注册进来的物品，都得有 `assets/<ns>/items/<id>.json`。

    26.1 起物品图标不再从方块模型或 `models/item/` 猜，必须显式声明。
    漏掉一个的后果**非常隐蔽**：

    * 不崩、不报红字、编译也过；
    * 只在完整日志（`run/logs/latest.log`）里留下一行
      `Missing item model for location <ns>:<id>`；
    * 游戏里那个物品直接变成没有贴图的东西。

    这一版就踩过：13 个树苗 + 果木原木全都没有物品定义，
    而排查时只搜了 `Missing model`（没搜 `Missing item model`），于是漏了很久。
    所以这里从 Java 注册处**反着**查一遍，彻底堵掉这类漏网。
    """
    java_root = os.path.join(ROOT, "src", "main", "java")
    items_dir = os.path.join(RES, "assets", NS, "items")
    pattern = re.compile(
        r"ITEMS\.(?:registerSimpleBlockItem|registerItem|register)\(\s*\"([^\"]+)\"")

    registered = {}
    for path in walk(java_root, ".java"):
        for lineno, line in enumerate(io.open(path, encoding="utf-8"), 1):
            m = pattern.search(line)
            if m:
                registered.setdefault(m.group(1),
                                      os.path.relpath(path, ROOT) + ":" + str(lineno))

    for item_id, where in sorted(registered.items()):
        if not os.path.exists(os.path.join(items_dir, "%s.json" % item_id)):
            fail("物品 %s 没有 items/%s.json（注册于 %s）—— "
                 "进游戏会报 Missing item model"
                 % (item_id, item_id, where))
    return len(registered)


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
    print("硬编码处理表: %d 条" % check_cutting(ids))
    print("资源引用: %d 处" % check_model_refs())
    print("物品图标定义: %d 个注册物品" % check_item_models())
    check_icon_kinds()

    if problems:
        print("\n发现 %d 个问题：" % len(problems))
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("\n全部检查通过。")


if __name__ == "__main__":
    main()
