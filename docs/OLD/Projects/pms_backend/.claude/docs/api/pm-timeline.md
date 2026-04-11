# PM - Timeline 接口文档

> 最后更新：2026-03-31
> App: `PM` | Model: `Project_Node`
> Base URL: `/timeline`

---

## 模块说明

时间线模块用于管理项目节点的时间规划，支持获取和更新项目里程碑节点的时间范围。该模块提供项目时间线的可视化数据，并支持时间分配算法。

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
| GET | `/timeline/{project_id}` | 获取项目时间线 | ✅ |
| PUT | `/timeline/{project_id}` | 更新项目时间线 | ✅ |

---

## 接口详情

### 1. 获取项目时间线

获取指定项目的里程碑节点时间线信息。

**请求**

```
GET /timeline/{project_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID（通过URL路径传递） |

**请求示例**

```bash
curl -X GET "/timeline/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "项目启动",
        "state": 0,
        "startTime": "2024-01-01",
        "endTime": "2024-01-31"
      },
      {
        "id": 2,
        "name": "需求确认",
        "state": 1,
        "startTime": "2024-02-01",
        "endTime": "2024-02-15"
      },
      {
        "id": 3,
        "name": "设计完成",
        "state": 2,
        "startTime": "2024-02-16",
        "endTime": "2024-03-31"
      }
    ],
    "createTime": "2023-12-01",
    "deadlineTime": "2024-12-31"
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 里程碑节点列表 |
| items[].id | integer | 节点ID |
| items[].name | string | 节点名称 |
| items[].state | integer | 节点状态（0=待处理，1=进行中，2=已完成，4=项目变更中，5=申请中） |
| items[].startTime | string | 开始时间（YYYY-MM-DD格式） |
| items[].endTime | string | 结束时间（YYYY-MM-DD格式） |
| createTime | string | 项目创建时间 |
| deadlineTime | string | 项目交付时间 |

**业务逻辑说明**

1. **仅显示里程碑节点**: 只返回 `category` 为 `MILESTONE` 的节点
2. **按ID排序**: 节点按 `id` 升序排列
3. **时间格式**: 所有时间转换为本地时区并以 `YYYY-MM-DD` 格式返回

**错误响应**

```json
{
  "msg": "获取时间线失败, 项目不存在"
}
```

```json
{
  "msg": "获取时间线失败"
}
```

---

### 2. 更新项目时间线

批量更新项目节点的时间范围，系统会自动分配子节点时间。

**请求**

```
PUT /timeline/{project_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID（通过URL路径传递） |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| timeline | array | ✅ | 时间线数据数组 |
| timeline[].nodeId | integer | ✅ | 节点ID（里程碑节点） |
| timeline[].startDate | string | ✅ | 开始时间（ISO 8601格式） |
| timeline[].endDate | string | ✅ | 结束时间（ISO 8601格式） |

**请求示例**

```bash
curl -X PUT "/timeline/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "timeline": [
      {
        "nodeId": 1,
        "startDate": "2024-01-01T00:00:00Z",
        "endDate": "2024-01-31T23:59:59Z"
      },
      {
        "nodeId": 2,
        "startDate": "2024-02-01T00:00:00Z",
        "endDate": "2024-02-28T23:59:59Z"
      },
      {
        "nodeId": 3,
        "startDate": "2024-03-01T00:00:00Z",
        "endDate": "2024-03-31T23:59:59Z"
      }
    ]
  }'
```

**响应示例**

```json
{
  "msg": "时间线设置成功"
}
```

**业务逻辑说明**

1. **时间验证**
   - 开始时间不能晚于结束时间
   - 历史验证（v1.3.6版本已关闭）：
     - 开始时间不能早于项目创建时间
     - 结束时间不能晚于项目交付时间
   - 里程碑开始时间不能早于前一个里程碑的开始时间

2. **时间分配算法**
   - **里程碑节点**: 直接设置开始和结束时间
   - **主节点**: 时间跟随所属里程碑
   - **子节点**: 时间在主节点范围内平均分配
     - 当子节点数 ≤ 总天数：平均分配天数
     - 当子节点数 > 总天数：同一天可能有多个节点

3. **事务安全**: 所有更新在原子事务中执行，确保数据一致性

4. **操作日志**: 自动记录"更新项目时间线"操作日志

**时间分配示例**

假设里程碑时间范围为 2024-01-01 至 2024-01-10（10天），有 3 个子节点：

```
节点1: 2024-01-01 至 2024-01-04  (4天)
节点2: 2024-01-05 至 2024-01-07  (3天)
节点3: 2024-01-08 至 2024-01-10  (3天)
```

如果只有 10 个子节点但时间范围只有 5 天：

```
节点1-2:  2024-01-01
节点3-4:  2024-01-02
节点5-6:  2024-01-03
节点7-8:  2024-01-04
节点9-10: 2024-01-05
```

**错误响应**

```json
{
  "msg": "时间修改失败：开始时间 不可晚于 结束时间"
}
```

```json
{
  "msg": "开始时间不能早于前一个里程碑的开始时间"
}
```

```json
{
  "msg": "时间线数据验证失败：请设置时间线"
}
```

```json
{
  "msg": "更新失败: <错误详情>"
}
```

---

## 数据模型

### Project_Node（项目节点）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 节点ID |
| name | String | 节点名称 |
| start_time | DateTime | 开始时间 |
| end_time | DateTime | 结束时间 |
| complete_time | DateTime | 完成时间 |
| state | String | 节点状态 |
| node_category | String | 节点分类（MILESTONE/MAIN_NODE/SUB_NODE） |
| node_definition | ForeignKey | 节点定义（PSC.NodeDefinitionVersion） |
| list | ForeignKey | 所属项目（Project_List） |
| parent | ForeignKey | 父节点（自关联） |
| node_parent_id | Integer | 父节点ID |

---

## 枚举值说明

### NodeState（节点状态）

| 值 | 说明 | 颜色 |
|----|------|------|
| 0 | 待处理 | 灰色 (#d2d3d7) |
| 1 | 进行中 | 黄色 (#efc95f) |
| 2 | 已完成 | 绿色 (#68b948) |
| 4 | 项目变更中 | 紫色 (#793AFF) |
| 5 | 申请中 | 紫色 (#793AFF) |

### NodeCategory（节点分类）

| 值 | 说明 |
|----|------|
| MILESTONE | 里程碑节点 |
| MAIN_NODE | 主节点 |
| SUB_NODE | 子节点 |

---

## 树形结构说明

项目节点采用三层树形结构：

```
里程碑节点 (MILESTONE)
├── 主节点 (MAIN_NODE)
│   ├── 子节点 (SUB_NODE)
│   ├── 子节点 (SUB_NODE)
│   └── ...
└── 主节点 (MAIN_NODE)
    ├── 子节点 (SUB_NODE)
    └── ...
```

**层级关系**:
- 里程碑节点为根节点（无父节点）
- 主节点的 `parent` 指向里程碑节点
- 子节点的 `parent` 指向主节点

---

## 时间分配算法

### split_time_for_sub_nodes 函数

将时间段平均分配给子节点，每个节点至少分配一天。

**参数**:
- `start_time`: 开始日期
- `end_time`: 结束日期
- `node_count`: 子节点数量

**分配规则**:
1. 当 `node_count <= total_days`: 平均分配天数
   - 计算每个节点的基础天数 = `total_days // node_count`
   - 余数天数依次分配给前 `total_days % node_count` 个节点
2. 当 `node_count > total_days`: 同一天可能有多个节点
   - 计算每天的基础节点数 = `node_count // total_days`
   - 余数节点依次分配给前 `node_count % total_days` 天

**返回**: 包含每个节点开始和结束时间的字典列表

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
| 404 | 项目不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取项目时间线
curl -X GET "/timeline/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 更新项目时间线
curl -X PUT "/timeline/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "timeline": [
      {
        "nodeId": 1,
        "startDate": "2024-01-01T00:00:00+08:00",
        "endDate": "2024-01-31T23:59:59+08:00"
      },
      {
        "nodeId": 2,
        "startDate": "2024-02-01T00:00:00+08:00",
        "endDate": "2024-02-28T23:59:59+08:00"
      },
      {
        "nodeId": 3,
        "startDate": "2024-03-01T00:00:00+08:00",
        "endDate": "2024-03-31T23:59:59+08:00"
      }
    ]
  }'
```

---

## 相关接口

- `GET /project/node` - 获取项目节点列表
- `GET /project/node/{id}` - 获取节点详情
- `PUT /project/node/{id}` - 更新节点信息

---

## 注意事项

1. **时区处理**: 所有时间会转换为本地时区（Asia/Shanghai）后返回
2. **事务安全**: 更新操作使用数据库事务，确保数据一致性
3. **操作日志**: 所有时间线更新操作会自动记录到项目操作日志
4. **历史验证**: v1.3.6版本已关闭历史时间验证，允许设置任意时间范围
5. **子节点自动分配**: 更新里程碑时间后，子节点时间会自动重新分配
