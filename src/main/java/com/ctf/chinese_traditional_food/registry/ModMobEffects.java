package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 本模组的自定义状态效果（Buff）。
 *
 * <p>只有"名字有梗、原版没有对应物"的效果才在这里注册；
 * 暖身 / 提神 / 滋补 / 饱足 / 爽脆 等直接用原版效果模拟，见
 * {@link com.ctf.chinese_traditional_food.common.food.DishEffects}。</p>
 */
public final class ModMobEffects {
    public static final DeferredRegister<MobEffect> MOB_EFFECTS =
            DeferredRegister.create(BuiltInRegistries.MOB_EFFECT, ChineseTraditionalFood.MOD_ID);

    /**
     * 团圆 —— 食用饺子 / 汤圆 / 粽子等"团圆"类食物后获得。
     * 机制：每秒恢复 1 点生命（≈ 生命恢复 I，但持续更久）。
     */
    public static final DeferredHolder<MobEffect, MobEffect> REUNION =
            MOB_EFFECTS.register("reunion", () -> new MobEffect(MobEffectCategory.BENEFICIAL, 0xE24A3B) {
                @Override
                public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
                    float amount = (1.0F + amplifier) / 20.0F; // 每秒 (1 + 等级) 点生命
                    if (entity.getHealth() < entity.getMaxHealth()) {
                        entity.heal(amount);
                    }
                    return true;
                }
            });

    /**
     * 步步高升 —— 食用年糕 / 重阳糕后获得。
     * 机制：持续时间内免疫摔落伤害（脚踩得更高，自然摔不着）。
     */
    public static final DeferredHolder<MobEffect, MobEffect> RISE_UP =
            MOB_EFFECTS.register("rise_up", () -> new MobEffect(MobEffectCategory.BENEFICIAL, 0xF2C14E) {
                @Override
                public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
                    entity.resetFallDistance();
                    return true;
                }
            });

    /**
     * 圆满 —— 食用月饼后获得。
     * 机制：每秒有 20% 的概率获得 1 点经验（"月圆人圆事事圆满"）。
     */
    public static final DeferredHolder<MobEffect, MobEffect> PERFECTION =
            MOB_EFFECTS.register("perfection", () -> new MobEffect(MobEffectCategory.BENEFICIAL, 0xB8860B) {
                @Override
                public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
                    if (entity instanceof Player player
                            && level.getRandom().nextFloat() < 0.2F + 0.1F * amplifier) {
                        player.giveExperiencePoints(1);
                    }
                    return true;
                }
            });

    public static void register(IEventBus modBus) {
        MOB_EFFECTS.register(modBus);
    }

    private ModMobEffects() {}
}
