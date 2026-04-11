# 核心业务逻辑

## 账户验证流程

支持三种验证方式：

### 1. 用户名密码

直接使用 Duolingo 账号密码登录验证

### 2. 手机号 + 验证码

1. 发送验证码到手机
2. 输入验证码验证

### 3. API Token

直接使用 API Token 验证

### 凭证缓存

验证成功的凭据会在 Redis 中缓存（10分钟 TTL），使用 `cacheKey` 用于账户创建。

## 订单状态机

```
waiting → doing → done
   ↓         ↓
pause    cancel
   ↓         ↓
  ←      error
```

### 状态说明

- **waiting**: 等待执行
- **doing**: 执行中
- **done**: 已完成
- **pause**: 已暂停
- **cancel**: 已取消
- **error**: 执行出错

### 状态转换

- waiting → doing: 开始执行
- doing → done: 执行完成
- doing → pause: 暂停执行
- pause → waiting: 恢复等待
- doing → cancel: 取消执行
- doing → error: 执行失败

## 多租户

所有数据按用户组织过滤：

- 后端根据认证用户自动应用组织过滤
- 用户只能访问自己创建的数据
- 跨用户数据隔离

## 数据流转

1. 用户创建客户
2. 为客户添加 Duolingo 账户
3. 创建订单并关联账户
4. 订单进入任务队列
5. 后台执行任务
6. 更新订单状态
7. 前端实时显示状态
