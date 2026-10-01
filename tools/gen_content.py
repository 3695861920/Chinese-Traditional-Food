# -*- coding: utf-8 -*-
"""
由 tools/content_data.py 生成模组内容。

    python tools/gen_content.py

生成物（全部会被覆盖，不要手改，改 content_data.py）：
    src/main/java/.../registry/ModItems.java          物品注册表
    src/main/java/.../registry/ModCreativeTabs.java   创造标签页
    src/main/resources/assets/.../lang/zh_cn.json     中文语言文件
    src/main/resources/assets/.../lang/en_us.json     英文语言文件
    src/main/resources/assets/.../items/<id>.json     客户端物品
    src/main/resources/assets/.../models/item/<id>.json  物品模型
    src/main/resources/data/.../recipe/<id>.json      配方
    src/main/resources/data/.../tags/item/*.json      本模组标签
    src/main/resources/data/c/tags/item/*.json        c 命名空间通用标签
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_data as DATA  # noqa: E402
import gen_crops  # noqa: E402  （作物植株：ModCrops.java / 模型 / 掉落 / 世界生成）
import gen_trees  # noqa: E402  （果树：ModTrees.java / 模型 / 掉落）
import gen_woods  # noqa: E402  （13 套木制品：ModWoods.java / 117 个方块）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf", "chinese_traditional_food")
RES = os.path.join(ROOT, "src", "main", "resources")
NAMESPACE = "chinese_traditional_food"

ZERO = object()   # 表示"这个物品不做成常量条目"（用于递归处理时占位）


def const_name(item_id):
    return item_id.upper()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote " + os.path.relpath(path, ROOT))


def drop_if_exists(path):
    """删掉被取代的旧生成文件（重命名时要记得改这里）。"""
    if os.path.exists(path):
        os.remove(path)
        print("removed stale " + os.path.relpath(path, ROOT))


def write_json(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# ======================================================================
# 汇总所有物品
# ======================================================================

def collect():
    """返回 (items, dishes)。items 里每项是 dict。"""
    items = []

    def add(row, category):
        item_id, zh, en, kind, palette, nutrition, saturation = row[:7]
        items.append(dict(id=item_id, zh=zh, en=en, kind=kind, palette=palette,
                          nutrition=nutrition, saturation=saturation,
                          effects="NONE", category=category,
                          durability=0, group=None))

    for row in DATA.INGREDIENTS:
        add(row, "ingredient")
    for row in DATA.SEEDS:
        add(row, "seed")
    for row in DATA.SEASONINGS:
        add(row, "seasoning")
    for row in DATA.FRUITS:
        add(row, "fruit")
    for row in DATA.VEGETABLES:
        add(row, "vegetable")
    for row in DATA.TOOLS:
        item_id, zh, en, kind, palette, durability = row
        items.append(dict(id=item_id, zh=zh, en=en, kind=kind, palette=palette,
                          nutrition=0, saturation=0, effects="NONE",
                          category="tool", durability=durability, group=None))

    dishes = []
    for row in DATA.DISHES:
        item_id, zh, en, group, kind, palette, nutrition, saturation, effects = row
        dishes.append(dict(id=item_id, zh=zh, en=en, kind=kind, palette=palette,
                           nutrition=nutrition, saturation=saturation,
                           effects=effects, category="dish", durability=0, group=group))

    return items, dishes


CATEGORY_TITLE = {
    "ingredient": "基础食材",
    "seed": "作物种子",
    "seasoning": "调味料",
    "fruit": "常见水果",
    "vegetable": "常见蔬菜",
    "tool": "厨具与餐具",
    "dish": "菜品",
}


# ======================================================================
# ModItems.java
# ======================================================================

HEADER = """package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.food.DishEffects;
import com.ctf.chinese_traditional_food.common.item.DishItem;
import java.util.List;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 物品注册表。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b>
 * 要加物品 / 改配方，请编辑 {@code tools/content_data.py} 后重新生成。</p>
 *
 * <p>内容规模：基础食材、调味料、水果、蔬菜、厨具餐具，以及
 * 八大菜系与九大传统节日的菜品，全部实现为可摆放的 {@link DishItem}。</p>
 */
@SuppressWarnings("unused")
public final class ModItems {
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    // ==================================================================
    // 摆放方块对应的方块物品（手写部分，见 ModBlocks）
    // ==================================================================

    /** 餐盘，摆放 1 份菜。 */
    public static final DeferredItem<BlockItem> PLATE = ITEMS.registerSimpleBlockItem(ModBlocks.PLATE);

    /** 案板，放上食材后用刀切。 */
    public static final DeferredItem<BlockItem> CUTTING_BOARD =
            ITEMS.registerSimpleBlockItem(ModBlocks.CUTTING_BOARD);

    /** 电动脱壳机，吃电给谷物脱壳。 */
    public static final DeferredItem<BlockItem> ELECTRIC_SHELLER =
            ITEMS.registerSimpleBlockItem(ModBlocks.ELECTRIC_SHELLER);

    /** 电动磨粉机，吃电把谷物磨成粉。 */
    public static final DeferredItem<BlockItem> ELECTRIC_MILL =
            ITEMS.registerSimpleBlockItem(ModBlocks.ELECTRIC_MILL);

    /** 熔炉发电机，烧燃料发电。 */
    public static final DeferredItem<BlockItem> FURNACE_GENERATOR =
            ITEMS.registerSimpleBlockItem(ModBlocks.FURNACE_GENERATOR);

    // ---- 大型机（"3×3 放大版"）--------------------------------------
    // 仍是单方块，但造型铺满整格、没有腿部留空；数值上批次 ×4、
    // 速度快 3.3 倍、单位耗电约三成。详见 MachineEnergy 的"大型机"一节。

    /** 大型熔炉发电机，200 FE/t、缓冲 40000 FE。 */
    public static final DeferredItem<BlockItem> LARGE_FURNACE_GENERATOR =
            ITEMS.registerSimpleBlockItem(ModBlocks.LARGE_FURNACE_GENERATOR);

    /** 大型电动磨粉机，32 个一批 / 3 秒一批。 */
    public static final DeferredItem<BlockItem> LARGE_ELECTRIC_MILL =
            ITEMS.registerSimpleBlockItem(ModBlocks.LARGE_ELECTRIC_MILL);

    /** 大型电动脱壳机，32 个一批 / 3 秒一批。 */
    public static final DeferredItem<BlockItem> LARGE_ELECTRIC_SHELLER =
            ITEMS.registerSimpleBlockItem(ModBlocks.LARGE_ELECTRIC_SHELLER);

    // ---- 灶火系统：炉灶 + 三件锅具 --------------------------------------
    // 和电力系统并行的一条路线：炉灶烧燃料只供热，锅具坐在它正上方用热。

    /** 炉灶，烧燃料给正上方一格的锅具供热。 */
    public static final DeferredItem<BlockItem> STOVE =
            ITEMS.registerSimpleBlockItem(ModBlocks.STOVE);

    /** 炒锅，坐在炉灶上快炒。 */
    public static final DeferredItem<BlockItem> WOK =
            ITEMS.registerSimpleBlockItem(ModBlocks.WOK);

    /** 蒸笼，坐在炉灶上蒸。 */
    public static final DeferredItem<BlockItem> STEAMER =
            ITEMS.registerSimpleBlockItem(ModBlocks.STEAMER);

    /** 汤锅，坐在炉灶上吊汤。 */
    public static final DeferredItem<BlockItem> SOUP_POT =
            ITEMS.registerSimpleBlockItem(ModBlocks.SOUP_POT);
"""

FOOTER = """
    public static void register(IEventBus modBus) {
        ITEMS.register(modBus);
    }

    /** 生成器写出的所有餐食类物品（菜品 + 可直接摆盘的食材），供创造标签页使用。 */
    public static List<DeferredItem<? extends Item>> allFoods() {
        return ALL_FOODS;
    }

    private ModItems() {}
}
"""


def food_props(item):
    """生成 FoodProperties 表达式。"""
    parts = ["new FoodProperties.Builder()"]
    parts.append(".nutrition(%d)" % item["nutrition"])
    parts.append(".saturationModifier(%.2fF)" % item["saturation"])
    if item["nutrition"] <= 0:
        # 纯饮品（如菊花酒）：不顶饱，但随时能喝
        parts.append(".alwaysEdible()")
    return "\n                        ".join(parts) + "\n                        .build()"


def item_entry(item, indent="    "):
    """生成一条物品注册代码。"""
    name = const_name(item["id"])
    has_effects = item["effects"] != "NONE"
    is_food = item["nutrition"] > 0 or has_effects

    lines = []
    if item["durability"] > 0:
        # 工具：带耐久
        lines.append('%s/** %s（%s），耐久 %d。 */' % (indent, item["zh"], item["en"], item["durability"]))
        lines.append('%spublic static final DeferredItem<Item> %s = ITEMS.registerItem(' % (indent, name))
        lines.append('%s        "%s",' % (indent, item["id"]))
        lines.append('%s        Item::new,' % indent)
        lines.append('%s        props -> props.durability(%d));' % (indent, item["durability"]))
    elif is_food:
        lines.append('%s/** %s（%s）：%d 饥饿 / %.1f 饱和，效果 %s。 */'
                     % (indent, item["zh"], item["en"], item["nutrition"],
                        item["saturation"], item["effects"]))
        lines.append('%spublic static final DeferredItem<DishItem> %s = ITEMS.registerItem('
                     % (indent, name))
        lines.append('%s        "%s",' % (indent, item["id"]))
        lines.append('%s        props -> new DishItem(props, DishEffects.%s),'
                     % (indent, item["effects"]))
        lines.append('%s        props -> props.food(%s));' % (indent, food_props(item)))
    else:
        lines.append('%s/** %s（%s）。 */' % (indent, item["zh"], item["en"]))
        lines.append('%spublic static final DeferredItem<Item> %s = ITEMS.registerSimpleItem("%s");'
                     % (indent, name, item["id"]))
    return "\n".join(lines)


def gen_mod_items(items, dishes):
    out = [HEADER]

    # --- 按类别分组 ---
    sections = [
        ("基础食材", [i for i in items if i["category"] == "ingredient"]),
        # 作物种子不在这里 —— 它们是 ModCrops 里的方块物品（种下去会变成植株），
        # 见 tools/gen_crops.py。
        ("调味料", [i for i in items if i["category"] == "seasoning"]),
        ("常见水果", [i for i in items if i["category"] == "fruit"]),
        ("常见蔬菜", [i for i in items if i["category"] == "vegetable"]),
        ("厨具与餐具", [i for i in items if i["category"] == "tool"]),
    ]
    for title, rows in sections:
        if not rows:
            continue
        out.append("\n    // ==================================================================\n")
        out.append("    // %s\n" % title)
        out.append("    // ==================================================================\n\n")
        out.append("\n\n".join(item_entry(i) for i in rows))
        out.append("\n")

    # --- 八大菜系 + 节日 ---
    for group in DATA.GROUP_ORDER:
        rows = [d for d in dishes if d["group"] == group]
        if not rows:
            continue
        cuisine = group in ("lu", "chuan", "yue", "su", "min", "zhe", "xiang", "hui")
        kind_note = " —— 八大菜系" if cuisine else (
            " —— 早餐" if group == "breakfast" else (
                " —— 特色小吃" if group == "snack" else " —— 传统节日"))
        out.append("\n    // ==================================================================\n")
        out.append("    // %s%s（%d 道）\n"
                   % (DATA.GROUP_TITLES[group], kind_note, len(rows)))
        out.append("    // ==================================================================\n\n")
        out.append("\n\n".join(item_entry(d) for d in rows))
        out.append("\n")

    # --- 汇总列表（供创造标签页） ---
    out.append("\n    // ==================================================================\n")
    out.append("    // 汇总：所有可食用 / 可摆盘的物品\n")
    out.append("    // ==================================================================\n\n")
    out.append("    private static final List<DeferredItem<? extends Item>> ALL_FOODS = List.of(\n")
    entries = []
    for i in items + dishes:
        if i["nutrition"] > 0 or i["effects"] != "NONE":
            entries.append("            %s" % const_name(i["id"]))
    for chunk in range(0, len(entries), 4):
        out.append(",\n".join(entries[chunk:chunk + 4]) + (",\n" if chunk + 4 < len(entries) else "\n"))
    out.append("    );\n")

    out.append(FOOTER)
    write(os.path.join(JAVA, "registry", "ModItems.java"), "".join(out))


# ======================================================================
# ModCreativeTabs.java
# ======================================================================

CREATIVE_HEADER = """package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 创造模式标签页。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b></p>
 */
public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ChineseTraditionalFood.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN =
            CREATIVE_MODE_TABS.register("main", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.chinese_traditional_food.main"))
                    .icon(() -> new ItemStack(ModItems.MAPO_TOFU.get()))
                    .displayItems((params, output) -> {
                        // 餐具与功能方块
                        output.accept(ModItems.PLATE.get());
                        output.accept(ModItems.CUTTING_BOARD.get());
                        output.accept(ModItems.FURNACE_GENERATOR.get());
                        output.accept(ModItems.ELECTRIC_MILL.get());
                        output.accept(ModItems.ELECTRIC_SHELLER.get());
                        output.accept(ModItems.LARGE_FURNACE_GENERATOR.get());
                        output.accept(ModItems.LARGE_ELECTRIC_MILL.get());
                        output.accept(ModItems.LARGE_ELECTRIC_SHELLER.get());
                        output.accept(ModItems.STOVE.get());
                        output.accept(ModItems.WOK.get());
                        output.accept(ModItems.STEAMER.get());
                        output.accept(ModItems.SOUP_POT.get());
                        // 食材压缩方块（生成出来的，走另一个注册表）
                        for (var item : ModCompressed.all()) {
                            output.accept(item.get());
                        }
                        // 其余全部内容（食材 / 调味料 / 水果 / 蔬菜 / 厨具 / 菜品）
                        for (var item : ModItems.allFoods()) {
                            output.accept(item.get());
                        }
                    })
                    .build());
"""

CREATIVE_FOOTER = """
    /** 追加到原版标签页（mod 事件总线，逻辑客户端）。 */
    public static void addToVanillaTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.FOOD_AND_DRINKS) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            // 压缩方块也是"食材"，放进原料页最合适
            for (var item : ModCompressed.all()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.NATURAL_BLOCKS) {
            // 植株也在"自然"页 —— 找种子的时候最直觉
            for (var block : ModCrops.allPlants()) {
                event.accept(block.get());
            }
            // 果树：树苗与树叶。
            // 两者**都必须**是方块物品（ModTrees 里已经给树叶也注册了物品）——
            // accept 收的是 ItemLike，而 Block.asItem() 在没有 BlockItem 时
            // 返回空气，会直接抛 "The stack count must be 1 for 0 minecraft:air"。
            for (var item : ModTrees.allSaplings()) {
                event.accept(item.get());
            }
            for (var item : ModTrees.allLeaves()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.BUILDING_BLOCKS) {
            // 13 套木制品：原木 / 木头 / 去皮 / 木板 / 楼梯 / 台阶 / 栅栏 / 栅栏门
            for (var item : ModWoods.allItems()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) {
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.FURNACE_GENERATOR.get());
            event.accept(ModItems.ELECTRIC_MILL.get());
            event.accept(ModItems.ELECTRIC_SHELLER.get());
            event.accept(ModItems.LARGE_FURNACE_GENERATOR.get());
            event.accept(ModItems.LARGE_ELECTRIC_MILL.get());
            event.accept(ModItems.LARGE_ELECTRIC_SHELLER.get());
            event.accept(ModItems.STOVE.get());
            event.accept(ModItems.WOK.get());
            event.accept(ModItems.STEAMER.get());
            event.accept(ModItems.SOUP_POT.get());
        }
        if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            // 种子是"原料"：每一样都能种下去，是整条食材线的起点
            for (var seed : ModCrops.allSeeds()) {
                event.accept(seed.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.FURNACE_GENERATOR.get());
            event.accept(ModItems.ELECTRIC_MILL.get());
            event.accept(ModItems.ELECTRIC_SHELLER.get());
            event.accept(ModItems.LARGE_FURNACE_GENERATOR.get());
            event.accept(ModItems.LARGE_ELECTRIC_MILL.get());
            event.accept(ModItems.LARGE_ELECTRIC_SHELLER.get());
            event.accept(ModItems.STOVE.get());
            event.accept(ModItems.WOK.get());
            event.accept(ModItems.STEAMER.get());
            event.accept(ModItems.SOUP_POT.get());
        }
    }

    public static void register(IEventBus modBus) {
        CREATIVE_MODE_TABS.register(modBus);
    }

    private ModCreativeTabs() {}
}
"""


def gen_creative_tabs():
    write(os.path.join(JAVA, "registry", "ModCreativeTabs.java"),
          CREATIVE_HEADER + CREATIVE_FOOTER)


# ======================================================================
# 案板切割表（ModCutting.java）
# ======================================================================

CUTTING_HEADER = '''package com.ctf.chinese_traditional_food.common.recipe;

import java.util.List;

/**
 * 本模组自研装置与工具的硬编码处理表。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b>
 * 要改配方请编辑 {@code tools/content_data.py}。</p>
 *
 * <p>为什么用代码表而不是自定义 {@code RecipeType}：
 * 一来这些装置被要求"配方独立于其它模组、始终可用"，代码表最直接；
 * 二来不受数据包加载顺序影响。将来若要支持数据包自定义，
 * 把下面的 List 换成读 JSON 即可，{@link ProcessRecipes} / {@link CuttingRecipes}
 * 这些调用方不用改。</p>
 */
public final class ModRecipes {
    /** 一条"进料 -> 出料"规则。
     *
     * @param input           输入（物品 id 或 {@code #命名空间:标签路径}）
     * @param output          产出物品 id
     * @param outputCount     产出数量
     * @param byproduct       副产物物品 id，空字符串表示没有
     * @param byproductChance 副产物概率（0~1）
     * @param ticks           耗时（tick）
     */
    public record Entry(String input, String output, int outputCount,
                        String byproduct, float byproductChance, int ticks) {}

    /**
     * 一条"锅谱"。**这是菜品唯一的做法。**
     *
     * <p>与 {@link Entry} 的区别是<b>可以要好几样材料</b>：一口锅要凑齐
     * 配料才做得出一道菜，而不是一样东西变一样。材料里重复写两次就表示
     * 要两份（比如腊八蒜要两瓶醋）。</p>
     *
     * @param output        产出物品 id
     * @param outputCount   产出数量
     * @param ticks         耗时（tick）
     * @param ingredients   需要的材料（物品 id 或 {@code #命名空间:标签路径}）
     */
    public record CookEntry(String output, int outputCount, int ticks,
                            List<String> ingredients) {}

    /** 一条案板切割规则。
     *
     * @param input      输入（物品 id 或 {@code #命名空间:标签路径}）
     * @param output     产出物品 id
     * @param needsKnife 是否需要手持刀类工具
     * @param extraTime  额外耗时（tick），0 表示瞬间完成
     */
    public record CuttingEntry(String input, String output, boolean needsKnife, int extraTime) {}

    /** 水磨：谷物 -> 粉末。需要紧邻水源。 */
    public static final List<Entry> MILLING = List.of(
'''

CUTTING_MID = '''    );

    /** 脱壳机：带壳谷物 -> 米。需要红石信号。 */
    public static final List<Entry> SHELLING = List.of(
'''

CUTTING_FOOTER = '''    );

    /** 蒸笼的锅谱：面点、糕饼这类靠蒸汽的东西。 */
    public static final List<CookEntry> STEAMER = List.of(
'''

BOILING_MID = '''    );

    /** 汤锅的锅谱：炖、汤、饭这类久煮的东西。 */
    public static final List<CookEntry> SOUP_POT = List.of(
'''

COOKING_MID = '''    );

    /** 炒锅的锅谱：炒、煎、整菜这类猛火的东西。 */
    public static final List<CookEntry> WOK = List.of(
'''

CUTTING_REAL = '''    );

    /** 案板切割。先匹配具体物品、再匹配标签，所以顺序有意义。 */
    public static final List<CuttingEntry> CUTTING = List.of(
'''

CUTTING_END = '''    );

    private ModRecipes() {}
}
'''


def _bare(item_id):
    """把本模组命名空间前缀去掉。

    产出 / 副产物统一写成本模组的裸 id（由 ProcessRecipes 解析时补命名空间），
    这样生成出来的表更短，也不会出现"有的带前缀、有的不带"的不一致。
    """
    prefix = NAMESPACE + ":"
    return item_id[len(prefix):] if item_id.startswith(prefix) else item_id


def _entry_lines(entries):
    lines = []
    for (inp, out, count, by, chance, ticks) in entries:
        lines.append('            new Entry("%s", "%s", %d, "%s", %.2fF, %d)'
                     % (inp, _bare(out), count, _bare(by), chance, ticks))
    return lines


def _cook_lines(entries):
    """把 (产出, 数量, tick, [材料...]) 写成 CookEntry 的构造调用。"""
    lines = []
    for (out, count, ticks, ingredients) in entries:
        mats = ", ".join('"%s"' % m for m in ingredients)
        lines.append('            new CookEntry("%s", %d, %d, List.of(%s))'
                     % (_bare(out), count, ticks, mats))
    return lines


def dish_cook_plan(dishes):
    """算出每道菜该在哪口锅里做、要哪些材料。

    返回 {@code {锅名: [(产出, 数量, tick, [材料...]), ...]}}。

    三道规矩：

    1. **简单转化优先**。像"面粉 -> 馒头"这种一样进一样出的，已经在
       STEAMING 那一类表里写好了；如果菜单/小吃里恰好有同名的菜，
       就不再给它生成一份"面粉 + 葱 + 姜"的怪配方。
    2. **手写过的不自动生成**。少数菜（麻婆豆腐、腊八蒜）的用料得精确，
       写在 {@code DISH_COOK_OVERRIDE} 里。
    3. 其余的按"图标种类 -> 做法 -> 锅"三级映射批量展开 ——
       所以加一道新菜只要在 DISHES 里填一行，锅谱会自动跟上。
    """
    # 第 1 条：已经被简单转化产出的东西，不再自动配锅谱
    shortcuts = set()
    for table in (DATA.STEAMING, DATA.BOILING, DATA.COOKING):
        for (_inp, out, _count, _by, _chance, _ticks) in table:
            shortcuts.add(out.split(":")[-1])
    # 多材料的调味料配方（见 DATA.POT）同样是"已经写好了"的，不要再自动生成
    for (_pot, out, _count, _ticks, _mats) in DATA.POT:
        shortcuts.add(out.split(":")[-1])

    plan = {"STEAMER": [], "SOUP_POT": [], "WOK": []}

    # 多材料的酱 / 醋 / 酒 / 汤底：直接按写好的锅与材料放进计划
    for (pot, out, count, ticks, mats) in DATA.POT:
        plan[pot].append((out, count, ticks, list(mats)))

    # 简单转化本身也是一条锅谱（一样材料）
    for table, key in ((DATA.STEAMING, "STEAMER"),
                       (DATA.BOILING, "SOUP_POT"),
                       (DATA.COOKING, "WOK")):
        for (inp, out, count, by, chance, ticks) in table:
            if by or chance:
                raise ValueError(
                    "锅谱里的简单转化不支持副产物（%s -> %s）；"
                    "要副产物请改用 Entry 那张表" % (inp, out))
            plan[key].append((out, count, ticks, [inp]))

    for dish in dishes:
        did = dish["id"]
        override = DATA.DISH_COOK_OVERRIDE.get(did)
        if override is not None:
            cooker, mats, count, ticks = override
            plan[cooker].append((did, count, ticks, list(mats)))
            continue

        if did in shortcuts:
            continue        # 第 1 条

        mapping = DATA.DISH_RECIPE_KIND.get(dish["kind"])
        if mapping is None:
            raise ValueError(
                "菜品 %s（图标种类 %s）没有锅谱映射："
                "请在 DISH_RECIPE_KIND 里加上容器与做法，"
                "或把这道菜写进 DISH_COOK_OVERRIDE" % (did, dish["kind"]))
        _vessel, method = mapping
        cooker = DATA.DISH_COOKER.get(method)
        if cooker is None:
            raise ValueError("做法 %s 没有对应的锅（DISH_COOKER）" % method)
        plan[cooker].append((did, 1, DATA.DISH_COOK_TICKS[method],
                             list(DATA.DISH_RECIPE_MATERIALS[method])))
    return plan


def gen_recipes_table(dishes):
    plan = dish_cook_plan(dishes)

    # 注意：List.of(...) 的实参列表不能有尾随逗号（数组初始化才行），
    # 所以用 ",\n".join 而不是给每行都加逗号。
    parts = [CUTTING_HEADER,
             ",\n".join(_entry_lines(DATA.MILLING)), "\n",
             CUTTING_MID,
             ",\n".join(_entry_lines(DATA.SHELLING)), "\n",
             CUTTING_FOOTER,
             ",\n".join(_cook_lines(plan["STEAMER"])), "\n",
             BOILING_MID,
             ",\n".join(_cook_lines(plan["SOUP_POT"])), "\n",
             COOKING_MID,
             ",\n".join(_cook_lines(plan["WOK"])), "\n",
             CUTTING_REAL,
             ",\n".join('            new CuttingEntry("%s", "%s", %s, %d)'
                        % (i, o, "true" if k else "false", t)
                        for (i, o, k, t) in DATA.CUTTING), "\n",
             CUTTING_END]
    write(os.path.join(JAVA, "common", "recipe", "ModRecipes.java"), "".join(parts))
    # 早期版本叫 ModCutting，现已合并进 ModRecipes；留着会编译进旧表
    drop_if_exists(os.path.join(JAVA, "common", "recipe", "ModCutting.java"))
    print("recipes: milling=%d shelling=%d | 锅谱 steamer=%d soup_pot=%d wok=%d | cutting=%d"
          % (len(DATA.MILLING), len(DATA.SHELLING),
             len(plan["STEAMER"]), len(plan["SOUP_POT"]), len(plan["WOK"]),
             len(DATA.CUTTING)))
    return plan


# ======================================================================
# 菜品摆放：器型表 + 配色表（给「直接摆在地上的菜」用）
# ======================================================================

DISH_PLACEMENT_HEADER = '''package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.registry.ModItems;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.item.Item;
import org.jetbrains.annotations.Nullable;

/**
 * 菜品 -> 三维器型 / 配色 的查表。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b>
 * 要调整请编辑 {@code tools/content_data.py}（配色）
 * 与 {@code tools/dish_models.py}（器型）。</p>
 *
 * <p>摆在地上的菜是<b>一个方块 + 两个方块状态属性</b>（原版蛋糕 / 南瓜派
 * 也是这个路子）：{@code shape} 选三维几何，{@code palette} 决定颜色。
 * 颜色被方块着色（BlockTintSource）读出来 —— 但它<b>必须</b>放在方块状态里，
 * 原因见下面 {@link Palette} 的注释。所以不需要给每道菜写渲染器。</p>
 */
public final class DishPlacement {
    /** 器型，顺序必须与 {@code tools/dish_models.py} 的 SHAPE_ORDER 一致。
     *  实现 {@link StringRepresentable} 是 {@code EnumProperty} 的要求，
     *  序列化出来的名字就是方块状态 JSON 里的键。 */
    public enum Shape implements StringRepresentable {
'''

DISH_PLACEMENT_MID = '''        ;

        private final int id;

        Shape(int id) {
            this.id = id;
        }

        public int id() {
            return this.id;
        }

        @Override
        public String getSerializedName() {
            return this.name().toLowerCase(java.util.Locale.ROOT);
        }
    }

    /**
     * 每种器型的包围盒：<b>minX, minY, minZ, maxX, maxY, maxZ</b>（方块坐标系，0~16）。
     *
     * <p>这些数字不是拍脑袋写的，而是 {@code tools/dish_models.py} 从模型元素
     * 的极值实测出来的 —— 所以落在地上时是"<b>模型多大就占多大</b>"：
     * 盘子只有薄薄一层，粽子占地很小，酒盏不会挡住整格。</p>
     */
    private static final float[][] BOUNDS = {
'''

DISH_PLACEMENT_MID_B = '''    };

    /**
     * 配色（取值就是 {@code content_data.PALETTES} 的键）。
     *
     * <h2>为什么颜色要放进方块状态</h2>
     * 26.1 的方块模型着色走 {@code BlockStateModelWrapper#updateTints}，
     * 它<b>只调用 {@code BlockTintSource#color(BlockState)}</b>：
     * {@code update()} 里传给模型的上下文是 {@code BlockAndTintGetter.EMPTY}
     * 与 {@code BlockPos.ZERO}，整条路径上既没有世界也没有方块实体，
     * {@code colorInWorld} <b>永远不会被调用</b>。
     *
     * <p>所以原先"从方块实体查颜色"的做法只会拿到常量白 —— 菜全是白的。
     * 把颜色做成方块状态属性之后，区块烘焙、物品栏、破坏粒子
     * 拿到的都是同一个正确颜色（顺便也不再需要方块实体参与渲染）。</p>
     */
    public enum Palette implements StringRepresentable {
'''

DISH_PLACEMENT_PALETTE_TAIL = '''        ;

        private final int id;
        private final int color;
        private final int liquidColor;

        Palette(int id, int color) {
            this.id = id;
            this.color = color;
            int r = (color >> 16 & 0xFF) * 3 / 4;
            int g = (color >> 8 & 0xFF) * 3 / 4;
            int b = (color & 0xFF) * 3 / 4;
            this.liquidColor = r << 16 | g << 8 | b;
        }

        public int id() {
            return this.id;
        }

        /** 食物主体色（0xRRGGBB）。 */
        public int color() {
            return this.color;
        }

        /** 汤汁 / 汁水色：主色压暗一档。 */
        public int liquidColor() {
            return this.liquidColor;
        }

        @Override
        public String getSerializedName() {
            return this.name().toLowerCase(java.util.Locale.ROOT);
        }
    }

    private static final Map<Item, Shape> SHAPE_BY_ITEM = new HashMap<>();
    private static final Map<Item, Palette> PALETTE_BY_ITEM = new HashMap<>();

    static {
'''

DISH_PLACEMENT_FOOTER = '''    }

    /** 这道菜的器型；不在表里返回 {@code null}（表示不能摆）。 */
    @Nullable
    public static Shape shapeOf(Item item) {
        return SHAPE_BY_ITEM.get(item);
    }

    /** 这道菜的配色；不在表里返回 {@code null}。 */
    @Nullable
    public static Palette paletteOf(Item item) {
        return PALETTE_BY_ITEM.get(item);
    }

    /**
     * 器型的包围盒，顺序是 {@code [minX, minY, minZ, maxX, maxY, maxZ]}。
     *
     * <p>拿它直接建 {@code VoxelShape}，就能做到"模型多大就占多大"。</p>
     */
    public static float[] boundsOf(Shape shape) {
        return BOUNDS[shape.id()];
    }

    private DishPlacement() {}
}
'''


def gen_dish_placement(dishes):
    """生成 DishPlacement.java：器型枚举 + 配色枚举 + 两张查表 + 实测包围盒。"""
    import dish_models as DM

    enum_lines = []
    for i, shape in enumerate(DM.SHAPE_ORDER):
        enum_lines.append("        %s(%d)" % (shape.upper(), i))
    enum_body = ",\n".join(enum_lines) + "\n"

    # 配色枚举：顺序与 content_data.PALETTES 的插入顺序一致
    palette_lines = []
    palette_color = {}
    for i, (name, ramp) in enumerate(DATA.PALETTES.items()):
        main = ramp[0]
        palette_color[name] = main
        palette_lines.append("        %s(%d, 0x%02X%02X%02X)" % (name.upper(), i, main[0], main[1], main[2]))
    palette_body = ",\n".join(palette_lines) + "\n"

    # 包围盒：直接从 dish_models 的模型元素实测，保证模型与碰撞箱一致
    bounds_lines = []
    for shape in DM.SHAPE_ORDER:
        b = DM.bounds(shape)
        bounds_lines.append("            {%s}," % ", ".join("%.2fF" % v for v in b))
    bounds_body = "\n".join(bounds_lines) + "\n"

    shape_lines = []
    palette_puts = []
    for dish in dishes:
        shape = DM.shape_for(dish["kind"])
        if shape is None:
            continue
        const = const_name(dish["id"])
        shape_lines.append("        SHAPE_BY_ITEM.put(ModItems.%s.get(), Shape.%s);"
                           % (const, shape.upper()))
        palette_puts.append("        PALETTE_BY_ITEM.put(ModItems.%s.get(), Palette.%s);"
                            % (const, dish["palette"].upper()))

    body = (DISH_PLACEMENT_HEADER + enum_body + DISH_PLACEMENT_MID + bounds_body
            + DISH_PLACEMENT_MID_B + palette_body + DISH_PLACEMENT_PALETTE_TAIL
            + "\n".join(shape_lines) + "\n\n" + "\n".join(palette_puts) + "\n"
            + DISH_PLACEMENT_FOOTER)
    write(os.path.join(JAVA, "common", "block", "DishPlacement.java"), body)
    print("dish placement: %d 道菜可摆，器型 %d 种，配色 %d 种"
          % (len(shape_lines), len(DM.SHAPE_ORDER), len(DATA.PALETTES)))


# ======================================================================
# 语言文件
# ======================================================================

def gen_lang(items, dishes):
    zh = {"itemGroup.chinese_traditional_food.main": "国风·传统食物"}
    en = {"itemGroup.chinese_traditional_food.main": "Chinese Traditional Food"}

    # 方块与已有条目
    zh.update({
        "block.chinese_traditional_food.plate": "餐盘",
        "block.chinese_traditional_food.cutting_board": "案板",
        # 摆在地上的菜：没有对应物品（拿不起来），但准星指着它时
        # Jade 会显示名字，所以还是得有键，否则那里会显示出一串键名
        "block.chinese_traditional_food.placed_dish": "摆放的菜品",
        "block.chinese_traditional_food.furnace_generator": "熔炉发电机",
        "block.chinese_traditional_food.electric_mill": "电动磨粉机",
        "block.chinese_traditional_food.electric_sheller": "电动脱壳机",
        "block.chinese_traditional_food.large_furnace_generator": "大型熔炉发电机",
        "block.chinese_traditional_food.large_electric_mill": "大型电动磨粉机",
        "block.chinese_traditional_food.large_electric_sheller": "大型电动脱壳机",
        "container.chinese_traditional_food.large_electric_mill": "大型电动磨粉机",
        "container.chinese_traditional_food.large_electric_sheller": "大型电动脱壳机",
        "block.chinese_traditional_food.stove": "磁烧炉",
        "block.chinese_traditional_food.wok": "炒锅",
        "block.chinese_traditional_food.steamer": "蒸笼",
        "block.chinese_traditional_food.soup_pot": "汤锅",
        "container.chinese_traditional_food.stove": "磁烧炉",
        "container.chinese_traditional_food.wok": "炒锅",
        "container.chinese_traditional_food.steamer": "蒸笼",
        "container.chinese_traditional_food.soup_pot": "汤锅",
        "tooltip.chinese_traditional_food.stove_heating": "正在供热（%d / %d FE）",
        "tooltip.chinese_traditional_food.stove_no_power": "没有接电（%d / %d FE）",
        "tooltip.chinese_traditional_food.appliance_hot": "有热，正在加热",
        "tooltip.chinese_traditional_food.appliance_cold": "没有热——请在正下方放一个磁烧炉并接上电",
        "tooltip.chinese_traditional_food.heat_amount": "热力",
        "tooltip.chinese_traditional_food.gui_no_heat": "炉灶没火",
        "tooltip.chinese_traditional_food.gui_heat_hint": "需坐在炉灶上",
        "container.chinese_traditional_food.electric_mill": "电动磨粉机",
        "container.chinese_traditional_food.electric_sheller": "电动脱壳机",
        "container.chinese_traditional_food.furnace_generator": "熔炉发电机",
        "tooltip.chinese_traditional_food.furnace_generator":
            "烧原版燃料发电，六个面自动往外送电（煤炭就能烧）",
        "tooltip.chinese_traditional_food.electric_mill":
            "接上电就能磨粉：一次 8 个，一批 10 秒",
        "tooltip.chinese_traditional_food.electric_sheller":
            "接上电就能脱壳：一次 8 个，一批 10 秒",
        "tooltip.chinese_traditional_food.machine_has_power":
            "电量 %s / %s FE —— 可以开工",
        "tooltip.chinese_traditional_food.machine_no_power":
            "电量 %s / %s FE —— 没电，接一台熔炉发电机",
        "tooltip.chinese_traditional_food.generator_burning":
            "正在发电：%s / %s FE，输出 %s FE/t",
        "tooltip.chinese_traditional_food.generator_idle":
            "已停机：%s / %s FE，输出 %s FE/t（需要燃料）",
        "tooltip.chinese_traditional_food.energy_amount": "%s / %s FE",
        "tooltip.chinese_traditional_food.gui_no_power": "没电：给它接一台熔炉发电机",
        "tooltip.chinese_traditional_food.gui_burning": "正在发电",
        "tooltip.chinese_traditional_food.gui_need_fuel": "缺燃料",
        "tooltip.chinese_traditional_food.gui_output": "输出 40 FE/t",
        # ---- JEI（配方查看器）上的文案 ----
        "jei.chinese_traditional_food.duration": "耗时 %s 秒",
        "jei.chinese_traditional_food.byproduct": "有 %s%% 的概率额外得到",
        "jei.chinese_traditional_food.needs_knife": "需要手持刀才好使",
        "jei.chinese_traditional_food.pot_hint": "把它放在电磁炉正上方就能开火",
    })
    en.update({
        "block.chinese_traditional_food.plate": "Plate",
        "block.chinese_traditional_food.cutting_board": "Cutting Board",
        "block.chinese_traditional_food.placed_dish": "Placed Dish",
        "block.chinese_traditional_food.furnace_generator": "Furnace Generator",
        "block.chinese_traditional_food.electric_mill": "Electric Mill",
        "block.chinese_traditional_food.electric_sheller": "Electric Sheller",
        "block.chinese_traditional_food.large_furnace_generator": "Large Furnace Generator",
        "block.chinese_traditional_food.large_electric_mill": "Large Electric Mill",
        "block.chinese_traditional_food.large_electric_sheller": "Large Electric Sheller",
        "container.chinese_traditional_food.large_electric_mill": "Large Electric Mill",
        "container.chinese_traditional_food.large_electric_sheller": "Large Electric Sheller",
        "block.chinese_traditional_food.stove": "Induction Cooker",
        "block.chinese_traditional_food.wok": "Wok",
        "block.chinese_traditional_food.steamer": "Bamboo Steamer",
        "block.chinese_traditional_food.soup_pot": "Soup Pot",
        "container.chinese_traditional_food.stove": "Induction Cooker",
        "container.chinese_traditional_food.wok": "Wok",
        "container.chinese_traditional_food.steamer": "Bamboo Steamer",
        "container.chinese_traditional_food.soup_pot": "Soup Pot",
        "tooltip.chinese_traditional_food.stove_heating": "Heating (%d / %d FE)",
        "tooltip.chinese_traditional_food.stove_no_power": "No power (%d / %d FE)",
        "tooltip.chinese_traditional_food.appliance_hot": "Heating",
        "tooltip.chinese_traditional_food.appliance_cold": "No heat - place an Induction Cooker below and power it",
        "tooltip.chinese_traditional_food.heat_amount": "Heat",
        "tooltip.chinese_traditional_food.gui_no_heat": "No fire",
        "tooltip.chinese_traditional_food.gui_heat_hint": "Needs a Stove below",
        "container.chinese_traditional_food.electric_mill": "Electric Mill",
        "container.chinese_traditional_food.electric_sheller": "Electric Sheller",
        "container.chinese_traditional_food.furnace_generator": "Furnace Generator",
        "tooltip.chinese_traditional_food.furnace_generator":
            "Burns vanilla fuel (coal is enough) and pushes power out on all six sides",
        "tooltip.chinese_traditional_food.electric_mill":
            "Give it power and it mills: 8 items per batch, 10 seconds each",
        "tooltip.chinese_traditional_food.electric_sheller":
            "Give it power and it shells: 8 items per batch, 10 seconds each",
        "tooltip.chinese_traditional_food.machine_has_power":
            "Energy %s / %s FE -- ready to run",
        "tooltip.chinese_traditional_food.machine_no_power":
            "Energy %s / %s FE -- no power, hook up a Furnace Generator",
        "tooltip.chinese_traditional_food.generator_burning":
            "Generating: %s / %s FE, output %s FE/t",
        "tooltip.chinese_traditional_food.generator_idle":
            "Idle: %s / %s FE, output %s FE/t (needs fuel)",
        "tooltip.chinese_traditional_food.energy_amount": "%s / %s FE",
        "tooltip.chinese_traditional_food.gui_no_power": "No power -- hook up a Furnace Generator",
        "tooltip.chinese_traditional_food.gui_burning": "Generating",
        "tooltip.chinese_traditional_food.gui_need_fuel": "Needs fuel",
        "tooltip.chinese_traditional_food.gui_output": "Output 40 FE/t",
        # ---- JEI（配方查看器）上的文案 ----
        "jei.chinese_traditional_food.duration": "%s s",
        "jei.chinese_traditional_food.byproduct": "%s%% chance of an extra drop",
        "jei.chinese_traditional_food.needs_knife": "Requires a knife in hand",
        "jei.chinese_traditional_food.pot_hint": "Stand it on an induction cooker to fire up",
    })

    # 按类别写注释分组（JSON 不支持注释，用顺序 + 分组标题的键值对不可行，
    # 所以这里直接按键排序输出，人工阅读依然清晰）
    for item in items + dishes:
        if item["category"] == "seed":
            # 种子是**方块物品**（BlockItem），键必须跟着方块走。
            #
            # NeoForge 的 registerSimpleBlockItem 会给物品加上
            # `useBlockDescriptionPrefix`，于是它的翻译键是 `block.<物品id>`
            # 而不是 `item.<物品id>`。写在 item. 下的话，游戏里
            # 会把键名原样显示出来（"block.chinese_traditional_food.rice_seeds"）——
            # 这就是玩家看到的"语言坏了"。
            zh["block.chinese_traditional_food.%s" % item["id"]] = item["zh"]
            en["block.chinese_traditional_food.%s" % item["id"]] = item["en"]
            continue
        zh["item.chinese_traditional_food.%s" % item["id"]] = item["zh"]
        en["item.chinese_traditional_food.%s" % item["id"]] = item["en"]

    # 状态效果
    zh.update({
        "effect.chinese_traditional_food.reunion": "团圆",
        "effect.chinese_traditional_food.rise_up": "步步高升",
        "effect.chinese_traditional_food.perfection": "圆满",
    })
    en.update({
        "effect.chinese_traditional_food.reunion": "Reunion",
        "effect.chinese_traditional_food.rise_up": "Rising Step",
        "effect.chinese_traditional_food.perfection": "Perfection",
    })

    # 提示文本
    zh["tooltip.chinese_traditional_food.dish_display"] = "空手右键夹一口，潜行右键整份端走"
    en["tooltip.chinese_traditional_food.dish_display"] = \
        "Empty-hand right-click to take a bite, sneak right-click to pick the dish up"

    # 食材压缩方块的语言键。
    #
    # 这里**必须**写进来，不能让 gen_compressed.py 自己追加 ——
    # 本函数会整份重写 lang 文件，先跑 gen_compressed 再跑 gen_content
    # 就会把它写进去的键全冲掉（踩过一次）。所以让"唯一的语言来源"
    # 在这里把压缩方块的清单读进来一起写。
    import gen_compressed as COMP
    for row in COMP.COMPRESSED:
        bid, zh_name, en_name = row[0], row[1], row[2]
        zh["block.%s.%s" % (NAMESPACE, bid)] = zh_name
        en["block.%s.%s" % (NAMESPACE, bid)] = en_name

    # 作物植株与野生植株的方块名。同样是"唯一的语言来源"把它一起写掉 ——
    # gen_crops.py 不碰 lang 文件，免得两边抢着重写（和压缩方块一个道理）。
    names = {row[0]: (row[1], row[2]) for row in DATA.CROPS}
    for (crop_id, zh_name, en_name, _seed, _prod, _habit) in DATA.CROPS:
        zh["block.%s.%s_crop" % (NAMESPACE, crop_id)] = "%s植株" % zh_name
        en["block.%s.%s_crop" % (NAMESPACE, crop_id)] = "%s Crop" % en_name
    for row in DATA.WILD_CROPS:
        zh_name, en_name = names[row[0]]
        zh["block.%s.wild_%s" % (NAMESPACE, row[0])] = "野生%s" % zh_name
        en["block.%s.wild_%s" % (NAMESPACE, row[0])] = "Wild %s" % en_name

    # 果树：树苗 / 树叶 / 以及 13 套木制品。名字里的水果名直接取那一行，不手抄。
    fruit_names = {row[0]: (row[1], row[2]) for row in DATA.FRUITS}
    fruit_names.update({row[0]: (row[1], row[2]) for row in DATA.INGREDIENTS})
    for (fruit, _size) in DATA.TREE_FRUITS:
        zh_name, en_name = fruit_names[fruit]
        zh["block.%s.%s_sapling" % (NAMESPACE, fruit)] = "%s树苗" % zh_name
        en["block.%s.%s_sapling" % (NAMESPACE, fruit)] = "%s Sapling" % en_name
        zh["block.%s.%s_leaves" % (NAMESPACE, fruit)] = "%s树叶" % zh_name
        en["block.%s.%s_leaves" % (NAMESPACE, fruit)] = "%s Leaves" % en_name

    # 木质方块：`枣木原木` / `枣木木板` / `去皮枣木原木` ……
    # 后缀与名字模板都在 content_data 里，所以这里一个名字都不用硬编码。
    # **注意**：这些是方块物品（BlockItem），键必须是 `block.` —— 写 `item.`
    # 的话游戏里会直接显示键名（踩过，见 check_lang.py 的说明）。
    for (fruit, _size) in DATA.TREE_FRUITS:
        zh_name, en_name = fruit_names[fruit]
        for (_suffix, zh_tpl, en_tpl, _src) in DATA.TREE_WOOD_FORMS:
            bid = "%s%s" % (fruit, _suffix)
            zh["block.%s.%s" % (NAMESPACE, bid)] = zh_tpl.format(w=zh_name)
            en["block.%s.%s" % (NAMESPACE, bid)] = en_tpl.format(f=en_name)

    write_json(os.path.join(RES, "assets", NAMESPACE, "lang", "zh_cn.json"), zh)
    write_json(os.path.join(RES, "assets", NAMESPACE, "lang", "en_us.json"), en)


# ======================================================================
# 客户端物品 + 物品模型
# ======================================================================

def gen_item_assets(items, dishes):
    base_items = os.path.join(RES, "assets", NAMESPACE, "items")
    base_models = os.path.join(RES, "assets", NAMESPACE, "models", "item")

    for entry in items + dishes:
        item_id = entry["id"]
        write_json(os.path.join(base_items, "%s.json" % item_id), {
            "model": {
                "type": "minecraft:model",
                "model": "%s:item/%s" % (NAMESPACE, item_id),
            }
        })
        write_json(os.path.join(base_models, "%s.json" % item_id), {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": "%s:item/%s" % (NAMESPACE, item_id)},
        })


# ======================================================================
# 手写功能方块的「方块物品」客户端资源
# ======================================================================

# id -> 物品模型指向。写成 "block/<id>" 就是用**三维方块模型**当物品图标
# （像原版的台阶、栅栏那样有立体感），写成 "item/<id>" 就是用 2D 图标。
BLOCK_ITEM_MODELS = {
    # 餐具类：三维模型本身就很精致，直接拿来做物品图标最有立体感
    "plate": "block/plate",
    "cutting_board": "block/cutting_board",
    # 机器：三个都是单方块，用 2D 图标最清楚（尤其发电机和加工机长得像，
    # 直接拿模型当图标很难分辨）。
    "furnace_generator": "item/furnace_generator",
    "electric_mill": "item/electric_mill",
    "electric_sheller": "item/electric_sheller",
    # 大型机也用 2D 图标，理由同上；图标里多画了双烟囱 / 双磨盘 / 双滚筒，
    # 和小型机放在一起能一眼区分。
    "large_furnace_generator": "item/large_furnace_generator",
    "large_electric_mill": "item/large_electric_mill",
    "large_electric_sheller": "item/large_electric_sheller",
    # 灶火系统：四件器物的造型本身就很有辨识度（矮灶 / 敞口锅 / 三层蒸笼 /
    # 高筒汤锅），直接拿三维模型当物品图标比再画一张 2D 图标更省事也更好认。
    "stove": "block/stove",
    "wok": "block/wok",
    "steamer": "block/steamer",
    "soup_pot": "block/soup_pot",
}


def gen_block_item_assets():
    """给手写方块生成客户端物品定义（26.1 起物品模型改由 items/*.json 指定）。"""
    base_items = os.path.join(RES, "assets", NAMESPACE, "items")
    base_models = os.path.join(RES, "assets", NAMESPACE, "models", "item")

    count = 0
    for block_id, target in BLOCK_ITEM_MODELS.items():
        write_json(os.path.join(base_items, "%s.json" % block_id), {
            "model": {
                "type": "minecraft:model",
                "model": "%s:%s" % (NAMESPACE, target),
            }
        })
        if target.startswith("item/"):
            # 2D 图标：还需要一张 models/item 的生成模型
            write_json(os.path.join(base_models, "%s.json" % block_id), {
                "parent": "minecraft:item/generated",
                "textures": {"layer0": "%s:item/%s" % (NAMESPACE, block_id)},
            })
        count += 1
    print("block item assets: %d" % count)


# ======================================================================
# 配方
# ======================================================================

def ingredient_json(token):
    """26.1 起 Ingredient 的 JSON 就是**纯字符串**：

       具体物品 -> {"minecraft:wheat"}
       标签     -> {"#c:flour"}

    老版本的 {"item": ...} / {"tag": ...} 对象形式已经不用了。
    这一点是跑客户端时从日志里发现的（List is too short: 0, expected range [1-9]），
    对照原版 data/minecraft/recipe/*.json 才确认。
    """
    return token


def recipe_object(recipe_id, spec):
    kind = spec[0]
    if kind == "shapeless":
        mats, count = spec[1], spec[2]
        return {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [ingredient_json(m) for m in mats],
            "result": {"id": "%s:%s" % (NAMESPACE, recipe_id), "count": count},
        }
    if kind == "shaped":
        shaped, count = spec[1], spec[2]
        return {
            "type": "minecraft:crafting_shaped",
            "pattern": shaped["pattern"],
            "key": {k: ingredient_json(v) for k, v in shaped["key"].items()},
            "result": {"id": "%s:%s" % (NAMESPACE, recipe_id), "count": count},
        }
    if kind == "smelting":
        mats, count = spec[1], spec[2]
        return {
            "type": "minecraft:smelting",
            "ingredient": ingredient_json(mats[0]),
            "experience": 0.1,
            "cookingtime": 200,
            "result": {"id": "%s:%s" % (NAMESPACE, recipe_id), "count": count},
        }
    raise ValueError("未知配方类型: %s (%s)" % (kind, recipe_id))


def gen_recipes(items, dishes):
    """生成工作台 / 熔炉配方。

    <b>菜品不在这里。</b> 所有菜品一律用锅做，锅谱由
    {@link gen_recipes_table} 写进 {@code ModRecipes}。
    这里只处理"工作台能直接做出来的东西"：食材加工、调料、厨具、机器。
    """
    base = os.path.join(RES, "data", NAMESPACE, "recipe")
    known = ({i["id"] for i in items} | {d["id"] for d in dishes}
             | {"plate", "cutting_board",
                "furnace_generator", "electric_mill", "electric_sheller",
                "large_furnace_generator", "large_electric_mill", "large_electric_sheller",
                "stove", "wok", "steamer", "soup_pot",
                "placed_dish"})

    # 菜品 id 集合：这些**不该**出现在工作台配方里（要用锅）
    dish_ids = {d["id"] for d in dishes}

    written = 0
    skipped = 0
    keep = set()
    for recipe_id, spec in DATA.RECIPES.items():
        if recipe_id not in known:
            raise ValueError("配方 %s 对应的物品不存在" % recipe_id)
        if recipe_id in dish_ids:
            # 手滑把菜写进 RECIPES 了 —— 直接报错，免得出现"工作台也能做"的双重做法
            raise ValueError(
                "配方 %s 是一道菜，菜品必须用锅做：请把它写进 DISH_COOK_OVERRIDE，"
                "或改成靠 DISH_RECIPE_KIND 自动展开" % recipe_id)
        write_json(os.path.join(base, "%s.json" % recipe_id), recipe_object(recipe_id, spec))
        keep.add(recipe_id)
        written += 1

    # ---- 清理：把"以前生成过、现在不该再有"的配方删掉 ----
    #
    # 生成器只写不删的话，删掉 RECIPES 里的条目并不会让旧 json 消失，
    # 结果就是"改了代码但游戏里的配方没变"（数据包照样加载那些残留文件）。
    #
    # 但清理**必须知道有哪些文件是别的生成器管理**的：压缩方块那 190 条配方
    # 也写在这个目录里（由 gen_compressed.py 生成），不知道就会一起删掉 ——
    # 第一次加这段清理时就误删过一次。
    try:
        import gen_compressed as COMP
        for row in COMP.COMPRESSED:
            keep.add(row[0])                  # 9 个原料 → 1 个方块
            keep.add("%s_unpack" % row[0])     # 1 个方块 → 9 个原料
    except Exception:                          # noqa: BLE001
        pass

    # 木制品那 78 条配方也写在这个目录里（gen_woods.py 生成）。
    # 忘了排除的话，第一次加清理就会把它们全删掉 —— 压缩方块那次已经栽过一回。
    try:
        import gen_woods as WOODS
        keep |= WOODS.recipe_ids()
    except Exception:                          # noqa: BLE001
        pass

    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name)
        if not os.path.isfile(path) or not name.endswith(".json"):
            continue
        recipe_id = name[:-5]
        if recipe_id in keep:
            continue
        os.remove(path)
        skipped += 1

    print("recipes: workbench=%d（另清理了 %d 个不再需要的配方文件）" % (written, skipped))


# ======================================================================
# 标签
# ======================================================================

def gen_tags(dishes):
    # --- 本模组标签 ---
    item_tags = os.path.join(RES, "data", NAMESPACE, "tags", "item")
    write_json(os.path.join(item_tags, "dishes.json"), {
        "replace": False,
        "values": ["%s:%s" % (NAMESPACE, d["id"]) for d in dishes],
    })
    write_json(os.path.join(item_tags, "placeable_dishes.json"), {
        "replace": False,
        "values": ["#%s:dishes" % NAMESPACE, "%s:tofu" % NAMESPACE],
    })
    for tag, values in DATA.OWN_TAGS.items():
        if tag in ("dishes", "placeable_dishes"):
            continue
        # seeds 标签的成员变了：种子不再由 ModItems 注册，而是 ModCrops 里的
        # 方块物品，所以这里按 CROPS 表现算，别用 content_data 里那份手写的旧清单
        # （那份里有一半 id 已经不存在了，进游戏会报 "missing following references"）。
        if tag == "seeds":
            values = ["%s:%s" % (NAMESPACE, row[3]) for row in DATA.CROPS]
            values.append("minecraft:wheat_seeds")
        write_json(os.path.join(item_tags, "%s.json" % tag), {
            "replace": False,
            "values": values,
        })

    # --- c 命名空间通用标签（NeoForge / Fabric 通用约定） ---
    c_tags = os.path.join(RES, "data", "c", "tags", "item")
    for tag, values in DATA.C_TAGS.items():
        write_json(os.path.join(c_tags, "%s.json" % tag), {
            "replace": False,
            "values": values,
        })
    print("tags: own=%d c=%d" % (len(DATA.OWN_TAGS), len(DATA.C_TAGS)))


# ======================================================================
def main():
    items, dishes = collect()
    print("items: %d, dishes: %d, total: %d" % (len(items), len(dishes), len(items) + len(dishes)))

    gen_mod_items(items, dishes)
    gen_creative_tabs()
    # 锅谱要先算：gen_recipes 会清理旧的"菜品工作台配方"，
    # 而 gen_recipes_table 需要完整的菜品表来展开
    gen_recipes_table(dishes)
    gen_dish_placement(dishes)
    gen_lang(items, dishes)
    gen_item_assets(items, dishes)
    gen_block_item_assets()
    gen_recipes(items, dishes)
    gen_tags(dishes)
    # 作物：它要写 ModCrops.java、植株模型与掉浇、以及野生作物的世界生成
    gen_crops.main()
    # 果树：ModTrees.java + 树苗/树叶模型与掉浇
    gen_trees.main()
    # 13 套木制品：ModWoods.java + 117 个方块的模型/掉落/配方/标签/去皮数据图。
    # **必须在 gen_recipes 之后** —— 它写的配方要参与下面这一步的清理集合，
    # 而那个集合是在 gen_recipes 里读 gen_woods.recipe_ids() 算出来的。
    gen_woods.main()


if __name__ == "__main__":
    main()
