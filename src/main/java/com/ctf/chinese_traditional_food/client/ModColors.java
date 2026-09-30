package com.ctf.chinese_traditional_food.client;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.DishPlacement;
import com.ctf.chinese_traditional_food.common.block.PlacedDishBlock;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import java.util.List;
import java.util.Set;
import net.minecraft.client.color.block.BlockTintSource;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterColorHandlersEvent;

/**
 * 方块着色：给「摆在地上的菜」按菜系配色上色。
 *
 * <p>模型里只有食物与汤汁那两组面带 {@code tintindex}（0 = 食物、1 = 汤汁），
 * 其余面保持材质本色，所以同一套几何能表现所有菜。</p>
 *
 * <h2>颜色为什么从方块状态读，而不是从方块实体读</h2>
 * 26.1 的方块模型着色走 {@code BlockStateModelWrapper#updateTints}，
 * 它调用的<b>只有</b> {@link BlockTintSource#color(BlockState)} ——
 * 在 {@code update()} 里传给模型的上下文是
 * {@code BlockAndTintGetter.EMPTY} 与 {@code BlockPos.ZERO}，
 * 整条路径上既没有世界也没有方块实体。
 * 换句话说 {@code colorInWorld} <b>永远不会被调用</b>。
 *
 * <p>所以这里只实现 {@code color(BlockState)}，颜色全部来自
 * {@link PlacedDishBlock#PALETTE} 这个方块状态属性。
 * 好处是区块烘焙、物品栏渲染、破坏粒子拿到的颜色完全一致。</p>
 *
 * <p>注意 26.1 的写法：事件是 {@code RegisterColorHandlersEvent.BlockTintSources}，
 * 而且必须<b>按 tintindex 依次给出</b>一个 {@link BlockTintSource} 列表
 * （列表下标就是 tintindex），不再是一个 BlockColor 回调。</p>
 */
@EventBusSubscriber(value = Dist.CLIENT, modid = ChineseTraditionalFood.MOD_ID)
public final class ModColors {

    /** 只有 palette 这一个属性会影响颜色，如告诉引擎。 */
    private static final Set<Property<?>> RELEVANT = Set.of(PlacedDishBlock.PALETTE);

    @SubscribeEvent
    public static void registerBlockTintSources(RegisterColorHandlersEvent.BlockTintSources event) {
        // 下标 0 -> 食物主体；下标 1 -> 汤汁（同色压暗一档）
        event.register(List.of(new PaletteTintSource(false), new PaletteTintSource(true)),
                ModBlocks.PLACED_DISH.get());
    }

    /** 从方块状态的 palette 属性取色。 */
    private static final class PaletteTintSource implements BlockTintSource {
        private final boolean liquid;

        private PaletteTintSource(boolean liquid) {
            this.liquid = liquid;
        }

        @Override
        public int color(BlockState state) {
            if (!state.hasProperty(PlacedDishBlock.PALETTE)) {
                return 0xFFFFFF;
            }
            DishPlacement.Palette palette = state.getValue(PlacedDishBlock.PALETTE);
            return this.liquid ? palette.liquidColor() : palette.color();
        }

        @Override
        public Set<Property<?>> relevantProperties() {
            return RELEVANT;
        }
    }

    private ModColors() {}
}
