package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.ModCropBlock;
import com.ctf.chinese_traditional_food.common.block.WildCropBlock;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 作物植株与种子的注册表。
 *
 * <p><b>本文件由 {@code tools/gen_crops.py} 生成，请不要手改。</b>
 * 要加作物请编辑 {@code tools/content_data.py} 的 {@code CROPS} 表。</p>
 *
 * <h2>每样作物三条东西</h2>
 * <ol>
 *   <li><b>植株</b> {@link ModCropBlock} —— 种在耕地上，八个生长阶段；</li>
 *   <li><b>种子</b> —— 就是植株方块的 {@link BlockItem}，右键耕地即种下；</li>
 *   <li><b>野生植株</b> {@link WildCropBlock} —— 野外自然生成，打掉就得种子。</li>
 * </ol>
 *
 * <p>所以"种子"在代码里只有一份，不存在"物品种子"和"方块种子"两套要对齐的问题。</p>
 *
 * <h2>为什么没有 {@code IEventBus} 之外的依赖</h2>
 * 植株的行为全在原版 {@code CropBlock} 里（就地生长、骨粉催熟、光不够不长），
 * 掉落全在战利品表里。这个类因此只是一张"名字 -> 方块"的清单。
 */
public final class ModCrops {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    /**
     * 种在地里的作物：没有碰撞箱、踩一下就掉、会随机生长。
     *
     * <p>注意第三个参数是 {@code UnaryOperator<Properties>}（拿到属性再加料），
     * 不是现成的 {@code Properties} —— 注册表要先挂上 id 再交给构造器，
     * 所以只能连线传。写成 {@code ModCrops.cropProps()} 会编译不过。</p>
     */
    private static BlockBehaviour.Properties cropProps(BlockBehaviour.Properties props) {
        return props.noCollision()
                .randomTicks()
                .instabreak()
                .sound(SoundType.CROP)
                .pushReaction(PushReaction.DESTROY);
    }

    /** 野生的：同样没有碰撞箱，但**不**随机生长（它一长出来就是熟的）。 */
    private static BlockBehaviour.Properties wildProps(BlockBehaviour.Properties props) {
        return props.noCollision()
                .instabreak()
                .sound(SoundType.CROP)
                .pushReaction(PushReaction.DESTROY);
    }

    /** 全部种子物品（创造标签页用）。 */
    public static List<DeferredItem<? extends Item>> allSeeds() {
        return SEEDS;
    }

    /**
     * 全部<b>种在地里</b>的植株（创造标签页用）。
     *
     * <p>野生植株<b>不在</b>这里：它们没有对应的物品（拿不到手里），
     * 而创造页要的是物品栈，所以放进创造页只会是一个空。
     * 想摆出来看就去野外找，或者用 {@code /setblock}。</p>
     */
    public static List<DeferredBlock<?>> allPlants() {
        return PLANTS;
    }

    /** 全部植株方块，含野生（调试与校验用）。 */
    public static List<DeferredBlock<?>> allCrops() {
        return CROPS;
    }

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
    }

    private ModCrops() {}

    // ==================================================================
    // 植株与种子（按株型分组，方便对照贴图）
    // ==================================================================

    // ---- 禾本：一根主茎挑着穗子 ----

    /** 水稻（Rice）：种子「水稻」，收成「paddy」。 */
    public static final DeferredBlock<ModCropBlock> RICE_CROP =
            BLOCKS.registerBlock("rice_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> RICE_SEEDS =
            ITEMS.registerSimpleBlockItem("rice_seeds", RICE_CROP);

    /** 谷子（Millet）：种子「谷子」，收成「millet_grass」。 */
    public static final DeferredBlock<ModCropBlock> MILLET_CROP =
            BLOCKS.registerBlock("millet_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> MILLET_SEEDS =
            ITEMS.registerSimpleBlockItem("millet_seeds", MILLET_CROP);

    /** 高粱（Sorghum）：种子「高粱」，收成「sorghum」。 */
    public static final DeferredBlock<ModCropBlock> SORGHUM_CROP =
            BLOCKS.registerBlock("sorghum_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> SORGHUM_SEEDS =
            ITEMS.registerSimpleBlockItem("sorghum_seeds", SORGHUM_CROP);

    /** 玉米（Corn）：种子「玉米」，收成「corn」。 */
    public static final DeferredBlock<ModCropBlock> CORN_CROP =
            BLOCKS.registerBlock("corn_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CORN_SEEDS =
            ITEMS.registerSimpleBlockItem("corn_seeds", CORN_CROP);



    // ---- 豆科：矮丛上挂着豆荚 ----

    /** 黄豆（Soybean）：种子「黄豆」，收成「soybean」。 */
    public static final DeferredBlock<ModCropBlock> SOYBEAN_CROP =
            BLOCKS.registerBlock("soybean_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> SOYBEAN_SEEDS =
            ITEMS.registerSimpleBlockItem("soybean_seeds", SOYBEAN_CROP);

    /** 绿豆（Mung Bean）：种子「绿豆」，收成「mung_bean」。 */
    public static final DeferredBlock<ModCropBlock> MUNG_BEAN_CROP =
            BLOCKS.registerBlock("mung_bean_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> MUNG_BEAN_SEEDS =
            ITEMS.registerSimpleBlockItem("mung_bean_seeds", MUNG_BEAN_CROP);

    /** 红豆（Red Bean）：种子「红豆」，收成「red_bean」。 */
    public static final DeferredBlock<ModCropBlock> RED_BEAN_CROP =
            BLOCKS.registerBlock("red_bean_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> RED_BEAN_SEEDS =
            ITEMS.registerSimpleBlockItem("red_bean_seeds", RED_BEAN_CROP);

    /** 豌豆（Pea）：种子「豌豆」，收成「pea」。 */
    public static final DeferredBlock<ModCropBlock> PEA_CROP =
            BLOCKS.registerBlock("pea_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> PEA_SEEDS =
            ITEMS.registerSimpleBlockItem("pea_seeds", PEA_CROP);

    /** 蚕豆（Broad Bean）：种子「蚕豆」，收成「broad_bean」。 */
    public static final DeferredBlock<ModCropBlock> BROAD_BEAN_CROP =
            BLOCKS.registerBlock("broad_bean_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> BROAD_BEAN_SEEDS =
            ITEMS.registerSimpleBlockItem("broad_bean_seeds", BROAD_BEAN_CROP);

    /** 豆角（Green Bean）：种子「豆角」，收成「green_bean」。 */
    public static final DeferredBlock<ModCropBlock> GREEN_BEAN_CROP =
            BLOCKS.registerBlock("green_bean_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> GREEN_BEAN_SEEDS =
            ITEMS.registerSimpleBlockItem("green_bean_seeds", GREEN_BEAN_CROP);

    /** 花生（Peanut）：种子「花生」，收成「peanut」。 */
    public static final DeferredBlock<ModCropBlock> PEANUT_CROP =
            BLOCKS.registerBlock("peanut_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> PEANUT_SEEDS =
            ITEMS.registerSimpleBlockItem("peanut_seeds", PEANUT_CROP);



    // ---- 籽用：细茎顶着小蒴果 ----

    /** 芝麻（Sesame）：种子「芝麻」，收成「sesame」。 */
    public static final DeferredBlock<ModCropBlock> SESAME_CROP =
            BLOCKS.registerBlock("sesame_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> SESAME_SEEDS =
            ITEMS.registerSimpleBlockItem("sesame_seeds", SESAME_CROP);



    // ---- 块根块茎：贴地叶 + 露头的根 ----

    /** 萝卜（Radish）：种子「萝卜」，收成「radish」。 */
    public static final DeferredBlock<ModCropBlock> RADISH_CROP =
            BLOCKS.registerBlock("radish_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> RADISH_SEEDS =
            ITEMS.registerSimpleBlockItem("radish_seeds", RADISH_CROP);

    /** 芋头（Taro）：种子「芋头」，收成「taro」。 */
    public static final DeferredBlock<ModCropBlock> TARO_CROP =
            BLOCKS.registerBlock("taro_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> TARO_SEEDS =
            ITEMS.registerSimpleBlockItem("taro_seeds", TARO_CROP);

    /** 红薯（Sweet Potato）：种子「红薯」，收成「sweet_potato」。 */
    public static final DeferredBlock<ModCropBlock> SWEET_POTATO_CROP =
            BLOCKS.registerBlock("sweet_potato_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> SWEET_POTATO_SLIP =
            ITEMS.registerSimpleBlockItem("sweet_potato_slip", SWEET_POTATO_CROP);

    /** 山药（Chinese Yam）：种子「山药」，收成「chinese_yam」。 */
    public static final DeferredBlock<ModCropBlock> CHINESE_YAM_CROP =
            BLOCKS.registerBlock("chinese_yam_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CHINESE_YAM_SLIP =
            ITEMS.registerSimpleBlockItem("chinese_yam_slip", CHINESE_YAM_CROP);

    /** 姜（Ginger）：种子「姜」，收成「ginger」。 */
    public static final DeferredBlock<ModCropBlock> GINGER_CROP =
            BLOCKS.registerBlock("ginger_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> GINGER_SEEDS =
            ITEMS.registerSimpleBlockItem("ginger_seeds", GINGER_CROP);

    /** 蒜（Garlic）：种子「蒜」，收成「garlic」。 */
    public static final DeferredBlock<ModCropBlock> GARLIC_CROP =
            BLOCKS.registerBlock("garlic_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> GARLIC_SEEDS =
            ITEMS.registerSimpleBlockItem("garlic_seeds", GARLIC_CROP);



    // ---- 叶菜：一层层向外摊开 ----

    /** 白菜（Napa Cabbage）：种子「白菜」，收成「napa_cabbage」。 */
    public static final DeferredBlock<ModCropBlock> NAPA_CABBAGE_CROP =
            BLOCKS.registerBlock("napa_cabbage_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> NAPA_CABBAGE_SEEDS =
            ITEMS.registerSimpleBlockItem("napa_cabbage_seeds", NAPA_CABBAGE_CROP);

    /** 小白菜（Bok Choy）：种子「小白菜」，收成「bok_choy」。 */
    public static final DeferredBlock<ModCropBlock> BOK_CHOY_CROP =
            BLOCKS.registerBlock("bok_choy_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> BOK_CHOY_SEEDS =
            ITEMS.registerSimpleBlockItem("bok_choy_seeds", BOK_CHOY_CROP);

    /** 菠菜（Spinach）：种子「菠菜」，收成「spinach」。 */
    public static final DeferredBlock<ModCropBlock> SPINACH_CROP =
            BLOCKS.registerBlock("spinach_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> SPINACH_SEEDS =
            ITEMS.registerSimpleBlockItem("spinach_seeds", SPINACH_CROP);

    /** 芹菜（Celery）：种子「芹菜」，收成「celery」。 */
    public static final DeferredBlock<ModCropBlock> CELERY_CROP =
            BLOCKS.registerBlock("celery_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CELERY_SEEDS =
            ITEMS.registerSimpleBlockItem("celery_seeds", CELERY_CROP);

    /** 香菜（Cilantro）：种子「香菜」，收成「cilantro」。 */
    public static final DeferredBlock<ModCropBlock> CILANTRO_CROP =
            BLOCKS.registerBlock("cilantro_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CILANTRO_SEEDS =
            ITEMS.registerSimpleBlockItem("cilantro_seeds", CILANTRO_CROP);

    /** 韭菜（Chive）：种子「韭菜」，收成「chive」。 */
    public static final DeferredBlock<ModCropBlock> CHIVE_CROP =
            BLOCKS.registerBlock("chive_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CHIVE_SEEDS =
            ITEMS.registerSimpleBlockItem("chive_seeds", CHIVE_CROP);

    /** 葱（Scallion）：种子「葱」，收成「scallion」。 */
    public static final DeferredBlock<ModCropBlock> SCALLION_CROP =
            BLOCKS.registerBlock("scallion_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> SCALLION_SEEDS =
            ITEMS.registerSimpleBlockItem("scallion_seeds", SCALLION_CROP);



    // ---- 茄果：小灌木垂着果实 ----

    /** 辣椒（Chili）：种子「辣椒」，收成「chili」。 */
    public static final DeferredBlock<ModCropBlock> CHILI_CROP =
            BLOCKS.registerBlock("chili_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CHILI_SEEDS =
            ITEMS.registerSimpleBlockItem("chili_seeds", CHILI_CROP);

    /** 茄子（Eggplant）：种子「茄子」，收成「eggplant」。 */
    public static final DeferredBlock<ModCropBlock> EGGPLANT_CROP =
            BLOCKS.registerBlock("eggplant_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> EGGPLANT_SEEDS =
            ITEMS.registerSimpleBlockItem("eggplant_seeds", EGGPLANT_CROP);

    /** 西红柿（Tomato）：种子「西红柿」，收成「tomato」。 */
    public static final DeferredBlock<ModCropBlock> TOMATO_CROP =
            BLOCKS.registerBlock("tomato_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> TOMATO_SEEDS =
            ITEMS.registerSimpleBlockItem("tomato_seeds", TOMATO_CROP);



    // ---- 藤本：蔓生的藤与大叶 ----

    /** 黄瓜（Cucumber）：种子「黄瓜」，收成「cucumber」。 */
    public static final DeferredBlock<ModCropBlock> CUCUMBER_CROP =
            BLOCKS.registerBlock("cucumber_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> CUCUMBER_SEEDS =
            ITEMS.registerSimpleBlockItem("cucumber_seeds", CUCUMBER_CROP);

    /** 冬瓜（Winter Melon）：种子「冬瓜」，收成「winter_melon」。 */
    public static final DeferredBlock<ModCropBlock> WINTER_MELON_CROP =
            BLOCKS.registerBlock("winter_melon_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> WINTER_MELON_SEEDS =
            ITEMS.registerSimpleBlockItem("winter_melon_seeds", WINTER_MELON_CROP);

    /** 丝瓜（Luffa）：种子「丝瓜」，收成「luffa」。 */
    public static final DeferredBlock<ModCropBlock> LUFFA_CROP =
            BLOCKS.registerBlock("luffa_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> LUFFA_SEEDS =
            ITEMS.registerSimpleBlockItem("luffa_seeds", LUFFA_CROP);

    /** 苦瓜（Bitter Melon）：种子「苦瓜」，收成「bitter_melon」。 */
    public static final DeferredBlock<ModCropBlock> BITTER_MELON_CROP =
            BLOCKS.registerBlock("bitter_melon_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> BITTER_MELON_SEEDS =
            ITEMS.registerSimpleBlockItem("bitter_melon_seeds", BITTER_MELON_CROP);



    // ---- 菌：簸开的耳片 ----

    /** 木耳（Wood Ear）：种子「木耳」，收成「wood_ear」。 */
    public static final DeferredBlock<ModCropBlock> WOOD_EAR_CROP =
            BLOCKS.registerBlock("wood_ear_crop", ModCropBlock::new, ModCrops::cropProps);
    public static final DeferredItem<BlockItem> WOOD_EAR_SPAWN =
            ITEMS.registerSimpleBlockItem("wood_ear_spawn", WOOD_EAR_CROP);


    // ---- 野生植株：野外自然生成，打掉直接给种子 ----

    /** 野生的水稻（Rice）。 */
    public static final DeferredBlock<WildCropBlock> WILD_RICE =
            BLOCKS.registerBlock("wild_rice", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的谷子（Millet）。 */
    public static final DeferredBlock<WildCropBlock> WILD_MILLET =
            BLOCKS.registerBlock("wild_millet", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的高粱（Sorghum）。 */
    public static final DeferredBlock<WildCropBlock> WILD_SORGHUM =
            BLOCKS.registerBlock("wild_sorghum", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的玉米（Corn）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CORN =
            BLOCKS.registerBlock("wild_corn", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的黄豆（Soybean）。 */
    public static final DeferredBlock<WildCropBlock> WILD_SOYBEAN =
            BLOCKS.registerBlock("wild_soybean", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的绿豆（Mung Bean）。 */
    public static final DeferredBlock<WildCropBlock> WILD_MUNG_BEAN =
            BLOCKS.registerBlock("wild_mung_bean", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的红豆（Red Bean）。 */
    public static final DeferredBlock<WildCropBlock> WILD_RED_BEAN =
            BLOCKS.registerBlock("wild_red_bean", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的豌豆（Pea）。 */
    public static final DeferredBlock<WildCropBlock> WILD_PEA =
            BLOCKS.registerBlock("wild_pea", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的蚕豆（Broad Bean）。 */
    public static final DeferredBlock<WildCropBlock> WILD_BROAD_BEAN =
            BLOCKS.registerBlock("wild_broad_bean", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的豆角（Green Bean）。 */
    public static final DeferredBlock<WildCropBlock> WILD_GREEN_BEAN =
            BLOCKS.registerBlock("wild_green_bean", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的花生（Peanut）。 */
    public static final DeferredBlock<WildCropBlock> WILD_PEANUT =
            BLOCKS.registerBlock("wild_peanut", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的芝麻（Sesame）。 */
    public static final DeferredBlock<WildCropBlock> WILD_SESAME =
            BLOCKS.registerBlock("wild_sesame", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的萝卜（Radish）。 */
    public static final DeferredBlock<WildCropBlock> WILD_RADISH =
            BLOCKS.registerBlock("wild_radish", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的芋头（Taro）。 */
    public static final DeferredBlock<WildCropBlock> WILD_TARO =
            BLOCKS.registerBlock("wild_taro", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的红薯（Sweet Potato）。 */
    public static final DeferredBlock<WildCropBlock> WILD_SWEET_POTATO =
            BLOCKS.registerBlock("wild_sweet_potato", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的山药（Chinese Yam）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CHINESE_YAM =
            BLOCKS.registerBlock("wild_chinese_yam", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的白菜（Napa Cabbage）。 */
    public static final DeferredBlock<WildCropBlock> WILD_NAPA_CABBAGE =
            BLOCKS.registerBlock("wild_napa_cabbage", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的小白菜（Bok Choy）。 */
    public static final DeferredBlock<WildCropBlock> WILD_BOK_CHOY =
            BLOCKS.registerBlock("wild_bok_choy", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的菠菜（Spinach）。 */
    public static final DeferredBlock<WildCropBlock> WILD_SPINACH =
            BLOCKS.registerBlock("wild_spinach", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的芹菜（Celery）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CELERY =
            BLOCKS.registerBlock("wild_celery", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的香菜（Cilantro）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CILANTRO =
            BLOCKS.registerBlock("wild_cilantro", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的韭菜（Chive）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CHIVE =
            BLOCKS.registerBlock("wild_chive", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的葱（Scallion）。 */
    public static final DeferredBlock<WildCropBlock> WILD_SCALLION =
            BLOCKS.registerBlock("wild_scallion", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的辣椒（Chili）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CHILI =
            BLOCKS.registerBlock("wild_chili", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的茄子（Eggplant）。 */
    public static final DeferredBlock<WildCropBlock> WILD_EGGPLANT =
            BLOCKS.registerBlock("wild_eggplant", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的西红柿（Tomato）。 */
    public static final DeferredBlock<WildCropBlock> WILD_TOMATO =
            BLOCKS.registerBlock("wild_tomato", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的黄瓜（Cucumber）。 */
    public static final DeferredBlock<WildCropBlock> WILD_CUCUMBER =
            BLOCKS.registerBlock("wild_cucumber", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的冬瓜（Winter Melon）。 */
    public static final DeferredBlock<WildCropBlock> WILD_WINTER_MELON =
            BLOCKS.registerBlock("wild_winter_melon", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的丝瓜（Luffa）。 */
    public static final DeferredBlock<WildCropBlock> WILD_LUFFA =
            BLOCKS.registerBlock("wild_luffa", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的苦瓜（Bitter Melon）。 */
    public static final DeferredBlock<WildCropBlock> WILD_BITTER_MELON =
            BLOCKS.registerBlock("wild_bitter_melon", WildCropBlock::new, ModCrops::wildProps);
    /** 野生的木耳（Wood Ear）。 */
    public static final DeferredBlock<WildCropBlock> WILD_WOOD_EAR =
            BLOCKS.registerBlock("wild_wood_ear", WildCropBlock::new, ModCrops::wildProps);

    /** 全部种子（创造标签页用）。 */
    private static final List<DeferredItem<? extends Item>> SEEDS = List.of(
            RICE_SEEDS,
            MILLET_SEEDS,
            SORGHUM_SEEDS,
            CORN_SEEDS,
            SOYBEAN_SEEDS,
            MUNG_BEAN_SEEDS,
            RED_BEAN_SEEDS,
            PEA_SEEDS,
            BROAD_BEAN_SEEDS,
            GREEN_BEAN_SEEDS,
            PEANUT_SEEDS,
            SESAME_SEEDS,
            RADISH_SEEDS,
            TARO_SEEDS,
            SWEET_POTATO_SLIP,
            CHINESE_YAM_SLIP,
            GINGER_SEEDS,
            GARLIC_SEEDS,
            NAPA_CABBAGE_SEEDS,
            BOK_CHOY_SEEDS,
            SPINACH_SEEDS,
            CELERY_SEEDS,
            CILANTRO_SEEDS,
            CHIVE_SEEDS,
            SCALLION_SEEDS,
            CHILI_SEEDS,
            EGGPLANT_SEEDS,
            TOMATO_SEEDS,
            CUCUMBER_SEEDS,
            WINTER_MELON_SEEDS,
            LUFFA_SEEDS,
            BITTER_MELON_SEEDS,
            WOOD_EAR_SPAWN
    );

    /** 全部植株（含野生）。 */
    private static final List<DeferredBlock<?>> CROPS = List.of(
            RICE_CROP,
            WILD_RICE,
            MILLET_CROP,
            WILD_MILLET,
            SORGHUM_CROP,
            WILD_SORGHUM,
            CORN_CROP,
            WILD_CORN,
            SOYBEAN_CROP,
            WILD_SOYBEAN,
            MUNG_BEAN_CROP,
            WILD_MUNG_BEAN,
            RED_BEAN_CROP,
            WILD_RED_BEAN,
            PEA_CROP,
            WILD_PEA,
            BROAD_BEAN_CROP,
            WILD_BROAD_BEAN,
            GREEN_BEAN_CROP,
            WILD_GREEN_BEAN,
            PEANUT_CROP,
            WILD_PEANUT,
            SESAME_CROP,
            WILD_SESAME,
            RADISH_CROP,
            WILD_RADISH,
            TARO_CROP,
            WILD_TARO,
            SWEET_POTATO_CROP,
            WILD_SWEET_POTATO,
            CHINESE_YAM_CROP,
            WILD_CHINESE_YAM,
            GINGER_CROP,
            GARLIC_CROP,
            NAPA_CABBAGE_CROP,
            WILD_NAPA_CABBAGE,
            BOK_CHOY_CROP,
            WILD_BOK_CHOY,
            SPINACH_CROP,
            WILD_SPINACH,
            CELERY_CROP,
            WILD_CELERY,
            CILANTRO_CROP,
            WILD_CILANTRO,
            CHIVE_CROP,
            WILD_CHIVE,
            SCALLION_CROP,
            WILD_SCALLION,
            CHILI_CROP,
            WILD_CHILI,
            EGGPLANT_CROP,
            WILD_EGGPLANT,
            TOMATO_CROP,
            WILD_TOMATO,
            CUCUMBER_CROP,
            WILD_CUCUMBER,
            WINTER_MELON_CROP,
            WILD_WINTER_MELON,
            LUFFA_CROP,
            WILD_LUFFA,
            BITTER_MELON_CROP,
            WILD_BITTER_MELON,
            WOOD_EAR_CROP,
            WILD_WOOD_EAR
    );

    /** 只有种在地里的那些（有物品、能进创造页）。 */
    private static final List<DeferredBlock<?>> PLANTS = List.of(
            RICE_CROP,
            MILLET_CROP,
            SORGHUM_CROP,
            CORN_CROP,
            SOYBEAN_CROP,
            MUNG_BEAN_CROP,
            RED_BEAN_CROP,
            PEA_CROP,
            BROAD_BEAN_CROP,
            GREEN_BEAN_CROP,
            PEANUT_CROP,
            SESAME_CROP,
            RADISH_CROP,
            TARO_CROP,
            SWEET_POTATO_CROP,
            CHINESE_YAM_CROP,
            GINGER_CROP,
            GARLIC_CROP,
            NAPA_CABBAGE_CROP,
            BOK_CHOY_CROP,
            SPINACH_CROP,
            CELERY_CROP,
            CILANTRO_CROP,
            CHIVE_CROP,
            SCALLION_CROP,
            CHILI_CROP,
            EGGPLANT_CROP,
            TOMATO_CROP,
            CUCUMBER_CROP,
            WINTER_MELON_CROP,
            LUFFA_CROP,
            BITTER_MELON_CROP,
            WOOD_EAR_CROP
    );
}
