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
 * 加工机（电动磨粉机 / 电动脱壳机）的界面：两个槽 + 进度箭头 + 右侧电量条。
 *
 * <h2>贴图布局（为什么画布是 256×256）</h2>
 * 底图分成两块：
 * <ul>
 *   <li>左上角 <b>0..176 × 0..166</b> 是面板，整张 blit 上去；</li>
 *   <li><b>x ≥ 176</b> 是"动态部件的满帧"条带（满箭头 / 满电量条）。</li>
 * </ul>
 *
 * <p>满帧<b>必须</b>放在面板之外：底图是整张贴上去的，画在面板里的东西
 * 一上来就会显示 —— 以前把满帧画在面板正下方，结果 0% 进度时箭头
 * 看起来已经是满的。放在外侧它才只在需要裁切时出现。</p>
 *
 * <p>也正因如此，{@code blit} 的 textureWidth/Height 要传 <b>256/256</b>：
 * 引擎按 {@code u / textureWidth} 归一化 UV，传成 176 就会错位。</p>
 */
public class ProcessorScreen extends AbstractContainerScreen<ProcessorMenu> {
    private static final Identifier TEXTURE =
            ChineseTraditionalFood.id("textures/gui/processor.png");

    /** 贴图画布尺寸 —— 必须和 PNG 一致，也是 blit 的 textureWidth/Height。 */
    private static final int TEX_W = 256;
    private static final int TEX_H = 256;
    /** 面板尺寸（贴图左上角那一块）。 */
    private static final int PANEL_W = 176;
    private static final int PANEL_H = 166;

    /** 进度箭头：面板里的位置（空帧），以及画布上满帧的位置。 */
    private static final int ARROW_X = 79;
    private static final int ARROW_Y = 34;
    private static final int ARROW_W = 24;
    private static final int ARROW_H = 17;
    private static final int ARROW_FULL_X = 176;
    private static final int ARROW_FULL_Y = 0;

    /** 竖排电量条：面板位置 + 满帧位置。 */
    private static final int ENERGY_X = 152;
    private static final int ENERGY_Y = 20;
    private static final int ENERGY_W = 16;
    private static final int ENERGY_H = 26;
    private static final int ENERGY_FULL_X = 176;
    private static final int ENERGY_FULL_Y = 40;

    private static final int TEXT_COLOR = 0xFF404040;
    private static final int WARN_COLOR = 0xFF8B2E2E;

    public ProcessorScreen(ProcessorMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
    }

    @Override
    public void extractBackground(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        // 先让原版画默认背景（暗化 + 模糊），再叠我们自己的底图
        super.extractBackground(graphics, mouseX, mouseY, partialTick);

        int x = this.leftPos;
        int y = this.topPos;
        // 面板（只取左上角那一块）
        graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x, y, 0.0F, 0.0F,
                PANEL_W, PANEL_H, TEX_W, TEX_H);

        // 进度：从满帧条带上裁左边一段，贴到箭头位置（左 -> 右填充）
        int filled = (int) (ARROW_W * this.menu.getProgressRatio());
        if (filled > 0) {
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE,
                    x + ARROW_X, y + ARROW_Y,
                    (float) ARROW_FULL_X, (float) ARROW_FULL_Y,
                    filled, ARROW_H, TEX_W, TEX_H);
        }

        // 电量：从满帧条带的底部裁一段，从下往上填
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

        // 右上角把电量写成数字 —— 进度条只能看个大概，够不够跑一批还得看数
        Component energy = Component.translatable(
                "tooltip.chinese_traditional_food.energy_amount",
                this.menu.getEnergy(), this.menu.getEnergyCapacity());
        int w = this.font.width(energy);
        graphics.text(this.font, energy,
                this.leftPos + PANEL_W - 8 - w, this.topPos + 6, TEXT_COLOR, false);

        // 没电的时候在箭头下面提一句，省得玩家对着不动的机器发呆
        if (!this.menu.hasEnergy()) {
            Component hint = Component.translatable(
                    "tooltip.chinese_traditional_food.gui_no_power");
            int hw = this.font.width(hint);
            graphics.text(this.font, hint,
                    this.leftPos + (PANEL_W - hw) / 2, this.topPos + 58,
                    WARN_COLOR, false);
        }
    }
}
