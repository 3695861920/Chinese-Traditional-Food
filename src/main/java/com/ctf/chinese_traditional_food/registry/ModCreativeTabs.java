package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 创造模式标签页。
 *
 * <p>自带一个"国风·传统食物"主标签页；同时把代表条目挂到原版的食物 / 原材料标签页，
 * 方便在创造模式里快速找到。</p>
 */
public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ChineseTraditionalFood.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN =
            CREATIVE_MODE_TABS.register("main", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.chinese_traditional_food.main"))
                    .icon(() -> new ItemStack(ModItems.MAPO_TOFU.get()))
                    .displayItems((params, output) -> {
                        // 菜品
                        output.accept(ModItems.MAPO_TOFU.get());
                        // 基础食材
                        output.accept(ModItems.TOFU.get());
                        // 餐具：把菜摆出来的关键
                        output.accept(ModItems.PLATE.get());
                        output.accept(ModItems.SERVING_PLATTER.get());
                    })
                    .build());

    /** 追加到原版标签页（mod 事件总线，逻辑客户端）。 */
    public static void addToVanillaTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.FOOD_AND_DRINKS) {
            event.accept(ModItems.MAPO_TOFU.get());
            event.accept(ModItems.TOFU.get());
        }
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) {
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.SERVING_PLATTER.get());
        }
    }

    public static void register(IEventBus modBus) {
        CREATIVE_MODE_TABS.register(modBus);
    }

    private ModCreativeTabs() {}
}
