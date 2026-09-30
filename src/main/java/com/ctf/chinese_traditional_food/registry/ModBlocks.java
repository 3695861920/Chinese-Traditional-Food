package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.PlateBlock;
import com.ctf.chinese_traditional_food.common.block.ServingPlatterBlock;
import net.minecraft.world.level.block.SoundType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 方块注册表。
 *
 * <p>本批次只注册"用来摆放菜品"的两个方块。
 * 灶台 / 蒸笼 / 炒锅 / 汤锅 / 砂锅 / 案板 / 水磨 / 脱壳机 按 <code>docs/物品清单.md</code>
 * 的阶段 3~4 陆续补进来，写法与这里完全一致。</p>
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

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
    }

    private ModBlocks() {}
}
