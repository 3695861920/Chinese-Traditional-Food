package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.ServingPlatterBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 大拼盘：2×2 摆 4 份菜的展示方块，用来"摆一桌"。
 *
 * <p>配合 {@code ServingPlatterBlockEntityRenderer} 把槽位 0~3 渲染到四个象限。</p>
 *
 * <h2>实际占用体积</h2>
 * <p>托盘本体只有 {@code y = 0..2.35} 高、横向留了一点缝，所以碰撞箱就是
 * 「一块矮托盘」：能踩上去，不会挡路。两侧的提手在模型里伸到了格子外面
 * （{@code -0.9 / 16.9}），但碰撞箱不跟着外扩 —— 否则会把邻居格子咬掉一块。</p>
 */
public class ServingPlatterBlock extends AbstractDishDisplayBlock {

    /** 托盘的真实占用体积（与 {@code display_models.serving_platter()} 一致）。 */
    private static final VoxelShape SHAPE =
            Block.box(0.0, 0.0, 0.0, 16.0, 2.35, 16.0);

    public ServingPlatterBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos,
                                  CollisionContext context) {
        return SHAPE;
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos,
                                           CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new ServingPlatterBlockEntity(pos, state);
    }
}
