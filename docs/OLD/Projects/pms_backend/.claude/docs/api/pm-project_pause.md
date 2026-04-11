# PM - Project_Pause 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `Project_Pause`
> Base URL: `/pm/pause`

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
| POST | `/pause/{code}` | 创建项目暂停申请 | ✅ |
| PATCH | `/pause/{code}/{action}` | 更新暂停状态（测试用） | ✅ |

---

## 接口详情

### 1. 创建项目暂停申请

**POST** `/pause/{code}`

为指定项目创建暂停申请，触发审批流程。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 项目 ID 或编码 |

**请求体**

```json
{
  "reason": "项目需要等待客户确认需求"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | ✅ | 暂停原因说明 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "project": {
      "state": 1
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| project.state | int | 项目当前状态（1-进行中，4-已暂停） |

**业务规则**

- 项目状态必须为"进行中"（state=1）
- 项目当前不能有待审批的暂停申请（在有效期内）
- 项目不能已经处于暂停状态（state=4）
- 创建成功后会自动发起审批流
- 审批通过后项目状态将变为"已暂停"（state=4）

**错误响应示例**

```json
{
  "msg": "error",
  "data": {
    "暂停申请创建失败": "项目已发起暂停申请，请等待审批结果"
  }
}
```

---

### 2. 更新暂停状态（测试用）

**PATCH** `/pause/{code}/{action}`

更新暂停申请的状态（测试接口，生产环境需通过审批流）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 暂停记录 ID |
| action | string | 目标状态（PENDING/APPROVED/REJECTED/CANCEL） |

**响应示例**

```json
{
  "msg": "success"
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

**常见业务错误**

| 错误信息 | 说明 |
|---------|------|
| 暂停申请创建失败：项目已发起暂停申请，请等待审批结果 | 项目存在待审批的暂停申请 |
| 暂停申请创建失败：项目已处于暂停模式 | 项目状态已为暂停 |
| 暂停申请创建失败：项目状态不正确 | 项目状态不是"进行中" |
| 暂停审批流创建失败：未能成功构建暂停审批 | 审批流创建失败 |

---

## 完整 cURL 示例

```bash
# 1. 创建项目暂停申请
curl -X POST "https://your-domain.com/api/pm/pause/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "reason": "项目需要等待客户确认需求"
  }'

# 2. 更新暂停状态（测试用）
curl -X PATCH "https://your-domain.com/api/pm/pause/456/APPROVED" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 附录：项目状态枚举

| 状态值 | 说明 |
|-------|------|
| 1 | 进行中 |
| 2 | 已完成 |
| 3 | 项目变更中 |
| 4 | 已暂停 |
| 5 | 申请中 |
| 6 | 取消立项 |

## 附录：暂停申请状态枚举

| 状态值 | 说明 |
|-------|------|
| PENDING | 待评审 |
| APPROVED | 已评审 |
| REJECTED | 已拒绝 |
| CANCEL | 已取消 |
