package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModMenus;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 自研装置（水磨 / 脱壳机）的公共方块。
 *
 * <h2>交互约定</h2>
 * <ul>
 *   <li><b>空手右键</b> —— 打开界面（放原料、取出成品）。</li>
 *   <li><b>潜行 + 空手右键</b> —— 手摇一轮（脱壳机专用；水磨也允许，方便测试）。</li>
 * </ul>
 *
 * <p>机器的动力由子类的方块实体决定：水磨要邻水，脱壳机要红石信号。</p>
 */
public abstract class AbstractProcessorBlock extends Block implements EntityBlock {
    protected AbstractProcessorBlock(Properties properties) {
        super(properties);
    }

    /** 机器界面的标题翻译键。 */
    protected abstract String containerKey();

    /** 手动操作时的提示（空手潜行右键）。 */
    protected abstract boolean supportsManualCrank();

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof AbstractProcessorBlockEntity machine)) {
            return InteractionResult.PASS;
        }

        // 潜行 -> 手摇一轮
        if (player.isShiftKeyDown() && this.supportsManualCrank()) {
            if (level.isClientSide()) {
                return InteractionResult.SUCCESS;
            }
            boolean worked = machine.processOnce();
            // 26.1 里 Player#displayClientMessage 已不存在；
            // 提示在动作栏显示用 sendOverlayMessage。
            player.sendOverlayMessage(
                    Component.translatable(worked
                            ? "tooltip.chinese_traditional_food.machine_crank_ok"
                            : "tooltip.chinese_traditional_food.machine_crank_fail"));
            return worked ? InteractionResult.SUCCESS : InteractionResult.FAIL;
        }

        // 普通右键 -> 开界面
        if (!level.isClientSide()) {
            player.openMenu(this.menuProvider(machine));
        }
        return InteractionResult.SUCCESS;
    }

    /** 给 {@code Player#openMenu} 用的菜单提供者。标题由子类决定。 */
    protected MenuProvider menuProvider(AbstractProcessorBlockEntity machine) {
        return new SimpleMenuProvider(
                (containerId, playerInventory, player) ->
                        ModMenus.createMenu(containerId, playerInventory, machine),
                Component.translatable(this.containerKey()));
    }

    @Nullable
    @Override
    public abstract BlockEntity newBlockEntity(BlockPos pos, BlockState state);

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state,
                                                                  BlockEntityType<T> type) {
        if (level.isClientSide()) {
            return null;    // 机器逻辑只在服务端跑
        }
        return (lvl, pos, st, be) -> {
            if (be instanceof AbstractProcessorBlockEntity machine) {
                AbstractProcessorBlockEntity.serverTick(lvl, pos, st, machine);
            }
        };
    }
}
