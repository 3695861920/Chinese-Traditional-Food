package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 大型电动脱壳机：和大型磨粉机同一套放大档，只是查脱壳表。
 *
 * @see LargeElectricMillBlockEntity
 */
public class LargeElectricShellerBlockEntity extends AbstractProcessorBlockEntity {

    public LargeElectricShellerBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.LARGE_ELECTRIC_SHELLER.get(), pos, state);
    }

    public LargeElectricShellerBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected boolean large() {
        return true;
    }

    @Override
    protected Kind kind() {
        return Kind.SHELLING;
    }
}
