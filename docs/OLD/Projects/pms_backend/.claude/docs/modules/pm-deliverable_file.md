# PM 交付物文件模块 (DeliverableFile) 技能文档

## 模块定位

`pm-deliverable_file` 是 PM 项目管理系统中负责**交付物文件上传、临时存储与模板创建**的核心模块，采用**职责分离架构**设计。

### 核心定位

1. **文件上传层**：仅负责文件上传核心业务，不处理业务逻辑
2. **临时存储管理**：文件上传后存储到临时目录，等待后续处理
3. **存储服务商抽象**：支持多种存储服务商（飞书云文档、阿里云OSS等）
4. **元数据管理**：管理交付物文件的通用元数据（名称、大小、类型等）
5. **🆕 模板创建**：基于飞书模板快速创建交付物文件

### 架构原则

**🆕 职责分离设计**（Since 2026-03-06 重构）：

| 模块 | 职责 | 边界 |
|------|------|------|
| `pm-deliverable_file` | **文件上传层**：文件接收、元数据提取、临时存储、模板创建 | 返回 `file_id` 后任务结束 |
| `pm-deliverable_instance` | **业务逻辑层**：同步到飞书、写入实例、节点关联 | 使用 `file_id` 继续处理 |

### 与相关模块的边界

| 模块 | 职责边界 | 关联关系 |
|------|---------|---------|
| `pm-deliverable_file` | **文件上传层**：管理文件上传和临时存储 | 返回 `file_id` |
| `pm-deliverable_instance` | **业务逻辑层**：管理交付物的业务属性（所属节点、定义、状态等） | 使用 `file_id` 创建实例 |
| `pm-deliverable_folder` | **文件夹管理**：管理存储服务商中的文件夹层级结构 | 同步到飞书时需要目标文件夹 |
| `pm-nodelist` | **节点管理**：交付物归属于项目节点 | 通过 `deliverable_instance` 关联 |
| `psc-deliverable_definition_template` | **模板管理**：交付物定义模板配置 | 模板创建时读取 |

## 核心数据模型

### 模型架构设计

模块采用**主表+子表**模式：

```
DeliverableFile (主表: 通用文件元数据)
    ↓ OneToOne
DeliverableFileFeishu (子表: 飞书特有字段)
```

**设计优势**：
- ✅ 支持多存储服务商扩展（添加新服务商只需新建子表）
- ✅ 通用字段集中管理（避免冗余）
- ✅ 服务商特有字段隔离（如飞书的 `token`、阿里云的 `oss_key`）

### DeliverableFile（主表）

**表名**：`PM_deliverable_file`

**核心字段**：

| 字段名 | 类型 | 说明 | 变更 |
|--------|------|------|------|
| `id` | BigAutoField | 主键 | - |
| `name` | CharField(255) | 文件名称 | - |
| `size` | CharField(255) | 文件大小（可读格式） | - |
| `category` | CharField(255) | 文件类型（document/sheet/image等） | - |
| `storage_provider` | CharField(50) | **存储服务商标识**（feishu/aliyun_oss） | - |
| `temp_path` | CharField(500) | **临时文件路径** | 🆕 新增 |
| `temp_token` | CharField(255) | **临时访问令牌**（UUID） | 🆕 新增 |
| `is_temp` | BooleanField | **是否为临时文件**（默认True） | 🆕 新增 |
| `created_at` | DateTimeField | 创建时间 | - |
| `updated_at` | DateTimeField | 更新时间 | - |

**枚举值**（`storage_provider`）：
```python
class StorageProvider(models.TextChoices):
    FEISHU = 'FEISHU', '飞书云文档'
    ALIYUN_OSS = 'ALIYUN_OSS', '阿里云 OSS'
```

**索引**：
- `storage_provider` 字段索引（支持按服务商查询）

### DeliverableFileFeishu（飞书子表）

**表名**：`PM_deliverable_file_feishu`

**核心字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | AutoField | 主键 |
| `file` | OneToOneField | 关联 `DeliverableFile` 主表 |
| `token` | CharField(255) | **飞书文件唯一标识**（初始为空，同步后更新） |

**约束**：
- `token` 字段唯一索引（确保飞书文件唯一性）
- `file` 一对一关联（主表删除时级联删除子表）

## API接口

### 文件上传接口

**🆕 精简版接口**（Since 2026-03-06 重构）

**端点**：`POST /pm/deliverable/file/upload`

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | 是 | 上传的文件 |
| `storage_provider` | String | 否 | 存储服务商（默认feishu） |

**返回**：

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "insertId": 123
  }
}
```

**变更说明**：
- ⚠️ **已删除**：`node_id`、`attach_rule_id`、`type`、`document` 等业务字段
- ⚠️ **已删除**：link 和 template 相关逻辑
- ✅ **新增**：`storage_provider` 字段支持
- ✅ **简化**：返回值只包含 `insertId`

### 🆕 模板创建接口

**端点**：`POST /pm/deliverable/file/template/create`

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `nodeId` | Integer | 是 | 节点ID（camelCase规范） |
| `deliverableDefinitionVersionId` | Integer | 是 | 交付物定义版本ID（camelCase规范） |

**返回**：

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "insertId": 123
  }
}
```

**功能说明**：
- 🆕 基于飞书模板快速创建交付物文件
- 🆕 自动检查并创建目录（客户编码→机型编码→交付物目录）
- 🆕 文件名从交付物定义自动获取
- 🆕 通过节点获取项目信息（`node.list.id`）

**变更说明**：
- ✅ **新增**：模板创建能力（Since 2026-03-07）
- ✅ **优化**：使用 `PrimaryKeyRelatedField` 自动验证对象存在性
- ✅ **优化**：字段名遵循 camelCase 规范

## 业务流程

### 文件上传流程（🆕 职责分离架构）

```
1. 客户端上传文件
   ↓
2. FileUploadSerializer 验证文件
   ├─ 验证文件存在性
   └─ 验证文件名长度（≤100字符）
   ↓
3. 提取文件元数据
   ├─ 文件大小（转换为可读格式）
   ├─ 文件类型（根据扩展名判断）
   └─ 版本号（从文件名提取）
   ↓
4. 保存到临时目录（MEDIA_ROOT/temp_deliverable/{temp_token}/）
   ↓
5. 创建 DeliverableFile 记录（is_temp=True）
   ↓
6. 返回 file_id
   ↓
【任务结束 - 职责分离边界】
   ↓
7. [由 deliverable_instance 模块处理]
   ├─ 根据 file_id 获取文件信息
   ├─ 验证项目状态和权限
   ├─ 同步到飞书/阿里云OSS
   ├─ 创建 DeliverableInstance 记录
   ├─ 关联项目节点
   └─ 清理临时文件
```

**关键变更**：
- ⚠️ **已删除**：项目状态验证、权限验证、文件重名检查（移至 `deliverable_instance`）
- ⚠️ **已删除**：`async_upload_deliverable_task` 异步任务（移至 `deliverable_instance`）
- ✅ **新增**：临时目录存储机制（`utils.save_to_temp_directory`）

### 🆕 模板创建流程

```
1. 客户端发起模板创建请求
   ├─ nodeId: 节点ID
   └─ deliverableDefinitionVersionId: 交付物定义版本ID
   ↓
2. FileTemplateCreateSerializer 验证
   ├─ PrimaryKeyRelatedField 自动验证节点存在性
   ├─ PrimaryKeyRelatedField 自动验证版本存在性
   ├─ 验证版本是否关联模板
   └─ 验证模板是否配置飞书信息
   ↓
3. 获取模板配置
   ├─ 从 version.definition_template.feishu_template 获取
   ├─ template_token: 模板文件token
   └─ file_type: 文件类型（docx/sheet等）
   ↓
4. 检查并创建目录
   ├─ 调用 async_ensure_folder_exists(node.list.id, deliverable_definition_code)
   ├─ 创建客户编码目录
   ├─ 创建机型编码目录
   └─ 创建交付物目录
   ↓
5. 复制模板文件
   ├─ 使用 FeishuFileManager.file_copy()
   ├─ 从模板复制到目标文件夹
   └─ 文件名从交付物定义获取（version.deliverable_definition.name）
   ↓
6. 创建文件记录
   ├─ 创建 DeliverableFile 记录（is_temp=False）
   └─ 创建 DeliverableFileFeishu 记录（保存新文件token）
   ↓
7. 返回 insertId
   ↓
【任务结束】
```

**关键特性**：
- ✅ **自动验证**：`PrimaryKeyRelatedField` 自动验证对象存在性
- ✅ **自动命名**：文件名从交付物定义自动获取
- ✅ **自动创建目录**：三层目录结构自动创建
- ✅ **非临时文件**：直接创建正式文件（`is_temp=False`）

### 临时文件管理

**临时目录结构**：

```
MEDIA_ROOT/temp_deliverable/
└── {temp_token}/
    └── {file_name}
```

**清理方法**：

- **自动清理**：`cleanup_expired_temp_files(expiration_hours=24)` 定期清理过期文件
- **手动清理**：`delete_temp_file(temp_token)` 删除指定临时文件

## 核心代码实现

### FileUploadSerializer（🆕 精简版）

```python
# apps/PM/deliverable/file/serializers.py

class FileUploadSerializer(serializers.Serializer):
    """文件上传序列化器 - 仅负责文件上传核心业务"""

    storage_provider = serializers.ChoiceField(
        choices=Choices.StorageProvider.choices,
        default=Choices.StorageProvider.FEISHU,
        required=False
    )

    def validate(self, attrs):
        """验证上传文件"""
        if 'file' not in self.files:
            raise serializers.ValidationError({'上传失败': '请选择要上传的文件'})

        uploaded_file = self.files['file']
        file_name = str(uploaded_file)

        # 验证文件名长度
        if len(file_name) > 100:
            raise serializers.ValidationError({'上传失败': '文件名称不能长于100字符'})

        return attrs

    def create(self, validated_data):
        """创建文件记录"""
        uploaded_file = self.files['file']
        file_name = str(uploaded_file)
        storage_provider = validated_data.get('storage_provider', Choices.StorageProvider.FEISHU)

        # 提取文件元数据
        file_size = self._get_file_size(uploaded_file)
        file_category = self._get_file_category(file_name)

        # 生成临时令牌
        temp_token = self._generate_temp_token()

        # 保存到临时目录
        temp_file_path = save_to_temp_directory(uploaded_file, file_name, temp_token)

        # 创建主表记录
        deliverable_file = DeliverableFile.objects.create(
            name=file_name,
            size=str(file_size),
            category=file_category,
            storage_provider=storage_provider,
            temp_path=temp_file_path,
            temp_token=temp_token,
            is_temp=True  # 标记为临时文件
        )

        # 根据存储服务商创建子表记录
        if storage_provider == Choices.StorageProvider.FEISHU:
            DeliverableFileFeishu.objects.create(
                file=deliverable_file,
                token=''  # 待同步到飞书后更新
            )

        return deliverable_file
```

### 🆕 FileTemplateCreateSerializer

```python
# apps/PM/deliverable/file/serializers.py

class FileTemplateCreateSerializer(serializers.Serializer):
    """文件模板创建序列化器 - 基于飞书模板创建交付物文件"""

    nodeId = serializers.PrimaryKeyRelatedField(
        queryset=Project_Node.objects.all(),
        help_text='节点ID'
    )
    deliverableDefinitionVersionId = serializers.PrimaryKeyRelatedField(
        queryset=DeliverableDefinitionVersion.objects.all(),
        help_text='交付物定义版本ID'
    )

    def validate_deliverableDefinitionVersionId(self, value):
        """验证交付物定义版本是否具有模板"""
        # 检查是否有关联的模板
        if not hasattr(value, 'definition_template') or not value.definition_template:
            raise serializers.ValidationError('该交付物定义未配置模板')

        # 检查模板是否配置飞书信息
        template = value.definition_template
        if not hasattr(template, 'feishu_template') or not template.feishu_template:
            raise serializers.ValidationError('模板未配置飞书信息')

        return value

    def create(self, validated_data):
        """创建交付物文件（基于模板）"""
        node = validated_data['nodeId']
        version = validated_data['deliverableDefinitionVersionId']

        # 文件名从交付物定义中获取
        file_name = version.deliverable_definition.name

        # 获取模板配置
        template = version.definition_template.feishu_template
        template_token = template.token
        file_type = template.category

        # 1. 检查并创建目录（客户编码目录、机型编码目录、交付物目录）
        deliverable_definition_code = version.deliverable_definition.code
        folder = async_ensure_folder_exists(node.list.id, deliverable_definition_code)

        if not folder or not hasattr(folder, 'feishu_storage'):
            raise serializers.ValidationError('项目文件夹创建失败')

        target_folder_token = folder.feishu_storage.folder_token

        # 2. 调用file_manager复制模板文件
        file_manager = FeishuFileManager()
        new_file_token = file_manager.file_copy(
            file_token=template_token,
            name=file_name,
            folder_token=target_folder_token,
            file_type=file_type
        )

        if not new_file_token:
            raise serializers.ValidationError('复制模板文件失败')

        # 3. 创建DeliverableFile记录
        deliverable_file = DeliverableFile.objects.create(
            name=file_name,
            size='0',
            category=file_type,
            storage_provider=Choices.StorageProvider.FEISHU,
            is_temp=False
        )

        # 4. 创建DeliverableFileFeishu记录
        DeliverableFileFeishu.objects.create(
            file=deliverable_file,
            token=new_file_token
        )

        return deliverable_file
```

### 临时目录辅助方法

```python
# apps/PM/deliverable/file/utils.py

def save_to_temp_directory(uploaded_file, file_name, temp_token):
    """将上传的文件保存到临时目录"""
    temp_dir = get_temp_directory()
    token_dir = os.path.join(temp_dir, temp_token)
    os.makedirs(token_dir, exist_ok=True)

    temp_file_path = os.path.join(token_dir, file_name)

    with open(temp_file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return temp_file_path

def delete_temp_file(temp_token):
    """删除临时文件（当文件正式同步后）"""
    import shutil
    temp_dir = get_temp_directory()
    token_dir = os.path.join(temp_dir, temp_token)

    if os.path.exists(token_dir):
        shutil.rmtree(token_dir)

def cleanup_expired_temp_files(expiration_hours=24):
    """清理过期的临时文件"""
    # 定期清理过期文件
    pass
```

## 与其他模块关系

### 依赖关系图

```
pm-deliverable_file (文件上传/模板创建)
    ↓ 返回 file_id
pm-deliverable_instance (业务逻辑)
    ↓ ForeignKey
pm-nodelist (节点管理)
    ↓ ForeignKey
pm-project_list (项目)
    ↑ 通过 node.list.id 获取
psc-deliverable_definition_template (模板配置)
    ↑ 读取模板token
```

### 核心关联

#### 1. 与 `DeliverableInstance` 的关系

```python
# apps/PM/deliverable/instance/models.py

class DeliverableInstance(models.Model):
    file = models.OneToOneField(  # 可选关联
        'PM.DeliverableFile',
        on_delete=models.CASCADE,
        verbose_name='交付物文件',
        related_name='deliverable_instance',
        null=True,
        blank=True
    )

    # 向后兼容的属性
    @property
    def name(self):
        return self.file.name if self.file else None

    @property
    def token(self):
        if self.file and hasattr(self.file, 'feishu'):
            return self.file.feishu.token
        return None
```

**关联特点**：
- ✅ **可选关联**：`null=True` 允许创建无文件的交付物实例（如外部链接）
- ✅ **级联删除**：`on_delete=CASCADE` 删除实例时自动删除文件记录
- ✅ **向后兼容**：通过 `@property` 保持原有 API 不变

#### 2. 🆕 与节点和模板的关系

```python
# 通过节点获取项目
node = validated_data['nodeId']
project_id = node.list.id  # 节点关联项目

# 通过模板获取配置
template = version.definition_template.feishu_template
template_token = template.token
file_type = template.category
```

## 存储服务商扩展

### 新增存储服务商步骤

**1. 创建子表模型**：

```python
# apps/PM/deliverable/file/models.py

class DeliverableFileAliyunOss(models.Model):
    """阿里云 OSS 存储子表"""
    id = models.AutoField(primary_key=True)
    file = models.OneToOneField(
        DeliverableFile,
        on_delete=models.CASCADE,
        related_name='aliyun_oss'
    )
    bucket = models.CharField(max_length=255)
    key = models.CharField(max_length=500)  # OSS 文件路径
    etag = models.CharField(max_length=100)

    class Meta:
        db_table = 'PM_deliverable_file_aliyun_oss'
```

**2. 更新枚举**：

```python
# apps/PM/deliverable/enums.py

class StorageProvider(models.TextChoices):
    FEISHU = 'FEISHU', '飞书云文档'
    ALIYUN_OSS = 'ALIYUN_OSS', '阿里云 OSS'
```

**3. 更新序列化器**：

```python
# apps/PM/deliverable/file/serializers.py

def create(self, validated_data):
    # ...
    # 根据存储服务商创建子表记录
    if storage_provider == Choices.StorageProvider.FEISHU:
        DeliverableFileFeishu.objects.create(...)
    elif storage_provider == Choices.StorageProvider.ALIYUN_OSS:
        DeliverableFileAliyunOss.objects.create(...)
```

## 文件类型映射

```python
category_map = {
    # 文档
    'doc': 'document', 'docx': 'document', 'pdf': 'document', 'txt': 'document',
    'xls': 'sheet', 'xlsx': 'sheet', 'csv': 'sheet',
    'ppt': 'bitable', 'pptx': 'bitable',
    # 图片
    'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'bmp': 'image',
    # 视频
    'mp4': 'video', 'avi': 'video', 'mov': 'video', 'mkv': 'video',
    # 压缩包
    'zip': 'archive', 'rar': 'archive', '7z': 'archive',
    # 其他
    'dxf': 'dxf', 'step': 'step', 'stp': 'step',
}
```

## 常见业务场景

### 场景1：用户上传本地文件（🆕 精简版）

**流程**：

```
用户选择文件
    ↓
前端发起 POST /pm/deliverable/file/upload
    ↓
DeliverableFileUploadView.post()
    ↓
FileUploadSerializer.validate()
    ├─ 验证文件存在性
    └─ 验证文件名长度（≤100字符）
    ↓
FileUploadSerializer.create()
    ├─ 提取文件元数据（大小、类型、版本）
    ├─ 生成临时令牌（UUID）
    ├─ 保存到临时目录
    ├─ 创建 DeliverableFile 记录（is_temp=True）
    └─ 创建存储服务商子表记录
    ↓
返回 insertId
    ↓
【任务结束】
```

**关键代码片段**：

```python
# apps/PM/deliverable/file/serializers.py:56-95

def create(self, validated_data):
    uploaded_file = self.files['file']
    file_name = str(uploaded_file)
    storage_provider = validated_data.get('storage_provider', Choices.StorageProvider.FEISHU)

    # 提取文件元数据
    file_size = self._get_file_size(uploaded_file)
    file_category = self._get_file_category(file_name)

    # 生成临时令牌
    temp_token = self._generate_temp_token()

    # 保存到临时目录
    temp_file_path = save_to_temp_directory(uploaded_file, file_name, temp_token)

    # 创建主表记录
    deliverable_file = DeliverableFile.objects.create(
        name=file_name,
        size=str(file_size),
        category=file_category,
        storage_provider=storage_provider,
        temp_path=temp_file_path,
        temp_token=temp_token,
        is_temp=True
    )

    return deliverable_file
```

### 场景2：🆕 基于模板创建交付物文件

**流程**：

```
用户选择模板
    ↓
前端发起 POST /pm/deliverable/file/template/create
    ├─ nodeId: 节点ID
    └─ deliverableDefinitionVersionId: 交付物定义版本ID
    ↓
DeliverableFileTemplateCreateView.post()
    ↓
FileTemplateCreateSerializer.validate()
    ├─ PrimaryKeyRelatedField 自动验证节点存在
    ├─ PrimaryKeyRelatedField 自动验证版本存在
    └─ validate_deliverableDefinitionVersionId() 验证模板配置
    ↓
FileTemplateCreateSerializer.create()
    ├─ 获取节点项目（node.list.id）
    ├─ 获取模板配置（template.token, template.category）
    ├─ 获取文件名（version.deliverable_definition.name）
    ├─ 检查并创建目录结构
    ├─ 复制模板文件到目标目录
    ├─ 创建 DeliverableFile 记录（is_temp=False）
    └─ 创建 DeliverableFileFeishu 记录
    ↓
返回 insertId
    ↓
【任务结束】
```

**关键代码片段**：

```python
# apps/PM/deliverable/file/serializers.py:144-252

def create(self, validated_data):
    node = validated_data['nodeId']
    version = validated_data['deliverableDefinitionVersionId']

    # 文件名从交付物定义中获取
    file_name = version.deliverable_definition.name

    # 获取模板配置
    template = version.definition_template.feishu_template
    template_token = template.token
    file_type = template.category

    # 检查并创建目录
    folder = async_ensure_folder_exists(node.list.id, deliverable_definition_code)

    # 复制模板文件
    new_file_token = file_manager.file_copy(
        file_token=template_token,
        name=file_name,
        folder_token=target_folder_token,
        file_type=file_type
    )

    # 创建文件记录
    deliverable_file = DeliverableFile.objects.create(
        name=file_name,
        size='0',
        category=file_type,
        storage_provider=Choices.StorageProvider.FEISHU,
        is_temp=False
    )

    return deliverable_file
```

### 场景3：后续业务处理（由 deliverable_instance 模块实现）

```python
# apps/PM/deliverable/instance/services.py

class DeliverableService:
    @staticmethod
    def create_deliverable_from_file(file_id, project_id, node_id, rule_id):
        """根据 file_id 创建交付物实例"""
        # 1. 获取文件信息
        deliverable_file = DeliverableFile.objects.get(id=file_id)

        # 2. 验证项目状态和权限
        # 3. 同步到飞书
        # 4. 创建 DeliverableInstance 记录
        # 5. 清理临时文件
```

## 模块特有名词速查

| 名词 | 说明 | 定位 |
|------|------|------|
| `DeliverableFile` | 交付物文件主表，存储通用元数据 | 数据模型 |
| `DeliverableFileFeishu` | 飞书存储子表，存储飞书特有字段 | 数据模型 |
| `storage_provider` | 存储服务商标识字段 | 枚举值 |
| `temp_token` | 临时文件标识（UUID格式） | 🆕 新增 |
| `temp_path` | 临时文件路径 | 🆕 新增 |
| `is_temp` | 是否为临时文件标记 | 🆕 新增 |
| `insertId` | 文件创建成功后返回的ID | 返回值 |
| `save_to_temp_directory` | 保存文件到临时目录方法 | 🆕 新增 |
| `FileUploadSerializer` | 文件上传序列化器（精简版） | 🆕 重命名 |
| `FileTemplateCreateSerializer` | 🆕 模板创建序列化器 | 新增 |
| `nodeId` | 🆕 节点ID（camelCase规范） | 请求参数 |
| `deliverableDefinitionVersionId` | 🆕 交付物定义版本ID（camelCase规范） | 请求参数 |

## 已废弃设计（Deprecated）

| 旧设计 | 废弃原因 | 替代方案 |
|--------|---------|---------|
| `UploadDeliverableSerializer` | 包含业务逻辑，违反职责分离 | `FileUploadSerializer` + `deliverable_instance` |
| `_create_link()` | link功能移至 `deliverable_instance` | `deliverable_instance` 模块 |
| `_create_template()` | 旧模板功能移至 `deliverable_instance` | 🆕 `FileTemplateCreateSerializer` |
| `async_upload_deliverable_task` | 异步上传移至 `deliverable_instance` | `deliverable_instance` 模块 |
| `validate_upload_permission()` | 权限验证移至 `deliverable_instance` | `deliverable_instance` 模块 |
| `project_id` | 参数命名不符合camelCase规范 | 🆕 `nodeId` |
| `name` 参数 | 🆕 模板创建时文件名应从定义获取 | 🆕 自动获取 |


**文档版本**：v3.0
**最后更新**：2026-03-07
**维护者**：Claude Code (pm-deliverable_file 模块专家)
**重大变更**：
- v2.0 (2026-03-06): 职责分离重构，仅负责文件上传核心业务
- v3.0 (2026-03-07): 新增模板创建功能，使用节点ID替代项目ID，遵循camelCase规范