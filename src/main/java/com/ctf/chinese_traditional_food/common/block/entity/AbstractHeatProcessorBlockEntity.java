package com.ctf.chinese_traditional_food.common.block.entity;

import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes.Kind;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * 「锅」的公共方块实体：炒锅 / 蒸笼 / 汤锅。
 *
 * <h2>动力来自下面的电磁炉</h2>
 * 锅本身不耗电：{@link #hasPower()} 覆写成"正下方有热源"，
 * {@link #consumePower()} 是空实现（电是电磁炉吃掉的）。
 * 于是主循环（推进度、结算批次）一行都不用重写。
 *
 * <h2>九个原料槽 + 多材料锅谱</h2>
 * 一口锅备着九样东西才顺手 —— 三份配菜的料往槽里一塞，
 * 它会自己一道一道做下去，不用守在旁边一遍遍开界面。
 *
 * <p>每道菜要的材料不一样（见 {@code ModRecipes.WOK / STEAMER / SOUP_POT}），
 * 所以这里把父类的"一样进一样出"调度换成<b>凑料</b>：</p>
 *
 * <ol>
 *   <li>在一堆槽位里找一道<b>材料齐了</b>的菜（{@link ProcessRecipes#findCook}）；</li>
 *   <li>凑齐了就开火，进度走完 <b>每样材料各扣一份</b>、产出一份；</li>
 *   <li>同一种材料槽里放好几份，就能连着做好几道 —— 不必一次只放一份。</li>
 * </ol>
 *
 * <p>一次只做一道（{@link #batchSize()} 固定 1）：锅谱要凑材料，
 * 一次做多份很难说清"该扣哪几格"。</p>
 *
 * <h2>界面</h2>
 * 那根竖条在电动设备上是电量，在这里是<b>热度</b>：有火就是满的。
 * 布局也换成九格版（见 {@code ProcessorMenu.COOKER} 与 {@code ProcessorScreen}）。
 */
public abstract class AbstractHeatProcessorBlockEntity extends AbstractProcessorBlockEntity {

    /** 灶上锅具的进料槽数量。九格 = 3×3，界面里正好排成方阵。 */
    public static final int INPUT_SLOTS = 9;

    protected AbstractHeatProcessorBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    /** 这一台是哪一类灶活。 */
    @Override
    protected abstract Kind kind();

    /** 九个进料槽（见类注释）。 */
    @Override
    public int inputSlots() {
        return INPUT_SLOTS;
    }

    /** 一次做一道菜。 */
    @Override
    protected int batchSize() {
        return 1;
    }

    // ------------------------------------------------------------------
    // 与电动设备不同的数值
    // ------------------------------------------------------------------

    /**
     * 灶具内部**不存电**。
     *
     * <p>容量给 0 之后 {@code Capabilities.Energy} 也不会挂上去（见
     * {@code ModCapabilities}），所以漏斗和管道不会往里灌电 ——
     * 免得出现"插根线就能免费炒菜"这种漏洞。</p>
     */
    @Override
    protected int machineBuffer() {
        return 0;
    }

    @Override
    protected int ioRate() {
        return 0;
    }

    // ------------------------------------------------------------------
    // 动力：来自下面的热源
    // ------------------------------------------------------------------

    @Override
    protected boolean hasPower() {
        if (this.level == null) {
            return false;
        }
        HeatSource source = HeatSource.below(this.level, this.worldPosition);
        return source != null && source.heat() >= HeatSource.HEAT_WORKING;
    }

    /** 不扣任何东西 —— 电由下面的电磁炉吃。 */
    @Override
    protected void consumePower() {
        // 有意留空
    }

    /** 界面那根竖条：有火就是满的。 */
    @Override
    public int getPowerForDisplay() {
        return this.hasPower() ? HeatSource.HEAT_CAPACITY : 0;
    }

    @Override
    public int getPowerCapacityForDisplay() {
        return HeatSource.HEAT_CAPACITY;
    }

    @Override
    public boolean heatPowered() {
        return true;
    }

    // ------------------------------------------------------------------
    // 厨具的调度：凑料
    // ------------------------------------------------------------------

    /** 锅里有没有活等着做。电磁炉靠这个决定要不要供电。 */
    public boolean wantsHeat() {
        return this.hasWork();
    }

    /** 把槽位拷一份成列表，交给锅谱做匹配（锅谱不该直接碰容器）。 */
    private List<ItemStack> slotSnapshot() {
        List<ItemStack> out = new ArrayList<>(this.inputSlots());
        for (int i = 0; i < this.inputSlots(); i++) {
            out.add(this.getInventory().getItem(i));
        }
        return out;
    }

    /** 现在能不能凑出一道菜。 */
    @Override
    protected int plannedBatchSize() {
        ProcessRecipes.Cook cook = this.currentCook();
        if (cook == null) {
            return 0;
        }
        // 出料口塞不下就别开火
        return this.outputRoom(cook.result()) > 0 ? 1 : 0;
    }

    /** 这一批要多久 —— 直接取锅谱里写的 tick（每道菜不一样）。 */
    @Override
    protected int batchTicks() {
        ProcessRecipes.Cook cook = this.currentCook();
        return cook != null ? cook.ticks() : super.batchTicks();
    }

    /** 当前匹配到的锅谱；凑不出菜就是 {@code null}。 */
    @Nullable
    protected ProcessRecipes.Cook currentCook() {
        return ProcessRecipes.findCook(this.kind(), this.slotSnapshot());
    }

    /**
     * 高亮哪一格：当前这道菜用到的**第一个**材料所在的位置。
     *
     * <p>只影响界面高亮与"换槽重置进度"。因为材料是在批次结束时才扣的，
     * 所以一整批里这个值不会自己变。</p>
     */
    @Override
    protected int activeInputSlot() {
        ProcessRecipes.Cook cook = this.currentCook();
        if (cook == null) {
            return FIRST_INPUT_SLOT;
        }
        for (int slot = 0; slot < this.inputSlots(); slot++) {
            ItemStack stack = this.getInventory().getItem(slot);
            if (stack.isEmpty()) {
                continue;
            }
            for (ProcessRecipes.Resolved need : cook.ingredients()) {
                if (need.matches(stack)) {
                    return slot;
                }
            }
        }
        return FIRST_INPUT_SLOT;
    }

    /**
     * 结算一道菜：每样材料各扣一份，产出一份。
     *
     * <p>这里刻意**重新匹配一次**而不是缓存上一 tick 的结果：
     * 缓存会在"玩家中途把材料拿走"时留下脏状态；重新匹配最多让这批白做
     * （进度归零），绝不会扣错东西。</p>
     */
    @Override
    protected void finishBatch(int count) {
        if (count <= 0) {
            return;
        }
        ProcessRecipes.Cook cook = this.currentCook();
        if (cook == null || this.outputRoom(cook.result()) <= 0) {
            return;
        }

        // 逐样材料扣一份：同一种要两份的（腊八蒜）会走两遍
        for (ProcessRecipes.Resolved need : cook.ingredients()) {
            if (!this.consumeOne(need)) {
                return;     // 材料在结算前被拿走了 —— 这批作废，不产出
            }
        }
        this.putResult(cook.result().copy());
    }

    /** 从槽里扣掉一份匹配这种东西的材料。 */
    private boolean consumeOne(ProcessRecipes.Resolved need) {
        for (int slot = 0; slot < this.inputSlots(); slot++) {
            ItemStack stack = this.getInventory().getItem(slot);
            if (stack.isEmpty() || !need.matches(stack)) {
                continue;
            }
            stack.shrink(1);
            if (stack.isEmpty()) {
                this.getInventory().setItem(slot, ItemStack.EMPTY);
            } else {
                this.getInventory().setChanged();
            }
            return true;
        }
        return false;
    }
}
