# -*- coding: utf-8 -*-
"""炉灶与三件锅具的方块模型与方块状态。

    python tools/machine_models.py     # 一并生成（本模块被它调用）

造型要点
--------
四件器物**高矮分明**，摆在灶边一眼能分清：

    炉灶   y 0 ~ 10.4   矮而宽的砖台，正面一个灶眼
    炒锅   y 0 ~  5.6   敞口浅圆锅 + 两耳 + 搭在沿上的铲子
    蒸笼   y 0 ~ 11.4   三层竹蒸笼 + 盖子 + 缝隙里的白汽
    汤锅   y 0 ~  9.6   高筒深锅 + 双耳 + 盖钮

三件锅具都**刻意做成坐得进炉灶上方那一格**：底面从 y=0 开始、横向比整格略小，
所以放到灶上时看起来是"坐进去"的，不是浮在空中。

仍然全部是实心盒子，不做薄壳中空 —— 不会出现"透视"。
圆柱形零件（锅身、灶眼）复用 `machine_models.oct_prism`。
"""

import math

# machine_models 会在自己加载完之后调用 bind() 把基元塞进来。
#
# 为什么不用 `from machine_models import box`：本脚本是被
# `python tools/machine_models.py` **作为 __main__ 导入**再反过来 import 的，
# 直接 import 会让 machine_models 被**第二次执行**，撞上半初始化的模块。
# 传引用就没有这个问题，和 texture_icons / crop_icons 的做法一致。
MM = None


def bind(module):
    """由 machine_models 注入 box / oct_prism / sq_ring。"""
    global MM
    MM = module


def box(*a, **kw):
    return MM.box(*a, **kw)


def oct_prism(*a, **kw):
    return MM.oct_prism(*a, **kw)


def sq_ring(*a, **kw):
    return MM.sq_ring(*a, **kw)


def _ring_oct(cx, cz, r_out, r_in, y0, y1, tex, cut=0.30):
    """八边形圆环：一圈厚壁。

    做法是"大八棱柱沿 Y 切成上下两段"是不行的（中间还是实心），
    所以改为**四段矩形拼一圈**：上下两条通长、左右两条避开 ——
    和 `sq_ring` 一样的不重叠拼法，只是把切角做在四个角上。
    """
    ch = r_out * cut
    ch_in = r_in * cut
    out = [
        # 上下两条通长
        box({}, cx - r_out + ch, y0, cz - r_out, cx + r_out - ch, y1, cz - r_in,
            default=tex),
        box({}, cx - r_out + ch, y0, cz + r_in, cx + r_out - ch, y1, cz + r_out,
            default=tex),
        # 左右两条（避开上面两条在 z 上的范围）
        box({}, cx - r_out, y0, cz - r_out + ch_in, cx - r_in, y1, cz + r_out - ch_in,
            default=tex),
        box({}, cx + r_in, y0, cz - r_out + ch_in, cx + r_out, y1, cz + r_out - ch_in,
            default=tex),
    ]
    return out


def stove():
    """电磁炉：**一整格**的方块，顶面是发光的线圈。

    刻意做得简单：它就是个台面，不需要四条腿、不需要烟囱。
    通电 / 断电靠方块状态换两张顶面贴图（``machine_cooker_top`` /
    ``machine_cooker_top_on``），远远看一眼就知道在工作没有。
    """
    E = []
    # 机身：整格铺满，和旁边的方块码在一起不突兀
    E.append(box({}, 0.0, 0.0, 0.0, 16.0, 15.0, 16.0, default="#iron"))
    # 顶面：单独一块薄板，方便换"通电"那张贴图
    E.append(box({"up": "#cookerTop"}, 0.0, 15.0, 0.0, 16.0, 16.0, 16.0,
                 default="#iron"))
    # 正面的一道控制条（一条亮边，卡通感来源之一）
    E.append(box({"north": "#cookerPanel"}, 2.0, 12.0, -0.1, 14.0, 14.0, 0.2,
                 default="#iron"))
    # 四角的圆角护角：让整格方块不那么"方"
    for (cx, cz) in ((0.0, 0.0), (14.4, 0.0), (0.0, 14.4), (14.4, 14.4)):
        E.append(box({}, cx, 0.0, cz, cx + 1.6, 15.4, cz + 1.6, default="#iron"))
    # 底部的散热缝
    for i in range(3):
        z = 4.0 + i * 4.0
        E.append(box({}, -0.1, 1.6, z, 0.2, 3.0, z + 2.4, default="#vent"))
        E.append(box({}, 15.8, 1.6, z, 16.1, 3.0, z + 2.4, default="#vent"))
    return E


def wok():
    """炒锅：敞口浅圆锅 + 两侧锅耳 + 搭在锅沿上的铲子。"""
    E = []
    # 锅身：下小上大的八棱柱堆叠（做出碗形）
    E += oct_prism(8.0, 8.0, 3.4, 0.0, 1.0, "#iron", top="#iron")
    E += oct_prism(8.0, 8.0, 4.8, 1.0, 2.4, "#iron", top="#iron")
    E += oct_prism(8.0, 8.0, 6.0, 2.4, 3.6, "#iron", top="#iron")
    # 内壁：一圈暗色，让锅看起来是"敞口"的
    E += _ring_oct(8.0, 8.0, 6.0, 4.4, 3.6, 4.4, "#shadow")
    # 锅里的菜
    E.append(box({"up": "#food"}, 4.4, 3.6, 4.4, 11.6, 4.6, 11.6,
                 default="#food"))
    # 锅沿
    E += _ring_oct(8.0, 8.0, 6.8, 4.6, 4.4, 5.2, "#iron")

    # 两侧锅耳：短而厚，贴在锅口上（不像上一版那样伸出方块外）
    E.append(box({}, 0.0, 3.8, 6.4, 1.4, 5.0, 9.6, default="#iron"))
    E.append(box({}, 14.6, 3.8, 6.4, 16.0, 5.0, 9.6, default="#iron"))

    # 搭在锅沿上的锅铲
    E.append(box({}, 9.4, 5.2, 3.0, 10.8, 5.6, 11.0, default="#iron"))
    E.append(box({}, 10.2, 5.2, 11.0, 12.6, 5.8, 12.8, default="#hopper"))
    return E


def steamer():
    """蒸笼：三层竹蒸笼 + 盖子 + 层间冒出的白汽。"""
    E = []
    # 三层笼屉：每层是"一圈墙 + 一层薄底"
    for i in range(3):
        y0 = i * 3.4
        E += sq_ring(2.2, 2.2, 13.8, 13.8, 1.4, y0, y0 + 3.4, "#bamboo")
        # 层底（薄薄一片，从缝里看是"有一层"）
        E.append(box({}, 2.2, y0, 2.2, 13.8, y0 + 0.5, 13.8, default="#bamboo"))
        # 层与层之间的缝：**只做一圈细环**，不能铺成整块板 ——
        # 铺满的话就等于给每一层加了个盖子，从上面看进去是一片死黑。
        E += sq_ring(2.0, 2.0, 14.0, 14.0, 0.5, y0 + 3.4, y0 + 3.8, "#shadow")
    # 顶层里的食物（不走方块着色，直接画成熟食色）
    E.append(box({"up": "#food"}, 4.0, 6.8, 4.0, 12.0, 7.6, 12.0,
                 default="#food"))

    # 盖子
    E.append(box({"up": "#bamboo"}, 1.2, 10.6, 1.2, 14.8, 11.4, 14.8,
                 default="#bamboo"))
    # 盖钮：只做中间一小坨 —— 上一版给成了 9x9 的大板，
    # 等轴测下看着就像整个盖子都是黑的。
    E.append(box({}, 7.0, 11.4, 7.0, 9.0, 12.0, 9.0, default="#hopper"))
    E.append(box({}, 7.6, 12.0, 7.6, 8.4, 12.4, 8.4, default="#coil"))

    # 白汽：几根细柱从盖沿冒出来
    for (sx, sz) in ((2.6, 2.6), (13.4, 2.6), (2.6, 13.4), (13.4, 13.4)):
        E.append(box({}, sx - 0.4, 11.4, sz - 0.4, sx + 0.4, 12.6, sz + 0.4,
                     default="#steam"))
    return E


def soup_pot():
    """汤锅：高筒深锅 + 双耳 + 盖子 + 盖钮上的热气。"""
    E = []
    # 锅身：直筒（八棱柱），下略收
    E += oct_prism(8.0, 8.0, 6.6, 0.0, 1.0, "#iron", top="#iron")
    E += oct_prism(8.0, 8.0, 7.2, 1.0, 7.6, "#iron", top="#iron")
    # 内壁
    E += _ring_oct(8.0, 8.0, 7.2, 5.8, 7.6, 8.2, "#shadow")
    # 锅沿
    E += _ring_oct(8.0, 8.0, 7.8, 6.0, 8.2, 8.8, "#iron")

    # 盖子（略鼓起）
    E += oct_prism(8.0, 8.0, 6.6, 8.8, 9.6, "#iron", top="#iron")
    E += oct_prism(8.0, 8.0, 4.8, 9.6, 10.2, "#iron", top="#coil")
    # 盖钮
    E.append(box({}, 7.2, 10.2, 7.2, 8.8, 10.8, 8.8, default="#coil"))

    # 双耳：短而厚，贴在锅腰上
    E.append(box({}, 0.0, 5.2, 6.2, 1.6, 6.6, 9.8, default="#iron"))
    E.append(box({}, 14.4, 5.2, 6.2, 16.0, 6.6, 9.8, default="#iron"))

    # 盖钮上冒的热气
    for (sx, sz) in ((7.0, 7.0), (8.8, 8.8)):
        E.append(box({}, sx - 0.35, 10.8, sz - 0.35, sx + 0.35, 12.4, sz + 0.35,
                     default="#steam"))
    return E
