package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.FurnaceGeneratorBlockEntity;
import com.ctf.chinese_traditional_food.common.menu.GeneratorMenu;
import com.ctf.chinese_traditional_food.common.menu.ProcessorMenu;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.MenuType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 菜单类型注册表。
 *
 * <p>两台加工机<b>共用同一个 MenuType</b> —— 它们的槽位布局完全一样，
 * 只有标题不同，而标题是服务端开界面时随菜单一起发过来的，
 * 所以没必要各注册一个类型。发电机只有 1 个燃料槽，布局不一样，
 * 单独一个类型。</p>
 */
public final class ModMenus {
    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(BuiltInRegistries.MENU, ChineseTraditionalFood.MOD_ID);

    /**
     * 加工机共用的界面类型。
     *
     * <p>注册 lambda 里通过 {@link #processorType()} 方法间接取类型，<b>不</b>直接写
     * {@code PROCESSOR.get()} —— 后者会被 javac 判为"初始化器里的自引用"。
     * 方法调用就没有这个问题，而且真正执行时注册早已完成。</p>
     */
    public static final DeferredHolder<MenuType<?>, MenuType<ProcessorMenu>> PROCESSOR =
            MENUS.register("processor", () -> new MenuType<>(
                    (containerId, inventory) -> new ProcessorMenu(
                            processorType(), containerId, inventory),
                    FeatureFlags.DEFAULT_FLAGS));

    /** 熔炉发电机的界面类型。 */
    public static final DeferredHolder<MenuType<?>, MenuType<GeneratorMenu>> GENERATOR =
            MENUS.register("generator", () -> new MenuType<>(
                    (containerId, inventory) -> new GeneratorMenu(
                            generatorType(), containerId, inventory),
                    FeatureFlags.DEFAULT_FLAGS));

    /** 取共用的加工机界面类型（方法形式，避开初始化器自引用）。 */
    public static MenuType<ProcessorMenu> processorType() {
        return PROCESSOR.get();
    }

    /** 取发电机界面类型。 */
    public static MenuType<GeneratorMenu> generatorType() {
        return GENERATOR.get();
    }

    /** 服务端开界面时用的工厂：把加工机方块实体包成菜单。 */
    public static ProcessorMenu createMenu(int containerId, Inventory playerInventory,
                                           AbstractProcessorBlockEntity machine) {
        return new ProcessorMenu(PROCESSOR.get(), containerId, playerInventory, machine);
    }

    /** 服务端开界面时用的工厂：把发电机方块实体包成菜单。 */
    public static GeneratorMenu createGeneratorMenu(int containerId, Inventory playerInventory,
                                                    FurnaceGeneratorBlockEntity generator) {
        return new GeneratorMenu(GENERATOR.get(), containerId, playerInventory, generator);
    }

    public static void register(IEventBus modBus) {
        MENUS.register(modBus);
    }

    private ModMenus() {}
}
