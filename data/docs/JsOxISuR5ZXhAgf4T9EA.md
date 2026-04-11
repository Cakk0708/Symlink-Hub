# Utils OpenAPI Feishu 模块 (utils-openapi-feishu)

## 模块定位

飞书开放平台 API 统一管理模块，位于 `utils/openapi/feishu/`，提供对飞书开放平台 API 的封装和管理功能。

### 在项目中的位置

```
utils/
├── openapi/              # 开放平台 API 封装
│   └── feishu/          # 飞书开放平台 API ← 当前模块
│       ├── __init__.py
│       ├── token_manager.py    # Token 管理
│       ├── auth_manager.py     # 认证管理
│       ├── user_manager.py     # 用户管理
│       ├── message_manager.py  # 消息管理
│       ├── file_manager.py     # 文件管理
│       └── sheet_manager.py    # 表格管理
├── api_security/         # API 安全
├── serializer/           # 序列化工具
├── api_utils.py          # API 工具
├── conversion.py         # 数据转换
├── date.py               # 时间处理
├── redis.py              # Redis 工具
└── user.py               # 用户工具
```

## 模块职责边界

### 核心职责

1. **Token 管理**：tenant_access_token、user_access_token、app_access_token 的获取和刷新
2. **认证管理**：飞书 OAuth 认证流程、授权码换取 token
3. **用户管理**：获取用户信息、批量获取用户、用户部门信息
4. **消息管理**：发送模板消息、更新消息、批量发送消息
5. **文件管理**：文件上传、下载、移动、复制、删除，文件夹操作
6. **表格管理**：电子表格创建、数据读写、样式设置

### 不负责的内容

- ❌ 消息模型定义由 `apps/SM/messages/` 模块负责
- ❌ 用户模型定义由 `apps/SM/user/` 模块负责
- ❌ 审批流逻辑由 `apps/SM/approval/` 模块负责
- ❌ 业务逻辑处理（本模块仅提供 API 封装）

## 核心组件

### 1. FeishuTokenManager（Token 管理器）

**文件位置**：`utils/openapi/feishu/token_manager.py`

统一的飞书 Token 管理，支持三种 Token 类型：

| Token 类型 | 用途 | 缓存策略 |
|-----------|------|---------|
| `tenant_access_token` | 机器人 token，用于应用级 API 调用 | Redis 缓存，提前 5 分钟刷新 |
| `app_access_token` | 应用 token，用于刷新用户 token | Redis 缓存，提前 5 分钟刷新 |
| `user_access_token` | 用户 token，用于用户级 API 调用 | 存储在 UserFeishu 模型，自动刷新 |

#### 主要方法

```python
class FeishuTokenManager:
    @classmethod
    def get_tenant_token(cls) -> str:
        """获取 tenant_access_token（机器人 token）"""

    @classmethod
    def get_user_token(cls, user) -> str:
        """获取有效的 user_access_token，自动处理刷新"""

    @classmethod
    def _is_token_valid(cls, expires_at: str) -> bool:
        """检查 token 是否有效（提前 5 分钟刷新）"""

    @classmethod
    def _fetch_tenant_token(cls, cache_key: str) -> str:
        """从飞书 API 获取新的 tenant_access_token"""

    @classmethod
    def _refresh_user_token(cls, token_obj) -> str:
        """使用 refresh_token 刷新用户 token"""

    @classmethod
    def _get_app_token(cls) -> str:
        """获取 app_access_token（用于刷新用户 token）"""
```

**缓存策略**：

- 缓存键格式：`feishu:tenant_access_token:v2`、`feishu:app_access_token:v2`
- 缓存时间：与 token 有效期一致（通常 2 小时）
- 提前刷新：在过期前 5 分钟自动刷新

### 2. FeishuAuthManager（认证管理器）

**文件位置**：`utils/openapi/feishu/auth_manager.py`

封装飞书 OAuth 认证流程相关的 API 调用。

#### 主要方法

```python
class FeishuAuthManager:
    @classmethod
    def exchange_code(cls, code: str) -> Optional[Dict]:
        """
        通过授权码换取访问令牌

        Args:
            code: 飞书 OAuth 授权码

        Returns:
            Dict: {'access_token': 'xxx', 'refresh_token': 'yyy', 'token_type': 'Bearer'}
        """

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Optional[Dict]:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            Dict: 包含新的 access_token, refresh_token, token_type
        """

    @classmethod
    def format_token(cls, token_type: str, access_token: str) -> str:
        """格式化 token 为 Authorization header 格式"""
```

**使用场景**：

- 飞书用户登录流程（`apps/API/auth/utils.py`）
- 用户 token 刷新（`FeishuTokenManager` 内部调用）

### 3. FeishuUserManager（用户管理器）

**文件位置**：`utils/openapi/feishu/user_manager.py`

封装飞书用户信息相关的 API 调用。

#### 主要方法

```python
class FeishuUserManager:
    @classmethod
    def get_user_info(cls, token: str) -> Optional[Dict]:
        """
        获取用户信息

        Args:
            token: 访问令牌，格式："{token_type} {access_token}"

        Returns:
            Dict: {'nickname': '张三', 'avatar': 'https://...', 'mobile': '13800138000', 'open_id': 'ou_xxx'}
        """

    @classmethod
    def batch_get_user_info(cls, user_ids: List[str], access_token: Optional[str] = None) -> Dict:
        """
        批量获取用户信息

        Args:
            user_ids: open_id 列表
            access_token: 可选的访问令牌

        Returns:
            Dict: {'status': 'SUCCESS' | 'ERROR' | 'INCORRECT', 'data': [...]}
        """

    @classmethod
    def get_user_departments(cls, open_id: str, access_token: Optional[str] = None) -> Optional[List[Dict]]:
        """
        获取用户的部门信息

        第一步：获取用户的 department_ids
        第二步：根据 department_ids 逐个请求部门详情获取部门名称

        Returns:
            List[Dict]: [{'id': 'od_xxx', 'name': '部门名称'}, ...]
        """

    @classmethod
    def _get_department_info(cls, department_id: str, headers: Dict) -> Optional[Dict]:
        """获取单个部门的详细信息"""
```

**使用场景**：

- 飞书用户登录后获取用户信息
- 批量获取用户信息（如项目成员列表）
- 同步用户部门信息（`apps/SM/user/tasks.py`）

### 4. FeishuMessageManager（消息管理器）

**文件位置**：`utils/openapi/feishu/message_manager.py`

封装飞书消息相关的 API 调用，支持发送模板消息和批量消息。

#### 主要方法

```python
class FeishuMessageManager:
    @classmethod
    def send_template_message(
        cls,
        receive_id: str,
        template_id: str,
        template_variable: Dict,
        receive_id_type: str = 'open_id',
        access_token: Optional[str] = None
    ) -> Optional[str]:
        """
        发送模板消息

        Args:
            receive_id: 接收人ID（open_id 或 chat_id）
            template_id: 模板ID
            template_variable: 模板变量
            receive_id_type: 接收ID类型（默认 open_id）
            access_token: 可选的访问令牌

        Returns:
            str: 消息ID，失败返回 None
        """

    @classmethod
    def update_template_message(
        cls,
        message_id: str,
        template_id: str,
        template_variable: Dict,
        access_token: Optional[str] = None
    ) -> Optional[str]:
        """
        更新已发送的模板消息

        Returns:
            str: 消息ID，失败返回 None
        """

    @classmethod
    def batch_send_message(
        cls,
        open_ids: List[str],
        template_id: str,
        template_variable: Dict,
        access_token: Optional[str] = None
    ) -> Optional[Dict]:
        """
        批量发送消息

        注意：批量发送消息不能更新消息内容，只能撤回和查看已读情况

        Returns:
            Dict: API 响应数据，失败返回 None
        """

    @classmethod
    def send_message_to_chat(
        cls,
        chat_id: str,
        template_id: str,
        template_variable: Dict,
        access_token: Optional[str] = None
    ) -> Optional[Dict]:
        """
        发送消息到群聊

        Returns:
            Dict: API 响应数据，失败返回 None
        """

    @classmethod
    def send_message(
        cls,
        receive_id: Union[str, List[str]],
        template_id: str,
        template_variable: Dict,
        receive_id_type: str = 'open_id',
        access_token: Optional[str] = None
    ) -> Optional[Union[str, Dict]]:
        """
        通用发送消息方法

        根据 receive_id 的类型自动选择发送方式：
        - 单个 open_id：使用 send_template_message
        - 多个 open_id（列表）：使用 batch_send_message
        - chat_id：使用 send_message_to_chat
        """
```

**使用场景**：

- 审批消息发送（`apps/SM/messages/tasks.py`）
- 通知消息发送（异步任务）
- 卡片消息更新

**API 端点**：

```
POST https://open.feishu.cn/open-apis/im/v1/messages
PATCH https://open.feishu.cn/open-apis/im/v1/messages/{message_id}
POST https://open.feishu.cn/open-apis/message/v4/batch_send/
```

### 5. FeishuFileManager（文件管理器）

**文件位置**：`utils/openapi/feishu/file_manager.py`

统一管理飞书文件相关接口，包括文件上传、下载、移动、复制、删除等操作。

#### 初始化

```python
class FeishuFileManager:
    def __init__(self, access_token=''):
        """
        初始化文件管理器

        Args:
            access_token: 用户访问令牌，为空时使用应用令牌
        """
```

#### 文件夹操作

```python
def folder_create(self, name, parent_token):
    """创建文件夹"""

def folder_get_info(self, folder_token):
    """获取文件夹信息"""
```

#### 文件上传操作

```python
def file_upload(self, parent_token, name, file_data, size):
    """
    上传文件到文件夹（小文件）
    适用于文件小于 15MB
    """

def file_split_upload_prepare(self, parent_token, name, size):
    """准备分片上传（大文件）"""

def file_split_upload_part(self, upload_id, part_number, part_data):
    """上传分片"""

def file_split_upload_finish(self, upload_id, part_count):
    """完成分片上传"""
```

#### 高级上传功能

```python
def upload_file_to_temp(self, file_data, file_name, file_size):
    """
    上传文件到临时文件夹
    根据文件大小自动选择普通上传或分片上传
    """

def _upload_large_file(self, parent_token, file_name, file_data, file_size):
    """
    分片上传大文件
    - 分片大小：4MB
    - 完成上传时带重试机制（最多 10 次）
    """
```

#### 文件移动/复制/删除操作

```python
def file_move(self, file_token, file_type, folder_token):
    """移动文件到文件夹"""

def move_file_with_retry(self, file_token, file_type, folder_token, max_retries=10):
    """移动文件到指定文件夹（带重试机制）"""

def file_copy(self, file_token, name, folder_token, file_type):
    """复制文件到文件夹"""

def file_delete(self, file_token, file_type):
    """删除文件"""

def file_get_info(self, file_tokens):
    """批量获取文件信息"""
```

#### 系统配置

```python
def get_root_folder_token(self):
    """获取系统根文件夹 token"""

def get_temp_folder_token(self):
    """获取临时文件夹 token"""
```

#### 🆕 权限管理操作（Since 2026-03-19）

```python
def permissions_get_members_list(self, file_token, file_type):
    """
    获取文件权限成员列表

    Args:
        file_token: 文件 token
        file_type: 文件类型 (file/folder)

    Returns:
        dict: 成员列表，包含 items 数组
              每个成员包含 member_id、member_type、perm 等信息
    """

def permissions_delete_members(self, file_token, file_type, member_id,
                               member_type):
    """
    删除文件权限成员

    Args:
        file_token: 文件 token
        file_type: 文件类型 (file/folder)
        member_id: 成员 ID
        member_type: 成员类型 (user/group/org)

    Returns:
        dict: 返回数据，失败返回 False
    """

def permissions_add(self, file_token, member_id, file_type, perm,
                    member_type='openid'):
    """
    添加文件权限成员

    Args:
        file_token: 文件 token
        member_id: 成员 ID (open_id)
        file_type: 文件类型 (file/folder)
        perm: 权限类型 (view/edit/full_access)
        member_type: 成员类型 (openid/user/group/org)

    Returns:
        bool: 成功返回 True，失败返回 False
    """
```

**权限类型说明**：

| 权限类型 | 说明 | 权限等级 |
|---------|------|----------|
| `view` | 查看权限 | 1 |
| `edit` | 编辑权限 | 2 |
| `full_access` | 完全控制权限 | 3 |

**使用场景**：

- 交付物文件上传（`apps/PM/deliverable/file/`）
- 项目文件夹创建（`apps/PM/project/folder/`）
- 文件移动和复制操作
- 🆕 交付物飞书权限管理（`apps/PM/deliverable/instance/validators.py`）

**API 端点**：

```
POST https://open.feishu.cn/open-apis/drive/v1/files/create_folder
POST https://open.feishu.cn/open-apis/drive/v1/files/upload_all
POST https://open.feishu.cn/open-apis/drive/v1/files/upload_prepare
POST https://open.feishu.cn/open-apis/drive/v1/files/upload_part/{upload_id}/{part_number}
POST https://open.feishu.cn/open-apis/drive/v1/files/upload_finish
POST https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/move
POST https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/copy
DELETE https://open.feishu.cn/open-apis/drive/v1/files/{file_token}
GET https://open.feishu.cn/open-apis/drive/v1/permissions/{file_token}/members
DELETE https://open.feishu.cn/open-apis/drive/v1/permissions/{file_token}/members/{member_id}
POST https://open.feishu.cn/open-apis/drive/v1/permissions/{file_token}/members
```

**🆕 权限管理示例（Since 2026-03-19）**：

```python
from utils.openapi.feishu import FeishuFileManager

# 初始化文件管理器
manager = FeishuFileManager()

# 获取文件权限成员列表
members = manager.permissions_get_members_list(
    file_token='file_token_xxx',
    file_type='file'
)

# 检查用户是否已有权限
user_open_id = 'ou_xxx'
existing_permission = None
for member in members.get('items', []):
    if member.get('member_id') == user_open_id:
        existing_permission = member.get('perm')
        break

# 添加文件权限（如果用户没有权限）
success = manager.permissions_add(
    file_token='file_token_xxx',
    member_id=user_open_id,
    file_type='file',
    perm='edit',  # view/edit/full_access
    member_type='openid'
)

# 删除文件权限
success = manager.permissions_delete_members(
    file_token='file_token_xxx',
    file_type='file',
    member_id=user_open_id,
    member_type='openid'
)
```

### 6. FeishuSheetManager（表格管理器）

**文件位置**：`utils/openapi/feishu/sheet_manager.py`

飞书电子表格（Sheets）API 统一管理器，负责表格创建、数据读写、样式设置等操作。

#### 主要方法

```python
class FeishuSheetManager:
    def __init__(self, access_token=''):
        """初始化表格管理器"""

    # ========== 新 API ==========

    def get_spreadsheet_information(self, spreadsheet_token):
        """
        获取电子表格信息
        """

    # ========== 旧业务 API（待过度）==========

    def sheet_create(self, name, folder_token):
        """创建电子表格"""

    def sheet_get_detail(self, spreadsheet_token):
        """
        获取工作表
        获取表格中所有工作表及其属性信息
        """

    def sheet_get_info(self, spreadsheet_token, sheet_id):
        """
        查询工作表
        根据工作表 ID 查询工作表属性信息
        """

    def sheet_get_range(self, spreadsheet_token, ranges=None):
        """
        获取指定表的单个范围内容
        """

    def sheet_styles_batch_update(self, sheet_token, styleData):
        """批量设置单元格样式"""

    def sheet_values_batch_update(self, sheet_token, valueRanges):
        """向多个范围写入数据"""

    def sheet_merge_cells(self, sheet_token, mergeData):
        """合并单元格"""

    def sheet_data_validation(self, sheet_token, dataValidation):
        """设置下拉列表"""

    def sheet_spreadsheets_update(self, sheet_token, update_data):
        """
        操作工作表
        支持更新、新增、复制、删除工作表
        """

    def sheet_delete_rows_columns(self, sheet_token, sheet_id, major_dimension, start_index, end_index):
        """删除行或列"""
```

**使用场景**：

- 报表生成
- 数据导入导出
- 项目数据统计

**API 端点**：

```
POST https://open.feishu.cn/open-apis/sheets/v3/spreadsheets
GET https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}
GET https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query
GET https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{ranges}
PUT https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/styles_batch_update
POST https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values_batch_update
```

## 模块导入

### 统一导入方式

```python
from utils.openapi.feishu import (
    FeishuTokenManager,
    FeishuFileManager,
    FeishuAuthManager,
    FeishuUserManager,
    FeishuMessageManager,
)
```

### 直接导入方式

```python
from utils.openapi.feishu.token_manager import FeishuTokenManager
from utils.openapi.feishu.auth_manager import FeishuAuthManager
from utils.openapi.feishu.user_manager import FeishuUserManager
from utils.openapi.feishu.message_manager import FeishuMessageManager
from utils.openapi.feishu.file_manager import FeishuFileManager
from utils.openapi.feishu.sheet_manager import FeishuSheetManager
```

## 使用示例

### 1. 获取 tenant_access_token

```python
from utils.openapi.feishu import FeishuTokenManager

token = FeishuTokenManager.get_tenant_token()
print(token)  # "Bearer xxx"
```

### 2. 飞书用户认证流程

```python
from utils.openapi.feishu import FeishuAuthManager

# 通过授权码换取 token
token_data = FeishuAuthManager.exchange_code('auth_code_xxx')
print(token_data)
# {'access_token': 'xxx', 'refresh_token': 'yyy', 'token_type': 'Bearer'}
```

### 3. 获取用户信息

```python
from utils.openapi.feishu import FeishuUserManager

# 获取用户信息
userinfo = FeishuUserManager.get_user_info("Bearer xxx")
print(userinfo)
# {'nickname': '张三', 'avatar': 'https://...', 'mobile': '13800138000', 'open_id': 'ou_xxx'}

# 获取用户部门信息
departments = FeishuUserManager.get_user_departments('ou_xxx')
print(departments)
# [{'id': 'od_xxx', 'name': '部门名称'}]
```

### 4. 发送模板消息

```python
from utils.openapi.feishu import FeishuMessageManager

# 发送单条消息
message_id = FeishuMessageManager.send_template_message(
    receive_id='ou_xxx',
    template_id='template_xxx',
    template_variable={'key': 'value'}
)

# 批量发送消息
result = FeishuMessageManager.batch_send_message(
    open_ids=['ou_xxx', 'ou_yyy'],
    template_id='template_xxx',
    template_variable={'key': 'value'}
)

# 发送到群聊
result = FeishuMessageManager.send_message_to_chat(
    chat_id='oc_xxx',
    template_id='template_xxx',
    template_variable={'key': 'value'}
)

# 通用发送方法（自动选择发送方式）
result = FeishuMessageManager.send_message(
    receive_id='ou_xxx',  # 或 ['ou_xxx', 'ou_yyy'] 或 'oc_xxx'
    template_id='template_xxx',
    template_variable={'key': 'value'}
)
```

### 5. 文件上传和管理

```python
from utils.openapi.feishu import FeishuFileManager

# 初始化文件管理器
manager = FeishuFileManager()

# 创建文件夹
folder_token = manager.folder_create(
    name='新文件夹',
    parent_token='parent_token_xxx'
)

# 上传小文件（< 15MB）
file_token = manager.file_upload(
    parent_token='folder_token_xxx',
    name='example.pdf',
    file_data=file_bytes,
    size=len(file_bytes)
)

# 上传大文件（>= 15MB，自动分片）
file_token = manager.upload_file_to_temp(
    file_data=large_file_bytes,
    file_name='large_file.pdf',
    file_size=len(large_file_bytes)
)

# 移动文件（带重试）
manager.move_file_with_retry(
    file_token='file_token_xxx',
    file_type='file',
    folder_token='target_folder_token'
)

# 复制文件
new_file_token = manager.file_copy(
    file_token='file_token_xxx',
    name='新文件名.pdf',
    folder_token='target_folder_token',
    file_type='file'
)

# 删除文件
manager.file_delete(
    file_token='file_token_xxx',
    file_type='file'
)
```

### 6. 电子表格操作

```python
from utils.openapi.feishu import FeishuSheetManager

# 初始化表格管理器
manager = FeishuSheetManager(access_token='Bearer xxx')

# 创建电子表格
spreadsheet_token = manager.sheet_create(
    name='新表格',
    folder_token='folder_token_xxx'
)

# 获取工作表详情
sheets = manager.sheet_get_detail(spreadsheet_token)

# 写入数据
manager.sheet_values_batch_update(
    sheet_token=spreadsheet_token,
    valueRanges={
        'valueRanges': [
            {
                'range': f'{sheet_id}!A1:C1',
                'values': [['姓名', '年龄', '部门']]
            }
        ]
    }
)

# 设置样式
manager.sheet_styles_batch_update(
    sheet_token=spreadsheet_token,
    styleData=[
        {
            'ranges': [f'{sheet_id}!A1:C1'],
            'style': {
                'font': {'bold': True, 'fontSize': '12pt'},
                'backColor': '#f0f0f0'
            }
        }
    ]
)
```

## 数据流

### 1. 飞书用户登录流程

```
飞书 OAuth 授权
    ↓
apps/API/auth/utils.py::exchange_code()
    ↓
FeishuAuthManager.exchange_code()
    ├── 使用 FeishuTokenManager.get_tenant_token()
    └── 调用飞书 API 获取 token
    ↓
返回 token_data
    ├── access_token
    ├── refresh_token
    └── token_type
    ↓
创建/更新 User 和 UserFeishu 模型
    ↓
触发 UserFeishu.post_save 信号
    ↓
apps/SM/user/tasks.py::sync_user_departments()
    ↓
FeishuUserManager.get_user_departments()
    └── 同步用户部门信息
```

### 2. 消息发送流程

```
业务逻辑触发
    ↓
创建 Message 模型
    ↓
apps/SM/messages/signals.py::handle_new_message()
    ↓
创建 Message_Feishu 模型
    ↓
apps/SM/messages/signals.py::handle_new_feishu_msg()
    ↓
异步任务: async_send_feishu_msg.delay()
    ↓
apps/SM/messages/tasks.py::async_send_feishu_msg()
    ↓
FeishuMessageManager.send_template_message()
    ├── 使用 FeishuTokenManager.get_tenant_token()
    ├── 调用飞书 API 发送消息
    └── 更新消息状态
```

### 3. 文件上传流程

```
用户上传文件
    ↓
apps/PM/deliverable/file/views.py
    ↓
FeishuFileManager.upload_file_to_temp()
    ├── 判断文件大小
    ├── < 15MB：file_upload()
    └── >= 15MB：_upload_large_file()
        ├── file_split_upload_prepare()
        ├── file_split_upload_part() (循环)
        └── file_split_upload_finish() (带重试)
    ↓
返回 file_token
    ↓
创建 DeliverableFile 模型
```

## 配置依赖

### settings.API_FEISHU 配置

```python
API_FEISHU = {
    'robot': {
        'api': {
            'appid': 'cli_xxx',
            'app_secret': 'xxx'
        }
    },
    'folder_token': {
        'folder_root': 'root_token_xxx',
        'temp_file': 'temp_token_xxx'
    }
}
```

### 缓存依赖

本模块依赖 Django cache backend（通常使用 Redis）：
- `feishu:tenant_access_token:v2` - tenant token 缓存
- `feishu:app_access_token:v2` - app token 缓存

## 错误处理

### 统一错误处理策略

所有管理器的方法在失败时：
1. 记录错误日志（`logger.error()`）
2. 返回 `None`、`False` 或空字典
3. 不抛出异常（由调用方处理）

### 日志示例

```python
logger.error(f"飞书 send_template_message 失败: {response}")
logger.error(f"飞书 exchange_code 网络请求错误: {e}")
logger.error(f"飞书 get_user_info 异常: {e}")
```

## 禁止事项

### ❌ 禁止直接调用飞书 API

所有飞书 API 调用必须通过对应的管理器，禁止在业务代码中直接使用 `requests` 调用飞书 API。

### ❌ 禁止绕过 Token 管理器

禁止手动构建 Authorization header，必须使用 `FeishuTokenManager` 获取 token。

### ❌ 禁止在业务逻辑中处理 Token 刷新

Token 刷新逻辑由 `FeishuTokenManager` 自动处理，业务代码不应关心 token 过期和刷新。

## 特有名词索引

当以下名词出现时，应关联到此模块：

| 名词 | 说明 |
|------|------|
| **FeishuTokenManager** | 飞书 Token 统一管理器 |
| **FeishuAuthManager** | 飞书认证管理器 |
| **FeishuUserManager** | 飞书用户管理器 |
| **FeishuMessageManager** | 飞书消息管理器 |
| **FeishuFileManager** | 飞书文件管理器 |
| **FeishuSheetManager** | 飞书表格管理器 |
| **tenant_access_token** | 机器人 token |
| **user_access_token** | 用户 token |
| **app_access_token** | 应用 token |
| **exchange_code** | 授权码换 token |
| **refresh_access_token** | 刷新访问令牌 |
| **send_template_message** | 发送模板消息 |
| **batch_send_message** | 批量发送消息 |
| **file_upload** | 文件上传 |
| **upload_file_to_temp** | 上传到临时文件夹 |
| **move_file_with_retry** | 带重试的文件移动 |
| 🆕 **permissions_get_members_list** | 🆕 获取文件权限成员列表 |
| 🆕 **permissions_add** | 🆕 添加文件权限成员 |
| 🆕 **permissions_delete_members** | 🆕 删除文件权限成员 |
| 🆕 **飞书权限管理** | 🆕 飞书文件权限的增删查操作 |

## 相关技能

- **sm-user**：SM 用户模块（User, UserFeishu 模型）
- **sm-messages**：SM 消息模块（Message, Message_Feishu 模型）
- **sm-auth**：SM 认证模块（登录流程）
- **pm-deliverable_file**：PM 交付物文件模块（文件上传业务）
- **pm-deliverable_instance**：🆕 PM 交付物实例模块（飞书权限验证器）
- **user-token-management**：PMS 用户认证与飞书 Token 管理