package com.ctf.chinese_traditional_food.common.recipe;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.jetbrains.annotations.Nullable;

/**
 * 自研装置（水磨 / 脱壳机）的规则解析与匹配。
 *
 * <p>规则表本身由 {@link ModRecipes} 提供（那是生成出来的）。这里负责：</p>
 * <ol>
 *   <li>把字符串输入（{@code "ns:path"} 或 {@code "#ns:tag"}）解析成物品或标签并缓存 ——
 *       不在每次 tick 里查注册表；</li>
 *   <li>按表顺序匹配：<b>先具体物品、后标签</b>；</li>
 *   <li>掷副产物。副产物的概率判定在调用方（服务端）做，这里只提供描述。</li>
 * </ol>
 */
public final class ProcessRecipes {

    /** 装置类型。 */
    public enum Kind {
        /** 水磨：磨粉。单材料，一次出来一批。 */
        MILLING(ModRecipes.MILLING, null),
        /** 脱壳机：脱壳。单材料。 */
        SHELLING(ModRecipes.SHELLING, null),
        /** 蒸笼：蒸汽催熟。多材料锅谱，一次一道。 */
        STEAMING(null, ModRecipes.STEAMER),
        /** 汤锅：炖、汤、饭。 */
        BOILING(null, ModRecipes.SOUP_POT),
        /** 炒锅：炒、煎、整菜。 */
        COOKING(null, ModRecipes.WOK);

        private final List<ModRecipes.Entry> definitions;
        private final List<ModRecipes.CookEntry> cookEntries;

        Kind(List<ModRecipes.Entry> definitions, List<ModRecipes.CookEntry> cookEntries) {
            this.definitions = definitions;
            this.cookEntries = cookEntries;
        }

        /** 这一台是"多材料锅"还是"单材料机"。 */
        public boolean isCook() {
            return this.cookEntries != null;
        }
    }

    /** 解析后的一条规则。 */
    public record Resolved(@Nullable Item item, @Nullable TagKey<Item> tag,
                           ItemStack result, @Nullable ItemStack byproduct,
                           float byproductChance, int ticks) {

        /**
         * 这一堆东西里是不是有匹配的。
         *
         * <p>{@code public} 是因为锅谱也要用它逐样比对材料
         * （见 {@code AbstractHeatProcessorBlockEntity#activeInputSlot}）。</p>
         */
        public boolean matches(ItemStack stack) {
            if (stack.isEmpty()) {
                return false;
            }
            if (this.item != null) {
                return stack.is(this.item);
            }
            return this.tag != null && stack.is(this.tag);
        }
    }

    private static final List<List<Resolved>> CACHE = new ArrayList<>();

    /**
     * 一条解析好的锅谱。
     *
     * <p>{@link #ingredients} 里**重复出现**表示要两份（比如腊八蒜要两瓶醋）。</p>
     *
     * @param result      产出的模板（数量已经在里面）
     * @param ticks       耗时
     * @param ingredients 需要的材料，每一项是一个 {@link Resolved} 的单材料形式
     */
    public record Cook(ItemStack result, int ticks, List<Resolved> ingredients) {

        /**
         * 这一堆槽位里够不够凑出这道菜。
         *
         * <p>做法是逐项清点：每样材料先算"要几份"，再数槽里"有几份"。
         * 不做排列组合搜索 —— 因为材料表很短（≤ 9 项）而且同一种材料
         * 在槽里是可互换的，按种类计数就够了，也不会因为槽位顺序不同
         * 而出现"明明够了却匹配不上"。</p>
         */
        public boolean matches(List<ItemStack> slots) {
            List<Resolved> need = new ArrayList<>(this.ingredients);
            List<ItemStack> pool = new ArrayList<>();
            for (ItemStack s : slots) {
                if (!s.isEmpty()) {
                    pool.add(s);
                }
            }
            for (Resolved ingredient : need) {
                boolean found = false;
                for (int i = 0; i < pool.size(); i++) {
                    if (ingredient.matches(pool.get(i))) {
                        pool.remove(i);
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    return false;
                }
            }
            return true;
        }
    }

    private static final List<List<Cook>> COOK_CACHE = new ArrayList<>();

    /** 解析并缓存某个锅的锅谱。 */
    private static List<Cook> cookRules(Kind kind) {
        while (COOK_CACHE.size() <= kind.ordinal()) {
            COOK_CACHE.add(null);
        }
        List<Cook> cached = COOK_CACHE.get(kind.ordinal());
        if (cached != null) {
            return cached;
        }

        List<Cook> list = new ArrayList<>();
        for (ModRecipes.CookEntry entry : kind.cookEntries) {
            Item outItem = lookup(entry.output());
            if (outItem == null) {
                ChineseTraditionalFood.LOGGER.warn("锅谱引用了不存在的产出: {}", entry.output());
                continue;
            }
            List<Resolved> mats = new ArrayList<>();
            boolean ok = true;
            for (String token : entry.ingredients()) {
                Resolved r = resolveToken(token);
                if (r == null) {
                    ChineseTraditionalFood.LOGGER.warn("锅谱引用了不存在的材料: {}（{} 的）",
                            token, entry.output());
                    ok = false;
                    break;
                }
                mats.add(r);
            }
            if (!ok) {
                continue;
            }
            list.add(new Cook(new ItemStack(outItem, entry.outputCount()),
                    entry.ticks(), List.copyOf(mats)));
        }
        COOK_CACHE.set(kind.ordinal(), List.copyOf(list));
        return COOK_CACHE.get(kind.ordinal());
    }

    /** 把一个材料标签（{@code "ns:item"} 或 {@code "#ns:tag"}）解析成单材料规则。 */
    @Nullable
    private static Resolved resolveToken(String token) {
        if (token.startsWith("#")) {
            String body = token.substring(1);
            Identifier id = body.contains(":")
                    ? Identifier.parse(body)
                    : ChineseTraditionalFood.id(body);
            return new Resolved(null, ItemTags.create(id), ItemStack.EMPTY, ItemStack.EMPTY, 0.0F, 0);
        }
        Item item = lookup(token);
        if (item == null) {
            return null;
        }
        return new Resolved(item, null, ItemStack.EMPTY, ItemStack.EMPTY, 0.0F, 0);
    }

    /** 解析并缓存某个装置的规则表。 */
    private static List<Resolved> rules(Kind kind) {
        while (CACHE.size() <= kind.ordinal()) {
            CACHE.add(null);
        }
        List<Resolved> cached = CACHE.get(kind.ordinal());
        if (cached != null) {
            return cached;
        }

        List<Resolved> list = new ArrayList<>();
        for (ModRecipes.Entry entry : kind.definitions) {
            Item item = null;
            TagKey<Item> tag = null;
            String input = entry.input();

            if (input.startsWith("#")) {
                String body = input.substring(1);
                Identifier id = body.contains(":")
                        ? Identifier.parse(body)
                        : ChineseTraditionalFood.id(body);
                tag = ItemTags.create(id);
            } else {
                item = lookup(input);
                if (item == null) {
                    ChineseTraditionalFood.LOGGER.warn("装置规则引用了不存在的输入: {}", input);
                    continue;
                }
            }

            Item outItem = lookup(entry.output());
            if (outItem == null) {
                ChineseTraditionalFood.LOGGER.warn("装置规则引用了不存在的产出: {}", entry.output());
                continue;
            }

            ItemStack byproduct = ItemStack.EMPTY;
            if (!entry.byproduct().isEmpty()) {
                Item byItem = lookup(entry.byproduct());
                if (byItem != null) {
                    byproduct = new ItemStack(byItem);
                }
            }

            list.add(new Resolved(item, tag, new ItemStack(outItem, entry.outputCount()),
                    byproduct, entry.byproductChance(), entry.ticks()));
        }
        CACHE.set(kind.ordinal(), List.copyOf(list));
        return CACHE.get(kind.ordinal());
    }

    @Nullable
    private static Item lookup(String idText) {
        Identifier id = idText.contains(":")
                ? Identifier.parse(idText)
                : ChineseTraditionalFood.id(idText);
        Item item = BuiltInRegistries.ITEM.getValue(id);
        return (item == null || item == Items.AIR) ? null : item;
    }

    /**
     * 查一条规则（不掷副产物）。
     *
     * <p>只用于**单材料**的装置（水磨 / 脱壳机）。锅用 {@link #findCook}。</p>
     *
     * @return 匹配到的规则，没有则 {@code null}
     */
    @Nullable
    public static Resolved find(Kind kind, ItemStack input) {
        for (Resolved rule : rules(kind)) {
            if (rule.matches(input)) {
                return rule;
            }
        }
        return null;
    }

    /**
     * 在一堆槽位里找一道做得出来的菜（锅专用）。
     *
     * <p>按表顺序取**第一条**能凑齐材料的 —— 所以表里越靠前的越优先。
     * 想调优先级就调 {@code content_data} 里的顺序。</p>
     *
     * @return 匹配到的锅谱，没有则 {@code null}
     */
    @Nullable
    public static Cook findCook(Kind kind, List<ItemStack> slots) {
        for (Cook cook : cookRules(kind)) {
            if (cook.matches(slots)) {
                return cook;
            }
        }
        return null;
    }

    /** 按概率掷副产物；没命中或没有副产物则返回 {@link ItemStack#EMPTY}。 */
    public static ItemStack rollByproduct(Resolved rule, RandomSource random) {
        if (rule.byproduct().isEmpty()) {
            return ItemStack.EMPTY;
        }
        if (rule.byproductChance() < 1.0F && random.nextFloat() >= rule.byproductChance()) {
            return ItemStack.EMPTY;
        }
        return rule.byproduct().copy();
    }

    // ------------------------------------------------------------------
    // 给配方查看器（JEI）用的只读出口
    // ------------------------------------------------------------------
    //
    // 下面两个方法本身不参与游戏逻辑，只为把"硬编码表"翻译成
    // "一堆可以逐条展示的配方"。之所以要专门开口子，是因为
    // 这两张表是**代码常量**而不是数据包配方，JEI 自己扫不到。

    /**
     * 某个装置的全部规则（磨粉 / 脱壳）。
     *
     * <p>返回的是**已经解析好**的规则，所以外部不用再处理
     * {@code "ns:item"} 与 {@code "#ns:tag"} 的区别。</p>
     */
    public static List<Resolved> allRules(Kind kind) {
        return kind.isCook() ? List.of() : rules(kind);
    }

    /**
     * 某个锅的全部锅谱。
     *
     * <p>和 {@link #allRules} 一样，拿到的已经是解析后的形式 ——
     * 材料表里重复出现的项表示"要两份"。</p>
     */
    public static List<Cook> allCooks(Kind kind) {
        return kind.isCook() ? cookRules(kind) : List.of();
    }

    private ProcessRecipes() {}
}
