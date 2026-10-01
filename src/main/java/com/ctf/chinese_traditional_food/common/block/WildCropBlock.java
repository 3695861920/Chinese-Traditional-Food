package com.ctf.chinese_traditional_food.common.block;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 野生作物：自然生成在野外、能直接采的"没人种但长着"的作物。
 *
 * <h2>和地里的作物差在哪</h2>
 * <table border="1">
 *   <tr><th></th><th>{@link ModCropBlock 地里种的}</th><th>野生的（本类）</th></tr>
 *   <tr><td>长在哪</td><td>耕地，且会退化</td><td>草方块 / 泥土，随便踩</td></tr>
 *   <tr><td>有生长期吗</td><td>八个阶段</td><td>没有，一长出来就是"熟的"</td></tr>
 *   <tr><td>怎么拿</td><td>等成熟了收</td><td>直接打掉，掉种子 + 一点收成</td></tr>
 * </table>
 *
 * <p>它的存在意义是<b>给生存模式一个起点</b>：不靠工作台、也不靠别人给，
 * 在野外找到一丛就能拿回种子开始种。所以它掉落里<b>一定有种子</b>
 * （见 {@code loot_table/blocks/wild_*.json}）。</p>
 *
 * <p>实现上直接继承 {@link BushBlock}（原版草丛、枯木丛就是它）：
 * 自带"下面是土才能活、下面没了就消失"的逻辑，我们只要把
 * "能长在什么上面"放宽到泥土类就行。</p>
 */
public class WildCropBlock extends BushBlock {

    public WildCropBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    /**
     * 能长在什么上面。
     *
     * <p>原版 {@code SUPPORTS_VEGETATION} 这个方块标签其实已经涵盖了
     * 草方块与泥土，这里显式再列一遍是为了两件事：</p>
     * <ul>
     *   <li>别的模组动了那个标签也不会把野生作物搞没；</li>
     *   <li>读代码的人一眼看得见"它就是长在土上的"。</li>
     * </ul>
     */
    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(BlockTags.DIRT)
                || state.is(Blocks.GRASS_BLOCK)
                || state.is(Blocks.FARMLAND)
                || state.is(Blocks.MOSS_BLOCK)
                || super.mayPlaceOn(state, level, pos);
    }
}
