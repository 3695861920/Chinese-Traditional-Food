package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.common.block.entity.CuttingBoardBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;

/**
 * 案板渲染器：左边画待切的食材，右边画切好的成品。
 *
 * <p>因为 {@link CuttingBoardBlockEntity} 复用了"摆放类"的存储与渲染状态，
 * 这里只要决定两个槽位的位置与大小即可 —— 和餐盘 / 大拼盘是同一套机制。</p>
 */
public class CuttingBoardBlockEntityRenderer extends AbstractDishDisplayRenderer<CuttingBoardBlockEntity> {

    public CuttingBoardBlockEntityRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    protected void transformDish(PoseStack poseStack, DishDisplayRenderState renderState, int index) {
        if (index == CuttingBoardBlockEntity.SLOT_INPUT) {
            // 待切食材：摆在板子左半边
            poseStack.translate(0.31D, 0.10D, 0.5D);
            poseStack.scale(0.52F, 0.52F, 0.52F);
        } else {
            // 成品：右半边，稍微小一点，暗示"切好的"
            poseStack.translate(0.70D, 0.10D, 0.5D);
            poseStack.scale(0.46F, 0.46F, 0.46F);
        }
    }
}
