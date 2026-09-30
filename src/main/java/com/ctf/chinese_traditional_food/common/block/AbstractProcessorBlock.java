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
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 自研装置（水磨）的公共方块。
 *
 * <h2>交互约定</h2>
 * <ul>
 *   <li><b>空手右键</b> —— 打开界面（放原料、取出成品）。</li>
 *   <li><b>潜行 + 空手右键</b> —— 手摇一轮（方便没水的时候也能先用）。</li>
 * </ul>
 *
 * <p>继承 {@link AbstractMachineCoreBlock}，所以机器必须先
 * <b>结构完整</b>才会工作；缺零件时只给一句提示，不开界面。
 * 对着机身任意一个部件右键也一样能开 —— 交互由部件转发过来。</p>
 */
public abstract class AbstractProcessorBlock extends AbstractMachineCoreBlock {
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

        // 结构不完整就不干活：先提示，别让玩家对着半台机器白贳力气
        if (!state.getValue(FORMED)) {
            if (!level.isClientSide()) {
                warnIncomplete(player);
            }
            return InteractionResult.FAIL;
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
            // 结构不完整的机器不转 —— 缺零件就该停着，而不是照旧默默干活
            if (!st.getValue(FORMED)) {
                return;
            }
            if (be instanceof AbstractProcessorBlockEntity machine) {
                AbstractProcessorBlockEntity.serverTick(lvl, pos, st, machine);
            }
        };
    }
}
