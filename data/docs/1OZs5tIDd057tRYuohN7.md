# PSC - NodeDefinition 接口文档

> 最后更新：2026-03-27
> App: `PSC` | Model: `NodeDefinition`
> Base URL: `/psc/node/definitions`

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
| GET | `/psc/node/definitions/simple` | 获取简化列表 | ✅ |
| GET | `/psc/node/definitions` | 获取列表（分页） | ✅ |
| POST | `/psc/node/definitions` | 创建节点定义 | ✅ |
| GET | `/psc/node/definitions/<id>` | 获取详情 | ✅ |
| PUT | `/psc/node/definitions/<id>` | 版本迭代 | ✅ |
| PATCH | `/psc/node/definitions` | 批量更新 | ✅ |
| DELETE | `/psc/node/definitions` | 批量删除 | ✅ |
| GET | `/psc/node/definitions/enums` | 获取枚举数据 | ✅ |

---

## 接口详情

### 1. 获取简化列表

**GET** `/psc/node/definitions/simple`

仅返回 `id`、`code`、`currentName`、`currentVersionId`、`currentCategory` 字段，适用于下拉选择等场景。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 按编码筛选 |
| name | string | 否 | 按名称筛选 |
| category | string | 否 | 按节点类型筛选 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "NODEDEF000001",
        "currentName": "项目立项",
        "currentVersionId": 1,
        "currentCategory": "MILESTONE"
      }
    ],
    "total": 1
  }
}
```

---

### 2. 获取列表（分页）

**GET** `/psc/node/definitions`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 按编码筛选 |
| currentName | string | 否 | 按当前版本名称筛选 |
| category | string | 否 | 按节点类型筛选 |
| pageNum | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| pageSort | string | 否 | 排序，格式 `字段:方向`，默认 `id:DESC` |

**pageSort 支持的字段**

- `id` - ID
- `code` - 编码

**方向**: `ASC` 或 `DESC`

**category 可选值**

- `MILESTONE` - 里程碑
- `MAIN_NODE` - 主节点
- `SUB_NODE` - 子节点

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "NODEDEF000001",
        "isActive": true,
        "createdAt": "2024-01-01T00:00:00+08:00",
        "updatedAt": "2024-01-01T00:00:00+08:00",
        "currentName": "项目立项",
        "currentCategory": "MILESTONE",
        "currentDefaultOwnerNickname": "张三",
        "currentProjectRoleName": "项目经理",
        "currentEvaluateOnComplete": true,
        "currentDefaultWorkhours": 8,
        "currentCreatedByNickname": "管理员"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 1,
      "totalPages": 1
    }
  }
}
```

---

### 3. 获取详情

**GET** `/psc/node/definitions/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 节点定义 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "NODEDEF000001",
      "name": "项目立项",
      "isActive": true
    },
    "versionData": {
      "id": 1,
      "versionNumber": 1,
      "name": "项目立项",
      "category": "MILESTONE",
      "isCurrent": true,
      "evaluateOnComplete": true,
      "defaultWorkhours": 8,
      "remark": "项目启动里程碑",
      "createdAt": "2024-01-01T00:00:00+08:00",
      "defaultOwner": {
        "id": 1,
        "nickname": "张三"
      },
      "projectRole": {
        "id": 1,
        "name": "项目经理"
      },
      "createdBy": {
        "id": 1,
        "nickname": "管理员"
      },
      "reviewItems": [
        {
          "id": 1,
          "reviewDefinitionVersionId": 1,
          "sortOrder": 1
        }
      ],
      "deliverableDefinitions": [
        {
          "id": 1,
          "deliverableDefinitionId": 1,
          "deliverableDefinitionName": "立项报告",
          "deliverableDefinitionVersionId": 1,
          "deliverableDefinitionVersion": "V1.0",
          "deliverableDefinitionIsRequired": true,
          "functionRestriction": "EDIT",
          "sortOrder": 1
        }
      ],
      "featureConfigs": [
        {
          "id": 1,
          "featureCode": "TIMELINE_PRESET",
          "featureLabel": "时间线预设",
          "isEnabled": true
        }
      ]
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-01T00:00:00+08:00",
      "versionCount": 1
    }
  }
}
```

---

### 4. 创建节点定义

**POST** `/psc/node/definitions`

创建节点定义和第一个版本（`isActive` 默认为 `true`）

**请求体**

```json
{
  "code": "NODEDEF000002",
  "name": "需求分析",
  "category": "MAIN_NODE",
  "defaultOwnerId": 1,
  "projectRoleId": 1,
  "evaluateOnComplete": true,
  "defaultWorkhours": 16,
  "remark": "需求分析阶段",
  "reviewItems": [
    {
      "versionId": 1,
      "sortOrder": 1
    }
  ],
  "deliverableDefinitions": [
    {
      "versionId": 1,
      "functionRestriction": "EDIT",
      "sortOrder": 1,
      "isRequired": true
    }
  ],
  "featureConfigs": [
    "TIMELINE_PRESET",
    "REQUIREMENT_REVIEW"
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 节点定义编码，唯一 |
| name | string | ✅ | 节点名称 |
| category | string | ✅ | 节点类型 |
| defaultOwnerId | int | 否 | 默认负责人 ID |
| projectRoleId | int | 否 | 项目角色 ID |
| evaluateOnComplete | boolean | 否 | 节点完成时评价，默认 false |
| defaultWorkhours | int | 否 | 节点默认工时，默认 0 |
| remark | string | 否 | 备注 |
| reviewItems | array | 否 | 评审项列表 |
| reviewItems[].versionId | int | ✅ | 评审项定义版本 ID |
| reviewItems[].sortOrder | int | 否 | 排序序号 |
| deliverableDefinitions | array | 否 | 交付物定义列表 |
| deliverableDefinitions[].versionId | int | ✅ | 交付物定义版本 ID |
| deliverableDefinitions[].functionRestriction | string | 否 | 功能限制，默认 `EDIT` |
| deliverableDefinitions[].isRequired | boolean | 否 | 是否必填，默认 `false` |
| deliverableDefinitions[].sortOrder | int | 否 | 排序序号 |
| featureConfigs | array | 否 | 功能配置列表 |

**category 可选值**

- `MILESTONE` - 里程碑
- `MAIN_NODE` - 主节点
- `SUB_NODE` - 子节点

**functionRestriction 可选值**

- `EDIT` - 编辑
- `VIEW` - 查看

**featureConfigs 可选值**

- `TIMELINE_PRESET` - 时间线预设
- `PRODUCT_MANIFEST_EDIT` - 配置清单编辑
- `PRODUCT_MANIFEST_DELIVERABLE_UPLOAD` - 配置清单交付物上传
- `PRODUCT_MANIFEST_DELIVERABLE_REVIEW` - 配置清单交付物复核
- `CHANGE_MILESTONE` - 变更里程碑
- `CHANGE_MAIN_NODE` - 变更主节点
- `CHANGE_NOTE` - 变更说明
- `CHANGE_CONFIRM` - 变更确认
- `SUBMIT_TEST` - 提交测试
- `REQUIREMENT_REVIEW` - 需求评审
- `DOCKING_REQUIREMENTS` - 对接需求
- `PREDECESSOR_NODE` - 前置节点

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 2
  }
}
```

---

### 5. 版本迭代

**PUT** `/psc/node/definitions/<id>`

创建新版本（不更新 `code`、`isActive`）

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 节点定义 ID |

**请求体**

```json
{
  "name": "需求分析 V2",
  "category": "MAIN_NODE",
  "defaultOwnerId": 1,
  "projectRoleId": 1,
  "evaluateOnComplete": false,
  "defaultWorkhours": 20,
  "remark": "更新后的需求分析",
  "reviewItems": [
    {
      "versionId": 1,
      "sortOrder": 1
    },
    {
      "versionId": 2,
      "sortOrder": 2
    }
  ],
  "deliverableDefinitions": [
    {
      "versionId": 1,
      "functionRestriction": "EDIT",
      "sortOrder": 1,
      "isRequired": true
    }
  ],
  "featureConfigs": [
    "TIMELINE_PRESET"
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 节点名称 |
| category | string | 否 | 节点类型 |
| defaultOwnerId | int | 否 | 默认负责人 ID |
| projectRoleId | int | 否 | 项目角色 ID |
| evaluateOnComplete | boolean | 否 | 节点完成时评价 |
| defaultWorkhours | int | 否 | 节点默认工时 |
| remark | string | 否 | 备注 |
| reviewItems | array | 否 | 评审项列表 |
| deliverableDefinitions | array | 否 | 交付物定义列表（支持 `isRequired` 字段） |
| featureConfigs | array | 否 | 功能配置列表 |

**注意事项**

- 此接口会创建新版本，旧版本保留
- `code` 和 `isActive` 不能通过此接口修改

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 2,
    "document": {
      "code": "NODEDEF000002",
      "name": "需求分析 V2",
      "isActive": true
    },
    "versionData": {
      "id": 2,
      "versionNumber": 2,
      "name": "需求分析 V2",
      "category": "MAIN_NODE",
      "isCurrent": true,
      "evaluateOnComplete": false,
      "defaultWorkhours": 20,
      "remark": "更新后的需求分析",
      "createdAt": "2024-01-02T00:00:00+08:00",
      "defaultOwner": {
        "id": 1,
        "nickname": "张三"
      },
      "projectRole": {
        "id": 1,
        "name": "项目经理"
      },
      "createdBy": {
        "id": 1,
        "nickname": "管理员"
      },
      "reviewItems": [],
      "deliverableDefinitions": [],
      "featureConfigs": []
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-02T00:00:00+08:00",
      "versionCount": 2
    }
  }
}
```

---

### 6. 批量更新

**PATCH** `/psc/node/definitions`

仅能更新 `isActive` 字段

**请求体**

```json
{
  "ids": [1, 2],
  "isActive": false
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 节点定义 ID 列表 |
| isActive | boolean | ✅ | 是否启用 |

**响应示例**

```json
{
  "msg": "success，更新了 2 条记录"
}
```

---

### 7. 批量删除

**DELETE** `/psc/node/definitions`

**请求体**

```json
{
  "ids": [1, 2]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 节点定义 ID 列表 |

**注意事项**

- 删除前会检查该节点定义是否已被项目模板引用
- 如果已被引用，则无法删除

**响应示例**

```json
{
  "msg": "success"
}
```

**错误示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "ids": [
      "\"NODEDEF000001\" 已被项目模板引用，无法删除"
    ]
  }
}
```

---

### 8. 获取枚举数据

**GET** `/psc/node/definitions/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "choices": {
      "category": [
        {
          "value": "MILESTONE",
          "label": "里程碑"
        },
        {
          "value": "MAIN_NODE",
          "label": "主节点"
        },
        {
          "value": "SUB_NODE",
          "label": "子节点"
        }
      ],
      "featureConfigCategories": [
        {
          "value": "PRODUCT_MANIFEST",
          "label": "配置清单设置"
        },
        {
          "value": "CHANGE",
          "label": "变更设置"
        },
        {
          "value": "FEATURE_ATTRIBUTE",
          "label": "功能属性设置"
        }
      ],
      "featureConfigs": [
        {
          "value": "TIMELINE_PRESET",
          "label": "时间线预设",
          "category": "FEATURE_ATTRIBUTE",
          "tips": "时间线预设节点未分配节点时间线后，无法完成"
        },
        {
          "value": "PRODUCT_MANIFEST_EDIT",
          "label": "配置清单编辑",
          "category": "PRODUCT_MANIFEST",
          "tips": "节点允许编辑项目产品清单（硬件配置/BOM等）"
        },
        {
          "value": "PRODUCT_MANIFEST_DELIVERABLE_UPLOAD",
          "label": "配置清单交付物上传",
          "category": "PRODUCT_MANIFEST",
          "tips": "节点允许上传配置清单相关交付物文件"
        },
        {
          "value": "PRODUCT_MANIFEST_DELIVERABLE_REVIEW",
          "label": "配置清单交付物复核",
          "category": "PRODUCT_MANIFEST",
          "tips": "节点需要对配置清单交付物进行复核"
        },
        {
          "value": "CHANGE_MILESTONE",
          "label": "变更里程碑",
          "category": "CHANGE",
          "tips": "变更里程碑"
        },
        {
          "value": "CHANGE_MAIN_NODE",
          "label": "变更主节点",
          "category": "CHANGE",
          "tips": "变更主节点"
        },
        {
          "value": "CHANGE_NOTE",
          "label": "变更说明",
          "category": "CHANGE",
          "tips": "节点允许填写项目设计变更说明（硬件变更/软件变更说明）"
        },
        {
          "value": "CHANGE_CONFIRM",
          "label": "变更确认",
          "category": "CHANGE",
          "tips": "节点需要确认项目设计变更（硬件变更确认/软件变更确认）"
        },
        {
          "value": "SUBMIT_TEST",
          "label": "提交测试",
          "category": "FEATURE_ATTRIBUTE",
          "tips": "交付资料节点有提交测试按钮：点击按钮后弹窗"若点击确定，执行验证，验证结论已完成则将回滚节点""
        },
        {
          "value": "REQUIREMENT_REVIEW",
          "label": "需求评审",
          "category": "FEATURE_ATTRIBUTE",
          "tips": "当需求评审节点完成后，项目状态切换为进行中"
        },
        {
          "value": "DOCKING_REQUIREMENTS",
          "label": "对接需求",
          "category": "FEATURE_ATTRIBUTE",
          "tips": "当对接需求节点完成后，将对特定人群推送消息通知"
        },
        {
          "value": "PREDECESSOR_NODE",
          "label": "前置节点",
          "category": "FEATURE_ATTRIBUTE",
          "tips": "项目在申请中也能够完成的前置节点标识"
        }
      ],
      "deliverable": {
        "functionRestriction": [
          {
            "value": "EDIT",
            "label": "编辑"
          },
          {
            "value": "VIEW",
            "label": "查看"
          }
        ]
      }
    }
  }
}
```

---

## 字段权限说明

| 字段 | POST 创建 | PUT 版本迭代 | PATCH 批量更新 |
|------|-----------|-------------|---------------|
| code | ✅ 可设置 | ❌ 不可修改 | ❌ 不可修改 |
| name | ✅ 必填 | ✅ 必填 | ❌ 不可修改 |
| isActive | ✅ 默认 true | ❌ 不可修改 | ✅ 可修改 |
| category | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| defaultOwnerId | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| projectRoleId | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| evaluateOnComplete | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| defaultWorkhours | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| remark | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| reviewItems | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| deliverableDefinitions | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |
| featureConfigs | ✅ 可选 | ✅ 可选 | ❌ 不可修改 |

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

**业务错误示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "code": [
      "\"NODEDEF000001\"已被使用，请更换编码后重试"
    ],
    "name": [
      "\"项目立项\"已被其他节点定义使用，请更换名称后重试"
    ]
  }
}
```

```json
{
  "msg": "参数错误",
  "errors": {
    "ids": [
      "\"NODEDEF000001\" 已被项目模板引用，无法删除"
    ]
  }
}
```

---

## 数据模型说明

### NodeDefinition（节点定义）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string | 唯一编码，自动生成，前缀 `NODEDEF` |
| is_active | boolean | 是否启用 |
| created_at | DateTime | 创建时间 |

### NodeDefinitionVersion（节点定义版本）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| version_number | int | 版本号（内部） |
| node_definition | ForeignKey | 关联节点定义 |
| name | string | 节点名称 |
| category | string | 节点类型 |
| default_owner | ForeignKey | 默认负责人 |
| project_role | ForeignKey | 项目角色 |
| evaluate_on_complete | boolean | 节点完成时评价 |
| default_workhours | int | 节点默认工时 |
| remark | string | 备注 |
| is_current | boolean | 是否当前版本 |
| created_by | ForeignKey | 创建人 |
| created_at | DateTime | 创建时间 |

### NodeDefinitionFeatureMapping（节点定义功能配置）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| node_definition_version | ForeignKey | 节点定义版本 |
| feature_code | string | 功能配置枚举值 |
| is_enabled | boolean | 是否启用 |

---

## 完整 cURL 示例

```bash
# 1. 获取简化列表
curl -X GET "http://your-domain.com/psc/node/definitions/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取列表（分页）
curl -X GET "http://your-domain.com/psc/node/definitions?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 获取详情
curl -X GET "http://your-domain.com/psc/node/definitions/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 创建节点定义
curl -X POST "http://your-domain.com/psc/node/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "code": "NODEDEF000002",
    "name": "需求分析",
    "category": "MAIN_NODE",
    "defaultOwnerId": 1,
    "projectRoleId": 1,
    "evaluateOnComplete": true,
    "defaultWorkhours": 16,
    "remark": "需求分析阶段",
    "reviewItems": [
      {
        "versionId": 1,
        "sortOrder": 1
      }
    ],
    "deliverableDefinitions": [
      {
        "versionId": 1,
        "functionRestriction": "EDIT",
        "sortOrder": 1,
        "isRequired": true
      }
    ],
    "featureConfigs": [
      "TIMELINE_PRESET",
      "REQUIREMENT_REVIEW"
    ]
  }'

# 5. 版本迭代
curl -X PUT "http://your-domain.com/psc/node/definitions/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "需求分析 V2",
    "category": "MAIN_NODE",
    "defaultOwnerId": 1,
    "evaluateOnComplete": false,
    "remark": "更新后的需求分析"
  }'

# 6. 批量更新
curl -X PATCH "http://your-domain.com/psc/node/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2],
    "isActive": false
  }'

# 7. 批量删除
curl -X DELETE "http://your-domain.com/psc/node/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2]
  }'

# 8. 获取枚举数据
curl -X GET "http://your-domain.com/psc/node/definitions/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
