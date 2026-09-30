package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.CuttingRecipes;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import com.ctf.chinese_traditional_food.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 案板方块实体。
 *
 * <p>直接复用 {@link AbstractDishDisplayBlockEntity} 的两格存储：</p>
 * <ul>
 *   <li>槽位 {@link #SLOT_INPUT} —— 待切的食材（1 个）</li>
 *   <li>槽位 {@link #SLOT_RESULT} —— 切好的成品（可堆叠）</li>
 * </ul>
 *
 * <p>复用它的好处是白拿三件事：存档、客户端同步、方块被破坏时把东西吐出来。
 * 连渲染都省了 —— 客户端渲染器拿的就是这两个槽位里的物品。</p>
 */
public class CuttingBoardBlockEntity extends AbstractDishDisplayBlockEntity {
    public static final int SLOT_INPUT = 0;
    public static final int SLOT_RESULT = 1;
    public static final int CAPACITY = 2;

    /** 输出槽最多堆多少 —— 和普通物品一样 64。 */
    public static final int MAX_RESULT = 64;

    public CuttingBoardBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.CUTTING_BOARD.get(), pos, state);
    }

    public CuttingBoardBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state, CAPACITY);
    }

    public ItemStack getInput() {
        return this.getDish(SLOT_INPUT);
    }

    public ItemStack getResult() {
        return this.getDish(SLOT_RESULT);
    }

    public void setInput(ItemStack stack) {
        this.setDish(SLOT_INPUT, stack);
    }

    public void setResult(ItemStack stack) {
        this.setDish(SLOT_RESULT, stack);
    }

    /** 案板上有没有东西（用于判断能否放下 / 拆掉）。 */
    public boolean hasAnything() {
        return !this.getInput().isEmpty() || !this.getResult().isEmpty();
    }

    /** 玩家手持的物品是不是刀（决定「能不能切」和「要不要消耗耐久」）。 */
    public static boolean isKnife(ItemStack stack) {
        return !stack.isEmpty() && stack.is(ModTags.ItemTags.KNIVES);
    }

    /**
     * 尝试切一刀。
     *
     * @param knife 玩家手里的刀（可能为 {@link ItemStack#EMPTY}，表示徒手）
     * @return 切出了成品返回 {@code true}
     */
    public boolean tryCut(ItemStack knife) {
        ItemStack input = this.getInput();
        if (input.isEmpty()) {
            return false;
        }
        CuttingRecipes.Result result = CuttingRecipes.find(input, isKnife(knife));
        if (result == null) {
            return false;
        }
        // 输出槽放不下就不切
        ItemStack existing = this.getResult();
        ItemStack produced = result.output();
        if (!existing.isEmpty()) {
            if (!ItemStack.isSameItemSameComponents(existing, produced)) {
                return false;
            }
            if (existing.getCount() + produced.getCount() > MAX_RESULT) {
                return false;
            }
            existing.grow(produced.getCount());
        } else {
            this.setResult(produced);
        }

        // 消耗一个输入
        input.shrink(1);
        if (input.isEmpty()) {
            this.setInput(ItemStack.EMPTY);
        }

        // 用了刀就掉一点耐久。
        // 26.1 的签名是 hurtAndBreak(int, ServerLevel, LivingEntity, Consumer<ItemStack>)，
        // 传 null 表示"没有持有者"（NeoForge 自己的测试也是这么调的）。
        if (!knife.isEmpty() && isKnife(knife)
                && knife.isDamageableItem()
                && this.level instanceof net.minecraft.server.level.ServerLevel serverLevel) {
            knife.hurtAndBreak(1, serverLevel, null, stack -> {});
        }

        this.onDishesChanged();
        return true;
    }

    /** 把输入槽的东西还给玩家（空手右键取回）。 */
    @Nullable
    public ItemStack takeInput() {
        ItemStack stack = this.removeDish(SLOT_INPUT);
        if (!stack.isEmpty()) {
            this.onDishesChanged();
        }
        return stack.isEmpty() ? null : stack;
    }

    /** 把成品取走。 */
    @Nullable
    public ItemStack takeResult() {
        ItemStack stack = this.removeDish(SLOT_RESULT);
        if (!stack.isEmpty()) {
            this.onDishesChanged();
        }
        return stack.isEmpty() ? null : stack;
    }
}
