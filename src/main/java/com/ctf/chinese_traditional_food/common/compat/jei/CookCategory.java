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

/**
 * 锅具（炒锅 / 蒸笼 / 汤锅）的 JEI 分类。
 *
 * <h2>为什么要排六个材料槽</h2>
 * 一道菜要的材料有多有少：一般菜四样、腊八蒜三样（其中醋要两份）、
 * 五香粉五样。槽位数量是<b>每类固定</b>的（JEI 的宽度/高度是分类级常量），
 * 所以按最多的那种排六个，空着的槽画成空的就行 ——
 * 排六个比"按最多九个原料槽排九列"窄得多，看着不散。
 *
 * <p>材料表里重复出现的东西（腊八蒜的两瓶醋）会占两个槽，
 * 这是刻意的：一眼看得出"要两份"，而不是把数量藏在提示里。</p>
 */
public class CookCategory implements IRecipeCategory<ProcessRecipes.Cook> {

    /** 材料槽的横坐标（最多六样）。 */
    private static final int[] INPUT_X = {4, 24, 44, 64, 84, 104};
    private static final int INPUT_Y = 5;
    private static final int MAX_INPUT = 6;

    private static final int ARROW_X = 128;
    private static final int ARROW_Y = 5;
    private static final int OUTPUT_X = 152;
    private static final int OUTPUT_Y = 5;

    private static final int WIDTH = 176;
    private static final int HEIGHT = 26;

    private final IRecipeType<ProcessRecipes.Cook> type;
    private final Component title;
    private final IDrawable icon;
    private final IDrawable arrow;

    /**
     * @param type    看哪张锅谱表
     * @param station 这口锅的方块 —— 标题名与分类图标都用它
     */
    public CookCategory(IRecipeType<ProcessRecipes.Cook> type, ItemLike station,
                        IGuiHelper gui) {
        this.type = type;
        this.title = new ItemStack(station.asItem()).getHoverName();
        this.icon = gui.createDrawableIngredient(VanillaTypes.ITEM_STACK,
                new ItemStack(station.asItem()));
        this.arrow = gui.getRecipeArrow();
    }

    @Override
    public IRecipeType<ProcessRecipes.Cook> getRecipeType() {
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
    public void setRecipe(IRecipeLayoutBuilder builder, ProcessRecipes.Cook recipe,
                          IFocusGroup focuses) {
        int n = Math.min(recipe.ingredients().size(), MAX_INPUT);
        for (int i = 0; i < n; i++) {
            ProcessRecipes.Resolved need = recipe.ingredients().get(i);
            JeiIngredients.add(
                    builder.addInputSlot(INPUT_X[i], INPUT_Y).setStandardSlotBackground(),
                    need.item(), need.tag());
        }

        builder.addOutputSlot(OUTPUT_X, OUTPUT_Y)
                .setOutputSlotBackground()
                .add(recipe.result());
    }

    @Override
    public void draw(ProcessRecipes.Cook recipe, IRecipeSlotsView slots,
                     GuiGraphicsExtractor guiGraphics, double mouseX, double mouseY) {
        this.arrow.draw(guiGraphics, ARROW_X, ARROW_Y);
    }

    @Override
    public void getTooltip(ITooltipBuilder tooltip, ProcessRecipes.Cook recipe,
                           IRecipeSlotsView slots, double mouseX, double mouseY) {
        tooltip.add(JeiTexts.duration(recipe.ticks()));
        tooltip.add(JeiTexts.potHint());
    }
}
