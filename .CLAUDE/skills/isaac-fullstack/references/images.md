# Isaac 游戏图片资源获取指南

## 图片来源优先级

| 优先级 | 来源 | 适合场景 |
|---|---|---|
| 1（推荐） | Fandom Rebirth Wiki | 单张道具/角色/结局图标，最方便 |
| 2 | The Spriters Resource | 批量精灵表，适合需要整套资源 |
| 3 | Steam 游戏文件提取 | 获取最高质量原始资源（需要拥有正版游戏） |

---

## 一、Fandom Rebirth Wiki

**网址**：https://bindingofisaacrebirth.fandom.com/wiki/Binding_of_Isaac:_Rebirth_Wiki

覆盖范围：Rebirth / Afterbirth / Afterbirth+ / Repentance 全部 DLC。

### 道具列表页（聚合索引）

https://bindingofisaacrebirth.fandom.com/wiki/Items

每个道具单元格里都有小图标，点击进入详情页可以看到大图。

### 单个道具页面示例

- https://bindingofisaacrebirth.fandom.com/wiki/Torn_Photo
- https://bindingofisaacrebirth.fandom.com/wiki/D8

每个页面包含：
- 道具精灵图（sprite icon），通常为 PNG 格式
- 道具效果描述
- 解锁条件
- 道具品质和类型标签

### 角色页面示例

- https://bindingofisaacrebirth.fandom.com/wiki/Isaac_(Character)
- https://bindingofisaacrebirth.fandom.com/wiki/Azazel

每个页面包含角色精灵图、属性、解锁方式。

### 直接下载图片

打开任意 Wiki 页面 → 右键点击道具图标 → "在新标签页中打开图片" → 得到 PNG 文件的直链。

也可以使用 Fandom 的 MediaWiki API 批量获取图片 URL（见下方"批量获取"章节）。

### 旧版 Wiki

https://bindingofisaac.fandom.com/wiki/The_Binding_of_Isaac_Wiki

覆盖原版 Flash 游戏，更新不如 Rebirth Wiki 及时，但包含一些历史版本内容。

---

## 二、The Spriters Resource

**Rebirth / Afterbirth / Repentance**：
https://www.spriters-resource.com/pc_computer/bindingofisaacrebirth/

**原版 Flash 版**：
https://www.spriters-resource.com/pc_computer/bindingofisaac/

分类包括：可玩角色、敌人与 Boss、道具与拾取物、瓦片集、特效、杂项。

精灵表格式为 PNG（例如 Lazarus 角色表为 1024×512）。适合以下场景：
- 需要一整套统一风格的道具图标
- 需要角色的完整动画帧
- 需要 UI 元素和特效素材

---

## 三、从游戏文件中提取

### Steam PC 版

游戏安装目录下的 `resources/gfx/` 路径包含大量 `.png` 和 `.anm2` 文件。

路径示例：
```
Steam/steamapps/common/The Binding of Isaac Rebirth/resources/gfx/items/collectibles/
```

需要使用资源解包工具（如 ResourceExtractor）来处理 `.anm2` 动画文件。

### 原版 Flash 版

工具：JPEXS Flash Decompiler（https://github.com/jindrapetrik/jpexs-decompiler）

目标文件：`%appdata%/The Binding of Isaac/` 下的 SWF 文件。

---

## 四、其他社区资源

| 资源 | 地址 | 说明 |
|---|---|---|
| Modding of Isaac | https://moddingofisaac.com/ | 社区模组中心，大量自定义道具精灵图 |
| The Cutting Room Floor | https://tcrf.net/The_Binding_of_Isaac | 未使用/隐藏的游戏素材 |
| 百度贴吧图鉴 | https://tieba.baidu.com/p/4237589821 | 中文版道具图鉴帖 |
| isaac-qualityonsprites | https://github.com/boildead/isaac-qualityonsprites-mod | 道具品质图标叠加模组 |

---

## 五、批量获取（Fandom API）

Fandom 提供 MediaWiki API，可以编程方式批量获取道具图片 URL：

```
https://bindingofisaacrebirth.fandom.com/api.php?action=query&titles=Items&prop=images&format=json
```

结合 `action=query&prop=imageinfo&iiprop=url` 可获取图片直链。

Python 示例框架：
```python
import requests

BASE_URL = "https://bindingofisaacrebirth.fandom.com/api.php"
params = {
    "action": "query",
    "titles": "Items",
    "prop": "images",
    "format": "json",
}
resp = requests.get(BASE_URL, params=params)
# 然后逐张获取 imageinfo.url
```

---

## 六、版权说明

- 所有《以撒的结合》游戏资产（精灵图、图标、角色设计）版权归 **Edmund McMillen** 和 **Nicalis** 公司
- 非商业性个人项目（如图鉴/资料站）使用 Wiki 图片属于 **合理使用（fair use）**，但必须标注版权归属
- **不要**：直接用于商业产品、重新分发原始游戏文件、声称拥有版权
- 建议在项目页脚注明：`游戏图片版权 © Edmund McMillen / Nicalis`

---

## 七、项目中图片使用约定

为保持一致性，建议：

- **道具图标**：统一裁剪/缩放为 **64×64 PNG**
- **角色立绘**：统一缩放为 **128×128 PNG**
- **文件命名**：使用道具/角色的英文名或游戏内 ID，小写 + 短横线，如 `brimstone.png`、`azazel.png`
- **存储路径**：前端 `public/images/items/`、`public/images/characters/`、`public/images/endings/`
- **数据库存储**：只存相对路径（如 `items/brimstone.png`），不存完整 URL
