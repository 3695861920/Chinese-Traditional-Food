package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.BonemealableBlock;
import net.minecraft.world.level.block.VegetationBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.IntegerProperty;

/**
 * 果树苗：种在地上，过一阵自己长成一棵会结果的树。
 *
 * <h2>为什么不用原版的 {@code SaplingBlock}</h2>
 * 原版树苗把"长成什么树"交给 {@code TreeGrower}，而它是去**世界生成注册表**里
 * 按 key 找一个 {@code ConfiguredFeature}。那意味着每种果树都要配一套
 * {@code worldgen/configured_feature/*.json} 再加 {@code placed_feature} ——
 * 十几个 JSON 只为描述"一根树干加一团树叶"。
 *
 * <p>这里直接继承 {@link VegetationBlock} 自己写生长逻辑：树形就三种，
 * 代码里二十行就够，而且**改树形不用重新生成数据包**。</p>
 *
 * <h2>为什么只存"果子名"而不是存方块引用</h2>
 * 长树时要放"本种果树的树叶"（掉落靠它区分是哪种果子）。直觉上可以在构造时
 * 把树叶的 {@code DeferredBlock} 存进来，但那会带来一个死结：
 *
 * <ul>
 *   <li>{@link VegetationBlock#codec()} 是**抽象**的 —— 方块必须有 codec，
 *       而 codec 要能把方块**从 JSON 还原出来**（数据包、结构方块、
 *       {@code /setblock} 都要用）。可 {@code DeferredBlock} 不是可序列化的东西；</li>
 *   <li>注册又是按顺序的：树苗注册时树叶可能还没注册。</li>
 * </ul>
 *
 * <p>所以改成只序列化**两个字符串**（果子名 + 树形），长树时再去
 * {@link BuiltInRegistries#BLOCK} 里按 id 取方块。这样 codec 干净、
 * 顺序无关，而且从 JSON 还原出来的实例一样能正常长树。</p>
 */
public class FruitSaplingBlock extends VegetationBlock implements BonemealableBlock {

    /** 和原版树苗一样有一个"是否被骨粉催过"的阶段位。 */
    public static final IntegerProperty STAGE = BlockStateProperties.STAGE;

    public static final MapCodec<FruitSaplingBlock> CODEC = RecordCodecBuilder.mapCodec(
            i -> i.group(
                    Codec.intRange(0, 2).fieldOf("size").forGetter(b -> b.size),
                    Codec.STRING.fieldOf("fruit").forGetter(b -> b.fruit),
                    propertiesCodec()
            ).apply(i, FruitSaplingBlock::new));

    private final int size;
    private final String fruit;

    public FruitSaplingBlock(int size, String fruit, BlockBehaviour.Properties properties) {
        super(properties);
        this.size = Math.max(0, Math.min(2, size));
        this.fruit = fruit;
        this.registerDefaultState(this.stateDefinition.any().setValue(STAGE, 0));
    }

    @Override
    protected MapCodec<? extends VegetationBlock> codec() {
        return CODEC;
    }

    private int trunkHeight() {
        return 4 + this.size;
    }

    private int crownRadius() {
        return this.size == 0 ? 2 : 3;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(STAGE);
    }

    // ------------------------------------------------------------------

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(BlockTags.DIRT)
                || state.is(Blocks.GRASS_BLOCK)
                || state.is(Blocks.FARMLAND)
                || state.is(Blocks.MOSS_BLOCK)
                || super.mayPlaceOn(state, level, pos);
    }

    @Override
    protected boolean isRandomlyTicking(BlockState state) {
        return true;
    }

    @Override
    protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        // 1/7 —— 和原版树苗一个节奏（平均约两分半钟；骨粉可以立刻催）
        if (random.nextInt(7) == 0) {
            this.grow(level, pos);
        }
    }

    @Override
    public boolean isValidBonemealTarget(LevelReader level, BlockPos pos, BlockState state) {
        return true;
    }

    @Override
    public boolean isBonemealSuccess(Level level, RandomSource random, BlockPos pos, BlockState state) {
        return level.getRandom().nextFloat() < 0.45F;
    }

    @Override
    public void performBonemeal(ServerLevel level, RandomSource random, BlockPos pos, BlockState state) {
        this.grow(level, pos);
    }

    /** 长成一棵树：一根树干 + 一团球形的树冠。 */
    private void grow(ServerLevel level, BlockPos pos) {
        int height = this.trunkHeight();
        if (pos.getY() + height + 3 > level.getMaxY()) {
            return;
        }
        BlockState up = level.getBlockState(pos.above());
        if (!up.isAir() && !up.canBeReplaced()) {
            return;      // 头顶被挡着，先别长（免得顶穿房子）
        }

        // 树干用**这棵树自己的**木头（`plum_log` / `jujube_log` …）。
        // 26.1 起每种果木各有一套原木/去皮/木板，由 ModWoods 注册。
        Block logBlock = BuiltInRegistries.BLOCK.getValue(
                ChineseTraditionalFood.id(this.fruit + "_log"));
        Block leavesBlock = BuiltInRegistries.BLOCK.getValue(
                ChineseTraditionalFood.id(this.fruit + "_leaves"));
        if (logBlock == null || leavesBlock == null) {
            ChineseTraditionalFood.LOGGER.warn(
                    "果树苗 %s 找不到配套的木头/树叶（%s_log / %s_leaves）",
                    this.fruit, this.fruit, this.fruit);
            return;
        }
        BlockState logState = logBlock.defaultBlockState();
        BlockState leafState = leavesBlock.defaultBlockState();

        // 树干
        for (int i = 0; i < height; i++) {
            level.setBlock(pos.above(i), logState, 3);
        }

        // 树冠：上下两层，中心半径大、往上收一格
        int r = this.crownRadius();
        int top = pos.getY() + height;
        for (int dy = -1; dy <= 1; dy++) {
            int layer = (dy == 1) ? r - 1 : r;
            for (int dx = -layer; dx <= layer; dx++) {
                for (int dz = -layer; dz <= layer; dz++) {
                    // 削角：让树冠是球而不是方盒子
                    if (Math.abs(dx) == layer && Math.abs(dz) == layer && layer > 1) {
                        continue;
                    }
                    if (dx * dx + dz * dz > layer * layer + 1) {
                        continue;
                    }
                    BlockPos p = new BlockPos(pos.getX() + dx, top + dy, pos.getZ() + dz);
                    BlockState there = level.getBlockState(p);
                    if (there.isAir() || there.canBeReplaced()) {
                        level.setBlock(p, leafState, 3);
                    }
                }
            }
        }
        level.setBlock(pos, Blocks.DIRT.defaultBlockState(), 3);
    }
}
