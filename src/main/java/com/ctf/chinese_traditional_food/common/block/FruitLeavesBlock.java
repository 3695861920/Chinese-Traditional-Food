package com.ctf.chinese_traditional_food.common.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.ParticleUtils;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

/**
 * 果树的树叶。
 *
 * <h2>它几乎没有逻辑</h2>
 * "离树干太远就枯萎"（{@code distance} 属性）、"剪刀能整块剪下来"、
 * "下雨会滴水"都在原版 {@link LeavesBlock} 里。我们需要的只是
 * **一种果子一套树叶** —— 因为掉落表挂在方块身上：
 *
 * <pre>
 *   梨树叶 → 10% 掉梨树苗 + 10% 掉梨
 *   桃树叶 → 10% 掉桃树苗 + 10% 掉桃
 * </pre>
 *
 * 如果所有果树共用一种树叶，就没法知道该掉哪种果子
 * （除非再引入方块实体或方块状态，那更重）。
 *
 * <h2>为什么必须写 {@code spawnFallingLeavesParticle}</h2>
 * 原版把它声明成 {@code protected abstract}（因为"飘落叶"的粒子颜色
 * 每种树都不一样），子类非实现不可。这里照抄原版橡树的写法：
 * 用 {@code TINTED_LEAVES} 粒子、颜色取群系对该方块的着色 ——
 * 于是我们的果树落叶和周围的原版树一个观感。
 */
public class FruitLeavesBlock extends LeavesBlock {

    public static final MapCodec<FruitLeavesBlock> CODEC =
            simpleCodec(FruitLeavesBlock::new);

    /** 落叶颗粒概率。原版橡树 0.01、樱花 0.1，果树取中间偏小。 */
    private static final float PARTICLE_CHANCE = 0.05F;

    public FruitLeavesBlock(BlockBehaviour.Properties properties) {
        super(PARTICLE_CHANCE, properties);
    }

    @Override
    public MapCodec<? extends LeavesBlock> codec() {
        return CODEC;
    }

    @Override
    protected void spawnFallingLeavesParticle(Level level, BlockPos pos, RandomSource random) {
        ColorParticleOption particle = ColorParticleOption.create(
                ParticleTypes.TINTED_LEAVES, level.getClientLeafTintColor(pos));
        ParticleUtils.spawnParticleBelow(level, pos, random, particle);
    }
}
