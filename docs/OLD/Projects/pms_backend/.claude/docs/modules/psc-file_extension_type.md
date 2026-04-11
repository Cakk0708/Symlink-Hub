# PSC 文件扩展名类型模块技能文档

## 简介

**PSC 文件扩展名类型模块** (`apps/PSC/file_extension_type`) 是交付物定义的公共配置模块，负责管理系统支持的文件扩展名类型。

本模块采用**中央化配置管理**模式，定义所有可用的文件扩展名（如 `.pdf`、`.docx`），供交付物定义模块引用。

## 触发条件 (When to use)

| 触发词/场景 | 说明 |
|------------|------|
| "文件扩展名类型"、"FileExtensionType" | 涉及文件类型定义 |
| "allowed_file_extensions" | 涉及交付物文件类型限制 |
| "文件类型限制"、"允许的文件类型" | 涉及上传文件验证 |
| 修改 `apps/PSC/file_extension_type/` 下的文件 | 直接修改模块代码 |

## 核心指令 (Instructions)

### 1. 模块理解准则

- **定位**：本模块是**公共配置层**，提供文件扩展名类型的增删查功能
- **核心关联**：被 `deliverable_definition.DeliverableDefinitionVersion.allowed_file_extensions` 多对多引用
- **设计简洁**：仅包含 `name` 字段，每个实例代表一个扩展名（如 `.pdf`）

### 2. 代码修改规范

**模型修改**：
- `name` 字段最大长度 50，存储格式如 `.pdf`、`.docx`
- 必须保持唯一性约束
- 不需要 `is_active`、`extensions`、`created_at`、`updated_at` 等冗余字段

**视图修改**：
- 仅支持 GET（查询列表，支持分页）和 POST（创建）
- 不需要 PATCH、DELETE 接口
- 视图仅做服务层，查询集由 `utils.get_list_queryset()` 提供
- **返回格式标准**：使用 `items` + `pagination` 结构（参考 customer 模块）

**序列化器修改**：
- `FileExtensionTypeListSerializer`：输出 `id`、`name`
- `FileExtensionTypeParamsSerializer`：处理查询、分页、排序参数
- `FileExtensionTypeWriteSerializer`：创建时仅验证 `name` 唯一性

### 3. 关键字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | AutoField | 主键 |
| `name` | CharField(50) | 文件扩展名，如 `.pdf`（UNIQUE） |


## 模块定位

**所属系统**: PSC (Project Settings Configuration) - 项目设置配置中心

**核心职责**: 提供文件扩展名类型的集中管理，供交付物定义模块引用。

**架构层级**:
```
PSC (配置中心)
├── file_extension_type (文件扩展名类型) ← 公共配置
└── deliverable_definition (交付物定义)
    └── 版本通过 allowed_file_extensions (M2M) 引用本模块
```

**特有名词索引**:
- `FileExtensionType`: 文件扩展名类型模型
- `allowed_file_extensions`: 交付物版本的多对多字段，引用本模块


## 模块职责边界

### 核心职责

| 职责 | 说明 |
|------|------|
| **扩展名定义** | 定义系统支持的文件扩展名类型 |
| **公共配置** | 为交付物定义提供可复用的文件类型选项 |

### 边界界定

| 归属 | 模块 | 说明 |
|------|------|------|
| ✅ 本模块 | 文件扩展名类型定义（增删查） | 定义"允许什么扩展名" |
| ✅ deliverable_definition | 交付物定义引用扩展名 | 选择需要的扩展名类型 |
| ✅ PM/deliverable | 上传文件时验证 | 验证文件是否符合扩展名限制 |

### 不负责

- ❌ 文件上传验证逻辑（PM/deliverable 负责）
- ❌ 交付物定义管理（deliverable_definition 负责）
- ❌ 文件内容检查（独立服务负责）


## 核心数据模型

### 模型架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    FileExtensionType                         │
│                    (文件扩展名类型)                           │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ name          (文件扩展名，如 ".pdf") ⭐                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ M2M (allowed_file_extensions)
                            │
┌─────────────────────────────────────────────────────────────┐
│              DeliverableDefinitionVersion                    │
│              (交付物定义版本 - 引用方)                        │
├─────────────────────────────────────────────────────────────┤
│ allowed_file_extensions (M2M) → FileExtensionType[]         │
│ └── 一个版本可选择多个扩展名类型                              │
└─────────────────────────────────────────────────────────────┘
```

### 字段详解

#### FileExtensionType

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `name` | CharField(50) | UNIQUE | 文件扩展名，如 `.pdf`、`.docx` |


## 视图架构设计

### 设计标准

本模块遵循项目的标准视图分层架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        视图分层设计                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  utils.py → get_list_queryset()                              │
│      └── 提供基础查询集                                      │
│                                                             │
│  views.py                                                    │
│      └── ListViews  (GET: 查询列表, POST: 创建)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 视图职责划分

| 视图类 | 职责 | 端点 |
|--------|------|------|
| `ListViews` | 查询列表（GET，支持分页）、创建扩展名（POST） | `/list` |

### 分页参数（GET 请求）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| query | string | - | 搜索关键词（匹配 name） |
| pageNum | int | 1 | 页码 |
| pageSize | int | 10 | 每页数量 |
| sortField | string | id | 排序字段 |
| sortOrder | string | asc | 排序方向（asc/desc） |

### 核心设计原则

1. **视图简洁化**：视图仅作为服务层，不包含业务逻辑
2. **查询复用**：基础查询集由 utils 统一提供
3. **功能精简**：仅提供查询和创建功能，无更新和删除
4. **返回标准**：遵循项目标准的 `items` + `pagination` 返回格式


## 权限验证流程

### 当前实现

```python
# views.py
permission_classes = [IsAuthenticated]
```

**说明**: 当前仅实现基础认证（登录验证）。


## 与其他模块关系

### 模块依赖图

```
┌──────────────────────────────────────────────────────────────┐
│                   PSC/file_extension_type                   │
│                   (本模块 - 文件扩展名类型)                   │
└──────┬───────────────────────────────────────────────────────┘
       │ 提供 (M2M)
       ↓
┌──────────────────────────────────────────────────────────────┐
│              PSC/deliverable_definition_version              │
│                   (交付物定义版本)                            │
│   └── allowed_file_extensions (M2M → FileExtensionType)      │
└──────────────────────────────────────────────────────────────┘
```

### 关键关联字段

| 模块 | 关联字段 | 说明 |
|------|----------|------|
| `deliverable_definition_version` | `allowed_file_extensions` (M2M) | 可选择多个扩展名类型 |


## 常见业务场景

### 场景 1: 创建新的文件扩展名类型

```python
# 业务流程
1. 管理员创建 FileExtensionType(name=".pdf")
2. 交付物定义创建时可选择引用 .pdf
3. 用户上传交付物时验证文件扩展名
```

### 场景 2: 交付物定义引用扩展名

```python
# 业务流程
1. 创建交付物版本时设置:
   allowedFileExtensionsIds = [1, 2, 3]  # .pdf, .docx, .xlsx
2. 版本保存后建立多对多关联
3. 前端获取版本时可看到允许的扩展名列表
```


## 技术实现建议 (Django)

### 模型设计要点

```python
# 1. 简洁模型设计
class FileExtensionType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'PSC_file_extension_type'
        ordering = ['name']
```

### 视图设计

```python
# serializers.py - 参数序列化器
class FileExtensionTypeParamsSerializer(serializers.Serializer):
    """处理查询、分页、排序参数"""
    query = serializers.CharField(required=False, default=None)
    pageNum = serializers.IntegerField(required=False, default=1)
    pageSize = serializers.IntegerField(required=False, default=10)
    sortField = serializers.CharField(required=False, default='id')
    sortOrder = serializers.ChoiceField(choices=['asc', 'desc'], required=False, default='asc')

    def get_paginated_queryset(self, queryset):
        """返回 (分页后的查询集, 分页信息字典)"""
        # ... 处理搜索、排序、分页逻辑
        return paginated_queryset, pagination

# views.py - 标准分页返回格式
class ListViews(APIView):
    def get(self, request):
        # 使用参数序列化器统一处理
        params_serializer = FileExtensionTypeParamsSerializer(data=request.GET)
        if not params_serializer.is_valid():
            return Response({'msg': '数据验证失败', 'errors': params_serializer.errors},
                          status=status.HTTP_400_BAD_REQUEST)

        paginated_queryset, pagination = params_serializer.get_paginated_queryset(
            get_list_queryset()
        )
        serializer = FileExtensionTypeListSerializer(paginated_queryset, many=True)

        return Response({
            'msg': 'success',
            'data': {
                'items': serializer.data,      # ← 标准：使用 items
                'pagination': pagination        # ← 标准：分页信息
            }
        })

    def post(self, request):
        serializer = FileExtensionTypeWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'msg': '参数错误', 'errors': serializer.errors},
                          status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response({
            'msg': 'success',
            'data': {'insertId': instance.id}  # ← 标准：创建成功返回 insertId
        }, status=status.HTTP_201_CREATED)
```


## 关键文件索引

| 文件路径 | 说明 |
|----------|------|
| `apps/PSC/file_extension_type/models.py` | 数据模型定义 |
| `apps/PSC/file_extension_type/serializers.py` | 序列化器 |
| `apps/PSC/file_extension_type/views.py` | 视图逻辑 |
| `apps/PSC/file_extension_type/utils.py` | 公共查询函数 |
| `apps/PSC/file_extension_type/urls.py` | 路由配置 |
| `apps/PSC/urls.py` | 主路由引入 |


## 快速参考

### 导入方式

```python
# 从模块直接导入
from apps.PSC.file_extension_type.models import FileExtensionType
```

### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/psc/deliverable/file-extension-type` | GET | 查询扩展名类型列表（支持分页、搜索、排序） |
| `/psc/deliverable/file-extension-type` | POST | 创建扩展名类型 |

**GET 请求示例**：
```http
GET /psc/deliverable/file-extension-type?query=.pdf&pageNum=1&pageSize=10
```

**响应格式**：
```json
{
  "msg": "success",
  "data": {
    "items": [
      {"id": 1, "name": ".pdf"},
      {"id": 2, "name": ".docx"}
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 2,
      "totalPages": 1
    }
  }
}
```


## 扩展设计策略

### 当前设计评估

| 方面 | 评估 | 说明 |
|------|------|------|
| 数据模型 | ✅ 充分 | 单表设计，字段简单 |
| 权限控制 | ⚠️ 基础 | 仅 `IsAuthenticated`，可增加管理员权限 |
| 文件验证 | ⚠️ 简单 | 只验证扩展名，未验证MIME类型 |

### 潜在扩展方向

1. **MIME类型关联**：
   ```python
   class FileExtensionType(models.Model):
       name = models.CharField(...)
       mime_type = models.CharField(max_length=100, blank=True)  # application/pdf
   ```

2. **文件大小限制**：
   ```python
   max_size_mb = models.IntegerField(default=10)  # 该类型文件的最大大小
   ```

3. **分类管理**：
   ```python
   category = models.CharField(...)  # 文档/图片/模型/其他
   ```


## 演进方向 (Future Evolution)

### 短期优化
- [ ] 增加删除接口（需检查是否被引用）
- [ ] 增加批量创建接口

### 中长期规划
- [ ] 支持文件类型分组（文档类、模型类、图片类）
- [ ] 集成前端文件上传组件的自动配置生成
- [ ] 增加文件内容验证（MIME type检查）


## 版本历史 (🆕 Since 2026-02-27)

### v1.1.0 - 标准分页格式 (2026-02-27)

- [x] 添加 `FileExtensionTypeParamsSerializer` 参数序列化器
- [x] 支持分页、搜索、排序功能
- [x] 返回格式统一为 `items` + `pagination` 标准
- [x] 创建成功返回 `insertId`

### v1.0.0 - 初始版本

- [x] 基础模型定义
- [x] GET/POST 接口
- [x] 与 deliverable_definition 模块集成（M2M）
