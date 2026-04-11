# PM - ProjectCategory 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `ProjectCategory`
> Base URL: `/pm/projects`

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
| GET | `/pm/projects/category` | 获取项目分类统计 | ✅ |

---

## 接口详情

### GET 获取项目分类统计

获取项目列表的分类统计数据，包括全部、进行中、变更中等状态的统计信息。

**接口路径：** `GET /pm/projects/category`

**权限要求：** 需要登录（`IsAuthenticated`）

**请求参数：** 无

**请求示例：**

```bash
curl -X GET "/pm/projects/category" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应示例：**

```json
{
  "msg": "success",
  "data": [
    {
      "type": "ALL",
      "name": "全部",
      "total": 100,
      "overdue": 5
    },
    {
      "type": "PRO",
      "name": "进行中",
      "total": 50,
      "overdue": 3
    },
    {
      "type": "CHG",
      "name": "变更中",
      "total": 10,
      "overdue": 1
    },
    {
      "type": "CHGS",
      "name": "变更完成",
      "total": 8,
      "overdue": 0
    },
    {
      "type": "COM",
      "name": "已完成",
      "total": 25,
      "overdue": 1
    },
    {
      "type": "SUS",
      "name": "已暂停",
      "total": 3,
      "overdue": 0
    },
    {
      "type": "INPROG",
      "name": "申请中",
      "total": 4,
      "overdue": 0
    },
    {
      "type": "CANCEL",
      "name": "取消立项",
      "total": 0,
      "overdue": 0
    },
    {
      "type": "RPB",
      "name": "我负责的",
      "total": 15,
      "overdue": 2
    },
    {
      "type": "FLW",
      "name": "我关注的",
      "total": 8,
      "overdue": 0
    },
    {
      "type": "IND",
      "name": "我参与的",
      "total": 20,
      "overdue": 1
    }
  ]
}
```

**响应字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 分类类型代码 |
| name | string | 分类名称 |
| total | integer | 该分类下的项目总数 |
| overdue | integer | 该分类下已逾期的项目数 |

**分类类型说明：**

| Type | 名称 | 说明 |
|------|------|------|
| ALL | 全部 | 所有状态的项目总数 |
| PRO | 进行中 | 状态为进行中的项目（state=1） |
| CHG | 变更中 | 状态为变更中的项目（state=3） |
| CHGS | 变更完成 | 状态为已完成且变更已批准的项目（state=2） |
| COM | 已完成 | 状态为已完成的项目（state=2） |
| SUS | 已暂停 | 状态为已暂停的项目（state=4） |
| INPROG | 申请中 | 状态为申请中的项目（state=5） |
| CANCEL | 取消立项 | 状态为取消立项的项目（state=6） |
| RPB | 我负责的 | 当前用户作为负责人的项目 |
| FLW | 我关注的 | 当前用户关注的项目 |
| IND | 我参与的 | 当前用户作为节点参与者的项目 |

**逾期判断标准：** 项目 `deadline_time` 早于当前时间

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
# 获取项目分类统计
curl -X GET "/pm/projects/category" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 相关模型

### Project_List
项目列表主模型，包含项目基本信息和状态。

**关键字段：**
- `id`: 项目ID
- `name`: 项目名称
- `content`: 项目内容描述
- `state`: 项目状态（1=进行中, 2=已完成, 3=变更中, 4=已暂停, 5=申请中, 6=取消立项）
- `deadline_time`: 截止时间（用于判断是否逾期）
- `owner`: 项目负责人（外键关联 SM.User）
- `creator`: 创建者（外键关联 SM.User）
- `customer`: 客户（外键关联 BDM.Customer）
- `model`: 客户模型（外键关联 BDM.CustomerModel）

### Project_Node_Owners
项目节点负责人关系表，用于统计"我参与的"项目。

**关联关系：**
- `user`: 用户（外键关联 SM.User）
- `node`: 项目节点（外键关联 Project_Node）

### ProjectFollower
项目关注者关系表，用于统计"我关注的"项目。

**关联关系：**
- `user`: 关注用户（外键关联 SM.User）
- `project`: 被关注的项目（外键关联 Project_List）
