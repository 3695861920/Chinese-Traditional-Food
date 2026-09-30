package com.ctf.chinese_traditional_food.common.block.entity;

import java.util.List;
import java.util.function.Predicate;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
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
import com.mojang.serialization.Codec;
import org.jetbrains.annotations.Nullable;

/**
 * "可以摆菜"的方块实体的公共父类。
 *
 * <p>核心职责：</p>
 * <ol>
 *   <li>存一组 {@link ItemStack}（几份菜），支持存档 / 读档；</li>
 *   <li>内容变化时标记脏并同步给客户端（客户端渲染器要看到盘里的菜）；</li>
 *   <li>被破坏时把盘里的菜吐出来。</li>
 * </ol>
 *
 * <p>注意：这里存的是"菜本身"（比如一份麻婆豆腐），
 * 一份菜吃完后槽位才会清空；所以餐盘是"可重复取食的容器"而不是一次性摆件。</p>
 */
public abstract class AbstractDishDisplayBlockEntity extends BlockEntity {
    /** 每个槽位保存一份菜。用 OPTIONAL_CODEC 是因为空槽要用 ItemStack.EMPTY 表示。 */
    private static final Codec<List<ItemStack>> DISHES_CODEC = ItemStack.OPTIONAL_CODEC.listOf();

    private final NonNullList<ItemStack> dishes;

    protected AbstractDishDisplayBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state, int capacity) {
        super(type, pos, state);
        this.dishes = NonNullList.withSize(capacity, ItemStack.EMPTY);
    }

    /** 能摆几份菜。 */
    public final int getCapacity() {
        return this.dishes.size();
    }

    public final ItemStack getDish(int slot) {
        return this.dishes.get(slot);
    }

    public final void setDish(int slot, ItemStack stack) {
        this.dishes.set(slot, stack);
    }

    /** 取出并清空指定槽位。 */
    public final ItemStack removeDish(int slot) {
        ItemStack current = this.dishes.get(slot);
        this.dishes.set(slot, ItemStack.EMPTY);
        return current;
    }

    /** 第一个空槽位，-1 表示已满。 */
    public final int firstFreeSlot() {
        for (int i = 0; i < this.dishes.size(); i++) {
            if (this.dishes.get(i).isEmpty()) {
                return i;
            }
        }
        return -1;
    }

    /** 最后一个有菜的槽位，-1 表示空盘。 */
    public final int lastOccupiedSlot() {
        for (int i = this.dishes.size() - 1; i >= 0; i--) {
            if (!this.dishes.get(i).isEmpty()) {
                return i;
            }
        }
        return -1;
    }

    public final boolean isFull() {
        return this.firstFreeSlot() < 0;
    }

    public final boolean isEmpty() {
        return this.lastOccupiedSlot() < 0;
    }

    /** 槽位里的菜是否满足某个条件（用于"想放进去的是不是菜"这类判断）。 */
    public final boolean anyDishMatches(Predicate<ItemStack> predicate) {
        for (ItemStack dish : this.dishes) {
            if (predicate.test(dish)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 内容发生变化后必须调用：标记区块需要保存，并把方块实体数据推给客户端。
     *
     * <p>不调用 {@code sendBlockUpdated} 的话，服务端把菜放上盘子，
     * 客户端渲染器还以为盘子是空的 —— 这是新手最容易踩的坑。</p>
     */
    public void onDishesChanged() {
        this.setChanged();
        if (this.level != null && !this.level.isClientSide()) {
            BlockState state = this.getBlockState();
            this.level.sendBlockUpdated(this.getBlockPos(), state, state, Block.UPDATE_CLIENTS);
        }
    }

    /** 方块被破坏 / 被活塞推动时，把盘里的菜掉出来。 */
    @Override
    public void preRemoveSideEffects(BlockPos pos, BlockState state) {
        if (this.level != null && !this.level.isClientSide()) {
            for (int i = 0; i < this.dishes.size(); i++) {
                ItemStack dish = this.dishes.get(i);
                if (!dish.isEmpty()) {
                    Containers.dropItemStack(this.level, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, dish);
                }
            }
        }
        super.preRemoveSideEffects(pos, state);
    }

    // ------------------------------------------------------------------
    // 存档 / 读档
    // ------------------------------------------------------------------

    @Override
    public void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        List<ItemStack> saved = input.read("dishes", DISHES_CODEC).orElse(List.of());
        for (int i = 0; i < this.dishes.size(); i++) {
            this.dishes.set(i, i < saved.size() ? saved.get(i) : ItemStack.EMPTY);
        }
    }

    @Override
    public void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.store("dishes", DISHES_CODEC, List.copyOf(this.dishes));
    }

    // ------------------------------------------------------------------
    // 客户端同步（区块加载 + 方块更新两条路径）
    // ------------------------------------------------------------------

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
}
