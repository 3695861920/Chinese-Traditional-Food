package com.ctf.chinese_traditional_food.common.recipe;

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
            new Entry("minecraft:wheat", "flour", 2, "", 0.00F, 100),
            new Entry("chinese_traditional_food:rice", "rice_flour", 2, "", 0.00F, 100),
            new Entry("chinese_traditional_food:glutinous_rice", "glutinous_rice_flour", 2, "", 0.00F, 100),
            new Entry("chinese_traditional_food:corn", "corn_flour", 2, "", 0.00F, 100),
            new Entry("minecraft:potato", "starch", 2, "", 0.00F, 100),
            new Entry("chinese_traditional_food:sichuan_peppercorn", "pepper_powder", 2, "", 0.00F, 80),
            new Entry("chinese_traditional_food:dried_chili", "chili_powder", 2, "", 0.00F, 80),
            new Entry("chinese_traditional_food:sesame", "sesame_oil", 1, "sesame_paste", 0.35F, 120)
    );

    /** 脱壳机：带壳谷物 -> 米。需要红石信号。 */
    public static final List<Entry> SHELLING = List.of(
            new Entry("chinese_traditional_food:paddy", "rice", 1, "rice_bran", 0.45F, 120),
            new Entry("chinese_traditional_food:millet_grass", "millet", 1, "rice_bran", 0.30F, 100)
    );

    /** 蒸笼的锅谱：面点、糕饼这类靠蒸汽的东西。 */
    public static final List<CookEntry> STEAMER = List.of(
            new CookEntry("mantou", 2, 120, List.of("chinese_traditional_food:flour")),
            new CookEntry("zao_zong", 2, 140, List.of("chinese_traditional_food:glutinous_rice")),
            new CookEntry("rice_cake", 2, 130, List.of("chinese_traditional_food:rice_flour")),
            new CookEntry("dou_sha_bao", 2, 150, List.of("chinese_traditional_food:bean_paste")),
            new CookEntry("baozi", 2, 160, List.of("minecraft:porkchop")),
            new CookEntry("xiao_long_bao", 2, 170, List.of("#c:raw_meat")),
            new CookEntry("steamed_pumpkin", 1, 110, List.of("chinese_traditional_food:sweet_potato")),
            new CookEntry("baked_sweet_potato", 1, 110, List.of("chinese_traditional_food:sweet_potato")),
            new CookEntry("xiajiao_huang", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("jiaozi", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("nian_gao", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("chun_juan", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("tang_yuan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("zhima_tangyuan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("dousha_tangyuan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("huasheng_tangyuan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("qing_tuan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("ai_jiao", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("rou_zong", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("dousha_zong", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("qiao_guo", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("lianrong_yuebing", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("dousha_yuebing", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("wuren_yuebing", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("danyue_yuebing", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("chongyang_gao", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("hua_juan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("jianbing", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("chashao_bao", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("tangyuan", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("kao_lengmian", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("roujiamo", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("jian_gao", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("guo_tie", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("shaomai", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil")),
            new CookEntry("tanghulu", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("shao_bing", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("zhima_tuan", 1, 160, List.of("chinese_traditional_food:bean_paste", "minecraft:sugar", "chinese_traditional_food:red_date", "chinese_traditional_food:osmanthus")),
            new CookEntry("zongzi_xian", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "chinese_traditional_food:sesame_oil"))
    );

    /** 汤锅的锅谱：炖、汤、饭这类久煮的东西。 */
    public static final List<CookEntry> SOUP_POT = List.of(
            new CookEntry("tofu", 2, 150, List.of("chinese_traditional_food:soybean", "chinese_traditional_food:soybean", "chinese_traditional_food:salt")),
            new CookEntry("bean_paste", 2, 200, List.of("chinese_traditional_food:red_bean", "chinese_traditional_food:red_bean", "minecraft:sugar")),
            new CookEntry("soy_sauce", 1, 180, List.of("chinese_traditional_food:soybean", "minecraft:wheat", "chinese_traditional_food:salt")),
            new CookEntry("vinegar", 1, 160, List.of("chinese_traditional_food:rice", "minecraft:sugar")),
            new CookEntry("cooking_wine", 1, 170, List.of("chinese_traditional_food:rice", "chinese_traditional_food:rice", "chinese_traditional_food:salt")),
            new CookEntry("doubanjiang", 1, 200, List.of("chinese_traditional_food:broad_bean", "chinese_traditional_food:chili", "chinese_traditional_food:salt")),
            new CookEntry("douchi", 2, 170, List.of("chinese_traditional_food:black_bean", "chinese_traditional_food:salt")),
            new CookEntry("fermented_tofu", 2, 190, List.of("chinese_traditional_food:tofu", "chinese_traditional_food:salt", "chinese_traditional_food:cooking_wine")),
            new CookEntry("sweet_bean_sauce", 1, 180, List.of("chinese_traditional_food:flour", "chinese_traditional_food:salt", "minecraft:sugar")),
            new CookEntry("oyster_sauce", 1, 170, List.of("minecraft:kelp", "chinese_traditional_food:salt", "minecraft:sugar")),
            new CookEntry("stock", 2, 200, List.of("minecraft:bone", "minecraft:bone", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger")),
            new CookEntry("pickled_vegetable", 2, 180, List.of("chinese_traditional_food:napa_cabbage", "chinese_traditional_food:salt", "chinese_traditional_food:salt")),
            new CookEntry("dou_ya", 3, 160, List.of("chinese_traditional_food:soybean", "chinese_traditional_food:salt")),
            new CookEntry("egg_drop_soup", 1, 120, List.of("chinese_traditional_food:stock")),
            new CookEntry("winter_melon_soup", 1, 130, List.of("chinese_traditional_food:napa_cabbage")),
            new CookEntry("red_bean_soup", 1, 160, List.of("chinese_traditional_food:red_bean")),
            new CookEntry("mung_bean_soup", 1, 150, List.of("chinese_traditional_food:mung_bean")),
            new CookEntry("zhou_congee", 1, 140, List.of("chinese_traditional_food:rice")),
            new CookEntry("xiaomi_zhou", 1, 130, List.of("chinese_traditional_food:millet")),
            new CookEntry("lotus_seed_soup", 1, 170, List.of("chinese_traditional_food:lotus_seed")),
            new CookEntry("yam_ribs_soup", 1, 175, List.of("chinese_traditional_food:chinese_yam")),
            new CookEntry("wonton_soup", 1, 165, List.of("#c:raw_meat")),
            new CookEntry("suantang", 1, 110, List.of("chinese_traditional_food:vinegar")),
            new CookEntry("doufunao", 1, 150, List.of("chinese_traditional_food:soybean")),
            new CookEntry("jiuzhuan_dachang", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("congsao_haishen", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("naitang_pucai", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("kongfu_yipinguo", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("shuizhu_yu", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("maoxue_wang", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("kaishui_baicai", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("laohuo_liangtang", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("zeze_bao", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("yuntun_mian", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("dazhu_gansi", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("wensi_doufu", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("fotiaoqiang", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("babao_hongxun_fan", 1, 220, List.of("chinese_traditional_food:rice", "chinese_traditional_food:soy_sauce", "minecraft:carrot", "chinese_traditional_food:scallion")),
            new CookEntry("jitang_tun_haibang", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("xuecai_huangyu", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("qingtang_yueji", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("zuan_yuchi", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("huizhou_yipinguo", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("huangshan_dunge", 1, 260, List.of("chinese_traditional_food:stock", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark")),
            new CookEntry("wenzheng_shansun", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("qiaoya_mian", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("laba_zhou", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("laba_suan", 2, 240, List.of("chinese_traditional_food:garlic", "chinese_traditional_food:vinegar", "chinese_traditional_food:vinegar")),
            new CookEntry("yangrou_tang", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("chao_gan", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("huntun", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("mixian", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("chao_mian", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot")),
            new CookEntry("liangpi", 1, 200, List.of("chinese_traditional_food:stock", "chinese_traditional_food:scallion", "chinese_traditional_food:ginger", "minecraft:carrot"))
    );

    /** 炒锅的锅谱：炒、煎、整菜这类猛火的东西。 */
    public static final List<CookEntry> WOK = List.of(
            new CookEntry("five_spice_powder", 2, 140, List.of("chinese_traditional_food:star_anise", "chinese_traditional_food:cinnamon_bark", "chinese_traditional_food:cumin", "chinese_traditional_food:sichuan_peppercorn", "chinese_traditional_food:bay_leaf")),
            new CookEntry("sesame_paste", 1, 140, List.of("chinese_traditional_food:sesame", "chinese_traditional_food:sesame")),
            new CookEntry("chili_oil", 1, 120, List.of("chinese_traditional_food:chili_powder", "chinese_traditional_food:sesame_oil")),
            new CookEntry("scrambled_egg", 1, 90, List.of("minecraft:egg")),
            new CookEntry("tomato_egg", 1, 110, List.of("chinese_traditional_food:tomato")),
            new CookEntry("dry_fried_beans", 1, 120, List.of("chinese_traditional_food:green_bean")),
            new CookEntry("stir_fried_pea", 1, 110, List.of("chinese_traditional_food:pea")),
            new CookEntry("chive_egg", 1, 105, List.of("chinese_traditional_food:chive")),
            new CookEntry("braised_bamboo", 1, 125, List.of("chinese_traditional_food:bamboo_shoot")),
            new CookEntry("twice_cooked_pork", 1, 140, List.of("#c:raw_meat")),
            new CookEntry("chou_doufu", 1, 150, List.of("chinese_traditional_food:tofu")),
            new CookEntry("youtiao", 2, 100, List.of("chinese_traditional_food:flour")),
            new CookEntry("mahuadou", 2, 110, List.of("chinese_traditional_food:rice_flour")),
            new CookEntry("tangcu_liyu", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("youbao_shuangcui", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("guota_doufu", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("dezhou_paji", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("sixi_wanzi", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("zaoliu_yupian", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("mapo_tofu", 1, 200, List.of("chinese_traditional_food:tofu", "chinese_traditional_food:doubanjiang", "chinese_traditional_food:sichuan_peppercorn", "chinese_traditional_food:chili_powder")),
            new CookEntry("huiguo_rou", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("fuqi_feipian", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("gongbao_jiding", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("yuxiang_rousi", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("laziji", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("dongpo_zhouzi", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("baiqie_ji", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("mizhi_chashao", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("qingzheng_shibanyu", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("shaoe", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("ganchao_niuhe", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("baozhi_liaoshen", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("songshu_guiyu", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("dazhaxie", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("yangzhou_shizitou", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("jinling_yanshuiya", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("wuxi_jiangpaigu", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("qingzheng_shiyu", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("shuijing_yaorou", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("biluo_xiaren", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("lizhi_rou", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("zui_paigu", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("zhan_hetianji", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("wuyi_xune", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("xiangnan_ribao", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("xihu_cuyu", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("dongpo_rou", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("longjing_xiaren", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("gancai_menrou", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("wuwei_jianxie", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("duojiao_yutou", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("maoshi_hongshaorou", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("lajiao_chaorou", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("dongan_ziji", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("lawei_hezheng", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("xiangxi_waipocai", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("jiangbanya", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("yongzhou_xueya", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("zhuxue_wanzi", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("chou_guiyu", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("humao_doufu", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("fangla_yu", 1, 160, List.of("minecraft:cod", "chinese_traditional_food:ginger", "chinese_traditional_food:scallion", "chinese_traditional_food:cooking_wine")),
            new CookEntry("mizhi_hongyu", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("qingzheng_shiji", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("la_rou", 1, 200, List.of("minecraft:beef", "chinese_traditional_food:soy_sauce", "chinese_traditional_food:star_anise", "chinese_traditional_food:ginger")),
            new CookEntry("juhua_jiu", 1, 100, List.of("chinese_traditional_food:osmanthus", "chinese_traditional_food:cooking_wine", "minecraft:sugar", "chinese_traditional_food:red_date")),
            new CookEntry("doujiang", 1, 100, List.of("chinese_traditional_food:osmanthus", "chinese_traditional_food:cooking_wine", "minecraft:sugar", "chinese_traditional_food:red_date")),
            new CookEntry("youtiao_doujiang", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("chuan_chuan", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil")),
            new CookEntry("chuanbei_liangfen", 1, 120, List.of("minecraft:porkchop", "chinese_traditional_food:scallion", "chinese_traditional_food:garlic", "chinese_traditional_food:sesame_oil"))
    );

    /** 案板切割。先匹配具体物品、再匹配标签，所以顺序有意义。 */
    public static final List<CuttingEntry> CUTTING = List.of(
            new CuttingEntry("chinese_traditional_food:tofu", "shredded_tofu", true, 0),
            new CuttingEntry("chinese_traditional_food:wood_ear", "shredded_vegetable", true, 0),
            new CuttingEntry("chinese_traditional_food:bamboo_shoot", "shredded_vegetable", true, 0),
            new CuttingEntry("#c:raw_fish", "fish_fillet", true, 0),
            new CuttingEntry("#c:raw_meat", "shredded_meat", true, 0),
            new CuttingEntry("chinese_traditional_food:fermented_tofu", "shredded_tofu", false, 20),
            new CuttingEntry("#c:vegetables", "shredded_vegetable", true, 0)
    );

    private ModRecipes() {}
}
