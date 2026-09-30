package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.menu.ProcessorMenu;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Inventory;

/**
 * 自研装置的界面。
 *
 * <p>26.1 把 GUI 渲染拆成了"提取渲染状态 / 提交"两段，
 * 所以这里覆写的是 {@code extractBackground}（画底图 + 进度条）与
 * {@code extractLabels}（画标题），而<b>不是</b>老版本的 {@code renderBg}。
 * 具体做法参考了 NeoForge 自带测试里的 {@code RecipeBookTestScreen}。</p>
 */
public class ProcessorScreen extends AbstractContainerScreen<ProcessorMenu> {
    private static final Identifier TEXTURE =
            ChineseTraditionalFood.id("textures/gui/processor.png");

    /** 进度条在底图上的位置（相对界面左上角）。 */
    private static final int ARROW_X = 79;
    private static final int ARROW_Y = 34;
    private static final int ARROW_WIDTH = 24;
    private static final int ARROW_HEIGHT = 17;

    public ProcessorScreen(ProcessorMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
    }

    @Override
    public void extractBackground(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        // 先让原版画默认背景（暗化 + 模糊），再叠我们自己的底图
        super.extractBackground(graphics, mouseX, mouseY, partialTick);

        int x = this.leftPos;
        int y = this.topPos;
        graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x, y, 0.0F, 0.0F,
                this.imageWidth, this.imageHeight, 256, 256);

        // 进度条：只画左边那段，宽度按进度裁
        int filled = (int) (ARROW_WIDTH * this.menu.getProgressRatio());
        if (filled > 0) {
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE,
                    x + ARROW_X, y + ARROW_Y,
                    (float) ARROW_X, (float) (ARROW_Y + ARROW_HEIGHT),
                    filled, ARROW_HEIGHT, 256, 256);
        }
    }

    @Override
    protected void extractLabels(GuiGraphicsExtractor graphics, int mouseX, int mouseY) {
        super.extractLabels(graphics, mouseX, mouseY);
    }
}
