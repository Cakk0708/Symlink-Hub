# customer 模块

## 职责
订单生命周期管理：创建、支付确认、取消、退款。

## 模块位置

## 数据模型

## 序列化器

## 视图

## URL 路由配置

## 枚举数据

## 关联模块

## 业务规则

## 使用场景

## 常见问题

## 开发注意事项

## 依赖
- users.selectors.get_user()       获取用户信息
- payments.services.charge()       触发支付
- notifications.services.send()    发送状态通知

## 状态机
\```
PENDING → PAID → SHIPPED → COMPLETED
    ↓
CANCELLED
\```

## 禁止事项
- 禁止直接操作 User model
- 禁止在 views.py 里判断订单状态
- 禁止 orders 反向被 users 模块引用

## 变更记录
### 2026-03-13
- 创建文档
### 2026-03-14
- 更新 name 备注