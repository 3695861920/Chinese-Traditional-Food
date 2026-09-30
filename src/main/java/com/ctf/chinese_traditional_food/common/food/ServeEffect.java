package com.ctf.chinese_traditional_food.common.food;

import net.minecraft.core.Holder;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;

/**
 * "取食一份菜时会施加的效果"的描述。
 *
 * <p>为什么不直接存 {@link MobEffectInstance}？
 * 因为物品是在 {@code DeferredRegister} 的注册阶段构造的，那时注册表还没冻结完，
 * 直接 new 出实例容易踩坑。这里只存 {@link Holder} 和时长，
 * 真正实例化推迟到"玩家真的吃了一口"的时刻。</p>
 *
 * @param effect        状态效果（可以用 DeferredHolder，它实现了 Holder）
 * @param durationTicks 持续 tick 数（20 tick = 1 秒）
 * @param amplifier     等级，0 = I 级
 * @param chance        生效概率，1.0 = 必定生效
 */
public record ServeEffect(Holder<MobEffect> effect, int durationTicks, int amplifier, float chance) {

    /** 必定生效、I 级的快捷构造：{@code ServeEffect.of(ModMobEffects.REUNION, 5)} = 团圆 5 秒。 */
    public static ServeEffect of(Holder<MobEffect> effect, int seconds) {
        return new ServeEffect(effect, seconds * 20, 0, 1.0F);
    }

    /** 带概率的快捷构造。 */
    public static ServeEffect chanced(Holder<MobEffect> effect, int seconds, int amplifier, float chance) {
        return new ServeEffect(effect, seconds * 20, amplifier, chance);
    }

    /** 按概率产出一个可施加的效果实例；未命中返回 {@code null}。 */
    public MobEffectInstance roll(net.minecraft.util.RandomSource random) {
        if (this.chance < 1.0F && random.nextFloat() >= this.chance) {
            return null;
        }
        return new MobEffectInstance(this.effect, this.durationTicks, this.amplifier);
    }
}
