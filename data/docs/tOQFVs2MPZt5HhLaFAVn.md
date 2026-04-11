# PM - NodeListNote 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `NodeNote`
> Base URL: `/pm/nodelist`

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
| POST | `/{id}/note` | 添加节点笔记 | ✅ |

---

## 接口详情

### POST 添加节点笔记

为指定节点添加笔记。

#### 请求

```
POST /pm/nodelist/{id}/note
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

**请求体：**

```json
{
  "content": "这是一条节点笔记"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 笔记内容，不能为空 |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "content": "这是一条节点笔记",
    "createdAt": "2025-01-01T12:00:00+08:00",
    "createdBy": {
      "id": 123,
      "nickname": "张三",
      "avatar": "avatar_url"
    }
  }
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 笔记 ID |
| content | string | 笔记内容 |
| createdAt | string | 创建时间（ISO 8601） |
| createdBy | object | 创建人信息 |
| createdBy.id | integer | 创建人 ID |
| createdBy.nickname | string | 创建人昵称 |
| createdBy.avatar | string | 创建人头像 URL |

**错误响应（400 Bad Request）：**

```json
{
  "msg": "error",
  "data": {
    "添加笔记失败": "笔记内容不能为空"
  }
}
```

**错误响应（404 Not Found）：**

```json
{
  "msg": "error",
  "data": "节点不存在"
}
```

---

## 数据模型

### NodeNote 模型

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 主键 |
| content | TextField | 笔记内容 |
| created_by | ForeignKey | 创建人（SM.User） |
| created_at | DateTimeField | 创建时间 |
| node | ForeignKey | 关联节点（Project_Node） |

**约束：**
- 一个节点可以有多个笔记（一对多关系）
- 一个笔记只能属于一个节点
- 按创建时间倒序排列（最新的在前）

---

## 业务逻辑说明

1. **自动关联**：创建时自动关联当前用户和指定节点
2. **操作日志**：添加笔记时会自动记录项目操作日志
3. **日志格式**：`在 {节点名称} 节点添加了备注`
4. **内容验证**：笔记内容不能为空或仅包含空白字符

---

## 权限说明

- **添加笔记**：所有认证用户
- 节点必须存在才能添加笔记

---

## 完整 cURL 示例

```bash
# 添加节点笔记
curl -X POST "https://api.example.com/pm/nodelist/1/note" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "content": "这是一条节点笔记"
  }'
```
