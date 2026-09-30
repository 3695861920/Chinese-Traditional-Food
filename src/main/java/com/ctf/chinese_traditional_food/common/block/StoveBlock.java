package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.StoveBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 电磁炉：一格大小的完整方块，插上电就给<b>正上方</b>的锅具供热。
 *
 * <h2>比原来那台灶台简单在哪</h2>
 * 旧版是"砖石灶台 + 燃料槽 + 燃烧时间 + 火苗界面"，本质上是把熔炉发电机
 * 又抄了一遍。新版只有三件事：
 *
 * <ul>
 *   <li><b>完整方块</b>：模型 0~16 铺满，和旁边的方块码在一起不突兀 ——
 *       它就是个台面，不需要"四条腿"那种造型；</li>
 *   <li><b>用电</b>：FE 走 {@code Capabilities.Energy.BLOCK}，
 *       不用再喂燃料，也没有桶回收之类的麻烦；</li>
 *   <li><b>没有界面</b>：通电就亮（方块状态 {@link #POWERED}），
 *       贴图上直接能看到一圈发光的线圈。右键会报一下剩余电量。</li>
 * </ul>
 *
 * <p>那"锅"的界面还在 —— 锅有四个原料槽，值得看一眼。</p>
 */
public class StoveBlock extends AbstractFacingBlock implements EntityBlock {

    /**
     * 是否正在给上面的锅供热。
     *
     * <p>写进方块状态的目的是让<b>贴图</b>能跟着变：客户端只看一眼
     * 就知道这台有没有在工作，不必开界面或者右键。</p>
     */
    public static final BooleanProperty POWERED = BlockStateProperties.POWERED;

    /** 完整方块：模型铺满整格，碰撞箱自然也是整格。 */
    private static final VoxelShape SHAPE =
            Block.box(0.0, 0.0, 0.0, 16.0, 16.0, 16.0);

    public StoveBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.defaultBlockState().setValue(POWERED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(POWERED);
    }

    @Override
    protected VoxelShape machineShape() {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new StoveBlockEntity(pos, state);
    }

    /**
     * 右键：只报状态，不开界面。
     *
     * <p>电磁炉没有可调的东西 —— 它要么有电要么没电。报一下剩余电量
     * 就够了，为一个只有一根条的空界面反而增加负担。</p>
     */
    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof StoveBlockEntity stove)) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide()) {
            player.sendOverlayMessage(state.getValue(POWERED)
                    ? Component.translatable("tooltip.chinese_traditional_food.stove_heating",
                            stove.getEnergy(), stove.getEnergyCapacity())
                    : Component.translatable("tooltip.chinese_traditional_food.stove_no_power",
                            stove.getEnergy(), stove.getEnergyCapacity()));
        }
        return InteractionResult.SUCCESS;
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state,
                                                                  BlockEntityType<T> type) {
        if (level.isClientSide()) {
            return null;    // 逻辑只在服务端跑
        }
        return (lvl, pos, st, be) -> {
            if (be instanceof StoveBlockEntity stove) {
                StoveBlockEntity.serverTick(lvl, pos, st, stove);
            }
        };
    }
}
