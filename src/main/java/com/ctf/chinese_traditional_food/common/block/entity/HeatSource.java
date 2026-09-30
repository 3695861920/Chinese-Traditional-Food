package com.ctf.chinese_traditional_food.common.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;

/**
 * 「热源」：能给它<b>上面那一格</b>的锅具供热。
 *
 * <p>目前唯一的实现是 {@link StoveBlockEntity}（炉灶，烧原版燃料）。
 * 做成接口而不是直接判类型，是为了以后能挂别的热源 ——
 * 比如原版营火、岩浆块，或者其它模组的灶台。</p>
 *
 * <h2>为什么只供热给正上方</h2>
 * 现实里锅是坐在灶眼上的，所以这里也只认正上方一格。
 * 这样玩家一眼就能看出"锅要放在灶上"，不用去猜判定范围。
 */
public interface HeatSource {

    /**
     * 热度上限。数字本身没有单位，只是"够不够"的阈值。
     *
     * <p>放在接口上而不是某个实现里：锅具（消费方）与电磁炉（提供方）
     * 要比较的是同一个标尺，两边各写一份迟早会调歪。</p>
     */
    int HEAT_CAPACITY = 100;

    /** 锅具开工所需的最低热度。 */
    int HEAT_WORKING = 20;

    /** 当前热度（0 = 没火）。 */
    int heat();

    /** 热度上限。 */
    int heatCapacity();

    /**
     * 找某一格下面的热源。
     *
     * @return 热度大于 0 的热源；没有就返回 {@code null}
     */
    static HeatSource below(Level level, BlockPos pos) {
        if (level == null) {
            return null;
        }
        BlockPos under = pos.relative(Direction.DOWN);
        if (level.getBlockEntity(under) instanceof HeatSource source && source.heat() > 0) {
            return source;
        }
        return null;
    }
}
