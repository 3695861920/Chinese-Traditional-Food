package com.ctf.chinese_traditional_food.common.food;

import com.ctf.chinese_traditional_food.registry.ModMobEffects;
import java.util.List;
import net.minecraft.world.effect.MobEffects;

/**
 * 菜品效果预设表。
 *
 * <p>命名与 <code>docs/物品清单.md</code> 的「自定义状态效果一览」一一对应。
 * 原版已有对应物的效果直接复用原版（省一个注册项，也方便 JEI 之类的模组识别）。</p>
 */
public final class DishEffects {
    /** 无任何效果（原味食材，例如生豆腐）。 */
    public static final List<ServeEffect> NONE = List.of();

    // ---- 自定义效果（见 ModMobEffects） ----

    /** 团圆（生命恢复）5 秒。 */
    public static final List<ServeEffect> REUNION = List.of(ServeEffect.of(ModMobEffects.REUNION, 5));
    /** 步步高升（免疫摔落）8 秒。 */
    public static final List<ServeEffect> RISE_UP = List.of(ServeEffect.of(ModMobEffects.RISE_UP, 8));
    /** 圆满（额外经验）10 秒，并附带原版幸运 I。 */
    public static final List<ServeEffect> PERFECTION = List.of(
            ServeEffect.of(ModMobEffects.PERFECTION, 10),
            ServeEffect.of(MobEffects.LUCK, 10));

    // ---- 原版效果模拟 ----

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

    /** 组合技：滋补 + 暖身。 */
    public static final List<ServeEffect> NOURISH_AND_WARMTH = concat(NOURISH, WARMTH);
    /** 组合技：滋补 + 饱足。 */
    public static final List<ServeEffect> NOURISH_AND_SATED = concat(NOURISH, SATED);

    private static List<ServeEffect> concat(List<ServeEffect> a, List<ServeEffect> b) {
        return java.util.stream.Stream.concat(a.stream(), b.stream()).toList();
    }

    private DishEffects() {}
}
