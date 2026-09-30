package com.ctf.chinese_traditional_food.common.food;

import com.ctf.chinese_traditional_food.registry.ModMobEffects;
import java.util.List;
import java.util.stream.Stream;
import net.minecraft.world.effect.MobEffects;

/**
 * 菜品效果预设表。
 *
 * <p>名称与 <code>tools/content_data.py</code> 里 DISHES 表的最后一列一一对应，
 * 由生成器写进 {@code ModItems}。原版已有对应物的效果直接复用原版
 * （省一个注册项，也方便 JEI 之类的模组识别）。</p>
 *
 * <p>单一效果与组合效果都在这里，菜谱只写名字、不写具体数值，
 * 将来调平衡只改这一个文件。</p>
 */
public final class DishEffects {
    // ==================================================================
    // 单效果
    // ==================================================================

    /** 无效果（原味食材，例如生豆腐）。 */
    public static final List<ServeEffect> NONE = List.of();

    /** 团圆（生命恢复）5 秒。 */
    public static final List<ServeEffect> REUNION = List.of(ServeEffect.of(ModMobEffects.REUNION, 5));
    /** 步步高升（免疫摔落）8 秒。 */
    public static final List<ServeEffect> RISE_UP = List.of(ServeEffect.of(ModMobEffects.RISE_UP, 8));
    /** 圆满（额外经验）10 秒，并附带原版幸运 I。 */
    public static final List<ServeEffect> PERFECTION = List.of(
            ServeEffect.of(ModMobEffects.PERFECTION, 10),
            ServeEffect.of(MobEffects.LUCK, 10));

    /** 暖身（抗寒）= 抗性提升 I，10 秒。 */
    public static final List<ServeEffect> WARMTH = List.of(ServeEffect.of(MobEffects.RESISTANCE, 10));
    /** 提神 = 速度 I，10 秒。 */
    public static final List<ServeEffect> REFRESH = List.of(ServeEffect.of(MobEffects.SPEED, 10));
    /** 滋补 = 生命提升 I，30 秒。 */
    public static final List<ServeEffect> NOURISH = List.of(ServeEffect.of(MobEffects.HEALTH_BOOST, 30));
    /** 饱足 = 饱和 I，5 秒。 */
    public static final List<ServeEffect> SATED = List.of(ServeEffect.of(MobEffects.SATURATION, 5));
    /** 爽脆 = 急迫 I，8 秒。 */
    public static final List<ServeEffect> CRISP = List.of(ServeEffect.of(MobEffects.HASTE, 8));

    // ==================================================================
    // 组合效果（硬菜 / 大菜用，吃一道顶两道）
    // ==================================================================

    public static final List<ServeEffect> NOURISH_WARMTH = join(NOURISH, WARMTH);
    public static final List<ServeEffect> NOURISH_SATED = join(NOURISH, SATED);
    public static final List<ServeEffect> REFRESH_NOURISH = join(REFRESH, NOURISH);
    public static final List<ServeEffect> REFRESH_SATED = join(REFRESH, SATED);
    public static final List<ServeEffect> REUNION_SATED = join(REUNION, SATED);
    public static final List<ServeEffect> PERFECTION_NOURISH = join(PERFECTION, NOURISH);
    public static final List<ServeEffect> PERFECTION_SATED = join(PERFECTION, SATED);
    public static final List<ServeEffect> WARMTH_REFRESH = join(WARMTH, REFRESH);
    public static final List<ServeEffect> WARMTH_NOURISH = join(WARMTH, NOURISH);

    // 早餐 / 小吃的组合：都是"顶饱 + 一点小收益"，符合早点与街头小吃的定位
    /** 饱足 + 提神（煎饼果子、小笼包这类"吃完就能出门干活"的）。 */
    public static final List<ServeEffect> SATED_REFRESH = join(SATED, REFRESH);
    /** 饱足 + 滋补（肉夹馍这类扎实的）。 */
    public static final List<ServeEffect> SATED_NOURISH = join(SATED, NOURISH);
    /** 爽脆 + 提神（油条豆浆、豆浆油条）。 */
    public static final List<ServeEffect> CRISP_REFRESH = join(CRISP, REFRESH);

    /**
     * 佛跳墙、孔府一品锅这类压轴大菜：滋补 + 暖身 + 饱足，一次给满。
     */
    public static final List<ServeEffect> FEAST = join(join(NOURISH, WARMTH), SATED);

    private static List<ServeEffect> join(List<ServeEffect> a, List<ServeEffect> b) {
        return Stream.concat(a.stream(), b.stream()).toList();
    }

    private DishEffects() {}
}
