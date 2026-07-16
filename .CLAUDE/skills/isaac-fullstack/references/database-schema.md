# 数据库表设计

## 约定

- 表名：小写复数（`users`, `items`, `characters`, `endings`, `guides`, `favorites`）
- 主键：统一 `id`，自增整数
- 时间戳：`created_at` + `updated_at`，使用 `DATETIME`，由 SQLAlchemy 自动维护
- 枚举类型字段使用 `VARCHAR` 配合 Python `Enum` 约束
- 引擎：InnoDB，字符集 utf8mb4

---

## users — 用户表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 用户 ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | Argon2 哈希后的密码 |
| avatar | VARCHAR(255) | NULLABLE | 头像路径（相对于 uploads/） |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 注册时间 |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | 更新时间 |

---

## items — 道具表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 道具 ID（对应游戏内 item id） |
| name_en | VARCHAR(100) | NOT NULL | 英文名 |
| name_cn | VARCHAR(100) | NOT NULL | 中文名 |
| category | VARCHAR(50) | NOT NULL | 分类：active（主动）/ passive（被动）/ trinket（饰品）/ card（卡牌）/ pill（药丸） |
| quality | TINYINT | NULLABLE | 品质等级 0-4 |
| description | TEXT | NOT NULL | 道具功能详细描述 |
| effect | TEXT | NULLABLE | 具体效果和机制说明 |
| unlock_method | TEXT | NULLABLE | 解锁方式 |
| suitable_characters | JSON | NULLABLE | 适合使用的角色 ID 数组，如 `[1, 3, 5]` |
| image_url | VARCHAR(255) | NULLABLE | 道具图片路径（相对路径） |
| pick_up_text | VARCHAR(255) | NULLABLE | 拾取时显示的文字（Flavor text） |
| recharge_time | VARCHAR(50) | NULLABLE | 充能时间（仅主动道具有效） |
| item_pools | JSON | NULLABLE | 可能出现此道具的道具池 |
| created_at | DATETIME | NOT NULL | 创建时间 |

---

## characters — 角色表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 角色 ID |
| name_en | VARCHAR(50) | NOT NULL | 英文名 |
| name_cn | VARCHAR(50) | NOT NULL | 中文名 |
| is_tainted | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否为表角色（里角色为 TRUE） |
| base_character_id | INT | NULLABLE, FK→characters.id | 如果是里角色，关联对应的表角色 |
| health | VARCHAR(50) | NOT NULL | 生命值（如 "3❤ + 1🖤"） |
| damage | DECIMAL(4,2) | NULLABLE | 初始攻击力 |
| speed | DECIMAL(4,2) | NULLABLE | 初始速度 |
| tears | DECIMAL(4,2) | NULLABLE | 初始射速 |
| starting_items | JSON | NULLABLE | 初始携带道具 ID 数组 |
| unlock_method | TEXT | NULLABLE | 解锁方式 |
| description | TEXT | NULLABLE | 角色特性描述 |
| suitable_items | JSON | NULLABLE | 适合使用的道具 ID 数组 |
| image_url | VARCHAR(255) | NULLABLE | 角色图片路径 |
| created_at | DATETIME | NOT NULL | 创建时间 |

---

## endings — 结局表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 结局 ID |
| name_en | VARCHAR(100) | NOT NULL | 英文名 |
| name_cn | VARCHAR(100) | NOT NULL | 中文名 |
| ending_number | INT | NOT NULL | 结局编号（游戏内编号 1-22+） |
| completion_method | TEXT | NOT NULL | 完成方式（如"击败 Mega Satan"） |
| unlock_method | TEXT | NULLABLE | 解锁该结局区域的条件 |
| required_character | VARCHAR(50) | NULLABLE | 是否强制某一角色（填角色名，NULL 表示不强制） |
| boss_name | VARCHAR(100) | NOT NULL | 最终 Boss 名称 |
| unlocks | JSON | NULLABLE | 完成后解锁的内容（角色/道具名称数组） |
| image_url | VARCHAR(255) | NULLABLE | 结局画面图片路径 |
| created_at | DATETIME | NOT NULL | 创建时间 |

---

## guides — 攻略表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 攻略 ID |
| title | VARCHAR(200) | NOT NULL | 标题 |
| content | TEXT | NOT NULL | 正文（Markdown 格式） |
| author_id | INT | FK→users.id, NOT NULL | 作者 ID |
| category | VARCHAR(50) | NOT NULL | 分类：item / character / ending / general |
| related_item_id | INT | NULLABLE, FK→items.id | 关联道具（攻略关于某个道具时填写） |
| related_character_id | INT | NULLABLE, FK→characters.id | 关联角色 |
| related_ending_id | INT | NULLABLE, FK→endings.id | 关联结局 |
| created_at | DATETIME | NOT NULL | 发布时间 |
| updated_at | DATETIME | NOT NULL | 最后编辑时间 |

---

## favorites — 收藏表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 收藏记录 ID |
| user_id | INT | FK→users.id, NOT NULL | 收藏用户 ID |
| guide_id | INT | FK→guides.id, NOT NULL | 被收藏攻略 ID |
| created_at | DATETIME | NOT NULL | 收藏时间 |

UNIQUE 约束：`UNIQUE(user_id, guide_id)` — 同一用户对同一攻略只能收藏一次。

---

## likes — 点赞表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 点赞记录 ID |
| user_id | INT | FK→users.id, NOT NULL | 点赞用户 ID |
| guide_id | INT | FK→guides.id, NOT NULL | 被点赞攻略 ID |
| created_at | DATETIME | NOT NULL | 点赞时间 |

UNIQUE 约束：`UNIQUE(user_id, guide_id)` — 同一用户对同一攻略只能点赞一次。

---

## comments — 评论表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | 评论 ID |
| guide_id | INT | FK→guides.id, NOT NULL | 所属攻略 ID |
| user_id | INT | FK→users.id, NOT NULL | 评论者 ID |
| content | TEXT | NOT NULL | 评论内容 |
| created_at | DATETIME | NOT NULL | 评论时间 |

---

## ER 关系概览

```
users ──< guides ──< favorites >── users
        │       └──< likes >── users
        │       └──< comments >── users
        │
┌───────┼────────┐
▼       ▼        ▼
items  characters  endings
```

- 一个用户可以发布多篇攻略
- 一篇攻略可以关联一个道具/角色/结局（可选）
- 一个用户可以收藏多篇攻略，一篇攻略可以被多个用户收藏（多对多）
- 一个用户可以点赞多篇攻略，一篇攻略可以被多个用户点赞（多对多）
- 一个用户可以对多篇攻略发表多条评论，一篇攻略可以有多个用户的评论（一对多）
