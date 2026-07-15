# ISAAC 项目图片任务进度

最后更新：2026-07-15 16:40

## 已完成

### ✅ 道具图片 (2.5.2)
- **数量**：866/866 道具有 image_url
- **文件位置**：`frontend/public/images/items/<id>.png`（867 个文件）
- **数据库**：`items.image_url` 已全部同步
- **前端**：ItemCard + ItemDetailPage 已显示图片
- **验证**：`/items` 列表页和 `/items/:id` 详情页图片正常显示

### ✅ 角色图片 (2.5.3)
- **数量**：32/34 角色有图片
- **文件位置**：`frontend/public/images/characters/<id>.png`
- **数据库**：`characters.image_url` 已更新
- **前端**：CharacterCard + CharacterDetailPage 已显示图片
- **缺失**：
  - ID 5: ??? (小蓝人) — Wiki 无立绘图片
  - ID 17: Jacob & Esau (雅各与以扫) — Wiki 无立绘图片

### ✅ 结局图片 (2.5.4)
- **数量**：22/22 结局有图片
- **文件位置**：`frontend/public/images/endings/<id>.png`
- **数据库**：`endings.image_url` 已全部更新
- **前端**：EndingCard + EndingDetailPage 已显示图片

### ✅ 生命类型图片
- **数量**：7/7 类型
- **文件位置**：`frontend/public/images/heart/<type>.png`
- **类型**：red, soul, black, eternal, gold, bone, rotten
- **来源**：Fandom Wiki (Hearts 页面)
- **用途**：角色详情页生命值显示、角色卡片生命值显示

### ✅ 角色属性图片
- **数量**：7/7 属性
- **文件位置**：`frontend/public/images/stat/<key>.png`
- **属性**：health, damage, tears, speed, range, shot_speed, luck
- **来源**：Fandom Wiki (Attributes 页面)
- **用途**：角色详情页属性表格、道具详情页属性变化表

### ✅ 饰品图片 (2.5.2 补充)
- **数量**：187/187 饰品全部有图片 ✅
- **文件位置**：`frontend/public/images/items/<id>.png`（ID 880-1067）
- **数据库**：`items.image_url` 已全部更新
- **下载脚本**：`backend/seed_data/fetch_trinket_images.py`
- **命名格式**：`Trinket <Name> icon.png`（Fandom Wiki）
- **ID 880 补充**：`Trinket_Blue_Baby's_Soul_icon.png`（Fandom Wiki 页面图片）

### ✅ 套装卡片图片
- **修改文件**：`frontend/src/components/TransformationCard.tsx` + `.module.css`
- **改动**：空白 `<div>` 占位符 → `<img src="/images/items/{first_item_id}.png">`
- **数据来源**：API 返回 `first_item_id`（第一个所需道具的 ID）
- **图片已有**：所有道具图片（1-732）已在磁盘上

## 图片文件统计

| 目录 | 文件数 | 说明 |
|---|---|---|
| `public/images/items/` | 1054 | 道具+饰品精灵图（含 `_shared/` 子目录） |
| `public/images/characters/` | 32 | 角色立绘 |
| `public/images/endings/` | 22 | Boss 头像 |
| `public/images/heart/` | 7 | 生命类型图标 |
| `public/images/stat/` | 7 | 角色属性图标 |
| `public/images/` (根) | 3 | 首页配图（妈刀/以撒/妈心） |

## 待做

### 首页配图 (2.5.1)
- 妈刀和以撒图片不合适，待用户确认替换方案

### 道具池图片
- CLAUDE.md 约定了 pool_key 列表（treasure_room, devil_room 等）
- 需要从 Wiki 下载对应图片到 `frontend/public/images/pool/`

### 缺失图片
- ID 5 (???) 角色立绘 — Wiki 无图
- ID 17 (Jacob & Esau) 角色立绘 — Wiki 无图

## 关键发现

1. **道具图片同步**：磁盘有 867 个图片文件，但数据库 image_url 全为 NULL，需运行 `update_item_images.py` 同步
2. **角色图片 Wiki 格式**：Fandom Wiki 角色页面标题就是英文名（如 "Isaac"），不需要加 "(Character)" 后缀
3. **图片格式**：Wiki 返回 WebP 格式（不是 PNG），但以 .png 扩展名保存，浏览器能识别
4. **Lazy loading**：Wiki 页面图片在 `data-src` 属性中，`src` 包含 base64 占位符
5. **心形/属性图标**：从 Hearts 和 Attributes 页面提取，文件名格式为 `XXX_Stat_Icon.png`

## 使用的脚本

| 脚本 | 用途 |
|---|---|
| `update_item_images.py` | 同步磁盘道具图片到数据库 |
| `download_missing_character_images.py` | 下载缺失角色图片 |
| `download_character_images.py` | 批量下载角色图片（已用过） |
| `create_ui_icons.py` | 创建 UI 图标（已废弃，改用 Wiki 下载） |
