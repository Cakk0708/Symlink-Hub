# SM 角色管理模块

## 模块定位

SM（System Management）角色管理模块是系统权限体系的核心基础单元，负责定义和管理系统中的角色实体。角色作为连接用户与权限的桥梁，是 RBAC（基于角色的访问控制）权限模型中的关键组件。

**核心价值**：
- 提供系统角色的标准化定义和管理
- 支持角色编码自动生成机制
- 实现角色禁用/启用状态控制
- 为用户-角色关联提供基础数据

## 模块职责边界

### 核心职责
1. **角色基础信息管理**：角色编码、角色名称的维护
2. **角色编码生成**：基于规则自动生成唯一角色编码
3. **角色状态控制**：禁用/启用角色的业务状态
4. **角色查询服务**：提供列表、枚举、简单列表等多维查询

### 职责边界（不负责）
- ❌ 用户-角色关联分配（由用户管理模块负责）
- ❌ 角色-权限关联分配（由权限管理模块负责）
- ❌ 权限验证逻辑（由权限验证工具负责）
- ❌ 组织维度角色控制（由组织模块配合处理）

### 模块边界示意
```
┌─────────────────────────────────────────────────────────┐
│                    SM 角色管理模块                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 角色CRUD    │  │ 编码生成    │  │ 状态控制    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
         ↓                ↓                ↓
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  用户管理     │ │  权限管理     │ │  业务模块     │
│ (分配角色)    │ │ (分配权限)    │ │ (使用角色)    │
└───────────────┘ └───────────────┘ └───────────────┘
```

## 核心数据模型

### Role（角色实体）

```typescript
interface Role {
  // 主键字段
  id: number;                    // 角色唯一标识

  // 基础业务字段
  code: string;                  // 角色编码（自动生成，唯一）
  name: string;                  // 角色名称（必填，人工输入）
  roleType: string;              // 角色类型：BUILTIN（内置）/ CUSTOM（自定义）

  // 扩展字段（通过 others 对象返回）
  others?: {
    createTime?: string;         // 创建时间
    createBy?: string;           // 创建人
    updateTime?: string;         // 更新时间
    updatedBy?: string;          // 更新人
    disableFlag?: string;        // 禁用状态（"0"=启用, "1"=禁用）
    approvalHidden?: string;     // 审核隐藏标志
  };
}
```

### 角色类型说明

**BUILTIN（内置流程角色）：**
- 系统预设的角色，用于项目/节点级别的权限控制
- 包含：项目负责人 (PROJECT_OWNER)、节点负责人 (NODE_OWNER)、节点协助者 (NODE_ASSISTOR)、管理者 (MANAGER)
- 约束：不可删除、列表页隐藏删除按钮
- 显示：角色列表页显示"内置"标签

**CUSTOM（自定义角色）：**
- 用户创建的角色
- 约束：可删除（需先解除用户关联）
- 显示：无标签或"自定义"标签

### 数据约束
- `code`：保存时自动生成，遵循系统编码规则（调用 `getCode` API，参数 `"sm_role"`）
- `name`：必填字段，需唯一性校验
- `disableFlag`：基于字典枚举值

### 枚举定义
```typescript
enum DisableFlag {
  Enabled = "0",    // 启用
  Disabled = "1"    // 禁用
}
```

## 权限验证流程

### 权限标识符
```typescript
// 角色相关权限标识符
const ROLE_PERMISSIONS = {
  ADD: "SM.add_role",       // 新增角色权限
  CHANGE: "SM.change_role", // 修改角色权限
  VIEW: "SM.view_role",     // 查看角色权限
};
```

### 权限验证函数
```typescript
// 权限验证工具函数（src/utils/index.js）
function validatePerm(perm: string, showTip: boolean = true): boolean {
  if (permsList.length === 0) return true;  // 无权限列表时默认通过

  const paraList = perm.split(',');  // 支持多权限组合（逗号分隔）
  let hasPerm = true;

  paraList.forEach(item => {
    if (permsList.indexOf(item) === -1) hasPerm = false;
  });

  if (!hasPerm && showTip) {
    ElMessage.error('您没有对应权限');
  }

  return hasPerm;
}
```

### 权限验证应用场景

| 操作 | 权限标识符 | 验证位置 |
|------|-----------|----------|
| 新增角色 | `SM.add_role` | 列表页新增按钮、新增页面保存 |
| 修改角色 | `SM.change_role` | 编辑页面保存按钮状态 |
| 查看角色 | `SM.view_role` | 编辑/查看模式切换 |
| 删除角色 | `SM.del_role` | 列表页删除按钮 |
| 导出角色 | `SM.export_role` | 列表页导出按钮 |

### 权限控制流程图
```
用户操作
    ↓
权限验证 (validatePerm)
    ↓
┌─────────────┬─────────────┐
│ 有权限      │ 无权限      │
│ ↓           │ ↓           │
│ 执行操作    │ 提示错误    │
│             │ 阻止操作    │
└─────────────┴─────────────┘
```

## 认证与授权区别说明

### 认证（Authentication）
- **定义**：验证用户身份的过程
- **实现**：用户登录时，后端返回 `tokenType` + `tokenData.access`
- **存储**：Token 存储在 `localStorage[TOKEN_KEY]`
- **使用**：每次 API 请求自动在 Header 中携带 `Authorization: Bearer {token}`
- **相关代码**：`src/stores/modules/user.js` 中的 `login()` 函数

### 授权（Authorization）
- **定义**：验证用户是否有权限执行特定操作
- **实现**：基于用户的 `roles` 和 `perms` 进行权限判断
- **存储**：权限列表存储在 `localStorage[PERMS_KEY]`
- **使用**：通过 `validatePerm()` 函数验证权限标识符
- **相关代码**：`src/utils/index.js` 中的 `validatePerm()` 函数

### 两者关系
```
登录认证 (Authentication)
    ↓
获取 Token
    ↓
携带 Token 请求用户信息
    ↓
获取用户角色 (roles) + 权限 (perms)
    ↓
权限验证 (Authorization)
    ↓
控制 UI 元素显示/隐藏 + API 访问控制
```

### 角色在权限体系中的位置
```
User (用户)
    ↓ N:M
Role (角色) ← 本模块管理范围
    ↓ N:M
Permission (权限) ← 权限管理模块
```

## 与其他模块关系

### 依赖关系图
```
┌─────────────────────────────────────────────────────────────┐
│                         前端应用层                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ 用户管理     │───▶│ 角色管理     │◀───│ 权限管理     │    │
│  │ SM User     │    │ SM Role     │    │ Permission  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         ↓                   ↓                   ↓          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              业务模块（PM/PMS/BDM/CRM...）           │  │
│  └─────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                         状态管理层                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ User Store  │    │ Permission  │    │ Enum Dict   │    │
│  │             │    │ Store       │    │ Store       │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                         工具层                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ validatePerm│    │ request.js  │    │ getCode     │    │
│  │ (权限验证)   │    │ (HTTP封装)  │    │ (编码生成)  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 与用户管理模块的关系
- **关系类型**：多对多关联
- **关联方式**：用户管理模块负责分配角色给用户
- **数据流向**：用户登录后，`user.roles` 包含用户拥有的角色列表
- **相关代码**：`src/stores/modules/user.js` 中的 `getUserInfo()` 函数

### 与权限管理模块的关系
- **关系类型**：多对多关联
- **关联方式**：权限管理模块负责分配权限给角色
- **数据流向**：角色关联的权限列表决定用户可访问的资源
- **相关代码**：`src/stores/modules/user.js` 中的 `user.perms`

### 与组织管理模块的关系
- **关系类型**：维度控制关系
- **关联方式**：角色可以限定在特定组织范围内生效
- **数据流向**：通过 `toggleOrg()` 切换组织后，角色权限范围相应变化
- **相关代码**：`src/stores/modules/user.js` 中的 `toggleOrg()` 函数

### 与编码服务的关系
- **关系类型**：服务依赖
- **关联方式**：新增角色时调用编码生成服务
- **数据流向**：调用 `getCode("sm_role")` 获取自动生成的角色编码
- **相关代码**：`src/api/code.js`

### 与各业务模块的关系
- **关系类型**：消费者
- **关联方式**：各业务模块通过权限标识符使用角色进行权限控制
- **使用场景**：
  - PM（项目管理）：项目创建、审批权限
  - PMS（项目管理系统）：项目角色配置
  - BDM（基础数据管理）：物料、BOM 维护权限
  - CRM（客户管理）：客户信息访问权限

## 常见业务场景

### 场景1：新增角色
**操作流程**：
1. 点击列表页"新增"按钮（验证 `SM.add_role` 权限）
2. 进入新增页面，输入角色名称
3. 点击"保存"按钮，触发编码自动生成
4. 提交数据到后端，成功后跳转到编辑页面

**关键代码位置**：
- 列表页新增按钮：`src/views/sm/role/index.vue`
- 新增页面：`src/views/sm/role/add.vue`
- 编码生成：`src/views/sm/role/components/smRoleRender.vue:138`

### 场景2：编辑角色
**操作流程**：
1. 从列表页点击角色编码或双击行进入编辑页
2. 根据权限判断进入编辑或查看模式（`SM.change_role`）
3. 修改角色信息
4. 点击"保存"提交变更（仅提交修改的字段）

**关键代码位置**：
- 编辑页面：`src/views/sm/role/edit.vue`
- 表单组件：`src/views/sm/role/components/smRoleRender.vue`
- 权限判断：`SM.change_role` 验证

### 场景3：复制角色
**操作流程**：
1. 从列表页选择"复制"操作
2. 跳转到新增页面，携带 `addId` 参数
3. 加载原角色数据作为初始值
4. 保存时生成新的角色编码

**关键代码位置**：
- 路由配置：`src/router/modules/sm.js:15`
- 新增页面：`src/views/sm/role/add.vue`

### 场景4：禁用角色
**操作流程**：
1. 在编辑页面的"业务操作"下拉菜单
2. 选择"禁用"选项（当前按钮为禁用状态，功能待实现）
3. 修改 `disableFlag` 状态为 "1"

**关键代码位置**：
- 业务操作按钮：`src/views/sm/role/components/smRoleRender.vue:47-63`
- PATCH API：`src/api/sm/role.js:55`

### 场景5：删除角色
**操作流程**：
1. 在编辑页面点击"删除"按钮（验证权限）
2. 弹出确认对话框
3. 调用删除 API，成功后返回列表页

**BUILTIN 角色约束：**
- BUILTIN 类型的角色不显示删除按钮
- BUILTIN 类型的角色不允许删除

**关键代码位置**：
- 删除函数：`src/views/sm/role/components/smRoleRender.vue:156`

**前端实现示例：**
```vue
<template>
  <el-button
    v-if="role.roleType !== 'BUILTIN'"
    type="danger"
    @click="handleDelete"
  >
    删除
  </el-button>
</template>
```

### 场景6：角色列表查询
**操作流程**：
1. 进入角色列表页
2. 输入角色编码或名称进行搜索
3. 点击列头进行排序
4. 分页浏览结果

**关键代码位置**：
- 列表页：`src/views/sm/role/index.vue`
- 查询 API：`src/api/sm/role.js:4`

## 技术实现建议（Vue 3）

### 页面组件结构
```
views/sm/role/
├── index.vue                    # 角色列表页
├── add.vue                      # 角色新增页
├── edit.vue                     # 角色编辑/查看页
└── components/
    └── smRoleRender.vue         # 角色表单渲染组件（可复用）
```

### 状态管理建议
```typescript
// stores/modules/role.js（可选，按需创建）
export const useRoleStore = defineStore('role', () => {
  const roleList = ref([]);
  const roleEnum = ref([]);

  // 获取角色列表
  async function fetchRoleList(params) {
    const { data } = await getRoleList(params);
    roleList.value = data.items;
    return data;
  }

  // 获取角色枚举
  async function fetchRoleEnum() {
    const { data } = await getRoleEnum();
    roleEnum.value = data;
    return data;
  }

  return {
    roleList,
    roleEnum,
    fetchRoleList,
    fetchRoleEnum
  };
});
```

### 权限控制最佳实践
```vue
<template>
  <!-- 方式1：指令式权限控制 -->
  <el-button
    v-if="hasPermission('SM.add_role')"
    @click="handleAdd"
  >
    新增
  </el-button>

  <!-- 方式2：函数式权限控制 -->
  <el-button
    :disabled="!hasPermission('SM.change_role')"
    @click="handleEdit"
  >
    编辑
  </el-button>
</template>

<script setup>
import { validatePerm } from '@/utils';

// 组合式函数
function hasPermission(perm) {
  return validatePerm(perm, false);  // 不显示提示
}

// 使用示例
function handleAdd() {
  if (!hasPermission('SM.add_role')) {
    ElMessage.error('您没有新增权限');
    return;
  }
  // 执行新增逻辑
}
</script>
```

### API 调用最佳实践
```typescript
// 使用 async/await 统一错误处理
async function handleSave(formData) {
  try {
    const { data } = await addRole(formData);
    ElMessage.success('保存成功');
    // 跳转逻辑
    router.push(`/sm/role/edit/${data.insertId}/edit`);
  } catch (error) {
    console.error('保存失败：', error);
    ElMessage.error(error.message || '保存失败');
  }
}

// 使用差异更新优化性能
async function handleUpdate(formData) {
  // 仅提交修改的字段
  const changedFields = getChangedFields(originalData, formData);
  if (Object.keys(changedFields).length === 0) {
    ElMessage.info('没有修改内容');
    return;
  }

  try {
    await updateRole({ id: formData.id, ...changedFields });
    ElMessage.success('更新成功');
  } catch (error) {
    ElMessage.error('更新失败');
  }
}
```

### 表单验证最佳实践
```vue
<script setup>
const rules = {
  name: [
    { required: true, message: '角色名称不能为空', trigger: 'change' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { pattern: /^[A-Z0-9_]+$/, message: '角色编码只能包含大写字母、数字和下划线', trigger: 'blur' }
  ]
};

// 异步验证（编码唯一性）
const validateCodeUnique = async (rule, value, callback) => {
  if (!value) return callback();
  try {
    const { data } = await checkCodeUnique(value);
    if (!data.unique) {
      callback(new Error('角色编码已存在'));
    } else {
      callback();
    }
  } catch (error) {
    callback(new Error('验证失败'));
  }
};
</script>
```

## 扩展设计策略

### 短期扩展（3-6个月）
1. **角色模板功能**
   - 支持创建角色模板，快速生成相似角色
   - 模板包含预设的权限配置

2. **角色分组功能**
   - 支持按业务模块分组角色（如：PM角色组、BDM角色组）
   - 提升角色管理效率

3. **角色导入导出**
   - 支持批量导入角色数据
   - 支持导出角色配置用于跨环境迁移

### 中期扩展（6-12个月）
1. **角色继承机制**
   - 支持角色间的继承关系
   - 子角色自动拥有父角色的权限

2. **角色版本管理**
   - 记录角色配置变更历史
   - 支持角色配置回滚

3. **动态角色规则**
   - 基于条件自动分配角色
   - 支持基于用户属性的组织角色分配

### 长期扩展（12个月以上）
1. **角色生命周期管理**
   - 角色审批工作流
   - 角色定期审核机制
   - 角色过期自动清理

2. **智能角色推荐**
   - 基于用户行为推荐合适的角色
   - AI 辅助角色权限配置

3. **跨系统角色同步**
   - 支持与外部系统的角色映射
   - 统一角色管理平台

## 演进方向（Future Evolution）

### 架构演进
```
当前架构（单体角色管理）
    ↓
模块化架构（按业务域划分角色）
    ↓
微服务架构（独立的角色服务）
    ↓
联邦身份管理（跨系统统一角色）
```

### 技术演进
1. **从静态到动态**
   - 当前：静态配置的角色权限
   - 未来：基于上下文动态调整角色权限

2. **从粗粒度到细粒度**
   - 当前：模块级权限控制
   - 未来：字段级、数据级权限控制

3. **从人工到智能**
   - 当前：人工分配和管理角色
   - 未来：AI 辅助角色分配和权限优化

### 业务演进
1. **从内部到外部**
   - 当前：仅管理内部系统角色
   - 未来：支持外部合作伙伴角色管理

2. **从单一到多元**
   - 当前：单一维度的角色定义
   - 未来：支持多租户、多组织的角色体系

3. **从管理到治理**
   - 当前：基础的角色 CRUD 管理
   - 未来：完整的角色治理体系（合规、审计、风险控制）

## API 规范文档

### 1. 查询角色列表
```http
GET /sm/roles
```

**请求参数（Query Parameters）**
```typescript
interface RoleListQuery {
  code?: string;           // 角色编码（模糊查询）
  name?: string;           // 角色名称（模糊查询）
  pageNum?: number;        // 页码（默认1）
  pageSize?: number;       // 页大小（默认10）
  pageSort?: string;       // 排序条件（JSON格式）
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "ROLE_ADMIN",
        "name": "系统管理员",
        "others": {
          "createTime": "2024-01-01 10:00:00",
          "createBy": "admin",
          "updateTime": "2024-01-15 14:30:00",
          "updatedBy": "admin",
          "disableFlag": "0"
        }
      }
    ],
    "pagination": {
      "total": 100,
      "pageNum": 1,
      "pageSize": 10
    }
  }
}
```

### 2. 获取角色枚举
```http
GET /sm/roles/enums
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "label": "系统管理员", "value": 1 },
    { "label": "项目经理", "value": 2 }
  ]
}
```

### 3. 获取角色简单列表
```http
GET /sm/roles/simple
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "id": 1, "name": "系统管理员" },
    { "id": 2, "name": "项目经理" }
  ]
}
```

### 4. 获取角色详情
```http
GET /sm/roles/{id}
```

**路径参数**
- `id`: 角色ID（必填）

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "code": "ROLE_ADMIN",
    "name": "系统管理员",
    "others": {
      "createTime": "2024-01-01 10:00:00",
      "createBy": "admin",
      "updateTime": "2024-01-15 14:30:00",
      "updatedBy": "admin",
      "disableFlag": "0"
    }
  }
}
```

### 5. 新增角色
```http
POST /sm/roles
```

**请求体**
```json
{
  "code": "ROLE_PM",
  "name": "项目经理",
  "disableFlag": "0"
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "insertId": 3
  }
}
```

### 6. 修改角色
```http
PUT /sm/roles/{id}
```

**路径参数**
- `id`: 角色ID（必填）

**请求体**
```json
{
  "id": 3,
  "code": "ROLE_PM",
  "name": "高级项目经理",
  "disableFlag": "0"
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 7. 部分更新角色
```http
PATCH /sm/roles/{id}
```

**路径参数**
- `id`: 角色ID（必填）

**请求体**
```json
{
  "name": "项目经理（已更新）"
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 8. 删除角色
```http
DELETE /sm/roles
```

**请求体**
```json
{
  "ids": [1, 2, 3]
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

## 模块特有名词索引

当在项目上下文中出现以下名词时，应快速定位到本技能：

| 名词 | 说明 | 定位 |
|------|------|------|
| SM Role | 系统管理模块的角色实体 | 本技能核心 |
| 角色编码 | 角色的唯一标识符 | 数据模型 |
| 角色名称 | 角色的显示名称 | 数据模型 |
| 角色管理 | 角色的增删改查操作 | 业务场景 |
| 禁用角色 | 将角色状态设置为不可用 | 业务场景 |
| SM.add_role | 新增角色权限标识符 | 权限控制 |
| SM.change_role | 修改角色权限标识符 | 权限控制 |
| SM.view_role | 查看角色权限标识符 | 权限控制 |
| 角色列表 | 展示所有角色的页面 | 页面组件 |
| 角色模板 | 用于快速创建相似角色 | 扩展功能 |
| 角色分组 | 按业务模块分类角色 | 扩展功能 |

## 关键文件速查表

| 文件路径 | 功能说明 | 关键函数/组件 |
|---------|---------|--------------|
| `src/views/sm/role/index.vue` | 角色列表页 | LYTable组件 |
| `src/views/sm/role/add.vue` | 角色新增页 | smRoleRender组件 |
| `src/views/sm/role/edit.vue` | 角色编辑页 | smRoleRender组件 |
| `src/views/sm/role/components/smRoleRender.vue` | 角色表单渲染组件 | 表单验证、编码生成 |
| `src/api/sm/role.js` | 角色API定义 | getRoleList, addRole, updateRole |
| `src/router/modules/sm.js` | SM模块路由配置 | 角色相关路由 |
| `src/stores/modules/user.js` | 用户状态管理 | getUserInfo, roles |
| `src/utils/index.js` | 工具函数 | validatePerm |

## 开发注意事项

1. **编码生成**：角色编码在保存时自动生成，不应手动输入
2. **权限验证**：所有操作前都应进行权限验证
3. **差异更新**：编辑时应只提交修改的字段，提升性能
4. **禁用状态**：禁用角色不应删除，而是设置 `disableFlag` 为 "1"
5. **路由跳转**：新增成功后自动跳转到编辑页面
6. **表单验证**：角色名称为必填字段，需进行客户端验证
7. **删除确认**：删除操作需二次确认，防止误操作
8. **角色类型显示**：角色列表页应显示 `roleType` 字段，BUILTIN 角色显示"内置"标签
9. **删除按钮控制**：BUILTIN 角色的删除按钮应隐藏（`v-if="role.roleType !== 'BUILTIN'"`）
10. **角色类型不可编辑**：创建角色时强制 `role_type='CUSTOM'`，前端不允许修改此字段
