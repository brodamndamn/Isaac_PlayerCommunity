# 种子数据指南

## 概述

种子数据脚本用于向数据库批量导入 Isaac 游戏的基础数据（道具、角色、结局），避免手工逐条录入。

脚本位置：`backend/seed_data.py`

运行方式：
```bash
cd backend
python seed_data.py
```

## 数据量预估

| 数据类别 | 预估数量 | 数据来源 |
|---|---|---|
| 道具（Items） | ~700+ | Fandom Rebirth Wiki |
| 饰品（Trinkets） | ~180+ | Fandom Rebirth Wiki |
| 卡牌/符文（Cards & Runes） | ~60+ | Fandom Rebirth Wiki |
| 角色（Characters） | 34（17 表 + 17 里） | Fandom Wiki |
| 结局（Endings） | 22+ | Fandom Wiki |

## 数据来源建议

种子数据优先手工整理关键字段，图片逐张下载存于 `frontend/public/images/`：

1. **道具数据**：从 Fandom Wiki 的 Items 页面出发，逐页抓取或手工整理
2. **角色数据**：Fandom Characters 分类页
3. **结局数据**：Fandom Endings 页面

### 实用链接

- 道具备份列表：https://bindingofisaacrebirth.fandom.com/wiki/Items
- 角色列表：https://bindingofisaacrebirth.fandom.com/wiki/Characters
- 结局列表：https://bindingofisaacrebirth.fandom.com/wiki/Endings

## 脚本结构建议

```python
# backend/seed_data.py

from app.database import SessionLocal
from app.models import Item, Character, Ending

def seed_items(db):
    """导入道具种子数据"""
    items_data = [
        {
            "id": 1,
            "name_en": "The Sad Onion",
            "name_cn": "伤心洋葱",
            "category": "passive",
            "quality": 3,
            "description": "Tears up. You feel sad.",
            "effect": "+0.7 射速提升",
            "unlock_method": "初始即可获得",
            "pick_up_text": "Tears up",
            "image_url": "items/sad_onion.png",
        },
        # ... 更多道具
    ]
    for item_data in items_data:
        item = Item(**item_data)
        db.merge(item)  # merge 避免重复插入时主键冲突
    db.commit()

# 类似地编写 seed_characters() 和 seed_endings()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_items(db)
        seed_characters(db)
        seed_endings(db)
        print("✅ 种子数据导入完成")
    finally:
        db.close()
```

## 注意事项

- 使用 `db.merge()` 而非 `db.add()`，这样脚本可以重复运行而不会因为主键冲突报错
- 道具 ID 建议与游戏内 item id 保持一致，方便对照
- 图片文件需提前手动下载并放入对应目录
- 种子数据中的中文名和描述可以优先参考中文 Wiki 或贴吧资料
- 首次导入可能需要较长时间（700+ 条道具），可以分批提交
- 不要将所有 700 条数据硬编码在脚本里——可以维护一个 JSON 或 YAML 数据文件，由脚本读取

## 推荐数据文件结构

```
backend/
├── seed_data.py              # 导入脚本
└── seed_data/
    ├── items.json            # 道具数据（JSON 数组）
    ├── characters.json       # 角色数据
    └── endings.json          # 结局数据
```

这样数据内容和导入逻辑分离，后续修改数据不需要改代码。
