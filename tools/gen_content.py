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

    /** 大拼盘，摆放 4 份菜。 */
    public static final DeferredItem<BlockItem> SERVING_PLATTER =
            ITEMS.registerSimpleBlockItem(ModBlocks.SERVING_PLATTER);

    /** 案板，放上食材后用刀切。 */
    public static final DeferredItem<BlockItem> CUTTING_BOARD =
            ITEMS.registerSimpleBlockItem(ModBlocks.CUTTING_BOARD);

    /** 水磨，谷物磨粉。 */
    public static final DeferredItem<BlockItem> WATER_MILL =
            ITEMS.registerSimpleBlockItem(ModBlocks.WATER_MILL);

    /** 脱壳机，手摇式，无界面。 */
    public static final DeferredItem<BlockItem> GRAIN_SHELLER =
            ITEMS.registerSimpleBlockItem(ModBlocks.GRAIN_SHELLER);

    /** 水磨部件（石台 / 水轮 / 传动箱）。 */
    public static final DeferredItem<BlockItem> WATER_MILL_PART =
            ITEMS.registerSimpleBlockItem(ModBlocks.WATER_MILL_PART);

    /** 碾米机部件（木架 / 机箱板 / 立柱 / 料斗）。 */
    public static final DeferredItem<BlockItem> GRAIN_SHELLER_PART =
            ITEMS.registerSimpleBlockItem(ModBlocks.GRAIN_SHELLER_PART);

    /** 水车：装在水磨两侧接口的外侧，泡在水里转，给水磨提供动力。 */
    public static final DeferredItem<BlockItem> WATER_WHEEL =
            ITEMS.registerSimpleBlockItem(ModBlocks.WATER_WHEEL);
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
        ("作物种子", [i for i in items if i["category"] == "seed"]),
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
        out.append("\n    // ==================================================================\n")
        out.append("    // %s%s（%d 道）\n"
                   % (DATA.GROUP_TITLES[group], " —— 八大菜系" if cuisine else " —— 传统节日", len(rows)))
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
                        output.accept(ModItems.SERVING_PLATTER.get());
                        output.accept(ModItems.CUTTING_BOARD.get());
                        output.accept(ModItems.WATER_MILL.get());
                        output.accept(ModItems.WATER_MILL_PART.get());
                        output.accept(ModItems.WATER_WHEEL.get());
                        output.accept(ModItems.GRAIN_SHELLER.get());
                        output.accept(ModItems.GRAIN_SHELLER_PART.get());
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
        }
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) {
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.SERVING_PLATTER.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.WATER_MILL.get());
            event.accept(ModItems.WATER_MILL_PART.get());
            event.accept(ModItems.WATER_WHEEL.get());
            event.accept(ModItems.GRAIN_SHELLER.get());
            event.accept(ModItems.GRAIN_SHELLER_PART.get());
        }
        if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.SERVING_PLATTER.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.WATER_MILL.get());
            event.accept(ModItems.WATER_MILL_PART.get());
            event.accept(ModItems.WATER_WHEEL.get());
            event.accept(ModItems.GRAIN_SHELLER.get());
            event.accept(ModItems.GRAIN_SHELLER_PART.get());
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


def gen_recipes_table():
    # 注意：List.of(...) 的实参列表不能有尾随逗号（数组初始化才行），
    # 所以用 ",\n".join 而不是给每行都加逗号。
    parts = [CUTTING_HEADER,
             ",\n".join(_entry_lines(DATA.MILLING)), "\n",
             CUTTING_MID,
             ",\n".join(_entry_lines(DATA.SHELLING)), "\n",
             CUTTING_FOOTER,
             ",\n".join('            new CuttingEntry("%s", "%s", %s, %d)'
                        % (i, o, "true" if k else "false", t)
                        for (i, o, k, t) in DATA.CUTTING), "\n",
             CUTTING_END]
    write(os.path.join(JAVA, "common", "recipe", "ModRecipes.java"), "".join(parts))
    # 早期版本叫 ModCutting，现已合并进 ModRecipes；留着会编译进旧表
    drop_if_exists(os.path.join(JAVA, "common", "recipe", "ModCutting.java"))
    print("machine recipes: milling=%d shelling=%d cutting=%d"
          % (len(DATA.MILLING), len(DATA.SHELLING), len(DATA.CUTTING)))


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
        "block.chinese_traditional_food.serving_platter": "大拼盘",
        "block.chinese_traditional_food.cutting_board": "案板",
        "block.chinese_traditional_food.water_mill": "水磨",
        "block.chinese_traditional_food.water_mill_part": "水磨部件",
        "block.chinese_traditional_food.water_wheel": "水车",
        "tooltip.chinese_traditional_food.water_wheel":
            "装在水磨两侧接口的外侧一格；泡到水里就会转，水磨随之开工",
        "block.chinese_traditional_food.grain_sheller": "手摇碾米机",
        "block.chinese_traditional_food.grain_sheller_part": "碾米机部件",
        "container.chinese_traditional_food.water_mill": "水磨",
        "tooltip.chinese_traditional_food.water_mill":
            "放下后自动展开成 3×3×3 的大型水磨，紧邻水源即可自动研磨",
        "tooltip.chinese_traditional_food.water_mill_part":
            "水磨的石台 / 水轮 / 传动箱，补在缺件的位置即可修复水磨",
        "tooltip.chinese_traditional_food.grain_sheller":
            "3×3×3 手摇碾米机：带壳谷物右键倒入 · 潜行空手摇柄 · 空手取出米糗",
        "tooltip.chinese_traditional_food.grain_sheller_part":
            "碾米机的木架 / 机箱板 / 立柱 / 料斗，补在缺件的位置即可修复机器",
        "tooltip.chinese_traditional_food.machine_incomplete":
            "机器结构不完整，先把缺的部件补上",
        "tooltip.chinese_traditional_food.sheller_full": "装不下了，先摇几圈再倒",
        "tooltip.chinese_traditional_food.sheller_empty": "里面没有带壳谷物",
        "tooltip.chinese_traditional_food.sheller_output_full": "出料口堵住了，先把米取走",
        "tooltip.chinese_traditional_food.machine_progress": "进度",
        "tooltip.chinese_traditional_food.machine_crank_ok": "摇了一圈，出了东西",
        "tooltip.chinese_traditional_food.machine_crank_fail": "里面没东西可处理",
    })
    en.update({
        "block.chinese_traditional_food.plate": "Plate",
        "block.chinese_traditional_food.serving_platter": "Serving Platter",
        "block.chinese_traditional_food.cutting_board": "Cutting Board",
        "block.chinese_traditional_food.water_mill": "Water Mill",
        "block.chinese_traditional_food.water_mill_part": "Water Mill Part",
        "block.chinese_traditional_food.water_wheel": "Water Wheel",
        "tooltip.chinese_traditional_food.water_wheel":
            "Mount outside a mill's axle socket; submerge it in water to power the mill",
        "block.chinese_traditional_food.grain_sheller": "Hand-cranked Rice Mill",
        "block.chinese_traditional_food.grain_sheller_part": "Rice Mill Part",
        "container.chinese_traditional_food.water_mill": "Water Mill",
        "tooltip.chinese_traditional_food.water_mill":
            "Unfolds into a 3x3x3 mill; runs automatically next to water",
        "tooltip.chinese_traditional_food.water_mill_part":
            "Frame, wheel or gearbox -- put it back to repair the mill",
        "tooltip.chinese_traditional_food.grain_sheller":
            "3x3x3 hand mill: right-click with grain, sneak + empty hand to crank, empty hand to collect",
        "tooltip.chinese_traditional_food.grain_sheller_part":
            "Frame, panel, pillar or hopper -- put it back to repair the machine",
        "tooltip.chinese_traditional_food.machine_incomplete":
            "The machine is incomplete -- put the missing parts back",
        "tooltip.chinese_traditional_food.sheller_full": "It's full -- crank a few times before pouring more",
        "tooltip.chinese_traditional_food.sheller_empty": "No unhusked grain inside",
        "tooltip.chinese_traditional_food.sheller_output_full": "The outlet is blocked -- take the rice out first",
        "tooltip.chinese_traditional_food.machine_progress": "Progress",
        "tooltip.chinese_traditional_food.machine_crank_ok": "Cranked once -- something came out",
        "tooltip.chinese_traditional_food.machine_crank_fail": "There is nothing to process inside",
    })

    # 按类别写注释分组（JSON 不支持注释，用顺序 + 分组标题的键值对不可行，
    # 所以这里直接按键排序输出，人工阅读依然清晰）
    for item in items + dishes:
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
    "serving_platter": "block/serving_platter",
    "cutting_board": "block/cutting_board",
    # 机器与部件：结构复杂（还会伸到邻格），一律用 2D 图标 ——
    # 直接拿模型当图标会被 "截断" 成看不出是什么的一角。
    "water_mill": "item/water_mill",
    "water_mill_part": "item/water_mill_part",
    "grain_sheller": "item/grain_sheller",
    "grain_sheller_part": "item/grain_sheller_part",
    "water_wheel": "item/water_wheel",
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
    base = os.path.join(RES, "data", NAMESPACE, "recipe")
    known = ({i["id"] for i in items} | {d["id"] for d in dishes}
             | {"plate", "serving_platter", "cutting_board", "water_mill", "grain_sheller",
                "water_mill_part", "grain_sheller_part", "water_wheel", "placed_dish"})

    written = 0
    for recipe_id, spec in DATA.RECIPES.items():
        if recipe_id not in known:
            raise ValueError("配方 %s 对应的物品不存在" % recipe_id)
        write_json(os.path.join(base, "%s.json" % recipe_id), recipe_object(recipe_id, spec))
        written += 1

    # 其余菜品按"图标种类 -> 容器 + 主料组合"自动展开
    for dish in dishes:
        if dish["id"] in DATA.RECIPES:
            continue
        mapping = DATA.DISH_RECIPE_KIND.get(dish["kind"])
        if mapping is None:
            raise ValueError("菜品 %s 的图标种类 %s 没有配方映射"
                             % (dish["id"], dish["kind"]))
        vessel, material_kind = mapping
        mats = [vessel] + list(DATA.DISH_RECIPE_MATERIALS[material_kind])
        write_json(os.path.join(base, "%s.json" % dish["id"]),
                   recipe_object(dish["id"], ("shapeless", mats, 1)))
        written += 1

    print("recipes: %d" % written)


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
    gen_recipes_table()
    gen_dish_placement(dishes)
    gen_lang(items, dishes)
    gen_item_assets(items, dishes)
    gen_block_item_assets()
    gen_recipes(items, dishes)
    gen_tags(dishes)


if __name__ == "__main__":
    main()
