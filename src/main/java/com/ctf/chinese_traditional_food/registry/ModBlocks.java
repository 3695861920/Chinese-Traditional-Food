package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.CuttingBoardBlock;
import com.ctf.chinese_traditional_food.common.block.ElectricMillBlock;
import com.ctf.chinese_traditional_food.common.block.ElectricShellerBlock;
import com.ctf.chinese_traditional_food.common.block.FurnaceGeneratorBlock;
import com.ctf.chinese_traditional_food.common.block.PlacedDishBlock;
import com.ctf.chinese_traditional_food.common.block.PlateBlock;
import com.ctf.chinese_traditional_food.common.block.ServingPlatterBlock;
import net.minecraft.world.level.block.SoundType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 方块注册表。
 *
 * <p>共 8 个方块：</p>
 * <ul>
 *   <li>餐盘 / 大拼盘 —— 把菜摆出来（1 份 / 4 份）；</li>
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
    public static final DeferredBlock<ServingPlatterBlock> SERVING_PLATTER = BLOCKS.registerBlock(
            "serving_platter",
            ServingPlatterBlock::new,
            props -> props
                    .strength(0.6F)
                    .sound(SoundType.WOOD)
                    .noOcclusion());

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

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
    }

    private ModBlocks() {}
}
