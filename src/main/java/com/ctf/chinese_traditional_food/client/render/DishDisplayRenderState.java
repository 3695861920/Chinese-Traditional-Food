package com.ctf.chinese_traditional_food.client.render;

import net.minecraft.client.renderer.blockentity.state.BlockEntityRenderState;
import net.minecraft.client.renderer.item.ItemStackRenderState;

/**
 * 摆放类方块（餐盘 / 大拼盘）的渲染状态。
 *
 * <p>渲染状态是"每帧抽取一次、供提交阶段只读使用"的快照，
 * 所以里面的 {@link ItemStackRenderState} 也必须每帧重新构建，
 * 不能缓存到渲染器实例上。</p>
 *
 * <p>数组长度固定为 {@value #MAX_DISHES}，即当前所有摆放方块里最大的容量（大拼盘 4 份）。</p>
 */
public class DishDisplayRenderState extends BlockEntityRenderState {
    public static final int MAX_DISHES = 4;

    /** 每个槽位一份菜的渲染状态；空槽为 {@code null}。 */
    public final ItemStackRenderState[] dishes = new ItemStackRenderState[MAX_DISHES];
}
