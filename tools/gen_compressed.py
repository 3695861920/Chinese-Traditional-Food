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
    ("doubanjiang_barrel",  "豆瓣酱桶", "Doubanjiang Barrel", "doubanjiang",       "barrel", "paste",   "paste"),
    ("pickled_barrel",      "腌菜桶",   "Pickled Vegetable Barrel", "pickled_vegetable", "barrel", "leaf", "leafy"),
    ("douchi_barrel",       "豆豉桶",   "Douchi Barrel",     "douchi",            "barrel", "black",   "grain"),
    ("sichuan_peppercorn_barrel", "花椒桶", "Peppercorn Barrel", "sichuan_peppercorn", "barrel", "sichuan", "grain"),
    # --- 压块 ---
    ("bean_paste_brick",   "豆沙块",   "Bean Paste Block", "bean_paste",     "brick", "paste", "paste"),
    ("tofu_brick",         "豆腐块",   "Tofu Block",       "tofu",           "brick", "white", "solid"),
    ("rice_bran_brick",    "米糠块",   "Bran Block",       "rice_bran",      "brick", "wheat", "grain"),
]

# ======================================================================
# 自动补齐：剩下那些还没打包的原材料
# ======================================================================
# 农夫乐事的做法是"每种作物一只箱子"，这里也照做：
# 凡是上面没写进 COMPRESSED 的原材料，按下面这张表补一份包装。
#
# 名字与配色**直接取自 content_data 那一行**，不在这儿再抄一遍 ——
# 以后往 content_data 里加一样作物，它自己就会多出一只箱子 / 一只袋子。
#
# 三种样式怎么选（跟农夫乐事一个思路）：
#   sack  散装果菜 —— 小颗的果子、粉料、香料，装袋子里
#   crate 大颗果菜 —— 白菜、冬瓜、萝卜这类，敞口木箱一眼看得见
#   jar   酱料液体 —— 酱油、醋、豆瓣酱，装缸里
#
# 表：(源物品, 包装样式, 内容物形态)
# 形态决定贴图画什么，取值见文件头的说明（grain/round/leafy/lump/paste/solid）。
PACK_THE_REST = [
    # --- 果子 -> 布袋 ---
    ("pear", "sack", "round"), ("peach", "sack", "round"),
    ("plum", "sack", "round"), ("apricot", "sack", "round"),
    ("jujube", "sack", "round"), ("persimmon", "sack", "round"),
    ("mandarin", "sack", "round"), ("pomelo", "sack", "round"),
    ("banana", "sack", "round"), ("grape", "sack", "round"),
    ("strawberry", "sack", "round"), ("cherry", "sack", "round"),
    ("pomegranate", "sack", "round"), ("kiwi", "sack", "round"),
    ("mango", "sack", "round"), ("pineapple", "crate", "round"),
    # --- 叶菜 / 瓜豆 -> 木箱 ---
    ("bok_choy", "crate", "leafy"), ("spinach", "crate", "leafy"),
    ("celery", "crate", "leafy"), ("chive", "crate", "leafy"),
    ("cilantro", "crate", "leafy"), ("scallion", "crate", "leafy"),
    ("garlic_sprout", "crate", "leafy"),
    ("dried_bamboo_shoot", "crate", "leafy"),
    ("winter_melon", "crate", "round"), ("luffa", "crate", "round"),
    ("bitter_melon", "crate", "round"), ("green_bean", "crate", "lump"),
    # --- 五谷杂粮 / 干货 -> 袋 ---
    ("paddy", "sack", "grain"), ("sorghum", "sack", "grain"),
    ("millet_grass", "sack", "leafy"),
    ("glutinous_rice_flour", "sack", "grain"),
    ("broad_bean", "sack", "grain"), ("lotus_seed", "sack", "grain"),
    ("goji_berry", "sack", "round"), ("longan", "sack", "round"),
    ("lychee", "sack", "round"), ("osmanthus", "sack", "grain"),
    ("corn", "crate", "lump"), ("chinese_yam", "crate", "lump"),
    ("dried_jujube", "crate", "lump"),
    # --- 调味料 -> 粉装袋 / 酱装缸 ---
    ("salt", "sack", "grain"), ("rock_sugar", "sack", "grain"),
    ("cumin", "sack", "grain"), ("chili_powder", "sack", "grain"),
    ("pepper_powder", "sack", "grain"), ("five_spice_powder", "sack", "grain"),
    ("star_anise", "sack", "lump"), ("cinnamon_bark", "sack", "lump"),
    ("dried_chili", "sack", "lump"), ("bay_leaf", "sack", "leafy"),
    ("soy_sauce", "barrel", "paste"), ("vinegar", "barrel", "paste"),
    ("cooking_wine", "barrel", "paste"), ("sweet_bean_sauce", "barrel", "paste"),
    ("oyster_sauce", "barrel", "paste"), ("sesame_oil", "barrel", "paste"),
    ("sesame_paste", "barrel", "paste"), ("fermented_tofu", "barrel", "paste"),
    ("chili_oil", "barrel", "paste"), ("stock", "barrel", "paste"),
]

# 样式 -> (id 后缀, 中文后缀, 英文后缀)
#
# 注意 `barrel` 这一档的前身叫 `jar`（陶缸）。用户要求
# "那些桶装材料，大不了设计成颜色不同的木桶来对应不同的材料"，
# 所以贴图、后缀、中英文名全部改成了木桶 —— 不然代码里写着 jar、
# 游戏里却是只木桶，以后没人搞得清。旧文件由 `cleanup_legacy()` 删掉。
FORM_SUFFIX = {
    "bag": ("_bag", "袋", "Sack"),
    "sack": ("_sack", "袋", "Sack"),
    "crate": ("_crate", "箱", "Crate"),
    "barrel": ("_barrel", "桶", "Barrel"),
    "brick": ("_block", "块", "Block"),
}


def _expand_rest():
    """把 PACK_THE_REST 展开成和 COMPRESSED 同样的 7 元组，追加进去。"""
    import content_data as CDATA

    # 物品 id -> (中文名, 英文名, 配色键)
    info = {}
    for row in (CDATA.INGREDIENTS + CDATA.SEEDS + CDATA.SEASONINGS
                + CDATA.FRUITS + CDATA.VEGETABLES):
        info[row[0]] = (row[1], row[2], row[4])

    taken = {row[0] for row in COMPRESSED}
    taken |= {row[3] for row in COMPRESSED}

    for (src, form, family) in PACK_THE_REST:
        if src in taken:
            continue        # 上面已经手工打包过了
        entry = info.get(src)
        if entry is None:
            raise ValueError("PACK_THE_REST 里的 %s 在 content_data 里找不到" % src)
        zh, en, palette = entry
        suffix, zh_suffix, en_suffix = FORM_SUFFIX[form]
        block_id = src + suffix
        if block_id in taken:
            raise ValueError("包装方块 id 撞车：%s" % block_id)
        COMPRESSED.append((block_id, zh + zh_suffix, en + " " + en_suffix,
                           src, form, palette, family))
        taken.add(block_id)


_expand_rest()


# ======================================================================
# 清理上一版的残留
# ======================================================================

# "陶缸"时代用过的**全部** id。
#
# 木桶把 `_jar` 换成了 `_barrel`，旧 id 的文件不删就会变成孤儿
# （`items/*.json` 指一个不存在的模型、顶面贴图没人引用 →
# `validate_content.py` 会报，游戏里还会冒 "Couldn't parse data file"）。
#
# 为什么不按 `FORM_SUFFIX` 反推：手工写进 COMPRESSED 的那 4 只缸
# 用的 id 是 `pickled_jar` 而不是 `<源物品>_jar`（源物品是
# `pickled_vegetable`），反推不出来 —— 第一版就是这样漏掉了 `pickled_jar`，
# 客户端日志里留了一条 "Couldn't parse data file ... blocks/pickled_jar"。
# 所以这里**明写清单**，宁可啰嗦也不要漏。
LEGACY_JAR_IDS = [
    # 手工写在 COMPRESSED 里的 4 只
    "doubanjiang_jar", "pickled_jar", "douchi_jar", "sichuan_peppercorn_jar",
    # PACK_THE_REST 自动展开的 10 只（id = 源物品 + "_jar"）
    "soy_sauce_jar", "vinegar_jar", "cooking_wine_jar", "sweet_bean_sauce_jar",
    "oyster_sauce_jar", "sesame_oil_jar", "sesame_paste_jar",
    "fermented_tofu_jar", "chili_oil_jar", "stock_jar",
]


def cleanup_legacy():
    """删掉 `_jar`（陶缸）时代的全部文件。"""
    targets = []
    for old in LEGACY_JAR_IDS:
        targets += [
            os.path.join(RES, "blockstates", "%s.json" % old),
            os.path.join(RES, "models", "block", "%s.json" % old),
            os.path.join(RES, "items", "%s.json" % old),
            os.path.join(RES, "textures", "block", "%s.png" % old),
            os.path.join(RES, "textures", "block", "%s_top.png" % old),
            os.path.join(DATA, "loot_table", "blocks", "%s.json" % old),
            os.path.join(DATA, "recipe", "%s.json" % old),
            os.path.join(DATA, "recipe", "%s_unpack.json" % old),
        ]
    removed = 0
    for path in targets:
        if os.path.isfile(path):
            os.remove(path)
            removed += 1
    if removed:
        print("compressed legacy cleanup: 删掉 %d 个陶缸时代的残留文件" % removed)
    return removed


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            fh.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# ======================================================================
# 模型
# 模型只用原版那几套 parent，不再需要自己拼 elements；
# 所以旧的 FACES / _faces / _el / _ring 全部删掉（留着就是死代码）。


def _model(form, bid):
    """按包装样式给出方块模型。

    <h3>为什么放弃上一版"一堆 elements 堆出来的造型"</h3>

    用户的要求是两条很具体的话：

    * **"米袋这些做成完整的一整个方块，材质贴近羊毛和布袋"**
    * **"萝卜箱之类的做成类似于原版木桶的形式（直接套用这些材质）"**

    原版木桶（barrel）的模型其实是<b>一句话</b>：

        {"parent": "minecraft:block/cube_bottom_top",
         "textures": {"bottom": ..., "side": ..., "top": ...}}

    上一版为了"立体感"堆了十几个盒子，代价是：共面闪烁、模型庞大、
    顶面贴图被斜面拉伸、码墙时格子间露缝。既然要的是"完整方块 +
    看得见装的是什么"，那就退回原版这套最朴素的写法：

    <table border="1">
      <tr><th>样式</th><th>parent</th><th>说明</th></tr>
      <tr><td>袋（编织袋）</td><td>cube_bottom_top</td>
          <td>侧面 = 经纬交织布 + 顶部一道麻绳，顶面 = 内容物 + 一圈绳</td></tr>
      <tr><td>桶（原来的陶缸）</td><td>cube_bottom_top</td>
          <td>侧面 = 竖桶板 + 两道铁箍（木色按内容物染），顶面 = 铁箍圈 + 内容物</td></tr>
      <tr><td>箱</td><td>cube_bottom_top</td>
          <td>侧面与底面 = <b>原版木桶的贴图</b>，顶面 = 木口 + 铺满的货</td></tr>
      <tr><td>压块</td><td>cube_all</td><td>六面同一张压实贴图</td></tr>
    </table>

    这样"装的是什么"全部由<b>顶面</b>表达，侧视一律干净，
    而且它就是一个完整方块 —— 能当建材码墙、能直接叠。
    """
    if form == "crate":
        # 木桶的形式：桶身与桶底**直接套用原版木桶的材质**
        # （barrel_side 自带那两道箍，barrel_bottom 是桶底的横板）
        return {
            "parent": "minecraft:block/cube_bottom_top",
            "textures": {
                "particle": "minecraft:block/barrel_side",
                "bottom": "minecraft:block/barrel_bottom",
                "side": "minecraft:block/barrel_side",
                "top": "%s:block/%s_top" % (NS, bid),
            },
        }

    if form == "barrel":
        # **木桶**：贴图由我们自己生成（见 texture_compressed._barrel_staves / _barrel_top）。
        #
        # 用户的要求是"那些桶装材料，大不了设计成颜色不同的木桶来对应不同的材料"。
        # 所以桶板颜色跟着内容物走 —— 豆瓣酱的桶偏红、醋的桶偏琥珀、酱油的桶偏黑褐。
        #
        # 为什么不用原版木桶的贴图：那张是固定的橡木色，
        # 34 只缸会一模一样，与"颜色要对应材料"直接冲突。
        # 中间试过的两条“套用原版”的路也都不行：
        #   1. `minecraft:entity/decorated_pot/decorated_pot_side`
        #      —— 陶罐本体那张在 entity/ 下，**不在方块图集里**，
        #      方块模型用不了（日志报 Missing textures）。
        #   2. `minecraft:block/terracotta` —— 那张是原版拿来拼
        #      “带纹陶块”的**图案贴图**，自带斜向色带，单独铺满一个
        #      方块就是一片错乱的花。
        # 所以按"竖桶板 + 两道铁箍"自己画，木色由配色决定。
        return {
            "parent": "minecraft:block/cube_bottom_top",
            "textures": {
                "particle": "%s:block/%s" % (NS, bid),
                "bottom": "%s:block/%s" % (NS, bid),
                "side": "%s:block/%s" % (NS, bid),
                "top": "%s:block/%s_top" % (NS, bid),
            },
        }

    # 袋 / 压块：**一整块布 / 压实的料**，顶面各另外一张。
    return {
        "parent": "minecraft:block/cube_bottom_top",
        "textures": {
            "particle": "%s:block/%s" % (NS, bid),
            "bottom": "%s:block/%s" % (NS, bid),
            "side": "%s:block/%s" % (NS, bid),
            "top": "%s:block/%s_top" % (NS, bid),
        },
    }


def build_models():
    for (bid, _zh, _en, _src, form, _pal, _fam) in COMPRESSED:
        # 模型现在极简（见 _model），贴图键交给它自己拼
        _write(os.path.join(RES, "models", "block", "%s.json" % bid),
               _model(form, bid))
        # 物品栏直接用方块模型（完整方块，六面都对）
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


def main():
    cleanup_legacy()
    build_models()
    build_recipes()
    build_java()


if __name__ == "__main__":
    main()
