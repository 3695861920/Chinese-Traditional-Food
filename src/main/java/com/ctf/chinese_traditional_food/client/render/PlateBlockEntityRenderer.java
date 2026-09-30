package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.common.block.entity.PlateBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;

/**
 * 餐盘渲染器：一份菜居中、略微浮在盘面上。
 */
public class PlateBlockEntityRenderer extends AbstractDishDisplayRenderer<PlateBlockEntity> {

    public PlateBlockEntityRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    protected void transformDish(PoseStack poseStack, DishDisplayRenderState renderState, int index) {
        // 平移让菜的中心落在方块中心，再抬高到盘面上方一点点
        poseStack.translate(0.5D, 0.16D, 0.5D);
        // 缩到 0.62 —— 盘子直径约 14/16 格，菜比盘子略小才好看
        poseStack.scale(0.62F, 0.62F, 0.62F);
    }
}
