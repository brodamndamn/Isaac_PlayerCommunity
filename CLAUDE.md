# ISAAC 玩家社区

以撒的结合（The Binding of Isaac）全栈玩家社区项目。攻略资料库（道具/角色/结局图鉴）+ 玩家社区（注册登录、攻略发帖、收藏）。

技术栈：React + Vite + TypeScript / FastAPI + SQLAlchemy / MySQL 8 / JWT + Argon2 / Nginx + Uvicorn

---

## 功能清单（按实现顺序）

状态：⬜ 未开始 &nbsp; 🔄 进行中 &nbsp; ✅ 已完成

### 阶段一：项目初始化

| # | 功能 | 状态 |
|---|---|---|
| 0.1 | 前端脚手架（Vite + React + TypeScript） | ✅ |
| 0.2 | 后端脚手架（FastAPI 项目结构） | ✅ |
| 0.3 | MySQL 数据库创建 + SQLAlchemy 连接配置 | ✅ |
| 0.4 | Git 初始化 + .gitignore | ✅ |

### 阶段二：攻略数据层（道具 → 角色 → 结局）

| # | 功能 | 状态 |
|---|---|---|
| 1.1 | 道具数据模型 + 数据库迁移 | ✅ |
| 1.2 | 道具种子数据（~700 条） | ✅ |
| 1.3 | 道具列表 API（分页 + 搜索 + 分类筛选） | ✅ |
| 1.4 | 道具详情 API | ✅ |
| 1.5 | 道具列表页面 + 详情页面 | ✅ |
| 2.1 | 角色数据模型（含表里角色） | ✅ |
| 2.2 | 角色种子数据（~34 个） | ✅ |
| 2.3 | 角色列表 API + 详情 API | ✅ |
| 2.4 | 角色列表页面 + 详情页面 | ✅ |
| 3.1 | 结局数据模型 | ✅ |
| 3.2 | 结局种子数据（~20+ 个） | ✅ |
| 3.3 | 结局列表 API + 详情 API | ✅ |
| 3.4 | 结局列表页面 + 详情页面 | ✅ |

### 阶段二点五：图片资源

| # | 功能 | 状态 |
|---|---|---|
| 2.5.1 | 首页卡片配图：道具图鉴🎒→妈刀、角色资料👤→以撒、结局一览🏆→妈心 | ⬜ |
| 2.5.2 | 道具图鉴配图：列表页 719 张卡片 + 详情页道具图 + 效果图（如有） | ⬜ |
| 2.5.3 | 角色资料配图：列表页 34 张卡片 + 详情页立绘（全部/表/里 tab） | ⬜ |
| 2.5.4 | 结局一览配图：列表页 22 张 Boss 图 + 详情页 Boss 图 + 解锁道具/角色图 | ⬜ |

### 阶段三：用户系统

| # | 功能 | 状态 |
|---|---|---|
| 4.1 | 用户数据模型 + 数据库迁移 | ⬜ |
| 4.2 | 注册 API（Argon2 哈希） | ⬜ |
| 4.3 | 登录 API（返回 JWT） | ⬜ |
| 4.4 | JWT 认证中间件 | ⬜ |
| 4.5 | 注册页面 + 登录页面 | ⬜ |
| 4.6 | 前端 token 存储 + 登录状态持久化 | ⬜ |

### 阶段四：社区功能

| # | 功能 | 状态 |
|---|---|---|
| 5.1 | 攻略数据模型 | ⬜ |
| 5.2 | 创建攻略 API + 删除攻略 API（需登录） | ⬜ |
| 5.3 | 攻略列表 API（分页 + 筛选） | ⬜ |
| 5.4 | 收藏/取消收藏 API | ⬜ |
| 5.5 | 攻略列表页 + 详情页 + 创建页 | ⬜ |
| 5.6 | 我的收藏页面 | ⬜ |

### 阶段五：部署

| # | 功能 | 状态 |
|---|---|---|
| 6.1 | Nginx 配置 + Uvicorn 生产配置 | ⬜ |
| 6.2 | 前端构建 + 部署验证 | ⬜ |

---

## Skill 使用指南

### 项目专属 Skill

| Skill | 何时使用 |
|---|---|
| `isaac-fullstack` | **自动触发** — 遵循项目目录结构约定、先判断意图再行动、未经用户验证不标已完成（"检查结构符合就改"除外）。详细规范见 `SKILL.md` |

### 何时查阅 Skill 的 Reference 文件

| 场景 | 查阅文件 |
|---|---|
| 设计/修改数据库表结构 | `.claude/skills/isaac-fullstack/references/database-schema.md` |
| 新增 API 端点、不确定路由怎么写 | `.claude/skills/isaac-fullstack/references/api-conventions.md` |
| 新增前端页面或组件 | `.claude/skills/isaac-fullstack/references/frontend-conventions.md` |
| 需要下载道具/角色/结局图片 | `.claude/skills/isaac-fullstack/references/images.md` |
| 准备导入种子数据 | `.claude/skills/isaac-fullstack/references/seed-data.md` |

### 开发流程中常用的系统 Skill

| 场景 | 使用的 Skill / 命令 |
|---|---|
| 初始化项目结构、写 CLAUDE.md | `/init` |
| 完成一个功能后，验证是否正常 | `/verify` — 启动项目并实际跑一遍该功能 |
| 阶段性检查代码质量 | `/code-review` |
| 启动前端/后端看效果 | `/run` |
| 需要搜索 isaac 游戏相关技术信息 | `deep-research`（如"道具的 item pools 有哪些分类"） |

---

## 进度记录

### 2026-07-13 — 前端脚手架 ✅

- **文件**：`frontend/`（Vite + React + TypeScript 模板）
- **验证**：`cd frontend && npx tsc --noEmit && npx vite build` — 类型检查通过，构建成功
- **备注**：清理了 Vite 默认模板（App.tsx、index.css、无用资源），按约定创建了 `src/api/`、`src/components/`、`src/pages/`、`src/types/`、`src/hooks/` 子目录

### 2026-07-13 — 后端脚手架 ✅

- **文件**：`backend/app/main.py`、`backend/app/core/config.py`、`backend/requirements.txt`
- **验证**：`cd backend && python -m uvicorn app.main:app --port 8000` → 服务正常启动
- **备注**：创建了 `app/models/`、`app/schemas/`、`app/api/`、`app/core/` 包结构；含 CORS（允许 `localhost:5173`）和 `/api/v1/health` 端点

### 2026-07-13 — 数据库连接配置 ✅

- **文件**：`backend/app/core/database.py`、`backend/.env`
- **验证**：`cd backend && python -m uvicorn app.main:app --port 8000` → `[OK] 数据库连接成功: isaac_community`
- **备注**：PyMySQL + SQLAlchemy 2.0；`Base` 声明式基类 + `get_db` 依赖注入已就绪

### 2026-07-13 — 道具数据模型 + 数据库迁移 ✅

- **文件**：`backend/app/models/item.py`、`backend/alembic/`
- **验证**：`python -c "from app.core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_columns('items'))"` — 14 字段对应 schema 约定
- **备注**：Alembic 已初始化，后续新增模型只需 `alembic revision --autogenerate -m "xxx"` + `alembic upgrade head`

### 2026-07-13 — 道具种子数据 ✅

- **文件**：`backend/seed_data/fetch_items.py`、`backend/seed_data/items.json`、`backend/seed_data.py`
- **验证**：`db.query(Item).count()` → 719 条
- **备注**：`fetch_items.py` 从 Fandom Wiki API 抓取所有 wikitable + 逐页详情；`seed_data.py` 分批导入（200 条/批）。中文名需手动补充，部分分类和描述空格待修正

### 2026-07-13 — 道具列表 API ✅

- **文件**：`backend/app/api/items.py`、`backend/app/schemas/item.py`
- **验证**：`curl localhost:8000/api/v1/items?page_size=5` → 200，返回分页数据；`?category=passive&search=tears` → 组合筛选正常
- **备注**：支持 `page`/`page_size`/`search`/`category` 四个参数，响应格式符合 api-conventions

### 2026-07-13 — 道具详情 API ✅

- **文件**：`backend/app/api/items.py`
- **验证**：`/api/v1/items/1` → 200，`/api/v1/items/99999` → 404
- **备注**：`GET /api/v1/items/{id}`，返回完整 Item 字段；不存在时返回 404

### 2026-07-13 — 角色数据模型 + 数据库迁移 ✅

- **文件**：`backend/app/models/character.py`、`backend/alembic/versions/*_add_characters_table.py`
- **验证**：`inspect(engine).get_columns('characters')` → 15 字段完整
- **备注**：含 `is_tainted` 区分表里角色，`base_character_id` 自联外键关联表角色

### 2026-07-13 — 角色种子数据 ✅

- **文件**：`backend/seed_data/characters.json`、`backend/seed_data.py`
- **验证**：`db.query(Character).count()` → 34 条（17 表 + 17 里）
- **备注**：手工整理，含中英文名、生命值、初始属性、初始道具、解锁方式、角色描述

### 2026-07-13 — 角色列表 API + 详情 API ✅
- **文件**：`backend/app/api/characters.py`、`backend/app/schemas/character.py`
- **验证**：`/api/v1/characters` → 200（34个），`/api/v1/characters?is_tainted=true` → 17个，`/api/v1/characters/8` → 阿萨谢尔
- **备注**：支持分页、表/里角色筛选、名称搜索

### 2026-07-13 — 角色列表页面 + 详情页面 ✅

- **状态**：✅ 已完成
- **文件**：
  - `frontend/src/pages/CharactersPage.tsx` — 列表页（全部/表/里 tab 切换 + 卡片网格）
  - `frontend/src/pages/CharacterDetailPage.tsx` — 详情页（属性表格 + 角色特性 + 适合道具）
  - `frontend/src/components/CharacterCard.tsx` — 卡片展示组件
  - `frontend/src/components/HealthHearts.tsx` + `HealthHearts.module.css` — 生命值渲染（解析 `3❤` / `3💙` / `3❤ + 3💰` 等格式）
  - `frontend/src/api/characters.ts` — API 封装（getCharacters + getCharacterById）
  - `frontend/src/types/character.ts` — Character 类型定义
- **验证**：
  - `cd frontend && npm run dev` → `http://localhost:5173/characters` 列表页（12 卡片）+ `/characters/1` `/characters/5` `/characters/15` `/characters/17` `/characters/33` 详情页均正常
  - 心形显示：红/蓝/黑心 + 复合值（如 `3❤ + 3❤`）+ 文字（`随机`）全部按预期渲染
  - API：`/api/v1/characters` 返回 34 条，`?is_tainted=true/false` 各 17 条，`?search=Isaac` 和 `?search=以撒` 搜索正常
  - 错误：`/characters/99999` → 404，`/characters/abc` → 422（Pydantic 拦截）
- **注意事项**：
  - CharactersPage 用 useEffect `[]` 只 fetch 一次全部；tab 切换不重 fetch，三个按钮 count 永远显示 `34/17/17`
  - #15 遗骸的骨头 emoji 🦴 在 Windows 默认字体下渲染偏小（Segoe UI Emoji 旧版本对 Unicode 11.0 覆盖不全；`💙` 等老 emoji 正常）。是字体 fallback 问题，非代码 bug，可后续替换图标
  - CharactersPage 的 filter 是 React state 而非 URL query，深链/刷新会回到全部

### 2026-07-13 — 结局数据模型 ✅

- **状态**：✅ 已完成
- **文件**：
  - `backend/app/models/ending.py` — Ending 模型（11 字段，对齐 [database-schema.md](.claude/skills/isaac-fullstack/references/database-schema.md) 第 70-85 行）
  - `backend/app/models/__init__.py` — 注册 `from app.models.ending import Ending`
  - `backend/alembic/versions/74ec38e1d111_add_endings_table.py` — alembic autogen 迁移
- **验证**：
  - `python -c "from app.models.ending import Ending; ..."` 输出 11 字段，类型 + nullable 与 schema 一致
  - `alembic upgrade head` → `74ec38e1d111 (head)`，从 `f154ff715828` 升级成功
  - 实际表：`InnoDB` + `utf8mb4_unicode_ci`，`SHOW FULL COLUMNS` 显示 11 字段 + 默认值 + comment 完整
  - alembic 链路：`f38cb977c006 → 6f7512d50b5f → f154ff715828 → 74ec38e1d111`
- **注意事项**：
  - schema 故意只有 `created_at` 没 `updated_at`（与 characters/items 一致；只有 users/guides 有 updated_at）
  - 没有外键自联（endings 表无需表里区分）
  - 之前模型阶段没写 `fetch_endings.py`——按 [seed-data.md](.claude/skills/isaac-fullstack/references/seed-data.md) 第 7 行约定，留到 3.2 写抓取脚本

### 2026-07-13 — 结局种子数据 ✅

- **状态**：✅ 已完成
- **文件**：
  - `backend/seed_data/fetch_endings.py` — 从 Fandom Wiki Endings 页面抓取结局数据，合并手工补充的 Boss/完成方式
  - `backend/seed_data/endings.json` — 22 个结局的完整数据（Wiki 提取编号+名称 + 手工补充 boss/completion_method/unlocks）
  - `backend/seed_data.py` — 新增 `seed_endings()` 函数
- **验证**：`db.query(Ending).count()` → 22 条；11 字段全部对齐 database-schema.md；ending_number 1-22 全部正确
- **注意事项**：
  - Wiki 的 Endings 页面没有 wikitable（与 Items 不同），只有 h3 段落 + 图片 gallery，编号和名称从 h3 标题正则提取
  - Wiki API 返回的 unlocks 文本是未渲染的模板占位符（"said item"/"said character"），已手工修正为实际解锁内容
  - 编号以 Repentance DLC 最终版本为准：18=Ultra Greed, 19=Ultra Greedier, 20=Delirium, 21=Mother, 22=The Beast
  - Wiki 把 The Beast 标为 "Final Ending" 无数字编号，脚本中检测 "beast" 关键词自动分配 #22

### 2026-07-13 — 结局列表 API + 详情 API ✅

- **状态**：✅ 已完成
- **文件**：
  - `backend/app/schemas/ending.py` — EndingResponse + EndingListData Pydantic schema
  - `backend/app/api/endings.py` — 列表 `GET /api/v1/endings`（分页+搜索）+ 详情 `GET /api/v1/endings/{id}`
  - `backend/app/main.py` — 注册 `endings.router`
- **验证**：
  - `curl localhost:8000/api/v1/endings?page_size=3` → 200，返回 3 条，total=22
  - `curl localhost:8000/api/v1/endings/12` → 200，11 字段完整，中文正确
  - `curl localhost:8000/api/v1/endings/999` → 404，统一格式 `{code:404, message:"结局不存在", data:null}`
  - 搜索 `?search=Beast` 返回空 — 当前只搜 name_en/name_cn，boss_name 不在搜索范围内，与 characters API 行为一致

### 2026-07-13 — 结局列表页面 + 详情页面 ✅

- **状态**：✅ 已完成
- **文件**：
  - `frontend/src/types/ending.ts` — Ending 接口类型
  - `frontend/src/api/endings.ts` — getEndings + getEndingById API 封装
  - `frontend/src/components/EndingCard.tsx` + `.module.css` — 结局卡片（编号、Boss、完成方式、解锁）
  - `frontend/src/pages/EndingsPage.tsx` + `.module.css` — 列表页（22 张卡片网格）
  - `frontend/src/pages/EndingDetailPage.tsx` + `.module.css` — 详情页（Boss/完成方式/解锁条件/解锁内容）
  - `frontend/src/App.tsx` — ComingSoon 占位替换为正式路由
- **验证**：`npx tsc --noEmit` 通过，`npx vite build` 成功；`/endings` 和 `/endings/12` 页面正常渲染
- **注意事项**：
  - 结局数据无表/里区分，列表页比角色页简单（无 tab 切换）
  - 详情页表格包含 Boss、完成方式、解锁条件、指定角色、完成后解锁
  - 前端展示的中文译名已全部对齐灰机 wiki + 项目 characters.json/items.json 标准

### 2026-07-13 — 道具列表页面 + 详情页面 ✅

- **文件**：`frontend/src/pages/ItemsPage.tsx`、`ItemDetailPage.tsx`、`HomePage.tsx`、`frontend/src/components/ItemCard.tsx`
- **验证**：`cd frontend && npm run dev` → `http://localhost:5173/items`，分页/搜索/分类筛选/详情页均正常
- **备注**：中文效果优先展示（灰机wiki抓取），英文描述作参考。HomePage 以撒暗色主题。详情页表格布局预留了图片位

### 2026-07-13 — Git 初始化 + .gitignore ✅

- **文件**：`.gitignore`、`.git/`
- **验证**：`git status` 正常运行，`.env` 和 `node_modules/` 已被忽略
- **备注**：已忽略 Python/Node/IDE/环境变量文件；`uploads/*` 保留目录但忽略内容


---

## 项目架构与代码逻辑

### 目录结构

```
ISAAC/
├── frontend/src/              # React + Vite + TypeScript
│   ├── api/                   # axios 请求封装（client.ts + 各模块）
│   ├── components/            # 可复用组件（ItemCard, CharacterCard）
│   ├── pages/                 # 页面组件（与路由一一对应）
│   └── types/                 # TS 类型定义（api.ts, item.ts, character.ts）
├── backend/
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM 模型（item.py, character.py）
│   │   ├── schemas/           # Pydantic 响应模型（item.py, character.py）
│   │   ├── api/               # FastAPI 路由（items.py, characters.py）
│   │   ├── core/              # 基础设施（config.py, database.py, security.py）
│   │   └── main.py            # FastAPI 入口 + CORS + lifespan
│   ├── alembic/               # 数据库迁移工具
│   └── seed_data/             # 种子数据 + 抓取脚本
└── .claude/skills/isaac-fullstack/  # 项目专属 Skill
```

### 后端架构（已完成部分）

**数据层**（`app/models/`）：
- `item.py` — 道具表 14 字段（id, name_en/cn, category, quality, description, effect, unlock_method, pick_up_text, recharge_time, image_url, item_pools, suitable_characters, created_at）
- `character.py` — 角色表 15 字段（id, name_en/cn, is_tainted, base_character_id[自联FK], health, damage/speed/tears, starting_items[JSON], unlock_method, description, suitable_items[JSON], image_url）
- 所有模型继承 `app/core/database.py` 的 `Base`，通过 `get_db()` 依赖注入获取会话
- 迁移用 Alembic：`alembic revision --autogenerate -m "xxx"` → `alembic upgrade head`

**API 层**（`app/api/`）：
- 每个资源一个 Router 文件（`items.py`, `characters.py`），prefix `/api/v1/xxx`
- 统一响应格式 `{ code: 200, message: "ok", data: {...} }`
- 列表接口支持 `page`/`page_size`/`search` 参数
- 详情接口 `GET /{id}`，不存在返回 404
- 路由在 `main.py` 中 `app.include_router()` 注册

**数据流**：Client → FastAPI Router → `get_db()` 会话 → SQLAlchemy Model → MySQL → Pydantic Schema → JSON 响应

**种子数据流**：
1. `fetch_items.py` → Fandom Wiki API → `items.json`（720 条，英文）
2. `fetch_cn_names.py` → 灰机 wiki API → 中文名合并到 `items.json`
3. `fetch_cn_effects.py` → 灰机 wiki API → 中文效果合并到 `items.json`
4. `characters.json` — 手工整理的 34 个角色
5. `seed_data.py` → 读取 JSON → `db.merge()` → MySQL

### 前端架构（已完成部分）

**路由**（App.tsx）：React Router v6
- `/` → HomePage（以撒暗色主题首页 + 三个入口卡片）
- `/items` → ItemsPage（分页 + 搜索 + 分类筛选）
- `/items/:id` → ItemDetailPage（属性表格 + 中文效果 + 英文参考）
- `/characters` → CharactersPage（表/里角色筛选）
- `/characters/:id` → CharacterDetailPage（属性表格 + 角色特性）

**数据流**：Page → `api/xxx.ts`（调用 client.ts 的 axios 实例）→ `/api/v1/xxx` → Vite proxy → FastAPI

**axios 拦截器**（`api/client.ts`）：请求自动附加 `Bearer token`，响应 401 自动清除 token 并跳转 `/login`

**样式**：CSS Modules（`*.module.css`），组件和页面各自维护

---

## 当前状态速览

### 已完成（17/32）

| 模块 | 完成项 |
|---|---|
| 项目初始化 (0.x) | 前端脚手架、后端脚手架、数据库连接、Git |
| 道具系统 (1.x) | 数据模型、种子数据(719条)、列表API、详情API、前端页面 |
| 角色系统 (2.x) | 数据模型、种子数据(34个)、列表API、详情API、前端页面 |
| 结局系统 (3.x) | 数据模型、种子数据(22个)、列表API、详情API、前端页面 |

### 即将做

| 顺序 | 模块 |
|---|---|
| 2.5.1~2.5.4 | 图片资源（首页/道具/角色/结局全部配图） |
| 4.1~4.6 | 用户系统（注册登录 + JWT） |
| 5.1~5.6 | 社区功能（攻略发帖 + 收藏） |
| 6.1~6.2 | 部署 |

---

## 环境信息

- 项目路径：`d:\暑假task\ISAAC`
- 后端端口：`8000` / 前端端口：`5173`
- MySQL 数据库名：`isaac_community`
