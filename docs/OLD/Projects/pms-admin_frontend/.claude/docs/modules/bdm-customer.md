# BDM 客户管理模块 (Customer)

## 模块定位

**业务域**: BDM（基础数据管理）
**模块路径**: `/bdm/customer`
**核心职责**: 客户主数据管理，是系统的基础业务实体之一

客户管理模块是 OMC 系统的基础数据模块，负责维护客户的基本信息和状态。客户数据被多个业务模块引用，包括订阅管理、项目管理等。客户的状态（禁用/启用）会直接影响订阅服务和小程序用户的登录权限。

---

## 模块职责边界

### 核心职责
- 客户基础信息维护（编码、名称、备注）
- 客户禁用状态管理
- 客户数据的生命周期管理（增删改查）

### 模块边界
**包含**:
- 客户基础属性管理
- 客户状态控制（禁用/启用）
- 客户列表查询与筛选

**不包含**（属于其他模块）:
- 订阅关系管理（SUB/CRM 模块）
- 客户接口管理（CRM 模块）
- 客户相关的业务流程（如订单、合同等）

### 关联模块
- **SUB（订阅管理）**: 客户被禁用会导致订阅失效
- **CRM（客户关系管理）**: 更复杂的客户关系管理功能
- **小程序系统**: 客户禁用状态影响小程序用户登录

---

## 核心数据模型

### Customer（客户主模型）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id / primaryId | int | 是 | 主键 ID |
| code | string | 否 | 客户编码（保存时自动生成） |
| name | string | 是 | 客户名称 |
| remark | string | 否 | 备注信息 |
| disableFlag | boolean | 是 | 禁用状态（true=禁用，false=启用） |
| createdAt | datetime | 是 | 创建时间 |
| updatedAt | datetime | 是 | 更新时间 |

### Others 字段结构

```javascript
{
  creator: { username: string },      // 创建人
  createTime: string,                 // 创建时间
  updatedBy: { username: string },    // 最后修改人
  updateTime: string                  // 最后修改时间
}
```

---

## API 规范

### 基础路径
- **应用**: BDM (业务数据管理)
- **模块路径**: `/bdm/customers`

### 接口列表

#### 1. 获取客户列表
- **方法**: `GET /bdm/customers`
- **参数**:
  ```javascript
  {
    pageNum: number,      // 页码
    pageSize: number,     // 每页数量
    code: string,         // 客户编码（可选）
    name: string,         // 客户名称（可选）
    disableFlag: boolean, // 禁用状态（可选）
    date: [string, string], // 创建时间范围（可选）
    pageSort: string      // 排序（可选，格式：字段:ASC/DESC）
  }
  ```
- **返回**:
  ```javascript
  {
    data: {
      pagination: {
        pageNum: number,
        pageSize: number,
        total: number
      },
      items: [
        {
          primaryId: number,
          code: string,
          name: string,
          region: string,        // 客户来源
          disableFlag: boolean,
          createdAt: string,
          remark: string
        }
      ]
    }
  }
  ```

#### 2. 获取客户详情
- **方法**: `GET /bdm/customers/{id}`
- **返回**:
  ```javascript
  {
    data: {
      id: number,
      document: {
        code: string,
        name: string,
        remark: string
      },
      others: {
        creator: { username: string },
        createTime: string,
        updatedBy: { username: string },
        updateTime: string
      }
    }
  }
  ```

#### 3. 新增客户
- **方法**: `POST /bdm/customers`
- **参数**:
  ```javascript
  {
    code: string,      // 可选，不填则自动生成
    name: string,      // 必填
    remark: string     // 可选
  }
  ```
- **返回**:
  ```javascript
  {
    data: {
      insertId: number  // 新增客户的 ID
    }
  }
  ```

#### 4. 更新客户
- **方法**: `PUT /bdm/customers/{id}`
- **参数**:
  ```javascript
  {
    code: string,      // 可选，不修改则不传
    name: string,      // 必填
    remark: string     // 可选
  }
  ```

#### 5. 修改客户状态（PATCH）
- **方法**: `PATCH /bdm/customers/{id}`
- **参数**:
  ```javascript
  {
    disableFlag: boolean  // true=禁用，false=启用
  }
  ```
- **批量操作**:
  ```javascript
  // id 可以是逗号分隔的多个 ID
  PATCH /bdm/customers/{id1,id2,id3}
  {
    disableFlag: boolean
  }
  ```

#### 6. 删除客户
- **方法**: `DELETE /bdm/customers`
- **参数**:
  ```javascript
  {
    ids: number[]  // 要删除的客户 ID 数组
  }
  ```

#### 7. 获取客户枚举值
- **方法**: `GET /bdm/customers/enum`
- **说明**: 用于下拉选择等场景

---

## 权限验证流程

### 认证机制
- 基于 Token 的身份认证
- Token 通过请求头 `Authorization` 传递
- Token 过期返回 401，自动跳转登录页

### 授权机制
客户管理模块目前未启用细粒度权限控制，相关权限检查代码已被注释：

```javascript
// src/views/bdm/customer/index.vue:271
// const isEdit = validatePerm('CRM.add_cust', false);

// src/views/bdm/customer/index.vue:322
// const isEdit = validatePerm('CRM.change_cust', false);
```

**预留权限点**:
- `CRM.add_cust` - 新增客户
- `CRM.change_cust` - 修改客户

### 禁用操作的业务约束

禁用客户是一个**高风险操作**，会影响：
1. 订阅服务失效
2. 小程序用户无法登录

**交互要求**:
- 禁用操作必须弹出二次确认对话框
- 确认文案需明确说明后果
- 单个禁用和批量禁用都需要确认

```javascript
// 确认文案模板
ElMessageBox.confirm(
  '禁用客户，将导致订阅失效且小程序用户无法登录，请确认是否继续操作？',
  '提示',
  {
    distinguishCancelAndClose: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }
)
```

### 状态一致性

- **列表页**: 禁用操作后需更新本地数据状态
- **详情页**: 禁用后表单置为不可编辑状态
- **禁用状态**: `forbiddenStatus.disabled = true`

---

## 与其他模块关系

### 依赖关系图

```
┌─────────────────┐
│  BDM/Customer   │  客户主数据
│   (本模块)       │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────────┐ ┌─────────────────┐
│  SUB/订阅管理     │ │  CRM/客户关系    │
│  - 订阅状态      │ │  - 接口管理      │
│  - 客户关联      │ │  - 关系维护      │
└─────────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────┐
│  小程序系统      │
│  - 用户登录      │
│  - 权限验证      │
└─────────────────┘
```

### 数据流向

1. **客户创建** → 生成客户编码 → 可被订阅模块引用
2. **客户禁用** → 订阅服务失效 → 小程序用户无法登录
3. **客户删除** → 需检查是否有关联数据（订阅、项目等）

---

## 常见业务场景

### 场景 1: 新增客户
1. 点击"新增"按钮
2. 进入新增页面（只显示客户名称、备注字段）
3. 填写客户名称（必填）
4. 点击"保存"
5. 系统自动生成客户编码
6. 保存成功后自动跳转到编辑页面

### 场景 2: 编辑客户
1. 双击列表行或点击客户编码
2. 进入编辑页面
3. 修改客户信息
4. 点击"保存"更新数据

### 场景 3: 禁用客户（列表页）
1. 勾选要禁用的客户
2. 点击"业务操作" → "禁用"
3. 弹出确认对话框
4. 确认后执行禁用
5. 更新列表状态

### 场景 4: 禁用客户（详情页）
1. 在编辑页点击"业务操作" → "禁用"
2. 弹出确认对话框
3. 确认后禁用表单
4. 显示禁用状态

### 场景 5: 删除客户
1. 勾选要删除的客户
2. 点击"删除"按钮
3. 弹出确认对话框
4. 确认后删除并刷新列表

---

## 文件结构

```
src/
├── api/bdm/
│   └── cust.js                       # 客户 API 接口
├── views/bdm/customer/
│   ├── index.vue                     # 客户列表页
│   ├── add.vue                       # 客户新增页
│   ├── edit.vue                      # 客户编辑页
│   └── components/
│       └── custRender.vue            # 客户表单渲染组件
└── router/modules/
    └── bdm.js                        # BDM 路由配置
```

---

## UI 设计规范

### 列表页 (index.vue)

**搜索条件**:
- 客户编码（code）
- 客户名称（name）
- 禁用状态（disableFlag）- 字典类型
- 创建时间（date）- 日期范围选择

**表格列**:
1. 选择框 (selection) - rowKey="primaryId"
2. 客户编码 (code) - 可点击跳转，高亮显示
3. 客户名称 (name)
4. 客户来源 (region)
5. 禁用状态 (disableFlag) - 字典显示
6. 创建时间 (createdAt)

**操作按钮**:
- 新增（下拉菜单样式，但目前只有新增项）
- 删除（批量，需要选中）
- 业务操作（下拉菜单）:
  - 禁用（目前禁用）
  - 反禁用（目前禁用）

**排序支持**:
- 客户编码字段支持自定义排序（sortable: 'custom'）

### 新增页 (add.vue)

**显示字段**:
- 客户编码（code）- 禁用状态，占位符"保存时自动生成"
- 客户名称（name）- 必填，placeholder="请输入客户名称"
- 备注（remark）- placeholder="请输入客户备注"

**按钮状态**:
- 保存：可用
- 业务操作：查看模式下禁用
- 删除：需要 ID 时才可用
- 退出：始终可用

### 编辑页 (edit.vue)

**显示字段**:
- 客户编码（code）- 禁用，自动生成后显示
- 客户名称（name）
- 备注（remark）

**其他信息** (LYOther 组件):
- 创建人
- 创建时间
- 最后更新人
- 最后更新时间

**特殊逻辑**:
- 客户编码未修改时不提交 code 字段
- 保存成功后更新 others 字段的 updatedBy 和 updateTime

### 组件 (custRender.vue)

**Props**:
```javascript
{
  formData: Object,      // 表单数据
  busiForm: Object,      // 业务表单（预留）
  dataStatus: Object,    // 按钮状态
  forbiddenStatus: {     // 禁用状态
    disabled: boolean
  }
}
```

**Emits**:
- `generateCode` - 生成编码
- `clickConfirm` - 保存确认
- `clickToggleStatus` - 切换禁用状态

---

## 交互细节

### 路由跳转

**新增**:
```javascript
router.push({ path: "customer/add" });
```

**编辑/查看**:
```javascript
router.push({
  path: `customer/edit/${row.primaryId}/${true?'edit':'view'}`
});
```

**新增成功后跳转**（使用 replace 避免返回到新增页）:
```javascript
useTagsViewStore().delView(route);
router.replace({
  path: `/bdm/customer/edit/${res.data.insertId}/edit`
});
```

### 列表操作

**双击行跳转编辑**:
```javascript
const rowDblclick = (row) => {
  handleUpdate(row)
}
```

**点击编码跳转编辑**:
```javascript
const cellClick = (row) => {
  handleUpdate(row)
}
```

### 状态更新（乐观更新）

```javascript
patchCust({ id, disableFlag: val }).then(res => {
  custList.value.forEach(item => {
    if (ids.value.includes(item.id)) {
      item.disableFlag = val
    }
  })
})
```

### 编码处理

编辑页保存时，如果编码未修改则不提交：
```javascript
let oldCode = initData.value.code
if (initData.value.code == billFormData.code || !billFormData.code) {
  delete billFormData.code
  // 保持原编码显示
  if (!billFormData.code) {
    initData.value.code = oldCode
    formData.value.code = oldCode
  }
}
```

---

## 字典配置

### disableFlag（禁用状态）
- 数据源：系统字典 `disableFlag`
- 显示类型：下拉选择/标签显示
- 用途：客户启用/禁用状态

### billStatus（单据状态）
- 数据源：系统字典 `billStatus`
- 说明：预留字段，当前未使用

---

## 特有名词索引

当未来对话中出现以下名词时，可快速定位到本模块：

| 名词 | 说明 |
|------|------|
| 客户管理 | BDM 模块的客户主数据管理 |
| 客户编码 | 自动生成的客户唯一标识 |
| 禁用客户 | 高风险操作，影响订阅和小程序 |
| 订阅失效 | 客户禁用后的业务影响 |
| 小程序登录 | 受客户禁用状态影响 |
| 客户来源 | 客户的 region 字段 |

---

## 技术实现建议（后端参考）

### Django 模型设计

```python
from django.db import models

class Customer(models.Model):
    """客户主数据模型"""
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="客户编码")
    name = models.CharField(max_length=200, verbose_name="客户名称")
    remark = models.TextField(null=True, blank=True, verbose_name="备注")
    disable_flag = models.BooleanField(default=False, verbose_name="禁用状态")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'bdm_customer'
        verbose_name = "客户"
        verbose_name_plural = "客户"
        ordering = ['-id']

    def __str__(self):
        return f"{self.code} - {self.name}"
```

### DRF 序列化器

```python
from rest_framework import serializers

class CustomerListSerializer(serializers.ModelSerializer):
    """客户列表序列化器"""
    primary_id = serializers.IntegerField(source='id')
    region = serializers.CharField(source='get_region_display', required=False)

    class Meta:
        model = Customer
        fields = ['primary_id', 'code', 'name', 'region', 'disable_flag', 'created_at', 'remark']

class CustomerDetailSerializer(serializers.ModelSerializer):
    """客户详情序列化器"""
    class Meta:
        model = Customer
        fields = '__all__'
```

### 视图集

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class CustomerViewSet(viewsets.ModelViewSet):
    """客户视图集"""
    queryset = Customer.objects.all()
    serializer_class = CustomerDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # 搜索过滤
        code = self.request.query_params.get('code')
        name = self.request.query_params.get('name')
        disable_flag = self.request.query_params.get('disableFlag')

        if code:
            queryset = queryset.filter(code__icontains=code)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if disable_flag is not None:
            queryset = queryset.filter(disable_flag=disable_flag)

        return queryset

    @action(detail=False, methods=['get'])
    def enum(self, request):
        """获取客户枚举值"""
        customers = self.queryset.filter(disable_flag=False)
        data = [{'id': c.id, 'name': c.name, 'code': c.code} for c in customers]
        return Response(data)

    @action(detail=True, methods=['patch'])
    def partial_update(self, request, pk=None):
        """部分更新（主要用于禁用状态）"""
        customer = self.get_object()
        disable_flag = request.data.get('disableFlag')

        if disable_flag is not None:
            customer.disable_flag = disable_flag
            customer.save()

        return Response({'status': 'success'})
```

---

## 扩展设计策略

### 短期扩展
1. **启用细粒度权限控制**
   - 取消注释权限验证代码
   - 配置 CRM.add_cust、CRM.change_cust 权限点

2. **完善禁用确认**
   - 启用列表页的禁用/反禁用按钮
   - 实现批量禁用功能

3. **客户来源管理**
   - 将 region 字段改为字典类型
   - 支持客户来源的自定义配置

### 中期扩展
1. **客户关联数据检查**
   - 删除前检查是否有关联订阅
   - 删除前检查是否有关联项目

2. **客户分类管理**
   - 支持客户类型/等级
   - 支持客户标签体系

3. **客户联系方式**
   - 添加联系电话、邮箱等字段
   - 支持多个联系方式

### 长期演进
1. **客户360视图**
   - 整合订阅、项目、订单等信息
   - 提供客户全生命周期视图

2. **客户数据导入导出**
   - 支持 Excel 批量导入
   - 支持数据导出功能

3. **客户数据归档**
   - 支持历史数据归档
   - 提供数据恢复机制

---

## 演进方向 (Future Evolution)

### 1. 与 CRM 模块深度整合
- 客户管理作为 CRM 的子模块
- 支持更复杂的客户关系管理
- 客户分级、信用额度等功能

### 2. 客户数据质量治理
- 客户数据重复检测
- 客户数据清洗规则
- 客户数据完整性校验

### 3. 客户画像与分析
- 客户行为分析
- 客户价值评估
- 客户生命周期管理

### 4. 多租户支持
- 支持组织隔离的客户数据
- 跨组织的客户共享机制

---

## 注意事项

1. **客户编码自动生成**: 新增时不显示编码，保存时后端自动生成并返回
2. **编码修改限制**: 客户编码生成后一般不允许修改
3. **禁用操作影响**: 禁用客户会影响订阅服务和小程序登录
4. **删除前检查**: 生产环境建议添加删除前的关联数据检查
5. **使用 primaryId**: 列表操作使用 primaryId 而不是 id
6. **路由跳转**: 新增成功后使用 replace 而不是 push
7. **乐观更新**: 状态更新时先更新本地数据再请求接口
