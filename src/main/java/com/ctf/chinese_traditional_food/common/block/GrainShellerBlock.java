package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.GrainShellerBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 手摇式碾米机（脱壳机）的核心。
 *
 * <h2>为什么做成大型机器、而且没有界面</h2>
 * 现实里的手摇碾米机是一整套设备：木架、机箱、四角立柱、上面的料斗、
 * 侧面的摇柄 —— 根本不是一个方块能装下的东西，也没有任何"界面"可言。
 * 所以这里做成 <b>3×3×3</b> 的多方块结构，并且<b>全部操作都在原地右键完成</b>：
 *
 * <table border="1">
 *   <tr><th>手上</th><th>是否潜行</th><th>行为</th></tr>
 *   <tr><td>带壳谷物</td><td>否</td><td>倒进料斗（一次最多 16 个）</td></tr>
 *   <tr><td>空手</td><td><b>是</b></td><td><b>摇一圈</b>：加工一个</td></tr>
 *   <tr><td>空手</td><td>否</td><td>把加工好的米 / 米糠取出来</td></tr>
 * </table>
 *
 * <p>对着机身<b>任意一个部件</b>右键都行 —— 交互会由部件转发到核心，
 * 这是 {@link AbstractMachineCoreBlock} 提供的能力。</p>
 *
 * <h2>结构</h2>
 * 放下核心时会自动展开：3×3 木架（核心在正中）+ 四角立柱 + 四边机箱板
 * + 顶部料斗。缺零件时机器不工作，核心会显示成"缺零件"的外观。
 */
public class GrainShellerBlock extends AbstractMachineCoreBlock {

    public GrainShellerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected List<MachineStructure.Part> structureParts() {
        return MachineStructure.GRAIN_SHELLER;
    }

    @Override
    protected Block partBlock() {
        return ModBlocks.GRAIN_SHELLER_PART.get();
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
    // 倒料
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
        if (!state.getValue(FORMED)) {
            if (!level.isClientSide()) {
                warnIncomplete(player);
            }
            return InteractionResult.FAIL;
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

    // ------------------------------------------------------------------
    // 摇 / 取
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof GrainShellerBlockEntity sheller)) {
            return InteractionResult.PASS;
        }
        if (!state.getValue(FORMED)) {
            if (!level.isClientSide()) {
                warnIncomplete(player);
            }
            return InteractionResult.FAIL;
        }

        // 潜行 -> 摇一圈
        if (player.isShiftKeyDown()) {
            if (level.isClientSide()) {
                return InteractionResult.SUCCESS;
            }
            GrainShellerBlockEntity.CrankResult result = sheller.crank();
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
}
