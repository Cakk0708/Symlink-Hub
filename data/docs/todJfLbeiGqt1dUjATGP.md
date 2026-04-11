# PM - ProjectFolder 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `ProjectFolder`
> Base URL: `/pm/project`

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
| GET | `/project/{id}/folder` | 获取项目文件夹列表 | ✅ |

---

## 接口详情

### GET 获取项目文件夹列表

获取指定项目的文件夹列表及其包含的交付物信息。

#### 请求

```
GET /pm/project/{id}/folder
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 项目 ID |

**请求体：**

```json
{
  "project_id": int
}
```

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "folder_name",
        "deliverables": [
          {
            "id": 1,
            "name": "交付物名称",
            "version": "1.0",
            "fileCategory": "category_code",
            "state": "NORMAL",
            "createdAt": "2025-01-01T00:00:00+08:00",
            "createdBy": {
              "id": 1,
              "nickname": "用户昵称",
              "avatar": "头像URL"
            }
          }
        ]
      }
    ],
    "count": 10
  }
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| items | array | 文件夹列表 |
| items[].id | integer | 文件夹 ID |
| items[].name | string | 文件夹名称 |
| items[].deliverables | array | 交付物列表 |
| deliverables[].id | integer | 交付物实例 ID |
| deliverables[].name | string | 交付物名称 |
| deliverables[].version | string | 版本号 |
| deliverables[].fileCategory | string | 文件分类 |
| deliverables[].state | string | 交付物状态 |
| deliverables[].createdAt | string | 创建时间（ISO 8601） |
| deliverables[].createdBy | object | 创建人信息 |
| count | integer | 文件夹总数 |

**错误响应（400 Bad Request）：**

```json
{
  "msg": "参数错误",
  "data": {
    "project_id": ["项目不存在"]
  }
}
```

---

## 数据模型

### 文件夹类型（folder_type）

| 值 | 说明 |
|----|------|
| DELIVERABLE | 交付物文件夹 |
| CUSTOMER_ROOT | 客户根文件夹 |
| MODEL_ROOT | 机型根文件夹 |

### 交付物状态（state）

| 值 | 说明 |
|----|------|
| NORMAL | 正常 |
| FROZEN | 冻结 |
| INITIAL_FROZEN | 初始冻结 |
| STORAGE_MIGRATION_ERROR | 储存迁移异常 |
| REVIEW_REJECTED | 评审拒绝 |

---

## 业务逻辑说明

1. **文件夹过滤**：只返回 `DELIVERABLE` 类型的文件夹，排除 `CUSTOMER_ROOT` 和 `MODEL_ROOT`
2. **交付物匹配**：通过 `definition.deliverable_definition.code` 与文件夹 `name` 进行匹配
3. **时区处理**：所有时间字段自动转换为本地时区（Asia/Shanghai）

---

## 完整 cURL 示例

```bash
# 获取项目文件夹列表
curl -X GET "https://api.example.com/pm/project/1/folder" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1
  }'
```
