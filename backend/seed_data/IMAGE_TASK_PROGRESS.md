# 图片任务进度

## 已完成

### 1. 分析 Fandom Wiki 页面结构
- **角色立绘**：alt='Character image'，URL 格式 `Character_<Name>_appearance.png`
- **Boss 头像**：alt='Boss portrait'，URL 格式 `Boss_<Name>_portrait.png`
- Wiki 使用懒加载，真实 URL 在 `data-src` 属性中

### 2. 创建下载脚本
- 文件：`backend/seed_data/fetch_character_ending_images.py`
- 功能：从 Fandom Wiki 下载角色立绘和结局 Boss 头像
- 输出目录：
  - 角色：`frontend/public/images/characters/<id>.png`
  - 结局：`frontend/public/images/endings/<id>.png`

### 3. 首次运行结果
- 角色图片：29/34 找到 URL，但只下载了 2 张（网络问题）
- 结局图片：0/22（boss_name 是中文，需要映射到英文 Wiki 标题）

## 进行中

### 修复结局映射问题
endings.json 中的 boss_name 是中文（如"妈妈的心脏"），需要映射到英文 Wiki 标题（如"Mom's Heart"）。

中文 boss_name 列表：
- 妈妈的心脏 → Mom's Heart
- 撒旦 → Satan
- 以撒 → Isaac (Boss)
- ???（小蓝人）→ ??? (Boss)
- 羔羊 → The Lamb
- 超级撒旦 → Mega Satan
- 悬崖 → Hush
- 超级贪婪 → Ultra Greed
- 超级贪婪者 → Ultra Greedier
- 虚妄 → Delirium
- 母亲 → Mother
- 兽兽 → The Beast
- 狗教条 → Dogma
- 妈妈 → Mom

## 待做

1. **修复结局映射**：在 `fetch_character_ending_images.py` 中添加中文到英文的映射
2. **重新运行脚本**：下载所有角色和结局图片
3. **更新数据库**：
   - `UPDATE characters SET image_url = CONCAT('characters/', id, '.png') WHERE image_url IS NULL`
   - `UPDATE endings SET image_url = CONCAT('endings/', id, '.png') WHERE image_url IS NULL`
4. **验证前端显示**：检查角色和结局页面是否正常显示图片
5. **清理临时文件**：删除 `analyze_wiki_images.py` 和 `analyze_wiki_images_v2.py`

## 关键代码位置

### 角色图片
- 占位符：`frontend/src/components/CharacterCard.tsx:16-25`
- 图片路径：`/images/${character.image_url}`
- CSS：`frontend/src/components/CharacterCard.module.css:28-43`

### 结局图片
- 占位符：`frontend/src/components/EndingCard.tsx:15`
- 图片路径：需要修改为 `/images/${ending.image_url}`
- CSS：需要添加 `.bossImg` 的图片样式

### 数据库字段
- 角色：`characters.image_url` (VARCHAR 255, nullable)
- 结局：`endings.image_url` (VARCHAR 255, nullable)

## 注意事项

1. Wiki API 有限流，脚本中已添加 `await asyncio.sleep(0.3)`
2. 部分角色 Wiki 页面标题与 name_en 不同（如 "Jacob & Esau" vs "Jacob and Esau"）
3. 里角色（Tainted）的 Wiki 页面标题格式是 "Tainted <Name>"
4. 图片文件是 WebP 格式，但以 .png 扩展名保存（浏览器能识别）
