package com.ctf.chinese_traditional_food.common.menu;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractHeatProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.block.entity.HeatSource;
import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

/**
 * 加工设备的界面容器：若干进料槽 + 1 个出料槽 + 玩家背包。
 *
 * <h2>为什么进料槽数量要由菜单类型定死</h2>
 * 原版的 {@code AbstractContainerMenu} 在<b>服务端与客户端各建一次</b>，
 * 两边的 {@code slots} 列表必须逐项对应。客户端建菜单时拿不到方块实体，
 * 所以"这台机器有几个槽"这件事<b>不能</b>由服务端说了算 ——
 * 否则客户端会少建几个槽，一放东西就错位 / 报错。
 *
 * <p>原版对箱子就是这么解决的：小箱子和大箱子是<b>两个 MenuType</b>。
 * 这里照做：</p>
 *
 * <ul>
 *   <li>{@code PROCESSOR} —— 1 个进料槽，电动磨粉机 / 脱壳机（含大型机）用；</li>
 *   <li>{@code COOKER} —— {@value AbstractHeatProcessorBlockEntity#INPUT_SLOTS}
 *       个进料槽，炒锅 / 蒸笼 / 汤锅用。</li>
 * </ul>
 *
 * <p>界面布局也跟着分两套：1 格是"左进右出"，多格是 2×2 原料区 + 右侧出料。</p>
 *
 * <p>服务端与客户端共用同一个类，靠构造参数区分：</p>
 * <ul>
 *   <li>服务端：传入真正的方块实体，槽位直接读写它的容器；</li>
 *   <li>客户端：传入一个同尺寸的空 {@link SimpleContainer} 与
 *       {@link SimpleContainerData}，由原版自动同步服务端数据进来。</li>
 * </ul>
 */
public class ProcessorMenu extends AbstractContainerMenu {

    /** 同步给界面的整数个数：进度、总耗时、动力数值、动力类型、当前加工的槽。 */
    private static final int DATA_COUNT = 5;

    /** 单进料口机器的槽位坐标。 */
    public static final int INPUT_X = 56;
    public static final int INPUT_Y = 35;
    public static final int OUTPUT_X = 116;
    public static final int OUTPUT_Y = 35;

    /** 多进料口机器（锅）的槽位坐标：2×2 原料区 + 右侧出料。 */
    public static final int GRID_INPUT_X = 44;
    public static final int GRID_INPUT_Y = 24;
    public static final int GRID_STEP = 22;
    public static final int GRID_OUTPUT_X = 122;
    public static final int GRID_OUTPUT_Y = 33;

    private final int inputSlots;
    private final int machineSlots;
    private final int playerInvStart;

    private final Container machine;
    private final ContainerData data;

    // ------------------------------------------------------------------
    // 服务端构造
    // ------------------------------------------------------------------

    /** 服务端：接一个真实的机器方块实体。 */
    public static ProcessorMenu forMachine(MenuType<?> type, int containerId,
                                           Inventory playerInventory,
                                           AbstractProcessorBlockEntity machine) {
        return new ProcessorMenu(type, containerId, playerInventory,
                machine.getInventory(), machine, machine.inputSlots());
    }

    // ------------------------------------------------------------------
    // 客户端构造
    // ------------------------------------------------------------------

    /** 客户端：只有类型与背包，槽位数量由菜单类型决定（见类注释）。 */
    public ProcessorMenu(MenuType<?> type, int containerId, Inventory playerInventory,
                         int inputSlots) {
        this(type, containerId, playerInventory,
                new SimpleContainer(inputSlots + 1), new SimpleContainerData(DATA_COUNT),
                inputSlots);
    }

    private ProcessorMenu(MenuType<?> type, int containerId, Inventory playerInventory,
                          Container machine, ContainerData data, int inputSlots) {
        super(type, containerId);
        this.inputSlots = inputSlots;
        this.machineSlots = inputSlots + 1;
        this.playerInvStart = this.machineSlots;
        checkContainerSize(machine, this.machineSlots);
        this.machine = machine;
        this.data = data;

        // ---- 进料槽 ----
        for (int i = 0; i < inputSlots; i++) {
            this.addSlot(new Slot(machine, i,
                    inputSlotX(i, inputSlots), inputSlotY(i, inputSlots)) {
                @Override
                public boolean mayPlace(ItemStack stack) {
                    return !stack.isEmpty();
                }
            });
        }
        // ---- 出料槽：只出不进 ----
        this.addSlot(new Slot(machine, inputSlots,
                outputX(inputSlots), outputY(inputSlots)) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return false;
            }
        });

        // ---- 玩家背包 ----
        this.addStandardInventorySlots(playerInventory, 8, 84);
        this.addDataSlots(data);
    }

    // ------------------------------------------------------------------
    // 槽位坐标：1 个进料口与多个进料口用两套排布
    // ------------------------------------------------------------------

    /** 进料槽的横坐标。 */
    public static int inputSlotX(int index, int inputSlots) {
        if (inputSlots <= 1) {
            return INPUT_X;
        }
        return GRID_INPUT_X + (index % 2) * GRID_STEP;
    }

    /** 进料槽的纵坐标。 */
    public static int inputSlotY(int index, int inputSlots) {
        if (inputSlots <= 1) {
            return INPUT_Y;
        }
        return GRID_INPUT_Y + (index / 2) * GRID_STEP;
    }

    /** 出料槽的横坐标。 */
    public static int outputX(int inputSlots) {
        return inputSlots <= 1 ? OUTPUT_X : GRID_OUTPUT_X;
    }

    /** 出料槽的纵坐标。 */
    public static int outputY(int inputSlots) {
        return inputSlots <= 1 ? OUTPUT_Y : GRID_OUTPUT_Y;
    }

    /** 这个菜单服务几格进料口（客户端也是准的，由菜单类型决定）。 */
    public int inputSlots() {
        return this.inputSlots;
    }

    /** 出料槽在菜单里的下标（也是机器容器里的下标）。 */
    public int outputSlot() {
        return this.inputSlots;
    }

    // ------------------------------------------------------------------
    // 界面要用的读取口
    // ------------------------------------------------------------------

    public int getProgress() {
        int max = this.data.get(1);
        int now = this.data.get(0);
        return max <= 0 ? 0 : Math.min(now, max);
    }

    public int getMaxProgress() {
        return Math.max(1, this.data.get(1));
    }

    /** 进度条填充比例 0~1。 */
    public float getProgressRatio() {
        int max = this.data.get(1);
        if (max <= 0) {
            return 0.0F;
        }
        return Math.min(1.0F, this.data.get(0) / (float) max);
    }

    /**
     * 现在正在加工第几个进料槽 —— 界面把那一格框出来，
     * 玩家就知道"刚放的东西到底轮到没有"。
     */
    public int getActiveSlot() {
        return Math.max(0, Math.min(this.inputSlots - 1, this.data.get(4)));
    }

    /** 当前动力数值（电动设备是 FE，灶上锅具是热度）。 */
    public int getEnergy() {
        return this.data.get(2);
    }

    public int getEnergyCapacity() {
        // 灶上锅具走的是"有火 / 没火"，满值就是热度上限；电动设备是 FE 缓冲。
        return this.isHeatPowered()
                ? HeatSource.HEAT_CAPACITY
                : MachineEnergy.MACHINE_BUFFER;
    }

    /** 动力条填充比例 0~1。 */
    public float getEnergyRatio() {
        int cap = this.getEnergyCapacity();
        return cap <= 0 ? 0.0F : Math.min(1.0F, this.getEnergy() / (float) cap);
    }

    /** 有没有动力 —— 用来决定要不要提示"接台发电机 / 垫个电磁炉"。 */
    public boolean hasEnergy() {
        return this.data.get(2) > 0;
    }

    /** 这台机器吃的是热力（灶上锅具）还是电（电动设备）—— 只影响界面文案。 */
    public boolean isHeatPowered() {
        return this.data.get(3) > 0;
    }

    // ------------------------------------------------------------------
    // AbstractContainerMenu
    // ------------------------------------------------------------------

    @Override
    public boolean stillValid(Player player) {
        return this.machine.stillValid(player);
    }

    @Override
    public ItemStack quickMoveStack(Player player, int slotIndex) {
        Slot slot = this.slots.get(slotIndex);
        if (slot == null || !slot.hasItem()) {
            return ItemStack.EMPTY;
        }

        ItemStack raw = slot.getItem();
        ItemStack moved = raw.copy();

        if (slotIndex < this.machineSlots) {
            // 机器 -> 玩家背包
            if (!this.moveItemStackTo(raw, this.playerInvStart, this.slots.size(), true)) {
                return ItemStack.EMPTY;
            }
        } else {
            // 玩家背包 -> 进料槽（出料槽拒绝放入，所以不会误塞）
            if (!this.moveItemStackTo(raw, 0, this.inputSlots, false)) {
                return ItemStack.EMPTY;
            }
        }

        if (raw.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        return moved;
    }
}
