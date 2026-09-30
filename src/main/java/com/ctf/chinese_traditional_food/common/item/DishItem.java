package com.ctf.chinese_traditional_food.common.item;

import com.ctf.chinese_traditional_food.common.food.ServeEffect;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

/**
 * 菜品物品。
 *
 * <p>比普通 {@link Item} 多了一件事：记录"<b>从餐盘上夹一口</b>"时要施加的效果。
 * 手上直接吃走原版流程（{@code FOOD} + {@code CONSUMABLE} 数据组件），
 * 从盘子里吃走 {@link #serve(Level, Player, ItemStack)}，
 * 两条路径共享同一份效果表，避免"盘子里吃没效果"这种割裂感。</p>
 */
public class DishItem extends Item {
    private final List<ServeEffect> serveEffects;

    public DishItem(Properties properties, List<ServeEffect> serveEffects) {
        super(properties);
        this.serveEffects = List.copyOf(serveEffects);
    }

    /** 从餐盘/案板上取食时施加的效果。 */
    public List<ServeEffect> getServeEffects() {
        return this.serveEffects;
    }

    /**
     * 从盘子/案板上取食一份菜：结算饥饿值、饱和度和效果。
     *
     * <p><b>只应在服务端调用。</b>调用方负责在返回 {@code true} 后扣减盘中份数。</p>
     *
     * @return 是否成功吃下一份
     */
    public static boolean serve(Level level, Player player, ItemStack dish) {
        FoodProperties food = dish.get(DataComponents.FOOD);
        if (food == null) {
            return false;
        }
        if (level.isClientSide()) {
            // 客户端只回一个"成功"让手臂摆动，实际结算在服务端
            return true;
        }
        player.getFoodData().eat(food.nutrition(), food.saturation());
        if (dish.getItem() instanceof DishItem dishItem && level instanceof ServerLevel serverLevel) {
            for (ServeEffect effect : dishItem.getServeEffects()) {
                MobEffectInstance instance = effect.roll(serverLevel.getRandom());
                if (instance != null) {
                    player.addEffect(instance);
                }
            }
        }
        // 26.1 起 GENERIC_EAT 是 Holder.Reference<SoundEvent>，要 .value() 取出本体。
        // （ITEM_FRAME_ADD_ITEM / WOOD_HIT / ITEM_PICKUP 等仍是普通 SoundEvent）
        level.playSound(null, player.blockPosition(), SoundEvents.GENERIC_EAT.value(), SoundSource.PLAYERS,
                0.8F, 0.9F + level.getRandom().nextFloat() * 0.2F);
        return true;
    }

    /** 这个物品能不能被摆到餐盘上。 */
    public static boolean isPlaceable(ItemStack stack) {
        return stack.has(DataComponents.FOOD)
                || stack.is(com.ctf.chinese_traditional_food.registry.ModTags.ItemTags.PLACEABLE_DISHES);
    }

    /**
     * 对着地面右键：把这道菜<b>直接摆在地上</b>（不需要盘子）。
     *
     * <p>规则（尽量贴近原版放置方块的直觉）：</p>
     * <ul>
     *   <li>点的是方块的<b>顶面</b>，且上方那一格可以替换；</li>
     *   <li>踩着的方块要有稳固的上表面（不能悬空放在草上）；</li>
     *   <li>潜行时不摆放 —— 把右键让给"往餐盘上放"等其它逻辑。</li>
     * </ul>
     *
     * <p>能摆的器型来自生成出来的 {@code DishPlacement}（不是每道菜一个方块）。</p>
     */
    @Override
    public InteractionResult useOn(net.minecraft.world.item.context.UseOnContext context) {
        Player player = context.getPlayer();
        if (player != null && player.isShiftKeyDown()) {
            return InteractionResult.PASS;
        }
        if (context.getClickedFace() != net.minecraft.core.Direction.UP) {
            return InteractionResult.PASS;
        }

        net.minecraft.world.level.Level level = context.getLevel();
        BlockPos supportPos = context.getClickedPos();
        BlockPos target = supportPos.above();

        if (!com.ctf.chinese_traditional_food.common.block.PlacedDishBlock.canPlaceItem(context.getItemInHand())) {
            return InteractionResult.PASS;
        }
        if (!level.getBlockState(supportPos).isFaceSturdy(level, supportPos,
                net.minecraft.core.Direction.UP)) {
            return InteractionResult.PASS;
        }
        if (!level.getBlockState(target).canBeReplaced()) {
            return InteractionResult.PASS;
        }

        if (!level.isClientSide()) {
            if (!com.ctf.chinese_traditional_food.common.block.PlacedDishBlock.place(
                    level, target, context.getItemInHand())) {
                return InteractionResult.FAIL;
            }
            if (player == null || !player.hasInfiniteMaterials()) {
                context.getItemInHand().shrink(1);
            }
        }
        return InteractionResult.SUCCESS;
    }
}
