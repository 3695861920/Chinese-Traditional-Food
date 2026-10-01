package com.ctf.chinese_traditional_food.common.compat.jei;

import net.minecraft.network.chat.Component;

/**
 * JEI 上的几句提示文案。
 *
 * <p>集中放在这里有两个好处：一是键名不会到处飘（改文案只改一处），
 * 二是这几个键和 {@code lang} 文件里的能一眼对上。</p>
 *
 * <p>耗时统一换算成"秒"，因为玩家看到 {@code 260} 这种数字没感觉，
 * 看到"13.0 秒"才知道大概要等多久。</p>
 */
final class JeiTexts {

    /** 一条配方要多久。 */
    static Component duration(int ticks) {
        return Component.translatable("jei.chinese_traditional_food.duration",
                String.format("%.1f", ticks / 20.0));
    }

    /** 副产物提示（只有概率，因为是什么东西已经在槽里画出来了）。 */
    static Component byproduct(float chance) {
        return Component.translatable("jei.chinese_traditional_food.byproduct",
                Math.round(chance * 100.0F));
    }

    /** 案板提示：这一条得拿着刀才好使。 */
    static Component needsKnife() {
        return Component.translatable("jei.chinese_traditional_food.needs_knife");
    }

    /** 锅类的统一提示：这东西怎么用。 */
    static Component potHint() {
        return Component.translatable("jei.chinese_traditional_food.pot_hint");
    }

    private JeiTexts() {}
}
