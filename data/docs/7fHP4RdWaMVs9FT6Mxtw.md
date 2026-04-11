# BDM 客户管理模块 (Customer Module)

## 模块定位

客户管理模块是 BDM (Business Data Management) 系统的核心基础模块，负责维护系统中所有客户（Customer）的基础信息。该模块作为业务数据的顶层聚合节点，与订单（Order）、账号（Account）等模块形成一对多的关联关系。

**核心价值**：提供统一的客户主数据管理，确保下游业务模块（订单、账号）的数据一致性。

---

## 模块职责边界

### 负责范围
- 客户基础信息的增删改查（CRUD）
- 客户编码（code）的自动生成与唯一性保证
- 客户类别（category）的枚举管理
- 客户订单数量的实时统计
- 客户名称的唯一性校验
- 客户删除时的关联账户验证

### 不负责范围
- 订单执行流程（属于 APS 模块）
- 账号登录验证（属于 Account 模块）
- 支付处理（属于业务支付模块）

---

## 核心数据模型

### Customer 模型

**文件位置**: `apps/BDM/customer/models.py`

```python
class Customer(models.Model):
    code        = CharField(max_length=20, unique=True, null=True, blank=True)
    name        = CharField(max_length=50)
    category    = CharField(max_length=50, choices=Choices.category, default='GOOFISH')
    organization= ForeignKey(Organization, null=True, blank=True, on_delete=SET_NULL)
    created_at  = DateTimeField(auto_now_add=True)
    updated_at  = DateTimeField(auto_now=True)
```

**字段说明**:
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `code` | CharField(20) | UNIQUE, NULLABLE | 客户编码，自动生成，格式：C + YYYYMMDD + 3位序号 |
| `name` | CharField(50) | REQUIRED | 客户名称，需唯一性校验 |
| `category` | CharField(50) | CHOICES | 客户类别，当前支持：GOOFISH(闲鱼) |
| `organization` | ForeignKey | NULLABLE | 所属组织，关联到 SM.Organization |
| `created_at` | DateTimeField | AUTO | 创建时间 |
| `updated_at` | DateTimeField | AUTO | 更新时间 |

**组织关联说明**:
- 创建客户时自动关联创建者的组织
- 通过序列化器的 `create` 方法自动设置
- 组织删除时不级联删除客户（SET_NULL）

**编码生成规则**:
- 格式：`C20250308001`
- 前缀：`C` (Customer)
- 日期：`YYYYMMDD` (8位)
- 序号：`001` (3位，每日重置)
- 工具函数：`utils.code_generator.generate_code()`

---

## API 接口规范

### 序列化器

**文件位置**: `apps/BDM/customer/serializers.py`

| 序列化器 | 用途 | 字段特点 |
|---------|------|---------|
| `CustomerDetailSerializer` | 客户详情 | 包含 accounts、organization 关联数据，驼峰型字段命名 |
| `CustomerListSerializer` | 客户列表 | 包含 orderCount、organization，驼峰型字段命名 |
| `CustomerWriteSerializer` | 创建/更新 | 仅包含 name, category，create 方法自动设置组织 |
| `CustomerDeleteSerializer` | 删除操作 | ids 批量删除 + 关联验证 |
| `serializerOrganization` | 组织嵌套 | 嵌套序列化器，返回 id 和 name |

**字段命名规范**（驼峰型）:
- `categoryDisplay` - 类别显示名称
- `createdAt` - 创建时间
- `updatedAt` - 更新时间
- `orderCount` - 订单数量

### 响应格式规范

**列表接口**:
```json
{
    "msg": "success",
    "data": {
        "items": [...],
        "count": 42
    }
}
```

**详情接口**:
```json
{
    "msg": "success",
    "data": {
        "id": 1,
        "code": "C20250308001",
        "name": "客户名称",
        "categoryDisplay": "闲鱼",
        "createdAt": "2025-03-08 13:45:00",
        "updatedAt": "2025-03-08 13:45:00",
        "orderCount": 15,
        "organization": {
            "id": 1,
            "name": "组织名称"
        },
        "accounts": [...]
    }
}
```

**删除接口**:
```json
{
    "msg": "success"
}
```

### URL 路由

```
GET  /api/customer              # 列表查询
POST /api/customer              # 创建客户
GET  /api/customer/<id>         # 客户详情
DELETE /api/customer/delete     # 删除客户（批量）
GET  /api/customer/simple       # 简略列表（下拉选择）
```

### 简略列表接口

**接口**: `GET /api/customer/simple`
**用途**: 用于前端下拉选择组件，返回精简的客户列表

**响应格式**:
```json
{
    "msg": "success",
    "data": {
        "items": [
            {
                "value": 1,
                "label": "客户名称",
                "code": "C20250308001",
                "category": "GOOFISH",
                "organization": {
                    "id": 1,
                    "name": "组织名称"
                }
            }
        ],
        "pagination": {
            "page": 0,
            "pageSize": 10,
            "total": 1
        }
    }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `value` | Integer | 客户 ID，用于下拉选项值 |
| `label` | String | 客户名称，用于下拉选项显示 |
| `code` | String | 客户编码 |
| `category` | String | 客户类别（GOOFISH等） |
| `organization` | Object | 所属组织信息（id, name），可能为 null |

---

## 删除功能规范

### 关联验证规则

删除客户前必须验证是否存在关联账户：

```python
# CustomerDeleteSerializer.validate_ids()
for customer in value:
    if customer.accounts.exists():
        raise serializers.ValidationError(
            f'客户"{customer.name}"存在关联账户，无法删除'
        )
```

### 删除请求示例

**请求**: `DELETE /api/customer/delete`
**Body**:
```json
{
    "ids": [1, 2, 3]
}
```

**成功响应**:
```json
{
    "msg": "success"
}
```

**失败响应（有关联账户）**:
```json
{
    "msg": "error",
    "data": {
        "ids": ["客户\"客户名称\"存在关联账户，无法删除"]
    }
}
```

---

## 权限验证流程

当前模块**未实现**细粒度权限控制，所有认证用户均可访问。

**未来设计方向**:
```
请求 -> JWT认证 -> 角色检查 -> 资源所有权验证 -> 业务逻辑
```

### 建议权限矩阵

| 操作 | 管理员 | 普通用户 | 只读用户 |
|------|--------|----------|----------|
| 创建客户 | ✓ | ✗ | ✗ |
| 查看客户 | ✓ | ✓ | ✓ |
| 修改客户 | ✓ | 仅自己的 | ✗ |
| 删除客户 | ✓ | ✗ | ✗ |

---

## 与其他模块关系

### 依赖关系图

```
Customer (客户)
    ├─ 1:N ─> Account (账号) [通过 customer 外键关联]
    ├─ 1:N ─> Order (订单) [通过 Account.account → Customer 间接关联]
    ├─ N:1 ─> Organization (组织) [通过 organization 外键关联]
    └─ N:1 ─> Category (类别) [枚举值]
```

### 关键关联

**1. Customer ↔ Account**
- 当前状态：通过 ForeignKey 关联
- 影响：客户删除时需验证是否有关联账号（通过 `accounts.exists()` 检查）

**2. Customer ↔ Order**
- 关联路径：`Order.account → Account` → Account 所属客户
- 当前实现：通过 `model_order.objects.filter(account__customer=obj)` 统计订单数

**3. Customer ↔ Organization**
- 关联方式：通过 ForeignKey 关联到 `SM.Organization`
- 自动设置：创建客户时从 `request.user.organization` 自动获取
- 删除策略：SET_NULL，组织删除时客户记录保留（organization 置空）

**4. Customer ↔ Category**
- 实现方式：`Choices.category` 枚举类
- 扩展性：若类别需动态管理，建议独立为 Category 模型

---

## 常见业务场景

### 场景1：创建新客户
**请求**: `POST /api/customer`
**Body**:
```json
{
    "name": "闲鱼店铺A",
    "category": "GOOFISH"
}
```

**响应**:
```json
{
    "msg": "success",
    "data": {
        "id": 1,
        "code": "C20250308001",
        "name": "闲鱼店铺A",
        "categoryDisplay": "闲鱼",
        "orderCount": 0,
        "createdAt": "2025-03-08 13:45:00",
        "updatedAt": "2025-03-08 13:45:00"
    }
}
```

### 场景2：查询客户列表（带分页）
**请求**: `GET /api/customer?page=1&name=闲鱼`
**响应**:
```json
{
    "msg": "success",
    "data": {
        "items": [...],
        "count": 42
    }
}
```

### 场景3：获取客户详情
**请求**: `GET /api/customer/1`
**响应**:
```json
{
    "msg": "success",
    "data": {
        "id": 1,
        "code": "C20250308001",
        "name": "闲鱼店铺A",
        "categoryDisplay": "闲鱼",
        "orderCount": 15,
        "accounts": [
            {
                "id": 1,
                "username": "test_user",
                "nickname": "测试用户",
                "email": "test@example.com",
                "phone": "13800138000"
            }
        ],
        "createdAt": "2025-03-08 13:45:00",
        "updatedAt": "2025-03-08 13:45:00"
    }
}
```

### 场景4：删除客户（批量）
**请求**: `DELETE /api/customer/delete`
**Body**:
```json
{
    "ids": [1, 2, 3]
}
```

**成功响应**:
```json
{
    "msg": "success"
}
```

**失败响应（存在关联账户）**:
```json
{
    "msg": "error",
    "data": {
        "ids": ["客户\"闲鱼店铺A\"存在关联账户，无法删除"]
    }
}
```

---

## 技术实现建议 (Django)

### 文件结构
```
apps/BDM/customer/
├── __init__.py       # 导出 Customer, Choices
├── models.py         # Customer 模型 + save() 重写
├── enums.py          # Choices 枚举类
├── serializers.py    # 序列化器集合
└── views.py          # viewsCustomer
```

### 代码规范
- **序列化器命名**: `CustomerDetailSerializer`, `CustomerListSerializer`, `CustomerWriteSerializer`, `CustomerDeleteSerializer`
- **字段顺序**: 基础字段 → 对象/嵌套字段
- **缩进**: 3个空格
- **导入顺序**: 标准库 → 第三方库 → 本地应用
- **响应格式**: 遵循标准格式
  - 列表接口: `{msg, data: {items: [], count: N}}`
  - 单条接口: `{msg, data: {...}}`

### 性能优化建议
1. **订单统计优化**: 当前每次查询都执行 `COUNT`，建议：
   - 添加 `order_count` 冗余字段
   - 通过信号（post_save）自动更新
2. **分页优化**: 当前使用列表切片，建议使用 Django Paginator
3. **索引优化**: 为 `name`, `code`, `category` 字段添加数据库索引

---

## 扩展设计策略

### 1. 客户类别动态化
**当前**: 硬编码枚举 `Choices.category`
**目标**: 独立 Category 模型
```python
class Category(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    # 支持前端动态配置
```

### 2. 客户标签系统
```python
class Customer(models.Model):
    tags = models.ManyToManyField('CustomerTag')

class CustomerTag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7)  # HEX 颜色
```

### 3. 客户等级体系
```python
LEVEL_CHOICES = [
    ('BRONZE', '青铜'),
    ('SILVER', '白银'),
    ('GOLD', '黄金'),
]
class Customer(models.Model):
    level = models.CharField(choices=LEVEL_CHOICES, default='BRONZE')
```

---

## 演进方向 (Future Evolution)

### 短期计划 (1-2个月)
- [x] API 响应格式标准化 (2025-03-08 完成)
- [x] 序列化器规范化命名 (2026-03-14 完成)
- [x] 客户删除功能 + 关联验证 (2026-03-14 完成)
- [x] 客户简略列表接口（SimpleView，用于下拉选择） (2026-03-15 完成)
- [x] 序列化器字段驼峰型命名（categoryDisplay/createdAt/updatedAt/orderCount） (2026-03-15 完成)
- [x] 客户模块添加组织字段支持 (2026-03-15 完成)
- [ ] 添加客户删除软删除支持（`is_deleted` 字段）
- [ ] 实现 API 速率限制（防止滥用）
- [ ] 添加客户操作日志（审计追踪）

### 中期计划 (3-6个月)
- [ ] 引入客户等级体系
- [ ] 实现客户标签系统
- [ ] 添加客户联系人管理（多人关联）
- [ ] 实现客户数据导入导出（Excel）

### 长期愿景 (6个月+)
- [ ] 客户画像分析（基于订单数据）
- [ ] 客户生命周期管理（CLV计算）
- [ ] 智能客户推荐（相似客户推荐）
- [ ] 客户自助服务门户

---

## 模块特有名词索引

当用户提到以下术语时，Claude 应快速定位到本技能：

| 术语 | 定位 |
|------|------|
| `customer_code` / `客户编码` | 见 `编码生成规则` 章节 |
| `GOOFISH` / `闲鱼` | 见 `核心数据模型` 章节 |
| `order_count` / `订单统计` | 见 `与其他模块关系` 章节 |
| `organization` / `组织` | 见 `核心数据模型` 章节 |
| `generate_code` | 见 `utils/code_generator.py` 工具函数 |
| `CustomerDeleteSerializer` | 见 `删除功能规范` 章节 |

---

## 快速参考

**依赖工具**:
- `utils.code_generator.generate_code()` - 编码生成
- `utils.common.to_local_time()` - 时间格式化

**相关模块**:
- `apps/BDM/account/` - 账号管理
- `apps/APS/orders/` - 订单管理
- `apps/SM/organization/` - 组织管理

---

**最后更新**: 2026-03-15
