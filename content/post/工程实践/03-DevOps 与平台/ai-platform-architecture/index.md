---
title: 企业AI工具平台架构设计：拥抱快速变化的AI生态
description: 探讨如何设计一个高扩展性、模块化的企业AI工具平台，支持多容器、多项目、用户管理以及各类AI工具的统一集成。
date: 2025-01-15T10:00:00+08:00
slug: ai-platform-architecture
image: images/index/index.svg
categories:
    - Engineering
tags:
    - Architecture
    - AI Platform
    - Enterprise Tools
    - Extensible Design
    - Multi-tenancy
draft: false
---

# 企业AI工具平台架构设计：拥抱快速变化的AI生态

> "唯一不变的是变化本身" —— 这句话在AI领域尤为贴切。本文探讨如何设计一个既能满足当前需求，又能优雅应对未来变化的企业AI工具平台。

## 核心理念

> **"数据是资产，必须持久化；Agent是工具，可以随时替换"**

这是本平台设计的核心哲学，贯穿整个架构设计。

### 为什么这样设计？

AI领域的变化速度远超传统软件：
- 去年最好的模型，今年可能已经被超越
- 今年流行的Agent框架，明年可能就有更好的替代
- 今天支持的协议，明天可能就有更优的标准

如果平台紧耦合某个特定的AI服务或Agent框架，当它过时或出问题的时候，平台就会陷入困境。

而用户的数据——创建的智能体、积累的知识、对话的历史——这些才是真正的资产，不应该因为技术迭代而被丢失。

### 分层设计思想

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          分层架构                                        │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 1: 持久化层 (数据资产)                                      │   │
│  │   PostgreSQL + 对象存储                                          │   │
│  │   • 用户数据    • Agent配置    • 知识库原文    • 对话历史        │   │
│  │   ★ 永久保留，跨版本迁移，跨供应商迁移                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼ (可重建)                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 2: 索引层 (可重建)                                         │   │
│  │   向量数据库 + 搜索引擎                                           │   │
│  │   • 向量索引    • 倒排索引    • 全文索引                          │   │
│  │   ← 从 Layer 1 可以100%重建                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼ (可替换)                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 3: Agent工具层                                             │   │
│  │   从注册中心动态加载                                             │   │
│  │   • Claude Code    • OpenCAW    • OpenCode    • Custom...       │   │
│  │   ← 随时可替换，配置不变                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼ (可扩展)                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 4: AI模型层                                               │   │
│  │   适配器模式                                                     │   │
│  │   • OpenAI    • Claude    • GLM    • Qwen    • DeepSeek...      │   │
│  │   ← 新模型接入只需实现适配器                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 设计原则

| 原则 | 含义 | 实践 |
|------|------|------|
| **数据主权** | 用户的数据属于用户 | 可导出、可迁移、可删除 |
| **存储与计算分离** | 数据持久化，Agent按需调用 | 数据库存数据，运行时加载工具 |
| **接口稳定，实现可变** | 契约不变，实现灵活 | 固定接口定义，适配器可替换 |
| **核心稳定，边缘灵活** | 核心不变，边缘扩展 | 稳定层vs灵活层 |
| **Layer 1 是唯一真相** | 原始数据不可丢失 | 索引可重建，原始数据不可 |

### 三个"不怕"

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   不怕换模型         不怕换Agent        不怕换向量数据库                 │
│   ─────────         ─────────         ──────────────                     │
│   适配器模式         注册中心           索引重建服务                     │
│   接口不变           热插拔             从Layer 1重建                     │
│                                                                         │
│   配置在DB           配置在DB           原文在PostgreSQL                 │
│   模型随便换         Agent随便换        向量随便换                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心价值

- **面向未来**：新模型、新Agent、新协议出现时，可以轻松接入
- **数据安全**：用户数据永久保留，不因技术迭代而丢失
- **成本可控**：根据业务需求灵活选择性价比最优的方案
- **员工激励**：贡献的知识和配置可以跨版本使用

---

## 背景与挑战

### AI领域的现状

当前AI领域呈现出几个显著特点：

1. **模型快速迭代**
   - 国际：GPT-4o、GPT-o1、Claude 3.5、Gemini 2.0 等不断推陈出新
   - 国内：智谱GLM-4、通义Qwen、DeepSeek、百度文心、字节豆包等百花齐放
   - 每个模型都有其擅长的领域：推理、创作、长文本、多模态...

2. **工具生态繁荣**
   - RAG（检索增强生成）能力日益成熟
   - Agent（智能体）框架快速演进
   - Function Calling、Tool Use 成为标配
   - MCP（Model Context Protocol）协议崭露头角

3. **企业需求多样**
   - 不同部门需要不同的AI能力组合
   - 不同项目有不同的数据隔离要求
   - 不同的成本和合规考虑

4. **员工参与诉求**
   - 希望员工能自主创建智能体
   - 希望能设计适合团队的工作流
   - 希望能贡献和分享知识

### 核心痛点

| 痛点 | 描述 | 影响 |
|------|------|------|
| 紧耦合 | AI模型直接嵌入业务代码 | 新模型接入成本高 |
| 信息孤岛 | 各部门重复建设AI能力 | 资源浪费，标准不一 |
| 难复用 | 好的智能体/工作流难以分享 | 重复造轮子 |
| 无激励 | 员工贡献无人知晓 | 参与度低 |

### 设计目标

基于这些背景，我们的设计必须满足：

- **扩展性优先**：新模型、新工具能低成本接入
- **灵活性**：支持多容器、多项目隔离
- **激励性**：鼓励员工贡献智能体和工作流
- **核心收敛**：用户管理与工具接口作为稳定内核

---

## 整体架构设计

### 分层架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户层 (User Layer)                            │
│                    Web Console │ CLI │ API Gateway │ SDK │
├─────────────────────────────────────────────────────────────────────────┤
│                        业务应用层 (App Layer)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   智能体     │  │   工作流     │  │   知识库     │  │   插件市场   │ │
│  │   Agent │  │   Workflow   │  │   Knowledge  │  │   Marketplace│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                         编排调度层 (Orchestration)                      │
│      Agent Runtime │ Workflow Engine │ Task Scheduler │ Event Bus │
├─────────────────────────────────────────────────────────────────────────┤
│                         核心服务层 (Core Services)                      │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │  用户管理    │  │  容器管理    │  │  项目管理    │  │  权限管理    │   │
│   │  User Mgmt │  │  Tenant │  │  Project    │  │  Permission │   │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                         集成层 (Integration Layer)                      │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     Adapter Registry                             │   │
│   │  ┌────────┐ ┌────────┐┌────────┐ ┌────────┐ ┌────────┐       │   │
│   │  │ OpenAI │ │Claude │ │ Gemini │ │ 智谱   │ │ 通义   │ ... │   │
│   │  │Adapter │ │Adapter │ │Adapter │ │Adapter │ │Adapter │       │   │
│   │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                         外部AI服务 (External AI Services)                │
│      OpenAI │ Anthropic │ Google │ 智谱AI │ 阿里云 │ 百度 │ ... │
└─────────────────────────────────────────────────────────────────────────┘
```

### 各层职责详解

#### 1. 用户层 (User Layer)

这是用户与平台交互的入口点，提供多种访问方式：

| 入口 | 说明 | 典型场景 |
|------|------|----------|
| **Web Console** | 浏览器访问的管理控制台 | 日常管理、智能体创建 |
| **CLI** | 命令行工具 | 开发者集成、自动化脚本 |
| **API Gateway** | RESTful API | 第三方集成、系统对接 |
| **SDK** | 多语言SDK | 应用内集成 |

#### 2. 业务应用层 (App Layer)

这是平台的核心业务能力：

##### 2.1 智能体 (Agent)

智能体是平台的核心生产力单元：

```python
@dataclass
class Agent:
    id: str
    name: str
    description: str
    model_config: ModelConfig
    
    # 组成要素
    instructions: str          # 系统提示词
    tools: list[str]          # 关联的工具
    knowledge_ids: list[str]  # 关联的知识库
    
    # 元数据
    created_by: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    
    # 分享与激励
    is_public: bool           # 是否公开分享
    likes: int = 0            # 点赞数
    uses: int = 0             # 使用次数
    
    # 版本控制
    version: int = 1
    version_history: list[dict] = field(default_factory=list)
```

**智能体类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| 对话型 | 问答交互 | 客服机器人 |
| 任务型 | 完成特定任务 | 代码审查助手 |
| 分析型 | 数据分析处理 | 报表生成器 |
| 创作型 | 内容生成 | 文案撰写助手 |

##### 2.2 工作流 (Workflow)

工作流实现复杂的自动化流程编排：

```python
@dataclass
class Workflow:
    id: str
    name: str
    description: str
    
    # 工作流定义
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]
    
    # 执行配置
    trigger_type: TriggerType  # manual/scheduled/event
    trigger_config: dict
    timeout: int = 300         # 超时时间(秒)
    
    # 元数据
    created_by: str
    project_id: str
    is_public: bool
    likes: int = 0

@dataclass
class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    config: dict
    position: tuple[int, int]
    
@dataclass  
class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    condition: str | None     # 条件判断
    label: str | None
```

**工作流节点类型**：

```
┌──────────────────────────────────────────────────────────────┐
│                    工作流节点类型                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  开始    │  │  Agent  │  │  工具   │  │  条件   │        │
│  │  Start  │  │         │  │  Tool   │  │ Condition│        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       ▼            ▼            ▼            ▼               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  输入    │  │  LLM    │  │  搜索   │  │  分支   │        │
│  │  Input  │  │  Call   │  │  Search │  │  Branch │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       ▼            ▼            ▼            ▼               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  输出    │  │  知识库 │  │  脚本   │  │  循环   │        │
│  │  Output │  │  RAG    │  │  Script │  │  Loop   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       └────────────┴────────────┴────────────┘               │
│                         ▼                                     │
│                  ┌─────────┐                                 │
│                  │   结束   │                                 │
│                  │   End   │                                 │
│                  └─────────┘                                 │
└──────────────────────────────────────────────────────────────┘
```

##### 2.3 知识库 (Knowledge)

支持多种知识来源：

| 类型 | 说明 | 格式支持 |
|------|------|----------|
| **文档库** | 上传文档 | PDF、Word、PPT、TXT、Markdown |
| **网页抓取** | 同步网页内容 | URL |
| **数据库** | 连接数据库 | MySQL、PostgreSQL、MongoDB |
| **API** | 接入外部API | REST API |
| **向量库** | 直接导入向量 | Embedding批量导入 |

##### 2.4 插件市场 (Marketplace)

开放的插件生态：

```python
@dataclass
class Plugin:
    id: str
    name: str
    version: str
    author: str
    description: str
    
    # 插件类型
    type: PluginType  # model/tool/memory/middleware
    
    # 能力定义
    capabilities: list[str]
    
    # 配置
    config_schema: dict
    default_config: dict
    
    # 分享与激励
    downloads: int = 0
    rating: float = 0.0
    reviews: list[Review] = field(default_factory=list)
```

#### 3. 编排调度层 (Orchestration)

这一层负责智能体和工作的运行调度：

| 组件 | 职责 |
|------|------|
| **Agent Runtime** | 智能体的运行时环境，管理会话、上下文、工具调用 |
| **Workflow Engine** | 工作流的执行引擎，处理节点调度、条件分支、循环 |
| **Task Scheduler** | 任务调度器，支持定时任务、延迟任务、优先级队列 |
| **Event Bus** | 事件总线，解耦组件间通信，支持发布订阅模式 |

#### 4. 核心服务层 (Core Services)

这是平台最稳定的基础能力：

##### 4.1 用户管理 (User Management)

```python
@dataclass
class User:
    id: str
    name: str
    email: str
    phone: str | None
    avatar: str | None
    
    # 组织关系
    tenant_id: str           # 所属容器
    department: str          # 部门
    position: str           # 职位
    
    # 角色与权限
    role: UserRole           # admin/editor/viewer
    
    # 贡献积分
    contribution_score: int = 0
    badges: list[str] = field(default_factory=list)
    
    # 时间戳
    created_at: datetime
    last_login_at: datetime

class UserRole(Enum):
    TENANT_ADMIN = "tenant_admin"    # 容器管理员
    PROJECT_ADMIN = "project_admin" # 项目管理员
    EDITOR = "editor"               # 编辑者
    VIEWER = "viewer"              # 查看者
```

##### 4.2 容器管理 (Tenant Management)

容器是最大的隔离单元，通常对应一个部门或业务线：

```python
@dataclass
class Tenant:
    id: str
    name: str                      # 容器名称，如"研发中心"
    code: str                      # 唯一标识，如"rd"
    
    # 配置
    config: TenantConfig
    
    # 配额
    quotas: TenantQuotas
    
    # 成员
    member_count: int
    project_count: int
    
    # 状态
    status: TenantStatus = TenantStatus.ACTIVE
    created_at: datetime

@dataclass
class TenantConfig:
    # AI模型配置
    allowed_providers: list[str]   # 允许使用的AI提供商
    default_provider: str         # 默认提供商
    model_restrictions: dict       # 模型限制
    
    # 功能开关
    features: dict                 # 功能开关
    
    # 安全配置
    allowed_ips: list[str]         # IP白名单
    data_retention_days: int       # 数据保留天数

@dataclass
class TenantQuotas:
    max_users: int                 # 最大用户数
    max_projects: int              # 最大项目数
    max_agents: int                # 最大智能体数
    max_workflows: int             # 最大工作流数
    max_storage_gb: int             # 最大存储(GB)
    monthly_token_limit: int       # 月度Token限额
```

##### 4.3 项目管理 (Project Management)

项目是容器内的业务单元：

```python
@dataclass
class Project:
    id: str
    name: str
    tenant_id: str                 # 所属容器
    code: str                      # 项目标识
    
    description: str
    icon: str | None
    
    # 成员
    owner_id: str                  # 项目负责人
    members: list[ProjectMember]
    
    # 配置
    config: ProjectConfig
    
    # 统计
    agent_count: int = 0
    workflow_count: int = 0
    knowledge_count: int = 0
    
    created_at: datetime
    updated_at: datetime

@dataclass
class ProjectMember:
    user_id: str
    role: ProjectRole              # owner/admin/member
    joined_at: datetime
```

##### 4.4 权限管理 (Permission Control)

采用RBAC（基于角色的访问控制）模型：

```python
class PermissionMatrix:
    """权限矩阵"""
    
    PERMISSIONS = {
        # 用户管理
        "user:create": ["tenant_admin"],
        "user:invite": ["tenant_admin"],
        "user:remove": ["tenant_admin"],
        
        # 容器管理
        "tenant:view": ["tenant_admin"],
        "tenant:edit": ["tenant_admin"],
        "tenant:quota": ["tenant_admin"],
        
        # 项目管理
        "project:create": ["tenant_admin", "project_admin"],
        "project:view": ["tenant_admin", "project_admin", "member"],
        "project:edit": ["tenant_admin", "project_admin"],
        "project:delete": ["tenant_admin", "project_admin"],
        
        # 智能体管理
        "agent:create": ["tenant_admin", "project_admin", "editor"],
        "agent:view": ["tenant_admin", "project_admin", "editor", "viewer"],
        "agent:edit": ["tenant_admin", "project_admin", "editor"],
        "agent:delete": ["tenant_admin", "project_admin", "editor"],
        "agent:publish": ["tenant_admin", "project_admin", "editor"],
        
        # 工作流管理
        "workflow:create": ["tenant_admin", "project_admin", "editor"],
        "workflow:view": ["tenant_admin", "project_admin", "editor", "viewer"],
        "workflow:edit": ["tenant_admin", "project_admin", "editor"],
        "workflow:delete": ["tenant_admin", "project_admin", "editor"],
        
        # 知识库管理
        "knowledge:create": ["tenant_admin", "project_admin", "editor"],
        "knowledge:view": ["tenant_admin", "project_admin", "editor", "viewer"],
        "knowledge:edit": ["tenant_admin", "project_admin", "editor"],
        "knowledge:delete": ["tenant_admin", "project_admin", "editor"],
    }
    
    @classmethod
    def check(cls, role: UserRole, permission: str) -> bool:
        return role.value in cls.PERMISSIONS.get(permission, [])
```

#### 5. 集成层 (Integration Layer)

这是平台的核心扩展机制：

##### 5.1 统一AI Provider接口

```python
class AIProvider(Protocol):
    """所有AI提供者必须实现的接口"""
    
    @property
    def name(self) -> str:
        """提供商名称"""
        ...
    
    @property
    def supported_models(self) -> list[str]:
        """支持的模型列表"""
        ...
    
    async def chat_completion(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[Tool] | None = None,
        **kwargs
    ) -> ChatResponse:
        """聊天补全"""
        ...
    
    async def embeddings(
        self,
        texts: list[str],
        model: str = "embeddings",
        **kwargs
    ) -> EmbeddingResponse:
        """文本嵌入"""
        ...
    
    async def images_generate(
        self,
        prompt: str,
        model: str,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageResponse:
        """图像生成"""
        ...
    
    async def models_list(self) -> list[ModelInfo]:
        """获取可用模型列表"""
        ...
    
    async def health_check(self) -> bool:
        """健康检查"""
        ...
```

##### 5.2 适配器实现示例

```python
class OpenAIAdapter:
    """OpenAI适配器"""
    
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.openai.com/v1",
        timeout: int = 60
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.client = OpenAIClient(api_key, api_base, timeout)
    
    @property
    def name(self) -> str:
        return "openai"
    
    @property
    def supported_models(self) -> list[str]:
        return [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "text-embedding-3-small",
            "text-embedding-3-large",
            "dall-e-3",
            "dall-e-2"
        ]
    
    async def chat_completion(
        self,
        messages: list[Message],
        model: str = "gpt-4o",
        **kwargs
    ) -> ChatResponse:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[m.to_dict() for m in messages],
            **kwargs
        )
        return ChatResponse.from_openai(response)
    
    async def embeddings(
        self,
        texts: list[str],
        model: str = "text-embedding-3-small"
    ) -> EmbeddingResponse:
        response = await self.client.embeddings.create(
            model=model,
            input=texts
        )
        return EmbeddingResponse.from_openai(response)


class ClaudeAdapter:
    """Anthropic Claude适配器"""
    
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.anthropic.com/v1",
        timeout: int = 60
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.client = AnthropicClient(api_key, api_base, timeout)
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    @property
    def supported_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-latest",
            "claude-3-opus-latest",
            "claude-3-haiku-latest"
        ]
    
    async def chat_completion(
        self,
        messages: list[Message],
        model: str = "claude-sonnet-4-20250514",
        **kwargs
    ) -> ChatResponse:
        response = await self.client.messages.create(
            model=model,
            messages=[m.to_anthropic_format() for m in messages],
            **kwargs
        )
        return ChatResponse.from_anthropic(response)


class DeepSeekAdapter:
    """DeepSeek适配器 - 演示新模型接入的简易性"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAICompatibleClient(
            api_key=api_key,
            api_base="https://api.deepseek.com/v1"
        )
    
    @property
    def name(self) -> str:
        return "deepseek"
    
    @property
    def supported_models(self) -> list[str]:
        return ["deepseek-chat", "deepseek-coder"]
    
    async def chat_completion(self, messages, model="deepseek-chat", **kwargs):
        response = await self.client.chat.completions.create(
            model=model,
            messages=[m.to_dict() for m in messages],
            **kwargs
        )
        return ChatResponse.from_openai(response)
```

##### 5.3 适配器注册中心

```python
class AdapterRegistry:
    """适配器注册中心 - 核心扩展机制"""
    
    def __init__(self):
        self._adapters: dict[str, AIProvider] = {}
        self._metadata: dict[str, AdapterMetadata] = {}
    
    def register(
        self,
        name: str,
        adapter: AIProvider,
        metadata: AdapterMetadata | None = None
    ):
        """注册适配器"""
        self._adapters[name] = adapter
        self._metadata[name] = metadata or AdapterMetadata(
            name=name,
            version="1.0.0",
            capabilities=["chat", "embeddings"]
        )
        logger.info(f"Registered adapter: {name}")
    
    def unregister(self, name: str):
        """注销适配器"""
        if name in self._adapters:
            del self._adapters[name]
            del self._metadata[name]
            logger.info(f"Unregistered adapter: {name}")
    
    def get(self, name: str) -> AIProvider | None:
        """获取适配器"""
        return self._adapters.get(name)
    
    def list_adapters(self) -> list[str]:
        """列出所有适配器"""
        return list(self._adapters.keys())
    
    def list_by_capability(self, capability: str) -> list[str]:
        """按能力筛选适配器"""
        return [
            name for name, meta in self._metadata.items()
            if capability in meta.capabilities
        ]
    
    async def health_check_all(self) -> dict[str, bool]:
        """检查所有适配器健康状态"""
        results = {}
        for name, adapter in self._adapters.items():
            try:
                results[name] = await adapter.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        return results


@dataclass
class AdapterMetadata:
    name: str
    version: str
    capabilities: list[str]
    description: str = ""
    author: str = ""
    docs_url: str = ""
```

##### 5.4 工具注册中心

```python
class ToolCapability(Protocol):
    """工具能力抽象"""
    
    @property
    def name(self) -> str:
        ...
    
    @property
    def description(self) -> str:
        ...
    
    def get_schema(self) -> ToolSchema:
        """获取工具定义schema，用于LLM function calling"""
        ...
    
    async def execute(
        self,
        context: ExecutionContext,
        params: dict
    ) -> ToolResult:
        """执行工具"""
        ...


class ToolType(Enum):
    """工具类型枚举"""
    RETRIEVER = "retriever"           # 知识检索
    WEB_SEARCH = "web_search"          # 网络搜索
    CALCULATOR = "calculator"         # 计算器
    CODE_INTERPRETER = "code"         # 代码执行
    FILE_SYSTEM = "filesystem"        # 文件操作
    DATABASE = "database"             # 数据库查询
    API_CALL = "api_call"             # API调用
    IMAGE_PROCESSOR = "image"         # 图像处理
    DOCUMENT_PARSER = "document"      # 文档解析
    CUSTOM = "custom"                 # 自定义工具


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self._tools: dict[str, ToolCapability] = {}
        self._by_type: dict[ToolType, list[str]] = defaultdict(list)
    
    def register(self, tool: ToolCapability, types: list[ToolType] = None):
        """注册工具"""
        self._tools[tool.name] = tool
        for tool_type in (types or [ToolType.CUSTOM]):
            self._by_type[tool_type].append(tool.name)
        logger.info(f"Registered tool: {tool.name}")
    
    def execute(
        self,
        tool_name: str,
        params: dict,
        context: ExecutionContext
    ) -> ToolResult:
        """执行工具"""
        tool = self._tools.get(tool_name)
        if not tool:
            raise ToolNotFoundError(f"Tool not found: {tool_name}")
        return await tool.execute(context, params)
    
    def list_by_type(self, tool_type: ToolType) -> list[ToolCapability]:
        """按类型列出工具"""
        tool_names = self._by_type.get(tool_type, [])
        return [self._tools[name] for name in tool_names]
```

##### 5.5 外部Agent框架集成（重点！）

这是你提到的关键需求：平台需要能随时接入市面上的Agent框架，如OpenCAW、Claude Code、OpenCode等。

###### 5.5.1 主流Agent框架分析

| 框架 | 特点 | 接入方式 | 复杂度 |
|------|------|----------|--------|
| **Claude Code** | Anthropic官方CLI，支持代码编写、审查、重构 | CLI调用/stdio | ⭐⭐ |
| **OpenCode** | 开源多语言支持，强大的代码编辑能力 | CLI调用/stdio | ⭐⭐ |
| **Codex** | OpenAI出品，强大的代码生成能力 | API调用 | ⭐ |
| **Devin** | 独立Agent，强大的自主完成任务能力 | API调用 | ⭐⭐⭐ |
| **OpenCAW** | 国产开源，开放架构，易于扩展 | MCP/CLI | ⭐⭐ |
| **SWE-agent** | 专门针对软件工程的Agent | CLI调用 | ⭐⭐ |
| **Devika** | 开源AI软件工程师，类Devin | API调用 | ⭐⭐ |

###### 5.5.2 统一Agent集成接口

```python
from abc import ABC, abstractmethod
from typing import Protocol, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio

class AgentFramework(Enum):
    """支持的Agent框架"""
    CLAUDE_CODE = "claude_code"
    OPENCODE = "opencode"
    CODEX = "codex"
    DEVIN = "devin"
    OPENCAW = "opencaw"
    SWE_AGENT = "swe_agent"
    CUSTOM = "custom"  # 支持自定义框架

@dataclass
class AgentExecutionRequest:
    """Agent执行请求"""
    task: str                          # 任务描述
    framework: AgentFramework          # 使用的框架
    working_dir: str # 工作目录
    timeout: int = 300                 # 超时时间(秒)
    allowed_tools: list[str] | None = None  # 允许的工具
    extra_config: dict = field(default_factory=dict)  # 框架特定配置

@dataclass
class AgentExecutionResponse:
    """Agent执行响应"""
    success: bool
    result: str | None
    error: str | None
    session_id: str | None
    duration_ms: int
    tokens_used: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

@dataclass
class AgentFrameworkMetadata:
    """框架元数据"""
    name: str
    version: str
    capabilities: list[str]           # ["code_generation", "code_review", ...]
    supported_languages: list[str]     # 支持的编程语言
    requires_permissions: list[str]    # 需要的权限
    config_schema: dict                # 配置schema
    auth_method: str                  # 认证方式: "api_key", "oauth", "cli_auth"

class ExternalAgentAdapter(ABC):
    """外部Agent框架适配器基类"""
    
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        """执行Agent任务"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
    
    @abstractmethod
    async def get_status(self) -> dict:
        """获取Agent状态"""
        pass
    
    def get_metadata(self) -> AgentFrameworkMetadata:
        """获取框架元数据"""
        raise NotImplementedError
```

###### 5.5.3 Claude Code适配器实现

```python
import subprocess
import json
import asyncio
from pathlib import Path

class ClaudeCodeAdapter(ExternalAgentAdapter):
    """Claude Code适配器"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.cli_path = config.get("cli_path", "claude")
        self.api_key = config.get("api_key")  # 可选，使用ANTHROPIC_API_KEY
        self.default_model = config.get("default_model", "sonnet")
    
    def get_metadata(self) -> AgentFrameworkMetadata:
        return AgentFrameworkMetadata(
            name="Claude Code",
            version="2.x",
            capabilities=[
                "code_generation",
                "code_review",
                "refactoring",
                "bug_fixing",
                "test_writing",
                "git_operations"
            ],
            supported_languages=[
                "python", "javascript", "typescript", "go", "rust",
                "java", "c", "cpp", "csharp", "ruby", "php"
            ],
            requires_permissions=["file_read", "file_write", "bash"],
            config_schema={
                "cli_path": {"type": "string", "default": "claude"},
                "default_model": {"type": "enum", "values": ["sonnet", "opus", "haiku"]},
                "max_turns": {"type": "int", "default": 10}
            },
            auth_method="api_key"
        )
    
    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        """执行Claude Code任务"""
        start_time = asyncio.get_event_loop().time()
        
        # 构建命令
        cmd = [
            self.cli_path,
            "-p", request.task,
            "--model", request.extra_config.get("model", self.default_model),
            "--output-format", "json",
            "--max-turns", str(request.extra_config.get("max_turns", 10))
        ]
        
        # 处理工具限制
        if request.allowed_tools:
            cmd.extend(["--allowedTools", ",".join(request.allowed_tools)])
        
        # 权限绕过（生产环境需谨慎）
        if request.extra_config.get("skip_permissions"):
            cmd.append("--dangerously-skip-permissions")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=request.working_dir,
                capture_output=True,
                text=True,
                timeout=request.timeout
            )
            
            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            if result.returncode == 0:
                # 解析JSON输出
                output = json.loads(result.stdout)
                return AgentExecutionResponse(
                    success=True,
                    result=output.get("result", ""),
                    session_id=output.get("session_id"),
                    duration_ms=duration_ms,
                    tokens_used=output.get("usage", {})
                )
            else:
                return AgentExecutionResponse(
                    success=False,
                    error=result.stderr,
                    duration_ms=duration_ms
                )
        except subprocess.TimeoutExpired:
            return AgentExecutionResponse(
                success=False,
                error=f"Task timeout after {request.timeout}s",
                duration_ms=request.timeout * 1000
            )
        except Exception as e:
            return AgentExecutionResponse(
                success=False,
                error=str(e),
                duration_ms=int((asyncio.get_event_loop().time() - start_time) * 1000)
            )
    
    async def health_check(self) -> bool:
        """检查Claude Code是否可用"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def get_status(self) -> dict:
        """获取Claude Code状态"""
        try:
            result = subprocess.run(
                [self.cli_path, "auth", "status", "--text"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "installed": True,
                "authenticated": "logged in" in result.stdout.lower(),
                "version": result.stdout.split("\n")[0] if result.stdout else "unknown"
            }
        except Exception as e:
            return {"installed": False, "error": str(e)}
```

###### 5.5.4 OpenCAW适配器实现

```python
class OpenCAWAdapter(ExternalAgentAdapter):
    """OpenCAW适配器 - 国产开源Agent框架"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_base = config.get("api_base", "http://localhost:8080")
        self.api_key = config.get("api_key")
        self.ws_endpoint = config.get("ws_endpoint")
    
    def get_metadata(self) -> AgentFrameworkMetadata:
        return AgentFrameworkMetadata(
            name="OpenCAW",
            version="1.x",
            capabilities=[
                "code_generation",
                "code_review",
                "mcp_integration",
                "multi_agent"
            ],
            supported_languages=["python", "javascript", "typescript", "go"],
            requires_permissions=["file_read", "file_write", "bash", "network"],
            config_schema={
                "api_base": {"type": "string"},
                "api_key": {"type": "string"},
                "ws_endpoint": {"type": "string"}
            },
            auth_method="api_key"
        )
    
    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        """通过HTTP API执行OpenCAW任务"""
        import aiohttp
        
        start_time = asyncio.get_event_loop().time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "task": request.task,
            "working_dir": request.working_dir,
            "timeout": request.timeout,
            "config": request.extra_config
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/execute",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as response:
                    data = await response.json()
                    
                    duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                    
                    if response.status == 200:
                        return AgentExecutionResponse(
                            success=True,
                            result=data.get("result"),
                            session_id=data.get("session_id"),
                            duration_ms=duration_ms,
                            metadata=data.get("metadata", {})
                        )
                    else:
                        return AgentExecutionResponse(
                            success=False,
                            error=data.get("error", "Unknown error"),
                            duration_ms=duration_ms
                        )
        except Exception as e:
            return AgentExecutionResponse(
                success=False,
                error=str(e),
                duration_ms=int((asyncio.get_event_loop().time() - start_time) * 1000)
            )
    
    async def health_check(self) -> bool:
        """检查OpenCAW服务状态"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def get_status(self) -> dict:
        """获取OpenCAW状态"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/api/status",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    return await response.json()
        except Exception as e:
            return {"error": str(e)}
```

###### 5.5.5 MCP协议集成

MCP（Model Context Protocol）是连接AI模型与外部工具的新标准，主流Agent框架正在逐步支持：

```python
class MCPBridge:
    """MCP协议桥接器 - 连接平台与外部Agent"""
    
    def __init__(self):
        self.servers: dict[str, MCPServer] = {}
        self.tools_cache: dict[str, list[ToolSchema]] = {}
    
    async def connect_server(
        self,
        name: str,
        command: str,
        args: list[str] = None,
        env: dict = None,
        transport: str = "stdio"  # stdio | http | sse
    ) -> bool:
        """连接MCP服务器"""
        server = MCPServer(
            name=name,
            command=command,
            args=args or [],
            env=env or {},
            transport=transport
        )
        
        try:
            await server.start()
            await server.initialize()
            
            # 获取可用工具
            tools = await server.list_tools()
            self.servers[name] = server
            self.tools_cache[name] = tools
            
            logger.info(f"Connected MCP server: {name} with {len(tools)} tools")
            return True
        except Exception as e:
            logger.error(f"Failed to connect MCP server {name}: {e}")
            return False
    
    async def disconnect_server(self, name: str):
        """断开MCP服务器"""
        if name in self.servers:
            await self.servers[name].stop()
            del self.servers[name]
            del self.tools_cache[name]
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict
    ) -> dict:
        """调用MCP工具"""
        server = self.servers.get(server_name)
        if not server:
            raise MCPServerNotFoundError(f"Server not found: {server_name}")
        
        return await server.call_tool(tool_name, arguments)
    
    def get_all_tools(self) -> list[dict]:
        """获取所有MCP服务器的工具清单"""
        all_tools = []
        for server_name, tools in self.tools_cache.items():
            for tool in tools:
                all_tools.append({
                    "server": server_name,
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema
                })
        return all_tools


@dataclass
class MCPServer:
    name: str
    command: str
    args: list[str]
    env: dict
    transport: str
    
    process: asyncio.subprocess.Process | None = None
    capabilities: dict = field(default_factory=dict)
    
    async def start(self):
        """启动MCP服务器进程"""
        env = {**os.environ, **self.env}
        self.process = await asyncio.create_subprocess_exec(
            self.command, *self.args,
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
    
    async def initialize(self):
        """初始化MCP协议"""
        # 发送initialize请求
        request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ai-platform", "version": "1.0"}
            }
        }
        # ...协议处理
```

###### 5.5.6 Agent框架注册中心

```python
class AgentFrameworkRegistry:
    """Agent框架注册中心 - 统一管理所有外部Agent"""
    
    def __init__(self):
        self._adapters: dict[AgentFramework, ExternalAgentAdapter] = {}
        self._metadata: dict[AgentFramework, AgentFrameworkMetadata] = {}
        self._mcp_bridge = MCPBridge()
        self._execution_history: list[AgentExecutionResponse] = []
    
    def register(
        self,
        framework: AgentFramework,
        adapter: ExternalAgentAdapter
    ):
        """注册Agent框架"""
        self._adapters[framework] = adapter
        self._metadata[framework] = adapter.get_metadata()
        logger.info(f"Registered agent framework: {framework.value}")
    
    def unregister(self, framework: AgentFramework):
        """注销Agent框架"""
        if framework in self._adapters:
            del self._adapters[framework]
            del self._metadata[framework]
            logger.info(f"Unregistered agent framework: {framework.value}")
    
    def get_adapter(self, framework: AgentFramework) -> ExternalAgentAdapter | None:
        """获取适配器"""
        return self._adapters.get(framework)
    
    def list_frameworks(self) -> list[AgentFrameworkMetadata]:
        """列出所有注册的框架"""
        return list(self._metadata.values())
    
    async def execute(
        self,
        request: AgentExecutionRequest
    ) -> AgentExecutionResponse:
        """统一执行入口"""
        adapter = self._adapters.get(request.framework)
        if not adapter:
            raise AgentFrameworkNotFoundError(
                f"Framework not supported: {request.framework.value}"
            )
        
        response = await adapter.execute(request)
        self._execution_history.append(response)
        
        # 记录执行统计
        await self._record_execution_stats(request.framework, response)
        
        return response
    
    async def execute_with_fallback(
        self,
        request: AgentExecutionRequest,
        fallback_frameworks: list[AgentFramework]
    ) -> AgentExecutionResponse:
        """带降级的执行 - 主框架失败时尝试备选框架"""
        # 首先尝试主框架
        try:
            response = await self.execute(request)
            if response.success:
                return response
        except Exception as e:
            logger.warning(f"Primary framework failed: {e}")
        
        # 尝试备选框架
        for framework in fallback_frameworks:
            try:
                request.framework = framework
                response = await self.execute(request)
                if response.success:
                    logger.info(f"Fallback to {framework.value} succeeded")
                    return response
            except Exception as e:
                logger.warning(f"Fallback framework {framework.value} failed: {e}")
                continue
        
        return AgentExecutionResponse(
            success=False,
            error="All frameworks failed"
        )
    
    async def health_check_all(self) -> dict[AgentFramework, bool]:
        """检查所有Agent框架健康状态"""
        results = {}
        for framework, adapter in self._adapters.items():
            try:
                results[framework] = await adapter.health_check()
            except Exception:
                results[framework] = False
        return results
```

###### 5.5.7 平台集成架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         外部Agent框架集成层 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │              Agent Framework Registry (注册中心)                 │     │
│    │                                                                 │     │
│    │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │     │
│    │   │Claude Code │  │  OpenCAW   │  │   Codex │  │  Custom  │ │     │
│    │   │  Adapter │  │  Adapter   │  │  Adapter   │  │  Adapter │ │     │
│    │   └────────────┘  └────────────┘  └────────────┘  └──────────┘ │     │
│    │ │              │              │               │        │     │
│    └──────────┼──────────────┼──────────────┼───────────────┼────────┘     │
│               │              │              │               │              │
│               ▼              ▼              ▼               ▼              │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                    MCP Bridge (协议桥接)                         │     │
│    │                                                                 │     │
│    │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │     │
│    │   │   MCP      │  │   MCP      │  │   MCP      │  │   MCP    │ │     │
│    │   │  Server 1  │  │  Server 2  │  │  Server 3  │  │   ... │ │     │
│    │   │ (GitHub)   │  │ ( Postgres) │ │ (Filesystem) │ │    │     │
│    │  └────────────┘  └────────────┘ └────────────┘  └──────────┘ │     │
│   └─────────────────────────────────────────────────────────────────┘     │
│ │                                            │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         平台编排调度层                                      │
│             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│   │ Agent │  │  Workflow  │  │    Task     │  │   Event     │      │
│   │ Runtime     │  │   Engine   │  │  Scheduler  │  │    Bus      │      │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐     │
│   │ Execution Router (执行路由)                         │     │
│   │   • 框架选择策略  • 降级策略  • 并发控制  • 超时管理 │     │
│   └─────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

###### 5.5.8 新增框架接入指南

**快速接入新框架只需3步：**

```python
# Step 1: 实现适配器
class NewFrameworkAdapter(ExternalAgentAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        # 初始化配置
    
    def get_metadata(self) -> AgentFrameworkMetadata:
        return AgentFrameworkMetadata(
            name="NewFramework",
            version="1.0",
            capabilities=["..."],
            supported_languages=["..."],
            requires_permissions=["..."],
            config_schema={},
            auth_method="..."
        )
    
    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        # 实现执行逻辑
        pass
    
    async def health_check(self) -> bool:
        # 健康检查
        pass

# Step 2: 注册到框架注册中心
registry = AgentFrameworkRegistry()
registry.register(
    AgentFramework("new_framework"),
    NewFrameworkAdapter({"api_key": "..."})
)

# Step 3: 在平台中使用
response = await registry.execute(AgentExecutionRequest(
    task="帮我修复这个bug",
    framework=AgentFramework("new_framework"),
    working_dir="/path/to/project"
))
```

---

## 核心设计原则：数据资产化 · Agent工具化

> 这是本平台最重要的架构设计原则：**用户的数据是核心资产，必须持久化；Agent是工具，可以随时替换。**

### 设计哲学

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ┌───────────────────────────────────────────────────────────────────┐   │
│    │                        数据资产 (Data Assets)                        │   │
│    │                                                                     │   │
│    │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│    │   │   知识库    │  │  对话记录   │  │  使用痕迹   │              │   │
│    │   │ Knowledge  │  │  Sessions   │  │  Usage Logs │              │   │
│    │   └─────────────┘  └─────────────┘  └─────────────┘              │   │
│    │                                                                     │   │
│    │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│    │   │   智能体    │  │  工作流     │  │   配置文件  │              │   │
│    │   │  Config    │  │  Config    │  │   Settings  │              │   │
│    │   └─────────────┘  └─────────────┘  └─────────────┘              │   │
│    │                                                                     │   │
│    │   ★ 持久化存储 ★ 跨版本迁移 ★ 数据主权 ★                         │   │
│    │                                                                     │   │
│    └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│    ┌───────────────────────────────────────────────────────────────────┐   │
│    │                        Agent工具 (Agent Tools)                      │   │
│    │                                                                     │   │
│    │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│    │   │ Claude Code │  │  OpenCAW   │  │   Custom    │              │   │
│    │   └─────────────┘  └─────────────┘  └─────────────┘              │   │
│    │                                                                     │   │
│    │   • 即插即用    • 版本迭代    • 随时替换                          │   │
│    │                                                                     │   │
│    └───────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 核心原则

| 原则 | 说明 | 实践 |
|------|------|------|
| **数据主权** | 用户数据属于用户，平台只是保管者 | 数据可导出、可迁移、可删除 |
| **存储与计算分离** | 数据持久化，Agent按需调用 | 数据在数据库，Agent在注册中心 |
| **接口稳定，实现可变** | 数据模型稳定，Agent实现灵活 | 固定AIProvider接口，适配器可替换 |
| **版本兼容** | 新版本必须兼容旧数据 | 数据迁移脚本，版本回滚支持 |

### 数据模型设计

```python
# ============================================================================
# 用户数据层 (必须持久化)
# ============================================================================

@dataclass
class UserData:
    """用户核心数据 - 永久存储"""
    id: str
    name: str
    email: str
    tenant_id: str
    
    # 创建的数据
    created_agents: list[str]      # 创建的智能体ID列表
    created_workflows: list[str]    # 创建的工作流ID列表
    created_knowledge: list[str]   # 创建的知识库ID列表
    
    # 配置与偏好
    preferences: UserPreferences
    api_keys: list[APIKey]         # 绑定的API密钥
    
    # 元数据
    created_at: datetime
    updated_at: datetime

@dataclass
class UserPreferences:
    """用户偏好设置"""
    default_model: str
    theme: str = "light"
    language: str = "zh-CN"
    notification_enabled: bool = True

@dataclass
class AgentConfig:
    """智能体配置 - 持久化"""
    id: str
    user_id: str                    # 所有者
    
    # 配置内容（持久化的核心）
    name: str
    description: str
    instructions: str               # 系统提示词
    model_config: ModelConfig       # 模型配置
    
    # 关联数据
    tool_ids: list[str]            # 关联的工具ID
    knowledge_ids: list[str]       # 关联的知识库ID
    
    # 版本控制
    version: int
    version_history: list[AgentVersion]
    
    # 公开属性
    is_public: bool = False
    tags: list[str] = field(default_factory=list)
    
    created_at: datetime
    updated_at: datetime

@dataclass
class WorkflowConfig:
    """工作流配置 - 持久化"""
    id: str
    user_id: str
    project_id: str
    
    name: str
    description: str
    nodes: list[WorkflowNode]      # 节点定义（持久化）
    edges: list[WorkflowEdge]      # 连线定义（持久化）
    
    trigger_config: dict
    version: int
    
    is_public: bool = False
    
    created_at: datetime
    updated_at: datetime

# ============================================================================
# 知识库 - 持久化 (分层设计)
# ============================================================================

@dataclass
class KnowledgeBase:
    """知识库 - 分层持久化设计"""
    id: str
    user_id: str
    project_id: str
    
    name: str
    description: str
    
    # ========== 持久化层 (原始数据，不可丢失) ==========
    
    # 1. 原始文档 - 对象存储 (真正持久化)
    raw_documents: list[RawDocument]       # PDF/Word/MD等原始文件
    
    # 2. 解析后的结构化数据 - PostgreSQL
    parsed_content: list[ParsedDocument]   # 提取的文本、结构
    
    # 3. 元数据 - PostgreSQL
    metadata: KnowledgeMetadata
    
    # ========== 可重建索引层 (可以从原始数据重新生成) ==========
    
    # 4. 向量索引 - 向量数据库 (可重建)
    vector_index_id: str | None            # 指向向量数据库中的索引
    embedding_model: str
    
    # 5. 统计信息 - PostgreSQL
    doc_count: int = 0
    chunk_count: int = 0
    total_size_bytes: int = 0
    
    created_at: datetime
    updated_at: datetime

@dataclass
class RawDocument:
    """原始文档 - 真正持久化到对象存储"""
    id: str
    knowledge_base_id: str
    
    # 存储位置（对象存储路径）
    storage_path: str                       # s3://bucket/knowledge/{kb_id}/{doc_id}/file.pdf
    storage_bucket: str
    storage_region: str
    
    # 文件信息
    filename: str
    file_size: int
    mime_type: str                          # application/pdf, text/markdown, ...
    
    # 内容哈希（完整性校验）
    content_hash: str                       # SHA256
    
    # 版本控制
    version: int
    previous_versions: list[str]           # 历史版本ID列表
    
    uploaded_at: datetime
    updated_at: datetime

@dataclass
class ParsedDocument:
    """解析后的文档内容 - PostgreSQL持久化"""
    id: str
    raw_document_id: str
    
    # 解析后的文本内容（原始文本副本）
    content: str                            # 完整文本内容
    content_length: int
    
    # 结构化提取
    title: str | None
    author: str | None
    created_date: datetime | None
    sections: list[DocumentSection]        # 分节信息
    
    # 预处理标记
    language: str
    encoding: str
    
    parsed_at: datetime

@dataclass
class DocumentSection:
    """文档章节"""
    title: str
    start_char: int
    end_char: int
    level: int                              # 1=h1, 2=h2, 3=h3...
    subsections: list[DocumentSection] = field(default_factory=list)

@dataclass
class KnowledgeMetadata:
    """知识库元数据 - PostgreSQL"""
    id: str
    knowledge_base_id: str
    
    # 索引状态
    index_status: IndexStatus               # pending/processing/completed/failed
    vector_index_id: str | None            # 向量数据库中的索引ID
    
    # 嵌入配置
    embedding_model: str                   # "text-embedding-3-small"
    chunk_size: int = 512                   # 块大小
    chunk_overlap: int = 50                # 重叠大小
    
    # 统计
    total_documents: int = 0
    total_chunks: int = 0
    indexed_chunks: int = 0
    
    # 最后一次索引时间
    last_indexed_at: datetime | None
    last_error: str | None

@dataclass
class VectorIndex:
    """向量索引记录 - 记录索引元信息，可重建"""
    id: str
    knowledge_base_id: str
    
    # 索引来源
    source_document_ids: list[str]         # 关联的原始文档
    
    # 索引配置
    embedding_model: str
    dimension: int
    metric: str                             # "cosine" / "euclidean"
    
    # 向量数据库连接信息
    vector_db_type: str                    # "milvus" / "qdrant" / "pinecone"
    vector_db_endpoint: str
    collection_name: str
    
    # 状态
    status: str                            # "active" / "rebuilding" / "failed"
    
    # 统计
    total_vectors: int = 0
    vector_count_by_doc: dict[str, int] = field(default_factory=dict)  # doc_id -> count
    
    created_at: datetime
    updated_at: datetime
```

```python
# ============================================================================
# 会话数据层 (重要的运行时数据)
# ============================================================================

@dataclass
class Session:
    """会话 - 重要数据，需持久化"""
    id: str
    user_id: str
    agent_id: str                   # 使用的智能体
    
    # 对话历史（持久化核心）
    messages: list[Message]
    
    # 会话上下文
    context: dict                   # 会话级别的上下文变量
    
    # 统计
    message_count: int
    token_usage: TokenUsage
    
    # 状态
    status: SessionStatus           # active/archived/deleted
    pinned: bool = False
    
    created_at: datetime
    updated_at: datetime

@dataclass
class Message:
    """消息"""
    id: str
    session_id: str
    
    role: MessageRole               # user/assistant/system/tool
    content: str
    
    # 工具调用记录
    tool_calls: list[ToolCall] | None
    
    # 元数据
    model: str                      # 使用的模型
    latency_ms: int | None
    tokens_used: int | None
    
    created_at: datetime

@dataclass
class TokenUsage:
    """Token使用统计 - 用于计费和监控"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # 按模型统计
    by_model: dict[str, int] = field(default_factory=dict)
    
    # 按时间统计
    daily_usage: dict[str, int] = field(default_factory=dict)  # date -> tokens

@dataclass
class UsageLog:
    """使用日志 - 必须持久化"""
    id: str
    user_id: str
    tenant_id: str
    
    # 使用信息
    resource_type: ResourceType    # agent/workflow/knowledge
    resource_id: str
    action: str                    # chat/run/search
    
    # 消耗
    tokens_used: int
    latency_ms: int
    cost_usd: float
    
    # 上下文（用于分析）
    model: str | None
    session_id: str | None
    
    created_at: datetime
```

```python
# ============================================================================
# Agent运行时层 (临时，可替换)
# ============================================================================

class AgentRuntime:
    """Agent运行时 - 不持久化，动态创建"""
    
    def __init__(self, config: AgentConfig, adapter: ExternalAgentAdapter):
        self.config = config
        self.adapter = adapter
        self.session_context: dict = {}
    
    async def chat(self, message: str) -> str:
        """聊天执行"""
        # 使用adapter执行
        response = await self.adapter.execute(...)
        return response.result
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str]:
        """流式聊天"""
        async for chunk in self.adapter.stream_execute(...):
            yield chunk

# ============================================================================
# 数据流向
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户数据流向                                     │
│                                                                             │
│    User ─────────────────────────────────────────────────────────────────▶ │
│      │                                                                     │
│      │ 1. 创建数据                                                          │
│      ▼                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│  │   知识库    │────▶│   智能体    │────▶│   工作流    │                  │
│  │ 持久化存储  │     │   配置      │     │   配置      │                  │
│  └─────────────┘     └─────────────┘     └─────────────┘                  │
│      │                     │                     │                         │
│      │                     │                     │                         │
│      ▼                     │                     │                         │
│  ┌─────────────┐           │                     │                         │
│  │   会话      │◀──────────┤                     │                         │
│  │   历史      │           │                     │                         │
│  └─────────────┘           │                     │                         │
│      │                     │                     │                         │
│      │                     │                     │                         │
│      ▼                     ▼                     ▼                         │
│  ┌─────────────────────────────────────────────────────────────────┐      │
│  │                    PostgreSQL / 向量数据库                        │      │
│  │                 (数据永久存储，可迁移、可导出)                      │      │
│  └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                             Agent调用流程                                     │
│                                                                             │
│    User Request                                                              │
│         │                                                                     │
│         ▼                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│  │   加载      │────▶│   调用      │────▶│   返回      │                  │
│  │ AgentConfig │     │  Agent      │     │  Response   │                  │
│  │ (从DB读取)  │     │  Runtime    │     │             │                  │
│  └─────────────┘     └──────┬──────┘     └─────────────┘                  │
│                             │                                             │
│                             ▼                                             │
│                    ┌─────────────┐                                       │
│                    │  Agent      │  ← 可以随时替换                         │
│                    │  Adapter    │    (Claude/DeepSeek/...)               │
│                    │ (不持久化)   │                                       │
│                    └─────────────┘                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""
```

### 数据持久化策略

> **核心原则：原始数据必须持久化，索引数据可以重建**

```python
# ============================================================================
# 分层存储策略
# ============================================================================

class DataPersistenceStrategy:
    """数据持久化策略 - 分层设计"""
    
    """
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ 分层存储架构                                   │
    │                                                                         │
    │  ┌─────────────────────────────────────────────────────────────────┐   │
    │  │ Layer 1: 原始数据层 (真正持久化，不可丢失)                         │   │
    │  │                                                                 │   │
    │  │   • 原始文档文件 → 对象存储 (S3/MinIO)                           │   │
    │  │   • 解析后文本内容 → PostgreSQL TEXT字段 │   │
    │  │   • 用户配置/元数据 → PostgreSQL │   │
    │  │                                                                 │   │
    │  │   ★ 保留策略: FOREVER (永久) │   │
    │  │   ★ 备份策略: 多副本实时同步                                     │   │
    │  │   ★ 供应商锁定: 无 (标准化S3协议)                                 │   │
    │  └─────────────────────────────────────────────────────────────────┘   │
    │ │                                    │
    │                                    ▼ (可重建) │
    │  ┌─────────────────────────────────────────────────────────────────┐   │
    │  │ Layer 2: 索引数据层 (可重建，不要作为唯一数据源)                 │   │
    │  │                                                                 │   │
    │  │   • 向量索引 → 向量数据库 (Milvus/Qdrant/Pinecone)             │   │
    │  │   • 倒排索引 → Elasticsearch │   │
    │  │   • 全文索引 → Elasticsearch / PostgreSQL FTS │   │
    │  │                                                                 │   │
    │  │   ★ 保留策略: 按需 (重建成本低)                                  │   │
    │  │   ★ 备份策略: 可选 (重建成本低)                                  │   │
    │  │   ★ 供应商锁定: 有 (换供应商需重建)                             │   │
    │ └─────────────────────────────────────────────────────────────────┘   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """
    
    # 数据分类与存储
    STORAGE_CONFIG = {
        #核心数据 - Layer 1: 永久保留
        "user": {
            "layer": 1,
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "replication": ReplicationType.SYNC,
            "backup": BackupType.DAILY,
            "retention": RetentionPolicy.FOREVER
        },
        "agent_config": {
            "layer": 1,
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "replication": ReplicationType.SYNC,
            "backup": BackupType.DAILY,
            "retention": RetentionPolicy.FOREVER
        },
        "workflow_config": {
            "layer": 1,
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "replication": ReplicationType.SYNC,
            "backup": BackupType.DAILY,
            "retention": RetentionPolicy.FOREVER
        },
        
        # 知识库数据 - 分层存储
        "raw_document": {
            "layer": 1, # 原始文档真正持久化
            "storage": StorageType.OBJECT,
            "database": "s3_compatible",
            "replication": ReplicationType.SYNC,
            "backup": BackupType.REALTIME,
            "retention": RetentionPolicy.FOREVER
        },
        "parsed_content": {
            "layer": 1,                    # 解析后文本持久化
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "field_type": "TEXT", # 完整文本内容
            "replication": ReplicationType.SYNC,
            "backup": BackupType.DAILY,
            "retention": RetentionPolicy.FOREVER
        },
        "knowledge_metadata": {
            "layer": 1,
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "replication": ReplicationType.SYNC,
            "backup": BackupType.DAILY,
            "retention": RetentionPolicy.FOREVER
        },
        "vector_index": { # 向量索引只是索引
            "layer": 2,
            "storage": StorageType.VECTOR,
            "database": "milvus/qdrant/pinecone",
            "replication": ReplicationType.NONE,  # 向量数据库自己管理
            "backup": BackupType.NONE, # 不单独备份，可重建
            "retention": RetentionPolicy.REBUILDABLE
        },
        
        # 会话数据 - 用户控制
        "session": {
            "layer": 1,
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "replication": ReplicationType.ASYNC,
            "backup": BackupType.WEEKLY,
            "retention": RetentionPolicy.USER_CONTROLLED,
            "default_days": 90
        },
        "message": {
            "layer": 1,                    # 消息内容也持久化
            "storage": StorageType.PRIMARY,
            "database": "postgresql",
            "field_type": "TEXT",
            "replication": ReplicationType.NONE,
            "backup": BackupType.MONTHLY,
            "retention": RetentionPolicy.USER_CONTROLLED,
            "default_days": 30
        },
        "usage_log": {
            "layer": 1,
            "storage": StorageType.COLD,
            "database": "postgresql",
            "replication": ReplicationType.NONE,
            "backup": BackupType.MONTHLY,
            "retention": RetentionPolicy.COMPLIANCE,
            "min_days": 365
        }
    }


class VectorIndexRebuilder:
    """向量索引重建服务 - 当向量数据库出问题时的救星"""
    
    def __init__(
        self,
        document_store: DocumentStore,
        vector_db: VectorDatabase,
        embedding_service: EmbeddingService
    ):
        self.document_store = document_store
        self.vector_db = vector_db
        self.embedding_service = embedding_service
    
    async def rebuild_index(
        self,
        knowledge_base_id: str,
        progress_callback: Callable[[int, int], None] = None
    ) -> RebuildResult:
        """从原始数据重建向量索引"""
        
        # 1. 获取知识库
        kb = await self.get_knowledge_base(knowledge_base_id)
        
        # 2. 清理旧索引
        if kb.metadata.vector_index_id:
            await self.vector_db.delete_collection(kb.metadata.vector_index_id)
        
        # 3. 创建新索引
        new_collection = await self.vector_db.create_collection(
            name=f"kb_{knowledge_base_id}",
            dimension=self.embedding_service.get_dimension(kb.metadata.embedding_model),
            metric="cosine"
        )
        
        # 4. 遍历所有原始文档，重建向量
        documents = await self.document_store.get_parsed_documents(kb.id)
        total_chunks = 0
        processed = 0
        
        for doc in documents:
            # 分块
            chunks = self.chunker.chunk(doc.content, kb.metadata)
            
            # 生成向量
            embeddings = await self.embedding_service.embed_texts(
                [c.text for c in chunks],
                model=kb.metadata.embedding_model
            )
            
            #写入向量数据库
            await self.vector_db.insert(
                collection=new_collection,
                vectors=embeddings,
                metadatas=[c.metadata for c in chunks],
                ids=[c.id for c in chunks]
            )
            
            total_chunks += len(chunks)
            processed += 1
            
            if progress_callback:
                progress_callback(processed, len(documents))
        
        # 5. 更新元数据
        await self.update_knowledge_base_metadata(kb.id, {
            "vector_index_id": new_collection,
            "index_status": IndexStatus.COMPLETED,
            "last_indexed_at": datetime.now(),
            "total_chunks": total_chunks
        })
        
        return RebuildResult(
            success=True,
            knowledge_base_id=knowledge_base_id,
            total_documents=len(documents),
            total_chunks=total_chunks,
            duration_seconds=...
        )
    
    async def incremental_update(
        self,
        document_id: str,
        operation: str # "add" / "update" / "delete"
    ) -> IncrementalResult:
        """增量更新向量索引"""
        
        doc = await self.document_store.get_document(document_id)
        
        if operation == "delete":
            # 删除向量
            await self.vector_db.delete_by_metadata(
                {"document_id": document_id}
            )
        else:
            # 重新生成向量
            chunks = self.chunker.chunk(doc.content)
            embeddings = await self.embedding_service.embed_texts(
                [c.text for c in chunks]
            )
            
            if operation == "add":
                await self.vector_db.insert(...)
            else:  # update
                await self.vector_db.delete_by_metadata({"document_id": document_id})
                await self.vector_db.insert(...)
        
        return IncrementalResult(success=True)


class IndexRebuildTrigger:
    """索引重建触发器"""
    
    TRIGGERS = {
        # 向量数据库服务不可用
        "vector_db_unavailable": {
            "check": "health_check_failed",
            "action": "failover_to_backup",
            "timeout": 30 # 秒
        },
        
        # 索引数据损坏
        "index_corruption": {
            "check": "checksum_mismatch",
            "action": "rebuild_from_source",
            "timeout": 3600  # 1小时
        },
        
        # 供应商通知迁移
        "provider_migration": {
            "check": "migration_notice_received",
            "action": "preemptive_rebuild",
            "timeout": 86400  # 24小时
        },
        
        # 定期验证
        "periodic_validation": {
            "check": "daily_spot_check",
            "action": "validate_sample_vectors",
            "interval": 86400  # 每天
        }
    }
```

class DataExportService:
    """数据导出服务 - 用户数据主权"""
    
    async def export_user_data(
        self,
        user_id: str,
        format: ExportFormat  # json/csv/zip
    ) -> ExportResult:
        """导出用户所有数据"""
        data = {
            "user_profile": await self.get_user_profile(user_id),
            "agents": await self.get_user_agents(user_id),
            "workflows": await self.get_user_workflows(user_id),
            "knowledge_bases": await self.get_user_knowledge(user_id),
            "sessions": await self.get_user_sessions(user_id),
            "usage_stats": await self.get_user_usage(user_id)
        }
        
        # 打包导出
        return await self.package_export(data, format)
    
    async def import_user_data(
        self,
        user_id: str,
        import_file: UploadedFile
    ) -> ImportResult:
        """导入用户数据"""
        # 验证格式
        data = await self.parse_import_file(import_file)
        
        # 转换并导入
        await self.import_agents(user_id, data["agents"])
        await self.import_workflows(user_id, data["workflows"])
        await self.import_knowledge(user_id, data["knowledge_bases"])
        
        return ImportResult(success=True, items_imported=...)
    
    async def delete_user_data(
        self,
        user_id: str,
        scope: DeleteScope  # all/specific
    ) -> DeleteResult:
        """删除用户数据 - GDPR合规"""
        # 删除所有关联数据
        await self.db.users.delete(user_id)
        await self.db.agents.delete_many({"user_id": user_id})
        await self.db.sessions.delete_many({"user_id": user_id})
        # ... 其他数据
        
        return DeleteResult(completed_at=datetime.now())
```

### Agent适配器生命周期

```python
class AgentAdapterLifecycle:
    """Agent适配器生命周期管理"""
    
    def __init__(self, registry: AgentFrameworkRegistry):
        self.registry = registry
        self._active_adapters: dict[str, ExternalAgentAdapter] = {}
    
    def get_or_create_adapter(
        self,
        framework: AgentFramework,
        config: dict
    ) -> ExternalAgentAdapter:
        """获取或创建适配器实例"""
        adapter_key = f"{framework.value}:{hash_config(config)}"
        
        if adapter_key not in self._active_adapters:
            # 创建新实例
            adapter = self.registry.get_adapter(framework)
            if not adapter:
                raise AgentNotAvailableError(framework)
            
            self._active_adapters[adapter_key] = adapter
        
        return self._active_adapters[adapter_key]
    
    def swap_adapter(
        self,
        old_framework: AgentFramework,
        new_framework: AgentFramework,
        new_config: dict
    ):
        """热切换适配器 - 不影响已有数据"""
        # 1. 验证新适配器可用
        new_adapter = self.registry.get_adapter(new_framework)
        if not new_adapter:
            raise AgentNotAvailableError(new_framework)
        
        # 2. 切换（已有的AgentConfig等数据完全不变）
        logger.info(f"Swapping agent adapter: {old_framework} -> {new_framework}")
        
        # 3. 清理旧实例
        old_keys = [k for k in self._active_adapters 
                   if k.startswith(old_framework.value)]
        for key in old_keys:
            del self._active_adapters[key]
    
    def rollback_adapter(
        self,
        framework: AgentFramework,
        config: dict
    ):
        """回滚适配器版本"""
        # 适配器版本管理
        ...

class AgentMigrationService:
    """Agent迁移服务 - 支持跨适配器迁移"""
    
    async def migrate_agent(
        self,
        agent_id: str,
        from_adapter: AgentFramework,
        to_adapter: AgentFramework
    ) -> MigrationResult:
        """迁移智能体到新的Agent框架"""
        agent = await self.get_agent(agent_id)
        
        # 1. 验证目标适配器
        if not self.registry.get_adapter(to_adapter):
            raise MigrationError(f"Target adapter not available: {to_adapter}")
        
        # 2. 创建新版本配置
        new_config = await self.translate_config(
            agent.config,
            from_adapter,
            to_adapter
        )
        
        # 3. 更新配置（保持原有数据不变）
        agent.model_config = new_config
        agent.adapter_type = to_adapter.value
        agent.version += 1
        agent.version_history.append(AgentVersion(
            version=agent.version,
            adapter=to_adapter.value,
            migrated_at=datetime.now(),
            migrated_by="system"
        ))
        
        await self.save_agent(agent)
        
        return MigrationResult(
            success=True,
            old_adapter=from_adapter,
            new_adapter=to_adapter,
            data_preserved=True  # 关键：数据完整保留
        )
```

### 版本兼容性保障

```python
class VersionCompatibility:
    """版本兼容性管理"""
    
    CURRENT_VERSION = "2.0"
    
    # 版本迁移路径
    MIGRATION_PATHS = {
        "1.0": ["1.1", "1.2", "2.0"],
        "1.1": ["1.2", "2.0"],
        "1.2": ["2.0"],
    }
    
    async def migrate_if_needed(self, data: dict) -> dict:
        """必要时执行数据迁移"""
        current_version = data.get("version", "1.0")
        
        if current_version == self.CURRENT_VERSION:
            return data
        
        # 执行迁移
        migration_path = self.find_migration_path(current_version)
        for target_version in migration_path:
            data = await self.migrate_to(data, target_version)
        
        return data
    
    async def migrate_to(self, data: dict, target_version: str) -> dict:
        """迁移到指定版本"""
        migrator = getattr(self, f"migrate_to_{target_version.replace('.', '_')}", None)
        if migrator:
            return await migrator(data)
        return data
    
    async def rollback(self, data: dict, target_version: str) -> dict:
        """回滚到指定版本"""
        # 支持回滚，确保数据不丢失
        ...
```

### 数据隔离与安全

```python
class DataIsolation:
    """数据隔离保障"""
    
    async def verify_ownership(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str
    ) -> bool:
        """验证数据所有权"""
        resource = await self.get_resource(resource_type, resource_id)
        return resource.user_id == user_id
    
    async def list_user_accessible(
        self,
        user_id: str,
        resource_type: str
    ) -> list:
        """列出用户可访问的资源"""
        # 1. 自己创建的
        owned = await self.db[resource_type].find({"user_id": user_id})
        
        # 2. 公开分享的
        shared = await self.db[resource_type].find({
            "is_public": True,
            "tenant_id": await self.get_user_tenant(user_id)
        })
        
        # 3. 项目内共享的
        project_shared = await self.get_project_shared_resources(
            user_id, resource_type
        )
        
        return self.deduplicate([*owned, *shared, *project_shared])
    
    async def enforce_data_retention(
        self,
        tenant_id: str,
        resource_type: str,
        retention_days: int
    ):
        """执行数据保留策略"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # 删除过期数据
        deleted = await self.db[resource_type].delete_many({
            "tenant_id": tenant_id,
            "created_at": {"$lt": cutoff_date},
            "status": "archived"
        })
        
        logger.info(f"Deleted {deleted.count} expired {resource_type} records")
```

---

## 多容器/多项目隔离设计

### 层级关系

```
┌────────────────────────────────────────────────────────────────┐
│                         平台层 Platform                          │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    容器层 (Tenant)                         │  │
│  │                                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │  容器 A     │  │  容器 B     │  │  容器 C     │       │  │
│  │  │  研发中心   │  │  市场部     │  │  行政部     │       │  │
│  │  │            │  │            │  │            │       │  │
│  │  │ ┌─────────┐│  │ ┌─────────┐│  │ ┌─────────┐│       │  │
│  │  │ │项目 A1  ││  │ │项目 B1  ││  │ │项目 C1  ││       │  │
│  │  │ │项目 A2  ││  │ │项目 B2  ││  │ │项目 C2  ││       │  │
│  │  │ └─────────┘│  │ └─────────┘│  │ └─────────┘│       │  │
│  │  │            │  │            │  │            │       │  │
│  │  │ ┌─────────┐│  │            │  │            │       │  │
│  │  │ │共享知识 ││  │            │  │            │       │  │
│  │  │ └─────────┘│  │            │  │            │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    共享资源层                               │  │
│  │                                                          │  │
│  │  • 公共模型库（平台统一采购的模型）                        │  │
│  │  • 全局知识库（公司制度、流程文档）                        │  │
│  │  • 组织配置（角色、权限模板）                              │  │
│  │  • 审计日志（操作记录、合规审计）                          │  │
│  │  • 贡献排行（员工激励数据）                                │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 隔离策略

| 隔离维度 | 实现方式 | 说明 |
|----------|----------|------|
| **数据隔离** | 租户ID + 项目ID | 所有资源关联租户/项目ID |
| **模型隔离** | 租户级模型配置 | 不同租户可配置不同的AI提供商 |
| **配额隔离** | 租户级配额限制 | Token用量、存储空间等 |
| **权限隔离** | RBAC模型 | 租户管理员、项目管理员、普通用户 |
| **成本隔离** | 租户级计费 | 各容器独立核算AI使用成本 |
| **审计隔离** | 租户级日志 | 操作日志按租户隔离存储 |

### 数据模型关系

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Tenant    │────<│   Project   │────<│    User     │
│   (容器)    │     │   (项目)    │     │   (用户)    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Agent    │     │   Workflow  │     │  UserRole   │
│   (智能体)  │     │   (工作流)  │     │  (用户角色) │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  Knowledge  │     │   Tool      │
│   (知识库)  │     │   (工具)    │
└─────────────┘     └─────────────┘
```

---

## 员工激励机制设计

### 设计理念

让员工从"被动使用"转变为"主动贡献"，形成平台与员工的良性循环：

```
┌─────────────────────────────────────────────────────────────────┐
│                     员工激励飞轮                                  │
│                                                                  │
│      ┌──────────────┐                                           │
│      │   贡献者     │                                           │
│      │  Create     │                                           │
│      └──────┬───────┘                                           │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────────────┐                               │
│  │                             │                               │
│  │  发布到平台  Publish        │                               │
│  │                             │                               │
│  └─────────────────────────────┘                               │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────────────┐                               │
│  │                             │                               │
│  │  被其他人使用  Use          │                               │
│  │                             │                               │
│  └─────────────────────────────┘                               │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────────────┐                               │
│  │                             │                               │
│  │  获得认可  Like/Favorite    │                               │
│  │                             │                               │
│  └─────────────────────────────┘                               │
│             │                                                   │
│             ▼                                                   │
│      ┌──────────────┐                                           │
│      │   积分奖励   │                                           │
│      │   Score     │                                           │
│      └──────┬───────┘                                           │
│             │                                                   │
│             ▼                                                   │
│      ┌──────────────┐                                           │
│      │   更多激励   │                                           │
│      │   More      │                                           │
│      └──────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 贡献积分系统

```python
@dataclass
class UserContribution:
    """用户贡献统计"""
    user_id: str
    tenant_id: str
    
    # 贡献数量
    agent_count: int = 0
    workflow_count: int = 0
    knowledge_count: int = 0
    plugin_count: int = 0
    
    # 被认可情况
    likes_received: int = 0
    uses_received: int = 0
    favorites_received: int = 0
    reviews_count: int = 0
    
    # 综合评分
    total_score: int = 0
    
    # 徽章
    badges: list[str] = field(default_factory=list)


class ContributionTracker:
    """贡献追踪器"""
    
    # 积分规则
    POINTS = {
        # 创建贡献
        "create_agent": 10,
        "create_workflow": 15,
        "create_knowledge": 5,
        "create_plugin": 20,
        
        # 被认可
        "receive_like": 1,
        "receive_use": 2,
        "receive_favorite": 3,
        "receive_review": 5,
        
        # 被评为优质
        "featured_by_admin": 50,
        
        # 排行榜
        "weekly_top_agent": 50,
        "monthly_best": 100,
        
        # 持续贡献
        "streak_7_days": 30,
        "streak_30_days": 100,
    }
    
    def record(self, user_id: str, action: str, target_id: str):
        """记录贡献行为"""
        points = self.POINTS.get(action, 0)
        self.db.contribution_records.insert({
            "user_id": user_id,
            "action": action,
            "target_id": target_id,
            "points": points,
            "created_at": datetime.now()
        })
        self._update_user_score(user_id)
    
    def _update_user_score(self, user_id: str):
        """更新用户总分"""
        total = self.db.contribution_records.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$user_id", "total": {"$sum": "$points"}}}
        ])
        self.db.users.update_one(
            {"_id": user_id},
            {"$set": {"contribution_score": total}}
        )
    
    def leaderboard(
        self, 
        tenant_id: str, 
        period: str = "monthly",
        limit: int = 10
    ) -> list[UserContribution]:
        """贡献排行榜"""
        start_date = self._get_period_start(period)
        
        pipeline = [
            {"$match": {
                "tenant_id": tenant_id,
                "created_at": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$user_id",
                "total_score": {"$sum": "$points"}
            }},
            {"$sort": {"total_score": -1}},
            {"$limit": limit}
        ]
        
        return list(self.db.contribution_records.aggregate(pipeline))
```

### 徽章系统

```python
# 徽章定义
BADGES = {
    "first_agent": {
        "name": "初露锋芒",
        "description": "创建了第一个智能体",
        "icon": "🌟",
        "condition": lambda u: u.agent_count >= 1
    },
    "agent_master": {
        "name": "智能体大师",
        "description": "创建了10个智能体",
        "icon": "🏆",
        "condition": lambda u: u.agent_count >= 10
    },
    "workflow_expert": {
        "name": "工作流专家",
        "description": "创建了5个工作流",
        "icon": "⚙️",
        "condition": lambda u: u.workflow_count >= 5
    },
    "knowledge_curator": {
        "name": "知识守护者",
        "description": "贡献了100条知识",
        "icon": "📚",
        "condition": lambda u: u.knowledge_count >= 100
    },
    "popular_creator": {
        "name": "人气创作者",
        "description": "累计获得100个赞",
        "icon": "❤️",
        "condition": lambda u: u.likes_received >= 100
    },
    "top_contributor": {
        "name": "月度之星",
        "description": "本月贡献排行第一",
        "icon": "🌙",
        "condition": lambda u: u.is_monthly_top
    },
    "streak_master": {
        "name": "坚持达人",
        "description": "连续30天有贡献",
        "icon": "🔥",
        "condition": lambda u: u.streak_days >= 30
    }
}
```

---

## 技术栈选型

### 推荐技术栈

| 层级 | 推荐技术 | 说明 |
|------|----------|------|
| **API Gateway** | Kong / Traefik | 高性能网关，支持插件扩展 |
| **后端框架** | FastAPI / Go | 异步高性能，类型安全 |
| **数据库** | PostgreSQL + Redis | 主数据存储 + 缓存 |
| **消息队列** | Kafka / RabbitMQ | 工作流异步处理 |
| **向量数据库** | Qdrant / Milvus | 知识库向量检索 |
| **全文搜索** | Elasticsearch | 知识库全文检索 |
| **容器编排** | Kubernetes | 多容器隔离 |
| **前端** | React + Ant Design | 管理控制台 |
| **工作流引擎** | Temporal / Prefect | 工作流编排 |

### 技术选型考量

#### 1. 后端框架对比

| 框架 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| **FastAPI** | 异步、类型安全、自动文档 | 运行时性能略低 | 快速迭代、中小型规模 |
| **Go** | 高性能、并发强、部署简单 | 生态较新、泛型支持弱 | 高并发、大规模场景 |
| **Python** | AI生态丰富、开发快 | GIL限制、性能一般 | AI集成优先的场景 |

#### 2. 工作流引擎对比

| 引擎 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| **Temporal** | 强大的持久化、可观测 | 学习曲线陡、资源占用高 | 复杂长时任务 |
| **Prefect** | Python原生、简洁 | 分布式能力较弱 | Python团队、简单流程 |
| **自研** | 完全可控、定制灵活 | 开发维护成本高 | 有特殊需求的场景 |

---

## 实施路线图

### 总体规划

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           实施路线图 Roadmap                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1          Phase 2          Phase 3          Phase 4                │
│  核心搭建          功能完善          生态建设          高级特性              │
│  8-10周           8-10周           8-10周           8-10周                 │
│                                                                             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐                │
│  │ MVP发布 │     │ 正式版  │     │ 平台化  │     │ 智能化  │                │
│  │  V1.0   │────▶│  V2.0   │────▶│  V3.0   │────▶│  V4.0   │                │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: 核心搭建（8-10周）

#### 目标
搭建平台基础骨架，实现最小可用产品。

#### 里程碑
- [ ] 用户注册、登录、认证
- [ ] 基础用户管理（CRUD、角色）
- [ ] 单容器支持
- [ ] 至少2个AI适配器（OpenAI + 1个国产模型）
- [ ] 基础的智能体创建界面
- [ ] 简单的对话功能

#### 详细任务分解

**Week 1-2: 项目初始化**
```
□ 项目结构搭建
  ├── backend/           # 后端代码
  │   ├── app/
  │   ├── core/
  │   └── api/
  ├── frontend/          # 前端代码
  │   ├── src/
  │   └── public/
  ├── infra/             # 基础设施
  │   ├── docker/
  │   └── k8s/
  └── docs/              # 文档
□ 技术选型确认
□ 开发环境搭建
□ 代码规范制定
□ Git流程确定
```

**Week 3-4: 核心服务**
```
□ 数据库设计
  ├── users
  ├── tenants
  ├── projects
  ├── roles
  └── permissions
□ 用户认证模块
  ├── JWT实现
  ├── 登录/登出
  └── 刷新Token
□ 用户管理API
  ├── CRUD接口
  ├── 角色分配
  └── 权限校验
□ 容器管理API
  ├── 创建容器
  └── 配额管理
```

**Week 5-6: 集成层**
```
□ AI Provider接口定义
□ OpenAI适配器实现
□ 国产模型适配器实现（智谱/通义）
□ 适配器注册中心
□ 统一调用入口
□ 模型路由基础功能
```

**Week 7-8: 智能体基础**
```
□ 智能体数据模型
□ 智能体CRUD API
□ 基础对话API
□ 会话管理
□ 简单的管理界面
```

**Week 9-10: 集成测试**
```
□ 端到端测试
□ 性能测试
□ 安全测试
□ 文档完善
□ MVP发布
```

#### Phase 1 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| 用户认证系统 | 完整的注册登录流程 | 支持邮箱/手机登录 |
| 用户管理 | 增删改查用户 | 支持角色分配 |
| 单容器支持 | 基础的多租户隔离 | 数据隔离验证 |
| 2个AI适配器 | OpenAI + 国产模型 | 可切换调用 |
| 智能体创建 | 创建和管理智能体 | 可配置提示词和模型 |
| 基础对话 | 与智能体对话 | 支持多轮对话 |

---

### Phase 2: 功能完善（8-10周）

#### 目标
完善核心功能，增加项目管理、知识库、工作流。

#### 里程碑
- [ ] 多容器支持
- [ ] 项目管理
- [ ] 知识库管理
- [ ] 工作流基础
- [ ] 工具系统
- [ ] 贡献激励基础

#### 详细任务分解

**Week 11-12: 多容器与项目**
```
□ 容器管理完善
  ├── 配额系统
  ├── 容器配置
  └── 容器监控
□ 项目管理
  ├── 项目CRUD
  ├── 项目成员管理
  └── 项目级配置
□ RBAC权限完善
  ├── 权限矩阵
  ├── 资源级权限
  └── 审计日志
```

**Week 13-14: 知识库**
```
□ 知识库模型设计
□ 文档上传与解析
  ├── PDF解析
  ├── Word解析
  └── Markdown解析
□ 向量化处理
□ 知识检索API
□ 知识库管理界面
```

**Week 15-16: 工作流引擎**
```
□ 工作流数据模型
□ 可视化编辑器
  ├── 节点拖拽
  ├── 连线绘制
  └── 属性配置
□ 工作流执行引擎
  ├── 节点执行
  ├── 条件分支
  └── 异常处理
□ 工作流API
□ 工作流执行监控
```

**Week 17-18: 工具系统**
```
□ 工具接口定义
□ 内置工具实现
  ├── 网络搜索
  ├── 计算器
  ├── 代码执行
  └── 文档处理
□ 工具注册中心
□ 工具管理界面
□ 智能体工具配置
```

**Week 19-20: 贡献激励**
```
□ 贡献积分系统
□ 贡献记录追踪
□ 排行榜API
□ 徽章系统
□ 激励展示界面
```

#### Phase 2 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| 多容器支持 | 完整的租户隔离 | 配额、配置、监控 |
| 项目管理 | 项目级资源隔离 | 成员管理、权限控制 |
| 知识库 | 文档管理和检索 | 支持多种格式、支持向量检索 |
| 工作流引擎 | 可视化流程编排 | 拖拽设计、循环、条件分支 |
| 工具系统 | 扩展工具能力 | 内置5+工具、支持自定义 |
| 贡献激励 | 积分和徽章 | 积分记录、排行榜、徽章展示 |

---

### Phase 3: 生态建设（8-10周）

#### 目标
构建开放生态，支持插件市场、员工分享。

#### 里程碑
- [ ] 插件市场
- [ ] 模板中心
- [ ] 分享机制
- [ ] 评论系统
- [ ] API开放平台
- [ ] 第三方集成

#### 详细任务分解

**Week 21-22: 插件市场**
```
□ 插件数据模型
□ 插件上传与审核
□ 插件发现与搜索
□ 插件安装/卸载
□ 插件市场界面
□ 插件评分与评论
```

**Week 23-24: 模板中心**
```
□ 模板市场设计
□ 预置模板开发
  ├── 客服机器人模板
  ├── 代码审查模板
  ├── 报表生成模板
  └── 内容创作模板
□ 模板分类与推荐
□ 模板一键使用
```

**Week 25-26: 分享机制**
```
□ 分享流程设计
□ 公开/私有切换
□ 分享权限控制
□ 分享记录追踪
□ 分享效果统计
□ 热门内容推荐
```

**Week 27-28: API开放平台**
```
□ API文档自动生成
□ API密钥管理
□ API调用监控
□ 速率限制
□ SDK自动生成
□ 开发者门户
```

**Week 29-30: 高级特性**
```
□ 批量导入导出
□ 智能体版本管理
□ A/B测试支持
□ 实验追踪
□ 效果分析
□ 优化建议
```

#### Phase 3 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| 插件市场 | 开放的插件生态 | 支持第三方插件、审核流程 |
| 模板中心 | 预置和社区模板 | 10+预置模板、一键使用 |
| 分享机制 | 智能体和工作流分享 | 公开/私有、权限控制 |
| API开放平台 | 第三方集成能力 | 完整API、SDK、文档 |
| 开发者门户 | 开发者资源中心 | 文档、示例、社区 |

---

### Phase 4: 高级特性（8-10周）

#### 目标
实现高级AI能力，提升平台智能化水平。

#### 里程碑
- [ ] 智能模型路由
- [ ] 多模态支持
- [ ] Agent协作
- [ ] 自定义训练
- [ ] 企业级安全
- [ ] 高可用部署

#### 详细任务分解

**Week 31-32: 智能路由**
```
□ 模型评估体系
□ 任务分类器
□ 智能路由策略
  ├── 成本优先
  ├── 速度优先
  └── 质量优先
□ 动态模型切换
□ 路由效果追踪
□ 成本优化建议
```

**Week 33-34: 多模态**
```
□ 图像理解支持
□ 语音合成/识别
□ 视频理解
□ 多模态智能体
□ 多模态工作流
□ 跨模态检索
```

**Week 35-36: Agent协作**
```
□ 多Agent通信协议
□ Agent协作工作流
□ Agent角色分配
□ 协作状态管理
□ 协作效果评估
□ 协作模板市场
```

**Week 37-38: 自定义训练**
```
□ Fine-tuning平台
□ 数据集管理
□ 训练任务管理
□ 模型评估
□ 模型发布
□ 成本控制
```

**Week 39-40: 企业级特性**
```
□ SSO集成
  ├── SAML
  ├── OIDC
  └── LDAP
□ 合规审计
□ 数据加密
□ 私有化部署
□ 高可用架构
□ 灾备方案
```

#### Phase 4 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| 智能路由 | 自动选择最优模型 | 支持多种策略、成本降低30%+ |
| 多模态 | 图像/语音/视频支持 | 全模态覆盖 |
| Agent协作 | 多智能体协作 | 通信协议、协作模板 |
| 自定义训练 | Fine-tuning能力 | 支持主流模型、数据闭环 |
| 企业级安全 | 完整的企业安全 | SSO、审计、私有化 |

---

### 资源规划

#### 团队规模建议

| 阶段 | 后端 | 前端 | DevOps | 产品 | 测试 | 总计 |
|------|------|------|--------|------|------|------|
| Phase 1 | 2-3 | 1-2 | 1 | 1 | 1 | 6-8 |
| Phase 2 | 2-3 | 1-2 | 1 | 1 | 1 | 6-8 |
| Phase 3 | 1-2 | 1-2 | 1 | 1 | 1 | 5-7 |
| Phase 4 | 1-2 | 1 | 1 | 1 | 1 | 5-6 |

#### 基础设施估算

| 资源 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|
| 云服务器 | 4-8核 | 8-16核 | 16-32核 | 32-64核 |
| 数据库 | 100GB | 500GB | 1TB | 2TB+ |
| 向量数据库 | - | 100GB | 500GB | 1TB+ |
| API调用量 | 10万/月 | 100万/月 | 500万/月 | 1000万+/月 |

---

## 开发路线图

### 整体规划

> **核心原则：小步快跑，先跑通核心，再迭代完善**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         开发路线图                                        │
│                                                                         │
│   Phase 1 (MVP)     Phase 2 (完善)     Phase 3 (扩展)     Phase 4 (企业级) │
│   ───────────       ───────────       ───────────       ─────────────    │
│   核心框架          智能体支持         生态建设           企业级安全       │
│   2-3个月           3-4个月           3-4个月           2-3个月           │
│                                                                         │
│   └─────────────────┴─────────────────┴─────────────────┴────────────►  │
│                                                                         │
│   2025 Q1           2025 Q2           2025 Q3           2025 Q4        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: MVP (Month 1-3)

#### 目标
> **跑通核心流程：用户 → 创建Agent → 调用 → 持久化数据**

#### 核心功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 用户管理 | P0 | 注册、登录、角色、权限 |
| 容器管理 | P0 | 多容器隔离、配额管理 |
| 项目管理 | P0 | 多项目、成员管理 |
| Agent创建 | P0 | 基础配置、模型选择 |
| Agent对话 | P0 | 基础对话能力 |
| 数据持久化 | P0 | PostgreSQL存储 |
| 适配器框架 | P0 | OpenAI/Claude适配器 |

#### 技术债务

| 内容 | 说明 |
|------|------|
| 用户认证 | JWT / OAuth2 |
| 基础监控 | 日志、错误追踪 |
| 基础测试 | 单元测试覆盖 |

#### Phase 1 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Phase 1 MVP 架构                                    │
│                                                                         │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                          │
│   │   Web   │     │   API   │     │   CLI   │                          │
│   └────┬────┘     └────┬────┘     └────┬────┘                          │
│        │              │              │                                 │
│        └──────────────┼──────────────┘                                 │
│                       ▼                                                 │
│              ┌─────────────────┐                                       │
│              │   业务逻辑层     │                                       │
│              │  • 用户管理      │                                       │
│              │  • 容器管理      │                                       │
│              │  • Agent对话     │                                       │
│              └────────┬─────────┘                                       │
│                       │                                                 │
│        ┌──────────────┼──────────────┐                                  │
│        ▼              ▼              ▼                                  │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐                              │
│   │   PG    │   │  适配器  │   │  Agent  │                              │
│   │  用户   │   │  框架   │   │ Runtime │                              │
│   │  配置   │   │         │   │         │                              │
│   └─────────┘   └─────────┘   └─────────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Phase 1 验收标准

- ✅ 用户可以注册、登录
- ✅ 可以创建容器和项目
- ✅ 可以创建Agent并配置模型
- ✅ 可以与Agent对话
- ✅ 对话历史可以持久化存储
- ✅ 支持 OpenAI / Claude 模型
- ✅ 基础测试覆盖

#### Phase 1 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| 用户系统 | 注册/登录/角色 | 3种角色、RBAC权限 |
| 容器管理 | 多容器隔离 | 容器创建、配额限制 |
| Agent对话 | 基础对话 | 流畅对话、持久化 |
| 适配器框架 | 模型接入 | 2个以上适配器 |

---

### Phase 2: 智能体支持 (Month 4-7)

#### 目标
> **扩展Agent能力：支持工具、知识库、工作流**

#### 核心功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| Agent工具 | P0 | 工具注册、调用 |
| 知识库RAG | P0 | 文档上传、向量检索 |
| 工作流 | P1 | 基础编排能力 |
| 会话管理 | P0 | 多会话、上下文 |
| MCP支持 | P1 | MCP协议桥接 |

#### Phase 2 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Phase 2 智能体架构                                   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      业务应用层                                  │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│   │  │Agent管理│  │知识库   │  │工作流   │  │会话管理 │           │   │
│   │  │ +工具   │  │ RAG    │  │编排    │  │上下文   │           │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    编排调度层                                     │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│   │  │ Agent   │  │ Workflow│  │  Task   │  │  MCP    │           │   │
│   │  │ Runtime │  │ Engine  │  │Scheduler│  │ Bridge  │           │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      数据层                                        │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│   │  │   PG    │  │对象存储│  │向量数据库│  │ 搜索   │           │   │
│   │  │ 配置+会话│  │ 文档   │  │  RAG   │  │ 增强   │           │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Phase 2 验收标准

- ✅ Agent可以使用多种工具
- ✅ 可以上传文档构建知识库
- ✅ 可以实现RAG增强对话
- ✅ 可以设计简单工作流
- ✅ 支持MCP协议

#### Phase 2 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| Agent工具 | 多工具支持 | 5种以上内置工具 |
| 知识库RAG | 文档检索 | 支持PDF/Word/MD |
| 工作流 | 可视化编排 | 基础节点类型 |
| MCP支持 | 协议桥接 | GitHub/FS工具 |

---

### Phase 3: 生态建设 (Month 8-11)

#### 目标
> **开放生态：插件市场、员工激励、协作分享**

#### 核心功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 插件市场 | P0 | 发布、发现、安装插件 |
| 智能体市场 | P0 | 分享、发现、使用Agent |
| 员工激励 | P0 | 积分、徽章、排行榜 |
| 工作流模板 | P1 | 模板市场、模板创建 |
| 团队协作 | P1 | 共享、评论、版本控制 |

#### Phase 3 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Phase 3 生态架构                                    │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      用户层                                       │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│   │  │ 创建者  │  │ 使用者  │  │ 贡献者  │  │ 评审者  │           │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      市场层                                       │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│   │  │Agent市场│  │插件市场│  │模板市场│  │知识市场│           │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    激励层                                         │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │   │
│   │  │  积分   │  │  徽章   │  │  排行   │  │  成就   │           │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Phase 3 验收标准

- ✅ 可以发布Agent到市场
- ✅ 可以发布插件到市场
- ✅ 有完整的积分激励系统
- ✅ 有排行榜和徽章系统
- ✅ 支持工作流模板分享

#### Phase 3 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| Agent市场 | 分享发现Agent | 搜索、评分、评论 |
| 插件市场 | 插件生态 | 发布、审核、安装 |
| 激励机制 | 积分徽章 | 积分系统、徽章墙 |
| 工作流模板 | 模板市场 | 模板创建、分享 |

---

### Phase 4: 企业级安全 (Month 12-14)

#### 目标
> **企业级能力：安全、合规、可观测**

#### 核心功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| SSO/LDAP | P0 | 企业身份集成 |
| 审计日志 | P0 | 完整操作记录 |
| 数据加密 | P0 | 传输/存储加密 |
| 私有化部署 | P1 | 离线部署支持 |
| 高可用 | P1 | 集群、灾备 |

#### Phase 4 验收标准

- ✅ 支持SSO/LDAP
- ✅ 完整审计日志
- ✅ 数据加密
- ✅ 可私有化部署
- ✅ 高可用保障

#### Phase 4 交付物

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| SSO集成 | 企业身份 | SAML/OIDC/LDAP |
| 审计日志 | 合规要求 | 操作记录、查询 |
| 私有部署 | 离线方案 | Docker/K8s部署 |
| 高可用 | 99.9%可用 | 集群、灾备 |

---

### 开发优先级矩阵

```
                        高影响
                          ▲
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          │    快速胜利    │    主要目标    │
          │   (Quick Win)  │  (Big Bet)    │
          │               │               │
  低优先级┼───────────────┼───────────────┼高优先级
          │               │               │
          │    后缓       │    策略性      │
          │   (Later)     │ (Strategic)   │
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                        低影响
```

| 象限 | 内容 | 策略 |
|------|------|------|
| 快速胜利 | 基础功能、核心持久化 | 优先做，低成本高回报 |
| 主要目标 | Agent能力、知识库 | Phase 1-2重点 |
| 策略性 | 生态建设、企业安全 | Phase 3-4重点 |
| 后缓 | 高级特性、实验功能 | 按需安排 |

---

## 风险与应对

### 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| AI模型不稳定 | 高 | 高 | 多模型冗余、降级策略 |
| 适配器接口变化 | 中 | 中 | 版本隔离、接口适配层 |
| 性能瓶颈 | 中 | 中 | 提前压测、缓存策略 |
| 安全漏洞 | 低 | 高 | 安全审计、渗透测试 |

### 业务风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 员工参与度低 | 中 | 中 | 激励机制优化、引导运营 |
| 需求变更频繁 | 高 | 中 | 敏捷开发、迭代交付 |
| 成本超支 | 中 | 高 | 配额管理、成本监控 |
| 合规风险 | 低 | 高 | 法务介入、定期审计 |

### 应对策略

1. **技术风险应对**
   - 建立模型抽象层，隔离底层变化
   - 实现降级策略，保证核心功能可用
   - 持续性能监控，及时发现瓶颈

2. **业务风险应对**
   - 设计简洁的激励机制，降低参与门槛
   - 采用敏捷开发，快速响应需求
   - 建立成本预警机制
   - 提前介入合规审查

---

## 总结

### 核心设计思想

> **"数据是资产，必须持久化；Agent是工具，可以随时替换"**

```
┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│    ┌────────────────────────────────────────────────────────┐   │
│    │                    稳定核心                              │   │
│    │   用户管理 · 权限控制 · 容器/项目管理 · 审计日志         │   │
│    │   Layer 1 持久化 · PostgreSQL + 对象存储                 │   │
│    └────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│    ┌────────────────────────────────────────────────────────┐   │
│    │                    灵活边缘                              │   │
│    │   AI模型 · 工具能力 · 插件生态 · 工作流节点              │   │
│    │   Layer 2 索引 · Layer 3 Agent · Layer 4 模型           │   │
│    └────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│    ┌────────────────────────────────────────────────────────┐   │
│    │                    社区参与                               │   │
│    │   智能体分享 · 工作流模板 · 知识贡献 · 激励机制          │   │
│    └────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 三个"不怕"

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   不怕换模型         不怕换Agent        不怕换向量数据库                 │
│   ─────────         ─────────         ──────────────                     │
│   适配器模式         注册中心           索引重建服务                     │
│   接口不变           热插拔             从Layer 1重建                     │
│                                                                         │
│   配置在DB           配置在DB           原文在PostgreSQL                 │
│   模型随便换         Agent随便换        向量随便换                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 开发路线图

| 阶段 | 时间 | 目标 | 交付物 |
|------|------|------|--------|
| Phase 1 | 1-3月 | MVP核心框架 | 用户系统、Agent对话、持久化 |
| Phase 2 | 4-7月 | 智能体支持 | 工具、知识库RAG、工作流 |
| Phase 3 | 8-11月 | 生态建设 | 市场、激励、协作 |
| Phase 4 | 12-14月 | 企业级安全 | SSO、审计、私有部署 |

### 架构优势

| 优势 | 说明 |
|------|------|
| **快速扩展** | 新模型接入只需实现适配器，1-2天完成 |
| **灵活隔离** | 容器/项目多级隔离，满足各种组织需求 |
| **员工激励** | 贡献可见、积分排行、徽章荣誉 |
| **成本可控** | 租户级配额和计费，避免资源浪费 |
| **持续演进** | 插件市场、生态共建，平台不断丰富 |
| **数据安全** | Layer 1 永久保留，不因技术迭代丢失 |

### 关键成功因素

1. **核心理念要坚守** - "数据是资产，Agent是工具"贯穿始终
2. **接口设计要稳定** - 核心接口设计好后尽量不变
3. **激励机制要简单** - 门槛低、反馈及时、荣誉可见
4. **扩展机制要开放** - 让员工和第三方都能贡献
5. **迭代节奏要快** - 小步快跑、快速验证、及时调整

---

*"AI的世界变化很快，但好的架构设计可以让你的平台从容应对这些变化。数据是唯一不变的资产，Agent只是工具。"*

*本文档持续更新中，欢迎提出建议和讨论。*