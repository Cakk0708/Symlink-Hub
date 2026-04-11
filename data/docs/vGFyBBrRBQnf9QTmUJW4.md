# SM 用户管理模块

## 模块定位

SM（系统管理）用户模块是 OMC 系统的核心认证授权基础，负责系统用户的全生命周期管理，包括用户创建、身份认证、权限分配、状态控制等核心功能。本模块是整个系统权限体系的入口，与角色、组织、权限模块紧密协作。

## 核心职责边界

### 用户模块负责
- 用户基础信息管理（账号、昵称、联系方式）
- 用户认证与登录状态管理
- 用户启用/禁用状态控制
- 密码管理与重置
- 用户特殊标识管理（铁三角、超级管理员、服务状态）
- 用户与角色关联
- 用户与组织关联

### 用户模块不负责
- 角色定义与权限配置 → 属于 `sm-role` 模块
- 组织架构管理 → 属于 `sm-organization` 模块
- 具体业务权限的细粒度控制 → 属于各业务模块

## 核心数据模型

### User 用户实体
```javascript
{
  id: String,                    // 用户唯一标识
  username: String,              // 用户账号（登录凭证，唯一，不可修改）
  nickname: String,              // 用户名称/昵称
  password: String,              // 密码（加密存储，默认值：MOM888）
  mobile: String,                // 联系电话（格式：+86手机号）
  isInService: Boolean,          // 是否为服务中用户
  isExecutiveCore: Boolean,      // 是否为铁三角成员
  isSuperuser: Boolean,          // 是否为超级管理员
  disableFlag: Boolean,          // 禁用状态（true=已禁用，false=正常）
  roles: Array<Role>,            // 关联角色列表
  orgs: Array<Organization>,     // 关联组织列表
  createdAt: DateTime,           // 创建时间
  updatedAt: DateTime            // 更新时间
}
```

### 用户状态说明
| 字段 | 类型 | 说明 | 业务含义 |
|------|------|------|----------|
| `disableFlag` | Boolean | 禁用状态 | true=用户被禁用无法登录，false=正常可登录 |
| `isInService` | Boolean | 服务状态 | true=服务中用户，false=非服务中用户 |
| `isExecutiveCore` | Boolean | 铁三角标识 | true=铁三角成员（项目经理、技术经理、产品经理），false=普通成员 |
| `isSuperuser` | Boolean | 超级管理员 | true=系统超级管理员，拥有所有权限，false=普通用户 |

## API 接口规范

### 1. 用户列表查询
```javascript
// GET /sm/users
getUserList(params)
```
**请求参数：**
```javascript
{
  pageNum: Number,      // 页码，默认1
  pageSize: Number,     // 每页条数，默认10
  code: String,         // 用户编码（模糊查询）
  username: String,     // 用户名（模糊查询）
  role: Number,         // 角色ID
  disableFlag: Boolean, // 禁用状态
  pageSort: String      // 排序（格式：FIELD:ORDER，如 ID:DESC）
}
```
**响应示例：**
```javascript
{
  data: {
    items: [
      {
        id: "uuid-1",
        username: "admin",
        nickname: "系统管理员",
        mobile: "+8613800138000",
        isInService: true,
        isExecutiveCore: false,
        isSuperuser: true,
        disableFlag: false,
        roleName: "超级管理员",
        createdAt: "2024-01-01T00:00:00Z"
      }
    ],
    total: 100
  }
}
```

### 2. 用户简单列表（用于下拉选择）
```javascript
// GET /sm/users/simple
getSimpleUserList(params)
```
**响应示例：**
```javascript
{
  data: {
    items: [
      { id: "uuid-1", username: "admin", nickname: "系统管理员" }
    ]
  }
}
```

### 3. 获取单个用户详情
```javascript
// GET /sm/users/{userId}
getUser(userId)
```

### 4. 新增用户
```javascript
// POST /sm/users
addUser(data)
```
**请求体：**
```javascript
{
  username: String,         // 必填
  nickname: String,         // 必填
  password: String,         // 必填，默认MOM888
  mobile: String,           // 可选，格式+86手机号
  isInService: Boolean,     // 可选，默认false
  isExecutiveCore: Boolean, // 可选，默认false
  isSuperuser: Boolean,     // 可选，默认false
  roles: Array<String>      // 可选，角色ID数组
}
```
**响应示例：**
```javascript
{
  data: {
    insertId: "uuid-new-user-id"  // 返回新创建用户ID
  }
}
```

### 5. 更新用户
```javascript
// PUT /sm/users/{userId}
updateUser(userId, data)
```

### 6. 部分更新用户（主要用于禁用/反禁用）
```javascript
// PATCH /sm/users/{id}
patchUser(data)
```
**请求体：**
```javascript
{
  id: String,              // 用户ID，支持批量（逗号分隔）
  disableFlag: Boolean,    // 禁用状态
  status: String           // 操作状态标识
}
```

### 7. 删除用户
```javascript
// DELETE /sm/users/{id}
delUser(id)
```
**注意：** id 支持批量删除（逗号分隔多个ID）

### 8. 获取当前登录用户信息
```javascript
// GET /sm/userinfo
getUserInfo()
```

### 9. 更新用户密码
```javascript
// POST /sm/user_password
updateUserPassword(data)
```

### 10. 重置用户密码为初始密码
```javascript
// PATCH /sm/user_password/{id}
resetUserPassword(id)
```
**说明：** 将用户密码重置为默认值 `MOM888`

## 权限验证流程

### 前端权限标识
系统使用基于权限码的前端权限控制：

| 操作 | 权限码 | 说明 |
|------|--------|------|
| 查看用户 | `SM.view_user` | 查看用户列表和详情 |
| 新增用户 | `SM.add_user` | 创建新用户 |
| 修改用户 | `SM.change_user` | 编辑用户信息 |
| 删除用户 | `SM.delete_user` | 删除用户 |

### 权限验证方法
```javascript
import { validatePerm } from '@/utils/index';

// 检查权限，无权限时自动提示并阻止操作
validatePerm('SM.add_user')

// 检查权限但仅返回布尔值，不自动提示
const hasPermission = validatePerm('SM.change_user', false)
```

### 用户状态与权限关系
1. **disableFlag=true** 的用户无法登录系统
2. **isSuperuser=true** 的用户拥有所有权限，不受权限码限制
3. 其他用户权限由其关联的角色（roles）决定

## 认证与授权区别说明

### 认证（Authentication）
- **目的**：验证用户身份
- **机制**：用户名+密码登录
- **存储**：Token 存储在 localStorage，key 为 `TOKEN_KEY`
- **流程**：
  1. 用户提交登录表单
  2. 调用 `/sm/auth/login` 接口
  3. 后端验证成功返回 token 和用户信息
  4. 前端存储 token 和用户信息到 Pinia Store 和 localStorage
- **相关文件**：
  - API：`src/api/auth.js`
  - Store：`src/stores/modules/user.js`

### 授权（Authorization）
- **目的**：控制用户可访问的资源
- **机制**：基于角色（RBAC）的权限控制
- **存储**：权限列表存储在 Pinia Store，key 为 `user.perms`
- **流程**：
  1. 登录成功后获取用户的权限列表（`authority.items`）
  2. 前端通过 `validatePerm()` 函数验证权限码
  3. 根据权限显示/隐藏按钮、菜单等 UI 元素
- **相关文件**：
  - API：`src/api/sm/user.js`
  - 工具：`src/utils/index.js` 中的 `validatePerm`

## 与其他模块关系

### 依赖关系
```
sm-user (用户模块)
  ├── 依赖 sm-role (角色模块) - 用户关联角色获取权限
  ├── 依赖 sm-organization (组织模块) - 用户所属组织
  ├── 依赖 sm-perm (权限模块) - 权限码定义
  └── 被所有业务模块依赖 - 所有模块都需要用户信息
```

### 数据流向
1. **登录流程**：auth.js → user Store → 存储 token 和用户信息
2. **权限获取**：登录响应 → authority.items → Store.user.perms
3. **权限验证**：业务组件 → validatePerm(permCode) → 显示/隐藏功能
4. **组织切换**：用户 Store.toggleOrg() → 更新当前组织 → 刷新页面

## 常见业务场景

### 场景1：用户新增流程
1. 点击"新增"按钮 → 跳转到 `/sm/user/add`
2. 初始化默认密码为 `MOM888`
3. 填写用户信息（账号、昵称、手机号等）
4. 保存成功后 → 跳转到编辑页面 `/sm/user/edit/{newId}/edit`
5. 自动返回新创建的用户ID（`insertId`）

### 场景2：用户编辑与查看
1. 编辑模式：`/sm/user/edit/{id}/edit` - 可修改用户信息
2. 查看模式：`/sm/user/edit/{id}/view` - 只读模式
3. 用户账号（username）在编辑模式下不可修改
4. 密码字段始终禁用，只能通过"重置密码"按钮重置

### 场景3：用户禁用/反禁用
1. 列表页批量操作：选中多个用户 → "业务操作" → "禁用/反禁用"
2. 编辑页单个操作：点击"业务操作" → "禁用/反禁用"
3. 操作完成后显示提示消息
4. 批量操作显示操作数量，单个操作仅显示操作成功

### 场景4：密码重置
1. 在编辑页点击密码输入框右侧的重置图标
2. 确认后调用 `resetUserPassword(id)` 接口
3. 密码重置为默认值 `MOM888`
4. 页面显示密码字段更新为 `MOM888`

### 场景5：权限控制
1. 按钮级权限：使用 `validatePerm('SM.xxx', false)` 控制 disabled 属性
2. 功能级权限：使用 `validatePerm('SM.xxx')` 在操作前验证
3. 超级管理员：`isSuperuser=true` 的用户不受权限限制

## 技术实现建议（Vue 3）

### 组件设计
1. **列表页** (`index.vue`)：LYTable + 搜索表单 + 操作按钮
2. **新增页** (`add.vue`)：复用 userRender 组件
3. **编辑页** (`edit.vue`)：复用 userRender 组件，传入禁用状态
4. **渲染组件** (`userRender.vue`)：表单渲染与验证逻辑

### 状态管理
- **用户状态**：Pinia Store (`stores/modules/user.js`)
- **权限列表**：`user.perms` 数组
- **登录状态**：`user.token` + localStorage

### 路由配置
```javascript
// 路由路径格式
/sm/user/add              // 新增用户
/sm/user/add/:addId       // 复制新增
/sm/user/edit/:id/:type   // 编辑/查看用户，type=edit|view
```

### 表单验证
```javascript
// 用户账号必填
username: [{ required: true, message: "用户账号不能为空", trigger: "change" }]

// 手机号格式校验（11位）
mobile: [{ pattern: /^1[3-9]\d{9}$/, message: "请输入正确的手机号" }]
```

### 数据处理
```javascript
// 手机号格式化：+8613800138000 <-> 13800138000
const formatMobile = (mobile) => {
  return mobile ? mobile.replace(/^\+86/, '') : ''
}

// 查询参数清理：移除空值
import { trimQueryParams } from '@/utils/trimParams'
const cleanParams = trimQueryParams(queryParams.value)
```

## 扩展设计策略

### 1. 用户字段扩展
新增用户属性时：
1. 在 `userRender.vue` 的表单中添加字段
2. 在 `add.vue` 和 `edit.vue` 的 formData 中添加初始值
3. 确保后端 API 支持新字段

### 2. 状态字段扩展
新增布尔状态字段时：
1. 在 formData 中添加字段
2. 在 userRender 中使用 `el-switch` 组件
3. 在 index.vue 的 tableColumns 中配置列显示
4. 在字典中配置显示文本（如果需要）

### 3. 权限扩展
新增用户操作权限时：
1. 在后端添加权限码
2. 在前端使用 `validatePerm('SM.new_perm')` 验证
3. 更新本文档的"权限验证流程"章节

## 演进方向

### 短期优化
1. **批量操作增强**：支持批量分配角色、批量移动组织
2. **导入导出**：支持用户信息的 Excel 导入导出
3. **操作日志**：记录用户管理操作审计日志
4. **密码策略**：支持自定义密码复杂度要求和过期策略

### 中期规划
1. **用户组**：支持用户分组管理，便于批量权限分配
2. **在线用户**：查看当前在线用户列表，支持强制下线
3. **登录历史**：记录用户登录日志，包括IP、时间、设备
4. **多因子认证**：支持手机验证码、邮箱验证码等二次认证

### 长期愿景
1. **SSO 集成**：支持企业单点登录（LDAP、OAuth2、SAML）
2. **用户画像**：基于用户行为构建用户画像，辅助权限推荐
3. **智能权限**：基于机器学习推荐用户角色和权限
4. **联邦身份**：支持跨系统的用户身份联邦

## 模块特有名词索引

当用户提到以下名词时，应该关联到本技能模块：

| 名词 | 关联说明 |
|------|----------|
| 用户账号 | username 字段，用户登录凭证 |
| 用户名称/昵称 | nickname 字段，用户显示名称 |
| 禁用状态 | disableFlag 字段，控制用户能否登录 |
| 铁三角 | isExecutiveCore 字段，标识核心团队成员 |
| 超级管理员 | isSuperuser 字段，拥有所有权限的用户 |
| 服务中用户 | isInService 字段，标识是否在服务状态 |
| 密码重置 | 将密码重置为默认值 MOM888 的操作 |
| +86 | 手机号前缀，中国区号 |
| MOM888 | 系统默认初始密码 |
| SM | 系统管理（System Management）模块 |
| validatePerm | 权限验证函数名 |
| TOKEN_KEY | Token 存储的 localStorage 键名 |
| USER_KEY | 用户信息存储的 localStorage 键名 |

## 文件索引

### 前端核心文件
- **API**：`src/api/sm/user.js` - 用户接口定义
- **API**：`src/api/auth.js` - 认证接口定义
- **Store**：`src/stores/modules/user.js` - 用户状态管理
- **页面**：`src/views/sm/user/index.vue` - 用户列表页
- **页面**：`src/views/sm/user/add.vue` - 用户新增页
- **页面**：`src/views/sm/user/edit.vue` - 用户编辑页
- **组件**：`src/views/sm/user/components/userRender.vue` - 用户表单渲染组件
- **路由**：`src/router/modules/sm.js` - SM 模块路由配置

### 相关模块文件
- **角色模块**：`src/api/sm/role.js`
- **组织模块**：`src/api/sm/org.js`
- **权限模块**：`src/api/sm/perm.js`
