# BDM - Staff 接口文档

> 最后更新：2026-03-21
> App: `BDM` | Model: `Staff`
> Base URL: `/bdm/staff`

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
| GET | `/bdm/staff` | 获取列表（不分页） | ✅ |
| POST | `/bdm/staff` | 创建员工 | ✅ |
| GET | `/bdm/staff/<id>` | 获取详情 | ✅ |
| PUT | `/bdm/staff/<id>` | 完整更新 | ✅ |
| GET | `/bdm/staff/list` | 获取列表（分页） | ✅ |
| PATCH | `/bdm/staff/list` | 批量部分更新 | ✅ |
| DELETE | `/bdm/staff/list` | 批量删除 | ✅ |
| GET | `/bdm/staff/enums` | 获取枚举数据 | ✅ |

---

## 接口详情

### 1. 获取员工列表（不分页）

**GET** `/bdm/staff`

等同于 GET `/bdm/staff/list`，但不分页。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 否 | 搜索关键词（匹配员工编码或名称） |
| sortField | string | 否 | 排序字段，默认 `id` |
| sortOrder | string | 否 | 排序方向，`asc` 或 `desc`，默认 `desc` |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "index": 1,
        "id": 1,
        "code": "STAFF000001",
        "name": "张三",
        "disableFlag": false,
        "createdAt": "2024-01-01T00:00:00+08:00",
        "updatedAt": "2024-01-01T00:00:00+08:00",
        "createdByName": "管理员",
        "updatedByName": "管理员"
      }
    ]
  }
}
```

---

### 2. 获取员工列表（分页）

**GET** `/bdm/staff/list`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 否 | 搜索关键词（匹配员工编码或名称） |
| pageNum | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| sortField | string | 否 | 排序字段，默认 `id` |
| sortOrder | string | 否 | 排序方向，`asc` 或 `desc`，默认 `desc` |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "index": 1,
        "id": 1,
        "code": "STAFF000001",
        "name": "张三",
        "disableFlag": false,
        "createdAt": "2024-01-01T00:00:00+08:00",
        "updatedAt": "2024-01-01T00:00:00+08:00",
        "createdByName": "管理员",
        "updatedByName": "管理员"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 50,
      "totalPages": 5
    }
  }
}
```

---

### 3. 获取员工详情

**GET** `/bdm/staff/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 员工 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "STAFF000001",
      "name": "张三",
      "remark": "研发部工程师",
      "disableFlag": false,
      "departments": [
        {
          "departmentId": 1,
          "departmentName": "研发部",
          "isLeader": false
        }
      ]
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-01T00:00:00+08:00",
      "createdBy": {
        "id": 1,
        "username": "admin"
      },
      "updatedBy": {
        "id": 1,
        "username": "admin"
      }
    }
  }
}
```

---

### 4. 创建员工

**POST** `/bdm/staff`

**请求体**

```json
{
  "code": "STAFF000002",
  "name": "李四",
  "remark": "市场部经理",
  "disable_flag": false,
  "departments": [
    {
      "departmentId": 2,
      "isLeader": true
    }
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 员工编码，唯一 |
| name | string | ✅ | 员工名称，唯一 |
| remark | string | 否 | 备注 |
| disable_flag | boolean | 否 | 禁用状态，默认 false |
| departments | array | 否 | 部门列表 |
| departments[].departmentId | int | ✅ | 部门 ID |
| departments[].isLeader | boolean | 否 | 是否为部门负责人，默认 false |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 2
  }
}
```

---

### 5. 更新员工

**PUT** `/bdm/staff/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 员工 ID |

**请求体**

```json
{
  "code": "STAFF000002",
  "name": "李四（更新）",
  "remark": "备注已更新",
  "disable_flag": true,
  "departments": [
    {
      "departmentId": 2,
      "isLeader": false
    },
    {
      "departmentId": 3,
      "isLeader": true
    }
  ]
}
```

**注意事项**

- 更新时若提供 `departments` 字段，会完全替换员工与部门的关联关系

**响应示例**

```json
{
  "msg": "修改成功"
}
```

---

### 6. 批量部分更新员工

**PATCH** `/bdm/staff/list`

**请求体**

```json
{
  "ids": [1, 2, 3],
  "disableFlag": true
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 员工 ID 列表 |
| disableFlag | boolean | 否 | 禁用状态 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 7. 批量删除员工

**DELETE** `/bdm/staff/list`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 员工 ID 列表 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 8. 获取枚举数据

**GET** `/bdm/staff/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "choices": {
      "disable_flag": [
        {
          "value": true,
          "label": "禁用"
        },
        {
          "value": false,
          "label": "启用"
        }
      ]
    },
    "permissions": [
      {
        "value": "CREATE",
        "label": "创建",
        "key": "BDM.add_staff"
      },
      {
        "value": "VIEW",
        "label": "查看",
        "key": "BDM.view_staff"
      },
      {
        "value": "CHANGE",
        "label": "修改",
        "key": "BDM.change_staff"
      },
      {
        "value": "DELETE",
        "label": "删除",
        "key": "BDM.delete_staff"
      },
      {
        "value": "DISABLE",
        "label": "禁用",
        "key": "BDM.disable_staff"
      }
    ]
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

**业务错误示例**

```json
{
  "msg": "error",
  "errors": {
    "code": [
      "\"STAFF000001\"已被使用，请更换员工编码后重试"
    ],
    "name": [
      "\"张三\"已被使用，请更换员工名称后重试"
    ]
  }
}
```

```json
{
  "msg": "error",
  "errors": {
    "STAFF000001": [
      "修改禁用状态失败，禁用状态不正确"
    ]
  }
}
```

---

## 数据模型说明

### Staff（员工）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string | 员工编码，唯一 |
| name | string | 员工名称，唯一 |
| remark | string | 备注 |
| disable_flag | boolean | 禁用状态 |
| created_by | ForeignKey | 创建人（关联 SM.User） |
| updated_by | ForeignKey | 更新人（关联 SM.User） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### StaffDepartment（员工部门关联）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| staff | ForeignKey | 员工（关联 Staff） |
| department | ForeignKey | 部门（关联 Department） |
| is_leader | boolean | 是否为部门负责人 |

---

## 完整 cURL 示例

```bash
# 1. 获取员工列表（分页）
curl -X GET "http://your-domain.com/bdm/staff/list?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取员工详情
curl -X GET "http://your-domain.com/bdm/staff/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建员工
curl -X POST "http://your-domain.com/bdm/staff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "code": "STAFF000002",
    "name": "李四",
    "remark": "市场部经理",
    "disable_flag": false,
    "departments": [
      {
        "departmentId": 2,
        "isLeader": true
      }
    ]
  }'

# 4. 更新员工
curl -X PUT "http://your-domain.com/bdm/staff/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "李四（更新）",
    "remark": "备注已更新",
    "departments": [
      {
        "departmentId": 2,
        "isLeader": false
      }
    ]
  }'

# 5. 批量部分更新
curl -X PATCH "http://your-domain.com/bdm/staff/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3],
    "disableFlag": true
  }'

# 6. 批量删除
curl -X DELETE "http://your-domain.com/bdm/staff/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3]
  }'

# 7. 获取枚举数据
curl -X GET "http://your-domain.com/bdm/staff/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
