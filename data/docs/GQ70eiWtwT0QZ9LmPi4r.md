# PM - Project_Pause 模块说明

> 最后更新：2026-03-20
> 路径：`apps/PM/pause/`
> 模型：`Project_Pause`

---

## 模块概述

项目暂停模块负责处理项目的暂停申请和审批流程。当项目需要临时暂停时，用户可以通过该模块发起暂停申请，经审批通过后项目状态将变更为"已暂停"。

---

## 数据模型

### Project_Pause

项目暂停申请记录模型。

**表名：** `PM_project_pause`

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 ID |
| project | ForeignKey | 关联项目（PM.Project_List） |
| applicant | ForeignKey | 申请人（SM.User） |
| approval | ForeignKey | 审批信息（SM.Approval） |
| reason | TextField | 暂停原因 |
| create_time | DateTimeField | 创建时间 |
| complete_time | DateTimeField | 完成时间（可空） |
| status | CharField | 状态（PENDING/APPROVED/REJECTED/CANCEL） |

**关联关系**

- `project` - 关联项目，通过 `pause_project` 反向查询
- `applicant` - 申请人，通过 `pause_applicant` 反向查询
- `approval` - 审批信息，通过 `pause_approver` 反向查询

---

## 状态枚举

### 暂停申请状态（status）

| 值 | 说明 |
|-------|------|
| PENDING | 待评审 |
| APPROVED | 已评审 |
| REJECTED | 已拒绝 |
| CANCEL | 已取消 |

### 项目状态（Project_List.state）

| 值 | 说明 |
|-------|------|
| 1 | 进行中 |
| 2 | 已完成 |
| 3 | 项目变更中 |
| 4 | 已暂停 |
| 5 | 申请中 |
| 6 | 取消立项 |

---

## 业务流程

### 创建暂停申请

1. 用户提交暂停申请，填写暂停原因
2. 系统验证项目状态和权限
3. 创建暂停申请记录（状态为 PENDING）
4. 自动触发审批流程
5. 记录操作日志

### 审批流程

1. 审批人收到飞书审批通知
2. 审批人通过飞书审批界面进行审批
3. 审批通过后：
   - 暂停申请状态变为 APPROVED
   - 项目状态变更为"已暂停"（state=4）
   - 发送飞书消息通知申请人
4. 审批拒绝后：
   - 暂停申请状态变为 REJECTED
   - 项目状态保持不变

---

## 验证规则

### 创建暂停申请时的验证

1. **项目状态验证**
   - 项目状态必须为"进行中"（state=1）
   - 项目不能已经处于暂停状态（state=4）

2. **重复申请验证**
   - 项目在有效期内不能有多个待审批的暂停申请
   - 有效期由配置文件中的 `API_FEISHU['message']['expiry_date']` 决定

3. **权限验证**
   - 用户必须已登录（IsAuthenticated）
   - 用户需具有暂停项目的权限

---

## 文件结构

```
apps/PM/pause/
├── __init__.py
├── models.py        # Project_Pause 模型定义
├── serializers.py   # 序列化器
├── views.py         # API 视图
├── enums.py         # 枚举定义
└── signals.py       # 信号处理
```

---

## API 接口

详细接口文档请参考：[PM - Project_Pause 接口文档](../api/pm-project_pause.md)

---

## 依赖模块

- **SM** - 用户管理、审批流
- **PM.project** - 项目列表、项目状态管理
- **PM.log** - 操作日志记录

---

## 注意事项

1. 项目暂停后，所有相关节点的操作将受限
2. 暂停申请审批通过后，项目状态才会真正变更
3. 暂停的项目需要通过"项目继续"模块来恢复
4. 审批流模板代码配置在 `settings.CUSTOM_SETTING['approval']['template']['project_pause_application']['code']`
