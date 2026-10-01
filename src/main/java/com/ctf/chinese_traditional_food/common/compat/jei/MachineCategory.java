package com.ctf.chinese_traditional_food.common.compat.jei;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.builder.ITooltipBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.category.IRecipeCategory;
import mezz.jei.api.recipe.types.IRecipeType;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ItemLike;
import org.jetbrains.annotations.Nullable;

/**
 * 电动磨粉机 / 电动脱壳机的 JEI 分类：一个进料槽，一个出料槽。
 *
 * <p>两类机器共用这一个类 —— 它们的配方形状完全一样（1 进 1 出，
 * 可能带副产物），差别只在"看哪张表"和"图标用哪个方块"，
 * 所以构造时把这两样传进来就够了。</p>
 *
 * <h2>副产物怎么显示</h2>
 * 有副产物的规则（比如"稻谷 → 大米 + 30% 米糠"）会在右侧多出一个槽，
 * 并在悬停提示里写明概率。概率用 tooltip 而不是直接画在图上，
 * 是因为它在图上是死的、在提示里能跟着语言走。
 */
public class MachineCategory implements IRecipeCategory<ProcessRecipes.Resolved> {

    // ---- 布局。槽统一 18×18，箭头是 JEI 自带的那张图 ----
    private static final int INPUT_X = 4;
    private static final int INPUT_Y = 4;
    private static final int ARROW_X = 26;
    private static final int ARROW_Y = 5;
    private static final int OUTPUT_X = 50;
    private static final int OUTPUT_Y = 4;
    /** 副产物槽：主产出右边，一眼看出"还有一样东西"。 */
    private static final int BYPRODUCT_X = 74;
    private static final int BYPRODUCT_Y = 4;

    private static final int WIDTH = 96;
    private static final int HEIGHT = 26;

    private final IRecipeType<ProcessRecipes.Resolved> type;
    private final Component title;
    private final IDrawable icon;
    private final IDrawable arrow;

    /**
     * @param type    看的哪张表（磨粉还是脱壳）
     * @param station 代表性方块 —— 标题名和分类图标都用它
     */
    public MachineCategory(IRecipeType<ProcessRecipes.Resolved> type, ItemLike station,
                           IGuiHelper gui) {
        this.type = type;
        this.title = new ItemStack(station.asItem()).getHoverName();
        this.icon = gui.createDrawableIngredient(VanillaTypes.ITEM_STACK,
                new ItemStack(station.asItem()));
        this.arrow = gui.getRecipeArrow();
    }

    @Override
    public IRecipeType<ProcessRecipes.Resolved> getRecipeType() {
        return this.type;
    }

    @Override
    public Component getTitle() {
        return this.title;
    }

    @Override
    public int getWidth() {
        return WIDTH;
    }

    @Override
    public int getHeight() {
        return HEIGHT;
    }

    @Override
    public IDrawable getIcon() {
        return this.icon;
    }

    @Override
    public void setRecipe(IRecipeLayoutBuilder builder, ProcessRecipes.Resolved recipe,
                          IFocusGroup focuses) {
        JeiIngredients.add(
                builder.addInputSlot(INPUT_X, INPUT_Y).setStandardSlotBackground(),
                recipe.item(), recipe.tag());

        builder.addOutputSlot(OUTPUT_X, OUTPUT_Y)
                .setOutputSlotBackground()
                .add(recipe.result());

        if (!recipe.byproduct().isEmpty()) {
            builder.addOutputSlot(BYPRODUCT_X, BYPRODUCT_Y)
                    .setOutputSlotBackground()
                    .add(recipe.byproduct())
                    .addRichTooltipCallback((slotView, tooltip) -> tooltip.add(
                            Component.translatable("jei.chinese_traditional_food.byproduct",
                                    Math.round(recipe.byproductChance() * 100.0F))));
        }
    }

    @Override
    public void draw(ProcessRecipes.Resolved recipe, IRecipeSlotsView slots,
                     GuiGraphicsExtractor guiGraphics, double mouseX, double mouseY) {
        this.arrow.draw(guiGraphics, ARROW_X, ARROW_Y);
    }

    @Override
    public void getTooltip(ITooltipBuilder tooltip, ProcessRecipes.Resolved recipe,
                           IRecipeSlotsView slots, double mouseX, double mouseY) {
        tooltip.add(JeiTexts.duration(recipe.ticks()));
    }
}
