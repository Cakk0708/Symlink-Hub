# PM - HardwareDeliverable Reuse 接口文档

> 最后更新：2026-03-31
> App: `PM` | Model: `HardwareDeliverable`
> Base URL: `/hardware/deliverable`

---

## 模块说明

硬件交付物复用模块，用于在不同项目硬件之间复用已验证的通用程序（交付物）。该功能提高了开发效率，确保代码一致性。

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
| GET | `/reuse` | 获取可复用的交付物列表 | ✅ |
| POST | `/reuse` | 执行复用操作 | ✅ |
| PUT | `/reuse/<action>` | 替换已复用的交付物 | ✅ |

---

## 接口详情

### 1. 获取可复用的交付物列表

获取系统中所有可被复用的硬件交付物列表。

**请求**

```
GET /hardware/deliverable/reuse
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categoryId | integer | 否 | 硬件分类ID（用于筛选） |
| key | string | 否 | 搜索关键词（匹配文件名） |

**请求示例**

```bash
curl -X GET "/hardware/deliverable/reuse?categoryId=1&key=程序" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 123,
      "create_time": "2026-03-31",
      "reuse_status": "ORIGINAL",
      "project_info": {
        "id": 456,
        "name": "智能门锁项目",
        "model": "MT-2023-001"
      },
      "hardware_info": {
        "id": 789,
        "name": "主控板",
        "version": "V1.2",
        "category": {
          "id": 1,
          "name": "MCU"
        }
      },
      "attachment_info": {
        "id": 101,
        "name": "主控板固件_V1.2.hex",
        "creator": "张三",
        "create_time": "2026-03-31",
        "state": "NORMAL",
        "operation": true,
        "type": "COMMON",
        "note": "已验证版本",
        "file_name": "主控板固件_V1.2.hex"
      }
    }
  ],
  "total": 1
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 交付物映射ID（复用时的源ID） |
| create_time | string | 创建时间 |
| reuse_status | string | 复用状态（ORIGINAL=原始，REUSED=已复用） |
| project_info | object | 项目信息 |
| hardware_info | object | 硬件信息 |
| attachment_info | object | 交付物附件信息 |

**复用条件说明**

只有满足以下条件的交付物才会出现在列表中：
- 交付物状态为 `NORMAL`（正常）
- 交付物类型为 `COMMON`（通用程序）
- 复用状态为 `ORIGINAL`（未被复用）

---

### 2. 执行复用操作

将选中的交付物复用到目标硬件。

**请求**

```
POST /hardware/deliverable/reuse
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | ✅ | 复用来源的交付物映射ID |
| hardwareId | integer | ✅ | 目标硬件ID |
| nodeId | integer | ✅ | 当前节点ID（用于权限验证） |

**请求示例**

```bash
curl -X POST "/hardware/deliverable/reuse" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 123,
    "hardwareId": 789,
    "nodeId": 45
  }'
```

**响应示例**

```json
{
  "msg": "success"
}
```

**业务逻辑说明**

1. **权限验证**：用户必须对目标节点有操作权限（权限码：2011）
2. **复用状态校验**：源交付物必须是 `ORIGINAL` 状态，不能是 `REUSED` 状态
3. **交付物类型校验**：源交付物必须是 `COMMON`（通用程序）类型
4. **交付物状态校验**：源交付物状态必须是 `NORMAL`（正常）
5. **创建复用记录**：创建新的 `HardwareDeliverableMapping` 记录，`reuse_status` 设置为 `REUSED`

**错误响应**

```json
{
  "msg": "复用失败：该交付物为复用状态，请勿重复复用"
}
```

```json
{
  "msg": "复用失败：该交付物为非通用程序，请勿复用"
}
```

```json
{
  "msg": "复用失败：该交付物为 FROZEN 状态，请勿复用"
}
```

```json
{
  "msg": "操作失败：权限不匹配"
}
```

---

### 3. 替换已复用的交付物

用另一个可复用的交付物替换当前硬件的交付物。

**请求**

```
PUT /hardware/deliverable/reuse/<action>
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| action | string | 要替换的交付物映射ID |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | ✅ | 新的复用来源交付物映射ID |
| hardwareId | integer | ✅ | 目标硬件ID |
| nodeId | integer | ✅ | 当前节点ID（用于权限验证） |

**请求示例**

```bash
curl -X PUT "/hardware/deliverable/reuse/456" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 123,
    "hardwareId": 789,
    "nodeId": 45
  }'
```

**响应示例**

```json
{
  "msg": "success"
}
```

**业务逻辑说明**

1. **查找被替换的记录**：根据 `action` 参数中的ID查找 `HardwareDeliverableMapping` 记录
2. **复用条件校验**：同"执行复用操作"中的校验逻辑
3. **额外校验**：如果被替换的交付物是 `ORIGINAL` 状态且已被其他记录复用，则不允许替换
4. **更新记录**：将当前记录的 `deliverable` 更新为新的交付物，`reuse_status` 设置为 `REUSED`

**错误响应**

```json
{
  "msg": "操作失败：该交付物已被复用，不可替换"
}
```

```json
{
  "msg": "复用交付物失败, 数据不存在"
}
```

---

## 数据模型

### HardwareDeliverable（硬件交付物）

| 字段 | 类型 | 说明 |
|------|------|------|
| file | ForeignKey | 关联的交付物文件 |
| state | string | 交付物状态（NORMAL/FROZEN/INITIAL_FROZEN/STORAGE_MIGRATION_ERROR） |
| type | string | 交付物类型（COMMON=通用，STANDARD=标准） |
| version | string | 文件版本 |
| creator | ForeignKey | 创建人 |
| create_time | DateTime | 创建时间 |
| update_by | ForeignKey | 最后修改人 |
| update_time | DateTime | 最后修改时间 |

### HardwareDeliverableMapping（硬件交付物映射）

| 字段 | 类型 | 说明 |
|------|------|------|
| deliverable | ForeignKey | 关联的硬件交付物 |
| hardware | ForeignKey | 关联的项目硬件 |
| node | ForeignKey | 所属节点 |
| reuse_status | string | 复用状态（ORIGINAL=原始，REUSED=已复用） |
| remark | string | 备注 |
| creator | ForeignKey | 创建人 |
| create_time | DateTime | 创建时间 |
| update_by | ForeignKey | 最后修改人 |
| update_time | DateTime | 最后修改时间 |

### ProjectHardware（项目硬件）

| 字段 | 类型 | 说明 |
|------|------|------|
| project | ForeignKey | 所属项目 |
| node | ForeignKey | 所属节点 |
| version | ForeignKey | 硬件版本规格 |
| quantity | integer | 分板数量 |
| is_need_program | boolean | 是否需要程序 |
| remark | string | 备注 |

---

## 枚举值说明

### ReuseStatus（复用状态）

| 值 | 说明 |
|----|------|
| ORIGINAL | 原始附件（未复用） |
| REUSED | 直接复用 |

### DeliverableState（交付物状态）

| 值 | 说明 |
|----|------|
| NORMAL | 正常 |
| FROZEN | 冻结 |
| INITIAL_FROZEN | 初始冻结（新上传等待异步处理） |
| STORAGE_MIGRATION_ERROR | 储存迁移异常 |

### DeliverableType（交付物类型）

| 值 | 说明 |
|----|------|
| COMMON | 通用程序（可复用） |
| STANDARD | 标准程序（不可复用） |
| REUSED | 复用 |

---

## 错误响应

所有接口错误时统一返回：

```json
{
  "msg": "error message"
}
```

**常见错误码**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误或业务逻辑校验失败 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取可复用的交付物列表
curl -X GET "/hardware/deliverable/reuse?categoryId=1&key=程序" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 执行复用操作
curl -X POST "/hardware/deliverable/reuse" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 123,
    "hardwareId": 789,
    "nodeId": 45
  }'

# 3. 替换已复用的交付物
curl -X PUT "/hardware/deliverable/reuse/456" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 123,
    "hardwareId": 789,
    "nodeId": 45
  }'
```

---

## 相关接口

- `GET /hardware/deliverable/instance` - 获取硬件交付物实例
- `POST /hardware/deliverable/common/<id>` - 设置为通用程序
- `POST /hardware/deliverable/freeze/<action>` - 冻结/解冻程序
