package com.ctf.chinese_traditional_food.common.block;

import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

/**
 * 本模组所有"种在地里的作物"共用这一个类。
 *
 * <h2>为什么不一种作物写一个类</h2>
 * 三十多种作物的<b>行为完全一样</b>（八个生长阶段、要在耕地上、要光、
 * 骨粉能催、成熟了才能收），差别只有三处：<b>贴图</b>、<b>掉落</b>、
 * <b>能种出什么</b>。前两样都在资源文件里（blockstate 挑图、loot_table 给掉落），
 * 所以 Java 这边一行都不用分家 —— 一种作物一个新实例就行。
 *
 * <h2>只覆写了一个方法</h2>
 * 原版 {@link CropBlock} 把"这是谁的种子"写死成了小麦种子
 * （{@code getBaseSeedId()} 返回 {@code Items.WHEAT_SEEDS}），
 * 于是拿剪刀 / 中键复制作物会掉出小麦种子。这里改成"我自己对应的那个物品"——
 * 而我们的种子物品就是<b>这个方块的 BlockItem</b>，所以 {@code asItem()} 正好。
 */
public class ModCropBlock extends CropBlock {

    public ModCropBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    /** 种子物品 = 本方块的方块物品（见 {@code ModCrops} 的注册方式）。 */
    @Override
    protected ItemLike getBaseSeedId() {
        return this.asItem();
    }
}
