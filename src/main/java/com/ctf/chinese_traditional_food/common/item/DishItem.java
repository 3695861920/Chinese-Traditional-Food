package com.ctf.chinese_traditional_food.common.item;

import com.ctf.chinese_traditional_food.common.food.ServeEffect;
import java.util.List;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

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
        level.playSound(null, player.blockPosition(), SoundEvents.GENERIC_EAT, SoundSource.PLAYERS,
                0.8F, 0.9F + level.getRandom().nextFloat() * 0.2F);
        return true;
    }

    /** 这个物品能不能被摆到餐盘上。 */
    public static boolean isPlaceable(ItemStack stack) {
        return stack.has(DataComponents.FOOD)
                || stack.is(com.ctf.chinese_traditional_food.registry.ModTags.ItemTags.PLACEABLE_DISHES);
    }
}
