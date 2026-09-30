package com.ctf.chinese_traditional_food.common.block.entity;

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
import org.jetbrains.annotations.Nullable;

/**
 * 自研装置（水磨 / 脱壳机）的公共方块实体。
 *
 * <p>结构：两个槽位 —— 0 进料、1 出料；外加一个进度计数器。有动力时每 tick 推进，
 * 进度满就消耗一个输入、产出结果与可能的副产物。</p>
 *
 * <p>用 {@link SimpleContainer} <b>做委托</b>而不是自己实现 {@code Container}：
 * 后者有一大堆必须实现的方法，用现成的容器更稳，
 * 而且 NeoForge 的 {@code VanillaContainerWrapper.of(container)} 能直接把它
 * 适配成新的传输 API（{@code ResourceHandler<ItemResource>}），
 * 这样漏斗 / 管道就能和它交互。</p>
 */
public abstract class AbstractProcessorBlockEntity extends BlockEntity implements ContainerData {
    public static final int SLOT_INPUT = 0;
    public static final int SLOT_OUTPUT = 1;
    public static final int SIZE = 2;

    /** 同步到界面的两个整数在 {@link ContainerData} 里的下标。 */
    private static final int DATA_PROGRESS = 0;
    private static final int DATA_MAX_PROGRESS = 1;

    private final SimpleContainer inventory = new SimpleContainer(SIZE) {
        @Override
        public void setChanged() {
            super.setChanged();
            AbstractProcessorBlockEntity.this.setChanged();
        }
    };

    // protected 而不是 private：这些字段会被下面的 static serverTick 访问。
    // 注意不能用泛型形参来访问 private 成员（Java 不允许通过类型变量访问
    // 声明类自己的 private 成员），所以 serverTick 也取了具体类型。
    protected int progress;
    protected int maxProgress;

    protected AbstractProcessorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    /** 这台机器属于哪一类处理（决定查哪张表）。 */
    protected abstract Kind kind();

    /**
     * 当前是否有动力。
     *
     * @param level 服务端世界
     */
    protected abstract boolean hasPower(Level level);

    /** 暴露给能力系统的容器。 */
    public SimpleContainer getInventory() {
        return this.inventory;
    }

    // ------------------------------------------------------------------
    // 主循环
    // ------------------------------------------------------------------

    /** 由方块注册为 ticker 调用的静态入口。 */
    public static void serverTick(Level level, BlockPos pos, BlockState state,
                                  AbstractProcessorBlockEntity be) {
        if (level.isClientSide()) {
            return;
        }

        boolean changed = false;

        if (!be.hasPower(level)) {
            // 没动力：进度缓慢回退（模拟"停下"），但不清零得太快
            if (be.progress > 0) {
                be.progress = Math.max(0, be.progress - 2);
                changed = true;
            }
        } else {
            ItemStack input = be.inventory.getItem(SLOT_INPUT);
            ProcessRecipes.Resolved rule = input.isEmpty()
                    ? null
                    : ProcessRecipes.find(be.kind(), input);

            if (rule == null) {
                if (be.progress != 0) {
                    be.progress = 0;
                    be.maxProgress = 0;
                    changed = true;
                }
            } else {
                if (be.maxProgress != rule.ticks()) {
                    be.maxProgress = rule.ticks();
                    changed = true;
                }
                be.progress++;
                changed = true;

                if (be.progress >= be.maxProgress) {
                    if (be.complete(rule)) {
                        be.progress = 0;
                    } else {
                        // 出料口放不下：停在满进度，等玩家腾位置
                        be.progress = be.maxProgress;
                    }
                }
            }
        }

        if (changed) {
            be.setChanged();
            // 让客户端知道进度变了（界面上的进度条要用）
            if (be.level != null) {
                BlockState s = be.getBlockState();
                be.level.sendBlockUpdated(pos, s, s, Block.UPDATE_CLIENTS);
            }
        }
    }

    /** 结算一次产出。出料口放不下时返回 {@code false}。 */
    protected boolean complete(ProcessRecipes.Resolved rule) {
        ItemStack output = rule.result().copy();
        ItemStack existing = this.inventory.getItem(SLOT_OUTPUT);

        if (!existing.isEmpty()) {
            if (!ItemStack.isSameItemSameComponents(existing, output)) {
                return false;
            }
            if (existing.getCount() + output.getCount() > existing.getMaxStackSize()) {
                return false;
            }
            existing.grow(output.getCount());
        } else {
            this.inventory.setItem(SLOT_OUTPUT, output);
        }

        this.inventory.getItem(SLOT_INPUT).shrink(1);

        // 副产物：能塞进出料口就塞，塞不下就掉在机器上方
        ItemStack extra = ProcessRecipes.rollByproduct(rule, this.level.getRandom());
        if (!extra.isEmpty()) {
            this.pushOut(extra);
        }
        return true;
    }

    /** 把多余的东西塞进出料口，塞不下就掉落。 */
    private void pushOut(ItemStack stack) {
        ItemStack slot = new ItemStack(this.inventory.getItem(SLOT_OUTPUT).getItem(),
                this.inventory.getItem(SLOT_OUTPUT).getCount());
        if (!slot.isEmpty() && ItemStack.isSameItemSameComponents(slot, stack)
                && slot.getCount() + stack.getCount() <= slot.getMaxStackSize()) {
            slot.grow(stack.getCount());
            this.inventory.setItem(SLOT_OUTPUT, slot);
            return;
        }
        if (this.level != null) {
            Containers.dropItemStack(this.level,
                    this.worldPosition.getX() + 0.5, this.worldPosition.getY() + 1.0,
                    this.worldPosition.getZ() + 0.5, stack);
        }
    }

    /** 手动操作一次（脱壳机的手摇柄）。忽略动力，直接结算。 */
    public boolean processOnce() {
        if (this.level == null || this.level.isClientSide()) {
            return false;
        }
        ItemStack input = this.inventory.getItem(SLOT_INPUT);
        if (input.isEmpty()) {
            return false;
        }
        ProcessRecipes.Resolved rule = ProcessRecipes.find(this.kind(), input);
        if (rule == null || !this.complete(rule)) {
            return false;
        }
        this.progress = 0;
        this.setChanged();
        BlockState state = this.getBlockState();
        this.level.sendBlockUpdated(this.worldPosition, state, state, Block.UPDATE_CLIENTS);
        return true;
    }

    // ------------------------------------------------------------------
    // ContainerData：把进度同步到界面
    // ------------------------------------------------------------------

    @Override
    public int getCount() {
        return 2;
    }

    @Override
    public int get(int dataId) {
        return switch (dataId) {
            case DATA_PROGRESS -> this.progress;
            case DATA_MAX_PROGRESS -> this.maxProgress;
            default -> 0;
        };
    }

    @Override
    public void set(int dataId, int value) {
        // 服务端写入、客户端只读；这里服务端不需要被界面反向写
        if (dataId == DATA_PROGRESS) {
            this.progress = value;
        } else if (dataId == DATA_MAX_PROGRESS) {
            this.maxProgress = value;
        }
    }

    // ------------------------------------------------------------------
    // 存档 / 同步
    // ------------------------------------------------------------------

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putInt("progress", this.progress);
        output.putInt("maxProgress", this.maxProgress);
        output.store("input", ItemStack.OPTIONAL_CODEC, this.inventory.getItem(SLOT_INPUT));
        output.store("output", ItemStack.OPTIONAL_CODEC, this.inventory.getItem(SLOT_OUTPUT));
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        this.progress = input.getIntOr("progress", 0);
        this.maxProgress = input.getIntOr("maxProgress", 0);
        this.inventory.setItem(SLOT_INPUT,
                input.read("input", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY));
        this.inventory.setItem(SLOT_OUTPUT,
                input.read("output", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY));
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

    /** 机器被拆掉时把里面的东西吐出来。 */
    @Override
    public void preRemoveSideEffects(BlockPos pos, BlockState state) {
        if (this.level != null && !this.level.isClientSide()) {
            for (int i = 0; i < SIZE; i++) {
                ItemStack stack = this.inventory.getItem(i);
                if (!stack.isEmpty()) {
                    Containers.dropItemStack(this.level, pos.getX() + 0.5, pos.getY() + 0.5,
                            pos.getZ() + 0.5, stack);
                }
            }
        }
        super.preRemoveSideEffects(pos, state);
    }

    /** 给界面用的只读视图。 */
    public int getProgress() {
        return this.progress;
    }

    public int getMaxProgress() {
        return this.maxProgress;
    }
}
