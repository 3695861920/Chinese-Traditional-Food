package com.ctf.chinese_traditional_food.client;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.client.render.CuttingBoardBlockEntityRenderer;
import com.ctf.chinese_traditional_food.client.render.PlateBlockEntityRenderer;
import com.ctf.chinese_traditional_food.client.render.ProcessorScreen;
import com.ctf.chinese_traditional_food.client.render.ServingPlatterBlockEntityRenderer;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import com.ctf.chinese_traditional_food.registry.ModMenus;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;

/**
 * 客户端注册（只在物理客户端加载）。
 *
 * <p>用 {@code @EventBusSubscriber} 挂在 mod 事件总线上，NeoForge 会自动发现。</p>
 */
@EventBusSubscriber(value = Dist.CLIENT, modid = ChineseTraditionalFood.MOD_ID)
public final class ClientSetup {

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        // "摆菜"类方块：把方块实体槽位里的物品画出来
        event.registerBlockEntityRenderer(ModBlockEntities.PLATE.get(),
                PlateBlockEntityRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.SERVING_PLATTER.get(),
                ServingPlatterBlockEntityRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.CUTTING_BOARD.get(),
                CuttingBoardBlockEntityRenderer::new);
        // 水磨 / 脱壳机没有额外的动态渲染，普通方块模型就够了，不注册渲染器。
    }

    @SubscribeEvent
    public static void registerScreens(RegisterMenuScreensEvent event) {
        event.register(ModMenus.PROCESSOR.get(), ProcessorScreen::new);
    }

    private ClientSetup() {}
}
