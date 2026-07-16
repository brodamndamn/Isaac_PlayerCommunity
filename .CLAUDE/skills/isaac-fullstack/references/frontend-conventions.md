# 前端组件规范

## 目录结构

```
frontend/src/
├── api/                    # API 请求封装
│   ├── client.ts           # axios 实例（baseURL、拦截器、JWT 自动附加）
│   ├── items.ts            # 道具相关 API 函数
│   ├── characters.ts       # 角色相关 API 函数
│   ├── endings.ts          # 结局相关 API 函数
│   ├── auth.ts             # 登录注册 API 函数
│   ├── guides.ts           # 攻略 CRUD API 函数
│   ├── likes.ts              # 点赞 API 函数
│   ├── comments.ts           # 评论 API 函数
│   └── favorites.ts        # 收藏 API 函数
├── components/             # 可复用展示组件
│   ├── Layout/             # 布局组件（Header、Footer、Sidebar）
│   ├── ItemCard.tsx        # 道具卡片（列表展示用）
│   ├── CharacterCard.tsx   # 角色卡片
│   ├── GuideCard.tsx       # 攻略卡片
│   ├── CommentList.tsx     # 评论列表 + 发表评论
│   ├── AvatarUpload.tsx    # 头像上传组件
│   └── ui/                 # 通用 UI 组件（Button、Modal、Pagination 等）
├── pages/                  # 页面级组件
│   ├── HomePage.tsx        # 首页
│   ├── ItemsPage.tsx       # 道具列表页
│   ├── ItemDetailPage.tsx  # 道具详情页
│   ├── CharactersPage.tsx  # 角色列表页
│   ├── CharacterDetailPage.tsx
│   ├── EndingsPage.tsx     # 结局列表页
│   ├── EndingDetailPage.tsx
│   ├── LoginPage.tsx       # 登录页
│   ├── RegisterPage.tsx    # 注册页
│   ├── CreateGuidePage.tsx # 创建攻略页
│   ├── GuideDetailPage.tsx # 攻略详情页
│   └── MyFavoritesPage.tsx # 我的收藏页
├── types/                  # TypeScript 类型定义
│   ├── item.ts             # Item 接口
│   ├── character.ts        # Character 接口
│   ├── ending.ts           # Ending 接口
│   ├── user.ts             # User 接口
│   ├── guide.ts            # Guide 接口
│   └── api.ts              # API 响应通用类型（ApiResponse<T> 等）
├── hooks/                  # 自定义 Hooks
│   ├── useAuth.ts          # 登录状态管理
│   └── usePagination.ts   # 分页逻辑
├── App.tsx                 # 根组件 + React Router 路由配置
└── main.tsx                # 入口文件
```

## 命名规范

- **组件文件名**：PascalCase，如 `ItemCard.tsx`、`LoginPage.tsx`
- **页面组件**：以 `Page` 结尾，如 `ItemsPage.tsx`
- **API 文件**：小写，与后端模块名对应，如 `items.ts`
- **类型文件**：小写，如 `item.ts`
- **Hooks**：`use` 开头，如 `useAuth.ts`
- **CSS 文件**：与组件同名，如 `ItemCard.module.css`（使用 CSS Modules）

## 组件设计原则

### 展示组件（`components/`）

- 不包含业务逻辑，只负责渲染
- 通过 `props` 接收数据
- 通过回调函数向父组件报告事件
- 可以跨页面复用

示例 — ItemCard：
```tsx
interface ItemCardProps {
  item: Item;
  onFavorite?: (itemId: number) => void;
}
```

### 页面组件（`pages/`）

- 负责数据获取、状态管理
- 组装多个展示组件
- 对应一个路由路径
- 不直接在其他页面中被引用

## API 请求封装

`client.ts` — axios 实例：
```typescript
import axios from "axios";

const client = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});

// 请求拦截器：自动附加 JWT
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：统一错误处理
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default client;
```

`items.ts` — 模块化 API 函数示例：
```typescript
import client from "./client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Item } from "../types/item";

export async function getItems(params: {
  page?: number;
  page_size?: number;
  category?: string;
  search?: string;
}): Promise<ApiResponse<PaginatedData<Item>>> {
  const { data } = await client.get("/items", { params });
  return data;
}

export async function getItemById(id: number): Promise<ApiResponse<Item>> {
  const { data } = await client.get(`/items/${id}`);
  return data;
}
```

## 路由设计

使用 React Router v6，路由表：

| 路径 | 页面组件 | 说明 |
|---|---|---|
| `/` | HomePage | 首页 |
| `/items` | ItemsPage | 道具列表 |
| `/items/:id` | ItemDetailPage | 道具详情 |
| `/characters` | CharactersPage | 角色列表 |
| `/characters/:id` | CharacterDetailPage | 角色详情 |
| `/endings` | EndingsPage | 结局列表 |
| `/endings/:id` | EndingDetailPage | 结局详情 |
| `/login` | LoginPage | 登录 |
| `/register` | RegisterPage | 注册 |
| `/guides/new` | CreateGuidePage | 创建攻略（需登录） |
| `/guides/:id` | GuideDetailPage | 攻略详情 |
| `/favorites` | MyFavoritesPage | 我的收藏（需登录） |

## 样式方案

使用 **CSS Modules**（Vite 原生支持），避免样式冲突：
- 文件命名：`ComponentName.module.css`
- 类名使用 camelCase
- 全局样式放在 `src/index.css`

如果要引入组件库（如 Ant Design 或 MUI），需先确认。默认手写组件，保持轻量。
