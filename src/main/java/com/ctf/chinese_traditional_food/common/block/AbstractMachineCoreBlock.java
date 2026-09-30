package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.common.block.MachineStructure.Part;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.redstone.Orientation;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

/**
 * 「一体成型的大型机器」的核心方块。
 *
 * <h2>为什么要有这一层</h2>
 * 水磨和脱壳机在现实里都不是一个方块装得下的东西：一个要有水轮、传动轴、
 * 磨盘和石台，另一个要有木架、机箱、摇柄和上面的料斗。所以它们被做成
 * <b>3×3×3 的多方块结构</b>，而玩家只需要放<b>一个核心方块</b>：
 *
 * <ul>
 *   <li>放置时先检查所有部件格子都是可替换的，放不下就直接<b>不许放</b>
 *       （避免"放出来半台机器"这种半残状态）；</li>
 *   <li>放下以后自动把整台机器展开 —— 这就是"一体成型"；</li>
 *   <li>拆掉任意一个部件只会让机器<b>失效</b>（核心换成"未成形"外观），
 *       补上就恢复，不会连坐炸掉；</li>
 *   <li>拆掉核心则整台机器一起收走。</li>
 * </ul>
 *
 * <h2>部件怎么找核心</h2>
 * 不靠方块实体、不靠 ID 同步：每个部件自己带 {@code dx/dy/dz} 三个属性，
 * 记录它相对核心的偏移，于是 {@code 核心 = 部件位置 - 偏移}。
 * 两台机器挨着也绝不会串到对方身上。
 *
 * @see MachineStructure 结构表（由 {@code tools/machine_models.py} 生成）
 */
public abstract class AbstractMachineCoreBlock extends Block implements EntityBlock {
    /** 结构是否完整。不完整时机器不工作，并且换成"缺零件"的外观。 */
    public static final BooleanProperty FORMED = BooleanProperty.create("formed");

    protected AbstractMachineCoreBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(FORMED, false));
    }

    /** 这台机器的全部部件位置（不含核心自身）。 */
    protected abstract List<Part> structureParts();

    /** 构成这台机器的部件方块。 */
    protected abstract Block partBlock();

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FORMED);
    }

    // ------------------------------------------------------------------
    // 放置：空间不够就不许放
    // ------------------------------------------------------------------

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        if (!this.hasRoomFor(context.getLevel(), context.getClickedPos())) {
            return null;
        }
        return this.defaultBlockState();
    }

    /** 所有部件格子是不是都能被替换（空气 / 草 / 雪之类）。 */
    public boolean hasRoomFor(BlockGetter level, BlockPos core) {
        for (Part part : this.structureParts()) {
            BlockPos p = core.offset(part.dx(), part.dy(), part.dz());
            if (!level.getBlockState(p).canBeReplaced()) {
                return false;
            }
        }
        return true;
    }

    @Override
    public void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState,
                        boolean movedByPiston) {
        super.onPlace(state, level, pos, oldState, movedByPiston);
        if (level.isClientSide()) {
            return;
        }
        this.expand(level, pos);
    }

    /**
     * 展开（或补全）整台机器。
     *
     * <p>已经在正确位置上的部件会跳过，所以对一台完整的机器再调一次
     * 等价于什么都没做 —— 这也让"重新放一次核心来修机器"成为可能。</p>
     *
     * @return 是否全部就位
     */
    public boolean expand(Level level, BlockPos core) {
        for (Part part : this.structureParts()) {
            BlockPos p = core.offset(part.dx(), part.dy(), part.dz());
            BlockState wanted = this.partState(part);
            BlockState existing = level.getBlockState(p);
            // BlockState 是方块与属性组合的单例，所以引用相等就代表"已经在位"
            if (existing == wanted) {
                continue;
            }
            // 只有原本可替换（或是本机器的部件）才允许覆盖，绝不吃掉玩家的建筑
            if (!existing.canBeReplaced() && !existing.is(this.partBlock())) {
                return false;
            }
            level.setBlock(p, wanted, Block.UPDATE_ALL);
        }
        this.setFormed(level, core, true);
        return true;
    }

    /** 把某个偏移对应的部件方块状态拼出来。 */
    protected BlockState partState(Part part) {
        return this.partBlock().defaultBlockState()
                .setValue(MachinePartBlock.DX, part.encodedX())
                .setValue(MachinePartBlock.DY, part.encodedY())
                .setValue(MachinePartBlock.DZ, part.encodedZ());
    }

    // ------------------------------------------------------------------
    // 结构完整性
    // ------------------------------------------------------------------

    /** 这个偏移是不是本机器结构的一部分。 */
    public boolean hasPartAt(int dx, int dy, int dz) {
        for (Part part : this.structureParts()) {
            if (part.dx() == dx && part.dy() == dy && part.dz() == dz) {
                return true;
            }
        }
        return false;
    }

    /** 逐格检查部件都在、而且都是属于<b>本核心</b>的。 */
    public boolean isComplete(BlockGetter level, BlockPos core) {
        for (Part part : this.structureParts()) {
            BlockPos p = core.offset(part.dx(), part.dy(), part.dz());
            BlockState state = level.getBlockState(p);
            if (!state.is(this.partBlock())) {
                return false;
            }
            // 偏移不同的部件会指向不同的核心，所以这一条也顺带校验了 dx/dy/dz
            if (!MachinePartBlock.corePos(state, p).equals(core)) {
                return false;
            }
        }
        return true;
    }

    /** 重新校验并刷新 {@link #FORMED}。 */
    public void revalidate(Level level, BlockPos core) {
        BlockState state = level.getBlockState(core);
        if (!state.is(this)) {
            return;
        }
        boolean complete = this.isComplete(level, core);
        if (state.getValue(FORMED) != complete) {
            this.setFormed(level, core, complete);
        }
    }

    private void setFormed(Level level, BlockPos core, boolean formed) {
        BlockState state = level.getBlockState(core);
        if (state.is(this) && state.getValue(FORMED) != formed) {
            // 只更新客户端：这纯粹是外观，不牵动任何逻辑
            level.setBlock(core, state.setValue(FORMED, formed), Block.UPDATE_CLIENTS);
        }
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock,
                                   @Nullable Orientation orientation, boolean movedByPiston) {
        super.neighborChanged(state, level, pos, neighborBlock, orientation, movedByPiston);
        if (!level.isClientSide()) {
            this.revalidate(level, pos);
        }
    }

    /** 核心被拆：把整台机器一起收走。 */
    @Override
    protected void affectNeighborsAfterRemoval(BlockState state, ServerLevel level, BlockPos pos,
                                               boolean movedByPiston) {
        this.tearDown(level, pos);
        super.affectNeighborsAfterRemoval(state, level, pos, movedByPiston);
    }

    /**
     * 正在拆除的机器（以核心位置为键）。
     *
     * <p>拆整机时会对每一格调 {@code destroyBlock}，而那些格子又会各自触发
     * 自己的移除回调 —— 不加保护就会互相递归，直接把栈打爆。
     * 所以拆之前先把核心位置登记进来，重入时直接返回。</p>
     *
     * <p>用 {@link ThreadLocal} 是因为方块拆除只发生在服务端线程；
     * 即便将来有并行，也不会把两个线程搞混。</p>
     */
    private static final ThreadLocal<java.util.Set<BlockPos>> TEARING_DOWN =
            ThreadLocal.withInitial(java.util.HashSet::new);

    /** 这台机器是不是正在被拆。 */
    public static boolean isTearingDown(BlockPos core) {
        return TEARING_DOWN.get().contains(core);
    }

    /**
     * 拆掉整台机器，每一格都按正常掉落走。
     *
     * <p>触发时机：核心被拆、或<b>任意一个部件被拆</b>。
     * 用户要的就是"拆一块就整个散掉"，而不是留着半台残骸。</p>
     *
     * @return 是否真的执行了拆除（重入时返回 {@code false}）
     */
    public boolean tearDown(Level level, BlockPos core) {
        java.util.Set<BlockPos> guard = TEARING_DOWN.get();
        if (!guard.add(core)) {
            return false;                  // 已经在拆了，避免递归
        }
        try {
            // 先拆部件，再拆核心：这样拆到每格时核心还在，
            // 别人看起来就是"一台机器整体崩掉"。
            for (Part part : this.structureParts()) {
                BlockPos p = core.offset(part.dx(), part.dy(), part.dz());
                BlockState at = level.getBlockState(p);
                if (at.is(this.partBlock())
                        && MachinePartBlock.corePos(at, p).equals(core)) {
                    level.destroyBlock(p, true);       // true = 掉落战利品
                }
            }
            if (level.getBlockState(core).is(this)) {
                level.destroyBlock(core, true);
            }
        } finally {
            guard.remove(core);
        }
        return true;
    }

    // ------------------------------------------------------------------
    // 把部件的交互转给核心
    // ------------------------------------------------------------------

    /**
     * 部件被右键时由 {@link MachinePartBlock} 调用。
     *
     * <p>这里伪造一个"点在核心顶面"的 {@link BlockHitResult} 再走一遍正常流程 ——
     * 机器变大之后玩家会习惯性地对着机身操作，让每个部件都能用才顺手。</p>
     */
    public InteractionResult usePart(ItemStack stack, Level level, BlockPos corePos,
                                     Player player, InteractionHand hand) {
        BlockState coreState = level.getBlockState(corePos);
        if (!coreState.is(this)) {
            return InteractionResult.PASS;
        }
        return this.useItemOn(stack, coreState, level, corePos, player, hand, hitAt(corePos));
    }

    /** 同 {@link #usePart}，但对应"空手右键"。 */
    public InteractionResult usePartWithoutItem(Level level, BlockPos corePos, Player player) {
        BlockState coreState = level.getBlockState(corePos);
        if (!coreState.is(this)) {
            return InteractionResult.PASS;
        }
        return this.useWithoutItem(coreState, level, corePos, player, hitAt(corePos));
    }

    private static BlockHitResult hitAt(BlockPos corePos) {
        return new BlockHitResult(Vec3.atCenterOf(corePos), Direction.UP, corePos, false);
    }

    /** 机器没成形时给玩家一句提示（子类在动手前调用）。 */
    protected static void warnIncomplete(Player player) {
        player.sendOverlayMessage(
                net.minecraft.network.chat.Component.translatable(
                        "tooltip.chinese_traditional_food.machine_incomplete"));
    }
}
