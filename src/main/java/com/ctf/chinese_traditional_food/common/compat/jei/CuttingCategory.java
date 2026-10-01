package com.ctf.chinese_traditional_food.common.compat.jei;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.recipe.CuttingRecipes;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
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

/**
 * 案板切割的 JEI 分类：左边放食材（可能是一把刀），右边出成品。
 *
 * <h2>为什么材料槽里会画一把刀</h2>
 * 表里有一条"必须手持刀"的标记（{@code needsKnife}）。JEI 的槽位是
 * <b>或</b>关系（"这些东西里的任意一样"），塞刀进去会变成"放把刀就能切"，
 * 那是错的。所以刀只在提示里说，槽里老老实实放食材。
 */
public class CuttingCategory implements IRecipeCategory<CuttingRecipes.Cut> {

    private static final IRecipeType<CuttingRecipes.Cut> TYPE =
            IRecipeType.create(ChineseTraditionalFood.id("cutting"),
                    CuttingRecipes.Cut.class);

    private static final int INPUT_X = 4;
    private static final int INPUT_Y = 5;
    private static final int ARROW_X = 46;
    private static final int ARROW_Y = 5;
    private static final int OUTPUT_X = 70;
    private static final int OUTPUT_Y = 5;

    private static final int WIDTH = 92;
    private static final int HEIGHT = 26;

    private final Component title;
    private final IDrawable icon;
    private final IDrawable arrow;

    public CuttingCategory(IGuiHelper gui) {
        ItemStack board = new ItemStack(ModBlocks.CUTTING_BOARD.get().asItem());
        this.title = board.getHoverName();
        this.icon = gui.createDrawableIngredient(VanillaTypes.ITEM_STACK, board);
        this.arrow = gui.getRecipeArrow();
    }

    @Override
    public IRecipeType<CuttingRecipes.Cut> getRecipeType() {
        return TYPE;
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
    public void setRecipe(IRecipeLayoutBuilder builder, CuttingRecipes.Cut recipe,
                          IFocusGroup focuses) {
        JeiIngredients.add(
                builder.addInputSlot(INPUT_X, INPUT_Y).setStandardSlotBackground(),
                recipe.item(), recipe.tag());

        builder.addOutputSlot(OUTPUT_X, OUTPUT_Y)
                .setOutputSlotBackground()
                .add(recipe.result());
    }

    @Override
    public void draw(CuttingRecipes.Cut recipe, IRecipeSlotsView slots,
                     GuiGraphicsExtractor guiGraphics, double mouseX, double mouseY) {
        this.arrow.draw(guiGraphics, ARROW_X, ARROW_Y);
    }

    @Override
    public void getTooltip(ITooltipBuilder tooltip, CuttingRecipes.Cut recipe,
                           IRecipeSlotsView slots, double mouseX, double mouseY) {
        if (recipe.needsKnife()) {
            tooltip.add(JeiTexts.needsKnife());
        }
    }
}
