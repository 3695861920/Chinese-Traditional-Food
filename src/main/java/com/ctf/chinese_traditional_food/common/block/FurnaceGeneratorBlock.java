package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.FurnaceGeneratorBlockEntity;
import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import com.ctf.chinese_traditional_food.registry.ModMenus;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 熔炉发电机：塞燃料、往外送电的简单电源。
 *
 * <h2>交互</h2>
 * <ul>
 *   <li><b>拿着燃料右键</b> —— 塞进燃料槽（不用开界面也能用）；</li>
 *   <li><b>拿着别的右键 / 空手右键</b> —— 打开界面（塞燃料、看电量和火苗）；</li>
 *   <li>潜行空手右键 —— 把燃料取回来。</li>
 * </ul>
 *
 * <p>电会自动往<b>六个方向</b>推，所以把加工机贴着它放、或者用管道接都行。</p>
 *
 * <p>继承 {@link AbstractFacingBlock} 让它有正面 —— 带炉栅和火光的那一面
 * 放下时朝着玩家，一眼就知道这台是烧东西的。</p>
 */
public class FurnaceGeneratorBlock extends AbstractFacingBlock implements EntityBlock {

    public FurnaceGeneratorBlock(Properties properties) {
        super(properties);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new FurnaceGeneratorBlockEntity(pos, state);
    }

    // ------------------------------------------------------------------
    // 交互
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                          Player player, InteractionHand hand, BlockHitResult hit) {
        if (stack.isEmpty()) {
            // 空手交给 useWithoutItem 处理（否则默认会吃掉这次右键）
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        if (!(level.getBlockEntity(pos) instanceof FurnaceGeneratorBlockEntity generator)) {
            return InteractionResult.PASS;
        }
        // 只有真的是燃料才吃掉这次右键，否则让别的逻辑接手
        if (!level.isClientSide() && !isFuel(level, stack)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide()) {
            return InteractionResult.SUCCESS;
        }

        ItemStack fuelSlot = generator.getFuel().getItem(FurnaceGeneratorBlockEntity.SLOT_FUEL);
        if (!fuelSlot.isEmpty() && !ItemStack.isSameItemSameComponents(fuelSlot, stack)) {
            // 槽里已经有别的燃料了，直接开界面让玩家自己处理
            player.openMenu(this.menuProvider(generator));
            return InteractionResult.SUCCESS;
        }
        int room = fuelSlot.isEmpty() ? stack.getMaxStackSize()
                : fuelSlot.getMaxStackSize() - fuelSlot.getCount();
        if (room <= 0) {
            player.openMenu(this.menuProvider(generator));
            return InteractionResult.SUCCESS;
        }
        int moved = Math.min(room, stack.getCount());
        if (fuelSlot.isEmpty()) {
            generator.getFuel().setItem(FurnaceGeneratorBlockEntity.SLOT_FUEL,
                    stack.copyWithCount(moved));
        } else {
            fuelSlot.grow(moved);
            generator.getFuel().setChanged();
        }
        if (!player.hasInfiniteMaterials()) {
            stack.shrink(moved);
        }
        level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.6F, 0.9F);
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof FurnaceGeneratorBlockEntity generator)) {
            return InteractionResult.PASS;
        }

        // 潜行空手：把燃料取回来（方便换个炉子）
        if (player.isShiftKeyDown()) {
            if (level.isClientSide()) {
                return InteractionResult.SUCCESS_SERVER;
            }
            ItemStack taken = generator.getFuel().removeItem(
                    FurnaceGeneratorBlockEntity.SLOT_FUEL, 64);
            if (!taken.isEmpty() && !player.getInventory().add(taken)) {
                player.drop(taken, false);
            }
            generator.getFuel().setChanged();
            level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.7F, 1.0F);
            return InteractionResult.SUCCESS_SERVER;
        }

        // 普通空手右键：报一下当前状态 + 开界面
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable(
                    generator.isBurning()
                            ? "tooltip.chinese_traditional_food.generator_burning"
                            : "tooltip.chinese_traditional_food.generator_idle",
                    generator.getEnergy(), generator.getEnergyCapacity(),
                    MachineEnergy.GENERATOR_OUTPUT));
            player.openMenu(this.menuProvider(generator));
        }
        return InteractionResult.SUCCESS;
    }

    private MenuProvider menuProvider(FurnaceGeneratorBlockEntity generator) {
        return new SimpleMenuProvider(
                (id, inv, player) -> ModMenus.createGeneratorMenu(id, inv, generator),
                Component.translatable("container.chinese_traditional_food.furnace_generator"));
    }

    /** 这个物品能不能当燃料（用原版的燃料表）。 */
    private static boolean isFuel(Level level, ItemStack stack) {
        return stack.getBurnTime(net.minecraft.world.item.crafting.RecipeType.SMELTING,
                level.fuelValues()) > 0;
    }

    // ------------------------------------------------------------------
    // ticker
    // ------------------------------------------------------------------

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state,
                                                                  BlockEntityType<T> type) {
        if (level.isClientSide()) {
            return null;    // 发电逻辑只在服务端跑
        }
        return (lvl, pos, st, be) -> {
            if (be instanceof FurnaceGeneratorBlockEntity generator) {
                FurnaceGeneratorBlockEntity.serverTick(lvl, pos, st, generator);
            }
        };
    }
}
