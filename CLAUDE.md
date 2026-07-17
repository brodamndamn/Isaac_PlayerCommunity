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

### 阶段三：用户系统

| # | 功能 | 状态 |
|---|---|---|
| 4.1 | 用户数据模型 + 数据库迁移 | ✅ |
| 4.2 | 注册 API（Argon2 哈希） | ✅ |
| 4.3 | 登录 API（返回 JWT） | ✅ |
| 4.4 | JWT 认证中间件 | ✅ |
| 4.5 | 注册页面 + 登录页面 | ✅ |
| 4.6 | 前端 token 存储 + 登录状态持久化 | ✅ |

### 阶段四：社区功能

| # | 功能 | 状态 |
|---|---|---|
| 5.1 | 攻略数据模型 | ✅ |
| 5.2 | 创建攻略 API + 删除攻略 API（需登录） | ✅ |
| 5.3 | 攻略列表 API（分页 + 筛选） | ✅ |
| 5.4 | 收藏/取消收藏 API | ✅ |
| 5.5 | 攻略列表页 + 详情页 + 创建页 | ✅ |
| 5.6 | 我的收藏页面 | ✅ |
| 5.7 | 点赞数据模型 + 数据库迁移 | ✅ |
| 5.8 | 点赞/取消点赞 API（需登录） | ✅ |
| 5.9 | 评论数据模型 + 数据库迁移 | ✅ |
| 5.10 | 发表/删除评论 API（需登录） | ✅ |
| 5.11 | 头像上传 API（需登录） | ✅ |

### 阶段五：部署

#### 部署架构

```
浏览器 (80/443)
  │
  ▼
Nginx
  ├── /              → 前端静态文件 (/var/www/isaac)
  ├── /api/*         → proxy_pass → 127.0.0.1:8000
  └── /uploads/*     → proxy_pass → 127.0.0.1:8000
                            │
                            ▼
                    Uvicorn (systemd 守护)
                            │
                            ▼
                       MySQL 8.0
```

#### 6.1 服务器环境准备

- 操作系统：Ubuntu 22.04+ / Debian 12+
- 安装依赖：
  ```bash
  sudo apt update
  sudo apt install nginx mysql-server python3 python3-pip python3-venv -y
  ```
- 启动并启用 Nginx / MySQL：
  ```bash
  sudo systemctl enable --now nginx mysql
  ```

#### 6.2 MySQL 建库建用户

```sql
CREATE DATABASE isaac_community CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'isaac'@'localhost' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON isaac_community.* TO 'isaac'@'localhost';
FLUSH PRIVILEGES;
```

#### 6.3 后端部署

```bash
# 放置代码
cd /opt
git clone <仓库地址> isaac
# 或 scp backend/ 到 /opt/isaac/

# 虚拟环境
cd /opt/isaac/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

创建 `.env`（生产配置）：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=isaac
DB_PASSWORD=你的密码
DB_NAME=isaac_community
JWT_SECRET=<python3 -c "import secrets; print(secrets.token_hex(32))">
DEBUG=False
```

初始化数据库：
```bash
source venv/bin/activate
alembic upgrade head
python seed_data.py
```

#### 6.4 代码层面生产配置修改

部署前需要改两个文件：

**`backend/app/core/config.py`** — `DEBUG` 默认值从 `True` 改 `False`：
```python
DEBUG: bool = False
```
这样 SQL echo 日志关闭，不会在生产环境刷屏。

**`backend/app/main.py`** — CORS `allow_origins` 从 `localhost:5173` 改为实际域名：
```python
allow_origins=["https://你的域名"],
```
如果前后端同域名（Nginx 反代），浏览器视为同源，CORS 实际不需要；但保留显式白名单更安全。

#### 6.5 systemd 服务 —— 让后端在后台运行、挂了自动重启

```bash
sudo nano /etc/systemd/system/isaac-backend.service
```

```ini
[Unit]
Description=ISAAC Community Backend
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/isaac/backend
ExecStart=/opt/isaac/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

> `--host 127.0.0.1` 只监听本机——外网只能通过 Nginx 访问，不暴露端口。

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now isaac-backend
sudo systemctl status isaac-backend   # 确认 active (running)
```

#### 6.6 前端构建

```bash
cd /opt/isaac/frontend
npm install
npm run build          # 产出 dist/
```

```bash
sudo mkdir -p /var/www/isaac
sudo cp -r dist/* /var/www/isaac/
sudo chown -R www-data:www-data /var/www/isaac
```

#### 6.7 Nginx 配置

```bash
sudo nano /etc/nginx/sites-available/isaac
```

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    root /var/www/isaac;
    index index.html;

    # SPA 路由回退 —— 所有非文件请求返回 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 转发给后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件（头像等）
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态图片缓存
    location /images/ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用并重载：

```bash
sudo ln -s /etc/nginx/sites-available/isaac /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default   # 删掉默认站点
sudo nginx -t                              # 语法检查
sudo systemctl reload nginx
```

#### 6.8 防火墙

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp   # 后续配 HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

#### 6.9 HTTPS（Let's Encrypt 免费证书）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d 你的域名
```

certbot 会自动修改 Nginx 配置，加上 SSL 证书并开启 HTTP→HTTPS 重定向。

#### 6.10 生产环境检查清单

| 检查项 | 说明 |
|---|---|
| `.env` 不在版本控制中 | `backend/.env` 已在 `.gitignore` |
| `JWT_SECRET` 已更换 | 不再使用 `change-me-in-production` |
| `DEBUG=False` | 生产环境关闭 SQL echo |
| CORS 指向真实域名 | 不再 `localhost:5173` |
| MySQL 密码已设置 | 不用 root 空密码 |
| Nginx 不暴露 8000 端口 | 后端 `--host 127.0.0.1` 仅本机监听 |
| systemd enable | 服务器重启后自动拉起后端 |
| HTTPS 已启用 | certbot 配置 + 自动续期 |

#### 6.11 日常运维命令

```bash
# 后端
sudo systemctl status isaac-backend     # 查看状态
sudo systemctl restart isaac-backend    # 重启
sudo journalctl -u isaac-backend -f     # 实时日志

# Nginx
sudo nginx -t && sudo systemctl reload nginx   # 改配置后重载

# 数据库备份
mysqldump -u isaac -p isaac_community > backup_$(date +%Y%m%d).sql

# 更新部署
cd /opt/isaac && git pull
cd backend && source venv/bin/activate && alembic upgrade head
cd ../frontend && npm install && npm run build
sudo cp -r dist/* /var/www/isaac/
sudo systemctl restart isaac-backend
```

| # | 功能 | 状态 |
|---|---|---|
| 6.1 | 服务器环境准备（Nginx + MySQL + Python） | ⬜ |
| 6.2 | MySQL 建库建用户 | ⬜ |
| 6.3 | 后端部署（代码 + venv + .env + 数据迁移） | ⬜ |
| 6.4 | 代码层面生产配置修改（DEBUG + CORS） | ⬜ |
| 6.5 | systemd 守护进程 | ⬜ |
| 6.6 | 前端构建 + 部署到 Nginx | ⬜ |
| 6.7 | Nginx 配置（反向代理 + SPA 路由） | ⬜ |
| 6.8 | 防火墙开放端口 | ⬜ |
| 6.9 | HTTPS（Let's Encrypt） | ⬜ |
| 6.10 | 生产检查清单逐项确认 | ⬜ |

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


### 2026-07-14 — Bug 修复 + 道具分类重做 + 卡牌药丸数据补充

#### 1. ORM 类型修正

3 个 model 文件的 5 处 JSON 字段类型从 `dict` 改为 `list`（实际存的是数组）：
- `item.py`: `suitable_characters`, `item_pools`
- `character.py`: `starting_items`, `suitable_items`
- `ending.py`: `unlocks`

#### 2. 后端统一异常处理

`main.py` 加了 `exception_handler`，`HTTPException` 统一返回 `{code, message, data: null}`。

#### 3. 前端返回/首页链接

- 列表页（ItemsPage / CharactersPage / EndingsPage）：左上角 `返回首页` 纯文字链接 → `/`
- 详情页（ItemDetailPage / CharacterDetailPage / EndingDetailPage）：左上角 `← 返回` 纯文字按钮 → `navigate(-1)`
- CSS：`position: absolute` 浮在 `<main>` padding 区域上，不占内容空间
- `<main>` 加了 `position: relative`

#### 4. ItemsPage 实时搜索 + 翻页跳转

- 搜索框改为 `onChange` 实时搜索（300ms 防抖），删光文字自动回到完整列表
- 翻页栏加了页码输入框（`pageJump`），输入数字回车直接跳页

#### 5. 道具分类重做（五轮修正）

原始分类仅按 ID 区间映射，大量错误。改为按 effect 实际内容判断：

| 轮次 | 内容 | 变化 |
|---|---|---|
| 第一轮 | 被动中 effect 含"使用后" → 主动 | passive 320→235, active 100→185 |
| 第二轮 | 主动中 effect 不含"使用后" → 被动 | passive 235→309, active 185→111 |
| 第三轮 | 饰品中 effect 含"使用后" → 主动 | trinket 99→81, active 111→129 |
| 第四轮 | 卡牌分类：含"使用后"→主动，其余→被动 | card 100→0, passive→395, active→143 |
| 第五轮 | 药丸分类：含"使用后"→主动，其余→被动 | pill 100→0, passive→470, active→168 |

最终分类：passive 470 / active 168 / trinket 81 / card 0 / pill 0

#### 6. 卡牌 + 药丸数据抓取

- Fandom Wiki 的 `Cards and Runes` 页面（19 张 wikitable）→ 97 条卡牌
- Fandom Wiki 的 `Pills` 页面（主 wikitable）→ 50 条药丸
- 新文件：`seed_data/fetch_cards_pills.py`、`seed_data/cards_pills.json`
- 卡牌含：塔罗牌 22、逆位塔罗 22、扑克牌、符文、灵魂石等
- 药丸含：全部 50 种口袋药丸（Bad Gas、Balls of Steel 等）

#### 7. 卡牌 + 药丸中文翻译

- 灰机 wiki 的 K-page（卡牌）和 P-page（药丸）→ `displaytitle` 中文名 + 页面正文中文效果
- 新文件：`seed_data/fetch_cn_cards_pills.py`
- 覆盖：卡牌 81/97 中文名 + 66/97 中文效果；药丸 45/50 中文名 + 50/50 中文效果
- 灰机 wiki 反爬（Cloudflare），但 K/P-page 的 `action=parse` 接口可用

#### 8. HomePage 图片（2.5.1）

- 三张卡片 emoji 替换为游戏图片：妈刀（道具）、以撒（角色）、妈心（Boss）
- 图片来自 Fandom Wiki，存于 `frontend/public/images/`
- 用户反馈妈刀和以撒图片不合适，等 2.5.2/2.5.3 完成后再替换

#### 9. 道具图片下载（2.5.2 部分）

- 脚本：`seed_data/fetch_item_images.py`
- 从 Fandom Wiki 下载 604 张道具精灵图至 `frontend/public/images/items/<id>.png`
- 图片命名格式：`Collectible_<name>_icon.png`（空格保留，不要下划线）
- 数据库 `items.image_url` 已批量更新
- 前端 ItemCard + ItemDetailPage 已改为显示图片
- 约 115 张缺失（特殊字符名匹配不到 + 网络超时，需翻墙重试）
- 用户标记部分图片为非像素风（错误图片），暂未修复

#### 10. ItemCard 分类色

五个分类各不同左边框色（CSS Module）：
- passive 蓝 `#1565c0` / active 金 `#f9a825` / trinket 紫 `#7b1fa2` / card 红 `#d32f2f` / pill 青 `#00897b`

#### 当前数据总量

866 条道具（719 原 + 147 卡牌药丸新）

### 2026-07-14 — 图片系统完整重构 ✅

- **状态**：✅ 已完成
- **总结果**：866 条 item 全部 image_url 可用，详情页/列表页都显示 32×32 像素精灵图（药丸 19×19，卡牌 14×18）
- **涉及文件**：
  - `frontend/src/components/ItemCard.tsx` — 列表页（左图右标题布局）
  - `frontend/src/components/ItemCard.module.css` — 重构为 flex row + image 左布局
  - `frontend/src/pages/ItemDetailPage.tsx` — 详情页标题区用 `<img>` 显示 sprite
  - `frontend/src/pages/ItemDetailPage.module.css` — `.itemImage` 128×128
  - `backend/seed_data/fetch_item_images_fixed.py` — **新建**：用 `Collectible <Name> icon.png` 模板抓缺失道具图（150/155 成功）
  - `backend/seed_data/fetch_card_sprites.py` — **新建**：95 张卡牌每张独立 sprite
  - `backend/seed_data/update_item_images.py` — **新建**：磁盘合法 sprite → DB image_url 同步
  - `backend/seed_data/mark_pill_images.py` — **新建**（部分回退）：将药丸 image_url 标记为 polarity
  - `frontend/public/images/items/_shared/` — 11 张共享 sprite 源（2 塔罗 + 1 扑克 + Joker/Rules/Chaos/Rune/Soul_stone + 3 药丸 + 1 杂项）
- **关键发现与决策**：
  1. **之前 `fetch_item_images.py` 全失败**：用 MediaWiki `pageimages` API 抓到的全是 `Dlc_a_indicator.png` 占位图（变异颜色只有 3 个不同 URL）。改用 `Collectible <Name> icon.png` 直接拼文件名模板，命中率 90%+
  2. **路径问题**：DB 存的 `items/1.png` 对应磁盘 `public/images/items/1.png`，前端 `src` 必须是 `/images/${image_url}`（不是 `/${image_url}`），否则路径错导致 alt 文字显示
  3. **图片尺寸**：道具 sprite 是 32×32 WebP，卡牌是 14×18，药丸是 19×19，符文是 39×50 — 用 pixelated CSS 让大图不糊
  4. **卡牌 sprite 共享 fallback**：8 个符文（Fandom 无独立 sprite）+ Ace of Spades + ? Card 用 `_shared/` 文件 fallback
  5. **药丸按列分配**：用户要求按列循环，最左 `_shared/pill_black_white.png`，中间 `_shared/pill_white_white.png`，右边 `_shared/pill_white_yellow.png`，按 `(ID-733) % 3` 分配
  6. **？Card 仍未解决**：Fandom Wiki 没 `? Card` 独立 sprite，目前用 tarot_normal 临时占位
  7. **逆位塔罗中文「？」丢失**：原 fetch_cn_cards_pills_v2.py 正则 `[一-鿿?!]+` 只匹配半角 `?`，匹配不了全角 `？`（U+FF1F）。修复后用 `[一-鿿㐀-䶿?!？！]+` 重新抓 ID 805-826 22 张
- **修复流程**：
  | 步骤 | 操作 |
  |---|---|
  | 1 | 隔离 41 个 >15KB 可疑大图到 `_quarantine/`，删 56 个文件 |
  | 2 | 用户报 15 个错误图 ID，移到 `_quarantine/`，重抓真 sprite（全部 32×32） |
  | 3 | 用户报 3 个无图 ID（320/550/551），补抓 `Blue Baby's Only Friend` / `Mom's Shovel` sprite |
  | 4 | 重抓 150/155 个 1-732 范围缺失图（用 `Collectible <Name> icon.png` 模板） |
  | 5 | 抓 95 张卡牌每张独立 sprite |
  | 6 | 修改前端 ItemCard 布局（图左 + 标题右 + 描述下） |
  | 7 | 修改 src 路径 `/images/${image_url}` 修复图片加载 |
  | 8 | 修复逆位塔罗中文「？」丢失 |
  | 9 | ItemDetailPage 加图片（128×128） |
  | 10 | 删除 `_quarantine/` 目录（用户确认） |
- **验证**：
  - `curl /api/v1/items/733` 返回 `image_url: "items/_shared/pill_black_white.png"`
  - `curl /images/items/_shared/pill_black_white.png` → 200 + 138B
  - `curl /images/items/1.png` → 200
  - 数据库 866/866 有 image_url
- **注意事项**：
  - `_shared/` 子目录在 `items/` 下，DB image_url 路径必须含 `items/` 前缀
  - WebP 文件虽然是 .png 后缀，但浏览器能识别（都是 WebP lossless with alpha）
  - 卡牌 sprite 大小差异：塔罗/扑克/Joker/Rules 14×18、符文 39×50、魂石 19×22、杂项各种
  - ? Card 仍是 todo，等用户决定 fallback 方案

### 2026-07-14 — 卡牌药丸翻译补全 ✅

- **状态**：✅ 已完成
- **问题**：之前卡牌翻译覆盖率只到 81/97 名 + 66/97 效，主要缺失塔罗正位（II/III/XV）、逆位、扑克梅花、8 个符文等
- **涉及文件**：
  - `backend/seed_data/fetch_cn_cards_pills_v2.py` — 改进版爬虫（核心突破）
  - `backend/seed_data/update_cn_cards_pills.py` — 增量同步翻译到 DB
- **关键发现**：灰机 wiki 用 **K 编号组织卡牌**、**P 编号组织药丸**，与 cards_pills.json 的 ID 有确定映射关系：
  - 药丸 ID 733-782 → P0-P49（`P = ID - 733`）
  - 塔罗正位 ID 783-804 → K1-K22（`K = ID - 782`）
  - 塔罗逆位 ID 805-826 → K56-K77（`K = ID - 749`）
  - 扑克牌 ID 827-834 → K23-K30（`K = ID - 804`）
  - 魂石 ID 860-876 → K81-K97（`K = ID - 779`）
  - 特殊卡/符文用硬编码 `name_en → K 编号` 映射
- **爬虫改进**：
  - 不再用 search API（容易匹配错），直接通过 K/P 编号 `action=parse` 精确取页
  - 三层优先级提取效果：含 "使用后" > 含其他关键词 > 最长中文段
  - 过滤 wiki 元信息（"是一个 X 中加入的 Y" 这类）
  - 中文名提取保留 `???` 等特殊符号，去掉 `0-`/`I-` 等罗马数字前缀
- **覆盖率**：

| 类别 | 之前 | 现在 |
|---|---|---|
| 卡牌 中文名 | 81/97 | **97/97** ✓ |
| 卡牌 中文效果 | 66/97 | **97/97** ✓ |
| 药丸 中文名 | 45/50 | **49/50** |
| 药丸 中文效果 | 50/50 | **50/50** ✓ |

- **唯一未翻译**：药丸 ID 764 `???`（灰机 wiki P31 页面标题本身就是 `???`，没有中文）
- **验证**：`curl /api/v1/items/850` 返回 `name_cn="收获符文"` + 中文效果（不再是之前的卢恩字母释义）
- **注意事项**：
  - `update_cn_cards_pills.py` 只更新 `name_cn` 和 `effect`，不动 `description`（description 保留英文）
  - 如果以后重新跑 `seed_data.py` 全量导入，cards_pills 部分需要走 `update_cn_cards_pills.py` 单独同步（因为 seed_data.py 的 `seed_items` 只读 items.json，不读 cards_pills.json）

### 2026-07-16 — 用户数据模型 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/models/user.py` — User 模型（7 字段，对齐 database-schema.md）
  - `backend/app/models/__init__.py` — 注册 User
  - `backend/alembic/versions/8f9ff1fbea7a_add_users_table.py` — alembic autogen 迁移
- **验证**：`python -c "from app.models.user import User; from sqlalchemy import inspect; ..."` — 7 字段完整（id/username/email/password_hash/avatar/created_at/updated_at）
- **注意事项**：
  - users 表有 `updated_at`（其他表只有 `created_at`），使用 `onupdate=func.now()` 在 ORM 层自动更新
  - username + email 双 UNIQUE 约束
  - `password_hash` 存 Argon2 哈希，在 4.2 注册 API 中处理

### 2026-07-16 — 注册 API（Argon2 哈希）✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/core/security.py` — 新增 `hash_password()` 和 `verify_password()`（Argon2id）
  - `backend/app/schemas/user.py` — UserCreate（username/email/password）+ UserResponse
  - `backend/app/api/auth.py` — `POST /api/v1/auth/register`
  - `backend/app/main.py` — 注册 `auth.router`
- **验证**：
  - 正常注册 → 201 + 用户数据（不含 password_hash）
  - 重复用户名 → 409 `"用户名已被注册"`
  - 重复邮箱 → 409 `"邮箱已被注册"`
  - 密码 <6 位 → 422 Pydantic 拦截
  - 无效邮箱 → 422 Pydantic 拦截
  - 数据库验证：`verify_password("abc123", hash)` → True，错误密码 → False
  - Argon2id 参数：`m=65536,t=3,p=4`
- **注意事项**：
  - `EmailStr` 需要 `pydantic[email]` 依赖（已在 requirements.txt）
  - 注册不返回 JWT——登录在 4.3 实现
  - HTTPException 由 `main.py` 的 `exception_handler` 统一转为 `{code, message, data}` 格式

### 2026-07-16 — 登录 API（返回 JWT）✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/schemas/user.py` — 新增 `UserLogin`（login + password 字段）
  - `backend/app/api/auth.py` — 新增 `POST /api/v1/auth/login`（支持用户名或邮箱登录）
- **验证**：
  - 用户名登录 → 200 + JWT token + 用户数据
  - 邮箱登录 → 200 + JWT token + 用户数据
  - 错误密码 → 401 `"用户名或密码错误"`
  - 不存在用户 → 401 `"用户名或密码错误"`
  - JWT 解码验证 → sub=2, username=alice, exp 正确
- **注意事项**：
  - `login` 字段支持用户名或邮箱（`or_(User.username == x, User.email == x)`）
  - 不存在的用户和错误密码返回相同 401 提示，防止用户枚举攻击
  - JWT 有效期 30 分钟（`settings.JWT_EXPIRE_MINUTES`）

### 2026-07-16 — JWT 认证中间件 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/core/security.py` — 新增 `get_current_user()` 依赖注入（HTTPBearer + JWT 解析 + 数据库查用户）
  - `backend/app/api/auth.py` — 新增 `GET /api/v1/auth/me`（验证中间件可用 + 前端获取当前用户）
- **验证**：
  - 有效 token 访问 `/api/v1/auth/me` → 200 + 用户数据
  - 无 token → 401 `"请先登录"`
  - 无效 token → 401 `"无效的认证令牌"`
  - 过期 token → 401 `"无效的认证令牌"`
- **注意事项**：
  - `HTTPBearer(auto_error=False)` 避免 FastAPI 默认 403，统一返回 401
  - 后续受保护端点只需在函数签名加 `current_user: User = Depends(get_current_user)` 即可
  - `/auth/me` 同时作为中间件测试端点和前端"获取当前用户"的 API

### 2026-07-16 — 注册页面 + 登录页面 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `frontend/src/api/auth.ts` — auth API 封装（register / login / getMe）
  - `frontend/src/components/AuthModal.tsx` + `.module.css` — 登录/注册弹窗组件（tab 切换）
  - `frontend/src/App.tsx` — header 右侧 `登录 | 注册` 入口 + modal 状态管理 + 页面刷新自动恢复登录
  - `frontend/src/api/client.ts` — 401 拦截器移除 `/login` 跳转（改为仅清除 token）
- **验证**：
  - `npx tsc --noEmit` 零错误
  - 注册新用户 → 201 + 自动登录
  - 登录 → 200 + JWT 存 localStorage
  - `/auth/me` 带 token → 200
  - 退出 → 清除 token → `/auth/me` 401
  - 页面刷新 → useEffect 从 token 恢复用户状态
- **注意事项**：
  - 登录/注册使用 modal 弹窗形式，不是独立路由页面
  - 注册成功后自动调用登录接口获取 token（一站式）
  - header 的 `authChecked` 状态避免刷新时闪烁（token 校验完成前不显示按钮）
  - 后续受保护操作（发帖/收藏）通过 `get_current_user` 依赖注入验证

### 2026-07-16 — 前端 token 存储 + 登录状态持久化 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `frontend/src/hooks/useAuth.ts` — 登录状态管理 hook（user/modal/token 恢复/logout）
  - `frontend/src/App.tsx` — 重构为使用 `useAuth()` hook
- **验证**：
  - `npx tsc --noEmit` 零错误
  - `npx vite build` 构建成功（3.00s）
- **Hook 导出接口**：
  - `user` / `authChecked` — 当前用户 + 是否已检查完毕（避免刷新闪烁）
  - `modalOpen` / `modalTab` — 登录弹窗状态
  - `login(u)` — 登录成功后设置用户状态
  - `logout()` — 清除 token + 用户状态
  - `openModal(tab)` / `closeModal()` — 控制弹窗
- **注意事项**：
  - `useAuth` 可在任何组件中使用，后续社区功能页面可直接 `const { user } = useAuth()` 获取当前用户
  - 页面刷新 → `useEffect` 检测 localStorage token → 调 `GET /auth/me` 验证 → 有效则恢复，无效则清除

### 2026-07-16 — 攻略数据模型 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/models/guide.py` — Guide 模型（10 字段，4 个外键）
  - `backend/app/models/__init__.py` — 注册 Guide
  - `backend/alembic/versions/45f87b3b9dab_add_guides_table.py` — autogen 迁移
- **验证**：`inspect(engine).get_columns('guides')` → 10 字段，4 FK 全部正确
- **注意事项**：
  - `updated_at` 使用 `onupdate=func.now()`（与 User 一致）
  - 4 个外键：author_id→users, related_item_id→items, related_character_id→characters, related_ending_id→endings
  - 攻略正文存 Markdown 格式

### 2026-07-16 — 创建攻略 API + 删除攻略 API ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/schemas/guide.py` — GuideCreate + GuideResponse
  - `backend/app/api/guides.py` — `POST /api/v1/guides` + `DELETE /api/v1/guides/{id}`
  - `backend/app/main.py` — 注册 `guides.router`
- **验证**：
  - 登录用户创建 → 201 + 攻略数据
  - 无 token 创建 → 401
  - 非作者删除 → 403 `"无权删除此攻略"`
  - 作者自己删除 → 200
  - admin 删除他人攻略 → 200
  - 不存在的攻略 → 404
- **注意事项**：
  - 删除权限：`current_user.id == guide.author_id or current_user.role == "admin"`
  - category 支持 item / character / ending / general
  - related_*_id 均为可选，不填表示不关联特定资源

### 2026-07-16 — 攻略列表 API（分页 + 筛选）✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/schemas/guide.py` — GuideResponse 增加 `author_name` + GuideListData
  - `backend/app/api/guides.py` — 新增 `GET /api/v1/guides` + `_make_response()` 辅助函数
- **验证**：
  - 默认列表 → 200 + 含 author_name
  - 搜索 `azazel` → 1 条（标题/正文模糊匹配）
  - 分类筛选 `category=character` → 1 条
  - 分页 `page_size=2` → page1=2, page2=2
- **注意事项**：
  - 列表按 `created_at DESC` 排序（最新在前）
  - 作者名通过 `IN (author_ids)` 批量查询，避免 N+1 问题
  - 搜索同时匹配标题和正文

### 2026-07-16 — 收藏/取消收藏 API ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/models/favorite.py` — Favorite 模型（UNIQUE(user_id, guide_id)）
  - `backend/app/schemas/favorite.py` — FavoriteResponse + FavoriteListData
  - `backend/app/api/favorites.py` — `GET/POST /api/v1/favorites` + `DELETE /api/v1/favorites/{guide_id}`
  - `backend/app/main.py` — 注册 `favorites.router`
  - `backend/alembic/versions/8ec1094b8f41_add_favorites_table.py` — autogen 迁移
- **验证**：
  - 收藏 → 201；重复收藏 → 409；取消 → 200；再次取消 → 404
  - 我的收藏列表 → 仅返回当前用户的收藏，用户间隔离
  - 无 token → 401
- **注意事项**：
  - 收藏列表只返回 Favorite 记录（含 guide_id），前端需额外查攻略详情
  - UNIQUE 约束 `uq_user_guide_favorite` 防止重复收藏

### 2026-07-16 — 攻略列表页 + 详情页 + 创建页 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `frontend/src/types/guide.ts` — Guide 接口类型
  - `frontend/src/api/guides.ts` — getGuides / getGuideById / createGuide / deleteGuide
  - `frontend/src/components/GuideCard.tsx` + `.module.css` — 攻略卡片（分类标签+日期+作者）
  - `frontend/src/pages/GuidesPage.tsx` + `.module.css` — 列表页（分页+搜索+分类筛选+"发布攻略"按钮）
  - `frontend/src/pages/GuideDetailPage.tsx` + `.module.css` — 详情页（正文+作者名+删除按钮）
  - `frontend/src/pages/CreateGuidePage.tsx` + `.module.css` — 创建页（表单+分类单选）
  - `frontend/src/App.tsx` — 注册 3 条路由
  - `backend/app/api/guides.py` — 新增 `GET /api/v1/guides/{id}` 详情端点
- **验证**：
  - `npx tsc --noEmit` 零错误
  - `npx vite build` 2.81s 构建成功
  - `GET /api/v1/guides/6` → 200 + author_name
  - `GET /api/v1/guides/99999` → 404
- **注意事项**：
  - 详情页删除按钮仅在当前用户是作者或 admin 时显示（`canDelete` 判断）
  - CreateGuidePage 使用 radio button 选择分类（general/item/character/ending）
  - 首页社区卡片 + 导航栏"社区"链接已在之前完成，现在都指向 `/guides`
  - 前端路由：`/guides`（列表）→ `/guides/new`（创建）→ `/guides/:id`（详情）

### 2026-07-16 — 我的收藏页面 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/schemas/favorite.py` — FavoriteResponse 增加 `guide_title` + `guide_author`
  - `backend/app/api/favorites.py` — 列表端点加入 guides + users 表关联查询
  - `frontend/src/types/favorite.ts` — Favorite 接口类型
  - `frontend/src/api/favorites.ts` — getMyFavorites / addFavorite / removeFavorite
  - `frontend/src/pages/MyFavoritesPage.tsx` + `.module.css` — 收藏列表 + 取消收藏按钮
  - `frontend/src/App.tsx` — 注册 `/favorites` 路由 + header 已登录用户旁"我的收藏"链接
- **验证**：
  - `npx tsc --noEmit` 零错误
  - `npx vite build` 3.76s 构建成功
  - `GET /api/v1/favorites` → 200 + guide_title + guide_author
- **注意事项**：
  - 收藏列表后端用 3 次批量查询（favorites → guides → users），避免 N+1
  - 导航栏"我的收藏"仅在已登录时显示
  - 取消收藏即时从列表移除（乐观更新）

### 2026-07-16 — 点赞数据模型 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/models/like.py` — Like 模型（UNIQUE(user_id, guide_id)）
  - `backend/app/models/__init__.py` — 注册 Like
  - `backend/alembic/versions/c9a570ba2d76_add_likes_table.py` — autogen 迁移
- **验证**：4 字段 + 2 FK（user_id→users, guide_id→guides）+ UNIQUE 约束
- **注意事项**：
  - 迁移链路：`8ec1094b8f41 → c9a570ba2d76`
  - 结构与 favorites 表一致，可复用相同模式实现 API

### 2026-07-16 — 点赞/取消点赞 API ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/schemas/like.py` — LikeResponse
  - `backend/app/api/likes.py` — `POST /api/v1/likes` + `DELETE /api/v1/likes/{guide_id}`
  - `backend/app/main.py` — 注册 `likes.router`
- **验证**：
  - 点赞 → 201 + like_count；取消 → 200 + like_count
  - 重复点赞 → 409；重复取消 → 404
  - 无 token → 401
  - 两人点赞同一攻略 count=2，各自取消互不影响
- **注意事项**：
  - 端点返回 `like_count` 方便前端直接显示点赞数
  - 与 favorites API 结构一致，只是表名和字段名不同

### 2026-07-16 — 评论数据模型 ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/models/comment.py` — Comment 模型（5 字段，2 FK）
  - `backend/alembic/versions/95066bf0ae3d_add_comments_table.py` — autogen 迁移
- **验证**：5 字段 + 2 FK（guide_id→guides, user_id→users）
- **注意事项**：
  - 迁移链路：`c9a570ba2d76 → 95066bf0ae3d`
  - 无 UNIQUE 约束（同一用户可多次评论同一攻略）

### 2026-07-16 — 发表/删除评论 API ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/schemas/comment.py` — CommentCreate + CommentResponse（含 author_name）
  - `backend/app/api/comments.py` — `GET/POST /api/v1/guides/{id}/comments` + `DELETE /api/v1/comments/{id}`
  - `backend/app/main.py` — 注册 `comments.router`
- **验证**：
  - 发表评论 → 201 + author_name
  - 评论列表（公开）→ 200 + 含作者名
  - 非作者删除 → 403；admin 删除 → 200
  - 无 token → 401
- **注意事项**：
  - 评论列表无需登录（公开可看）
  - 删除权限：作者本人或 admin
  - comments 路由无统一 prefix（两个端点前缀不同：/guides/{id}/comments 和 /comments/{id}）

### 2026-07-16 — 头像上传 API ✅

- **状态**：✅ 已完成
- **涉及文件**：
  - `backend/app/api/auth.py` — 新增 `POST /api/v1/auth/avatar`
  - `backend/app/main.py` — 挂载 `/uploads` 静态文件目录
- **验证**：
  - 上传 PNG → 200 + `{"avatar": "avatars/2_xxx.png"}`
  - `/uploads/avatars/2_xxx.png` → HTTP 200 可访问
  - `/me` 响应含 `avatar` 字段
- **注意事项**：
  - 仅允许 PNG/JPEG/GIF/WebP，文件大小限制 2MB
  - 文件名格式：`{user_id}_{uuid8}.{ext}`

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

### 已完成

| 模块 | 完成项 |
|---|---|
| 项目初始化 (0.x) | 脚手架、数据库、Git |
| 道具系统 (1.x) | 模型、种子(866)、API、前端页面（列表+详情） |
| 角色系统 (2.x) | 模型、种子(34)、API、前端页面（列表+详情） |
| 结局系统 (3.x) | 模型、种子(22)、API、前端页面（列表+详情） |
| 道具分类重做 | passive 470 / active 168 / trinket 81 / card 97 / pill 50 = 866 条 |
| 卡牌药丸数据 | 从 Wiki 抓取 147 条 + 中文名/效果（97/97 卡牌名+效果、49/50 药丸名、50/50 药丸效果） |
| 前端优化 | 实时搜索、翻页跳转、返回按钮、道具分色边框 |
| 图片系统重构 | 866/866 item 都有 image_url；列表页图左标题右布局；详情页 128×128 sprite |
| 用户系统 (4.x) | 注册/登录 API（Argon2 + JWT）+ 认证中间件 + 前端登录弹窗 + token 持久化 |
| 社区功能 (5.x) | 攻略 CRUD + 收藏/点赞/评论 API + 列表/详情/创建页 + 我的收藏页 + 头像上传 |

### 待做

| 顺序 | 模块 |
|---|---|
| 2.5.1 | 首页配图（妈刀和以撒图片不合适，待换） |
| 2.5.2-a | ? Card (ID 844) 缺独立 sprite，目前 fallback 到 tarot_normal——待选方案 |
| 2.5.3 | 角色配图（⬜ 未开始） |
| 2.5.4 | 结局配图（⬜ 未开始） |
| 6.1~6.10 | 部署（详见阶段五详细步骤） |

---

## 图片占位符约定

项目中所有图片占位符使用 HTML `data-*` 属性标记，方便后续识图模型根据 ID/标识 查找对应图片进行替换。

### 通用占位符格式

无图片时：
```html
<span class="xxxPlaceholder" data-item-id="道具ID" />
<!-- 或 -->
<div class="xxxPlaceholder" data-item-id="道具ID" />
```

有图片时：
```html
<img src="/images/items/道具ID.png" data-item-id="道具ID" />
```

### 各模块占位符详细约定

#### 道具（Items）

| 位置 | 属性 | 尺寸 | 说明 |
|---|---|---|---|
| 列表卡片 (ItemCard) | `data-item-id` 标注道具 ID | 64×64 | 左图右文字布局 |
| 详情页标题区 | `data-item-id` 标注道具 ID | 128×128 | 标题行左侧 |
| 道具池 | `data-stat` 不适用，用 `<img src="/images/pool/pool_key.png">` | 20×20 | 路径格式 `/images/pool/treasure_room.png` 等 |
| 属性变化表 | 用 `<img src="/images/stat/stat_key.png">` | 20×20 | 路径格式 `/images/stat/damage.png`、`/images/stat/tears.png` 等 |

道具池 pool_key 列表：`treasure_room`, `devil_room`, `angel_room`, `secret_room`, `ultra_secret_room`, `shop`, `boss`, `library`, `planetarium`, `curse_room`, `golden_chest`, `red_chest`, `old_chest`, `moms_chest`, `beggar`, `devil_beggar`, `bomb_bum`, `battery_bum`, `rotten_beggar`, `shell_game`, `crane_game`, `key_master`, `baby_shop`, `wooden_chest`, `challenge_room`, `boss_challenge_room`, `dice_room`, `bedroom`, `card_drop`（卡牌）, `pill_pool`（胶囊）, `trinket_drop`（饰品）, `transformation`（套装）

属性 stat_key 列表：`damage`（伤害/攻击）, `tears`（射速）, `speed`（移速）, `range`（射程）, `shot_speed`（弹速）, `luck`（幸运）, `health`（生命/心之容器）, `soul_heart`（魂心）, `black_heart`（黑心）, `eternal_heart`（永恒之心）, `bomb`（炸弹）, `coin`（硬币）, `key`（钥匙）

#### 套装效果（Transformations）

| 位置 | 属性 | 尺寸 | 说明 |
|---|---|---|---|
| 列表卡片 | `data-item-id` 标注第一个所需道具 ID | 64×64 | 后端 `first_item_id` 字段 |
| 详情页所需道具 | `data-item-id` 标注每个道具的实际 ID | 24×24 | 后端 `required_items_enriched[].id` |
| 卡片分类标签 | 无占位符，CSS 粉色椭圆标签 `#c2185b` | — | 文字"套装" |

#### 角色（Characters）

| 位置 | 属性 | 尺寸 | 说明 |
|---|---|---|---|
| 列表卡片立绘 | `data-item-id` 标注角色 ID | 64×64 | 左图右文字布局 |
| 列表卡片生命值 | `data-heart="health"` | 16×16 | 中文名右侧，后跟原始生命文本（如 `3❤ 1🖤`） |
| 列表卡片攻击力 | `data-stat="damage"` | 16×16 | 英文名右侧，后跟数值 |
| 详情页生命值 | `data-heart="heart_type"` | 20×20 | 每种心类型独立占位符 |
| 详情页初始属性表 | `<img src="/images/stat/damage.png">` 等 | 20×20 | 表头"属性 / 数值"，与道具属性变化表一致 |
| 详情页初始道具 | `data-item-id` 标注道具 ID | 24×24 | 后端 `starting_items_enriched[].id` |

心类型 `data-heart` 值：`red`（❤红心）, `soul`（💙魂心）, `black`（🖤黑心）, `gold`（💛金心）, `eternal`（🤍永恒之心）, `bone`（🦴骨心）, `rotten`（💚腐心）

#### 结局（Endings）

| 位置 | 属性 | 尺寸 | 说明 |
|---|---|---|---|
| 列表卡片 | `data-boss` 标注 Boss 中文名 | 64×64 | "结局 N"文字右侧 |
| 详情页标题 | `data-boss` 标注 Boss 中文名 | 80×80 | 标题行右侧 |
| 详情页完成后解锁 | `data-item-id` 标注道具/角色 ID | 24×24 | 后端 `unlocks_enriched[].item_id` / `character_id` |

#### 生命类型（HeartTypes，角色页）

| 位置 | 属性 | 尺寸 | 说明 |
|---|---|---|---|
| 生命类型卡片 | `data-heart="type_key"` | 22×22 | type_key: `red`, `soul`, `black`, `eternal`, `gold`, `bone`, `rotten` |

### 数据来源

- **道具名/效果/解锁**：灰机 wiki（`isaac.huijiwiki.com`），C 页（道具）、K 页（卡牌）、P 页（药丸）、T 页（饰品）
- **道具池**：Fandom wiki（`bindingofisaacrebirth.fandom.com`）infobox `data-source="alias"` 字段
- **角色/结局**：灰机 wiki 页面 parse
- **套装效果**：json 手工整理 + 后端查 items/characters 表自动匹配中文名和图片 URL
- **属性变化**：正则从中文 effect 文本提取数值
- **LaTeX 公式**：字符串替换去 `\dfrac`/`\lfloor`/`\times` 等，保留可读部分

### 后端 enrich 模式

以下 API 在详情端点自动从 items/characters 表查询中文名和图片 URL：

- `GET /api/v1/characters/{id}` → `starting_items_enriched`（每个 item 的 id/name_cn/image_url）
- `GET /api/v1/transformations/{id}` → `required_items_enriched`（每个 item 的 id/name_cn/image_url）；列表端点 → `first_item_id`
- `GET /api/v1/endings/{id}` → `unlocks_enriched`（每个 unlock 的 item_id/character_id/image_url）

### 不可自行翻译的原则

所有中文文本必须从灰机 wiki 获取，**绝对禁止**自行翻译或机翻。英文名保留用于数据库匹配，前端优先显示中文名。

---

## 环境信息

- 项目路径：`d:\暑假task\ISAAC`
- 后端端口：`8000` / 前端端口：`5173`
- MySQL 数据库名：`isaac_community`
