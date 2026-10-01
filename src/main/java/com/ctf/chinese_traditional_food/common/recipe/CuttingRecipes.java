package com.ctf.chinese_traditional_food.common.recipe;

import com.ctf.chinese_traditional_food.ChineseTraditionalFood;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

/**
 * 案板切割规则的运行时解析。
 *
 * <p>规则表本身由 {@link ModRecipes#CUTTING} 提供（那是生成出来的）。这里只做两件事：</p>
 * <ol>
 *   <li>把字符串形式的输入（{@code "ns:path"} 或 {@code "#ns:tag"}）解析成
 *       物品或标签，并缓存下来 —— 不在每次右键时去查注册表；</li>
 *   <li>按表顺序匹配：<b>先具体物品、后标签</b>，
 *       这样「豆腐 → 豆腐丝」不会被「蔬菜 → 蔬菜丝」抢先命中。</li>
 * </ol>
 *
 * <p>之所以用代码表而不是自定义 {@code RecipeType}：
 * 本装置被要求「配方独立于其它模组、始终可用」，代码表最直接、也不受
 * 数据包加载顺序影响。将来若要支持数据包自定义，把
 * {@link ModRecipes#CUTTING} 换成读取 JSON 即可，调用方不用改。</p>
 */
public final class CuttingRecipes {
    /** 解析后的一条规则。 */
    private record Resolved(@Nullable Item item, @Nullable TagKey<Item> tag,
                            ItemStack result, boolean needsKnife, int extraTime) {

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

    private static List<Resolved> resolved;

    /** 解析并缓存规则表。第一次调用时做，之后走缓存。 */
    private static List<Resolved> rules() {
        if (resolved != null) {
            return resolved;
        }
        List<Resolved> list = new ArrayList<>();
        for (ModRecipes.CuttingEntry entry : ModRecipes.CUTTING) {
            Item item = null;
            TagKey<Item> tag = null;
            String input = entry.input();

            if (input.startsWith("#")) {
                // 标签：先写路径里带命名空间的，再退回本模组命名空间
                String body = input.substring(1);
                Identifier id = body.contains(":")
                        ? Identifier.parse(body)
                        : ChineseTraditionalFood.id(body);
                tag = ItemTags.create(id);
            } else {
                Identifier id = input.contains(":")
                        ? Identifier.parse(input)
                        : ChineseTraditionalFood.id(input);
                item = BuiltInRegistries.ITEM.getValue(id);
                if (item == null || item == net.minecraft.world.item.Items.AIR) {
                    // 引用了不存在的物品：跳过而不是崩溃，方便多模组环境
                    ChineseTraditionalFood.LOGGER.warn("案板切割表引用了不存在的物品: {}", input);
                    continue;
                }
            }

            Identifier outId = ChineseTraditionalFood.id(entry.output());
            Item outItem = BuiltInRegistries.ITEM.getValue(outId);
            if (outItem == null || outItem == net.minecraft.world.item.Items.AIR) {
                ChineseTraditionalFood.LOGGER.warn("案板切割表引用了不存在的产出: {}", entry.output());
                continue;
            }

            list.add(new Resolved(item, tag, new ItemStack(outItem),
                    entry.needsKnife(), entry.extraTime()));
        }
        resolved = List.copyOf(list);
        return resolved;
    }

    /**
     * 查一条切割规则。
     *
     * @param input    要切的食材
     * @param hasKnife 玩家是否手持刀类工具（{@code #chinese_traditional_food:knives}）
     * @return 匹配到的规则，没有则 {@code null}
     */
    @Nullable
    public static Result find(ItemStack input, boolean hasKnife) {
        for (Resolved rule : rules()) {
            if (!rule.matches(input)) {
                continue;
            }
            if (rule.needsKnife() && !hasKnife) {
                continue;   // 这道食材必须用刀，没刀就换下一档（比如标签规则）
            }
            return new Result(rule.result().copy(), rule.extraTime(), rule.needsKnife());
        }
        return null;
    }

    /** 匹配结果。 */
    public record Result(ItemStack output, int extraTime, boolean usedKnife) {}

    /**
     * 案板表里的一条（给配方查看器用）。
     *
     * <p>和内部的 {@code Resolved} 长得几乎一样，之所以单独开一个
     * 公开 record：内部那条是 {@code private}，把它开放出去等于把
     * "以后可以随便改"的自由丢掉了。多写十行换一个稳定的对外契约，值。</p>
     *
     * @param item       具体输入物品；标签规则时为 {@code null}
     * @param tag        标签输入；具体物品规则时为 {@code null}
     * @param result     产出
     * @param needsKnife 是否必须手持刀
     */
    public record Cut(@Nullable Item item, @Nullable TagKey<Item> tag,
                      ItemStack result, boolean needsKnife) {}

    /** 整张案板表（已解析）。 */
    public static List<Cut> all() {
        List<Cut> list = new ArrayList<>();
        for (Resolved rule : rules()) {
            list.add(new Cut(rule.item(), rule.tag(), rule.result(), rule.needsKnife()));
        }
        return list;
    }

    private CuttingRecipes() {}
}
