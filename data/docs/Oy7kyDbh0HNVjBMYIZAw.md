# PM - Project_Continuation 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `Project_Continuation`
> Base URL: `/pm/continuation`

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
| POST | `/continuation/{code}` | 创建项目继续申请 | ✅ |
| PATCH | `/continuation/{code}/{action}` | 更新继续状态（测试用） | ✅ |

---

## 接口详情

### 1. 创建项目继续申请

**POST** `/continuation/{code}`

为已暂停的项目创建继续申请，触发审批流程。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 项目 ID |

**请求体**

```json
{
  "reason": "客户需求已确认，可以继续项目"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | ✅ | 继续原因说明 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "project": {
      "state": 4
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| project.state | int | 项目当前状态 |

**业务规则**

- 项目状态必须为"已暂停"（state=4）
- 项目当前不能有待审批的继续申请（在有效期内）
- 项目不能已经处于进行中状态（state=1）
- 创建成功后会自动发起审批流
- 审批通过后项目状态将变为"进行中"（state=1）

**错误响应示例**

```json
{
  "msg": "error",
  "data": {
    "继续申请创建失败": "项目已发起继续申请，请等待审批结果"
  }
}
```

---

### 2. 更新继续状态（测试用）

**PATCH** `/continuation/{code}/{action}`

更新继续申请的状态（测试接口，生产环境需通过审批流）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | string | 继续记录 ID |
| action | string | 目标状态（PENDING/APPROVED/REJECTED/CANCEL） |

**响应示例**

```json
{
  "msg": "success"
}
```

---

## 数据模型

### Project_Continuation

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project | ForeignKey (PM.Project_List) | 关联项目 |
| applicant | ForeignKey (SM.User) | 申请人 |
| approval | ForeignKey (SM.Approval) | 审批信息 |
| reason | TextField | 继续原因 |
| status | string | 状态（PENDING/APPROVED/REJECTED/CANCEL） |
| create_time | DateTime | 创建时间 |
| complete_time | DateTime | 完成时间 |

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
| 继续申请创建失败：项目已发起继续申请，请等待审批结果 | 项目存在待审批的继续申请 |
| 继续申请创建失败：项目已处于进行中 | 项目状态已是进行中 |
| 继续申请创建失败：项目状态不正确 | 项目状态不是"已暂停" |
| 项目继续审批流创建失败：未能成功构建项目继续审批 | 审批流创建失败 |

---

## 完整 cURL 示例

```bash
# 1. 创建项目继续申请
curl -X POST "https://your-domain.com/api/pm/continuation/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "reason": "客户需求已确认，可以继续项目"
  }'

# 2. 更新继续状态（测试用）
curl -X PATCH "https://your-domain.com/api/pm/continuation/456/APPROVED" \
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

## 附录：继续申请状态枚举

| 状态值 | 说明 |
|-------|------|
| PENDING | 待评审 |
| APPROVED | 已评审 |
| REJECTED | 已拒绝 |
| CANCEL | 已取消 |
