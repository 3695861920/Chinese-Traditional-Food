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

    /** 豆瓣酱桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DOUBANJIANG_BARREL =
            BLOCKS.registerBlock("doubanjiang_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DOUBANJIANG_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("doubanjiang_barrel", DOUBANJIANG_BARREL);

    /** 腌菜桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PICKLED_BARREL =
            BLOCKS.registerBlock("pickled_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PICKLED_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("pickled_barrel", PICKLED_BARREL);

    /** 豆豉桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DOUCHI_BARREL =
            BLOCKS.registerBlock("douchi_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DOUCHI_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("douchi_barrel", DOUCHI_BARREL);

    /** 花椒桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SICHUAN_PEPPERCORN_BARREL =
            BLOCKS.registerBlock("sichuan_peppercorn_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SICHUAN_PEPPERCORN_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("sichuan_peppercorn_barrel", SICHUAN_PEPPERCORN_BARREL);

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

    /** 梨袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PEAR_SACK =
            BLOCKS.registerBlock("pear_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PEAR_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("pear_sack", PEAR_SACK);

    /** 桃袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PEACH_SACK =
            BLOCKS.registerBlock("peach_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PEACH_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("peach_sack", PEACH_SACK);

    /** 李子袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PLUM_SACK =
            BLOCKS.registerBlock("plum_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PLUM_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("plum_sack", PLUM_SACK);

    /** 杏袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> APRICOT_SACK =
            BLOCKS.registerBlock("apricot_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> APRICOT_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("apricot_sack", APRICOT_SACK);

    /** 枣袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> JUJUBE_SACK =
            BLOCKS.registerBlock("jujube_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> JUJUBE_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("jujube_sack", JUJUBE_SACK);

    /** 柿子袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PERSIMMON_SACK =
            BLOCKS.registerBlock("persimmon_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PERSIMMON_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("persimmon_sack", PERSIMMON_SACK);

    /** 橘子袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> MANDARIN_SACK =
            BLOCKS.registerBlock("mandarin_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> MANDARIN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("mandarin_sack", MANDARIN_SACK);

    /** 柚子袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> POMELO_SACK =
            BLOCKS.registerBlock("pomelo_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> POMELO_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("pomelo_sack", POMELO_SACK);

    /** 香蕉袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BANANA_SACK =
            BLOCKS.registerBlock("banana_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BANANA_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("banana_sack", BANANA_SACK);

    /** 葡萄袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GRAPE_SACK =
            BLOCKS.registerBlock("grape_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GRAPE_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("grape_sack", GRAPE_SACK);

    /** 草莓袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> STRAWBERRY_SACK =
            BLOCKS.registerBlock("strawberry_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> STRAWBERRY_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("strawberry_sack", STRAWBERRY_SACK);

    /** 樱桃袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CHERRY_SACK =
            BLOCKS.registerBlock("cherry_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CHERRY_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("cherry_sack", CHERRY_SACK);

    /** 石榴袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> POMEGRANATE_SACK =
            BLOCKS.registerBlock("pomegranate_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> POMEGRANATE_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("pomegranate_sack", POMEGRANATE_SACK);

    /** 猕猴桃袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> KIWI_SACK =
            BLOCKS.registerBlock("kiwi_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> KIWI_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("kiwi_sack", KIWI_SACK);

    /** 芒果袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> MANGO_SACK =
            BLOCKS.registerBlock("mango_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> MANGO_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("mango_sack", MANGO_SACK);

    /** 菠萝箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PINEAPPLE_CRATE =
            BLOCKS.registerBlock("pineapple_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PINEAPPLE_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("pineapple_crate", PINEAPPLE_CRATE);

    /** 小白菜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BOK_CHOY_CRATE =
            BLOCKS.registerBlock("bok_choy_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BOK_CHOY_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("bok_choy_crate", BOK_CHOY_CRATE);

    /** 菠菜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SPINACH_CRATE =
            BLOCKS.registerBlock("spinach_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SPINACH_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("spinach_crate", SPINACH_CRATE);

    /** 芹菜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CELERY_CRATE =
            BLOCKS.registerBlock("celery_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CELERY_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("celery_crate", CELERY_CRATE);

    /** 韭菜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CHIVE_CRATE =
            BLOCKS.registerBlock("chive_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CHIVE_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("chive_crate", CHIVE_CRATE);

    /** 香菜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CILANTRO_CRATE =
            BLOCKS.registerBlock("cilantro_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CILANTRO_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("cilantro_crate", CILANTRO_CRATE);

    /** 葱箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SCALLION_CRATE =
            BLOCKS.registerBlock("scallion_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SCALLION_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("scallion_crate", SCALLION_CRATE);

    /** 蒜苗箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GARLIC_SPROUT_CRATE =
            BLOCKS.registerBlock("garlic_sprout_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GARLIC_SPROUT_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("garlic_sprout_crate", GARLIC_SPROUT_CRATE);

    /** 笋干箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DRIED_BAMBOO_SHOOT_CRATE =
            BLOCKS.registerBlock("dried_bamboo_shoot_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DRIED_BAMBOO_SHOOT_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("dried_bamboo_shoot_crate", DRIED_BAMBOO_SHOOT_CRATE);

    /** 冬瓜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> WINTER_MELON_CRATE =
            BLOCKS.registerBlock("winter_melon_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> WINTER_MELON_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("winter_melon_crate", WINTER_MELON_CRATE);

    /** 丝瓜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> LUFFA_CRATE =
            BLOCKS.registerBlock("luffa_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> LUFFA_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("luffa_crate", LUFFA_CRATE);

    /** 苦瓜箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BITTER_MELON_CRATE =
            BLOCKS.registerBlock("bitter_melon_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BITTER_MELON_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("bitter_melon_crate", BITTER_MELON_CRATE);

    /** 豆角箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GREEN_BEAN_CRATE =
            BLOCKS.registerBlock("green_bean_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GREEN_BEAN_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("green_bean_crate", GREEN_BEAN_CRATE);

    /** 稻谷袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PADDY_SACK =
            BLOCKS.registerBlock("paddy_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PADDY_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("paddy_sack", PADDY_SACK);

    /** 高粱袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SORGHUM_SACK =
            BLOCKS.registerBlock("sorghum_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SORGHUM_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("sorghum_sack", SORGHUM_SACK);

    /** 谷子袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> MILLET_GRASS_SACK =
            BLOCKS.registerBlock("millet_grass_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> MILLET_GRASS_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("millet_grass_sack", MILLET_GRASS_SACK);

    /** 糯米粉袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GLUTINOUS_RICE_FLOUR_SACK =
            BLOCKS.registerBlock("glutinous_rice_flour_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GLUTINOUS_RICE_FLOUR_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("glutinous_rice_flour_sack", GLUTINOUS_RICE_FLOUR_SACK);

    /** 蚕豆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BROAD_BEAN_SACK =
            BLOCKS.registerBlock("broad_bean_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BROAD_BEAN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("broad_bean_sack", BROAD_BEAN_SACK);

    /** 莲子袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> LOTUS_SEED_SACK =
            BLOCKS.registerBlock("lotus_seed_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> LOTUS_SEED_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("lotus_seed_sack", LOTUS_SEED_SACK);

    /** 枸杞袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> GOJI_BERRY_SACK =
            BLOCKS.registerBlock("goji_berry_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> GOJI_BERRY_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("goji_berry_sack", GOJI_BERRY_SACK);

    /** 桂圆袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> LONGAN_SACK =
            BLOCKS.registerBlock("longan_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> LONGAN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("longan_sack", LONGAN_SACK);

    /** 荔枝袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> LYCHEE_SACK =
            BLOCKS.registerBlock("lychee_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> LYCHEE_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("lychee_sack", LYCHEE_SACK);

    /** 桂花袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> OSMANTHUS_SACK =
            BLOCKS.registerBlock("osmanthus_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> OSMANTHUS_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("osmanthus_sack", OSMANTHUS_SACK);

    /** 玉米箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CORN_CRATE =
            BLOCKS.registerBlock("corn_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CORN_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("corn_crate", CORN_CRATE);

    /** 山药箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CHINESE_YAM_CRATE =
            BLOCKS.registerBlock("chinese_yam_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CHINESE_YAM_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("chinese_yam_crate", CHINESE_YAM_CRATE);

    /** 干枣箱（crate，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DRIED_JUJUBE_CRATE =
            BLOCKS.registerBlock("dried_jujube_crate", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DRIED_JUJUBE_CRATE_ITEM =
            ITEMS.registerSimpleBlockItem("dried_jujube_crate", DRIED_JUJUBE_CRATE);

    /** 盐袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SALT_SACK =
            BLOCKS.registerBlock("salt_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SALT_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("salt_sack", SALT_SACK);

    /** 冰糖袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> ROCK_SUGAR_SACK =
            BLOCKS.registerBlock("rock_sugar_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> ROCK_SUGAR_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("rock_sugar_sack", ROCK_SUGAR_SACK);

    /** 孜然袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CUMIN_SACK =
            BLOCKS.registerBlock("cumin_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CUMIN_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("cumin_sack", CUMIN_SACK);

    /** 辣椒粉袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CHILI_POWDER_SACK =
            BLOCKS.registerBlock("chili_powder_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CHILI_POWDER_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("chili_powder_sack", CHILI_POWDER_SACK);

    /** 胡椒粉袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> PEPPER_POWDER_SACK =
            BLOCKS.registerBlock("pepper_powder_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> PEPPER_POWDER_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("pepper_powder_sack", PEPPER_POWDER_SACK);

    /** 五香粉袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> FIVE_SPICE_POWDER_SACK =
            BLOCKS.registerBlock("five_spice_powder_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> FIVE_SPICE_POWDER_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("five_spice_powder_sack", FIVE_SPICE_POWDER_SACK);

    /** 八角袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> STAR_ANISE_SACK =
            BLOCKS.registerBlock("star_anise_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> STAR_ANISE_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("star_anise_sack", STAR_ANISE_SACK);

    /** 桂皮袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CINNAMON_BARK_SACK =
            BLOCKS.registerBlock("cinnamon_bark_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CINNAMON_BARK_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("cinnamon_bark_sack", CINNAMON_BARK_SACK);

    /** 干辣椒袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> DRIED_CHILI_SACK =
            BLOCKS.registerBlock("dried_chili_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> DRIED_CHILI_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("dried_chili_sack", DRIED_CHILI_SACK);

    /** 香叶袋（sack，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> BAY_LEAF_SACK =
            BLOCKS.registerBlock("bay_leaf_sack", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> BAY_LEAF_SACK_ITEM =
            ITEMS.registerSimpleBlockItem("bay_leaf_sack", BAY_LEAF_SACK);

    /** 酱油桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SOY_SAUCE_BARREL =
            BLOCKS.registerBlock("soy_sauce_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SOY_SAUCE_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("soy_sauce_barrel", SOY_SAUCE_BARREL);

    /** 醋桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> VINEGAR_BARREL =
            BLOCKS.registerBlock("vinegar_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> VINEGAR_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("vinegar_barrel", VINEGAR_BARREL);

    /** 料酒桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> COOKING_WINE_BARREL =
            BLOCKS.registerBlock("cooking_wine_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> COOKING_WINE_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("cooking_wine_barrel", COOKING_WINE_BARREL);

    /** 甜面酱桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SWEET_BEAN_SAUCE_BARREL =
            BLOCKS.registerBlock("sweet_bean_sauce_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SWEET_BEAN_SAUCE_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("sweet_bean_sauce_barrel", SWEET_BEAN_SAUCE_BARREL);

    /** 蚝油桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> OYSTER_SAUCE_BARREL =
            BLOCKS.registerBlock("oyster_sauce_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> OYSTER_SAUCE_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("oyster_sauce_barrel", OYSTER_SAUCE_BARREL);

    /** 香油桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SESAME_OIL_BARREL =
            BLOCKS.registerBlock("sesame_oil_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SESAME_OIL_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("sesame_oil_barrel", SESAME_OIL_BARREL);

    /** 芝麻酱桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> SESAME_PASTE_BARREL =
            BLOCKS.registerBlock("sesame_paste_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> SESAME_PASTE_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("sesame_paste_barrel", SESAME_PASTE_BARREL);

    /** 腐乳桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> FERMENTED_TOFU_BARREL =
            BLOCKS.registerBlock("fermented_tofu_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> FERMENTED_TOFU_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("fermented_tofu_barrel", FERMENTED_TOFU_BARREL);

    /** 辣椒油桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> CHILI_OIL_BARREL =
            BLOCKS.registerBlock("chili_oil_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> CHILI_OIL_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("chili_oil_barrel", CHILI_OIL_BARREL);

    /** 高汤桶（barrel，满格方块）。 */
    public static final DeferredBlock<CompressedBlock> STOCK_BARREL =
            BLOCKS.registerBlock("stock_barrel", CompressedBlock::new,
                    props -> props.strength(1.2F).sound(SoundType.WOOD));
    public static final DeferredItem<BlockItem> STOCK_BARREL_ITEM =
            ITEMS.registerSimpleBlockItem("stock_barrel", STOCK_BARREL);

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
            DOUBANJIANG_BARREL_ITEM,
            PICKLED_BARREL_ITEM,
            DOUCHI_BARREL_ITEM,
            SICHUAN_PEPPERCORN_BARREL_ITEM,
            BEAN_PASTE_BRICK_ITEM,
            TOFU_BRICK_ITEM,
            RICE_BRAN_BRICK_ITEM,
            PEAR_SACK_ITEM,
            PEACH_SACK_ITEM,
            PLUM_SACK_ITEM,
            APRICOT_SACK_ITEM,
            JUJUBE_SACK_ITEM,
            PERSIMMON_SACK_ITEM,
            MANDARIN_SACK_ITEM,
            POMELO_SACK_ITEM,
            BANANA_SACK_ITEM,
            GRAPE_SACK_ITEM,
            STRAWBERRY_SACK_ITEM,
            CHERRY_SACK_ITEM,
            POMEGRANATE_SACK_ITEM,
            KIWI_SACK_ITEM,
            MANGO_SACK_ITEM,
            PINEAPPLE_CRATE_ITEM,
            BOK_CHOY_CRATE_ITEM,
            SPINACH_CRATE_ITEM,
            CELERY_CRATE_ITEM,
            CHIVE_CRATE_ITEM,
            CILANTRO_CRATE_ITEM,
            SCALLION_CRATE_ITEM,
            GARLIC_SPROUT_CRATE_ITEM,
            DRIED_BAMBOO_SHOOT_CRATE_ITEM,
            WINTER_MELON_CRATE_ITEM,
            LUFFA_CRATE_ITEM,
            BITTER_MELON_CRATE_ITEM,
            GREEN_BEAN_CRATE_ITEM,
            PADDY_SACK_ITEM,
            SORGHUM_SACK_ITEM,
            MILLET_GRASS_SACK_ITEM,
            GLUTINOUS_RICE_FLOUR_SACK_ITEM,
            BROAD_BEAN_SACK_ITEM,
            LOTUS_SEED_SACK_ITEM,
            GOJI_BERRY_SACK_ITEM,
            LONGAN_SACK_ITEM,
            LYCHEE_SACK_ITEM,
            OSMANTHUS_SACK_ITEM,
            CORN_CRATE_ITEM,
            CHINESE_YAM_CRATE_ITEM,
            DRIED_JUJUBE_CRATE_ITEM,
            SALT_SACK_ITEM,
            ROCK_SUGAR_SACK_ITEM,
            CUMIN_SACK_ITEM,
            CHILI_POWDER_SACK_ITEM,
            PEPPER_POWDER_SACK_ITEM,
            FIVE_SPICE_POWDER_SACK_ITEM,
            STAR_ANISE_SACK_ITEM,
            CINNAMON_BARK_SACK_ITEM,
            DRIED_CHILI_SACK_ITEM,
            BAY_LEAF_SACK_ITEM,
            SOY_SAUCE_BARREL_ITEM,
            VINEGAR_BARREL_ITEM,
            COOKING_WINE_BARREL_ITEM,
            SWEET_BEAN_SAUCE_BARREL_ITEM,
            OYSTER_SAUCE_BARREL_ITEM,
            SESAME_OIL_BARREL_ITEM,
            SESAME_PASTE_BARREL_ITEM,
            FERMENTED_TOFU_BARREL_ITEM,
            CHILI_OIL_BARREL_ITEM,
            STOCK_BARREL_ITEM
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
