# -*- coding: utf-8 -*-
"""语言文件体检：把"注册了什么"和"翻译了什么"对一遍。

    python tools/check_lang.py

游戏里**不会**因为缺翻译键报错，它只会把键名原样显示出来 ——
所以这类问题只能靠对账发现。

一个必须记住的规则：**方块物品的键是 `block.` 不是 `item.`**
------------------------------------------------------------
NeoForge 的 `registerSimpleBlockItem` 会给物品加上
`useBlockDescriptionPrefix`，于是方块物品用的翻译键是

    block.<物品 id>

注意是**物品**的 id，不是方块的 id —— 种子的物品 id 是 `rice_seeds`、
方块 id 是 `rice_crop`，两者的键各是各的：

    block.chinese_traditional_food.rice_crop    水稻植株   （方块本身）
    block.chinese_traditional_food.rice_seeds   稻种       （种子物品）

第一版把种子写在 `item.rice_seeds` 下，游戏里就显示成键名了。
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAVA = os.path.join(ROOT, "src", "main", "java", "com", "ctf",
                    "chinese_traditional_food")
LANG = os.path.join(ROOT, "src", "main", "resources", "assets",
                    "chinese_traditional_food", "lang")
NS = "chinese_traditional_food"


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def scan():
    """返回 (block_keys, item_keys) —— 各自**需要**的翻译键。

    做成"需要哪些键"而不是"注册了哪些 id"，是因为两者的对应关系
    并非一一对应（方块物品要 block. 键，普通物品要 item. 键）。
    """
    block_keys, item_keys = set(), set()

    # ---- 包装方块：ModCompressed.java ----
    src = read(os.path.join(JAVA, "registry", "ModCompressed.java"))
    for bid in re.findall(r'BLOCKS\.registerBlock\(\s*"([a-z_0-9]+)"', src):
        block_keys.add(bid)
    for iid in re.findall(r'ITEMS\.registerSimpleBlockItem\(\s*"([a-z_0-9]+)"', src):
        block_keys.add(iid)          # 方块物品 -> block. 键

    # ---- 作物：ModCrops.java ----
    src = read(os.path.join(JAVA, "registry", "ModCrops.java"))
    for bid in re.findall(r'BLOCKS\.registerBlock\("([a-z_0-9]+)"', src):
        block_keys.add(bid)
    for iid in re.findall(r'ITEMS\.registerSimpleBlockItem\("([a-z_0-9]+)"', src):
        block_keys.add(iid)          # 种子 = 方块物品 -> block. 键

    # ---- 果树：ModTrees.java ----
    src = read(os.path.join(JAVA, "registry", "ModTrees.java"))
    for bid in re.findall(r'BLOCKS\.registerBlock\(\s*\n?\s*"([a-z_0-9]+)"', src):
        block_keys.add(bid)
    for iid in re.findall(r'ITEMS\.registerSimpleBlockItem\("([a-z_0-9]+)"', src):
        block_keys.add(iid)          # 树苗/原木 = 方块物品 -> block. 键

    # ---- 手写方块：ModBlocks.java（常量名 -> id）----
    blocks_src = read(os.path.join(JAVA, "registry", "ModBlocks.java"))
    const_to_id = dict(re.findall(
        r'DeferredBlock<\w+>\s+(\w+)\s*=\s*BLOCKS\.registerBlock\(\s*"([a-z_0-9]+)"',
        blocks_src))
    for bid in const_to_id.values():
        block_keys.add(bid)

    # ---- 物品：ModItems.java ----
    src = read(os.path.join(JAVA, "registry", "ModItems.java"))
    for name in re.findall(r'registerSimpleBlockItem\(ModBlocks\.(\w+)\)', src):
        if name in const_to_id:
            block_keys.add(const_to_id[name])
    for iid in re.findall(r'ITEMS\.registerSimpleItem\("([a-z_0-9]+)"', src):
        item_keys.add(iid)
    for iid in re.findall(r'ITEMS\.registerItem\(\s*\n?\s*"([a-z_0-9]+)"', src):
        item_keys.add(iid)

    return ({"block.%s.%s" % (NS, b) for b in block_keys},
            {"item.%s.%s" % (NS, i) for i in item_keys})


def main():
    zh = json.load(io.open(os.path.join(LANG, "zh_cn.json"), encoding="utf-8"))
    en = json.load(io.open(os.path.join(LANG, "en_us.json"), encoding="utf-8"))

    block_keys, item_keys = scan()
    problems = []

    for key in sorted(block_keys):
        if key not in zh:
            problems.append("缺中文：%s" % key)
        if key not in en:
            problems.append("缺英文：%s" % key)
    for key in sorted(item_keys):
        if key not in zh:
            problems.append("缺中文：%s" % key)
        if key not in en:
            problems.append("缺英文：%s" % key)
    for key in sorted(set(zh) - set(en)):
        problems.append("只有中文：%s" % key)
    for key in sorted(set(en) - set(zh)):
        problems.append("只有英文：%s" % key)

    # 多余键：本模组命名空间下、既不是方块也不是物品的 item./block. 键
    known = block_keys | item_keys
    stale = [k for k in zh
             if k.startswith(("block.%s." % NS, "item.%s." % NS)) and k not in known]

    print("需要：方块键 %d / 物品键 %d" % (len(block_keys), len(item_keys)))
    print("语言：中文 %d 键 / 英文 %d 键" % (len(zh), len(en)))
    if stale:
        print("\n多余（id 已不存在，%d 个）：" % len(stale))
        for k in sorted(stale)[:25]:
            print("  - %s = %s" % (k, zh[k]))
    if problems:
        print("\n发现 %d 个问题：" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
    else:
        print("\n缺键 / 不一致：无")
    return 0


if __name__ == "__main__":
    sys.exit(main())
