# -*- coding: utf-8 -*-
"""作物植株：把 33 种种子变成能种、能长、能收的植株。

    python tools/gen_crops.py

产出
----
* Java：{@code registry/ModCrops.java}（33 个植株方块 + 33 个种子物品 + 31 个野生植株）
* 资源：blockstates / models / items / loot_table
* 世界生成：configured_feature + placed_feature + biome_modifier（野生作物）

三件事一件一件说
----------------

**一、种子物品就是方块物品。**
种子不用单独注册成 {@code Item} —— 它是植株方块的 {@code BlockItem}，
右键耕地就能种下去。于是"种子"这个概念在代码里只有一份。

**二、掉落写在战利品表里，不写在 Java 里。**
成熟（{@code age=7}）掉 1 份产物 + 2~4 份种子；没熟只掉 1 份种子
（和原版小麦一个规矩）。幸运附魔对两者都有效。

**三、野生作物是另一套方块。**
它长在草地和泥土上、没有生长阶段（一出来就是熟的），
打掉直接给产物 + 种子。世界生成靠三个 JSON 串起来：

    biome_modifier（往哪些群系加）
        └─ placed_feature（加多少、什么概率、怎么挑位置）
               └─ configured_feature（具体放哪个方块）

这三层是原版的固定套路，所以野生作物在哪、多稀罕全是数据说了算，
再加一种作物只要往 {@code CROPS} 里写一行。
"""

import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources")
DATA = os.path.join(RES, "data", "chinese_traditional_food")
ASSETS = os.path.join(RES, "assets", "chinese_traditional_food")
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                    "chinese_traditional_food")
NS = "chinese_traditional_food"

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_data as DATA_SRC  # noqa: E402

# 八个生长阶段 -> 一阶段一张贴图。
#
# 原版作物就是八个阶段、每个阶段单独一张（`wheat_stage0..7`），
# 这样"长大了"才是一格格看得见的；之前把相邻两阶合并成一张，
# 种下去会有两段时间完全看不出变化。
AGE_TO_STAGE = tuple(range(8))

# 野外一丛能采到多少种子。给得比种地少一点，鼓励玩家把苗移回自家田里。
WILD_SEED_MIN = 1
WILD_SEED_MAX = 2


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            fh.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def _const(name):
    return name.upper()


# ======================================================================
# 名字
# ======================================================================

def crop_block(crop_id):
    return "%s_crop" % crop_id


def wild_block(crop_id):
    return "wild_%s" % crop_id


def crop_texture(crop_id, stage):
    return "%s_crop_stage%d" % (crop_id, stage)


def wild_texture(crop_id):
    return "wild_%s" % crop_id


# ======================================================================
# 方块状态 + 模型
# ======================================================================

def build_models():
    n = 0
    for (crop_id, _zh, _en, _seed, _prod, _habit) in DATA_SRC.CROPS:
        bid = crop_block(crop_id)

        # ---- 八个生长阶段各自的模型 ----
        for stage in range(8):
            _write(os.path.join(ASSETS, "models", "block",
                                "%s.json" % crop_texture(crop_id, stage)),
                   {
                       "parent": "minecraft:block/crop",
                       "textures": {
                           "crop": "%s:block/%s" % (NS, crop_texture(crop_id, stage)),
                       },
                   })

        # ---- 八个年龄各用自己那张 ----
        variants = {}
        for age in range(8):
            variants["age=%d" % age] = {
                "model": "%s:block/%s" % (NS, crop_texture(crop_id, AGE_TO_STAGE[age]))
            }
        _write(os.path.join(ASSETS, "blockstates", "%s.json" % bid),
               {"variants": variants})

        # ---- 野生植株：一张图、没有年龄 ----
        wbid = wild_block(crop_id)
        _write(os.path.join(ASSETS, "models", "block", "%s.json" % wbid),
               {
                   "parent": "minecraft:block/crop",
                   "textures": {"crop": "%s:block/%s" % (NS, wild_texture(crop_id))},
               })
        _write(os.path.join(ASSETS, "blockstates", "%s.json" % wbid),
               {"variants": {"": {"model": "%s:block/%s" % (NS, wbid)}}})
        n += 1
    print("crop models/blockstates: %d 种作物" % n)


# ======================================================================
# 掉落
# ======================================================================

def _fortune(multiplier=1):
    return {
        "function": "minecraft:apply_bonus",
        "enchantment": "minecraft:fortune",
        "formula": "minecraft:uniform_bonus_count",
        "parameters": {"bonusMultiplier": multiplier},
    }


def _uniform(mn, mx):
    return {"type": "minecraft:uniform", "min": float(mn), "max": float(mx)}


def _item(name, functions=None):
    entry = {"type": "minecraft:item", "name": name}
    if functions:
        entry["functions"] = functions
    return entry


def _is_ripe(block_id, ripe=True):
    cond = {
        "condition": "minecraft:block_state_property",
        "block": "%s:%s" % (NS, block_id),
        "properties": {"age": "7"},
    }
    return cond if ripe else {"condition": "minecraft:inverted", "term": cond}


def build_loot():
    n = 0
    for (crop_id, _zh, _en, seed, prod, _habit) in DATA_SRC.CROPS:
        bid = crop_block(crop_id)
        produce = "%s:%s" % (NS, prod)
        seeds = "%s:%s" % (NS, seed)

        # 三池：熟了的产物 / 种子 / 没熟时的种子补偿
        pools = [
            {
                "rolls": 1, "bonus_rolls": 0,
                "entries": [_item(produce, [_fortune(1)])],
                "conditions": [_is_ripe(bid)],
            },
            {
                "rolls": 1, "bonus_rolls": 0,
                "entries": [_item(seeds, [
                    {"function": "minecraft:set_count",
                     "count": _uniform(2, 4)},
                    _fortune(1),
                ])],
                "conditions": [_is_ripe(bid)],
            },
            {
                # 没熟就拔：至少把种子还给你，和原版一个规矩
                "rolls": 1, "bonus_rolls": 0,
                "entries": [_item(seeds)],
                "conditions": [_is_ripe(bid, ripe=False)],
            },
        ]
        _write(os.path.join(DATA, "loot_table", "blocks", "%s.json" % bid), {
            "type": "minecraft:block",
            "random_sequence": "%s:blocks/%s" % (NS, bid),
            "pools": pools,
        })

        wbid = wild_block(crop_id)
        _write(os.path.join(DATA, "loot_table", "blocks", "%s.json" % wbid), {
            "type": "minecraft:block",
            "random_sequence": "%s:blocks/%s" % (NS, wbid),
            "pools": [
                {"rolls": 1, "bonus_rolls": 0,
                 "entries": [_item(produce)]},
                {"rolls": 1, "bonus_rolls": 0,
                 "entries": [_item(seeds, [
                     {"function": "minecraft:set_count",
                      "count": _uniform(WILD_SEED_MIN, WILD_SEED_MAX)},
                 ])]},
            ],
        })
        n += 2
    print("crop loot tables: %d" % n)


# ======================================================================
# 世界生成：野生作物
# ======================================================================

def build_worldgen():
    n = 0
    wild = {row[0]: row for row in DATA_SRC.WILD_CROPS}
    for (crop_id, _zh, _en, _seed, _prod, _habit) in DATA_SRC.CROPS:
        if crop_id not in wild:
            continue
        (_cid, chance, tries) = wild[crop_id]
        habitat = DATA_SRC.WILD_HABITAT.get(crop_id, "temperate")
        biome_tag = DATA_SRC.WILD_BIOMES[habitat]
        wbid = wild_block(crop_id)
        state = {"Name": "%s:%s" % (NS, wbid)}

        # ---- 1. 放哪个方块 ----
        _write(os.path.join(DATA, "worldgen", "configured_feature",
                            "%s.json" % wbid), {
            "type": "minecraft:simple_block",
            "config": {
                "to_place": {
                    "type": "minecraft:weighted_state_provider",
                    "entries": [{"data": state, "weight": 1}],
                },
            },
        })

        # ---- 2. 放多少、放哪 ----
        # 顺序有讲究：
        #   rarity_filter  先按概率筛掉一大批区块（"稀罕"就是靠它）
        #   in_square      在区块里随机取一点
        #   heightmap      落到地表
        #   count          一个点周围试着长几株
        #   would_survive  下面不是土就放弃 —— 于是不会长在石头上、也不会浮空
        _write(os.path.join(DATA, "worldgen", "placed_feature",
                            "%s.json" % wbid), {
            "feature": "%s:%s" % (NS, wbid),
            "placement": [
                {"type": "minecraft:rarity_filter", "chance": chance},
                {"type": "minecraft:in_square"},
                {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"},
                {"type": "minecraft:count", "count": tries},
                {"type": "minecraft:random_offset",
                 "xz_spread": {"type": "minecraft:trapezoid",
                               "max": 4, "min": -4, "plateau": 0},
                 "y_spread": {"type": "minecraft:trapezoid",
                              "max": 1, "min": -1, "plateau": 0}},
                {"type": "minecraft:block_predicate_filter",
                 "predicate": {"type": "minecraft:would_survive", "state": state}},
            ],
        })

        # ---- 3. 加到哪些群系 ----
        _write(os.path.join(DATA, "neoforge", "biome_modifier",
                            "%s.json" % wbid), {
            "type": "neoforge:add_features",
            "biomes": biome_tag,
            "features": "%s:%s" % (NS, wbid),
            "step": "vegetal_decoration",
        })
        n += 1
    print("wild crop features: %d（configured + placed + biome_modifier 各一份）" % n)


# ======================================================================
# Java
# ======================================================================

JAVA_HEAD = '''package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.ModCropBlock;
import com.ctf.chinese_traditional_food.common.block.WildCropBlock;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 作物植株与种子的注册表。
 *
 * <p><b>本文件由 {@code tools/gen_crops.py} 生成，请不要手改。</b>
 * 要加作物请编辑 {@code tools/content_data.py} 的 {@code CROPS} 表。</p>
 *
 * <h2>每样作物三条东西</h2>
 * <ol>
 *   <li><b>植株</b> {@link ModCropBlock} —— 种在耕地上，八个生长阶段；</li>
 *   <li><b>种子</b> —— 就是植株方块的 {@link BlockItem}，右键耕地即种下；</li>
 *   <li><b>野生植株</b> {@link WildCropBlock} —— 野外自然生成，打掉就得种子。</li>
 * </ol>
 *
 * <p>所以"种子"在代码里只有一份，不存在"物品种子"和"方块种子"两套要对齐的问题。</p>
 *
 * <h2>为什么没有 {@code IEventBus} 之外的依赖</h2>
 * 植株的行为全在原版 {@code CropBlock} 里（就地生长、骨粉催熟、光不够不长），
 * 掉落全在战利品表里。这个类因此只是一张"名字 -> 方块"的清单。
 */
public final class ModCrops {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    /**
     * 种在地里的作物：没有碰撞箱、踩一下就掉、会随机生长。
     *
     * <p>注意第三个参数是 {@code UnaryOperator<Properties>}（拿到属性再加料），
     * 不是现成的 {@code Properties} —— 注册表要先挂上 id 再交给构造器，
     * 所以只能连线传。写成 {@code ModCrops.cropProps()} 会编译不过。</p>
     */
    private static BlockBehaviour.Properties cropProps(BlockBehaviour.Properties props) {
        return props.noCollision()
                .randomTicks()
                .instabreak()
                .sound(SoundType.CROP)
                .pushReaction(PushReaction.DESTROY);
    }

    /** 野生的：同样没有碰撞箱，但**不**随机生长（它一长出来就是熟的）。 */
    private static BlockBehaviour.Properties wildProps(BlockBehaviour.Properties props) {
        return props.noCollision()
                .instabreak()
                .sound(SoundType.CROP)
                .pushReaction(PushReaction.DESTROY);
    }

    /** 全部种子物品（创造标签页用）。 */
    public static List<DeferredItem<? extends Item>> allSeeds() {
        return SEEDS;
    }

    /**
     * 全部<b>种在地里</b>的植株（创造标签页用）。
     *
     * <p>野生植株<b>不在</b>这里：它们没有对应的物品（拿不到手里），
     * 而创造页要的是物品栈，所以放进创造页只会是一个空。
     * 想摆出来看就去野外找，或者用 {@code /setblock}。</p>
     */
    public static List<DeferredBlock<?>> allPlants() {
        return PLANTS;
    }

    /** 全部植株方块，含野生（调试与校验用）。 */
    public static List<DeferredBlock<?>> allCrops() {
        return CROPS;
    }

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }

    private ModCrops() {}
'''


def build_java():
    out = [JAVA_HEAD]
    out.append("\n    // ==================================================================\n")
    out.append("    // 植株与种子（按株型分组，方便对照贴图）\n")
    out.append("    // ==================================================================\n")

    by_habit = {}
    for row in DATA_SRC.CROPS:
        by_habit.setdefault(row[5], []).append(row)

    habit_titles = {
        "grass": "禾本：一根主茎挑着穗子",
        "legume": "豆科：矮丛上挂着豆荚",
        "seedpod": "籽用：细茎顶着小蒴果",
        "root": "块根块茎：贴地叶 + 露头的根",
        "leafy": "叶菜：一层层向外摊开",
        "bush": "茄果：小灌木垂着果实",
        "vine": "藤本：蔓生的藤与大叶",
        "fungus": "菌：簸开的耳片",
    }
    for habit in ("grass", "legume", "seedpod", "root", "leafy", "bush", "vine", "fungus"):
        rows = by_habit.get(habit, [])
        if not rows:
            continue
        out.append("\n    // ---- %s ----\n\n" % habit_titles.get(habit, habit))
        for (crop_id, zh, en, seed, prod, _h) in rows:
            out.append("    /** %s（%s）：种子「%s」，收成「%s」。 */\n" % (zh, en, zh, prod))
            out.append('    public static final DeferredBlock<ModCropBlock> %s =\n'
                       % _const(crop_block(crop_id)))
            out.append('            BLOCKS.registerBlock("%s", ModCropBlock::new, ModCrops::cropProps);\n'
                       % crop_block(crop_id))
            out.append('    public static final DeferredItem<BlockItem> %s =\n'
                       % _const(seed))
            # **物品 id 要显式指定成种子 id**。若用 registerSimpleBlockItem(block)
            # 这一个重载，物品 id 会跟着方块走，变成 "rice_crop" ——
            # 于是所有配方、标签、掉落里写的 "rice_seeds" 全部指向一个不存在的物品
            # （进游戏会报 Unknown registry key，踩过一次）。
            out.append('            ITEMS.registerSimpleBlockItem("%s", %s);\n\n'
                       % (seed, _const(crop_block(crop_id))))
        out.append("\n")

    out.append("    // ---- 野生植株：野外自然生成，打掉直接给种子 ----\n\n")
    wild = {row[0] for row in DATA_SRC.WILD_CROPS}
    for (crop_id, zh, en, _seed, _prod, _h) in DATA_SRC.CROPS:
        if crop_id not in wild:
            continue
        out.append("    /** 野生的%s（%s）。 */\n" % (zh, en))
        out.append('    public static final DeferredBlock<WildCropBlock> %s =\n'
                   % _const(wild_block(crop_id)))
        out.append('            BLOCKS.registerBlock("%s", WildCropBlock::new, ModCrops::wildProps);\n'
                   % wild_block(crop_id))
    out.append("\n")

    # ---- 汇总 ----
    out.append("    /** 全部种子（创造标签页用）。 */\n")
    out.append("    private static final List<DeferredItem<? extends Item>> SEEDS = List.of(\n")
    entries = ["            %s" % _const(row[3]) for row in DATA_SRC.CROPS]
    for chunk in range(0, len(entries), 4):
        tail = ",\n" if chunk + 4 < len(entries) else "\n"
        out.append(",\n".join(entries[chunk:chunk + 4]) + tail)
    out.append("    );\n\n")

    out.append("    /** 全部植株（含野生）。 */\n")
    out.append("    private static final List<DeferredBlock<?>> CROPS = List.of(\n")
    entries = []
    for row in DATA_SRC.CROPS:
        entries.append("            %s" % _const(crop_block(row[0])))
        if row[0] in wild:
            entries.append("            %s" % _const(wild_block(row[0])))
    for chunk in range(0, len(entries), 4):
        tail = ",\n" if chunk + 4 < len(entries) else "\n"
        out.append(",\n".join(entries[chunk:chunk + 4]) + tail)
    out.append("    );\n\n")

    out.append("    /** 只有种在地里的那些（有物品、能进创造页）。 */\n")
    out.append("    private static final List<DeferredBlock<?>> PLANTS = List.of(\n")
    entries = ["            %s" % _const(crop_block(row[0])) for row in DATA_SRC.CROPS]
    for chunk in range(0, len(entries), 4):
        tail = ",\n" if chunk + 4 < len(entries) else "\n"
        out.append(",\n".join(entries[chunk:chunk + 4]) + tail)
    out.append("    );\n")

    out.append("}\n")
    _write(os.path.join(JAVA, "registry", "ModCrops.java"), "".join(out))
    print("ModCrops.java: %d 种作物 + %d 个野生" % (len(DATA_SRC.CROPS), len(wild)))


# ======================================================================
# 校验：数据表自洽
# ======================================================================

def self_check(item_ids):
    """尽早发现写错的 id —— 比等编译报错便宜。"""
    problems = []
    ids = set()
    for row in DATA_SRC.CROPS:
        if len(row) != 6:
            problems.append("CROPS 有长度不是 6 的行: %r" % (row,))
            continue
        crop_id, _zh, _en, seed, prod, habit = row
        if crop_id in ids:
            problems.append("作物 id 重复: %s" % crop_id)
        ids.add(crop_id)
        if seed not in item_ids:
            problems.append("作物 %s 的种子 %s 不在物品表里" % (crop_id, seed))
        if prod not in item_ids:
            problems.append("作物 %s 的产物 %s 不在物品表里" % (crop_id, prod))
        if habit not in ("grass", "legume", "seedpod", "root",
                         "leafy", "bush", "vine", "fungus"):
            problems.append("作物 %s 的株型 %s 没有画法" % (crop_id, habit))

    # 种子必须一一对应：一粒种子只能种出一种作物
    seed_owner = {}
    for row in DATA_SRC.CROPS:
        seed = row[3]
        if seed in seed_owner:
            problems.append("种子 %s 被 %s 和 %s 共用"
                            % (seed, seed_owner[seed], row[0]))
        seed_owner[seed] = row[0]

    for (crop_id, chance, tries) in DATA_SRC.WILD_CROPS:
        if crop_id not in ids:
            problems.append("WILD_CROPS 里的 %s 不是已定义的作物" % crop_id)
        if chance < 1 or tries < 1:
            problems.append("野生作物 %s 的概率/株数必须 ≥ 1" % crop_id)
    for crop_id, habitat in DATA_SRC.WILD_HABITAT.items():
        if crop_id not in ids:
            problems.append("WILD_HABITAT 里的 %s 不是已定义的作物" % crop_id)
        if habitat not in DATA_SRC.WILD_BIOMES:
            problems.append("野生作物 %s 的生态类型 %s 没有对应群系"
                            % (crop_id, habitat))
    return problems


def main():
    item_ids = set()
    for row in (DATA_SRC.INGREDIENTS + DATA_SRC.SEEDS + DATA_SRC.SEASONINGS
                + DATA_SRC.FRUITS + DATA_SRC.VEGETABLES):
        item_ids.add(row[0])
    for row in DATA_SRC.TOOLS:
        item_ids.add(row[0])

    problems = self_check(item_ids)
    if problems:
        print("作物表有 %d 个问题：" % len(problems))
        for p in problems:
            print("  - " + p)
        raise SystemExit(1)

    build_models()
    build_loot()
    build_worldgen()
    build_java()


if __name__ == "__main__":
    main()
