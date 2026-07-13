---
name: isaac-fullstack
description: ISAAC 玩家社区全栈项目开发技能。当用户提到 ISAAC 项目、以撒、isaac 游戏社区、道具图鉴、角色攻略、玩家社区功能，或在此项目目录下进行 React+FastAPI+MySQL 全栈开发时使用此技能。包含项目技术栈、功能模块追踪、进度记录规则、图片资源获取指南、数据库设计规范、API 约定和前端组件规范。
---

# ISAAC 玩家社区 — 全栈项目技能

> 项目概述、技术栈、功能清单和完成状态见项目根目录的 `CLAUDE.md`。本文件聚焦开发规范。

## 项目目录结构

```
ISAAC/
├── frontend/                  # React + Vite 前端
│   ├── src/
│   │   ├── api/               # API 请求封装（axios 实例 + 各模块 API）
│   │   ├── components/        # 可复用展示组件
│   │   ├── pages/             # 页面级组件（与路由一一对应）
│   │   ├── types/             # TypeScript 类型定义
│   │   ├── App.tsx            # 根组件 + 路由配置
│   │   └── main.tsx           # 入口文件
│   └── ...
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── api/               # 路由处理器（按模块拆分）
│   │   ├── core/              # 配置、安全（JWT、密码哈希）、依赖注入
│   │   └── main.py            # FastAPI 应用入口
│   ├── uploads/               # 用户上传文件目录
│   ├── seed_data.py           # 种子数据脚本
│   └── requirements.txt
├── CLAUDE.md                  # 项目进度追踪文件（自动维护）
└── .claude/skills/isaac-fullstack/  # 本技能目录
```

## 工作方式

- **收到用户消息时，先判断意图再行动**：疑问句 ≠ 执行指令。如果用户只是提问、确认状态、讨论方案，只需回答，不要趁机修改文件或扩展目录结构
- **只有用户明确要求实现某个功能时，才动手改代码**。不确定意图时先问，不要猜着改
- **实现功能时，严格遵循本 skill 和 `CLAUDE.md` 定义的项目目录结构**，文件放到约定位置，不要自创目录或偏离命名规范

## 进度追踪规则

状态流转规则（严格遵守）：

- **开始实现某个功能时**：将 `⬜` 改为 `🔄`，表示"进行中"
- **实现完成后**：保持 `🔄`，**不能自行改为 `✅`**——等用户亲自验证通过后，由用户确认或要求你再改
- **用户说"检查是否符合项目结构，符合就改成已完成"时**：对照 skill 和 CLAUDE.md 中的约定逐项检查，全部符合则直接改 `✅` + 追加记录，无需再次确认
- **其他情况**：等用户亲自验证通过后，由用户确认或要求你再改

核心原则：**未经用户验证，不得标记为已完成**。但"检查结构→自改已完成"是唯一的例外。

### 更新格式

在 `CLAUDE.md` 的"已完成功能"区域，按以下格式追加一条记录：

```markdown
### YYYY-MM-DD — 功能名称

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/models/xxx.py` — 数据模型定义
  - `backend/app/api/xxx.py` — API 路由
  - `frontend/src/pages/XxxPage.tsx` — 前端页面
- **如何验证**：`cd backend && uvicorn app.main:app --reload`，访问 `http://localhost:8000/api/v1/xxx`
- **注意事项**：（如有特殊配置、踩坑记录等，写在这里）
```

同时更新功能清单表格中对应行的状态标记（⬜ → ✅）。

### 为什么这样做

上下文窗口有长度限制，长对话会被压缩。如果 CLAUDE.md 里记录了已完成功能和实现细节，即使上下文被截断，新的 Claude 实例也能从 CLAUDE.md 中恢复项目状态，知道哪些做完了、怎么做的、代码在哪，从而准确接续工作。

## 开发顺序建议

1. **项目初始化** — 前后端脚手架搭建
2. **数据库** — 创建所有数据模型，运行迁移
3. **种子数据** — 导入道具、角色、结局的基础数据
4. **攻略 API** — 道具/角色/结局的只读 API（不需要用户系统）
5. **攻略页面** — 前端展示页面（可以先看到效果）
6. **图片资源** — 下载道具/角色/Boss 图片，更新数据库 image_url，替换前端 emoji/占位符（阶段二点五）
7. **用户系统** — 注册、登录、JWT 中间件
8. **社区 API** — 创建攻略、删除、收藏（需要认证）
9. **社区页面** — 发帖、收藏页面
10. **部署** — Nginx + Uvicorn 生产配置

先做只读展示（道具/角色/结局），让项目尽早有可见成果，再做需要用户系统的社区功能。

## 图片资源

《以撒的结合》道具、角色、结局的精灵图/图标获取方式，详见 [references/images.md](references/images.md)。

**阶段二点五 — 配图任务总览：**

| 任务 | 范围 | 图片类型 | 存储路径 |
|---|---|---|---|
| 2.5.1 首页卡片 | 3 张（妈刀、以撒、妈心） | 道具/角色/Boss 图标 | `frontend/public/images/` |
| 2.5.2 道具配图 | 719 个道具 | 精灵图 + 效果截图 | `frontend/public/images/items/` |
| 2.5.3 角色配图 | 34 个角色 | 角色立绘 | `frontend/public/images/characters/` |
| 2.5.4 结局配图 | 22 个结局 | Boss 图 + 解锁道具/角色图 | `frontend/public/images/endings/` |

**通用流程（每个子任务都遵循）：**
1. 从 Fandom Rebirth Wiki 逐张下载图片（右键 → 在新标签页中打开图片 → 保存 PNG）
2. 图片尺寸统一处理（道具 64×64、角色立绘 128×128、Boss 图 128×128）
3. 文件命名：英文小写 + 短横线（如 `moms-knife.png`、`azazel.png`）
4. 存入对应 `frontend/public/images/` 子目录
5. 更新数据库对应 `image_url` 字段（相对路径，如 `items/moms-knife.png`）
6. 修改前端组件：将 emoji/占位 div 替换为 `<img>` 标签，src 指向数据库 `image_url` 或默认路径

简要原则：
- 个人资料站使用 Wiki 图片属于合理使用，需标注版权归 Edmund McMillen / Nicalis
- 推荐从 Fandom Rebirth Wiki 逐张下载（最方便），或从 The Spriters Resource 批量下载精灵表
- 不要打包分发游戏原始资源文件
- 项目中存储图片时道具图标统一为 64x64 PNG，角色/Boss 立绘统一为 128×128 PNG

## 技术规范

以下约定在各 reference 文件中详细说明，开发时请参考：

- **数据库表设计**：[references/database-schema.md](references/database-schema.md) — 6 张核心表的完整字段定义
- **API 端点约定**：[references/api-conventions.md](references/api-conventions.md) — RESTful 路由、响应格式、分页、JWT
- **前端组件规范**：[references/frontend-conventions.md](references/frontend-conventions.md) — 目录结构、命名、类型定义
- **种子数据指南**：[references/seed-data.md](references/seed-data.md) — 数据来源、脚本编写方式

开发某模块前，先阅读对应的 reference 文件，确保风格一致。
