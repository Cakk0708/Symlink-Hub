---
name: API-response
description: PMS API 接口响应参考专家，提供接口请求参数和响应数据结构作为参考。当用户提到"接口"、"API"、"取项目列表接口"、"pm/project/list"或相关术语时激活此技能。
---

# PMS API 接口响应参考 (API Response Reference)

## 简介

本技能提供 PMS 项目的 API 接口响应数据结构参考，用于帮助理解和处理接口返回的数据格式。

## 触发条件 (When to use)

在以下情况下激活此技能：

- 用户询问"接口"、"API"、"接口响应"、"返回数据"相关的问题
- 用户提到"取项目列表接口"、"项目列表接口"、"pm/project/list"
- 用户需要了解接口的请求参数和响应结构
- 用户需要调试接口数据或处理接口返回的数据

## 详细指令

### 1. 使用接口参考

当用户提到接口相关问题时，按以下步骤操作：

1. **检查 references/ 目录**：查找对应的接口参考文件
2. **提供请求参数说明**：解释接口的请求参数
3. **提供响应数据结构**：展示接口的响应数据格式
4. **提供代码示例**：如有需要，提供调用接口的代码示例

### 2. 已收录的接口

| 接口名称 | 接口地址 | 参考文件 |
|---------|---------|---------|
| 取项目列表 | `GET pm/project/list` | `references/取项目列表.json` |

### 3. 接口参考文件格式

每个接口参考文件应包含：

```json
{
  "接口名称": "取项目列表",
  "接口地址": "GET pm/project/list",
  "请求参数": {
    "参数名": {
      "类型": "参数类型",
      "必填": "是/否",
      "说明": "参数说明"
    }
  },
  "响应结构": {
    "data": {
      "字段说明": "字段含义"
    }
  },
  "示例响应": {
    "实际数据示例": "..."
  }
}
```

## 示例 (Examples)

### 示例 1：用户询问项目列表接口

**用户**：取项目列表接口的参数有哪些？

**助手**：取项目列表接口 `GET pm/project/list` 的请求参数如下：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | Number | 是 | 跳过的记录数（分页偏移量） |
| type | String | 是 | 项目类型（ALL/PRO/COM/CHG/CHGS/SUS/RPB/FLW/IND） |
| limit | Number | 是 | 每页返回数量，默认为 15 |
| participant | String | 否 | 参与者类型筛选，多个用逗号分隔 |
| owner | String | 否 | 负责人筛选，多个用逗号分隔 |
| customer | String | 否 | 客户筛选，多个用逗号分隔 |
| order | String | 否 | 下单状态筛选（ALL/True/False） |
| time_type | String | 否 | 时间类型筛选 |
| start_time | String | 否 | 开始时间（格式：YYYY-MM-DD HH:mm:ss） |
| end_time | String | 否 | 结束时间（格式：YYYY-MM-DD HH:mm:ss） |
| sort | String | 否 | 排序字段（如：CT:DESC,GT:ASC,OWN:ASC） |

详细响应数据结构请参考 `references/取项目列表.json`。

---

### 示例 2：用户需要调试接口数据

**用户**：我需要处理项目列表接口返回的数据，但不知道数据结构

**助手**：项目列表接口 `GET pm/project/list` 的响应数据结构如下：

```javascript
{
  statusCode: 200,
  data: {
    data: {
      list: [
        {
          id: "项目ID",
          project_id: "项目ID",
          name: "项目名称",
          state: 1,  // 1=进行中，2=已完成，3=变更中，4=暂停
          owner: {
            id: "负责人ID",
            nickname: "负责人姓名"
          },
          customer: "客户名称",
          create_time: "2024-01-01 00:00:00",
          deadline_time: "2024-12-31 00:00:00",
          complete_time: "完成时间",
          temp_pause_time: "暂停时间",
          archive_time: "归档时间",
          expire_status: "ACTIVE",  // ACTIVE=正常, EXPIRING=有超期风险, EXPIRED=已超期
          milestone: [
            {
              id: "里程碑ID",
              name: "里程碑名称",
              state: 1  // 0=未开始，1=进行中，2=已完成
            }
          ],
          progress: "项目进展描述",
          todo_node: {
            name: "待处理节点名称",
            is_overdue: false,
            list: [...]
          },
          change: {
            type: "变更类型",
            reason: "变更原因",
            complete_time: "变更完成时间"
          },
          place_order_flag: true,  // 是否已下单
          last_updated: false,     // 是否最后更新
          is_overdue: false        // 是否超期
        }
      ],
      total: 100  // 项目总数
    }
  }
}
```

完整的数据结构请参考 `references/取项目列表.json`。

---

### 示例 3：用户询问如何添加新接口参考

**用户**：我想添加一个新接口的参考文档

**助手**：按以下步骤添加新接口参考：

1. **创建参考文件**：在 `references/` 目录下创建 `{接口名称}.json` 文件
2. **填写接口信息**：包含接口名称、地址、请求参数、响应结构、示例响应
3. **更新 SKILL.md**：在"已收录的接口"表格中添加新接口条目

参考 `references/取项目列表.json` 的格式创建新接口参考文件。

## 特有名词索引

| 名词 | 说明 |
|------|------|
| pm/project/list | 取项目列表接口地址 |
| skip | 分页偏移量参数 |
| type | 项目类型参数 |
| expire_status | 超期状态（ACTIVE/EXPIRING/EXPIRED） |
| milestone | 里程碑数组 |
| todo_node | 待处理节点对象 |