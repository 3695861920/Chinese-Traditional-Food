package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractDishDisplayBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.PlateBlockEntity;
import com.ctf.chinese_traditional_food.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 餐盘：单份菜的展示方块（素面白瓷）。
 *
 * <p>把菜摆上去之后，客户端由
 * {@code com.ctf.chinese_traditional_food.client.render.PlateBlockEntityRenderer}
 * 把菜渲染在盘子上方。</p>
 *
 * <h2>实际占用体积</h2>
 * <p>盘子的模型是 {@code x/z = 0.8..15.2, y = 0..3.35}
 * （盘沿顶面 3.35 = 0.21 格高），所以它<b>只占这么点空间</b>：
 * 挡不住玩家走路、跳不上去、旁边方块也不受影响。</p>
 * <p>如果不写 {@code getShape}，方块会默认占满一整格 —— 明明是 3 像素高的
 * 盘子却有一格高的碰撞箱，走上去会「上台阶」，非常别扭。</p>
 *
 * <h2>空盘子可以端走</h2>
 * <p>地上吃完菜留下的空盘子（见 {@code PlacedDishBlock}）是同一个方块。
 * 空手右键一只空盘会把<b>盘子本身</b>收进背包 —— 否则摆一桌吃完全剩一地空盘子，
 * 只能一个个敲掉，太碎。</p>
 */
public class PlateBlock extends AbstractDishDisplayBlock {

    /** 盘子的真实占用体积（与 {@code display_models.plate()} 的模型边界一致）。 */
    private static final VoxelShape SHAPE =
            Block.box(0.8, 0.0, 0.8, 15.2, 3.35, 15.2);

    public PlateBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos,
                                  CollisionContext context) {
        return SHAPE;
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos,
                                           CollisionContext context) {
        return SHAPE;
    }

    /**
     * 空盘 + 空手右键 → 把盘子收回背包；盘里有菜 → 走父类（夹一口 / 端走）。
     */
    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (level.getBlockEntity(pos) instanceof AbstractDishDisplayBlockEntity display
                && display.lastOccupiedSlot() < 0) {
            if (level.isClientSide()) {
                return InteractionResult.SUCCESS_SERVER;
            }
            level.removeBlock(pos, false);
            ItemStack plate = new ItemStack(ModItems.PLATE.get());
            if (!player.getInventory().add(plate)) {
                player.drop(plate, false);
            }
            level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.7F, 1.1F);
            return InteractionResult.SUCCESS_SERVER;
        }
        return super.useWithoutItem(state, level, pos, player, hit);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new PlateBlockEntity(pos, state);
    }
}
