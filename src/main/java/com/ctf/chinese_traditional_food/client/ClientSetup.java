package com.ctf.chinese_traditional_food.client;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.client.render.CuttingBoardBlockEntityRenderer;
import com.ctf.chinese_traditional_food.client.render.PlateBlockEntityRenderer;
import com.ctf.chinese_traditional_food.client.render.ServingPlatterBlockEntityRenderer;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

/**
 * 客户端注册（只在物理客户端加载）。
 *
 * <p>用 {@code @EventBusSubscriber} 挂在 mod 事件总线上，NeoForge 会自动发现。</p>
 */
@EventBusSubscriber(value = Dist.CLIENT, modid = ChineseTraditionalFood.MOD_ID)
public final class ClientSetup {

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        // 把"摆菜"的方块实体和它们的渲染器配对
        event.registerBlockEntityRenderer(ModBlockEntities.PLATE.get(), PlateBlockEntityRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.SERVING_PLATTER.get(), ServingPlatterBlockEntityRenderer::new);
        event.registerBlockEntityRenderer(ModBlockEntities.CUTTING_BOARD.get(), CuttingBoardBlockEntityRenderer::new);
    }

    private ClientSetup() {}
}
