# PM - NodeList 接口文档

> 最后更新：2026-03-27
> App: `PM` | Model: `Project_Node`
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
| GET | `/` | 获取节点枚举信息 | ✅ |
| GET | `/` | 获取节点列表 | ✅ |
| POST | `/add` | 添加节点 | ✅ |
| GET | `/add` | 查看可添加节点 | ✅ |
| GET | `/{id}` | 获取节点详情 | ✅ |
| DELETE | `/{id}` | 删除节点 | ✅ |
| POST | `/{id}/urge` | 催办节点 | ✅ |
| POST | `/{id}/appley-test` | 提交测试 | ✅ |
| PATCH | `/{id}/schedule` | 修改节点时间 | ✅ |
| PATCH | `/{id}/state/rollback` | 节点回滚 | ✅ |
| PATCH | `/{id}/state/complete` | 完成节点 | ✅ |
| GET | `/role/{action}` | 节点角色信息 | ✅ |
| POST | `/{id}/note` | 添加节点笔记 | ✅ |
| PATCH | `/{id}/standard-time` | 设置节点工时 | ✅ |

---

## 接口详情

### GET 获取节点枚举信息

获取节点相关的枚举值，包括节点状态、节点类别等。

#### 请求

```
GET /pm/nodelist/enums
```

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "state": [
      {"value": "0", "label": "待处理"},
      {"value": "1", "label": "进行中"},
      {"value": "2", "label": "已完成"},
      {"value": "4", "label": "项目变更节点中"},
      {"value": "5", "label": "申请中"}
    ],
    "category": [
      {"value": "MILESTONE", "label": "里程碑节点"},
      {"value": "MAIN_NODE", "label": "主节点"},
      {"value": "SUB_NODE", "label": "子节点"}
    ]
  }
}
```

---

### GET 获取节点列表

获取指定项目的所有节点列表。

#### 请求

```
GET /pm/nodelist/
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| list_id | integer | 是 | 项目 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "节点名称",
      "category": "MAIN_NODE",
      "start_time": "2025-01-01T00:00:00+08:00",
      "end_time": "2025-01-02T23:59:59+08:00",
      "complete_time": null,
      "state": "1",
      "owners": [
        {
          "id": 1,
          "user": {
            "id": 123,
            "name": "张三",
            "avatar": "avatar_url"
          },
          "is_major": true,
          "standard_time": 8.0
        }
      ]
    }
  ]
}
```

---

### POST 添加节点

向项目中添加新节点。

#### 请求

```
POST /pm/nodelist/add
```

**请求体：**

```json
{
  "listId": 1,
  "nodeIds": [1, 2, 3],
  "parentId": null
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| listId | integer | 是 | 项目 ID |
| nodeIds | array | 是 | 节点定义 ID 列表 |
| parentId | integer | 否 | 父节点 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "addedCount": 3
  }
}
```

---

### GET 获取节点详情

获取单个节点的详细信息，包括节点交付物列表。

#### 请求

```
GET /pm/nodelist/{id}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "name": "节点名称",
    "category": "MAIN_NODE",
    "start_time": "2025-01-01T00:00:00+08:00",
    "end_time": "2025-01-02T23:59:59+08:00",
    "complete_time": null,
    "state": "1",
    "canComplete": true,
    "canDelete": false,
    "canRollback": true,
    "features": {
      "timelinePreset": false,
      "submitTest": true,
      "review": {
        "list": [...]
      },
      "deliverable": {
        "list": [
          {
            "id": 1,
            "name": "交付物名称",
            "code": "DELIVERABLE_CODE",
            "required": true,
            "isLinkFirst": false,
            "hasTemplate": true,
            "nodeDefinitionDeliverableMappingId": 1,
            "functionRestriction": "none",
            "allowedFileExtensions": ["pdf", "docx"],
            "instances": [
              {
                "id": 1,
                "name": "文件名.pdf",
                "version": "v1.0",
                "state": "INITIAL_FROZEN",
                "remark": "备注信息",
                "createdAt": "2025-01-01T10:00:00+08:00"
              }
            ]
          }
        ]
      },
      "note": {
        "content": "节点笔记内容"
      },
      "productManifestEdit": false,
      "productManifestDeliverableUpload": null,
      "productManifestDeliverableReview": null,
      "changeConfirm": null
    },
    "owners": [
      {
        "id": 1,
        "is_major": true,
        "standard_time": 8.0,
        "user": {
          "id": 123,
          "name": "张三",
          "avatar": "avatar_url"
        }
      }
    ],
    "project_state": "1",
    "node_state_list": [...],
    "authority": {...}
  }
}
```

#### 响应字段说明 - features.deliverable

节点交付物列表结构说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | array | 交付物定义列表 |
| list[].id | integer | 交付物定义版本 ID |
| list[].name | string | 交付物名称 |
| list[].code | string | 交付物编码（唯一标识） |
| list[].required | boolean | 是否必填（来源：NodeDefinitionDeliverableMapping.is_required） |
| list[].isLinkFirst | boolean | 是否优先使用链接上传 |
| list[].hasTemplate | boolean | 是否关联飞书模板 |
| list[].nodeDefinitionDeliverableMappingId | integer | 节点交付物映射 ID |
| list[].functionRestriction | string | 功能限制（如：none/read_only） |
| list[].allowedFileExtensions | array | 允许的文件扩展名列表 |
| list[].instances | array | 已上传的交付物实例列表（可选） |
| list[].instances[].id | integer | 实例 ID |
| list[].instances[].name | string | 文件名或"自定义链接" |
| list[].instances[].version | string | 文件版本 |
| list[].instances[].state | string | 状态（INITIAL_FROZEN/FROZEN/APPROVED等） |
| list[].instances[].remark | string | 备注信息 |
| list[].instances[].createdAt | string | 创建时间（ISO 8601） |

#### 交付物实例状态（state）

| 值 | 说明 |
|----|------|
| INITIAL_FROZEN | 初始冻结 |
| FROZEN | 已冻结 |
| APPROVED | 已批准 |

---

### DELETE 删除节点

删除指定节点。

#### 请求

```
DELETE /pm/nodelist/{id}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "deletedId": 1
  }
}
```

---

### POST 催办节点

向节点负责人发送催办通知。

#### 请求

```
POST /pm/nodelist/{id}/urge
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "message": "催办通知已发送"
  }
}
```

---

### POST 提交测试

提交节点测试（功能检查）。

#### 请求

```
POST /pm/nodelist/{id}/appley-test
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "message": "测试已提交"
  }
}
```

---

### PATCH 修改节点时间

修改节点的开始和结束时间。

#### 请求

```
PATCH /pm/nodelist/{id}/schedule
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

**请求体：**

```json
{
  "startDate": "2025-01-01T00:00:00+08:00",
  "endDate": "2025-01-02T23:59:59+08:00"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| startDate | string | 是 | 开始时间（ISO 8601） |
| endDate | string | 是 | 结束时间（ISO 8601） |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "start_time": "2025-01-01T00:00:00+08:00",
    "end_time": "2025-01-02T23:59:59+08:00"
  }
}
```

---

### PATCH 节点回滚

将节点状态回滚到进行中。

#### 请求

```
PATCH /pm/nodelist/{id}/state/rollback
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

**请求体：**

```json
{
  "reason": "回滚原因说明"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| reason | string | 是 | 回滚原因 |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "state": "1",
    "message": "节点已回滚"
  }
}
```

---

### PATCH 完成节点

将节点标记为已完成。

#### 请求

```
PATCH /pm/nodelist/{id}/state/complete
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "state": "2",
    "complete_time": "2025-01-02T10:00:00+08:00"
  }
}
```

---

### GET 节点角色信息

获取节点相关的角色信息。

#### 请求

```
GET /pm/nodelist/role/{action}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| action | string | 是 | 操作类型 |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "roles": [...],
    "users": [...]
  }
}
```

---

### PATCH 设置节点工时

设置节点的标准工时。

#### 请求

```
PATCH /pm/nodelist/{id}/standard-time
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 节点 ID |

**请求体：**

```json
{
  "standardTime": 8.0
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| standardTime | decimal | 是 | 标准工时（小时） |

#### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "standard_time": 8.0
  }
}
```

---

## 数据模型

### 节点状态（state）

| 值 | 说明 |
|----|------|
| 0 | 待处理 |
| 1 | 进行中 |
| 2 | 已完成 |
| 4 | 项目变更节点中 |
| 5 | 申请中 |

### 节点类别（category）

| 值 | 说明 |
|----|------|
| MILESTONE | 里程碑节点 |
| MAIN_NODE | 主节点 |
| SUB_NODE | 子节点 |

---

## 权限说明

| 权限码 | 说明 | 允许角色 |
|--------|------|----------|
| 1007 | 添加节点 | OWNER, SUPERUSER, MANAGER |
| 1008 | 删除节点 | OWNER, SUPERUSER, MANAGER |
| 2001 | 编辑负责人 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR, MANAGER |
| 2004 | 编辑工时 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR |
| 2200 | 完成节点 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR, MANAGER |
| 2201 | 回滚节点 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR, MANAGER |
| 2205 | 提交测试 | OWNER, SUPERUSER, OWNER_NODE, ASSISTOR, MANAGER |

---

## 完整 cURL 示例

```bash
# 1. 获取节点枚举信息
curl -X GET "https://api.example.com/pm/nodelist/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取节点列表
curl -X GET "https://api.example.com/pm/nodelist/?list_id=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 获取节点详情
curl -X GET "https://api.example.com/pm/nodelist/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 完成节点
curl -X PATCH "https://api.example.com/pm/nodelist/1/state/complete" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 节点回滚
curl -X PATCH "https://api.example.com/pm/nodelist/1/state/rollback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"reason": "需要修改设计"}'

# 6. 修改节点时间
curl -X PATCH "https://api.example.com/pm/nodelist/1/schedule" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "startDate": "2025-01-01T00:00:00+08:00",
    "endDate": "2025-01-02T23:59:59+08:00"
  }'

# 7. 催办节点
curl -X POST "https://api.example.com/pm/nodelist/1/urge" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 8. 设置节点工时
curl -X PATCH "https://api.example.com/pm/nodelist/1/standard-time" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"standardTime": 8.0}'
```
