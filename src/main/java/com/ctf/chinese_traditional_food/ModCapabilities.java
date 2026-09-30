package com.ctf.chinese_traditional_food;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.transfer.item.VanillaContainerWrapper;

/**
 * 能力注册：把机器的容器与能量存储接到 NeoForge 的传输 API 上。
 *
 * <h2>物品</h2>
 * 两台加工机把内部的 {@code SimpleContainer} 通过
 * {@link VanillaContainerWrapper#of(net.minecraft.world.Container)} 暴露成
 * {@code ResourceHandler<ItemResource>}，挂在 {@link Capabilities.Item#BLOCK} 上，
 * 这样漏斗、管道就能自动送料 / 抽成品。
 *
 * <h2>能量</h2>
 * 熔炉发电机暴露自己的 {@code EnergyHandler}，两台加工机也暴露 ——
 * 既能被供电，也能被自动化设备读出电量。
 * 发电机自己用 {@code EnergyHandlerUtil.move} 往六个方向推电，靠的就是这套注册。
 *
 * <p>餐盘 / 大拼盘 / 案板不暴露能力：它们是"给人用的"台面，
 * 挂上去反而会让漏斗把摆好的菜吸走。</p>
 */
public final class ModCapabilities {

    public static void registerCapabilities(RegisterCapabilitiesEvent event) {
        // ---- 物品 ----
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.ELECTRIC_MILL.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.ELECTRIC_SHELLER.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));

        // ---- 能量 ----
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.FURNACE_GENERATOR.get(),
                (generator, side) -> generator.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.ELECTRIC_MILL.get(),
                (machine, side) -> machine.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.ELECTRIC_SHELLER.get(),
                (machine, side) -> machine.getEnergyHandler());
    }

    private ModCapabilities() {}
}
