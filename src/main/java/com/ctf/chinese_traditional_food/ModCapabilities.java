package com.ctf.chinese_traditional_food;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.transfer.item.VanillaContainerWrapper;

/**
 * 物品能力注册。
 *
 * <p>把机器内部的 {@code SimpleContainer} 通过
 * {@link VanillaContainerWrapper#of(net.minecraft.world.Container)} 暴露成
 * NeoForge 26.1 的传输 API —— {@code ResourceHandler<ItemResource>}，
 * 挂到 {@link Capabilities.Item#BLOCK} 上。这样漏斗、管道以及其它模组的
 * 自动化设备就能直接和这两台机器交互了。</p>
 *
 * <p>注意 26.1 的写法：老的 {@code IItemHandler} / {@code Capabilities.ItemHandler}
 * 已经不存在，统一改成了 {@code ResourceHandler<ItemResource>} +
 * {@code Capabilities.Item.BLOCK}。</p>
 *
 * <p>餐盘 / 大拼盘 / 案板<b>不</b>暴露能力：它们是"给人用的"台面，
 * 不是自动化设备的对接点，挂上去反而会让漏斗把摆好的菜吸走。</p>
 *
 * <p>手摇脱壳机也<b>不</b>暴露能力：它没有界面，进料靠右键倒、脱壳靠潜行右键摇，
 * 本质上是"人力驱动的工具"而不是自动化设备；给它挂上能力只会让漏斗
 * 白白往里塞谷子却永远摇不动。</p>
 */
public final class ModCapabilities {

    public static void registerCapabilities(RegisterCapabilitiesEvent event) {
        event.registerBlockEntity(Capabilities.Item.BLOCK, ModBlockEntities.WATER_MILL.get(),
                (machine, side) -> VanillaContainerWrapper.of(machine.getInventory()));
    }

    private ModCapabilities() {}
}
