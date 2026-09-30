package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.common.block.entity.ServingPlatterBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;

/**
 * 大拼盘渲染器：槽位 0~3 依次摆在 2×2 的四个角上。
 *
 * <pre>
 *   0 | 1
 *   --+--
 *   2 | 3
 * </pre>
 */
public class ServingPlatterBlockEntityRenderer extends AbstractDishDisplayRenderer<ServingPlatterBlockEntity> {

    /** 四个象限的 X 偏移（方块局部坐标）。 */
    private static final double[] OFFSET_X = { 0.29D, 0.71D, 0.29D, 0.71D };
    /** 四个象限的 Z 偏移。 */
    private static final double[] OFFSET_Z = { 0.29D, 0.29D, 0.71D, 0.71D };

    public ServingPlatterBlockEntityRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    protected void transformDish(PoseStack poseStack, DishDisplayRenderState renderState, int index) {
        int slot = Math.min(index, OFFSET_X.length - 1);
        poseStack.translate(OFFSET_X[slot], 0.14D, OFFSET_Z[slot]);
        // 拼盘上每份菜要小一点，否则四份会互相穿插
        poseStack.scale(0.45F, 0.45F, 0.45F);
    }
}
