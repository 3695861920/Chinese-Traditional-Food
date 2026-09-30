package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 大型熔炉发电机：输出 200 FE/t、缓冲 40000 FE。
 *
 * <p>为什么要 200 FE/t：四台大型加工机同时跑就要 4 × 40 = 160 FE/t，
 * 留一点余量给管道损耗和缓冲回充。缓冲 40000 FE 约等于
 * 两块半煤炭的发电量，足够让"加燃料的手速"不再是瓶颈。</p>
 */
public class LargeFurnaceGeneratorBlockEntity extends FurnaceGeneratorBlockEntity {

    public LargeFurnaceGeneratorBlockEntity(BlockPos pos, BlockState state) {
        this(ModBlockEntities.LARGE_FURNACE_GENERATOR.get(), pos, state);
    }

    public LargeFurnaceGeneratorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    protected boolean large() {
        return true;
    }
}
