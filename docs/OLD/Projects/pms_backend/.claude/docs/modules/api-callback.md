# API Callback 模块说明

## 概述

飞书回调处理模块，负责处理飞书开放平台的机器人消息、卡片交互和事件回调。采用分层架构设计，将视图、处理器、服务和工具分离。

## 目录结构

```
apps/API/callback/
├── __init__.py              # 导出处理器和视图
├── views.py                 # 视图层（HTTP 请求/响应）
├── constants.py             # 常量定义
├── handlers/                # 处理器层（业务逻辑）
│   ├── __init__.py
│   ├── base.py              # 基础处理器类
│   ├── message_handler.py   # 消息处理器
│   ├── card_handler.py      # 卡片处理器
│   └── event_handler.py     # 事件处理器
├── services/                # 服务层（可复用业务逻辑）
│   ├── __init__.py
│   ├── time_utils.py        # 时间转换工具
│   ├── template_service.py  # 文档模板服务
│   ├── project_report_service.py  # 项目报告服务
│   └── approval_service.py  # 审批处理服务
└── utils/                   # 工具层（通用工具函数）
    ├── __init__.py
    ├── decryption.py        # 解密工具
    └── validation.py        # 验证工具
```

## 对外接口

### 视图函数

| 视图函数 | 路由 | 功能 |
|---------|------|------|
| `msg_callback_view` | `POST /api/msg` | 机器人消息回调 |
| `card_callback_view` | `POST /api/card` | 卡片交互回调 |
| `event_callback_view` | `POST /api/event` | 事件回调 |

### 处理器类

| 处理器 | 功能 |
|--------|------|
| `MessageCallbackHandler` | 处理飞书机器人消息回调 |
| `CardCallbackHandler` | 处理飞书卡片交互回调 |
| `EventCallbackHandler` | 处理业务事件回调 |

### 服务类

| 服务 | 功能 |
|------|------|
| `TimeConverter` | 时间格式转换 |
| `TemplateService` | 文档模板管理 |
| `ProjectReportService` | 项目报告生成 |
| `ApprovalService` | 审批处理 |

### 工具类

| 工具 | 功能 |
|------|------|
| `CallbackDecryption` | 回调数据解密 |
| `CallbackValidator` | 回调请求验证 |

## 依赖模块

### 外部依赖

- `apps.API.feishu` - 飞书 API 封装
- `apps.SM.models.Message` - 消息模型
- `apps.API.tasks` - 异步任务

### 内部依赖

```
callback/views.py
  ↓
callback/handlers/
  ├── base.py
  ├── message_handler.py
  │   ├── services/
  │   │   ├── time_utils.py
  │   │   ├── template_service.py
  │   │   └── project_report_service.py
  │   └── utils/
  │       ├── decryption.py
  │       └── validation.py
  ├── card_handler.py
  └── event_handler.py
      └── services/
          └── approval_service.py
```

## 业务流程

### 机器人消息处理流程

```
飞书回调 → /api/msg → msg_callback_view
    ↓
MessageCallbackHandler.handle()
    ↓
decrypt_request() → 解密回调数据
    ↓
validate_timestamp() → 验证时间戳（防重放）
    ↓
根据事件类型分发：
    - MESSAGE_RECEIVE → 处理私聊消息
    - MESSAGE_READ → 更新消息已读状态
    - BOT_MENU → 处理菜单点击
    - TASK_UPDATE → 处理任务更新（已停用）
```

### 卡片回调处理流程

```
飞书卡片交互 → /api/card → card_callback_view
    ↓
CardCallbackHandler.handle()
    ↓
处理按钮点击事件
    ↓
返回卡片更新响应
```

### 事件回调处理流程

```
飞书事件回调 → /api/event → event_callback_view
    ↓
EventCallbackHandler.handle()
    ↓
根据业务类型分发：
    - 日期选择器 → 生成项目报告
    - 按钮点击 → 审批处理
        ├── project_customer_confirm → 客户确认审批
        ├── project_upgrade_confirm → 项目升级确认
        ├── project_pause_application → 项目暂停申请
        ├── project_continuation_application → 项目继续申请
        ├── project_change_notice_confirm → 变更通知确认
        ├── project_change_confirm_cc → 变更抄送确认
        └── general_notice → 通用通知
```

## 常量定义

### EventType（事件类型）

| 常量 | 值 | 说明 |
|------|-----|------|
| MESSAGE_RECEIVE | `im.message.receive_v1` | 用户私聊消息 |
| MESSAGE_READ | `im.message.message_read_v1` | 消息已读 |
| BOT_MENU | `application.bot.menu_v6` | 机器人菜单 |
| TASK_UPDATE | `task.task.update_tenant_v1` | 任务更新 |

### BusinessType（业务类型）

| 常量 | 说明 |
|------|------|
| PROJECT_CUSTOMER_CONFIRM | 项目客户确认审批 |
| PROJECT_UPGRADE_CONFIRM | 项目升级确认 |
| PROJECT_PAUSE_APPLICATION | 项目暂停申请 |
| PROJECT_CONTINUATION_APPLICATION | 项目继续申请 |
| PROJECT_CHANGE_NOTICE_CONFIRM | 项目变更通知确认 |
| PROJECT_CHANGE_CONFIRM_CC | 项目变更抄送确认 |
| GENERAL_NOTICE | 通用通知 |
| GENERATE_PROJECT_LIST | 生成项目列表 |

### HandleType（操作类型）

| 常量 | 说明 |
|------|------|
| ADOPT | 通过 |
| REFUSE | 拒绝 |

## 时间验证

- **验证窗口：** 3 秒（`TIMESTAMP_VALIDATION_WINDOW`）
- **目的：** 防止重放攻击

## 禁止事项

1. **禁止修改 `apps/API/callback/constants.py` 中的常量值** - 常量与飞书平台配置强关联
2. **禁止直接访问 `user.open_id`** - 应使用 `get_user_feishu_open_id(user)` 工具函数
3. **禁止绕过时间验证** - 时间验证是防止重放攻击的关键
4. **禁止在处理器中直接执行耗时操作** - 应使用 Celery 异步任务

## 扩展指南

### 新增回调类型

1. 在 `constants.py` 中添加新的事件类型常量
2. 在对应的处理器中添加处理逻辑
3. 如需复杂业务逻辑，创建新的服务类

### 新增服务类

1. 在 `services/` 目录下创建新文件
2. 继承或组合现有服务类
3. 在 `services/__init__.py` 中导出

### 新增工具函数

1. 在 `utils/` 目录下创建或修改工具类
2. 在 `utils/__init__.py` 中导出
3. 确保工具函数是纯函数或无状态方法
