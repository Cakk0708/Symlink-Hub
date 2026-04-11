# PMS Backend 项目地图

本文档完整描述项目结构、模块命名、模块别名，涉及项目关键词必须在本文中找到对应模块

## 架构设计

项目采用模块化设计，主要模块位于 `apps/` 目录下。
若模块提供了模块说明时必须阅读模块说明了解模块详细内容。

### SM（系统管理模块）

系统基础管理功能。

#### user
- 路径: `/sm/user`
- 别名: 用户管理/用户列表/用户/user
- 模块说明：`modules/SM.md`
- 接口文档：`api/sm-user.md`

#### user_preference
- 路径: `/sm/user-preference`
- 别名: 用户偏好/偏好设置/通知配置/user_preference
- 接口文档：`api/sm-user_preference.md`

#### auth
- 路径: `/sm/auth`
- 别名: 认证模块/鉴权/用户认证/用户鉴权
- 模块说明：`modules/sm-auth.md`
- 接口文档：`api/sm-auth.md`

##### auth_oauth
- 路径: `/sm/auth/oauth`
- 别名: OAuth认证
- 模块说明：`modules/sm-auth_oauth.md`

#### role
- 路径: `/sm/role`
- 别名: 角色管理
- 模块说明：`modules/sm-role.md`

#### approval
- 路径: `/sm/approval`
- 别名: 审批流管理/审批流

##### approval_flow
- 路径: `/sm/approval/flow`
- 别名: 审批流

##### approval_template
- 路径: `/sm/approval/template`
- 别名: 审批模板

#### permission
- 訡块说明: `modules/sm-perm.md`。
- 接口文档：`api/sm-permission.md`

#### messages
- 路径: `/sm/messages`
- 别名: 消息管理

#### code
- 路径: `/sm/code`
- 别名: 编码管理

#### route
- 路径: `/sm/route`
- 别名: 路由管理

#### system
- 路径: `/sm/system`
- 别名: 系统基础配置

#### version_control
- 路径: `/sm/version_control`
- 别名: 版本控制
- 模块说明：`modules/sm-version_control.md`

**路由前缀：** `/sm/`

### BDM（商务数据管理模块）

来自 PMS-admin 的商务数据管理。

#### customer
- 路径: `/bdm/customer`
- 别名: 客户管理/客户列表
- 模块说明：`modules/bdm-customer.md`
- 接口文档：`api/bdm-customer.md`

#### customer_model
- 路径: `/bdm/customer_model`
- 别名: 客户机型管理
- 模块说明：`modules/bdm-customer_model.md`

#### department
- 路径: `/bdm/department`
- 别名: 部门管理/部门列表
- 模块说明：`modules/bdm-department.md`
- 接口文档：`api/bdm-department.md`

#### staff
- 路径: `/bdm/staff`
- 别名: 员工管理/员工列表
- 模块说明：`modules/bdm-staff.md`
- 接口文档：`api/bdm-staff.md`

**路由前缀：** `/bdm/`

### PM（项目管理核心模块）

核心项目管理功能，包含项目全生命周期管理。

#### project

##### project
- 路径: `/pm/project`
- 别名: 项目管理/项目列表
- 模块说明：`modules/pm-project_list.md`
- 接口文档：`api/pm-project.md`

##### project_category
- 路径: `/pm/project/category`
- 别名: 项目分类
- 模块说明：`modules/pm-project_category.md`
- 接口文档：`api/pm-project_category.md`

##### project_folder
- 路径: `/pm/project/folder`
- 别名: 项目文件夹/文件管理
- 模块说明：`modules/pm-project_folder.md`
- 接口文档：`api/pm-project_folder.md`

##### project_follower
- 路径: `/pm/project/follower`
- 别名: 项目关注者
- 模块说明：`modules/pm-project_follower.md`
- 接口文档：`api/pm-project_follower.md`

#### nodelist

##### nodelist
- 路径: `/pm/nodelist`
- 别名: 节点列表管理
- 模块说明：`modules/pm-nodelist.md`
- 接口文档：`api/pm-nodelist.md`

##### nodelist_owner
- 路径: `/pm/nodelist/owner`
- 别名: 节点负责人管理/节点负责人/负责人列表
- 模块说明：`modules/pm-nodelist_owner.md`
- 接口文档：`api/pm-nodelist_owner.md`

##### nodelist_note
- 路径: `/pm/nodelist/note`
- 别名: 节点笔记/节点备注
- 模块说明：`modules/pm-nodelist_note.md`
- 接口文档：`api/pm-nodelist_note.md`

##### nodelist_deliverable
- 路径: `/pm/nodelist/deliverable`
- 别名: 节点交付物关联/节点交付物列表
- 模块说明：`modules/pm-nodelist_deliverable.md`
- 接口文档：`api/pm-nodelist.md`（作为节点详情接口的一部分返回）

#### review
- 路径: `/pm/review`
- 别名: 节点评审项管理/评审项列表/评审项/节点评审项
- 模块说明：`modules/pm-nodelist_review.md`
- 接口文档：`api/pm-nodelist_review.md`

#### deliverable

##### deliverable
- 路径: `/pm/deliverable`
- 别名: 交付物管理/交付物列表

##### deliverable_instance
- 路径: `/pm/deliverable/instance`
- 别名: 交付物实例/交付物列表
- 模块说明：`modules/pm-deliverable_instance.md`
- 接口文档：`api/pm-deliverable_instance.md`

##### deliverable_file
- 路径: `/pm/deliverable/file`
- 别名: 交付物文件上传/交付物上传
- 模块说明：`modules/pm-deliverable_file.md`
- 接口文档：`api/pm-deliverable_file.md`

##### deliverable_folder
- 路径: `/pm/deliverable/folder`
- 别名: 交付物文件夹/交付物文件管理
- 模块说明：`modules/pm-deliverable_folder.md`

##### deliverable_freeze
- 路径: `/pm/deliverable/freeze`
- 别名: 交付物冻结
- 模块说明：`modules/pm-deliverable_freeze.md`
- 接口文档：`api/pm-deliverable_freeze.md`

##### deliverable_evaluate
- 路径: `/pm/deliverable/evaluate`
- 别名: 交付物评价
- 模块说明：`modules/pm-deliverable_evaluate.md`

#### change
- 路径: `/pm/change`
- 别名: 项目设计变更流程/设计变更/项目变更
- 模块说明：`modules/pm-project_change.md`
- 接口文档：`api/pm-project_change.md`

#### pause
- 路径: `/pm/pause`
- 别名: 项目暂停申请/项目暂停
- 模块说明：`modules/pm-project_pause.md`
- 接口文档：`api/pm-project_pause.md`

#### continuation
- 路径: `/pm/continuation`
- 别名: 项目继续申请/项目继续
- 模块说明：`modules/pm-project_continuation.md`
- 接口文档：`api/pm-continuation.md`

#### log
- 路径: `/pm/log`
- 别名: 项目操作日志/项目日志/操作记录/操作日志
- 模块说明：`modules/pm-project_log.md`
- 接口文档：`api/pm-project_log.md`

#### evaluation
- 路径: `/pm/evaluation`
- 别名: 绩效评价/绩效

##### v2
- 路径: `/pm/evaluation/v2`
- 别名: 项目绩效2.0
- 接口文档：`api/pm-evaluation_v2.md`

##### v3/config 
- 路径: `/pm/evaluation/v3/config`
- 别名: 项目绩效3.0
- 接口文档: `api/pm-evaluation_v3_config.md`

##### v3/record
- 路径: `/pm/evaluation/v3/record`
- 别名: 评价记录
- 模块说明:
- 接口文档:

#### hardwares

##### hardwares
- 路径: `/pm/hardwares`
- 别名: 硬件模块

##### hardwares_config
- 路径: `/pm/hardwares/config`
- 别名: 硬件配置/配置清单
- 模块说明：`modules/pm-hardwares_config.md`
- 接口文档：`api/pm-project_hardware.md`

##### hardwares_deliverable
- 路径: `/pm/hardwares/deliverable`
- 别名: 硬件交付物/配置清单交付物/配置清单交付物实例
- 模块说明：`modules/pm-hardwares_deliverable.md`
- 接口文档：`api/pm-hardware_deliverable.md`

##### hardwares_reuse
- 路径: `/pm/hardwares/reuse`
- 别名: 硬件复用
- 模块说明：`modules/pm-hardware_reuse.md`
- 接口文档：`api/pm-hardware_reuse.md`

#### timeline
- 路径: `/pm/timeline`
- 别名: 项目时间线/时间线
- 模块说明：`modules/pm-timeline.md`
- 接口文档：`api/pm-timeline.md`

#### authority
- 路径: `/pm/authority`
- 别名: 权限验证/项目权限
- 模块说明：`modules/pm-authority.md`

**路由前缀：** `/pm/`

### PSC（项目设置配置模块）

来自 PMS-admin 的项目设置配置模块。

#### project

##### project
- 路径: `/psc/project`
- 别名: 项目模板/项目定义

##### project_template
- 路径: `/psc/project/template`
- 别名: 项目模板管理
- 模块说明：`modules/psc-project_template.md`
- 接口文档：`api/psc-project_template.md`

##### project_label
- 路径: `/psc/project/label`
- 别名: 项目标签配置/项目模板标签
- 模块说明：`modules/psc-project_label.md`
- 接口文档：`api/psc-project_template_label.md`

##### project_node
- 路径: `/psc/project/node`
- 别名: 项目模板节点映射

#### project_role
- 路径: `/psc/project_role`
- 别名: 项目角色设计/项目角色配置/项目角色管理
- 模块说明：`modules/psc-project_role.md`
- 接口文档：`api/psc-project_role.md`

#### node

##### node_definition
- 路径: `/psc/node/definition`
- 别名: 节点定义主模型/节点定义/节点模板
- 模块说明：`modules/psc-node_definition.md`
- 接口文档：`api/psc-node_definition.md`

##### node_deliverable
- 路径: `/psc/node/deliverable`
- 别名: 节点交付物关联

##### node_review
- 路径: `/psc/node/review`
- 别名: 节点评审项关联

#### deliverable

##### deliverable_definition
- 路径: `/psc/deliverable/definition`
- 别名: 交付物定义/交付物模板
- 模块说明：`modules/psc-deliverable_definition.md`
- 接口文档：`api/psc-deliverable_definition.md`

##### deliverable_template
- 路径: `/psc/deliverable/template`
- 别名: 飞书模板配置
- 模块说明：`modules/psc-deliverable_definition_template.md`

##### file_extension_type
- 路径: `/psc/deliverable/file_extension_type`
- 别名: 文件扩展名类型
- 模块说明：`modules/psc-file_extension_type.md`
- 接口文档：`api/psc-file_extension_type.md`

#### review_definition
- 路径: `/psc/review_definition`
- 别名: 评审项定义/评审项模板
- 模块说明：`modules/psc-review_definition.md`
- 接口文档：`api/psc-review_definition.md`

#### evaluation_config
- 路径: `/psc/evaluation_config`
- 别名: 项目评价配置
- 接口文档：`api/psc-evaluation_config.md`

#### pmconfig

##### pmconfig
- 路径: `/psc/pmconfig`
- 别名: 项目配置

##### pmconfig_category
- 路径: `/psc/pmconfig/category`
- 别名: 硬件分类
- 模块说明：`modules/psc-pmconfig_category.md`

##### pmconfig_hardware
- 路径: `/psc/pmconfig/hardware`
- 别名: 硬件信息/硬件规格
- 模块说明：`modules/psc-pmconfig_hardware.md`
- 接口文档：`api/psc-hardware_spec.md`

#### event
- 路径: `/psc/event`
- 别名: 事件定义

**路由前缀：** `/psc/`

### API（接口模块）

外部接口和飞书机器人回调处理。

#### callback

##### callback
- 路径: `/api/callback`
- 别名: 飞书回调处理模块/飞书回调
- 模块说明：`modules/api-callback.md`

##### callback_views
- 路径: `/api/callback/views.py`
- 别名: 回调视图入口

##### callback_handlers
- 路径: `/api/callback/handlers/`
- 别名: 回调处理器

##### callback_services
- 路径: `/api/callback/services/`
- 别名: 业务服务层

##### callback_utils
- 路径: `/api/callback/utils/`
- 别名: 工具层

##### callback_constants
- 路径: `/api/callback/constants.py`
- 别名: 常量定义

#### api_views
- 路径: `/api/views.py`
- 别名: 辅助视图（定时任务触发、白名单消息）

#### api_tasks
- 路径: `/api/tasks.py`
- 别名: API异步任务

#### api_feishu
- 路径: `/api/feishu.py`
- 别名: 飞书API封装

**回调接口：**
- `POST /api/msg` - 机器人消息回调
- `POST /api/card` - 卡片交互回调
- `POST /api/event` - 事件回调

##### project（遗留模块）

旧的项目相关功能，正在迁移到 PM 模块。

**路由前缀：** `/web/`、`/project/`

### utils（工具模块）

飞书开放平台 API 封装和公共工具。

#### openapi_feishu
- 路径: `/utils/openapi/feishu/`
- 别名: 飞书开放平台 API 管理器/飞书API
- 模块说明：`modules/utils-openapi-feishu.md`

##### feishu_token_manager
- 路径: `/utils/openapi/feishu/token_manager.py`
- 别名: FeishuTokenManager（Token 管理）

##### feishu_auth_manager
- 路径: `/utils/openapi/feishu/auth_manager.py`
- 别名: FeishuAuthManager（认证管理）

##### feishu_user_manager
- 路径: `/utils/openapi/feishu/user_manager.py`
- 别名: FeishuUserManager（用户管理）

##### feishu_message_manager
- 路径: `/utils/openapi/feishu/message_manager.py`
- 别名: FeishuMessageManager（消息管理）

##### feishu_file_manager
- 路径: `/utils/openapi/feishu/file_manager.py`
- 别名: FeishuFileManager（文件管理）

##### feishu_sheet_manager
- 路径: `/utils/openapi/feishu/sheet_manager.py`
- 别名: FeishuSheetManager（表格管理）

#### api_security
- 路径: `/utils/api_security/`
- 别名: API 安全

#### serializer
- 路径: `/utils/serializer/`
- 别名: 序列化工具

#### api_utils
- 路径: `/utils/api_utils.py`
- 别名: API 工具

#### conversion
- 路径: `/utils/conversion.py`
- 别名: 数据转换

#### date
- 路径: `/utils/date.py`
- 别名: 时间处理

#### redis
- 路径: `/utils/redis.py`
- 别名: Redis 工具

#### user
- 路径: `/utils/user.py`
- 别名: 用户工具

