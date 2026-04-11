# PM - NodeListOwner 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `Project_Node_Owners`
> Base URL: `/pm/nodelist/owner`

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
| POST | `/set` | 批量设置节点负责人 | ✅ |
| POST | `/{code}` | 创建节点负责人 | ✅ |
| PATCH | `/{code}` | 更新节点负责人 | ✅ |
| DELETE | `/{code}` | 删除节点负责人 | ✅ |

---

## 接口详情

### POST 批量设置节点负责人

批量设置节点的负责人和协作者，第一个用户自动设为主要负责人。

#### 请求

```
POST /pm/nodelist/owner/set
```

**请求体：**

```json
{
  "nodeId": 1,
  "userIds": [123, 456, 789]
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nodeId | integer | 是 | 节点 ID |
| userIds | array | 是 | 用户 ID 列表，第一个自动设为主要负责人 |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "node_id": 100,
      "user_id": 123,
      "user": {
        "id": 123,
        "name": "张三",
        "avatar": "avatar_url"
      },
      "standard_time": 0.0,
      "is_major": true
    },
    {
      "id": 2,
      "node_id": 100,
      "user_id": 456,
      "user": {
        "id": 456,
        "name": "李四",
        "avatar": "avatar_url"
      },
      "standard_time": 0.0,
      "is_major": false
    }
  ]
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 负责人记录 ID |
| node_id | integer | 节点 ID |
| user_id | integer | 用户 ID |
| user | object | 用户信息 |
| standard_time | decimal | 标准工时（小时） |
| is_major | boolean | 是否主要负责人 |

**错误响应（400 Bad Request）：**

```json
{
  "msg": "操作失败，权限不匹配",
  "errors": {
    "负责人编辑失败": "权限不匹配"
  }
}
```

---

### POST 创建节点负责人

为指定节点添加负责人。

#### 请求

```
POST /pm/nodelist/owner/{code}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 节点代码或 ID（支持逗号分隔的多个值） |

**请求体：**

```json
{
  "node_id": 1,
  "user_id": 123,
  "standard_time": 8.0,
  "is_major": true
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| node_id | integer | 是 | 节点 ID |
| user_id | integer | 是 | 用户 ID |
| standard_time | decimal | 否 | 标准工时（小时），默认 0 |
| is_major | boolean | 否 | 是否主要负责人，默认 false |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "node_id": 1,
    "user_id": 123,
    "user": {
      "id": 123,
      "name": "张三",
      "avatar": "avatar_url"
    },
    "standard_time": 8.0,
    "is_major": true
  }
}
```

---

### PATCH 更新节点负责人

更新节点负责人信息。

#### 请求

```
PATCH /pm/nodelist/owner/{code}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 节点代码或 ID（支持逗号分隔的多个值） |

**请求体：**

```json
{
  "standard_time": 8.0,
  "is_major": false
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| standard_time | decimal | 否 | 标准工时（小时） |
| is_major | boolean | 否 | 是否主要负责人 |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "standard_time": 8.0,
    "is_major": false
  }
}
```

---

### DELETE 删除节点负责人

删除节点负责人（支持批量删除）。

#### 请求

```
DELETE /pm/nodelist/owner/{code}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 负责人记录 ID（支持逗号分隔的多个值） |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "deletedCount": 2
  }
}
```

---

## 数据模型

### Project_Node_Owners 模型

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 主键 |
| node | ForeignKey | 关联节点（Project_Node） |
| user | ForeignKey | 关联用户（SM.User） |
| standard_time | DecimalField | 标准工时（小时） |
| is_major | BooleanField | 是否主要负责人 |

**约束：**
- 同一节点-用户组合不能重复

---

## 权限说明

| 权限码 | 说明 | 允许角色 |
|--------|------|----------|
| 2001 | 负责人编辑 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR, MANAGER |
| 2004 | 工时编辑 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR |

**业务规则：**
- 节点已完成状态时，仅超级管理员可编辑负责人
- 节点已完成状态时，仅超级管理员可修改工时
- 节点必须先设置负责人才能设置工时

---

## 业务逻辑说明

1. **批量设置**：批量设置时第一个用户自动设为 `is_major=true`，后续用户为 `false`
2. **事务处理**：使用事务确保批量操作的原子性
3. **重复验证**：防止同一用户重复设置为节点负责人
4. **操作日志**：所有操作都会记录项目操作日志

---

## 完整 cURL 示例

```bash
# 1. 批量设置节点负责人
curl -X POST "https://api.example.com/pm/nodelist/owner/set" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nodeId": 1,
    "userIds": [123, 456, 789]
  }'

# 2. 创建节点负责人
curl -X POST "https://api.example.com/pm/nodelist/owner/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "node_id": 1,
    "user_id": 123,
    "standard_time": 8.0,
    "is_major": true
  }'

# 3. 更新节点负责人
curl -X PATCH "https://api.example.com/pm/nodelist/owner/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "standard_time": 8.0,
    "is_major": false
  }'

# 4. 删除节点负责人
curl -X DELETE "https://api.example.com/pm/nodelist/owner/1,2,3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
