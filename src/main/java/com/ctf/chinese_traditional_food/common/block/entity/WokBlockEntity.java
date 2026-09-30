package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 炒锅：坐在炉灶上快炒。
 *
 * <p>规则表见 {@code ModRecipes.COOKING}，动力来自正下方的
 * {@code 炉灶}（见 {@link AbstractHeatProcessorBlockEntity}）。</p>
 */
public class WokBlockEntity extends AbstractHeatProcessorBlockEntity {

    public WokBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.WOK.get(), pos, state);
    }

    public WokBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected Kind kind() {
        return Kind.COOKING;
    }
}
