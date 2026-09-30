# 素材署名与许可证 (Attribution)

本模组的所有纹理都由 `tools/build_textures.py` **程序化绘制**，不直接复制任何第三方图片。
绘制过程中从以下 **CC0 / 公有领域** 素材中提取了配色（主要是暖棕色相），
因此不需要署名，但这里仍按惯例记录来源。

---

## 1. 配色来源素材（全部 CC0 1.0）

### Kenney — Pixel Platformer Food Expansion

- 来源：<https://kenney.nl/assets/pixel-platformer-food-expansion>
- 作者：Kenney (<https://kenney.nl>)
- 许可证：**CC0 1.0 Universal**（公有领域贡献）
  <https://creativecommons.org/publicdomain/zero/1.0/>
- 用途：从 `Tilemap/tilemap.png` 量化提取暖棕色相候选

### OpenGameArt — 16x16px Food Items

- 来源：<https://opengameart.org/content/16x16px-food-items>
- 作者：maruki (<https://opengameart.org/users/maruki>)
- 许可证：**CC0**（作者声明 "Public domain - you're free to use it as you wish."）
- 用途：从 `foodies_sheet.png` 量化提取暖棕色相候选

### OpenGameArt — Food Pixel Art (45 icons)

- 来源：<https://opengameart.org/content/food-pixel-art-45-icons>
- 作者：Luca Pixel (<https://www.patreon.com/LucaPixel>)
- 许可证：**CC0 1.0 Universal**
- 用途：备用配色参考（署名非强制）

### 已评估但未采用

| 站点 / 素材包 | 原因 |
| --- | --- |
| Kenney — Food Kit | 3D 模型（OBJ/FBX），不是 2D 像素贴图 |
| itch.io 免费素材区 | 大多数需要页内手动下载、许可证不一，无法稳定自动化 |
| OpenGameArt 上的 `chinese` 关键词结果 | 多为音频与角色素材，无中餐菜品纹理 |

> **结论**：上述 CC0 素材包中**没有中餐菜式的像素图**（都是西式快餐、甜点、西蓝花胡萝卜之类），
> 因此不能直接照搬素材当成品纹理，只能作为**配色依据**。
> 成品纹理全部由 `tools/build_textures.py` 按 Minecraft 像素画规范重绘。

---

## 2. 代码许可证

本模组自身的代码与资源以 **MIT** 授权，见 [`LICENSE`](LICENSE)。

---

## 3. 复现步骤

```powershell
# 1) 抓取 CC0 素材（本机实测可直连）
powershell -NoProfile -ExecutionPolicy Bypass -File tools/fetch_cc0_assets.ps1

# 2) 生成 64x64 纹理，并输出配色提取报告
python tools/build_textures.py --size 64
```

配色提取结果会写到 `tools/downloads/cc0_palette_report.txt`，
里面列出了量化后的全部主色、被筛选为"棕橙"的候选色及其 HSV 值、
以及最终生成的四档木色，可用于复查配色确实来自上述素材。
