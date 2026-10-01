package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.FruitLeavesBlock;
import com.ctf.chinese_traditional_food.common.block.FruitSaplingBlock;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 果树：树苗 + 树叶。
 *
 * <p><b>本文件由 {@code tools/gen_trees.py} 生成，请不要手改。</b>
 * 要加果树请编辑 {@code tools/content_data.py} 的 {@code TREE_FRUITS} 表。</p>
 *
 * <h2>两种方块各管一件事</h2>
 * <ol>
 *   <li><b>树苗</b> {@link FruitSaplingBlock} —— 种下去，过一阵长成树；</li>
 *   <li><b>树叶</b> {@link FruitLeavesBlock} —— 掉落表挂在它身上，
 *       10% 掉自己的树苗、10% 掉自己的果子。</li>
 * </ol>
 *
 * <p>树干不在这里 —— 13 种树各有自己的原木/木板/楼梯/…，
 * 由 {@link ModWoods} 生成。早先这里有一个共用的 {@code fruit_log}，
 * 现在已废掉。</p>
 */
public final class ModTrees {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    private static BlockBehaviour.Properties leafProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.PLANT)
                .strength(0.2F)
                .randomTicks()
                .sound(SoundType.GRASS)
                .noOcclusion()
                .isValidSpawn((state, level, pos, type) -> false)
                .isSuffocating((state, level, pos) -> false)
                .isViewBlocking((state, level, pos) -> false)
                .ignitedByLava()
                .pushReaction(PushReaction.DESTROY);
    }

    private static BlockBehaviour.Properties saplingProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.PLANT)
                .noCollision()
                .randomTicks()
                .instabreak()
                .sound(SoundType.GRASS)
                .pushReaction(PushReaction.DESTROY);
    }

    // ==================================================================
    // 树叶（掉落表挂在它们身上）
    // ==================================================================

    /** plum树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> PLUM_LEAVES =
            BLOCKS.registerBlock("plum_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> PLUM_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("plum_leaves", PLUM_LEAVES);

    /** apricot树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> APRICOT_LEAVES =
            BLOCKS.registerBlock("apricot_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> APRICOT_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("apricot_leaves", APRICOT_LEAVES);

    /** jujube树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> JUJUBE_LEAVES =
            BLOCKS.registerBlock("jujube_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> JUJUBE_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("jujube_leaves", JUJUBE_LEAVES);

    /** mandarin树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> MANDARIN_LEAVES =
            BLOCKS.registerBlock("mandarin_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> MANDARIN_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("mandarin_leaves", MANDARIN_LEAVES);

    /** pear树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> PEAR_LEAVES =
            BLOCKS.registerBlock("pear_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> PEAR_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("pear_leaves", PEAR_LEAVES);

    /** peach树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> PEACH_LEAVES =
            BLOCKS.registerBlock("peach_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> PEACH_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("peach_leaves", PEACH_LEAVES);

    /** cherry树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> CHERRY_LEAVES =
            BLOCKS.registerBlock("cherry_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> CHERRY_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("cherry_leaves", CHERRY_LEAVES);

    /** pomegranate树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> POMEGRANATE_LEAVES =
            BLOCKS.registerBlock("pomegranate_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> POMEGRANATE_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("pomegranate_leaves", POMEGRANATE_LEAVES);

    /** longan树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> LONGAN_LEAVES =
            BLOCKS.registerBlock("longan_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> LONGAN_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("longan_leaves", LONGAN_LEAVES);

    /** lychee树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> LYCHEE_LEAVES =
            BLOCKS.registerBlock("lychee_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> LYCHEE_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("lychee_leaves", LYCHEE_LEAVES);

    /** persimmon树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> PERSIMMON_LEAVES =
            BLOCKS.registerBlock("persimmon_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> PERSIMMON_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("persimmon_leaves", PERSIMMON_LEAVES);

    /** pomelo树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> POMELO_LEAVES =
            BLOCKS.registerBlock("pomelo_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> POMELO_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("pomelo_leaves", POMELO_LEAVES);

    /** mango树叶：10% 掉树苗、10% 掉果子。 */
    public static final DeferredBlock<FruitLeavesBlock> MANGO_LEAVES =
            BLOCKS.registerBlock("mango_leaves", FruitLeavesBlock::new, ModTrees::leafProps);
    public static final DeferredItem<BlockItem> MANGO_LEAVES_ITEM =
            ITEMS.registerSimpleBlockItem("mango_leaves", MANGO_LEAVES);


    // ==================================================================
    // 树苗（引用上面那一片树叶，长大时用它的方块）
    // ==================================================================

    /** plum树苗（树形 0）。 */
    public static final DeferredBlock<FruitSaplingBlock> PLUM_SAPLING =
            BLOCKS.registerBlock("plum_sapling",
                    props -> new FruitSaplingBlock(0, "plum", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> PLUM_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("plum_sapling", PLUM_SAPLING);

    /** apricot树苗（树形 0）。 */
    public static final DeferredBlock<FruitSaplingBlock> APRICOT_SAPLING =
            BLOCKS.registerBlock("apricot_sapling",
                    props -> new FruitSaplingBlock(0, "apricot", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> APRICOT_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("apricot_sapling", APRICOT_SAPLING);

    /** jujube树苗（树形 0）。 */
    public static final DeferredBlock<FruitSaplingBlock> JUJUBE_SAPLING =
            BLOCKS.registerBlock("jujube_sapling",
                    props -> new FruitSaplingBlock(0, "jujube", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> JUJUBE_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("jujube_sapling", JUJUBE_SAPLING);

    /** mandarin树苗（树形 0）。 */
    public static final DeferredBlock<FruitSaplingBlock> MANDARIN_SAPLING =
            BLOCKS.registerBlock("mandarin_sapling",
                    props -> new FruitSaplingBlock(0, "mandarin", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> MANDARIN_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("mandarin_sapling", MANDARIN_SAPLING);

    /** pear树苗（树形 1）。 */
    public static final DeferredBlock<FruitSaplingBlock> PEAR_SAPLING =
            BLOCKS.registerBlock("pear_sapling",
                    props -> new FruitSaplingBlock(1, "pear", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> PEAR_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("pear_sapling", PEAR_SAPLING);

    /** peach树苗（树形 1）。 */
    public static final DeferredBlock<FruitSaplingBlock> PEACH_SAPLING =
            BLOCKS.registerBlock("peach_sapling",
                    props -> new FruitSaplingBlock(1, "peach", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> PEACH_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("peach_sapling", PEACH_SAPLING);

    /** cherry树苗（树形 1）。 */
    public static final DeferredBlock<FruitSaplingBlock> CHERRY_SAPLING =
            BLOCKS.registerBlock("cherry_sapling",
                    props -> new FruitSaplingBlock(1, "cherry", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> CHERRY_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("cherry_sapling", CHERRY_SAPLING);

    /** pomegranate树苗（树形 1）。 */
    public static final DeferredBlock<FruitSaplingBlock> POMEGRANATE_SAPLING =
            BLOCKS.registerBlock("pomegranate_sapling",
                    props -> new FruitSaplingBlock(1, "pomegranate", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> POMEGRANATE_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("pomegranate_sapling", POMEGRANATE_SAPLING);

    /** longan树苗（树形 1）。 */
    public static final DeferredBlock<FruitSaplingBlock> LONGAN_SAPLING =
            BLOCKS.registerBlock("longan_sapling",
                    props -> new FruitSaplingBlock(1, "longan", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> LONGAN_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("longan_sapling", LONGAN_SAPLING);

    /** lychee树苗（树形 1）。 */
    public static final DeferredBlock<FruitSaplingBlock> LYCHEE_SAPLING =
            BLOCKS.registerBlock("lychee_sapling",
                    props -> new FruitSaplingBlock(1, "lychee", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> LYCHEE_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("lychee_sapling", LYCHEE_SAPLING);

    /** persimmon树苗（树形 2）。 */
    public static final DeferredBlock<FruitSaplingBlock> PERSIMMON_SAPLING =
            BLOCKS.registerBlock("persimmon_sapling",
                    props -> new FruitSaplingBlock(2, "persimmon", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> PERSIMMON_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("persimmon_sapling", PERSIMMON_SAPLING);

    /** pomelo树苗（树形 2）。 */
    public static final DeferredBlock<FruitSaplingBlock> POMELO_SAPLING =
            BLOCKS.registerBlock("pomelo_sapling",
                    props -> new FruitSaplingBlock(2, "pomelo", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> POMELO_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("pomelo_sapling", POMELO_SAPLING);

    /** mango树苗（树形 2）。 */
    public static final DeferredBlock<FruitSaplingBlock> MANGO_SAPLING =
            BLOCKS.registerBlock("mango_sapling",
                    props -> new FruitSaplingBlock(2, "mango", props),
                    ModTrees::saplingProps);
    public static final DeferredItem<BlockItem> MANGO_SAPLING_ITEM =
            ITEMS.registerSimpleBlockItem("mango_sapling", MANGO_SAPLING);


    /** 全部树苗物品（创造标签页用）。 */
    public static List<DeferredItem<? extends Item>> allSaplings() {
        return SAPLINGS;
    }

    private static final List<DeferredItem<? extends Item>> SAPLINGS = List.of(
            PLUM_SAPLING_ITEM,
            APRICOT_SAPLING_ITEM,
            JUJUBE_SAPLING_ITEM,
            MANDARIN_SAPLING_ITEM,
            PEAR_SAPLING_ITEM,
            PEACH_SAPLING_ITEM,
            CHERRY_SAPLING_ITEM,
            POMEGRANATE_SAPLING_ITEM,
            LONGAN_SAPLING_ITEM,
            LYCHEE_SAPLING_ITEM,
            PERSIMMON_SAPLING_ITEM,
            POMELO_SAPLING_ITEM,
            MANGO_SAPLING_ITEM
    );

    /** 全部树叶物品（创造标签页用）。 */
    public static List<DeferredItem<? extends Item>> allLeaves() {
        return LEAVES;
    }

    private static final List<DeferredItem<? extends Item>> LEAVES = List.of(
            PLUM_LEAVES_ITEM,
            APRICOT_LEAVES_ITEM,
            JUJUBE_LEAVES_ITEM,
            MANDARIN_LEAVES_ITEM,
            PEAR_LEAVES_ITEM,
            PEACH_LEAVES_ITEM,
            CHERRY_LEAVES_ITEM,
            POMEGRANATE_LEAVES_ITEM,
            LONGAN_LEAVES_ITEM,
            LYCHEE_LEAVES_ITEM,
            PERSIMMON_LEAVES_ITEM,
            POMELO_LEAVES_ITEM,
            MANGO_LEAVES_ITEM
    );

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }

    private ModTrees() {}
}
