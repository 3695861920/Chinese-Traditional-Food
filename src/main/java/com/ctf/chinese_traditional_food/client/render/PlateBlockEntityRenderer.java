package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.common.block.entity.PlateBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;

/**
 * 餐盘渲染器：一份菜居中、平铺在盘底的凹面里。
 *
 * <h2>为什么要绕 X 轴转 -90°</h2>
 * 这里用的是 {@code ItemDisplayContext.FIXED}（展示框用的那套）。
 * 原版的物品贴片是画在 <b>XY 平面</b>上的（见 {@code ItemModelGenerator}：
 * 几何范围 x 0~16、y 0~16、z 7.5~8.5），所以 FIXED 下物品是<b>竖立</b>的。
 * 原版营火、地面上的展示框都要额外转一下才会放平：
 * <ul>
 *   <li>营火：{@code mulPose(Axis.XP.rotationDegrees(90.0F))}</li>
 *   <li>朝上的展示框：{@code xRot = -90}，再配上 FIXED 自带的
 *       {@code rotation: [0,180,0]}，净效果就是绕 X 转 -90°</li>
 * </ul>
 * 这里采用和「朝上的展示框」完全一致的写法（净旋转 Rx(-90)），
 * 贴片就会<b>正面朝上、方向正确</b>地躺在盘子里。
 */
public class PlateBlockEntityRenderer extends AbstractDishDisplayRenderer<PlateBlockEntity> {

    public PlateBlockEntityRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    protected void transformDish(PoseStack poseStack, DishDisplayRenderState renderState, int index) {
        // 盘子中央，y 抬到盘底顶面（模型里是 2.55/16 格）之上一点点
        poseStack.translate(0.5D, 0.165D, 0.5D);
        // 放平：贴片的正面朝上（与「朝上的展示框」同一套变换）
        poseStack.mulPose(Axis.XP.rotationDegrees(-90.0F));
        // 缩到 0.62 —— 盘内圈大约 0.68 格，菜比盘子略小才好看
        poseStack.scale(0.62F, 0.62F, 0.62F);
    }
}
