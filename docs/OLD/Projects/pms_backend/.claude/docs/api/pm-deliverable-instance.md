# PM - DeliverableInstance 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `DeliverableInstance`
> Base URL: `/api/deliverables`

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
| POST | `/instances` | 创建交付物实例 | ✅ |
| GET | `/instances/{deliverable_id}` | 获取交付物详情（下载链接） | ✅ |
| PATCH | `/instances/{deliverable_id}` | 更新交付物 | ✅ |
| DELETE | `/instances/{deliverable_id}` | 删除交付物 | ✅ |
| POST | `/instances/{deliverable_id}/reupload` | 重新上传交付物（评审拒绝后） | ✅ |

---

## 接口详情

### 1. 创建交付物实例

**POST** `/instances`

**请求体**

```json
{
  "projectNodeId": 1,
  "definitionId": 1,
  "nodeDefinitionDeliverableMappingId": 1,
  "fileId": 1,
  "url": "https://example.com/doc.pdf",
  "version": "v1.0",
  "remark": "备注信息"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectNodeId | int | ✅ | 项目节点 ID |
| definitionId | int | ✅ | 交付物版本 ID |
| nodeDefinitionDeliverableMappingId | int | ✅ | 节点交付物映射 ID |
| fileId | int | 否 | 交付物文件 ID |
| url | string | 否 | 外部链接（最大长度 2000） |
| version | string | 否 | 文件版本（最大长度 255） |
| remark | string | 否 | 备注信息（最大长度 255） |

**业务规则**

- 用户必须有上传权限（通过节点和部门验证）
- 只读交付物不允许创建
- 相同 project_node + definition 下 version 不能重复

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 123
  }
}
```

---

### 2. 获取交付物详情（下载链接）

**GET** `/instances/{deliverable_id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| container | string | 否 | 运行容器标识。传入 `feishu` 时，返回的 URL 会补充飞书 applink 前缀以在客户端内打开 |

**业务规则**

- **冻结状态检查**：只有交付物创建者可访问 INITIAL_FROZEN 状态
- **权限检查**：超级用户、创建者、节点负责人、同部门用户可访问
- **文件验证**：验证飞书文件是否存在，并自动授予访问权限
- 对于飞书文件，会自动授予用户相应的查看或编辑权限

**响应示例**

普通请求：

```json
{
  "msg": "success",
  "data": {
    "id": 123,
    "url": "https://feishu.cn/document/docx/xxxxx"
  }
}
```

飞书容器内请求（`?container=feishu`）：

```json
{
  "msg": "success",
  "data": {
    "id": 123,
    "url": "https://applink.feishu.cn/client/web_url/open?mode=appCenter&url=https://feishu.cn/document/docx/xxxxx"
  }
}
```

---

### 3. 更新交付物

**PATCH** `/instances/{deliverable_id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**请求体**

```json
{
  "fileId": 2,
  "version": "v2.0",
  "remark": "更新后的备注",
  "url": "https://example.com/updated-doc.pdf"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | int | 否 | 新的交付物文件 ID |
| version | string | 否 | 更新版本号 |
| remark | string | 否 | 更新备注 |
| url | string | 否 | 更新外部链接 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 123,
    "version": "v2.0",
    "state": "NORMAL",
    "url": "https://example.com/updated-doc.pdf"
  }
}
```

---

### 4. 删除交付物

**DELETE** `/instances/{deliverable_id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**业务规则**

- 节点完成后不允许删除交付物
- 节点首次完成后删除交付物需要管理员或项目负责人权限
- 只有创建者、项目负责人、超级管理员可删除

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 5. 重新上传交付物

**POST** `/instances/{deliverable_id}/reupload`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**业务规则**

- 只有状态为 `REVIEW_REJECTED`（评审拒绝）的交付物才能重新上传
- 只有交付物创建者、项目负责人或超级管理员才能执行此操作
- 操作成功后交付物状态将变更为 `NORMAL`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 123,
    "state": "NORMAL"
  }
}
```

---

## 数据模型

### DeliverableInstance

交付物实例模型，只负责业务逻辑，文件存储相关字段已迁移到 DeliverableFile 模型。

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 ID |
| project_node | ForeignKey | 项目节点 |
| definition | ForeignKey | 交付物版本 |
| node_deliverable_mapping | ForeignKey | 节点交付物映射 |
| created_by | ForeignKey | 创建人 |
| file | ForeignKey | 交付物文件（可为空） |
| version | string | 文件版本 |
| remark | string | 备注 |
| url | string | 外部链接 |
| state | string | 状态 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**关联属性（从 DeliverableFile 获取）**

| 属性 | 类型 | 说明 |
|------|------|------|
| name | string | 文件名称 |
| size | int | 文件大小 |
| category | string | 文件类型 |
| token | string | 文件唯一标识（从飞书子表获取） |
| folder | string | 文件夹路径（从飞书子表获取） |
| path | string | 文件路径（从飞书子表获取） |

---

## 交付物状态枚举

| 状态值 | 显示名称 | 说明 |
|--------|----------|------|
| NORMAL | 正常 | 交付物正常可用 |
| FROZEN | 冻结 | 交付物已被冻结 |
| INITIAL_FROZEN | 初始冻结 | 新上传的交付物，等待异步处理 |
| STORAGE_MIGRATION_ERROR | 储存迁移异常 | 上传交付物储存迁移异常 |
| REVIEW_REJECTED | 评审拒绝 | 评审项拒绝后交付物状态 |

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
| 400 | 请求参数错误或业务规则验证失败 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限 |
| 404 | 交付物不存在 |
| 500 | 服务器内部错误 |

**常见业务错误**

| 错误信息 | 场景 |
|----------|------|
| 权限不匹配 | 用户无上传权限 |
| 该交付物是只读的，不允许创建 | 只读交付物 |
| 该节点下已存在版本 {version} 的交付物 | 版本重复 |
| 交付物已冻结 | 尝试访问冻结状态的交付物 |
| 节点已完成，无法删除交付物 | 删除已完成节点的交付物 |
| 只有评审拒绝状态的交付物才能重新上传 | 重新上传状态不正确 |

---

## 完整 cURL 示例

```bash
# 1. 创建交付物
curl -X POST "http://your-domain/api/deliverables/instances" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectNodeId": 1,
    "definitionId": 1,
    "nodeDefinitionDeliverableMappingId": 1,
    "fileId": 1,
    "version": "v1.0",
    "remark": "初版交付物"
  }'

# 2. 获取交付物详情（下载链接）
curl -X GET "http://your-domain/api/deliverables/instances/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 更新交付物
curl -X PATCH "http://your-domain/api/deliverables/instances/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "version": "v2.0",
    "remark": "更新版本"
  }'

# 4. 删除交付物
curl -X DELETE "http://your-domain/api/deliverables/instances/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 重新上传交付物（评审拒绝后）
curl -X POST "http://your-domain/api/deliverables/instances/123/reupload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
