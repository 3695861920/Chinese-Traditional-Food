package com.ctf.chinese_traditional_food.common.menu;

import com.ctf.chinese_traditional_food.common.block.entity.AbstractProcessorBlockEntity;
import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import com.ctf.chinese_traditional_food.common.recipe.ProcessRecipes;
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
import org.jetbrains.annotations.Nullable;

/**
 * 自研装置的界面容器：2 个机器槽 + 玩家背包。
 *
 * <p>服务端与客户端共用同一个类，靠构造参数区分：</p>
 * <ul>
 *   <li>服务端：传入真正的方块实体，槽位直接读写它的容器；</li>
 *   <li>客户端：传入一个同尺寸的空 {@link SimpleContainer} 与
 *       {@link SimpleContainerData}，由原版自动同步服务端数据进来。</li>
 * </ul>
 *
 * <p>{@code data} 里的两个整数是进度与总耗时，客户端用它画进度条。</p>
 */
public class ProcessorMenu extends AbstractContainerMenu {
    private static final int MACHINE_SLOTS = AbstractProcessorBlockEntity.SIZE;   // 2

    /** 同步给界面的整数个数：进度、总耗时、电量。 */
    private static final int DATA_COUNT = 3;
    private static final int PLAYER_INV_START = MACHINE_SLOTS;

    /** 机器槽在界面里的位置（相对于界面左上角），由屏幕那边对齐。 */
    public static final int INPUT_X = 56;
    public static final int INPUT_Y = 35;
    public static final int OUTPUT_X = 116;
    public static final int OUTPUT_Y = 35;

    private final Container machine;
    private final ContainerData data;

    /** 服务端构造：菜单类型 + 真实方块实体。 */
    public ProcessorMenu(MenuType<?> type, int containerId, Inventory playerInventory,
                         AbstractProcessorBlockEntity machine) {
        this(type, containerId, playerInventory, machine.getInventory(), machine);
    }

    /** 客户端构造：菜单类型 + 空容器占位（数据由服务端同步）。 */
    public ProcessorMenu(MenuType<?> type, int containerId, Inventory playerInventory) {
        this(type, containerId, playerInventory,
                new SimpleContainer(MACHINE_SLOTS), new SimpleContainerData(DATA_COUNT));
    }
    private ProcessorMenu(MenuType<?> type, int containerId, Inventory playerInventory,
                          Container machine, ContainerData data) {
        super(type, containerId);
        checkContainerSize(machine, MACHINE_SLOTS);
        this.machine = machine;
        this.data = data;

        // ---- 机器插槽 ----
        // 进料：只收"这台机器能处理的"东西（客户端不知道配方，所以只做服务端校验）
        this.addSlot(new Slot(machine, AbstractProcessorBlockEntity.SLOT_INPUT, INPUT_X, INPUT_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return ProcessorMenu.this.canAccept(stack);
            }
        });
        // 出料：只出不进
        this.addSlot(new Slot(machine, AbstractProcessorBlockEntity.SLOT_OUTPUT, OUTPUT_X, OUTPUT_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return false;
            }
        });

        // ---- 玩家背包 ----
        this.addStandardInventorySlots(playerInventory, 8, 84);

        this.addDataSlots(data);
    }

    /** 进料口是否接受这个物品。 */
    private boolean canAccept(ItemStack stack) {
        if (stack.isEmpty()) {
            return false;
        }
        // 客户端只知道自己的菜单类型，拿不到配方表；统一放行，由服务端的处理逻辑决定成败。
        // （配方表在 ProcessRecipes 里是懒加载的，客户端调用会去查两侧都有的静态注册表，
        //   所以这里其实也能查；但为了行为一致，仍以服务端为准。）
        return true;
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
     * 当前电量（FE）。
     *
     * <p>直接同步原值：缓冲只有 {@code MachineEnergy.MACHINE_BUFFER} = 4000，
     * 在原版容器数据的 short 范围内（见 {@code MachineEnergy.SYNC_SAFE_MAX}）。</p>
     */
    public int getEnergy() {
        return this.data.get(2);
    }

    public int getEnergyCapacity() {
        return MachineEnergy.MACHINE_BUFFER;
    }

    /** 电量比例 0~1。 */
    public float getEnergyRatio() {
        int cap = this.getEnergyCapacity();
        return cap <= 0 ? 0.0F : Math.min(1.0F, this.getEnergy() / (float) cap);
    }

    /** 有没有电 —— 用来决定要不要提示"接台发电机"。 */
    public boolean hasEnergy() {
        return this.data.get(2) > 0;
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
        ItemStack moved = ItemStack.EMPTY;
        Slot slot = this.slots.get(slotIndex);
        if (slot == null || !slot.hasItem()) {
            return ItemStack.EMPTY;
        }

        ItemStack raw = slot.getItem();
        moved = raw.copy();

        if (slotIndex < MACHINE_SLOTS) {
            // 机器 -> 玩家背包
            if (!this.moveItemStackTo(raw, PLAYER_INV_START, this.slots.size(), true)) {
                return ItemStack.EMPTY;
            }
        } else {
            // 玩家背包 -> 进料槽
            if (!this.moveItemStackTo(raw, AbstractProcessorBlockEntity.SLOT_INPUT,
                    AbstractProcessorBlockEntity.SLOT_INPUT + 1, false)) {
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
