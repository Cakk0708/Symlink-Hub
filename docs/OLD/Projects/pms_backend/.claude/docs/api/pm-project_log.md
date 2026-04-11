# PM - ProjectLog 接口文档

> 最后更新：2026-03-24
> App: `PM` | Model: `Log`
> Base URL: `/pm/log`

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
| GET | `/pm/log` | 获取日志列表 | ✅ |
| GET | `/pm/log/progress` | 获取项目进展列表 | ✅ |
| POST | `/pm/log/progress` | 创建项目进展 | ✅ |

---

## 接口详情

### 1. 获取日志列表

**GET** `/pm/log`

**描述**

获取项目日志列表，支持按项目ID、日志类型筛选，支持分页。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | 否 | 项目 ID |
| type | int | 否 | 日志类型：0-操作记录，1-进展汇报，2-评价记录 |
| page_num | int | 否 | 页码，从 1 开始，默认 1 |
| page_size | int | 否 | 每页数量，默认 10，最大 100 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "content": "项目启动",
        "createdAt": "2026-03-16T10:30:00+08:00",
        "displayTime": "刚刚",
        "createdBy": {
          "id": 1,
          "avatar": "https://example.com/avatar.jpg",
          "nickname": "张三"
        }
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

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 日志 ID |
| content | string | 日志内容（评价记录仅对超管显示详情） |
| createdAt | string | 创建时间（ISO 8601 格式） |
| displayTime | string | 智能时间显示（刚刚/分钟前/小时前/天前/完整日期） |
| createdBy.id | int | 创建人 ID |
| createdBy.avatar | string | 创建人头像 URL |
| createdBy.nickname | string | 创建人昵称 |

---

### 2. 获取项目进展列表

**GET** `/pm/log/progress`

**描述**

获取项目进展汇报列表（type=1 的日志记录）。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| page_num | int | 否 | 页码，从 1 开始，默认 1 |
| page_size | int | 否 | 每页数量，默认 10，最大 100 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "content": "完成需求分析",
        "createdAt": "2026-03-16T10:30:00+08:00",
        "displayTime": "2小时前",
        "createdBy": {
          "id": 1,
          "avatar": "https://example.com/avatar.jpg",
          "nickname": "张三"
        }
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

### 3. 创建项目进展

**POST** `/pm/log/progress`

**描述**

创建一条项目进展汇报记录。

**请求体**

```json
{
  "projectId": 1,
  "content": "完成需求评审"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectId | int | ✅ | 项目 ID |
| content | string | ✅ | 进展内容，最大长度 1000 |

**响应示例**

```json
{
  "msg": "success",
  "code": 0
}
```

**错误响应示例**

```json
{
  "msg": "项目不存在"
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

---

## 数据模型

### Log 日志模型

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 日志 ID（自增主键） |
| content | string | 日志内容，最大长度 1000 |
| type | int | 类型：0-操作记录，1-进展汇报，2-评价记录 |
| project | int (FK) | 关联项目 ID（外键至 PM.Project_List） |
| operator | int (FK) | 操作人 ID（外键至 SM.User） |
| create_time | datetime | 创建时间（自动添加） |
| content_detail | json | 内容详情（评价记录使用） |

**数据库表名：** `PM_log_list`

---

## 完整 cURL 示例

```bash
# 1. 获取日志列表
curl -X GET "http://localhost:8001/pm/log?projectId=1&pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取项目进展列表
curl -X GET "http://localhost:8001/pm/log/progress?projectId=1&pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建项目进展
curl -X POST "http://localhost:8001/pm/log/progress" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectId": 1,
    "content": "完成需求评审"
  }'
```

---

## 业务规则

1. **时间显示规则**
   - 1 分钟内：显示"刚刚"
   - 1 小时内：显示"X分钟前"
   - 1 天内：显示"X小时前"
   - 7 天内：显示"X天前"
   - 7 天以上：显示完整时间

2. **评价记录隐私**
   - type=2 的评价记录，仅超级管理员可查看详细内容
   - 普通用户看到的创建人显示为"智慧岭阳"

3. **分页默认值**
   - page_num 默认为 1
   - page_size 默认为 10，最大 100
