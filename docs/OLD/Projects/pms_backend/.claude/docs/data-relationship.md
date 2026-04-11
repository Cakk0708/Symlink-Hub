# PMS Backend 数据模型关系地图

## 数据模型关系

### 核心模型关系图

```
User (SM/User)
├── UserFeishu (飞书Token扩展)
├── Project_List (创建的项目)
├── Project_List (负责的项目)
├── Project_Node_Owners (节点负责人关联)
└── UserDepartment (部门关联)

Project_List (PM/project)
├── customer → Customer (BDM)
├── model → CustomerModel (BDM)
├── template → ProjectTemplateVersion (PSC)
├── project_nodes → Project_Node []
├── creator → User (SM)
├── owner → User (SM)
└── approvals → Approval (SM) [GenericRelation]

Project_change (PM/change)
├── project → Project_List (项目)
├── applicant → User (SM) (申请人)
├── approval → Approval (SM) (审批流)
└── 通过 GenericRelation 关联回 Project_List

Project_Node (PM/nodelist)
├── list → Project_List (项目)
├── node_definition → NodeDefinitionVersion (PSC)
├── parent → Project_Node (父节点)
├── children → Project_Node [] (子节点)
├── node_owners → Project_Node_Owners []
└── node_definition 通过关联获取：
    ├── project_role → ProjectRole (PSC)
    ├── feature_mappings → NodeDefinitionFeatureMapping []
    ├── deliverable_mappings → 节点交付物关联
    └── review_mappings → 节点评审项关联

NodeDefinition (PSC/node/definition)
└── versions → NodeDefinitionVersion []

NodeDefinitionVersion (PSC/node/definition)
├── node_definition → NodeDefinition
├── project_role → ProjectRole (PSC)
├── default_owner → User (SM)
├── feature_mappings → NodeDefinitionFeatureMapping []
├── 交付物关联（通过中间表）
└── 评审项关联（通过中间表）

DeliverableDefinition (PSC/deliverable/definition)
└── versions → DeliverableDefinitionVersion []

DeliverableDefinitionVersion (PSC/deliverable/definition)
├── deliverable_definition → DeliverableDefinition
├── allowed_file_extensions → FileExtensionType []
└── created_by → User (SM)

ProjectRole (PSC/project_role)
├── node_definition_versions → NodeDefinitionVersion []
└── evaluation_config → EvaluationConfig []

ProjectTemplate (PSC/project/template)
└── versions → ProjectTemplateVersion []

ProjectTemplateVersion (PSC/project/template)
├── project_template → ProjectTemplate
└── node_mappings → ProjectTemplateNodeMapping []

Approval (SM/approval/flow)
├── initiator → User (SM) (发起人)
├── template → Template (审批模板)
├── template_current_step → Template_Step (当前步骤)
├── approval_approvers → Approval_Approver [] (审批人列表)
├── approval_ccs → Approval_Cc [] (抄送人列表)
└── content_object → GenericForeignKey (关联对象：Project_change、Project_pause、Project_continuation 等)

Approval_Approver (SM/approval/flow)
├── approval → Approval
├── template_step → Template_Step
├── user → User (SM) (审批人)
└── messages → Message [] [GenericRelation]

Template (SM/approval/template)
├── template_step → Template_Step []
└── 通过审批模板配置审批流程
```
