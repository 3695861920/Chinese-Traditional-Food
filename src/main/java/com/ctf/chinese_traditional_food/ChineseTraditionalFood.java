package com.ctf.chinese_traditional_food;

import com.ctf.chinese_traditional_food.registry.ModBlockEntities;
import com.ctf.chinese_traditional_food.registry.ModBlocks;
import com.ctf.chinese_traditional_food.registry.ModCreativeTabs;
import com.ctf.chinese_traditional_food.registry.ModItems;
import com.ctf.chinese_traditional_food.registry.ModMobEffects;
import com.mojang.logging.LogUtils;
import net.minecraft.resources.Identifier;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;

/**
 * 国风·传统食物 —— 主模组入口。
 *
 * <p>本模组新增：食材、调味料、八大菜系菜品、传统节日食物、
 * 厨具餐具（物品与方块）、以及可把菜品<b>摆放出来</b>的餐盘 / 大拼盘。</p>
 *
 * <p>参考代码只写到"能跑通的地基"为止：注册表 + 餐盘摆放系统 + 一道示例菜（麻婆豆腐）。
 * 后续按 <code>docs/物品清单.md</code> 逐个补齐即可。</p>
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
        ModMobEffects.register(modBus);
        ModCreativeTabs.register(modBus);

        // 把我们的条目追加进原版创造模式标签页
        modBus.addListener(ModCreativeTabs::addToVanillaTabs);
    }

    /** 生成 {@code chinese_traditional_food:<path>} 形式的资源路径。 */
    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }
}
