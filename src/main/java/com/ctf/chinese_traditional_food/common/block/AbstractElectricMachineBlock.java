package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.ElectricMillBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModMenus;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 电力加工设备的公共方块（电动磨粉机 / 电动脱壳机）。
 *
 * <h2>为什么改成单方块</h2>
 * 之前那套 3×3 多方块结构搭起来麻烦、搬起来更麻烦，而且一旦少了零件
 * 就整台停机。改成单方块 + 电力之后：放下就能用，接上发电机就跑，
 * 想搬走直接挖掉。
 *
 * <h2>朝向</h2>
 * 正面朝向由 {@link AbstractFacingBlock} 提供，这里不用再管。
 *
 * <h2>交互</h2>
 * <ul>
 *   <li>空手右键 —— 打开界面（放原料、取成品、看电量和进度）；</li>
 *   <li>潜行空手右键 —— 报一下当前状态（够不够电）。</li>
 * </ul>
 */
public abstract class AbstractElectricMachineBlock extends AbstractFacingBlock
        implements EntityBlock {
    protected AbstractElectricMachineBlock(Properties properties) {
        super(properties);
    }

    /** 界面标题的翻译键。 */
    protected abstract String containerKey();

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof AbstractProcessorBlockEntity machine)) {
            return InteractionResult.PASS;
        }

        // 潜行：只报状态，不开界面（方便贴着机器快速看一眼够不够电）
        if (player.isShiftKeyDown()) {
            if (!level.isClientSide()) {
                boolean powered = machine.getEnergy() > 0;
                player.sendOverlayMessage(Component.translatable(
                        powered
                                ? "tooltip.chinese_traditional_food.machine_has_power"
                                : "tooltip.chinese_traditional_food.machine_no_power",
                        machine.getEnergy(), machine.getEnergyCapacity()));
            }
            return InteractionResult.SUCCESS;
        }

        if (!level.isClientSide()) {
            player.openMenu(this.menuProvider(machine));
        }
        return InteractionResult.SUCCESS;
    }

    protected MenuProvider menuProvider(AbstractProcessorBlockEntity machine) {
        return new SimpleMenuProvider(
                (id, inv, player) -> ModMenus.createMenu(id, inv, machine),
                Component.translatable(this.containerKey()));
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state,
                                                                  BlockEntityType<T> type) {
        if (level.isClientSide()) {
            return null;    // 加工逻辑只在服务端跑
        }
        return (lvl, pos, st, be) -> {
            if (be instanceof AbstractProcessorBlockEntity machine) {
                AbstractProcessorBlockEntity.serverTick(lvl, pos, st, machine);
            }
        };
    }
}
