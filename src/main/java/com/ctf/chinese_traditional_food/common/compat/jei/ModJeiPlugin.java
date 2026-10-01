package com.ctf.chinese_traditional_food.common.compat.jei;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.recipe.CuttingRecipes;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.types.IRecipeType;
import mezz.jei.api.registration.IRecipeCatalystRegistration;
import mezz.jei.api.registration.IRecipeCategoryRegistration;
import mezz.jei.api.registration.IRecipeRegistration;
import net.minecraft.resources.Identifier;

/**
 * 把本模组那些"写在代码里的配方表"搬进 JEI。
 *
 * <h2>为什么非写不可</h2>
 * 磨粉、脱壳、案板、锅谱都是<b>硬编码的 Java 常量表</b>（见 {@link ProcessRecipes}、
 * {@link CuttingRecipes}），而不是数据包里的 {@code Recipe} 对象。
 * JEI 只会自己去翻数据包加载出来的 {@code RecipeManager} —— 所以这几张表
 * 它一条也扫不到。玩家打开 JEI 看到的结果就是：本模组的菜、粉、丝，
 * <b>统统"查不到配方"</b>。
 *
 * <p>这个插件就是当<b>翻译</b>：把那些常量表翻成 JEI 认识的
 * "分类 + 配方条目"，在它启动时一条条喂过去。</p>
 *
 * <h2>六个分类</h2>
 * <table border="1">
 *   <tr><th>分类</th><th>看的表</th><th>条数</th></tr>
 *   <tr><td>电动磨粉机</td><td>{@code MILLING}</td><td>10</td></tr>
 *   <tr><td>电动脱壳机</td><td>{@code SHELLING}</td><td>2</td></tr>
 *   <tr><td>案板</td><td>{@code CUTTING}</td><td>7</td></tr>
 *   <tr><td>蒸笼 / 汤锅 / 炒锅</td><td>{@code STEAMER / SOUP_POT / WOK}</td><td>147</td></tr>
 * </table>
 *
 * <p>三口锅拆成三个分类而不是合成一个："炒菜在炒锅里做、蒸点在蒸笼里做"
 * 这件事本身就是玩家要记住的信息，分开显示比在一张长列表里混着强。</p>
 *
 * <h2>类的加载安全</h2>
 * JEI 靠 {@code @JeiPlugin} 注解 + 反射无参构造来找插件，所以：
 * <ul>
 *   <li>插件类必须<b>没有状态</b>—— 一切都等回调里再算；</li>
 *   <li>没装 JEI 的玩家<b>不会</b>加载这个类（本模组没有任何非 JEI 代码引用它），
 *       所以"配方独立于其它模组"这条承诺没有被打破。</li>
 * </ul>
 */
@JeiPlugin
public class ModJeiPlugin implements IModPlugin {

    /** 插件 id —— JEI 用它标识"这是哪个模组的插件"。 */
    private static final Identifier UID = ChineseTraditionalFood.id("jei");

    // ------------------------------------------------------------------
    // 六个配方类型
    // ------------------------------------------------------------------
    // 类型是"分类的身份"。同一个类型只能有一个分类，所以磨粉与脱壳必须分开。

    private static final IRecipeType<ProcessRecipes.Resolved> MILLING = machineType("milling");
    private static final IRecipeType<ProcessRecipes.Resolved> SHELLING = machineType("shelling");
    private static final IRecipeType<CuttingRecipes.Cut> CUTTING = cuttingType();

    private static final IRecipeType<ProcessRecipes.Cook> WOK = cookType("wok");
    private static final IRecipeType<ProcessRecipes.Cook> STEAMER = cookType("steamer");
    private static final IRecipeType<ProcessRecipes.Cook> SOUP_POT = cookType("soup_pot");

    private static IRecipeType<ProcessRecipes.Resolved> machineType(String path) {
        return IRecipeType.create(ChineseTraditionalFood.id("machine/" + path),
                ProcessRecipes.Resolved.class);
    }

    private static IRecipeType<CuttingRecipes.Cut> cuttingType() {
        return IRecipeType.create(ChineseTraditionalFood.id("cutting"),
                CuttingRecipes.Cut.class);
    }

    private static IRecipeType<ProcessRecipes.Cook> cookType(String path) {
        return IRecipeType.create(ChineseTraditionalFood.id("cooking/" + path),
                ProcessRecipes.Cook.class);
    }

    @Override
    public Identifier getPluginUid() {
        return UID;
    }

    @Override
    public void registerCategories(IRecipeCategoryRegistration registration) {
        IGuiHelper gui = registration.getJeiHelpers().getGuiHelper();

        registration.addRecipeCategories(
                new MachineCategory(MILLING, ModBlocks.ELECTRIC_MILL.get(), gui),
                new MachineCategory(SHELLING, ModBlocks.ELECTRIC_SHELLER.get(), gui),
                new CuttingCategory(gui),
                new CookCategory(WOK, ModBlocks.WOK.get(), gui),
                new CookCategory(STEAMER, ModBlocks.STEAMER.get(), gui),
                new CookCategory(SOUP_POT, ModBlocks.SOUP_POT.get(), gui));
    }

    @Override
    public void registerRecipes(IRecipeRegistration registration) {
        registration.addRecipes(MILLING, ProcessRecipes.allRules(ProcessRecipes.Kind.MILLING));
        registration.addRecipes(SHELLING, ProcessRecipes.allRules(ProcessRecipes.Kind.SHELLING));
        registration.addRecipes(CUTTING, CuttingRecipes.all());
        registration.addRecipes(WOK, ProcessRecipes.allCooks(ProcessRecipes.Kind.COOKING));
        registration.addRecipes(STEAMER, ProcessRecipes.allCooks(ProcessRecipes.Kind.STEAMING));
        registration.addRecipes(SOUP_POT, ProcessRecipes.allCooks(ProcessRecipes.Kind.BOILING));
    }

    /**
     * 登记"这台机器能做这些配方"。
     *
     * <p>不登记的话，JEI 里点某个配方不会提示"用哪台机器"；更重要的是
     * <b>按 R 查用途</b>时会因为找不到催化剂而什么都不显示。</p>
     */
    @Override
    public void registerRecipeCatalysts(IRecipeCatalystRegistration registration) {
        // 大型机走的是同一张表，所以同样是这套配方的"合法工具"
        registration.addCraftingStation(MILLING,
                ModBlocks.ELECTRIC_MILL.get(), ModBlocks.LARGE_ELECTRIC_MILL.get());
        registration.addCraftingStation(SHELLING,
                ModBlocks.ELECTRIC_SHELLER.get(), ModBlocks.LARGE_ELECTRIC_SHELLER.get());
        registration.addCraftingStation(CUTTING, ModBlocks.CUTTING_BOARD.get());
        registration.addCraftingStation(WOK, ModBlocks.WOK.get());
        registration.addCraftingStation(STEAMER, ModBlocks.STEAMER.get());
        registration.addCraftingStation(SOUP_POT, ModBlocks.SOUP_POT.get());
    }
}
