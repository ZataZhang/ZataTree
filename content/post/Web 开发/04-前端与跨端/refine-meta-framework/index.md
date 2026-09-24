---
title: "Refine: 当 API 即界面，CRUD 不再是体力活"
description: "一个 React 元框架，让你的后台界面由 API 结构自动决定"
date: 2025-06-05T10:00:00+08:00
image: images/index/index.png
categories:
    - Web 开发
tags:
    - 前端与跨端
    - React
    - Meta-Framework
    - CRUD
    - Headless
---

## 问题：后台管理界面，为什么总是重复劳动？

你有没有发现，每次写后台管理界面，都在做同样的事情：

**项目列表页**：表格 + 分页 + 搜索 + 排序 + 新建按钮 + 编辑按钮 + 删除按钮

**项目详情页**：表单 + 字段校验 + 提交按钮 + 错误提示

**用户管理页**：表格 + 分页 + 搜索 + 排序 + 新建按钮 + ...

这些页面长得几乎一样，但你还是要：

1. 写表格组件
2. 写分页逻辑
3. 写搜索过滤
4. 写表单校验
5. 写 API 调用
6. 写错误处理
7. 写乐观更新
8. 写权限控制

**一个 CRUD 页面，至少 200 行代码**。10 个资源就是 2000 行。

而且这些代码有个特点：**业务逻辑和 UI 混在一起**。

```tsx
// 典型的后台页面代码
const ProjectList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  
  useEffect(() => {
    setLoading(true);
    fetch(`/api/projects?page=${page}&search=${search}`)
      .then(res => res.json())
      .then(data => {
        setProjects(data.items);
        setLoading(false);
      })
      .catch(err => {
        toast.error("加载失败");
        setLoading(false);
      });
  }, [page, search]);
  
  // ... 还有 100 行
};
```

这段代码的问题：

- **数据获取逻辑**（fetch、loading、error）和 **UI 逻辑**（表格、分页）混在一起
- 换一个资源（tasks、users），这段代码几乎要重写一遍
- 后端 API 改了，前端要改 N 个地方

**这就是 Refine 要解决的问题**。

---

## Refine 是什么？

Refine 不是 UI 库，不是组件库，而是一个 **元框架（meta-framework）**。

它的核心思想：

> **你的后端 API 长什么样，前端 CRUD 就长什么样。**

用一张图说明：

```
┌─────────────────────────────────────────────────────────────┐
│                     后端 API 结构                            │
│  GET /api/projects    → 列表页（表格 + 分页 + 搜索）         │
│  GET /api/projects/:id → 详情页（表单展示）                  │
│  POST /api/projects   → 新建页（表单 + 校验）                │
│  PUT /api/projects/:id → 编辑页（表单 + 校验）               │
│  DELETE /api/projects/:id → 删除功能                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
                   Refine 自动映射
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     前端页面结构                             │
│  /projects        → ProjectList 组件                        │
│  /projects/:id    → ProjectShow 组件                        │
│  /projects/create → ProjectCreate 组件                      │
│  /projects/edit/:id → ProjectEdit 组件                      │
└─────────────────────────────────────────────────────────────┘
```

**你只需要告诉 Refine：**

1. 你的 API 在哪里（Data Provider）
2. 你有哪些资源（Resource）
3. 用什么 UI（shadcn/ui、Material UI、Ant Design...）

**Refine 会帮你生成：**

- 数据获取逻辑
- 路由配置
- 侧边栏菜单
- 权限控制
- 表单校验
- 错误处理

---

## 核心概念 1：Headless（无头）

这是 Refine 最关键的设计决策：**业务逻辑和 UI 完全分离**。

### Refine 提供什么？

```tsx
// Refine 提供的核心能力
import { 
  useList,      // 列表数据获取
  useOne,       // 单条数据获取
  useCreate,    // 新建
  useUpdate,    // 更新
  useDelete,    // 删除
  useForm,      // 表单状态管理
  useNavigation,// 路由跳转
  useCan,       // 权限判断
} from "@refinedev/core";
```

这些 hooks **不依赖任何 UI 库**。它们只负责：

- 发 API 请求
- 管理请求状态（loading、error、data）
- 缓存数据
- 乐观更新

### 你用什么 UI？

**完全自由**。Refine 官方提供了集成：

- `@refinedev/mui` — Material UI
- `@refinedev/antd` — Ant Design
- `@refinedev/mantine` — Mantine
- `@refinedev/chakra` — Chakra UI

或者用你自己的组件：

```tsx
// 用 shadcn/ui 的 Table
import { Table } from "@/components/ui/table";
import { useList } from "@refinedev/core";

const ProjectList = () => {
  const { data, isLoading } = useList({
    resource: "projects",
  });
  
  return (
    <Table>
      {data?.data.map(project => (
        <TableRow key={project.id}>
          <TableCell>{project.name}</TableCell>
        </TableRow>
      ))}
    </Table>
  );
};
```

**对比 Ant Design Pro**：

| 维度 | Ant Design Pro | Refine |
|------|----------------|--------|
| UI 库 | 强绑定 Ant Design | 任意 UI 库 |
| 业务逻辑 | 和 UI 耦合 | 完全分离 |
| 自定义 | 要覆盖 Pro 组件 | 直接用自己的组件 |
| 学习成本 | 要学 Pro 组件体系 | 只学 Refine hooks |

---

## 核心概念 2：Resource（资源）

Refine 把一切后台对象抽象成 **Resource**。

### 资源的定义

```tsx
<Refine
  resources={[
    {
      name: "projects",           // API 路径
      list: "/projects",          // 列表页路由
      create: "/projects/create", // 新建页路由
      edit: "/projects/edit/:id", // 编辑页路由
      show: "/projects/:id",      // 详情页路由
      meta: {
        label: "项目",            // 侧边栏显示名称
        icon: <ProjectIcon />,    // 侧边栏图标
      }
    },
    {
      name: "tasks",
      list: "/tasks",
      create: "/tasks/create",
      edit: "/tasks/edit/:id",
    },
    {
      name: "users",
      list: "/team",  // 路由可以自定义
    },
  ]}
/>
```

### 这段配置做了什么？

**1. 自动生成侧边栏菜单**

```
┌──────────────┐
│ 📁 项目      │
│ ✅ 任务      │
│ 👥 团队      │
└──────────────┘
```

**2. 自动生成路由表**

```
/projects        → 项目列表
/projects/create → 新建项目
/projects/edit/123 → 编辑项目 123
/projects/123    → 项目详情
/tasks           → 任务列表
...
```

**3. 自动关联 Data Provider**

当你调用 `useList({ resource: "projects" })`，Refine 知道要去 `/api/projects` 取数据。

**对比传统方式**：

```tsx
// 传统方式：每个页面单独写
<Route path="/projects" element={<ProjectList />} />
<Route path="/projects/create" element={<ProjectCreate />} />
<Route path="/projects/edit/:id" element={<ProjectEdit />} />
<Route path="/tasks" element={<TaskList />} />
<Route path="/tasks/create" element={<TaskCreate />} />
// ... 重复 N 次
```

用 Refine，**配置一次，路由、菜单、数据源全部搞定**。

---

## 核心概念 3：Data Provider（数据提供者）

这是 Refine 最有价值的设计。

### Data Provider 的接口

```tsx
const dataProvider = {
  // 获取列表（带分页、过滤、排序）
  getList: async ({ resource, pagination, filters, sorters }) => {
    const { current, pageSize } = pagination;
    const response = await fetch(
      `/api/${resource}?` +
      `_start=${(current - 1) * pageSize}&` +
      `_end=${current * pageSize}&` +
      filters.map(f => `${f.field}=${f.value}`).join('&')
    );
    const data = await response.json();
    const total = parseInt(response.headers.get('x-total-count'));
    
    return { data, total };
  },
  
  // 获取单条
  getOne: async ({ resource, id }) => {
    const response = await fetch(`/api/${resource}/${id}`);
    const data = await response.json();
    return { data };
  },
  
  // 新建
  create: async ({ resource, variables }) => {
    const response = await fetch(`/api/${resource}`, {
      method: 'POST',
      body: JSON.stringify(variables),
    });
    const data = await response.json();
    return { data };
  },
  
  // 更新
  update: async ({ resource, id, variables }) => {
    const response = await fetch(`/api/${resource}/${id}`, {
      method: 'PUT',
      body: JSON.stringify(variables),
    });
    const data = await response.json();
    return { data };
  },
  
  // 删除
  deleteOne: async ({ resource, id }) => {
    await fetch(`/api/${resource}/${id}`, { method: 'DELETE' });
    return { data: { id } };
  },
};
```

### 这个接口的意义

**一次实现，所有页面复用**。

```tsx
// 项目列表页
const ProjectList = () => {
  const { data } = useList({ resource: "projects" });
  // 自动调用 dataProvider.getList({ resource: "projects" })
};

// 任务列表页
const TaskList = () => {
  const { data } = useList({ resource: "tasks" });
  // 自动调用 dataProvider.getList({ resource: "tasks" })
};

// 项目编辑页
const ProjectEdit = () => {
  const { data } = useOne({ resource: "projects", id: 123 });
  // 自动调用 dataProvider.getOne({ resource: "projects", id: 123 })
};
```

**你不用在每个页面写 fetch**。Refine 帮你：

- 拼接 URL
- 处理分页参数
- 处理过滤参数
- 处理排序参数
- 缓存响应
- 处理错误

### 内置的 Data Provider

Refine 提供了 15+ 开箱即用的 Data Provider：

| Provider | 用途 |
|----------|------|
| `@refinedev/simple-rest` | 标准 REST API |
| `@refinedev/graphql` | GraphQL API |
| `@refinedev/strapi` | Strapi CMS |
| `@refinedev/supabase` | Supabase |
| `@refinedev/hasura` | Hasura GraphQL |
| `@refinedev/nestjs-crud` | NestJS CRUD |
| `@refinedev/airtable` | Airtable |
| `@refinedev/firebase` | Firebase |

**如果你的后端是 FastAPI**，写一个自定义 Data Provider 即可：

```tsx
// customDataProvider.ts
import dataProvider from "@refinedev/simple-rest";

export const customDataProvider = {
  ...dataProvider("https://your-fastapi.com/api"),
  
  // 自定义 getList，适配你的 FastAPI 分页格式
  getList: async ({ resource, pagination, filters, sorters }) => {
    const response = await fetch(
      `/api/${resource}?` +
      `page=${pagination.current}&` +
      `size=${pagination.pageSize}`
    );
    const { items, total } = await response.json();
    return { data: items, total };
  },
};
```

---

## 核心概念 4：Auth Provider（认证提供者）

认证逻辑也抽象成 Provider：

```tsx
const authProvider = {
  // 登录
  login: async ({ email, password }) => {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    
    if (response.ok) {
      const { token } = await response.json();
      localStorage.setItem("token", token);
      return { success: true };
    }
    
    return { success: false, error: { message: "登录失败" } };
  },
  
  // 登出
  logout: async () => {
    localStorage.removeItem("token");
    return { success: true };
  },
  
  // 检查登录状态
  check: async () => {
    const token = localStorage.getItem("token");
    return token 
      ? { authenticated: true }
      : { authenticated: false, redirectTo: "/login" };
  },
  
  // 获取当前用户
  getIdentity: async () => {
    const response = await fetch("/api/auth/me");
    const user = await response.json();
    return user;
  },
  
  // 权限检查
  can: async ({ action, resource }) => {
    const user = await authProvider.getIdentity();
    return user.role === "admin" || user.permissions.includes(`${action}:${resource}`);
  },
};
```

### 使用方式

```tsx
// 包裹整个应用
<Refine
  authProvider={authProvider}
  // ...
>
  <App />
</Refine>

// 在组件中使用
import { useCan } from "@refinedev/core";

const DeleteButton = ({ projectId }) => {
  const { data: canDelete } = useCan({
    action: "delete",
    resource: "projects",
    params: { id: projectId },
  });
  
  return canDelete ? <Button>删除</Button> : null;
};
```

**Refine 会自动处理**：

- 未登录跳转到 `/login`
- 登录后跳回原页面
- 侧边栏根据权限显示/隐藏菜单项
- 按钮根据权限显示/隐藏

---

## 核心概念 5：Inferencer（自动生成 CRUD 页面）

这是最惊艳的功能。

### 使用方式

```bash
# 安装 Inferencer
npm install @refinedev/inferencer

# 运行
npx @refinedev/cli@latest inferencer
```

### Inferencer 做了什么？

1. **读取你的 API Schema**（通过 Data Provider）
2. **分析字段类型**：
   - `string` → 文本输入框
   - `number` → 数字输入框
   - `boolean` → 开关
   - `date` → 日期选择器
   - `enum` → 下拉选择
   - `relation` → 关联选择器
3. **生成完整的 CRUD 页面代码**

### 生成的代码示例

```tsx
// Inferencer 生成的列表页（简化版）
import { List, useTable } from "@refinedev/antd";
import { Table } from "antd";

export const ProjectList = () => {
  const { tableProps } = useTable({
    resource: "projects",
  });
  
  return (
    <List>
      <Table {...tableProps}>
        <Table.Column dataIndex="id" title="ID" />
        <Table.Column dataIndex="name" title="名称" />
        <Table.Column dataIndex="status" title="状态" />
        <Table.Column dataIndex="created_at" title="创建时间" />
        <Table.Column
          title="操作"
          render={(record) => (
            <>
              <EditButton hideText recordItemId={record.id} />
              <DeleteButton hideText recordItemId={record.id} />
            </>
          )}
        />
      </Table>
    </List>
  );
};
```

**这个代码你可以**：

- 直接使用（功能完整）
- 作为起点修改（符合你的需求）
- 保留核心逻辑，换 UI（用 shadcn/ui 替换 Ant Design）

---

## 实战：用 Refine + shadcn/ui 搭建后台

### 步骤 1：创建项目

```bash
npm create refine-app@latest my-admin -- \
  --preset next \
  --ui shadcn
```

### 步骤 2：配置 Data Provider

```tsx
// src/dataProvider.ts
import dataProvider from "@refinedev/simple-rest";

export const dataProvider = {
  ...dataProvider("https://your-fastapi.com/api"),
  
  // 适配 FastAPI 的分页格式
  getList: async ({ resource, pagination, filters, sorters }) => {
    const params = new URLSearchParams({
      page: String(pagination.current),
      size: String(pagination.pageSize),
    });
    
    const response = await fetch(`/api/${resource}?${params}`);
    const { items, total } = await response.json();
    
    return { data: items, total };
  },
};
```

### 步骤 3：配置资源

```tsx
// src/app.tsx
import { Refine } from "@refinedev/core";
import { dataProvider } from "./dataProvider";

export default function App() {
  return (
    <Refine
      dataProvider={dataProvider}
      resources={[
        {
          name: "projects",
          list: "/projects",
          create: "/projects/create",
          edit: "/projects/edit/:id",
          meta: { label: "项目" },
        },
        {
          name: "tasks",
          list: "/tasks",
          create: "/tasks/create",
          edit: "/tasks/edit/:id",
          meta: { label: "任务" },
        },
        {
          name: "users",
          list: "/team",
          meta: { label: "团队" },
        },
      ]}
    >
      {/* 你的路由配置 */}
    </Refine>
  );
}
```

### 步骤 4：用 Inferencer 生成页面

```bash
npx @refinedev/cli@latest inferencer
```

这会在 `src/pages/` 下生成：

```
pages/
  projects/
    list.tsx
    show.tsx
    create.tsx
    edit.tsx
  tasks/
    list.tsx
    show.tsx
    create.tsx
    edit.tsx
  users/
    list.tsx
```

### 步骤 5：美化 UI

生成的代码用的是 shadcn/ui 组件。你可以直接修改：

```tsx
// src/pages/projects/list.tsx
import { Table } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useList } from "@refinedev/core";

export const ProjectList = () => {
  const { data, isLoading } = useList({ resource: "projects" });
  
  if (isLoading) return <div>加载中...</div>;
  
  return (
    <div className="p-6">
      <div className="flex justify-between mb-4">
        <h1 className="text-2xl font-bold">项目列表</h1>
        <Button>新建项目</Button>
      </div>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>名称</TableHead>
            <TableHead>状态</TableHead>
            <TableHead>创建时间</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.data.map((project) => (
            <TableRow key={project.id}>
              <TableCell>{project.name}</TableCell>
              <TableCell>{project.status}</TableCell>
              <TableCell>{project.created_at}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
```

---

## 对比：Refine vs 传统开发

假设你要开发一个包含 5 个资源的后台（projects、tasks、users、teams、settings）：

| 能力 | 传统开发 | 用 Refine |
|------|----------|-----------|
| **列表分页** | 每个页面手写（5 × 50 行） | 自动 |
| **搜索过滤** | 每个页面手写（5 × 30 行） | 自动 |
| **排序** | 每个页面手写（5 × 20 行） | 自动 |
| **新建表单** | 每个页面手写（5 × 100 行） | 自动生成 |
| **编辑表单** | 每个页面手写（5 × 100 行） | 自动生成 |
| **API 错误处理** | 每个调用手写（N × 10 行） | 统一处理 |
| **乐观更新** | 手写（复杂） | 内置 |
| **权限控制** | 每个按钮判断（N × 5 行） | Provider 统一 |
| **侧边栏菜单** | 手写配置（50 行） | 自动生成 |
| **路由配置** | 手写（5 × 4 × 5 行） | 自动生成 |
| **总代码量** | **约 3000 行** | **约 300 行**（主要是 Data Provider + UI 美化） |

**开发时间对比**：

| 阶段 | 传统开发 | 用 Refine |
|------|----------|-----------|
| 搭建框架 | 2 天 | 0.5 天 |
| 写 CRUD 页面 | 5 天 | 0.5 天（Inferencer） |
| 美化 UI | 2 天 | 2 天 |
| 处理边界情况 | 3 天 | 1 天 |
| **总计** | **12 天** | **4 天** |

---

## Refine 的局限

### 1. 后端 API 要规范

Refine 的核心假设：**API 即界面**。

如果你的 API 是标准的 RESTful：

```
GET    /api/projects
GET    /api/projects/:id
POST   /api/projects
PUT    /api/projects/:id
DELETE /api/projects/:id
```

Refine 可以零成本对接。

但如果你的 API 比较随意：

```
GET  /api/get_project_list
POST /api/create_new_project
GET  /api/project_detail?id=123
```

你就得写很多自定义 Data Provider，优势减弱。

**建议**：用 Refine 之前，先规范后端 API。

### 2. 学习成本

Refine 的概念：

- Data Provider
- Auth Provider
- Resource
- Access Control
- Live Mode（实时更新）
- Audit Log（操作日志）

**学习曲线**：中等。比从头写低，比用 Ant Design Pro 高。

### 3. 复杂场景还是要手写

如果你的页面：

- 有复杂的图表
- 有拖拽排序
- 有复杂的联动逻辑
- 有非 CRUD 的业务

Refine 帮不了你。它只解决 **CRUD 部分**。

但好消息是：**Refine 不妨碍你手写**。你可以在 Refine 项目里混用手写页面。

---

## 总结：Refine 的价值

Refine 解决了一个真实痛点：**后台管理界面的重复劳动**。

它的核心价值：

1. **API 驱动界面**：后端 API 结构决定前端页面结构
2. **Headless 设计**：业务逻辑和 UI 完全分离
3. **Provider 抽象**：数据、认证、权限统一管理
4. **Inferencer**：自动生成 CRUD 页面代码

**适合的场景**：

- 后台管理系统
- Admin Panel
- Dashboard
- B2B 应用
- 内部工具

**不适合的场景**：

- 面向 C 端的产品（UI 要求高）
- 非 CRUD 为主的业务
- API 非常不规范的后端

**我的建议**：

如果你的项目符合以下条件，强烈推荐尝试 Refine：

1. 后端是 RESTful API（或者可以改成 RESTful）
2. 大部分页面是 CRUD
3. 愿意接受新的架构方式
4. 用 React 技术栈

Refine + shadcn/ui 是一个很好的组合：**Refine 负责业务逻辑，shadcn/ui 负责美观 UI**。

这样既享受了 Refine 的开发效率，又不会变成 Ant Design 那种"一眼模板"的 UI。

---

## 参考

- [Refine 官网](https://refine.dev)
- [Refine GitHub](https://github.com/refinedev/refine) - 34,898 ⭐
- [Refine 文档](https://refine.dev/docs/)
- [Inferencer 文档](https://refine.dev/docs/packages/documentation/inferencer/)
- [Data Provider 列表](https://refine.dev/docs/data/data-provider/)
