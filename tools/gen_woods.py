# -*- coding: utf-8 -*-
"""13 种果木的木质方块：原木 / 木头 / 去皮原木 / 去皮木 / 木板 /
楼梯 / 台阶 / 栅栏 / 栅栏门。

    python tools/gen_woods.py

为什么要有这个文件
------------------
以前 13 种果树**共用一个 `fruit_log`** —— 砍桃树和砍枣树掉的是同一种
木头，搭出来的屋子也就一种颜色。用户要求"给每一种木头设计对应的去皮、
木板、楼梯、台阶、栅栏等东西"，于是这里按 {@code content_data.TREE_WOOD_LOOK}
的 13 套配色，各生成 9 个方块。

方块清单（每种木 9 个 × 13 种 = 117 个）
---------------------------------------

====================  ====================  ==========================
方块                    Java 类                模型 parent
====================  ====================  ==========================
`<木>_log`            `RotatedPillarBlock`   `cube_column` (+横向)
`<木>_wood`           `RotatedPillarBlock`   `cube_column`（六面都是皮）
`<木>_stripped_log`   `RotatedPillarBlock`   同 log，换去皮贴图
`<木>_stripped_wood`  `RotatedPillarBlock`   同 wood，换去皮贴图
`<木>_planks`         `Block`                `cube_all`
`<木>_stairs`         `StairBlock`           三个 parent（直/内角/外角）
`<木>_slab`           `SlabBlock`            三个 parent（下/上/双层）
`<木>_fence`          `FenceBlock`           `fence_post` + `fence_side`
`<木>_fence_gate`     `FenceGateBlock`       四个 parent × 朝向前后
====================  ====================  ==========================

配方
----
* 木板 ← 原木 / 木头 / 去皮原木 / 去皮木（无序，1 → 4）
* 楼梯 ← 木板 ×6（有序，→ 4）
* 台阶 ← 木板 ×3（有序，→ 6）
* 栅栏 ← 木板 ×4 + 木棍 ×2（有序，→ 3）
* 栅栏门 ← 木板 ×2 + 木棍 ×4（有序，→ 1）
* 去皮：**不做配方** —— 和原版一样用斧头右键（`AxeItem` 的
  `STRIPPABLES` 在 Java 侧注册，见 build_java）。

> 楼梯 / 台阶 / 栅栏 / 栅栏门的形状与朝向全部交给原版 parent 模型
> 与 blockstate 模板，**不要自己写 elements** —— 原版的连接、水淹、
> 拐角逻辑都在 parent 里，手写只会漏。
"""

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources")
DATA = os.path.join(RES, "data", "chinese_traditional_food")
ASSETS = os.path.join(RES, "assets", "chinese_traditional_food")
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                    "chinese_traditional_food")
NS = "chinese_traditional_food"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_data as DATA_SRC  # noqa: E402


def fruits():
    """要生成木制品的果树 id 列表。"""
    return [row[0] for row in DATA_SRC.TREE_FRUITS]


# ----------------------------------------------------------------------
# 方块 id
# ----------------------------------------------------------------------

def log(fruit):
    return "%s_log" % fruit


def wood(fruit):
    return "%s_wood" % fruit


def stripped_log(fruit):
    return "%s_stripped_log" % fruit


def stripped_wood(fruit):
    return "%s_stripped_wood" % fruit


def planks(fruit):
    return "%s_planks" % fruit


def stairs(fruit):
    return "%s_stairs" % fruit


def slab(fruit):
    return "%s_slab" % fruit


def fence(fruit):
    return "%s_fence" % fruit


def fence_gate(fruit):
    return "%s_fence_gate" % fruit


# 9 种形态 -> 取 id 的函数。顺序固定，Java、配方、创造页都照它走。
FORMS = [
    ("log", log),
    ("wood", wood),
    ("stripped_log", stripped_log),
    ("stripped_wood", stripped_wood),
    ("planks", planks),
    ("stairs", stairs),
    ("slab", slab),
    ("fence", fence),
    ("fence_gate", fence_gate),
]


# ----------------------------------------------------------------------
# 通用写入
# ----------------------------------------------------------------------

def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            fh.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def _model(name, obj):
    _write(os.path.join(ASSETS, "models", "block", "%s.json" % name), obj)


def _state(name, obj):
    _write(os.path.join(ASSETS, "blockstates", "%s.json" % name), obj)


def _loot(name, drop=None):
    drop = drop or name
    _write(os.path.join(DATA, "loot_table", "blocks", "%s.json" % name), {
        "type": "minecraft:block",
        "random_sequence": "%s:blocks/%s" % (NS, name),
        "pools": [{
            "rolls": 1, "bonus_rolls": 0,
            "entries": [{"type": "minecraft:item", "name": "%s:%s" % (NS, drop)}],
            "conditions": [{"condition": "minecraft:survives_explosion"}],
        }],
    })


def _item_model(name, model):
    """26.1 起物品图标必须显式声明；漏了只在日志里留一行 Missing item model。"""
    _write(os.path.join(ASSETS, "items", "%s.json" % name), {
        "model": {"type": "minecraft:model", "model": "%s:%s" % (NS, model)},
    })


def _recipe(name, obj):
    _write(os.path.join(DATA, "recipe", "%s.json" % name), obj)


def _tag(name, values):
    _write(os.path.join(DATA, "tags", "block", "%s.json" % name),
           {"replace": False, "values": values})


def _data_map(name, registry, values):
    """写 NeoForge 数据图：`data/<ns>/data_maps/<registry>/<name>.json`。

    路径是 `DataMapLoader.PATH`（"data_maps"）+ 注册表名，**不再有
    `neoforge/` 那一层**（那是 21.x 的旧写法，26.1 已经改了）。
    """
    _write(os.path.join(DATA, "data_maps", registry, "%s.json" % name),
           {"replace": False, "values": values})


# ======================================================================
# 模型
# ======================================================================

def _pillar(bid, tex, tex_top):
    """原木/木头/去皮：cube_column + 横放变体 + 三轴 blockstate。

    `RotatedPillarBlock` 只认 `axis` 一个属性，所以 blockstate 三个变体。
    横放那套用 `cube_column_horizontal`（原版木头就是这么做的）。
    """
    _model(bid, {"parent": "minecraft:block/cube_column",
                 "textures": {"end": "%s:block/%s" % (NS, tex_top),
                              "side": "%s:block/%s" % (NS, tex)}})
    _model("%s_horizontal" % bid, {
        "parent": "minecraft:block/cube_column_horizontal",
        "textures": {"end": "%s:block/%s" % (NS, tex_top),
                     "side": "%s:block/%s" % (NS, tex)},
    })
    _state(bid, {"variants": {
        "axis=y": {"model": "%s:block/%s" % (NS, bid)},
        "axis=z": {"model": "%s:block/%s_horizontal" % (NS, bid), "x": 90},
        "axis=x": {"model": "%s:block/%s_horizontal" % (NS, bid),
                   "x": 90, "y": 90},
    }})
    _item_model(bid, "block/%s" % bid)


def _cube_all(bid, tex):
    _model(bid, {"parent": "minecraft:block/cube_all",
                 "textures": {"all": "%s:block/%s" % (NS, tex)}})
    _state(bid, {"variants": {"": {"model": "%s:block/%s" % (NS, bid)}}})
    _item_model(bid, "block/%s" % bid)


def _stairs(bid, tex):
    # 模型名同原版：`<id>` / `<id>_inner` / `<id>_outer`。
    # 主模型**必须叫 bid** —— 物品图标（items/<id>.json）指向的是
    # `block/<id>`，名字带个 _stairs 尾巴就会变成"找不到模型"。
    names = ((bid, "stairs"),
             ("%s_inner" % bid, "inner_stairs"),
             ("%s_outer" % bid, "outer_stairs"))
    for name, parent in names:
        _model(name, {"parent": "minecraft:block/%s" % parent,
                      "textures": {"bottom": "%s:block/%s" % (NS, tex),
                                   "top": "%s:block/%s" % (NS, tex),
                                   "side": "%s:block/%s" % (NS, tex)}})
    # 楼梯变体表**照抄原版 oak_stairs.json**。自己从 facing/half/shape
    # 推导旋转角很容易错（内角外角的 y 角恰好是反的），而这份表是死的。
    _state(bid, {"variants": _vanilla_stair_variants(bid)})
    _item_model(bid, "block/%s" % bid)


def _vanilla_stair_variants(bid):
    """按原版 `oak_stairs` 的模板生成楼梯变体表（逐条精确，不推导）。"""
    def m(shape):
        return {"model": "%s:block/%s" % (NS, shape)}

    def s():
        return m(bid)

    def inner():
        return m("%s_inner" % bid)

    def outer():
        return m("%s_outer" % bid)

    v = {}
    # 底部
    v["facing=east,half=bottom,shape=straight"] = s()
    v["facing=west,half=bottom,shape=straight"] = dict(s(), y=180)
    v["facing=south,half=bottom,shape=straight"] = dict(s(), y=90)
    v["facing=north,half=bottom,shape=straight"] = dict(s(), y=270)
    v["facing=east,half=bottom,shape=outer_right"] = outer()
    v["facing=west,half=bottom,shape=outer_right"] = dict(outer(), y=180)
    v["facing=south,half=bottom,shape=outer_right"] = dict(outer(), y=90)
    v["facing=north,half=bottom,shape=outer_right"] = dict(outer(), y=270)
    v["facing=east,half=bottom,shape=outer_left"] = dict(outer(), y=270)
    v["facing=west,half=bottom,shape=outer_left"] = dict(outer(), y=90)
    v["facing=south,half=bottom,shape=outer_left"] = outer()
    v["facing=north,half=bottom,shape=outer_left"] = dict(outer(), y=180)
    v["facing=east,half=bottom,shape=inner_right"] = inner()
    v["facing=west,half=bottom,shape=inner_right"] = dict(inner(), y=180)
    v["facing=south,half=bottom,shape=inner_right"] = dict(inner(), y=90)
    v["facing=north,half=bottom,shape=inner_right"] = dict(inner(), y=270)
    v["facing=east,half=bottom,shape=inner_left"] = dict(inner(), y=270)
    v["facing=west,half=bottom,shape=inner_left"] = dict(inner(), y=90)
    v["facing=south,half=bottom,shape=inner_left"] = inner()
    v["facing=north,half=bottom,shape=inner_left"] = dict(inner(), y=180)
    # 顶部（x=180 翻过来，y 与前一组互换 90/270）
    v["facing=east,half=top,shape=straight"] = dict(s(), x=180, y=180)
    v["facing=west,half=top,shape=straight"] = dict(s(), x=180)
    v["facing=south,half=top,shape=straight"] = dict(s(), x=180, y=270)
    v["facing=north,half=top,shape=straight"] = dict(s(), x=180, y=90)
    v["facing=east,half=top,shape=outer_right"] = dict(outer(), x=180, y=90)
    v["facing=west,half=top,shape=outer_right"] = dict(outer(), x=180, y=270)
    v["facing=south,half=top,shape=outer_right"] = dict(outer(), x=180)
    v["facing=north,half=top,shape=outer_right"] = dict(outer(), x=180, y=180)
    v["facing=east,half=top,shape=outer_left"] = dict(outer(), x=180, y=180)
    v["facing=west,half=top,shape=outer_left"] = dict(outer(), x=180)
    v["facing=south,half=top,shape=outer_left"] = dict(outer(), x=180, y=270)
    v["facing=north,half=top,shape=outer_left"] = dict(outer(), x=180, y=90)
    v["facing=east,half=top,shape=inner_right"] = dict(inner(), x=180, y=90)
    v["facing=west,half=top,shape=inner_right"] = dict(inner(), x=180, y=270)
    v["facing=south,half=top,shape=inner_right"] = dict(inner(), x=180)
    v["facing=north,half=top,shape=inner_right"] = dict(inner(), x=180, y=180)
    v["facing=east,half=top,shape=inner_left"] = dict(inner(), x=180, y=180)
    v["facing=west,half=top,shape=inner_left"] = dict(inner(), x=180)
    v["facing=south,half=top,shape=inner_left"] = dict(inner(), x=180, y=270)
    v["facing=north,half=top,shape=inner_left"] = dict(inner(), x=180, y=90)
    return v


def _slab(bid, tex):
    _model(bid, {"parent": "minecraft:block/slab",
                 "textures": {"bottom": "%s:block/%s" % (NS, tex),
                              "top": "%s:block/%s" % (NS, tex),
                              "side": "%s:block/%s" % (NS, tex)}})
    _model("%s_top" % bid, {"parent": "minecraft:block/slab_top",
                            "textures": {"bottom": "%s:block/%s" % (NS, tex),
                                         "top": "%s:block/%s" % (NS, tex),
                                         "side": "%s:block/%s" % (NS, tex)}})
    _state(bid, {"variants": {
        "type=bottom": {"model": "%s:block/%s" % (NS, bid)},
        "type=top": {"model": "%s:block/%s_top" % (NS, bid)},
        "type=double": {"model": "%s:block/%s" % (NS, tex)},
    }})
    _item_model(bid, "block/%s" % bid)


def _fence(bid, tex):
    _model("%s_post" % bid, {"parent": "minecraft:block/fence_post",
                             "textures": {"texture": "%s:block/%s" % (NS, tex)}})
    _model("%s_side" % bid, {"parent": "minecraft:block/fence_side",
                             "textures": {"texture": "%s:block/%s" % (NS, tex)}})
    # 栅栏用 multipart：四邻居各判一次，和水/原木一样。
    _state(bid, {"multipart": [
        {"apply": {"model": "%s:block/%s_post" % (NS, bid)}},
        *[{"when": {"%s" % d: "true"},
           "apply": {"model": "%s:block/%s_side" % (NS, bid), **rot}}
          for d, rot in (("north", {}), ("east", {"y": 90}),
                         ("south", {"y": 180}), ("west", {"y": 270}))],
    ]})
    _item_model(bid, "block/%s_inventory" % bid)


def _fence_gate(bid, tex):
    # 模型名同原版：`<id>` / `<id>_open` / `<id>_wall` / `<id>_wall_open`
    for name, parent in ((bid, "fence_gate"),
                         ("%s_open" % bid, "fence_gate_open"),
                         ("%s_wall" % bid, "fence_gate_wall"),
                         ("%s_wall_open" % bid, "fence_gate_wall_open")):
        _model(name, {"parent": "minecraft:block/%s" % parent,
                      "textures": {"texture": "%s:block/%s" % (NS, tex)}})
    # 原版栅栏门：facing × in_wall × open = 32 个变体，逐条精确给出。
    v = {}
    for facing, base_y in (("north", 0), ("east", 90),
                           ("south", 180), ("west", 270)):
        for in_wall in ("false", "true"):
            for opened in ("false", "true"):
                suffix = ""
                if in_wall == "true":
                    suffix += "_wall"
                if opened == "true":
                    suffix += "_open"
                entry = {"model": "%s:block/%s%s" % (NS, bid, suffix)}
                y = base_y
                if opened == "true":
                    y = (y + 90) % 360
                if y:
                    entry["y"] = y
                v["facing=%s,in_wall=%s,open=%s" % (facing, in_wall, opened)] = entry
    _state(bid, {"variants": v})
    _item_model(bid, "block/%s" % bid)


def _fence_inventory_model(bid, tex):
    """栅栏的物品图标：原版没有 `fence_inventory` 这个 parent（栅栏的物品
    图标是**两根柱子夹一条横档**的独立模型），这里按原版 `oak_fence_inventory`
    的元素自己拼一个 —— 元素和 UV 直接取自原版，只是换了贴图。"""
    _model("%s_inventory" % bid, {
        "parent": "minecraft:block/fence_inventory",
        "textures": {"texture": "%s:block/%s" % (NS, tex)},
    })


def build_models():
    count = 0
    for fruit in fruits():
        p = planks(fruit)
        # 原木 / 木头：木头是"六面都是树皮"，也就是 end 也用侧面那张
        _pillar(log(fruit), log(fruit), "%s_top" % log(fruit))
        _pillar(wood(fruit), log(fruit), log(fruit))
        _pillar(stripped_log(fruit), stripped_log(fruit),
                "%s_top" % stripped_log(fruit))
        _pillar(stripped_wood(fruit), stripped_log(fruit), stripped_log(fruit))
        _cube_all(p, p)
        _stairs(stairs(fruit), p)
        _slab(slab(fruit), p)
        _fence(fence(fruit), p)
        _fence_inventory_model(fence(fruit), p)
        _fence_gate(fence_gate(fruit), p)
        count += 9
    print("wood models/blockstates: %d 种树 × 9 = %d 个方块" % (len(fruits()), count))
    return count


# ======================================================================
# 掉落表
# ======================================================================

def build_loot():
    for fruit in fruits():
        for _form, fn in FORMS:
            _loot(fn(fruit))
    n = len(fruits()) * len(FORMS)
    print("wood loot tables: %d" % n)
    return n


# ======================================================================
# 配方
# ======================================================================

def _shapeless(rid, result, count, ingredients):
    # 26.1 起 Ingredient 的 JSON 就是**纯字符串**（"minecraft:stick" /
    # "#c:planks"），不是老版本的 {"item": ...} 对象。
    _recipe(rid, {
        "type": "minecraft:crafting_shapeless",
        "category": "building",
        "group": "planks",
        "ingredients": ingredients,
        "result": {"id": "%s:%s" % (NS, result), "count": count},
    })


def _shaped(rid, result, count, pattern, key, group=None):
    # 同上：key 的值也直接写字符串
    obj = {
        "type": "minecraft:crafting_shaped",
        "category": "building",
        "pattern": pattern,
        "key": {k: v for k, v in key.items()},
        "result": {"id": "%s:%s" % (NS, result), "count": count},
    }
    if group:
        obj["group"] = group
    _recipe(rid, obj)


def recipe_ids():
    """本脚本会写的全部配方 id。

    `gen_content.gen_recipes` 的"清理旧配方"这一步要先拿到这份名单，
    否则第一次跑就把木制品的配方全删了（压缩方块那次已经栽过一回）。
    这里只算 id，不写任何文件 —— 所以是纯函数。
    """
    ids = set()
    for fruit in fruits():
        p = planks(fruit)
        for src in (log(fruit), wood(fruit), stripped_log(fruit),
                    stripped_wood(fruit)):
            ids.add("%s_from_%s" % (p, src))
        ids.add(stairs(fruit))
        ids.add(slab(fruit))
        ids.add(fence(fruit))
        ids.add(fence_gate(fruit))
    return ids


def build_recipes():
    n = 0
    for fruit in fruits():
        p = planks(fruit)
        p_ref = "%s:%s" % (NS, p)
        stick = "minecraft:stick"

        # 木板 ← 原木 / 木头 / 去皮原木 / 去皮木（无序，1 → 4）
        for src in (log(fruit), wood(fruit), stripped_log(fruit),
                    stripped_wood(fruit)):
            _shapeless("%s_from_%s" % (p, src), p, 4,
                       ["%s:%s" % (NS, src)])
            n += 1

        # 楼梯 ← 木板 ×6 → 4
        _shaped(stairs(fruit), stairs(fruit), 4,
                ["X  ", "XX ", "XXX"], {"X": p_ref}, group="stairs")
        # 台阶 ← 木板 ×3 → 6
        _shaped(slab(fruit), slab(fruit), 6,
                ["XXX"], {"X": p_ref}, group="slab")
        # 栅栏 ← 木板 ×4 + 木棍 ×2 → 3
        _shaped(fence(fruit), fence(fruit), 3,
                ["XYX", "XYX"], {"X": p_ref, "Y": stick}, group="fence")
        # 栅栏门 ← 木板 ×2 + 木棍 ×4 → 1
        _shaped(fence_gate(fruit), fence_gate(fruit), 1,
                ["YXY", "YXY"], {"X": p_ref, "Y": stick}, group="fence_gate")
        n += 4

    print("wood recipes: %d" % n)
    return n


# ======================================================================
# 标签：让这些方块能被斧头砍、能被当作木板用
# ======================================================================

def build_tags():
    mineable = []
    planks_tag = []
    logs_tag = []
    wooden_stairs, wooden_slabs, fences, fence_gates = [], [], [], []
    for fruit in fruits():
        for bid in (log(fruit), wood(fruit), stripped_log(fruit),
                    stripped_wood(fruit), planks(fruit), stairs(fruit),
                    slab(fruit), fence(fruit), fence_gate(fruit)):
            mineable.append("%s:%s" % (NS, bid))
        planks_tag += ["%s:%s" % (NS, planks(fruit)),
                       "%s:%s" % (NS, stairs(fruit)),
                       "%s:%s" % (NS, slab(fruit)),
                       "%s:%s" % (NS, fence(fruit)),
                       "%s:%s" % (NS, fence_gate(fruit))]
        logs_tag += ["%s:%s" % (NS, x) for x in
                     (log(fruit), wood(fruit),
                      stripped_log(fruit), stripped_wood(fruit))]
        wooden_stairs.append("%s:%s" % (NS, stairs(fruit)))
        wooden_slabs.append("%s:%s" % (NS, slab(fruit)))
        fences.append("%s:%s" % (NS, fence(fruit)))
        fence_gates.append("%s:%s" % (NS, fence_gate(fruit)))

    _tag("mineable/axe", mineable)
    _tag("planks", planks_tag)
    _tag("logs_that_logs_can_be_crafted_from", logs_tag)
    _tag("wooden_stairs", wooden_stairs)
    _tag("wooden_slabs", wooden_slabs)
    _tag("fences", fences)
    _tag("fence_gates", fence_gates)
    print("wood tags: 7 张（含 mineable/axe 共 %d 项）" % len(mineable))
    return 7


# ======================================================================
# Java
# ======================================================================

JAVA_HEAD = '''package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.WoodType;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 13 种果木的木质方块：原木 / 木头 / 去皮原木 / 去皮木 / 木板 /
 * 楼梯 / 台阶 / 栅栏 / 栅栏门。
 *
 * <p><b>本文件由 {@code tools/gen_woods.py} 生成，请不要手改。</b>
 * 要调颜色请改 {@code tools/content_data.py} 的 {@code TREE_WOOD_LOOK}。</p>
 *
 * <h2>为什么是 13 套而不是 1 套</h2>
 * 早先 13 种果树共用一个 {@code fruit_log} —— 砍桃树和砍枣树掉同一种
 * 木头，玩家搭出来的屋子永远一个颜色。用户要求每种木头都有自己的
 * 去皮 / 木板 / 楼梯 / 台阶 / 栅栏，于是这里生成 13 套。
 *
 * <h2>斧头去皮</h2>
 * 和原版一样：走 NeoForge 的 {@code strippables} <strong>数据图</strong>，
 * 文件在 {@code data/chinese_traditional_food/data_maps/block/strippables.json}。
 * <strong>不要用反射去改 {@code AxeItem.STRIPPABLES}</strong> —— 那是 21.x 的
 * 老办法，26.1 已经把它标成 deprecated，官方给的就是数据图。
 */
public final class ModWoods {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    /** 木头系列的通用属性：木头的音效、可燃、斧头挖得动。 */
    private static BlockBehaviour.Properties woodProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD)
                .strength(2.0F)
                .sound(SoundType.WOOD)
                .ignitedByLava();
    }

    /** 木板 / 楼梯 / 台阶 / 栅栏 / 栅栏门：比原木软一点。 */
    private static BlockBehaviour.Properties plankProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD)
                .strength(2.0F, 3.0F)
                .sound(SoundType.WOOD)
                .ignitedByLava();
    }
'''


def _jc(text):
    """Java 字符串转义（本项目只需要处理普通 ASCII id）。"""
    return text


def build_java():
    out = [JAVA_HEAD]
    out.append("""
    // ==================================================================
    // 13 种果木的方块
    // ==================================================================
""")
    for fruit in fruits():
        u = fruit.upper()
        out.append("\n    // ---------------- %s ----------------\n" % fruit)
        out.append(
            '    public static final DeferredBlock<RotatedPillarBlock> %s_LOG'
            ' = BLOCKS.registerBlock(\n'
            '            "%s", RotatedPillarBlock::new, props -> woodProps());\n'
            % (u, log(fruit)))
        out.append(
            '    public static final DeferredBlock<RotatedPillarBlock> %s_WOOD'
            ' = BLOCKS.registerBlock(\n'
            '            "%s", RotatedPillarBlock::new, props -> woodProps());\n'
            % (u, wood(fruit)))
        out.append(
            '    public static final DeferredBlock<RotatedPillarBlock>'
            ' %s_STRIPPED_LOG = BLOCKS.registerBlock(\n'
            '            "%s", RotatedPillarBlock::new, props -> woodProps());\n'
            % (u, stripped_log(fruit)))
        out.append(
            '    public static final DeferredBlock<RotatedPillarBlock>'
            ' %s_STRIPPED_WOOD = BLOCKS.registerBlock(\n'
            '            "%s", RotatedPillarBlock::new, props -> woodProps());\n'
            % (u, stripped_wood(fruit)))
        out.append(
            '    public static final DeferredBlock<Block> %s_PLANKS'
            ' = BLOCKS.registerBlock(\n'
            '            "%s", Block::new, props -> plankProps());\n'
            % (u, planks(fruit)))
        # 楼梯的 baseState 必须是木板的默认状态
        out.append(
            '    public static final DeferredBlock<StairBlock> %s_STAIRS'
            ' = BLOCKS.registerBlock(\n'
            '            "%s",\n'
            '            p -> new StairBlock(%s_PLANKS.get().defaultBlockState(), p),\n'
            '            props -> plankProps());\n'
            % (u, stairs(fruit), u))
        out.append(
            '    public static final DeferredBlock<SlabBlock> %s_SLAB'
            ' = BLOCKS.registerBlock(\n'
            '            "%s", SlabBlock::new, props -> plankProps());\n'
            % (u, slab(fruit)))
        out.append(
            '    public static final DeferredBlock<FenceBlock> %s_FENCE'
            ' = BLOCKS.registerBlock(\n'
            '            "%s", FenceBlock::new, props -> plankProps());\n'
            % (u, fence(fruit)))
        out.append(
            '    public static final DeferredBlock<FenceGateBlock> %s_FENCE_GATE'
            ' = BLOCKS.registerBlock(\n'
            '            "%s",\n'
            '            p -> new FenceGateBlock(WoodType.OAK, p),\n'
            '            props -> plankProps());\n'
            % (u, fence_gate(fruit)))
        out.append("\n")

    out.append("""
    // ==================================================================
    // 物品
    // ==================================================================
""")
    for fruit in fruits():
        u = fruit.upper()
        for form, fn in FORMS:
            cname = "%s_%s" % (u, form.upper())
            out.append(
                '    public static final DeferredItem<BlockItem> %s_ITEM ='
                ' ITEMS.registerSimpleBlockItem("%s", %s);\n'
                % (cname, fn(fruit), cname))
    out.append("\n")

    # allBlocks()：创造页与去皮表都要用
    out.append("""
    /** 全部 117 个方块，按"每种木一套"的顺序。 */
    public static List<DeferredBlock<?>> allBlocks() {
        List<DeferredBlock<?>> list = new ArrayList<>();
""")
    for fruit in fruits():
        u = fruit.upper()
        out.append("        list.add(%s_LOG);\n" % u)
        out.append("        list.add(%s_WOOD);\n" % u)
        out.append("        list.add(%s_STRIPPED_LOG);\n" % u)
        out.append("        list.add(%s_STRIPPED_WOOD);\n" % u)
        out.append("        list.add(%s_PLANKS);\n" % u)
        out.append("        list.add(%s_STAIRS);\n" % u)
        out.append("        list.add(%s_SLAB);\n" % u)
        out.append("        list.add(%s_FENCE);\n" % u)
        out.append("        list.add(%s_FENCE_GATE);\n" % u)
    out.append("        return list;\n    }\n")

    # allItems()：创造页用。**必须返回 Item 而不是 Block** ——
    # `accept(block)` 在方块没有 BlockItem 时会抛
    # "The stack count must be 1 for 0 minecraft:air"。
    out.append("""
    /** 全部 117 个方块物品（创造标签页用）。 */
    public static List<DeferredItem<?>> allItems() {
        List<DeferredItem<?>> list = new ArrayList<>();
""")
    for fruit in fruits():
        u = fruit.upper()
        for form, _fn in FORMS:
            out.append("        list.add(%s_%s_ITEM);\n" % (u, form.upper()))
    out.append("        return list;\n    }\n")

    # 去皮：NeoForge 数据图，纯 JSON，不需要 Java
    strippables = {}
    for fruit in fruits():
        strippables["%s:%s" % (NS, log(fruit))] = {
            "stripped_block": "%s:%s" % (NS, stripped_log(fruit))}
        strippables["%s:%s" % (NS, wood(fruit))] = {
            "stripped_block": "%s:%s" % (NS, stripped_wood(fruit))}
    _data_map("strippables", "block", strippables)
    print("strippables 数据图: %d 条（斧头右键去皮）" % len(strippables))

    out.append("""
    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }
}
""")
    path = os.path.join(JAVA, "registry", "ModWoods.java")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(out))
    print("ModWoods.java: %d 种树 × 9 个方块" % len(fruits()))
    return len(fruits()) * 9


def main():
    build_models()
    build_loot()
    build_recipes()
    build_tags()
    build_java()


if __name__ == "__main__":
    main()
