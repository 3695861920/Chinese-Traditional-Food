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
 * <p>摆在地上的菜是<b>一个方块 + 一个方块状态属性</b>（原版蛋糕 / 南瓜派
 * 也是这个路子）：属性选三维几何，颜色由方块着色（BlockTintSource）按这里的配色染。
 * 所以不需要给每道菜写渲染器。</p>
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

    private static final Map<Item, Shape> SHAPE_BY_ITEM = new HashMap<>();
    private static final Map<Item, Integer> COLOR_BY_ITEM = new HashMap<>();

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

        COLOR_BY_ITEM.put(ModItems.JIUZHUAN_DACHANG.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.CONGSAO_HAISHEN.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.TANGCU_LIYU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.YOUBAO_SHUANGCUI.get(), 0xB08A4E);
        COLOR_BY_ITEM.put(ModItems.GUOTA_DOUFU.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.NAITANG_PUCAI.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.DEZHOU_PAJI.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.SIXI_WANZI.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.ZAOLIU_YUPIAN.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.KONGFU_YIPINGUO.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.MAPO_TOFU.get(), 0xB03E1E);
        COLOR_BY_ITEM.put(ModItems.HUIGUO_ROU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.SHUIZHU_YU.get(), 0xB03E1E);
        COLOR_BY_ITEM.put(ModItems.FUQI_FEIPIAN.get(), 0xB03E1E);
        COLOR_BY_ITEM.put(ModItems.GONGBAO_JIDING.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.YUXIANG_ROUSI.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.MAOXUE_WANG.get(), 0xB03E1E);
        COLOR_BY_ITEM.put(ModItems.LAZIJI.get(), 0xBA2E26);
        COLOR_BY_ITEM.put(ModItems.DONGPO_ZHOUZI.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.KAISHUI_BAICAI.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.BAIQIE_JI.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.MIZHI_CHASHAO.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.QINGZHENG_SHIBANYU.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.LAOHUO_LIANGTANG.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.SHAOE.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.XIAJIAO_HUANG.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.GANCHAO_NIUHE.get(), 0xB08A4E);
        COLOR_BY_ITEM.put(ModItems.BAOZHI_LIAOSHEN.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.ZEZE_BAO.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.YUNTUN_MIAN.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.SONGSHU_GUIYU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.DAZHAXIE.get(), 0xBA2E26);
        COLOR_BY_ITEM.put(ModItems.YANGZHOU_SHIZITOU.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.JINLING_YANSHUIYA.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.DAZHU_GANSI.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.WUXI_JIANGPAIGU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.QINGZHENG_SHIYU.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.SHUIJING_YAOROU.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.BILUO_XIAREN.get(), 0x769E4A);
        COLOR_BY_ITEM.put(ModItems.WENSI_DOUFU.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.FOTIAOQIANG.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.LIZHI_ROU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.ZUI_PAIGU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.BABAO_HONGXUN_FAN.get(), 0xE28430);
        COLOR_BY_ITEM.put(ModItems.JITANG_TUN_HAIBANG.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.ZHAN_HETIANJI.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.WUYI_XUNE.get(), 0x966C46);
        COLOR_BY_ITEM.put(ModItems.XIANGNAN_RIBAO.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.XIHU_CUYU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.DONGPO_ROU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.LONGJING_XIAREN.get(), 0x769E4A);
        COLOR_BY_ITEM.put(ModItems.XUECAI_HUANGYU.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.QINGTANG_YUEJI.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.GANCAI_MENROU.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.WUWEI_JIANXIE.get(), 0xBA2E26);
        COLOR_BY_ITEM.put(ModItems.DUOJIAO_YUTOU.get(), 0xBA2E26);
        COLOR_BY_ITEM.put(ModItems.MAOSHI_HONGSHAOROU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.LAJIAO_CHAOROU.get(), 0xBA2E26);
        COLOR_BY_ITEM.put(ModItems.DONGAN_ZIJI.get(), 0xBA2E26);
        COLOR_BY_ITEM.put(ModItems.LAWEI_HEZHENG.get(), 0x966C46);
        COLOR_BY_ITEM.put(ModItems.XIANGXI_WAIPOCAI.get(), 0x4A7434);
        COLOR_BY_ITEM.put(ModItems.JIANGBANYA.get(), 0x966C46);
        COLOR_BY_ITEM.put(ModItems.YONGZHOU_XUEYA.get(), 0xB03E1E);
        COLOR_BY_ITEM.put(ModItems.ZUAN_YUCHI.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.ZHUXUE_WANZI.get(), 0x966C46);
        COLOR_BY_ITEM.put(ModItems.CHOU_GUIYU.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.HUIZHOU_YIPINGUO.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.HUMAO_DOUFU.get(), 0xB08A4E);
        COLOR_BY_ITEM.put(ModItems.HUANGSHAN_DUNGE.get(), 0x804226);
        COLOR_BY_ITEM.put(ModItems.WENZHENG_SHANSUN.get(), 0x769E4A);
        COLOR_BY_ITEM.put(ModItems.FANGLA_YU.get(), 0x9C3A20);
        COLOR_BY_ITEM.put(ModItems.MIZHI_HONGYU.get(), 0xE28430);
        COLOR_BY_ITEM.put(ModItems.QINGZHENG_SHIJI.get(), 0xEEE8D6);
        COLOR_BY_ITEM.put(ModItems.JIAOZI.get(), 0xEEE0BE);
        COLOR_BY_ITEM.put(ModItems.NIAN_GAO.get(), 0xEEE0BE);
        COLOR_BY_ITEM.put(ModItems.CHUN_JUAN.get(), 0xE2B044);
        COLOR_BY_ITEM.put(ModItems.TANG_YUAN.get(), 0xF0EEE2);
        COLOR_BY_ITEM.put(ModItems.LA_ROU.get(), 0x966C46);
        COLOR_BY_ITEM.put(ModItems.ZHIMA_TANGYUAN.get(), 0xF0EEE2);
        COLOR_BY_ITEM.put(ModItems.DOUSHA_TANGYUAN.get(), 0xE8D6AC);
        COLOR_BY_ITEM.put(ModItems.HUASHENG_TANGYUAN.get(), 0xC4A476);
        COLOR_BY_ITEM.put(ModItems.QING_TUAN.get(), 0x4A7434);
        COLOR_BY_ITEM.put(ModItems.AI_JIAO.get(), 0x4A7434);
        COLOR_BY_ITEM.put(ModItems.ROU_ZONG.get(), 0x4A7434);
        COLOR_BY_ITEM.put(ModItems.ZAO_ZONG.get(), 0x4A7434);
        COLOR_BY_ITEM.put(ModItems.DOUSHA_ZONG.get(), 0x4A7434);
        COLOR_BY_ITEM.put(ModItems.QIAO_GUO.get(), 0xEEE0BE);
        COLOR_BY_ITEM.put(ModItems.QIAOYA_MIAN.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.LIANRONG_YUEBING.get(), 0xD6B276);
        COLOR_BY_ITEM.put(ModItems.DOUSHA_YUEBING.get(), 0xD6B276);
        COLOR_BY_ITEM.put(ModItems.WUREN_YUEBING.get(), 0xD6B276);
        COLOR_BY_ITEM.put(ModItems.DANYUE_YUEBING.get(), 0xD6B276);
        COLOR_BY_ITEM.put(ModItems.CHONGYANG_GAO.get(), 0xD6B276);
        COLOR_BY_ITEM.put(ModItems.JUHUA_JIU.get(), 0xD4BE8A);
        COLOR_BY_ITEM.put(ModItems.LABA_ZHOU.get(), 0xD8BE8C);
        COLOR_BY_ITEM.put(ModItems.YANGROU_TANG.get(), 0xD8BE8C);
    }

    /** 这道菜的器型；不在表里返回 {@code null}（表示不能摆）。 */
    @Nullable
    public static Shape shapeOf(Item item) {
        return SHAPE_BY_ITEM.get(item);
    }

    /** 这道菜的主色（0xRRGGBB）；不在表里返回白色。 */
    public static int colorOf(Item item) {
        Integer c = COLOR_BY_ITEM.get(item);
        return c == null ? 0xFFFFFF : c;
    }

    /** 汤汁 / 汁水的颜色：主色压暗一档。 */
    public static int liquidColorOf(Item item) {
        int c = colorOf(item);
        int r = (c >> 16 & 0xFF) * 3 / 4;
        int g = (c >> 8 & 0xFF) * 3 / 4;
        int b = (c & 0xFF) * 3 / 4;
        return r << 16 | g << 8 | b;
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
