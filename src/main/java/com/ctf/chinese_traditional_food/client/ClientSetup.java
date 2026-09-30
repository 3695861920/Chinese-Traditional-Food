package com.ctf.chinese_traditional_food.client;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.client.render.CuttingBoardBlockEntityRenderer;
import com.ctf.chinese_traditional_food.client.render.GeneratorScreen;
import com.ctf.chinese_traditional_food.client.render.PlateBlockEntityRenderer;
import com.ctf.chinese_traditional_food.client.render.ProcessorScreen;
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
        event.registerBlockEntityRenderer(ModBlockEntities.CUTTING_BOARD.get(),
                CuttingBoardBlockEntityRenderer::new);
        // 发电机 / 加工机 / 炉灶 / 锅具都没有额外的动态渲染，普通方块模型就够了。
    }

    @SubscribeEvent
    public static void registerScreens(RegisterMenuScreensEvent event) {
        // 电动设备（1 个进料槽）
        event.register(ModMenus.PROCESSOR.get(), ProcessorScreen::new);
        // 灶上锅具（4 个进料槽）—— 同一个屏幕类，布局按进料口数量自己切
        event.register(ModMenus.COOKER.get(), ProcessorScreen::new);
        event.register(ModMenus.GENERATOR.get(), GeneratorScreen::new);
        // 电磁炉没有界面：通电就亮，方块状态直接写在贴图上。
    }

    private ClientSetup() {}
}
