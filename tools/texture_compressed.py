# -*- coding: utf-8 -*-
"""食材包装方块的贴图：包装本身 + 露出来的内容物。

    python tools/build_textures.py --only compressed

**卡通风**（这一版的重点）
------------------------
之前是"写实像素画"：细噪声、多色阶、弱对比。看起来像真的粗麻布，
但放在一起灰扑扑的、辨识度也不高。这一版改成卡通：

1. **平涂**：每种材质只用 2~3 个色阶，中间不做抖动渐变 —— 色块边界干净；
2. **粗描边**：所有形状都套一圈 1 像素的深色轮廓。这是卡通感最关键的一条，
   它让"一袋米""一箱番茄"在远处就能从背景里跳出来；
3. **高饱和**：颜色往饱和端推（内容物尤其明显），不再往灰里调；
4. **大色块**：颗粒画大、果子画大、少画小碎点。

实现上的做法：所有内容物都由"先铺色块，再统一描边"两步完成 ——
描边是后处理（`_outline_all`），所以每种形态不用各自操心边界。

一张图分两半
------------
每种方块生成两张：

* ``<id>.png``       —— **包装本身**（麻袋是布纹、木箱是木板、陶缸是釉面）；
* ``<id>_top.png``   —— **露出来的内容物**（袋口 / 箱口 / 缸口）。

这样才像农夫乐事的稻米袋 / 卷心菜箱：**不用右键，一眼就看出装的是什么**。
"""

import math

from PIL import Image

SIZE = 16
U = SIZE / 16.0

_noise = None
_bayer = None
_quantize = None
_shade = None


def set_size(size):
    global SIZE, U
    SIZE = size
    U = size / 16.0


def bind(noise, bayer, quantize, shade):
    global _noise, _bayer, _quantize, _shade
    _noise, _bayer, _quantize, _shade = noise, bayer, quantize, shade


def _px(img, x, y, colour, alpha=255):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        img.putpixel((int(x), int(y)), (colour[0], colour[1], colour[2], alpha))


def _opaque():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))


def _alpha(img, x, y):
    """取某个像素的 alpha（越界当 0）。落影要用它判断"这里是不是空的"。"""
    if 0 <= x < SIZE and 0 <= y < SIZE:
        return img.getpixel((int(x), int(y)))[3]
    return 0


def _pix_at(img, x, y):
    """取某个像素的颜色（只要 RGB）。"""
    return img.getpixel((int(x), int(y)))[:3]


def _seed(name):
    import zlib
    return zlib.crc32(name.encode("utf-8")) & 0x7FFF or 1


# ======================================================================
# 卡通风的两个基础手法
# ======================================================================

# 描边用的深色。不用纯黑 —— 纯黑在像素画里太硬，深暖褐更贴木头与食物。
INK = (56, 38, 28)


def _saturate(colour, amount=0.45):
    """把颜色往饱和端推（卡通的第一条：颜色要"艳"）。

    做法是把当前亮度当作基准，把每个通道往"离灰最远"的方向拉。
    """
    r, g, b = colour[:3]
    grey = (r + g + b) / 3.0
    out = []
    for c in (r, g, b):
        v = grey + (c - grey) * (1.0 + amount)
        out.append(max(0, min(255, int(v + 0.5))))
    return tuple(out)


def _flat(value, levels):
    """平涂：把连续值切成 levels 档，**不做抖动** —— 卡通的色块边界要干净。"""
    v = max(0.0, min(0.9999, value))
    return int(v * levels)


def _palette(pal, levels=3):
    """从一个 4 档配色里取出一组"平涂用"的颜色：暗 / 主 / 亮（都加饱和）。"""
    dark, main, light, _accent = pal
    if levels >= 3:
        return [_saturate(dark), _saturate(main), _saturate(light)]
    return [_saturate(dark), _saturate(main)]


def _ink(img, colour=INK):
    """给整张图上**粗描边**：所有不透明像素的边缘套一圈深色。

    这是卡通感最关键的一步 —— 形状有了明确的轮廓，
    远处就能认出来，而且同一套画风横跨 34 种方块。
    """
    px = img.load()
    w, h = img.size
    edges = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                continue
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                    edges.append((x, y))
                    break
    for (x, y) in edges:
        px[x, y] = colour + (255,)
    return img
# ======================================================================
# 包装本身
# ======================================================================

# 布袋的底色：偏中性的粗麻色。内容物的颜色会往这上面"染"一点，
# 于是不同内容物的袋子各不相同，但一眼还都是布。
BURLAP = (150, 128, 96)

# 麻绳的颜色阶（暗 / 主 / 亮）
ROPE = ((118, 92, 52), (166, 134, 78), (206, 180, 118))

# 木桶的铁箍
IRON = ((58, 60, 66), (92, 96, 104), (134, 138, 146))

# 木桶的桶板基色（会被内容物的颜色染）
BARREL_WOOD = (150, 110, 70)


def _tint_toward(pal, base, amount):
    """把配色往基准色里调 —— amount=0 全是基准色，1 全是配色。"""
    dark, main, light, accent = pal
    return tuple(int(base[i] + (main[i] - base[i]) * amount + 0.5) for i in range(3))


# ======================================================================
# 体积感：把"平涂"升级成"有厚度的平涂"
# ======================================================================
#
# 一个方块的六个面贴的是**同一张**图，所以没法靠真正的方向光做出立体；
# 只能把光影**画进贴图里**。三条一起用，16×16 上也能看出是个鼓的东西：
#
#   1. 上下渐变 —— 顶面受光、底部积影（最有效的一条）；
#   2. 两侧压暗 —— 边缘往深色收一档，读作"圆柱 / 鼓腹"；
#   3. 接缝阴影 —— 两个部件交界处压一道暗线，部件之间才有前后关系。
#
# 关键是**依然分档**（每通道只取 4~5 个色阶），不做连续渐变 ——
# 这样既有体积感，又还是像素画。

def _steps(base, count=5):
    """从基准色往两头各拉几档，得到一组"平涂用"的色阶（暗 → 亮）。"""
    out = []
    for i in range(count):
        t = (i / (count - 1.0)) * 2.0 - 1.0        # -1 .. +1
        out.append(_shade(base, t * 0.34))
    return out


def _volume_level(col, row, size=None):
    """返回 0（最暗）~4（最亮）的体积档位。

    ``col`` / ``row`` 是像素坐标，都是 0 起。竖向占七成权重（光从上面来），
    横向占三成（两侧收进去）。
    """
    size = size or SIZE
    last = max(1, size - 1)

    down = row / float(last)                       # 0 顶 → 1 底
    # 上亮下暗：顶两档亮、底一档最暗，中间过渡
    vert = 4.0 - down * 4.4
    if down > 0.86:                                # 最底下再压一档（接地影）
        vert -= 0.6
    if down < 0.08:                                # 最顶上留一档高光
        vert += 0.5

    # 两侧压暗，做出"鼓"的错觉
    edge = abs(col + 0.5 - size / 2.0) / (size / 2.0)
    side = -1.2 if edge > 0.74 else (-0.5 if edge > 0.52 else 0.0)

    return max(0, min(4, int(round(vert + side))))


def _side_level(row, size=None, levels=4):
    """侧面 / 顶面的光影档位：**只有上下渐变**。

    方块是方的，两侧不该有圆柱感 —— 所以这里刻意不用 `_volume_level`
    （那个会压暗左右边缘，是给"鼓起来的东西"用的）。
    上面受光、下面积影。

    ``levels`` 必须和调用方准备的色阶数**对上**（色阶 6 档就传 5，返回 0~5）：
    传小了最亮那档永远用不到、整体偏暗；传大了会取到不存在的色阶。
    """
    size = size or SIZE
    top = levels - 1
    t = row / float(max(1, size - 1))
    lvl = top - t * (top * 0.80)
    if t > 0.90:
        lvl -= 0.7
    return max(0, min(top, int(round(lvl))))


# 麻绳在袋身侧面的位置：贴图**最上面**那三行。
#
# 用户明确要求"要看得出最上面有麻绳"。放在侧面贴图的顶上还有个额外好处：
# 一垛袋子叠起来，每隔一格就横着一道绳，比只在顶面画绳更容易认出来。
ROPE_TOP = (2, 4)          # 闭区间，三行


def _woven(name, palette):
    """**编织袋**：整块方块的经纬交织布 + 顶部一道麻绳。

    <h3>为什么不再"撒斑点"</h3>
    上一版的做法是在一块布色上撒疏落的斑点。斑点确实要"疏落 + 成簇"
    才像布（每个像素独立随机就是电视雪花，16×16 里一眼只剩脏），
    但撒得再好，2 米外看还是一块**有颗粒的色块** ——
    几只袋子摆一起分不清是"布袋"还是"抹布"。
    用户要求改成**编织袋**、并"换成不同颜色的整个方块"，所以这一版：

    1. **颜色跟着内容物走 70%**，再整体加饱和 ——
       米袋是米白、红豆袋是暗红、绿豆袋是豆绿，一眼分得开；
    2. **真的画经纬**：把贴图切成 2×2 的格子，偶数格竖线压在上面、
       奇数格横线压在上面，并且**在横线钻进竖线下面的那一格压一像素暗**
       —— 这一点点暗是"交织"能被看出来的唯一原因（没有它只是一张网格）；
    3. **顶部一道麻绳**（见 {@link ROPE_TOP}），绳是拧过的（明暗交替），
       绳上方两行是"被绳勒上来的褶皱"，比下面略暗。

    依然**不描边** —— 整张不透明贴图描边会让相邻方块之间浮出网格线。
    """
    base = _saturate(_tint_toward(palette, BURLAP, 0.70), 0.50)
    ramp = _steps(base, 6)
    seed = _seed(name)
    img = _opaque()

    rope_y0, rope_y1 = ROPE_TOP
    for y in range(SIZE):
        lvl = _side_level(y, levels=5)
        # 绳上方两行：布被绳勒着，压暗一档（这就是"扎口"的褶皱）
        if rope_y0 - 2 <= y < rope_y0:
            lvl = max(0, lvl - 2)
        # 绳下方一行：绳压出来的影
        if y == rope_y1 + 1:
            lvl = max(0, lvl - 2)
        for x in range(SIZE):
            over_vertical = ((x // 2) + (y // 2)) % 2 == 0
            if over_vertical:
                # 竖线压在上面：受光。**只加不减** ——
                # 一开始给"横线"减一档，结果整张图平均暗了两档，
                # 米袋看着像泥袋。现在基准不动，只把压在上面的那半提亮。
                lvl2 = min(5, lvl + 1)
                if y % 3 == 0:
                    lvl2 = max(0, lvl2 - 1)     # 竖线上每隔 3 像素一道线结
            else:
                lvl2 = lvl
                if x % 2 == 0:
                    lvl2 = max(0, lvl - 1)      # 横线钻进下面的那道影
            _px(img, x, y, ramp[lvl2])

    _rope_band(img, rope_y0, rope_y1, seed)
    return img


def _rope_band(img, y0, y1, seed):
    """横过整张图的一道麻绳。

    绳子是**拧**的：两像素一组，一组偏亮一组偏暗，交替排过去。
    再给绳的上下各压一行更暗的 —— 绳子才会像"勒进布里"，
    而不是贴上去的一条色带。
    """
    dark_c, main_c, light_c = ROPE
    for x in range(SIZE):
        tw = (x // 2) % 2
        c = light_c if tw == 0 else main_c
        if (x // 2) % 4 == 3:
            c = dark_c
        for y in range(y0, y1 + 1):
            _px(img, x, y, c)
    # 绳的最上一行提亮一档（受光），最下一行压暗一档（影子）
    for x in range(SIZE):
        _px(img, x, y0, _shade(ROPE[1], 0.30))
        _px(img, x, y1, _shade(ROPE[0], -0.10))


def _barrel_staves(name, palette):
    """**木桶**的桶身：竖着的桶板 + 两道铁箍。木色按内容物染。

    <h3>为什么陶缸改成了木桶</h3>
    用户的原话是"那些桶装材料，大不了设计成颜色不同的木桶来对应不同的材料"。
    原来的陶缸只有一个陶土色，34 只缸长得一模一样，而且"缸"和"酱"之间
    没有任何视觉联系。改成木桶之后：

    * 桶板颜色**跟着内容物走**（豆瓣酱的桶偏红、醋的桶偏琥珀、
      酱油的桶偏黑褐）—— 一排桶一眼看出哪只是什么；
    * 两道铁箍把"桶"这个器型说清楚（不然就是一根木方）。

    <h3>为什么要"桶板"而不是一整片木纹</h3>
    木桶的侧面是**一块块竖板拼的**，所以每 4 像素换一块板、板与板之间
    压一道暗缝。周期 4 整除 16，左右拼接不会断层。
    """
    wood = _saturate(_tint_toward(palette, BARREL_WOOD, 0.50), 0.28)
    ramp = _steps(wood, 6)
    seed = _seed(name)
    img = _opaque()

    for y in range(SIZE):
        lvl = _side_level(y, levels=5)
        for x in range(SIZE):
            v = lvl
            slot = x % 4
            if slot == 0:
                v = max(0, v - 2)            # 板缝
            elif slot == 3:
                v = max(0, v - 1)            # 板缘的影
            elif slot == 1:
                v = min(5, v + 1)            # 板面受光
            # 木纹：竖向连续的深色纹理
            if _noise(x, y // 5, seed) > 0.84:
                v = max(0, v - 1)
            _px(img, x, y, ramp[v])

    # 两道铁箍（上下各一道，靠近桶的两头 —— 和原版木桶的位置一致）
    _iron_hoop(img, 3)
    _iron_hoop(img, 11)
    return img


def _iron_hoop(img, y0):
    """一道铁箍，两像素高：上一行受光、下一行背光，中间压一道暗心。"""
    dark_c, main_c, light_c = IRON
    for x in range(SIZE):
        _px(img, x, y0, light_c if x % 3 != 2 else main_c)
        _px(img, x, y0 + 1, main_c)
        _px(img, x, y0 + 2, dark_c)


def _pressed(name, palette):
    """一整块压实的料（压块）。大颗粒 + 上亮下暗。

    压块和袋 / 桶不一样：它要看起来**被压实了**，所以用的是
    "大颗粒"（4×4 一格）而不是疏落的小斑点，而且每颗颗粒自己
    左上亮、右下暗 —— 于是表面是一颗颗凸起的东西压在一起。
    """
    ramp = _palette(palette, 3)
    img = _opaque()
    seed = _seed(name)
    for y in range(SIZE):
        for x in range(SIZE):
            v = _noise(x // 4, y // 4, seed)
            c = ramp[min(2, _flat(v, 4))]
            if x % 4 == 0 and y % 4 == 0:
                c = _shade(c, 0.16)            # 每颗的左上：亮
            elif x % 4 == 3 or y % 4 == 3:
                c = _shade(c, -0.16)           # 每颗的右下：暗
            c = _shade(c, (_side_level(y, levels=5) - 2) * 0.06)
            _px(img, x, y, c)
    return img


def shell(name, palette, form):
    """包装的**侧面 / 底面**。

    <h3>为什么这里**不**调 _ink()</h3>
    描边是给"有透明背景的图形"用的（比如箱子顶上的一堆果子）。
    整张不透明的方块贴图如果也描边，相邻两块之间会浮出一道**网格线**，
    本来该连成一片的货架就变成了一块块瓷砖。原版羊毛、木板都不描边。
    """
    if form in ("bag", "sack"):
        return _woven(name, palette)
    if form == "barrel":
        return _barrel_staves(name, palette)
    return _pressed(name, palette)


def shell_top(name, palette, form, family):
    """包装的**顶面**：袋口露货、桶口露货、压块的压边。

    <h3>统一的原则：顶面必须"看得见装的是什么"</h3>
    袋 / 桶 / 箱三种容器都遵守同一条：顶面**铺满内容物**，只在外面留
    一圈"器皿"的边（箱是木框、桶是铁箍、袋是麻绳圈）。

    这样不用右键就能认出方块里是什么 —— 也是农夫乐事那套稻米袋 /
    卷心菜箱的做法。
    """
    if form == "barrel":
        return _barrel_top(name, palette, family)
    if form == "brick":
        return _pressed_edge(_pressed(name, palette), palette)
    return _sack_mouth(name, palette, family)


def _material_window(inset, name, palette, family):
    """把内容物铺进"内缩 inset 像素"的区域里。

    调用 `contents` 时**必须把 inset 传下去**而不是"先画满再裁边" ——
    裁的话三排果子会被切成中间一坨，根本不像番茄（这个坑踩过）。
    """
    return contents(name, palette, family, inset=inset)


def _sack_mouth(name, palette, family):
    """编织袋的顶面：**内容物占绝对主体 + 最外一圈麻绳**。

    用户的要求是"最顶部有对应材料的逼真贴图"，所以内容物必须够大。
    `cx = cy = 7.5`，于是 `box = max(dx, dy)` 只能取 0.5,1.5,…,7.5
    这 8 个值，正好对应 8 圈。这一版的分层是：

        box = 7.5   麻绳（最外一圈）
        box = 6.5   麻绳（第二圈 —— 绳看着有两像素粗）
        box ≤ 5.5   内容物（**11×11**，占 69%）

    <h3>为什么四角是布、不是绳</h3>
    一圈绳如果画成规整的方框，看着像**画框**而不是袋口。真实的布袋
    从上面看是"布从四角被拢过来扎住"，所以四个角换成布色 ——
    绳圈在四角断开，读起来就是"被拢住的布口"。方框 = 画框，收角 = 袋口。

    <h3>走过的一版弯路</h3>
    上一版绳圈只有**一圈**、内容物又被裁到 9×9，用户要的
    "最顶部有材料的逼真贴图"就缩成了一小撮。这一版把绳加粗到两圈、
    内容物放大到 11×11。
    """
    cloth = _shade(_saturate(_tint_toward(palette, BURLAP, 0.70), 0.50), -0.14)
    img = _opaque()

    # 先把内容物按"整块铺满"画上去，再把外面两圈换成绳与布
    full = contents(name, palette, family, inset=0)
    for y in range(SIZE):
        for x in range(SIZE):
            _px(img, x, y, _pix_at(full, x, y))

    cx = cy = (SIZE - 1) / 2.0
    dark_c, main_c, light_c = ROPE
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = abs(x - cx), abs(y - cy)
            box = max(dx, dy)                      # 方框距离（8 档）
            corner = min(dx, dy) < 3.0 and box >= 5.5
            if corner:
                _px(img, x, y, cloth)              # 四角：拢过来的布
            elif box >= 7.0:
                # 最外一圈：麻绳，**拧**过的（斜向明暗交替）
                tw = ((x + y) // 2) % 2
                _px(img, x, y, light_c if tw == 0 else main_c)
            elif box >= 6.0:
                # 第二圈：绳的暗面，于是绳看着有两像素粗
                tw = ((x + y) // 2) % 2
                _px(img, x, y, main_c if tw == 0 else dark_c)
    return img


def _barrel_top(name, palette, family):
    """木桶的顶面：**铁箍一圈 + 中间一整块内容物**。

    和木箱（`crate_top`）的区别在于：木箱用的是原版桶身的**木框**，
    木桶用的是**铁箍**。两者摆在一起，一个像敞口木箱、一个像装了料的木桶，
    不会混。

    内容物同样占主体（内缩 3 像素），因为桶口是圆的，外圈留多一点才
    不显得挤。
    """
    goods = _material_window(3, name, palette, family)
    wood = _saturate(_tint_toward(palette, BARREL_WOOD, 0.50), 0.28)
    ramp = _steps(wood, 6)
    img = _opaque()
    seed = _seed(name)

    # 桶顶的木板：一圈一圈的木纹（和桶身同一套木色，所以整体是"一只桶"）
    for y in range(SIZE):
        for x in range(SIZE):
            v = 3
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge == 0:
                v = 1                        # 最外圈：桶沿的影
            elif edge == 1:
                v = 4                        # 桶沿受光
            if _noise(x // 3, y, seed) > 0.86:
                v = max(0, v - 1)
            _px(img, x, y, ramp[v])

    # 铁箍：桶顶也有，半径 6（比内容物的 5 稍大）
    cx = cy = (SIZE - 1) / 2.0
    dark_c, main_c, light_c = IRON
    for y in range(SIZE):
        for x in range(SIZE):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if abs(d - 6.2) < 0.6:
                _px(img, x, y, light_c)
            elif abs(d - 5.1) < 0.6:
                _px(img, x, y, dark_c)

    # 内容物：铺进圆窗（半径 5）
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 5.0 ** 2:
                _px(img, x, y, _pix_at(goods, x, y))
    return img


def _pressed_edge(img, palette):
    """压块顶面：四周压出一圈边（模具压出来的）。"""
    ramp = _palette(palette, 3)
    for y in range(SIZE):
        for x in range(SIZE):
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge == 0:
                _px(img, x, y, ramp[0])
            elif edge == 1:
                _px(img, x, y, _shade(_pix_at(img, x, y), 0.18))
    return img


def crate_top(name, palette, family):
    """木箱的顶面：**一圈木框 + 框里铺满的货**。

    <h3>为什么以原版 `barrel_top` 为底</h3>
    用户要的是"**顶端颜色要和侧边颜色一样**"。侧边用的就是原版木桶的
    `barrel_side`，所以顶面的木框也必须用**同一张图里的木头**才可能一样。

    原版 `barrel_top` 正好给了这件事：它本身就是"木框 + 中间一个圆盖子"
    （盖子直径约 12 像素）。我们把**中间那个圆换成货**，外圈木框原样保留：

        ┌──────────────┐  ← 木框：原版 barrel_top 的像素，和桶身同色
        │   ○○○○○○○○   │
        │  ○ 货 货 货 ○  │  ← 圆窗里塞满货
        │   ○○○○○○○○   │
        └──────────────┘

    取不到原版贴图时（比如还没 build 过），退回自己画一圈木头色。
    """
    import vanilla_extract as VX

    goods = contents(name, palette, family, inset=2)
    img = _opaque()
    base = VX.image("block/barrel_top")

    if base is not None:
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, base.getpixel((x, y))[:3])
    else:
        wood = VX.average("block/barrel_side") or (150, 108, 66)
        dark = _shade(wood, -0.34)
        light = _shade(wood, 0.20)
        for y in range(SIZE):
            for x in range(SIZE):
                c = light if (x % 4 == 1) else (dark if (x % 4 == 0) else wood)
                if min(x, y, SIZE - 1 - x, SIZE - 1 - y) == 0:
                    c = dark
                _px(img, x, y, c)

    # 把货填进中间那个圆窗（半径 5.5，正好接上原版盖子的内沿）
    cx = cy = (SIZE - 1) / 2.0
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 5.5 ** 2:
                _px(img, x, y, goods.getpixel((x, y))[:3])
    return img


# ======================================================================
# 内容物
# ======================================================================

def _blob(img, cx, cy, rx, ry, pal, seed, shade=True):
    """一个"果子"：三档平涂 + 一块方形高光 + 底下一条接触影。

    卡通风和写实反着来 —— **不做连续球面渐变**，只用
    "亮面 / 主色 / 暗面"三块硬边色 + 一块白高光。三档色本身已经
    让球"鼓"起来了，再在**下方贴一条更暗的宽影**，果子就坐实在堆里、
    不会像贴纸浮着 —— 这条接触影是"立体"的关键。
    """
    ramp = _palette(pal, 3)
    dark_c, main_c, light_c = ramp[0], ramp[1], ramp[2]
    shadow = _shade(dark_c, -0.30)

    pts = []
    for y in range(max(0, int(cy - ry - 2)), min(SIZE, int(cy + ry + 3))):
        for x in range(max(0, int(cx - rx - 2)), min(SIZE, int(cx + rx + 3))):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                pts.append((x, y, dx, dy))

    # 先铺接触影：把球往下挪一点再画一遍，作为"落在地上的影"
    if shade:
        for (x, y, _dx, _dy) in pts:
            yy = y + max(1, int(ry * 0.42))
            if 0 <= yy < SIZE:
                _px(img, x, yy, _shade(shadow, -0.10))

    for (x, y, dx, dy) in pts:
        # 受光在左上：只用硬边两档
        if (dx + dy) < -0.30:
            c = light_c
        elif (dx + dy) > 0.50:
            c = dark_c
        else:
            c = main_c
        _px(img, x, y, c)

    # 方形高光（不是圆点 —— 方点才是卡通）
    if rx >= 2.0:
        hx, hy = int(cx - rx * 0.45), int(cy - ry * 0.45)
        inside = {(p[0], p[1]) for p in pts}
        for y in (hy, hy + 1):
            for x in (hx, hx + 1):
                if (x, y) in inside:
                    _px(img, x, y, (255, 255, 255))
    return pts


def _layout_round(seed):
    """圆果怎么摆 —— 由名字决定，所以"梨袋""桃袋"不会摆成同一堆。

    在 3×3 的格子上选 6~8 个位置并各自抖动，返回值是
    ``(x, y, r, k)``，x/y/r 都是 **16 单位**（和模型同一套坐标），
    由调用方乘 ``U`` 换成像素。

    果子取大、取满：箱子是要"堆得冒尖"的，边缘留一圈空气就不像装满了。
    """
    centers = (2.8, 8.0, 13.2)
    order = sorted(range(9), key=lambda i: _noise(i, 0, seed))
    n = 6 + (seed >> 3) % 3                       # 6 / 7 / 8 个
    out = []
    for k, idx in enumerate(order[:n]):
        gx, gy = centers[idx % 3], centers[idx // 3]
        jx = (_noise(idx, 1, seed) - 0.5) * 1.2
        jy = (_noise(idx, 2, seed) - 0.5) * 1.2
        r = 3.4 + _noise(idx, 3, seed) * 0.9      # 每颗大小不同 → 不像复制粘贴
        out.append((gx + jx, gy + jy, r, k))
    return out


def contents(name, palette, family, inset=0):
    """露出来的内容物（大色块 + 体积光影）。

    ``inset`` 是四周留白的像素数。木箱的顶面要留一圈木框，
    这时候得让货**按框内那块区域重新布局**，而不是先画满整张再裁掉边 ——
    裁的话会把三排果子切成"中间一坨"，看起来根本不像番茄。
    """
    img = _opaque()
    seed = _seed(name)
    ramp = _palette(palette, 3)
    dark_c, main_c, light_c = ramp
    # 整堆底下压一层暗，货才像"堆在袋里"而不是"浮在口上"
    floor = _shade(dark_c, -0.42)
    # 内缩映射：K 是缩放、OFF 是平移。所有"16 单位空间"的坐标都要过这两个值。
    # （底色依然铺满整张 —— 多出来的部分会被外面的木框盖住。）
    K = (SIZE - 2 * inset) / float(SIZE)
    OFF = inset

    if family == "round":
        blobs = _layout_round(seed)
        # 先把整张图填成**堆底的深色**，再往上摆果子。
        # 这一步很重要：缝里如果留纯黑，整张图会显得是"贴在黑底上的贴纸"；
        # 填成内容的深色，一堆东西才读作"一团货"。
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, floor)
        for (cx, cy, r, k) in blobs:
            _blob(img, OFF + cx * U * K, OFF + cy * U * K,
                  r * U * K, r * U * K,
                  palette, seed + k * 17, shade=False)

    elif family == "leafy":
        # 几片叠在一起的大叶子：先铺堆底，再往上叠。
        # 每片只两色 + 一条叶脉，剩下的交给统一描边。
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, floor)
        leaves = ((5.6, 6.4, 5.8, 5.2, -0.30),
                  (11.4, 8.4, 5.2, 4.8, 0.35),
                  (7.6, 12.4, 5.4, 4.6, -0.10))
        # 用名字把三片叶子的顺序和角度都搅一下，两只菜箱不会叠得一模一样
        rot0 = ((seed % 24) - 12) * 0.05
        for order_i, idx in enumerate(sorted(range(3), key=lambda i: _noise(i, 7, seed))):
            cx, cy, rx, ry, rot = leaves[idx]
            rot += rot0 * (1 if order_i % 2 == 0 else -1)
            pts = []
            ca, sa = math.cos(rot), math.sin(rot)
            for y in range(SIZE):
                for x in range(SIZE):
                    dx = (x + 0.5 - OFF - cx * U * K) / (U * K)
                    dy = (y + 0.5 - OFF - cy * U * K) / (U * K)
                    u = dx * ca - dy * sa
                    v = dx * sa + dy * ca
                    # 叶子不是椭圆：一头尖一头圆
                    if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0 + 0.35 * (u / rx):
                        pts.append((x, y, u / rx, v / ry))
            # 这片叶子的落影（往右下偏）
            for (x, y, _u, _v) in pts:
                sx, sy = x + max(1, int(1.2 * U)), y + max(1, int(1.2 * U))
                if sx < SIZE and sy < SIZE and _alpha(img, sx, sy) == 0:
                    _px(img, sx, sy, floor)
            for (x, y, u, v) in pts:
                if (u + v) < -0.30:
                    c = light_c
                elif (u + v) > 0.55:
                    c = dark_c
                else:
                    c = main_c
                _px(img, x, y, c)
            # 叶脉：一条从基部到头部的粗线
            for (x, y, u, v) in pts:
                if abs(v) < 0.12:
                    _px(img, x, y, dark_c)

    elif family == "lump":
        # 大块干货：几块不规则的大块，平涂三档 + 落影
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, floor)
        lumps = ((4.6, 5.0, 4.4, 4.0, -0.3), (11.0, 4.8, 4.2, 3.8, 0.2),
                 (7.8, 10.6, 4.6, 4.2, -0.1), (13.4, 12.2, 3.4, 3.2, 0.4))
        # 块的大小随名字抖一抖，"花生箱"和"红枣箱"不会长得一样
        jitter = 0.85 + (_noise(0, 0, seed)) * 0.35
        for (cx, cy, rx, ry, rot) in lumps:
            rx, ry = rx * jitter, ry * jitter
            pts = []
            ca, sa = math.cos(rot), math.sin(rot)
            for y in range(SIZE):
                for x in range(SIZE):
                    dx = (x + 0.5 - OFF - cx * U * K) / (U * K)
                    dy = (y + 0.5 - OFF - cy * U * K) / (U * K)
                    u = dx * ca - dy * sa
                    v = dx * sa + dy * ca
                    # 加一点不规则，免得全是椭圆
                    wob = 1.0 + 0.22 * math.sin(math.atan2(v, u) * 3.0)
                    if (u / (rx * wob)) ** 2 + (v / (ry * wob)) ** 2 <= 1.0:
                        pts.append((x, y, u / rx, v / ry))
            for (x, y, _u, _v) in pts:
                sx, sy = x + max(1, int(0.9 * U)), y + max(1, int(0.9 * U))
                if sx < SIZE and sy < SIZE and _alpha(img, sx, sy) == 0:
                    _px(img, sx, sy, floor)
            for (x, y, u, v) in pts:
                if (u + v) < -0.35:
                    c = light_c
                elif (u + v) > 0.60:
                    c = dark_c
                else:
                    c = main_c
                _px(img, x, y, c)

    elif family == "paste":
        # 酱：一整片平涂 + 几处凹窝 + 两处油光。
        # 卡通的酱不能画成一锅粥 —— 要有"面"和"点"的层次才立体。
        steps = _steps(main_c, 5)
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, steps[_volume_level(x, y)])
        # 5 个凹窝：外圈暗、里面亮（凹下去才有体积）
        for i in range(5):
            gx = int(OFF + (1.6 + i * 2.9) * U * K)
            gy = int(OFF + (2.4 + (i % 2) * 5.4) * U * K)
            w = max(2, int(1.5 * U * K))
            for y in range(gy, min(SIZE, gy + w)):
                for x in range(gx, min(SIZE, gx + w)):
                    _px(img, x, y, dark_c)
            for y in range(gy + 1, min(SIZE, gy + w - 1)):
                for x in range(gx + 1, min(SIZE, gx + w - 1)):
                    _px(img, x, y, light_c)
        # 两处油光
        for (gx, gy) in ((int(OFF + 5.0 * U * K), int(OFF + 6.2 * U * K)),
                         (int(OFF + 11.0 * U * K), int(OFF + 10.2 * U * K))):
            for y in range(gy, min(SIZE, gy + max(1, int(0.8 * U * K)))):
                for x in range(gx, min(SIZE, gx + max(1, int(0.8 * U * K)))):
                    _px(img, x, y, (255, 255, 255))

    else:  # grain
        # 颗粒堆：**大颗**的颗粒，每颗自己上亮下暗 —— 一把真的谷物。
        # 底色先用堆底深色，缝里才不会漏出纯黑。
        for y in range(SIZE):
            for x in range(SIZE):
                _px(img, x, y, floor)
        cell = 4 if (seed & 1) == 0 else 5        # 颗粒大小也随名字变
        # 颗粒只在框内那块铺（外面会被木框盖住，不必画）
        for y in range(inset, SIZE - inset):
            for x in range(inset, SIZE - inset):
                gx, gy = x // cell, y // cell
                v = _noise(gx, gy, seed)
                c = ramp[min(2, _flat(v, 4))]
                lx, ly = x % cell, y % cell
                if lx == 0 and ly == 0:
                    c = _shade(c, 0.22)            # 左上：亮
                elif lx == cell - 1 or ly == cell - 1:
                    c = _shade(c, -0.22)           # 右下：暗
                else:
                    c = _shade(c, 0.0)
                _px(img, x, y, c)
        # 堆底压暗，谷物才像堆着的
        for y in range(int(SIZE * 0.78), SIZE):
            for x in range(SIZE):
                _px(img, x, y, _shade(_pix_at(img, x, y), -0.18))

    return _ink(img)
