# PM 交付物文件夹模块技能

## 模块定位

**交付物文件夹模块** (`apps/PM/deliverable/folder/`) 是 PM 系统中负责管理项目交付物存储文件夹结构的子模块。

### 核心职责
- 🆕 维护项目交付物的四级文件夹层级结构（客户/机型/交付物定义/交付物）（Since 2026-03-07）
- 抽象化存储服务商接口（飞书云文档、阿里云 OSS 等）
- 提供异步文件夹创建能力
- 为交付物模块提供存储基础设施支持

### 模块边界
- **负责**：文件夹的创建、记录、存储服务商对接
- **不负责**：交付物上传业务（由 `apps/PM/deliverable/instance/` 模块处理）
- **不负责**：项目、节点等核心业务逻辑（由 PM 主模块处理）


## 核心数据模型

### 🆕 文件夹层级结构（Since 2026-03-07）

```
PM_deliverable_folder (交付物文件夹表)
├── id: 主键
├── project: 外键 -> PM.Project_List
├── name: 文件夹名称
├── folder_type: 文件夹类型 (枚举)
│   ├── CUSTOMER_ROOT: 客户根文件夹
│   ├── MODEL_ROOT: 机型根文件夹
│   └── 🆕 DELIVERABLE: 交付物定义文件夹（Since 2026-03-07）
├── storage_provider: 存储服务商 (枚举)
│   ├── FEISHU: 飞书云文档
│   └── ALIYUN_OSS: 阿里云 OSS
└── 时间戳

PM_deliverable_folder_feishu (飞书存储信息表)
├── id: 主键
├── folder: OneToOne -> DeliverableFolder
├── folder_token: 飞书文件夹 token
└── 时间戳
```

### 🆕 文件夹层级（Since 2026-03-07）

**旧结构**（Deprecated）：
```
客户编码 (customer_root)
  └── 机型编码 (model_root)
        └── 交付物文件
```

**新结构**：
```
客户编码 (CUSTOMER_ROOT)
  └── 机型编码 (MODEL_ROOT)
        └── 交付物定义编码 (DELIVERABLE)
              └── 交付物文件
```

### 关键设计原则

1. **关联关系由 attachment 侧维护**
   - `DeliverableFolder` 不包含 `attachment` 外键
   - `DeliverableInstance` 通过 `folder` 外键关联到 `DeliverableFolder`
   - 这样设计的原因：交付物是业务主体，文件夹是附属资源

2. **存储服务商抽象化**
   - 通过 `storage_provider` 字段标识使用的存储服务
   - 不同存储服务的特定信息通过关联表存储（如 `DeliverableFolderFeishu`）
   - 便于未来扩展到其他存储服务商（阿里云 OSS、腾讯云 COS 等）

3. **🆕 按交付物定义分类**（Since 2026-03-07）
   - 新增交付物定义文件夹层级，避免交付物文件混乱
   - 通过 `deliverable_definition.code` 获取交付物定义编码
   - 同类型的交付物集中存储


## 枚举定义 (Enums)

```python
class Choices:
    class FolderType(models.TextChoices):
        CUSTOMER_ROOT = 'CUSTOMER_ROOT', '客户根文件夹'
        MODEL_ROOT = 'MODEL_ROOT', '机型根文件夹'
        DELIVERABLE = 'DELIVERABLE', '交付物定义文件夹'  # 🆕 (Since 2026-03-07)
```

**枚举值变更**：
- 从小写+下划线（`customer_root`）改为大写（`CUSTOMER_ROOT`）
- 新增 `DELIVERABLE` 类型


## 🆕 异步任务（Since 2026-03-07）

### async_ensure_folder_exists(project_id, deliverable_definition_code=None)

确保项目的文件夹层级存在，并创建对应的飞书云文档文件夹。

**参数变更**：
- `project_id`: 项目 ID
- 🆕 `deliverable_definition_code`: 交付物定义编码（可选）

**执行流程**：
1. 获取项目信息
2. 创建/获取客户根文件夹 (`CUSTOMER_ROOT`)
3. 确保客户根文件夹的飞书存储存在
4. 创建/获取机型根文件夹 (`MODEL_ROOT`)
5. 确保机型根文件夹的飞书存储存在
6. 🆕 如果提供了 `deliverable_definition_code`：
   - 创建/获取交付物定义文件夹 (`DELIVERABLE`)
   - 确保交付物定义文件夹的飞书存储存在
   - 返回交付物定义文件夹对象
7. 否则返回机型根文件夹对象

**返回值**：
- 如果提供了 `deliverable_definition_code`：返回 `DeliverableFolder` (交付物定义文件夹)
- 否则：返回 `DeliverableFolder` (机型根文件夹)

**使用场景**：
- 项目创建时初始化文件夹结构
- 🆕 交付物上传前确保目标文件夹存在（传入交付物定义编码）

**调用方式变更**：
```python
# 旧方式（Deprecated）
folder = async_ensure_folder_exists(project_id)

# 🆕 新方式（Since 2026-03-07）
deliverable_definition_code = deliverable.definition.deliverable_definition.code
folder = async_ensure_folder_exists(project_id, deliverable_definition_code)
```


## 与其他模块关系

### 依赖关系

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `PM.Project_List` | ForeignKey | 文件夹属于项目 |
| `PM.DeliverableInstance` | 反向关联 | 交付物关联到文件夹 |
| 🆕 `PSC.DeliverableDefinition` | 🆕 弱依赖 | 🆕 获取交付物定义编码（Since 2026-03-07） |
| `utils.openapi.feishu.FeishuFileManager` | 服务依赖 | 🆕 飞书文件管理服务（替代 FeishuStorageProvider） |

### 🆕 模块通信变更（Since 2026-03-07）

**被调用位置变更**：

| 文件 | 函数 | 变更内容 |
|------|------|----------|
| `apps/PM/deliverable/tasks.py` | `async_upload_deliverable_task` | 🆕 传入 `deliverable_definition_code` |
| `apps/PM/deliverable/tasks.py` | `async_move_temp_file_to_folder_task` | 🆕 传入 `deliverable_definition_code` |
| `apps/PM/deliverable/file/tasks.py` | `async_upload_deliverable_task` | 🆕 传入 `deliverable_definition_code` |
| `apps/PM/deliverable/template/tasks.py` | `async_upload_deliverable_task` | 🆕 传入 `deliverable_definition_code` |
| `apps/PM/deliverable/template/serializers.py` | `_create_link` | 🆕 传入 `deliverable_definition_code` |
| `apps/PM/deliverable/template/serializers.py` | `_create_template` | 🆕 传入 `deliverable_definition_code` |


## 常见业务场景

### 🆕 场景 1：交付物上传（Since 2026-03-07）

当用户上传交付物时，需要确保目标文件夹存在（包含交付物定义层级）。

```python
from apps.PM.deliverable.folder.tasks import async_ensure_folder_exists

# 获取交付物定义编码
deliverable_definition_code = deliverable.definition.deliverable_definition.code
# 确保四级文件夹结构存在
folder = async_ensure_folder_exists(project_id, deliverable_definition_code)
```

### 场景 2：项目初始化

当新项目创建时，为客户和机型创建根文件夹。

```python
from apps.PM.deliverable.folder.tasks import async_ensure_folder_exists

# 异步创建基础文件夹结构（不包含交付物定义层级）
async_ensure_folder_exists.delay(project_id)
```


## 技术实现建议

### 1. 添加新的存储服务商

当需要支持新的存储服务商时（如阿里云 OSS）：

1. 在 `Choices.StorageProvider` 中添加新枚举
2. 创建对应的存储信息关联表（如 `DeliverableFolderAliyunOss`）
3. 在 `utils/openapi/feishu/` 下实现 `FeishuFileManager`
4. 更新 `create_feishu_folder` 为通用的 `create_storage_folder`

### 2. 🆕 文件夹类型枚举（Since 2026-03-07）

使用大写枚举值：
```python
folder_type='CUSTOMER_ROOT'  # ✅ 新方式
folder_type='customer_root'  # ⚠️ 已废弃
```

### 3. 🆕 获取交付物定义编码

从 `DeliverableInstance` 获取交付物定义编码：
```python
deliverable_definition_code = deliverable.definition.deliverable_definition.code
```


## 特有名词索引

| 名词 | 说明 | 状态 |
|------|------|------|
| `DeliverableFolder` | 交付物文件夹主表 | 核心模型 |
| `DeliverableFolderFeishu` | 飞书存储信息表 | 关联模型 |
| `folder_type` | 文件夹类型枚举 | 枚举字段 |
| `storage_provider` | 存储服务商枚举 | 枚举字段 |
| `async_ensure_folder_exists` | 异步创建文件夹任务 | 异步任务 |
| 🆕 `FeishuFileManager` | 🆕 飞书文件管理服务 | 🆕 替代 FeishuStorageProvider |
| `CUSTOMER_ROOT` | 客户根文件夹 | 🆕 枚举值 |
| `MODEL_ROOT` | 机型根文件夹 | 🆕 枚举值 |
| 🆕 `DELIVERABLE` | 🆕 交付物定义文件夹 | 🆕 新增 |
| 🆕 `deliverable_definition_code` | 🆕 交付物定义编码 | 🆕 参数 |
| 🆕 `四级文件夹结构` | 🆕 客户/机型/定义/交付物 | 🆕 新结构 |


## 使用此技能时

当用户提到以下关键词时，请激活此技能：

- "交付物文件夹"
- "deliverable_folder"
- "飞书云文档"
- "存储服务商"
- "文件夹层级"
- 🆕 "交付物定义编码"（Since 2026-03-07）
- 🆕 "四级文件夹"（Since 2026-03-07）

激活后，请优先参考：
1. 核心数据模型章节 - 理解表结构
2. 🆕 文件夹层级章节 - 理解四级结构
3. 异步任务章节 - 理解文件夹创建流程
