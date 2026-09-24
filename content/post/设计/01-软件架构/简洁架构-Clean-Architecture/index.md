---
title: 简洁架构（Clean Architecture）：让业务逻辑永远不依赖框架
description: "深入解析 Uncle Bob 提出的简洁架构（Clean Architecture），从同心圆模型、依赖规则到 Python 完整落地示例。"
date: 2026-04-12T11:00:00+08:00
image: images/index/index.png
categories:
    - Design
tags:
    - 软件架构设计
draft: false
---

## 什么是简洁架构？

简洁架构（Clean Architecture）由 Robert C. Martin（Uncle Bob）在 2012 年提出，它并非一个新概念，而是对**六边形架构**、**洋葱架构**、**BCE 架构**等多种架构思想的统一与提炼。

**核心目标只有一个**：让系统中最重要的部分——**业务规则（Business Rules）**——与框架、数据库、UI 完全解耦，使其可以独立测试、独立替换。

---

## 同心圆模型

简洁架构的标志性图示是四个同心圆，从内到外依次是：

```
        ┌─────────────────────────────────────────┐
        │          Frameworks & Drivers            │  ← 最外层：Web框架、DB、UI
        │   ┌─────────────────────────────────┐   │
        │   │      Interface Adapters          │   │  ← 控制器、网关、Presenter
        │   │   ┌─────────────────────────┐   │   │
        │   │   │    Application Business  │   │   │  ← Use Cases（用例）
        │   │   │         Rules           │   │   │
        │   │   │   ┌─────────────────┐   │   │   │
        │   │   │   │  Enterprise     │   │   │   │  ← Entities（实体/领域对象）
        │   │   │   │  Business Rules │   │   │   │
        │   │   │   └─────────────────┘   │   │   │
        │   │   └─────────────────────────┘   │   │
        │   └─────────────────────────────────┘   │
        └─────────────────────────────────────────┘
```

```mermaid
graph LR
    classDef entity fill:#e8f5e9,stroke:#43a047,color:#000
    classDef usecase fill:#e3f2fd,stroke:#1e88e5,color:#000
    classDef adapter fill:#fff3e0,stroke:#fb8c00,color:#000
    classDef framework fill:#fce4ec,stroke:#d81b60,color:#000

    subgraph L4 [Frameworks & Drivers]
        FastAPI[FastAPI / Flask]
        MySQL[(MySQL / PostgreSQL)]
        Redis[(Redis)]
    end

    subgraph L3 [Interface Adapters]
        Controller[Controller 控制器]
        Presenter[Presenter 输出格式化]
        Gateway[Repository Gateway]
    end

    subgraph L2 [Application Business Rules]
        UC1[UseCase: CreateOrder]
        UC2[UseCase: CancelOrder]
        UC3[UseCase: QueryOrder]
    end

    subgraph L1 [Enterprise Business Rules]
        Order[Order 实体]
        OrderItem[OrderItem 值对象]
        IOrderRepo[IOrderRepository 接口]
    end

    FastAPI --> Controller
    Controller --> UC1
    UC1 --> Order
    UC1 --> IOrderRepo
    Gateway -->|实现| IOrderRepo
    MySQL --> Gateway

    class Order,OrderItem,IOrderRepo entity
    class UC1,UC2,UC3 usecase
    class Controller,Presenter,Gateway adapter
    class FastAPI,MySQL,Redis framework
```

---

## 核心原则：依赖规则（The Dependency Rule）

> **源代码依赖只能从外向内指向。内层对外层一无所知。**

这条规则是简洁架构的灵魂：

| 层级 | 可以依赖 | 不可以依赖 |
|------|----------|------------|
| Entities（实体） | 无任何外部依赖 | 全部外层 |
| Use Cases（用例） | Entities | Adapters、Frameworks |
| Adapters（适配器） | Use Cases、Entities | Frameworks（直接耦合） |
| Frameworks（框架） | 全部内层 | — |

**实际含义举例**：

- `Order` 实体类里，不能出现 `import sqlalchemy`
- `CreateOrderUseCase` 里，不能出现 `import fastapi`
- 数据库从 MySQL 换成 MongoDB，只需修改最外层的 Repository 实现，业务逻辑零改动

---

## 四层详解

### 第一层：Entities（企业业务规则）

实体封装了最核心、最稳定的业务规则，它们与任何应用无关，只表达"这个领域的事物是什么"。

```python
# entities/order.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    customer_id: UUID
    items: List[OrderItem] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"只有 PENDING 状态的订单才能确认，当前状态: {self.status}")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status == OrderStatus.CANCELLED:
            raise ValueError("订单已经取消")
        self.status = OrderStatus.CANCELLED
```

> **注意**：这里没有任何 `import` 涉及框架或数据库。实体是纯 Python 对象，可以独立测试。

---

### 第二层：Use Cases（应用业务规则）

用例编排实体的业务行为，代表"系统能做什么"。它通过**接口（抽象）**与外部世界交互，而不直接依赖具体实现。

```python
# use_cases/interfaces.py  （定义抽象接口，属于内层）
from abc import ABC, abstractmethod
from uuid import UUID
from entities.order import Order


class IOrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...


class IPaymentGateway(ABC):
    @abstractmethod
    def charge(self, customer_id: UUID, amount: float) -> bool: ...


class INotificationService(ABC):
    @abstractmethod
    def send_confirmation(self, order: Order) -> None: ...
```

```python
# use_cases/create_order.py
from dataclasses import dataclass
from uuid import UUID
from entities.order import Order, OrderItem
from use_cases.interfaces import IOrderRepository, IPaymentGateway, INotificationService


@dataclass
class CreateOrderRequest:
    customer_id: UUID
    items: list[dict]  # [{product_id, product_name, quantity, unit_price}]


@dataclass
class CreateOrderResponse:
    order_id: UUID
    total_amount: float
    status: str


class CreateOrderUseCase:
    def __init__(
        self,
        order_repo: IOrderRepository,
        payment_gateway: IPaymentGateway,
        notification_service: INotificationService,
    ):
        self._order_repo = order_repo
        self._payment = payment_gateway
        self._notification = notification_service

    def execute(self, request: CreateOrderRequest) -> CreateOrderResponse:
        # 1. 创建领域对象
        order = Order(customer_id=request.customer_id)
        for item_data in request.items:
            order.items.append(OrderItem(**item_data))

        # 2. 执行支付（通过接口，不关心底层是支付宝还是微信）
        success = self._payment.charge(request.customer_id, order.total_amount)
        if not success:
            raise ValueError("支付失败，请检查账户余额")

        # 3. 确认订单（领域规则在实体内部）
        order.confirm()

        # 4. 持久化
        self._order_repo.save(order)

        # 5. 发送通知
        self._notification.send_confirmation(order)

        return CreateOrderResponse(
            order_id=order.id,
            total_amount=order.total_amount,
            status=order.status.value,
        )
```

---

### 第三层：Interface Adapters（接口适配器）

这一层负责在"用例的数据格式"和"外部世界的数据格式"之间做转换。

```python
# adapters/repositories/sql_order_repository.py
from uuid import UUID
from sqlalchemy.orm import Session
from entities.order import Order, OrderItem, OrderStatus
from use_cases.interfaces import IOrderRepository
from adapters.models import OrderORM, OrderItemORM  # ORM 模型定义在此层


class SqlOrderRepository(IOrderRepository):
    """将 IOrderRepository 接口适配到 SQLAlchemy 实现"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        orm = OrderORM(
            id=str(order.id),
            customer_id=str(order.customer_id),
            status=order.status.value,
            created_at=order.created_at,
        )
        for item in order.items:
            orm.items.append(OrderItemORM(
                product_id=str(item.product_id),
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            ))
        self._session.merge(orm)
        self._session.commit()

    def find_by_id(self, order_id: UUID) -> Order | None:
        orm = self._session.get(OrderORM, str(order_id))
        if not orm:
            return None
        return self._orm_to_entity(orm)

    def _orm_to_entity(self, orm: OrderORM) -> Order:
        order = Order(customer_id=UUID(orm.customer_id))
        order.id = UUID(orm.id)
        order.status = OrderStatus(orm.status)
        order.created_at = orm.created_at
        for item_orm in orm.items:
            order.items.append(OrderItem(
                product_id=UUID(item_orm.product_id),
                product_name=item_orm.product_name,
                quantity=item_orm.quantity,
                unit_price=item_orm.unit_price,
            ))
        return order
```

```python
# adapters/controllers/order_controller.py  （FastAPI 路由层）
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from use_cases.create_order import CreateOrderUseCase, CreateOrderRequest
from adapters.dependencies import get_create_order_use_case  # 依赖注入工厂

router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderHTTPRequest(BaseModel):
    customer_id: UUID
    items: list[dict]


@router.post("/", status_code=201)
def create_order(
    body: CreateOrderHTTPRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
):
    request = CreateOrderRequest(
        customer_id=body.customer_id,
        items=body.items,
    )
    response = use_case.execute(request)
    return {"order_id": str(response.order_id), "total": response.total_amount}
```

---

### 第四层：Frameworks & Drivers（框架与驱动）

最外层是所有技术细节：Web 框架、ORM、消息队列、缓存。这层的代码量最少，主要是"组装"，而非"业务"。

```python
# main.py  （应用入口，负责依赖组装）
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from adapters.controllers.order_controller import router
from adapters.repositories.sql_order_repository import SqlOrderRepository
from adapters.gateways.stripe_payment_gateway import StripePaymentGateway
from adapters.services.email_notification_service import EmailNotificationService
from use_cases.create_order import CreateOrderUseCase

app = FastAPI()
app.include_router(router)

engine = create_engine("postgresql://user:pass@localhost/orders_db")
SessionLocal = sessionmaker(bind=engine)

# 依赖注入：在此处将接口绑定到具体实现
def get_create_order_use_case() -> CreateOrderUseCase:
    session = SessionLocal()
    return CreateOrderUseCase(
        order_repo=SqlOrderRepository(session),
        payment_gateway=StripePaymentGateway(api_key="sk_live_..."),
        notification_service=EmailNotificationService(smtp_host="smtp.example.com"),
    )
```

---

## 项目目录结构

```plaintext
my_app/
├── entities/                   # 第一层：纯领域对象，零外部依赖
│   ├── order.py
│   └── user.py
│
├── use_cases/                  # 第二层：业务用例 + 接口定义
│   ├── interfaces.py           # 抽象接口（Repository, Gateway 等）
│   ├── create_order.py
│   └── cancel_order.py
│
├── adapters/                   # 第三层：格式转换和具体实现
│   ├── controllers/            # HTTP 控制器（FastAPI/Flask 路由）
│   ├── repositories/           # Repository 具体实现（SQL/MongoDB）
│   ├── gateways/               # 第三方服务网关（支付、短信等）
│   ├── services/               # 其他服务实现（通知、缓存等）
│   └── models.py               # ORM 模型定义
│
├── frameworks/                 # 第四层：框架配置、应用组装
│   └── dependencies.py         # 依赖注入工厂函数
│
├── tests/
│   ├── unit/                   # 单元测试：只测 entities 和 use_cases
│   └── integration/            # 集成测试：测 adapters 层
│
└── main.py                     # 应用入口
```

---

## 如何测试？

简洁架构最大的优势就是**可测性**。用例层可以通过 Mock 接口进行纯单元测试，无需启动数据库或 HTTP 服务：

```python
# tests/unit/test_create_order.py
from unittest.mock import MagicMock
from uuid import uuid4
from entities.order import Order
from use_cases.create_order import CreateOrderUseCase, CreateOrderRequest


def test_create_order_success():
    # Arrange：Mock 所有外部依赖
    mock_repo = MagicMock()
    mock_payment = MagicMock()
    mock_payment.charge.return_value = True  # 支付成功
    mock_notification = MagicMock()

    use_case = CreateOrderUseCase(mock_repo, mock_payment, mock_notification)

    request = CreateOrderRequest(
        customer_id=uuid4(),
        items=[{
            "product_id": uuid4(),
            "product_name": "Python 编程书",
            "quantity": 2,
            "unit_price": 89.0,
        }]
    )

    # Act
    response = use_case.execute(request)

    # Assert：不依赖数据库，测试飞快
    assert response.total_amount == 178.0
    assert response.status == "confirmed"
    mock_repo.save.assert_called_once()
    mock_notification.send_confirmation.assert_called_once()
```

---

## 简洁架构 vs 传统三层架构

| 对比维度 | 传统三层（Controller → Service → DAO） | 简洁架构 |
|----------|---------------------------------------|----------|
| **依赖方向** | 从上往下，Service 依赖 DAO | 向内收敛，业务不依赖技术 |
| **可测性** | Service 难以脱离数据库测试 | Use Case 可纯 Mock 测试 |
| **替换框架** | 换 ORM 需改 Service 层 | 只改最外层 Repository 实现 |
| **业务清晰度** | 业务逻辑散落在 Service 和 DAO 之间 | 业务逻辑集中在 Entity + Use Case |
| **学习成本** | 低，上手快 | 中等，需要理解接口抽象 |
| **适用规模** | 小型项目、CRUD 为主 | 中大型、业务复杂、长期维护 |

---

## 常见误区

**误区 1：实体（Entity）= 数据库表**

在简洁架构中，Entity 是**领域对象**，包含业务规则和行为，不是数据库行的映射。数据库 ORM 模型应放在 Adapters 层。

**误区 2：每个项目都要用简洁架构**

对于简单的 CRUD 项目，简洁架构反而是过度设计。当业务规则复杂、团队较大、需要长期维护时，它的价值才能充分体现。

**误区 3：必须严格分四层**

层数可以根据项目规模调整。小项目可以合并 Entities + Use Cases 为一个 `domain/` 目录，重要的是**依赖方向的原则**不能违背。

---

## 参考资料

- Robert C. Martin - *Clean Architecture: A Craftsman's Guide to Software Structure and Design* (2017)
- [The Clean Architecture - Uncle Bob's Blog](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
