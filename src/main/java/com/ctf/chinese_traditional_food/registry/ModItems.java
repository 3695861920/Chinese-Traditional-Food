package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.food.DishEffects;
import com.ctf.chinese_traditional_food.common.item.DishItem;
import java.util.List;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 物品注册表。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b>
 * 要加物品 / 改配方，请编辑 {@code tools/content_data.py} 后重新生成。</p>
 *
 * <p>内容规模：基础食材、调味料、水果、蔬菜、厨具餐具，以及
 * 八大菜系与九大传统节日的菜品，全部实现为可摆放的 {@link DishItem}。</p>
 */
@SuppressWarnings("unused")
public final class ModItems {
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(ChineseTraditionalFood.MOD_ID);

    // ==================================================================
    // 摆放方块对应的方块物品（手写部分，见 ModBlocks）
    // ==================================================================

    /** 餐盘，摆放 1 份菜。 */
    public static final DeferredItem<BlockItem> PLATE = ITEMS.registerSimpleBlockItem(ModBlocks.PLATE);

    /** 案板，放上食材后用刀切。 */
    public static final DeferredItem<BlockItem> CUTTING_BOARD =
            ITEMS.registerSimpleBlockItem(ModBlocks.CUTTING_BOARD);

    /** 电动脱壳机，吃电给谷物脱壳。 */
    public static final DeferredItem<BlockItem> ELECTRIC_SHELLER =
            ITEMS.registerSimpleBlockItem(ModBlocks.ELECTRIC_SHELLER);

    /** 电动磨粉机，吃电把谷物磨成粉。 */
    public static final DeferredItem<BlockItem> ELECTRIC_MILL =
            ITEMS.registerSimpleBlockItem(ModBlocks.ELECTRIC_MILL);

    /** 熔炉发电机，烧燃料发电。 */
    public static final DeferredItem<BlockItem> FURNACE_GENERATOR =
            ITEMS.registerSimpleBlockItem(ModBlocks.FURNACE_GENERATOR);

    // ---- 大型机（"3×3 放大版"）--------------------------------------
    // 仍是单方块，但造型铺满整格、没有腿部留空；数值上批次 ×4、
    // 速度快 3.3 倍、单位耗电约三成。详见 MachineEnergy 的"大型机"一节。

    /** 大型熔炉发电机，200 FE/t、缓冲 40000 FE。 */
    public static final DeferredItem<BlockItem> LARGE_FURNACE_GENERATOR =
            ITEMS.registerSimpleBlockItem(ModBlocks.LARGE_FURNACE_GENERATOR);

    /** 大型电动磨粉机，32 个一批 / 3 秒一批。 */
    public static final DeferredItem<BlockItem> LARGE_ELECTRIC_MILL =
            ITEMS.registerSimpleBlockItem(ModBlocks.LARGE_ELECTRIC_MILL);

    /** 大型电动脱壳机，32 个一批 / 3 秒一批。 */
    public static final DeferredItem<BlockItem> LARGE_ELECTRIC_SHELLER =
            ITEMS.registerSimpleBlockItem(ModBlocks.LARGE_ELECTRIC_SHELLER);

    // ---- 灶火系统：炉灶 + 三件锅具 --------------------------------------
    // 和电力系统并行的一条路线：炉灶烧燃料只供热，锅具坐在它正上方用热。

    /** 炉灶，烧燃料给正上方一格的锅具供热。 */
    public static final DeferredItem<BlockItem> STOVE =
            ITEMS.registerSimpleBlockItem(ModBlocks.STOVE);

    /** 炒锅，坐在炉灶上快炒。 */
    public static final DeferredItem<BlockItem> WOK =
            ITEMS.registerSimpleBlockItem(ModBlocks.WOK);

    /** 蒸笼，坐在炉灶上蒸。 */
    public static final DeferredItem<BlockItem> STEAMER =
            ITEMS.registerSimpleBlockItem(ModBlocks.STEAMER);

    /** 汤锅，坐在炉灶上吊汤。 */
    public static final DeferredItem<BlockItem> SOUP_POT =
            ITEMS.registerSimpleBlockItem(ModBlocks.SOUP_POT);

    // ==================================================================
    // 基础食材
    // ==================================================================

    /** 稻谷（Paddy）。 */
    public static final DeferredItem<Item> PADDY = ITEMS.registerSimpleItem("paddy");

    /** 谷子（Foxtail Millet Grass）。 */
    public static final DeferredItem<Item> MILLET_GRASS = ITEMS.registerSimpleItem("millet_grass");

    /** 米糠（Rice Bran）。 */
    public static final DeferredItem<Item> RICE_BRAN = ITEMS.registerSimpleItem("rice_bran");

    /** 大米（Rice）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> RICE = ITEMS.registerItem(
            "rice",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 糯米（Glutinous Rice）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GLUTINOUS_RICE = ITEMS.registerItem(
            "glutinous_rice",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 小米（Millet）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> MILLET = ITEMS.registerItem(
            "millet",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 高粱（Sorghum）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SORGHUM = ITEMS.registerItem(
            "sorghum",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 玉米（Corn）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CORN = ITEMS.registerItem(
            "corn",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 面粉（Flour）。 */
    public static final DeferredItem<Item> FLOUR = ITEMS.registerSimpleItem("flour");

    /** 米粉（Rice Flour）。 */
    public static final DeferredItem<Item> RICE_FLOUR = ITEMS.registerSimpleItem("rice_flour");

    /** 糯米粉（Glutinous Rice Flour）。 */
    public static final DeferredItem<Item> GLUTINOUS_RICE_FLOUR = ITEMS.registerSimpleItem("glutinous_rice_flour");

    /** 玉米面（Cornmeal）。 */
    public static final DeferredItem<Item> CORN_FLOUR = ITEMS.registerSimpleItem("corn_flour");

    /** 淀粉（Starch）。 */
    public static final DeferredItem<Item> STARCH = ITEMS.registerSimpleItem("starch");

    /** 红豆（Red Bean）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> RED_BEAN = ITEMS.registerItem(
            "red_bean",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 绿豆（Mung Bean）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> MUNG_BEAN = ITEMS.registerItem(
            "mung_bean",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 黄豆（Soybean）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SOYBEAN = ITEMS.registerItem(
            "soybean",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 黑豆（Black Bean）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BLACK_BEAN = ITEMS.registerItem(
            "black_bean",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 豌豆（Pea）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PEA = ITEMS.registerItem(
            "pea",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 蚕豆（Broad Bean）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BROAD_BEAN = ITEMS.registerItem(
            "broad_bean",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 豆沙（Red Bean Paste）：2 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BEAN_PASTE = ITEMS.registerItem(
            "bean_paste",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.20F)
                        .build()));

    /** 豆芽（Bean Sprouts）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> DOU_YA = ITEMS.registerItem(
            "dou_ya",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 红薯（Sweet Potato）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SWEET_POTATO = ITEMS.registerItem(
            "sweet_potato",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 烤红薯（Baked Sweet Potato）：5 饥饿 / 0.6 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BAKED_SWEET_POTATO = ITEMS.registerItem(
            "baked_sweet_potato",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.60F)
                        .build()));

    /** 山药（Chinese Yam）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CHINESE_YAM = ITEMS.registerItem(
            "chinese_yam",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 芋头（Taro）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> TARO = ITEMS.registerItem(
            "taro",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 豆腐（Tofu）：3 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> TOFU = ITEMS.registerItem(
            "tofu",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.30F)
                        .build()));

    /** 花生（Peanut）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PEANUT = ITEMS.registerItem(
            "peanut",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 芝麻（Sesame）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SESAME = ITEMS.registerItem(
            "sesame",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 莲子（Lotus Seed）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> LOTUS_SEED = ITEMS.registerItem(
            "lotus_seed",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 枸杞（Goji Berry）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GOJI_BERRY = ITEMS.registerItem(
            "goji_berry",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 红枣（Red Date）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> RED_DATE = ITEMS.registerItem(
            "red_date",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 干枣（Dried Jujube）：3 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> DRIED_JUJUBE = ITEMS.registerItem(
            "dried_jujube",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.40F)
                        .build()));

    /** 桂圆（Longan）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> LONGAN = ITEMS.registerItem(
            "longan",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 桂花（Osmanthus）。 */
    public static final DeferredItem<Item> OSMANTHUS = ITEMS.registerSimpleItem("osmanthus");

    /** 荔枝（Lychee）：4 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> LYCHEE = ITEMS.registerItem(
            "lychee",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.40F)
                        .build()));

    /** 蔬菜丝（Shredded Vegetables）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SHREDDED_VEGETABLE = ITEMS.registerItem(
            "shredded_vegetable",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 肉丝（Shredded Meat）：3 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SHREDDED_MEAT = ITEMS.registerItem(
            "shredded_meat",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.40F)
                        .build()));

    /** 鱼片（Fish Fillet）：3 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> FISH_FILLET = ITEMS.registerItem(
            "fish_fillet",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.40F)
                        .build()));

    /** 豆腐丝（Shredded Tofu）：3 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SHREDDED_TOFU = ITEMS.registerItem(
            "shredded_tofu",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.30F)
                        .build()));

    // ==================================================================
    // 作物种子
    // ==================================================================

    /** 稻种（Rice Seeds）。 */
    public static final DeferredItem<Item> RICE_SEEDS = ITEMS.registerItem(
        "rice_seeds",
        props -> new BlockItem(ModBlocks.RICE_CROP.get(), props));

    /** 谷种（Millet Seeds）。 */
    public static final DeferredItem<Item> MILLET_SEEDS = ITEMS.registerSimpleItem("millet_seeds");

    /** 高粱种（Sorghum Seeds）。 */
    public static final DeferredItem<Item> SORGHUM_SEEDS = ITEMS.registerSimpleItem("sorghum_seeds");

    /** 玉米种（Corn Kernels）。 */
    public static final DeferredItem<Item> CORN_SEEDS = ITEMS.registerSimpleItem("corn_seeds");

    /** 黄豆种（Soybean Seeds）。 */
    public static final DeferredItem<Item> SOYBEAN_SEEDS = ITEMS.registerSimpleItem("soybean_seeds");

    /** 绿豆种（Mung Bean Seeds）。 */
    public static final DeferredItem<Item> MUNG_BEAN_SEEDS = ITEMS.registerSimpleItem("mung_bean_seeds");

    /** 红豆种（Red Bean Seeds）。 */
    public static final DeferredItem<Item> RED_BEAN_SEEDS = ITEMS.registerSimpleItem("red_bean_seeds");

    /** 豌豆种（Pea Seeds）。 */
    public static final DeferredItem<Item> PEA_SEEDS = ITEMS.registerSimpleItem("pea_seeds");

    /** 蚕豆种（Broad Bean Seeds）。 */
    public static final DeferredItem<Item> BROAD_BEAN_SEEDS = ITEMS.registerSimpleItem("broad_bean_seeds");

    /** 豆角种（Green Bean Seeds）。 */
    public static final DeferredItem<Item> GREEN_BEAN_SEEDS = ITEMS.registerSimpleItem("green_bean_seeds");

    /** 花生种（Peanut Seeds）。 */
    public static final DeferredItem<Item> PEANUT_SEEDS = ITEMS.registerSimpleItem("peanut_seeds");

    /** 芝麻种（Sesame Seeds）。 */
    public static final DeferredItem<Item> SESAME_SEEDS = ITEMS.registerSimpleItem("sesame_seeds");

    /** 芋种（Taro Corms）。 */
    public static final DeferredItem<Item> TARO_SEEDS = ITEMS.registerSimpleItem("taro_seeds");

    /** 红薯秧（Sweet Potato Slips）。 */
    public static final DeferredItem<Item> SWEET_POTATO_SLIP = ITEMS.registerSimpleItem("sweet_potato_slip");

    /** 山药嘴子（Yam Sets）。 */
    public static final DeferredItem<Item> CHINESE_YAM_SLIP = ITEMS.registerSimpleItem("chinese_yam_slip");

    /** 姜种（Ginger Sets）。 */
    public static final DeferredItem<Item> GINGER_SEEDS = ITEMS.registerSimpleItem("ginger_seeds");

    /** 蒜种（Garlic Cloves）。 */
    public static final DeferredItem<Item> GARLIC_SEEDS = ITEMS.registerSimpleItem("garlic_seeds");

    /** 白菜种（Napa Cabbage Seeds）。 */
    public static final DeferredItem<Item> NAPA_CABBAGE_SEEDS = ITEMS.registerSimpleItem("napa_cabbage_seeds");

    /** 小白菜种（Bok Choy Seeds）。 */
    public static final DeferredItem<Item> BOK_CHOY_SEEDS = ITEMS.registerSimpleItem("bok_choy_seeds");

    /** 萝卜种（Radish Seeds）。 */
    public static final DeferredItem<Item> RADISH_SEEDS = ITEMS.registerSimpleItem("radish_seeds");

    /** 菠菜种（Spinach Seeds）。 */
    public static final DeferredItem<Item> SPINACH_SEEDS = ITEMS.registerSimpleItem("spinach_seeds");

    /** 芹菜种（Celery Seeds）。 */
    public static final DeferredItem<Item> CELERY_SEEDS = ITEMS.registerSimpleItem("celery_seeds");

    /** 香菜种（Cilantro Seeds）。 */
    public static final DeferredItem<Item> CILANTRO_SEEDS = ITEMS.registerSimpleItem("cilantro_seeds");

    /** 韭菜种（Chive Seeds）。 */
    public static final DeferredItem<Item> CHIVE_SEEDS = ITEMS.registerSimpleItem("chive_seeds");

    /** 葱种（Scallion Seeds）。 */
    public static final DeferredItem<Item> SCALLION_SEEDS = ITEMS.registerSimpleItem("scallion_seeds");

    /** 辣椒种（Chili Seeds）。 */
    public static final DeferredItem<Item> CHILI_SEEDS = ITEMS.registerSimpleItem("chili_seeds");

    /** 茄子种（Eggplant Seeds）。 */
    public static final DeferredItem<Item> EGGPLANT_SEEDS = ITEMS.registerSimpleItem("eggplant_seeds");

    /** 西红柿种（Tomato Seeds）。 */
    public static final DeferredItem<Item> TOMATO_SEEDS = ITEMS.registerSimpleItem("tomato_seeds");

    /** 黄瓜种（Cucumber Seeds）。 */
    public static final DeferredItem<Item> CUCUMBER_SEEDS = ITEMS.registerSimpleItem("cucumber_seeds");

    /** 冬瓜种（Winter Melon Seeds）。 */
    public static final DeferredItem<Item> WINTER_MELON_SEEDS = ITEMS.registerSimpleItem("winter_melon_seeds");

    /** 丝瓜种（Luffa Seeds）。 */
    public static final DeferredItem<Item> LUFFA_SEEDS = ITEMS.registerSimpleItem("luffa_seeds");

    /** 苦瓜种（Bitter Melon Seeds）。 */
    public static final DeferredItem<Item> BITTER_MELON_SEEDS = ITEMS.registerSimpleItem("bitter_melon_seeds");

    /** 木耳菌种（Wood Ear Spawn）。 */
    public static final DeferredItem<Item> WOOD_EAR_SPAWN = ITEMS.registerSimpleItem("wood_ear_spawn");

    // ==================================================================
    // 调味料
    // ==================================================================

    /** 盐（Salt）。 */
    public static final DeferredItem<Item> SALT = ITEMS.registerSimpleItem("salt");

    /** 冰糖（Rock Sugar）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> ROCK_SUGAR = ITEMS.registerItem(
            "rock_sugar",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 酱油（Soy Sauce）。 */
    public static final DeferredItem<Item> SOY_SAUCE = ITEMS.registerSimpleItem("soy_sauce");

    /** 醋（Vinegar）。 */
    public static final DeferredItem<Item> VINEGAR = ITEMS.registerSimpleItem("vinegar");

    /** 料酒（Cooking Wine）。 */
    public static final DeferredItem<Item> COOKING_WINE = ITEMS.registerSimpleItem("cooking_wine");

    /** 花椒（Sichuan Peppercorn）。 */
    public static final DeferredItem<Item> SICHUAN_PEPPERCORN = ITEMS.registerSimpleItem("sichuan_peppercorn");

    /** 八角（Star Anise）。 */
    public static final DeferredItem<Item> STAR_ANISE = ITEMS.registerSimpleItem("star_anise");

    /** 桂皮（Cinnamon Bark）。 */
    public static final DeferredItem<Item> CINNAMON_BARK = ITEMS.registerSimpleItem("cinnamon_bark");

    /** 香叶（Bay Leaf）。 */
    public static final DeferredItem<Item> BAY_LEAF = ITEMS.registerSimpleItem("bay_leaf");

    /** 孜然（Cumin）。 */
    public static final DeferredItem<Item> CUMIN = ITEMS.registerSimpleItem("cumin");

    /** 辣椒粉（Chili Powder）。 */
    public static final DeferredItem<Item> CHILI_POWDER = ITEMS.registerSimpleItem("chili_powder");

    /** 胡椒粉（Pepper Powder）。 */
    public static final DeferredItem<Item> PEPPER_POWDER = ITEMS.registerSimpleItem("pepper_powder");

    /** 五香粉（Five Spice Powder）。 */
    public static final DeferredItem<Item> FIVE_SPICE_POWDER = ITEMS.registerSimpleItem("five_spice_powder");

    /** 干辣椒（Dried Chili）。 */
    public static final DeferredItem<Item> DRIED_CHILI = ITEMS.registerSimpleItem("dried_chili");

    /** 豆瓣酱（Doubanjiang）。 */
    public static final DeferredItem<Item> DOUBANJIANG = ITEMS.registerSimpleItem("doubanjiang");

    /** 甜面酱（Sweet Bean Sauce）。 */
    public static final DeferredItem<Item> SWEET_BEAN_SAUCE = ITEMS.registerSimpleItem("sweet_bean_sauce");

    /** 蚝油（Oyster Sauce）。 */
    public static final DeferredItem<Item> OYSTER_SAUCE = ITEMS.registerSimpleItem("oyster_sauce");

    /** 香油（Sesame Oil）。 */
    public static final DeferredItem<Item> SESAME_OIL = ITEMS.registerSimpleItem("sesame_oil");

    /** 芝麻酱（Sesame Paste）。 */
    public static final DeferredItem<Item> SESAME_PASTE = ITEMS.registerSimpleItem("sesame_paste");

    /** 腐乳（Fermented Tofu）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> FERMENTED_TOFU = ITEMS.registerItem(
            "fermented_tofu",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 豆豉（Fermented Black Bean）：1 饥饿 / 0.1 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> DOUCHI = ITEMS.registerItem(
            "douchi",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.10F)
                        .build()));

    /** 辣椒油（Chili Oil）。 */
    public static final DeferredItem<Item> CHILI_OIL = ITEMS.registerSimpleItem("chili_oil");

    /** 高汤（Stock）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> STOCK = ITEMS.registerItem(
            "stock",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    // ==================================================================
    // 常见水果
    // ==================================================================

    /** 梨（Pear）：4 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PEAR = ITEMS.registerItem(
            "pear",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.30F)
                        .build()));

    /** 桃（Peach）：4 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PEACH = ITEMS.registerItem(
            "peach",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.30F)
                        .build()));

    /** 李子（Plum）：3 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PLUM = ITEMS.registerItem(
            "plum",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.30F)
                        .build()));

    /** 杏（Apricot）：3 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> APRICOT = ITEMS.registerItem(
            "apricot",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.30F)
                        .build()));

    /** 枣（Jujube）：3 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> JUJUBE = ITEMS.registerItem(
            "jujube",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.30F)
                        .build()));

    /** 柿子（Persimmon）：4 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PERSIMMON = ITEMS.registerItem(
            "persimmon",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.30F)
                        .build()));

    /** 橘子（Mandarin）：4 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> MANDARIN = ITEMS.registerItem(
            "mandarin",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.30F)
                        .build()));

    /** 柚子（Pomelo）：5 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> POMELO = ITEMS.registerItem(
            "pomelo",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.30F)
                        .build()));

    /** 香蕉（Banana）：5 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BANANA = ITEMS.registerItem(
            "banana",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.40F)
                        .build()));

    /** 葡萄（Grape）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GRAPE = ITEMS.registerItem(
            "grape",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 草莓（Strawberry）：3 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> STRAWBERRY = ITEMS.registerItem(
            "strawberry",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.40F)
                        .build()));

    /** 樱桃（Cherry）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CHERRY = ITEMS.registerItem(
            "cherry",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 石榴（Pomegranate）：4 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> POMEGRANATE = ITEMS.registerItem(
            "pomegranate",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.30F)
                        .build()));

    /** 猕猴桃（Kiwi）：3 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> KIWI = ITEMS.registerItem(
            "kiwi",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.30F)
                        .build()));

    /** 芒果（Mango）：5 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> MANGO = ITEMS.registerItem(
            "mango",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.40F)
                        .build()));

    /** 菠萝（Pineapple）：5 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PINEAPPLE = ITEMS.registerItem(
            "pineapple",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.40F)
                        .build()));

    // ==================================================================
    // 常见蔬菜
    // ==================================================================

    /** 白菜（Napa Cabbage）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> NAPA_CABBAGE = ITEMS.registerItem(
            "napa_cabbage",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 小白菜（Bok Choy）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BOK_CHOY = ITEMS.registerItem(
            "bok_choy",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 萝卜（Radish）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> RADISH = ITEMS.registerItem(
            "radish",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 菠菜（Spinach）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SPINACH = ITEMS.registerItem(
            "spinach",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 芹菜（Celery）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CELERY = ITEMS.registerItem(
            "celery",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 韭菜（Chive）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CHIVE = ITEMS.registerItem(
            "chive",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 茄子（Eggplant）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> EGGPLANT = ITEMS.registerItem(
            "eggplant",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 黄瓜（Cucumber）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CUCUMBER = ITEMS.registerItem(
            "cucumber",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 冬瓜（Winter Melon）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> WINTER_MELON = ITEMS.registerItem(
            "winter_melon",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 丝瓜（Luffa）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> LUFFA = ITEMS.registerItem(
            "luffa",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 苦瓜（Bitter Melon）：2 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BITTER_MELON = ITEMS.registerItem(
            "bitter_melon",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.20F)
                        .build()));

    /** 豆角（Green Bean）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GREEN_BEAN = ITEMS.registerItem(
            "green_bean",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 西红柿（Tomato）：3 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> TOMATO = ITEMS.registerItem(
            "tomato",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(3)
                        .saturationModifier(0.40F)
                        .build()));

    /** 辣椒（Chili Pepper）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CHILI = ITEMS.registerItem(
            "chili",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 葱（Scallion）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SCALLION = ITEMS.registerItem(
            "scallion",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 姜（Ginger）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GINGER = ITEMS.registerItem(
            "ginger",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 蒜（Garlic）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GARLIC = ITEMS.registerItem(
            "garlic",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 蒜苗（Garlic Sprout）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GARLIC_SPROUT = ITEMS.registerItem(
            "garlic_sprout",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 香菜（Cilantro）：1 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CILANTRO = ITEMS.registerItem(
            "cilantro",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(1)
                        .saturationModifier(0.20F)
                        .build()));

    /** 木耳（Wood Ear）：2 饥饿 / 0.2 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> WOOD_EAR = ITEMS.registerItem(
            "wood_ear",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.20F)
                        .build()));

    /** 笋（Bamboo Shoot）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BAMBOO_SHOOT = ITEMS.registerItem(
            "bamboo_shoot",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 笋干（Dried Bamboo Shoot）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> DRIED_BAMBOO_SHOOT = ITEMS.registerItem(
            "dried_bamboo_shoot",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    /** 腌菜（Pickled Vegetable）：2 饥饿 / 0.3 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> PICKLED_VEGETABLE = ITEMS.registerItem(
            "pickled_vegetable",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.30F)
                        .build()));

    // ==================================================================
    // 厨具与餐具
    // ==================================================================

    /** 菜刀（Kitchen Knife），耐久 250。 */
    public static final DeferredItem<Item> KITCHEN_KNIFE = ITEMS.registerItem(
            "kitchen_knife",
            Item::new,
            props -> props.durability(250));

    /** 砍刀（Cleaver），耐久 400。 */
    public static final DeferredItem<Item> CLEAVER = ITEMS.registerItem(
            "cleaver",
            Item::new,
            props -> props.durability(400));

    /** 铲子（Spatula），耐久 250。 */
    public static final DeferredItem<Item> SPATULA = ITEMS.registerItem(
            "spatula",
            Item::new,
            props -> props.durability(250));

    /** 漏勺（Slotted Spoon），耐久 200。 */
    public static final DeferredItem<Item> SLOTTED_SPOON = ITEMS.registerItem(
            "slotted_spoon",
            Item::new,
            props -> props.durability(200));

    /** 汤勺（Soup Spoon），耐久 200。 */
    public static final DeferredItem<Item> SOUP_SPOON = ITEMS.registerItem(
            "soup_spoon",
            Item::new,
            props -> props.durability(200));

    /** 擀面杖（Rolling Pin），耐久 150。 */
    public static final DeferredItem<Item> ROLLING_PIN = ITEMS.registerItem(
            "rolling_pin",
            Item::new,
            props -> props.durability(150));

    /** 筷子（Chopsticks）。 */
    public static final DeferredItem<Item> CHOPSTICKS = ITEMS.registerSimpleItem("chopsticks");

    /** 碟子（Saucer）。 */
    public static final DeferredItem<Item> SAUCER = ITEMS.registerSimpleItem("saucer");

    /** 杯子（Cup）。 */
    public static final DeferredItem<Item> CUP = ITEMS.registerSimpleItem("cup");

    // ==================================================================
    // 鲁菜 —— 八大菜系（10 道）
    // ==================================================================

    /** 九转大肠（Braised Pork Intestines）：8 饥饿 / 1.0 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> JIUZHUAN_DACHANG = ITEMS.registerItem(
            "jiuzhuan_dachang",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 葱烧海参（Braised Sea Cucumber）：7 饥饿 / 1.2 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> CONGSAO_HAISHEN = ITEMS.registerItem(
            "congsao_haishen",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.20F)
                        .build()));

    /** 糖醋鲤鱼（Sweet and Sour Carp）：8 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> TANGCU_LIYU = ITEMS.registerItem(
            "tangcu_liyu",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 油爆双脆（Stir-fried Giblets）：7 饥饿 / 0.9 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> YOUBAO_SHUANGCUI = ITEMS.registerItem(
            "youbao_shuangcui",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 锅塌豆腐（Pan-fried Tofu）：6 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> GUOTA_DOUFU = ITEMS.registerItem(
            "guota_doufu",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 奶汤蒲菜（Milk Soup with Cattail）：5 饥饿 / 1.0 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> NAITANG_PUCAI = ITEMS.registerItem(
            "naitang_pucai",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(1.00F)
                        .build()));

    /** 德州扒鸡（Dezhou Braised Chicken）：9 饥饿 / 1.0 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> DEZHOU_PAJI = ITEMS.registerItem(
            "dezhou_paji",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.00F)
                        .build()));

    /** 四喜丸子（Four Joy Meatballs）：8 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> SIXI_WANZI = ITEMS.registerItem(
            "sixi_wanzi",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    /** 糟溜鱼片（Fish Slices in Wine Sauce）：7 饥饿 / 0.9 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> ZAOLIU_YUPIAN = ITEMS.registerItem(
            "zaoliu_yupian",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 孔府一品锅（Kong Family Pot）：10 饥饿 / 1.2 饱和，效果 NOURISH_WARMTH。 */
    public static final DeferredItem<DishItem> KONGFU_YIPINGUO = ITEMS.registerItem(
            "kongfu_yipinguo",
            props -> new DishItem(props, DishEffects.NOURISH_WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(10)
                        .saturationModifier(1.20F)
                        .build()));

    // ==================================================================
    // 川菜 —— 八大菜系（10 道）
    // ==================================================================

    /** 麻婆豆腐（Mapo Tofu）：7 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> MAPO_TOFU = ITEMS.registerItem(
            "mapo_tofu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.00F)
                        .build()));

    /** 回锅肉（Twice-cooked Pork）：9 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> HUIGUO_ROU = ITEMS.registerItem(
            "huiguo_rou",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 水煮鱼（Boiled Fish in Chili Oil）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> SHUIZHU_YU = ITEMS.registerItem(
            "shuizhu_yu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 夫妻肺片（Sliced Beef in Chili Sauce）：6 饥饿 / 0.9 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> FUQI_FEIPIAN = ITEMS.registerItem(
            "fuqi_feipian",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 宫保鸡丁（Kung Pao Chicken）：8 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> GONGBAO_JIDING = ITEMS.registerItem(
            "gongbao_jiding",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    /** 鱼香肉丝（Yuxiang Shredded Pork）：8 饥饿 / 1.0 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> YUXIANG_ROUSI = ITEMS.registerItem(
            "yuxiang_rousi",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 毛血旺（Mao Xue Wang）：9 饥饿 / 1.0 饱和，效果 REFRESH_NOURISH。 */
    public static final DeferredItem<DishItem> MAOXUE_WANG = ITEMS.registerItem(
            "maoxue_wang",
            props -> new DishItem(props, DishEffects.REFRESH_NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.00F)
                        .build()));

    /** 辣子鸡（Spicy Chicken）：8 饥饿 / 0.9 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> LAZIJI = ITEMS.registerItem(
            "laziji",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(0.90F)
                        .build()));

    /** 东坡肘子（Dongpo Pork Hock）：10 饥饿 / 1.2 饱和，效果 NOURISH_SATED。 */
    public static final DeferredItem<DishItem> DONGPO_ZHOUZI = ITEMS.registerItem(
            "dongpo_zhouzi",
            props -> new DishItem(props, DishEffects.NOURISH_SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(10)
                        .saturationModifier(1.20F)
                        .build()));

    /** 开水白菜（Cabbage in Clear Broth）：4 饥饿 / 1.4 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> KAISHUI_BAICAI = ITEMS.registerItem(
            "kaishui_baicai",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(1.40F)
                        .build()));

    // ==================================================================
    // 粤菜 —— 八大菜系（10 道）
    // ==================================================================

    /** 白切鸡（Poached Chicken）：8 饥饿 / 1.0 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> BAIQIE_JI = ITEMS.registerItem(
            "baiqie_ji",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 蜜汁叉烧（Honey Char Siu）：9 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> MIZHI_CHASHAO = ITEMS.registerItem(
            "mizhi_chashao",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 清蒸石斑鱼（Steamed Grouper）：7 饥饿 / 1.2 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> QINGZHENG_SHIBANYU = ITEMS.registerItem(
            "qingzheng_shibanyu",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.20F)
                        .build()));

    /** 老火靓汤（Slow-simmered Soup）：6 饥饿 / 1.4 饱和，效果 NOURISH_WARMTH。 */
    public static final DeferredItem<DishItem> LAOHUO_LIANGTANG = ITEMS.registerItem(
            "laohuo_liangtang",
            props -> new DishItem(props, DishEffects.NOURISH_WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(1.40F)
                        .build()));

    /** 烧鹅（Roast Goose）：9 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> SHAOE = ITEMS.registerItem(
            "shaoe",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 虾饺皇（Shrimp Dumplings）：5 饥饿 / 1.2 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> XIAJIAO_HUANG = ITEMS.registerItem(
            "xiajiao_huang",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(1.20F)
                        .build()));

    /** 干炒牛河（Beef Chow Fun）：9 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> GANCHAO_NIUHE = ITEMS.registerItem(
            "ganchao_niuhe",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.00F)
                        .build()));

    /** 鲍汁扣辽参（Abalone Sauce Sea Cucumber）：7 饥饿 / 1.3 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> BAOZHI_LIAOSHEN = ITEMS.registerItem(
            "baozhi_liaoshen",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.30F)
                        .build()));

    /** 啫啫煲（Sizzling Clay Pot）：8 饥饿 / 1.0 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> ZEZE_BAO = ITEMS.registerItem(
            "zeze_bao",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 云吞面（Wonton Noodles）：8 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> YUNTUN_MIAN = ITEMS.registerItem(
            "yuntun_mian",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    // ==================================================================
    // 苏菜 —— 八大菜系（10 道）
    // ==================================================================

    /** 松鼠鳜鱼（Squirrel Mandarin Fish）：8 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> SONGSHU_GUIYU = ITEMS.registerItem(
            "songshu_guiyu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    /** 阳澄湖大闸蟹（Hairy Crab）：7 饥饿 / 1.2 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> DAZHAXIE = ITEMS.registerItem(
            "dazhaxie",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.20F)
                        .build()));

    /** 扬州狮子头（Yangzhou Lion's Head）：9 饥饿 / 1.1 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> YANGZHOU_SHIZITOU = ITEMS.registerItem(
            "yangzhou_shizitou",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 金陵盐水鸭（Nanjing Salted Duck）：8 饥饿 / 1.0 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> JINLING_YANSHUIYA = ITEMS.registerItem(
            "jinling_yanshuiya",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 大煮干丝（Braised Shredded Tofu）：5 饥饿 / 1.0 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> DAZHU_GANSI = ITEMS.registerItem(
            "dazhu_gansi",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(1.00F)
                        .build()));

    /** 无锡酱排骨（Wuxi Braised Ribs）：9 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> WUXI_JIANGPAIGU = ITEMS.registerItem(
            "wuxi_jiangpaigu",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 清蒸鲥鱼（Steamed Hilsa Herring）：7 饥饿 / 1.2 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> QINGZHENG_SHIYU = ITEMS.registerItem(
            "qingzheng_shiyu",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.20F)
                        .build()));

    /** 水晶肴肉（Crystal Pork Terrine）：6 饥饿 / 0.9 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> SHUIJING_YAOROU = ITEMS.registerItem(
            "shuijing_yaorou",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 碧螺虾仁（Biluoshun Shrimp）：6 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> BILUO_XIAREN = ITEMS.registerItem(
            "biluo_xiaren",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(1.10F)
                        .build()));

    /** 文思豆腐（Wensi Tofu Soup）：5 饥饿 / 1.3 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> WENSI_DOUFU = ITEMS.registerItem(
            "wensi_doufu",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(1.30F)
                        .build()));

    // ==================================================================
    // 闽菜 —— 八大菜系（8 道）
    // ==================================================================

    /** 佛跳墙（Buddha Jumps Over the Wall）：10 饥饿 / 1.4 饱和，效果 FEAST。 */
    public static final DeferredItem<DishItem> FOTIAOQIANG = ITEMS.registerItem(
            "fotiaoqiang",
            props -> new DishItem(props, DishEffects.FEAST),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(10)
                        .saturationModifier(1.40F)
                        .build()));

    /** 荔枝肉（Lychee Pork）：8 饥饿 / 1.0 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> LIZHI_ROU = ITEMS.registerItem(
            "lizhi_rou",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 醉排骨（Drunken Ribs）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> ZUI_PAIGU = ITEMS.registerItem(
            "zui_paigu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 八宝红鲟饭（Eight Treasure Crab Rice）：9 饥饿 / 1.2 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> BABAO_HONGXUN_FAN = ITEMS.registerItem(
            "babao_hongxun_fan",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.20F)
                        .build()));

    /** 鸡汤氽海蚌（Clam in Chicken Broth）：7 饥饿 / 1.3 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> JITANG_TUN_HAIBANG = ITEMS.registerItem(
            "jitang_tun_haibang",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.30F)
                        .build()));

    /** 斩河田鸡（Hetian Chicken）：8 饥饿 / 1.0 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> ZHAN_HETIANJI = ITEMS.registerItem(
            "zhan_hetianji",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 武夷熏鹅（Wuyi Smoked Goose）：9 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> WUYI_XUNE = ITEMS.registerItem(
            "wuyi_xune",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.00F)
                        .build()));

    /** 香南日鲍（Braised Nanri Abalone）：7 饥饿 / 1.3 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> XIANGNAN_RIBAO = ITEMS.registerItem(
            "xiangnan_ribao",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.30F)
                        .build()));

    // ==================================================================
    // 浙菜 —— 八大菜系（7 道）
    // ==================================================================

    /** 西湖醋鱼（West Lake Vinegar Fish）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> XIHU_CUYU = ITEMS.registerItem(
            "xihu_cuyu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 东坡肉（Dongpo Pork）：9 饥饿 / 1.2 饱和，效果 NOURISH_SATED。 */
    public static final DeferredItem<DishItem> DONGPO_ROU = ITEMS.registerItem(
            "dongpo_rou",
            props -> new DishItem(props, DishEffects.NOURISH_SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.20F)
                        .build()));

    /** 龙井虾仁（Longjing Shrimp）：6 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> LONGJING_XIAREN = ITEMS.registerItem(
            "longjing_xiaren",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(1.10F)
                        .build()));

    /** 雪菜大汤黄鱼（Yellow Croaker Soup）：7 饥饿 / 1.1 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> XUECAI_HUANGYU = ITEMS.registerItem(
            "xuecai_huangyu",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.10F)
                        .build()));

    /** 清汤越鸡（Clear Broth Chicken）：7 饥饿 / 1.3 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> QINGTANG_YUEJI = ITEMS.registerItem(
            "qingtang_yueji",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.30F)
                        .build()));

    /** 干菜焖肉（Braised Pork with Greens）：9 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> GANCAI_MENROU = ITEMS.registerItem(
            "gancai_menrou",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 五味煎蟹（Five-flavour Crab）：7 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> WUWEI_JIANXIE = ITEMS.registerItem(
            "wuwei_jianxie",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.10F)
                        .build()));

    // ==================================================================
    // 湘菜 —— 八大菜系（10 道）
    // ==================================================================

    /** 剁椒鱼头（Fish Head with Chopped Chili）：8 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> DUOJIAO_YUTOU = ITEMS.registerItem(
            "duojiao_yutou",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    /** 毛氏红烧肉（Mao's Braised Pork）：9 饥饿 / 1.2 饱和，效果 NOURISH_SATED。 */
    public static final DeferredItem<DishItem> MAOSHI_HONGSHAOROU = ITEMS.registerItem(
            "maoshi_hongshaorou",
            props -> new DishItem(props, DishEffects.NOURISH_SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.20F)
                        .build()));

    /** 辣椒炒肉（Pork with Green Chili）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> LAJIAO_CHAOROU = ITEMS.registerItem(
            "lajiao_chaorou",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 东安子鸡（Dongan Chicken）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> DONGAN_ZIJI = ITEMS.registerItem(
            "dongan_ziji",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 腊味合蒸（Steamed Cured Meats）：9 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> LAWEI_HEZHENG = ITEMS.registerItem(
            "lawei_hezheng",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 湘西外婆菜（Grandma's Pickles）：6 饥饿 / 0.9 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> XIANGXI_WAIPOCAI = ITEMS.registerItem(
            "xiangxi_waipocai",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 酱板鸭（Soy-braised Duck）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> JIANGBANYA = ITEMS.registerItem(
            "jiangbanya",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 永州血鸭（Yongzhou Blood Duck）：9 饥饿 / 1.1 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> YONGZHOU_XUEYA = ITEMS.registerItem(
            "yongzhou_xueya",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 组庵鱼翅（Zuan Shark Fin）：7 饥饿 / 1.4 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> ZUAN_YUCHI = ITEMS.registerItem(
            "zuan_yuchi",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.40F)
                        .build()));

    /** 猪血丸子（Pig Blood Meatball）：7 饥饿 / 0.9 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> ZHUXUE_WANZI = ITEMS.registerItem(
            "zhuxue_wanzi",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    // ==================================================================
    // 徽菜 —— 八大菜系（8 道）
    // ==================================================================

    /** 臭鳜鱼（Stinky Mandarin Fish）：8 饥饿 / 1.1 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> CHOU_GUIYU = ITEMS.registerItem(
            "chou_guiyu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    /** 徽州一品锅（Huizhou One-pot）：10 饥饿 / 1.3 饱和，效果 NOURISH_WARMTH。 */
    public static final DeferredItem<DishItem> HUIZHOU_YIPINGUO = ITEMS.registerItem(
            "huizhou_yipinguo",
            props -> new DishItem(props, DishEffects.NOURISH_WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(10)
                        .saturationModifier(1.30F)
                        .build()));

    /** 虎皮毛豆腐（Hairy Tofu）：6 饥饿 / 1.0 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> HUMAO_DOUFU = ITEMS.registerItem(
            "humao_doufu",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(1.00F)
                        .build()));

    /** 黄山炖鸽（Huangshan Pigeon Stew）：7 饥饿 / 1.3 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> HUANGSHAN_DUNGE = ITEMS.registerItem(
            "huangshan_dunge",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.30F)
                        .build()));

    /** 问政山笋（Wenzheng Bamboo Shoots）：5 饥饿 / 1.1 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> WENZHENG_SHANSUN = ITEMS.registerItem(
            "wenzheng_shansun",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(1.10F)
                        .build()));

    /** 方腊鱼（Fangla Fish）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> FANGLA_YU = ITEMS.registerItem(
            "fangla_yu",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 蜜汁红芋（Honeyed Sweet Potato）：6 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> MIZHI_HONGYU = ITEMS.registerItem(
            "mizhi_hongyu",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(1.00F)
                        .build()));

    /** 清蒸石鸡（Steamed Stone Frog）：7 饥饿 / 1.2 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> QINGZHENG_SHIJI = ITEMS.registerItem(
            "qingzheng_shiji",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.20F)
                        .build()));

    // ==================================================================
    // 春节 —— 传统节日（5 道）
    // ==================================================================

    /** 饺子（Dumplings）：6 饥饿 / 0.9 饱和，效果 REUNION。 */
    public static final DeferredItem<DishItem> JIAOZI = ITEMS.registerItem(
            "jiaozi",
            props -> new DishItem(props, DishEffects.REUNION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 年糕（Nian Gao）：6 饥饿 / 0.8 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> NIAN_GAO = ITEMS.registerItem(
            "nian_gao",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 春卷（Spring Rolls）：5 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CHUN_JUAN = ITEMS.registerItem(
            "chun_juan",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 汤圆（Tangyuan）：5 饥饿 / 0.8 饱和，效果 REUNION。 */
    public static final DeferredItem<DishItem> TANG_YUAN = ITEMS.registerItem(
            "tang_yuan",
            props -> new DishItem(props, DishEffects.REUNION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 腊肉（Cured Pork）：7 饥饿 / 0.9 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> LA_ROU = ITEMS.registerItem(
            "la_rou",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    // ==================================================================
    // 元宵 —— 传统节日（3 道）
    // ==================================================================

    /** 芝麻汤圆（Sesame Tangyuan）：6 饥饿 / 0.9 饱和，效果 REUNION。 */
    public static final DeferredItem<DishItem> ZHIMA_TANGYUAN = ITEMS.registerItem(
            "zhima_tangyuan",
            props -> new DishItem(props, DishEffects.REUNION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 豆沙汤圆（Red Bean Tangyuan）：6 饥饿 / 0.9 饱和，效果 REUNION。 */
    public static final DeferredItem<DishItem> DOUSHA_TANGYUAN = ITEMS.registerItem(
            "dousha_tangyuan",
            props -> new DishItem(props, DishEffects.REUNION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 花生汤圆（Peanut Tangyuan）：6 饥饿 / 0.9 饱和，效果 REUNION_SATED。 */
    public static final DeferredItem<DishItem> HUASHENG_TANGYUAN = ITEMS.registerItem(
            "huasheng_tangyuan",
            props -> new DishItem(props, DishEffects.REUNION_SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    // ==================================================================
    // 清明 —— 传统节日（2 道）
    // ==================================================================

    /** 青团（Qingtuan）：5 饥饿 / 0.8 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> QING_TUAN = ITEMS.registerItem(
            "qing_tuan",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 艾饺（Mugwort Dumplings）：5 饥饿 / 0.8 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> AI_JIAO = ITEMS.registerItem(
            "ai_jiao",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    // ==================================================================
    // 端午 —— 传统节日（3 道）
    // ==================================================================

    /** 肉粽（Meat Zongzi）：8 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> ROU_ZONG = ITEMS.registerItem(
            "rou_zong",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 枣粽（Date Zongzi）：7 饥饿 / 0.9 饱和，效果 REUNION。 */
    public static final DeferredItem<DishItem> ZAO_ZONG = ITEMS.registerItem(
            "zao_zong",
            props -> new DishItem(props, DishEffects.REUNION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 豆沙粽（Red Bean Zongzi）：7 饥饿 / 0.9 饱和，效果 REUNION。 */
    public static final DeferredItem<DishItem> DOUSHA_ZONG = ITEMS.registerItem(
            "dousha_zong",
            props -> new DishItem(props, DishEffects.REUNION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    // ==================================================================
    // 七夕 —— 传统节日（2 道）
    // ==================================================================

    /** 巧果（Qiaoguo）：4 饥饿 / 0.7 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> QIAO_GUO = ITEMS.registerItem(
            "qiao_guo",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.70F)
                        .build()));

    /** 巧芽面（Sprout Noodles）：7 饥饿 / 0.9 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> QIAOYA_MIAN = ITEMS.registerItem(
            "qiaoya_mian",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    // ==================================================================
    // 中秋 —— 传统节日（4 道）
    // ==================================================================

    /** 莲蓉月饼（Lotus Paste Mooncake）：7 饥饿 / 1.1 饱和，效果 PERFECTION。 */
    public static final DeferredItem<DishItem> LIANRONG_YUEBING = ITEMS.registerItem(
            "lianrong_yuebing",
            props -> new DishItem(props, DishEffects.PERFECTION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.10F)
                        .build()));

    /** 豆沙月饼（Red Bean Mooncake）：7 饥饿 / 1.0 饱和，效果 PERFECTION。 */
    public static final DeferredItem<DishItem> DOUSHA_YUEBING = ITEMS.registerItem(
            "dousha_yuebing",
            props -> new DishItem(props, DishEffects.PERFECTION),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.00F)
                        .build()));

    /** 五仁月饼（Five Kernel Mooncake）：8 饥饿 / 1.1 饱和，效果 PERFECTION_NOURISH。 */
    public static final DeferredItem<DishItem> WUREN_YUEBING = ITEMS.registerItem(
            "wuren_yuebing",
            props -> new DishItem(props, DishEffects.PERFECTION_NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    /** 蛋黄月饼（Salted Yolk Mooncake）：8 饥饿 / 1.1 饱和，效果 PERFECTION_SATED。 */
    public static final DeferredItem<DishItem> DANYUE_YUEBING = ITEMS.registerItem(
            "danyue_yuebing",
            props -> new DishItem(props, DishEffects.PERFECTION_SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    // ==================================================================
    // 重阳 —— 传统节日（2 道）
    // ==================================================================

    /** 重阳糕（Chongyang Cake）：6 饥饿 / 0.9 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> CHONGYANG_GAO = ITEMS.registerItem(
            "chongyang_gao",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 菊花酒（Chrysanthemum Wine）：0 饥饿 / 0.0 饱和，效果 WARMTH_REFRESH。 */
    public static final DeferredItem<DishItem> JUHUA_JIU = ITEMS.registerItem(
            "juhua_jiu",
            props -> new DishItem(props, DishEffects.WARMTH_REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(0)
                        .saturationModifier(0.00F)
                        .alwaysEdible()
                        .build()));

    // ==================================================================
    // 腊八 —— 传统节日（2 道）
    // ==================================================================

    /** 腊八粥（Laba Porridge）：7 饥饿 / 1.2 饱和，效果 NOURISH_WARMTH。 */
    public static final DeferredItem<DishItem> LABA_ZHOU = ITEMS.registerItem(
            "laba_zhou",
            props -> new DishItem(props, DishEffects.NOURISH_WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.20F)
                        .build()));

    /** 腊八蒜（Laba Garlic）：2 饥饿 / 0.4 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> LABA_SUAN = ITEMS.registerItem(
            "laba_suan",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(2)
                        .saturationModifier(0.40F)
                        .build()));

    // ==================================================================
    // 冬至 —— 传统节日（1 道）
    // ==================================================================

    /** 羊肉汤（Mutton Soup）：8 饥饿 / 1.3 饱和，效果 WARMTH_NOURISH。 */
    public static final DeferredItem<DishItem> YANGROU_TANG = ITEMS.registerItem(
            "yangrou_tang",
            props -> new DishItem(props, DishEffects.WARMTH_NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.30F)
                        .build()));

    // ==================================================================
    // 早餐 —— 早餐（18 道）
    // ==================================================================

    /** 馒头（Steamed Bun）：5 饥饿 / 0.7 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> MANTOU = ITEMS.registerItem(
            "mantou",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.70F)
                        .build()));

    /** 花卷（Steamed Twisted Roll）：6 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> HUA_JUAN = ITEMS.registerItem(
            "hua_juan",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 包子（Steamed Stuffed Bun）：7 饥饿 / 0.9 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> BAOZI = ITEMS.registerItem(
            "baozi",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 小笼包（Soup Dumpling）：6 饥饿 / 0.9 饱和，效果 SATED_REFRESH。 */
    public static final DeferredItem<DishItem> XIAO_LONG_BAO = ITEMS.registerItem(
            "xiao_long_bao",
            props -> new DishItem(props, DishEffects.SATED_REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 豆沙包（Red Bean Bun）：6 饥饿 / 0.9 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> DOU_SHA_BAO = ITEMS.registerItem(
            "dou_sha_bao",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 油条（Fried Dough Stick）：6 饥饿 / 0.8 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> YOUTIAO = ITEMS.registerItem(
            "youtiao",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 豆浆（Soy Milk）：4 饥饿 / 0.6 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> DOUJIANG = ITEMS.registerItem(
            "doujiang",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.60F)
                        .build()));

    /** 豆浆油条（Soy Milk and Fried Dough）：9 饥饿 / 1.1 饱和，效果 CRISP_REFRESH。 */
    public static final DeferredItem<DishItem> YOUTIAO_DOUJIANG = ITEMS.registerItem(
            "youtiao_doujiang",
            props -> new DishItem(props, DishEffects.CRISP_REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.10F)
                        .build()));

    /** 炒肝（Stir-fried Liver）：6 饥饿 / 0.9 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> CHAO_GAN = ITEMS.registerItem(
            "chao_gan",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 馄饨（Wonton）：7 饥饿 / 1.1 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> HUNTUN = ITEMS.registerItem(
            "huntun",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.10F)
                        .build()));

    /** 馄饨汤（Wonton Soup）：8 饥饿 / 1.2 饱和，效果 WARMTH_NOURISH。 */
    public static final DeferredItem<DishItem> WONTON_SOUP = ITEMS.registerItem(
            "wonton_soup",
            props -> new DishItem(props, DishEffects.WARMTH_NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.20F)
                        .build()));

    /** 小米粥（Millet Porridge）：5 饥饿 / 0.9 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> XIAOMI_ZHOU = ITEMS.registerItem(
            "xiaomi_zhou",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.90F)
                        .build()));

    /** 白粥（Plain Rice Porridge）：4 饥饿 / 0.7 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> ZHOU_CONGEE = ITEMS.registerItem(
            "zhou_congee",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.70F)
                        .build()));

    /** 煎饼果子（Jianbing）：9 饥饿 / 1.2 饱和，效果 SATED_REFRESH。 */
    public static final DeferredItem<DishItem> JIANBING = ITEMS.registerItem(
            "jianbing",
            props -> new DishItem(props, DishEffects.SATED_REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.20F)
                        .build()));

    /** 叉烧包（BBQ Pork Bun）：7 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> CHASHAO_BAO = ITEMS.registerItem(
            "chashao_bao",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.00F)
                        .build()));

    /** 汤圆（Glutinous Rice Ball）：5 饥饿 / 0.9 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> TANGYUAN = ITEMS.registerItem(
            "tangyuan",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.90F)
                        .build()));

    /** 米线（Rice Noodles）：7 饥饿 / 1.1 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> MIXIAN = ITEMS.registerItem(
            "mixian",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(1.10F)
                        .build()));

    /** 炒面（Fried Noodles）：8 饥饿 / 1.1 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> CHAO_MIAN = ITEMS.registerItem(
            "chao_mian",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.10F)
                        .build()));

    // ==================================================================
    // 特色小吃 —— 特色小吃（31 道）
    // ==================================================================

    /** 臭豆腐（Stinky Tofu）：5 饥饿 / 0.7 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> CHOU_DOUFU = ITEMS.registerItem(
            "chou_doufu",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.70F)
                        .build()));

    /** 烤冷面（Grilled Cold Noodles）：7 饥饿 / 0.9 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> KAO_LENGMIAN = ITEMS.registerItem(
            "kao_lengmian",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 串串香（Chuanchuan Skewers）：6 饥饿 / 0.8 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> CHUAN_CHUAN = ITEMS.registerItem(
            "chuan_chuan",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 肉夹馍（Roujiamo）：9 饥饿 / 1.2 饱和，效果 SATED_NOURISH。 */
    public static final DeferredItem<DishItem> ROUJIAMO = ITEMS.registerItem(
            "roujiamo",
            props -> new DishItem(props, DishEffects.SATED_NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(9)
                        .saturationModifier(1.20F)
                        .build()));

    /** 煎糕（Pan-fried Cake）：6 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> JIAN_GAO = ITEMS.registerItem(
            "jian_gao",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 锅贴（Pot Stickers）：7 饥饿 / 0.9 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> GUO_TIE = ITEMS.registerItem(
            "guo_tie",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 烧卖（Siu Mai）：7 饥饿 / 0.9 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> SHAOMAI = ITEMS.registerItem(
            "shaomai",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 凉皮（Cold Skin Noodles）：6 饥饿 / 0.8 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> LIANGPI = ITEMS.registerItem(
            "liangpi",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 川北凉粉（Sichuan Bean Jelly）：6 饥饿 / 0.8 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> CHUANBEI_LIANGFEN = ITEMS.registerItem(
            "chuanbei_liangfen",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 糖葫芦（Candied Hawthorn）：4 饥饿 / 0.6 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> TANGHULU = ITEMS.registerItem(
            "tanghulu",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.60F)
                        .build()));

    /** 麻花（Fried Dough Twist）：5 饥饿 / 0.7 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> MAHUADOU = ITEMS.registerItem(
            "mahuadou",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.70F)
                        .build()));

    /** 烧饼（Baked Flatbread）：6 饥饿 / 0.8 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> SHAO_BING = ITEMS.registerItem(
            "shao_bing",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 芝麻团（Sesame Ball）：5 饥饿 / 0.7 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> ZHIMA_TUAN = ITEMS.registerItem(
            "zhima_tuan",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.70F)
                        .build()));

    /** 咸肉粽（Savoury Zongzi）：8 饥饿 / 1.0 饱和，效果 SATED。 */
    public static final DeferredItem<DishItem> ZONGZI_XIAN = ITEMS.registerItem(
            "zongzi_xian",
            props -> new DishItem(props, DishEffects.SATED),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 年糕片（Sliced Rice Cake）：5 饥饿 / 0.7 饱和，效果 RISE_UP。 */
    public static final DeferredItem<DishItem> RICE_CAKE = ITEMS.registerItem(
            "rice_cake",
            props -> new DishItem(props, DishEffects.RISE_UP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.70F)
                        .build()));

    /** 蒸南瓜（Steamed Pumpkin）：5 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> STEAMED_PUMPKIN = ITEMS.registerItem(
            "steamed_pumpkin",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 豆腐脑（Tofu Pudding）：5 饥饿 / 0.8 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> DOUFUNAO = ITEMS.registerItem(
            "doufunao",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 酸汤（Sour Soup）：5 饥饿 / 0.8 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> SUANTANG = ITEMS.registerItem(
            "suantang",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 蛋花汤（Egg Drop Soup）：5 饥饿 / 0.8 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> EGG_DROP_SOUP = ITEMS.registerItem(
            "egg_drop_soup",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 西红柿炒蛋（Tomato and Egg）：7 饥饿 / 0.9 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> TOMATO_EGG = ITEMS.registerItem(
            "tomato_egg",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 炒蛋（Scrambled Egg）：5 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> SCRAMBLED_EGG = ITEMS.registerItem(
            "scrambled_egg",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.80F)
                        .build()));

    /** 韭黄炒蛋（Chive and Egg）：7 饥饿 / 0.9 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> CHIVE_EGG = ITEMS.registerItem(
            "chive_egg",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(7)
                        .saturationModifier(0.90F)
                        .build()));

    /** 干煸豆角（Dry-fried Green Beans）：6 饥饿 / 0.8 饱和，效果 CRISP。 */
    public static final DeferredItem<DishItem> DRY_FRIED_BEANS = ITEMS.registerItem(
            "dry_fried_beans",
            props -> new DishItem(props, DishEffects.CRISP),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 清炒豌豆（Stir-fried Peas）：6 饥饿 / 0.8 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> STIR_FRIED_PEA = ITEMS.registerItem(
            "stir_fried_pea",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.80F)
                        .build()));

    /** 油焖笋（Braised Bamboo Shoots）：6 饥饿 / 0.9 饱和，效果 NONE。 */
    public static final DeferredItem<DishItem> BRAISED_BAMBOO = ITEMS.registerItem(
            "braised_bamboo",
            props -> new DishItem(props, DishEffects.NONE),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(6)
                        .saturationModifier(0.90F)
                        .build()));

    /** 回锅肉片（Twice-cooked Pork Slices）：8 饥饿 / 1.0 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> TWICE_COOKED_PORK = ITEMS.registerItem(
            "twice_cooked_pork",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.00F)
                        .build()));

    /** 红豆汤（Red Bean Soup）：5 饥饿 / 0.9 饱和，效果 WARMTH。 */
    public static final DeferredItem<DishItem> RED_BEAN_SOUP = ITEMS.registerItem(
            "red_bean_soup",
            props -> new DishItem(props, DishEffects.WARMTH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.90F)
                        .build()));

    /** 绿豆汤（Mung Bean Soup）：5 饥饿 / 0.9 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> MUNG_BEAN_SOUP = ITEMS.registerItem(
            "mung_bean_soup",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.90F)
                        .build()));

    /** 冬瓜汤（Winter Melon Soup）：4 饥饿 / 0.7 饱和，效果 REFRESH。 */
    public static final DeferredItem<DishItem> WINTER_MELON_SOUP = ITEMS.registerItem(
            "winter_melon_soup",
            props -> new DishItem(props, DishEffects.REFRESH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(4)
                        .saturationModifier(0.70F)
                        .build()));

    /** 莲子羹（Lotus Seed Soup）：5 饥饿 / 0.9 饱和，效果 NOURISH。 */
    public static final DeferredItem<DishItem> LOTUS_SEED_SOUP = ITEMS.registerItem(
            "lotus_seed_soup",
            props -> new DishItem(props, DishEffects.NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(5)
                        .saturationModifier(0.90F)
                        .build()));

    /** 山药排骨汤（Yam and Rib Soup）：8 饥饿 / 1.2 饱和，效果 WARMTH_NOURISH。 */
    public static final DeferredItem<DishItem> YAM_RIBS_SOUP = ITEMS.registerItem(
            "yam_ribs_soup",
            props -> new DishItem(props, DishEffects.WARMTH_NOURISH),
            props -> props.food(new FoodProperties.Builder()
                        .nutrition(8)
                        .saturationModifier(1.20F)
                        .build()));

    // ==================================================================
    // 汇总：所有可食用 / 可摆盘的物品
    // ==================================================================

    private static final List<DeferredItem<? extends Item>> ALL_FOODS = List.of(
            RICE,
            GLUTINOUS_RICE,
            MILLET,
            SORGHUM,
            CORN,
            RED_BEAN,
            MUNG_BEAN,
            SOYBEAN,
            BLACK_BEAN,
            PEA,
            BROAD_BEAN,
            BEAN_PASTE,
            DOU_YA,
            SWEET_POTATO,
            BAKED_SWEET_POTATO,
            CHINESE_YAM,
            TARO,
            TOFU,
            PEANUT,
            SESAME,
            LOTUS_SEED,
            GOJI_BERRY,
            RED_DATE,
            DRIED_JUJUBE,
            LONGAN,
            LYCHEE,
            SHREDDED_VEGETABLE,
            SHREDDED_MEAT,
            FISH_FILLET,
            SHREDDED_TOFU,
            ROCK_SUGAR,
            FERMENTED_TOFU,
            DOUCHI,
            STOCK,
            PEAR,
            PEACH,
            PLUM,
            APRICOT,
            JUJUBE,
            PERSIMMON,
            MANDARIN,
            POMELO,
            BANANA,
            GRAPE,
            STRAWBERRY,
            CHERRY,
            POMEGRANATE,
            KIWI,
            MANGO,
            PINEAPPLE,
            NAPA_CABBAGE,
            BOK_CHOY,
            RADISH,
            SPINACH,
            CELERY,
            CHIVE,
            EGGPLANT,
            CUCUMBER,
            WINTER_MELON,
            LUFFA,
            BITTER_MELON,
            GREEN_BEAN,
            TOMATO,
            CHILI,
            SCALLION,
            GINGER,
            GARLIC,
            GARLIC_SPROUT,
            CILANTRO,
            WOOD_EAR,
            BAMBOO_SHOOT,
            DRIED_BAMBOO_SHOOT,
            PICKLED_VEGETABLE,
            JIUZHUAN_DACHANG,
            CONGSAO_HAISHEN,
            TANGCU_LIYU,
            YOUBAO_SHUANGCUI,
            GUOTA_DOUFU,
            NAITANG_PUCAI,
            DEZHOU_PAJI,
            SIXI_WANZI,
            ZAOLIU_YUPIAN,
            KONGFU_YIPINGUO,
            MAPO_TOFU,
            HUIGUO_ROU,
            SHUIZHU_YU,
            FUQI_FEIPIAN,
            GONGBAO_JIDING,
            YUXIANG_ROUSI,
            MAOXUE_WANG,
            LAZIJI,
            DONGPO_ZHOUZI,
            KAISHUI_BAICAI,
            BAIQIE_JI,
            MIZHI_CHASHAO,
            QINGZHENG_SHIBANYU,
            LAOHUO_LIANGTANG,
            SHAOE,
            XIAJIAO_HUANG,
            GANCHAO_NIUHE,
            BAOZHI_LIAOSHEN,
            ZEZE_BAO,
            YUNTUN_MIAN,
            SONGSHU_GUIYU,
            DAZHAXIE,
            YANGZHOU_SHIZITOU,
            JINLING_YANSHUIYA,
            DAZHU_GANSI,
            WUXI_JIANGPAIGU,
            QINGZHENG_SHIYU,
            SHUIJING_YAOROU,
            BILUO_XIAREN,
            WENSI_DOUFU,
            FOTIAOQIANG,
            LIZHI_ROU,
            ZUI_PAIGU,
            BABAO_HONGXUN_FAN,
            JITANG_TUN_HAIBANG,
            ZHAN_HETIANJI,
            WUYI_XUNE,
            XIANGNAN_RIBAO,
            XIHU_CUYU,
            DONGPO_ROU,
            LONGJING_XIAREN,
            XUECAI_HUANGYU,
            QINGTANG_YUEJI,
            GANCAI_MENROU,
            WUWEI_JIANXIE,
            DUOJIAO_YUTOU,
            MAOSHI_HONGSHAOROU,
            LAJIAO_CHAOROU,
            DONGAN_ZIJI,
            LAWEI_HEZHENG,
            XIANGXI_WAIPOCAI,
            JIANGBANYA,
            YONGZHOU_XUEYA,
            ZUAN_YUCHI,
            ZHUXUE_WANZI,
            CHOU_GUIYU,
            HUIZHOU_YIPINGUO,
            HUMAO_DOUFU,
            HUANGSHAN_DUNGE,
            WENZHENG_SHANSUN,
            FANGLA_YU,
            MIZHI_HONGYU,
            QINGZHENG_SHIJI,
            JIAOZI,
            NIAN_GAO,
            CHUN_JUAN,
            TANG_YUAN,
            LA_ROU,
            ZHIMA_TANGYUAN,
            DOUSHA_TANGYUAN,
            HUASHENG_TANGYUAN,
            QING_TUAN,
            AI_JIAO,
            ROU_ZONG,
            ZAO_ZONG,
            DOUSHA_ZONG,
            QIAO_GUO,
            QIAOYA_MIAN,
            LIANRONG_YUEBING,
            DOUSHA_YUEBING,
            WUREN_YUEBING,
            DANYUE_YUEBING,
            CHONGYANG_GAO,
            JUHUA_JIU,
            LABA_ZHOU,
            LABA_SUAN,
            YANGROU_TANG,
            MANTOU,
            HUA_JUAN,
            BAOZI,
            XIAO_LONG_BAO,
            DOU_SHA_BAO,
            YOUTIAO,
            DOUJIANG,
            YOUTIAO_DOUJIANG,
            CHAO_GAN,
            HUNTUN,
            WONTON_SOUP,
            XIAOMI_ZHOU,
            ZHOU_CONGEE,
            JIANBING,
            CHASHAO_BAO,
            TANGYUAN,
            MIXIAN,
            CHAO_MIAN,
            CHOU_DOUFU,
            KAO_LENGMIAN,
            CHUAN_CHUAN,
            ROUJIAMO,
            JIAN_GAO,
            GUO_TIE,
            SHAOMAI,
            LIANGPI,
            CHUANBEI_LIANGFEN,
            TANGHULU,
            MAHUADOU,
            SHAO_BING,
            ZHIMA_TUAN,
            ZONGZI_XIAN,
            RICE_CAKE,
            STEAMED_PUMPKIN,
            DOUFUNAO,
            SUANTANG,
            EGG_DROP_SOUP,
            TOMATO_EGG,
            SCRAMBLED_EGG,
            CHIVE_EGG,
            DRY_FRIED_BEANS,
            STIR_FRIED_PEA,
            BRAISED_BAMBOO,
            TWICE_COOKED_PORK,
            RED_BEAN_SOUP,
            MUNG_BEAN_SOUP,
            WINTER_MELON_SOUP,
            LOTUS_SEED_SOUP,
            YAM_RIBS_SOUP
    );

    public static void register(IEventBus modBus) {
        ITEMS.register(modBus);
    }

    /** 生成器写出的所有餐食类物品（菜品 + 可直接摆盘的食材），供创造标签页使用。 */
    public static List<DeferredItem<? extends Item>> allFoods() {
        return ALL_FOODS;
    }

    private ModItems() {}
}
