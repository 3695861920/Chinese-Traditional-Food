# -*- coding: utf-8 -*-
"""
《国风·传统食物》内容数据表。

这里是**唯一的内容来源**：新增一道菜 / 一种食材，只改这一个文件，
然后运行 `python tools/gen_content.py` 与 `python tools/build_textures.py`，
Java 注册表、语言文件、物品模型、客户端物品、配方、标签、纹理全部自动同步。

字段说明
--------
INGREDIENTS / SEASONINGS / FRUITS / VEGETABLES / TOOLS
    每行 = (id, 中文名, 英文名, 图标种类, 配色名, 饥饿值, 饱和度修饰符)
    饥饿值为 0 表示不可食用（不会挂 food 组件）。

DISHES
    每行 = (id, 中文名, 英文名, 分组, 图标种类, 配色名, 饥饿值, 饱和度修饰符, 效果名)
    分组：lu/chuan/yue/su/min/zhe/xiang/hui（八大菜系）
          spring/lantern/qingming/duanwu/qixi/midautumn/chongyang/laba/winter（节日）

RECIPES
    id -> (类型, 材料, 产出数量)
    类型 "shapeless"：材料是无序列表
    类型 "shaped"   ：材料是 (pattern, key) 二元组
    材料写法：
        "minecraft:bone_meal"                 直接引用具体物品
        "#c:flour"                            引用标签
        "tool:bowl"                           引用本模组物品的简写
"""

# ======================================================================
# 配色
# ======================================================================
# 每种配色给 4 档：(主色, 暗部, 亮部, 点缀色)
PALETTES = {
    # 谷物 / 粉类
    "white":    ((240, 238, 226), (198, 196, 182), (252, 251, 245), (222, 214, 190)),
    "cream":    ((232, 214, 172), (188, 166, 124), (248, 238, 210), (204, 176, 128)),
    "wheat":    ((206, 168, 96), (158, 122, 60), (232, 202, 140), (176, 134, 72)),
    "gold":     ((226, 176, 68), (172, 126, 40), (246, 208, 118), (150, 104, 32)),
    # 豆类
    "red":      ((178, 62, 50), (128, 36, 30), (208, 96, 78), (92, 24, 20)),
    "green":    ((106, 156, 64), (68, 108, 38), (142, 190, 92), (52, 84, 30)),
    "palegreen": ((150, 186, 96), (106, 138, 62), (184, 214, 130), (78, 108, 48)),
    "darkgreen": ((74, 116, 52), (46, 78, 34), (104, 148, 72), (34, 58, 26)),
    "yellow":   ((228, 200, 92), (176, 146, 54), (246, 226, 142), (150, 118, 40)),
    "black":    ((74, 66, 60), (42, 36, 32), (104, 94, 86), (28, 24, 22)),
    # 绿豆专用：现实中的绿豆是发暗的橄榄黄绿，不是草绿 ——
    # 用草绿会看起来像青豆，看不出是绿豆
    "mung":     ((124, 142, 74), (86, 102, 48), (154, 172, 100), (62, 76, 34)),
    # 根茎
    "orange":   ((226, 132, 48), (172, 92, 30), (246, 170, 86), (140, 72, 24)),
    "brown":    ((160, 112, 62), (112, 74, 38), (192, 146, 92), (86, 54, 28)),
    "tan":      ((196, 164, 118), (150, 122, 84), (224, 198, 158), (122, 96, 64)),
    "purple":   ((128, 78, 140), (88, 48, 100), (162, 110, 174), (66, 34, 76)),
    # 叶菜
    "leaf":     ((88, 148, 60), (52, 100, 36), (124, 184, 84), (40, 78, 28)),
    "cabbage":  ((186, 208, 140), (138, 164, 96), (216, 232, 176), (110, 136, 76)),
    "silver":   ((186, 194, 172), (138, 146, 126), (216, 222, 202), (110, 118, 100)),
    # 茄果
    "tomato":   ((198, 62, 44), (146, 36, 26), (228, 96, 72), (108, 24, 18)),
    "chili":    ((186, 46, 38), (134, 26, 22), (216, 78, 62), (98, 18, 16)),
    "eggplant": ((104, 72, 138), (68, 44, 96), (138, 104, 172), (50, 30, 72)),
    # 瓜类：黄瓜深绿、冬瓜青皮带霜、苦瓜青黄
    "cucumber": ((78, 116, 54), (46, 78, 34), (116, 154, 82), (196, 214, 150)),
    "wintermelon": ((118, 144, 108), (80, 106, 76), (168, 190, 156), (234, 240, 228)),
    "bitter":   ((148, 172, 100), (108, 130, 70), (186, 204, 138), (88, 110, 56)),
    # 菌菇 / 干货
    "fungus":   ((104, 76, 60), (68, 46, 36), (138, 106, 86), (48, 30, 24)),
    "woodear":  ((70, 58, 50), (34, 26, 22), (104, 90, 80), (22, 16, 14)),
    "dried":    ((150, 108, 70), (104, 70, 42), (182, 140, 98), (78, 50, 30)),
    # 种子：芥菜类红褐、萝卜类浅褐、葱类深褐
    "seedbr":   ((158, 118, 78), (110, 78, 48), (190, 152, 110), (78, 52, 32)),
    "seedpale": ((200, 178, 132), (154, 132, 90), (228, 210, 172), (122, 100, 62)),
    "seedsb":   ((86, 74, 62), (48, 40, 32), (122, 108, 92), (30, 24, 18)),
    # 液体 / 酱料
    "soy":      ((92, 52, 28), (58, 30, 16), (126, 78, 44), (40, 20, 10)),
    "vinegar":  ((122, 84, 44), (84, 54, 26), (156, 116, 68), (62, 38, 18)),
    "wine":     ((212, 190, 138), (164, 142, 96), (238, 222, 182), (136, 114, 74)),
    "oil":      ((232, 200, 96), (180, 148, 56), (250, 226, 148), (152, 120, 42)),
    "chili_oil": ((176, 62, 30), (126, 34, 16), (212, 96, 54), (92, 22, 12)),
    "paste":    ((128, 52, 34), (86, 30, 20), (162, 78, 54), (64, 20, 14)),
    "sauce":    ((70, 40, 24), (44, 24, 14), (102, 62, 40), (30, 16, 10)),
    # 香料
    "spice":    ((142, 96, 52), (98, 62, 32), (176, 128, 76), (72, 44, 22)),
    "star":     ((122, 78, 44), (84, 50, 26), (156, 108, 68), (62, 34, 18)),
    "sichuan":  ((168, 54, 46), (120, 30, 26), (200, 86, 74), (88, 20, 18)),
    # 器皿 / 工具
    "iron":     ((196, 200, 208), (146, 152, 162), (226, 230, 236), (112, 118, 128)),
    "wood":     ((176, 126, 74), (128, 86, 46), (206, 158, 104), (100, 66, 34)),
    "porcelain": ((232, 236, 242), (188, 194, 204), (250, 252, 255), (62, 94, 158)),
    "bamboo":   ((186, 196, 118), (140, 150, 78), (214, 222, 154), (110, 120, 60)),
    "stone":    ((150, 148, 144), (108, 106, 104), (182, 180, 176), (86, 84, 82)),
    "clay":     ((170, 108, 76), (124, 74, 50), (200, 142, 108), (98, 56, 38)),
    # 菜品专用
    "braised":  ((128, 66, 38), (86, 40, 22), (162, 96, 60), (62, 28, 16)),
    "redbraised": ((156, 58, 32), (110, 34, 18), (192, 92, 58), (78, 22, 12)),
    "steamed":  ((238, 232, 214), (192, 184, 164), (252, 248, 236), (168, 158, 138)),
    "soup":     ((216, 190, 140), (166, 140, 96), (242, 222, 182), (140, 114, 76)),
    "stirfry":  ((176, 138, 78), (128, 96, 50), (208, 174, 114), (98, 70, 36)),
    "greendish": ((118, 158, 74), (78, 112, 46), (154, 192, 106), (58, 86, 34)),
    "pastry":   ((238, 224, 190), (194, 178, 144), (252, 242, 216), (176, 154, 116)),
    "cake":     ((214, 178, 118), (166, 132, 80), (240, 210, 158), (140, 108, 64)),
}

# ======================================================================
# 基础食材
# ======================================================================
INGREDIENTS = [
    # --- 谷物 ---
    ("paddy",                 "稻谷",     "Paddy",              "ear_paddy",   "wheat",  0, 0),
    ("millet_grass",          "谷子",     "Foxtail Millet Grass", "ear_foxtail", "gold", 0, 0),
    ("rice_bran",             "米糠",     "Rice Bran",          "powder", "wheat",    0, 0),
    ("rice",                  "大米",     "Rice",               "grain_rice",  "white",  1, 0.2),
    ("glutinous_rice",        "糯米",     "Glutinous Rice",     "grain_glutinous", "cream", 1, 0.2),
    ("millet",                "小米",     "Millet",             "grain_millet", "gold", 1, 0.2),
    ("sorghum",               "高粱",     "Sorghum",            "ear_sorghum", "red",  1, 0.2),
    ("corn",                  "玉米",     "Corn",               "crop_corn", "yellow",  2, 0.3),
    ("flour",                 "面粉",     "Flour",              "powder", "white",    0, 0),
    ("rice_flour",            "米粉",     "Rice Flour",         "powder", "white",    0, 0),
    ("glutinous_rice_flour",  "糯米粉",   "Glutinous Rice Flour", "powder", "white",  0, 0),
    ("corn_flour",            "玉米面",   "Cornmeal",           "powder", "yellow",   0, 0),
    ("starch",                "淀粉",     "Starch",             "powder", "white",    0, 0),
    # --- 豆类 ---
    ("red_bean",              "红豆",     "Red Bean",           "bean_kidney", "red",    1, 0.1),
    ("mung_bean",             "绿豆",     "Mung Bean",          "bean_mung", "mung",     1, 0.1),
    ("soybean",               "黄豆",     "Soybean",            "bean_round", "cream",  1, 0.1),
    ("black_bean",            "黑豆",     "Black Bean",         "bean_round", "black",  1, 0.1),
    ("pea",                   "豌豆",     "Pea",                "bean_pea", "palegreen", 1, 0.1),
    ("broad_bean",            "蚕豆",     "Broad Bean",         "bean_flat", "palegreen", 1, 0.1),
    ("bean_paste",            "豆沙",     "Red Bean Paste",     "paste_ball", "paste", 2, 0.2),
    ("dou_ya",                "豆芽",     "Bean Sprouts",       "veg_bean_sprout", "white", 1, 0.2),
    # --- 薯类 ---
    ("sweet_potato",          "红薯",     "Sweet Potato",       "veg_sweetpotato",  "orange",   2, 0.3),
    ("baked_sweet_potato",    "烤红薯",   "Baked Sweet Potato", "veg_sweetpotato",  "redbraised", 5, 0.6),
    ("chinese_yam",           "山药",     "Chinese Yam",        "veg_yam",  "tan",      1, 0.2),
    ("taro",                  "芋头",     "Taro",               "veg_taro",  "purple",   2, 0.3),
    # --- 坚果 / 干货 ---
    ("tofu",                  "豆腐",     "Tofu",               "tofu_block", "white",  3, 0.3),
    ("peanut",                "花生",     "Peanut",             "bean_peanut",   "tan",      1, 0.2),
    ("sesame",                "芝麻",     "Sesame",             "crop_sesame",  "white",    1, 0.2),
    ("lotus_seed",            "莲子",     "Lotus Seed",         "crop_lotus_seed",  "cream",    1, 0.2),
    ("goji_berry",            "枸杞",     "Goji Berry",         "berries", "red",     1, 0.2),
    ("red_date",              "红枣",     "Red Date",           "berries", "red",     2, 0.3),
    ("dried_jujube",          "干枣",     "Dried Jujube",       "berries", "dried",   3, 0.4),
    ("longan",                "桂圆",     "Longan",             "berries", "dried",   2, 0.3),
    ("osmanthus",             "桂花",     "Osmanthus",          "flowers", "gold",    0, 0),
    ("lychee",                "荔枝",     "Lychee",             "berries", "red",     4, 0.4),
    # --- 案板切好的半成品 ---
    ("shredded_vegetable",    "蔬菜丝",   "Shredded Vegetables", "shredded", "leaf",   2, 0.3),
    ("shredded_meat",         "肉丝",     "Shredded Meat",       "shredded", "red",    3, 0.4),
    ("fish_fillet",           "鱼片",     "Fish Fillet",         "fillet",   "steamed", 3, 0.4),
    ("shredded_tofu",         "豆腐丝",   "Shredded Tofu",       "shredded", "white",  3, 0.3),
]

# ======================================================================
# 作物种子（可播种；本阶段先作为“留种”物品，种植系统见阶段 5）
# ======================================================================
# 每行同 INGREDIENTS。营养值一律为 0：种子不是食物，
# 所以它们会注册成普通 Item 而不是可摆放的 DishItem。
SEEDS = [
    # --- 谷物 ---
    ("rice_seeds",         "稻种",     "Rice Seeds",         "seed_paddy",  "wheat",    0, 0),
    ("millet_seeds",       "谷种",     "Millet Seeds",       "seed_millet",  "gold",     0, 0),
    ("sorghum_seeds",      "高粱种",   "Sorghum Seeds",      "seed_sorghum",  "red",      0, 0),
    ("corn_seeds",         "玉米种",   "Corn Kernels",       "seed_corn",  "yellow",   0, 0),
    # --- 豆类 ---
    ("soybean_seeds",      "黄豆种",   "Soybean Seeds",      "bean_round",  "cream",    0, 0),
    ("mung_bean_seeds",    "绿豆种",   "Mung Bean Seeds",    "bean_mung",   "mung",     0, 0),
    ("red_bean_seeds",     "红豆种",   "Red Bean Seeds",     "bean_kidney", "red",      0, 0),
    ("pea_seeds",          "豌豆种",   "Pea Seeds",          "bean_pea",    "palegreen", 0, 0),
    ("broad_bean_seeds",   "蚕豆种",   "Broad Bean Seeds",   "bean_flat",   "palegreen", 0, 0),
    ("green_bean_seeds",   "豆角种",   "Green Bean Seeds",   "bean_kidney", "green",    0, 0),
    ("peanut_seeds",       "花生种",   "Peanut Seeds",       "seed_peanut",   "brown",      0, 0),
    ("sesame_seeds",       "芝麻种",   "Sesame Seeds",       "seed_sesame",  "cream",    0, 0),
    # --- 薯类 ---
    ("taro_seeds",         "芋种",     "Taro Corms",         "seed_taro",  "purple",   0, 0),
    ("sweet_potato_slip",  "红薯秧",   "Sweet Potato Slips", "seed_slip", "green",    0, 0),
    ("chinese_yam_slip",   "山药嘴子", "Yam Sets",           "seed_yam",  "tan",      0, 0),
    ("ginger_seeds",       "姜种",     "Ginger Sets",        "seed_ginger", "tan",    0, 0),
    ("garlic_seeds",       "蒜种",     "Garlic Cloves",      "seed_garlic", "white",  0, 0),
    # --- 叶菜 / 茎菜 ---
    ("napa_cabbage_seeds", "白菜种",   "Napa Cabbage Seeds", "seed_brassica",  "seedbr",  0, 0),
    ("bok_choy_seeds",     "小白菜种", "Bok Choy Seeds",     "seed_brassica",  "seedpale", 0, 0),
    ("radish_seeds",       "萝卜种",   "Radish Seeds",       "seed_radish",  "seedpale",    0, 0),
    ("spinach_seeds",      "菠菜种",   "Spinach Seeds",      "seed_prickly",  "seedbr",   0, 0),
    ("celery_seeds",       "芹菜种",   "Celery Seeds",       "seed_umbel",  "seedpale",   0, 0),
    ("cilantro_seeds",     "香菜种",   "Cilantro Seeds",     "seed_umbel",  "seedbr",    0, 0),
    ("chive_seeds",        "韭菜种",   "Chive Seeds",        "seed_allium",  "black",   0, 0),
    ("scallion_seeds",     "葱种",     "Scallion Seeds",     "seed_allium_round",  "seedsb",    0, 0),
    ("chili_seeds",        "辣椒种",   "Chili Seeds",        "seed_capsicum",  "chili",    0, 0),
    ("eggplant_seeds",     "茄子种",   "Eggplant Seeds",     "seed_solanum",  "cream",  0, 0),
    ("tomato_seeds",       "西红柿种", "Tomato Seeds",       "seed_solanum",  "seedpale",  0, 0),
    ("cucumber_seeds",     "黄瓜种",   "Cucumber Seeds",     "seed_cucurbit",  "leaf",     0, 0),
    ("winter_melon_seeds", "冬瓜种",   "Winter Melon Seeds", "seed_cucurbit",  "white",   0, 0),
    ("luffa_seeds",        "丝瓜种",   "Luffa Seeds",        "seed_cucurbit",  "seedsb",   0, 0),
    ("bitter_melon_seeds", "苦瓜种",   "Bitter Melon Seeds", "seed_cucurbit",  "seedbr",  0, 0),
    # --- 菌 ---
    ("wood_ear_spawn",     "木耳菌种", "Wood Ear Spawn",     "seed_spawn",  "fungus",   0, 0),
]

# ======================================================================
# 常见水果
# ======================================================================
FRUITS = [
    ("pear",        "梨",     "Pear",        "fruit_pear",   "palegreen", 4, 0.3),
    ("peach",       "桃",     "Peach",       "fruit_peach",  "orange",    4, 0.3),
    ("plum",        "李子",   "Plum",        "fruit_round",  "purple",    3, 0.3),
    ("apricot",     "杏",     "Apricot",     "fruit_peach",  "gold",      3, 0.3),
    ("jujube",      "枣",     "Jujube",      "berries",      "red",       3, 0.3),
    ("persimmon",   "柿子",   "Persimmon",   "fruit_persimmon", "orange", 4, 0.3),
    ("mandarin",    "橘子",   "Mandarin",    "fruit_citrus", "orange",    4, 0.3),
    ("pomelo",      "柚子",   "Pomelo",      "fruit_citrus", "palegreen", 5, 0.3),
    ("banana",      "香蕉",   "Banana",      "banana",       "yellow",    5, 0.4),
    ("grape",       "葡萄",   "Grape",       "grape",        "purple",    2, 0.3),
    ("strawberry",  "草莓",   "Strawberry",  "strawberry",   "red",       3, 0.4),
    ("cherry",      "樱桃",   "Cherry",      "cherries",     "red",       2, 0.3),
    ("pomegranate", "石榴",   "Pomegranate", "fruit_pomegranate", "red", 4, 0.3),
    ("kiwi",        "猕猴桃", "Kiwi",        "kiwi",         "brown",     3, 0.3),
    ("mango",       "芒果",   "Mango",       "mango",        "gold",      5, 0.4),
    ("pineapple",   "菠萝",   "Pineapple",   "pineapple",    "gold",      5, 0.4),
]

# ======================================================================
# 常见蔬菜
# ======================================================================
VEGETABLES = [
    ("napa_cabbage",     "白菜",     "Napa Cabbage",     "veg_napa",  "cabbage",   2, 0.3),
    ("bok_choy",         "小白菜",   "Bok Choy",         "veg_bokchoy",  "leaf",      2, 0.3),
    ("radish",           "萝卜",     "Radish",           "veg_radish",  "white",     2, 0.3),
    ("spinach",          "菠菜",     "Spinach",          "veg_spinach",  "darkgreen", 2, 0.3),
    ("celery",           "芹菜",     "Celery",           "veg_celery",  "palegreen",      1, 0.2),
    ("chive",            "韭菜",     "Chive",            "veg_chive",  "darkgreen", 1, 0.2),
    ("eggplant",         "茄子",     "Eggplant",         "veg_eggplant", "eggplant", 2, 0.3),
    ("cucumber",         "黄瓜",     "Cucumber",         "veg_cucumber", "cucumber",    2, 0.3),
    ("winter_melon",     "冬瓜",     "Winter Melon",     "veg_wintermelon", "wintermelon", 2, 0.3),
    ("luffa",            "丝瓜",     "Luffa",            "veg_luffa", "palegreen",   2, 0.3),
    ("bitter_melon",     "苦瓜",     "Bitter Melon",     "veg_bitter", "bitter", 2, 0.2),
    ("green_bean",       "豆角",     "Green Bean",       "veg_greenbean",    "green",     1, 0.2),
    ("tomato",           "西红柿",   "Tomato",           "veg_tomato",  "tomato",  3, 0.4),
    ("chili",            "辣椒",     "Chili Pepper",     "veg_chili",   "chili",   2, 0.3),
    ("scallion",         "葱",       "Scallion",         "veg_scallion",   "leaf",      1, 0.2),
    ("ginger",           "姜",       "Ginger",           "veg_ginger", "tan",       1, 0.2),
    ("garlic",           "蒜",       "Garlic",           "veg_garlic", "white",     1, 0.2),
    ("garlic_sprout",    "蒜苗",     "Garlic Sprout",    "veg_garlic_sprout", "palegreen",      1, 0.2),
    ("cilantro",         "香菜",     "Cilantro",         "veg_cilantro",  "leaf",      1, 0.2),
    ("wood_ear",         "木耳",     "Wood Ear",         "veg_woodear", "woodear",    2, 0.2),
    ("bamboo_shoot",     "笋",       "Bamboo Shoot",     "veg_shoot",  "bamboo",    2, 0.3),
    ("dried_bamboo_shoot", "笋干",   "Dried Bamboo Shoot", "veg_shoot_dried", "dried",    2, 0.3),
    ("pickled_vegetable", "腌菜",    "Pickled Vegetable", "veg_pickle",   "leaf",      2, 0.3),
]

# ======================================================================
# 调味料
# ======================================================================
SEASONINGS = [
    ("salt",                "盐",       "Salt",                "powder", "white",    0, 0),
    ("rock_sugar",          "冰糖",     "Rock Sugar",          "crystal", "white",   1, 0.1),
    ("soy_sauce",           "酱油",     "Soy Sauce",           "bottle", "soy",      0, 0),
    ("vinegar",             "醋",       "Vinegar",             "bottle", "vinegar",  0, 0),
    ("cooking_wine",        "料酒",     "Cooking Wine",        "bottle", "wine",     0, 0),
    ("sichuan_peppercorn",  "花椒",     "Sichuan Peppercorn",  "sachet", "sichuan",  0, 0),
    ("star_anise",          "八角",     "Star Anise",          "star",   "star",     0, 0),
    ("cinnamon_bark",       "桂皮",     "Cinnamon Bark",       "bark",   "brown",    0, 0),
    ("bay_leaf",            "香叶",     "Bay Leaf",            "leaf_flat", "leaf",   0, 0),
    ("cumin",               "孜然",     "Cumin",               "seeds",  "spice",    0, 0),
    ("chili_powder",        "辣椒粉",   "Chili Powder",        "powder", "chili",    0, 0),
    ("pepper_powder",       "胡椒粉",   "Pepper Powder",       "powder", "black",    0, 0),
    ("five_spice_powder",   "五香粉",   "Five Spice Powder",   "powder", "spice",    0, 0),
    ("dried_chili",         "干辣椒",   "Dried Chili",         "dried_chili", "chili", 0, 0),
    ("doubanjiang",         "豆瓣酱",   "Doubanjiang",         "jar",    "paste",    0, 0),
    ("sweet_bean_sauce",    "甜面酱",   "Sweet Bean Sauce",    "jar",    "sauce",    0, 0),
    ("oyster_sauce",        "蚝油",     "Oyster Sauce",        "bottle", "sauce",    0, 0),
    ("sesame_oil",          "香油",     "Sesame Oil",          "bottle", "oil",      0, 0),
    ("sesame_paste",        "芝麻酱",   "Sesame Paste",        "jar",    "tan",      0, 0),
    ("fermented_tofu",      "腐乳",     "Fermented Tofu",      "jar",    "chili",    1, 0.2),
    ("douchi",              "豆豉",     "Fermented Black Bean", "jar",   "black",    1, 0.1),
    ("chili_oil",           "辣椒油",   "Chili Oil",           "bottle", "chili_oil", 0, 0),
    ("stock",               "高汤",     "Stock",               "jar",    "soup",     1, 0.2),
]

# ======================================================================
# 厨具与餐具（物品）
# ======================================================================
TOOLS = [
    ("kitchen_knife", "菜刀",   "Kitchen Knife", "tool_knife",     "iron",  250),
    ("cleaver",       "砍刀",   "Cleaver",       "tool_cleaver",   "iron",  400),
    ("spatula",       "铲子",   "Spatula",       "tool_spatula",   "iron",  250),
    ("slotted_spoon", "漏勺",   "Slotted Spoon", "tool_slotted",   "iron",  200),
    ("soup_spoon",    "汤勺",   "Soup Spoon",    "tool_spoon",     "iron",  200),
    ("rolling_pin",   "擀面杖", "Rolling Pin",   "tool_rolling",   "wood",  150),
    ("chopsticks",    "筷子",   "Chopsticks",    "tool_chopsticks","wood",  0),
    ("saucer",        "碟子",   "Saucer",        "table_saucer",   "porcelain", 0),
    ("cup",           "杯子",   "Cup",           "table_cup",      "porcelain", 0),
]

# 玻璃 / 黏土类的非本模组材料
VANILLA = {
    "stick": "minecraft:stick",
    "iron_ingot": "minecraft:iron_ingot",
    "clay_ball": "minecraft:clay_ball",
    "glass": "minecraft:glass",
    "planks": "#minecraft:planks",
    "bowl": "minecraft:bowl",
    "water_bucket": "minecraft:water_bucket",
    "milk_bucket": "minecraft:milk_bucket",
    "bone_meal": "minecraft:bone_meal",
    "sugar": "minecraft:sugar",
    "blaze_powder": "minecraft:blaze_powder",
    "egg": "minecraft:egg",
    "wheat": "minecraft:wheat",
    "potato": "minecraft:potato",
    "carrot": "minecraft:carrot",
    "beef": "minecraft:beef",
    "porkchop": "minecraft:porkchop",
    "chicken": "minecraft:chicken",
    "mutton": "minecraft:mutton",
    "rabbit": "minecraft:rabbit",
    "cod": "minecraft:cod",
    "salmon": "minecraft:salmon",
    "kelp": "minecraft:kelp",
    "dried_kelp": "minecraft:dried_kelp",
    "mushroom": "minecraft:brown_mushroom",
    "honey_bottle": "minecraft:honey_bottle",
    "sweet_berries": "minecraft:sweet_berries",
    "cocoa_beans": "minecraft:cocoa_beans",
    "ink_sac": "minecraft:ink_sac",
    "rice_vanilla": "minecraft:wheat",
}

# ======================================================================
# 八大菜系 + 传统节日
# ======================================================================
# 效果名 -> 见 common/food/DishEffects.java
DISHES = [
    # ---------------- 鲁菜 ----------------
    ("jiuzhuan_dachang", "九转大肠",   "Braised Pork Intestines", "lu", "braised",    "redbraised", 8, 1.0, "NOURISH"),
    ("congsao_haishen",  "葱烧海参",   "Braised Sea Cucumber",    "lu", "braised",    "braised",    7, 1.2, "NOURISH"),
    ("tangcu_liyu",      "糖醋鲤鱼",   "Sweet and Sour Carp",     "lu", "dish_plate", "redbraised", 8, 1.0, "SATED"),
    ("youbao_shuangcui", "油爆双脆",   "Stir-fried Giblets",      "lu", "dish_plate", "stirfry",    7, 0.9, "CRISP"),
    ("guota_doufu",      "锅塌豆腐",   "Pan-fried Tofu",          "lu", "dish_plate", "steamed",    6, 0.8, "NONE"),
    ("naitang_pucai",    "奶汤蒲菜",   "Milk Soup with Cattail",  "lu", "dish_soup",  "soup",       5, 1.0, "WARMTH"),
    ("dezhou_paji",      "德州扒鸡",   "Dezhou Braised Chicken",  "lu", "dish_whole", "braised",    9, 1.0, "NOURISH"),
    ("sixi_wanzi",       "四喜丸子",   "Four Joy Meatballs",      "lu", "meatball",   "braised",    8, 1.1, "SATED"),
    ("zaoliu_yupian",    "糟溜鱼片",   "Fish Slices in Wine Sauce", "lu", "dish_plate", "steamed",  7, 0.9, "REFRESH"),
    ("kongfu_yipinguo",  "孔府一品锅", "Kong Family Pot",         "lu", "dish_pot",   "braised",   10, 1.2, "NOURISH_WARMTH"),

    # ---------------- 川菜 ----------------
    ("mapo_tofu",        "麻婆豆腐",   "Mapo Tofu",               "chuan", "mapo",     "chili_oil",  7, 1.0, "REFRESH"),
    ("huiguo_rou",       "回锅肉",     "Twice-cooked Pork",       "chuan", "dish_plate", "redbraised", 9, 1.1, "SATED"),
    ("shuizhu_yu",       "水煮鱼",     "Boiled Fish in Chili Oil", "chuan", "dish_soup", "chili_oil", 8, 1.0, "REFRESH"),
    ("fuqi_feipian",     "夫妻肺片",   "Sliced Beef in Chili Sauce", "chuan", "dish_plate", "chili_oil", 6, 0.9, "REFRESH"),
    ("gongbao_jiding",   "宫保鸡丁",   "Kung Pao Chicken",        "chuan", "dish_plate", "redbraised", 8, 1.1, "REFRESH"),
    ("yuxiang_rousi",    "鱼香肉丝",   "Yuxiang Shredded Pork",   "chuan", "dish_plate", "redbraised", 8, 1.0, "NONE"),
    ("maoxue_wang",      "毛血旺",     "Mao Xue Wang",            "chuan", "dish_pot",   "chili_oil",  9, 1.0, "REFRESH_NOURISH"),
    ("laziji",           "辣子鸡",     "Spicy Chicken",           "chuan", "dish_plate", "chili",      8, 0.9, "REFRESH"),
    ("dongpo_zhouzi",    "东坡肘子",   "Dongpo Pork Hock",        "chuan", "dish_whole", "redbraised", 10, 1.2, "NOURISH_SATED"),
    ("kaishui_baicai",   "开水白菜",   "Cabbage in Clear Broth",  "chuan", "dish_soup",  "steamed",    4, 1.4, "NOURISH"),

    # ---------------- 粤菜 ----------------
    ("baiqie_ji",        "白切鸡",     "Poached Chicken",         "yue", "dish_whole",  "steamed",    8, 1.0, "NOURISH"),
    ("mizhi_chashao",    "蜜汁叉烧",   "Honey Char Siu",          "yue", "dish_plate",  "redbraised", 9, 1.1, "SATED"),
    ("qingzheng_shibanyu", "清蒸石斑鱼", "Steamed Grouper",       "yue", "dish_fish",   "steamed",    7, 1.2, "NOURISH"),
    ("laohuo_liangtang", "老火靓汤",   "Slow-simmered Soup",      "yue", "dish_soup",   "soup",       6, 1.4, "NOURISH_WARMTH"),
    ("shaoe",            "烧鹅",       "Roast Goose",             "yue", "dish_whole",  "redbraised", 9, 1.1, "SATED"),
    ("xiajiao_huang",    "虾饺皇",     "Shrimp Dumplings",        "yue", "dumpling",    "steamed",    5, 1.2, "REFRESH"),
    ("ganchao_niuhe",    "干炒牛河",   "Beef Chow Fun",           "yue", "dish_plate",  "stirfry",    9, 1.0, "SATED"),
    ("baozhi_liaoshen",  "鲍汁扣辽参", "Abalone Sauce Sea Cucumber", "yue", "dish_plate", "braised",  7, 1.3, "NOURISH"),
    ("zeze_bao",         "啫啫煲",     "Sizzling Clay Pot",       "yue", "dish_pot",    "braised",    8, 1.0, "WARMTH"),
    ("yuntun_mian",      "云吞面",     "Wonton Noodles",          "yue", "noodles",     "soup",       8, 1.1, "SATED"),

    # ---------------- 苏菜 ----------------
    ("songshu_guiyu",    "松鼠鳜鱼",   "Squirrel Mandarin Fish",  "su", "dish_fish",    "redbraised", 8, 1.1, "REFRESH"),
    ("dazhaxie",         "阳澄湖大闸蟹", "Hairy Crab",            "su", "crab",         "chili",      7, 1.2, "NOURISH"),
    ("yangzhou_shizitou","扬州狮子头", "Yangzhou Lion's Head",    "su", "meatball",     "braised",    9, 1.1, "NOURISH"),
    ("jinling_yanshuiya","金陵盐水鸭", "Nanjing Salted Duck",     "su", "dish_whole",   "steamed",    8, 1.0, "NOURISH"),
    ("dazhu_gansi",      "大煮干丝",   "Braised Shredded Tofu",   "su", "dish_soup",    "steamed",    5, 1.0, "NOURISH"),
    ("wuxi_jiangpaigu",  "无锡酱排骨", "Wuxi Braised Ribs",       "su", "dish_plate",   "redbraised", 9, 1.1, "SATED"),
    ("qingzheng_shiyu",  "清蒸鲥鱼",   "Steamed Hilsa Herring",   "su", "dish_fish",    "steamed",    7, 1.2, "NOURISH"),
    ("shuijing_yaorou",  "水晶肴肉",   "Crystal Pork Terrine",    "su", "dish_plate",   "steamed",    6, 0.9, "CRISP"),
    ("biluo_xiaren",     "碧螺虾仁",   "Biluoshun Shrimp",        "su", "dish_plate",   "greendish",  6, 1.1, "REFRESH"),
    ("wensi_doufu",      "文思豆腐",   "Wensi Tofu Soup",         "su", "dish_soup",    "steamed",    5, 1.3, "NOURISH"),

    # ---------------- 闽菜 ----------------
    ("fotiaoqiang",      "佛跳墙",     "Buddha Jumps Over the Wall", "min", "dish_pot", "braised", 10, 1.4, "FEAST"),
    ("lizhi_rou",        "荔枝肉",     "Lychee Pork",             "min", "meatball",     "redbraised", 8, 1.0, "CRISP"),
    ("zui_paigu",        "醉排骨",     "Drunken Ribs",            "min", "dish_plate",   "redbraised", 8, 1.0, "REFRESH"),
    ("babao_hongxun_fan","八宝红鲟饭", "Eight Treasure Crab Rice", "min", "rice_dish",   "orange",     9, 1.2, "NOURISH"),
    ("jitang_tun_haibang","鸡汤氽海蚌","Clam in Chicken Broth",   "min", "dish_soup",    "soup",       7, 1.3, "NOURISH"),
    ("zhan_hetianji",    "斩河田鸡",   "Hetian Chicken",          "min", "dish_whole",   "steamed",    8, 1.0, "NOURISH"),
    ("wuyi_xune",        "武夷熏鹅",   "Wuyi Smoked Goose",       "min", "dish_whole",   "dried",      9, 1.0, "SATED"),
    ("xiangnan_ribao",   "香南日鲍",   "Braised Nanri Abalone",   "min", "dish_plate",   "braised",    7, 1.3, "NOURISH"),

    # ---------------- 浙菜 ----------------
    ("xihu_cuyu",        "西湖醋鱼",   "West Lake Vinegar Fish",  "zhe", "dish_fish",   "redbraised", 8, 1.0, "REFRESH"),
    ("dongpo_rou",       "东坡肉",     "Dongpo Pork",             "zhe", "braised_block", "redbraised", 9, 1.2, "NOURISH_SATED"),
    ("longjing_xiaren",  "龙井虾仁",   "Longjing Shrimp",         "zhe", "dish_plate",  "greendish",  6, 1.1, "REFRESH"),
    ("xuecai_huangyu",   "雪菜大汤黄鱼","Yellow Croaker Soup",    "zhe", "dish_soup",   "soup",       7, 1.1, "NOURISH"),
    ("qingtang_yueji",   "清汤越鸡",   "Clear Broth Chicken",     "zhe", "dish_soup",   "steamed",    7, 1.3, "NOURISH"),
    ("gancai_menrou",    "干菜焖肉",   "Braised Pork with Greens","zhe", "dish_plate",  "braised",    9, 1.1, "SATED"),
    ("wuwei_jianxie",    "五味煎蟹",   "Five-flavour Crab",       "zhe", "crab",        "chili",      7, 1.1, "REFRESH"),

    # ---------------- 湘菜 ----------------
    ("duojiao_yutou",    "剁椒鱼头",   "Fish Head with Chopped Chili", "xiang", "dish_fish", "chili", 8, 1.1, "REFRESH"),
    ("maoshi_hongshaorou","毛氏红烧肉","Mao's Braised Pork",        "xiang", "braised_block", "redbraised", 9, 1.2, "NOURISH_SATED"),
    ("lajiao_chaorou",   "辣椒炒肉",   "Pork with Green Chili",   "xiang", "dish_plate",  "chili",      8, 1.0, "REFRESH"),
    ("dongan_ziji",      "东安子鸡",   "Dongan Chicken",          "xiang", "dish_whole",  "chili",      8, 1.0, "REFRESH"),
    ("lawei_hezheng",    "腊味合蒸",   "Steamed Cured Meats",     "xiang", "steamed_plate", "dried",    9, 1.1, "SATED"),
    ("xiangxi_waipocai", "湘西外婆菜", "Grandma's Pickles",       "xiang", "dish_plate",  "darkgreen",  6, 0.9, "CRISP"),
    ("jiangbanya",       "酱板鸭",     "Soy-braised Duck",        "xiang", "dish_whole",  "dried",      8, 1.0, "REFRESH"),
    ("yongzhou_xueya",   "永州血鸭",   "Yongzhou Blood Duck",     "xiang", "dish_plate",  "chili_oil",  9, 1.1, "NOURISH"),
    ("zuan_yuchi",       "组庵鱼翅",   "Zuan Shark Fin",          "xiang", "dish_soup",   "braised",    7, 1.4, "NOURISH"),
    ("zhuxue_wanzi",     "猪血丸子",   "Pig Blood Meatball",      "xiang", "meatball",    "dried",      7, 0.9, "SATED"),

    # ---------------- 徽菜 ----------------
    ("chou_guiyu",       "臭鳜鱼",     "Stinky Mandarin Fish",    "hui", "dish_fish",   "braised",    8, 1.1, "REFRESH"),
    ("huizhou_yipinguo", "徽州一品锅", "Huizhou One-pot",          "hui", "dish_pot",    "braised",   10, 1.3, "NOURISH_WARMTH"),
    ("humao_doufu",      "虎皮毛豆腐", "Hairy Tofu",              "hui", "dish_plate",  "stirfry",    6, 1.0, "CRISP"),
    ("huangshan_dunge",  "黄山炖鸽",   "Huangshan Pigeon Stew",   "hui", "dish_pot",    "braised",    7, 1.3, "NOURISH"),
    ("wenzheng_shansun", "问政山笋",   "Wenzheng Bamboo Shoots",  "hui", "dish_soup",   "greendish",  5, 1.1, "CRISP"),
    ("fangla_yu",        "方腊鱼",     "Fangla Fish",             "hui", "dish_fish",   "redbraised", 8, 1.0, "REFRESH"),
    ("mizhi_hongyu",     "蜜汁红芋",   "Honeyed Sweet Potato",    "hui", "steamed_plate", "orange",   6, 1.0, "SATED"),
    ("qingzheng_shiji",  "清蒸石鸡",   "Steamed Stone Frog",      "hui", "dish_plate",  "steamed",    7, 1.2, "NOURISH"),

    # ---------------- 春节 ----------------
    ("jiaozi",           "饺子",       "Dumplings",               "spring", "dumpling",   "pastry",   6, 0.9, "REUNION"),
    ("nian_gao",         "年糕",       "Nian Gao",                "spring", "cake_slice", "pastry",   6, 0.8, "RISE_UP"),
    ("chun_juan",        "春卷",       "Spring Rolls",            "spring", "spring_roll", "gold",    5, 0.8, "NONE"),
    ("tang_yuan",        "汤圆",       "Tangyuan",                "spring", "balls_bowl",  "white",    5, 0.8, "REUNION"),
    ("la_rou",           "腊肉",       "Cured Pork",              "spring", "cured_meat", "dried",    7, 0.9, "SATED"),

    # ---------------- 元宵 ----------------
    ("zhima_tangyuan",   "芝麻汤圆",   "Sesame Tangyuan",         "lantern", "balls_bowl", "white",   6, 0.9, "REUNION"),
    ("dousha_tangyuan",  "豆沙汤圆",   "Red Bean Tangyuan",       "lantern", "balls_bowl", "cream",   6, 0.9, "REUNION"),
    ("huasheng_tangyuan","花生汤圆",   "Peanut Tangyuan",         "lantern", "balls_bowl", "tan",     6, 0.9, "REUNION_SATED"),

    # ---------------- 清明 ----------------
    ("qing_tuan",        "青团",       "Qingtuan",                "qingming", "balls_bowl", "darkgreen", 5, 0.8, "CRISP"),
    ("ai_jiao",          "艾饺",       "Mugwort Dumplings",       "qingming", "dumpling",  "darkgreen", 5, 0.8, "CRISP"),

    # ---------------- 端午 ----------------
    ("rou_zong",         "肉粽",       "Meat Zongzi",             "duanwu", "zongzi",  "darkgreen", 8, 1.0, "SATED"),
    ("zao_zong",         "枣粽",       "Date Zongzi",             "duanwu", "zongzi",  "darkgreen", 7, 0.9, "REUNION"),
    ("dousha_zong",      "豆沙粽",     "Red Bean Zongzi",         "duanwu", "zongzi",  "darkgreen", 7, 0.9, "REUNION"),

    # ---------------- 七夕 ----------------
    ("qiao_guo",         "巧果",       "Qiaoguo",                 "qixi", "cookie",      "pastry",   4, 0.7, "NONE"),
    ("qiaoya_mian",      "巧芽面",     "Sprout Noodles",          "qixi", "noodles",     "soup",     7, 0.9, "REFRESH"),

    # ---------------- 中秋 ----------------
    ("lianrong_yuebing", "莲蓉月饼",   "Lotus Paste Mooncake",    "midautumn", "mooncake", "cake",   7, 1.1, "PERFECTION"),
    ("dousha_yuebing",   "豆沙月饼",   "Red Bean Mooncake",       "midautumn", "mooncake", "cake",   7, 1.0, "PERFECTION"),
    ("wuren_yuebing",    "五仁月饼",   "Five Kernel Mooncake",    "midautumn", "mooncake", "cake",   8, 1.1, "PERFECTION_NOURISH"),
    ("danyue_yuebing",   "蛋黄月饼",   "Salted Yolk Mooncake",    "midautumn", "mooncake", "cake",   8, 1.1, "PERFECTION_SATED"),

    # ---------------- 重阳 ----------------
    ("chongyang_gao",    "重阳糕",     "Chongyang Cake",          "chongyang", "cake_slice", "cake",  6, 0.9, "RISE_UP"),
    ("juhua_jiu",        "菊花酒",     "Chrysanthemum Wine",      "chongyang", "wine_cup",   "wine",  0, 0,   "WARMTH_REFRESH"),

    # ---------------- 腊八 ----------------
    ("laba_zhou",        "腊八粥",     "Laba Porridge",           "laba", "congee",  "soup",    7, 1.2, "NOURISH_WARMTH"),
    ("laba_suan",        "腊八蒜",     "Laba Garlic",             "laba", "garlic",  "palegreen", 2, 0.4, "NONE"),

    # ---------------- 冬至 ----------------
    ("yangrou_tang",     "羊肉汤",     "Mutton Soup",             "winter", "dish_soup", "soup", 8, 1.3, "WARMTH_NOURISH"),
]

# ======================================================================
# 配方
# ======================================================================
# id -> (类型, 材料, 数量)
#   "shapeless": 材料是无序列表
#   "shaped"   : 材料是 {"pattern": [...], "key": {...}}
#   "smelting" : 材料是单个输入，走熔炉
#
# 注意：“水磨 / 脱壳机”专用的配方会在后续阶段以 mill / sheller 类型接入；
# 本批次先用工作台 + 熔炉配方，保证进游戏不报未知配方类型。
RECIPES = {
    # ---------------- 基础加工 ----------------
    "tofu": ("shapeless", ["minecraft:milk_bucket", "minecraft:bone_meal"], 2),
    "flour": ("shapeless", ["minecraft:wheat"], 2),
    "rice": ("shapeless", ["chinese_traditional_food:paddy"], 1),
    "rice_flour": ("shapeless", ["chinese_traditional_food:rice"], 2),
    "glutinous_rice_flour": ("shapeless", ["chinese_traditional_food:glutinous_rice"], 2),
    "corn_flour": ("shapeless", ["chinese_traditional_food:corn"], 2),
    "starch": ("shapeless", ["minecraft:potato"], 2),
    "bean_paste": ("shapeless", ["chinese_traditional_food:red_bean", "chinese_traditional_food:red_bean", "minecraft:sugar"], 2),
    "dou_ya": ("shapeless", ["chinese_traditional_food:soybean", "minecraft:water_bucket"], 3),
    "baked_sweet_potato": ("smelting", ["chinese_traditional_food:sweet_potato"], 1),
    "dried_jujube": ("smelting", ["chinese_traditional_food:red_date"], 1),
    "dried_bamboo_shoot": ("smelting", ["chinese_traditional_food:bamboo_shoot"], 1),
    "pickled_vegetable": ("shapeless", ["chinese_traditional_food:napa_cabbage", "chinese_traditional_food:salt", "chinese_traditional_food:salt"], 2),
    # 稻谷：暂时用小麦代替"未脱壳的谷物"（后续做作物种植时改为草丛掉落）
    "paddy": ("shapeless", ["minecraft:wheat", "minecraft:wheat"], 2),
    # 谷子同理；米糠现在只能靠脱壳机副产，合成上先不解

    # ---------------- 留种：作物 -> 种子 ----------------
    # 现实里种子就是从成熟作物里留出来的。这里每一行都是"拿一份作物留种"，
    # 等阶段 5 的种植系统上线后，种子另会有"下地播种"的用法。
    "rice_seeds": ("shapeless", ["chinese_traditional_food:paddy"], 2),
    "millet_seeds": ("shapeless", ["chinese_traditional_food:millet_grass"], 2),
    "sorghum_seeds": ("shapeless", ["chinese_traditional_food:sorghum"], 2),
    "corn_seeds": ("shapeless", ["chinese_traditional_food:corn"], 2),
    "soybean_seeds": ("shapeless", ["chinese_traditional_food:soybean"], 2),
    "mung_bean_seeds": ("shapeless", ["chinese_traditional_food:mung_bean"], 2),
    "red_bean_seeds": ("shapeless", ["chinese_traditional_food:red_bean"], 2),
    "peanut_seeds": ("shapeless", ["chinese_traditional_food:peanut"], 2),
    "sesame_seeds": ("shapeless", ["chinese_traditional_food:sesame"], 2),
    "taro_seeds": ("shapeless", ["chinese_traditional_food:taro"], 2),
    "sweet_potato_slip": ("shapeless", ["chinese_traditional_food:sweet_potato"], 2),
    "napa_cabbage_seeds": ("shapeless", ["chinese_traditional_food:napa_cabbage"], 2),
    "radish_seeds": ("shapeless", ["chinese_traditional_food:radish"], 2),
    "chili_seeds": ("shapeless", ["chinese_traditional_food:chili"], 2),
    "cucumber_seeds": ("shapeless", ["chinese_traditional_food:cucumber"], 2),

    # ---------------- 电力设备（单方块） ----------------
    # 熔炉发电机：石头外壳 + 铁芯 + 熔炉
    "furnace_generator": ("shaped", {"pattern": ["III", "IFI", "SSS"],
                                      "key": {"I": "minecraft:iron_ingot",
                                              "F": "minecraft:furnace",
                                              "S": "minecraft:stone"}}, 1),
    # 电动磨粉机：铁外壳 + 磨盘
    "electric_mill": ("shaped", {"pattern": ["III", "ISI", "III"],
                                  "key": {"I": "minecraft:iron_ingot",
                                          "S": "minecraft:stone_bricks"}}, 1),
    # 电动脱壳机：铁外壳 + 铁滚筒
    "electric_sheller": ("shaped", {"pattern": ["III", "ICI", "III"],
                                     "key": {"I": "minecraft:iron_ingot",
                                             "C": "minecraft:cauldron"}}, 1),

    # ---------------- 调味料 ----------------
    "salt": ("smelting", ["minecraft:dried_kelp"], 1),
    "rock_sugar": ("shapeless", ["minecraft:sugar", "minecraft:sugar"], 1),
    "soy_sauce": ("shapeless", ["chinese_traditional_food:soybean", "chinese_traditional_food:salt", "minecraft:wheat"], 1),
    "vinegar": ("shapeless", ["chinese_traditional_food:rice", "minecraft:sugar"], 1),
    "cooking_wine": ("shapeless", ["chinese_traditional_food:rice", "chinese_traditional_food:rice", "minecraft:sugar"], 1),
    "five_spice_powder": ("shapeless", ["chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark",
                                        "chinese_traditional_food:sichuan_peppercorn", "chinese_traditional_food:bay_leaf",
                                        "chinese_traditional_food:cumin"], 1),
    "chili_powder": ("shapeless", ["chinese_traditional_food:dried_chili"], 2),
    "pepper_powder": ("shapeless", ["chinese_traditional_food:sichuan_peppercorn"], 2),
    "dried_chili": ("smelting", ["chinese_traditional_food:chili"], 1),
    "doubanjiang": ("shapeless", ["chinese_traditional_food:broad_bean", "chinese_traditional_food:chili",
                                  "chinese_traditional_food:salt"], 1),
    "sweet_bean_sauce": ("shapeless", ["chinese_traditional_food:flour", "chinese_traditional_food:salt"], 1),
    "oyster_sauce": ("shapeless", ["minecraft:kelp", "chinese_traditional_food:salt", "minecraft:dried_kelp"], 1),
    "sesame_oil": ("shapeless", ["chinese_traditional_food:sesame"], 1),
    "sesame_paste": ("shapeless", ["chinese_traditional_food:sesame", "chinese_traditional_food:sesame"], 1),
    "fermented_tofu": ("shapeless", ["chinese_traditional_food:tofu", "chinese_traditional_food:salt",
                                     "chinese_traditional_food:cooking_wine"], 2),
    "douchi": ("shapeless", ["chinese_traditional_food:black_bean", "chinese_traditional_food:salt"], 2),
    "chili_oil": ("shapeless", ["chinese_traditional_food:chili_powder", "minecraft:honey_bottle"], 1),
    "stock": ("shapeless", ["minecraft:bone_meal", "minecraft:water_bucket", "chinese_traditional_food:scallion",
                            "chinese_traditional_food:ginger"], 2),

    # ---------------- 餐具 / 厨具 ----------------
    "plate": ("shaped", {"pattern": ["C C", " C "], "key": {"C": "minecraft:clay_ball"}}, 1),
    "serving_platter": ("shaped", {"pattern": ["PPP", "P P"], "key": {"P": "#minecraft:planks"}}, 1),
    "cutting_board": ("shaped", {"pattern": ["PPP", "P P"], "key": {"P": "minecraft:stick"}}, 1),
    "chopsticks": ("shaped", {"pattern": ["S", "S"], "key": {"S": "minecraft:stick"}}, 2),
    "rolling_pin": ("shaped", {"pattern": ["S  ", " S ", "  S"], "key": {"S": "minecraft:stick"}}, 1),
    "saucer": ("shaped", {"pattern": ["CC"], "key": {"C": "minecraft:clay_ball"}}, 1),
    "cup": ("shaped", {"pattern": ["G G", " G "], "key": {"G": "minecraft:glass"}}, 1),
    "kitchen_knife": ("shaped", {"pattern": [" I", "S "], "key": {"I": "minecraft:iron_ingot", "S": "minecraft:stick"}}, 1),
    "cleaver": ("shaped", {"pattern": ["II", "IS"], "key": {"I": "minecraft:iron_ingot", "S": "minecraft:stick"}}, 1),
    "spatula": ("shaped", {"pattern": ["I", "S"], "key": {"I": "minecraft:iron_ingot", "S": "minecraft:stick"}}, 1),
    "slotted_spoon": ("shaped", {"pattern": ["II", " S"], "key": {"I": "minecraft:iron_ingot", "S": "minecraft:stick"}}, 1),
    "soup_spoon": ("shaped", {"pattern": ["I ", " S"], "key": {"I": "minecraft:iron_ingot", "S": "minecraft:stick"}}, 1),

    # ---------------- 招牌菜（手写，其余由生成器展开） ----------------
    "mapo_tofu": ("shapeless", ["chinese_traditional_food:tofu", "chinese_traditional_food:doubanjiang",
                                 "chinese_traditional_food:sichuan_peppercorn", "chinese_traditional_food:chili_powder"], 1),
    # 腊八蒜：蒜泡醋，用罐装（图标沿用蒜的造型，所以单独写配方）
    "laba_suan": ("shapeless", ["chinese_traditional_food:garlic", "chinese_traditional_food:vinegar",
                                "chinese_traditional_food:vinegar"], 2),
}

# 其余菜品的配方规则：
#   按图标种类决定"容器"，再配 3 样主料 —— 具体由 gen_content.py 展开
DISH_RECIPE_KIND = {
    "braised":       ("chinese_traditional_food:plate", "stew"),
    "dish_soup":     ("minecraft:bowl", "soup"),
    "congee":        ("minecraft:bowl", "soup"),
    "noodles":       ("minecraft:bowl", "soup"),
    "balls_bowl":    ("minecraft:bowl", "sweet"),
    "dish_plate":    ("chinese_traditional_food:plate", "stirfry"),
    "dish_fish":     ("chinese_traditional_food:plate", "fish"),
    "dish_whole":    ("chinese_traditional_food:serving_platter", "meat"),
    "dish_pot":      ("minecraft:bowl", "stew"),
    "braised_block": ("chinese_traditional_food:plate", "meat"),
    "steamed_plate": ("chinese_traditional_food:plate", "meat"),
    "meatball":      ("chinese_traditional_food:plate", "meat"),
    "rice_dish":     ("minecraft:bowl", "rice"),
    "crab":          ("chinese_traditional_food:plate", "fish"),
    "dumpling":      ("chinese_traditional_food:plate", "pastry"),
    "zongzi":        ("chinese_traditional_food:plate", "pastry"),
    "mooncake":      ("chinese_traditional_food:plate", "pastry"),
    "cake_slice":    ("chinese_traditional_food:plate", "sweet"),
    "cookie":        ("chinese_traditional_food:plate", "sweet"),
    "spring_roll":   ("chinese_traditional_food:plate", "pastry"),
    "cured_meat":    ("chinese_traditional_food:serving_platter", "meat"),
    "wine_cup":      ("chinese_traditional_food:cup", "drink"),
    "mapo":          ("minecraft:bowl", "stirfry"),
}

# 每种"主料类型"的候选材料（配方生成器按顺序取用）
DISH_RECIPE_MATERIALS = {
    "soup":    ["chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger"],
    "stew":    ["chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise"],
    "stirfry": ["minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic"],
    "fish":    ["minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion"],
    "meat":    ["minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise"],
    "rice":    ["chinese_traditional_food:rice", "chinese_traditional_food:soy_sauce", "minecraft:carrot"],
    "pastry":  ["chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger"],
    "sweet":   ["chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date"],
    "drink":   ["chinese_traditional_food:osmanthus", "chinese_traditional_food:cooking_wine", "minecraft:sugar"],
}

# ======================================================================
# 自研装置的处理表
# ======================================================================
# 每行 = (输入, 产出, 产出数量, 副产物, 副产物概率, 耗时 tick)
# 输入以 # 开头表示标签，否则是具体物品 id。按顺序匹配，先具体物品后标签。
#
# 水磨：把谷物磨成粉。需要紧邻水源，不需红石（水轮一直在转）。
MILLING = [
    ("minecraft:wheat",                            "flour",                2, "", 0.0, 100),
    ("chinese_traditional_food:rice",               "rice_flour",           2, "", 0.0, 100),
    ("chinese_traditional_food:glutinous_rice",     "glutinous_rice_flour", 2, "", 0.0, 100),
    ("chinese_traditional_food:corn",               "corn_flour",           2, "", 0.0, 100),
    ("minecraft:potato",                            "starch",               2, "", 0.0, 100),
    ("chinese_traditional_food:sichuan_peppercorn", "pepper_powder",        2, "", 0.0, 80),
    ("chinese_traditional_food:dried_chili",        "chili_powder",         2, "", 0.0, 80),
    ("chinese_traditional_food:sesame",             "sesame_oil",           1,
     "chinese_traditional_food:sesame_paste", 0.35, 120),
    ("chinese_traditional_food:red_bean",           "bean_paste",           1, "", 0.0, 140),
    ("chinese_traditional_food:soybean",            "soybean",              1, "", 0.0, 0),
]

# 脱壳机：把带壳谷物脱壳。需要红石信号。
SHELLING = [
    ("chinese_traditional_food:paddy",         "rice",     1,
     "chinese_traditional_food:rice_bran", 0.45, 120),
    ("chinese_traditional_food:millet_grass",  "millet",   1,
     "chinese_traditional_food:rice_bran", 0.30, 100),
]

# ======================================================================
# 案板切割表
# ======================================================================
# 每行 = (输入标签或物品, 输出物品, 需要“刀”与否, 额外耗时 tick)
# 输入以 # 开头表示标签，否则是具体物品 id。
# 必须先匹配具体物品、再匹配标签，所以顺序有意义。
CUTTING = [
    ("chinese_traditional_food:tofu",           "shredded_tofu",      True,  0),
    ("chinese_traditional_food:wood_ear",       "shredded_vegetable", True,  0),
    ("chinese_traditional_food:bamboo_shoot",   "shredded_vegetable", True,  0),
    ("#c:raw_fish",                             "fish_fillet",        True,  0),
    ("#c:raw_meat",                             "shredded_meat",      True,  0),
    ("chinese_traditional_food:fermented_tofu", "shredded_tofu",      False, 20),
    ("#c:vegetables",                           "shredded_vegetable", True,  0),
]

# ======================================================================
# c 命名空间通用标签（供配方与其它模组复用）
# ======================================================================
C_TAGS = {
    "flour":         ["chinese_traditional_food:flour", "chinese_traditional_food:rice_flour",
                      "chinese_traditional_food:glutinous_rice_flour", "chinese_traditional_food:corn_flour"],
    "rice":          ["chinese_traditional_food:rice", "chinese_traditional_food:glutinous_rice"],
    "grain":         ["chinese_traditional_food:rice", "chinese_traditional_food:glutinous_rice",
                      "chinese_traditional_food:millet", "chinese_traditional_food:sorghum",
                      "chinese_traditional_food:corn", "minecraft:wheat"],
    "beans":         ["chinese_traditional_food:red_bean", "chinese_traditional_food:mung_bean",
                      "chinese_traditional_food:soybean", "chinese_traditional_food:black_bean",
                      "chinese_traditional_food:pea", "chinese_traditional_food:broad_bean"],
    "vegetables":    ["chinese_traditional_food:napa_cabbage", "chinese_traditional_food:bok_choy",
                      "chinese_traditional_food:radish", "chinese_traditional_food:spinach",
                      "chinese_traditional_food:celery", "chinese_traditional_food:chive",
                      "chinese_traditional_food:eggplant", "chinese_traditional_food:cucumber",
                      "chinese_traditional_food:winter_melon", "chinese_traditional_food:luffa",
                      "chinese_traditional_food:bitter_melon", "chinese_traditional_food:green_bean",
                      "chinese_traditional_food:tomato", "chinese_traditional_food:chili",
                      "minecraft:carrot", "minecraft:potato", "minecraft:beetroot"],
    "fruits":        ["chinese_traditional_food:pear", "chinese_traditional_food:peach",
                      "chinese_traditional_food:plum", "chinese_traditional_food:apricot",
                      "chinese_traditional_food:jujube", "chinese_traditional_food:persimmon",
                      "chinese_traditional_food:mandarin", "chinese_traditional_food:pomelo",
                      "chinese_traditional_food:banana", "chinese_traditional_food:grape",
                      "chinese_traditional_food:strawberry", "chinese_traditional_food:cherry",
                      "chinese_traditional_food:pomegranate", "chinese_traditional_food:kiwi",
                      "chinese_traditional_food:mango", "chinese_traditional_food:pineapple",
                      "chinese_traditional_food:lychee", "minecraft:apple", "minecraft:sweet_berries"],
    "sugar":         ["minecraft:sugar", "chinese_traditional_food:rock_sugar"],
    "raw_meat":      ["minecraft:beef", "minecraft:porkchop", "minecraft:chicken",
                      "minecraft:mutton", "minecraft:rabbit"],
    "raw_fish":      ["minecraft:cod", "minecraft:salmon"],
    "mushrooms":     ["chinese_traditional_food:wood_ear", "minecraft:brown_mushroom",
                      "minecraft:red_mushroom"],    "crops":         ["chinese_traditional_food:napa_cabbage", "chinese_traditional_food:bok_choy",
                      "chinese_traditional_food:radish", "chinese_traditional_food:tomato",
                      "chinese_traditional_food:chili", "chinese_traditional_food:eggplant"],
    "crops/chili":   ["chinese_traditional_food:chili"],
    "crops/tomato":  ["chinese_traditional_food:tomato"],
    "crops/potato":  ["minecraft:potato"],
}

# 本模组自己的标签
OWN_TAGS = {
    "dishes": "ALL_DISHES",
    "placeable_dishes": "dishes + tofu",
    "knives": ["chinese_traditional_food:kitchen_knife", "chinese_traditional_food:cleaver"],
    "raw_meat": ["#c:raw_meat"],
    "tofu": ["chinese_traditional_food:tofu", "chinese_traditional_food:fermented_tofu"],
    "prepared": ["chinese_traditional_food:shredded_vegetable", "chinese_traditional_food:shredded_meat",
                 "chinese_traditional_food:fish_fillet", "chinese_traditional_food:shredded_tofu"],
    "husked_grain": ["chinese_traditional_food:paddy", "chinese_traditional_food:millet_grass"],
    "bran": ["chinese_traditional_food:rice_bran"],
    "seeds": ["chinese_traditional_food:rice_seeds", "chinese_traditional_food:millet_seeds",
              "chinese_traditional_food:sorghum_seeds", "chinese_traditional_food:corn_seeds",
              "chinese_traditional_food:soybean_seeds", "chinese_traditional_food:mung_bean_seeds",
              "chinese_traditional_food:red_bean_seeds", "chinese_traditional_food:peanut_seeds",
              "chinese_traditional_food:sesame_seeds", "chinese_traditional_food:taro_seeds",
              "chinese_traditional_food:sweet_potato_slip", "chinese_traditional_food:napa_cabbage_seeds",
              "chinese_traditional_food:radish_seeds", "chinese_traditional_food:chili_seeds",
              "chinese_traditional_food:cucumber_seeds", "minecraft:wheat_seeds"],
    "seasonings": ["chinese_traditional_food:salt", "chinese_traditional_food:soy_sauce",
                   "chinese_traditional_food:vinegar", "chinese_traditional_food:cooking_wine",
                   "chinese_traditional_food:sichuan_peppercorn", "chinese_traditional_food:star_anise",
                   "chinese_traditional_food:cinnamon_bark", "chinese_traditional_food:chili_powder",
                   "chinese_traditional_food:doubanjiang", "minecraft:sugar"],
    "utensils": ["chinese_traditional_food:kitchen_knife", "chinese_traditional_food:cleaver",
                 "chinese_traditional_food:spatula", "chinese_traditional_food:slotted_spoon",
                 "chinese_traditional_food:soup_spoon", "chinese_traditional_food:rolling_pin",
                 "chinese_traditional_food:chopsticks", "chinese_traditional_food:saucer",
                 "chinese_traditional_food:cup", "minecraft:bowl"],
}

# 中文名 -> 分组标题（用于生成 Java 注释与语言文件分组）
GROUP_TITLES = {
    "lu": "鲁菜", "chuan": "川菜", "yue": "粤菜", "su": "苏菜",
    "min": "闽菜", "zhe": "浙菜", "xiang": "湘菜", "hui": "徽菜",
    "spring": "春节", "lantern": "元宵", "qingming": "清明", "duanwu": "端午",
    "qixi": "七夕", "midautumn": "中秋", "chongyang": "重阳", "laba": "腊八",
    "winter": "冬至",
}

GROUP_ORDER = ["lu", "chuan", "yue", "su", "min", "zhe", "xiang", "hui",
               "spring", "lantern", "qingming", "duanwu", "qixi", "midautumn",
               "chongyang", "laba", "winter"]
