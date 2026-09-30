package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 大型电动磨粉机：把小型机"一条产线"塞进一个方块。
 *
 * <p>占地仍是一个方块（造型铺满整格、没有腿部留空），但数值上
 * 批次 ×4（32 个）、批次耗时 60 tick（3 秒）、单位耗电降到约三成 ——
 * 详见 {@code MachineEnergy} 里"大型机"那一节的账。</p>
 *
 * <p>实现上只多了 {@link #large()} 这一个开关：容量、批次、耗电全部由
 * {@code AbstractProcessorBlockEntity} 的数值钩子推到大型档，主循环逻辑不分叉。</p>
 */
public class LargeElectricMillBlockEntity extends AbstractProcessorBlockEntity {

    public LargeElectricMillBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.LARGE_ELECTRIC_MILL.get(), pos, state);
    }

    public LargeElectricMillBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected boolean large() {
        return true;
    }

    @Override
    protected Kind kind() {
        return Kind.MILLING;
    }
}
