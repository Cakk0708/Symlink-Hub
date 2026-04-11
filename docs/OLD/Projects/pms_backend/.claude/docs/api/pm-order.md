# PM - Order 接口文档

> 最后更新：2026-03-16
> App: `PM` | Module: `order`
> Base URL: `/pm`

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
| PATCH | `/projects/{id}/order` | 切换项目下单状态 | ✅ |
| POST | `/projects/{id}/order` | 发送下单提醒消息 | ✅ |

---

## 接口详情

### 1. 切换项目下单状态

**PATCH** `/projects/{id}/order`

切换项目的下单标志（`place_order_flag`）状态，同时更新下单时间。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |

**请求体**

无需请求体

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "place_order_flag": true
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| place_order_flag | boolean | 切换后的下单状态（true/false） |

**错误响应**

```json
{
  "msg": "错误，项目ID不正确"
}
```

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 项目 ID 不正确 |

---

### 2. 发送下单提醒消息

**POST** `/projects/{id}/order`

向项目节点负责人发送下单提醒消息（通过飞书卡片）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |

**权限要求**

需要权限码 `1106`（下单提醒权限）

**请求体**

```json
{
  "type": "IN_PROGRESS",
  "content": "请尽快处理下单相关事宜"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 接收者类型，可选值：`ALL`（所有节点负责人）、`IN_PROGRESS`（进行中的节点负责人），默认 `IN_PROGRESS` |
| content | string | 否 | 提示内容，最多 500 字符，默认 "未填写" |

**业务规则**

1. 项目必须已下单（`place_order_flag = true`），否则返回错误
2. 接收者筛选规则：
   - `type = ALL`：所有节点负责人
   - `type = IN_PROGRESS` 或未指定：未完成/未暂停节点的负责人（排除 `state = 2` 已完成、`state = 3` 暂停）
3. 为每个接收者创建独立的消息记录（`SM_Message`）
4. 消息通过 Celery 异步发送到飞书

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "createdMessages": 3,
    "messageIds": [123, 124, 125]
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| createdMessages | int | 成功创建的消息数量 |
| messageIds | array[int] | 创建成功的消息 ID 列表 |

**错误响应**

```json
{
  "msg": "错误，项目尚未下单无法发起下单提醒"
}
```

```json
{
  "msg": "下单提醒失败，权限不匹配"
}
```

**常见错误**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 项目尚未下单 |
| 400 | 权限不匹配（需要权限码 1106） |
| 400 | 项目 ID 不正确 |
| 500 | 消息创建失败 |

**飞书消息模板**

| 参数 | 说明 |
|------|------|
| template_id | `AAqSEJRBoNBzL` |
| project_name | 项目名称 |
| customer_name | 客户名称 |
| place_order_date | 下单日期 |
| tip_content | 提示内容 |
| publisher | 发送者 open_id |
| project_url | 项目详情页 URL |

---

## 错误响应

所有接口错误时统一返回：

```json
{
  "msg": "错误描述信息"
}
```

**常见错误码**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误 / 业务逻辑错误 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 切换项目下单状态
curl -X PATCH "http://your-domain/pm/projects/123/order" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 发送下单提醒（进行中的节点负责人）
curl -X POST "http://your-domain/pm/projects/123/order" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "IN_PROGRESS",
    "content": "请尽快处理下单相关事宜"
  }'

# 3. 发送下单提醒（所有节点负责人）
curl -X POST "http://your-domain/pm/projects/123/order" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "ALL"
  }'
```

---

## 枚举类型

### ReminderType（接收者类型）

| 值 | 标签 | 说明 |
|---|------|------|
| ALL | 所有节点负责人 | 发送给项目的所有节点负责人 |
| IN_PROGRESS | 进行中的节点负责人 | 仅发送给未完成/未暂停节点的负责人 |
