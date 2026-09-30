package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.CuttingBoardBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 案板：把食材放上去，再用刀切。
 *
 * <h2>交互约定</h2>
 * <table border="1">
 *   <tr><th>手上</th><th>案板状态</th><th>行为</th></tr>
 *   <tr><td>拿着可切的食材</td><td>空</td><td>放上去（一次放 1 个）</td></tr>
 *   <tr><td>拿着刀</td><td>有食材</td><td><b>切一刀</b>，刀掉 1 点耐久</td></tr>
 *   <tr><td>拿着别的</td><td>有食材</td><td>试着按"徒手规则"切（例如腐乳不需要刀）</td></tr>
 *   <tr><td>空手</td><td>有成品</td><td>取走成品</td></tr>
 *   <tr><td>空手</td><td>没有成品但有食材</td><td>把食材取回来</td></tr>
 * </table>
 *
 * <p>注意这里<b>不做</b>"空手吃一口"—— 案板是加工台，不是餐具。
 * 想吃菜请用餐盘 / 大拼盘。</p>
 */
public class CuttingBoardBlock extends Block implements EntityBlock {

    /**
     * 案板的真实占用体积（与 {@code display_models.cutting_board()} 一致）。
     *
     * <p>板子是 {@code x/z = 0.4..15.6, y = 0..1.9} —— 只有 0.12 格高。
     * 默认的整格碰撞箱会让玩家"踩上台阶"，也会挡住相邻方块的面部别除，
     * 所以要显式给出真实尺寸。</p>
     */
    private static final VoxelShape SHAPE =
            Block.box(0.4, 0.0, 0.4, 15.6, 1.9, 15.6);

    public CuttingBoardBlock(Properties properties) {
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
    public net.minecraft.world.level.block.entity.BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new CuttingBoardBlockEntity(pos, state);
    }

    // ------------------------------------------------------------------
    // 手上拿着东西
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                          Player player, InteractionHand hand, BlockHitResult hit) {
        if (stack.isEmpty()) {
            // 空手 → 交给 useWithoutItem 处理取回逻辑
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        if (!(level.getBlockEntity(pos) instanceof CuttingBoardBlockEntity board)) {
            return InteractionResult.PASS;
        }

        boolean hasKnife = CuttingBoardBlockEntity.isKnife(stack);

        // 1) 案板上有食材 → 先尝试切
        if (!board.getInput().isEmpty()) {
            if (cut(level, pos, player, board, stack)) {
                return InteractionResult.SUCCESS;
            }
            // 切不动：如果是刀，说明这道食材不在切割表里
            return InteractionResult.PASS;
        }

        // 2) 案板是空的 → 拿着刀点空板没有意义
        if (hasKnife) {
            return InteractionResult.PASS;
        }

        // 3) 放食材上去（一次一个）
        if (!level.isClientSide()) {
            board.setInput(stack.copyWithCount(1));
            board.onDishesChanged();
            if (!player.hasInfiniteMaterials()) {
                stack.shrink(1);
            }
            playSound(level, pos, SoundEvents.WOOD_PLACE, 0.9F);
        }
        return InteractionResult.SUCCESS;
    }

    // ------------------------------------------------------------------
    // 空手
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof CuttingBoardBlockEntity board)) {
            return InteractionResult.PASS;
        }

        // 先取成品，再取食材 —— 保证"切完直接空手右键就能拿到"
        ItemStack toGive = board.takeResult();
        if (toGive == null) {
            toGive = board.takeInput();
        }
        if (toGive == null) {
            return InteractionResult.PASS;
        }

        if (!level.isClientSide()) {
            if (!player.getInventory().add(toGive)) {
                player.drop(toGive, false);
            }
            playSound(level, pos, SoundEvents.ITEM_PICKUP, 1.0F);
        }
        return InteractionResult.SUCCESS;
    }

    // ------------------------------------------------------------------
    // 内部
    // ------------------------------------------------------------------

    /** 切一刀，成功时播放砧板声。 */
    private boolean cut(Level level, BlockPos pos, Player player,
                        CuttingBoardBlockEntity board, ItemStack knife) {
        if (level.isClientSide()) {
            // 客户端只知道"手里有没有刀"，无法查表；统一先回成功让手臂摆动，
            // 真正的判定与扣耐久在服务端做。
            return true;
        }
        if (!board.tryCut(knife)) {
            return false;
        }
        playSound(level, pos, SoundEvents.WOOD_HIT, 1.1F);
        return true;
    }

    private static void playSound(Level level, BlockPos pos,
                                  net.minecraft.sounds.SoundEvent event, float pitch) {
        level.playSound(null, pos, event, SoundSource.BLOCKS, 0.7F, pitch);
    }
}
