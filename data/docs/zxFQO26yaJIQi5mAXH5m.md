# PM 项目文件夹模块

## 模块定位

PM 项目文件夹模块 (`apps/PM/project/folder/`) 负责项目交付物文件夹的查询与展示功能，返回项目下所有 `DELIVERABLE` 类型文件夹及其包含的交付物列表，以树形结构呈现。

**核心职责**：查询项目文件夹、关联交付物实例、构造树形返回结构。

**模块边界**：
- **负责**：文件夹列表查询、交付物分组展示
- **不负责**：文件夹创建（由 `apps/PM/deliverable/folder/tasks.py` 处理）、文件上传、权限验证

## 核心数据模型

### DeliverableFolder (交付物文件夹主表)
```python
# 位置: apps/PM/deliverable/folder/models.py
class DeliverableFolder(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey('PM.Project_List', related_name='deliverable_folders')
    name = models.CharField(max_length=255)  # 文件夹名称
    folder_type = models.CharField choices=['CUSTOMER_ROOT', 'MODEL_ROOT', 'DELIVERABLE']
    storage_provider = models.CharField choices=['FEISHU', 'ALIYUN_OSS']
```

### DeliverableFolderFeishu (飞书存储信息表)
```python
class DeliverableFolderFeishu(models.Model):
    folder = models.OneToOneField(DeliverableFolder, related_name='feishu_storage')
    folder_token = models.CharField(max_length=255, unique=True)
```

### 文件夹层级结构
```
CUSTOMER_ROOT (客户根文件夹)
  └── MODEL_ROOT (机型根文件夹)
        └── DELIVERABLE (交付物文件夹, name=交付物定义code)
              └── 交付物文件...
```

## 核心业务逻辑

### 文件夹与交付物关联机制

**重要**：`DeliverableFolder` 与 `DeliverableInstance` 之间**没有外键关系**，通过以下方式关联：

```python
# 文件夹创建时 (apps/PM/deliverable/folder/tasks.py)
DeliverableFolder.objects.get_or_create(
    project=project,
    folder_type='DELIVERABLE',
    name=deliverable_definition_code,  # name = 交付物定义的 code
)

# 关联查询时
folder.name == deliverable.definition.deliverable_definition.code
```

**关键点**：
- 文件夹的 `name` 字段存储的是 `DeliverableDefinition.code`
- 通过此匹配关系将交付物分组到对应文件夹

### 查询优化
```python
# 使用 select_related 避免 N+1 查询
folders = DeliverableFolder.objects.filter(
    project_id=project_id,
    folder_type='DELIVERABLE'
).select_related('feishu_storage')

deliverables = DeliverableInstance.objects.filter(
    project_node__list_id=project_id
).select_related(
    'file', 'created_by', 'project_node', 'definition__deliverable_definition'
)
```

## API 接口

### GET /pm/project/{id}/folder

**请求**：无参数

**响应**：
```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "DELIV001",
        "deliverables": [
          {
            "id": 1,
            "name": "交付物.pdf",
            "version": "1.0",
            "fileCategory": "file",
            "state": "NORMAL",
            "createdAt": "2026-03-10 10:00:00",
            "createdBy": {"id": 1, "nickname": "张三", "avatar": "xxx"}
          }
        ]
      }
    ],
    "count": 1
  }
}
```

## 代码结构规范

### 目录结构
```
apps/PM/project/folder/
├── __init__.py          # 模块说明
├── views.py             # 视图层（仅负责响应）
└── serializers.py       # 序列化器层（业务逻辑）
```

### 分层职责

**视图层 (`views.py`)**：
- 获取 URL 参数
- 调用序列化器验证
- 返回标准响应格式
- **不包含业务逻辑**

**序列化器层 (`serializers.py`)**：
- `ProjectFolderListSerializer`：主业务逻辑
  - 验证项目存在性
  - 查询文件夹和交付物
  - 构造映射关系
  - 返回序列化数据
- `FolderSerializer`：文件夹序列化
- `DeliverableSerializer`：交付物序列化

### 代码规范

1. **命名规范**：
   - 序列化器类：`XxxSerializer`
   - 视图类：`XxxListView`
   - 字段名：使用 camelCase（前端对接）

2. **返回格式**：
   ```python
   return JsonResponse({
       'msg': 'success',
       'data': {
           'items': data,
           'count': len(data)
       }
   })
   ```

3. **导入顺序**：
   ```python
   # 标准库
   from django.http import JsonResponse

   # 第三方
   from rest_framework import views

   # 本地
   from .serializers import XxxSerializer
   ```

## 常见业务场景

### 场景1：获取项目文件夹列表
```python
# 触发条件：用户访问 GET /pm/project/{id}/folder
# 处理流程：
# 1. 验证项目是否存在
# 2. 查询 DELIVERABLE 类型文件夹
# 3. 查询项目所有交付物
# 4. 通过 folder.name 匹配 definition.code
# 5. 返回树形结构
```

### 场景2：文件夹为空
```python
# 如果项目没有交付物，返回空数组
{
  "msg": "success",
  "data": {"items": [], "count": 0}
}
```

## 技术实现建议

### Django ORM 最佳实践
```python
# ✅ 正确：使用 select_related 优化查询
folders = DeliverableFolder.objects.select_related('feishu_storage')

# ❌ 错误：N+1 查询问题
for folder in folders:
    token = folder.feishu_storage.folder_token  # 每次循环都查询
```

### 序列化器最佳实践
```python
# ✅ 正确：业务逻辑在序列化器的 save() 方法
class ProjectFolderListSerializer(serializers.Serializer):
    def save(self):
        # 查询和业务逻辑
        return serializer.data

# ❌ 错误：业务逻辑在视图层
def get(self, request):
    folders = DeliverableFolder.objects.filter(...)
    # 大量业务逻辑...
```

## 与其他模块关系

| 模块 | 关系 | 说明 |
|------|------|------|
| `apps/PM/deliverable/folder/` | 依赖 | 文件夹模型定义、异步创建任务 |
| `apps/PM/deliverable/instance/` | 依赖 | 交付物实例模型 |
| `apps/PSC/deliverable/definition/` | 依赖 | 交付物定义（获取 code） |
| `apps/PM/project/` | 所属 | 项目模块的子功能 |

## 扩展设计策略

### 支持多存储服务商
当前模型已支持存储服务商抽象：
- `FEISHU`: 飞书云文档
- `ALIYUN_OSS`: 阿里云 OSS

扩展时添加新的 `storage_provider` 选项和对应的存储信息表。

### 文件夹权限控制
未来可添加权限验证：
- 在序列化器中检查用户是否有权限访问项目
- 过滤用户无权限的文件夹

## 特有名词索引

| 名词 | 定位 | 说明 |
|------|------|------|
| `DeliverableFolder` | 数据模型 | 交付物文件夹主表 |
| `folder_type` | 枚举字段 | 文件夹类型：CUSTOMER_ROOT/MODEL_ROOT/DELIVERABLE |
| `folder_token` | 飞书字段 | 飞书文件夹唯一标识 |
| `feishu_storage` | 关联属性 | OneToOne 关联到 DeliverableFolderFeishu |
| `definition_code` | 匹配字段 | 交付物定义编码，用于文件夹名称和匹配 |

## 常见问题

### Q1: 为什么文件夹和交付物没有外键关联？
**A**: 采用松耦合设计，文件夹按交付物定义创建，通过 `name` 字段匹配 `DeliverableDefinition.code` 实现关联。

### Q2: 如何处理空文件夹？
**A**: 直接返回空数组，前端根据 `deliverables.length` 判断是否显示文件夹。

### Q3: 如何区分不同类型的文件夹？
**A**: 使用 `folder_type` 字段过滤，本模块只返回 `DELIVERABLE` 类型。
