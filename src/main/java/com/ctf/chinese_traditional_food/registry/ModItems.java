package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.food.DishEffects;
import com.ctf.chinese_traditional_food.common.item.DishItem;
import net.minecraft.world.item.BlockItem;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 物品注册表。
 *
 * <p>本批次只放：一道示例菜（麻婆豆腐）+ 两件餐具（餐盘、大拼盘）。
 * 其余条目按 <code>docs/物品清单.md</code> 的节奏补，写法照抄这里即可。</p>
 */
public final class ModItems {
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    // ------------------------------------------------------------------
    // 基础食材 —— 豆腐（川菜的灵魂，也是本批次"能自洽跑通"的最小前置）
    // ------------------------------------------------------------------

    /**
     * 豆腐。合成：牛奶桶 + 骨粉（"点卤"），牛奶桶自带 craftRemainder 会返还空桶。
     */
    public static final DeferredItem<DishItem> TOFU = ITEMS.registerItem(
            "tofu",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(ModFoods.TOFU));

    // ------------------------------------------------------------------
    // 八大菜系 —— 示例：麻婆豆腐（川菜）
    // ------------------------------------------------------------------

    /**
     * 麻婆豆腐：7 饥饿 / 1.0 饱和，取食时获得"提神"（速度 I / 10 秒）。
     *
     * <p>{@code props.food(FoodProperties)} 会自动补上默认的 CONSUMABLE 组件，
     * 所以手持右键也能正常吃。</p>
     */
    public static final DeferredItem<DishItem> MAPO_TOFU = ITEMS.registerItem(
            "mapo_tofu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(ModFoods.MAPO_TOFU));

    // ------------------------------------------------------------------
    // 餐具（方块物品）—— 用来把菜摆出来
    // ------------------------------------------------------------------

    /** 餐盘，摆放 1 份菜。 */
    public static final DeferredItem<BlockItem> PLATE = ITEMS.registerSimpleBlockItem(ModBlocks.PLATE);

    /** 大拼盘，摆放 4 份菜。 */
    public static final DeferredItem<BlockItem> SERVING_PLATTER =
            ITEMS.registerSimpleBlockItem(ModBlocks.SERVING_PLATTER);

    public static void register(IEventBus modBus) {
        ITEMS.register(modBus);
    }

    private ModItems() {}
}
