# -*- coding: utf-8 -*-
"""果树：树苗 → 果树 → 树叶掉果子。

    python tools/gen_trees.py

产出
----
* Java：{@code registry/ModTrees.java}（13 种树苗 + 13 种树叶 + 1 种共用原木）
* 资源：blockstates / models / items / loot_table

三件事
------

**一、原木共用一种。**
现实里梨木桃木确实不同，但在方块游戏里"13 种几乎一样的木头"只是
徒增合成表与背包压力。所以树干统一用"果木原木"，辨认靠树苗与树叶。

**二、树叶必须一种果子一套。**
掉落表挂在方块身上：

    梨树叶 → 10% 梨树苗 + 10% 梨
    桃树叶 → 10% 桃树苗 + 10% 桃

如果共用一种树叶，就没法知道该掉哪种果子（除非再引入方块实体或方块状态，
那重得多）。所以这里多出 13 个方块是**必要的**，不是冗余。

**三、掉落概率写在 content_data 里。**
{@code TREE_LEAF_DROP_CHANCE} 默认 0.10。改那个数，重跑本脚本，
战利品表就跟着变 —— 不用改 Java。
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


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            fh.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def _const(name):
    return name.upper()


# 方块 id

def sapling(fruit):
    return "%s_sapling" % fruit


def trunk(fruit):
    """这棵树的树干方块 id —— 由 `gen_woods.py` 生成。

    早先 13 种树共用一个 `fruit_log`，现在每种树一棵。
    树苗长成树时引用的是这个 id（见 `FruitSaplingBlock`）。
    """
    return "%s_log" % fruit


def leaves(fruit):
    return "%s_leaves" % fruit


def leaves_item(fruit):
    """树叶**物品图标**用的贴图名（不是方块贴图）。

    方块上的树叶是半透明 + 带洞的；同一个像素拿去当物品图标，物品栏里
    就是一块又镂空又发虚的绿。所以物品另走一张实心图标。
    """
    return "%s_leaves_item" % fruit


def texture(name):
    return name


def item_model(item_id, model):
    """写 `assets/<ns>/items/<item_id>.json` —— 26.1 起**物品图标必须显式声明**。

    漏了这一步，客户端只会在日志里写一行
    `Missing item model for location chinese_traditional_food:xxx`，
    游戏里物品直接变成没有贴图的方块，**不会崩、不会报红字**，
    所以很容易漏过去。这一版就是因为搜日志只搜了 "Missing model"
    而漏掉了 "Missing item model" 才一直没发现。
    """
    _write(os.path.join(ASSETS, "items", "%s.json" % item_id), {
        "model": {"type": "minecraft:model",
                  "model": "%s:%s" % (NS, model)},
    })


# ======================================================================
# 模型与方块状态
# ======================================================================

def build_models():
    """树苗与树叶的模型。

    原木/木头/去皮/木板/楼梯/… 全部由 `gen_woods.py` 负责，这里不碰 ——
    之前这里写过一套共用原木的模型，现在删掉了，否则会留下没人用的
    孤儿贴图（`validate_content.py` 会报）。
    """
    n = 0
    for (fruit, _size) in DATA_SRC.TREE_FRUITS:
        # ---- 树苗：一个"十字"模型（和原版树苗一样的两片交叉贴图） ----
        _write(os.path.join(ASSETS, "models", "block", "%s.json" % sapling(fruit)),
               {"parent": "minecraft:block/cross",
                "textures": {"cross": "%s:block/%s" % (NS, sapling(fruit))}})
        _write(os.path.join(ASSETS, "blockstates", "%s.json" % sapling(fruit)),
               {"variants": {"stage=0": {"model": "%s:block/%s" % (NS, sapling(fruit))},
                             "stage=1": {"model": "%s:block/%s" % (NS, sapling(fruit))}}})
        # 树苗物品：和原版一样直接引用方块里的 cross 模型
        item_model(sapling(fruit), "block/%s" % sapling(fruit))

        # ---- 树叶：cube_all（六面同一张，半透明 + 镂空） ----
        _write(os.path.join(ASSETS, "models", "block", "%s.json" % leaves(fruit)),
               {"parent": "minecraft:block/leaves",
                "textures": {"all": "%s:block/%s" % (NS, leaves(fruit))}})
        _write(os.path.join(ASSETS, "blockstates", "%s.json" % leaves(fruit)),
               {"variants": {"": {"model": "%s:block/%s" % (NS, leaves(fruit))}}})

        # ---- 树叶的物品：**另用一张实心 2D 图标**（26.1 起物品模型写在 items/） ----
        _write(os.path.join(ASSETS, "items", "%s.json" % leaves(fruit)), {
            "model": {"type": "minecraft:model",
                      "model": "%s:item/%s" % (NS, leaves_item(fruit))},
        })
        _write(os.path.join(ASSETS, "models", "item", "%s.json" % leaves_item(fruit)), {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": "%s:item/%s" % (NS, leaves_item(fruit))},
        })
        n += 1
    print("tree models/blockstates: %d 种果树（树苗 + 树叶）" % n)


# ======================================================================
# 掉落
# ======================================================================

def build_loot():
    chance = DATA_SRC.TREE_LEAF_DROP_CHANCE
    n = 0

    for (fruit, _size) in DATA_SRC.TREE_FRUITS:
        bid = leaves(fruit)
        pools = [
            {
                # 木棍：原版树叶都有这一池
                "rolls": 1, "bonus_rolls": 0,
                "entries": [{
                    "type": "minecraft:item", "name": "minecraft:stick",
                    "functions": [
                        {"function": "minecraft:set_count",
                         "count": {"type": "minecraft:uniform",
                                   "min": 0.0,
                                   "max": float(DATA_SRC.TREE_LEAF_STICK_MAX)}},
                        {"function": "minecraft:apply_bonus",
                         "enchantment": "minecraft:fortune",
                         "formula": "minecraft:uniform_bonus_count",
                         "parameters": {"bonusMultiplier": 1}},
                    ],
                }],
                "conditions": [{"condition": "minecraft:inverted",
                                "term": {"condition": "minecraft:table_bonus",
                                         "enchantment": "minecraft:fortune",
                                         "chances": [0.0]}}],
            },
            {
                # 树苗：默认 10%
                "rolls": 1, "bonus_rolls": 0,
                "entries": [{"type": "minecraft:item",
                             "name": "%s:%s" % (NS, sapling(fruit))}],
                "conditions": [{"condition": "minecraft:random_chance",
                                "chance": chance}],
            },
            {
                # 果子：默认 10%
                "rolls": 1, "bonus_rolls": 0,
                "entries": [{"type": "minecraft:item",
                             "name": "%s:%s" % (NS, fruit)}],
                "conditions": [{"condition": "minecraft:random_chance",
                                "chance": chance}],
            },
        ]
        _write(os.path.join(DATA, "loot_table", "blocks", "%s.json" % bid), {
            "type": "minecraft:block",
            "random_sequence": "%s:blocks/%s" % (NS, bid),
            "pools": pools,
        })
        n += 1
    print("tree loot tables: %d 种树叶（树苗/果实各 %.0f%%）"
          % (n, chance * 100))


# ======================================================================
# Java
# ======================================================================

JAVA_HEAD = '''package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.FruitLeavesBlock;
import com.ctf.chinese_traditional_food.common.block.FruitSaplingBlock;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 果树：树苗 + 树叶。
 *
 * <p><b>本文件由 {@code tools/gen_trees.py} 生成，请不要手改。</b>
 * 要加果树请编辑 {@code tools/content_data.py} 的 {@code TREE_FRUITS} 表。</p>
 *
 * <h2>两种方块各管一件事</h2>
 * <ol>
 *   <li><b>树苗</b> {@link FruitSaplingBlock} —— 种下去，过一阵长成树；</li>
 *   <li><b>树叶</b> {@link FruitLeavesBlock} —— 掉落表挂在它身上，
 *       10% 掉自己的树苗、10% 掉自己的果子。</li>
 * </ol>
 *
 * <p>树干不在这里 —— 13 种树各有自己的原木/木板/楼梯/…，
 * 由 {@link ModWoods} 生成。早先这里有一个共用的 {@code fruit_log}，
 * 现在已废掉。</p>
 */
public final class ModTrees {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    private static BlockBehaviour.Properties leafProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.PLANT)
                .strength(0.2F)
                .randomTicks()
                .sound(SoundType.GRASS)
                .noOcclusion()
                .isValidSpawn((state, level, pos, type) -> false)
                .isSuffocating((state, level, pos) -> false)
                .isViewBlocking((state, level, pos) -> false)
                .ignitedByLava()
                .pushReaction(PushReaction.DESTROY);
    }

    private static BlockBehaviour.Properties saplingProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.PLANT)
                .noCollision()
                .randomTicks()
                .instabreak()
                .sound(SoundType.GRASS)
                .pushReaction(PushReaction.DESTROY);
    }
'''


def build_java():
    out = [JAVA_HEAD]

    # ---- 树叶与树苗（先注册树叶：树苗要引用它） ----
    out.append("\n    // ==================================================================\n")
    out.append("    // 树叶（掉落表挂在它们身上）\n")
    out.append("    // ==================================================================\n\n")
    for (fruit, _size) in DATA_SRC.TREE_FRUITS:
        out.append("    /** %s树叶：10%% 掉树苗、10%% 掉果子。 */\n" % fruit)
        out.append("    public static final DeferredBlock<FruitLeavesBlock> %s =\n"
                   % _const(leaves(fruit)))
        out.append('            BLOCKS.registerBlock("%s", FruitLeavesBlock::new, ModTrees::leafProps);\n'
                   % leaves(fruit))
        # 树叶**必须有方块物品**：创造页的 accept 收的是 ItemLike，
        # 而 Block.asItem() 在没有 BlockItem 时会返回空气 ——
        # 那样创造页里会多出一堆"空槽"，而且玩家没法拿它去摆。
        # 原版的橡树叶也都是有物品的（剪刀剪下来 / 精准采集得到）。
        out.append("    public static final DeferredItem<BlockItem> %s_ITEM =\n"
                   % _const(leaves(fruit)))
        out.append('            ITEMS.registerSimpleBlockItem("%s", %s);\n\n'
                   % (leaves(fruit), _const(leaves(fruit))))

    out.append("\n    // ==================================================================\n")
    out.append("    // 树苗（引用上面那一片树叶，长大时用它的方块）\n")
    out.append("    // ==================================================================\n\n")
    for (fruit, size) in DATA_SRC.TREE_FRUITS:
        out.append("    /** %s树苗（树形 %d）。 */\n" % (fruit, size))
        out.append("    public static final DeferredBlock<FruitSaplingBlock> %s =\n"
                   % _const(sapling(fruit)))
        out.append('            BLOCKS.registerBlock("%s",\n'
                   % sapling(fruit))
        # 只传"树形 + 果子名"两个常量：长树时由方块自己去注册表里
        # 取 <fruit>_log 与 <fruit>_leaves（见 FruitSaplingBlock 的类注释，
        # 那里解释了为什么不能存 DeferredBlock —— codec 要能把方块从 JSON 还原）
        out.append('                    props -> new FruitSaplingBlock(%d, "%s", props),\n'
                   % (size, fruit))
        out.append("                    ModTrees::saplingProps);\n")
        out.append('    public static final DeferredItem<BlockItem> %s_ITEM =\n'
                   % _const(sapling(fruit)))
        out.append('            ITEMS.registerSimpleBlockItem("%s", %s);\n\n'
                   % (sapling(fruit), _const(sapling(fruit))))

    # ---- 树苗的物品 ----
    out.append("\n    /** 全部树苗物品（创造标签页用）。 */\n")
    out.append("    public static List<DeferredItem<? extends Item>> allSaplings() {\n")
    out.append("        return SAPLINGS;\n")
    out.append("    }\n\n")
    out.append("    private static final List<DeferredItem<? extends Item>> SAPLINGS = List.of(\n")
    entries = ["            %s_ITEM" % _const(sapling(f)) for (f, _s) in DATA_SRC.TREE_FRUITS]
    for chunk in range(0, len(entries), 4):
        tail = ",\n" if chunk + 4 < len(entries) else "\n"
        out.append(",\n".join(entries[chunk:chunk + 4]) + tail)
    out.append("    );\n\n")

    out.append("    /** 全部树叶物品（创造标签页用）。 */\n")
    out.append("    public static List<DeferredItem<? extends Item>> allLeaves() {\n")
    out.append("        return LEAVES;\n")
    out.append("    }\n\n")
    out.append("    private static final List<DeferredItem<? extends Item>> LEAVES = List.of(\n")
    entries = ["            %s_ITEM" % _const(leaves(f)) for (f, _s) in DATA_SRC.TREE_FRUITS]
    for chunk in range(0, len(entries), 4):
        tail = ",\n" if chunk + 4 < len(entries) else "\n"
        out.append(",\n".join(entries[chunk:chunk + 4]) + tail)
    out.append("    );\n\n")

    out.append("""    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }

    private ModTrees() {}
}
""")
    _write(os.path.join(JAVA, "registry", "ModTrees.java"), "".join(out))
    print("ModTrees.java: %d 种果树" % len(DATA_SRC.TREE_FRUITS))


# ======================================================================
# 自检
# ======================================================================

def self_check(item_ids):
    problems = []
    seen = set()
    for row in DATA_SRC.TREE_FRUITS:
        if len(row) != 2:
            problems.append("TREE_FRUITS 有长度不是 2 的行: %r" % (row,))
            continue
        fruit, size = row
        if fruit in seen:
            problems.append("果树重复: %s" % fruit)
        seen.add(fruit)
        if fruit not in item_ids:
            problems.append("果树 %s 对应的水果不在物品表里" % fruit)
        if size not in (0, 1, 2):
            problems.append("果树 %s 的树形 %r 不是 0/1/2" % (fruit, size))
    ch = DATA_SRC.TREE_LEAF_DROP_CHANCE
    if not 0.0 < ch <= 1.0:
        problems.append("TREE_LEAF_DROP_CHANCE 必须在 (0, 1] 之间，现在是 %r" % ch)
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
        print("果树表有 %d 个问题：" % len(problems))
        for p in problems:
            print("  - " + p)
        raise SystemExit(1)

    cleanup_legacy()
    build_models()
    build_loot()
    build_java()


def cleanup_legacy():
    """删掉"共用原木"时代的残留文件。

    早先 13 种树共用一个 `fruit_log`（方块 + 模型 + 贴图 + 掉落表）。
    现在每种树一棵，那个 id 已经不存在了 —— 但如果文件留在资源目录里，
    会变成一堆指向已删方块的孤儿：

    * `items/fruit_log.json` 指向一个不存在的方块模型；
    * `textures/block/fruit_log*.png` 没有任何模型引用 →
      `validate_content.py` 的孤儿贴图检查会直接报错。

    生成器只写不删的话这类残留永远清不掉，所以这里显式删一遍。
    """
    stale = [
        os.path.join(ASSETS, "models", "block", "fruit_log.json"),
        os.path.join(ASSETS, "models", "block", "fruit_log_horizontal.json"),
        os.path.join(ASSETS, "blockstates", "fruit_log.json"),
        os.path.join(ASSETS, "items", "fruit_log.json"),
        os.path.join(ASSETS, "textures", "block", "fruit_log.png"),
        os.path.join(ASSETS, "textures", "block", "fruit_log_top.png"),
        os.path.join(DATA, "loot_table", "blocks", "fruit_log.json"),
    ]
    removed = 0
    for path in stale:
        if os.path.isfile(path):
            os.remove(path)
            removed += 1
    if removed:
        print("tree legacy cleanup: 删掉 %d 个共用原木时代的残留文件" % removed)
    return removed


if __name__ == "__main__":
    main()
