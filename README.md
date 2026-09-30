# 国风·传统食物 (Chinese Traditional Food)

> Minecraft **26.1.2** + **NeoForge** 模组 · 许可证 **MIT** · 模组 ID `chinese_traditional_food`

添加中国常见的食材、调味料、厨具餐具、**八大菜系典型菜品** 与 **传统节日食物**，
并提供两个自研食材处理装置（水磨、脱壳机）、案板与刀具。

**最大的特点：做出来的菜能"摆出来"。** 不是背包里一格图标，而是端上桌的实体。

---

## 核心亮点：菜品摆放系统

只为每道菜注册一个方块会带来 70+ 方块 × 4 个 JSON 的资源爆炸，
所以这里走的是**通用摆放方块 + 方块实体**的路线：

```
餐盘 plate (1 份)          大拼盘 serving_platter (2×2 共 4 份)
      ┌─────┐                    ┌────┬────┐
      │  ●  │                    │ ●  │ ●  │
      └─────┘                    ├────┼────┤
                                 │ ●  │ ●  │
                                 └────┴────┘
```

方块实体记住"盘里是哪道菜"，客户端渲染器把**菜品自己的物品模型**画到盘子上。
**新增任何一道菜都不需要新代码、新模型、新方块 —— 它能吃，就能摆。**

| 手上 | 潜行 | 行为 |
| --- | --- | --- |
| 拿着菜 | 否 | 摆一份上去 |
| 空手 | 否 | 夹一口吃（那一份吃完自动清空） |
| 空手 | 是 | 把整份菜端回背包 |

判定"能不能摆"：带 `minecraft:food` 数据组件即可（原版食物也能摆），
或在 `#chinese_traditional_food:placeable_dishes` 标签里。

类似的还有**案板**：放上食材再用刀切，左边是待切的、右边是切好的。

```
案板 cutting_board
   ┌──────────────────┐
   │  待切食材 │ 成品   │
   └──────────────────┘
```

| 手上 | 案板状态 | 行为 |
| --- | --- | --- |
| 可切的食材 | 空 | 放上去 |
| 刀（`#knives`） | 有食材 | 切一刀，刀掉 1 点耐久 |
| 空手 | 有成品 | 取走成品（没成品则取回食材） |

切割表定义在 `tools/content_data.py` 的 `CUTTING`（由生成器写成 `ModCutting.java`），
匹配时**先具体物品、后标签**，所以「豆腐 → 豆腐丝」不会被「蔬菜 → 蔬菜丝」抢先命中。

---

## 当前进度

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| 0 | 完整物品清单（`docs/物品清单.md`） | ✅ |
| 1 | 工程骨架、**菜品摆放系统**、示例菜品、3 个自定义效果、核心标签与配方 | ✅ |
| 2 | **全部 222 个条目**（食材 / 作物种子 / 调味料 / 水果 / 蔬菜 / 厨具餐具 / 八大菜系 73 道 / 节日食物 24 道）+ 图标 + 159 个配方 | ✅ |
| 3 | **水磨**（邻水自动磨粉）+ **手摇脱壳机**（无界面、可叠料斗组多方块） | ✅ |
| 4a | **案板 + 刀切割**（7 条切割规则，产出蔬菜丝 / 肉丝 / 鱼片 / 豆腐丝） | ✅ |
| 4c | **12 种三维器型 + 三维餐具**（餐盘 / 大拼盘 / 案板全部是叠层立方体模型） | ✅ |
| 4b | 灶台 / 蒸笼 / 炒锅 / 汤锅 / 砂锅 | ⬜ |
| 5 | 作物种植（种子已入库）、果树、村民交易 | ⬜ |
| 6 | `farmersdelight` / `kaleidoscope_cookery` 兼容配方 | ⬜ |

### 内容规模

| 分类 | 数量 |
| --- | --- |
| 基础食材 | 39 |
| 作物种子 | 15 |
| 调味料 | 23 |
| 常见水果 | 16 |
| 常见蔬菜 | 23 |
| 厨具与餐具 | 9 |
| 八大菜系菜品 | 73 |
| 传统节日食物 | 24 |
| **合计注册条目** | **222**（另有 6 个功能方块：餐盘 / 大拼盘 / 案板 / 水磨 / 脱壳机 / 料斗） |
| 配方 | 159 |
| 标签 | 26（11 自有 + 15 `c:` 通用） |
| 纹理 | 244 张（原版分辨率的 16×16） |

---

## 三维模型：为什么不用渲染器

菜品摆在地上、摆在盘里，用的都是**标准的方块模型 + 方块状态**
（原版的蛋糕、南瓜派、营火也是这个路子），而不是自定义渲染器：

* 只注册**一个**方块 `placed_dish`，靠 `shape` 属性在 12 种器型间切换；
* 12 种器型（碗 / 盘 / 大盘 / 砂锅 / 鱼盘 / 饺子 / 月饼 / 粽 / 糕片 / 酒盏 / 罐 / 方块）
  全部是**手写的立方体元素**，有真正的厚度与叠层；
* 每道菜的颜色由**方块着色**（`BlockTintSource`）按菜系配色染上去 ——
  和原版给树叶 / 草 / 药水上色是同一套机制。

“怎么用立方体画出圆”——`tools/dish_models.py` 里的 `_oct()` 把一个圆
**精确拆成 3 个互不重叠的矩形**（拼成八边形），再沿 Y 一层层收缩堆叠，
就有了圆润的盘沿与碗腹。共享边界上的两个面法线相反，背面剔除自动处理，
不重叠、不闪烁，也不需要任何旋转元素。

器皿（餐盘 / 大拼盘 / 案板）的三维模型由 `tools/display_models.py` 生成，
餐盘做成“圈足 + 盘腹 + 翘起的盘沿”，盘心比盘沿**低 0.8 像素** ——
菜是“盛”在盘子里，而不是浮在一块板上。

### “模型多大就占多大”

`dish_models.bounds(shape)` 会**从生成的模型元素里实测包围盒极值**，
写进生成的 `DishPlacement.BOUNDS`，Java 端直接拿它建 `VoxelShape`。
所以碰撞箱与看得见的模型**永远一致**：盘子只有薄薄一层、酒盏不会挡住整格 ——
以后改了模型也不用回头手动同步碰撞箱。

### 菜为什么要绕 X 轴转 -90°

原版物品贴片是画在 **XY 平面** 上的（见 `ItemModelGenerator`：
几何范围 x 0~16、y 0~16、z 7.5~8.5），所以 `ItemDisplayContext.FIXED`
下物品是**竖立**的。原版营火、地面上的展示框都要额外转一下才会放平。
这里采用和“朝上的展示框”完全一致的写法（净旋转 `Rx(-90)`），
菜才会正面朝上、方向正确地躺在盘里（见 `PlateBlockEntityRenderer`）。

---

## 内容全部由数据表生成

`tools/content_data.py` 是**唯一的内容来源**。
改这一个文件，再跑两个脚本，下面这些东西全部自动同步：

```
tools/content_data.py
        │
        ├── python tools/gen_content.py
        │       → ModItems.java / ModCreativeTabs.java
        │       → zh_cn.json / en_us.json
        │       → items/*.json （客户端物品，含 6 个功能方块）
        │       → models/item/*.json
        │       → DishPlacement.java（器型表 + 配色表 + 实测包围盒）
        │       → recipe/*.json
        │       → tags/item/*.json、data/c/tags/item/*.json
        │
        ├── python tools/build_textures.py
        │       → textures/item/*.png （参数化绘制）
        │       → textures/block/*.png
        │
        ├── python tools/dish_models.py      12 种器型的三维模型
        ├── python tools/display_models.py   餐盘 / 大拼盘 / 案板的三维模型
        └── python tools/machine_models.py   水磨 / 脱壳机 / 料斗的三维模型

python tools/validate_content.py    # 完整性 + 资源引用链校验（入库前必跑）
python tools/preview_icons.py       # 拼一张预览图检查画风
```

加一道菜只需要在 `content_data.py` 的 `DISHES` 里填一行：

```python
# id, 中文名, 英文名, 分组, 图标种类, 配色, 饥饿, 饱和, 效果
("gulao_rou", "咕噜肉", "Sweet and Sour Pork", "yue", "dish_plate", "redbraised", 8, 1.0, "SATED"),
```

**零新增代码、零新增方块**——它会自动出现在创造标签页，并直接能在餐盘 / 大拼盘上摆出来。

---

## 目录结构

```
src/main/java/com/ctf/chinese_traditional_food/
├── ChineseTraditionalFood.java          主入口（@Mod）
├── registry/
│   ├── ModItems.java                    物品：菜品 / 食材 / 餐具
│   ├── ModBlocks.java                   方块：餐盘 / 大拼盘
│   ├── ModBlockEntities.java            方块实体类型
│   ├── ModCreativeTabs.java             创造标签页
│   ├── ModMobEffects.java               自定义状态效果
│   ├── ModFoods.java                    食物属性（饥饿 / 饱和）
│   └── ModTags.java                     自定义标签
├── common/
│   ├── item/DishItem.java               菜品物品（带"取食一份"效果表）
│   ├── food/ServeEffect.java            效果描述（Holder + 时长 + 概率）
│   ├── food/DishEffects.java            效果预设表
│   └── block/
│       ├── AbstractDishDisplayBlock.java       摆放方块父类（交互逻辑）
│       ├── PlateBlock.java / ServingPlatterBlock.java
│       └── entity/
│           ├── AbstractDishDisplayBlockEntity.java  存菜 / 存档 / 客户端同步
│           ├── PlateBlockEntity.java
│           └── ServingPlatterBlockEntity.java
└── client/
    ├── ClientSetup.java                 渲染器注册
    └── render/
        ├── DishDisplayRenderState.java  渲染状态
        ├── AbstractDishDisplayRenderer.java
        ├── PlateBlockEntityRenderer.java
        └── ServingPlatterBlockEntityRenderer.java

src/main/resources/
├── assets/chinese_traditional_food/     模型 / 客户端物品 / 纹理 / 语言
└── data/chinese_traditional_food/       配方 / 战利品表 / 标签

tools/
├── content_data.py                      内容数据表（唯一内容来源）
├── gen_content.py                       生成 Java / 语言 / 模型 / 配方 / 标签 / 切割表
├── build_textures.py                    生成 64×64 纹理（器皿 + 内容图标 + 工具方块）
├── texture_icons.py                     约 50 种图标造型的画法
├── texture_utilities.py                 功能方块（案板）的纹理
├── validate_content.py                  完整性校验
├── preview_icons.py                     图标预览拼图
└── fetch_cc0_assets.ps1                 抓取 CC0 素材（取色用）
docs/物品清单.md                          完整物品清单与设计文档
ATTRIBUTION.md                            素材署名与许可证
```

---

## 如何接入工程

本仓库**只包含 Java 代码与 resources**（不含 `build.gradle`、Gradle Wrapper）。
使用方式：

1. 打开 <https://neoforged.net/mod-generator/>，填：
   - Mod name: `国风-传统食物`，Mod id: `chinese_traditional_food`
   - Package: `com.ctf.chinese_traditional_food`
   - Minecraft version: `26.1.2`，Gradle plugin: `ModDevGradle`
   - 下载并解压。
2. 把本仓库的 `src/main/java`、`src/main/resources`、`docs`、`tools` 覆盖进去。
3. 按需在 `gradle.properties` 里设 `mod_license=MIT`。
4. `gradlew runClient` 启动测试。

> 需要 JDK **25** 与 Gradle **9.1+**（Minecraft 26.1 起使用 Java 25）。

## 纹理：64×64，但仍然是 Minecraft 风格

分辨率提到 64×64（相当于 4 倍细节的 HD 材质包），**风格没有变**：

| 规范 | 做法 |
| --- | --- |
| 边缘 | 逐像素直接写，**不做** 超采样 / LANCZOS / 高斯模糊 —— 抗锯齿会让材质发糊 |
| 渐变 | 每种材质只用 6~8 档亮度，档间用 **Bayer 4×4 有序抖动**过渡（像素画经典手法） |
| 质感 | 叠加确定性逐像素噪声，模拟苔痕/木纹/釉面颗粒 |
| 光照 | **不烘焙方向光** —— 方块进游戏后由引擎按面打光（顶 1.0 / 南北 0.8 / 东西 0.6 / 底 0.5），
顶面贴图只画器皿自身的弧度明暗，否则会双重变暗 |
| 平铺 | 方块贴图左右上下自洽，连续摆一排无硬接缝 |
| 物品图标 | 透明背景 + 右下压暗一档做体积感，与原版食物图标一致 |

### 配色来源

木色不是拍脑袋定的，而是从 **CC0 公有领域素材**里提取的：

1. 抓取 [Kenney Pixel Platformer Food Expansion](https://kenney.nl/assets/pixel-platformer-food-expansion)（CC0）
   与 [OpenGameArt 16x16px Food Items](https://opengameart.org/content/16x16px-food-items)（CC0）；
2. 量化后按 HSV 筛出「棕橙」候选（色相 18~46 度）；
3. 取候选的**色相中位数**作为木材色相，再按受控饱和度生成四档亮度阶梯。

见 [`ATTRIBUTION.md`](ATTRIBUTION.md)。

### 重新生成纹理

```powershell
pip install Pillow
powershell -NoProfile -ExecutionPolicy Bypass -File tools/fetch_cc0_assets.ps1
python tools/build_textures.py --size 64     # 想要原版分辨率可加 --size 16
```

输出 7 张 64×64 PNG：青花瓷盘顶面/侧面、木质拼盘、盘子图标、拼盘图标、豆腐、麻婆豆腐。
全部由脚本生成，**无版权争议**，CC0 素材仅用于取色。

---

## 后续路线

见 [`docs/物品清单.md`](docs/物品清单.md) 第十三节：

- 阶段 2：八大菜系每菜系 2~3 道代表菜 + 全部节日食物（直接复用摆放系统）
- 阶段 3：水磨 / 脱壳机（方块实体 + GUI + `IItemHandler`）+ `c:` 标签体系
- 阶段 4：灶台 / 蒸笼 / 炒锅 / 汤锅 / 砂锅；案板 + 刀切割
- 阶段 5：作物种植、果树、村民交易
- 阶段 6：纹理补齐、`farmersdelight` / `kaleidoscope_cookery` 兼容配方

---

## 许可证

MIT。本模组完全独立实现，不复制 TFC、TFC Food Port 或任何其他模组的代码。
