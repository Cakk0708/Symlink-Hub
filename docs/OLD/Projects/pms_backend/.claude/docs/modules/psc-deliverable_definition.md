# PSC 交付物定义模块技能文档

## 简介

**PSC 交付物定义模块** (`apps/PSC/deliverable_definition`) 是项目设置配置中心的核心组成部分，负责定义和管理项目节点所需的交付物规则标准。

本模块采用**版本化配置管理**模式，将交付物定义与具体规则分离，支持规则的持续演进而不影响已有项目。

## 触发条件 (When to use)

| 触发词/场景 | 说明 |
|------------|------|
| "交付物定义"、"DeliverableDefinition" | 涉及交付物规则定义 |
| "交付物版本"、"DeliverableDefinitionVersion" | 涉及版本管理 |
| "版本号"、"displayVersion" | 涉及用户自定义版本号 |
| "PSC配置"、"项目设置配置" | 涉及PSC模块配置 |
| "allowed_file_extensions" | 涉及文件扩展名类型关联 |
| 修改 `apps/PSC/deliverable_definition/` 下的文件 | 直接修改模块代码 |

## 核心指令 (Instructions)

### 1. 模块理解准则

- **定位**：本模块是**配置定义层**，不负责具体的交付物文件管理（由PM/deliverable负责）
- **版本策略**：每次修改创建新版本，`is_current=True` 标识当前生效版本
- **版本号体系**：双版本号设计
  - `version_number`：内部版本号（Integer，系统自动递增，不对外展示）
  - `display_version`：用户版本号（String，用户可自定义，默认 "1.0"，用于对外展示）🆕
- **文件类型限制**：通过 `allowed_file_extensions` (M2M) 关联 `file_extension_type` 模块
- **编码生成**：`code` 字段支持自动生成（使用 `get_unique_code('DELIV', ...)`）

### 2. 代码修改规范

**模型修改**：
- 添加新字段需考虑版本兼容性
- 索引优化优先考虑 `(deliverable_definition, is_current)` 复合查询
- `allowed_file_extensions` 为 ManyToManyField，关联 `file_extension_type.FileExtensionType`

**视图修改**:
- 视图必须分离为 `ListViews`（列表）和 `DetailViews`（详情）
- 视图仅做服务层，不实现具体业务逻辑
- 筛选、分页、排序逻辑由 `GetListParamsSerializer.get_queryset()` 处理
- 基础查询集由 `utils.get_list_queryset()` 提供（含 annotate 优化）

**序列化器修改**：
- `DeliverableDefinitionListSerializer`：扁平化输出主模型 + 最新版本数据，继承 `DateTimeFormatMixin` 处理时区
- `DeliverableDefinitionDetailSerializer`：分块输出（id, document, items, others），使用 `to_local_time` 处理时区
- `DeliverableDefinitionVersionSimpleSerializer`：继承 `DateTimeFormatMixin` 处理时区，包含 `displayVersion` 字段 🆕
- `WriteSerializer`：POST 创建定义+版本（code/name 必填），PUT 仅版本迭代（code/name 非必填），支持设置 `displayVersion` 🆕
- `GetListParamsSerializer`：必须实现 `get_queryset()` 方法处理筛选逻辑

### 3. 关键字段说明

| 字段 | 位置 | 作用 |
|------|------|------|
| `code` | `DeliverableDefinition` | 唯一标识，POST 时必填（为空时自动生成格式：`DELIV0001`），PUT 时非必填 |
| `name` | `DeliverableDefinition` | 名称，POST 时必填，PUT 时非必填 |
| `is_active` | `DeliverableDefinition` | 启用状态，仅 PATCH 可修改 |
| `version_number` | `DeliverableDefinitionVersion` | 内部版本号（Integer，系统自动递增，不对外展示）🆕 |
| `display_version` | `DeliverableDefinitionVersion` | 用户版本号（String，用户可自定义，默认 "1.0"，用于对外展示）🆕 |
| `remark` | `DeliverableDefinitionVersion` | 版本备注（TextField，可空）🆕 |
| `is_current` | `DeliverableDefinitionVersion` | 标识当前生效版本 |
| `allowed_file_extensions` | `DeliverableDefinitionVersion` | M2M → `file_extension_type.FileExtensionType` |

### 4. 常用查询模式

```python
# 获取定义的当前版本
definition = DeliverableDefinition.objects.get(code="PROJECT_REQUIREMENT")
current = definition.versions.filter(is_current=True).first()

# 创建新版本（自动处理旧版本）
new_version = definition.create_new_version(
    display_version="2.0",  # 用户可指定版本号
    remark="新版本备注"  # 使用 remark 字段
)

# 创建定义时 code 为空将自动生成
definition = DeliverableDefinition.objects.create(
    code="",  # 空值触发自动生成
    name="项目需求"
)
# 结果：code = "DELIV0001"
```


## 模块定位

**所属系统**: PSC (Project Settings Configuration) - 项目设置配置中心

**核心职责**: 管理项目节点的交付物规则定义，支持版本化配置管理。

**架构层级**:
```
PSC (配置中心)
├── file_extension_type (文件扩展名类型 - 公共配置)
└── deliverable_definition (交付物定义)
    ├── 定义层 (DeliverableDefinition) - 交付物抽象
    └── 版本层 (DeliverableDefinitionVersion) - 具体规则实现
        ├── display_version (用户版本号) 🆕
        ├── version_number (内部版本号) 🆕
        ├── remark (版本备注) 🆕
        └── allowed_file_extensions (M2M) → FileExtensionType
```

**特有名词索引**:
- `DeliverableDefinition`: 交付物定义主表
- `DeliverableDefinitionVersion`: 交付物定义版本表
- `version_number`: 内部版本号（系统自动递增）🆕
- `display_version`: 用户版本号（用户可自定义）🆕
- `remark`: 版本备注字段（原 `description`）🆕
- `is_current`: 版本当前状态标识
- `allowed_file_extensions`: 允许的文件扩展名（多对多关联）
- `get_unique_code`: 编码自动生成函数
- `to_local_time`: 时区转换函数（UTC → Asia/Shanghai）


## 模块职责边界

### 核心职责

| 职责 | 说明 |
|------|------|
| **规则定义管理** | 定义项目节点所需的交付物类型、数量、要求 |
| **版本化管理** | 每次规则修改生成新版本，支持版本历史追溯 |
| **双版本号管理** | 内部版本号（自动递增）+ 用户版本号（自定义展示）🆕 |
| **文件类型限制** | 通过 `allowed_file_extensions` 关联扩展名类型 |
| **编码自动生成** | 支持交付物定义编码自动生成（DELIV 前缀） |

### 边界界定

| 归属 | 模块 | 说明 |
|------|------|------|
| ✅ 本模块 | 交付物规则定义、版本管理、双版本号、编码生成 | 定义"什么交付物"、"如何交付" |
| ✅ file_extension_type | 文件扩展名类型定义 | 提供"允许什么扩展名" |
| ✅ SM/code | 编码生成工具 | 提供 `get_unique_code` 函数 |
| ✅ utils/date | 时区转换工具 | 提供 `to_local_time`, `DateTimeFormatMixin` |
| ✅ PM 模块 | 节点规则配置、交付物实例 | 使用定义规则，创建具体交付物 |

### 不负责

- ❌ 文件扩展名类型管理（file_extension_type 负责）
- ❌ 交付物文件上传/存储（PM/deliverable 负责）
- ❌ 节点实例管理（PM/node 负责）
- ❌ 权限控制验证（PM/authority 负责）


## 核心数据模型

### 模型架构图

```
┌─────────────────────────────────────────────────────────────┐
│                  DeliverableDefinition                       │
│                  (交付物定义主表)                             │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ code          (唯一标识，为空时自动生成如 "DELIV0001")       │
│ name          (名称，如 "项目需求")                          │
│ is_active     (是否启用)                                     │
│ created_at / updated_at                                     │
├─────────────────────────────────────────────────────────────┤
│ methods:                                                    │
│ └── save() → code 为空时调用 get_unique_code('DELIV', ...)  │
│                                                              │
│ relations:                                                  │
│ └── versions → DeliverableDefinitionVersion[] (反向关联)    │
└─────────────────────────────────────────────────────────────┘
                            │ 1:N
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              DeliverableDefinitionVersion                    │
│              (交付物定义版本表 - 具体规则)                     │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ deliverable_definition (FK) → DeliverableDefinition        │
│ version_number    (内部版本号，Integer，自动递增) 🆕         │
│ display_version   (用户版本号，String，默认 "1.0") 🆕        │
│ remark           (版本备注，TextField，可空) 🆕              │
│ allowed_file_extensions (M2M) → FileExtensionType[]         │
│ is_link_first    (是否链接优先)                              │
│ is_current       (是否当前版本) ⭐                           │
│ created_at / created_by                                      │
└─────────────────────────────────────────────────────────────┘
```

### 字段详解

#### DeliverableDefinition (定义主表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `code` | CharField(255) | UNIQUE, default='' | 业务标识，如 `DELIV0001`，POST 时必填（为空时自动生成），PUT 时非必填 |
| `name` | CharField(255) | UNIQUE | 显示名称，如 `项目需求`，POST 时必填，PUT 时非必填 |
| `is_active` | BooleanField | default=True | 启用状态，仅 PATCH 可修改 |

#### DeliverableDefinitionVersion (版本表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `version_number` | IntegerField | - | 内部版本号（系统自动递增，不对外展示）🆕 |
| `display_version` | CharField(50) | blank=True, default='1.0' | 用户版本号（用户可自定义，用于对外展示）🆕 |
| `remark` | TextField | blank=True, null=True | 版本备注（原 `description` 字段）🆕 |
| `allowed_file_extensions` | ManyToManyField | - | 文件扩展名类型（多对多） |
| `is_current` | BooleanField | - | 标识当前生效版本 |

### 索引设计

```python
# 版本表索引
indexes = [
    models.Index(fields=['deliverable_definition', 'is_current']),  # 快速获取当前版本
]
```

### 实例方法

```python
# DeliverableDefinition
def save(self, *args, **kwargs):
    """保存时自动生成 code（如果为空）"""
    if not self.code:
        self.code = get_unique_code('DELIV', DeliverableDefinition)
    super().save(*args, **kwargs)

def create_new_version(self, **version_data):
    """创建新版本（自动处理旧版本）"""
    self.versions.filter(is_current=True).update(is_current=False)
    return self.versions.create(**version_data, is_current=True)

# DeliverableDefinitionVersion
def __str__(self):
    """仅显示用户自定义版本号，内部版本号不对外展示"""
    return f"{self.deliverable_definition.code} {self.display_version}"  # 🆕
```


## 视图架构设计

### 设计标准

本模块遵循项目的标准视图分层架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        视图分层设计                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  utils.py → get_list_queryset()                              │
│      └── annotate() + Subquery() 预加载最新版本数据            │
│                                                             │
│  serializers.py → GetListParamsSerializer.get_queryset()      │
│      └── 处理筛选、分页、排序                                │
│                                                             │
│  views.py                                                    │
│      ├── ListViews     (列表查询、创建、批量更新、批量删除)    │
│      └── DetailViews   (详情查询、版本迭代)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 视图职责划分

| 视图类 | 职责 | 端点 |
|--------|------|------|
| `ListViews` | GET: 列表查询（分页）<br>POST: 创建定义<br>PATCH: 批量更新 isActive<br>DELETE: 批量删除 | `/list` |
| `DetailViews` | GET: 详情查询（分块输出）<br>PUT: 版本迭代 | `/<id>` |

### 核心设计原则

1. **视图简洁化**：视图仅作为服务层，不包含业务逻辑
2. **逻辑下沉**：筛选、分页逻辑由序列化器处理
3. **查询优化**：使用 `annotate()` + `Subquery()` 预加载版本数据，避免 N+1
4. **职责分离**：列表和详情操作分离到不同视图类
5. **版本号展示**：对外仅展示 `displayVersion`，`version_number` 仅内部使用 🆕

### 字段权限说明

| 字段 | 可修改方式 | 说明 |
|------|-----------|------|
| `code` | POST 时必填（可为空触发自动生成），PUT 时非必填 | 为空时自动生成（`DELIV0001` 格式），创建后不可修改 |
| `name` | POST 时必填，PUT 时非必填 | 创建后不可修改 |
| `is_active` | 仅 PATCH | POST 默认 true |
| `display_version` | POST/PUT 可选 | 用户可自定义版本号，默认 "1.0" 🆕 |
| `remark` | POST/PUT 可选 | 版本备注，可空 🆕 |
| 版本相关字段 | POST 创建版本<br>PUT 创建新版本（迭代） | PUT 不修改 code/name/isActive |


## 与其他模块关系

### 模块依赖图

```
                    ┌─────────────────┐
                    │  SM/code        │
                    │  (编码生成工具)  │
                    └────────┬────────┘
                             │ get_unique_code()
                             ↓
┌──────────────────────────────────────────────────────────────┐
│                   PSC/deliverable_definition                 │
│                   (本模块 - 交付物定义)                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         引用 (allowed_file_extensions M2M)            │    │
│  ↓                                                      │    │
│  │ PSC/file_extension_type (文件扩展名类型)             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         引用 (时区转换)                                │    │
│  ↓                                                      │    │
│  │ utils/date (DateTimeFormatMixin, to_local_time)      │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
       │ 提供规则定义
       ↓
┌──────────────────────────────────────────────────────────────┐
│                      PM/node_rule                            │
│                   (节点规则配置)                              │
└──────────────────────────────────────────────────────────────┘
```

### 关键关联字段

| 模块 | 关联字段 | 说明 |
|------|----------|------|
| `file_extension_type.FileExtensionType` | `allowed_file_extensions` (M2M) | 版本可选择多个扩展名类型 |
| `SM.code.utils` | `get_unique_code()` | 编码自动生成函数 |
| `utils.date` | `to_local_time`, `DateTimeFormatMixin` | 时区转换工具 |
| `PSC.node.definition` | `upgrade_node_definition_version_when_deliverable_changes()` | 🆕 交付物变化触发节点定义版本升级 |

### 信号驱动 (🆕 Since 2026-03-10)

本模块通过信号机制实现**交付物定义变化自动触发节点定义版本升级**：

**触发条件**：
1. 新创建的交付物定义版本（`created=True`）
2. 是当前版本（`is_current=True`）
3. 不是首次创建（第一个版本不需要触发升级）

**处理流程**：
```
DeliverableDefinitionVersion.post_save
    ↓
handle_deliverable_definition_version_created (signals.py)
    ↓
upgrade_node_definition_version_when_deliverable_changes (node/definition/utils.py)
    ↓
查找所有引用旧交付物版本的节点定义
    ↓
为每个节点定义创建新版本（复制所有关联数据）
    ↓
更新交付物映射到新版本
```

**防重复处理**：
- 使用缓存标记（`deliverable_version_upgrade_{instance.id}`）防止重复处理
- 缓存有效期 5 分钟

**信号注册**：
- 信号文件：`apps/PSC/deliverable/definition/signals.py`
- 导入位置：`apps/PSC/signals.py`


## 常见业务场景

### 场景 1: 创建交付物定义（code 自动生成）

```python
# 业务流程（code 为空）
POST /psc/deliverable/definition/list
{
  "name": "项目需求",
  "remark": "需求文档"
}

# 结果：
# code 自动生成为 "DELIV0001"
# display_version 默认为 "1.0"
```

### 场景 2: 创建交付物定义（指定 code 和 displayVersion）

```python
# 业务流程（指定 code）
POST /psc/deliverable/definition/list
{
  "code": "PROJECT_REQUIREMENT",
  "name": "项目需求",
  "displayVersion": "v1.0.0",
  "remark": "需求文档"
}

# 结果：使用指定的 code 和 displayVersion
```

### 场景 3: 版本迭代（PUT，code/name 非必填）

```python
# 业务流程
PUT /psc/deliverable/definition/{id}
{
  "displayVersion": "v2.0.0",
  "remark": "新版本备注"
}
# code 和 name 保持不变，仅创建新版本
```

### 场景 4: 批量更新状态（PATCH）

```python
# 业务流程
1. PATCH /psc/deliverable/definition/list
2. 请求体: { "ids": [1, 2, 3], "isActive": false }
3. 批量更新 is_active 状态
```


## 技术实现建议 (Django)

### 双版本号管理 (🆕 Since 2026-02-28)

```python
# models.py
class DeliverableDefinitionVersion(models.Model):
    version_number = models.IntegerField(verbose_name='版本号内部')
    display_version = models.CharField(
        max_length=50,
        blank=True,
        default='1.0',
        verbose_name='版本号'
    )
    remark = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )  # 🆕

    def __str__(self):
        # 仅显示用户自定义版本号
        return f"{self.deliverable_definition.code} {self.display_version}"

    def save(self, *args, **kwargs):
        # 自动设置内部版本号
        if self.is_current and not self.id:
            max_version = DeliverableDefinitionVersion.objects.filter(
                deliverable_definition=self.deliverable_definition
            ).aggregate(models.Max('version_number'))['version_number__max'] or 0
            self.version_number = max_version + 1
        super().save(*args, **kwargs)

# serializers.py
class DeliverableDefinitionVersionSimpleSerializer(serializers.ModelSerializer):
    displayVersion = serializers.CharField(source='display_version', read_only=True)
    remark = serializers.CharField(source='remark', read_only=True)  # 🆕
    # 注意：不返回 version_number

class WriteSerializer(serializers.Serializer):
    displayVersion = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default='1.0',
        source='display_version'
    )
    remark = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )  # 🆕

    def create(self, validated_data):
        version_data = {
            'display_version': validated_data.get('display_version', '1.0'),
            'remark': validated_data.get('remark'),  # 🆕
            # ...
        }

# utils.py
def get_list_queryset():
    latest_version = DeliverableDefinitionVersion.objects.filter(
        deliverable_definition=OuterRef('pk'),
        is_current=True
    ).order_by('-version_number')[:1]

    return DeliverableDefinition.objects.annotate(
        currentVersionId=Subquery(latest_version.values('id')),
        currentDisplayVersion=Subquery(latest_version.values('display_version')),  # 🆕
        # 注意：不暴露 version_number
    ).order_by('-id')
```

### 编码自动生成

```python
# models.py
from apps.SM.code.utils import get_unique_code

class DeliverableDefinition(models.Model):
    code = models.CharField(max_length=255, default='', unique=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_unique_code('DELIV', DeliverableDefinition)
        super().save(*args, **kwargs)

# serializers.py
class WriteSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    name = serializers.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # POST 时（无 instance）：code 和 name 必填
        # PUT 时（有 instance）：code 和 name 非必填
        if not self.instance:
            self.fields['name'].required = True

    def validate_code(self, code):
        # code 为空时跳过验证，将在 save 时自动生成
        if not code or not code.strip():
            return code
        # ... 唯一性验证
        return code
```

### 时区处理

```python
# 方案一：使用 DateTimeFormatMixin（ModelSerializer）
from utils.date import DateTimeFormatMixin

class DeliverableDefinitionListSerializer(DateTimeFormatMixin, serializers.ModelSerializer):
    # 自动处理所有 DateTimeField 字段
    pass

class DeliverableDefinitionVersionSimpleSerializer(DateTimeFormatMixin, serializers.ModelSerializer):
    # 自动处理 createdAt 等时间字段
    pass

# 方案二：使用 to_local_time（SerializerMethodField）
from utils.date import to_local_time

class DeliverableDefinitionDetailSerializer(serializers.Serializer):
    def get_others(self, obj):
        return {
            'createdAt': to_local_time(obj.created_at.isoformat()) if obj.created_at else None,
            'updatedAt': to_local_time(obj.updated_at.isoformat()) if obj.updated_at else None,
            'versionCount': obj.versions.count(),
        }
```

### 查询优化

```python
# utils.py - 使用 annotate + Subquery 预加载
def get_list_queryset():
    from django.db.models import OuterRef, Subquery

    latest_version = DeliverableDefinitionVersion.objects.filter(
        deliverable_definition=OuterRef('pk'),
        is_current=True
    ).order_by('-version_number')[:1]

    return DeliverableDefinition.objects.annotate(
        currentVersionId=Subquery(latest_version.values('id')),
        currentDisplayVersion=Subquery(latest_version.values('display_version')),
    ).order_by('-id')
```

### 序列化器策略

```python
# 1. 列表序列化器 - 扁平化输出 + DateTimeFormatMixin
class DeliverableDefinitionListSerializer(DateTimeFormatMixin, ToInternalValueMixin, serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active')
    currentVersionId = serializers.IntegerField(read_only=True)
    currentDisplayVersion = serializers.CharField(read_only=True)  # 🆕
    # ... 其他预加载字段

# 2. 详情序列化器 - 分块输出 + to_local_time
class DeliverableDefinitionDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    document = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    others = serializers.SerializerMethodField()
    # get_others 使用 to_local_time 处理时区

# 3. 版本序列化器 - DateTimeFormatMixin + displayVersion + remark 🆕
class DeliverableDefinitionVersionSimpleSerializer(DateTimeFormatMixin, serializers.ModelSerializer):
    displayVersion = serializers.CharField(source='display_version', read_only=True)  # 🆕
    remark = serializers.CharField(source='remark', read_only=True)  # 🆕
    # 自动处理 createdAt 时区转换

# 4. 写入序列化器 - POST/PUT 复用 + 动态必填 + displayVersion + remark 🆕
class WriteSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False)
    displayVersion = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default='1.0',
        source='display_version'
    )  # 🆕
    remark = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )  # 🆕
    # __init__ 中动态设置 required（POST 必填，PUT 非必填）
```


## 关键文件索引

| 文件路径 | 说明 |
|----------|------|
| `apps/PSC/deliverable/definition/models.py` | 数据模型定义 |
| `apps/PSC/deliverable/definition/serializers.py` | 序列化器 |
| `apps/PSC/deliverable/definition/views.py` | 视图逻辑 |
| `apps/PSC/deliverable/definition/utils.py` | 公共查询函数 |
| `apps/PSC/deliverable/definition/urls.py` | 路由配置 |
| `apps/SM/code/utils.py` | 编码生成工具函数 |
| `utils/date.py` | 时区转换工具（`to_local_time`, `DateTimeFormatMixin`） |


## 快速参考

### 导入方式

```python
# 推荐：从 PSC 模块统一导入
from apps.PSC.deliverable.definition.models import DeliverableDefinition, DeliverableDefinitionVersion

# 引用文件扩展名类型
from apps.PSC.file_extension_type.models import FileExtensionType

# 引用编码生成工具
from apps.SM.code.utils import get_unique_code

# 引用时区转换工具
from utils.date import to_local_time, DateTimeFormatMixin
```

### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/psc/deliverable/definition/list` | GET | 列表查询（分页），返回 `currentDisplayVersion` 🆕 |
| `/psc/deliverable/definition/list` | POST | 创建交付物定义（code/name 必填，可设置 displayVersion 和 remark）🆕 |
| `/psc/deliverable/definition/list` | PATCH | 批量更新 isActive |
| `/psc/deliverable/definition/list` | DELETE | 批量删除（允许删除有版本的记录） |
| `/psc/deliverable/definition/{id}` | GET | 获取详情，版本列表包含 `displayVersion` 和 `remark` 🆕 |
| `/psc/deliverable/definition/{id}` | PUT | 版本迭代（code/name 非必填，可更新 displayVersion 和 remark）🆕 |

### API 返回格式

**列表响应：**
```json
{
  "id": 1,
  "code": "PROJECT_REQUIREMENT",
  "name": "项目需求",
  "currentDisplayVersion": "1.0",
  "isActive": true
}
```

**版本详情响应：**
```json
{
  "items": [
    {
      "id": 1,
      "displayVersion": "1.0",
      "remark": "需求文档",
      "isCurrent": true
    }
  ]
}
```

**创建/更新请求：**
```json
{
  "name": "项目需求",
  "displayVersion": "v1.0.0",
  "remark": "需求文档"
}
```

### 已废弃设计 (Deprecated)

| 设计 | 废弃原因 | 替代方案 |
|------|----------|----------|
| `is_review` 字段 | 字段多余，评审逻辑不再需要通过交付物定义判断 | 已移除 ⚠️ |
| `description` 字段 | 字段命名不规范，统一使用 `remark` | `remark` 字段 🆕 |
| `classes` 字段（JSONField） | 改为多对多关联 | `allowed_file_extensions` (M2M) |
| 文件扩展名内联管理 | 抽取为独立模块 | `file_extension_type` 模块 |
| 路由 `/file_extension_type/list` | 模块独立化 | `/psc/deliverable/file-extension-type/list` |
| `folder` 字段 | 字段冗余，已移除 | 不再使用 |
| 单一版本号设计 | 需要区分内部版本号和用户版本号 | 双版本号体系 🆕 |
| 暴露内部 version_number | 内部版本号不应对外展示 | 仅返回 displayVersion 🆕 |
| `is_required` 字段 | 必填性迁移至节点定义映射表 | `NodeDefinitionDeliverableMapping.is_required` |
| `is_temp_appley_test` 字段 | 字段冗余，已移除 | 不再使用 |


## 版本历史

### v2.5.0 - is_required 迁移 (2026-03-27)

- [x] 移除 `DeliverableDefinition.is_temp_appley_test` 字段
- [x] 移除 `DeliverableDefinitionVersion.is_required` 字段
- [x] `is_required` 迁移至 `NodeDefinitionDeliverableMapping.is_required`
- [x] 移除所有序列化器中的 `isRequired` / `currentIsRequired` 字段
- [x] 移除 `utils.get_list_queryset()` 中的 `currentIsRequired` annotation
- [x] 创建数据库迁移文件

### v2.4.0 - 信号驱动机制 (2026-03-10)

- [x] 新增 `signals.py` 信号处理器文件
- [x] 新增 `handle_deliverable_definition_version_created` 信号处理器
- [x] 交付物定义版本变化自动触发节点定义版本升级
- [x] 防重复处理机制（缓存标记）
- [x] 在 `apps/PSC/signals.py` 中注册信号

### v2.3.0 - 字段优化 (2026-03-05) 🆕

- [x] 移除 `is_review` 字段（字段多余，评审逻辑不再需要通过交付物定义判断）⚠️
- [x] `description` 字段重命名为 `remark`（字段命名规范化）🆕
- [x] 更新所有序列化器引用
- [x] 更新跨模块引用（`apps/PM/nodelist/deliverable/serializers.py`）
- [x] 创建数据库迁移文件

### v2.2.0 - 双版本号体系 (2026-02-28) 🆕

- [x] 新增 `display_version` 字段（用户版本号，String，默认 "1.0"）🆕
- [x] 保留 `version_number` 字段（内部版本号，Integer，自动递增）🆕
- [x] 更新 `__str__` 方法，仅显示用户版本号 🆕
- [x] 列表查询返回 `currentDisplayVersion` 🆕
- [x] 版本详情序列化器返回 `displayVersion` 🆕
- [x] 写入序列化器支持设置 `displayVersion` 🆕

### v2.1.1 - 字段权限与时区处理 (2026-02-27)

- [x] `name` 字段：POST 时必填，PUT 时非必填
- [x] `DeliverableDefinitionDetailSerializer` 使用 `to_local_time` 处理时区
- [x] `DeliverableDefinitionVersionSimpleSerializer` 添加 `DateTimeFormatMixin`
- [x] 删除验证：允许删除有版本的记录（验证已被注释）

### v2.1.0 - 编码自动生成与字段清理 (2026-02-27)

- [x] `code` 字段支持自动生成（`get_unique_code('DELIV', ...)`）
- [x] 移除 `folder` 字段（模型、序列化器、utils）⚠️
- [x] `WriteSerializer.code` 改为非必填（`required=False`）

### v2.0.0 - 模块重构

- [x] `classes` 字段改为 `allowed_file_extensions` (ManyToManyField)
- [x] 文件扩展名类型抽取为独立模块 `file_extension_type`
- [x] 列表查询使用 `annotate()` + `Subquery()` 优化
- [x] 详情接口改为分块输出（id, document, items, others）
- [x] 字段权限控制（code/name POST-only, isActive PATCH-only）

### v1.0.0 - 初始版本

- [x] 基础版本化管理
- [x] 视图分层架构
