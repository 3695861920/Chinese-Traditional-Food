package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.CuttingBoardBlock;
import com.ctf.chinese_traditional_food.common.block.ElectricMillBlock;
import com.ctf.chinese_traditional_food.common.block.ElectricShellerBlock;
import com.ctf.chinese_traditional_food.common.block.FurnaceGeneratorBlock;
import com.ctf.chinese_traditional_food.common.block.LargeElectricMillBlock;
import com.ctf.chinese_traditional_food.common.block.LargeElectricShellerBlock;
import com.ctf.chinese_traditional_food.common.block.LargeFurnaceGeneratorBlock;
import com.ctf.chinese_traditional_food.common.block.PlacedDishBlock;
import com.ctf.chinese_traditional_food.common.block.PlateBlock;
import com.ctf.chinese_traditional_food.common.block.RiceCropBlock;
import com.ctf.chinese_traditional_food.common.block.SoupPotBlock;
import com.ctf.chinese_traditional_food.common.block.SteamerBlock;
import com.ctf.chinese_traditional_food.common.block.StoveBlock;
import com.ctf.chinese_traditional_food.common.block.WokBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 方块注册表。
 *
 * <p>共 7 个方块：</p>
 * <ul>
 *   <li>餐盘 —— 把菜摆出来（1 份）；</li>
 *   <li>案板 —— 放上食材后用刀切；</li>
 *   <li>熔炉发电机 —— 烧燃料发电，给下面几台设备供电；</li>
 *   <li>电动磨粉机 —— 吃电，把谷物磨成粉；</li>
 *   <li>电动脱壳机 —— 吃电，给谷物脱壳；</li>
 *   <li>摆在地上的菜。</li>
 * </ul>
 *
 * <p>机器全部是<b>单方块</b>，靠 {@code Capabilities.Energy.BLOCK} 互相连电 ——
 * 比多方块结构好放、好搬、好接线。</p>
 */
public final class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(ChineseTraditionalFood.MOD_ID);

    /**
     * 餐盘：摆放 <b>1 份</b>菜。
     *
     * <ul>
     *   <li>强度 0.4（徒手两下敲碎），木质音效；</li>
     *   <li>{@code noOcclusion()} —— 盘子很薄，别挡住邻居的贴面剔除；</li>
     *   <li>贴图带透明通道，模型里用 {@code "render_type": "cutout"}。</li>
     * </ul>
     */
    public static final DeferredBlock<PlateBlock> PLATE = BLOCKS.registerBlock(
            "plate",
            PlateBlock::new,
            props -> props
                    .strength(0.4F)
                    .sound(SoundType.WOOD)
                    .noOcclusion());

    /**
     * 大拼盘：2×2 摆放 <b>4 份</b>菜，用来"摆一桌菜"。
     */
    /**
     * 案板：放上食材后用刀切。厚度 1 格，带方块实体。
     */
    public static final DeferredBlock<CuttingBoardBlock> CUTTING_BOARD = BLOCKS.registerBlock(
            "cutting_board",
            CuttingBoardBlock::new,
            props -> props
                    .strength(0.8F)
                    .sound(SoundType.WOOD)
                    .noOcclusion());

    /**
     * 熔炉发电机：单方块电源。烧原版燃料，六个面往外送电。
     */
    public static final DeferredBlock<FurnaceGeneratorBlock> FURNACE_GENERATOR =
            BLOCKS.registerBlock(
                    "furnace_generator",
                    FurnaceGeneratorBlock::new,
                    props -> props
                            .strength(3.5F, 6.0F)
                            .sound(SoundType.STONE)
                            .noOcclusion()
                            .requiresCorrectToolForDrops());

    /** 电动磨粉机：单方块，吃电把谷物磨成粉。 */
    public static final DeferredBlock<ElectricMillBlock> ELECTRIC_MILL =
            BLOCKS.registerBlock(
                    "electric_mill",
                    ElectricMillBlock::new,
                    props -> props
                            .strength(3.5F, 6.0F)
                            .sound(SoundType.STONE)
                            .noOcclusion()
                            .requiresCorrectToolForDrops());

    /** 电动脱壳机：单方块，吃电给谷物脱壳。 */
    public static final DeferredBlock<ElectricShellerBlock> ELECTRIC_SHELLER =
            BLOCKS.registerBlock(
                    "electric_sheller",
                    ElectricShellerBlock::new,
                    props -> props
                            .strength(3.5F, 6.0F)
                            .sound(SoundType.METAL)
                            .noOcclusion()
                            .requiresCorrectToolForDrops());

    // ==================================================================
    // 大型机（“3×3 放大版”）
    // ==================================================================
    //
    // 定位：仍是**单方块**（好放、好搬、好接线），但造型铺满整格、没有腿部留空，
    // 数值上批次 ×4、速度快 3.3 倍、单位耗电降到约三成。
    //
    // 为什么不真的做 3×3 多方块：早先试过 3×3×3 一体成型的多方块，
    // 放一次要占 9 格、搬运时得整台拆掉、交互还要从部件转发到核心 ——
    // 体验反而差。所以“放大”落在**造型与数值**上，而不是占地。

    /** 大型熔炉发电机：200 FE/t、缓冲 40000 FE。 */
    public static final DeferredBlock<LargeFurnaceGeneratorBlock> LARGE_FURNACE_GENERATOR =
            BLOCKS.registerBlock(
                    "large_furnace_generator",
                    LargeFurnaceGeneratorBlock::new,
                    props -> props
                            .strength(5.0F, 9.0F)
                            .sound(SoundType.STONE)
                            .requiresCorrectToolForDrops());

    /** 大型电动磨粉机：32 个一批、3 秒一批。 */
    public static final DeferredBlock<LargeElectricMillBlock> LARGE_ELECTRIC_MILL =
            BLOCKS.registerBlock(
                    "large_electric_mill",
                    LargeElectricMillBlock::new,
                    props -> props
                            .strength(5.0F, 9.0F)
                            .sound(SoundType.STONE)
                            .requiresCorrectToolForDrops());

    /** 大型电动脱壳机：32 个一批、3 秒一批。 */
    public static final DeferredBlock<LargeElectricShellerBlock> LARGE_ELECTRIC_SHELLER =
            BLOCKS.registerBlock(
                    "large_electric_sheller",
                    LargeElectricShellerBlock::new,
                    props -> props
                            .strength(5.0F, 9.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    // ==================================================================
    // 灶火系统：炉灶 + 炒锅 / 蒸笼 / 汤锅
    // ==================================================================
    //
    // 与电力系统并行的一条路线：炉灶烧燃料只供热不发电，
    // 三件锅具**坐在炉灶正上方**用热，不拉电线。

    /** 炉灶：烧原版燃料，给正上方一格的锅具供热。 */
    public static final DeferredBlock<StoveBlock> STOVE =
            BLOCKS.registerBlock(
                    "stove",
                    StoveBlock::new,
                    props -> props
                            .strength(3.0F, 6.0F)
                            .sound(SoundType.STONE)
                            .requiresCorrectToolForDrops());

    /** 炒锅：坐在炉灶上快炒。 */
    public static final DeferredBlock<WokBlock> WOK =
            BLOCKS.registerBlock(
                    "wok",
                    WokBlock::new,
                    props -> props
                            .strength(2.0F, 6.0F)
                            .sound(SoundType.METAL)
                            .noOcclusion());

    /** 蒸笼：坐在炉灶上蒸。 */
    public static final DeferredBlock<SteamerBlock> STEAMER =
            BLOCKS.registerBlock(
                    "steamer",
                    SteamerBlock::new,
                    props -> props
                            .strength(1.6F, 4.0F)
                            .sound(SoundType.WOOD)
                            .noOcclusion());

    /** 汤锅：坐在炉灶上吊汤。 */
    public static final DeferredBlock<SoupPotBlock> SOUP_POT =
            BLOCKS.registerBlock(
                    "soup_pot",
                    SoupPotBlock::new,
                    props -> props
                            .strength(2.4F, 6.0F)
                            .sound(SoundType.METAL)
                            .noOcclusion());

    /**
     * 直接摆在地上的菜。
     *
     * <p>没有对应的方块物品 —— 由菜品自己（{@code DishItem#useOn}）放下来，
     * 空手右键端起来。所以也不掉战利品（{@code noLootTable()}），
     * 免得坏了之后刷出两份菜。</p>
     */
    public static final DeferredBlock<PlacedDishBlock> PLACED_DISH = BLOCKS.registerBlock(
            "placed_dish",
            PlacedDishBlock::new,
            props -> props
                    .strength(0.3F)
                    .sound(SoundType.STONE)
                    .noOcclusion()
                    .noLootTable());

    // ==================================================================
    // 农作物
    // ==================================================================

    /** 水稻作物：长在耕地上，8 个生长阶段，成熟后掉落稻谷和种子。 */
    public static final DeferredBlock<RiceCropBlock> RICE_CROP =
            BLOCKS.registerBlock(
                    "rice_crop",
                    RiceCropBlock::new,
                    props -> props); // 直接返回原属性，BushBlock 会自动处理无碰撞、随机刻、瞬破和音效

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
    }

    private ModBlocks() {}
}
