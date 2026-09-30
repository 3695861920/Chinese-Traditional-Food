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

    /**
     * 第一个进料槽的下标。进料槽永远是 {@code 0 .. inputSlots()-1}，
     * 出料槽紧跟在后面（{@link #outputSlot()}）。
     *
     * <p>为什么把槽位做成"几号到几号"而不是写死两个常量：
     * 灶上的锅具要多几个进料口（见 {@link AbstractHeatProcessorBlockEntity}），
     * 槽位数量就得按机器变，不能用固定下标。</p>
     */
    public static final int FIRST_INPUT_SLOT = 0;

    /**
     * 同步给界面的几个数在 {@link ContainerData} 里的下标。
     *
     * <p><b>注意</b>：原版的容器数据是按 {@code short} 同步的，
     * 所以每个数都得在 ±32767 之内（见 {@code MachineEnergy.clampForSync}）。</p>
     */
    private static final int DATA_PROGRESS = 0;
    private static final int DATA_MAX_PROGRESS = 1;
    private static final int DATA_ENERGY = 2;
    /**
     * 第 4 个数：这台机器吃的是热力还是电。
     *
     * <p>只用来决定界面文案（“热量”还是“电量”），数值本身没意义。</p>
     */
    private static final int DATA_HEAT_POWERED = 3;
    /**
     * 第 5 个数：**正在加工哪个进料槽**。
     *
     * <p>有多个进料口时，机器一次只做一件事（进度条只有一条），
     * 所以必须让客户端知道"现在轮到哪一格"，界面上才能把那一格标出来；
     * 服务端也靠它判断"换槽了要重新计时"。</p>
     */
    private static final int DATA_ACTIVE_SLOT = 4;
    private static final int DATA_COUNT = 5;

    private final SimpleContainer inventory = new SimpleContainer(this.containerSize()) {
        @Override
        public void setChanged() {
            super.setChanged();
            AbstractProcessorBlockEntity.this.setChanged();
        }
    };

    /**
     * 内部电量。
     *
     * <p>容量与单次速率都由 {@link #machineBuffer()} / {@link #ioRate()} 决定 ——
     * 大型机把这两个数放大，其余逻辑一行都不用改。</p>
     */
    private final SimpleEnergyHandler energy;

    // protected：下面的 static serverTick 要访问（不能用泛型形参访问 private 成员）
    protected int progress;

    /** 正在加工第几个进料槽（见 {@link #DATA_ACTIVE_SLOT} 的说明）。 */
    protected int activeSlot = FIRST_INPUT_SLOT;

    protected AbstractProcessorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
        this.energy = new SimpleEnergyHandler(this.machineBuffer(),
                this.ioRate(), this.ioRate()) {
            @Override
            protected void onEnergyChanged(int previousAmount) {
                AbstractProcessorBlockEntity.this.setChanged();
                AbstractProcessorBlockEntity.this.syncToClient();
            }
        };
    }

    /** 这台机器属于哪一类处理（决定查哪张表）。 */
    protected abstract Kind kind();

    // ------------------------------------------------------------------
    // 数值：小型机直接用 MachineEnergy 的常量，大型机覆写成放大版的
    // ------------------------------------------------------------------

    /** 这台是不是“大型机”。覆写时必须返回**常量** —— 构造期就会调用它。 */
    protected boolean large() {
        return false;
    }

    /** 一个批次加工多少个。 */
    protected int batchSize() {
        return this.large() ? MachineEnergy.LARGE_BATCH_SIZE : MachineEnergy.BATCH_SIZE;
    }

    /** 一个批次跑多少 tick。 */
    protected int batchTicks() {
        return this.large() ? MachineEnergy.LARGE_BATCH_TICKS : MachineEnergy.BATCH_TICKS;
    }

    /** 运行时每 tick 吃多少 FE。 */
    protected int energyPerTick() {
        return this.large() ? MachineEnergy.LARGE_ENERGY_PER_TICK : MachineEnergy.ENERGY_PER_TICK;
    }

    /** 内部缓冲容量。 */
    protected int machineBuffer() {
        return this.large() ? MachineEnergy.LARGE_MACHINE_BUFFER : MachineEnergy.MACHINE_BUFFER;
    }

    /** 单次插入 / 抽取上限。大型机管子粗，给得多。 */
    protected int ioRate() {
        return this.large() ? MachineEnergy.LARGE_GENERATOR_OUTPUT : MachineEnergy.GENERATOR_OUTPUT;
    }

    // ------------------------------------------------------------------
    // 槽位：进料口数量按机器变
    // ------------------------------------------------------------------

    /**
     * 有几个进料槽。
     *
     * <p>电动设备 1 个就够（漏斗一口气喂一种料）；灶上的锅具给 4 个 ——
     * 一口锅同时备着几样配菜，比一次只能放一种顺手得多。</p>
     *
     * <p>覆写时**必须返回常量**：构造 {@code SimpleContainer} 时就会调用它。</p>
     */
    public int inputSlots() {
        return 1;
    }

    /** 出料槽的下标，紧跟在最后一个进料槽之后。 */
    public final int outputSlot() {
        return this.inputSlots();
    }

    /** 容器总槽数 = 进料槽 + 1 个出料槽。 */
    public final int containerSize() {
        return this.inputSlots() + 1;
    }

    /** 这个下标是不是进料槽。 */
    public final boolean isInputSlot(int slot) {
        return slot >= FIRST_INPUT_SLOT && slot < this.outputSlot();
    }

    // ------------------------------------------------------------------
    // 动力：默认吃电；灶上的锅具（炒锅 / 蒸笼 / 汤锅）覆写成"吃热力"
    // ------------------------------------------------------------------

    /**
     * 现在能不能开工。
     *
     * <p>默认实现是"电量够跑一 tick"。{@code AbstractHeatProcessorBlockEntity}
     * 把它覆写成"下面有热源" —— 于是整条主循环（扣动力、推进度、结算批次）
     * 一行都不用改，两种动力的机器共用同一套逻辑。</p>
     */
    protected boolean hasPower() {
        return this.energy.getAmountAsLong() >= this.energyPerTick();
    }

    /** 扣掉一 tick 的动力。 */
    protected void consumePower() {
        this.energy.set((int) this.energy.getAmountAsLong() - this.energyPerTick());
    }

    /** 界面里那根竖条要显示的数值。默认是电量。 */
    public int getPowerForDisplay() {
        return this.getEnergyForDisplay();
    }

    /** 界面里那根竖条的满值。 */
    public int getPowerCapacityForDisplay() {
        return MachineEnergy.clampForSync(this.getEnergyCapacity());
    }

    /** 界面用：这台机器吃的是热力（灶上的锅具）还是电（电动设备）。 */
    public boolean heatPowered() {
        return false;
    }

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
            if (machine.activeSlot != FIRST_INPUT_SLOT) {
                machine.activeSlot = FIRST_INPUT_SLOT;
                dirty = true;
            }
        } else if (!machine.hasPower()) {
            // 2) 没动力（没电 / 灶上没火）：原地等，进度不清零
            //    （什么也不做，等发电机把电送过来、或炉灶点着火，接着跑）
        } else {
            // 3) 有活干又有动力：扣动力、推进度
            //
            //    换槽 = 换菜谱，所以进度要**从头算**。否则会出现
            //    "刚放了新东西进去，因为上一道菜的进度还在，一眨眼就出锅了"。
            int slot = machine.activeInputSlot();
            if (slot != machine.activeSlot) {
                machine.activeSlot = slot;
                machine.progress = 0;
            }

            machine.consumePower();
            machine.progress++;
            dirty = true;

            if (machine.progress >= machine.batchTicks()) {
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
     * 现在该做哪个进料槽里的东西 —— 返回**第一个**能加工的槽。
     *
     * <p>"第一个"而不是"轮流"：这样机器对玩家是可预测的。
     * 想让某样先做，把它放到靠前的槽里就行，不需要研究调度算法。</p>
     */
    private int activeInputSlot() {
        for (int slot = FIRST_INPUT_SLOT; slot < this.outputSlot(); slot++) {
            ItemStack input = this.inventory.getItem(slot);
            if (!input.isEmpty() && ProcessRecipes.find(this.kind(), input) != null) {
                return slot;
            }
        }
        return FIRST_INPUT_SLOT;
    }

    /**
     * 这一批打算加工几个（服务端算，不消耗）。
     *
     * <p>取三者的最小值：批次上限、进料数量、出料口还能放下的数量。
     * 返回 0 表示这一批做不了（没料 / 出料满 / 配方不认识）。</p>
     */
    private int plannedBatchSize() {
        ItemStack input = this.inventory.getItem(this.activeInputSlot());
        if (input.isEmpty()) {
            return 0;
        }
        ProcessRecipes.Resolved rule = ProcessRecipes.find(this.kind(), input);
        if (rule == null) {
            return 0;
        }
        int size = Math.min(this.batchSize(), input.getCount());
        // 出料口能塞下几份主产物（副产物不参与判断，塞不下就掉在机器上方）
        return Math.min(size, this.outputRoom(rule.result()));
    }

    /**
     * 有没有活可干（有材料、有配方、出料口放得下）。
     *
     * <p>给热源用：电磁炉靠这个决定"要不要给上面的锅供电" ——
     * 锅里没东西就不该白烧电。</p>
     */
    public boolean hasWork() {
        return this.plannedBatchSize() > 0;
    }

    /** 出料口还能放下几份这种东西；放不下返回 0。 */
    private int outputRoom(ItemStack product) {
        ItemStack out = this.inventory.getItem(this.outputSlot());
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
        int slot = this.activeInputSlot();
        ItemStack input = this.inventory.getItem(slot);
        ProcessRecipes.Resolved rule = ProcessRecipes.find(this.kind(), input);
        if (rule == null || count <= 0) {
            return;
        }

        ItemStack result = rule.result().copyWithCount(rule.result().getCount() * count);
        int outSlot = this.outputSlot();
        ItemStack out = this.inventory.getItem(outSlot);
        if (out.isEmpty()) {
            this.inventory.setItem(outSlot, result);
        } else {
            out.grow(result.getCount());
            this.inventory.setChanged();
        }

        input.shrink(count);
        if (input.isEmpty()) {
            this.inventory.setItem(slot, ItemStack.EMPTY);
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
        int outSlot = this.outputSlot();
        ItemStack out = this.inventory.getItem(outSlot);
        if (!out.isEmpty() && ItemStack.isSameItemSameComponents(out, stack)
                && out.getCount() + stack.getCount() <= out.getMaxStackSize()) {
            out.grow(stack.getCount());
            this.inventory.setChanged();
            return;
        }
        // 出料口塞不下也别丢：试试别的进料槽是不是同一种东西（锅有好几格）
        for (int slot = FIRST_INPUT_SLOT; slot < outSlot; slot++) {
            ItemStack other = this.inventory.getItem(slot);
            if (!other.isEmpty() && ItemStack.isSameItemSameComponents(other, stack)
                    && other.getCount() + stack.getCount() <= other.getMaxStackSize()) {
                other.grow(stack.getCount());
                this.inventory.setChanged();
                return;
            }
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
            case DATA_MAX_PROGRESS -> MachineEnergy.clampForSync(this.batchTicks());
            case DATA_ENERGY -> this.getPowerForDisplay();
            case DATA_HEAT_POWERED -> this.heatPowered() ? 1 : 0;
            case DATA_ACTIVE_SLOT -> this.activeSlot;
            default -> 0;
        };
    }

    @Override
    public void set(int dataId, int value) {
        // 服务端写入、客户端只读；界面不会反向写服务端
        if (dataId == DATA_PROGRESS) {
            this.progress = value;
        } else if (dataId == DATA_ACTIVE_SLOT) {
            this.activeSlot = value;
        }
    }

    // ------------------------------------------------------------------
    // 存档 / 同步
    // ------------------------------------------------------------------

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putInt("progress", this.progress);
        output.putInt("activeSlot", this.activeSlot);
        // 槽位数量是**代码里定死的**，所以直接按容器顺序存一个列表，
        // 比每个槽起一个名字更省事、也不会因为改槽位数而漏存。
        for (int slot = 0; slot < this.containerSize(); slot++) {
            output.store("slot" + slot, ItemStack.OPTIONAL_CODEC, this.inventory.getItem(slot));
        }
        this.energy.serialize(output.child("energy"));
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        this.progress = input.getIntOr("progress", 0);
        this.activeSlot = input.getIntOr("activeSlot", FIRST_INPUT_SLOT);
        for (int slot = 0; slot < this.containerSize(); slot++) {
            this.inventory.setItem(slot,
                    input.read("slot" + slot, ItemStack.OPTIONAL_CODEC)
                            .orElse(ItemStack.EMPTY));
        }
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
            for (int i = 0; i < this.containerSize(); i++) {
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
