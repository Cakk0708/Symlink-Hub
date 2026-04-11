# User 模型参考

## 位置
`apps/SM/models.py`

## User 模型

Django JWT 认证用户模型，独立表，通过 `open_id` 关联到 `Feishu_users`。

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| open_id | CharField(255) | 飞书 open_id，唯一标识 |
| password | CharField(128) | 密码（可为空） |
| last_login | DateTimeField | 最后登录时间 |
| email | CharField(150) | 邮箱（可为空） |
| is_staff | BooleanField | 是否为员工 |
| is_active | BooleanField | 是否激活 |
| date_joined | DateTimeField | 加入时间 |

### 关系

| 关系 | 类型 | 反向关系 |
|------|------|----------|
| feishu_token | OneToOneField → UserFeishuToken | related_name='feishu_token' |

### 方法

```python
# 获取关联的飞书用户
feishu_user = user.get_feishu_user()
```

## UserFeishuToken 模型

飞书 Token 存储。

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| user | OneToOneField → User | 关联的用户 |
| token_type | CharField(50) | Token 类型 |
| access_token | CharField(255) | 访问令牌 |
| refresh_token | CharField(255) | 刷新令牌 |
| expires_at | DateTimeField | 过期时间 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

## Feishu_users 模型

飞书用户信息模型。

### 关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| open_id | CharField | 飞书 open_id（主键） |
| nickname | CharField | 昵称 |
| avatar | CharField | 头像 |
| department | JSONField | 部门信息 |
| in_service | BooleanField | 是否在职 |
| is_superuser | BooleanField | 是否为超级用户 |
