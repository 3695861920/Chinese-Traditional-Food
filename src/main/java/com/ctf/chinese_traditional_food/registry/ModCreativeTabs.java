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
                        output.accept(ModItems.CUTTING_BOARD.get());
                        output.accept(ModItems.FURNACE_GENERATOR.get());
                        output.accept(ModItems.ELECTRIC_MILL.get());
                        output.accept(ModItems.ELECTRIC_SHELLER.get());
                        output.accept(ModItems.LARGE_FURNACE_GENERATOR.get());
                        output.accept(ModItems.LARGE_ELECTRIC_MILL.get());
                        output.accept(ModItems.LARGE_ELECTRIC_SHELLER.get());
                        output.accept(ModItems.STOVE.get());
                        output.accept(ModItems.WOK.get());
                        output.accept(ModItems.STEAMER.get());
                        output.accept(ModItems.SOUP_POT.get());
                        // 食材压缩方块（生成出来的，走另一个注册表）
                        for (var item : ModCompressed.all()) {
                            output.accept(item.get());
                        }
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
            // 压缩方块也是"食材"，放进原料页最合适
            for (var item : ModCompressed.all()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.NATURAL_BLOCKS) {
            // 植株也在"自然"页 —— 找种子的时候最直觉
            for (var block : ModCrops.allPlants()) {
                event.accept(block.get());
            }
            // 果树：树苗与树叶。
            // 两者**都必须**是方块物品（ModTrees 里已经给树叶也注册了物品）——
            // accept 收的是 ItemLike，而 Block.asItem() 在没有 BlockItem 时
            // 返回空气，会直接抛 "The stack count must be 1 for 0 minecraft:air"。
            for (var item : ModTrees.allSaplings()) {
                event.accept(item.get());
            }
            for (var item : ModTrees.allLeaves()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.BUILDING_BLOCKS) {
            // 13 套木制品：原木 / 木头 / 去皮 / 木板 / 楼梯 / 台阶 / 栅栏 / 栅栏门
            for (var item : ModWoods.allItems()) {
                event.accept(item.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) {
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.FURNACE_GENERATOR.get());
            event.accept(ModItems.ELECTRIC_MILL.get());
            event.accept(ModItems.ELECTRIC_SHELLER.get());
            event.accept(ModItems.LARGE_FURNACE_GENERATOR.get());
            event.accept(ModItems.LARGE_ELECTRIC_MILL.get());
            event.accept(ModItems.LARGE_ELECTRIC_SHELLER.get());
            event.accept(ModItems.STOVE.get());
            event.accept(ModItems.WOK.get());
            event.accept(ModItems.STEAMER.get());
            event.accept(ModItems.SOUP_POT.get());
        }
        if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            // 种子是"原料"：每一样都能种下去，是整条食材线的起点
            for (var seed : ModCrops.allSeeds()) {
                event.accept(seed.get());
            }
        }
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            for (var item : ModItems.allFoods()) {
                event.accept(item.get());
            }
            event.accept(ModItems.PLATE.get());
            event.accept(ModItems.CUTTING_BOARD.get());
            event.accept(ModItems.FURNACE_GENERATOR.get());
            event.accept(ModItems.ELECTRIC_MILL.get());
            event.accept(ModItems.ELECTRIC_SHELLER.get());
            event.accept(ModItems.LARGE_FURNACE_GENERATOR.get());
            event.accept(ModItems.LARGE_ELECTRIC_MILL.get());
            event.accept(ModItems.LARGE_ELECTRIC_SHELLER.get());
            event.accept(ModItems.STOVE.get());
            event.accept(ModItems.WOK.get());
            event.accept(ModItems.STEAMER.get());
            event.accept(ModItems.SOUP_POT.get());
        }
    }

    public static void register(IEventBus modBus) {
        CREATIVE_MODE_TABS.register(modBus);
    }

    private ModCreativeTabs() {}
}
