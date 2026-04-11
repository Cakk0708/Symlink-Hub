# PSC 交付物定义模板模块

## 模块定位

本模块位于 `apps/PSC/deliverable/template/`，是 PSC（项目设置配置）模块的子模块，负责管理交付物定义的飞书模板配置。

**核心价值**：通过预配置的飞书文档/表格模板，规范项目交付物的创建格式，提升协作效率。


## 模块职责边界

### 职责范围
- **飞书模板验证**：验证用户提供的飞书文档/表格 Token 是否有效
- **模板记录管理**：创建和存储模板配置信息
- **版本关联**：将模板与交付物定义版本（DeliverableDefinitionVersion）关联

### 不负责
- 交付物实例的创建（由 PM/deliverable/instance 负责）
- 飞书文档的复制操作（由 PM/deliverable/folder 的存储服务负责）
- 文件上传处理（由 PM/deliverable/file 负责）


## 核心数据模型

### 模型关系图

```
DeliverableDefinition (交付物定义)
    │
    └── versions (OneToMany) → DeliverableDefinitionVersion (交付物定义版本)
                                    │
                                    └── definition_template (OneToOne) → DeliverableDefinitionTemplate (模板)
                                                                                │
                                                                                └── feishu_templates (OneToOne) → DeliverableDefinitionTemplateFeishu (飞书配置)
```

### 1. DeliverableDefinitionTemplate
**文件位置**：`apps/PSC/deliverable/template/models.py:11-42`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | AutoField | 主键 |
| `name` | CharField(255) | 模板名称（存储飞书文档标题） |
| `storage_provider` | CharField(50) | 存储服务商（feishu/aliyun_oss） |
| `definition_version` | OneToOneField | 关联的交付物定义版本 |

### 2. DeliverableDefinitionTemplateFeishu
**文件位置**：`apps/PSC/deliverable/template/models.py:45-73`

| 字段 | 类型 | 说明 |
|------|------|------|
| `template` | OneToOneField | 关联的模板（主键所在） |
| `token` | CharField(255) | 飞书文档 Token（唯一） |
| `category` | CharField(50) | 飞书文档分类（document/sheet） |


## 业务流程

### 创建交付物定义时附带飞书模板

```
用户请求 (POST /psc/deliverable/definition/)
    │
    ├─> WriteSerializer.create()
    │       │
    │       ├─> 创建 DeliverableDefinition
    │       │
    │       ├─> 创建 DeliverableDefinitionVersion (第一个版本)
    │       │
    │       └─> 如果提供了 feishuTemplate
    │               │
    │               ├─> FeishuTemplateSerializer.validate()
    │               │       │
    │               │       └─> FeishuSheetManager.get_spreadsheet_information()
    │               │               └─> 验证 Token 并获取标题
    │               │
    │               └─> _create_feishu_template()
    │                       │
    │                       ├─> 创建 DeliverableDefinitionTemplate
    │                       │
    │                       └─> 创建 DeliverableDefinitionTemplateFeishu
```


## API 接口

### 创建交付物定义（附带飞书模板）

**请求示例**：
```json
POST /psc/deliverable/definition/

{
  "name": "技术规格书",
  "description": "项目技术规格说明文档模板",
  "isRequired": true,
  "isReview": true,
  "allowedFileExtensionsIds": [1, 2],
  "feishuTemplate": {
    "category": "sheet",
    "token": "L0uBsnjdIh4ORstP6OgcBXXVnvc"
  }
}
```

**响应示例**：
```json
{
  "id": 1,
  "document": {
    "code": "DELIV0001",
    "name": "技术规格书",
    "isActive": true
  },
  "versionData": {
    "items": [
      {
        "id": 1,
        "template": {
          "id": 1,
          "name": "技术规格书模板（从飞书获取的标题）"
        },
        "allowedFileExtensions": [
          {"id": 1, "name": ".pdf"},
          {"id": 2, "name": ".docx"}
        ]
      }
    ],
    "count": 1
  }
}
```


## 枚举定义

### 存储服务商 (StorageProvider)
**文件位置**：`apps/PSC/deliverable/template/enums.py:5-8`

| 值 | 标签 |
|---|---|
| `feishu` | 飞书云文档 |
| `aliyun_oss` | 阿里云 OSS |

### 飞书文档分类 (Category)
**文件位置**：`apps/PSC/deliverable/template/enums.py:11-14`

| 值 | 标签 |
|---|---|
| `document` | 文档 |
| `sheet` | 表格 |


## 序列化器说明

### 1. FeishuTemplateSerializer
**文件位置**：`apps/PSC/deliverable/template/serializers.py:14-55`

**职责**：验证飞书模板参数

- `category`: 必填，选择文档类型
- `token`: 必填，飞书文档 Token

**验证逻辑**：
1. 获取租户访问令牌（`FeishuTokenManager.get_tenant_token()`）
2. 调用飞书 API 验证 Token（`FeishuSheetManager.get_spreadsheet_information()`）
3. 获取文档标题作为模板名称

### 2. TemplateSimpleSerializer
**文件位置**：`apps/PSC/deliverable/template/serializers.py:58-66`

**职责**：简化输出模板信息（用于版本详情）


## 与其他模块关系

### 依赖模块
| 模块 | 依赖关系 | 说明 |
|------|----------|------|
| `PSC/deliverable/definition` | 被依赖 | 定义版本通过 `definition_template` 关联模板 |
| `utils/openapi/feishu` | 依赖 | 使用飞书 SDK 进行 Token 验证 |

### 关联模块
| 模块 | 关联方式 | 未来协作点 |
|------|----------|------------|
| `PM/deliverable/instance` | 间接使用 | 交付物实例创建时根据模板复制飞书文档 |
| `PM/deliverable/folder` | 间接使用 | 文件夹模块的存储服务可使用模板信息 |


## 常见业务场景

### 场景1：创建带飞书表格模板的交付物定义
用户希望项目创建时自动生成标准的《项目进度表》。

**操作流程**：
1. 在飞书中创建标准表格模板
2. 调用创建交付物定义接口，传入表格 Token
3. 系统验证 Token 并保存模板配置
4. 后续创建交付物实例时，系统根据模板复制表格

### 场景2：更新交付物定义时更换模板
用户需要更新《技术规格书》的模板格式。

**操作流程**：
1. PUT 请求交付物定义接口，传入新的 `feishuTemplate`
2. 系统创建新版本并关联新模板
3. 旧版本的模板保持不变（版本追溯）


## 技术实现建议

### 1. 飞书 API 调用
- 使用 `FeishuTokenManager` 管理租户令牌
- 使用 `FeishuSheetManager.get_spreadsheet_information()` 验证表格
- 注意处理 API 调用失败的情况

### 2. 数据一致性
- 模板与版本是 OneToOne 关系，一个版本只能有一个模板
- 更新交付物定义时，新版本可以创建新模板，旧版本保持不变

### 3. 错误处理
```python
if not sheet_data:
    raise serializers.ValidationError({
        'token': '无法获取飞书表格信息，请检查 token 是否正确'
    })
```


## 扩展设计策略

### 短期（已完成）
- [x] 飞书表格验证
- [x] 模板与版本关联
- [x] 创建时附带模板

### 中期
- [ ] 飞书文档类型验证（当前只有表格）
- [ ] 模板预览功能（返回飞书文档预览链接）
- [ ] 模板复用（多个定义版本可使用同一模板）

### 长期
- [ ] 支持阿里云 OSS 模板
- [ ] 模板版本管理
- [ ] 模板权限控制（谁可以使用该模板）


## 演进方向 (Future Evolution)

### 1. 文档类型支持
当前仅支持飞书表格（sheet）验证，需要补充文档（document）类型的 API 调用：

```python
elif category == Choices.Category.DOCUMENT:
    # TODO: 实现文档信息获取
    document_data = document_manager.get_document_information(token)
    title = document_data.get('title', '')
```

### 2. 模板市场
建立企业级模板库，支持：
- 模板分类管理
- 模板评分与推荐
- 跨项目模板共享

### 3. 动态模板
支持基于规则自动生成模板：
- 根据项目类型自动选择模板
- 根据节点配置动态调整模板字段


## 关键名词索引

当在对话中出现以下名词时，应关联到此技能：

| 名词 | 说明 |
|------|------|
| `feishuTemplate` | 创建/更新交付物定义时的飞书模板参数 |
| `DeliverableDefinitionTemplate` | 交付物定义模板模型 |
| `DeliverableDefinitionTemplateFeishu` | 飞书模板配置模型 |
| `definition_template` | 版本与模板的反向关联字段 |
| `FeishuTemplateSerializer` | 飞书模板验证序列化器 |
| `TemplateSimpleSerializer` | 模板简化输出序列化器 |
