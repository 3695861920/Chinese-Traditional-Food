package com.ctf.chinese_traditional_food.client;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.ctf.chinese_traditional_food.common.block.DishPlacement;
import com.ctf.chinese_traditional_food.common.block.entity.PlacedDishBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import java.util.List;
import net.minecraft.client.color.block.BlockTintSource;
import net.minecraft.client.renderer.block.BlockAndTintGetter;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterColorHandlersEvent;

/**
 * 方块着色：给「摆在地上的菜」按菜系配色上色。
 *
 * <p>模型里只有食物与汤汁那两组面带 {@code tintindex}（0 = 食物、1 = 汤汁），
 * 其余面保持材质本色。颜色从方块实体里那份菜查 {@link DishPlacement} 得到 ——
 * 所以同一套几何能表现所有菜，不需要给每道菜单独做模型。</p>
 *
 * <p>注意 26.1 的写法：事件是 {@code RegisterColorHandlersEvent.BlockTintSources}，
 * 而且必须<b>按 tintindex 依次给出</b>一个 {@link BlockTintSource} 列表
 * （列表下标就是 tintindex），不再是一个 BlockColor 回调。</p>
 */
@EventBusSubscriber(value = Dist.CLIENT, modid = ChineseTraditionalFood.MOD_ID)
public final class ModColors {

    @SubscribeEvent
    public static void registerBlockTintSources(RegisterColorHandlersEvent.BlockTintSources event) {
        // 下标 0 -> 食物主体；下标 1 -> 汤汁（同色压暗一档）
        BlockTintSource food = new BlockTintSource() {
            @Override
            public int color(BlockState state) {
                return 0xFFFFFF;    // 没有世界上下文时用中性色
            }

            @Override
            public int colorInWorld(BlockState state, BlockAndTintGetter level, BlockPos pos) {
                return tintFor(level, pos, false);
            }
        };

        BlockTintSource liquid = new BlockTintSource() {
            @Override
            public int color(BlockState state) {
                return 0xFFFFFF;
            }

            @Override
            public int colorInWorld(BlockState state, BlockAndTintGetter level, BlockPos pos) {
                return tintFor(level, pos, true);
            }
        };

        event.register(List.of(food, liquid), ModBlocks.PLACED_DISH.get());
    }

    /** 从方块实体里那份菜查颜色。 */
    private static int tintFor(BlockAndTintGetter level, BlockPos pos, boolean liquid) {
        if (level == null || pos == null) {
            return 0xFFFFFF;
        }
        if (!(level.getBlockEntity(pos) instanceof PlacedDishBlockEntity be)) {
            return 0xFFFFFF;
        }
        ItemStack dish = be.getDish(0);
        if (dish.isEmpty()) {
            return 0xFFFFFF;
        }
        return liquid
                ? DishPlacement.liquidColorOf(dish.getItem())
                : DishPlacement.colorOf(dish.getItem());
    }

    private ModColors() {}
}
