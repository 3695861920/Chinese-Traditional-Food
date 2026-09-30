package com.ctf.chinese_traditional_food.common.block;

import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * 「有正面」的方块：放下时正面朝着玩家。
 *
 * <h2>为什么不继承 HorizontalDirectionalBlock</h2>
 * 26.1 的那个类多了个抽象方法 {@code codec()}（数据包序列化用），
 * 子类不实现就编译不过；而我们这三台机器根本不需要被数据包引用，
 * 自己声明一个 {@code EnumProperty} 反而更干脆。
 *
 * <h2>为什么要有这一层</h2>
 * 发电机（只有燃料槽）和加工机（进料 + 出料槽）不是同一个继承链，
 * 但**都要有正面** —— 把朝向这块单独提出来，
 * 两个分支各取所需，不用为了共享朝向而硬凑成一棵树。
 */
public abstract class AbstractFacingBlock extends Block {
    /**
     * 水平朝向（正面的方向）。
     *
     * <p>26.1 的 {@code BlockStateProperties.HORIZONTAL_FACING} 是
     * {@code EnumProperty<Direction>}，不再是老的 {@code DirectionProperty}。</p>
     */
    public static final EnumProperty<Direction> FACING = BlockStateProperties.HORIZONTAL_FACING;

    /**
     * 机器的碰撞箱：机身从 1 到 15，四周留出一圈空。
     *
     * <p>机器的造型是"四条腿搭起的机身"，所以碰撞箱也跟着内缩 ——
     * 否则会出现"看着能走过去却被空气墙挡住"这种恼人的情况。</p>
     */
    public static final VoxelShape MACHINE_SHAPE = Block.box(1.0, 0.0, 1.0, 15.0, 16.0, 15.0);

    /**
     * 大型机的碰撞箱：**整整一格**。
     *
     * <p>小型机是“四条腿搭起的机身”，所以内缩一圈；而大型机造型就是铺满整格的
     * 方箱，碰撞箱自然也该是一整格 —— 否则一面对它站着就会被空气墙顶住。</p>
     */
    public static final VoxelShape LARGE_MACHINE_SHAPE = Block.box(0.0, 0.0, 0.0, 16.0, 16.0, 16.0);

    protected AbstractFacingBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(FACING, Direction.NORTH));
    }

    /** 供子类覆写：大型机返回整格长方体。 */
    protected VoxelShape machineShape() {
        return MACHINE_SHAPE;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, net.minecraft.core.BlockPos pos,
                                  CollisionContext context) {
        return this.machineShape();
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level,
                                           net.minecraft.core.BlockPos pos,
                                           CollisionContext context) {
        return this.machineShape();
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    /** 正面朝着玩家（玩家看过来时是"正对着他"）。 */
    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return this.defaultBlockState()
                .setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    protected BlockState rotate(BlockState state, Rotation rotation) {
        return state.setValue(FACING, rotation.rotate(state.getValue(FACING)));
    }

    @Override
    protected BlockState mirror(BlockState state, Mirror mirror) {
        return state.rotate(mirror.getRotation(state.getValue(FACING)));
    }
}
