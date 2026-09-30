package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 「灶上的锅具」的公共方块实体：炒锅 / 蒸笼 / 汤锅。
 *
 * <h2>动力来自热源，不是电</h2>
 * 它们把 {@link #hasPower()} 覆写成"下面那一格有热源且够热"，
 * 于是主循环（推进度、结算批次）完全套用 {@code AbstractProcessorBlockEntity}，
 * 一行都不用重写。{@link #consumePower()} 是空实现 ——
 * 电是被下面的电磁炉吃掉的，锅具只是"借用"。
 *
 * <h2>四个原料槽</h2>
 * 一口锅只放得下一样东西太憋屈，所以给了 {@value #INPUT_SLOTS} 个进料槽：
 * 备着几样配菜轮流下锅，比反复开界面倒进倒出顺手得多。
 * 机器一次只做一件事（进度条只有一条），所以**先做靠前的那一格**，
 * 想让某样先下锅就把它放在前面。
 *
 * <h2>界面</h2>
 * 那根竖条在电动设备上是电量，在这里是<b>热度</b>：
 * {@link #getPowerForDisplay()} 返回 0 或满值（有火 / 没火），
 * {@link #heatPowered()} 返回 true，界面据此把文案换成"热力"，
 * 并且会换成四格版的布局（见 {@code ProcessorScreen}）。
 */
public abstract class AbstractHeatProcessorBlockEntity extends AbstractProcessorBlockEntity {

    /** 灶上锅具的进料槽数量。 */
    public static final int INPUT_SLOTS = 4;

    protected AbstractHeatProcessorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    /** 这一台是哪一类灶活。 */
    @Override
    protected abstract Kind kind();

    /** 四个进料槽（比电动设备多，见类注释）。 */
    @Override
    public int inputSlots() {
        return INPUT_SLOTS;
    }

    /**
     * 锅里有没有活等着做。
     *
     * <p>电磁炉靠这个决定要不要给上面的锅供电 —— 锅里没东西就不该白烧电。</p>
     */
    public boolean wantsHeat() {
        return this.hasWork();
    }

    // ------------------------------------------------------------------
    // 与电动设备不同的数值
    // ------------------------------------------------------------------

    /**
     * 灶活是<b>一份一份做</b>的，不是一批一批。
     *
     * <p>电动设备一次推 8 个（磨粉、脱壳本来就是连续作业）；而炒锅、蒸笼
     * 现实里就是一份一份来的 —— 所以批次大小固定 1，耗时用
     * {@link #HEAT_TICKS_PER_ITEM}。这样界面上的进度条读起来也更自然：
     * 一格一格走完就是一道菜。</p>
     */
    @Override
    protected int batchSize() {
        return 1;
    }

    /** 一道灶活要做多久（{@value #HEAT_TICKS_PER_ITEM} tick = 5 秒）。 */
    @Override
    protected int batchTicks() {
        return HEAT_TICKS_PER_ITEM;
    }

    /** 炒一份菜 / 蒸一笼的耗时。 */
    public static final int HEAT_TICKS_PER_ITEM = 100;

    /**
     * 灶具内部**不存电**。
     *
     * <p>容量给 0 之后 {@code Capabilities.Energy} 也不会挂上去（见
     * {@code ModCapabilities}），所以漏斗和管道不会往里灌电 ——
     * 免得出现"插根线就能免费炒菜"这种漏洞。</p>
     */
    @Override
    protected int machineBuffer() {
        return 0;
    }

    @Override
    protected int ioRate() {
        return 0;
    }

    @Override
    protected boolean hasPower() {
        if (this.level == null) {
            return false;
        }
        HeatSource source = HeatSource.below(this.level, this.worldPosition);
        return source != null && source.heat() >= HeatSource.HEAT_WORKING;
    }

    /** 不扣任何东西 —— 燃料由炉灶烧。 */
    @Override
    protected void consumePower() {
        // 有意留空
    }

    /** 界面那根竖条：有火就是满的。 */
    @Override
    public int getPowerForDisplay() {
        return this.hasPower() ? HeatSource.HEAT_CAPACITY : 0;
    }

    @Override
    public int getPowerCapacityForDisplay() {
        return HeatSource.HEAT_CAPACITY;
    }

    @Override
    public boolean heatPowered() {
        return true;
    }
}
