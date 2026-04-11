---
name: utils-feishu-file_manager
description: 飞书文件管理器专家。统一管理飞书文件相关接口，包括文件上传、下载、移动、复制、删除等操作。当用户提到 FeishuFileManager、文件上传、飞书 API、文件管理时激活此技能。
---

# 飞书文件管理器技能

## 模块定位

**飞书文件管理器** (`utils/openapi/feishu/file_manager.py`) 是统一管理飞书文件操作的核心模块。

### 核心职责
- 提供统一的飞书文件操作接口
- 封装飞书开放平台 API（文件上传、移动、复制、删除等）
- 支持小文件直接上传和大文件分片上传
- 提供带重试机制的高级文件操作

### 模块边界
- **负责**：飞书文件和文件夹的所有操作
- **不负责**：业务逻辑（由调用方模块处理）
- **不负责**：权限验证（假设调用方已处理）

---

## 核心类

### FeishuFileManager

**位置**：`utils/openapi/feishu/file_manager.py:17`

```python
class FeishuFileManager:
    """
    飞书文件管理器

    提供统一的文件操作接口，包括基础文件操作和高级功能如重试机制等。
    """

    def __init__(self, access_token=''):
        """
        初始化文件管理器

        Args:
            access_token: 用户访问令牌，为空时使用应用令牌
        """
```

---

## 方法列表

### 文件夹操作

#### folder_create(name, parent_token)

**功能**：创建文件夹

**参数**：
- `name`: 文件夹名称
- `parent_token`: 父文件夹 token

**返回**：`str` - 新创建的文件夹 token，失败返回 `False`

#### folder_get_info(folder_token)

**功能**：获取文件夹信息

**参数**：
- `folder_token`: 文件夹 token

**返回**：`dict` - 文件夹信息，失败返回 `False`

---

### 文件上传操作

#### file_upload(parent_token, name, file_data, size)

**功能**：上传文件到文件夹（小文件，<15MB）

**参数**：
- `parent_token`: 目标文件夹 token
- `name`: 文件名
- `file_data`: 文件二进制数据
- `size`: 文件大小（字节）

**返回**：`str` - 文件 token，失败返回 `False`

#### file_split_upload_prepare(parent_token, name, size)

**功能**：准备分片上传（大文件）

**参数**：
- `parent_token`: 目标文件夹 token
- `name`: 文件名
- `size`: 文件大小（字节）

**返回**：`str` - 上传 ID，失败返回 `False`

#### file_split_upload_part(upload_id, part_number, part_data)

**功能**：上传分片

**参数**：
- `upload_id`: 上传 ID
- `part_number`: 分片序号（从 0 开始）
- `part_data`: 分片二进制数据

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

#### file_split_upload_finish(upload_id, part_count)

**功能**：完成分片上传

**参数**：
- `upload_id`: 上传 ID
- `part_count`: 分片总数

**返回**：`str` - 文件 token，失败返回 `False`

---

### 🆕 高级上传功能（Since 2026-03-07）

#### upload_file_to_temp(file_data, file_name, file_size)

**功能**：上传文件到临时文件夹，自动选择普通/分片上传

**参数**：
- `file_data`: 文件二进制数据
- `file_name`: 文件名
- `file_size`: 文件大小（字节）

**返回**：`str` - 临时文件 token，失败返回 `False`

**逻辑**：
- 小文件（<15MB）：使用 `file_upload()` 直接上传
- 大文件（≥15MB）：使用 `_upload_large_file()` 分片上传

#### _upload_large_file(parent_token, file_name, file_data, file_size)

**功能**：分片上传大文件（私有方法）

**参数**：
- `parent_token`: 目标文件夹 token
- `file_name`: 文件名
- `file_data`: 文件二进制数据
- `file_size`: 文件大小（字节）

**返回**：`str` - 文件 token，失败返回 `False`

**流程**：
1. 调用 `file_split_upload_prepare()` 准备上传
2. 按 4MB 分片循环调用 `file_split_upload_part()` 上传
3. 调用 `file_split_upload_finish()` 完成上传（带重试，最多 10 次）

---

### 文件移动/复制/删除操作

#### file_move(file_token, file_type, folder_token)

**功能**：移动文件到文件夹

**参数**：
- `file_token`: 文件 token
- `file_type`: 文件类型 (file/folder)
- `folder_token`: 目标文件夹 token

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

#### 🆕 move_file_with_retry(file_token, file_type, folder_token, max_retries=10)

**功能**：移动文件到指定文件夹（带重试机制）

**参数**：
- `file_token`: 文件 token
- `file_type`: 文件类型 (file/folder)
- `folder_token`: 目标文件夹 token
- `max_retries`: 最大重试次数（默认 10）

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

**逻辑**：
- 循环调用 `file_move()` 最多 `max_retries` 次
- 每次重试间隔 0.5 秒
- 任意一次成功即返回 `True`

#### file_copy(file_token, name, folder_token, file_type)

**功能**：复制文件到文件夹

**参数**：
- `file_token`: 源文件 token
- `name`: 新文件名
- `folder_token`: 目标文件夹 token
- `file_type`: 文件类型

**返回**：`str` - 新文件 token，失败返回 `False`

#### file_delete(file_token, file_type)

**功能**：删除文件

**参数**：
- `file_token`: 文件 token
- `file_type`: 文件类型

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

#### file_get_info(file_tokens)

**功能**：批量获取文件信息

**参数**：
- `file_tokens`: 文件 token 列表 [{'doc_token': token, 'doc_type': type}]

**返回**：`list` - 文件信息列表，失败返回 `False`

---

### 系统配置

#### get_root_folder_token()

**功能**：获取系统根文件夹 token

**返回**：`str` - 根文件夹 token

#### get_temp_folder_token()

**功能**：获取临时文件夹 token

**返回**：`str` - 临时文件夹 token

---

## 使用场景

### 场景 1：上传小文件

```python
from utils.openapi.feishu import FeishuFileManager

manager = FeishuFileManager()
file_token = manager.file_upload(
    parent_token='folder_token',
    name='document.pdf',
    file_data=file_bytes,
    size=len(file_bytes)
)
```

### 场景 2：上传大文件

```python
from utils.openapi.feishu import FeishuFileManager

manager = FeishuFileManager()
file_token = manager.upload_file_to_temp(
    file_data=large_file_bytes,
    file_name='large_file.zip',
    file_size=len(large_file_bytes)
)
```

### 场景 3：移动文件（带重试）

```python
from utils.openapi.feishu import FeishuFileManager

manager = FeishuFileManager()
success = manager.move_file_with_retry(
    file_token='temp_token',
    file_type='file',
    folder_token='target_folder_token',
    max_retries=10
)
```

### 场景 4：使用用户权限

```python
from utils.openapi.feishu import FeishuFileManager
from utils.openapi.feishu import FeishuTokenManager

user_token = FeishuTokenManager.get_user_token(user)
manager = FeishuFileManager(access_token=user_token)
file_token = manager.file_upload(...)
```

---

## 模块演进

### ⚠️ 已废弃（Deprecated）

**FeishuStorageProvider** (`utils/openapi/feishu/storage.py`)

- **废弃时间**：2026-03-07
- **原因**：功能已合并到 `FeishuFileManager`
- **替代方案**：使用 `FeishuFileManager`

### 🆕 新增（Since 2026-03-07）

**FeishuFileManager** (`utils/openapi/feishu/file_manager.py`)

- 新增高级上传功能 `upload_file_to_temp()`
- 新增重试机制 `move_file_with_retry()`
- 统一管理所有文件操作接口

---

## 与其他模块关系

### 被依赖的模块

| 模块 | 用途 | 调用方法 |
|------|------|----------|
| `PM/deliverable/folder` | 文件夹创建 | `folder_create()` |
| `PM/deliverable/tasks` | 文件上传/移动 | `file_upload()`, `move_file_with_retry()` |
| `PM/deliverable/file/tasks` | 文件上传 | `file_upload()` |
| `PM/deliverable/template/tasks` | 文件上传 | `file_upload()` |

### 依赖的服务

| 服务 | 用途 |
|------|------|
| `FeishuTokenManager` | 获取访问令牌 |
| 飞书开放平台 API | 文件操作 |

---

## 特有名词索引

| 名词 | 说明 | 状态 |
|------|------|------|
| `FeishuFileManager` | 飞书文件管理器 | 核心类 |
| `file_upload` | 上传小文件 | 方法 |
| `file_split_upload_prepare` | 准备分片上传 | 方法 |
| `file_split_upload_part` | 上传分片 | 方法 |
| `file_split_upload_finish` | 完成分片上传 | 方法 |
| `upload_file_to_temp` | 🆕 自动选择上传方式 | 方法 |
| `move_file_with_retry` | 🆕 带重试的文件移动 | 方法 |
| `file_copy` | 复制文件 | 方法 |
| `file_delete` | 删除文件 | 方法 |
| `file_get_info` | 获取文件信息 | 方法 |
| `get_temp_folder_token` | 获取临时文件夹 | 方法 |
| `FeishuStorageProvider` | ⚠️ 已废弃 | Deprecated |

---

## 使用此技能时

当用户提到以下关键词时，请激活此技能：

- "FeishuFileManager"
- "文件上传"
- "飞书 API"
- "文件管理"
- "file_upload"
- "move_file"
- 🆕 "file_manager"（Since 2026-03-07）

激活后，请优先参考：
1. 核心类章节 - 理解类结构
2. 方法列表章节 - 查找具体方法
3. 使用场景章节 - 参考示例代码
