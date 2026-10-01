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

    /**
     * 多进料口机器（锅）用的另一张底图。
     *
     * <p>为什么不把两套槽位画在同一张图上：那样单进料口的机器会多出三个
     * 永远空着的格子，玩家会以为"还有别的位置能放料"。分开两张最诚实。</p>
     */
    private static final Identifier TEXTURE_COOKER =
            ChineseTraditionalFood.id("textures/gui/cooker.png");

    /** 贴图画布尺寸 —— 必须和 PNG 一致，也是 blit 的 textureWidth/Height。 */
    private static final int TEX_W = 256;
    private static final int TEX_H = 256;
    /** 面板尺寸（贴图左上角那一块）。 */
    private static final int PANEL_W = 176;
    private static final int PANEL_H = 166;

    // ---- 单进料口：箭头在槽位右边 ----
    private static final int ARROW_X = 79;
    private static final int ARROW_Y = 34;
    private static final int ARROW_W = 24;
    private static final int ARROW_H = 17;

    // ---- 九进料口（锅）：3×3 原料区占得宽，箭头相应右移 ----
    private static final int COOKER_ARROW_X = 86;
    private static final int COOKER_ARROW_Y = 37;

    /** 满帧（箭头 / 动力条）一律画在面板右侧的条带上，两张图共用同一坐标。 */
    private static final int ARROW_FULL_X = 176;
    private static final int ARROW_FULL_Y = 0;

    /** 竖排动力条：电动设备上是电量、锅上是热力。 */
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

    /** 这台机器是不是多进料口（锅）。 */
    private boolean multiSlot() {
        return this.menu.inputSlots() > 1;
    }

    private int arrowX() {
        return this.multiSlot() ? COOKER_ARROW_X : ARROW_X;
    }

    private int arrowY() {
        return this.multiSlot() ? COOKER_ARROW_Y : ARROW_Y;
    }

    @Override
    public void extractBackground(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        // 先让原版画默认背景（暗化 + 模糊），再叠我们自己的底图
        super.extractBackground(graphics, mouseX, mouseY, partialTick);

        int x = this.leftPos;
        int y = this.topPos;
        // 面板（只取左上角那一块）
        graphics.blit(RenderPipelines.GUI_TEXTURED,
                this.multiSlot() ? TEXTURE_COOKER : TEXTURE,
                x, y, 0.0F, 0.0F, PANEL_W, PANEL_H, TEX_W, TEX_H);

        // 多进料口：把"正在加工的那一格"框出来 ——
        // 否则玩家分不清九格里到底轮到谁了
        if (this.multiSlot()) {
            int active = this.menu.getActiveSlot();
            int sx = x + ProcessorMenu.inputSlotX(active, 9) - 1;
            int sy = y + ProcessorMenu.inputSlotY(active, 9) - 1;
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE_COOKER,
                    sx, sy,
                    (float) SLOT_MARK_U, (float) SLOT_MARK_V,
                    20, 20, TEX_W, TEX_H);
        }

        // 进度：从满帧条带上裁左边一段，贴到箭头位置（左 -> 右填充）
        int filled = (int) (ARROW_W * this.menu.getProgressRatio());
        if (filled > 0) {
            graphics.blit(RenderPipelines.GUI_TEXTURED,
                    this.multiSlot() ? TEXTURE_COOKER : TEXTURE,
                    x + this.arrowX(), y + this.arrowY(),
                    (float) ARROW_FULL_X, (float) ARROW_FULL_Y,
                    filled, ARROW_H, TEX_W, TEX_H);
        }

        // 动力：从满帧条带的底部裁一段，从下往上填
        int lit = (int) (ENERGY_H * this.menu.getEnergyRatio());
        if (lit > 0) {
            graphics.blit(RenderPipelines.GUI_TEXTURED,
                    this.multiSlot() ? TEXTURE_COOKER : TEXTURE,
                    x + ENERGY_X, y + ENERGY_Y + (ENERGY_H - lit),
                    (float) ENERGY_FULL_X,
                    (float) (ENERGY_FULL_Y + ENERGY_H - lit),
                    ENERGY_W, lit, TEX_W, TEX_H);
        }
    }

    /** 选中框在贴图上的位置（放在满帧条带里，不会一开始就露出来）。 */
    private static final int SLOT_MARK_U = 176;
    private static final int SLOT_MARK_V = 140;

    @Override
    protected void extractLabels(GuiGraphicsExtractor graphics, int mouseX, int mouseY) {
        super.extractLabels(graphics, mouseX, mouseY);

        // 灶上锅具吃的是"热力"、电动设备吃的是"电量" —— 同一个界面，
        // 靠菜单同步过来的标志位换文案，免得玩家对着炒锅满世界找插口。
        boolean heat = this.menu.isHeatPowered();

        // 右上角把数值写成文字 —— 光看竖条只能看个大概
        Component power = heat
                ? Component.translatable(
                        "tooltip.chinese_traditional_food.heat_amount")
                : Component.translatable(
                        "tooltip.chinese_traditional_food.energy_amount",
                        this.menu.getEnergy(), this.menu.getEnergyCapacity());
        int w = this.font.width(power);
        graphics.text(this.font, power,
                this.leftPos + PANEL_W - 8 - w, this.topPos + 6, TEXT_COLOR, false);

        // 没动力的时候提一句，省得玩家对着不动的机器发呆
        if (!this.menu.hasEnergy()) {
            Component hint = Component.translatable(heat
                    ? "tooltip.chinese_traditional_food.gui_no_heat"
                    : "tooltip.chinese_traditional_food.gui_no_power");
            int hw = this.font.width(hint);
            graphics.text(this.font, hint,
                    this.leftPos + (PANEL_W - hw) / 2, this.topPos + 58,
                    WARN_COLOR, false);
        }
    }
}
