package com.ctf.chinese_traditional_food.registry;

import net.minecraft.world.food.FoodProperties;

/**
 * 食物属性表（饥饿值 / 饱和度修饰符 / 是否随时可食）。
 *
 * <p>饱和度实际值 = {@code min(2 × 饥饿值 × 饱和度修饰符, 当前饥饿值)}，
 * 因此修饰符 0.5 表示"回多少饥饿就补多少饱和"，1.0 表示双倍。</p>
 */
public final class ModFoods {
    /** 麻婆豆腐：7 饥饿 / 1.0 饱和（对照：熟牛排 8 / 0.8）。 */
    public static final FoodProperties MAPO_TOFU = new FoodProperties.Builder()
            .nutrition(7)
            .saturationModifier(1.0F)
            .build();

    /** 豆腐：生吃也行，3 饥饿 / 0.3 饱和（对照：胡萝卜 3 / 0.6，豆腐更"清汤寡水"）。 */
    public static final FoodProperties TOFU = new FoodProperties.Builder()
            .nutrition(3)
            .saturationModifier(0.3F)
            .build();

    private ModFoods() {}
}
