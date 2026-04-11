# 数据流

"""
=============
Module: data_flow.md
Description: PMS 系统核心数据流程说明
Author: Cakk
=============
"""

## 消息发送流程（异步）

系统使用 Celery 异步任务发送飞书消息，避免阻塞主业务流程。

```
┌─────────────────┐
│  Message 创建   │ SerializerMessage.create()
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  handle_new_message     │ apps/SM/messages/signals.py
│  (Message 信号)          │ @receiver(post_save, sender=Message)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  判断用户是否有飞书账号  │ get_user_feishu_open_id(user)
│  (安全获取 open_id)      │ 返回 None 或 open_id
└────────┬────────────────┘
         │ 有 open_id
         ▼
┌─────────────────────────┐
│  创建 Message_Feishu    │ Message_Feishu.objects.create()
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  handle_new_feishu_msg  │ apps/SM/messages/signals.py
│  (Message_Feishu 信号)   │ @receiver(post_save, sender=Message_Feishu)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  async_send_feishu_msg  │ apps/SM/messages/tasks.py
│  (Celery 异步任务)       │ @shared_task(max_retries=3)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  FeishuMessageManager   │ utils/openapi/feishu/message_manager.py
│  .send_template_message │ 发送飞书模板消息
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  更新消息状态           │ SENT / FAILED
└─────────────────────────┘
```

**关键特性：**
- **异步执行**：消息发送在 Celery worker 中异步执行，不阻塞主流程
- **安全判断**：使用 `get_user_feishu_open_id()` 安全获取用户 open_id
- **错误重试**：任务失败时自动重试，最多 3 次
- **状态管理**：根据发送结果更新消息状态（SENT/FAILED）

**相关文件：**
- `apps/SM/messages/models.py` - Message、Message_Feishu 模型
- `apps/SM/messages/serializers.py` - SerializerMessage 序列化器
- `apps/SM/messages/signals.py` - 消息信号处理器
- `apps/SM/messages/tasks.py` - 消息异步任务
- `utils/openapi/feishu/message_manager.py` - 飞书消息管理器

---

## 项目状态更新流程

系统使用专用接口和验证器模式处理项目状态变更，确保状态转换的合法性和权限控制。

```
┌─────────────────────────┐
│  PATCH /pm/project/{id}/status
│  PatchStatusView        │ apps/PM/project/views.py
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  PatchStatusSerializer  │ apps/PM/project/serializers.py
│  .validate()            │ 接收 state、reason 参数
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  选择对应的状态验证器      │
│  - ProjectStatusPauseValidator     (4: 暂停)
│  - ProjectStatusCompleteValidator  (2: 完成)
│  - ProjectStatusCancelValidator   (6: 取消)
│  - ProjectStatusInProgressValidator (1: 恢复)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  验证器执行验证检查        │ apps/PM/project/validators.py
│  1. 权限验证              │ authority.verify(权限码)
│  2. 状态转换验证           │ 检查当前状态是否允许转换
│  3. 业务规则验证           │ 如：完成项目需里程碑完成
└────────┬────────────────┘
         │ 验证通过
         ▼
┌─────────────────────────┐
│  执行状态更新              │
│  - 更新 project.state    │
│  - 记录操作日志           │ common.projectInsertPeratorLog()
│  - 完成项目保存评价数据    │ eva_views.save_evaluate_data()
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  返回响应                 │
│  { projectId, state }    │
└─────────────────────────┘
```

**关键特性：**
- **验证器模式**：参考 nodelist 模块设计，支持双模式验证（抛出异常/收集错误）
- **权限分离**：每个状态转换有独立的权限码（1100-1103）
- **业务规则封装**：复杂的业务规则（如里程碑检查）封装在验证器中
- **可复用性**：验证器可在其他场景复用（如权限判断、UI 状态控制）

**相关文件：**
- `apps/PM/project/validators.py` - 项目状态验证器
- `apps/PM/project/serializers.py` - PatchStatusSerializer
- `apps/PM/project/views.py` - PatchStatusView
- `apps/PM/project/enums.py` - 状态枚举定义
- `apps/PM/authority/authority.py` - 权限验证模块

---

## 🆕 评审拒绝处理流程（Since 2026-03-18）

当评审项被拒绝时，系统自动处理交付物状态更新、节点回滚和消息通知。

```
┌─────────────────────────┐
│  POST 创建 NodeReview   │ apps/PM/review/views.py
│  process_status=REJECTED │ NodeReviewWriteSerializer.create()
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  handle_node_review_created │ apps/PM/review/signals.py
│  (NodeReview 信号)       │ @receiver(post_save, sender=NodeReview)
└────────┬────────────────┘
         │ 检查: created=True AND process_status=REJECTED
         ▼
┌─────────────────────────┐
│  NodeReviewService      │ apps/PM/review/services.py
│  .handle_review_rejection() │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  检查交付物定义版本       │ review_definition_version
│  deliverable_definition_version │
└────────┬────────────────┘
         │ 存在
         ▼
┌─────────────────────────┐
│  查找项目所有节点中的     │ DeliverableInstance.objects.filter(
│  交付物实例               │ project_node__list=project,
│                          │ definition=deliverable_definition_version
│                          │ )
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  更新交付物状态           │ state = REVIEW_REJECTED
│  (所有找到的实例)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  回滚节点到进行中状态     │ node.state = IN_PROGRESS
│  (去重处理)              │ 重置 review_rule.history
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  async_send_review_    │ apps/PM/review/tasks.py
│  rejection_notice()     │ Celery 异步任务
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  SerializerMessage      │ apps/SM/messages/serializers.py
│  .create()              │ 创建消息记录
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  飞书消息发送流程        │ (参考消息发送流程)
│  (异步)                 │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  完成                   │ 节点负责人收到拒绝通知
└─────────────────────────┘
```

**关键特性：**
- **信号驱动**：通过 `post_save` 信号自动触发处理
- **跨节点处理**：查找项目所有节点中包含该交付物定义的实例
- **状态更新**：交付物状态更新为 `REVIEW_REJECTED`
- **节点回滚**：相关节点回滚到 `IN_PROGRESS` 状态
- **异步通知**：使用 Celery 异步任务发送飞书消息
- **去重处理**：同一节点只回滚一次

**相关文件：**
- `apps/PM/review/signals.py` - 评审项信号处理器
- `apps/PM/review/services.py` - 评审项服务层
- `apps/PM/review/tasks.py` - 评审拒绝通知任务
- `apps/PM/deliverable/instance/enums.py` - 交付物状态枚举（含 REVIEW_REJECTED）
- `apps/PM/nodelist/enums.py` - 节点状态枚举（IN_PROGRESS）
