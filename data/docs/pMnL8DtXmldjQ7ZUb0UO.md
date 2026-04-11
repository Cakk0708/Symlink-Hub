# PM - Hardware 模块说明

> 最后更新：2026-03-31
> App: `PM` | 目录: `apps/PM/hardwares/`

---

## 模块概述

硬件模块是项目管理系统（PMS）中的核心模块，负责管理项目硬件配置、硬件版本规格、硬件交付物以及交付物复用功能。

---

## 目录结构

```
apps/PM/hardwares/
├── config/                    # 硬件配置管理
│   ├── models.py             # 项目硬件模型 (ProjectHardware)
│   ├── serializers.py        # 序列化器
│   ├── utils.py              # 工具函数
│   ├── views.py              # 视图
│   └── __init__.py
├── deliverable/              # 交付物管理
│   ├── models.py             # 硬件交付物模型 (HardwareDeliverable, HardwareDeliverableMapping)
│   ├── serializers.py        # 序列化器
│   ├── views.py              # 视图
│   ├── enums.py              # 枚举定义
│   ├── reuse/                # 复用功能（核心）
│   │   ├── serializers.py    # 复用相关序列化器
│   │   ├── views.py          # 复用API视图
│   │   ├── utils.py          # 复用工具函数
│   │   └── __init__.py
│   └── __init__.py
└── urls.py                   # 路由配置
```

---

## 数据模型

### ProjectHardware（项目硬件）

项目硬件是项目与硬件规格的关联实体，记录每个项目使用的硬件配置。

**表名**: `PM_hardware`

**关键字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| project | ForeignKey | 所属项目 (PM.Project_List) |
| node | ForeignKey | 所属节点 (PM.Project_Node) |
| version | ForeignKey | 硬件版本规格 (PSC.Hardware_Spec_Child) |
| quantity | Integer | 分板数量 |
| is_need_program | Boolean | 是否需要程序 |
| remark | String | 备注 |

**属性方法**:
- `hardware_name`: 硬件名称（从 version.spec.name 获取）
- `category_name`: 分类名称（从 version.spec.category.name 获取）
- `version_code`: 硬件版本号（从 version.version 获取）

---

### HardwareDeliverable（硬件交付物）

硬件交付物是硬件关联的文件实体，存储固件、程序等交付物信息。

**表名**: `PM_hardware_deliverable`

**关键字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| file | ForeignKey | 关联的交付物文件 (PM.DeliverableFile) |
| state | String | 交付物状态 (NORMAL/FROZEN/INITIAL_FROZEN/STORAGE_MIGRATION_ERROR) |
| type | String | 交付物类型 (COMMON/STANDARD/REUSED) |
| version | String | 文件版本 |
| creator | ForeignKey | 创建人 (SM.User) |
| create_time | DateTime | 创建时间 |
| update_by | ForeignKey | 最后修改人 (SM.User) |
| update_time | DateTime | 最后修改时间 |

**飞书云文档属性**（从关联的 file.feishu 获取）:
- `token`: 文件唯一标识
- `folder`: 文件夹路径
- `path`: 文件路径

---

### HardwareDeliverableMapping（硬件交付物映射）

硬件交付物映射是实现复用功能的核心模型，记录交付物与硬件的关联关系及复用状态。

**表名**: `PM_hardware_deliverable_mapping`

**关键字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| deliverable | ForeignKey | 关联的硬件交付物 (PM.HardwareDeliverable) |
| hardware | ForeignKey | 关联的项目硬件 (PM.ProjectHardware) |
| node | ForeignKey | 所属节点 (PM.Project_Node) |
| reuse_status | String | 复用状态 (ORIGINAL/REUSED) |
| remark | String | 备注 |
| creator | ForeignKey | 创建人 (SM.User) |
| create_time | DateTime | 创建时间 |
| update_by | ForeignKey | 最后修改人 (SM.User) |
| update_time | DateTime | 最后修改时间 |

---

## 枚举定义

### ReuseStatus（复用状态）

| 值 | 说明 |
|----|------|
| ORIGINAL | 原始附件（未复用，可被复用） |
| REUSED | 直接复用（已被复用） |

### DeliverableState（交付物状态）

| 值 | 说明 |
|----|------|
| NORMAL | 正常（可复用） |
| FROZEN | 冻结（不可修改） |
| INITIAL_FROZEN | 初始冻结（新上传等待异步处理） |
| STORAGE_MIGRATION_ERROR | 储存迁移异常 |

### DeliverableType（交付物类型）

| 值 | 说明 |
|----|------|
| COMMON | 通用程序（可被复用） |
| STANDARD | 标准程序（不可复用） |
| REUSED | 复用（标记为复用类型） |

---

## 核心功能

### 1. 硬件配置管理

**路径**: `config/`

**功能**:
- 获取项目硬件信息
- 选择硬件版本规格
- 管理硬件配置

**API接口**:
- `GET /hardware/project` - 获取项目硬件信息
- `GET /hardware/version` - 选择硬件版本
- `GET /hardware/version/<int:id>` - 获取特定版本信息

---

### 2. 交付物管理

**路径**: `deliverable/`

**功能**:
- 创建硬件交付物实例
- 设置为通用程序
- 冻结/解冻程序
- 批量替换交付物

**API接口**:
- `GET /hardware/deliverable/instance` - 获取硬件交付物实例
- `POST /hardware/deliverable/instance` - 创建交付物实例
- `POST /hardware/deliverable/common/<int:id>` - 设置为通用程序
- `POST /hardware/deliverable/freeze/<str:action>` - 冻结/解冻程序
- `POST /hardware/deliverable/replace` - 批量替换交付物

---

### 3. 硬件复用功能

**路径**: `deliverable/reuse/`

**功能**:
- 获取可复用的交付物列表
- 执行复用操作（将通用程序复制到目标硬件）
- 替换已复用的交付物

**复用条件**:
1. 交付物状态必须是 `NORMAL`（正常）
2. 交付物类型必须是 `COMMON`（通用程序）
3. 交付物映射必须是 `ORIGINAL` 状态（未被复用）

**复用流程**:
1. 查找符合复用条件的交付物
2. 验证用户权限（必须有目标节点操作权限）
3. 创建新的 `HardwareDeliverableMapping` 记录，`reuse_status` 设置为 `REUSED`

**API接口**:
- `GET /hardware/deliverable/reuse` - 获取可复用的交付物列表
- `POST /hardware/deliverable/reuse` - 执行复用操作
- `PUT /hardware/deliverable/reuse/<str:action>` - 替换已复用的交付物

---

## 对外接口

### 序列化器

#### ReuseVisibleSerializer
复用查询结果序列化器，用于返回可复用的交付物列表。

**输出结构**:
```python
{
    'id': int,
    'create_time': str,
    'reuse_status': str,
    'project_info': {
        'id': int,
        'name': str,
        'model': str
    },
    'hardware_info': {
        'id': int,
        'name': str,
        'version': str,
        'category': {
            'id': int,
            'name': str
        }
    },
    'attachment_info': {
        'id': int,
        'name': str,
        'creator': str,
        'create_time': str,
        'state': str,
        'operation': bool,
        'type': str,
        'note': str,
        'file_name': str
    }
}
```

#### ReuseHardwareDeliverableSerializer
复用操作序列化器，处理复用和替换业务逻辑。

**验证逻辑**:
- 用户权限验证（权限码：2011）
- 复用状态校验（不能复用已复用的交付物）
- 交付物类型校验（必须为通用程序）
- 交付物状态校验（必须为正常状态）
- 替换操作额外校验（被替换的交付物若已被复用则不允许替换）

**方法**:
- `execute_reuse()`: 执行复用操作
- `execute_replace()`: 执行替换操作

---

## 依赖关系

### 外部依赖

| 模块 | 依赖说明 |
|------|----------|
| `PM.Project_List` | 项目主表 |
| `PM.Project_Node` | 项目节点 |
| `PM.DeliverableFile` | 交付物文件主表 |
| `PSC.Hardware_Spec_Child` | 硬件版本规格 |
| `PSC.Hardware_Category` | 硬件分类 |
| `SM.User` | 用户表 |

### 内部依赖

- `PM.hardwares.config.models.ProjectHardware`
- `PM.hardwares.deliverable.models.HardwareDeliverable`
- `PM.hardwares.deliverable.models.HardwareDeliverableMapping`

---

## 工具函数

### get_hardware_deliverable_reuse_list

**路径**: `deliverable/reuse/utils.py`

**功能**: 获取可复用的硬件交付物列表

**参数**:
- `category`: 硬件分类（可选）
- `search_key`: 搜索关键词（可选）

**返回**: QuerySet（可复用的交付物映射列表）

**筛选条件**:
```python
Q(
    deliverable__state=Choices.DeliverableState.NORMAL,
    deliverable__type=Choices.DeliverableType.COMMON,
    reuse_status=Choices.ReuseStatus.ORIGINAL
)
```

---

## 权限控制

模块使用 `AuthorityVerifier` 进行权限验证：

| 操作 | 权限码 | 说明 |
|------|--------|------|
| 复用/替换交付物 | 2011 | 节点操作权限 |

---

## 禁止事项

1. **禁止复用已复用的交付物**: 复用状态为 `REUSED` 的交付物不能再次被复用
2. **禁止复用非通用程序**: 只有类型为 `COMMON` 的交付物可以被复用
3. **禁止复用非正常状态的交付物**: 只有状态为 `NORMAL` 的交付物可以被复用
4. **禁止替换已被复用的原始交付物**: 如果原始交付物已被其他记录复用，则不允许替换
5. **禁止在无权限情况下操作**: 所有复用操作都需要节点操作权限

---

## 数据关系图

```
Project_List (项目)
    ↓ (1:N)
ProjectHardware (项目硬件)
    ↓ (1:N)
HardwareDeliverableMapping (硬件交付物映射)
    ↓ (N:1)
HardwareDeliverable (硬件交付物)
    ↓ (N:1)
DeliverableFile (交付物文件)
    ↓ (1:1)
DeliverableFileFeishu (飞书云文档)
```

---

## 相关文档

- **API接口文档**: `.claude/docs/api/pm-hardware-reuse.md`
- **数据关系**: `.claude/docs/data-relationship.md`
- **数据流**: `.claude/docs/data-flow.md`
