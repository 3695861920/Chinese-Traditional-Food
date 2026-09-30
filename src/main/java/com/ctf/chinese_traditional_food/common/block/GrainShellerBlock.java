package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.GrainShellerBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 手摇式脱壳机。
 *
 * <h2>为什么做成"无 UI + 手摇"</h2>
 * 现实里的手摇碾米机就是一个木箱、一个摇柄、上面一个料斗 ——
 * 没有任何"界面"可言，操作方式就是<b>往里倒谷子，然后摇</b>。
 * 所以这里刻意不做 GUI，全部用原地的右键动作完成，
 * 也更符合"能看见自己在干活"的原版手感。
 *
 * <h2>操作（全程不看界面）</h2>
 * <table border="1">
 *   <tr><th>手上</th><th>是否潜行</th><th>行为</th></tr>
 *   <tr><td>带壳谷物</td><td>否</td><td>倒进机器（装了料斗一次最多倒 16 个）</td></tr>
 *   <tr><td>空手</td><td><b>是</b></td><td><b>摇一圈</b>：加工一个，摇柄转 90°</td></tr>
 *   <tr><td>空手</td><td>否</td><td>把加工好的米 / 糠取出来</td></tr>
 * </table>
 *
 * <h2>多方块：加料斗</h2>
 * 在机器正上方放一个 {@link GrainShellerHopperBlock}，进料上限从 1 涨到 16，
 * 可以一次倒进去一整把谷子再慢慢摇。拆掉料斗退回单格上限（斗里的东西不会丢）。
 *
 * <h2>转动动画怎么来的</h2>
 * 方块状态 {@link #CRANK} 有 0~3 四个值，每个值对应一张摇柄角度的模型。
 * 每摇一次就换下一个值 —— 于是<b>不需要任何渲染器</b>就有转动动画
 * （原版拉杆、中继器也是这个套路）。
 */
public class GrainShellerBlock extends Block implements EntityBlock {
    /** 摇柄角度（0~3），同时用作转动动画。 */
    public static final IntegerProperty CRANK = IntegerProperty.create("crank", 0, 3);

    private static final VoxelShape SHAPE = Block.box(1.0, 0.0, 1.0, 15.0, 11.5, 15.0);

    public GrainShellerBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(CRANK, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(CRANK);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos,
                                  CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new GrainShellerBlockEntity(pos, state);
    }

    /** 机器不自己动 —— 只有摇柄能驱动它，所以不注册 ticker。 */
    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state,
                                                                  BlockEntityType<T> type) {
        return null;
    }

    // ------------------------------------------------------------------
    // 交互
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                          Player player, InteractionHand hand, BlockHitResult hit) {
        if (stack.isEmpty()) {
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        if (!(level.getBlockEntity(pos) instanceof GrainShellerBlockEntity sheller)) {
            return InteractionResult.PASS;
        }
        if (!sheller.accepts(stack)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide()) {
            return InteractionResult.SUCCESS;
        }

        int room = sheller.inputRoom();
        if (room <= 0) {
            player.sendOverlayMessage(Component.translatable(
                    "tooltip.chinese_traditional_food.sheller_full"));
            return InteractionResult.FAIL;
        }
        int moved = Math.min(room, stack.getCount());
        sheller.insertInput(stack.copyWithCount(moved));
        if (!player.hasInfiniteMaterials()) {
            stack.shrink(moved);
        }
        level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.6F, 0.8F);
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof GrainShellerBlockEntity sheller)) {
            return InteractionResult.PASS;
        }

        // 潜行 -> 摇一圈
        if (player.isShiftKeyDown()) {
            if (level.isClientSide()) {
                return InteractionResult.SUCCESS;
            }
            GrainShellerBlockEntity.CrankResult result = sheller.crank();
            // 摇柄转 90°：这就是全部的动画
            level.setBlock(pos, state.cycle(CRANK), Block.UPDATE_CLIENTS);
            level.playSound(null, pos,
                    result == GrainShellerBlockEntity.CrankResult.DONE
                            ? SoundEvents.ITEM_PICKUP : SoundEvents.WOOD_HIT,
                    SoundSource.BLOCKS, 0.8F,
                    result == GrainShellerBlockEntity.CrankResult.DONE ? 1.2F : 0.8F);

            if (result == GrainShellerBlockEntity.CrankResult.EMPTY) {
                player.sendOverlayMessage(Component.translatable(
                        "tooltip.chinese_traditional_food.sheller_empty"));
            } else if (result == GrainShellerBlockEntity.CrankResult.OUTPUT_FULL) {
                player.sendOverlayMessage(Component.translatable(
                        "tooltip.chinese_traditional_food.sheller_output_full"));
            }
            return InteractionResult.SUCCESS;
        }

        // 不潜行 -> 取成品
        ItemStack out = sheller.takeOutput();
        if (out.isEmpty()) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide()) {
            return InteractionResult.SUCCESS;
        }
        if (!player.getInventory().add(out)) {
            player.drop(out, false);
        }
        level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.7F, 1.0F);
        return InteractionResult.SUCCESS;
    }

    // ------------------------------------------------------------------
    // 多方块：料斗
    // ------------------------------------------------------------------

    /** 正上方是否装了料斗。 */
    public static boolean hasHopper(BlockGetter level, BlockPos pos) {
        return level.getBlockState(pos.above()).is(ModBlocks.GRAIN_SHELLER_HOPPER.get());
    }

    /** 进料上限：加料斗后从 1 变 16。 */
    public static int capacityOf(BlockGetter level, BlockPos pos) {
        return hasHopper(level, pos)
                ? GrainShellerBlockEntity.CAPACITY_WITH_HOPPER
                : GrainShellerBlockEntity.CAPACITY_BARE;
    }

    /** 装上 / 拆掉料斗时刷新一下，客户端要据此显示不同的斗容量提示。 */
    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState,
                        boolean movedByPiston) {
        super.onPlace(state, level, pos, oldState, movedByPiston);
        if (!level.isClientSide()) {
            level.sendBlockUpdated(pos, state, state, Block.UPDATE_CLIENTS);
        }
    }

    /** 出料口朝向（模型把出料口做在北面）。 */
    public static Direction outputFacing() {
        return Direction.NORTH;
    }

    /** 机器音效类型。 */
    public static SoundType machineSound() {
        return SoundType.WOOD;
    }
}
