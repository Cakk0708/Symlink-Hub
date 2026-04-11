# PM - DeliverableFreeze 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `DeliverableFreeze`
> Base URL: `/api/pm/deliverable`

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
| PATCH | `/instances/{deliverable_id}/freeze` | 冻结/解冻交付物 | ✅ |

---

## 接口详情

### 1. 冻结/解冻交付物

**PATCH** `/instances/{deliverable_id}/freeze`

根据交付物当前状态自动切换冻结/解冻状态：
- **NORMAL** → **FROZEN**（冻结）
- **FROZEN** / **INITIAL_FROZEN** → **NORMAL**（解冻）

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**请求体**

```json
{
  "reason": "需要冻结的原因（可选）"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | 否 | 冻结/解冻原因，最长 255 字符 |

**权限要求**

- 需要节点权限码 `2300`（交付物冻结/解冻权限）

**状态限制**

仅允许以下状态之间进行切换：
- `NORMAL`（正常）→ `FROZEN`（已冻结）
- `FROZEN`（已冻结）→ `NORMAL`（正常）
- `INITIAL_FROZEN`（初始冻结）→ `NORMAL`（正常）

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 123,
    "state": "FROZEN",
    "stateDisplay": "已冻结",
    "action": "freeze"
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物实例 ID |
| state | string | 交付物状态代码 |
| stateDisplay | string | 交付物状态显示名称 |
| action | string | 执行的操作：`freeze`（冻结）或 `unfreeze`（解冻） |

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
| 400 | 请求参数错误 / 权限不足 / 状态不允许操作 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限 |
| 404 | 交付物不存在 |
| 500 | 服务器内部错误 |

**错误示例**

```json
{
  "msg": "error",
  "data": {
    "操作失败": "权限不匹配"
  }
}
```

```json
{
  "msg": "error",
  "data": {
    "操作失败": "交付物当前状态为\"已完成\"，无法执行冻结/解冻操作"
  }
}
```

---

## 完整 cURL 示例

```bash
# 1. 冻结交付物
curl -X PATCH "http://your-domain/api/pm/deliverable/instances/123/freeze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"reason": "等待审核"}'

# 2. 解冻交付物
curl -X PATCH "http://your-domain/api/pm/deliverable/instances/123/freeze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"reason": "审核通过，解冻继续"}'
```

---

## 数据模型

### DeliverableFreeze（交付物冻结记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| deliverable | ForeignKey | 关联的交付物实例 |
| reason | string(255) | 冻结原因 |
| frozen_by | ForeignKey | 冻结人 |
| frozen_at | DateTime | 冻结时间 |
| unfrozen_by | ForeignKey | 解冻人（可为空） |
| unfrozen_at | DateTime | 解冻时间（可为空） |

### 交付物状态枚举

| 状态码 | 显示名称 | 说明 |
|--------|---------|------|
| NORMAL | 正常 | 交付物正常状态，可编辑 |
| FROZEN | 已冻结 | 交付物已冻结，不可编辑 |
| INITIAL_FROZEN | 初始冻结 | 交付物初始冻结状态 |
| COMPLETED | 已完成 | 交付物已完成 |
