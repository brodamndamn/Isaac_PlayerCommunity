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
| 2.4 | 角色列表页面 + 详情页面 | 🔄 |
| 3.1 | 结局数据模型 | ⬜ |
| 3.2 | 结局种子数据（~20+ 个） | ⬜ |
| 3.3 | 结局列表 API + 详情 API | ⬜ |
| 3.4 | 结局列表页面 + 详情页面 | ⬜ |

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

### 已完成（13/28）

| 模块 | 完成项 |
|---|---|
| 项目初始化 (0.x) | 前端脚手架、后端脚手架、数据库连接、Git |
| 道具系统 (1.x) | 数据模型、种子数据(720条)、列表API、详情API、前端页面 |
| 角色系统 (2.x) | 数据模型、种子数据(34个)、列表API、详情API、前端页面（待验证） |

### 即将做

| 顺序 | 模块 |
|---|---|
| 2.4 | 角色前端页面验证 → ✅ |
| 3.1~3.4 | 结局系统（模型→种子→API→页面） |
| 4.1~4.6 | 用户系统（注册登录 + JWT） |
| 5.1~5.6 | 社区功能（攻略发帖 + 收藏） |
| 6.1~6.2 | 部署 |

---

## 环境信息

- 项目路径：`d:\暑假task\ISAAC`
- 后端端口：`8000` / 前端端口：`5173`
- MySQL 数据库名：`isaac_community`
