package com.ctf.chinese_traditional_food.common.menu;

import com.ctf.chinese_traditional_food.common.block.entity.FurnaceGeneratorBlockEntity;
import com.ctf.chinese_traditional_food.common.energy.MachineEnergy;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

/**
 * 熔炉发电机的界面容器：1 个燃料槽 + 玩家背包。
 *
 * <p>和 {@link ProcessorMenu} 同一套路：服务端传入真实的方块实体，
 * 客户端传入同尺寸的空容器占位，数据由原版自动同步。</p>
 *
 * <p>{@code data} 里三个数：剩余燃烧 tick、总燃烧 tick（画火苗条用）、
 * 以及映射到 0~1000 的电量（画电量条用）。</p>
 */
public class GeneratorMenu extends AbstractContainerMenu {
    private static final int MACHINE_SLOTS = FurnaceGeneratorBlockEntity.SIZE;   // 1

    /** 燃料槽在界面里的位置（相对界面左上角）。 */
    public static final int FUEL_X = 80;
    public static final int FUEL_Y = 35;

    private static final int DATA_BURN_LEFT = 0;
    private static final int DATA_BURN_TOTAL = 1;
    private static final int DATA_ENERGY = 2;
    private static final int DATA_COUNT = 3;

    private final ContainerData data;

    /** 那根竖条的满值（发电机的 FE 缓冲）。 */
    private final int powerCapacity;

    /** 服务端构造：熔炉发电机。
     *
     * <p>用<b>命名工厂</b>而不是构造重载：构造签名都一样、只有参数类型不同，
     * 重载在调用点上很容易歧义（javac 会报
     * "reference to GeneratorMenu is ambiguous"），名字分开最省心。</p>
     */
    public static GeneratorMenu forGenerator(MenuType<?> type, int containerId,
                                             Inventory playerInventory,
                                             FurnaceGeneratorBlockEntity generator) {
        return new GeneratorMenu(type, containerId, playerInventory, generator.getFuel(),
                generator, MachineEnergy.GENERATOR_BUFFER);
    }

    /** 客户端构造：只有类型与背包，具体数据由服务端同步进来。 */
    public GeneratorMenu(MenuType<?> type, int containerId, Inventory playerInventory) {
        this(type, containerId, playerInventory,
                new SimpleContainer(MACHINE_SLOTS), new SimpleContainerData(DATA_COUNT),
                MachineEnergy.GENERATOR_BUFFER);
    }

    private GeneratorMenu(MenuType<?> type, int containerId, Inventory playerInventory,
                          Container fuel, ContainerData data, int powerCapacity) {
        super(type, containerId);
        checkContainerSize(fuel, MACHINE_SLOTS);
        this.data = data;
        this.powerCapacity = powerCapacity;

        this.addSlot(new Slot(fuel, FurnaceGeneratorBlockEntity.SLOT_FUEL, FUEL_X, FUEL_Y));
        this.addStandardInventorySlots(playerInventory, 8, 84);
        this.addDataSlots(data);
    }

    // ------------------------------------------------------------------
    // 界面读取口
    // ------------------------------------------------------------------

    /** 火苗条剩余比例 0~1。 */
    public float getBurnRatio() {
        int total = this.data.get(DATA_BURN_TOTAL);
        if (total <= 0) {
            return 0.0F;
        }
        return Math.min(1.0F, this.data.get(DATA_BURN_LEFT) / (float) total);
    }

    public boolean isBurning() {
        return this.data.get(DATA_BURN_LEFT) > 0;
    }

    /** 当前数值（发电机是 FE，炉灶是热度）。缓冲小，short 范围内，直接同步原值。 */
    public int getEnergy() {
        return this.data.get(DATA_ENERGY);
    }

    public int getEnergyCapacity() {
        return this.powerCapacity;
    }

    /** 竖条代表热力而不是电量 —— 界面据此换文案。 */
    public boolean isHeatPowered() {
        return false;
    }

    /** 电量比例 0~1。 */
    public float getEnergyRatio() {
        int cap = this.getEnergyCapacity();
        return cap <= 0 ? 0.0F : Math.min(1.0F, this.getEnergy() / (float) cap);
    }

    // ------------------------------------------------------------------
    // AbstractContainerMenu
    // ------------------------------------------------------------------

    @Override
    public ItemStack quickMoveStack(net.minecraft.world.entity.player.Player player, int index) {
        ItemStack original = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot == null || !slot.hasItem()) {
            return ItemStack.EMPTY;
        }
        ItemStack stack = slot.getItem();
        original = stack.copy();

        if (index == 0) {
            // 燃料槽 -> 背包
            if (!this.moveItemStackTo(stack, 1, this.slots.size(), true)) {
                return ItemStack.EMPTY;
            }
        } else if (!this.moveItemStackTo(stack, 0, 1, false)) {
            // 背包 -> 燃料槽（不是燃料就移不动，正常）
            return ItemStack.EMPTY;
        }

        if (stack.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        return original;
    }

    @Override
    public boolean stillValid(net.minecraft.world.entity.player.Player player) {
        return true;
    }
}
