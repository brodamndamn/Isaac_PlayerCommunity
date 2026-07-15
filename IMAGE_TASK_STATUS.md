# 图片 & 数据修正任务状态

## 最后更新：2026-07-15

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
- ID 16 超级撒但换图（ingame sprite）
- ID 19 究极大贪婪换图（ingame sprite）
- 详情页"完成后解锁"显示道具/角色图片（15 个 enrich）
- D6 别名修复：`_ALIAS_ITEM = {'D6': '六面骰'}`

### 2026-07-14 — 套装详情页图片 ✅
- 详情页标题区显示第一个所需道具的图片
- `_enrich` 函数增加 `first_item_id` 查找

### 2026-07-15 — 套装数据修正 ✅

**状态**：✅ 已完成（两轮修正）

**数据来源**：Fandom wiki（英文 required_items）+ 灰机 wiki（中文名称和效果）

**第一轮修正**：
- 数据库从 19 个套装修正为 **15 个**（删除 Mom/Angel/Planetarium + 重编号）
- 所有 15 个套装的 `required_items` 按 wiki collectible table 完全对齐
- 中文名统一为灰机 wiki 标准

**第二轮修正**（名称匹配 + 前端去英文）：
- 7 个套装修正了道具名称大小写/格式不匹配问题
- 前端移除所有英文名显示

**删除的套装**：
| 旧 ID | 名称 | 原因 |
|---|---|---|
| #9 | Mom | Wiki 不存在，是 Yes Mother? 的旧版 |
| #16 | Stompy (旧) | 重编号为 #13 |
| #17 | Adult (旧) | 重编号为 #14 |
| #18 | Angel | Wiki 不存在，是 Seraphim 的旧版 |
| #19 | Planetarium | Wiki 不存在 |

**第二轮名称修正**：
| 套装 | 修正前 | 修正后 | 原因 |
|---|---|---|---|
| 嗝屁猫！ | 缺 Kid's Drawing | +Kid's Drawing | Fandom wiki 遗漏（饰品） |
| 别西卜！ | Forever Alone | Forever alone | DB 大小写不匹配 |
| 利维坦！ | 缺 Sulfur | +Sulfur | Fandom wiki 遗漏 |
| 利维坦！ | Maw of the Void | Maw Of The Void | DB 大小写不匹配 |
| 拉了！ | Number Two | No. 2 | 游戏内实际名称 |
| 肆意践踏！ | One Makes You Larger pill | One makes you larger | 去掉 pill 后缀 |
| 成人！ | Puberty pill | Puberty | 去掉 pill 后缀 |
| 蜘蛛宝宝！ | Spider Baby (重复) | Spiderbaby | 去空格 + 去重 (17→16) |

**最终 15 个套装**：

| ID | 中文名 | 英文名 | 道具数 |
|---|---|---|---|
| 1 | 嗝屁猫！ | Guppy | 8 |
| 2 | 别西卜！ | Beelzebub | 25 |
| 3 | 蘑菇头！ | Fun Guy | 10 |
| 4 | 鲍勃！ | Bob | 5 |
| 5 | 书虫！ | Bookworm | 15 |
| 6 | 连体！ | Conjoined | 31 |
| 7 | 好的妈妈？！ | Yes Mother? | 21 |
| 8 | 利维坦！ | Leviathan | 11 |
| 9 | 拉了！ | Oh Crap | 10 |
| 10 | 撒拉弗！ | Seraphim | 19 |
| 11 | 嗑药！ | Spun | 8 |
| 12 | 乞丐套装 | Super Bum | 3 |
| 13 | 肆意践踏！ | Stompy | 3 |
| 14 | 成人！ | Adult | 1 |
| 15 | 蜘蛛宝宝！ | Spider Baby | 16 |

**涉及文件**：
- `backend/seed_data/transformations.json` — 修正后的种子数据
- `frontend/src/pages/TransformationDetailPage.tsx` — 移除英文名显示
- `frontend/src/components/TransformationCard.tsx` — 移除英文名显示
- 数据库 `transformations` 表 — 直接 UPDATE

**验证**：
- 所有 15 个套装的 required_items 都能在 items 表中找到对应中文名
- 前端页面不再显示英文文本
- `npx tsc --noEmit` + `npx vite build` 通过

**注意事项**：
- 灰机 wiki 有 16 个套装（多一个"死灵法师！Necromancer"，来自忏悔+ DLC），但 Fandom wiki 暂无此数据，未加入数据库
- `transformations.json` 中 `items_needed` 全部为3（Stompy 和 Adult 虽然是药丸触发，但也需要3次）

---

## 二、进行中

（无）

---

## 三、待做（图片相关）

### 2.5.1 首页卡片配图
- 妈刀和以撒图片不合适，待用户确认替换方案
- 妈心图片 OK

### 2.5.2 道具图鉴配图
- 列表页 866 张卡片 ✅
- 详情页道具图 ✅
- 详情页效果图 ⬜（大部分道具没有效果图）

### 2.5.2-a ? Card (ID 844)
- 缺独立 sprite，目前 fallback 到 tarot_normal
- 待用户决定 fallback 方案

### 2.5.3 角色资料配图 ⬜
- 列表页 34 张卡片（64×64 立绘）
- 详情页角色立绘（需按表/里角色区分）
- 需要从 wiki 下载角色图片

### 2.5.4 结局一览配图 ✅
- 列表页 22 张 Boss 图（96×96）✅
- 详情页 Boss 图（128×128）✅
- 详情页解锁道具/角色图 ✅

### 道具池图片下载 ⬜
- pool 图标（treasure_room, devil_room 等）到 `frontend/public/images/pool/`
- stat 图标（damage, tears, speed 等）到 `frontend/public/images/stat/`

---

## 四、待做（非图片）

### 用户系统（阶段三）
- 4.1~4.6：注册登录 + JWT

### 社区功能（阶段四）
- 5.1~5.6：攻略发帖 + 收藏

### 部署（阶段五）
- 6.1~6.2：Nginx + Uvicorn 生产配置
