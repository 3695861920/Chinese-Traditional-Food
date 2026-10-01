package com.ctf.chinese_traditional_food;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import com.ctf.chinese_traditional_food.registry.ModCompressed;
import com.ctf.chinese_traditional_food.registry.ModCreativeTabs;
import com.ctf.chinese_traditional_food.registry.ModCrops;
import com.ctf.chinese_traditional_food.registry.ModItems;
import com.ctf.chinese_traditional_food.registry.ModMenus;
import com.ctf.chinese_traditional_food.registry.ModMobEffects;
import com.ctf.chinese_traditional_food.registry.ModTrees;
import com.ctf.chinese_traditional_food.registry.ModWoods;
import com.mojang.logging.LogUtils;
import net.minecraft.resources.Identifier;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;

/**
 * 国风·传统食物 —— 主模组入口。
 *
 * <p>本模组新增：食材、调味料、水果、蔬菜、厨具餐具、八大菜系菜品与传统节日食物，
 * 以及五件自有装置：餐盘 / 大拼盘（把菜摆出来）、案板（用刀切）、
 * 水磨（磨粉）、脱壳机（脱壳）。</p>
 */
@Mod(ChineseTraditionalFood.MOD_ID)
public class ChineseTraditionalFood {
    /** 模组 ID，同时作为所有资源与数据包文件的命名空间。 */
    public static final String MOD_ID = "chinese_traditional_food";
    public static final Logger LOGGER = LogUtils.getLogger();

    public ChineseTraditionalFood(IEventBus modBus, ModContainer container) {
        // 注册顺序很重要：
        // 1) 方块先于物品进行类加载 —— 方块物品(BlockItem)在静态初始化时会引用 DeferredBlock；
        // 2) 方块实体类型依赖方块已经注册（在 Supplier 求值时取 DeferredBlock#get()）。
        ModBlocks.register(modBus);
        ModBlockEntities.register(modBus);
        ModItems.register(modBus);
        // 食材压缩方块（34 种）是生成出来的，单独一个注册表
        ModCompressed.register(modBus);
        ModCrops.register(modBus);
        ModTrees.register(modBus);
        // 13 套木制品（原木/去皮/木板/楼梯/台阶/栅栏/栅栏门 = 117 个方块）。
        // **必须排在 ModTrees 之后**：树苗长成树时会去注册表里取 <fruit>_log，
        // 而注册表在那之后才能查。
        ModWoods.register(modBus);
        ModMenus.register(modBus);
        ModMobEffects.register(modBus);
        ModCreativeTabs.register(modBus);

        // 把我们的条目追加进原版创造模式标签页
        modBus.addListener(ModCreativeTabs::addToVanillaTabs);
        // 给装置挂上物品能力，让漏斗与其它模组的管道能和它们交互
        modBus.addListener(ModCapabilities::registerCapabilities);
    }

    /** 生成 {@code chinese_traditional_food:<path>} 形式的资源路径。 */
    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }
}
