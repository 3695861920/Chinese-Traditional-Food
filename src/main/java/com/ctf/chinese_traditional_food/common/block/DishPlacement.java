package com.ctf.chinese_traditional_food.common.block;

import com.ctf.chinese_traditional_food.registry.ModItems;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.item.Item;
import org.jetbrains.annotations.Nullable;

/**
 * 菜品 -> 三维器型 / 配色 的查表。
 *
 * <p><b>本文件由 {@code tools/gen_content.py} 生成，请不要手改。</b>
 * 要调整请编辑 {@code tools/content_data.py}（配色）
 * 与 {@code tools/dish_models.py}（器型）。</p>
 *
 * <p>摆在地上的菜是<b>一个方块 + 两个方块状态属性</b>（原版蛋糕 / 南瓜派
 * 也是这个路子）：{@code shape} 选三维几何，{@code palette} 决定颜色。
 * 颜色被方块着色（BlockTintSource）读出来 —— 但它<b>必须</b>放在方块状态里，
 * 原因见下面 {@link Palette} 的注释。所以不需要给每道菜写渲染器。</p>
 */
public final class DishPlacement {
    /** 器型，顺序必须与 {@code tools/dish_models.py} 的 SHAPE_ORDER 一致。
     *  实现 {@link StringRepresentable} 是 {@code EnumProperty} 的要求，
     *  序列化出来的名字就是方块状态 JSON 里的键。 */
    public enum Shape implements StringRepresentable {
        BOWL(0),
        PLATE(1),
        PLATTER(2),
        POT(3),
        FISH_PLATE(4),
        DUMPLING(5),
        MOONCAKE(6),
        ZONGZI(7),
        CAKE_SLICE(8),
        CUP(9),
        JAR(10),
        CUBE(11)
        ;

        private final int id;

        Shape(int id) {
            this.id = id;
        }

        public int id() {
            return this.id;
        }

        @Override
        public String getSerializedName() {
            return this.name().toLowerCase(java.util.Locale.ROOT);
        }
    }

    /**
     * 每种器型的包围盒：<b>minX, minY, minZ, maxX, maxY, maxZ</b>（方块坐标系，0~16）。
     *
     * <p>这些数字不是拍脑袋写的，而是 {@code tools/dish_models.py} 从模型元素
     * 的极值实测出来的 —— 所以落在地上时是"<b>模型多大就占多大</b>"：
     * 盘子只有薄薄一层，粽子占地很小，酒盏不会挡住整格。</p>
     */
    private static final float[][] BOUNDS = {
            {1.90F, 0.00F, 1.90F, 14.10F, 6.50F, 14.10F},
            {1.20F, 0.00F, 1.20F, 14.80F, 4.20F, 14.80F},
            {0.60F, 0.00F, 0.60F, 15.40F, 4.80F, 15.40F},
            {0.00F, 0.00F, 0.60F, 16.00F, 7.30F, 15.40F},
            {0.80F, 0.00F, 3.40F, 15.20F, 3.60F, 12.60F},
            {2.70F, 0.00F, 3.00F, 13.30F, 2.90F, 13.00F},
            {2.40F, 0.00F, 2.40F, 13.80F, 2.60F, 13.40F},
            {2.70F, 0.00F, 5.10F, 13.30F, 4.30F, 10.70F},
            {3.50F, 0.00F, 3.50F, 11.20F, 5.30F, 11.30F},
            {4.60F, 0.00F, 4.60F, 11.40F, 4.00F, 11.40F},
            {3.80F, 0.00F, 3.80F, 12.20F, 8.30F, 12.20F},
            {2.50F, 0.00F, 2.60F, 13.30F, 5.60F, 13.30F},
    };

    /**
     * 配色（取值就是 {@code content_data.PALETTES} 的键）。
     *
     * <h2>为什么颜色要放进方块状态</h2>
     * 26.1 的方块模型着色走 {@code BlockStateModelWrapper#updateTints}，
     * 它<b>只调用 {@code BlockTintSource#color(BlockState)}</b>：
     * {@code update()} 里传给模型的上下文是 {@code BlockAndTintGetter.EMPTY}
     * 与 {@code BlockPos.ZERO}，整条路径上既没有世界也没有方块实体，
     * {@code colorInWorld} <b>永远不会被调用</b>。
     *
     * <p>所以原先"从方块实体查颜色"的做法只会拿到常量白 —— 菜全是白的。
     * 把颜色做成方块状态属性之后，区块烘焙、物品栏、破坏粒子
     * 拿到的都是同一个正确颜色（顺便也不再需要方块实体参与渲染）。</p>
     */
    public enum Palette implements StringRepresentable {
        WHITE(0, 0xF0EEE2),
        CREAM(1, 0xE8D6AC),
        WHEAT(2, 0xCEA860),
        GOLD(3, 0xE2B044),
        RED(4, 0xB23E32),
        GREEN(5, 0x6A9C40),
        PALEGREEN(6, 0x96BA60),
        DARKGREEN(7, 0x4A7434),
        YELLOW(8, 0xE4C85C),
        BLACK(9, 0x4A423C),
        MUNG(10, 0x7C8E4A),
        ORANGE(11, 0xE28430),
        BROWN(12, 0xA0703E),
        TAN(13, 0xC4A476),
        PURPLE(14, 0x804E8C),
        LEAF(15, 0x58943C),
        CABBAGE(16, 0xBAD08C),
        SILVER(17, 0xBAC2AC),
        TOMATO(18, 0xC63E2C),
        CHILI(19, 0xBA2E26),
        EGGPLANT(20, 0x68488A),
        CUCUMBER(21, 0x4E7436),
        WINTERMELON(22, 0x76906C),
        BITTER(23, 0x94AC64),
        FUNGUS(24, 0x684C3C),
        WOODEAR(25, 0x463A32),
        DRIED(26, 0x966C46),
        SEEDBR(27, 0x9E764E),
        SEEDPALE(28, 0xC8B284),
        SEEDSB(29, 0x564A3E),
        SOY(30, 0x5C341C),
        VINEGAR(31, 0x7A542C),
        WINE(32, 0xD4BE8A),
        OIL(33, 0xE8C860),
        CHILI_OIL(34, 0xB03E1E),
        PASTE(35, 0x803422),
        SAUCE(36, 0x462818),
        SPICE(37, 0x8E6034),
        STAR(38, 0x7A4E2C),
        SICHUAN(39, 0xA8362E),
        IRON(40, 0xC4C8D0),
        WOOD(41, 0xB07E4A),
        PORCELAIN(42, 0xE8ECF2),
        BAMBOO(43, 0xBAC476),
        STONE(44, 0x969490),
        CLAY(45, 0xAA6C4C),
        BRAISED(46, 0x804226),
        REDBRAISED(47, 0x9C3A20),
        STEAMED(48, 0xEEE8D6),
        SOUP(49, 0xD8BE8C),
        STIRFRY(50, 0xB08A4E),
        GREENDISH(51, 0x769E4A),
        PASTRY(52, 0xEEE0BE),
        CAKE(53, 0xD6B276)
        ;

        private final int id;
        private final int color;
        private final int liquidColor;

        Palette(int id, int color) {
            this.id = id;
            this.color = color;
            int r = (color >> 16 & 0xFF) * 3 / 4;
            int g = (color >> 8 & 0xFF) * 3 / 4;
            int b = (color & 0xFF) * 3 / 4;
            this.liquidColor = r << 16 | g << 8 | b;
        }

        public int id() {
            return this.id;
        }

        /** 食物主体色（0xRRGGBB）。 */
        public int color() {
            return this.color;
        }

        /** 汤汁 / 汁水色：主色压暗一档。 */
        public int liquidColor() {
            return this.liquidColor;
        }

        @Override
        public String getSerializedName() {
            return this.name().toLowerCase(java.util.Locale.ROOT);
        }
    }

    private static final Map<Item, Shape> SHAPE_BY_ITEM = new HashMap<>();
    private static final Map<Item, Palette> PALETTE_BY_ITEM = new HashMap<>();

    static {
        SHAPE_BY_ITEM.put(ModItems.JIUZHUAN_DACHANG.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.CONGSAO_HAISHEN.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.TANGCU_LIYU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.YOUBAO_SHUANGCUI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.GUOTA_DOUFU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.NAITANG_PUCAI.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.DEZHOU_PAJI.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.SIXI_WANZI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.ZAOLIU_YUPIAN.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.KONGFU_YIPINGUO.get(), Shape.POT);
        SHAPE_BY_ITEM.put(ModItems.MAPO_TOFU.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.HUIGUO_ROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.SHUIZHU_YU.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.FUQI_FEIPIAN.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.GONGBAO_JIDING.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.YUXIANG_ROUSI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.MAOXUE_WANG.get(), Shape.POT);
        SHAPE_BY_ITEM.put(ModItems.LAZIJI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.DONGPO_ZHOUZI.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.KAISHUI_BAICAI.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.BAIQIE_JI.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.MIZHI_CHASHAO.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.QINGZHENG_SHIBANYU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.LAOHUO_LIANGTANG.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.SHAOE.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.XIAJIAO_HUANG.get(), Shape.DUMPLING);
        SHAPE_BY_ITEM.put(ModItems.GANCHAO_NIUHE.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.BAOZHI_LIAOSHEN.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.ZEZE_BAO.get(), Shape.POT);
        SHAPE_BY_ITEM.put(ModItems.YUNTUN_MIAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.SONGSHU_GUIYU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.DAZHAXIE.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.YANGZHOU_SHIZITOU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.JINLING_YANSHUIYA.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.DAZHU_GANSI.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.WUXI_JIANGPAIGU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.QINGZHENG_SHIYU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.SHUIJING_YAOROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.BILUO_XIAREN.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.WENSI_DOUFU.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.FOTIAOQIANG.get(), Shape.POT);
        SHAPE_BY_ITEM.put(ModItems.LIZHI_ROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.ZUI_PAIGU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.BABAO_HONGXUN_FAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.JITANG_TUN_HAIBANG.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.ZHAN_HETIANJI.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.WUYI_XUNE.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.XIANGNAN_RIBAO.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.XIHU_CUYU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.DONGPO_ROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.LONGJING_XIAREN.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.XUECAI_HUANGYU.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.QINGTANG_YUEJI.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.GANCAI_MENROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.WUWEI_JIANXIE.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.DUOJIAO_YUTOU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.MAOSHI_HONGSHAOROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.LAJIAO_CHAOROU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.DONGAN_ZIJI.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.LAWEI_HEZHENG.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.XIANGXI_WAIPOCAI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.JIANGBANYA.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.YONGZHOU_XUEYA.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.ZUAN_YUCHI.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.ZHUXUE_WANZI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.CHOU_GUIYU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.HUIZHOU_YIPINGUO.get(), Shape.POT);
        SHAPE_BY_ITEM.put(ModItems.HUMAO_DOUFU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.HUANGSHAN_DUNGE.get(), Shape.POT);
        SHAPE_BY_ITEM.put(ModItems.WENZHENG_SHANSUN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.FANGLA_YU.get(), Shape.FISH_PLATE);
        SHAPE_BY_ITEM.put(ModItems.MIZHI_HONGYU.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.QINGZHENG_SHIJI.get(), Shape.PLATE);
        SHAPE_BY_ITEM.put(ModItems.JIAOZI.get(), Shape.DUMPLING);
        SHAPE_BY_ITEM.put(ModItems.NIAN_GAO.get(), Shape.CAKE_SLICE);
        SHAPE_BY_ITEM.put(ModItems.CHUN_JUAN.get(), Shape.CAKE_SLICE);
        SHAPE_BY_ITEM.put(ModItems.TANG_YUAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.LA_ROU.get(), Shape.PLATTER);
        SHAPE_BY_ITEM.put(ModItems.ZHIMA_TANGYUAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.DOUSHA_TANGYUAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.HUASHENG_TANGYUAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.QING_TUAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.AI_JIAO.get(), Shape.DUMPLING);
        SHAPE_BY_ITEM.put(ModItems.ROU_ZONG.get(), Shape.ZONGZI);
        SHAPE_BY_ITEM.put(ModItems.ZAO_ZONG.get(), Shape.ZONGZI);
        SHAPE_BY_ITEM.put(ModItems.DOUSHA_ZONG.get(), Shape.ZONGZI);
        SHAPE_BY_ITEM.put(ModItems.QIAO_GUO.get(), Shape.MOONCAKE);
        SHAPE_BY_ITEM.put(ModItems.QIAOYA_MIAN.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.LIANRONG_YUEBING.get(), Shape.MOONCAKE);
        SHAPE_BY_ITEM.put(ModItems.DOUSHA_YUEBING.get(), Shape.MOONCAKE);
        SHAPE_BY_ITEM.put(ModItems.WUREN_YUEBING.get(), Shape.MOONCAKE);
        SHAPE_BY_ITEM.put(ModItems.DANYUE_YUEBING.get(), Shape.MOONCAKE);
        SHAPE_BY_ITEM.put(ModItems.CHONGYANG_GAO.get(), Shape.CAKE_SLICE);
        SHAPE_BY_ITEM.put(ModItems.JUHUA_JIU.get(), Shape.CUP);
        SHAPE_BY_ITEM.put(ModItems.LABA_ZHOU.get(), Shape.BOWL);
        SHAPE_BY_ITEM.put(ModItems.YANGROU_TANG.get(), Shape.BOWL);

        PALETTE_BY_ITEM.put(ModItems.JIUZHUAN_DACHANG.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.CONGSAO_HAISHEN.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.TANGCU_LIYU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.YOUBAO_SHUANGCUI.get(), Palette.STIRFRY);
        PALETTE_BY_ITEM.put(ModItems.GUOTA_DOUFU.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.NAITANG_PUCAI.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.DEZHOU_PAJI.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.SIXI_WANZI.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.ZAOLIU_YUPIAN.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.KONGFU_YIPINGUO.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.MAPO_TOFU.get(), Palette.CHILI_OIL);
        PALETTE_BY_ITEM.put(ModItems.HUIGUO_ROU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.SHUIZHU_YU.get(), Palette.CHILI_OIL);
        PALETTE_BY_ITEM.put(ModItems.FUQI_FEIPIAN.get(), Palette.CHILI_OIL);
        PALETTE_BY_ITEM.put(ModItems.GONGBAO_JIDING.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.YUXIANG_ROUSI.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.MAOXUE_WANG.get(), Palette.CHILI_OIL);
        PALETTE_BY_ITEM.put(ModItems.LAZIJI.get(), Palette.CHILI);
        PALETTE_BY_ITEM.put(ModItems.DONGPO_ZHOUZI.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.KAISHUI_BAICAI.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.BAIQIE_JI.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.MIZHI_CHASHAO.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.QINGZHENG_SHIBANYU.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.LAOHUO_LIANGTANG.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.SHAOE.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.XIAJIAO_HUANG.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.GANCHAO_NIUHE.get(), Palette.STIRFRY);
        PALETTE_BY_ITEM.put(ModItems.BAOZHI_LIAOSHEN.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.ZEZE_BAO.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.YUNTUN_MIAN.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.SONGSHU_GUIYU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.DAZHAXIE.get(), Palette.CHILI);
        PALETTE_BY_ITEM.put(ModItems.YANGZHOU_SHIZITOU.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.JINLING_YANSHUIYA.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.DAZHU_GANSI.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.WUXI_JIANGPAIGU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.QINGZHENG_SHIYU.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.SHUIJING_YAOROU.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.BILUO_XIAREN.get(), Palette.GREENDISH);
        PALETTE_BY_ITEM.put(ModItems.WENSI_DOUFU.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.FOTIAOQIANG.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.LIZHI_ROU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.ZUI_PAIGU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.BABAO_HONGXUN_FAN.get(), Palette.ORANGE);
        PALETTE_BY_ITEM.put(ModItems.JITANG_TUN_HAIBANG.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.ZHAN_HETIANJI.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.WUYI_XUNE.get(), Palette.DRIED);
        PALETTE_BY_ITEM.put(ModItems.XIANGNAN_RIBAO.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.XIHU_CUYU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.DONGPO_ROU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.LONGJING_XIAREN.get(), Palette.GREENDISH);
        PALETTE_BY_ITEM.put(ModItems.XUECAI_HUANGYU.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.QINGTANG_YUEJI.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.GANCAI_MENROU.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.WUWEI_JIANXIE.get(), Palette.CHILI);
        PALETTE_BY_ITEM.put(ModItems.DUOJIAO_YUTOU.get(), Palette.CHILI);
        PALETTE_BY_ITEM.put(ModItems.MAOSHI_HONGSHAOROU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.LAJIAO_CHAOROU.get(), Palette.CHILI);
        PALETTE_BY_ITEM.put(ModItems.DONGAN_ZIJI.get(), Palette.CHILI);
        PALETTE_BY_ITEM.put(ModItems.LAWEI_HEZHENG.get(), Palette.DRIED);
        PALETTE_BY_ITEM.put(ModItems.XIANGXI_WAIPOCAI.get(), Palette.DARKGREEN);
        PALETTE_BY_ITEM.put(ModItems.JIANGBANYA.get(), Palette.DRIED);
        PALETTE_BY_ITEM.put(ModItems.YONGZHOU_XUEYA.get(), Palette.CHILI_OIL);
        PALETTE_BY_ITEM.put(ModItems.ZUAN_YUCHI.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.ZHUXUE_WANZI.get(), Palette.DRIED);
        PALETTE_BY_ITEM.put(ModItems.CHOU_GUIYU.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.HUIZHOU_YIPINGUO.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.HUMAO_DOUFU.get(), Palette.STIRFRY);
        PALETTE_BY_ITEM.put(ModItems.HUANGSHAN_DUNGE.get(), Palette.BRAISED);
        PALETTE_BY_ITEM.put(ModItems.WENZHENG_SHANSUN.get(), Palette.GREENDISH);
        PALETTE_BY_ITEM.put(ModItems.FANGLA_YU.get(), Palette.REDBRAISED);
        PALETTE_BY_ITEM.put(ModItems.MIZHI_HONGYU.get(), Palette.ORANGE);
        PALETTE_BY_ITEM.put(ModItems.QINGZHENG_SHIJI.get(), Palette.STEAMED);
        PALETTE_BY_ITEM.put(ModItems.JIAOZI.get(), Palette.PASTRY);
        PALETTE_BY_ITEM.put(ModItems.NIAN_GAO.get(), Palette.PASTRY);
        PALETTE_BY_ITEM.put(ModItems.CHUN_JUAN.get(), Palette.GOLD);
        PALETTE_BY_ITEM.put(ModItems.TANG_YUAN.get(), Palette.WHITE);
        PALETTE_BY_ITEM.put(ModItems.LA_ROU.get(), Palette.DRIED);
        PALETTE_BY_ITEM.put(ModItems.ZHIMA_TANGYUAN.get(), Palette.WHITE);
        PALETTE_BY_ITEM.put(ModItems.DOUSHA_TANGYUAN.get(), Palette.CREAM);
        PALETTE_BY_ITEM.put(ModItems.HUASHENG_TANGYUAN.get(), Palette.TAN);
        PALETTE_BY_ITEM.put(ModItems.QING_TUAN.get(), Palette.DARKGREEN);
        PALETTE_BY_ITEM.put(ModItems.AI_JIAO.get(), Palette.DARKGREEN);
        PALETTE_BY_ITEM.put(ModItems.ROU_ZONG.get(), Palette.DARKGREEN);
        PALETTE_BY_ITEM.put(ModItems.ZAO_ZONG.get(), Palette.DARKGREEN);
        PALETTE_BY_ITEM.put(ModItems.DOUSHA_ZONG.get(), Palette.DARKGREEN);
        PALETTE_BY_ITEM.put(ModItems.QIAO_GUO.get(), Palette.PASTRY);
        PALETTE_BY_ITEM.put(ModItems.QIAOYA_MIAN.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.LIANRONG_YUEBING.get(), Palette.CAKE);
        PALETTE_BY_ITEM.put(ModItems.DOUSHA_YUEBING.get(), Palette.CAKE);
        PALETTE_BY_ITEM.put(ModItems.WUREN_YUEBING.get(), Palette.CAKE);
        PALETTE_BY_ITEM.put(ModItems.DANYUE_YUEBING.get(), Palette.CAKE);
        PALETTE_BY_ITEM.put(ModItems.CHONGYANG_GAO.get(), Palette.CAKE);
        PALETTE_BY_ITEM.put(ModItems.JUHUA_JIU.get(), Palette.WINE);
        PALETTE_BY_ITEM.put(ModItems.LABA_ZHOU.get(), Palette.SOUP);
        PALETTE_BY_ITEM.put(ModItems.YANGROU_TANG.get(), Palette.SOUP);
    }

    /** 这道菜的器型；不在表里返回 {@code null}（表示不能摆）。 */
    @Nullable
    public static Shape shapeOf(Item item) {
        return SHAPE_BY_ITEM.get(item);
    }

    /** 这道菜的配色；不在表里返回 {@code null}。 */
    @Nullable
    public static Palette paletteOf(Item item) {
        return PALETTE_BY_ITEM.get(item);
    }

    /**
     * 器型的包围盒，顺序是 {@code [minX, minY, minZ, maxX, maxY, maxZ]}。
     *
     * <p>拿它直接建 {@code VoxelShape}，就能做到"模型多大就占多大"。</p>
     */
    public static float[] boundsOf(Shape shape) {
        return BOUNDS[shape.id()];
    }

    private DishPlacement() {}
}
