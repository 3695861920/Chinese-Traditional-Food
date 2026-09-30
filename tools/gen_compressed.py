# -*- coding: utf-8 -*-
"""食材包装方块：把 9 个散装食材打包成"一袋 / 一箱 / 一缸"。

    python tools/gen_compressed.py

参考：农夫乐事的稻米袋 / 卷心菜箱
-------------------------------
那类方块的特点是**一眼看得出里面装的是什么**：

* 麻袋里装着东西、袋口鼓着，颜色跟着内容物走；
* 木箱是**敞口**的，从上面直接看见一根根胡萝卜、一颗颗番茄；
* 本身就是普通方块 —— 能放、能挖、挖了掉自己，**不需要右键取出**，
  想拆就放工作台上拆（反向配方）。

所以这里的取舍是：

1. **模型全部铺满整格**（0~16）。码成一面墙、塞进箱子都整齐，
   格子之间也不会漏缝 —— 这也是那种"仓库存货"的观感。
2. **靠一张"内容物"贴图说清装的是什么**。麻袋是布纹 + 袋口露出的内容物，
   木箱是四面木板 + 顶面铺满的菜 —— 后者直接把内容物贴在箱口那一面上。
3. 全部是实心盒子，不做薄壳中空，不会有透视。

输出
----
* Java：{@code registry/ModCompressed.java}
* 资源：blockstates / models / items / textures / loot_table / recipe
* 语言键由 {@code gen_content.py} 统一写（避免两边抢同一个文件）
"""

import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "chinese_traditional_food")
DATA = os.path.join(ROOT, "src", "main", "resources", "data",
                    "chinese_traditional_food")
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                    "chinese_traditional_food")
NS = "chinese_traditional_food"

# 一个方块里装多少个。农夫乐事也是 9，跟着来。
ITEMS_PER_BLOCK = 9

# ======================================================================
# 清单：(方块 id, 中文名, 英文名, 源物品 id, 包装样式, 配色键, 内容物形态)
# ======================================================================
# 包装样式（决定模型几何）：
#   bag    麻袋 —— 满格鼓腹 + 顶上收口，袋口露内容物
#   sack   布袋 —— 满格矮胖 + 敞口堆着内容物
#   crate  木箱 —— 满格、**四面只到箱子高度**，箱口铺满内容物（最像农夫乐事）
#   jar    陶缸 —— 满格鼓腹 + 收口 + 缸盖
#   brick  压块 —— 满格实心，中间一道模缝
#
# 内容物形态（决定贴图画什么）：
#   grain  颗粒堆（米、面、豆、芝麻…）
#   round  圆的果子（番茄、辣椒、蒜、姜、芋…）
#   leafy  叶球（白菜、竹笋…）
#   lump   块状 / 干货（花生、红枣、木耳…）
#   paste  酱（豆瓣酱、腌菜…）
#   solid  压实的整块
COMPRESSED = [
    # --- 谷物 / 粉类 -> 麻袋 ---
    ("rice_bag",           "米袋",     "Rice Sack",        "rice",           "bag",   "white",  "grain"),
    ("flour_sack",         "面粉袋",   "Flour Sack",       "flour",          "bag",   "white",  "grain"),
    ("rice_flour_sack",    "米粉袋",   "Rice Flour Sack",  "rice_flour",     "bag",   "white",  "grain"),
    ("corn_flour_sack",    "玉米面袋", "Cornmeal Sack",    "corn_flour",     "bag",   "yellow", "grain"),
    ("starch_sack",        "淀粉袋",   "Starch Sack",      "starch",         "bag",   "white",  "grain"),
    ("millet_bag",         "小米袋",   "Millet Sack",      "millet",         "bag",   "gold",   "grain"),
    ("glutinous_bag",      "糯米袋",   "Glutinous Rice Sack", "glutinous_rice", "bag", "cream", "grain"),
    # --- 豆类 -> 布袋 ---
    ("red_bean_sack",      "红豆袋",   "Red Bean Sack",    "red_bean",       "sack",  "red",      "grain"),
    ("mung_bean_sack",     "绿豆袋",   "Mung Bean Sack",   "mung_bean",      "sack",  "mung",     "grain"),
    ("soybean_sack",       "黄豆袋",   "Soybean Sack",     "soybean",        "sack",  "cream",    "grain"),
    ("black_bean_sack",    "黑豆袋",   "Black Bean Sack",  "black_bean",     "sack",  "black",    "grain"),
    ("pea_sack",           "豌豆袋",   "Pea Sack",         "pea",            "sack",  "palegreen", "round"),
    # --- 蔬果 -> 木箱 ---
    ("napa_cabbage_crate", "白菜箱",   "Cabbage Crate",    "napa_cabbage",   "crate", "cabbage",  "leafy"),
    ("radish_crate",       "萝卜箱",   "Radish Crate",     "radish",         "crate", "white",    "round"),
    ("tomato_crate",       "番茄箱",   "Tomato Crate",     "tomato",         "crate", "tomato",   "round"),
    ("chili_crate",        "辣椒箱",   "Chili Crate",      "chili",          "crate", "chili",    "round"),
    ("cucumber_crate",     "黄瓜箱",   "Cucumber Crate",   "cucumber",       "crate", "cucumber", "round"),
    ("eggplant_crate",     "茄子箱",   "Eggplant Crate",   "eggplant",       "crate", "eggplant", "round"),
    ("garlic_crate",       "蒜箱",     "Garlic Crate",     "garlic",         "crate", "white",    "round"),
    ("ginger_crate",       "姜箱",     "Ginger Crate",     "ginger",         "crate", "tan",      "lump"),
    ("sweet_potato_crate", "红薯箱",   "Sweet Potato Crate", "sweet_potato", "crate", "orange",   "lump"),
    ("taro_crate",         "芋头箱",   "Taro Crate",       "taro",           "crate", "purple",   "round"),
    # --- 干货 / 菌 -> 木箱 ---
    ("wood_ear_crate",     "木耳箱",   "Wood Ear Crate",   "wood_ear",       "crate", "woodear",  "lump"),
    ("peanut_crate",       "花生箱",   "Peanut Crate",     "peanut",         "crate", "tan",      "lump"),
    ("red_date_crate",     "红枣箱",   "Red Date Crate",   "red_date",       "crate", "red",      "lump"),
    ("sesame_crate",       "芝麻箱",   "Sesame Crate",     "sesame",         "crate", "white",    "grain"),
    ("bamboo_shoot_crate", "笋箱",     "Bamboo Shoot Crate", "bamboo_shoot", "crate", "bamboo",   "leafy"),
    # --- 调味 / 腌货 -> 陶缸 ---
    ("doubanjiang_jar",    "豆瓣酱缸", "Doubanjiang Jar",  "doubanjiang",       "jar", "paste",   "paste"),
    ("pickled_jar",        "腌菜缸",   "Pickled Vegetable Jar", "pickled_vegetable", "jar", "leaf", "leafy"),
    ("douchi_jar",         "豆豉缸",   "Douchi Jar",       "douchi",            "jar", "black",   "grain"),
    ("sichuan_peppercorn_jar", "花椒缸", "Peppercorn Jar", "sichuan_peppercorn", "jar", "sichuan", "grain"),
    # --- 压块 ---
    ("bean_paste_brick",   "豆沙块",   "Bean Paste Block", "bean_paste",     "brick", "paste", "paste"),
    ("tofu_brick",         "豆腐块",   "Tofu Block",       "tofu",           "brick", "white", "solid"),
    ("rice_bran_brick",    "米糠块",   "Bran Block",       "rice_bran",      "brick", "wheat", "grain"),
]

# 需要"袋口 / 箱口露内容物"的样式：这些方块会多生成一张 <id>_top.png
SHOWS_CONTENTS = ("bag", "sack")


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            fh.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# ======================================================================
# 模型
# ======================================================================
#
# 材质键：
#   #body      包装本身（布纹 / 木板 / 釉面 / 压块）—— 每种方块一张
#   #contents  袋口 / 箱口露出的内容物 —— 每种方块一张（<id>_top.png）
#   #crate     木箱的板条 —— 所有箱子共用
#   #band      捆扎绳 / 箱箍 / 缸沿 —— 所有方块共用

FACES = ("up", "down", "north", "south", "west", "east")


def _faces(texture):
    return {f: {"texture": texture, "uv": [0, 0, 16, 16]} for f in FACES}


def _el(x0, y0, z0, x1, y1, z1, texture, overrides=None):
    """一个实心盒子。``overrides`` 逐面换材质（例如箱口顶面换成内容物）。"""
    f = _faces(texture)
    for key, tex in (overrides or {}).items():
        f[key] = {"texture": tex, "uv": [0, 0, 16, 16]}
    return {"from": [x0, y0, z0], "to": [x1, y1, z1], "faces": f}


def _ring(x0, z0, x1, z1, t, y0, y1, texture, top=None):
    """一圈厚壁（上下通长、左右避开）—— 精确铺满、不重叠。"""
    return [
        _el(x0, y0, z0, x1, y1, z0 + t, texture, {"up": top} if top else None),
        _el(x0, y0, z1 - t, x1, y1, z1, texture, {"up": top} if top else None),
        _el(x0, y0, z0 + t, x0 + t, y1, z1 - t, texture),
        _el(x1 - t, y0, z0 + t, x1, y1, z1 - t, texture),
    ]


def _model(form):
    E = []

    if form == "bag":
        # 麻袋：满格的鼓腹 + 顶上收细的脖子；袋口的顶面露出内容物
        E.append(_el(0.2, 0.0, 0.2, 15.8, 12.8, 15.8, "#body"))
        E.append(_el(3.0, 12.8, 3.0, 13.0, 15.0, 13.0, "#body"))
        E.append(_el(4.4, 15.0, 4.4, 11.6, 15.8, 11.6, "#body",
                     {"up": "#contents"}))
        # 袋口堆出来的一点内容物（让"鼓着"更明显）
        E.append(_el(2.6, 12.6, 2.6, 13.4, 13.8, 13.4, "#contents"))
        # 捆扎绳
        E.append(_el(2.6, 12.8, 2.6, 13.4, 13.6, 13.4, "#band"))

    elif form == "sack":
        # 布袋：更矮胖、口是散开的，内容物堆到袋口之上
        E.append(_el(0.2, 0.0, 0.2, 15.8, 11.6, 15.8, "#body"))
        E.append(_el(1.0, 11.6, 1.0, 15.0, 13.4, 15.0, "#body",
                     {"up": "#contents"}))
        # 袋口上面堆着的一层货
        E.append(_el(1.6, 13.4, 1.6, 14.4, 14.6, 14.4, "#contents"))
        E.append(_el(0.8, 11.4, 0.8, 15.2, 12.4, 15.2, "#band"))

    elif form == "crate":
        # 木箱：**敞口** —— 四面墙只到箱高，箱口铺满内容物。
        # 这是最像农夫乐事菜箱的一种。
        t = 2.2                       # 壁厚
        wall_top = 11.0               # 墙只有这么高
        E.append(_el(0.0, 0.0, 0.0, 16.0, 1.4, 16.0, "#crate"))       # 箱底
        E += _ring(0.0, 0.0, 16.0, 16.0, t, 1.4, wall_top, "#crate")  # 四面墙
        # 四角立柱：比墙面高一点，箱口因此有"骨架"
        for (cx, cz) in ((0.2, 0.2), (14.2, 0.2), (0.2, 14.2), (14.2, 14.2)):
            E.append(_el(cx, 0.0, cz, cx + 1.6, 12.4, cz + 1.6, "#crate"))
        # 箱箍：两道，比墙面略凸
        E += _ring(-0.2, -0.2, 16.2, 16.2, 0.5, 3.6, 4.6, "#band")
        E += _ring(-0.2, -0.2, 16.2, 16.2, 0.5, 8.4, 9.4, "#band")
        # 箱口的内容物：顶面铺满，一直堆到略微高过墙
        E.append(_el(t, 1.4, t, 16.0 - t, 12.6, 16.0 - t, "#contents"))

    elif form == "jar":
        # 陶缸：满格的鼓腹 + 收口 + 缸盖
        E.append(_el(0.0, 0.0, 0.0, 16.0, 3.0, 16.0, "#body"))
        E.append(_el(-0.1, 3.0, -0.1, 16.1, 10.6, 16.1, "#body"))
        E.append(_el(0.4, 10.6, 0.4, 15.6, 13.6, 15.6, "#body"))
        # 缸盖：顶面用内容物（揭盖的状态）—— 让玩家看得见里面
        E.append(_el(0.0, 13.6, 0.0, 16.0, 15.2, 16.0, "#body",
                     {"up": "#contents"}))
        E.append(_el(1.6, 15.2, 1.6, 14.4, 15.8, 14.4, "#band"))

    else:  # brick
        # 压块：满格的压实块，中间一道模缝
        E.append(_el(0.0, 0.0, 0.0, 16.0, 7.4, 16.0, "#body"))
        E.append(_el(0.0, 7.4, 0.0, 16.0, 16.0, 16.0, "#body"))
        E.append(_el(-0.1, 7.0, -0.1, 16.1, 8.0, 16.1, "#band"))

    return E


def build_models():
    for (bid, _zh, _en, _src, form, _pal, _fam) in COMPRESSED:
        # 木箱的四壁用**共用**的木板贴图，所以它不需要自己那张 "body"
        # （箱口的内容物仍然是各自一张 <id>_top.png）。
        textures = {
            # particle（挖掉时的碎屑）也要指向**真实存在**的贴图：
            # 箱子没有自己的底图，就用共用的木板。
            "particle": "%s:block/%s" % (NS, "compressed_crate" if form == "crate" else bid),
            "band": "%s:block/compressed_band" % NS,
        }
        if form == "crate":
            textures["crate"] = "%s:block/compressed_crate" % NS
            textures["contents"] = "%s:block/%s_top" % (NS, bid)
        else:
            textures["body"] = "%s:block/%s" % (NS, bid)
            if form in SHOWS_CONTENTS + ("jar",):
                textures["contents"] = "%s:block/%s_top" % (NS, bid)
            else:
                # 压块不需要单独一张，直接拿主体当内容物
                textures["contents"] = "%s:block/%s" % (NS, bid)

        _write(os.path.join(RES, "models", "block", "%s.json" % bid), {
            "parent": "minecraft:block/block",
            "textures": textures,
            "elements": _model(form),
        })
        # 物品栏直接用方块模型（有立体感）
        _write(os.path.join(RES, "items", "%s.json" % bid), {
            "model": {"type": "minecraft:model",
                      "model": "%s:block/%s" % (NS, bid)}
        })
        _write(os.path.join(RES, "blockstates", "%s.json" % bid),
               {"variants": {"": {"model": "%s:block/%s" % (NS, bid)}}})
        # 战利品：挖下来掉自己
        _write(os.path.join(DATA, "loot_table", "blocks", "%s.json" % bid), {
            "type": "minecraft:block",
            "random_sequence": "%s:blocks/%s" % (NS, bid),
            "pools": [{
                "rolls": 1, "bonus_rolls": 0,
                "entries": [{"type": "minecraft:item",
                             "name": "%s:%s" % (NS, bid)}],
                "conditions": [{"condition": "minecraft:survives_explosion"}],
            }],
        })
    print("compressed models/assets: %d" % len(COMPRESSED))


# ======================================================================
# 配方
# ======================================================================

def build_recipes():
    n = 0
    for (bid, _zh, _en, src, _form, _pal, _fam) in COMPRESSED:
        full = "%s:%s" % (NS, src)
        # 9 个原料 -> 1 个方块（3×3 摆满）
        _write(os.path.join(DATA, "recipe", "%s.json" % bid), {
            "type": "minecraft:crafting_shaped",
            "pattern": ["AAA", "AAA", "AAA"],
            "key": {"A": full},
            "result": {"id": "%s:%s" % (NS, bid), "count": 1},
        })
        # 反向：1 个方块 -> 9 个原料（农夫乐事的稻米袋也是这么拆的）
        _write(os.path.join(DATA, "recipe", "%s_unpack.json" % bid), {
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["%s:%s" % (NS, bid)],
            "result": {"id": full, "count": ITEMS_PER_BLOCK},
        })
        n += 2
    print("compressed recipes: %d" % n)


# ======================================================================
# Java
# ======================================================================

JAVA_HEAD = '''package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.CompressedBlock;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 食材包装方块：把 9 个散装食材打包成"一袋 / 一箱 / 一缸 / 一块"。
 *
 * <p><b>这个文件是生成出来的</b>（{@code tools/gen_compressed.py}），
 * 要加一种包装方块请改那个脚本的 {@code COMPRESSED} 表，别手改这里。</p>
 *
 * <h2>设计参考：农夫乐事的稻米袋 / 卷心菜箱</h2>
 * <ul>
 *   <li>都是<b>满格方块</b>（模型 0~16 铺满），码墙、进箱子都整齐；</li>
 *   <li><b>一眼看得出装的是什么</b>——木箱是敞口的，箱口直接铺着菜；
 *       麻袋的袋口也露出内容物；</li>
 *   <li>行为就是普通方块：能放、能挖、挖了掉自己。
 *       想拆开就放工作台上用反向配方，<b>不需要右键取出</b>。</li>
 * </ul>
 *
 * <p>为什么不给每种写一个类：包装方块的行为完全一致，唯一不同的是贴图，
 * 所以全部复用 {@link CompressedBlock}，用注册 id 区分。</p>
 */
public final class ModCompressed {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    /** 全部包装方块的方块物品，供创造标签页遍历。 */
    private static final List<DeferredItem<? extends Item>> ALL = new ArrayList<>();

'''

JAVA_FOOT = '''
    /** 全部包装方块（方块物品）。 */
    public static List<DeferredItem<? extends Item>> all() {
        return ALL;
    }

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }

    private ModCompressed() {}
}
'''


def _const(name):
    return name.upper()


def build_java():
    parts = [JAVA_HEAD]
    for (bid, zh, _en, _src, form, _pal, _fam) in COMPRESSED:
        parts.append("    /** %s（%s，满格方块）。 */\n" % (zh, form))
        parts.append("    public static final DeferredBlock<CompressedBlock> %s =\n"
                     % _const(bid))
        parts.append("            BLOCKS.registerBlock(\"%s\", CompressedBlock::new,\n" % bid)
        parts.append("                    props -> props.strength(1.2F).sound(SoundType.WOOD));\n")
        parts.append("    public static final DeferredItem<BlockItem> %s_ITEM =\n"
                     % _const(bid))
        parts.append("            ITEMS.registerSimpleBlockItem(\"%s\", %s);\n"
                     % (bid, _const(bid)))
        parts.append("\n")
    parts.append("    static {\n")
    parts.append("        ALL.addAll(List.of(\n")
    entries = ["            %s_ITEM" % _const(bid) for (bid, _z, _e, _s, _f, _p, _m) in COMPRESSED]
    for i in range(0, len(entries), 4):
        chunk = entries[i:i + 4]
        parts.append(",\n".join(chunk) + (",\n" if i + 4 < len(entries) else "\n"))
    parts.append("        ));\n")
    parts.append("    }\n")
    parts.append(JAVA_FOOT)
    _write(os.path.join(JAVA, "registry", "ModCompressed.java"), "".join(parts))
    print("compressed java: ModCompressed.java (%d blocks)" % len(COMPRESSED))


if __name__ == "__main__":
    build_models()
    build_recipes()
    build_java()
