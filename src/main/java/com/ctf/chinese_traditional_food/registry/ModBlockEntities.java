package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.entity.CuttingBoardBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.ElectricMillBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.ElectricShellerBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.FurnaceGeneratorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.LargeElectricMillBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.LargeElectricShellerBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.LargeFurnaceGeneratorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.PlacedDishBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.PlateBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.SoupPotBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.SteamerBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.StoveBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.WokBlockEntity;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 方块实体类型注册表。
 *
 * <p>{@code new BlockEntityType<>(Supplier, Block...)} 的 Supplier 就是
 * {@code (BlockPos, BlockState) -> BlockEntity}，所以每个方块实体类都必须有一个
 * 这样的构造函数。</p>
 */
public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(BuiltInRegistries.BLOCK_ENTITY_TYPE, ChineseTraditionalFood.MOD_ID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<PlateBlockEntity>> PLATE =
            BLOCK_ENTITIES.register("plate",
                    () -> new BlockEntityType<>(PlateBlockEntity::new, ModBlocks.PLATE.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<CuttingBoardBlockEntity>> CUTTING_BOARD =
            BLOCK_ENTITIES.register("cutting_board",
                    () -> new BlockEntityType<>(CuttingBoardBlockEntity::new, ModBlocks.CUTTING_BOARD.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<FurnaceGeneratorBlockEntity>> FURNACE_GENERATOR =
            BLOCK_ENTITIES.register("furnace_generator",
                    () -> new BlockEntityType<>(FurnaceGeneratorBlockEntity::new,
                            ModBlocks.FURNACE_GENERATOR.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<ElectricMillBlockEntity>> ELECTRIC_MILL =
            BLOCK_ENTITIES.register("electric_mill",
                    () -> new BlockEntityType<>(ElectricMillBlockEntity::new,
                            ModBlocks.ELECTRIC_MILL.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<ElectricShellerBlockEntity>> ELECTRIC_SHELLER =
            BLOCK_ENTITIES.register("electric_sheller",
                    () -> new BlockEntityType<>(ElectricShellerBlockEntity::new,
                            ModBlocks.ELECTRIC_SHELLER.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<PlacedDishBlockEntity>> PLACED_DISH =
            BLOCK_ENTITIES.register("placed_dish",
                    () -> new BlockEntityType<>(PlacedDishBlockEntity::new, ModBlocks.PLACED_DISH.get()));

    // ---- 大型机 ----------------------------------------------------

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<LargeFurnaceGeneratorBlockEntity>> LARGE_FURNACE_GENERATOR =
            BLOCK_ENTITIES.register("large_furnace_generator",
                    () -> new BlockEntityType<>(LargeFurnaceGeneratorBlockEntity::new,
                            ModBlocks.LARGE_FURNACE_GENERATOR.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<LargeElectricMillBlockEntity>> LARGE_ELECTRIC_MILL =
            BLOCK_ENTITIES.register("large_electric_mill",
                    () -> new BlockEntityType<>(LargeElectricMillBlockEntity::new,
                            ModBlocks.LARGE_ELECTRIC_MILL.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<LargeElectricShellerBlockEntity>> LARGE_ELECTRIC_SHELLER =
            BLOCK_ENTITIES.register("large_electric_sheller",
                    () -> new BlockEntityType<>(LargeElectricShellerBlockEntity::new,
                            ModBlocks.LARGE_ELECTRIC_SHELLER.get()));

    // ---- 灶火系统 --------------------------------------------------

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<StoveBlockEntity>> STOVE =
            BLOCK_ENTITIES.register("stove",
                    () -> new BlockEntityType<>(StoveBlockEntity::new, ModBlocks.STOVE.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<WokBlockEntity>> WOK =
            BLOCK_ENTITIES.register("wok",
                    () -> new BlockEntityType<>(WokBlockEntity::new, ModBlocks.WOK.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<SteamerBlockEntity>> STEAMER =
            BLOCK_ENTITIES.register("steamer",
                    () -> new BlockEntityType<>(SteamerBlockEntity::new, ModBlocks.STEAMER.get()));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<SoupPotBlockEntity>> SOUP_POT =
            BLOCK_ENTITIES.register("soup_pot",
                    () -> new BlockEntityType<>(SoupPotBlockEntity::new, ModBlocks.SOUP_POT.get()));

    public static void register(IEventBus modBus) {
        BLOCK_ENTITIES.register(modBus);
    }

    private ModBlockEntities() {}
}
