package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractDishDisplayBlockEntity;
import com.ctf.chinese_traditional_food.common.item.DishItem;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/**
 * "能把菜摆出来"的方块父类（餐盘、大拼盘都继承它）。
 *
 * <h2>交互约定（写死在代码里，方便玩家形成肌肉记忆）</h2>
 * <table border="1">
 *   <tr><th>手上</th><th>是否潜行</th><th>行为</th></tr>
 *   <tr><td>拿着菜</td><td>否</td><td>摆一份上去（最多摆满容量）</td></tr>
 *   <tr><td>空手</td><td>否</td><td>夹一口吃（吃的是最上面那一份）</td></tr>
 *   <tr><td>空手</td><td>是</td><td>把整份菜端回背包</td></tr>
 *   <tr><td>拿着别的</td><td>否</td><td>不响应，交给方块物品等其他逻辑</td></tr>
 * </table>
 *
 * <p>交互分两个方法：{@code useItemOn} 处理"手上有东西"，
 * {@code useWithoutItem} 处理"空手"。{@code useItemOn} 返回
 * {@link InteractionResult#TRY_WITH_EMPTY_HAND} 才会继续走到 {@code useWithoutItem}。</p>
 */
public abstract class AbstractDishDisplayBlock extends Block implements EntityBlock {
    protected AbstractDishDisplayBlock(Properties properties) {
        super(properties);
    }

    // ------------------------------------------------------------------
    // 放菜
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                          Player player, InteractionHand hand, BlockHitResult hit) {
        if (stack.isEmpty()) {
            // 空手：把流程让给 useWithoutItem（否则默认会吃掉这次右键）
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        if (!(level.getBlockEntity(pos) instanceof AbstractDishDisplayBlockEntity display)) {
            return InteractionResult.PASS;
        }
        if (!DishItem.isPlaceable(stack)) {
            return InteractionResult.PASS;
        }
        int slot = display.firstFreeSlot();
        if (slot < 0) {
            return InteractionResult.PASS; // 摆满了
        }
        if (!level.isClientSide()) {
            display.setDish(slot, stack.copyWithCount(1));
            display.onDishesChanged();
            if (!player.hasInfiniteMaterials()) {
                stack.shrink(1);
            }
            level.playSound(null, pos, SoundEvents.ITEM_FRAME_ADD_ITEM, SoundSource.BLOCKS,
                    0.7F, 1.0F + level.getRandom().nextFloat() * 0.2F);
        }
        return InteractionResult.SUCCESS;
    }

    // ------------------------------------------------------------------
    // 吃 / 端走
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof AbstractDishDisplayBlockEntity display)) {
            return InteractionResult.PASS;
        }
        int slot = display.lastOccupiedSlot();
        if (slot < 0) {
            return InteractionResult.PASS; // 空盘
        }

        if (player.isShiftKeyDown()) {
            return takeBack(level, pos, player, display, slot);
        }
        return eatOne(level, pos, player, display, slot);
    }

    /** 潜行 + 空手：把整份菜端回背包。 */
    private InteractionResult takeBack(Level level, BlockPos pos, Player player,
                                       AbstractDishDisplayBlockEntity display, int slot) {
        if (level.isClientSide()) {
            return InteractionResult.SUCCESS_SERVER; // 需要服务端信息才知道能不能装下
        }
        ItemStack taken = display.removeDish(slot);
        display.onDishesChanged();
        if (!player.getInventory().add(taken)) {
            player.drop(taken, false);
        }
        level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.7F, 1.0F);
        return InteractionResult.SUCCESS_SERVER;
    }

    /** 空手：夹一口，吃完一份后槽位自动清空。 */
    private InteractionResult eatOne(Level level, BlockPos pos, Player player,
                                     AbstractDishDisplayBlockEntity display, int slot) {
        ItemStack dish = display.getDish(slot);
        if (!DishItem.serve(level, player, dish)) {
            return InteractionResult.PASS; // 不是能吃的东西
        }
        if (!level.isClientSide()) {
            ItemStack remaining = dish.copy();
            remaining.shrink(1);
            display.setDish(slot, remaining.isEmpty() ? ItemStack.EMPTY : remaining);
            display.onDishesChanged();
        }
        return InteractionResult.SUCCESS;
    }
}
