# PM 节点评审项模块 (PM Node Review)

## 模块定位

PM/nodelist/review 是 PM 节点列表模块的子模块，专门负责**节点评审项**的序列化处理。它是一个轻量级的序列化器模块，不涉及数据库模型的直接操作，而是通过复杂的关联链路从 PSC 模块读取评审项配置数据。

**关键特征：**
- 只读序列化器，不处理创建/更新操作
- 依赖跨模块关联链路（PM → PSC）
- 支持评审项类型动态判断（fixed/custom）


## 模块职责边界

### 核心职责

1. **评审项列表序列化**：将节点的评审项配置转换为前端可用的 JSON 格式
2. **类型判断**：根据评审项是否关联交付物定义，自动判断评审项类型
3. **排序支持**：按配置的 sort_order 返回评审项列表

### 不负责

- 评审项的创建、修改、删除（由 PSC/review_definition 模块负责）
- 节点与评审项的关联配置（由 PSC/node/review 模块负责）
- 评审流程的执行（由 SM/approval 模块负责）
- 评审结果的存储（不在此模块处理）


## 核心数据模型

### 本模块

本模块**没有自己的数据模型**，它是一个纯序列化器模块。

### 依赖的外部模型关联链路

```
Project_Node (PM/nodelist)
    ↓ node_definition (ForeignKey)
ProjectTemplateNodeMapping (PSC/project/node)
    ↓ node_definition_version (ForeignKey)
NodeDefinitionVersion (PSC/node/definition)
    ↓ review_mappings (Related_name)
NodeDefinitionReviewMapping (PSC/node/review)  [中间表]
    ↓ review_definition_version (ForeignKey)
ReviewDefinitionVersion (PSC/review_definition)
    ↓ review_definition (ForeignKey)
ReviewDefinition (PSC/review_definition)
    └── name (评审项名称)
```

### 关键字段说明

| 字段来源 | 模型 | 字段名 | 用途 |
|---------|------|-------|------|
| NodeDefinitionReviewMapping | 中间表 | sort_order | 评审项排序 |
| ReviewDefinitionVersion | 版本模型 | deliverable_definition_version | 判断 type=fixed 的依据 |
| ReviewDefinition | 主模型 | name | 评审项名称 |


## 序列化器实现

### NodeReviewSerializer

**文件路径：** `apps/PM/nodelist/review/serializers.py`

```python
class NodeReviewSerializer(serializers.Serializer):
    """
    节点评审项序列化器

    注意：这是一个只读序列化器，不处理创建/更新操作
    """
    def to_representation(self, instance):
        """
        将 Project_Node 实例转换为评审项列表

        Args:
            instance: Project_Node 实例

        Returns:
            list: 评审项列表，格式见下方返回结构
        """
```

### 返回数据结构

```python
[
    {
        "id": int,           # ReviewDefinitionVersion.id
        "name": str,         # ReviewDefinition.name
        "required": True,    # 固定值
        "type": str          # "fixed" 或 "custom"
    }
]
```

### 类型判断逻辑

```python
# 如果评审项版本存在交付物定义版本关联
review_type = "fixed" if review_def_version.deliverable_definition_version else "custom"
```

- **fixed**: 评审项关联了具体的交付物定义模板
- **custom**: 评审项是自定义类型，没有固定交付物模板


## 在主序列化器中的使用

### ReadSerializer (PM/nodelist/serializers.py)

```python
from .review.serializers import NodeReviewSerializer

class ReadSerializer(serializers.ModelSerializer):
    review = serializers.SerializerMethodField()

    def get_review(self, instance):
        """获取节点评审信息"""
        serializer = NodeReviewSerializer(instance)
        return serializer.data
```


## 性能优化建议

### N+1 查询问题

由于关联链路较长，在节点列表接口中可能产生 N+1 查询问题。

### 解决方案：预加载

在视图中使用 `prefetch_related` 预加载关联数据：

```python
# 在获取节点列表的视图中添加
queryset = queryset.prefetch_related(
    'node_definition__node_definition_version__review_mappings__review_definition_version__review_definition'
)
```


## 模块特有名词索引

| 术语 | 定位 | 说明 |
|-----|------|------|
| **NodeReviewSerializer** | 序列化器 | 节点评审项序列化器，本模块核心类 |
| **review_mappings** | 反向关联 | NodeDefinitionVersion 的反向关联，指向 NodeDefinitionReviewMapping |
| **deliverable_definition_version** | 字段 | ReviewDefinitionVersion 的外键，用于判断评审项类型 |
| **fixed/custom** | 类型值 | 评审项类型，fixed=固定模板，custom=自定义 |
| **Project_Node** | 模型 | PM 模块的项目节点模型，评审项的载体 |


## 技术实现规范

### Django REST Framework

1. **继承 Serializer 而非 ModelSerializer**
   - 本模块不是直接序列化某个模型
   - 需要通过复杂的关联链路获取数据

2. **使用 to_representation 方法**
   - 自定义输出格式
   - 返回 list 而非 dict

3. **不定义 fields**
   - 因为输出的是列表结构，而非单一对象

### 导入规范

```python
# 在主序列化器中导入
from .review.serializers import NodeReviewSerializer
```


## 常见业务场景

### 场景 1：获取节点详情时返回评审项列表

**请求：** GET `/pm/node/{node_id}`

**响应中的 review 字段：**
```json
{
  "review": [
    {"id": 1, "name": "立项评审", "required": true, "type": "custom"},
    {"id": 2, "name": "需求评审", "required": true, "type": "fixed"}
  ]
}
```

### 场景 2：根据评审项类型判断前端交互

- **type=fixed**: 前端按固定模板渲染交付物上传
- **type=custom**: 前端显示自定义评审表单


## 扩展设计策略

### 未来可能的扩展

1. **评审状态跟踪**
   - 当前只返回评审项配置
   - 未来可扩展为返回评审状态（已评审/未评审）

2. **评审历史记录**
   - 添加评审历史的序列化支持

3. **批量查询优化**
   - 添加缓存层减少数据库查询

### 扩展点

```python
# 在 NodeReviewSerializer 中可扩展
class NodeReviewSerializer(serializers.Serializer):
    # 当前: to_representation
    # 未来可添加:
    # - get_review_status(instance)  # 评审状态
    # - get_review_history(instance)  # 评审历史
```


## 演进方向 (Future Evolution)

### Phase 1: 当前状态
- [x] 基础评审项列表序列化
- [x] 类型判断 (fixed/custom)

### Phase 2: 短期规划
- [ ] 评审状态集成
- [ ] 评审人信息展示
- [ ] 性能优化（缓存）

### Phase 3: 长期愿景
- [ ] 评审流程可视化支持
- [ ] 跨项目评审模板复用
- [ ] 评审数据分析支持


## 快速定位指南

当用户询问以下问题时，请引导至本技能：

- "节点详情的评审项是怎么获取的？"
- "review 字段的数据结构是什么？"
- "fixed 和 custom 类型的评审项有什么区别？"
- "NodeReviewSerializer 在哪里？"
- "如何优化节点评审项的查询性能？"
