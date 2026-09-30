package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.block.StoveBlock;
import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.neoforged.neoforge.transfer.energy.EnergyHandler;
import net.neoforged.neoforge.transfer.energy.SimpleEnergyHandler;

/**
 * 电磁炉：用电给<b>正上方一格</b>的锅具供热。
 *
 * <h2>为什么从"烧柴的灶台"改成用电</h2>
 * 原来那台要烧燃料，于是有燃料槽、燃烧时间、火苗条、一套界面 ——
 * 一个"把锅垫高的东西"背了太多东西。改成电磁炉之后：
 *
 * <ul>
 *   <li><b>没有燃料槽</b>，插上电就能用（FE 走 {@code Capabilities.Energy.BLOCK}）；</li>
 *   <li><b>没有界面</b>：通电就亮、断电就灭，方块状态 {@code powered} 直接写在贴图上，
 *       远远看一眼就知道有没有在工作；</li>
 *   <li>它除了"有热 / 没热"之外不维护别的状态。</li>
 * </ul>
 *
 * <h2>只在真正需要时才吃电</h2>
 * 面板一直烧着电待机是很讨厌的，所以：只有上面那口锅<b>确实有活可干</b>
 * （{@link AbstractHeatProcessorBlockEntity#wantsHeat()}）时才抽电。
 * 锅里空着 = 一度电都不花。
 *
 * <h2>数值</h2>
 * 每 tick 抽 {@link MachineEnergy#STOVE_ENERGY_PER_TICK} FE，
 * 比一台加工机便宜得多 —— 灶活本来就慢，成本就该低。
 */
public class StoveBlockEntity extends BlockEntity implements HeatSource {

    /** 内部缓冲：够在电网抖动时顶一小会儿。 */
    public static final int BUFFER = 800;

    /** 接受外部送电的速率上限。 */
    public static final int INSERT_RATE = 200;

    private final SimpleEnergyHandler energy = new SimpleEnergyHandler(
            BUFFER,
            INSERT_RATE,
            0) {                       // 只进不出：电磁炉不往外送电
        @Override
        protected void onEnergyChanged(int previousAmount) {
            StoveBlockEntity.this.setChanged();
            StoveBlockEntity.this.syncToClient();
        }
    };

    /** 当前是不是在供热（会同步到方块状态，贴图跟着变）。 */
    private boolean powered;

    public StoveBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.STOVE.get(), pos, state);
    }

    public StoveBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    public EnergyHandler getEnergyHandler() {
        return this.energy;
    }

    public int getEnergy() {
        return (int) this.energy.getAmountAsLong();
    }

    public int getEnergyCapacity() {
        return (int) this.energy.getCapacityAsLong();
    }

    /** 提示用：把电量夹到同步安全范围（缓冲只有 800，本来就够）。 */
    public int getEnergyForDisplay() {
        return MachineEnergy.clampForSync(this.getEnergy());
    }

    public boolean isPowered() {
        return this.powered;
    }

    // ------------------------------------------------------------------
    // HeatSource：锅具只认"有热 / 没热"
    // ------------------------------------------------------------------

    @Override
    public int heat() {
        return this.powered ? HEAT_CAPACITY : 0;
    }

    @Override
    public int heatCapacity() {
        return HEAT_CAPACITY;
    }

    // ------------------------------------------------------------------
    // 主循环
    // ------------------------------------------------------------------

    public static void serverTick(Level level, BlockPos pos, BlockState state,
                                  StoveBlockEntity stove) {
        if (level.isClientSide()) {
            return;
        }

        // 上面有没有一口"正等着下锅"的锅？
        boolean wanted = false;
        BlockEntity above = level.getBlockEntity(pos.above());
        if (above instanceof AbstractHeatProcessorBlockEntity appliance) {
            wanted = appliance.wantsHeat();
        }

        boolean nowPowered = false;
        if (wanted && stove.energy.getAmountAsLong() >= MachineEnergy.STOVE_ENERGY_PER_TICK) {
            stove.energy.set((int) stove.energy.getAmountAsLong()
                    - MachineEnergy.STOVE_ENERGY_PER_TICK);
            nowPowered = true;
        }

        if (nowPowered != stove.powered) {
            stove.powered = nowPowered;
            // 方块状态要跟着变，贴图才会亮 / 灭
            level.setBlock(pos, state.setValue(StoveBlock.POWERED, nowPowered),
                    Block.UPDATE_ALL);
        }
        if (nowPowered) {
            stove.setChanged();
        }
    }

    private void syncToClient() {
        if (this.level != null && !this.level.isClientSide()) {
            BlockState state = this.getBlockState();
            this.level.sendBlockUpdated(this.worldPosition, state, state, Block.UPDATE_CLIENTS);
        }
    }

    // ------------------------------------------------------------------
    // 存档
    // ------------------------------------------------------------------

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putBoolean("powered", this.powered);
        this.energy.serialize(output.child("energy"));
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        this.powered = input.getBooleanOr("powered", false);
        input.child("energy").ifPresent(this.energy::deserialize);
    }
}
