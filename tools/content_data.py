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
# 作物种子
# ======================================================================
# 每行同 INGREDIENTS。营养值一律为 0：种子不是食物。
#
# 这些名字**按农民嘴里的叫法**取，而不是机械地“作物名 + 种”：
#
#   玉米粒   玉米播种用的就是玉米粒本身，没有“玉米种”这个东西
#   花生仁   花生是把英里的仁剥出来种的
#   蒜瓣     种蒜就是埋一瓣蒜
#   芋子     芋头留种用的子芋
#   红薯秧   红薯靠插秧，不是撒籽
#   山药嘴子 山药的“龙头/嘴子”就是种
#   西瓜／萝卜／白菜… 籽   这些真的就是籽
#
# id 不能改（配方、标签、掉落都引着它），改的只是显示名。
SEEDS = [
    # --- 谷物 ---
    ("rice_seeds",         "稻种",     "Rice Seeds",         "seed_paddy",  "wheat",    0, 0),
    ("millet_seeds",       "谷子种",   "Millet Seeds",       "seed_millet",  "gold",     0, 0),
    ("sorghum_seeds",      "高粱籽",   "Sorghum Seeds",      "seed_sorghum",  "red",      0, 0),
    ("corn_seeds",         "玉米粒",   "Corn Kernels",       "seed_corn",  "yellow",   0, 0),
    # --- 豆类 ---
    ("soybean_seeds",      "黄豆种",   "Soybean Seeds",      "bean_round",  "cream",    0, 0),
    ("mung_bean_seeds",    "绿豆种",   "Mung Bean Seeds",    "bean_mung",   "mung",     0, 0),
    ("red_bean_seeds",     "红豆种",   "Red Bean Seeds",     "bean_kidney", "red",      0, 0),
    ("pea_seeds",          "豌豆种",   "Pea Seeds",          "bean_pea",    "palegreen", 0, 0),
    ("broad_bean_seeds",   "蚕豆种",   "Broad Bean Seeds",   "bean_flat",   "palegreen", 0, 0),
    ("green_bean_seeds",   "豆角种",   "Green Bean Seeds",   "bean_kidney", "green",    0, 0),
    ("peanut_seeds",       "花生仁",   "Peanut Kernels",     "seed_peanut",   "brown",      0, 0),
    ("sesame_seeds",       "芝麻种",   "Sesame Seeds",       "seed_sesame",  "cream",    0, 0),
    # --- 薯类 ---
    ("taro_seeds",         "芋子",     "Taro Corms",         "seed_taro",  "purple",   0, 0),
    ("sweet_potato_slip",  "红薯秧",   "Sweet Potato Slips", "seed_slip", "green",    0, 0),
    ("chinese_yam_slip",   "山药嘴子", "Yam Sets",           "seed_yam",  "tan",      0, 0),
    ("ginger_seeds",       "姜种",     "Ginger Sets",        "seed_ginger", "tan",    0, 0),
    ("garlic_seeds",       "蒜瓣",     "Garlic Cloves",      "seed_garlic", "white",  0, 0),
    # --- 叶菜 / 茎菜 ---
    ("napa_cabbage_seeds", "白菜籽",   "Napa Cabbage Seeds", "seed_brassica",  "seedbr",  0, 0),
    ("bok_choy_seeds",     "小白菜籽", "Bok Choy Seeds",     "seed_brassica",  "seedpale", 0, 0),
    ("radish_seeds",       "萝卜籽",   "Radish Seeds",       "seed_radish",  "seedpale",    0, 0),
    ("spinach_seeds",      "菠菜种",   "Spinach Seeds",      "seed_prickly",  "seedbr",   0, 0),
    ("celery_seeds",       "芹菜籽",   "Celery Seeds",       "seed_umbel",  "seedpale",   0, 0),
    ("cilantro_seeds",     "香菜籽",   "Cilantro Seeds",     "seed_umbel",  "seedbr",    0, 0),
    ("chive_seeds",        "韭菜籽",   "Chive Seeds",        "seed_allium",  "black",   0, 0),
    ("scallion_seeds",     "葱籽",     "Scallion Seeds",     "seed_allium_round",  "seedsb",    0, 0),
    ("chili_seeds",        "辣椒种",   "Chili Seeds",        "seed_capsicum",  "chili",    0, 0),
    ("eggplant_seeds",     "茄子种",   "Eggplant Seeds",     "seed_solanum",  "cream",  0, 0),
    ("tomato_seeds",       "番茄种",   "Tomato Seeds",       "seed_solanum",  "seedpale",  0, 0),
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

    # ---------------- 早餐 ----------------
    # 早点的共同点：饱食度不高但**饱和度高**，而且大多带一点即时收益
    # （提神 / 暖身），符合"吃了好去干活"的感觉。
    ("mantou",          "馒头",       "Steamed Bun",            "breakfast", "cake_slice", "steamed",  5, 0.7, "NONE"),
    ("hua_juan",        "花卷",       "Steamed Twisted Roll",   "breakfast", "cake_slice", "cake",     6, 0.8, "NONE"),
    ("baozi",           "包子",       "Steamed Stuffed Bun",    "breakfast", "dumpling",   "steamed",  7, 0.9, "SATED"),
    ("xiao_long_bao",   "小笼包",     "Soup Dumpling",          "breakfast", "dumpling",   "steamed",  6, 0.9, "SATED_REFRESH"),
    ("dou_sha_bao",     "豆沙包",     "Red Bean Bun",           "breakfast", "dumpling",   "cake",     6, 0.9, "RISE_UP"),
    ("youtiao",         "油条",       "Fried Dough Stick",      "breakfast", "spring_roll", "gold",    6, 0.8, "CRISP"),
    ("doujiang",        "豆浆",       "Soy Milk",               "breakfast", "wine_cup",   "white",     4, 0.6, "REFRESH"),
    ("youtiao_doujiang", "豆浆油条",  "Soy Milk and Fried Dough", "breakfast", "dish_plate", "gold",   9, 1.1, "CRISP_REFRESH"),
    ("chao_gan",        "炒肝",       "Stir-fried Liver",       "breakfast", "dish_soup",  "braised",   6, 0.9, "NOURISH"),
    ("huntun",          "馄饨",       "Wonton",                 "breakfast", "dish_soup",  "soup",      7, 1.1, "WARMTH"),
    ("wonton_soup",     "馄饨汤",     "Wonton Soup",            "breakfast", "dish_soup",  "soup",      8, 1.2, "WARMTH_NOURISH"),
    ("xiaomi_zhou",     "小米粥",     "Millet Porridge",        "breakfast", "congee",     "gold",      5, 0.9, "WARMTH"),
    ("zhou_congee",     "白粥",       "Plain Rice Porridge",    "breakfast", "congee",     "white",     4, 0.7, "NONE"),
    ("jianbing",        "煎饼果子",   "Jianbing",               "breakfast", "cake_slice", "wheat",     9, 1.2, "SATED_REFRESH"),
    ("chashao_bao",     "叉烧包",     "BBQ Pork Bun",           "breakfast", "dumpling",   "redbraised", 7, 1.0, "SATED"),
    ("tangyuan",        "汤圆",       "Glutinous Rice Ball",    "breakfast", "dumpling",   "white",     5, 0.9, "RISE_UP"),
    ("mixian",          "米线",       "Rice Noodles",           "breakfast", "noodles",    "steamed",   7, 1.1, "WARMTH"),
    ("chao_mian",       "炒面",       "Fried Noodles",          "breakfast", "noodles",    "stirfry",   8, 1.1, "SATED"),

    # ---------------- 特色小吃 ----------------
    # 小吃：单价低、饱食度小、但往往带**可叠加的小收益**，适合边逛边吃。
    ("chou_doufu",       "臭豆腐",     "Stinky Tofu",            "snack", "mapo",        "fungus",    5, 0.7, "CRISP"),
    ("kao_lengmian",     "烤冷面",     "Grilled Cold Noodles",   "snack", "spring_roll", "redbraised", 7, 0.9, "SATED"),
    ("chuan_chuan",      "串串香",     "Chuanchuan Skewers",     "snack", "dish_plate",  "chili_oil",  6, 0.8, "REFRESH"),
    ("roujiamo",         "肉夹馍",     "Roujiamo",               "snack", "dumpling",    "braised",    9, 1.2, "SATED_NOURISH"),
    ("jian_gao",         "煎糕",       "Pan-fried Cake",         "snack", "cake_slice",  "pastry",     6, 0.8, "NONE"),
    ("guo_tie",          "锅贴",       "Pot Stickers",           "snack", "dumpling",    "gold",       7, 0.9, "CRISP"),
    ("shaomai",          "烧卖",       "Siu Mai",                "snack", "dumpling",    "gold",       7, 0.9, "SATED"),
    ("liangpi",          "凉皮",       "Cold Skin Noodles",      "snack", "noodles",     "stirfry",    6, 0.8, "REFRESH"),
    ("chuanbei_liangfen", "川北凉粉",  "Sichuan Bean Jelly",     "snack", "dish_plate",  "chili_oil",  6, 0.8, "REFRESH"),
    ("tanghulu",         "糖葫芦",     "Candied Hawthorn",       "snack", "cherries",    "red",        4, 0.6, "RISE_UP"),
    ("mahuadou",         "麻花",       "Fried Dough Twist",      "snack", "spring_roll", "gold",       5, 0.7, "CRISP"),
    ("shao_bing",        "烧饼",       "Baked Flatbread",        "snack", "cake_slice",  "wheat",      6, 0.8, "SATED"),
    ("zhima_tuan",       "芝麻团",     "Sesame Ball",            "snack", "cookie",      "tan",        5, 0.7, "RISE_UP"),
    ("zongzi_xian",      "咸肉粽",     "Savoury Zongzi",         "snack", "zongzi",      "braised",    8, 1.0, "SATED"),
    ("rice_cake",        "年糕片",     "Sliced Rice Cake",       "snack", "cake_slice",  "white",      5, 0.7, "RISE_UP"),
    ("steamed_pumpkin",  "蒸南瓜",     "Steamed Pumpkin",        "snack", "steamed_plate", "orange",   5, 0.8, "NONE"),
    ("doufunao",         "豆腐脑",     "Tofu Pudding",           "snack", "congee",      "white",      5, 0.8, "REFRESH"),
    ("suantang",         "酸汤",       "Sour Soup",              "snack", "dish_soup",   "vinegar",    5, 0.8, "REFRESH"),
    ("egg_drop_soup",    "蛋花汤",     "Egg Drop Soup",          "snack", "dish_soup",   "soup",       5, 0.8, "WARMTH"),
    ("tomato_egg",       "西红柿炒蛋", "Tomato and Egg",         "snack", "dish_plate",  "tomato",     7, 0.9, "NONE"),
    ("scrambled_egg",    "炒蛋",       "Scrambled Egg",          "snack", "dish_plate",  "gold",       5, 0.8, "NONE"),
    ("chive_egg",        "韭黄炒蛋",   "Chive and Egg",          "snack", "dish_plate",  "greendish",  7, 0.9, "NONE"),
    ("dry_fried_beans",  "干煸豆角",   "Dry-fried Green Beans",  "snack", "dish_plate",  "chili",      6, 0.8, "CRISP"),
    ("stir_fried_pea",   "清炒豌豆",   "Stir-fried Peas",        "snack", "dish_plate",  "greendish",  6, 0.8, "NONE"),
    ("braised_bamboo",   "油焖笋",     "Braised Bamboo Shoots",  "snack", "dish_plate",  "braised",    6, 0.9, "NONE"),
    ("twice_cooked_pork", "回锅肉片",  "Twice-cooked Pork Slices", "snack", "dish_plate", "redbraised", 8, 1.0, "REFRESH"),
    ("red_bean_soup",    "红豆汤",     "Red Bean Soup",          "snack", "dish_soup",   "red",        5, 0.9, "WARMTH"),
    ("mung_bean_soup",   "绿豆汤",     "Mung Bean Soup",         "snack", "dish_soup",   "mung",       5, 0.9, "REFRESH"),
    ("winter_melon_soup", "冬瓜汤",    "Winter Melon Soup",      "snack", "dish_soup",   "palegreen",  4, 0.7, "REFRESH"),
    ("lotus_seed_soup",  "莲子羹",     "Lotus Seed Soup",        "snack", "dish_soup",   "cream",      5, 0.9, "NOURISH"),
    ("yam_ribs_soup",    "山药排骨汤", "Yam and Rib Soup",       "snack", "dish_soup",   "soup",       8, 1.2, "WARMTH_NOURISH"),
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
    # ==================================================================
    # 工作台只做"器物"——机器、锅具、餐具、厨具。
    #
    # **食材一律不在这里。** 早先本表里塞了一大堆"小麦×2 = 稻谷"、
    # "牛奶桶 + 骨粉 = 豆腐"、"作物×2 = 种子"这种充数配方，
    # 现在全部拆掉，换成三条真实路线：
    #
    #   1. 野生作物 —— 野外自然生成，采一次就有种子和收成（见 CROPS）
    #   2. 机器加工 —— 磨粉（MILLING）、脱壳（SHELLING）
    #   3. 下锅     —— 酱、醋、酒、高汤、豆腐都在汤锅/炒锅里做（见 BOILING / COOKING）
    #
    # 所以"第一粒种子"只能从野外拿到，不能凭空合成 —— 这是真实感的关键一步。
    # ==================================================================

    # ---------------- 熔炼类 ----------------
    # 烘干 / 熬糖 / 晒盐：这些确实是"放在火上"的事，用熔炉最贴切。
    "baked_sweet_potato": ("smelting", ["chinese_traditional_food:sweet_potato"], 1),
    "dried_jujube": ("smelting", ["chinese_traditional_food:red_date"], 1),
    "dried_bamboo_shoot": ("smelting", ["chinese_traditional_food:bamboo_shoot"], 1),
    "dried_chili": ("smelting", ["chinese_traditional_food:chili"], 1),
    "rock_sugar": ("smelting", ["minecraft:sugar"], 1),
    "salt": ("smelting", ["minecraft:dried_kelp"], 1),

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

    # ---------------- 大型机（"3×3 放大版"）----------------
    # 配方思路：**四台小型机 + 一个中枢材料** —— 看一眼就知道是"把四条产线
    # 合成一条"，而且成本正好是小型机的四倍左右，不会出现"直接做大的更划算"。
    # 中枢材料按机器性质选：发电机用岩浆桶（热源）、磨粉机用石磨（磨盘）、
    # 脱壳机用铁块（滚筒）。
    "large_furnace_generator": ("shaped",
                                {"pattern": ["GGG", "GLG", "GGG"], "key": {
                                    "G": "chinese_traditional_food:furnace_generator",
                                    "L": "minecraft:lava_bucket"}}, 1),
    "large_electric_mill": ("shaped",
                            {"pattern": ["III", "MSM", "III"], "key": {
                                "I": "minecraft:iron_block",
                                "M": "chinese_traditional_food:electric_mill",
                                "S": "minecraft:stone_bricks"}}, 1),
    "large_electric_sheller": ("shaped",
                               {"pattern": ["III", "MSM", "III"], "key": {
                                   "I": "minecraft:iron_block",
                                   "M": "chinese_traditional_food:electric_sheller",
                                   "S": "minecraft:cauldron"}}, 1),

    # ---------------- 灶火系统 ----------------
    # 电磁炉：铜线圈 + 铁壳 + 石台面 —— 看得出是“用电的”
    "stove": ("shaped", {"pattern": ["CCC", "IRI", "SSS"],
                          "key": {"C": "minecraft:copper_ingot",
                                  "I": "minecraft:iron_ingot",
                                  "R": "minecraft:redstone",
                                  "S": "minecraft:stone"}}, 1),
    # 炒锅：铁块敲出来的圆锅 + 两耳
    "wok": ("shaped", {"pattern": ["I I", " I "],
                        "key": {"I": "minecraft:iron_ingot"}}, 1),
    # 蒸笼：竹材 + 木
    "steamer": ("shaped", {"pattern": ["PPP", "B B", "PPP"],
                            "key": {"P": "#minecraft:planks",
                                    "B": "minecraft:bamboo"}}, 1),
    # 汤锅：深筒锅 + 双耳
    "soup_pot": ("shaped", {"pattern": ["I I", "ICI", "III"],
                             "key": {"I": "minecraft:iron_ingot",
                                     "C": "minecraft:cauldron"}}, 1),

    # ---------------- 餐具 / 厨具 ----------------
    "plate": ("shaped", {"pattern": ["C C", " C "], "key": {"C": "minecraft:clay_ball"}}, 1),
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

    # ---------------- 招牌菜 ----------------
    # **注意：菜品不在这里。** 所有菜品一律用锅做，见下面的
    # DISH_COOK_OVERRIDE 与 DISH_RECIPE_KIND。
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
    "dish_whole":    ("chinese_traditional_food:plate", "meat"),
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
    "cured_meat":    ("chinese_traditional_food:plate", "meat"),
    "wine_cup":      ("chinese_traditional_food:cup", "drink"),
    "mapo":          ("minecraft:bowl", "stirfry"),
    # 糖葫芦：串在竹签上的山楂 —— 用碗当容器不合适，用糖当主料
    "cherries":      ("chinese_traditional_food:cup", "sweet"),
}

# 每种"主料类型"的候选材料（配方生成器按顺序取用）
DISH_RECIPE_MATERIALS = {
    "soup":    ["chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger",
                "minecraft:carrot"],
    "stew":    ["chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce",
                "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark"],
    "stirfry": ["minecraft:porkchop", "chinese_traditional_food:scallion",
                "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil"],
    "fish":    ["minecraft:cod", "chinese_traditional_food:ginger",
                "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine"],
    "meat":    ["minecraft:beef", "chinese_traditional_food:soy_sauce",
                "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger"],
    "rice":    ["chinese_traditional_food:rice", "chinese_traditional_food:soy_sauce",
                "minecraft:carrot", "chinese_traditional_food:scallion"],
    "pastry":  ["chinese_traditional_food:flour", "chinese_traditional_food:scallion",
                "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil"],
    "sweet":   ["chinese_traditional_food:bean_paste", "minecraft:sugar",
                "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus"],
    "drink":   ["chinese_traditional_food:osmanthus", "chinese_traditional_food:cooking_wine",
                "minecraft:sugar", "chinese_traditional_food:red_date"],
}

# ======================================================================
# 锅合成：做法 -> 用哪口锅
# ======================================================================
# 三件锅具各自负责一类做法，和现实里一致，玩家不用记：
#
#   汤锅 boiler   炖、汤、饭 —— 久煮的
#   蒸笼 steamer  面点、糕饼 —— 靠蒸汽的
#   炒锅 wok      炒、煎、整菜 —— 猛火的
#
# 值就是 ModRecipes 里的表名，gen_content.py 按它把菜谱分到三张表里。
DISH_COOKER = {
    "soup":    "SOUP_POT",
    "stew":    "SOUP_POT",
    "rice":    "SOUP_POT",
    "pastry":  "STEAMER",
    "sweet":   "STEAMER",
    "stirfry": "WOK",
    "fish":    "WOK",
    "meat":    "WOK",
    "drink":   "WOK",
}

# 每种做法在锅里要多久（tick）。数字按"这道菜现实里大概要多久"排：
# 炖汤最久、面点居中、爆炒最快。
DISH_COOK_TICKS = {
    "stew":    260,
    "soup":    200,
    "rice":    220,
    "pastry":  180,
    "sweet":   160,
    "meat":    200,
    "fish":    160,
    "stirfry": 120,
    "drink":   100,
}

# 少数菜品的锅谱需要手写（它们的图标种类不在 DISH_RECIPE_KIND 里，
# 或者材料必须精确到某几样才像那道菜）。
#   id -> (锅, [材料...], 产出数量, 耗时 tick)
DISH_COOK_OVERRIDE = {
    # 麻婆豆腐：豆腐 + 豆瓣酱 + 花椒 + 辣椒粉才是那个味，不能用通用的"炒"料包
    "mapo_tofu": ("WOK", ["chinese_traditional_food:tofu",
                          "chinese_traditional_food:doubanjiang",
                          "chinese_traditional_food:sichuan_peppercorn",
                          "chinese_traditional_food:chili_powder"], 1, 200),
    # 腊八蒜：蒜泡醋 —— 图标沿用蒜的造型，所以单独写
    "laba_suan": ("SOUP_POT", ["chinese_traditional_food:garlic",
                               "chinese_traditional_food:vinegar",
                               "chinese_traditional_food:vinegar"], 2, 240),
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
]

# 脱壳机：把带壳谷物脱壳。需要红石信号。
SHELLING = [
    ("chinese_traditional_food:paddy",         "rice",     1,
     "chinese_traditional_food:rice_bran", 0.45, 120),
    ("chinese_traditional_food:millet_grass",  "millet",   1,
     "chinese_traditional_food:rice_bran", 0.30, 100),
]

# ======================================================================
# 炉灶系列：热力加工表
# ======================================================================
# 这三张表对应三件"锅具"，它们本身不耗电 —— 而是**坐在炉灶上一格**，
# 由炉灶烧燃料提供热力。见 common/block/entity/AbstractHeatProcessorBlockEntity。
#
# 每行同 MILLING：(输入, 产出, 数量, 副产物, 概率, tick)
#
# 为什么做成"热力"而不是继续用 FE：现实里蒸包子、炖汤、爆炒都是烧火，
# 不是插电。分开之后玩家有了两条并行路线 —— 电气线（磨粉/脱壳，快且省）
# 与灶火线（蒸煮炒，慢但便宜、随处可搭）。

# 蒸笼：蒸汽把生料催熟。产出多为"熟"形态。
# 每行 = (输入, 产出, 数量, 副产物, 概率, tick)，与磨粉表同构。
# 这些是"一样进一样出"的简单转化；**菜品**另有锅谱，见 DISH_COOKER。
STEAMING = [
    ("chinese_traditional_food:flour",          "mantou",           2, "", 0.0, 120),
    ("chinese_traditional_food:glutinous_rice", "zao_zong",         2, "", 0.0, 140),
    ("chinese_traditional_food:rice_flour",     "rice_cake",        2, "", 0.0, 130),
    ("chinese_traditional_food:bean_paste",     "dou_sha_bao",      2, "", 0.0, 150),
    ("minecraft:porkchop",                      "baozi",            2, "", 0.0, 160),
    ("#c:raw_meat",                             "xiao_long_bao",    2, "", 0.0, 170),
    ("chinese_traditional_food:sweet_potato",   "steamed_pumpkin",  1, "", 0.0, 110),
    ("chinese_traditional_food:sweet_potato",   "baked_sweet_potato", 1, "", 0.0, 110),
]

# 汤锅：加水 / 高汤把料吊成汤。
BOILING = [
    ("chinese_traditional_food:stock",         "egg_drop_soup",    1, "", 0.0, 120),
    ("chinese_traditional_food:napa_cabbage",  "winter_melon_soup", 1, "", 0.0, 130),
    ("chinese_traditional_food:red_bean",      "red_bean_soup",    1, "", 0.0, 160),
    ("chinese_traditional_food:mung_bean",     "mung_bean_soup",   1, "", 0.0, 150),
    ("chinese_traditional_food:rice",          "zhou_congee",      1, "", 0.0, 140),
    ("chinese_traditional_food:millet",        "xiaomi_zhou",      1, "", 0.0, 130),
    ("chinese_traditional_food:lotus_seed",    "lotus_seed_soup",  1, "", 0.0, 170),
    ("chinese_traditional_food:chinese_yam",   "yam_ribs_soup",    1, "", 0.0, 175),
    ("#c:raw_meat",                            "wonton_soup",      1, "", 0.0, 165),
    ("chinese_traditional_food:vinegar",       "suantang",         1, "", 0.0, 110),
    ("chinese_traditional_food:soybean",       "doufunao",         1, "", 0.0, 150),
]

# 炒锅：猛火快炒。
COOKING = [
    ("minecraft:egg",                          "scrambled_egg",      1, "", 0.0, 90),
    ("chinese_traditional_food:tomato",        "tomato_egg",         1, "", 0.0, 110),
    ("chinese_traditional_food:green_bean",    "dry_fried_beans",    1, "", 0.0, 120),
    ("chinese_traditional_food:pea",           "stir_fried_pea",     1, "", 0.0, 110),
    ("chinese_traditional_food:chive",         "chive_egg",          1, "", 0.0, 105),
    ("chinese_traditional_food:bamboo_shoot",  "braised_bamboo",     1, "", 0.0, 125),
    ("#c:raw_meat",                            "twice_cooked_pork",  1, "", 0.0, 140),
    ("chinese_traditional_food:tofu",          "chou_doufu",         1, "", 0.0, 150),
    ("chinese_traditional_food:flour",         "youtiao",            2, "", 0.0, 100),
    ("chinese_traditional_food:rice_flour",    "mahuadou",           2, "", 0.0, 110),
]

# ======================================================================
# 锅里的"非菜品"配方：酱 / 醋 / 酒 / 汤底 / 豆腐 ……
# ======================================================================
# 上面 STEAMING / BOILING / COOKING 三张表都是"一样进一样出"的简单转化。
# 但真正的调味料几乎都是"几样东西一起熬"：豆腐要豆浆加盐卤、豆瓣酱要蚕豆加辣椒、
# 高汤要骨头加葱姜。这些**多材料**的配方另行写在这里。
#
# 每行 = (锅, 产出, 数量, 耗时 tick, [材料...])
# 材料可以重复（写两次 = 要两份），和菜品的锅谱同一套规则。
POT = [
    # ---------------- 汤锅：熬与酿 ----------------
    # 豆腐：豆浆要用盐卤（这里就是盐）点，两把黄豆出一份 —— 这是真正的做法
    ("SOUP_POT", "tofu",              2, 150, ["chinese_traditional_food:soybean",
                                                "chinese_traditional_food:soybean",
                                                "chinese_traditional_food:salt"]),
    # 豆沙：红豆加糖煮烂
    ("SOUP_POT", "bean_paste",        2, 200, ["chinese_traditional_food:red_bean",
                                                "chinese_traditional_food:red_bean",
                                                "minecraft:sugar"]),
    # 酱油：黄豆 + 小麦 + 盐，酿出来的
    ("SOUP_POT", "soy_sauce",         1, 180, ["chinese_traditional_food:soybean",
                                                "minecraft:wheat",
                                                "chinese_traditional_food:salt"]),
    # 醋：米加糖发酵
    ("SOUP_POT", "vinegar",           1, 160, ["chinese_traditional_food:rice",
                                                "minecraft:sugar"]),
    # 料酒：米加盐
    ("SOUP_POT", "cooking_wine",      1, 170, ["chinese_traditional_food:rice",
                                                "chinese_traditional_food:rice",
                                                "chinese_traditional_food:salt"]),
    # 豆瓣酱：蚕豆 + 辣椒 + 盐
    ("SOUP_POT", "doubanjiang",       1, 200, ["chinese_traditional_food:broad_bean",
                                                "chinese_traditional_food:chili",
                                                "chinese_traditional_food:salt"]),
    # 豆豉：黑豆加盐
    ("SOUP_POT", "douchi",            2, 170, ["chinese_traditional_food:black_bean",
                                                "chinese_traditional_food:salt"]),
    # 腐乳：豆腐泡盐和料酒
    ("SOUP_POT", "fermented_tofu",    2, 190, ["chinese_traditional_food:tofu",
                                                "chinese_traditional_food:salt",
                                                "chinese_traditional_food:cooking_wine"]),
    # 甜面酱：面粉加糖盐炒熟
    ("SOUP_POT", "sweet_bean_sauce",  1, 180, ["chinese_traditional_food:flour",
                                                "chinese_traditional_food:salt",
                                                "minecraft:sugar"]),
    # 蚝油：海带版（游戏里拿不到生蚝，用海带与紫菜类替代提鲜）
    ("SOUP_POT", "oyster_sauce",      1, 170, ["minecraft:kelp",
                                                "chinese_traditional_food:salt",
                                                "minecraft:sugar"]),
    # 高汤：骨头 + 葱 + 姜，吊出来的
    ("SOUP_POT", "stock",             2, 200, ["minecraft:bone",
                                                "minecraft:bone",
                                                "chinese_traditional_food:scallion",
                                                "chinese_traditional_food:ginger"]),
    # 腌菜：白菜加盐压
    ("SOUP_POT", "pickled_vegetable", 2, 180, ["chinese_traditional_food:napa_cabbage",
                                                "chinese_traditional_food:salt",
                                                "chinese_traditional_food:salt"]),
    # 豆芽：黄豆用淡盐水泡发
    ("SOUP_POT", "dou_ya",            3, 160, ["chinese_traditional_food:soybean",
                                                "chinese_traditional_food:salt"]),

    # ---------------- 炒锅：干焙与泼油 ----------------
    # 五香粉：五味香料炒香，再焙成粉
    ("WOK", "five_spice_powder", 2, 140, ["chinese_traditional_food:star_anise",
                                            "chinese_traditional_food:cinnamon_bark",
                                            "chinese_traditional_food:cumin",
                                            "chinese_traditional_food:sichuan_peppercorn",
                                            "chinese_traditional_food:bay_leaf"]),
    # 芝麻酱：炒香芝麻再研磨
    ("WOK", "sesame_paste",      1, 140, ["chinese_traditional_food:sesame",
                                            "chinese_traditional_food:sesame"]),
    # 辣椒油：热油泼辣子
    ("WOK", "chili_oil",         1, 120, ["chinese_traditional_food:chili_powder",
                                            "chinese_traditional_food:sesame_oil"]),
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
    # seeds 标签的成员由 gen_content.py 按 CROPS 表现算 ——
    # 因为种子不是 ModItems 里的物品，而是 ModCrops 里植株方块的方块物品，
    # 手抄一份清单必然会和 CROPS 表走散。
    "seeds": [],
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
    "breakfast": "早餐", "snack": "特色小吃",
}

GROUP_ORDER = ["lu", "chuan", "yue", "su", "min", "zhe", "xiang", "hui",
               "spring", "lantern", "qingming", "duanwu", "qixi", "midautumn",
               "chongyang", "laba", "winter",
               "breakfast", "snack"]

# ======================================================================
# 果树：树上的水果要有树苗，树苗长成树，树叶掉果子
# ======================================================================
# (水果 id, 树形, 树干高, 树冠半径)
#
# 树形只有三档，差别就是"多高、多胖"：
#   0 小  李 / 杏 / 枣 / 橘       —— 院子里的小果木
#   1 中  梨 / 桃 / 樱桃 / 石榴 / 龙眼 / 荔枝
#   2 大  柿 / 柚 / 芒果          —— 能长到两层楼
#
# 水果（草莓、葡萄、香蕉、菠萝、猕猴桃）不在表里 —— 它们本来就不是树：
#   草莓是草本、葡萄是藤、香蕉是草本、菠萝是地面植物、猕猴桃是藤本。
#   所以它们仍然由野生作物 / 作物种植来获得，不硬塞进果树。
TREE_FRUITS = [
    ("plum",        0),
    ("apricot",     0),
    ("jujube",      0),
    ("mandarin",    0),
    ("pear",        1),
    ("peach",       1),
    ("cherry",      1),
    ("pomegranate", 1),
    ("longan",      1),
    ("lychee",      1),
    ("persimmon",   2),
    ("pomelo",      2),
    ("mango",       2),
]

# 树叶的掉落概率。用户要求"默认概率为10%掉落树苗和果实"，
# 所以两者都是 10%。想调就改这里 —— 它会被写进战利品表。
TREE_LEAF_DROP_CHANCE = 0.10

# 树苗长成树的概率（1/N）。原版树苗是 1/7（平均约两分半钟）。
TREE_GROW_ONE_IN = 7

# 树叶掉落的木棍数量（原版橡树树叶会掉 0~2 根木棍）
TREE_LEAF_STICK_MAX = 2

# ----------------------------------------------------------------------
# 每棵树的树叶长什么样
# ----------------------------------------------------------------------
# 一开始 13 种树叶是"同一张图换色相"，看着像复制粘贴。这里给每棵树
# 单独定一套：**(叶基色, 明暗跨度, 镂空率, 叶簇尺度, 蜡质反光)**。
#
#   叶基色      —— 贴图直接写进像素的颜色（不走运行时 tint）
#   明暗跨度    —— 4 档明度之间拉多开；越大越"花"，越小越"平"
#   镂空率      —— 原版橡树叶是 0.328，围着它上下浮动，但每棵树略有不同
#   叶簇尺度    —— 低频噪声的格子大小（3=小叶密、5=大叶疏）
#   蜡质反光    —— 柑橘 / 柿 / 柚这类革质叶，加几点高光
#
# 依据是真实的叶色：枣、杏、石榴是亮黄绿；桃、李、樱桃是嫩绿；
# 柑橘、龙眼、荔枝、柿、柚是深绿；芒果偏蓝绿；梨偏灰绿。
TREE_LEAF_LOOK = {
    "plum":        ((92, 146, 62),  2.3, 0.32, 4, False),
    "apricot":     ((118, 162, 74), 2.5, 0.30, 4, False),
    "jujube":      ((126, 170, 68), 2.6, 0.28, 3, False),
    "mandarin":    ((58, 112, 52),  2.2, 0.34, 4, True),
    "pear":        ((104, 146, 82), 2.1, 0.33, 5, False),
    "peach":       ((110, 158, 70), 2.4, 0.30, 3, False),
    "cherry":      ((76, 126, 56),  2.5, 0.31, 4, False),
    "pomegranate": ((116, 158, 62), 2.4, 0.29, 5, False),
    "longan":      ((66, 118, 58),  2.3, 0.33, 4, False),
    "lychee":      ((62, 114, 64),  2.4, 0.32, 4, False),
    "persimmon":   ((52, 98, 48),   2.6, 0.34, 5, True),
    "pomelo":      ((60, 116, 56),  2.3, 0.33, 4, True),
    "mango":       ((70, 126, 82),  2.4, 0.31, 3, False),
}

# ----------------------------------------------------------------------
# 每棵树的叶片形状 / 排列（决定树苗与树叶图标的画法）
# ----------------------------------------------------------------------
# 只让 13 种树叶"颜色不同、形状一样"是不够的 —— 图标摆一排一眼就是
# 复制粘贴。这里按**真实叶形**给每棵树一套：
#
# 叶形（`TREE_LEAF_FORM` 的键）
#   lanceolate 披针形  两头尖、中段最宽偏基部 —— 桃 / 李 / 杏 / 梅 / 芒果
#   ovate      卵形    基部最宽、向尖端收     —— 枣 / 石榴
#   obovate    倒卵形  基部窄、前端宽        —— 柑橘 / 柚（叶柄有翼）
#   elliptic   椭圆形  上下对称的椭圆        —— 梨 / 柿 / 樱桃 / 龙眼 / 荔枝
#
# 排列
#   alternate 互生  左右交替各长一片
#   opposite  对生  同一个高度左右各一片
#   pinnate   羽状复叶 —— **一眼就认得出来**：一根叶轴上排好几对小叶
#             （龙眼、荔枝本来就是羽状复叶，这是它们最好认的特征）
#
# 特征
#   three_vein    基部三出脉（枣树的标志）
#   petiole_wing  叶柄上的翼叶（柑橘类的标志）
#   drip_tip      尾尖（芒果、荔枝 —— 热带植物的"滴水尖"）
#
# 表：(叶形, 排列, 几片/几对, 宽长比, 特征集合)
TREE_LEAF_SHAPE = {
    "plum":        ("lanceolate", "alternate", 3, 0.27, ()),
    "apricot":     ("lanceolate", "alternate", 3, 0.29, ()),
    "jujube":      ("ovate",      "alternate", 4, 0.44, ("three_vein",)),
    "mandarin":    ("obovate",    "alternate", 3, 0.42, ("petiole_wing",)),
    "pear":        ("elliptic",   "alternate", 3, 0.38, ()),
    "peach":       ("lanceolate", "alternate", 3, 0.26, ()),
    "cherry":      ("elliptic",   "alternate", 4, 0.34, ("drip_tip",)),
    "pomegranate": ("ovate",      "opposite",  2, 0.40, ()),
    "longan":      ("elliptic",   "pinnate",   3, 0.40, ()),
    "lychee":      ("elliptic",   "pinnate",   4, 0.36, ("drip_tip",)),
    "persimmon":   ("elliptic",   "alternate", 3, 0.46, ()),
    "pomelo":      ("obovate",    "alternate", 2, 0.44, ("petiole_wing",)),
    "mango":       ("lanceolate", "alternate", 4, 0.24, ("drip_tip",)),
}

# 叶形的宽长比修正（表里的值再乘这个），以及叶尖的收束指数。
# 指数越大，两头收得越尖 —— 披针形的尖利、椭圆形的圆钝。
TREE_LEAF_FORM = {
    #             基部指数  尖端指数
    "lanceolate": (0.72,      0.72),
    "ovate":      (0.42,      1.15),
    "obovate":    (1.15,      0.42),
    "elliptic":   (0.85,      0.85),
}


# ----------------------------------------------------------------------
# 每棵树的木头长什么样
# ----------------------------------------------------------------------
# **(树皮暗, 树皮主, 树皮亮, 去皮色, 木板基色)**。
#
# 13 种树以前共用一种 `果木原木`。现在每棵树一套：原木 / 木头 /
# 去皮原木 / 去皮木 / 木板 / 楼梯 / 台阶 / 栅栏 / 栅栏门。
#
# <h3>色相要真的分得开</h3>
# 真树皮当然全是褐的，但 13 种褐色用眼睛分不出来 —— 第一版就是这样：
# 原木并排一摆全是同一块木头。原版区分木材靠的就是**明度 + 色相同时拉开**
# （桦木近白、云杉暗灰、丛林红、金合欢橙红、深色橡木近黑），这里照做：
#
#   李  灰白偏冷（最浅）        枣  深红              柿  近黑（最深）
#   杏  暖黄                  橘  姜黄              柚  黄绿
#   梨  浅灰                  桃  粉红褐            芒果 金黄
#   樱  深红褐                石榴 黄褐              龙眼 中褐
#   荔枝 红褐
#
# 去皮色一律比树皮浅而干净（就是"削掉一层皮"的样子），木板色取中间的暖调。
TREE_WOOD_LOOK = {
    #             树皮暗            树皮主            树皮亮            去皮              木板
    "plum":        ((76,  66,  60), (114,  98,  88), (150, 132, 120), (198, 178, 158), (186, 164, 144)),
    "apricot":     ((86,  58,  30), (128,  92,  48), (168, 126,  72), (206, 172, 118), (196, 160, 104)),
    "jujube":      ((48,  24,  20), (88,  46,  34), (124,  72,  52), (162, 104,  76), (150,  94,  66)),
    "mandarin":    ((66,  56,  22), (108,  92,  38), (148, 128,  62), (210, 180, 100), (200, 168,  88)),
    "pear":        ((92,  86,  72), (134, 124, 106), (172, 160, 140), (212, 198, 174), (204, 188, 164)),
    "peach":       ((84,  52,  46), (126,  82,  70), (166, 116,  98), (204, 164, 146), (192, 150, 132)),
    "cherry":      ((54,  26,  26), (96,  50,  46), (136,  82,  72), (178, 116, 104), (166, 104,  92)),
    "pomegranate": ((82,  66,  34), (124, 102,  54), (164, 138,  82), (206, 176, 112), (196, 164, 100)),
    "longan":      ((62,  44,  30), (100,  74,  50), (138, 106,  74), (186, 150, 104), (176, 140,  94)),
    "lychee":      ((58,  36,  26), (96,  62,  44), (134,  92,  66), (180, 132,  96), (170, 122,  86)),
    "persimmon":   ((34,  30,  28), (62,  56,  52), (96,  88,  82), (156, 138, 118), (146, 126, 106)),
    "pomelo":      ((64,  68,  34), (100, 106,  56), (138, 142,  84), (196, 190, 128), (186, 178, 116)),
    "mango":       ((74,  50,  20), (118,  84,  36), (158, 116,  56), (206, 164,  86), (196, 152,  74)),
}

# 木质方块的 id 后缀与中英文名模板。生成器照着这张表逐项产出。
#
# 名字用**模板**而不是"水果名 + 后缀"，因为中文的语序不是简单拼接：
# 原版的 "Oak Planks" 译作 "橡木木板"，"Stripped Oak Log" 译作
# "去皮橡木原木" —— 前缀在中间、修饰语在最前。直接拼会得到
# "枣木板""枣去皮原木"这种读着别扭的名字。
#
#   {w} = 水果的中文名（枣 / 桃 / 梨…）      {f} = 水果的英文名
#
# 第四列是"配方原料"：None 表示不做配方（去皮用斧头右键）。
TREE_WOOD_FORMS = [
    ("_log",           "{w}木原木",     "{f} Log",           None),
    ("_wood",          "{w}木",         "{f} Wood",          None),
    ("_stripped_log",  "去皮{w}木原木",  "Stripped {f} Log",  None),
    ("_stripped_wood", "去皮{w}木",     "Stripped {f} Wood", None),
    ("_planks",        "{w}木木板",     "{f} Planks",        "log"),
    ("_stairs",        "{w}木楼梯",     "{f} Stairs",        "planks"),
    ("_slab",          "{w}木台阶",     "{f} Slab",          "planks"),
    ("_fence",         "{w}木栅栏",     "{f} Fence",         "planks"),
    ("_fence_gate",    "{w}木栅栏门",   "{f} Fence Gate",    "planks"),
]

# ======================================================================
# 作物：种子 ⇄ 植株 ⇄ 收成
# ======================================================================
# (作物 id, 中文, 英文, 种子 id, 产物 id, 株型)
#
# 这三样东西一一对应：
#
#   种子   就是一个方块物品，右键耕地就种下"植株"
#   植株   ModCropBlock，八个生长阶段，长到第 8 阶段才能收
#   产物   收割时掉的东西（由 loot_table 决定：1 份产物 + 2~4 份种子）
#
# 所以玩家手上的每一粒种子都能自给自足地循环下去，
# 不需要任何工作台配方来"变"种子 —— 这正是取消那些充数配方的底气。
#
# 株型（habit）决定贴图画成什么样，一共八种，长得像的作物共用一种株型、
# 各自套自己的配色（见 tools/crop_art.py，完全程序化生成）：
#
#   grass   禾本：一根主茎挑着穗子      水稻 / 谷子 / 高粱 / 玉米
#   legume  豆科：矮丛 + 挂着豆荚        黄豆 / 绿豆 / 红豆 / 豌豆 / 蚕豆 / 豆角 / 花生
#   seedpod 籽用：细茎 + 顶端小蒴果      芝麻
#   leafy   叶菜：一层层向外摊开的叶球   白菜 / 小白菜 / 菠菜 / 芹菜 / 香菜 / 韭菜 / 葱
#   root    块根：贴地的羽状叶 + 露头的根 萝卜 / 芋头 / 红薯 / 山药 / 姜 / 蒜
#   bush    茄果：直立小灌木 + 垂着果实   辣椒 / 茄子 / 西红柿
#   vine    藤本：蔓生的藤 + 大叶片       黄瓜 / 冬瓜 / 丝瓜 / 苦瓜
#   fungus  菌：木头上簸开的耳片         木耳
CROPS = [
    # --- 禾本 ---
    ("rice",          "水稻",     "Rice",            "rice_seeds",         "paddy",        "grass"),
    ("millet",        "谷子",     "Millet",          "millet_seeds",       "millet_grass", "grass"),
    ("sorghum",       "高粱",     "Sorghum",         "sorghum_seeds",      "sorghum",      "grass"),
    ("corn",          "玉米",     "Corn",            "corn_seeds",         "corn",         "grass"),
    # --- 豆科 ---
    ("soybean",       "黄豆",     "Soybean",         "soybean_seeds",      "soybean",      "legume"),
    ("mung_bean",     "绿豆",     "Mung Bean",       "mung_bean_seeds",    "mung_bean",    "legume"),
    ("red_bean",      "红豆",     "Red Bean",        "red_bean_seeds",     "red_bean",     "legume"),
    ("pea",           "豌豆",     "Pea",             "pea_seeds",          "pea",          "legume"),
    ("broad_bean",    "蚕豆",     "Broad Bean",      "broad_bean_seeds",   "broad_bean",   "legume"),
    ("green_bean",    "豆角",     "Green Bean",      "green_bean_seeds",   "green_bean",   "legume"),
    ("peanut",        "花生",     "Peanut",          "peanut_seeds",       "peanut",       "legume"),
    # --- 籽用 ---
    ("sesame",        "芝麻",     "Sesame",          "sesame_seeds",       "sesame",       "seedpod"),
    # --- 块根 / 块茎 ---
    ("radish",        "萝卜",     "Radish",          "radish_seeds",       "radish",       "root"),
    ("taro",          "芋头",     "Taro",            "taro_seeds",         "taro",         "root"),
    ("sweet_potato",  "红薯",     "Sweet Potato",    "sweet_potato_slip",  "sweet_potato", "root"),
    ("chinese_yam",   "山药",     "Chinese Yam",     "chinese_yam_slip",   "chinese_yam",  "root"),
    ("ginger",        "姜",       "Ginger",          "ginger_seeds",       "ginger",       "root"),
    ("garlic",        "蒜",       "Garlic",          "garlic_seeds",       "garlic",       "root"),
    # --- 叶菜 ---
    ("napa_cabbage",  "白菜",     "Napa Cabbage",    "napa_cabbage_seeds", "napa_cabbage", "leafy"),
    ("bok_choy",      "小白菜",   "Bok Choy",        "bok_choy_seeds",     "bok_choy",     "leafy"),
    ("spinach",       "菠菜",     "Spinach",         "spinach_seeds",      "spinach",      "leafy"),
    ("celery",        "芹菜",     "Celery",          "celery_seeds",       "celery",       "leafy"),
    ("cilantro",      "香菜",     "Cilantro",        "cilantro_seeds",     "cilantro",     "leafy"),
    ("chive",         "韭菜",     "Chive",           "chive_seeds",        "chive",        "leafy"),
    ("scallion",      "葱",       "Scallion",        "scallion_seeds",     "scallion",     "leafy"),
    # --- 茄果 ---
    ("chili",         "辣椒",     "Chili",           "chili_seeds",        "chili",        "bush"),
    ("eggplant",      "茄子",     "Eggplant",        "eggplant_seeds",     "eggplant",     "bush"),
    ("tomato",        "西红柿",   "Tomato",          "tomato_seeds",       "tomato",       "bush"),
    # --- 藤本 ---
    ("cucumber",      "黄瓜",     "Cucumber",        "cucumber_seeds",     "cucumber",     "vine"),
    ("winter_melon",  "冬瓜",     "Winter Melon",    "winter_melon_seeds", "winter_melon", "vine"),
    ("luffa",         "丝瓜",     "Luffa",           "luffa_seeds",        "luffa",        "vine"),
    ("bitter_melon",  "苦瓜",     "Bitter Melon",    "bitter_melon_seeds", "bitter_melon", "vine"),
    # --- 菌 ---
    ("wood_ear",      "木耳",     "Wood Ear",        "wood_ear_spawn",     "wood_ear",     "fungus"),
]

# 野生作物会不会在野外生成、生成多稀罕。
# 每行 = (作物 id, 出现概率倒数, 每次生成几株)
# 数值是"village 里找得到"的尺度：罕见的值取 24~40，常见的取 8~14。
# 没列出来的作物默认不在野外生成（比如姜、蒜本来就是靠留种，不野生）。
WILD_CROPS = [
    ("rice",         16, 3), ("millet",        14, 3), ("sorghum",      18, 2),
    ("corn",         26, 2),
    ("soybean",      12, 3), ("mung_bean",     16, 3), ("red_bean",     16, 3),
    ("pea",          14, 3), ("broad_bean",    20, 2), ("green_bean",   18, 2),
    ("peanut",       24, 2),
    ("sesame",       22, 2),
    ("radish",       10, 3), ("taro",          18, 2), ("sweet_potato", 14, 2),
    ("chinese_yam",  24, 2),
    ("napa_cabbage", 12, 2), ("bok_choy",      10, 3), ("spinach",      12, 3),
    ("celery",       16, 2), ("cilantro",     10, 3), ("chive",        14, 3),
    ("scallion",     12, 3),
    ("chili",        20, 2), ("eggplant",      22, 2), ("tomato",       26, 2),
    ("cucumber",     16, 2), ("winter_melon",  28, 1), ("luffa",        22, 2),
    ("bitter_melon", 24, 2),
    ("wood_ear",     20, 2),
]

# 野生作物长在什么生物群系里。用原版标签，跨模组也稳。
# （26.1 里没有 is_swamp 这个标签，湿地就用河岸标签；这四个是最接近的现成标签。）
#   temperate 温带：森林
#   tropical  热带：丛林
#   dry       干旱：热带草原
#   wet       湿地：河岸
WILD_BIOMES = {
    "temperate": "#minecraft:is_forest",
    "tropical": "#minecraft:is_jungle",
    "dry": "#minecraft:is_savanna",
    "wet": "#minecraft:is_river",
}

# 每种野生作物归到哪一类群系。归得细一点，玩家跑不同地方能采到不同的东西。
WILD_HABITAT = {
    "rice": "wet", "millet": "dry", "sorghum": "dry", "corn": "temperate",
    "soybean": "temperate", "mung_bean": "dry", "red_bean": "temperate",
    "pea": "temperate", "broad_bean": "temperate", "green_bean": "tropical",
    "peanut": "dry",
    "sesame": "dry",
    "radish": "temperate", "taro": "wet", "sweet_potato": "temperate",
    "chinese_yam": "temperate",
    "napa_cabbage": "temperate", "bok_choy": "temperate", "spinach": "temperate",
    "celery": "wet", "cilantro": "temperate", "chive": "temperate",
    "scallion": "temperate",
    "chili": "tropical", "eggplant": "tropical", "tomato": "temperate",
    "cucumber": "temperate", "winter_melon": "tropical", "luffa": "tropical",
    "bitter_melon": "tropical",
    "wood_ear": "wet",
}
