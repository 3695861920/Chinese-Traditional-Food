package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.CompressedBlock;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 食材包装方块：把 9 个散装食材打包成"一袋 / 一箱 / 一缸 / 一块"。
 *
 * <p><b>这个文件是生成出来的</b>（{@code tools/gen_compressed.py}），
 * 要加一种包装方块请改那个脚本的 {@code COMPRESSED} 表，别手改这里。</p>
 *
 * <h2>设计参考：农夫乐事的稻米袋 / 卷心菜箱</h2>
 * <ul>
 *   <li>都是<b>满格方块</b>（模型 0~16 铺满），码墙、进箱子都整齐；</li>
 *   <li><b>一眼看得出装的是什么</b>——木箱是敞口的，箱口直接铺着菜；
 *       麻袋的袋口也露出内容物；</li>
 *   <li>行为就是普通方块：能放、能挖、挖了掉自己。
 *       想拆开就放工作台上用反向配方，<b>不需要右键取出</b>。</li>
 * </ul>
 *
 * <p>为什么不给每种写一个类：包装方块的行为完全一致，唯一不同的是贴图，
 * 所以全部复用 {@link CompressedBlock}，用注册 id 区分。</p>
 */
public final class ModCompressed {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    /** 全部包装方块的方块物品，供创造标签页遍历。 */
    private static final List<DeferredItem<? extends Item>> ALL = new ArrayList<>();

    /** 米袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> RICE_BAG =
            BLOCKS.registerBlock("rice_bag", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> RICE_BAG_ITEM =
            ITEMS.registerSimpleBlockItem("rice_bag", RICE_BAG);

    /** 面粉袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> FLOUR_SACK =
            BLOCKS.registerBlock("flour_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> FLOUR_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("flour_sack", FLOUR_SACK);

    /** 米粉袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> RICE_FLOUR_SACK =
            BLOCKS.registerBlock("rice_flour_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> RICE_FLOUR_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("rice_flour_sack", RICE_FLOUR_SACK);

    /** 玉米面袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CORN_FLOUR_SACK =
            BLOCKS.registerBlock("corn_flour_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CORN_FLOUR_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("corn_flour_sack", CORN_FLOUR_SACK);

    /** 淀粉袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> STARCH_SACK =
            BLOCKS.registerBlock("starch_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> STARCH_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("starch_sack", STARCH_SACK);

    /** 小米袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> MILLET_BAG =
            BLOCKS.registerBlock("millet_bag", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> MILLET_BAG_ITEM =
            ITEMS.registerSimpleBlockItem("millet_bag", MILLET_BAG);

    /** 糯米袋（bag，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GLUTINOUS_BAG =
            BLOCKS.registerBlock("glutinous_bag", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GLUTINOUS_BAG_ITEM =
            ITEMS.registerSimpleBlockItem("glutinous_bag", GLUTINOUS_BAG);

    /** 红豆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> RED_BEAN_SACK =
            BLOCKS.registerBlock("red_bean_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> RED_BEAN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("red_bean_sack", RED_BEAN_SACK);

    /** 绿豆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> MUNG_BEAN_SACK =
            BLOCKS.registerBlock("mung_bean_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> MUNG_BEAN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("mung_bean_sack", MUNG_BEAN_SACK);

    /** 黄豆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SOYBEAN_SACK =
            BLOCKS.registerBlock("soybean_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SOYBEAN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("soybean_sack", SOYBEAN_SACK);

    /** 黑豆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BLACK_BEAN_SACK =
            BLOCKS.registerBlock("black_bean_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BLACK_BEAN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("black_bean_sack", BLACK_BEAN_SACK);

    /** 豌豆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PEA_SACK =
            BLOCKS.registerBlock("pea_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PEA_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("pea_sack", PEA_SACK);

    /** 白菜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> NAPA_CABBAGE_CRATE =
            BLOCKS.registerBlock("napa_cabbage_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> NAPA_CABBAGE_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("napa_cabbage_crate", NAPA_CABBAGE_CRATE);

    /** 萝卜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> RADISH_CRATE =
            BLOCKS.registerBlock("radish_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> RADISH_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("radish_crate", RADISH_CRATE);

    /** 番茄箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> TOMATO_CRATE =
            BLOCKS.registerBlock("tomato_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> TOMATO_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("tomato_crate", TOMATO_CRATE);

    /** 辣椒箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CHILI_CRATE =
            BLOCKS.registerBlock("chili_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CHILI_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("chili_crate", CHILI_CRATE);

    /** 黄瓜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CUCUMBER_CRATE =
            BLOCKS.registerBlock("cucumber_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CUCUMBER_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("cucumber_crate", CUCUMBER_CRATE);

    /** 茄子箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> EGGPLANT_CRATE =
            BLOCKS.registerBlock("eggplant_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> EGGPLANT_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("eggplant_crate", EGGPLANT_CRATE);

    /** 蒜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GARLIC_CRATE =
            BLOCKS.registerBlock("garlic_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GARLIC_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("garlic_crate", GARLIC_CRATE);

    /** 姜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GINGER_CRATE =
            BLOCKS.registerBlock("ginger_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GINGER_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("ginger_crate", GINGER_CRATE);

    /** 红薯箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SWEET_POTATO_CRATE =
            BLOCKS.registerBlock("sweet_potato_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SWEET_POTATO_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("sweet_potato_crate", SWEET_POTATO_CRATE);

    /** 芋头箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> TARO_CRATE =
            BLOCKS.registerBlock("taro_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> TARO_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("taro_crate", TARO_CRATE);

    /** 木耳箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> WOOD_EAR_CRATE =
            BLOCKS.registerBlock("wood_ear_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> WOOD_EAR_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("wood_ear_crate", WOOD_EAR_CRATE);

    /** 花生箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PEANUT_CRATE =
            BLOCKS.registerBlock("peanut_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PEANUT_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("peanut_crate", PEANUT_CRATE);

    /** 红枣箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> RED_DATE_CRATE =
            BLOCKS.registerBlock("red_date_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> RED_DATE_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("red_date_crate", RED_DATE_CRATE);

    /** 芝麻箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SESAME_CRATE =
            BLOCKS.registerBlock("sesame_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SESAME_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("sesame_crate", SESAME_CRATE);

    /** 笋箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BAMBOO_SHOOT_CRATE =
            BLOCKS.registerBlock("bamboo_shoot_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BAMBOO_SHOOT_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("bamboo_shoot_crate", BAMBOO_SHOOT_CRATE);

    /** 豆瓣酱缸（jar，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DOUBANJIANG_JAR =
            BLOCKS.registerBlock("doubanjiang_jar", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DOUBANJIANG_JAR_ITEM =
            ITEMS.registerSimpleBlockItem("doubanjiang_jar", DOUBANJIANG_JAR);

    /** 腌菜缸（jar，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PICKLED_JAR =
            BLOCKS.registerBlock("pickled_jar", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PICKLED_JAR_ITEM =
            ITEMS.registerSimpleBlockItem("pickled_jar", PICKLED_JAR);

    /** 豆豉缸（jar，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DOUCHI_JAR =
            BLOCKS.registerBlock("douchi_jar", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DOUCHI_JAR_ITEM =
            ITEMS.registerSimpleBlockItem("douchi_jar", DOUCHI_JAR);

    /** 花椒缸（jar，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SICHUAN_PEPPERCORN_JAR =
            BLOCKS.registerBlock("sichuan_peppercorn_jar", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SICHUAN_PEPPERCORN_JAR_ITEM =
            ITEMS.registerSimpleBlockItem("sichuan_peppercorn_jar", SICHUAN_PEPPERCORN_JAR);

    /** 豆沙块（brick，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BEAN_PASTE_BRICK =
            BLOCKS.registerBlock("bean_paste_brick", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BEAN_PASTE_BRICK_ITEM =
            ITEMS.registerSimpleBlockItem("bean_paste_brick", BEAN_PASTE_BRICK);

    /** 豆腐块（brick，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> TOFU_BRICK =
            BLOCKS.registerBlock("tofu_brick", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> TOFU_BRICK_ITEM =
            ITEMS.registerSimpleBlockItem("tofu_brick", TOFU_BRICK);

    /** 米糠块（brick，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> RICE_BRAN_BRICK =
            BLOCKS.registerBlock("rice_bran_brick", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> RICE_BRAN_BRICK_ITEM =
            ITEMS.registerSimpleBlockItem("rice_bran_brick", RICE_BRAN_BRICK);

    static {
        ALL.addAll(List.of(
            RICE_BAG_ITEM,
            FLOUR_SACK_ITEM,
            RICE_FLOUR_SACK_ITEM,
            CORN_FLOUR_SACK_ITEM,
            STARCH_SACK_ITEM,
            MILLET_BAG_ITEM,
            GLUTINOUS_BAG_ITEM,
            RED_BEAN_SACK_ITEM,
            MUNG_BEAN_SACK_ITEM,
            SOYBEAN_SACK_ITEM,
            BLACK_BEAN_SACK_ITEM,
            PEA_SACK_ITEM,
            NAPA_CABBAGE_CRATE_ITEM,
            RADISH_CRATE_ITEM,
            TOMATO_CRATE_ITEM,
            CHILI_CRATE_ITEM,
            CUCUMBER_CRATE_ITEM,
            EGGPLANT_CRATE_ITEM,
            GARLIC_CRATE_ITEM,
            GINGER_CRATE_ITEM,
            SWEET_POTATO_CRATE_ITEM,
            TARO_CRATE_ITEM,
            WOOD_EAR_CRATE_ITEM,
            PEANUT_CRATE_ITEM,
            RED_DATE_CRATE_ITEM,
            SESAME_CRATE_ITEM,
            BAMBOO_SHOOT_CRATE_ITEM,
            DOUBANJIANG_JAR_ITEM,
            PICKLED_JAR_ITEM,
            DOUCHI_JAR_ITEM,
            SICHUAN_PEPPERCORN_JAR_ITEM,
            BEAN_PASTE_BRICK_ITEM,
            TOFU_BRICK_ITEM,
            RICE_BRAN_BRICK_ITEM
        ));
    }

    /** 全部包装方块（方块物品）。 */
    public static List<DeferredItem<? extends Item>> all() {
        return ALL;
    }

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }

    private ModCompressed() {}
}
