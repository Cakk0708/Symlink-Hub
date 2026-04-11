# PM - Project Status 接口文档

> 最后更新：2026-03-17
> App: `PM` | Model: `ProjectStatus`
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
| PATCH | `/{id}/status` | 更新项目状态 | ✅ |

---

## 接口详情

### 1. 更新项目状态

**PATCH** `/pm/project/{id}/status`

专门处理项目状态变更的接口，支持暂停、完成、取消、恢复等状态转换。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |

**请求体**

```json
{
  "status": "6",
  "reason": "项目需求变更，不再需要实施"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | ✅ | 目标状态，见下方状态值说明 |
| reason | string | 否 | 状态变更原因（用于取消、暂停等操作） |

**状态值说明**

| 值 | 状态名称 | 说明 | 所需权限 |
|----|---------|------|----------|
| `1` | 进行中 | 恢复项目进行中（仅限已暂停的项目） | 1103 |
| `2` | 已完成 | 完成项目（需所有里程碑已完成） | 1100 |
| `4` | 已暂停 | 暂停项目（仅限进行中的项目） | 1101 |
| `6` | 取消立项 | 取消项目（仅限进行中或申请中的项目） | 1102 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "projectId": 123,
    "status": 6
  }
}
```

**状态转换规则**

| 当前状态 | 可转换至 | 说明 |
|---------|---------|------|
| 进行中 (1) | 已暂停 (4)、已完成 (2)、取消立项 (6) | |
| 已暂停 (4) | 进行中 (1) | |
| 申请中 (5) | 取消立项 (6) | |

**权限说明**

- 1100: 可完成项目
- 1101: 可暂停项目
- 1102: 可取消项目
- 1103: 可恢复项目

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
| 404 | 项目不存在 |
| 500 | 服务器内部错误 |

**错误示例**

```json
{
  "msg": "项目暂停失败：权限不匹配"
}
```

```json
{
  "msg": "项目完成失败：尚有里程碑未完成"
}
```

```json
{
  "msg": "项目取消失败：只有进行中或申请中的项目可以取消"
}
```

---

## cURL 示例

### 暂停项目

```bash
curl -X PATCH "http://your-domain/pm/project/123/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "state": "4",
    "reason": "等待客户确认需求"
  }'
```

### 完成项目

```bash
curl -X PATCH "http://your-domain/pm/project/123/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "state": "2"
  }'
```

### 取消项目

```bash
curl -X PATCH "http://your-domain/pm/project/123/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "state": "6",
    "reason": "项目需求变更，不再需要实施"
  }'
```

### 恢复项目

```bash
curl -X PATCH "http://your-domain/pm/project/123/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "state": "1",
    "reason": "客户确认完成，继续实施"
  }'
```

<!-- NOTE: 权限码 1102 和 1103 为新增权限，需在权限系统中配置 -->
