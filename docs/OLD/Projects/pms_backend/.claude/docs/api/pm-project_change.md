# PM - Project_change 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `Project_change`
> Base URL: `/pm/change`

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
| GET | `/change` | 获取项目变更记录列表 | ✅ |
| POST | `/change` | 发起项目变更（旧版，已废弃） | ✅ |
| PATCH | `/change/{id}` | 批准项目变更（旧版，已废弃） | ✅ |
| GET | `/change/{action}` | 获取项目变更记录列表（按项目） | ✅ |
| POST | `/change/{action}` | 发起项目变更 | ✅ |
| PATCH | `/change/{action}` | 批准项目变更 | ✅ |
| GET | `/change/list/{projectId}` | 获取项目变更枚举和范围 | ✅ |

---

## 接口详情

### 1. 获取项目变更记录列表

**GET** `/change/{action}`

获取指定项目的已批准变更记录。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| action | int | 项目 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "reason": "客户需求调整",
      "category": "REQUIREMENT_CHANGE",
      "type": "客户需求变动",
      "createTime": "2024-01-15",
      "applicant": {
        "id": 123,
        "name": "张三",
        "avatar": "https://..."
      },
      "scope": "硬件设计: 方案设计、原理图设计"
    }
  ]
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 变更记录 ID |
| reason | string | 变更原因 |
| category | string | 变更类型代码 |
| type | string | 变更类型名称 |
| createTime | string | 创建时间（日期格式） |
| applicant | object | 申请人信息 |
| scope | string \| null | 变更范围（节点名称拼接） |

---

### 2. 发起项目变更

**POST** `/change`

发起项目设计变更申请。

**请求体**

```json
{
  "projectId": 123,
  "reason": "客户需要增加新功能",
  "changeTypes": "REQUIREMENT_CHANGE",
  "subItems": [456, 457],
  "userConfigs": {
    "change_note": [789, 790],
    "change_confirm": [791, 792]
  }
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectId | int | ✅ | 项目 ID |
| reason | string | ✅ | 变更原因 |
| changeTypes | string | ✅ | 变更类型，见下方枚举值 |
| subItems | array[int] | 否 | 变更节点 ID 列表（部分类型需要） |
| userConfigs | object | 否 | 节点负责人配置 |

**userConfigs 配置说明**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| change_note | array[int] | 否 | 变更说明节点负责人 ID 列表 |
| change_confirm | array[int] | 否 | 变更确认节点负责人 ID 列表 |

**变更类型枚举 (changeTypes)**

| 值 | 说明 | 可选范围 |
|---|------|---------|
| BASIC_INFO_CHANGE | 基础信息变更 | 否 |
| REQUIREMENT_CHANGE | 客户需求变动 | 是 |
| ISSUE_FIX | 问题修复 | 是 |
| TECH_UPGRADE | 技术升级 | 是 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "project": {
      "state": 3
    }
  }
}
```

**业务规则**

- 项目状态必须为"已完成"（state=2）
- 项目当前不能有待审批的变更申请
- 同一项目 5 秒内不可重复提交
- 只有部分变更类型需要选择变更范围

---

### 3. 批准项目变更

**PATCH** `/change/{action}`

批准项目变更申请（管理员操作）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| action | int | 变更记录 ID |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 4. 获取项目变更枚举和范围

**GET** `/change/list/{projectId}`

获取创建项目变更所需的枚举值和可选范围。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| projectId | int | 项目 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "projectId": 123,
    "changeTypes": [
      {
        "value": "BASIC_INFO_CHANGE",
        "label": "基础信息变更",
        "isScopeSelectable": false,
        "isDefault": false
      },
      {
        "value": "REQUIREMENT_CHANGE",
        "label": "客户需求变动",
        "isScopeSelectable": true,
        "isDefault": true
      },
      {
        "value": "ISSUE_FIX",
        "label": "问题修复",
        "isScopeSelectable": true,
        "isDefault": false
      },
      {
        "value": "TECH_UPGRADE",
        "label": "技术升级",
        "isScopeSelectable": true,
        "isDefault": false
      }
    ],
    "scopes": [
      {
        "id": 456,
        "name": "硬件设计",
        "userConfigs": [
          {
            "value": "change_note",
            "label": "变更说明",
            "required": true,
            "multiple": true,
            "disabled": false
          },
          {
            "value": "change_confirm",
            "label": "变更确认",
            "required": true,
            "multiple": true,
            "disabled": false
          }
        ],
        "subItems": [
          {
            "id": 789,
            "name": "方案设计",
            "userConfigs": [
              {
                "value": "change_note",
                "label": "变更说明",
                "required": true,
                "multiple": true,
                "disabled": false
              },
              {
                "value": "change_confirm",
                "label": "变更确认",
                "required": true,
                "multiple": true,
                "disabled": false
              }
            ]
          }
        ]
      }
    ]
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| projectId | int | 项目 ID |
| changeTypes | array | 变更类型枚举列表 |
| scopes | array | 可选变更范围（节点树结构） |

**scopes 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 节点 ID |
| name | string | 节点名称 |
| userConfigs | array | 节点负责人配置选项 |
| subItems | array | 子节点列表 |

**注意**：scopes 会自动排除包含变更功能的节点和里程碑节点。

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

**常见业务错误**

| 错误信息 | 说明 |
|---------|------|
| 设计变更创建失败：项目已发起设计变更，请等待审批结果 | 项目存在待审批的变更申请 |
| 设计变更创建失败：项目已处于项目变更模式 | 项目状态已为变更模式 |
| 设计变更创建失败：项目未完成，如有更新需求，请回滚节点进行变更 | 项目未完成，不能发起变更 |
| 设计变更创建失败：请勿重复提交 | 短时间内重复提交 |
| 以下节点不属于该项目 | 提交的节点 ID 不属于该项目 |

---

## 完整 cURL 示例

```bash
# 1. 获取项目变更记录列表
curl -X GET "https://your-domain.com/api/pm/change/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取变更枚举和范围
curl -X GET "https://your-domain.com/api/pm/change/list/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 发起项目变更（基础信息变更）
curl -X POST "https://your-domain.com/api/pm/change" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectId": 123,
    "reason": "项目基础信息需要调整",
    "changeTypes": "BASIC_INFO_CHANGE"
  }'

# 4. 发起项目变更（需求变更，含节点范围）
curl -X POST "https://your-domain.com/api/pm/change" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectId": 123,
    "reason": "客户需要增加新功能",
    "changeTypes": "REQUIREMENT_CHANGE",
    "subItems": [456, 789],
    "userConfigs": {
      "change_note": [100, 101],
      "change_confirm": [102, 103]
    }
  }'

# 5. 批准项目变更
curl -X PATCH "https://your-domain.com/api/pm/change/456" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 附录：变更状态枚举

| 状态值 | 说明 |
|-------|------|
| PENDING | 待评审 |
| APPROVED | 已评审 |
| REJECTED | 已拒绝 |
| CANCEL | 已取消 |
