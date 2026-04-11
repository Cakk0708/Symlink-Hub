# PM - NodeListReview 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `NodeReview`
> Base URL: `/pm/node`

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
| GET | `/{node_id}/reviews/{review_id}` | 获取评审记录列表 | ✅ |
| POST | `/{node_id}/reviews/{review_id}` | 创建评审记录 | ✅ |

---

## 接口详情

### GET 获取评审记录列表

获取指定节点评审项的所有评审记录。

#### 请求

```
GET /pm/node/{node_id}/reviews/{review_id}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| node_id | integer | 是 | 节点 ID |
| review_id | integer | 是 | 评审项定义版本 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "nodeId": 123,
      "nodeName": "设计节点",
      "reviewDefinitionVersionId": 456,
      "reviewName": "UI设计评审",
      "processStatus": "APPROVED",
      "processStatusDisplay": "通过",
      "remark": "评审通过，符合要求",
      "createdAt": "2024-01-01T10:00:00+08:00",
      "processedBy": {
        "id": 789,
        "name": "张三",
        "avatar": "https://example.com/avatar.jpg"
      }
    }
  ]
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 评审记录 ID |
| nodeId | integer | 节点 ID |
| nodeName | string | 节点名称 |
| reviewDefinitionVersionId | integer | 评审项定义版本 ID |
| reviewName | string | 评审项名称 |
| processStatus | string | 处理状态（PENDING/APPROVED/REJECTED） |
| processStatusDisplay | string | 处理状态显示文本 |
| remark | string | 处理备注 |
| createdAt | string | 创建时间（ISO 8601） |
| processedBy | object | 处理人信息 |
| processedBy.id | integer | 处理人 ID |
| processedBy.name | string | 处理人姓名 |
| processedBy.avatar | string | 处理人头像 URL |

---

### POST 创建评审记录

为指定节点评审项创建新的评审记录。

#### 请求

```
POST /pm/node/{node_id}/reviews/{review_id}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| node_id | integer | 是 | 节点 ID |
| review_id | integer | 是 | 评审项定义版本 ID |

**请求体：**

```json
{
  "processStatus": "APPROVED",
  "remark": "评审通过，符合要求"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| processStatus | string | 是 | 处理状态：PENDING（待评审）、APPROVED（通过）、REJECTED（拒绝） |
| remark | string | 否 | 处理备注 |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "nodeId": 123,
    "nodeName": "设计节点",
    "reviewDefinitionVersionId": 456,
    "reviewName": "UI设计评审",
    "processStatus": "APPROVED",
    "processStatusDisplay": "通过",
    "remark": "评审通过，符合要求",
    "createdAt": "2024-01-01T10:00:00+08:00",
    "processedBy": {
      "id": 789,
      "name": "张三",
      "avatar": "https://example.com/avatar.jpg"
    }
  }
}
```

**错误响应（400 Bad Request）：**

```json
{
  "msg": "error",
  "data": {
    "processStatus": ["无效的处理状态"]
  }
}
```

---

## 数据模型

### NodeReview 模型

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 主键 |
| node | ForeignKey | 关联节点（PM.Project_Node） |
| review_definition_version | ForeignKey | 关联评审项定义版本（PSC.ReviewDefinitionVersion） |
| process_status | string | 评审状态（PENDING/APPROVED/REJECTED） |
| processed_by | ForeignKey | 处理人（SM.User），可为空 |
| remark | TextField | 处理备注 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

**索引：**
- 复合索引：(node, review_definition_version)
- 状态索引：(process_status)
- 时间索引：(created_at)

**属性方法：**
- `is_approved` - 判断是否通过
- `is_rejected` - 判断是否拒绝

### 评审状态（process_status）

| 值 | 说明 |
|----|------|
| PENDING | 待评审 |
| APPROVED | 通过 |
| REJECTED | 拒绝 |

---

## 业务逻辑说明

1. **评审拒绝处理**：当评审状态为 REJECTED 时，自动触发：
   - 更新关联交付物状态为 REVIEW_REJECTED
   - 回滚节点到 IN_PROGRESS 状态
   - 发送通知消息给节点负责人

2. **信号处理**：通过 `post_save` 信号自动处理评审拒绝逻辑

3. **异步通知**：评审拒绝后异步发送飞书通知给节点负责人

4. **交付物关联**：支持固定类型（fixed）和自定义类型（custom）的评审项

---

## 权限说明

- 所有接口都需要用户认证（`IsAuthenticated`）
- 评审记录的创建和处理需要相应的节点权限

---

## 完整 cURL 示例

```bash
# 1. 获取评审记录列表
curl -X GET "https://api.example.com/pm/node/123/reviews/456" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建评审记录（通过）
curl -X POST "https://api.example.com/pm/node/123/reviews/456" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "processStatus": "APPROVED",
    "remark": "评审通过，符合要求"
  }'

# 3. 创建评审记录（拒绝）
curl -X POST "https://api.example.com/pm/node/123/reviews/456" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "processStatus": "REJECTED",
    "remark": "需要修改设计"
  }'
```
