package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.entity.PlacedDishBlockEntity;
import com.ctf.chinese_traditional_food.common.item.DishItem;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 「直接摆在地上的菜」。
 *
 * <h2>为什么要做成一个方块而不是一个渲染器</h2>
 * 原版表达三维食物用的就是<b>方块 + 方块状态 + 立方体模型</b>
 * （蛋糕、南瓜派、讲台都是这个路子）。所以这里照做：
 *
 * <ul>
 *   <li>只注册<b>一个</b>方块，用 {@link #SHAPE} 属性选三维模型；</li>
 *   <li>模型是手写的立方体元素，有真正的体积与叠层，不是平面贴图；</li>
 *   <li>每道菜的颜色由<b>方块着色</b>（见 {@code ModColors}）按菜系配色的主色染上去 ——
 *       和原版给树叶 / 草 / 药水上色是同一套机制。</li>
 * </ul>
 *
 * <p>结果是：零自定义渲染器、零自定义模型加载器，进游戏就是标准方块模型，
 * 和原版摆在一起完全不违和。</p>
 *
 * <h2>交互</h2>
 * <ul>
 *   <li>拿菜对着<b>地面或方块顶面</b>右键 → 摆在地上；</li>
 *   <li><b>空手右键</b> → 端起来放回背包（方便收拾）。</li>
 * </ul>
 */
public class PlacedDishBlock extends Block implements EntityBlock {
    /** 选三维模型用的属性。取值顺序与 {@code tools/dish_models.py} 的 SHAPE_ORDER 一致。 */
    public static final EnumProperty<DishPlacement.Shape> SHAPE =
            EnumProperty.create("shape", DishPlacement.Shape.class);

    /**
     * 每种器型的碰撞箱，下标就是 {@link DishPlacement.Shape#id()}。
     *
     * <p>这些数字不是手写的，而是 {@code tools/dish_models.py} 从模型元素的
     * 极值**实测**出来、写进 {@link DishPlacement#boundsOf} 的 ——
     * 也就是用户要的"<b>模型多大就占多大</b>"：
     * 盘子只有薄薄一层、酒盏不会挡住整格、粽子占地最小。</p>
     *
     * <p>用 {@code VoxelShape} 的惰性数组而不是每次 {@code Block.box()}：
     * 碰撞箱查得非常频繁，不能每次都新建对象。</p>
     */
    private static final VoxelShape[] SHAPES = new VoxelShape[DishPlacement.Shape.values().length];

    public PlacedDishBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(SHAPE, DishPlacement.Shape.BOWL));
    }

    /** 按器型取碰撞箱（首次访问时从 DishPlacement 的实测包围盒构建）。 */
    private static VoxelShape shapeFor(DishPlacement.Shape shape) {
        int i = shape.id();
        VoxelShape cached = SHAPES[i];
        if (cached == null) {
            float[] b = DishPlacement.boundsOf(shape);
            cached = Block.box(b[0], b[1], b[2], b[3], b[4], b[5]);
            SHAPES[i] = cached;
        }
        return cached;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(SHAPE);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos,
                                  CollisionContext context) {
        return shapeFor(state.getValue(SHAPE));
    }

    /** 碰撞用同一个盒子 —— 玩家能走到盘子边上，不会被一整格挡 住。 */
    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos,
                                           CollisionContext context) {
        return shapeFor(state.getValue(SHAPE));
    }

    @Nullable
    @Override
    public net.minecraft.world.level.block.entity.BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new PlacedDishBlockEntity(pos, state);
    }

    // ------------------------------------------------------------------
    // 端起来
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof PlacedDishBlockEntity be)) {
            return InteractionResult.PASS;
        }
        ItemStack dish = be.takeDish();
        if (dish.isEmpty()) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide()) {
            return InteractionResult.SUCCESS;
        }
        if (!player.getInventory().add(dish)) {
            player.drop(dish, false);
        }
        level.removeBlock(pos, false);
        level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.7F, 1.0F);
        return InteractionResult.SUCCESS;
    }

    /** 别的模组 / 玩家用桶之类的东西右键时，不要把它当容器抢走。 */
    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                          Player player, InteractionHand hand, BlockHitResult hit) {
        // 手上还拿着菜再点，就再摆一份（叠到旁边的地面逻辑由 DishItem#useOn 处理）
        return InteractionResult.TRY_WITH_EMPTY_HAND;
    }

    /** 只有玩家拿着能摆的菜时才用得上；给 DishItem 调用的静态放置。 */
    public static boolean place(Level level, BlockPos above, ItemStack dish) {
        DishPlacement.Shape shape = DishPlacement.shapeOf(dish.getItem());
        if (shape == null) {
            return false;
        }
        BlockState state = com.ctf.chinese_traditional_food.registry.ModBlocks.PLACED_DISH.get()
                .defaultBlockState()
                .setValue(SHAPE, shape);
        if (!level.setBlock(above, state, Block.UPDATE_ALL)) {
            return false;
        }
        if (level.getBlockEntity(above) instanceof PlacedDishBlockEntity be) {
            be.setDish(0, dish.copyWithCount(1));
            be.onDishesChanged();
        }
        level.playSound(null, above, SoundEvents.STONE_PLACE, SoundSource.BLOCKS,
                0.7F, 1.0F + level.getRandom().nextFloat() * 0.2F);
        return true;
    }

    /** 让 {@link DishItem} 判断"这道菜能不能摆地上"。 */
    public static boolean canPlaceItem(ItemStack stack) {
        return DishPlacement.shapeOf(stack.getItem()) != null;
    }

    /** 供方块物品（若有）复用：音效类型。 */
    public static SoundType sound() {
        return SoundType.STONE;
    }
}
