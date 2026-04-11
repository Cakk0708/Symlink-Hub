# PSC - FileExtensionType 接口文档

> 最后更新：2026-03-21
> App: `PSC` | Model: `FileExtensionType`
> Base URL: `/psc/deliverable/file-extension-type`

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
| GET | `/psc/deliverable/file-extension-type` | 获取分页列表 | ✅ |
| GET | `/psc/deliverable/file-extension-type/list` | 获取分页列表 | ✅ |
| POST | `/psc/deliverable/file-extension-type` | 创建文件扩展名类型 | ✅ |
| POST | `/psc/deliverable/file-extension-type/list` | 创建文件扩展名类型 | ✅ |

---

## 接口详情

### 1. 获取分页列表

**GET** `/psc/deliverable/file-extension-type`

或

**GET** `/psc/deliverable/file-extension-type/list`

获取文件扩展名类型列表，支持搜索、分页、排序。

**Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 否 | - | 搜索关键词（匹配文件扩展名） |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |
| sortField | string | 否 | id | 排序字段 |
| sortOrder | string | 否 | asc | 排序方向（asc/desc） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "index": 1,
        "id": 1,
        "name": ".pdf"
      },
      {
        "index": 2,
        "id": 2,
        "name": ".docx"
      },
      {
        "index": 3,
        "id": 3,
        "name": ".xlsx"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 3,
      "totalPages": 1
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| index | int | 序号（当前页内的序号） |
| id | int | 文件扩展名类型 ID |
| name | string | 文件扩展名（如 .pdf、.docx） |
| pagination | object | 分页信息 |

**分页信息字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| pageNum | int | 当前页码 |
| pageSize | int | 每页数量 |
| total | int | 总记录数 |
| totalPages | int | 总页数 |

---

### 2. 创建文件扩展名类型

**POST** `/psc/deliverable/file-extension-type`

或

**POST** `/psc/deliverable/file-extension-type/list`

创建新的文件扩展名类型。

**请求体**

```json
{
  "name": ".pdf"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 文件扩展名（必须全局唯一，如 .pdf、.docx、.xlsx） |

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
  "msg": "参数错误",
  "errors": {
    "name": ["\".pdf\"已被使用，请更换名称后重试"]
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

---

## 完整 cURL 示例

```bash
# 1. 获取分页列表
curl -X GET "http://localhost:8001/psc/deliverable/file-extension-type?pageNum=1&pageSize=10&query=.pdf" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建文件扩展名类型
curl -X POST "http://localhost:8001/psc/deliverable/file-extension-type" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": ".pdf"
  }'

# 3. 搜索并排序
curl -X GET "http://localhost:8001/psc/deliverable/file-extension-type?query=doc&sortField=name&sortOrder=asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### FileExtensionType 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | string(50) | 文件扩展名（唯一，如 .pdf、.docx、.xlsx） |

### 表名

`PSC_file_extension_type`

---

## 设计说明

### 用途

文件扩展名类型用于管理交付物定义中允许的文件类型限制。

1. 在创建交付物定义时，可以通过 `allowedFileExtensionsIds` 字段关联多个文件扩展名类型
2. 用于验证用户上传的文件类型是否符合要求

### 命名规范

- 文件扩展名必须以 `.` 开头，如 `.pdf`、`.docx`、`.xlsx`
- 存储时会保持原始格式，不做大小写转换

### 唯一性约束

- `name` 字段全局唯一，不允许重复
- 创建时如果名称已存在，将返回错误提示

---

## 使用场景

### 1. 创建交付物定义时关联文件类型

在创建交付物定义时，可以指定允许的文件扩展名类型：

```json
{
  "name": "需求文档",
  "allowedFileExtensionsIds": [1, 2, 3],
  "isRequired": true
}
```

其中 `allowedFileExtensionsIds` 就是文件扩展名类型的 ID 列表。

### 2. 常见文件扩展名类型

| ID | name | 说明 |
|----|------|------|
| 1 | .pdf | PDF 文档 |
| 2 | .docx | Word 文档 |
| 3 | .xlsx | Excel 表格 |
| 4 | .pptx | PowerPoint 演示文稿 |
| 5 | .zip | 压缩文件 |
| 6 | .rar | RAR 压缩文件 |
| 7 | .jpg | 图片（JPEG） |
| 8 | .png | 图片（PNG） |