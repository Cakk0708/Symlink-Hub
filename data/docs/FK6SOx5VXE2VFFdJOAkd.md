# PM - HardwareDeliverable 接口文档

> 最后更新：2026-04-11
> App: `PM` | Model: `HardwareDeliverable`, `HardwareDeliverableMapping`
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
| GET | `/deliverable/instance/<id>` | 获取/检查硬件交付物 | ✅ |
| POST | `/deliverable/instance` | 创建硬件交付物 | ✅ |
| PUT | `/deliverable/instance/<id>` | 更新硬件交付物（版本、备注） | ✅ |
| PATCH | `/deliverable/instance/<id>` | 替换硬件交付物（单个） | ✅ |
| DELETE | `/deliverable/instance/<id>` | 删除硬件交付物 | ✅ |
| PATCH | `/deliverable/common/<id>` | 设置为通用程序 | ✅ |
| PATCH | `/deliverable/freeze/<action>` | 批量冻结/解冻程序 | ✅ |
| POST | `/deliverable/replace` | 批量替换交付物 | ✅ |
| GET | `/deliverable/reuse` | 获取可复用交付物列表 | ✅ |
| POST | `/deliverable/reuse` | 复用交付物 | ✅ |
| PUT | `/deliverable/reuse/<action>` | 替换为复用交付物 | ✅ |

---

## 接口详情

### 1. 获取/检查硬件交付物

**GET** `/deliverable/instance/<id>`

**权限说明**：
- 需要 `pm.product_manifest.deliverable_view` 或 `pm.product_manifest.deliverable_edit` 权限（超级用户除外）
- 超级用户可下载任何状态的交付物
- 交付物创建者可下载 INITIAL_FROZEN 状态的交付物
- 通过 AuthorityVerifier 验证拥有项目级权限的用户可下载

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件交付物映射ID |

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| container | string | 否 | 传 `feishu` 表示在飞书容器内访问，后端返回 applink 前缀 URL |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "url": "https://open.feishu.cn/open-apis/drive/v1/files/xxx/download"
  }
}
```

**飞书容器内响应示例**（`?container=feishu`）

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "url": "https://applink.feishu.cn/client/web_url/open?mode=appCenter&url=https://open.feishu.cn/open-apis/drive/v1/files/xxx/download"
  }
}
```

**错误响应示例**

```json
{
  "msg": "交付物不可访问",
  "data": "交付物状态为"冻结"，无法下载"
}
```

```json
{
  "msg": "权限不足",
  "data": "您没有权限下载此交付物"
}
```

---

### 2. 创建硬件交付物

**POST** `/deliverable/instance`

**权限要求**：`pm.product_manifest.deliverable_edit`

**请求体**

```json
{
  "hardwareId": 10,
  "fileId": 100,
  "nodeId": 50
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| hardwareId | int | ✅ | 项目硬件ID |
| fileId | int | ✅ | 交付物文件ID |
| nodeId | int | ✅ | 节点ID |

**响应示例**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "name": "firmware_v1.0.hex",
    "history": [
      {
        "id": 1,
        "name": "firmware_v1.0.hex",
        "version": "1.0.0",
        "state": "INITIAL_FROZEN",
        "createTime": "2026-01-01 00:00:00",
        "is_last": true
      }
    ]
  }
}
```

**错误响应示例**

```json
{
  "msg": "创建失败",
  "data": "该配置已存在同名交付物 firmware_v1.0.hex 的交付物"
}
```

---

### 3. 更新硬件交付物（版本、备注）

**PUT** `/deliverable/instance/<id>`

**权限要求**：`pm.product_manifest.deliverable_edit`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件交付物映射ID |

**请求体**

```json
{
  "version": "1.0.0",
  "remark": "稳定版本"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | string | 否 | 版本号（格式：X.Y.Z，如 1.0.0） |
| remark | string | 否 | 备注 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "版本号格式校验错误",
  "data": "版本号必须是三级格式：X.Y.Z（如1.0.0），每部分1-3位数字"
}
```

---

### 4. 替换硬件交付物（单个）

**PATCH** `/deliverable/instance/<id>`

**权限要求**：节点操作权限（`pm.product_manifest.deliverable_edit`）

**说明**：替换单个硬件交付物，会创建新的交付物记录，旧交付物保留历史

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件交付物映射ID |

**请求体**

```json
{
  "fileId": 101
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | int | ✅ | 新的交付物文件ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "replaceData": {
      "total": 3,
      "items": [
        {
          "id": 2,
          "hardwareName": "STM32F103",
          "hardwareVersion": "1.0",
          "projectName": "智能门锁项目"
        }
      ]
    }
  }
}
```

---

### 5. 删除硬件交付物

**DELETE** `/deliverable/instance/<id>`

**权限要求**：`pm.product_manifest.deliverable_edit`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件交付物映射ID |

**响应示例**

```json
{
  "msg": "删除成功"
}
```

**错误响应示例**

```json
{
  "msg": "删除失败",
  "data": "该交付物被其他分板复用，无法删除"
}
```

---

### 6. 设置为通用程序

**PATCH** `/deliverable/common/<id>`

**权限要求**：节点操作权限（`pm.product_manifest.deliverable_edit`）

**说明**：将硬件交付物设置为通用程序（COMMON）或标准程序（STANDARD）

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 硬件交付物映射ID |

**请求体**

```json
{
  "type": "COMMON"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | ✅ | 交付物类型：COMMON（通用）/ STANDARD（标准） |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 7. 批量冻结/解冻程序

**PATCH** `/deliverable/freeze/<action>`

**权限要求**：节点操作权限（独立冻结权限校验）

**说明**：批量冻结或解冻硬件交付物，不允许跨项目操作

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| action | string | 逗号分隔的硬件交付物映射ID，如 `1,2,3` |

**请求体**

```json
{
  "state": "FROZEN"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| state | string | ✅ | 目标状态：FROZEN（冻结）/ NORMAL（正常） |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "冻结/解冻交付物失败",
  "data": "请勿跨项目操作"
}
```

---

### 8. 批量替换交付物

**POST** `/deliverable/replace`

**权限要求**：节点操作权限（`pm.product_manifest.deliverable_edit`）

**说明**：使用原始交付物批量替换多个硬件的交付物

**请求体**

```json
{
  "originalId": 1,
  "updateIds": [2, 3, 4]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| originalId | int | ✅ | 原始硬件交付物映射ID |
| updateIds | array | ✅ | 要替换的硬件交付物映射ID列表 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 9. 获取可复用交付物列表

**GET** `/deliverable/reuse`

**说明**：获取可复用的通用程序交付物列表

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categoryId | int | 否 | 硬件分类ID |
| key | string | 否 | 搜索关键字 |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "create_time": "2026-01-01",
      "reuse_status": "ORIGINAL",
      "project_info": {
        "id": 10,
        "name": "智能门锁项目",
        "model": "标准型"
      },
      "hardware_info": {
        "id": 20,
        "name": "STM32F103",
        "version": "1.0",
        "category": {
          "id": 1,
          "name": "MCU"
        }
      },
      "attachment_info": {
        "id": 100,
        "name": "common_firmware.hex",
        "creator": "张三",
        "create_time": "2026-01-01",
        "state": "NORMAL",
        "operation": true,
        "type": "COMMON",
        "note": "通用程序",
        "file_name": "common_firmware.hex"
      }
    }
  ],
  "total": 50
}
```

---

### 10. 复用交付物

**POST** `/deliverable/reuse`

**权限要求**：节点操作权限（`pm.product_manifest.deliverable_edit`）

**说明**：复用已有的通用程序交付物

**请求体**

```json
{
  "id": 1,
  "hardwareId": 10,
  "nodeId": 50
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | ✅ | 复用来源硬件交付物映射ID |
| hardwareId | int | ✅ | 当前项目硬件ID |
| nodeId | int | ✅ | 当前节点ID |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "复用失败",
  "data": "该交付物为复用状态，请勿重复复用"
}
```

```json
{
  "msg": "复用失败",
  "data": "该交付物为非通用程序，请勿复用"
}
```

```json
{
  "msg": "复用失败",
  "data": "该交付物为 冻结 状态，请勿复用"
}
```

---

### 11. 替换为复用交付物

**PUT** `/deliverable/reuse/<action>`

**权限要求**：节点操作权限（`pm.product_manifest.deliverable_edit`）

**说明**：选择复用程序替换当前程序的交付物

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| action | int | 要替换的硬件交付物映射ID |

**请求体**

```json
{
  "id": 1,
  "nodeId": 50,
  "hardwareId": 10
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | ✅ | 复用来源硬件交付物映射ID |
| hardwareId | int | ✅ | 当前项目硬件ID |
| nodeId | int | ✅ | 当前节点ID |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "操作失败",
  "data": "该交付物已被复用，不可替换"
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

### HardwareDeliverable（硬件交付物）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物ID |
| file | int | 关联的交付物文件ID |
| state | string | 交付物状态（NORMAL/FROZEN/INITIAL_FROZEN/STORAGE_MIGRATION_ERROR） |
| type | string | 交付物类型（COMMON=通用程序，STANDARD=标准程序） |
| version | string | 文件版本 |
| creator | int | 创建人ID |
| create_time | datetime | 创建时间 |
| update_by | int | 最后修改人ID |
| update_time | datetime | 最后修改时间 |

### 属性方法

| 属性 | 类型 | 说明 |
|------|------|------|
| name | string | 文件名称（从关联的 file 主表获取） |
| size | int | 文件大小（从关联的 file 主表获取） |
| category | string | 文件类型（从关联的 file 主表获取） |
| token | string | 文件唯一标识（从关联的 file.feishu 子表获取） |
| folder | string | 文件夹路径（从关联的 file.feishu 子表获取） |
| path | string | 文件路径（从关联的 file.feishu 子表获取） |

### HardwareDeliverableMapping（硬件交付物映射）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 映射ID |
| deliverable | int | 硬件交付物ID |
| hardware | int | 项目硬件ID |
| node | int | 所属节点ID |
| reuse_status | string | 复用状态（ORIGINAL=原始附件，REUSED=直接复用） |
| remark | string | 备注 |
| creator | int | 创建人ID |
| create_time | datetime | 创建时间 |
| update_by | int | 最后修改人ID |
| update_time | datetime | 最后修改时间 |

---

## 枚举说明

### DeliverableState（交付物状态）

| 值 | 说明 |
|------|------|
| NORMAL | 正常 |
| FROZEN | 冻结 |
| INITIAL_FROZEN | 初始冻结（新上传的交付物，等待异步处理） |
| STORAGE_MIGRATION_ERROR | 储存迁移异常 |

### DeliverableType（交付物类型）

| 值 | 说明 |
|------|------|
| COMMON | 通用程序 |
| STANDARD | 标准程序 |

### ReuseStatus（复用状态）

| 值 | 说明 |
|------|------|
| ORIGINAL | 原始附件（未复用） |
| REUSED | 直接复用 |

---

## 权限说明

### 节点操作权限

| 权限码 | 说明 |
|-------|------|
| pm.product_manifest.edit | 配置清单编辑 |
| pm.product_manifest.deliverable_view | 配置清单交付物查看 |
| pm.product_manifest.deliverable_edit | 配置清单交付物编辑 |

### 接口权限对照

| 接口 | 权限码 |
|------|-------|
| GET 获取/检查交付物 | `deliverable_view` 或 `deliverable_edit` |
| POST 创建交付物 | `deliverable_edit` |
| PUT 更新交付物 | `deliverable_edit` |
| PATCH 替换交付物 | `deliverable_edit` |
| DELETE 删除交付物 | `deliverable_edit` |
| PATCH 设为通用程序 | `deliverable_edit` |
| PATCH 冻结/解冻 | 独立冻结权限校验 |
| POST 批量替换 | `deliverable_edit` |

### 交付物下载权限

**冻结状态检查：**
- state 为 NORMAL 的可以下载
- state 为 INITIAL_FROZEN 的情况下仅允许创建者、超级管理员可下载

**权限验证（统一通过 AuthorityVerifier）：**
- 超级用户可下载
- 通过 AuthorityVerifier 验证拥有 `pm.product_manifest.deliverable_view` 或 `pm.product_manifest.deliverable_edit` 权限的用户可下载

---

## 业务流程说明

### 1. 硬件交付物创建流程

```
1. 用户上传文件到交付物文件表（DeliverableFile）
2. 创建硬件交付物记录（HardwareDeliverable）
3. 创建硬件交付物映射记录（HardwareDeliverableMapping）
4. 记录操作日志
5. 返回交付物历史记录
```

### 2. 硬件交付物复用流程

```
1. 查询可复用的通用程序列表（GET /deliverable/reuse）
2. 选择要复用的交付物
3. 创建新的映射记录，复用状态为 REUSED
4. 记录操作日志
```

### 3. 硬件交付物冻结流程

```
1. 选择要冻结的交付物（同一项目内）
2. 批量更新交付物状态为 FROZEN
3. 冻结后的交付物不可下载（除创建者和管理员）
4. 记录操作日志
```

### 4. 硬件交付物替换流程

```
单个替换（PATCH /deliverable/instance/<id>）：
1. 上传新文件
2. 创建新的交付物记录
3. 更新映射记录关联到新交付物
4. 查找所有使用旧交付物的项目，返回列表

批量替换（POST /deliverable/replace）：
1. 选择原始交付物
2. 批量更新多个映射记录关联到原始交付物
3. 所有映射记录的复用状态更新为 REUSED
4. 记录操作日志
```

---

## 完整 cURL 示例

```bash
# 1. 获取/检查硬件交付物
curl -X GET "http://your-domain.com/hardwares/deliverable/instance/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建硬件交付物
curl -X POST "http://your-domain.com/hardwares/deliverable/instance" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "hardwareId": 10,
    "fileId": 100,
    "nodeId": 50
  }'

# 3. 更新硬件交付物
curl -X PUT "http://your-domain.com/hardwares/deliverable/instance/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "version": "1.0.0",
    "remark": "稳定版本"
  }'

# 4. 替换硬件交付物（单个）
curl -X PATCH "http://your-domain.com/hardwares/deliverable/instance/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "fileId": 101
  }'

# 5. 删除硬件交付物
curl -X DELETE "http://your-domain.com/hardwares/deliverable/instance/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 6. 设置为通用程序
curl -X PATCH "http://your-domain.com/hardwares/deliverable/common/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "COMMON"
  }'

# 7. 批量冻结程序
curl -X PATCH "http://your-domain.com/hardwares/deliverable/freeze/1,2,3" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "state": "FROZEN"
  }'

# 8. 批量替换交付物
curl -X POST "http://your-domain.com/hardwares/deliverable/replace" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "originalId": 1,
    "updateIds": [2, 3, 4]
  }'

# 9. 获取可复用交付物列表
curl -X GET "http://your-domain.com/hardwares/deliverable/reuse?categoryId=1&key=firmware" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 10. 复用交付物
curl -X POST "http://your-domain.com/hardwares/deliverable/reuse" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 1,
    "hardwareId": 10,
    "nodeId": 50
  }'

# 11. 替换为复用交付物
curl -X PUT "http://your-domain.com/hardwares/deliverable/reuse/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": 2,
    "nodeId": 50,
    "hardwareId": 10
  }'
```
