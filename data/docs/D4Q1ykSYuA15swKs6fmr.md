# PM - ProjectFollower 接口文档

> 最后更新：2026-03-16
> App: `PM` | Model: `ProjectFollower`
> Base URL: `/pm/project`

---

## 认证说明

所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| POST | `/pm/project/{id}/follower` | 切换关注状态 | ✅ |
| DELETE | `/pm/project/{id}/follower` | 批量移除关注者 | ✅ |

---

## 接口详情

### 1. 切换关注状态

**POST** `/pm/project/{id}/follower`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |

**请求体**

```json
{
  "userId": 123
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userId | int | ✅ | 用户 ID |

**响应示例（关注成功）**

```json
{
  "msg": "关注成功",
  "data": {
    "isFollowing": true
  }
}
```

**响应示例（取消关注成功）**

```json
{
  "msg": "取消关注成功",
  "data": {
    "isFollowing": false
  }
}
```

**逻辑说明**
- 如果用户未关注该项目，则添加关注
- 如果用户已关注该项目，则取消关注
- 返回操作后的当前关注状态

---

### 2. 批量移除关注者

**DELETE** `/pm/project/{id}/follower`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |

**请求体**

```json
{
  "projectId": 1,
  "ids": [456, 789]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectId | int | ✅ | 项目 ID |
| ids | array[int] | ✅ | 要移除的用户 ID 列表 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "deletedCount": 2
  }
}
```

**错误响应（用户未关注）**

```json
{
  "msg": "参数错误",
  "data": {
    "projectId": "用户 [456] 未关注此项目"
  }
}
```

---

## 错误响应

所有接口错误时统一返回：

```json
{
  "msg": "error",
  "data": "错误描述信息"
}
```

**常见错误码**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 切换关注状态（关注/取消关注）
curl -X POST "http://your-domain/pm/project/32/follower" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"userId": 123}'

# 2. 批量移除关注者
curl -X DELETE "http://your-domain/pm/project/32/follower" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"projectId": 32, "ids": [456, 789]}'
```

---

## 数据模型

### ProjectFollower

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project | ForeignKey | 关联项目（Project_List） |
| user | ForeignKey | 关联用户（User） |
| created_at | DateTime | 关注时间 |

**约束**
- 同一用户不能重复关注同一项目（unique_together: project, user）
