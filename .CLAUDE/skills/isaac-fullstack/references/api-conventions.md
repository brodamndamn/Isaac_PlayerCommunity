# API 端点约定

## 路由前缀

所有 API 端点统一使用 `/api/v1/` 前缀。

## RESTful 命名规则

| 资源 | 路由 | HTTP 方法 |
|---|---|---|
| 道具列表 | `/api/v1/items` | GET |
| 道具详情 | `/api/v1/items/{id}` | GET |
| 角色列表 | `/api/v1/characters` | GET |
| 角色详情 | `/api/v1/characters/{id}` | GET |
| 结局列表 | `/api/v1/endings` | GET |
| 结局详情 | `/api/v1/endings/{id}` | GET |
| 注册 | `/api/v1/auth/register` | POST |
| 登录 | `/api/v1/auth/login` | POST |
| 攻略列表 | `/api/v1/guides` | GET |
| 攻略详情 | `/api/v1/guides/{id}` | GET |
| 创建攻略 | `/api/v1/guides` | POST（需登录） |
| 删除攻略 | `/api/v1/guides/{id}` | DELETE（仅作者） |
| 收藏攻略 | `/api/v1/favorites` | POST（需登录） |
| 取消收藏 | `/api/v1/favorites/{guide_id}` | DELETE（需登录） |
| 我的收藏 | `/api/v1/favorites` | GET（需登录） |

命名要点：
- 资源名用复数名词
- 动作用 HTTP 方法表达，不写在 URL 里（如 `POST /items` 而不是 `/items/create`）
- 子资源用嵌套路由（如 `/guides/{id}/comments`）

---

## 统一响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "ok",
  "data": { ... }
}
```

- `data` 可能是对象、数组或 `null`
- 列表响应额外包含分页信息：

```json
{
  "code": 200,
  "message": "ok",
  "data": {
    "items": [...],
    "total": 700,
    "page": 1,
    "page_size": 20
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "具体错误描述",
  "data": null
}
```

HTTP 状态码与响应体 `code` 保持一致。

### 常用状态码

| 状态码 | 场景 |
|---|---|
| 200 | 请求成功 |
| 201 | 创建成功（如注册、发帖） |
| 400 | 请求参数错误 |
| 401 | 未登录或 token 过期 |
| 403 | 无权限（如删除别人的攻略） |
| 404 | 资源不存在 |
| 409 | 冲突（如重复收藏、用户名已存在） |
| 422 | 请求体验证失败（Pydantic 校验不通过） |
| 500 | 服务器内部错误 |

---

## 分页约定

列表接口通用查询参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `page` | int | 1 | 页码（1-based） |
| `page_size` | int | 20 | 每页条数（最大 100） |
| `search` | str | — | 模糊搜索关键词 |
| `category` | str | — | 按分类筛选 |

---

## JWT 认证

**Token 格式**：Bearer Token

**请求头**：
```
Authorization: Bearer <access_token>
```

**Token 内容**（Payload）：
```json
{
  "sub": "<user_id>",
  "username": "<username>",
  "exp": "<expiration_timestamp>"
}
```

**过期时间**：
- access_token：30 分钟
- refresh_token：7 天（可选实现）

**FastAPI 依赖注入**：
```python
from app.core.security import get_current_user

@router.post("/guides")
def create_guide(..., current_user = Depends(get_current_user)):
    ...
```

---

## 后端路由文件组织

```
backend/app/api/
├── __init__.py
├── items.py          # /api/v1/items/*
├── characters.py     # /api/v1/characters/*
├── endings.py        # /api/v1/endings/*
├── auth.py           # /api/v1/auth/*
├── guides.py         # /api/v1/guides/*
└── favorites.py      # /api/v1/favorites/*
```

每个文件内使用 FastAPI 的 `APIRouter(prefix="/api/v1/xxx", tags=["xxx"])` 定义子路由，然后在 `main.py` 中 `app.include_router()` 汇总。
