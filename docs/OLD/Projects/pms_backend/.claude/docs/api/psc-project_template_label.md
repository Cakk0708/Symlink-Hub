# PSC - ProjectTemplateLabel 接口文档

> 最后更新：2026-03-21
> App: `PSC` | Model: `ProjectTemplateLabel`
> Base URL: `/psc/project/template/labels`

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
| GET | `/psc/project/template/labels` | 获取项目标签列表（分页） | ✅ |
| POST | `/psc/project/template/labels` | 创建项目标签 | ✅ |

---

## 接口详情

### 1. 获取项目标签列表

**GET** `/psc/project/template/labels`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNum | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| pageSort | string | 否 | 排序字段和方向，格式：`字段:ASC/DESC`，默认 `createdAt:DESC`。支持字段：`createdAt`、`name`、`code` |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "PROJ_LABEL000001",
        "name": "研发项目",
        "createdAt": "2024-01-01T00:00:00+08:00",
        "createdBy": "张三"
      },
      {
        "id": 2,
        "code": "PROJ_LABEL000002",
        "name": "市场项目",
        "createdAt": "2024-01-02T00:00:00+08:00",
        "createdBy": "李四"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

---

### 2. 创建项目标签

**POST** `/psc/project/template/labels`

**请求体**

```json
{
  "name": "测试项目标签"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 唯一编码，不填时自动生成（前缀：PROJ_LABEL） |
| name | string | ✅ | 标签名称，全局唯一 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 3
  }
}
```

**错误响应示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "name": [
      ""研发项目"已被使用，请更换名称后重试"
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

---

## 完整 cURL 示例

```bash
# 1. 获取项目标签列表
curl -X GET "http://your-domain/psc/project/template/labels?pageNum=1&pageSize=10&pageSort=createdAt:DESC" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建项目标签
curl -X POST "http://your-domain/psc/project/template/labels" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"新项目标签"}'

# 3. 创建项目标签（指定编码）
curl -X POST "http://your-domain/psc/project/template/labels" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"code":"PROJ_LABEL_CUSTOM001","name":"自定义标签"}'
```

---

## 数据模型

### ProjectTemplateLabel

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 ID |
| code | string | 唯一编码，自动生成或手动指定 |
| name | string | 标签名称，全局唯一 |
| createdBy | string | 创建人昵称 |
| createdAt | datetime | 创建时间 |

### ProjectTemplateLabelMapping

标签与项目模板的多对多映射关系。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 ID |
| project_template_label | ForeignKey | 关联 ProjectTemplateLabel |
| project_template | ForeignKey | 关联 ProjectTemplate |

---

## 业务说明

1. **编码规则**：code 字段默认自动生成，格式为 `PROJ_LABEL` + 6位数字序码
2. **唯一性约束**：
   - `code` 字段全局唯一
   - `name` 字段全局唯一
3. **缓存机制**：创建/更新标签后会触发缓存更新（`cache_update_template_labels`）
4. **分页排序**：支持按 `createdAt`、`name`、`code` 字段升序或降序排序
