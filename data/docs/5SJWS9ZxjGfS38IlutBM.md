# SM/messages 模块说明

## 模块概述

消息管理模块，负责系统中各类消息的创建、管理和异步发送，主要支持飞书消息推送。

**路径**: `apps/SM/messages/`

## 模型

### Message（消息）

消息主模型，存储消息的基本信息。

**字段**:
- `receiver_user` - 接收用户（ForeignKey → SM.User）
- `sender_user` - 发送用户（ForeignKey → SM.User）
- `metadata` - 元数据（JSONField）
- `create_time` - 创建时间（DateTimeField）
- `update_time` - 更新时间（DateTimeField）
- `expire_time` - 到期时间（DateTimeField）
- `content` - 消息内容（TextField）
- `category` - 消息类型（CharField，选项：NOTICE/APPROVAL）
- `status` - 状态（CharField，选项：PENDING/SENT/FAILED）
- `is_read` - 是否已读（BooleanField）
- `object_id` - 泛型对象ID（PositiveIntegerField）
- `content_type` - 泛型内容类型（ForeignKey → ContentType）
- `content_object` - 泛型外键（GenericForeignKey）

**状态**:
- `PENDING` - 待发送
- `SENT` - 已发送
- `FAILED` - 发送失败

### Message_Feishu（飞书消息）

飞书消息扩展模型，存储飞书特有信息。

**字段**:
- `message` - 关联消息（OneToOneField → Message，related_name='message_feishu'）
- `robot_id` - 机器人ID（CharField）
- `open_message_id` - 飞书消息ID（CharField，nullable）
- `card_template_id` - 卡片模板ID（CharField）
- `message_type` - 消息类型（CharField，选项：CARD/TEXT）

## 序列化器

### SerializerMessage

消息序列化器，处理消息的创建和更新。

**字段**:
- `receiver_user_id` - 接收用户ID（PrimaryKeyRelatedField）
- `sender_user_id` - 发送用户ID（PrimaryKeyRelatedField）
- `template` - 卡片模板ID（CharField）
- `object_id` - 关联对象ID（IntegerField）
- `content_type_id` - 内容类型ID（PrimaryKeyRelatedField）
- `expire_time` - 到期时间（DateTimeField）
- `category` - 消息类型（CharField）
- `content` - 消息内容（CharField）
- `metadata` - 元数据（JSONField）

**create() 方法**:
1. 从 `validated_data` 中提取 `template` 字段
2. 将 `template_id` 临时存储在 `metadata['_card_template_id']` 中
3. 调用父类 `create()` 方法创建 Message 实例
4. 信号处理器会自动创建 Message_Feishu 并异步发送

**update() 方法**:
1. 更新 `metadata`
2. 安全获取用户的飞书 `open_id`
3. 如果用户有飞书账号，调用 `FeishuMessageManager.update_template_message()` 更新消息卡片

## 信号处理器

### handle_new_message

监听 `Message` 模型的 `post_save` 事件。

**逻辑**:
1. 检查是否为新创建的实例
2. 从 `metadata` 中提取 `template_id`
3. 清理临时字段
4. 调用 `get_user_feishu_open_id()` 安全获取用户 open_id
5. 如果用户有飞书账号，创建 `Message_Feishu` 实例

### handle_new_feishu_message

监听 `Message_Feishu` 模型的 `post_save` 事件。

**逻辑**:
1. 检查是否为新创建的实例
2. 调用异步任务 `async_send_feishu_message.delay(instance.id)`
3. 立即返回，不阻塞主流程

## 异步任务

### async_send_feishu_message

异步发送飞书消息的 Celery 任务。

**参数**:
- `message_feishu_id` - Message_Feishu 实例 ID

**逻辑**:
1. 使用 `select_related` 优化查询，获取 Message_Feishu 实例
2. 调用 `get_user_feishu_open_id()` 安全获取用户 open_id
3. 如果用户没有飞书账号，标记消息状态为 `FAILED`
4. 调用 `FeishuMessageManager.send_template_message()` 发送消息
5. 根据发送结果更新消息状态（`SENT` 或 `FAILED`）
6. 失败时自动重试，最多 3 次

## 工具函数

### get_user_feishu_open_id(user)

安全获取用户的飞书 open_id。

**参数**:
- `user` - User 模型实例

**返回**:
- `str` - 飞书 open_id
- `None` - 用户没有飞书账号

**实现**:
```python
try:
    return user.user_feishu.open_id
except user.user_feishu.__class__.RelatedObjectDoesNotExist:
    return None
```

## 数据流

```
SerializerMessage.create()
    → Message.objects.create()
    → handle_new_message (信号)
    → get_user_feishu_open_id() (判断)
    → Message_Feishu.objects.create()
    → handle_new_feishu_message (信号)
    → async_send_feishu_message.delay() (异步任务)
    → FeishuMessageManager.send_template_message()
    → 更新消息状态 (SENT/FAILED)
```

## 依赖关系

### 依赖的模块

- `apps.SM.user.models` - User、UserFeishu 模型
- `utils.openapi.feishu.message_manager` - FeishuMessageManager

### 被依赖的模块

- `apps.SM.approval.flow` - 审批流创建消息
- `apps.PM` - 项目管理模块创建通知消息

## 禁止事项

1. **禁止直接访问 `user.open_id`**：应使用 `get_user_feishu_open_id(user)` 函数安全获取
2. **禁止同步发送消息**：必须通过异步任务 `async_send_feishu_message.delay()` 发送
3. **禁止绕过信号创建 Message_Feishu**：应让信号处理器自动创建，确保异步流程正常执行

## 注意事项

1. **异步执行**：消息发送是异步的，需要确保 Celery worker 正常运行
2. **错误处理**：任务失败会自动重试 3 次，超过后标记为 `FAILED`
3. **状态管理**：消息状态由异步任务更新，不要在信号中直接更新
4. **安全判断**：始终使用 `get_user_feishu_open_id()` 判断用户是否有飞书账号