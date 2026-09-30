package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.CuttingBoardBlock;
import com.ctf.chinese_traditional_food.common.block.GrainShellerBlock;
import com.ctf.chinese_traditional_food.common.block.MachinePartBlock;
import com.ctf.chinese_traditional_food.common.block.PlacedDishBlock;
import com.ctf.chinese_traditional_food.common.block.PlateBlock;
import com.ctf.chinese_traditional_food.common.block.ServingPlatterBlock;
import com.ctf.chinese_traditional_food.common.block.WaterMillBlock;
import com.ctf.chinese_traditional_food.common.block.WaterWheelBlock;
import net.minecraft.world.level.block.SoundType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 方块注册表。
 *
 * <p>共 6 个方块：</p>
 * <ul>
 *   <li>餐盘 / 大拼盘 —— 把菜摆出来（1 份 / 4 份）；</li>
 *   <li>案板 —— 放上食材后用刀切；</li>
 *   <li>水磨 —— 邻水自动把谷物磨成粉（3×3×3 大型机器）；</li>
 *   <li>脱壳机 —— 手摇，无界面（3×3×3 大型机器）；</li>
 *   <li>两种机器部件 —— 大型机器的组成零件，自己不带逻辑。</li>
 * </ul>
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
     * 水磨核心：石台正中那扇磨盘，也是整台机器的控制器。
     *
     * <p>放下它会自动展开成一整台水磨（石台 + 横轴 + 两侧水车接口 + 立柱），
     * 空间不够就不让放。水车接口在机身左右两侧，装上会转的水车它才会磨粉。</p>
     */
    public static final DeferredBlock<WaterMillBlock> WATER_MILL = BLOCKS.registerBlock(
            "water_mill",
            WaterMillBlock::new,
            props -> props
                    .strength(2.0F, 6.0F)
                    .sound(SoundType.STONE)
                    .requiresCorrectToolForDrops());

    /**
     * 手摇式脱壳机核心：木机身 + 侧面摇柄，<b>没有界面</b>。
     *
     * <p>放下它会自动展开成一整台 3×3×3 的碾米机（木架 + 机箱 + 立柱 + 顶部料斗）。
     * 带壳谷物右键 = 倒进去，潜行空手右键 = 摇一圈，空手右键 = 取成品。</p>
     */
    public static final DeferredBlock<GrainShellerBlock> GRAIN_SHELLER = BLOCKS.registerBlock(
            "grain_sheller",
            GrainShellerBlock::new,
            props -> props
                    .strength(2.0F, 6.0F)
                    .sound(SoundType.WOOD)
                    .requiresCorrectToolForDrops());

    /**
     * 水车：挂在水磨两侧的接口上，泡在水里转，给水磨提供动力。
     *
     * <p>{@code noOcclusion()} —— 水车是一个薄轮子，有很多镂空，
     * 不该挡住邻居的贴面剔除。轮轴朝向与转动帧都是方块状态。</p>
     */
    public static final DeferredBlock<WaterWheelBlock> WATER_WHEEL = BLOCKS.registerBlock(
            "water_wheel",
            WaterWheelBlock::new,
            props -> props
                    .strength(1.5F, 4.0F)
                    .sound(SoundType.WOOD)
                    .noOcclusion()
                    .requiresCorrectToolForDrops());

    /**
     * 水磨部件：石台 / 水轮 / 传动箱。
     *
     * <p>同一个方块用 {@code dx/dy/dz} 三个属性表达所有格子，
     * 用哪个模型由属性决定。玩家拆下来的零件都是这一个物品，
     * 补回去时会自动认领正确的格子。</p>
     */
    public static final DeferredBlock<MachinePartBlock> WATER_MILL_PART = BLOCKS.registerBlock(
            "water_mill_part",
            MachinePartBlock::new,
            props -> props
                    .strength(1.5F, 4.0F)
                    .sound(SoundType.STONE)
                    .requiresCorrectToolForDrops());

    /** 脱壳机部件：木架 / 机箱板 / 立柱 / 顶部料斗。 */
    public static final DeferredBlock<MachinePartBlock> GRAIN_SHELLER_PART = BLOCKS.registerBlock(
            "grain_sheller_part",
            MachinePartBlock::new,
            props -> props
                    .strength(1.5F, 4.0F)
                    .sound(SoundType.WOOD)
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
