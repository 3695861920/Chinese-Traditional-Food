package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;

/**
 * 本模组自定义的标签（Tag）。
 *
 * <p>约定：<b>通用</b>概念优先塞进 {@code c} 命名空间（如 {@code c:flour}），
 * 只有"本模组独有"的概念才用自己的命名空间，这里就是后者。</p>
 *
 * <p>标签文件路径：{@code data/chinese_traditional_food/tags/item/<path>.json}</p>
 */
public final class ModTags {
    public static final class ItemTags {
        /** 所有菜品（八大菜系 + 节日食物）。 */
        public static final TagKey<Item> DISHES = create("dishes");
        /** 可以摆到餐盘上的物品（默认 = 所有菜品 + 任何带 FOOD 组件的物品）。 */
        public static final TagKey<Item> PLACEABLE_DISHES = create("placeable_dishes");
        /** 刀具（菜刀 / 砍刀），案板切割时判定用。 */
        public static final TagKey<Item> KNIVES = create("knives");
        /** 生肉，案板切成肉丝用。 */
        public static final TagKey<Item> RAW_MEAT = create("raw_meat");
        /** 豆腐及其制品。 */
        public static final TagKey<Item> TOFU = create("tofu");

        private static TagKey<Item> create(String path) {
            return TagKey.create(Registries.ITEM, ChineseTraditionalFood.id(path));
        }

        private ItemTags() {}
    }

    public static final class BlockTags {
        /** 所有可摆放菜品的方块（餐盘、大拼盘）。 */
        public static final TagKey<Block> DISH_DISPLAYS = create("dish_displays");

        private static TagKey<Block> create(String path) {
            return TagKey.create(Registries.BLOCK, ChineseTraditionalFood.id(path));
        }

        private BlockTags() {}
    }

    private ModTags() {}
}
