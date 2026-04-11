# PM - DeliverableInstance 接口文档

> 最后更新：2026-04-11
> App: `PM` | Model: `DeliverableInstance`
> Base URL: `/pm/deliverable`

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
| GET | `/instances/{deliverable_id}` | 获取交付物详情/下载链接 | ✅ |
| PATCH | `/instances/{deliverable_id}` | 更新交付物 | ✅ |
| DELETE | `/instances/{deliverable_id}` | 删除交付物 | ✅ |
| POST | `/instances/{deliverable_id}/freeze` | 冻结/解冻交付物 | ✅ |
| POST | `/instances/{deliverable_id}/reupload` | 重新上传交付物 | ✅ |
| POST | `/file/upload` | 上传交付物文件 | ✅ |
| POST | `/file/template` | 创建飞书模板文件 | ✅ |

---

## 接口详情

### 1. 创建交付物实例

**POST** `/instances`

创建项目节点交付物实例，关联文件或外部链接。

**请求体**

```json
{
  "projectNodeId": 123,
  "definitionId": 456,
  "nodeDefinitionDeliverableMappingId": 789,
  "fileId": 321,
  "url": "https://example.com/file.pdf",
  "version": "v1.0",
  "remark": "项目需求文档"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectNodeId | int | ✅ | 项目节点 ID |
| definitionId | int | ✅ | 交付物定义版本 ID |
| nodeDefinitionDeliverableMappingId | int | ✅ | 节点交付物映射 ID |
| fileId | int | 否 | 交付物文件 ID（与 url 二选一） |
| url | string | 否 | 外部链接 URL（与 fileId 二选一） |
| version | string | 否 | 文件版本号 |
| remark | string | 否 | 备注说明 |

**业务规则**

- 用户必须具备该节点上传权限
- 相同 `projectNode + definition` 下 `version` 不能重复
- 只读交付物不允许创建

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1001
  }
}
```

**HTTP 状态码**

| 状态码 | 说明 |
|--------|------|
| 201 | 创建成功 |
| 400 | 请求参数错误或权限不足 |

---

### 2. 获取交付物详情/下载链接

**GET** `/instances/{deliverable_id}`

获取交付物的下载链接，包含权限验证和飞书文件权限分配。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| container | string | 否 | 运行容器标识。传入 `feishu` 时，返回的 URL 会补充飞书 applink 前缀以在客户端内打开 |

**权限要求**

- 超级管理员可下载任何状态交付物
- 交付物创建者可下载 NORMAL 和 INITIAL_FROZEN 状态
- 通过 DeliverableAuthorityVerifier 验证拥有项目级或交付物级权限的用户可下载
  - 权限码：`pm.deliverable.can_edit`（编辑）、`pm.deliverable.can_view`（查看）

**响应示例**

普通请求：

```json
{
  "msg": "success",
  "data": {
    "id": 1001,
    "url": "https://feishu.cn/docx/ABC123"
  }
}
```

飞书容器内请求（`?container=feishu`）：

```json
{
  "msg": "success",
  "data": {
    "id": 1001,
    "url": "https://applink.feishu.cn/client/web_url/open?mode=appCenter&url=https://feishu.cn/docx/ABC123"
  }
}
```

**错误响应**

```json
{
  "交付物不可访问": "交付物状态为\"评审拒绝\"，无法下载"
}
```

```json
{
  "权限不足": "您没有权限下载此交付物"
}
```

---

### 3. 更新交付物

**PATCH** `/instances/{deliverable_id}`

更新交付物的文件、版本号、备注或外部链接。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**请求体**

```json
{
  "fileId": 322,
  "version": "v1.1",
  "remark": "更新后的需求文档",
  "url": "https://example.com/updated.pdf"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | int | 否 | 新的文件 ID |
| version | string | 否 | 版本号 |
| remark | string | 否 | 备注说明 |
| url | string | 否 | 外部链接 URL |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1001,
    "version": "v1.1",
    "state": "NORMAL",
    "url": "https://example.com/updated.pdf"
  }
}
```

---

### 4. 删除交付物

**DELETE** `/instances/{deliverable_id}`

删除指定的交付物实例。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**业务规则**

- 节点已完成时无法删除交付物
- 节点首次完成后删除交付物需要管理员权限
- 只有创建者、项目负责人、超级管理员可删除

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应**

```json
{
  "删除失败": "节点已完成，无法删除交付物"
}
```

```json
{
  "删除失败": "您没有权限删除该交付物"
}
```

---

### 5. 冻结/解冻交付物

**POST** `/instances/{deliverable_id}/freeze`

冻结或解冻指定的交付物，冻结后交付物无法被下载或访问。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**请求体**

```json
{
  "action": "freeze",
  "reason": "文件需要重新审核"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | ✅ | 操作类型：`freeze`（冻结）/ `unfreeze`（解冻） |
| reason | string | 否 | 冻结原因 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 6. 重新上传交付物

**POST** `/instances/{deliverable_id}/reupload`

将评审拒绝状态（`REVIEW_REJECTED`）的交付物重新切换为正常状态（`NORMAL`）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| deliverable_id | int | 交付物实例 ID |

**业务规则**

- 交付物状态必须为 `REVIEW_REJECTED`
- 只有交付物创建者、项目负责人、超级管理员可操作

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1001,
    "state": "NORMAL"
  }
}
```

**错误响应**

```json
{
  "状态错误": "只有评审拒绝状态的交付物才能重新上传，当前状态为\"正常\""
}
```

```json
{
  "权限不足": "只有交付物创建者、项目负责人或超级管理员才能重新上传"
}
```

---

### 7. 上传交付物文件

**POST** `/file/upload`

上传文件到飞书或本地存储，返回文件 ID 用于创建交付物实例。

**请求体**

```json
{
  "file": "base64_encoded_content",
  "name": "需求文档.pdf",
  "category": "docx",
  "size": 1024000
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | string | ✅ | 文件内容（Base64 编码）或文件对象 |
| name | string | ✅ | 文件名 |
| category | string | ✅ | 文件类型（docx/sheet/pdf 等） |
| size | int | ✅ | 文件大小（字节） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 321,
    "name": "需求文档.pdf",
    "token": "feishu_token_abc123"
  }
}
```

---

### 8. 创建飞书模板文件

**POST** `/file/template`

基于飞书模板创建新的文档实例。

**请求体**

```json
{
  "templateId": "tpl_abc123",
  "name": "项目需求文档_v1.0"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| templateId | string | ✅ | 飞书模板 ID |
| name | string | ✅ | 新文件名称 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 322,
    "name": "项目需求文档_v1.0",
    "url": "https://feishu.cn/docx/xyz789"
  }
}
```

---

## 数据模型

### DeliverableInstance 状态枚举

| 状态值 | 说明 |
|--------|------|
| `NORMAL` | 正常 |
| `FROZEN` | 冻结 |
| `INITIAL_FROZEN` | 初始冻结（新上传等待异步处理） |
| `STORAGE_MIGRATION_ERROR` | 储存迁移异常 |
| `REVIEW_REJECTED` | 评审拒绝 |

### DeliverableInstance 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物实例 ID |
| project_node | int | 关联的项目节点 ID |
| definition | int | 交付物定义版本 ID |
| node_deliverable_mapping | int | 节点交付物映射 ID |
| file | int | 关联的文件 ID |
| version | string | 文件版本号 |
| remark | string | 备注说明 |
| url | string | 外部链接 URL |
| state | string | 交付物状态 |
| created_by | int | 创建人用户 ID |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 关联文件属性

通过 `DeliverableFile` 模型关联获取的属性：

| 属性 | 说明 |
|------|------|
| name | 文件名称 |
| size | 文件大小 |
| category | 文件类型 |
| token | 飞书文件唯一标识 |
| folder | 文件夹路径 |
| path | 文件路径 |

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
| 400 | 请求参数错误、权限不足、业务规则校验失败 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限访问 |
| 404 | 交付物不存在 |
| 500 | 服务器内部错误 |

**常见业务错误**

| 错误信息 | 说明 |
|----------|------|
| `交付物准备中：请稍后再试` | 文件正在上传处理中（temp-token） |
| `当前交付物已冻结` | 交付物已被冻结，无法访问 |
| `节点已完成，无法删除交付物` | 已完成节点的交付物不允许删除 |
| `该节点下已存在版本 {version} 的交付物` | 版本号重复 |
| `该交付物是只读的，不允许创建` | 只读交付物不允许创建实例 |
