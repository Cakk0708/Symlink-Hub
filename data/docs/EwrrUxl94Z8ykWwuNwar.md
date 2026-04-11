# PM交付物定义模块 (DeliverableDefinition)

## 模块定位

交付物定义模块是项目配置(PSC)子系统的核心模块之一，负责定义和管理项目各阶段需要提交的交付物模板。该模块与项目模板、节点定义、评审定义等模块紧密协作，构成完整的项目管理体系。

**核心价值**：
- 标准化项目交付物的格式和要求
- 支持交付物版本管理和历史追溯
- 集成飞书文档模板，提升协作效率
- 提供灵活的文件类型校验机制

## 模块职责边界

### 核心职责
1. **交付物模板管理**：创建、编辑、删除、启用/禁用交付物定义
2. **版本控制**：维护交付物定义的版本历史，支持版本切换和对比
3. **文件类型管理**：定义可接受的文件扩展名类型，支持动态扩展
4. **飞书集成**：配置飞书文档/表格/多维表格作为交付物预设模板
5. **权限控制**：基于用户角色的操作权限验证

### 边界界定
- **属于本模块**：
  - 交付物定义的CRUD操作
  - 交付物版本列表的展示和管理
  - 文件类型的定义和扩展
  - 飞书模板链接的解析和存储
  - 交付物的启用/禁用状态管理

- **不属于本模块**：
  - 交付物的实际文件上传（由文件服务处理）
  - 交付物与项目节点的关联（由项目模板模块处理）
  - 交付物的审批流程（由评审定义模块处理）

## 核心数据模型

### DeliverableDefinition (交付物定义)
```typescript
{
  id: number;                    // 交付物定义ID
  code: string;                  // 编码（系统自动生成，只读）
  name: string;                  // 交付物名称（必填）
  isActive: boolean;             // 是否启用
  displayVersion: string;        // 版本号（如：v1.0、v2.0）
  isLinkFirst: boolean;          // 是否链接优先
  isRequired: boolean;           // 是否必填
  remark: string;                // 说明
  feishuTemplate: {              // 飞书模板配置
    url?: string;                // 完整链接（后端返回）
    originalUrl?: string;        // 原始粘贴链接（前端存储）
    token: string;               // 飞书文档token
    category: string;            // 类型：doc/docx/sheet/doc/bitable
  };
  allowedFileExtensionsIds: number[]; // 允许的文件类型ID列表
  allowedFileExtensions: FileExtension[]; // 文件类型详情
  createdAt: string;             // 创建时间
  updatedAt: string;             // 更新时间
  currentCreatedByNickname: string; // 创建者昵称
}
```

### FileExtension (文件类型扩展)
```typescript
{
  id: number;                    // 文件类型ID
  name: string;                  // 类型名称（如：pdf、docx、xlsx）
}
```

### VersionData (版本数据)
```typescript
{
  items: Array<{
    id: number;
    displayVersion: string;      // 版本号
    remark: string;              // 版本说明
    isCurrent: boolean;          // 是否当前版本
    isRequired: boolean;         // 是否必填
    isLinkFirst: boolean;        // 是否链接优先
    allowedFileExtensions: FileExtension[];
    template?: {                 // 飞书模板信息
      name: string;
      token: string;
      category: string;
    };
    createdBy: string;           // 创建者
    createdAt: string;           // 创建时间
  }>;
}
```

## API规范文档

### 基础路径
```
psc/deliverable/definitions
```

### 接口列表

#### 1. 查询交付物定义列表
```typescript
GET psc/deliverable/definitions
Query Params:
  code?: string;                 // 交付物模板编号（模糊搜索）
  currentName?: string;          // 交付物名称（模糊搜索）
  pageNum?: number;              // 页码，默认1
  pageSize?: number;             // 每页条数，默认10
  pageSort?: string;             // 排序，格式："FIELD:ORDER"（如：ID:DESC）

Response:
{
  data: {
    items: DeliverableDefinition[];
    pagination: {
      total: number;
    };
  };
}
```

#### 2. 查询交付物定义详情
```typescript
GET psc/deliverable/definitions/{id}

Response:
{
  data: {
    id: number;
    document: {
      code: string;
      name: string;
      isActive: boolean;
    };
    others: any;                 // 其他信息
    versionData: {
      items: VersionItem[];
    };
  };
}
```

#### 3. 新增交付物定义
```typescript
POST psc/deliverable/definitions
Body:
{
  name: string;                  // 必填
  displayVersion?: string;       // 版本号
  isLinkFirst?: boolean;         // 是否链接优先
  isRequired?: boolean;          // 是否必填
  remark?: string;               // 说明
  feishuTemplate?: {             // 飞书模板
    token: string;
    category: string;
    originalUrl?: string;
  };
  allowedFileExtensionsIds?: number[]; // 文件类型ID数组
}

Response:
{
  data: {
    insertId: number;            // 新增的交付物定义ID
  };
}
```

#### 4. 修改交付物定义
```typescript
PUT psc/deliverable/definitions/{id}
Body:
{
  displayVersion?: string;
  isLinkFirst?: boolean;
  isRequired?: boolean;
  remark?: string;
  feishuTemplate?: {
    token?: string;
    category?: string;
    url?: string;
  };
  allowedFileExtensionsIds?: number[];
}

Response: Success
```

#### 5. 删除交付物定义
```typescript
DELETE psc/deliverable/definitions
Body:
{
  ids: number[];                 // 要删除的ID数组
}

Response: Success
```

#### 6. 启用/禁用交付物定义
```typescript
PATCH psc/deliverable/definitions
Body:
{
  ids: number[];
  isActive: boolean;             // true=启用，false=禁用
}

Response: Success
```

#### 7. 获取枚举值
```typescript
GET psc/deliverable/definitions/enums

Response:
{
  data: {
    choices: {
      disable_flag: Array<{
        value: boolean;
        label: string;
      }>;
    };
  };
}
```

#### 8. 获取简单列表（用于下拉选择）
```typescript
GET psc/deliverable/definitions/simple
Query Params:
  (同列表接口)

Response: (同列表接口)
```

#### 9. 获取文件类型扩展列表
```typescript
GET psc/deliverable/file-extension-type

Response:
{
  data: FileExtension[];
}
```

#### 10. 新增文件类型扩展
```typescript
POST psc/deliverable/file-extension-type
Body:
{
  name: string;                  // 文件类型名称（如：pdf、docx）
}

Response:
{
  data: {
    insertId: number;
    name: string;
  };
}
```

## 权限验证流程

### 权限点定义
```javascript
// 前端权限验证
'PSC.add_definitions'        // 新增权限
'PSC.change_definitions'     // 修改权限
'PSC.delete_definitions'     // 删除权限
'PSC.view_definitions'       // 查看权限
```

### 权限验证实现
```javascript
import { validatePerm } from '@/utils';

// 在操作前验证权限
const handleUpdate = (row) => {
  const isEdit = validatePerm('PSC.change_definitions');
  router.push({
    path: `deliverabledefinition/edit/${row.id}/${isEdit ? 'edit' : 'view'}`
  });
};
```

### 操作权限矩阵
| 操作 | 所需权限 | 说明 |
|------|----------|------|
| 查看列表 | PSC.view_definitions | 基础查看权限 |
| 新增 | PSC.add_definitions | 创建新的交付物定义 |
| 编辑 | PSC.change_definitions | 修改现有定义 |
| 删除 | PSC.delete_definitions | 删除定义 |
| 复制 | PSC.add_definitions | 复制现有定义创建新版本 |
| 启用/禁用 | PSC.change_definitions | 修改isActive状态 |

## 与其他模块关系

### 依赖关系图
```
┌─────────────────────┐
│   项目模板模块       │
│ (ProjectTemplate)   │
└──────────┬──────────┘
           │ 引用
           ↓
┌─────────────────────┐
│  交付物定义模块      │ ◄──── 本模块
│ (DeliverableDefinition)│
└──────────┬──────────┘
           │ 配置
           ↓
┌─────────────────────┐
│   文件类型扩展       │
│ (FileExtension)     │
└─────────────────────┘
           │ 集成
           ↓
┌─────────────────────┐
│   飞书文档服务       │
│ (Feishu Template)   │
└─────────────────────┘
```

### 关联说明
1. **与项目模板的关系**：项目模板可以引用多个交付物定义，定义项目各阶段的交付要求
2. **与节点定义的关系**：项目节点可以配置需要提交的交付物清单
3. **与评审定义的关系**：评审节点可以要求提交特定交付物作为评审依据
4. **与文件服务的关系**：实际交付的文件存储在文件服务中，本模块仅定义模板

## 常见业务场景

### 场景1：创建新的交付物定义
```javascript
// 1. 点击新增按钮，跳转到新增页面
router.push({ path: "deliverabledefinition/add" });

// 2. 填写基础信息
{
  name: "技术方案文档",
  displayVersion: "v1.0",
  isRequired: true,
  isLinkFirst: false,
  remark: "项目启动后必须提交的技术方案"
}

// 3. 配置允许的文件类型
allowedFileExtensionsIds: [1, 2, 3] // pdf, docx, xlsx

// 4. 配置飞书模板（可选）
feishuTemplate: {
  token: "xxxxx",
  category: "doc",
  originalUrl: "https://xxx.feishu.cn/doc/xxxxx"
}

// 5. 提交保存
addDefinitions(data).then(res => {
  // 保存成功后跳转到编辑页面
  router.replace({
    path: `/psc/deliverabledefinition/edit/${res.data.insertId}/edit`
  });
});
```

### 场景2：复制现有交付物定义
```javascript
// 1. 在列表页选中一个定义，点击复制
handleCopy() {
  router.push({ path: `deliverabledefinition/add/${ids.value[0]}` });
}

// 2. 新增页面会加载源数据，但生成新的编码
const initData = async () => {
  if (route.params.addId) {
    let response = await getDefinitionsById(route.params.addId);
    // 加载数据但不清空code，后端会生成新编码
  }
};
```

### 场景3：管理文件类型
```javascript
// 1. 选择文件类型时，如果输入新类型名称
const handleFileTypeChange = async (value) => {
  const last = value[value.length - 1];
  const exists = fileTypeOptions.value.some(item => item.value === last);

  if (!exists) {
    // 2. 自动创建新的文件类型
    const res = await addDefinitionsExtend({ name: last });

    // 3. 更新选项列表
    fileTypeOptions.value.push({
      label: res.data.name,
      value: res.data.insertId
    });
  }
};
```

### 场景4：飞书模板链接解析
```javascript
// 正则表达式解析飞书链接
const FEISHU_URL_REG = /^https:\/\/[A-Za-z0-9]+\.feishu\.cn\/([A-Za-z0-9]+)\/([A-Za-z0-9]+)/;

const parseFeishuLink = (url) => {
  const match = url.match(FEISHU_URL_REG);
  if (!match) return null;

  let category = match[1]; // doc/docx/sheet等
  const token = match[2];   // 文档token

  // 统一sheets为sheet
  if (category === "sheets") {
    category = "sheet";
  }

  return { category, token };
};

// 粘贴时自动解析
const handleFeishuPaste = (e) => {
  const text = e.clipboardData?.getData("text");
  const parsed = parseFeishuLink(text);

  if (parsed) {
    props.formData.feishuTemplate = {
      ...parsed,
      originalUrl: text
    };
  }
};
```

## 技术实现建议

### 前端实现要点

#### 1. 页面结构
```
deliverabledefinition/
├── index.vue        # 列表页
├── add.vue          # 新增页（使用deliverRender组件）
├── edit.vue         # 编辑页（使用deliverRender组件）
└── components/
    └── deliverRender.vue  # 表单渲染组件（复用）
```

#### 2. 表单验证规则
```javascript
const rules = {
  name: [{ required: true, message: "名称不能为空", trigger: "blur" }],
  displayVersion: [{ required: true, message: "版本号不能为空", trigger: "blur" }]
};
```

#### 3. 数据处理注意事项
- **编码处理**：新增时不需要填写code，后端自动生成；编辑时code只读
- **状态显示**：列表中isActive需要取反显示（!item.isActive）
- **飞书模板同步**：需要watch feishuTemplate字段，同步更新输入框显示
- **文件类型转换**：提交时需要将ID数组转换为后端期望格式

#### 4. 版本列表展示
```html
<el-table :data="versionTableData" border>
  <el-table-column prop="displayVersion" label="版本号" />
  <el-table-column prop="remark" label="说明" />
  <el-table-column prop="isCurrent" label="当前版本">
    <template #default="{ row }">
      {{ row.isCurrent ? '是' : '否' }}
    </template>
  </el-table-column>
</el-table>
```

### 后端实现要点（Django）

#### 1. 模型设计建议
```python
class DeliverableDefinition(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    # 使用JSONField存储版本信息
    version_data = models.JSONField(default=dict)

class FileExtension(models.Model):
    name = models.CharField(max_length=20, unique=True)
```

#### 2. 序列化器建议
```python
class DeliverableDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverableDefinition
        fields = [
            'id', 'code', 'name', 'is_active',
            'display_version', 'is_link_first',
            'is_required', 'remark', 'feishu_template',
            'allowed_file_extensions'
        ]

    def validate_feishu_template(self, value):
        # 验证飞书链接格式
        if value and not all(k in value for k in ['token', 'category']):
            raise ValidationError("飞书模板格式不正确")
        return value
```

## 扩展设计策略

### 当前扩展点
1. **自定义文件类型**：支持用户动态添加新的文件类型
2. **多模板支持**：一个交付物定义可关联多个版本的模板
3. **灵活配置**：是否必填、是否链接优先等可配置项

### 未来扩展方向
1. **模板库**：建立企业级交付物模板库，支持跨项目复用
2. **智能推荐**：基于项目类型智能推荐需要的交付物
3. **版本对比**：支持不同版本间的差异对比
4. **批量导入**：支持Excel批量导入交付物定义
5. **多语言支持**：交付物名称和说明支持多语言

## 演进方向 (Future Evolution)

### 短期优化（1-3个月）
- [ ] 增加交付物定义的导入/导出功能
- [ ] 优化飞书模板的预览体验
- [ ] 增加文件类型的批量管理功能
- [ ] 完善版本管理的用户界面

### 中期规划（3-6个月）
- [ ] 建立交付物标准库，支持快速选择常用模板
- [ ] 实现交付物定义的审批流程
- [ ] 支持交付物之间的依赖关系配置
- [ ] 增加交付物完成度统计功能

### 长期愿景（6-12个月）
- [ ] AI驱动的交付物智能推荐
- [ ] 与项目管理工具深度集成（如Jira、Tapd）
- [ ] 建立交付物质量评估体系
- [ ] 支持自定义交付物工作流

## 模块特有名词索引

当用户提到以下名词时，应快速定位到本模块：

| 名词 | 英文 | 说明 |
|------|------|------|
| 交付物定义 | DeliverableDefinition | 本模块核心概念 |
| 交付物模板 | Deliverable Template | 交付物定义的别名 |
| 文件类型 | FileExtension | 可上传文件的扩展名 |
| 飞书模板 | Feishu Template | 集成的飞书文档模板 |
| 版本号 | Display Version | 交付物定义的版本标识 |
| 链接优先 | Link First | 优先使用链接而非文件上传 |
| 必填项 | Required | 是否必须提交的交付物 |

## 触发条件总结

当用户提到以下关键词或场景时，应激活本技能：

1. **明确关键词**：
   - "交付物定义"、"交付物模板"、"DeliverableDefinition"
   - "deliverable"、"交付物"
   - "文件类型"、"FileExtension"、"文件扩展名"
   - "飞书模板"、"feishu"
   - "版本管理"、"版本号"

2. **操作场景**：
   - 创建/编辑/删除交付物定义
   - 配置文件上传限制
   - 集成飞书文档模板
   - 管理交付物版本历史

3. **路径相关**：
   - `/psc/deliverabledefinition/*`
   - `psc/deliverable/definitions` API路径
