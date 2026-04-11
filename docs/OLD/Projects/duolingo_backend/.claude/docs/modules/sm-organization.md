# organization 模块

## 职责
组织管理：组织信息的增删改查、编码自动生成、超级用户权限控制。

## 模块位置
`apps/SM/organization/`

## 数据模型

### Organization
组织模型，用于管理业务组织信息。

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | AutoField | 主键 |
| code | CharField(20) | 组织编码（唯一，自动生成：O + 日期 + 序号） |
| name | CharField(100) | 组织名称 |
| remark | CharField(255) | 备注 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

**数据库表**: `sm_organization`

## 序列化器

### ListSerializer
组织列表序列化器（驼峰型字段命名）。

**字段**: `id`, `code`, `name`, `remark`, `createdAt`, `updatedAt`

**特性**:
- 时间字段自动转换为本地时间格式

### WriteSerializer
组织写入序列化器。

**字段**: `name`, `remark`

**验证规则**:
- `name`: 组织名称必须唯一

### GetParamsSerializer
列表查询参数序列化器。

**字段**:
- `page`: 页码（默认 0）
- `name`: 组织名称模糊搜索（可选）

**功能**:
- 分页查询（每页 10 条）
- 支持按名称模糊筛选

### DeleteSerializer
批量删除序列化器。

**字段**:
- `ids`: 待删除的组织 ID 列表

## 视图

### ListView
组织列表视图（需要超级用户权限）。

**权限**: `PermissionSuperUser`（仅超级用户可访问）

**方法**:
- `GET /organizations`: 获取组织列表（支持分页和名称筛选）
- `POST /organizations`: 创建组织
- `DELETE /organizations`: 批量删除组织

**响应格式**:
```python
# GET 列表
{
  'msg': 'success',
  'data': {
    'items': [...],
    'pagination': {
      'page': 0,
      'page_size': 10,
      'total': 100
    }
  }
}

# POST 创建
{
  'msg': 'success',
  'data': {
    'id': 1,
    'code': 'O202503150001'
  }
}
```

### DetailView
组织详情视图（需要超级用户权限）。

**权限**: `PermissionSuperUser`（仅超级用户可访问）

**方法**:
- `GET /organizations/<id>`: 获取组织详情
- `PUT /organizations/<id>`: 更新组织信息

**错误响应**:
- 404: 组织不存在

## URL 路由配置

```python
path('organizations', ListView.as_view()),
path('organizations/<int:action>', DetailView.as_view()),
```

## 枚举数据
无

## 关联模块

### 被依赖方
- **apps/SM/user**: User 模型通过 `organization` 字段一对一关联 Organization
- **apps/BDM/account**: Account 模型通过 `organization` 字段关联 Organization
- **apps/BDM/customer**: Customer 模型通过 `organization` 字段关联 Organization
- **apps/APS/orders**: Order 模型通过 `organization` 字段关联 Organization

### 依赖方
- **utils/code_generator**: `generate_code()` 函数用于生成组织编码

## 业务规则

1. **编码生成**: 创建组织时自动生成唯一编码，格式为 `O + 日期 + 序号`（如 O202503150001）
2. **权限控制**: 所有接口仅超级用户（is_superuser=True）可访问
3. **名称唯一性**: 组织名称在系统中必须唯一
4. **批量删除**: 支持批量删除，不存在的 ID 自动跳过

## 使用场景

1. **超级用户管理组织**: 系统管理员创建和管理多个组织
2. **数据隔离**: 通过组织实现不同用户/客户/账户的数据隔离
3. **多租户支持**: 支持多组织架构

## 常见问题

**Q: 为什么普通用户无法访问组织接口？**
A: 组织管理是系统级别的管理功能，仅超级用户可操作。普通用户通过 `request.user.organization` 自动关联其所属组织。

**Q: 组织编码可以修改吗？**
A: 不可以。组织编码在创建时自动生成且唯一，后续不允许修改。

## 开发注意事项

1. **权限检查**: 所有视图必须使用 `PermissionSuperUser` 权限类
2. **编码自动生成**: 创建组织时无需手动传递 code，由 `save()` 方法自动生成
3. **级联删除**: 删除组织前需确认没有关联的用户、客户、账户、订单数据
4. **时间格式**: 前端显示使用驼峰型字段名（createdAt/updatedAt）

## 依赖
- `utils.code_generator.generate_code()`: 生成唯一组织编码
- `utils.common.to_local_time()`: 时间字段转换为本地时间

## 状态机
无

## 禁止事项
- 禁止普通用户访问组织管理接口
- 禁止手动修改组织编码
- 禁止创建重名组织
- 禁止删除有关联数据的组织（需先处理关联数据）

## 变更记录
### 2026-03-15
- 创建文档
