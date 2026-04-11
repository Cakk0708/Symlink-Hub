# PM 项目设计变更模块专家 (PM-project_change)

## 简介

本模块是 PM 项目管理系统中**项目设计变更**的核心功能模块，负责处理项目进行中因客户需求变动、问题修复、技术升级等原因引发的项目变更申请、审批流程及状态管理。

模块位置：`apps.PM.change`


## 模块定位

### 核心职责
- **变更申请管理**：处理项目设计变更的发起、审批、拒绝、取消等全生命周期
- **变更范围控制**：支持按硬件/软件部件选择变更范围，或按具体节点选择变更范围
- **负责人配置**：支持为变更说明、变更确认节点配置专门负责人
- **审批流集成**：与 SM 模块的审批流深度集成，实现变更审批自动化
- **状态同步**：变更审批通过后自动将项目状态切换为"变更中"（state=3）

### 模块边界
| 职责 | 归属模块 | 说明 |
|------|---------|------|
| 项目设计变更申请 | 本模块 | 客户需求变动、技术升级等 |
| 项目基础信息变更 | 本模块 | 项目名称、描述等信息修改 |
| 项目暂停/继续 | `PM.pause` / `PM.continuation` | 项目临时暂停和恢复 |
| 节点回滚变更 | `PM.nodelist` | 节点状态回滚 |


## 核心数据模型

### Project_change (项目变更表)

**表名**：`project_change`

**核心字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `project` | FK(Project_List) | 关联项目 |
| `applicant` | FK(SM.User) | 申请人 |
| `approval` | FK(SM.Approval) | 关联审批流（可为空） |
| `reason` | TextField | 变更原因 |
| `parts` | TextField | 变更部件（逗号分隔："1,2" 表示硬件+软件） |
| `parts_owners` | TextField/JSON | 变更部件对应的负责人配置 |
| `status` | CharField | 状态：PENDING/APPROVED/REJECTED/CANCEL |
| `category` | CharField | 变更类型枚举 |
| `nodes` | TextField | 变更节点列表（逗号分隔的节点ID） |
| `nodes_owners` | JSONField | 变更节点的负责人配置 |
| `create_time` | DateTimeField | 创建时间 |
| `complete_time` | DateTimeField | 完成时间 |

**重要方法**：
```python
def get_change_parts_owners(self, part, node_rule_id):
    """
    获取指定部件和节点规则的负责人ID列表
    :param part: 部件编号 ('1' 硬件, '2' 软件)
    :param node_rule_id: 节点规则ID (如 10616 硬件变更说明)
    :return: 用户ID列表
    """
```

**状态缓存机制**：
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._original_status = self.status if self.pk else None
```
使用 `_original_status` 缓存旧状态，在信号处理器中判断状态是否发生变化。


## 变更类型枚举 (ChangeType)

**位置**：`apps.PM.change.enums.Choices.ChangeType`

| 枚举值 | 标签 | 是否可选范围 | 说明 |
|--------|------|-------------|------|
| `BASIC_INFO_CHANGE` | 基础信息变更 | 否 | 仅修改项目基础信息 |
| `REQUIREMENT_CHANGE` | 客户需求变动 | 是 | 默认选择，需选择变更范围 |
| `ISSUE_FIX` | 问题修复 | 是 | 需选择变更范围 |
| `TECH_UPGRADE` | 技术升级 | 是 | 需选择变更范围 |

**属性方法**：
- `is_scope_selectable`：判断该类型是否可选择变更范围
- `is_default`：判断是否为默认选择（REQUIREMENT_CHANGE）


## 硬件/软件变更节点配置

### 硬件变更 (HWChange)
| 枚举值 | 标签 | 对应节点规则ID |
|--------|------|---------------|
| `hw_desc` | 变更说明(H) | 10616 |
| `hw_confirm` | 变更确认(H) | 10614 |

### 软件变更 (SWChange)
| 枚举值 | 标签 | 对应节点规则ID |
|--------|------|---------------|
| `sw_desc` | 变更说明(S) | 10625 |
| `sw_confirm` | 变更确认(S) | 10623 |

### 节点负责人配置映射 (node_owner_config_map)
根据项目父节点规则ID，配置需要填写的负责人字段：

| 父节点规则ID | 适用场景 | 配置 |
|-------------|---------|------|
| 10301 | 硬件设计 | HWChange (hw_desc + hw_confirm) |
| 10401 | 硬件开发 | HWChange (hw_desc + hw_confirm) |
| 10302 | 软件设计 | SWChange (sw_desc + sw_confirm) |
| 10402 | 软件开发 | SWChange (sw_desc + sw_confirm) |

### 自动创建节点映射 (create_node_mapping)
当选择某个子节点作为变更范围时，自动创建对应的变更说明和变更确认节点：

| 父节点规则ID | 自动创建的节点规则ID |
|-------------|---------------------|
| 10301 | [10614, 10616] |
| 10401 | [10614, 10616] |
| 10302 | [10623, 10625] |
| 10402 | [10623, 10625] |


## 信号处理器

**位置**：`apps.PM.change.signals`

### handle_change_approval (post_save)

**触发条件**：Project_change 模型保存（创建或状态变化）

**处理逻辑**：

1. **创建时自动创建审批流** (`created=True`)
   - 调用 `_create_approval_flow(change_instance)` 创建审批流
   - 从审批模板获取审批人和抄送人配置
   - 创建 `Approval`、`Approval_Approver`、`Approval_Cc` 记录
   - 将审批流关联到变更实例

2. **审批通过 (PENDING → APPROVED)**

   根据 `category` 类型分别处理：

   a) **category = None**（旧版本兼容）
   - 将项目状态设为 3（变更中）
   - 根据 `parts` 字段（部件列表 "1,2"）获取负责人
   - 发送通知给部件负责人

   b) **category = BASIC_INFO_CHANGE**（基础信息变更）
   - 记录日志，不改变项目状态
   - 发送通知给申请人

   c) **其他类型**（需求变动/问题修复/技术升级）
   - 将项目状态设为 3（变更中）
   - 从 `nodes_owners` 中提取硬件变更说明(10616)、软件变更说明(10625)的负责人
   - 发送通知给相关负责人

3. **审批拒绝 (PENDING → REJECTED)**
   - 发送拒绝通知给申请人

### _create_approval_flow (内部函数)

**功能**：创建审批流

**处理流程**：
1. 获取审批模板（`settings.CUSTOM_SETTING['approval']['template']['project_change']['code']`）
2. 创建 `Approval` 记录
3. 遍历审批模板的所有步骤，创建：
   - `Approval_Approver` 记录（审批人）
   - `Approval_Cc` 记录（抄送人）
4. 第一步骤的审批人状态设为 `IN_PROGRESS`
5. 将审批流关联到变更实例

### _event_create_message (内部函数)

**功能**：创建审批通知消息

**参数**：
- `classify`：消息类型（APPROVED/REJECTED）
- `receiver_user_list`：接收用户列表

### _get_change_owners (内部函数)

**功能**：获取发起变更时设置的变更说明、变更确认的负责人

**参数**：
- `project_change_instance`：项目变更实例
- `part`：部件编号（'1' 硬件，'2' 软件）
- `node_rule_id`：节点规则ID（兼容旧代码）

**返回**：用户实例列表


## API 接口

### 1. 发起项目变更（旧版本兼容）

**端点**：`POST /pm/change/{project_id}`

**请求体**：
```json
{
  "project_id": 123,
  "parts": "1,2",
  "reason": "客户需求变更",
  "hw_desc": [user_id1, user_id2],
  "hw_confirm": [user_id3],
  "sw_desc": [user_id4],
  "sw_confirm": [user_id5]
}
```

**验证规则**：
- 项目状态必须为已完成（state=2）
- 项目不能已处于变更中（state=3）
- 不能有待审批的变更申请
- 短时间内防止重复提交（60秒缓存）

**响应**：
```json
{
  "msg": "success",
  "data": {
    "project": {
      "state": 3  // 变更为变更中状态
    }
  }
}
```

### 2. 获取项目变更枚举配置

**端点**：`GET /pm/change/enums/{project_id}`

**响应**：
```json
{
  "msg": "success",
  "data": {
    "projectId": 123,
    "changeTypes": [
      {
        "value": "BASIC_INFO_CHANGE",
        "label": "基础信息变更",
        "isScopeSelectable": false,
        "isDefault": false
      },
      {
        "value": "REQUIREMENT_CHANGE",
        "label": "客户需求变动",
        "isScopeSelectable": true,
        "isDefault": true
      }
    ],
    "scopes": [
      {
        "id": node_id,
        "name": "硬件设计",
        "subItems": [
          {
            "id": child_node_id,
            "name": "原理图设计",
            "userConfigs": [
              {
                "value": "hw_desc",
                "label": "变更说明(H)",
                "required": true,
                "multiple": true,
                "disabled": false
              },
              {
                "value": "hw_confirm",
                "label": "变更确认(H)",
                "required": true,
                "multiple": true,
                "disabled": false
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 3. 发起项目变更（新版本）

**端点**：`POST /pm/change/views/{project_id}`

**请求体**：
```json
{
  "projectId": 123,
  "reason": "客户需求变动",
  "changeTypes": "REQUIREMENT_CHANGE",
  "subItems": [node_id1, node_id2],
  "userConfigs": {
    "hw_desc": [user_id1, user_id2],
    "hw_confirm": [user_id3],
    "sw_desc": [user_id4],
    "sw_confirm": [user_id5]
  }
}
```

### 4. 获取项目变更记录

**端点**：`GET /pm/change/views/{project_id}`

**响应**：
```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "reason": "客户需求变动",
      "category": "REQUIREMENT_CHANGE",
      "type": "客户需求变动",
      "createTime": "2026-03-07",
      "scope": "硬件设计: 原理图设计、PCB设计",
      "applicant": {
        "id": 1,
        "name": "张三",
        "avatar": "https://..."
      }
    }
  ]
}
```


## 权限验证流程

本模块**不直接处理权限验证**，权限验证通过以下方式实现：

1. **用户认证**：通过 `utils.user.UserHelper.setup_request_userinfo()` 从请求中获取用户信息
2. **序列化器验证**：在 `validate()` 方法中进行业务规则验证
3. **审批流权限**：由 SM 模块的审批流系统负责审批权限控制


## 与其他模块关系

### 依赖模块

| 模块 | 依赖方式 | 说明 |
|------|---------|------|
| `SM.Approval` | 外键关联 | 每个变更申请关联一个审批流 |
| `SM.User` | 外键关联 | 申请人和负责人 |
| `SM.Message` | 信号触发 | 审批结果通过消息通知 |
| `PM.Project_List` | 外键关联 | 变更所属项目 |
| `PM.Project_Node` | 关联查询 | 变更范围节点 |

### 被依赖模块

| 模块 | 依赖方式 | 说明 |
|------|---------|------|
| `PM.signals` | 信号导入 | 导入本模块信号处理器 |
| `SM.approval.flow.signals` | 信号触发 | `handle_new_approval_approver` 监听审批人状态变化，创建审批消息 |
| `SM.approval.flow.signals` | 工具函数 | `get_user_feishu_open_id(user)` 安全获取用户飞书 open_id |


## 节点定义模型迁移

### 旧方案（已废弃）

使用 `node_rule` 关联到节点规则表：
- `node.rule_id` - 节点规则ID（硬编码）
- `node.rule.parent_id` - 父节点的规则ID
- 排除条件：`exclude(node_rule__rule_id__in=[10614, 10616, 10623, 10625])`

### 新方案（当前使用）

使用 `node_definition` 关联到节点定义表：
- `node.node_definition` - 节点定义版本
- `node.parent_id` - 父节点的ID（直接关联）
- 排除条件：`exclude(node_definition__feature_mappings__feature_code__in=['CHANGE_NOTE', 'CHANGE_CONFIRM'])`

### 功能配置（Feature Mappings）

通过 `NodeDefinitionFeatureMapping` 表存储节点功能配置：

| 功能代码 | 说明 | 排除原因 |
|---------|------|---------|
| `CHANGE_NOTE` | 变更说明 | 变更说明节点不参与变更范围选择 |
| `CHANGE_CONFIRM` | 变更确认 | 变更确认节点不参与变更范围选择 |

### 迁移注意事项

1. **兼容属性**：`NodeDefinitionVersion` 提供了兼容属性（如 `rule_id`、`parent_id`），但这些仅用于兼容旧代码
2. **新代码应使用**：
   - `node.node_definition` 而非 `node.node_rule`
   - `node.parent_id` 而非 `node_definition.parent_id`
   - `node.id` 作为唯一标识而非 `node_definition.rule_id`
3. **父子关系**：使用 `node.parent` 直接关联父节点，而非通过 `node_definition`


## 常见业务场景

### 场景1：客户需求变动（硬件+软件）

1. 用户选择变更类型为"客户需求变动"
2. 选择变更范围：硬件设计下的原理图设计、软件设计下的代码开发
3. 配置负责人：
   - 硬件变更说明：工程师A、工程师B
   - 硬件变更确认：工程师C
   - 软件变更说明：工程师D
   - 软件变更确认：工程师E
4. 提交后自动创建审批流
5. 审批通过后：
   - 项目状态变为"变更中"（state=3）
   - 自动创建变更说明/变更确认节点
   - 向配置的负责人发送通知

### 场景2：基础信息变更

1. 用户选择变更类型为"基础信息变更"
2. 只需填写变更原因，无需选择变更范围
3. 审批通过后仅记录日志，不改变项目状态

### 场景3：问题修复（单节点）

1. 用户选择变更类型为"问题修复"
2. 选择具体的问题节点
3. 仅配置该节点相关的负责人
4. 审批通过后项目进入变更状态


## 技术实现建议

### 序列化器设计

1. **serializerProjectChange**：旧版本兼容，使用 `parts` + `parts_owners` 方式
2. **ChangeDetailsSerializer**：新版本，使用 `category` + `nodes` + `nodes_owners` 方式
   - `create()` 方法：创建 Project_change 实例
   - **不再创建审批流**：审批流由信号处理器 `handle_change_approval` 自动创建
3. **ChangeListSerializer**：变更记录列表展示，包含变更范围格式化

### 工具函数

**位置**：`apps.PM.change.utils`

| 函数 | 说明 |
|------|------|
| `construct_project_change_scopes(project_instance)` | 构建项目可选的变更范围树形结构 |
| `get_project_change_scope(node_ids)` | 获取项目已选的变更范围（格式化字符串） |
| `get_project_change_scope_list_for_feishu(change_instance)` | 获取变更范围用于飞书卡片展示 |

**变更范围构建逻辑（`construct_project_change_scopes`）**：

1. 获取项目节点，排除：
   - 里程碑节点（`node_definition.category='MILESTONE'`）
   - 包含 `CHANGE_NOTE`、`CHANGE_CONFIRM` 功能的节点
2. 基于节点的 `parent` 关系组织父子节点：
   - 有 `parent_id` 的为子节点
   - 没有 `parent_id` 的为父节点
3. 返回树形结构：`[{id, name, subItems: [{id, name}]}]`

### 状态管理

- 使用 `_original_status` 缓存机制在模型 `__init__` 中保存旧状态
- 在信号处理器中通过对比 `_original_status` 和当前状态判断是否发生变化

### 事务处理

- 创建变更申请和审批流时使用 `transaction.atomic()` 确保数据一致性
- 缓存机制防止短时间内重复提交（60秒）


## 用户 open_id 访问注意事项

### 问题背景

`User.open_id` 属性实现有问题：
- 访问 `self.user_feishu` 时会抛出 `DoesNotExist` 异常
- 未来多端情况下 `open_id` 会随不同端变化，不应作为 User 的通用属性

### 解决方案

**禁止直接访问 `user.open_id`**，应使用工具函数：

```python
# apps/SM/approval/flow/signals.py
def get_user_feishu_open_id(user):
    """
    获取用户的飞书 open_id

    TODO: 未来删除 User.open_id 属性后，需要重构 open_id 获取逻辑
    多端情况下 open_id 会随不同端变化，应从上下文或配置中获取
    """
    try:
        return user.user_feishu.open_id
    except User.user_feishu.RelatedObjectDoesNotExist:
        return None
```

### 相关代码

以下文件中已添加 TODO 标签，等待重构：
- `apps/SM/messages/signals.py`
- `apps/SM/messages/serializers.py`
- `apps/PM/nodelist/utils.py`
- `apps/PM/deliverable/instance/serializers.py`


## 扩展设计策略

### 添加新的变更类型

1. 在 `Choices.ChangeType` 枚举中添加新值
2. 设置 `is_scope_selectable` 属性
3. 在信号处理器的 `handle_change_approval` 中添加对应的处理逻辑

### 添加新的变更节点类型

1. 在 `Choices.HWChange` 或 `Choices.SWChange` 中添加新枚举值
2. 更新 `node_mapping` 映射关系
3. 更新 `node_owner_config_map` 配置
4. 更新 `create_node_mapping` 配置

### 支持更多审批流模板

在 `settings.CUSTOM_SETTING['approval']['template']` 中添加新的模板配置，并在序列化器中引用。


## 演进方向 (Future Evolution)

### 短期优化

1. **API 统一**：逐步迁移到新版本 API，废弃旧版本的 `parts` 方式
2. **权限细化**：添加变更申请的发起权限控制
3. **通知优化**：支持更灵活的通知配置

### 中期规划

1. **变更版本管理**：支持变更的版本回溯和对比
2. **变更影响分析**：自动分析变更对项目进度、成本的影响
3. **变更模板**：支持常用变更场景的模板化

### 长期愿景

1. **智能变更建议**：基于历史数据提供变更处理建议
2. **变更流程可视化**：可视化展示变更审批流程和状态
3. **跨项目变更**：支持批量项目的统一变更


## 模块特有名词速查

| 名词 | 说明 | 定位 |
|------|------|------|
| `Project_change` | 项目变更模型 | 核心模型 |
| `parts` | 变更部件字段（旧版） | 逗号分隔的部件编号 |
| `parts_owners` | 部件负责人配置 | TextField/JSON |
| `nodes` | 变更节点列表（新版） | 逗号分隔的节点ID |
| `nodes_owners` | 节点负责人配置 | JSONField |
| `hw_desc` | 硬件变更说明 | 字段名/枚举值 |
| `hw_confirm` | 硬件变更确认 | 字段名/枚举值 |
| `sw_desc` | 软件变更说明 | 字段名/枚举值 |
| `sw_confirm` | 软件变更确认 | 字段名/枚举值 |
| `BASIC_INFO_CHANGE` | 基础信息变更 | 变更类型 |
| `REQUIREMENT_CHANGE` | 客户需求变动 | 变更类型 |
| `node_owner_config_map` | 节点负责人配置映射 | 枚举配置 |
| `create_node_mapping` | 自动创建节点映射 | 枚举配置 |
| `construct_project_change_scopes` | 构建变更范围 | 工具函数 |
| `handle_change_approval` | 变更审批信号处理器 | 信号处理器 |
