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
        /** 水磨：磨粉。 */
        MILLING(ModRecipes.MILLING),
        /** 脱壳机：脱壳。 */
        SHELLING(ModRecipes.SHELLING);

        private final List<ModRecipes.Entry> definitions;

        Kind(List<ModRecipes.Entry> definitions) {
            this.definitions = definitions;
        }
    }

    /** 解析后的一条规则。 */
    public record Resolved(@Nullable Item item, @Nullable TagKey<Item> tag,
                           ItemStack result, @Nullable ItemStack byproduct,
                           float byproductChance, int ticks) {

        boolean matches(ItemStack stack) {
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

    private ProcessRecipes() {}
}
