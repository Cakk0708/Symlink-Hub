# 项目地图

> 新成员和 AI 的第一份必读文档。读完此文件可理解整个项目全貌。

## 项目一句话定位
XX 电商平台后端 API，Django 5 + DRF + PostgreSQL + Celery。

---

## 模块全景

\```
apps/
├── users/          用户注册、登录、权限（JWT）
├── products/       商品管理、分类、库存
├── orders/         订单创建、状态流转、退款
├── payments/       支付集成（Stripe），依赖 orders
├── notifications/  邮件/推送，被 orders + payments 触发
└── shared/         公共工具，禁止引用任何业务模块
\```

---

## 依赖关系

\```
users ◄─── orders ◄─── payments
              │
              ▼
        notifications ◄─── payments
        
shared ◄─── 所有模块
\```

**规则：依赖只能单向，禁止循环。**

---

## 数据流

用户下单 → orders.services.create_order()
         → payments.services.charge()
         → notifications.services.send_confirmation()

---

## 分层规范

| 层 | 文件 | 职责 |
|----|------|------|
| 视图层 | views.py | 只处理请求/响应，无业务逻辑 |
| 业务层 | services.py | 所有写操作和业务判断 |
| 查询层 | selectors.py | 所有只读 ORM 查询 |
| 序列化 | serializers.py | 数据校验和格式转换 |

**跨模块调用只能通过对方的 services.py 或 selectors.py。**

---

## 各模块详情

- [用户模块](./modules/users.md)
- [订单模块](./modules/orders.md)
- [支付模块](./modules/payments.md)
- [通知模块](./modules/notifications.md)

---

## 不在这里的内容

- API 接口规范 → [api-conventions.md](./api-conventions.md)
- 数据库模型详情 → [data-model.md](./data-model.md)
- 本地开发启动 → [dev-setup.md](./dev-setup.md)