# SM 模块

## 职责
系统管理模块，提供用户、认证、角色、权限、审批流、消息等基础系统功能。

## 模块位置
`apps/SM/`

## 子模块说明

### user - 用户管理
用户生命周期管理：创建、更新、查询、密码管理。

#### 数据模型
- `User` - 统一用户模型（继承 AbstractUser）
  - 支持飞书 OAuth 登录（通过 UserFeishu.open_id 关联）
  - 支持用户名/密码登录
  - 关键字段：username, nickname, mobile, email, avatar, is_superuser, is_active, is_in_service
- `UserFeishu` - 飞书用户信息存储
  - 存储 open_id, access_token, refresh_token

#### 序列化器
- `ListSerializer` - 用户列表序列化器（只读）
- `WriteSerializer` - 用户创建/更新序列化器
  - 支持字段：username, nickname, email, mobile, avatar, isSuperuser, is_active, is_executive_core, disable_flag, roles
  - **权限验证**：`isSuperuser` 字段只有超级用户可以设置
- `SimpleSerializer` - 用户简化序列化器（id, code, name）
- `ChangePasswordSerializer` - 修改密码序列化器
- `ResetPasswordSerializer` - 重置密码序列化器（仅超级用户）

#### URL 路由
```
GET    /sm/user/                    - 用户列表
POST   /sm/user/                    - 创建用户
GET    /sm/user/<int:id>            - 用户详情
PUT    /sm/user/<int:id>            - 更新用户
GET    /sm/user/enums               - 用户枚举
GET    /sm/user/simple              - 用户简化列表
POST   /sm/user/change-password     - 修改当前用户密码
PATCH  /sm/user/<int:id>/reset-password - 重置指定用户密码（仅超级用户）
```

#### 业务规则
- 创建用户时使用初始密码（配置项 `INITIAL_PASSWORD`）
- 手机号自动补充 +86 前缀
- 用户名、邮箱、手机号唯一性校验
- 更新用户时只允许修改特定字段（nickname, email, mobile, avatar, is_executive_core, roles, password）
- `isSuperuser` 字段只有超级用户可以设置为 true

### auth - 认证模块
飞书 OAuth 认证、用户登录。

### role - 角色管理
角色定义与分配。

### approval - 审批流管理
审批模板、审批流程。

### permission - 权限管理
权限映射与配置，提供三 Tab 权限管理（后台管理/项目管理/交付物管理）。

**模块说明：** `modules/sm-perm.md`
**接口文档：** `api/sm-permission.md`

### messages - 消息管理
消息发送与管理。

### code - 编码管理
编码规则（已重构为包结构）。

### route - 路由管理
路由配置。

### system - 系统配置
系统基础配置。

### version_control - 版本控制
版本管理。

## 关联模块
- `PM` - 项目管理模块（创建者、负责人等）
- `PSC` - 项目设置配置模块（项目模板等）
- `BDM` - 商务数据管理模块（部门关联）

## 依赖
- `utils.openapi.feishu.UserFeishuManager` - 飞书用户信息获取
- `utils.openapi.feishu.FeishuAuthManager` - 飞书认证管理
- `django.contrib.auth.models.Group` - Django 权限组（角色）

## 禁止事项
- 禁止直接访问 `user.open_id`，使用 `get_user_feishu_open_id(user)` 工具函数
- 禁止在 views.py 里直接操作用户密码（使用序列化器）
- 禁止非超级用户设置 `isSuperuser=true`

## 变更记录
### 2026-04-06
- 权限模块重构：PermissionConfig` → 映射表架构，删除 `PermissionConfig`、 `DeliverablePermission` 模型，新增 `ProjectPermissionMapping` + `DeliverablePermissionMapping`
- 权限模块文档更新
