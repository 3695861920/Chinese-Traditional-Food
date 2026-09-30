package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.block.GrainShellerBlock;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.Containers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.jetbrains.annotations.Nullable;

/**
 * 手摇式脱壳机的方块实体。
 *
 * <p>和"自动机器"最大的不同：它<b>不 tick</b>。所有加工都由玩家摇柄触发，
 * 一次 {@link #crank()} 就完成一轮，所以逻辑比带进度的机器简单得多，
 * 也没有 ContainerData / 界面同步那一套。</p>
 *
 * <p>进料上限受"上方有没有料斗"影响（多方块）：
 * 裸机只能放 1 个，加了料斗可以一次倒 16 个进去慢慢摇。</p>
 *
 * <p>刻意<b>不</b>继承 {@link AbstractProcessorBlockEntity}：
 * 那个基类是给"有动力、按进度自动跑"的水磨用的，两者只有配方表是共用的。</p>
 */
public class GrainShellerBlockEntity extends BlockEntity {
    /** 裸机进料上限。 */
    public static final int CAPACITY_BARE = 1;
    /** 装上料斗后的进料上限。 */
    public static final int CAPACITY_WITH_HOPPER = 16;
    /** 出料上限（米和糠都堆在这一格里）。 */
    public static final int OUTPUT_LIMIT = 64;

    /** 进料（带壳谷物，可堆叠）。 */
    private ItemStack input = ItemStack.EMPTY;
    /** 出料（米、糠混在一起，取的时候一起给）。 */
    private ItemStack output = ItemStack.EMPTY;
    /** 累计摇过的圈数，仅供调试 / 后续做成就用。 */
    private int cranks;

    public GrainShellerBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.GRAIN_SHELLER.get(), pos, state);
    }

    public GrainShellerBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    /** 这台机器只认"脱壳"这一类规则。 */
    private static Kind shelling() {
        return Kind.SHELLING;
    }

    // ------------------------------------------------------------------
    // 进料 / 出料
    // ------------------------------------------------------------------

    public ItemStack getInput() {
        return this.input;
    }

    public ItemStack getOutput() {
        return this.output;
    }

    public int getCranks() {
        return this.cranks;
    }

    /** 当前进料上限（受料斗影响）。 */
    public int inputCapacity() {
        if (this.level == null) {
            return CAPACITY_BARE;
        }
        return GrainShellerBlock.capacityOf(this.level, this.worldPosition);
    }

    /** 还能再放几个。 */
    public int inputRoom() {
        if (this.input.isEmpty()) {
            return this.inputCapacity();
        }
        return Math.max(0, this.inputCapacity() - this.input.getCount());
    }

    /** 这个物品能不能倒进来（查得到脱壳规则就行）。 */
    public boolean accepts(ItemStack stack) {
        return !stack.isEmpty() && ProcessRecipes.find(shelling(), stack) != null;
    }

    /** 往进料里加东西（调用方负责保证不超上限）。 */
    public void insertInput(ItemStack stack) {
        if (this.input.isEmpty()) {
            this.input = stack.copy();
        } else {
            this.input.grow(stack.getCount());
        }
        this.sync();
    }

    /** 取走全部成品。 */
    public ItemStack takeOutput() {
        ItemStack out = this.output;
        this.output = ItemStack.EMPTY;
        if (!out.isEmpty()) {
            this.sync();
        }
        return out;
    }

    // ------------------------------------------------------------------
    // 摇一圈
    // ------------------------------------------------------------------

    /** 一次摇柄的结果。 */
    public enum CrankResult {
        /** 摇不动：进料是空的（或者认不出是什么）。 */
        EMPTY,
        /** 出料口放不下了。 */
        OUTPUT_FULL,
        /** 成功加工了一个。 */
        DONE,
    }

    /**
     * 摇一圈：加工一个并产出可能的副产物。
     *
     * <p>这是整台机器唯一的"工作"入口 —— 由方块在玩家潜行右键时调用。</p>
     */
    public CrankResult crank() {
        if (this.level == null || this.level.isClientSide()) {
            return CrankResult.EMPTY;
        }
        this.cranks++;
        if (this.input.isEmpty()) {
            return CrankResult.EMPTY;
        }
        ProcessRecipes.Resolved rule = ProcessRecipes.find(shelling(), this.input);
        if (rule == null) {
            return CrankResult.EMPTY;
        }

        // 先算出这一轮会产出什么（主产物 + 副产物），放不下就不摇，免得白扣料
        ItemStack main = rule.result().copy();
        ItemStack extra = ProcessRecipes.rollByproduct(rule, this.level.getRandom());
        if (!this.canFit(main) || (!extra.isEmpty() && !this.canFit(extra))) {
            return CrankResult.OUTPUT_FULL;
        }

        this.pushOut(main);
        if (!extra.isEmpty()) {
            this.pushOut(extra);
        }
        this.input.shrink(1);
        if (this.input.isEmpty()) {
            this.input = ItemStack.EMPTY;
        }
        this.sync();
        return CrankResult.DONE;
    }

    /** 出料口还放得下这些吗。 */
    private boolean canFit(ItemStack stack) {
        if (stack.isEmpty() || this.output.isEmpty()) {
            return true;
        }
        return ItemStack.isSameItemSameComponents(this.output, stack)
                && this.output.getCount() + stack.getCount() <= OUTPUT_LIMIT;
    }

    private void pushOut(ItemStack stack) {
        if (this.output.isEmpty()) {
            this.output = stack.copy();
        } else {
            this.output.grow(stack.getCount());
        }
    }

    private void sync() {
        this.setChanged();
        if (this.level != null && !this.level.isClientSide()) {
            BlockState state = this.getBlockState();
            this.level.sendBlockUpdated(this.worldPosition, state, state, Block.UPDATE_CLIENTS);
        }
    }

    // ------------------------------------------------------------------
    // 存档 / 同步
    // ------------------------------------------------------------------

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.store("input", ItemStack.OPTIONAL_CODEC, this.input);
        output.store("output", ItemStack.OPTIONAL_CODEC, this.output);
        output.putInt("cranks", this.cranks);
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        this.input = input.read("input", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY);
        this.output = input.read("output", ItemStack.OPTIONAL_CODEC).orElse(ItemStack.EMPTY);
        this.cranks = input.getIntOr("cranks", 0);
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

    /** 被拆掉时把进料和成品都吐出来。 */
    @Override
    public void preRemoveSideEffects(BlockPos pos, BlockState state) {
        if (this.level != null && !this.level.isClientSide()) {
            for (ItemStack stack : new ItemStack[] { this.input, this.output }) {
                if (!stack.isEmpty()) {
                    Containers.dropItemStack(this.level, pos.getX() + 0.5, pos.getY() + 0.5,
                            pos.getZ() + 0.5, stack);
                }
            }
        }
        super.preRemoveSideEffects(pos, state);
    }
}
