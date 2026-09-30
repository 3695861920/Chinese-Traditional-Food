package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
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
 * <p>水磨与脱壳机<b>共用同一个 MenuType</b> —— 两者的槽位布局完全一样，
 * 只有标题和背景图不同，而标题是服务端开界面时随菜单一起发过来的，
 * 所以没必要为它们各注册一个类型。少一个类型就少一处出错的地方。</p>
 */
public final class ModMenus {
    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(BuiltInRegistries.MENU, ChineseTraditionalFood.MOD_ID);

    /**
     * 自研装置共用的界面类型。
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

    /** 取共用的界面类型（方法形式，避开初始化器自引用）。 */
    public static MenuType<ProcessorMenu> processorType() {
        return PROCESSOR.get();
    }

    /** 服务端开界面时用的工厂：把方块实体包成菜单。 */
    public static ProcessorMenu createMenu(int containerId, Inventory playerInventory,
                                           AbstractProcessorBlockEntity machine) {
        return new ProcessorMenu(PROCESSOR.get(), containerId, playerInventory, machine);
    }

    public static void register(IEventBus modBus) {
        MENUS.register(modBus);
    }

    private ModMenus() {}
}
