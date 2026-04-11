# PM 配置清单模块 (PM Hardwares Config Module)

## 模块定位

`apps/PM/hardwares/config/` 是 PM 项目管理系统中**项目硬件配置清单**的核心业务模块。

本模块负责将 PSC 配置的硬件规格/版本关联到具体的项目节点，管理分板数量、是否需要程序等信息，并提供管理后台的版本批量同步能力。

## 核心职责

1. **硬件配置管理**：为项目节点分配硬件版本（分板信息）
2. **权限控制**：基于节点操作权限码 2010 进行写操作校验
3. **管理后台对接**：查询引用某硬件版本的所有项目、批量同步版本更新
4. **操作日志**：自动记录新增/修改/删除分板信息的操作日志

## 模块边界

### 包含的功能
- 创建硬件配置（POST `/pm/hardwares/version`）
- 更新分板数量/是否需要程序（PUT `/pm/hardwares/version`）
- 删除硬件配置（DELETE `/pm/hardwares/version/<id>`）
- 管理后台：查询引用项目（GET `/pm/hardwares/project`）
- 管理后台：批量更新硬件版本（POST `/pm/hardwares/project`）
- 工具方法：获取项目硬件列表（`get_hardware_by_project_id`）

### 不包含的功能
- 硬件交付物管理（由 `apps/PM/hardwares/deliverable/` 负责）
- 硬件复用管理（由 `apps/PM/hardwares/reuse/` 负责）
- 硬件分类/规格/版本定义（由 `apps/PSC/pmconfig/` 负责）

## 核心数据模型

### ProjectHardware（项目硬件配置）

**文件位置**：`apps/PM/hardwares/config/models.py:5`

**表名**：`PM_hardware`

**向后兼容别名**：`Project_Hardware`

```
核心字段：
- id: 主键
- project: 外键→PM.Project_List（所属项目，CASCADE 删除）
- node: 外键→PM.Project_Node（所属节点，CASCADE 删除）
- version: 外键→PSC.Hardware_Spec_Child（硬件版本，SET_NULL 删除）
- quantity: IntegerField（分板数量）
- is_need_program: BooleanField（是否需要程序，默认 True）
- remark: CharField（备注，max_length=255）
- creator: 外键→SM.User（创建人，SET_NULL 删除）
- create_time: DateTimeField（创建时间，auto_now_add）
- update_by: 外键→SM.User（最后修改人，SET_NULL 删除）
- update_time: DateTimeField（最后修改日期，auto_now）

属性方法：
- hardware_name → version.spec.name（硬件名称）
- category_name → version.spec.category.name（分类名称）
- version_code → version.version（硬件版本号）

Meta:
- default_permissions = ()（禁用默认权限）
```

### 关键关系

```
PSC.Hardware_Category（硬件分类）
  └── PSC.Hardware_Spec（硬件规格，FK→Category）
        └── PSC.Hardware_Spec_Child（硬件版本，FK→Spec）
              └── ProjectHardware.version（项目硬件配置）

PM.Project_List（项目）
  └── PM.Project_Node（节点，FK→Project_List）
        └── ProjectHardware.node（项目硬件配置，FK→Node）

SM.User（用户）
  ├── ProjectHardware.creator（创建人）
  └── ProjectHardware.update_by（最后修改人）
```

## 序列化器

### ProjectHardwareSerializer（创建/更新硬件配置）

**文件位置**：`apps/PM/hardwares/config/serializers.py:19`

```python
class ProjectHardwareSerializer(serializer_func.ToInternalValueMixin, serializers.ModelSerializer):
    node_id = PrimaryKeyRelatedField(source='node', queryset=Project_Node, required=False)
    version_id = PrimaryKeyRelatedField(source='version', queryset=Hardware_Spec_Child)
    quantity = IntegerField(required=False, default=1)
    is_need_program = BooleanField(required=False, default=True)

    class Meta:
        model = ProjectHardware
        fields = ['node_id', 'quantity', 'is_need_program', 'version_id']
```

**验证逻辑**：
- 新增时 `node_id` 不能为空
- 用户必须具有节点操作权限 2010
- 节点状态不能为已完成（state = 2）
- 自动从节点实例获取 `project_id`

**更新限制**：只允许修改 `quantity` 和 `is_need_program` 两个字段

### ProjectHardwareDetailSerializer（硬件配置详情）

**文件位置**：`apps/PM/hardwares/config/serializers.py:111`

返回嵌套结构的硬件详情：
```json
{
  "id": 1,
  "is_need": true,
  "quantity": 3,
  "note": "备注",
  "category": { "id": 1, "name": "主控板" },
  "hardware": { "id": 1, "name": "STM32F103" },
  "version": { "id": 1, "name": "V2.0" }
}
```

### ProjectInfoToPSCSerializer（管理后台项目信息）

**文件位置**：`apps/PM/hardwares/config/serializers.py:144`

用于管理后台展示引用某硬件版本的项目信息，包含项目名称、状态（含中文展开）、创建时间、创建人。

### BatchUpdateHardwareVersionSerializer（批量更新版本）

**文件位置**：`apps/PM/hardwares/config/serializers.py:182`

管理后台使用，批量将多个项目硬件记录的版本更新为同一新版本，使用事务保证原子性。

## 视图

### PSCHardwareView（管理后台视图）

**文件位置**：`apps/PM/hardwares/config/views.py:23`

**URL**：`/pm/hardwares/project`

| 方法 | 功能 | 说明 |
|------|------|------|
| GET | 查询引用项目 | 支持按 versionId 筛选（逗号分隔/数组），支持分页（pageNum/pageSize）和全量返回（all=true） |
| POST | 批量更新版本 | 使用事务原子更新多个项目硬件的版本号 |

### ViewHardware（硬件配置操作视图）

**文件位置**：`apps/PM/hardwares/config/views.py:135`

**URL**：`/pm/hardwares/version`、`/pm/hardwares/version/<id>`

| 方法 | URL | 功能 | 说明 |
|------|-----|------|------|
| POST | `/pm/hardwares/version` | 创建硬件配置 | 为节点添加分板信息 |
| PUT | `/pm/hardwares/version` | 更新硬件配置 | 仅可修改 quantity、is_need_program |
| DELETE | `/pm/hardwares/version/<id>` | 删除硬件配置 | 需要权限 2010，记录操作日志 |

## 工具方法

**文件位置**：`apps/PM/hardwares/config/utils.py`

| 方法 | 说明 |
|------|------|
| `get_project_hardware_list()` | 获取所有硬件配置，按创建时间倒序 |
| `get_hardware_by_project_id(project_id)` | 获取指定项目的硬件配置详情，使用 `select_related` + `only` 优化查询，按分类排序字段排序 |

## URL 路由配置

**文件位置**：`apps/PM/hardwares/urls.py`

```python
path('project', PSCHardwareView.as_view()),           # GET/POST 管理后台
path('version', ViewHardware.as_view()),              # POST/PUT 配置操作
path('version/<int:id>', ViewHardware.as_view()),     # DELETE 删除配置
```

## 权限验证

### 权限码

| 权限码 | 说明 | 使用位置 |
|--------|------|----------|
| 2010 | 节点操作权限 | 创建/更新/删除硬件配置 |

### 验证方式

```python
from apps.PM.authority.utils import permission as auth_permission

authority = auth_permission(node_instance.id, userinfo, 'project_node')
if not authority.verify(2010):
    raise serializers.ValidationError({'操作失败': '权限校验失败'})
```

### 业务限制

- 节点状态为已完成（state = 2）时，禁止创建和更新
- 删除操作需要权限 2010 校验
- 更新操作只允许修改 `quantity` 和 `is_need_program`

## 与其他模块关系

### 依赖的上游模块

| 模块 | 用途 | 关键交互 |
|------|------|----------|
| `PM.Project_List` | 项目主表 | ForeignKey 关联 |
| `PM.Project_Node` | 项目节点 | ForeignKey 关联，获取 project_id |
| `PSC.Hardware_Spec_Child` | 硬件版本定义 | ForeignKey 关联，获取分类/名称/版本号 |
| `SM.User` | 用户模型 | 记录创建人和修改人 |
| `PM.authority` | 权限验证 | 使用 `permission.verify('pm.product_manifest.edit')` 校验操作权限 |
| `utils.user.UserHelper` | 用户工具 | `setup_request_userinfo()` 构造用户信息 |

### 被依赖的下游模块

| 模块 | 用途 | 关键交互 |
|------|------|----------|
| `PM.hardwares.deliverable` | 硬件交付物 | 通过 `ProjectHardware` 关联硬件与交付物 |
| `PM.hardwares.reuse` | 硬件复用 | 复用硬件配置到其他项目 |
| `PM.nodelist` | 节点管理 | 节点详情返回配置清单数据（通过 `node_hardward` 反向关系） |

### 工具方法被调用方

```python
# apps/PM/hardwares/config/utils.py
# get_hardware_by_project_id() 被以下场景调用：
# - 项目详情/节点详情中展示配置清单
# - 硬件交付物关联时获取项目硬件列表
```

## 常见业务场景

### 场景1：为节点添加分板信息

```
1. 前端提交 node_id、version_id、quantity、is_need_program
2. 验证节点操作权限 2010
3. 验证节点状态非已完成
4. 创建 ProjectHardware 记录
5. 自动记录操作日志："在分板信息中添加了 {分类}{硬件名称}"
6. 返回创建结果
```

### 场景2：修改分板信息

```
1. 前端提交 id、quantity、is_need_program
2. 获取 ProjectHardware 实例
3. 验证权限 2010
4. 仅更新 quantity 和 is_need_program 字段
5. 记录操作日志："在分板信息中修改了 {分类} {硬件名称} 的数量为 {数量}，需要/不需要软件"
```

### 场景3：管理后台批量更新硬件版本

```
1. 管理后台提交 versionId（目标版本）和 projectId 列表（要更新的硬件记录ID）
2. 在事务中批量更新
3. 记录修改人
```

## 模块特有名词索引

| 名词 | 说明 |
|------|------|
| **ProjectHardware** | 项目硬件配置模型 |
| **配置清单** | 项目中使用的硬件版本列表 |
| **分板信息** | 为节点分配的硬件配置 |
| **分板数量** | 硬件的使用数量（quantity） |
| **是否需要程序** | 标识该硬件是否需要配套软件（is_need_program） |
| **硬件版本** | PSC.Hardware_Spec_Child 中定义的具体版本 |
| **versionId** | 管理后台批量更新时的目标版本ID |

## 禁止事项

- 禁止在更新操作中修改 `version` 字段（版本变更需通过管理后台批量更新）
- 禁止对已完成节点（state = 2）进行配置的新增和更新
- 禁止新增时省略 `node_id`（节点为必填项）
- 禁止绕过权限码 2010 进行写操作

## 相关技能

- **pm-hardwares_deliverable**：硬件交付物管理模块
- **psc-pmconfig_category**：硬件分类配置模块
- **psc-pmconfig_hardware**：硬件规格/版本配置模块
- **pm-nodelist**：节点管理模块
- **pm-authority**：权限验证模块

## 变更记录

### 2026-03-29
- 创建文档
