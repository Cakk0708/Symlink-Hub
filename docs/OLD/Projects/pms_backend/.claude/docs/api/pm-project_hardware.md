# PM - ProjectHardware 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `ProjectHardware`
> Base URL: `/hardwares`

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
| GET | `/hardwares/project` | 获取项目硬件列表（管理后台） | ✅ |
| POST | `/hardwares/project` | 批量更新项目硬件版本 | ✅ |
| POST | `/hardwares/version` | 创建项目硬件配置 | ✅ |
| PUT | `/hardwares/version` | 更新项目硬件配置 | ✅ |
| DELETE | `/hardwares/version/<id>` | 删除项目硬件配置 | ✅ |

---

## 接口详情

### 1. 获取项目硬件列表（管理后台）

**GET** `/hardwares/project`

**说明**：用于管理后台-项目配置-硬件信息，获取引用了指定硬件版本的项目列表

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| versionId | string | 否 | 版本ID，支持逗号分隔（如 '1,2'）或数组格式 |
| all | boolean | 否 | 是否返回全部列表，默认 false |
| pageNum | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "version_id": 10,
      "version_name": "1.0",
      "name": "智能门锁项目",
      "state": 1,
      "state_expand": "进行中",
      "create_time": "2026-01-01T00:00:00+08:00",
      "createTime": "2026-01-01T00:00:00+08:00",
      "creator": "张三"
    }
  ],
  "total": 50
}
```

---

### 2. 批量更新项目硬件版本

**POST** `/hardwares/project`

**说明**：在管理后台批量同步更新多个项目硬件的版本

**请求体**

```json
{
  "versionId": 15,
  "projectId": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| versionId | int | ✅ | 目标硬件版本ID |
| projectId | array | ✅ | 项目硬件ID列表 |

**响应示例**

```json
{
  "msg": "更新成功"
}
```

**错误响应示例**

```json
{
  "msg": "批量更新过程中出错",
  "error": "错误详情"
}
```

---

### 3. 创建项目硬件配置

**POST** `/hardwares/version`

**权限要求**：需要节点操作权限（权限码 2010）

**请求体**

```json
{
  "node_id": 100,
  "version_id": 15,
  "quantity": 5,
  "is_need_program": true
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| node_id | int | ✅ | 节点ID |
| version_id | int | ✅ | 硬件版本ID |
| quantity | int | 否 | 分板数量，默认 1 |
| is_need_program | boolean | 否 | 是否需要程序，默认 true |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 50,
    "node_id": 100,
    "version_id": 15,
    "quantity": 5,
    "is_need_program": true
  }
}
```

**错误响应示例**

```json
{
  "msg": "操作失败，权限不匹配"
}
```

```json
{
  "msg": "操作失败",
  "errors": {
    "操作失败": "节点已完成"
  }
}
```

---

### 4. 更新项目硬件配置

**PUT** `/hardwares/version`

**权限要求**：需要节点操作权限（权限码 2010）

**说明**：仅允许修改 `quantity` 和 `is_need_program` 字段

**请求体**

```json
{
  "id": 50,
  "quantity": 10,
  "is_need_program": false
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | ✅ | 项目硬件配置ID |
| quantity | int | 否 | 分板数量 |
| is_need_program | boolean | 否 | 是否需要程序 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 50,
    "quantity": 10,
    "is_need_program": false
  },
  "id": 50
}
```

---

### 5. 删除项目硬件配置

**DELETE** `/hardwares/version/<id>`

**权限要求**：需要节点操作权限（权限码 2010）

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目硬件配置ID |

**响应示例**

```json
{
  "msg": "删除成功"
}
```

**错误响应示例**

```json
{
  "msg": "权限不匹配"
}
```

```json
{
  "msg": "分板记录不存在"
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

### ProjectHardware

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 项目硬件配置ID |
| project | int | 所属项目ID |
| node | int | 所属节点ID |
| version | int | 硬件版本ID（关联 Hardware_Spec_Child） |
| quantity | int | 分板数量 |
| is_need_program | boolean | 是否需要程序 |
| remark | string | 备注 |
| creator | int | 创建人ID |
| create_time | datetime | 创建时间 |
| update_by | int | 最后修改人ID |
| update_time | datetime | 最后修改时间 |

### 属性方法

| 属性 | 类型 | 说明 |
|------|------|------|
| hardware_name | string | 硬件名称（从 version.spec.name 获取） |
| category_name | string | 分类名称（从 version.spec.category.name 获取） |
| version_code | string | 硬件版本号（从 version.version 获取） |

---

## 权限说明

### 节点操作权限

创建、更新、删除项目硬件配置需要节点操作权限（权限码：2010）

**权限验证逻辑**：
- 检查用户是否对节点具有指定权限
- 节点状态不能为"已完成"（state = 2）

---

## 完整 cURL 示例

```bash
# 1. 获取项目硬件列表（管理后台）
curl -X GET "http://your-domain.com/hardwares/project?versionId=10,15&pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 批量更新项目硬件版本
curl -X POST "http://your-domain.com/hardwares/project" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "versionId": 15,
    "projectId": [1, 2, 3]
  }'

# 3. 创建项目硬件配置
curl -X POST "http://your-domain.com/hardwares/version" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "node_id": 100,
    "version_id": 15,
    "quantity": 5,
    "is_need_program": true
  }'

# 4. 更新项目硬件配置
curl -X PUT "http://your-domain.com/hardwares/version" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 50,
    "quantity": 10,
    "is_need_program": false
  }'

# 5. 删除项目硬件配置
curl -X DELETE "http://your-domain.com/hardwares/version/50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 业务流程说明

### 1. 硬件配置流程

```
1. 在管理后台创建硬件规格（PSC/hardware/spec）
2. 为硬件规格添加版本（HardwareSpecChild）
3. 在PMS项目节点中选择硬件版本并配置
4. 记录操作日志
```

### 2. 版本同步流程

```
1. 管理后台发现硬件版本更新
2. 查询使用该版本的所有项目（/hardwares/project）
3. 批量更新项目硬件版本（POST /hardwares/project）
4. 项目中自动使用新版本
```

### 3. 权限校验流程

```
1. 用户发起操作请求
2. 从请求中获取节点信息
3. 验证用户对节点的操作权限（权限码 2010）
4. 检查节点状态（不能是已完成状态）
5. 执行操作并记录日志
```
