# PSC - HardwareSpec 接口文档

> 最后更新：2026-03-20
> App: `PSC` | Model: `HardwareSpec`, `HardwareSpecChild`
> Base URL: `/PSC/hardware`

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
| GET | `/hardware/spec` | 获取硬件规格列表 | ✅ |
| POST | `/hardware/spec` | 创建硬件规格 | ✅ |
| GET | `/hardware/spec/<action>` | 获取硬件规格详情 | ✅ |
| PUT | `/hardware/spec` | 更新硬件规格 | ✅ |
| PATCH | `/hardware/spec/<action>` | 批量禁用/启用硬件规格 | ✅ |
| DELETE | `/hardware/spec/<action>` | 批量删除硬件规格 | ✅ |
| GET | `/hardware/version` | 获取可用硬件规格列表（PMS使用） | ✅ |
| GET | `/hardware/version/<action>` | 获取硬件规格版本详情 | ✅ |

---

## 接口详情

### 1. 获取硬件规格列表

**GET** `/hardware/spec`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | int | 否 | 硬件分类ID |
| name | string | 否 | 硬件名称（模糊搜索） |
| state | string | 否 | 硬件状态（AVAILABLE/UNAVAILABLE） |
| pageNum | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| pageSort | string | 否 | 排序，默认 `ID:DESC` |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "STM32F103",
      "category": 1,
      "category_name": "MCU",
      "state": "AVAILABLE",
      "remark": "常用MCU",
      "create_time": "2026-01-01T00:00:00+08:00",
      "creator": "admin"
    }
  ],
  "total": 100
}
```

---

### 2. 创建硬件规格

**POST** `/hardware/spec`

**权限要求**：`PM.add_hardware_spec`

**请求体**

```json
{
  "name": "STM32F407",
  "category": 1,
  "remark": "高性能MCU",
  "version_list": [
    {
      "id": "",
      "version": "1.0",
      "remark": "初始版本",
      "state": "AVAILABLE"
    }
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 硬件名称 |
| category | int | ✅ | 硬件分类ID |
| remark | string | 否 | 备注 |
| version_list | array | 否 | 硬件版本列表 |

**version_list 参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 否 | 版本ID（更新时必填） |
| version | string | ✅ | 版本号（格式：1.0 或 1.2.3） |
| remark | string | 否 | 版本备注 |
| state | string | 否 | 版本状态 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1,
    "id": 1,
    "name": "STM32F407",
    "category": 1,
    "category_name": "MCU",
    "state": "AVAILABLE",
    "remark": "高性能MCU",
    "create_time": "2026-01-01T00:00:00+08:00",
    "creator": "admin",
    "versions": [
      {
        "id": 1,
        "version": "1.0",
        "remark": "初始版本",
        "state": "AVAILABLE",
        "use": 0,
        "create_time": "2026-01-01T00:00:00+08:00",
        "creator": "admin"
      }
    ]
  }
}
```

---

### 3. 获取硬件规格详情

**GET** `/hardware/spec/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件规格ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "name": "STM32F407",
    "category": 1,
    "category_name": "MCU",
    "state": "AVAILABLE",
    "remark": "高性能MCU",
    "create_time": "2026-01-01T00:00:00+08:00",
    "creator": "admin",
    "versions": [
      {
        "id": 1,
        "version": "1.0",
        "remark": "初始版本",
        "state": "AVAILABLE",
        "use": 5,
        "create_time": "2026-01-01T00:00:00+08:00",
        "creator": "admin"
      }
    ]
  }
}
```

---

### 4. 更新硬件规格

**PUT** `/hardware/spec`

**权限要求**：`PM.change_hardware_spec`

**请求体**

```json
{
  "id": 1,
  "name": "STM32F407",
  "category": 1,
  "state": "AVAILABLE",
  "remark": "高性能MCU",
  "version_list": [
    {
      "id": 1,
      "version": "1.0",
      "remark": "初始版本",
      "state": "AVAILABLE"
    },
    {
      "id": "",
      "version": "2.0",
      "remark": "升级版本",
      "state": "AVAILABLE"
    }
  ]
}
```

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

---

### 5. 批量禁用/启用硬件规格

**PATCH** `/hardware/spec/<ids>`

**权限要求**：`PM.disable_hardware_spec`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| ids | string | 逗号分隔的硬件规格ID，如 `1,2,3` |

**请求体**

```json
{
  "state": "UNAVAILABLE"
}
```

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "updated_count": 3
  }
}
```

---

### 6. 批量删除硬件规格

**DELETE** `/hardware/spec/<ids>`

**权限要求**：`PM.delete_hardware_spec`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| ids | string | 逗号分隔的硬件规格ID，如 `1,2,3` |

**响应示例**

```json
{
  "msg": "success",
  "data": ""
}
```

**错误响应示例**

```json
{
  "msg": "删除失败，共发现 1 个错误",
  "errors": [
    {
      "删除失败": "版本 1.0 已被项目使用，无法删除"
    }
  ]
}
```

---

### 7. 获取可用硬件规格列表（PMS使用）

**GET** `/hardware/version`

**说明**：仅返回状态为 `AVAILABLE` 的硬件规格，按使用次数降序排序

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | int | 否 | 硬件分类ID |
| name | string | 否 | 硬件名称（模糊搜索） |
| pageNum | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "STM32F407",
      "category": 1,
      "category_name": "MCU",
      "state": "AVAILABLE",
      "remark": "高性能MCU",
      "versions": [
        {
          "id": 1,
          "version": "1.0",
          "remark": "初始版本"
        }
      ]
    }
  ],
  "total": 50
}
```

---

### 8. 获取硬件规格版本详情（PMS使用）

**GET** `/hardware/version/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件规格ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "name": "STM32F407",
    "category": 1,
    "category_name": "MCU",
    "state": "AVAILABLE",
    "remark": "高性能MCU",
    "versions": [
      {
        "id": 1,
        "version": "1.0",
        "remark": "初始版本"
      },
      {
        "id": 2,
        "version": "2.0",
        "remark": "升级版本"
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

**权限错误响应**

```json
{
  "detail": "您没有执行该操作的权限"
}
```

---

## 数据模型

### HardwareSpec

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件规格ID |
| code | string | 唯一编码（自动生成） |
| name | string | 硬件名称 |
| category | int | 硬件分类ID |
| state | string | 硬件状态（AVAILABLE/UNAVAILABLE） |
| remark | string | 备注 |
| creator | string | 创建人用户名 |
| create_time | datetime | 创建时间 |

### HardwareSpecChild

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 版本ID |
| spec | int | 所属硬件规格ID |
| version | string | 版本号 |
| remark | string | 备注 |
| state | string | 版本状态（AVAILABLE/UNAVAILABLE） |
| use | int | 使用次数 |
| original_id | int | 原始版本ID |
| creator | string | 创建人用户名 |
| create_time | datetime | 创建时间 |

---

## 权限说明

| 权限代码 | 权限名称 | 说明 |
|---------|---------|------|
| PM.add_hardware_spec | 创建硬件规格 | 创建新硬件规格 |
| PM.view_hardware_spec | 查看硬件规格 | 查看硬件规格列表和详情 |
| PM.change_hardware_spec | 修改硬件规格 | 修改硬件规格信息 |
| PM.delete_hardware_spec | 删除硬件规格 | 删除硬件规格 |
| PM.disable_hardware_spec | 禁用硬件规格 | 批量禁用/启用硬件规格 |

---

## 完整 cURL 示例

```bash
# 1. 获取硬件规格列表
curl -X GET "http://your-domain.com/PSC/hardware/spec?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建硬件规格
curl -X POST "http://your-domain.com/PSC/hardware/spec" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "STM32F407",
    "category": 1,
    "remark": "高性能MCU",
    "version_list": [
      {
        "version": "1.0",
        "remark": "初始版本"
      }
    ]
  }'

# 3. 获取硬件规格详情
curl -X GET "http://your-domain.com/PSC/hardware/spec/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 更新硬件规格
curl -X PUT "http://your-domain.com/PSC/hardware/spec" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 1,
    "name": "STM32F407",
    "category": 1,
    "state": "AVAILABLE",
    "remark": "高性能MCU"
  }'

# 5. 批量禁用硬件规格
curl -X PATCH "http://your-domain.com/PSC/hardware/spec/1,2,3" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"state": "UNAVAILABLE"}'

# 6. 批量删除硬件规格
curl -X DELETE "http://your-domain.com/PSC/hardware/spec/1,2,3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. 获取可用硬件规格列表（PMS使用）
curl -X GET "http://your-domain.com/PSC/hardware/version?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
