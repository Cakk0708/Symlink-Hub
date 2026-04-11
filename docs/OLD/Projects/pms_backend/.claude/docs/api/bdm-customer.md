# BDM - Customer 接口文档

> 最后更新：2026-03-19
> App: `BDM` | Model: `Customer`
> Base URL: `/bdm/customer`

---

## 认证说明

当前所有接口使用 `AllowAny` 权限，无需认证即可访问。

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/bdm/customer/enums` | 获取枚举数据 | ❌ |
| GET | `/bdm/customer/simple` | 获取简化列表 | ❌ |
| GET | `/bdm/customer/list` | 获取分页列表 | ❌ |
| POST | `/bdm/customer/list` | 创建客户 | ❌ |
| PATCH | `/bdm/customer/list` | 批量部分更新 | ❌ |
| DELETE | `/bdm/customer/list` | 批量删除 | ❌ |
| GET | `/bdm/customer/<id>` | 获取详情 | ❌ |
| PUT | `/bdm/customer/<id>` | 完整更新 | ❌ |

---

## 接口详情

### 1. 获取枚举数据

**GET** `/bdm/customer/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "choices": {
      "region": [
        {"value": 0, "label": "北京市"},
        {"value": 1, "label": "天津市"},
        {"value": 2, "label": "河北省"},
        {"value": 3, "label": "山西省"},
        {"value": 4, "label": "内蒙古自治区"},
        {"value": 5, "label": "辽宁省"},
        {"value": 6, "label": "吉林省"},
        {"value": 7, "label": "黑龙江省"},
        {"value": 8, "label": "上海市"},
        {"value": 9, "label": "江苏省"},
        {"value": 10, "label": "浙江省"},
        {"value": 11, "label": "安徽省"},
        {"value": 12, "label": "福建省"},
        {"value": 13, "label": "江西省"},
        {"value": 14, "label": "山东省"},
        {"value": 15, "label": "河南省"},
        {"value": 16, "label": "湖北省"},
        {"value": 17, "label": "湖南省"},
        {"value": 18, "label": "广东省"},
        {"value": 19, "label": "广西壮族自治区"},
        {"value": 20, "label": "海南省"},
        {"value": 21, "label": "重庆市"},
        {"value": 22, "label": "四川省"},
        {"value": 23, "label": "贵州省"},
        {"value": 24, "label": "云南省"},
        {"value": 25, "label": "西藏自治区"},
        {"value": 26, "label": "陕西省"},
        {"value": 27, "label": "甘肃省"},
        {"value": 28, "label": "青海省"},
        {"value": 29, "label": "宁夏回族自治区"},
        {"value": 30, "label": "新疆维吾尔自治区"},
        {"value": 31, "label": "台湾省"},
        {"value": 32, "label": "香港特别行政区"},
        {"value": 33, "label": "澳门特别行政区"}
      ],
      "disable_flag": [
        {"value": true, "label": "禁用"},
        {"value": false, "label": "启用"}
      ]
    },
    "permissions": [
      {"value": "CREATE", "label": "创建", "key": "BDM.add_customer"},
      {"value": "VIEW", "label": "查看", "key": "BDM.view_customer"},
      {"value": "CHANGE", "label": "修改", "key": "BDM.change_customer"},
      {"value": "DELETE", "label": "删除", "key": "BDM.delete_customer"},
      {"value": "DISABLE", "label": "禁用", "key": "BDM.disable_customer"}
    ]
  }
}
```

---

### 2. 获取简化列表

**GET** `/bdm/customer/simple`

获取所有客户的简化信息，仅返回 `id`、`code`、`name`、`namePinyin` 字段。适用于下拉选择等场景。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "CUST001",
        "name": "客户A",
        "namePinyin": ["ke", "hu", "A"]
      },
      {
        "id": 2,
        "code": "CUST002",
        "name": "客户B",
        "namePinyin": ["ke", "hu", "B"]
      }
    ],
    "total": 2
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 客户 ID |
| code | string | 客户编码（唯一） |
| name | string | 客户名称（唯一） |
| namePinyin | array[string] | 客户名称拼音数组 |

---

### 3. 获取分页列表

**GET** `/bdm/customer/list`

**Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 否 | - | 搜索关键词（匹配客户编码、名称、代号） |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |
| sortField | string | 否 | id | 排序字段 |
| sortOrder | string | 否 | desc | 排序方向（asc/desc） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "index": 1,
        "primaryId": 1,
        "code": "CUST001",
        "name": "客户A",
        "aliasCode": "A001",
        "namePinyin": ["ke", "hu", "A"],
        "region": {
          "value": 0,
          "label": "分组A"
        },
        "disableFlag": false,
        "createdAt": "2024-01-01T00:00:00+08:00"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 100,
      "totalPages": 10
    }
  }
}
```

---

### 4. 创建客户

**POST** `/bdm/customer/list`

**请求体**

```json
{
  "code": "CUST001",
  "name": "客户A",
  "aliasCode": "A001",
  "remark": "备注信息",
  "region": 0,
  "disable_flag": false
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 客户编码（唯一，不传则自动生成） |
| name | string | ✅ | 客户名称（唯一） |
| aliasCode | string | 否 | 客户代号（唯一） |
| remark | string | 否 | 备注 |
| region | int | 否 | 客户分组（枚举值） |
| disable_flag | boolean | 否 | 禁用状态 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

**错误响应示例**

```json
{
  "msg": "\"CUST001\"已被使用，请更换客户编码后重试",
  "errors": {
    "code": ["\"CUST001\"已被使用，请更换客户编码后重试"]
  }
}
```

---

### 5. 批量部分更新

**PATCH** `/bdm/customer/list`

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
| ids | array[int] | ✅ | 客户 ID 列表 |
| disableFlag | boolean | 否 | 新的禁用状态 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 6. 批量删除

**DELETE** `/bdm/customer/list`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array[int] | ✅ | 客户 ID 列表 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "数据验证失败",
  "errors": {
    "客户A": "客户已被项目关联，无法删除"
  }
}
```

---

### 7. 获取详情

**GET** `/bdm/customer/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 客户 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "CUST001",
      "name": "客户A",
      "aliasCode": "A001",
      "namePinyin": ["ke", "hu", "A"],
      "region": {
        "value": 0,
        "label": "分组A"
      },
      "remark": "备注信息",
      "disableFlag": false
    },
    "others": {
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-01-01 00:00:00",
      "createdBy": {
        "id": 1,
        "nickname": "创建人"
      },
      "updatedBy": {
        "id": 2,
        "nickname": "修改人"
      }
    }
  }
}
```

**错误响应示例**

```json
{
  "msg": "客户 ID \"999\" 不存在",
  "data": null
}
```

---

### 8. 完整更新

**PUT** `/bdm/customer/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 客户 ID |

**请求体**

```json
{
  "code": "CUST001",
  "name": "客户A",
  "aliasCode": "A001",
  "remark": "备注信息",
  "region": 0,
  "disable_flag": false
}
```

**响应示例**

```json
{
  "msg": "修改成功"
}
```

**错误响应示例**

```json
{
  "msg": "error",
  "errors": {
    "name": ["\"客户A\"已被使用，请更换客户名称后重试"]
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
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取简化列表
curl -X GET "http://localhost:8001/bdm/customer/simple"

# 2. 获取分页列表
curl -X GET "http://localhost:8001/bdm/customer/list?pageNum=1&pageSize=10&query=客户"

# 3. 创建客户
curl -X POST "http://localhost:8001/bdm/customer/list" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CUST001",
    "name": "客户A",
    "aliasCode": "A001"
  }'

# 4. 获取详情
curl -X GET "http://localhost:8001/bdm/customer/1"

# 5. 完整更新
curl -X PUT "http://localhost:8001/bdm/customer/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "客户A（更新）"
  }'

# 6. 批量部分更新
curl -X PATCH "http://localhost:8001/bdm/customer/list" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3],
    "disableFlag": true
  }'

# 7. 批量删除
curl -X DELETE "http://localhost:8001/bdm/customer/list" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3]
  }'

# 8. 获取枚举数据
curl -X GET "http://localhost:8001/bdm/customer/enums"
```

---

## 数据模型

### Customer 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string(255) | 客户编码（唯一） |
| name | string(255) | 客户名称（唯一） |
| alias_code | string(50) | 客户代号（唯一，可空） |
| name_pinyin | JSON | 客户名称拼音数组 |
| remark | string(255) | 备注 |
| disable_flag | boolean | 禁用状态 |
| region | int | 客户分组（枚举） |
| creator | FK(User) | 创建人 |
| updated_by | FK(User) | 最后修改人 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 最后修改时间 |

### 表名

`BDM_customer`
