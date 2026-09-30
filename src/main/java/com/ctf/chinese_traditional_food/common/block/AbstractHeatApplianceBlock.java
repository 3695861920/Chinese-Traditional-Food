package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractHeatProcessorBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModMenus;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 「灶上锅具」的公共方块：炒锅 / 蒸笼 / 汤锅。
 *
 * <h2>必须坐在炉灶上</h2>
 * 它们自己不吃电，动力来自<b>正下方</b>的 {@code 炉灶}
 * （见 {@code HeatSource.below}）。所以：
 *
 * <ul>
 *   <li>下面没灶、或者灶没烧 → 进度原地等（和电动设备"没电"的表现一致）；</li>
 *   <li>不用拉电线，随手搭个灶就能做饭。</li>
 * </ul>
 *
 * <p>另外这里刻意<b>不</b>暴露 {@code Capabilities.Energy}（见 {@code ModCapabilities}）——
 * 否则玩家插根线就能免费炒菜，把设计意图绕过去了。</p>
 *
 * <h2>模型与碰撞箱</h2>
 * 子类给出各自的模型尺寸，碰撞箱跟着模型走：锅是圆的、蒸笼是矮的、
 * 汤锅是高筒，三者都不一样高 —— "模型多大就占多大"。
 */
public abstract class AbstractHeatApplianceBlock extends AbstractFacingBlock
        implements EntityBlock {
    protected AbstractHeatApplianceBlock(Properties properties) {
        super(properties);
    }

    /** 界面标题的翻译键。 */
    protected abstract String containerKey();

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof AbstractHeatProcessorBlockEntity machine)) {
            return InteractionResult.PASS;
        }

        // 潜行：报一下灶上的火够不够，不开界面
        if (player.isShiftKeyDown()) {
            if (!level.isClientSide()) {
                boolean hot = machine.getPowerForDisplay() > 0;
                player.sendOverlayMessage(Component.translatable(
                        hot
                                ? "tooltip.chinese_traditional_food.appliance_hot"
                                : "tooltip.chinese_traditional_food.appliance_cold"));
            }
            return InteractionResult.SUCCESS;
        }

        if (!level.isClientSide()) {
            player.openMenu(this.menuProvider(machine));
        }
        return InteractionResult.SUCCESS;
    }

    protected MenuProvider menuProvider(AbstractHeatProcessorBlockEntity machine) {
        return new SimpleMenuProvider(
                (id, inv, player) -> ModMenus.createCookerMenu(id, inv, machine),
                Component.translatable(this.containerKey()));
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state,
                                                                  BlockEntityType<T> type) {
        if (level.isClientSide()) {
            return null;
        }
        return (lvl, pos, st, be) -> {
            if (be instanceof AbstractHeatProcessorBlockEntity machine) {
                AbstractHeatProcessorBlockEntity.serverTick(lvl, pos, st, machine);
            }
        };
    }
}
