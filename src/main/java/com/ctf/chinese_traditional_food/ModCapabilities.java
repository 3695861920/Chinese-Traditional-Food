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
        // 大型机也要挂物品能力，否则漏斗没法自动喂料 / 抽成品
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.LARGE_ELECTRIC_MILL.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.LARGE_ELECTRIC_SHELLER.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));

        // ---- 能量 ----
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.FURNACE_GENERATOR.get(),
                (generator, side) -> generator.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.ELECTRIC_MILL.get(),
                (machine, side) -> machine.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.ELECTRIC_SHELLER.get(),
                (machine, side) -> machine.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.LARGE_FURNACE_GENERATOR.get(),
                (generator, side) -> generator.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.LARGE_ELECTRIC_MILL.get(),
                (machine, side) -> machine.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.LARGE_ELECTRIC_SHELLER.get(),
                (machine, side) -> machine.getEnergyHandler());

        // ---- 灶火系统 ----
        //
        // 电磁炉是**用电**的热源，所以要挂能量能力（插上电线就能用）；
        // 三件锅具则是**刻意不挂能量能力**的 —— 它们靠正下方的电磁炉供热，
        // 如果挂上 Energy，玩家插根线就能免费炒菜，整个"灶火线"的设计就绕过去了。
        //
        // 锅具要挂**物品能力**：漏斗自动送料、往外抽成品是刚需。
        event.registerBlockEntity(Capabilities.Energy.BLOCK, ModBlockEntities.STOVE.get(),
                (stove, side) -> stove.getEnergyHandler());
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.WOK.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.STEAMER.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.SOUP_POT.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));
    }

    private ModCapabilities() {}
}
