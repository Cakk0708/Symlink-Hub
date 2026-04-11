# BDM - Department 接口文档

> 最后更新：2026-03-21
> App: `BDM` | Model: `Department`
> Base URL: `/bdm/department`

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
| GET | `/bdm/department` | 获取列表（不分页） | ✅ |
| POST | `/bdm/department` | 创建部门 | ✅ |
| GET | `/bdm/department/<id>` | 获取详情 | ✅ |
| PUT | `/bdm/department/<id>` | 完整更新 | ✅ |
| GET | `/bdm/department/list` | 获取列表（分页） | ✅ |
| PATCH | `/bdm/department/list` | 批量部分更新 | ✅ |
| DELETE | `/bdm/department/list` | 批量删除 | ✅ |
| GET | `/bdm/department/enums` | 获取枚举数据 | ✅ |
| GET | `/bdm/department/simple` | 获取简化列表 | ✅ |

---

## 接口详情

### 1. 获取部门列表（不分页）

**GET** `/bdm/department`

等同于 GET `/bdm/department/list`，但不分页。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 否 | 搜索关键词（匹配部门编码或名称） |
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
        "code": "DEPT000001",
        "name": "研发部",
        "ownerName": "张三",
        "parentName": "总公司",
        "memberQty": 10,
        "disableFlag": false,
        "createdAt": "2024-01-01T00:00:00+08:00"
      }
    ]
  }
}
```

---

### 2. 获取部门列表（分页）

**GET** `/bdm/department/list`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 否 | 搜索关键词（匹配部门编码或名称） |
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
        "code": "DEPT000001",
        "name": "研发部",
        "ownerName": "张三",
        "parentName": "总公司",
        "memberQty": 10,
        "disableFlag": false,
        "createdAt": "2024-01-01T00:00:00+08:00"
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

### 3. 获取部门详情

**GET** `/bdm/department/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 部门 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "DEPT000001",
      "name": "研发部",
      "owner": {
        "id": 5,
        "code": "STAFF000001",
        "name": "张三"
      },
      "parent": {
        "id": 1,
        "code": "DEPT000000",
        "name": "总公司"
      }
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-01T00:00:00+08:00",
      "createdBy": {
        "id": 1,
        "nickname": "管理员"
      },
      "updatedBy": {
        "id": 1,
        "nickname": "管理员"
      }
    }
  }
}
```

---

### 4. 创建部门

**POST** `/bdm/department`

**请求体**

```json
{
  "code": "DEPT000002",
  "name": "市场部",
  "remark": "负责市场推广",
  "parentId": 1,
  "ownerId": 5,
  "disable_flag": false
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 部门编码，唯一 |
| name | string | ✅ | 部门名称，唯一 |
| remark | string | 否 | 备注 |
| parentId | int | 否 | 上级部门 ID |
| ownerId | int | 否 | 部门负责人（员工 ID） |
| disable_flag | boolean | 否 | 禁用状态，默认 false |

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

### 5. 更新部门

**PUT** `/bdm/department/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 部门 ID |

**请求体**

```json
{
  "code": "DEPT000002",
  "name": "市场部（更新）",
  "remark": "备注已更新",
  "parentId": 1,
  "ownerId": 5,
  "disable_flag": true
}
```

**响应示例**

```json
{
  "msg": "修改成功"
}
```

---

### 6. 批量部分更新部门

**PATCH** `/bdm/department/list`

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
| ids | array | ✅ | 部门 ID 列表 |
| disableFlag | boolean | 否 | 禁用状态 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 7. 批量删除部门

**DELETE** `/bdm/department/list`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 部门 ID 列表 |

**注意事项**

- 删除前会检查是否存在下级部门，如果存在则无法删除

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 8. 获取枚举数据

**GET** `/bdm/department/enums`

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
        "key": "BDM.add_department"
      },
      {
        "value": "VIEW",
        "label": "查看",
        "key": "BDM.view_department"
      },
      {
        "value": "CHANGE",
        "label": "修改",
        "key": "BDM.change_department"
      },
      {
        "value": "DELETE",
        "label": "删除",
        "key": "BDM.delete_department"
      },
      {
        "value": "DISABLE",
        "label": "禁用",
        "key": "BDM.disable_department"
      }
    ]
  }
}
```

---

### 9. 获取简化列表

**GET** `/bdm/department/simple`

只返回 `id`、`code`、`name` 三个字段，适用于下拉选择等场景。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "DEPT000001",
        "name": "研发部"
      },
      {
        "id": 2,
        "code": "DEPT000002",
        "name": "市场部"
      }
    ],
    "total": 2
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
      "\"DEPT000001\"已被使用，请更换部门编码后重试"
    ],
    "name": [
      "\"研发部\"已被使用，请更换部门名称后重试"
    ]
  }
}
```

```json
{
  "msg": "error",
  "errors": {
    "ids": [
      "删除失败，存在下级部门"
    ]
  }
}
```

---

## 完整 cURL 示例

```bash
# 1. 获取部门列表（分页）
curl -X GET "http://your-domain.com/bdm/department/list?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取部门详情
curl -X GET "http://your-domain.com/bdm/department/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建部门
curl -X POST "http://your-domain.com/bdm/department" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "code": "DEPT000002",
    "name": "市场部",
    "remark": "负责市场推广",
    "parentId": 1,
    "ownerId": 5,
    "disable_flag": false
  }'

# 4. 更新部门
curl -X PUT "http://your-domain.com/bdm/department/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "市场部（更新）",
    "remark": "备注已更新"
  }'

# 5. 批量部分更新
curl -X PATCH "http://your-domain.com/bdm/department/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3],
    "disableFlag": true
  }'

# 6. 批量删除
curl -X DELETE "http://your-domain.com/bdm/department/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3]
  }'

# 7. 获取枚举数据
curl -X GET "http://your-domain.com/bdm/department/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 8. 获取简化列表
curl -X GET "http://your-domain.com/bdm/department/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```