package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.WoodType;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 13 种果木的木质方块：原木 / 木头 / 去皮原木 / 去皮木 / 木板 /
 * 楼梯 / 台阶 / 栅栏 / 栅栏门。
 *
 * <p><b>本文件由 {@code tools/gen_woods.py} 生成，请不要手改。</b>
 * 要调颜色请改 {@code tools/content_data.py} 的 {@code TREE_WOOD_LOOK}。</p>
 *
 * <h2>为什么是 13 套而不是 1 套</h2>
 * 早先 13 种果树共用一个 {@code fruit_log} —— 砍桃树和砍枣树掉同一种
 * 木头，玩家搭出来的屋子永远一个颜色。用户要求每种木头都有自己的
 * 去皮 / 木板 / 楼梯 / 台阶 / 栅栏，于是这里生成 13 套。
 *
 * <h2>斧头去皮</h2>
 * 和原版一样：走 NeoForge 的 {@code strippables} <strong>数据图</strong>，
 * 文件在 {@code data/chinese_traditional_food/data_maps/block/strippables.json}。
 * <strong>不要用反射去改 {@code AxeItem.STRIPPABLES}</strong> —— 那是 21.x 的
 * 老办法，26.1 已经把它标成 deprecated，官方给的就是数据图。
 */
public final class ModWoods {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    /** 木头系列的通用属性：木头的音效、可燃、斧头挖得动。 */
    private static BlockBehaviour.Properties woodProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD)
                .strength(2.0F)
                .sound(SoundType.WOOD)
                .ignitedByLava();
    }

    /** 木板 / 楼梯 / 台阶 / 栅栏 / 栅栏门：比原木软一点。 */
    private static BlockBehaviour.Properties plankProps() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD)
                .strength(2.0F, 3.0F)
                .sound(SoundType.WOOD)
                .ignitedByLava();
    }

    // ==================================================================
    // 13 种果木的方块
    // ==================================================================

    // ---------------- plum ----------------
    public static final DeferredBlock<RotatedPillarBlock> PLUM_LOG = BLOCKS.registerBlock(
            "plum_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PLUM_WOOD = BLOCKS.registerBlock(
            "plum_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PLUM_STRIPPED_LOG = BLOCKS.registerBlock(
            "plum_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PLUM_STRIPPED_WOOD = BLOCKS.registerBlock(
            "plum_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> PLUM_PLANKS = BLOCKS.registerBlock(
            "plum_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> PLUM_STAIRS = BLOCKS.registerBlock(
            "plum_stairs",
            p -> new StairBlock(PLUM_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> PLUM_SLAB = BLOCKS.registerBlock(
            "plum_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> PLUM_FENCE = BLOCKS.registerBlock(
            "plum_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> PLUM_FENCE_GATE = BLOCKS.registerBlock(
            "plum_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- apricot ----------------
    public static final DeferredBlock<RotatedPillarBlock> APRICOT_LOG = BLOCKS.registerBlock(
            "apricot_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> APRICOT_WOOD = BLOCKS.registerBlock(
            "apricot_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> APRICOT_STRIPPED_LOG = BLOCKS.registerBlock(
            "apricot_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> APRICOT_STRIPPED_WOOD = BLOCKS.registerBlock(
            "apricot_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> APRICOT_PLANKS = BLOCKS.registerBlock(
            "apricot_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> APRICOT_STAIRS = BLOCKS.registerBlock(
            "apricot_stairs",
            p -> new StairBlock(APRICOT_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> APRICOT_SLAB = BLOCKS.registerBlock(
            "apricot_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> APRICOT_FENCE = BLOCKS.registerBlock(
            "apricot_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> APRICOT_FENCE_GATE = BLOCKS.registerBlock(
            "apricot_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- jujube ----------------
    public static final DeferredBlock<RotatedPillarBlock> JUJUBE_LOG = BLOCKS.registerBlock(
            "jujube_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> JUJUBE_WOOD = BLOCKS.registerBlock(
            "jujube_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> JUJUBE_STRIPPED_LOG = BLOCKS.registerBlock(
            "jujube_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> JUJUBE_STRIPPED_WOOD = BLOCKS.registerBlock(
            "jujube_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> JUJUBE_PLANKS = BLOCKS.registerBlock(
            "jujube_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> JUJUBE_STAIRS = BLOCKS.registerBlock(
            "jujube_stairs",
            p -> new StairBlock(JUJUBE_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> JUJUBE_SLAB = BLOCKS.registerBlock(
            "jujube_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> JUJUBE_FENCE = BLOCKS.registerBlock(
            "jujube_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> JUJUBE_FENCE_GATE = BLOCKS.registerBlock(
            "jujube_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- mandarin ----------------
    public static final DeferredBlock<RotatedPillarBlock> MANDARIN_LOG = BLOCKS.registerBlock(
            "mandarin_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> MANDARIN_WOOD = BLOCKS.registerBlock(
            "mandarin_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> MANDARIN_STRIPPED_LOG = BLOCKS.registerBlock(
            "mandarin_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> MANDARIN_STRIPPED_WOOD = BLOCKS.registerBlock(
            "mandarin_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> MANDARIN_PLANKS = BLOCKS.registerBlock(
            "mandarin_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> MANDARIN_STAIRS = BLOCKS.registerBlock(
            "mandarin_stairs",
            p -> new StairBlock(MANDARIN_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> MANDARIN_SLAB = BLOCKS.registerBlock(
            "mandarin_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> MANDARIN_FENCE = BLOCKS.registerBlock(
            "mandarin_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> MANDARIN_FENCE_GATE = BLOCKS.registerBlock(
            "mandarin_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- pear ----------------
    public static final DeferredBlock<RotatedPillarBlock> PEAR_LOG = BLOCKS.registerBlock(
            "pear_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PEAR_WOOD = BLOCKS.registerBlock(
            "pear_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PEAR_STRIPPED_LOG = BLOCKS.registerBlock(
            "pear_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PEAR_STRIPPED_WOOD = BLOCKS.registerBlock(
            "pear_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> PEAR_PLANKS = BLOCKS.registerBlock(
            "pear_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> PEAR_STAIRS = BLOCKS.registerBlock(
            "pear_stairs",
            p -> new StairBlock(PEAR_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> PEAR_SLAB = BLOCKS.registerBlock(
            "pear_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> PEAR_FENCE = BLOCKS.registerBlock(
            "pear_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> PEAR_FENCE_GATE = BLOCKS.registerBlock(
            "pear_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- peach ----------------
    public static final DeferredBlock<RotatedPillarBlock> PEACH_LOG = BLOCKS.registerBlock(
            "peach_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PEACH_WOOD = BLOCKS.registerBlock(
            "peach_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PEACH_STRIPPED_LOG = BLOCKS.registerBlock(
            "peach_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PEACH_STRIPPED_WOOD = BLOCKS.registerBlock(
            "peach_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> PEACH_PLANKS = BLOCKS.registerBlock(
            "peach_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> PEACH_STAIRS = BLOCKS.registerBlock(
            "peach_stairs",
            p -> new StairBlock(PEACH_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> PEACH_SLAB = BLOCKS.registerBlock(
            "peach_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> PEACH_FENCE = BLOCKS.registerBlock(
            "peach_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> PEACH_FENCE_GATE = BLOCKS.registerBlock(
            "peach_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- cherry ----------------
    public static final DeferredBlock<RotatedPillarBlock> CHERRY_LOG = BLOCKS.registerBlock(
            "cherry_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> CHERRY_WOOD = BLOCKS.registerBlock(
            "cherry_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> CHERRY_STRIPPED_LOG = BLOCKS.registerBlock(
            "cherry_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> CHERRY_STRIPPED_WOOD = BLOCKS.registerBlock(
            "cherry_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> CHERRY_PLANKS = BLOCKS.registerBlock(
            "cherry_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> CHERRY_STAIRS = BLOCKS.registerBlock(
            "cherry_stairs",
            p -> new StairBlock(CHERRY_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> CHERRY_SLAB = BLOCKS.registerBlock(
            "cherry_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> CHERRY_FENCE = BLOCKS.registerBlock(
            "cherry_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> CHERRY_FENCE_GATE = BLOCKS.registerBlock(
            "cherry_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- pomegranate ----------------
    public static final DeferredBlock<RotatedPillarBlock> POMEGRANATE_LOG = BLOCKS.registerBlock(
            "pomegranate_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> POMEGRANATE_WOOD = BLOCKS.registerBlock(
            "pomegranate_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> POMEGRANATE_STRIPPED_LOG = BLOCKS.registerBlock(
            "pomegranate_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> POMEGRANATE_STRIPPED_WOOD = BLOCKS.registerBlock(
            "pomegranate_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> POMEGRANATE_PLANKS = BLOCKS.registerBlock(
            "pomegranate_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> POMEGRANATE_STAIRS = BLOCKS.registerBlock(
            "pomegranate_stairs",
            p -> new StairBlock(POMEGRANATE_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> POMEGRANATE_SLAB = BLOCKS.registerBlock(
            "pomegranate_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> POMEGRANATE_FENCE = BLOCKS.registerBlock(
            "pomegranate_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> POMEGRANATE_FENCE_GATE = BLOCKS.registerBlock(
            "pomegranate_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- longan ----------------
    public static final DeferredBlock<RotatedPillarBlock> LONGAN_LOG = BLOCKS.registerBlock(
            "longan_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> LONGAN_WOOD = BLOCKS.registerBlock(
            "longan_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> LONGAN_STRIPPED_LOG = BLOCKS.registerBlock(
            "longan_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> LONGAN_STRIPPED_WOOD = BLOCKS.registerBlock(
            "longan_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> LONGAN_PLANKS = BLOCKS.registerBlock(
            "longan_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> LONGAN_STAIRS = BLOCKS.registerBlock(
            "longan_stairs",
            p -> new StairBlock(LONGAN_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> LONGAN_SLAB = BLOCKS.registerBlock(
            "longan_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> LONGAN_FENCE = BLOCKS.registerBlock(
            "longan_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> LONGAN_FENCE_GATE = BLOCKS.registerBlock(
            "longan_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- lychee ----------------
    public static final DeferredBlock<RotatedPillarBlock> LYCHEE_LOG = BLOCKS.registerBlock(
            "lychee_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> LYCHEE_WOOD = BLOCKS.registerBlock(
            "lychee_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> LYCHEE_STRIPPED_LOG = BLOCKS.registerBlock(
            "lychee_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> LYCHEE_STRIPPED_WOOD = BLOCKS.registerBlock(
            "lychee_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> LYCHEE_PLANKS = BLOCKS.registerBlock(
            "lychee_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> LYCHEE_STAIRS = BLOCKS.registerBlock(
            "lychee_stairs",
            p -> new StairBlock(LYCHEE_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> LYCHEE_SLAB = BLOCKS.registerBlock(
            "lychee_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> LYCHEE_FENCE = BLOCKS.registerBlock(
            "lychee_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> LYCHEE_FENCE_GATE = BLOCKS.registerBlock(
            "lychee_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- persimmon ----------------
    public static final DeferredBlock<RotatedPillarBlock> PERSIMMON_LOG = BLOCKS.registerBlock(
            "persimmon_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PERSIMMON_WOOD = BLOCKS.registerBlock(
            "persimmon_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PERSIMMON_STRIPPED_LOG = BLOCKS.registerBlock(
            "persimmon_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> PERSIMMON_STRIPPED_WOOD = BLOCKS.registerBlock(
            "persimmon_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> PERSIMMON_PLANKS = BLOCKS.registerBlock(
            "persimmon_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> PERSIMMON_STAIRS = BLOCKS.registerBlock(
            "persimmon_stairs",
            p -> new StairBlock(PERSIMMON_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> PERSIMMON_SLAB = BLOCKS.registerBlock(
            "persimmon_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> PERSIMMON_FENCE = BLOCKS.registerBlock(
            "persimmon_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> PERSIMMON_FENCE_GATE = BLOCKS.registerBlock(
            "persimmon_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- pomelo ----------------
    public static final DeferredBlock<RotatedPillarBlock> POMELO_LOG = BLOCKS.registerBlock(
            "pomelo_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> POMELO_WOOD = BLOCKS.registerBlock(
            "pomelo_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> POMELO_STRIPPED_LOG = BLOCKS.registerBlock(
            "pomelo_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> POMELO_STRIPPED_WOOD = BLOCKS.registerBlock(
            "pomelo_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> POMELO_PLANKS = BLOCKS.registerBlock(
            "pomelo_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> POMELO_STAIRS = BLOCKS.registerBlock(
            "pomelo_stairs",
            p -> new StairBlock(POMELO_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> POMELO_SLAB = BLOCKS.registerBlock(
            "pomelo_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> POMELO_FENCE = BLOCKS.registerBlock(
            "pomelo_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> POMELO_FENCE_GATE = BLOCKS.registerBlock(
            "pomelo_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ---------------- mango ----------------
    public static final DeferredBlock<RotatedPillarBlock> MANGO_LOG = BLOCKS.registerBlock(
            "mango_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> MANGO_WOOD = BLOCKS.registerBlock(
            "mango_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> MANGO_STRIPPED_LOG = BLOCKS.registerBlock(
            "mango_stripped_log", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<RotatedPillarBlock> MANGO_STRIPPED_WOOD = BLOCKS.registerBlock(
            "mango_stripped_wood", RotatedPillarBlock::new, props -> woodProps());
    public static final DeferredBlock<Block> MANGO_PLANKS = BLOCKS.registerBlock(
            "mango_planks", Block::new, props -> plankProps());
    public static final DeferredBlock<StairBlock> MANGO_STAIRS = BLOCKS.registerBlock(
            "mango_stairs",
            p -> new StairBlock(MANGO_PLANKS.get().defaultBlockState(), p),
            props -> plankProps());
    public static final DeferredBlock<SlabBlock> MANGO_SLAB = BLOCKS.registerBlock(
            "mango_slab", SlabBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceBlock> MANGO_FENCE = BLOCKS.registerBlock(
            "mango_fence", FenceBlock::new, props -> plankProps());
    public static final DeferredBlock<FenceGateBlock> MANGO_FENCE_GATE = BLOCKS.registerBlock(
            "mango_fence_gate",
            p -> new FenceGateBlock(WoodType.OAK, p),
            props -> plankProps());


    // ==================================================================
    // 物品
    // ==================================================================
    public static final DeferredItem<BlockItem> PLUM_LOG_ITEM = ITEMS.registerSimpleBlockItem("plum_log", PLUM_LOG);
    public static final DeferredItem<BlockItem> PLUM_WOOD_ITEM = ITEMS.registerSimpleBlockItem("plum_wood", PLUM_WOOD);
    public static final DeferredItem<BlockItem> PLUM_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("plum_stripped_log", PLUM_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> PLUM_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("plum_stripped_wood", PLUM_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> PLUM_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("plum_planks", PLUM_PLANKS);
    public static final DeferredItem<BlockItem> PLUM_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("plum_stairs", PLUM_STAIRS);
    public static final DeferredItem<BlockItem> PLUM_SLAB_ITEM = ITEMS.registerSimpleBlockItem("plum_slab", PLUM_SLAB);
    public static final DeferredItem<BlockItem> PLUM_FENCE_ITEM = ITEMS.registerSimpleBlockItem("plum_fence", PLUM_FENCE);
    public static final DeferredItem<BlockItem> PLUM_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("plum_fence_gate", PLUM_FENCE_GATE);
    public static final DeferredItem<BlockItem> APRICOT_LOG_ITEM = ITEMS.registerSimpleBlockItem("apricot_log", APRICOT_LOG);
    public static final DeferredItem<BlockItem> APRICOT_WOOD_ITEM = ITEMS.registerSimpleBlockItem("apricot_wood", APRICOT_WOOD);
    public static final DeferredItem<BlockItem> APRICOT_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("apricot_stripped_log", APRICOT_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> APRICOT_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("apricot_stripped_wood", APRICOT_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> APRICOT_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("apricot_planks", APRICOT_PLANKS);
    public static final DeferredItem<BlockItem> APRICOT_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("apricot_stairs", APRICOT_STAIRS);
    public static final DeferredItem<BlockItem> APRICOT_SLAB_ITEM = ITEMS.registerSimpleBlockItem("apricot_slab", APRICOT_SLAB);
    public static final DeferredItem<BlockItem> APRICOT_FENCE_ITEM = ITEMS.registerSimpleBlockItem("apricot_fence", APRICOT_FENCE);
    public static final DeferredItem<BlockItem> APRICOT_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("apricot_fence_gate", APRICOT_FENCE_GATE);
    public static final DeferredItem<BlockItem> JUJUBE_LOG_ITEM = ITEMS.registerSimpleBlockItem("jujube_log", JUJUBE_LOG);
    public static final DeferredItem<BlockItem> JUJUBE_WOOD_ITEM = ITEMS.registerSimpleBlockItem("jujube_wood", JUJUBE_WOOD);
    public static final DeferredItem<BlockItem> JUJUBE_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("jujube_stripped_log", JUJUBE_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> JUJUBE_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("jujube_stripped_wood", JUJUBE_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> JUJUBE_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("jujube_planks", JUJUBE_PLANKS);
    public static final DeferredItem<BlockItem> JUJUBE_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("jujube_stairs", JUJUBE_STAIRS);
    public static final DeferredItem<BlockItem> JUJUBE_SLAB_ITEM = ITEMS.registerSimpleBlockItem("jujube_slab", JUJUBE_SLAB);
    public static final DeferredItem<BlockItem> JUJUBE_FENCE_ITEM = ITEMS.registerSimpleBlockItem("jujube_fence", JUJUBE_FENCE);
    public static final DeferredItem<BlockItem> JUJUBE_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("jujube_fence_gate", JUJUBE_FENCE_GATE);
    public static final DeferredItem<BlockItem> MANDARIN_LOG_ITEM = ITEMS.registerSimpleBlockItem("mandarin_log", MANDARIN_LOG);
    public static final DeferredItem<BlockItem> MANDARIN_WOOD_ITEM = ITEMS.registerSimpleBlockItem("mandarin_wood", MANDARIN_WOOD);
    public static final DeferredItem<BlockItem> MANDARIN_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("mandarin_stripped_log", MANDARIN_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> MANDARIN_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("mandarin_stripped_wood", MANDARIN_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> MANDARIN_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("mandarin_planks", MANDARIN_PLANKS);
    public static final DeferredItem<BlockItem> MANDARIN_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("mandarin_stairs", MANDARIN_STAIRS);
    public static final DeferredItem<BlockItem> MANDARIN_SLAB_ITEM = ITEMS.registerSimpleBlockItem("mandarin_slab", MANDARIN_SLAB);
    public static final DeferredItem<BlockItem> MANDARIN_FENCE_ITEM = ITEMS.registerSimpleBlockItem("mandarin_fence", MANDARIN_FENCE);
    public static final DeferredItem<BlockItem> MANDARIN_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("mandarin_fence_gate", MANDARIN_FENCE_GATE);
    public static final DeferredItem<BlockItem> PEAR_LOG_ITEM = ITEMS.registerSimpleBlockItem("pear_log", PEAR_LOG);
    public static final DeferredItem<BlockItem> PEAR_WOOD_ITEM = ITEMS.registerSimpleBlockItem("pear_wood", PEAR_WOOD);
    public static final DeferredItem<BlockItem> PEAR_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("pear_stripped_log", PEAR_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> PEAR_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("pear_stripped_wood", PEAR_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> PEAR_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("pear_planks", PEAR_PLANKS);
    public static final DeferredItem<BlockItem> PEAR_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("pear_stairs", PEAR_STAIRS);
    public static final DeferredItem<BlockItem> PEAR_SLAB_ITEM = ITEMS.registerSimpleBlockItem("pear_slab", PEAR_SLAB);
    public static final DeferredItem<BlockItem> PEAR_FENCE_ITEM = ITEMS.registerSimpleBlockItem("pear_fence", PEAR_FENCE);
    public static final DeferredItem<BlockItem> PEAR_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("pear_fence_gate", PEAR_FENCE_GATE);
    public static final DeferredItem<BlockItem> PEACH_LOG_ITEM = ITEMS.registerSimpleBlockItem("peach_log", PEACH_LOG);
    public static final DeferredItem<BlockItem> PEACH_WOOD_ITEM = ITEMS.registerSimpleBlockItem("peach_wood", PEACH_WOOD);
    public static final DeferredItem<BlockItem> PEACH_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("peach_stripped_log", PEACH_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> PEACH_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("peach_stripped_wood", PEACH_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> PEACH_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("peach_planks", PEACH_PLANKS);
    public static final DeferredItem<BlockItem> PEACH_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("peach_stairs", PEACH_STAIRS);
    public static final DeferredItem<BlockItem> PEACH_SLAB_ITEM = ITEMS.registerSimpleBlockItem("peach_slab", PEACH_SLAB);
    public static final DeferredItem<BlockItem> PEACH_FENCE_ITEM = ITEMS.registerSimpleBlockItem("peach_fence", PEACH_FENCE);
    public static final DeferredItem<BlockItem> PEACH_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("peach_fence_gate", PEACH_FENCE_GATE);
    public static final DeferredItem<BlockItem> CHERRY_LOG_ITEM = ITEMS.registerSimpleBlockItem("cherry_log", CHERRY_LOG);
    public static final DeferredItem<BlockItem> CHERRY_WOOD_ITEM = ITEMS.registerSimpleBlockItem("cherry_wood", CHERRY_WOOD);
    public static final DeferredItem<BlockItem> CHERRY_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("cherry_stripped_log", CHERRY_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> CHERRY_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("cherry_stripped_wood", CHERRY_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> CHERRY_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("cherry_planks", CHERRY_PLANKS);
    public static final DeferredItem<BlockItem> CHERRY_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("cherry_stairs", CHERRY_STAIRS);
    public static final DeferredItem<BlockItem> CHERRY_SLAB_ITEM = ITEMS.registerSimpleBlockItem("cherry_slab", CHERRY_SLAB);
    public static final DeferredItem<BlockItem> CHERRY_FENCE_ITEM = ITEMS.registerSimpleBlockItem("cherry_fence", CHERRY_FENCE);
    public static final DeferredItem<BlockItem> CHERRY_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("cherry_fence_gate", CHERRY_FENCE_GATE);
    public static final DeferredItem<BlockItem> POMEGRANATE_LOG_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_log", POMEGRANATE_LOG);
    public static final DeferredItem<BlockItem> POMEGRANATE_WOOD_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_wood", POMEGRANATE_WOOD);
    public static final DeferredItem<BlockItem> POMEGRANATE_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_stripped_log", POMEGRANATE_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> POMEGRANATE_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_stripped_wood", POMEGRANATE_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> POMEGRANATE_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_planks", POMEGRANATE_PLANKS);
    public static final DeferredItem<BlockItem> POMEGRANATE_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_stairs", POMEGRANATE_STAIRS);
    public static final DeferredItem<BlockItem> POMEGRANATE_SLAB_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_slab", POMEGRANATE_SLAB);
    public static final DeferredItem<BlockItem> POMEGRANATE_FENCE_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_fence", POMEGRANATE_FENCE);
    public static final DeferredItem<BlockItem> POMEGRANATE_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("pomegranate_fence_gate", POMEGRANATE_FENCE_GATE);
    public static final DeferredItem<BlockItem> LONGAN_LOG_ITEM = ITEMS.registerSimpleBlockItem("longan_log", LONGAN_LOG);
    public static final DeferredItem<BlockItem> LONGAN_WOOD_ITEM = ITEMS.registerSimpleBlockItem("longan_wood", LONGAN_WOOD);
    public static final DeferredItem<BlockItem> LONGAN_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("longan_stripped_log", LONGAN_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> LONGAN_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("longan_stripped_wood", LONGAN_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> LONGAN_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("longan_planks", LONGAN_PLANKS);
    public static final DeferredItem<BlockItem> LONGAN_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("longan_stairs", LONGAN_STAIRS);
    public static final DeferredItem<BlockItem> LONGAN_SLAB_ITEM = ITEMS.registerSimpleBlockItem("longan_slab", LONGAN_SLAB);
    public static final DeferredItem<BlockItem> LONGAN_FENCE_ITEM = ITEMS.registerSimpleBlockItem("longan_fence", LONGAN_FENCE);
    public static final DeferredItem<BlockItem> LONGAN_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("longan_fence_gate", LONGAN_FENCE_GATE);
    public static final DeferredItem<BlockItem> LYCHEE_LOG_ITEM = ITEMS.registerSimpleBlockItem("lychee_log", LYCHEE_LOG);
    public static final DeferredItem<BlockItem> LYCHEE_WOOD_ITEM = ITEMS.registerSimpleBlockItem("lychee_wood", LYCHEE_WOOD);
    public static final DeferredItem<BlockItem> LYCHEE_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("lychee_stripped_log", LYCHEE_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> LYCHEE_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("lychee_stripped_wood", LYCHEE_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> LYCHEE_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("lychee_planks", LYCHEE_PLANKS);
    public static final DeferredItem<BlockItem> LYCHEE_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("lychee_stairs", LYCHEE_STAIRS);
    public static final DeferredItem<BlockItem> LYCHEE_SLAB_ITEM = ITEMS.registerSimpleBlockItem("lychee_slab", LYCHEE_SLAB);
    public static final DeferredItem<BlockItem> LYCHEE_FENCE_ITEM = ITEMS.registerSimpleBlockItem("lychee_fence", LYCHEE_FENCE);
    public static final DeferredItem<BlockItem> LYCHEE_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("lychee_fence_gate", LYCHEE_FENCE_GATE);
    public static final DeferredItem<BlockItem> PERSIMMON_LOG_ITEM = ITEMS.registerSimpleBlockItem("persimmon_log", PERSIMMON_LOG);
    public static final DeferredItem<BlockItem> PERSIMMON_WOOD_ITEM = ITEMS.registerSimpleBlockItem("persimmon_wood", PERSIMMON_WOOD);
    public static final DeferredItem<BlockItem> PERSIMMON_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("persimmon_stripped_log", PERSIMMON_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> PERSIMMON_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("persimmon_stripped_wood", PERSIMMON_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> PERSIMMON_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("persimmon_planks", PERSIMMON_PLANKS);
    public static final DeferredItem<BlockItem> PERSIMMON_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("persimmon_stairs", PERSIMMON_STAIRS);
    public static final DeferredItem<BlockItem> PERSIMMON_SLAB_ITEM = ITEMS.registerSimpleBlockItem("persimmon_slab", PERSIMMON_SLAB);
    public static final DeferredItem<BlockItem> PERSIMMON_FENCE_ITEM = ITEMS.registerSimpleBlockItem("persimmon_fence", PERSIMMON_FENCE);
    public static final DeferredItem<BlockItem> PERSIMMON_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("persimmon_fence_gate", PERSIMMON_FENCE_GATE);
    public static final DeferredItem<BlockItem> POMELO_LOG_ITEM = ITEMS.registerSimpleBlockItem("pomelo_log", POMELO_LOG);
    public static final DeferredItem<BlockItem> POMELO_WOOD_ITEM = ITEMS.registerSimpleBlockItem("pomelo_wood", POMELO_WOOD);
    public static final DeferredItem<BlockItem> POMELO_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("pomelo_stripped_log", POMELO_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> POMELO_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("pomelo_stripped_wood", POMELO_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> POMELO_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("pomelo_planks", POMELO_PLANKS);
    public static final DeferredItem<BlockItem> POMELO_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("pomelo_stairs", POMELO_STAIRS);
    public static final DeferredItem<BlockItem> POMELO_SLAB_ITEM = ITEMS.registerSimpleBlockItem("pomelo_slab", POMELO_SLAB);
    public static final DeferredItem<BlockItem> POMELO_FENCE_ITEM = ITEMS.registerSimpleBlockItem("pomelo_fence", POMELO_FENCE);
    public static final DeferredItem<BlockItem> POMELO_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("pomelo_fence_gate", POMELO_FENCE_GATE);
    public static final DeferredItem<BlockItem> MANGO_LOG_ITEM = ITEMS.registerSimpleBlockItem("mango_log", MANGO_LOG);
    public static final DeferredItem<BlockItem> MANGO_WOOD_ITEM = ITEMS.registerSimpleBlockItem("mango_wood", MANGO_WOOD);
    public static final DeferredItem<BlockItem> MANGO_STRIPPED_LOG_ITEM = ITEMS.registerSimpleBlockItem("mango_stripped_log", MANGO_STRIPPED_LOG);
    public static final DeferredItem<BlockItem> MANGO_STRIPPED_WOOD_ITEM = ITEMS.registerSimpleBlockItem("mango_stripped_wood", MANGO_STRIPPED_WOOD);
    public static final DeferredItem<BlockItem> MANGO_PLANKS_ITEM = ITEMS.registerSimpleBlockItem("mango_planks", MANGO_PLANKS);
    public static final DeferredItem<BlockItem> MANGO_STAIRS_ITEM = ITEMS.registerSimpleBlockItem("mango_stairs", MANGO_STAIRS);
    public static final DeferredItem<BlockItem> MANGO_SLAB_ITEM = ITEMS.registerSimpleBlockItem("mango_slab", MANGO_SLAB);
    public static final DeferredItem<BlockItem> MANGO_FENCE_ITEM = ITEMS.registerSimpleBlockItem("mango_fence", MANGO_FENCE);
    public static final DeferredItem<BlockItem> MANGO_FENCE_GATE_ITEM = ITEMS.registerSimpleBlockItem("mango_fence_gate", MANGO_FENCE_GATE);


    /** 全部 117 个方块，按"每种木一套"的顺序。 */
    public static List<DeferredBlock<?>> allBlocks() {
        List<DeferredBlock<?>> list = new ArrayList<>();
        list.add(PLUM_LOG);
        list.add(PLUM_WOOD);
        list.add(PLUM_STRIPPED_LOG);
        list.add(PLUM_STRIPPED_WOOD);
        list.add(PLUM_PLANKS);
        list.add(PLUM_STAIRS);
        list.add(PLUM_SLAB);
        list.add(PLUM_FENCE);
        list.add(PLUM_FENCE_GATE);
        list.add(APRICOT_LOG);
        list.add(APRICOT_WOOD);
        list.add(APRICOT_STRIPPED_LOG);
        list.add(APRICOT_STRIPPED_WOOD);
        list.add(APRICOT_PLANKS);
        list.add(APRICOT_STAIRS);
        list.add(APRICOT_SLAB);
        list.add(APRICOT_FENCE);
        list.add(APRICOT_FENCE_GATE);
        list.add(JUJUBE_LOG);
        list.add(JUJUBE_WOOD);
        list.add(JUJUBE_STRIPPED_LOG);
        list.add(JUJUBE_STRIPPED_WOOD);
        list.add(JUJUBE_PLANKS);
        list.add(JUJUBE_STAIRS);
        list.add(JUJUBE_SLAB);
        list.add(JUJUBE_FENCE);
        list.add(JUJUBE_FENCE_GATE);
        list.add(MANDARIN_LOG);
        list.add(MANDARIN_WOOD);
        list.add(MANDARIN_STRIPPED_LOG);
        list.add(MANDARIN_STRIPPED_WOOD);
        list.add(MANDARIN_PLANKS);
        list.add(MANDARIN_STAIRS);
        list.add(MANDARIN_SLAB);
        list.add(MANDARIN_FENCE);
        list.add(MANDARIN_FENCE_GATE);
        list.add(PEAR_LOG);
        list.add(PEAR_WOOD);
        list.add(PEAR_STRIPPED_LOG);
        list.add(PEAR_STRIPPED_WOOD);
        list.add(PEAR_PLANKS);
        list.add(PEAR_STAIRS);
        list.add(PEAR_SLAB);
        list.add(PEAR_FENCE);
        list.add(PEAR_FENCE_GATE);
        list.add(PEACH_LOG);
        list.add(PEACH_WOOD);
        list.add(PEACH_STRIPPED_LOG);
        list.add(PEACH_STRIPPED_WOOD);
        list.add(PEACH_PLANKS);
        list.add(PEACH_STAIRS);
        list.add(PEACH_SLAB);
        list.add(PEACH_FENCE);
        list.add(PEACH_FENCE_GATE);
        list.add(CHERRY_LOG);
        list.add(CHERRY_WOOD);
        list.add(CHERRY_STRIPPED_LOG);
        list.add(CHERRY_STRIPPED_WOOD);
        list.add(CHERRY_PLANKS);
        list.add(CHERRY_STAIRS);
        list.add(CHERRY_SLAB);
        list.add(CHERRY_FENCE);
        list.add(CHERRY_FENCE_GATE);
        list.add(POMEGRANATE_LOG);
        list.add(POMEGRANATE_WOOD);
        list.add(POMEGRANATE_STRIPPED_LOG);
        list.add(POMEGRANATE_STRIPPED_WOOD);
        list.add(POMEGRANATE_PLANKS);
        list.add(POMEGRANATE_STAIRS);
        list.add(POMEGRANATE_SLAB);
        list.add(POMEGRANATE_FENCE);
        list.add(POMEGRANATE_FENCE_GATE);
        list.add(LONGAN_LOG);
        list.add(LONGAN_WOOD);
        list.add(LONGAN_STRIPPED_LOG);
        list.add(LONGAN_STRIPPED_WOOD);
        list.add(LONGAN_PLANKS);
        list.add(LONGAN_STAIRS);
        list.add(LONGAN_SLAB);
        list.add(LONGAN_FENCE);
        list.add(LONGAN_FENCE_GATE);
        list.add(LYCHEE_LOG);
        list.add(LYCHEE_WOOD);
        list.add(LYCHEE_STRIPPED_LOG);
        list.add(LYCHEE_STRIPPED_WOOD);
        list.add(LYCHEE_PLANKS);
        list.add(LYCHEE_STAIRS);
        list.add(LYCHEE_SLAB);
        list.add(LYCHEE_FENCE);
        list.add(LYCHEE_FENCE_GATE);
        list.add(PERSIMMON_LOG);
        list.add(PERSIMMON_WOOD);
        list.add(PERSIMMON_STRIPPED_LOG);
        list.add(PERSIMMON_STRIPPED_WOOD);
        list.add(PERSIMMON_PLANKS);
        list.add(PERSIMMON_STAIRS);
        list.add(PERSIMMON_SLAB);
        list.add(PERSIMMON_FENCE);
        list.add(PERSIMMON_FENCE_GATE);
        list.add(POMELO_LOG);
        list.add(POMELO_WOOD);
        list.add(POMELO_STRIPPED_LOG);
        list.add(POMELO_STRIPPED_WOOD);
        list.add(POMELO_PLANKS);
        list.add(POMELO_STAIRS);
        list.add(POMELO_SLAB);
        list.add(POMELO_FENCE);
        list.add(POMELO_FENCE_GATE);
        list.add(MANGO_LOG);
        list.add(MANGO_WOOD);
        list.add(MANGO_STRIPPED_LOG);
        list.add(MANGO_STRIPPED_WOOD);
        list.add(MANGO_PLANKS);
        list.add(MANGO_STAIRS);
        list.add(MANGO_SLAB);
        list.add(MANGO_FENCE);
        list.add(MANGO_FENCE_GATE);
        return list;
    }

    /** 全部 117 个方块物品（创造标签页用）。 */
    public static List<DeferredItem<?>> allItems() {
        List<DeferredItem<?>> list = new ArrayList<>();
        list.add(PLUM_LOG_ITEM);
        list.add(PLUM_WOOD_ITEM);
        list.add(PLUM_STRIPPED_LOG_ITEM);
        list.add(PLUM_STRIPPED_WOOD_ITEM);
        list.add(PLUM_PLANKS_ITEM);
        list.add(PLUM_STAIRS_ITEM);
        list.add(PLUM_SLAB_ITEM);
        list.add(PLUM_FENCE_ITEM);
        list.add(PLUM_FENCE_GATE_ITEM);
        list.add(APRICOT_LOG_ITEM);
        list.add(APRICOT_WOOD_ITEM);
        list.add(APRICOT_STRIPPED_LOG_ITEM);
        list.add(APRICOT_STRIPPED_WOOD_ITEM);
        list.add(APRICOT_PLANKS_ITEM);
        list.add(APRICOT_STAIRS_ITEM);
        list.add(APRICOT_SLAB_ITEM);
        list.add(APRICOT_FENCE_ITEM);
        list.add(APRICOT_FENCE_GATE_ITEM);
        list.add(JUJUBE_LOG_ITEM);
        list.add(JUJUBE_WOOD_ITEM);
        list.add(JUJUBE_STRIPPED_LOG_ITEM);
        list.add(JUJUBE_STRIPPED_WOOD_ITEM);
        list.add(JUJUBE_PLANKS_ITEM);
        list.add(JUJUBE_STAIRS_ITEM);
        list.add(JUJUBE_SLAB_ITEM);
        list.add(JUJUBE_FENCE_ITEM);
        list.add(JUJUBE_FENCE_GATE_ITEM);
        list.add(MANDARIN_LOG_ITEM);
        list.add(MANDARIN_WOOD_ITEM);
        list.add(MANDARIN_STRIPPED_LOG_ITEM);
        list.add(MANDARIN_STRIPPED_WOOD_ITEM);
        list.add(MANDARIN_PLANKS_ITEM);
        list.add(MANDARIN_STAIRS_ITEM);
        list.add(MANDARIN_SLAB_ITEM);
        list.add(MANDARIN_FENCE_ITEM);
        list.add(MANDARIN_FENCE_GATE_ITEM);
        list.add(PEAR_LOG_ITEM);
        list.add(PEAR_WOOD_ITEM);
        list.add(PEAR_STRIPPED_LOG_ITEM);
        list.add(PEAR_STRIPPED_WOOD_ITEM);
        list.add(PEAR_PLANKS_ITEM);
        list.add(PEAR_STAIRS_ITEM);
        list.add(PEAR_SLAB_ITEM);
        list.add(PEAR_FENCE_ITEM);
        list.add(PEAR_FENCE_GATE_ITEM);
        list.add(PEACH_LOG_ITEM);
        list.add(PEACH_WOOD_ITEM);
        list.add(PEACH_STRIPPED_LOG_ITEM);
        list.add(PEACH_STRIPPED_WOOD_ITEM);
        list.add(PEACH_PLANKS_ITEM);
        list.add(PEACH_STAIRS_ITEM);
        list.add(PEACH_SLAB_ITEM);
        list.add(PEACH_FENCE_ITEM);
        list.add(PEACH_FENCE_GATE_ITEM);
        list.add(CHERRY_LOG_ITEM);
        list.add(CHERRY_WOOD_ITEM);
        list.add(CHERRY_STRIPPED_LOG_ITEM);
        list.add(CHERRY_STRIPPED_WOOD_ITEM);
        list.add(CHERRY_PLANKS_ITEM);
        list.add(CHERRY_STAIRS_ITEM);
        list.add(CHERRY_SLAB_ITEM);
        list.add(CHERRY_FENCE_ITEM);
        list.add(CHERRY_FENCE_GATE_ITEM);
        list.add(POMEGRANATE_LOG_ITEM);
        list.add(POMEGRANATE_WOOD_ITEM);
        list.add(POMEGRANATE_STRIPPED_LOG_ITEM);
        list.add(POMEGRANATE_STRIPPED_WOOD_ITEM);
        list.add(POMEGRANATE_PLANKS_ITEM);
        list.add(POMEGRANATE_STAIRS_ITEM);
        list.add(POMEGRANATE_SLAB_ITEM);
        list.add(POMEGRANATE_FENCE_ITEM);
        list.add(POMEGRANATE_FENCE_GATE_ITEM);
        list.add(LONGAN_LOG_ITEM);
        list.add(LONGAN_WOOD_ITEM);
        list.add(LONGAN_STRIPPED_LOG_ITEM);
        list.add(LONGAN_STRIPPED_WOOD_ITEM);
        list.add(LONGAN_PLANKS_ITEM);
        list.add(LONGAN_STAIRS_ITEM);
        list.add(LONGAN_SLAB_ITEM);
        list.add(LONGAN_FENCE_ITEM);
        list.add(LONGAN_FENCE_GATE_ITEM);
        list.add(LYCHEE_LOG_ITEM);
        list.add(LYCHEE_WOOD_ITEM);
        list.add(LYCHEE_STRIPPED_LOG_ITEM);
        list.add(LYCHEE_STRIPPED_WOOD_ITEM);
        list.add(LYCHEE_PLANKS_ITEM);
        list.add(LYCHEE_STAIRS_ITEM);
        list.add(LYCHEE_SLAB_ITEM);
        list.add(LYCHEE_FENCE_ITEM);
        list.add(LYCHEE_FENCE_GATE_ITEM);
        list.add(PERSIMMON_LOG_ITEM);
        list.add(PERSIMMON_WOOD_ITEM);
        list.add(PERSIMMON_STRIPPED_LOG_ITEM);
        list.add(PERSIMMON_STRIPPED_WOOD_ITEM);
        list.add(PERSIMMON_PLANKS_ITEM);
        list.add(PERSIMMON_STAIRS_ITEM);
        list.add(PERSIMMON_SLAB_ITEM);
        list.add(PERSIMMON_FENCE_ITEM);
        list.add(PERSIMMON_FENCE_GATE_ITEM);
        list.add(POMELO_LOG_ITEM);
        list.add(POMELO_WOOD_ITEM);
        list.add(POMELO_STRIPPED_LOG_ITEM);
        list.add(POMELO_STRIPPED_WOOD_ITEM);
        list.add(POMELO_PLANKS_ITEM);
        list.add(POMELO_STAIRS_ITEM);
        list.add(POMELO_SLAB_ITEM);
        list.add(POMELO_FENCE_ITEM);
        list.add(POMELO_FENCE_GATE_ITEM);
        list.add(MANGO_LOG_ITEM);
        list.add(MANGO_WOOD_ITEM);
        list.add(MANGO_STRIPPED_LOG_ITEM);
        list.add(MANGO_STRIPPED_WOOD_ITEM);
        list.add(MANGO_PLANKS_ITEM);
        list.add(MANGO_STAIRS_ITEM);
        list.add(MANGO_SLAB_ITEM);
        list.add(MANGO_FENCE_ITEM);
        list.add(MANGO_FENCE_GATE_ITEM);
        return list;
    }

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }
}
