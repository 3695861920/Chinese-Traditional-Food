package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import net.minecraft.core.BlockPos;
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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.neoforged.neoforge.transfer.energy.EnergyHandler;
import net.neoforged.neoforge.transfer.energy.SimpleEnergyHandler;
import net.neoforged.neoforge.transfer.transaction.TransactionContext;
import org.jetbrains.annotations.Nullable;

/**
 * 电力加工设备（电动磨粉机 / 电动脱壳机）的公共方块实体。
 *
 * <h2>加工规则</h2>
 * <ul>
 *   <li>一个<b>批次</b> = {@value MachineEnergy#BATCH_SIZE} 个物品，
 *       耗时 {@value MachineEnergy#BATCH_TICKS} tick（10 秒）；</li>
 *   <li>运行期间每 tick 吃 {@link MachineEnergy#ENERGY_PER_TICK} FE，
 *       所以一批正好 2000 FE；</li>
 *   <li>没电时进度<b>原地等待</b>（不倒退），来电接着走 ——
 *       这样接上发电机之后不用重新开始。</li>
 * </ul>
 *
 * <h2>为什么用 SimpleEnergyHandler</h2>
 * NeoForge 26.1 的能量统一是 {@code EnergyHandler} + 事务（transaction）。
 * {@link SimpleEnergyHandler} 已经把"容量 / 单次上限 / 存档 / 事务回滚"都做好了，
 * 我只需要覆写 {@link SimpleEnergyHandler#onEnergyChanged} 去标脏和同步客户端。
 */
public abstract class AbstractProcessorBlockEntity extends BlockEntity
        implements ContainerData {
    public static final int SLOT_INPUT = 0;
    public static final int SLOT_OUTPUT = 1;
    public static final int SIZE = 2;

    /** 同步给界面的三个数在 {@link ContainerData} 里的下标。 */
    private static final int DATA_PROGRESS = 0;
    private static final int DATA_MAX_PROGRESS = 1;
    private static final int DATA_ENERGY = 2;
    private static final int DATA_COUNT = 3;

    private final SimpleContainer inventory = new SimpleContainer(SIZE) {
        @Override
        public void setChanged() {
            super.setChanged();
            AbstractProcessorBlockEntity.this.setChanged();
        }
    };

    /**
     * 内部电量。
     *
     * <p>单次插入 / 抽取上限各给 {@link MachineEnergy#GENERATOR_OUTPUT} 级别就够 ——
     * 管道和邻居发电机都按这个速率来。</p>
     */
    private final SimpleEnergyHandler energy = new SimpleEnergyHandler(
            MachineEnergy.MACHINE_BUFFER,
            MachineEnergy.GENERATOR_OUTPUT,
            MachineEnergy.GENERATOR_OUTPUT) {
        @Override
        protected void onEnergyChanged(int previousAmount) {
            AbstractProcessorBlockEntity.this.setChanged();
            AbstractProcessorBlockEntity.this.syncToClient();
        }
    };

    // protected：下面的 static serverTick 要访问（不能用泛型形参访问 private 成员）
    protected int progress;

    protected AbstractProcessorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    /** 这台机器属于哪一类处理（决定查哪张表）。 */
    protected abstract Kind kind();

    /** 暴露给能力系统的容器。 */
    public SimpleContainer getInventory() {
        return this.inventory;
    }

    /** 暴露给能力系统的能量存储。 */
    public EnergyHandler getEnergyHandler() {
        return this.energy;
    }

    public int getEnergy() {
        return (int) this.energy.getAmountAsLong();
    }

    public int getEnergyCapacity() {
        return (int) this.energy.getCapacityAsLong();
    }

    /** 界面用：把电量夹到安全范围（原值就是 FE，容量只有 4000）。 */
    public int getEnergyForDisplay() {
        return MachineEnergy.clampForSync(this.getEnergy());
    }

    // ------------------------------------------------------------------
    // 主循环
    // ------------------------------------------------------------------

    /**
     * 由方块注册为 ticker 调用的静态入口。
     *
     * <p>注意这里取的是<b>具体类型</b>而不是泛型形参：Java 不允许通过类型变量
     * 访问声明类自己的 private / protected 成员。</p>
     */
    public static void serverTick(Level level, BlockPos pos, BlockState state,
                                  AbstractProcessorBlockEntity machine) {
        if (level.isClientSide()) {
            return;
        }

        boolean dirty = false;

        // 1) 先看有没有活干、出料口放不放得下
        int batch = machine.plannedBatchSize();
        if (batch <= 0) {
            // 没活干：进度直接归零（不像以前那样缓慢回退，归一更符合直觉）
            if (machine.progress != 0) {
                machine.progress = 0;
                dirty = true;
            }
        } else if (machine.energy.getAmountAsLong() < MachineEnergy.ENERGY_PER_TICK) {
            // 2) 没电：原地等，进度不清零
            //    （什么也不做，等发电机把电送过来接着跑）
        } else {
            // 3) 有活干又有电：扣电、推进度
            machine.energy.set((int) machine.energy.getAmountAsLong()
                    - MachineEnergy.ENERGY_PER_TICK);
            machine.progress++;
            dirty = true;

            if (machine.progress >= MachineEnergy.BATCH_TICKS) {
                machine.finishBatch(batch);
                machine.progress = 0;
            }
        }

        if (dirty) {
            machine.setChanged();
            machine.syncToClient();
        }
    }

    /**
     * 这一批打算加工几个（服务端算，不消耗）。
     *
     * <p>取三者的最小值：批次上限、进料数量、出料口还能放下的数量。
     * 返回 0 表示这一批做不了（没料 / 出料满 / 配方不认识）。</p>
     */
    private int plannedBatchSize() {
        ItemStack input = this.inventory.getItem(SLOT_INPUT);
        if (input.isEmpty()) {
            return 0;
        }
        ProcessRecipes.Resolved rule = ProcessRecipes.find(this.kind(), input);
        if (rule == null) {
            return 0;
        }
        int size = Math.min(MachineEnergy.BATCH_SIZE, input.getCount());
        // 出料口能塞下几份主产物（副产物不参与判断，塞不下就掉在机器上方）
        return Math.min(size, this.outputRoom(rule.result()));
    }

    /** 出料口还能放下几份这种东西；放不下返回 0。 */
    private int outputRoom(ItemStack product) {
        ItemStack out = this.inventory.getItem(SLOT_OUTPUT);
        int limit = product.getMaxStackSize();
        if (out.isEmpty()) {
            return limit / Math.max(1, product.getCount());
        }
        if (!ItemStack.isSameItemSameComponents(out, product)) {
            return 0;
        }
        return (limit - out.getCount()) / Math.max(1, product.getCount());
    }

    /** 结算一批：扣掉输入、放上产物与副产物。 */
    private void finishBatch(int count) {
        ItemStack input = this.inventory.getItem(SLOT_INPUT);
        ProcessRecipes.Resolved rule = ProcessRecipes.find(this.kind(), input);
        if (rule == null || count <= 0) {
            return;
        }

        ItemStack result = rule.result().copyWithCount(rule.result().getCount() * count);
        ItemStack out = this.inventory.getItem(SLOT_OUTPUT);
        if (out.isEmpty()) {
            this.inventory.setItem(SLOT_OUTPUT, result);
        } else {
            out.grow(result.getCount());
            this.inventory.setChanged();
        }

        input.shrink(count);
        if (input.isEmpty()) {
            this.inventory.setItem(SLOT_INPUT, ItemStack.EMPTY);
        }

        // 副产物按每一份各掷一次；塞不进就掉在机器上方，不吞东西
        for (int i = 0; i < count; i++) {
            ItemStack extra = ProcessRecipes.rollByproduct(rule, this.level.getRandom());
            if (!extra.isEmpty()) {
                this.pushOut(extra);
            }
        }
    }

    /** 把多余的东西塞进出料口，塞不下就丢在机器上方。 */
    private void pushOut(ItemStack stack) {
        ItemStack out = this.inventory.getItem(SLOT_OUTPUT);
        if (!out.isEmpty() && ItemStack.isSameItemSameComponents(out, stack)
                && out.getCount() + stack.getCount() <= out.getMaxStackSize()) {
            out.grow(stack.getCount());
            this.inventory.setChanged();
            return;
        }
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
    // ContainerData：把进度与电量同步到界面
    // ------------------------------------------------------------------

    @Override
    public int getCount() {
        return DATA_COUNT;
    }

    @Override
    public int get(int dataId) {
        return switch (dataId) {
            case DATA_PROGRESS -> MachineEnergy.clampForSync(this.progress);
            case DATA_MAX_PROGRESS -> MachineEnergy.clampForSync(MachineEnergy.BATCH_TICKS);
            case DATA_ENERGY -> this.getEnergyForDisplay();
            default -> 0;
        };
    }

    @Override
    public void set(int dataId, int value) {
        // 服务端写入、客户端只读；界面不会反向写服务端
        if (dataId == DATA_PROGRESS) {
            this.progress = value;
        }
    }

    // ------------------------------------------------------------------
    // 存档 / 同步
    // ------------------------------------------------------------------

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putInt("progress", this.progress);
        output.store("input", ItemStack.OPTIONAL_CODEC, this.inventory.getItem(SLOT_INPUT));
        output.store("output", ItemStack.OPTIONAL_CODEC, this.inventory.getItem(SLOT_OUTPUT));
        this.energy.serialize(output.child("energy"));
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        this.progress = input.getIntOr("progress", 0);
        this.inventory.setItem(SLOT_INPUT,
                input.read("input", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY));
        this.inventory.setItem(SLOT_OUTPUT,
                input.read("output", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY));
        // 电量可能比容量大（改过数值时），SimpleEnergyHandler 会自己处理
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

    /** 被拆掉时把进料与成品都吐出来。 */
    @Override
    public void preRemoveSideEffects(BlockPos pos, BlockState state) {
        if (this.level != null && !this.level.isClientSide()) {
            for (int i = 0; i < SIZE; i++) {
                ItemStack stack = this.inventory.getItem(i);
                if (!stack.isEmpty()) {
                    Containers.dropItemStack(this.level, pos.getX() + 0.5,
                            pos.getY() + 0.5, pos.getZ() + 0.5, stack);
                }
            }
        }
        super.preRemoveSideEffects(pos, state);
    }

    /** 供子类做自定义的能量写入（比如发电机直接灌电）。 */
    protected boolean consumeEnergy(int amount, @Nullable TransactionContext transaction) {
        return this.energy.extract(amount, transaction) == amount;
    }
}
