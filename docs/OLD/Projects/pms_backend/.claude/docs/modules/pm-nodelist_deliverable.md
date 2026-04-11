# PM 节点交付物模块 (PM NodeList Deliverable Module)

## 模块定位

PM/nodelist/deliverable 是 PM 节点列表模块的子模块，负责在节点详情接口中返回节点关联的交付物信息。

**模块路径**: `apps/PM/nodelist/deliverable/`

## 核心职责

1. **交付物信息序列化**：将节点实例转换为交付物列表
2. **关联链路查询**：通过节点定义关联链路获取交付物定义
3. **只读数据输出**：仅提供数据查询，不涉及写入操作

## 模块边界

### 包含的功能
- 节点交付物列表查询（通过 NodeDeliverableSerializer）
- 交付物定义信息输出（名称、编码、必填状态、文件扩展名等）

### 不包含的功能
- 交付物文件上传/存储（PM/deliverable 负责）
- 交付物定义管理（PSC/deliverable_definition 负责）
- 节点定义管理（PSC/node/definition 负责）
- 项目模板管理（PSC/project/template 负责）

## 核心数据模型

### 关联链路

```
Project_Node (项目节点)
    ↓ node_definition (FK)
ProjectTemplateNodeMapping (项目模板节点映射)
    ↓ node_definition_version (FK)
NodeDefinitionVersion (节点定义版本)
    ↓ deliverable_mappings (related_name)
NodeDefinitionDeliverableMapping (节点定义交付物关联)
    ↓ deliverable_definition_version (FK)
DeliverableDefinitionVersion (交付物定义版本)
    ↓ deliverable_definition (FK)
DeliverableDefinition (交付物定义)
```

### 核心模型说明

**Project_Node（项目节点）**：
- `node_definition`: 关联到 ProjectTemplateNodeMapping
- 通过此关联可获取节点的交付物配置

**NodeDefinitionVersion（节点定义版本）**：
- `deliverable_mappings`: 反向关联到 NodeDefinitionDeliverableMapping
- 包含节点的交付物配置

**NodeDefinitionDeliverableMapping（节点定义交付物关联）**：
- `node_definition_version`: 关联节点定义版本
- `deliverable_definition_version`: 关联交付物定义版本
- `is_required`: 是否必填（节点级别控制）
- `function_restriction`: 功能限制（EDIT/READ_ONLY）
- `sort_order`: 排序

**DeliverableDefinitionVersion（交付物定义版本）**：
- `deliverable_definition`: 关联交付物定义主表
- `is_link_first`: 是否链接优先
- `allowed_file_extensions`: 允许的文件扩展名（ManyToMany）

**DeliverableDefinition（交付物定义）**：
- `code`: 唯一标识（如 DELIV0001）
- `name`: 交付物名称

**FileExtensionType（文件扩展名类型）**：
- `name`: 扩展名（如 .pdf, .docx）

## API 输出格式

### 节点详情接口返回结构

```json
{
  "features": {
    "deliverable": {
      "list": [
        {
          "id": 1,
          "name": "项目需求",
          "code": "PROJECT_REQUIREMENT",
          "required": true,
          "isLinkFirst": false,
          "allowedFileExtensions": [".pdf", ".docx"],
          "functionRestriction": "EDIT"
        }
      ]
    }
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 | 来源 |
|------|------|------|------|
| `id` | Integer | 交付物定义版本ID | DeliverableDefinitionVersion.id |
| `name` | String | 交付物名称 | DeliverableDefinition.name |
| `code` | String | 交付物编码 | DeliverableDefinition.code |
| `required` | Boolean | 是否必填 | NodeDefinitionDeliverableMapping.is_required |
| `isLinkFirst` | Boolean | 是否链接优先 | DeliverableDefinitionVersion.is_link_first |
| `allowedFileExtensions` | Array[String] | 允许的文件扩展名 | FileExtensionType.name |
| `functionRestriction` | String | 功能限制 | NodeDefinitionDeliverableMapping.function_restriction |

## 与其他模块关系

### 依赖的模块

```
apps.PM.nodelist
  └── serializers.py (ReadSerializer) - 使用 NodeDeliverableSerializer

apps.PSC.node.definition
  └── NodeDefinitionVersion - 节点定义版本模型

apps.PSC.node.deliverable
  └── NodeDefinitionDeliverableMapping - 节点定义交付物关联

apps.PSC.deliverable.definition
  └── DeliverableDefinition - 交付物定义主表
  └── DeliverableDefinitionVersion - 交付物定义版本

apps.PSC.deliverable.file_extension_type
  └── FileExtensionType - 文件扩展名类型
```

### 被依赖的模块

```
apps.PM.nodelist.serializers
  └── ReadSerializer.get_features() - 节点详情接口
```

## 技术实现要点

### 序列化器实现

**NodeDeliverableSerializer**：
```python
class NodeDeliverableSerializer(serializers.Serializer):
    """
    节点交付物序列化器
    """
    def to_representation(self, instance):
        # 获取交付物列表
        deliverable_mappings = instance.node_definition.node_definition_version \
                               .deliverable_mappings.all().order_by('sort_order')

        # 构造返回数据
        deliverable_list = []
        for mapping in deliverable_mappings:
            deliverable_def_version = mapping.deliverable_definition_version
            if not deliverable_def_version:
                continue

            deliverable_def = deliverable_def_version.deliverable_definition
            allowed_extensions = list(
                deliverable_def_version.allowed_file_extensions.values_list('name', flat=True)
            )

            deliverable_list.append({
                "id": deliverable_def_version.id,
                "name": deliverable_def.name,
                "code": deliverable_def.code,
                "required": mapping.is_required,
                "isLinkFirst": deliverable_def_version.is_link_first,
                "allowedFileExtensions": allowed_extensions,
                "functionRestriction": mapping.function_restriction,
            })

        return {'list': deliverable_list}
```

### 在 ReadSerializer 中使用

```python
from .deliverable.serializers import NodeDeliverableSerializer

class ReadSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()

    def get_features(self, obj):
        return {
            'review': self._get_review_info(obj),
            'deliverable': self._get_deliverable_info(obj),
        }

    def _get_deliverable_info(self, instance):
        serializer = NodeDeliverableSerializer(instance)
        return serializer.data
```

## 设计原则

### 1. 只读序列化器
- NodeDeliverableSerializer 继承自 `serializers.Serializer`（非 ModelSerializer）
- 仅提供 `to_representation` 方法
- 不涉及数据写入操作

### 2. 参考评审项模块设计
- 与 NodeReviewSerializer 保持一致的实现模式
- 通过关联链路获取配置信息
- 返回统一的列表结构

### 3. 版本锁定机制
- 交付物定义通过版本号锁定
- 节点创建时关联特定版本的交付物定义
- 确保历史节点不受后续配置变更影响

## 常见业务场景

### 场景 1：查询节点交付物列表

```http
GET /pm/nodelist/{id}
Response: {
  "features": {
    "deliverable": {
      "list": [...]
    }
  }
}
```

### 场景 2：节点创建时继承交付物配置

1. 项目从模板创建时，节点关联 ProjectTemplateNodeMapping
2. ProjectTemplateNodeMapping 关联 NodeDefinitionVersion
3. NodeDefinitionVersion 包含 deliverable_mappings
4. 节点详情查询时自动返回交付物列表

## 特殊名词索引

当用户提到以下名词时，应定位到此模块：

- **节点交付物**、**NodeDeliverable** → PM/nodelist/deliverable
- **交付物列表**、**attach_rule** → PM/nodelist/deliverable
- **节点交付物信息**、**交付物配置** → PM/nodelist/deliverable
- **allowedFileExtensions** → 文件扩展名列表
- **functionRestriction** → 功能限制（EDIT/READ_ONLY）

## 扩展设计策略

### 当前架构优势

1. **版本化配置**：交付物定义采用版本管理，确保历史节点不受配置变更影响
2. **关联链路清晰**：通过 node_definition → node_definition_version → deliverable_mappings 链路查询
3. **职责分离**：仅负责序列化输出，不涉及交付物文件管理

### 未来演进方向

1. **缓存优化**：对交付物列表进行缓存，减少数据库查询
2. **权限控制**：根据用户权限过滤可查看的交付物
3. **状态追踪**：添加交付物提交状态（已提交/未提交）
4. **批量查询优化**：使用 prefetch_related 优化查询性能

## 相关文件清单

### 核心文件

| 文件 | 说明 |
|------|------|
| `apps/PM/nodelist/deliverable/serializers.py` | 序列化器定义 |
| `apps/PM/nodelist/deliverable/__init__.py` | 模块初始化 |

### 关联文件

| 文件 | 说明 |
|------|------|
| `apps/PM/nodelist/serializers.py` | 节点序列化器（调用 NodeDeliverableSerializer） |
| `apps/PSC/node/deliverable/models.py` | 节点定义交付物关联模型 |
| `apps/PSC/deliverable/definition/models.py` | 交付物定义模型 |
| `apps/PSC/deliverable/file_extension_type/models.py` | 文件扩展名类型模型 |
| `apps/PSC/node/definition/models.py` | 节点定义版本模型 |

## 版本历史

### vX.X.X - is_required 来源迁移 (2026-03-27)

- [x] `required` 字段来源从 `DeliverableDefinitionVersion.is_required` 改为 `NodeDefinitionDeliverableMapping.is_required`
- [x] 节点完成校验中的必填交付物判断逻辑更新
