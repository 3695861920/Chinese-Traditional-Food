package com.ctf.chinese_traditional_food.common.block;

import java.util.List;

/**
 * 大型多方块机器的结构表。
 *
 * <p><b>本文件由 {@code tools/machine_models.py} 生成，请不要手改。</b>
 * 要调整机器形状请改那个脚本里的 {@code water_mill_parts()} /
 * {@code sheller_parts()}，模型、方块状态、结构表会一起同步。</p>
 *
 * <h2>为什么用"相对核心的偏移"描述结构</h2>
 * 每个部件方块都带 {@code dx/dy/dz} 三个属性记录它相对核心的偏移，
 * 所以部件能自己算出核心在哪（{@code 核心 = 部件位置 - 偏移}），
 * 不需要方块实体、不需要 ID 同步，两台机器挨着也不会串。
 *
 * <p>偏移范围是 -1~2，方块状态里编码成 0~3（值 = 偏移 + 1）。
 * 核心一律在结构最底层（{@code dy >= 0}），因为放置时下方是实地，
 * 结构往地下延伸就放不下来了。</p>
 */
public final class MachineStructure {

    /**
     * 结构中的一格。
     *
     * @param dx 相对核心的 X 偏移（-1 ~ 2）
     * @param dy 相对核心的 Y 偏移（0 ~ 2）
     * @param dz 相对核心的 Z 偏移（-1 ~ 2）
     */
    public record Part(int dx, int dy, int dz) {
        public int encodedX() {
            return this.dx + 1;
        }

        public int encodedY() {
            return this.dy + 1;
        }

        public int encodedZ() {
            return this.dz + 1;
        }
    }

    /** water_mill 的全部部件位置（不含核心自身）。 */
    public static final List<Part> WATER_MILL = List.of(
            new Part(-1, 0, -1),
            new Part(0, 0, -1),
            new Part(1, 0, -1),
            new Part(-1, 0, 0),
            new Part(1, 0, 0),
            new Part(-1, 0, 1),
            new Part(0, 0, 1),
            new Part(1, 0, 1),
            new Part(-1, 1, -1),
            new Part(0, 1, -1),
            new Part(1, 1, -1),
            new Part(-1, 1, 0),
            new Part(1, 1, 0),
            new Part(-1, 1, 1),
            new Part(0, 1, 1),
            new Part(1, 1, 1),
            new Part(0, 2, 0)
    );

    /** grain_sheller 的全部部件位置（不含核心自身）。 */
    public static final List<Part> GRAIN_SHELLER = List.of(
            new Part(-1, 0, -1),
            new Part(0, 0, -1),
            new Part(1, 0, -1),
            new Part(-1, 0, 0),
            new Part(1, 0, 0),
            new Part(-1, 0, 1),
            new Part(0, 0, 1),
            new Part(1, 0, 1),
            new Part(-1, 1, -1),
            new Part(0, 1, -1),
            new Part(1, 1, -1),
            new Part(-1, 1, 0),
            new Part(1, 1, 0),
            new Part(-1, 1, 1),
            new Part(0, 1, 1),
            new Part(1, 1, 1),
            new Part(0, 2, 0)
    );

    private MachineStructure() {}
}
