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
| 1.2 | 道具种子数据（~700 条） | ⬜ |
| 1.3 | 道具列表 API（分页 + 搜索 + 分类筛选） | ⬜ |
| 1.4 | 道具详情 API | ⬜ |
| 1.5 | 道具列表页面 + 详情页面 | ⬜ |
| 2.1 | 角色数据模型（含表里角色） | ⬜ |
| 2.2 | 角色种子数据（~34 个） | ⬜ |
| 2.3 | 角色列表 API + 详情 API | ⬜ |
| 2.4 | 角色列表页面 + 详情页面 | ⬜ |
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
| `isaac-fullstack` | **自动触发** — 遵循项目目录结构约定、先判断意图再行动、未经用户验证不标已完成。详细规范见 `SKILL.md` |

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

### 2026-07-13 — Git 初始化 + .gitignore ✅

- **文件**：`.gitignore`、`.git/`
- **验证**：`git status` 正常运行，`.env` 和 `node_modules/` 已被忽略
- **备注**：已忽略 Python/Node/IDE/环境变量文件；`uploads/*` 保留目录但忽略内容


---

## 环境信息

- 项目路径：`d:\暑假task\ISAAC`
- 后端端口：`8000` / 前端端口：`5173`
- MySQL 数据库名：`isaac_community`
