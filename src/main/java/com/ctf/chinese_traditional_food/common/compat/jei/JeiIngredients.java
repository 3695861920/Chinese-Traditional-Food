package com.ctf.chinese_traditional_food.common.compat.jei;

import mezz.jei.api.gui.builder.IRecipeSlotBuilder;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.display.SlotDisplay;
import org.jetbrains.annotations.Nullable;

/**
 * 把本模组的"材料"塞进 JEI 槽里的小工具。
 *
 * <h2>为什么材料有两种形态</h2>
 * 配方表里的材料写成 {@code "minecraft:porkchop"} 或者
 * {@code "#c:raw_meat"} 两种。解析之后前者是具体物品、后者是标签。
 * JEI 两种都能显示，但要用不同的东西喂：
 *
 * <ul>
 *   <li>具体物品 → {@link ItemStack}；</li>
 *   <li>标签 → {@link SlotDisplay.TagSlotDisplay}（原版就是这么表达标签的）。</li>
 * </ul>
 *
 * <p>注意：<b>标签不要自己展开成物品列表</b>。展开之后 JEI 只会显示
 * 当时注册表里的那几样，别的模组后来加进这个标签的东西就看不到了；
 * 直接给标签，JEI 会自己按当前注册表解析，永远是最新的。</p>
 */
final class JeiIngredients {

    /** 按材料形态选合适的方式加进去。两种都为空表示这条材料没解析出来。 */
    static void add(IRecipeSlotBuilder slot, @Nullable Item item, @Nullable TagKey<Item> tag) {
        if (item != null) {
            slot.add(new ItemStack(item));
        } else if (tag != null) {
            slot.add(new SlotDisplay.TagSlotDisplay(tag));
        }
    }

    private JeiIngredients() {}
}
