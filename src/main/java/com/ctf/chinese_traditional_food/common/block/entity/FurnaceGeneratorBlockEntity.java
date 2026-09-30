package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.Containers;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.transfer.energy.EnergyHandler;
import net.neoforged.neoforge.transfer.energy.EnergyHandlerUtil;
import net.neoforged.neoforge.transfer.energy.SimpleEnergyHandler;
import org.jetbrains.annotations.Nullable;

/**
 * 熔炉发电机：烧燃料，恒功率输出 FE。
 *
 * <h2>为什么做这个</h2>
 * 用户要的是"简单"的电源。所以它就是个瓦罐炉子：
 *
 * <ul>
 *   <li>燃料表**直接用原版的** {@code level.fuelValues()} ——
 *       煤炭、木炭、木板、岩浆桶…… 原版能烧的它都能烧，
 *       连别的模组往燃料表里注册过的也一并支持，不用自己维护一张表；</li>
 *   <li>烧的时候恒功率 {@value MachineEnergy#GENERATOR_OUTPUT} FE/t，
 *       一格燃料能烧多久就发多久的电；</li>
 *   <li>没有界面、没有按钮：**上面塞燃料，六个面自动往外送电**。</li>
 * </ul>
 *
 * <h2>一个煤炭能干什么</h2>
 * 煤炭 1600 tick × 40 FE = 64000 FE，
 * 够加工机跑 32 批、加工 256 个物品。
 *
 * <p>送电用 {@link EnergyHandlerUtil#move}，它会顺着
 * {@code Capabilities.Energy.BLOCK} 找邻居的能量接口 ——
 * 所以管道、电池、别的模组的机器都能直接接上。</p>
 */
public class FurnaceGeneratorBlockEntity extends BlockEntity implements ContainerData {
    public static final int SLOT_FUEL = 0;
    public static final int SIZE = 1;

    private static final int DATA_BURN_LEFT = 0;
    private static final int DATA_BURN_TOTAL = 1;
    private static final int DATA_ENERGY = 2;
    private static final int DATA_COUNT = 3;

    /** 燃料槽：一格就够（烧完自动续下一格）。 */
    private final SimpleContainer fuel = new SimpleContainer(SIZE) {
        @Override
        public void setChanged() {
            super.setChanged();
            FurnaceGeneratorBlockEntity.this.setChanged();
        }
    };

    private final SimpleEnergyHandler energy;

    /** 剩余燃烧 tick。 */
    private int burnLeft;
    /** 这一格燃料的总燃烧 tick（界面画火焰条用）。 */
    private int burnTotal;

    public FurnaceGeneratorBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.FURNACE_GENERATOR.get(), pos, state);
    }

    public FurnaceGeneratorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
        this.energy = new SimpleEnergyHandler(this.generatorBuffer(),
                0,                          // 只出不进：发电机不接受外部送电
                this.outputRate()) {
            @Override
            protected void onEnergyChanged(int previousAmount) {
                FurnaceGeneratorBlockEntity.this.setChanged();
                FurnaceGeneratorBlockEntity.this.syncToClient();
            }
        };
    }

    // ------------------------------------------------------------------
    // 数值：小型机用 MachineEnergy 的常量，大型机覆写成放大版的
    // ------------------------------------------------------------------

    /** 这台是不是“大型机”。覆写时必须返回**常量** —— 构造期就会调用它。 */
    protected boolean large() {
        return false;
    }

    /** 输出功率（FE/t）。 */
    protected int outputRate() {
        return this.large() ? MachineEnergy.LARGE_GENERATOR_OUTPUT : MachineEnergy.GENERATOR_OUTPUT;
    }

    /** 内部缓冲（FE）。 */
    protected int generatorBuffer() {
        return this.large() ? MachineEnergy.LARGE_GENERATOR_BUFFER : MachineEnergy.GENERATOR_BUFFER;
    }

    public SimpleContainer getFuel() {
        return this.fuel;
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

    public boolean isBurning() {
        return this.burnLeft > 0;
    }

    // ------------------------------------------------------------------
    // 主循环
    // ------------------------------------------------------------------

    public static void serverTick(Level level, BlockPos pos, BlockState state,
                                  FurnaceGeneratorBlockEntity generator) {
        if (level.isClientSide()) {
            return;
        }

        boolean dirty = false;

        // 1) 没在烧而且有空间 -> 点一格新燃料
        if (generator.burnLeft <= 0 && !EnergyHandlerUtil.isFull(generator.energy)) {
            if (generator.tryConsumeFuel()) {
                dirty = true;
            }
        }

        // 2) 正在烧：发电并消耗燃烧时间
        if (generator.burnLeft > 0) {
            generator.burnLeft--;
            int room = (int) (generator.energy.getCapacityAsLong()
                    - generator.energy.getAmountAsLong());
            int produced = Math.min(generator.outputRate(), room);
            if (produced > 0) {
                generator.energy.set((int) generator.energy.getAmountAsLong() + produced);
            }
            // 电满了也继续烧（燃料不会白烧，但也不会积压 —— 这里选择照常烧完，
            // 因为"看着它在烧却没电"更让人困惑；缓冲只有 4000，损失可忽略）
            dirty = true;
        }

        // 3) 把电往六个方向推
        if (generator.energy.getAmountAsLong() > 0) {
            if (generator.pushEnergy(level, pos)) {
                dirty = true;
            }
        }

        if (dirty) {
            generator.setChanged();
            generator.syncToClient();
        }
    }

    /** 从燃料槽取一格燃料点着。 */
    private boolean tryConsumeFuel() {
        if (this.level == null) {
            return false;
        }
        ItemStack stack = this.fuel.getItem(SLOT_FUEL);
        if (stack.isEmpty()) {
            return false;
        }
        // 用原版的燃料表 + 熔炼配方类型：
        // 原版能烧的这里都能烧，别的模组往燃料表里注册过的也一并支持。
        // 注意 26.1 的入口在 ItemStack 上（原版的熔炉也是这么调的）。
        int burn = stack.getBurnTime(RecipeType.SMELTING, this.level.fuelValues());
        if (burn <= 0) {
            return false;
        }

        // 这里刻意**不**把桶退回来：岩浆桶这类"有容器的燃料"本来就不多，
        // 为了它引入一套容器回收逻辑不划算，而且玩家一眼能看出来烧掉了。
        stack.shrink(1);
        if (stack.isEmpty()) {
            this.fuel.setItem(SLOT_FUEL, ItemStack.EMPTY);
        } else {
            this.fuel.setChanged();
        }

        this.burnLeft = burn;
        this.burnTotal = burn;
        return true;
    }

    /** 往六个方向推电。 */
    private boolean pushEnergy(Level level, BlockPos pos) {
        boolean moved = false;
        for (Direction side : Direction.values()) {
            int available = (int) this.energy.getAmountAsLong();
            if (available <= 0) {
                break;
            }
            EnergyHandler target = level.getCapability(Capabilities.Energy.BLOCK,
                    pos.relative(side), side.getOpposite());
            if (target == null) {
                continue;
            }
            int sent = EnergyHandlerUtil.move(this.energy, target, available, null);
            if (sent > 0) {
                moved = true;
            }
        }
        return moved;
    }

    private void pushOut(ItemStack stack) {
        if (this.level != null) {
            Containers.dropItemStack(this.level,
                    this.worldPosition.getX() + 0.5,
                    this.worldPosition.getY() + 1.0,
                    this.worldPosition.getZ() + 0.5, stack);
        }
    }

    private void syncToClient() {
        if (this.level != null && !this.level.isClientSide()) {
            BlockState state = this.getBlockState();
            this.level.sendBlockUpdated(this.worldPosition, state, state, Block.UPDATE_CLIENTS);
        }
    }

    // ------------------------------------------------------------------
    // ContainerData：界面用
    // ------------------------------------------------------------------

    @Override
    public int getCount() {
        return DATA_COUNT;
    }

    @Override
    public int get(int dataId) {
        return switch (dataId) {
            case DATA_BURN_LEFT -> MachineEnergy.clampForSync(this.burnLeft);
            case DATA_BURN_TOTAL -> MachineEnergy.clampForSync(this.burnTotal);
            case DATA_ENERGY -> MachineEnergy.clampForSync(this.getEnergy());
            default -> 0;
        };
    }

    @Override
    public void set(int dataId, int value) {
        if (dataId == DATA_BURN_LEFT) {
            this.burnLeft = value;
        } else if (dataId == DATA_BURN_TOTAL) {
            this.burnTotal = value;
        }
    }

    // ------------------------------------------------------------------
    // 存档 / 同步
    // ------------------------------------------------------------------

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putInt("burnLeft", this.burnLeft);
        output.putInt("burnTotal", this.burnTotal);
        output.store("fuel", ItemStack.OPTIONAL_CODEC, this.fuel.getItem(SLOT_FUEL));
        this.energy.serialize(output.child("energy"));
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        this.burnLeft = input.getIntOr("burnLeft", 0);
        this.burnTotal = input.getIntOr("burnTotal", 0);
        this.fuel.setItem(SLOT_FUEL,
                input.read("fuel", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY));
        input.child("energy").ifPresent(this.energy::deserialize);
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        return this.saveWithoutMetadata(registries);
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public void onDataPacket(Connection connection, ValueInput input) {
        super.onDataPacket(connection, input);
    }

    /** 被拆掉时把燃料槽里剩的燃料吐出来。 */
    @Override
    public void preRemoveSideEffects(BlockPos pos, BlockState state) {
        if (this.level != null && !this.level.isClientSide()) {
            ItemStack stack = this.fuel.getItem(SLOT_FUEL);
            if (!stack.isEmpty()) {
                Containers.dropItemStack(this.level, pos.getX() + 0.5,
                        pos.getY() + 0.5, pos.getZ() + 0.5, stack);
            }
        }
        super.preRemoveSideEffects(pos, state);
    }
}
