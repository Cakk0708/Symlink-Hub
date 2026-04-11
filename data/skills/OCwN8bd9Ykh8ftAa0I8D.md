---
name: apifox-import
description: 根据Django REST Framework模块代码生成Apifox导入文件(.apifox.json)。当用户说"生成xxx模块的.apifox.json文件"、"导出接口文档"或提到"apifox导入"时激活。
---

# Apifox 导入文件生成技能

## 简介

本技能用于根据 Django REST Framework 模块的现有代码（models/serializers/views/urls），生成符合 Apifox 规范的 `.apifox.json` 文件，可直接导入 Apifox 形成完整的接口文档和测试用例。

## 触发条件 (When to use)

当出现以下任一情况时，激活此技能：

1. 用户说"生成xxx模块的.apifox.json文件"（如"生成BDM/customer模块的.apifox.json文件"）
2. 用户说"导出接口文档"、"生成API文档"
3. 用户提到"apifox导入"、"接口设计文档"
4. 用户询问某个模块的接口列表设计

## 详细指令 (Instructions)

### 第一步：分析 Django 模块代码

1. **读取模块的四个核心文件**：
   ```
   apps/<MODULE>/<module>/models.py
   apps/<MODULE>/<module>/serializers.py
   apps/<MODULE>/<module>/views.py
   apps/<MODULE>/<module>/urls.py
   ```

2. **从 models.py 提取**：
   - 模型类名 (`class Customer`)
   - 字段定义 (`name = CharField`)
   - 字段类型（CharField → string, IntegerField → integer 等）
   - 必填字段（没有 blank=True 或 default 值）

3. **从 views.py 提取**：
   - 视图集类名 (`CustomerViewSet`)
   - 继承的基类 (`ModelViewSet` → CRUD, `ReadOnlyModelViewSet` → 只读)
   - 自定义 action 方法

4. **从 urls.py 提取**：
   - URL 路径前缀 (`router.register(r'customers', ...)`)
   - 完整路径模式 (`/bdm/customers`)

### 第二步：生成 .apifox.json 结构

按照 PMS-BDM.apifox.json 的参考格式，生成以下结构：

```json
{
  "apifoxProject": "1.0.0",
  "$schema": {
    "app": "apifox",
    "type": "project",
    "version": "1.2.0"
  },
  "info": {
    "name": "PMS",
    "description": ""
  },
  "projectSetting": {
    "id": "2456699",
    "language": "zh-CN",
    "apiStatuses": ["developing", "testing", "released", "deprecated", "pending"]
  },
  "apiCollection": [
    {
      "name": "Root",
      "id": 78507476,
      "parentId": 0,
      "items": [
        {
          "name": "{ModelName}-{模型中文名}",
          "id": {自动生成唯一ID},
          "items": [
            {接口1},
            {接口2},
            ...
          ]
        }
      ]
    }
  ],
  "schemaCollection": [
    {
      "id": 18430808,
      "name": "根目录",
      "items": [
        {
          "id": {唯一ID},
          "name": "{ModelName}",
          "items": [
            {
              "name": "Request",
              "displayName": "请求模型",
              "id": "#/definitions/{定义ID}",
              "schema": {请求体Schema}
            }
          ]
        }
      ]
    }
  ],
  "commonParameters": {
    "parameters": {
      "header": [
        {
          "name": "Authorization",
          "defaultValue": "Bearer {{access_token}}"
        }
      ]
    }
  }
}
```

### 第三步：生成标准 CRUD 接口

根据 PMS 项目的标准模式，每个模型生成以下接口：

| 接口名称 | HTTP 方法 | 路径 | 功能 |
|---------|-----------|------|------|
| 取列表 | GET | `/{module}/{models}` | 分页列表 |
| 取详情 | GET | `/{module}/{models}/{ID}` | 单条详情 |
| Create | POST | `/{module}/{models}` | 批量创建 |
| Update | PUT | `/{module}/{models}/{ID}` | 单条更新 |
| Del | DELETE | `/{module}/{models}` | 批量删除 |

**接口生成模板**：

```json
{
  "name": "取列表",
  "api": {
    "id": "{唯一ID}",
    "method": "get",
    "path": "/{module}/{models}",
    "parameters": {
      "query": [],
      "path": [],
      "header": []
    },
    "commonParameters": {
      "header": [{"name": "Authorization"}]
    },
    "requestBody": {
      "type": "none"
    },
    "responses": [
      {
        "code": 200,
        "name": "成功",
        "jsonSchema": {
          "type": "object",
          "properties": {}
        }
      }
    ]
  }
}
```

### 第四步：生成数据模型 Schema

从 Django 模型字段映射到 JSON Schema：

| Django 字段 | JSON Schema 类型 | 示例 |
|------------|-----------------|------|
| CharField | string | `{"type": "string"}` |
| IntegerField | integer | `{"type": "integer"}` |
| BooleanField | boolean | `{"type": "boolean"}` |
| TextField | string | `{"type": "string"}` |
| DateField | string | `{"type": "string", "format": "date"}` |
| DateTimeField | string | `{"type": "string", "format": "date-time"}` |
| FloatField | number | `{"type": "number"}` |
| DecimalField | number | `{"type": "number"}` |
| JSONField | object | `{"type": "object"}` |
| ForeignKey | integer | `{"type": "integer"}` |
| ManyToManyField | array | `{"type": "array"}` |

### 第五步：PMS 项目特定处理

1. **批量操作模式**：
   - 创建接口：请求体 `{ "models": [...] }`
   - 删除接口：请求体 `{ "ids": [...] }`
   - 响应体：统一 `{ "models": [...] }`

2. **路径参数**：
   - 详情和更新接口需要 `{ID}` 路径参数
   - 参数定义：`{"name": "ID", "required": true, "type": "string"}`

3. **认证**：
   - 所有接口添加 `Authorization` header
   - 默认值：`Bearer {{access_token}}`

4. **状态码**：
   - 200：成功响应
   - 统一返回格式

### 第六步：生成完整文件

将以上内容组合成完整的 `.apifox.json` 文件，确保：
1. 所有 ID 唯一（使用随机整数）
2. JSON 格式正确
3. 包含所有必要的字段
4. 符合 Apifox 导入规范

## 示例 (Examples)

### 示例 1：生成 Customer 模块的 .apifox.json

**用户**：生成BDM/customer模块的.apifox.json文件

**助手**：
1. 读取 `apps/BDM/customer/models.py`，识别 `Customer` 模型
2. 读取 `apps/BDM/customer/views.py`，识别 `CustomerViewSet`
3. 读取 `apps/BDM/customer/urls.py`，识别 URL 路径 `/bdm/customers`
4. 分析模型字段：name, code, remark 等
5. 生成标准 CRUD 接口定义
6. 生成数据模型 Schema
7. 组合成完整的 .apifox.json 文件

### 示例 2：生成 Department 模块的 .apifox.json

**用户**：帮我导出 BDM/department 模块的接口文档

**助手**：
1. 分析 Department 模型的字段
2. 识别部门模块特有的接口（如层级查询）
3. 生成包含所有接口的 .apifox.json 文件

## 参考 Template

### 接口文件夹结构

```
apiCollection[0].items[0] = {
  "name": "Customer-客户列表",
  "id": 78507502,
  "items": [接口数组]
}
```

### 单个接口结构

```
{
  "name": "取列表",
  "api": {
    "id": 418548078,
    "method": "get",
    "path": "/bdm/customers",
    "parameters": {...},
    "commonParameters": {
      "header": [{"name": "Authorization"}]
    },
    "requestBody": {...},
    "responses": [...]
  }
}
```

### Schema 结构

```
schemaCollection[0].items[0].items[0] = {
  "name": "Request",
  "displayName": "请求模型",
  "id": "#/definitions/247721465",
  "schema": {
    "jsonSchema": {
      "type": "object",
      "properties": {
        "name": {"type": "string"}
      },
      "required": ["name"]
    }
  }
}
```

## 注意事项

1. **ID 生成**：所有 id 字段需要唯一，使用递增或随机整数
2. **模型命名**：文件夹名使用 "ModelName-中文名" 格式
3. **路径大小写**：URL 路径使用小写（如 `/bdm/customers`）
4. **必填字段**：从 Django 模型的 `blank=False` 和无默认值推断
5. **外键处理**：ForeignKey 字段映射为 integer 类型
6. **枚举类型**：如有 choices，需在 description 中说明可选项
7. **时间字段**：DateTimeField 添加 format: "date-time"
