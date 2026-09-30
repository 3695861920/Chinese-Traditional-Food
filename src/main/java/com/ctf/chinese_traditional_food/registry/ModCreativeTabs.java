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
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b></p>
 */
public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ChineseTraditionalFood.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN =
            CREATIVE_MODE_TABS.register("main", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.chinese_traditional_food.main"))
                    .icon(() -> new ItemStack(ModItems.MAPO_TOFU.get()))
                    .displayItems((params, output) -> {
                        // 餐具与功能方块
                        output.accept(ModItems.PLATE.get());
                        output.accept(ModItems.SERVING_PLATTER.get());
                        output.accept(ModItems.CUTTING_BOARD.get());
                        output.accept(ModItems.FURNACE_GENERATOR.get());
                        output.accept(ModItems.ELECTRIC_MILL.get());
                        output.accept(ModItems.ELECTRIC_SHELLER.get());
                        // 其余全部内容（食材 / 调味料 / 水果 / 蔬菜 / 厨具 / 菜品）
                        for (var item : ModItems.allFoods()) {
                            output.accept(item.get());
                        }
                    })
                    .build());

    /** 追加到原版标签页（mod 事件总线，逻辑客户端）。 */
    public static void addToVanillaTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.FOOD_AND_DRINKS) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) {
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.SERVING_PLATTER.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.FURNACE_GENERATOR.get());
            event.accept(ModItems.ELECTRIC_MILL.get());
            event.accept(ModItems.ELECTRIC_SHELLER.get());
        }
        if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.SERVING_PLATTER.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.FURNACE_GENERATOR.get());
            event.accept(ModItems.ELECTRIC_MILL.get());
            event.accept(ModItems.ELECTRIC_SHELLER.get());
        }
    }

    public static void register(IEventBus modBus) {
        CREATIVE_MODE_TABS.register(modBus);
    }

    private ModCreativeTabs() {}
}
