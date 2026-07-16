# 图片 & 数据修正任务状态

## 最后更新：2026-07-16

---

## 一、已完成

### 2026-07-14 — 图片系统完整重构 ✅
- 866/866 item 全部 image_url 可用
- 列表页/详情页都显示像素精灵图
- 列表页左图右文字布局，详情页 128×128

### 2026-07-14 — 卡牌药丸翻译补全 ✅
- 卡牌 97/97 中文名+效果
- 药丸 49/50 中文名 + 50/50 中文效果

### 2026-07-14 — 结局界面图片 ✅
- Boss 图片列表页 96×96，详情页 128×128
- 详情页"完成后解锁"显示道具/角色图片

### 2026-07-14 — 套装详情页图片 ✅
- 详情页标题区显示第一个所需道具的图片

### 2026-07-15 — 套装数据修正 ✅
- 数据库从 19 个套装修正为 15 个
- 所有 required_items 按 wiki 对齐
- 前端移除英文名显示

### 2026-07-16 — 首页卡片配图 ✅
- emoji（🎒👤🏆）替换为游戏图片
- 道具图鉴 → `images/items/114.png`（妈刀 sprite）
- 角色资料 → `images/characters/1.png`（以撒立绘）
- 结局一览 → `images/moms-heart.png`（妈心 boss 图）
- 图片尺寸从 64px 放大到 96px
- 道具计数从 "700+" 改为 "1000+"
- **涉及文件**：
  - `frontend/src/pages/HomePage.tsx` — SECTIONS 的 icon→image，JSX 用 `<img>` 替换 emoji
  - `frontend/src/pages/HomePage.module.css` — `.cardImage` 96×96 + pixelated

### 2026-07-16 — 角色页生命类型贴图 ✅
- HeartTypes 组件：占位符 `<span data-heart>` → `<img src="/images/heart/{key}.png">`
- 7 张心形图片（red/soul/black/eternal/gold/bone/rotten）已在 `public/images/heart/`
- **涉及文件**：
  - `frontend/src/components/HeartTypes.tsx` — `<span>` → `<img>`
  - `frontend/src/components/HeartTypes.module.css` — `.icon` 22×22 + pixelated

### 2026-07-16 — 角色卡片生命值+攻击力贴图 ✅
- HealthHearts 组件重写：emoji→图片映射（❤→red, 💙→soul, 🖤→black, 💛→gold, 🤍→eternal, 🦴→bone, 💚→rotten, 💰→coin）
- 新增 `size` 参数控制图片尺寸
- 卡片布局重构：生命值/攻击/速度/射速排成一行，各自带图标
- **涉及文件**：
  - `frontend/src/components/HealthHearts.tsx` — 完全重写，支持图片渲染
  - `frontend/src/components/HealthHearts.module.css` — flex 布局
  - `frontend/src/components/CharacterCard.tsx` — 引入 HealthHearts，statsRow 布局
  - `frontend/src/components/CharacterCard.module.css` — `.statsRow` + `.stat` + `.statIcon`

### 2026-07-16 — 角色详情页生命值贴图 ✅
- 详情页生命值从手写占位符改为 HealthHearts 组件
- 属性列表改回表格样式（和道具详情页一致），标题为"初始属性"
- **涉及文件**：
  - `frontend/src/pages/CharacterDetailPage.tsx` — 引入 HealthHearts，删除 HEART_ICONS 映射
  - `frontend/src/pages/CharacterDetailPage.module.css` — 删除 .heartItem，.statIcon 去掉灰色背景

### 2026-07-16 — 店主硬币生命值贴图 ✅
- 从 Fandom Wiki 下载硬币 sprite → `public/images/heart/coin.png`
- HealthHearts 映射表加了 `"💰": "coin"`
- 店主 (ID 13) 和里店主 (ID 30) 的 `2💰` 会显示 2 张硬币图片
- **涉及文件**：
  - `backend/seed_data/fetch_coin_image.py` — 下载脚本

### 2026-07-16 — 道具池+属性图标 ✅
- `public/images/pool/` — pool 图标（treasure_room, devil_room 等）
- `public/images/stat/` — stat 图标（damage, tears, speed, luck, range, shot_speed, health）

---

## 二、进行中

（无）

---

## 三、待做（图片相关）

### 2.5.2-a ? Card (ID 844)
- 缺独立 sprite，目前 fallback 到 tarot_normal
- 待用户决定 fallback 方案

### 2.5.3 角色资料配图
- 列表页 34 张卡片立绘 ✅（已有 `characters/<id>.png`）
- 详情页角色立绘 ✅（已有）
- 角色属性图标 ✅（已有 `stat/` 目录）

### 道具池图片
- pool 图标 ✅（已有 `pool/` 目录）
- stat 图标 ✅（已有 `stat/` 目录）

---

## 四、待做（非图片）

### 用户系统（阶段三）
- 4.1~4.6：注册登录 + JWT

### 社区功能（阶段四）
- 5.1~5.6：攻略发帖 + 收藏

### 部署（阶段五）
- 6.1~6.2：Nginx + Uvicorn 生产配置

---

## 五、关键文件索引

### 前端组件
| 文件 | 用途 |
|---|---|
| `frontend/src/components/HealthHearts.tsx` | 心形图片渲染（emoji→图片映射，支持 size 参数） |
| `frontend/src/components/HealthHearts.module.css` | HealthHearts 样式 |
| `frontend/src/components/HeartTypes.tsx` | 生命类型卡片（7 种心形图片） |
| `frontend/src/components/CharacterCard.tsx` | 角色卡片（图片立绘 + 属性行） |
| `frontend/src/pages/CharacterDetailPage.tsx` | 角色详情页（HealthHearts + 表格属性） |
| `frontend/src/pages/HomePage.tsx` | 首页（3 张卡片图片） |

### 图片目录
| 目录 | 内容 |
|---|---|
| `frontend/public/images/heart/` | 8 张心形图片（red/soul/black/eternal/gold/bone/rotten/coin） |
| `frontend/public/images/stat/` | 7 张属性图标（damage/speed/tears/luck/range/shot_speed/health） |
| `frontend/public/images/pool/` | 道具池图标 |
| `frontend/public/images/characters/` | 34 张角色立绘 |
| `frontend/public/images/items/` | 866 张道具 sprite |
| `frontend/public/images/endings/` | 22 张 Boss 头像 |

### 后端脚本
| 文件 | 用途 |
|---|---|
| `backend/seed_data/fetch_coin_image.py` | 下载硬币 sprite |

---

## 六、Emoji→图片映射表（HealthHearts）

| Emoji | 图片文件 | 用途 |
|---|---|---|
| ❤ | heart/red.png | 红心 |
| 💙 | heart/soul.png | 魂心 |
| 🖤 | heart/black.png | 黑心 |
| 💛 | heart/gold.png | 金心 |
| 🤍 | heart/eternal.png | 永恒之心 |
| 🦴 | heart/bone.png | 骨心 |
| 💚 | heart/rotten.png | 腐心 |
| 💰 | heart/coin.png | 硬币（店主专用） |