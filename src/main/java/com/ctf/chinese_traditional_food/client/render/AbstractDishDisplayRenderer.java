package com.ctf.chinese_traditional_food.client.render;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractDishDisplayBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.feature.ModelFeatureRenderer;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

/**
 * 摆放类方块渲染器的公共父类：把方块实体里的菜"当作物品"渲染在方块上方。
 *
 * <p>整体流程（26.1 的渲染拆分模型）：</p>
 * <ol>
 *   <li>{@code extractRenderState} —— 渲染线程之外，把方块实体数据拷成快照，
 *       并用 {@link ItemModelResolver} 把每个 {@link ItemStack} 解析成
 *       {@link ItemStackRenderState}；</li>
 *   <li>{@code submit} —— 把快照提交给 {@link SubmitNodeCollector}，
 *       由引擎按不透明度 / 顺序统一绘制。</li>
 * </ol>
 *
 * <p>子类只需要实现 {@link #createRenderState()} 和
 * {@link #transformDish(PoseStack, DishDisplayRenderState, int)}，
 * 决定第 i 份菜摆在哪个位置、多大。</p>
 */
public abstract class AbstractDishDisplayRenderer<T extends AbstractDishDisplayBlockEntity>
        implements BlockEntityRenderer<T, DishDisplayRenderState> {

    protected final ItemModelResolver itemModelResolver;

    protected AbstractDishDisplayRenderer(BlockEntityRendererProvider.Context context) {
        this.itemModelResolver = context.itemModelResolver();
    }

    @Override
    public DishDisplayRenderState createRenderState() {
        return new DishDisplayRenderState();
    }

    @Override
    public void extractRenderState(T blockEntity, DishDisplayRenderState renderState, float partialTick,
                                   Vec3 cameraPos,
                                   ModelFeatureRenderer.@Nullable CrumblingOverlay crumblingOverlay) {
        // 必须调用 super，它会填充 lightCoords 等基础字段
        BlockEntityRenderer.super.extractRenderState(blockEntity, renderState, partialTick, cameraPos, crumblingOverlay);

        // 逐个槽位重建渲染状态；用不到的槽位必须显式置空，
        // 否则渲染状态会在帧之间复用而残留上一帧的菜。
        int capacity = Math.min(blockEntity.getCapacity(), DishDisplayRenderState.MAX_DISHES);
        for (int i = 0; i < DishDisplayRenderState.MAX_DISHES; i++) {
            if (i >= capacity) {
                renderState.dishes[i] = null;
                continue;
            }
            ItemStack dish = blockEntity.getDish(i);
            if (dish.isEmpty()) {
                renderState.dishes[i] = null;
                continue;
            }
            ItemStackRenderState itemState = new ItemStackRenderState();
            this.itemModelResolver.updateForTopItem(
                    itemState,
                    dish,
                    ItemDisplayContext.FIXED,
                    blockEntity.getLevel(),
                    null,
                    0);
            renderState.dishes[i] = itemState;
        }
    }

    @Override
    public void submit(DishDisplayRenderState renderState, PoseStack poseStack,
                       SubmitNodeCollector collector, CameraRenderState camera) {
        for (int i = 0; i < renderState.dishes.length; i++) {
            ItemStackRenderState dish = renderState.dishes[i];
            if (dish == null) {
                continue;
            }
            poseStack.pushPose();
            this.transformDish(poseStack, renderState, i);
            dish.submit(poseStack, collector, renderState.lightCoords, OverlayTexture.NO_OVERLAY, 0);
            poseStack.popPose();
        }
    }

    /**
     * 决定第 {@code index} 份菜的摆放位置（方块局部坐标系，0~1 为方块本身，可略微超出）。
     */
    protected abstract void transformDish(PoseStack poseStack, DishDisplayRenderState renderState, int index);
}
