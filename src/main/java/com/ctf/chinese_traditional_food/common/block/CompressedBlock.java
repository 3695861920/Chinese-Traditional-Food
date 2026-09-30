package com.ctf.chinese_traditional_food.common.block;

import net.minecraft.world.level.block.Block;

/**
 * 食材包装方块：把 9 个散装食材打包成"一袋 / 一箱 / 一缸 / 一块"。
 *
 * <h2>参考的是农夫乐事的稻米袋与卷心菜箱</h2>
 * <ul>
 *   <li><b>满格方块</b>：模型 0~16 铺满，码成一面墙、塞进箱子都整齐，
 *       格子之间也不会漏缝；</li>
 *   <li><b>一眼看得出装的是什么</b>：木箱是敞口的，箱口直接铺着菜；
 *       麻袋的袋口也露出内容物；</li>
 *   <li>行为就是<b>普通方块</b> —— 能放、能挖、挖了掉自己，
 *       <b>不需要右键取出</b>。想拆开就放工作台上用反向配方（9 个原料 ⇄ 1 个方块）。</li>
 * </ul>
 *
 * <p>不给每种写一个类：包装方块的行为完全一致，唯一不同的是贴图。
 * 所以全部复用这一个，用注册 id 区分。</p>
 *
 * <p><b>这个类与它的注册表都是生成出来的</b>，见 {@code tools/gen_compressed.py}。
 * 要加一种包装方块，往那个脚本的 {@code COMPRESSED} 表里填一行就行。</p>
 */
public class CompressedBlock extends Block {
    public CompressedBlock(Properties properties) {
        super(properties);
    }
}
