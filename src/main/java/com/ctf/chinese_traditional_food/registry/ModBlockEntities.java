package com.ctf.chinese_traditional_food.registry;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.entity.CuttingBoardBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.ElectricMillBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.ElectricShellerBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.FurnaceGeneratorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.PlacedDishBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.PlateBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.ServingPlatterBlockEntity;
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

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<ServingPlatterBlockEntity>> SERVING_PLATTER =
            BLOCK_ENTITIES.register("serving_platter",
                    () -> new BlockEntityType<>(ServingPlatterBlockEntity::new, ModBlocks.SERVING_PLATTER.get()));

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

    public static void register(IEventBus modBus) {
        BLOCK_ENTITIES.register(modBus);
    }

    private ModBlockEntities() {}
}
