package com.ctf.chinese_traditional_food.common.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * 大型机器的<b>部件</b>方块（水磨的石台 / 水轮 / 传动箱，脱壳机的木架 / 机箱板 / 立柱 / 料斗）。
 *
 * <h2>三个属性就够用</h2>
 * {@link #DX} / {@link #DY} / {@link #DZ} 记录这一格<b>相对核心的偏移</b>
 * （属性值 0~2，实际偏移 = 值 - 1）。于是：
 *
 * <ul>
 *   <li>部件能自己算出核心在哪：{@code 核心 = 部件位置 - 偏移} ——
 *       不需要方块实体，也不需要额外的 ID 同步；</li>
 *   <li>这三个值同时决定了用哪个模型（同一格的外观），一举两得；</li>
 *   <li>结构表里没列出的偏移组合根本没有方块状态，
 *       所以也不可能被"放到不该在的地方"。</li>
 * </ul>
 *
 * <p>部件本身不存任何东西：机器的数据全在核心的方块实体里，
 * 所以这些方块零存档负担、也不消耗 tick。</p>
 */
public class MachinePartBlock extends Block {
    /**
     * 三个偏移属性。取值范围 0~3，对应实际偏移 -1~2（值 = 偏移 + 1）。
     *
     * <p>范围要比结构需要的大一格：水平方向要能表达 -1~1（机器两侧对称），
     * 竖直方向要能表达 0~2（核心在底层、机器只向上长）。
     * 虽然 4³=64 种组合里实际只用得到十几个，但属性范围必须覆盖它们，
     * 否则结构表里合法的格子会因为“超出属性范围”而整个 blockstate 解析失败。</p>
     */
    public static final IntegerProperty DX = IntegerProperty.create("dx", 0, 3);
    public static final IntegerProperty DY = IntegerProperty.create("dy", 0, 3);
    public static final IntegerProperty DZ = IntegerProperty.create("dz", 0, 3);

    public MachinePartBlock(Properties properties) {
        super(properties);
        // 默认取正中的偏移（1,1,1 -> 偏移 0,0,0），只影响"凭空出现"的极端情况
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(DX, 1).setValue(DY, 1).setValue(DZ, 1));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(DX, DY, DZ);
    }

    /** 由偏移反推核心位置。 */
    public static BlockPos corePos(BlockState state, BlockPos pos) {
        return pos.offset(1 - state.getValue(DX), 1 - state.getValue(DY), 1 - state.getValue(DZ));
    }

    /** 机器的一部分不该被活塞推走（推走就散架了）。 */
    @Override
    public PushReaction getPistonPushReaction(BlockState state) {
        return PushReaction.BLOCK;
    }

    // ------------------------------------------------------------------
    // 手动补零件
    // ------------------------------------------------------------------

    /**
     * 玩家手动放部件时，就近找一个核心并算出自己该在哪一格。
     *
     * <p>这样机器缺一块时可以直接拿同样的部件补上去，不用拆了重放。
     * 附近没有核心就<b>不给放</b> —— 免得零件满世界都是。</p>
     */
    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();
        for (BlockPos core : BlockPos.betweenClosed(pos.offset(-1, -1, -1), pos.offset(1, 1, 1))) {
            if (level.getBlockState(core).getBlock() instanceof AbstractMachineCoreBlock machine
                    && machine.partBlock() == this) {
                int dx = pos.getX() - core.getX();
                int dy = pos.getY() - core.getY();
                int dz = pos.getZ() - core.getZ();
                // 必须真的是这台机器的一格：结构表里没列出的偏移根本没有
                // 对应的方块状态，放下去会变成一个没有模型的方块。
                if (!machine.hasPartAt(dx, dy, dz)) {
                    continue;
                }
                return this.defaultBlockState()
                        .setValue(DX, dx + 1)
                        .setValue(DY, dy + 1)
                        .setValue(DZ, dz + 1);
            }
        }
        return null;
    }

    /** 放好之后让核心重新校验 —— 机器可能就此恢复了。 */
    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState,
                        boolean movedByPiston) {
        super.onPlace(state, level, pos, oldState, movedByPiston);
        if (level.isClientSide()) {
            return;
        }
        this.notifyCore(level, state, pos);
    }

    /** 拆掉之后同样要让核心知道"我缺了一块"。 */
    @Override
    protected void affectNeighborsAfterRemoval(BlockState state, ServerLevel level, BlockPos pos,
                                               boolean movedByPiston) {
        // 拆掉任意一块部件 = 拆掉整台机器。
        // 这是用户明确要的：机器是一体的，拆一块就整个散掉，零件全部掉出来。
        // 没有核心的话（比如结构表里没列出的格子）就什么都不做。
        BlockPos core = corePos(state, pos);
        if (level.getBlockState(core).getBlock() instanceof AbstractMachineCoreBlock machine) {
            machine.tearDown(level, core);
        }
        super.affectNeighborsAfterRemoval(state, level, pos, movedByPiston);
    }

    private void notifyCore(Level level, BlockState state, BlockPos pos) {
        BlockPos core = corePos(state, pos);
        if (level.getBlockState(core).getBlock() instanceof AbstractMachineCoreBlock machine) {
            machine.revalidate(level, core);
        }
    }

    // ------------------------------------------------------------------
    // 交互转发
    // ------------------------------------------------------------------

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos,
                                          Player player, InteractionHand hand, BlockHitResult hit) {
        if (stack.isEmpty()) {
            // 空手交给 useWithoutItem（否则默认会吃掉这次右键）
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        AbstractMachineCoreBlock machine = coreAt(level, state, pos);
        if (machine == null) {
            return InteractionResult.PASS;
        }
        return machine.usePart(stack, level, corePos(state, pos), player, hand);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        AbstractMachineCoreBlock machine = coreAt(level, state, pos);
        if (machine == null) {
            return InteractionResult.PASS;
        }
        return machine.usePartWithoutItem(level, corePos(state, pos), player);
    }

    @Nullable
    private static AbstractMachineCoreBlock coreAt(Level level, BlockState state, BlockPos pos) {
        return level.getBlockState(corePos(state, pos)).getBlock() instanceof AbstractMachineCoreBlock m
                ? m : null;
    }

    /** 部件不会单独掉落（没有战利品表），但保留这个常量方便注册时对照。 */
    public static Direction partFacing() {
        return Direction.NORTH;
    }
}
