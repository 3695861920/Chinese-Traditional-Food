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

---

## 当前进度（阶段 1 已完成）

| 内容 | 位置 |
| --- | --- |
| 完整物品清单（210 条，12 大类） | [`docs/物品清单.md`](docs/物品清单.md) |
| 工程骨架 / 注册表 | `src/main/java/.../registry/` |
| 摆放方块 + 方块实体 | `src/main/java/.../common/block/` |
| 客户端渲染器 | `src/main/java/.../client/render/` |
| 示例菜品 麻婆豆腐 + 豆腐 | `src/main/java/.../common/item/`、`src/main/resources/data/.../recipe/` |
| 3 个自定义效果（团圆 / 步步高升 / 圆满） | `registry/ModMobEffects.java` |
| 7 张 64×64 纹理（Minecraft 像素画风格，程序化生成） | `tools/build_textures.py` |

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
├── fetch_cc0_assets.ps1                 抓取 CC0 素材（提取配色用）
└── build_textures.py                    64×64 Minecraft 风格纹理生成脚本
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
