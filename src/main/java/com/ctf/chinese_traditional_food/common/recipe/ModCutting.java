package com.ctf.chinese_traditional_food.common.recipe;

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
            new Entry("chinese_traditional_food:tofu", "shredded_tofu", true, 0),
            new Entry("chinese_traditional_food:wood_ear", "shredded_vegetable", true, 0),
            new Entry("chinese_traditional_food:bamboo_shoot", "shredded_vegetable", true, 0),
            new Entry("#c:raw_fish", "fish_fillet", true, 0),
            new Entry("#c:raw_meat", "shredded_meat", true, 0),
            new Entry("chinese_traditional_food:fermented_tofu", "shredded_tofu", false, 20),
            new Entry("#c:vegetables", "shredded_vegetable", true, 0),
    );

    private ModCutting() {}
}
