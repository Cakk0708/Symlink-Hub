# PMS Admin Frontend 项目地图

> 本文档提供项目的高层次导航视图，详细模块说明请查看对应的模块文档。

---

## 快速导航

| 文档 | 说明 |
|------|------|
| [CLAUDE.md](/CLAUDE.md) | 项目开发指南和技术栈说明 |
| [modules/](./modules/) | 各业务模块详细文档 |
| [components/](./components/) | 公共组件详细文档 |

---

## 业务模块全景

### SM（系统管理模块）

#### Auth
- 别名: `用户鉴权/用户登陆`
- 接口文档: `../backend/.claude/docs/api/sm-auth.md`

#### User
- 路径: `sm/user`
- 别名: `用户管理/用户列表`
- 模块说明: `modules/sm-user.md`
- 接口文档: `../backend/.claude/docs/api/sm-user.md`

#### Role
- 路径: `sm/role`
- 别名: `用户角色/角色`
- 模块说明: `modules/sm-role.md`
- 接口文档: `../backend/.claude/docs/api/sm-role.md`

#### Perm
- 路径: `sm/perm`
- 别名: `业务授权/权限配置/权限列表`
- 模块说明: 
- 接口文档: `../backend/.claude/docs/api/sm-permission.md`
- 元素布局: `layouts/perm-list.md`

### BDM（基础数据管理模块）

#### Customer
- 路径: `bdm/customer`
- 别名: `客户列表/客户模块/客户管理`
- 模块说明: `modules/bdm-customer.md`
- 接口文档: `../backend/.claude/docs/api/bdm-customer.md`

#### Department
- 路径: `bdm/department`
- 别名: `部门管理`
- 模块说明: `modules/bdm-department.md`
- 接口文档: `../backend/.claude/docs/api/bdm-department.md`

#### Staff
- 路径: `bdm/staff`
- 别名: `员工管理`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/bdm-staff.md` 

### PSC（项目配置模块）

#### ProjectTemplate
- 路径: `psc/projecttemplate`
- 别名: `项目模板`
- 模块说明: `modules/psc-project_template.md`
- 接口文档: `../backend/.claude/docs/api/psc-project_template.md`

#### NodeDefinition
- 路径: `psc/nodedefinition`
- 别名: `节点定义`
- 模块说明: `modules/psc-node_definition.md`
- 接口文档: `../backend/.claude/docs/api/psc-node_definition.md` 

#### DeliverableDefinition
- 路径: `psc/deliverabledefinition`
- 别名: `交付物定义`
- 模块说明: `modules/psc-deliverable_definition.md`
- 接口文档: `../backend/.claude/docs/api/psc-deliverable_definition.md`

#### ReviewDefinition
- 路径: `psc/reviewdefinition`
- 别名: `评审定义`
- 模块说明: `modules/psc-review_definition.md`
- 接口文档: `../backend/.claude/docs/api/psc-project_template.md`

#### EventDefinition
- 路径: `psc/eventdefinition`
- 别名: `事件定义`
- 模块说明:
- 接口文档:

#### FileExtensionType
- 路径: `psc/file_extension_type`
- 别名: `文件扩展类型`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/psc-file_extension_type.md`

#### HardwareSpec
- 路径: `psc/hardware_spec`
- 别名: `硬件规格`
- 模块说明: `modules/psc-hardware_spec.md`
- 接口文档: `../backend/.claude/docs/api/psc-ehardware_spec.md`

#### EvaluationConfig
- 路径: `psc/evaluationconfig`
- 别名: `项目评价`
- 模块说明: `modules/psc-evaluation_config.md`
- 接口文档:

#### ProjectRole
- 路径: `psc/projectrole`
- 别名: `项目角色`
- 模块说明: `modules/psc-project_role.md`
- 接口文档: `../backend/.claude/docs/api/psc-project_role.md`

#### ProjectTemplateLabel
- 路径: `psc/project_template_label`
- 别名: `项目模板标签`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/psc-project_template_label.md`


---

### PM（项目管理模块）

#### Project
- 路径: `pm/project`
- 别名: `项目/项目管理`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project.md`

#### NodeList
- 路径: `pm/nodelist`
- 别名: `节点列表`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-nodelist.md`

#### NodeListOwner
- 路径: `pm/nodelist_owner`
- 别名: `节点负责人`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-nodelist_owner.md`

#### NodeListReview
- 路径: `pm/nodelist_review`
- 别名: `节点评审`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-nodelist_review.md`

#### NodeListNote
- 路径: `pm/nodelist_note`
- 别名: `节点备注`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-nodelist_note.md`

#### DeliverableInstance
- 路径: `pm/deliverable_instance`
- 别名: `交付物实例`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-deliverable_instance.md`

#### DeliverableFile
- 路径: `pm/deliverable_file`
- 别名: `交付物文件`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-deliverable_file.md`

#### DeliverableFreeze
- 路径: `pm/deliverable_freeze`
- 别名: `交付物冻结`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-deliverable_freeze.md`

#### HardwareDeliverable
- 路径: `pm/hardware_deliverable`
- 别名: `硬件交付物`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-hardware_deliverable.md`

#### ProjectHardware
- 路径: `pm/project_hardware`
- 别名: `项目硬件`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_hardware.md`

#### EvaluationV2
- 路径: `pm/evaluation_v2`
- 别名: `项目评价v2`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-evaluation_v2.md`

#### EvaluationV3Config
- 路径: `pm/evaluation_v3_config`
- 别名: `项目评价v3配置`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-evaluation_v3_config.md`

#### ProjectCategory
- 路径: `pm/project_category`
- 别名: `项目分类`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_category.md`

#### ProjectChange
- 路径: `pm/project_change`
- 别名: `项目变更`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_change.md`

#### ProjectFolder
- 路径: `pm/project_folder`
- 别名: `项目文件夹`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_folder.md`

#### ProjectFollower
- 路径: `pm/project_follower`
- 别名: `项目关注者`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_follower.md`

#### ProjectLog
- 路径: `pm/project_log`
- 别名: `项目日志`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_log.md`

#### ProjectPause
- 路径: `pm/project_pause`
- 别名: `项目暂停`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_pause.md`

#### ProjectStatus
- 路径: `pm/project_status`
- 别名: `项目状态`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-project_status.md`

#### Continuation
- 路径: `pm/continuation`
- 别名: `项目延续`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-continuation.md`

#### Order
- 路径: `pm/order`
- 别名: `项目订单`
- 模块说明:
- 接口文档: `../backend/.claude/docs/api/pm-order.md`


---
