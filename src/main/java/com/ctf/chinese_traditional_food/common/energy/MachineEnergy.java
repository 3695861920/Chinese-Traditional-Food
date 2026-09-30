package com.ctf.chinese_traditional_food.common.energy;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

/**
 * 电力设备的统一数值表。
 *
 * <p>把数字集中在一处，是为了让"发电机出多少电、机器吃多少电"这两件事
 * 永远对得上 —— 分开写在两个类里迟早会调歪。</p>
 *
 * <h2>一套账</h2>
 * <ul>
 *   <li>发电机烧燃料，恒功率输出 {@link #GENERATOR_OUTPUT} FE/t；</li>
 *   <li>机器每 tick 吃 {@link #ENERGY_PER_TICK} FE/t；</li>
 *   <li>一个批次 = {@link #BATCH_SIZE} 个物品、{@link #BATCH_TICKS} tick（10 秒）；
 *       所以一批正好吃掉 {@code 10 × 200 = 2000} FE。</li>
 * </ul>
 *
 * <p>换算一下：一块煤炭在原版熔炉里烧 1600 tick，在这里就能发出
 * {@code 1600 × 40 = 64000} FE —— 够机器跑 32 批、加工 256 个物品。
 * 数字不夸张，但也不至于让人为了磨一袋面粉砍半天树。</p>
 */
public final class MachineEnergy {
    /** 发电机输出功率（FE/t）。 */
    public static final int GENERATOR_OUTPUT = 40;

    /** 发电机内部缓冲（FE）。一桶岩浆的零头都不到，纯粹为了削峰。 */
    public static final int GENERATOR_BUFFER = 4000;

    /** 一个批次加工多少个物品。 */
    public static final int BATCH_SIZE = 8;

    /** 一个批次要跑多少 tick（200 tick = 10 秒）。 */
    public static final int BATCH_TICKS = 200;

    /** 机器运行时的耗电（FE/t）。一批正好 {@code 10 × 200 = 2000} FE。 */
    public static final int ENERGY_PER_TICK = 10;

    /** 一个批次的总耗电（FE），仅供界面 / 提示显示。 */
    public static final int ENERGY_PER_BATCH = ENERGY_PER_TICK * BATCH_TICKS;

    /** 机器内部缓冲（FE）。够存 2 批，避免发电机稍微打个嗝机器就停。 */
    public static final int MACHINE_BUFFER = ENERGY_PER_BATCH * 2;

    /**
     * 同步给界面的整数上限。
     *
     * <p>原版的容器数据同步走的是 <b>short</b>（±32767）。我们的缓冲只有
     * 4000 FE、燃烧时间最长也就岩浆桶的 20000 tick，**都在范围内**，
     * 所以直接把原值丢进 {@code ContainerData} 就行，不必折算。
     * 万一以后把缓冲调大到超过这个范围，就得在这里改回按比例折算。</p>
     */
    public static final int SYNC_SAFE_MAX = Short.MAX_VALUE;

    /** 把要放进 {@code ContainerData} 的值夹到安全范围。 */
    public static int clampForSync(int value) {
        return Math.max(0, Math.min(SYNC_SAFE_MAX, value));
    }

    /** 电量文案，例如 {@code 1234 / 4000 FE}。 */
    public static MutableComponent describe(int energy, int capacity) {
        return Component.translatable("tooltip.chinese_traditional_food.energy_amount",
                energy, capacity);
    }

    private MachineEnergy() {}
}
