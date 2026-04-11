# API 接口详情模板参考

> 按需读取此文件。在生成"接口详情"章节时加载。

---

## LIST 接口模板

### {序号}. 获取{ModelName}列表

**GET** `/{app_name}`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 0 开始，默认 0 |
| page_size | int | 否 | 每页数量，默认 20 |
| {filter_field} | string | 否 | 按{字段说明}筛选 |

**响应示例**

```json
{
  "msg": "ok",
  "data": {
    "total": 100,
    "page": 0,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "{field}": "{value}",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

---

## CREATE 接口模板

### {序号}. 创建{ModelName}

**POST** `/{app_name}`

**请求体**

```json
{
  "{required_field}": "{value}",
  "{optional_field}": "{value}"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| {field} | string | ✅ | {说明} |
| {field} | string | 否 | {说明} |

**响应示例**

```json
{
  "msg": "ok",
  "data": {
    "id": 1,
    "{field}": "{value}"
  }
}
```

---

## RETRIEVE 接口模板

### {序号}. 获取{ModelName}详情

**GET** `/{app_name}/{id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | {ModelName} ID |

**响应示例**

```json
{
  "msg": "ok",
  "data": {
    "id": 1,
    "{field}": "{value}",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## UPDATE 接口模板

### {序号}. 更新{ModelName}

**PUT** `/{app_name}/{id}`

**请求体**

```json
{
  "{field}": "{new_value}"
}
```

**响应示例**

```json
{
  "msg": "ok",
  "data": {
    "id": 1,
    "{field}": "{new_value}"
  }
}
```

---

## BULK DELETE 接口模板

### {序号}. 批量删除{ModelName}

**DELETE** `/{app_name}`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**响应示例**

```json
{
  "msg": "ok",
  "data": null
}
```

---

## 自定义 Action 接口模板

### {序号}. {action描述}

**{METHOD}** `/{app_name}/{id}/{action}` 或 `/{app_name}/{action}`

**请求体 / Query 参数**（根据 method 决定）

```json
{
  "{field}": "{value}"
}
```

**响应示例**

```json
{
  "msg": "ok",
  "data": {
    "{field}": "{value}"
  }
}
```

---

## 嵌套对象响应示例

当序列化器包含嵌套关联对象时，展开完整结构：

```json
{
  "msg": "ok",
  "data": {
    "id": 1,
    "{field}": "{value}",
    "{nested_object}": {
      "id": 2,
      "{nested_field}": "{value}"
    },
    "{nested_list}": [
      {
        "id": 3,
        "{item_field}": "{value}"
      }
    ]
  }
}
```