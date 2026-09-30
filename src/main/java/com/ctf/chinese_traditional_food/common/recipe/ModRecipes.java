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
            new Entry("chinese_traditional_food:sesame", "sesame_oil", 1, "sesame_paste", 0.35F, 120),
            new Entry("chinese_traditional_food:red_bean", "bean_paste", 1, "", 0.00F, 140),
            new Entry("chinese_traditional_food:soybean", "soybean", 1, "", 0.00F, 0)
    );

    /** 脱壳机：带壳谷物 -> 米。需要红石信号。 */
    public static final List<Entry> SHELLING = List.of(
            new Entry("chinese_traditional_food:paddy", "rice", 1, "rice_bran", 0.45F, 120),
            new Entry("chinese_traditional_food:millet_grass", "millet", 1, "rice_bran", 0.30F, 100)
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
