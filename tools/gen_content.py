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
                        // 餐具与摆放 / 加工方块
                        output.accept(ModItems.PLATE.get());
                        output.accept(ModItems.SERVING_PLATTER.get());
                        output.accept(ModItems.CUTTING_BOARD.get());
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

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import java.util.List;

/**
 * 案板切割表。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b>
 * 要改配方请编辑 {@code tools/content_data.py} 的 CUTTING 表。</p>
 *
 * <p>输入写法：{@code "chinese_traditional_food:tofu"} 或 {@code "#c:raw_meat"}（标签）。
 * 匹配时<strong>先具体物品、后标签</strong>，所以表的顺序有意义。</p>
 */
public final class ModCutting {
    /** 一条切割规则。
     *
     * @param input      输入（物品 id 或 {@code #命名空间:标签路径}）
     * @param output     产出物品的路径（命名空间固定为本模组）
     * @param needsKnife 是否需要手持刀类工具
     * @param extraTime  额外耗时（tick），0 表示瞬间完成
     */
    public record Entry(String input, String output, boolean needsKnife, int extraTime) {}

    public static final List<Entry> ENTRIES = List.of(
'''

CUTTING_FOOTER = '''    );

    private ModCutting() {}
}
'''


def gen_cutting():
    lines = []
    for (input, output, needs_knife, extra) in DATA.CUTTING:
        lines.append('            new Entry("%s", "%s", %s, %d),'
                     % (input, output, "true" if needs_knife else "false", extra))
    body = CUTTING_HEADER + "\n".join(lines) + "\n" + CUTTING_FOOTER
    write(os.path.join(JAVA, "common", "recipe", "ModCutting.java"), body)
    print("cutting entries: %d" % len(DATA.CUTTING))


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
    })
    en.update({
        "block.chinese_traditional_food.plate": "Plate",
        "block.chinese_traditional_food.serving_platter": "Serving Platter",
        "block.chinese_traditional_food.cutting_board": "Cutting Board",
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
# 配方
# ======================================================================

def ingredient_json(token):
    """把材料写法转成配方 JSON。"""
    if token.startswith("#"):
        return {"tag": token[1:]}
    return {"item": token}


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
             | {"plate", "serving_platter", "cutting_board"})

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
    gen_cutting()
    gen_lang(items, dishes)
    gen_item_assets(items, dishes)
    gen_recipes(items, dishes)
    gen_tags(dishes)


if __name__ == "__main__":
    main()
