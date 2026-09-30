package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.menu.GeneratorMenu;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Inventory;

/**
 * 熔炉发电机的界面：燃料槽 + 火苗 + 右侧电量条。
 *
 * <p>贴图布局与坐标约定见 {@link ProcessorScreen}：
 * 画布 256×256，面板在左上角，动态部件的满帧放在 x ≥ 176 的条带上。</p>
 */
public class GeneratorScreen extends AbstractContainerScreen<GeneratorMenu> {
    private static final Identifier TEXTURE =
            ChineseTraditionalFood.id("textures/gui/generator.png");

    private static final int TEX_W = 256;
    private static final int TEX_H = 256;
    private static final int PANEL_W = 176;
    private static final int PANEL_H = 166;

    /** 火苗：面板里的位置（空帧），以及画布上满帧的位置。 */
    private static final int FLAME_X = 81;
    private static final int FLAME_Y = 54;
    private static final int FLAME_W = 14;
    private static final int FLAME_H = 14;
    private static final int FLAME_FULL_X = 176;
    private static final int FLAME_FULL_Y = 20;

    /** 竖排电量条。 */
    private static final int ENERGY_X = 152;
    private static final int ENERGY_Y = 20;
    private static final int ENERGY_W = 16;
    private static final int ENERGY_H = 26;
    private static final int ENERGY_FULL_X = 176;
    private static final int ENERGY_FULL_Y = 40;

    private static final int TEXT_COLOR = 0xFF404040;
    private static final int WARN_COLOR = 0xFF8B2E2E;

    public GeneratorScreen(GeneratorMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
    }

    @Override
    public void extractBackground(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        super.extractBackground(graphics, mouseX, mouseY, partialTick);

        int x = this.leftPos;
        int y = this.topPos;
        graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x, y, 0.0F, 0.0F,
                PANEL_W, PANEL_H, TEX_W, TEX_H);

        // 火苗：从满帧条带上裁底部一段，从下往上填
        if (this.menu.isBurning()) {
            int h = Math.max(1, (int) (FLAME_H * this.menu.getBurnRatio()));
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE,
                    x + FLAME_X, y + FLAME_Y + (FLAME_H - h),
                    (float) FLAME_FULL_X,
                    (float) (FLAME_FULL_Y + FLAME_H - h),
                    FLAME_W, h, TEX_W, TEX_H);
        }

        // 电量：同样从下往上填
        int lit = (int) (ENERGY_H * this.menu.getEnergyRatio());
        if (lit > 0) {
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE,
                    x + ENERGY_X, y + ENERGY_Y + (ENERGY_H - lit),
                    (float) ENERGY_FULL_X,
                    (float) (ENERGY_FULL_Y + ENERGY_H - lit),
                    ENERGY_W, lit, TEX_W, TEX_H);
        }
    }

    @Override
    protected void extractLabels(GuiGraphicsExtractor graphics, int mouseX, int mouseY) {
        super.extractLabels(graphics, mouseX, mouseY);

        // 右上角：电量数字
        Component energy = Component.translatable(
                "tooltip.chinese_traditional_food.energy_amount",
                this.menu.getEnergy(), this.menu.getEnergyCapacity());
        int w = this.font.width(energy);
        graphics.text(this.font, energy,
                this.leftPos + PANEL_W - 8 - w, this.topPos + 6, TEXT_COLOR, false);

        // 左侧：运行状态，缺燃料时用警示色
        Component state = Component.translatable(this.menu.isBurning()
                ? "tooltip.chinese_traditional_food.gui_burning"
                : "tooltip.chinese_traditional_food.gui_need_fuel");
        graphics.text(this.font, state, this.leftPos + 8, this.topPos + 40,
                this.menu.isBurning() ? TEXT_COLOR : WARN_COLOR, false);

        // 输出功率
        graphics.text(this.font,
                Component.translatable("tooltip.chinese_traditional_food.gui_output"),
                this.leftPos + 8, this.topPos + 52, TEXT_COLOR, false);
    }
}
