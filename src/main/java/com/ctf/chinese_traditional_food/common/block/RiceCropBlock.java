package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.registry.ModItems;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

public class RiceCropBlock extends CropBlock {
    public RiceCropBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    protected Item getBaseSeedId() {
        // 绑定到种子物品，成熟掉落或骨粉催熟时会用到
        return ModItems.RICE_SEEDS.get();
    }

    @Override
    public int getMaxAge() {
        return 7; // 8个生长阶段（0~7），和原版小麦一致
    }
}