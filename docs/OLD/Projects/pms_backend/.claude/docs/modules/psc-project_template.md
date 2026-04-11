# PSC 项目模板模块 (Project Template)

## 模块定位

PSC 项目模板模块是项目设置配置（Project Settings Configuration）的核心子模块，负责管理可复用的项目模板库。新项目创建时可以引用模板，快速初始化项目节点结构和评审规则。

**模块路径**: `apps/PSC/project/template/`

## 核心架构

### 版本化设计模式

项目模板采用**主模型 + 版本模型**的分离设计：

```
ProjectTemplate (主模型)
├── code, is_active            # 仅创建时可编辑
├── created_at                 # 创建时间
└── versions (1:N)             # 版本关联

ProjectTemplateVersion (版本模型)
├── name                       # 🆕 模板名称（版本迭代时可修改）
├── remark                     # 版本备注
├── version_number             # 版本号（自增）
├── is_current                 # 是否当前版本
├── created_by                 # 创建人
├── created_at                 # 创建时间
└── node_mappings (1:N)        # 节点映射关联
```

**设计原则**：
- 主模型字段（code）仅在 POST 创建时可设置，PUT/PATCH 不能修改
- **name 字段存储在版本模型中，允许在版本迭代时修改**（🆕 Since 2026-03-09）
- `is_active` 仅可通过 PATCH 批量更新
- 所有业务变更通过版本迭代实现（PUT 请求创建新版本）
- `updatedAt` 取自最新版本的 `created_at`（主模型无 `updated_at` 字段）

### 关联关系

| 关联类型 | 目标模型 | 说明 |
|---------|---------|------|
| 1:N | ProjectTemplateVersion | 主模型 → 版本 |
| M:N | ProjectTemplateLabel | 通过 ProjectTemplateLabelMapping |
| 1:N | NodeDefinitionVersion | 通过 ProjectTemplateNodeMapping |

## 数据模型详解

### ProjectTemplate（项目模板主模型）

**表名**: `PSC_project_template`

| 字段 | 类型 | 说明 | 编辑权限 |
|-----|------|------|---------|
| id | AutoField | 主键 | 只读 |
| code | CharField(100) | 唯一编码（PROJ_TMP前缀） | 仅POST |
| is_active | BooleanField | 是否启用 | 仅PATCH |
| created_at | DateTimeField | 创建时间 | 只读 |

**索引**: `id` (主键), `code` (unique)

**变更说明**：⚠️ `name` 字段已移至版本模型（Deprecated since 2026-03-09）

### ProjectTemplateVersion（项目模板版本）

**表名**: `PSC_project_template_version`

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | AutoField | 主键 |
| project_template | ForeignKey | 关联主模型 |
| name | CharField(255) | 🆕 模板名称（版本迭代时可修改） |
| version_number | IntegerField | 版本号（自动递增） |
| remark | TextField | 版本备注 |
| is_current | BooleanField | 是否当前版本 |
| created_by | ForeignKey | 创建人 |
| created_at | DateTimeField | 创建时间 |

**索引**: `(project_template, is_current)`

**版本控制逻辑**：
- 创建新版本时，旧版本的 `is_current` 自动设为 False
- `version_number` 按 `project_template` 分组自增
- 删除模板时级联删除所有版本
- **name 唯一性在序列化器层验证，模型层无约束**（🆕 Since 2026-03-09）

### ProjectTemplateNodeMapping（节点映射）

**表名**: `PSC_project_template_node_mapping`

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | AutoField | 主键 |
| project_template_version | ForeignKey | 项目模板版本 |
| node_definition_version | ForeignKey | 节点定义版本（锁定快照） |
| parent | ForeignKey(self) | 父节点（自引用） |
| sort_order | IntegerField | 排序 |

**唯一约束**: `(project_template_version, node_definition_version)`

**设计说明**：
- 关联 `NodeDefinitionVersion` 而非 `NodeDefinition`，确保模板引用特定版本
- 支持 N 层树形结构（通过 parent 自引用）

### ProjectTemplateLabel（项目标签）

**表名**: `PSC_project_template_label`

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | AutoField | 主键 |
| code | CharField(100) | 唯一编码（PROJ_LABEL前缀） |
| name | CharField(255) | 标签名称（唯一） |
| created_by | ForeignKey | 创建人 |
| created_at | DateTimeField | 创建时间 |

### ProjectTemplateLabelMapping（标签映射）

**表名**: `PSC_project_template_label_mapping`

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | AutoField | 主键 |
| project_template | ForeignKey | 项目模板 |
| project_template_label | ForeignKey | 项目标签 |

## API 路由设计

```
GET    /psc/project/templates/list      列表查询（分页）
POST   /psc/project/templates/list      创建模板（含第一个版本）
PATCH  /psc/project/templates/list      批量更新（仅isActive）
DELETE /psc/project/templates/list      批量删除

GET    /psc/project/templates/<id>      详情查询
PUT    /psc/project/templates/<id>      版本迭代（创建新版本，name可修改）
```

## 字段权限矩阵

| 字段 | POST | PATCH | PUT |
|-----|------|-------|-----|
| code | ✅创建 | ❌ | ❌ |
| name | ✅必填 | ❌ | ✅可修改 |
| is_active | ✅默认true | ✅ | ❌ |
| remark | ✅ | ❌ | ✅ |
| labelIds | ✅ | ❌ | ✅ |
| nodes | ✅ | ❌ | ✅ |

**变更说明**：PUT 时 name 可修改，不传则使用上一个版本的 name（🆕 Since 2026-03-09）

## name 字段唯一性验证

**验证层级**：序列化器（Serializer），模型层无唯一约束

### POST（创建模板）

检查其他模板的**当前版本**（`is_current=True`）是否已有相同 name：

```python
ProjectTemplateVersion.objects.filter(
    name=name,
    is_current=True
).exists()
```

### PUT（版本迭代）

排除本模板的所有版本，检查其他模板的**所有版本**是否有相同 name：

```python
ProjectTemplateVersion.objects \
    .exclude(id__in=[v.id for v in self.instance.versions.all()]) \
    .filter(name=name).exists()
```

**验证逻辑**：
- POST: 只检查当前版本，因为旧版本已被标记为非当前
- PUT: 检查所有版本，排除本模板的所有版本（防止跨模板重复）

## 节点树形结构规则

### Category 层级关系

节点定义包含三种 category，必须遵循严格的父子关系：

| Category | 中文 | 父节点要求 | 层级 |
|----------|------|-----------|------|
| MILESTONE | 里程碑 | 不能有 parent | 第1层（根） |
| MAIN_NODE | 主节点 | 必须是 MILESTONE | 第2层 |
| SUB_NODE | 子节点 | 必须是 MAIN_NODE | 第3层 |

### 验证规则

**单节点验证** (`ProjectTemplateNodeMappingItemSerializer`)：
1. MILESTONE 不能有 parent
2. 除 MILESTONE 外必须提供 parent
3. 防止自引用（node 不能是自己的 parent）
4. SUB_NODE 的 parent 必须是 MAIN_NODE
5. MAIN_NODE 的 parent 必须是 MILESTONE

**批量验证** (`ProjectTemplateNodeMappingListSerializer`)：
1. parent 引用必须在同一批次节点列表中
2. DFS 循环引用检测（时间复杂度 O(N+E)）

### 示例结构

```json
{
  "nodes": [
    {
      "nodeDefinitionVersionId": 1,  // MILESTONE
      "parent": null,
      "sortOrder": 1
    },
    {
      "nodeDefinitionVersionId": 2,  // MAIN_NODE
      "parent": 1,                    // parent 是 MILESTONE
      "sortOrder": 1
    },
    {
      "nodeDefinitionVersionId": 3,  // SUB_NODE
      "parent": 2,                    // parent 是 MAIN_NODE
      "sortOrder": 1
    }
  ]
}
```

## 列表查询优化

使用 `get_list_queryset()` 预加载当前版本数据，避免 N+1 查询：

```python
# utils.py
current_version = ProjectTemplateVersion.objects.filter(
    project_template=OuterRef('pk'),
    is_current=True
)[:1]

queryset = ProjectTemplate.objects.annotate(
    currentVersionId=Subquery(current_version.values('id')),
    currentName=Subquery(current_version.values('name')),  # 🆕 当前版本名称
    currentRemark=Subquery(current_version.values('remark')),
    currentVersionNumber=Subquery(current_version.values('version_number')),
    currentCreatedByNickname=Subquery(current_version.values('created_by_id__nickname')),
    updatedAt=Subquery(latest_version.values('created_at')),  # 最新版本时间
)
```

**注意**：
- `updatedAt` 取自**最新版本**的 `created_at`，而非主模型的 `updated_at`（主模型无此字段）
- `name` 字段来自 `currentName` 注解（🆕 Since 2026-03-09）

## 序列化器说明

### ListSerializer

**输出字段**：
- 主模型字段：`id`, `code`, `name`（来自 currentName）, `isActive`, `createdAt`, `updatedAt`
- 当前版本字段：`currentVersionId`, `currentVersionNumber`, `currentRemark`, `currentCreatedByNickname`
- 关联字段：`labels`（逗号分隔字符串）

### DetailSerializer

**分块输出结构**：
```json
{
  "id": 1,
  "document": {
    "code": "PROJ_TMP001",
    "name": "标准硬件开发项目",  // 来自当前版本
    "isActive": true,
    "remark": "版本备注",
    "labels": [{"id": 1, "code": "PROJ_LABEL001", "name": "硬件"}]
  },
  "nodeData": {
    "list": [
      {
        "id": 1,
        "nodeDefinitionId": 10,
        "nodeDefinitionVersionId": 100,
        "nodeCode": "M001",
        "nodeName": "里程碑1",
        "parent": null,
        "sortOrder": 1,
        "children": []
      }
    ]
  },
  "others": {
    "createdAt": "2025-01-01T00:00:00+08:00",
    "updatedAt": "2025-01-02T00:00:00+08:00",
    "versionCount": 3
  }
}
```

### WriteSerializer

**POST 创建流程**：
1. 创建 ProjectTemplate（code, is_active=True）
2. 调用 `create_new_version()` 创建第一个版本（包含 name）
3. 处理标签关联（删除旧的，创建新的）
4. 处理节点关联（两阶段创建：先创建映射，再设置 parent）

**PUT 版本迭代流程**：
1. 获取上一个版本的 name 作为默认值（不传 name 时使用）
2. 调用 `create_new_version()` 创建新版本（支持 name 修改）
3. 更新标签关联
4. 更新节点关联

**name 处理逻辑**（🆕 Since 2026-03-09）：
```python
# POST: name 必填，存储到版本中
version_data = {
    'name': validated_data['name'],  # 必填
    'initial_status': validated_data.get('initial_status'),
    'remark': validated_data.get('remark'),
    'created_by': user,
}

# PUT: name 可选，不传则使用上一个版本的 name
previous_version = instance.versions.filter(is_current=True).first()
previous_name = previous_version.name if previous_version else None

version_data = {
    'name': validated_data.get('name', previous_name),  # 可选
    'remark': validated_data.get('remark'),
    'created_by': user,
}
```

### PatchSerializer

批量更新 `is_active` 字段，传入 `ids` 数组和 `isActive` 值。

### DeleteSerializer

批量删除模板，**验证逻辑**（🆕 已修复）：
- 检查该模板的所有版本是否被项目使用
- 项目引用的是 `ProjectTemplateVersion`，而非 `ProjectTemplate` 主模型
- 验证逻辑：`Project_List.objects.filter(template_id__in=version_ids).exists()`
- 已被使用的模板无法删除，返回字典格式错误：`{"PROJ_TMP001": "已被项目使用，无法删除"}`

**关键实现**（serializers.py:444-460）：
```python
def validate(self, attrs):
    instances = attrs['ids']
    errors = {}

    for instance in instances:
        # 获取该模板的所有版本 ID
        version_ids = instance.versions.values_list('id', flat=True)
        # 检查项目是否引用了任何版本
        if Project_List.objects.filter(template_id__in=version_ids).exists():
            errors[instance.code] = f'"{instance.code}" 已被项目使用，无法删除'

    if errors:
        raise serializers.ValidationError(errors)

    return attrs
```

## 两阶段节点创建

节点映射需要两阶段创建以处理 parent 自引用：

```python
# 阶段 1：创建所有映射（parent 暂时为 None）
for node in nodes_data:
    mapping = ProjectTemplateNodeMapping.objects.create(
        project_template_version=version,
        node_definition_version=node['versionId'],
        parent=None,  # 稍后设置
        sort_order=node.get('sortOrder', 0)
    )
    node_id_to_mapping[node['versionId'].id] = mapping

# 阶段 2：设置 parent 关系
for node in nodes_data:
    parent = node.get('parent')
    if parent is not None:
        mapping = node_id_to_mapping[node['versionId'].id]
        parent_mapping = node_id_to_mapping.get(parent.id)
        if parent_mapping:
            mapping.parent = parent_mapping
            mapping.save()
```

## 与其他模块关系

### 依赖模块

| 模块 | 依赖类型 | 说明 |
|-----|---------|------|
| `apps/SM` | 认证 | `IsAuthenticated` 权限，User 模型 |
| `apps/PSC/node/definition` | 强依赖 | NodeDefinitionVersion，节点 Category 枚举 |
| `apps/PM/projects` | 软依赖 | 删除时检查是否被 Project_List 引用（引用 ProjectTemplateVersion） |
| `apps/PSC/project/label` | 内部关联 | ProjectTemplateLabel 标签系统 |
| `apps/PSC/project/node` | 内部关联 | ProjectTemplateNodeMapping 节点映射 |

### 被依赖模块

| 模块 | 说明 |
|-----|------|
| `apps/PM/projects` | 项目创建时引用模板初始化节点结构（关联 ProjectTemplateVersion） |

### 关键数据流向

**项目创建引用模板**：
```
Project_List.template → ProjectTemplateVersion (ForeignKey)
                                     ↓
                                     name (版本模型的 name 字段) 🆕
                                     ↓
                         ProjectTemplate (主模型)
```

**删除验证检查流向**：
```
ProjectTemplate (待删除)
      ↓ versions
ProjectTemplateVersion (所有版本)
      ↓ template_id__in
Project_List (检查是否被引用)
```

## 权限验证

当前使用 Django REST Framework 的 `IsAuthenticated` 权限类：

```python
permission_classes = [IsAuthenticated]
```

**未来扩展方向**：
- 基于角色的细粒度权限（RBAC）
- 模板所有权验证（创建人 vs 其他人）
- 部门级权限隔离

## 常见业务场景

### 场景 1：创建新项目模板

```http
POST /psc/project/templates/list
Content-Type: application/json

{
  "code": "PROJ_TMP001",
  "name": "标准硬件开发项目",
  "remark": "初始版本",
  "labelIds": [1, 2],
  "nodes": [
    {
      "nodeDefinitionVersionId": 100,
      "parent": null,
      "sortOrder": 1
    }
  ]
}
```

### 场景 2：版本迭代（修改 name 和节点结构）

```http
PUT /psc/project/templates/1
Content-Type: application/json

{
  "name": "硬件开发项目 V2",  // 🆕 修改名称
  "remark": "新增评审节点",
  "nodes": [
    {
      "nodeDefinitionVersionId": 101,
      "parent": null,
      "sortOrder": 1
    }
  ]
}
```

**结果**：
- 创建新版本（version_number +1）
- 旧版本 `is_current` 设为 False
- code, is_active 保持不变
- **新版本的 name 为"硬件开发项目 V2"**（🆕）

### 场景 3：版本迭代（不修改 name）

```http
PUT /psc/project/templates/1
Content-Type: application/json

{
  "remark": "新增评审节点"
}
```

**结果**：
- 新版本的 name 自动使用上一个版本的 name
- 只修改 remark 和其他传入字段

### 场景 4：批量启用/禁用模板

```http
PATCH /psc/project/templates/list
Content-Type: application/json

{
  "ids": [1, 2, 3],
  "isActive": false
}
```

### 场景 5：删除模板（🆕 已修复验证逻辑）

```http
DELETE /psc/project/templates/list
Content-Type: application/json

{
  "ids": [1]
}
```

**验证**：
- 检查该模板的所有版本是否被项目引用
- 如果被引用，返回错误：
  ```json
  {
    "PROJ_TMP001": "\"PROJ_TMP001\" 已被项目使用，无法删除"
  }
  ```

## 扩展设计策略

### 1. 模板复制（Clone）

未来支持基于现有模板创建新模板：

```python
def clone_template(self, original_id, new_name):
    original = ProjectTemplate.objects.get(id=original_id)
    current_version = original.versions.filter(is_current=True).first()

    # 复制节点结构
    nodes_data = self._extract_nodes(current_version)

    # 创建新模板
    new_template = ProjectTemplate.objects.create(
        code=get_unique_code('PROJ_TMP', ProjectTemplate),
        is_active=True
    )

    # 创建版本并关联节点
    new_version = new_template.create_new_version(
        name=new_name,  # 🆕 name 在版本中
        remark=f"复制自 {original.code}",
        created_by=request.user
    )
    self._process_nodes(new_version, nodes_data)

    return new_template
```

### 2. 模板导入/导出

支持 JSON 格式的模板导入导出，实现跨系统迁移。

### 3. 版本对比

提供版本间节点结构差异对比功能。

### 4. 模板发布工作流

增加草稿、审核、发布状态，支持模板变更审核流程。

## 演进方向 (Future Evolution)

### 短期优化（3-6个月）

1. **性能优化**
   - 列表查询增加缓存（Redis）
   - 节点树构建算法优化（当前 O(N²) 可优化至 O(N)）

2. **验证增强**
   - 节点重复检测（同一 nodeDefinitionVersionId 不能在同一模板中重复）
   - 必填节点验证（某些节点必须存在于模板中）

3. **API 增强**
   - 批量操作支持事务回滚
   - 增加版本列表 API

### 中期扩展（6-12个月）

1. **模板分类体系**
   - 支持多级标签分类
   - 行业、项目类型维度分类

2. **模板推荐**
   - 基于历史项目数据推荐模板
   - 相似项目模板推荐

3. **权限细化**
   - 模板所有者权限
   - 部门级权限隔离
   - 只读/编辑权限分离

### 长期愿景（12个月+）

1. **模板市场**
   - 企业级模板库
   - 最佳实践模板共享

2. **智能模板**
   - AI 辅助模板设计
   - 基于项目特点自动推荐节点结构

3. **多版本并行**
   - 支持多个草稿版本
   - 版本合并功能

## 技术债务与注意事项

### 当前限制

1. **无软删除机制**：删除模板直接物理删除，数据无法恢复
2. **版本无审核**：版本迭代无需审核，可能引入错误配置
3. **节点重复**：允许同一节点在不同分支下重复使用
4. **缺少版本锁定**：正在被项目使用的模板仍然可以修改

### 建议改进

1. 增加软删除（is_deleted 标记）
2. 版本发布审核工作流
3. 模板锁定机制（被引用时锁定）
4. 操作日志记录（谁在何时修改了什么）

## 相关文件清单

### 核心文件

| 文件 | 说明 |
|-----|------|
| `apps/PSC/project/template/models.py` | 数据模型定义（name 在版本模型中） |
| `apps/PSC/project/template/serializers.py` | 序列化器（含 name 唯一性验证） |
| `apps/PSC/project/template/views.py` | API 视图 |
| `apps/PSC/project/template/utils.py` | 查询集优化（currentName 注解） |
| `apps/PSC/project/template/urls.py` | 路由配置 |

### 关联文件

| 文件 | 说明 |
|-----|------|
| `apps/PSC/project/node/models.py` | 节点映射模型 |
| `apps/PSC/project/node/serializers.py` | 节点序列化器（含 DFS 验证） |
| `apps/PSC/project/label/models.py` | 标签模型 |
| `apps/PSC/project/label/serializers.py` | 标签序列化器 |
| `apps/PSC/project/label/views.py` | 标签视图 |
| `apps/PSC/project/urls.py` | 模块路由汇总 |
| `apps/PM/project/models.py` | Project_List 模型（引用 ProjectTemplateVersion） |
| `apps/PM/project/serializers.py` | 🆕 项目创建时使用 `template_version_instance.name` |

## 术语索引

| 术语 | 定位 |
|-----|------|
| 项目模板 | 本模块核心概念 |
| ProjectTemplate | 主模型（无 name 字段） |
| ProjectTemplateVersion | 版本模型（包含 name 字段）🆕 |
| 版本迭代 | PUT 请求创建新版本的行为 |
| name 可修改 | PUT 时可修改模板名称（🆕 Since 2026-03-09） |
| 节点映射 | ProjectTemplateNodeMapping |
| 树形结构 | 节点的父子层级关系 |
| MILESTONE/MAIN_NODE/SUB_NODE | 节点 Category 枚举值 |
| DFS 循环引用检测 | 验证算法 |
| 两阶段创建 | 节点映射创建策略 |
| updatedAt | 最新版本的 created_at |
| currentName | 当前版本的 name 注解（🆕） |
| currentVersionId | 当前版本 ID |
| 删除验证 | 检查模板所有版本是否被项目引用 |
